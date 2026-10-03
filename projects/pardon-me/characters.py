"""Procedural chibi sprites of Donald Trump ("trump") and Benjamin Netanyahu ("bibi").

Each figure is drawn facing right on a 48x84 canvas with its feet at (24, 81),
then outlined in ink; `figure()` mirrors it to face left. The heads are big
(about 24 px) because most shots see them from the chest up, behind the
rostrum or a delegation desk. Poses are small dicts of named parts, cached per
combination:

    body    stand walk1 walk2                                    (the legs)
    mouth   closed open wide o smirk frown grit smile grin pout
    eyes    open blink shut wide side x half squint
    brows   neutral angry up worried
    arm     down point up fist palm hold pinch chop shrug thumb wave cross
    far     down out up hold                                     (the far arm, mostly hidden)
    hat     none cap crown visor mortar
    outfit  suit golf
    flush 0-2;   lean, bob: upper body shifts in pixels

Anchors come back in canvas pixels: feet, head (centre), mouth, eye, hand
(near hand), far (far hand), top (top of the hair), chest, nose.
"""
from functools import lru_cache

from PIL import Image

from engine import Canvas, mirror, outlined, rim_light

CW, CH = 48, 84
OX, OY = 6, 2                 # offset of the design grid (a 36x80 figure) inside the canvas
FEET = (24, 81)
EYE, MOUTH = (22, 12), (22, 20)

DEFAULT = dict(body="stand", mouth="closed", eyes="open", brows="neutral", arm="down", far="down", hat="none",
               outfit="suit", flush=0, lean=0, bob=0)

# per character: skin, skin shade, skin light; suit, shade, light; tie, tie shade
SKIN = {"trump": ("tskin", "tskin_sh", "tskin_hi"), "bibi": ("bskin", "bskin_sh", "bskin_hi")}
SUIT = {"trump": ("suit", "suit_sh", "suit_hi"), "bibi": ("bsuit", "bsuit_sh", "bsuit_hi")}
TIE = {"trump": ("tie", "tie_sh", "tie_hi"), "bibi": ("btie", "btie_sh", "btie_hi")}


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


def sleeve_cols(who, outfit):
    if outfit == "golf":
        return ("shirt", "shirt_sh", "shirt")
    return SUIT[who]


# --- legs --------------------------------------------------------------------------------

def legs(f, who, outfit, body):
    cloth, shade, _ = SUIT[who] if outfit != "golf" else ("khaki", "khaki_sh", None)
    if outfit == "golf":
        cloth, shade = (214, 196, 150), (170, 150, 104)
    a, b = {"stand": (0, 0), "walk1": (-3, 3), "walk2": (3, -3)}.get(body, (0, 0))
    f.poly([(8, 54), (17, 54), (16 + a, 75), (10 + a, 75)], cloth)
    f.poly([(18, 54), (27, 54), (26 + b, 75), (20 + b, 75)], cloth)
    f.line([(17, 56), (17, 74)], shade)
    f.line([(9, 56), (10 + a, 74)], shade)
    f.rect((8 + a, 75, 17 + a, 77), "shoe")
    f.rect((19 + b, 75, 28 + b, 77), "shoe")
    f.line([(13 + a, 75), (16 + a, 75)], "shoe_hi")
    f.line([(24 + b, 75), (27 + b, 75)], "shoe_hi")


# --- torsos ------------------------------------------------------------------------------

