"""Hasan and Asmongold as front-view cartoon busts: smooth paths, posed by numbers.

figure(who, pose, at) returns the drawing as a list of Parts, back to front. The rig only says where things
are and what they are (skin, hair, the tank top): a style decides what that looks like, whether a flat fill,
an inked outline, a tube of neon or a sheet of cut paper.

Units are heads: a head is about two units tall, the origin is the middle of the head at rest, y runs down,
and the desk the man sits at is at DESK. `at` = (x, y, scale) puts the origin on the screen. "l" and "r" are
the screen's left and right, not his.

    hasan   the broad square jaw under stubble, heavy black brows, the hair faded at the sides and swept
            up on top, heavy lids, big shoulders and arms in a white tank top, the chain
    asmon   the long narrow face, the centre parting and the hairline in retreat, hair past the shoulders,
            the full scraggly beard, tired eyes with bags, the headphones, a gap in his teeth, thin arms
            in a black T-shirt
"""
import math
from dataclasses import dataclass, fields, replace

import skia

import sk

DESK = 3.5                                   # where the hands rest, in heads below the middle of the head

PAL = {
    "hasan": dict(skin=(226, 172, 130), skin_sh=(196, 138, 100), hair=(40, 32, 36), hair_hi=(84, 70, 76),
                  fade=(104, 82, 76), stub=(170, 122, 96), brow=(34, 28, 32), iris=(104, 66, 40),
                  lip=(176, 104, 90), top=(238, 236, 230), top_sh=(198, 196, 192), chain=(238, 190, 72),
                  tooth=(252, 250, 242)),
    "asmon": dict(skin=(240, 214, 196), skin_sh=(210, 174, 156), hair=(122, 82, 54), hair_sh=(86, 56, 40),
                  hair_hi=(164, 120, 82), beard=(104, 68, 46), brow=(86, 56, 40), iris=(96, 136, 162),
                  lip=(190, 130, 120), top=(38, 38, 48), top_sh=(24, 24, 32), phones=(30, 30, 38),
                  phones_hi=(104, 106, 126), tooth=(232, 214, 150)),
}
COMMON = dict(eye=(252, 250, 246), pupil=(28, 20, 28), mouth=(96, 24, 36), tongue=(214, 92, 100), ink=(26, 20, 28))


def colour(who, key):
    return PAL[who].get(key) or COMMON[key]


@dataclass
class Part:
    name: str
    path: skia.Path
    col: str                # a key of PAL[who] or COMMON
    who: str
    grp: str                # "hair_back", "body", "head", "face", "hair", "arm_l", "arm_r"
    line: int = 2           # 2 a contour, 1 a feature, 0 no line of its own
    open: bool = False      # a stroke rather than a shape
    w: float = 0.0          # the stroke's width in pixels, for open parts
    shade: bool = False     # a shadow on the part before it
    mask: skia.Path = None  # where this part's outline is not drawn: an arm has no line across its own shoulder


@dataclass
class Pose:
    lean: float = 0.0       # the body's tilt in degrees, about the seat
    dx: float = 0.0         # the body moved, in heads
    dy: float = 0.0
    squash: float = 0.0     # squashed (+) or stretched (-)
    head: float = 0.0       # the head's tilt in degrees
    turn: float = 0.0       # the face turned to screen left (-1) or right (1)
    nod: float = 0.0        # the face up (-1) or down (1)
    look_x: float = 0.0     # the pupils, -1..1
    look_y: float = 0.0
    lid: float = 0.0        # the upper lids: 0 open, 1 shut
    wide: float = 0.0       # eyes wide
    brow: float = 0.0       # brows up (+) or down (-)
    frown: float = 0.0      # inner ends down (+, angry) or up (-, worried)
    skew: float = 0.0       # the left brow up and the right one down: doubt
    smile: float = 0.0      # corners of the mouth up (+) or down (-)
    mw: float = 0.80        # the mouth: width, opening, teeth, tongue, lip under the teeth (script.mouth)
    mh: float = 0.0
    teeth: float = 0.0
    tongue: float = 0.0
    mf: float = 0.0
    lx: float = None        # the left hand, in heads from the middle of the head; None rests it on the desk
    ly: float = None
    rx: float = None
    ry: float = None
    grip_l: str = "rest"    # rest, fist, point, open, thumb, pinch
    grip_r: str = "rest"
    aim_l: float = None     # where the finger (or thumb) points, degrees; None follows the forearm
    aim_r: float = None
    tuck_l: bool = False    # the elbow kept in and down (a shrug) rather than out
    tuck_r: bool = False
    blend: dict = None      # set by mix(): hands on their way between the desk and the air

    def say(self, m):
        """This pose with script.mouth(t) for a mouth."""
        return replace(self, mw=m["w"], mh=m["h"], teeth=m["teeth"], tongue=m["tongue"], mf=m["f"])


