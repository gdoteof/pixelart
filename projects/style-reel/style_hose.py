"""A 1930s rubber-hose cartoon: ink and grey wash on cels, over a painted backdrop, shot on worn film.

Everything alive pumps on the beat, on twos: the two men (hose_cast.py), the house, the palms, the tubs
on their little legs. The words sit on a title strip and a ball bounces along them, word by word. The
film is black and white, so the red flag is a dark one with a star, and Hasan's fist goes up for it.
"""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFilter

import script as S
import sk
from hose_cast import INK, WHITE, asmon, g, hasan, ink, line, noodle, tube

NAME = "Rubber hose"
NOTES = "1930s cartoon: noodle limbs, pie eyes, white gloves; everything bounces on the beat, on twos; worn film."

GRAIN = 2.3                                 # the grain is the dear part of the file: at 7 it is 9 MB of the 720p clip
PAD = 14                                    # the picture is painted this far past the frame, for the gate weave
AX, HX, GROUND = 300, 1588, 846             # where the two men stand
HOUSE = (960, 696)
TUB_X = (584, 734, 884, 1034, 1184)
HALF_X = 1314
BOOK_I = "/usr/share/fonts/opentype/urw-base35/URWBookman-DemiItalic.otf"


# --- the painted backdrop -----------------------------------------------------------------------

def _soft(v, blur, a=1.0):
    p = sk.fill(g(v), a)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


@lru_cache(maxsize=1)
def backdrop():
    w, h = S.W + 2 * PAD, S.H + 2 * PAD
    surf = sk.surface(w, h)
    c = surf.getCanvas()
    c.translate(PAD, PAD)
    sky = skia.Paint(Shader=skia.GradientShader.MakeLinear(points=[(0, 0), (0, 800)], colors=[sk.rgb(g(182)), sk.rgb(g(238))]))
    c.drawRect(skia.Rect.MakeLTRB(-PAD, -PAD, S.W + PAD, S.H + PAD), sky)
    for cx, cy, s in ((230, 150, 1.0), (1650, 130, 1.15), (1330, 400, 0.55), (560, 420, 0.5)):
        puffs = [(-90, 14, 52), (-36, -20, 66), (34, -30, 74), (96, 6, 56), (10, 26, 70)]
        cloud = sk.union(*[sk.oval(cx + x * s, cy + y * s, r * s) for x, y, r in puffs])
        c.drawPath(sk.xf(cloud, 8, 14), _soft(168, 12, 0.7))
        c.drawPath(cloud, _soft(250, 2.5))
    far = sk.curve([(-60, 650), (180, 566), (430, 616), (700, 548), (980, 604), (1300, 536), (1610, 604), (1980, 556),
                    (1980, 1140), (-60, 1140)])
    c.drawPath(far, _soft(196, 2))
    for x, y, r in ((120, 590, 46), (205, 604, 34), (470, 596, 40), (1450, 566, 44), (1540, 586, 32), (1800, 576, 48)):
        c.drawLine(x, y + r * 0.6, x, y + r * 1.7, sk.stroke(g(120), 6))
        c.drawPath(sk.oval(x, y, r, r * 0.92), _soft(150, 1.5))
        c.drawPath(sk.oval(x - r * 0.25, y - r * 0.25, r * 0.5, r * 0.42), _soft(176, 5))
    hill = sk.curve([(300, 930), (560, 770), (820, 700), (1100, 700), (1360, 770), (1620, 930)])
    c.drawPath(hill, _soft(170, 2))
    drive = sk.curve([(944, 700), (962, 736), (916, 780), (860, 830), (1030, 830), (996, 780), (1014, 736), (978, 700)])
    c.drawPath(drive, _soft(212, 2))
    ground = sk.curve([(-60, 824), (500, 810), (960, 804), (1420, 810), (1980, 824), (1980, 1140), (-60, 1140)])
    c.drawPath(ground, _soft(140, 1.5))
    for k in range(46):
        x, y = S.rnd("tuft", k) * S.W, 818 + S.rnd("tufty", k) * 74
        for dx in (-7, 0, 7):
            c.drawLine(x, y, x + dx, y - 11, sk.stroke(g(86), 2.5))
    a = sk.array(surf)[..., 0].astype(np.float32)
    a = a * (0.90 + 0.2 * sk.cloud(w, h, seed=7, cell=180)) + 8 * (sk.cloud(w, h, seed=8, cell=5, octaves=2) - 0.5)
    grey = np.clip(a, 0, 255).astype(np.uint8)
    return sk.from_array(np.dstack([grey, grey, grey]))


