"""Procedural chibi sprites: King George III, George Washington and the Town Crier.

Each figure is drawn facing right on a 40x56 canvas with its feet at (20, 52),
then outlined in ink; `figure()` mirrors it to face left and adds a rim light
on the sun side. Poses are small dicts of named parts, cached per combination:

    mouth   closed open wide o smirk frown grit smile
    eyes    open blink shut wide side x
    brows   neutral angry up worried
    arm     down mic point fist palm hold cross hip shrug wave chop   (the near arm)
    mic     True: the far hand holds a mic in front of the face (for rapping)
    hat     on askew off                                               (crown or tricorn)
    flush   0, 1 (cheeks), 2 (face red with rage)
    lean    upper body shift in pixels (+ toward facing), bob: upper body down

Anchors come back in canvas pixels: feet, head (centre), mouth, hand (near
hand), mic (mic head), top (top of hat or crown).
"""
from functools import lru_cache

import numpy as np
from PIL import Image

from engine import INK, Canvas, mirror, outlined

CW, CH = 40, 56
OX, OY = 5, 5                 # offset of the design grid (a 30x50 figure) inside the canvas
FEET = (20, 52)

HEADS = {
    # eye (x, y), mouth box top-left, nose top, dy of the shoulders relative to George
    "george": dict(eye=(20, 16), mouth=(20, 19), nose=(25, 16), sh=0, face=(12, 10, 24, 23)),
    "washington": dict(eye=(20, 11), mouth=(20, 15), nose=(25, 12), sh=-4, face=(12, 6, 24, 20)),
    "crier": dict(eye=(20, 12), mouth=(20, 16), nose=(25, 13), sh=-3, face=(12, 7, 24, 21)),
}
SLEEVE = {"george": ("red", "red_sh", "ermine"), "washington": ("navy", "navy_sh", "buff"),
          "crier": ("green", "green_sh", "white")}

DEFAULT = dict(mouth="closed", eyes="open", brows="neutral", arm="down", mic=False, hat="on", flush=0,
               lean=0, bob=0, bell=False)


class Fig(Canvas):
    """A Canvas that draws in design-grid coordinates, shifted by (ox, oy)."""

    def __init__(self, ox=OX, oy=OY):
        super().__init__(CW, CH)
        self.ox, self.oy = ox, oy

    def _p(self, pts):
        return [(x + self.ox, y + self.oy) for x, y in pts]

    def _b(self, box):
        x0, y0, x1, y1 = box
        return (x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy)

    def rect(self, box, col):
        super().rect(self._b(box), col)

    def ell(self, box, col):
        super().ell(self._b(box), col)

    def poly(self, pts, col):
        super().poly(self._p(pts), col)

    def line(self, pts, col, w=1):
        super().line(self._p(pts), col, w)

    def px(self, xy, col):
        super().px(self._p([xy])[0], col)

    def pxs(self, pts, col):
        for p in pts:
            self.px(p, col)


# --- bodies (lower half: drawn once, never leans) ------------------------------

def legs_george(f):
    f.rect((10, 40, 14, 45), "white"); f.rect((16, 40, 20, 45), "white")
    f.rect((10, 43, 11, 45), "white_sh"); f.rect((16, 43, 17, 45), "white_sh")
    f.rect((9, 46, 14, 47), "boot"); f.rect((16, 46, 21, 47), "boot")
    f.px((12, 46), "gold"); f.px((18, 46), "gold")


def legs_washington(f):
    f.rect((10, 36, 14, 41), "buff"); f.rect((16, 36, 20, 41), "buff")
    f.rect((10, 41, 14, 47), "boot"); f.rect((16, 41, 20, 47), "boot")
    f.rect((10, 41, 14, 41), "boot_hi"); f.rect((16, 41, 20, 41), "boot_hi")
    f.rect((9, 47, 14, 47), "boot"); f.rect((16, 47, 21, 47), "boot")


def legs_crier(f):
    f.rect((10, 40, 14, 45), "white"); f.rect((16, 40, 20, 45), "white")
    f.rect((10, 43, 11, 45), "white_sh"); f.rect((16, 43, 17, 45), "white_sh")
    f.rect((9, 46, 14, 47), "boot"); f.rect((16, 46, 21, 47), "boot")
    f.px((12, 46), "steel"); f.px((18, 46), "steel")


# --- torsos ----------------------------------------------------------------------