MOVES = {"lean", "dx", "dy", "squash", "head", "lx", "ly", "rx", "ry"}


def mix(a, b, k, over=None):
    """Pose a moved a fraction k of the way to pose b. `over` is the fraction for the things that travel
    (the body, the head, the hands), which may overshoot 1 and settle. A hand at rest moves from and to
    the desk."""
    if k <= 0:
        return a
    over = k if over is None else over
    if k >= 1 and over == 1:
        return b
    vals, blend = {}, {}
    for f in fields(Pose):
        x, y = getattr(a, f.name), getattr(b, f.name)
        kk = over if f.name in MOVES else min(1.0, k)
        if f.name == "blend":
            continue
        if isinstance(x, (str, bool)) or (x is None and y is None):
            vals[f.name] = y if k >= 0.5 else x
        elif x is None or y is None:
            if f.name in ("lx", "ly", "rx", "ry"):
                vals[f.name], blend[f.name] = None, (x, y, kk)
            else:
                vals[f.name] = y if k >= 0.5 else x
        else:
            vals[f.name] = x + (y - x) * kk
    return Pose(**vals, blend=blend)


# --- the men ------------------------------------------------------------------------------------

BODY = {
    "hasan": dict(shoulder=(1.50, 2.02), upper=1.22, fore=1.12, r=(0.34, 0.27, 0.25, 0.19), hand=0.25,
                  rest=(0.74, DESK - 0.06), neck=(0.36, 0.44), sleeve=0.0),
    "asmon": dict(shoulder=(0.98, 2.00), upper=1.02, fore=0.98, r=(0.17, 0.14, 0.13, 0.105), hand=0.215,
                  rest=(0.50, DESK - 0.05), neck=(0.22, 0.27), sleeve=0.44),
}
FACE = {
    "hasan": dict(eye=(0.35, -0.14), eye_r=(0.17, 0.115), iris=0.086, lid=0.22, brow=((0.13, -0.385), (0.61, -0.44)),
                  brow_r=(0.078, 0.045), mouth=(0.0, 0.60), mouth_w=0.34, mouth_h=0.30),
    "asmon": dict(eye=(0.255, -0.20), eye_r=(0.128, 0.088), iris=0.066, lid=0.34, brow=((0.10, -0.415), (0.42, -0.36)),
                  brow_r=(0.034, 0.024), mouth=(0.0, 0.67), mouth_w=0.25, mouth_h=0.26),
}
HEAD = {
    "hasan": [(0, -1.02), (0.42, -0.99), (0.72, -0.74), (0.81, -0.30), (0.80, 0.22), (0.74, 0.60), (0.50, 0.93),
              (0.20, 1.05), (0, 1.06)],
    "asmon": [(0, -1.10), (0.36, -1.06), (0.59, -0.76), (0.64, -0.28), (0.60, 0.22), (0.50, 0.64), (0.32, 0.98),
              (0.12, 1.15), (0, 1.17)],
}


