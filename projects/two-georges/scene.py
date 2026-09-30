"""The Atlantic between them: Boston (west, left) at dawn and London (east, right) at dusk,
with one sun on the horizon between them, rising for one George and setting for the other.

The static art is drawn once: the scenery functions draw London on the left and
Boston on the right, lit toward the middle, and `backdrop()` mirrors that layer
so west ends up on the left. Everything that must not read backwards (flags,
text, ships) and everything that moves is drawn per frame, after the flip.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import C, INK, SILK, H, W, Canvas, dither_rect, mask, mix, outline_text, rnd
from pixelart import pixel

HORIZON = 97
SUN = (160, 97)
FEET_Y = 115                  # the Georges stand on the wharf and quay tops
WASH_X, GEORGE_X = 71, 247    # their centre lines
BOSTON_EDGE, LONDON_EDGE = 100, 219   # where the wharf and the quay end over the water

P = {
    # skies, top -> horizon
    "dusk": [(34, 26, 58), (54, 38, 82), (82, 56, 106), (116, 78, 124), (150, 102, 134)],
    "glow": [(48, 40, 90), (96, 66, 122), (168, 98, 130), (226, 140, 122), (250, 196, 138)],
    "dawn": [(52, 58, 106), (102, 88, 138), (184, 122, 134), (236, 164, 130), (252, 208, 150)],
    # sea, horizon -> foreground
    "sea": [(108, 96, 146), (76, 76, 130), (52, 58, 110), (36, 42, 88), (26, 30, 66)],
    "cap": (222, 226, 242),
    # London, lit from the right by the setting sun (before the mirror)
    "far_l": (92, 76, 120), "far_l_lit": (126, 100, 146), "far_l_dk": (70, 56, 100),
    "stone": (112, 100, 136), "stone_dk": (78, 68, 106), "stone_hi": (156, 138, 160), "mortar": (60, 50, 88),
    "rain": (158, 148, 192),
    # Boston, lit from the left by the rising sun (before the mirror)
    "far_r": (156, 112, 122), "far_r_lit": (206, 148, 138), "far_r_dk": (116, 84, 106),
    "hill": (112, 146, 100), "hill_dk": (76, 102, 92), "hill_hi": (170, 176, 112),
    "brick": (160, 94, 84), "brick_dk": (112, 66, 80),
    "steeple": (240, 226, 208), "steeple_dk": (176, 156, 184),
    "lamp": (255, 214, 120),
}


def mx(x, width=1):
    """Where a thing drawn at x (width wide) in the unmirrored scenery lands after the flip."""
    return W - x - width


def ramp_color(ramp, pos, thr):
    """Banded ramp lookup: flat bands, dithered only near each boundary."""
    n = len(ramp) - 1
    pos = np.clip(pos, 0, n - 1e-6)
    i = np.floor(pos).astype(int)
    f = np.clip((pos - i - 0.62) / 0.38, 0, 1)
    pick = np.where(thr < f, i + 1, i)
    return np.array(ramp)[np.clip(pick, 0, n)]


# --- static layers ------------------------------------------------------------------

def _sky(arr):
    ys, xs = np.mgrid[0:HORIZON, 0:W]
    thr = pixel.bayer(HORIZON, W)
    thr2 = np.roll(thr, 1, axis=1)
    d = np.hypot((xs - SUN[0]) * 0.8, (ys - SUN[1]) * 1.6)
    pos = ys / HORIZON * 4.0 + np.clip(1 - d / 70, 0, 1) * 1.6
    # before the mirror: dusk on the left, dawn on the right
    left, mid, right = (ramp_color(P[k], pos, thr) for k in ("dusk", "glow", "dawn"))
    wl = np.clip((xs - 70) / 70, 0, 1)
    wr = np.clip((xs - 180) / 70, 0, 1)
    a = np.where((thr2 < wl)[..., None], mid, left)
    arr[:HORIZON] = np.where((thr2 < wr)[..., None], right, a)


def _clouds(d):
    for (x0, x1, y, col, lit) in [(6, 70, 22, (60, 42, 88), (98, 66, 118)), (24, 96, 34, (72, 50, 98), (120, 80, 126)),
                                  (200, 262, 26, (122, 92, 136), (214, 150, 136)),
                                  (228, 306, 40, (160, 108, 132), (240, 176, 140)),
                                  (120, 176, 52, (150, 92, 126), (232, 150, 126))]:
        d.line([(x0, y), (x1, y)], fill=col)
        d.line([(x0 + 4, y - 1), (x1 - 10, y - 1)], fill=col)
        d.line([(x0 + 6, y + 1), (x1 - 4, y + 1)], fill=lit)


def _sea(arr):
    h = H - HORIZON
    ys, xs = np.mgrid[0:h, 0:W]
    t = np.clip(ys / 55.0, 0, 1) ** 0.8
    arr[HORIZON:] = ramp_color(P["sea"], t * 4.0, pixel.bayer(h, W))


def _london(d):
    xs = [0, 6, 6, 14, 14, 20, 20, 30, 30, 46, 46, 54, 54, 66, 66, 78, 78, 92, 92, 100]
    ys = [104, 104, 100, 100, 106, 106, 102, 102, 104, 104, 100, 100, 105, 105, 101, 101, 106, 106, 108, 108]
    d.polygon(list(zip(xs, ys)) + [(100, 114), (0, 114)], fill=P["far_l"])
    # the White Tower: a square keep with four corner turrets and cupolas
    d.rectangle((3, 86, 17, 110), fill=P["far_l"])
    d.rectangle((14, 86, 17, 110), fill=P["far_l_lit"])
    for x in (3, 8, 14):
        d.rectangle((x, 80, x + 2, 86), fill=P["far_l"])
        d.ellipse((x - 1, 77, x + 3, 81), fill=P["far_l_dk"])
    d.rectangle((14, 80, 16, 86), fill=P["far_l_lit"])
    for x in (6, 11):
        d.point((x, 94), fill=P["far_l_dk"]); d.point((x, 100), fill=P["far_l_dk"])
    # St Paul's: portico, drum with columns, dome, lantern, ball and cross
    d.rectangle((20, 88, 50, 108), fill=P["far_l"])
    d.polygon([(20, 88), (35, 83), (50, 88)], fill=P["far_l"])
    d.rectangle((44, 88, 50, 108), fill=P["far_l_lit"])
    d.rectangle((24, 74, 46, 84), fill=P["far_l"])
    for x in range(25, 46, 3):
        d.line([(x, 76), (x, 83)], fill=P["far_l_dk"])
    d.rectangle((42, 74, 46, 84), fill=P["far_l_lit"])
    d.pieslice((23, 58, 47, 90), 180, 360, fill=P["far_l"])
    d.pieslice((23, 58, 47, 90), 290, 360, fill=P["far_l_lit"])
    for x in (29, 35, 41):
        d.line([(x, 62), (x + (x - 35) // 3, 73)], fill=P["far_l_dk"])
    d.rectangle((33, 52, 37, 59), fill=P["far_l"]); d.rectangle((36, 52, 37, 59), fill=P["far_l_lit"])
    d.polygon([(33, 52), (35, 49), (37, 52)], fill=P["far_l"])
    d.point((35, 46), fill=C["gold"]); d.line([(35, 45), (35, 48)], fill=P["far_l_dk"])
    d.line([(34, 46), (36, 46)], fill=P["far_l_dk"])
    # stone quay: paving on top, courses of blocks on the face
    d.rectangle((0, 114, 100, 117), fill=P["stone_hi"])
    d.line([(0, 114), (100, 114)], fill=(186, 168, 176))
    d.rectangle((0, 118, 100, H), fill=P["stone"])
    for row, y in enumerate(range(118, H, 6)):
        d.line([(0, y), (100, y)], fill=P["mortar"])
        off = 0 if row % 2 else 7
        for x in range(off, 100, 14):
            d.line([(x, y), (x, y + 5)], fill=P["mortar"])
        d.line([(0, y + 1), (100, y + 1)], fill=P["stone_dk"])
    d.rectangle((96, 118, 100, H), fill=P["stone_dk"])
    d.line([(100, 114), (100, H)], fill=P["mortar"])
    for x in range(0, 101, 2):
        d.point((x, 140 + (x % 3 == 0)), fill=(62, 78, 86))
    d.rectangle((0, 142, 100, H), fill=P["stone_dk"])
    d.rectangle((88, 110, 92, 114), fill=P["far_l_dk"]); d.rectangle((87, 109, 93, 110), fill=P["stone_hi"])


def _boston(d, img):
    # Beacon Hill with the beacon mast, behind everything
    d.ellipse((268, 84, 380, 140), fill=P["hill"])
    d.pieslice((268, 84, 380, 140), 180, 235, fill=P["hill_hi"])
    d.rectangle((268, 104, 320, 114), fill=P["hill_dk"])
    d.line([(311, 60), (311, 90)], fill=P["far_r_dk"])
    for yy in (66, 74, 82):
        d.line([(309, yy), (313, yy)], fill=P["far_r_dk"])
    d.rectangle((309, 56, 313, 59), fill=INK); d.point((310, 56), fill=C["gold"])
    for tx, ty in ((276, 93), (283, 90), (304, 94), (317, 91)):
        d.ellipse((tx - 3, ty - 3, tx + 3, ty + 2), fill=P["hill_dk"])
        d.ellipse((tx - 3, ty - 3, tx, ty), fill=P["hill"])
        d.point((tx - 2, ty - 2), fill=P["hill_hi"])
        d.line([(tx, ty + 3), (tx, ty + 6)], fill=P["far_r_dk"])
    houses = [(214, 227, 103, 5), (227, 238, 100, 5), (238, 251, 104, 4), (251, 262, 99, 6),
              (262, 274, 102, 5), (274, 288, 100, 6), (300, 312, 103, 4), (312, 322, 101, 5)]
    roof, roof_lit = (112, 70, 82), (170, 104, 104)
    for i, (x0, x1, top, gable) in enumerate(houses):
        wall = P["far_r"] if i % 2 else (168, 120, 124)
        d.rectangle((x0, top, x1 - 1, 113), fill=wall)
        d.line([(x0, top), (x0, 113)], fill=P["far_r_lit"])
        mid = (x0 + x1 - 1) // 2
        d.polygon([(x0 - 1, top), (mid, top - gable), (x1, top)], fill=roof)
        d.line([(x0 - 1, top), (mid, top - gable)], fill=roof_lit)
        cx = x1 - 4 if i % 2 else x0 + 2
        d.rectangle((cx, top - gable - 1, cx + 1, top - 1), fill=P["far_r_dk"])
        d.point((cx, top - gable - 1), fill=P["far_r_lit"])
        for wx in range(x0 + 2, x1 - 2, 4):
            for wy in (top + 3, top + 7):
                if wy < 112:
                    lit = (wx * 3 + wy + i) % 4 == 0
                    d.rectangle((wx, wy, wx + 1, wy + 1), fill=P["lamp"] if lit else P["far_r_dk"])
    pixel.dither_rect(img, (214, 110, 320, 114), P["far_r_dk"], density=0.5)
    # Old North Church: brick tower, white tiered steeple (the lanterns are lit per frame)
    bx = 288
    d.rectangle((bx, 72, bx + 12, 113), fill=P["brick"])
    d.rectangle((bx + 8, 72, bx + 12, 113), fill=P["brick_dk"])
    for yy in (80, 92, 104):
        d.rectangle((bx + 4, yy, bx + 6, yy + 4), fill=P["far_r_dk"])
    d.rectangle((bx + 1, 62, bx + 11, 72), fill=P["steeple"])
    d.rectangle((bx + 8, 62, bx + 11, 72), fill=P["steeple_dk"])
    d.rectangle((bx + 3, 54, bx + 9, 62), fill=P["steeple"])
    d.rectangle((bx + 7, 54, bx + 9, 62), fill=P["steeple_dk"])
    d.rectangle((bx + 4, 48, bx + 8, 54), fill=P["steeple"])
    d.rectangle((bx + 7, 48, bx + 8, 54), fill=P["steeple_dk"])
    d.polygon([(bx + 4, 48), (bx + 6, 36), (bx + 8, 48)], fill=P["steeple"])
    d.line([(bx + 7, 40), (bx + 8, 48)], fill=P["steeple_dk"])
    d.line([(bx + 6, 32), (bx + 6, 36)], fill=INK); d.point((bx + 7, 33), fill=C["gold"])
    # wooden wharf: plank deck, stringer, pilings into the sea
    d.rectangle((220, 114, 320, 117), fill=C["wood_hi"])
    for x in range(222, 320, 7):
        d.line([(x, 114), (x, 117)], fill=C["wood"])
    d.rectangle((220, 118, 320, 122), fill=C["wood"])
    d.line([(220, 122), (320, 122)], fill=C["wood_sh"])
    for x in range(222, 320, 13):
        d.rectangle((x, 123, x + 3, H), fill=C["wood_sh"])
        d.line([(x, 123), (x, H)], fill=C["wood"])
        for yy in range(137, H, 3):
            d.point((x + 1, yy), fill=C["wood_deep"])
    d.line([(222, 126), (235, 138)], fill=C["wood_sh"]); d.line([(261, 126), (274, 138)], fill=C["wood_sh"])
    # crates and a barrel on the wharf
    d.rectangle((296, 104, 306, 113), fill=C["wood"]); d.rectangle((296, 104, 298, 113), fill=C["wood_hi"])
    d.line([(296, 104), (306, 113)], fill=C["wood_sh"])
    d.rectangle((308, 106, 315, 113), fill=C["wood_sh"]); d.line([(308, 109), (315, 109)], fill=C["wood_deep"])
    d.rectangle((308, 106, 309, 113), fill=C["wood"])


@lru_cache(maxsize=1)
def _layers():
    """(static RGB array, sea mask): the sea mask marks open water the animation may draw on."""
    base = np.zeros((H, W, 3), np.uint8)
    _sky(base)
    _sea(base)
    img = Image.fromarray(base)
    d = ImageDraw.Draw(img)
    _clouds(d)
    cx, cy = SUN
    d.line([(0, HORIZON), (W, HORIZON)], fill=(150, 116, 150))
    d.line([(96, HORIZON), (230, HORIZON)], fill=(236, 170, 136))
    land = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(land)
    _london(ld)
    _boston(ld, land)
    sky_sea = np.array(img.transpose(Image.FLIP_LEFT_RIGHT))
    land = land.transpose(Image.FLIP_LEFT_RIGHT)
    la = np.array(land)
    solid = la[..., 3] > 0
    out = sky_sea.copy()
    out[solid] = la[solid][:, :3]
    # the sun goes behind the land but in front of the sky: redraw it into sky pixels only
    sun = mask(lambda m: m.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=255)) > 0
    core = mask(lambda m: m.ellipse((cx - 8, cy - 9, cx + 8, cy + 7), fill=255)) > 0
    sky_rows = np.zeros_like(sun)
    sky_rows[:HORIZON] = True
    out[sun & sky_rows & ~solid] = C["sun"]
    out[core & sky_rows & ~solid] = C["sun_core"]
    sea = ~solid
    sea[:HORIZON + 1] = False
    return out, sea


def static_backdrop():
    return _layers()[0]


# --- the animated sea -----------------------------------------------------------------

_YS = np.arange(H)[:, None]
_XS = np.arange(W)[None, :]


def sea_band(y):
    """Index of the sea colour band at row y."""
    return min(4, int(np.clip((y - HORIZON) / 55.0, 0, 1) ** 0.8 * 4.0))


@lru_cache(maxsize=1)
def _swell_rows():
    rows, y, k = [], HORIZON + 3.0, 0
    while y < H:
        yi = int(y)
        depth = (yi - HORIZON) / 55.0
        rows.append((yi, k, 0.4 + min(depth, 1.6) * 1.6, max(0.05, 0.22 - depth * 0.14), sea_band(yi)))
        y += 2.0 + (y - HORIZON) * 0.16
        k += 1
    return rows


def animate_sea(arr, t, calm=0.0, glitter=1.0):
    """Swells drifting, whitecaps twinkling and the sun's glitter path, on open water only."""
    sea = _layers()[1]
    for yi, k, amp, freq, band in _swell_rows():
        light = np.array(P["sea"][max(0, band - 1)])
        drift = t * (0.9 + 0.2 * k % 3) * freq * 2.0
        xs = np.arange(W)
        on = np.sin(xs * freq + k * 1.7 - drift) > 0.55 + 0.3 * calm
        dy = np.round(amp * np.sin(xs * freq * 0.5 + k + t * 0.8)).astype(int)
        yy = np.clip(yi + dy, 0, H - 1)
        sel = on & sea[yy, xs]
        arr[yy[sel], xs[sel]] = light
    # whitecaps: more and bigger toward the viewer, each lives about a second
    slot = int(t * 3)
    for i in range(34):
        seed = (slot + i * 7) // 3
        yy = int(HORIZON + 4 + rnd("capy", i, seed) ** 0.7 * 60)
        xx = int(96 + rnd("capx", i, seed) * 128)
        size = 1 + int((yy - HORIZON) / 16)
        life = ((slot + i * 7) % 3)
        if life == 2 and size < 2:
            continue
        for x in range(xx, min(W, xx + size + 1)):
            if sea[yy, x]:
                arr[yy, x] = P["cap"]
        if size > 2 and sea[yy - 1, xx + 1]:
            arr[yy - 1, xx + 1] = P["cap"]
    # glitter path under the sun, widening toward the viewer
    if glitter > 0:
        f = int(t * 8)
        for yy in range(HORIZON + 1, H, 2):
            spread = 4 + (yy - HORIZON) * 0.45
            n = int(round(3 * glitter))
            for j in range(n):
                xx = int(SUN[0] + (rnd("glx", yy, j, f) - 0.5) * 2 * spread)
                ln = 1 + int(rnd("gll", yy, j, f) * (2 + (yy - HORIZON) / 12))
                col = C["sun"] if yy < HORIZON + 10 else C["glint"]
                for x in range(xx, min(W, xx + ln + 1)):
                    if sea[yy, x]:
                        arr[yy, x] = col
    # foam around the pilings and along the quay wall
    for x in range(1, BOSTON_EDGE - 2, 13):
        px = mx(x + 221, 1) - 3
        w = 2 + (int(t * 4 + x) % 2)
        for xx in range(px - 1, px + w + 2):
            if 0 <= xx < W and sea[140, xx]:
                arr[140, xx] = P["cap"]
    for y in range(128, H, 5):
        ln = 2 + int(1.5 + 1.5 * math.sin(t * 3 + y))
        for xx in range(LONDON_EDGE - ln, LONDON_EDGE):
            if sea[y, xx]:
                arr[y, xx] = P["cap"]


