"""Caricatures of PewDiePie ("felix") and Sam Altman ("sam"), and the two assistants: ChatGPT's orb and Ajax.

The heads are three-quarter views facing right on a 40x40 canvas, drawn big because the faces carry the
caricature:

    felix   the blond hair swept up and back, the beard, the headphones, and a grin most of the time
    sam     the tousled brown fringe, the wide round eyes under high brows, the small polite mouth

Expressions are named parts:

    eyes    open squint half wide blink shut side up down
    brows   neutral angry up worried
    mouth   closed smile open wide o smirk grin frown grit

The bodies are pixelart.figure's layered rig: Felix in the black hoodie (hood up for the apology), Sam in
the grey crewneck (or the two polo shirts of 2008). `figure(who, ...)` returns the sprite and its anchors.
"""
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, Canvas, col, mirror  # noqa: F401
from pixelart.figure import Body, Rig

HW, HH = 40, 40
SKIN = {"felix": ("fskin", "fskin_sh", "fskin_dk", "fskin_hi"), "sam": ("sskin", "sskin_sh", "sskin_dk", "sskin_hi")}
# eye centres (near, far) and the mouth centre. Facing right in three-quarter view: the ear is on the
# left, then the near eye, the bridge of the nose, and the small far eye against the contour.
EYES = {"felix": ((19, 21), (28, 21)), "sam": ((19, 22), (28, 22))}
MOUTH = {"felix": (27, 33), "sam": (27, 34)}
LIP = {"felix": "flip", "sam": "slip"}
IRIS = {"felix": "eye_b", "sam": "eye_g"}


# --- the heads ------------------------------------------------------------------------------

def head_felix(f, hood=False):
    skin, sh, dk, hi = SKIN["felix"]
    if not hood:                                                         # the length at the back, to the collar
        f.poly([(5, 15), (2, 22), (2, 30), (5, 35), (9, 36), (10, 28), (8, 20)], "fhair_sh")
        f.line([(4, 22), (4, 31)], "fhair_dk")
    f.poly([(10, 12), (28, 10), (31, 14), (32, 21), (34, 25), (35, 28), (33, 29), (33, 32), (32, 35), (29, 38),
            (24, 39), (17, 38), (12, 35), (9, 30), (8, 23), (8, 16)], skin)
    f.poly([(8, 16), (10, 12), (13, 13), (12, 22), (13, 30), (15, 36), (12, 35), (9, 30), (8, 23)], sh)   # side plane
    f.line([(15, 26), (18, 27)], hi)                                     # the cheek
    f.poly([(26, 19), (28, 22), (33, 25), (34, 28), (32, 29), (28, 29), (26, 28)], skin)                 # the nose
    f.line([(27, 21), (31, 24)], hi); f.px((31, 28), dk); f.line([(28, 29), (32, 29)], sh)
    # the beard: full along the jaw and the chin, up to the sideburn, and the moustache
    f.poly([(9, 22), (10, 29), (13, 35), (18, 38), (25, 39), (30, 38), (33, 35), (34, 31), (32, 31), (30, 35),
            (25, 37), (20, 35), (16, 31), (14, 26), (12, 21)], "fbeard")
    f.poly([(22, 30), (25, 29), (32, 29), (33, 31), (24, 31)], "fbeard")
    f.pxs([(12, 30), (15, 34), (19, 37), (24, 38), (29, 37), (32, 34), (27, 30)], "fbeard_sh")
    f.pxs([(14, 28), (17, 33), (22, 36)], "fhair")
    if hood:
        return
    # the hair: swept up off the forehead and back, with some height
    f.poly([(7, 22), (4, 16), (4, 9), (7, 4), (12, 1), (19, 0), (26, 0), (32, 2), (35, 6), (35, 10), (32, 13),
            (28, 10), (23, 10), (17, 11), (13, 13), (11, 17), (10, 22)], "fhair")
    f.poly([(7, 22), (4, 16), (5, 11), (9, 12), (11, 17), (10, 22)], "fhair_sh")
    f.line([(28, 10), (33, 11)], "fhair_sh")                             # under the quiff
    f.line([(32, 3), (23, 2), (13, 4)], "fhair_hi")                      # strands, combed back
    f.line([(34, 7), (26, 5), (16, 7), (9, 11)], "fhair_hi")
    f.line([(30, 8), (21, 8), (13, 11)], "fhair_sh")
    f.pxs([(33, 4), (27, 1)], "white")
    # the headphones: the band over the top, the cup on the ear
    f.line([(8, 17), (9, 9), (13, 4), (19, 1)], "phones", w=2)
    f.line([(10, 9), (14, 4)], "phones_hi")
    f.ell((3, 16, 12, 29), "phones")
    f.ell((5, 18, 10, 27), "felix")
    f.ell((6, 20, 9, 25), "phones")
    f.px((6, 19), "felix_hi")


