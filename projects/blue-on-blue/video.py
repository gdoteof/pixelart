"""Frame renderer for Blue on Blue: Zohran Mamdani on Gavin Newsom's podcast, streamed live.

Newsom hosts from the left and Mamdani sits on the right, at one long desk with a podcast mic each; the
show's name glows in neon between them. The stream's UI carries the lyrics (the lower third), the live
viewer count, chapter cards, the live chat (a ticker along the bottom, and a flood in the hook) and the
reactions that float up the side. The wide two-shot is home; the camera cuts in on a rapper only briefly.

render_frame(t) builds one 1920x1080 frame: a 320x180 world seen through an integer-zoom camera
(pixelart.camera), plus a 320x180 UI layer shown at 6x. Per-line gags (gags_*.py, see gagkit.py)
hook into its phases:

    <setup>  poses and props: gags change `c` here (c.st[who], c.shot, c.neon_word, c.viewers...)
    "back"   world: on the wall (the portrait, the neon sign), behind the hosts
    "mid"    world: in front of the hosts and the desk, behind the mics and the laptop
    "front"  world: in front of everything in the studio
    "ui"     UI layer, under the lower third
    "top"    UI layer, over everything
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import studio
import timeline as TL
from characters import FH, FW, figure
from engine import C, INK, PRESS, PRESS16, SILK, H, W, Canvas, blend, mix, rnd
from pixelart import pixel
from pixelart.camera import Cam, compose
from pixelart.gags import Gags

FPS = TL.FPS
PHASES = ("back", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
HOSTS = ("newsom", "mamdani")
STATE = ("arms", "lean", "bob", "eyes", "brows", "mouth", "flush")
NAME = {"newsom": "GAVIN NEWSOM", "mamdani": "ZOHRAN MAMDANI", "chat": "LIVE CHAT", "trump": "DONALD TRUMP"}
ROLE = {"newsom": "HOST", "mamdani": "MAYOR OF NEW YORK", "chat": "EVERYBODY", "trump": "ON SPEAKERPHONE"}
TAG = {"newsom": C["blazer_hi"], "mamdani": C["mtie_sh"], "chat": C["tt_pink"], "trump": C["tie"]}
REST_MOUTH = {"newsom": "smile", "mamdani": "grin"}

SEATS = {"newsom": (studio.SEAT_L, 1), "mamdani": (studio.SEAT_R, -1)}
SHOTS = {
    "wide": (160, 90, 6),             # the studio: home
    "newsom": (84, 84, 12),           # Newsom from the hair to the desk
    "mamdani": (236, 84, 12),
    "neon": (160, 44, 12),            # the sign, the two heads at the edges
}


def default_state(who):
    s = dict(hidden=False, dx=0, dy=0, arms="desk", lean=1, bob=0, eyes="open", brows="neutral", mouth="closed",
             flush=0, held=None, gesture=True, react=True, sweat=False, tears=False, tint=None, facing=1)
    if who == "newsom":
        s.update(arms="clasp", mouth="smile")
    else:
        s.update(arms="desk", mouth="grin", facing=-1)
    return s


# --- per-frame context -----------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = TL.RAPPER.get(self.sec)
        self.st = {w: default_state(w) for w in HOSTS}
        self.vars = {}
        self.subs = True                                   # the lower third's lyrics
        self.tag = True                                    # the speaker's name tab
        self.cards = True                                  # chapter cards
        self.ticker = True                                 # the chat ticker
        self.bug = True                                    # LIVE and the viewer count
        self.hitfx = True                                  # reactions on punchlines
        self.viewers = None                                # None: the count follows the song
        self.neon_word, self.neon_lit, self.neon_color, self.neon_flicker = "IS", True, None, False
        self.onair = True
        self.ring = 1.0
        self.laptop = True
        self.phone_lit, self.phone_dx = False, 0
        self.flash, self.flash_color = 0.0, C["white"]
        self.floats = []                                   # extra reactions: (kind, x, y)
        self.shake = 0.0
        self.shot = "wide"
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
# A rapper changes gesture every two beats. Newsom presents: the steeple, the open palm, the point,
# the chop, the raised finger, a hand smoothing the hair, the pinch. Mamdani explains, smiling: the open
# palm, the shrug, the point, a hand on his heart, the finger guns. Listening, Newsom clasps his hands on
# the desk and keeps the smile on; Mamdani leans on the desk and grins.

TALK = {"newsom": (("steeple", 3), ("palm", 3), ("point", 2), ("chop", 2), ("finger", 2), ("hair", 1), ("pinch", 1)),
        "mamdani": (("palm", 3), ("shrug", 3), ("point", 2), ("chest", 2), ("finger", 1), ("chop", 1), ("guns", 1))}


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
        return REST_MOUTH[who]
    if loud < 0.4:
        return "open"
    if loud < 0.7:
        return "grin" if who == "mamdani" else "open"
    return "wide"


def pose_rapper(c, who):
    s = c.st[who]
    if s["gesture"]:
        s["arms"] = pick(who, c.beat_i // 2)
        ln = c.ln
        if ln and ln["who"] == who and (ln["sec"], ln["idx"]) in TL.KILL_SHOTS:
            if TL.last_word(ln) - 0.15 <= c.t <= TL.last_word(ln) + 0.9:   # the punchline: point at him
                s["arms"] = "point"
        if s["arms"] == "pinch" and c.ph < 0.35:
            s["dy"] = 1
    s["bob"] = 1 if c.ph < 0.3 else 0
    s["lean"] = 2
    s["mouth"] = mouth_for(who, TL.loudness(c.t)) if singing(c, who) else REST_MOUTH[who]
    if who == "newsom":
        s["brows"] = "angry" if s["arms"] in ("point", "chop") else "up" if s["arms"] in ("palm", "steeple") else "neutral"
        s["eyes"] = "half" if s["arms"] == "hair" else "open"
    else:
        s["brows"] = "up" if s["arms"] in ("shrug", "palm", "chest") else "neutral"
        s["eyes"] = "shut" if s["arms"] == "chest" else "open"


def pose_listener(c, who):
    s = c.st[who]
    bar = c.beat_i // 4
    s["lean"] = 1
    if who == "newsom":
        if s["gesture"]:
            s["arms"] = ("clasp", "clasp", "chin", "cross")[(bar // 2) % 4]
        s["mouth"] = "smile" if bar % 4 != 3 else "smirk"
        s["eyes"] = "side" if bar % 5 == 2 else "open"
    else:
        if s["gesture"]:
            s["arms"] = ("desk", "clasp", "desk", "chin")[(bar // 2) % 4]
        s["mouth"] = "grin" if bar % 3 != 1 else "smile"
        s["eyes"] = "shut" if bar % 6 == 4 else "open"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"newsom": (3.4, 0.6), "mamdani": (3.8, 1.9)}[who]
        if s["eyes"] in ("open", "half", "side") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The target flinches as each line lands, and reels from the big ones."""
    for who in HOSTS:
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
                    s["arms"] = "shrug" if who == "mamdani" else "facepalm"
        kb = (2 if big else 1) * max(0.0, 1 - age / 0.35)
        s["dx"] += int(round(kb * -s["facing"]))                         # knocked back in his chair