def torso_george(f):
    f.poly([(9, 24), (21, 24), (24, 41), (6, 41)], "red")
    f.poly([(9, 24), (12, 24), (10, 41), (6, 41)], "red_sh")
    f.line([(15, 26), (16, 41)], "gold")
    for y in (29, 33, 37):
        f.px((18, y), "gold")
    f.line([(10, 27), (21, 38)], "sash", 2)
    f.line([(10, 29), (19, 38)], "sash_sh")
    f.px((20, 36), "gold"); f.px((19, 37), "gold")          # the Garter star
    f.ell((7, 22, 23, 29), "ermine")
    f.rect((7, 26, 23, 27), "ermine_sh")
    for xy in ((9, 25), (13, 27), (17, 24), (20, 26), (11, 23)):
        f.px(xy, "ink")
    f.rect((17, 22, 19, 26), "white")


def torso_washington(f):
    f.poly([(9, 20), (21, 20), (23, 38), (7, 39)], "navy")
    f.poly([(9, 20), (12, 20), (10, 39), (7, 39)], "navy_sh")
    f.poly([(16, 21), (21, 21), (21, 34), (17, 34)], "buff")
    f.line([(16, 21), (16, 34)], "buff_sh")
    for y in (24, 27, 30):
        f.px((19, y), "gold")
    f.rect((8, 20, 12, 21), "gold"); f.rect((8, 22, 12, 22), "gold_sh")
    f.rect((18, 20, 22, 21), "gold"); f.rect((18, 22, 22, 22), "gold_sh")
    f.line([(17, 22), (20, 31)], "sash")                    # the blue ribbon of a commander-in-chief
    f.rect((15, 18, 19, 20), "white")


def torso_crier(f):
    f.poly([(9, 23), (21, 23), (25, 42), (5, 42)], "green")
    f.poly([(9, 23), (12, 23), (9, 42), (5, 42)], "green_sh")
    f.line([(16, 25), (17, 42)], "gold")
    for y in (28, 32, 36, 40):
        f.px((19, y), "gold")
    f.rect((14, 21, 19, 25), "white")                        # bands at the neck
    f.rect((16, 25, 17, 28), "white"); f.px((16, 28), "white_sh")
    f.rect((5, 34, 8, 36), "brown")                          # satchel
    f.line([(7, 24), (7, 34)], "brown_sh")


# --- heads -------------------------------------------------------------------------

def head_george(f, pose):
    f.ell((7, 7, 22, 21), "wig")
    f.ell((6, 13, 11, 18), "wig_sh"); f.ell((6, 17, 11, 22), "wig_sh")
    f.ell((7, 13, 11, 17), "wig"); f.ell((7, 17, 11, 21), "wig")
    f.rect((3, 16, 6, 18), "ink"); f.px((2, 15), "ink"); f.px((2, 19), "ink")
    f.ell((12, 10, 24, 23), "skin")
    f.rect((12, 17, 14, 22), "skin_sh")
    f.px((25, 16), "skin"); f.px((25, 17), "skin")
    f.poly([(11, 9), (22, 9), (23, 12), (11, 13)], "wig")
    f.line([(12, 12), (22, 11)], "wig_sh")


def crown(f, state, dx=0, dy=0):
    if state == "off":
        return
    if state == "askew":
        f.poly([(9 + dx, 7 + dy), (18 + dx, 3 + dy), (19 + dx, 6 + dy), (10 + dx, 10 + dy)], "gold")
        f.line([(10 + dx, 10 + dy), (19 + dx, 6 + dy)], "gold_sh")
        for x, y in ((9, 4), (13, 2), (18, 0)):
            f.rect((x + dx, y + dy, x + dx, y + dy + 2), "gold")
        f.px((14 + dx, 6 + dy), "jewel")
        return
    f.rect((11 + dx, 6 + dy, 20 + dx, 8 + dy), "gold"); f.rect((11 + dx, 8 + dy, 20 + dx, 8 + dy), "gold_sh")
    for x in (11, 15, 20):
        f.rect((x + dx, 3 + dy, x + dx, 5 + dy), "gold")
    f.rect((13 + dx, 4 + dy, 13 + dx, 5 + dy), "gold"); f.rect((18 + dx, 4 + dy, 18 + dx, 5 + dy), "gold")
    f.px((15 + dx, 7 + dy), "jewel"); f.px((12 + dx, 7 + dy), "sash"); f.px((19 + dx, 7 + dy), "sash")
    f.px((15 + dx, 2 + dy), "gold_hi")