def rain(img, t, amount=1.0):
    """London drizzle, falling on the right-hand third."""
    d = ImageDraw.Draw(img)
    n = int(56 * amount)
    for i in range(n):
        x0 = 202 + rnd("rx", i) * 118
        speed = 70 + rnd("rs", i) * 30
        y = (rnd("ry", i) * 120 + t * speed) % 120 + 4
        x = x0 - (y / 3)
        if x < 200 or (x < 236 and 70 < y < 112 and abs(x - 218) < 18):
            continue
        d.line([(x, y), (x - 1, y + 3)], fill=P["rain"])


# --- flags, ships and small life ---------------------------------------------------------

def union_canton(fd, x, y, w, h):
    """The pre-1801 Union: St George's cross, fimbriated white, over St Andrew's saltire on blue."""
    fd.rectangle((x, y, x + w - 1, y + h - 1), fill=C["flag_blue"])
    fd.line((x, y, x + w - 1, y + h - 1), fill=C["flag_white"])
    fd.line((x, y + h - 1, x + w - 1, y), fill=C["flag_white"])
    cx, cy = x + w // 2, y + h // 2
    fd.rectangle((cx - 1, y, cx + 1, y + h - 1), fill=C["flag_white"])
    fd.rectangle((x, cy - 1, x + w - 1, cy + 1), fill=C["flag_white"])
    fd.line((cx, y, cx, y + h - 1), fill=C["flag_red"])
    fd.line((x, cy, x + w - 1, cy), fill=C["flag_red"])


