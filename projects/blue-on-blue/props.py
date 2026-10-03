"""Props and inset pictures for the gags: what the hosts hold up and wear, what lands on the desk, and the
pictures that slide into the inset between them (phones, posts, Trump's day).

Every prop is a cached RGBA sprite drawn with the video's palette and outlined in ink; inset pictures are
84x64 RGB images (`INSET_SIZE`). Text is Silkscreen (5 px capitals); keep it to a few words so it reads.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from characters import figure
from engine import C, INK, PRESS, SILK, Canvas, mirror, scaled  # noqa: F401
from pixelart import fx, pixel

INSET_SIZE = (84, 64)


def _text(f, xy, s, col="mk_black", anchor="la"):
    """Silkscreen on a prop canvas, glyph tops at y (its glyphs sit 4 px down their box)."""
    x, y = xy
    f.d.text((x, y - 4), s, font=SILK, fill=f.c(col), anchor=anchor)


def text(d, xy, s, col="mk_black", anchor="la", fnt=SILK):
    """Silkscreen (or Press Start) on an ImageDraw, glyph tops at y."""
    x, y = xy
    d.text((x, y - (4 if fnt is SILK else 0)), s, font=fnt, fill=C[col] if isinstance(col, str) else col, anchor=anchor)


def text_w(s, fnt=SILK):
    return pixel.text_width(s, fnt)


def signature(d, x0, y, x1, col="mk_black"):
    """Trump's signature: a jagged seismograph of a scrawl."""
    pts, x, k = [], x0, 0
    while x <= x1:
        pts.append((x, y + (-3 if k % 2 else 2) + (k % 3 == 0)))
        x += 2
        k += 1
    d.line(pts, fill=C[col])


# --- tiny people, for the insets --------------------------------------------------------------------------

LOOK = {"trump": ("tskin", "thair", "suit", "tie"), "newsom": ("nskin", "nhair", "blazer", "shirt"),
        "mamdani": ("mskin", "mhair", "msuit", "mtie"), "caddie": ("nskin_hi", "white", "white", "green"),
        "melania": ("mel_skin", "mel_hair", "white", "white"), "kimberly": ("nskin", "nhair_sh", "red", "red"),
        "junior": ("nskin", "mhair", "suit", "suit_sh")}


def mini(d, x, y, who, arms="down", facing=1, mouth=False):
    """A tiny person (about 16 px tall), feet at (x, y)."""
    skin, hair, body, tie = (C[k] for k in LOOK[who])
    big = who == "trump"
    w = 4 if big else 3
    d.rectangle((x - 2, y - 5, x - 1, y), fill=C["ink"]); d.rectangle((x + 1, y - 5, x + 2, y), fill=C["ink"])   # legs
    d.rectangle((x - w, y - 12, x + w, y - 5), fill=C["ink"])
    d.rectangle((x - w + 1, y - 11, x + w - 1, y - 6), fill=body)
    if who in ("trump", "mamdani", "junior"):
        d.line([(x, y - 11), (x, y - 7 if big else y - 8)], fill=tie)
    if who == "caddie":
        d.line([(x - 2, y - 9), (x + 2, y - 9)], fill=C["green"])
    if who in ("melania", "kimberly"):                                    # a dress
        d.polygon([(x - w - 1, y - 4), (x + w + 1, y - 4), (x + w - 1, y - 11), (x - w + 1, y - 11)], fill=body)
    d.ellipse((x - 3, y - 18, x + 3, y - 12), fill=C["ink"])
    d.ellipse((x - 2, y - 17, x + 2, y - 13), fill=skin)
    if who == "trump":
        d.rectangle((x - 3, y - 19, x + 3 + facing, y - 17), fill=hair)
    elif who in ("melania", "kimberly"):
        d.rectangle((x - 3, y - 18, x + 3, y - 16), fill=hair); d.rectangle((x - 3 * facing, y - 16, x - 2 * facing, y - 12), fill=hair)
    elif who == "caddie":
        d.rectangle((x - 3, y - 19, x + 2, y - 17), fill=C["white"]); d.line([(x + 2 * facing, y - 17), (x + 4 * facing, y - 17)], fill=C["white"])
    else:
        d.rectangle((x - 3, y - 19, x + 2, y - 16), fill=hair)
        if who in ("mamdani", "junior"):
            d.line([(x - 2, y - 13), (x + 2, y - 13)], fill=C["mbeard"])
    d.point((x + facing, y - 15), fill=C["ink"])
    if mouth:
        d.point((x + 2 * facing, y - 13), fill=C["mouth"])
    if arms == "up":
        d.line([(x - w, y - 11), (x - w - 3, y - 15)], fill=body); d.line([(x + w, y - 11), (x + w + 3, y - 15)], fill=body)
    elif arms == "out":
        d.line([(x + w * facing, y - 10), (x + (w + 4) * facing, y - 10)], fill=body)
    elif arms == "hug":
        d.line([(x + w * facing, y - 10), (x + (w + 3) * facing, y - 9)], fill=body)


def mini_head(d, x, y, who, mood="smile"):
    """A tiny face (9x9), for avatars: centre (x, y)."""
    skin, hair = C[LOOK[who][0]], C[LOOK[who][1]]
    d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=C["ink"])
    d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=skin)
    if who == "trump":
        d.rectangle((x - 5, y - 6, x + 5, y - 3), fill=hair); d.rectangle((x + 2, y - 3, x + 5, y - 2), fill=hair)
        d.line([(x - 2, y - 1), (x - 1, y - 1)], fill=C["tring"]); d.line([(x + 1, y - 1), (x + 2, y - 1)], fill=C["tring"])
    elif who in ("melania", "kimberly"):
        d.rectangle((x - 5, y - 6, x + 5, y - 3), fill=hair); d.rectangle((x - 5, y - 3, x - 3, y + 5), fill=hair)
        d.rectangle((x + 3, y - 3, x + 5, y + 5), fill=hair)
    else:
        d.rectangle((x - 5, y - 6, x + 4, y - 3), fill=hair)
        if who in ("mamdani", "junior"):
            d.arc((x - 4, y - 3, x + 4, y + 5), 20, 160, fill=C["mbeard"])
    d.point((x - 2, y), fill=C["ink"]); d.point((x + 2, y), fill=C["ink"])
    if mood == "smile":
        d.line([(x - 1, y + 2), (x + 1, y + 2)], fill=C["mouth"])
    elif mood == "o":
        d.point((x, y + 2), fill=C["mouth"])


