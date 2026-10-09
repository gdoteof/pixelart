"""What the verse gags draw with: `Pic`, a picture for the window (PW x PH = 100 x 54), and the small
things that turn up in more than one of them.

    p = Pic("panel")
    p.header("CAP TABLE", "emiru_sh", h=9)
    p.put(mug("emiru", mouth="grin"), 50, 30)
    show(c, p.img, "RECEIPTS", "DOC")

A picture is up for as long as its bar lasts: the host has pulled something up. Each verse's pictures live
next to the gags that show them (gags_<section>.py).
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from characters import head
from engine import C, INK, KIT, PRESS, PRESS16, SILK, SILK16, Canvas, col, mirror, rgba, rnd, silk_w
from stream import PH, PW


class Pic(KIT.Pic):
    """An opaque picture for the window (PW x PH unless told otherwise); `img` is the picture."""

    def __init__(self, bg="panel", w=PW, h=PH):
        super().__init__(bg, w, h)

    def panel(self, box, edge="gold", fill="bg"):
        """A game's window: dark, with a thin coloured edge."""
        self.rect(box, fill)
        self.d.rectangle(box, outline=col(edge))

    def meter(self, box, k, fill="ok", back="black"):
        """A health or progress bar, k of the way full."""
        x0, y0, x1, y1 = box
        self.rect(box, back)
        if k > 0:
            self.rect((x0, y0, x0 + int(round((x1 - x0) * min(1.0, k))), y1), fill)
        self.d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), outline=INK)

    def ground(self, y, top="pasture", line="pasture_sh"):
        """Grass (or a floor) from y down."""
        self.rect((0, y, self.w, self.h), top)
        self.line([(0, y), (self.w, y)], line)

    def sky(self, y, top="sky", bottom="sky_hi"):
        self.grad((0, 0, self.w, y), top, bottom, steps=3)

    def fence(self, y, x0=0, x1=None, step=12, color="wood"):
        """A rail fence across the picture, its top rail at y."""
        x1 = self.w if x1 is None else x1
        for x in range(x0 + 2, x1, step):
            self.rect((x, y - 3, x + 1, y + 8), color + "_sh")
        self.line([(x0, y), (x1, y)], color + "_hi"); self.line([(x0, y + 4), (x1, y + 4)], color + "_hi")

    def verdict(self, x, y, s, color="live", bg="paper"):
        """A word in a heavy box, centred on (x, y): a ruling, a rubber stamp that can be read."""
        w = len(s) * 8 + 6
        x0, y0 = x - w // 2, y - 7
        self.rect((x0, y0, x0 + w, y0 + 13), bg)
        self.d.rectangle((x0, y0, x0 + w, y0 + 13), outline=col(color), width=2)
        self.press((x, y0 + 3), s, color, anchor="ma")

    def coin(self, x, y, r=4):
        self.ell((x - r, y - r, x + r, y + r), "gold"); self.d.ellipse((x - r, y - r, x + r, y + r), outline=INK)
        self.line([(x, y - r + 2), (x, y + r - 2)], "gold_sh")


