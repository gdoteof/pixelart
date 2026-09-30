"""Procedural chibi sprites of Sir David ("david") and Morgan ("morgan").

Each figure is drawn facing right on a 40x56 canvas with its feet at (20, 52),
then outlined in ink; `figure()` mirrors it to face left. Poses are small
dicts of named parts, cached per combination:

    body    stand crouch sit kneel walk1 walk2 lie              (whole-body stance)
    mouth   closed open wide o smirk frown grit smile grin
    eyes    open blink shut wide side x half
    brows   neutral angry up worried
    arm     down mic point fist palm hold cross hip shrug wave chop whisper up
    mic     True: the far hand holds a mic in front of the face (for rapping); "fluffy": a field mic
    hat     none pith chauffeur fedora crown headphones cap
    outfit  david: field prison      morgan: suit god prison chauffeur president tux lucius madiba
    glasses True: round specs;   flush 0-2;   lean, bob: upper body shifts in pixels

Anchors come back in canvas pixels: feet, head (centre), mouth, eye, hand
(near hand), mic (mic head), top (top of the head).
"""
from functools import lru_cache

from PIL import Image

from engine import Canvas, mirror, outlined, rim_light

CW, CH = 40, 56
OX, OY = 5, 5                 # offset of the design grid (a 30x50 figure) inside the canvas
FEET = (20, 52)
EYE, MOUTH, NOSE = (20, 11), (20, 15), (25, 12)
FACE = (12, 6, 24, 20)

DEFAULT = dict(body="stand", mouth="closed", eyes="open", brows="neutral", arm="down", mic=False, hat="none",
               outfit=None, glasses=False, flush=0, lean=0, bob=0)
OUTFITS = {"david": ("field", "prison"),
           "morgan": ("suit", "god", "prison", "chauffeur", "president", "tux", "lucius", "madiba")}

# (sleeve, sleeve shade, cuff) per outfit; skin per character
SLEEVES = {
    "field": ("shirt", "shirt_sh", "shirt_hi"), "prison": ("denim", "denim_sh", "denim_hi"),
    "suit": ("suit", "suit_sh", "white"), "god": ("wsuit", "wsuit_sh", "wsuit_hi"),
    "chauffeur": ("chauf", "chauf_sh", "white"), "president": ("navy", "navy_sh", "white"),
    "tux": ("black", "suit_sh", "white"), "lucius": ("suit", "suit_sh", "white"),
    "madiba": ("gold_sh", "wood_sh", "gold_sh"),
}
SKIN = {"david": ("skin", "skin_sh"), "morgan": ("mskin", "mskin_sh")}


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


# --- legs (the lower body never leans) ---------------------------------------------

def trouser_cols(who, outfit):
    if who == "david":
        return ("denim", "denim_sh", "black") if outfit == "prison" else ("khaki", "khaki_sh", "shoe")
    return {"god": ("wsuit", "wsuit_sh", "wsuit_sh"), "prison": ("denim", "denim_sh", "black"),
            "chauffeur": ("chauf", "chauf_sh", "black"), "president": ("navy", "navy_sh", "black"),
            "tux": ("black", "suit_sh", "black"), "madiba": ("suit", "suit_sh", "black")}.get(outfit,
                                                                                            ("suit", "suit_sh", "black"))


