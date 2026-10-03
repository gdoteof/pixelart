"""Caricatures of Donald Trump ("trump"), Benjamin Netanyahu ("bibi") and Barack Obama ("obama").

The heads are three-quarter views facing right, on a 40x40 canvas, drawn big (about 32 px) because
the faces carry the caricature:

    trump   the hair swoop, the orange tan with pale goggle rings, the squint, the pout, the jowls
    bibi    the silver side-sweep over a high forehead, the dark heavy brows, the hooded eyes, the smirk
    obama   the cropped grey hair, the ears, the long jaw and the big grin

Expressions are named parts:

    eyes    open squint half wide blink shut side up
    brows   neutral angry up worried
    mouth   closed pout open wide o smirk grin frown grit
"""
from functools import lru_cache

from engine import INK, Canvas, mirror  # noqa: F401

HW, HH = 40, 40
EXPR = dict(eyes="open", brows="neutral", mouth="closed", flush=0)
SKIN = {"trump": ("tskin", "tskin_sh", "tskin_dk", "tskin_hi"), "bibi": ("bskin", "bskin_sh", "bskin_dk", "bskin_hi"),
        "obama": ("oskin", "oskin_sh", "oskin_dk", "oskin_hi")}
# eye centres (near, far) and the mouth centre, per head. Facing right in three-quarter view: the ear
# is on the left, then the near eye, the nose bridge, and the small far eye tucked against the contour.
EYES = {"trump": ((19, 21), (28, 21)), "bibi": ((19, 20), (28, 20)), "obama": ((19, 19), (28, 19))}
MOUTH = {"trump": (28, 32), "bibi": (27, 32), "obama": (25, 31)}
LIP = {"trump": "tlip", "bibi": "blip", "obama": "olip"}


# --- the heads ------------------------------------------------------------------------------

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


def head_bibi(f):
    skin, sh, dk, hi = SKIN["bibi"]
    f.ell((4, 4, 25, 25), "bhair_sh")                                   # the close-cropped back and sides
    f.ell((7, 6, 32, 33), skin)                                         # face
    f.ell((7, 18, 33, 38), skin)                                        # the full jowls
    f.poly([(16, 4), (29, 5), (33, 12), (16, 13)], skin)                # the high forehead
    f.ell((5, 17, 10, 34), sh)                                          # the turned-away side
    f.ell((7, 19, 12, 27), skin); f.pxs([(8, 21), (9, 22), (9, 23), (8, 25)], dk)   # ear
    f.rect((6, 11, 11, 18), "bhair_sh"); f.line([(7, 12), (10, 12)], "bhair")       # grey above the ear
    f.line([(11, 35), (17, 37)], sh); f.line([(17, 37), (28, 37)], sh)  # the chin under the chin
    f.line([(13, 31), (16, 35)], sh)                                    # jowl
    f.poly([(25, 19), (29, 23), (32, 26), (31, 28), (27, 28)], skin)    # nose: modest, never the feature
    f.line([(26, 21), (28, 23)], hi)
    f.line([(28, 28), (31, 28)], sh)
    f.line([(32, 30), (33, 35)], sh); f.line([(21, 29), (19, 34)], sh)  # the long folds down to the jowls
    f.line([(21, 8), (28, 9)], hi)                                      # forehead shine
    # the silver hair: combed up off the high forehead into a crest, then back; short and darker at the sides
    f.poly([(4, 18), (3, 11), (5, 5), (10, 2), (17, 0), (24, 0), (29, 1), (32, 4), (32, 8), (29, 9), (25, 7),
            (20, 7), (15, 9), (12, 12), (11, 17), (8, 19)], "bhair")
    f.poly([(4, 18), (3, 11), (6, 8), (10, 11), (11, 17), (8, 19)], "bhair_sh")
    f.line([(8, 4), (16, 1), (24, 1)], "white"); f.line([(10, 6), (18, 3), (28, 3)], "bhair_hi")
    f.line([(13, 8), (20, 5), (31, 5)], "bhair_hi")
    f.line([(6, 9), (12, 6), (18, 5)], "bhair_sh"); f.line([(21, 6), (29, 7)], "bhair_sh")


