"""Sprites for Verse 3's gags (Trump's right of reply): the gold wall letters and the marquee T,
the science-fair trifold, its volcano and ribbon, a tumbleweed, the bottle cart and the
bottle-return machine, the meme coin and the CERTIFIED REAL seal. Cached RGBA images outlined in ink.

    uv run python projects/pardon-me/art_v3.py     # -> build/art_v3.png, a sheet of them all
"""
import math
from functools import cache

import numpy as np
from PIL import Image, ImageDraw
from pixelart.sprites import grow

from engine import INK, PRESS, PRESS16, PRESS24, C, Canvas, mix, outlined, rnd

MAROON = (112, 20, 34)
BULB_ON, BULB_OFF = (255, 252, 214), (150, 104, 40)
BOTTLE_COLS = ((58, 150, 84), (150, 96, 44), (170, 214, 232), (40, 120, 70), (190, 120, 60))
TUMBLE, TUMBLE_SH = (204, 168, 106), (140, 102, 60)

# 3x5 glyphs for lettering too small for the fonts
TINY = {"3": ["xxx", "..x", ".xx", "..x", "xxx"], "R": ["xx.", "x.x", "xx.", "x.x", "x.x"],
        "D": ["xx.", "x.x", "x.x", "x.x", "xx."]}


def tiny_text(s, x, y, color, canvas):
    for ch in s:
        for j, row in enumerate(TINY[ch]):
            for i, v in enumerate(row):
                if v == "x":
                    canvas.px((x + i, y + j), color)
        x += 4


def _glyph_mask(s, fnt, pad=2):
    """Boolean mask of text in a pixel font, with `pad` empty pixels all round."""
    w, h = int(fnt.getlength(s)) + 2 * pad, fnt.size + 2 * pad
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    d.text((pad, pad), s, font=fnt, fill=255)
    return np.array(m) > 0


# --- the name on the wall and the gold T ------------------------------------------------------

@cache
def gold_letter(ch):
    """A raised gold letter (PRESS16) with an ink outline and a shadow cast down-right on the wall."""
    a = _glyph_mask(ch, PRESS16)
    ys, xs = np.where(a.any(axis=1))[0], np.where(a.any(axis=0))[0]
    a = a[ys.min() - 2:ys.max() + 4, xs.min() - 2:xs.max() + 4]
    ring = grow(a)
    shadow = np.zeros_like(ring)
    shadow[1:, 1:] = ring[:-1, :-1]
    out = np.zeros(a.shape + (4,), np.uint8)
    out[shadow & ~ring] = C["wall_dk"] + (255,)
    out[ring] = INK + (255,)
    rows = np.arange(a.shape[0])[:, None]
    mid = (np.where(a.any(axis=1))[0].min() + np.where(a.any(axis=1))[0].max()) / 2
    out[a & (rows <= mid)] = C["gold"] + (255,)
    out[a & (rows > mid)] = C["gold_sh"] + (255,)
    up = np.zeros_like(a)
    up[1:] = a[:-1]
    out[a & ~up] = C["gold_hi"] + (255,)
    return Image.fromarray(out)


def bulb_points(r=17, n=16):
    """Where the marquee bulbs sit round the gold disc, relative to its centre."""
    return [(round((r - 2.5) * math.cos(2 * math.pi * k / n - math.pi / 2)),
             round((r - 2.5) * math.sin(2 * math.pi * k / n - math.pi / 2))) for k in range(n)]