def legs(f, who, outfit, body):
    cloth, shade, shoe = trouser_cols(who, outfit)
    if body in ("stand", "walk1", "walk2"):
        a, b = {"stand": (0, 0), "walk1": (-2, 2), "walk2": (2, -2)}[body]
        f.poly([(10, 38), (14, 38), (14 + a, 46), (10 + a, 46)], cloth)
        f.poly([(16, 38), (20, 38), (20 + b, 46), (16 + b, 46)], cloth)
        f.line([(10, 39), (10 + a, 46)], shade)
        f.rect((9 + a, 46, 14 + a, 47), shoe)
        f.rect((16 + b, 46, 21 + b, 47), shoe)
    elif body == "crouch":
        # the presenter's crouch: thighs forward to the knee, shins down, heels up
        f.poly([(8, 39), (13, 37), (25, 38), (26, 42), (11, 44)], cloth)
        f.line([(11, 44), (26, 42)], shade)
        f.poly([(21, 40), (26, 40), (25, 46), (21, 46)], cloth)
        f.line([(21, 41), (21, 46)], shade)
        f.poly([(7, 42), (12, 42), (12, 46), (7, 46)], shade)
        f.rect((12, 43, 20, 46), shade)
        f.rect((5, 46, 12, 47), shoe)
        f.rect((20, 46, 27, 47), shoe)
    elif body == "sit":
        f.rect((9, 38, 22, 41), cloth)
        f.line([(9, 41), (22, 41)], shade)
        f.rect((19, 41, 22, 46), cloth)
        f.rect((19, 46, 24, 47), shoe)
    elif body == "kneel":
        f.poly([(9, 38), (15, 38), (22, 42), (20, 45), (12, 42)], cloth)
        f.rect((6, 43, 13, 46), cloth)
        f.line([(6, 46), (13, 46)], shade)
        f.rect((3, 45, 7, 47), shoe)
        f.rect((20, 40, 23, 46), cloth)
        f.rect((20, 46, 25, 47), shoe)


# --- torsos ------------------------------------------------------------------------

def torso(f, who, outfit):
    sleeve, shade, cuff = SLEEVES[outfit]
    skin = SKIN[who][0]
    f.poly([(9, 20), (21, 20), (23, 39), (7, 39)], sleeve)
    f.poly([(9, 20), (12, 20), (10, 39), (7, 39)], shade)
    if who == "david":
        if outfit == "prison":
            f.poly([(14, 20), (18, 20), (16, 24)], skin)
            f.rect((17, 27, 21, 30), "white"); f.px((18, 28), "ink"); f.px((20, 28), "ink")     # number patch
        else:
            f.poly([(14, 20), (19, 20), (16, 25)], skin)                  # open collar
            f.line([(13, 20), (16, 25)], "shirt_hi"); f.line([(19, 20), (16, 25)], "shirt_hi")
            f.rect((18, 27, 20, 29), "shirt_sh"); f.px((19, 26), "red")   # breast pocket and a pen
            f.line([(15, 26), (15, 38)], "shirt_sh")
            f.rect((8, 36, 22, 37), "khaki_sh")                           # tucked in, belt
            f.px((16, 36), "gold")
        return
    if outfit in ("suit", "god", "president", "lucius", "chauffeur", "tux"):
        shirt = "wsuit_hi" if outfit == "god" else "white"
        tie = {"god": "wsuit_sh", "president": "red", "tux": None, "chauffeur": "black"}.get(outfit, "tie")
        f.poly([(14, 20), (19, 20), (18, 30), (15, 30)], shirt)
        if outfit == "tux":
            f.rect((15, 20, 18, 21), "black"); f.px((16, 21), "black")                  # bow tie
            f.poly([(12, 20), (14, 20), (16, 32), (13, 36)], "suit_sh")                 # satin lapels
            f.pxs([(16, 25), (16, 28)], "ink")
        else:
            f.poly([(16, 21), (17, 21), (18, 28), (16, 30), (15, 28)], tie)
            f.line([(13, 20), (16, 31)], shade); f.line([(20, 20), (17, 31)], shade)     # lapels
        if outfit == "president":
            f.px((13, 24), "red"); f.px((13, 23), "white")                              # flag pin
        if outfit == "chauffeur":
            for y in (26, 30, 34):
                f.px((18, y), "gold")
    elif outfit == "prison":
        f.poly([(14, 20), (18, 20), (16, 23)], skin)
        f.line([(16, 23), (16, 38)], "denim_sh")
        f.rect((17, 26, 21, 29), "white"); f.px((18, 27), "ink"); f.px((20, 27), "ink")
    elif outfit == "madiba":
        f.poly([(9, 20), (21, 20), (23, 39), (7, 39)], "gold")
        for y in range(22, 39, 4):
            f.line([(9, y), (22, y + 1)], "wood")
            f.pxs([(11, y + 2), (15, y + 2), (19, y + 2)], "red")
        f.poly([(9, 20), (12, 20), (10, 39), (7, 39)], "gold_sh")
        f.rect((14, 19, 18, 20), "wood")


