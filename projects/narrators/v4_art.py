"""Sprites and sets for Verse 4, Morgan's DRIVING MR. DAVID (gags_v4.py stages them).

Sprites are Canvas drawings outlined in ink, cached per pose; sets are registered
with sets.scene under "v4_*" names and return the world image.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, PRESS, SILK, H, W, Canvas, blend, blend_poly, mask, mix, rnd, text_width, vgrad
from pixelart import pixel
from props import globe, poster
from sets import frond, leaf_blob, scene

STONE = (150, 150, 160)
SOIL, SOIL_SH, SOIL_HI = C["soil"], C["soil_sh"], (150, 110, 76)
MOLE, MOLE_HI, PINK = (58, 52, 60), (92, 86, 96), (236, 150, 164)
SLOTH, SLOTH_SH, SLOTH_HI, SLOTH_FACE = (140, 112, 82), (104, 80, 60), (176, 148, 110), (220, 204, 170)
DODO, DODO_SH, DODO_HI, BEAK = (128, 136, 158), (96, 102, 124), (168, 176, 196), (214, 206, 140)
BAMBOO, BAMBOO_SH = (206, 170, 100), (160, 124, 70)
WEB_BLACK = (30, 26, 34)


def stext(s, x, y, txt, color, anchor="la"):
    """Silkscreen on a Canvas with the capitals' top row at y (the font sets them 4px down)."""
    s.text((x, y - 4), txt, color, anchor=anchor)


def itext(img, x, y, txt, color, anchor="la", fnt=SILK):
    """Text straight onto an image, capitals' top row at y."""
    pixel.text(img, (x, y - (4 if fnt is SILK else 0)), txt, fnt, color, shadow=None, anchor=anchor)


def silk_w(txt):
    return text_width(txt, SILK) - 1


def grass_line(d, y, x0, x1, color, seed, every=3, h=3):
    for x in range(int(x0), int(x1), every):
        hh = 1 + int(rnd(seed, x) * h)
        d.line([(x, y), (x + (1 if rnd(seed, "l", x) > 0.5 else 0), y - hh)], fill=color)


# --- lines 0-1: the road -------------------------------------------------------------------------

@lru_cache(maxsize=None)
def daisy(h=6):
    s = Canvas(9, h + 7)
    s.line([(4, 5), (4, h + 6)], "leaf")
    s.px((3, h + 3), "leaf_hi"); s.px((5, h + 4), "leaf_hi")
    s.pxs([(4, 1), (2, 3), (6, 3), (4, 5), (3, 2), (5, 2), (3, 4), (5, 4)], "white")
    s.px((4, 3), "gold")
    return s.done()


