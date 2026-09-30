"""Sprite helpers shared by the videos: a palette canvas, ink outlines, anchored and scaled pasting.

A video binds its own palette and ink colour:

    PAL = {"skin": (244, 204, 174), ...}
    s = Canvas(24, 12, PAL)            # draw with palette names or RGB tuples
    s.rect((2, 2, 21, 9), "skin")
    img = s.done(INK)                  # 1px 4-connected ink outline around the drawing

Sprites are RGBA images at native resolution; paste them with an anchor
("mb" = bottom centre), scale them by whole numbers, mirror or rotate them
without resampling blur.
"""
import numpy as np
from PIL import Image, ImageDraw

from pixelart.pixel import dither


def grow(solid):
    """4-connected dilation of a boolean mask."""
    g = solid.copy()
    g[1:] |= solid[:-1]
    g[:-1] |= solid[1:]
    g[:, 1:] |= solid[:, :-1]
    g[:, :-1] |= solid[:, 1:]
    return g


def outlined(img, color):
    """A 1px 4-connected outline around everything opaque in an RGBA image (which needs a 1px margin)."""
    a = np.array(img)
    solid = a[..., 3] > 0
    a[grow(solid) & ~solid] = tuple(color) + (255,)
    return Image.fromarray(a)


class Canvas:
    """A small RGBA canvas for props and sprites: draw with palette names or RGB, then `done()`."""

    def __init__(self, w, h, pal, font=None):
        self.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.d.fontmode = "1"
        self.pal, self.font = pal, font

    def c(self, col):
        return (self.pal[col] if isinstance(col, str) else tuple(col)) + (255,)

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

    def text(self, xy, s, col, fnt=None, anchor="la"):
        self.d.text(xy, s, font=fnt or self.font, fill=self.c(col), anchor=anchor)

    def done(self, outline=None):
        return outlined(self.img, outline) if outline else self.img


def paste(dst, src, x, y, anchor="lt"):
    """Paste an RGBA sprite by an anchor: l/m/r then t/m/b, like 'mb' for bottom centre. Returns its top-left."""
    w, h = src.size
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    y -= {"t": 0, "m": h // 2, "b": h}[anchor[1]]
    dst.paste(src, (int(round(x)), int(round(y))), src)
    return int(round(x)), int(round(y))


def scaled(img, n):
    """Nearest-neighbour scale by `n` (whole numbers keep pixels square)."""
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


def tint(img, color, amount=1.0):
    """A copy of an RGBA sprite pushed toward `color` (for silhouettes, statues, ghosts)."""
    a = np.array(img).astype(np.float32)
    a[..., :3] = a[..., :3] * (1 - amount) + np.array(color, np.float32) * amount
    return Image.fromarray(a.round().astype(np.uint8))


def fade_to(img, color, amount):
    """Dither the whole image toward `color` (0 = untouched, 1 = solid)."""
    if amount <= 0:
        return
    if amount >= 1:
        img.paste(Image.new(img.mode, img.size, tuple(color) + ((255,) if img.mode == "RGBA" else ())))
        return
    dither(img, amount, color)


def rim_light(spr, side, color, ink, amount=0.5):
    """Light on the pixels just inside the outline on one side (+1 right, -1 left); `ink` is the outline colour."""
    a = np.array(spr).astype(np.float32)
    solid = a[..., 3] > 0
    body = solid & ~np.all(a[..., :3] == ink, axis=-1)
    outside = np.zeros_like(solid)
    if side > 0:
        outside[:, :-2] = ~solid[:, 2:]
    else:
        outside[:, 2:] = ~solid[:, :-2]
    sel = body & outside
    a[sel, :3] = a[sel, :3] * (1 - amount) + np.array(color, np.float32) * amount
    return Image.fromarray(a.round().astype(np.uint8))