def hood_felix(f):
    """The hood up, for the apology: it covers the hair and the headphones and shades the brow."""
    f.poly([(5, 39), (2, 30), (1, 19), (3, 10), (8, 4), (15, 1), (23, 0), (30, 2), (34, 7), (35, 12), (32, 13),
            (27, 11), (20, 11), (14, 13), (11, 18), (10, 25), (11, 32), (14, 39)], "hood")
    f.poly([(5, 39), (2, 30), (1, 19), (3, 12), (7, 14), (6, 24), (8, 33), (11, 39)], "hood_sh")
    f.line([(32, 13), (27, 11), (20, 11), (14, 13), (11, 18), (10, 25), (11, 32)], "hood_sh")            # the rim
    f.line([(8, 6), (15, 3), (23, 2), (29, 4)], "hood_hi")


def head_sam(f):
    skin, sh, dk, hi = SKIN["sam"]
    f.poly([(11, 12), (28, 10), (31, 14), (32, 21), (34, 25), (35, 28), (33, 29), (33, 32), (31, 36), (27, 39),
            (21, 39), (15, 36), (11, 32), (9, 26), (8, 20), (9, 15)], skin)
    f.poly([(9, 15), (11, 12), (13, 13), (12, 22), (13, 30), (16, 37), (15, 36), (11, 32), (9, 26), (8, 20)], sh)
    f.ell((5, 19, 11, 28), skin)                                         # the ear
    f.line([(7, 21), (7, 26)], sh); f.pxs([(8, 22), (8, 25)], dk)
    f.line([(21, 39), (27, 39)], sh)                                     # under the chin
    f.line([(15, 28), (18, 29)], hi)
    f.poly([(26, 20), (28, 23), (33, 26), (34, 28), (32, 29), (28, 29), (26, 28)], skin)                 # the nose
    f.line([(27, 22), (31, 25)], hi); f.px((31, 28), dk); f.line([(28, 29), (32, 29)], sh)
    # the hair: short, tousled, the fringe falling forward in pieces
    f.poly([(7, 22), (5, 15), (6, 9), (9, 5), (13, 3), (16, 4), (19, 1), (23, 3), (26, 1), (30, 3), (33, 7),
            (34, 11), (32, 14), (30, 11), (27, 13), (24, 10), (20, 12), (16, 11), (13, 13), (11, 19), (10, 22)], "shair")
    f.poly([(7, 22), (5, 15), (6, 10), (9, 11), (11, 19), (10, 22)], "shair_sh")
    f.line([(30, 11), (27, 13), (24, 10), (20, 12), (16, 11)], "shair_sh")                                # the fringe's edge
    f.line([(12, 6), (17, 5)], "shair_hi"); f.line([(21, 4), (27, 4)], "shair_hi")
    f.line([(15, 9), (22, 8), (29, 8)], "shair_hi")
    f.pxs([(19, 2), (26, 2), (31, 5)], "shair_hi")


HEAD = {"felix": head_felix, "sam": head_sam}


# --- the faces ------------------------------------------------------------------------------

