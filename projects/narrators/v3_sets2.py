"""Sets and sprites for the back half of Verse 3 (gags_v3.py).

Space (God twice for Universal, God's nap after making one planet, the seven worlds), the throne
room of the actual Crown, the study shelf of planet trophies, the Se7en desert and its box, the
steering wheel at ten and two, the grave pushing up daisies, and the savanna at dusk. Also the
action replay's tools: a VHS tear for the rewind and the pundit's telestrator pen.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import C, INK, PRESS, SILK, H, W, Canvas, blend, blend_poly, clamp, col, lerp, mask, outlined, rnd, vgrad
from pixelart import pixel
from props import crown, globe, sparkle
from sets import scene
from v3_sets import DASH, road_view


# --- planets ------------------------------------------------------------------------------------------

PLANETS = {   # (shadow, mid, light, accent)
    "blue": ((24, 50, 120), (40, 96, 184), (96, 160, 232), (206, 232, 252)),
    "frozen": ((120, 160, 206), (186, 216, 240), (240, 248, 255), (96, 140, 196)),
    "green": ((30, 92, 52), (62, 142, 70), (124, 194, 90), (246, 224, 96)),
    "sand": ((170, 104, 54), (214, 150, 80), (240, 196, 120), (150, 84, 50)),
    "lava": ((70, 30, 40), (120, 44, 44), (170, 70, 56), (255, 150, 50)),
    "gas": ((96, 60, 140), (150, 100, 190), (206, 160, 230), (250, 220, 250)),
}


def _pattern(kind, lon, lat):
    """Which of a planet's colours a point shows: 'base' (shaded) or 'accent'."""
    if kind == "blue":                                     # ocean swirls and foam
        return math.sin(lon * 3 + lat * 5) + 0.5 * math.sin(lon * 7 - lat * 3) > 1.05
    if kind == "frozen":                                   # cracks in the ice
        return abs(math.sin(lon * 4 + lat * 6) + 0.4 * math.sin(lon * 9)) < 0.14
    if kind == "green":                                    # flowers in the canopy
        return math.sin(lon * 11 + 1) * math.sin(lat * 13) > 0.86
    if kind == "sand":                                     # dunes
        return math.sin(lat * 10 + math.sin(lon * 3) * 2) > 0.7
    if kind == "lava":                                     # glowing rivers
        return abs(math.sin(lon * 3 + lat * 4) + 0.5 * math.sin(lon * 7)) < 0.2
    return math.sin(lat * 9) > 0.5                         # gas bands