@lru_cache(maxsize=None)
def flag_cloth(kind):
    """Flat flag images, hoist on the left: the Grand Union (the Continental Colours, 1775-77),
    George III's royal standard (before 1801), the red ensign and a white flag of surrender."""
    if kind == "grand_union":
        w, h = 20, 13
        fl = Image.new("RGB", (w, h))
        fd = ImageDraw.Draw(fl)
        for r in range(h):
            fd.line([(0, r), (w - 1, r)], fill=C["flag_red"] if r % 2 == 0 else C["flag_white"])
        union_canton(fd, 0, 0, 9, 7)
        return fl
    if kind == "royal_standard":
        w, h = 18, 12
        fl = Image.new("RGB", (w, h))
        fd = ImageDraw.Draw(fl)
        red, blue, gold = (200, 40, 50), (46, 70, 170), (246, 200, 70)
        fd.rectangle((0, 0, 8, 5), fill=red); fd.rectangle((9, 0, 17, 5), fill=blue)
        fd.rectangle((0, 6, 8, 11), fill=blue); fd.rectangle((9, 6, 17, 11), fill=red)
        for px in [(2, 1), (4, 3), (6, 1), (11, 2), (13, 4), (15, 2), (4, 8), (3, 9), (12, 8), (14, 9), (13, 7)]:
            fd.point(px, fill=gold if px[1] < 6 or px[0] < 9 else (240, 240, 240))
        return fl
    if kind == "red_ensign":
        fl = Image.new("RGB", (22, 13), C["flag_red"])
        union_canton(ImageDraw.Draw(fl), 0, 0, 10, 7)
        return fl
    if kind == "white":
        fl = Image.new("RGB", (16, 11), C["flag_white"])
        ImageDraw.Draw(fl).line((0, 10, 15, 10), fill=C["white_sh"])
        return fl
    raise ValueError(kind)


