"""The Oval Office, the way the press pool sees it: the two armchairs in front of the fireplace, Bibi on
the left and Trump on the right, Washington's portrait over the mantel, gold on everything.

World layout (320x180):
    the portrait over the fireplace   PORTRAIT = (141, 18, 179, 78); its picture is PICTURE
    the mantel shelf                  y 84-88, x 126-194; the firebox FIREBOX
    the side portraits                SIDE_L / SIDE_R (above the two heads)
    the doors                         DOOR_L / DOOR_R at the edges (Obama comes in on the left)
    the chairs                        figure canvases at SEAT_L / SEAT_R (top-left), feet near y 152
    the rug                           y 132-180
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from characters import FW
from engine import C, H, W, Canvas, dither_rect, rnd, vgrad

PORTRAIT = (141, 18, 179, 78)
PICTURE = (145, 22, 175, 74)                 # inside the frame: what a gag may paint over
FIREBOX = (146, 100, 174, 129)
SIDE_L, SIDE_R = (88, 14, 120, 54), (200, 14, 232, 54)
SMALL_L, SMALL_R = (58, 12, 80, 40), (240, 12, 262, 40)
DOOR_L, DOOR_R = (4, 34, 40, 130), (280, 34, 316, 130)
SEAT_L, SEAT_R = (50, 44), (186, 44)          # where the figure canvases go (Bibi faces right, Trump left)
FLOOR_Y = 130
TABLE = (148, 132, 172, 146)                  # the little table between the chairs


def _box(d, box, col):
    d.rectangle(box, fill=C[col] if isinstance(col, str) else col)


def frame(d, box, inner=None):
    """A gilded frame: gold with a dark bevel inside and a highlight on top."""
    x0, y0, x1, y1 = box
    _box(d, (x0 - 1, y0 - 1, x1 + 1, y1 + 1), "ink")
    _box(d, box, "gold")
    d.line([(x0, y0), (x1, y0)], fill=C["gold_hi"]); d.line([(x0, y0), (x0, y1)], fill=C["gold_hi"])
    d.line([(x0, y1), (x1, y1)], fill=C["gold_sh"]); d.line([(x1, y0), (x1, y1)], fill=C["gold_sh"])
    for x in range(x0 + 2, x1 - 1, 3):                                   # a beaded edge
        d.point((x, y0 + 1), fill=C["gold_sh"]); d.point((x, y1 - 1), fill=C["gold_dk"])
    if inner:
        ix0, iy0, ix1, iy1 = inner
        _box(d, (ix0 - 1, iy0 - 1, ix1 + 1, iy1 + 1), "gold_dk")


def washington(d, box):
    """Peale's porthole portrait: Washington in a painted stone oval."""
    x0, y0, x1, y1 = box
    _box(d, box, (78, 82, 74))
    cx = (x0 + x1) // 2
    d.ellipse((x0 + 2, y0 + 2, x1 - 2, y1 - 12), fill=C["marble_sh"])           # the stone oval
    d.ellipse((x0 + 4, y0 + 4, x1 - 4, y1 - 14), fill=(52, 46, 40))
    d.polygon([(cx - 10, y1 - 15), (cx - 8, y0 + 30), (cx + 8, y0 + 30), (cx + 10, y1 - 15)], fill=C["gw_coat"])
    d.polygon([(cx - 2, y0 + 26), (cx + 2, y0 + 26), (cx + 1, y0 + 34), (cx - 1, y0 + 34)], fill=C["white"])
    d.ellipse((cx - 7, y0 + 9, cx + 6, y0 + 22), fill=C["gw_hair"])             # powdered hair
    d.ellipse((cx - 4, y0 + 11, cx + 5, y0 + 27), fill=C["gw_skin"])
    d.point((cx - 1, y0 + 17), fill=C["ink"]); d.point((cx + 3, y0 + 17), fill=C["ink"])
    d.line([(cx, y0 + 23), (cx + 2, y0 + 23)], fill=(170, 110, 100))
    d.rectangle((cx - 6, y0 + 12, cx - 5, y0 + 20), fill=C["gw_hair"])
    _box(d, (x0 + 3, y1 - 11, x1 - 3, y1 - 3), "marble_sh")                    # the stone sill
    d.line([(x0 + 6, y1 - 7), (x1 - 6, y1 - 7)], fill=C["marble_vein"])


