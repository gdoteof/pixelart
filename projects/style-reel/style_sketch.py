"""Pencil sketch: graphite line over coloured-pencil hatching, on dotted paper. Nothing is ever redrawn
quite the same, so the line boils (a new tracing every three frames); new things draw themselves on, and
the lyric is written out as it is sung."""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image

import acting
import props
import puppet
import script as S
import sk

NAME = "Pencil sketch"
WEB_CRF = 26                                 # a boiling line is expensive to compress
PAPER, LEAD, RED = (250, 247, 238), (60, 58, 68), (206, 52, 60)
ASMON_AT, HASAN_AT = (372, 440, 150), (1556, 455, 140)
BOARD = (622, 120, 0.676)
DESK_Y = 950
ANGLE = {"skin": 38, "skin_sh": -52, "stub": -52, "hair": 78, "hair_sh": 82, "beard": 70, "top": -40, "phones": 20,
         "roof": 8, "hedge": 60, "frond": 30, "flag": -30, "window": 45, "door": 80, "trunk": 85, "tub_sh": -20,
         "wall_sh": 0, "foot": 20, "water": 60, "fade": 78, "brow": 10, "mouth": 60, "tongue": 30, "iris": 45}


def boil(t):
    """Which tracing this frame shows: a new one every three frames."""
    return S.frame_no(S.hold(t, 3)) // 3


def pencil(colour, width, seed, alpha=0.85, wobble=1.5):
    p = sk.stroke(colour, width, alpha)
    p.setPathEffect(skia.DiscretePathEffect.Make(13, wobble, seed))
    return p


def hatch(c, path, colour, angle, gap, seed, alpha=0.6, width=1.7):
    """Shade a shape with a run of pencil strokes."""
    b = path.getBounds()
    if b.isEmpty():
        return
    cx, cy, r = b.centerX(), b.centerY(), math.hypot(b.width(), b.height()) / 2 + 6
    lines = skia.Path()
    n = int(r / gap) + 1
    for k in range(-n, n + 1):
        y = cy + k * gap + (S.rnd("h", seed, k) - 0.5) * gap * 0.5
        lines.moveTo(cx - r, y)
        lines.lineTo(cx + r, y + (S.rnd("s", seed, k) - 0.5) * gap)
    lines.transform(sk.matrix(rot=angle, about=(cx, cy)))
    c.save()
    c.clipPath(path, True)
    c.drawPath(lines, pencil(colour, width, seed, alpha, 1.8))
    c.restore()


def draw(c, parts, seed, grow=None, weight=1.0):
    """Parts in pencil. `grow` gives each part how much of it has been drawn yet, 0..1 (None: all of it)."""
    for i, q in enumerate(parts):
        k = 1.0 if grow is None else S.clamp(grow(i))
        if k <= 0:
            continue
        col = puppet.colour(q.who, q.col)
        sd = seed * 7919 + i * 31
        dark = sum(col) < 250
        if q.open:
            path = q.path if k >= 1 else sk.part(q.path, 0, k)
            c.drawPath(path, pencil(col if not q.line else LEAD, max(1.6, q.w * 0.8), sd, 0.85))
            continue
        if k >= 1 or grow is None:
            if not q.shade:
                c.drawPath(q.path, sk.fill(PAPER))                    # rub out what is behind it
            if sum(col) < 700:                                        # anything paler is left as paper
                if not q.shade:
                    c.drawPath(q.path, sk.fill(col, 0.26))
                hatch(c, q.path, col if not q.shade else LEAD, ANGLE.get(q.col, 45) + (S.rnd("a", sd % 9973) - 0.5) * 6,
                      4.2 if dark else 7.0, sd, 0.42 if q.shade else 0.62)
                if dark and not q.shade:
                    hatch(c, q.path, col, ANGLE.get(q.col, 45) - 62, 6.5, sd + 5, 0.45)
        if q.line:
            w = (2.7 if q.line == 2 else 1.9) * weight
            path = q.path if k >= 1 else sk.part(q.path, 0, k)
            path_m = q.mask
            for n in range(2 if q.line == 2 else 1):                  # twice over, never in quite the same place
                if path_m is not None:
                    c.save()
                    c.clipPath(path_m, skia.ClipOp.kDifference, True)
                    c.drawPath(path, pencil(LEAD, w, sd + n * 13, 0.8 - 0.25 * n, 1.5 + n))
                    c.restore()
                else:
                    c.drawPath(path, pencil(LEAD, w, sd + n * 13, 0.8 - 0.25 * n, 1.5 + n))