def torso(f, who, outfit):
    cloth, shade, light = sleeve_cols(who, outfit)
    tie, tie_sh, tie_hi = TIE[who]
    big = who == "trump"
    x0, x1 = (3, 31) if big else (5, 29)
    f.poly([(x0 + 3, 29), (x1 - 3, 29), (x1, 33), (x1 + (1 if big else 0), 55), (x0 - (1 if big else 0), 55),
            (x0, 33)], cloth)
    f.poly([(x0 + 3, 29), (x0 + 8, 29), (x0 + 5, 55), (x0 - (1 if big else 0), 55), (x0, 33)], shade)   # far side
    if outfit == "golf":
        f.poly([(14, 29), (22, 29), (18, 35)], "shirt_sh")
        f.rect((17, 29, 19, 37), "shirt_sh")
        f.pxs([(18, 32), (18, 35)], "steel_sh")
        f.line([(x0, 52), (x1, 52)], (170, 150, 104))
        return
    f.poly([(14, 29), (23, 29), (18, 40)], "shirt")                                 # shirt in the V
    f.line([(14, 29), (18, 40)], light)
    f.line([(23, 29), (18, 40)], shade)                                              # lapels
    if big:                                                                          # the long red tie, past the belt
        f.poly([(17, 30), (20, 30), (21, 54), (19, 57), (16, 54)], tie)
        f.line([(19, 32), (20, 52)], tie_hi)
        f.line([(16, 34), (17, 53)], tie_sh)
        f.rect((17, 29, 20, 31), tie_sh)
        f.px((24, 34), "red"); f.px((25, 34), "white"); f.px((24, 35), "blue")       # flag pin
    else:
        f.poly([(17, 30), (20, 30), (20, 43), (18, 45), (16, 43)], tie)
        f.line([(19, 32), (19, 42)], tie_hi)
        f.rect((17, 29, 20, 31), tie_sh)
        f.px((24, 34), "white"); f.px((25, 34), "blue"); f.px((24, 35), "blue")      # flag pin
    f.pxs([(23, 45), (23, 50)], shade)                                               # buttons
    f.line([(x0 + 1, 54), (x1 - 1, 54)], shade)


# --- heads -------------------------------------------------------------------------------

def head_trump(f, pose):
    skin, sh, hi = SKIN["trump"]
    f.ell((9, 5, 28, 27), skin)                                                      # face
    f.ell((11, 14, 28, 29), skin)                                                    # jowls
    f.ell((9, 10, 14, 24), sh)                                                       # the shaded side
    f.ell((11, 12, 15, 19), skin); f.pxs([(12, 14), (12, 15), (13, 16)], sh)          # ear
    f.line([(14, 27), (24, 28)], sh)                                                 # the chin under the chin
    f.line([(25, 18), (24, 22)], sh)                                                 # cheek fold
    f.rect((19, 10, 26, 14), "tring")                                                # the goggle tan
    f.px((19, 14), skin); f.px((26, 14), skin)
    f.poly([(27, 11), (30, 15), (30, 17), (27, 17)], skin)                           # nose
    f.px((28, 17), sh)
    # the hair: a swept helmet, the back combed down, the front lock riding out over the brow
    f.ell((4, 0, 26, 14), "thair")
    f.ell((3, 4, 14, 21), "thair_sh")
    f.ell((5, 4, 14, 19), "thair")
    f.poly([(14, 0), (24, 0), (31, 4), (31, 7), (27, 8), (24, 7), (19, 9), (15, 6)], "thair")
    f.line([(25, 5), (30, 6)], "thair_sh")
    f.line([(17, 7), (24, 6)], "thair_sh")
    f.line([(8, 2), (20, 0)], "thair_hi"); f.line([(21, 1), (28, 3)], "thair_hi")
    f.pxs([(6, 8), (7, 12), (6, 15)], "thair_sh")
    f.line([(9, 6), (13, 4)], "thair_hi")


