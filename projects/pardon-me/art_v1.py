"""Sprites for Verse 1's gags: Bibi's giant fan, the gift jumbo jet, gold stars and hearts.

Each is a cached RGBA image outlined in ink, in the hall's palette.

    uv run python projects/pardon-me/art_v1.py     # -> build/art_v1.png, a sheet of them all
"""
import math
from functools import cache

import numpy as np
from PIL import Image, ImageDraw

from engine import C, INK, PRESS, SILK, Canvas, mix, text_width

BLADE, BLADE_SH = (190, 222, 250), (120, 170, 226)


def heart_pts(cx, cy, r, n=28):
    """Points round a heart (r is about half its width), for marker strokes."""
    pts = []
    for k in range(n + 1):
        a = 2 * math.pi * k / n
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * r / 16, cy + y * r / 16))
    return pts


HEART_ROWS = {
    3: [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."],
    5: ["..###...###..", ".#####.#####.", "#############", "#############", "#############", ".###########.",
        "..#########..", "...#######...", "....#####....", ".....###.....", "......#......"],
}


@cache
def heart(r=3, color="red"):
    """A filled heart sticker (r 3: 7 px wide, r 5: 13 px), outlined in ink."""
    rows = HEART_ROWS[r]
    s = Canvas(len(rows[0]) + 2, len(rows) + 2)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                s.px((x + 1, y + 1), color)
    s.px((2, 2), mix(C[color] if isinstance(color, str) else color, C["white"], 0.6))
    return s.done()


@cache
def gold_star(r=6):
    """A gold star sticker."""
    w = 2 * r + 4
    s = Canvas(w, w)
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((w / 2 + rr * math.cos(a), w / 2 + 0.5 + rr * math.sin(a)))
    s.poly(pts, "gold")
    s.poly([pts[9], pts[0], pts[1], (w / 2, w / 2 + 0.5)], "gold_hi")
    return s.done()


# --- line 0: the biggest fan ------------------------------------------------------------------------

FAN_C = (16, 22)        # the hub, in fan-sprite pixels
FAN_R = (13, 20)        # the cage's radii (seen three-quarter on, facing left)


def _blade(cx, cy, ang, squash, r0=2.5, r1=17.5, w=6.5):
    """One fan blade as a polygon: a petal from the hub out, turned to `ang` and squashed sideways."""
    side, back = [], []
    for k in range(9):
        s = k / 8
        r = r0 + (r1 - r0) * s
        half = w * math.sin(math.pi * min(1.0, s * 1.15)) ** 0.7 * (0.55 + 0.45 * s)
        for out, sign in ((side, 1), (back, -1)):
            u, v = r, sign * half * (1.0 if sign > 0 else 0.6)
            x = u * math.cos(ang) - v * math.sin(ang)
            y = u * math.sin(ang) + v * math.cos(ang)
            out.append((cx + x * squash, cy + y))
    return side + back[::-1]


@cache
def fan_head(step=0, blur=False):
    """Bibi's giant pedestal fan, turned three-quarters towards the left; `step` (0-11) turns the blades,
    `blur` spins them up. The hub is at FAN_C."""
    s = Canvas(40, 46)
    cx, cy = FAN_C
    rx, ry = FAN_R
    squash = rx / ry
    s.ell((20, 14, 34, 31), "steel_sh")                                   # the motor, behind the cage
    s.ell((22, 15, 33, 26), "steel")
    s.line([(25, 17), (30, 17)], (226, 230, 240))
    s.rect((25, 30, 29, 45), "steel_sh")                                  # the neck down to the pole
    s.line([(26, 30), (26, 45)], "steel")
    if blur:
        s.ell((cx - rx + 2, cy - ry + 2, cx + rx - 2, cy + ry - 2), mix(BLADE, C["screen_bg"], 0.35))
    ang0 = math.radians(step * 10)
    for k in range(3):
        a = ang0 + k * 2 * math.pi / 3
        s.poly(_blade(cx, cy, a, squash), BLADE_SH if blur else BLADE)
        s.poly(_blade(cx, cy, a, squash, r1=15, w=3.5), BLADE if blur else (226, 240, 255))
    d = s.d
    for k in range(10):                                                   # the grille's spokes
        a = k * math.pi / 5
        d.line([(cx + 3 * math.cos(a) * squash, cy + 3 * math.sin(a)),
                (cx + (rx - 1) * math.cos(a), cy + (ry - 1) * math.sin(a))], fill=s.c("steel_sh"))
    d.ellipse((cx - rx * 0.55, cy - ry * 0.55, cx + rx * 0.55, cy + ry * 0.55), outline=s.c("steel_sh"))
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=s.c("steel"), width=2)
    d.arc((cx - rx, cy - ry, cx + rx, cy + ry), 200, 300, fill=s.c((236, 240, 248)))
    s.ell((cx - 3, cy - 4, cx + 2, cy + 4), "steel")                      # the hub
    s.px((cx - 1, cy - 2), (236, 240, 248))
    s.rect((cx - 1, cy + 1, cx, cy + 2), "red")
    return s.done()


