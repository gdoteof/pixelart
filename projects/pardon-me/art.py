"""Sprites that more than one section's gags use: the pardoned turkey, the Nobel medal, the UN
escalator, hand-held markers and signs. Each is a cached RGBA image outlined in ink.
(The OUT OF ORDER sign is `sign_sprite("OUT OF ORDER")`, set in front of the escalator.)

    uv run python projects/pardon-me/art.py     # -> build/art.png, a sheet of them all
"""
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, SILK, Canvas, outlined, text_width

TURKEY = {"body": (122, 78, 50), "body_sh": (88, 54, 38), "body_hi": (160, 108, 70),
          "tail": ((176, 96, 44), (214, 150, 70), (140, 70, 40), (226, 186, 110)),
          "wattle": (214, 40, 48), "beak": (246, 196, 70), "roast": (196, 120, 52), "roast_hi": (236, 172, 92),
          "roast_sh": (150, 84, 36), "plate": (236, 236, 240), "plate_sh": (190, 194, 206)}


@lru_cache(maxsize=None)
def turkey(hair=None, facing=1, gobble=False):
    """A cartoon turkey, about 30x28, facing right; `hair` is None, "trump" (the swoop) or "bibi" (grey).
    `gobble` opens the beak."""
    s = Canvas(34, 32)
    T = TURKEY
    for i, (a0, a1) in enumerate(((150, 200), (125, 165), (100, 140), (75, 115), (55, 90))):
        col = T["tail"][i % 4]
        s.d.pieslice((0, 1, 28, 29), -a1, -a0, fill=col + (255,))          # the fanned tail
    s.ell((6, 11, 24, 28), T["body"])
    s.ell((7, 18, 22, 28), T["body_sh"])
    s.ell((9, 12, 18, 19), T["body_hi"])
    s.rect((19, 6, 23, 18), T["body"])                                     # neck
    s.ell((19, 2, 28, 11), T["body"])                                      # head
    s.px((25, 5), "eye")
    if gobble:
        s.poly([(28, 6), (32, 5), (31, 7), (28, 8)], T["beak"])
        s.poly([(28, 8), (31, 9), (28, 10)], T["beak"])
    else:
        s.poly([(28, 6), (32, 8), (28, 9)], T["beak"])
    s.rect((27, 9, 28, 14), T["wattle"])                                   # wattle
    s.px((26, 13), T["wattle"])
    s.line([(12, 28), (12, 31)], T["beak"]); s.line([(17, 28), (17, 31)], T["beak"])
    s.line([(10, 31), (13, 31)], T["beak"]); s.line([(15, 31), (18, 31)], T["beak"])
    if hair == "trump":
        s.poly([(18, 3), (22, 0), (29, 0), (33, 3), (30, 4), (26, 3), (21, 5)], "thair")
        s.line([(21, 1), (29, 1)], "thair_hi")
    elif hair == "bibi":
        s.poly([(19, 3), (22, 1), (26, 1), (24, 3), (21, 6)], "bhair")
        s.rect((19, 4, 20, 8), "bhair")
    img = s.done()
    return img.transpose(Image.FLIP_LEFT_RIGHT) if facing < 0 else img


@lru_cache(maxsize=None)
def roast_turkey(hair=None):
    """The turkey after the basting: golden on a platter, drumsticks up, with (or without) someone's hair."""
    T = TURKEY
    s = Canvas(40, 26)
    s.ell((0, 16, 39, 25), T["plate"])
    s.ell((3, 18, 36, 24), T["plate_sh"])
    s.ell((5, 5, 33, 22), T["roast"])
    s.ell((8, 6, 26, 15), T["roast_hi"])
    s.ell((10, 15, 30, 22), T["roast_sh"])
    for x in (6, 30):                                                      # drumsticks with paper frills
        s.ell((x - 3, 6, x + 4, 14), T["roast"])
        s.rect((x, 2, x + 1, 6), "white")
        s.pxs([(x - 1, 2), (x + 2, 2)], "white")
    if hair == "trump":
        s.poly([(12, 6), (17, 1), (27, 1), (32, 5), (27, 5), (22, 4), (16, 7)], "thair")
        s.line([(17, 2), (26, 2)], "thair_hi")
    elif hair == "bibi":
        s.poly([(13, 6), (17, 3), (24, 3), (21, 5), (16, 7)], "bhair")
    return s.done()


