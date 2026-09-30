"""Props and text effects for the gags: the planet trophy, screens, posters, paperwork, smoke.

Sprites are cached RGBA images drawn on a Canvas and outlined in ink. Functions
that take an `img` draw straight onto a world or UI layer. The text and comic
effects are pixelart.fx bound to this video's ink and fonts.
"""
import math
from functools import lru_cache, partial

from PIL import Image, ImageDraw

from engine import (C, INK, PRESS, PRESS16, PRESS24, SILK, Canvas, blend, clamp, col, mix, outlined, paste, rnd, text_width)
from pixelart import fx, pixel

GOLD, WHITE, RED = C["gold"], C["white"], C["red"]
ORANGE = (255, 138, 40)

# --- text and comic effects (pixelart.fx in this video's ink) ---------------------------------

big_text = partial(fx.big_text, outline=INK, ink=INK)
pop_text = partial(fx.pop_text, outline=INK, ink=INK)
bubble = partial(fx.bubble, ink=INK, fill=WHITE)
strike = partial(fx.strike, ink=INK, color=RED)
arrow = partial(fx.arrow, ink=INK, color=GOLD)
burst = partial(fx.burst, ink=INK)
sparkle, typed = fx.sparkle, fx.typed


def label(img, xy, s, fnt=SILK, bg=WHITE, fg=INK, pad=2, anchor="la", border=INK):
    """Text on a flat plate with a 1px border."""
    silk = fnt is SILK
    return fx.label(img, xy, s, fnt, bg, fg, pad, anchor, border, th=6 if silk else None, text_dy=-2 if silk else 0)


def stamp(img, cx, cy, s, color=RED, angle=-12, size=16, age=1.0):
    """An ink stamp that slams down; `size` is 8, 16 or 24."""
    fx.stamp(img, cx, cy, s, {8: PRESS, 16: PRESS16, 24: PRESS24}[size], tuple(col(color)), angle, age)


def projectile(p, a, b, lift):
    """Position along a parabolic arc from a to b that rises `lift` pixels at the top, p in [0, 1]."""
    return a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p - lift * 4 * p * (1 - p)


def puff(img, x, y, age, size=1.0, seed=0, color=(214, 204, 220), drift=(-10, -6), life=1.6):
    """A puff of smoke or dust that billows out and thins (flat tints, no dither)."""
    if not 0 <= age < life:
        return
    r = (3 + 8 * min(1.0, age / 0.4)) * size
    fade = clamp(1.0 - age / life, 0, 1)
    for i in range(5):
        a = rnd("pf", seed, i) * 2 * math.pi
        cx = x + math.cos(a) * r * 0.6 + drift[0] * age
        cy = y + math.sin(a) * r * 0.4 + drift[1] * age
        rr = r * (0.5 + 0.4 * rnd("pr", seed, i))
        m = pixel.mask(lambda d: d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255), img.size)
        blend(img, m, color, 0.75 * fade)


def ring(img, x, y, r, color=RED, width=1):
    """A circle drawn round something (with an ink edge), like a pundit's marker."""
    a = (255,) if img.mode == "RGBA" else ()
    d = ImageDraw.Draw(img)
    d.ellipse((x - r - 1, y - r - 1, x + r + 1, y + r + 1), outline=INK + a, width=width + 1)
    d.ellipse((x - r, y - r, x + r, y + r), outline=col(color) + a, width=width)


def speed_lines(img, cx, cy, r0, color=WHITE, n=24, seed=0, width=1):
    """Manga speed lines converging on (cx, cy), starting r0 out."""
    d = ImageDraw.Draw(img)
    for k in range(n):
        a = k * 2 * math.pi / n + rnd("sl", seed, k) * 0.2
        r1 = r0 + 30 + rnd("sl-l", seed, k) * 60
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)],
               fill=col(color) + ((255,) if img.mode == "RGBA" else ()), width=width)


# --- the planet: the trophy the battle is for -------------------------------------------------

