"""Chibi battle-rapper sprites, built procedurally at native resolution.

Heads are assembled from simple shapes, then shaded and outlined with
pixel-art rules (4-connected outline, crescent shadows, rim light) so they
stay clean at any integer camera zoom. Everything is drawn facing
screen-right and mirrored for facing=-1.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import PAL

K = PAL["k"]
SKIN, SKIN_SH = PAL["s"], PAL["S"]
HW, HH = 36, 36  # head canvas

INK = {
    "k": K, "w": (255, 255, 255), "W": (255, 255, 255), "e": (24, 20, 44),
    "t": PAL["t"], "m": PAL["m"], "r": (206, 86, 96), "s": SKIN, "S": SKIN_SH,
}

EYES = {
    "open":   ["kkkkk", "kwiek", "kwiik", "..kk."],
    "squint": [".....", "kkkkk", "kwiik", "..kk."],
    "wide":   [".kkk.", "kwwwk", "kwewk", "kwwwk", ".kkk."],
    "blink":  [".....", ".....", "kkkkk", "....."],
    "happy":  [".....", ".kkk.", "k...k", "....."],
    "x":      ["k...k", ".k.k.", "..k..", ".k.k.", "k...k"],
}

MOUTHS = {
    "closed": ["kkkk"],
    "smirk":  ["....k", "kkkk."],
    "frown":  [".kkk.", "k...k"],
    "open":   [".kkkk.", "kttttk", "kmmmmk", ".kkkk."],
    "shout":  [".kkkkkk.", "kttttttk", "kmmmmmmk", "kmmrrmmk", ".kkkkkk."],
    "grin":   ["kkkkkkkk", "kttttttk", ".kkkkkk."],
    "o":      [".kk.", "kmmk", "kmmk", ".kk."],
    "teeth":  ["kkkkkk", "ktktkk", "kkkkkk"],
}

BROWS = {  # per-pixel row offsets, outer end first
    "neutral": [0, 0, 0, 0, 0],
    "angry":   [-1, 0, 0, 1, 1],
    "worried": [1, 1, 0, 0, -1],
    "raised":  [-2, -2, -2, -2, -2],
}


def _mask(fn, size=(HW, HH)):
    m = Image.new("1", size, 0)
    fn(ImageDraw.Draw(m))
    return np.array(m, dtype=bool)


def _shift(m, dx, dy):
    out = np.zeros_like(m)
    h, w = m.shape
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = m[ys0:ys1, xs0:xs1]
    return out


def _grow(m):
    g = m.copy()
    g[1:] |= m[:-1]
    g[:-1] |= m[1:]
    g[:, 1:] |= m[:, :-1]
    g[:, :-1] |= m[:, 1:]
    return g


class Sprite:
    def __init__(self, w, h):
        self.arr = np.zeros((h, w, 4), np.uint8)

    def fill(self, m, c):
        self.arr[m] = tuple(c) + (255,)

    def opaque(self):
        return self.arr[:, :, 3] > 0

    def outline(self, c=K):
        a = self.opaque()
        self.fill(_grow(a) & ~a, c)

    def put(self, x0, y0, rows, ink):
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch in ink:
                    self.arr[y0 + dy, x0 + dx] = tuple(ink[ch]) + (255,)

    def image(self):
        return Image.fromarray(self.arr, "RGBA")


def _features(spr, spec, eyes, brows, mouth):
    ink = dict(INK, i=spec["iris"])
    for ex in spec["eye_x"]:
        spr.put(ex, spec["eye_y"], EYES[eyes], ink)
    styles = (brows, brows) if brows != "smug" else ("neutral", "raised")
    for (bx, inner_right), style in zip(((spec["eye_x"][0], True), (spec["eye_x"][1], False)),
                                        styles):
        offs = BROWS[style] if inner_right else BROWS[style][::-1]
        for i, dy in enumerate(offs):
            for t in range(spec["brow_thick"]):
                spr.arr[spec["brow_y"] + dy + t, bx + i] = spec["brow"] + (255,)
    rows = MOUTHS[mouth]
    mx, my = spec["mouth"]
    spr.put(int(mx + 0.5 - len(rows[0]) / 2), my - (1 if len(rows) > 2 else 0), rows, ink)


def _sam(eyes, brows, mouth):
    spr = Sprite(HW, HH)
    hair, hair_hi, hair_dk = PAL["h"], PAL["H"], (62, 40, 30)
    ears = _mask(lambda d: (d.ellipse((3, 18, 8, 25), fill=1), d.ellipse((27, 18, 32, 25), fill=1)))
    face = _mask(lambda d: d.ellipse((5, 7, 30, 33), fill=1))
    head = face | ears
    rows = np.arange(HH)[:, None]
    cap = _mask(lambda d: d.ellipse((3, 1, 32, 30), fill=1)) & (rows < 14)
    burns = _mask(lambda d: (d.rectangle((4, 12, 6, 19), fill=1), d.rectangle((29, 12, 31, 18), fill=1)))
    fringe = _mask(lambda d: d.polygon([(5, 10), (6, 17), (9, 13), (12, 16), (15, 12), (19, 15),
                                        (22, 12), (26, 15), (29, 12), (31, 16), (31, 10)], fill=1))
    tufts = _mask(lambda d: (d.polygon([(9, 5), (12, 0), (15, 3)], fill=1),
                             d.polygon([(15, 2), (19, -1), (21, 2)], fill=1),
                             d.polygon([(21, 2), (26, 0), (26, 5)], fill=1)))
    hairm = cap | burns | fringe | tufts

    spr.fill(head, SKIN)
    spr.fill(head & ~_shift(head, 2, -2), SKIN_SH)
    spr.fill(_shift(hairm, 0, 1) & head & ~hairm, SKIN_SH)
    spr.fill(hairm, hair)
    spr.fill(hairm & ~_shift(hairm, -1, 2), hair_hi)
    spr.fill(hairm & _shift(head & ~hairm, 0, -1), hair_dk)
    for pts in ([(11, 6), (14, 4)], [(18, 4), (21, 3)], [(24, 6), (27, 5)]):
        spr.fill(_mask(lambda d: d.line(pts, fill=1)) & hairm, hair_hi)
    spr.fill(_mask(lambda d: d.point([(19, 25), (18, 26)], fill=1)), SKIN_SH)
    spr.fill(_mask(lambda d: d.point([(9, 26), (10, 26), (26, 26), (27, 26)], fill=1)),
             (236, 160, 140))
    _features(spr, SPECS["sam"], eyes, brows, mouth)
    spr.outline()
    return spr


def _dario(eyes, brows, mouth):
    spr = Sprite(HW, HH)
    hair, hair_hi, hair_dk = (40, 30, 34), (96, 76, 80), (14, 9, 13)
    face = _mask(lambda d: d.ellipse((6, 9, 30, 34), fill=1))
    ears = _mask(lambda d: (d.ellipse((4, 19, 9, 26), fill=1), d.ellipse((27, 19, 32, 26), fill=1)))
    head = face | ears

    curls = []
    for i in range(14):
        a = math.radians(156 + i * (228 / 13))
        r = 4.4 if i % 2 else 3.6
        curls.append((18 + 14.2 * math.cos(a), 17 + 13.6 * math.sin(a), r))
    for i in range(6):
        curls.append((9 + i * 3.6, 12.5 + (i % 2), 3.0))
    for cx, cy in ((13, 8), (19, 7), (25, 9), (16, 12), (22, 12)):
        curls.append((cx, cy, 3.0))
    bulk = _mask(lambda d: d.ellipse((6, 4, 30, 22), fill=1))

    spr.fill(head, SKIN)
    spr.fill(head & ~_shift(head, 2, -2), SKIN_SH)
    hairm = bulk.copy()
    for cx, cy, r in curls:
        hairm |= _mask(lambda d: d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=1))
    hairm &= ~(face & (np.arange(HH)[:, None] > 14))
    spr.fill(_shift(hairm, 0, 1) & head & ~hairm, SKIN_SH)
    spr.fill(hairm, hair)
    for cx, cy, r in curls:
        dark = _mask(lambda d: d.arc((cx - r, cy - r, cx + r, cy + r), 10, 150, fill=1))
        spr.fill(dark & hairm, hair_dk)
        ring = _mask(lambda d: d.arc((cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1), 190, 290, fill=1))
        spr.fill(ring & hairm, hair_hi)
    spr.fill(_mask(lambda d: d.point([(19, 26), (18, 27)], fill=1)), SKIN_SH)

    _features(spr, SPECS["dario"], eyes, brows, mouth)
    g, glint = PAL["g"], PAL["G"]
    for x0 in (9, 20):
        frame = _mask(lambda d: d.rounded_rectangle((x0, 18, x0 + 7, 24), radius=1, outline=1))
        spr.fill(frame, g)
        spr.fill(_mask(lambda d: d.point([(x0 + 1, 19), (x0 + 2, 19), (x0 + 1, 20)], fill=1)), glint)
    spr.fill(_mask(lambda d: (d.line([(17, 20), (19, 20)], fill=1),
                              d.line([(5, 20), (8, 20)], fill=1),
                              d.line([(28, 20), (30, 20)], fill=1))), g)
    spr.outline()
    return spr


SPECS = {
    "sam": dict(build=_sam, iris=(70, 132, 184), eye_x=(11, 21), eye_y=19, brow_y=16,
                brow_thick=1, brow=PAL["h"], mouth=(18.5, 29)),
    "dario": dict(build=_dario, iris=(96, 70, 52), eye_x=(10, 21), eye_y=20, brow_y=16,
                  brow_thick=2, brow=PAL["d"], mouth=(18.5, 30)),
}


@lru_cache(maxsize=None)
def render_head(who, mouth="closed", brows="neutral", eyes="open", facing=1):
    img = SPECS[who]["build"](eyes, brows, mouth).image()
    return img if facing == 1 else img.transpose(Image.FLIP_LEFT_RIGHT)


def mouth_xy(who, hx, hy, facing):
    mx, my = SPECS[who]["mouth"]
    return (hx + (mx if facing == 1 else HW - 1 - mx), hy + my)


LOOKS = {
    "sam": {"top": PAL["n"], "top_shade": PAL["N"], "legs": PAL["j"], "legs_shade": PAL["J"],
            "shoe": PAL["o"], "shoe_shade": PAL["O"], "collar": "crew"},
    "dario": {"top": PAL["b"], "top_shade": PAL["B"], "legs": PAL["p"], "legs_shade": PAL["P"],
              "shoe": (64, 42, 34), "shoe_shade": (40, 26, 22), "collar": "shirt"},
}


def _limb(d, pts, color, shade):
    d.line(pts, fill=K, width=7, joint="curve")
    d.line(pts, fill=color, width=5, joint="curve")
    d.line([(x + 1, y + 1) for x, y in pts], fill=shade, width=1)


def _fist(d, x, y):
    d.rounded_rectangle([x - 3, y - 3, x + 3, y + 3], radius=1, fill=K)
    d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=SKIN)
    d.line([(x - 2, y + 2), (x + 2, y + 2)], fill=SKIN_SH)


def _finger(d, x, y, f):
    a, b = sorted((x + 3 * f, x + 8 * f))
    d.rectangle([a, y - 2, b, y], fill=K)
    a, b = sorted((x + 3 * f, x + 7 * f))
    d.line([(a, y - 1), (b, y - 1)], fill=SKIN)


def _mic(d, x, y):
    d.rectangle([x - 2, y - 10, x + 2, y - 1], fill=K)
    d.rectangle([x - 1, y - 9, x + 1, y - 2], fill=PAL["r"])
    d.ellipse([x - 4, y - 17, x + 4, y - 9], fill=K)
    d.ellipse([x - 3, y - 16, x + 3, y - 10], fill=PAL["R"])
    for gy in (y - 14, y - 12):
        d.line([(x - 2, gy), (x + 2, gy)], fill=(104, 104, 116))
    d.point([(x - 2, y - 15), (x - 1, y - 15)], fill=(226, 226, 236))


def _arm(pose, sx, sy, f, x, facing, mouth):
    """Elbow and hand for a shoulder at (sx, sy); f is that arm's outward direction."""
    table = {
        "down":  ((2, 8), (3, 16)),
        "cross": ((3, 8), None),
        "point": ((8, 3), (17, 0)),
        "up":    ((5, -6), (6, -17)),
        "pump":  ((7, -2), (9, -12)),
        "hip":   ((8, 7), (3, 14)),
        "shrug": ((8, 4), (12, -4)),
        "mic":   ((7, 10), None),
        "punch": ((9, 0), (19, -1)),
        "reach": ((9, -6), (16, -17)),   # holding a neighbour's raised hand
    }
    (ex, ey), hand = table[pose]
    elbow = (sx + f * ex, sy + ey)
    if pose == "cross":
        return elbow, (x - f * 5, sy + 10)
    if pose == "mic":
        return elbow, (int(mouth[0]) + facing * 6, mouth[1] + 12)
    return elbow, (sx + f * hand[0], sy + hand[1])


