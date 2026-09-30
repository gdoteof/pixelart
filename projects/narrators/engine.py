"""Canvas, palette and fonts for Attenborough vs. Freeman, bound onto pixelart.pixel and pixelart.sprites.

Everything is drawn at 320x180 and shown 6x (nearest-neighbour) at 1080p.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw  # noqa: F401

from pixelart import pixel, sprites
from pixelart.anim import (arc_pt, back_out, clamp, ease_in, ease_in_out, ease_out, lerp, pop_dy,  # noqa: F401
                           ramp, rnd, wobble)
from pixelart.pixel import dither, dither_poly, dither_rect, mix, text_width  # noqa: F401
from pixelart.sprites import (fade_to, grow, mirror, paste, paste_rot, paste_scaled, scaled, tint)  # noqa: F401

W, H = 320, 180
SCALE = 6
ROOT = Path(__file__).parent

INK = (28, 22, 30)
C = {
    "ink": INK,
    # Sir David: pale skin, white swept hair, the blue field shirt and khakis
    "skin": (246, 210, 184), "skin_sh": (220, 170, 146), "skin_hi": (255, 230, 212), "flush": (234, 142, 128),
    "hair": (240, 240, 244), "hair_sh": (192, 196, 212),
    "shirt": (150, 192, 232), "shirt_sh": (104, 146, 198), "shirt_hi": (196, 224, 248),
    "khaki": (198, 178, 130), "khaki_sh": (152, 134, 94),
    "shoe": (98, 66, 50), "shoe_hi": (140, 100, 72),
    # Morgan: brown skin, white crop and beard, freckles, the narrator's charcoal suit
    "mskin": (136, 88, 62), "mskin_sh": (100, 62, 46), "mskin_hi": (170, 118, 86),
    "mhair": (230, 228, 224), "mhair_sh": (172, 170, 172), "freckle": (82, 50, 38),
    "suit": (60, 62, 76), "suit_sh": (40, 40, 52), "suit_hi": (90, 94, 112),
    "tie": (150, 40, 52), "tie_hi": (196, 70, 76),
    "wsuit": (246, 244, 238), "wsuit_sh": (206, 204, 212), "wsuit_hi": (255, 255, 255),
    "denim": (86, 114, 152), "denim_sh": (60, 82, 118), "denim_hi": (122, 150, 184),
    "chauf": (84, 88, 96), "chauf_sh": (58, 60, 68), "chauf_hi": (120, 124, 132),
    "navy": (40, 52, 96), "navy_sh": (26, 34, 66), "navy_hi": (66, 80, 132),
    # shared bits
    "white": (246, 244, 238), "white_sh": (204, 202, 210),
    "gold": (246, 200, 70), "gold_sh": (186, 132, 40), "gold_hi": (255, 240, 170),
    "mouth": (120, 36, 46), "tongue": (204, 88, 98), "eye": (26, 20, 34), "tooth": (250, 248, 240),
    "mic": (60, 60, 70), "mic_hi": (150, 150, 164), "steel": (196, 204, 220), "steel_sh": (120, 128, 150),
    "sweat": (150, 200, 255), "red": (206, 50, 56), "red_sh": (140, 30, 44), "red_hi": (240, 96, 96),
    "paper": (242, 232, 204), "paper_sh": (200, 184, 156), "wood": (150, 98, 64), "wood_sh": (98, 62, 56),
    "wood_hi": (204, 146, 96), "black": (18, 16, 22), "glass": (170, 214, 232), "glass_sh": (110, 160, 190),
    # nature
    "leaf": (58, 128, 72), "leaf_sh": (34, 86, 58), "leaf_hi": (104, 170, 88), "leaf_dk": (22, 54, 44),
    "moss": (120, 150, 64), "grass": (206, 176, 86), "grass_sh": (160, 128, 58), "grass_hi": (238, 214, 128),
    "soil": (112, 78, 56), "soil_sh": (78, 54, 44), "rock": (128, 122, 130), "rock_sh": (88, 84, 96),
    "rock_hi": (170, 164, 170), "sky": (140, 198, 236), "sky_hi": (200, 230, 248), "cloud": (250, 250, 252),
    "cloud_sh": (212, 220, 236), "snow": (240, 246, 252), "snow_sh": (190, 210, 232), "ice": (172, 216, 240),
    "ice_sh": (120, 170, 214), "sea": (40, 90, 150), "sea_sh": (26, 60, 110), "sea_hi": (90, 150, 200),
    "fur": (58, 54, 60), "fur_sh": (36, 34, 40), "fur_hi": (92, 88, 96), "silver": (178, 180, 190),
    "fluff": (168, 160, 150), "fluff_sh": (122, 114, 108), "fluff_hi": (212, 206, 196),
    "mane": (166, 102, 44), "mane_sh": (118, 66, 34), "lion": (214, 164, 88), "lion_sh": (170, 122, 62),
    # screen furniture
    "text": (244, 242, 248), "dim": (150, 146, 170), "tele": (255, 232, 40), "rec": (236, 40, 40),
    "band": (12, 10, 16), "doc": (250, 250, 250), "docbar": (230, 196, 60),
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


def mask(draw_fn):
    """Coverage mask over the whole canvas; see pixelart.pixel.mask."""
    return pixel.mask(draw_fn, (W, H))


def outlined(img, color=INK):
    return sprites.outlined(img, color)


def rim_light(spr, side, color=(255, 214, 160), amount=0.5):
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
    """A vertical gradient from `top` to `bottom` inside box, the pixel-art way: flat bands, with a
    dithered seam over the last `soft` fraction of each band."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    top, bottom = np.array(col(top), np.float32), np.array(col(bottom), np.float32)
    a = np.asarray(img).copy()
    ys = np.arange(h)[:, None]
    p = ys / max(1, h - 1)
    if steps:
        q = p * steps
        lo = np.floor(q)
        frac = q - lo
        thr = pixel.bayer(h, x1 - x0, phase)
        p = (lo + (frac > (1 - soft) + soft * thr)) / steps
    p = np.broadcast_to(p, (h, x1 - x0))[..., None]
    a[y0:y1, x0:x1] = (top * (1 - p) + bottom * p).round().astype(np.uint8)
    img.paste(Image.fromarray(a))


def blend(img, m, color, alpha=0.3):
    """Mix `color` into an RGB image by mask `m` (an (h, w) array in [0, 1], or a scalar) times alpha.
    A flat tint rather than a dither: for light, glass and haze that the camera zooms in on."""
    a = np.asarray(img, dtype=np.float32).copy()
    w = np.clip(np.asarray(m, np.float32) * alpha, 0, 1)
    w = w[..., None] if w.ndim == 2 else w
    a[..., :3] = a[..., :3] * (1 - w) + np.array(col(color), np.float32) * w
    img.paste(Image.fromarray(a.round().astype(np.uint8)))


def blend_poly(img, pts, color, alpha=0.3):
    blend(img, mask(lambda d: d.polygon(pts, fill=255)), color, alpha)