def waving(fl, t, phase=0.0, amp=1.4, flip=False):
    """A flag rippling in the wind: an RGBA image 3px taller than the cloth."""
    if flip:
        fl = fl.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.array(fl)
    h, w = a.shape[:2]
    out = np.zeros((h + 3, w, 4), np.uint8)
    for i in range(w):
        hoist = (w - 1 - i) if flip else i
        k = hoist * 0.55 - t * 5.0 + phase
        dy = int(round(amp * math.sin(k) * min(1.0, hoist / 5)))
        col = a[:, i].astype(np.float32)
        if math.cos(k) < -0.3:
            col *= 0.82
        out[1 + dy:1 + dy + h, i, :3] = col.astype(np.uint8)
        out[1 + dy:1 + dy + h, i, 3] = 255
    return Image.fromarray(out)


def flagpole(img, x, top, bottom, kind, t, phase=0.0, flip=False, amp=1.4):
    d = ImageDraw.Draw(img)
    d.line([(x, top - 2), (x, bottom)], fill=INK)
    d.point((x, top - 3), fill=C["gold"])
    fl = waving(flag_cloth(kind), t, phase, amp, flip)
    if flip:
        img.paste(fl, (x - fl.width, top - 1), fl)
    else:
        img.paste(fl, (x + 1, top - 1), fl)


