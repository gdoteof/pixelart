"""The cast of the rubber-hose cartoon: Asmongold and Hasan as period caricatures, and how a cel is inked.

Each man is drawn front on, from the feet up, in his own pixels (about 680 tall). The torso pumps on
every beat and squashes at the bottom of it; arms and legs are noodles that bow by as much as they are too
long for the gap, which is all the elbow or knee a rubber hose has; hands are white gloves, eyes are pie-cut.
The acting is pose to pose: a list of (time, value) keys per hand, each snapped to on its word.
"""
import math
from functools import lru_cache

import skia

import script as S
import sk

INK = (20, 18, 18)
WHITE = (250, 250, 250)
LW = 6.0


def g(v):
    return (v, v, v)


SKIN_A, SKIN_H = g(244), g(204)


# --- ink ----------------------------------------------------------------------------------------

def ink(c, path, col, lw=LW):
    """A cel shape: flat grey inside a black line."""
    if col is not None:
        c.drawPath(path, sk.fill(col))
    c.drawPath(path, sk.stroke(INK, lw))


def line(c, pts, w=LW, col=INK, sharp=False):
    path = sk.poly(pts, closed=False) if sharp else sk.curve(pts, closed=False)
    c.drawPath(path, sk.stroke(col, w))


def tube(c, path, w, col=None, lw=LW):
    """A hose: a black one, or a grey one inside a black line."""
    if col is None:
        c.drawPath(path, sk.stroke(INK, w))
    else:
        c.drawPath(path, sk.stroke(INK, w + 2 * lw))
        c.drawPath(path, sk.stroke(col, w))


def noodle(p0, p1, length, away):
    """A limb from p0 to p1. Shorter than `length`, the gap makes it bow, to the side away from a point."""
    (x0, y0), (x1, y1) = p0, p1
    d = math.hypot(x1 - x0, y1 - y0) or 1e-6
    bow = max(2 * math.sqrt(3 * d * max(0.0, length - d) / 8), 0.07 * d)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0) / d, (x1 - x0) / d
    if (mx + nx - away[0]) ** 2 + (my + ny - away[1]) ** 2 < (mx - nx - away[0]) ** 2 + (my - ny - away[1]) ** 2:
        nx, ny = -nx, -ny
    path = skia.Path()
    path.moveTo(x0, y0)
    path.quadTo(mx + nx * bow, my + ny * bow, x1, y1)
    return path


# --- time ---------------------------------------------------------------------------------------

def lerp(a, b, k):
    if isinstance(a, (int, float)):
        return a + (b - a) * k
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def pose(t, keys, dur=0.2, s=1.7):
    """Pose to pose: at each key's time the value goes to it, a little past it and back, and then holds."""
    i = max([k for k, (tk, _) in enumerate(keys) if tk <= t], default=0)
    if i == 0:
        return keys[0][1]
    return lerp(keys[i - 1][1], keys[i][1], S.back((t - keys[i][0]) / dur, s))


def step(t, keys):
    """The value of the last key at or before t."""
    out = keys[0][1]
    for tk, v in keys:
        if tk <= t:
            out = v
    return out


def pump(t, phase=0.0):
    """(how far the knees are bent, 0..1: all the way on the beat; the sway, -1..1: one way a beat)."""
    i, p = S.beat(t)
    return 0.5 + 0.5 * math.cos(2 * math.pi * p), math.cos(math.pi * (i + p) + phase)


class Body:
    """Body space: the waist at the origin, leaning and squashed, in a figure whose feet are at (0, 0)."""

    def __init__(self, x, y, rot, sx, sy):
        self.x, self.y, self.rot, self.sx, self.sy = x, y, rot, sx, sy
        self.ca, self.sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def out(self, p):
        px, py = p[0] * self.sx, p[1] * self.sy
        return self.x + px * self.ca - py * self.sa, self.y + px * self.sa + py * self.ca

    def enter(self, c):
        c.save()
        c.translate(self.x, self.y)
        c.rotate(self.rot)
        c.scale(self.sx, self.sy)


