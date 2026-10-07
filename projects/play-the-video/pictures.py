"""What the verse gags draw with: `Pic`, a picture for the window in the corner (PW x PH = 100 x 54), and
the small things that turn up in more than one of them.

    p = Pic("panel")
    p.header("MOLD FOUND ON", "mold_sh", h=9)
    p.put(roach_big(), 50, 30)
    show(c, p.img, "EXHIBIT", "CLIP")

A picture stands in for the other man's paused video for as long as its bar lasts: the host has pulled
something up. Each verse's pictures live next to the gags that show them (gags_<section>.py).
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from characters import head
from engine import C, INK, KIT, PRESS, PRESS16, SILK, SILK16, Canvas, col, rgba, rnd, silk_w
from stream import PH, PW


class Pic(KIT.Pic):
    """An opaque picture for the window (PW x PH unless told otherwise); `img` is the picture."""

    def __init__(self, bg="panel", w=PW, h=PH):
        super().__init__(bg, w, h)

    def mold(self, box, n, seed=0, dark=0.3):
        """Spots of mould scattered in a box."""
        x0, y0, x1, y1 = box
        for i in range(n):
            x = x0 + int(rnd("mx", seed, i) * (x1 - x0))
            y = y0 + int(rnd("my", seed, i) * (y1 - y0))
            c = "mold_sh" if rnd("mc", seed, i) < dark else "mold"
            if rnd("ms", seed, i) < 0.4:
                self.rect((x, y, x + 1, y + 1), c)
            else:
                self.px((x, y), c)

    def stink(self, x, y, t, n=3, h=10, gap=5, color="mold"):
        """Wavy lines rising from a point."""
        for i in range(n):
            pts = [(x + i * gap + int(round(1.5 * math.sin(k * 0.9 + t * 6 + i))), y - k) for k in range(0, h, 2)]
            self.line(pts, color)

    def panel(self, box, edge="gold", fill="bg"):
        """A game's window: dark, with a thin coloured edge."""
        self.rect(box, fill)
        self.d.rectangle(box, outline=col(edge))

    def meter(self, box, k, fill="ok", back="black"):
        """A health or experience bar, k of the way full."""
        x0, y0, x1, y1 = box
        self.rect(box, back)
        if k > 0:
            self.rect((x0, y0, x0 + int(round((x1 - x0) * min(1.0, k))), y1), fill)
        self.d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), outline=INK)

    def bolt(self, x, y, s=1, color="yellow"):
        """A lightning bolt, its top at (x, y), 5 s wide and 9 s tall."""
        self.poly([(x + 3 * s, y), (x, y + 5 * s), (x + 2 * s, y + 5 * s), (x + s, y + 9 * s), (x + 5 * s, y + 3 * s),
                   (x + 3 * s, y + 3 * s), (x + 4 * s, y)], color)


