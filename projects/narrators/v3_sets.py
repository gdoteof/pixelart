"""Sets and sprites for Verse 3 (gags_v3.py), Sir David going for the kill.

The Red List, the Lucy lecture and the X-ray camera, the Jurassic sea with its
Attenborosaurus, the Ford Taurus and its sat-nav, the plastic-versus-Tennessee split
screen, the pitcher plant (outside and in), the Universal globe, the knighting, the
shelf of planets, the Se7en desert, the steering wheel clock, the daisy grave and the
savanna at dusk.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from characters import figure
from engine import (INK, PRESS, SILK, H, W, Canvas, blend, blend_poly, mask, mix, rnd, scaled, vgrad)
from pixelart import pixel
from sets import scene


def portrait(who, size=1, **pose):
    """A character's head and shoulders cut from their sprite (for screens, pages and photos)."""
    spr, a = figure(who, 1, **pose)
    hx, hy = a["head"]
    crop = spr.crop((int(hx - 11), int(hy - 11), int(hx + 11), int(hy + 12)))
    return scaled(crop, size)


# --- the Red List -------------------------------------------------------------------------------

RED_BOOK, RED_BOOK_SH, RED_BOOK_HI = (186, 38, 44), (128, 24, 36), (226, 84, 78)


@lru_cache(maxsize=None)
def red_list(open_=False, stamped=False):
    """The IUCN Red List as a big red hardback: shut, or open at Morgan's entry (optionally stamped EX)."""
    if not open_:
        s = Canvas(22, 27)
        s.rect((1, 1, 20, 25), RED_BOOK)
        s.rect((1, 1, 3, 25), RED_BOOK_SH)
        s.line([(4, 2), (19, 2)], RED_BOOK_HI)
        s.rect((19, 3, 20, 24), "paper")
        s.text((12, 3), "RED", "gold", anchor="ma")
        s.text((12, 10), "LIST", "gold", anchor="ma")
        s.ell((9, 18, 14, 23), "gold_sh")
        s.px((11, 20), "gold_hi")
        return s.done()
    s = Canvas(46, 30)
    s.rect((1, 3, 44, 28), RED_BOOK)
    s.rect((2, 1, 21, 26), "paper")
    s.rect((24, 1, 43, 26), "paper")
    s.line([(22, 1), (22, 27)], RED_BOOK_SH)
    s.line([(23, 1), (23, 27)], "paper_sh")
    s.rect((5, 4, 18, 17), (70, 66, 80))                               # the specimen's photo
    s.ell((8, 6, 16, 16), "mskin")
    s.line([(8, 7), (15, 6)], "mhair")
    s.line([(9, 15), (15, 15)], "mhair")
    s.px((13, 10), "eye")
    for y in (19, 22):
        s.line([(5, y), (18, y)], "paper_sh")
    s.line([(26, 4), (38, 4)], "ink")                                  # the entry
    for y in (8, 11):
        s.line([(26, y), (41, y)], "paper_sh")
    for k, (_, _, c) in enumerate([(0, 0, (76, 170, 92)), (0, 0, (150, 190, 70)), (0, 0, (236, 196, 50)),
                                   (0, 0, (240, 140, 50)), (0, 0, (220, 60, 50)), (0, 0, (120, 40, 90)),
                                   (0, 0, (30, 24, 30))]):
        s.rect((26 + k * 2, 15, 26 + k * 2, 16), c if (k == 6 if stamped else k == 0) else "paper_sh")
    if stamped:
        s.rect((27, 18, 40, 25), "red")
        s.rect((28, 19, 39, 24), "paper")
        s.text((34, 18), "EX", "red", anchor="ma")
    return s.done()


# --- the Lucy lecture -----------------------------------------------------------------------------

LEC = {"wall": (46, 50, 74), "wall2": (60, 66, 92), "panel": (104, 70, 52), "panel_sh": (80, 54, 44),
       "screen": (238, 236, 228), "screen_sh": (206, 204, 198), "brain": (236, 156, 176), "brain_sh": (196, 110, 136),
       "lit": (255, 228, 80), "head": (26, 24, 34), "wood": (120, 80, 56), "wood_hi": (160, 112, 76)}
SCREEN = (30, 16, 206, 110)
LECTERN = (234, 118, 270, 152)
PROF = (252, 140)                  # Morgan's feet, behind the lectern
BRAIN_AT = (118, 70)               # centre of the brain on the slide