@lru_cache(maxsize=None)
def paper():
    """The page: tooth and a little unevenness, to multiply over the drawing; and its dot grid."""
    g = 0.94 + 0.06 * sk.cloud(S.W, S.H, 21, cell=140) + sk.grain(S.W, S.H, 8, 1, -0.045, 0.045)
    yy, xx = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
    edge = np.clip(np.hypot((xx - S.W / 2) / S.W, (yy - S.H / 2) / S.H) * 1.6 - 0.45, 0, 1)
    return (g * (1 - 0.12 * edge))[..., None]


@lru_cache(maxsize=None)
def page():
    s = sk.surface(S.W, S.H, PAPER)
    c = s.getCanvas()
    dot = sk.fill((150, 170, 200), 0.55)
    for y in range(30, S.H, 40):
        for x in range(30, S.W, 40):
            c.drawCircle(x, y, 1.7, dot)
    return s.makeImageSnapshot()


def ground(c, b):
    """A quick block of colour behind each man, and the edge of the desk."""
    for (x0, x1), col, a in (((90, 700), (86, 170, 110), 48), ((1230, 1860), (140, 110, 220), -48)):
        hatch(c, sk.rect(x0, 150, x1, DESK_Y), col, a, 15, b * 3 + x0, 0.5, 5.0)
    for k in range(2):
        c.drawPath(sk.poly([(40, DESK_Y + k * 3), (S.W - 40, DESK_Y - k * 2)], closed=False), pencil(LEAD, 3.0, b + k, 0.85, 2.0))
    hatch(c, sk.rect(40, DESK_Y + 6, S.W - 40, DESK_Y + 40), LEAD, 80, 9, b + 90, 0.35)


def scene_house(c, t, b):
    age = t - S.EV["mansion"]
    if age >= 0:                                            # the house draws itself, part by part
        draw(c, props.house(), 3 + b, lambda i: (age - i * 0.006) / 0.14 if age < 0.75 else 1.0, 0.9)
    c.drawPath(sk.poly([(10, 500), (990, 502)], closed=False), pencil(LEAD, 2.6, b + 40, 0.8))
    draw(c, props.flag(t), 4 + b, None, 0.9)
    for i, x in enumerate(props.TUB_X):
        t0 = S.EV["tubs"][i] if i < 5 else S.EV["half"]
        if t >= t0:
            tub = props.placed(props.tub(i == 5), sk.matrix(x, props.TUB_Y - 40, props.TUB_K, about=(0.0, 40.0)))
            draw(c, tub, 50 + i + b, lambda _, k=(t - t0) / 0.1: k, 0.9)
    k = S.clamp((t - S.EV["baths"]) / 0.3)
    if k > 0:
        x, y, rot = props.STAMP
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        ring = sk.xf(sk.oval(0, 0, 205, 72), rot=-3)
        for n in range(2):
            c.drawPath(sk.part(sk.xf(ring, s=1 + 0.06 * n, rot=8 * n), 0, min(1.0, k * 1.4)), pencil(RED, 4.5, b + n, 0.85, 2.4))
        if k > 0.4:
            sk.text(c, "5½ baths!", 0, 22, sk.font("hand", 62), sk.fill(RED, 0.92), "m")
        c.restore()


def scene_score(c, t, b):
    sk.text(c, "BATHS THIS YEAR", 500, 108, sk.font("hand", 66), sk.fill(LEAD, 0.92), "m")
    for k in range(2):
        c.drawPath(sk.poly([(120, 132 + k * 12), (880, 128 + k * 12)], closed=False), pencil(LEAD, 3, b + k, 0.85, 2.2))
    c.drawPath(sk.poly([(500, 170), (498, 690)], closed=False), pencil(LEAD, 3, b + 3, 0.85, 2.2))
    for key, name, col in (("him", "him", (120, 90, 210)), ("me", "me", (60, 150, 80))):
        x0, y0, x1, y1 = props.SCORE[key]
        sk.text(c, name, (x0 + x1) / 2, y0 + 96, sk.font("hand", 64), sk.fill(col, 0.95), "m")
    x0, y0, x1, y1 = props.SCORE["him"]
    sk.text(c, "5½", (x0 + x1) / 2, y1 - 110, sk.font("hand", 240), sk.fill((120, 90, 210), 0.92), "m")
    x0, y0, x1, y1 = props.SCORE["me"]
    cx, cy = (x0 + x1) / 2, y1 - 110
    if t < S.EV["ive"]:
        sk.text(c, "?", cx, cy, sk.font("hand", 240), sk.fill(LEAD, 0.5), "m")
    elif t < S.EV["had"]:                                   # he scribbles while he works it out
        scr = sk.curve([(cx - 110 + 220 * S.rnd("sx", b, k), cy - 190 + 170 * S.rnd("sy", b, k)) for k in range(14)], closed=False)
        c.drawPath(scr, pencil(LEAD, 4, b, 0.7, 3))
    else:
        k = S.clamp((t - S.EV["had"]) / 0.22)
        sk.text(c, "0", cx, cy, sk.font("hand", 250), sk.fill(RED, 0.95), "m")
        ring = sk.oval(cx + 6, cy - 86, 150, 132)
        for n in range(2):
            c.drawPath(sk.part(sk.xf(ring, rot=12 * n + 200, about=(cx, cy - 86)), 0, k), pencil(RED, 5, b + n, 0.85, 3))
        if k >= 1:
            for n in range(9):
                a = -math.pi * (0.08 + 0.84 * n / 8)
                c.drawPath(sk.poly([(cx + 175 * math.cos(a), cy - 86 + 160 * math.sin(a)),
                                    (cx + 215 * math.cos(a), cy - 86 + 200 * math.sin(a))], closed=False), pencil(RED, 4, b + n, 0.85))