def old_portrait(d, box, hair, coat=(34, 30, 36)):
    """A president in oils, in a gilded frame: just enough to read as one."""
    x0, y0, x1, y1 = box
    frame(d, box)
    ix0, iy0, ix1, iy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 3
    _box(d, (ix0, iy0, ix1, iy1), (64, 56, 50))
    cx = (ix0 + ix1) // 2
    d.polygon([(ix0 + 2, iy1), (cx - 6, iy1 - 14), (cx + 6, iy1 - 14), (ix1 - 2, iy1)], fill=coat)
    d.ellipse((cx - 5, iy1 - 26, cx + 5, iy1 - 13), fill=(222, 186, 160))
    d.ellipse((cx - 6, iy1 - 28, cx + 6, iy1 - 21), fill=hair)
    d.line([(cx - 1, iy1 - 14), (cx + 1, iy1 - 14)], fill=C["white"])


def door(d, box):
    x0, y0, x1, y1 = box
    _box(d, (x0 - 3, y0 - 3, x1 + 3, y1), "trim_sh")                           # the casing
    _box(d, (x0 - 2, y0 - 2, x1 + 2, y1), "trim")
    _box(d, box, "trim")
    d.line([(x0, y0), (x0, y1)], fill=C["trim_sh"]); d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=C["trim_sh"])
    for px0, px1 in ((x0 + 3, (x0 + x1) // 2 - 3), ((x0 + x1) // 2 + 3, x1 - 3)):
        for py0, py1 in ((y0 + 4, y0 + 30), (y0 + 34, y0 + 70), (y0 + 74, y1 - 6)):
            d.rectangle((px0, py0, px1, py1), outline=C["trim_sh"])
            d.line([(px0 + 1, py1 - 1), (px1 - 1, py1 - 1)], fill=C["wall_hi"])
    mx = (x0 + x1) // 2
    d.point((mx - 2, y0 + 56), fill=C["gold"]); d.point((mx + 2, y0 + 56), fill=C["gold"])
    # the pediment, with a gilded shell
    d.polygon([(x0 - 5, y0 - 3), (mx, y0 - 13), (x1 + 5, y0 - 3)], fill=C["trim"])
    d.line([(x0 - 5, y0 - 3), (mx, y0 - 13), (x1 + 5, y0 - 3)], fill=C["trim_sh"])
    d.line([(x0 - 5, y0 - 3), (x1 + 5, y0 - 3)], fill=C["trim_sh"])
    d.ellipse((mx - 4, y0 - 11, mx + 4, y0 - 4), fill=C["gold"])
    d.line([(mx, y0 - 10), (mx, y0 - 5)], fill=C["gold_sh"])
    d.line([(mx - 3, y0 - 8), (mx + 3, y0 - 8)], fill=C["gold_sh"])


def urn(d, x, y, h=14):
    """A gilded urn on the mantel, its foot at (x, y)."""
    w = h // 2
    d.rectangle((x - 2, y - 2, x + 2, y), fill=C["gold_sh"])
    d.ellipse((x - w // 2 - 1, y - h + 3, x + w // 2 + 1, y - 2), fill=C["gold"])
    d.rectangle((x - 2, y - h, x + 2, y - h + 4), fill=C["gold"])
    d.line([(x - w // 2, y - h + 1), (x + w // 2, y - h + 1)], fill=C["gold_sh"])
    d.line([(x - 1, y - h + 5), (x - 1, y - 4)], fill=C["gold_hi"])
    d.point((x - w // 2 - 2, y - h + 6), fill=C["gold_sh"]); d.point((x + w // 2 + 2, y - h + 6), fill=C["gold_sh"])


def eagle(d, x, y):
    """A small gilded eagle, wings up, standing at (x, y)."""
    d.polygon([(x - 6, y - 8), (x - 1, y - 4), (x, y - 7), (x + 1, y - 4), (x + 6, y - 8), (x + 3, y - 2),
               (x + 1, y), (x - 1, y), (x - 3, y - 2)], fill=C["gold"])
    d.point((x, y - 6), fill=C["gold_hi"]); d.line([(x - 5, y - 7), (x - 2, y - 4)], fill=C["gold_sh"])


def fireplace(d):
    # the marble surround: two pilasters, the frieze and the shelf
    _box(d, (128, 88, 192, FLOOR_Y), "marble")
    _box(d, (128, 88, 137, FLOOR_Y), "marble_sh"); _box(d, (183, 88, 192, FLOOR_Y), "marble_sh")
    d.line([(130, 90), (130, FLOOR_Y)], fill=C["marble"]); d.line([(185, 90), (185, FLOOR_Y)], fill=C["marble"])
    _box(d, (138, 89, 182, 98), "marble")
    d.ellipse((155, 90, 165, 97), fill=C["gold"]); d.point((160, 93), fill=C["gold_hi"])          # the medallion
    d.line([(139, 93), (153, 93)], fill=C["gold_sh"]); d.line([(167, 93), (181, 93)], fill=C["gold_sh"])
    d.line([(136, 98), (184, 99)], fill=C["marble_vein"]); d.line([(140, 120), (136, 126)], fill=C["marble_vein"])
    _box(d, (125, 84, 195, 88), "marble"); d.line([(125, 88), (195, 88)], fill=C["marble_sh"])
    d.line([(125, 84), (195, 84)], fill=C["gold"])
    # the firebox, its brick back, and the brass fender
    _box(d, FIREBOX, "firebox")
    for y in range(103, 126, 4):
        d.line([(149, y), (171, y)], fill=C["brick_sh"])
    d.polygon([(146, 100), (174, 100), (168, 106), (152, 106)], fill=(22, 16, 18))
    _box(d, (143, 126, 177, 129), "gold_sh"); d.line([(143, 126), (177, 126)], fill=C["gold"])
    # the mantel shelf's gold
    urn(d, 131, 83, 15); urn(d, 189, 83, 15)
    eagle(d, 137, 83); eagle(d, 183, 83)
    for x in (147, 173):                                                    # candlesticks
        d.rectangle((x - 1, 76, x + 1, 83), fill=C["gold"]); d.rectangle((x - 2, 82, x + 2, 83), fill=C["gold_sh"])
        d.point((x, 74), fill=C["white"]); d.point((x, 75), fill=C["white"])


def rug(img):
    """Reagan's sunburst rug: cream rays from a sun below the frame, a gold border."""
    d = ImageDraw.Draw(img)
    _box(d, (0, FLOOR_Y, W, H), "floor")
    for x in range(-8, W, 22):
        d.line([(x, FLOOR_Y), (x + 6, FLOOR_Y + 2)], fill=C["floor_sh"])
    rug_top = FLOOR_Y + 3
    rays = Image.new("RGB", (W, H - rug_top), C["rug"])                 # the rays, clipped to the rug
    r = ImageDraw.Draw(rays)
    sx, sy = 160, 250 - rug_top
    for k in range(-14, 15):
        a, b = math.radians(90 + k * 6.0), math.radians(93 + k * 6.0)
        r.polygon([(sx, sy), (sx + 400 * math.cos(a), sy - 400 * math.sin(a)),
                   (sx + 400 * math.cos(b), sy - 400 * math.sin(b))], fill=C["rug_sh"])
    img.paste(rays, (0, rug_top))
    _box(d, (0, rug_top, W, rug_top + 3), "rug_dk")
    d.line([(0, rug_top + 1), (W, rug_top + 1)], fill=C["gold"])


@lru_cache(maxsize=1)
def backdrop():
    """The empty room (RGB, 320x180): the walls, the fireplace, the portraits, the doors and the rug."""
    img = Image.new("RGB", (W, H), C["wall"])
    vgrad(img, (0, 0, W, FLOOR_Y), "wall_hi", "wall", steps=6)
    for x0, x1 in ((0, 30), (290, W)):                                      # the wall curves away at the sides
        dither_rect(img, (x0, 0, x1, FLOOR_Y), C["wall_sh"], density=0.5, blend=0.6)
    d = ImageDraw.Draw(img)
    # crown moulding and baseboard
    _box(d, (0, 0, W, 7), "trim"); d.line([(0, 7), (W, 7)], fill=C["trim_sh"])
    for x in range(0, W, 3):
        d.point((x, 5), fill=C["trim_sh"])
    d.line([(0, 8), (W, 8)], fill=C["gold"])
    _box(d, (0, FLOOR_Y - 5, W, FLOOR_Y), "trim"); d.line([(0, FLOOR_Y - 5), (W, FLOOR_Y - 5)], fill=C["trim_sh"])
    # doors at the edges, portraits stacked the way the gold-era Oval Office has them
    door(d, DOOR_L); door(d, DOOR_R)
    old_portrait(d, SIDE_L, (60, 40, 34)); old_portrait(d, SIDE_R, (236, 236, 240))
    old_portrait(d, SMALL_L, (200, 200, 206)); old_portrait(d, SMALL_R, (140, 96, 60))
    for x in (54, 262):                                                     # gilded sconces
        d.rectangle((x - 1, 66, x + 1, 74), fill=C["gold"]); d.ellipse((x - 3, 60, x + 3, 66), fill=C["fire_hi"])
        d.point((x, 63), fill=C["white"])
    fireplace(d)
    frame(d, PORTRAIT, inner=PICTURE)
    washington(d, PICTURE)
    eagle(d, 160, 16)
    rug(img)
    return img


def fire(img, f):
    """The fire in the grate at frame f: low flames that flicker every couple of frames."""
    d = ImageDraw.Draw(img)
    k = f // 2
    d.rectangle((150, 124, 170, 126), fill=C["wood_sh"])
    for i, x in enumerate(range(151, 170, 3)):
        h = 4 + int(rnd("fire", k, i) * 6)
        sway = int(rnd("sway", k, i) * 3) - 1
        d.polygon([(x - 2, 125), (x + sway, 125 - h), (x + 2, 125)], fill=C["fire_red"])
        d.polygon([(x - 1, 125), (x + sway, 127 - h), (x + 1, 125)], fill=C["fire"])
        if h > 7:
            d.point((x + sway, 128 - h), fill=C["fire_hi"])
    d.line([(150, 125), (170, 125)], fill=C["fire_hi"])


@lru_cache(maxsize=4)
def table_sprite():
    """The little gilded table between the chairs, where the gifts go."""
    f = Canvas(30, 18)
    f.ell((0, 0, 29, 6), "marble"); f.line([(2, 3), (27, 3)], "marble_sh")
    f.rect((3, 6, 26, 8), "gold"); f.line([(4, 7), (25, 7)], "gold_sh")
    for x in (5, 24):
        f.line([(x, 8), (x - 1 if x < 15 else x + 1, 17)], "gold", w=2)
    return f.done()


if __name__ == "__main__":
    from characters import chair, figure
    from engine import ROOT, scaled
    img = backdrop().copy()
    fire(img, 0)
    t = table_sprite()
    img.paste(t, (145, 132), t)
    for (x, y), who, legs, arms, facing, e in ((SEAT_L, "bibi", "together", "lap", 1, dict(mouth="smirk")),
                                               (SEAT_R, "trump", "spread", "between", -1, dict(mouth="pout", lean=2, bob=2))):
        ch = chair(facing)
        img.paste(ch, (x, y), ch)
        fig, _ = figure(who, legs, arms, facing=facing, **e)
        img.paste(fig, (x, y), fig)
    out = ROOT / "build" / "office.png"
    scaled(img, 4).save(out)
    print(out, FW)
