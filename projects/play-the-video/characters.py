"""Caricatures of Hasan Piker ("hasan") and Asmongold ("asmon"), big enough to hold the frame alone.

The heads are three-quarter views facing right on a 60x60 canvas:

    hasan   the square jaw under dark stubble, heavy black brows, the hair cropped at the sides and
            swept up on top, and a wide white grin
    asmon   the long thin face, the centre parting with the hairline in retreat, hair past the shoulders,
            the full beard, tired eyes, the headphones, and not all of his teeth

Expressions are named parts:

    eyes    open squint half wide blink shut side up down
    brows   neutral angry up worried skeptic
    mouth   closed smile open wide o smirk grin frown grit

The bodies are pixelart.figure's layered rig at one and a half times its size: Hasan in the tank top (or
the Mao suit), Asmongold in the black T-shirt. `figure(who, ...)` returns the sprite and its anchors. The
man in the other one's window is not a second, smaller drawing: it is his own webcam frame, shrunk
(stream.preview_pic).

Gestures are pixelart.figure's, plus two of this video's own (in the 84x96 rig's pixels, like the rest):

    window  the far hand points up and out of frame, at the window in the corner
    click   the near hand is on the mouse
"""
from functools import lru_cache

from PIL import Image

from engine import C, INK, Canvas, col, mirror  # noqa: F401
from pixelart.figure import GESTURES, Body, Rig

HW, HH = 60, 60
FACE = {
    # eye centres (near, far) and the mouth centre. Facing right in three-quarter view: the ear is on the
    # left, then the near eye, the bridge of the nose, and the narrower far eye against the contour.
    "hasan": dict(skin=("hskin", "hskin_sh", "hskin_dk", "hskin_hi"), eyes=((28, 32), (43, 32)), mouth=(40, 50),
                  lip="lip_h", iris="iris_h", brow="hhair", brow_w=3, eye_h=5, tooth="tooth", gaps=()),
    "asmon": dict(skin=("askin", "askin_sh", "askin_dk", "askin_hi"), eyes=((28, 32), (42, 32)), mouth=(40, 49),
                  lip="lip_a", iris="iris_a", brow="ahair_dk", brow_w=2, eye_h=4, tooth="tooth_y", gaps=(-3, 1)),
}


# --- the heads ------------------------------------------------------------------------------

def head_hasan(f):
    skin, sh, dk, hi = FACE["hasan"]["skin"]
    f.poly([(16, 18), (42, 15), (47, 21), (49, 30), (52, 37), (53, 42), (51, 44), (51, 49), (50, 53), (46, 58),
            (30, 59), (21, 55), (15, 48), (12, 36), (12, 24)], skin)
    f.poly([(12, 24), (16, 18), (20, 20), (18, 34), (20, 46), (24, 55), (21, 55), (15, 48), (12, 36)], sh)   # side plane
    f.ell((7, 29, 16, 43), skin)                                         # the ear
    f.line([(10, 32), (10, 40)], sh); f.pxs([(12, 33), (12, 39), (11, 36)], dk)
    f.line([(22, 39), (27, 41)], hi)                                     # the cheekbone
    # the nose: a strong one
    f.poly([(39, 28), (42, 34), (51, 38), (54, 42), (52, 44), (42, 44), (39, 42)], skin)
    f.line([(41, 31), (49, 37)], hi); f.line([(42, 44), (51, 44)], sh)
    f.pxs([(50, 43), (49, 43)], dk); f.line([(39, 30), (39, 40)], sh)
    # the stubble: along the jaw from the sideburn, over the lip and across the chin
    f.poly([(13, 32), (15, 45), (20, 53), (29, 58), (38, 59), (46, 58), (50, 53), (51, 46), (48, 46), (46, 52),
            (38, 55), (30, 53), (24, 47), (20, 39), (18, 31)], "hstub")
    f.poly([(33, 46), (37, 45), (50, 45), (51, 48), (35, 48)], "hstub")
    f.poly([(33, 54), (46, 53), (47, 57), (34, 58)], "hstub")
    f.pxs([(16, 40), (18, 46), (22, 52), (27, 55), (33, 57), (40, 57), (45, 55), (48, 51), (20, 44), (25, 51),
           (37, 46), (43, 46), (47, 47), (36, 56), (42, 55)], "hstub_dk")
    # the hair: faded at the sides, swept up and back on top
    f.poly([(11, 30), (8, 22), (8, 13), (12, 6), (19, 2), (29, 0), (39, 1), (46, 4), (50, 9), (50, 14), (47, 19),
            (42, 15), (34, 16), (25, 17), (20, 20), (17, 26), (16, 31)], "hhair")
    f.poly([(11, 30), (8, 22), (9, 15), (14, 17), (17, 26), (16, 31)], "hfade")
    f.line([(42, 15), (34, 16), (25, 17), (20, 20)], "hhair_sh")         # the hairline
    f.line([(13, 9), (20, 5), (30, 3), (38, 4)], "hhair_hi")
    f.line([(17, 12), (25, 9), (35, 8), (44, 9), (48, 12)], "hhair_hi")
    f.line([(22, 14), (31, 12), (40, 12)], "hhair_sh")
    f.pxs([(46, 6), (41, 3), (26, 2)], "hhair_hi")


