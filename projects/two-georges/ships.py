"""Broadsides: the ship duel for Verse 4. The Continental ship Alfred sits west (left, bow east) and
HMS Royal George, a 100-gun first-rate, sits east (right, bow west), at dusk with the sun between them.

Registered as video.SCENES["ships"] = (world, front): `world(c)` draws the set behind the
characters and `front(c)` draws each ship's bulwark over the Georges' boots so they stand on deck.
Royal George takes damage in stages (RG_DAMAGE), cannon volleys (VOLLEYS) leave smoke that rolls
across the gap, and `c.ship` (a dict a gag may set) overrides any of the time-driven state.

Also here: small versions of both ships (`small_ship`) that sail in on the shores set.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import video as V
from engine import INK, H, W, Canvas, clamp, lerp, mirror, rnd
from pixelart import pixel
from scene import flag_cloth, waving

HORIZON = 96
WL = 142                                 # both waterlines
W_FEET = (127, 116)                      # Washington at Alfred's bow rail
G_FEET = (195, 106)                      # George on Royal George's forecastle
SHIP_SHOTS = {
    "duel": (160, 90, 6), "alfred": (112, 92, 12), "royal": (206, 82, 12), "gap": (160, 104, 12),
    "sky": (160, 46, 12), "wx": (126, 88, 18), "gx": (196, 78, 18), "two": (160, 92, 7),
    "rgwide": (222, 101, 8), "stern": (270, 116, 12),
}

P = {
    "sky0": (34, 26, 70), "sky1": (60, 38, 100), "sky2": (104, 52, 124), "sky3": (160, 74, 128),
    "sky4": (214, 106, 118), "sky5": (246, 152, 106), "sky6": (255, 204, 128),
    "sun": (255, 246, 212), "glow": (255, 224, 150),
    "sea0": (170, 96, 138), "sea1": (104, 62, 124), "sea2": (60, 44, 100), "sea3": (34, 28, 72),
    "foam": (236, 222, 236), "far": (150, 96, 146),
    "ochre": (204, 142, 74), "ochre_sh": (146, 92, 74), "wale": (46, 34, 58), "port": (24, 16, 32),
    "lid": (178, 50, 56), "gilt": (246, 202, 96), "frieze": (58, 76, 150), "window": (255, 222, 124),
    "buff": (214, 186, 140), "buff_sh": (158, 128, 112),
    "mast": (112, 72, 60), "mast_sh": (70, 44, 58), "rope": (66, 44, 70), "rope_far": (116, 72, 110),
    "sail_hi": (255, 222, 172), "sail_lit": (226, 170, 156), "sail": (168, 128, 156), "sail_sh": (130, 98, 140),
    "sail_dk": (92, 70, 118),
    "smoke_hi": (248, 234, 222), "smoke": (208, 190, 208), "smoke_sh": (152, 134, 174), "smoke_dk": (104, 90, 138),
    "red": (204, 40, 50), "white": (248, 246, 240), "gold": (255, 210, 90),
    "fire": (255, 150, 50), "fire_hi": (255, 230, 120), "night": (14, 12, 34),
}

# Royal George's damage, by time: (from, level). 0 intact; 1 holed fore topsail and hull;
# 2 the main topmast chopped away ("your family tree in two"); 3 dismasted after the big broadside.
RG_DAMAGE = [(0.0, 0), (190.45, 1), (197.14, 2), (209.2, 3)]
ALFRED_DAMAGE = [(0.0, 0), (188.6, 1)]
MAST_CHOP = 197.14                       # the main topmast comes down (the hatchet lands)
# Cannon volleys: (time, shooter "al" or "rg", number of guns, hit?)
VOLLEYS = [
    (187.62, "rg", 9, False), (188.05, "rg", 7, False), (188.42, "rg", 6, True),
    (190.10, "al", 5, True),
    (207.92, "al", 6, True), (208.34, "al", 6, True), (208.76, "al", 8, True), (209.18, "al", 10, True),
]


def damage(table, t):
    lvl = 0
    for a, v in table:
        if t >= a:
            lvl = v
    return lvl


def state(c):
    """The ship set's state at c.t, with any overrides a gag put in c.ship."""
    t = c.t
    s = dict(rg=damage(RG_DAMAGE, t), al=damage(ALFRED_DAMAGE, t), sink=0.0, dark=0.0, fires=t >= 209.0,
             volleys=True, alfred_x=0.0, stars=0.0)
    s.update(getattr(c, "ship", None) or {})
    return s


# --- the static backdrop -----------------------------------------------------------------------

def smooth_bands(stops, h, width, soft=3, phase=0):
    """Banded vertical gradient: flat bands with short ordered-dither seams between them."""
    arr = np.zeros((h, width, 3), np.uint8)
    n = len(stops)
    thr = pixel.bayer(h, width, phase)
    for i in range(h):
        v = i / max(1, h - 1) * (n - 1)
        k = min(int(v), n - 2)
        f = v - k
        t = min(max((f - 0.5) * (h / (n - 1)) / (2 * soft) + 0.5, 0.0), 1.0)
        a, b = np.array(P[stops[k]]), np.array(P[stops[k + 1]])
        arr[i] = np.where((thr[i] < t)[:, None], b, a)
    return arr