@lru_cache(maxsize=None)
def packet_sprite():
    """A small two-masted packet, backlit by the sun, bow to the right."""
    s = Canvas(28, 24)
    hull, sail, sail_lit = (58, 40, 70), (214, 196, 196), (255, 226, 176)
    s.poly([(3, 17), (24, 17), (21, 21), (6, 21)], hull)
    s.line([(10, 4), (10, 17)], hull); s.line([(18, 6), (18, 17)], hull)
    s.poly([(5, 6), (10, 5), (10, 15), (6, 14)], sail)
    s.poly([(13, 7), (18, 6), (18, 15), (14, 14)], sail)
    s.line([(5, 6), (6, 14)], sail_lit); s.line([(13, 7), (14, 14)], sail_lit)
    s.poly([(18, 8), (24, 16), (18, 16)], sail)
    s.px((10, 3), C["flag_red"]); s.px((11, 3), C["flag_red"])
    return s.done((40, 26, 52))


def packet_ship(img, t):
    """A packet boat crossing the horizon from west to east over the length of the song."""
    x = int(104 + (t / 290.0) * 86)
    y = 81 + int(round(math.sin(t * 1.3) * 0.6))
    spr = packet_sprite()
    img.paste(spr, (x, y), spr)
    d = ImageDraw.Draw(img)
    d.line([(x - 8, y + 22), (x + 3, y + 22)], fill=P["cap"])


