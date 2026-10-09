"""Portraits of Emiru ("emiru") and Maya Higa ("maya"), big enough to hold the frame alone.

The heads are turned a little to the right on a 60x60 canvas, both eyes in full view:

    emiru   long, very dark brown hair with a blunt fringe and a lock down each cheek, big eyes under
            winged liner and pink shadow, blush, glossy lips, and the pink headset with the cat's ears
    maya    long brown hair parted in the middle, falling in waves and sun-bleached at the ends, warm
            brown eyes, and the wide smile

Expressions are named parts, drawn here in a softer style than the men of the other videos get:

    eyes    open squint half wide blink shut side up down
    brows   neutral angry up worried skeptic
    mouth   closed smile open wide o smirk grin frown grit

The bodies are pixelart.figure's layered rig at one and a half times its size: Emiru in a pink crop top
and a choker, her midriff bare; Maya in the sanctuary's green T-shirt (and, as "glove", with the
falconer's glove on her far hand). `figure(who, ...)` returns the sprite and its anchors.

Gestures are pixelart.figure's, plus two of this video's own (in the 84x96 rig's pixels, like the rest):

    window  the far hand points up and out of frame, at the window in the corner
    click   the near hand is on the mouse
"""
from functools import lru_cache

from PIL import Image

from engine import C, INK, Canvas, col, mirror  # noqa: F401
from pixelart.figure import GESTURES, Body, Rig

HW, HH = 60, 60
WOMEN = ("emiru", "maya")
FACE = {
    # eyes: their centres (near, far); eye_hw: half their widths; eye_rows: rows of eye above and below the
    # centre; mouth: its centre, and mouth_w half its width at rest. `shadow` is eyeshadow on the lid.
    "emiru": dict(skin=("eskin", "eskin_sh", "eskin_dk", "eskin_hi"), eyes=((28, 37), (44, 37)), eye_hw=(4, 3),
                  eye_rows=(3, 2), iris=("iris_e", "iris_e_dk", "iris_e_hi"), brow="ebrow", brow_gap=5,
                  mouth=(38, 51), mouth_w=3, lip=("lip_e", "lip_e_hi"), blush="eblush", shadow="eshadow",
                  wing=2, lower_lash=True),
    "maya": dict(skin=("mskin", "mskin_sh", "mskin_dk", "mskin_hi"), eyes=((28, 36), (44, 36)), eye_hw=(4, 3),
                 eye_rows=(2, 2), iris=("iris_m", "iris_m_dk", "iris_m_hi"), brow="mbrow", brow_gap=3, brow_w=2,
                 mouth=(38, 51), mouth_w=4, lip=("lip_m", "lip_m_hi"), blush="mblush", wing=1),
}


# --- the heads ------------------------------------------------------------------------------