# --- the house, its flag, the palms -------------------------------------------------------------

def _house(c):
    lw = 4

    def box(x0, y0, x1, y1, v):
        ink(c, sk.rect(x0, y0, x1, y1), g(v), lw)

    def window(x, y0, y1, w=26):
        ink(c, sk.rect(x - w / 2, y0, x + w / 2, y1), g(66), 3.5)
        c.drawLine(x, y0, x, y1, sk.stroke(g(226), 2.5))
        c.drawLine(x - w / 2, (y0 + y1) / 2, x + w / 2, (y0 + y1) / 2, sk.stroke(g(226), 2.5))

    for sx in (-1, 1):
        box(sx * 260, -150, sx * 140, 0, 224)
        ink(c, sk.poly([(sx * 272, -150), (sx * 128, -150), (sx * 150, -186), (sx * 250, -186)]), g(90), lw)
        window(sx * 200, -124, -86)
        window(sx * 200, -62, -22)
        for x in (sx * 246, sx * 206):
            ink(c, sk.oval(x, -14, 22, 18), g(104), 3.5)
    box(170, -238, 230, -186, 224)
    ink(c, sk.poly([(160, -238), (240, -238), (200, -290)]), g(90), lw)
    window(200, -228, -198, 20)
    box(-94, -266, -70, -224, 200)
    box(-140, -190, 140, 0, 238)
    ink(c, sk.poly([(-156, -190), (156, -190), (126, -238), (-126, -238)]), g(90), lw)
    ink(c, sk.poly([(-100, -190), (100, -190), (0, -266)]), g(244), lw)
    ink(c, sk.oval(0, -214, 14), g(66), 3.5)
    for x in (-112, -57, 57, 112):
        window(x, -168, -128)
    for x in (-112, 112):
        window(x, -98, -48)
    ink(c, sk.union(sk.rect(-22, -80, 22, -8), sk.oval(0, -80, 22)), g(62), lw)
    c.drawLine(0, -102, 0, -8, sk.stroke(g(200), 2.5))
    for x in (-82, -36, 36, 82):
        ink(c, sk.rect(x - 8, -184, x + 8, -10), WHITE, 3.5)
        ink(c, sk.rect(x - 12, -190, x + 12, -180), WHITE, 3)
        ink(c, sk.rect(x - 12, -16, x + 12, -8), WHITE, 3)
    ink(c, sk.rect(-106, -8, 106, 0), g(212), 3.5)


def _flag(c, t):
    c.drawLine(200, -290, 200, -408, sk.stroke(INK, 5))
    ink(c, sk.oval(200, -412, 6), WHITE, 3)
    if t < S.EV["austere"] - 0.04:
        return
    up = S.back((t - S.EV["austere"] + 0.04) / 0.3, 1.5)
    top = -302 + (-402 + 302) * up

    def wave(x):
        return 7 * (x / 104) * math.sin(x / 17 - t * 11)

    xs = [k * 13 for k in range(9)]
    cloth = sk.curve([(200 + x, top + wave(x), "c") if x in (0, 104) else (200 + x, top + wave(x)) for x in xs]
                     + [(200 + x, top + 66 + wave(x), "c") if x in (0, 104) else (200 + x, top + 66 + wave(x))
                        for x in reversed(xs)])
    ink(c, cloth, g(70), 4)
    star = [(252 + r * math.cos(math.radians(-90 + 36 * k)), top + 33 + wave(52) + r * math.sin(math.radians(-90 + 36 * k)))
            for k, r in zip(range(10), [21, 8.8] * 5)]
    c.drawPath(sk.poly(star), sk.fill(WHITE))


def mansion(c, t):
    """Up out of the hill on "mansion's", too tall, and back; then it pumps with everything else."""
    t0 = S.EV["mansion"] - 0.04
    if t < t0:
        return
    grow = S.back((t - t0) / 0.36, 2.4)
    i, p = S.beat(t)
    bob = 0.022 * math.cos(2 * math.pi * p)
    c.save()
    c.translate(*HOUSE)
    c.rotate(1.1 * math.cos(math.pi * (i + p)))
    c.scale((1 + 0.4 * (1 - grow)) * (1 + bob), grow * (1 - bob))
    _house(c)
    _flag(c, t)
    c.restore()