def head_bibi(f, pose):
    skin, sh, hi = SKIN["bibi"]
    # the hair goes down first as a close cap; the face is laid over it, which leaves the high,
    # receding hairline
    f.ell((5, 1, 25, 21), "bhair_sh")
    f.ell((6, 1, 25, 19), "bhair")
    f.ell((10, 5, 29, 28), skin)                                                     # broad face
    f.poly([(19, 2), (25, 4), (27, 9), (17, 9), (15, 6)], skin)                      # the forehead, up into the hair
    f.ell((11, 15, 28, 29), skin)                                                    # jowls
    f.ell((10, 11, 14, 24), sh)
    f.ell((11, 12, 15, 19), skin); f.pxs([(12, 14), (12, 15), (13, 16)], sh)          # ear
    f.rect((10, 9, 12, 12), "bhair"); f.px((13, 10), "bhair")                         # over the ear
    f.line([(14, 27), (23, 28)], sh)
    f.line([(25, 17), (24, 22)], sh)                                                 # the long cheek fold
    f.line([(16, 22), (18, 25)], sh)                                                 # jowl
    f.poly([(27, 9), (31, 15), (31, 18), (27, 18)], skin)                            # the nose
    f.px((28, 18), sh); f.px((30, 18), sh)
    f.line([(19, 5), (24, 6)], hi)                                                   # forehead shine
    f.line([(9, 3), (17, 2)], "bhair_hi")                                            # combed straight back
    f.line([(8, 6), (14, 5)], "bhair_sh")
    f.pxs([(7, 10), (6, 13), (8, 16)], "bhair_sh")


HEAD = {"trump": head_trump, "bibi": head_bibi}


def face(f, who, pose):
    ex, ey = EYE
    mx, my = MOUTH
    eyes, brows, mouth = pose["eyes"], pose["brows"], pose["mouth"]
    skin, sh, hi = SKIN[who]
    if pose["flush"]:
        f.pxs([(ex + 1, ey + 4), (ex + 2, ey + 4), (ex + 3, ey + 4)] +
              ([(ex, ey + 5), (ex + 3, ey + 5), (ex + 2, ey + 5)] if pose["flush"] >= 2 else []), "flush")
    # eyes (Trump squints by default; Bibi has heavy lids)
    if eyes == "open":
        f.rect((ex, ey, ex, ey + 1), "eye")
        f.line([(ex - 1, ey - 1), (ex + 1, ey - 1)], sh)
    elif eyes == "squint":
        f.line([(ex - 1, ey + 1), (ex + 1, ey + 1)], "eye")
    elif eyes == "half":
        f.px((ex, ey + 1), "eye"); f.line([(ex - 1, ey), (ex + 1, ey)], sh)
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
    # brows: Trump's pale and barely there, Bibi's dark and heavy
    bc = "thair_sh" if who == "trump" else "bbrow"
    by = ey - 2
    thick = who == "bibi"
    if brows == "neutral":
        f.line([(ex - 2, by), (ex + 2, by)], bc)
        if thick:
            f.line([(ex - 1, by - 1), (ex + 2, by - 1)], bc)
    elif brows == "angry":
        f.line([(ex - 2, by - 1), (ex + 2, by + 1)], bc)
        if thick:
            f.line([(ex - 2, by - 2), (ex + 2, by)], bc)
    elif brows == "up":
        f.line([(ex - 2, by - 1), (ex + 2, by - 2)], bc)
        if thick:
            f.line([(ex - 1, by - 2), (ex + 2, by - 3)], bc)
    elif brows == "worried":
        f.line([(ex - 2, by + 1), (ex + 2, by - 1)], bc)
        if thick:
            f.line([(ex - 2, by), (ex + 2, by - 2)], bc)
    # mouths
    if mouth == "closed":
        f.line([(mx, my + 1), (mx + 4, my + 1)], "mouth")
    elif mouth == "open":
        f.rect((mx, my, mx + 4, my + 3), "mouth"); f.line([(mx, my), (mx + 4, my)], "tooth")
    elif mouth == "wide":
        f.rect((mx - 1, my - 1, mx + 4, my + 4), "mouth"); f.line([(mx - 1, my - 1), (mx + 4, my - 1)], "tooth")
        f.line([(mx, my + 4), (mx + 3, my + 4)], "tongue")
    elif mouth == "o":
        f.rect((mx + 1, my, mx + 3, my + 3), "mouth")
    elif mouth == "pout":                                    # the famous pursed lips
        f.rect((mx + 1, my, mx + 4, my + 2), sh)
        f.rect((mx + 2, my + 1, mx + 3, my + 1), "mouth")
    elif mouth == "smirk":
        f.pxs([(mx, my + 1), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my + 1), (mx + 4, my)], "mouth")
    elif mouth == "frown":
        f.pxs([(mx, my + 2), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my + 1), (mx + 4, my + 2)], "mouth")
    elif mouth == "grit":
        f.rect((mx, my, mx + 4, my + 2), "tooth"); f.line([(mx, my + 1), (mx + 4, my + 1)], "ink")
    elif mouth == "smile":
        f.pxs([(mx, my), (mx + 1, my + 1), (mx + 2, my + 1), (mx + 3, my + 1), (mx + 4, my)], "mouth")
    elif mouth == "grin":
        f.rect((mx, my, mx + 4, my + 1), "tooth"); f.pxs([(mx - 1, my - 1), (mx + 5, my - 1)], "mouth")
        f.line([(mx, my + 2), (mx + 4, my + 2)], "mouth")


