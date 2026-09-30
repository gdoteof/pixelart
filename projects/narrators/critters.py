"""The wildlife: chibi animals drawn on a Canvas facing right, outlined in ink, cached per pose.

Each returns an RGBA sprite whose feet (or belly) rest on the bottom row, centred,
unless noted. Mirror them with engine.mirror to face left.
"""
from functools import lru_cache

from engine import C, INK, Canvas, mix

GFACE, GFACE_HI = (44, 38, 46), (74, 66, 74)          # a gorilla's bare face
FUR, FUR_SH, FUR_HI, SILVER, SILVER_SH = C["fur"], C["fur_sh"], C["fur_hi"], C["silver"], (140, 142, 156)
REX, REX_SH, REX_HI, REX_BELLY = (98, 138, 76), (68, 100, 60), (136, 172, 96), (196, 196, 130)
WHALE, WHALE_SH, WHALE_HI, WHALE_BELLY = (92, 118, 150), (64, 86, 118), (134, 158, 186), (176, 192, 206)
RAT, RAT_SH, PINK = (136, 128, 132), (100, 94, 100), (232, 160, 170)


@lru_cache(maxsize=None)
def gorilla(pose="walk", face="calm"):
    """A silverback. pose: walk (knuckle-walking), stand, beat (fists on the chest), phone (a phone
    to his ear), sit. face: calm, roar, smug."""
    if pose == "walk":
        s = Canvas(40, 32)
        s.ell((3, 6, 28, 26), FUR)                                   # the great humped back
        s.ell((7, 6, 24, 15), SILVER)
        s.ell((9, 7, 20, 11), mix(SILVER, (255, 255, 255), 0.3))
        s.poly([(4, 18), (12, 18), (13, 30), (6, 30)], FUR)          # back leg
        s.rect((5, 29, 13, 30), GFACE)
        s.poly([(19, 12), (28, 12), (30, 29), (21, 30)], FUR)        # the front arm, huge
        s.line([(21, 14), (22, 28)], FUR_HI)
        s.rect((21, 27, 30, 30), GFACE)                              # knuckles
        s.pxs([(23, 28), (26, 28)], GFACE_HI)
        head = (24, 3)
    else:
        s = Canvas(34, 42)
        s.ell((5, 10, 27, 36), FUR)                                  # upright body
        s.ell((10, 22, 23, 35), GFACE_HI)                            # chest
        s.poly([(6, 32), (13, 32), (13, 41), (5, 41)], FUR)
        s.poly([(18, 32), (26, 32), (27, 41), (19, 41)], FUR)
        s.rect((4, 40, 13, 41), GFACE); s.rect((19, 40, 28, 41), GFACE)
        head = (13, 0)
        if pose == "stand":
            s.poly([(4, 14), (10, 14), (11, 34), (4, 34)], FUR)
            s.poly([(22, 14), (28, 14), (29, 34), (22, 34)], FUR)
            s.rect((4, 33, 11, 36), GFACE); s.rect((22, 33, 29, 36), GFACE)
        elif pose == "beat":
            s.poly([(4, 14), (10, 13), (17, 24), (12, 28)], FUR)
            s.poly([(28, 14), (22, 13), (16, 24), (21, 28)], FUR)
            s.ell((10, 23, 17, 29), GFACE); s.ell((17, 23, 24, 29), GFACE)
        elif pose == "phone":
            s.poly([(4, 14), (10, 14), (11, 34), (4, 34)], FUR)
            s.rect((4, 33, 11, 36), GFACE)
            s.poly([(22, 14), (28, 16), (29, 8), (25, 6)], FUR)      # arm up to the ear
            s.rect((26, 3, 30, 8), GFACE)
            s.rect((28, 1, 31, 10), (30, 30, 36)); s.px((29, 2), (120, 200, 255))   # the phone
        elif pose == "sit":
            s.poly([(4, 14), (10, 14), (11, 34), (4, 34)], FUR)
            s.poly([(22, 14), (28, 14), (29, 34), (22, 34)], FUR)
    hx, hy = head
    s.ell((hx, hy + 2, hx + 13, hy + 15), FUR)                       # head, with the crest on top
    s.poly([(hx + 3, hy + 3), (hx + 7, hy), (hx + 10, hy + 3)], FUR)
    s.ell((hx + 4, hy + 5, hx + 15, hy + 15), GFACE)                 # face
    s.line([(hx + 5, hy + 6), (hx + 14, hy + 6)], GFACE_HI)          # the brow ridge
    s.line([(hx + 5, hy + 7), (hx + 14, hy + 7)], FUR_SH)
    s.pxs([(hx + 8, hy + 8), (hx + 12, hy + 8)], "eye")
    s.pxs([(hx + 9, hy + 8), (hx + 13, hy + 8)], (150, 110, 60))
    s.pxs([(hx + 12, hy + 11), (hx + 14, hy + 11)], FUR_SH)          # nostrils
    if face == "roar":
        s.rect((hx + 8, hy + 12, hx + 14, hy + 15), "mouth")
        s.pxs([(hx + 8, hy + 12), (hx + 13, hy + 12), (hx + 8, hy + 15), (hx + 13, hy + 15)], "tooth")
    elif face == "smug":
        s.pxs([(hx + 9, hy + 14), (hx + 10, hy + 14), (hx + 11, hy + 14), (hx + 12, hy + 13)], GFACE_HI)
    else:
        s.line([(hx + 9, hy + 14), (hx + 13, hy + 14)], GFACE_HI)
    return s.done()