def palm(c, t, x, base, height, phase):
    i, p = S.beat(t)
    sw = math.cos(math.pi * (i + p) + phase)
    top = (x + 16 + 22 * sw, base - height)
    trunk = skia.Path()
    trunk.moveTo(x, base)
    trunk.quadTo(x + 26, base - height * 0.5, *top)
    tube(c, trunk, 20, g(150), 4)
    for k in range(1, 9):
        (rx, ry), ra = sk.along(trunk, k / 9)
        c.save()
        c.translate(rx, ry)
        c.rotate(ra + 90)
        c.drawLine(-9, 0, 9, 0, sk.stroke(INK, 2.5))
        c.restore()
    leaf = sk.curve([(0, -6, "c"), (46, -24), (96, -12), (132, 24, "c"), (94, 10), (46, 5), (0, 6, "c")])
    for flip in (-1, 1):
        for a in (-64, -30, 6, 40):
            m = sk.matrix(top[0], top[1], rot=flip * (a + 5 * sw * flip), sx=flip, sy=1)
            ink(c, sk.xf(leaf, m=m), g(82), 4)
    for dx in (-9, 8):
        ink(c, sk.oval(top[0] + dx, top[1] + 12, 9), g(54), 3)


# --- the sign that becomes the scoreboard -------------------------------------------------------

def _shadowed(c, s, x, y, fnt, v=20):
    sk.text(c, s, x + 4, y + 4, fnt, sk.fill(g(168)), "m")
    sk.text(c, s, x, y, fnt, sk.fill(g(v)), "m")


def board(c, t):
    """It drops in on its ropes for "baths", turns over for the second line, and takes the nought on "had"."""
    t0 = S.EV["baths"] - 0.23
    if t < t0:
        return
    drop = S.bounce((t - t0) / 0.5)
    had = t - S.EV["had"]
    swing = 1.5 * math.sin(2 * math.pi * (t - t0) / (2 * S.BEAT))
    if had > 0:
        swing += 4.5 * math.exp(-3.2 * had) * math.sin(2 * math.pi * 1.5 * had)
    flip = S.ramp(t, S.EV["line2"] - 0.07, 0.3)
    c.save()
    c.translate(960, -80)
    c.rotate(swing)
    c.translate(0, 234 - (1 - drop) * 340)
    for sx in (-1, 1):
        c.drawLine(sx * 236, -112, sx * 236, -600, sk.stroke(INK, 5))
        c.drawLine(sx * 236, -112, sx * 236, -600, sk.stroke(g(170), 1.5))
    c.scale(max(0.03, abs(math.cos(math.pi * flip))), 1)
    ink(c, sk.rect(-300, -118, 300, 118, 12), g(240), 7)
    for y in (-78, -30, 26, 72):
        line(c, [(-282, y), (-90, y + 4), (120, y - 3), (282, y + 2)], 2, g(214))
    c.drawPath(sk.rect(-286, -104, 286, 104, 7), sk.stroke(g(120), 3))
    for sx in (-1, 1):
        for sy in (-1, 1):
            c.drawCircle(sx * 272, sy * 90, 4.5, sk.fill(INK))
    if flip < 0.5:
        _shadowed(c, "5½ BATHS", 0, 38, sk.font("book", 106))
    else:
        _shadowed(c, "BATHS THIS YEAR", 0, -56, sk.font("book", 40))
        c.drawLine(-270, -40, 270, -40, sk.stroke(INK, 4))
        c.drawLine(0, -40, 0, 100, sk.stroke(INK, 4))
        small, big = sk.font(BOOK_I, 30), sk.font("book", 98)
        sk.text(c, "HIM", -140, -6, small, sk.fill(g(70)), "m")
        _shadowed(c, "5½", -140, 88, big)
        if had < 0:
            sk.text(c, "ME", 140, -6, small, sk.fill(g(70)), "m")
            rolling = t >= S.EV["ive"]
            mark = "8531"[min(3, int((t - S.EV["ive"]) * 12))] if rolling else "?"
            c.save()
            c.translate(140, 54)
            c.rotate(0 if rolling else 9 * math.sin(2 * math.pi * S.beat(t)[1]))
            _shadowed(c, mark, 0, 34, big, 20 if not rolling else 110)
            c.restore()
        else:
            c.drawPath(sk.rect(12, -34, 280, 98, 6), sk.fill(INK))
            sk.text(c, "ME", 140, -6, small, sk.fill(g(200)), "m")
            slam = 1 + 1.5 * (1 - S.ease_out(had / 0.2))
            c.save()
            c.translate(140, 54)
            c.scale(slam * (1 + 0.25 * math.exp(-9 * had)), slam * (1 - 0.2 * math.exp(-9 * had)))
            sk.text(c, "0", 0, 34, big, sk.fill(WHITE), "m")
            c.restore()
            if 0.06 < had < 0.3:
                for k in range(10):
                    a = math.radians(36 * k + 12)
                    r0, r1 = 150 + 180 * had, 176 + 230 * had
                    c.drawLine(140 + r0 * math.cos(a), 30 + 0.62 * r0 * math.sin(a), 140 + r1 * math.cos(a),
                               30 + 0.62 * r1 * math.sin(a), sk.stroke(INK, 5))
    c.restore()