@lru_cache(maxsize=1)
def backdrop():
    img = Image.new("RGB", (W, H), P["sky0"])
    img.paste(Image.fromarray(smooth_bands(["sky0", "sky1", "sky2", "sky3", "sky4", "sky5", "sky6"], HORIZON, W)))
    d = ImageDraw.Draw(img)
    glow = pixel.mask(lambda m: m.ellipse((126, 64, 194, 124), fill=255), (W, H))
    pixel.dither(img, glow * 0.55, P["sky6"])
    glow2 = pixel.mask(lambda m: m.ellipse((140, 76, 180, 112), fill=255), (W, H))
    pixel.dither(img, glow2 * 0.6, P["glow"])
    d.ellipse((150, 83, 170, 103), fill=P["sun"])
    for x0, x1, y, col in [(8, 96, 40, "sky4"), (30, 120, 44, "sky3"), (210, 300, 34, "sky4"),
                           (232, 312, 38, "sky3"), (60, 150, 70, "sky5"), (186, 262, 64, "sky5"),
                           (0, 70, 20, "sky2"), (250, 320, 16, "sky2")]:
        d.line((x0, y, x1, y), fill=P[col])
        d.line((x0 + 6, y + 1, x1 - 10, y + 1), fill=P[col])
    img.paste(Image.fromarray(smooth_bands(["sea0", "sea1", "sea2", "sea3"], H - HORIZON, W, soft=4, phase=1)),
              (0, HORIZON))
    d.line((0, HORIZON, W, HORIZON), fill=P["sky5"])
    for x, s in ((34, 1), (286, -1), (262, -1)):
        d.polygon([(x - 7 * s, 95), (x + 7 * s, 95), (x + 5 * s, 97), (x - 5 * s, 97)], fill=P["far"])
        d.line((x, 86, x, 95), fill=P["far"])
        d.polygon([(x - 3, 87), (x + 3, 87), (x + 4, 93), (x - 4, 93)], fill=P["far"])
    return np.array(img)


@lru_cache(maxsize=1)
def _swells():
    """Swell dashes: (y, x, length, colour index), sparse near the horizon and longer toward the viewer."""
    out, y, gap = [], HORIZON + 3, 3
    k = 0
    while y < H:
        depth = (y - HORIZON) / (H - HORIZON)
        for _ in range(int(10 + 14 * depth)):
            x = int(rnd("swx", k) * W)
            ln = int(2 + 8 * depth + rnd("swl", k) * 4)
            col = "sea0" if depth < 0.35 else "sea1" if depth < 0.7 else "sea2"
            out.append((y, x, ln, col, 0.4 + depth * 1.6))
            k += 1
        y += gap
        gap += 1 if depth > 0.2 else 0
    return out


def sea(img, t, dark=0.0):
    d = ImageDraw.Draw(img)
    for y, x, ln, col, speed in _swells():
        xx = (x + t * speed * 3) % (W + 20) - 10
        d.line((xx, y, xx + ln, y), fill=P[col])
    if dark < 0.9:
        f = int(t * 8)
        for yy in range(HORIZON + 1, H, 2):
            depth = (yy - HORIZON) / (H - HORIZON)
            half = 4 + depth * 26
            for k in range(int((3 + depth * 6) * (1 - dark))):
                x = int(160 + (rnd("gx", yy, k, f) - 0.5) * 2 * half)
                ln = 1 + int(rnd("gl", yy, k, f) * (3 + depth * 5))
                d.line((x, yy, x + ln, yy), fill=P["glow"] if rnd("gc", yy, k, f) < 0.7 else P["sun"])


# --- ships ------------------------------------------------------------------------------------------

def sheer(x, x0, x1, rise=4):
    """Hull sheer: rail and gun rows rise toward bow and stern."""
    tt = (x - (x0 + x1) / 2) / ((x1 - x0) / 2)
    return -int(round(rise * tt * tt))