# --- reactions: hearts, laughs and skulls floating up the side of the stream -------------------------

@lru_cache(maxsize=None)
def react_icon(kind):
    f = Canvas(9, 9)
    if kind == "heart":
        f.ell((0, 0, 4, 4), "red"); f.ell((4, 0, 8, 4), "red"); f.poly([(0, 3), (8, 3), (4, 7)], "red")
        f.px((2, 1), "red_hi")
    elif kind == "laugh":
        f.ell((0, 0, 8, 8), "duck"); f.line([(2, 3), (3, 2)], "ink"); f.line([(5, 2), (6, 3)], "ink")
        f.poly([(2, 5), (6, 5), (4, 7)], "mouth"); f.pxs([(1, 4), (7, 4)], "tear")
    elif kind == "skull":
        f.ell((0, 0, 8, 6), "white"); f.rect((2, 5, 6, 8), "white")
        f.rect((2, 3, 3, 4), "ink"); f.rect((5, 3, 6, 4), "ink"); f.pxs([(3, 7), (5, 7)], "ink")
    elif kind == "fire":
        f.poly([(4, 0), (8, 5), (7, 8), (1, 8), (0, 5), (2, 3), (3, 5)], "orange")
        f.poly([(4, 4), (6, 7), (2, 7)], "duck")
    elif kind == "zzz":
        f.line([(1, 1), (7, 1)], "white"); f.line([(7, 1), (1, 7)], "white"); f.line([(1, 7), (7, 7)], "white")
    return f.done()