# --- gloves, eyes -------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _glove(kind):
    parts = [sk.oval(30, 0, 24)]
    if kind == "open":
        parts += [sk.capsule((40, -15), (72, -31), 10, 9), sk.capsule((46, 0), (84, 0), 10, 9),
                  sk.capsule((40, 15), (72, 31), 10, 9), sk.capsule((22, -16), (30, -48), 10, 9)]
    elif kind == "point":
        parts += [sk.capsule((44, -8), (96, -10), 10, 9), sk.oval(50, 10, 12), sk.oval(40, 20, 11),
                  sk.capsule((24, -16), (44, -34), 10, 9)]
    elif kind == "thumb":
        parts += [sk.oval(50, -10, 11), sk.oval(54, 4, 11), sk.oval(48, 17, 11), sk.capsule((22, -16), (16, -56), 10, 9.5)]
    else:                                                       # a fist
        parts += [sk.oval(50, -10, 11), sk.oval(54, 4, 11), sk.oval(48, 17, 11), sk.capsule((24, -18), (44, -22), 9, 9)]
    return sk.union(*parts), sk.oval(2, 0, 10, 21)


def glove(c, kind, at, angle, scale=1.0, flip=None):
    """A white glove with its wrist at `at`, the fingers along `angle`. The thumb stays on the upper side."""
    hand, cuff = _glove(kind)
    flip = math.cos(math.radians(angle)) < 0 if flip is None else flip
    c.save()
    c.translate(*at)
    c.rotate(angle)
    c.scale(scale, -scale if flip else scale)
    ink(c, hand, WHITE)
    for y in (-8, 0, 8):
        c.drawLine(17, y, 33, y, sk.stroke(INK, 3.5))
    ink(c, cuff, WHITE)
    c.restore()


def pie_eye(c, cx, cy, rx, ry, look, shut, skin, lid=0.0, wide=0.0, side=1):
    """A black oval with a slice of pie cut out of it; "happy" and "tight" are the two ways it shuts."""
    if shut == "happy":
        return line(c, [(cx - rx - 3, cy + 4), (cx, cy - 7), (cx + rx + 3, cy + 4)], 4.5)
    if shut == "tight":
        far, near = cx + side * rx * 1.3, cx - side * rx * 0.9
        return line(c, [(far, cy - 10), (near, cy), (far, cy + 10)], 4.5, sharp=True)
    cx, cy = cx + look[0] * 3.5, cy + look[1] * 3.5
    if wide:
        ink(c, sk.oval(cx, cy, rx + 9 * wide, ry + 10 * wide), WHITE, 4)
    eye = sk.oval(cx, cy, rx * (1 + 0.15 * wide), ry * (1 + 0.15 * wide))
    c.drawPath(eye, sk.fill(INK))
    a = math.radians(-58 if look[0] >= 0 else -122)
    wedge = sk.poly([(cx + 0.1 * rx * math.cos(a), cy + 0.1 * ry * math.sin(a)),
                     (cx + 3 * ry * math.cos(a - 0.42), cy + 3 * ry * math.sin(a - 0.42)),
                     (cx + 3 * ry * math.cos(a + 0.42), cy + 3 * ry * math.sin(a + 0.42))])
    c.drawPath(sk.intersect(wedge, eye), sk.fill(WHITE if wide else skin))
    if lid > 0:
        y = cy - ry + 2 * ry * lid
        c.drawRect(skia.Rect.MakeLTRB(cx - rx - 2, cy - ry - 3, cx + rx + 2, y), sk.fill(skin))
        c.drawLine(cx - rx - 3, y, cx + rx + 3, y, sk.stroke(INK, 4))


# --- Asmongold ----------------------------------------------------------------------------------

