"""Frame renderer for Pardon Me (Trump vs. Bibi), a rap battle at the UN General Assembly.

Both men are famous for holding up props at podiums: the cartoon bomb with its red
line, the Sharpie hurricane map, the tariff board. So the battle is fought with
visual aids. Whoever raps has the floor at the rostrum and a flip chart beside it;
the other heckles from the delegation desk in the front row. The two big screens
carry UN Web TV's close-ups of both of them, so a reaction never needs the camera
to move. The wide shot is home; the camera cuts in on the rapper only briefly.

render_frame(t) builds one 1920x1080 frame: a 320x180 world seen through an
integer-zoom camera (pixelart.camera), plus a 320x180 UI layer shown at 6x.
The per-line gags (gags*.py, see pixelart.gags and gagkit.py) hook into its phases:

    <setup>   shot, poses, flags: gags change `c` here (c.st[who], c.shot, c.screens, c.page_flip...)
    "back"    world: over the wall, the screens and the dais, behind everyone
    "chart"   the flip chart's current page, c.page (chart coordinates, CHART_W x CHART_H)
    "mid"     world: in front of the rostrum and the rapper, behind the desk and the heckler
    "front"   world: in front of everything, the front rows included
    "ui"      UI layer, under the karaoke
    "top"     UI layer, over everything
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import hall
import timeline as TL
from characters import figure, mouth_for
from engine import C, INK, PRESS, PRESS16, SILK, H, W, blend, dither, mask, mix, rnd, scaled, tint
from pixelart import pixel
from pixelart.anim import ease_in_out, lerp
from pixelart.camera import Cam, compose
from pixelart.gags import Gags
from props import big_text, new_page, write
from props import label as plate

FPS = TL.FPS
PHASES = ("back", "chart", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
CAST = ("trump", "bibi")
POSE = ("body", "mouth", "eyes", "brows", "arm", "far", "hat", "outfit", "flush", "lean", "bob")
NAME = {"trump": "TRUMP", "bibi": "BIBI", "announcer": "PRESIDENT OF THE ASSEMBLY", "delegates": "DELEGATES"}
COUNTRY = {"trump": "UNITED STATES", "bibi": "ISRAEL"}
TAG_COLOR = {"trump": C["tie"], "bibi": C["btie_sh"], "announcer": (90, 92, 110), "delegates": C["marble"]}

# the two places to be: (x, y of the feet, facing, layer)
SPOTS = {"rostrum": (hall.PODIUM_SPOT[0], hall.PODIUM_SPOT[1], 1, "podium"),
         "desk": (hall.DESK_SPOT[0], 176, -1, "desk")}
LAYERS = ("podium", "desk", "floor", "front")
SHOTS = {
    "wide": (160, 90, 6),            # the whole hall: home
    "rapper": (160, 112, 12),        # the rostrum, the rapper from the chest up, half the chart
    "tight": (160, 104, 18),         # the rapper's face, for a closer
    "chart": (70, 100, 12),          # the flip chart (only while the rapper is presenting it)
}


def default_state():
    return dict(x=160, y=166, facing=1, hidden=False, layer="podium", dx=0, dy=0, rot=0.0, tint=None, rim=0.0,
                shadow=False, gesture=True, sweat=False, dizzy=False,
                body="stand", mouth="closed", eyes="open", brows="neutral", arm="down", far="down", hat="none",
                outfit="suit", flush=0, lean=0, bob=0)


# --- per-frame context -----------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = TL.RAPPER.get(self.sec)              # who is rapping this section (None outside verses)
        self.floor = TL.FLOOR[self.sec]                    # who holds the rostrum
        self.heckler = TL.OTHER[self.floor]
        self.st = {w: default_state() for w in CAST}
        self.vars = {}
        self.subs = True                                   # the karaoke
        self.tag = True                                    # the speaker tag over the karaoke
        self.cards = True                                  # section cards
        self.hitfx = True                                  # shake and crowd reactions on hits
        self.hit_react = {"trump": True, "bibi": True}
        self.screens = {"L": "floor", "R": "heckler"}      # a who, a callable(c, img, box), or None (blank)
        self.chart = True                                  # draw the flip chart
        self.page = None                                   # the chart's page during the "chart" phase
        self.page_flip = None                              # when the current page went up (flip animation)
        self.rostrum = True
        self.mics = True
        self.desk = True
        self.placard = None                                # country on the desk (None: the heckler's)
        self.president = {"arm": "down", "mouth": "closed", "hidden": False}
        self.gavel = []                                    # extra gavel slams (times)
        self.crowd = {"stand": {}, "react": {}, "gone": set(), "hidden": False}
        self.mood = 0.0
        self.flash, self.flash_color = 0.0, C["white"]
        self.shake = 0.0
        self.shot = "wide"
        self.cam = self.world = self.ui = None
        self.anchor = {}
        for who in CAST:
            self.put(who, "rostrum" if who == self.floor else "desk")

    def get(self, key, default=None):
        return self.vars.get(key, default)

    def put(self, who, spot):
        """Stand `who` at a spot: "rostrum" or "desk"."""
        x, y, facing, layer = SPOTS[spot]
        self.st[who].update(x=x, y=y, facing=facing, layer=layer, hidden=False)

    def to_ui(self, x, y):
        return self.cam.ui(x, y)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color


# --- posing -------------------------------------------------------------------------------------

GESTURES = {"trump": [("point", "down"), ("pinch", "down"), ("palm", "down"), ("shrug", "out"), ("point", "down"),
                      ("thumb", "down"), ("pinch", "down"), ("palm", "out")],
            "bibi": [("up", "down"), ("palm", "down"), ("point", "down"), ("chop", "down"), ("up", "down"),
                     ("palm", "out"), ("point", "down"), ("hold", "hold")]}


def singing(c, who):
    ln = c.ln
    return ln is not None and ln["who"] == who and ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.45


def pose_rapper(c, who):
    s = c.st[who]
    if s["gesture"]:
        s["arm"], s["far"] = GESTURES[who][int(rnd(who, c.beat_i // 2) * 8)]
    s["bob"] = 1 if c.ph < 0.3 else 0
    if singing(c, who):
        s["mouth"] = mouth_for(TL.loudness(c.t), who=who)
    s["brows"] = "angry" if s["mouth"] == "wide" else "up" if who == "trump" else "neutral"
    if who == "trump":
        s["eyes"] = "squint" if s["mouth"] in ("wide", "pout") else "open"


def pose_heckler(c, who):
    s = c.st[who]
    if s["gesture"]:
        s["arm"] = "cross"
    if who == "trump":
        s["mouth"] = "pout" if (c.beat_i // 4) % 3 == 0 else "frown"
        s["eyes"] = "squint"
    else:
        s["mouth"] = "frown"
        s["eyes"] = "half" if (c.beat_i // 4) % 3 == 0 else "open"
        s["brows"] = "angry"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"trump": (3.3, 0.4), "bibi": (3.9, 1.7)}[who]
        if s["eyes"] in ("open", "half") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The heckler flinches as each line lands, and reels from the big ones."""
    for who in CAST:
        h = TL.last_hit(c.t, target=who, window=1.2)
        if not h or not c.hit_react[who]:
            continue
        age = c.t - h["t"]
        s = c.st[who]
        big = h["big"]
        if age < (0.9 if big else 0.35):
            s["eyes"] = "wide" if big else s["eyes"]
            s["brows"] = "worried"
            s["mouth"] = "wide" if big and age < 0.3 else "o" if big else s["mouth"]
            if big and age < 0.5 and s["gesture"]:
                s["arm"] = "palm"
        if big:
            s["sweat"] = True
        kb = (3 if big else 1) * max(0.0, 1 - age / 0.4)
        s["dx"] += int(round(kb * -s["facing"]))