# --- things held and worn ----------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def phone_held(lit=True):
    """A phone held up to the camera, screen out."""
    f = Canvas(14, 22)
    f.rect((0, 0, 13, 21), "phone")
    f.rect((1, 2, 12, 18), "screen_hi" if lit else "phone_scr")
    f.line([(5, 1), (8, 1)], "phone_hi")
    return f.done()


@lru_cache(maxsize=None)
def placard(*lines, w=46, h=22, bg="red", fg="white"):
    """A protest sign or a campaign placard on a stick."""
    w = max(w, max(text_w(s) for s in lines) + 8)
    f = Canvas(w, h + 9)
    f.rect((0, 0, w - 1, h - 1), bg)
    f.line([(1, 1), (w - 2, 1)], "white" if bg != "white" else "paper_sh")
    f.rect((w // 2 - 1, h, w // 2, h + 8), "slat")
    y = (h - 7 * len(lines)) // 2 + 1
    for s in lines:
        _text(f, (w // 2, y), s, fg, anchor="ma")
        y += 7
    return f.done()


@lru_cache(maxsize=None)
def big_check():
    """The novelty cheque: a billion dollars, made out to Zohran, memo: housing."""
    w, h = 82, 32
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), "money")
    f.rect((2, 2, w - 3, h - 3), (236, 248, 228))
    _text(f, (4, 4), "PAY TO ZOHRAN", "mk_black")
    f.rect((4, 11, w - 5, 18), "white"); _text(f, (w // 2, 12), "$1 BILLION", "mk_green", anchor="ma")
    _text(f, (4, 22), "HOUSING", "mk_blue")
    pts, x, k = [], 50, 0
    while x <= w - 6:
        pts.append((x, 25 + (-2 if k % 2 else 1)))
        x += 2
        k += 1
    f.line(pts, "mk_black")
    return f.done()


@lru_cache(maxsize=None)
def folder(*lines, w=40, h=28, cover="folder"):
    """A folder held open to the camera: a page with a word or two."""
    w = max(w, max(text_w(s) for s in lines) + 12)
    h = max(h, 7 * len(lines) + 12)
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 1), cover)
    f.line([(1, 1), (w - 2, 1)], "folder_hi")
    f.rect((3, 3, w - 4, h - 4), "paper")
    y = (h - 7 * len(lines)) // 2 + 1
    for s in lines:
        _text(f, (w // 2, y), s, anchor="ma")
        y += 7
    return f.done()


@lru_cache(maxsize=None)
def lawsuit():
    """TRUMP v. ZOHRAN, slapped on the desk."""
    f = Canvas(50, 21)
    f.rect((0, 0, 49, 20), "paper")
    f.rect((0, 0, 49, 2), "mk_black")
    _text(f, (25, 5), "TRUMP V.", anchor="ma"); _text(f, (25, 12), "ZOHRAN", "mk_red", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def crown(word="RENT FREE"):
    """A gold crown with a sash across it, to sit on a head (40 wide, drawn facing right)."""
    f = Canvas(40, 20)
    f.poly([(9, 18), (31, 18), (33, 6), (27, 12), (21, 3), (15, 12), (8, 5)], "gold")
    f.line([(10, 16), (30, 16)], "gold_sh")
    for x in (8, 21, 33):
        f.ell((x - 2, 2 if x == 21 else 4, x + 2, 6 if x == 21 else 8), "red")
    f.px((20, 4), "red_hi")
    return f.done()


@lru_cache(maxsize=None)
def cap(word="GAVIN", color="red"):
    """A red ball cap, sitting on a head (40 wide, facing right): the crown, the brim out front, a word."""
    f = Canvas(40, 16)
    f.ell((5, 2, 33, 18), color)
    f.rect((5, 10, 33, 13), color)
    f.poly([(28, 11), (39, 12), (39, 14), (27, 14)], "red_sh" if color == "red" else color)
    f.line([(7, 13), (32, 13)], "red_sh" if color == "red" else color)
    f.px((18, 2), "red_hi")
    _text(f, (20, 6), word, "white", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def nightcap():
    """A striped nightcap with a bobble, flopping back (40 wide, facing right)."""
    f = Canvas(44, 22)
    f.poly([(8, 14), (34, 14), (30, 6), (18, 2), (6, 6), (2, 14)], "blue")
    f.poly([(6, 6), (2, 8), (0, 16), (4, 15)], "blue")
    for x in range(8, 32, 6):
        f.line([(x, 13), (x + 3, 5)], "white")
    f.rect((6, 13, 35, 16), "white")
    f.ell((0, 15, 5, 20), "white")
    return f.done()


@lru_cache(maxsize=None)
def trump_wig():
    """The Temu Trump: a yellow swoop to sit on Newsom's head (40 wide, facing right), price tag on."""
    f = Canvas(48, 22)
    f.poly([(4, 18), (3, 10), (8, 4), (17, 1), (30, 1), (39, 4), (42, 9), (41, 13), (36, 14), (33, 11),
            (26, 12), (18, 13), (12, 15), (8, 19)], "thair")
    f.line([(8, 9), (16, 4), (28, 3), (38, 6)], "thair_hi"); f.line([(10, 13), (20, 9), (33, 9)], "thair_hi")
    f.line([(14, 14), (24, 12), (32, 11)], "thair_dk")
    f.poly([(34, 12), (36, 14), (40, 13), (41, 10)], "thair_sh")
    return f.done()


@lru_cache(maxsize=None)
def price_tag(s="$1.99"):
    w = text_w(s) + 8
    f = Canvas(w, 9)
    f.poly([(3, 0), (w - 1, 0), (w - 1, 8), (3, 8), (0, 4)], "orange")
    f.px((3, 4), "white")
    _text(f, (5, 2), s, "white")
    return f.done()


@lru_cache(maxsize=None)
def wine_glass():
    f = Canvas(9, 14)
    f.ell((0, 0, 8, 7), "glass"); f.ell((1, 3, 7, 7), "wine")
    f.line([(4, 7), (4, 11)], "glass"); f.line([(1, 12), (7, 12)], "glass")
    f.px((2, 1), "white")
    return f.done()


@lru_cache(maxsize=None)
def ice_block(word="RENT"):
    """The rent, frozen solid."""
    f = Canvas(30, 22)
    f.rect((0, 2, 29, 21), "ice")
    f.poly([(0, 2), (4, 0), (29, 0), (29, 2)], "ice_hi")
    f.rect((5, 7, 24, 16), "paper")
    _text(f, (15, 9), word, "mk_red", anchor="ma")
    f.line([(2, 4), (8, 4)], "ice_hi"); f.line([(22, 18), (27, 18)], "ice_sh"); f.line([(26, 4), (26, 12)], "ice_sh")
    return f.done()


@lru_cache(maxsize=None)
def rubber_duck():
    """The lame duck: a rubber duck with a bandage and a crutch."""
    f = Canvas(24, 20)
    f.ell((2, 8, 18, 19), "duck")
    f.ell((10, 1, 20, 11), "duck")
    f.poly([(19, 5), (24, 6), (19, 8)], "beak")
    f.px((16, 4), "ink")
    f.line([(4, 12), (14, 12)], "duck_sh")
    f.rect((11, 2, 19, 3), "white"); f.px((14, 2), "red")                 # the bandage round its head
    f.line([(1, 19), (5, 7)], "steel"); f.line([(3, 7), (7, 7)], "steel")   # the crutch
    return f.done()


@lru_cache(maxsize=None)
def desk_box():
    """A cardboard box of desk things: the bear, a plant, a mug."""
    f = Canvas(34, 26)
    f.poly([(6, 0), (14, 6), (8, 10)], "plant")
    f.poly([(10, 2), (12, 10), (16, 4)], "plant_hi")
    f.rect((18, 2, 24, 10), "mug")
    f.ell((24, 4, 30, 10), "bear")
    f.rect((0, 9, 33, 25), "box")
    f.poly([(0, 9), (4, 5), (12, 9)], "box_sh"); f.poly([(33, 9), (29, 5), (21, 9)], "box_sh")
    _text(f, (17, 15), "GAVIN", "box_sh", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def heart(r=4, broken=0.0):
    """A heart; `broken` > 0 splits it down the middle (the halves drift apart)."""
    w = 2 * r + 3
    f = Canvas(w + 2 * int(broken * 4), 2 * r + 3)
    off = int(broken * 4)
    for side in (0, 1):
        dx = 0 if side == 0 else 2 * off
        g = Canvas(w, 2 * r + 3)
        g.ell((0, 0, r + 1, r + 1), "mk_red"); g.ell((r, 0, 2 * r + 1, r + 1), "mk_red")
        g.poly([(0, r // 2 + 1), (2 * r + 1, r // 2 + 1), (r, 2 * r)], "mk_red")
        g.px((1, 1), "red_hi")
        if broken:
            half = (0, 0, r, 2 * r + 2) if side == 1 else (r + 1, 0, w, 2 * r + 2)
            g.d.rectangle(half, fill=(0, 0, 0, 0))
            g.d.line([(r, 0), (r - 1, r // 2), (r + 1, r), (r, 2 * r)], fill=(0, 0, 0, 0))
        f.img.alpha_composite(g.img, (dx, 0))
        if not broken:
            break
    return f.done()


@lru_cache(maxsize=None)
def note(kind=0):
    f = Canvas(7, 9)
    f.ell((0, 5, 4, 8), "white"); f.line([(4, 0), (4, 6)], "white")
    if kind:
        f.line([(4, 0), (6, 2)], "white")
    return f.done()


@lru_cache(maxsize=None)
def rain_cloud():
    f = Canvas(30, 12)
    f.ell((0, 3, 12, 11), "steel_sh"); f.ell((8, 0, 22, 11), "steel_sh"); f.ell((18, 3, 29, 11), "steel_sh")
    f.line([(4, 5), (10, 3)], "steel")
    return f.done()


@lru_cache(maxsize=None)
def tiny_hand():
    """Trump's hand, reaching in: a huge navy sleeve, a white cuff, a very small orange hand."""
    f = Canvas(46, 12)
    f.rect((10, 1, 45, 10), "suit"); f.line([(10, 2), (45, 2)], "suit_hi")
    f.rect((6, 2, 9, 9), "shirt")
    f.ell((1, 3, 6, 8), "tskin"); f.px((0, 5), "tskin")
    return f.done()


@lru_cache(maxsize=None)
def soldier():
    """A tiny Guardsman in a vest that says FEDS."""
    f = Canvas(10, 18)
    f.ell((2, 0, 8, 5), (90, 110, 70))
    f.ell((3, 3, 7, 8), "nskin")
    f.rect((2, 8, 8, 14), (90, 110, 70)); f.rect((2, 9, 8, 12), (40, 46, 56))
    f.rect((2, 14, 4, 17), "ink"); f.rect((6, 14, 8, 17), "ink")
    return f.done()


@lru_cache(maxsize=None)
def calendar(month="JAN", year="2027"):
    f = Canvas(28, 30)
    f.rect((0, 3, 27, 29), "paper")
    f.rect((0, 3, 27, 11), "red")
    f.pxs([(6, 1), (6, 2), (21, 1), (21, 2)], "steel_sh")
    _text(f, (14, 5), month, "white", anchor="ma")
    _text(f, (14, 15), year, "mk_black", anchor="ma")
    for i in range(3):
        f.line([(4, 23 + 2 * i), (23, 23 + 2 * i)], "paper_ln")
    return f.done()


@lru_cache(maxsize=None)
def l_sticker():
    """The L, for the forehead."""
    f = Canvas(10, 12)
    f.rect((0, 0, 9, 11), "red")
    f.rect((2, 2, 4, 9), "white"); f.rect((2, 8, 7, 9), "white")
    return f.done()


@lru_cache(maxsize=None)
def trotsky_filter():
    """The TikTok filter on Mamdani's face: round wire specs and a pointed goatee (40 wide, facing right)."""
    f = Canvas(40, 40)
    for cx in (19, 29):
        f.d.ellipse((cx - 3, 18, cx + 3, 24), outline=f.c("steel"))
    f.line([(22, 21), (26, 21)], "steel"); f.line([(10, 20), (16, 21)], "steel")
    f.poly([(22, 34), (33, 34), (29, 43), (26, 44)], "mhair")                # the goatee
    f.line([(24, 30), (33, 30)], "mhair")
    return f.done()


# --- inset pictures (84x64) ---------------------------------------------------------------------------------

def canvas(bg):
    img = Image.new("RGB", INSET_SIZE, C[bg] if isinstance(bg, str) else bg)
    return img, ImageDraw.Draw(img)


def bubble_left(d, x, y, s, fill="imsg_grey", fg="mk_black", w=None):
    w = w or text_w(s) + 6
    d.rounded_rectangle((x, y, x + w, y + 9), 3, fill=C[fill])
    text(d, (x + 3, y + 2), s, fg)
    return w


def bubble_right(d, x1, y, s, fill="imsg", fg="white"):
    w = text_w(s) + 6
    d.rounded_rectangle((x1 - w, y, x1, y + 9), 3, fill=C[fill])
    text(d, (x1 - w + 3, y + 2), s, fg)


def imessage(msgs, contact="DONNIE <3", typing=False):
    """A text thread on a phone: [(side, text)], "l" from the contact, "r" from the phone's owner."""
    img, d = canvas("white")
    d.rectangle((0, 0, 84, 11), fill=C["imsg_grey"])
    mini_head(d, 8, 6, "trump")
    text(d, (16, 3), contact, "mk_black")
    y = 15
    for side, s in msgs:
        if side == "l":
            bubble_left(d, 3, y, s)
        else:
            bubble_right(d, 80, y, s)
        y += 12
    if typing:
        d.rounded_rectangle((3, y, 21, y + 9), 3, fill=C["imsg_grey"])
        for k in range(3):
            d.ellipse((6 + 4 * k, y + 3, 8 + 4 * k, y + 5), fill=C["dim"])
    return img


def truth_post(lines, likes="88.2K", strike=None, fix=None):
    """A post on Truth Social: the avatar, the name, the text in capitals. `strike` is a line index to cross
    out, and `fix` a word written under it in red marker."""
    img, d = canvas("white")
    d.rectangle((0, 0, 84, 9), fill=C["truth"])
    text(d, (3, 2), "TRUTH SOCIAL", "white")
    mini_head(d, 7, 16, "trump")
    text(d, (14, 14), "DONALD TRUMP", "mk_black")
    y = 25
    for i, s in enumerate(lines):
        text(d, (3, y), s, "mk_black")
        if strike == i:
            d.line([(2, y + 3), (4 + text_w(s), y + 1)], fill=C["mk_red"], width=2)
        y += 8
    if fix:
        text(d, (3, y), fix, "mk_red")
    text(d, (3, 57), "<3 " + likes, "dim")
    return img


def tiktok(t, filt=False, hearts="2.1M"):
    """Mamdani's campaign TikTok: a vertical video in the middle, the counters down the right."""
    img, d = canvas("tiktok")
    vx0, vx1 = 22, 62
    d.rectangle((vx0, 0, vx1, 64), fill=(40, 60, 100))
    d.rectangle((vx0, 44, vx1, 64), fill=(60, 64, 80))                    # a subway platform, roughly
    d.line([(vx0, 44), (vx1, 44)], fill=C["duck"])
    bob = int(2 * math.sin(t * 9))
    body, _ = figure("mamdani", arms="point" if int(t * 2) % 2 else "palm", facing=1, mouth="grin", eyes="open",
                     brows="up", phones=False)
    crop = body.crop((10, 0, 74, 64))
    img.paste(crop, (vx0 - 10, 6 + bob), crop)
    if filt:
        g = trotsky_filter()
        img.paste(g, (vx0 - 10 + 18, 6 + bob + 5), g)
        d.rectangle((vx0 + 2, 2, vx1 - 2, 9), fill=C["tt_pink"])
        text(d, ((vx0 + vx1) // 2, 3), "TROTSKY", "white", anchor="ma")
    for k, (icon, s) in enumerate((("<3", hearts), ("..", "94K"), (">", "12K"))):
        text(d, (73, 6 + 14 * k), icon, "white", anchor="ma")
        text(d, (73, 12 + 14 * k), s, "white", anchor="ma")
    text(d, (23, 55), "@ZOHRAN", "white")
    d.line([(0, 63), (int(84 * (t % 1.0)), 63)], fill=C["tt_pink"])
    return img


def scene(sky="sky", ground="grass", horizon=44):
    img, d = canvas(sky)
    d.rectangle((0, horizon, 84, 64), fill=C[ground] if isinstance(ground, str) else ground)
    return img, d


def golf(t):
    """Trump on the course, telling his caddie he's handsome."""
    img, d = scene()
    d.ellipse((50, 46, 82, 58), fill=(120, 190, 100))
    d.line([(72, 36), (72, 52)], fill=C["white"]); d.polygon([(72, 36), (79, 39), (72, 42)], fill=C["red"])
    d.rectangle((6, 34, 26, 44), fill=C["white"]); d.rectangle((8, 30, 24, 33), fill=C["white"])    # the cart
    d.ellipse((7, 42, 12, 47), fill=C["ink"]); d.ellipse((20, 42, 25, 47), fill=C["ink"])
    mini(d, 36, 54, "trump", arms="out")
    mini(d, 50, 54, "caddie", facing=-1)
    if t > 0.1:
        fx.bubble(img, 36, 24, ["HANDSOME!"], tail=(37, 34), fnt=SILK, fill=C["white"], ink=INK, pad=2, line_h=7,
                  text_dy=-3)
    if t > 0.5:
        d.point((49, 39), fill=C["flush"]); d.point((51, 39), fill=C["flush"])
    return img


def stood_up(t):
    """The planet, alone at a table for two, checking the time."""
    img, d = canvas((60, 40, 50))
    d.rectangle((0, 40, 84, 64), fill=(90, 50, 50))
    d.ellipse((14, 40, 70, 52), fill=C["white"]); d.rectangle((14, 46, 70, 64), fill=C["white"])
    d.line([(42, 30), (42, 40)], fill=C["white"]); d.point((42, 28 - int(t * 4) % 2), fill=C["orange"])
    d.ellipse((4, 14, 30, 40), fill=C["blue"])                             # the Earth, in the chair
    d.polygon([(10, 20), (18, 18), (20, 26), (12, 30)], fill=C["green"]); d.polygon([(22, 30), (28, 26), (26, 36)], fill=C["green"])
    d.point((13, 25), fill=C["ink"]); d.point((20, 25), fill=C["ink"])
    d.arc((12, 28, 22, 34), 200, 340, fill=C["ink"])
    d.rectangle((58, 24, 80, 40), fill=(80, 50, 40))                      # the empty chair
    text(d, (69, 8), "TABLE", "gold_hi", anchor="ma"); text(d, (69, 15), "FOR 2", "gold_hi", anchor="ma")
    if int(t * 3) % 2:
        text(d, (17, 6), "...", "white", anchor="ma")
    return img


def lobby(t):
    """Trump in Zohran's lobby with flowers."""
    img, d = canvas((230, 220, 196))
    d.rectangle((0, 46, 84, 64), fill=(150, 120, 90))
    for x in range(4, 84, 20):
        d.rectangle((x, 6, x + 6, 46), fill=(250, 246, 236)); d.line([(x + 6, 6), (x + 6, 46)], fill=(200, 190, 170))
    d.rectangle((50, 16, 76, 46), fill=(90, 60, 40)); d.line([(63, 16), (63, 46)], fill=C["ink"])   # the door
    mini(d, 34, 58, "trump", arms="out")
    for k in range(3):
        d.ellipse((40 + 3 * k, 45 - (k % 2) * 2, 43 + 3 * k, 48 - (k % 2) * 2), fill=C["red"])
    d.line([(41, 50), (44, 48)], fill=C["green"])
    if t > 0.1:
        text(d, (42, 2), "CITY HALL", "mk_black", anchor="ma")
    return img


@lru_cache(maxsize=None)
def mansion_base():
    img, d = scene(horizon=48)
    d.polygon([(10, 22), (42, 10), (74, 22)], fill=C["white"])           # the roof
    d.line([(10, 22), (42, 10), (74, 22)], fill=C["ink"])
    d.rectangle((12, 22, 72, 50), fill=(250, 244, 220))
    d.rectangle((12, 22, 72, 50), outline=C["ink"])
    for x in range(16, 70, 10):
        d.rectangle((x, 26, x + 5, 32), fill=C["bus_win"], outline=C["ink"])
        d.rectangle((x, 38, x + 5, 44), fill=C["bus_win"], outline=C["ink"])
    d.rectangle((38, 40, 46, 50), fill=C["slat_dk"])
    d.line([(10, 36), (74, 36)], fill=C["ink"])                           # the porch rail
    return img


def mansion(t, gold=0.0, boxes=0, who="trump"):
    """Gracie Mansion: Trump on the tour, gilding it (gold 0-1), or Zohran moving in with boxes."""
    img = mansion_base().copy()
    d = ImageDraw.Draw(img)
    if gold > 0:
        x1 = 12 + int(60 * min(1.0, gold))
        d.rectangle((12, 22, x1, 35), fill=C["gold"]); d.rectangle((12, 37, x1, 50), fill=C["gold_sh"])
        d.line([(12, 22), (x1, 22)], fill=C["gold_hi"])
        mini(d, x1 + 3, 58, "trump", arms="up")
        d.rectangle((x1 + 4, 36, x1 + 8, 40), fill=C["gold_hi"])
    elif who == "mamdani":
        mini(d, 30, 60, "mamdani", arms="out")
        for k in range(boxes):
            d.rectangle((52 + 8 * (k % 3), 52 - 6 * (k // 3), 58 + 8 * (k % 3), 57 - 6 * (k // 3)), fill=C["box"], outline=C["ink"])
    else:
        mini(d, 28, 60, "trump", arms="out")
    return img


def skyline(t, claimed=0):
    """Manhattan at night; `claimed` towers have TRUMP on them in gold."""
    img, d = canvas("night")
    for x, y in ((6, 6), (30, 3), (70, 9), (58, 4), (18, 12)):
        d.point((x, y), fill=C["white"])
    towers = [(2, 30, 12), (14, 18, 10), (26, 26, 9), (36, 8, 8), (45, 22, 10), (56, 14, 9), (66, 28, 8), (75, 20, 9)]
    for i, (x, top, w) in enumerate(towers):
        d.rectangle((x, top, x + w, 64), fill=C["city"], outline=C["ink"])
        for wy in range(top + 4, 60, 5):
            for wx in range(x + 2, x + w - 1, 3):
                if (wx * 7 + wy * 3 + i) % 5 != 0:
                    d.point((wx, wy), fill=C["city_win"])
        if i < claimed:
            d.rectangle((x + 1, top + 1, x + w - 1, top + 6), fill=C["gold"])
            text(d, (x + w // 2 + 1, top + 1), "T", "ink", anchor="ma")
    d.line([(39, 8), (39, 2)], fill=C["steel"])                          # the Empire State's mast
    return img


def tarmac(t):
    """LAX, January 2025: the hug on the tarmac. Trump doesn't hug back."""
    img, d = scene(sky="sky_hi", ground="road", horizon=46)
    d.polygon([(46, 22), (84, 18), (84, 34), (50, 34)], fill=C["white"]); d.line([(48, 28), (84, 25)], fill=C["blue"])
    d.polygon([(40, 34), (52, 34), (52, 50), (40, 50)], fill=C["steel"])  # the stairs
    for y in range(36, 50, 3):
        d.line([(40, y), (52, y)], fill=C["steel_sh"])
    mini(d, 28, 58, "newsom", arms="hug")
    mini(d, 33, 58, "trump", facing=-1)
    if t > 0.2:
        d.polygon([(22, 36), (24, 34), (26, 36), (24, 39)], fill=C["red"])
    text(d, (4, 3), "LAX, 2025", "mk_black")
    return img


def relationship(t):
    """IT'S OFFICIAL: in a relationship with Donald J. Trump."""
    img, d = canvas("white")
    d.rectangle((0, 0, 84, 10), fill=C["blue_sh"])
    text(d, (42, 3), "IT'S OFFICIAL", "white", anchor="ma")
    mini_head(d, 26, 21, "mamdani")
    mini_head(d, 58, 21, "trump")
    d.polygon([(38, 19), (40, 17), (42, 19), (44, 17), (46, 19), (42, 24)], fill=C["red"])
    text(d, (42, 31), "IN A", "mk_black", anchor="ma")
    text(d, (42, 38), "RELATIONSHIP", "mk_black", anchor="ma")
    text(d, (42, 45), "WITH DONALD", "mk_blue", anchor="ma")
    text(d, (3, 56), "<3 2.4M", "dim")
    return img


def all_caps(t):
    """The governor's press office, posting like the president."""
    img, d = canvas("white")
    d.rectangle((0, 0, 84, 9), fill=C["mk_black"])
    text(d, (3, 2), "@GOVPRESS", "white")
    lines = ["NEWSOM IS THE", "GREATEST GOV", "EVER!! TRUMP", "IS SAD. THANK", "YOU FOR YOUR", "ATTENTION!!"]
    n = min(len(lines), int(t * 12) + 1)
    for i, s in enumerate(lines[:n]):
        text(d, (3, 13 + 8 * i), s, "mk_black")
    return img


def merch(t):
    """The governor's merch store: a red cap that says what it says."""
    img, d = canvas((236, 236, 240))
    d.rectangle((0, 0, 84, 9), fill=C["red"])
    text(d, (42, 2), "PATRIOT SHOP", "white", anchor="ma")
    d.ellipse((8, 12, 74, 62), fill=C["red"]); d.rectangle((8, 38, 74, 50), fill=C["red"])
    d.polygon([(64, 44), (84, 48), (84, 54), (62, 52)], fill=C["red_sh"])
    for i, s in enumerate(("NEWSOM", "WAS RIGHT", "ABOUT", "EVERYTHING")):
        text(d, (41, 17 + 7 * i), s, "white", anchor="ma")
    text(d, (3, 56), "$45", "mk_black")
    return img


def two_photos(t):
    """Two framed photos: the ex-wife and Junior; Donald and Zohran."""
    img, d = canvas((60, 50, 44))
    for i, (a, b, cap_) in enumerate((("kimberly", "junior", "YOUR EX"), ("trump", "mamdani", "ME"))):
        x0 = 4 + 41 * i
        d.rectangle((x0, 6, x0 + 35, 46), fill=C["gold"])
        d.rectangle((x0 + 2, 8, x0 + 33, 44), fill=(170, 200, 230) if i == 0 else (250, 200, 210))
        mini(d, x0 + 11, 42, a, arms="hug", facing=1)
        mini(d, x0 + 23, 42, b, facing=-1)
        text(d, (x0 + 18, 50), cap_, "white", anchor="ma")
        if i == 1 and t > 0.3:
            d.polygon([(x0 + 16, 12), (x0 + 18, 10), (x0 + 20, 12), (x0 + 18, 15)], fill=C["red"])
    return img


def lounge(t):
    """Trump on the sofa at Gracie Mansion, feet up, a Diet Coke on the go."""
    img, d = canvas((230, 214, 180))
    d.rectangle((0, 48, 84, 64), fill=(140, 90, 60))
    d.rectangle((10, 30, 70, 50), fill=C["red_sh"]); d.rectangle((10, 26, 70, 34), fill=C["red"])
    d.rectangle((6, 30, 12, 50), fill=C["red"]); d.rectangle((68, 30, 74, 50), fill=C["red"])
    mini(d, 34, 44, "trump", arms="out")
    d.rectangle((38, 38, 58, 41), fill=C["suit"])                          # his legs, up on the sofa
    d.rectangle((58, 36, 61, 41), fill=C["ink"])
    d.rectangle((20, 36, 22, 41), fill=C["steel"]); d.point((21, 35), fill=C["red"])   # the Diet Coke
    text(d, (42, 3), "GRACIE MANSION", "mk_black", anchor="ma")
    return img


@lru_cache(maxsize=None)
def rent_free_head():
    """Inside Newsom's head: Trump on a little sofa, rent: $0."""
    img = Image.new("RGBA", (44, 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((4, 14, 38, 26), fill=C["red_sh"]); d.rectangle((4, 10, 38, 16), fill=C["red"])
    mini(d, 20, 24, "trump", arms="out")
    d.rectangle((24, 18, 34, 21), fill=C["suit"])
    text(d, (22, 1), "RENT: $0", "mk_green", anchor="ma")
    return img


@lru_cache(maxsize=None)
def crush_heart():
    """Z + D in a heart, the way it's carved in a school desk."""
    img = Image.new("RGBA", (34, 26), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((1, 1, 18, 16), fill=C["mk_red"]); d.ellipse((15, 1, 32, 16), fill=C["mk_red"])
    d.polygon([(2, 10), (31, 10), (17, 25)], fill=C["mk_red"])
    text(d, (17, 7), "Z+D", "white", anchor="ma")
    return img


def family(t):
    """IN BRIEF: my ex dated Junior; you date his dad."""
    img, d = canvas("paper")
    text(d, (42, 2), "IN BRIEF", "mk_black", anchor="ma")
    d.line([(4, 9), (80, 9)], fill=C["mk_black"])
    rows = ((("kimberly", "MY EX"), ("junior", "JUNIOR")), (("mamdani", "YOU"), ("trump", "HIS DAD")))
    for r, ((a, la), (b, lb)) in enumerate(rows):
        if r == 1 and t < 0.25:
            break
        y = 20 + 23 * r
        mini_head(d, 18, y, a)
        mini_head(d, 64, y, b)
        d.polygon([(38, y - 1), (40, y - 3), (42, y - 1), (44, y - 3), (46, y - 1), (42, y + 4)], fill=C["red"])
        text(d, (18, y + 8), la, "mk_red" if r == 1 else "mk_black", anchor="ma")
        text(d, (64, y + 8), lb, "mk_black", anchor="ma")
    return img


def dates_chart(t):
    """DATES WITH DONALD: a bar chart."""
    img, d = canvas("white")
    text(d, (42, 2), "DATES WITH", "mk_black", anchor="ma")
    text(d, (42, 9), "DONALD", "mk_black", anchor="ma")
    k = min(1.0, t / 0.8)
    d.line([(43, 18), (43, 52)], fill=C["mk_black"])
    d.rectangle((44, 21, 44 + int(36 * k), 31), fill=C["mtie"])
    text(d, (3, 24), "ZOHRAN", "mk_black")
    d.rectangle((44, 39, 45, 49), fill=C["pink"])
    text(d, (3, 42), "MELANIA", "mk_black")
    text(d, (49, 42), "0", "mk_black")
    return img


def melania(t):
    """Melania at the pool at Mar-a-Lago: sunglasses, a hat, a drink, a very good mood."""
    img, d = scene(sky="sky", ground=(60, 170, 220), horizon=40)
    d.rectangle((0, 40, 84, 44), fill=C["white"])
    d.ellipse((60, 4, 76, 20), fill=C["duck"])                            # the sun
    d.polygon([(20, 52), (60, 44), (64, 50), (24, 58)], fill=C["white"])  # the lounger
    d.line([(24, 58), (22, 64)], fill=C["steel"]); d.line([(60, 50), (62, 56)], fill=C["steel"])
    d.ellipse((14, 34, 28, 48), fill=C["mel_skin"])
    d.rectangle((13, 36, 29, 38), fill=C["mel_hair"]); d.rectangle((13, 38, 16, 50), fill=C["mel_hair"])
    d.ellipse((6, 28, 36, 36), fill=C["white"]); d.ellipse((14, 24, 28, 34), fill=C["white"])   # the hat
    d.rectangle((17, 40, 26, 42), fill=C["ink"])                          # the sunglasses
    d.arc((18, 42, 25, 46), 20, 160, fill=C["mouth"])
    d.polygon([(28, 48), (56, 44), (58, 48), (30, 52)], fill=C["pink"])   # the dress
    gx = 34 if t > 0.5 else 32
    d.polygon([(gx, 34), (gx + 6, 34), (gx + 3, 39)], fill=C["glass"]); d.line([(gx + 3, 39), (gx + 3, 44)], fill=C["glass"])
    d.point((gx + 2, 35), fill=C["orange"])
    if t > 0.5:
        for k in range(3):
            fx.sparkle(img, 44 + 8 * k, 26 - 4 * (k % 2), 2, C["white"])
    return img


def bus(t, smoke=True):
    """The free bus, out of service, smoking."""
    img, d = scene(sky="sky_hi", ground="road", horizon=46)
    d.rectangle((0, 50, 84, 51), fill=C["duck"])
    d.rectangle((8, 24, 74, 48), fill=C["bus"], outline=C["ink"])
    d.rectangle((8, 40, 74, 48), fill=C["bus_sh"])
    for x in range(12, 66, 11):
        d.rectangle((x, 28, x + 8, 36), fill=C["bus_win"], outline=C["ink"])
    d.rectangle((66, 28, 72, 40), fill=C["bus_win"], outline=C["ink"])
    d.ellipse((16, 44, 26, 54), fill=C["ink"]); d.ellipse((56, 44, 66, 54), fill=C["ink"])
    d.rectangle((10, 18, 40, 24), fill=C["ink"])
    text(d, (25, 19), "FREE", "orange", anchor="ma")
    if smoke:
        for k in range(4):
            p = (t * 0.8 + k / 4) % 1.0
            r = 3 + int(p * 6)
            x, y = 70 + int(p * 8), 22 - int(p * 20)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 120, 130))
    if int(t * 4) % 2:
        text(d, (42, 3), "OUT OF SERVICE", "mk_red", anchor="ma")
    return img


def road_to_texas(t, convoy=()):
    """I-10 east: the state, driving to Texas. `convoy` is [(label, age)] for the vehicles on the road."""
    img, d = scene(sky="sky", ground=(210, 180, 120), horizon=26)
    d.polygon([(0, 26), (18, 26), (14, 64), (0, 64)], fill=C["grass"])   # California, behind
    text(d, (2, 30), "CA", "white")
    d.rectangle((0, 40, 84, 56), fill=C["road"])
    for x in range(0, 84, 10):
        d.line([(x + int(t * 40) % 10, 48), (x + int(t * 40) % 10 + 4, 48)], fill=C["duck"])
    d.rectangle((48, 4, 82, 20), fill=C["green"], outline=C["white"])
    text(d, (65, 6), "TEXAS", "white", anchor="ma"); text(d, (65, 13), "->", "white", anchor="ma")
    d.line([(60, 20), (60, 38)], fill=C["steel"]); d.line([(70, 20), (70, 38)], fill=C["steel"])
    for i, (label, a) in enumerate(convoy):
        if a < 0:
            continue
        x = int(-40 + a * 46)
        y = 44 if i % 2 == 0 else 52
        body = {"U-HAUL": "white", "$$$": "ink", "HQ": "steel_sh", "EX": "red"}.get(label, "steel_sh")
        d.rectangle((x, y - 9, x + 37, y + 1), fill=C[body], outline=C["ink"])
        if label == "U-HAUL":
            d.rectangle((x + 37, y - 5, x + 43, y + 1), fill=C["orange"], outline=C["ink"])
        text(d, (x + 19, y - 6), label, "orange" if label == "U-HAUL" else "gold" if label == "$$$" else "white", anchor="ma")
        d.ellipse((x + 3, y, x + 8, y + 5), fill=C["ink"]); d.ellipse((x + 28, y, x + 33, y + 5), fill=C["ink"])
    return img


@lru_cache(maxsize=None)
def oval_bg():
    """The Oval Office behind Trump on the call: gold curtains, the flags."""
    img, d = canvas((236, 226, 196))
    d.rectangle((0, 0, 20, 64), fill=C["gold"]); d.rectangle((64, 0, 84, 64), fill=C["gold"])
    for x in (4, 10, 16, 68, 74, 80):
        d.line([(x, 0), (x, 64)], fill=C["gold_sh"])
    d.rectangle((24, 4, 60, 30), fill=(150, 190, 230)); d.line([(42, 4), (42, 30)], fill=C["white"])
    d.line([(24, 17), (60, 17)], fill=C["white"])
    d.line([(22, 8), (22, 50)], fill=C["gold_dk"]); d.rectangle((14, 8, 22, 18), fill=C["blue"])
    d.line([(62, 8), (62, 50)], fill=C["gold_dk"]); d.rectangle((62, 8, 70, 18), fill=C["red"])
    return img


def trump_call(arms="acc1", mouth="closed", eyes="squint", brows="neutral"):
    """Trump on the line, on video: from the chest up, at the Resolute Desk."""
    img = oval_bg().copy()
    spr, _ = figure("trump", arms=arms, facing=1, mouth=mouth, eyes=eyes, brows=brows, phones=False)
    img.paste(spr.crop((0, 0, 84, 64)), (0, 4), spr.crop((0, 0, 84, 64)))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 58, 84, 64), fill=(110, 70, 40))                       # the desk
    d.rectangle((60, 1, 82, 8), fill=C["ink"])
    text(d, (71, 2), "LIVE", "red", anchor="ma")
    return img


def call_screen(t, name="DONNIE <3"):
    """An incoming call: the name, the photo, the green button."""
    img, d = canvas((20, 24, 40))
    text(d, (42, 4), "INCOMING CALL", "dim", anchor="ma")
    text(d, (42, 12), name, "white", anchor="ma")
    r = 10 + (1 if int(t * 6) % 2 else 0)
    d.ellipse((42 - r, 34 - r, 42 + r, 34 + r), fill=C["tskin"])
    d.rectangle((32, 22, 52, 28), fill=C["thair"])
    d.line([(37, 33), (39, 33)], fill=C["tring"]); d.line([(45, 33), (47, 33)], fill=C["tring"])
    d.ellipse((60, 50, 72, 62), fill=C["green"]); d.ellipse((12, 50, 24, 62), fill=C["red"])
    return img


def chart_line(img, pts, color):
    ImageDraw.Draw(img).line(pts, fill=C[color])


def zzz(img, x, y, a):
    """Sleepy Zs drifting up from (x, y)."""
    for k in range(3):
        p = (a * 0.8 + k / 3) % 1.0
        zx, zy = int(x + 6 * p + 2 * math.sin(p * 6)), int(y - 22 * p)
        pixel.outline_text(img, (zx, zy - 4), "Z" if p > 0.4 else "z", SILK, C["white"], INK)


def sparkles(img, x, y, a, n=4, r=10, seed=0, color="white"):
    for k in range(n):
        ang = seed + k * 2 * math.pi / n + a * 1.5
        fx.sparkle(img, int(x + r * math.cos(ang)), int(y + r * 0.7 * math.sin(ang)),
                   size=2 if int(a * 10 + k) % 3 else 3, color=C[color])


# --- comic text ---------------------------------------------------------------------------------------------

def word_pop(img, x, y, s, age, size=16, top=None, bottom=None, anchor="ma"):
    """Comic-book text that pops in: 'HANDSOME!', 'BOO', 'WHO?'."""
    from engine import PRESS16
    fnt = PRESS16 if size == 16 else PRESS
    fx.pop_text(img, x, y, s, age, fnt=fnt, top=top or C["gold_hi"], bottom=bottom or C["orange"], outline=INK,
                anchor=anchor)


if __name__ == "__main__":
    from engine import ROOT
    items = [phone_held(), placard("TAX THE", "RICH"), placard("NEWSOM", "2028", bg="blue"), big_check(), folder("IN", "BRIEF"),
             lawsuit(), crown(), cap(), nightcap(), trump_wig(), price_tag("TEMU $1.99"), wine_glass(), ice_block(),
             rubber_duck(), desk_box(), heart(), heart(4, 1.0), note(), rain_cloud(), tiny_hand(), soldier(), calendar(),
             l_sticker(), trotsky_filter(), placard("NO", "LANDLORDS"), placard("MAMDANI", "2028", bg="white", fg="mk_blue")]
    pics = [tiktok(0.3), tiktok(0.6, True), imessage([("l", "U UP?"), ("r", "...")], typing=True),
            truth_post(["ZOHRAN IS A", "COMMUNIST!"], strike=1, fix="HOTTIE!"), golf(1.0), stood_up(0.5),
            lobby(0.5), mansion(0.5, gold=0.6), mansion(0.5, who="mamdani", boxes=4), skyline(0.5, 5), tarmac(0.5),
            relationship(0.5), all_caps(1.0), merch(0.5), two_photos(0.5), lounge(0.5), family(0.5), dates_chart(1.0),
            melania(0.7), bus(0.4), road_to_texas(0.5, [("U-HAUL", 1.0), ("$$$", 0.6)]), trump_call(), call_screen(0.2)]
    sheet = Image.new("RGB", (8 * 90 + 6, 4 * 50 + 4 + ((len(pics) + 7) // 8) * 70 + 6), C["wall"])
    for i, im in enumerate(items):
        x, y = 4 + (i % 8) * 90, 4 + (i // 8) * 50
        sheet.paste(im, (x, y), im)
    y0 = 4 * 50 + 6
    for i, im in enumerate(pics):
        sheet.paste(im, (4 + (i % 8) * 90, y0 + (i // 8) * 70))
    out = ROOT / "build" / "props.png"
    scaled(sheet, 3).save(out)
    print(out)