def sam_eyes(f, eyes):
    """Sam's eyes when they are open: wide and round, with white all the way round the iris."""
    _, sh, dk, _ = SKIN["sam"]
    for n, (cx, cy) in enumerate(EYES["sam"]):
        far = n == 1
        x0, x1 = (cx - 1, cx + 1) if far else (cx - 3, cx + 2)           # the far eye is foreshortened
        top = cy - (3 if eyes == "wide" else 2)
        f.rect((x0, top, x1, cy + 1 + (eyes == "wide")), "eye_w")
        f.line([(x0 - 1, top - 1), (x1 + 1, top - 1)], dk)               # the upper lid
        f.pxs([(x0 + 1, cy + 2 + (eyes == "wide")), (x1 - 1, cy + 2 + (eyes == "wide"))], sh)   # and what's under it
        ix = {"side": x1, "up": cx if far else cx - 1, "wide": cx if far else cx - 1}.get(eyes, x1 if far else cx)
        iy = top if eyes == "up" else cy - 1
        if eyes == "wide":                                               # a pinprick in all that white
            f.rect((ix, cy - 1, ix + (not far), cy), "eye")
            continue
        f.rect((ix - (0 if far or eyes == "side" else 0), iy, min(x1, ix + (0 if far else 1)), iy + 2 - (eyes == "up")), "eye_g")
        f.px((min(x1, ix + (0 if far else 1)), iy + 1 - (eyes == "up")), "eye")


def eyes_draw(f, who, eyes):
    _, sh, dk, _ = SKIN[who]
    if who == "sam" and eyes in ("open", "wide", "side", "up"):
        return sam_eyes(f, eyes)
    big = False
    for n, (cx, cy) in enumerate(EYES[who]):
        far = n == 1
        w = 1 if far else 2                                              # the far eye is foreshortened
        up = 1                                                           # how far the white opens above the centre
        if eyes == "open":
            f.rect((cx - w - big, cy - up, cx + w - 1 + (big and not far), cy + 1), "eye_w")
            f.rect((cx - (0 if far else 1 if big else 0), cy - up + big, cx + w - 1, cy + 1), IRIS[who])
            f.px((cx + w - 1, cy), "eye")
            f.line([(cx - w - 1 - big, cy - up - 1), (cx + w + (big and not far), cy - up - 1)], dk)     # the upper lid
        elif eyes == "squint":
            f.line([(cx - w - 1, cy + 1), (cx + w, cy)], "eye")
        elif eyes == "half":
            f.rect((cx - w, cy, cx + w - 1, cy + 1), "eye")
            f.line([(cx - w - 1, cy - 1), (cx + w, cy - 1)], dk); f.line([(cx - w, cy), (cx + w - 1, cy)], sh)
        elif eyes == "wide":
            f.rect((cx - w - 1, cy - 2 - big, cx + w, cy + 2), "eye_w")
            f.rect((cx, cy - 1, cx + w - 1, cy + 1), "eye")
        elif eyes == "blink":
            f.line([(cx - w - 1, cy + 1), (cx + w, cy + 1)], "ink")
        elif eyes == "shut":                                             # beaming, or smug: closed in an arc
            f.pxs([(cx - w - 1, cy + 1), (cx - w, cy), (cx + w - 1, cy), (cx + w, cy + 1)], "ink")
            f.line([(cx - w, cy), (cx + w - 1, cy)], "ink")
        elif eyes == "side":                                             # a glance across the call
            f.rect((cx - w - big, cy - up, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx + w - 1 - (not far), cy - up + big, cx + w - 1, cy + 1), "eye")
            f.line([(cx - w - 1 - big, cy - up - 1), (cx + w, cy - up - 1)], dk)
        elif eyes == "up":                                               # rolling them
            f.rect((cx - w - big, cy - up, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx - w + 1, cy - up, cx + w - 1, cy - up + (1 if big else 0)), "eye")
        elif eyes == "down":                                             # at the desk, or the floor
            f.rect((cx - w, cy, cx + w - 1, cy + 1), "eye_w")
            f.rect((cx - w + 1, cy + 1, cx + w - 1, cy + 1), "eye")
            f.line([(cx - w - 1, cy - 1), (cx + w, cy - 1)], dk)