@lru_cache(maxsize=None)
def nobel_medal(ribbon=True):
    """A gold medal (a profile in relief) on a ribbon; about 14x22."""
    s = Canvas(16, 24)
    if ribbon:
        s.poly([(2, 0), (6, 0), (8, 9), (6, 10)], "blue")
        s.poly([(13, 0), (9, 0), (7, 9), (9, 10)], (60, 90, 170))
    s.ell((1, 8, 14, 21), "gold_sh")
    s.ell((2, 9, 13, 20), "gold")
    s.ell((5, 11, 10, 17), "gold_sh")                                      # the profile
    s.px((10, 13), "gold_sh")
    s.px((4, 10), "gold_hi"); s.px((3, 12), "gold_hi")
    return s.done()


@lru_cache(maxsize=None)
def escalator(width=60, rise=34):
    """The UN's escalator in side view, going up to the right: the steel truss, the steps, a glass
    balustrade and the black handrail. About width x (rise + 22); its foot is at the bottom-left."""
    w, h = width + 2, rise + 24
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fl, top = h - 4, h - 4 - rise                        # tread level at the bottom and top landings
    xa, xb = 12, width - 12                              # where the incline starts and ends
    rail = 13                                            # handrail height over the treads
    glass = (150, 200, 220, 150)
    d.polygon([(2, fl - rail), (xa, fl - rail), (xb, top - rail), (width - 2, top - rail), (width - 2, top),
               (xb, top), (xa, fl), (2, fl)], fill=glass)
    d.polygon([(0, fl), (xa, fl), (xb, top), (width, top), (width, top + 5), (xb + 2, top + 5), (xa + 2, fl + 3),
               (0, fl + 3)], fill=C["steel_sh"] + (255,))
    n = 9
    for k in range(n):                                   # the steps: a sawtooth up the incline
        x = xa + (xb - xa) * k / n
        y = fl - rise * k / n
        sx, sy = (xb - xa) / n, rise / n
        d.polygon([(x, y), (x, y - sy), (x + sx, y - sy), (x + sx, y)], fill=C["steel"] + (255,))
        d.line([(x, y - sy), (x + sx, y - sy)], fill=(232, 234, 242, 255))
    d.line([(0, fl), (xa, fl)], fill=(232, 234, 242, 255))
    d.line([(xb, top), (width, top)], fill=(232, 234, 242, 255))
    pts = [(2, fl - rail), (xa, fl - rail), (xb, top - rail), (width - 2, top - rail)]
    d.line(pts, fill=INK + (255,), width=3)               # handrail, curling over at both ends
    d.line(pts, fill=(40, 40, 48, 255), width=1)
    d.arc((0, fl - rail, 5, fl - rail + 5), 90, 270, fill=INK + (255,), width=2)
    d.arc((width - 5, top - rail, width, top - rail + 5), 270, 90, fill=INK + (255,), width=2)
    return outlined(img)


@lru_cache(maxsize=None)
def sign_sprite(text, color="red", fg="white", stand=True):
    """A small printed sign (white on red, say) on a little stand."""
    w = text_width(text, SILK) + 8
    s = Canvas(w, 16 if stand else 11)
    s.rect((0, 0, w - 1, 9), color)
    s.text((4, 0), text, fg)
    if stand:
        s.rect((w // 2 - 1, 10, w // 2, 14), "steel_sh")
        s.rect((w // 2 - 4, 14, w // 2 + 3, 15), "steel_sh")
    return s.done()


@lru_cache(maxsize=None)
def marker(color="mk_red", capped=False, angle=0):
    """A hand-held marker pen, about 3x9, nib up; `angle` in degrees."""
    s = Canvas(5, 12)
    s.rect((1, 3, 3, 10), "white")
    s.rect((1, 7, 3, 8), color)
    if capped:
        s.rect((1, 1, 3, 4), color)
    else:
        s.rect((2, 1, 2, 2), color)
        s.rect((1, 2, 3, 3), "steel_sh")
    img = s.done()
    return img.rotate(angle, resample=Image.NEAREST, expand=True) if angle else img


if __name__ == "__main__":
    from engine import ROOT
    items = [turkey(), turkey("trump"), turkey("bibi", gobble=True), roast_turkey("trump"), nobel_medal(),
             escalator(), sign_sprite("OUT OF ORDER"), sign_sprite("PLEASE TAKE THE STAIRS", "blue"), marker(),
             marker("mk_black", True, 30)]
    sheet = Image.new("RGB", (sum(i.width + 6 for i in items) + 6, 70), (196, 150, 70))
    x = 6
    for i in items:
        sheet.paste(i, (x, 64 - i.height), i)
        x += i.width + 6
    out = ROOT / "build" / "art.png"
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)
    print(out)
