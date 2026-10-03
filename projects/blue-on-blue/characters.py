"""Caricatures of Gavin Newsom ("newsom"), Zohran Mamdani ("mamdani") and Donald Trump ("trump").

The heads are three-quarter views facing right, on a 40x40 canvas, drawn big (about 32 px) because
the faces carry the caricature:

    newsom   the slicked-back helmet of hair with the gel shine and the grey temples, the long face and
             the square jaw, the straight nose, the anchorman's smile
    mamdani  the short dark hair, the trimmed beard, the thick brows that go up when he grins, and the
             grin, which is most of the time
    trump    the hair swoop, the orange tan with pale goggle rings, the squint, the pout, the jowls

Expressions are named parts:

    eyes    open squint half wide blink shut side up
    brows   neutral angry up worried
    mouth   closed smile pout open wide o smirk grin frown grit
"""
from functools import lru_cache

from PIL import Image

from engine import INK, Canvas, mirror  # noqa: F401

HW, HH = 40, 40
EXPR = dict(eyes="open", brows="neutral", mouth="closed", flush=0)
SKIN = {"newsom": ("nskin", "nskin_sh", "nskin_dk", "nskin_hi"), "mamdani": ("mskin", "mskin_sh", "mskin_dk", "mskin_hi"),
        "trump": ("tskin", "tskin_sh", "tskin_dk", "tskin_hi")}
# eye centres (near, far) and the mouth centre, per head. Facing right in three-quarter view: the ear
# is on the left, then the near eye, the nose bridge, and the small far eye tucked against the contour.
EYES = {"newsom": ((19, 21), (28, 21)), "mamdani": ((19, 21), (28, 21)), "trump": ((19, 21), (28, 21))}
MOUTH = {"newsom": (28, 33), "mamdani": (27, 33), "trump": (28, 32)}
LIP = {"newsom": "nlip", "mamdani": "mlip", "trump": "tlip"}


# --- the heads ------------------------------------------------------------------------------

def head_newsom(f):
    skin, sh, dk, hi = SKIN["newsom"]
    # the face: long, and a jaw like a desk drawer
    f.poly([(10, 11), (29, 9), (32, 14), (33, 21), (35, 24), (36, 27), (34, 28), (34, 31), (34, 35), (32, 38),
            (27, 39), (18, 39), (13, 36), (10, 32), (8, 25), (8, 16)], skin)
    f.poly([(8, 16), (10, 11), (13, 12), (12, 22), (13, 31), (16, 38), (13, 36), (10, 32), (8, 25)], sh)  # side plane
    f.ell((5, 18, 11, 28), skin)                                          # the ear
    f.line([(7, 20), (7, 26)], sh); f.pxs([(8, 21), (8, 25)], dk)
    f.line([(13, 32), (17, 38)], sh)                                      # the corner of the jaw
    f.line([(18, 39), (30, 39)], sh); f.px((31, 37), sh)                  # under the chin, and the cleft
    f.line([(15, 26), (19, 27)], hi)                                      # the cheekbone
    f.line([(25, 29), (24, 34)], sh)                                      # the smile line
    f.poly([(27, 19), (29, 22), (34, 26), (36, 28), (34, 29), (29, 29), (27, 28)], skin)   # the nose
    f.line([(28, 21), (32, 25)], hi); f.px((32, 28), dk); f.line([(29, 29), (33, 29)], sh)
    # the hair: lifted at the front and slicked straight back, shining, going grey over the ear
    f.poly([(6, 22), (4, 15), (4, 9), (7, 4), (12, 1), (19, 0), (26, 0), (31, 1), (35, 4), (35, 8), (32, 10),
            (27, 9), (21, 10), (15, 11), (12, 13), (11, 17), (10, 21)], "nhair")
    f.poly([(6, 22), (4, 15), (5, 11), (9, 12), (11, 17), (10, 21)], "nhair_sh")      # the back, in shade
    f.poly([(10, 21), (11, 15), (14, 12), (17, 12), (14, 16), (12, 21)], "ngrey")     # the grey temple
    f.px((13, 14), "ngrey_hi")
    f.line([(27, 9), (33, 9)], "nhair_sh")                                             # under the lift
    f.line([(31, 2), (21, 1), (11, 3)], "nhair_hi")                                    # the gel, combed back
    f.line([(33, 5), (24, 3), (14, 5), (7, 9)], "nhair_gl")
    f.line([(29, 7), (19, 6), (10, 10)], "nhair_hi")
    f.pxs([(34, 5), (25, 3)], "white")