@lru_cache(maxsize=64)
def globe(r=8, phase=0, lit=True):
    """The Earth as a little sphere: seas, three continents and an ice cap, lit from the top left.
    `phase` (0-15) turns it."""
    n = 2 * r + 3
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    px = img.load()
    sea, sea_sh, sea_hi = C["sea"], C["sea_sh"], C["sea_hi"]
    land, land_sh = C["leaf_hi"], C["leaf"]
    for y in range(n):
        for x in range(n):
            dx, dy = (x - r - 1) / (r + 0.5), (y - r - 1) / (r + 0.5)
            if dx * dx + dy * dy > 1:
                continue
            z = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
            lon = math.atan2(dx, z) + phase * math.pi / 8
            lat = math.asin(clamp(dy, -1, 1))
            v = (math.sin(lon * 2 + 0.6) * math.cos(lat * 3) + 0.55 * math.sin(lon * 5 + lat * 4)
                 + 0.35 * math.cos(lon * 3 - lat * 6))
            light = -0.6 * dx - 0.6 * dy + 0.5 * z
            if abs(lat) > 1.15:
                c = C["snow"] if light > -0.1 else C["snow_sh"]
            elif v > 0.55:
                c = land if light > 0.05 else land_sh
            else:
                c = sea_hi if light > 0.55 else sea if light > -0.25 else sea_sh
            px[x, y] = c + (255,)
    if lit:
        px[r - r // 2, r - r // 2] = WHITE + (255,)
    return outlined(img)


@lru_cache(maxsize=32)
def trophy(phase=0, r=7, planet=True):
    """The prize: a gold cup on a stepped plinth, holding up the planet (or not, once it's been won)."""
    g = globe(r, phase)
    w = max(g.width, 26)
    s = Canvas(w + 2, g.height + 26)
    cx = (w + 2) // 2
    top = g.height - 2
    s.poly([(cx - 8, top), (cx + 8, top), (cx + 5, top + 7), (cx - 5, top + 7)], "gold")      # the cup
    s.line([(cx - 7, top + 1), (cx - 4, top + 6)], "gold_hi")
    s.line([(cx + 7, top + 1), (cx + 4, top + 6)], "gold_sh")
    s.rect((cx - 1, top + 7, cx + 1, top + 12), "gold_sh")                                     # stem
    s.rect((cx - 6, top + 13, cx + 6, top + 16), "gold")                                       # base
    s.line([(cx - 6, top + 13), (cx + 6, top + 13)], "gold_hi")
    s.rect((cx - 9, top + 17, cx + 9, top + 22), "wood")                                       # plinth
    s.line([(cx - 9, top + 22), (cx + 9, top + 22)], "wood_sh")
    s.rect((cx - 5, top + 18, cx + 5, top + 20), "gold_sh")                                    # name plate
    img = s.done()
    if planet:
        img.alpha_composite(g, ((w + 2 - g.width) // 2, 0))
    return img


# --- screens, posters, paper ------------------------------------------------------------------

def tv(img, box, screen=None, on=True, color=(96, 70, 56), knobs=True):
    """A wood-cased CRT television; `screen` (an RGB/RGBA image) is fitted into the glass."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    a = (255,) if img.mode == "RGBA" else ()
    d.rounded_rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), radius=4, fill=INK + a)
    d.rounded_rectangle((x0, y0, x1, y1), radius=3, fill=col(color) + a)
    sx0, sy0, sx1, sy1 = x0 + 4, y0 + 4, x1 - (14 if knobs else 4), y1 - 4
    d.rounded_rectangle((sx0 - 1, sy0 - 1, sx1 + 1, sy1 + 1), radius=3, fill=INK + a)
    if screen is not None and on:
        scr = screen.resize((sx1 - sx0, sy1 - sy0), Image.NEAREST) if screen.size != (sx1 - sx0, sy1 - sy0) else screen
        img.paste(scr.convert(img.mode), (sx0, sy0))
    else:
        d.rounded_rectangle((sx0, sy0, sx1, sy1), radius=2, fill=(40, 46, 44) + a)
    d.line([(sx0 + 2, sy0 + 1), (sx0 + 8, sy0 + 1)], fill=(230, 240, 236) + a)
    if knobs:
        for k in range(2):
            d.ellipse((x1 - 10, y0 + 6 + k * 9, x1 - 5, y0 + 11 + k * 9), fill=(50, 40, 36) + a)
        d.rectangle((x1 - 10, y1 - 9, x1 - 5, y1 - 5), fill=(60, 50, 44) + a)
    return sx0, sy0, sx1, sy1


def poster(img, box, title, sub=None, color=(40, 30, 60), art=None, fg=C["gold_hi"]):
    """A film poster: a colour field, optional art (RGBA sprite, pasted centred), a title block."""
    x0, y0, x1, y1 = (int(v) for v in box)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    a = (255,) if img.mode == "RGBA" else ()
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK + a)
    d.rectangle((x0, y0, x1, y1), fill=col(color) + a)
    if art is not None:
        paste(img, art, (x0 + x1) // 2, y0 + (y1 - y0) * 2 // 5, "mm")
    rows = title.split("\n")
    yy = y1 - 4 - 7 * len(rows) - (7 if sub else 0)
    for r in rows:
        pixel.text(img, ((x0 + x1) // 2, yy), r, SILK, col(fg), shadow=INK, anchor="ma")
        yy += 7
    if sub:
        pixel.text(img, ((x0 + x1) // 2, yy), sub, SILK, (220, 214, 200), shadow=None, anchor="ma")


@lru_cache(maxsize=None)
def book(title="", w=22, h=28, color=(120, 60, 140), sub=None):
    s = Canvas(w + 2, h + 2)
    s.rect((1, 1, w, h), color)
    s.rect((1, 1, 3, h), mix(color, INK, 0.35))
    s.line([(4, 2), (w - 1, 2)], mix(color, WHITE, 0.3))
    s.rect((w - 1, 3, w, h - 1), "paper")
    if title:
        for i, row in enumerate(title.split("\n")):
            s.text(((w + 5) // 2, 4 + i * 7), row, "paper", anchor="ma")
    if sub:
        s.text(((w + 5) // 2, h - 8), sub, "gold", anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def toe_tag(text="MORGAN F."):
    """A mortuary toe tag on its string."""
    w = max(30, text_width(text, SILK) + 16)
    s = Canvas(w, 16)
    s.poly([(6, 2), (w - 3, 2), (w - 3, 13), (6, 13), (2, 8)], (226, 206, 150))
    s.line([(6, 13), (w - 3, 13)], (184, 160, 110))
    s.ell((5, 6, 8, 9), "white")
    s.text(((w + 7) // 2, 1), text, "ink", anchor="ma")
    s.line([(11, 10), (w - 6, 10)], (170, 150, 110))
    return s.done()


@lru_cache(maxsize=None)
def clapper(text="TAKE 1"):
    s = Canvas(30, 26)
    s.rect((1, 8, 28, 24), "black")
    s.line([(3, 12), (26, 12)], "white")
    s.text((15, 14), text, "white", anchor="ma")
    s.poly([(1, 2), (27, 0), (28, 6), (2, 8)], "black")
    for k in range(4):
        s.poly([(4 + k * 7, 2), (8 + k * 7, 1), (6 + k * 7, 7), (2 + k * 7, 7)], "white")
    return s.done()


def clapperboard(img, cx, cy, rows, open_=0.0):
    """A film slate drawn straight onto img, centred on (cx, cy): chalk `rows` on the board and the
    striped clapstick raised by `open_` (0 shut, 1 wide open)."""
    a = (255,) if img.mode == "RGBA" else ()
    ink, white, black = INK + a, WHITE + a, C["black"] + a
    tw = max(text_width(r, SILK) for r in rows)
    w, h = tw + 14, 10 * len(rows) + 6
    x0, y0 = int(cx - w / 2), int(cy - h / 2 + 5)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.rectangle((x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1), fill=ink)
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=black)
    for i, r in enumerate(rows):
        yy = y0 + 3 + i * 10
        if i:
            d.line([(x0 + 3, yy - 2), (x0 + w - 3, yy - 2)], fill=(150, 150, 150) + a)
        d.text((x0 + w // 2, yy - 1), r, font=SILK, fill=white, anchor="ma")

    def stick(y_top, ang):
        """A striped bar hinged at the board's top-left corner, turned up by ang radians."""
        hx, hy = x0, y_top + 6
        def rot(px, py):
            dx, dy = px - hx, py - hy
            return (hx + dx * math.cos(ang) + dy * math.sin(ang), hy - dx * math.sin(ang) + dy * math.cos(ang))
        body = [rot(x0 - 1, y_top - 1), rot(x0 + w + 1, y_top - 1), rot(x0 + w + 1, y_top + 7), rot(x0 - 1, y_top + 7)]
        d.polygon(body, fill=ink)
        d.polygon([rot(x0, y_top), rot(x0 + w, y_top), rot(x0 + w, y_top + 6), rot(x0, y_top + 6)], fill=black)
        for k in range(0, w, 10):
            d.polygon([rot(x0 + k + 2, y_top), rot(x0 + k + 7, y_top), rot(x0 + k + 4, y_top + 6),
                       rot(x0 + k - 1, y_top + 6)], fill=white)

    stick(y0 - 8, 0.0)
    stick(y0 - 16, 0.5 * clamp(open_, 0, 1))


def checkbox(img, x, y, checked=0.0, size=9, color=(60, 180, 90)):
    """A ruled checkbox; `checked` 0-1 draws the tick stroke by stroke."""
    d = ImageDraw.Draw(img)
    a = (255,) if img.mode == "RGBA" else ()
    d.rectangle((x, y, x + size, y + size), fill=WHITE + a, outline=INK + a)
    if checked > 0:
        p = clamp(checked, 0, 1)
        m1 = (x + 2, y + size // 2)
        m2 = (x + size // 2 - 1, y + size - 2)
        m3 = (x + size + 3, y - 3)
        if p < 0.4:
            q = p / 0.4
            d.line([m1, (m1[0] + (m2[0] - m1[0]) * q, m1[1] + (m2[1] - m1[1]) * q)], fill=col(color) + a, width=2)
        else:
            q = (p - 0.4) / 0.6
            d.line([m1, m2], fill=col(color) + a, width=2)
            d.line([m2, (m2[0] + (m3[0] - m2[0]) * q, m2[1] + (m3[1] - m2[1]) * q)], fill=col(color) + a, width=2)


@lru_cache(maxsize=None)
def teacup():
    s = Canvas(14, 10)
    s.poly([(1, 2), (10, 2), (9, 7), (2, 7)], "white"); s.line([(2, 7), (9, 7)], "white_sh")
    s.ell((9, 3, 13, 6), "white"); s.img.putpixel((11, 4), (0, 0, 0, 0))
    s.line([(0, 8), (11, 8)], "white_sh")
    s.line([(2, 3), (9, 3)], (150, 90, 60))
    return s.done()


@lru_cache(maxsize=None)
def field_camera():
    """Sir David's camera: a boxy 16mm film camera with a big lens."""
    s = Canvas(24, 16)
    s.rect((3, 4, 16, 13), "black")
    s.line([(3, 4), (16, 4)], "mic_hi")
    s.ell((4, 0, 10, 5), "mic"); s.ell((10, 0, 16, 5), "mic")
    s.rect((17, 6, 22, 11), "mic"); s.rect((21, 5, 22, 12), "mic_hi")
    s.px((5, 7), "rec")
    return s.done()


@lru_cache(maxsize=None)
def crown(w=14):
    s = Canvas(w + 2, 10)
    s.poly([(1, 8), (1, 2), (4, 5), (w // 2 + 1, 1), (w - 2, 5), (w, 2), (w, 8)], "gold")
    s.line([(1, 8), (w, 8)], "gold_sh")
    s.px((w // 2 + 1, 5), "red"); s.px((4, 7), "sea"); s.px((w - 2, 7), "sea")
    return s.done()