REACT = {"newsom": ("skull", "laugh", "laugh", "fire", "skull"), "mamdani": ("laugh", "heart", "laugh", "fire")}


def draw_reactions(c):
    """Big punchlines send a stream of reactions up the right edge for two seconds."""
    for h in TL.HITS:
        age = c.t - h["t"]
        if not h["big"] or not 0 <= age < 2.4:
            continue
        kinds = REACT[h["target"]]
        for j in range(9):
            a = age - j * 0.12
            if not 0 <= a < 1.6:
                continue
            x = 296 + int(rnd("rx", h["t"], j) * 16) + int(4 * math.sin(a * 5 + j))
            y = 140 - int(a * 70)
            spr = react_icon(kinds[j % len(kinds)])
            c.ui.alpha_composite(spr, (x, y))
    for kind, x, y in c.floats:
        spr = react_icon(kind)
        c.ui.alpha_composite(spr, (int(x), int(y)))


# --- drawing the hosts ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def place(c, who):
    """(x, y) of the top-left of who's canvas this frame."""
    s = c.st[who]
    (x, y), _ = SEATS[who]
    return int(round(x + s["dx"])), int(round(y + s["dy"]))


def draw_host(c, img, who):
    s = c.st[who]
    if s["hidden"]:
        return None
    pose = {k: s[k] for k in STATE}
    spr, a = figure(who, facing=s["facing"], held=s["held"], phones=False, **pose)
    if s["tint"]:
        from engine import tint
        spr = tint(spr, *s["tint"])
    x, y = place(c, who)
    pad = (spr.width - FW) // 2                                           # figure() pads for a wide held prop
    x, y = x - pad, y - pad
    img.paste(spr, (x, y), spr)
    anchors = {k: (px + x, py + y) for k, (px, py) in a.items()}
    hx, hy = anchors["head"]
    if s["sweat"]:
        d = sweat_drop()
        img.paste(d, (int(hx - s["facing"] * 18), int(hy + 6 + int(c.t * 6) % 3)), d)
    if s["tears"]:                                                        # two streams down the near cheek
        ex, ey = anchors["eye"]
        dd = ImageDraw.Draw(img)
        k = int(c.t * 10) % 4
        dd.line([(ex, ey + 2), (ex, ey + 7)], fill=C["tear"])
        dd.point((ex, ey + 8 + k % 2), fill=C["tear"])
    c.anchor[who] = anchors
    return anchors


# --- the UI: the stream's bug, chapter cards, the lower third and the chat ticker ------------------------

def ui_text(ui, xy, s, fnt=SILK, fill=C["white"], anchor="la"):
    """Silkscreen glyphs sit 4 px down their box: this puts the glyph tops at y."""
    x, y = xy
    dy = 4 if fnt is SILK else 0
    pixel.text(ui, (x, y - dy), s, fnt, tuple(fill), None, anchor)


VIEWERS = [(0.0, 48200), (10.0, 51900), (36.0, 64300), (47.0, 412000), (58.0, 1240000), (80.0, 3410000),
           (100.0, 3020000), (108.0, 2870000), (200.0, 2870000)]


def viewers_at(t):
    ts = [a for a, _ in VIEWERS]
    vs = [math.log(v) for _, v in VIEWERS]
    return int(round(math.exp(float(np.interp(t, ts, vs)))))


def fmt_count(n):
    if n >= 1_000_000:
        return f"{n / 1e6:.1f}M"
    if n >= 10_000:
        return f"{n / 1e3:.1f}K"
    return f"{n:,}"