# --- the tubs -----------------------------------------------------------------------------------

BOWL = [(-60, -62, "c"), (-55, -32), (-40, -15), (40, -15), (55, -32), (60, -62, "c")]
CUT = [(0, -80), (9, -64), (-5, -50), (9, -36), (-5, -22), (4, -10)]


def tub(c, t, k):
    """Tub k of five (k = 5 is the half): it pops up on its count and then dances on its little legs."""
    half = k == 5
    t0 = (S.EV["half"] if half else S.EV["tubs"][k]) - 0.02
    if t < t0:
        return
    grow = S.back((t - t0) / 0.3, 2.6)
    _, p = S.beat(t)
    live = S.ramp(t, t0 + 0.3, 0.2)
    beat = math.sin(2 * math.pi * p + math.pi * k)
    hop = 10 * live * max(0.0, beat)
    lean = 5 * live * beat + 8 * S.ease_out((t - 73.05) / 0.2)       # they lean away from him too
    c.save()
    c.translate(HALF_X if half else TUB_X[k], 838)
    c.scale(1.12, 1.12)
    c.drawPath(sk.oval(-16 if half else 0, 3, 34 if half else 58, 8), sk.fill(g(84), 0.5))
    for fx in ((-34,) if half else (-34, 34)):
        tube(c, noodle((fx * 0.8, -18 * grow - hop), (fx, -5), 26, (0, -300)), 7)
        c.drawPath(sk.oval(fx + math.copysign(7, fx), -4, 14, 6.5), sk.fill(INK))
    if t - t0 < 0.19:                                           # pop
        for a in (-150, -118, -62, -30):
            r0, r1 = 92 + 120 * (t - t0), 112 + 170 * (t - t0)
            c.drawLine(r0 * math.cos(math.radians(a)), -40 + r0 * math.sin(math.radians(a)),
                       r1 * math.cos(math.radians(a)), -40 + r1 * math.sin(math.radians(a)), sk.stroke(INK, 4))
    c.translate(0, -hop)
    c.rotate(lean)
    c.scale(1 + 0.45 * (1 - grow), grow)
    tube(c, sk.curve([(-50, -60), (-57, -96), (-36, -106), (-24, -88)], closed=False), 8, g(150), 4)
    c.save()
    if half:
        c.clipPath(sk.poly([(-130, -170), (0, -170)] + CUT + [(4, 30), (-130, 30)]), doAntiAlias=True)
    ink(c, sk.curve(BOWL), WHITE, 5)
    ink(c, sk.rect(-67, -73, 67, -58, 7), WHITE, 4.5)
    c.restore()
    if half:
        line(c, CUT, 4.5, sharp=True)
    sk.text(c, "½" if half else "12345"[k], -30 if half else 0, -25, sk.font("book", 36), sk.fill(INK), "m")
    for j, (bx, by, br) in enumerate(((-27, -88, 11), (2, -100, 14), (28, -86, 10))):
        if not (half and bx > -10):
            wob = 3 * math.sin(t * 6 + j * 2 + k)
            ink(c, sk.oval(bx, by + wob, br), WHITE, 3)
            c.drawCircle(bx - br * 0.3, by + wob - br * 0.3, br * 0.22, sk.fill(g(170)))
    c.restore()


# --- the title strip and its bouncing ball ------------------------------------------------------