@lru_cache(maxsize=None)
def mug(who, eyes="open", brows="neutral", mouth="smile", k=2):
    """Her head, small enough for a picture: 30 x 30 at k=2, 20 x 20 at k=3."""
    h = head(who, eyes, brows, mouth).convert("RGBa")
    m = h.resize((h.width // k, h.height // k), Image.BOX).convert("RGBA")
    m.putalpha(m.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    return m


@lru_cache(maxsize=None)
def title_pic():
    """The song's title: what a window shows before anything has been pulled up."""
    p = Pic("bg")
    p.grad((0, 0, PW, PH), "emiru_sh", "maya_sh", steps=5)
    p.press((PW // 2, 8), "OUT OF YOUR", "white", anchor="ma", shadow="ink")
    p.big((PW // 2, 19), "LEAGUE", "gold_hi", "gold")
    p.silk((PW // 2, 42), "EMIRU + MAYA HIGA", "text", anchor="ma")
    return p.img


@lru_cache(maxsize=None)
def welcome_pic():
    """The sign at the gate."""
    p = Pic("cream")
    p.d.rectangle((1, 1, PW - 2, PH - 3), outline=col("maya_sh"))
    p.silk((PW // 2, 6), "WELCOME TO", "maya_sh", anchor="ma")
    p.big((PW // 2, 14), "ALVEUS", "maya", "maya_sh")
    p.silk((PW // 2, 39), "THE ANIMALS ARE WORKING", "wood_sh", anchor="ma")
    return p.img


STANDBY_TITLE = {"emiru": "NOW PLAYING", "maya": "NOW PLAYING", "gate": "WELCOME", "shop": "GIFT SHOP"}


def standby(view):
    """What a view's window shows when no gag has put a picture in it."""
    return {"emiru": title_pic, "maya": title_pic, "gate": welcome_pic, "shop": title_pic}[view]()


__all__ = ["Pic", "PW", "PH", "mug", "title_pic", "welcome_pic", "Image", "ImageDraw", "C", "INK", "PRESS", "PRESS16",
           "SILK", "SILK16", "Canvas", "col", "mirror", "rgba", "rnd", "silk_w", "math", "lru_cache"]


# --- small things ------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def glue_gun():
    """The hot glue gun, nozzle to the right (26 x 18)."""
    f = Canvas(28, 20)
    f.rect((1, 4, 5, 6), "white")                                        # the stick, going in
    f.poly([(5, 2), (19, 2), (22, 5), (19, 8), (12, 8), (10, 17), (5, 17)], "teal")
    f.line([(7, 4), (17, 4)], "teal_sh"); f.rect((6, 10, 8, 15), "teal_sh")
    f.poly([(22, 4), (27, 5), (22, 7)], "orange")
    f.line([(12, 9), (14, 12)], "orange", w=2)                           # the trigger
    return f.done()


@lru_cache(maxsize=None)
def scissors(open_=1):
    """Dressmaker's shears, points up (16 x 26): `open_` 0 shuts them."""
    f = Canvas(18, 28)
    dx = 4 if open_ else 1
    f.line([(8, 16), (8 - dx, 1)], "steel", w=2); f.line([(9, 16), (9 + dx, 1)], "steel_hi", w=2)
    f.px((8, 14), "steel_sh")
    f.ell((2, 17, 8, 25), "ears"); f.ell((9, 17, 15, 25), "ears")
    f.d.ellipse((4, 19, 6, 23), fill=(0, 0, 0, 0)); f.d.ellipse((11, 19, 13, 23), fill=(0, 0, 0, 0))
    return f.done()


@lru_cache(maxsize=None)
def can(wings=False):
    """The energy drink (9 x 18, wider with its wings)."""
    f = Canvas(31 if wings else 11, 20)
    x = 11 if wings else 1
    if wings:
        for s in (-1, 1):
            cx = x + 4 + s * 5
            f.poly([(cx, 8), (cx + s * 9, 2), (cx + s * 8, 7), (cx + s * 6, 8), (cx + s * 7, 11), (cx + s * 3, 11)], "white")
    f.rect((x, 2, x + 8, 18), "can_silver")
    f.rect((x, 2, x + 4, 9), "can_blue"); f.rect((x + 4, 10, x + 8, 18), "can_blue")
    f.rect((x + 3, 8, x + 5, 11), "red"); f.px((x + 4, 7), "yellow")
    f.line([(x, 1), (x + 8, 1)], "steel"); f.line([(x + 1, 3), (x + 1, 17)], "white")
    return f.done()


@lru_cache(maxsize=None)
def heel(color="red"):
    """A high heel, toe to the right (17 x 15)."""
    f = Canvas(19, 17)
    f.poly([(2, 3), (6, 2), (9, 8), (16, 10), (17, 13), (9, 13), (5, 9), (4, 14), (2, 14)], color)
    f.line([(3, 4), (6, 4)], color + "_hi"); f.line([(10, 10), (15, 11)], color + "_hi")
    f.px((14, 11), "white")
    return f.done()


def crown(p, x, y, color="gold"):
    """A small crown, 11 x 8, its top left at (x, y)."""
    p.poly([(x, y + 7), (x, y + 2), (x + 3, y + 5), (x + 5, y), (x + 7, y + 5), (x + 10, y + 2), (x + 10, y + 7)], color)
    p.line([(x, y + 7), (x + 10, y + 7)], color + "_sh")
    p.px((x + 5, y + 3), "red")


def wig_icon(p, x, y, color, style=0):
    """A wig on a foam head, 12 x 13, its top left at (x, y)."""
    p.rect((x + 3, y + 4, x + 8, y + 11), "foam"); p.rect((x + 5, y + 11, x + 6, y + 12), "foam_sh")
    p.rect((x + 2, y + 1, x + 9, y + 4), color); p.rect((x + 3, y, x + 8, y), color)
    if style == 0:                                                       # long
        p.rect((x + 1, y + 2, x + 2, y + 11), color); p.rect((x + 9, y + 2, x + 10, y + 11), color)
    elif style == 1:                                                     # a bob
        p.rect((x + 1, y + 2, x + 2, y + 7), color); p.rect((x + 9, y + 2, x + 10, y + 7), color)
    else:                                                                # tails
        p.rect((x, y + 2, x + 1, y + 9), color); p.rect((x + 10, y + 2, x + 11, y + 9), color)
        p.px((x + 2, y + 3), color); p.px((x + 9, y + 3), color)


__all__ += ["glue_gun", "scissors", "can", "heel", "crown", "wig_icon"]


def phone(p, title, color="bar"):
    """A phone's screen filling the picture's middle: returns its box, to draw in."""
    x0, y0, x1, y1 = 24, 0, 76, p.h - 3
    p.rbox((x0, y0, x1, y1), "black", "ink", 4)
    p.rect((x0 + 3, y0 + 3, x1 - 3, y1 - 3), color)
    p.rect((46, 1, 54, 2), "grey_sh")
    if title:
        p.silk((50, 6), title, "dim", anchor="ma")
    return x0 + 3, y0 + 3, x1 - 3, y1 - 3


def round_btn(p, x, y, color, kind):
    """A call's round button, 11 across: "yes" picks up, "no" hangs up."""
    p.ell((x - 5, y - 5, x + 5, y + 5), color)
    p.d.ellipse((x - 5, y - 5, x + 5, y + 5), outline=INK)
    if kind == "no":
        p.line([(x - 3, y), (x + 3, y)], "white", w=2)
    else:
        p.line([(x - 2, y - 2), (x - 2, y + 2), (x + 2, y + 2)], "white", w=2)


def bubble(p, box, s, fill, fg="ink", right=False):
    """A message in a text thread."""
    x0, y0, x1, y1 = box
    p.rbox(box, fill, None, 3)
    p.poly([(x1 - 2, y1 - 3), (x1 + 3, y1), (x1 - 5, y1)] if right else [(x0 + 2, y1 - 3), (x0 - 3, y1), (x0 + 5, y1)], fill)
    p.silk(((x0 + x1) // 2 + 1, (y0 + y1) // 2 - 2), s, fg, anchor="ma")


__all__ += ["phone", "round_btn", "bubble"]