def whale(img, t, x=190, y=93, every=23.0):
    """A whale surfacing now and then far out, with a spout."""
    k = (t % every) / every * every
    if k > 3.2:
        return
    d = ImageDraw.Draw(img)
    rise = min(1.0, k / 0.4) * min(1.0, (3.2 - k) / 0.4)
    if rise <= 0:
        return
    d.line([(x, y), (x + 6, y)], fill=P["sea"][3])
    d.line([(x + 1, y - 1), (x + 4, y - 1)], fill=P["sea"][3])
    if 0.5 < k < 2.6:
        h = min(6, int((k - 0.5) * 12))
        for i in range(h):
            d.point((x + 2 + (i % 2) * (1 if i > 3 else 0), y - 2 - i), fill=P["cap"])
        if h >= 5:
            for px in [(x, y - 7), (x + 4, y - 7), (x - 1, y - 6), (x + 5, y - 6)]:
                d.point(px, fill=P["cap"])


def lanterns(img, t):
    """Two lanterns in the Old North Church steeple ("two if by sea"), flickering."""
    d = ImageDraw.Draw(img)
    bx = 288
    for i, ox in enumerate((4, 7)):
        x = mx(bx + ox)
        lit = C["gold_hi"] if rnd("lan", i, int(t * 6)) < 0.8 else P["lamp"]
        d.point((x, 66), fill=lit); d.point((x, 67), fill=P["lamp"])