def head_asmon(f):
    skin, sh, dk, hi = FACE["asmon"]["skin"]
    # the hair down the back, and the far side's behind the jaw
    f.poly([(12, 9), (6, 18), (3, 32), (3, 59), (22, 59), (20, 46), (16, 30), (16, 16)], "ahair_sh")
    f.poly([(49, 44), (53, 48), (55, 59), (45, 59), (48, 54), (50, 49)], "ahair_sh")
    # the face, long and narrow, under a high dome
    f.poly([(15, 16), (20, 9), (30, 5), (40, 6), (46, 12), (48, 21), (48, 30), (51, 37), (52, 42), (50, 44), (50, 49),
            (48, 54), (43, 59), (33, 59), (25, 56), (19, 50), (15, 42), (13, 32), (13, 23)], skin)
    f.poly([(13, 23), (15, 16), (19, 17), (18, 33), (20, 45), (24, 54), (19, 50), (15, 42), (13, 32)], sh)   # side plane
    f.line([(22, 41), (29, 46)], sh); f.line([(23, 42), (28, 45)], sh)   # the hollow of the cheek
    f.line([(23, 38), (27, 39)], hi)
    f.line([(26, 21), (36, 20)], sh)                                     # a line across the forehead
    # the nose: long and thin
    f.poly([(39, 28), (41, 34), (50, 38), (53, 42), (51, 44), (42, 44), (39, 42)], skin)
    f.line([(41, 31), (48, 37)], hi); f.line([(42, 44), (50, 44)], sh)
    f.pxs([(49, 43)], dk); f.line([(39, 30), (39, 40)], sh)
    # the beard: up to the sideburn, over the lip, and down past the chin
    f.poly([(14, 33), (15, 44), (19, 52), (25, 57), (33, 59), (43, 59), (48, 55), (50, 50), (50, 45), (33, 45),
            (30, 50), (25, 48), (21, 41), (19, 33)], "abeard")
    f.poly([(32, 45), (37, 43), (50, 44), (51, 47), (34, 48)], "abeard")
    f.pxs([(17, 40), (19, 47), (23, 53), (29, 57), (36, 58), (43, 57), (47, 53), (28, 51), (34, 54), (41, 55),
           (46, 49), (22, 46)], "abeard_sh")
    f.pxs([(26, 54), (38, 57), (45, 52), (20, 43)], "ahair")
    # the hair: thin on top, the hairline in retreat either side of the peak, falling straight past the jaw
    f.poly([(11, 22), (11, 13), (16, 6), (24, 2), (34, 1), (42, 3), (47, 8), (50, 15), (50, 30), (48, 29), (48, 20),
            (46, 13), (42, 9), (38, 11), (34, 15), (29, 10), (24, 9), (20, 13), (18, 19), (17, 26)], "ahair")
    f.poly([(11, 14), (8, 26), (7, 40), (7, 59), (17, 59), (16, 48), (15, 38), (15, 27), (18, 19), (16, 12)], "ahair")
    f.line([(33, 14), (32, 8), (31, 2)], "ahair_sh")                     # the parting
    f.line([(13, 16), (10, 28), (9, 44), (9, 58)], "ahair_hi")           # strands
    f.line([(15, 22), (12, 36), (12, 56)], "ahair_sh")
    f.line([(21, 6), (15, 13)], "ahair_hi"); f.line([(40, 5), (46, 10), (49, 18)], "ahair_hi")
    f.line([(26, 4), (22, 9)], "ahair_sh"); f.line([(37, 4), (41, 8)], "ahair_sh")
    f.pxs([(32, 5), (32, 10), (27, 6), (36, 7), (24, 6), (30, 8), (35, 11)], skin)   # the scalp showing through
    # the headphones: the band over the top, the cup on the ear
    f.line([(11, 29), (11, 17), (15, 9), (22, 3), (30, 1)], "phones", w=3)
    f.line([(13, 16), (16, 10), (22, 5)], "phones_hi")
    f.ell((3, 25, 18, 46), "phones")
    f.ell((6, 28, 15, 43), "grey_sh")
    f.ell((8, 31, 13, 40), "phones")
    f.pxs([(7, 31), (8, 30)], "grey_hi")