def head_mamdani(f):
    skin, sh, dk, hi = SKIN["mamdani"]
    f.poly([(10, 11), (28, 9), (31, 13), (32, 20), (34, 24), (35, 27), (33, 28), (33, 31), (32, 35), (29, 38),
            (24, 39), (17, 38), (12, 35), (9, 30), (8, 22), (8, 15)], skin)
    f.poly([(8, 15), (10, 11), (13, 12), (12, 22), (13, 30), (15, 36), (12, 35), (9, 30), (8, 22)], sh)
    f.ell((5, 18, 11, 27), skin)                                          # the ear
    f.line([(7, 20), (7, 25)], sh); f.pxs([(8, 21), (8, 24)], dk)
    f.line([(15, 25), (18, 26)], hi)                                      # the cheek, round from grinning
    f.poly([(26, 19), (28, 22), (33, 25), (34, 28), (32, 29), (28, 29), (26, 28)], skin)   # the nose
    f.line([(27, 21), (31, 24)], hi); f.px((31, 28), dk); f.line([(28, 29), (32, 29)], sh)
    # the beard: trimmed short along the jaw to the chin, joined to the hair at the sideburn, and the moustache
    f.poly([(10, 23), (12, 30), (15, 35), (20, 38), (26, 39), (30, 37), (33, 34), (33, 31), (31, 31), (30, 35),
            (25, 37), (19, 35), (15, 31), (13, 26), (12, 22)], "mbeard")
    f.line([(25, 30), (32, 30)], "mbeard")
    f.pxs([(14, 33), (18, 36), (23, 38), (28, 38), (31, 35)], "mhair_sh")
    # the hair: short at the sides, a little height on top, neat
    f.poly([(6, 20), (4, 13), (5, 7), (9, 3), (15, 1), (22, 0), (28, 1), (32, 4), (33, 8), (31, 11), (27, 9),
            (22, 9), (17, 10), (13, 12), (11, 16), (10, 21)], "mhair")
    f.poly([(6, 20), (4, 13), (6, 10), (9, 12), (11, 16), (10, 21)], "mhair_sh")
    f.pxs([(12, 3), (16, 2), (21, 2), (26, 3), (30, 5), (14, 6), (19, 5), (24, 6), (9, 7), (28, 7)], "mhair_hi")


def head_trump(f):
    skin, sh, dk, hi = SKIN["trump"]
    # the face: narrow at the temples, heavy at the jowls
    f.poly([(9, 12), (30, 11), (32, 16), (32, 23), (34, 25), (35, 28), (33, 29), (33, 33), (32, 35), (29, 37),
            (24, 39), (17, 39), (12, 37), (9, 34), (7, 28), (7, 20)], skin)
    f.poly([(7, 20), (9, 12), (12, 12), (11, 22), (12, 31), (15, 38), (12, 37), (9, 34), (7, 28)], sh)   # side plane
    f.ell((6, 19, 12, 29), skin)                                          # the ear
    f.line([(8, 21), (8, 27)], sh); f.pxs([(9, 22), (9, 26)], dk)
    f.line([(13, 33), (17, 37)], sh)                                      # the jowl
    f.line([(17, 37), (28, 37)], sh); f.line([(19, 39), (26, 39)], sh)   # the chin under the chin
    f.line([(29, 30), (31, 34)], sh)                                      # the fold down from the nose
    f.line([(14, 27), (17, 29)], hi)                                      # cheek
    f.ell((14, 17, 24, 24), "tring"); f.ell((25, 17, 31, 24), "tring")   # the goggle tan
    f.poly([(26, 20), (28, 22), (33, 25), (35, 28), (33, 29), (29, 29), (27, 28)], skin)   # the nose
    f.line([(27, 22), (31, 25)], hi); f.px((31, 28), dk); f.line([(28, 29), (32, 29)], sh)
    # the hair: low at the back, rising into one big wave at the front that rolls forward over the brow
    f.poly([(5, 20), (3, 13), (4, 8), (8, 4), (13, 3), (17, 1), (22, 1), (25, 0), (30, 0), (34, 1), (38, 4),
            (39, 8), (39, 12), (37, 16), (34, 17), (32, 15), (30, 13), (26, 14), (20, 15), (14, 16), (11, 18),
            (9, 21)], "thair")
    f.poly([(5, 20), (3, 13), (4, 9), (9, 11), (12, 16), (11, 18), (9, 21)], "thair_sh")    # the back, in shade
    f.line([(14, 16), (20, 15), (26, 14), (30, 13)], "thair_dk")                              # the wave's shadow
    f.poly([(32, 15), (34, 17), (37, 16), (38, 13), (35, 13)], "thair_sh")                     # under the curl
    f.line([(36, 11), (38, 14)], "thair_hi")
    f.line([(6, 12), (12, 6), (22, 2), (30, 2)], "thair_hi")                                   # strands, swept forward
    f.line([(10, 13), (18, 8), (28, 5), (36, 5)], "thair_hi")
    f.line([(16, 12), (26, 9), (34, 9), (38, 9)], "thair_hi")
    f.line([(8, 16), (14, 11), (22, 8)], "thair_sh"); f.line([(20, 12), (30, 11)], "thair_sh")
    f.px((37, 3), "thair_hi")