AS = 0.9
# The hand on the house's side, then the other: (x, y) in body space, and the glove with the way it points
# (None: the way the arm does).
A_RH = [(0.0, (66, 6)), (67.63, (196, -150)), (68.03, (190, -262)), (68.65, (160, -46)), (68.87, (222, -52)),
        (69.29, (190, -134)), (69.41, (190, -66)), (69.59, (124, -368)), (70.02, (136, -170)), (70.67, (124, -368)),
        (72.31, (30, -128)), (72.61, (180, -236)), (73.01, (60, -10))]
A_RG = [(0.0, ("open", None)), (67.63, ("point", -6)), (68.03, ("point", -16)), (68.65, ("point", 24)),
        (69.29, ("open", None)), (69.59, ("point", -54)), (70.02, ("open", -24)), (70.67, ("point", -54)),
        (72.31, ("thumb", None)), (72.61, ("open", -52)), (73.01, ("fist", None))]
A_LH = [(0.0, (-66, 6)), (67.63, (-60, -10)), (70.02, (-136, -170)), (70.67, (-60, -10)), (72.61, (-180, -236)),
        (73.01, (-60, -10))]
A_LG = [(0.0, ("open", None)), (67.63, ("fist", None)), (70.02, ("open", -156)), (70.67, ("fist", None)),
        (72.61, ("open", -128)), (73.01, ("fist", None))]
A_LEAN = [(0.0, 0.0), (67.63, 4.0), (70.02, -3.0), (70.67, 3.0), (72.31, 0.0), (72.61, -4.0), (73.01, -5.0)]
A_TILT = [(0.0, 0.0), (67.63, 4.0), (69.59, -4.0), (70.02, -9.0), (70.67, -3.0), (72.31, 5.0), (72.61, -6.0), (73.01, -8.0)]
A_LOOK = [(0.0, (0.6, 0.0)), (67.63, (1.0, 0.0)), (68.03, (1.0, -0.6)), (68.65, (1.0, 0.9)), (69.59, (0.7, -1.0)),
          (70.02, (0.0, 0.0)), (70.67, (0.7, -1.0)), (72.31, (0.0, 0.0))]
A_BROW = [(0.0, 0.0), (70.02, 1.0), (70.67, 0.0), (72.61, 1.0)]


def gap_mouth(c, cx, cy, m, grin=False):
    """Asmongold's mouth, in the beard: S.mouth()'s shape, or the proud grin, with not all of the teeth."""
    lip = g(214)
    if grin:
        shape = sk.curve([(cx - 33, cy - 8, "c"), (cx, cy + 1), (cx + 33, cy - 8, "c"), (cx + 22, cy + 15), (cx, cy + 21),
                          (cx - 22, cy + 15)])
        c.drawPath(shape, sk.fill(g(238)))
        c.save()
        c.clipPath(shape, doAntiAlias=True)
        for x0, x1 in ((-19, -9), (6, 13)):
            c.drawRect(skia.Rect.MakeLTRB(cx + x0, cy - 12, cx + x1, cy + 24), sk.fill(g(14)))
        for x in (-26, -3, 0, 19, 26):
            c.drawLine(cx + x, cy - 12, cx + x, cy + 24, sk.stroke(INK, 2))
        c.restore()
        return c.drawPath(shape, sk.stroke(lip, 4))
    w, h = 27 * m["w"], 30 * m["h"]
    if h < 3.5:
        return line(c, [(cx - w, cy - 2), (cx, cy + 3), (cx + w, cy - 2)], 4.5, lip)
    shape = sk.curve([(cx - w, cy - h * 0.2), (cx, cy - h * 0.42), (cx + w, cy - h * 0.2), (cx + w * 0.72, cy + h * 0.58),
                      (cx, cy + h), (cx - w * 0.72, cy + h * 0.58)])
    c.drawPath(shape, sk.fill(g(12)))
    c.save()
    c.clipPath(shape, doAntiAlias=True)
    if m["tongue"] > 0.15:
        c.drawPath(sk.oval(cx, cy + h, w * 0.55, h * 0.5), sk.fill(g(150)))
    if m["teeth"] > 0.15:
        bottom = cy - h * 0.42 + 4 + (8 + 7 * m["f"]) * m["teeth"]
        c.drawRect(skia.Rect.MakeLTRB(cx - w, cy - h, cx + w, bottom), sk.fill(g(238)))
        for x0, x1 in ((-15, -7), (5, 11)):
            c.drawRect(skia.Rect.MakeLTRB(cx + x0, cy - h, cx + x1, bottom + 1), sk.fill(g(12)))
    c.restore()
    c.drawPath(shape, sk.stroke(lip, 4))