def outline(path, width, cap=skia.Paint.kRound_Cap):
    """The shape a stroke of this width along the path covers."""
    paint = skia.Paint(Style=skia.Paint.kStroke_Style, StrokeWidth=width, StrokeCap=cap,
                       StrokeJoin=skia.Paint.kRound_Join)
    out = skia.Path()
    paint.getFillPath(path, out)
    return out


def _below(pts, lo=4.0):
    """The region under an open line of points given left to right (down to y = lo)."""
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    return sk.curve([(x0, lo, "c"), (x0, y0, "c"), *pts[1:-1], (x1, y1, "c"), (x1, lo, "c")])


class _Builder:
    def __init__(self, who):
        self.who, self.parts = who, []

    def add(self, name, path, col, grp, line=2, shade=False):
        self.parts.append(Part(name, path, col, self.who, grp, line=line, shade=shade))

    def stroke(self, name, path, col, grp, w, line=1):
        self.parts.append(Part(name, path, col, self.who, grp, line=line, open=True, w=w))


def _eye(b, side, f, p):
    ex, ey = side * f["eye"][0], f["eye"][1]
    rx, ry = f["eye_r"]
    ry = ry * (1 + 0.4 * p.wide)
    lid = max(0.0, min(1.0, f["lid"] * (1 - p.wide) + p.lid * (1 - f["lid"] * (1 - p.wide))))
    shape = sk.curve([(ex - rx, ey + 0.012, "c"), (ex - rx * 0.1, ey - ry), (ex + rx, ey - 0.008, "c"),
                      (ex + rx * 0.05, ey + ry * 0.86)])
    mid = ey - ry + lid * ry * 1.86                       # the lid line's middle: the top, then down past the corners
    lash = [(ex - rx * 1.04, ey + 0.012), (ex - rx * 0.1, mid), (ex + rx * 1.04, ey - 0.008)]
    vis = sk.intersect(shape, _below(lash)) if lid > 0.02 else shape
    if lid < 0.97:
        b.add("eye", vis, "eye", "face", line=1)
        cx, cy = ex + p.look_x * rx * 0.44, ey + p.look_y * ry * 0.42 + lid * ry * 0.25
        b.add("iris", sk.intersect(sk.oval(cx, cy, f["iris"]), vis), "iris", "face", line=0)
        b.add("pupil", sk.intersect(sk.oval(cx, cy, f["iris"] * 0.52), vis), "pupil", "face", line=0)
        if lid < 0.6:
            b.add("glint", sk.intersect(sk.oval(cx - f["iris"] * 0.38, cy - f["iris"] * 0.42, f["iris"] * 0.24), vis),
                  "eye", "face", line=0)
    b.stroke("lash", sk.curve(lash, closed=False), "pupil", "face", 0.034 if b.who == "hasan" else 0.026)
    if b.who == "asmon":                                  # the bags
        b.stroke("bag", sk.curve([(ex - rx * 0.85, ey + ry * 1.25), (ex, ey + ry * 1.75), (ex + rx * 0.85, ey + ry * 1.25)],
                                 closed=False), "skin_sh", "face", 0.022)


def _brow(b, side, f, p):
    (ix, iy), (ox, oy) = f["brow"]
    r_in, r_out = f["brow_r"]
    lift = -0.11 * p.brow + 0.07 * p.skew * side
    rot = -side * 16 * p.frown
    cx, cy = side * (ix + ox) / 2, (iy + oy) / 2
    path = sk.capsule((side * ix, iy), (side * ox, oy), r_in, r_out)
    b.add("brow", sk.xf(path, 0, lift, rot=rot, about=(cx, cy)), "brow", "face", line=0)