HEAD = {"newsom": head_newsom, "mamdani": head_mamdani, "trump": head_trump}


# --- the faces ------------------------------------------------------------------------------

def eyes_draw(f, who, eyes):
    _, sh, dk, _ = SKIN[who]
    for n, (cx, cy) in enumerate(EYES[who]):
        far = n == 1
        w = 1 if far else 2                                              # the far eye is foreshortened
        if eyes == "open":
            if who == "trump":                                           # always a little narrowed
                f.rect((cx - w, cy, cx + w - 1, cy + 1), "eye")
                f.line([(cx - w - 1, cy - 1), (cx + w, cy - 1)], dk)
            else:
                f.rect((cx - w, cy - 1, cx + w - 1, cy + 1), "eye_w")
                f.rect((cx, cy - 1, cx + w - 1, cy + 1), "eye_b" if who == "newsom" else "eye")
                f.px((cx + w - 1, cy), "eye")
                f.line([(cx - w - 1, cy - 2), (cx + w, cy - 2)], dk)    # the upper lid
        elif eyes == "squint":
            f.line([(cx - w - 1, cy + 1), (cx + w, cy)], "eye")
        elif eyes == "half":
            f.rect((cx - w, cy, cx + w - 1, cy + 1), "eye")
            f.line([(cx - w - 1, cy - 1), (cx + w, cy - 1)], dk); f.line([(cx - w, cy), (cx + w - 1, cy)], sh)
        elif eyes == "wide":
            f.rect((cx - w - 1, cy - 2, cx + w, cy + 2), "eye_w")
            f.rect((cx, cy - 1, cx + w - 1, cy + 1), "eye")
        elif eyes == "blink":
            f.line([(cx - w - 1, cy + 1), (cx + w, cy + 1)], "ink")
        elif eyes == "shut":                                             # smug, or beaming: eyes closed
            f.pxs([(cx - w - 1, cy + 1), (cx - w, cy), (cx + w - 1, cy), (cx + w, cy + 1)], "ink")
            f.line([(cx - w, cy), (cx + w - 1, cy)], "ink")
        elif eyes == "side":                                             # glancing at the other man
            f.rect((cx - w, cy - 1, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx + w - 1, cy - 1, cx + w - 1, cy + 1), "eye")
            f.line([(cx - w - 1, cy - 2), (cx + w, cy - 2)], dk)
        elif eyes == "up":                                               # rolling them
            f.rect((cx - w, cy - 1, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx - w + 1, cy - 1, cx + w - 1, cy - 1), "eye")
        elif eyes == "heart":                                            # smitten
            f.pxs([(cx - w, cy - 1), (cx + w - 1, cy - 1)], "red")
            f.rect((cx - w, cy, cx + w - 1, cy), "red"); f.px((cx - 1 + (w > 1), cy + 1), "red")