def brows_draw(f, who, brows):
    color = {"felix": "fhair_dk", "sam": "shair"}[who]
    lift = 2 if who == "sam" else 0                                      # his sit high: always a little surprised
    for n, (cx, cy) in enumerate(EYES[who]):
        far = n == 1                                                     # the far brow sits across the nose
        a, b = (cx - 2, cx + 2) if far else (cx - 3, cx + 3)
        y = cy - 4 - lift
        inner, outer = (a, b) if far else (b, a)                         # the end nearest the nose first
        if brows == "angry":                                             # the inner ends pulled down
            pts = [(inner, y + 1 + lift), (outer, y - 1 + lift)]
        elif brows == "worried":                                         # the inner ends pushed up
            pts = [(inner, y - 1), (outer, y + 1)]
        elif brows == "up":
            pts = [(inner, y - 2), (outer, y - 1)]
        else:
            pts = [(inner, y), (outer, y)]
        f.line(pts, color)
        if who == "felix":                                               # his are thick
            f.line([(x, yy - 1) for x, yy in pts], color)


def mouth_draw(f, who, mouth):
    skin, sh, dk, hi = SKIN[who]
    lip = LIP[who]
    mx, my = MOUTH[who]
    if mouth == "closed":
        f.line([(mx - 3, my), (mx + 2, my)], "mouth")
    elif mouth == "smile":                                               # lips together, corners up
        f.line([(mx - 3, my), (mx + 2, my)], "mouth")
        f.pxs([(mx - 4, my - 1), (mx + 3, my - 1)], "mouth")
        if who == "sam":
            f.line([(mx - 2, my + 1), (mx + 1, my + 1)], lip)
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
def head(who, eyes="open", brows="neutral", mouth="closed", flush=0, hood=False):
    """A head sprite facing right (40x40, outlined); mirror it to face left."""
    f = Canvas(HW, HH)
    if who == "felix":
        head_felix(f, hood)
    else:
        head_sam(f)
    eyes_draw(f, who, eyes)
    brows_draw(f, who, brows)
    mouth_draw(f, who, mouth)
    if flush:                                                            # red cheeks
        cx, cy = EYES[who][0]
        f.pxs([(cx - 2, cy + 5), (cx, cy + 5), (cx + 2, cy + 5), (cx - 1, cy + 6), (cx + 1, cy + 6)], "flush")
    if hood:
        hood_felix(f)
    return f.done()


# --- the bodies -----------------------------------------------------------------------------

HEM = 95


def hoodie(f):
    """Felix's black hoodie: the hood bunched behind the neck, the drawstrings, a red zigzag on the chest."""
    f.ell((27, 37, 53, 50), "hood_sh")                                   # the hood, down
    f.poly([(22, 45), (34, 42), (46, 42), (54, 44), (58, 50), (59, 60), (59, 70), (58, HEM), (19, HEM), (17, 70),
            (17, 58), (18, 49)], "hood")
    f.poly([(54, 44), (58, 50), (59, 60), (59, 70), (58, HEM), (55, HEM), (55, 68), (55, 57), (52, 50)], "hood_sh")
    f.line([(21, 46), (32, 43)], "hood_hi")
    f.poly([(36, 40), (45, 40), (44, 46), (40, 48), (37, 46)], "fskin_sh")                                # the neck
    f.line([(35, 43), (40, 49), (46, 43)], "hood_hi")                                                    # the collar
    f.line([(38, 49), (37, 58)], "white"); f.line([(42, 49), (43, 58)], "white")                          # drawstrings
    for i, y in enumerate((60, 61, 60, 61, 60)):                                                         # the zigzag
        f.px((24 + 2 * i, y), "felix"); f.px((25 + 2 * i, y + (1 if i % 2 == 0 else -1) * 0), "felix_sh")
    f.rect((30, 74, 50, 86), "hood_sh")                                                                  # the pouch
    f.line([(30, 74), (50, 74)], "hood_hi")


