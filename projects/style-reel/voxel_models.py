"""The voxel models of the diorama: the island with the two stream rooms on it, the house, the baths, the
signs, and the two men in pieces (torso, head, arms) so that they can move.

Every builder is cached and returns a mesh. Coordinates are voxels, y up, +z toward the camera; a model's
origin is wherever is handy for placing it (said in its docstring).
"""
import math
from functools import lru_cache

import script as S
from voxel_engine import Vox, mesh

C = dict(
    grass=(110, 182, 92), grass2=(124, 196, 100), dirt=(140, 102, 74), dirt2=(118, 84, 62), rock=(134, 132, 142),
    rock2=(108, 106, 120), path=(216, 206, 186), path2=(198, 188, 170),
    stucco=(248, 242, 230), trim=(226, 216, 198), roof=(200, 100, 66), roof2=(178, 84, 56), glass=(110, 168, 224),
    glass_hi=(196, 226, 248), door=(112, 72, 46), column=(255, 252, 246), hedge=(58, 126, 68), hedge2=(72, 142, 78),
    trunk=(146, 108, 76), trunk2=(126, 92, 64), palm=(66, 148, 76), palm2=(98, 178, 88), nut=(96, 68, 48),
    pole=(206, 210, 218), red=(220, 38, 44), star=(252, 214, 64),
    tub=(250, 250, 253), tub_sh=(214, 220, 234), water=(98, 186, 240), foam=(255, 255, 255), gold=(238, 192, 70),
    duck=(255, 214, 52), beak=(244, 128, 40),
    hskin=(226, 172, 130), hskin_sh=(196, 140, 104), hhair=(40, 32, 36), hhair_hi=(74, 62, 68), hstub=(152, 108, 90),
    hfade=(104, 80, 72), tank=(240, 238, 232), lip_h=(150, 84, 76), iris_h=(84, 52, 34),
    askin=(238, 212, 194), askin_sh=(210, 176, 158), ahair=(138, 90, 58), ahair_hi=(160, 110, 72),
    ahair_dk=(98, 64, 44), abeard=(94, 60, 44), abeard_dk=(72, 46, 36), tee=(36, 36, 44), tee_hi=(66, 68, 84),
    phones=(32, 32, 40), phones_hi=(120, 122, 142), iris_a=(84, 124, 156), tooth_y=(232, 214, 150),
    eye=(252, 250, 246), mouth=(92, 26, 36), tongue=(214, 92, 100), tooth=(252, 250, 242), line=(58, 30, 30),
    hasan=(150, 96, 255), hasan_hi=(206, 176, 255), asmon=(96, 226, 48), asmon_hi=(176, 252, 128),
    awall=(138, 146, 138), awall2=(116, 124, 118), afloor=(98, 72, 52), afloor2=(84, 60, 44), stain=(120, 44, 40),
    blind=(206, 200, 182), blind2=(148, 142, 126), web=(236, 236, 240), bag=(44, 44, 52), bag2=(64, 64, 76),
    chair_a=(72, 80, 100), chair_a2=(88, 98, 122),
    can=(176, 40, 48), box=(196, 160, 110), adesk=(88, 62, 46), adesk2=(70, 50, 38), rat=(132, 128, 126),
    hwall=(236, 230, 240), hwall2=(224, 216, 232), hfloor=(216, 192, 152), hfloor2=(202, 178, 140),
    led=(184, 120, 255), hdesk=(244, 244, 248), hleg=(64, 64, 74), chair_r=(204, 40, 52), chair_k=(34, 34, 40),
    pot=(190, 106, 72), leaf=(52, 140, 82), leaf2=(74, 164, 96), mic=(26, 26, 32),
    steel=(150, 154, 166), key=(36, 36, 42), board=(22, 26, 44), board2=(34, 40, 64), led_gold=(255, 208, 74),
    led_white=(255, 255, 255), led_red=(255, 76, 70), led_dim=(120, 128, 156),
    fly=(22, 22, 26), wing=(206, 220, 240), stink=(158, 206, 58), dust=(236, 232, 220),
)

# --- lettering ----------------------------------------------------------------------------------

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    # a half, stacked: 1 over a bar over 2, two rows taller than the line above it and below
    "½": ["..#.", ".##.", "..#.", "..#.", "....", "####", "....", "###.", "...#", ".##.", "####"],
}


def cells(text, k=1):
    """The lit cells of a line of text, as (x, y) with y up from the baseline, and the line's width.
    Each cell of a glyph is k x k."""
    out, x = [], 0
    for ch in text:
        if ch == " ":
            x += 3 * k
            continue
        rows = FONT[ch]
        top = len(rows) - 1 - (len(rows) - 7) // 2
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "#":
                    out += [(x + c * k + i, (top - r) * k + j) for i in range(k) for j in range(k)]
        x += (len(rows[0]) + 1) * k
    return out, x - k