def head_emiru(f):
    skin, sh, dk, hi = FACE["emiru"]["skin"]
    # the hair down her back, either side of the neck
    f.poly([(12, 12), (5, 22), (3, 34), (2, 48), (2, 59), (26, 59), (23, 50), (20, 40), (18, 24)], "ehair_sh")
    f.poly([(50, 24), (56, 34), (57, 46), (58, 59), (45, 59), (48, 52), (51, 44)], "ehair_sh")
    # the face: full cheeks coming down to a small chin
    f.poly([(17, 24), (47, 24), (51, 30), (52, 38), (51, 44), (48, 50), (43, 56), (39, 58), (35, 58), (29, 55),
            (23, 49), (19, 43), (17, 33)], skin)
    f.line([(20, 45), (24, 51), (29, 55), (34, 58)], sh)                                                # along the jaw
    f.pxs([(20, 44), (22, 44), (24, 44), (26, 44), (21, 45), (23, 45), (25, 45), (22, 46), (24, 46)], "eblush")
    f.pxs([(46, 44), (48, 44), (50, 44), (47, 45), (49, 45), (48, 46)], "eblush")
    f.px((40, 46), sh); f.px((41, 47), sh); f.px((40, 45), hi)                                          # the nose
    # the hair: a blunt fringe to the lashes, a lock down each cheek
    f.poly([(9, 36), (6, 26), (8, 16), (14, 9), (24, 5), (38, 5), (48, 9), (54, 16), (56, 26), (56, 36), (55, 46),
            (52, 51), (51, 40), (51, 29), (49, 28), (47, 30), (45, 28), (42, 30), (39, 28), (36, 30), (33, 28),
            (30, 30), (27, 28), (24, 30), (21, 28), (20, 40), (19, 48), (17, 54), (13, 52), (10, 44)], "ehair")
    f.line([(15, 21), (22, 17), (31, 15), (41, 16), (48, 20)], "ehair_hi")                              # the shine
    f.line([(19, 23), (26, 20), (33, 19), (42, 20), (45, 22)], "ehair_hi")
    for x in (24, 30, 36, 42, 48):                                                                      # the fringe's strands
        f.line([(x, 23), (x, 27)], "ehair_sh")
    f.line([(14, 34), (14, 44), (15, 50)], "ehair_hi"); f.line([(54, 32), (54, 44)], "ehair_hi")
    # the headset: a band over the top with a cat's ears on it, and a cup on each ear
    f.poly([(12, 14), (14, 0), (25, 8)], "ears"); f.poly([(15, 11), (16, 4), (22, 8)], "ears_hi")
    f.poly([(37, 8), (48, 0), (50, 14)], "ears"); f.poly([(41, 8), (47, 3), (48, 11)], "ears_hi")
    f.line([(10, 31), (10, 23), (12, 16), (17, 11), (25, 8), (37, 8), (45, 11), (50, 16), (52, 23), (52, 30)], "ears", w=2)
    f.line([(13, 16), (18, 11), (25, 8)], "ears_hi")
    f.ell((2, 29, 16, 48), "ears")
    f.ell((5, 32, 13, 45), "ears_hi")
    f.ell((7, 35, 11, 42), "ears_sh")
    f.ell((51, 30, 58, 46), "ears")
    f.ell((54, 33, 57, 43), "ears_sh")


def head_maya(f):
    skin, sh, dk, hi = FACE["maya"]["skin"]
    # the hair behind her, either side of the neck
    f.poly([(14, 10), (6, 22), (4, 36), (5, 48), (3, 59), (26, 59), (23, 50), (20, 40), (18, 22)], "mhair_sh")
    f.poly([(50, 20), (56, 32), (56, 44), (58, 59), (45, 59), (48, 52), (51, 44)], "mhair_sh")
    # the face: an oval, the forehead clear
    f.poly([(18, 22), (29, 17), (43, 17), (49, 21), (51, 28), (52, 37), (51, 44), (48, 50), (43, 56), (39, 58),
            (35, 58), (29, 55), (23, 49), (19, 43), (17, 32)], skin)
    f.line([(20, 45), (24, 51), (29, 55), (34, 58)], sh)                                                # along the jaw
    f.pxs([(21, 43), (23, 43), (25, 43), (22, 44), (24, 44), (26, 44)], "mblush")
    f.pxs([(47, 43), (49, 43), (48, 44), (50, 44)], "mblush")
    f.px((40, 45), sh); f.px((41, 46), sh); f.px((40, 44), hi)                                          # the nose
    # the hair: from the parting, down past the cheek in waves, and across the far temple
    f.poly([(37, 5), (28, 3), (19, 6), (12, 13), (8, 24), (6, 36), (8, 46), (5, 54), (6, 59), (24, 59), (21, 52),
            (23, 45), (19, 37), (20, 29), (24, 23), (31, 19), (37, 17)], "mhair")
    f.poly([(37, 5), (44, 5), (51, 10), (55, 18), (57, 30), (56, 40), (58, 50), (57, 59), (49, 59), (51, 52), (52, 44),
            (53, 36), (52, 28), (50, 23), (45, 19), (37, 17)], "mhair")
    f.line([(37, 5), (37, 17)], "mhair_dk")                                                             # the parting
    f.line([(32, 6), (23, 10), (16, 17), (12, 28), (10, 38), (12, 46), (9, 56)], "mhair_hi")
    f.line([(28, 10), (21, 16), (17, 25), (15, 36), (17, 45), (14, 55)], "mhair_sh")
    f.line([(33, 11), (26, 15), (22, 21)], "mhair_hi")
    f.line([(41, 7), (48, 12), (53, 20), (55, 30), (54, 40), (56, 50)], "mhair_hi")
    f.line([(41, 11), (47, 15), (51, 22)], "mhair_sh")
    f.line([(7, 50), (8, 58)], "mhair_lt"); f.line([(12, 51), (11, 58)], "mhair_lt")                    # the ends, sun-bleached
    f.line([(18, 53), (19, 58)], "mhair_lt"); f.line([(55, 52), (55, 58)], "mhair_lt")
    f.line([(51, 54), (52, 58)], "mhair_lt")