def hit_effects(c):
    """Big punchlines: a small shake and an "oooh" from the front rows."""
    for h in TL.HITS:
        age = c.t - h["t"]
        if 0 <= age < 0.7 and h["big"]:
            if age < 0.3:
                c.add_shake(4 * (1 - age / 0.3))
            k = 1 - age / 0.7
            for j in range(4):
                i = int(rnd("ooh", h["t"], j) * len(hall.DELEGATES))
                c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), k)


# --- changing places between verses --------------------------------------------------------------
# When the floor passes to the other man they cross: one steps down from the rostrum to the desk,
# the other goes up, both walking behind the rostrum and the desk.

def _swaps():
    out = []
    for prev, nxt in zip(TL.ORDER, TL.ORDER[1:]):
        if TL.FLOOR[prev] == TL.FLOOR[nxt] or not TL.lines_of(nxt):
            continue
        before = [ln for ln in TL.LINES if TL.ORDER.index(ln["sec"]) < TL.ORDER.index(nxt)]
        end_prev = TL.last_word(before[-1]) + 0.35 if before else 0.0
        first = TL.lines_of(nxt)[0]["t0"]
        start = min(max(end_prev, first - 1.6), TL.section_start(nxt))   # under way when the section opens
        out.append((start, start + 1.4, TL.FLOOR[nxt]))
    return out