def asmon_head(c, look, shut, brow, mouth, grin, lag):
    lx, ly = lag                                       # how far the loose ends trail behind the head
    face = sk.curve(sk.mirror([(0, -96), (36, -90), (57, -58), (61, -4), (55, 46), (37, 84), (0, 98)]))
    ink(c, face, SKIN_A)
    line(c, [(-17, -75), (0, -78), (17, -75)], 2.5, g(165))
    beard = sk.curve([(-60, 0, "c"), (-55, 52), (-41, 102), (-27 + lx * 0.5, 136 + ly, "c"), (-15 + lx * 0.7, 119 + ly, "c"),
                      (lx, 154 + ly, "c"), (15 + lx * 0.7, 119 + ly, "c"), (27 + lx * 0.5, 136 + ly, "c"), (41, 102), (55, 52),
                      (60, 0, "c"), (45, 30), (30, 41), (14, 27), (0, 35), (-14, 27), (-30, 41), (-45, 30)])
    ink(c, beard, g(62), 5)
    for x0 in (-34, -12, 12, 34):
        line(c, [(x0, 86), (x0 * 0.8 + lx * 0.4, 112 + ly * 0.6)], 2.5, g(112))
    gap_mouth(c, 0, 66, mouth, grin)
    nx = 5 * look[0]
    nose = sk.curve([(nx - 6, -30), (nx - 10, 14), (nx, 27), (nx + 10, 14), (nx + 6, -30)], closed=False)
    c.drawPath(nose, sk.fill(SKIN_A))
    c.drawPath(nose, sk.stroke(INK, 4))
    for sx in (-1, 1):
        ex, ey = sx * 21 + nx * 0.5, -38
        pie_eye(c, ex, ey, 8.5, 14, look, shut, SKIN_A, lid=0.36, side=sx)
        line(c, [(ex - 9, ey + 19), (ex, ey + 22), (ex + 9, ey + 19)], 2.5, g(140))
        by = -63 - 9 * brow
        line(c, [(sx * 9 + nx * 0.5, by - 5), (sx * 22 + nx * 0.5, by - 3), (sx * 34 + nx * 0.5, by + 5)], 4)
    for sx in (-1, 1):                                 # the hair: a centre parting, a long way back, and down past the shoulders
        curtain = sk.curve([(0, -104, "c"), (sx * 30, -108), (sx * 58, -86), (sx * 71, -30), (sx * 77, 60),
                            (sx * 84 + lx, 150 + ly * 0.7), (sx * 93 + lx, 198 + ly, "c"), (sx * 76 + lx, 172 + ly, "c"),
                            (sx * 67 + lx, 206 + ly, "c"), (sx * 54 + lx, 178 + ly, "c"), (sx * 43 + lx, 198 + ly, "c"),
                            (sx * 41 + lx * 0.5, 120), (sx * 45, 40), (sx * 47, -30), (sx * 41, -66), (sx * 23, -92),
                            (0, -85, "c")])
        ink(c, curtain, g(40), 5)
        line(c, [(sx * 20, -98), (sx * 52, -60), (sx * 62, 40), (sx * 66 + lx, 150 + ly * 0.7)], 3, g(128))
        line(c, [(sx * 34, -82), (sx * 55, 30), (sx * 56 + lx, 140 + ly * 0.7)], 2.5, g(96))
    c.drawLine(0, -104, 0, -87, sk.stroke(g(205), 3))
    line(c, [(-76, -6), (-66, -78), (0, -119), (66, -78), (76, -6)], 14)                       # the headphones
    line(c, [(-58, -82), (0, -113), (42, -99)], 3, g(150))
    for sx in (-1, 1):
        ink(c, sk.oval(sx * 78, 2, 19, 32), g(98), 5)
        c.drawPath(sk.oval(sx * 80, 2, 9, 19), sk.fill(g(40)))


