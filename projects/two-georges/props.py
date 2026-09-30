"""Props and text effects for the gags: period objects, projectiles, splashes, banners.

Sprites are cached RGBA images drawn on a Canvas and outlined in ink. Functions
that take an `img` draw straight onto a world or UI layer.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import (C, INK, PRESS, PRESS16, PRESS24, SILK, Canvas, back_out, clamp, grow, mix, paste,
                    rnd, text_width)
from pixelart import pixel

GOLD, WHITE, RED = C["gold"], C["white"], C["flag_red"]
ORANGE = (255, 138, 40)


# --- text -------------------------------------------------------------------------------

def _shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = a[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    return out


@lru_cache(maxsize=512)
def big_text_img(s, fnt=PRESS16, top=GOLD, bottom=ORANGE, outline=INK, shadow=2, thick=2):
    """Arcade title text as a sprite: two-tone fill, thick outline, hard drop shadow."""
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
    out[sh & ~ring] = INK + (255,)
    out[ring] = tuple(outline) + (255,)
    rows = np.arange(a.shape[0])[:, None]
    top_m = a & (rows < pad + th * 0.55)
    out[top_m] = tuple(top) + (255,)
    out[a & ~top_m] = tuple(bottom) + (255,)
    out[a & ~_shift(a, 0, 1)] = tuple(mix(top, WHITE, 0.6)) + (255,)
    return Image.fromarray(out, "RGBA"), pad


def big_text(img, xy, s, fnt=PRESS16, top=GOLD, bottom=ORANGE, outline=INK, anchor="la", scale=1.0):
    """Draw arcade text anchored like PIL ('la', 'ma', 'mm'...); returns its width."""
    im, pad = big_text_img(s, fnt, top, bottom, outline)
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


def pop_text(img, x, y, s, age, fnt=PRESS16, top=GOLD, bottom=ORANGE, anchor="ma", dur=0.16):
    """big_text that pops in (scales up past full size and settles); nothing before age 0."""
    if age < 0:
        return
    s_ = back_out(age / dur)
    big_text(img, (x, y), s, fnt, top, bottom, anchor=anchor, scale=max(0.2, s_) if s_ < 0.999 else 1.0)


def label(img, xy, s, bg=WHITE, fg=INK, fnt=SILK, pad=2, anchor="la", border=INK):
    """Text on a flat plate with a 1px border."""
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    tw = text_width(s, fnt)
    th = 6 if fnt is SILK else fnt.size
    x, y = xy
    w, h = tw + 2 * pad + 1, th + 2 * pad
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    y -= {"t": 0, "a": 0, "m": h // 2, "b": h}[anchor[1]]
    box = (int(x), int(y), int(x + w), int(y + h))
    d.rectangle((box[0] - 1, box[1] - 1, box[2] + 1, box[3] + 1), fill=border)
    d.rectangle(box, fill=bg)
    d.text((box[0] + pad + 1, box[1] + pad - (2 if fnt is SILK else 0)), s, font=fnt, fill=fg)
    return box


def bubble(img, x, y, lines, tail=None, fnt=PRESS, fill=WHITE, ink=INK, pad=4, anchor="mb"):
    """Comic speech bubble; (x, y) anchors the box, the tail tip points at `tail`."""
    if isinstance(lines, str):
        lines = [lines]
    lh = 10 if fnt is PRESS else 8
    tw = max(text_width(s, fnt) for s in lines)
    w, h = tw + 2 * pad + 2, len(lines) * lh + 2 * pad - 2
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
        d.text((x + (w - text_width(s, fnt)) // 2 + 1, y + pad + i * lh - (2 if fnt is SILK else 0)), s,
               font=fnt, fill=ink)
    return (x, y, x + w, y + h)


@lru_cache(maxsize=256)
def _stamp_img(s, color, angle, size):
    fnt = {8: PRESS, 16: PRESS16, 24: PRESS24}[size]
    tw, th = text_width(s, fnt), fnt.size
    pad = 3 if size == 8 else 4
    w, h = tw + 2 * pad + 4, th + 2 * pad + 3
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w - 1, h - 1), outline=tuple(color) + (255,), width=2 if size > 8 else 1)
    d.text((pad + 2, pad + 2), s, font=fnt, fill=tuple(color) + (255,))
    arr = np.array(im)
    holes = np.random.default_rng(len(s) * 7 + size).random(arr.shape[:2]) < 0.12
    arr[holes, 3] = 0
    return Image.fromarray(arr, "RGBA").rotate(angle, resample=Image.NEAREST, expand=True)


def stamp(img, cx, cy, s, color=RED, angle=-12, size=16, age=1.0):
    """An ink stamp that slams down (drops in over ~0.1 s); nothing before age 0."""
    if age < 0:
        return
    im = _stamp_img(s, tuple(color), angle, size)
    dy = int(round(max(0.0, 1 - age / 0.1) * -14))
    paste(img, im, cx, cy + dy, "mm")


def strike(img, x0, y, x1, p=1.0, color=RED, width=2):
    """A hand-drawn strike-through, drawn left to right as p goes 0 -> 1."""
    if p <= 0:
        return
    d = ImageDraw.Draw(img)
    xe = x0 + (x1 - x0) * min(1.0, p)
    d.line([(x0, y + 1), (xe, y - 1)], fill=INK, width=width + 2)
    d.line([(x0, y + 1), (xe, y - 1)], fill=color, width=width)


def arrow(img, x0, y0, x1, y1, color=GOLD, width=2, head=5):
    d = ImageDraw.Draw(img)
    a = math.atan2(y1 - y0, x1 - x0)
    tip = [(x1, y1), (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5)),
           (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))]
    d.line([(x0, y0), (x1, y1)], fill=INK, width=width + 2)
    d.polygon([(x + (x - x1) * 0.25, y + (y - y1) * 0.25) for x, y in tip], fill=INK)
    d.line([(x0, y0), (x1 - 2 * math.cos(a), y1 - 2 * math.sin(a))], fill=color, width=width)
    d.polygon(tip, fill=color)


def typed(s, age, cps=20.0):
    """The part of `s` typed (or quilled) so far."""
    return s[:max(0, int(age * cps))]


# --- parchment and paper ------------------------------------------------------------------

def parchment(img, box, title=None, lines=(), fnt=SILK, ink=(70, 40, 20), seal=False, rolled=True):
    """A sheet of parchment with optional rolled ends, a title, text lines and a wax seal."""
    x0, y0, x1, y1 = (int(v) for v in box)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK)
    d.rectangle((x0, y0, x1, y1), fill=C["paper"])
    d.line([(x0, y1), (x1, y1)], fill=C["paper_sh"]); d.line([(x1, y0), (x1, y1)], fill=C["paper_sh"])
    if rolled:
        for yy in (y0, y1):
            d.rectangle((x0 - 2, yy - 2, x1 + 2, yy + 1), fill=INK)
            d.rectangle((x0 - 1, yy - 1, x1 + 1, yy), fill=C["paper_sh"])
            d.line([(x0 - 1, yy - 1), (x1 + 1, yy - 1)], fill=C["paper"])
    y = y0 + 3
    if title:
        tf = PRESS if fnt is SILK else fnt
        d.text(((x0 + x1) // 2, y), title, font=tf, fill=ink, anchor="ma")
        y += tf.size + 3
    for s in lines:
        if s == "~":                                   # a scribble line of handwriting
            for x in range(x0 + 4, x1 - 4, 3):
                d.line([(x, y + 3 + (x % 2)), (x + 2, y + 3 - (x % 3 == 0))], fill=mix(C["paper"], ink, 0.6))
            y += 6
            continue
        d.text((x0 + 4, y - (2 if fnt is SILK else 0)), s, font=fnt, fill=ink)
        y += 8 if fnt is SILK else fnt.size + 2
    if seal:
        sx, sy = x1 - 7, y1 - 7
        d.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=INK)
        d.ellipse((sx - 3, sy - 3, sx + 3, sy + 3), fill=C["wax"])
        d.point((sx - 1, sy - 1), fill=C["wax_hi"])
    return (x0, y0, x1, y1)


@lru_cache(maxsize=None)
def envelope(w=24, h=16, seal=True, sprig=False, text=None):
    """A sealed letter."""
    s = Canvas(w + 2, h + 2)
    s.rect((1, 1, w, h), "paper")
    s.line([(1, h), (w, h)], "paper_sh"); s.line([(w, 1), (w, h)], "paper_sh")
    s.line([(1, 1), (w // 2, h // 2)], "paper_sh"); s.line([(w, 1), (w // 2 + 1, h // 2)], "paper_sh")
    if sprig:
        s.line([(3, 4), (9, 2)], "olive")
        s.pxs([(4, 2), (6, 4), (7, 1), (9, 3)], "olive")
    if text:
        s.text((w // 2 + 1, h // 2 + 1), text, "ink", anchor="ma")
    if seal:
        s.ell((w // 2 - 2, h // 2 - 2, w // 2 + 3, h // 2 + 2), "wax")
        s.px((w // 2 - 1, h // 2 - 1), "wax_hi")
    return s.done()


@lru_cache(maxsize=None)
def scroll_sprite(w=30, h=22, title=None, lines=2, seal=False):
    """A small rolled document for carrying about or throwing."""
    im = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
    parchment(im, (3, 3, w + 2, h + 2), title=title, lines=["~"] * lines, seal=seal)
    return im


# --- ordnance, water and smoke ----------------------------------------------------------------

@lru_cache(maxsize=None)
def cannonball(r=2, gilt=False):
    s = Canvas(2 * r + 3, 2 * r + 3)
    s.ell((1, 1, 2 * r + 1, 2 * r + 1), "gold" if gilt else "iron")
    s.px((r, r), "gold_hi" if gilt else "iron_hi")
    return s.done()


def projectile(p, a, b, lift):
    """Position along a parabolic arc from a to b that rises `lift` pixels at the top, p in [0, 1]."""
    return a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p - lift * 4 * p * (1 - p)


def splash(img, x, y, age, size=1.0, seed=0):
    """A splash where something hits the water: a crown of spray, then rings."""
    if not 0 <= age < 0.9:
        return
    d = ImageDraw.Draw(img)
    foam, spray = C["white"], (190, 204, 236)
    n = int(8 * size) + 3
    for i in range(n):
        a = math.pi * (0.15 + 0.7 * i / (n - 1))
        v = (40 + 30 * rnd("spl", seed, i)) * size
        px = x + math.cos(a) * v * age * 0.6
        py = y - math.sin(a) * v * age + 140 * age * age
        if py <= y:
            d.point((int(px), int(py)), fill=foam if i % 2 else spray)
            if size > 1.2:
                d.point((int(px) + 1, int(py)), fill=spray)
    if age < 0.25:
        h = int((6 + 4 * size) * (1 - abs(age - 0.12) / 0.13))
        d.line([(x, y), (x, y - h)], fill=foam, width=max(1, int(size + 0.5)))
    r = 2 + age * 14 * size
    d.arc((x - r, y - r * 0.3, x + r, y + r * 0.3), 180, 360, fill=foam)
    if age > 0.3:
        r2 = r * 0.6
        d.arc((x - r2, y - r2 * 0.3, x + r2, y + r2 * 0.3), 0, 180, fill=spray)


def puff(img, x, y, age, size=1.0, seed=0, color=None, drift=(-10, -6)):
    """A cannon-smoke puff that billows out and fades (dithered)."""
    if not 0 <= age < 2.0:
        return
    base = color or (214, 204, 220)
    r = (3 + 8 * min(1.0, age / 0.4)) * size
    for i in range(5):
        a = rnd("pf", seed, i) * 2 * math.pi
        ox, oy = math.cos(a) * r * 0.6, math.sin(a) * r * 0.4
        cx, cy = x + ox + drift[0] * age, y + oy + drift[1] * age
        rr = r * (0.5 + 0.4 * rnd("pr", seed, i))
        dens = clamp(1.0 - age / 2.0, 0, 1)
        m = pixel.mask(lambda dd: dd.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255), img.size)
        pixel.dither(img, m * dens, base, blend=0.9, phase=i)
        pixel.dither(img, m * dens * 0.5, mix(base, WHITE, 0.6), blend=0.9, phase=i + 2)


def muzzle_flash(img, x, y, age, facing=1, size=1.0):
    if not 0 <= age < 0.12:
        return
    d = ImageDraw.Draw(img)
    L = int(6 * size)
    d.polygon([(x, y - 2), (x + facing * L, y), (x, y + 2)], fill=C["gold"])
    d.polygon([(x, y - 1), (x + facing * L * 0.6, y), (x, y + 1)], fill=C["gold_hi"])


def burst(img, x, y, r0, r1, color=GOLD, spikes=10, rot=0.0):
    """A spiky impact star."""
    pts = []
    for i in range(spikes * 2):
        a = rot + i * math.pi / spikes
        r = r1 if i % 2 == 0 else r0
        pts.append((x + math.cos(a) * r, y + math.sin(a) * r))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=color, outline=INK)


def sparkle(img, x, y, size=2, color=WHITE):
    d = ImageDraw.Draw(img)
    d.line([(x - size, y), (x + size, y)], fill=color)
    d.line([(x, y - size), (x, y + size)], fill=color)


# --- period objects --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def tea_crate(label_="TEA"):
    s = Canvas(18, 14)
    s.rect((1, 2, 16, 12), "wood"); s.rect((1, 2, 16, 3), "wood_hi"); s.line([(1, 12), (16, 12)], "wood_sh")
    s.line([(1, 7), (16, 7)], "wood_sh")
    s.text((9, 3), label_, "ink", anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def barrel():
    s = Canvas(12, 14)
    s.rect((2, 1, 9, 12), "wood"); s.rect((1, 3, 10, 10), "wood")
    s.line([(3, 1), (3, 12)], "wood_hi")
    for y in (3, 10):
        s.line([(1, y), (10, y)], "iron")
    return s.done()


@lru_cache(maxsize=None)
def bottle(message=True):
    s = Canvas(16, 8)
    s.rect((1, 2, 10, 5), (120, 170, 140)); s.rect((11, 3, 13, 4), (120, 170, 140)); s.rect((14, 3, 14, 4), "wood")
    s.line([(2, 2), (9, 2)], (190, 230, 200))
    if message:
        s.rect((3, 3, 8, 4), "paper")
    return s.done()


@lru_cache(maxsize=None)
def coin(face="george", r=6):
    """A coin with a profile on it (a stack of pixels suggests the head)."""
    s = Canvas(2 * r + 3, 2 * r + 3)
    s.ell((1, 1, 2 * r + 1, 2 * r + 1), "steel_sh" if face == "washington" else "gold_sh")
    s.ell((2, 2, 2 * r, 2 * r), "steel" if face == "washington" else "gold")
    cx, cy = r + 1, r + 1
    col = "steel_sh" if face == "washington" else "gold_sh"
    s.rect((cx - 2, cy - 3, cx + 1, cy + 2), col)
    s.px((cx + 2, cy - 1), col)
    s.rect((cx - 3, cy - 2, cx - 3, cy + 1), col)
    return s.done()


@lru_cache(maxsize=None)
def quill():
    s = Canvas(14, 14)
    s.poly([(12, 1), (8, 3), (3, 10), (5, 10), (11, 4)], "white")
    s.line([(12, 1), (2, 12)], "white_sh")
    s.line([(2, 12), (1, 13)], "ink")
    return s.done()


@lru_cache(maxsize=None)
def white_flag():
    s = Canvas(18, 20)
    s.line([(2, 1), (2, 19)], "wood_sh")
    s.poly([(3, 2), (15, 3), (13, 7), (15, 11), (3, 10)], "white")
    s.line([(3, 10), (15, 11)], "white_sh")
    return s.done()


@lru_cache(maxsize=None)
def cherry_tree(chopped=False):
    s = Canvas(24, 30)
    s.rect((10, 16, 13, 28), "wood_sh"); s.line([(10, 16), (10, 28)], "wood")
    if not chopped:
        s.ell((2, 1, 21, 18), (70, 120, 70)); s.ell((4, 2, 14, 11), (100, 150, 84))
        for p in ((6, 8), (15, 6), (11, 13), (17, 12), (8, 4)):
            s.rect((p[0], p[1], p[0] + 1, p[1] + 1), (200, 30, 50))
    else:
        s.rect((10, 14, 13, 16), "wood_hi")
    return s.done()


@lru_cache(maxsize=None)
def hatchet():
    s = Canvas(14, 14)
    s.line([(2, 12), (10, 4)], "wood", 2)
    s.poly([(8, 1), (13, 4), (11, 7), (7, 4)], "steel")
    s.line([(12, 4), (10, 6)], "steel_sh")
    return s.done()


@lru_cache(maxsize=None)
def teacup():
    s = Canvas(14, 10)
    s.poly([(1, 2), (10, 2), (9, 7), (2, 7)], "white"); s.line([(2, 7), (9, 7)], "white_sh")
    s.ell((9, 3, 13, 6), "white"); s.img.putpixel((11, 4), (0, 0, 0, 0))
    s.line([(0, 8), (11, 8)], "white_sh")
    s.line([(2, 3), (9, 3)], (150, 90, 60))
    s.px((4, 5), "sash"); s.px((7, 5), "sash")
    return s.done()


@lru_cache(maxsize=None)
def planet(ring=True, color=(150, 220, 226)):
    s = Canvas(22, 16)
    s.ell((5, 2, 16, 13), color)
    s.ell((5, 2, 11, 8), mix(color, WHITE, 0.4))
    if ring:
        s.line([(1, 9), (20, 5)], (210, 230, 240))
    return s.done()


# --- floating on the water -------------------------------------------------------------------

def float_on_water(img, spr, x, y, t, seed=0, sink=3, amp=1.0, sea_color=None, foam=(222, 226, 242)):
    """Paste `spr` bobbing with its waterline at y (x is its centre); the bottom `sink` rows go under.
    A sink as deep as the sprite is tall hides it completely."""
    from scene import P, sea_band
    sea_color = sea_color or P["sea"][sea_band(y + 2)]
    bob = int(round(amp * math.sin(t * 2.3 + seed * 1.7)))
    tilt = math.sin(t * 1.7 + seed) * 4 * amp
    im = spr.rotate(tilt, resample=Image.NEAREST, expand=True) if abs(tilt) > 1.5 else spr
    if sink >= im.height:
        return
    top = int(y + bob - im.height + sink)
    left = int(x - im.width // 2)
    if sink > 3:                       # deeper than the painted waterline: crop, don't paint the sea over it
        im = im.crop((0, 0, im.width, im.height - sink + 3))
    img.paste(im, (left, top), im)
    wl = y + bob
    d = ImageDraw.Draw(img)
    for yy in range(wl + 1, wl + min(sink, 3) + 1):
        for xx in range(left - 1, left + im.width + 1):
            if (xx + yy) % 2 == 0 or yy > wl + 1:
                d.point((xx, yy), fill=sea_color)
    for xx in range(left - 2, left + im.width + 2):
        if (xx // 2 + int(t * 3)) % 3 != 2:
            d.point((xx, wl), fill=foam)