def _mouth(b, f, p):
    cx, cy = f["mouth"]
    w = f["mouth_w"] * p.mw
    h = f["mouth_h"] * p.mh
    lift = -0.07 * p.smile                                # the corners
    if h < 0.018:                                         # shut: a line that smiles or doesn't
        sag = 0.085 * p.smile
        line = sk.curve([(cx - w, cy + lift), (cx - w * 0.5, cy + lift * 0.3 + sag * 0.8), (cx, cy + sag),
                         (cx + w * 0.5, cy + lift * 0.3 + sag * 0.8), (cx + w, cy + lift)], closed=False)
        b.stroke("lips", line, "pupil", "face", 0.036)
        return
    up, low = 0.34 * h + 0.012, 0.66 * h + 0.014 + 0.05 * max(0.0, p.smile)
    shape = sk.curve([(cx - w, cy + lift, "c"), (cx - w * 0.5, cy - up), (cx, cy - up * 0.92), (cx + w * 0.5, cy - up),
                      (cx + w, cy + lift, "c"), (cx + w * 0.55, cy + low), (cx, cy + low * 1.08), (cx - w * 0.55, cy + low)])
    b.add("mouth", shape, "mouth", "face", line=1)
    if p.tongue > 0.05:
        b.add("tongue", sk.intersect(sk.oval(cx, cy + low * 1.02, w * 0.56, 0.05 + 0.07 * p.tongue), shape), "tongue",
              "face", line=0)
    if p.teeth > 0.05:
        depth = (0.05 + 0.055 * p.teeth) * (1 + 0.6 * p.mf)
        teeth = sk.intersect(sk.rect(cx - w, cy - up - 0.1, cx + w, cy - up * 0.92 + depth), shape)
        if b.who == "asmon":                              # not all of them
            teeth = sk.minus(teeth, sk.rect(cx - w * 0.44, cy - 1, cx - w * 0.20, cy + 1))
            teeth = sk.minus(teeth, sk.rect(cx + w * 0.34, cy - 1, cx + w * 0.50, cy + 1))
        b.add("teeth", teeth, "tooth", "face", line=0)
        if p.teeth > 0.9 and p.mf < 0.5:                  # ee, s: the lower row too
            b.add("teeth", sk.intersect(sk.rect(cx - w * 0.8, cy + low * 1.08 - 0.05, cx + w * 0.8, cy + low + 0.2), shape),
                  "tooth", "face", line=0)


