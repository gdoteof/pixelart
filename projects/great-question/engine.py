"""Canvas, palette and fonts for Great Question, bound onto pixelart.pixel and pixelart.sprites.

Everything is drawn at 320x180 and shown 6x (nearest-neighbour) at 1080p.
"""
from pathlib import Path

from PIL import Image, ImageDraw  # noqa: F401

from pixelart import pixel, sprites
from pixelart.anim import (arc_pt, back_out, clamp, ease_in, ease_in_out, ease_out, lerp, pop_dy,  # noqa: F401
                           ramp, rnd, wobble)
from pixelart.pixel import dither, dither_rect, mix, text_width  # noqa: F401
from pixelart.sprites import (fade_to, fly, mirror, paste, paste_rot, paste_scaled, pop_in, scaled,  # noqa: F401
                              tint)

W, H = 320, 180
ROOT = Path(__file__).parent

INK = (20, 18, 28)
C = {
    "ink": INK,
    # the call app: a dark window, tiles, and one accent colour per speaker
    "bg": (20, 22, 32), "bar": (30, 33, 48), "panel": (34, 38, 56), "panel_hi": (58, 64, 92),
    "line": (74, 80, 110), "text": (240, 242, 248), "dim": (146, 152, 178), "mute": (96, 100, 126),
    "felix": (228, 60, 64), "felix_hi": (255, 128, 116), "felix_sh": (150, 30, 44),
    "sam": (40, 184, 150), "sam_hi": (136, 238, 208), "sam_sh": (20, 110, 96),
    "gpt": (250, 250, 252), "gpt_glow": (116, 220, 190), "gpt_sh": (56, 150, 128), "gpt_dk": (24, 84, 76),
    "ajax": (206, 150, 70), "ajax_hi": (250, 214, 130), "ajax_sh": (140, 90, 40),
    "live": (236, 52, 56), "ok": (70, 200, 110), "warn": (250, 180, 50),
    # Felix: the swept-back blond hair, the beard, the headphones, the black hoodie
    "fskin": (246, 208, 178), "fskin_sh": (214, 166, 136), "fskin_dk": (170, 118, 94), "fskin_hi": (255, 232, 210),
    "fhair": (226, 186, 108), "fhair_sh": (176, 132, 66), "fhair_dk": (130, 92, 46), "fhair_hi": (252, 228, 164),
    "fbeard": (172, 126, 76), "fbeard_sh": (126, 88, 52),
    "hood": (40, 40, 52), "hood_sh": (24, 24, 34), "hood_hi": (76, 78, 98),
    "phones": (30, 30, 38), "phones_hi": (96, 98, 116),
    # Sam: the tousled brown hair, the wide eyes, the grey crewneck
    "sskin": (248, 220, 200), "sskin_sh": (222, 182, 162), "sskin_dk": (178, 132, 118), "sskin_hi": (255, 240, 226),
    "shair": (78, 58, 46), "shair_sh": (50, 36, 32), "shair_hi": (124, 96, 78),
    "sweater": (130, 136, 150), "sweater_sh": (94, 100, 116), "sweater_hi": (172, 178, 192), "tee": (244, 244, 246),
    "polo1": (240, 120, 150), "polo1_sh": (196, 80, 112), "polo2": (150, 214, 90), "polo2_sh": (104, 164, 60),
    # faces
    "eye": (30, 22, 30), "eye_w": (252, 250, 246), "eye_b": (70, 130, 204), "eye_g": (96, 122, 150),
    "mouth": (110, 30, 40), "flip": (206, 130, 110), "slip": (214, 148, 134), "tongue": (214, 92, 100),
    "tooth": (252, 250, 242), "flush": (240, 110, 100), "sweat": (150, 210, 255), "tear": (150, 210, 255),
    # Felix's room, at night: a paper screen, wood, the server rack's LEDs, the chair
    "room": (62, 48, 68), "room_sh": (42, 32, 50), "room_hi": (88, 68, 92),
    "shoji": (238, 224, 190), "shoji_sh": (200, 180, 142), "wood": (122, 82, 54), "wood_sh": (84, 54, 38),
    "wood_hi": (164, 116, 76),
    "led_r": (255, 70, 90), "led_c": (70, 230, 255), "led_p": (190, 110, 255), "led_g": (110, 240, 130),
    "rack": (30, 32, 44), "rack_hi": (62, 66, 86),
    "chair": (62, 64, 86), "chair_hi": (96, 100, 128), "chair_sh": (44, 46, 64), "chair_red": (214, 48, 56),
    "mesh": (44, 46, 58), "mesh_sh": (30, 32, 42),
    "fdesk": (58, 44, 52), "fdesk_hi": (90, 70, 78),
    # Sam's office, by day: off-white, a window on the city, a plant, a whiteboard
    "wall": (198, 206, 216), "wall_sh": (172, 182, 196), "wall_hi": (222, 228, 236),
    "window": (168, 206, 238), "window_hi": (216, 234, 250), "city": (128, 148, 178), "city_sh": (100, 118, 150),
    "sdesk": (240, 238, 234), "sdesk_sh": (198, 196, 192),
    "plant": (60, 132, 76), "plant_sh": (38, 94, 56), "plant_hi": (110, 180, 110), "pot": (214, 204, 186),
    "pot_sh": (170, 158, 140), "board": (250, 250, 252), "laptop": (190, 194, 204), "laptop_sh": (140, 144, 156),
    # the things on ChatGPT's screen
    "white": (248, 246, 240), "black": (18, 16, 22), "grey": (128, 130, 144), "grey_sh": (84, 86, 100),
    "grey_hi": (190, 192, 204),
    "paper": (250, 248, 240), "paper_sh": (214, 210, 198), "paper_ln": (190, 204, 226),
    "gold": (246, 200, 70), "gold_sh": (190, 136, 40), "gold_hi": (255, 242, 172),
    "red": (208, 48, 56), "red_sh": (142, 30, 44), "red_hi": (242, 98, 98),
    "blue": (60, 110, 200), "blue_sh": (36, 70, 150), "blue_hi": (120, 170, 240),
    "green": (60, 170, 90), "green_sh": (36, 110, 60), "green_hi": (130, 220, 140),
    "orange": (255, 138, 40), "pink": (255, 120, 170), "purple": (150, 100, 220), "purple_sh": (96, 60, 160),
    "yellow": (252, 214, 60), "brown": (130, 84, 52), "brown_sh": (96, 60, 38), "brown_hi": (174, 124, 80),
    "steel": (182, 188, 202), "steel_sh": (114, 120, 138), "steel_hi": (224, 228, 238),
    "sky": (120, 170, 230), "sky_hi": (176, 210, 246), "grass": (96, 170, 84), "grass_sh": (62, 126, 62),
    "night": (24, 28, 60), "night_hi": (52, 60, 110), "stone": (152, 152, 164), "stone_sh": (106, 106, 122),
    "cream": (244, 232, 204), "baby": (250, 214, 190), "baby_sh": (226, 176, 150),
    "pan": (64, 150, 70), "pan_sh": (40, 104, 50), "sea": (60, 120, 190), "sea_hi": (120, 180, 230),
}