HEAD = {"emiru": head_emiru, "maya": head_maya}


# --- the faces ------------------------------------------------------------------------------

def eyes_draw(f, F, eyes):
    skin, sh, dk, hi = F["skin"]
    iris, iris_dk, iris_hi = F["iris"]
    up, lo = F["eye_rows"]
    for n, (cx, cy) in enumerate(F["eyes"]):
        hw = F["eye_hw"][n]
        x0, x1 = cx - hw, cx + hw
        out = -1 if n == 0 else 1                                        # which way the outer corner lies
        xo = x0 if n == 0 else x1
        if eyes == "shut":                                               # laughing: an arch of lash
            f.pxs([(x0, cy + 1), (x0 + 1, cy), (x1 - 1, cy), (x1, cy + 1)] + [(x, cy - 1) for x in range(x0 + 2, x1 - 1)],
                  "eye")
            f.px((xo + out, cy + 2), "eye")
            continue
        if eyes == "blink":                                              # closed: the lashes on the cheek
            f.pxs([(x0, cy), (x0 + 1, cy + 1), (x1 - 1, cy + 1), (x1, cy)] + [(x, cy + 2) for x in range(x0 + 2, x1 - 1)],
                  "eye")
            f.px((xo + out, cy - 1), "eye")
            if F.get("shadow"):
                f.line([(x0 + 1, cy - 1), (x1 - 1, cy - 1)], F["shadow"]); f.line([(x0 + 2, cy), (x1 - 2, cy)], F["shadow"])
            continue
        top, bot = cy - up, cy + lo
        lid = top                                                        # where the lash line would sit, open
        if eyes == "wide":
            top -= 1
        elif eyes in ("half", "down"):
            top += 2
        elif eyes == "squint":
            top, bot = top + 1, bot - 1
        f.rect((x0 + 1, top, x1 - 1, bot), "eye_w")
        # the iris: dark under the lash, lighter towards the bottom, a point of light in it
        iw = 5 if n == 0 else 4
        ix = x0 + 2 if n == 0 else x0 + 1
        it, ib = top, bot
        if eyes == "side":
            ix += 1
        elif eyes == "up":
            ib -= 1
        elif eyes == "down":
            it += 1
        elif eyes == "wide":
            it, ib, iw, ix = top + 1, bot - 1, iw - 1, ix + (n == 0)
        ix = min(ix, x1 - iw)
        f.rect((ix, it, ix + iw - 1, ib), iris)
        f.line([(ix, it), (ix + iw - 1, it)], iris_dk)
        if ib - it >= 3:
            f.line([(ix + 1, ib), (ix + iw - 2, ib)], iris_hi)
        px = ix + iw // 2 - (n == 1)
        f.rect((px, min(it + 1, ib), px + (n == 0), max(min(ib - 1, it + 2), min(it + 1, ib))), "eye")   # the pupil
        if ib - it >= 2:
            f.px((ix, it + 1), "eye_w")
            if n == 0 and ib - it >= 3:
                f.px((ix + iw - 1, ib - 1), iris_hi)
        # the lids: a dark upper lash that wings out, a soft lower one
        f.line([(x0, top - 1), (x1, top - 1)], "eye")
        f.px((x0, top), "eye"); f.px((x1, top), "eye")
        for k in range(1, F.get("wing", 1) + 1):
            f.px((xo + out * k, top - 1 - k), "eye")
        if F.get("wing", 1) > 1:
            f.px((xo + out, top - 1), "eye")
        if top > lid:                                                    # the lid, lowered: its crease above
            f.line([(x0 + 1, lid - 1), (x1 - 1, lid - 1)], F.get("shadow", sh))
        elif F.get("shadow"):                                            # eyeshadow, over the lash
            f.line([(x0 + 1, top - 2), (x1 - 1, top - 2)], F["shadow"])
            f.px((xo, top - 2), F["shadow"])
        f.line([(x0 + 2, bot + 1), (x1 - 2, bot + 1)], sh)
        if F.get("lower_lash"):
            f.px((xo, bot), "eye"); f.px((xo, bot - 1), "eye")


