"""Two-colour print: fluorescent pink and blue ink on cream paper, as a risograph lays them down. Every
tone is a screen of dots in one ink or both, the two layers never quite line up, and the ink goes on
unevenly. Printed on twos, with the registration slipping from sheet to sheet."""
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

NAME = "Two-colour print"
WEB_CRF = 25
PAPER = np.array((245, 240, 226), np.float32)
PINK = np.array((255, 72, 150), np.float32)
BLUE = np.array((0, 104, 190), np.float32)
ASMON_AT, HASAN_AT = (372, 440, 150), (1556, 455, 140)
BOARD = (622, 120, 0.676)
DESK_Y = 950
# How much of each ink (pink, blue) a thing gets.
COVER = {
    ("hasan", "skin"): (0.30, 0), ("hasan", "skin_sh"): (0.55, 0), ("hasan", "stub"): (0.34, 0.34),
    ("hasan", "hair"): (0.55, 1), ("hasan", "hair_hi"): (0.2, 0.45), ("hasan", "fade"): (0.4, 0.6),
    ("hasan", "brow"): (0.5, 1), ("hasan", "iris"): (0.3, 0.9), ("hasan", "top"): (0, 0), ("hasan", "chain"): (1, 0),
    ("hasan", "tooth"): (0, 0),
    ("asmon", "skin"): (0.15, 0), ("asmon", "skin_sh"): (0.40, 0), ("asmon", "hair"): (1, 0.22),
    ("asmon", "hair_sh"): (1, 0.5), ("asmon", "hair_hi"): (0.55, 0), ("asmon", "beard"): (1, 0.55),
    ("asmon", "brow"): (1, 0.6), ("asmon", "iris"): (0, 0.8), ("asmon", "top"): (0.12, 1), ("asmon", "phones"): (0.5, 1),
    ("asmon", "phones_hi"): (0, 0.45), ("asmon", "tooth"): (0.1, 0),
    "eye": (0, 0), "pupil": (0.5, 1), "mouth": (1, 0.6), "tongue": (0.7, 0), "ink": (0.5, 1),
    ("prop", "wall"): (0.05, 0), ("prop", "wall_sh"): (0.22, 0), ("prop", "roof"): (1, 0), ("prop", "stone"): (0, 0),
    ("prop", "door"): (0.8, 0.7), ("prop", "window"): (0.5, 0), ("prop", "hedge"): (0, 0.62), ("prop", "trunk"): (0.6, 0.45),
    ("prop", "frond"): (0, 0.85), ("prop", "pole"): (0.3, 1), ("prop", "flag"): (1, 0), ("prop", "star"): (0, 0),
    ("prop", "tub"): (0, 0), ("prop", "tub_sh"): (0, 0.34), ("prop", "foot"): (0.7, 0), ("prop", "water"): (0, 0.6),
    ("prop", "bubble"): (0, 0.12), ("prop", "fly"): (0.5, 1), ("prop", "wing"): (0, 0.2),
}


def plate(pink, blue):
    """The paint that lays down this much of each ink: pink rides in the red channel, blue in the blue."""
    return (255 * pink, 0, 255 * blue)


def cover(q):
    return COVER.get((q.who, q.col)) or COVER[q.col]


def lay(c, parts, key=3.2):
    """Each part knocks out what is under it; the contours are then overprinted in blue, as a key plate."""
    for q in parts:
        col = plate(*cover(q))
        c.drawPath(q.path, sk.stroke(col, q.w) if q.open else sk.fill(col))
        if key and q.line == 2 and not q.open and not q.shade:
            pen = sk.stroke(plate(0, 1), key)
            pen.setBlendMode(skia.BlendMode.kPlus)
            if q.mask is not None:
                c.save()
                c.clipPath(q.mask, skia.ClipOp.kDifference, True)
                c.drawPath(q.path, pen)
                c.restore()
            else:
                c.drawPath(q.path, pen)


@lru_cache(maxsize=None)
def screens():
    """The two halftone screens, at different angles: each pixel's threshold, 0..1."""
    yy, xx = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
    out = []
    for angle, pitch in ((75, 6.4), (15, 6.4)):
        a = math.radians(angle)
        u, v = xx * math.cos(a) + yy * math.sin(a), -xx * math.sin(a) + yy * math.cos(a)
        out.append((np.cos(2 * math.pi * u / pitch) + np.cos(2 * math.pi * v / pitch)) / 4 + 0.5)
    return out