SWAPS = _swaps()


def walk_floor(c):
    for a, b, new in SWAPS:
        if a <= c.t < b:
            p = ease_in_out((c.t - a) / (b - a))
            old = TL.OTHER[new]
            for who, src, dst in ((new, "desk", "rostrum"), (old, "rostrum", "desk")):
                x0, y0, f0, _ = SPOTS[src]
                x1, y1, f1, _ = SPOTS[dst]
                s = c.st[who]
                s.update(x=lerp(x0, x1, p), y=lerp(y0, y1, p) - 2 * math.sin(p * math.pi),
                         facing=1 if x1 > x0 else -1, layer="podium",
                         body="walk1" if int(c.t * 6) % 2 else "walk2", arm="down", far="down", gesture=False)
            c.placard = COUNTRY[old] if p > 0.5 else COUNTRY[new]
            return True
    return False


# --- characters ------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def sprite_of(c, who):
    """(sprite, anchors) for a character as posed this frame."""
    s = c.st[who]
    pose = {k: s[k] for k in POSE}
    spr, a = figure(who, s["facing"], rim=s["rim"], **pose)
    if s["tint"]:
        spr = tint(spr, *s["tint"])
    return spr, a


def draw_char(c, img, who):
    s = c.st[who]
    if s["hidden"]:
        return None
    spr, a = sprite_of(c, who)
    x, y = int(round(s["x"] + s["dx"])), int(round(s["y"] + s["dy"]))
    ox, oy = x - a["feet"][0], y - a["feet"][1]
    if s["shadow"] and not s["rot"]:
        dither(img, mask(lambda d: d.ellipse((x - 12, y - 1, x + 12, y + 2), fill=255)) * 0.6, (0, 0, 0), blend=0.3)
    if s["rot"]:
        m = 40
        layer = Image.new("RGBA", (spr.width + 2 * m, spr.height + 2 * m), (0, 0, 0, 0))
        layer.paste(spr, (m, m), spr)
        layer = layer.rotate(s["rot"], resample=Image.NEAREST, center=(m + a["feet"][0], m + a["feet"][1]))
        img.paste(layer, (ox - m, oy - m), layer)
    else:
        img.paste(spr, (ox, oy), spr)
    anchors = {k: (px + ox, py + oy) for k, (px, py) in a.items()}
    if s["sweat"] and not s["rot"]:
        hx, hy = anchors["head"]
        d = sweat_drop()
        img.paste(d, (int(hx - s["facing"] * 13) - 1, int(hy - 8 + int(c.t * 6) % 3)), d)
    if s["dizzy"]:
        hx, hy = anchors["head"]
        dd = ImageDraw.Draw(img)
        for k in range(3):
            ang = c.t * 7 + k * 2 * math.pi / 3
            dd.point((int(hx + 14 * math.cos(ang)), int(hy - 18 + 3 * math.sin(ang))), fill=C["gold"])
    c.anchor[who] = anchors
    return anchors


def draw_layer(c, layer):
    for who in sorted(CAST, key=lambda w: c.st[w]["y"]):
        if c.st[who]["layer"] == layer:
            draw_char(c, c.world, who)


# --- the screens: UN Web TV ----------------------------------------------------------------------------