def head_obama(f):
    skin, sh, dk, hi = SKIN["obama"]
    f.ell((2, 14, 10, 30), skin); f.pxs([(4, 18), (5, 19), (5, 22), (4, 25)], dk)   # the ear, out wide
    f.line([(3, 16), (3, 27)], sh)
    f.ell((7, 2, 31, 34), skin)                                         # the long face
    f.ell((10, 18, 31, 39), skin)                                       # the long jaw
    f.ell((7, 14, 10, 31), sh)
    f.line([(16, 37), (27, 38)], sh)
    f.poly([(24, 16), (29, 21), (34, 25), (33, 27), (26, 27)], skin)    # nose
    f.line([(25, 18), (28, 21)], hi)
    f.line([(27, 27), (33, 27)], sh); f.px((30, 26), dk)
    f.line([(31, 28), (32, 33)], sh); f.line([(19, 27), (17, 33)], sh)  # the smile lines
    f.pxs([(14, 20), (13, 21)], sh)                                     # crow's feet
    # the hair: short and grey, a cap close to the skull with a soft, receding hairline
    f.ell((7, 0, 30, 13), "ohair")
    f.rect((7, 7, 11, 14), "ohair")
    f.pxs([(11, 2), (15, 1), (19, 1), (23, 2), (13, 5), (18, 4), (24, 5), (10, 8), (27, 4), (9, 11)], "ohair_hi")
    f.pxs([(14, 3), (21, 3), (17, 6), (12, 9), (26, 7)], "ohair_sh")
    f.poly([(27, 10), (31, 9), (31, 13), (28, 12)], skin)               # the temple, receding a little


HEAD = {"trump": head_trump, "bibi": head_bibi, "obama": head_obama}


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
                f.rect((cx, cy - 1, cx + w - 1, cy + 1), "eye")
                f.line([(cx - w - 1, cy - 2), (cx + w, cy - 2)], dk)    # the upper lid
                if who == "bibi":                                       # the hooded lid and the bag under
                    f.line([(cx - w, cy - 1), (cx + w - 1, cy - 1)], sh)
                    f.line([(cx - w, cy + 3), (cx + w, cy + 3)], sh)
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
        elif eyes == "shut":                                             # smug, eyes closed
            f.pxs([(cx - w - 1, cy), (cx - w, cy + 1), (cx + w - 1, cy + 1), (cx + w, cy)], "ink")
            f.line([(cx - w, cy + 1), (cx + w - 1, cy + 1)], "ink")
        elif eyes == "side":                                             # glancing at the other man
            f.rect((cx - w, cy - 1, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx + w - 1, cy - 1, cx + w - 1, cy + 1), "eye")
            f.line([(cx - w - 1, cy - 2), (cx + w, cy - 2)], dk)
        elif eyes == "up":                                               # rolling them
            f.rect((cx - w, cy - 1, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx - w + 1, cy - 1, cx + w - 1, cy - 1), "eye")


def brows_draw(f, who, brows):
    col = {"trump": "thair_sh", "bibi": "bbrow", "obama": "ohair_sh"}[who]
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
# Bodies are three-quarter front views turned to the right, on an FW x FH canvas (FH_STAND for the
# standing cast), built from layers that are outlined one by one, so an arm in front of the suit
# still reads: the far arm (when it hangs behind), the legs, the torso, the far arm (when it comes
# forward), the head, the near arm, and the far arm again when it must cover the face (a cup, a mic).
# Gestures are named poses of the two arms:
#
#     seated   between lap steeple acc0 acc1 acc2 pinch point thumb shrug cross hold hold1 wave fist
#              chop finger palm dance0 dance1 phone chin drink clear mic
#     standing rest, plus everything above that doesn't need a lap
#
# Legs are "spread" (Trump's wide-kneed sit), "together" (Bibi's) or "stand".

