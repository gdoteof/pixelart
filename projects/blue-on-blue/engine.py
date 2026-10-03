"""Canvas, palette and fonts for Blue on Blue, bound onto pixelart.pixel and pixelart.sprites.

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

INK = (24, 20, 32)
C = {
    "ink": INK,
    # Newsom: the tan, the slicked-back helmet of hair going grey at the temples, the navy blazer
    "nskin": (236, 180, 140), "nskin_sh": (202, 140, 106), "nskin_dk": (160, 100, 76), "nskin_hi": (250, 210, 178),
    "nhair": (70, 52, 44), "nhair_sh": (46, 34, 30), "nhair_hi": (130, 108, 96), "nhair_gl": (196, 182, 170),
    "ngrey": (156, 150, 152), "ngrey_hi": (204, 200, 202),
    "blazer": (34, 48, 96), "blazer_sh": (22, 30, 64), "blazer_hi": (66, 84, 140),
    # Mamdani: the cropped hair and the trimmed beard, the big grin, the charcoal suit and the blue tie
    "mskin": (182, 124, 88), "mskin_sh": (148, 96, 66), "mskin_dk": (112, 70, 48), "mskin_hi": (208, 154, 114),
    "mhair": (38, 30, 32), "mhair_sh": (24, 18, 22), "mhair_hi": (78, 66, 68), "mbeard": (52, 42, 44),
    "msuit": (60, 62, 76), "msuit_sh": (40, 42, 54), "msuit_hi": (94, 98, 116),
    "mshirt": (214, 228, 248), "mtie": (60, 110, 210), "mtie_sh": (36, 72, 160), "mtie_hi": (130, 176, 250),
    # Trump, on the phone: the tan, the pale goggle rings, the hair, the navy suit and the long red tie
    "tskin": (240, 140, 66), "tskin_sh": (200, 98, 48), "tskin_dk": (160, 70, 40), "tskin_hi": (252, 178, 108),
    "tring": (250, 214, 168), "tring_sh": (232, 190, 140),
    "thair": (252, 220, 110), "thair_sh": (214, 164, 62), "thair_dk": (170, 120, 44), "thair_hi": (255, 246, 190),
    "suit": (40, 50, 96), "suit_sh": (26, 30, 62), "suit_hi": (72, 86, 140),
    "tie": (216, 36, 46), "tie_sh": (150, 20, 34), "tie_hi": (252, 96, 96),
    "shirt": (248, 248, 250), "shirt_sh": (206, 210, 224),
    # faces
    "eye": (30, 22, 30), "eye_w": (250, 248, 244), "eye_b": (70, 120, 190), "mouth": (110, 30, 40),
    "nlip": (200, 120, 100), "mlip": (130, 74, 62), "tlip": (204, 98, 72), "tlip_hi": (236, 140, 104),
    "tongue": (214, 92, 100), "tooth": (252, 250, 242),
    "flush": (240, 92, 86), "sick": (150, 196, 110), "sweat": (150, 200, 255), "tear": (150, 210, 255),
    # the studio: a navy wall of acoustic panels, wood slats at the sides, the neon sign, the desk
    "wall": (30, 38, 70), "wall_sh": (20, 26, 50), "wall_dk": (14, 18, 36), "wall_hi": (46, 58, 100),
    "foam": (38, 48, 88), "foam_sh": (26, 34, 64), "foam_hi": (54, 68, 116),
    "slat": (140, 94, 58), "slat_sh": (104, 68, 40), "slat_dk": (72, 46, 28), "slat_hi": (176, 126, 80),
    "neon": (226, 244, 255), "neon_glow": (90, 160, 255), "neon_dim": (58, 74, 110), "neon_red": (255, 120, 120),
    "onair": (236, 52, 56), "onair_hi": (255, 150, 140), "onair_off": (86, 34, 40),
    "ring": (252, 252, 255), "ring_glow": (200, 220, 255), "stand": (40, 40, 48), "stand_hi": (88, 88, 100),
    "desk": (112, 76, 52), "desk_sh": (80, 52, 36), "desk_dk": (54, 34, 24), "desk_hi": (150, 106, 72),
    "desk_top": (128, 88, 60), "desk_edge": (170, 124, 86),
    "micbody": (34, 34, 40), "micbody_hi": (84, 86, 98), "grille": (110, 112, 124), "boom": (44, 44, 52),
    "phones": (30, 30, 36), "phones_hi": (80, 80, 92),
    "plant": (60, 132, 76), "plant_sh": (38, 94, 56), "plant_hi": (110, 180, 110), "pot": (214, 204, 186),
    "pot_sh": (170, 158, 140),
    "book1": (170, 60, 60), "book2": (60, 110, 170), "book3": (210, 180, 90), "book4": (70, 140, 100),
    "book5": (220, 220, 210), "shelf": (96, 64, 42),
    "bear": (130, 84, 52), "bear_sh": (96, 60, 38), "flag": (248, 246, 236), "flag_red": (200, 46, 52),
    "laptop": (190, 194, 204), "laptop_sh": (140, 144, 156), "screen": (40, 60, 110), "screen_hi": (120, 170, 240),
    "mug": (240, 238, 232), "mug_sh": (200, 196, 190), "coffee": (90, 56, 36),
    "phone": (26, 26, 34), "phone_hi": (80, 80, 96), "phone_scr": (40, 46, 70),
    # chat, posts, phones and paper
    "chat_bg": (14, 16, 30), "chat_name": (255, 196, 90), "chat_name2": (120, 220, 255), "chat_name3": (170, 255, 140),
    "chat_name4": (255, 140, 200), "chat_text": (236, 238, 248),
    "imsg": (52, 132, 246), "imsg_grey": (226, 228, 234), "truth": (90, 70, 210), "truth_hi": (150, 130, 250),
    "tiktok": (20, 20, 24), "tt_pink": (254, 44, 85), "tt_cyan": (37, 244, 238),
    "paper": (250, 250, 244), "paper_sh": (214, 214, 204), "paper_ln": (196, 214, 236),
    "folder": (30, 28, 40), "folder_hi": (70, 66, 86),
    "mk_black": (30, 30, 40), "mk_red": (222, 38, 44), "mk_blue": (40, 86, 206), "mk_green": (36, 150, 72),
    "money": (120, 190, 110), "money_sh": (70, 140, 80),
    "ice": (200, 236, 255), "ice_sh": (140, 196, 236), "ice_hi": (246, 252, 255),
    "bus": (40, 110, 210), "bus_sh": (26, 70, 150), "bus_win": (180, 220, 250),
    "sky": (120, 170, 230), "sky_hi": (176, 210, 246), "grass": (90, 160, 80), "road": (90, 90, 100),
    "night": (24, 28, 60), "city": (40, 46, 80), "city_win": (255, 220, 120),
    "duck": (252, 214, 60), "duck_sh": (210, 160, 30), "beak": (250, 140, 40),
    "box": (196, 156, 104), "box_sh": (156, 116, 74),
    "wine": (130, 24, 48), "wine_hi": (200, 70, 96), "glass": (220, 236, 246),
    "mel_hair": (196, 150, 96), "mel_skin": (240, 200, 170), "gold_chair": (234, 196, 92),
    # shared bits
    "white": (248, 246, 240), "gold": (246, 200, 70), "gold_sh": (190, 136, 40), "gold_dk": (140, 96, 30),
    "gold_hi": (255, 242, 172),
    "red": (208, 48, 56), "red_sh": (142, 30, 44), "red_hi": (242, 98, 98),
    "blue": (60, 110, 200), "blue_sh": (36, 70, 150), "blue_hi": (120, 170, 240), "green": (60, 170, 90),
    "orange": (255, 138, 40), "pink": (255, 120, 170),
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


def silk(img, xy, s, fill="mk_black", anchor="la"):
    """Silkscreen glyphs sit 4 px down their box: this puts the glyph tops at y."""
    x, y = xy
    ImageDraw.Draw(img).text((x, y - 4), s, font=SILK, fill=col(fill), anchor=anchor)


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