def brows_draw(f, who, brows):
    col = {"newsom": "nhair_sh", "mamdani": "mhair", "trump": "thair_sh"}[who]
    thick = who != "trump"
    for n, (cx, cy) in enumerate(EYES[who]):
        far = n == 1                                                     # the far brow sits across the nose
        a, b = (cx - 2, cx + 2) if far else (cx - 3, cx + 3)
        y = cy - 4
        inner, outer = (a, b) if far else (b, a)                         # the end nearest the nose first
        if brows == "angry":                                             # the inner ends pulled down
            pts = [(inner, y + 1), (outer, y - 1)]
        elif brows == "worried":                                         # the inner ends pushed up
            pts = [(inner, y - 1), (outer, y + 1)]
        elif brows == "up":
            pts = [(inner, y - 2), (outer, y - 1)]
        else:
            pts = [(inner, y), (outer, y)]
        f.line(pts, col)
        if thick:
            f.line([(x, yy - 1) for x, yy in pts], col)


def mouth_draw(f, who, mouth):
    skin, sh, dk, hi = SKIN[who]
    lip = LIP[who]
    mx, my = MOUTH[who]
    if mouth == "closed":
        f.line([(mx - 4, my), (mx + 2, my)], "mouth")
        if who == "trump":                                               # pursed even at rest
            f.line([(mx - 3, my + 1), (mx + 1, my + 1)], lip)
    elif mouth == "smile":                                               # the anchorman's: lips together, corners up
        f.line([(mx - 4, my), (mx + 2, my)], "mouth")
        f.pxs([(mx - 5, my - 1), (mx + 3, my - 1)], "mouth")
        f.line([(mx - 3, my + 1), (mx + 1, my + 1)], lip)
    elif mouth == "pout":                                                # the pursed duck lips, pushed out
        f.ell((mx - 3, my - 2, mx + 5, my + 3), lip)
        f.line([(mx - 2, my - 2), (mx + 3, my - 2)], "tlip_hi" if who == "trump" else lip)
        f.line([(mx, my), (mx + 3, my)], "mouth"); f.px((mx + 1, my + 1), "mouth")
        f.line([(mx - 3, my + 4), (mx + 3, my + 4)], sh)
    elif mouth == "open":
        f.rect((mx - 4, my - 1, mx + 2, my + 2), "mouth")
        f.line([(mx - 3, my - 1), (mx + 2, my - 1)], "tooth")
        f.line([(mx - 3, my + 3), (mx + 1, my + 3)], lip)
    elif mouth == "wide":
        f.ell((mx - 5, my - 2, mx + 3, my + 5), "mouth")
        f.line([(mx - 3, my - 2), (mx + 1, my - 2)], "tooth")
        f.line([(mx - 3, my + 4), (mx, my + 4)], "tongue")
    elif mouth == "o":
        f.ell((mx - 3, my - 2, mx + 3, my + 3), lip)
        f.ell((mx - 1, my - 1, mx + 1, my + 2), "mouth")
    elif mouth == "smirk":                                               # one corner up
        f.line([(mx - 4, my + 1), (mx, my + 1)], "mouth")
        f.line([(mx, my + 1), (mx + 3, my - 1)], "mouth")
        f.px((mx + 4, my - 2), sh)
    elif mouth == "grin":
        f.ell((mx - 6, my - 2, mx + 4, my + 4), "mouth")
        f.rect((mx - 5, my - 1, mx + 3, my + 1), "tooth")
        f.line([(mx - 4, my + 2), (mx + 2, my + 2)], "tooth")
        if who == "mamdani":                                             # the grin pushes the cheeks up
            f.pxs([(mx - 7, my - 3), (mx + 5, my - 3)], sh)
    elif mouth == "frown":
        f.line([(mx - 4, my + 1), (mx - 2, my)], "mouth"); f.line([(mx - 2, my), (mx + 2, my + 1)], "mouth")
    elif mouth == "grit":
        f.rect((mx - 4, my - 1, mx + 2, my + 1), "tooth")
        f.line([(mx - 4, my), (mx + 2, my)], "ink")


@lru_cache(maxsize=None)
def head(who, eyes="open", brows="neutral", mouth="closed", flush=0):
    """A head sprite facing right (40x40, outlined); mirror it to face left."""
    f = Canvas(HW, HH)
    HEAD[who](f)
    eyes_draw(f, who, eyes)
    brows_draw(f, who, brows)
    mouth_draw(f, who, mouth)
    if flush:                                                            # 1: red cheeks; 2: queasy green
        (cx, cy), (fx_, fy) = EYES[who]
        col = "sick" if flush == 2 else "flush"
        f.pxs([(cx - 1, cy + 4), (cx + 1, cy + 4), (cx + 3, cy + 4)], col)
        if flush == 2:
            f.line([(cx - 2, cy + 3), (cx + 2, cy + 3)], col); f.line([(fx_ - 1, fy + 3), (fx_ + 2, fy + 3)], col)
    return f.done()