def head_washington(f, pose):
    f.ell((8, 5, 21, 18), "hair")
    f.ell((8, 11, 12, 15), "hair_sh"); f.ell((9, 11, 12, 14), "hair")
    f.rect((4, 13, 7, 15), "ink"); f.px((3, 12), "ink"); f.px((3, 16), "ink")
    f.ell((12, 6, 24, 20), "skin")
    f.rect((12, 13, 14, 19), "skin_sh")
    f.px((25, 12), "skin"); f.px((25, 13), "skin")
    f.rect((21, 18, 23, 19), "skin_sh")                     # the long jaw


def tricorn(f, state, dx=0, dy=0, trim=None):
    if state == "off":
        return
    if state == "askew":
        f.poly([(7 + dx, 9 + dy), (25 + dx, 3 + dy), (21 + dx, 0 + dy), (13 + dx, 0 + dy), (8 + dx, 4 + dy)], "hat")
        f.line([(7 + dx, 9 + dy), (25 + dx, 3 + dy)], trim or "gold_sh")
        f.ell((18 + dx, 1 + dy, 21 + dx, 4 + dy), "ink")
        return
    f.poly([(6 + dx, 7 + dy), (26 + dx, 7 + dy), (23 + dx, 3 + dy), (16 + dx, 1 + dy), (9 + dx, 3 + dy)], "hat")
    f.line([(6 + dx, 7 + dy), (26 + dx, 7 + dy)], trim or "gold_sh")
    f.line([(10 + dx, 3 + dy), (16 + dx, 1 + dy)], "hat_hi")
    if trim is None:
        f.ell((20 + dx, 3 + dy, 23 + dx, 6 + dy), "ink"); f.px((21 + dx, 4 + dy), "hat_hi")   # black cockade


def head_crier(f, pose):
    f.ell((8, 6, 21, 19), "wig")
    f.ell((7, 12, 11, 17), "wig_sh"); f.ell((8, 12, 11, 16), "wig")
    f.ell((12, 7, 24, 21), "skin")
    f.rect((12, 14, 14, 20), "skin_sh")
    f.px((25, 13), "skin"); f.px((25, 14), "skin"); f.px((26, 14), "skin")
    f.pxs([(22, 17), (23, 17)], "flush")                    # a town crier's ruddy cheeks


def face(f, who, pose):
    h = HEADS[who]
    ex, ey = h["eye"]
    mx, my = h["mouth"]
    eyes, brows, mouth = pose["eyes"], pose["brows"], pose["mouth"]
    if pose["flush"] >= 2:
        a = np.array(f.img)
        x0, y0, x1, y1 = f._b(h["face"])
        box = a[y0:y1 + 3, x0:x1 + 3]
        for src, dst in (((244, 204, 174), (238, 132, 118)), ((216, 164, 136), (196, 96, 96))):
            box[np.all(box[..., :3] == src, axis=-1), :3] = dst
        f.img.paste(Image.fromarray(a))
    elif pose["flush"]:
        f.pxs([(ex + 1, my - 1), (ex + 2, my - 1), (ex + 2, my - 2)], "flush")
    # eyes
    if eyes == "open":
        f.rect((ex, ey, ex, ey + 1), "eye")
        if who == "george":
            f.px((ex + 1, ey), "white")                     # the bulging Hanover eye
    elif eyes == "blink":
        f.line([(ex - 1, ey + 1), (ex + 1, ey + 1)], "ink")
    elif eyes == "shut":
        f.pxs([(ex - 1, ey + 1), (ex, ey), (ex + 1, ey + 1)], "ink")
    elif eyes == "wide":
        f.rect((ex - 1, ey - 1, ex + 1, ey + 1), "white")
        f.px((ex + 1, ey), "eye")
    elif eyes == "side":
        f.rect((ex - 1, ey, ex - 1, ey + 1), "eye")
    elif eyes == "x":
        f.pxs([(ex - 1, ey - 1), (ex + 1, ey - 1), (ex, ey), (ex - 1, ey + 1), (ex + 1, ey + 1)], "ink")
    # brows
    by = ey - 1
    if brows == "neutral":
        f.line([(ex - 1, by), (ex, by)], "ink")
    elif brows == "angry":
        f.pxs([(ex - 1, by - 1), (ex, by), (ex + 1, by)], "ink")
    elif brows == "up":
        f.line([(ex - 1, by - 2), (ex + 1, by - 2)], "ink")
    elif brows == "worried":
        f.pxs([(ex - 1, by), (ex, by - 1), (ex + 1, by - 2)], "ink")
    # mouth
    if mouth == "closed":
        f.line([(mx, my + 1), (mx + 3, my + 1)], "mouth")
    elif mouth == "open":
        f.rect((mx, my, mx + 3, my + 2), "mouth"); f.line([(mx, my), (mx + 3, my)], "white")
    elif mouth == "wide":
        f.rect((mx - 1, my, mx + 3, my + 3), "mouth"); f.line([(mx - 1, my), (mx + 3, my)], "white")
        f.line([(mx, my + 3), (mx + 2, my + 3)], "tongue")
    elif mouth == "o":
        f.rect((mx + 1, my, mx + 2, my + 2), "mouth")
    elif mouth == "smirk":
        f.pxs([(mx, my + 1), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my)], "mouth")
    elif mouth == "frown":
        f.pxs([(mx, my + 1), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my + 2)], "mouth")
    elif mouth == "grit":
        f.rect((mx, my, mx + 3, my + 2), "white"); f.line([(mx, my + 1), (mx + 3, my + 1)], "ink")
    elif mouth == "smile":
        f.rect((mx, my, mx + 3, my + 1), "white"); f.pxs([(mx, my - 1), (mx + 3, my - 1)], "mouth")
        f.line([(mx + 1, my + 2), (mx + 2, my + 2)], "mouth")