# --- heads -------------------------------------------------------------------------

def head_david(f, pose):
    f.ell((7, 4, 21, 18), "hair")                                          # the swept-back mane
    f.ell((6, 9, 11, 17), "hair_sh"); f.ell((7, 9, 11, 16), "hair")
    f.ell((12, 6, 24, 20), "skin")
    f.rect((12, 13, 14, 19), "skin_sh")
    f.rect((12, 11, 13, 14), "skin"); f.px((12, 12), "skin_sh"); f.px((12, 13), "skin_sh")  # ear
    f.poly([(10, 6), (15, 3), (22, 3), (24, 6), (21, 7), (15, 7), (11, 10)], "hair")         # swept top
    f.line([(14, 5), (21, 4)], "hair_sh")
    f.px((25, 12), "skin"); f.px((25, 13), "skin"); f.px((26, 13), "skin")                   # the nose
    f.px((21, 17), "skin_sh")                                                                 # smile line
    f.px((22, 9), "skin_sh")


def head_morgan(f, pose):
    f.ell((8, 5, 21, 18), "mskin")
    f.ell((12, 6, 24, 20), "mskin")
    f.rect((12, 13, 14, 19), "mskin_sh")
    f.ell((11, 10, 14, 15), "mskin"); f.px((12, 12), "mskin_sh"); f.px((12, 13), "mskin_sh")
    f.px((12, 15), "gold")                                                                    # the stud
    f.poly([(8, 9), (10, 5), (16, 3), (21, 4), (23, 6), (16, 5), (11, 7), (9, 11)], "mhair")  # close white crop
    f.line([(9, 10), (10, 13)], "mhair_sh")
    f.px((25, 12), "mskin"); f.px((25, 13), "mskin"); f.px((26, 13), "mskin")
    # the white beard along the jaw, and the moustache
    f.poly([(13, 16), (15, 19), (19, 21), (23, 20), (25, 17), (24, 16), (22, 18), (18, 18), (15, 16)], "mhair")
    f.line([(15, 19), (21, 20)], "mhair_sh")
    f.line([(20, 14), (24, 14)], "mhair")
    f.pxs([(22, 14), (24, 13)], "freckle")                                                    # freckles


HATS = {}


def hat(f, who, kind):
    if kind == "none":
        return
    if kind == "pith":
        f.ell((9, 0, 23, 8), "khaki"); f.rect((7, 6, 25, 7), "khaki_sh"); f.line([(11, 5), (21, 5)], "wood_sh")
        f.px((12, 2), "paper")
    elif kind == "chauffeur":
        f.rect((10, 2, 22, 5), "chauf"); f.rect((11, 1, 21, 2), "chauf_hi")
        f.rect((17, 5, 25, 6), "black"); f.px((16, 3), "gold")
    elif kind == "fedora":
        f.rect((10, 1, 21, 5), "suit_sh"); f.rect((7, 5, 25, 6), "suit_sh"); f.line([(10, 4), (21, 4)], "tie")
        f.line([(12, 1), (19, 1)], "suit_hi")
    elif kind == "cap":
        f.ell((10, 1, 22, 7), "red"); f.rect((19, 5, 26, 6), "red_sh")
    elif kind == "crown":
        f.rect((11, 1, 21, 4), "gold"); f.line([(11, 4), (21, 4)], "gold_sh")
        for x in (11, 16, 21):
            f.rect((x, -1, x, 1), "gold")
        f.px((16, 2), "red"); f.px((13, 2), "sea"); f.px((19, 2), "sea")
    elif kind == "headphones":
        f.line([(10, 8), (13, 2), (19, 1)], "black", 2)
        f.rect((9, 9, 13, 15), "black"); f.rect((10, 10, 12, 14), "mic")


