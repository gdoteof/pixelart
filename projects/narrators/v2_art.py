"""Sets and sprites for Verse 2 (THE BBC REDEMPTION): the cell, the mugshot wall, the cave, the museum,
the void where the light switch is, the creation line, Dickie's park, the awards, the ship, the war
room, the Cretaceous and London.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import (C, INK, PRESS, PRESS16, SILK, H, W, Canvas, blend, blend_poly, clamp, mask, mirror, mix, rnd,
                    scaled, text_width, vgrad)
from pixelart import pixel
from sets import frond, heaven_static, leaf_blob, scene

# --- the cell ------------------------------------------------------------------------------------

CELL = {"wall": (138, 132, 126), "wall_sh": (112, 106, 104), "wall_hi": (160, 154, 146), "mortar": (120, 114, 110),
        "floor": (92, 88, 88), "floor_hi": (112, 108, 106), "bar": (56, 58, 66), "bar_hi": (126, 130, 142),
        "bunk": (74, 88, 76), "mattress": (196, 190, 172), "blanket": (120, 96, 72), "pan": (222, 224, 228),
        "light": (255, 238, 196), "window": (190, 214, 236)}
CELL_FLOOR = 136
BUNK_SEAT = (70, 118)                 # where you sit on the bunk (thigh height)
DOOR = (144, 208)                     # the span of bars that slides open
AT_BARS = (176, 134)                  # standing at the cell door
POSTER = (220, 54, 246, 90)           # the pin-up on the back wall (the tunnel is behind it)
CALENDAR = (184, 44, 212, 82)


@lru_cache(maxsize=1)
def cell_static():
    img = Image.new("RGB", (W, H), CELL["wall"])
    d = ImageDraw.Draw(img)
    for r, y in enumerate(range(6, CELL_FLOOR, 10)):                  # breeze blocks
        d.line([(0, y), (W, y)], fill=CELL["mortar"])
        for x in range(-10 + (r % 2) * 12, W, 24):
            d.line([(x, y - 9), (x, y)], fill=CELL["mortar"])
    blend_poly(img, [(0, 0), (W, 0), (W, 16), (0, 16)], (40, 36, 40), 0.35)          # ceiling shade
    d.rectangle((0, CELL_FLOOR, W, H), fill=CELL["floor"])
    d.line([(0, CELL_FLOOR), (W, CELL_FLOOR)], fill=CELL["floor_hi"])
    d.rectangle((140, 26, 168, 46), fill=CELL["window"])                               # a high window
    for x in (147, 154, 161):
        d.line([(x, 26), (x, 46)], fill=CELL["bar"])
    d.rectangle((139, 25, 169, 47), outline=CELL["wall_sh"])
    # the bunk
    d.rectangle((22, 112, 108, 120), fill=CELL["mattress"])
    d.rectangle((22, 116, 108, 120), fill=CELL["blanket"])
    d.rectangle((20, 120, 110, 123), fill=CELL["bunk"])
    for x in (22, 106):
        d.rectangle((x, 123, x + 2, CELL_FLOOR), fill=CELL["bunk"])
    d.ellipse((24, 108, 38, 114), fill=(236, 232, 220))                                # pillow
    # the toilet
    d.rectangle((272, 116, 288, 120), fill=CELL["pan"])
    d.polygon([(274, 120), (286, 120), (284, CELL_FLOOR), (276, CELL_FLOOR)], fill=CELL["pan"])
    d.rectangle((282, 100, 290, 116), fill=CELL["pan"])
    return img


@lru_cache(maxsize=2)
def pinup(lifted=False):
    """The poster on the cell wall: a silverback, glamorously lit (Rita Hayworth was busy)."""
    from critters import gorilla
    x0, y0, x1, y1 = POSTER
    s = Canvas(x1 - x0 + 3, y1 - y0 + 3)
    s.rect((1, 1, x1 - x0 + 1, y1 - y0 + 1), (236, 196, 150))
    s.rect((2, 2, x1 - x0, 12), (200, 90, 110))
    g = gorilla("sit", "smug")
    g = g.resize((g.width * 2 // 3, g.height * 2 // 3), Image.NEAREST)
    s.img.alpha_composite(g, ((x1 - x0 + 3 - g.width) // 2, y1 - y0 - g.height + 1))
    s.text(((x1 - x0) // 2 + 2, 3), "HUBBA", "white")
    img = s.done()
    if lifted:
        img = img.crop((0, 0, img.width, 10))
    return img


def cell(c):
    img = cell_static().copy()
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = POSTER
    if c.get("tunnel", 0) > 0:                         # the hole behind the poster
        r = int(4 + 8 * min(1.0, c.get("tunnel")))
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 + 4
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(30, 26, 26))
        d.ellipse((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), fill=(12, 10, 12))
    p = pinup(bool(c.get("tunnel", 0)))
    img.paste(p, (x0 - 1, y0 - 1), p)
    if c.get("cosy"):
        cosy(img)
    # the window's light falls across the cell
    sweep = c.get("sun", 0.0)
    blend_poly(img, [(140 + sweep, 46), (168 + sweep, 46), (212 + sweep * 3, CELL_FLOOR),
                     (160 + sweep * 3, CELL_FLOOR)], CELL["light"], 0.22)
    return img


def cosy(img):
    """What a few decades inside does for a cell: lamp, fern, rug, a sampler and the good teapot."""
    d = ImageDraw.Draw(img)
    d.rectangle((6, 128, 60, 136), fill=(150, 60, 60))                                 # rug
    for x in range(8, 60, 6):
        d.point((x, 132), fill=(230, 190, 90))
    d.rectangle((112, 118, 128, CELL_FLOOR), fill=(150, 104, 66))                      # crate side table
    d.line([(112, 118), (128, 118)], fill=(190, 140, 90))
    d.rectangle((118, 104, 120, 118), fill=(60, 50, 40))                               # lamp
    d.polygon([(113, 104), (125, 104), (122, 96), (116, 96)], fill=(236, 200, 110))
    blend_poly(img, [(112, 104), (126, 104), (140, 136), (98, 136)], (255, 226, 150), 0.25)
    d.rectangle((22, 74, 56, 98), fill=(234, 226, 206))                               # the sampler
    d.rectangle((22, 74, 56, 98), outline=(120, 80, 50))
    pixel.text(img, (39, 74), "HOME", SILK, (170, 60, 70), shadow=None, anchor="ma")
    pixel.text(img, (39, 81), "SWEET", SILK, (60, 110, 70), shadow=None, anchor="ma")
    pixel.text(img, (39, 88), "HOME", SILK, (170, 60, 70), shadow=None, anchor="ma")
    d.polygon([(250, 136), (262, 136), (260, 124), (252, 124)], fill=(180, 100, 60))    # a potted fern
    for k in range(5):
        frond(d, 256, 124, 12, 0.6 + k * 0.5, C["leaf"] if k % 2 else C["leaf_hi"], width=3)
    d.ellipse((124, 110, 130, 116), fill=(236, 236, 240))                             # teapot on the crate
    d.rectangle((113, 112, 116, 117), fill=(236, 236, 240))


def cell_bars(c):
    """The bars in front of the camera; the door section slides by c.vars['door'] (0 shut, 1 open)."""
    img = c.world
    d = ImageDraw.Draw(img)
    slide = int(c.get("door", 0.0) * 62)
    shake = c.get("rattle", 0)
    top, bot = 12, H

    def bar(x):
        d.rectangle((x, top, x + 2, bot), fill=CELL["bar"])
        d.line([(x + 1, top), (x + 1, bot)], fill=CELL["bar_hi"])

    for x in range(0, W, 16):
        if DOOR[0] <= x < DOOR[1]:
            bar(x + slide + shake)
        else:
            bar(x)
    for y in (top, 126):
        d.rectangle((0, y, DOOR[0] - 2, y + 3), fill=CELL["bar"])
        d.rectangle((DOOR[1] + 2, y, W, y + 3), fill=CELL["bar"])
        d.rectangle((DOOR[0] - 2 + slide + shake, y, DOOR[1] + slide + shake, y + 3), fill=CELL["bar"])
        d.line([(0, y + 1), (W, y + 1)], fill=CELL["bar_hi"])


scene("v2_cell", near=cell_bars,
      shots={"bars": (176, 104, 12), "bunk": (80, 102, 12), "door": (170, 100, 9), "wall": (214, 76, 12)},
      cast={"david": dict(x=AT_BARS[0], y=AT_BARS[1], facing=1, outfit="prison")})(cell)


# --- the mugshot --------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def mug_static():
    img = Image.new("RGB", (W, H), (176, 186, 172))
    d = ImageDraw.Draw(img)
    for k, y in enumerate(range(60, 152, 8)):                          # the height chart
        d.line([(60, y), (260, y)], fill=(120, 130, 118))
        if k % 2 == 0:
            s = f"{7 - k // 2}'"
            pixel.text(img, (52, y - 3), s, SILK, (80, 90, 80), shadow=None, anchor="ra")
            pixel.text(img, (266, y - 3), s, SILK, (80, 90, 80), shadow=None)
    d.rectangle((0, 152, W, H), fill=(110, 110, 112))
    return img


def mugshot(c):
    return mug_static().copy()


scene("v2_mug", shots={"mug": (166, 112, 12)},
      cast={"david": dict(x=160, y=152, facing=1, outfit="prison", arm="hold", gesture=False)})(mugshot)


@lru_cache(maxsize=None)
def placard(top="B.B.C.", bottom="No. 1952"):
    w = max(text_width(top, SILK), text_width(bottom, SILK)) + 8
    s = Canvas(w + 2, 18)
    s.rect((1, 1, w, 16), (26, 26, 30))
    s.text((w // 2 + 1, 1), top, "white", anchor="ma")
    s.text((w // 2 + 1, 8), bottom, "white", anchor="ma")
    return s.done()


# --- birthday: the young buck ------------------------------------------------------------------------

@lru_cache(maxsize=None)
def antlers():
    """A fine pair of antlers, to wear."""
    s = Canvas(34, 16)
    ant, sh = (214, 186, 136), (164, 132, 90)
    for side in (-1, 1):
        cx = 17
        base = (cx + side * 4, 15)
        tip = (cx + side * 15, 2)
        s.line([base, (cx + side * 9, 8), tip], ant, 2)
        s.line([(cx + side * 7, 10), (cx + side * 5, 3)], ant, 2)
        s.line([(cx + side * 11, 6), (cx + side * 11, 0)], ant)
        s.line([(cx + side * 13, 4), (cx + side * 16, 6)], ant)
        s.px(base, sh)
    return s.done()


def cake(img, x, y, t, blaze=1.0):
    """A birthday cake with all 89 candles lit: less a cake than a controlled burn. (x, y) is its base."""
    d = ImageDraw.Draw(img)
    d.rectangle((x - 16, y - 3, x + 16, y), fill=(236, 236, 240))                         # plate
    d.rectangle((x - 13, y - 13, x + 13, y - 3), fill=(236, 170, 190))
    d.rectangle((x - 13, y - 13, x + 13, y - 11), fill=(255, 240, 246))
    for k in range(-12, 13, 4):
        d.point((x + k, y - 10), fill=(255, 240, 246))
    pixel.text(img, (x, y - 10), "89", SILK, (170, 40, 70), shadow=None, anchor="ma")
    if blaze <= 0:
        return
    for k in range(27):                                                                    # the candles
        cx = x - 13 + k
        d.line([(cx, y - 14), (cx, y - 17)], fill=[(120, 180, 240), (250, 250, 250), (240, 120, 150)][k % 3])
    for k in range(27):                                                                    # the fire
        cx = x - 13 + k
        h = blaze * (10 + 8 * math.sin(k * 1.7 + t * 23) * math.sin(k * 0.6 + t * 9) + 6 * (1 - abs(k - 13) / 13))
        d.line([(cx, y - 18), (cx, y - 18 - h)], fill=(240, 90, 40))
        d.line([(cx, y - 18), (cx, y - 18 - h * 0.66)], fill=(255, 170, 50))
        d.line([(cx, y - 18), (cx, y - 18 - h * 0.33)], fill=(255, 244, 190))


# --- the cave: baby pictures -----------------------------------------------------------------------------

OCHRE, OCHRE_Y, CHAR = (176, 70, 44), (206, 150, 70), (40, 30, 30)
CAVE_WALL = (112, 88, 72)


@lru_cache(maxsize=1)
def cave_static():
    img = Image.new("RGB", (W, H), CAVE_WALL)
    d = ImageDraw.Draw(img)
    for k in range(40):                                                    # the rock's facets
        x, y = rnd("cave", k) * W, rnd("cave-y", k) * H
        r = 10 + rnd("cave-r", k) * 24
        pts = [(x + math.cos(a) * r * (0.6 + 0.4 * rnd("cv", k, a)), y + math.sin(a) * r * 0.6)
               for a in (0, 1.3, 2.4, 3.5, 4.6, 5.6)]
        d.polygon(pts, fill=mix(CAVE_WALL, (150, 120, 96) if k % 2 else (84, 66, 58), 0.4))
    d.polygon([(0, 150), (80, 142), (180, 148), (320, 140), (320, 180), (0, 180)], fill=(70, 56, 50))
    # the paintings: a mammoth, a bison, hunters, hands
    mammoth(d, 60, 70)
    bison(d, 250, 64)
    for k, x in enumerate((196, 206, 216)):
        d.line([(x, 104), (x, 112)], fill=CHAR)
        d.line([(x - 3, 118), (x, 112), (x + 3, 118)], fill=CHAR)
        d.point((x, 102), fill=CHAR)
        d.line([(x + 1, 106), (x + 7, 100 - k)], fill=CHAR)
    for (hx, hy, col_) in ((30, 118, OCHRE), (290, 112, OCHRE_Y), (276, 124, OCHRE)):
        d.ellipse((hx - 4, hy - 3, hx + 4, hy + 5), fill=col_)
        for f in range(4):
            d.line([(hx - 3 + f * 2, hy - 2), (hx - 4 + f * 2.6, hy - 8)], fill=col_)
        d.line([(hx + 4, hy + 1), (hx + 8, hy - 2)], fill=col_)
    return img


def mammoth(d, x, y):
    d.ellipse((x - 26, y - 16, x + 18, y + 16), fill=OCHRE)
    d.ellipse((x + 8, y - 20, x + 30, y + 4), fill=OCHRE)                      # head and hump
    d.line([(x + 26, y), (x + 30, y + 22), (x + 25, y + 26)], fill=OCHRE, width=3)   # trunk
    d.arc((x + 14, y + 2, x + 38, y + 22), 200, 330, fill=(236, 226, 200), width=2)  # tusk
    for lx in (x - 20, x - 10, x + 2, x + 10):
        d.rectangle((lx, y + 12, lx + 4, y + 26), fill=OCHRE)
    for k in range(8):
        d.line([(x - 22 + k * 5, y + 14), (x - 23 + k * 5, y + 18)], fill=CHAR)


def bison(d, x, y):
    d.ellipse((x - 18, y - 10, x + 14, y + 12), fill=CHAR)
    d.ellipse((x - 26, y - 12, x - 8, y + 6), fill=CHAR)
    d.polygon([(x - 26, y - 10), (x - 30, y - 16), (x - 22, y - 12)], fill=(236, 226, 200))
    for lx in (x - 14, x - 6, x + 4, x + 10):
        d.line([(lx, y + 10), (lx, y + 20)], fill=CHAR, width=2)
    d.ellipse((x - 10, y - 6, x + 8, y + 8), fill=OCHRE)


def baby_david(img, x, y):
    """The earliest known portrait of Sir David: a babe in a pram, already holding a camera."""
    d = ImageDraw.Draw(img)
    d.arc((x - 16, y - 16, x + 12, y + 12), 180, 360, fill=CHAR, width=2)        # the pram's hood
    d.line([(x - 16, y - 2), (x + 14, y - 2)], fill=CHAR, width=2)
    d.polygon([(x - 14, y - 2), (x + 12, y - 2), (x + 8, y + 8), (x - 10, y + 8)], fill=OCHRE)
    for wx in (x - 8, x + 6):
        d.ellipse((wx - 3, y + 8, wx + 3, y + 14), outline=CHAR)
    d.line([(x + 12, y - 2), (x + 20, y - 10)], fill=CHAR, width=2)
    d.ellipse((x - 4, y - 14, x + 6, y - 4), fill=OCHRE_Y)                      # the baby's head
    d.polygon([(x - 6, y - 10), (x - 2, y - 17), (x + 8, y - 16), (x + 4, y - 12)], fill=(236, 232, 220))  # the hair
    d.point((x + 3, y - 10), fill=CHAR)
    d.rectangle((x + 6, y - 9, x + 12, y - 5), fill=CHAR)                       # tiny camera
    d.rectangle((x + 12, y - 8, x + 14, y - 6), fill=CHAR)


def cave(c):
    img = cave_static().copy()
    baby_david(img, 140, 96)
    return img


scene("v2_cave", shots={"wall": (150, 92, 9), "baby": (140, 92, 18)},
      cast={"morgan": dict(x=72, y=152, facing=1, outfit="suit", mic=False, arm="point", gesture=False)})(cave)


def torchlight(img, x, y, r, amount=0.72):
    """Darken everything outside a pool of torchlight at (x, y)."""
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot(xx - x, (yy - y) * 1.1)
    m = np.clip((dist - r) / 26, 0, 1)
    m = np.floor(m * 3) / 3
    blend(img, m, (10, 6, 8), amount)


@lru_cache(maxsize=None)
def museum_label(title, sub):
    w = max(text_width(title, SILK), text_width(sub, SILK)) + 10
    s = Canvas(w + 2, 20)
    s.rect((1, 1, w, 18), (236, 228, 206))
    s.line([(3, 10), (w - 2, 10)], (180, 170, 150))
    s.text((5, 1), title, (60, 40, 30))
    s.text((5, 10), sub, (120, 90, 60))
    return s.done()


# --- the calendar and the King's card ----------------------------------------------------------------------

def calendar(img, year, day, box=CALENDAR, flutter=0.0):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK)
    d.rectangle((x0, y0, x1, y1), fill=(244, 240, 228))
    d.rectangle((x0, y0, x1, y0 + 9), fill=(200, 50, 56))
    pixel.text(img, ((x0 + x1) // 2, y0 + 1), str(year), SILK, (255, 255, 255), shadow=None, anchor="ma")
    pixel.text(img, ((x0 + x1) // 2, y0 + 14), str(day), PRESS16, (40, 34, 40), shadow=None, anchor="ma")
    d.line([(x0 + 2, y0 - 3), (x0 + 2, y0 + 1)], fill=INK)
    d.line([(x1 - 2, y0 - 3), (x1 - 2, y0 + 1)], fill=INK)


@lru_cache(maxsize=None)
def calendar_page(n):
    s = Canvas(16, 14)
    s.poly([(1, 1), (14, 2), (13, 12), (2, 11)], (244, 240, 228))
    s.rect((2, 2, 13, 4), (200, 50, 56))
    s.text((8, 5), str(n % 31 + 1), (40, 34, 40), anchor="ma")
    return s.done()


@lru_cache(maxsize=1)
def kings_card():
    """The card the monarch sends when you turn 100."""
    s = Canvas(96, 58)
    s.rect((1, 1, 94, 56), (248, 242, 224))
    s.rect((4, 4, 91, 53), (248, 242, 224))
    s.line([(4, 4), (91, 4)], (200, 160, 70)); s.line([(4, 53), (91, 53)], (200, 160, 70))
    s.line([(4, 4), (4, 53)], (200, 160, 70)); s.line([(91, 4), (91, 53)], (200, 160, 70))
    s.poly([(40, 16), (40, 9), (44, 12), (48, 7), (52, 12), (56, 9), (56, 16)], "gold")      # the crown
    s.line([(40, 16), (56, 16)], "gold_sh"); s.px((48, 12), "red")
    s.text((48, 19), "HAPPY 100TH", (120, 30, 50), anchor="ma")
    s.text((48, 28), "BIRTHDAY,", (120, 30, 50), anchor="ma")
    s.text((48, 37), "SIR DAVID", (40, 40, 60), anchor="ma")
    s.text((48, 45), "- THE KING", (100, 90, 80), anchor="ma")
    return s.done()


# --- the museum -------------------------------------------------------------------------------------

MUSEUM_FLOOR = 150


@lru_cache(maxsize=1)
def museum_static():
    img = Image.new("RGB", (W, H), (214, 200, 176))
    d = ImageDraw.Draw(img)
    for x in range(-20, W, 80):                                           # arches of the great hall
        d.rectangle((x + 26, 20, x + 34, MUSEUM_FLOOR), fill=(190, 172, 146))
        d.arc((x - 14, 0, x + 74, 70), 180, 360, fill=(170, 150, 126), width=3)
    d.rectangle((0, 0, W, 8), fill=(170, 150, 126))
    # a whale skeleton hangs from the ceiling
    for k in range(18):
        x = 60 + k * 11
        y = 26 + 4 * math.sin(k * 0.35)
        d.line([(x, y), (x + 2, y + 8 + (6 if k < 14 else 2))], fill=(242, 236, 222), width=2)
    d.line([(60, 26), (258, 30)], fill=(242, 236, 222), width=2)
    d.ellipse((252, 20, 284, 36), fill=(242, 236, 222))
    d.rectangle((0, MUSEUM_FLOOR, W, H), fill=(150, 120, 96))
    for x in range(0, W, 20):
        d.line([(x, MUSEUM_FLOOR), (x - 10, H)], fill=(136, 108, 88))
    return img


CASE = (170, 70, 246, 136)


def museum(c):
    img = museum_static().copy()
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = CASE
    d.rectangle((x0 - 6, y1, x1 + 6, MUSEUM_FLOOR), fill=(120, 96, 80))          # the plinth
    d.line([(x0 - 6, y1), (x1 + 6, y1)], fill=(160, 130, 108))
    if c.get("fossil"):
        img.paste(fossil_david(), (x0 + 8, y0 + 8), fossil_david())
    return img


def museum_glass(c):
    img = c.world
    x0, y0, x1, y1 = CASE
    blend_poly(img, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (200, 230, 240), 0.14)
    blend_poly(img, [(x0 + 10, y0), (x0 + 16, y0), (x0 + 2, y0 + 30), (x0 - 4 + 4, y0 + 30)], (255, 255, 255), 0.3)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x1, y1), outline=(80, 70, 66))


scene("v2_museum", mid=museum_glass,
      shots={"lectern": (96, 110, 12), "case": (208, 104, 12), "hall": (160, 96, 6)},
      cast={"david": dict(x=92, y=MUSEUM_FLOOR, facing=1, mic="fluffy", arm="palm", gesture=False)})(museum)


@lru_cache(maxsize=1)
def fossil_david():
    """Sir David, mineralised: a slab of sandstone with his bones in it, and the hair, which endures."""
    s = Canvas(62, 60)
    s.poly([(2, 6), (58, 2), (60, 56), (4, 58)], (206, 180, 134))
    for k in range(20):
        x, y = 4 + rnd("fs", k) * 52, 4 + rnd("fs-y", k) * 50
        s.px((int(x), int(y)), (184, 158, 116))
    bone = (246, 240, 222)
    s.ell((22, 8, 36, 22), bone)                          # skull
    s.ell((25, 12, 28, 15), (120, 100, 80)); s.ell((30, 12, 33, 15), (120, 100, 80))
    s.line([(26, 19), (32, 19)], (120, 100, 80))
    s.poly([(18, 10), (26, 4), (38, 5), (40, 9), (30, 8), (22, 12)], (255, 255, 255))   # the hair, intact
    s.line([(29, 22), (29, 40)], bone, 2)                 # spine
    for k in range(4):
        s.line([(22, 25 + k * 3), (36, 25 + k * 3)], bone)
    s.line([(29, 25), (18, 36)], bone, 2); s.line([(29, 25), (41, 36)], bone, 2)       # arms
    s.line([(29, 40), (22, 54)], bone, 2); s.line([(29, 40), (36, 54)], bone, 2)       # legs
    s.ell((38, 34, 46, 40), (60, 60, 70))                 # his camera, also fossilised
    return s.done()



def pool(x, y, rx, ry):
    """An ellipse mask: a pool of light on the floor."""
    return mask(lambda d: d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=255))


def paste_pivot(dst, spr, px, py, sx, sy, angle):
    """Paste `spr` with its own point (sx, sy) at (px, py), turned `angle` degrees (counter-clockwise)
    about that point: for things that topple over."""
    r = int(math.ceil(max(math.hypot(x - sx, y - sy) for x in (0, spr.width) for y in (0, spr.height)))) + 1
    big = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0))
    big.paste(spr, (r - int(sx), r - int(sy)))
    if angle:
        big = big.rotate(angle, resample=Image.NEAREST)
    dst.paste(big, (int(px) - r, int(py) - r), big)


# --- the void, and the switch that made the light --------------------------------------------------------

SWITCH = (180, 102)                   # the light switch's centre, where God can reach it


def void(c):
    img = Image.new("RGB", (W, H), (12, 10, 16))
    d = ImageDraw.Draw(img)
    for k in range(40):                                                   # specks of the not-yet-made
        d.point((int(rnd("void", k) * W), int(rnd("void-y", k) * H)), fill=(40, 36, 52))
    blend_poly(img, [(144, 0), (156, 0), (184, 152), (116, 152)], (255, 246, 220), 0.12)       # his spotlight
    blend(img, pool(150, 151, 34, 5), (255, 246, 220), 0.4)
    return img


scene("v2_void", shots={"god": (168, 106, 12)},
      cast={"morgan": dict(x=150, y=150, facing=1, outfit="god", mic=False)})(void)


@lru_cache(maxsize=2)
def light_switch(on=False):
    """A plain white wall switch at cosmic scale, with its masking-tape label."""
    s = Canvas(30, 46)
    s.rect((3, 1, 26, 34), (236, 232, 220))
    s.line([(4, 2), (25, 2)], (255, 255, 250)); s.line([(4, 33), (25, 33)], (196, 190, 176))
    s.rect((10, 9, 19, 26), (190, 184, 170))                              # the rocker's well
    if on:
        s.rect((11, 10, 18, 17), (252, 250, 244)); s.line([(11, 18), (18, 18)], (150, 144, 130))
    else:
        s.rect((11, 18, 18, 25), (252, 250, 244)); s.line([(11, 17), (18, 17)], (150, 144, 130))
    s.px((14, 4), (170, 164, 150)); s.px((14, 30), (170, 164, 150))      # screws
    s.poly([(1, 37), (28, 36), (28, 44), (1, 45)], (232, 214, 160))       # the label
    s.text((15, 37), "LIGHT", (60, 50, 50), anchor="ma")
    return s.done()


# --- the creation line --------------------------------------------------------------------------------------

BELT_TOP = 136                         # creatures ride on this
BELT_X = (126, 330)
BELT_SPEED = 34.0
CHUTE_X = 136                          # where they drop onto the belt
GOD_AT_BELT = (228, 152)               # God, behind the belt, tagging them as they pass
DAY_BOARD = (150, 54, 208, 82)


def factory(c):
    img = heaven_static().copy()
    d = ImageDraw.Draw(img)
    x0, y0, x1 = 70, 64, 126
    d.polygon([(x0 - 8, 40), (x1 + 8, 40), (x1 - 6, y0), (x0 + 6, y0)], fill=(176, 170, 200))   # the hopper
    d.line([(x0 - 8, 40), (x1 + 8, 40)], fill=(214, 210, 232))
    d.rectangle((x0, y0, x1, 150), fill=(196, 190, 214))                  # the machine
    d.line([(x1, y0), (x1, 150)], fill=(150, 144, 172))
    d.rectangle((x0 + 4, 70, x1 - 4, 88), fill=(250, 244, 222))
    d.rectangle((x0 + 4, 70, x1 - 4, 88), outline=(186, 132, 40))
    pixel.text(img, ((x0 + x1) // 2, 71), "CREATION", SILK, (150, 100, 40), shadow=None, anchor="ma")
    pixel.text(img, ((x0 + x1) // 2, 79), "INC.", SILK, (150, 100, 40), shadow=None, anchor="ma")
    spin = 0 if c.get("belt_stop") else c.t
    for k, (gx, gy, r) in enumerate(((86, 108, 8), (107, 114, 6))):      # gears
        a = spin * (2.4 if k else -1.8)
        for j in range(8):
            aa = a + j * math.pi / 4
            d.line([(gx, gy), (gx + math.cos(aa) * (r + 2), gy + math.sin(aa) * (r + 2))], fill=(186, 132, 40),
                   width=3)
        d.ellipse((gx - r, gy - r, gx + r, gy + r), fill=(246, 204, 90))
        d.ellipse((gx - 2, gy - 2, gx + 2, gy + 2), fill=(186, 132, 40))
    d.rectangle((x1 - 2, BELT_TOP - 20, x1 + 8, BELT_TOP - 18), fill=(150, 144, 172))     # the chute's mouth
    d.rectangle((x1 - 2, BELT_TOP - 18, x1 + 6, BELT_TOP), fill=(40, 36, 52))
    if c.get("closed"):
        d.line([(x0 + 14, 90), (98, 86), (x1 - 14, 90)], fill=INK)
        d.rectangle((x0 + 10, 90, x1 - 10, 102), fill=(150, 98, 64))
        pixel.text(img, ((x0 + x1) // 2, 92), "CLOSED", SILK, (255, 236, 200), shadow=None, anchor="ma")
    bx0, by0, bx1, by1 = DAY_BOARD                                          # the day board, hung from the clouds
    for x in (bx0 + 6, bx1 - 6):
        d.line([(x, 0), (x, by0)], fill=(186, 132, 40))
    d.rectangle((bx0, by0, bx1, by1), fill=(40, 36, 64))
    d.rectangle((bx0, by0, bx1, by1), outline=(246, 204, 90))
    pixel.text(img, ((bx0 + bx1) // 2, by0 + 3), "TODAY IS", SILK, (230, 222, 206), shadow=None, anchor="ma")
    pixel.text(img, ((bx0 + bx1) // 2, by0 + 13), f"DAY {c.get('day', 5)}", PRESS, (246, 204, 90), shadow=None,
               anchor="ma")
    return img


def factory_belt(c):
    """The conveyor, in front of whoever works behind it."""
    img = c.world
    d = ImageDraw.Draw(img)
    x0, x1 = BELT_X
    d.rectangle((x0, BELT_TOP + 4, x1, 150), fill=(170, 164, 192))
    d.line([(x0, BELT_TOP + 5), (x1, BELT_TOP + 5)], fill=(206, 200, 224))
    for x in range(x0 + 10, x1, 22):
        d.rectangle((x - 1, BELT_TOP + 11, x + 1, 148), fill=(150, 144, 172))
        d.point((x, BELT_TOP + 8), fill=(120, 116, 140))
    d.rectangle((x0, BELT_TOP, x1, BELT_TOP + 4), fill=(52, 50, 62))
    run = 0 if c.get("belt_stop") else c.t * BELT_SPEED
    for x in range(x0 - 8, x1 + 8, 8):
        xx = x + int(run) % 8
        if x0 <= xx <= x1:
            d.line([(xx, BELT_TOP + 1), (xx, BELT_TOP + 3)], fill=(84, 82, 98))
    d.line([(x0, 150), (x1, 150)], fill=(120, 116, 140))


scene("v2_factory", mid=factory_belt, shots={"line": (178, 100, 9), "god": (230, 118, 12)},
      cast={"morgan": dict(x=GOD_AT_BELT[0], y=GOD_AT_BELT[1], facing=-1, outfit="god", mic=False)})(factory)


@lru_cache(maxsize=None)
def fish(color=(90, 170, 220), frame=0):
    s = Canvas(18, 12)
    flip = 1 if frame else 0
    s.ell((4, 2 + flip, 15, 9 + flip), color)
    s.poly([(1, 1 + 2 * flip), (6, 5 + flip), (1, 10)], mix(color, INK, 0.3))
    s.line([(6, 6 + flip), (12, 6 + flip)], mix(color, (255, 255, 255), 0.45))
    s.px((12, 4 + flip), "eye")
    return s.done()


@lru_cache(maxsize=None)
def tag(text_="M.F."):
    """The little paper tag tied to everything God makes."""
    w = text_width(text_, SILK) + 4
    s = Canvas(w + 3, 11)
    s.line([(0, 0), (2, 3)], "paper_sh")
    s.poly([(2, 3), (w + 1, 2), (w + 1, 9), (2, 9)], "paper")
    s.text((w // 2 + 2, 2), text_, (180, 40, 50), anchor="ma")
    return s.done()


@lru_cache(maxsize=1)
def deckchair():
    s = Canvas(34, 30)
    s.line([(3, 28), (24, 4)], "wood", 2)
    s.line([(12, 28), (30, 15)], "wood", 2)
    s.line([(6, 20), (28, 20)], "wood", 2)
    s.poly([(8, 20), (23, 4), (27, 7), (13, 22)], (230, 90, 90))
    for k in range(3):
        s.line([(11 + k * 4, 17 - k * 4), (15 + k * 4, 19 - k * 4)], (250, 240, 240), 2)
    return s.done()


# --- Dickie's park --------------------------------------------------------------------------------------------

DICKIE_SWAP = {C["shirt"]: (238, 230, 206), C["shirt_sh"]: (206, 196, 170), C["shirt_hi"]: (250, 246, 232),
               C["khaki"]: (232, 224, 200), C["khaki_sh"]: (200, 190, 166), C["shoe"]: (130, 90, 64)}


@lru_cache(maxsize=64)
def dickie(facing=1, cane="ground", **pose):
    """His brother Richard, who ran the park: Sir David's face with a white beard, a cream suit and the
    amber-topped cane, on the ground ("ground", with arm="down") or held up ("aloft", with arm="up").
    Returns (sprite, anchors) like characters.figure."""
    import numpy as np
    from characters import figure
    img, a = figure("david", 1, **pose)
    pad = 20                                                  # headroom for the cane held up
    tall = Image.new("RGBA", (img.width, img.height + pad), (0, 0, 0, 0))
    tall.paste(img, (0, pad))
    img, a = tall, {k: (x, y + pad) for k, (x, y) in a.items()}
    arr = np.array(img)
    for src, dst in DICKIE_SWAP.items():
        arr[np.all(arr[..., :3] == src, axis=-1), :3] = dst
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    mx, my = int(a["mouth"][0]), int(a["mouth"][1])
    top = my - 1
    d.polygon([(mx - 6, top), (mx + 2, top), (mx + 1, top + 4), (mx - 2, top + 6), (mx - 5, top + 4)], fill=INK)
    d.polygon([(mx - 5, top), (mx + 1, top), (mx, top + 3), (mx - 2, top + 5), (mx - 4, top + 3)],
              fill=(246, 246, 250))
    d.line([(mx - 3, my), (mx, my)], fill=C["mouth"])
    if cane:
        hx, hy = int(a["hand"][0]), int(a["hand"][1])
        if cane == "ground":
            (x0, y0), (x1, y1), knob = (hx + 1, hy), (hx + 2, int(a["feet"][1])), (hx + 1, hy - 3)
        else:
            (x0, y0), (x1, y1), knob = (hx, hy + 8), (hx + 1, hy - 14), (hx + 1, hy - 17)
        d.line([(x0, y0), (x1, y1)], fill=INK, width=3)
        d.line([(x0, y0), (x1, y1)], fill=(120, 80, 50))
        kx, ky = knob
        d.ellipse((kx - 3, ky - 3, kx + 3, ky + 3), fill=INK)
        d.ellipse((kx - 2, ky - 2, kx + 2, ky + 2), fill=(240, 150, 40))     # amber, with a mosquito in it
        d.point((kx, ky), fill=(70, 30, 20))
    if facing < 0:
        img = mirror(img)
        a = {k: (img.width - 1 - x, y) for k, (x, y) in a.items()}
    return img, a


GATE_FLOOR = 152


@lru_cache(maxsize=1)
def jungle_back():
    img = Image.new("RGB", (W, H), (150, 196, 170))
    vgrad(img, (0, 0, W, 104), (240, 206, 160), (160, 200, 170), steps=5)
    d = ImageDraw.Draw(img)
    for k in range(15):
        leaf_blob(d, k * 24 + rnd("jb", k) * 10, 92 + rnd("jby", k) * 18, 28, (84, 134, 96), ("jb", k), n=7)
    for k in range(13):
        leaf_blob(d, k * 27 + rnd("jb2", k) * 12, 122 + rnd("jb2y", k) * 10, 22, (52, 104, 72), ("jb2", k), n=6)
    d.rectangle((0, GATE_FLOOR - 8, W, H), fill=(128, 106, 74))
    d.line([(0, GATE_FLOOR - 8), (W, GATE_FLOOR - 8)], fill=(150, 128, 92))
    return img


def gate(c):
    img = jungle_back().copy()
    d = ImageDraw.Draw(img)
    open_ = c.get("gate_open", 0.0)
    lo, hi = 126, 194                                                     # the opening between the pillars
    d.rectangle((lo, 44, hi, GATE_FLOOR - 8), fill=(30, 52, 40))           # the dark road in
    for k in range(5):
        leaf_blob(d, lo + 8 + k * 13, 70 + (k % 2) * 8, 10, (40, 76, 54), ("gr", k), n=5)
    if open_:
        blend_poly(img, [(lo + 22, 60), (hi - 22, 60), (hi, GATE_FLOOR - 8), (lo, GATE_FLOOR - 8)],
                   (255, 240, 200), 0.2 * open_)
    w = int((hi - lo) // 2 * (1 - 0.82 * open_))                         # the doors swing out toward us
    for x0, x1 in ((lo, lo + w), (hi - w, hi)):
        d.rectangle((x0, 50, x1, GATE_FLOOR - 8), fill=(122, 86, 58))
        for x in range(x0 + 2, x1, 5):
            d.line([(x, 50), (x, GATE_FLOOR - 8)], fill=(98, 68, 48))
        d.line([(x0, 70), (x1, 70)], fill=(88, 60, 42), width=2)
        d.line([(x0, 122), (x1, 122)], fill=(88, 60, 42), width=2)
    for px_ in (lo - 12, hi + 12):                                        # the great log pillars, with torches
        d.rectangle((px_ - 12, 24, px_ + 12, GATE_FLOOR - 8), fill=(112, 78, 52))
        d.line([(px_ - 6, 24), (px_ - 6, GATE_FLOOR - 8)], fill=(142, 102, 68))
        d.line([(px_ + 7, 24), (px_ + 7, GATE_FLOOR - 8)], fill=(86, 58, 40))
        flick = 2 * math.sin(c.t * 17 + px_)
        d.rectangle((px_ - 3, 56, px_ + 3, 62), fill=(60, 44, 34))
        d.polygon([(px_ - 5, 56), (px_ + flick, 42), (px_ + 5, 56)], fill=(255, 150, 40))
        d.polygon([(px_ - 2, 56), (px_ + flick * 0.5, 48), (px_ + 2, 56)], fill=(255, 236, 150))
    d.rectangle((lo - 26, 24, hi + 26, 42), fill=(84, 56, 40))            # the sign across the top
    d.rectangle((lo - 22, 27, hi + 22, 39), fill=(206, 70, 40))
    pixel.text(img, (160, 29), "JURASSIC PARK", PRESS, (255, 214, 90), shadow=(90, 24, 10), anchor="ma")
    return img


scene("v2_gate", shots={"gate": (160, 92, 6), "brothers": (160, 112, 12)}, cast={})(gate)


PADDOCK_FLOOR = 152
FENCE_X = 150


def paddock_fence(c):
    """The electric fence, over the T. rex behind it."""
    img = c.world
    d = ImageDraw.Draw(img)
    for x in range(FENCE_X, W + 40, 44):
        d.rectangle((x - 3, 30, x + 3, PADDOCK_FLOOR - 6), fill=(84, 84, 92))
        d.line([(x - 2, 30), (x - 2, PADDOCK_FLOOR - 6)], fill=(122, 122, 132))
        d.rectangle((x - 5, 26, x + 5, 31), fill=(112, 112, 122))
    for y in range(40, PADDOCK_FLOOR - 10, 10):
        d.line([(FENCE_X, y), (W, y)], fill=(34, 34, 40))
    for k in range(4):                                                    # current running along the wires
        sx = FENCE_X + (c.t * 90 + k * 47) % (W - FENCE_X)
        sy = 40 + 10 * ((k * 3 + int(c.t * 3)) % 10)
        d.line([(sx - 2, sy), (sx + 2, sy)], fill=(255, 250, 190))
    d.rectangle((220, 92, 268, 114), fill=INK)
    d.rectangle((221, 93, 267, 113), fill=(240, 204, 40))
    pixel.text(img, (244, 95), "DANGER", SILK, INK, shadow=None, anchor="ma")
    pixel.text(img, (244, 104), "10,000V", SILK, INK, shadow=None, anchor="ma")


def paddock(c):
    return jungle_back().copy()


scene("v2_paddock", mid=paddock_fence, shots={"island": (176, 100, 9), "david": (118, 116, 12)},
      cast={"david": dict(x=104, y=PADDOCK_FLOOR, facing=1, body="crouch", mic="fluffy", arm="whisper",
                          gesture=False, z=1)})(paddock)


@lru_cache(maxsize=None)
def wood_sign(lines, point=-1):
    """A park sign on a post: a plank with an arrow end pointing left (-1) or right (1)."""
    tw = max(text_width(s, SILK) for s in lines)
    w, h = tw + 8, 8 * len(lines) + 4
    s = Canvas(w + 12, h + 26)
    s.rect((w // 2 + 4, h, w // 2 + 7, h + 25), "wood_sh")
    x0 = 6 if point < 0 else 1
    s.rect((x0, 1, x0 + w, h), "wood_hi")
    if point < 0:
        s.poly([(0, (h + 1) // 2), (x0, 1), (x0, h)], "wood_hi")
    else:
        s.poly([(x0 + w + 5, (h + 1) // 2), (x0 + w, 1), (x0 + w, h)], "wood_hi")
    for i, row in enumerate(lines):
        s.text((x0 + w // 2 + 1, 2 + i * 8), row, (70, 40, 20), anchor="ma")
    return s.done()


# --- the awards ---------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def oscar():
    """A gold statuette: a knight on a reel."""
    s = Canvas(9, 22)
    s.ell((3, 1, 6, 4), "gold")
    s.rect((3, 4, 5, 14), "gold"); s.px((3, 6), "gold_hi")
    s.line([(2, 6), (2, 11)], "gold_sh"); s.line([(6, 6), (6, 11)], "gold_sh")
    s.rect((2, 15, 6, 16), "gold_sh")
    s.rect((1, 17, 7, 20), (40, 36, 40))
    return s.done()


@lru_cache(maxsize=None)
def bafta(tilt=0):
    """A gold theatre mask on a little stand; tilt cocks it to one side, unsure of itself."""
    s = Canvas(14, 20)
    s.poly([(3, 1), (10, 1), (12, 5), (11, 11), (7, 14), (3, 11), (2, 5)], "gold")     # the mask, tilted back
    s.line([(3, 2), (3, 9)], "gold_hi")
    s.line([(11, 5), (10, 11)], "gold_sh")
    s.line([(4, 5), (5, 5)], (90, 56, 20)); s.line([(8, 5), (9, 5)], (90, 56, 20))     # eye slits
    s.line([(7, 6), (7, 9)], "gold_sh")                                               # nose
    s.line([(6, 11), (8, 11)], (90, 56, 20))                                           # mouth
    s.rect((6, 14, 7, 15), "gold_sh")
    s.rect((3, 15, 10, 18), (40, 36, 40))
    img = s.done()
    return img.rotate(-16 * tilt, resample=Image.NEAREST, center=(7, 17)) if tilt else img


@lru_cache(maxsize=1)
def boxing_baby():
    """Million Dollar Baby: a baby in red gloves, sat on a million dollars."""
    s = Canvas(36, 40)
    for k in range(4):                                                    # the money
        s.rect((3, 26 + k * 3, 32, 28 + k * 3), (110, 160, 90))
        s.line([(3, 26 + k * 3), (32, 26 + k * 3)], (150, 200, 120))
        s.px((17, 27 + k * 3), (60, 100, 50))
    s.ell((11, 12, 25, 26), (250, 214, 190))                              # body
    s.rect((11, 20, 25, 25), (250, 250, 250))                             # nappy
    s.ell((12, 1, 24, 13), (250, 214, 190))                               # head
    s.px((15, 6), "eye"); s.px((20, 6), "eye")
    s.line([(16, 10), (19, 10)], "mouth")
    s.px((18, 1), (120, 80, 50))                                          # a curl
    s.ell((3, 12, 11, 19), "red"); s.ell((25, 12, 33, 19), "red")         # the gloves
    s.px((5, 13), "red_hi"); s.px((27, 13), "red_hi")
    return s.done()


STAGE_FLOOR = 150


def stage(c):
    img = Image.new("RGB", (W, H), (40, 20, 30))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 12):                                             # curtains
        d.rectangle((x, 0, x + 11, STAGE_FLOOR), fill=(150, 30, 44) if (x // 12) % 2 else (126, 22, 36))
        d.line([(x + 3, 0), (x + 3, STAGE_FLOOR)], fill=(176, 48, 60))
    d.rectangle((0, 0, W, 34), fill=(110, 18, 30))
    for x in range(0, W, 20):
        d.polygon([(x, 34), (x + 20, 34), (x + 10, 42)], fill=(110, 18, 30))
    d.line([(0, 34), (W, 34)], fill=(246, 204, 90))
    d.rectangle((0, STAGE_FLOOR, W, H), fill=(80, 56, 44))
    d.line([(0, STAGE_FLOOR), (W, STAGE_FLOOR)], fill=(246, 204, 90))
    blend(img, 1.0, (10, 4, 10), 0.45)                                    # the house lights are down
    for x in c.get("spots", ()):
        blend_poly(img, [(x - 5, 0), (x + 5, 0), (x + 28, STAGE_FLOOR), (x - 28, STAGE_FLOOR)], (255, 244, 210), 0.3)
        blend(img, pool(x, STAGE_FLOOR + 1, 28, 5), (255, 244, 210), 0.5)
    return img


scene("v2_stage", shots={"stage": (160, 104, 9)},
      cast={"morgan": dict(x=214, y=STAGE_FLOOR, facing=-1, outfit="tux", mic=False)})(stage)


STUDY_FLOOR = 152
SHELF_Y = 96


@lru_cache(maxsize=1)
def study_static():
    img = Image.new("RGB", (W, H), (110, 70, 50))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 16):                                             # panelling
        d.rectangle((x + 2, 6, x + 14, STUDY_FLOOR - 6), outline=(90, 56, 40))
    d.rectangle((0, STUDY_FLOOR - 6, W, H), fill=(70, 40, 36))
    for x in range(0, W, 8):
        d.line([(x, STUDY_FLOOR - 6), (x, H)], fill=(60, 34, 30))
    d.rectangle((0, SHELF_Y, W, SHELF_Y + 4), fill=(150, 104, 66))          # the long shelf
    d.line([(0, SHELF_Y), (W, SHELF_Y)], fill=(196, 146, 96))
    d.rectangle((0, SHELF_Y + 4, W, SHELF_Y + 6), fill=(70, 44, 32))
    return img


def study(c):
    img = study_static().copy()
    shrug = c.get("shrug", 0.0)
    for k, x in enumerate(range(6, W, 17)):
        tilt = 0 if not shrug else (1 if (k + int(c.t * 3)) % 2 else -1)
        spr = bafta(tilt)
        img.paste(spr, (x, SHELF_Y - 18), spr)
    return img


scene("v2_study", shots={"shelf": (160, 104, 9), "two": (172, 108, 12)},
      cast={"david": dict(x=156, y=STUDY_FLOOR, facing=1, arm="palm", gesture=False),
            "morgan": dict(x=196, y=STUDY_FLOOR, facing=-1, outfit="tux", mic=False)})(study)


# --- the ship -------------------------------------------------------------------------------------------------

SEA_Y = 128
HULL = (40, 88, 270, 138)
QUAY = 140


def dock(c):
    img = Image.new("RGB", (W, H), (176, 200, 220))
    vgrad(img, (0, 0, W, SEA_Y), (140, 170, 204), (214, 226, 236), steps=4)
    d = ImageDraw.Draw(img)
    d.rectangle((0, SEA_Y, W, H), fill=(52, 90, 130))
    for k in range(24):
        x = (k * 37 + c.t * 8) % W
        y = SEA_Y + 4 + (k * 13) % 30
        d.line([(x, y), (x + 6, y)], fill=(90, 130, 170))
    x0, y0, x1, y1 = HULL
    bob = int(round(math.sin(c.t * 1.4)))
    d.rectangle((170, 50 + bob, 250, y0 + bob), fill=(246, 244, 238))        # superstructure
    d.rectangle((190, 36 + bob, 236, 50 + bob), fill=(246, 244, 238))
    for x in range(176, 246, 10):
        d.rectangle((x, 58 + bob, x + 5, 62 + bob), fill=(40, 60, 80))
    d.rectangle((196, 40 + bob, 230, 44 + bob), fill=(40, 60, 80))
    d.rectangle((214, 20 + bob, 218, 36 + bob), fill=(230, 180, 40))         # mast
    d.line([(100, 88 + bob), (130, 40 + bob)], fill=(230, 180, 40), width=3)   # crane
    d.line([(130, 40 + bob), (140, 70 + bob)], fill=(60, 60, 70))
    d.polygon([(x0, y0 + bob), (x1 + 20, y0 + bob), (x1, y1 + bob), (x0 + 10, y1 + bob)], fill=(196, 40, 40))
    d.line([(x0, y0 + bob), (x1 + 20, y0 + bob)], fill=(246, 244, 238), width=2)
    d.rectangle((x0 + 10, y1 - 6 + bob, x1, y1 + bob), fill=(120, 30, 34))
    for k in range(9):                                                    # bunting, bow to mast
        bx = 50 + k * 18
        by = 60 + abs(k - 4) * 3 + bob
        d.polygon([(bx, by), (bx + 6, by), (bx + 3, by + 6)], fill=[(230, 60, 60), (250, 250, 250), (60, 90, 200)][k % 3])
    return img


def dock_near(c):
    """The quay in front, where Sir David stands proud."""
    d = ImageDraw.Draw(c.world)
    d.rectangle((0, QUAY, 64, H), fill=(120, 116, 110))
    d.line([(0, QUAY), (64, QUAY)], fill=(160, 156, 150))
    d.rectangle((58, QUAY - 6, 62, QUAY), fill=(60, 60, 64))                # a bollard


def hull_name(img, name, p=1.0, bob=0):
    """The ship's name on the bow: blank white until it is painted, letter by letter, as p goes 0 -> 1."""
    d = ImageDraw.Draw(img)
    d.rectangle((64, 100 + bob, 236, 118 + bob), fill=(236, 236, 232))
    d.rectangle((64, 100 + bob, 236, 118 + bob), outline=INK)
    shown = name[:int(round(len(name) * clamp(p, 0, 1)))]
    if shown:
        pixel.text(img, (150 - text_width(name, PRESS) // 2, 105 + bob), shown, PRESS, (20, 30, 60), shadow=None)


scene("v2_dock", mid=dock_near, shots={"ship": (160, 92, 6), "hull": (150, 106, 12)},
      cast={"david": dict(x=30, y=QUAY, facing=1, arm="palm", gesture=False)})(dock)


# --- the war room ---------------------------------------------------------------------------------------------

WINDOW = (112, 30, 208, 100)
PODIUM_X = 160


def oval(c):
    img = Image.new("RGB", (W, H), (40, 50, 90))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 14):                                             # navy drapes
        d.rectangle((x, 0, x + 13, 150), fill=(46, 58, 104) if (x // 14) % 2 else (36, 46, 86))
    wx0, wy0, wx1, wy1 = WINDOW
    d.rectangle((wx0, wy0, wx1, wy1), fill=mix((110, 150, 200), (255, 250, 236), c.get("sky", 0.0)))
    return img


def oval_mid(c):
    """The window frame, the flags and the podium, over the sky (and the comet) and over the President."""
    img = c.world
    d = ImageDraw.Draw(img)
    wx0, wy0, wx1, wy1 = WINDOW
    d.rectangle((wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), outline=(236, 232, 220), width=3)
    d.line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=(236, 232, 220), width=2)
    d.line([(wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2)], fill=(236, 232, 220), width=2)
    for fx, colr in ((78, (200, 40, 50)), (238, (40, 60, 140))):             # flags
        d.line([(fx, 36), (fx, 150)], fill=(200, 170, 80), width=2)
        d.rectangle((fx + 2, 38, fx + 22, 60), fill=colr)
        for y in range(40, 60, 4):
            d.line([(fx + 2, y), (fx + 22, y)], fill=(236, 232, 220))
    d.rectangle((0, 150, W, H), fill=(120, 30, 40))
    x, top = PODIUM_X, 124
    d.polygon([(x - 20, top), (x + 20, top), (x + 17, 152), (x - 17, 152)], fill=INK)
    d.polygon([(x - 19, top + 1), (x + 19, top + 1), (x + 16, 151), (x - 16, 151)], fill=(120, 80, 54))
    d.line([(x - 19, top + 1), (x + 19, top + 1)], fill=(170, 120, 80))
    d.ellipse((x - 7, top + 6, x + 7, top + 20), fill=(40, 60, 120))
    d.ellipse((x - 5, top + 8, x + 5, top + 18), fill=(236, 200, 90))
    d.ellipse((x - 2, top + 11, x + 2, top + 15), fill=(40, 60, 120))
    for k in (-5, 5):                                                     # the microphones
        d.line([(x + k, top + 1), (x + k // 2, top - 8)], fill=(40, 40, 46))


scene("v2_oval", mid=oval_mid, shots={"podium": (162, 104, 12)},
      cast={"morgan": dict(x=PODIUM_X, y=150, facing=1, outfit="president", mic=False, z=0)})(oval)


def comet(img, x, y, r):
    """A comet heading down and left, its tail streaming back up and to the right."""
    d = ImageDraw.Draw(img)
    for k in range(6, 0, -1):
        rr = r * (1 - k * 0.12)
        cx, cy = x + k * r * 0.9, y - k * r * 0.7
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr),
                  fill=[(255, 250, 220), (255, 226, 150), (255, 190, 90), (250, 150, 60), (220, 110, 60),
                        (180, 90, 70)][k - 1])
    d.ellipse((x - r, y - r, x + r, y + r), fill=(110, 86, 70))
    d.ellipse((x - r * 0.5, y - r * 0.6, x + r * 0.1, y), fill=(150, 120, 90))


# --- the Cretaceous --------------------------------------------------------------------------------------------

CRET_FLOOR = 150


def cretaceous(c):
    img = Image.new("RGB", (W, H), (240, 170, 110))
    vgrad(img, (0, 0, W, 110), (196, 120, 116), (250, 200, 130), steps=5)
    d = ImageDraw.Draw(img)
    d.polygon([(190, 110), (238, 50), (256, 50), (310, 110)], fill=(110, 84, 80))     # the volcano
    d.polygon([(238, 50), (256, 50), (250, 58), (244, 54)], fill=(230, 90, 40))
    for k in range(4):
        r = 8 + k * 5 + (c.t * 3) % 5
        d.ellipse((247 - r, 44 - k * 12 - r * 0.6, 247 + r, 44 - k * 12 + r * 0.6), fill=(150, 130, 130))
    d.polygon([(0, 116), (70, 100), (160, 112), (320, 104), (320, 180), (0, 180)], fill=(116, 130, 70))
    d.rectangle((0, CRET_FLOOR, W, H), fill=(96, 110, 60))
    for k in range(9):
        x = k * 38 + 10
        for j in range(4):
            frond(d, x, CRET_FLOOR + 2, 14 + rnd("cf", k, j) * 8, 0.5 + j * 0.7,
                  (70, 110, 60) if j % 2 else (50, 90, 50), width=4)
    return img


scene("v2_cret", shots={"pair": (170, 104, 9), "david": (126, 116, 12)},
      cast={"david": dict(x=116, y=CRET_FLOOR, facing=1, body="crouch", mic="fluffy", arm="whisper", gesture=False,
                          z=1)})(cretaceous)


@lru_cache(maxsize=1)
def ash_world():
    """After: grey sky, grey ground, and the bones."""
    img = Image.new("RGB", (W, H), (120, 110, 110))
    vgrad(img, (0, 0, W, 120), (70, 62, 66), (140, 128, 124), steps=5)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 118), (90, 108), (200, 116), (320, 108), (320, 180), (0, 180)], fill=(150, 142, 138))
    d.rectangle((0, CRET_FLOOR, W, H), fill=(170, 162, 156))
    for k in range(30):
        x, y = rnd("ash", k) * W, rnd("ash-y", k) * 110
        d.point((int(x), int(y)), fill=(200, 196, 196))
    return img