def brows_draw(f, F, brows):
    up, _ = F["eye_rows"]
    for n, (cx, cy) in enumerate(F["eyes"]):
        hw = F["eye_hw"][n]
        inner, outer = (cx + hw, cx - hw - 1) if n == 0 else (cx - hw, cx + hw + 1)    # the end by the nose first
        y = cy - up - F["brow_gap"]
        kind = brows
        if brows == "skeptic":                                           # one up, one down
            kind = "up" if n == 0 else "angry"
        if kind == "angry":                                              # the inner ends pulled down
            yi, ym, yo = y + 2, y, y - 1
        elif kind == "worried":                                          # the inner ends pushed up
            yi, ym, yo = y - 2, y - 1, y + 1
        elif kind == "up":
            yi, ym, yo = y - 2, y - 3, y - 1
        else:                                                            # an easy arch
            yi, ym, yo = y, y - 1, y + 1
        mid = (inner + outer) // 2
        f.line([(inner, yi), (mid, ym), (outer, yo)], F["brow"])
        if F.get("brow_w", 1) > 1:
            f.line([(inner, yi + 1), (mid, ym + 1)], F["brow"])


def mouth_draw(f, F, mouth):
    skin, sh, dk, hi = F["skin"]
    lip, lip_hi = F["lip"]
    mx, my = F["mouth"]
    w = F["mouth_w"]
    if mouth in ("closed", "smile", "smirk", "frown"):
        f.line([(mx - w + 1, my - 1), (mx - 1, my - 1)], lip); f.line([(mx + 1, my - 1), (mx + w - 1, my - 1)], lip)
        f.line([(mx - w, my), (mx + w, my)], "mouth")
        f.line([(mx - w + 1, my + 1), (mx + w - 1, my + 1)], lip)
        f.line([(mx - w + 2, my + 2), (mx + w - 2, my + 2)], lip)
        f.px((mx - 1, my + 1), lip_hi)
        if mouth == "smile":                                             # the corners up
            f.pxs([(mx - w - 1, my - 1), (mx + w + 1, my - 1)], "mouth")
        elif mouth == "smirk":                                           # one corner up
            f.pxs([(mx + w + 1, my - 1), (mx + w + 2, my - 2)], "mouth")
        elif mouth == "frown":
            f.pxs([(mx - w - 1, my + 1), (mx + w + 1, my + 1)], "mouth")
    elif mouth == "open":                                                # mid-word
        f.line([(mx - w + 1, my - 2), (mx + w - 1, my - 2)], lip)
        f.rect((mx - w, my - 1, mx + w, my + 2), "mouth")
        f.line([(mx - w + 1, my - 1), (mx + w - 1, my - 1)], "tooth")
        f.line([(mx - w + 2, my + 2), (mx + w - 2, my + 2)], "tongue")
        f.line([(mx - w + 1, my + 3), (mx + w - 1, my + 3)], lip)
        f.px((mx - 1, my + 3), lip_hi)
        f.pxs([(mx - w, my + 2), (mx + w, my + 2)], lip)
    elif mouth == "wide":                                                # a held note
        f.line([(mx - w + 1, my - 3), (mx + w - 1, my - 3)], lip)
        f.rect((mx - w, my - 2, mx + w, my + 3), "mouth")
        f.line([(mx - w + 1, my - 2), (mx + w - 1, my - 2)], "tooth")
        f.rect((mx - w + 2, my + 2, mx + w - 2, my + 3), "tongue")
        f.line([(mx - w + 1, my + 4), (mx + w - 1, my + 4)], lip)
        f.px((mx - 1, my + 4), lip_hi)
        f.pxs([(mx - w, my + 3), (mx + w, my + 3), (mx - w, my - 2), (mx + w, my - 2)], lip)
    elif mouth == "o":
        f.ell((mx - 3, my - 2, mx + 3, my + 3), lip)
        f.rect((mx - 1, my - 1, mx + 1, my + 2), "mouth")
        f.px((mx - 2, my + 2), lip_hi)
    elif mouth == "grin":                                                # the smile, teeth and all
        f.line([(mx - w, my - 2), (mx + w, my - 2)], lip)
        f.poly([(mx - w - 2, my - 1), (mx + w + 2, my - 1), (mx + w, my + 2), (mx - w, my + 2)], "mouth")
        f.rect((mx - w - 1, my - 1, mx + w + 1, my), "tooth")
        f.line([(mx - w + 1, my + 1), (mx + w - 1, my + 1)], "tooth")
        f.pxs([(mx - w - 3, my - 2), (mx + w + 3, my - 2)], "mouth")
        f.line([(mx - w + 1, my + 3), (mx + w - 1, my + 3)], lip)
        f.px((mx - 1, my + 3), lip_hi)
    elif mouth == "grit":
        f.rect((mx - w - 1, my - 1, mx + w + 1, my + 2), "mouth")
        f.rect((mx - w, my - 1, mx + w, my + 2), "tooth")
        f.line([(mx - w, my + 1), (mx + w, my + 1)], "grey_hi")
        f.line([(mx - w, my - 2), (mx + w, my - 2)], lip); f.line([(mx - w, my + 3), (mx + w, my + 3)], lip)