def face(f, who, pose):
    ex, ey = EYE
    mx, my = MOUTH
    eyes, brows, mouth = pose["eyes"], pose["brows"], pose["mouth"]
    skin_sh = SKIN[who][1]
    if pose["flush"] >= 2:
        f.pxs([(ex + 1, my - 1), (ex + 2, my - 1), (ex + 2, my - 2), (ex - 1, my - 1)], "flush")
    elif pose["flush"]:
        f.pxs([(ex + 1, my - 1), (ex + 2, my - 1)], "flush")
    # eyes
    if eyes == "open":
        f.rect((ex, ey, ex, ey + 1), "eye")
    elif eyes == "half":
        f.px((ex, ey + 1), "eye"); f.line([(ex - 1, ey), (ex + 1, ey)], skin_sh)
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
    if pose["glasses"]:
        f.rect((ex - 2, ey - 1, ex + 2, ey + 2), "ink"); f.rect((ex - 1, ey, ex + 1, ey + 1), "glass")
        if eyes in ("open", "half", "wide", "side"):
            f.px((ex, ey + 1 if eyes != "wide" else ey), "eye")
        f.line([(ex - 3, ey), (ex - 6, ey - 1)], "ink")
    # brows: Sir David's are big and white, Morgan's grey
    bc = "hair_sh" if who == "david" else "mhair_sh"
    by = ey - 2
    if brows == "neutral":
        f.line([(ex - 1, by), (ex + 1, by)], bc)
    elif brows == "angry":
        f.pxs([(ex - 1, by - 1), (ex, by), (ex + 1, by + 1)], bc)
    elif brows == "up":
        f.line([(ex - 1, by - 1), (ex + 1, by - 1)], bc)
    elif brows == "worried":
        f.pxs([(ex - 1, by + 1), (ex, by), (ex + 1, by - 1)], bc)
    if who == "david":
        f.px((ex + 2, by), bc); f.px((ex - 2, by), bc)
    # mouth (Morgan's sits in the beard)
    if mouth == "closed":
        f.line([(mx, my + 1), (mx + 3, my + 1)], "mouth")
    elif mouth == "open":
        f.rect((mx, my, mx + 3, my + 2), "mouth"); f.line([(mx, my), (mx + 3, my)], "tooth")
    elif mouth == "wide":
        f.rect((mx - 1, my, mx + 3, my + 3), "mouth"); f.line([(mx - 1, my), (mx + 3, my)], "tooth")
        f.line([(mx, my + 3), (mx + 2, my + 3)], "tongue")
    elif mouth == "o":
        f.rect((mx + 1, my, mx + 2, my + 2), "mouth")
    elif mouth == "smirk":
        f.pxs([(mx, my + 1), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my)], "mouth")
    elif mouth == "frown":
        f.pxs([(mx, my + 2), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my + 2)], "mouth")
    elif mouth == "grit":
        f.rect((mx, my, mx + 3, my + 2), "tooth"); f.line([(mx, my + 1), (mx + 3, my + 1)], "ink")
    elif mouth == "smile":
        f.pxs([(mx, my), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my)], "mouth")
    elif mouth == "grin":
        f.rect((mx, my, mx + 3, my + 1), "tooth"); f.pxs([(mx - 1, my - 1), (mx + 4, my - 1)], "mouth")
        f.line([(mx, my + 2), (mx + 3, my + 2)], "mouth")


# --- arms ----------------------------------------------------------------------------