def hat(f, who, kind):
    if kind == "none":
        return
    if kind == "cap":                                       # a plain red ball cap
        f.ell((5, -1, 26, 10), "red"); f.rect((5, 6, 26, 8), "red")
        f.poly([(24, 6), (33, 7), (33, 9), (24, 9)], "red_sh")
        f.line([(9, 1), (20, 0)], "red_hi")
    elif kind == "visor":                                   # golf visor
        f.rect((6, 4, 26, 7), "white"); f.poly([(24, 6), (33, 7), (33, 9), (24, 8)], "white")
        f.line([(6, 7), (26, 7)], "shirt_sh")
    elif kind == "crown":
        f.rect((8, -1, 25, 4), "gold"); f.line([(8, 4), (25, 4)], "gold_sh")
        for x in (8, 13, 18, 23, 25):
            f.rect((x, -4, x, -1), "gold")
        f.pxs([(12, 1), (21, 1)], "blue"); f.px((16, 1), "red")
    elif kind == "mortar":                                  # pop quiz: a graduation cap
        f.rect((7, 1, 25, 4), "black")
        f.poly([(3, 0), (16, -4), (30, 0), (16, 3)], "black")
        f.line([(16, -1), (26, 3)], "gold"); f.rect((26, 3, 26, 7), "gold")


# --- arms ----------------------------------------------------------------------------------

def far_arm(f, who, outfit, far):
    """The far arm, drawn behind the torso. Returns the far hand (design grid) or None when hidden."""
    cloth, shade, light = sleeve_cols(who, outfit)
    skin = SKIN[who][0]
    cuff = "shirt"
    if far == "down":
        return None
    if far == "out":                                         # the other hand out, palm up (shrug, accordion)
        f.poly([(6, 31), (10, 31), (4, 41), (1, 39)], shade)
        f.rect((0, 39, 2, 41), cuff)
        f.rect((-3, 38, 0, 41), skin)
        return (-2, 39)
    if far == "up":
        f.poly([(7, 31), (11, 31), (6, 18), (3, 19)], shade)
        f.rect((3, 15, 6, 17), cuff)
        f.rect((3, 11, 6, 15), skin)
        return (4, 12)
    if far == "hold":                                        # both hands on whatever is held in front
        f.poly([(8, 31), (12, 31), (22, 38), (20, 41)], shade)
        f.rect((22, 37, 23, 41), cuff)
        f.rect((24, 37, 26, 40), skin)
        return (25, 38)
    raise ValueError(far)


