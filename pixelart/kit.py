"""A video's palette and ink colour, bound onto the drawing primitives.

A video names its colours once and then draws with the names. Its engine.py makes one Kit and re-exports
the bound helpers under their plain names, so the rest of the project imports them from there:

    KIT = Kit(C, INK)                                    # C = {"ink": INK, "bg": ..., "text": ..., ...}
    col, rgba, silk, press, Canvas = KIT.col, KIT.rgba, KIT.silk, KIT.press, KIT.Canvas

    silk(img, (4, 4), "LIVE", "red")                     # Silkscreen text; a colour is a name or an RGB tuple
    f = Canvas(24, 12)                                   # a sprite canvas: draw, then done() outlines it in ink
    f.rect((2, 2, 21, 9), "skin")
    sprite = f.done()

    p = Pic("paper", 100, 54)                            # an opaque picture for a screen in the frame
    p.header("MATCH HISTORY", "blue")
    p.silk((6, 20), "BARREL")
    screen.paste(p.img, (x, y))

The palette needs "text" (the default for text on a picture), "ink" (the default on a sprite canvas) and
"bg" (the default background of a picture).
"""
from PIL import Image, ImageDraw

from pixelart import fx, pixel, sprites

PRESS = pixel.font(size=8)
PRESS16 = pixel.font(size=16)
SILK = pixel.font("Silkscreen-Regular.ttf", 8)
SILK16 = pixel.font("Silkscreen-Regular.ttf", 16)


def silk_w(s, fnt=SILK):
    return pixel.text_width(s, fnt)


class Kit:
    def __init__(self, pal, ink):
        self.pal, self.ink = pal, ink
        kit = self

        class Canvas(sprites.Canvas):
            """A sprite canvas drawing with this video's palette names; `done()` outlines in ink."""

            def __init__(self, w, h):
                super().__init__(w, h, pal, SILK)

            def silk(self, xy, s, col_="ink", anchor="la", fnt=SILK):
                kit.silk(self.img, xy, s, col_, anchor, fnt)

            def done(self, outline=ink):
                return super().done(outline)

        class Pic(Canvas):
            """An opaque picture drawn with the palette's names, for a screen or a window in the frame: `img`
            is the picture. A project that shows many of one size subclasses it with that size."""

            def __init__(self, bg="bg", w=100, h=60):
                super().__init__(w, h)
                self.w, self.h = w, h
                self.rect((0, 0, w, h), bg)

            def put(self, spr, x, y, anchor="mm"):
                sprites.paste(self.img, spr, int(round(x)), int(round(y)), anchor)

            def press(self, xy, s, col_="ink", anchor="la", fnt=PRESS, shadow=None):
                x, y = xy
                if shadow:
                    self.d.text((x + 1, y + 1), s, font=fnt, fill=self.c(shadow), anchor=anchor)
                self.d.text((x, y), s, font=fnt, fill=self.c(col_), anchor=anchor)

            def big(self, xy, s, top="gold", bottom="orange", anchor="ma", fnt=PRESS16, scale=1.0, outline="black"):
                fx.big_text(self.img, xy, s, fnt, kit.col(top), kit.col(bottom), kit.col(outline), anchor=anchor,
                            scale=scale, ink=ink)

            def pop(self, xy, s, age, top="gold", bottom="orange", fnt=PRESS16, anchor="mm"):
                fx.pop_text(self.img, xy[0], xy[1], s, age, fnt, kit.col(top), kit.col(bottom), kit.col("black"),
                            anchor=anchor, ink=ink)

            def grad(self, box, top, bottom, steps=4):
                rgb = self.img.convert("RGB")
                kit.vgrad(rgb, box, top, bottom, steps=steps)
                self.img.paste(rgb)

            def header(self, s, bg="blue", fg="white", h=11, fnt=SILK):
                """A title bar across the top."""
                self.rect((0, 0, self.w, h - 1), bg)
                self.silk((self.w // 2, (h - 5) // 2), s, fg, anchor="ma", fnt=fnt)

            def box(self, box, fill, outline="ink"):
                self.d.rectangle(box, fill=self.c(fill), outline=self.c(outline) if outline else None)

            def rbox(self, box, fill, outline="ink", r=3):
                self.d.rounded_rectangle(box, r, fill=self.c(fill), outline=self.c(outline) if outline else None)

            def stamp(self, x, y, s, age=1.0, color="red", angle=-12, fnt=PRESS):
                fx.stamp(self.img, x, y, s, fnt, kit.col(color), angle, age)

            def tag(self, xy, s, bg="ink", fg="white", anchor="la"):
                """Small text on a plate; returns the plate's right edge."""
                w = silk_w(s) + 5
                x, y = xy
                x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
                self.rect((x, y, x + w, y + 8), bg)
                self.silk((x + 3, y + 2), s, fg)
                return x + w

            def tick(self, x, y, col_="green"):
                self.line([(x, y + 3), (x + 2, y + 5), (x + 6, y)], col_, w=2)

            def cross(self, x, y, col_="red", r=3):
                self.line([(x - r, y - r), (x + r, y + r)], col_, w=2)
                self.line([(x - r, y + r), (x + r, y - r)], col_, w=2)

            def heart(self, x, y, col_="red"):
                self.rect((x, y, x + 1, y + 1), col_); self.rect((x + 3, y, x + 4, y + 1), col_)
                self.rect((x, y + 1, x + 4, y + 2), col_); self.rect((x + 1, y + 3, x + 3, y + 3), col_)
                self.px((x + 2, y + 4), col_)

            def lines(self, box, n, col_="ink", gap=5, short=()):
                """Ruled lines of pretend text in a box; the rows in `short` stop early."""
                x0, y0, x1, _ = box
                for i in range(n):
                    self.line([(x0, y0 + i * gap), (x1 - (12 if i in short else 0), y0 + i * gap)], col_)

        self.Canvas, self.Pic = Canvas, Pic

    def col(self, c):
        return self.pal[c] if isinstance(c, str) else tuple(c)[:3]

    def rgba(self, c, a=255):
        return self.col(c) + (a,)

    def silk(self, img, xy, s, fill="text", anchor="la", fnt=SILK):
        """Silkscreen text with its glyph tops at y (the glyphs sit 4 px down their box, 8 px at double size)."""
        x, y = xy
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        d.text((x, y - fnt.size // 2), s, font=fnt, fill=self.rgba(fill) if img.mode == "RGBA" else self.col(fill),
               anchor=anchor)

    def press(self, img, xy, s, fill="text", anchor="la", fnt=PRESS, shadow=None):
        """Press Start text; `shadow` is a colour for a 1 px drop shadow."""
        pixel.text(img, xy, s, fnt, self.col(fill), self.col(shadow) if shadow else None, anchor)

    def outline_text(self, img, xy, s, fnt=PRESS, fill="text", outline=None, anchor="la"):
        pixel.outline_text(img, xy, s, fnt, self.col(fill), self.col(self.ink if outline is None else outline), anchor)

    def picture(self, w, h, bg="bg"):
        """A flat RGB picture and its ImageDraw."""
        img = Image.new("RGB", (w, h), self.col(bg))
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        return img, d

    def vgrad(self, img, box, top, bottom, steps=None, phase=0, soft=0.3):
        return pixel.vgrad(img, box, self.col(top), self.col(bottom), steps, phase, soft)

    def blend(self, img, m, color, alpha=0.3):
        return pixel.blend(img, m, self.col(color), alpha)
