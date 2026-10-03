"""Frame renderer for Trump vs. Netanyahu Round 2: an Oval Office sit-down, carried live.

The two men sit where every visiting leader sits: the gold armchairs in front of the fireplace, Bibi
on the left, Trump on the right, Washington's portrait between them. The press pool is on the camera's
side of the room, and the broadcast's lower third carries the lyrics and a news ticker. The wide shot
is home; the camera cuts in on a rapper only briefly.

render_frame(t) builds one 1920x1080 frame: a 320x180 world seen through an integer-zoom camera
(pixelart.camera), plus a 320x180 UI layer shown at 6x. Per-line gags (gags_*.py, see gagkit.py)
hook into its phases:

    <setup>  poses and props: gags change `c` here (c.st[who], c.shot, c.press, c.flags...)
    "back"   world: on the room (the wall, the portrait, the mantel), behind the chairs and the men
    "mid"    world: in front of the seated men, behind anyone standing and the press
    "front"  world: in front of everything in the room
    "ui"     UI layer, under the lower third
    "top"    UI layer, over everything
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import office
import timeline as TL
from characters import FEET_STAND, FH, FW, chair, figure
from engine import C, INK, PRESS, PRESS16, SILK, H, W, blend, mix, rnd
from pixelart import pixel
from pixelart.camera import Cam, compose
from pixelart.gags import Gags

FPS = TL.FPS
PHASES = ("back", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
SEATED = ("bibi", "trump")
STANDING = ("obama", "announcer")
CAST = SEATED + STANDING
STATE = ("legs", "arms", "lean", "bob", "eyes", "brows", "mouth", "flush")
NAME = {"trump": "TRUMP", "bibi": "NETANYAHU", "obama": "OBAMA", "announcer": "ANNOUNCER", "press": "PRESS POOL"}
ROLE = {"trump": "PRESIDENT", "bibi": "PRIME MINISTER", "obama": "PEACE PRIZE, 2009",
        "announcer": "NOBEL PEACE PRIZE FIGHT", "press": "WHITE HOUSE PRESS CORPS"}
TAG = {"trump": C["tie"], "bibi": C["btie_sh"], "obama": C["tan_sh"], "announcer": C["gold_sh"], "press": (90, 92, 110)}

# where everyone is: the seated men in their chairs (canvas top-left), the others by their feet
SEATS = {"bibi": (office.SEAT_L, 1), "trump": (office.SEAT_R, -1)}
SPOTS = {"centre": (160, 166), "door": (22, 150), "front": (160, 196)}
SHOTS = {
    "wide": (160, 90, 6),             # the room: home
    "bibi": (100, 88, 12),            # Bibi from the hair to the knees, the portrait at the edge
    "trump": (220, 88, 12),
    "portrait": (160, 52, 12),        # the portrait over the fireplace, the two heads at the sides
    "centre": (160, 96, 12),          # whoever stands in front of the fireplace
}


def default_state(who):
    s = dict(hidden=False, dx=0, dy=0, legs="stand", arms="rest", lean=0, bob=0, eyes="open", brows="neutral",
             mouth="closed", flush=0, held=None, gesture=True, react=True, sweat=False, soot=0.0, tint=None,
             spot=None, facing=1)
    if who == "bibi":
        s.update(legs="together", arms="lap", mouth="smirk")
    elif who == "trump":
        s.update(legs="spread", arms="between", lean=2, bob=2, mouth="pout", eyes="squint", facing=-1)
    elif who == "obama":
        s.update(hidden=True, spot="centre", mouth="grin")
    elif who == "announcer":
        s.update(hidden=True, spot="front", arms="mic", mouth="grin", gesture=False)
    return s


def mic_hand(s):
    """Whoever has the mic holds it in the hand that isn't pointing."""
    import props
    hand = "hand_far" if s["arms"] in ("mic", "rest", "read") else "hand_near"
    return (props.mic(), (hand, 5))


# --- per-frame context -----------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = TL.RAPPER.get(self.sec)
        self.st = {w: default_state(w) for w in CAST}
        self.vars = {}
        self.subs = True                                   # the lower third's lyrics
        self.tag = True                                    # the speaker's name tab
        self.cards = True                                  # section cards
        self.ticker = True
        self.bug = True                                    # the LIVE bug
        self.hitfx = True                                  # flashes and reactions on punchlines
        self.press = 0.0                                   # how far the press pool has risen into frame (0-1)
        self.press_mood = "chant"                          # chant, gasp, cheer, gobble
        self.flash, self.flash_color = 0.0, C["white"]
        self.pops = []                                     # press camera flashes this frame: (x, y, size)
        self.shake = 0.0
        self.shot = "wide"
        self.fire = True
        self.cam = self.world = self.ui = None
        self.anchor = {}

    def get(self, key, default=None):
        return self.vars.get(key, default)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color

    def to_ui(self, x, y):
        return self.cam.ui(x, y)


