"""Gag props and UI widgets, drawn at native resolution with outlined pixel shapes."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from pixelart.anim import back_out, ease_out  # noqa: F401  (re-exported for the gags)
from characters import SKIN, SKIN_SH, Sprite, _features, _grow, _mask, _shift
from engine import (CLAUDE_ORANGE, GOLD, OPENAI_GREEN, PAL, dither, font, mix, outline_text,
                    sprite, text_width)
from scene import PRESS, SILK, bevel, silk

K = PAL["k"]
WHITE = (255, 255, 255)
PAPER, PAPER_SH = (244, 234, 204), (206, 186, 146)
RED, RED_DK = (226, 52, 60), (150, 24, 40)
BLUE, BLUE_DK = (84, 146, 232), (44, 84, 164)
GRAY, GRAY_DK = (192, 192, 200), (120, 118, 134)
PRESS16 = font(size=16)
PRESS24 = font(size=24)

TEAM = {"sam": (OPENAI_GREEN, (8, 104, 80)), "dario": (CLAUDE_ORANGE, (160, 78, 52))}


# --- low-level helpers ------------------------------------------------------

class Prop:
    """A small RGBA canvas: draw flat shapes, then `done()` adds the outline."""

    def __init__(self, w, h):
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.d.fontmode = "1"

    def done(self, outline=K):
        arr = np.array(self.img)
        a = arr[:, :, 3] > 0
        ring = _grow(a) & ~a
        arr[ring] = tuple(outline) + (255,)
        return Image.fromarray(arr, "RGBA")


def paste(dst, src, x, y, anchor="lt"):
    w, h = src.size
    if anchor[0] == "m":
        x -= w // 2
    elif anchor[0] == "r":
        x -= w
    if anchor[1] == "m":
        y -= h // 2
    elif anchor[1] == "b":
        y -= h
    dst.paste(src, (int(x), int(y)), src)
    return int(x), int(y)


def pop(age, dur=0.18):
    """Pop-in offset in pixels (drops from above with a small bounce)."""
    if age < 0:
        return None
    return int(round((1 - back_out(age / dur)) * -10))


def big_text(img, xy, s, fnt=PRESS16, top=GOLD, bottom=(255, 138, 40), outline=K, shadow=2,
             anchor="la", thick=2):
    """Arcade title text: two-tone fill, thick outline and a hard drop shadow."""
    x, y = xy
    tw, th = text_width(s, fnt), fnt.size
    if anchor[0] == "m":
        x -= tw // 2
    elif anchor[0] == "r":
        x -= tw
    pad = thick + shadow + 1
    m = Image.new("L", (tw + 2 * pad, th + 2 * pad), 0)
    ImageDraw.Draw(m).text((pad, pad), s, font=fnt, fill=255)
    a = np.array(m) > 0
    ring = a.copy()
    for _ in range(thick):
        ring = _grow(ring)
    sh = _shift(ring, shadow, shadow)
    out = np.zeros(a.shape + (4,), np.uint8)
    out[sh & ~ring] = K + (255,)
    out[ring] = tuple(outline) + (255,)
    rows = np.arange(a.shape[0])[:, None]
    mid = pad + th * 0.55
    top_m = a & (rows < mid)
    out[top_m] = tuple(top) + (255,)
    out[a & ~top_m] = tuple(bottom) + (255,)
    out[a & ~_shift(a, 0, 1)] = tuple(mix(top, WHITE, 0.6)) + (255,)
    im = Image.fromarray(out, "RGBA")
    img.paste(im, (int(x - pad), int(y - pad)), im)
    return tw


def label(img, xy, s, bg=WHITE, fg=K, fnt=None, pad=2, anchor="la", border=K):
    """Text on a flat plate. Uses Silkscreen (small caps) unless a font is given."""
    fnt = fnt or SILK
    d = ImageDraw.Draw(img)
    tw = text_width(s, fnt)
    th = 6 if fnt is SILK else 8
    x, y = xy
    if anchor[0] == "m":
        x -= (tw + 2 * pad) // 2
    elif anchor[0] == "r":
        x -= tw + 2 * pad
    box = (x, y, x + tw + 2 * pad, y + th + 2 * pad - 1)
    d.rectangle((box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1), fill=border)
    d.rectangle(box, fill=bg)
    if fnt is SILK:
        silk(d, (x + pad + 1, y + pad), s, fg)
    else:
        d.fontmode = "1"
        d.text((x + pad + 1, y + pad), s, font=fnt, fill=fg)
    return box


def bubble(img, x, y, lines, tail=None, fnt=None, fill=WHITE, ink=K, pad=4, anchor="mb"):
    """Comic speech bubble with its tail tip at `tail`; (x, y) anchors the box."""
    fnt = fnt or PRESS
    if isinstance(lines, str):
        lines = [lines]
    lh = 10 if fnt is PRESS else 8
    tw = max(text_width(s, fnt) for s in lines)
    w, h = tw + 2 * pad + 2, len(lines) * lh + 2 * pad - 2
    if anchor[0] == "m":
        x -= w // 2
    elif anchor[0] == "r":
        x -= w
    if anchor[1] == "b":
        y -= h
    elif anchor[1] == "m":
        y -= h // 2
    x, y = int(x), int(y)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    if tail:
        tx, ty = tail
        bx = min(max(tx, x + 6), x + w - 7)
        by = y + h if ty > y + h else y
        base = [(bx - 4, by), (bx + 4, by)]
        d.polygon(base + [(tx, ty)], fill=ink)
        d.polygon([(bx - 3, by), (bx + 3, by), (tx + (1 if tx < bx else -1 if tx > bx else 0),
                                                ty + (-2 if ty > by else 2))], fill=fill)
    d.rounded_rectangle((x - 1, y - 1, x + w, y + h), radius=4, fill=ink)
    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=3, fill=fill)
    if tail:
        d.polygon([(bx - 3, by - (1 if ty > by else -1)), (bx + 3, by - (1 if ty > by else -1)),
                   (bx, by + (2 if ty > by else -2))], fill=fill)
    for i, s in enumerate(lines):
        lx = x + (w - text_width(s, fnt)) // 2 + 1
        ly = y + pad + i * lh
        if fnt is SILK:
            silk(d, (lx, ly), s, ink)
        else:
            d.text((lx, ly), s, font=fnt, fill=ink)
    return (x, y, x + w, y + h)


def thought(img, x, y, lines, toward, fnt=None):
    box = bubble(img, x, y, lines, None, fnt=fnt)
    d = ImageDraw.Draw(img)
    (x0, y0, x1, y1), (tx, ty) = box, toward
    sx, sy = (x0 + x1) / 2, y1 + 2
    for i, r in enumerate((3, 2, 1)):
        px = sx + (tx - sx) * (i + 1) / 4
        py = sy + (ty - sy) * (i + 1) / 4
        d.ellipse((px - r - 1, py - r - 1, px + r + 1, py + r + 1), fill=K)
        d.ellipse((px - r, py - r, px + r, py + r), fill=WHITE)
    return box


@lru_cache(maxsize=256)
def _stamp_img(s, color, angle, fnt_size):
    fnt = PRESS16 if fnt_size == 16 else PRESS
    tw = text_width(s, fnt)
    th = fnt.size
    pad = 4
    w, h = tw + 2 * pad + 4, th + 2 * pad + 3
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w - 1, h - 1), outline=color + (255,), width=2)
    d.text((pad + 2, pad + 2), s, font=fnt, fill=color + (255,))
    # Worn ink: knock out a sparse pattern of pixels.
    arr = np.array(im)
    rng = np.random.default_rng(len(s) * 7 + fnt_size)
    holes = rng.random(arr.shape[:2]) < 0.12
    arr[holes, 3] = 0
    im = Image.fromarray(arr, "RGBA").rotate(angle, resample=Image.NEAREST, expand=True)
    return im


def stamp(img, cx, cy, s, color=RED, angle=-12, big=True, age=1.0):
    """Rubber stamp that slams down (drops in over ~0.1 s)."""
    if age < 0:
        return
    im = _stamp_img(s, color, angle, 16 if big else 8)
    dy = int(round(max(0.0, 1 - age / 0.1) * -14))
    paste(img, im, cx, cy + dy, "mm")


def win95(img, x, y, w, h, title, active=True, close=True):
    """A Win95 window frame; returns the client box (x0, y0, x1, y1)."""
    d = ImageDraw.Draw(img)
    bevel(d, (x, y, x + w - 1, y + h - 1))
    c0, c1 = ((0, 0, 128), (16, 132, 208)) if active else ((128, 128, 128), (180, 180, 180))
    for i in range(w - 6):
        d.line([(x + 3 + i, y + 3), (x + 3 + i, y + 12)], fill=mix(c0, c1, i / max(1, w - 7)))
    silk(d, (x + 5, y + 5), title, WHITE)
    if close:
        bx = x + w - 13
        bevel(d, (bx, y + 4, bx + 8, y + 11))
        d.line([(bx + 2, y + 6), (bx + 5, y + 9)], fill=(0, 0, 0))
        d.line([(bx + 5, y + 6), (bx + 2, y + 9)], fill=(0, 0, 0))
    return (x + 3, y + 15, x + w - 4, y + h - 4)


def caption(img, x, y, s, bg=(20, 16, 36), fg=GOLD, anchor="la"):
    return label(img, (x, y), s, bg=bg, fg=fg, fnt=PRESS, pad=3, anchor=anchor, border=fg)


# --- small sprites ----------------------------------------------------------

PROP_PAL = {
    "k": K, "w": WHITE, "W": (224, 222, 232), "g": GRAY, "G": GRAY_DK, "d": (70, 68, 84),
    "r": RED, "R": RED_DK, "y": GOLD, "Y": (206, 150, 30), "b": BLUE, "B": BLUE_DK,
    "c": (180, 226, 255), "s": SKIN, "S": SKIN_SH, "p": (255, 150, 196), "P": (206, 90, 146),
    "u": (140, 92, 56), "U": (92, 58, 36), "t": PAPER, "T": PAPER_SH, "l": (96, 180, 72),
    "L": (52, 116, 44), "e": (8, 8, 12), "m": PAL["m"], "o": CLAUDE_ORANGE, "O": (160, 78, 52),
    "n": OPENAI_GREEN, "N": (8, 104, 80), "h": (236, 236, 244), "H": (176, 176, 196),
    "f": (255, 120, 40), "F": (255, 220, 90), "v": (150, 110, 220),
}


def ascii_sprite(rows, **overrides):
    pal = dict(PROP_PAL)
    pal.update(overrides)
    return sprite(rows, pal)


BOT_ROWS = [
    ".....kkk.....",
    ".....kyk.....",
    "......k......",
    "..kkkkkkkkk..",
    ".kooooooooOk.",
    ".kowwoowwoOk.",
    ".kowkoowkoOk.",
    ".kooooooooOk.",
    ".koooRRRooOk.",
    ".kOOOOOOOOOk.",
    "..kkkkkkkkk..",
    "...kdddddk...",
    "..kkooooOkk..",
    ".kokooooOkok.",
    ".kkkooooOkkk.",
    "...kok.kOk...",
    "...kkk.kkk...",
]


@lru_cache(maxsize=None)
def bot(team="dario", shades=False, chain=False, mask_=False):
    c, dk = TEAM[team]
    rows = [r for r in BOT_ROWS]
    if shades:
        rows[5] = ".kokkkokkkOk."
        rows[6] = ".kokkkokkkOk."
    if mask_:
        rows[5] = ".kkkkkkkkkkk."
        rows[6] = ".kkwkkkkwkkk."
    if chain:
        rows[12] = "..kkyyyyykk.."
        rows[13] = ".kokoyyyOkok."
    return ascii_sprite(rows, o=c, O=dk)


CHICKEN = [
    [
        "....kk........",
        "...krrk.......",
        "..kwwwwk......",
        "..kwkwwwk.....",
        ".kyywwwwk...k.",
        "kyyywwwwwk.kwk",
        ".kkkwwwwwwkwwk",
        "...kwwwwwwwwk.",
        "...kwwwwWwwwk.",
        "....kwwWWWwk..",
        ".....kkkkkk...",
        "......ky.ky...",
        ".....kyk.yk...",
        ".....kk...kk..",
    ],
    [
        "....kk........",
        "...krrk.......",
        "..kwwwwk......",
        "..kwkwwwk.....",
        ".kyywwwwk...k.",
        "kyyywwwwwk.kwk",
        ".kkkwwwwwwkwwk",
        "...kwwwwwwwwk.",
        "...kwwwwWwwwk.",
        "....kwwWWWwk..",
        ".....kkkkkk...",
        ".....kyk.ky...",
        "......ky..yk..",
        "......kk...k..",
    ],
]


@lru_cache(maxsize=None)
def chicken(frame=0):
    return ascii_sprite(CHICKEN[frame % 2])


STAR5 = ["..y..", ".yyy.", "yyyyy", ".y.y."]
SPARKLE = ["...w...", "...w...", "..www..", "wwwwwww", "..www..", "...w...", "...w..."]
SPARKLE_S = [".w.", "www", ".w."]
HEART = [
    ".kkk...kkk.",
    "krrrk.krrrk",
    "krwrrkrrrRk",
    "krrrrrrrrRk",
    ".krrrrrrRk.",
    "..krrrrRk..",
    "...krrRk...",
    "....kRk....",
    ".....k.....",
]
HEART_CRACK = [
    ".kkk...kkk.",
    "krrrk.krrrk",
    "krwrrkkrrRk",
    "krrrrk.krRk",
    ".krrrrk.kk.",
    "..krrk.krk.",
    "...kk.krRk.",
    "....k.kRk..",
    "......kk...",
]
BELL = [
    "....kk....",
    "...kyyk...",
    "..kyyyYk..",
    "..kyyyYk..",
    ".kyyyyyYk.",
    ".kyyyyyYk.",
    "kyyyyyyyYk",
    "kkkkkkkkkk",
    "....kYk...",
    ".....k....",
]
BUG = [
    [
        "k..k..k...",
        ".k.k.k....",
        "..kkkkkk..",
        "kkRrrrrRkk",
        "..kRrRrk..",
        "kkRrrrrRkk",
        "..kkkkkk..",
        ".k..k..k..",
    ],
    [
        ".k.k.k....",
        "k..k..k...",
        "..kkkkkk..",
        ".kRrrrrRk.",
        "kkkRrRrkkk",
        ".kRrrrrRk.",
        "..kkkkkk..",
        "k..k..k...",
    ],
]
HAND_UP = [
    "....kk......",
    "...kssk.....",
    "...kssk.....",
    "...kssk.....",
    "...ksskkk...",
    "...ksskssk..",
    ".kkksskssKk.",
    "ksskssksskSk",
    "ksskssssssSk",
    "ksssssssssSk",
    ".ksssssssSk.",
    ".ksssssssSk.",
    "..kssssssk..",
    "..kbbbbbbk..",
    "..kbbbbbBk..",
    "..kbbbbbBk..",
]
MUSTACHE = [".kk...kk.", "kUUk.kUUk", "kUUUkUUUk", ".kkUUUkk.", "...kkk..."]
NOSE_CLOWN = [".kkk.", "krrrk", "krwrk", "krrRk", ".kkk."]
SWEAT_BIG = ["..k..", ".kck.", "kcccb", "kcwcb", ".kbb."]
Z_ROWS = ["kkkk", "..k.", ".k..", "kkkk"]
DIZZY = ["..y..", ".yYy.", "yYwYy", ".yYy.", "..y.."]


# --- procedural props -------------------------------------------------------

@lru_cache(maxsize=None)
def bomb(spark=0):
    p = Prop(22, 22)
    d = p.d
    d.ellipse((2, 6, 18, 21), fill=(40, 40, 52))
    d.ellipse((5, 9, 9, 13), fill=(110, 110, 130))
    d.rectangle((8, 3, 12, 7), fill=(70, 70, 86))
    d.line([(12, 3), (14, 1), (17, 1)], fill=PAPER_SH)
    img = p.done()
    ImageDraw.Draw(img).point([(18, 0), (19, 1), (17, 0), (18, 2)][spark % 2::2], fill=GOLD)
    return img


@lru_cache(maxsize=None)
def shelter():
    p = Prop(34, 26)
    d = p.d
    d.rectangle((2, 12, 31, 25), fill=(120, 124, 110))
    d.polygon([(0, 13), (16, 2), (33, 13)], fill=(86, 92, 80))
    d.rectangle((12, 16, 20, 25), fill=(60, 60, 64))
    d.rectangle((13, 17, 19, 25), fill=(170, 150, 60))
    for x in range(4, 31, 5):
        d.line([(x, 14), (x, 24)], fill=(104, 108, 96))
    img = p.done()
    return img


@lru_cache(maxsize=None)
def radio():
    p = Prop(30, 22)
    d = p.d
    d.line([(22, 0), (27, 6)], fill=GRAY)
    d.rounded_rectangle((1, 6, 28, 21), radius=3, fill=(160, 80, 60))
    d.rectangle((3, 9, 13, 18), fill=(70, 50, 44))
    for y in range(10, 18, 2):
        d.line([(4, y), (12, y)], fill=(40, 30, 28))
    d.rectangle((16, 9, 26, 13), fill=(236, 220, 160))
    d.line([(20, 9), (20, 13)], fill=RED)
    d.ellipse((17, 15, 20, 18), fill=GRAY)
    d.ellipse((23, 15, 26, 18), fill=GRAY)
    return p.done()


def laurel(img, cx, top, w=30):
    """Leafy wreath hugging the top of a head (world space)."""
    d = ImageDraw.Draw(img)
    for side in (-1, 1):
        for i in range(7):
            a = math.radians(200 + i * 20) if side < 0 else math.radians(340 - i * 20)
            x = cx + math.cos(a) * w / 2
            y = top + 10 + math.sin(a) * 9
            d.ellipse((x - 2.5, y - 1.5, x + 2.5, y + 1.5), fill=(22, 60, 20))
            d.ellipse((x - 1.5, y - 1, x + 1.5, y + 0.5), fill=(110, 200, 80) if i % 2 else (70, 160, 60))


@lru_cache(maxsize=None)
def book(title="POEMS", w=26, h=32, color=(120, 60, 140), pages=0):
    p = Prop(w + pages + 2, h + pages + 2)
    d = p.d
    if pages:
        d.rectangle((pages, pages + 2, w + pages, h + pages), fill=PAPER)
        for i in range(0, pages, 2):
            d.line([(w + i // 2 + 1, i + 3), (w + i // 2 + 1, h + i // 2)], fill=PAPER_SH)
    d.rectangle((0, 0, w - 1, h - 1), fill=color)
    d.rectangle((0, 0, 2, h - 1), fill=mix(color, (0, 0, 0), 0.35))
    d.rectangle((6, 5, w - 4, 12), fill=mix(color, WHITE, 0.25))
    img = p.done()
    dd = ImageDraw.Draw(img)
    silk(dd, (w // 2 + 2, 7), title, GOLD, anchor="ma")
    return img


def signal_bars(img, x, y, n=1, total=4, color=GOLD):
    d = ImageDraw.Draw(img)
    for i in range(total):
        h = 4 + i * 4
        box = (x + i * 6, y + 16 - h, x + i * 6 + 4, y + 16)
        d.rectangle((box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1), fill=K)
        d.rectangle(box, fill=color if i < n else (60, 56, 76))


def scroll(img, x, y, w, lines, unroll=1.0, fnt=None, title=None, ink=(70, 40, 20)):
    """Parchment scroll unrolling downward; returns its bottom y."""
    fnt = fnt or SILK
    lh = 9
    full = (len(lines) + (1.6 if title else 0)) * lh + 10
    h = max(6, int(full * min(max(unroll, 0), 1)))
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y + 2, x + w, y + h + 1), fill=K)
    d.rectangle((x, y + 3, x + w - 1, y + h), fill=PAPER)
    d.line([(x + w - 2, y + 3), (x + w - 2, y + h)], fill=PAPER_SH)
    ty = y + 7
    if title:
        if ty + 8 < y + h:
            outline_text(img, (x + w // 2, ty - 1), title, PRESS, RED_DK, outline=PAPER, anchor="ma")
        ty += int(1.6 * lh)
    for s in lines:
        if ty + 6 > y + h:
            break
        silk(d, (x + w // 2, ty), s, ink, anchor="ma") if fnt is SILK else d.text(
            (x + w // 2, ty), s, font=fnt, fill=ink, anchor="ma")
        ty += lh
    for yy in (y, y + h):
        d.rounded_rectangle((x - 3, yy - 1, x + w + 2, yy + 4), radius=2, fill=K)
        d.rounded_rectangle((x - 2, yy, x + w + 1, yy + 3), radius=1, fill=(200, 170, 110))
        d.line([(x - 1, yy + 1), (x + w, yy + 1)], fill=(236, 214, 160))
    return y + h + 4


def chart_frame(img, x, y, w, h, title=None):
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=(250, 248, 240))
    for gy in range(y + 8, y + h - 8, 8):
        d.line([(x + 10, gy), (x + w - 4, gy)], fill=(222, 222, 230))
    d.line([(x + 10, y + 4), (x + 10, y + h - 8), (x + w - 4, y + h - 8)], fill=K)
    if title:
        silk(d, (x + w // 2, y + 2), title, K, anchor="ma")


def police_tape(img, x0, y0, x1, y1, s="CHART CRIME", phase=0):
    """Diagonal yellow/black tape with repeating text."""
    length = int(math.hypot(x1 - x0, y1 - y0))
    strip = Image.new("RGBA", (length, 11), GOLD + (255,))
    d = ImageDraw.Draw(strip)
    d.line([(0, 0), (length, 0)], fill=K)
    d.line([(0, 10), (length, 10)], fill=K)
    x = -phase
    while x < length:
        silk(d, (x + 4, 3), s, K)
        x += text_width(s, SILK) + 10
        d.rectangle((x - 6, 2, x - 4, 8), fill=K)
    ang = -math.degrees(math.atan2(y1 - y0, x1 - x0))
    rot = strip.rotate(ang, resample=Image.NEAREST, expand=True)
    paste(img, rot, (x0 + x1) // 2, (y0 + y1) // 2, "mm")


def keycap(img, x, y, label_, pressed=0, led=None):
    from scene import draw_keycap
    w = draw_keycap(img, x, y, label_, pressed)
    if led is not None:
        d = ImageDraw.Draw(img)
        d.rectangle((x + w - 7, y + 4 + pressed, x + w - 5, y + 5 + pressed),
                    fill=(90, 255, 120) if led else (40, 60, 44))
    return w


def pentagon(img, cx, cy, r=14):
    d = ImageDraw.Draw(img)
    pts = [(cx + r * math.cos(math.radians(-90 + i * 72)), cy + r * math.sin(math.radians(-90 + i * 72)))
           for i in range(5)]
    d.polygon(pts, fill=K)
    inner = [(cx + (px - cx) * 0.86, cy + (py - cy) * 0.86) for px, py in pts]
    d.polygon(inner, fill=(150, 156, 140))
    core = [(cx + (px - cx) * 0.45, cy + (py - cy) * 0.45) for px, py in pts]
    d.polygon(core, fill=K)
    core2 = [(cx + (px - cx) * 0.33, cy + (py - cy) * 0.33) for px, py in pts]
    d.polygon(core2, fill=(96, 120, 80))


def paper(img, x, y, w, h, lines=0, title=None, fill=WHITE):
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=fill)
    d.polygon([(x + w - 6, y), (x + w - 1, y + 5), (x + w - 6, y + 5)], fill=(210, 210, 220))
    ly = y + (14 if title else 5)
    if title:
        silk(d, (x + w // 2, y + 4), title, K, anchor="ma")
    for i in range(lines):
        if ly + 2 > y + h - 3:
            break
        d.line([(x + 4, ly), (x + w - 5 - (i % 3) * 5, ly)], fill=(170, 170, 186))
        ly += 4


def calendar(img, x, y, top_text, big, color=RED):
    d = ImageDraw.Draw(img)
    w, h = 34, 34
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=WHITE)
    d.rectangle((x, y, x + w - 1, y + 9), fill=color)
    silk(d, (x + w // 2 + 1, y + 2), top_text, WHITE, anchor="ma")
    d.fontmode = "1"
    d.text((x + w // 2 + 1, y + 14), big, font=PRESS16, fill=K, anchor="ma")
    for rx in (x + 8, x + w - 9):
        d.rectangle((rx - 1, y - 3, rx + 1, y + 2), fill=K)


def newspaper(img, x, y, headline, sub="", masthead="THE DAILY BYTE"):
    d = ImageDraw.Draw(img)
    w = max(96, text_width(headline, PRESS) + 14)
    h = 58
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=(236, 232, 220))
    silk(d, (x + w // 2 + 1, y + 3), masthead, K, anchor="ma")
    d.line([(x + 3, y + 11), (x + w - 4, y + 11)], fill=K)
    d.line([(x + 3, y + 13), (x + w - 4, y + 13)], fill=K)
    d.fontmode = "1"
    d.text((x + w // 2 + 1, y + 17), headline, font=PRESS, fill=K, anchor="ma")
    if sub:
        silk(d, (x + w // 2 + 1, y + 29), sub, (90, 90, 100), anchor="ma")
    for i in range(4):
        ly = y + 39 + i * 4
        d.line([(x + 4, ly), (x + w // 2 - 4, ly)], fill=(160, 160, 170))
        d.line([(x + w // 2 + 3, ly), (x + w - 5, ly)], fill=(160, 160, 170))
    return w


@lru_cache(maxsize=None)
def bread(broken=0):
    """A loaf; broken > 0 splits it into two halves `broken` px apart."""
    p = Prop(36 + broken, 18)
    d = p.d
    halves = [(0, 0)] if not broken else [(0, 0), (broken, 1)]
    for i, (dx, _) in enumerate(halves):
        box = (1 + dx, 3, 34 + dx, 16)
        if broken:
            box = (1, 3, 17, 16) if i == 0 else (18 + broken, 3, 34 + broken, 16)
        d.rounded_rectangle(box, radius=6, fill=(200, 130, 60))
        d.rounded_rectangle((box[0] + 1, box[1], box[2] - 1, box[1] + 5), radius=3, fill=(226, 164, 88))
    for sx in (8, 16, 24):
        if not broken or abs(sx - 17) > 3:
            x = sx + (broken if broken and sx > 17 else 0)
            d.line([(x, 5), (x + 3, 8)], fill=(150, 90, 40))
    img = p.done()
    if broken:
        d2 = ImageDraw.Draw(img)
        d2.rectangle((17, 5, 17, 14), fill=(250, 230, 180))
        d2.rectangle((18 + broken, 5, 18 + broken, 14), fill=(250, 230, 180))
    return img


@lru_cache(maxsize=None)
def brain():
    p = Prop(30, 24)
    d = p.d
    d.ellipse((1, 3, 16, 20), fill=(255, 160, 190))
    d.ellipse((12, 2, 28, 20), fill=(255, 160, 190))
    d.rectangle((12, 16, 18, 23), fill=(230, 130, 160))
    for pts in ([(5, 8), (9, 6), (12, 9)], [(4, 14), (8, 12), (11, 15)], [(17, 7), (21, 5), (24, 8)],
                [(16, 13), (20, 11), (25, 14)], [(14, 4), (14, 17)]):
        d.line(pts, fill=(200, 90, 130))
    return p.done()


@lru_cache(maxsize=None)
def hugging_face(robbed=False):
    """Yellow smiley with open hands (a nod to the 'hugging face' emoji)."""
    p = Prop(40, 34)
    d = p.d
    d.ellipse((6, 1, 33, 28), fill=(255, 206, 60))
    d.ellipse((6, 1, 33, 28), outline=(236, 170, 30))
    d.ellipse((9, 3, 30, 22), fill=(255, 222, 96))
    if robbed:
        d.arc((12, 17, 27, 27), 200, 340, fill=(100, 50, 20))
        d.point([(14, 12), (15, 11), (24, 11), (25, 12)], fill=(100, 50, 20))
        d.ellipse((17, 19, 22, 24), fill=(120, 40, 40))
    else:
        d.chord((12, 12, 27, 25), 0, 180, fill=(120, 40, 40))
        d.arc((12, 8, 17, 13), 200, 340, fill=(100, 50, 20))
        d.arc((22, 8, 27, 13), 200, 340, fill=(100, 50, 20))
    for hx in (1, 31):
        d.rounded_rectangle((hx, 18, hx + 8, 29), radius=3, fill=(255, 196, 50))
        d.line([(hx + 2, 19), (hx + 2, 23)], fill=(236, 160, 30))
        d.line([(hx + 5, 19), (hx + 5, 23)], fill=(236, 160, 30))
    return p.done()


@lru_cache(maxsize=None)
def loot_bag(text="ANSWER KEY"):
    p = Prop(28, 24)
    d = p.d
    d.ellipse((2, 6, 26, 23), fill=(150, 120, 80))
    d.polygon([(9, 7), (19, 7), (16, 2), (12, 2)], fill=(130, 100, 64))
    d.line([(10, 7), (18, 7)], fill=(90, 64, 40))
    img = p.done()
    silk(ImageDraw.Draw(img), (14, 12), "$", GOLD, anchor="ma")
    return img


def bubble_sheet(img, x, y, filled_seed=3, rows=6):
    d = ImageDraw.Draw(img)
    w, h = 64, 12 + rows * 7
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=(236, 244, 236))
    silk(d, (x + w // 2 + 1, y + 2), "SAT  ANSWERS", (40, 90, 60), anchor="ma")
    rng = np.random.default_rng(filled_seed)
    for r in range(rows):
        silk(d, (x + 3, y + 11 + r * 7), str(r + 1), (40, 90, 60))
        pick = rng.integers(0, 5)
        for c in range(5):
            cx, cy = x + 14 + c * 10, y + 13 + r * 7
            d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), outline=(40, 90, 60),
                      fill=(20, 20, 30) if c == pick else None)


def tile_grid(img, x, y, n=3, size=20):
    """CAPTCHA-style grid; returns tile boxes row-major."""
    d = ImageDraw.Draw(img)
    boxes = []
    for r in range(n):
        for c in range(n):
            bx, by = x + c * (size + 2), y + r * (size + 2)
            boxes.append((bx, by, bx + size - 1, by + size - 1))
            d.rectangle(boxes[-1], fill=(120, 150, 170))
    return boxes


def tile_art(img, box, kind, seed=0):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    d.rectangle((x0, y0, x1, y0 + 9), fill=(150, 196, 236))
    d.rectangle((x0, y0 + 10, x1, y1), fill=(96, 100, 110))
    d.line([(x0, y0 + 15), (x1, y0 + 15)], fill=(220, 220, 180))
    if kind == "bus":
        d.rectangle((x0 + 2, y0 + 5, x1 - 2, y0 + 15), fill=K)
        d.rectangle((x0 + 3, y0 + 6, x1 - 3, y0 + 14), fill=GOLD)
        for wx in range(x0 + 4, x1 - 4, 4):
            d.rectangle((wx, y0 + 7, wx + 2, y0 + 9), fill=(120, 170, 220))
        d.point([(x0 + 5, y0 + 16), (x1 - 5, y0 + 16)], fill=K)
    elif kind == "tree":
        cx = int(x0 + 6 + rng.integers(0, 8))
        d.rectangle((cx - 1, y0 + 9, cx + 1, y0 + 15), fill=(100, 70, 40))
        d.ellipse((cx - 5, y0 + 1, cx + 5, y0 + 11), fill=(60, 140, 60))
    elif kind == "light":
        d.rectangle((x0 + 9, y0 + 1, x0 + 12, y0 + 11), fill=K)
        for i, c in enumerate(((230, 60, 50), (240, 200, 40), (60, 200, 90))):
            d.point((x0 + 10, y0 + 2 + i * 3), fill=c)
            d.point((x0 + 11, y0 + 2 + i * 3), fill=c)
        d.line([(x0 + 10, y0 + 12), (x0 + 10, y0 + 16)], fill=K)
    elif kind == "hydrant":
        d.rectangle((x0 + 8, y0 + 8, x0 + 12, y0 + 16), fill=(210, 50, 50))
        d.rectangle((x0 + 7, y0 + 10, x0 + 13, y0 + 11), fill=(210, 50, 50))


@lru_cache(maxsize=None)
def ladder(h=40):
    p = Prop(16, h)
    d = p.d
    d.rectangle((1, 0, 3, h - 1), fill=(170, 120, 70))
    d.rectangle((12, 0, 14, h - 1), fill=(170, 120, 70))
    for y in range(4, h - 1, 6):
        d.rectangle((3, y, 12, y + 1), fill=(200, 150, 90))
    return p.done()


def gavel(img, x, y, angle=0):
    p = Prop(34, 34)
    d = p.d
    d.rounded_rectangle((4, 4, 22, 13), radius=2, fill=(140, 84, 44))
    d.rectangle((9, 4, 11, 13), fill=GOLD)
    d.rectangle((12, 13, 15, 31), fill=(170, 110, 60))
    im = p.done().rotate(angle, resample=Image.NEAREST, center=(14, 30))
    paste(img, im, x, y, "mb")


@lru_cache(maxsize=None)
def cannon():
    p = Prop(46, 28)
    d = p.d
    d.polygon([(4, 10), (36, 2), (40, 12), (8, 20)], fill=(60, 60, 72))
    d.polygon([(6, 11), (36, 4), (37, 7), (7, 14)], fill=(96, 96, 112))
    d.ellipse((34, 0, 44, 14), fill=(40, 40, 50))
    d.ellipse((37, 3, 41, 10), fill=K)
    d.ellipse((6, 12, 22, 27), fill=(120, 76, 40))
    d.ellipse((11, 17, 17, 22), fill=(80, 50, 28))
    return p.done()


def smoke(img, cx, cy, age, n=5, seed=1):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r = 4 + age * rng.uniform(18, 30)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.6 - age * 10
        s = max(1.0, 6 - age * 7)
        c = mix((236, 236, 240), (150, 150, 160), min(1, age * 2))
        d.ellipse((x - s - 1, y - s - 1, x + s + 1, y + s + 1), fill=K)
        d.ellipse((x - s, y - s, x + s, y + s), fill=c)


@lru_cache(maxsize=None)
def map_prop():
    p = Prop(60, 42)
    d = p.d
    cols = [(236, 226, 190), (220, 208, 170), (236, 226, 190), (220, 208, 170)]
    for i, c in enumerate(cols):
        x0 = 1 + i * 14
        d.polygon([(x0, 2 + (i % 2) * 2), (x0 + 14, 2 + ((i + 1) % 2) * 2),
                   (x0 + 14, 40 - ((i + 1) % 2) * 2), (x0, 40 - (i % 2) * 2)], fill=c)
    d.line([(4, 30), (14, 22), (26, 26), (38, 14), (54, 18)], fill=(90, 170, 220), width=2)
    d.line([(8, 8), (20, 16), (30, 10), (46, 32)], fill=(220, 120, 100))
    d.ellipse((34, 22, 44, 30), fill=(120, 190, 100))
    img = p.done()
    return img


def pin(img, x, y):
    d = ImageDraw.Draw(img)
    d.polygon([(x - 4, y - 8), (x + 4, y - 8), (x, y)], fill=K)
    d.ellipse((x - 5, y - 14, x + 5, y - 4), fill=K)
    d.ellipse((x - 4, y - 13, x + 4, y - 5), fill=RED)
    d.polygon([(x - 3, y - 7), (x + 3, y - 7), (x, y - 1)], fill=RED)
    d.point((x - 2, y - 11), fill=WHITE)


@lru_cache(maxsize=None)
def sandbox():
    p = Prop(64, 22)
    d = p.d
    d.polygon([(6, 4), (58, 4), (63, 17), (1, 17)], fill=(150, 100, 60))
    d.polygon([(9, 6), (55, 6), (58, 14), (6, 14)], fill=(236, 206, 140))
    d.line([(1, 17), (63, 17)], fill=(110, 70, 40))
    d.rectangle((1, 18, 63, 20), fill=(120, 80, 48))
    for sx, sy in ((14, 9), (26, 11), (40, 8), (48, 12), (20, 12)):
        d.point((sx, sy), fill=(210, 176, 110))
    d.polygon([(44, 7), (50, 7), (49, 12), (45, 12)], fill=(220, 60, 60))
    d.arc((44, 4, 50, 10), 180, 360, fill=K)
    return p.done()


@lru_cache(maxsize=None)
def crib():
    p = Prop(40, 26)
    d = p.d
    d.rectangle((2, 10, 37, 20), fill=(236, 220, 190))
    for x in range(4, 37, 4):
        d.rectangle((x, 2, x + 1, 20), fill=(200, 160, 120))
    d.rectangle((0, 0, 3, 25), fill=(170, 120, 80))
    d.rectangle((36, 0, 39, 25), fill=(170, 120, 80))
    d.rectangle((2, 2, 37, 3), fill=(190, 140, 96))
    return p.done()


@lru_cache(maxsize=None)
def envelope(open_=False):
    p = Prop(26, 18)
    d = p.d
    d.rectangle((1, 3, 24, 16), fill=WHITE)
    d.line([(1, 3), (12, 11), (24, 3)], fill=(180, 180, 196))
    d.ellipse((10, 8, 15, 13), fill=RED)
    return p.done()


@lru_cache(maxsize=None)
def road_sign(text1="SLOW", text2="DOWN"):
    p = Prop(36, 50)
    d = p.d
    d.rectangle((16, 30, 19, 49), fill=GRAY_DK)
    d.polygon([(18, 1), (34, 17), (18, 33), (2, 17)], fill=GOLD)
    img = p.done()
    dd = ImageDraw.Draw(img)
    dd.polygon([(18, 4), (31, 17), (18, 30), (5, 17)], outline=K)
    silk(dd, (19, 11), text1, K, anchor="ma")
    silk(dd, (19, 18), text2, K, anchor="ma")
    return img


@lru_cache(maxsize=None)
def medal(text="1ST"):
    p = Prop(22, 30)
    d = p.d
    d.polygon([(4, 0), (9, 0), (12, 12), (7, 12)], fill=(60, 110, 220))
    d.polygon([(13, 0), (18, 0), (15, 12), (10, 12)], fill=(220, 60, 60))
    d.ellipse((2, 10, 20, 28), fill=GOLD)
    d.ellipse((5, 13, 17, 25), fill=(255, 232, 120))
    img = p.done()
    silk(ImageDraw.Draw(img), (12, 17), text, (150, 100, 20), anchor="ma")
    return img


@lru_cache(maxsize=None)
def uncle_sam_hat():
    p = Prop(28, 26)
    d = p.d
    d.rectangle((6, 1, 21, 20), fill=WHITE)
    for x in range(8, 21, 4):
        d.rectangle((x, 1, x + 1, 20), fill=RED)
    d.rectangle((6, 14, 21, 19), fill=(40, 60, 170))
    for x in (9, 13, 17):
        d.point((x, 16), fill=WHITE)
        d.point((x, 17), fill=WHITE)
    d.rounded_rectangle((0, 20, 27, 24), radius=2, fill=(40, 60, 170))
    return p.done()


@lru_cache(maxsize=None)
def fedora():
    p = Prop(36, 16)
    d = p.d
    d.rounded_rectangle((8, 1, 27, 11), radius=4, fill=(120, 96, 70))
    d.line([(15, 1), (18, 4), (21, 1)], fill=(90, 70, 50))
    d.rectangle((8, 8, 27, 10), fill=(50, 40, 34))
    d.rounded_rectangle((0, 10, 35, 14), radius=2, fill=(110, 88, 64))
    return p.done()


@lru_cache(maxsize=None)
def trench_collar():
    p = Prop(30, 14)
    d = p.d
    d.polygon([(0, 0), (12, 13), (6, 13), (0, 6)], fill=(196, 166, 110))
    d.polygon([(29, 0), (17, 13), (23, 13), (29, 6)], fill=(196, 166, 110))
    return p.done()


def x_mark(img, cx, cy, r=5, color=RED):
    d = ImageDraw.Draw(img)
    for w, c in ((5, K), (3, color)):
        d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=c, width=w)
        d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=c, width=w)


def check_mark(img, cx, cy, color=(60, 200, 90)):
    d = ImageDraw.Draw(img)
    for w, c in ((5, K), (3, color)):
        d.line([(cx - 5, cy), (cx - 1, cy + 4), (cx + 6, cy - 5)], fill=c, width=w)


def waveform(img, x, y, w, h, t, color=(120, 200, 255), bars=14, active=True):
    d = ImageDraw.Draw(img)
    for i in range(bars):
        amp = (0.25 + 0.75 * abs(math.sin(t * 9 + i * 1.7) * math.sin(t * 5.3 + i))) if active else 0.1
        bh = max(1, int(h * amp))
        bx = x + i * (w // bars)
        d.rectangle((bx - 1, y + (h - bh) // 2 - 1, bx + 2, y + (h + bh) // 2 + 1), fill=K)
        d.rectangle((bx, y + (h - bh) // 2, bx + 1, y + (h + bh) // 2), fill=color)


def flames(img, x, y, w, t, h=14):
    d = ImageDraw.Draw(img)
    for i in range(0, w, 5):
        fh = h * (0.55 + 0.45 * abs(math.sin(t * 13 + i * 0.9)))
        pts = [(x + i - 1, y), (x + i + 3, y - fh), (x + i + 7, y)]
        d.polygon(pts, fill=K)
        d.polygon([(x + i, y), (x + i + 3, y - fh + 2), (x + i + 6, y)], fill=(255, 110, 40))
        d.polygon([(x + i + 2, y), (x + i + 3, y - fh * 0.5), (x + i + 4, y)], fill=GOLD)


def confetti(img, t, n=90, seed=5, area=(0, 0, 320, 180)):
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = area
    cols = [GOLD, OPENAI_GREEN, CLAUDE_ORANGE, (255, 80, 160), (80, 220, 255), WHITE]
    for i in range(n):
        sx = rng.uniform(x0, x1)
        speed = rng.uniform(18, 40)
        start = rng.uniform(0, 3)
        y = y0 - 10 + ((t + start) * speed) % (y1 - y0 + 20)
        x = sx + math.sin(t * 3 + i) * 4
        c = cols[i % len(cols)]
        if int(t * 8 + i) % 2:
            d.rectangle((x, y, x + 1, y + 2), fill=c)
        else:
            d.rectangle((x, y, x + 2, y + 1), fill=c)


# --- cameo portraits (same construction as the main heads) ------------------

@lru_cache(maxsize=None)
def grandma_head(mouth="closed"):
    spr = Sprite(36, 36)
    face = _mask(lambda d: d.ellipse((6, 9, 30, 34), fill=1))
    ears = _mask(lambda d: (d.ellipse((4, 19, 9, 26), fill=1), d.ellipse((27, 19, 32, 26), fill=1)))
    head = face | ears
    rows = np.arange(36)[:, None]
    hair = (_mask(lambda d: d.ellipse((4, 4, 32, 30), fill=1)) & (rows < 17)) | \
        _mask(lambda d: d.ellipse((12, -1, 24, 9), fill=1))
    hair |= _mask(lambda d: (d.rectangle((4, 14, 7, 22), fill=1), d.rectangle((29, 14, 32, 22), fill=1)))
    spr.fill(head, SKIN)
    spr.fill(head & ~_shift(head, 2, -2), SKIN_SH)
    spr.fill(hair, (232, 232, 240))
    spr.fill(hair & ~_shift(hair, -1, 2), WHITE)
    spr.fill(hair & _shift(head & ~hair, 0, -1), (176, 176, 196))
    spr.fill(_mask(lambda d: d.arc((12, 0, 24, 9), 200, 340, fill=1)) & hair, (190, 190, 206))
    spr.fill(_mask(lambda d: d.point([(9, 27), (10, 27), (26, 27), (27, 27)], fill=1)), (236, 150, 150))
    spec = dict(iris=(90, 120, 170), eye_x=(10, 21), eye_y=20, brow_y=17, brow_thick=1,
                brow=(200, 200, 214), mouth=(18.5, 30))
    _features(spr, spec, "happy", "neutral", mouth)
    for x0 in (8, 19):
        ring = _mask(lambda d: d.ellipse((x0, 17, x0 + 9, 25), outline=1))
        spr.fill(ring, (200, 160, 60))
    spr.fill(_mask(lambda d: d.line([(17, 21), (19, 21)], fill=1)), (200, 160, 60))
    spr.outline()
    return spr.image()


def cutin(img, x, y, w, h, color, head, name=None, flip=False):
    """Fighting-game cut-in panel with a portrait (head image) inside."""
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=color)
    for i in range(-h, w, 6):
        d.line([(x + i, y + h - 1), (x + i + h, y)], fill=mix(color, WHITE, 0.18))
    hx = x + (w - head.width) // 2
    hy = y + h - head.height + 4
    region = img.crop((x, y, x + w, y + h))
    tmp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = head.transpose(Image.FLIP_LEFT_RIGHT) if flip else head
    tmp.paste(hd, (hx - x, hy - y), hd)
    region.paste(tmp, (0, 0), tmp)
    img.paste(region, (x, y))
    if name:
        label(img, (x + w // 2, y + h - 6), name, bg=K, fg=WHITE, anchor="ma", pad=1)


@lru_cache(maxsize=None)
def chat_window(team, title):
    """Empty chat window chrome (body drawn by caller)."""
    c, dk = TEAM[team]
    p = Prop(96, 58)
    d = p.d
    d.rectangle((0, 0, 95, 57), fill=(250, 250, 252))
    d.rectangle((0, 0, 95, 10), fill=c)
    img = p.done()
    dd = ImageDraw.Draw(img)
    silk(dd, (5, 3), title, WHITE)
    for i, cc in enumerate(((255, 96, 86), (255, 190, 46), (40, 200, 64))):
        dd.point([(86 - i * 4, 5), (87 - i * 4, 5)], fill=cc)
    return img