@lru_cache(maxsize=8)
def mottle(sheet):
    """How unevenly each ink went on for this sheet, and the paper under it."""
    pink = 0.80 + 0.20 * sk.cloud(S.W, S.H, 100 + sheet, cell=26, octaves=3) + sk.grain(S.W, S.H, 300 + sheet, 2, -0.06, 0.06)
    blue = 0.82 + 0.18 * sk.cloud(S.W, S.H, 200 + sheet, cell=30, octaves=3) + sk.grain(S.W, S.H, 400 + sheet, 2, -0.06, 0.06)
    return pink, blue


@lru_cache(maxsize=None)
def stock():
    return (0.955 + 0.045 * sk.cloud(S.W, S.H, 7, cell=90) + sk.grain(S.W, S.H, 9, 1, -0.03, 0.03))[..., None]


def press(plates, sheet):
    """Print the plates: screen each ink into dots, slip the blue a little out of register, lay both on paper."""
    cov = [plates[..., 0].astype(np.float32) / 255, plates[..., 2].astype(np.float32) / 255]
    slip = (2 + int(S.rnd("sx", sheet) * 3) - 1, -2 + int(S.rnd("sy", sheet) * 3) - 1)
    cov[1] = np.roll(cov[1], slip, (1, 0))
    out = np.broadcast_to(PAPER, (S.H, S.W, 3)) * stock()
    for c, screen, ink, uneven in zip(cov, screens(), (PINK, BLUE), mottle(sheet % 4)):
        dots = np.clip((c - screen) * 9 + 0.5, 0, 1)
        dots = np.where(c > 0.96, 1.0, np.where(c < 0.02, 0.0, dots)) * np.clip(uneven, 0, 1)
        out = out * (1 - dots[..., None] * (1 - ink / 255))
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def scene_house(c, t):
    w, h = props.BOARD
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(skia.GradientShader.MakeLinear(points=[(0, 0), (0, 500)], colors=[sk.rgb(plate(0, 0.42)), sk.rgb(plate(0, 0.04))]))
    c.drawRect(skia.Rect.MakeWH(w, 500), sky)
    c.drawRect(skia.Rect.MakeLTRB(0, 498, w, 546), sk.fill(plate(0, 0.62)))
    c.drawRect(skia.Rect.MakeLTRB(0, 546, w, h), sk.fill(plate(0.26, 0.22)))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, w, 500))
    lay(c, props.house_at(t))
    c.restore()
    lay(c, props.flag(t))
    lay(c, props.tubs(t))
    k = S.pop(t, S.EV["baths"], 0.18, 2.8)
    if k > 0:
        x, y, rot = props.STAMP
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(k, k)
        c.drawPath(sk.rect(-178, -54, 178, 54), sk.fill(plate(1, 0)))
        sk.text(c, "5½ BATHS", 0, 28, sk.font("cond", 80), sk.fill(plate(0, 0)), "m")
        c.restore()


def scene_score(c, t):
    w, h = props.BOARD
    c.drawRect(skia.Rect.MakeWH(w, h), sk.fill(plate(0.14, 0)))
    c.drawRect(skia.Rect.MakeWH(w, 140), sk.fill(plate(0, 1)))
    sk.text(c, "BATHS THIS YEAR", 500, 108, sk.font("cond", 104), sk.fill(plate(0, 0)), "m")
    for key, name, ink in (("him", "HIM", (0, 1)), ("me", "ME", (1, 0))):
        x0, y0, x1, y1 = props.SCORE[key]
        c.drawPath(sk.rect(x0, y0 + 14, x1, y1), sk.fill(plate(0, 0)))
        c.drawPath(sk.rect(x0, y0 + 14, x1, y1), sk.stroke(plate(*ink), 12, join="miter"))
        sk.text(c, name, (x0 + x1) / 2, y0 + 104, sk.font("cond", 80), sk.fill(plate(*ink)), "m")
    x0, y0, x1, y1 = props.SCORE["him"]
    sk.text(c, "5½", (x0 + x1) / 2, y1 - 86, sk.font("black", 300), sk.fill(plate(0, 1)), "m")
    x0, y0, x1, y1 = props.SCORE["me"]
    me = props.me_score(t)
    cx, cy = (x0 + x1) / 2, y1 - 86
    if t >= S.EV["had"]:
        k = S.pop(t, S.EV["had"], 0.2, 3.2)
        c.save()
        c.translate(cx, cy)
        c.scale(k, k)
        sk.text(c, "0", 0, 0, sk.font("black", 320), sk.fill(plate(1, 0)), "m")
        c.restore()
    else:
        sk.text(c, me, cx, cy, sk.font("black", 300), sk.fill(plate(0.35, 0.35)), "m")