# --- mannerisms --------------------------------------------------------------------------------
# A rapper changes gesture every two beats. Trump talks with his hands: the accordion (hands
# pumping in and out on the beat), the pinch (thumb and finger together, jabbing), the point, the
# shrug, the thumbs-up, the chop and the rally fist. Bibi lectures: the raised finger, the open
# palm, the point and the chop. Listening, Trump sits knees wide with his hands clasped between them
# and pouts; Bibi sits up straight, hands on his knees, and smirks.

TALK = {"trump": (("acc", 5), ("pinch", 4), ("point", 2), ("shrug", 2), ("thumb", 1), ("chop", 2), ("fist", 1),
                  ("steeple", 1)),
        "bibi": (("finger", 4), ("palm", 3), ("point", 2), ("chop", 2), ("steeple", 1), ("lap", 1)),
        "obama": (("clear", 4), ("point", 2), ("shrug", 2), ("palm", 2))}


def pick(who, slot):
    """The gesture for a two-beat slot: weighted, and never the same twice running."""
    opts = TALK[who]
    total = sum(w for _, w in opts)

    def draw(k):
        r = rnd(who, "gesture", k) * total
        for g, w in opts:
            r -= w
            if r < 0:
                return g
        return opts[-1][0]

    g = draw(slot)
    if g == draw(slot - 1):
        g = draw(slot + 1000)
    return g


def singing(c, who):
    ln = c.ln
    return ln is not None and ln["who"] == who and ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.45


def mouth_for(who, loud):
    if loud < 0.12:
        return {"trump": "pout", "bibi": "closed", "obama": "grin", "announcer": "grin"}[who]
    if who == "trump":
        return "o" if loud < 0.35 else "open" if loud < 0.65 else "wide"
    return "open" if loud < 0.6 else "wide"


def pose_rapper(c, who):
    s = c.st[who]
    if s["gesture"]:
        slot = c.beat_i // 2
        g = pick(who, slot)
        beat_up = c.ph < 0.35                                             # the downstroke of each beat
        if g == "acc":                                                    # hands in and out with the beat
            g = ("acc0", "acc1", "acc2", "acc1")[(c.beat_i * 2 + (c.ph >= 0.5)) % 4]
        s["arms"] = g
        ln = c.ln
        if ln and ln["who"] == who and (ln["sec"], ln["idx"]) in TL.KILL_SHOTS:
            if TL.last_word(ln) - 0.15 <= c.t <= TL.last_word(ln) + 0.9:   # the punchline: point at him
                s["arms"] = "point" if who != "bibi" or ln["idx"] % 4 == 1 else "finger"
        if s["arms"] == "pinch" and beat_up:
            s["dy"] = 1
    s["bob"] = (2 if who == "trump" else 0) + (1 if c.ph < 0.3 else 0)
    s["lean"] = 2 if who == "trump" else 1
    if singing(c, who):
        s["mouth"] = mouth_for(who, TL.loudness(c.t))
    else:
        s["mouth"] = {"trump": "pout", "bibi": "smirk", "obama": "grin"}.get(who, s["mouth"])
    if who == "trump":
        s["eyes"] = "squint" if s["mouth"] in ("wide", "pout", "o") else "open"
        s["brows"] = "angry" if s["mouth"] == "wide" else "up" if s["arms"] == "shrug" else "neutral"
    elif who == "bibi":
        s["eyes"] = "half" if s["mouth"] in ("closed", "smirk") else "open"
        s["brows"] = "angry" if s["arms"] in ("point", "chop") else "neutral"
    else:
        s["brows"] = "up" if s["arms"] == "clear" else "neutral"