def board(c, t, b):
    x, y, k = BOARD
    w, h = props.BOARD[0] * k, props.BOARD[1] * k
    sheet = sk.rect(x - 14, y - 14, x + w + 14, y + h + 14)
    c.drawPath(sheet, sk.fill(PAPER))
    for n in range(2):
        c.drawPath(sheet, pencil(LEAD, 3.2, b + n * 7, 0.85 - 0.3 * n, 1.6 + n))
    c.save()
    c.translate(x, y)
    c.scale(k, k)
    if t < S.EV["line2"]:
        scene_house(c, t, b)
    else:
        scene_score(c, t, b)
    c.restore()


def written(c, t, b):
    """The lyric in his own hand: each word is written as it is sung, and the one being sung is underlined."""
    line, words = S.caption(t)
    if not line:
        return
    fnt = sk.font("hand", 52)
    gap = 22
    widths = [sk.text_width(w, fnt) for w, _ in words]
    x = S.W / 2 - (sum(widths) + gap * (len(words) - 1)) / 2
    for (w, st), wd, (_, a, z) in zip(words, widths, line["words"]):
        if st:
            k = 1.0 if st == 2 else S.clamp((t - a) / max(0.08, (z - a) * 0.7))
            c.save()
            c.clipRect(skia.Rect.MakeLTRB(x - 6, 960, x + (wd + 12) * k - 6, 1076))
            sk.text(c, w, x, 1034, fnt, sk.fill(LEAD, 0.95))
            c.restore()
            if st == 1:
                c.drawPath(sk.poly([(x, 1050), (x + wd * k, 1048)], closed=False), pencil(RED, 4.5, b, 0.9, 2.5))
        x += wd + gap


def frame(t):
    b = boil(t)
    th = S.hold(t, 2)
    s = sk.surface(S.W, S.H)
    c = s.getCanvas()
    c.drawImage(page(), 0, 0)
    ground(c, b)
    board(c, t, b)
    for who, at, seed in (("asmon", ASMON_AT, 1), ("hasan", HASAN_AT, 2)):
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, 0, S.W, DESK_Y - 2))
        draw(c, puppet.figure(who, acting.pose(who, th), at), seed * 100 + b)
        c.restore()
    ax, ay, sc = ASMON_AT
    for path, strength in props.stink(th):
        c.drawPath(sk.xf(path, ax, ay, sc), pencil((110, 140, 50), 4, b, 0.8 * strength, 2.2))
    for n, (fx, fy, wing, heading) in enumerate(props.flies(th)):
        x, y = ax + fx * sc, ay + fy * sc
        trail = [(ax + q[n][0] * sc, ay + q[n][1] * sc) for q in (props.flies(th - d * 0.035) for d in range(1, 9)) if len(q) > n]
        if len(trail) > 2:
            dash = pencil(LEAD, 1.8, b + n, 0.6, 1.0)
            dash.setPathEffect(skia.DashPathEffect.Make([7, 8], 0))
            c.drawPath(sk.curve([(x, y)] + trail, closed=False), dash)
        c.drawCircle(x, y, 7, sk.fill(LEAD, 0.9))
        for side in (-1, 1):
            c.drawPath(sk.oval(x + side * 8, y - 9, 7, 4 + 3 * wing, rot=side * 30), pencil(LEAD, 1.8, b + n + side, 0.85, 0.8))
    written(c, t, b)
    out = np.asarray(sk.array(s)[..., :3], np.float32) * paper()
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
