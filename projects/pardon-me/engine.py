"""Canvas, palette and fonts for Pardon Me (Trump vs. Bibi), bound onto pixelart.pixel and pixelart.sprites.

Everything is drawn at 320x180 and shown 6x (nearest-neighbour) at 1080p.
"""
from pathlib import Path

from PIL import Image, ImageDraw  # noqa: F401

from pixelart import pixel, sprites
from pixelart.anim import (arc_pt, back_out, clamp, ease_in, ease_in_out, ease_out, lerp, pop_dy,  # noqa: F401
                           ramp, rnd, wobble)
from pixelart.pixel import dither, dither_poly, dither_rect, mix, text_width  # noqa: F401
from pixelart.sprites import (fade_to, grow, mirror, paste, paste_rot, paste_scaled, scaled, tint)  # noqa: F401

W, H = 320, 180
SCALE = 6
ROOT = Path(__file__).parent

INK = (26, 22, 34)
C = {
    "ink": INK,
    # Trump: the tan, the pale goggle rings, the hair, the navy suit and the long red tie
    "tskin": (236, 146, 78), "tskin_sh": (196, 104, 56), "tskin_hi": (250, 182, 118), "tring": (250, 222, 176),
    "thair": (250, 216, 104), "thair_sh": (210, 160, 60), "thair_hi": (255, 244, 186),
    # Bibi: paler skin, the grey hair, dark brows, the navy suit and the blue tie
    "bskin": (236, 190, 160), "bskin_sh": (200, 146, 120), "bskin_hi": (250, 216, 192),
    "bhair": (214, 214, 222), "bhair_sh": (150, 150, 166), "bhair_hi": (244, 244, 250), "bbrow": (80, 76, 86),
    # the suits
    "suit": (40, 50, 92), "suit_sh": (26, 30, 60), "suit_hi": (70, 84, 136),
    "bsuit": (52, 56, 72), "bsuit_sh": (34, 36, 50), "bsuit_hi": (84, 90, 112),
    "shirt": (246, 246, 250), "shirt_sh": (204, 208, 222),
    "tie": (214, 38, 48), "tie_sh": (150, 22, 36), "tie_hi": (250, 96, 96),
    "btie": (84, 140, 220), "btie_sh": (50, 90, 170), "btie_hi": (150, 196, 246),
    "shoe": (24, 20, 28), "shoe_hi": (70, 66, 80),
    # faces
    "eye": (24, 18, 30), "mouth": (122, 34, 44), "tongue": (210, 90, 100), "tooth": (250, 248, 240),
    "flush": (236, 96, 90), "sweat": (150, 200, 255),
    # the General Assembly hall
    "wall": (206, 156, 70), "wall_sh": (168, 118, 50), "wall_hi": (234, 196, 116), "wall_dk": (132, 88, 40),
    "marble": (54, 112, 86), "marble_sh": (36, 80, 62), "marble_hi": (102, 160, 124), "marble_vein": (150, 196, 164),
    "carpet": (40, 70, 118), "carpet_sh": (28, 50, 90), "carpet_hi": (62, 98, 150),
    "desk": (196, 152, 98), "desk_sh": (150, 108, 66), "desk_hi": (228, 190, 132),
    "chair": (52, 104, 140), "chair_sh": (34, 72, 104),
    "un": (92, 156, 224), "un_sh": (56, 110, 184), "un_hi": (170, 210, 250),
    "screen": (14, 18, 30), "screen_bg": (30, 52, 96), "screen_hi": (60, 92, 150),
    "steel": (180, 186, 200), "steel_sh": (112, 118, 136), "black": (16, 14, 20),
    # paper and marker, for the flip chart and the posters
    "paper": (250, 250, 244), "paper_sh": (214, 214, 204), "paper_ln": (196, 214, 236),
    "mk_black": (30, 30, 40), "mk_red": (222, 38, 44), "mk_blue": (40, 86, 206), "mk_green": (36, 150, 72),
    # shared bits
    "white": (246, 244, 238), "gold": (246, 200, 70), "gold_sh": (186, 132, 40), "gold_hi": (255, 240, 170),
    "red": (206, 50, 56), "red_sh": (140, 30, 44), "red_hi": (240, 96, 96),
    "blue": (60, 110, 200), "green": (60, 170, 90), "orange": (255, 138, 40),
    "text": (244, 242, 248), "dim": (150, 146, 170),
}

PRESS = pixel.font(size=8)
PRESS16 = pixel.font(size=16)
PRESS24 = pixel.font(size=24)
SILK = pixel.font("Silkscreen-Regular.ttf", 8)
SILK16 = pixel.font("Silkscreen-Regular.ttf", 16)


def col(c):
    return C[c] if isinstance(c, str) else tuple(c)


def text(img, xy, s, fnt=PRESS, fill=C["text"], shadow=(0, 0, 0), anchor="la"):
    pixel.text(img, xy, s, fnt, col(fill), shadow, anchor)


def outline_text(img, xy, s, fnt=PRESS, fill=C["text"], outline=INK, anchor="la"):
    pixel.outline_text(img, xy, s, fnt, col(fill), outline, anchor)


def mask(draw_fn, size=(W, H)):
    """Coverage mask over the whole canvas (or `size`); see pixelart.pixel.mask."""
    return pixel.mask(draw_fn, size)


def outlined(img, color=INK):
    return sprites.outlined(img, color)


def rim_light(spr, side, color=(255, 230, 170), amount=0.5):
    return sprites.rim_light(spr, side, color, INK, amount)


class Canvas(sprites.Canvas):
    """A sprite canvas drawing with this video's palette names; `done()` outlines in ink."""

    def __init__(self, w, h):
        super().__init__(w, h, C, SILK)

    def done(self, outline=INK):
        return super().done(outline)


def new_world(color=(0, 0, 0)):
    return Image.new("RGB", (W, H), col(color))


def vgrad(img, box, top, bottom, steps=None, phase=0, soft=0.3):
    return pixel.vgrad(img, box, col(top), col(bottom), steps, phase, soft)


def blend(img, m, color, alpha=0.3):
    return pixel.blend(img, m, col(color), alpha)


def blend_poly(img, pts, color, alpha=0.3):
    return pixel.blend_poly(img, pts, col(color), alpha)