FW, FH, FH_STAND = 84, 110, 132
FEET_STAND = 128                    # the soles of a standing figure, in canvas pixels
NECK = (40, 42)                     # where the chin lands on the body
HEAD_CHIN = (22, 37)                # the chin, in head-canvas pixels
SUIT = {"trump": ("suit", "suit_sh", "suit_hi"), "bibi": ("bsuit", "bsuit_sh", "bsuit_hi"),
        "obama": ("tan", "tan_sh", "tan_hi"), "announcer": ("tux", "tux_sh", "tux_hi")}
SKIN["announcer"] = ("askin", "askin_sh", "askin_sh", "askin")
HAND = {"trump": 3, "bibi": 4, "obama": 4, "announcer": 4}       # Trump's hands are tiny
SLEEVE = {"trump": 7, "bibi": 6, "obama": 5, "announcer": 5}     # and his sleeves are huge
SHOULDERS = {"trump": ((18, 48), (59, 47)), "bibi": ((20, 48), (56, 47)), "obama": ((21, 48), (56, 47)),
             "announcer": ((21, 48), (56, 47))}

# (near elbow, near hand, near hand shape), (far elbow, far hand, far hand shape), far arm's layer;
# in Trump's body coordinates, moved with each body's shoulders
_ON_THIGH = ((16, 66), (30, 78), "open")
GESTURES = {
    "between": (((15, 66), (38, 84), "clasp"), ((61, 64), (42, 84), "clasp"), "front"),
    "lap":     (_ON_THIGH, ((58, 65), (50, 78), "open"), "front"),
    "steeple": (((14, 66), (36, 62), "finger"), ((63, 64), (44, 62), "finger"), "front"),
    "acc0":    (((13, 64), (35, 58), "edge"), ((64, 62), (45, 58), "edge"), "front"),
    "acc1":    (((12, 64), (28, 57), "edge"), ((65, 62), (52, 57), "edge"), "front"),
    "acc2":    (((10, 62), (19, 55), "edge"), ((67, 60), (63, 55), "edge"), "front"),
    "pinch":   (_ON_THIGH, ((65, 63), (58, 51), "pinch"), "front"),
    "point":   (_ON_THIGH, ((69, 49), (81, 47), "point"), "back"),
    "thumb":   (_ON_THIGH, ((67, 62), (65, 47), "thumb"), "back"),
    "shrug":   (((9, 62), (3, 54), "palm"), ((67, 62), (76, 54), "palm"), "back"),
    "cross":   (((15, 64), (52, 59), "fist"), ((63, 62), (28, 59), "fist"), "front"),
    "hold":    (((12, 62), (29, 52), "fist"), ((65, 60), (52, 52), "fist"), "front"),
    "show":    (((11, 64), (20, 74), "fist"), ((67, 62), (60, 74), "fist"), "front"),
    "shoulder": (((16, 62), (52, 50), "open"), ((58, 65), (50, 78), "open"), "front"),
    "tummy":   (((14, 64), (31, 67), "open"), ((64, 62), (49, 67), "open"), "front"),
    "beg":     (((12, 60), (36, 45), "clasp"), ((64, 60), (42, 45), "clasp"), "front"),
    "hold1":   (_ON_THIGH, ((68, 58), (65, 44), "fist"), "back"),
    "wave":    (_ON_THIGH, ((70, 52), (72, 36), "open"), "back"),
    "fist":    (_ON_THIGH, ((70, 54), (66, 35), "fist"), "back"),
    "chop":    (_ON_THIGH, ((65, 60), (76, 58), "edge"), "back"),
    "finger":  (_ON_THIGH, ((65, 62), (63, 46), "finger"), "front"),
    "palm":    (_ON_THIGH, ((66, 62), (76, 58), "palm"), "back"),
    "dance0":  (((9, 58), (20, 47), "fist"), ((69, 61), (60, 54), "fist"), "front"),
    "dance1":  (((9, 61), (19, 55), "fist"), ((69, 56), (61, 45), "fist"), "front"),
    "phone":   (((10, 58), (26, 32), "fist"), ((58, 65), (50, 78), "open"), "front"),
    "chin":    (((14, 62), (37, 42), "fist"), ((58, 65), (50, 78), "open"), "front"),
    "drink":   (((12, 60), (39, 45), "fist"), ((64, 60), (48, 45), "fist"), "over"),
    "clear":   (((13, 63), (29, 56), "palm"), ((64, 61), (51, 56), "palm"), "front"),
    "mic":     (_ON_THIGH, ((66, 60), (50, 44), "fist"), "over"),
    "read":    (((14, 62), (27, 54), "fist"), ((66, 60), (50, 44), "fist"), "over"),
    "thumbs2": (((10, 62), (16, 50), "thumb"), ((67, 62), (66, 47), "thumb"), "back"),
}
STAND_REST = (((19, 64), (21, 80), "open"), ((61, 63), (59, 79), "open"), "back")


