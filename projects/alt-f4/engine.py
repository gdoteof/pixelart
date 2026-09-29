"""Canvas, palette and drawing primitives for the ALT-F4 music video.

Everything is drawn at native resolution (320x180) and upscaled with
nearest-neighbour so every pixel stays crisp at 1080p. The primitives live in
pixelart.pixel; this module binds them to this video's canvas and palette.
"""
from pathlib import Path

from pixelart import pixel
from pixelart.pixel import dither, dither_poly, dither_rect, font, mix, text, text_width  # noqa: F401

W, H = 320, 180
SCALE = 6
ROOT = Path(__file__).parent

PAL = {
    "k": (22, 14, 30),       # outline
    "s": (242, 194, 155),    # skin
    "S": (214, 154, 120),    # skin shadow
    "w": (255, 255, 255),
    "e": (32, 24, 58),       # pupil
    "m": (122, 35, 48),      # mouth
    "t": (250, 246, 236),    # teeth
    "h": (86, 56, 40),       # sam hair
    "H": (122, 84, 58),      # sam hair highlight
    "d": (30, 22, 24),       # dario hair
    "D": (70, 54, 56),       # dario hair highlight
    "g": (20, 20, 26),       # glasses frame
    "G": (190, 228, 255),    # lens glint
    "n": (58, 60, 70),       # sam sweater
    "N": (38, 40, 48),       # sweater shadow
    "b": (150, 190, 236),    # dario shirt
    "B": (108, 146, 200),    # shirt shadow
    "j": (64, 94, 154),      # jeans
    "J": (44, 68, 116),
    "p": (54, 52, 64),       # dark trousers
    "P": (36, 34, 44),
    "o": (236, 236, 236),    # sneaker
    "O": (170, 170, 180),
    "r": (60, 60, 66),       # mic body
    "R": (140, 140, 150),    # mic grill
}

OPENAI_GREEN = (16, 163, 127)
CLAUDE_ORANGE = (217, 119, 87)
CREAM = (240, 238, 230)
GOLD = (255, 214, 64)
NEON_PINK = (255, 64, 160)
NEON_CYAN = (64, 240, 255)


def sprite(rows, pal=PAL):
    return pixel.sprite(rows, pal)


def outline_text(img, xy, s, fnt, fill, outline=PAL["k"], anchor="la"):
    pixel.outline_text(img, xy, s, fnt, fill, outline, anchor)


def mask(draw_fn):
    """Coverage mask over the whole canvas; see pixelart.pixel.mask."""
    return pixel.mask(draw_fn, (W, H))


def upscale(img):
    return pixel.upscale(img, (W * SCALE, H * SCALE))


def compose(world, ui, cx=W / 2, cy=H / 2, k=SCALE, shake=(0, 0)):
    return pixel.compose(world, ui, cx, cy, k, shake, out=(W * SCALE, H * SCALE))
