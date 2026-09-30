"""Frame renderer for Two Georges.

render_frame(t) builds one 1920x1080 frame: a 320x180 world seen through an
integer-zoom camera (pixelart.camera), plus a 320x180 UI layer shown at 6x.

The frame is built in steps, and the per-line gags (gags*.py, see
pixelart.gags) hook into them by yielding the phase they draw in next:

    <setup>     scene choice, shot, poses and moods: gags change `c` here
    "back"      world, over the set but behind the characters (things on the water)
    "front"     world, in front of the characters
    "ui"        UI layer, under the karaoke band
    "top"       UI layer, over everything
"""
import math
from functools import lru_cache

import numpy as np

from PIL import Image, ImageDraw

import timeline as TL
from characters import figure
from engine import (C, INK, PRESS, PRESS16, SILK, H, W, back_out, clamp, dither, dither_rect, ease_in, lerp, outline_text, paste, ramp, rnd, text_width)
from pixelart import pixel
from pixelart.camera import Cam, compose
from pixelart.gags import Gags
from scene import FEET_Y, GEORGE_X, WASH_X, shadow_under, shore_labels, shores

FPS = TL.FPS
PHASES = ("back", "front", "ui", "top")
GAGS = Gags(PHASES)
# Other sets register here as name -> fn(c) returning the world (RGB), or (fn, front_fn) where
# front_fn(c) draws over the characters (a ship's rail, say). "shores" is built in.
SCENES = {}
# Wreckage of the argument: things the gags leave floating in the Atlantic (see gagkit.debris).
DEBRIS = []
DEBRIS_GONE = TL.section_bounds("v4")[0]      # ...and sinks as Verse 4 turns to the slave trade

SHOTS = {
    "wide": (160, 90, 6), "two": (160, 94, 7),
    "boston": (82, 88, 12), "london": (238, 88, 12),
    "bostonx": (73, 82, 18), "londonx": (247, 84, 18),
    "sea": (160, 112, 12), "sky": (160, 50, 12), "sun": (160, 92, 12),
}
SIDE = {"washington": "boston", "george": "london"}
HOME = {"washington": WASH_X, "george": GEORGE_X}
NAME = {"crier": ("TOWN CRIER", C["green"], C["gold"]), "george": ("GEORGE III", C["red"], C["gold"]),
        "washington": ("G. WASHINGTON", C["navy"], C["buff"])}
LEGEND = {"george": "KING GEORGE III", "washington": "GEN. GEORGE WASHINGTON"}


# --- per-frame context ------------------------------------------------------------------

def default_state(who):
    x = {"washington": WASH_X, "george": GEORGE_X, "crier": 160}[who]
    return dict(x=x, y=FEET_Y, facing=-1 if who == "george" else 1, hidden=who == "crier",
                mouth="closed", eyes="open", brows="neutral", arm="down", mic=False, hat="on", flush=0,
                lean=0, bob=0, bell=False, dx=0, dy=0, rot=0.0, sweat=False, dizzy=False, rim=0.45,
                shadow=True)


class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = TL.RAPPER.get(self.sec)
        self.st = {w: default_state(w) for w in ("washington", "george", "crier")}
        self.scene = "shores"
        self.shot = "wide"
        self.lock_shot = False
        self.karaoke = True
        self.labels = True
        self.card = True
        self.hitfx = True
        self.hit_react = {"washington": True, "george": True}
        self.calm = 0.0              # flattens the sea
        self.rain = 1.0
        self.mood = 0.0              # darkens the world for the sober lines
        self.flash, self.flash_color = 0.0, C["white"]
        self.shake = 0.0
        self.cam = None
        self.world = None
        self.ui = None
        self.anchor = {}

    def to_ui(self, x, y):
        return self.cam.ui(x, y)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color

    def take_shot(self, L, shot, lock=False):
        """Cut to `shot` once line L owns the camera (the previous line's gag keeps it until then,
        and so does the reaction to its big hit)."""
        r = reaction(self)
        if r and L is not None and r[1] is not L.ln:
            return
        if L is None or self.t >= L.t0 - 0.12:
            self.shot = shot
            self.lock_shot = self.lock_shot or lock


# --- posing -------------------------------------------------------------------------------