# --- the bodies -----------------------------------------------------------------------------
# Seated at the desk, from the chest up: the desk hides everything below canvas y 76. Bodies are
# three-quarter front views turned to the right, on an FW x FH canvas, built from layers that are
# outlined one by one so an arm in front of the jacket still reads: the far arm (when it hangs behind),
# the torso, the far arm (when it comes forward), the head, the near arm, and the far arm again when
# it must cover the face (a mug, a phone at the ear). Gestures are named poses of the two arms:
#
#     desk clasp steeple point finger palm shrug chop fist wave thumb thumbs2 hold show hold1 cross
#     chin drink chest hair type phone ear facepalm guns beg acc0 acc1 acc2 pinch

FW, FH = 84, 96
NECK = (40, 42)                     # where the chin lands on the body
HEAD_CHIN = (22, 37)                # the chin, in head-canvas pixels
DESK_Y = 76                         # the desk's far edge, in canvas pixels
SUIT = {"newsom": ("blazer", "blazer_sh", "blazer_hi"), "mamdani": ("msuit", "msuit_sh", "msuit_hi"),
        "trump": ("suit", "suit_sh", "suit_hi")}
HAND = {"newsom": 4, "mamdani": 4, "trump": 3}        # Trump's hands are tiny
SLEEVE = {"newsom": 6, "mamdani": 5, "trump": 7}       # and his sleeves are huge
SHOULDERS = {"trump": ((18, 48), (59, 47)), "newsom": ((20, 48), (57, 47)), "mamdani": ((22, 48), (56, 47))}

# (near elbow, near hand, near hand shape), (far elbow, far hand, far hand shape), far arm's layer;
# in Trump's body coordinates, moved with each body's shoulders
_ON_DESK = ((14, 66), (28, 74), "open")
GESTURES = {
    "desk":    (_ON_DESK, ((60, 66), (50, 74), "open"), "front"),
    "clasp":   (((15, 66), (37, 72), "clasp"), ((61, 64), (42, 72), "clasp"), "front"),
    "steeple": (((14, 66), (36, 60), "finger"), ((63, 64), (44, 60), "finger"), "front"),
    "acc0":    (((13, 64), (35, 58), "edge"), ((64, 62), (45, 58), "edge"), "front"),
    "acc1":    (((12, 64), (28, 57), "edge"), ((65, 62), (52, 57), "edge"), "front"),
    "acc2":    (((10, 62), (19, 55), "edge"), ((67, 60), (63, 55), "edge"), "front"),
    "pinch":   (_ON_DESK, ((65, 63), (58, 51), "pinch"), "front"),
    "point":   (_ON_DESK, ((69, 49), (81, 47), "point"), "back"),
    "thumb":   (_ON_DESK, ((67, 62), (65, 47), "thumb"), "back"),
    "shrug":   (((9, 62), (3, 54), "palm"), ((67, 62), (76, 54), "palm"), "back"),
    "cross":   (((15, 64), (52, 59), "fist"), ((63, 62), (28, 59), "fist"), "front"),
    "hold":    (((12, 62), (29, 54), "fist"), ((65, 60), (52, 54), "fist"), "front"),
    "show":    (((11, 64), (20, 70), "fist"), ((67, 62), (60, 70), "fist"), "front"),
    "beg":     (((12, 60), (36, 45), "clasp"), ((64, 60), (42, 45), "clasp"), "front"),
    "hold1":   (_ON_DESK, ((68, 58), (65, 44), "fist"), "back"),
    "wave":    (_ON_DESK, ((70, 52), (72, 36), "open"), "back"),
    "fist":    (_ON_DESK, ((70, 54), (66, 35), "fist"), "back"),
    "chop":    (_ON_DESK, ((65, 60), (76, 58), "edge"), "back"),
    "finger":  (_ON_DESK, ((65, 62), (63, 46), "finger"), "front"),
    "palm":    (_ON_DESK, ((66, 62), (76, 58), "palm"), "back"),
    "chin":    (((14, 62), (37, 42), "fist"), ((58, 66), (50, 74), "open"), "front"),
    "drink":   (((12, 60), (39, 45), "fist"), _ON_DESK, "front"),
    "chest":   (((14, 64), (32, 56), "open"), ((60, 66), (50, 74), "open"), "front"),
    "hair":    (((8, 44), (24, 14), "open"), ((60, 66), (50, 74), "open"), "front"),
    "type":    (((14, 66), (31, 72), "edge"), ((60, 66), (47, 71), "edge"), "front"),
    "phone":   (((12, 62), (33, 54), "fist"), ((62, 62), (46, 54), "fist"), "front"),
    "ear":     (((10, 58), (26, 32), "fist"), ((60, 66), (50, 74), "open"), "front"),
    "facepalm": (_ON_DESK, ((64, 56), (50, 28), "open"), "over"),
    "guns":    (((14, 60), (30, 50), "point"), ((68, 52), (80, 46), "point"), "back"),
    "thumbs2": (((10, 62), (16, 50), "thumb"), ((67, 62), (66, 47), "thumb"), "back"),
}