# --- arms ----------------------------------------------------------------------------

def mic_hand(f, who, sh):
    """The far hand holding a mic just in front of the face."""
    sleeve, shade, cuff = SLEEVE[who]
    f.poly([(19, 26 + sh), (24, 25 + sh), (25, 28 + sh), (20, 29 + sh)], shade)
    f.rect((24, 24 + sh, 25, 28 + sh), cuff)
    f.rect((26, 25 + sh, 27, 28 + sh), "skin")
    f.rect((27, 20 + sh, 28, 25 + sh), "mic")
    f.ell((26, 16 + sh, 29, 20 + sh), "mic_hi"); f.px((27, 17 + sh), "white")


def near_arm(f, who, arm, sh):
    """The near arm; returns the hand position in design-grid coordinates."""
    sleeve, shade, cuff = SLEEVE[who]
    y = sh
    if arm == "down":
        f.poly([(17, 25 + y), (21, 25 + y), (22, 35 + y), (18, 35 + y)], sleeve)
        f.line([(17, 26 + y), (18, 35 + y)], shade)
        f.rect((18, 35 + y, 22, 36 + y), cuff)
        f.rect((19, 37 + y, 21, 38 + y), "skin")
        return (20, 38 + y)
    if arm == "mic":
        f.rect((18, 27 + y, 25, 30 + y), sleeve); f.rect((18, 30 + y, 25, 30 + y), shade)
        f.rect((24, 26 + y, 25, 31 + y), cuff)
        f.rect((26, 27 + y, 27, 30 + y), "skin")
        f.rect((27, 22 + y, 28, 27 + y), "mic"); f.ell((26, 19 + y, 29, 23 + y), "mic_hi"); f.px((27, 20 + y), "white")
        return (27, 28 + y)
    if arm == "point":
        f.poly([(17, 26 + y), (24, 27 + y), (25, 30 + y), (18, 31 + y)], sleeve)
        f.line([(18, 31 + y), (25, 30 + y)], shade)
        f.rect((24, 26 + y, 25, 30 + y), cuff)
        f.rect((26, 27 + y, 27, 29 + y), "skin"); f.line([(28, 27 + y), (30, 27 + y)], "skin")
        return (30, 27 + y)
    if arm == "fist":
        f.poly([(17, 27 + y), (21, 27 + y), (28, 15 + y), (25, 13 + y)], sleeve)
        f.line([(17, 27 + y), (25, 14 + y)], shade)
        f.rect((25, 11 + y, 29, 12 + y), cuff)
        f.rect((26, 7 + y, 29, 10 + y), "skin"); f.line([(27, 8 + y), (27, 10 + y)], "skin_sh")
        return (27, 8 + y)
    if arm == "wave":
        f.poly([(17, 27 + y), (21, 27 + y), (28, 15 + y), (25, 13 + y)], sleeve)
        f.line([(17, 27 + y), (25, 14 + y)], shade)
        f.rect((25, 11 + y, 29, 12 + y), cuff)
        f.rect((26, 6 + y, 28, 10 + y), "skin"); f.px((29, 8 + y), "skin"); f.px((25, 7 + y), "skin")
        return (27, 7 + y)
    if arm == "palm":
        f.poly([(17, 26 + y), (23, 28 + y), (23, 31 + y), (17, 31 + y)], sleeve)
        f.line([(17, 31 + y), (23, 31 + y)], shade)
        f.rect((23, 27 + y, 24, 31 + y), cuff)
        f.rect((25, 29 + y, 28, 30 + y), "skin"); f.px((28, 28 + y), "skin")
        return (27, 28 + y)
    if arm == "hold":
        f.poly([(17, 26 + y), (23, 27 + y), (23, 31 + y), (17, 31 + y)], sleeve)
        f.line([(17, 31 + y), (23, 31 + y)], shade)
        f.rect((23, 26 + y, 24, 31 + y), cuff)
        f.rect((25, 27 + y, 27, 30 + y), "skin")
        return (26, 28 + y)
    if arm == "chop":
        f.poly([(17, 26 + y), (22, 27 + y), (26, 33 + y), (22, 34 + y)], sleeve)
        f.line([(22, 34 + y), (26, 33 + y)], shade)
        f.rect((25, 32 + y, 26, 35 + y), cuff)
        f.line([(27, 34 + y), (30, 36 + y)], "skin"); f.line([(27, 35 + y), (29, 36 + y)], "skin")
        return (29, 36 + y)
    if arm == "cross":
        f.rect((9, 28 + y, 22, 32 + y), sleeve)
        f.line([(9, 32 + y), (22, 32 + y)], shade)
        f.line([(13, 28 + y), (18, 32 + y)], shade)
        f.rect((20, 28 + y, 21, 30 + y), cuff); f.rect((22, 28 + y, 23, 30 + y), "skin")
        f.rect((9, 30 + y, 10, 32 + y), cuff)
        return (22, 29 + y)
    if arm == "hip":
        f.poly([(17, 26 + y), (22, 27 + y), (25, 32 + y), (21, 35 + y), (19, 33 + y), (21, 31 + y)], sleeve)
        f.line([(21, 35 + y), (25, 32 + y)], shade)
        f.rect((19, 33 + y, 20, 36 + y), "skin")
        return (19, 34 + y)
    if arm == "shrug":
        f.poly([(17, 26 + y), (22, 28 + y), (26, 27 + y), (26, 30 + y), (21, 32 + y), (17, 31 + y)], sleeve)
        f.rect((26, 26 + y, 27, 30 + y), cuff)
        f.line([(28, 27 + y), (30, 26 + y)], "skin"); f.line([(28, 28 + y), (30, 28 + y)], "skin")
        f.rect((3, 28 + y, 7, 31 + y), SLEEVE[who][1]); f.rect((1, 27 + y, 2, 29 + y), "skin")
        return (30, 26 + y)
    raise ValueError(arm)


