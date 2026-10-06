"""A video's palette and ink colour, bound onto the drawing primitives.

A video names its colours once and then draws with the names. Its engine.py makes one Kit and re-exports
the bound helpers under their plain names, so the rest of the project imports them from there:

    KIT = Kit(C, INK)                                    # C = {"ink": INK, "bg": ..., "text": ..., ...}
    col, rgba, silk, press, Canvas = KIT.col, KIT.rgba, KIT.silk, KIT.press, KIT.Canvas

    silk(img, (4, 4), "LIVE", "red")                     # Silkscreen text; a colour is a name or an RGB tuple
    f = Canvas(24, 12)                                   # a sprite canvas: draw, then done() outlines it in ink
    f.rect((2, 2, 21, 9), "skin")
    sprite = f.done()

The palette needs "text" (the default for text on a picture), "ink" (the default on a sprite canvas) and
"bg" (the default background of a picture).
"""
from PIL import Image, ImageDraw

from pixelart import pixel, sprites

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

        self.Canvas = Canvas

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
