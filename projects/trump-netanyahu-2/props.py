"""Props for the gags: what the two men hold up, hand over and throw, and what flies past.

Every prop is a cached RGBA sprite drawn with the video's palette and outlined in ink. Text on props
is Silkscreen (5 px capitals); keep it to a word or two so it reads in the wide shot.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, SILK, Canvas, mirror  # noqa: F401
from pixelart import fx, pixel


def _text(f, xy, s, col="mk_black", anchor="la"):
    """Silkscreen on a prop canvas, glyph tops at y (its glyphs sit 4 px down their box)."""
    x, y = xy
    f.d.text((x, y - 4), s, font=SILK, fill=f.c(col), anchor=anchor)


def hole(f, box):
    """Punch a transparent hole (a mug's handle, a trophy's ears)."""
    f.d.ellipse(box, fill=(0, 0, 0, 0))


def text_w(s):
    return pixel.text_width(s, SILK)


def signature(f, x0, y, x1, col="mk_black"):
    """Trump's signature: a jagged seismograph of a scrawl."""
    pts, x, k = [], x0, 0
    while x <= x1:
        pts.append((x, y + (-3 if k % 2 else 2) + (k % 3 == 0)))
        x += 2
        k += 1
    f.line(pts, col)


# --- paper: folders, posters, notes ------------------------------------------------------------

@lru_cache(maxsize=None)
def folder(*lines, sig=True, w=42, h=30):
    """Trump's black leather folder held open to the cameras: a page with a word or two and a signature."""
    w = max(w, max(text_w(s) for s in lines) + 12) if lines else w
    h = max(h, 7 * len(lines) + 18)
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), "folder")
    f.line([(1, 1), (w - 2, 1)], "folder_hi")
    f.rect((3, 3, w - 4, h - 4), "paper")
    f.px((5, 5), "gold"); f.px((w - 6, 5), "gold")                              # the seal's corners
    y = 6
    for s in lines:
        _text(f, (w // 2, y), s, anchor="ma")
        y += 7
    if sig:
        signature(f, 7, h - 9, w - 8)
    return f.done()


@lru_cache(maxsize=None)
def poster(kind, w=46, h=34):
    """One of Bibi's foam boards, on its own (draw it held or on an easel)."""
    if kind == "bonespur":
        w = 76
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), "paper")
    f.line([(0, h - 1), (w - 1, h - 1)], "paper_sh")
    cx = w // 2
    if kind == "bomb":                                                        # the cartoon bomb with its red line
        f.ell((cx - 11, 10, cx + 11, 31), "mk_black")
        f.rect((cx - 3, 6, cx + 3, 10), "mk_black")
        f.line([(cx + 1, 6), (cx + 5, 2)], "mk_black")
        f.pxs([(cx + 6, 1), (cx + 7, 2), (cx + 5, 0)], "mk_red")
        f.line([(4, 15), (w - 5, 15)], "mk_red", w=2)
        _text(f, (cx + 12, 18), "90", "mk_red")
    elif kind == "weeks":                                                     # Iran is weeks away (since 1992)
        f.rect((5, 3, w - 6, 9), "mk_red")
        _text(f, (cx, 4), "IRAN", "paper", anchor="ma")
        _text(f, (cx, 13), "WEEKS", anchor="ma")
        _text(f, (cx, 20), "AWAY!", anchor="ma")
        f.line([(8, 28), (w - 9, 28)], "paper_sh")
    elif kind == "dome":                                                      # his Iron Dome, traced, coloured gold
        f.ell((6, 8, w - 7, 40), "paper_ln")
        f.ell((8, 10, w - 9, 40), "paper")
        f.ell((9, 11, w - 10, 40), "gold")                                    # crayon, over the lines
        for x in range(10, w - 10, 3):
            f.line([(x, 14), (x - 2, 28)], "gold_hi")
        f.rect((3, 27, w - 4, 30), "mk_green")
        _text(f, (cx, 3), "MY DOME", "mk_blue", anchor="ma")
    elif kind == "stars":                                                     # Donald's sticker chart
        _text(f, (cx, 3), "DONALD", "mk_blue", anchor="ma")
        for r in range(3):
            for k in range(5):
                x, y = 6 + k * 8, 12 + r * 7
                f.line([(x - 1, y + 5), (x + 6, y + 5)], "paper_sh")
                if (r, k) not in ((2, 3), (2, 4), (1, 4)):
                    star(f, x + 2, y + 2, "gold")
    elif kind == "bonespur":                                                  # Daddy's note (made wide)
        f.rect((0, 0, w - 1, h - 1), "paper")
        for y in range(8, h - 2, 5):
            f.line([(3, y), (w - 4, y)], "paper_ln")
        _text(f, (4, 3), "BONE SPURS.", "mk_blue")
        _text(f, (4, 11), "HE'LL GO WHEN", "mk_blue")
        _text(f, (4, 18), "HE'S OLDER.", "mk_blue")
        _text(f, (w - 5, 26), "-DAD", "mk_blue", anchor="ra")
    return f.done()


def star(f, cx, cy, col="gold", r=3):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    f.poly(pts, col)