def flies(c, t, cx, cy):
    """The flies that find him: the first on "I've", the rest for "year", each trailing its dots."""
    for k in range(6):
        t0 = S.EV["ive"] + 0.04 if k == 0 else S.EV["year"] - 0.06 + 0.09 * (k - 1)
        if t < t0:
            continue

        def at(tt, k=k, t0=t0):
            # In from up on the left, on a spiral, then round and round his head: never across his face.
            a = math.radians(196 + 13 * k) + (1 if k % 2 else -1) * 2 * math.pi * (0.7 + 0.3 * S.rnd("fa", k)) * (tt - t0)
            r = 130 + 36 * S.rnd("fx", k) + 13 * math.sin(2 * math.pi * 1.7 * tt + k)
            r += 620 * (1 - S.ease_out((tt - t0) / 0.5))
            return cx + r * math.cos(a), cy - 10 + r * math.sin(a)

        for j in range(1, 7):
            if t - 0.035 * j >= t0:
                c.drawCircle(*at(t - 0.035 * j), 3.6 - 0.4 * j, sk.fill(INK, 0.8))
        x, y = at(t)
        flap = 1 if S.frame_no(t) // 2 % 2 else -1
        for sx in (-1, 1):
            ink(c, sk.oval(x + sx * 9, y - 10 - flap, 11, 6.5, rot=sx * (28 + 14 * flap)), WHITE, 2.5)
        c.drawPath(sk.oval(x, y, 11, 8), sk.fill(INK))


def stink(c, t, cx, top):
    """The smell, in wavy lines, rising off him from "had"."""
    for k, dx in enumerate((-132, -92, 96, 136)):
        grow = S.ease_out((t - S.EV["had"] - 0.08 - 0.09 * k) / 0.5)
        if grow <= 0:
            continue
        ph = t * 7 + k * 1.9
        wave = sk.curve([(cx + dx + 12 * math.sin(ph + j * 1.3), top + 70 - j * 30) for j in range(7)], closed=False)
        c.drawPath(sk.part(wave, 0, grow), sk.stroke(g(48), 5.5))