def _head_hasan(b, p):
    f = FACE["hasan"]
    fx, fy = 0.13 * p.turn, 0.09 * p.nod                  # the face slides over the skull as he turns
    head = sk.curve(sk.mirror(HEAD["hasan"]))
    for side in (-1, 1):
        b.add("ear", sk.oval(side * 0.84 - 0.05 * p.turn, 0.04, 0.10, 0.20, rot=side * -8), "skin", "head")
    b.add("head", head, "skin", "head")
    b.add("head_sh", sk.minus(head, sk.xf(head, -0.20 + 0.06 * p.turn, -0.05)), "skin_sh", "head", line=0, shade=True)
    # the stubble: down from the sideburns, over the lip and the chin
    edge = [(-1.0, -0.22), (-0.66 + fx * 0.5, -0.20), (-0.61 + fx * 0.5, 0.20), (-0.47 + fx, 0.42), (-0.30 + fx, 0.40),
            (-0.15 + fx, 0.37), (fx, 0.395), (0.15 + fx, 0.37), (0.30 + fx, 0.40), (0.47 + fx, 0.42),
            (0.61 + fx * 0.5, 0.20), (0.66 + fx * 0.5, -0.20), (1.0, -0.22)]
    b.add("stubble", sk.intersect(head, _below([(x, y + fy * 0.6) for x, y in edge])), "stub", "head", line=0)
    face = _Builder("hasan")
    nose = [(0.06, -0.10), (0.11, 0.10), (0.17, 0.24), (0.11, 0.34), (0.0, 0.365), (-0.11, 0.34), (-0.16, 0.26)]
    face.add("nose_sh", sk.curve([(0.03, -0.14, "c"), (0.12, 0.08), (0.18, 0.24), (0.11, 0.35), (0.0, 0.37, "c")]),
             "skin_sh", "face", line=0, shade=True)
    face.stroke("nose", sk.curve(nose, closed=False), "skin_sh", "face", 0.034)
    _mouth(face, f, p)
    for side in (-1, 1):
        _eye(face, side, f, p)
        _brow(face, side, f, p)
    b.parts += [replace(q, path=sk.xf(q.path, fx * (1.5 if q.name.startswith("nose") else 1.0), fy)) for q in face.parts]
    # the hair: faded at the sides, swept up and over on top
    hx = 0.05 * p.turn
    for side in (-1, 1):
        b.add("fade", sk.curve([(side * 0.80, -0.20), (side * 0.885, -0.52), (side * 0.84, -0.80), (side * 0.60, -0.72),
                                (side * 0.71, -0.50), (side * 0.735, -0.24)]), "fade", "hair", line=0)
    top = [(-0.84, -0.50), (-0.92, -0.84), (-0.74, -1.20), (-0.36, -1.42), (0.10, -1.52), (0.52, -1.46), (0.84, -1.20),
           (0.95, -0.82), (0.85, -0.50), (0.74, -0.52, "c"), (0.69, -0.60), (0.52, -0.80, "c"), (0.24, -0.71), (0.0, -0.755),
           (-0.25, -0.70), (-0.52, -0.80, "c"), (-0.69, -0.60), (-0.74, -0.52, "c")]
    b.add("hair", sk.xf(sk.curve(top), hx, 0), "hair", "hair")
    for k, (y0, y1) in enumerate(((-1.02, -1.20), (-1.20, -1.34))):
        b.stroke("hair_hi", sk.xf(sk.curve([(-0.52, y0), (-0.05, y1 - 0.02), (0.50, y1 + 0.10)], closed=False), hx, 0),
                 "hair_hi", "hair", 0.045 - 0.012 * k, line=0)