def bell(f, sh, ringing):
    """The crier's brass handbell, held up in the near hand."""
    y = sh
    f.poly([(17, 27 + y), (21, 26 + y), (25, 16 + y), (22, 15 + y)], "green")
    f.line([(17, 27 + y), (22, 16 + y)], "green_sh")
    f.rect((22, 13 + y, 26, 14 + y), "white")
    f.rect((23, 10 + y, 25, 12 + y), "skin")
    f.rect((23, 6 + y, 24, 10 + y), "wood")
    t = 2 if ringing else 0
    f.poly([(21 + t, 6 + y), (27 + t, 6 + y), (26 + t, 1 + y), (22 + t, 1 + y)], "gold")
    f.line([(22 + t, 1 + y), (21 + t, 6 + y)], "gold_hi")
    f.line([(21 + t, 6 + y), (27 + t, 6 + y)], "gold_sh")
    f.px((24 + t, 7 + y), "gold_sh")


# --- whole figures ----------------------------------------------------------------------

@lru_cache(maxsize=4096)
def _figure(who, key):
    pose = dict(key)
    sh = HEADS[who]["sh"]
    lower = Fig()
    {"george": legs_george, "washington": legs_washington, "crier": legs_crier}[who](lower)
    upper = Fig(OX + pose["lean"], OY + pose["bob"])
    {"george": torso_george, "washington": torso_washington, "crier": torso_crier}[who](upper)
    {"george": head_george, "washington": head_washington, "crier": head_crier}[who](upper, pose)
    face(upper, who, pose)
    if who == "george":
        crown(upper, pose["hat"])
    elif who == "washington":
        tricorn(upper, pose["hat"])
    else:
        tricorn(upper, pose["hat"], dy=1, trim="gold")
        upper.pxs([(12, 4), (13, 3)], "white")               # a feather
    if pose["mic"] and pose["arm"] not in ("mic", "cross"):
        mic_hand(upper, who, sh)
    if who == "crier" and pose["bell"]:
        bell(upper, sh, pose["bell"] == "ring")
        hand = (24, 10 + sh)
    else:
        hand = near_arm(upper, who, pose["arm"], sh)
    img = lower.img
    img.alpha_composite(upper.img)
    img = outlined(img)
    dx, dy = OX + pose["lean"], OY + pose["bob"]
    h = HEADS[who]
    fx0, fy0, fx1, fy1 = h["face"]
    anchors = dict(
        feet=FEET,
        head=((fx0 + fx1) / 2 + dx, (fy0 + fy1) / 2 + dy),
        mouth=(h["mouth"][0] + 2 + dx, h["mouth"][1] + 1 + dy),
        eye=(h["eye"][0] + dx, h["eye"][1] + dy),
        hand=(hand[0] + dx, hand[1] + dy),
        mic=(27.5 + dx, 18 + sh + dy),
        top=(16 + dx, (3 if who == "george" else 1) + dy),
    )
    return img, anchors