@cache
def fan_plate():
    """The plate on the fan's pole: whose fan it is."""
    w = text_width("BIBI", SILK) + 12
    s = Canvas(w + 2, 13)
    s.rect((1, 1, w, 11), "btie_sh")
    s.rect((2, 2, w - 1, 10), "btie")
    s.text((4, -2), "BIBI", "white")
    s.px((w - 4, 4), "red")
    s.px((w - 2, 4), "red")                      # a little heart
    s.rect((w - 4, 5, w - 2, 5), "red")
    s.px((w - 3, 6), "red")
    return s.done()


# --- line 2: a tip for a waiter ----------------------------------------------------------------------

@cache
def tip_jar():
    """A glass tip jar with a TIPS label, a few bills and one cigar in it; about 28x30."""
    s = Canvas(30, 31)
    glass, glass_sh = (196, 226, 236), (150, 190, 206)
    s.poly([(21, 1), (25, 0), (26, 2), (16, 16), (13, 15)], (150, 96, 52))     # the cigar, sticking out
    s.line([(22, 1), (25, 1)], (190, 130, 76))
    s.poly([(19, 5), (21, 4), (22, 6), (20, 7)], "red")
    s.rect((3, 11, 26, 29), glass)                                         # the jar
    s.rect((2, 9, 27, 11), glass_sh)                                       # its rim
    s.rect((4, 22, 25, 28), (110, 170, 110))                               # bills at the bottom
    s.line([(5, 23), (24, 22)], (150, 206, 150))
    s.px((8, 25), "gold")
    s.px((17, 26), "gold")
    s.px((21, 24), "gold")
    s.rect((4, 13, 25, 20), "white")                                       # the label
    s.text((5, 10), "TIPS", "red")
    s.line([(25, 21), (25, 28)], (236, 248, 252))                          # a glint
    return s.done()


@cache
def bow_tie():
    """A waiter's black bow tie."""
    rows = ["##...##", "###.###", "#######", "###.###", "##...##"]
    s = Canvas(9, 7)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                s.px((x + 1, y + 1), "black")
    s.px((4, 3), (70, 66, 80))
    return s.done()


# --- line 3: the gift jumbo jet ------------------------------------------------------------------------

@cache
def jumbo_jet():
    """A gold jumbo jet in side view, nose to the left, gift-wrapped: a red ribbon and a big bow. No livery."""
    s = Canvas(80, 34)
    body, sh, hi = "gold", "gold_sh", "gold_hi"
    s.poly([(60, 20), (68, 6), (75, 5), (74, 20)], sh)                     # the tail fin
    s.poly([(62, 19), (68, 8), (73, 7), (72, 19)], body)
    s.poly([(28, 22), (46, 22), (60, 28), (55, 28)], sh)                  # the near wing, swept back
    for ex, ey in ((30, 23), (44, 25)):                                   # two engines under it
        s.rect((ex, ey, ex + 10, ey + 4), "steel_sh")
        s.line([(ex + 1, ey), (ex + 10, ey)], "steel")
        s.rect((ex, ey + 1, ex + 1, ey + 3), INK)
    s.ell((3, 13, 22, 25), body)                                          # the nose
    s.rect((12, 14, 70, 24), body)                                        # the fuselage
    s.poly([(68, 14), (77, 15), (77, 19), (70, 24)], body)                # the tail cone
    s.ell((6, 9, 34, 20), body)                                           # the hump: the upper deck
    s.rect((12, 21, 70, 24), sh)
    s.ell((3, 19, 22, 25), sh)
    s.line([(14, 9), (30, 10)], hi)
    s.line([(34, 14), (68, 14)], hi)
    s.poly([(64, 18), (78, 17), (78, 19), (66, 20)], sh)                  # the tailplane
    for x in range(16, 66, 3):                                            # cabin windows
        s.px((x, 17), (70, 90, 130))
    for x in range(14, 28, 3):
        s.px((x, 12), (70, 90, 130))
    s.line([(6, 15), (9, 14)], (40, 60, 100))                             # the cockpit
    s.rect((40, 9, 42, 24), "red")                                        # the ribbon round the fuselage
    s.line([(40, 9), (40, 24)], "red_hi")
    s.ell((30, 0, 41, 9), "red")
    s.ell((41, 0, 52, 9), "red")             # the bow
    s.ell((33, 3, 39, 7), "red_sh")
    s.ell((43, 3, 49, 7), "red_sh")
    s.rect((39, 4, 43, 9), "red_hi")
    s.poly([(39, 9), (36, 13), (34, 13), (38, 8)], "red")                 # its tails
    s.poly([(43, 9), (47, 13), (45, 13), (42, 8)], "red")
    return s.done()


