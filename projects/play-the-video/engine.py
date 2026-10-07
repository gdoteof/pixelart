"""Canvas, palette and fonts for Play the Video, bound onto the shared drawing code with pixelart.kit.

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

INK = (20, 18, 28)
C = {
    "ink": INK,
    # the stream's overlay: dark panels, and one accent colour per streamer (purple for Hasan, green for Asmongold)
    "bg": (16, 16, 24), "bar": (26, 26, 38), "panel": (30, 30, 44), "panel_hi": (54, 56, 80),
    "line": (70, 74, 104), "text": (240, 242, 248), "dim": (150, 154, 180), "mute": (96, 100, 126),
    "hasan": (150, 96, 255), "hasan_hi": (198, 164, 255), "hasan_sh": (92, 52, 176),
    "asmon": (96, 226, 48), "asmon_hi": (176, 252, 128), "asmon_sh": (44, 136, 28),
    "chat": (255, 196, 64), "live": (236, 52, 56), "ok": (70, 200, 110), "warn": (250, 180, 50),
    # Hasan: olive skin, black hair cropped at the sides, heavy brows, stubble, the tank top and the chain
    "hskin": (226, 172, 130), "hskin_sh": (192, 134, 98), "hskin_dk": (146, 94, 70), "hskin_hi": (246, 204, 164),
    "hhair": (40, 32, 36), "hhair_sh": (24, 20, 26), "hhair_hi": (80, 66, 70),
    "hstub": (160, 114, 92), "hstub_dk": (118, 82, 68), "hfade": (96, 74, 68),
    "tank": (236, 234, 228), "tank_sh": (196, 194, 190), "tank_hi": (252, 250, 246),
    "mao": (104, 116, 100), "mao_sh": (72, 84, 72), "mao_hi": (140, 152, 132),
    # Asmongold: pale, the long thin brown hair, the beard, the headphones, a black T-shirt
    "askin": (238, 212, 194), "askin_sh": (206, 170, 152), "askin_dk": (160, 120, 108), "askin_hi": (252, 236, 222),
    "ahair": (116, 80, 54), "ahair_sh": (82, 54, 40), "ahair_dk": (56, 38, 30), "ahair_hi": (158, 116, 80),
    "abeard": (100, 66, 46), "abeard_sh": (68, 44, 34),
    "tee": (34, 34, 42), "tee_sh": (22, 22, 30), "tee_hi": (66, 68, 84),
    "phones": (30, 30, 38), "phones_hi": (96, 98, 116),
    # faces
    "eye": (30, 22, 30), "eye_w": (252, 250, 246), "iris_h": (104, 66, 40), "iris_a": (96, 128, 150),
    "mouth": (104, 28, 38), "lip_h": (184, 112, 96), "lip_a": (196, 138, 128), "tongue": (214, 92, 100),
    "tooth": (252, 250, 242), "tooth_y": (232, 214, 150), "flush": (240, 110, 100), "sweat": (150, 210, 255),
    "tear": (150, 210, 255),
    # Hasan's room: white walls, framed prints, the neon, the katanas, the shelves with their warm strip lights
    "hwall": (228, 226, 220), "hwall_sh": (198, 196, 194), "hwall_hi": (244, 243, 238),
    "neon": (72, 150, 255), "neon_hi": (196, 226, 255), "frame": (40, 36, 42), "frame_g": (190, 150, 84),
    "bed": (234, 230, 222), "bed_sh": (198, 194, 190), "bed_st": (140, 152, 188),
    "wood": (104, 70, 48), "wood_sh": (70, 46, 34), "wood_hi": (148, 104, 70),
    "shelf": (40, 36, 44), "shelf_hi": (68, 62, 72), "ledw": (255, 190, 110), "ledw_hi": (255, 232, 190),
    "parka": (150, 134, 108), "parka_sh": (110, 96, 78), "mitt": (126, 96, 74), "card": (196, 168, 124),
    "hdesk": (44, 42, 52), "hdesk_hi": (74, 72, 88), "hdesk_sh": (30, 28, 38),
    # Asmongold's room: dim and brown under a low dark ceiling, and nobody has taken the rubbish out
    "awall": (104, 76, 58), "awall_sh": (72, 52, 44), "awall_hi": (134, 98, 70), "aceil": (38, 30, 34),
    "aceil_hi": (58, 46, 48), "stain": (78, 56, 44), "grime": (60, 46, 40), "blood": (110, 34, 34),
    "blood_sh": (78, 24, 28), "bag": (36, 38, 48), "bag_hi": (76, 80, 98), "can": (124, 26, 44),
    "can_hi": (196, 66, 86), "roach": (124, 68, 34), "roach_sh": (76, 40, 24), "rat": (126, 120, 118),
    "rat_sh": (88, 82, 84), "rat_pink": (224, 156, 156), "blind": (156, 144, 122), "blind_sh": (116, 104, 90),
    "box": (176, 136, 88), "box_sh": (130, 96, 62), "mold": (104, 138, 74), "mold_sh": (70, 100, 56),
    "adesk": (54, 42, 40), "adesk_hi": (86, 68, 60), "adesk_sh": (36, 28, 30),
    # everything else
    "white": (248, 246, 240), "black": (18, 16, 22), "grey": (128, 130, 144), "grey_sh": (84, 86, 100),
    "grey_hi": (190, 192, 204),
    "paper": (250, 248, 240), "paper_sh": (214, 210, 198), "paper_ln": (190, 204, 226),
    "gold": (246, 200, 70), "gold_sh": (190, 136, 40), "gold_hi": (255, 242, 172),
    "red": (208, 48, 56), "red_sh": (142, 30, 44), "red_hi": (242, 98, 98),
    "blue": (60, 110, 200), "blue_sh": (36, 70, 150), "blue_hi": (120, 170, 240),
    "green": (60, 170, 90), "green_sh": (36, 110, 60), "green_hi": (130, 220, 140),
    "orange": (255, 138, 40), "orange_sh": (196, 92, 30), "pink": (255, 120, 170), "purple": (150, 100, 220),
    "purple_sh": (96, 60, 160), "yellow": (252, 214, 60), "brown": (130, 84, 52), "brown_sh": (96, 60, 38),
    "brown_hi": (174, 124, 80), "steel": (182, 188, 202), "steel_sh": (114, 120, 138), "steel_hi": (224, 228, 238),
    "sky": (120, 170, 230), "sky_hi": (176, 210, 246), "grass": (96, 170, 84), "grass_sh": (62, 126, 62),
    "night": (24, 28, 60), "night_hi": (52, 60, 110), "stone": (152, 152, 164), "stone_sh": (106, 106, 122),
    "cream": (244, 232, 204), "dog": (214, 168, 108), "dog_sh": (160, 112, 70), "dog_dk": (62, 46, 40),
}

KIT = kit.Kit(C, INK)
col, rgba, silk, press, outline_text = KIT.col, KIT.rgba, KIT.silk, KIT.press, KIT.outline_text
Canvas, picture, vgrad, blend = KIT.Canvas, KIT.picture, KIT.vgrad, KIT.blend