def asmon(c, t, x, ground):
    dip, sway = pump(t)
    late = pump(t - 0.09)
    sq = 0.05 * (2 * dip - 1)
    body = Body(6 * sway, -272 + 20 * dip, 2.0 * sway + pose(t, A_LEAN), 1 + 0.6 * sq, 1 - sq)
    proud = t >= 73.01
    c.save()
    c.translate(x, ground)
    c.scale(AS, AS)
    c.drawPath(sk.oval(0, 2, 96 + 8 * dip, 13), sk.fill(g(84), 0.5))
    for sx in (-1, 1):                                 # thin white legs, knees wherever the bow puts them
        tube(c, noodle(body.out((sx * 24, 62)), (sx * 40, -16), 197, (0, -90)), 15, SKIN_A, 5)
        ink(c, sk.oval(sx * 60, -9, 35, 15), g(52))
        line(c, [(sx * 46, -17), (sx * 62, -19), (sx * 78, -14)], 3, g(170))
    body.enter(c)
    ink(c, sk.curve([(-43, -8, "c"), (43, -8, "c"), (52, 70, "c"), (7, 70, "c"), (0, 42), (-7, 70, "c"), (-52, 70, "c")]), g(132))
    torso = sk.curve([(-40, 2), (-44, -80), (-52, -150), (-58, -176), (-32, -192), (32, -192), (58, -176), (52, -150),
                      (44, -80), (40, 2), (0, 10)])
    ink(c, torso, g(34))
    line(c, [(-40, -150), (-33, -80), (-30, -20)], 3.5, g(120))
    c.drawPath(sk.oval(0, -190, 20, 10), sk.fill(SKIN_A))
    c.save()
    c.translate(0, -296 + 4 * (late[0] - dip))
    c.rotate(pose(t, A_TILT) + 1.5 * sway)
    asmon_head(c, step(t, A_LOOK), "happy" if proud else None, pose(t, A_BROW), S.mouth(t), proud,
               (9 * (late[1] - sway), 16 * (late[0] - dip)))
    c.restore()
    for sx, hand, (kind, aim) in ((1, pose(t, A_RH), step(t, A_RG)), (-1, pose(t, A_LH), step(t, A_LG))):
        arm = noodle((sx * 54, -176), hand, 186, (0, -330) if hand[1] < -200 else (0, -90))
        tube(c, arm, 14, SKIN_A, 5)
        c.drawPath(sk.part(arm, 0, 0.2), sk.stroke(g(34), 30))
        glove(c, kind, hand, sk.along(arm, 1.0)[1] if aim is None else aim, 0.86)
    c.restore()
    head = body.out((0, -296))
    stink(c, t, head[0], head[1] - 130)
    flies(c, t, head[0], head[1])
    c.restore()


# --- Hasan --------------------------------------------------------------------------------------

HS = 0.9
# The hand on the house's side, then the far one.
H_IN = [(0.0, (-84, -14)), (68.03, (-230, -246)), (69.59, (-84, -14)), (71.00, (-150, -262)), (72.31, (-84, -14)),
        (73.01, (-34, -292))]
H_IG = [(0.0, "fist"), (68.03, "open"), (69.59, "fist")]
H_OUT = [(0.0, (84, -14)), (70.15, (150, -344)), (70.67, (84, -14)), (71.00, (150, -262)), (72.31, (84, -14)),
         (73.01, (182, -244))]
H_OG = [(0.0, "fist"), (73.01, "open")]
H_LEAN = [(0.0, 0.0), (68.03, -3.0), (70.15, -2.0), (72.61, 3.0), (73.01, 9.0)]
H_SHIFT = [(0.0, 0.0), (73.01, 8.0)]
H_TILT = [(0.0, 0.0), (68.03, -4.0), (70.15, 0.0), (72.31, -5.0), (72.61, 0.0), (73.01, 7.0)]
H_LOOK = [(0.0, (-0.7, 0.0)), (68.03, (-1.0, -0.5)), (68.65, (-1.0, 0.9)), (69.59, (-0.7, -1.0)), (70.15, (-0.3, -1.0)),
          (70.67, (-0.7, -1.0)), (72.31, (-1.0, 0.0)), (72.61, (-0.6, -1.0)), (73.01, (-1.0, 0.0))]
H_FACE = [(0.0, "grin"), (72.31, "smirk"), (72.61, "o"), (73.01, "wavy")]
H_BROW = [(0.0, 0.0), (68.03, 0.6), (69.59, 0.0), (72.31, 1.0), (72.61, 1.6), (73.01, -0.8)]


@lru_cache(maxsize=1)
def _hasan_face():
    head = sk.curve(sk.mirror([(0, -92), (58, -90), (92, -60), (99, 0), (97, 48), (78, 84), (40, 97), (0, 99)]))
    low = sk.curve([(-112, -10), (-76, 26), (-42, 30), (-20, 20), (0, 26), (20, 20), (42, 30), (76, 26), (112, -10),
                    (124, 130), (-124, 130)])
    stubble = sk.intersect(head, low)
    dots = []
    for k in range(260):
        x, y = (S.rnd("sx", k) - 0.5) * 196, -4 + S.rnd("sy", k) * 104
        if stubble.contains(x, y) and not (-52 < x < 52 and 34 < y < 78):
            dots.append((x, y))
    return head, stubble, dots