BASE, TOP = 1006, 958                        # the words' baseline, and where the ball rests on them


@lru_cache(maxsize=None)
def layout(which):
    """(font size, [(word, left edge, width)]) for a lyric line, centred, both lines at one size."""
    size = min(54.0, 54.0 * 1640 / max(sk.text_width(line_["text"], sk.font("book", 54)) for line_ in S.LINES))
    fnt = sk.font("book", size)
    words = [w for w, _, _ in S.LINES[which]["words"]]
    space = sk.text_width(" ", fnt)
    widths = [sk.text_width(w, fnt) for w in words]
    x = S.W / 2 - (sum(widths) + space * (len(words) - 1)) / 2
    out = []
    for w, wd in zip(words, widths):
        out.append((w, x, wd))
        x += wd + space
    return size, out


def ball(t, which):
    """Where the ball is over a line: (x, y, squash). It lands on each word as the word starts."""
    words = S.LINES[which]["words"]
    cx = [x + w / 2 for _, x, w in layout(which)[1]]
    a = [w[1] for w in words]
    if t < a[0]:
        u = S.clamp((t - a[0] + 0.34) / 0.34)
        return cx[0] - 80 * (1 - u), TOP - 76 * (1 - u * u), 0.0
    for i in range(len(a) - 1):
        if t < a[i + 1]:
            u = (t - a[i]) / (a[i + 1] - a[i])
            hop = min(46.0, 14 + 80 * (a[i + 1] - a[i]))
            return cx[i] + (cx[i + 1] - cx[i]) * u, TOP - hop * 4 * u * (1 - u), max(0.0, 1 - (t - a[i]) / 0.07)
    tau = t - a[-1]
    if which == 0:                                              # off the end of the line, to come down on the next
        u = S.clamp(tau / (words[-1][2] - a[-1]))
        return cx[-1] + 100 * u, TOP - 70 * 4 * u * (1 - u) - 30 * u, max(0.0, 1 - tau / 0.07)
    return cx[-1], TOP - 34 * math.exp(-1.7 * tau) * abs(math.sin(math.pi * tau / 0.34)), max(0.0, 1 - tau / 0.07)


def strip(c, t):
    ink(c, sk.rect(64, 894, S.W - 64, 1064, 26), g(12), 5)
    c.drawPath(sk.rect(78, 906, S.W - 78, 1052, 16), sk.stroke(g(196), 2.5))
    for sx in (-1, 1):
        c.drawPath(sk.poly([(S.W / 2 + sx * 862, 979), (S.W / 2 + sx * 846, 963), (S.W / 2 + sx * 830, 979),
                            (S.W / 2 + sx * 846, 995)]), sk.fill(g(196)))
    line_, words = S.caption(t)
    if line_ is None:
        sk.text(c, "follow the bouncing ball", S.W / 2, BASE - 4, sk.font(BOOK_I, 44), sk.fill(g(176)), "m")
        _, p = S.beat(t)
        c.drawCircle(S.W / 2 - 330, TOP + 14 - 40 * 4 * p * (1 - p), 12, sk.fill(WHITE))
        return
    which = S.LINES.index(line_)
    size, lay = layout(which)
    fnt = sk.font("book", size)
    for (w, x, _), (_, state), (_, a, _) in zip(lay, words, line_["words"]):
        dent = 5 * math.exp(-(t - a) / 0.07) if state == 1 else 0.0          # the word gives under the ball
        sk.text(c, w, x, BASE + dent, fnt, sk.fill(g(132) if state == 0 else WHITE))
    x, y, squash = ball(t, which)
    c.drawPath(sk.oval(x, y - 14 + 3.5 * squash, 14 * (1 + 0.3 * squash), 14 * (1 - 0.25 * squash)), sk.fill(WHITE))


# --- the film -----------------------------------------------------------------------------------

def iris(c, t):
    """The picture opens out of a circle on Asmongold and closes back onto him."""
    wide = 1500.0
    if t < S.T0 + 0.5:
        r = 175 + (wide - 175) * S.ease_in(S.ramp(t, S.T0 + 0.06, 0.42), 2)
    elif t > S.T1 - 0.5:
        r = wide + (185 - wide) * S.ease_out(S.ramp(t, S.T1 - 0.48, 0.34), 2)
    else:
        return
    hole = skia.Path()
    hole.addRect(skia.Rect.MakeLTRB(-60, -60, S.W + 60, S.H + 60))
    hole.addCircle(AX, 336, r)
    hole.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(hole, _soft(0, 5))