def mic_head(f, top, style):
    """The mic's head above the handle: a chrome ball, or a field recordist's furry windshield."""
    if style == "fluffy":
        f.ell((24, top - 3, 31, top + 5), "fluff")
        f.pxs([(23, top), (32, top + 2), (27, top - 4), (30, top - 3), (24, top + 5), (29, top + 6)], "fluff")
        f.pxs([(25, top - 2), (27, top - 3), (30, top - 1), (26, top), (28, top + 2), (31, top + 3)], "fluff_hi")
        f.pxs([(29, top + 1), (26, top + 3), (25, top + 4), (29, top + 4), (27, top + 5)], "fluff_sh")
    else:
        f.ell((26, top, 29, top + 4), "mic_hi"); f.px((27, top + 1), "white")


def mic_hand(f, who, outfit, style="hand"):
    sleeve, shade, cuff = SLEEVES[outfit]
    skin = SKIN[who][0]
    f.poly([(19, 26), (24, 25), (25, 28), (20, 29)], shade)
    f.rect((24, 24, 25, 28), cuff)
    f.rect((26, 25, 27, 28), skin)
    f.rect((27, 20, 28, 25), "mic")
    mic_head(f, 16, style)


def near_arm(f, who, outfit, arm, mic_style="hand"):
    """The near arm; returns the hand position in design-grid coordinates."""
    sleeve, shade, cuff = SLEEVES[outfit]
    skin, skin_sh = SKIN[who]
    rolled = who == "david" and outfit == "field"       # Sir David's rolled-up shirt sleeves
    fore = skin if rolled else sleeve
    if arm == "down":
        f.poly([(17, 22), (21, 22), (22, 33), (18, 33)], sleeve)
        f.line([(17, 23), (18, 33)], shade)
        f.rect((18, 30 if rolled else 33, 22, 33), fore if rolled else cuff)
        f.rect((19, 34, 21, 36), skin)
        return (20, 36)
    if arm == "mic":
        f.rect((18, 25, 25, 28), sleeve); f.rect((18, 28, 25, 28), shade)
        f.rect((22 if rolled else 24, 24, 25, 29), fore if rolled else cuff)
        f.rect((26, 25, 27, 28), skin)
        f.rect((27, 20, 28, 25), "mic"); mic_head(f, 17, mic_style)
        return (27, 26)
    if arm == "point":
        f.poly([(17, 23), (24, 25), (25, 28), (18, 28)], sleeve)
        f.line([(18, 28), (25, 28)], shade)
        f.rect((22 if rolled else 24, 24, 25, 28), fore if rolled else cuff)
        f.rect((26, 25, 27, 27), skin); f.line([(28, 25), (30, 25)], skin)
        return (30, 25)
    if arm in ("fist", "up"):
        f.poly([(17, 24), (21, 24), (28, 12), (25, 10)], sleeve)
        f.line([(17, 24), (25, 11)], shade)
        f.rect((25, 8, 29, 9), fore if rolled else cuff)
        if arm == "fist":
            f.rect((26, 4, 29, 7), skin); f.line([(27, 5), (27, 7)], skin_sh)
        else:
            f.rect((26, 3, 28, 7), skin); f.px((29, 5), skin); f.px((25, 4), skin)
        return (27, 5)
    if arm == "wave":
        f.poly([(17, 24), (21, 24), (28, 12), (25, 10)], sleeve)
        f.line([(17, 24), (25, 11)], shade)
        f.rect((25, 8, 29, 9), fore if rolled else cuff)
        f.rect((26, 3, 28, 7), skin); f.px((29, 5), skin); f.px((25, 4), skin)
        return (27, 4)
    if arm == "palm":
        f.poly([(17, 23), (23, 25), (23, 28), (17, 28)], sleeve)
        f.line([(17, 28), (23, 28)], shade)
        f.rect((21 if rolled else 23, 24, 24 if rolled else 24, 28), fore if rolled else cuff)
        f.rect((25, 26, 28, 27), skin); f.px((28, 25), skin); f.px((26, 25), skin)
        return (27, 25)
    if arm == "hold":
        f.poly([(17, 23), (23, 24), (23, 28), (17, 28)], sleeve)
        f.line([(17, 28), (23, 28)], shade)
        f.rect((23, 23, 24, 28), fore if rolled else cuff)
        f.rect((25, 24, 27, 27), skin)
        return (26, 25)
    if arm == "chop":
        f.poly([(17, 23), (22, 24), (26, 30), (22, 31)], sleeve)
        f.line([(22, 31), (26, 30)], shade)
        f.rect((25, 29, 26, 32), fore if rolled else cuff)
        f.line([(27, 31), (30, 33)], skin); f.line([(27, 32), (29, 33)], skin)
        return (29, 33)
    if arm == "cross":
        f.rect((9, 25, 22, 29), sleeve)
        f.line([(9, 29), (22, 29)], shade)
        f.line([(13, 25), (18, 29)], shade)
        f.rect((20, 25, 21, 27), fore if rolled else cuff); f.rect((22, 25, 23, 27), skin)
        f.rect((9, 27, 10, 29), fore if rolled else cuff)
        return (22, 26)
    if arm == "hip":
        f.poly([(17, 23), (22, 24), (25, 29), (21, 32), (19, 30), (21, 28)], sleeve)
        f.line([(21, 32), (25, 29)], shade)
        f.rect((19, 30, 20, 33), skin)
        return (19, 31)
    if arm == "shrug":
        f.poly([(17, 23), (22, 25), (26, 24), (26, 27), (21, 29), (17, 28)], sleeve)
        f.rect((26, 23, 27, 27), fore if rolled else cuff)
        f.line([(28, 24), (30, 23)], skin); f.line([(28, 25), (30, 25)], skin)
        f.rect((3, 25, 7, 28), shade); f.rect((1, 24, 2, 26), skin)
        return (30, 23)
    if arm == "whisper":
        # a hand cupped beside the mouth: the documentary aside
        f.poly([(17, 23), (21, 24), (25, 19), (23, 17)], sleeve)
        f.line([(17, 23), (23, 18)], shade)
        f.rect((23, 14, 25, 17), skin); f.px((26, 14), skin); f.px((26, 15), skin)
        return (25, 15)
    raise ValueError(arm)


