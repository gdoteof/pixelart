"""Pixel-art drawing primitives, independent of any one video's canvas or palette.

The working model: draw everything at a small native resolution (e.g. 320x180)
into RGB/RGBA PIL images, fake transparency with ordered dithering, and only
upscale with nearest-neighbour at the very end so every pixel stays square.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).parent / "fonts"
OUT_SIZE = (1920, 1080)

BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


@lru_cache(maxsize=64)
def bayer(h, w, phase=0):
    """Ordered-dither threshold map of shape (h, w), shifted diagonally by `phase`."""
    thr = np.tile(BAYER4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    return np.roll(thr, phase, axis=(0, 1)) if phase else thr


def mix(a, b, t):
    return tuple(int(round(p + (q - p) * t)) for p, q in zip(a, b))


def font(name="PressStart2P-Regular.ttf", size=8):
    """A TrueType font from pixelart/fonts (or any path). Pixel fonts want their native size or a multiple."""
    path = Path(name)
    return ImageFont.truetype(str(path if path.is_absolute() else FONTS / name), size)


def sprite(rows, pal):
    """RGBA sprite from strings: each character is a key into `pal`, anything else is transparent."""
    width = max(len(r) for r in rows)
    img = Image.new("RGBA", (width, len(rows)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c in pal:
                px[x, y] = pal[c] + (255,)
    return img


def text(img, xy, s, fnt, fill, shadow=(0, 0, 0), anchor="la"):
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    x, y = xy
    if shadow is not None:
        d.text((x + 1, y + 1), s, font=fnt, fill=shadow, anchor=anchor)
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)


def outline_text(img, xy, s, fnt, fill, outline=(0, 0, 0), anchor="la"):
    """Aliased text with a 1px outline all round (8-connected)."""
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    x, y = xy
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                d.text((x + dx, y + dy), s, font=fnt, fill=outline, anchor=anchor)
    d.text((x, y), s, font=fnt, fill=fill, anchor=anchor)


def text_width(s, fnt):
    return int(fnt.getlength(s))


def wrap(words, width, fnt):
    """Break words into rows no wider than `width` in font `fnt`: each row is a list of indices into `words`."""
    rows, row, x = [], [], 0
    space = text_width(" ", fnt)
    for i, w in enumerate(words):
        ww = text_width(w, fnt)
        if row and x + space + ww > width:
            rows.append(row)
            row, x = [], 0
        x += (space if row else 0) + ww
        row.append(i)
    return rows + [row] if row else rows


def mask(draw_fn, size):
    """Coverage mask in [0, 1] of shape (h, w), built by drawing with 255 on a blank L image."""
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    draw_fn(d)
    return np.asarray(m, dtype=np.float32) / 255.0


def dither(img, density, color, blend=1.0, phase=0):
    """Ordered-dither `color` into `img` in place, the pixel-art way to fake alpha.

    `density` is a scalar or an (h, w) array in [0, 1]; `blend` < 1 tints the
    chosen pixels toward `color` instead of replacing them.
    """
    arr = np.array(img, dtype=np.float32)
    sel = bayer(arr.shape[0], arr.shape[1], phase) < density
    c = np.array(color, np.float32)
    if arr.shape[2] == 4:
        c = np.append(c, 255.0)
    arr[sel] = arr[sel] * (1.0 - blend) + c * blend
    img.paste(Image.fromarray(arr.round().astype(np.uint8)))


def dither_rect(img, box, color, density=0.5, blend=1.0, phase=0):
    x0, y0, x1, y1 = box
    m = np.zeros((img.height, img.width), np.float32)
    m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = density
    dither(img, m, color, blend, phase)


def dither_poly(img, pts, color, density=0.35, blend=0.5, phase=0):
    dither(img, mask(lambda d: d.polygon(pts, fill=255), img.size) * density, color, blend, phase)


def upscale(img, out=OUT_SIZE):
    return img.convert("RGB").resize(out, Image.NEAREST)


def compose(world, ui, cx=None, cy=None, k=None, shake=(0, 0), out=OUT_SIZE):
    """Final frame: the world seen through a camera, the UI layer on top at a fixed scale.

    The UI is the same size as the world and is shown at out/world scale (6x for
    320x180 -> 1080p). `k` is screen pixels per world pixel (an integer, so
    every world pixel stays square; defaults to the UI scale); `cx, cy` is the
    world point at the centre of the view, clamped so the view stays inside.
    """
    W, H = world.size
    scale = out[0] // W
    cx = W / 2 if cx is None else cx
    cy = H / 2 if cy is None else cy
    k = scale if k is None else k
    ow, oh = W * scale, H * scale
    vw, vh = ow / k, oh / k
    x0 = min(max(cx - vw / 2, 0), W - vw)
    y0 = min(max(cy - vh / 2, 0), H - vh)
    sx, sy = int(round(x0 * k)) + shake[0], int(round(y0 * k)) + shake[1]
    wx, wy = sx // k, sy // k
    wx1, wy1 = min(W, (sx + ow) // k + 1), min(H, (sy + oh) // k + 1)
    part = world.crop((wx, wy, wx1, wy1)).resize(((wx1 - wx) * k, (wy1 - wy) * k), Image.NEAREST)
    frame = part.crop((sx - wx * k, sy - wy * k, sx - wx * k + ow, sy - wy * k + oh))
    if ui is not None:
        big = ui.resize((ow, oh), Image.NEAREST)
        frame.paste(big, (0, 0), big)
    return frame


def vgrad(img, box, top, bottom, steps=None, phase=0, soft=0.3):
    """A vertical gradient from `top` to `bottom` inside box, the pixel-art way: flat bands, with a
    dithered seam over the last `soft` fraction of each band (or a smooth ramp when `steps` is None)."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    top, bottom = np.array(top, np.float32), np.array(bottom, np.float32)
    a = np.asarray(img).copy()
    ys = np.arange(h)[:, None]
    p = ys / max(1, h - 1)
    if steps:
        q = p * steps
        lo = np.floor(q)
        frac = q - lo
        thr = bayer(h, x1 - x0, phase)
        p = (lo + (frac > (1 - soft) + soft * thr)) / steps
    p = np.broadcast_to(p, (h, x1 - x0))[..., None]
    a[y0:y1, x0:x1, :3] = (top * (1 - p) + bottom * p).round().astype(np.uint8)
    img.paste(Image.fromarray(a))


def blend(img, m, color, alpha=0.3):
    """Mix `color` into an image by mask `m` (an (h, w) array in [0, 1], or a scalar) times alpha.
    A flat tint rather than a dither: for light, glass and haze that the camera zooms in on."""
    a = np.asarray(img, dtype=np.float32).copy()
    w = np.clip(np.asarray(m, np.float32) * alpha, 0, 1)
    w = w[..., None] if w.ndim == 2 else w
    a[..., :3] = a[..., :3] * (1 - w) + np.array(color, np.float32)[:3] * w
    img.paste(Image.fromarray(a.round().astype(np.uint8)))


def blend_poly(img, pts, color, alpha=0.3):
    blend(img, mask(lambda d: d.polygon(pts, fill=255), img.size), color, alpha)