@lru_cache(maxsize=None)
def penguin(frame=0, tux=False):
    """An emperor penguin, waddling (frame 0/1)."""
    s = Canvas(16, 24)
    lean = 1 if frame else 0
    s.ell((2 + lean, 5, 13 + lean, 22), "black")
    s.ell((6 + lean, 8, 13 + lean, 21), "white")
    s.ell((4 + lean, 0, 12 + lean, 9), "black")
    s.poly([(12 + lean, 4), (15 + lean, 5), (12 + lean, 6)], "black")        # beak
    s.px((12 + lean, 5), (240, 140, 60))
    s.pxs([(9 + lean, 6), (10 + lean, 7), (10 + lean, 8), (11 + lean, 9)], "gold")  # the gold ear patch
    s.px((11 + lean, 10), "gold_hi")
    s.px((10 + lean, 3), "white")
    s.line([(3 + lean, 10), (2 + lean, 17)], (40, 40, 52))                   # flipper
    s.rect((4, 22, 7, 23) if frame else (5, 22, 8, 23), "black")
    s.rect((9, 22, 12, 23) if frame else (10, 22, 13, 23), "black")
    if tux:
        s.rect((11 + lean, 9, 12 + lean, 10), "red")                         # a bow tie, for the film
    return s.done()


@lru_cache(maxsize=None)
def trex(mouth="shut", frame=0):
    """A T. rex: huge head, tiny arms, tail out behind. mouth: shut, open, roar."""
    s = Canvas(64, 46)
    step = 2 if frame else 0
    s.poly([(0, 20), (24, 14), (30, 24), (6, 24)], REX)                      # tail
    s.ell((16, 12, 42, 34), REX)                                             # body
    s.ell((22, 22, 40, 34), REX_BELLY)
    s.poly([(24 - step, 30), (32 - step, 30), (30 - step, 44), (22 - step, 44)], REX_SH)   # far leg
    s.poly([(28 + step, 28), (38 + step, 28), (36 + step, 44), (28 + step, 44)], REX)      # near leg
    s.rect((26 - step, 43, 34 - step, 45), REX_SH); s.rect((33 + step, 43, 40 + step, 45), REX)
    s.poly([(34, 8), (40, 16), (38, 26), (30, 24)], REX)                     # neck
    s.ell((34, 0, 58, 16), REX)                                              # head
    s.rect((44, 4, 61, 12), REX)
    s.line([(36, 1), (56, 1)], REX_HI)
    s.pxs([(47, 4), (48, 4)], "eye"); s.px((46, 3), REX_SH)                  # eye and brow
    s.px((59, 5), REX_SH)                                                    # nostril
    if mouth == "shut":
        s.line([(44, 11), (61, 11)], REX_SH)
        for x in range(46, 61, 3):
            s.px((x, 10), "tooth")
    else:
        drop = 6 if mouth == "roar" else 3
        s.poly([(44, 11), (61, 11), (61, 12), (46, 12 + drop)], "mouth")
        s.poly([(44, 12 + drop), (58, 12 + drop), (58, 15 + drop), (44, 15 + drop)], REX)   # lower jaw
        for x in range(46, 61, 3):
            s.px((x, 12), "tooth"); s.px((x - 1, 11 + drop), "tooth")
    s.line([(40, 20), (44, 22)], REX_SH); s.px((45, 23), REX_SH)             # the tiny arm
    for x in range(20, 36, 4):
        s.px((x, 14), REX_HI)
    return s.done()


