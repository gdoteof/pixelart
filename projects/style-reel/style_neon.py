"""Neon sign: everything is a bent glass tube on a brick wall at night. A tube is either lit or dark, so
nothing glides: a sign strikes with a flicker, a figure switches between the poses it was bent in, and
the tubes that have not come on yet can be seen waiting as dark glass."""
from functools import lru_cache

import numpy as np
import skia
from PIL import Image

import acting
import props
import puppet
import script as S
import sk

NAME = "Neon sign"
ASMON_AT, HASAN_AT = (372, 462, 150), (1556, 476, 140)
BOARD = (622, 150, 0.676)
DESK_Y = 938
GAS = dict(red=(255, 52, 44), orange=(255, 128, 30), amber=(255, 186, 48), yellow=(255, 232, 70), green=(60, 255, 110),
           cyan=(50, 226, 255), blue=(64, 120, 255), violet=(176, 96, 255), pink=(255, 70, 170), white=(255, 236, 214),
           skin=(255, 150, 112))
# What each part of a man is bent from: (gas, tube width); parts not named here are left out.
TUBES = {
    ("asmon", "hair_back"): ("orange", 7), ("asmon", "lock"): ("orange", 7), ("asmon", "wisp"): ("amber", 3.5),
    ("asmon", "beard"): ("amber", 7), ("asmon", "tee"): ("green", 7), ("asmon", "sleeve"): ("green", 7),
    ("asmon", "band"): ("cyan", 6), ("asmon", "cup"): ("cyan", 6), ("asmon", "mouth"): ("red", 5),
    ("asmon", "brow"): ("amber", 0),
    ("hasan", "hair"): ("blue", 7), ("hasan", "hair_hi"): ("cyan", 3.5), ("hasan", "tank"): ("white", 7),
    ("hasan", "chain"): ("yellow", 4.5), ("hasan", "lips"): ("red", 6), ("hasan", "brow"): ("blue", 0),
    ("hasan", "torso"): ("skin", 7), ("hasan", "ear"): ("skin", 5),
    "head": ("skin", 7), "nose": ("skin", 5), "eye": ("white", 4), "pupil": ("white", 0), "lash": ("white", 4),
    "upper": ("skin", 7), "fore": ("skin", 7), "hand": ("skin", 6),
}
HOUSE = {"trunk": ("green", 6), "frond": ("green", 4), "wing": ("white", 5), "roof": ("red", 5), "window": ("amber", 4),
         "block": ("white", 5), "pediment": ("white", 5), "oculus": ("amber", 4), "door": ("amber", 5),
         "column": ("white", 3.5), "hedge": ("green", 4)}
TUB = {"tub": ("cyan", 5), "rim": ("cyan", 5), "bubble": ("white", 3), "foot": ("amber", 3.5), "drop": ("cyan", 3)}
SOLID = {"neck"}                 # not drawn, but it hides what is behind it


class Sign:
    """Two pictures built together: the glass (every tube, lit or not) and the light (the lit ones, in colour)."""

    def __init__(self):
        self.glass, self.light = sk.surface(S.W, S.H, (0, 0, 0)), sk.surface(S.W, S.H, (0, 0, 0))
        self.both = (self.glass.getCanvas(), self.light.getCanvas())

    def each(self, fn):
        for c in self.both:
            fn(c)

    def hide(self, path):
        """Something solid in front: no tube shows through it."""
        self.each(lambda c: c.drawPath(path, sk.fill((0, 0, 0))))

    def tube(self, path, gas, width, level=1.0):
        """A tube along this path; width 0 fills the shape instead (a short fat tube)."""
        r, g, b = GAS[gas]
        k = S.clamp(level)
        for c, col in zip(self.both, ((255, 255, 255), (r * k, g * k, b * k))):
            c.drawPath(path, sk.stroke(col, width) if width else sk.fill(col))

    def text(self, s, x, y, fnt, gas, level=1.0, align="m", width=0.0):
        r, g, b = GAS[gas]
        k = S.clamp(level)
        for c, col in zip(self.both, ((255, 255, 255), (r * k, g * k, b * k))):
            sk.text(c, s, x, y, fnt, sk.stroke(col, width) if width else sk.fill(col), align)