# --- whole figures ----------------------------------------------------------------------

UPPER_DY = {"stand": 0, "walk1": 0, "walk2": 1, "crouch": 8, "sit": 3, "kneel": 5}


@lru_cache(maxsize=4096)
def _figure(who, key):
    pose = dict(key)
    outfit = pose["outfit"] or ("field" if who == "david" else "suit")
    body = pose["body"]
    if body == "lie":
        img, a = _figure(who, pose_key(**{**pose, "body": "stand", "arm": "down", "mic": False}))
        return _lying(img, a)
    lower = Fig()
    legs(lower, who, outfit, body)
    dy = UPPER_DY[body]
    if body == "crouch":
        pose = {**pose, "lean": pose["lean"] - 2}
    upper = Fig(OX + pose["lean"], OY + pose["bob"] + dy)
    torso(upper, who, outfit)
    (head_david if who == "david" else head_morgan)(upper, pose)
    face(upper, who, pose)
    hat(upper, who, pose["hat"])
    style = pose["mic"] if isinstance(pose["mic"], str) else "hand"
    if pose["mic"] and pose["arm"] not in ("mic", "cross", "whisper"):
        mic_hand(upper, who, outfit, style)
    hand = near_arm(upper, who, outfit, pose["arm"], style)
    img = lower.img
    if body == "crouch":                    # the knees come up in front of the torso
        img = upper.img
        img.alpha_composite(lower.img)
    else:
        img.alpha_composite(upper.img)
    img = outlined(img)
    ox, oy = OX + pose["lean"], OY + pose["bob"] + dy
    fx0, fy0, fx1, fy1 = FACE
    anchors = dict(
        feet=FEET,
        head=((fx0 + fx1) / 2 + ox, (fy0 + fy1) / 2 + oy),
        mouth=(MOUTH[0] + 2 + ox, MOUTH[1] + 1 + oy),
        eye=(EYE[0] + ox, EYE[1] + oy),
        hand=(hand[0] + ox, hand[1] + oy),
        mic=(27.5 + ox, 18 + oy),
        top=(16 + ox, 2 + oy),
    )
    return img, anchors