@lru_cache(maxsize=None)
def gold_star(r=4):
    f = Canvas(2 * r + 3, 2 * r + 3)
    star(f, r + 1, r + 1, "gold", r)
    f.px((r + 1, r), "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def letter(heart=True, w=20, h=26, title="NOBEL"):
    """A letter on White House paper; the nomination ends in a heart."""
    w = max(w, text_w(title) + 6)
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), "paper")
    _text(f, (w // 2, 2), title, "mk_black", anchor="ma")
    for y in range(9, h - 9, 3):
        f.line([(3, y), (w - 4 - (y * 7) % 5, y)], "paper_sh")
    if heart:
        x, y = w // 2, h - 6
        f.ell((x - 4, y - 3, x, y + 1), "mk_red"); f.ell((x, y - 3, x + 4, y + 1), "mk_red")
        f.poly([(x - 4, y), (x + 4, y), (x, y + 4)], "mk_red")
    return f.done()


@lru_cache(maxsize=None)
def binder(*lines, w=30, h=36, col="paper"):
    """A white binder with a printed label (the Epstein files arrived in these)."""
    w = max(w, max(text_w(s) for s in lines) + 14)
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), col)
    f.rect((0, 0, 3, h - 1), "paper_sh")
    f.rect((7, 5, w - 4, 7 + 7 * len(lines)), "paper")
    f.line([(7, 5), (w - 4, 5)], "mk_black")
    for i, s in enumerate(lines):
        _text(f, ((w + 4) // 2, 8 + 7 * i), s, anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def ticket(word, w=40, h=14, col="gold"):
    w = max(w, text_w(word) + 16)
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), col)
    hole(f, (-3, h // 2 - 3, 2, h // 2 + 3)) if False else None
    f.line([(8, 1), (8, h - 2)], "gold_sh")
    _text(f, ((w + 8) // 2, h // 2 - 2), word, "ink", anchor="ma")
    return f.done()


# --- toys and gifts -------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def bb_gun():
    """A toy air rifle: wooden stock, black barrel, a little lever."""
    f = Canvas(32, 10)
    f.poly([(0, 4), (9, 2), (12, 2), (12, 6), (6, 9), (0, 8)], "wood")
    f.line([(1, 5), (8, 3)], "wood_hi")
    f.rect((12, 2, 31, 4), "black"); f.line([(12, 2), (30, 2)], "steel_sh")
    f.rect((13, 5, 20, 6), "steel_sh")
    f.line([(14, 7), (17, 9)], "steel")
    return f.done()


@lru_cache(maxsize=None)
def crate(word="AMMO", w=24, h=16, stamp="USA"):
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), "wood_hi")
    for y in (5, 10):
        f.line([(0, y), (w - 1, y)], "wood")
    f.line([(0, 0), (w - 1, h - 1)], "wood"); f.line([(0, h - 1), (w - 1, 0)], "wood")
    f.rect((3, 3, w - 4, 11), "wood_hi")
    _text(f, (w // 2, 4), word, "ink", anchor="ma")
    if stamp:
        _text(f, (w // 2, 11), stamp, "mk_red", anchor="ma") if h > 15 else None
    return f.done()


@lru_cache(maxsize=None)
def cigar():
    f = Canvas(14, 4)
    f.rect((0, 1, 12, 2), "wood"); f.line([(0, 1), (12, 1)], "wood_hi")
    f.rect((9, 0, 10, 3), "red")
    f.px((13, 1), "fire"); f.px((13, 2), "fire_red")
    return f.done()


@lru_cache(maxsize=None)
def cigar_box():
    """An open box of cigars, lid up."""
    f = Canvas(30, 20)
    f.rect((0, 0, 29, 7), "wood_sh"); f.rect((2, 1, 27, 6), "wood")                # the lid, open
    f.rect((10, 2, 19, 5), "gold"); f.px((14, 3), "red"); f.px((15, 3), "red")
    f.rect((0, 8, 29, 19), "wood"); f.line([(0, 8), (29, 8)], "wood_hi")
    for x in range(3, 27, 4):                                                    # the cigars
        f.rect((x, 9, x + 2, 15), "wood_sh"); f.px((x + 1, 11), "red")
    f.rect((8, 14, 21, 18), "gold"); f.line([(9, 16), (20, 16)], "gold_dk")
    return f.done()


@lru_cache(maxsize=None)
def jet(bow=True):
    """The 747 from Qatar, side on, with a bow on it."""
    f = Canvas(52, 20)
    f.ell((2, 8, 50, 15), "white")                                            # fuselage
    f.ell((40, 7, 51, 13), "white")                                           # the hump and nose
    f.poly([(2, 10), (0, 2), (6, 2), (12, 10)], (128, 30, 60))                # the maroon tail
    f.line([(4, 13), (48, 13)], (128, 30, 60))
    f.poly([(18, 12), (30, 12), (24, 19), (18, 19)], "steel")                # the wing
    f.rect((22, 16, 27, 18), "steel_sh")
    for x in range(14, 44, 3):
        f.px((x, 10), "blue_sh")
    f.px((46, 9), "blue_sh"); f.px((47, 9), "blue_sh")
    if bow:
        f.ell((24, 2, 30, 8), "red"); f.ell((30, 2, 36, 8), "red")
        f.rect((28, 6, 32, 9), "red_sh")
        f.line([(30, 6), (30, 14)], "red")
    return f.done()


@lru_cache(maxsize=None)
def laundry():
    """A laundry sack, stuffed, a sleeve and a sock hanging out."""
    f = Canvas(28, 28)
    f.ell((1, 6, 26, 27), "paper_sh")
    f.ell((3, 8, 24, 25), "paper")
    f.poly([(10, 7), (17, 7), (19, 2), (8, 2)], "paper_sh")
    f.line([(9, 6), (18, 6)], "steel_sh")
    f.poly([(19, 4), (26, 7), (24, 10), (18, 7)], "blue")                     # a shirt sleeve
    f.poly([(4, 3), (8, 5), (6, 9), (2, 7)], "mk_red")                         # a sock
    f.line([(8, 14), (12, 20)], "paper_sh"); f.line([(16, 12), (19, 19)], "paper_sh")
    return f.done()


@lru_cache(maxsize=None)
def turkey(beak="closed", medal=False):
    """The pardoned turkey: fanned tail, red wattle, and maybe the Nobel medal."""
    f = Canvas(34, 34)
    cols = ("wood", "orange", "tan", "wood_sh", "gold_sh")
    for k in range(9):                                                         # the fan
        a = math.radians(200 + k * 17.5)
        x, y = 15 + 13 * math.cos(a), 17 + 13 * math.sin(a)
        f.ell((x - 4, y - 4, x + 4, y + 4), cols[k % len(cols)])
    f.ell((8, 12, 25, 31), "wood")                                             # body
    f.ell((11, 16, 23, 29), "wood_hi")
    f.line([(14, 31), (13, 33)], "orange"); f.line([(19, 31), (20, 33)], "orange")   # legs
    f.ell((20, 6, 29, 16), "steel")                                            # head (blue-grey skin)
    f.px((25, 9), "ink")
    f.poly([(28, 10), (33, 11), (28, 12)] if beak == "closed" else [(28, 9), (33, 8), (29, 11), (33, 13), (28, 13)],
           "orange")
    f.ell((26, 12, 29, 19), "red")                                             # the wattle
    if medal:
        f.line([(18, 15), (22, 21), (26, 15)], "blue")
        f.ell((19, 20, 25, 26), "gold"); f.px((21, 22), "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def medal(ribbon=True):
    f = Canvas(16, 22)
    if ribbon:
        f.poly([(2, 0), (6, 0), (9, 12), (7, 12)], "blue")
        f.poly([(13, 0), (9, 0), (7, 12), (9, 12)], "blue_sh")
    f.ell((2, 9, 14, 21), "gold")
    f.ell((4, 11, 12, 19), "gold_sh")
    f.ell((5, 12, 11, 18), "gold")
    f.px((6, 13), "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def jello():
    f = Canvas(12, 12)
    f.poly([(1, 5), (10, 5), (9, 11), (2, 11)], "paper")
    f.ell((1, 1, 10, 7), "green")
    f.line([(3, 2), (6, 2)], "white")
    f.ell((5, 0, 7, 2), "red")                                                 # the cherry
    return f.done()


@lru_cache(maxsize=None)
def bottle():
    """A baby bottle: teat, collar, milk."""
    f = Canvas(8, 18)
    f.ell((2, 0, 5, 4), "tan_hi")
    f.rect((1, 4, 6, 5), "btie")
    f.rect((1, 6, 6, 17), "white"); f.rect((1, 10, 6, 17), "paper")
    for y in (8, 11, 14):
        f.px((5, y), "steel_sh")
    return f.done()


@lru_cache(maxsize=None)
def pacifier():
    f = Canvas(9, 7)
    f.ell((0, 0, 8, 6), "btie_hi")
    f.ell((3, 2, 5, 4), "tan_hi")
    f.line([(4, 0), (4, -1)], "btie")
    return f.done()


@lru_cache(maxsize=None)
def bonnet(facing=1):
    """A frilly baby bonnet, sized for a head canvas (40x40), facing right."""
    f = Canvas(40, 40)
    f.ell((3, -2, 34, 22), "white")
    f.ell((5, 0, 32, 20), (250, 214, 226))
    for x in range(4, 36, 3):                                                  # the frill
        f.ell((x - 2, 14 + (x % 2), x + 2, 19 + (x % 2)), "white")
    f.line([(10, 18), (12, 38)], (236, 150, 180)); f.line([(30, 16), (32, 36)], (236, 150, 180))
    img = f.done()
    return img if facing > 0 else mirror(img)


@lru_cache(maxsize=None)
def sippy():
    """The water glass, held in both hands."""
    f = Canvas(8, 12)
    f.poly([(0, 0), (7, 0), (6, 11), (1, 11)], (210, 230, 246))
    f.rect((1, 4, 6, 11), (150, 200, 240))
    f.line([(1, 1), (1, 9)], "white")
    return f.done()


@lru_cache(maxsize=None)
def ketchup(k=1.0):
    """Ketchup thrown at the wall, its drips running as k goes 0 -> 1."""
    f = Canvas(30, 40)
    f.ell((5, 4, 25, 18), "mk_red")
    for x, y in ((3, 8), (24, 4), (27, 13), (8, 2), (16, 1)):
        f.ell((x - 2, y - 2, x + 2, y + 2), "mk_red")
    for x, n in ((9, 14), (15, 22), (21, 10)):
        f.rect((x, 16, x + 1, 16 + int(n * k)), "red_sh")
    f.ell((10, 7, 14, 10), "red_hi")
    return f.done()


@lru_cache(maxsize=None)
def baby_balloon(phone=True):
    """The Trump Baby blimp: an orange baby in a nappy, the hair, a phone in one tiny hand."""
    f = Canvas(52, 56)
    f.ell((8, 18, 44, 52), "tskin")                                            # body
    f.ell((10, 34, 42, 52), "white"); f.line([(12, 42), (40, 42)], "paper_sh")  # the nappy
    f.ell((12, 2, 40, 28), "tskin")                                            # head
    f.ell((16, 10, 25, 17), "tring"); f.ell((27, 10, 36, 17), "tring")
    f.line([(18, 13), (22, 13)], "ink"); f.line([(29, 13), (33, 13)], "ink")
    f.line([(17, 9), (23, 11)], "thair_sh"); f.line([(29, 11), (35, 9)], "thair_sh")    # angry brows
    f.ell((22, 18, 30, 25), "mouth"); f.line([(23, 19), (29, 19)], "tooth")    # wailing
    f.poly([(10, 6), (20, 0), (34, 0), (44, 6), (40, 9), (30, 6), (20, 7), (14, 10)], "thair")
    f.poly([(36, 4), (46, 6), (44, 10), (40, 8)], "thair")
    f.ell((2, 26, 12, 36), "tskin"); f.ell((40, 26, 50, 36), "tskin")          # arms
    if phone:
        f.rect((44, 20, 48, 27), "black"); f.rect((45, 21, 47, 25), "lens")
    f.line([(26, 52), (26, 55)], "steel_sh")
    return f.done()


@lru_cache(maxsize=None)
def bunker_buster(wrapped=True):
    """A GBU-57, wrapped like a sweet."""
    f = Canvas(46, 14)
    f.ell((6, 2, 40, 12), "steel")
    f.line([(10, 4), (36, 4)], "white")
    f.rect((10, 9, 36, 11), "steel_sh")
    if wrapped:
        f.poly([(6, 7), (0, 1), (2, 7), (0, 13)], (240, 120, 180))
        f.poly([(40, 7), (46, 1), (44, 7), (46, 13)], (240, 120, 180))
        f.line([(14, 2), (16, 12)], (240, 120, 180)); f.line([(30, 2), (28, 12)], (240, 120, 180))
    _text(f, (23, 5), "GBU", "steel_sh", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def phone(receiver=True):
    """The Oval Office phone; the receiver can be off the hook."""
    f = Canvas(20, 12)
    f.poly([(1, 5), (18, 5), (19, 11), (0, 11)], (230, 222, 200))
    f.rect((5, 7, 14, 10), (196, 186, 160))
    for x in range(6, 14, 2):
        f.px((x, 8), "ink")
    if receiver:
        f.rect((2, 1, 17, 4), (230, 222, 200)); f.ell((0, 0, 5, 5), (230, 222, 200)); f.ell((14, 0, 19, 5), (230, 222, 200))
    return f.done()


@lru_cache(maxsize=None)
def receiver():
    f = Canvas(8, 16)
    f.rect((2, 2, 5, 13), (230, 222, 200))
    f.ell((0, 0, 7, 5), (230, 222, 200)); f.ell((0, 11, 7, 15), (230, 222, 200))
    return f.done()


@lru_cache(maxsize=None)
def golf_club():
    f = Canvas(8, 34)
    f.line([(5, 0), (4, 30)], "steel")
    f.rect((4, 0, 6, 6), "black")
    f.poly([(0, 30), (5, 29), (6, 33), (0, 33)], "steel_sh")
    return f.done()


@lru_cache(maxsize=None)
def golf_bag():
    f = Canvas(16, 34)
    for x, y in ((3, 0), (7, 2), (11, 0)):
        f.rect((x, y, x + 2, 10), "steel_sh"); f.rect((x - 1, y, x + 3, y + 3), "black")
    f.rect((1, 9, 14, 33), "red"); f.rect((1, 9, 14, 12), "white")
    f.rect((1, 30, 14, 33), "white"); f.line([(4, 13), (4, 29)], "red_sh")
    return f.done()


@lru_cache(maxsize=None)
def b2():
    """A B-2, from above: the flying wing."""
    f = Canvas(48, 14)
    f.poly([(24, 0), (47, 10), (42, 11), (38, 9), (34, 12), (30, 9), (24, 13), (18, 9), (14, 12), (10, 9),
            (6, 11), (1, 10)], (62, 64, 74))
    f.line([(24, 2), (24, 10)], (90, 92, 104))
    return f.done()


@lru_cache(maxsize=None)
def drone():
    """An armed drone, side on: long wings, the bulbous nose, a missile under the wing."""
    f = Canvas(40, 12)
    f.ell((4, 4, 34, 9), (150, 154, 160))
    f.ell((26, 2, 36, 9), (150, 154, 160))
    f.poly([(3, 6), (0, 0), (4, 0), (9, 6)], (130, 134, 140))
    f.line([(10, 6), (30, 6)], (110, 114, 120))
    f.rect((16, 9, 24, 10), "steel_sh")
    f.rect((1, 5, 2, 9), "steel_sh")
    return f.done()


@lru_cache(maxsize=None)
def chopper():
    f = Canvas(30, 14)
    f.line([(2, 2), (28, 2)], "ink")
    f.rect((14, 2, 15, 5), "ink")
    f.ell((8, 4, 22, 12), (70, 84, 60))
    f.rect((0, 6, 9, 8), (70, 84, 60)); f.rect((0, 4, 2, 9), (70, 84, 60))
    f.ell((16, 5, 21, 9), (150, 190, 220))
    f.line([(10, 13), (22, 13)], "ink")
    return f.done()


@lru_cache(maxsize=None)
def xray():
    """A foot, X-rayed: with bone spurs, and a gold star."""
    f = Canvas(26, 30)
    f.rect((0, 0, 25, 29), (24, 30, 48))
    f.poly([(8, 3), (12, 3), (13, 18), (21, 22), (22, 26), (6, 26), (6, 16)], (200, 214, 236))
    f.poly([(12, 18), (18, 20), (20, 24), (12, 24)], (150, 170, 200))
    for x, y in ((5, 18), (5, 22), (7, 26), (11, 27)):                          # the spurs
        f.px((x, y), "white")
    star(f, 20, 7, "gold", 4)
    return f.done()


@lru_cache(maxsize=None)
def bars(w=70, h=76):
    """Prison bars, dropped in front of someone."""
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, 3), "steel_sh")
    f.rect((0, h - 4, w - 1, h - 1), "steel_sh")
    for x in range(2, w - 2, 9):
        f.rect((x, 0, x + 2, h - 1), "steel")
        f.line([(x, 0), (x, h - 1)], "white")
    return f.done()


@lru_cache(maxsize=None)
def mug(face=True):
    """The mugshot mug: Trump's scowl on a coffee mug."""
    f = Canvas(16, 14)
    f.ell((10, 3, 16, 10), "white"); hole(f, (12, 5, 14, 8))
    f.rect((0, 1, 12, 13), "white"); f.ell((0, 0, 12, 3), "paper_sh")
    if face:
        f.rect((2, 3, 10, 11), (40, 50, 80))
        f.ell((3, 5, 9, 11), "tskin")
        f.poly([(2, 5), (6, 3), (10, 5), (9, 6), (3, 6)], "thair")
        f.line([(4, 7), (5, 7)], "ink"); f.line([(7, 7), (8, 7)], "ink")
        f.line([(5, 9), (7, 9)], "mouth")
    return f.done()


@lru_cache(maxsize=None)
def thermometer():
    f = Canvas(4, 14)
    f.rect((1, 0, 2, 10), "white")
    f.rect((1, 5, 2, 10), "red")
    f.ell((0, 9, 3, 13), "red")
    return f.done()


@lru_cache(maxsize=None)
def ball():
    f = Canvas(10, 10)
    f.ell((0, 0, 9, 9), "white")
    f.poly([(4, 3), (6, 3), (7, 5), (5, 7), (3, 5)], "ink")
    f.pxs([(1, 3), (8, 3), (2, 8), (7, 8), (5, 0)], "ink")
    return f.done()


@lru_cache(maxsize=None)
def trophy(word="FIFA"):
    """FIFA's peace prize: a gold trophy on a plinth."""
    f = Canvas(18, 26)
    f.ell((2, 0, 15, 10), "gold"); f.ell((4, 2, 13, 8), "gold_sh")
    f.ell((-1, 2, 5, 9), "gold"); f.ell((12, 2, 18, 9), "gold")
    hole(f, (1, 4, 3, 7)); hole(f, (14, 4, 16, 7))
    f.rect((7, 9, 10, 15), "gold_sh")
    f.rect((3, 15, 14, 25), "black")
    _text(f, (9, 18), word[:4], "gold", anchor="ma")
    f.px((5, 2), "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def sneakers():
    """Gold high-tops."""
    f = Canvas(22, 12)
    for x0 in (0, 11):
        f.poly([(x0, 11), (x0, 4), (x0 + 3, 1), (x0 + 6, 1), (x0 + 6, 6), (x0 + 10, 8), (x0 + 10, 11)], "gold")
        f.line([(x0, 10), (x0 + 10, 10)], "white")
        f.line([(x0 + 2, 3), (x0 + 5, 3)], "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def bible():
    f = Canvas(14, 17)
    f.rect((0, 0, 13, 16), "gold")
    f.rect((1, 1, 12, 15), "gold_sh")
    f.rect((6, 3, 7, 12), "gold_hi"); f.rect((3, 6, 10, 7), "gold_hi")
    f.line([(13, 1), (13, 16)], "white")
    return f.done()


@lru_cache(maxsize=None)
def potty():
    """A gold potty."""
    f = Canvas(22, 16)
    f.ell((0, 0, 21, 6), "gold")
    f.ell((3, 1, 18, 5), "gold_dk")
    f.poly([(2, 4), (19, 4), (17, 15), (4, 15)], "gold")
    f.line([(5, 7), (6, 13)], "gold_hi")
    f.ell((18, 6, 22, 12), "gold"); hole(f, (19, 8, 21, 10))
    return f.done()


@lru_cache(maxsize=None)
def pager(lit=False):
    """The gold pager Bibi gave Trump."""
    f = Canvas(14, 10)
    f.rect((0, 0, 13, 9), "gold")
    f.line([(0, 0), (13, 0)], "gold_hi")
    f.rect((2, 2, 11, 5), (150, 220, 120) if lit else (90, 120, 80))
    if lit:
        f.line([(3, 3), (10, 3)], (40, 70, 30))
    f.pxs([(3, 7), (6, 7), (9, 7)], "gold_dk")
    return f.done()


@lru_cache(maxsize=None)
def envelope():
    """The committee's envelope: gold, the flap folded down, a small seal at its point."""
    f = Canvas(22, 14)
    f.rect((0, 0, 21, 13), "gold")
    f.line([(0, 13), (21, 13)], "gold_sh")
    f.poly([(0, 0), (21, 0), (11, 8)], "gold_hi")
    f.line([(0, 0), (11, 8), (21, 0)], "gold_sh")
    f.ell((9, 7, 13, 11), "red")
    return f.done()


@lru_cache(maxsize=None)
def mic():
    """A handheld microphone, held head-up."""
    f = Canvas(6, 14)
    f.ell((0, 0, 5, 5), "steel")
    f.pxs([(1, 2), (3, 2), (2, 1), (2, 3)], "steel_sh")
    f.rect((2, 5, 3, 13), "black")
    return f.done()


@lru_cache(maxsize=None)
def sign(*lines, w=48, h=20, bg="blue", fg="white"):
    """A campaign placard."""
    f = Canvas(w, h + 10)
    f.rect((0, 0, w - 1, h - 1), bg)
    f.rect((w // 2 - 1, h, w // 2, h + 9), "wood")
    for i, s in enumerate(lines):
        _text(f, (w // 2, 3 + 7 * i), s, fg, anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def fridge(*items):
    """A fridge door with things stuck to it (for an inset)."""
    f = Canvas(44, 64)
    f.rect((0, 0, 43, 63), "white")
    f.line([(0, 22), (43, 22)], "paper_sh")
    f.rect((38, 6, 40, 16), "steel"); f.rect((38, 28, 40, 44), "steel")
    f.line([(1, 1), (1, 62)], "paper_sh")
    return f.done()


@lru_cache(maxsize=None)
def farm(with_trump=False):
    """A nice farm upstate: hills, a red barn, a tractor with a small white-haired man waving."""
    img = Image.new("RGB", (30, 52), (150, 196, 226))
    d = ImageDraw.Draw(img)
    d.ellipse((-10, 26, 24, 60), fill=(96, 160, 72))
    d.ellipse((8, 30, 44, 64), fill=(78, 140, 60))
    d.rectangle((3, 22, 13, 32), fill=(176, 40, 40)); d.polygon([(2, 22), (8, 16), (14, 22)], fill=(120, 30, 30))
    d.rectangle((6, 26, 9, 32), fill=(240, 236, 220))
    d.rectangle((16, 38, 25, 43), fill=(60, 140, 60)); d.ellipse((15, 41, 20, 46), fill=(30, 30, 30))
    d.ellipse((22, 39, 28, 46), fill=(30, 30, 30))
    d.rectangle((19, 33, 21, 38), fill=(40, 50, 90)); d.rectangle((19, 31, 21, 33), fill=(236, 200, 180))
    d.point((20, 30), fill=(250, 250, 250)); d.line([(22, 33), (24, 30)], fill=(236, 200, 180))
    if with_trump:
        d.rectangle((24, 34, 27, 40), fill=(40, 50, 96)); d.rectangle((24, 31, 27, 34), fill=(240, 140, 66))
        d.line([(24, 30), (28, 30)], fill=(252, 220, 110)); d.line([(26, 35), (26, 39)], fill=(216, 36, 46))
    d.ellipse((22, 3, 28, 9), fill=(255, 236, 140))
    return img


@lru_cache(maxsize=None)
def glove(color="red"):
    """A boxing glove, cuff down."""
    base, sh, hi = {"red": ("red", "red_sh", "red_hi"), "blue": ("blue", "blue_sh", "btie_hi")}[color]
    f = Canvas(11, 12)
    f.ell((0, 0, 10, 9), base)
    f.ell((6, 1, 10, 6), sh)
    f.rect((2, 8, 8, 11), "white")
    f.line([(2, 2), (4, 1)], hi)
    return f.done()


@lru_cache(maxsize=None)
def heart(r=3):
    f = Canvas(2 * r + 3, 2 * r + 2)
    f.ell((0, 0, r + 1, r + 1), "mk_red"); f.ell((r, 0, 2 * r + 1, r + 1), "mk_red")
    f.poly([(0, r // 2 + 1), (2 * r + 1, r // 2 + 1), (r, 2 * r)], "mk_red")
    f.px((1, 1), "red_hi")
    return f.done()


@lru_cache(maxsize=None)
def nobel_painting():
    """The Nobel medal, in oils."""
    img = Image.new("RGB", (31, 53), (40, 70, 60))
    d = ImageDraw.Draw(img)
    d.ellipse((2, 12, 28, 38), fill=C["gold_sh"]); d.ellipse((3, 13, 27, 37), fill=C["gold"])
    d.ellipse((6, 16, 24, 34), fill=C["gold_sh"])
    d.ellipse((10, 19, 20, 29), fill=C["gold_hi"])                                # Nobel's profile, roughly
    d.polygon([(14, 29), (19, 29), (21, 33), (12, 33)], fill=C["gold_hi"])
    d.point((18, 23), fill=C["gold_dk"])
    for y in (43, 47):
        d.line([(6, y), (24, y)], fill=C["gold_sh"])
    return img


@lru_cache(maxsize=None)
def soldier_painting():
    """A young soldier in olive drab, in a beret."""
    img = Image.new("RGB", (31, 53), (120, 130, 110))
    d = ImageDraw.Draw(img)
    d.polygon([(3, 53), (8, 33), (23, 33), (28, 53)], fill=(86, 96, 60))
    d.ellipse((10, 14, 21, 30), fill=(232, 190, 160))
    d.polygon([(8, 16), (13, 10), (24, 11), (24, 17)], fill=(140, 40, 60))   # the beret
    d.point((13, 21), fill=C["ink"]); d.point((18, 21), fill=C["ink"])
    d.line([(14, 26), (17, 26)], fill=(170, 110, 100))
    d.line([(12, 38), (18, 38)], fill=(200, 180, 90))
    return img


def zzz(img, x, y, a):
    """Sleepy Zs drifting up from (x, y)."""
    for k in range(3):
        p = (a * 0.8 + k / 3) % 1.0
        zx, zy = int(x + 6 * p + 2 * math.sin(p * 6)), int(y - 22 * p)
        s = 1 + k % 2
        d = ImageDraw.Draw(img)
        d.line([(zx, zy), (zx + 2 * s, zy), (zx, zy + 2 * s), (zx + 2 * s, zy + 2 * s)], fill=C["white"])
        d.line([(zx - 1, zy - 1), (zx + 2 * s + 1, zy - 1)], fill=INK)


def stink(img, x, y, a):
    """Wavy green stink lines rising off something."""
    d = ImageDraw.Draw(img)
    for k in range(3):
        x0 = x - 6 + 6 * k
        pts = [(x0 + int(2 * math.sin(a * 8 + j * 0.9 + k)), y - j) for j in range(0, 14, 2)]
        d.line(pts, fill=(130, 190, 80))


def sparkles(img, x, y, a, n=4, r=10, seed=0):
    for k in range(n):
        ang = seed + k * 2 * math.pi / n + a * 1.5
        fx.sparkle(img, int(x + r * math.cos(ang)), int(y + r * 0.7 * math.sin(ang)),
                   size=2 if int(a * 10 + k) % 3 else 3, color=C["white"])


@lru_cache(maxsize=None)
def crayon():
    f = Canvas(5, 16)
    f.rect((0, 3, 4, 15), "gold"); f.poly([(0, 3), (2, 0), (4, 3)], "gold_hi")
    f.rect((0, 7, 4, 11), "gold_sh")
    return f.done()


@lru_cache(maxsize=None)
def big_cigar():
    f = Canvas(22, 7)
    f.ell((0, 0, 20, 6), "wood"); f.line([(2, 1), (18, 1)], "wood_hi")
    f.rect((14, 0, 16, 6), "red"); f.px((15, 2), "gold")
    f.rect((19, 1, 21, 5), "ink"); f.px((21, 3), "fire")
    return f.done()


@lru_cache(maxsize=None)
def two_tickets():
    a, b = ticket("OSLO"), ticket("THE HAGUE", col="steel")
    img = Image.new("RGBA", (max(a.width, b.width) + 6, a.height + b.height + 2), (0, 0, 0, 0))
    img.paste(b, (6, a.height + 2), b)
    img.paste(a, (0, 0), a)
    return img


def redacted_page(a):
    """A page from the files: black bars, and a drawing nobody is allowed to see."""
    img = Image.new("RGB", (84, 64), (226, 220, 206))
    d = ImageDraw.Draw(img)
    d.rectangle((22, 2, 62, 62), fill=C["paper"])
    for y in range(8, 58, 6):
        d.rectangle((26, y, 58 - (y * 13) % 11, y + 2), fill=C["ink"])
    if a > 0.3:
        d.rectangle((16, 26, 68, 36), fill=C["red"])
        d.text((42, 27), "REDACTED", font=SILK, fill=C["white"], anchor="ma")
    return img


def ramp_inset(a):
    """West Point, 2020: the ramp, taken very carefully."""
    img = Image.new("RGB", (84, 64), (150, 190, 220))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 44, 84, 64), fill=(120, 150, 90))
    d.polygon([(4, 20), (30, 20), (76, 50), (50, 50)], fill=(200, 200, 196))
    d.line([(4, 18), (30, 18), (76, 48)], fill=(140, 140, 150))
    p = min(1.0, max(0.0, a) / 3.0)
    x, y = 14 + 44 * p, 18 + 27 * p
    step = int(a * 5) % 2
    d.rectangle((x - 2, y - 9, x + 2, y - 2), fill=C["suit"])
    d.rectangle((x - 2, y - 13, x + 2, y - 10), fill=C["tskin"])
    d.line([(x - 3, y - 14), (x + 3, y - 14)], fill=C["thair"])
    d.line([(x, y - 9), (x, y - 4)], fill=C["tie"])
    d.line([(x - 1, y - 2), (x - 1 - step, y)], fill=C["ink"]); d.line([(x + 1, y - 2), (x + 1 + step, y)], fill=C["ink"])
    return img


def fairway_inset(a):
    """The golf cam: a tiny man in a red cap kicks his ball towards the flag."""
    img = Image.new("RGB", (84, 64), (150, 200, 230))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 30, 84, 64), fill=(90, 160, 70))
    d.ellipse((50, 34, 82, 46), fill=(120, 190, 90))
    d.line([(70, 22), (70, 40)], fill=C["white"]); d.polygon([(70, 22), (78, 25), (70, 28)], fill=C["red"])
    kick = a > 0.3
    x, y = 20, 52
    d.rectangle((x - 3, y - 12, x + 3, y - 3), fill=C["suit"]); d.rectangle((x - 2, y - 17, x + 2, y - 13), fill=C["tskin"])
    d.rectangle((x - 3, y - 19, x + 3, y - 17), fill=C["red"])
    d.line([(x - 1, y - 3), (x - 2, y)], fill=C["ink"])
    d.line([(x + 1, y - 3), (x + 5, y - 5) if kick else (x + 2, y)], fill=C["ink"])
    p = min(1.0, max(0.0, a - 0.3) / 1.2)
    bx, by = lerp_pt((x + 6, y - 1), (68, 40), p)
    d.ellipse((bx - 1, by - 1, bx + 1, by + 1), fill=C["white"])
    return img


@lru_cache(maxsize=None)
def feet_inset(which=None, best=False):
    """The doctor's films: both feet, X-rayed. A question mark over one of them, or a gold star on each."""
    f = Canvas(84, 64)
    f.rect((0, 0, 83, 63), (24, 30, 48))
    for k, (x0, flip) in enumerate(((8, True), (48, False))):
        foot = [(8, 3), (12, 3), (13, 18), (21, 22), (22, 26), (6, 26), (6, 16)]
        foot = [((28 - x) if flip else x, y) for x, y in foot]
        f.poly([(x0 + x, 24 + y) for x, y in foot], (200, 214, 236))
        for x, y in ((5, 18), (5, 22), (7, 26)):
            f.px((x0 + ((28 - x) if flip else x), 24 + y), "white")
        _text(f, (x0 + 14, 4), "LR"[k], "paper", anchor="ma")
        if best:
            star(f, x0 + 14, 16, "gold", 4)
        elif which == k:
            _text(f, (x0 + 14, 12), "?", "mk_red", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def gift_bomb():
    """A cartoon bomb, gift-wrapped: a red ribbon and a bow."""
    f = Canvas(18, 21)
    f.ell((1, 5, 16, 20), "black")
    f.ell((4, 8, 7, 11), "steel_sh")
    f.rect((7, 3, 11, 6), "black")
    f.line([(11, 3), (14, 1)], "wood"); f.px((15, 0), "fire")
    f.rect((8, 6, 9, 20), "red")
    f.poly([(8, 3), (3, 0), (3, 6)], "red"); f.poly([(9, 3), (14, 0), (14, 6)], "red")
    f.rect((8, 2, 9, 4), "red_sh")
    return f.done()


@lru_cache(maxsize=None)
def turkey_portrait():
    """The new laureate's official portrait: the turkey, in the medal, on a dark green ground."""
    img = Image.new("RGB", (31, 53), (40, 56, 44))
    d = ImageDraw.Draw(img)
    d.ellipse((-8, 14, 38, 66), fill=(56, 76, 58))
    tk = turkey("closed", medal=True)
    img.paste(tk, (-2, 19), tk)
    d.rectangle((5, 3, 25, 9), fill=C["gold_sh"])
    d.text((15, 0), "2026", font=SILK, fill=C["gold_hi"], anchor="ma")
    return img


def checklist(ticks, pardon=False):
    """The laureate's record, ticked off: no wars, no trial, no drones."""
    img = Image.new("RGB", (84, 64), C["paper"])
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 83, 10), fill=C["gold_sh"])
    d.text((42, -3), "THE RECORD", font=SILK, fill=C["white"], anchor="ma")
    for i, s in enumerate(("NO WARS", "NO TRIAL", "NO DRONES")):
        y = 16 + i * 14
        d.rectangle((6, y, 14, y + 8), outline=C["ink"], fill=C["white"])
        d.text((20, y - 3), s, font=SILK, fill=C["ink"])
        if i < ticks:
            d.line([(7, y + 4), (10, y + 7), (16, y - 2)], fill=C["green"], width=2)
    return img


def handshake(cx, approach=1.0, pat=0.0, wince=False):
    """The handshake, close up (84x64): Bibi's hand from the left, Trump's tiny one from the right under a
    huge sleeve, clasped at x=cx. approach < 1 keeps the hands apart; pat (0-1) brings Trump's other hand
    down on top of the clasp."""
    img = Image.new("RGB", (84, 64), (232, 222, 190))
    d = ImageDraw.Draw(img)
    for x in range(2, 84, 7):                                            # the gold drapes behind
        d.line([(x, 0), (x, 63)], fill=(220, 204, 158))
    y = 38
    gap = (1 - approach) * 26
    bx, tx = cx - 7 - gap, cx + 3 + gap
    d.rectangle((-1, y - 8, bx - 4, y + 7), fill=C["bsuit"], outline=INK)            # Bibi's sleeve
    d.line([(0, y - 6), (bx - 6, y - 6)], fill=C["bsuit_hi"])
    d.rectangle((bx - 4, y - 6, bx, y + 5), fill=C["shirt"], outline=INK)
    d.rounded_rectangle((tx + 6, y - 11, 85, y + 10), radius=2, fill=C["suit"], outline=INK)   # Trump's sleeve
    d.line([(tx + 8, y - 9), (84, y - 9)], fill=C["suit_hi"])
    d.rectangle((tx + 2, y - 4, tx + 6, y + 3), fill=C["shirt"], outline=INK)
    d.rounded_rectangle((bx, y - 6, bx + 13, y + 5), radius=3, fill=C["bskin"], outline=INK)   # Bibi's hand
    for k in range(3):
        d.line([(bx + 9, y - 3 + 3 * k), (bx + 12, y - 3 + 3 * k)], fill=C["bskin_sh"])
    d.rounded_rectangle((tx - 4, y - 3, tx + 2, y + 2), radius=1, fill=C["tskin"], outline=INK)  # his tiny hand
    d.rectangle((bx + 6, y - 7, bx + 10, y - 3), fill=C["bskin"], outline=INK)       # Bibi's thumb, over it
    if wince:
        for k in range(3):
            d.line([(bx + 2 + 4 * k, y - 10), (bx + 1 + 4 * k, y - 14)], fill=INK)
    if pat > 0:                                                         # the other tiny hand, patting
        hx, hy = cx + 1, y - 8 - int(16 * (1 - pat))
        d.polygon([(84, hy - 20), (84, hy - 6), (hx + 8, hy + 2), (hx + 4, hy - 8)], fill=C["suit"], outline=INK)
        d.rectangle((hx + 2, hy - 3, hx + 6, hy + 2), fill=C["shirt"], outline=INK)
        d.rounded_rectangle((hx - 4, hy - 2, hx + 2, hy + 3), radius=1, fill=C["tskin"], outline=INK)
    return img


def lerp_pt(a, b, p):
    return a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p


def mug_inset():
    img = Image.new("RGB", (84, 64), (40, 50, 80))
    m = mug().resize((48, 42), Image.NEAREST)
    img.paste(m, (18, 12), m)
    return img


# --- effects ---------------------------------------------------------------------------------------

def puff(img, x, y, r, col=(236, 236, 240), seed=0):
    """A cartoon smoke puff: a few overlapping discs with an ink rim."""
    d = ImageDraw.Draw(img)
    discs = [(x + r * 0.6 * math.cos(k * 2.1 + seed), y + r * 0.5 * math.sin(k * 2.1 + seed), r * (0.55 + 0.1 * (k % 3)))
             for k in range(5)]
    for cx, cy, rr in discs:
        d.ellipse((cx - rr - 1, cy - rr - 1, cx + rr + 1, cy + rr + 1), fill=INK)
    for cx, cy, rr in discs:
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=tuple(col))


def bang(img, x, y, r, rot=0.0):
    fx.burst(img, x, y, r * 0.55, r, color=C["gold"], spikes=11, rot=rot, ink=INK)
    fx.burst(img, x, y, r * 0.3, r * 0.6, color=C["white"], spikes=9, rot=rot + 0.3, ink=C["gold"])


def word_pop(img, x, y, s, age, size=16, top=None, bottom=None, anchor="ma"):
    """Comic-book text that pops in: 'PEW PEW', 'BEEP', 'SAD!'."""
    from engine import PRESS, PRESS16
    fnt = PRESS16 if size == 16 else PRESS
    fx.pop_text(img, x, y, s, age, fnt=fnt, top=top or C["gold_hi"], bottom=bottom or C["orange"], outline=INK,
                anchor=anchor)


if __name__ == "__main__":
    from engine import ROOT, scaled
    items = [folder("PARDON"), folder("8 WARS", "ENDED"), folder("DEPT OF", "WAR"), poster("bomb"), poster("weeks"),
             poster("dome"), poster("stars"), poster("bonespur"), letter(), binder("EPSTEIN", "FILES"),
             ticket("OSLO"), ticket("THE HAGUE", col="steel"), bb_gun(), crate(), cigar(), cigar_box(), jet(),
             laundry(), turkey(), turkey("open", medal=True), medal(), jello(), bottle(), pacifier(), bonnet(),
             sippy(), ketchup(), baby_balloon(), bunker_buster(), phone(), receiver(), golf_club(), golf_bag(),
             b2(), drone(), chopper(), xray(), mug(), thermometer(), ball(), trophy(), sneakers(), bible(), potty(),
             pager(), pager(True), envelope(), mic(), sign("YES", "WE CAN"), gold_star()]
    sheet = Image.new("RGB", (8 * 58 + 4, ((len(items) + 7) // 8) * 60 + 4), C["wall"])
    for i, im in enumerate(items):
        x, y = 4 + (i % 8) * 58, 4 + (i // 8) * 60
        sheet.paste(im, (x, y), im)
    sheet.paste(farm(), (4 + 6 * 58, 4 + 6 * 60))
    out = ROOT / "build" / "props.png"
    scaled(sheet, 3).save(out)
    print(out)