@cache
def marquee_disc(r=17, lit=-1):
    """The gold T that replaces the UN emblem: a gold rim of marquee bulbs round a maroon field.
    `lit` = -1 lights every bulb, 0..2 lights every third (for a chase), -2 lights none."""
    size = 2 * r + 3
    s = Canvas(size, size)
    c = r + 1
    s.ell((c - r, c - r, c + r, c + r), "gold_sh")
    s.ell((c - r + 1, c - r + 1, c + r - 1, c + r - 2), "gold")
    s.ell((c - r + 5, c - r + 5, c + r - 5, c + r - 5), MAROON)
    s.ell((c - r + 6, c - r + 7, c + r - 5, c + r - 5), mix(MAROON, (0, 0, 0), 0.3))
    t = _glyph_mask("T", PRESS24, pad=0)
    ys, xs = np.where(t.any(axis=1))[0], np.where(t.any(axis=0))[0]
    t = t[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    th, tw = t.shape
    ox, oy = c - tw // 2, c - th // 2
    edge = grow(np.pad(t, 1)) & ~np.pad(t, 1)
    for y, x in zip(*np.where(edge)):
        s.px((ox + x - 1, oy + y - 1), INK)
    for y, x in zip(*np.where(t)):
        s.px((ox + x, oy + y), "gold_hi" if y < 2 else "gold" if y < th * 0.6 else "gold_sh")
    for k, (bx, by) in enumerate(bulb_points(r)):
        on = lit == -1 or (lit >= 0 and k % 3 == lit)
        s.rect((c + bx, c + by, c + bx + 1, c + by + 1), BULB_ON if on else BULB_OFF)
    return s.done()


# --- the science fair -------------------------------------------------------------------------------

@cache
def trifold():
    """A science-fair trifold board (about 48x34): BIBI's project, a red line, a chart and notes."""
    s = Canvas(50, 34)
    s.poly([(1, 4), (13, 1), (13, 31), (1, 29)], "paper_sh")              # the wings, angled back
    s.poly([(36, 1), (48, 4), (48, 29), (36, 31)], "paper_sh")
    s.rect((13, 0, 36, 31), "white")                                      # the centre panel
    s.rect((14, 1, 35, 8), "btie")
    s.text((16, -3), "BIBI", "white")
    s.line([(16, 18), (33, 18)], "mk_red", 1)                            # a red line, of course
    for i, (h, col) in enumerate(((5, "mk_blue"), (8, "mk_green"), (3, "mk_blue"))):
        s.rect((18 + i * 5, 27 - h, 20 + i * 5, 27), col)                # a little bar chart
    s.line([(16, 28), (33, 28)], "mk_black")
    s.ell((4, 8, 10, 14), "gold")                                         # left wing: the sun and a planet
    s.px((7, 18), "mk_blue"); s.px((10, 16), "mk_green")
    s.line([(4, 22), (11, 21)], "mk_black"); s.line([(4, 25), (11, 24)], "mk_black")
    for y in (8, 11, 14, 17, 20, 23):                                     # right wing: notes
        s.line([(38, y), (45, y + 1)], "paper_ln" if y % 2 else "mk_black")
    return s.done()


@cache
def volcano():
    """A papier-mache volcano on its cardboard base (30x20); the crater is at (12-17, 2-3)."""
    s = Canvas(30, 20)
    s.rect((1, 15, 28, 18), (70, 140, 70))
    s.line([(1, 18), (28, 18)], (48, 108, 52))
    s.poly([(4, 15), (12, 3), (17, 3), (25, 15)], (150, 96, 56))
    s.poly([(12, 3), (14, 3), (8, 15), (4, 15)], (186, 128, 76))            # the lit flank
    s.poly([(17, 3), (25, 15), (21, 15), (16, 5)], (118, 72, 44))           # the shaded one
    s.rect((12, 2, 17, 3), (70, 40, 34))
    return s.done()


LAVA, LAVA_HI = (236, 84, 76), (255, 178, 150)
ERUPT_UP = 8                                # the eruption overlay starts this many rows above the volcano


@cache
def eruption(step=12, fizz=0, n=12):
    """Red baking-soda foam welling out of the volcano's crater and running down its sides in drips, `step`
    of `n` of the way: an overlay in the volcano's coordinates, ERUPT_UP rows taller. `fizz` moves the
    bubbles."""
    p = step / n
    w, h = 30, 20 + ERUPT_UP
    yy, xx = np.mgrid[0:h, 0:w]
    yy = yy - ERUPT_UP                                                    # volcano rows
    rx, ry = 2.5 + 2 * p, 1.5 + 1.5 * p
    m = ((xx - 14.5) / rx) ** 2 + ((yy - (2.5 - 1.5 * p)) / ry) ** 2 <= 1   # the head of foam on the crater
    depth = 6 * p
    for x in range(w):
        top = 2 if 12 <= x <= 17 else 3 + 1.5 * (12 - x if x < 12 else x - 17)   # the cone's surface
        bottom = 3 + depth + 2.5 * rnd("drip", x // 2) * max(0.0, (p - 0.3) / 0.7)
        if bottom > top:
            m[int(top) + ERUPT_UP:int(bottom) + ERUPT_UP + 1, x] = True
    out = np.zeros((h, w, 4), np.uint8)
    out[grow(m) & ~m] = INK + (255,)
    out[m] = LAVA + (255,)
    up = np.zeros_like(m)
    up[1:] = m[:-1]
    out[m & ~up & (xx < 15)] = LAVA_HI + (255,)                             # the light on the top edge
    ys, xs = np.where(m)
    for k in range(5):                                                    # bubbles
        j = int(rnd("bubble", k, fizz) * len(ys))
        out[ys[j], xs[j]] = (255, 255, 255, 255)
    return Image.fromarray(out)


@cache
def rosette():
    """A third-place rosette: a yellow cockade marked 3RD on two ribbon tails (about 17x24)."""
    s = Canvas(19, 25)
    s.poly([(6, 10), (9, 12), (7, 23), (5, 21), (3, 23)], "gold_sh")
    s.poly([(10, 12), (13, 10), (16, 23), (14, 21), (12, 23)], "gold")
    for k in range(12):                                                   # the pleated edge
        a = 2 * math.pi * k / 12
        x, y = 9 + 7 * math.cos(a), 8 + 7 * math.sin(a)
        s.ell((x - 2, y - 2, x + 2, y + 2), "gold")
    s.ell((3, 2, 15, 14), "gold_hi")
    s.ell((4, 3, 14, 13), (255, 236, 150))
    tiny_text("3RD", 3, 6, INK, s)
    return s.done()


# --- the empty hall --------------------------------------------------------------------------------

@cache
def _tumbleweed_base():
    img = Image.new("RGBA", (25, 25), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(22):
        r = 4 + rnd("tw-r", i) * 6
        cx, cy = 12 + (rnd("tw-x", i) - 0.5) * 7, 12 + (rnd("tw-y", i) - 0.5) * 7
        a0 = rnd("tw-a", i) * 360
        col = TUMBLE if i % 3 else TUMBLE_SH
        d.arc((cx - r, cy - r, cx + r, cy + r), a0, a0 + 140 + rnd("tw-b", i) * 140, fill=col + (255,))
    return outlined(img, mix(INK, TUMBLE_SH, 0.35))


@cache
def tumbleweed(step=0, n=8):
    """A tumbleweed (about 25x25), turned to one of n steps of a roll."""
    return _tumbleweed_base().rotate(-step * 360 / n, resample=Image.NEAREST)


# --- the machines that walked out ---------------------------------------------------------------------

@cache
def prompter(step=0):
    """A glass teleprompter on its stand (16x33), facing right, out for a walk on two little legs; `step`
    0 or 1 swaps the stride."""
    s = Canvas(16, 33)
    s.poly([(2, 1), (13, 4), (13, 13), (2, 10)], (70, 96, 130))             # the glass, tilted to the speaker
    s.line([(3, 3), (8, 10)], (190, 214, 236))
    for k in range(3):                                                    # its lines of text
        s.line([(6 + k, 4 + 2 * k), (11, 6 + 2 * k)], (150, 176, 210))
    s.rect((5, 12, 11, 15), "black")                                     # the monitor under the glass
    s.rect((7, 16, 8, 24), "steel")                                      # the pole
    s.rect((4, 24, 11, 25), "steel_sh")                                  # the foot of the stand
    if step % 2:
        s.line([(6, 26), (4, 29)], "black"); s.line([(9, 26), (11, 29)], "black")
        s.rect((2, 30, 5, 31), "black"); s.rect((10, 30, 13, 31), "black")
    else:
        s.line([(6, 26), (6, 29)], "black"); s.line([(9, 26), (9, 29)], "black")
        s.rect((5, 30, 8, 31), "black"); s.rect((8, 30, 11, 31), "black")
    return s.done()


# --- the bottle hustle ------------------------------------------------------------------------------

@cache
def bottle(i=0):
    """One empty bottle (5x12), neck up, with a glint."""
    s = Canvas(5, 12)
    col = BOTTLE_COLS[i % len(BOTTLE_COLS)]
    s.rect((1, 5, 3, 10), col)
    s.rect((2, 1, 2, 4), col)
    hi = mix(col, (255, 255, 255), 0.55)
    s.line([(1, 6), (1, 8)], hi)
    s.px((2, 1), hi)
    return s.done()


@cache
def cart():
    """A shopping cart heaped with empty bottles, standing up in rows with more piled on top (34x38),
    rolling right: the handle trails."""
    heap = Image.new("RGBA", (34, 38), (0, 0, 0, 0))
    dy = 9
    rows = ((6 + dy, (12, 17, 22)), (10 + dy, (9, 13, 17, 21, 25)), (13 + dy, (7, 11, 15, 19, 23, 27)),
            (16 + dy, (10, 14, 18, 22, 26)))
    for r, (bottom, xs) in enumerate(rows):                               # the top of the heap first
        for k, x in enumerate(xs):
            i = 7 * r + k
            tilt = (rnd("cb-l", i) - 0.5) * (80 if r == 0 else 36)
            b = bottle(i).rotate(tilt, resample=Image.NEAREST, expand=True)
            heap.alpha_composite(b, (x - b.width // 2, bottom - b.height + int(rnd("cb-y", i) * 2)))
    s = Canvas(34, 38)
    s.poly([(7, 10 + dy), (30, 10 + dy), (27, 20 + dy), (10, 20 + dy)], (30, 92, 56))  # bottles through the wire
    for i in range(6):
        s.rect((10 + i * 3, 12 + dy + i % 2 * 3, 11 + i * 3, 16 + dy + i % 2 * 3), BOTTLE_COLS[i % 3])
    for x in range(9, 30, 3):                                             # the wire basket
        s.line([(x, 10 + dy), (x - (x - 18) // 6, 20 + dy)], "steel")
    for y in (10, 15, 20):
        s.line([(7 + (y - 10) // 3, y + dy), (30 - (y - 10) // 3, y + dy)], "steel")
    s.line([(7, 10 + dy), (3, 6 + dy)], "steel_sh", 2)                    # the handle, with its red grip
    s.line([(2, 4 + dy), (3, 8 + dy)], "red", 2)
    s.line([(10, 22 + dy), (28, 22 + dy)], "steel_sh")                    # the frame and the wheels
    s.line([(11, 20 + dy), (11, 24 + dy)], "steel_sh"); s.line([(26, 20 + dy), (26, 24 + dy)], "steel_sh")
    s.rect((9, 25 + dy, 12, 27 + dy), "black"); s.rect((24, 25 + dy, 27, 27 + dy), "black")
    heap.alpha_composite(s.done())
    return heap


@cache
def machine():
    """A bottle-return machine (about 26x40): a red header with the deposit, the round bottle hole, a
    display, the receipt slot."""
    s = Canvas(27, 41)
    s.rect((1, 1, 25, 39), "steel")
    s.rect((22, 1, 25, 39), "steel_sh")
    s.rect((1, 1, 25, 10), "red")
    s.line([(1, 10), (25, 10)], "red_sh")
    s.text((4, -1), "10¢", "white")
    s.ell((5, 13, 17, 25), (40, 150, 80))                                  # the bottle hole, ringed green
    s.ell((7, 15, 15, 23), "black")
    s.rect((9, 17, 11, 21), (36, 120, 72)); s.px((10, 16), (36, 120, 72))  # a bottle icon in the hole
    s.rect((5, 27, 17, 29), (30, 40, 60)); s.line([(6, 28), (11, 28)], (120, 240, 140))
    s.rect((5, 32, 17, 33), "black")                                      # the receipt slot
    s.rect((1, 37, 25, 39), "steel_sh")
    return s.done()


# --- the meme coin ------------------------------------------------------------------------------------

@cache
def coin(frame=0):
    """A gold coin (7x7) stamped with a T, at one of four spin frames (0 face-on .. 3 edge-on)."""
    w = (7, 5, 3, 1)[frame % 4]
    s = Canvas(w + 2, 9)
    x0 = 1
    s.ell((x0, 1, x0 + w - 1, 7), "gold_sh")
    if w >= 3:
        s.ell((x0, 1, x0 + w - 2, 6), "gold")
    if w >= 5:
        cx = x0 + w // 2 - 1
        s.line([(cx - 1, 3), (cx + 1, 3)], "gold_sh"); s.line([(cx, 3), (cx, 5)], "gold_sh")
        s.px((x0 + 1, 2), "gold_hi")
    return s.done()


# --- crawling back -------------------------------------------------------------------------------------------

@cache
def fingers():
    """Four fingertips hooked over the far edge of a desk (11x7)."""
    s = Canvas(11, 7)
    s.rect((1, 1, 9, 5), "bskin")
    for x in (3, 5, 7):
        s.line([(x, 2), (x, 5)], "bskin_sh")
    s.line([(1, 1), (9, 1)], mix(C["bskin"], (255, 255, 255), 0.35))
    return s.done()


# --- the hair --------------------------------------------------------------------------------------------

@cache
def seal(angle=-10):
    """The CERTIFIED REAL stamp: two lines in a double-ruled red box, the ink speckled."""
    red = C["mk_red"] + (255,)
    w, h = 80, 32
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w - 1, h - 1), outline=red, width=2)
    d.rectangle((3, 3, w - 4, h - 4), outline=red)
    d.text((w // 2, 6), "CERTIFIED", font=PRESS, fill=red, anchor="ma")
    d.text((w // 2, 14), "REAL", font=PRESS16, fill=red, anchor="ma")
    arr = np.array(im)
    gone = np.random.default_rng(34).random(arr.shape[:2]) < 0.1
    arr[gone, 3] = 0
    return Image.fromarray(arr).rotate(angle, resample=Image.NEAREST, expand=True)


if __name__ == "__main__":
    from engine import ROOT
    items = ([gold_letter(ch) for ch in "TRUMP"] + [marquee_disc(), marquee_disc(lit=1), trifold(), volcano(),
             eruption(4), eruption(12), rosette(), tumbleweed(0), tumbleweed(1), prompter(0), prompter(1), bottle(0),
             bottle(1), cart(), machine(), fingers()]
             + [coin(k) for k in range(4)] + [seal()])
    sheet = Image.new("RGB", (sum(i.width + 6 for i in items) + 6, 60), C["wall"])
    x = 6
    for i in items:
        sheet.paste(i, (x, 54 - i.height), i)
        x += i.width + 6
    out = ROOT / "build" / "art_v3.png"
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)
    print(out)
