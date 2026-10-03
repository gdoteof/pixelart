"""Sprites and printed pages for Verse 4 (gags_v4.py stages them): the caddie with his plea deal, the
golf replay, the hurricane forecast map, the book cover, a pocket-size Trump for the escalator cam.

    uv run python projects/pardon-me/art_v4.py     # -> build/art_v4.png, a sheet of them all
"""
import math
from functools import cache, lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, SILK, Canvas, mix, text_width
from pixelart import pixel

SKIN, SKIN_SH = (226, 176, 136), (190, 136, 104)        # the caddie: an anonymous man
BAG, BAG_SH = (150, 46, 50), (104, 30, 40)
SEA, SEA_SH = (150, 198, 234), (120, 170, 214)
LAND, LAND_SH = (218, 226, 170), (186, 198, 140)
GRASS, GRASS_SH, GREEN, GREEN_HI = (70, 150, 70), (50, 116, 56), (110, 190, 90), (150, 214, 120)
KHAKI, KHAKI_SH = (214, 196, 150), (170, 150, 104)


def stext(img, x, y, s, color, fnt=SILK, anchor="la"):
    """Text straight onto an image with the capitals' top row at y (Silkscreen sets them 4px down)."""
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    w = text_width(s, fnt)
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    c = tuple(C[color] if isinstance(color, str) else color)
    d.text((x, y - (4 if fnt is SILK else 0)), s, font=fnt, fill=c + ((255,) if img.mode == "RGBA" else ()))


# --- line 4: the caddie and his plea deal ------------------------------------------------------

@cache
def caddie(look=-1):
    """A caddie in a striped shirt with the golf bag on his shoulder, facing out, eyes sliding to
    `look` (-1 left, 1 right). 28x54, long in the body so he can stand up behind a desk."""
    s = Canvas(28, 54)
    s.poly([(17, 7), (23, 5), (26, 44), (20, 46)], BAG)                    # the bag, slung behind
    s.poly([(20, 8), (23, 7), (25, 43), (22, 44)], BAG_SH)
    s.rect((16, 6, 24, 9), "steel_sh")
    for x0, x1, head in ((18, 17, "steel"), (20, 21, "steel"), (22, 25, (120, 80, 50))):
        s.line([(x0, 6), (x1, 1)], "steel_sh")                             # club shafts and heads
        s.rect((x1 - 1, 0, x1 + 1, 1), head)
    s.poly([(5, 18), (19, 18), (22, 53), (2, 53)], "white")                # the striped shirt
    for y in range(19, 54, 3):
        s.line([(3, y), (21, y)], "black")
    s.line([(9, 17), (20, 7)], (60, 40, 30), 2)                           # the strap across his chest
    s.line([(9, 17), (20, 7)], (96, 66, 44), 1)
    s.rect((10, 15, 14, 18), SKIN_SH)                                      # neck
    s.ell((6, 4, 18, 17), SKIN)                                            # head
    s.ell((6, 9, 9, 15), SKIN_SH)
    s.ell((5, 1, 19, 8), "white")                                          # cap and its peak
    s.rect((5, 5, 19, 7), "white")
    s.rect((4, 7, 20, 8), "shirt_sh")
    s.line([(9, 2), (15, 2)], (250, 250, 250))
    ex = 9 if look < 0 else 11
    s.pxs([(ex, 11), (ex + 4, 11)], "eye")                                 # side-eye
    s.line([(ex - 1, 10), (ex + 1, 10)], SKIN_SH)
    s.line([(ex + 3, 10), (ex + 5, 10)], SKIN_SH)
    s.line([(10, 14), (13, 14)], "mouth")
    return s.done()


@cache
def plea_deal():
    """The plea agreement he holds up: PLEA / DEAL on a white sheet, signed at the bottom."""
    s = Canvas(28, 22)
    s.rect((0, 0, 27, 21), "white")
    s.rect((0, 19, 27, 21), "paper_sh")
    s.text((3, -2), "PLEA", "black")
    s.text((3, 5), "DEAL", "red")
    s.line([(3, 16), (24, 16)], "steel_sh")
    s.line([(4, 15), (7, 13), (9, 15), (12, 13), (14, 15)], "mk_blue")    # a signature
    s.rect((1, 21, 4, 21), SKIN)                                           # his thumbs
    s.rect((23, 21, 26, 21), SKIN)
    return s.done()