# --- lines 4-5: the dirty laundry ---------------------------------------------------------------------

LEATHER, LEATHER_SH, LEATHER_HI = (150, 96, 52), (110, 66, 38), (190, 130, 76)


@cache
def suitcase(open_=False):
    """A battered leather suitcase; open, its lid stands up behind and the laundry heaps over the edge."""
    s = Canvas(32, 26)
    if open_:
        s.poly([(3, 1), (28, 1), (30, 12), (1, 12)], LEATHER_SH)          # the lid, thrown back
        s.poly([(5, 3), (26, 3), (27, 11), (4, 11)], (140, 40, 50))        # its lining
        s.rect((1, 13, 30, 24), LEATHER)
        s.line([(1, 13), (30, 13)], LEATHER_HI)
        s.rect((1, 22, 30, 24), LEATHER_SH)
        for x, col in ((3, "white"), (8, "red"), (13, (120, 170, 230)), (18, "white"), (23, (240, 220, 120))):
            s.ell((x, 9, x + 7, 15), col)                                  # laundry heaped up
        s.px((10, 11), "white")
        s.px((12, 10), "white")
    else:
        s.rect((9, 6, 22, 9), INK)                                         # the handle
        s.d.rectangle((11, 8, 20, 9), fill=(0, 0, 0, 0))
        s.rect((1, 9, 30, 24), LEATHER)
        s.line([(1, 9), (30, 9)], LEATHER_HI)
        s.rect((1, 22, 30, 24), LEATHER_SH)
        for x in (7, 23):                                                  # straps and clasps
            s.rect((x, 9, x + 1, 24), LEATHER_SH)
            s.px((x, 12), "gold")
            s.px((x + 1, 12), "gold")
        s.rect((12, 14, 19, 18), (230, 220, 190))                          # a hotel sticker
        s.line([(13, 16), (18, 16)], "red")
    return s.done()


@cache
def laundry(kind):
    """One piece of dirty laundry: "shirt", "boxers", "sock" or "vest"."""
    stain = (200, 180, 110)
    if kind == "shirt":
        s = Canvas(13, 11)
        s.rect((1, 1, 11, 4), "white")
        s.rect((3, 1, 9, 9), "white")
        s.rect((3, 8, 9, 9), "paper_sh")
        s.px((6, 1), "paper_sh")
        s.px((5, 2), "btie")
        s.px((7, 2), "btie")
        s.px((6, 3), "btie")
        s.px((4, 6), stain)
        s.px((8, 5), stain)
    elif kind == "boxers":
        s = Canvas(15, 12)
        s.rect((1, 1, 13, 6), "red")
        s.rect((1, 6, 6, 10), "red")
        s.rect((8, 6, 13, 10), "red")
        s.rect((1, 1, 13, 2), "white")
        for x, y in ((3, 4), (8, 4), (11, 5), (3, 8), (11, 8)):
            s.px((x, y), "white")
            s.px((x + 1, y), "white")
    elif kind == "sock":
        s = Canvas(7, 11)
        s.rect((1, 1, 3, 7), "white")
        s.rect((1, 6, 5, 9), "white")
        s.line([(1, 2), (3, 2)], "red")
        s.line([(1, 4), (3, 4)], "blue")
        s.px((4, 9), stain)
    else:
        s = Canvas(10, 11)
        s.rect((1, 3, 8, 9), "white")
        s.rect((1, 1, 2, 3), "white")
        s.rect((7, 1, 8, 3), "white")
        s.ell((3, 4, 6, 7), stain)
    return s.done()