def _head_asmon(b, p):
    f = FACE["asmon"]
    fx, fy = 0.11 * p.turn, 0.09 * p.nod
    head = sk.curve(sk.mirror(HEAD["asmon"]))
    b.add("head", head, "skin", "head")
    b.add("head_sh", sk.minus(head, sk.xf(head, -0.15 + 0.05 * p.turn, -0.04)), "skin_sh", "head", line=0, shade=True)
    b.stroke("wrinkle", sk.curve([(-0.24 + fx, -0.55 + fy), (fx, -0.585 + fy), (0.24 + fx, -0.55 + fy)], closed=False),
             "skin_sh", "head", 0.022)
    # the beard: from the sideburns round under the chin, and over the lip
    beard = [(-0.645, -0.14), (-0.67, 0.30), (-0.60, 0.78), (-0.44, 1.14), (-0.31, 1.30, "c"), (-0.21, 1.44),
             (-0.11, 1.36, "c"), (0.0, 1.55), (0.11, 1.38, "c"), (0.21, 1.46), (0.31, 1.30, "c"), (0.44, 1.14),
             (0.60, 0.78), (0.67, 0.30), (0.645, -0.14), (0.545, -0.10, "c"), (0.50 + fx * 0.5, 0.26), (0.37 + fx, 0.42),
             (0.20 + fx, 0.36), (0.07 + fx, 0.385), (fx, 0.42), (-0.07 + fx, 0.385), (-0.20 + fx, 0.36),
             (-0.37 + fx, 0.42), (-0.50 + fx * 0.5, 0.26), (-0.545, -0.10, "c")]
    b.add("beard", sk.curve(beard), "beard", "head")
    face = _Builder("asmon")
    face.add("nose_sh", sk.curve([(0.025, -0.16, "c"), (0.085, 0.08), (0.125, 0.27), (0.07, 0.35), (0.0, 0.365, "c")]),
             "skin_sh", "face", line=0, shade=True)
    face.stroke("nose", sk.curve([(0.045, -0.12), (0.075, 0.10), (0.125, 0.27), (0.07, 0.345), (0.0, 0.365),
                                  (-0.075, 0.34), (-0.11, 0.28)], closed=False), "skin_sh", "face", 0.028)
    _mouth(face, f, p)
    for side in (-1, 1):
        _eye(face, side, f, p)
        _brow(face, side, f, p)
    b.parts += [replace(q, path=sk.xf(q.path, fx * (1.5 if q.name.startswith("nose") else 1.0), fy)) for q in face.parts]
    # the hair in front: parted in the middle, the hairline well back, down over the shoulders
    for side in (-1, 1):
        lock = [(0.025, -1.13), (0.34, -1.115), (0.63, -0.84), (0.735, -0.30), (0.75, 0.40), (0.83, 1.30), (0.88, 2.16),
                (0.66, 2.36, "c"), (0.47, 2.10), (0.50, 1.30), (0.525, 0.50), (0.575, -0.10), (0.515, -0.52), (0.37, -0.80),
                (0.15, -0.95), (0.035, -0.87, "c")]
        b.add("lock", sk.curve([(side * x, y, *c) for x, y, *c in lock]), "hair", "hair")
        for k, (x0, x1) in enumerate(((0.60, 0.66), (0.70, 0.78))):
            b.stroke("strand", sk.curve([(side * (x0 - 0.06), -0.50), (side * x0, 0.40), (side * (x0 + 0.03), 1.20),
                                         (side * x1, 2.0)], closed=False), "hair_sh" if k == 0 else "hair_hi", "hair", 0.03,
                     line=0)
    for x0, x1, y1 in ((-0.03, -0.20, -0.62), (0.04, 0.24, -0.66), (0.02, 0.10, -0.56)):
        b.stroke("wisp", sk.curve([(x0, -0.93), ((x0 + x1) / 2 + 0.03, -0.80), (x1, y1)], closed=False), "hair", "hair",
                 0.018, line=0)
    # the headphones
    band = sk.curve([(-0.74, -0.16), (-0.70, -0.82), (-0.36, -1.18), (0.0, -1.265), (0.36, -1.18), (0.70, -0.82),
                     (0.74, -0.16)], closed=False)
    b.add("band", outline(band, 0.12), "phones", "hair")
    for side in (-1, 1):
        b.add("cup", sk.oval(side * 0.745, -0.04, 0.18, 0.31, rot=side * 4), "phones", "hair")
        b.add("cup_hi", sk.oval(side * 0.775, -0.04, 0.085, 0.20, rot=side * 4), "phones_hi", "hair", line=0)


def _hand(grip, hand, elbow, r, side, aim):
    """A hand at `hand`, at the end of a forearm from `elbow`: a mitten, with a finger out when it points."""
    hx, hy = hand
    th = math.atan2(hy - elbow[1], hx - elbow[0])
    ux, uy = math.cos(th), math.sin(th)                  # along the forearm
    vx, vy = -uy * side, ux * side                       # across it, towards the thumb

    def at(a, c):
        return hx + ux * a * r + vx * c * r, hy + uy * a * r + vy * c * r

    palm = sk.xf(sk.oval(0, 0, r * 1.02, r * 0.88), *at(0.45, 0), rot=math.degrees(th))
    thumb = sk.capsule(at(0.0, -0.55), at(0.75, -1.02), r * 0.34, r * 0.28)
    if grip == "point":
        a = th if aim is None else math.radians(aim)
        base = at(0.95, -0.22)
        tip = base[0] + math.cos(a) * r * 1.9, base[1] + math.sin(a) * r * 1.9
        return sk.union(palm, sk.capsule(at(-0.1, -0.5), at(0.45, -0.95), r * 0.34, r * 0.3),
                        sk.capsule(base, tip, r * 0.33, r * 0.27))
    if grip == "open":
        fingers = [sk.capsule(at(0.8, c * 0.9), at(2.1 - 0.25 * abs(c), c * 1.95), r * 0.28, r * 0.24)
                   for c in (-0.55, -0.18, 0.18, 0.55)]
        return sk.union(sk.xf(sk.oval(0, 0, r * 1.05, r * 0.98), *at(0.45, 0), rot=math.degrees(th)),
                        sk.capsule(at(0.05, -0.6), at(0.75, -1.65), r * 0.33, r * 0.27), *fingers)
    if grip == "thumb":
        a = -math.pi / 2 if aim is None else math.radians(aim)
        base = at(0.35, -0.5)
        tip = base[0] + math.cos(a) * r * 1.75, base[1] + math.sin(a) * r * 1.75
        return sk.union(palm, sk.capsule(base, tip, r * 0.36, r * 0.3))
    if grip == "pinch":
        return sk.union(palm, sk.capsule(at(0.8, -0.4), at(1.6, -0.15), r * 0.3, r * 0.24),
                        sk.capsule(at(0.2, -0.7), at(1.35, -0.75), r * 0.32, r * 0.25))
    return sk.union(palm, thumb)


