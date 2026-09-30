"""Text and comic effects for gags, independent of any one video's palette: arcade title text,
labels, speech bubbles, ink stamps, strike-throughs, arrows and impact bursts.

Every function takes its fonts and colours as arguments; a project binds its own
defaults once (see projects/narrators/props.py) rather than copying these.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from pixelart.anim import back_out
from pixelart.pixel import font, mix, text_width
from pixelart.sprites import grow, paste

BLACK, WHITE, GOLD, ORANGE, RED = (0, 0, 0), (255, 255, 255), (255, 214, 64), (255, 138, 40), (206, 50, 56)
PRESS = font(size=8)
PRESS16 = font(size=16)


def _shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = a[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    return out


def _rgba(c):
    return tuple(c)[:3] + (255,)


@lru_cache(maxsize=512)
def big_text_img(s, fnt=PRESS16, top=GOLD, bottom=ORANGE, outline=BLACK, shadow=2, thick=2, ink=BLACK):
    """Arcade title text as a sprite: two-tone fill, thick outline, hard drop shadow. Returns (img, pad)."""
    tw, th = text_width(s, fnt), fnt.size
    pad = thick + shadow + 1
    m = Image.new("L", (tw + 2 * pad, th + 2 * pad), 0)
    ImageDraw.Draw(m).text((pad, pad), s, font=fnt, fill=255)
    a = np.array(m) > 0
    ring = a.copy()
    for _ in range(thick):
        ring = grow(ring)
    sh = _shift(ring, shadow, shadow)
    out = np.zeros(a.shape + (4,), np.uint8)
    out[sh & ~ring] = _rgba(ink)
    out[ring] = _rgba(outline)
    rows = np.arange(a.shape[0])[:, None]
    top_m = a & (rows < pad + th * 0.55)
    out[top_m] = _rgba(top)
    out[a & ~top_m] = _rgba(bottom)
    out[a & ~_shift(a, 0, 1)] = _rgba(mix(top, WHITE, 0.6))
    return Image.fromarray(out, "RGBA"), pad


def big_text(img, xy, s, fnt=PRESS16, top=GOLD, bottom=ORANGE, outline=BLACK, anchor="la", scale=1.0, ink=BLACK):
    """Draw arcade text anchored like PIL ('la', 'ma', 'mm'...); returns its width."""
    im, pad = big_text_img(s, fnt, tuple(top), tuple(bottom), tuple(outline), ink=tuple(ink))
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.NEAREST)
        pad = int(pad * scale)
    x, y = xy
    tw = im.width - 2 * pad
    if anchor[0] == "m":
        x -= tw // 2
    elif anchor[0] == "r":
        x -= tw
    if anchor[1] == "m":
        y -= (im.height - 2 * pad) // 2
    elif anchor[1] == "b":
        y -= im.height - 2 * pad
    img.paste(im, (int(x - pad), int(y - pad)), im)
    return tw


def pop_text(img, x, y, s, age, fnt=PRESS16, top=GOLD, bottom=ORANGE, outline=BLACK, anchor="ma", dur=0.16,
             ink=BLACK):
    """big_text that pops in (scales up past full size and settles); nothing before age 0."""
    if age < 0:
        return
    k = back_out(age / dur)
    big_text(img, (x, y), s, fnt, top, bottom, outline, anchor=anchor, scale=max(0.2, k) if k < 0.999 else 1.0,
             ink=ink)


def label(img, xy, s, fnt=PRESS, bg=WHITE, fg=BLACK, pad=2, anchor="la", border=BLACK, th=None, text_dy=0):
    """Text on a flat plate with a 1px border; returns the plate's box. `th` is the text's height
    (the font size by default) and `text_dy` nudges fonts whose glyphs sit low in their box."""
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    tw = text_width(s, fnt)
    th = fnt.size if th is None else th
    x, y = xy
    w, h = tw + 2 * pad + 1, th + 2 * pad
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    y -= {"t": 0, "a": 0, "m": h // 2, "b": h}[anchor[1]]
    box = (int(x), int(y), int(x + w), int(y + h))
    d.rectangle((box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1), fill=_rgba(border))
    d.rectangle(box, fill=_rgba(bg))
    d.text((box[0] + pad + 1, box[1] + pad + text_dy), s, font=fnt, fill=_rgba(fg))
    return box


def bubble(img, x, y, lines, tail=None, fnt=PRESS, fill=WHITE, ink=BLACK, pad=4, anchor="mb", line_h=10,
           text_dy=0):
    """A comic speech bubble; (x, y) anchors the box and the tail's tip points at `tail`."""
    if isinstance(lines, str):
        lines = [lines]
    fill, ink = _rgba(fill), _rgba(ink)
    tw = max(text_width(s, fnt) for s in lines)
    w, h = tw + 2 * pad + 2, len(lines) * line_h + 2 * pad - 2
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    y -= {"t": 0, "m": h // 2, "b": h}[anchor[1]]
    x, y = int(x), int(y)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    if tail:
        tx, ty = tail
        bx = min(max(tx, x + 6), x + w - 7)
        by = y + h if ty > y + h else y
        d.polygon([(bx - 4, by), (bx + 4, by), (tx, ty)], fill=ink)
        d.polygon([(bx - 3, by), (bx + 3, by), (tx + (1 if tx < bx else -1 if tx > bx else 0),
                                                ty + (-2 if ty > by else 2))], fill=fill)
    d.rounded_rectangle((x - 1, y - 1, x + w, y + h), radius=4, fill=ink)
    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=3, fill=fill)
    if tail:
        d.polygon([(bx - 3, by - (1 if ty > by else -1)), (bx + 3, by - (1 if ty > by else -1)),
                   (bx, by + (2 if ty > by else -2))], fill=fill)
    for i, s in enumerate(lines):
        d.text((x + (w - text_width(s, fnt)) // 2 + 1, y + pad + i * line_h + text_dy), s, font=fnt, fill=ink)
    return (x, y, x + w, y + h)


@lru_cache(maxsize=256)
def stamp_img(s, fnt=PRESS16, color=RED, angle=-12, holes=0.12):
    """A rubber stamp's impression: a ruled box round the text, with speckled gaps in the ink."""
    tw, th = text_width(s, fnt), fnt.size
    pad = 3 if th <= 8 else 4
    w, h = tw + 2 * pad + 4, th + 2 * pad + 3
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w - 1, h - 1), outline=_rgba(color), width=2 if th > 8 else 1)
    d.text((pad + 2, pad + 2), s, font=fnt, fill=_rgba(color))
    arr = np.array(im)
    gone = np.random.default_rng(len(s) * 7 + th).random(arr.shape[:2]) < holes
    arr[gone, 3] = 0
    return Image.fromarray(arr, "RGBA").rotate(angle, resample=Image.NEAREST, expand=True)