def near_arm(f, who, outfit, arm):
    """The near arm, drawn over the torso; returns the hand position in design-grid coordinates."""
    cloth, shade, light = sleeve_cols(who, outfit)
    skin, skin_sh, _ = SKIN[who]
    cuff = "shirt"
    small = who == "trump"                    # small hands, a matter of record
    if arm == "down":
        f.poly([(18, 32), (24, 32), (25, 49), (19, 49)], cloth)
        f.line([(18, 33), (19, 49)], shade)
        f.line([(17, 34), (18, 48)], "ink")
        f.line([(24, 33), (25, 47)], light)
        f.rect((19, 49, 25, 50), cuff)
        f.rect((20, 51, 23 if small else 24, 53), skin)
        return (22, 52)
    if arm == "point":
        f.poly([(18, 32), (24, 32), (32, 37), (31, 41), (19, 41)], cloth)
        f.line([(19, 41), (31, 41)], shade)
        f.rect((32, 37, 33, 41), cuff)
        f.rect((34, 38, 36, 40), skin)
        f.line([(37, 38), (39 if small else 40, 38)], skin)
        return (39, 38)
    if arm == "palm":
        f.poly([(18, 32), (24, 32), (31, 37), (30, 41), (19, 41)], cloth)
        f.line([(19, 41), (30, 41)], shade)
        f.rect((31, 37, 32, 41), cuff)
        f.rect((33, 36, 35, 40), skin)
        f.px((36, 36), skin); f.px((36, 38), skin)
        return (34, 37)
    if arm in ("up", "fist", "wave"):
        f.poly([(18, 32), (24, 32), (34, 35), (32, 40), (20, 38)], cloth)            # upper arm, out to the elbow
        f.line([(20, 38), (32, 40)], shade)
        f.poly([(31, 36), (35, 35), (36, 22), (32, 22)], cloth)                      # forearm, straight up
        f.line([(32, 23), (31, 36)], shade)
        f.rect((31, 20, 36, 22), cuff)
        if arm == "fist":
            f.rect((31, 15, 36, 19), skin); f.line([(32, 16), (32, 19)], skin_sh)
            return (33, 16)
        if arm == "up":                                     # one finger raised: "let me be clear"
            f.rect((32, 16, 35, 19), skin); f.rect((34, 11, 34, 15), skin)
            return (34, 12)
        f.rect((31, 14, 36, 19), skin); f.pxs([(37, 15), (30, 15)], skin)
        return (33, 14)
    if arm == "pinch":                                      # thumb to finger, the precise point
        f.poly([(18, 32), (24, 32), (31, 37), (28, 41), (20, 38)], cloth)
        f.line([(20, 38), (28, 41)], shade)
        f.poly([(28, 37), (32, 36), (35, 29), (32, 28)], cloth)
        f.rect((32, 26, 35, 28), cuff)
        f.rect((32, 21, 36, 25), skin)
        f.px((34, 23), "ink")
        return (34, 22)
    if arm == "hold":
        f.poly([(18, 32), (24, 32), (28, 40), (25, 43), (19, 42)], cloth)
        f.line([(19, 42), (25, 43)], shade)
        f.rect((27, 39, 29, 43), cuff)
        f.rect((30, 39, 32, 42), skin)
        return (31, 40)
    if arm == "chop":
        f.poly([(18, 32), (24, 32), (30, 42), (27, 45), (19, 40)], cloth)
        f.line([(19, 40), (27, 45)], shade)
        f.rect((29, 42, 31, 45), cuff)
        f.line([(32, 45), (35, 48)], skin); f.line([(32, 46), (34, 48)], skin)
        return (34, 47)
    if arm == "shrug":
        f.poly([(18, 32), (24, 32), (31, 36), (30, 40), (20, 39)], cloth)
        f.rect((31, 35, 32, 39), cuff)
        f.line([(33, 36), (36, 35)], skin); f.line([(33, 37), (36, 37)], skin); f.line([(33, 38), (35, 38)], skin)
        return (35, 36)
    if arm == "thumb":
        f.poly([(18, 32), (24, 32), (30, 37), (28, 41), (19, 41)], cloth)
        f.line([(19, 41), (28, 41)], shade)
        f.rect((29, 35, 31, 39), cuff)
        f.rect((32, 35, 35, 39), skin); f.rect((33, 31, 34, 34), skin)
        f.px((34, 37), skin_sh)
        return (33, 32)
    if arm == "cross":
        f.rect((8, 37, 27, 43), cloth)
        f.line([(8, 43), (27, 43)], shade)
        f.line([(14, 37), (20, 43)], shade)
        f.rect((24, 37, 25, 40), cuff); f.rect((26, 37, 28, 40), skin)
        f.rect((8, 40, 9, 43), cuff)
        return (27, 38)
    raise ValueError(arm)


# --- whole figures -------------------------------------------------------------------------