def gesture(who, arms):
    """The two arms as (shoulder, elbow, hand, shape) and the far arm's layer, for this body."""
    near, far, layer = GESTURES[arms]
    (tn, tf), (sn, sf) = SHOULDERS["trump"], SHOULDERS[who]
    out = []
    for (e, h, kind), t, s in ((near, tn, sn), (far, tf, sf)):
        dx, dy = s[0] - t[0], s[1] - t[1]
        out.append((s, (e[0] + dx, e[1] + dy), (h[0] + dx, h[1] + dy), kind))
    return out[0], out[1], layer


def torso_draw(f, who):
    cloth, shade, light = SUIT[who]
    hem = 92
    if who == "trump":                                                   # boxy, and a belly
        f.poly([(20, 45), (33, 42), (47, 42), (56, 44), (61, 49), (64, 57), (66, 65), (64, 73), (61, hem),
                (17, hem), (14, 71), (13, 59), (15, 50)], cloth)
        f.poly([(56, 44), (61, 49), (64, 57), (66, 65), (64, 73), (61, hem), (57, hem), (59, 71), (60, 61),
                (57, 51)], shade)
        f.line([(46, 64), (56, 66)], shade)                              # the jacket strains at the button
    elif who == "mamdani":                                               # slim
        f.poly([(23, 45), (34, 42), (46, 42), (53, 44), (57, 50), (58, 60), (58, 70), (57, hem), (21, hem),
                (19, 70), (19, 58), (20, 49)], cloth)
        f.poly([(53, 44), (57, 50), (58, 60), (58, 70), (57, hem), (54, hem), (54, 68), (54, 57), (51, 50)], shade)
    else:
        f.poly([(22, 45), (34, 42), (46, 42), (54, 44), (58, 50), (59, 60), (59, 70), (58, hem), (19, hem),
                (17, 70), (17, 58), (18, 49)], cloth)
        f.poly([(54, 44), (58, 50), (59, 60), (59, 70), (58, hem), (55, hem), (55, 68), (55, 57), (52, 50)], shade)
    f.line([(21, 45), (32, 42)], light)
    if who == "newsom":                                                  # open collar, no tie: a podcast
        f.poly([(35, 42), (45, 42), (41, 56)], "shirt")
        f.poly([(37, 42), (43, 42), (40, 47)], "nskin"); f.px((40, 46), "nskin_sh")
        f.line([(35, 42), (38, 47)], "shirt_sh"); f.line([(45, 42), (42, 47)], "shirt_sh")    # the collar points
        f.line([(34, 43), (40, 58)], shade); f.line([(46, 43), (42, 58)], shade)             # lapels
        f.rect((25, 52, 29, 53), "white"); f.px((26, 51), "white")                           # the pocket square
        return
    shirt = "mshirt" if who == "mamdani" else "shirt"
    f.poly([(35, 42), (45, 42), (41, 57)], shirt)                        # the shirt in the V
    f.line([(34, 43), (40, 58)], shade); f.line([(46, 43), (42, 58)], shade)   # lapels
    if who == "trump":                                                   # the long red tie, down to the lap
        f.poly([(38, 46), (42, 46), (45, 74), (41, 86), (37, 74)], "tie")
        f.line([(41, 47), (43, 73)], "tie_hi"); f.line([(38, 50), (38, 72)], "tie_sh")
        f.rect((38, 43, 42, 46), "tie_sh")
        f.px((30, 50), "red"); f.px((31, 50), "white"); f.px((30, 51), "blue")   # the flag pin
    else:
        f.poly([(38, 46), (42, 46), (43, 62), (40, 66), (37, 62)], "mtie")
        f.line([(41, 47), (42, 61)], "mtie_hi")
        f.rect((38, 43, 42, 46), "mtie_sh")