def sail(d, cx, top, bot, w_top, w_bot, belly=3, torn=False, holes=()):
    """A square sail side-on, bellied toward the viewer, backlit on its bow side."""
    l0, r0 = cx - w_top // 2, cx + w_top // 2
    l1, r1 = cx - w_bot // 2, cx + w_bot // 2
    foot = [(r1 - i, bot + int(round(belly * math.sin(math.pi * i / (r1 - l1))))) for i in range(0, r1 - l1 + 1)]
    d.polygon([(l0, top), (r0, top), (r1, bot)] + foot + [(l1, bot)], fill=P["sail"])
    d.polygon([(r0 - 6, top + 1), (r0, top + 1), (r1, bot), (r1 - 8, bot + 1)], fill=P["sail_lit"])
    d.line((r0, top + 1, r1, bot - 1), fill=P["sail_hi"])
    d.line((l0, top + 1, r0 - 7, top + 1), fill=P["sail_sh"])
    d.polygon([(l0, top), (l0 + 3, top), (l1 + 3, bot + 1), (l1, bot)], fill=P["sail_sh"])
    for x, y in foot:
        d.point((x, y), fill=P["sail_dk"])
    mid = top + (bot - top) * 2 // 5
    d.line((l0 + 4, mid, r0 - 7, mid), fill=P["sail_sh"])
    if torn:
        hx, hy = cx - 2, top + (bot - top) * 3 // 5
        hole = [(hx - 6, hy - 3), (hx - 2, hy - 5), (hx + 2, hy - 2), (hx + 5, hy - 5), (hx + 6, hy),
                (hx + 7, hy + 4), (hx + 1, hy + 4), (hx - 2, hy + 2), (hx - 7, hy + 3)]
        d.polygon(hole, fill=(0, 0, 0, 0))
        d.line(hole + [hole[0]], fill=P["sail_dk"])
        d.polygon([(hx - 3, hy + 3), (hx + 1, hy + 4), (hx + 3, hy + 12), (hx - 1, hy + 10)], fill=P["sail_lit"])
        d.line((hx + 1, hy + 4, hx + 3, hy + 12), fill=P["sail_hi"])
    for hx, hy, r in holes:                                  # round shot holes
        d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=(0, 0, 0, 0))
        d.arc((hx - r - 1, hy - r - 1, hx + r + 1, hy + r + 1), 200, 20, fill=P["sail_dk"])