def _arm(b, side, p, who):
    spec = BODY[who]
    grp = "arm_l" if side < 0 else "arm_r"
    sx, sy = side * spec["shoulder"][0], spec["shoulder"][1]
    hx, hy = (p.lx, p.ly) if side < 0 else (p.rx, p.ry)
    rest = (side * spec["rest"][0], spec["rest"][1])
    blend = p.blend or {}
    key = ("lx", "ly") if side < 0 else ("rx", "ry")
    if key[0] in blend:                                  # moving between the desk and the air
        (x0, x1, k), (y0, y1, _) = blend[key[0]], blend[key[1]]
        x0, y0 = rest if x0 is None else (x0, y0)
        x1, y1 = rest if x1 is None else (x1, y1)
        hx, hy = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
    elif hx is None:
        hx, hy = rest
    grip = p.grip_l if side < 0 else p.grip_r
    aim = p.aim_l if side < 0 else p.aim_r
    l1, l2 = spec["upper"], spec["fore"]
    dx, dy = hx - sx, hy - sy
    d = max(abs(l1 - l2) + 0.02, min(l1 + l2 - 0.01, math.hypot(dx, dy)))
    th = math.atan2(dy, dx)
    hx, hy = sx + math.cos(th) * d, sy + math.sin(th) * d
    a = math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    elbows = [(sx + l1 * math.cos(th + s * a), sy + l1 * math.sin(th + s * a)) for s in (-1, 1)]
    tuck = p.tuck_l if side < 0 else p.tuck_r
    ex, ey = max(elbows, key=lambda e: e[0] * side * (-0.5 if tuck else 1.0) + e[1] * (1.0 if tuck else 0.6))
    r0, r1, r2, r3 = spec["r"]
    b.add("upper", sk.capsule((sx, sy), (ex, ey), r0, r1), "skin", grp)
    if spec["sleeve"]:
        k = spec["sleeve"]
        b.add("sleeve", sk.capsule((sx, sy), (sx + (ex - sx) * k, sy + (ey - sy) * k), r0 * 1.30, r0 * 1.36), "top", grp)
    b.add("fore", sk.capsule((ex, ey), (hx, hy), r2, r3), "skin", grp)
    b.add("hand", _hand(grip, (hx, hy), (ex, ey), spec["hand"], side, aim), "skin", grp)