@lru_cache(maxsize=None)
def road_sign(rows, color=(38, 104, 70), post=20, icon=None):
    """A roadside sign on a post: white lettering on `color`; icon "cross" adds a little cemetery
    cross, "arrow" a right arrow."""
    tw = max(silk_w(r) for r in rows) + (8 if icon else 0)
    w, h = tw + 10, len(rows) * 8 + 7
    s = Canvas(w + 2, h + post + 2)
    x = (w + 2) // 2
    s.rect((x - 1, h, x + 1, h + post), (120, 124, 136))
    s.rect((1, 1, w, h), color)
    s.line([(3, 3), (w - 2, 3)], "white"); s.line([(3, h - 2), (w - 2, h - 2)], "white")
    s.line([(3, 3), (3, h - 2)], "white"); s.line([(w - 2, 3), (w - 2, h - 2)], "white")
    for i, r in enumerate(rows):
        stext(s, 6, 6 + i * 8, r, "white")
    if icon == "cross":
        cx = w - 8
        s.rect((cx, 5, cx + 1, h - 5), "white"); s.rect((cx - 2, 7, cx + 3, 8), "white")
    elif icon == "arrow":
        cx = w - 9
        s.poly([(cx, 5), (cx + 4, h // 2), (cx, h - 5)], "white")
    return s.done()


@lru_cache(maxsize=None)
def cemetery_gate():
    """Stone gateposts and a wrought-iron arch with the cemetery's name."""
    w, h = 104, 70
    s = Canvas(w, h)
    iron = (40, 36, 44)
    for x in range(16, w - 15, 5):
        s.line([(x, 28), (x, h - 2)], iron)
        s.px((x, 27), iron)
    s.line([(14, 34), (w - 15, 34)], iron)
    s.line([(14, h - 8), (w - 15, h - 8)], iron)
    for k in range(41):                                                # the arch
        a = math.pi * k / 40
        s.rect((int(w / 2 - math.cos(a) * 38), int(28 - math.sin(a) * 20),
                int(w / 2 - math.cos(a) * 38), int(29 - math.sin(a) * 20)), iron)
    for x in (2, w - 14):
        s.rect((x, 20, x + 11, h - 2), STONE)
        s.rect((x - 1, 16, x + 12, 20), mix(STONE, (255, 255, 255), 0.3))
        s.line([(x + 11, 21), (x + 11, h - 2)], mix(STONE, INK, 0.3))
        s.ell((x + 2, 9, x + 9, 16), mix(STONE, (255, 255, 255), 0.3))
    s.rect((22, 11, w - 23, 21), (70, 62, 58))
    stext(s, w // 2, 14, "RESTHAVEN", (230, 214, 170), anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def tombstone(rows=(), w=20, h=26, icon=None, color=STONE, text_y=None):
    """A round-topped headstone with engraved rows of text (from `text_y`) under an optional icon."""
    s = Canvas(w + 2, h + 2)
    hi, sh = mix(color, (255, 255, 255), 0.25), mix(color, INK, 0.45)
    top = min(14, w // 2)
    s.ell((1, 1, w, top * 2), color)
    s.rect((1, top, w, h), color)
    s.line([(w, top), (w, h)], mix(color, INK, 0.25))
    s.line([(3, top // 2 + 2), (3, h - 1)], hi)
    cx = w // 2 + 1
    y = 6
    if icon == "cross":
        s.rect((cx, 4, cx + 1, 12), sh); s.rect((cx - 2, 6, cx + 3, 7), sh)
        y = 15
    elif icon == "crown":
        s.poly([(cx - 6, 12), (cx - 6, 6), (cx - 3, 9), (cx, 4), (cx + 3, 9), (cx + 6, 6), (cx + 6, 12)], "gold")
        s.line([(cx - 6, 12), (cx + 6, 12)], "gold_sh"); s.px((cx, 9), "red")
        y = 16
    elif icon == "jet":                                                 # a delta-winged airliner in profile
        white = (240, 240, 246)
        s.line([(cx - 12, 9), (cx + 10, 9)], white); s.line([(cx - 11, 10), (cx + 8, 10)], white)
        s.px((cx + 11, 10), white); s.px((cx + 12, 11), white)          # the drooped nose
        s.poly([(cx - 6, 10), (cx + 3, 10), (cx - 9, 14)], white)
        s.poly([(cx - 12, 9), (cx - 12, 5), (cx - 9, 9)], white)        # the fin
        y = 17
    for i, r in enumerate(rows):
        stext(s, cx, (text_y or y) + i * 7, r, sh, anchor="ma")
    return s.done()


# --- line 2: the ferns ---------------------------------------------------------------------------

def fern_clump(img, x, y, t, curl=0.0, fiddle=0.0, shy=0.0):
    """A big fern growing from (x, y). `curl` 0-1 folds the fronds up and in, shyly (`shy` trembles
    them); `fiddle` 0-1 unrolls a fiddlehead in the middle."""
    d = ImageDraw.Draw(img)
    sway = math.sin(t * 1.6) * 0.04 + math.sin(t * 40) * 0.03 * shy
    for k in range(7):
        side = -1 if k % 2 else 1
        base = math.pi / 2 + side * (0.4 + 0.25 * (k // 2))
        a = base + (math.pi / 2 - base) * curl * 0.8 + sway
        length = (40 - 3 * (k // 2)) * (1 - 0.3 * curl)
        frond(d, x + side * (k // 2), y, length, a, C["leaf"] if k % 3 else C["leaf_sh"], width=5)
    if fiddle > 0:                                                      # the fiddlehead, unrolling
        top = y - 14 - 22 * fiddle
        d.line([(x, y), (x + 1, top)], fill=C["leaf_hi"], width=2)
        r = 4.5 * (1 - fiddle) + 1.5
        d.ellipse((x + 1 - r, top - 2 * r, x + 1 + r, top), outline=C["leaf_hi"], width=2)
        for k in range(int(6 * fiddle)):
            yy = top + 3 + k * 3
            d.line([(x - 4 * fiddle, yy + 2), (x + 5 * fiddle + 1, yy + 2)], fill=C["leaf_hi"])


@lru_cache(maxsize=None)
def folding_screen():
    """A three-panel paper privacy screen with a PRIVATE sign hung on it."""
    s = Canvas(64, 52)
    for k, shade in enumerate(("paper", "paper_sh", "paper")):
        x0 = 1 + k * 21
        s.rect((x0, 1, x0 + 19, 47), BAMBOO)
        s.rect((x0 + 2, 3, x0 + 17, 45), shade)
        s.line([(x0 + 2, 24), (x0 + 17, 24)], BAMBOO_SH)
        s.rect((x0 + 1, 47, x0 + 3, 50), BAMBOO_SH); s.rect((x0 + 16, 47, x0 + 18, 50), BAMBOO_SH)
    s.line([(22, 11), (32, 5), (42, 11)], "ink")
    s.rect((8, 11, 55, 21), (200, 40, 50))
    stext(s, 32, 14, "PRIVATE", "white", anchor="ma")
    return s.done()


# --- line 3: the bushes ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def long_lens(length=12):
    """A telephoto lens barrel pointing right, `length` pixels long."""
    s = Canvas(length + 6, 9)
    s.rect((1, 2, length + 2, 6), (224, 218, 200))
    for x in range(4, length, 6):
        s.line([(x, 2), (x, 6)], (60, 58, 60))
    s.rect((length + 1, 1, length + 4, 7), (40, 40, 46))
    s.line([(length + 4, 2), (length + 4, 6)], (120, 170, 220))
    s.line([(2, 3), (length, 3)], (246, 242, 230))
    return s.done()


def bush(img, x, y, w, h, t, rustle=0.0, seed=1):
    """A dense leafy bush, bottom centre (x, y); `rustle` shakes the leaves."""
    d = ImageDraw.Draw(img)
    for layer, col in enumerate((C["leaf_sh"], C["leaf"], C["leaf_hi"])):
        for k in range(9):
            jx = math.sin(t * 40 + k * 1.3 + layer) * 1.5 * rustle
            px = x - w / 2 + w * (k + 0.5) / 9 + (rnd(seed, layer, k) - 0.5) * 8 + jx
            top = y - h * (0.55 + 0.45 * math.sin(math.pi * (k + 0.5) / 9)) + layer * 6
            r = 9 + rnd(seed, "r", layer, k) * 6 - layer * 2
            d.ellipse((px - r, top, px + r, y), fill=col)
    for k in range(14):                                                 # leaf highlights
        px = x - w / 2 + rnd(seed, "hx", k) * w
        py = y - h * 0.7 + rnd(seed, "hy", k) * h * 0.6
        d.point((px, py), fill=C["leaf_hi"])


@lru_cache(maxsize=None)
def ike_poster():
    s = Canvas(46, 34)
    s.rect((1, 1, 44, 32), "white")
    for y in (3, 5, 28, 30):
        s.line([(3, y), (42, y)], "red")
    stext(s, 23, 9, "I LIKE", (40, 52, 110), anchor="ma")
    s.text((23, 17), "IKE", "red", fnt=PRESS, anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def nest():
    s = Canvas(22, 12)
    s.ell((1, 3, 20, 11), (150, 110, 70))
    for k in range(7):
        s.line([(2 + k * 3, 5 + k % 2), (5 + k * 3, 9 - k % 2)], (110, 80, 50))
    s.ell((6, 1, 10, 5), (200, 230, 240)); s.ell((11, 1, 15, 5), (200, 230, 240))    # eggs
    return s.done()


def cobweb(img, x, y, r, alpha=0.7):
    """A corner cobweb fanning down and right from (x, y)."""
    def draw(d):
        for k in range(5):
            a = k * math.pi / 8
            d.line([(x, y), (x + math.cos(a) * r, y + math.sin(a) * r)], fill=255)
        for rr in (r * 0.35, r * 0.65, r * 0.95):
            pts = [(x + math.cos(k * math.pi / 16) * rr, y + math.sin(k * math.pi / 16) * rr) for k in range(9)]
            d.line(pts, fill=255)
    blend(img, mask(draw), (236, 236, 244), alpha)


# --- line 4: the stadium ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def captain_hat():
    s = Canvas(18, 10)
    s.ell((2, 1, 15, 6), "white")
    s.rect((3, 4, 14, 6), "white")
    s.rect((3, 6, 14, 7), "black")
    s.poly([(9, 7), (17, 7), (16, 9), (9, 9)], "black")                # the peak, facing right
    s.px((9, 4), "gold"); s.px((8, 4), "gold_sh"); s.px((10, 4), "gold_sh")
    s.line([(4, 2), (12, 2)], (220, 220, 230))
    return s.done()


@lru_cache(maxsize=None)
def gold_cup():
    """A two-handled gold cup on a little base: the one you lift at the end of the final."""
    s = Canvas(20, 20)
    s.poly([(5, 2), (14, 2), (13, 9), (10, 11), (9, 11), (6, 9)], "gold")
    s.line([(6, 3), (7, 8)], "gold_hi")
    s.line([(5, 3), (2, 4), (2, 7), (6, 9)], "gold"); s.line([(14, 3), (17, 4), (17, 7), (13, 9)], "gold")
    s.rect((9, 11, 10, 14), "gold_sh")
    s.rect((6, 15, 13, 17), "gold"); s.line([(6, 17), (13, 17)], "gold_sh")
    return s.done()


# --- line 5: the mole -----------------------------------------------------------------------------

@lru_cache(maxsize=None)
def mole(pose="peek", blush=False):
    """A mole out of its hill, facing left: `peek`, or `kiss` (leaning in, lips puckered)."""
    s = Canvas(20, 16)
    lean = -2 if pose == "kiss" else 0
    s.ell((4 + lean, 2, 17 + lean, 15), MOLE)
    s.ell((6 + lean, 3, 12 + lean, 7), MOLE_HI)
    s.ell((1 + lean, 6, 7 + lean, 11), PINK)                            # the star nose
    s.pxs([(0 + lean, 7), (0 + lean, 9), (3 + lean, 5), (3 + lean, 12)], PINK)
    s.px((8 + lean, 6), "black")                                        # a tiny eye, hidden in fur
    s.rect((3, 12, 7, 15), PINK); s.rect((13, 12, 17, 15), PINK)        # the big digging paws
    s.pxs([(3, 15), (5, 15), (7, 15)], (200, 110, 130))
    if blush:
        s.pxs([(9 + lean, 9), (10 + lean, 9)], (240, 110, 130))
    if pose == "kiss":
        s.px((0 + lean, 10), "mouth"); s.px((1 + lean, 11), "mouth")
    return s.done()


@lru_cache(maxsize=None)
def heart(color=(236, 70, 100)):
    s = Canvas(9, 8)
    s.pxs([(2, 1), (3, 1), (5, 1), (6, 1)], color)
    s.rect((1, 2, 7, 3), color); s.rect((2, 4, 6, 4), color); s.rect((3, 5, 5, 5), color); s.px((4, 6), color)
    s.px((2, 2), (255, 200, 210))
    return s.done()


# --- lines 6-7: spiders ----------------------------------------------------------------------------

LEGS = (((3.5, -4), (6, -8.5)), ((4.5, -2), (8.5, -3)), ((4.5, 0.5), (8, 3.5)), ((3.5, 2.5), (5.5, 7)))


@lru_cache(maxsize=None)
def spider(size=2, step=0, pose="walk", hat=False, flower=False):
    """A spider head-up on her web, seen from the front: the big female (size 2, with a red
    hourglass) or the small male (size 1, courting in a top hat with a rose).
    pose: walk, lunge (front legs up to grab), burp (a leg sticks out of her jaws), smug."""
    k = size
    w, h = 20 * k + 10, 20 * k + 14
    s = Canvas(w, h)
    cx, hy = w // 2, 9 * k + 6                                         # head centre
    for i, ((kx, ky), (fx, fy)) in enumerate(LEGS):
        for side in (-1, 1):
            lift = 1 if (i + step + (side > 0)) % 2 else 0
            if pose == "lunge" and i < 2:
                kx, ky, fx, fy = 4, -6, 5 - i, -10 + i
            s.line([(cx + side * k, hy), (cx + side * kx * k, hy + (ky - lift) * k),
                    (cx + side * fx * k, hy + (fy - lift * 0.5) * k)], WEB_BLACK, k)
    s.ell((cx - 4 * k, hy + k, cx + 4 * k, hy + 10 * k), WEB_BLACK)      # abdomen
    s.ell((cx - 2 * k - 1, hy - 2 * k - 1, cx + 2 * k + 1, hy + 2 * k + 1), WEB_BLACK)   # head
    if size == 2:                                                       # the red hourglass
        ay = hy + 5 * k + 1
        s.poly([(cx - 3, ay - 4), (cx + 3, ay - 4), (cx, ay)], "red")
        s.poly([(cx - 3, ay + 4), (cx + 3, ay + 4), (cx, ay)], "red")
    ey = hy - k
    s.pxs([(cx - k, ey), (cx + k, ey)], "white")
    if pose == "smug":
        s.pxs([(cx - k - 1, ey - 1), (cx + k + 1, ey - 1)], WEB_BLACK)
    if pose == "burp":
        s.line([(cx - 1, hy + k), (cx + 1, hy + k)], "mouth")
        s.line([(cx + 1, hy + k), (cx + 5, hy + k - 3), (cx + 8, hy + k - 1)], (60, 56, 64))   # his leg
    if hat:
        s.rect((cx - 2, hy - 2 * k - 7, cx + 2, hy - 2 * k - 2), "black")
        s.line([(cx - 4, hy - 2 * k - 2), (cx + 4, hy - 2 * k - 2)], "black")
        s.line([(cx - 2, hy - 2 * k - 3), (cx + 2, hy - 2 * k - 3)], "red")
    if flower:
        fx, fy = cx + int(LEGS[0][1][0] * k), hy + int(LEGS[0][1][1] * k)
        s.pxs([(fx, fy - 1), (fx + 1, fy - 2), (fx - 1, fy - 2), (fx, fy - 3), (fx, fy - 2)], "red")
    return s.done()


@lru_cache(maxsize=None)
def top_hat():
    s = Canvas(11, 9)
    s.rect((3, 1, 7, 6), "black"); s.line([(1, 7), (9, 7)], "black"); s.line([(3, 5), (7, 5)], "red")
    return s.done()


@lru_cache(maxsize=None)
def rose():
    s = Canvas(9, 12)
    s.line([(4, 5), (4, 11)], "leaf"); s.px((5, 8), "leaf_hi")
    s.ell((2, 1, 7, 6), "red"); s.px((4, 3), "red_sh"); s.px((3, 2), "red_hi")
    return s.done()


def web(img, cx, cy, r, alpha=0.5, torn=False):
    """An orb web: spokes and a spiral, in thin silk (a flat tint)."""
    def draw(d):
        for k in range(10):
            a = k * math.pi / 5 + 0.2
            d.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=255)
        pts = []
        for s in range(0, 360 * 5, 10):
            a = math.radians(s)
            rr = 3 + (r - 4) * s / (360 * 5)
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        if torn:
            pts = pts[:len(pts) // 2]
        d.line(pts, fill=255)
    blend(img, mask(draw), (236, 236, 244), alpha)


@lru_cache(maxsize=None)
def tumbler(w=38, h=34):
    """A pint glass upside down: rims, sides and a glint (the rest is see-through)."""
    s = Canvas(w, h)
    glass = (200, 226, 236)
    s.line([(4, 1), (w - 5, 1)], glass); s.line([(1, h - 2), (w - 2, h - 2)], glass)
    s.line([(1, h - 3), (w - 2, h - 3)], glass)
    s.line([(4, 1), (1, h - 2)], glass); s.line([(w - 5, 1), (w - 2, h - 2)], glass)
    s.line([(7, 5), (5, h - 10)], (250, 252, 255)); s.line([(8, 5), (6, h - 14)], (250, 252, 255))
    s.line([(4, 2), (w - 5, 2)], (150, 186, 200))
    return s.img


@lru_cache(maxsize=None)
def case_file(closed=False):
    s = Canvas(52, 34)
    manila, manila_sh = (226, 196, 128), (184, 150, 92)
    if closed:
        s.rect((1, 6, 50, 32), manila)
        s.rect((4, 1, 24, 6), manila)
        s.line([(1, 32), (50, 32)], manila_sh)
        stext(s, 14, 3, "#1", (90, 60, 40), anchor="ma")
        stext(s, 26, 12, "SPIDER", (90, 60, 40), anchor="ma")
    else:
        s.rect((1, 10, 50, 32), manila_sh)
        s.rect((3, 5, 48, 30), "white")
        for y in range(10, 28, 4):
            s.line([(7, y), (30, y)], (150, 150, 170))
        s.rect((34, 8, 45, 20), (190, 190, 200))                         # a mugshot
        s.ell((37, 9, 42, 14), WEB_BLACK)
        s.pxs([(35, 13), (36, 11), (43, 11), (44, 13)], WEB_BLACK)
    return s.done()


# --- line 8: the cave -------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def armoured_car():
    """A long, low, finned black car with a jet exhaust (no badges)."""
    s = Canvas(96, 30)
    blk, blk_hi, blk_sh = (30, 30, 38), (70, 72, 86), (16, 16, 22)
    s.poly([(2, 20), (6, 12), (26, 10), (40, 4), (62, 4), (72, 11), (92, 14), (94, 22), (2, 24)], blk)
    s.poly([(40, 5), (61, 5), (68, 11), (36, 11)], (60, 90, 120))       # canopy
    s.line([(44, 6), (58, 6)], (130, 180, 220))
    s.poly([(2, 12), (6, 2), (14, 11)], blk)                            # the tail fins
    s.line([(6, 3), (12, 10)], blk_hi)
    s.line([(8, 13), (90, 15)], blk_hi)
    for wx in (20, 76):
        s.ell((wx - 8, 16, wx + 8, 29), blk_sh)
        s.ell((wx - 4, 20, wx + 4, 27), (60, 60, 70))
    s.rect((0, 16, 2, 20), (120, 200, 255))                             # the jet, idling blue
    s.rect((90, 16, 93, 17), (250, 220, 120))
    return s.done()


@lru_cache(maxsize=None)
def armour_suit():
    """A black armoured suit with a pointed-eared cowl, on a stand (no badge)."""
    s = Canvas(28, 58)
    blk, blk_hi = (34, 34, 42), (80, 82, 96)
    s.rect((12, 50, 15, 55), (120, 124, 136)); s.rect((6, 55, 21, 56), (120, 124, 136))
    s.poly([(3, 16), (24, 16), (26, 40), (20, 50), (7, 50), (1, 40)], (44, 40, 56))    # cape
    s.rect((8, 16, 19, 34), blk)
    s.line([(10, 20), (17, 20)], blk_hi); s.line([(10, 24), (17, 24)], blk_hi)
    s.rect((8, 34, 12, 50), blk); s.rect((15, 34, 19, 50), blk)
    s.rect((8, 30, 19, 31), (190, 160, 60))                             # utility belt
    s.ell((8, 4, 19, 16), blk)                                          # cowl
    s.poly([(9, 7), (9, 0), (12, 5)], blk); s.poly([(18, 7), (18, 0), (15, 5)], blk)
    s.rect((11, 12, 16, 15), (190, 150, 120))                           # chin
    s.pxs([(11, 9), (16, 9)], "white")
    return s.done()


@lru_cache(maxsize=None)
def bat(frame=0):
    s = Canvas(12, 7)
    s.ell((5, 2, 7, 5), (20, 18, 26))
    if frame:
        s.poly([(5, 3), (0, 1), (2, 5)], (20, 18, 26)); s.poly([(7, 3), (11, 1), (9, 5)], (20, 18, 26))
    else:
        s.poly([(5, 3), (0, 6), (3, 3)], (20, 18, 26)); s.poly([(7, 3), (11, 6), (8, 3)], (20, 18, 26))
    return s.done()


# --- line 9: the hide and the sloth --------------------------------------------------------------------

@lru_cache(maxsize=None)
def sloth(pose="hang", blink=False):
    """A three-toed sloth hanging under a branch (along its top row) by its long arms, face turned to
    camera at the left end. pose: hang, smug (a slow, wicked grin)."""
    s = Canvas(48, 32)
    for (x0, y0), (x1, y1) in (((13, 16), (9, 1)), ((17, 17), (16, 1)), ((33, 17), (34, 1)), ((37, 16), (41, 1))):
        s.line([(x0, y0), (x1, y1)], SLOTH, 3)
    for x in (9, 16, 34, 41):
        s.pxs([(x - 1, 0), (x, 0), (x + 1, 0)], (236, 226, 204))        # the claws hooked over
    s.ell((10, 11, 42, 28), SLOTH)                                      # the shaggy body
    s.ell((14, 19, 40, 29), SLOTH_SH)
    for k in range(9):
        s.line([(13 + k * 3, 14 + k % 2), (14 + k * 3, 17 + k % 3)], SLOTH_HI)
    s.ell((1, 8, 19, 26), SLOTH)                                        # the head, turned to us
    s.ell((3, 10, 17, 24), SLOTH_FACE)
    s.poly([(5, 13), (8, 14), (8, 18), (6, 19), (4, 16)], (70, 50, 40))    # the dark eye stripes
    s.poly([(15, 13), (12, 14), (12, 18), (14, 19), (16, 16)], (70, 50, 40))
    if not blink:
        s.px((7, 16), "white"); s.px((13, 16), "white")
    s.rect((9, 18, 11, 19), (60, 44, 36))                               # nose
    if pose == "smug":
        s.pxs([(6, 20), (7, 21), (8, 22), (9, 22), (10, 22), (11, 22), (12, 22), (13, 21), (14, 20)], (90, 50, 40))
        s.pxs([(8, 21), (12, 21)], (90, 50, 40))
    else:
        s.pxs([(7, 21), (8, 22), (9, 22), (10, 22), (11, 22), (12, 22), (13, 21)], (90, 50, 40))
    return s.done()


@lru_cache(maxsize=None)
def hide_hut():
    """A wildlife hide: a hut of sticks and thatch with a letterbox slot to watch through."""
    s = Canvas(64, 52)
    s.poly([(2, 18), (32, 2), (62, 18)], (150, 128, 70))                # thatch roof
    for x in range(6, 60, 5):
        s.line([(x, 17), (32 + (x - 32) // 3, 5)], (120, 100, 56))
    s.rect((6, 18, 57, 50), (116, 86, 56))
    for x in range(6, 58, 4):
        s.line([(x, 18), (x, 50)], (92, 68, 46))
    s.rect((12, 26, 50, 32), (22, 18, 20))                              # the slot
    for k in range(8):
        s.ell((4 + k * 7, 40 + (k % 2) * 3, 12 + k * 7, 50), C["leaf_sh"])
    return s.done()


@lru_cache(maxsize=None)
def poo():
    s = Canvas(9, 8)
    s.ell((1, 4, 7, 7), (110, 76, 44)); s.ell((2, 2, 6, 5), (110, 76, 44)); s.ell((3, 0, 5, 3), (110, 76, 44))
    s.px((3, 3), (150, 110, 70))
    return s.done()


# --- line 10: the ward -------------------------------------------------------------------------------

def planet_patient(img, cx, cy, r, t, eyes="half", fog=0.0):
    """The Earth as a patient, with a face and an oxygen mask. eyes: half, roll, shut."""
    g = globe(r, int(t * 1.5) % 16, lit=True)
    img.paste(g, (cx - g.width // 2, cy - g.height // 2), g)
    d = ImageDraw.Draw(img)
    for x in (cx - 6, cx + 3):
        d.rectangle((x - 1, cy - 6, x + 3, cy - 3), fill=(250, 250, 250))
        if eyes == "half":
            d.rectangle((x - 1, cy - 6, x + 3, cy - 5), fill=C["sea_sh"])
            d.rectangle((x + 1, cy - 4, x + 2, cy - 3), fill=INK)
        elif eyes == "roll":
            d.rectangle((x + 1, cy - 6, x + 2, cy - 6), fill=INK)
        else:
            d.rectangle((x - 1, cy - 6, x + 3, cy - 4), fill=C["sea_sh"])
            d.line([(x - 1, cy - 4), (x + 3, cy - 4)], fill=INK)
    d.ellipse((cx - 6, cy - 1, cx + 6, cy + 8), fill=(200, 230, 214), outline=(110, 150, 140))   # the mask
    d.line([(cx - 11, cy - 2), (cx - 6, cy + 2)], fill=(110, 150, 140))
    d.line([(cx + 11, cy - 2), (cx + 6, cy + 2)], fill=(110, 150, 140))
    if fog > 0:
        blend(img, mask(lambda m: m.ellipse((cx - 5, cy, cx + 5, cy + 7), fill=255)), (255, 255, 255), 0.75 * fog)
    d.line([(cx + 3, cy + 7), (cx + 16, cy + 12), (cx + 40, cy + 10)], fill=(170, 200, 190))


def ecg(img, box, t, bpm=70, color=(90, 240, 120)):
    """A heart monitor: a dark screen with the trace running left to right."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 8), fill=(150, 156, 168))
    d.rectangle(box, fill=(10, 18, 16))
    mid = (y0 + y1) // 2 + 3
    per = 60 / bpm
    pts = []
    for x in range(x0 + 1, x1):
        ph = ((t - (x1 - x) * 0.012) % per) / per
        y = mid
        if 0.10 < ph < 0.14:
            y = mid - 2
        elif 0.20 < ph < 0.23:
            y = mid + 2
        elif 0.23 <= ph < 0.27:
            y = mid - 9
        elif 0.27 <= ph < 0.30:
            y = mid + 3
        elif 0.45 < ph < 0.55:
            y = mid - 2
        pts.append((x, y))
    d.line(pts, fill=color)
    hx, hy = pts[-1]
    d.rectangle((hx - 1, hy - 1, hx, hy), fill=(220, 255, 220))
    itext(img, x0 + 2, y0 + 2, str(bpm), color)
    d.rectangle((x0 + 4, y1 + 3, x1 - 4, y1 + 5), fill=(110, 116, 128))


@lru_cache(maxsize=None)
def hospital_bed():
    s = Canvas(84, 34)
    steel = (170, 176, 190)
    s.rect((2, 2, 5, 32), steel); s.rect((78, 12, 81, 32), steel)        # head and foot rails
    s.line([(2, 2), (5, 2)], (220, 224, 234))
    s.rect((5, 18, 78, 22), steel)
    s.rect((4, 14, 80, 19), (236, 240, 244))                            # mattress and sheet
    s.rect((24, 11, 80, 18), (150, 190, 214))                           # the blanket
    s.line([(24, 11), (80, 11)], (190, 220, 236))
    s.ell((6, 8, 26, 16), (250, 250, 252))                              # pillow
    for x in (9, 74):
        s.ell((x - 2, 29, x + 2, 33), (60, 60, 70))
    return s.done()


@lru_cache(maxsize=None)
def iv_stand():
    s = Canvas(16, 62)
    s.line([(8, 6), (8, 58)], (170, 176, 190), 2)
    s.line([(3, 59), (13, 59)], (120, 124, 136), 2)
    s.line([(4, 6), (12, 6)], (170, 176, 190))
    s.rect((9, 7, 14, 18), (220, 236, 246)); s.rect((10, 12, 13, 17), (150, 200, 230))
    return s.done()


# --- line 11: the graveyard ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def scythe():
    s = Canvas(26, 44)
    s.line([(12, 42), (15, 5)], (120, 90, 60), 2)
    s.poly([(15, 4), (3, 3), (-1, 10), (7, 6)], (200, 206, 220))
    s.line([(3, 4), (14, 4)], (240, 244, 250))
    return s.done()


@lru_cache(maxsize=None)
def reaper_robe():
    """Death's black hooded robe, draped empty over a headstone."""
    s = Canvas(40, 30)
    robe, robe_hi = (34, 30, 40), (64, 58, 74)
    s.poly([(4, 29), (8, 8), (14, 2), (26, 2), (32, 8), (36, 29), (28, 24), (20, 29), (12, 24)], robe)
    s.ell((12, 1, 28, 15), robe)
    s.ell((15, 4, 25, 14), (10, 8, 12))                                 # the empty hood
    s.line([(9, 10), (6, 27)], robe_hi); s.line([(31, 10), (34, 27)], robe_hi)
    return s.done()


@lru_cache(maxsize=None)
def note(kind=0):
    """A little music note, whistled."""
    s = Canvas(8, 10)
    s.ell((1, 6, 4, 8), "white"); s.line([(4, 1), (4, 7)], "white")
    s.line([(4, 1), (6, 3)] if kind else [(4, 1), (7, 1)], "white")
    return s.done()


# --- line 12: the throne ---------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def throne():
    s = Canvas(42, 60)
    gold, gold_sh, velvet = C["gold"], C["gold_sh"], (150, 30, 50)
    s.rect((6, 4, 35, 44), gold)
    s.ell((6, 0, 35, 12), gold)
    s.rect((10, 8, 31, 40), velvet)
    s.ell((10, 4, 31, 14), velvet)
    s.rect((2, 34, 39, 42), gold)                                       # arms and seat
    s.rect((8, 36, 33, 40), (180, 40, 60))
    s.rect((4, 42, 8, 58), gold_sh); s.rect((33, 42, 37, 58), gold_sh)
    s.px((20, 2), C["red"]); s.pxs([(14, 3), (26, 3)], C["sea_hi"])
    s.line([(7, 6), (7, 42)], C["gold_hi"])
    return s.done()


@lru_cache(maxsize=None)
def little_crown():
    s = Canvas(9, 7)
    s.poly([(1, 5), (1, 1), (3, 3), (4, 0), (5, 3), (7, 1), (7, 5)], "gold")
    s.px((4, 4), "red")
    return s.done()


def rain_cloud(img, cx, cy, t, w=46, rain=1.0, seed=0):
    d = ImageDraw.Draw(img)
    if rain > 0:
        for k in range(int(22 * rain)):
            x = cx - w / 2 + 4 + rnd(seed, "rx", k) * (w - 8)
            y0 = cy + 4 + ((t * 150 + rnd(seed, "ry", k) * 70) % 70)
            d.line([(x, y0), (x - 1, y0 + 4)], fill=(150, 190, 240))
    grey, grey_hi = (110, 114, 130), (146, 150, 166)
    for k in range(5):
        x = cx - w / 2 + w * (k + 0.5) / 5
        r = 8 + 3 * math.sin(k * 1.9)
        d.ellipse((x - r, cy - r, x + r, cy + r * 0.7), fill=grey)
    d.rectangle((cx - w / 2 + 4, cy - 2, cx + w / 2 - 4, cy + 5), fill=grey)
    for k in range(4):
        x = cx - w / 2 + 8 + k * (w - 16) / 3
        d.ellipse((x - 5, cy - 9, x + 5, cy - 4), fill=grey_hi)


# --- lines 13-15: the bucket list -------------------------------------------------------------------------

@lru_cache(maxsize=None)
def bucket():
    s = Canvas(46, 40)
    tin, tin_sh, tin_hi = (170, 178, 186), (120, 128, 138), (214, 220, 228)
    s.line([(3, 8), (23, 1), (43, 8)], (90, 94, 104))                   # the handle
    s.poly([(3, 8), (42, 8), (37, 38), (8, 38)], tin)
    s.line([(5, 9), (9, 37)], tin_hi); s.line([(40, 9), (36, 37)], tin_sh)
    s.ell((3, 4, 42, 12), tin_sh)
    s.ell((6, 5, 39, 10), (60, 64, 72))
    s.rect((9, 16, 36, 32), "paper")
    stext(s, 23, 18, "BUCKET", "ink", anchor="ma")
    stext(s, 23, 25, "LIST", "red", anchor="ma")
    return s.done()


def birthday_cake(img, x, y, t, inferno=0.0):
    """A two-tier cake with 100 on it and a forest of candles; `inferno` roars them into one fire."""
    d = ImageDraw.Draw(img)
    icing, sponge = (250, 236, 240), (236, 190, 150)
    d.rectangle((x - 22, y - 14, x + 22, y), fill=sponge)
    d.rectangle((x - 22, y - 16, x + 22, y - 12), fill=icing)
    d.rectangle((x - 15, y - 30, x + 15, y - 16), fill=sponge)
    d.rectangle((x - 15, y - 32, x + 15, y - 28), fill=icing)
    for k in range(-20, 21, 5):
        d.point((x + k, y - 10), fill=(236, 90, 120))
    itext(img, x, y - 26, "100", (200, 40, 80), anchor="ma")
    d.rectangle((x - 24, y, x + 24, y + 2), fill=(230, 230, 236))
    for k in range(15):
        cx = x - 14 + k * 2
        d.line([(cx, y - 36), (cx, y - 33)], fill=(120, 190, 250) if k % 2 else (250, 150, 200))
        if inferno < 0.3:
            fy = y - 38 - (1 if int(t * 12 + k) % 2 else 0)
            d.point((cx, fy), fill=(255, 220, 90)); d.point((cx, fy - 1), fill=(255, 250, 200))
    if inferno > 0:
        hgt = 10 + 40 * inferno
        for k in range(9):
            fx = x - 16 + k * 4 + math.sin(t * 17 + k) * 2
            fh = hgt * (0.6 + 0.4 * math.sin(t * 11 + k * 1.7) ** 2)
            d.polygon([(fx - 5, y - 33), (fx + 5, y - 33), (fx, y - 33 - fh)], fill=(250, 120, 40))
        for k in range(9):
            fx = x - 16 + k * 4 + math.sin(t * 17 + k) * 2
            fh = hgt * (0.6 + 0.4 * math.sin(t * 11 + k * 1.7) ** 2)
            d.polygon([(fx - 2, y - 33), (fx + 2, y - 33), (fx, y - 33 - fh * 0.6)], fill=(255, 230, 110))


@lru_cache(maxsize=None)
def party_hat():
    s = Canvas(10, 12)
    s.poly([(1, 10), (5, 1), (8, 10)], (80, 170, 240))
    s.pxs([(4, 5), (6, 8), (3, 8)], (250, 220, 90))
    s.px((5, 0), (250, 90, 140))
    return s.done()


@lru_cache(maxsize=None)
def scroll(length=40):
    """The bucket list unrolled downward from its top roller."""
    s = Canvas(30, length + 8)
    s.rect((3, 3, 26, length + 3), "paper")
    for y in range(8, length, 4):
        s.line([(6, y), (6 + int(rnd("sc", y) * 8) + 12, y)], (120, 110, 140))
    s.rect((1, 1, 28, 4), "paper_sh"); s.rect((1, length + 3, 28, length + 6), "paper_sh")
    return s.done()


@lru_cache(maxsize=None)
def pen():
    s = Canvas(8, 22)
    s.rect((2, 1, 5, 16), (30, 30, 40)); s.line([(3, 2), (3, 15)], (90, 90, 110))
    s.rect((2, 5, 5, 6), C["gold"])
    s.poly([(2, 17), (5, 17), (4, 20), (3, 20)], (210, 200, 180))
    s.px((3, 21), "ink")
    return s.done()


@lru_cache(maxsize=None)
def padlock(shut=True):
    s = Canvas(18, 22)
    s.rect((1, 9, 16, 20), C["gold"])
    s.line([(1, 20), (16, 20)], C["gold_sh"]); s.line([(2, 10), (2, 19)], C["gold_hi"])
    s.ell((7, 12, 10, 15), (60, 44, 30)); s.rect((8, 14, 9, 17), (60, 44, 30))
    top = 1 if shut else -2
    s.line([(4, 9), (4, top + 3), (6, top), (11, top), (13, top + 3), (13, 9 if shut else 5)], (160, 164, 176), 2)
    return s.done()


@lru_cache(maxsize=None)
def polaroid(kind):
    """A snapshot clipped to the list: David with the whale, or with the gorilla."""
    from critters import gorilla, whale
    s = Canvas(30, 32)
    s.rect((1, 1, 28, 30), "white")
    photo = Image.new("RGBA", (24, 21), (110, 170, 214, 255) if kind == "whale" else (90, 140, 90, 255))
    d = ImageDraw.Draw(photo)
    if kind == "whale":
        w = whale(0).resize((46, 15), Image.NEAREST)
        photo.paste(w, (-14, 7), w)
        d.ellipse((15, 3, 19, 7), fill=C["skin"]); d.ellipse((14, 1, 19, 4), fill=C["hair"])
        d.line([(13, 8), (23, 8)], fill=(170, 210, 240))
    else:
        g = gorilla("stand")
        g = g.resize((g.width // 2, g.height // 2), Image.NEAREST)
        photo.paste(g, (11, 21 - g.height), g)
        d.ellipse((3, 7, 8, 12), fill=C["skin"]); d.ellipse((2, 5, 8, 9), fill=C["hair"])
        d.rectangle((3, 12, 8, 20), fill=C["shirt"])
    s.img.paste(photo, (3, 3))
    return s.done()


# --- lines 16-17: the cell, the birds and the dodo -----------------------------------------------------

def birdcage(img, cx, top, open_=0.0, w=26, h=32):
    """A gold birdcage hanging from its ring; `open_` 0-1 swings its door (on the right) open."""
    d = ImageDraw.Draw(img)
    gold, gold_sh = C["gold"], C["gold_sh"]
    x0, x1, y0, y1 = cx - w // 2, cx + w // 2, top + 8, top + h
    d.ellipse((cx - 2, top, cx + 2, top + 4), outline=gold)
    d.arc((x0, y0 - 8, x1, y0 + 10), 180, 360, fill=gold_sh, width=2)
    for x in range(x0 + 2, x1 - 1, 3):
        dy = int(math.sqrt(max(0, (w / 2) ** 2 - (x - cx) ** 2)) * 0.62)
        d.line([(x, y0 + 1 - dy + 1), (x, y1)], fill=gold)
    d.rectangle((x0 - 1, y1 - 2, x1 + 1, y1 + 1), fill=gold_sh)
    d.line([(x0, y0 + 8), (x1, y0 + 8)], fill=gold_sh)
    dx0, dy0, dy1 = x1 - 9, y0 + 10, y1 - 3                             # the door
    if open_ < 0.5:
        d.rectangle((dx0, dy0, x1 - 1, dy1), outline=gold_sh)
    else:
        sw = int(9 * (open_ - 0.5) * 2)
        d.rectangle((x1, dy0, x1 + sw, dy1), outline=gold_sh)
        for x in range(x1 + 2, x1 + sw, 3):
            d.line([(x, dy0), (x, dy1)], fill=gold)
    d.line([(cx - 8, y1 - 9), (cx + 2, y1 - 9)], fill=(150, 100, 60))   # the perch


@lru_cache(maxsize=None)
def dodo_david(pose="stand", step=0):
    """Sir David as a dodo: grey and plump, a great hooked beak, stubby wings, his swept white hair
    and bushy brow. pose: stand, flap (wings up), flop (sprawled flat on its beak, seeing stars)."""
    if pose == "flop":
        s = Canvas(46, 24)
        s.ell((7, 8, 31, 22), DODO)                                     # flat on its belly
        s.ell((10, 14, 29, 22), DODO_HI)
        s.poly([(12, 11), (3, 4), (16, 12)], DODO_SH)                   # a wing flung out
        s.line([(10, 10), (7, 3)], (230, 200, 90)); s.line([(13, 9), (12, 2)], (230, 200, 90))   # feet in the air
        s.pxs([(6, 3), (8, 3), (11, 2), (13, 2)], (230, 200, 90))
        s.pxs([(5, 14), (4, 12), (6, 11), (3, 13)], (240, 240, 244))    # tail curls
        s.ell((25, 11, 36, 22), DODO)                                   # head down, beak along the floor
        s.poly([(33, 15), (41, 17), (45, 20), (43, 22), (34, 21)], BEAK)
        s.poly([(42, 19), (45, 20), (44, 22)], (60, 60, 60))
        s.line([(28, 15), (30, 17)], "eye"); s.line([(30, 15), (28, 17)], "eye")      # x_x
        s.poly([(22, 10), (28, 6), (35, 9), (31, 12), (25, 13)], "hair")              # the swoop, awry
        s.line([(26, 8), (33, 9)], "hair_sh")
        return s.done()
    s = Canvas(36, 34)
    by = 4 if pose == "flap" else 6
    s.ell((3, by + 8, 25, by + 25), DODO)                               # body
    s.ell((6, by + 15, 22, by + 25), DODO_HI)
    s.pxs([(2, by + 12), (1, by + 10), (3, by + 9), (1, by + 13), (0, by + 11)], (240, 240, 244))   # tail curls
    s.ell((15, by, 27, by + 12), DODO)                                  # head
    s.poly([(24, by + 4), (32, by + 6), (34, by + 10), (31, by + 12), (25, by + 10)], BEAK)   # beak
    s.poly([(31, by + 9), (34, by + 10), (32, by + 13)], (60, 60, 60))  # the hooked tip
    s.px((22, by + 5), "eye")
    s.poly([(13, by + 3), (19, by - 3), (27, by - 2), (23, by + 2), (18, by + 2), (15, by + 6)], "hair")   # the swoop
    s.line([(17, by + 1), (24, by - 1)], "hair_sh")
    s.line([(20, by + 3), (24, by + 2)], "hair_sh")                     # the bushy brow
    if pose == "flap":
        s.poly([(10, by + 12), (3, by + 1), (15, by + 10)], DODO_SH)
        s.poly([(16, by + 12), (21, by + 2), (19, by + 13)], DODO_SH)
    else:
        s.poly([(9, by + 13), (17, by + 13), (13, by + 20)], DODO_SH)
    a, b = (0, 2) if step else (2, 0)
    s.rect((10 + a, by + 24, 11 + a, 31), (230, 200, 90)); s.rect((16 + b, by + 24, 17 + b, 31), (230, 200, 90))
    s.rect((9 + a, 31, 13 + a, 31), (230, 200, 90)); s.rect((15 + b, 31, 19 + b, 31), (230, 200, 90))
    return s.done()


# === sets ===============================================================================================

def ground(img, y, color, top=None):
    d = ImageDraw.Draw(img)
    d.rectangle((0, y, W, H), fill=color)
    if top:
        d.line([(0, y), (W, y)], fill=top)


@lru_cache(maxsize=1)
def ferns_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, 130), (70, 110, 80), (34, 70, 52), steps=4)
    d = ImageDraw.Draw(img)
    for k, x in enumerate((20, 70, 128, 250, 296)):
        d.rectangle((x, 0, x + 7 + k % 2 * 3, 130), fill=(52, 44, 40))
        d.line([(x, 0), (x, 130)], fill=(70, 60, 52))
    for k in range(10):
        leaf_blob(d, rnd("fc", k) * W, 10 + rnd("fcy", k) * 30, 20, (40, 84, 56), ("fcan", k), n=6)
    ground(img, 128, SOIL, SOIL_HI)
    for k in range(80):
        x, y = rnd("lit", k) * W, 130 + rnd("lit-y", k) * 48
        d.point((x, y), fill=[SOIL_SH, (150, 120, 70), (96, 120, 60)][k % 3])
    grass_line(d, 129, 0, W, C["moss"], "fg", every=2, h=3)
    return img


def ferns_set(c):
    img = ferns_static().copy()
    for k, (x, y, r) in enumerate(((190, 60, 26), (110, 90, 18), (250, 100, 22))):      # dappled light
        breathe = 0.5 + 0.5 * math.sin(c.t * 0.9 + k)
        blend(img, mask(lambda d: d.polygon([(x - 6, 0), (x + 6, 0), (x + r, y + 60), (x - r + 8, y + 60)], fill=255)),
              (230, 250, 200), 0.05 + 0.03 * breathe)
    return img


FERN = (176, 146)
scene("v4_ferns", cast={"david": dict(x=112, y=146, facing=1, body="crouch")})(ferns_set)


@lru_cache(maxsize=1)
def bushes_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, 124), (176, 210, 226), (214, 230, 214), steps=4)
    d = ImageDraw.Draw(img)
    for k in range(7):
        leaf_blob(d, 10 + k * 50, 96 + rnd("bb", k) * 8, 26, (120, 160, 110), ("bfar", k), n=6)
    d.rectangle((96, 0, 112, 128), fill=(92, 70, 56))                  # the tree the poster is nailed to
    d.line([(96, 0), (96, 128)], fill=(118, 92, 72))
    leaf_blob(d, 104, 8, 40, C["leaf"], "btree", n=9)
    ground(img, 124, (110, 150, 84), (140, 178, 100))
    grass_line(d, 125, 0, W, (150, 186, 110), "bg", every=2)
    return img


def bushes_set(c):
    img = bushes_static().copy()
    if c.get("ike"):
        p = ike_poster()
        img.paste(p, (81, 62), p)
    return img


BUSH = (206, 134)
scene("v4_bushes", cast={"david": dict(x=BUSH[0], y=BUSH[1], facing=-1, body="crouch")})(bushes_set)


@lru_cache(maxsize=1)
def stadium_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, 50), (110, 170, 230), (180, 214, 240), steps=4)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 36, W, 100), fill=(70, 70, 84))                     # the stands
    for y in range(40, 98, 5):
        d.line([(0, y + 4), (W, y + 4)], fill=(56, 56, 68))
    d.rectangle((0, 30, W, 36), fill=(200, 200, 210))
    d.rectangle((0, 98, W, 104), fill=(40, 44, 50))                     # the barrier
    for x in range(0, W, 26):
        d.rectangle((x, 99, x + 20, 102), fill=(0, 110, 70))
    d.rectangle((0, 104, W, H), fill=(76, 150, 72))                     # the pitch, mown in stripes
    for k in range(0, W, 40):
        d.polygon([(k, 104), (k + 20, 104), (k + 30, H), (k + 10, H)], fill=(88, 164, 80))
    d.line([(0, 118), (W, 118)], fill=(236, 240, 236))
    for x in (262, 300):                                                # the posts
        d.rectangle((x, 44, x + 2, 118), fill=(240, 240, 244))
    d.rectangle((262, 88, 302, 89), fill=(240, 240, 244))
    return img


CROWD_COLS = [(236, 200, 60), (40, 130, 80), (240, 240, 240), (200, 60, 60), (60, 110, 200)]


def crowd(img, t, cards=None, flip=1.0, wave=None):
    """The stands full of fans bobbing; `cards` spells a word in a card stunt across the middle rows,
    flipping over column by column as `flip` goes 0-1; `wave` is where a Mexican wave has reached."""
    d = ImageDraw.Draw(img)
    for row, y in enumerate(range(41, 97, 5)):
        for x in range(2 + (row % 2) * 3, W, 6):
            jump = 1 if math.sin(t * 9 + x * 0.3 + row) > 0.7 else 0
            if wave is not None and abs(x - wave) < 16:
                jump = 3
            d.rectangle((x, y - jump, x + 2, y + 2 - jump), fill=CROWD_COLS[(x * 7 + row * 3) % 5])
    if cards:
        tw = text_width(cards, PRESS)
        x0, x1 = W // 2 - tw // 2 - 8, W // 2 + tw // 2 + 8
        edge = x0 + (x1 - x0) * flip
        layer = Image.new("RGB", (W, H), (236, 200, 60))
        pixel.text(layer, (W // 2 - tw // 2, 55), cards, PRESS, (20, 90, 60), shadow=None)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rectangle((x0, 49, min(edge, x1), 69), fill=255)
        img.paste(layer, (0, 0), m)
        for x in range(x0, int(min(edge, x1)), 6):                     # the card seams
            d.line([(x, 49), (x, 69)], fill=(206, 170, 40))


def stadium_set(c):
    img = stadium_static().copy()
    crowd(img, c.t, c.get("cards"), c.get("flip", 1.0), c.get("wave"))
    return img


scene("v4_stadium", cast={"morgan": dict(x=150, y=146, facing=1, outfit="madiba")})(stadium_set)


@lru_cache(maxsize=1)
def dirt_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, 110), (150, 190, 170), (196, 214, 180), steps=3)
    d = ImageDraw.Draw(img)
    for k in range(6):
        leaf_blob(d, k * 64, 90, 30, (104, 140, 96), ("dfar", k), n=6)
    ground(img, 110, SOIL, SOIL_HI)
    for k in range(160):
        x, y = rnd("dd", k) * W, 112 + rnd("dd-y", k) * 66
        d.point((x, y), fill=[SOIL_SH, SOIL_HI, (96, 70, 50)][k % 3])
    grass_line(d, 111, 0, W, (110, 150, 80), "dg", every=2, h=4)
    return img


MOLEHILL = (204, 136)


def molehill(img):
    d = ImageDraw.Draw(img)
    x, y = MOLEHILL
    d.ellipse((x - 18, y - 12, x + 18, y + 8), fill=SOIL_SH)
    d.ellipse((x - 15, y - 12, x + 15, y + 2), fill=SOIL)
    d.ellipse((x - 6, y - 12, x + 6, y - 6), fill=(50, 34, 28))
    for k in range(8):
        d.point((x - 14 + k * 4, y - 2 - k % 3), fill=SOIL_HI)


scene("v4_dirt", cast={"david": dict(x=150, y=138, facing=1, body="lie", shadow=False)})(
    lambda c: dirt_static().copy())


@lru_cache(maxsize=1)
def office_static():
    img = Image.new("RGB", (W, H), (40, 36, 48))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 120), fill=(52, 46, 58))
    d.rectangle((210, 20, 290, 96), fill=(20, 24, 44))                  # the window: a city at night
    for k in range(9):
        bx = 212 + k * 9
        bh = 20 + rnd("city", k) * 40
        d.rectangle((bx, 96 - bh, bx + 7, 96), fill=(34, 36, 60))
        for wy in range(int(98 - bh), 94, 5):
            if rnd("win", k, wy) < 0.4:
                d.point((bx + 3, wy), fill=(250, 220, 120))
    for y in range(22, 96, 5):                                          # the blinds
        d.line([(210, y), (290, y)], fill=(70, 66, 80))
    d.rectangle((208, 18, 292, 98), outline=(24, 20, 28))
    return img


DESK_Y = 122


def office_set(c):
    img = office_static().copy()
    for k in range(6):                                                  # light through the blinds
        y = 30 + k * 11
        blend_poly(img, [(120, y), (200, y - 12), (200, y - 8), (120, y + 4)], (240, 220, 170), 0.12)
    return img


def office_desk(c):
    """The desk in front of him, with its lamp: drawn over the cast."""
    img = c.world
    d = ImageDraw.Draw(img)
    d.rectangle((0, DESK_Y, W, H), fill=(72, 48, 36))
    d.line([(0, DESK_Y), (W, DESK_Y)], fill=(110, 76, 56))
    for x in range(0, W, 40):
        d.line([(x, DESK_Y + 4), (x + 30, DESK_Y + 4)], fill=(84, 58, 44))
    d.rectangle((58, 106, 62, DESK_Y), fill=(40, 60, 40)); d.rectangle((52, DESK_Y - 2, 70, DESK_Y + 1), fill=(40, 60, 40))
    d.polygon([(48, 106), (72, 106), (66, 96), (54, 96)], fill=(40, 90, 60))
    blend_poly(img, [(50, 106), (70, 106), (132, 146), (-12, 146)], (255, 230, 160), 0.22)


scene("v4_office", near=office_desk,
      cast={"morgan": dict(x=176, y=144, facing=-1, outfit="suit", hat="fedora", shadow=False)})(office_set)


@lru_cache(maxsize=1)
def web_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, H), (80, 60, 110), (236, 150, 90), steps=6)
    d = ImageDraw.Draw(img)
    for k in range(9):                                                  # garden silhouettes
        x = k * 38 + rnd("gw", k) * 10
        leaf_blob(d, x, 150 + rnd("gwy", k) * 10, 26, (40, 30, 50), ("gs", k), n=6)
    d.rectangle((0, 150, W, H), fill=(40, 30, 50))
    d.line([(116, 0), (130, 150)], fill=(50, 38, 44), width=3)          # the two stems holding the web
    d.line([(262, 0), (246, 150)], fill=(50, 38, 44), width=3)
    return img


WEB = (188, 80)
scene("v4_web", cast={"david": dict(x=64, y=154, facing=1, body="crouch")})(
    lambda c: web_static().copy())


@lru_cache(maxsize=1)
def cave_static():
    img = Image.new("RGB", (W, H), (20, 22, 30))
    d = ImageDraw.Draw(img)
    for k in range(10):
        x = rnd("rock", k) * W
        d.ellipse((x - 30, 40 + rnd("rocky", k) * 50, x + 30, 120 + rnd("rocky", k) * 20), fill=(28, 30, 40))
    for k in range(26):                                                 # stalactites
        x = k * 13 + rnd("st", k) * 8
        length = 8 + rnd("stl", k) * 26
        d.polygon([(x - 5, 0), (x + 5, 0), (x, length)], fill=(40, 42, 56))
    d.rectangle((0, 132, W, H), fill=(44, 46, 56))                      # the platform
    d.line([(0, 132), (W, 132)], fill=(90, 94, 110))
    for x in range(0, W, 24):
        d.line([(x, 133), (x, H)], fill=(38, 40, 50))
    return img


def cave_set(c):
    img = cave_static().copy()
    lights = c.get("lights", 0.0)
    if lights > 0:
        blend(img, 1.0, (90, 110, 150), 0.3 * lights)
    d = ImageDraw.Draw(img)
    for k in range(4):                                                  # the waterfall on the left
        x = 10 + k * 5
        for y in range(0, 132, 6):
            yy = (y + c.t * 90 + k * 13) % 132
            d.line([(x, yy), (x, yy + 3)], fill=(90, 120, 170))
    return img


CAVE_CAR, CAVE_SUIT = (190, 136), (282, 136)       # bottom centres
scene("v4_cave", cast={"morgan": dict(x=84, y=140, facing=1, outfit="lucius", glasses=True)})(cave_set)


@lru_cache(maxsize=1)
def hide_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, H), (120, 170, 120), (50, 96, 66), steps=5)
    d = ImageDraw.Draw(img)
    for k in range(12):
        leaf_blob(d, rnd("hj", k) * W, 20 + rnd("hjy", k) * 100, 24, [(66, 116, 78), (56, 100, 70)][k % 2],
                  ("hjb", k), n=6)
    d.rectangle((0, 40, W, 46), fill=(96, 70, 52))                      # the sloth's branch
    d.line([(0, 40), (W, 40)], fill=(130, 100, 70))
    for x in (40, 280):
        d.line([(x, 46), (x + 8, 62)], fill=(96, 70, 52), width=2)
    ground(img, 146, (70, 96, 52), (96, 124, 66))
    for k in range(6):
        frond(d, 20 + k * 58, 152, 30, 0.6 + (k % 2) * 1.9, C["leaf_sh"], width=5)
    return img


HIDE = (120, 150)               # the hide's bottom centre
SLOT = (HIDE[0] - 20, HIDE[1] - 26, HIDE[0] + 18, HIDE[1] - 20)
SLOTH_AT = (128, 42)            # the sloth's sprite top-left hooks on the branch here
NIGHT = (22, 26, 56)
scene("v4_hide")(lambda c: hide_static().copy())


@lru_cache(maxsize=1)
def ward_static():
    img = Image.new("RGB", (W, H), (190, 214, 200))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 94, W, 132), fill=(170, 200, 186))
    d.line([(0, 94), (W, 94)], fill=(150, 180, 166))
    d.rectangle((0, 132, W, H), fill=(170, 170, 176))                   # floor tiles
    for x in range(0, W + 40, 16):
        d.line([(x, 132), (x - 20, H)], fill=(150, 150, 160))
    d.rectangle((30, 28, 94, 84), fill=(120, 170, 220))                 # window with blinds
    for y in range(30, 84, 4):
        d.line([(30, y), (94, y)], fill=(210, 220, 226))
    d.rectangle((28, 26, 96, 86), outline=(240, 244, 246))
    bed = hospital_bed()
    img.paste(bed, (150, 150 - bed.height), bed)
    iv = iv_stand()
    img.paste(iv, (138, 152 - iv.height), iv)
    return img


BED_HEAD = (168, 124)           # where the planet lies on the pillow
MONITOR = (250, 64, 294, 92)


def ward_set(c):
    img = ward_static().copy()
    d = ImageDraw.Draw(img)
    d.line([(272, 100), (272, 150)], fill=(150, 156, 168), width=2)     # the monitor's stand
    d.line([(262, 150), (282, 150)], fill=(120, 124, 136), width=2)
    ecg(img, MONITOR, c.t, bpm=c.get("bpm", 72))
    return img


scene("v4_ward", cast={"david": dict(x=112, y=152, facing=1)})(ward_set)


@lru_cache(maxsize=1)
def graveyard_static():
    img = Image.new("RGB", (W, H))
    vgrad(img, (0, 0, W, 120), (120, 124, 146), (176, 176, 190), steps=4)
    d = ImageDraw.Draw(img)
    d.ellipse((-60, 96, 380, 220), fill=(84, 110, 76))                  # the hill
    d.rectangle((0, 140, W, H), fill=(84, 110, 76))
    for x in range(0, W, 7):                                            # iron railings far back
        d.line([(x, 102), (x, 112)], fill=(50, 50, 60))
    d.line([(0, 104), (W, 104)], fill=(50, 50, 60))
    d.line([(24, 126), (30, 60)], fill=(60, 52, 50), width=3)           # a dead tree
    for a, b in (((28, 80), (8, 64)), ((29, 72), (44, 58)), ((27, 92), (42, 84))):
        d.line([a, b], fill=(60, 52, 50), width=2)
    for k, x in enumerate((60, 118, 300)):                              # older graves
        st = tombstone((), 12, 16, "cross" if k % 2 else None, (130, 130, 142))
        img.paste(st, (x, 124 - st.height), st)
    grass_line(d, 140, 0, W, (110, 140, 90), "gy", every=3)
    return img


GRAVES = {"concorde": (150, 138), "queen": (206, 138), "death": (266, 140)}    # bottom centres
scene("v4_graveyard", cast={"david": dict(x=80, y=152, facing=1)})(lambda c: graveyard_static().copy())


THRONE_AT = (216, 150)          # the throne's bottom centre


@lru_cache(maxsize=1)
def throne_static():
    img = Image.new("RGB", (W, H), (80, 60, 70))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 24):                                           # drapes
        d.rectangle((x, 0, x + 11, 130), fill=(130, 30, 46))
        d.rectangle((x + 12, 0, x + 23, 130), fill=(110, 24, 40))
    d.rectangle((0, 0, W, 12), fill=(196, 150, 60))
    d.rectangle((0, 130, W, H), fill=(120, 110, 120))
    d.polygon([(204, 130), (228, 130), (262, H), (170, H)], fill=(170, 30, 50))   # the red carpet
    t = throne()
    img.paste(t, (THRONE_AT[0] - t.width // 2, THRONE_AT[1] - t.height), t)
    return img


scene("v4_throne", cast={"david": dict(x=216, y=146, facing=-1, body="sit", hat="crown", shadow=False),
                         "morgan": dict(x=100, y=152, facing=1, outfit="chauffeur", hat="chauffeur")})(
    lambda c: throne_static().copy())


@lru_cache(maxsize=1)
def party_static():
    img = Image.new("RGB", (W, H), (226, 196, 150))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 16):                                           # wallpaper stripes
        d.rectangle((x, 0, x + 7, 120), fill=(214, 182, 138))
    d.rectangle((0, 120, W, H), fill=(120, 80, 56))
    d.line([(0, 120), (W, 120)], fill=(150, 104, 74))
    d.rectangle((110, 128, 250, 134), fill=(236, 236, 240))             # the table
    d.rectangle((120, 134, 124, 168), fill=(130, 90, 60)); d.rectangle((236, 134, 240, 168), fill=(130, 90, 60))
    for k in range(9):                                                  # bunting
        x = 20 + k * 34
        d.polygon([(x, 30), (x + 14, 30), (x + 7, 40)], fill=[(240, 90, 110), (90, 170, 240), (250, 210, 80)][k % 3])
    d.line([(0, 30), (W, 30)], fill=(110, 80, 60))
    return img


BUCKET_AT, CAKE_AT = (146, 128), (214, 128)      # bottom centres on the table
scene("v4_party", cast={"morgan": dict(x=74, y=152, facing=1, outfit="suit"),
                        "david": dict(x=284, y=152, facing=-1)})(lambda c: party_static().copy())


LIST_ITEMS = [("SWIM WITH A BLUE WHALE", 64), ("MEET A MOUNTAIN GORILLA", 92), ("BEAT MORGAN FREEMAN", 120)]
LIST_BOX_X = 64                 # the checkboxes' left edge; item text starts 16px right of it


@lru_cache(maxsize=1)
def list_static():
    img = Image.new("RGB", (W, H), (110, 76, 56))
    d = ImageDraw.Draw(img)
    for y in range(0, H, 9):
        d.line([(0, y), (W, y + 3)], fill=(98, 68, 50))
    d.rectangle((36, 14, 284, 190), fill=(150, 110, 70))                # the clipboard
    d.rectangle((44, 24, 276, 190), fill=(246, 244, 236))               # the paper
    for y in range(56, 190, 14):
        d.line([(48, y), (272, y)], fill=(190, 206, 232))
    d.line([(58, 24), (58, 190)], fill=(230, 150, 150))
    d.rectangle((136, 10, 184, 28), fill=(190, 194, 206))               # the clip
    d.rectangle((140, 12, 180, 20), fill=(150, 156, 170))
    itext(img, 160, 36, "SIR DAVID'S BUCKET LIST", (40, 40, 80), anchor="ma")
    d.line([(90, 43), (230, 43)], fill=(40, 40, 80))
    for text_, y in LIST_ITEMS:
        itext(img, LIST_BOX_X + 16, y + 2, text_, (30, 30, 60))
    return img


scene("v4_list")(lambda c: list_static().copy())


CELL_WINDOW = (206, 30, 276, 80)


@lru_cache(maxsize=None)
def diva():
    """The pin-up on the cell wall: a starlet in a long dress (a silhouette)."""
    s = Canvas(18, 30)
    s.ell((7, 1, 12, 7), (60, 30, 40))
    s.poly([(1, 2), (7, 3), (6, 8), (2, 6)], (60, 30, 40))              # hair tossed back
    s.poly([(8, 7), (12, 8), (13, 15), (15, 29), (4, 29), (7, 15)], (240, 236, 230))
    s.line([(12, 9), (16, 2)], (240, 236, 230), 2)                      # an arm up behind her head
    return s.done()


@lru_cache(maxsize=1)
def cell_static():
    img = Image.new("RGB", (W, H), (112, 110, 116))
    d = ImageDraw.Draw(img)
    for row, y in enumerate(range(0, 140, 10)):                         # the block wall
        off = (row % 2) * 12
        for x in range(-off, W, 24):
            shade = [(112, 110, 116), (104, 102, 110), (120, 118, 124)][int(rnd("blk", row, x) * 3)]
            d.rectangle((x + 1, y + 1, x + 23, y + 9), fill=shade)
    wx0, wy0, wx1, wy1 = CELL_WINDOW
    vgrad(img, (wx0, wy0, wx1, wy1), (110, 180, 240), (190, 226, 246), steps=3)
    d.ellipse((wx0 + 30, wy0 + 12, wx0 + 56, wy0 + 22), fill=(250, 250, 252))
    for x in range(wx0 + 5, wx1 - 2, 9):
        d.rectangle((x, wy0, x + 2, wy1), fill=(58, 58, 68))
    d.rectangle((wx0, wy1 - 16, wx1, wy1 - 15), fill=(58, 58, 68))
    d.rectangle((wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3), outline=(80, 78, 86), width=3)
    d.rectangle((0, 140, W, H), fill=(96, 92, 90))                      # the floor
    d.line([(0, 140), (W, 140)], fill=(130, 126, 124))
    d.rectangle((6, 110, 70, 118), fill=(70, 80, 60))                   # the bunk
    d.rectangle((6, 118, 70, 122), fill=(90, 90, 100))
    d.rectangle((8, 122, 11, 140), fill=(90, 90, 100)); d.rectangle((65, 122, 68, 140), fill=(90, 90, 100))
    d.ellipse((8, 104, 24, 112), fill=(220, 220, 214))
    poster(img, (86, 34, 122, 88), "GILDA", None, (60, 30, 50), art=diva(), fg=C["gold_hi"])
    return img


scene("v4_cell", cast={"morgan": dict(x=228, y=152, facing=1, outfit="prison")})(lambda c: cell_static().copy())