def crewneck(f):
    """Sam's grey crewneck over a white T-shirt."""
    f.poly([(36, 38), (45, 38), (45, 45), (40, 47), (36, 45)], "sskin_sh")                                # the neck
    f.poly([(23, 45), (34, 42), (46, 42), (53, 44), (57, 50), (58, 60), (58, 70), (57, HEM), (21, HEM), (19, 70),
            (19, 58), (20, 49)], "sweater")
    f.poly([(53, 44), (57, 50), (58, 60), (58, 70), (57, HEM), (54, HEM), (54, 68), (54, 57), (51, 50)], "sweater_sh")
    f.line([(22, 46), (32, 43)], "sweater_hi")
    f.poly([(35, 42), (46, 42), (44, 46), (40, 48), (37, 46)], "tee")                                     # the T-shirt
    f.poly([(36, 41), (45, 41), (44, 45), (40, 46), (37, 45)], "sskin_sh")
    f.line([(34, 43), (37, 47), (40, 49), (44, 47), (47, 43)], "sweater_hi")                              # the ribbed collar
    for y in range(88, HEM, 2):
        f.line([(22, y), (56, y)], "sweater_sh")                                                         # the ribbed hem


def polos(f):
    """Two polo shirts at once, both collars popped: a keynote stage, 2008."""
    f.poly([(36, 38), (45, 38), (45, 45), (40, 47), (36, 45)], "sskin_sh")
    f.poly([(23, 45), (34, 42), (46, 42), (53, 44), (57, 50), (58, 60), (58, 70), (57, HEM), (21, HEM), (19, 70),
            (19, 58), (20, 49)], "polo1")
    f.poly([(53, 44), (57, 50), (58, 60), (58, 70), (57, HEM), (54, HEM), (54, 68), (54, 57), (51, 50)], "polo1_sh")
    f.poly([(36, 43), (45, 43), (41, 58)], "polo2")                                                      # the one underneath
    f.poly([(38, 43), (43, 43), (40, 49)], "sskin_sh")
    f.line([(40, 50), (40, 57)], "polo2_sh"); f.pxs([(40, 52), (40, 55)], "white")                        # its placket
    f.poly([(30, 44), (33, 33), (37, 37), (38, 46), (35, 50)], "polo1")                                  # the outer collar, up
    f.poly([(51, 44), (47, 33), (44, 37), (43, 46), (46, 50)], "polo1")
    f.poly([(34, 43), (36, 35), (38, 39), (39, 46)], "polo2")                                            # the inner collar, up
    f.poly([(47, 43), (45, 35), (43, 39), (42, 46)], "polo2")
    f.line([(33, 34), (36, 38)], "polo1_sh"); f.line([(47, 34), (44, 38)], "polo1_sh")
    f.rect((25, 55, 29, 58), "polo1_sh")                                                                 # a pocket crest


def _head(who, **fixed):
    return lambda **expr: head(who, **dict(expr, **fixed))


BODIES = {
    "felix": Body("felix", hoodie, _head("felix"), ("fskin", "fskin_sh"), "hood", shoulders=((20, 48), (57, 47)),
                  eye=EYES["felix"][0], mouth=MOUTH["felix"]),
    "felix_hood": Body("felix_hood", hoodie, _head("felix", hood=True), ("fskin", "fskin_sh"), "hood",
                       shoulders=((20, 48), (57, 47)), eye=EYES["felix"][0], mouth=MOUTH["felix"]),
    "sam": Body("sam", crewneck, _head("sam"), ("sskin", "sskin_sh"), "sweater", sleeve_w=5,
                shoulders=((22, 48), (56, 47)), eye=EYES["sam"][0], mouth=MOUTH["sam"]),
    "sam_polos": Body("sam_polos", polos, _head("sam"), ("sskin", "sskin_sh"), "polo1", sleeve_w=5,
                      shoulders=((22, 48), (56, 47)), eye=EYES["sam"][0], mouth=MOUTH["sam"]),
}
RIG = Rig(Canvas)
FW, FH = RIG.size