@lru_cache(maxsize=None)
def brain(lit=False):
    """A brain in profile, front to the left; `lit` lights one small lobe: the famous ten percent."""
    s = Canvas(76, 50)
    s.ell((50, 26, 70, 44), LEC["brain_sh"])                           # cerebellum
    s.rect((42, 34, 49, 48), LEC["brain_sh"])                          # brainstem
    s.ell((2, 3, 68, 38), LEC["brain"])
    s.ell((4, 8, 30, 36), LEC["brain"])
    for pts in ([(8, 20), (14, 14), (22, 18), (30, 11), (40, 16)], [(12, 28), (20, 24), (30, 28), (38, 22), (48, 26)],
                [(36, 8), (44, 12), (52, 8), (60, 14)], [(26, 34), (34, 30), (44, 34), (54, 30), (62, 24)],
                [(44, 18), (52, 20), (58, 26), (64, 20)]):
        s.line(pts, LEC["brain_sh"])
    s.line([(24, 6), (30, 30), (36, 36)], LEC["brain_sh"])             # the central sulcus
    if lit:
        s.ell((8, 8, 19, 17), LEC["lit"])
        s.ell((11, 10, 16, 15), (255, 250, 210))
    return s.done()


@lru_cache(maxsize=1)
def lecture_static():
    img = Image.new("RGB", (W, H), LEC["wall"])
    vgrad(img, (0, 0, W, 120), LEC["wall2"], LEC["wall"], steps=3)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 120, W, H), fill=LEC["panel"])
    for x in range(0, W, 24):
        d.line([(x, 121), (x, H)], fill=LEC["panel_sh"])
    d.line([(0, 120), (W, 120)], fill=LEC["wood_hi"])
    x0, y0, x1, y1 = SCREEN
    d.rectangle((x0 - 4, y0 - 6, x1 + 4, y0 - 2), fill=(30, 30, 36))    # the roller
    d.rectangle((x0 + 2, y0 + 2, x1 + 2, y1 + 2), fill=(30, 32, 50))    # shadow
    d.rectangle((x0, y0, x1, y1), fill=LEC["screen"])
    d.line([(x0, y1), (x1, y1)], fill=LEC["screen_sh"])
    d.rectangle(((x0 + x1) // 2 - 2, y1, (x0 + x1) // 2 + 2, y1 + 3), fill=(30, 30, 36))
    blend_poly(img, [(262, 0), (274, 0), (x1 - 20, y0), (x1 - 60, y0)], (255, 250, 230), 0.07)   # projector beam
    return img


def slide(img, t, lit_at=None, title="LUCY (2014)"):
    """The slide on the screen: a title and the brain, lit up from `lit_at` on."""
    x0, y0, x1, y1 = SCREEN
    pixel.text(img, ((x0 + x1) // 2, y0 + 5), title, PRESS, (40, 36, 50), shadow=None, anchor="ma")
    ImageDraw.Draw(img).line([(x0 + 30, y0 + 15), (x1 - 30, y0 + 15)], fill=LEC["screen_sh"])
    b = brain(lit_at is not None and t >= lit_at)
    img.paste(b, (BRAIN_AT[0] - b.width // 2, BRAIN_AT[1] - b.height // 2 + 4), b)


def lecture(c):
    img = lecture_static().copy()
    slide(img, c.t, c.get("lit_at"))
    return img


def lecture_mid(c):
    """The lectern in front of the professor, and the heads of a packed hall."""
    img = c.world
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = LECTERN
    d.polygon([(x0 - 2, y0), (x1 + 2, y0), (x1, y1), (x0, y1)], fill=INK)
    d.polygon([(x0 - 1, y0 + 1), (x1 + 1, y0 + 1), (x1 - 1, y1 - 1), (x0 + 1, y1 - 1)], fill=LEC["wood"])
    d.rectangle((x0, y0 + 1, x1, y0 + 3), fill=LEC["wood_hi"])
    d.rectangle(((x0 + x1) // 2 - 5, y0 + 12, (x0 + x1) // 2 + 5, y0 + 20), fill=LEC["panel_sh"])
    d.line([(x0 + 6, y0), (x0 + 2, y0 - 7)], fill=(40, 40, 48))                   # the lectern mic
    d.ellipse((x0, y0 - 10, x0 + 4, y0 - 6), fill=(60, 60, 70))
    for k in range(14):                                                          # the audience
        x = 6 + k * 23 + (k % 2) * 6
        y = 150 + (k % 3) * 3
        bob = 1 if (k + int(c.t * 2.5)) % 5 == 0 else 0
        d.ellipse((x - 7, y - 8 - bob, x + 7, y + 10), fill=LEC["head"])
        d.rectangle((x - 11, y + 6, x + 11, H), fill=LEC["head"])
        if k % 4 == 1:
            d.ellipse((x - 6, y - 8 - bob, x + 6, y - 2 - bob), fill=(200, 200, 206))


scene("v3_lecture", mid=lecture_mid,
      shots={"hall": (160, 90, 6), "screen": (120, 61, 12), "prof": (236, 112, 12)},
      cast={"morgan": dict(x=PROF[0], y=PROF[1], facing=-1, glasses=True, shadow=False)})(lecture)


# --- the X-ray camera ----------------------------------------------------------------------------

XRAY = [(6, 12, 28), (12, 30, 54), (24, 58, 88), (60, 118, 150), (130, 196, 220), (226, 248, 252)]
BRAIN_LIT = (255, 222, 80)


@lru_cache(maxsize=None)
def mini_brain(lit=1.0):
    """The slide's brain in miniature, front to the right, dark but for one small lobe (`lit` 0-1)."""
    s = Canvas(15, 10)
    s.ell((1, 1, 13, 7), XRAY[3])                                      # cerebrum
    s.ell((1, 4, 6, 8), XRAY[2])                                       # cerebellum
    s.px((6, 8), XRAY[2])                                              # stem
    s.line([(4, 3), (6, 2), (8, 3), (10, 2)], XRAY[2])                 # folds
    s.line([(3, 5), (6, 5), (9, 4), (11, 5)], XRAY[2])
    s.ell((9, 1, 12, 4), mix(XRAY[3], BRAIN_LIT, lit))                 # the ten percent
    if lit > 0.5:
        s.px((10, 2), (255, 255, 230))
    return s.done()


def xray(c, who="morgan", lit=1.0, upto=H):
    """The camera's X-ray mode down to row `upto`: the set in dark blues, `who` as soft tissue with a
    skull, a spine and ribs, and in the skull the slide's brain, dark but for one small lobe."""
    from video import sprite_of
    before = np.asarray(c.world).copy()
    lum = before.mean(axis=2) / 255.0
    lev = np.clip((lum * 3).astype(int), 0, 2)
    s = c.st[who]
    if not s["hidden"]:
        spr, a = sprite_of(c, who)
        x, y = int(round(s["x"] + s["dx"])), int(round(s["y"] + s["dy"]))
        ox, oy = x - a["feet"][0], y - a["feet"][1]
        sa = np.asarray(spr)
        ys, xs = np.nonzero(sa[..., 3] > 0)
        wy, wx = ys + oy, xs + ox
        keep = (wy >= 0) & (wy < H) & (wx >= 0) & (wx < W)
        slum = sa[ys[keep], xs[keep], :3].mean(axis=1) / 255.0
        lev[wy[keep], wx[keep]] = np.where(slum > 0.6, 4, 3)
    c.world.paste(Image.fromarray(np.array(XRAY, np.uint8)[lev]))
    if not s["hidden"]:
        d = ImageDraw.Draw(c.world)
        f = s["facing"]
        hx, hy = a["head"][0] + ox, a["head"][1] + oy
        bone = XRAY[5]
        cx = hx - f
        d.ellipse((cx - 8, hy - 12, cx + 8, hy + 5), fill=XRAY[1], outline=bone)    # the skull
        d.line([(cx + 2 * f, hy + 5), (cx + 8 * f, hy + 2)], fill=bone)              # the jaw
        ex, ey = a["eye"][0] + ox, a["eye"][1] + oy
        d.ellipse((ex - 2, ey - 1, ex + 2, ey + 3), fill=XRAY[0], outline=XRAY[4])    # the eye socket
        b = mini_brain(round(lit, 2))
        if f < 0:
            b = b.transpose(Image.FLIP_LEFT_RIGHT)
        c.world.paste(b, (int(cx - 7), int(hy - 12)), b)
        sx = hx - 3 * f                                                               # the spine
        for k in range(7):
            d.rectangle((sx - 1, hy + 7 + k * 3, sx, hy + 8 + k * 3), fill=bone)
        for k in range(4):                                                            # the ribs
            ry = hy + 11 + k * 3
            d.line([(sx + f, ry), (sx + 4 * f, ry - 1), (sx + 8 * f, ry + 1)], fill=XRAY[4])
    if upto < H:
        after = np.asarray(c.world).copy()
        after[max(0, int(upto)):] = before[max(0, int(upto)):]
        c.world.paste(Image.fromarray(after))
        ImageDraw.Draw(c.world).line([(0, int(upto)), (W, int(upto))], fill=(170, 240, 255))


# --- the Jurassic sea ------------------------------------------------------------------------------

JURA = {"sky": (252, 214, 168), "sky2": (236, 172, 148), "sea": (56, 118, 128), "sea_sh": (40, 92, 110),
        "sea_hi": (122, 178, 176), "volcano": (94, 72, 88), "volcano_sh": (72, 56, 72), "lava": (255, 140, 60),
        "rock": (106, 92, 86), "rock_sh": (80, 70, 70), "cycad": (70, 112, 62), "cycad_hi": (104, 146, 80),
        "plesio": (76, 104, 92), "plesio_sh": (54, 78, 72), "plesio_hi": (112, 140, 118), "belly": (170, 180, 150)}
WATER_Y = 118


@lru_cache(maxsize=1)
def jurassic_static():
    img = Image.new("RGB", (W, H), JURA["sky"])
    vgrad(img, (0, 0, W, WATER_Y), JURA["sky2"], JURA["sky"], steps=4)
    d = ImageDraw.Draw(img)
    d.ellipse((222, 30, 250, 58), fill=(255, 240, 200))                          # a hazy sun
    d.polygon([(10, WATER_Y), (58, 50), (74, 50), (130, WATER_Y)], fill=JURA["volcano"])
    d.polygon([(10, WATER_Y), (58, 50), (62, 50), (40, WATER_Y)], fill=JURA["volcano_sh"])
    d.rectangle((58, 48, 74, 51), fill=JURA["lava"])
    d.line([(64, 52), (60, 70), (66, 90)], fill=JURA["lava"])
    d.rectangle((0, WATER_Y, W, H), fill=JURA["sea"])
    for y in range(WATER_Y + 6, H, 9):
        d.line([(0, y), (W, y)], fill=JURA["sea_sh"])
    d.polygon([(252, H), (262, 96), (284, 88), (320, 92), (320, H)], fill=JURA["rock"])   # the rocky shore
    d.polygon([(252, H), (262, 96), (268, 96), (262, H)], fill=JURA["rock_sh"])
    for k, x in enumerate((272, 292, 310)):                                        # cycads
        base = 92 - k % 2 * 3
        d.rectangle((x - 1, base - 16, x + 1, base), fill=(110, 84, 60))
        for a in range(6):
            ang = math.pi * (0.1 + 0.8 * a / 5)
            d.line([(x, base - 16), (x + math.cos(ang) * 12, base - 16 - math.sin(ang) * 7 + 5)],
                   fill=JURA["cycad"] if a % 2 else JURA["cycad_hi"], width=2)
    return img


def jurassic(c):
    img = jurassic_static().copy()
    d = ImageDraw.Draw(img)
    t = c.t
    for k in range(3):                                                            # the volcano smokes
        age = (t * 0.4 + k / 3) % 1.0
        r = 4 + age * 14
        cx, cy = 66 + age * 26, 44 - age * 34
        blend(img, mask(lambda m: m.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=255)), (120, 104, 110),
              0.55 * (1 - age))
    for k in range(4):                                                            # pterosaurs, far off
        x = (60 + k * 70 + t * (9 + k * 2)) % 360 - 20
        y = 30 + k * 7 + 2 * math.sin(t * 3 + k)
        flap = int(t * 5 + k) % 2
        d.line([(x - 3, y - flap), (x, y), (x + 3, y - flap)], fill=(80, 60, 70))
    for k in range(18):                                                           # waves
        x = (k * 37 + t * 14 * (1 + k % 3)) % (W + 20) - 10
        y = WATER_Y + 4 + (k * 13) % (H - WATER_Y - 8)
        d.line([(x, y), (x + 5 + k % 4, y)], fill=JURA["sea_hi"])
    return img


@lru_cache(maxsize=None)
def plesiosaur(mouth=False):
    """Attenborosaurus: a plesiosaur, facing right, with Sir David's swept white hair."""
    s = Canvas(78, 60)
    P = JURA
    s.poly([(0, 44), (12, 41), (12, 47)], P["plesio_sh"])                          # tail
    s.poly([(10, 48), (18, 46), (14, 58), (6, 58)], P["plesio_sh"])                # back flipper
    s.ell((8, 36, 56, 54), P["plesio"])                                            # body
    s.ell((16, 46, 52, 54), P["belly"])
    s.line([(14, 38), (48, 37)], P["plesio_hi"])
    s.poly([(38, 48), (48, 47), (46, 59), (36, 58)], P["plesio"])                  # front flipper
    pts = [(48, 42), (54, 34), (57, 26), (58, 18), (60, 12)]                        # the long neck
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        s.line([(x0, y0), (x1, y1)], P["plesio"], 7)
    s.line([(51, 40), (55, 32), (57, 22), (59, 14)], P["plesio_hi"])
    s.ell((55, 5, 72, 15), P["plesio"])                                             # head
    s.rect((64, 9, 75, 13), P["plesio"])
    if mouth:
        s.poly([(64, 12), (76, 11), (74, 15), (64, 14)], "mouth")
        s.pxs([(67, 12), (70, 12), (73, 12)], "tooth")
    else:
        s.line([(64, 12), (75, 12)], P["plesio_sh"])
    s.px((66, 8), "eye")
    s.ell((53, 1, 64, 8), "hair")                                                   # Sir David's hair
    s.poly([(55, 3), (60, 0), (67, 0), (69, 3), (64, 4), (58, 5)], "hair")
    s.line([(57, 2), (64, 1)], "hair_sh")
    s.pxs([(64, 6), (68, 6)], "hair_sh")                                            # and brows
    return s.done()


scene("v3_jurassic", shots={"sea": (160, 96, 6), "beast": (166, 100, 12)})(jurassic)


# --- the Ford Taurus and its sat-nav -------------------------------------------------------------

DASH = {"dash": (180, 164, 138), "dash_sh": (146, 130, 108), "dash_hi": (206, 192, 166), "pillar": (60, 56, 60),
        "wheel": (44, 42, 48), "wheel_hi": (84, 82, 90), "shirt": (170, 70, 60), "shirt_sh": (126, 46, 46),
        "skin": (238, 196, 170), "skin_sh": (206, 160, 136), "sky": (160, 206, 236), "sky2": (214, 234, 246),
        "field": (128, 172, 96), "field2": (104, 150, 82), "road": (96, 94, 100), "line": (240, 230, 190),
        "bezel": (28, 28, 34), "map": (128, 176, 110), "map_road": (246, 244, 236), "route": (60, 120, 240),
        "bar": (30, 42, 70)}


def road_view(img, t, box, horizon=None, speed=1.0):
    """The road ahead through a windscreen: sky, fields, the road running to a vanishing point, poles."""
    x0, y0, x1, y1 = box
    hz = horizon if horizon is not None else y0 + (y1 - y0) * 3 // 5
    vgrad(img, (x0, y0, x1, hz), DASH["sky"], DASH["sky2"], steps=3)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, hz, x1, y1), fill=DASH["field"])
    for k in range(4):
        yy = hz + 2 + k * k * 3
        d.line([(x0, yy), (x1, yy)], fill=DASH["field2"])
    vx = (x0 + x1) // 2
    d.polygon([(vx - 3, hz), (vx + 3, hz), (x1 - (x1 - x0) // 5, y1), (x0 + (x1 - x0) // 5, y1)], fill=DASH["road"])
    for k in range(6):                                                           # centre dashes, in perspective
        p = ((k / 6) + t * 0.9 * speed) % 1.0
        q = p * p
        ya, yb = hz + (y1 - hz) * q, hz + (y1 - hz) * min(1.0, (p + 0.06) ** 2)
        wa, wb = 1 + q * 3, 1 + min(1.0, (p + 0.06) ** 2) * 3
        d.polygon([(vx - wa / 2, ya), (vx + wa / 2, ya), (vx + wb / 2, yb), (vx - wb / 2, yb)], fill=DASH["line"])
    for k in range(3):                                                           # poles going by on the right
        p = ((k / 3) + t * 0.5 * speed) % 1.0
        q = p * p
        px_ = vx + 6 + (x1 - vx) * 1.2 * q
        top, bot = hz - 4 - 60 * q, hz + (y1 - hz) * q * 0.7
        if px_ < x1:
            d.line([(px_, top), (px_, bot)], fill=(90, 70, 56), width=max(1, int(1 + 3 * q)))


@lru_cache(maxsize=None)
def morgan_face(size=1, mouth="closed"):
    return portrait("morgan", size, mouth=mouth)


def satnav_screen(w, h, t, top="IN 400 FT, TURN LEFT", face=1, spin=False, lines=(), route_to=None):
    """What's on the sat-nav: a map with the route, a banner, and the voice's face in the corner."""
    img = Image.new("RGB", (w, h), DASH["map"])
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    cx = w // 2
    d.polygon([(cx - 4, h), (cx + 4, h), (cx + 2, 12), (cx - 2, 12)], fill=DASH["map_road"])
    d.line([(0, h * 3 // 5), (w, h * 2 // 5)], fill=DASH["map_road"], width=3)
    d.line([(w // 5, 12), (w // 3, h)], fill=DASH["map_road"], width=2)
    if route_to:
        d.line([(cx, h - 4), (cx, h * 3 // 5), route_to], fill=DASH["route"], width=3)
    else:
        d.line([(cx, h - 4), (cx, h * 2 // 5), (w * 3 // 10, h * 2 // 5 + 4)], fill=DASH["route"], width=3)
    d.polygon([(cx, h - 12), (cx + 4, h - 5), (cx - 4, h - 5)], fill=(250, 250, 255))
    if spin:
        a = t * 8
        for k in range(8):
            aa = a + k * math.pi / 4
            v = 90 + k * 20
            d.point((w - 8 + round(math.cos(aa) * 4), 20 + round(math.sin(aa) * 4)), fill=(v, v, min(255, v + 40)))
    for i, (s, colr) in enumerate(lines):
        d.rectangle((6, 16 + i * 11, 6 + pixel.text_width(s, SILK) + 5, 25 + i * 11), fill=(20, 24, 36))
        d.text((9, 15 + i * 11), s, font=SILK, fill=colr)
    if face:
        f = morgan_face(face)
        fx, fy = 3, h - f.height - 2
        d.ellipse((fx - 2, fy - 2, fx + f.width + 1, fy + f.height + 1), fill=(250, 250, 255))
        img.paste(f, (fx, fy), f)
    d.rectangle((0, 0, w, 10), fill=DASH["bar"])                   # the banner, over everything
    d.text((cx, 1), top, font=SILK, fill=(255, 255, 255), anchor="ma")
    return img


TAURUS_NAV = (136, 84, 188, 116)              # the sat-nav on the dashboard (screen box)


def taurus(c):
    img = Image.new("RGB", (W, H), DASH["sky"])
    road_view(img, c.t, (0, 0, W, 104), horizon=58)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 0), (22, 0), (8, 104), (0, 104)], fill=DASH["pillar"])            # windscreen pillars
    d.polygon([(W, 0), (W - 22, 0), (W - 8, 104), (W, 104)], fill=DASH["pillar"])
    d.rectangle((0, 0, W, 5), fill=DASH["pillar"])
    d.rectangle((136, 5, 184, 15), fill=(40, 38, 44))                                 # the rear-view mirror
    d.rectangle((138, 7, 182, 13), fill=(120, 140, 150))
    d.rectangle((150, 9, 152, 10), fill=INK)                                          # the bloke's eyes in it
    d.rectangle((158, 9, 160, 10), fill=INK)
    d.line([(147, 8), (153, 8)], fill=(90, 70, 50))
    d.line([(157, 8), (163, 8)], fill=(90, 70, 50))
    d.polygon([(0, 104), (W, 104), (W, H), (0, H)], fill=DASH["dash"])               # the dashboard
    d.rectangle((0, 100, W, 106), fill=DASH["dash_sh"])
    d.line([(0, 100), (W, 100)], fill=DASH["dash_hi"])
    for x in (110, 210):                                                               # air vents
        d.rectangle((x - 10, 120, x + 10, 128), fill=DASH["dash_sh"])
        for yy in (122, 124, 126):
            d.line([(x - 9, yy), (x + 9, yy)], fill=(120, 106, 90))
    d.rectangle((230, 140, 306, 170), fill=DASH["dash_sh"])                          # the glovebox and its badge
    d.rectangle((232, 142, 304, 168), fill=DASH["dash"])
    d.rectangle((250, 150, 288, 158), fill=(200, 204, 212))
    pixel.text(img, (269, 150), "TAURUS", SILK, (60, 60, 70), shadow=None, anchor="ma")
    # the steering wheel, with the bloke's hands on it (and his checked sleeves)
    cx, cy, r = 62, 158, 40
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=DASH["wheel"], width=5)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=DASH["wheel"])
    d.line([(cx - r + 3, cy), (cx + r - 3, cy)], fill=DASH["wheel"], width=4)
    for sx, hx, hy in ((-1, cx - r + 2, cy - 6), (1, cx + r - 2, cy - 6)):
        d.polygon([(hx - 7, hy + 4), (hx + 7, hy + 4), (hx + 12 * sx + 4, H), (hx + 12 * sx - 10, H)],
                  fill=DASH["shirt"])
        d.line([(hx - 5, hy + 10), (hx + 12 * sx - 6, H)], fill=DASH["shirt_sh"])
        d.ellipse((hx - 6, hy - 5, hx + 6, hy + 6), fill=DASH["skin"])
        d.line([(hx - 5, hy + 1), (hx + 5, hy + 1)], fill=DASH["skin_sh"])
    # the sat-nav on its suction arm
    x0, y0, x1, y1 = TAURUS_NAV
    d.line([((x0 + x1) // 2, y1), ((x0 + x1) // 2, y1 + 8)], fill=(40, 40, 46), width=3)
    d.rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), fill=DASH["bezel"])
    scr = satnav_screen(x1 - x0, y1 - y0, c.t, top=c.get("nav_top", "IN 400 FT, LEFT"), face=1)
    img.paste(scr, (x0, y0))
    return img


scene("v3_taurus", shots={"cab": (160, 90, 6), "nav": (162, 98, 12), "badge": (266, 146, 18)})(taurus)


NAV_BOX = (80, 38, 240, 134)                  # the sat-nav screen, filling the close-up


def satnav_close(c):
    img = Image.new("RGB", (W, H), DASH["sky"])
    road_view(img, c.t, (0, 0, W, H), horizon=70, speed=0.6)
    blend(img, 1.0, (200, 214, 226), 0.35)                                            # out of focus beyond
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = NAV_BOX
    d.line([((x0 + x1) // 2, y1), ((x0 + x1) // 2 + 6, H)], fill=(40, 40, 46), width=8)
    d.rounded_rectangle((x0 - 9, y0 - 9, x1 + 9, y1 + 9), radius=6, fill=DASH["bezel"])
    d.rounded_rectangle((x0 - 9, y0 - 9, x1 + 9, y1 + 9), radius=6, outline=(70, 70, 80))
    scr = satnav_screen(x1 - x0, y1 - y0, c.t, top=c.get("nav_top", "RECALCULATING..."), face=2,
                        spin=c.get("nav_spin", True), lines=c.get("nav_lines", ()))
    img.paste(scr, (x0, y0))
    d.line([(x0 + 2, y0 + 12), (x0 + 30, y0 + 12)], fill=(255, 255, 255))
    return img


scene("v3_satnav", shots={"nav": (160, 88, 6), "close": (160, 86, 9)})(satnav_close)


# --- plastic versus Tennessee -------------------------------------------------------------------

SPLIT_X = 160
BEACH = {"sky": (170, 214, 240), "sea": (60, 140, 190), "sea_hi": (130, 190, 220), "sand": (236, 212, 156),
         "sand_sh": (208, 180, 126), "land": (226, 214, 180), "land2": (206, 196, 160), "river": (120, 170, 220),
         "road": (250, 250, 246), "border": (176, 150, 150)}
PLASTIC = [(24, 124, "bottle"), (52, 132, "bag"), (78, 118, "bottle"), (104, 136, "bag"), (130, 126, "bottle"),
           (40, 100, "bag"), (96, 104, "bottle"), (120, 96, "bag")]


@lru_cache(maxsize=None)
def plastic(kind):
    if kind == "bottle":
        s = Canvas(12, 6)
        s.rect((1, 1, 8, 4), (170, 214, 230))
        s.rect((9, 2, 10, 3), (60, 120, 200))
        s.line([(2, 1), (7, 1)], (230, 246, 250))
        return s.done()
    s = Canvas(12, 10)
    s.poly([(1, 3), (4, 1), (7, 3), (10, 1), (10, 8), (1, 8)], (240, 240, 236))
    s.line([(2, 7), (9, 7)], (200, 200, 206))
    return s.done()


@lru_cache(maxsize=None)
def turtle(frame=0):
    s = Canvas(18, 11)
    s.ell((3, 2, 13, 9), (90, 130, 80))
    s.ell((5, 3, 11, 7), (120, 160, 96))
    s.ell((12, 3, 17, 7), (150, 170, 110))
    s.px((15, 4), "eye")
    fl = 1 if frame else 0
    s.poly([(6, 8), (9, 8), (5, 10 - fl)], (130, 160, 100))
    s.poly([(6, 2), (9, 2), (5, 0 + fl)], (130, 160, 100))
    return s.done()


@lru_cache(maxsize=1)
def split_static():
    img = Image.new("RGB", (W, H), BEACH["sky"])
    d = ImageDraw.Draw(img)
    d.rectangle((0, 60, SPLIT_X, 116), fill=BEACH["sea"])
    for y in range(64, 116, 8):
        d.line([(4 + y % 11, y), (40 + y % 11, y)], fill=BEACH["sea_hi"])
        d.line([(80 + y % 7, y), (120 + y % 7, y)], fill=BEACH["sea_hi"])
    d.rectangle((0, 116, SPLIT_X, H), fill=BEACH["sand"])
    d.line([(0, 116), (SPLIT_X, 116)], fill=(250, 250, 250))
    for k in range(30):
        d.point((rnd("sand", k) * SPLIT_X, 118 + rnd("sand-y", k) * 60), fill=BEACH["sand_sh"])
    # the right half: a road map
    d.rectangle((SPLIT_X, 0, W, H), fill=BEACH["land"])
    for k in range(6):
        d.line([(SPLIT_X + 8 + k * 27, 0), (SPLIT_X + 2 + k * 29, H)], fill=BEACH["land2"])
    d.line([(SPLIT_X, 120), (W, 60)], fill=BEACH["border"], width=1)
    d.line([(SPLIT_X, 40), (W, 150)], fill=BEACH["border"], width=1)
    pts = [(SPLIT_X + 20, 0), (SPLIT_X + 40, 50), (SPLIT_X + 30, 100), (SPLIT_X + 60, H)]
    d.line(pts, fill=BEACH["river"], width=3)
    d.line([(SPLIT_X, 96), (W, 88)], fill=BEACH["road"], width=3)
    d.line([(SPLIT_X + 90, H), (SPLIT_X + 100, 0)], fill=BEACH["road"], width=3)
    d.rectangle((SPLIT_X - 1, 0, SPLIT_X + 1, H), fill=INK)
    return img


def split(c):
    return split_static().copy()


scene("v3_split", shots={"both": (160, 90, 6)})(split)


# --- the pitcher plant ------------------------------------------------------------------------------

PITCH = {"bg": (40, 70, 58), "bg2": (64, 100, 76), "moss": (84, 120, 62), "moss_hi": (120, 156, 80),
         "body": (190, 196, 80), "body_sh": (150, 150, 60), "body_hi": (226, 226, 130), "rib": (170, 70, 60),
         "rim": (150, 50, 50), "rim_hi": (206, 90, 80), "inside": (224, 226, 170), "inside_sh": (196, 198, 140),
         "fluid": (200, 150, 60), "fluid_hi": (236, 196, 100), "wall": (120, 140, 60), "wall_sh": (90, 110, 50)}
PITCHER = (176, 150)            # the pitcher's base (centre bottom)


@lru_cache(maxsize=None)
def pitcher(lid=0):
    """Nepenthes attenboroughii: a big urn of a pitcher with a red ribbed rim and a lid (lid 0-2: wobble)."""
    s = Canvas(56, 80)
    P = PITCH
    s.ell((6, 26, 50, 78), P["body"])                                              # the swollen urn
    s.rect((12, 20, 44, 50), P["body"])
    s.ell((10, 30, 22, 74), P["body_hi"])
    s.ell((38, 34, 50, 76), P["body_sh"])
    for x in (18, 28, 38):                                                         # red streaks
        s.line([(x, 24), (x + 1, 72)], P["rib"])
    for k in range(12):
        s.px((12 + (k * 13) % 34, 30 + (k * 17) % 40), P["rib"])
    s.ell((8, 16, 48, 28), P["rim"])                                               # the peristome
    s.ell((12, 18, 44, 25), (60, 40, 30))                                           # the mouth
    for x in range(10, 48, 3):
        s.line([(x, 16 + (x % 2)), (x, 19)], P["rim_hi"])
    tilt = (-2, 0, 2)[lid]
    s.poly([(10, 14 + tilt), (46, 14 - tilt), (40, 3 - tilt), (16, 3 + tilt)], P["body_sh"])   # the lid
    s.line([(16, 4 + tilt), (40, 4 - tilt)], P["body_hi"])
    s.rect((26, 13, 30, 17), P["body_sh"])
    return s.done()


@lru_cache(maxsize=1)
def pitcher_static():
    img = Image.new("RGB", (W, H), PITCH["bg"])
    vgrad(img, (0, 0, W, 140), PITCH["bg2"], PITCH["bg"], steps=3)
    d = ImageDraw.Draw(img)
    for k in range(7):                                                             # misty mountain trunks
        x = 12 + k * 48
        d.rectangle((x, 0, x + 6, 140), fill=(52, 84, 66))
    blend(img, 1.0, (180, 210, 196), 0.18)
    d.rectangle((0, 140, W, H), fill=PITCH["moss"])
    for k in range(70):
        x, y = rnd("moss", k) * W, 142 + rnd("moss-y", k) * 36
        d.point((x, y), fill=PITCH["moss_hi"])
    d.line([(PITCHER[0] - 30, 152), (PITCHER[0] - 10, 140), (PITCHER[0], 126)], fill=(96, 120, 50), width=2)   # tendril
    for (x, y, s_) in ((60, 150, 0.5), (280, 152, 0.6)):                           # smaller pitchers about
        small = pitcher(1).resize((int(56 * s_), int(80 * s_)), Image.NEAREST)
        img.paste(small, (int(x - small.width / 2), int(y - small.height)), small)
    return img


def pitcher_set(c):
    img = pitcher_static().copy()
    p = pitcher(c.get("lid", 1))
    img.paste(p, (PITCHER[0] - p.width // 2, PITCHER[1] - p.height + 2), p)
    return img


scene("v3_pitcher", shots={"plant": (170, 110, 9), "mouth": (176, 96, 12)})(pitcher_set)


CAVITY = [(96, 26), (224, 26), (236, 60), (240, 110), (228, 150), (200, 168), (120, 168), (92, 150), (80, 110),
          (84, 60)]
FLUID_Y = 134


@lru_cache(maxsize=1)
def pitcher_x_static():
    """The pitcher cut open: a waxy slope down to a pool of digestive fluid."""
    img = Image.new("RGB", (W, H), PITCH["bg"])
    vgrad(img, (0, 0, W, H), PITCH["bg2"], PITCH["bg"], steps=3)
    d = ImageDraw.Draw(img)
    outer = [(x + (12 if x > 160 else -12), y + (8 if y > 100 else -4)) for x, y in CAVITY]
    d.polygon(outer, fill=PITCH["wall"])
    d.polygon(CAVITY, fill=PITCH["inside"])
    d.polygon([(96, 26), (120, 26), (104, 80), (92, 150), (80, 110), (84, 60)], fill=PITCH["inside_sh"])
    for k in range(9):                                                             # the slippery, waxy sheen
        y = 34 + k * 10
        d.line([(110 + k * 2, y), (126 + k * 2, y + 3)], fill=(246, 246, 210))
    d.rectangle((70, 18, 250, 28), fill=PITCH["rim"])                              # the ribbed rim
    for x in range(72, 250, 4):
        d.line([(x, 18), (x, 28)], fill=PITCH["rim_hi"])
    m = mask(lambda mm: mm.polygon(CAVITY, fill=255))
    m[:FLUID_Y] = 0
    a = np.asarray(img).copy()
    a[m > 0] = PITCH["fluid"]
    img = Image.fromarray(a)
    d = ImageDraw.Draw(img)
    d.line([(88, FLUID_Y), (234, FLUID_Y)], fill=PITCH["fluid_hi"])
    pixel.text(img, (160, 6), "INSIDE THE PITCHER", SILK, (220, 230, 190), shadow=INK, anchor="ma")
    return img


def pitcher_x(c):
    img = pitcher_x_static().copy()
    d = ImageDraw.Draw(img)
    for k in range(6):                                                             # the fluid bubbles
        age = (c.t * 0.7 + k / 6) % 1.0
        x = 110 + (k * 23) % 110
        y = 160 - age * 24
        if y > FLUID_Y + 1:
            d.ellipse((x - 1, y - 1, x + 1, y + 1), outline=PITCH["fluid_hi"])
    return img


scene("v3_pitcher_x", shots={"all": (160, 90, 6), "slope": (130, 90, 9)})(pitcher_x)