def hasan_head(c, look, shut, brow, face, wide, lag):
    lx, ly = lag
    head, stubble, dots = _hasan_face()
    for sx in (-1, 1):
        ink(c, sk.oval(sx * 100, -4, 14, 22), SKIN_H, 5)
    c.drawPath(head, sk.fill(SKIN_H))
    c.drawPath(stubble, sk.fill(g(170)))
    for x, y in dots:
        c.drawCircle(x, y, 1.8, sk.fill(INK, 0.8))
    c.drawPath(head, sk.stroke(INK, LW))
    if face == "grin":
        shape = sk.curve([(-48, 38, "c"), (0, 47), (48, 38, "c"), (35, 64), (0, 74), (-35, 64)])
        ink(c, shape, WHITE, 4.5)
        c.save()
        c.clipPath(shape, doAntiAlias=True)
        for x in (-30, -15, 0, 15, 30):
            c.drawLine(x, 30, x, 80, sk.stroke(INK, 2.5))
        c.restore()
    elif face == "smirk":
        line(c, [(-32, 56), (2, 60), (36, 47)], 5)
        line(c, [(34, 40), (41, 47), (38, 55)], 3.5)
    elif face == "o":
        ink(c, sk.oval(0, 58, 12, 15), g(30), 4.5)
    else:
        line(c, [(-34, 58), (-17, 50), (0, 60), (17, 50), (34, 58)], 5)
    nx = 6 * look[0]
    nose = sk.curve([(nx - 5, -34), (nx - 18, 10), (nx - 11, 24), (nx, 28), (nx + 11, 24), (nx + 18, 10), (nx + 5, -34)],
                    closed=False)
    c.drawPath(nose, sk.fill(g(216)))
    c.drawPath(nose, sk.stroke(INK, 4.5))
    for sx in (-1, 1):
        ex = sx * 39 + nx * 0.5
        pie_eye(c, ex, -30, 13.5, 21, look, shut, SKIN_H, wide=wide, side=sx)
        inner, outer = (-56 - 13 * brow + 5 * max(0.0, -brow), -66 - 13 * brow)
        c.drawPath(sk.capsule((sx * 13 + nx * 0.5, inner), (sx * 62 + nx * 0.5, outer), 7.5), sk.fill(INK))
    quiff = sk.curve([(-99, -30, "c"), (-107, -78), (-86, -128), (-36, -164 + ly), (30, -175 + ly), (88 + lx, -152 + ly),
                      (118 + lx, -116 + ly, "c"), (93, -106), (101, -66), (99, -30, "c"), (84, -60), (44, -78), (0, -72),
                      (-44, -78), (-84, -60)])
    ink(c, quiff, g(30), 5)
    line(c, [(-72, -98), (-22, -140 + ly), (52 + lx * 0.5, -147 + ly)], 3.5, g(140))
    line(c, [(-52, -84), (0, -113 + ly * 0.5), (72 + lx * 0.5, -118 + ly * 0.5)], 3, g(110))