HEAD = {"hasan": head_hasan, "asmon": head_asmon}


# --- the faces ------------------------------------------------------------------------------

def eyes_draw(f, who, eyes):
    F = FACE[who]
    skin, sh, dk, _ = F["skin"]
    for n, (cx, cy) in enumerate(F["eyes"]):
        far = n == 1
        x0, x1 = (cx - 2, cx + 2) if far else (cx - 4, cx + 3)           # the far eye is foreshortened
        hh = F["eye_h"]
        y0 = cy - 2
        y1 = y0 + hh - 1
        iw = 2 if far else 3
        if eyes in ("blink", "shut"):
            if eyes == "blink":
                f.line([(x0, cy + 1), (x1, cy + 1)], "eye")
                f.px((x0 - 1, cy), "eye")
            else:                                                        # beaming, or smug: closed in an arc
                f.line([(x0 + 1, cy), (x1 - 1, cy)], "eye")
                f.pxs([(x0, cy + 1), (x1, cy + 1), (x0 - 1, cy + 2)], "eye")
            continue
        if eyes == "squint":
            f.line([(x0, cy), (x1, cy)], "eye_w")
            ix = cx - (0 if far else 1)
            f.line([(ix, cy), (ix + iw - 1, cy)], "eye")
            f.line([(x0 - 1, cy - 1), (x1, cy - 1)], "eye")
            f.line([(x0, cy + 1), (x1, cy + 1)], dk)
            continue
        top, bot = y0, y1
        if eyes == "wide":
            top, bot = y0 - 1, y1 + 1
        elif eyes in ("half", "down"):
            top = y1 - 1 - (hh > 4)
        f.rect((x0, top, x1, bot), "eye_w")
        if bot - top >= 3:                                               # round the corners
            f.pxs([(x0, top), (x1, top), (x0, bot), (x1, bot)], skin)
        # the iris
        ix = {"side": x1 - iw + 1}.get(eyes, cx - (0 if far else 1))
        if eyes == "wide":                                               # a small one, in all that white
            f.rect((ix, cy - 1, ix + iw - 2 + far, cy + 1), F["iris"])
            f.px((ix + (not far), cy), "eye")
        elif eyes == "up":
            f.rect((ix, top, ix + iw - 1, top + 2), F["iris"])
            f.px((ix + (not far), top + 1), "eye")
        else:
            f.rect((ix, top, ix + iw - 1, bot - (bot - top >= 4)), F["iris"])
            f.rect((ix + (not far), top + (bot - top >= 2), ix + (not far), min(bot, top + 2)), "eye")
            if bot - top >= 3:
                f.px((ix, top + 1), "eye_w")
        # the lids
        f.line([(x0 - 1, top - 1), (x1, top - 1)], "eye")
        f.px((x0 - 1, top), "eye")
        if eyes in ("half", "down"):                                     # the lid, lowered
            f.rect((x0, y0, x1, top - 2), skin)
            f.line([(x0, y0 - 1), (x1 - 1, y0 - 1)], dk)
        f.line([(x0 + 1, bot + 1), (x1 - 1, bot + 1)], sh)
        if who == "asmon":                                               # the bags under them
            f.line([(x0 + 2, bot + 3), (x1 - 1, bot + 3)], sh)


def brows_draw(f, who, brows):
    F = FACE[who]
    w = F["brow_w"]
    for n, (cx, cy) in enumerate(F["eyes"]):
        far = n == 1                                                     # the far brow sits across the nose
        a, b = (cx - 3, cx + 3) if far else (cx - 5, cx + 5)
        y = cy - 7
        inner, outer = (a, b) if far else (b, a)                         # the end nearest the nose first
        kind = brows
        if brows == "skeptic":                                           # one up, one down
            kind = "angry" if far else "up"
        if kind == "angry":                                              # the inner ends pulled down
            pts = [(inner, y + 3), (outer, y)]
        elif kind == "worried":                                          # the inner ends pushed up
            pts = [(inner, y - 1), (outer, y + 2)]
        elif kind == "up":
            pts = [(inner, y - 3), (outer, y - 2)]
        else:
            pts = [(inner, y + 1), (outer, y)]
        for i in range(w):
            f.line([(x, yy + i) for x, yy in pts], F["brow"])