def pose_key(**pose):
    p = dict(DEFAULT)
    p.update(pose)
    return tuple(sorted(p.items()))


def figure(who, facing=1, rim=0.0, **pose):
    """(RGBA sprite, anchors) for a character; facing -1 mirrors it. `rim` adds a warm rim light
    on the side the character faces (the sun sits between the two shores)."""
    img, a = _figure(who, pose_key(**pose))
    if rim:
        img = rim_light(img, 1, amount=rim)
    if facing < 0:
        img = mirror(img)
        a = {k: (CW - 1 - x, y) for k, (x, y) in a.items()}
    return img, a


def rim_light(spr, side, color=(255, 200, 146), amount=0.5):
    """Warm light on the pixels just inside the outline on one side (+1 right, -1 left)."""
    a = np.array(spr).astype(np.float32)
    solid = a[..., 3] > 0
    ink = np.all(a[..., :3] == INK, axis=-1)
    body = solid & ~ink
    outside = np.zeros_like(solid)
    if side > 0:
        outside[:, :-2] = ~solid[:, 2:]
    else:
        outside[:, 2:] = ~solid[:, :-2]
    sel = body & outside
    a[sel, :3] = a[sel, :3] * (1 - amount) + np.array(color, np.float32) * amount
    return Image.fromarray(a.round().astype(np.uint8))


# --- loose props that come off the characters ------------------------------------------

@lru_cache(maxsize=None)
def crown_sprite():
    f = Fig(ox=-9, oy=-1)
    crown(f, "on")
    img = f.done()
    return img.crop(img.getbbox())


@lru_cache(maxsize=None)
def tricorn_sprite():
    f = Fig(ox=-4, oy=1)
    tricorn(f, "on")
    img = f.done()
    return img.crop(img.getbbox())


if __name__ == "__main__":
    from engine import ROOT
    poses = [dict(), dict(mic=True, mouth="open", arm="point"), dict(mic=True, mouth="wide", arm="fist", brows="angry"),
             dict(arm="cross", mouth="smirk", eyes="shut", brows="up"), dict(arm="palm", mouth="o", eyes="wide", brows="worried"),
             dict(arm="hip", mouth="frown", flush=2, brows="angry"), dict(arm="shrug", mouth="smile"),
             dict(arm="chop", mic=True, mouth="grit", hat="askew"), dict(arm="wave", eyes="x", hat="off", mouth="wide")]
    sheet = Image.new("RGB", (len(poses) * 42 + 4, 3 * 58 + 4), (90, 80, 100))
    for j, who in enumerate(("george", "washington", "crier")):
        for i, p in enumerate(poses):
            if who == "crier" and i == 1:
                p = dict(bell="ring", mouth="wide")
            img, a = figure(who, facing=1 if who != "george" else -1, rim=0.4, **p)
            sheet.paste(img, (4 + i * 42, 4 + j * 58), img)
    out = ROOT / "build" / "cast.png"
    out.parent.mkdir(exist_ok=True)
    sheet.resize((sheet.width * 6, sheet.height * 6), Image.NEAREST).save(out)
    print(out)