def chimney_smoke(img, t):
    """Curls of smoke from the Boston chimneys, drifting east."""
    d = ImageDraw.Draw(img)
    houses = [(214, 227, 103, 5), (227, 238, 100, 5), (238, 251, 104, 4), (251, 262, 99, 6),
              (262, 274, 102, 5), (274, 288, 100, 6), (300, 312, 103, 4), (312, 322, 101, 5)]
    for i, (x0, x1, top, gable) in enumerate(houses):
        cx = x1 - 4 if i % 2 else x0 + 2
        x, y = mx(cx) - 1, top - gable - 3
        for k in range(4):
            age = (t * 0.7 + k / 4 + i * 0.37) % 1.0
            px = x + age * 7 + math.sin(age * 6 + i) * 1.2
            py = y - age * 10
            col = mix((206, 184, 196), (150, 120, 150), age)
            d.point((int(px), int(py)), fill=col)
            if age < 0.5:
                d.point((int(px) + 1, int(py)), fill=col)


def gulls(img, t):
    d = ImageDraw.Draw(img)
    for i in range(3):
        a = t * (0.35 + i * 0.07) + i * 2.1
        x = 38 + i * 21 + math.cos(a) * 16
        y = 30 + i * 6 + math.sin(a * 1.7) * 5
        flap = int(t * 5 + i) % 2
        col = (250, 236, 226)
        d.point((int(x), int(y)), fill=col)
        d.point((int(x) - 1, int(y) - flap), fill=col); d.point((int(x) + 1, int(y) - flap), fill=col)
        d.point((int(x) - 2, int(y) - 1 + flap), fill=col); d.point((int(x) + 2, int(y) - 1 + flap), fill=col)


def shores(t, calm=0.0, rain_amount=1.0):
    """The whole shores backdrop at time t, without the characters (an RGB image)."""
    arr = static_backdrop().copy()
    animate_sea(arr, t, calm)
    img = Image.fromarray(arr)
    lanterns(img, t)
    chimney_smoke(img, t)
    gulls(img, t)
    whale(img, t)
    packet_ship(img, t)
    flagpole(img, mx(268), 44, 114, "grand_union", t, phase=1.0)
    flagpole(img, mx(52), 44, 114, "royal_standard", t, phase=0.0)
    rain(img, t, rain_amount)
    return img


def shore_labels(ui, cam, alpha=1.0):
    """BOSTON and LONDON in the top corners of the screen, for whichever shore is in view."""
    if alpha <= 0:
        return
    d = ImageDraw.Draw(ui)
    if cam.visible((0, 60, BOSTON_EDGE - 20, 116)):
        pixel.text(ui, (8, 2), "BOSTON", SILK, (255, 230, 190), shadow=(90, 60, 70))
        d.line([(8, 14), (44, 14)], fill=(214, 150, 140))
    if cam.visible((LONDON_EDGE + 20, 60, W, 116)):
        pixel.text(ui, (W - 8, 2), "LONDON", SILK, (218, 206, 236), shadow=(30, 20, 50), anchor="ra")
        d.line([(W - 46, 14), (W - 8, 14)], fill=(120, 96, 150))


def shadow_under(img, x, y, w=26, col=None):
    """A dithered contact shadow under a character's feet."""
    dither_rect(img, (int(x - w // 2), y - 1, int(x + w // 2), y + 1), col or (70, 46, 50), density=0.75)


__all__ = ["HORIZON", "SUN", "FEET_Y", "WASH_X", "GEORGE_X", "shores", "shore_labels", "flagpole",
           "flag_cloth", "waving", "packet_sprite", "mx", "P", "outline_text"]