def teeth(f, who, box):
    """A row of teeth in a box; Asmongold's has gaps."""
    F = FACE[who]
    x0, y0, x1, y1 = box
    f.rect(box, F["tooth"])
    mx = F["mouth"][0]
    for g in F["gaps"]:
        if x0 <= mx + g <= x1 - 1:
            f.rect((mx + g, y0, mx + g + 1, y1), "mouth")


def mouth_draw(f, who, mouth):
    F = FACE[who]
    skin, sh, dk, hi = F["skin"]
    lip = F["lip"]
    mx, my = F["mouth"]
    if mouth == "closed":
        f.line([(mx - 5, my), (mx + 4, my)], "mouth")
        f.line([(mx - 3, my + 2), (mx + 2, my + 2)], lip)
    elif mouth == "smile":                                               # lips together, corners up
        f.line([(mx - 5, my), (mx + 4, my)], "mouth")
        f.pxs([(mx - 6, my - 1), (mx + 5, my - 1), (mx - 7, my - 2)], "mouth")
        f.line([(mx - 3, my + 2), (mx + 2, my + 2)], lip)
    elif mouth == "open":
        f.rect((mx - 5, my - 2, mx + 4, my + 3), "mouth")
        teeth(f, who, (mx - 4, my - 2, mx + 3, my - 1))
        f.line([(mx - 3, my + 3), (mx + 2, my + 3)], "tongue")
        f.line([(mx - 4, my + 4), (mx + 3, my + 4)], lip)
    elif mouth == "wide":
        f.ell((mx - 7, my - 4, mx + 5, my + 7), "mouth")
        teeth(f, who, (mx - 4, my - 3, mx + 2, my - 2))
        f.line([(mx - 3, my + 5), (mx + 1, my + 5)], "tongue"); f.line([(mx - 2, my + 6), (mx, my + 6)], "tongue")
    elif mouth == "o":
        f.ell((mx - 4, my - 3, mx + 4, my + 5), lip)
        f.ell((mx - 2, my - 1, mx + 2, my + 3), "mouth")
    elif mouth == "smirk":                                               # one corner up
        f.line([(mx - 5, my + 1), (mx, my + 1)], "mouth")
        f.line([(mx, my + 1), (mx + 5, my - 2)], "mouth")
        f.pxs([(mx + 6, my - 3), (mx + 6, my - 4)], sh if who == "hasan" else "abeard_sh")
        f.line([(mx - 3, my + 3), (mx + 1, my + 3)], lip)
    elif mouth == "grin":
        f.poly([(mx - 8, my - 3), (mx + 6, my - 3), (mx + 5, my + 2), (mx + 1, my + 5), (mx - 4, my + 5),
                (mx - 7, my + 2)], "mouth")
        teeth(f, who, (mx - 7, my - 3, mx + 5, my - 1))
        teeth(f, who, (mx - 5, my + 2, mx + 3, my + 3))
        f.pxs([(mx - 5, my + 3), (mx + 3, my + 3)], "mouth")
    elif mouth == "frown":
        f.line([(mx - 5, my + 2), (mx - 3, my)], "mouth"); f.line([(mx - 3, my), (mx + 2, my)], "mouth")
        f.line([(mx + 2, my), (mx + 4, my + 2)], "mouth")
        f.line([(mx - 2, my + 2), (mx + 1, my + 2)], lip)
    elif mouth == "grit":
        f.rect((mx - 7, my - 3, mx + 5, my + 3), "mouth")
        teeth(f, who, (mx - 6, my - 2, mx + 4, my + 2))
        f.line([(mx - 6, my), (mx + 4, my)], "ink")
        for x in range(mx - 4, mx + 4, 3):
            f.line([(x, my - 2), (x, my + 2)], "grey")


@lru_cache(maxsize=None)
def head(who, eyes="open", brows="neutral", mouth="closed", flush=0):
    """A head sprite facing right (60x60, outlined); mirror it to face left."""
    f = Canvas(HW, HH)
    HEAD[who](f)
    eyes_draw(f, who, eyes)
    brows_draw(f, who, brows)
    mouth_draw(f, who, mouth)
    if flush:                                                            # red cheeks
        cx, cy = FACE[who]["eyes"][0]
        f.pxs([(cx - 3, cy + 8), (cx - 1, cy + 8), (cx + 1, cy + 8), (cx + 3, cy + 8), (cx - 2, cy + 9), (cx, cy + 9),
               (cx + 2, cy + 9), (cx - 1, cy + 10), (cx + 1, cy + 10)], "flush")
    return f.done()