def strike(t, t0, seed=0, dur=0.3):
    """A tube coming on at t0: it stutters, catches, and then only buzzes a little."""
    if t < t0:
        return 0.0
    f = S.frame_no(t)
    if t < t0 + dur:
        return 1.0 if S.rnd("strike", seed, f) < 0.35 + 0.65 * (t - t0) / dur else 0.12
    return 0.93 + 0.07 * S.rnd("buzz", seed, f // 2)


def figure(sign, who, pose, at, level):
    """A man in tubes: each part's outline, with whatever is in front of it hiding it."""
    for q in puppet.figure(who, pose, at):
        spec = TUBES.get((who, q.name)) or TUBES.get(q.name)
        if q.shade or (spec is None and q.name not in SOLID):
            continue
        if q.name in SOLID:
            sign.hide(q.path)
            continue
        gas, width = spec
        if not q.open and width:
            sign.hide(q.path)
        sign.tube(q.path, gas, width, level)


def placed(sign, parts, table, level, m=None):
    for q in parts:
        spec = table.get(q.name)
        if q.shade or spec is None:
            continue
        path = q.path if m is None else sk.xf(q.path, m=m)
        if not q.open:
            sign.hide(path)
        sign.tube(path, spec[0], spec[1], level)


def scene_house(sign, t, m):
    placed(sign, props.house(), HOUSE, strike(t, S.EV["mansion"], 1, 0.34), m)
    if t >= S.EV["austere"] - 1.2:                       # the flag: dark glass, then red on "austere"
        on = strike(t, S.EV["austere"], 2, 0.2)
        wave = 70.5 + (S.frame_no(t) // 5 % 2) * 0.21        # two positions, lit in turn
        for q in props.flag(wave):
            path = sk.xf(q.path, m=m)
            if q.name == "pole":
                sign.tube(path, "white", 3.5, on)
            elif q.name == "flag":
                sign.hide(path)
                sign.tube(path, "red", 5, on)
            else:
                sign.tube(path, "yellow", 0, on)
    for i, x in enumerate(props.TUB_X):                     # six tubs of dark glass, counted on one at a time
        t0 = S.EV["tubs"][i] if i < 5 else S.EV["half"]
        mt = skia.Matrix.Concat(m, sk.matrix(x, props.TUB_Y - 40, props.TUB_K, about=(0.0, 40.0)))
        placed(sign, props.tub(i == 5), TUB, strike(t, t0, 10 + i, 0.07), mt)
    x, y, rot = props.STAMP
    ms = skia.Matrix.Concat(m, sk.matrix(x, y, rot=rot))
    on = strike(t, S.EV["baths"], 3, 0.26)
    words = sk.text_path("5½ baths", sk.font("lobster", 104), 0, 34, "m")
    sign.hide(sk.xf(sk.rect(-200, -64, 200, 60, 20), m=ms))
    sign.tube(sk.xf(sk.rect(-200, -64, 200, 60, 20), m=ms), "pink", 4, on)
    sign.tube(sk.xf(words, m=ms), "pink", 0, on * 0.55)
    sign.tube(sk.xf(words, m=ms), "white", 2.2, on)


def scene_score(sign, t, m):
    def at(x, y):
        q = m.mapXY(x, y)
        return q.x(), q.y()

    k = m.getScaleX()
    on = strike(t, S.EV["line2"] + 0.05, 4, 0.24)
    sign.text("BATHS THIS YEAR", *at(500, 108), sk.font("cond", 100 * k), "yellow", on)
    sign.tube(sk.xf(sk.poly([(60, 140), (940, 140)], closed=False), m=m), "yellow", 4, on)
    sign.tube(sk.xf(sk.poly([(500, 176), (500, 680)], closed=False), m=m), "white", 4, on)
    for key, name, gas in (("him", "HIM", "violet"), ("me", "ME", "green")):
        x0, y0, x1, y1 = props.SCORE[key]
        sign.text(name, *at((x0 + x1) / 2, y0 + 96), sk.font("cond", 76 * k), gas, on)
    x0, y0, x1, y1 = props.SCORE["him"]
    big = sk.font("black", 300 * k)
    sign.text("5½", *at((x0 + x1) / 2, y1 - 92), big, "violet", on * 0.4)
    sign.text("5½", *at((x0 + x1) / 2, y1 - 92), big, "violet", on, width=5)
    x0, y0, x1, y1 = props.SCORE["me"]
    cx, cy = at((x0 + x1) / 2, y1 - 92)
    had = S.EV["had"]
    if t < had:                                             # the question mark: on and off with the beat, then faster
        fast = t >= S.EV["ive"]
        blink = (S.frame_no(t) // 2 % 2) if fast else (S.beat(t)[1] < 0.55)
        q = on * (1.0 if blink else 0.0)
        sign.text("0", cx, cy, big, "red", 0.0, width=5)
        sign.text("?", cx, cy, big, "amber", q * 0.4)
        sign.text("?", cx, cy, big, "amber", q, width=5)
    else:
        z = strike(t, had, 5, 0.16)
        sign.text("?", cx, cy, big, "amber", 0.0, width=5)
        sign.text("0", cx, cy, big, "red", z * 0.5)
        sign.text("0", cx, cy, big, "red", z, width=6)


def board(sign, t):
    x, y, k = BOARD
    w, h = props.BOARD[0] * k, props.BOARD[1] * k
    m = sk.matrix(x, y, k)
    sign.tube(sk.rect(x - 22, y - 22, x + w + 22, y + h + 22, 30), "blue", 6, strike(t, S.T0 + 0.22, 6, 0.3))
    gap = abs(t - S.EV["line2"]) < 0.045                    # the sign goes dark for a moment as it changes over
    if t < S.EV["line2"]:
        scene_house(sign, t if not gap else S.T0 - 1, m)
    else:
        scene_score(sign, t if not gap else S.T0 - 1, m)


def names(sign, t):
    for who, at, gas, text, t0 in (("asmon", ASMON_AT, "green", "Asmongold", 0.08), ("hasan", HASAN_AT, "violet", "HasanAbi", 0.34)):
        on = strike(t, S.T0 + t0, len(text), 0.36)
        fnt = sk.font("lobster", 78)
        sign.text(text, at[0], 112, fnt, gas, on * 0.5)
        sign.text(text, at[0], 112, fnt, "white", on, width=2)
        w = sk.text_width(text, fnt)
        sign.tube(sk.poly([(at[0] - w / 2, 136), (at[0] + w / 2, 136)], closed=False), gas, 4, on)


def caption(sign, t):
    line, words = S.caption(t)
    if not line:
        return
    fnt = sk.font("cond", 60)
    gap = 18
    text = [w.upper() for w, _ in words]
    widths = [sk.text_width(w, fnt) for w in text]
    x = S.W / 2 - (sum(widths) + gap * (len(text) - 1)) / 2
    gas = "green" if line["who"].lower().startswith("asmon") else "violet"
    for i, (w, (_, st), wd) in enumerate(zip(text, words, widths)):
        if st == 1:
            sign.text(w, x, 1030, fnt, "white", 1.0, "l")
        else:
            sign.text(w, x, 1030, fnt, gas, 0.8 if st == 2 else 0.0, "l")
        x += wd + gap


@lru_cache(maxsize=None)
def wall():
    """The brick wall, as how much light each pixel gives back (0..1, RGB)."""
    s = sk.surface(S.W, S.H, (44, 34, 40))
    c = s.getCanvas()
    bw, bh = 96, 38
    for row in range(S.H // bh + 1):
        for col in range(-1, S.W // bw + 1):
            x, y = col * bw + (bw // 2 if row % 2 else 0), row * bh
            k = 0.78 + 0.44 * S.rnd("brick", row, col)
            c.drawRect(skia.Rect.MakeXYWH(x + 2, y + 2, bw - 4, bh - 4),
                       sk.fill((min(255, 120 * k), min(255, 70 * k), min(255, 66 * k))))
    a = sk.array(s)[..., :3].astype(np.float32) / 255
    a *= (0.75 + 0.25 * sk.cloud(S.W, S.H, 5, cell=180) + sk.grain(S.W, S.H, 6, 1, -0.06, 0.06))[..., None]
    yy, xx = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
    a *= (1 - 0.35 * np.clip(np.hypot((xx - S.W / 2) / S.W, (yy - S.H / 2) / S.H) * 1.7 - 0.3, 0, 1))[..., None]
    return a


def blur(img, sigma, scale=1):
    """The picture blurred, as floats; big blurs are done small and scaled back up."""
    w, h = S.W // scale, S.H // scale
    s = sk.surface(w, h, (0, 0, 0))
    c = s.getCanvas()
    p = skia.Paint()
    p.setImageFilter(skia.ImageFilters.Blur(sigma / scale, sigma / scale))
    c.save()
    c.scale(1 / scale, 1 / scale)
    c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)
    c.restore()
    a = sk.array(s)[..., :3]
    if scale > 1:
        a = np.asarray(Image.fromarray(a).resize((S.W, S.H), Image.BILINEAR))
    return a.astype(np.float32)


def frame(t):
    th = S.hold(t, 3)                                       # a pose is a set of tubes: it switches, never glides
    sign = Sign()
    names(sign, t)
    board(sign, t)
    for who, at, t0, seed in (("asmon", ASMON_AT, 0.02, 21), ("hasan", HASAN_AT, 0.28, 22)):
        pose = acting.pose(who, th, snap=True)
        if who == "asmon" and S.singing(t):
            pose = pose.say(S.mouth(S.hold(t, 2)))
        figure(sign, who, pose, at, strike(t, S.T0 + t0, seed, 0.4))
    ax, ay, sc = ASMON_AT
    for i, (path, strength) in enumerate(props.stink(S.hold(t, 4))):
        sign.tube(sk.xf(path, ax, ay, sc), "green", 5, 1.0 if strength > 0.25 else 0.0)
    for fx, fy, wing, heading in props.flies(th):
        x, y = ax + fx * sc, ay + fy * sc
        up = S.frame_no(t) // 2 % 2
        sign.tube(sk.oval(x, y, 9, 7), "yellow", 0, 1.0)
        for side in (-1, 1):
            sign.tube(sk.oval(x + side * 11, y - 10, 9, 5, rot=side * (20 + 40 * up)), "white", 2.5, 1.0)
    sign.hide(sk.rect(0, DESK_Y - 4, S.W, S.H))
    sign.tube(sk.poly([(60, DESK_Y), (S.W - 60, DESK_Y)], closed=False), "pink", 7, strike(t, S.T0 + 0.16, 8, 0.3))
    caption(sign, t)

    glass = sk.array(sign.glass)[..., :1].astype(np.float32) / 255
    lit = sign.light.makeImageSnapshot()
    core = blur(lit, 1.1)
    spill = 4 * blur(lit, 40, 4) + 7 * blur(lit, 100, 8)
    out = wall() * (34 + 130 * (1 - np.exp(-spill / 130)))  # the wall, by the signs' own light
    out = out * (1 - 0.55 * glass) + glass * np.array((30, 30, 40), np.float32)       # dark glass
    out += 0.95 * blur(lit, 5) + 0.6 * blur(lit, 22, 2)     # the glow
    out += core + 0.62 * core.max(axis=2, keepdims=True)    # the tube itself, burnt nearly white
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