def figure(who, arms="desk", lean=0, bob=0, facing=1, held=None, outfit=None, **expr):
    """A figure (RGBA) and its anchors; `outfit` picks a variant body ("hood" for Felix, "polos" for Sam)."""
    body = BODIES[f"{who}_{outfit}" if outfit else who]
    return RIG.figure(body, arms, lean, bob, facing, held, **expr)


# --- the assistants ---------------------------------------------------------------------------

@lru_cache(maxsize=512)
def orb(r=14, mood="happy", talk=0, kind="gpt", ring=0):
    """An assistant as a glowing orb with a face, radius r. `talk` 0-3 opens its mouth; `ring` 0-2 adds
    rings of sound around it. mood: happy open wink sorry star flat hal. kind: gpt, ajax (bronze) or qwen."""
    core, glow, shade, dark = {"gpt": ("gpt", "gpt_glow", "gpt_sh", "gpt_dk"),
                               "ajax": ("ajax_hi", "ajax", "ajax_sh", "brown_sh"),
                               "qwen": ("white", "purple", "purple_sh", "purple_sh")}[kind]
    pad = 2 + 3 * ring
    n = 2 * r + 1 + 2 * pad
    f = Canvas(n, n)
    c0 = pad + r
    if mood == "hal":                                                    # a lens in a black plate: it can't do that
        f.ell((pad, pad, pad + 2 * r, pad + 2 * r), "black")
        f.ell((pad + 1, pad + 1, pad + 2 * r - 1, pad + 2 * r - 1), "grey_sh")
        f.ell((pad + 2, pad + 2, pad + 2 * r - 2, pad + 2 * r - 2), "black")
        k = max(2, r // 2)
        f.ell((c0 - k - 2, c0 - k - 2, c0 + k + 2, c0 + k + 2), "red_sh")
        f.ell((c0 - k, c0 - k, c0 + k, c0 + k), "red")
        f.ell((c0 - k // 2, c0 - k // 2, c0 + k // 2, c0 + k // 2), "orange")
        f.px((c0, c0), "gold_hi"); f.px((c0 - k // 2, c0 - k // 2 - 1), "red_hi")
        img = f.done()
    else:
        f.ell((pad, pad, pad + 2 * r, pad + 2 * r), glow)
        f.ell((pad + 1, pad + 1, pad + 2 * r - 2, pad + 2 * r - 2), core)
        f.d.arc((pad + 1, pad + 1, pad + 2 * r - 1, pad + 2 * r - 1), 20, 110, fill=col(shade) + (255,))  # the shaded limb
        f.px((c0 - r // 2, c0 - r // 2 - 1), "white"); f.px((c0 - r // 2 + 1, c0 - r // 2 - 2), "white")
        ex, ey = max(2, r // 3), c0 - max(1, r // 5)
        for sx in (-1, 1):
            x = c0 + sx * ex
            if mood == "happy":                                          # arcs: ^ ^
                f.pxs([(x - 1, ey + 1), (x, ey), (x + 1, ey + 1)], dark)
            elif mood == "wink" and sx > 0:
                f.line([(x - 1, ey + 1), (x + 1, ey + 1)], dark)
            elif mood == "sorry":                                        # eyes down, brows slanting out
                f.rect((x, ey + 1, x, ey + 2), dark)
                f.line([(x - sx, ey - 2), (x + sx, ey - 1)], dark)
            elif mood == "star":
                f.pxs([(x, ey - 1), (x - 1, ey), (x, ey), (x + 1, ey), (x, ey + 1)], "gold")
            elif mood == "flat":
                f.line([(x - 1, ey), (x + 1, ey)], dark)
            else:
                f.rect((x, ey - 1, x, ey + 1), dark)
        my = c0 + max(2, r // 3)
        if talk <= 0:
            if mood in ("sorry", "flat"):
                f.line([(c0 - 1, my), (c0 + 1, my)], dark)
            else:
                f.pxs([(c0 - 2, my - 1), (c0 - 1, my), (c0, my), (c0 + 1, my), (c0 + 2, my - 1)], dark)
        else:
            h = min(talk, 3)
            f.ell((c0 - 2, my - 1, c0 + 2, my - 1 + h), dark)
            if h > 1:
                f.px((c0, my + h - 1), "tongue")
        img = f.done()
    if ring:
        d = ImageDraw.Draw(img)
        for i in range(ring):
            rr = r + 3 + 3 * i
            d.arc((c0 - rr, c0 - rr, c0 + rr, c0 + rr), 200, 250, fill=col(glow) + (255,))
            d.arc((c0 - rr, c0 - rr, c0 + rr, c0 + rr), 290, 340, fill=col(glow) + (255,))
            d.arc((c0 - rr, c0 - rr, c0 + rr, c0 + rr), 20, 70, fill=col(glow) + (255,))
            d.arc((c0 - rr, c0 - rr, c0 + rr, c0 + rr), 110, 160, fill=col(glow) + (255,))
    return img


@lru_cache(maxsize=None)
def helmet(r=14):
    """Ajax's bronze helmet, with the nose guard and the red crest, to sit on an orb of radius r."""
    w = 2 * r + 9
    f = Canvas(w, 2 * r + 12)
    cx, top = w // 2, 9
    f.poly([(cx - 7, top + 1), (cx - 3, 1), (cx + 5, 0), (cx + 11, 4), (cx + 12, 10), (cx + 8, 6), (cx + 2, 5),
            (cx - 4, top + 2)], "red")                                                                   # the crest
    f.line([(cx - 4, 4), (cx + 4, 2), (cx + 10, 6)], "red_hi"); f.line([(cx - 6, top), (cx + 8, 8)], "red_sh")
    brow = top + r - r // 3 - 2                                                                         # above the orb's eyes
    f.d.chord((cx - r - 2, top, cx + r + 2, top + 2 * r + 4), 180, 360, fill=col("ajax") + (255,))       # the dome
    f.rect((cx - r - 2, brow - 3, cx + r + 2, brow), "ajax")
    f.rect((cx - r - 2, brow, cx - r + 2, top + 2 * r - 1), "ajax")                                       # the cheek pieces
    f.rect((cx + r - 2, brow, cx + r + 2, top + 2 * r - 1), "ajax")
    f.rect((cx - 1, brow, cx + 1, brow + r // 2 + 1), "ajax")                                             # the nose guard
    f.line([(cx - r - 1, brow), (cx + r + 1, brow)], "ajax_sh")                                           # the brow
    f.d.arc((cx - r, top + 2, cx + r, top + 2 * r), 200, 290, fill=col("ajax_hi") + (255,))
    f.line([(cx + r + 1, brow + 1), (cx + r + 1, top + 2 * r - 2)], "ajax_sh")
    f.d.rectangle((cx - r + 3, brow + 1, cx - 2, top + 2 * r + 4), fill=(0, 0, 0, 0))                     # the open face
    f.d.rectangle((cx + 2, brow + 1, cx + r - 3, top + 2 * r + 4), fill=(0, 0, 0, 0))
    f.d.rectangle((cx - r + 3, brow + r // 2 + 2, cx + r - 3, top + 2 * r + 4), fill=(0, 0, 0, 0))
    return f.done()


@lru_cache(maxsize=None)
def mini(who, mood="smile", facing=1):
    """A head small enough to stand in a picture (11x12): the hair and the beard carry it."""
    f = Canvas(13, 14)
    if who == "felix":
        f.rect((3, 3, 9, 10), "fskin")
        f.poly([(2, 5), (2, 2), (5, 0), (9, 0), (10, 2), (10, 4), (4, 4)], "fhair")                       # the quiff
        f.line([(2, 5), (2, 8)], "phones"); f.rect((1, 5, 2, 7), "felix")
        f.rect((3, 8, 9, 11), "fbeard"); f.rect((5, 7, 8, 8), "fskin")
        f.px((6, 5), "eye"); f.px((9, 5), "eye")
        if mood == "sad":
            f.line([(6, 10), (8, 10)], "mouth"); f.px((6, 6), "tear")
        elif mood == "yell":
            f.rect((6, 9, 8, 11), "mouth")
        else:
            f.line([(6, 9), (8, 9)], "tooth")
    else:
        f.rect((3, 3, 9, 11), "sskin")
        f.poly([(2, 5), (2, 2), (4, 0), (6, 1), (8, 0), (10, 2), (10, 5), (8, 3), (6, 5), (4, 4)], "shair")
        f.rect((5, 5, 6, 7), "eye_w"); f.rect((8, 5, 9, 7), "eye_w")
        f.px((6, 6), "eye"); f.px((9, 6), "eye")
        if mood == "shock":
            f.rect((6, 9, 8, 10), "mouth")
        elif mood == "sad":
            f.line([(6, 10), (8, 10)], "mouth")
        else:
            f.line([(6, 9), (8, 9)], "mouth")
    img = f.done()
    return img if facing > 0 else mirror(img)


if __name__ == "__main__":
    from engine import ROOT, scaled
    sheet = Image.new("RGB", (8 * 44 + 4, 2 * 44 + 4 + 2 * 100 + 60), (34, 38, 56))
    faces = [("open", "neutral", "closed"), ("open", "neutral", "smile"), ("open", "up", "grin"),
             ("squint", "angry", "open"), ("wide", "worried", "o"), ("half", "neutral", "smirk"),
             ("side", "angry", "frown"), ("shut", "up", "wide")]
    for r, who in enumerate(HEAD):
        for i, (eyes, brows, mouth) in enumerate(faces):
            h = head(who, eyes, brows, mouth)
            sheet.paste(h, (4 + i * 44, 4 + r * 44), h)
    poses = (("felix", "desk", None), ("felix", "bro", None), ("felix", "acc0", None), ("felix", "up2", "hood"),
             ("sam", "steeple", None), ("sam", "press", None), ("sam", "hush", None), ("sam", "shrug", "polos"))
    for i, (who, arms, outfit) in enumerate(poses):
        spr, _ = figure(who, arms, facing=1 if who == "felix" else -1, mouth="grin" if who == "felix" else "smile",
                        outfit=outfit)
        sheet.paste(spr, (4 + (i % 4) * 88, 92 + (i // 4) * 100), spr)
    x = 4
    for mood, kind, talk, ring in (("happy", "gpt", 0, 0), ("open", "gpt", 2, 1), ("star", "gpt", 3, 2), ("sorry", "gpt", 0, 0),
                                   ("wink", "gpt", 1, 0), ("hal", "gpt", 0, 0), ("happy", "ajax", 0, 0), ("open", "qwen", 1, 0)):
        o = orb(14, mood, talk, kind, ring)
        sheet.paste(o, (x, 296 + (22 - o.height // 2)), o)
        x += o.width + 4
    hl = helmet(14)
    o = orb(14, "happy", 0, "ajax").copy()
    sheet.paste(o, (x, 296 + 6), o); sheet.paste(hl, (x + o.width // 2 - hl.width // 2, 296 - 4), hl)
    x += 44
    for who, mood in (("felix", "smile"), ("felix", "sad"), ("felix", "yell"), ("sam", "smile"), ("sam", "shock")):
        m = mini(who, mood)
        sheet.paste(m, (x, 310), m)
        x += 16
    out = ROOT / "build" / "characters.png"
    scaled(sheet, 4).save(out)
    print(out)