def feed_backdrop(w, h, tone):
    """UN Web TV's slate behind a close-up (a fresh copy: draw on it freely)."""
    return _feed_backdrop(w, h, tone).copy()


@lru_cache(maxsize=4)
def _feed_backdrop(w, h, tone):
    img = Image.new("RGB", (w, h), C["screen_bg"])
    a = mix(C["screen_bg"], C["screen_hi"], 0.6)
    pixel.vgrad(img, (0, 0, w, h), mix(C["screen_bg"], (0, 0, 0), 0.3), a, steps=5)
    hall.emblem(img, w // 2 + (18 if tone else -18), h // 2 - 4, 13, fg=mix(C["screen_hi"], C["un"], 0.5),
                bg=mix(C["screen_bg"], C["screen_hi"], 0.4))
    return img


def bust(c, who, w, h, facing):
    """The character's face as posed now: w x h sprite pixels from the hair's swoop to the chin."""
    s = c.st[who]
    pose = {k: s[k] for k in POSE}
    pose["bob"] = 0
    spr, a = figure(who, facing, **pose)
    hx, hy = a["head"]
    x0, y0 = int(hx - w / 2 + 4 * facing), int(hy - (16 if s["hat"] != "none" else 11))   # a hat needs headroom
    return spr.crop((x0, y0, x0 + w, y0 + h))