@lru_cache(maxsize=None)
def head(who, eyes="open", brows="neutral", mouth="closed", flush=0):
    """A head sprite facing right (60x60, outlined); mirror it to face left."""
    F = FACE[who]
    f = Canvas(HW, HH)
    HEAD[who](f)
    eyes_draw(f, F, eyes)
    brows_draw(f, F, brows)
    mouth_draw(f, F, mouth)
    if flush:                                                            # red cheeks
        cx, cy = F["eyes"][0]
        f.rect((cx - 6, cy + 6, cx + 1, cy + 8), "flush"); f.rect((F["eyes"][1][0] + 1, cy + 6, F["eyes"][1][0] + 5, cy + 8), "flush")
    return f.done()


# --- the bodies -----------------------------------------------------------------------------

HEM = 143


def crop_top(f):
    """Emiru: a pink crop top, a black choker, the midriff bare over a black skirt."""
    skin, sh, dk, hi = FACE["emiru"]["skin"]
    f.poly([(70, 60), (82, 60), (86, 76), (87, 98), (84, 114), (80, 104), (78, 86), (74, 72)], "ehair_sh")   # the hair behind
    f.poly([(55, 56), (66, 56), (66, 68), (72, 72), (81, 76), (85, 83), (84, 92), (80, 99), (76, 108), (75, 116),
            (77, 128), (80, HEM), (40, HEM), (43, 128), (45, 116), (44, 108), (40, 99), (36, 92), (35, 83), (39, 76),
            (48, 72), (55, 68)], skin)
    f.poly([(55, 60), (66, 60), (66, 66), (60, 69), (55, 66)], sh)                                       # under the chin
    f.line([(55, 67), (60, 69), (66, 66)], "black", w=2)                                                 # the choker
    f.px((60, 71), "ears")
    f.poly([(43, 79), (48, 73), (54, 71), (56, 77), (60, 80), (64, 77), (66, 71), (72, 73), (78, 79), (83, 86),
            (83, 93), (80, 99), (79, 101), (60, 103), (41, 101), (40, 99), (37, 93), (37, 86)], "knit")
    f.line([(54, 72), (56, 78), (60, 81), (64, 78), (66, 72)], "knit_hi")                                # the neckline
    f.line([(44, 93), (50, 96), (57, 94)], "knit_sh"); f.line([(63, 94), (70, 96), (76, 93)], "knit_sh")
    f.line([(41, 100), (60, 102), (79, 100)], "knit_hi"); f.line([(41, 101), (60, 103), (79, 101)], "knit_sh")
    f.line([(80, 82), (82, 88), (82, 93), (79, 99)], "knit_sh")
    f.pxs([(49, 87), (51, 87), (48, 88), (49, 88), (50, 88), (51, 88), (52, 88), (49, 89), (50, 89), (51, 89), (50, 90)],
          "white")                                                                                       # a heart
    f.line([(43, 103), (45, 110), (46, 116)], sh); f.line([(77, 103), (75, 110), (74, 116)], sh)         # the waist
    f.rect((60, 106, 60, 108), dk); f.px((61, 106), sh); f.px((59, 108), sh)                             # the navel
    f.line([(60, 110), (60, 113)], hi)
    f.poly([(45, 118), (75, 118), (77, 128), (80, HEM), (40, HEM), (43, 128)], "black")                  # the skirt
    f.line([(46, 119), (74, 119)], "grey_sh")
    f.poly([(27, 60), (44, 60), (46, 74), (45, 92), (43, 108), (39, 117), (34, 107), (31, 90), (28, 75)], "ehair")
    f.line([(37, 62), (40, 78), (41, 96), (39, 110)], "ehair_sh"); f.line([(32, 62), (35, 78), (37, 96)], "ehair_hi")