def gate(c):
    edge = skia.Path()
    edge.addRect(skia.Rect.MakeLTRB(-60, -60, S.W + 60, S.H + 60))
    edge.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(7, 7, S.W - 7, S.H - 7), 44, 44))
    edge.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(edge, _soft(0, 4))


@lru_cache(maxsize=1)
def vignette():
    y, x = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
    r = np.hypot((x - S.W / 2) / (S.W / 2), (y - S.H / 2) / (S.H / 2)) / math.sqrt(2)
    return (1 - 0.5 * np.clip(r, 0, 1) ** 2.4).astype(np.float32)


def film(grey, f):
    """Grey cels to a worn print: soft, haloed, vignetted, flickering, grainy, scratched, a little warm."""
    def r(*key):
        return S.rnd("film", f, *key)

    img = Image.fromarray(grey)
    soft = np.asarray(img.filter(ImageFilter.GaussianBlur(1.0)), np.float32)
    glow = np.asarray(img.filter(ImageFilter.GaussianBlur(18)), np.float32)
    a = soft + 0.16 * glow * (1 - soft / 255)
    a = (22 + a * (232 - 22) / 255) * vignette() * (1 + 0.03 * (2 * r("flicker") - 1))
    rng = np.random.default_rng(4000 + f // 2)                  # the grain is on twos as well: it halves the file
    coarse = Image.fromarray(rng.standard_normal((S.H // 3, S.W // 3), np.float32) * GRAIN, "F")
    a += np.asarray(coarse.resize((S.W, S.H), Image.BICUBIC))
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    if 26 <= f <= 86:                                           # one scratch stays a while, wandering
        x = 1396 + 4 * math.sin(f * 0.7)
        for y0 in range(0, S.H, 90):
            if S.rnd("tram", f, y0) < 0.7:
                d.line([(x + 2 * r("a", y0), y0), (x + 2 * r("b", y0), y0 + 90)], fill=208, width=1)
    for k in range(2):
        if r("s", k) < 0.2:
            x, y0 = r("sx", k) * S.W, r("sy", k) * S.H * 0.6
            d.line([(x, y0), (x + 8 * (r("sw", k) - 0.5), y0 + 200 + 800 * r("sl", k))],
                   fill=222 if r("sc", k) < 0.75 else 44, width=1)
    for k in range(2 + int(6 * r("n"))):
        x, y, rad = r("dx", k) * S.W, r("dy", k) * S.H, 0.8 + 3.2 * r("dr", k) ** 2
        tall = rad * (0.6 + r("de", k))
        d.ellipse((x - rad, y - tall, x + rad, y + tall), fill=30 if r("dc", k) < 0.8 else 226)
    if r("hair") < 0.07:
        x, y, bend = r("hx") * S.W, r("hy") * S.H, 30 * (r("hb") - 0.5)
        d.line([(x + bend * math.sin(j / 3), y + 9 * j) for j in range(9)], fill=34, width=1)
    a = np.asarray(out, np.float32)
    return Image.fromarray(np.clip(np.stack([a, a * 0.968, a * 0.915], -1), 0, 255).astype(np.uint8))


def frame(t):
    f = S.frame_no(t)
    th = S.hold(t, 2)                                           # the cels are shot on twos; the ball and the film on ones
    surf = sk.surface(S.W, S.H, g(0))
    c = surf.getCanvas()
    c.save()
    w = f // 2                                                  # the gate weave, a pixel or so, on twos too
    c.translate(1.0 * math.sin(w * 0.54 + 1) + 0.6 * (S.rnd("wx", w) - 0.5),
                1.3 * math.sin(w * 0.74) + 0.8 * (S.rnd("wy", w) - 0.5))
    c.drawImage(backdrop(), -PAD, -PAD)
    palm(c, th, 640, 716, 300, 0.0)
    palm(c, th, 1290, 716, 280, 1.4)
    mansion(c, th)
    board(c, th)
    for k in range(6):
        tub(c, th, k)
    hasan(c, th, HX, GROUND)
    asmon(c, th, AX, GROUND)
    strip(c, t)
    iris(c, t)
    c.restore()
    gate(c)
    return film(sk.array(surf)[..., 0].copy(), f)