@lru_cache(maxsize=256)
def planet(kind, r=9, phase=0):
    """A little planet, lit from the top left; `phase` (0-15) turns it. 'earth' is the trophy's globe."""
    if kind == "earth":
        return globe(r, phase)
    shadow, mid, light, accent = PLANETS[kind]
    n = 2 * r + 3
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    px = img.load()
    for y in range(n):
        for x in range(n):
            dx, dy = (x - r - 1) / (r + 0.5), (y - r - 1) / (r + 0.5)
            if dx * dx + dy * dy > 1:
                continue
            z = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
            lon = math.atan2(dx, z) + phase * math.pi / 8
            lat = math.asin(clamp(dy, -1, 1))
            light_ = -0.6 * dx - 0.6 * dy + 0.5 * z
            if _pattern(kind, lon, lat):
                c = accent
            else:
                c = light if light_ > 0.55 else mid if light_ > -0.25 else shadow
            px[x, y] = c + (255,)
    if r >= 5:
        px[r - r // 2, r - r // 2] = (255, 255, 255, 255)
    return outlined(img)


@lru_cache(maxsize=64)
def planet_trophy(kind, phase=0, r=9):
    """The battle's prize, but one of Sir David's: a gold cup on a plinth holding up a planet."""
    g = planet(kind, r, phase)
    w = max(g.width, 26)
    s = Canvas(w + 2, g.height + 26)
    cx = (w + 2) // 2
    top = g.height - 2
    s.poly([(cx - 8, top), (cx + 8, top), (cx + 5, top + 7), (cx - 5, top + 7)], "gold")
    s.line([(cx - 7, top + 1), (cx - 4, top + 6)], "gold_hi")
    s.line([(cx + 7, top + 1), (cx + 4, top + 6)], "gold_sh")
    s.rect((cx - 1, top + 7, cx + 1, top + 12), "gold_sh")
    s.rect((cx - 6, top + 13, cx + 6, top + 16), "gold")
    s.line([(cx - 6, top + 13), (cx + 6, top + 13)], "gold_hi")
    s.rect((cx - 9, top + 17, cx + 9, top + 22), "wood")
    s.line([(cx - 9, top + 22), (cx + 9, top + 22)], "wood_sh")
    s.rect((cx - 5, top + 18, cx + 5, top + 20), "gold_sh")
    img = s.done()
    img.alpha_composite(g, ((w + 2 - g.width) // 2, 0))
    return img


# --- space: God, twice; God's nap; the seven worlds ---------------------------------------------------

SPACE = {"top": (6, 6, 22), "bottom": (34, 20, 60), "neb": (130, 60, 170), "neb2": (50, 110, 180),
         "star": (240, 240, 255), "star2": (150, 150, 200), "cloud": (250, 250, 255), "cloud_sh": (206, 200, 236)}


@lru_cache(maxsize=1)
def space_static():
    img = Image.new("RGB", (W, H), SPACE["top"])
    vgrad(img, (0, 0, W, H), SPACE["top"], SPACE["bottom"], steps=5)
    for x, y, rx, ry, colr in ((60, 50, 90, 30, SPACE["neb"]), (250, 130, 110, 36, SPACE["neb2"]),
                               (210, 36, 70, 20, SPACE["neb"])):
        for j in range(3):                                           # nebulae, in flat steps
            k = 1 - j * 0.3
            blend(img, mask(lambda d: d.ellipse((x - rx * k, y - ry * k, x + rx * k, y + ry * k), fill=255)), colr,
                  0.07)
    d = ImageDraw.Draw(img)
    for k in range(150):
        d.point((int(rnd("star", k) * W), int(rnd("star-y", k) * H)),
                fill=SPACE["star"] if k % 4 == 0 else SPACE["star2"])
    return img


def space(c):
    img = space_static().copy()
    for k in range(12):                                              # twinkles
        if (c.t * 1.3 + rnd("tw", k)) % 1.0 < 0.15:
            sparkle(img, int(rnd("tw-x", k) * W), int(rnd("tw-y", k) * H), 1, SPACE["star"])
    return img


GOD_SEAT = (150, 122)                  # Morgan's feet, sitting on his cloud
scene("v3_space", shots={"gods": (160, 92, 6), "logo": (160, 86, 9), "cloud": (152, 104, 12),
                         "nap": (156, 110, 18), "mine": (160, 104, 9)},
      cast={"morgan": dict(x=GOD_SEAT[0], y=GOD_SEAT[1], facing=1, outfit="god", shadow=False)})(space)


@lru_cache(maxsize=None)
def cloud_seat(w=58, h=20):
    """A small cloud to sit (or nap) on."""
    s = Canvas(w, h)
    for k, r in enumerate((5, 7, 9, 7, 5)):
        cx = 7 + k * (w - 14) / 4
        s.ell((cx - r - 2, h - 3 - r * 1.5, cx + r + 2, h - 2), SPACE["cloud"])
    s.rect((4, h - 8, w - 5, h - 2), SPACE["cloud"])
    s.line([(6, h - 3), (w - 7, h - 3)], SPACE["cloud_sh"])
    s.line([(10, h - 5), (w - 12, h - 5)], SPACE["cloud_sh"])
    return s.done((150, 146, 190))


def arc_letters(ui, s, cx, cy, rx, ry, a0, a1, age, fnt=PRESS, top=C["gold_hi"], bottom=C["gold"], per=0.035):
    """`s` set along the front of an ellipse from angle a0 to a1 (radians, 0 = right, pi/2 = down), evenly
    spaced across, one letter after another from age 0: the studio-logo sweep."""
    from props import big_text
    n = len(s)
    x0, x1 = cx + math.cos(a0) * rx, cx + math.cos(a1) * rx
    for i, ch in enumerate(s):
        if age < i * per or ch == " ":
            continue
        x = lerp(x0, x1, i / max(1, n - 1))
        y = cy + ry * math.sqrt(max(0.0, 1 - ((x - cx) / rx) ** 2))
        big_text(ui, (int(x), int(y)), ch, fnt, top, bottom, anchor="mm")


# --- the throne room: the actual Crown ----------------------------------------------------------------

THRONE = {"wall": (110, 28, 44), "wall_sh": (84, 20, 36), "trim": (214, 170, 70), "trim_sh": (160, 118, 50),
          "floor": (72, 56, 66), "floor_hi": (96, 76, 88), "carpet": (176, 34, 48), "carpet_sh": (128, 24, 40),
          "throne": (226, 184, 80), "throne_sh": (170, 128, 52), "velvet": (120, 30, 90), "banner": (40, 50, 120),
          "banner_sh": (28, 34, 88), "window": (250, 230, 170), "steel": (220, 226, 236), "steel_sh": (150, 156, 176)}
KNEEL = (140, 156)                     # Sir David, kneeling on the carpet
CROWN_AT = (206, 108)                  # where the Crown hovers


@lru_cache(maxsize=1)
def throne_static():
    img = Image.new("RGB", (W, H), THRONE["wall"])
    d = ImageDraw.Draw(img)
    for x in range(0, W, 32):                                        # panelled wall
        d.rectangle((x + 4, 14, x + 27, 98), outline=THRONE["wall_sh"])
    for x in (36, 284):                                              # tall windows and their light
        d.rectangle((x - 10, 18, x + 10, 92), fill=THRONE["trim_sh"])
        d.rectangle((x - 8, 20, x + 8, 90), fill=THRONE["window"])
        d.line([(x, 20), (x, 90)], fill=THRONE["trim_sh"])
        d.line([(x - 8, 50), (x + 8, 50)], fill=THRONE["trim_sh"])
    for x in (98, 222):                                              # banners with a crown on each
        d.polygon([(x - 12, 10), (x + 12, 10), (x + 12, 70), (x, 62), (x - 12, 70)], fill=THRONE["banner"])
        d.line([(x - 12, 10), (x - 12, 69)], fill=THRONE["banner_sh"])
        cr = crown(10)
        img.paste(cr, (x - cr.width // 2, 30), cr)
    d.rectangle((0, 98, W, 104), fill=THRONE["trim"])                # gold trim, then the floor
    d.line([(0, 104), (W, 104)], fill=THRONE["trim_sh"])
    d.rectangle((0, 105, W, H), fill=THRONE["floor"])
    for y in (118, 136, 160):
        d.line([(0, y), (W, y)], fill=THRONE["floor_hi"])
    tx = 160                                                         # the throne, empty
    d.rectangle((tx - 16, 44, tx + 16, 100), fill=THRONE["throne"])
    d.ellipse((tx - 16, 34, tx + 16, 56), fill=THRONE["throne"])
    d.rectangle((tx - 11, 46, tx + 11, 88), fill=THRONE["velvet"])
    d.ellipse((tx - 11, 40, tx + 11, 54), fill=THRONE["velvet"])
    d.rectangle((tx - 20, 86, tx + 20, 104), fill=THRONE["throne_sh"])
    d.rectangle((tx - 18, 84, tx + 18, 90), fill=THRONE["velvet"])
    for x in (tx - 18, tx + 16):
        d.rectangle((x, 72, x + 2, 104), fill=THRONE["throne"])
    d.polygon([(tx - 18, 105), (tx + 18, 105), (tx + 60, H), (tx - 60, H)], fill=THRONE["carpet"])   # the carpet
    d.line([(tx - 18, 105), (tx - 60, H)], fill=THRONE["trim"])
    d.line([(tx + 18, 105), (tx + 60, H)], fill=THRONE["trim"])
    for y in (120, 142, 168):
        d.line([(tx - 18 - (y - 105) * 42 // 75, y), (tx + 18 + (y - 105) * 42 // 75, y)], fill=THRONE["carpet_sh"])
    for x in (36, 284):
        blend_poly(img, [(x - 8, 90), (x + 8, 90), (x + 40 + (x - 160) // 6, 150), (x + 4 + (x - 160) // 6, 150)],
                   THRONE["window"], 0.12)
    return img


def throne(c):
    img = throne_static().copy()
    d = ImageDraw.Draw(img)
    x, y = KNEEL                                                      # the cushion
    d.ellipse((x - 14, y - 4, x + 14, y + 4), fill=THRONE["velvet"], outline=INK)
    d.line([(x - 10, y - 1), (x + 10, y - 1)], fill=(170, 60, 130))
    return img


scene("v3_throne", shots={"hall": (160, 90, 6), "knight": (166, 132, 12), "crown": (198, 110, 18)},
      cast={"david": dict(x=KNEEL[0], y=KNEEL[1] - 1, facing=1, body="kneel", arm="down", eyes="shut")})(throne)


def sword(img, tip, towards, length=36):
    """A sword whose point is at `tip`, its hilt `length` back along the line to `towards`."""
    tx, ty = tip
    dx, dy = towards[0] - tx, towards[1] - ty
    n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n
    hx, hy = tx + ux * length, ty + uy * length
    d = ImageDraw.Draw(img)
    d.line([(tx, ty), (hx, hy)], fill=INK, width=4)
    d.line([(tx, ty), (hx, hy)], fill=THRONE["steel"], width=2)
    d.line([(tx + uy * 0.5, ty - ux * 0.5), (hx, hy)], fill=THRONE["steel_sh"], width=1)
    gx, gy = -uy * 6, ux * 6                                          # the crossguard
    d.line([(hx - gx, hy - gy), (hx + gx, hy + gy)], fill=INK, width=4)
    d.line([(hx - gx, hy - gy), (hx + gx, hy + gy)], fill=C["gold"], width=2)
    ex, ey = hx + ux * 8, hy + uy * 8                                 # the grip and pommel
    d.line([(hx, hy), (ex, ey)], fill=C["wood_sh"], width=3)
    d.ellipse((ex - 2, ey - 2, ex + 2, ey + 2), fill=C["gold"], outline=INK)
    return hx, hy


# --- the study: four planets on a shelf ----------------------------------------------------------------

STUDY = {"wall": (70, 46, 42), "wall2": (86, 58, 50), "panel": (104, 70, 54), "panel_sh": (80, 52, 44),
         "shelf": (150, 100, 62), "shelf_sh": (100, 64, 44), "shelf_hi": (190, 136, 86), "brass": (214, 176, 90),
         "lamp": (255, 226, 160), "frame": (170, 130, 70), "floor": (60, 40, 36), "book1": (60, 90, 130),
         "book2": (130, 50, 50), "book3": (70, 110, 70)}
SHELF_Y = 100
SLOTS = (60, 104, 148, 192)                   # the four trophies
EXTRA = (226, 262, 298)                       # where the pundit's pen adds three more
KINDS = ("blue", "frozen", "green", "earth")
NAMES = ("BLUE", "FROZEN", "GREEN", "EARTH")


@lru_cache(maxsize=1)
def study_static():
    img = Image.new("RGB", (W, H), STUDY["wall"])
    vgrad(img, (0, 0, W, 124), STUDY["wall2"], STUDY["wall"], steps=3)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):                                        # panelling
        d.line([(x, 0), (x, 124)], fill=STUDY["panel_sh"])
    d.rectangle((0, 124, W, H), fill=STUDY["panel"])                  # wainscot
    for x in range(0, W, 20):
        d.line([(x, 125), (x, H)], fill=STUDY["panel_sh"])
    d.line([(0, 124), (W, 124)], fill=STUDY["shelf_hi"])
    blend(img, mask(lambda m: m.ellipse((150, -40, 330, 90), fill=255)), STUDY["lamp"], 0.08)   # lamplight
    # the shelf, with brackets
    d.rectangle((24, SHELF_Y, W - 8, SHELF_Y + 5), fill=STUDY["shelf"])
    d.line([(24, SHELF_Y), (W - 8, SHELF_Y)], fill=STUDY["shelf_hi"])
    d.line([(24, SHELF_Y + 5), (W - 8, SHELF_Y + 5)], fill=STUDY["shelf_sh"])
    for x in (40, 160, 280):
        d.polygon([(x - 2, SHELF_Y + 6), (x + 2, SHELF_Y + 6), (x + 2, SHELF_Y + 16)], fill=STUDY["shelf_sh"])
    for k, name in enumerate(NAMES):                                 # brass name plates on the shelf edge
        x = SLOTS[k]
        tw = pixel.text_width(name, SILK)
        d.rectangle((x - tw // 2 - 2, SHELF_Y + 7, x + tw // 2 + 1, SHELF_Y + 14), fill=STUDY["brass"])
        pixel.text(img, (x - tw // 2, SHELF_Y + 6), name, SILK, (70, 46, 30), shadow=None)
    for k, (x, h, colr) in enumerate(((212, 22, "book1"), (218, 18, "book2"), (223, 24, "book3"))):
        d.rectangle((x, SHELF_Y - h, x + 4, SHELF_Y - 1), fill=STUDY[colr], outline=INK)
    return img


def study(c):
    img = study_static().copy()
    n = c.get("planets", 4)
    ph = int(c.t * 2) % 16
    for k in range(min(n, 4)):
        tr = planet_trophy(KINDS[k], (ph + k * 4) % 16)
        dy = c.get(f"drop{k}", 0)
        img.paste(tr, (SLOTS[k] - tr.width // 2, SHELF_Y - tr.height + 1 - int(dy)), tr)
    return img


scene("v3_study", shots={"shelf": (126, 82, 9), "room": (150, 100, 9), "wide": (160, 90, 6)},
      cast={"david": dict(x=240, y=152, facing=-1, arm="palm", z=1)})(study)


# --- the desert: what's in the box -------------------------------------------------------------------

DESERT = {"sky": (156, 190, 212), "sky2": (236, 224, 186), "ground": (212, 182, 122), "ground_sh": (184, 150, 96),
          "ground_hi": (232, 208, 150), "far": (176, 158, 126), "pylon": (70, 64, 70), "wire": (60, 56, 62),
          "box": (196, 156, 102), "box_sh": (156, 118, 76), "box_hi": (226, 192, 138), "tape": (228, 216, 180),
          "bone": (238, 230, 212), "bone_sh": (190, 178, 158)}
HORIZON = 98
BOX = (198, 152)                              # the box's front bottom centre
PYLONS = ((262, 150, 1.0), (150, HORIZON + 14, 0.45), (92, HORIZON + 6, 0.26), (58, HORIZON + 2, 0.16))


def pylon(d, x, base, s):
    """A lattice pylon, scaled by s, feet on `base`; returns the tips of its arms."""
    h, w = 110 * s, 22 * s
    top = base - h
    d.line([(x - w, base), (x - 2 * s, top)], fill=DESERT["pylon"], width=max(1, int(2 * s)))
    d.line([(x + w, base), (x + 2 * s, top)], fill=DESERT["pylon"], width=max(1, int(2 * s)))
    for k in range(1, 6):                                            # the lattice
        p0, p1 = (k - 1) / 6, k / 6
        xa, xb = lerp(x - w, x - 2 * s, p0), lerp(x + w, x + 2 * s, p1)
        d.line([(xa, lerp(base, top, p0)), (xb, lerp(base, top, p1))], fill=DESERT["pylon"])
    arms = []
    for k, (yy, aw) in enumerate(((top + 12 * s, 24 * s), (top + 28 * s, 30 * s))):
        d.line([(x - aw, yy), (x + aw, yy)], fill=DESERT["pylon"], width=max(1, int(2 * s)))
        arms += [(x - aw, yy + 2 * s), (x + aw, yy + 2 * s)]
    return arms


@lru_cache(maxsize=1)
def desert_static():
    img = Image.new("RGB", (W, H), DESERT["sky"])
    vgrad(img, (0, 0, W, HORIZON), DESERT["sky"], DESERT["sky2"], steps=4)
    d = ImageDraw.Draw(img)
    d.polygon([(0, HORIZON), (40, HORIZON - 5), (90, HORIZON - 2), (140, HORIZON - 6), (200, HORIZON - 1),
               (260, HORIZON - 4), (W, HORIZON - 2), (W, HORIZON), ], fill=DESERT["far"])
    d.rectangle((0, HORIZON, W, H), fill=DESERT["ground"])
    for k in range(5):
        y = HORIZON + 3 + k * k * 4
        d.line([(0, y), (W, y)], fill=DESERT["ground_sh"])
    for k in range(80):                                              # scrub
        x, y = rnd("scrub", k) * W, HORIZON + 4 + rnd("scrub-y", k) ** 1.5 * (H - HORIZON - 4)
        s = 1 + int((y - HORIZON) / 30)
        d.line([(x, y), (x + s, y - s)], fill=DESERT["ground_hi"] if k % 2 else DESERT["ground_sh"])
    arms = [pylon(d, x, base, s) for x, base, s in PYLONS]
    for a, b in zip(arms, arms[1:]):                                 # the power lines, sagging
        for (x0, y0), (x1, y1) in zip(a, b):
            pts = [(lerp(x0, x1, p / 10), lerp(y0, y1, p / 10) + 6 * math.sin(math.pi * p / 10)) for p in range(11)]
            d.line(pts, fill=DESERT["wire"])
    for (x0, y0) in arms[0]:                                         # and on out of the frame
        d.line([(x0, y0), (W + 20, y0 + 16)], fill=DESERT["wire"])
    return img


def desert(c):
    return desert_static().copy()


scene("v3_desert", shots={"wide": (160, 90, 6), "box": (186, 124, 12), "close": (186, 126, 18)},
      cast={"morgan": dict(x=172, y=153, facing=1, hat="fedora", body="kneel", arm="down")})(desert)


@lru_cache(maxsize=None)
def cardboard_box(open_=0):
    """A cardboard box in three-quarter view: shut (0), flaps lifting (1), wide open (2)."""
    s = Canvas(30, 30)
    B = DESERT
    s.poly([(2, 12), (22, 12), (22, 28), (2, 28)], B["box"])               # front
    s.poly([(22, 12), (28, 8), (28, 24), (22, 28)], B["box_sh"])           # side
    if open_ == 0:
        s.poly([(2, 12), (8, 8), (28, 8), (22, 12)], B["box_hi"])          # lid
        s.line([(5, 10), (25, 10)], B["tape"])
        s.rect((11, 12, 13, 18), B["tape"])
    else:
        s.poly([(2, 12), (8, 8), (28, 8), (22, 12)], (40, 30, 26))         # the dark inside
        lift = 6 if open_ == 1 else 11
        s.poly([(2, 12), (8, 8), (7, 8 - lift), (1, 12 - lift)], B["box_hi"])          # flaps
        s.poly([(22, 12), (28, 8), (29, 8 - lift), (23, 12 - lift)], B["box_sh"])
        s.poly([(2, 12), (22, 12), (18, 12 - lift), (0, 12 - lift + 2)], B["box_hi"])
    s.line([(4, 22), (20, 22)], B["box_sh"])
    return s.done()


@lru_cache(maxsize=1)
def spine():
    """A spine: a column of vertebrae with a gentle S-curve, top to tail."""
    s = Canvas(12, 38)
    B = DESERT
    for k in range(11):
        y = 2 + k * 3
        x = 5 + round(math.sin(k / 10 * 2 * math.pi) * 1.5)
        w = 2 if k < 3 else 3 if k < 8 else 2
        s.rect((x - w, y, x + w, y + 1), B["bone"])
        s.px((x + w + 1, y), B["bone_sh"])
        s.px((x - w - 1, y + 1), B["bone_sh"])
        s.px((x, y + 2), B["bone_sh"])
    s.poly([(3, 34), (8, 34), (6, 37)], B["bone"])                          # the tailbone
    return s.done()


# --- the steering wheel: ten and two -------------------------------------------------------------------

WHEEL_C, WHEEL_R = (160, 160), 64
TEN_TWO = tuple((WHEEL_C[0] + WHEEL_R * math.sin(math.radians(a)), WHEEL_C[1] - WHEEL_R * math.cos(math.radians(a)))
                for a in (300, 60))


def wheel_close(c):
    img = Image.new("RGB", (W, H), DASH["sky"])
    road_view(img, c.t, (0, 0, W, 100), horizon=56)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (18, 0), (6, 100), (0, 100)], fill=(40, 60, 54))            # the pillars (bottle green)
    d.polygon([(W, 0), (W - 18, 0), (W - 6, 100), (W, 100)], fill=(40, 60, 54))
    d.rectangle((0, 0, W, 4), fill=(40, 60, 54))
    d.rectangle((0, 96, W, 124), fill=(120, 76, 50))                               # a walnut dash
    d.line([(0, 96), (W, 96)], fill=(170, 116, 76))
    d.line([(0, 124), (W, 124)], fill=(80, 50, 36))
    for x in (60, 260):                                                            # two round gauges
        d.ellipse((x - 11, 99, x + 11, 121), fill=(30, 28, 30), outline=(210, 214, 222))
        d.ellipse((x - 8, 102, x + 8, 118), fill=(240, 234, 214))
        a = math.radians(210 + (c.t * 40 + x) % 60)
        d.line([(x, 110), (x + math.cos(a) * 6, 110 - math.sin(a) * 6)], fill=C["red"])
    # the daisy in a bud vase on the dash
    vx = 292
    d.rectangle((vx - 2, 86, vx + 2, 96), fill=(170, 210, 220), outline=INK)
    d.line([(vx, 86), (vx - 1, 72)], fill=(70, 130, 60))
    for k in range(8):
        a = k * math.pi / 4
        d.ellipse((vx - 1 + math.cos(a) * 3 - 1.5, 70 + math.sin(a) * 3 - 1.5, vx - 1 + math.cos(a) * 3 + 1.5,
                   70 + math.sin(a) * 3 + 1.5), fill=(250, 250, 250))
    d.ellipse((vx - 3, 68, vx + 1, 72), fill=(246, 200, 50))
    d.rectangle((0, 124, W, H), fill=(40, 30, 30))                                  # the footwell's dark
    # the wheel: a thin black rim, three spokes, the horn
    cx, cy = WHEEL_C
    r = WHEEL_R
    for a in (90, 270, 180):
        ra = math.radians(a)
        d.line([(cx, cy), (cx + math.cos(ra) * r, cy + math.sin(ra) * r)], fill=(26, 24, 28), width=5)
        d.line([(cx, cy - 1), (cx + math.cos(ra) * r, cy + math.sin(ra) * r - 1)], fill=(150, 150, 160))
    d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), outline=INK, width=7)
    d.ellipse((cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), outline=(40, 36, 40), width=5)
    d.arc((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), 200, 250, fill=(110, 106, 116), width=1)
    d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(30, 28, 32), outline=INK)
    d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(200, 204, 214))
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=C["gold"])
    # the chauffeur's hands, at ten and two, and his grey sleeves
    for (hx, hy), side in zip(TEN_TWO, (-1, 1)):
        d.polygon([(hx - 7, hy + 5), (hx + 7, hy + 5), (hx + side * 34 + 10, H), (hx + side * 34 - 16, H)],
                  fill=C["chauf"], outline=INK)
        d.line([(hx + side * 2, hy + 12), (hx + side * 30, H)], fill=C["chauf_sh"])
        d.rectangle((hx - 7, hy + 3, hx + 7, hy + 7), fill=C["white"], outline=INK)            # the cuff
        d.ellipse((hx - 8, hy - 7, hx + 8, hy + 5), fill=C["mskin"], outline=INK)
        for k in range(3):                                                                  # knuckles
            d.point((hx - 4 + k * 4, hy - 4), fill=C["mskin_hi"])
        d.line([(hx - 6, hy + 1), (hx + 6, hy + 1)], fill=C["mskin_sh"])
    return img


scene("v3_wheel", shots={"wheel": (160, 110, 6), "hands": (160, 118, 9)})(wheel_close)


# --- the grave: pushing up daisies --------------------------------------------------------------------

GRAVE = {"sky": (150, 168, 196), "sky2": (206, 210, 218), "hill": (96, 140, 80), "hill_sh": (74, 112, 64),
         "hill_hi": (126, 168, 96), "stone": (156, 154, 162), "stone_sh": (112, 110, 122), "stone_hi": (192, 190, 196),
         "soil": (104, 74, 54), "soil_sh": (80, 56, 44), "yew": (40, 70, 52), "yew_hi": (58, 94, 66),
         "wall": (140, 130, 118), "wall_sh": (110, 102, 94)}
STONE = (214, 146)                             # the headstone's base centre
MOUND = (214, 158)                             # the grave mound's centre
EPITAPH_Y = STONE[1] - 34                      # where "narrated by" gets carved


@lru_cache(maxsize=1)
def grave_static():
    img = Image.new("RGB", (W, H), GRAVE["sky"])
    vgrad(img, (0, 0, W, 110), GRAVE["sky"], GRAVE["sky2"], steps=4)
    d = ImageDraw.Draw(img)
    d.ellipse((-60, 84, 200, 200), fill=GRAVE["hill_sh"])             # rolling hills
    d.ellipse((120, 92, 420, 220), fill=GRAVE["hill"])
    d.rectangle((0, 124, W, H), fill=GRAVE["hill"])
    for x in range(0, W, 12):                                         # a dry-stone wall along the back
        d.rectangle((x, 112, x + 10, 118), fill=GRAVE["wall"] if (x // 12) % 2 else GRAVE["wall_sh"])
    d.line([(0, 111), (W, 111)], fill=GRAVE["wall_sh"])
    for x, h in ((60, 12), (98, 10), (262, 11), (292, 9)):             # old headstones, further off
        d.rectangle((x - 4, 124 - h, x + 4, 124), fill=GRAVE["stone_sh"])
        d.ellipse((x - 4, 124 - h - 4, x + 4, 124 - h + 4), fill=GRAVE["stone_sh"])
    d.rectangle((24, 60, 30, 128), fill=(70, 50, 40))                  # a yew
    for k in range(6):
        d.ellipse((4 + k * 5, 30 + k * 6, 50 - k * 3, 86 + k * 4), fill=GRAVE["yew"] if k % 2 else GRAVE["yew_hi"])
    for k in range(60):
        x, y = rnd("gr", k) * W, 126 + rnd("gr-y", k) * 52
        d.line([(x, y), (x + 1, y - 2)], fill=GRAVE["hill_hi"])
    # the mound and the headstone
    mx, my = MOUND
    d.ellipse((mx - 34, my - 8, mx + 34, my + 8), fill=GRAVE["soil"], outline=INK)
    d.arc((mx - 30, my - 6, mx + 30, my + 6), 190, 350, fill=GRAVE["soil_sh"])
    x, y = STONE
    d.rectangle((x - 35, y - 50, x + 35, y), fill=GRAVE["stone"], outline=INK)
    d.ellipse((x - 35, y - 66, x + 35, y - 34), fill=GRAVE["stone"], outline=INK)
    d.rectangle((x - 34, y - 50, x + 34, y - 1), fill=GRAVE["stone"])
    d.line([(x + 34, y - 48), (x + 34, y - 1)], fill=GRAVE["stone_sh"])
    d.line([(x - 34, y - 48), (x - 34, y - 1)], fill=GRAVE["stone_hi"])
    d.rectangle((x - 40, y - 2, x + 40, y + 2), fill=GRAVE["stone_sh"], outline=INK)       # the plinth
    pixel.text(img, (x, y - 60), "R.I.P.", SILK, GRAVE["stone_sh"], shadow=None, anchor="ma")
    pixel.text(img, (x, y - 49), "MORGAN F.", SILK, (60, 58, 70), shadow=None, anchor="ma")
    d.line([(x - 16, y - 38), (x + 16, y - 38)], fill=GRAVE["stone_sh"])
    return img


def grave(c):
    return grave_static().copy()


scene("v3_grave", shots={"wide": (160, 90, 6), "stone": (206, 118, 12), "both": (182, 122, 9)},
      cast={"david": dict(x=164, y=168, facing=1, body="crouch", mic="fluffy", arm="down", z=1)})(grave)


@lru_cache(maxsize=None)
def daisy(h=6, open_=True):
    """A daisy on a stem of height h (its base at the bottom centre)."""
    s = Canvas(9, h + 9)
    s.line([(4, h + 8), (4, 6)], (70, 140, 60))
    if h > 8:
        s.pxs([(5, h // 2 + 7), (6, h // 2 + 6), (5, h // 2 + 6)], (90, 160, 70))    # a leaf
    if open_:
        s.ell((0, 0, 8, 8), (252, 252, 252))
        s.pxs([(6, 6), (7, 5), (5, 7)], (206, 212, 222))
        for xy in ((4, 0), (0, 4), (8, 4), (4, 8)):                                  # gaps between petals
            s.img.putpixel(xy, (0, 0, 0, 0))
        s.rect((3, 3, 5, 5), (246, 200, 50))
        s.px((5, 5), (206, 150, 40))
    else:
        s.ell((2, 3, 6, 8), (110, 176, 84))
        s.px((4, 3), (252, 252, 252))
    return s.done()


# --- the savanna at dusk -------------------------------------------------------------------------------

DUSK = {"top": (60, 36, 92), "mid": (176, 84, 112), "low": (250, 160, 90), "sun": (255, 228, 160),
        "hill": (100, 56, 86), "tree": (44, 22, 46), "ground": (116, 68, 62), "grass": (156, 98, 62),
        "grass_sh": (110, 64, 58), "grass_hi": (222, 156, 86), "grass_dk": (66, 34, 50)}
SAVANNA = 132                                  # the horizon


@lru_cache(maxsize=None)
def dusk_static(sun_x=228, sun_y=124, tx=72):
    img = Image.new("RGB", (W, H), DUSK["top"])
    vgrad(img, (0, 0, W, 70), DUSK["top"], DUSK["mid"], steps=4)
    vgrad(img, (0, 70, W, SAVANNA), DUSK["mid"], DUSK["low"], steps=4)
    d = ImageDraw.Draw(img)
    blend(img, mask(lambda m: m.ellipse((sun_x - 60, sun_y - 44, sun_x + 60, sun_y + 44), fill=255)), DUSK["sun"], 0.16)
    d.ellipse((sun_x - 20, sun_y - 20, sun_x + 20, sun_y + 20), fill=DUSK["sun"])
    for k in range(3):                                                 # bands of haze across the sun
        y = sun_y - 12 + k * 8
        d.line([(sun_x - 24, y), (sun_x + 24, y)], fill=DUSK["low"])
    d.polygon([(0, SAVANNA), (0, 118), (50, 112), (110, 122), (170, 116), (240, 124), (W, 114), (W, SAVANNA)],
              fill=DUSK["hill"])
    d.rectangle((0, SAVANNA, W, H), fill=DUSK["ground"])
    # an acacia, flat-topped
    d.polygon([(tx - 2, SAVANNA), (tx + 2, SAVANNA), (tx + 3, 92), (tx - 1, 92)], fill=DUSK["tree"])
    d.line([(tx + 1, 100), (tx - 16, 84)], fill=DUSK["tree"], width=2)
    d.line([(tx + 1, 96), (tx + 18, 82)], fill=DUSK["tree"], width=2)
    d.ellipse((tx - 44, 72, tx + 44, 88), fill=DUSK["tree"])
    d.ellipse((tx - 30, 66, tx + 30, 80), fill=DUSK["tree"])
    for k in range(90):                                                # grass tufts on the plain
        x, y = rnd("sv", k) * W, SAVANNA + 2 + rnd("sv-y", k) * 16
        d.line([(x, y), (x - 1, y - 3), ], fill=DUSK["grass"])
        d.line([(x + 2, y), (x + 3, y - 4)], fill=DUSK["grass_sh"])
    return img


def dusk(c):
    return dusk_static(*c.get("sun", (228, 124)), c.get("tree", 72)).copy()


def long_grass(img, t, y0, y1, n, colors, seed, height=(14, 26), sway=1.0):
    """A band of tall grass blades rooted between rows y0 and y1, leaning in the evening breeze."""
    d = ImageDraw.Draw(img)
    for k in range(n):
        x = rnd(seed, k) * (W + 20) - 10
        y = y0 + rnd(seed, k, "y") * (y1 - y0)
        h = lerp(height[0], height[1], rnd(seed, k, "h"))
        lean = (math.sin(t * 1.3 + x * 0.05) * 2 + 2) * sway
        d.line([(x, y), (x + lean * 0.5, y - h * 0.6), (x + lean, y - h)], fill=colors[k % len(colors)])


def dusk_mid(c):
    """The long grass: tall enough to hide a crouching male."""
    long_grass(c.world, c.t, 150, 176, 260, (DUSK["grass"], DUSK["grass_sh"], DUSK["grass_hi"]), "lg", (18, 30))
    d = ImageDraw.Draw(c.world)
    d.rectangle((0, 164, W, H), fill=DUSK["grass_sh"])


def dusk_near(c):
    long_grass(c.world, c.t, 176, 186, 60, (DUSK["grass_dk"],), "ng", (20, 44), sway=1.6)


scene("v3_dusk", mid=dusk_mid, near=dusk_near,
      shots={"wide": (160, 90, 6), "plain": (176, 120, 9), "grass": (196, 128, 12)},
      cast={"morgan": dict(x=206, y=158, facing=-1, shadow=False),
            "david": dict(x=96, y=170, facing=1, body="crouch", mic="fluffy", arm="down", z=1, shadow=False)})(dusk)


@lru_cache(maxsize=None)
def butterfly(frame=0):
    """A small butterfly, wings open (0) or closed up (1)."""
    s = Canvas(9, 8)
    s.line([(4, 2), (4, 6)], (40, 30, 40))
    if frame == 0:
        s.ell((0, 1, 3, 4), (250, 170, 60)); s.ell((5, 1, 8, 4), (250, 170, 60))
        s.ell((1, 4, 3, 6), (230, 120, 50)); s.ell((5, 4, 7, 6), (230, 120, 50))
    else:
        s.poly([(4, 4), (2, 0), (5, 0)], (250, 170, 60))
    return s.done()


# --- the action replay: the VHS tear and the pundit's pen -----------------------------------------------

PEN = (255, 236, 60)


def vhs_tear(img, t, amount=1.0):
    """A rewinding tape: bands of the picture torn sideways, and bright tracking lines."""
    a = np.asarray(img).copy()
    f = int(t * 24)
    for k in range(int(6 * amount) + 1):
        y = int(rnd("tear", f, k) * H)
        h = 3 + int(rnd("tear-h", f, k) * 10)
        dx = int((rnd("tear-x", f, k) - 0.5) * 60 * amount)
        a[y:y + h] = np.roll(a[y:y + h], dx, axis=1)
    img.paste(Image.fromarray(a))
    for k in range(3):
        y = int(rnd("trk", f, k) * H)
        blend(img, mask(lambda m: m.rectangle((0, y, W, y + 1 + k), fill=255)), (240, 240, 250), 0.5 * amount)


def pen_path(ui, pts, p, color=PEN, width=2):
    """Draw the first fraction p of a polyline, as a pundit's pen would: ink edge, bright stroke."""
    if p <= 0 or len(pts) < 2:
        return
    lens = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(lens) or 1
    left = total * min(1.0, p)
    out = [pts[0]]
    for (a, b), L in zip(zip(pts, pts[1:]), lens):
        if left <= 0:
            break
        q = min(1.0, left / L) if L else 1.0
        out.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q))
        left -= L
    d = ImageDraw.Draw(ui)
    d.line(out, fill=INK + (255,), width=width + 2, joint="curve")
    d.line(out, fill=col(color) + (255,), width=width, joint="curve")


def pen_ring(ui, cx, cy, rx, ry, p, color=PEN, seed=0):
    """A hand-drawn loop round (cx, cy): it starts at the top left and overshoots a little."""
    n = 28
    a0 = -2.2 + rnd("ring", seed) * 0.4
    pts = []
    for k in range(n + 1):
        a = a0 + (2 * math.pi + 0.5) * k / n
        wob = 1 + 0.06 * math.sin(k * 1.7 + seed)
        pts.append((cx + math.cos(a) * rx * wob, cy + math.sin(a) * ry * wob))
    pen_path(ui, pts, p, color)


def pen_text(ui, x, y, s, age, color=PEN, fnt=PRESS, cps=24.0):
    """The pundit's scrawl: text written out a letter at a time from age 0."""
    if age < 0:
        return
    shown = s[:max(1, int(age * cps) + 1)]
    pixel.text(ui, (int(x), int(y)), shown, fnt, col(color), shadow=INK)