def caption(c, t):
    line, words = S.caption(t)
    if not line:
        return
    fnt = sk.font("cond", 66)
    gap = 20
    text = [w.upper() for w, _ in words]
    widths = [sk.text_width(w, fnt) for w in text]
    x = S.W / 2 - (sum(widths) + gap * (len(text) - 1)) / 2
    for w, (_, st), wd in zip(text, words, widths):
        if st == 1:                                       # the word being sung: a pink block knocked out of the blue
            c.drawPath(sk.rect(x - 10, 972, x + wd + 10, 1052), sk.fill(plate(1, 0)))
            sk.text(c, w, x, 1036, fnt, sk.fill(plate(0, 0)))
        else:
            sk.text(c, w, x, 1036, fnt, sk.fill(plate(0, 0) if st == 2 else plate(1, 1)))
        x += wd + gap


def marks(c):
    """What the printer leaves in the margin: register crosses and a strip of each ink."""
    for x, y in ((46, 46), (S.W - 46, 46)):
        for ink in ((1, 0), (0, 1)):
            pen = sk.stroke(plate(1, 1), 2.5)
            c.drawCircle(x, y, 13, pen)
            c.drawLine(x - 22, y, x + 22, y, pen)
            c.drawLine(x, y - 22, x, y + 22, pen)
    for k, ink in enumerate(((1, 0), (0.5, 0), (0, 1), (0, 0.5), (1, 1))):
        c.drawRect(skia.Rect.MakeXYWH(S.W - 310 + k * 40, 28, 36, 36), sk.fill(plate(*ink)))


def frame(t):
    th = S.hold(t, 2)
    s = sk.surface(S.W, S.H, (0, 0, 0))
    c = s.getCanvas()
    c.drawPath(sk.oval(ASMON_AT[0], 450, 345), sk.fill(plate(0.45, 0)))          # a disc of colour behind each man
    c.drawPath(sk.oval(HASAN_AT[0], 470, 350), sk.fill(plate(0, 0.36)))
    for k in range(9):                                                            # and stripes between them
        c.drawRect(skia.Rect.MakeXYWH(760 + k * 46, 640, 23, 300), sk.fill(plate(0, 0.36) if k % 2 else plate(0.45, 0)))
    x, y, k = BOARD
    w, h = props.BOARD[0] * k, props.BOARD[1] * k
    c.drawRect(skia.Rect.MakeLTRB(x - 16, y - 16, x + w + 16, y + h + 16), sk.fill(plate(1, 1)))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    c.translate(x, y)
    c.scale(k, k)
    if th < S.EV["line2"]:
        scene_house(c, th)
    else:
        scene_score(c, th)
    c.restore()
    for who, at in (("asmon", ASMON_AT), ("hasan", HASAN_AT)):
        lay(c, puppet.figure(who, acting.pose(who, th), at))
    c.drawRect(skia.Rect.MakeLTRB(0, DESK_Y, S.W, S.H), sk.fill(plate(0, 1)))
    ax, ay, sc = ASMON_AT
    for path, strength in props.stink(th):
        c.drawPath(sk.xf(path, ax, ay, sc), sk.stroke(plate(0.4, 0.9), 0.08 * sc))
    for fx, fy, wing, heading in props.flies(th):
        lay(c, props.fly(ax + fx * sc, ay + fy * sc, sc * 1.4, wing, heading))
    caption(c, th)
    marks(c)
    return press(sk.array(s), S.frame_no(S.hold(t, 4)) // 4)
