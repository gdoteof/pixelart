"""Canvas, palette and fonts for Trump vs. Netanyahu Round 2, bound onto pixelart.pixel and pixelart.sprites.

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

INK = (30, 22, 30)
C = {
    "ink": INK,
    # Trump: the tan, the pale goggle rings, the hair, the navy suit and the long red tie
    "tskin": (240, 140, 66), "tskin_sh": (200, 98, 48), "tskin_dk": (160, 70, 40), "tskin_hi": (252, 178, 108),
    "tring": (250, 214, 168), "tring_sh": (232, 190, 140),
    "thair": (252, 220, 110), "thair_sh": (214, 164, 62), "thair_dk": (170, 120, 44), "thair_hi": (255, 246, 190),
    # Bibi: paler skin, the silver hair, the dark heavy brows
    "bskin": (238, 192, 164), "bskin_sh": (206, 150, 124), "bskin_dk": (170, 116, 98), "bskin_hi": (250, 218, 196),
    "bhair": (220, 222, 230), "bhair_sh": (160, 162, 178), "bhair_dk": (118, 120, 138), "bhair_hi": (248, 248, 252),
    "bbrow": (70, 64, 70),
    # Obama: the skin, the short grey hair, the tan suit
    "oskin": (150, 98, 66), "oskin_sh": (116, 72, 48), "oskin_dk": (88, 52, 36), "oskin_hi": (182, 128, 92),
    "ohair": (150, 146, 150), "ohair_sh": (108, 104, 110), "ohair_hi": (204, 202, 206),
    "tan": (204, 180, 132), "tan_sh": (164, 140, 98), "tan_hi": (228, 210, 168),
    # the announcer's tux
    "tux": (28, 26, 36), "tux_sh": (16, 14, 22), "tux_hi": (66, 62, 84),
    "askin": (236, 186, 150), "askin_sh": (200, 144, 112), "ahair": (60, 50, 50),
    # the suits
    "suit": (40, 50, 96), "suit_sh": (26, 30, 62), "suit_hi": (72, 86, 140),
    "bsuit": (48, 52, 66), "bsuit_sh": (32, 34, 46), "bsuit_hi": (82, 88, 108),
    "shirt": (248, 248, 250), "shirt_sh": (206, 210, 224),
    "tie": (216, 36, 46), "tie_sh": (150, 20, 34), "tie_hi": (252, 96, 96),
    "btie": (88, 146, 224), "btie_sh": (52, 94, 176), "btie_hi": (156, 200, 248),
    "otie": (60, 70, 96), "otie_sh": (40, 46, 66),
    "shoe": (26, 20, 26), "shoe_hi": (76, 68, 80),
    # faces
    "eye": (30, 22, 30), "eye_w": (250, 248, 244), "mouth": (110, 30, 40),
    "tlip": (204, 98, 72), "tlip_hi": (236, 140, 104), "blip": (196, 118, 106), "olip": (120, 64, 52),
    "tongue": (214, 92, 100), "tooth": (252, 250, 242),
    "flush": (240, 92, 86), "sick": (150, 196, 110), "sweat": (150, 200, 255),
    # the Oval Office
    "wall": (238, 226, 196), "wall_sh": (214, 198, 160), "wall_dk": (184, 164, 122), "wall_hi": (250, 244, 224),
    "trim": (250, 248, 238), "trim_sh": (218, 212, 194),
    "marble": (244, 242, 236), "marble_sh": (206, 202, 194), "marble_vein": (186, 182, 176),
    "firebox": (34, 26, 28), "brick": (110, 50, 40), "brick_sh": (80, 34, 30),
    "fire": (255, 200, 70), "fire_hi": (255, 244, 180), "fire_red": (236, 96, 40),
    "rug": (236, 222, 180), "rug_sh": (210, 190, 140), "rug_dk": (180, 156, 100),
    "floor": (150, 108, 70), "floor_sh": (120, 84, 52),
    "chair": (234, 196, 92), "chair_sh": (196, 152, 60), "chair_dk": (156, 112, 40), "chair_hi": (252, 228, 150),
    "wood": (120, 74, 44), "wood_sh": (86, 50, 30), "wood_hi": (160, 108, 66),
    "canvas": (60, 52, 44),
    # Washington, in the portrait over the fireplace
    "gw_coat": (40, 36, 40), "gw_skin": (236, 206, 182), "gw_hair": (232, 232, 236), "gw_sky": (120, 124, 116),
    # the press pool: silhouettes against the room
    "press": (52, 44, 54), "press_sh": (36, 30, 38), "press_hi": (96, 86, 98), "lens": (90, 110, 140),
    "flash": (255, 255, 250),
    # paper and marker, for the poster boards and the folders
    "paper": (250, 250, 244), "paper_sh": (214, 214, 204), "paper_ln": (196, 214, 236),
    "folder": (30, 28, 40), "folder_sh": (20, 18, 28), "folder_hi": (70, 66, 86),
    "mk_black": (30, 30, 40), "mk_red": (222, 38, 44), "mk_blue": (40, 86, 206), "mk_green": (36, 150, 72),
    # shared bits
    "white": (248, 246, 240), "gold": (246, 200, 70), "gold_sh": (190, 136, 40), "gold_dk": (140, 96, 30),
    "gold_hi": (255, 242, 172),
    "red": (208, 48, 56), "red_sh": (142, 30, 44), "red_hi": (242, 98, 98),
    "blue": (60, 110, 200), "blue_sh": (36, 70, 150), "green": (60, 170, 90), "orange": (255, 138, 40),
    "steel": (182, 188, 202), "steel_sh": (114, 120, 138), "black": (18, 16, 22),
    "text": (246, 244, 248), "dim": (150, 146, 170),
}

PRESS = pixel.font(size=8)
PRESS16 = pixel.font(size=16)
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