@lru_cache(maxsize=1)
def eye_icon():
    return pixel.sprite([".www.", "wwkww", ".www."], {"w": C["white"], "k": INK})


def draw_bug(c):
    if not c.bug:
        return
    d = ImageDraw.Draw(c.ui)
    d.rectangle((6, 6, 28, 14), fill=C["red"] + (255,))
    ui_text(c.ui, (10, 8), "LIVE")
    if int(c.t * 2) % 2 == 0:
        d.ellipse((7, 9, 8, 10), fill=C["white"] + (255,))
    n = c.viewers if c.viewers is not None else viewers_at(c.t)
    s = fmt_count(n)
    w = pixel.text_width(s, SILK) + 15
    d.rectangle((29, 6, 29 + w, 14), fill=(14, 16, 30, 220))
    c.ui.alpha_composite(eye_icon(), (32, 8))
    ui_text(c.ui, (40, 8), s)


CARDS = {"intro": ("EPISODE 112", "THE MAYOR OF NEW YORK"),
         "v1": ("CHAPTER 1", "GAVIN HAS NOTES"),
         "v2": ("CHAPTER 2", "THE GUEST RESPONDS"),
         "hook": ("CHAPTER 3", "THE CHAT HAS OPINIONS"),
         "v3": ("CHAPTER 4", "GAVIN IS FINE, ACTUALLY"),
         "v4": ("CHAPTER 5", "THE GUEST CLOSES")}
CARD_TIME = 2.0                   # seconds a chapter card stays up


def draw_card(c):
    if not c.cards or c.sec not in CARDS:
        return
    age = c.t - c.sa
    if not 0 <= age < CARD_TIME:
        return
    k = min(1.0, age / 0.2) if age < CARD_TIME - 0.3 else max(0.0, 1 - (age - CARD_TIME + 0.3) / 0.3)
    card(c, *CARDS[c.sec], k)