# --- the bodies -----------------------------------------------------------------------------

HEM = 143


def tank_top(f):
    """Hasan in a white tank top: the neck, the shoulders, the chest and the chain."""
    skin, sh, dk, hi = FACE["hasan"]["skin"]
    f.poly([(22, 82), (31, 72), (48, 63), (72, 62), (89, 68), (97, 76), (99, 90), (94, 108), (91, HEM), (29, HEM),
            (27, 108), (21, 94)], skin)                                                                  # the trunk
    f.poly([(49, 52), (72, 52), (75, 66), (61, 73), (47, 66)], sh)                                       # the neck
    f.line([(47, 66), (34, 71)], sh); f.line([(75, 65), (88, 69)], sh)                                   # the traps
    f.poly([(42, 68), (48, 66), (51, 77), (56, 85), (62, 87), (68, 85), (73, 77), (75, 65), (81, 67), (84, 81),
            (91, 98), (91, HEM), (29, HEM), (29, 100), (35, 85), (39, 75)], "tank")
    f.poly([(81, 67), (84, 81), (91, 98), (91, HEM), (86, HEM), (86, 102), (81, 85), (78, 72)], "tank_sh")
    f.line([(42, 68), (39, 75), (35, 85), (29, 100)], "tank_sh")
    f.line([(36, 102), (47, 107), (59, 104)], "tank_sh"); f.line([(63, 104), (74, 107), (85, 101)], "tank_sh")   # the chest
    f.line([(61, 90), (61, 104)], "tank_sh")
    f.line([(48, 79), (53, 86)], hi); f.line([(70, 86), (74, 79)], sh)
    for i, (x, y) in enumerate(((51, 67), (52, 70), (54, 73), (56, 76), (59, 78), (62, 78), (65, 76), (68, 73),
                                (70, 70), (71, 67))):                                                    # the chain
        f.px((x, y), "gold" if i % 2 else "gold_sh")
    f.rect((60, 79, 61, 81), "gold")


def mao_suit(f):
    """The Mao suit: a turn-down collar buttoned to the neck, four pockets with flaps."""
    skin, sh, dk, hi = FACE["hasan"]["skin"]
    f.poly([(52, 54), (70, 54), (71, 62), (61, 66), (51, 62)], sh)
    f.poly([(30, 72), (46, 63), (74, 62), (88, 70), (92, 84), (91, 100), (90, HEM), (26, HEM), (25, 100), (24, 84)], "mao")
    f.poly([(88, 70), (92, 84), (91, 100), (90, HEM), (85, HEM), (85, 100), (84, 84), (81, 72)], "mao_sh")
    f.poly([(46, 63), (60, 68), (55, 74), (45, 69)], "mao_hi"); f.poly([(74, 62), (61, 68), (66, 74), (76, 68)], "mao_hi")
    f.line([(46, 63), (60, 68), (74, 62)], "mao_sh")
    f.line([(60, 69), (60, HEM)], "mao_sh")
    for y in (78, 92, 106, 120, 134):
        f.rect((59, y, 61, y + 2), "gold_sh"); f.px((60, y + 1), "gold")
    for x in (34, 68):                                                                                   # the pockets
        f.rect((x, 82, x + 18, 96), "mao_hi"); f.line([(x, 82), (x + 18, 82)], "mao_sh")
        f.poly([(x, 83), (x + 18, 83), (x + 9, 88)], "mao"); f.px((x + 9, 86), "gold_sh")
        f.rect((x - 1, 114, x + 19, 132), "mao_hi"); f.line([(x - 1, 114), (x + 19, 114)], "mao_sh")
        f.poly([(x - 1, 115), (x + 19, 115), (x + 9, 121)], "mao"); f.px((x + 9, 119), "gold_sh")