def green_tee(f):
    """Maya: the sanctuary's green T-shirt, fitted, a leaf on the chest, and the hair that hangs over it."""
    skin, sh, dk, hi = FACE["maya"]["skin"]
    f.poly([(70, 60), (83, 60), (87, 74), (86, 88), (88, 100), (84, 110), (80, 98), (78, 84), (74, 70)], "mhair_sh")
    f.poly([(55, 56), (66, 56), (66, 70), (60, 76), (55, 70)], skin)                                     # the neck
    f.poly([(55, 60), (66, 60), (66, 66), (60, 69), (55, 66)], sh)
    f.poly([(48, 72), (55, 68), (60, 75), (66, 68), (72, 72), (81, 76), (86, 84), (85, 93), (80, 99), (76, 108),
            (75, 116), (77, 128), (80, HEM), (40, HEM), (43, 128), (45, 116), (44, 108), (40, 99), (35, 93), (34, 84),
            (39, 76)], "olive")
    f.poly([(81, 76), (86, 84), (85, 93), (80, 99), (76, 108), (75, 116), (77, 128), (80, HEM), (74, HEM), (72, 126),
            (71, 112), (75, 100), (79, 90)], "olive_sh")
    f.line([(54, 69), (60, 76), (67, 69)], "olive_hi")                                                   # the collar
    f.line([(44, 95), (50, 98), (57, 96)], "olive_sh"); f.line([(63, 96), (69, 98), (74, 95)], "olive_sh")
    f.line([(40, 78), (48, 73)], "olive_hi")
    f.pxs([(67, 85), (68, 85), (66, 86), (67, 86), (68, 86), (69, 86), (66, 87), (67, 87), (68, 87), (67, 88), (66, 89)],
          "white")                                                                                       # the leaf
    f.poly([(27, 60), (45, 60), (48, 72), (46, 84), (49, 96), (45, 110), (40, 104), (37, 92), (32, 82), (29, 72)], "mhair")
    f.line([(37, 62), (41, 76), (40, 88), (43, 100)], "mhair_sh"); f.line([(31, 62), (35, 76), (36, 88)], "mhair_hi")
    f.line([(44, 92), (47, 97), (44, 108)], "mhair_lt"); f.line([(41, 96), (42, 104)], "mhair_lt")