@lru_cache(maxsize=None)
def whale(frame=0):
    """A blue whale, side on, swimming right: long, mottled, a small fin far back, flukes."""
    s = Canvas(92, 30)
    lift = 2 if frame else 0
    s.poly([(0, 6 - lift), (8, 12), (0, 20 + lift), (4, 13)], WHALE_SH)      # flukes
    s.poly([(6, 12), (30, 7), (70, 5), (86, 9), (90, 15), (84, 22), (60, 25), (26, 20), (6, 15)], WHALE)
    s.poly([(50, 20), (84, 21), (78, 25), (58, 25)], WHALE_BELLY)            # pleated throat
    for x in range(56, 82, 4):
        s.line([(x, 21), (x + 2, 24)], WHALE_SH)
    s.poly([(28, 7), (34, 3), (36, 7)], WHALE_SH)                            # the small dorsal fin
    s.poly([(58, 20), (66, 20), (60, 28)], WHALE_SH)                         # flipper
    s.line([(70, 16), (88, 15)], WHALE_SH)                                   # mouth line
    s.px((74, 13), "eye")
    for k in range(14):
        x, y = 16 + (k * 37) % 60, 9 + (k * 13) % 9
        s.px((x, y), WHALE_HI)
    s.line([(40, 6), (70, 5)], WHALE_HI)
    return s.done()


@lru_cache(maxsize=None)
def rat(frame=0):
    s = Canvas(22, 10)
    s.ell((5, 2, 16, 9), RAT)
    s.ell((12, 3, 19, 8), RAT)
    s.px((19, 6), PINK); s.px((20, 6), PINK)                                 # nose
    s.ell((12, 1, 15, 4), PINK)                                              # ear
    s.px((16, 4), "eye")
    s.line([(5, 7), (1, 5 if frame else 8), (0, 3 if frame else 8)], PINK)   # tail
    s.pxs([(7, 9), (14, 9)] if frame else [(9, 9), (15, 9)], PINK)           # feet
    s.line([(6, 8), (15, 8)], RAT_SH)
    return s.done()


@lru_cache(maxsize=None)
def bird(frame=0, color=(236, 80, 60), wing=(250, 200, 60)):
    """A small bright bird in flight (wings up on frame 0, down on frame 1)."""
    s = Canvas(16, 12)
    s.ell((4, 4, 12, 9), color)
    s.ell((9, 2, 14, 7), color)
    s.poly([(14, 4), (16, 5), (14, 6)], "gold")
    s.px((12, 4), "eye")
    s.poly([(2, 6), (5, 5), (0, 9)], mix(color, INK, 0.3))                   # tail
    if frame:
        s.poly([(6, 6), (11, 6), (7, 11)], wing)
    else:
        s.poly([(6, 5), (11, 5), (5, 0)], wing)
    return s.done()


@lru_cache(maxsize=None)
def lion(mouth="shut"):
    """A lion, side on, facing right, with a dark mane. mouth: shut, open (breathing), roar."""
    s = Canvas(48, 30)
    s.poly([(0, 8), (3, 7), (8, 12), (6, 13)], C["lion_sh"])                 # tail
    s.ell((0, 5, 5, 10), C["mane_sh"])                                       # its tuft
    s.ell((6, 8, 36, 24), C["lion"])                                         # body
    s.line([(10, 21), (32, 21)], C["lion_sh"])
    for x0 in (9, 16, 27, 33):
        s.rect((x0, 20, x0 + 4, 28), C["lion"] if x0 % 2 else C["lion_sh"])
        s.rect((x0, 28, x0 + 5, 29), C["lion_sh"])
    s.ell((27, 0, 47, 22), C["mane"])                                        # the mane
    s.ell((29, 2, 44, 19), C["mane_sh"])
    s.ell((33, 4, 46, 17), C["lion"])                                        # face
    s.rect((40, 9, 47, 15), C["lion"])
    s.px((41, 7), "eye"); s.px((40, 6), C["lion_sh"])
    s.rect((45, 9, 47, 10), (80, 50, 40))                                    # nose
    if mouth == "shut":
        s.line([(42, 14), (46, 14)], (80, 50, 40))
    else:
        h = 4 if mouth == "roar" else 2
        s.rect((42, 13, 47, 13 + h), "mouth")
        s.pxs([(43, 13), (46, 13)], "tooth")
    return s.done()


if __name__ == "__main__":
    from PIL import Image

    from engine import ROOT
    row = [gorilla("walk"), gorilla("stand"), gorilla("beat", "roar"), gorilla("phone", "smug"), penguin(0),
           penguin(1, tux=True), trex(), trex("roar", 1), whale(), rat(), rat(1), bird(0), bird(1), lion(),
           lion("roar")]
    w = sum(im.width + 4 for im in row) + 4
    sheet = Image.new("RGB", (w, 52), (120, 150, 130))
    x = 4
    for im in row:
        sheet.paste(im, (x, 48 - im.height), im)
        x += im.width + 4
    out = ROOT / "build" / "critters.png"
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print(out)
