"""The places the video goes. Each set is `back(c) -> world image` plus an optional
`front(c)` that draws over the characters (glass, foreground leaves).

Static layers are built once and cached; each frame copies them and adds
what moves (mist, light shafts, the ON AIR lamp).
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import (SILK, H, W, blend, blend_poly, col, dither, dither_poly,
                    dither_rect, mask, rnd, vgrad)
from pixelart import pixel

SETS = {}


class Set:
    """A place. `back(c)` returns the world image. The cast is drawn in two layers: z=0 (in the set)
    then `mid(c)` (glass, mist), then z=1 (the foreground) and `near(c)` (leaves right by the lens).
    `shots` are named framings (cx, cy, k), `cycle` the shots a verse line rotates through when no
    gag picks one, and `cast` how anyone who appears is placed and dressed (absent: hidden)."""

    def __init__(self, back, mid=None, near=None, shots=None, cast=None, cycle=()):
        self.back, self.mid, self.near = back, mid, near
        self.shots = {"wide": (160, 90, 6), **(shots or {})}
        self.cast = cast or {}
        self.cycle = tuple(cycle)


def scene(name, **kw):
    """Register `fn(c) -> world` as a set (usable as a decorator)."""
    def reg(fn):
        SETS[name] = Set(fn, **kw)
        return fn
    return reg


def leaf_blob(d, cx, cy, r, color, seed, n=7, squash=0.8):
    """A clump of leaves: overlapping ellipses around a centre."""
    for k in range(n):
        a = rnd(seed, k) * 2 * math.pi
        rr = r * (0.3 + 0.5 * rnd(seed, k, "r"))
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * squash
        s = r * (0.45 + 0.35 * rnd(seed, k, "s"))
        d.ellipse((x - s, y - s * squash, x + s, y + s * squash), fill=col(color))


def frond(d, x, y, length, angle, color, width=5, leaflets=True):
    """A fern frond or palm leaf: a curved spine with leaflets either side."""
    pts = []
    for k in range(12):
        p = k / 11
        a = angle + 0.6 * p * (1 if angle < math.pi / 2 else -1)
        pts.append((x + math.cos(a) * length * p, y - math.sin(a) * length * p + 10 * p * p))
    for k in range(1, len(pts)):
        x0, y0 = pts[k - 1]
        x1, y1 = pts[k]
        w = width * (1 - k / len(pts)) + 1
        if leaflets:
            nx, ny = -(y1 - y0), (x1 - x0)
            nn = math.hypot(nx, ny) or 1
            nx, ny = nx / nn * w, ny / nn * w
            d.polygon([(x0, y0), (x1 + nx, y1 + ny + 2), (x1, y1)], fill=col(color))
            d.polygon([(x0, y0), (x1 - nx, y1 - ny + 2), (x1, y1)], fill=col(color))
        d.line([(x0, y0), (x1, y1)], fill=col(color), width=1)


# --- the habitat: a jungle clearing with a vocal booth in it -------------------------------

BOOTH = (178, 58, 238, 146)          # outer box of the booth: x0, y0, x1, y1 (floor at y1)
BOOTH_FLOOR = BOOTH[3] - 3
BOOTH_CX = (BOOTH[0] + BOOTH[2]) // 2
HAB_GROUND = 140
MORGAN_BOOTH = (198, BOOTH_FLOOR)     # Morgan's feet in the booth, facing the mic
MIC = (221, BOOTH_FLOOR - 31)         # the hanging mic's capsule, level with his mouth
DAVID_PRESENT = (112, 166)            # Sir David presenting in the foreground

JUNGLE = {
    "far": (120, 168, 150), "far2": (98, 150, 134), "mid": (58, 112, 82), "mid2": (44, 92, 70),
    "trunk": (78, 66, 60), "trunk_sh": (56, 46, 46), "near": (26, 60, 46), "near2": (18, 44, 36),
    "floor": (92, 118, 62), "floor_sh": (70, 92, 52), "floor_hi": (140, 162, 84), "path": (120, 96, 66),
    "ray": (246, 248, 214), "gap": (226, 240, 222), "vine": (64, 110, 60),
    "steel": (104, 110, 124), "steel_sh": (70, 74, 88), "steel_hi": (160, 168, 184),
    "foam": (58, 58, 70), "foam_sh": (42, 42, 52), "lamp": (255, 246, 206), "onair": (230, 40, 40),
    "onair_off": (96, 40, 44),
}


@lru_cache(maxsize=1)
def habitat_static():
    img = Image.new("RGB", (W, H), JUNGLE["far"])
    vgrad(img, (0, 0, W, 110), JUNGLE["gap"], JUNGLE["far"], steps=6)
    d = ImageDraw.Draw(img)
    # far layer: pale trunks and canopy in the haze
    for k in range(9):
        x = int(10 + k * 37 + rnd("ft", k) * 14)
        d.rectangle((x, 30, x + 4, 130), fill=JUNGLE["far2"])
        leaf_blob(d, x + 2, 26 + rnd("fty", k) * 14, 26, JUNGLE["far2"], ("far", k), n=6)
    # the canopy overhead, darker at the edges, with a gap of sky in the middle
    for k in range(16):
        x = k * 22 + rnd("cx", k) * 10
        edge = abs(x - 160) / 160
        y = -14 + 30 * edge + rnd("cy", k) * 8
        leaf_blob(d, x, y, 24 + 10 * edge, JUNGLE["mid2"] if edge > 0.4 else JUNGLE["mid"], ("can", k), n=8)
    # mid layer: big trunks left and right with vines
    for (x, w_) in ((22, 12), (96, 8), (262, 14), (300, 9)):
        d.rectangle((x, 0, x + w_, HAB_GROUND + 2), fill=JUNGLE["trunk"])
        d.rectangle((x, 0, x + 2, HAB_GROUND + 2), fill=JUNGLE["trunk_sh"])
        d.polygon([(x - 6, HAB_GROUND + 3), (x, HAB_GROUND - 12), (x + w_, HAB_GROUND - 12),
                   (x + w_ + 7, HAB_GROUND + 3)], fill=JUNGLE["trunk"])
        for v in range(2):
            vx = x + 3 + v * 5
            pts = [(vx + math.sin(yy / 9 + v + x) * 3, yy) for yy in range(0, 90, 6)]
            d.line(pts, fill=JUNGLE["vine"], width=1)
    for k in range(10):
        x = k * 34 + rnd("mx", k) * 12
        leaf_blob(d, x, 44 + rnd("my", k) * 30 * (abs(x - 160) / 160), 18, JUNGLE["mid"], ("mid", k), n=6)
    # the clearing floor
    d.rectangle((0, HAB_GROUND, W, H), fill=JUNGLE["floor"])
    dither_rect(img, (0, HAB_GROUND, W, HAB_GROUND + 6), JUNGLE["floor_sh"], density=0.5)
    d.polygon([(118, H), (150, HAB_GROUND + 4), (230, HAB_GROUND + 4), (262, H)], fill=JUNGLE["path"])
    dither_poly(img, [(118, H), (150, HAB_GROUND + 4), (230, HAB_GROUND + 4), (262, H)], JUNGLE["floor"],
                density=0.3, blend=1.0)
    for k in range(60):
        x, y = rnd("tuft", k) * W, HAB_GROUND + 4 + rnd("tuft-y", k) * (H - HAB_GROUND - 6)
        d.line([(x, y), (x + 1, y - 3)], fill=JUNGLE["floor_hi"])
        d.line([(x + 2, y), (x + 2, y - 2)], fill=JUNGLE["floor_sh"])
    # the booth
    booth(img)
    # ferns round the booth's feet and along the back of the clearing
    for k, x in enumerate((168, 184, 236, 250, 44, 72, 120)):
        for j in range(4):
            frond(d, x, HAB_GROUND + 4, 12 + rnd("fern", k, j) * 8, 0.5 + j * 0.7 + rnd("fa", k, j) * 0.3,
                  JUNGLE["mid"] if j % 2 else JUNGLE["mid2"], width=3)
    return img


def booth(img):
    """A studio vocal booth, left in the jungle: steel frame, foam inside, a mic under a hard light."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = BOOTH
    d.rectangle((x0 - 2, y0 - 12, x1 + 2, y0), fill=JUNGLE["steel_sh"])           # roof box
    d.rectangle((x0, y0 - 11, x1, y0 - 2), fill=JUNGLE["steel"])
    d.line([(x0, y0 - 11), (x1, y0 - 11)], fill=JUNGLE["steel_hi"])
    d.rectangle((x0, y0, x1, y1), fill=JUNGLE["steel"])
    d.rectangle((x0 + 4, y0 + 4, x1 - 4, y1 - 4), fill=JUNGLE["foam"])
    for yy in range(y0 + 5, y1 - 4, 4):                                           # foam wedges
        for xx in range(x0 + 5 + (yy // 4) % 2 * 2, x1 - 4, 4):
            d.point((xx, yy), fill=JUNGLE["foam_sh"])
            d.point((xx + 1, yy + 1), fill=JUNGLE["foam_sh"])
    d.rectangle((x0 + 4, y1 - 7, x1 - 4, y1 - 4), fill=(80, 70, 66))               # a bit of carpet
    d.line([(x0, y0), (x0, y1)], fill=JUNGLE["steel_hi"])
    d.line([(x1, y0), (x1, y1)], fill=JUNGLE["steel_sh"])
    d.line([(x0, y1), (x1, y1)], fill=JUNGLE["steel_sh"])
    d.rectangle((x0 + 18, y0 - 9, x1 - 18, y0 - 4), fill=JUNGLE["onair_off"])        # ON AIR sign (off)
    # vines have grown over it
    for v in range(3):
        vx = x0 + 6 + v * 21
        pts = [(vx + math.sin(yy / 7 + v) * 2, y0 - 12 + yy) for yy in range(0, 26 + v * 9, 3)]
        d.line(pts, fill=JUNGLE["vine"])
        for p in pts[2::3]:
            d.ellipse((p[0] - 2, p[1] - 1, p[0] + 1, p[1] + 1), fill=JUNGLE["mid"])
    # the hanging mic, with pop filter, at the singer's mouth height
    cx, my = MIC
    d.line([(cx, y0 + 4), (cx, my - 4)], fill=(30, 30, 36))
    d.rectangle((cx - 2, my - 4, cx + 2, my + 4), fill=(40, 40, 48))
    d.rectangle((cx - 1, my - 3, cx + 1, my + 3), fill=(110, 110, 124))
    d.line([(cx - 3, my), (cx - 7, my)], fill=(30, 30, 36))
    d.ellipse((cx - 11, my - 5, cx - 7, my + 5), outline=(30, 30, 36))
    dither(img, mask(lambda m: m.ellipse((cx - 10, my - 4, cx - 8, my + 4), fill=255)) * 0.5, (30, 30, 36))


def light_cone(img, t, strength=1.0):
    """The harsh light of the vocal booth: a cone down from the booth's ceiling lamp."""
    x0, y0, x1, y1 = BOOTH
    cx = BOOTH_CX
    flick = 0.92 + 0.08 * math.sin(t * 13) * math.sin(t * 7.3)
    blend_poly(img, [(cx - 5, y0 + 6), (cx + 5, y0 + 6), (x1 - 5, y1 - 5), (x0 + 5, y1 - 5)], JUNGLE["lamp"],
               0.22 * strength * flick)
    blend_poly(img, [(cx - 3, y0 + 6), (cx + 3, y0 + 6), (cx + 14, y1 - 5), (cx - 14, y1 - 5)], JUNGLE["lamp"],
               0.12 * strength * flick)
    d = ImageDraw.Draw(img)
    d.rectangle((cx - 6, y0 + 4, cx + 6, y0 + 5), fill=(40, 40, 48))
    d.rectangle((cx - 5, y0 + 6, cx + 5, y0 + 6), fill=JUNGLE["lamp"])


def god_rays(img, t, strength=1.0):
    """Shafts of light slanting down from the gap in the canopy, breathing slowly."""
    for k, (x, w) in enumerate(((120, 16), (150, 10), (176, 20), (206, 8))):
        breathe = 0.5 + 0.5 * math.sin(t * 0.7 + k * 1.7)
        pts = [(x, 0), (x + w, 0), (x + w + 60, HAB_GROUND + 10), (x + 40, HAB_GROUND + 10)]
        blend_poly(img, pts, JUNGLE["ray"], (0.10 + 0.06 * breathe) * strength)


def mist(img, t, y=118, strength=1.0):
    """A low band of mist drifting through the clearing, in flat steps."""
    xs = np.arange(W)
    band = np.zeros((H, W), np.float32)
    for k in range(3):
        yy = y + k * 7
        wob = np.sin(xs / (23 + 7 * k) + t * (0.3 + 0.1 * k) + k) * 3
        for dy in range(-5, 6):
            rows = np.clip((yy + wob + dy).astype(int), 0, H - 1)
            band[rows, xs] = np.maximum(band[rows, xs], 1 - abs(dy) / 6)
    band = np.floor(band * 3) / 3
    blend(img, band, (236, 244, 236), 0.16 * strength)


STUMP = (152, 151)            # the tree stump in the middle of the clearing, where the prize sits


def stump(img, x=STUMP[0], y=STUMP[1]):
    d = ImageDraw.Draw(img)
    d.polygon([(x - 10, y), (x - 7, y - 9), (x + 7, y - 9), (x + 10, y)], fill=JUNGLE["trunk"])
    d.ellipse((x - 7, y - 11, x + 7, y - 7), fill=(170, 130, 90))
    d.ellipse((x - 4, y - 10, x + 4, y - 8), outline=(130, 96, 70))
    d.line([(x - 6, y - 6), (x - 6, y - 1)], fill=JUNGLE["trunk_sh"])
    for k in range(5):                                          # moss
        d.point((x - 8 + k * 4, y - 1 - k % 2), fill=JUNGLE["mid"])
        d.point((x - 7 + k * 4, y - 1), fill=JUNGLE["vine"])


def prize(img, t, x=STUMP[0], y=STUMP[1] - 9, glint=True):
    """The planet trophy on its stump, turning slowly, catching the light now and then."""
    from props import sparkle, trophy
    tr = trophy(int(t * 3) % 16)
    img.paste(tr, (x - tr.width // 2, y - tr.height + 2), tr)
    if glint and (t % 2.6) < 0.25:
        sparkle(img, x - 5, y - tr.height + 6, 2, (255, 255, 255))


def habitat(c):
    img = habitat_static().copy()
    god_rays(img, c.t)
    light_cone(img, c.t, strength=c.get("booth_light", 1.0))
    if c.get("prize", True):
        stump(img)
        prize(img, c.t)
    if c.get("on_air"):
        x0, y0, x1, _ = BOOTH
        d = ImageDraw.Draw(img)
        d.rectangle((x0 + 18, y0 - 9, x1 - 18, y0 - 4), fill=JUNGLE["onair"])
        pixel.text(img, ((x0 + x1) // 2, y0 - 10), "ON AIR", SILK, (255, 236, 236), shadow=None, anchor="ma")
    return img


def habitat_front(c):
    img = c.world
    x0, y0, x1, y1 = BOOTH
    # the booth's glass: a faint tint and two diagonal glints
    blend_poly(img, [(x0 + 4, y0 + 4), (x1 - 4, y0 + 4), (x1 - 4, y1 - 4), (x0 + 4, y1 - 4)], (200, 230, 240), 0.08)
    for gx, gw in ((x0 + 30, 5), (x0 + 38, 2)):
        blend_poly(img, [(gx, y0 + 4), (gx + gw, y0 + 4), (gx + gw - 22, y0 + 44), (gx - 22, y0 + 44)],
                   (250, 252, 255), 0.22)
    d = ImageDraw.Draw(img)
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), outline=JUNGLE["steel_sh"])
    d.line([(BOOTH_CX, y0 + 3), (BOOTH_CX, y1 - 3)], fill=JUNGLE["steel_sh"])      # the glass door's seam
    d.rectangle((BOOTH_CX + 3, y0 + 44, BOOTH_CX + 4, y0 + 52), fill=JUNGLE["steel_hi"])   # handle
    mist(img, c.t, strength=c.get("mist", 1.0))


def habitat_near(c):
    if c.get("foreground", True):
        foreground_ferns(c.world, c.t)


def foreground_ferns(img, t):
    """Dark fronds framing the bottom corners, swaying a little: the camera is hiding in the bushes."""
    d = ImageDraw.Draw(img)
    sway = math.sin(t * 1.3) * 0.05
    for k, (x, y, L, a) in enumerate(((-6, 184, 70, 0.55), (4, 186, 60, 0.95), (-10, 150, 50, 0.2),
                                      (326, 184, 70, math.pi - 0.55), (318, 186, 56, math.pi - 0.9),
                                      (330, 146, 46, math.pi - 0.2))):
        frond(d, x, y, L, a + sway * (1 if k < 3 else -1), JUNGLE["near"] if k % 2 else JUNGLE["near2"], width=7)


scene("habitat", mid=habitat_front, near=habitat_near,
      shots={"present": (152, 122, 12), "booth": (208, 102, 12), "tele": (205, 110, 18), "face": (206, 104, 24),
             "clearing": (150, 110, 9)},
      cast={"morgan": dict(x=MORGAN_BOOTH[0], y=MORGAN_BOOTH[1], facing=1, hat="headphones"),
            "david": dict(x=DAVID_PRESENT[0], y=DAVID_PRESENT[1], facing=1, mic="fluffy", z=1)},
      cycle=("present", "booth", "present", "wide"))(habitat)


@scene("black")
def black(c):
    return Image.new("RGB", (W, H), (0, 0, 0))


# --- the yard: THE BBC REDEMPTION -------------------------------------------------------------

YARD = {
    "sky": (250, 188, 118), "sky2": (255, 226, 168), "sun": (255, 244, 206),
    "wall": (150, 138, 126), "wall_sh": (118, 106, 100), "wall_hi": (182, 170, 152), "mortar": (126, 114, 106),
    "block": (128, 120, 114), "block_sh": (98, 92, 92), "block_hi": (162, 152, 140), "window": (40, 36, 42),
    "dirt": (190, 158, 112), "dirt_sh": (160, 128, 92), "dirt_hi": (216, 188, 140), "wire": (70, 64, 66),
    "tower": (136, 124, 114), "roof": (88, 76, 74), "lamp": (255, 250, 220),
}
YARD_GROUND = 120
RED_SPOT = (100, 150)       # Morgan as Red, narrating by the wall
ANDY_SPOT = (228, 136)      # Sir David, the new fish, alone across the yard


@lru_cache(maxsize=1)
def yard_static():
    img = Image.new("RGB", (W, H), YARD["sky"])
    vgrad(img, (0, 0, W, 60), YARD["sky"], YARD["sky2"], steps=5)
    d = ImageDraw.Draw(img)
    d.ellipse((34, 26, 58, 50), fill=YARD["sun"])                                   # low sun behind the tower
    # the cell block on the right
    d.rectangle((226, 22, W, YARD_GROUND), fill=YARD["block"])
    d.rectangle((226, 22, W, 27), fill=YARD["block_hi"])
    d.line([(226, 22), (226, YARD_GROUND)], fill=YARD["block_sh"])
    for row, y in enumerate(range(34, 104, 16)):
        for x in range(236, 316, 14):
            d.rectangle((x, y, x + 7, y + 9), fill=YARD["window"])
            for bx in (x + 2, x + 5):
                d.line([(bx, y), (bx, y + 9)], fill=YARD["block_sh"])
    # the long wall
    d.rectangle((0, 58, 232, YARD_GROUND), fill=YARD["wall"])
    for r, y in enumerate(range(62, YARD_GROUND, 7)):
        d.line([(0, y), (232, y)], fill=YARD["mortar"])
        for x in range(-12 + (r % 2) * 9, 232, 18):
            d.line([(x, y - 6), (x, y)], fill=YARD["mortar"])
    d.rectangle((0, 56, 232, 60), fill=YARD["wall_hi"])
    blend_poly(img, [(0, YARD_GROUND - 14), (232, YARD_GROUND - 14), (232, YARD_GROUND), (0, YARD_GROUND)],
               YARD["wall_sh"], 0.4)
    # barbed wire along the top
    for x in range(0, 232, 6):
        d.line([(x, 52), (x + 6, 52)], fill=YARD["wire"])
        d.line([(x + 2, 50), (x + 4, 54)], fill=YARD["wire"])
        d.line([(x + 4, 50), (x + 2, 54)], fill=YARD["wire"])
    for x in range(4, 232, 26):
        d.line([(x, 50), (x, 57)], fill=YARD["wire"])
    # the gate, with the name over it
    d.rectangle((128, 76, 176, YARD_GROUND), fill=(84, 78, 80))
    for x in range(131, 176, 5):
        d.line([(x, 78), (x, YARD_GROUND)], fill=(58, 54, 58))
    d.rectangle((110, 62, 194, 73), fill=(62, 56, 60))
    pixel.text(img, (152, 64), "B.B.C. PENITENTIARY", SILK, (230, 214, 180), shadow=None, anchor="ma")
    # the guard tower on the left
    d.rectangle((40, 22, 64, YARD_GROUND), fill=YARD["tower"])
    d.line([(40, 22), (40, YARD_GROUND)], fill=YARD["wall_hi"])
    d.rectangle((34, 10, 70, 24), fill=YARD["tower"])
    d.rectangle((36, 13, 68, 21), fill=YARD["window"])
    d.polygon([(30, 10), (52, 0), (74, 10)], fill=YARD["roof"])
    d.rectangle((46, 16, 50, 20), fill=YARD["lamp"])
    # the dusty yard
    d.rectangle((0, YARD_GROUND, W, H), fill=YARD["dirt"])
    d.rectangle((0, YARD_GROUND, W, YARD_GROUND + 2), fill=YARD["dirt_sh"])
    for k in range(80):
        x, y = rnd("dirt", k) * W, YARD_GROUND + 5 + rnd("dirt-y", k) * (H - YARD_GROUND - 5)
        d.point((x, y), fill=YARD["dirt_sh"] if k % 3 else YARD["dirt_hi"])
    # the long shadows of late afternoon
    blend_poly(img, [(40, YARD_GROUND), (64, YARD_GROUND), (150, 180), (110, 180)], (96, 70, 60), 0.3)
    # a bench and a weights rack, prison-yard furniture
    d.rectangle((252, 128, 290, 131), fill=(120, 90, 66))
    d.rectangle((255, 131, 257, 138), fill=(90, 66, 52)); d.rectangle((285, 131, 287, 138), fill=(90, 66, 52))
    d.line([(20, 136), (46, 136)], fill=(70, 70, 76))
    d.ellipse((16, 130, 23, 142), fill=(50, 50, 56)); d.ellipse((43, 130, 50, 142), fill=(50, 50, 56))
    return img


def yard_searchlight(img, t):
    """The tower's searchlight sweeps the yard now and then."""
    ang = math.sin(t * 0.5) * 0.7
    x, y = 48, 18
    L = 190
    a0, a1 = math.pi / 2 + ang - 0.09, math.pi / 2 + ang + 0.09
    pts = [(x, y), (x + math.cos(a0) * L * 1.6, y + math.sin(a0) * L), (x + math.cos(a1) * L * 1.6, y + math.sin(a1) * L)]
    blend_poly(img, pts, YARD["lamp"], 0.12)


def yard(c):
    img = yard_static().copy()
    yard_searchlight(img, c.t)
    return img


scene("yard",
      shots={"red": (118, 118, 12), "fish": (226, 112, 18), "gate": (152, 84, 12), "yard": (170, 112, 9)},
      cast={"morgan": dict(x=RED_SPOT[0], y=RED_SPOT[1], facing=1, outfit="prison", mic=True, z=1),
            "david": dict(x=ANDY_SPOT[0], y=ANDY_SPOT[1], facing=-1, outfit="prison")},
      cycle=("red", "fish", "red", "yard"))(yard)


# --- the car: DRIVING MR. DAVID ---------------------------------------------------------------

CAR = {
    "body": (46, 74, 64), "body_sh": (30, 50, 46), "body_hi": (84, 122, 102), "chrome": (214, 218, 226),
    "chrome_sh": (140, 146, 160), "glass": (150, 190, 206), "inside": (38, 34, 40), "seat": (120, 84, 62),
    "tyre": (26, 24, 28), "wall": (236, 234, 226), "hub": (190, 194, 204),
    "road": (84, 82, 88), "road_hi": (110, 108, 114), "line": (236, 214, 120), "verge": (104, 150, 76),
    "verge_sh": (80, 120, 64), "hill": (140, 176, 120), "hill2": (170, 196, 150), "sky": (150, 200, 236),
    "sky2": (214, 234, 246), "pole": (110, 84, 64), "tree": (58, 110, 70), "tree_hi": (86, 140, 84),
}
ROAD_Y = 150
WHEELS = (110, 206)
CAR_Y = 146                  # wheel centres
DRIVER = (163, 146)          # Morgan's seat (feet), the wheel in front of him
BACKSEAT = (127, 146)
CAR_SPEED = 60.0             # world pixels per second, for the scenery


def car_speed(c):
    return c.get("car_speed", CAR_SPEED)


def car_body(img, x=0, bob=0, lower=True, upper=True):
    """A post-war sedan in bottle green, side on, facing right. `upper` is the cabin (drawn behind the
    passengers), `lower` the doors and wings (drawn in front of them)."""
    d = ImageDraw.Draw(img)
    y = bob
    if upper:
        d.polygon([(x + 110, y + 120), (x + 118, y + 97), (x + 150, y + 92), (x + 176, y + 94), (x + 192, y + 120)],
                  fill=CAR["body"])
        d.polygon([(x + 116, y + 119), (x + 122, y + 100), (x + 146, y + 97), (x + 146, y + 119)], fill=CAR["inside"])
        d.polygon([(x + 150, y + 119), (x + 150, y + 97), (x + 173, y + 98), (x + 186, y + 119)], fill=CAR["inside"])
        d.line([(x + 118, y + 97), (x + 150, y + 92), (x + 176, y + 94)], fill=CAR["body_hi"])
    if lower:
        d.polygon([(x + 84, y + 146), (x + 86, y + 126), (x + 104, y + 118), (x + 196, y + 118), (x + 212, y + 116),
                   (x + 234, y + 122), (x + 240, y + 146)], fill=CAR["body"])
        d.line([(x + 88, y + 125), (x + 104, y + 119), (x + 196, y + 119), (x + 212, y + 117), (x + 233, y + 123)],
               fill=CAR["body_hi"])
        d.rectangle((x + 86, y + 133, x + 238, y + 134), fill=CAR["chrome_sh"])          # the side trim
        d.line([(x + 86, y + 133), (x + 238, y + 133)], fill=CAR["chrome"])
        d.line([(x + 148, y + 120), (x + 148, y + 144)], fill=CAR["body_sh"])            # door seams
        d.line([(x + 112, y + 120), (x + 112, y + 144)], fill=CAR["body_sh"])
        d.rectangle((x + 138, y + 126, x + 142, y + 127), fill=CAR["chrome"])            # handles
        d.rectangle((x + 176, y + 126, x + 180, y + 127), fill=CAR["chrome"])
        d.rectangle((x + 82, y + 140, x + 90, y + 145), fill=CAR["chrome"])              # bumpers
        d.rectangle((x + 236, y + 139, x + 244, y + 145), fill=CAR["chrome"])
        d.ellipse((x + 233, y + 124, x + 239, y + 130), fill=(255, 246, 210))            # headlamp
        d.rectangle((x + 84, y + 128, x + 86, y + 131), fill=(200, 40, 40))              # tail light
        for wx in WHEELS:
            d.ellipse((x + wx - 16, y + 128, x + wx + 16, y + 150), fill=CAR["body_sh"])  # wheel arches
    return img


def wheel(img, cx, cy, t, speed):
    d = ImageDraw.Draw(img)
    d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill=CAR["tyre"])
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=CAR["wall"])
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=CAR["hub"])
    a = -t * speed / 11
    for k in range(3):
        aa = a + k * 2 * math.pi / 3
        d.point((cx + round(math.cos(aa) * 3), cy + round(math.sin(aa) * 3)), fill=CAR["chrome_sh"])


def road_scenery(img, t, speed=CAR_SPEED):
    """Sky, hills, trees and telegraph poles going by, and the road under the car."""
    vgrad(img, (0, 0, W, 90), CAR["sky"], CAR["sky2"], steps=4)
    d = ImageDraw.Draw(img)
    off = t * speed
    for k in range(-1, 6):                                                      # far hills
        x = k * 90 - (off * 0.1) % 90
        d.ellipse((x - 20, 72, x + 110, 130), fill=CAR["hill2"])
    for k in range(-1, 6):
        x = k * 70 - (off * 0.2) % 70 + 30
        d.ellipse((x - 10, 86, x + 80, 136), fill=CAR["hill"])
    d.rectangle((0, 112, W, ROAD_Y), fill=CAR["verge"])
    for k in range(-1, 8):                                                      # roadside trees
        x = k * 56 - (off * 0.5) % 56
        seed = int((off * 0.5) // 56) + k
        if rnd("tree", seed) < 0.6:
            h = 18 + rnd("tree-h", seed) * 16
            d.rectangle((x + 8, 124 - 4, x + 10, 124), fill=CAR["pole"])
            d.ellipse((x, 124 - h, x + 18, 124 - 2), fill=CAR["tree"])
            d.ellipse((x + 3, 124 - h + 2, x + 10, 124 - h + 8), fill=CAR["tree_hi"])
    for k in range(-1, 4):                                                      # telegraph poles
        x = k * 130 - (off * 0.8) % 130
        d.rectangle((x, 40, x + 2, 136), fill=CAR["pole"])
        d.rectangle((x - 6, 44, x + 8, 45), fill=CAR["pole"])
    for k in range(-1, 3):                                                      # the wires sag between them
        x0 = k * 130 - (off * 0.8) % 130
        pts = [(x0 + 130 * p / 10, 46 + 8 * math.sin(math.pi * p / 10)) for p in range(11)]
        d.line(pts, fill=(60, 56, 60))
    blend(img, mask(lambda m: m.rectangle((0, 132, W, 135), fill=255)), CAR["verge_sh"], 0.5)
    d.rectangle((0, 136, W, H), fill=CAR["road"])
    d.line([(0, 137), (W, 137)], fill=CAR["road_hi"])
    for k in range(-1, 12):                                                     # the centre line races by
        x = k * 34 - (off * 1.6) % 34
        d.rectangle((x, 166, x + 16, 167), fill=CAR["line"])
    return img


def car(c):
    img = Image.new("RGB", (W, H), CAR["sky"])
    road_scenery(img, c.t, car_speed(c))
    bob = 1 if (c.ph < 0.25 and c.get("car_bob", True)) else 0
    c.vars["car_bob_y"] = bob
    blend(img, mask(lambda m: m.rectangle((86, 154, 243, 157), fill=255)), (20, 18, 22), 0.5)   # shadow under the car
    car_body(img, bob=bob, lower=False)
    return img


def car_front(c):
    img, bob = c.world, c.get("car_bob_y", 0)
    car_body(img, bob=bob, upper=False)
    for wx in WHEELS:
        wheel(img, wx, CAR_Y, c.t, car_speed(c))
    d = ImageDraw.Draw(img)
    # glass over the passengers: a glint, and the window pillars
    for x0, x1 in ((118, 146), (150, 184)):
        blend_poly(img, [(x0 + 18, 99 + bob), (x0 + 23, 99 + bob), (x0 + 14, 117 + bob), (x0 + 9, 117 + bob)],
                   (240, 248, 255), 0.18)
    d.line([(148, 96 + bob), (148, 120 + bob)], fill=CAR["body"], width=3)
    d.ellipse((176, 108 + bob, 184, 118 + bob), outline=(30, 26, 30))            # the steering wheel


scene("car", mid=car_front,
      shots={"car": (164, 118, 9), "driver": (168, 110, 18), "back": (132, 110, 18), "road": (160, 110, 6)},
      cast={"morgan": dict(x=DRIVER[0], y=DRIVER[1], facing=1, body="sit", outfit="chauffeur", hat="chauffeur",
                           arm="hold", gesture=False, shadow=False),
            "david": dict(x=BACKSEAT[0], y=BACKSEAT[1], facing=1, body="sit", shadow=False)},
      cycle=("car", "driver", "car", "back"))(car)


# --- heaven -----------------------------------------------------------------------------------

HEAVEN = {"top": (255, 236, 200), "bottom": (226, 218, 252), "cloud": (255, 255, 255), "cloud_sh": (222, 222, 244),
          "cloud_sh2": (196, 196, 232), "gold": (246, 204, 90), "gold_sh": (196, 150, 60), "ray": (255, 250, 230)}
HEAVEN_FLOOR = 150


def cloud(d, x, y, w, h, color, seed):
    n = max(3, int(w / 10))
    for k in range(n):
        cx = x + w * (k + 0.5) / n
        r = h * (0.5 + 0.5 * math.sin(math.pi * (k + 0.5) / n)) * (0.8 + 0.3 * rnd(seed, k))
        d.ellipse((cx - r * 1.1, y + h - r * 1.5, cx + r * 1.1, y + h), fill=color)
    d.rectangle((x + 4, y + h - 3, x + w - 4, y + h), fill=color)


@lru_cache(maxsize=1)
def heaven_static():
    img = Image.new("RGB", (W, H), HEAVEN["top"])
    vgrad(img, (0, 0, W, H), HEAVEN["top"], HEAVEN["bottom"], steps=6)
    d = ImageDraw.Draw(img)
    # the pearly gates, far back
    gx, gy = 160, 60
    d.arc((gx - 34, gy - 26, gx + 34, gy + 30), 180, 360, fill=HEAVEN["gold"], width=3)
    for x in range(gx - 30, gx + 31, 6):
        top = gy + 2 - int(math.sqrt(max(0, 30 ** 2 - (x - gx) ** 2)) * 0.8)
        d.line([(x, top), (x, 128)], fill=HEAVEN["gold"])
        d.point((x, top - 1), fill=HEAVEN["gold_sh"])
    d.rectangle((gx - 36, 60, gx - 32, 130), fill=HEAVEN["gold"])
    d.rectangle((gx + 32, 60, gx + 36, 130), fill=HEAVEN["gold"])
    d.line([(gx - 34, 60), (gx - 34, 130)], fill=HEAVEN["gold_sh"])
    # distant clouds, then the cloud floor
    for k, (x, y, w, h) in enumerate(((0, 104, 90, 26), (230, 100, 100, 30), (70, 116, 80, 20), (190, 118, 70, 18))):
        cloud(d, x, y, w, h, HEAVEN["cloud_sh"], ("far-cloud", k))
    for k in range(9):
        x = -20 + k * 40
        cloud(d, x, HEAVEN_FLOOR - 14 - (k % 2) * 4, 56, 22, HEAVEN["cloud_sh"], ("floor", k))
    d.rectangle((0, HEAVEN_FLOOR, W, H), fill=HEAVEN["cloud_sh"])
    for k in range(10):
        x = -16 + k * 38
        cloud(d, x, HEAVEN_FLOOR - 8 + (k % 3) * 3, 50, 20, HEAVEN["cloud"], ("floor-top", k))
    d.rectangle((0, HEAVEN_FLOOR + 10, W, H), fill=HEAVEN["cloud"])
    for k in range(40):
        x, y = rnd("puff", k) * W, HEAVEN_FLOOR + 12 + rnd("puff-y", k) * 16
        d.ellipse((x - 5, y - 2, x + 5, y + 2), fill=HEAVEN["cloud_sh"] if k % 2 else HEAVEN["cloud"])
    return img


def heaven(c):
    img = heaven_static().copy()
    for k in range(6):                                          # rays from above, turning slowly
        a = -math.pi / 2 + (k - 2.5) * 0.28 + math.sin(c.t * 0.2) * 0.05
        pts = [(160, -40), (160 + math.cos(a - 0.05) * 300, -40 - math.sin(a - 0.05) * -300),
               (160 + math.cos(a + 0.05) * 300, -40 - math.sin(a + 0.05) * -300)]
        pts = [(160, -40)] + [(x, -40 + abs(y + 40)) for x, y in pts[1:]]
        blend_poly(img, pts, HEAVEN["ray"], 0.25)
    return img


scene("heaven",
      shots={"throne": (160, 110, 12), "god": (160, 104, 18)},
      cast={"morgan": dict(x=160, y=HEAVEN_FLOOR + 4, facing=-1, outfit="god", shadow=False)})(heaven)