def _head(who):
    return lambda **expr: head(who, **expr)


def _body(name, who, torso, sleeve, **kw):
    F = FACE[who]
    return Body(name, torso, _head(who), F["skin"][:2], sleeve, hand=6, eye=F["eyes"][0], mouth=F["mouth"], **kw)


_MAYA = dict(forearm="mskin", sleeve_w=9, forearm_w=6, shoulders=((38, 81), (82, 80)))
BODIES = {
    "emiru": _body("emiru", "emiru", crop_top, "eskin", sleeve_w=7, forearm_w=6, shoulders=((38, 81), (82, 80))),
    "maya": _body("maya", "maya", green_tee, "olive", **_MAYA),
    "maya_glove": _body("maya_glove", "maya", green_tee, "olive", far_glove=("glove", "glove_sh", "glove"), **_MAYA),
}
MOVES = {
    **GESTURES,
    "window": (GESTURES["desk"][0], ((70, 50), (82, 35), "point"), "back"),
    "click":  (((13, 66), (24, 75), "edge"), GESTURES["desk"][1], "front"),
}
# The canvas is wider than the body on the side she faces, so a pointing arm fits.
RIG = Rig(Canvas, size=(140, 144), neck=(60, 63), chin=(37, 57), head_size=(HW, HH), gestures=MOVES, scale=1.5)
FW, FH = RIG.size


def figure(who, arms="desk", lean=0, bob=0, facing=1, held=None, outfit=None, **expr):
    """A figure (RGBA, 140x144) and its anchors; `outfit` picks a variant body ("glove" for Maya)."""
    body = BODIES[f"{who}_{outfit}" if outfit else who]
    return RIG.figure(body, arms, lean, bob, facing, held, **expr)


if __name__ == "__main__":
    from engine import ROOT, scaled
    looks = [("open", "neutral", "smile"), ("open", "up", "grin"), ("half", "skeptic", "smirk"), ("shut", "up", "wide"),
             ("wide", "worried", "o"), ("side", "angry", "open"), ("open", "neutral", "closed"),
             ("squint", "angry", "frown"), ("blink", "neutral", "grit"), ("up", "up", "open"), ("down", "worried", "closed")]
    poses = ("desk", "point", "shrug", "palm", "chin", "hold1", "window", "thumb", "finger", "chop", "bro", "facepalm",
             "pinch", "wave", "fist", "up2")
    sheet = Image.new("RGB", (len(looks) * 64 + 4, 2 * 64 + 4 + 4 * 148), (86, 90, 110))
    for r, who in enumerate(HEAD):
        for i, (eyes, brows, mouth) in enumerate(looks):
            h = head(who, eyes, brows, mouth)
            sheet.paste(h, (4 + i * 64, 4 + r * 64), h)
    for r, who in enumerate(HEAD):
        for i, arms in enumerate(poses):
            spr, _ = figure(who, arms, facing=1 if who == "emiru" else -1, mouth="grin" if i % 3 == 0 else "smile",
                            outfit="glove" if who == "maya" and i >= 13 else None)
            sheet.paste(spr, (4 + (i % 8) * 86 - 14, 132 + (r * 2 + i // 8) * 148), spr)
    out = ROOT / "build" / "characters.png"
    out.parent.mkdir(exist_ok=True)
    scaled(sheet, 3).save(out)
    print(out)
