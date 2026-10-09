"""Canvas, palette and fonts for Out of Your League, bound onto the shared drawing code with pixelart.kit.

Everything is drawn at 320x180 and shown 6x (nearest-neighbour) at 1080p.
"""
from pathlib import Path

from PIL import Image, ImageDraw  # noqa: F401

from pixelart import kit
from pixelart.anim import (arc_pt, back_out, clamp, ease_in, ease_in_out, ease_out, k_in, lerp, pop_dy,  # noqa: F401
                           ramp, rnd, wobble)
from pixelart.kit import PRESS, PRESS16, SILK, SILK16, silk_w  # noqa: F401
from pixelart.pixel import dither, dither_rect, mix, text_width  # noqa: F401
from pixelart.sprites import (fade_to, fly, mirror, paste, paste_rot, paste_scaled, pop_in, scaled,  # noqa: F401
                              tint)

W, H = 320, 180
ROOT = Path(__file__).parent

INK = (24, 18, 30)
C = {
    "ink": INK,
    # the streams' overlay: dark panels, and one accent colour each (pink for Emiru, leaf green for Maya)
    "bg": (18, 16, 26), "bar": (30, 26, 42), "panel": (36, 32, 50), "panel_hi": (62, 58, 86),
    "line": (80, 76, 110), "text": (244, 242, 250), "dim": (160, 156, 186), "mute": (104, 100, 132),
    "emiru": (255, 110, 170), "emiru_hi": (255, 184, 214), "emiru_sh": (176, 58, 112),
    "maya": (116, 200, 92), "maya_hi": (188, 238, 156), "maya_sh": (58, 128, 56),
    "chat": (255, 196, 64), "live": (236, 52, 56), "ok": (70, 200, 110), "warn": (250, 180, 50),
    # Emiru: fair, long hair of a brown so dark it is nearly black, a blunt fringe, a full face of makeup, the
    # pink cat-ear headset, a pink crop top and a choker
    "eskin": (252, 224, 208), "eskin_sh": (232, 190, 174), "eskin_dk": (196, 146, 136), "eskin_hi": (255, 242, 232),
    "ehair": (46, 33, 32), "ehair_sh": (28, 20, 22), "ehair_hi": (104, 76, 68), "ebrow": (118, 88, 80),
    "eshadow": (236, 150, 176),
    "ears": (255, 150, 192), "ears_sh": (212, 94, 146), "ears_hi": (255, 212, 230),
    "knit": (255, 176, 204), "knit_sh": (224, 128, 166), "knit_hi": (255, 222, 234),
    "lip_e": (236, 118, 138), "lip_e_hi": (250, 168, 178), "iris_e": (134, 84, 60), "iris_e_dk": (74, 42, 38),
    "iris_e_hi": (190, 132, 88), "eblush": (252, 180, 180),
    # Maya: tanned, long wavy brown hair parted in the middle and lighter at the ends, the sanctuary's green tee
    "mskin": (236, 190, 152), "mskin_sh": (208, 154, 120), "mskin_dk": (164, 112, 88), "mskin_hi": (250, 216, 184),
    "mhair": (116, 76, 52), "mhair_sh": (80, 50, 38), "mhair_dk": (54, 34, 30), "mhair_hi": (168, 118, 76),
    "mhair_lt": (204, 156, 100), "mbrow": (74, 46, 36),
    "olive": (96, 134, 80), "olive_sh": (66, 98, 60), "olive_hi": (140, 174, 112),
    "glove": (180, 130, 78), "glove_sh": (130, 90, 54), "glove_hi": (214, 170, 112),
    "lip_m": (214, 112, 110), "lip_m_hi": (236, 156, 146), "iris_m": (120, 76, 46), "iris_m_dk": (66, 40, 30),
    "iris_m_hi": (176, 122, 70), "mblush": (240, 160, 134),
    # faces
    "eye": (34, 24, 34), "eye_w": (252, 250, 246), "mouth": (110, 30, 44), "tongue": (222, 98, 108),
    "tooth": (252, 250, 242), "flush": (244, 120, 120), "sweat": (150, 210, 255), "tear": (150, 210, 255),
    # Emiru's room: lilac walls under pink strip lights, white shelves of wigs, the sewing corner
    "ewall": (206, 188, 232), "ewall_sh": (172, 150, 208), "ewall_hi": (230, 218, 246), "eled": (255, 132, 196),
    "eshelf": (246, 242, 250), "eshelf_sh": (202, 194, 220), "foam": (240, 234, 230), "foam_sh": (204, 194, 196),
    "chair": (255, 164, 200), "chair_sh": (214, 110, 158), "chair_hi": (255, 214, 230),
    "edesk": (240, 236, 246), "edesk_hi": (254, 252, 255), "edesk_sh": (198, 190, 214),
    "form": (226, 206, 172), "form_sh": (186, 162, 130), "teal": (70, 200, 190), "teal_sh": (40, 140, 140),
    "lilac": (188, 150, 240),
    # Maya's set and the sanctuary: barn boards, the pasture, and who lives there
    "barn": (156, 102, 66), "barn_sh": (114, 72, 50), "barn_hi": (190, 134, 88), "beam": (80, 52, 40),
    "pasture": (126, 186, 88), "pasture_sh": (88, 146, 70), "pasture_hi": (170, 216, 116), "hills": (98, 152, 116),
    "tree": (62, 118, 72), "tree_sh": (42, 86, 60), "dirt": (184, 150, 104), "dirt_sh": (144, 112, 78),
    "angus": (164, 74, 46), "angus_sh": (120, 50, 36), "angus_hi": (200, 108, 70), "muzzle": (226, 170, 150),
    "hawk": (128, 88, 58), "hawk_sh": (88, 58, 44), "hawk_bib": (236, 218, 180), "hawk_tail": (196, 98, 56),
    "emu": (116, 100, 90), "emu_sh": (80, 70, 66), "emu_neck": (112, 136, 170), "beak": (70, 64, 66),
    "shell": (174, 144, 86), "shell_sh": (124, 98, 62), "shell_hi": (210, 184, 120), "tort": (150, 140, 100),
    "wolf": (154, 154, 162), "wolf_sh": (106, 106, 120), "wolf_hi": (212, 212, 218),
    "scorp": (44, 48, 66), "scorp_hi": (88, 98, 132), "chin": (172, 174, 188), "chin_sh": (126, 128, 146),
    "snake": (200, 174, 100), "snake_sh": (124, 98, 60), "hay": (232, 200, 104), "hay_sh": (188, 150, 70),
    "mdesk": (126, 84, 56), "mdesk_hi": (166, 116, 78), "mdesk_sh": (90, 60, 44),
    "shopwall": (240, 218, 178), "shopwall_sh": (212, 186, 146),
    # other people's brands, as the pictures need them
    "twitch": (145, 70, 255), "twitch_sh": (92, 44, 176), "twitch_hi": (196, 160, 255),
    "parcel": (200, 154, 100), "parcel_sh": (156, 114, 72), "tape": (232, 214, 170),
    "rift": (16, 26, 44), "rift_hi": (34, 54, 84), "lol_gold": (204, 172, 108), "lol_teal": (20, 196, 184),
    "can_blue": (44, 72, 152), "can_silver": (204, 210, 224),
    # everything else
    "white": (248, 246, 240), "black": (20, 18, 24), "grey": (128, 130, 144), "grey_sh": (84, 86, 100),
    "grey_hi": (190, 192, 204),
    "paper": (250, 248, 240), "paper_sh": (214, 210, 198), "paper_ln": (190, 204, 226),
    "gold": (246, 200, 70), "gold_sh": (190, 136, 40), "gold_hi": (255, 242, 172),
    "red": (208, 48, 56), "red_sh": (142, 30, 44), "red_hi": (242, 98, 98),
    "blue": (60, 110, 200), "blue_sh": (36, 70, 150), "blue_hi": (120, 170, 240),
    "green": (60, 170, 90), "green_sh": (36, 110, 60), "green_hi": (130, 220, 140),
    "orange": (255, 138, 40), "orange_sh": (196, 92, 30), "pink": (255, 120, 170), "purple": (150, 100, 220),
    "purple_sh": (96, 60, 160), "yellow": (252, 214, 60), "brown": (130, 84, 52), "brown_sh": (96, 60, 38),
    "brown_hi": (174, 124, 80), "steel": (182, 188, 202), "steel_sh": (114, 120, 138), "steel_hi": (224, 228, 238),
    "sky": (120, 178, 234), "sky_hi": (190, 220, 246), "sky_lo": (238, 230, 204), "grass": (96, 170, 84),
    "grass_sh": (62, 126, 62), "night": (24, 28, 60), "night_hi": (52, 60, 110), "stone": (152, 152, 164),
    "stone_sh": (106, 106, 122), "cream": (244, 232, 204), "wood": (120, 80, 54), "wood_sh": (84, 54, 40),
    "wood_hi": (164, 116, 76), "sea": (40, 100, 160), "sea_hi": (90, 160, 210), "sea_sh": (24, 62, 112),
}

KIT = kit.Kit(C, INK)
col, rgba, silk, press, outline_text = KIT.col, KIT.rgba, KIT.silk, KIT.press, KIT.outline_text
Canvas, picture, vgrad, blend = KIT.Canvas, KIT.picture, KIT.vgrad, KIT.blend