def headphones_draw(f):
    """Studio headphones, slung round the neck."""
    f.line([(29, 44), (33, 47), (40, 48), (47, 47), (51, 44)], "phones", w=2)
    f.ell((25, 40, 31, 47), "phones"); f.ell((49, 40, 54, 46), "phones")
    f.line([(26, 42), (27, 41)], "phones_hi"); f.px((50, 41), "phones_hi")


def hand_draw(f, who, e, h, kind):
    """A hand at h, its forearm coming from e. Shapes: open clasp fist point finger thumb pinch palm edge."""
    skin, sh, _, _ = SKIN[who]
    n = HAND[who]
    r = n // 2
    x, y = h
    dx, dy = x - e[0], y - e[1]
    d = max(1.0, (dx * dx + dy * dy) ** 0.5)
    if kind == "clasp":                                                  # both hands, fingers laced
        f.ell((x - r - 2, y - r, x + r + 2, y + r + 1), skin)
        f.line([(x, y - r), (x, y + r)], sh)
    elif kind == "open":
        f.ell((x - r, y - r, x + r, y + r + 1), skin)
        f.px((x - r, y + r), sh)
    elif kind == "palm":                                                 # flat, palm up
        f.ell((x - r - 1, y - 1, x + r + 1, y + 1), skin)
        f.line([(x - r, y + 1), (x + r, y + 1)], sh)
    elif kind == "edge":                                                 # flat, edge on: a chop, or the accordion
        f.rect((x - 1, y - r - 1, x, y + r + 1), skin)
        f.line([(x, y - r), (x, y + r)], sh)
    else:
        f.rect((x - r, y - r, x + r, y + r), skin)                       # a fist, and what sticks out of it
        f.line([(x - r, y + r), (x + r, y + r)], sh)
        if kind == "point":
            f.line([(x, y - (r > 1)), (round(x + dx / d * (r + 3)), round(y - (r > 1) + dy / d * (r + 3)))], skin)
        elif kind == "finger":
            f.line([(x + r - 1, y - r), (x + r - 1, y - r - 3 - (n > 3))], skin)
        elif kind == "thumb":
            f.rect((x - r, y - r - 3, x - r + 1, y - r), skin)
        elif kind == "pinch":                                            # thumb and finger in a ring
            f.pxs([(x, y - r - 1), (x + 1, y - r - 2), (x + 2, y - r - 1), (x + 1, y - r)], skin)