@cache
def iron():
    """A steam iron in side view, nose to the left."""
    s = Canvas(26, 17)
    s.poly([(1, 14), (7, 8), (24, 8), (24, 14)], (120, 170, 230))          # the body
    s.line([(7, 9), (23, 9)], (190, 220, 250))
    s.line([(3, 13), (23, 13)], (80, 130, 200))
    s.rect((1, 14, 24, 15), "steel")                                       # the sole plate
    s.line([(2, 15), (24, 15)], "steel_sh")
    s.line([(10, 8), (11, 2), (21, 2), (22, 8)], "black", 2)               # the handle
    s.rect((16, 10, 18, 11), "red")
    return s.done()


@cache
def blair_sign():
    """A brass-trimmed navy sign: the guest house's laundry service."""
    a, b = "BLAIR HOUSE", "LAUNDROMAT"
    w = max(text_width(a, SILK), text_width(b, SILK)) + 10
    s = Canvas(w + 2, 23)
    s.rect((1, 1, w, 21), "gold_sh")
    s.rect((2, 2, w - 1, 20), (36, 48, 90))
    s.line([(3, 3), (w - 2, 3)], (70, 84, 136))
    s.text(((w + 2) // 2, 0), a, "white", anchor="ma")
    s.text(((w + 2) // 2 + 1, 0), a, "white", anchor="ma")
    s.text(((w + 2) // 2, 9), b, "gold", anchor="ma")
    return s.done()


@cache
def press_camera():
    """A press photographer's camera with a flashgun on top, held up overhead."""
    s = Canvas(12, 11)
    s.rect((1, 4, 10, 9), "black")
    s.ell((4, 4, 9, 9), "steel_sh")
    s.ell((5, 5, 8, 8), (40, 50, 80))
    s.rect((2, 1, 6, 3), "steel")
    s.rect((3, 1, 5, 2), "white")          # the flashgun
    s.px((9, 5), "red")
    return s.done()


# --- line 8: the tariff board ------------------------------------------------------------------------------

BOARD_ROWS = (("CHINA", "34%"), ("EU", "20%"), ("JAPAN", "24%"), ("ISRAEL", "17%"))
BOARD_W, BOARD_H = 62, 50


@cache
def tariff_board():
    """The famous poster board: a navy header and a table of countries and rates (row k's text at
    y 13 + 9k, names from x 3, numbers right-aligned at x 61)."""
    s = Canvas(BOARD_W + 2, BOARD_H + 2)
    s.rect((1, 1, BOARD_W, BOARD_H), "white")
    s.rect((1, 1, BOARD_W, 11), (36, 48, 90))
    s.text((BOARD_W // 2 + 1, -1), "TARIFFS", "white", anchor="ma")
    s.text((BOARD_W // 2 + 2, -1), "TARIFFS", "white", anchor="ma")
    s.line([(2, 10), (BOARD_W - 1, 10)], "gold")
    for k, (name, rate) in enumerate(BOARD_ROWS):
        y = 13 + 9 * k
        s.text((3, y - 2), name, INK)
        s.text((61, y - 2), rate, "red" if name == "ISRAEL" else INK, anchor="ra")
        if k:
            s.line([(3, y - 1), (BOARD_W - 2, y - 1)], "paper_sh")
    s.rect((1, BOARD_H - 1, BOARD_W, BOARD_H), "paper_sh")
    return s.done()


# --- line 9: the flight in to beg ----------------------------------------------------------------------------

@cache
def small_plane():
    """A small white jet, nose to the left (no markings)."""
    s = Canvas(28, 12)
    s.poly([(20, 5), (23, 1), (26, 1), (26, 5)], "white")                  # the tail fin
    s.ell((1, 4, 8, 9), "white")
    s.rect((4, 4, 26, 8), "white")
    s.line([(5, 8), (25, 8)], "paper_sh")
    s.line([(3, 7), (25, 7)], (60, 110, 200))                              # a cheatline
    for x in range(8, 22, 3):
        s.px((x, 5), (70, 90, 130))
    s.px((3, 5), (40, 60, 100))
    s.poly([(10, 8), (16, 8), (19, 10), (14, 10)], "steel")                 # the wing
    s.rect((10, 10, 11, 10), INK)
    return s.done()


# --- line 11: ACME ------------------------------------------------------------------------------------------

@cache
def acme_crate(lid=True):
    """A wooden ACME crate, about 32x22; `lid` False leaves it open."""
    s = Canvas(34, 24)
    top = 4 if lid else 6
    s.rect((1, top, 32, 22), "desk")
    for y in (top + 5, top + 11):
        s.line([(1, y), (32, y)], "desk_sh")
    s.line([(1, top), (32, top)], "desk_hi")
    s.line([(4, top), (4, 22)], "desk_sh")
    s.line([(29, top), (29, 22)], "desk_sh")
    for x, y in ((2, top + 1), (31, top + 1), (2, 21), (31, 21)):
        s.px((x, y), INK)
    s.rect((8, 9, 25, 16), "desk_hi")
    s.text((17, 6), "ACME", INK, anchor="ma")
    s.text((18, 6), "ACME", INK, anchor="ma")
    if lid:
        s.rect((0, 2, 33, 4), "desk_sh")
        s.line([(0, 2), (33, 2)], "desk")
    else:
        s.rect((2, 6, 31, 7), INK)
    return s.done()


@cache
def crate_lid():
    s = Canvas(36, 5)
    s.rect((1, 1, 34, 3), "desk_sh")
    s.line([(1, 1), (34, 1)], "desk")
    return s.done()


@cache
def boxing_glove(facing=1):
    """A red boxing glove on the end of a spring, punching towards `facing`."""
    s = Canvas(15, 13)
    s.rect((1, 3, 4, 9), "white")                                          # the cuff
    s.ell((3, 1, 13, 11), "red")
    s.ell((5, 2, 11, 6), "red_hi")
    s.ell((4, 6, 9, 11), "red_sh")
    s.line([(6, 7), (9, 6)], "red_sh")                                     # the thumb
    img = s.done()
    return img.transpose(Image.FLIP_LEFT_RIGHT) if facing < 0 else img


# --- line 13: stuffing -------------------------------------------------------------------------------------

@cache
def pardon_stamp():
    """PARDONED, rubber-stamped in red on a cream slip, tilted up to the right."""
    red, cream = tuple(C["red"][:3]), (250, 238, 214)
    w, h = text_width("PARDONED", PRESS) + 10, 15
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w - 1, h - 1), fill=cream + (240,), outline=red + (255,))
    d.rectangle((2, 2, w - 3, h - 3), outline=red + (255,))
    d.text((5, 4), "PARDONED", font=PRESS, fill=red + (255,))
    a = np.array(im)
    inked = (a[..., 0] == red[0]) & (a[..., 1] == red[1]) & (a[..., 3] == 255)
    gaps = inked & (np.random.default_rng(17).random(inked.shape) < 0.06)  # the ink misses a few spots
    a[gaps] = cream + (240,)
    return Image.fromarray(a).rotate(8, resample=Image.NEAREST, expand=True)


@cache
def stuffing():
    """A wad of bread stuffing."""
    s = Canvas(12, 9)
    s.ell((1, 1, 10, 7), (196, 150, 90))
    for x, y, col in ((3, 2, (230, 196, 130)), (6, 3, (150, 104, 60)), (8, 2, (230, 196, 130)),
                      (4, 5, (110, 150, 70)), (7, 5, (150, 104, 60))):
        s.rect((x, y, x + 1, y + 1), col)
    return s.done()


if __name__ == "__main__":
    from engine import ROOT
    items = [fan_head(0), fan_head(4, True), fan_plate(), jumbo_jet(), gold_star(), heart(), heart(5), tip_jar(),
             bow_tie(), suitcase(), suitcase(True)] + [laundry(k) for k in ("shirt", "boxers", "sock", "vest")] + [
             iron(), blair_sign(), press_camera(), tariff_board(), small_plane(), acme_crate(), acme_crate(False),
             pardon_stamp(),
             crate_lid(), boxing_glove(), stuffing()]
    sheet = Image.new("RGB", (sum(i.width + 6 for i in items) + 6, 60), C["wall"])
    x = 6
    for i in items:
        sheet.paste(i, (x, 54 - i.height), i)
        x += i.width + 6
    out = ROOT / "build" / "art_v1.png"
    sheet.resize((sheet.width * 5, sheet.height * 5), Image.NEAREST).save(out)
    print(out)