def live_feed(c, img, box, who, facing):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    feed = feed_backdrop(w, h, facing > 0)
    b = scaled(bust(c, who, w // 2, h // 2, facing), 2)
    hb = TL.last_hit(c.t, target=who, window=0.5)
    jolt = int(round(2 * math.sin(c.t * 60))) if hb and hb["big"] and c.hit_react[who] else 0
    feed.paste(b, ((w - b.width) // 2 + jolt, h - b.height), b)
    d = ImageDraw.Draw(feed)
    name = NAME[who]
    tw = pixel.text_width(name, SILK)
    d.rectangle((1, h - 11, tw + 8, h - 2), fill=INK)
    d.rectangle((2, h - 10, tw + 7, h - 3), fill=C["white"])
    d.rectangle((2, h - 10, 3, h - 3), fill=TAG_COLOR[who])
    pixel.text(feed, (6, h - 12), name, SILK, INK, shadow=None)
    if int(c.t * 2) % 2 == 0:
        d.ellipse((3, 3, 6, 6), fill=C["red"])
    pixel.text(feed, (9, 1), "LIVE", SILK, C["white"], shadow=(0, 0, 0))
    img.paste(feed, (x0, y0))


def draw_screens(c):
    for side, frame in (("L", hall.SCREEN_L), ("R", hall.SCREEN_R)):
        box = hall.screen_inner(frame)
        what = c.screens.get(side)
        if what is None:
            continue
        if callable(what):
            what(c, c.world, box)
            continue
        who = {"floor": c.floor, "heckler": c.heckler}.get(what, what)
        live_feed(c, c.world, box, who, 1 if side == "L" else -1)


# --- the President of the Assembly and his gavel ---------------------------------------------------------

def _gavel_times():
    times = []
    for ln in TL.LINES:
        if ln["who"] == "announcer":
            times += [w["t0"] for w in ln["words"] if w["w"].strip(" !,.?").lower() == "order"]
    for s in TL.VERSES:
        times.append(TL.lines_of(s)[0]["t0"] - 0.45)          # the chair recognizes the next speaker
    return sorted(times)


GAVEL = _gavel_times()


def president(c):
    p = c.president
    if p["hidden"]:
        return
    slams = sorted(GAVEL + list(c.gavel))
    arm = p["arm"]
    for g in slams:
        if g - 0.22 <= c.t < g:
            arm = "up"
        elif g <= c.t < g + 0.12:
            arm = "down"
            c.add_shake(2)
    mouth = p["mouth"]
    if c.ln and c.ln["who"] == "announcer" and singing_line(c):
        mouth = "open" if TL.loudness(c.t) > 0.35 else "closed"
    hall.president(c.world, arm, mouth)


def singing_line(c):
    ln = c.ln
    return ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.3


# --- the flip chart --------------------------------------------------------------------------------------

def default_page(c, page):
    """What the chart shows when no gag has put a page up: the speaker's cover sheet."""
    who = c.floor
    write(page, (page.width // 2, 12), "VISUAL AIDS", "blue", fnt=SILK, anchor="ma", bold=True)
    write(page, (page.width // 2, 24), "PRESENTED BY", "black", anchor="ma")
    write(page, (page.width // 2, 34), "H.E. " + ("D.J. TRUMP" if who == "trump" else "B. NETANYAHU"),
          "red", anchor="ma")
    ImageDraw.Draw(page).line([(16, 46), (page.width - 16, 46)], fill=C["mk_black"])


def draw_chart(c, runner):
    if not c.chart:
        runner.run("chart")
        return
    page = new_page(hall.CHART_W, hall.CHART_H)
    c.page = page
    cover = c.page_flip is None
    if cover:
        default_page(c, page)
    runner.run("chart")
    flip = c.sa if cover else c.page_flip                      # the cover sheet goes up as a section opens
    if flip is not None and 0 <= c.t - flip < 0.2:             # the old sheet lifts away over the top
        p = (c.t - flip) / 0.2
        cover = int(round(page.height * (1 - ease_in_out(p))))
        if cover > 0:
            d = ImageDraw.Draw(page)
            d.rectangle((0, 0, page.width, cover), fill=C["paper"])
            d.line([(0, cover), (page.width, cover)], fill=C["paper_sh"])
            d.line([(0, cover + 1), (page.width, cover + 1)], fill=INK)
    x0, y0, _, _ = hall.CHART
    c.world.paste(page, (x0, y0))
    d = ImageDraw.Draw(c.world)
    d.rectangle((x0 - 1, y0, x0 + page.width, y0 + page.height), outline=INK)
    c.page = None


# --- the UI: karaoke, speaker tag, section cards -----------------------------------------------------------

LYRIC_FONT = PRESS


def clean(w):
    return w.strip()


def wrap(words, width):
    rows, row, x = [], [], 0
    space = pixel.text_width(" ", LYRIC_FONT)
    for i, w in enumerate(words):
        ww = pixel.text_width(w, LYRIC_FONT)
        if row and x + space + ww > width:
            rows.append(row)
            row, x = [], 0
        x += (space if row else 0) + ww
        row.append(i)
    return rows + [row] if row else rows


def draw_karaoke(c):
    ln = c.ln
    if not ln or not c.subs:
        return
    ui = c.ui
    words = [clean(w["w"]) for w in ln["words"]]
    now = TL.word_index(ln, c.t)
    rows = wrap(words, W - 20)
    if len(rows) > 2:                                   # a long line scrolls: the current row and the next
        k = next((r for r, row in enumerate(rows) if now <= row[-1]), len(rows) - 1)
        rows = rows[min(k, len(rows) - 2):][:2]
    y = H - 6 - 12 * len(rows)
    space = pixel.text_width(" ", LYRIC_FONT)
    for row in rows:
        x = (W - sum(pixel.text_width(words[i], LYRIC_FONT) for i in row) - space * (len(row) - 1)) // 2
        for i in row:
            fill, dy = (C["text"], 0) if i < now else (C["gold"], -1) if i == now else (C["dim"], 0)
            pixel.outline_text(ui, (x, y + dy), words[i], LYRIC_FONT, fill, INK)
            x += pixel.text_width(words[i], LYRIC_FONT) + space
        y += 12
    if c.tag and ln.get("who") in NAME:
        who = ln["who"]
        ty = H - 8 - 12 * len(rows) - 11
        plate(ui, (10, ty), NAME[who], SILK, bg=TAG_COLOR[who], fg=C["white"])


CARD_TEXT = {"v1": ("VERSE 1", "THE CHAIR RECOGNIZES | THE UNITED STATES"),
             "v2": ("VERSE 2", "THE CHAIR RECOGNIZES | ISRAEL"),
             "hook": ("ORDER!", "THE DELEGATES WILL | COME TO ORDER"),
             "v3": ("VERSE 3", "RIGHT OF REPLY: | THE UNITED STATES"),
             "v4": ("VERSE 4", "RIGHT OF REPLY: | ISRAEL")}


def draw_card(c):
    """The section's card, over the emblem between the screens, for two seconds as the section opens."""
    if not c.cards or c.sec not in CARD_TEXT:
        return
    age = c.t - c.sa
    if not 0 <= age < 2.2:
        return
    big, small = CARD_TEXT[c.sec]
    k = min(1.0, age / 0.15) if age < 1.9 else max(0.0, 1 - (age - 1.9) / 0.3)
    if k <= 0:
        return
    lines = small.split(" | ")
    x0, x1, y0 = 100, 220, 4
    y1 = y0 + 25 + 8 * len(lines)
    d = ImageDraw.Draw(c.ui)
    cy = (y0 + y1) // 2
    hh = int((y1 - y0) / 2 * k)
    d.rectangle((x0 - 1, cy - hh - 1, x1 + 1, cy + hh + 1), fill=INK + (255,))
    d.rectangle((x0, cy - hh, x1, cy + hh), fill=(16, 20, 40, 255))
    if k >= 1:
        d.line([(x0 + 2, y0 + 2), (x1 - 2, y0 + 2)], fill=C["gold"] + (255,))
        d.line([(x0 + 2, y1 - 2), (x1 - 2, y1 - 2)], fill=C["gold"] + (255,))
        big_text(c.ui, (W // 2, y0 + 5), big, PRESS16, anchor="ma")
        for i, s in enumerate(lines):
            pixel.outline_text(c.ui, (W // 2, y0 + 21 + 8 * i), s, SILK, C["text"], INK, anchor="ma")


# --- world effects --------------------------------------------------------------------------------------

def mood_overlay(img, amount):
    if amount <= 0:
        return
    a = np.asarray(img, dtype=np.float32)
    k = 0.55 * min(1.0, amount)
    a = a * (1 - k) + np.array((22, 18, 44), np.float32) * k
    img.paste(Image.fromarray(a.round().astype(np.uint8)))


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


# --- the frame --------------------------------------------------------------------------------------------

def setup(c):
    walking = walk_floor(c)
    if not walking:
        for who in CAST:
            if c.rapper == who:
                pose_rapper(c, who)
            elif who == c.heckler:
                pose_heckler(c, who)
            elif who == c.floor and singing(c, who):
                pose_rapper(c, who)


def build_frame(t, tweak=None):
    """Draw the frame at time t. Returns the context, with its world, ui and cam ready to compose.
    `tweak(c)`, if given, runs after the gags' setup (thumbnails use it to turn the karaoke off)."""
    import gags  # noqa: F401  (registers the per-line gags into GAGS)
    c = Ctx(t)
    setup(c)
    runner = GAGS.runner(c, t, TL.LINES, TL.section_end)
    if tweak:
        tweak(c)
    blink_eyes(c)
    apply_hits(c)
    if c.hitfx:
        hit_effects(c)
    c.cam = resolve_shot(c)
    world = hall.backdrop().copy()
    c.world = world
    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_screens(c)
    president(c)
    hall.ledge_front(world)
    runner.run("back")
    draw_chart(c, runner)
    if c.chart:
        hall.easel_front(world)
    draw_layer(c, "podium")
    if c.rostrum:
        hall.rostrum(world, mics=c.mics)
    runner.run("mid")
    draw_layer(c, "desk")
    if c.desk:
        hall.desk(world, c.placard or COUNTRY[c.heckler])
    draw_layer(c, "floor")
    if not c.crowd["hidden"]:
        hall.delegates(world, t, c.crowd["stand"], c.crowd["gone"], c.crowd["react"])
    draw_layer(c, "front")
    runner.run("front")
    mood_overlay(world, c.mood)
    if c.flash > 0:
        blend(world, 1.0, c.flash_color, min(1.0, c.flash))
    runner.run("ui")
    draw_card(c)
    draw_karaoke(c)
    runner.run("top")
    return c


def render_frame(t):
    c = build_frame(t)
    return compose(c.world, c.ui, c.cam, shake_offset(c))


def label(t):
    ln = TL.line_at(t)
    return f"{ln['sec']}.{ln['idx']} {ln['text']}" if ln else TL.section_at(t)[0]