def arm_layer(who, s, e, h, kind, size):
    """One arm (sleeve, cuff and hand) on its own outlined layer."""
    cloth, shade, light = SUIT[who]
    w = SLEEVE[who]
    f = Canvas(*size)
    f.line([s, e], cloth, w=w)
    f.ell((s[0] - w // 2, s[1] - w // 2, s[0] + w // 2, s[1] + w // 2), cloth)
    f.ell((e[0] - w // 2, e[1] - w // 2, e[0] + w // 2, e[1] + w // 2), cloth)
    f.line([e, h], cloth, w=w - 1)
    dx, dy = h[0] - e[0], h[1] - e[1]
    d = max(1.0, (dx * dx + dy * dy) ** 0.5)
    k = HAND[who] // 2 + 2
    cx, cy = round(h[0] - dx / d * k), round(h[1] - dy / d * k)
    f.ell((cx - 2, cy - 2, cx + 2, cy + 2), "mshirt" if who == "mamdani" else "shirt")    # the cuff
    hand_draw(f, who, e, h, kind)
    return f.done()


def hand_layer(who, arms_, size):
    f = Canvas(*size)
    for s, e, h, kind in arms_:
        hand_draw(f, who, e, h, kind)
    return f.done()


def _flip(xy, facing):
    return xy if facing > 0 else (FW - 1 - xy[0], xy[1])


@lru_cache(maxsize=512)
def _figure(who, arms, lean, bob, facing, phones, expr):
    size = (FW, FH)
    near, far, layer = gesture(who, arms)
    img = Canvas(*size).img
    if layer == "back":
        img.alpha_composite(arm_layer(who, *far, size))
    f = Canvas(*size); torso_draw(f, who)
    if phones:
        headphones_draw(f)
    img.alpha_composite(f.done())
    if layer == "front":
        img.alpha_composite(arm_layer(who, *far, size))
    hx, hy = NECK[0] - HEAD_CHIN[0] + lean, NECK[1] - HEAD_CHIN[1] + bob
    img.alpha_composite(head(who, **dict(expr)), (hx, hy))
    img.alpha_composite(arm_layer(who, *near, size))
    if layer == "over":
        img.alpha_composite(arm_layer(who, *far, size))
    hands = hand_layer(who, (near, far), size)
    if facing < 0:
        img, hands = mirror(img), mirror(hands)
    anchors = {"hand_near": _flip(near[2], facing), "hand_far": _flip(far[2], facing),
               "head": _flip((hx + HW // 2, hy), facing), "eye": _flip((hx + EYES[who][0][0], hy + EYES[who][0][1]), facing),
               "mouth": _flip((hx + MOUTH[who][0], hy + MOUTH[who][1]), facing),
               "chest": _flip((40, 58), facing), "desk": _flip((40, DESK_Y), facing)}
    return img, hands, anchors


def figure(who, arms="desk", lean=0, bob=0, facing=1, held=None, phones=True, **expr):
    """A figure (RGBA, FW x FH) and its anchors in sprite pixels: hand_near, hand_far, head (top centre),
    eye, mouth, chest, desk. held = (prop image, anchor name or (x, y)) is drawn in front of the body and
    under the hands, unmirrored, centred on the point (on the midpoint of both hands for "hands")."""
    e = dict(EXPR); e.update(expr)
    img, hands, anchors = _figure(who, arms, lean, bob, facing, phones and who != "trump", tuple(sorted(e.items())))
    if not held:
        return img, anchors
    prop, at = held
    if at in ("hands", "hands_top"):                                     # between the hands, or held up by
        (ax, ay), (bx, by) = anchors["hand_near"], anchors["hand_far"]   # its bottom corners
        at = ((ax + bx) // 2, (ay + by) // 2 - (prop.height // 2 - 3 if at == "hands_top" else 0))
    elif isinstance(at, str):
        at = anchors[at]
    elif isinstance(at[0], str):                                         # (anchor, raised by n pixels)
        ax, ay = anchors[at[0]]
        at = (ax, ay - at[1])
    x0, y0 = at[0] - prop.width // 2, at[1] - prop.height // 2
    pad = max(0, -x0, -y0, x0 + prop.width - FW, y0 + prop.height - FH)  # room for a prop wider than the body
    out = Image.new("RGBA", (FW + 2 * pad, FH + 2 * pad))
    out.alpha_composite(img, (pad, pad))
    out.alpha_composite(prop, (x0 + pad, y0 + pad))
    out.alpha_composite(hands, (pad, pad))
    anchors = {k: (x + pad, y + pad) for k, (x, y) in dict(anchors, held=at).items()}
    return out, anchors                                                  # "held": the prop's centre


if __name__ == "__main__":
    from PIL import Image

    from engine import ROOT, scaled
    sheet = Image.new("RGB", (8 * 44 + 4, 3 * 44 + 4 + 3 * 100), (30, 38, 70))
    for r, who in enumerate(HEAD):
        for i, (eyes, brows, mouth) in enumerate([("open", "neutral", "closed"), ("open", "neutral", "smile"),
                                                  ("open", "up", "grin"), ("squint", "angry", "open"),
                                                  ("wide", "worried", "o"), ("half", "neutral", "smirk"),
                                                  ("side", "angry", "frown"), ("heart", "up", "wide")]):
            h = head(who, eyes, brows, mouth)
            sheet.paste(h, (4 + i * 44, 4 + r * 44), h)
    for r, who in enumerate(HEAD):
        for i, arms in enumerate(("desk", "point", "shrug", "hair")):
            spr, _ = figure(who, arms, facing=1 if i % 2 == 0 else -1, mouth="grin")
            sheet.paste(spr, (4 + i * 88, 136 + r * 100), spr)
    out = ROOT / "build" / "characters.png"
    scaled(sheet, 3).save(out)
    print(out)