def hasan(c, t, x, ground):
    dip, sway = pump(t, 0.6)
    late = pump(t - 0.09, 0.6)
    sq = 0.05 * (2 * dip - 1)
    body = Body(5 * sway + pose(t, H_SHIFT), -200 + 18 * dip, 1.6 * sway + pose(t, H_LEAN), 1 + 0.6 * sq, 1 - sq)
    recoil = t >= 73.01
    flex = 71.00 <= t < 72.31
    c.save()
    c.translate(x, ground)
    c.scale(HS, HS)
    c.drawPath(sk.oval(0, 2, 132 + 8 * dip, 15), sk.fill(g(84), 0.5))
    for sx in (-1, 1):
        tube(c, noodle(body.out((sx * 42, 52)), (sx * 62, -18), 150, (0, -60)), 30, SKIN_H)
        ink(c, sk.oval(sx * 88, -11, 43, 18), g(246))
        line(c, [(sx * 52, -2), (sx * 90, 4), (sx * 128, -4)], 3, g(120))
        line(c, [(sx * 72, -24), (sx * 80, -16)], 3)
        line(c, [(sx * 84, -26), (sx * 92, -18)], 3)
    body.enter(c)
    shorts = [(-66, -10, "c"), (66, -10, "c"), (82, 60, "c"), (9, 60, "c"), (0, 34), (-9, 60, "c"), (-82, 60, "c")]
    ink(c, sk.curve(shorts), g(128))
    torso = sk.curve([(-62, 4), (-70, -56), (-112, -136), (-126, -176), (-98, -198), (-46, -206), (46, -206), (98, -198),
                      (126, -176), (112, -136), (70, -56), (62, 4), (0, 12)])
    ink(c, torso, SKIN_H)
    tank = sk.curve([(-78, -202, "c"), (-48, -207, "c"), (-30, -166), (0, -148), (30, -166), (48, -207, "c"), (78, -202, "c"),
                     (88, -168), (101, -128), (70, -56), (62, 4), (0, 12), (-62, 4), (-70, -56), (-101, -128), (-88, -168)])
    ink(c, tank, g(248), 5)
    chain = sk.curve([(-37, -203), (-22, -164), (9 * (late[1] - sway), -146 + 8 * (late[0] - dip)), (22, -164), (37, -203)],
                     closed=False)
    for k in range(15):
        ink(c, sk.oval(*sk.along(chain, (k + 0.5) / 15)[0], 4.4), g(236), 2)
    mx, my = sk.along(chain, 0.5)[0]
    ink(c, sk.oval(mx, my + 13, 11), g(236), 3)
    ink(c, sk.rect(-44, -224, 44, -196), SKIN_H, 5)
    c.save()
    c.translate(0, -300 + 4 * (late[0] - dip))
    c.rotate(pose(t, H_TILT) + 1.2 * sway)
    hasan_head(c, step(t, H_LOOK), "tight" if recoil else None, pose(t, H_BROW), step(t, H_FACE),
               S.ramp(t, 72.61, 0.1) if not recoil else 0.0, (10 * (late[1] - sway), 12 * (late[0] - dip)))
    c.restore()
    fan = 16 * math.sin(t * 19) if recoil else 0.0
    for sx, hand, kind in ((-1, pose(t, H_IN), step(t, H_IG)), (1, pose(t, H_OUT), step(t, H_OG))):
        if sx == 1:
            hand = (hand[0] + fan, hand[1] - abs(fan) * 0.5)
        arm = noodle((sx * 122, -172), hand, 190, (0, -330) if hand[1] < -200 else (0, -100))
        (bx, by), ba = sk.along(arm, 0.3)
        bulge = sk.oval(bx, by, 36 * (1 + (0.22 + 0.12 * S.thump(t)) * flex), 27 * (1 + 0.3 * flex), rot=ba)
        ball = sk.oval(sx * 120, -174, 38)
        for shape in (ball, bulge):
            c.drawPath(shape, sk.stroke(INK, 2 * LW))
        c.drawPath(arm, sk.stroke(INK, 40 + 2 * LW))
        for shape in (ball, bulge):
            c.drawPath(shape, sk.fill(SKIN_H))
        c.drawPath(arm, sk.stroke(SKIN_H, 40))
        _, angle = sk.along(arm, 1.0)
        if recoil and sx == -1:                        # two fingers on the nose
            glove(c, "fist", (hand[0] - 30, hand[1] + 26), -52, 0.92, flip=False)
        else:
            glove(c, kind, hand, angle, 1.0)
    c.restore()
    c.restore()