def card(c, big, small, k=1.0):
    """A chapter card at the top of the screen, sliding in from the left as k goes 0 -> 1."""
    bw = max(pixel.text_width(big, PRESS) + 14, pixel.text_width(small, SILK) + 14)
    x0 = int(W // 2 - bw // 2 - (1 - k) * (W // 2 + bw))
    d = ImageDraw.Draw(c.ui)
    d.rectangle((x0 - 1, 19, x0 + bw + 1, 42), fill=INK + (255,))
    d.rectangle((x0, 20, x0 + bw, 31), fill=C["blue_sh"] + (255,))
    d.rectangle((x0, 32, x0 + bw, 41), fill=C["white"] + (255,))
    d.line([(x0, 31), (x0 + bw, 31)], fill=C["neon_glow"] + (255,))
    pixel.outline_text(c.ui, (x0 + bw // 2, 22), big, PRESS, C["white"], INK, anchor="ma")
    ui_text(c.ui, (x0 + bw // 2, 34), small, fill=C["ink"], anchor="ma")


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
    d.rectangle((0, y0, W, y0 + 17), fill=(14, 18, 40, 235))
    d.line([(0, y0), (W, y0)], fill=C["neon_glow"] + (255,))
    space = pixel.text_width(" ", SILK)
    for r, row in enumerate(rows):
        x, y = 8, y0 + 3 + 7 * r + (3 if len(rows) == 1 else 0)
        for i in row:
            fill = C["gold"] if i == now else C["white"] if i < now else (170, 180, 210)
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


# The chat, scrolling along the bottom: (name, message) per section
CHAT = {
    "intro": [("bearflag_bro", "GAVIN LOOKING CRISP"), ("nyc_renter", "ZOHRAN!!!"), ("frenchlaundry", "first"),
              ("podcast_pete", "is this the one with the guest")],
    "v1": [("gavinstan", "HE'S COOKING"), ("dsa_dan", "tax the rich (not his texts)"), ("maga_mike", "HOTTIE??"),
           ("bearflag_bro", "the hair is undefeated"), ("pundit_pam", "this is a breakup")],
    "v2": [("nyc_renter", "HANDSOME!!!"), ("bearflag_bro", "gavin lowkey crying"), ("pundit_pam", "oh he's FINISHED"),
           ("temu_shopper", "temu trump is $1.99"), ("kimberly_fan", "leave her out of it")],
    "hook": [("nyc_renter", "HANDSOME"), ("dsa_dan", "NEWSCUM"), ("maga_mike", "HANDSOME"), ("mod_bot", "slow down")],
    "v3": [("gavinstan", "GAVIN'S BACK"), ("rentcontrol4life", "froze the rent W"), ("melania_fan", "she's GLAD lmao"),
           ("dsa_dan", "the bus is fine actually")],
    "v4": [("uhaul_guy", "on my way to texas"), ("listener_9", "zzz"), ("bot_4471", "is this still live"),
           ("nyc_renter", "THIS WAS LMAO")],
    "outro": [("realDonaldTrump", "HANDSOME!!!"), ("nyc_renter", "HE CALLED"), ("bearflag_bro", "who?? WHO??")],
    "end": [("mod_bot", "thanks for watching")],
}
CHAT_COLORS = (C["chat_name"], C["chat_name2"], C["chat_name3"], C["chat_name4"])


def chat_color(name):
    return C["tie_hi"] if name == "realDonaldTrump" else CHAT_COLORS[sum(map(ord, name)) % len(CHAT_COLORS)]


def draw_ticker(c):
    if not c.ticker:
        return
    d = ImageDraw.Draw(c.ui)
    y0 = 170
    d.rectangle((0, y0, W, H), fill=(18, 20, 36, 255))
    msgs = CHAT.get(c.sec, [("", "")])
    seg = []
    for name, msg in msgs:
        seg.append((name + ":", chat_color(name)))
        seg.append((msg + "     ", C["chat_text"]))
    tw = sum(pixel.text_width(s, SILK) + 3 for s, _ in seg)
    off = int((c.t - c.sa) * 26)
    x = 320 - off
    while x < -tw:
        x += tw
    while x < W:
        xx = x
        for s, col_ in seg:
            ui_text(c.ui, (xx, y0 + 3), s, fill=col_)
            xx += pixel.text_width(s, SILK) + 3
        x += tw
    d.rectangle((0, y0, 29, H), fill=C["tt_pink"] + (255,))
    ui_text(c.ui, (4, y0 + 3), "CHAT")


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

def setup(c):
    for who in HOSTS:
        if c.rapper == who:
            pose_rapper(c, who)
        else:
            pose_listener(c, who)


def build_frame(t, tweak=None):
    """Draw the frame at time t. Returns the context, with its world, ui and cam ready to compose.
    `tweak(c)`, if given, runs after the gags' setup (thumbnails use it to turn the UI off)."""
    import gags  # noqa: F401  (registers the per-line gags into GAGS)
    c = Ctx(t)
    setup(c)
    runner = GAGS.runner(c, t, TL.LINES, TL.section_end)
    if tweak:
        tweak(c)
    blink_eyes(c)
    if c.hitfx:
        apply_hits(c)
    c.cam = resolve_shot(c)
    world = studio.backdrop().copy()
    c.world = world
    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    studio.ring_light(world, c.ring)
    studio.onair(world, c.onair)
    if c.neon_word:
        studio.neon(world, c.neon_word, c.neon_lit, c.neon_color, c.neon_flicker, c.f)
    runner.run("back")
    for who in HOSTS:
        draw_host(c, world, who)
    studio.draw_desk(world)
    runner.run("mid")
    studio.desk_items(world, laptop=c.laptop, phone_lit=c.phone_lit, phone_dx=c.phone_dx)
    for who in HOSTS:
        studio.draw_mic(world, who, lit=singing(c, who))
    runner.run("front")
    if c.flash > 0:
        blend(world, 1.0, c.flash_color, min(1.0, c.flash))
    runner.run("ui")
    if c.hitfx:
        draw_reactions(c)
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


__all__ = ["FPS", "render_frame", "label", "build_frame", "GAGS", "Ctx", "np", "mix", "PRESS", "PRESS16", "FH", "FW"]