def stamp(img, cx, cy, s, fnt=PRESS16, color=RED, angle=-12, age=1.0):
    """An ink stamp that slams down (drops in over ~0.1 s); nothing before age 0."""
    if age < 0:
        return
    im = stamp_img(s, fnt, tuple(color), angle)
    dy = int(round(max(0.0, 1 - age / 0.1) * -14))
    paste(img, im, cx, cy + dy, "mm")


def strike(img, x0, y, x1, p=1.0, color=RED, width=2, ink=BLACK):
    """A hand-drawn strike-through, drawn left to right as p goes 0 -> 1."""
    if p <= 0:
        return
    d = ImageDraw.Draw(img)
    xe = x0 + (x1 - x0) * min(1.0, p)
    d.line([(x0, y + 1), (xe, y - 1)], fill=_rgba(ink), width=width + 2)
    d.line([(x0, y + 1), (xe, y - 1)], fill=_rgba(color), width=width)


def arrow(img, x0, y0, x1, y1, color=GOLD, width=2, head=5, ink=BLACK):
    d = ImageDraw.Draw(img)
    a = math.atan2(y1 - y0, x1 - x0)
    tip = [(x1, y1), (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5)),
           (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))]
    d.line([(x0, y0), (x1, y1)], fill=_rgba(ink), width=width + 2)
    d.polygon([(x + (x - x1) * 0.25, y + (y - y1) * 0.25) for x, y in tip], fill=_rgba(ink))
    d.line([(x0, y0), (x1 - 2 * math.cos(a), y1 - 2 * math.sin(a))], fill=_rgba(color), width=width)
    d.polygon(tip, fill=_rgba(color))


def typed(s, age, cps=20.0):
    """The part of `s` typed so far."""
    return s[:max(0, int(age * cps))]


def burst(img, x, y, r0, r1, color=GOLD, spikes=10, rot=0.0, ink=BLACK):
    """A spiky impact star."""
    pts = []
    for i in range(spikes * 2):
        a = rot + i * math.pi / spikes
        r = r1 if i % 2 == 0 else r0
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    ImageDraw.Draw(img).polygon(pts, fill=_rgba(color), outline=_rgba(ink))


def sparkle(img, x, y, size=2, color=WHITE):
    d = ImageDraw.Draw(img)
    d.line([(x - size, y), (x + size, y)], fill=_rgba(color))
    d.line([(x, y - size), (x, y + size)], fill=_rgba(color))