@lru_cache(maxsize=1)
def rex_bones():
    """What's left of the T. rex (facing right, like critters.trex): a skeleton in the ash."""
    s = Canvas(64, 46)
    bone = (236, 230, 214)
    s.line([(2, 20), (14, 17), (26, 16)], bone, 2)                                       # tail and spine
    s.line([(26, 16), (36, 14), (40, 10)], bone, 2)
    for x in range(8, 26, 3):
        s.px((x, 17 - (x - 8) // 6), bone); s.px((x, 16 - (x - 8) // 6), bone)
    for k in range(5):                                                                    # ribs
        x = 22 + k * 3
        s.line([(x, 17), (x - 1 + k // 2, 27 - abs(k - 2))], bone)
    s.line([(28, 24), (32, 33), (28, 44)], bone, 2); s.line([(34, 22), (38, 32), (35, 44)], bone, 2)   # legs
    s.line([(26, 44), (30, 44)], bone); s.line([(33, 44), (38, 44)], bone)
    s.poly([(38, 2), (56, 2), (61, 6), (61, 11), (44, 12), (38, 8)], bone)               # the skull
    s.ell((42, 3, 46, 7), (60, 56, 60)); s.rect((50, 4, 55, 7), (60, 56, 60))
    s.poly([(44, 13), (58, 13), (58, 16), (44, 16)], bone)                                # jaw
    for x in range(45, 60, 3):
        s.px((x, 12), (60, 56, 60))
    s.line([(40, 20), (44, 22)], bone)                                                    # the tiny arm
    return s.done()


# --- the title and the crown -----------------------------------------------------------------------------

HALL_FLOOR = 152


@lru_cache(maxsize=1)
def hall_static():
    img = Image.new("RGB", (W, H), (84, 60, 70))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):                                             # tall panels
        d.rectangle((x + 3, 8, x + 37, HALL_FLOOR - 16), fill=(98, 72, 84))
        d.rectangle((x + 3, 8, x + 37, HALL_FLOOR - 16), outline=(120, 90, 100))
    d.rectangle((0, HALL_FLOOR - 12, W, HALL_FLOOR - 8), fill=(150, 110, 70))     # dado rail
    d.rectangle((0, HALL_FLOOR - 8, W, H), fill=(120, 30, 40))                    # red carpet
    d.line([(0, HALL_FLOOR - 8), (W, HALL_FLOOR - 8)], fill=(200, 160, 80))
    return img


def hall(c):
    return hall_static().copy()


scene("v2_hall", shots={"both": (162, 104, 9)},
      cast={"morgan": dict(x=104, y=HALL_FLOOR, facing=1, outfit="suit", mic=True),
            "david": dict(x=212, y=HALL_FLOOR, facing=-1, hat="crown", gesture=False)})(hall)


def brass_plate(img, x, y, rows, lit=(), gone=()):
    """A brass name plate centred on (x, y) holding rows of text pieces, so that one piece can come off.
    Pieces in `lit` shine; pieces in `gone` have left a clean patch. Returns each piece's box."""
    w = max(sum(text_width(p, PRESS) for p in row) for row in rows) + 12
    h = 10 * len(rows) + 5
    x0, y0 = x - w // 2, y - h // 2
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1), fill=INK)
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=(214, 172, 90))
    d.rectangle((x0 + 2, y0 + 2, x0 + w - 2, y0 + h - 2), fill=(184, 140, 66))
    boxes = {}
    for r, row in enumerate(rows):
        rw = sum(text_width(p, PRESS) for p in row)
        xx, yy = x - rw // 2, y0 + 4 + r * 10
        for p in row:
            pw = text_width(p, PRESS)
            if p in gone:
                d.rectangle((xx, yy - 1, xx + pw - 3, yy + 8), fill=(206, 164, 84))
            else:
                pixel.text(img, (xx, yy), p, PRESS, (255, 240, 160) if p in lit else (70, 44, 20), shadow=None)
            boxes[p] = (xx, yy, xx + pw, yy + 8)
            xx += pw
    return boxes


@lru_cache(maxsize=None)
def word_chip(s):
    """A piece of a brass plate that has come off: the word on a scrap of brass."""
    w = text_width(s.strip(), PRESS) + 4
    c = Canvas(w + 2, 12)
    c.rect((1, 1, w, 10), (214, 172, 90))
    c.text((3, 2), s.strip(), (70, 44, 20), fnt=PRESS)
    return c.done()


# --- London ----------------------------------------------------------------------------------------------------

THAMES = 140
BEN = (178, 112)                        # the foot of the clock tower
STATUE = (250, 132)                     # the plinth top, where his feet are


def london(c):
    img = Image.new("RGB", (W, H), (90, 60, 80))
    vgrad(img, (0, 0, W, THAMES), (60, 40, 70), (236, 124, 80), steps=6)
    d = ImageDraw.Draw(img)
    sil = (40, 30, 44)
    d.rectangle((0, 112, W, THAMES), fill=sil)
    for x, w, h in ((0, 30, 20), (28, 20, 34), (60, 40, 18), (206, 24, 40), (296, 30, 30)):
        d.rectangle((x, 112 - h, x + w, 112), fill=sil)
    d.polygon([(232, 112), (246, 22), (260, 112)], fill=(52, 42, 58))                # the Shard
    d.ellipse((264, 60, 312, 108), outline=sil, width=2)                             # the Eye
    for k in range(12):
        a = k * math.pi / 6
        d.line([(288, 84), (288 + math.cos(a) * 24, 84 + math.sin(a) * 24)], fill=sil)
    d.rectangle((100, 98, 196, 114), fill=sil)                                       # Parliament
    for x in range(102, 196, 8):
        d.polygon([(x, 98), (x + 3, 92), (x + 6, 98)], fill=sil)
    d.rectangle((0, THAMES, W, H), fill=(50, 40, 60))
    for k in range(20):
        x = (k * 41 + c.t * 6) % W
        y = THAMES + 6 + k % 5 * 6
        d.line([(x, y), (x + 8, y)], fill=(200, 110, 80))
    for k, (fx, fy) in enumerate(((40, 98), (132, 96), (212, 102))):                 # fires, and their smoke
        for j in range(3):
            r = 6 + j * 5 + ((c.t * 0.8 + k * 0.3) % 1) * 3
            d.ellipse((fx - r + j * 4, fy - j * 12 - r * 0.7, fx + r + j * 4, fy - j * 12 + r * 0.7),
                      fill=(70, 60, 70) if j else (110, 84, 90))
        d.polygon([(fx - 5, fy + 6), (fx, fy - 5 - 2 * math.sin(c.t * 15 + k)), (fx + 5, fy + 6)], fill=(255, 160, 50))
    return img


def embankment(c):
    """The embankment in front, and the plinth."""
    d = ImageDraw.Draw(c.world)
    d.rectangle((0, 150, W, H), fill=(70, 64, 72))
    d.line([(0, 150), (W, 150)], fill=(110, 100, 110))
    x, y = STATUE
    d.rectangle((x - 41, y - 1, x + 41, 151), fill=INK)
    d.rectangle((x - 40, y, x + 40, 150), fill=(150, 146, 140))
    d.rectangle((x - 42, y - 3, x + 42, y), fill=(170, 166, 160))
    pixel.text(c.world, (x, y + 7), "ATTENBOROUGH", SILK, (60, 56, 60), shadow=None, anchor="ma")


scene("v2_london", mid=embankment, shots={"skyline": (160, 92, 6)},
      cast={"morgan": dict(x=64, y=166, facing=1, outfit="president", mic=True, z=1)})(london)


@lru_cache(maxsize=1)
def big_ben():
    """The Elizabeth Tower, lit by the fires: stone, a gold clock face and a spire."""
    s = Canvas(20, 92)
    stone, stone_sh = (170, 120, 96), (120, 80, 72)
    s.rect((5, 24, 14, 91), stone)
    s.line([(12, 24), (12, 91)], stone_sh); s.line([(13, 24), (13, 91)], stone_sh)
    for y in range(34, 90, 6):
        s.line([(7, y), (10, y)], stone_sh)
    s.rect((3, 14, 16, 30), stone)
    s.ell((5, 16, 14, 25), (255, 236, 160))
    s.line([(9, 20), (9, 17)], INK); s.line([(9, 20), (12, 20)], INK)
    s.poly([(3, 14), (9, 1), (10, 1), (16, 14)], stone_sh)
    s.rect((9, 0, 10, 1), (246, 200, 70))
    return s.done()


@lru_cache(maxsize=1)
def statue():
    """Sir David in bronze, twice life size, presenting. Returns (sprite, feet)."""
    import numpy as np
    from characters import figure
    img, a = figure("david", -1, arm="palm", mic=False)
    arr = np.array(img).astype(np.float32)
    body = (arr[..., 3] > 0) & ~np.all(arr[..., :3] == INK, axis=-1)
    lum = arr[..., :3].mean(axis=-1, keepdims=True) / 255.0
    dark, light = np.array((70, 50, 34), np.float32), np.array((200, 150, 84), np.float32)
    arr[..., :3] = np.where(body[..., None], dark + (light - dark) * lum, arr[..., :3])
    img = Image.fromarray(arr.round().astype(np.uint8))
    return scaled(img, 2), (a["feet"][0] * 2, a["feet"][1] * 2)