PRESS = pixel.font(size=8)
PRESS16 = pixel.font(size=16)
SILK = pixel.font("Silkscreen-Regular.ttf", 8)
SILK16 = pixel.font("Silkscreen-Regular.ttf", 16)


def col(c):
    return C[c] if isinstance(c, str) else tuple(c)[:3]


def rgba(c, a=255):
    return col(c) + (a,)


def silk(img, xy, s, fill="text", anchor="la", fnt=SILK):
    """Silkscreen text with its glyph tops at y (the glyphs sit 4 px down their box, 8 px at double size)."""
    x, y = xy
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.text((x, y - fnt.size // 2), s, font=fnt, fill=rgba(fill) if img.mode == "RGBA" else col(fill), anchor=anchor)


def press(img, xy, s, fill="text", anchor="la", fnt=PRESS, shadow=None):
    """Press Start text; `shadow` is a colour for a 1 px drop shadow."""
    pixel.text(img, xy, s, fnt, col(fill), col(shadow) if shadow else None, anchor)


def outline_text(img, xy, s, fnt=PRESS, fill="text", outline=INK, anchor="la"):
    pixel.outline_text(img, xy, s, fnt, col(fill), col(outline), anchor)


def silk_w(s, fnt=SILK):
    return pixel.text_width(s, fnt)


class Canvas(sprites.Canvas):
    """A sprite canvas drawing with this video's palette names; `done()` outlines in ink."""

    def __init__(self, w, h):
        super().__init__(w, h, C, SILK)

    def silk(self, xy, s, col_="ink", anchor="la", fnt=SILK):
        silk(self.img, xy, s, col_, anchor, fnt)

    def done(self, outline=INK):
        return super().done(outline)


def picture(w, h, bg="bg"):
    """A flat RGB picture and its ImageDraw, for tiles and for what ChatGPT's screen shows."""
    img = Image.new("RGB", (w, h), col(bg))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    return img, d


def vgrad(img, box, top, bottom, steps=None, phase=0, soft=0.3):
    return pixel.vgrad(img, box, col(top), col(bottom), steps, phase, soft)


def blend(img, m, color, alpha=0.3):
    return pixel.blend(img, m, col(color), alpha)