def _write(v, text, x, y, z, col, k=1, glow=True):
    lit, w = cells(text, k)
    for cx, cy in lit:
        v.put(x + cx, y + cy, z, col, glow)
    return w


def _shift(m, dx, dy, dz):
    m.corner = m.corner + (dx, dy, dz)
    m.centre = m.centre + (dx, dy, dz)
    return m


# --- the island ---------------------------------------------------------------------------------

AX, HX, CZ = -37, 37, 14                    # the two stream rooms' centres
WALL = 31                                   # how high their walls go


def _room_asmon(v):
    """Asmongold's corner: a grimy wall, the blinds, the stains, the bin bags."""
    x0, x1, z0, z1 = AX - 12, AX + 12, CZ - 11, CZ + 11
    for x in range(x0, x1):
        for z in range(z0, z1):
            v.put(x, 0, z, C["afloor"] if (x // 4 + (z % 2) * 2) % 2 else C["afloor2"])
    for x in range(x0, x1):
        for y in range(1, WALL):
            v.put(x, y, z0, C["awall2"] if S.rnd("aw", x // 3, y // 2) < 0.28 or y < 3 else C["awall"])
    for z in range(z0, z0 + 12):
        for y in range(1, WALL):
            v.put(x0, y, z, C["awall2"] if S.rnd("as", z // 3, y // 2) < 0.28 or y < 3 else C["awall"])
    # the window, its blinds a third of the way down, and the night behind them
    v.box((AX + 5, AX + 12), (14, 29), z0 + 1, C["adesk2"])
    v.box((AX + 6, AX + 11), (15, 28), z0 + 1, (34, 40, 74))
    for y in range(23, 28):
        v.box((AX + 6, AX + 11), y, z0 + 1, C["blind"] if y % 2 else C["blind2"])
    v.put(AX + 9, 20, z0 + 1, (250, 244, 200), True).put(AX + 7, 17, z0 + 1, (200, 210, 250), True)
    # the stains on the wall, and a cobweb in the corner
    for x, y in [(-11, 26), (-10, 26), (-11, 25), (-10, 25), (-9, 25), (-10, 24), (-10, 23), (-11, 22), (-10, 21), (-10, 19)]:
        v.put(AX + x, y, z0, C["stain"])
    for z, y in [(3, 20), (4, 20), (3, 19), (4, 18), (4, 17), (6, 12), (7, 12), (6, 11)]:
        v.put(x0, y, z0 + z, C["stain"])
    for x, y in [(1, 30), (2, 30), (3, 30), (4, 30), (1, 29), (2, 29), (1, 28), (3, 28), (1, 27), (5, 30), (1, 26)]:
        v.put(x0 + x, y, z0 + 1, C["web"])
    # the chair
    v.box((AX - 1, AX + 1), (1, 4), (CZ - 4, CZ - 2), C["key"])
    v.box((AX - 5, AX + 5), 4, (CZ - 6, CZ), C["chair_a"])
    v.box((AX - 5, AX + 5), (5, 20), CZ - 7, C["chair_a"])
    v.box((AX - 4, AX + 4), (6, 19), CZ - 7, C["chair_a2"])
    # the desk, and what is on it
    v.box((AX - 10, AX + 10), 8, (CZ + 2, CZ + 9), C["adesk"])
    v.box(AX - 10, (1, 8), (CZ + 2, CZ + 9), C["adesk2"]).box(AX + 9, (1, 8), (CZ + 2, CZ + 9), C["adesk2"])
    v.box((AX - 9, AX + 9), (3, 8), CZ + 8, C["adesk2"])
    v.box((AX - 4, AX + 3), 9, (CZ + 5, CZ + 7), C["key"])                       # keyboard
    v.box(AX + 5, 9, CZ + 6, C["key"])                                           # mouse
    for x, z, h in [(-8, 4, 2), (-7, 6, 2), (-9, 7, 1), (6, 3, 2)]:                 # cans
        v.box(AX + x, (9, 9 + h), CZ + z, C["can"])
        v.put(AX + x, 8 + h, CZ + z, C["steel"])
    v.box((AX - 9, AX - 5), 9, (CZ + 2, CZ + 4), C["box"])                       # pizza box
    v.box(AX + 8, (9, 12), CZ + 5, C["steel"])                                   # the mic
    v.box((AX + 8, AX + 10), (12, 15), (CZ + 4, CZ + 6), C["mic"])
    # bin bags and a rat
    for bx, bz, h in [(-11, 4, 4), (-8, 7, 3), (8, 9, 3)]:
        v.box((AX + bx, AX + bx + 3), (1, 1 + h), (CZ + bz - 14, CZ + bz - 11), C["bag"])
        v.put(AX + bx + 1, 1 + h, CZ + bz - 13, C["bag2"])
    v.box((AX + 6, AX + 8), 1, CZ - 9, C["rat"]).put(AX + 8, 1, CZ - 9, (224, 150, 150))


def _room_hasan(v):
    """Hasan's corner: a clean wall with a light strip, the poster, the plant."""
    x0, x1, z0, z1 = HX - 12, HX + 12, CZ - 11, CZ + 11
    for x in range(x0, x1):
        for z in range(z0, z1):
            v.put(x, 0, z, C["hfloor"] if (x // 4 + (z % 2) * 2) % 2 else C["hfloor2"])
    for x in range(x0, x1):
        for y in range(1, WALL):
            v.put(x, y, z0, C["hwall2"] if y < 3 else C["hwall"])
    for z in range(z0, z0 + 12):
        for y in range(1, WALL):
            v.put(x1 - 1, y, z, C["hwall2"] if y < 3 else C["hwall"])
    v.box((x0, x1), WALL, z0, C["led"], True).box(x1 - 1, WALL, (z0, z0 + 12), C["led"], True)
    v.box((x0 + 1, x0 + 9), (15, 27), z0 + 1, C["key"])                           # the poster
    v.box((x0 + 2, x0 + 8), (16, 26), z0 + 1, C["red"])
    for x, y in [(4, 23), (5, 23), (3, 22), (4, 22), (5, 22), (6, 22), (4, 21), (5, 21), (3, 20), (6, 20), (4, 24), (5, 24)]:
        v.put(x0 + x, y, z0 + 1, C["star"])
    # the chair: red, a black stripe, wings at the head
    v.box((HX - 1, HX + 1), (1, 4), (CZ - 4, CZ - 2), C["hleg"])
    v.box((HX - 6, HX + 6), 4, (CZ - 6, CZ), C["chair_r"])
    v.box((HX - 6, HX + 6), (5, 22), CZ - 7, C["chair_r"]).box((HX - 2, HX + 2), (5, 22), CZ - 7, C["chair_k"])
    v.box((HX - 7, HX - 5), (17, 22), (CZ - 7, CZ - 5), C["chair_r"]).box((HX + 5, HX + 7), (17, 22), (CZ - 7, CZ - 5), C["chair_r"])
    # the desk
    v.box((HX - 10, HX + 10), 8, (CZ + 2, CZ + 9), C["hdesk"])
    for x in (HX - 10, HX + 9):
        v.box(x, (1, 8), CZ + 2, C["hleg"]).box(x, (1, 8), CZ + 8, C["hleg"])
    for i, col in enumerate([(255, 70, 80), (255, 160, 60), (250, 230, 80), (90, 230, 120), (80, 170, 255), (190, 110, 255), (255, 110, 200)]):
        v.box(HX - 4 + i, 9, (CZ + 5, CZ + 7), col, True)                        # the keyboard, lit
    v.box(HX + 5, 9, CZ + 6, C["key"])
    v.box(HX + 8, (9, 12), CZ + 3, C["steel"]).put(HX + 8, 12, CZ + 3, C["hasan"])  # a shaker
    v.box(HX - 9, (9, 12), CZ + 5, C["steel"])                                   # the mic
    v.box((HX - 10, HX - 8), (12, 15), (CZ + 4, CZ + 6), C["mic"])
    # the plant
    v.box((x1 - 5, x1 - 2), (1, 4), (CZ - 9, CZ - 6), C["pot"])
    for x, y, z in [(1, 4, -8), (2, 5, -8), (1, 6, -8), (0, 7, -9), (2, 7, -7), (1, 8, -8), (3, 6, -8), (0, 5, -7),
                    (2, 9, -8), (1, 10, -9), (3, 8, -9), (0, 9, -7), (1, 11, -8), (2, 6, -9), (4, 7, -8), (0, 8, -8),
                    (1, 12, -8), (2, 13, -8), (0, 11, -8), (3, 10, -8), (1, 14, -8)]:
        v.put(x1 - 6 + x, y, CZ + z, C["leaf"] if (x + y) % 2 else C["leaf2"])


@lru_cache(maxsize=None)
def island():
    """The floating base and everything that never moves on it. World coordinates."""
    v = Vox()
    x0, x1, z0, z1 = -52, 52, -30, 29
    for x in range(x0, x1):
        for z in range(z0, z1):
            edge = min(x - x0, x1 - 1 - x, z - z0, z1 - 1 - z)
            if edge < 2 and min(x - x0, x1 - 1 - x) + min(z - z0, z1 - 1 - z) < 3:
                continue                                                         # the corners, knocked off
            v.put(x, -1, z, C["grass"] if ((x + z) // 6) % 2 else C["grass2"])
            depth = 2 + int(min(edge, 14) * (0.35 + 0.5 * S.rnd("isle", x // 3, z // 3)))
            for y in range(-2, -2 - depth, -1):
                d = -2 - y
                if d < 2:
                    v.put(x, y, z, C["dirt"] if S.rnd("d", x, y, z) < 0.8 else C["dirt2"])
                elif edge >= d - 1:
                    v.put(x, y, z, C["rock"] if S.rnd("r", x // 2, y, z // 2) < 0.6 else C["rock2"])
    for z in range(-10, 14):                                                     # the path from the door
        for x in range(-2, 2):
            v.put(x, -1, z, C["path"] if S.rnd("p", x, z) < 0.7 else C["path2"])
    _room_asmon(v)
    _room_hasan(v)
    return mesh(v, 0.035, 2)


# --- the house and its lawn ----------------------------------------------------------------------

@lru_cache(maxsize=None)
def mansion():
    """Hasan's house. Origin: the middle of its footprint, on the ground; the front is +z."""
    v = Vox()
    v.box((-11, 11), (0, 12), (-7, 5), C["stucco"])
    v.box((-20, -11), (0, 8), (-6, 4), C["stucco"]).box((11, 20), (0, 8), (-6, 4), C["stucco"])
    v.box((-11, 11), 11, 4, C["trim"]).box((-20, -11), 7, 3, C["trim"]).box((11, 20), 7, 3, C["trim"])
    for i in range(5):                                                           # the roofs, stepped
        v.box((-12 + 2 * i, 12 - 2 * i), 12 + i, (-8 + i, 6 - i), C["roof"] if i % 2 == 0 else C["roof2"])
    for i in range(3):
        col = C["roof"] if i % 2 == 0 else C["roof2"]
        v.box((-21 + i, -11), 8 + i, (-7 + i, 5 - i), col).box((11, 21 - i), 8 + i, (-7 + i, 5 - i), col)
    v.box((6, 8), (13, 19), (-4, -2), C["trim"])                                # chimney
    # the portico: a step, four columns, a gable
    v.box((-7, 7), 0, (5, 10), C["path"])
    for x in (-6, -3, 2, 5):
        v.box(x, (1, 9), 8, C["column"])
    v.box((-7, 7), 9, (5, 10), C["column"])
    for i in range(3):
        v.box((-6 + 2 * i, 6 - 2 * i), 10 + i, (6, 10), C["stucco"])
    v.box((-1, 1), (0, 6), 4, C["door"]).put(0, 3, 4, C["gold"])

    def window(x, y, w=2, h=3, z=4):
        v.box((x, x + w), (y, y + h), z, C["glass"])
        v.put(x, y + h - 1, z, C["glass_hi"])

    for x in (-10, -5, 3, 8):
        window(x, 7, 2, 3)
        window(x, 2, 2, 3)
    window(-18, 2, 4, 4, 3)
    window(14, 2, 4, 4, 3)
    for x in list(range(-20, -12)) + list(range(12, 20)):                        # hedges under the wings' windows
        v.box(x, (0, 2), (4, 6), C["hedge"] if x % 2 else C["hedge2"])
    v.box(0, (16, 30), -1, C["pole"]).put(0, 30, -1, C["gold"])                   # the flagpole
    return mesh(v, 0.02, 3)


@lru_cache(maxsize=None)
def palm(seed=0):
    """A palm tree. Origin: the foot of the trunk."""
    v = Vox()
    lean = 1 if seed % 2 else -1
    for y in range(16):
        x = lean * (y // 6)
        v.box((x, x + 2), y, (0, 2), C["trunk"] if y % 2 else C["trunk2"])
    tx = lean * 2
    for k, (dx, dz) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]):
        for i, drop in enumerate([0, 0, 0, 1, 2, 3] if k < 4 else [0, 0, 1, 2]):
            col = C["palm"] if (i + k) % 2 else C["palm2"]
            x, z, y = tx + dx * (i + 1), dz * (i + 1), 16 - drop
            v.put(x, y, z, col).put(x + 1, y, z, col).put(x, y, z + 1, col).put(x + 1, y, z + 1, col)
    v.box((tx, tx + 2), 16, (0, 2), C["palm"]).box((tx, tx + 2), 17, (0, 2), C["palm2"])
    v.put(tx - 1, 15, 0, C["nut"]).put(tx + 2, 15, 1, C["nut"])
    return mesh(v, 0.05, 4 + seed)


@lru_cache(maxsize=None)
def tub(half=False):
    """A clawfoot bath, full, end on to the camera, its high back at the far end. Origin: a corner of its
    footprint; 6 wide (x), 9 long (z). The half is the back of one, cut clean through and running out."""
    v = Vox()
    v.box((1, 5), 1, (1, 8), C["tub_sh"])
    v.box((0, 6), (2, 5), (0, 9), C["tub"])
    v.box((1, 5), (2, 5), (1, 8), C["water"])
    for x, z in ((0, 0), (5, 0), (0, 8), (5, 8)):
        v.cut(x, (2, 5), z)
    v.box((1, 5), (5, 7), 0, C["tub"]).cut(1, 6, 0).cut(4, 6, 0)                    # the high back
    for x in (0, 5):
        v.put(x, 5, 1, C["tub"]).put(x, 5, 2, C["tub"])
    v.box((2, 4), (5, 7), 1, C["gold"])                                          # the taps
    for x, z in [(1, 5), (2, 7), (4, 7), (1, 3), (4, 2)]:
        v.put(x, 5, z, C["foam"])
    v.put(1, 6, 5, C["foam"])
    v.put(3, 5, 4, C["duck"]).put(4, 5, 4, C["duck"]).put(4, 6, 4, C["duck"]).put(4, 6, 5, C["beak"])
    for x in (0, 5):
        for z in (1, 7):
            v.box(x, (0, 2), z, C["gold"])
    if half:
        v.cut((0, 6), (0, 9), (5, 10))
        v.box(0, (0, 2), 4, C["gold"]).box(5, (0, 2), 4, C["gold"])
        v.box((1, 5), 1, 5, C["water"]).box((2, 4), 2, 5, C["water"])            # what runs out of it
        for x in range(0, 6):
            for z in range(5, 9):
                if (x in (0, 5)) + (z >= 7) + (z == 8) < 2:
                    v.put(x, 0, z, C["water"])
    return mesh(v, 0.012, 5)


@lru_cache(maxsize=None)
def tag(ch):
    """A number on a little board, to hang over a bath. Origin: the middle of its foot; it faces +z."""
    v = Vox()
    w = cells(ch)[1]
    x0 = -(w + 4) // 2
    v.box((x0, x0 + w + 4), (0, 13), 0, C["board"])
    _write(v, ch, x0 + 2, 3, 1, C["led_gold"])
    return mesh(v, 0.0, 16)


@lru_cache(maxsize=None)
def flag(phase=0):
    """The red flag, blowing. Origin: the foot of its hoist; it flies toward +x."""
    v = Vox()
    for x in range(10):
        dz = round(1.4 * (x / 9) * math.sin(phase * math.pi / 4 - x * 0.75))
        for y in range(7):
            v.put(x, y, dz, C["red"])
        if 1 <= x <= 3:
            for y in ((4, 5) if x != 2 else (3, 4, 5, 6)):
                v.put(x, y, dz, C["star"])
    return mesh(v, 0.02, 6)


@lru_cache(maxsize=None)
def plaque():
    """The count, on a board to lean against the lawn's edge. Origin: the middle of its foot; it faces +z."""
    v = Vox()
    w = cells("5½ BATHS")[1]
    x0 = -(w + 8) // 2
    x1 = x0 + w + 8
    v.box((x0, x1), (0, 17), 0, C["board"])
    v.box((x0, x1), 0, 0, C["led_gold"]).box((x0, x1), 16, 0, C["led_gold"])
    v.box(x0, (0, 17), 0, C["led_gold"]).box(x1 - 1, (0, 17), 0, C["led_gold"])
    _write(v, "5½", x0 + 4, 5, 1, C["led_gold"])
    _write(v, "BATHS", x0 + 4 + cells("5½ ")[1] + 1, 5, 1, C["led_white"])
    return mesh(v, 0.0, 7)


@lru_cache(maxsize=None)
def scoreboard(me="?"):
    """BATHS THIS YEAR: ME on Asmongold's side, HIM on Hasan's. Origin: the middle of its foot, facing +z.
    Built small: place it at 0.6 of a voxel."""
    v = Vox()
    w = cells("BATHS THIS YEAR")[1]
    x0 = -(w + 8) // 2
    x1 = x0 + w + 8
    v.box((x0, x1), (5, 60), 0, C["board"])
    v.box((x0 + 4, x0 + 7), (0, 5), 0, C["hleg"]).box((x1 - 7, x1 - 4), (0, 5), 0, C["hleg"])
    v.box((x0, x1), (48, 60), 0, C["board2"])
    _write(v, "BATHS THIS YEAR", x0 + 4, 50, 1, C["led_gold"])
    mid = (x0 + x1) // 2
    for a, b, col, hi, label, value, vcol in [(x0 + 2, mid - 1, C["asmon"], C["asmon_hi"], "ME", me, C["led_red"] if me == "0" else C["led_dim"] if me == "?" else C["led_white"]),
                                              (mid + 1, x1 - 2, C["hasan"], C["hasan_hi"], "HIM", "5½", C["led_white"])]:
        v.box((a, b), 7, 1, col, True).box((a, b), 45, 1, col, True).box(a, (7, 46), 1, col, True).box(b - 1, (7, 46), 1, col, True)
        lw = cells(label)[1]
        _write(v, label, (a + b - lw) // 2, 36, 1, hi)
        vw = cells(value, 2)[1]
        _write(v, value, (a + b - vw) // 2, 15, 1, vcol, 2)
    return mesh(v, 0.0, 8)


# --- the men ------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def torso(who):
    """Shoulders to seat. Origin: a low back corner; the pivots are in PIVOT."""
    v = Vox()
    if who == "hasan":
        v.box((4, 13), (0, 7), (0, 6), C["tank"]).box((2, 15), (7, 9), (0, 6), C["tank"])
        v.box((0, 17), (9, 11), (0, 6), C["hskin"])
        v.box((2, 4), (7, 9), (0, 6), C["hskin"]).box((13, 15), (7, 9), (0, 6), C["hskin"])
        v.box((5, 7), (9, 11), (0, 6), C["tank"]).box((10, 12), (9, 11), (0, 6), C["tank"])    # the straps
        v.box((4, 8), (6, 9), 6, C["tank"]).box((9, 13), (6, 9), 6, C["tank"])                 # the chest
        v.box((6, 11), (11, 13), (1, 5), C["hskin"]).box((4, 13), 11, (1, 4), C["hskin"])      # neck
        for x, y in [(6, 10), (10, 10), (6, 9), (10, 9), (7, 8), (9, 8), (8, 7), (8, 6)]:
            v.put(x, y, 6, C["gold"])                                                         # the chain
    else:
        v.box((1, 8), (0, 8), (0, 5), C["tee"]).box((0, 9), (6, 8), (0, 5), C["tee"])
        v.box((3, 6), 7, 4, C["tee_hi"])
        v.box((3, 6), (8, 10), (1, 4), C["askin"])
    return mesh(v, 0.025, 9)


PIVOT = {       # in the torso's own coordinates: where it sits, where the neck ends, the two shoulders (-x, +x)
    "hasan": dict(seat=(8.5, 0, 3), neck=(8.5, 12.5, 3), shoulders=((0.8, 9.6, 3), (16.2, 9.6, 3)), arm=(6.0, 5.2)),
    "asmon": dict(seat=(4.5, 0, 2.5), neck=(4.5, 9.5, 2.5), shoulders=((0.6, 6.8, 2.5), (8.4, 6.8, 2.5)), arm=(5.0, 4.6)),
}


@lru_cache(maxsize=None)
def limb(who, part, hand="fist"):
    """An arm bone, hanging down from its joint. Origin: the joint, in the middle of the bone's top."""
    v = Vox()
    skin = C["hskin"] if who == "hasan" else C["askin"]
    if who == "hasan":
        if part == "upper":
            v.box((-2, 2), (-6, 0), (-2, 2), skin)
        elif part == "fore":
            v.box((-2, 2), (-5, 0), (-2, 2), skin)
        elif hand == "palm":
            v.box((-1, 1), (-5, 0), (-2, 2), skin)
        else:
            v.box((-2, 2), (-3, 0), (-2, 2), skin)
        return mesh(v, 0.02, 10)
    if part == "upper":
        v.box((-1, 2), (-5, 0), (-1, 2), skin).box((-1, 2), (-2, 0), (-1, 2), C["tee"])
    elif part == "fore":
        v.box((-1, 1), (-5, 0), (-1, 1), skin)
    elif hand == "thumb":                   # a fist about the wrist, held upright whatever the arm does
        v.box((-1, 2), (-1, 2), (-1, 2), skin).box(-1, (2, 5), (0, 2), skin)
    else:
        v.box((-1, 2), (-3, 0), (-1, 2), skin)
        if hand == "point":
            v.box(0, (-6, -3), 0, skin)
    m = mesh(v, 0.02, 10)
    return m if part == "fore" else _shift(m, -0.5, 0, -0.5)        # three wide: centre it on the joint


@lru_cache(maxsize=None)
def head_asmon(gape=0, wide=3, teeth=False, look=1, shut=False):
    """Asmongold's head: the long hair parted over a high forehead, the beard, the headphones. Origin: a low
    back corner of the skull (11 wide, 14 tall, 10 deep); the neck meets it at (5.5, 0, 4.5)."""
    v = Vox()

    def hair(*key):
        return C["ahair_hi"] if S.rnd("ah", *key) < 0.3 else C["ahair"]

    v.box((0, 11), (0, 14), (0, 10), C["askin"])
    Z = 9
    ends = {-2: -4, -1: -7, 0: -6, 1: -4, 9: -5, 10: -7, 11: -6, 12: -4}          # where each lock stops
    for x in range(0, 11):                                   # the top of it: back from the brow, parted
        for z in range(-1, 8):
            v.put(x, 14, z, C["ahair_dk"] if x == 5 else hair(x, z // 2))
    for x in range(-1, 12):                                  # down the back
        for y in range(-7, 14):
            v.put(x, y, -1, hair(x, y // 3, 50))
    for x in (-1, 11):                                       # down the sides
        for y in range(ends[x], 14):
            for z in range(0, 10):
                v.put(x, y, z, hair(x, y // 3, z // 3))
    for x in (-2, 12):                                       # spreading over the shoulders
        for y in range(ends[x], 3):
            for z in range(1, 11):
                v.put(x, y, z, hair(x, y // 3, z // 3))
    for x, top in ((-1, 12), (0, 12), (10, 12), (11, 12), (1, -1), (9, -1)):      # and down in front of them
        for y in range(ends[x], top + 1):
            v.put(x, y, 10, hair(x, y // 3, 70))
    for x, y in ((0, 13), (1, 13), (2, 13), (8, 13), (9, 13), (10, 13), (1, 12), (9, 12)):
        v.put(x, y, Z, hair(x, y, 80))                       # the parting, down each side of the forehead
    # the face
    for xs in ((2, 4), (7, 9)):
        v.box(xs, 10, Z, C["ahair_dk"]).box(xs, 8, Z, C["askin_sh"])
        if shut:
            v.box(xs, 9, Z, C["askin_sh"])
        else:
            a, b = (xs[0], xs[0] + 1) if look > 0 else (xs[0] + 1, xs[0])
            v.put(a, 9, Z, C["eye"]).put(b, 9, Z, C["iris_a"])
    v.box(5, (6, 9), 10, C["askin"]).put(5, 6, 11, C["askin"])                    # the nose
    v.put(4, 6, Z, C["askin_sh"]).put(6, 6, Z, C["askin_sh"])
    # the beard: the lip, the jaw, and on down to a point
    v.box((3, 8), 5, Z, C["abeard"]).box((1, 10), (0, 5), Z, C["abeard"])
    drop = 1 if gape >= 2 else 0
    if drop:
        v.box((1, 10), -1, (5, 10), C["abeard"])
    v.box((1, 10), -1 - drop, (5, 10), C["abeard"]).box((2, 9), -2 - drop, (6, 10), C["abeard"])
    v.box((3, 8), -3 - drop, (7, 10), C["abeard_dk"]).box((4, 7), -4 - drop, (8, 10), C["abeard_dk"])
    xs = (5 - wide // 2, 6 + wide // 2)
    if gape == 0:
        v.box(xs, 3, Z, C["line"])
    else:
        v.box(xs, (4 - gape, 4), Z, C["mouth"])
        if teeth:
            v.box(xs, 3, Z, C["tooth_y"])
            if wide >= 3:
                v.put(5 + (1 if wide > 3 else 0), 3, Z, C["mouth"])                # not all of his teeth
        if gape == 3:
            v.box((xs[0] + (1 if wide > 1 else 0), xs[1] - (1 if wide > 1 else 0)), 1, Z, C["tongue"])
    # the headphones
    v.box((-2, 13), 15, (3, 6), C["phones"]).box(-2, (10, 15), (3, 6), C["phones"]).box(12, (10, 15), (3, 6), C["phones"])
    v.box((-3, -1), (4, 10), (2, 7), C["phones"]).box((12, 14), (4, 10), (2, 7), C["phones"])
    v.box((-3, -1), (5, 9), 7, C["phones_hi"]).box((12, 14), (5, 9), 7, C["phones_hi"])
    return mesh(v, 0.03, 11)


@lru_cache(maxsize=None)
def head_hasan(face="smug", look=-1):
    """Hasan's head: the square jaw under stubble, the heavy brows, the hair swept up. Origin: a low back
    corner of the skull (13 wide, 11 tall, 10 deep); the neck meets it at (6.5, 0, 4.5)."""
    v = Vox()
    v.box((0, 13), (0, 11), (0, 10), C["hskin"])
    v.box(-1, (5, 8), (4, 7), C["hskin"]).box(13, (5, 8), (4, 7), C["hskin"])
    # the hair: up and forward at the front, faded at the sides
    for (xs, y, zs) in [((0, 13), 11, (0, 10)), ((1, 12), 12, (1, 11)), ((2, 11), 13, (4, 11)), ((3, 10), 14, (7, 11))]:
        for x in range(*xs):
            for z in range(*zs):
                v.put(x, y, z, C["hhair_hi"] if S.rnd("hh", x, z // 3) < 0.16 else C["hhair"])
    v.paint(0, (7, 11), (0, 10), C["hfade"]).paint(12, (7, 11), (0, 10), C["hfade"]).paint((0, 13), (5, 11), 0, C["hfade"])
    Z = 9
    v.box((0, 2), 10, Z, C["hhair"]).box((11, 13), 10, Z, C["hhair"])
    v.box((1, 6), 8, Z, C["hhair"]).box((7, 12), 8, Z, C["hhair"])                # the brows
    for x0 in (2, 8):
        if face == "ugh":
            v.box((x0, x0 + 3), 6, Z, C["hhair"]).box((x0, x0 + 3), 7, Z, C["hskin_sh"])       # screwed shut
            continue
        iris = (x0, x0 + 1) if look < 0 else (x0 + 1, x0 + 2)
        for x in range(x0, x0 + 3):
            dark = x in iris
            v.put(x, 6, Z, C["iris_h"] if dark else C["eye"])
            v.put(x, 7, Z, C["hskin_sh"] if face in ("smug", "flat") else C["iris_h"] if dark else C["eye"])
    v.box(6, (4, 8), 10, C["hskin"]).box((5, 8), 4, 10, C["hskin_sh"]).put(6, 4, 11, C["hskin"])      # the nose
    # stubble: the jaw, the lip, the chin
    v.box((0, 13), (0, 4), Z, C["hstub"]).box((0, 3), 4, Z, C["hstub"]).box((10, 13), 4, Z, C["hstub"])
    v.paint(0, (0, 5), (3, 10), C["hstub"]).paint(12, (0, 5), (3, 10), C["hstub"])
    v.box((4, 9), (0, 2), 10, C["hstub"])
    if face == "smug":
        v.box((5, 10), 2, Z, C["tooth"]).put(10, 3, Z, C["lip_h"]).put(4, 2, Z, C["lip_h"])
    elif face == "flat":
        v.box((4, 9), 2, Z, C["lip_h"])
    else:
        v.box((5, 8), (2, 4), Z, C["mouth"]).put(4, 2, Z, C["lip_h"]).put(8, 2, Z, C["lip_h"])
        v.box((5, 8), 3, Z, C["tooth"])
    return mesh(v, 0.025, 12)


# --- small things -------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def fly(flap=0):
    """A fly, nose toward +x, built small: place it at half a voxel. Origin: its middle."""
    v = Vox()
    v.box((-2, 2), (0, 2), (-1, 1), C["fly"]).box(2, (0, 2), (-1, 1), (126, 30, 30))
    if flap:
        v.box((-1, 1), (2, 4), -2, C["wing"]).box((-1, 1), (2, 4), 1, C["wing"])
    else:
        v.box((-1, 1), 2, (-3, -1), C["wing"]).box((-1, 1), 2, (1, 3), C["wing"])
    return _shift(mesh(v, 0.0, 13), 0, -1, 0)


@lru_cache(maxsize=None)
def cube(name, glow=False):
    """One voxel of a colour, about its middle: dust, a fly's wake, the smell."""
    v = Vox()
    v.put(0, 0, 0, C[name], glow)
    return _shift(mesh(v, 0.0, 14), -0.5, -0.5, -0.5)


@lru_cache(maxsize=None)
def cloud(seed=0):
    """A cloud of a few big blocks, lit from inside. Origin: its low corner."""
    v = Vox()
    for i in range(5):
        x, w, h = int(S.rnd("cx", seed, i) * 8), 3 + int(S.rnd("cw", seed, i) * 4), 1 + int(S.rnd("ch", seed, i) * 2)
        z = int(S.rnd("cz", seed, i) * 3)
        v.box((x, x + w), (0, 1), (z, z + 3), (226, 236, 250), True)
        v.box((x, x + w), (1, 1 + h), (z, z + 3), (252, 253, 255), True)
    return mesh(v, 0.0, 17 + seed)
