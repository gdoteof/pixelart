"""Canvas, palette and fonts for Two Georges, bound onto pixelart.pixel.

Everything is drawn at 320x180 and shown 6x (nearest-neighbour) at 1080p.
Map convention throughout: America (west) on the left, Britain (east) on the right.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from pixelart import pixel
from pixelart.anim import (arc_pt, back_out, clamp, ease_in, ease_in_out, ease_out, lerp, pop_dy,  # noqa: F401
                           ramp, rnd, wobble)
from pixelart.pixel import dither, dither_poly, dither_rect, mix, text_width  # noqa: F401

W, H = 320, 180
SCALE = 6
ROOT = Path(__file__).parent

INK = (34, 22, 30)
C = {
    "ink": INK,
    # skin, hair
    "skin": (244, 204, 174), "skin_sh": (216, 164, 136), "flush": (232, 120, 110),
    "wig": (238, 236, 244), "wig_sh": (188, 184, 206),
    "hair": (214, 214, 224), "hair_sh": (168, 168, 186),
    # King George III: red coat, ermine, Garter sash, gold
    "red": (186, 36, 46), "red_sh": (124, 22, 36), "red_hi": (222, 70, 72),
    "gold": (246, 200, 70), "gold_sh": (188, 130, 36), "gold_hi": (255, 240, 170),
    "ermine": (250, 250, 250), "ermine_sh": (210, 210, 222),
    "sash": (64, 116, 214), "sash_sh": (40, 74, 160),
    "jewel": (220, 40, 70),
    # Washington: Continental blue and buff
    "navy": (38, 58, 122), "navy_sh": (24, 36, 82), "navy_hi": (70, 96, 168),
    "buff": (226, 198, 140), "buff_sh": (182, 150, 100),
    "hat": (36, 32, 42), "hat_hi": (72, 66, 84),
    "boot": (30, 24, 28), "boot_hi": (78, 66, 70),
    # town crier: bottle-green coat
    "green": (46, 106, 78), "green_sh": (28, 70, 58), "green_hi": (80, 146, 100),
    "brown": (120, 76, 50), "brown_sh": (82, 50, 40),
    # shared
    "white": (246, 244, 236), "white_sh": (200, 198, 206),
    "mouth": (130, 40, 52), "tongue": (206, 86, 96), "eye": (26, 20, 40),
    "mic": (60, 60, 70), "mic_hi": (150, 150, 164), "steel": (196, 204, 220), "steel_sh": (120, 128, 150),
    "sweat": (150, 200, 255), "tear": (150, 200, 255),
    "paper": (240, 228, 196), "paper_sh": (196, 176, 150), "wax": (196, 36, 48), "wax_hi": (236, 90, 90),
    "iron": (52, 50, 60), "iron_hi": (104, 102, 118),
    "wood": (150, 98, 64), "wood_sh": (96, 60, 58), "wood_hi": (206, 148, 96), "wood_deep": (62, 40, 50),
    "olive": (110, 140, 70),
    "flag_red": (206, 44, 52), "flag_white": (244, 240, 236), "flag_blue": (40, 58, 140),
    "text": (240, 236, 248), "dim": (150, 140, 180), "band": (18, 14, 32), "band_edge": (54, 42, 84),
    "sun": (255, 236, 176), "sun_core": (255, 250, 226), "glint": (255, 214, 146),
}

PRESS = pixel.font(size=8)
PRESS16 = pixel.font(size=16)
PRESS24 = pixel.font(size=24)
SILK = pixel.font("Silkscreen-Regular.ttf", 8)
SILK16 = pixel.font("Silkscreen-Regular.ttf", 16)


def text(img, xy, s, fnt=PRESS, fill=C["text"], shadow=(0, 0, 0), anchor="la"):
    pixel.text(img, xy, s, fnt, fill, shadow, anchor)


def outline_text(img, xy, s, fnt=PRESS, fill=C["text"], outline=INK, anchor="la"):
    pixel.outline_text(img, xy, s, fnt, fill, outline, anchor)


def mask(draw_fn):
    """Coverage mask over the whole canvas; see pixelart.pixel.mask."""
    return pixel.mask(draw_fn, (W, H))


def grow(solid):
    """4-connected dilation of a boolean mask."""
    g = solid.copy()
    g[1:] |= solid[:-1]
    g[:-1] |= solid[1:]
    g[:, 1:] |= solid[:, :-1]
    g[:, :-1] |= solid[:, 1:]
    return g


def outlined(img, color=INK):
    """A 1px 4-connected outline around everything opaque in an RGBA image (which needs a 1px margin)."""
    a = np.array(img)
    solid = a[..., 3] > 0
    a[grow(solid) & ~solid] = tuple(color) + (255,)
    return Image.fromarray(a)


class Canvas:
    """A small RGBA canvas for props and sprites: draw with palette names or RGB, then `done()`."""

    def __init__(self, w, h):
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.d.fontmode = "1"

    @staticmethod
    def c(col):
        return (C[col] if isinstance(col, str) else tuple(col)) + (255,)

    def rect(self, box, col):
        self.d.rectangle(box, fill=self.c(col))

    def ell(self, box, col):
        self.d.ellipse(box, fill=self.c(col))

    def poly(self, pts, col):
        self.d.polygon(pts, fill=self.c(col))

    def line(self, pts, col, w=1):
        self.d.line(pts, fill=self.c(col), width=w)

    def px(self, xy, col):
        self.d.point(xy, fill=self.c(col))

    def pxs(self, pts, col):
        for p in pts:
            self.d.point(p, fill=self.c(col))

    def text(self, xy, s, col, fnt=SILK, anchor="la"):
        self.d.text(xy, s, font=fnt, fill=self.c(col), anchor=anchor)

    def done(self, outline=INK):
        return outlined(self.img, outline) if outline else self.img


def paste(dst, src, x, y, anchor="lt"):
    """Paste an RGBA sprite by an anchor: l/m/r then t/m/b, like 'mb' for bottom centre."""
    w, h = src.size
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    y -= {"t": 0, "m": h // 2, "b": h}[anchor[1]]
    dst.paste(src, (int(round(x)), int(round(y))), src)
    return int(round(x)), int(round(y))


def scaled(img, n):
    if n == 1:
        return img
    return img.resize((max(1, int(round(img.width * n))), max(1, int(round(img.height * n)))), Image.NEAREST)


def mirror(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def paste_scaled(dst, img, x, y, s=1.0, anchor="mm"):
    if s <= 0.04:
        return
    paste(dst, scaled(img, s), x, y, anchor)


def paste_rot(dst, img, x, y, angle, anchor="mm"):
    """Paste rotated by `angle` degrees (counter-clockwise), keeping it pixel-crisp."""
    if angle:
        img = img.rotate(angle, resample=Image.NEAREST, expand=True)
    paste(dst, img, x, y, anchor)


def fade_to(img, color, amount):
    """Dither the whole image toward `color` (0 = untouched, 1 = solid)."""
    if amount <= 0:
        return
    if amount >= 1:
        img.paste(Image.new(img.mode, img.size, tuple(color) + ((255,) if img.mode == "RGBA" else ())))
        return
    dither(img, amount, color)