def _lying(img, a):
    """Face down on the ground, head to the right: the stand sprite turned a quarter."""
    rot = img.rotate(-90, resample=Image.NEAREST, expand=True)       # head now points right
    w, h = img.size
    # a point (x, y) maps to (h - 1 - y, x) after a -90 degree turn with expand
    m = {k: (h - 1 - y, x) for k, (x, y) in a.items()}
    bbox = rot.getbbox()
    rot = rot.crop((0, 0, rot.width, bbox[3]))
    fx, fy = m["feet"]
    m["feet"] = (fx, bbox[3] - 1)
    return rot, m


def pose_key(**pose):
    p = dict(DEFAULT)
    p.update(pose)
    return tuple(sorted(p.items()))


def figure(who, facing=1, rim=0.0, rim_color=(255, 214, 160), **pose):
    """(RGBA sprite, anchors) for a character; facing -1 mirrors it. `rim` lights the facing edge."""
    img, a = _figure(who, pose_key(**pose))
    if rim:
        img = rim_light(img, 1, rim_color, amount=rim)
    if facing < 0:
        img = mirror(img)
        a = {k: (img.width - 1 - x, y) for k, (x, y) in a.items()}
    return img, a


def mouth_for(loud, rest="closed"):
    """A mouth shape from vocal loudness in [0, 1]."""
    return "wide" if loud > 0.8 else "open" if loud > 0.5 else "o" if loud > 0.22 else rest


if __name__ == "__main__":
    from engine import ROOT
    rows = [
        ("david", [dict(), dict(mouth="grin", arm="palm"), dict(body="crouch", arm="palm", mouth="open"),
                   dict(body="crouch", arm="whisper", mouth="o", eyes="side"), dict(arm="point", mouth="smirk", brows="up"),
                   dict(mic=True, arm="fist", mouth="wide", brows="angry"), dict(arm="cross", mouth="frown", brows="worried"),
                   dict(hat="pith", arm="hold"), dict(outfit="prison", arm="down", mouth="frown", eyes="half"),
                   dict(body="kneel", arm="down", eyes="shut", mouth="smile"), dict(body="walk1"), dict(body="lie")]),
        ("morgan", [dict(), dict(eyes="half", mouth="smirk", arm="palm"), dict(outfit="god", arm="up", mouth="smile"),
                    dict(outfit="prison", arm="cross", eyes="half"), dict(mic=True, arm="point", mouth="open"),
                    dict(outfit="chauffeur", hat="chauffeur", arm="hold"), dict(outfit="president", arm="palm", mouth="open"),
                    dict(outfit="tux", arm="down", mouth="smile"), dict(outfit="lucius", glasses=True, arm="hip"),
                    dict(outfit="madiba", arm="fist", mouth="grin"), dict(body="sit", arm="palm"),
                    dict(arm="shrug", eyes="wide", mouth="o", brows="worried")]),
    ]
    sheet = Image.new("RGB", (12 * 42 + 4, 2 * 58 + 4), (96, 120, 110))
    for j, (who, poses) in enumerate(rows):
        for i, p in enumerate(poses):
            img, a = figure(who, facing=1, **p)
            sheet.paste(img, (4 + i * 42, 4 + j * 58 + (56 - img.height)), img)
    out = ROOT / "build" / "cast.png"
    out.parent.mkdir(exist_ok=True)
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)
    print(out)