def gesture(who, arms, standing):
    """The two arms as (shoulder, elbow, hand, shape) and the far arm's layer, for this body."""
    near, far, layer = STAND_REST if arms == "rest" else GESTURES[arms]
    if standing and near is _ON_THIGH:                                   # no lap: the near arm hangs
        near = STAND_REST[0]
    if standing and far[1][1] >= 76 and arms != "rest":
        far = STAND_REST[1]
    (tn, tf), (sn, sf) = SHOULDERS["trump"], SHOULDERS[who]
    out = []
    for (e, h, kind), t, s in ((near, tn, sn), (far, tf, sf)):
        dx, dy = s[0] - t[0], s[1] - t[1]
        out.append((s, (e[0] + dx, e[1] + dy), (h[0] + dx, h[1] + dy), kind))
    return out[0], out[1], layer


def torso_draw(f, who, standing):
    cloth, shade, light = SUIT[who]
    hem = 91 if standing else 79
    if who == "trump":                                                   # boxy, and a belly
        f.poly([(20, 45), (33, 42), (47, 42), (56, 44), (61, 49), (64, 57), (66, 65), (64, 73), (61, hem),
                (17, hem), (14, 71), (13, 59), (15, 50)], cloth)
        f.poly([(56, 44), (61, 49), (64, 57), (66, 65), (64, 73), (61, hem), (57, hem), (59, 71), (60, 61),
                (57, 51)], shade)
        f.line([(46, 64), (56, 66)], shade)                              # the jacket strains at the button
    else:
        f.poly([(22, 45), (34, 42), (46, 42), (54, 44), (58, 50), (59, 60), (59, 70), (58, hem), (19, hem),
                (17, 70), (17, 58), (18, 49)], cloth)
        f.poly([(54, 44), (58, 50), (59, 60), (59, 70), (58, hem), (55, hem), (55, 68), (55, 57), (52, 50)], shade)
    f.line([(21, 45), (32, 42)], light)
    f.poly([(35, 42), (45, 42), (41, 57)], "shirt")                      # the shirt in the V
    f.line([(34, 43), (40, 58)], shade); f.line([(46, 43), (42, 58)], shade)   # lapels
    if who == "announcer":                                               # the bow tie and the shirt studs
        f.poly([(37, 43), (40, 44), (43, 43), (43, 47), (40, 46), (37, 47)], "black")
        f.pxs([(41, 50), (41, 53)], "black")
        return
    if who == "trump":                                                   # the long red tie, down to the lap
        f.poly([(38, 46), (42, 46), (45, 74), (41, 86), (37, 74)], "tie")
        f.line([(41, 47), (43, 73)], "tie_hi"); f.line([(38, 50), (38, 72)], "tie_sh")
        f.rect((38, 43, 42, 46), "tie_sh")
        f.px((30, 50), "red"); f.px((31, 50), "white"); f.px((30, 51), "blue")   # the flag pin
    else:
        tie, tie_sh, tie_hi = {"bibi": ("btie", "btie_sh", "btie_hi"), "obama": ("otie", "otie_sh", "otie_sh")}[who]
        f.poly([(38, 46), (42, 46), (43, 62), (40, 66), (37, 62)], tie)
        f.line([(41, 47), (42, 61)], tie_hi)
        f.rect((38, 43, 42, 46), tie_sh)
        if who == "bibi":
            f.px((31, 50), "white"); f.px((32, 50), "blue_sh")