# --- small things ------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def mug(who, eyes="open", brows="neutral", mouth="closed", k=2):
    """His head, small enough for a picture: 30 x 30 at k=2, 20 x 20 at k=3."""
    h = head(who, eyes, brows, mouth).convert("RGBa")
    m = h.resize((h.width // k, h.height // k), Image.BOX).convert("RGBA")
    m.putalpha(m.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    return m


@lru_cache(maxsize=None)
def roach_big(step=0, crown=False):
    """A cockroach in close-up, facing right (34 x 20, more with the crown): `step` 0/1 moves its legs."""
    f = Canvas(36, 28)
    oy = 7
    for i, x in enumerate((10, 15, 20)):                                # the legs
        dy = (i + step) % 2
        f.line([(x, oy + 5), (x - 3, oy + 1 + dy), (x - 5, oy + dy)], "roach_sh")
        f.line([(x, oy + 13), (x - 3, oy + 17 - dy), (x - 5, oy + 18 - dy)], "roach_sh")
    f.ell((5, oy + 4, 26, oy + 14), "roach")                            # the wing case
    f.line([(8, oy + 9), (24, oy + 9)], "roach_sh")
    f.line([(9, oy + 6), (20, oy + 6)], "orange")
    f.ell((22, oy + 5, 30, oy + 13), "roach_sh")                        # the head
    f.px((27, oy + 7), "white"); f.px((27, oy + 11), "white")
    f.line([(29, oy + 6), (33, oy + 2 + step), (35, oy + 2 + step)], "roach_sh")      # the feelers
    f.line([(29, oy + 12), (33, oy + 16 - step), (35, oy + 16 - step)], "roach_sh")
    img = f.done()
    if crown:
        img.alpha_composite(crown_small(), (17, 0))
    return img


@lru_cache(maxsize=None)
def crown_small():
    f = Canvas(13, 9)
    f.poly([(1, 7), (1, 2), (4, 5), (6, 1), (8, 5), (11, 2), (11, 7)], "gold")
    f.line([(1, 7), (11, 7)], "gold_sh")
    f.px((6, 3), "red"); f.px((2, 4), "gold_hi"); f.px((10, 4), "gold_hi")
    return f.done()


@lru_cache(maxsize=None)
def tooth(w=18, yellow=True, chipped=False):
    """A molar, crown up, `w` wide."""
    h = int(w * 1.25)
    f = Canvas(w + 2, h + 2)
    c0 = "tooth_y" if yellow else "tooth"
    q = w // 4
    f.poly([(1, 4), (1 + q, 1), (w // 2, 4), (w - q, 1), (w, 4), (w, h // 2), (w - 2, h), (w - q - 1, h),
            (w // 2, h // 2 + 3), (1 + q + 1, h), (3, h), (1, h // 2)], c0)
    f.line([(3, 5), (3, h // 2)], "white")
    if yellow:
        f.pxs([(w - 4, h // 2 - 2), (w - 5, h // 2 + 1), (w // 2 + 1, 6)], "brown_hi")
    if chipped:
        f.d.polygon([(w - q - 1, 0), (w + 1, 0), (w + 1, 7), (w - q + 1, 5)], fill=(0, 0, 0, 0))
    return f.done()


def villa(p, x, y):
    """His house in the hills, 48 x 34 with its palm: two white boxes and a lot of glass."""
    p.rect((x + 12, y, x + 38, y + 12), "white"); p.d.rectangle((x + 12, y, x + 38, y + 12), outline=INK)   # upstairs
    p.rect((x + 16, y + 3, x + 34, y + 9), "night_hi")
    p.rect((x + 4, y + 12, x + 47, y + 33), "white"); p.d.rectangle((x + 4, y + 12, x + 47, y + 33), outline=INK)
    p.rect((x + 8, y + 16, x + 28, y + 28), "night_hi"); p.line([(x + 18, y + 16), (x + 18, y + 28)], "white")
    p.rect((x + 34, y + 18, x + 42, y + 33), "wood")                                         # the door
    p.line([(x + 4, y + 12), (x + 47, y + 12)], "grey")
    p.rect((x, y + 18, x + 1, y + 33), "wood_sh")                                            # a palm
    for dx, dy in ((-5, 1), (-3, -2), (0, -3), (4, -2), (6, 1)):
        p.line([(x, y + 17), (x + dx, y + 16 + dy)], "grass_sh")


def tub(p, x, y, half=False, bg="hwall"):
    """A bathtub, 24 wide and 13 tall: or what's left of one."""
    p.rbox((x + 1, y + 3, x + 22, y + 10), "white", "ink", 3)
    p.rect((x, y + 2, x + 23, y + 3), "white"); p.d.rectangle((x - 1, y + 1, x + 24, y + 4), outline=INK)
    p.rect((x + 3, y + 5, x + 20, y + 5), "sky_hi")
    p.rect((x + 4, y + 11, x + 5, y + 12), "gold_sh"); p.rect((x + 18, y + 11, x + 19, y + 12), "gold_sh")
    p.rect((x + 19, y - 2, x + 20, y + 1), "steel_sh"); p.rect((x + 17, y - 2, x + 19, y - 1), "steel_sh")
    if half:
        p.rect((x + 12, y - 3, x + 25, y + 13), bg)
        p.d.line([(x + 12, y + 1), (x + 10, y + 4), (x + 12, y + 7), (x + 10, y + 10), (x + 12, y + 12)], fill=INK)


@lru_cache(maxsize=None)
def porsche():
    """His electric Porsche, from the side (48 x 19)."""
    f = Canvas(48, 19)
    body = [(0, 12), (2, 8), (12, 6), (18, 1), (31, 1), (39, 6), (45, 8), (47, 12), (45, 14), (2, 14)]
    f.poly(body, "white"); f.d.line(body + body[:1], fill=INK + (255,))
    f.poly([(19, 3), (30, 3), (35, 6), (15, 6)], "night_hi"); f.line([(25, 3), (25, 6)], "white")
    f.line([(3, 11), (44, 11)], "grey_hi")
    for x in (6, 33):
        f.ell((x, 9, x + 9, 18), "black"); f.ell((x + 3, 12, x + 6, 15), "steel")
    f.px((46, 10), "gold_hi"); f.px((1, 10), "live")
    return f.done()


def coin_stack(p, x, y, n):
    """n coins stacked with the top one's face showing, the bottom at y."""
    for i in range(n):
        p.rect((x, y - 3 * i - 2, x + 9, y - 3 * i), "gold")
        p.line([(x, y - 3 * i), (x + 9, y - 3 * i)], "gold_sh")
    p.ell((x, y - 3 * n - 2, x + 9, y - 3 * n + 2), "gold_hi")


__all__ = ["Pic", "PW", "PH", "mug", "roach_big", "crown_small", "tooth", "coin_stack", "villa", "tub", "porsche",
           "Image", "ImageDraw", "C",
           "INK", "PRESS", "PRESS16", "SILK", "SILK16", "Canvas", "col", "rgba", "rnd", "silk_w", "math", "lru_cache"]