GESTURES = ["point", "chop", "palm", "point", "fist", "chop", "down", "point"]


def singing(c, who):
    ln = c.ln
    return ln is not None and ln["who"] == who and ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.45


def mouth_for(c, who, rest="closed"):
    if not singing(c, who):
        return rest
    v = TL.loudness(c.t)
    return "wide" if v > 0.78 else "open" if v > 0.45 else "o" if v > 0.2 else "closed"


def pose_rapper(c, who):
    s = c.st[who]
    s["mic"] = True
    s["arm"] = GESTURES[int(rnd(who, c.beat_i // 2) * len(GESTURES))]
    s["bob"] = 1 if c.ph < 0.3 else 0
    s["mouth"] = mouth_for(c, who)
    if who == "george":
        s["brows"] = "up" if s["mouth"] != "wide" else "angry"
    else:
        s["brows"] = "angry" if s["mouth"] == "wide" else "neutral"


def pose_listener(c, who):
    s = c.st[who]
    s["mic"] = False
    s["arm"] = "cross"
    s["bob"] = 1 if (c.beat_i % 2 == 0 and c.ph < 0.3) else 0
    if who == "george":
        s["mouth"], s["brows"], s["eyes"] = "frown", "up", "shut" if (c.beat_i // 4) % 3 == 0 else "open"
    else:
        s["mouth"], s["brows"] = "closed", "neutral"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"washington": (3.3, 0.7), "george": (2.9, 1.9), "crier": (3.7, 0.2)}[who]
        if s["eyes"] == "open" and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The listener flinches as each line lands, and reels from the big ones."""
    for who in ("washington", "george"):
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
            s["arm"] = "palm" if big and age < 0.5 else s["arm"]
        if big:
            s["sweat"] = True
        kb = (4 if big else 1.5) * max(0.0, 1 - age / 0.4)
        s["dx"] += int(round(kb * -s["facing"]))


def hit_shake(c):
    for h in TL.HITS:
        age = c.t - h["t"]
        if 0 <= age < 0.35 and h["big"]:
            c.add_shake(10 * (1 - age / 0.35))


# --- drawing characters ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def draw_char(c, img, who):
    s = c.st[who]
    if s["hidden"]:
        return None
    pose = {k: s[k] for k in ("mouth", "eyes", "brows", "arm", "mic", "hat", "flush", "lean", "bob", "bell")}
    spr, a = figure(who, s["facing"], rim=s["rim"], **pose)
    x, y = int(round(s["x"] + s["dx"])), int(round(s["y"] + s["dy"]))
    ox, oy = x - a["feet"][0], y - a["feet"][1]
    if s["shadow"] and not s["rot"]:
        shadow_under(img, x, y + 1)
    if s["rot"]:
        m = 30
        layer = Image.new("RGBA", (spr.width + 2 * m, spr.height + 2 * m), (0, 0, 0, 0))
        layer.paste(spr, (m, m), spr)
        layer = layer.rotate(s["rot"], resample=Image.NEAREST, center=(m + a["feet"][0], m + a["feet"][1]))
        img.paste(layer, (ox - m, oy - m), layer)
    else:
        img.paste(spr, (ox, oy), spr)
    anchors = {k: (px + ox, py + oy) for k, (px, py) in a.items()}
    if s["sweat"] and not s["rot"]:
        hx, hy = anchors["head"]
        drip = int(c.t * 6) % 3
        d = sweat_drop()
        img.paste(d, (int(hx - s["facing"] * 8) - 1, int(hy - 6 + drip)), d)
    if s["dizzy"]:
        hx, hy = anchors["head"]
        dd = ImageDraw.Draw(img)
        for k in range(3):
            ang = c.t * 7 + k * 2 * math.pi / 3
            dd.point((int(hx + 10 * math.cos(ang)), int(hy - 12 + 3 * math.sin(ang))), fill=C["gold"])
    c.anchor[who] = anchors
    return anchors


# --- karaoke and cards ------------------------------------------------------------------------

BAND_Y = 151


def clean_word(w):
    return w.upper().replace("’", "'").replace("“", '"').replace("”", '"')


def wrap(words, width=304):
    rows, cur = [], []
    for i, w in enumerate(words):
        if cur and text_width(" ".join(words[j] for j in cur + [i]), PRESS) > width:
            rows.append(cur)
            cur = [i]
        else:
            cur.append(i)
    return rows + [cur] if cur else rows


def draw_band(ui, alpha=1.0):
    dither_rect(ui, (0, BAND_Y - 4, W, BAND_Y - 2), C["band"], density=0.35)
    dither_rect(ui, (0, BAND_Y - 2, W, BAND_Y), C["band"], density=0.7)
    ImageDraw.Draw(ui).rectangle((0, BAND_Y, W, H), fill=C["band"] + (255,))
    ImageDraw.Draw(ui).line([(0, BAND_Y), (W, BAND_Y)], fill=C["band_edge"] + (255,))


def speaker_chip(ui, who, y=BAND_Y - 11):
    name, bg, fg = NAME[who]
    tw = text_width(name, SILK)
    d = ImageDraw.Draw(ui)
    x = {"washington": 6, "crier": (W - tw - 8) // 2, "george": W - tw - 14}[who]
    d.rectangle((x, y, x + tw + 7, y + 9), fill=bg + (255,), outline=fg + (255,))
    pixel.text(ui, (x + 4, y - 2), name, SILK, fg, shadow=None)


def draw_karaoke(c):
    ln = c.ln
    if ln is None or not c.karaoke:
        return
    ui = c.ui
    draw_band(ui)
    words = [clean_word(w["w"]) for w in ln["words"]]
    now = TL.word_index(ln, c.t)
    rows = wrap(words)
    space = text_width(" ", PRESS)
    y = BAND_Y + 6 if len(rows) > 1 else BAND_Y + 11
    for row in rows:
        x = (W - text_width(" ".join(words[i] for i in row), PRESS)) // 2
        for i in row:
            if i < now:
                fill, dy, sh = C["text"], 0, (0, 0, 0)
            elif i == now:
                fill, dy, sh = C["gold"], -1, (120, 60, 0)
            else:
                fill, dy, sh = C["dim"], 0, (0, 0, 0)
            pixel.text(ui, (x, y + dy), words[i], PRESS, fill, shadow=sh)
            x += text_width(words[i], PRESS) + space
        y += 11
    speaker_chip(ui, ln["who"])


@lru_cache(maxsize=None)
def ribbon_img(top, bottom, fg, bg):
    """A parchment ribbon banner with swallowtail ends, two lines of text."""
    w = max(text_width(top, PRESS16), text_width(bottom, SILK)) + 28
    h = 34
    im = Image.new("RGBA", (w + 16, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    par, par_sh = C["paper"] + (255,), C["paper_sh"] + (255,)
    for side in (0, 1):
        x = 0 if side == 0 else w + 16
        s = 1 if side == 0 else -1
        d.polygon([(x, 8), (x + s * 14, 8), (x + s * 14, h + 2), (x, h + 2), (x + s * 5, h // 2 + 5)], fill=par_sh,
                  outline=INK + (255,))
    d.rectangle((8, 2, w + 8, h - 2), fill=par, outline=INK + (255,))
    d.line([(9, h - 3), (w + 7, h - 3)], fill=par_sh)
    d.rectangle((10, 4, w + 6, 5), fill=bg + (255,))
    outline_text(im, ((w + 16) // 2, 7), top, PRESS16, fg, INK, anchor="ma")
    pixel.text(im, ((w + 16) // 2, 22), bottom, SILK, INK, shadow=None, anchor="ma")
    return im


def draw_card(c):
    """The verse card: a parchment ribbon drops in as each verse starts."""
    if not c.card or c.sec not in TL.VERSE_NO:
        return
    first = TL.lines_of(c.sec)[0]["t0"]
    age = c.t - (first - 0.55)
    if not 0 <= age < 2.6:
        return
    who = c.rapper
    im = ribbon_img(f"VERSE {TL.VERSE_NO[c.sec]}", LEGEND[who], C["gold"], NAME[who][1])
    drop = back_out(age / 0.35)
    out = ramp(age, 2.2, 2.6)
    y = int(lerp(-40, 18, drop) - out * 60)
    paste(c.ui, im, W // 2, y, "mt")


# --- world ------------------------------------------------------------------------------------

def mood_overlay(img, amount):
    """Darken and cool the whole world by `amount` (0-1) for the sober lines. A flat colour shift, not a
    dither, so it stays clean when the camera zooms in."""
    if amount <= 0:
        return
    a = np.asarray(img, dtype=np.float32)
    k = 0.55 * min(1.0, amount)
    a = a * (1 - k) + np.array((22, 18, 44), np.float32) * k
    lum = a.mean(axis=2, keepdims=True)
    a = a * (1 - 0.35 * k) + lum * 0.35 * k          # and drain some of the colour
    img.paste(Image.fromarray(a.round().astype(np.uint8)))


def reaction(c):
    """(shot, line) while the listener is taking a big hit: 0.9 s after it lands, but only 0.5 s
    into the next line, so the rapper gets the camera back quickly."""
    h = TL.last_hit(c.t, window=0.9)
    if h is None or not h["big"] or h["line"]["sec"] != c.sec:
        return None
    if c.ln is not h["line"] and c.t - h["t"] >= 0.5:
        return None
    return SIDE[h["target"]], h["line"]


def default_shot(c):
    ln = c.ln
    if ln is None or ln["sec"] != c.sec or c.sec not in TL.VERSE_NO:
        return "wide"
    r = c.rapper
    react = reaction(c)
    if react:
        return react[0]
    return ["wide", SIDE[r], "two", SIDE[r] + "x" if ln["idx"] % 8 == 3 else SIDE[r]][ln["idx"] % 4]


def resolve_shot(shot):
    if isinstance(shot, Cam):
        return shot
    return Cam(*(SHOTS[shot] if isinstance(shot, str) else shot))


def draw_debris(c):
    """What the first three verses threw in the sea. It all goes under as Verse 4 opens on the slave trade."""
    from props import float_on_water
    under = ease_in(ramp(c.t, DEBRIS_GONE - 0.4, DEBRIS_GONE + 1.2))
    for d in DEBRIS:
        if d["t0"] <= c.t < d["t1"]:
            age = c.t - d["t0"]
            x = clamp(d["x"] + d["drift"] * age, 106, 214)
            spr = d["img"]()
            sink = d["sink"] + int(round(under * (spr.height + 4))) + (d["seed"] % 3) * (under > 0)
            float_on_water(c.world, spr, x, d["y"], c.t, seed=d["seed"], sink=sink)


def verse_setup(c):
    r = c.rapper
    if r in ("washington", "george"):
        pose_rapper(c, r)
        pose_listener(c, TL.OTHER[r])
        c.shot = default_shot(c)
    else:
        for who in ("washington", "george"):
            pose_listener(c, who)


def shake_offset(c):
    if c.shake < 0.5:
        return (0, 0)
    a = rnd("shake", c.f) * 2 * math.pi
    return (int(round(math.cos(a) * c.shake)), int(round(math.sin(a) * c.shake)))


def render_frame(t):
    import gags  # noqa: F401  (registers the per-line gags into GAGS)
    c = Ctx(t)
    verse_setup(c)
    runner = GAGS.runner(c, t, TL.LINES, TL.section_end)
    blink_eyes(c)
    apply_hits(c)
    if c.hitfx:
        hit_shake(c)
    c.cam = resolve_shot(c.shot)
    front = None
    if c.scene == "shores":
        world = shores(t, c.calm, c.rain)
    else:
        fn = SCENES[c.scene]
        fn, front = fn if isinstance(fn, tuple) else (fn, None)
        world = fn(c)
    c.world = world
    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if c.scene == "shores":
        draw_debris(c)
    runner.run("back")
    for who in ("washington", "george", "crier"):
        draw_char(c, world, who)
    if front:
        front(c)
    runner.run("front")
    mood_overlay(world, c.mood)
    if c.flash > 0:
        dither(world, c.flash, c.flash_color, blend=0.8)
    if c.labels and c.scene == "shores":
        shore_labels(c.ui, c.cam)
    runner.run("ui")
    draw_karaoke(c)
    draw_card(c)
    runner.run("top")
    return compose(world, c.ui, c.cam, shake_offset(c))


def label(t):
    ln = TL.line_at(t)
    return f"{ln['sec']}.{ln['idx']} {ln['text']}" if ln else TL.section_at(t)[0]