@lru_cache(maxsize=4096)
def _figure(who, key):
    pose = dict(key)
    outfit = pose["outfit"]
    lower = Fig()
    legs(lower, who, outfit, pose["body"])
    ox, oy = OX + pose["lean"], OY + pose["bob"]
    upper = Fig(ox, oy)
    far = far_arm(upper, who, outfit, pose["far"])
    torso(upper, who, outfit)
    HEAD[who](upper, pose)
    face(upper, who, pose)
    hat(upper, who, pose["hat"])
    hand = near_arm(upper, who, outfit, pose["arm"])
    img = lower.img
    img.alpha_composite(upper.img)
    img = outlined(img)
    anchors = dict(
        feet=FEET,
        head=(18 + ox, 14 + oy),
        mouth=(MOUTH[0] + 2 + ox, MOUTH[1] + 1 + oy),
        eye=(EYE[0] + ox, EYE[1] + oy),
        nose=(30 + ox, 15 + oy),
        hand=(hand[0] + ox, hand[1] + oy),
        far=((far[0] + ox, far[1] + oy) if far else (8 + ox, 50 + oy)),
        top=(16 + ox, oy),
        chest=(18 + ox, 38 + oy),
    )
    return img, anchors


def pose_key(**pose):
    p = dict(DEFAULT)
    p.update(pose)
    return tuple(sorted(p.items()))


def figure(who, facing=1, rim=0.0, rim_color=(255, 230, 170), **pose):
    """(RGBA sprite, anchors) for a character; facing -1 mirrors it. `rim` lights the facing edge."""
    img, a = _figure(who, pose_key(**pose))
    if rim:
        img = rim_light(img, 1, rim_color, amount=rim)
    if facing < 0:
        img = mirror(img)
        a = {k: (img.width - 1 - x, y) for k, (x, y) in a.items()}
    return img, a


def mouth_for(loud, rest="closed", who=None):
    """A mouth shape from vocal loudness in [0, 1] (Trump purses his lips on the quiet syllables)."""
    if loud > 0.8:
        return "wide"
    if loud > 0.5:
        return "open"
    if loud > 0.22:
        return "pout" if who == "trump" else "o"
    return rest


if __name__ == "__main__":
    from engine import ROOT
    rows = [
        ("trump", [dict(), dict(mouth="pout", arm="point"), dict(mouth="wide", arm="pinch", brows="angry"),
                   dict(arm="up", mouth="open"), dict(arm="shrug", far="out", mouth="o", brows="up"),
                   dict(arm="thumb", mouth="grin", eyes="squint"), dict(arm="fist", mouth="grit", brows="angry"),
                   dict(arm="cross", mouth="frown", eyes="half"), dict(arm="hold", far="hold", mouth="smirk"),
                   dict(eyes="wide", mouth="o", brows="worried", flush=2), dict(hat="cap", outfit="golf", arm="wave"),
                   dict(body="walk1", hat="crown")]),
        ("bibi", [dict(), dict(arm="up", mouth="open", brows="angry"), dict(arm="point", mouth="smirk"),
                  dict(arm="palm", mouth="o"), dict(arm="hold", far="hold", mouth="closed", brows="up"),
                  dict(arm="chop", mouth="wide", brows="angry"), dict(arm="cross", mouth="frown", eyes="half"),
                  dict(arm="shrug", far="out", eyes="side", mouth="smirk"),
                  dict(eyes="wide", brows="worried", mouth="o"),
                  dict(arm="fist", mouth="grin"), dict(hat="mortar", arm="up"), dict(body="walk2")]),
    ]
    sheet = Image.new("RGB", (12 * 50 + 4, 2 * 86 + 4), (196, 150, 70))
    for j, (who, poses) in enumerate(rows):
        for i, p in enumerate(poses):
            img, a = figure(who, facing=1, **p)
            sheet.paste(img, (4 + i * 50, 4 + j * 86), img)
    out = ROOT / "build" / "cast.png"
    out.parent.mkdir(exist_ok=True)
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print(out)