def pose_listener(c, who):
    s = c.st[who]
    bar = c.beat_i // 4
    if who == "trump":
        if s["gesture"]:
            s["arms"] = "cross" if (bar // 3) % 3 == 1 else "between"
        s["lean"], s["bob"] = (0, 1) if s["arms"] == "cross" else (2, 2)
        s["mouth"] = "pout" if bar % 4 != 3 else "frown"
        s["eyes"] = "side" if bar % 5 == 2 else "squint"
    elif who == "bibi":
        if s["gesture"]:
            s["arms"] = "chin" if (bar // 3) % 3 == 2 else "lap"
        s["mouth"] = "smirk" if bar % 3 != 1 else "closed"
        s["eyes"] = "half" if bar % 4 != 1 else "side"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"trump": (3.3, 0.4), "bibi": (3.9, 1.7), "obama": (3.6, 0.9), "announcer": (4.1, 2.2)}[who]
        if s["eyes"] in ("open", "half", "side") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The target flinches as each line lands, and reels from the big ones."""
    for who in SEATED:
        h = TL.last_hit(c.t, target=who, window=1.4)
        s = c.st[who]
        if not h or not s["react"]:
            continue
        age, big = c.t - h["t"], h["big"]
        if age < (1.1 if big else 0.4):
            s["eyes"] = "wide" if big else s["eyes"]
            s["brows"] = "worried"
            s["mouth"] = "o" if big and age < 0.5 else "frown"
            if big:
                s["flush"] = 1
                s["sweat"] = True
                if age < 0.6 and s["gesture"]:
                    s["arms"] = "shrug" if who == "trump" else "palm"
        kb = (2 if big else 1) * max(0.0, 1 - age / 0.35)
        s["dx"] += int(round(kb * -s["facing"]))                         # knocked back into the chair


def hit_effects(c):
    """Big punchlines: the press pool's cameras go off, and the room flashes."""
    for h in TL.HITS:
        age = c.t - h["t"]
        if h["big"] and 0 <= age < 0.5:
            press_flashes(c, h["t"], 5 if age < 0.25 else 2, age)
            if age < 0.08:
                c.add_flash(0.22)


def press_flashes(c, seed, n, age=0.0):
    """Camera flashes from the press pool, along the bottom of the frame."""
    for j in range(n):
        if rnd("pop", seed, j, int(age * 12)) < 0.6:
            x = 12 + int(rnd("popx", seed, j) * 296)
            y = 150 + int(rnd("popy", seed, j) * 22)
            c.pops.append((x, y, 2 + int(rnd("pops", seed, j) * 3)))


def idle_flashes(c):
    """Now and then a photographer gets a shot anyway."""
    k = int(c.t * 3)
    if rnd("idle", k) < 0.06:
        c.pops.append((12 + int(rnd("idlex", k) * 296), 156 + int(rnd("idley", k) * 16), 2))


# --- drawing the cast ------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def place(c, who):
    """(x, y) of the top-left of who's canvas this frame."""
    s = c.st[who]
    if who in SEATS:
        (x, y), _ = SEATS[who]
    else:
        fx, fy = SPOTS[s["spot"]] if isinstance(s["spot"], str) else s["spot"]
        x, y = fx - FW // 2, fy - FEET_STAND
    return int(round(x + s["dx"])), int(round(y + s["dy"]))


def draw_char(c, img, who):
    s = c.st[who]
    if s["hidden"]:
        return None
    pose = {k: s[k] for k in STATE}
    spr, a = figure(who, facing=s["facing"], held=s["held"], **pose)
    if s["tint"]:
        from engine import tint
        spr = tint(spr, *s["tint"])
    x, y = place(c, who)
    img.paste(spr, (x, y), spr)
    anchors = {k: (px + x, py + y) for k, (px, py) in a.items()}
    if s["sweat"]:
        hx, hy = anchors["head"]
        d = sweat_drop()
        img.paste(d, (int(hx - s["facing"] * 18), int(hy + 6 + int(c.t * 6) % 3)), d)
    c.anchor[who] = anchors
    return anchors


def draw_seated(c, img):
    for who in SEATED:
        (x, y), facing = SEATS[who]
        if not c.get(f"no_chair_{who}"):
            ch = chair(facing)
            img.paste(ch, (x, y), ch)
        draw_char(c, img, who)


# --- the press pool --------------------------------------------------------------------------------
# Silhouettes along the bottom of the frame: heads, shoulders, cameras held up, a boom mic. They rise
# into frame for the chant and the decision, and duck back down.

PRESS_PEOPLE = [(14 + i * 30 + int(rnd("px", i) * 10), int(rnd("ph", i) * 6), rnd("pk", i)) for i in range(11)]


def draw_press(c, img):
    if c.press <= 0:
        return
    d = ImageDraw.Draw(img)
    rise = int(round(72 * c.press))
    for i, (x, dh, kind) in enumerate(PRESS_PEOPLE):
        bounce = 0
        if c.press_mood in ("chant", "cheer", "gobble"):
            bounce = 2 if (c.beat_i + i) % 2 == 0 and c.ph < 0.4 else 0
        top = H + 8 - rise + dh - bounce
        col_, sh_ = C["press"], C["press_sh"]
        d.ellipse((x - 7, top + 12, x + 13, top + 40), fill=sh_)                   # shoulders
        d.ellipse((x - 4, top, x + 8, top + 13), fill=col_)                       # head
        if kind < 0.45:                                                           # a camera, held up
            d.rectangle((x + 4, top - 8, x + 15, top - 1), fill=C["black"])
            d.ellipse((x + 6, top - 7, x + 12, top - 2), fill=C["lens"])
            d.line([(x + 6, top + 14), (x + 8, top - 2)], fill=sh_, width=3)
        elif c.press_mood in ("chant", "cheer") and kind < 0.8:                   # a fist in the air
            up = 4 if (c.beat_i + i) % 2 == 0 else 0
            d.line([(x + 10, top + 16), (x + 13, top - 4 - up)], fill=sh_, width=3)
            d.ellipse((x + 10, top - 9 - up, x + 16, top - 3 - up), fill=col_)
        elif c.press_mood == "gasp":                                              # hands to faces
            d.ellipse((x - 2, top + 8, x + 3, top + 13), fill=sh_)
    if c.get("boom") is not None:                                                 # a boom mic over someone
        bx, by = c.get("boom")
        d.line([(0, H - 10), (bx - 6, by)], fill=C["press_sh"], width=2)
        d.ellipse((bx - 9, by - 4, bx + 3, by + 4), fill=(70, 66, 72))


def draw_pops(c, img):
    d = ImageDraw.Draw(img)
    for x, y, size in c.pops:
        d.line([(x - size * 2, y), (x + size * 2, y)], fill=C["flash"])
        d.line([(x, y - size * 2), (x, y + size * 2)], fill=C["flash"])
        d.ellipse((x - size, y - size, x + size, y + size), fill=C["flash"])


# --- the UI: LIVE bug, section cards, the lower third and the ticker -------------------------------------

def ui_text(ui, xy, s, fnt=SILK, fill=C["white"], anchor="la"):
    """Silkscreen glyphs sit 4 px down their box: this puts the glyph tops at y."""
    x, y = xy
    dy = 4 if fnt is SILK else 0
    pixel.text(ui, (x, y - dy), s, fnt, tuple(fill), None, anchor)


def draw_bug(c):
    if not c.bug:
        return
    d = ImageDraw.Draw(c.ui)
    d.rectangle((6, 6, 28, 14), fill=C["red"] + (255,))
    ui_text(c.ui, (9, 8), "LIVE")
    where = "THE OVAL OFFICE"
    d.rectangle((29, 6, 29 + pixel.text_width(where, SILK) + 6, 14), fill=(16, 22, 48, 230))
    ui_text(c.ui, (32, 8), where, fill=C["gold_hi"])
    if int(c.t * 2) % 2 == 0:
        d.ellipse((24, 9, 26, 11), fill=C["white"] + (255,))


CARDS = {"intro": ("LIVE", "NOBEL PEACE PRIZE FIGHT"),
         "v1": ("BREAKING", "TRUMP HAS THE FLOOR"),
         "v2": ("BREAKING", "NETANYAHU RESPONDS"),
         "hook": ("BREAKING", "THE PRESS POOL PICKS SIDES"),
         "v3": ("DEVELOPING", "TRUMP: 'VERY UNFAIR'"),
         "bridge": ("SURPRISE GUEST", "THE 2009 WINNER WALKS IN"),
         "v4": ("DEVELOPING", "NETANYAHU HITS BACK"),
         "outro": ("DECISION", "THE COMMITTEE HAS VOTED")}


CARD_TIME = 2.0                   # seconds a section card stays up


def draw_card(c):
    if not c.cards or c.sec not in CARDS:
        return
    age = c.t - c.sa
    if not 0 <= age < CARD_TIME:
        return
    k = min(1.0, age / 0.2) if age < CARD_TIME - 0.3 else max(0.0, 1 - (age - CARD_TIME + 0.3) / 0.3)
    card(c, *CARDS[c.sec], k)


def card(c, big, small, k=1.0):
    """A breaking-news card at the top of the screen, sliding in from the left as k goes 0 -> 1."""
    bw = max(pixel.text_width(big, PRESS16) + 12, pixel.text_width(small, SILK) + 12)
    x0 = int(W // 2 - bw // 2 - (1 - k) * (W // 2 + bw))
    d = ImageDraw.Draw(c.ui)
    d.rectangle((x0 - 1, 21, x0 + bw + 1, 50), fill=INK + (255,))
    d.rectangle((x0, 22, x0 + bw, 40), fill=C["red"] + (255,))
    d.rectangle((x0, 41, x0 + bw, 49), fill=C["white"] + (255,))
    d.line([(x0, 40), (x0 + bw, 40)], fill=C["gold"] + (255,))
    pixel.outline_text(c.ui, (x0 + bw // 2, 24), big, PRESS16, C["white"], INK, anchor="ma")
    ui_text(c.ui, (x0 + bw // 2, 43), small, fill=C["ink"], anchor="ma")


LYRIC_Y = 155                     # the lyric bar's first row of glyphs


def wrap(words, width):
    rows, row, x = [], [], 0
    space = pixel.text_width(" ", SILK)
    for i, w in enumerate(words):
        ww = pixel.text_width(w, SILK)
        if row and x + space + ww > width:
            rows.append(row)
            row, x = [], 0
        x += (space if row else 0) + ww
        row.append(i)
    return rows + [row] if row else rows


def draw_lower_third(c):
    ln = c.ln
    if not ln or not c.subs:
        return
    d = ImageDraw.Draw(c.ui)
    words = [w["w"] for w in ln["words"]]
    now = TL.word_index(ln, c.t)
    rows = wrap(words, W - 16)[:2]
    y0 = 152
    d.rectangle((0, y0, W, y0 + 17), fill=(16, 22, 48, 235))
    d.line([(0, y0), (W, y0)], fill=C["gold"] + (255,))
    space = pixel.text_width(" ", SILK)
    for r, row in enumerate(rows):
        x, y = 8, y0 + 3 + 7 * r + (3 if len(rows) == 1 else 0)
        for i in row:
            fill = C["gold"] if i == now else C["white"] if i < now else (178, 184, 206)
            ui_text(c.ui, (x, y), words[i], fill=fill)
            x += pixel.text_width(words[i], SILK) + space
    who = ln.get("who")
    if c.tag and who in NAME:
        name, role = NAME[who], ROLE[who]
        nw, rw = pixel.text_width(name, SILK) + 8, pixel.text_width(role, SILK) + 8
        d.rectangle((6, y0 - 10, 6 + nw, y0 - 1), fill=TAG[who] + (255,))
        ui_text(c.ui, (10, y0 - 8), name)
        d.rectangle((6 + nw, y0 - 10, 6 + nw + rw, y0 - 1), fill=(236, 236, 242, 255))
        ui_text(c.ui, (10 + nw, y0 - 8), role, fill=C["ink"])


TICKER = {
    "intro": ["NOBEL COMMITTEE 'MONITORING THE SITUATION'", "OVAL OFFICE GOLD LEAF SUPPLY 'RUNNING LOW'"],
    "v1": ["QATAR: JET WAS 'JUST A LITTLE SOMETHING'", "ACME DENIES ALL INVOLVEMENT",
           "NORWAY ASKS IF PEACE PRIZES CAN BE RETURNED"],
    "v2": ["PENCE SPOTTED ON A TRACTOR, WAVES", "WHITE HOUSE LAUNDRY 'AT CAPACITY'",
           "TURKEY HIRES A LAWYER, JUST IN CASE"],
    "hook": ["PRESS POOL SPLIT DOWN THE MIDDLE"],
    "v3": ["LONDON BABY BALLOON CLEARED FOR TAKEOFF", "JELL-O STOCKS SURGE",
           "IRAN 'WEEKS AWAY' FOR 34TH STRAIGHT YEAR"],
    "bridge": ["THE HAGUE: 'WE'LL LEAVE THE LIGHT ON'", "OSLO SUITE BOOKED, NON-REFUNDABLE"],
    "v4": ["OBAMA: 'STILL HAVE MINE, THANKS'", "TRIAL POSTPONED: TUMMY BUG",
           "FIFA ANNOUNCES PEACE PRIZE FOR GOLF"],
    "outro": ["BREAKING: TURKEY", "BREAKING: TURKEY"],
    "end": ["THANK YOU FOR WATCHING"],
}


def draw_ticker(c):
    if not c.ticker:
        return
    d = ImageDraw.Draw(c.ui)
    y0 = 170
    d.rectangle((0, y0, W, H), fill=(120, 16, 26, 255))
    s = "   +++   ".join(TICKER.get(c.sec, [""])) + "   +++   "
    tw = pixel.text_width(s, SILK)
    off = int((c.t - c.sa) * 26)
    x = 320 - off
    while x < -tw:
        x += tw
    while x < W:
        ui_text(c.ui, (x, y0 + 3), s)
        x += tw
    d.rectangle((0, y0, 33, H), fill=C["gold"] + (255,))
    ui_text(c.ui, (4, y0 + 3), "NEWS", fill=C["ink"])


# --- world effects ---------------------------------------------------------------------------------------

def resolve_shot(c):
    shot = c.shot
    if isinstance(shot, Cam):
        return shot
    if isinstance(shot, str):
        shot = SHOTS[shot]
    return Cam(*shot)


def shake_offset(c):
    if c.shake < 0.5:
        return (0, 0)
    a = rnd("shake", c.f) * 2 * math.pi
    return (int(round(math.cos(a) * c.shake)), int(round(math.sin(a) * c.shake)))


# --- the frame ------------------------------------------------------------------------------------------

OBAMA_ON = (TL.section_start("bridge"), TL.section_end("bridge") + 1.6)   # his walk-on, his verse, his exit


def setup(c):
    if c.sec in ("intro", "outro", "end"):
        c.st["announcer"]["hidden"] = False
    if OBAMA_ON[0] <= c.t < OBAMA_ON[1]:
        c.st["obama"]["hidden"] = False
    for who in SEATED:
        if c.rapper == who:
            pose_rapper(c, who)
        else:
            pose_listener(c, who)
    for who in STANDING:
        if not c.st[who]["hidden"] and singing(c, who):
            pose_rapper(c, who) if who == "obama" else None


def sing_extras(c):
    """Anyone visible who is singing this line gets a moving mouth, whatever the gags set up."""
    for who in STANDING:
        s = c.st[who]
        if not s["hidden"] and singing(c, who) and s.get("auto_mouth", True):
            s["mouth"] = mouth_for(who, TL.loudness(c.t)) if TL.loudness(c.t) >= 0.12 else s["mouth"]


def build_frame(t, tweak=None):
    """Draw the frame at time t. Returns the context, with its world, ui and cam ready to compose.
    `tweak(c)`, if given, runs after the gags' setup (thumbnails use it to turn the UI off)."""
    import gags  # noqa: F401  (registers the per-line gags into GAGS)
    c = Ctx(t)
    setup(c)
    runner = GAGS.runner(c, t, TL.LINES, TL.section_end)
    if tweak:
        tweak(c)
    sing_extras(c)
    for who in STANDING:
        s = c.st[who]
        if s.get("has_mic", who == "announcer") and s["held"] is None:
            s["held"] = mic_hand(s)
    blink_eyes(c)
    if c.hitfx:
        apply_hits(c)
        hit_effects(c)
    idle_flashes(c)
    c.cam = resolve_shot(c)
    world = office.backdrop().copy()
    c.world = world
    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if c.fire:
        office.fire(world, c.f)
    runner.run("back")
    tbl = office.table_sprite()
    world.paste(tbl, (office.TABLE[0] - 3, office.TABLE[1]), tbl)
    draw_seated(c, world)
    runner.run("mid")
    for who in STANDING:
        draw_char(c, world, who)
    draw_press(c, world)
    runner.run("front")
    draw_pops(c, world)
    if c.flash > 0:
        blend(world, 1.0, c.flash_color, min(1.0, c.flash))
    runner.run("ui")
    draw_bug(c)
    draw_card(c)
    draw_lower_third(c)
    draw_ticker(c)
    runner.run("top")
    return c


def render_frame(t):
    c = build_frame(t)
    return compose(c.world, c.ui, c.cam, shake_offset(c))


def label(t):
    ln = TL.line_at(t)
    return f"{ln['sec']}.{ln['idx']} {ln['text']}" if ln else TL.section_at(t)[0]


if __name__ == "__main__":
    import sys
    from engine import ROOT
    ts = [float(a) for a in sys.argv[1:]] or [30.0]
    for t in ts:
        render_frame(t).save(ROOT / "build" / f"frame_{t:07.2f}.png")
    print("ok")


__all__ = ["FPS", "render_frame", "label", "build_frame", "GAGS", "Ctx", "np", "mix", "PRESS", "FH"]