def black_tee(f):
    """Asmongold's black T-shirt, and the hair that hangs over it."""
    skin, sh, dk, hi = FACE["asmon"]["skin"]
    f.poly([(53, 54), (67, 54), (68, 66), (60, 70), (52, 66)], sh)                                       # the neck
    f.poly([(36, 74), (50, 65), (70, 65), (80, 70), (86, 80), (87, 94), (86, HEM), (31, HEM), (30, 94), (31, 82)], "tee")
    f.poly([(80, 70), (86, 80), (87, 94), (86, HEM), (82, HEM), (82, 96), (80, 82), (76, 72)], "tee_sh")
    f.line([(50, 66), (55, 71), (61, 73), (66, 71), (70, 66)], "tee_hi")                                 # the collar
    f.poly([(51, 65), (69, 65), (65, 70), (61, 72), (56, 70)], sh)
    f.line([(37, 76), (48, 68)], "tee_hi")
    f.rect((42, 92, 47, 95), "red"); f.px((43, 93), "red_hi")                                            # the logo
    # the hair, over the near shoulder and behind the far one
    f.poly([(33, 60), (45, 60), (49, 70), (51, 84), (49, 98), (45, 106), (42, 98), (39, 84), (35, 72)], "ahair")
    f.line([(40, 62), (44, 76), (46, 92), (45, 102)], "ahair_sh"); f.line([(36, 62), (40, 76), (43, 92)], "ahair_hi")
    f.poly([(72, 60), (80, 62), (83, 74), (84, 90), (82, 100), (79, 92), (77, 78), (74, 68)], "ahair_sh")
    f.line([(77, 64), (80, 78), (81, 92)], "ahair_dk")


def _head(who):
    return lambda **expr: head(who, **expr)


def _body(name, who, torso, sleeve, **kw):
    F = FACE[who]
    return Body(name, torso, _head(who), F["skin"][:2], sleeve, hand=6, eye=F["eyes"][0], mouth=F["mouth"], **kw)


BODIES = {
    "hasan": _body("hasan", "hasan", tank_top, "hskin", sleeve_w=14, forearm_w=10, shoulders=((28, 79), (93, 77))),
    "hasan_mao": _body("hasan_mao", "hasan", mao_suit, "mao", sleeve_w=12, forearm_w=10, shoulders=((29, 77), (90, 75))),
    "asmon": _body("asmon", "asmon", black_tee, "tee", forearm="askin", sleeve_w=8, shoulders=((35, 79), (83, 77))),
}
MOVES = {
    **GESTURES,
    "window": (GESTURES["desk"][0], ((70, 50), (82, 35), "point"), "back"),
    "click":  (((13, 66), (24, 75), "edge"), GESTURES["desk"][1], "front"),
}
# The canvas is wider than the body on the side he faces, so a pointing arm fits.
RIG = Rig(Canvas, size=(140, 144), neck=(60, 63), chin=(33, 55), head_size=(HW, HH), gestures=MOVES, scale=1.5)
FW, FH = RIG.size


def figure(who, arms="desk", lean=0, bob=0, facing=1, held=None, outfit=None, **expr):
    """A figure (RGBA, 140x144) and its anchors; `outfit` picks a variant body ("mao" for Hasan)."""
    body = BODIES[f"{who}_{outfit}" if outfit else who]
    return RIG.figure(body, arms, lean, bob, facing, held, **expr)


if __name__ == "__main__":
    from engine import ROOT, scaled
    faces = [("open", "neutral", "closed"), ("open", "neutral", "smile"), ("open", "up", "grin"),
             ("squint", "angry", "open"), ("wide", "worried", "o"), ("half", "skeptic", "smirk"),
             ("side", "angry", "frown"), ("shut", "up", "wide"), ("blink", "neutral", "grit"),
             ("up", "up", "closed"), ("down", "worried", "frown")]
    poses = ("desk", "point", "shrug", "cross", "palm", "chin", "hair", "fist", "finger", "chop", "bro", "facepalm",
             "pinch", "thumb", "clasp", "up2")
    sheet = Image.new("RGB", (len(faces) * 64 + 4, 2 * 64 + 4 + 4 * 148), (86, 90, 110))
    for r, who in enumerate(HEAD):
        for i, (eyes, brows, mouth) in enumerate(faces):
            h = head(who, eyes, brows, mouth)
            sheet.paste(h, (4 + i * 64, 4 + r * 64), h)
    for r, who in enumerate(HEAD):
        for i, arms in enumerate(poses):
            spr, _ = figure(who, arms, facing=1 if who == "hasan" else -1, mouth="grin" if i % 3 == 0 else "open",
                            outfit="mao" if who == "hasan" and i >= 13 else None)
            sheet.paste(spr, (4 + (i % 8) * 86 - 14, 132 + (r * 2 + i // 8) * 148), spr)
    out = ROOT / "build" / "characters.png"
    out.parent.mkdir(exist_ok=True)
    scaled(sheet, 3).save(out)
    print(out)