def legs_draw(f, who, legs):
    cloth, shade, light = SUIT[who]
    if legs == "spread":                                                 # knees wide, feet planted wide
        f.poly([(14, 72), (37, 75), (28, 90), (6, 91), (3, 85)], cloth)
        f.poly([(41, 75), (64, 72), (80, 82), (78, 89), (61, 89)], cloth)
        f.line([(15, 73), (4, 84)], light); f.line([(63, 73), (79, 82)], light)
        f.poly([(6, 89), (25, 89), (23, 103), (9, 103)], cloth); f.line([(10, 90), (11, 102)], shade)
        f.poly([(62, 87), (78, 87), (76, 101), (65, 101)], cloth); f.line([(73, 88), (73, 100)], shade)
        f.ell((3, 101, 26, 108), "shoe"); f.ell((61, 99, 81, 105), "shoe")
        f.line([(8, 102), (16, 102)], "shoe_hi"); f.line([(66, 100), (74, 100)], "shoe_hi")
    elif legs == "together":                                             # knees together, turned his way
        f.poly([(18, 72), (57, 72), (70, 80), (70, 90), (46, 90), (28, 84), (18, 80)], cloth)
        f.line([(19, 73), (56, 73)], light); f.line([(36, 79), (57, 89)], shade)
        f.poly([(48, 89), (70, 89), (67, 103), (51, 103)], cloth); f.line([(59, 90), (59, 102)], shade)
        f.ell((45, 101, 62, 108), "shoe"); f.ell((57, 100, 75, 107), "shoe")
        f.line([(50, 102), (56, 102)], "shoe_hi"); f.line([(63, 101), (70, 101)], "shoe_hi")
    elif legs in ("step0", "step1"):                                     # walking: one stride, then the other
        a, b = (-5, 4) if legs == "step0" else (4, -5)
        f.poly([(22, 89), (40, 89), (38 + a, 123), (26 + a, 123)], cloth)
        f.poly([(40, 89), (57, 89), (54 + b, 121), (43 + b, 121)], cloth)
        f.line([(40, 92), (40 + a // 2, 122)], shade)
        f.ell((22 + a, 121, 42 + a, 128), "shoe"); f.ell((40 + b, 119, 60 + b, 126), "shoe")
    elif legs == "stand":                                                # short legs: a caricature's
        f.poly([(22, 89), (40, 89), (38, 123), (26, 123)], cloth)
        f.poly([(40, 89), (57, 89), (54, 121), (43, 121)], cloth)
        f.line([(40, 92), (40, 122)], shade); f.line([(53, 92), (51, 120)], shade)
        f.ell((22, 121, 42, 128), "shoe"); f.ell((40, 119, 60, 126), "shoe")
        f.line([(27, 122), (34, 122)], "shoe_hi"); f.line([(46, 120), (53, 120)], "shoe_hi")


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
    f.ell((cx - 2, cy - 2, cx + 2, cy + 2), "shirt")                    # the cuff
    hand_draw(f, who, e, h, kind)
    return f.done()


def hand_layer(who, arms_, size):
    f = Canvas(*size)
    for s, e, h, kind in arms_:
        hand_draw(f, who, e, h, kind)
    return f.done()


def _flip(xy, facing):
    return xy if facing > 0 else (FW - 1 - xy[0], xy[1])


@lru_cache(maxsize=256)
def _figure(who, legs, arms, lean, bob, facing, expr):
    standing = legs in ("stand", "step0", "step1")
    size = (FW, FH_STAND if standing else FH)
    near, far, layer = gesture(who, arms, standing)
    img = Canvas(*size).img
    if layer == "back":
        img.alpha_composite(arm_layer(who, *far, size))
    f = Canvas(*size); legs_draw(f, who, legs); img.alpha_composite(f.done())
    f = Canvas(*size); torso_draw(f, who, standing); img.alpha_composite(f.done())
    if layer == "front":
        img.alpha_composite(arm_layer(who, *far, size))
    hx, hy = NECK[0] - HEAD_CHIN[0] + lean, NECK[1] - HEAD_CHIN[1] + bob
    img.alpha_composite(head("obama" if who == "announcer" else who, **dict(expr)) if who != "announcer"
                        else announcer_head(**dict(expr)), (hx, hy))
    img.alpha_composite(arm_layer(who, *near, size))
    if layer == "over":
        img.alpha_composite(arm_layer(who, *far, size))
    hands = hand_layer(who, (near, far), size)
    if facing < 0:
        img, hands = mirror(img), mirror(hands)
    anchors = {"hand_near": _flip(near[2], facing), "hand_far": _flip(far[2], facing),
               "head": _flip((hx + HW // 2, hy), facing), "eye": _flip((hx + EYES.get(who, EYES["obama"])[0][0],
                                                                         hy + EYES.get(who, EYES["obama"])[0][1]), facing),
               "mouth": _flip((hx + MOUTH.get(who, MOUTH["obama"])[0], hy + MOUTH.get(who, MOUTH["obama"])[1]), facing),
               "lap": _flip((40, 80), facing), "chest": _flip((40, 58), facing)}
    return img, hands, anchors


def figure(who, legs="spread", arms="between", lean=0, bob=0, facing=1, held=None, **expr):
    """A figure (RGBA, FW wide) and its anchors in sprite pixels: hand_near, hand_far, head (top centre),
    eye, mouth, lap, chest. held = (prop image, anchor name or (x, y)) is drawn in front of the body
    and under the hands, unmirrored, centred on the point (on the midpoint of both hands for "hands")."""
    e = dict(EXPR); e.update(expr)
    img, hands, anchors = _figure(who, legs, arms, lean, bob, facing, tuple(sorted(e.items())))
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
    out = img.copy()
    out.alpha_composite(prop, (at[0] - prop.width // 2, at[1] - prop.height // 2))
    out.alpha_composite(hands)
    return out, dict(anchors, held=at)                                   # the prop's centre


# --- the announcer's head: slicked dark hair, a big chin, a showman's smile ---------------------

@lru_cache(maxsize=None)
def announcer_head(eyes="open", brows="neutral", mouth="grin", flush=0):
    f = Canvas(HW, HH)
    f.ell((7, 6, 31, 34), "askin"); f.ell((9, 18, 31, 38), "askin")
    f.ell((7, 16, 11, 33), "askin_sh")
    f.ell((7, 19, 12, 27), "askin"); f.pxs([(8, 21), (9, 23)], "askin_sh")
    f.poly([(25, 17), (29, 22), (33, 26), (32, 28), (27, 28)], "askin")
    f.line([(27, 28), (32, 28)], "askin_sh")
    f.ell((6, 2, 30, 16), "ahair"); f.rect((7, 8, 12, 17), "ahair")     # slicked straight back
    f.line([(10, 5), (26, 3)], "tux_hi"); f.line([(9, 9), (20, 7)], "tux_hi")
    f.line([(14, 37), (26, 37)], "askin_sh")                             # the big chin
    saved = dict(SKIN)
    SKIN["obama"] = SKIN["announcer"]                                    # borrow Obama's face layout
    try:
        eyes_draw(f, "obama", eyes); brows_draw(f, "obama", brows); mouth_draw(f, "obama", mouth)
    finally:
        SKIN.update(saved)
    return f.done()


# --- the chair: the Oval Office armchair, turned with its sitter ----------------------------

@lru_cache(maxsize=None)
def chair(facing=1):
    """The armchair on the figure canvas, so a seated figure pasted at the same spot sits in it."""
    f = Canvas(FW, FH)
    f.poly([(14, 34), (36, 30), (60, 32), (66, 38), (66, 74), (12, 76), (10, 40)], "chair")   # the back
    f.line([(15, 35), (36, 31), (59, 33)], "chair_hi")
    f.poly([(60, 32), (66, 38), (66, 74), (62, 74), (62, 38)], "chair_sh")
    f.poly([(8, 70), (70, 68), (76, 80), (12, 84)], "chair")                                    # the seat
    f.line([(10, 71), (69, 69)], "chair_hi")
    f.poly([(2, 58), (14, 56), (18, 60), (18, 88), (6, 90), (2, 82)], "chair")                  # the near arm
    f.ell((1, 55, 15, 66), "chair_hi"); f.ell((4, 58, 12, 64), "chair"); f.px((8, 61), "chair_sh")
    f.poly([(64, 54), (74, 52), (78, 56), (78, 82), (68, 84), (64, 80)], "chair_sh")           # the far arm
    f.ell((66, 51, 78, 60), "chair")
    f.poly([(8, 84), (76, 80), (76, 90), (10, 94)], "chair_sh")                                 # the skirt
    f.line([(9, 86), (75, 82)], "gold_dk")
    for x0, y0 in ((10, 93), (70, 89), (40, 92)):                                               # gilded feet
        f.rect((x0, y0, x0 + 3, y0 + 6), "gold"); f.px((x0 + 1, y0 + 1), "gold_hi")
    img = f.done()
    return img if facing > 0 else mirror(img)


if __name__ == "__main__":
    from PIL import Image

    from engine import ROOT, C, scaled
    looks = [dict(), dict(mouth="pout"), dict(mouth="open"), dict(mouth="wide", brows="angry"),
             dict(eyes="squint", mouth="o"), dict(eyes="shut", mouth="smirk"), dict(eyes="side", brows="up"),
             dict(eyes="wide", mouth="o", brows="up"), dict(mouth="grin"), dict(mouth="frown", brows="worried"),
             dict(eyes="up", mouth="closed"), dict(mouth="grit", brows="angry")]
    who_all = ("trump", "bibi", "obama")
    sheet = Image.new("RGB", (len(looks) * 44 + 4, len(who_all) * 44 + 4), C["wall"])
    for r, who in enumerate(who_all):
        for i, look in enumerate(looks):
            sheet.paste(h := head(who, **look), (4 + i * 44, 4 + r * 44), h)
    out = ROOT / "build" / "heads.png"
    out.parent.mkdir(exist_ok=True)
    scaled(sheet, 4).save(out)

    seated = [("trump", "spread", a, e) for a, e in [
        ("between", dict(mouth="pout", lean=2, bob=2)), ("steeple", dict()), ("acc0", dict(mouth="open")),
        ("acc2", dict(mouth="wide")), ("pinch", dict(mouth="o")), ("point", dict(brows="angry", mouth="open")),
        ("thumb", dict(mouth="grin")), ("shrug", dict(brows="up", mouth="pout")),
        ("cross", dict(mouth="pout", eyes="squint")), ("hold", dict(mouth="grin")), ("fist", dict(mouth="wide")),
        ("dance0", dict(mouth="o"))]]
    seated += [("bibi", "together", a, e) for a, e in [
        ("lap", dict(mouth="smirk")), ("finger", dict(mouth="open")), ("palm", dict(mouth="smirk", eyes="half")),
        ("point", dict(mouth="open", brows="angry")), ("cross", dict(mouth="smirk", eyes="shut")),
        ("hold", dict()), ("phone", dict(mouth="frown", brows="worried")), ("chin", dict(mouth="smirk"))]]
    standing = [("obama", "stand", a, e) for a, e in [("rest", dict(mouth="grin")), ("clear", dict(mouth="open")),
                                                      ("point", dict(mouth="grin")), ("mic", dict(mouth="open"))]]
    standing += [("announcer", "stand", "mic", dict(mouth="wide"))]
    cast = Image.new("RGB", (12 * 86 + 4, 2 * FH + FH_STAND + 12), C["wall"])
    for i, (who, legs, arms, e) in enumerate(seated):
        x, y = 4 + (i % 12) * 86, 4 + (i // 12) * (FH + 4)
        facing = -1 if who == "trump" else 1
        cast.paste(ch := chair(facing), (x, y), ch)
        img, _ = figure(who, legs, arms, facing=facing, **e)
        cast.paste(img, (x, y), img)
    for i, (who, legs, arms, e) in enumerate(standing):
        img, _ = figure(who, legs, arms, **e)
        cast.paste(img, (4 + i * 86, 2 * FH + 8), img)
    out = ROOT / "build" / "cast.png"
    scaled(cast, 2).save(out)
    print(out)