def furled(d, cx, y, w):
    for x in range(cx - w // 2, cx + w // 2 + 1):
        lump = 1 + ((x * 7) % 5 == 0)
        d.line((x, y + 1, x, y + 1 + lump), fill=P["sail_sh"])
        if (x - cx) % 6 == 0:
            d.point((x, y + 2), fill=P["sail_dk"])
    d.line((cx + w // 2 - 5, y + 1, cx + w // 2, y + 1), fill=P["sail_lit"])


def shrouds(d, x, top, rail_y):
    for side in (-1, 1):
        a = (x + side * 2, top)
        d.line(a + (x + side * 7, rail_y), fill=P["rope"])
        d.line(a + (x + side * 11, rail_y), fill=P["rope_far"])
        for y in range(top + 5, rail_y - 1, 5):
            tt = (y - top) / (rail_y - top)
            xa, xb = x + side * (2 + 5 * tt), x + side * (2 + 9 * tt)
            d.line((min(xa, xb) + 1, y, max(xa, xb) - 1, y), fill=P["rope_far"])


def yard(d, cx, y, w):
    d.line((cx - w // 2 - 2, y, cx + w // 2 + 2, y), fill=P["mast_sh"])


def mast(d, x, top, bot):
    d.line((x, top, x, bot), fill=P["mast"])
    d.line((x - 1, top + 6, x - 1, bot), fill=P["mast_sh"])
    d.rectangle((x - 3, top + 22, x + 3, top + 23), fill=P["mast_sh"])


def stump(d, x, top, bot):
    """A mast shot away: a splintered stump."""
    d.line((x, top, x, bot), fill=P["mast"])
    d.line((x - 1, top + 2, x - 1, bot), fill=P["mast_sh"])
    for dx, h in ((-1, 3), (0, 1), (1, 4), (2, 2)):
        d.line((x + dx, top, x + dx, top - h), fill=P["mast"])


def rags(d, x, y, w, seed):
    """Canvas hanging in shreds from a broken yard."""
    for i in range(w):
        if rnd("rag", seed, i) < 0.35:
            continue
        h = 2 + int(rnd("ragh", seed, i) * 8)
        d.line((x + i, y, x + i + (1 if i % 3 == 0 else 0), y + h), fill=P["sail_sh"] if i % 2 else P["sail"])


def hanover_tree(d, cx, cy):
    """The House of Hanover, painted on the main topsail: George I > George II > Frederick > George III."""
    pts = [(cx - 6, cy - 6), (cx - 2, cy - 2), (cx + 2, cy + 2), (cx + 6, cy + 6)]
    for (a, b) in zip(pts, pts[1:]):
        d.line((a, b), fill=P["gold"])
    for x, y in pts:
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=P["red"])
        d.point((x, y - 2), fill=P["gold"])


@lru_cache(maxsize=8)
def royal_george(dmg):
    """HMS Royal George at damage level `dmg`, drawn bow-right then mirrored so it sits east, bow west.
    Returns (RGBA layer, rail heights by world x)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, x1, wl = 10, 150, WL
    if dmg < 3:
        main_top = 6 if dmg < 2 else 60
        for x, top in ((40, 16), (80, main_top), (118, 12)):
            if x == 80 and dmg >= 2:
                stump(d, 80, 60, 106)
            else:
                mast(d, x, top, 106)
        if dmg < 2:
            d.line((80, 8, 118, 64), fill=P["rope"])
            d.line((40, 18, 80, 54), fill=P["rope"])
        d.line((118, 14, 166, 90), fill=P["rope"])
        for x, top in ((40, 18), (80, 8), (118, 14)):
            if x == 80 and dmg >= 2:
                continue
            d.line((x, top, x - 22, 104), fill=P["rope"])
        if dmg < 2:
            shrouds(d, 80, 28, 104)
        shrouds(d, 118, 34, 102)
        shrouds(d, 40, 38, 100)
        if dmg < 2:
            sail(d, 80, 36, 56, 30, 36, belly=3, holes=((72, 50, 2),) if dmg >= 1 else ())
            hanover_tree(d, 84, 46)
            sail(d, 80, 18, 32, 20, 26, belly=2)
        furled(d, 80, 60, 42)
        furled(d, 118, 62, 36)
        sail(d, 118, 40, 58, 26, 32, belly=3, torn=dmg >= 1)
        sail(d, 40, 42, 58, 22, 26, belly=2, holes=((36, 50, 2), (44, 54, 1)) if dmg >= 1 else ())
        d.polygon([(40, 64), (40, 100), (18, 100), (24, 66)], fill=P["sail"])
        d.polygon([(40, 64), (40, 100), (35, 100), (36, 65)], fill=P["sail_lit"])
        d.line((40, 64, 40, 100), fill=P["sail_hi"])
        d.line((18, 100, 24, 66), fill=P["sail_sh"])
        yards = [(80, 60, 42), (118, 62, 36), (118, 40, 30), (40, 42, 24)]
        if dmg < 2:
            yards += [(80, 36, 34), (80, 18, 24)]
        for cx, y, w in yards:
            yard(d, cx, y, w)
        furled(d, 80, 60, 42)
        furled(d, 118, 62, 36)
        d.line((24, 66, 40, 62), fill=P["mast_sh"])
        if dmg >= 1:                                          # the fore t'gallant yard, shot away
            d.line((106, 24, 128, 34), fill=P["mast_sh"])
            d.polygon([(108, 25), (126, 33), (122, 40), (116, 36), (112, 41), (109, 32)], fill=P["sail_sh"])
        if dmg >= 2:                                          # rigging hanging off the stump
            d.line((80, 62, 92, 80), fill=P["rope"]); d.line((80, 62, 70, 84), fill=P["rope"])
            rags(d, 62, 61, 36, 7)
    else:                                                     # dismasted
        stump(d, 40, 70, 106); stump(d, 80, 64, 106); stump(d, 118, 76, 104)
        d.line((80, 66, 100, 104), fill=P["rope"]); d.line((40, 72, 22, 104), fill=P["rope"])
        d.line((118, 78, 140, 100), fill=P["rope"]); d.line((80, 66, 58, 104), fill=P["rope"])
        rags(d, 70, 66, 20, 3); rags(d, 110, 78, 14, 4)
        d.line((88, 90, 126, 102), fill=P["mast_sh"])        # a fallen yard across the deck
        rags(d, 92, 92, 26, 5)
    for i in range(12):
        d.line((150 + i, 97 - i // 2, 150 + i, 95 - i // 2), fill=P["sail_sh"])
    if dmg < 3:
        d.line((142, 102, 168, 88), fill=P["mast"])
        d.line((142, 103, 166, 90), fill=P["mast_sh"])
    else:
        d.line((142, 102, 154, 96), fill=P["mast"])          # bowsprit snapped short
    rail = []
    for x in range(x0, x1 + 1):
        base = 100 if x < 34 else 104 if x < 58 else 106 if x < 112 else 104
        rail.append((x, base + sheer(x, x0, x1, 3)))
    d.polygon(rail + [(154, 110), (152, 124), (146, 138), (140, wl + 2), (18, wl + 2), (12, 128), (6, 98)],
              fill=P["ochre"])
    for ya, yb in ((111, 112), (121, 122), (131, 132), (139, 142)):
        for x in range(12, 152):
            s = sheer(x, x0, x1, 3)
            d.line((x, ya + s, x, yb + s), fill=P["wale"])
    d.polygon([(18, wl + 2), (140, wl + 2), (146, 138), (14, 136)], fill=P["ochre_sh"])
    for y, x_first, x_last in ((114, 30, 136), (124, 26, 140), (134, 28, 138)):
        for x in range(x_first, x_last + 1, 9):
            yy = y + sheer(x, x0, x1, 3)
            d.rectangle((x, yy, x + 3, yy + 3), fill=P["port"])
            d.rectangle((x, yy - 2, x + 3, yy - 2), fill=P["lid"])
            d.point((x + 1, yy + 2), fill=P["wale"])
    d.polygon([(6, 98), (22, 96), (24, 120), (10, 124)], fill=P["frieze"])
    for yy in (102, 110, 118):
        d.line((9, yy, 22, yy - 1), fill=P["gilt"])
        for xx in (12, 16, 20):
            lit = dmg < 3 or (xx + yy) % 3
            d.point((xx, yy + 3), fill=P["window"] if lit else P["port"])
            d.point((xx, yy + 4), fill=P["window"] if lit else P["port"])
    d.line((6, 98, 10, 124), fill=P["gilt"])
    broken = set()
    if dmg >= 1:
        broken |= set(range(128, 137))
    if dmg >= 3:
        broken |= set(range(58, 76)) | set(range(20, 30)) | set(range(96, 104))
    for x, y in rail:
        if x in broken:
            continue
        d.point((x, y), fill=P["wale"])
        d.point((x, y - 1), fill=P["mast"])
    for x in sorted(broken):
        if x % 3 == 0:
            y = rail[x - x0][1]
            d.line((x, y, x, y - 1 - (x * 7) % 4), fill=P["mast"])
    holes = []
    if dmg >= 1:
        holes.append([(62, 114), (66, 112), (70, 114), (71, 118), (67, 120), (63, 119)])
    if dmg >= 3:
        holes += [[(100, 124), (104, 122), (107, 125), (104, 129), (100, 128)],
                  [(36, 130), (40, 128), (43, 131), (40, 134), (36, 133)],
                  [(120, 116), (123, 114), (126, 117), (123, 120)],
                  [(80, 132), (84, 130), (88, 133), (85, 137), (81, 136)]]
    for hole in holes:
        d.polygon(hole, fill=P["port"])
        cx = sum(p[0] for p in hole) / len(hole)
        cy = sum(p[1] for p in hole) / len(hole)
        for px, py in hole[::2]:
            d.line((px, py, px + (px - cx) * 0.6, py + (py - cy) * 0.6), fill=P["ochre"])
    d.polygon([(152, 106), (158, 104), (157, 110), (152, 112)], fill=P["gilt"])
    d.point((157, 105), fill=P["wale"])
    layer = mirror(layer)
    rails = {W - 1 - x: y for x, y in rail}
    return layer, rails


@lru_cache(maxsize=4)
def alfred(dmg):
    """The Continental ship Alfred (a converted merchantman, one gun deck), bow to the right."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, x1, wl = 12, 146, WL
    for x, top in ((42, 26), (82, 18), (118, 24)):
        mast(d, x, top, 114)
    d.line((82, 20, 118, 70), fill=P["rope"])
    d.line((42, 28, 82, 62), fill=P["rope"])
    d.line((118, 26, 162, 100), fill=P["rope"])
    for x, top in ((42, 28), (82, 20), (118, 26)):
        d.line((x, top, x - 22, 114), fill=P["rope"])
    shrouds(d, 82, 40, 114)
    shrouds(d, 118, 46, 112)
    shrouds(d, 42, 48, 110)
    sail(d, 82, 48, 68, 28, 32, belly=3, holes=((88, 58, 2),) if dmg >= 1 else ())
    sail(d, 82, 30, 44, 18, 24, belly=2)
    sail(d, 118, 52, 70, 24, 28, belly=3)
    sail(d, 118, 36, 50, 16, 20, belly=2, holes=((114, 44, 1),) if dmg >= 1 else ())
    sail(d, 42, 54, 70, 20, 24, belly=2)
    d.polygon([(42, 74), (42, 108), (20, 108), (26, 76)], fill=P["sail"])
    d.polygon([(42, 74), (42, 108), (37, 108), (38, 75)], fill=P["sail_lit"])
    d.line((42, 74, 42, 108), fill=P["sail_hi"])
    d.line((20, 108, 26, 76), fill=P["sail_sh"])
    for cx, y, w in ((82, 70, 38), (82, 48, 32), (82, 30, 22), (118, 72, 32), (118, 52, 28),
                     (118, 36, 20), (42, 54, 24)):
        yard(d, cx, y, w)
    furled(d, 82, 70, 38)
    furled(d, 118, 72, 32)
    d.line((26, 76, 42, 72), fill=P["mast_sh"])
    for i in range(12):
        d.line((146 + i, 106 - i // 2, 146 + i, 104 - i // 2), fill=P["sail_sh"])
    d.line((138, 110, 162, 98), fill=P["mast"])
    d.line((138, 111, 160, 100), fill=P["mast_sh"])
    rail = []
    for x in range(x0, x1 + 1):
        base = 112 if x < 34 else 116 if x < 116 else 114
        rail.append((x, base + sheer(x, x0, x1, 3)))
    d.polygon(rail + [(150, 118), (148, 130), (142, 140), (136, wl + 2), (20, wl + 2), (14, 132), (8, 110)],
              fill=P["wale"])
    for x in range(14, 148):
        s = sheer(x, x0, x1, 3)
        d.line((x, 122 + s, x, 128 + s), fill=P["buff"])
        d.point((x, 129 + s), fill=P["buff_sh"])
    for x in range(28, 138, 9):
        s = sheer(x, x0, x1, 3)
        d.rectangle((x, 123 + s, x + 3, 126 + s), fill=P["port"])
        d.point((x + 1, 125 + s), fill=P["mast_sh"])
    d.polygon([(8, 110), (22, 108), (22, 126), (12, 128)], fill=P["wale"])
    for yy in (114, 120):
        for xx in (13, 17):
            d.point((xx, yy), fill=P["window"])
    for x, y in rail:
        d.point((x, y - 1), fill=P["mast"])
        d.point((x, y), fill=P["sail_lit"] if x > 100 else P["mast_sh"])
    d.line((150, 118, 148, 130), fill=P["sail_lit"])
    d.line((148, 130, 142, 140), fill=P["mast_sh"])
    return layer, {x: y for x, y in rail}


def ports(shooter):
    """World positions of the forward gunports a volley fires from."""
    if shooter == "al":
        return [(x + 2, 124 + sheer(x, 12, 146, 3)) for x in range(64, 138, 9)]
    out = []
    for y, xs in ((114, range(84, 137, 9)), (124, range(80, 141, 9)), (134, range(82, 139, 9))):
        for x in xs:
            out.append((W - 1 - x - 2, y + 1 + sheer(x, 10, 150, 3)))
    return out


def bob(ship, t):
    return int(round(math.sin(t * (1.5 if ship == "al" else 1.25) + (0 if ship == "al" else 1.3)) * 1.0))


def deck(who, c):
    """Where a George stands on his ship at time c.t (the ships bob)."""
    s = state(c)
    if who == "washington":
        return W_FEET[0] + s["alfred_x"], W_FEET[1] + bob("al", c.t)
    return G_FEET[0], G_FEET[1] + bob("rg", c.t) + int(s["sink"])


def place(c):
    """Put both Georges on their decks and hide the crier (call from a gag's setup)."""
    for who in ("washington", "george"):
        x, y = deck(who, c)
        c.st[who].update(x=x, y=y, shadow=False, rim=0.5)
    c.st["crier"]["hidden"] = True


# --- smoke, shot and fire ----------------------------------------------------------------------

def _blob_mask(blobs, off=(0, 0), grow_by=0):
    def draw(m):
        for x, y, r in blobs:
            m.ellipse((x - r - grow_by + off[0], y - r - grow_by + off[1], x + r + grow_by + off[0],
                       y + r + grow_by + off[1]), fill=255)
    return pixel.mask(draw, (W, H)) > 0


def soft_mask(puffs):
    """A density mask from (density, x, y, r) circles; sorted by density so the densest wins overlaps."""
    return pixel.mask(lambda d: [d.ellipse((x - r, y - r, x + r, y + r), fill=int(255 * clamp(k, 0, 1)))
                                 for k, x, y, r in puffs], (W, H))


def smoke_blobs(t):
    """Smoke from every volley in the last few seconds: (x, y, r, age). Each volley leaves one long bank
    of overlapping lobes along the guns that fired, rolling out toward the gap and rising."""
    out = []
    for tv, who, n, _hit in VOLLEYS:
        age = t - tv
        if not 0 <= age < 3.2:
            continue
        pts = ports(who)
        if who == "rg":
            pts = [p for p in pts if abs(p[1] - 125) < 5]           # the middle gun deck
        pts = sorted(pts, reverse=who == "al")[:max(2, n)]     # the guns nearest the gap
        lo, hi = min(p[0] for p in pts), max(p[0] for p in pts)
        y0 = sum(p[1] for p in pts) / len(pts)
        drift = 1 if who == "al" else -1
        grow = min(1.0, age / 0.3)
        for k, x in enumerate(range(int(lo), int(hi) + 1, 5)):
            r = (1.5 + 3.0 * grow + age * 1.1) * (0.75 + 0.5 * rnd("sr", tv, k))
            xx = x + drift * (3 + age * (5 + 5 * rnd("sx", tv, k)))
            yy = y0 - 1 + (rnd("sj", tv, k) - 0.5) * 3 - age * (2.5 + 2 * rnd("sy", tv, k))
            out.append((xx, yy, r, age))
    return out


def draw_smoke(img, t, extra=()):
    blobs = smoke_blobs(t) + list(extra)
    if not blobs:
        return
    solid = [(x, y, r) for x, y, r, a in blobs if a < 1.1]
    thin = [(x, y, r, a) for x, y, r, a in blobs if a >= 1.1]
    if thin:
        puffs = sorted(((0.6 * (1 - (a - 1.1) / 2.1), x, y, r) for x, y, r, a in thin))
        pixel.dither(img, soft_mask(puffs), P["smoke"], blend=0.75, phase=1)
    if solid:
        a = np.array(img)
        body = _blob_mask(solid)
        rim = body & ~_blob_mask(solid, (1, 2))
        shade = body & ~_blob_mask(solid, (-2, -3))
        a[body] = P["smoke"]
        a[shade] = P["smoke_sh"]
        a[rim] = P["smoke_hi"]
        img.paste(Image.fromarray(a))


def draw_shot(img, t):
    """Round shot in flight and what it hits: splinters on a hull, a splash if it misses."""
    d = ImageDraw.Draw(img)
    for tv, who, n, hit in VOLLEYS:
        age = t - tv
        if not 0 <= age < 1.2:
            continue
        pts = ports(who)
        step = max(1, len(pts) // n)
        for i, (px, py) in enumerate(pts[::step][:n]):
            if age < 0.1:                                     # muzzle flash
                dx = 1 if who == "al" else -1
                d.polygon([(px, py - 1), (px + dx * 6, py), (px, py + 2)], fill=P["fire_hi"])
            if who == "al":
                tx, ty = 186 + rnd("tx", tv, i) * 90, 104 + rnd("ty", tv, i) * 30
            else:
                tx, ty = 40 + rnd("tx", tv, i) * 90, 112 + rnd("ty", tv, i) * 24
                if not hit:
                    tx, ty = 150 + rnd("tx", tv, i) * 30, WL + 2 + rnd("ty", tv, i) * 6
            dur = 0.3 + 0.1 * rnd("td", tv, i)
            p = (age - 0.04) / dur
            if 0 <= p <= 1:
                x = lerp(px, tx, p)
                y = lerp(py, ty, p) - 10 * 4 * p * (1 - p)
                d.rectangle((x - 1, y - 1, x, y), fill=INK)
            elif p > 1:
                a2 = age - 0.04 - dur
                if hit and a2 < 0.35:
                    for k in range(5):
                        ang = rnd("sp", tv, i, k) * math.pi * 2
                        v = 20 + 30 * rnd("sv", tv, i, k)
                        sx = tx + math.cos(ang) * v * a2
                        sy = ty + math.sin(ang) * v * a2 - 20 * a2 + 90 * a2 * a2
                        d.point((sx, sy), fill=P["mast"] if k % 2 else P["ochre"])
                    if a2 < 0.08:
                        d.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=P["fire_hi"])
                elif not hit and a2 < 0.5:
                    h = int(8 * (1 - a2 / 0.5))
                    d.line((tx, ty, tx, ty - h), fill=P["foam"])
                    d.point((tx - 2, ty - h // 2), fill=P["foam"]); d.point((tx + 2, ty - h // 2), fill=P["foam"])


def fires(img, t, amount=1.0):
    """Small fires burning on the wreck, with smoke rising off them."""
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate(((222, 101), (256, 102), (286, 97), (240, 104))):
        if i / 4 >= amount:
            continue
        for k in range(6):
            ph = (t * 3 + k / 6 + i * 0.3) % 1.0
            fx = x + (rnd("fx", i, k) - 0.5) * 6 + math.sin(t * 9 + k) * 1
            fy = y - ph * 8
            col = P["fire_hi"] if ph < 0.3 else P["fire"] if ph < 0.7 else P["red"]
            d.point((fx, fy), fill=col)
            if ph < 0.5:
                d.point((fx + 1, fy), fill=col)
    puffs = []
    for i, (x, y) in enumerate(((222, 101), (256, 102), (286, 97), (240, 104))):
        if i / 4 >= amount:
            continue
        for k in range(5):                                   # thin smoke drifting up and east
            ph = (t * 0.35 + k / 5 + i * 0.21) % 1.0
            puffs.append((0.7 - 0.55 * ph, x + ph * 16 + math.sin(t + k) * 2, y - 8 - ph * 36, 1.5 + ph * 3))
    pixel.dither(img, soft_mask(sorted(puffs)), P["smoke_sh"], blend=0.7, phase=2)


# --- the scene ---------------------------------------------------------------------------------------

def nightfall(img, amount, t, stars=0.0):
    """Dusk into night: shift toward deep blue (flat, not dithered, so it stays clean zoomed in), then stars."""
    if amount > 0:
        k = 0.55 * min(1.0, amount)
        a = np.asarray(img, dtype=np.float32)
        a = a * (1 - k) + np.array(P["night"][:3], np.float32) * k
        img.paste(Image.fromarray(a.round().astype(np.uint8)))
    if stars > 0:
        d = ImageDraw.Draw(img)
        for i in range(60):
            if rnd("st", i) > stars:
                continue
            x, y = int(rnd("sx", i) * W), int(rnd("sy", i) * 80)
            tw = rnd("tw", i, int(t * 3)) < 0.85
            d.point((x, y), fill=(250, 246, 220) if tw else (170, 160, 200))


def paste_ship(img, layer, dx, dy, sink=0):
    """Paste a ship layer shifted by (dx, dy); `sink` rows at the waterline go under."""
    if sink > 0:
        layer = layer.crop((0, 0, W, WL + 3 - sink))
    img.paste(layer, (int(dx), int(dy) + int(sink)), layer)


def foam(img, t, rg_sink=0):
    d = ImageDraw.Draw(img)
    for x0, x1, y in ((20, 146, WL + 1), (174, 308, WL + 1)):
        for x in range(x0, x1):
            if rnd("fm", x, int(t * 4)) < 0.6:
                d.point((x, y + (x % 3 == 0)), fill=P["foam"])
    for x0, x1 in ((22, 142), (178, 300)):
        for y in range(WL + 3, WL + 10, 2):
            for x in range(x0, x1, 5):
                if rnd("rf", x, y) < 0.6:
                    d.line((x, y, x + 2, y), fill=P["sea3"])


def world(c):
    s = state(c)
    t = c.t
    img = Image.fromarray(backdrop())
    sea(img, t, s["dark"])
    al, _ = alfred(s["al"])
    rg, _ = royal_george(s["rg"])
    ad, rd = bob("al", t), bob("rg", t)
    paste_ship(img, al, s["alfred_x"], ad)
    flagpole_on(img, "grand_union", 17 + s["alfred_x"], 14 + ad, t, flip=True)
    pen = ImageDraw.Draw(img)
    for i in range(26):
        pen.point((81 + s["alfred_x"] - i, 16 + ad + int(round(1.2 * math.sin(i / 3.0 + t * 5)))), fill=P["white"])
    paste_ship(img, rg, 0, rd, int(s["sink"]))
    if s["rg"] < 3:
        flagpole_on(img, "red_ensign", 280, 4 + rd + int(s["sink"]), t)
        if s["rg"] < 2:
            for i in range(30):
                pen.point((240 + i, 4 + rd + int(round(1.2 * math.sin(i / 3.0 + t * 5)))), fill=P["red"])
    else:                                                   # the ensign on a stump of the mizzen, tattered
        flagpole_on(img, "red_ensign", 280, 72 + rd + int(s["sink"]), t, amp=0.8)
    foam(img, t)
    if s["fires"]:
        fires(img, t, 1.0)
    if s["volleys"]:
        draw_shot(img, t)
        draw_smoke(img, t)
    nightfall(img, s["dark"], t, s["stars"])
    return img


def flagpole_on(img, kind, x, y, t, flip=False, amp=1.4):
    fl = waving(flag_cloth(kind), t, 0.7 if flip else 0.0, amp, flip)
    if flip:
        img.paste(fl, (int(x), int(y)), fl)
    else:
        img.paste(fl, (int(x), int(y)), fl)


@lru_cache(maxsize=16)
def bulwark(ship, dmg):
    """Just the bulwark rows of a ship around where its George stands, to draw over his boots."""
    layer, rails = (alfred(dmg) if ship == "al" else royal_george(dmg))
    a = np.array(layer)
    keep = np.zeros(a.shape[:2], bool)
    xs = range(W_FEET[0] - 16, W_FEET[0] + 17) if ship == "al" else range(G_FEET[0] - 16, G_FEET[0] + 17)
    for x in xs:
        if x in rails:
            y = rails[x]
            keep[y - 1:y + 5, x] = True
    a[~keep] = 0
    return Image.fromarray(a)


def front(c):
    """Draw each ship's bulwark over its George's feet."""
    s = state(c)
    t = c.t
    img = c.world
    if not getattr(c, "no_bulwark", False):
        b = bulwark("al", s["al"])
        img.paste(b, (int(s["alfred_x"]), bob("al", t)), b)
        b = bulwark("rg", s["rg"])
        sink = int(s["sink"])
        if sink:
            b = b.crop((0, 0, W, WL + 3 - sink))
        img.paste(b, (0, bob("rg", t) + sink), b)


V.SCENES["ships"] = (world, front)


# --- small ships for the shores set ----------------------------------------------------------------

@lru_cache(maxsize=None)
def small_ship(kind):
    """A small three-master (64x52), bow to the right: 'alfred' (black and buff) or 'royal' (ochre)."""
    s = Canvas(66, 54)
    hull = "wale" if kind == "alfred" else "ochre"
    hull_c = P[hull]
    for x, top in ((16, 6), (32, 2), (47, 5)):
        s.line([(x, top), (x, 38)], P["mast"])
    for x, top, w in ((16, 8, 10), (32, 4, 12), (47, 7, 10)):
        for k, (a, b) in enumerate(((top + 2, top + 12), (top + 14, top + 26))):
            ww = w + k * 3
            s.poly([(x - ww // 2, a), (x + ww // 2, a), (x + ww // 2 + 1, b), (x - ww // 2 - 1, b)], P["sail"])
            s.line([(x + ww // 2, a + 1), (x + ww // 2 + 1, b)], P["sail_hi"])
            s.line([(x - ww // 2 - 1, a), (x + ww // 2 + 1, a)], P["mast_sh"])
    s.line([(54, 34), (64, 28)], P["mast"])
    s.poly([(2, 34), (58, 36), (62, 38), (56, 46), (8, 46), (3, 40)], hull_c)
    if kind == "alfred":
        s.line([(4, 39), (58, 40)], P["buff"])
        for x in range(10, 54, 6):
            s.px((x, 40), P["port"])
    else:
        for y in (39, 43):
            s.line([(4, y), (58, y + 1)], P["wale"])
        for x in range(9, 55, 5):
            s.px((x, 41), P["port"]); s.px((x, 45), P["port"])
        s.poly([(2, 30), (10, 30), (10, 38), (3, 38)], P["frieze"])
        s.line([(2, 30), (10, 30)], P["gilt"])
    s.line([(2, 34), (58, 36)], P["mast"])
    img = s.done()
    fl = flag_cloth("grand_union" if kind == "alfred" else "red_ensign")
    fl = fl.resize((fl.width // 2, (fl.height + 1) // 2), Image.NEAREST)
    img.paste(fl, (32 - fl.width - 1 if kind == "alfred" else 33, 0))
    return img


def small_deck(kind):
    """(dx, dy) from a small ship's top-left to where a George stands on it."""
    return (40, 36) if kind == "alfred" else (22, 34)