def _body_hasan(b):
    n0, n1 = BODY["hasan"]["neck"]
    torso = sk.mirror([(0, 1.30), (0.44, 1.33), (0.96, 1.54), (1.50, 1.74), (1.80, 2.06), (1.84, 2.60), (1.66, 3.70, "c"),
                       (0, 3.70, "c")])
    b.add("torso", sk.curve(torso), "skin", "body")
    b.add("neck", sk.poly([(-n0, 0.70), (n0, 0.70), (n1, 1.52), (-n1, 1.52)]), "skin", "body", line=0)
    b.add("neck_sh", sk.curve([(-n0, 0.95, "c"), (n0, 0.95, "c"), (n0 + 0.03, 1.20), (0, 1.40), (-n0 - 0.03, 1.20)]),
          "skin_sh", "body", line=0, shade=True)
    tank = sk.mirror([(0, 2.12), (0.30, 1.90), (0.45, 1.50, "c"), (0.72, 1.56, "c"), (0.86, 1.96), (1.10, 2.44),
                      (1.26, 2.90), (1.48, 3.70, "c"), (0, 3.70, "c")])
    b.add("tank", sk.curve(tank), "top", "body")
    b.stroke("chain", sk.curve([(-0.43, 1.50), (-0.26, 1.86), (0.0, 2.0), (0.26, 1.86), (0.43, 1.50)], closed=False),
             "chain", "body", 0.055, line=0)


def _body_asmon(b):
    n0, n1 = BODY["asmon"]["neck"]
    b.add("neck", sk.poly([(-n0, 0.80), (n0, 0.80), (n1 + 0.04, 1.62), (-n1 - 0.04, 1.62)]), "skin", "body", line=0)
    tee = sk.mirror([(0, 1.68), (0.20, 1.60), (0.33, 1.42, "c"), (0.72, 1.60), (1.03, 1.84), (1.16, 2.20), (1.12, 3.70, "c"),
                     (0, 3.70, "c")])
    b.add("tee", sk.curve(tee), "top", "body")


def figure(who, pose, at):
    """The man as Parts in screen coordinates, back to front: hair behind, body, head, hair, arms."""
    x, y, s = at
    b = _Builder(who)
    if who == "asmon":
        back = sk.mirror([(0, -1.20), (0.45, -1.17), (0.77, -0.86), (0.87, -0.30), (0.90, 0.50), (0.96, 1.40), (1.0, 2.20),
                          (0.70, 2.38, "c"), (0, 2.20, "c")])
        b.add("hair_back", sk.curve(back), "hair_sh", "hair_back")
        n_back = len(b.parts)
        _body_asmon(b)
        n_body = len(b.parts)
        _head_asmon(b, pose)
    else:
        n_back = 0
        _body_hasan(b)
        n_body = len(b.parts)
        _head_hasan(b, pose)
    n_head = len(b.parts)
    for side in (-1, 1):
        _arm(b, side, pose, who)
    # the head turns on the neck; the whole man leans from the seat; then onto the screen
    m_head = sk.matrix(rot=pose.head, about=(0.0, 0.95))
    m_body = sk.matrix(pose.dx, pose.dy, rot=pose.lean, sx=1 + 0.6 * pose.squash, sy=1 - pose.squash, about=(0.0, DESK))
    m_at = sk.matrix(x, y, s)
    def onto(path, is_head):
        path = skia.Path(path)
        if is_head:
            path.transform(m_head)
        path.transform(m_body)
        path.transform(m_at)
        return path

    trunk = next(onto(q.path, False) for q in b.parts if q.name in ("torso", "tee"))
    out = []
    for i, q in enumerate(b.parts):
        is_head = n_body <= i < n_head or (who == "asmon" and i < n_back)
        out.append(replace(q, path=onto(q.path, is_head), w=q.w * s, mask=trunk if q.name in ("upper", "sleeve") else None))
    return out


def anchor(who, pose, at, point):
    """Where a point of the head (in heads from its middle) lands on the screen under this pose."""
    x, y, s = at
    m = sk.matrix(x, y, s)
    m.preConcat(sk.matrix(pose.dx, pose.dy, rot=pose.lean, sx=1 + 0.6 * pose.squash, sy=1 - pose.squash, about=(0.0, DESK)))
    m.preConcat(sk.matrix(rot=pose.head, about=(0.0, 0.95)))
    q = m.mapXY(*point)
    return q.x(), q.y()