# --- line 4: the golf replay on the right screen -------------------------------------------------

@cache
def golf_set(w, h):
    """The replay's background: sky, fairway, the putting green with the hole and the flag."""
    img = Image.new("RGB", (w, h), GRASS)
    d = ImageDraw.Draw(img)
    pixel.vgrad(img, (0, 0, w, 12), (120, 170, 230), (176, 210, 240), steps=3)
    d.rectangle((0, 12, w, 13), fill=(40, 100, 50))                       # the tree line
    for x in range(0, w, 6):
        d.ellipse((x - 3, 7, x + 4, 14), fill=(40, 100, 50))
    pixel.vgrad(img, (0, 14, w, h), GRASS_SH, GRASS, steps=3)
    d.ellipse((6, 18, w - 4, h + 10), fill=GREEN)
    d.ellipse((14, 22, w - 14, h + 4), fill=GREEN_HI)
    return img


def hole_pos(w, h):
    return w - 22, h - 15


def golf_replay(img, box, t, t_kick, t_end):
    """A replay of the putt: a shoe nudges the ball (at t_kick) and it rolls into the cup.
    Draws into `box` (world pixels)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    clip = golf_set(w, h).copy()
    d = ImageDraw.Draw(clip)
    hx, hy = hole_pos(w, h)
    d.ellipse((hx - 3, hy - 1, hx + 3, hy + 2), fill=INK)                 # the cup and the flag
    d.line([(hx, hy), (hx, hy - 22)], fill=C["white"])
    d.polygon([(hx + 1, hy - 22), (hx + 10, hy - 19), (hx + 1, hy - 16)], fill=C["red"])
    bx0, by = 16, h - 13
    k = (t - t_kick) / max(0.05, t_end - t_kick)
    if k < 0:
        ball = (bx0, by)
    else:
        q = min(1.0, k)
        ball = (bx0 + (hx - bx0) * (1 - (1 - q) ** 2), by + (hy - by) * q)
    in_cup = k >= 1
    # a khaki trouser leg and a two-tone golf shoe slide in from the top left, and give it a tap
    reach = min(1.0, max(0.0, (t - (t_kick - 0.35)) / 0.35))
    back = max(0.0, min(1.0, (t - t_kick - 0.1) / 0.3))
    fx = int(bx0 - 3 - 16 * (1 - reach) - 6 * back)
    fy = by + 1
    leg = [(fx - 20, -1), (fx - 9, -1), (fx - 3, fy - 4), (fx - 12, fy - 3)]
    d.polygon(leg, fill=INK)
    d.polygon([(x + 1, y) for x, y in leg[:2]] + [(x - 1, y + 0) for x, y in leg[2:]], fill=KHAKI)
    d.line([(fx - 18, -1), (fx - 11, fy - 4)], fill=KHAKI_SH)
    d.rounded_rectangle((fx - 14, fy - 5, fx + 2, fy + 1), radius=2, fill=INK)
    d.rounded_rectangle((fx - 13, fy - 4, fx + 1, fy), radius=2, fill=C["white"])
    d.rectangle((fx - 9, fy - 4, fx - 4, fy - 1), fill=(150, 96, 56))
    d.line([(fx - 13, fy), (fx + 1, fy)], fill=(60, 50, 50))
    if not in_cup:
        bx, byy = round(ball[0]), round(ball[1])
        d.ellipse((bx - 2, byy - 2, bx + 2, byy + 2), fill=INK)
        d.ellipse((bx - 1, byy - 1, bx + 1, byy + 1), fill=C["white"])
    if in_cup and int(t * 6) % 2 == 0:
        sparkle_cup(d, hx, hy)
    d.rectangle((1, 1, 47, 8), fill=(16, 20, 34))
    stext(clip, 10, 2, "REPLAY", "gold")
    d.rectangle((3, 3, 6, 6), fill=C["gold"])
    img.paste(clip, (x0, y0))
    return (x0 + fx, y0 + fy)


def sparkle_cup(d, x, y):
    for dx, dy in ((-6, -4), (6, -5), (0, -8)):
        d.point((x + dx, y + dy), fill=C["gold_hi"])


# --- lines 2-4: the hurricane forecast map ------------------------------------------------------

PW, PH = 90, 58
COAST = [(0, 31), (8, 30), (16, 32), (25, 31), (33, 29), (38, 31), (42, 36), (45, 42), (48, 48), (51, 54),
         (55, 55), (58, 50), (59, 43), (58, 36), (56, 30), (58, 24), (62, 18), (66, 13), (71, 9), (76, 9)]
STORM = (79, 45)
TRACK = [(79, 45), (68, 36), (60, 26), (56, 17)]
CONE_R = [2, 5, 8, 10]


def cone_poly():
    """The forecast cone round the track: narrow at the storm, wide at the far end, rounded off."""
    left, right = [], []
    for i, (x, y) in enumerate(TRACK):
        a = TRACK[min(i + 1, len(TRACK) - 1)]
        b = TRACK[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n, dx / n
        r = CONE_R[i]
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
    ex, ey = TRACK[-1]
    ang = math.atan2(TRACK[-1][1] - TRACK[-2][1], TRACK[-1][0] - TRACK[-2][0])
    cap = [(ex + CONE_R[-1] * math.cos(ang + a), ey + CONE_R[-1] * math.sin(ang + a))
           for a in [math.pi / 2 - k * math.pi / 6 for k in range(7)]]
    return left + cap + right[::-1]


@lru_cache(maxsize=1)
def forecast_map():
    """The printed forecast: the Gulf coast and Florida, the cone of uncertainty, the storm. 90x58 RGB."""
    img = Image.new("RGB", (PW, PH), SEA)
    d = ImageDraw.Draw(img)
    for y in range(12, PH, 6):                                            # a little swell in the sea
        for x in range((y // 6) % 2 * 5, PW, 10):
            d.line([(x, y), (x + 2, y)], fill=SEA_SH)
    land = [(0, 0)] + COAST + [(90, 9), (90, 0)]
    d.polygon(land, fill=LAND)
    d.line(COAST, fill=mix(LAND_SH, INK, 0.35))
    for a, b in (((14, 12), (16, 30)), ((30, 10), (31, 28)), ((44, 10), (56, 22))):  # state lines
        for k in range(0, 18, 3):
            p = k / 18
            d.point((round(a[0] + (b[0] - a[0]) * p), round(a[1] + (b[1] - a[1]) * p)), fill=LAND_SH)
    cone = cone_poly()
    d.polygon(cone, fill=(246, 246, 250))
    d.line(cone + cone[:1], fill=(70, 70, 90))
    d.line(TRACK, fill=(40, 40, 52))
    for x, y in TRACK[1:]:
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(40, 40, 52))
    d.rectangle((0, 0, PW - 1, 8), fill=C["white"])                        # the bulletin's header
    d.line([(0, 9), (PW - 1, 9)], fill=(70, 70, 90))
    stext(img, PW // 2, 2, "HURRICANE", C["red"], anchor="ma")
    return img


@lru_cache(maxsize=8)
def storm_icon(frame=0):
    """The hurricane symbol: an eye with two curling arms, in red."""
    s = Canvas(13, 13)
    cx, cy = 6, 6
    for k in range(2):
        a0 = k * math.pi + frame * math.pi / 4
        pts = [(cx + (2 + 0.9 * i) * math.cos(a0 + i * 0.45), cy + (2 + 0.9 * i) * math.sin(a0 + i * 0.45))
               for i in range(5)]
        s.line(pts, "red", 2)
    s.ell((cx - 2, cy - 2, cx + 2, cy + 2), "red")
    s.px((cx, cy), "white")
    return s.done()


# --- line 7: the book ------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def book_cover():
    """A bestseller's cover, 46x52: the title on a white panel, the author's hair under it."""
    w, h = 46, 52
    s = Canvas(w + 2, h + 2)
    s.rect((1, 1, w, h), (24, 22, 30))
    s.rect((1, 1, 4, h), (52, 48, 60))                                     # the spine side
    s.rect((7, 4, w - 3, 31), C["paper"])
    stext(s.img, 26, 6, "THE ART", INK, anchor="ma")
    stext(s.img, 26, 14, "OF THE", INK, anchor="ma")
    stext(s.img, 26, 23, "DEAL", C["red"], anchor="ma")
    s.ell((17, 36, 35, 53), "tskin")                                       # the author, beaming
    s.rect((22, 41, 25, 42), "tring")
    s.rect((29, 41, 32, 42), "tring")
    s.ell((15, 33, 34, 41), "thair")
    s.poly([(24, 33), (38, 35), (39, 39), (31, 40)], "thair")
    s.line([(18, 35), (33, 34)], "thair_hi")
    s.pxs([(23, 42), (30, 42)], INK)
    s.line([(24, 48), (28, 48)], "mouth")
    return s.done()


# --- line 9: the escalator cam ---------------------------------------------------------------------

@lru_cache(maxsize=4)
def lobby(w, h):
    """The UN lobby behind the escalator: pale stone wall, a window band, the floor."""
    img = Image.new("RGB", (w, h), (214, 206, 190))
    pixel.vgrad(img, (0, 0, w, h - 6), (196, 190, 178), (226, 220, 206), steps=4)
    d = ImageDraw.Draw(img)
    for x in range(4, w, 14):
        d.rectangle((x, 9, x + 9, 20), fill=(150, 184, 210))
        d.line([(x, 9), (x + 9, 9)], fill=(240, 240, 244))
    d.rectangle((0, h - 6, w, h), fill=(150, 130, 110))
    d.line([(0, h - 6), (w, h - 6)], fill=(120, 100, 84))
    return img


@lru_cache(maxsize=1)
def out_of_order():
    """OUT OF / ORDER, white on red, on a little stand."""
    s = Canvas(38, 26)
    s.rect((1, 1, 36, 17), "red")
    s.rect((1, 15, 36, 17), "red_sh")
    stext(s.img, 19, 3, "OUT OF", "white", anchor="ma")
    stext(s.img, 19, 10, "ORDER", "white", anchor="ma")
    s.rect((17, 18, 20, 23), "steel_sh")
    s.rect((12, 23, 25, 24), "steel_sh")
    return s.done()


# --- line 9: a pocket Trump for the escalator cam ---------------------------------------------------

@cache
def mini_trump(step=0, lurch=False):
    """Trump at a few pixels high, facing right: `step` 0/1 swings the legs, `lurch` pitches him forward
    with his arms out (the escalator just stopped)."""
    s = Canvas(16, 26)
    a = (-1, 1) if step else (0, 0)
    s.rect((4 + a[0], 17, 6 + a[0], 22), "suit")                           # legs
    s.rect((8 + a[1], 17, 10 + a[1], 22), "suit_sh")
    s.rect((3 + a[0], 22, 7 + a[0], 23), "shoe")
    s.rect((8 + a[1], 22, 12 + a[1], 23), "shoe")
    s.rect((3, 9, 11, 18), "suit")                                         # jacket, shirt, the long tie
    s.poly([(6, 9), (9, 9), (7, 12)], "shirt")
    s.rect((7, 10, 8, 17), "tie")
    if lurch:
        s.line([(10, 11), (14, 8)], "suit", 2)
        s.rect((14, 6, 15, 7), "tskin")
        s.line([(4, 11), (0, 8)], "suit_sh", 2)
    else:
        s.rect((10, 10, 11, 15), "suit_sh")
    s.ell((3, 2, 12, 10), "tskin")                                         # head
    s.rect((8, 5, 10, 5), "tring")
    s.px((9, 5), "eye")
    s.line([(9, 8), (10, 8)], "mouth")
    s.ell((2, 0, 11, 5), "thair")                                          # the swoop
    s.poly([(6, 0), (11, 0), (14, 2), (12, 4), (8, 3)], "thair")
    s.line([(4, 1), (9, 0)], "thair_hi")
    img = s.done()
    if lurch:
        img = img.rotate(-20, resample=Image.NEAREST, expand=True, center=(8, 24))
    return img


if __name__ == "__main__":
    from engine import ROOT
    clip = Image.new("RGB", (85, 49))
    golf_replay(clip, (0, 0, 85, 49), 1.0, 0.8, 1.3)
    clip2 = Image.new("RGB", (85, 49))
    golf_replay(clip2, (0, 0, 85, 49), 0.6, 0.8, 1.3)
    m = forecast_map().copy()
    m.paste(storm_icon(1), (STORM[0] - 6, STORM[1] - 6), storm_icon(1))
    items = [caddie(), plea_deal(), clip2, clip, m, book_cover(), mini_trump(), mini_trump(1), mini_trump(0, True),
             lobby(85, 49), out_of_order()]
    sheet = Image.new("RGB", (sum(i.width + 6 for i in items) + 6, 70), (196, 150, 70))
    x = 6
    for i in items:
        sheet.paste(i, (x, 64 - i.height), i if i.mode == "RGBA" else None)
        x += i.width + 6
    out = ROOT / "build" / "art_v4.png"
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)
    print(out)