def draw_character(img, who, x, y, facing=1, mouth="closed", brows="neutral", eyes="open",
                   back_arm="down", front_arm="down", bob=0, stride=0):
    """Draw a character standing on (x, y). The front arm is the one nearer the opponent.

    `stride` in [-3, 3] spreads the legs for a walk cycle. Returns the head's
    top-left corner and the mouth position, for props and speech bubbles.
    """
    look = LOOKS[who]
    d = ImageDraw.Draw(img)
    feet_y = y
    y += bob
    half = 11
    shoe_top = y - 4
    leg_top = shoe_top - 12
    t_top = leg_top - 21

    spread = abs(stride)
    for lx, s, lifted in ((x - 7, -spread, stride < 0), (x + 2, spread, stride > 0)):
        lift = 1 if lifted else 0
        foot = lx + s
        d.polygon([(lx - 1, leg_top), (lx + 5, leg_top), (foot + 5, shoe_top - lift),
                   (foot - 1, shoe_top - lift)], fill=K)
        d.polygon([(lx, leg_top), (lx + 4, leg_top), (foot + 4, shoe_top - 1 - lift),
                   (foot, shoe_top - 1 - lift)], fill=look["legs"])
        d.line([(lx + 4, leg_top), (foot + 4, shoe_top - 1 - lift)], fill=look["legs_shade"])
        s0 = foot - 2 + (1 if facing == 1 else -2)
        sb = min(y, feet_y) - lift
        d.rounded_rectangle([s0, shoe_top - lift, s0 + 10, sb], radius=1, fill=K)
        d.rectangle([s0 + 1, shoe_top + 1 - lift, s0 + 9, sb - 1], fill=look["shoe"])
        d.line([(s0 + 1, sb - 1), (s0 + 9, sb - 1)], fill=look["shoe_shade"])

    d.rounded_rectangle([x - half - 1, t_top - 1, x + half + 1, leg_top + 1], radius=6, fill=K)
    d.rounded_rectangle([x - half, t_top, x + half, leg_top], radius=5, fill=look["top"])
    back = x - half + 1 if facing == 1 else x + half - 4
    d.rectangle([back, t_top + 4, back + 3, leg_top - 2], fill=look["top_shade"])
    d.line([(x - half + 3, leg_top - 1), (x + half - 3, leg_top - 1)], fill=look["top_shade"])
    if look["collar"] == "crew":
        d.chord([x - 5, t_top - 4, x + 5, t_top + 3], 0, 180, fill=K)
        d.chord([x - 4, t_top - 4, x + 4, t_top + 2], 0, 180, fill=SKIN)
    else:
        collar = (236, 242, 250)
        d.polygon([(x - 7, t_top), (x - 1, t_top + 5), (x - 1, t_top)], fill=collar, outline=K)
        d.polygon([(x + 7, t_top), (x + 1, t_top + 5), (x + 1, t_top)], fill=collar, outline=K)
        d.line([(x, t_top + 6), (x, leg_top - 1)], fill=look["top_shade"])
        for by in range(t_top + 8, leg_top - 1, 4):
            d.point((x + 1, by), fill=(236, 242, 250))
        d.line([(x - half, leg_top), (x + half, leg_top)], fill=(40, 30, 30))

    head = render_head(who, mouth, brows, eyes, facing)
    hx = x - HW // 2 + (1 if facing == 1 else 0)
    hy = t_top - HH + 5
    img.paste(head, (hx, hy), head)
    mouth_pos = mouth_xy(who, hx, hy, facing)

    sy = t_top + 4
    hands = []
    for pose, f in ((back_arm, -facing), (front_arm, facing)):
        sx = x + f * (half - 2)
        elbow, hand = _arm(pose, sx, sy, f, x, facing, mouth_pos)
        _limb(d, [(sx, sy), elbow, hand], look["top"], look["top_shade"])
        hands.append((pose, hand, f))
    for pose, (hx2, hy2), f in hands:
        if pose == "mic":
            _mic(d, hx2, hy2)
        _fist(d, hx2, hy2)
        if pose == "point":
            _finger(d, hx2, hy2, f)
    return {"hx": hx, "hy": hy, "mouth": mouth_pos, "hands": [h for _, h, _ in hands],
            "top": hy, "chest": (x, t_top + 8)}
