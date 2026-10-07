"""What the gags draw with: `Pic`, an opaque picture for ChatGPT's window, and the small things that turn
up in more than one of them (toy blocks, ticks, hearts, coins, a sheet of paper).

A picture is PW x PH (100 x 96) and is drawn with the palette's names:

    p = Pic("paper")
    p.header("MATCH HISTORY", "blue")
    p.silk((6, 20), "BARREL")
    show(c, p.img, "EXHIBIT C", L.age())

Each section's pictures live next to the gags that show them (gags_<section>.py).
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

import call
from characters import orb
from engine import C, KIT, PRESS, PRESS16, SILK16, Canvas, back_out, clamp, col, rgba, rnd, text_width
from pixelart import fx

PW, PH = call.PW, call.PH


class Pic(KIT.Pic):
    """An opaque picture for ChatGPT's window (PW x PH unless told otherwise); `img` is the picture."""

    def __init__(self, bg="paper", w=PW, h=PH):
        super().__init__(bg, w, h)

    def orb(self, x, y, r=8, mood="happy", talk=0, kind="gpt", ring=0):
        self.put(orb(r, mood, talk, kind, ring), x, y)

    def lines(self, box, n, col_="paper_ln", gap=5, short=()):
        super().lines(box, n, col_, gap, short)


# --- small things ------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def block(word, color="red", depth=3, fnt=PRESS, w=None, h=20):
    """A toy alphabet block with a word on its face (the face is w x h; `depth` shows its top and side)."""
    tw = text_width(word, fnt)
    w = w or tw + 4
    d = depth
    f = Canvas(w + d + 2, h + d + 2)
    hi, sh = {"red": ("red_hi", "red_sh"), "blue": ("blue_hi", "blue_sh"), "yellow": ("gold_hi", "gold_sh"),
              "green": ("green_hi", "green_sh")}[color]
    face = {"yellow": "gold"}.get(color, color)
    f.poly([(1, d + 1), (1 + d, 1), (w + d, 1), (w, d + 1)], hi)         # the top
    f.poly([(w, d + 1), (w + d, 1), (w + d, h), (w, h + d)], sh)         # the side
    f.rect((1, d + 1, w, h + d), face)
    f.rect((2, d + 2, w - 1, h + d - 1), "cream")
    f.d.text((2 + (w - 2 - tw) // 2 + 1, d + 2 + (h - 10) // 2 + 1), word, font=fnt, fill=f.c(sh))
    return f.done()


@lru_cache(maxsize=None)
def coin(r=4):
    f = Canvas(2 * r + 3, 2 * r + 3)
    f.ell((1, 1, 2 * r + 1, 2 * r + 1), "gold")
    f.d.arc((1, 1, 2 * r + 1, 2 * r + 1), 20, 160, fill=f.c("gold_sh"))
    f.line([(r + 1, 3), (r + 1, 2 * r - 1)], "gold_sh")
    f.px((r - 1, 3), "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def sheet(w=26, h=32, title=None, color="blue", n=4, tick=False, dog_ear=True):
    """A sheet of paper with a heading and ruled lines: a form, a letter, a writ."""
    f = Canvas(w + 2, h + 2)
    f.rect((1, 1, w, h), "paper")
    if dog_ear:
        f.d.polygon([(w - 5, 1), (w, 6), (w, 1)], fill=(0, 0, 0, 0))
        f.poly([(w - 5, 1), (w - 5, 6), (w, 6)], "paper_sh")
    y = 4
    if title:
        f.silk((1 + w // 2, y), title, color, anchor="ma")
        y += 8
    for i in range(n):
        f.line([(4, y + i * 4), (w - 3 - (6 if i == n - 1 else 0), y + i * 4)], "paper_ln")
    if tick:
        f.line([(w - 11, h - 8), (w - 9, h - 6), (w - 5, h - 11)], "green", w=2)
    return f.done()


def confetti(img, age, n=40, seed=0, box=None):
    """Paper confetti falling through a picture from age 0."""
    if age < 0:
        return
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box or (0, 0, img.width, img.height)
    cols = ("gold", "pink", "sam_hi", "blue_hi", "red_hi", "green_hi")
    for i in range(n):
        x = x0 + rnd("cx", seed, i) * (x1 - x0)
        v = 30 + 50 * rnd("cv", seed, i)
        y = y0 - 6 + (age * v + rnd("cy", seed, i) * (y1 - y0)) % (y1 - y0 + 8)
        x += 3 * math.sin(age * 5 + i)
        c0 = rgba(cols[i % len(cols)])
        if int(age * 8 + i) % 2:
            d.rectangle((x, y, x + 1, y + 2), fill=c0)
        else:
            d.rectangle((x, y, x + 2, y + 1), fill=c0)


def sparkles(img, x, y, age, n=5, r=14, color="gold_hi", seed=0):
    """A few twinkles round a point for the first second."""
    if not 0 <= age < 1.2:
        return
    for i in range(n):
        if int(age * 10 + i * 3) % 3 == 0:
            continue
        a = rnd("sp", seed, i) * 6.283
        rr = r * (0.5 + 0.5 * rnd("sr", seed, i))
        fx.sparkle(img, int(x + rr * math.cos(a)), int(y + rr * math.sin(a)), 1 + i % 2, col(color))


__all__ = ["Pic", "PW", "PH", "block", "coin", "sheet", "confetti", "sparkles", "Image", "ImageDraw", "back_out",
           "clamp", "C", "SILK16", "PRESS16"]
