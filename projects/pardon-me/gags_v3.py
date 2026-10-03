"""Verse 3 gags: Trump has the rostrum again, Bibi heckles from the desk (lines v3 0-11).

Two things carry across lines. The front row walks out on Bibi in line 0 and its seats stay
empty (with Bibi's science-fair board still on his desk) until the camera cuts in on Trump's
"Me?" in line 4, which hides the reset. From "my name on every wall" the hall wears Trump's
name: gold letters over Bibi's desk and a gold T where the UN emblem was, to the end of the verse.
"""
import math
from functools import cache, lru_cache

from PIL import Image, ImageDraw

import art_v3 as A
from gagkit import (
    INK,
    PRESS,
    PRESS16,
    SILK,
    TL,
    C,
    H,
    P,
    V,
    W,
    back_out,
    bomb_doodle,
    check,
    circle_pts,
    clamp,
    ease_in,
    ease_in_out,
    ease_out,
    face,
    flip,
    gag,
    hall,
    hit_t,
    lerp,
    line_t,
    mirror,
    mix,
    page_title,
    paste,
    pixel,
    pop_text,
    pose,
    ramp,
    ring,
    rnd,
    scaled,
    screen_fill,
    span,
    sparkle,
    stroke,
    world_text,
    write,
    wt,
)

SEC = "v3"
END = TL.section_end(SEC)
RED = P.mk("red")


def T(idx, pat=None, n=0):
    """When line `idx` of this verse (or the n-th word in it matching `pat`) starts."""
    return line_t(SEC, idx, pat, n)


def live_from(idx):
    """When line `idx`'s gag goes live (the runner starts a gag 0.12 s before its line)."""
    return T(idx) - 0.12


ZOOM_IN, ZOOM_OUT = T(4, r"^Me\?") - 0.06, T(4, r"^I$") - 0.24     # the one cut-in of the verse
RESET = ZOOM_IN                 # what lines 0-3 left in the hall goes on the cut, out of shot


# --- 0: the walkouts (and the empty hall, lines 0-3) ---------------------------------------------------

PROMPTER_GO, PROMPTER_SPEED, PROMPTER_FEET = T(0, "machines") - 0.1, 125.0, 147


def walking_prompters(c, layer):
    """The two glass teleprompters walk out on "the machines walked out", one each way: from behind the
    rostrum (drawn in "back") and, once clear of it, in front of the chart or behind the desk ("mid")."""
    age = c.t - PROMPTER_GO
    if age < 0:
        return
    for side, x0 in ((-1, 150), (1, 170)):
        x = x0 + side * PROMPTER_SPEED * age
        clear = x < 124 if side < 0 else x > 196
        if clear != (layer == "mid") or not -20 < x < W + 20:
            continue
        step = int(age * 9) % 2
        spr = A.prompter(step)
        paste(c.world, mirror(spr) if side < 0 else spr, x, PROMPTER_FEET - step, "mb")


ROW = sorted(hall.DELEGATES)                                          # (x, y, i), left to right
WALK_GO = T(0, "people") - 0.04
WALK_GAP, WALK_STAND, WALK_SPEED = 0.075, 0.15, 130.0
PRES_GO = T(0, r"^you\.") - 0.15                                    # the President goes last, on "you"
PRES_EXIT_X = 120                                                     # where he goes down the dais steps


LEDGE_TOP = hall.LEDGE_Y - 1                                          # the dais ledge's top edge (ink)
DAIS_VIEW = (hall.SCREEN_L[2] + 2, 0, hall.SCREEN_R[0], LEDGE_TOP)     # what shows over the ledge, between the screens


def paste_clipped(img, spr, left, top, box):
    """Paste `spr` with its top-left at (left, top), showing only the part inside `box` (x0, y0, x1, y1)."""
    left, top = round(left), round(top)
    x0, y0 = max(left, box[0]), max(top, box[1])
    x1, y1 = min(left + spr.width, box[2]), min(top + spr.height, box[3])
    if x1 > x0 and y1 > y0:
        part = spr.crop((x0 - left, y0 - top, x1 - left, y1 - top))
        img.paste(part, (x0, y0), part)


@cache
def standing_president():
    """The President's sprite with his jacket run on down a few rows, for when he gets up."""
    spr = hall.president_sprite()
    out = Image.new("RGBA", (spr.width, spr.height + 4), (0, 0, 0, 0))
    out.paste(spr, (0, 0))
    last = spr.crop((0, spr.height - 1, spr.width, spr.height))
    for k in range(4):
        out.paste(last, (0, spr.height + k))
    return out


def president_leaving(img, a):
    """The President of the Assembly `a` seconds after he gets up: he stands, shuffles off along the dais
    and goes down its steps, only ever seen above the ledge."""
    spr = standing_president()
    x0, y0 = hall.PRESIDENT
    rise = 3 * ease_out(clamp(a / 0.15, 0, 1))
    walk = clamp((a - 0.2) / 0.6, 0, 1)
    sink = 26 * ease_in(clamp((a - 0.85) / 0.3, 0, 1))
    bob = 1 if 0 < walk < 1 and int(a * 10) % 2 else 0
    x = round(lerp(x0, PRES_EXIT_X, walk))
    top = round(y0 - (spr.height - 4) + 1 - rise + sink + bob)
    paste_clipped(img, spr, x - spr.width // 2, top, DAIS_VIEW)


@span(WALK_GO, RESET)
def empty_front_row(c, L):
    """The front row stands up and files out to the left, the seat by the door first, the one next to Bibi
    last; then the President gets up and goes too. The chairs (and the chair) stay empty."""
    walkers = []
    for k, (x, y, i) in enumerate(ROW):
        age = c.t - (WALK_GO + k * WALK_GAP)
        if age < 0:
            continue
        if age < WALK_STAND:
            c.crowd["stand"][i] = ease_out(age / WALK_STAND)
            continue
        c.crowd["gone"].add(i)
        wx = x - WALK_SPEED * (age - WALK_STAND)
        if wx > -14:
            walkers.append((round(wx), y - int(age * 10) % 2, i))
    if c.t >= PRES_GO:
        c.president["hidden"] = True
    yield "back"
    if c.t >= PRES_GO:
        president_leaving(c.world, c.t - PRES_GO)
    yield "front"
    d = ImageDraw.Draw(c.world)
    for wx, y, i in walkers:
        hall.delegate(d, wx, y, i, stand=1.0)


@gag(SEC, 0)
def walked_out_on_you(c, L):
    """"The machines walked out on me?": the teleprompters walk off on little legs, and Trump shrugs. "Bibi,
    the people walked out on you": the front row gets up and leaves, then the President of the Assembly."""
    t = c.t
    t_me, t_bibi = wt(L, r"^me\?"), wt(L, r"^Bibi")
    if t_me - 0.04 <= t < t_bibi - 0.08:
        pose(c, "trump", arm="shrug", far="out")
    elif t_bibi - 0.08 <= t < WALK_GO + 0.7:
        pose(c, "trump", arm="point")
    if WALK_GO + 0.5 <= t < hit_t(L):
        face(c, "bibi", eyes="wide", brows="worried", mouth="o")
    yield "back"
    walking_prompters(c, "back")
    yield "mid"
    walking_prompters(c, "mid")


# --- 1: crowd sizes ------------------------------------------------------------------------------------

CROWD_FLIP = live_from(1)
BASE = 46                                   # the crowd chart's baseline
ME_X = (79, 86)                             # Trump's bar (chart x); it runs off the page and up the wall


def zzz(img, x, y, t, color="blue"):
    """Three z's drifting up from (x, y), on a loop."""
    for k in range(3):
        ph = (t * 0.9 + k / 3) % 1.0
        s = 2 + k
        zx, zy = x + 4 * k + ph * 2, y - 5 * k - ph * 4
        stroke(img, [(zx, zy), (zx + s, zy), (zx, zy + s), (zx + s, zy + s)], color)


def sleeper(img, x, y, p, color="black"):
    """A stick figure asleep on its back on y, head at x, one knee up."""
    segs = [circle_pts(x + 2, y - 3, 2.5, n=12), [(x + 5, y - 2), (x + 12, y - 2)],
            [(x + 12, y - 2), (x + 15, y - 6), (x + 18, y - 1)], [(x + 7, y - 2), (x + 9, y - 5), (x + 12, y - 3)]]
    for i, seg in enumerate(segs):
        stroke(img, seg, color, p * len(segs) - i)


def hatched_bar(img, x0, y0, x1, y1, off=0, cap=False):
    """A bar in red marker: two sides and diagonal hatching (the hatching lines up across `off`)."""
    d = ImageDraw.Draw(img)
    y0, y1 = int(y0), int(y1)
    d.line([(x0, y0), (x0, y1)], fill=RED)
    d.line([(x1, y0), (x1, y1)], fill=RED)
    if cap:
        d.line([(x0, y0), (x1, y0)], fill=RED)
    pts = [(x, y) for y in range(y0, y1) for x in range(x0 + 1, x1) if (x + y + off) % 3 == 0]
    if pts:
        d.point(pts, fill=RED)


def me_bar_height(t):
    """How far Trump's bar has risen from the baseline: past the top of the page, up to the ceiling."""
    return ease_out((t - T(1, r"^It")) / 0.4) * (BASE + hall.CHART[1])


def crowd_page(c, page):
    """CROWD SIZE: Bibi's stub under a magnifying glass, Biden's one dozing fan, and ME."""
    t = c.t
    page_title(page, "CROWD SIZE", "black", age=t - CROWD_FLIP - 0.1, underline_color="red")
    stroke(page, [(4, BASE), (86, BASE)], "black", (t - CROWD_FLIP - 0.4) / 0.3)
    t_bibi, t_glass, t_biden, t_me = T(1, "crowd"), T(1, "ever"), T(1, "Biden"), T(1, r"^It")
    if t >= t_bibi:
        write(page, (16, BASE + 3), "BIBI", "blue", age=t - t_bibi, anchor="ma")
        if t >= t_bibi + 0.12:
            ImageDraw.Draw(page).line([(15, BASE - 1), (17, BASE - 1)], fill=RED)
    if t >= t_glass:
        p = (t - t_glass) / 0.3
        ring(page, 16, BASE - 5, 5, color="black", p=p)
        stroke(page, [(20, BASE - 9), (25, BASE - 14)], "black", (p - 1) * 3, width=2)
    if t >= t_biden - 0.2:
        p = (t - t_biden + 0.2) / 0.3
        sleeper(page, 38, BASE - 1, p)
        write(page, (47, BASE + 3), "BIDEN", "blue", age=t - t_biden, anchor="ma")
        if p >= 1:
            zzz(page, 42, BASE - 10, t)
    if t >= t_me:
        write(page, ((ME_X[0] + ME_X[1]) // 2 + 1, BASE + 3), "ME", "red", age=t - t_me, anchor="ma", bold=True)
        top = BASE - me_bar_height(t)
        hatched_bar(page, ME_X[0], max(0, top), ME_X[1], BASE, off=sum(hall.CHART[:2]), cap=top >= 0)


def me_bar_wall(c):
    """The rest of Trump's bar, in marker up the wall above the chart."""
    x0, y0 = hall.CHART[:2]
    top = y0 + BASE - me_bar_height(c.t)
    if c.t >= T(1, r"^It") and top < y0:
        hatched_bar(c.world, x0 + ME_X[0], max(0, top), x0 + ME_X[1], y0, cap=top >= 0)


@gag(SEC, 1)
def smallest_crowd(c, L):
    """"Smallest crowd I've ever seen, and I've seen Biden's. It's true.": a crowd-size chart. Bibi's stub
    needs a magnifying glass, Biden's crowd is one man asleep, and on "It's true" Trump's own bar goes
    off the page and up the wall."""
    flip(c, CROWD_FLIP)
    yield "chart"
    crowd_page(c, c.page)
    yield "mid"
    me_bar_wall(c)


# --- 2: the science fair -------------------------------------------------------------------------------

BOARD_UP = T(2, "poster")
BOARD_X, BOARD_Y = 235, 145                 # bottom centre of the trifold, standing on Bibi's desk
VOLCANO_X, VOLCANO_Y = 226, 148             # bottom centre of the volcano, on the desk in front of the board
ROSETTE_XY = (214, 99)                      # top centre of the third-place rosette, on the board's corner


def eruption(img, age):
    """The volcano foaming over: red foam wells up and runs down the cone over 0.6 s, then fizzes, with
    droplets popping off the top."""
    if age < 0:
        return
    step = min(12, int(age / 0.6 * 12))
    spr = A.eruption(step, int(age * 7) % 4)
    x0, y0 = VOLCANO_X - spr.width // 2, VOLCANO_Y - spr.height
    img.paste(spr, (x0, y0), spr)
    if step >= 4:
        d = ImageDraw.Draw(img)
        cx, cy = x0 + 14.5, y0 + A.ERUPT_UP - step / 12 * 3
        for k in range(3):                                                  # droplets popping off the top
            ph = (age * 1.6 + k / 3) % 1.0
            x, y = cx + (k - 1) * 4 * ph, cy - 2 - 8 * 4 * ph * (1 - ph)
            d.rectangle((round(x), round(y), round(x) + 1, round(y) + 1), fill=A.LAVA if k % 2 else A.LAVA_HI)


@span(BOARD_UP - 0.05, RESET)
def science_fair_board(c, L):
    """Bibi's science-fair trifold: it springs up on his desk on "poster", the volcano goes down on "kid" and
    foams over on "science", third place on "fair". It stays until the camera cuts in on Trump in line 4."""
    t = c.t
    yield "mid"
    board = A.trifold()
    p = (t - BOARD_UP) / 0.25
    rise = round((1 - back_out(p)) * (board.height + 2)) if p < 1 else 0
    paste(c.world, board, BOARD_X, BOARD_Y + rise, "mb")
    yield "front"
    t_kid, t_sci, t_fair = T(2, "kid"), T(2, "science"), T(2, "fair")
    if t >= t_kid:
        drop = round((1 - ease_out((t - t_kid) / 0.12)) * -8)
        paste(c.world, A.volcano(), VOLCANO_X, VOLCANO_Y + drop, "mb")
        eruption(c.world, t - t_sci)
    if t >= t_fair:
        k = back_out((t - t_fair) / 0.16)
        spr = A.rosette() if k >= 0.999 else scaled(A.rosette(), max(0.2, k))
        paste(c.world, spr, ROSETTE_XY[0], ROSETTE_XY[1] + A.rosette().height // 2, "mm")


@gag(SEC, 2)
def science_fair(c, L):
    """"You bring a poster to every speech like a kid at the science fair": Bibi proudly presents his
    trifold; its volcano foams over; it takes third place. The crowd chart stays up."""
    t = c.t
    flip(c, CROWD_FLIP)
    if BOARD_UP <= t < hit_t(L):
        pose(c, "bibi", arm="palm")
        face(c, "bibi", mouth="smile", brows="up", eyes="open")
    yield "chart"
    crowd_page(c, c.page)
    yield "mid"
    me_bar_wall(c)


# --- 3: grading the posters -------------------------------------------------------------------------------

GRADE_FLIP = live_from(3)
TUMBLE_SPEED = 110.0                        # across the empty dais, over the ledge from screen to screen


def poster_card(page, x, y, p, w=26, h=20):
    """A little poster outlined on the page as p goes 0 -> 1, with a red pin at the top."""
    stroke(page, [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], "black", p)
    if p >= 1:
        ImageDraw.Draw(page).rectangle((x + w // 2 - 1, y - 1, x + w // 2, y), fill=RED)


def map_doodle(page, cx, cy, p):
    """A map: a coastline, a dotted route and an X."""
    pts = [(cx + (8 + 3 * rnd("map", k)) * math.cos(k * 2 * math.pi / 14),
            cy + (5 + 2 * rnd("map-y", k)) * math.sin(k * 2 * math.pi / 14)) for k in range(15)]
    stroke(page, pts, "blue", p * 1.5)
    if p > 0.66:
        q = (p - 0.66) / 0.34
        d = ImageDraw.Draw(page)
        for k in range(int(q * 4)):
            d.point((cx - 5 + 2 * k, cy + 1 - k), fill=P.mk("black"))
        if q >= 1:
            stroke(page, [(cx + 2, cy - 4), (cx + 5, cy - 1)], "red")
            stroke(page, [(cx + 5, cy - 4), (cx + 2, cy - 1)], "red")


def grade_page(c, page):
    """BIBI'S POSTERS, graded: the cartoon bomb, a map, a pop quiz. Grade: a huge red F."""
    t = c.t
    page_title(page, "BIBI'S POSTERS", "black", age=t - GRADE_FLIP - 0.1)
    t_bomb, t_line, t_map, t_quiz = T(3, "cartoon"), T(3, "bomb"), T(3, "map"), T(3, "pop")
    t_grade, t_f = T(3, "Grade"), T(3, r"^F\.")
    if t >= t_bomb - 0.15:
        poster_card(page, 3, 13, (t - t_bomb + 0.15) / 0.2)
        bomb_doodle(page, 15, 25, 5, p=(t - t_bomb) / 0.35)
        if t >= t_line:
            stroke(page, [(6, 22), (25, 22)], "red", (t - t_line) / 0.15)
    if t >= t_map - 0.15:
        poster_card(page, 32, 13, (t - t_map + 0.15) / 0.2)
        map_doodle(page, 45, 23, (t - t_map) / 0.4)
    if t >= t_quiz - 0.15:
        poster_card(page, 61, 13, (t - t_quiz + 0.15) / 0.2)
        write(page, (74, 15), "QUIZ", "black", age=t - t_quiz, anchor="ma")
        for k in range(3):
            stroke(page, [(65, 25 + 3 * k), (83, 25 + 3 * k)], "blue", (t - t_quiz - 0.15 - 0.08 * k) / 0.1)
    if t >= t_grade:
        write(page, (6, 42), "GRADE:", "black", age=t - t_grade, bold=True)
    if t >= t_f:
        age = t - t_f
        for i, seg in enumerate(([(54, 35), (54, 55)], [(54, 35), (68, 35)], [(54, 45), (64, 45)])):
            stroke(page, seg, "red", age / 0.07 - i, width=3)
        ring(page, 61, 45, 14, 12, color="red", p=(age - 0.25) / 0.3)


@gag(SEC, 3)
def grade_f(c, L):
    """"A cartoon bomb, a map, a pop quiz. Grade: F. Nobody's there.": Bibi's three posters go up on the
    chart, one a word, and get a huge red F; on "Nobody's there" a tumbleweed rolls across the empty dais."""
    t = c.t
    flip(c, GRADE_FLIP)
    yield "back"
    age = t - (wt(L, "Nobody") - 0.1)
    x = DAIS_VIEW[0] - 13 + TUMBLE_SPEED * age
    if age >= 0 and x - 13 < DAIS_VIEW[2]:
        spr = A.tumbleweed(int(x / 6) % 8)
        hop = abs(math.sin(age * 7)) * 5
        paste_clipped(c.world, spr, x - spr.width // 2, LEDGE_TOP + 5 - spr.height - hop, DAIS_VIEW)
    yield "chart"
    grade_page(c, c.page)


# --- 4-5: the name on the wall and the gold T ---------------------------------------------------------------

LETTERS = list(zip("TRUMP", (T(4, "^my"), T(4, "name"), T(4, "^on"), T(4, "every"), T(4, "wall"))))
LETTER_X0, LETTER_Y = 233, 66               # the first letter's centre, the letters' top


@span(LETTERS[0][1] - 0.05, END)
def name_on_the_wall(c, L):
    """T-R-U-M-P in gold on the wall over Bibi's desk, slammed on one a word; it stays up."""
    t = c.t
    for _, tk in LETTERS:
        if 0 <= t - tk < 0.08:
            c.add_shake(3)
    yield "back"
    d = ImageDraw.Draw(c.world)
    for k, (ch, tk) in enumerate(LETTERS):
        age = t - tk
        if age < 0:
            continue
        spr = A.gold_letter(ch)
        x, y = LETTER_X0 + 17 * k, LETTER_Y + spr.height // 2
        if age < 0.08:
            spr = scaled(spr, 1 + 0.9 * (1 - age / 0.08))
        paste(c.world, spr, x, y, "mm")
        if 0.06 <= age < 0.2:                                              # impact ticks
            for sx in (-1, 1):
                for sy in (-1, 1):
                    d.line([(x + sx * 10, y + sy * 8), (x + sx * 12, y + sy * 10)], fill=INK)


T_GOLD = T(5, "gold")
FLIP_HALF = 0.08
EMBLEM_BOX = (142, 9, 179, 46)              # the emblem's disc in the backdrop (rows 9-45)
LAST_ROW = 44                               # the President's hair starts at y 45: draw nothing below this


@lru_cache(maxsize=1)
def clean_wall():
    """The gold wall behind the emblem, without the emblem."""
    img = Image.new("RGB", (W, H), C["wall"])
    hall.wall(img)
    return img.crop((EMBLEM_BOX[0] - 1, EMBLEM_BOX[1] - 1, EMBLEM_BOX[2] + 1, LAST_ROW + 1))


@lru_cache(maxsize=1)
def emblem_sprite():
    """The UN emblem cut out of the backdrop, as a round sprite."""
    img = hall.backdrop().crop(EMBLEM_BOX).convert("RGBA")
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, img.width - 1, img.height - 1), fill=255)
    img.putalpha(m)
    return img


def paste_disc(img, spr, sx=1.0):
    """Paste a disc sprite over the emblem's place, squashed to `sx` of its width, above the President."""
    if sx < 1:
        spr = spr.resize((max(1, round(spr.width * sx)), spr.height), Image.NEAREST)
    x = (EMBLEM_BOX[0] + EMBLEM_BOX[2]) // 2 - spr.width // 2
    spr = spr.crop((0, 0, spr.width, LAST_ROW + 1 - EMBLEM_BOX[1]))
    img.paste(spr, (x, EMBLEM_BOX[1]), spr)


def bulbs_lit(t):
    """Which marquee bulbs are on: chasing through line 5, flashing on "Not at all", then all on."""
    if t >= live_from(6):
        return -1
    if t >= T(5, r"^Not"):
        return -1 if int(t * 7) % 2 else -2
    return int(t * 9) % 3


@span(T_GOLD - 0.02, END)
def gold_t(c, L):
    """On "gold" the UN emblem over the dais flips over into a gold T in marquee bulbs; it stays."""
    t = c.t
    yield "back"
    age = t - T_GOLD
    c.world.paste(clean_wall(), (EMBLEM_BOX[0] - 1, EMBLEM_BOX[1] - 1))
    if age < FLIP_HALF:
        paste_disc(c.world, emblem_sprite(), 1 - age / FLIP_HALF)
    else:
        paste_disc(c.world, A.marquee_disc(lit=bulbs_lit(t)), min(1.0, (age - FLIP_HALF) / FLIP_HALF))


@gag(SEC, 4)
def so_secure(c, L):
    """"Insecure? Me?": a shrug, then the verse's one cut-in, on Trump's face; "I put my name on every wall":
    T-R-U-M-P slams onto the wall in gold, a letter a word (see name_on_the_wall)."""
    t = c.t
    if ZOOM_IN <= t < ZOOM_OUT:
        c.shot = "tight"
        face(c, "trump", eyes="wide", brows="up")
    if wt(L, "Insecure") - 0.05 <= t < ZOOM_IN:
        pose(c, "trump", arm="shrug", far="out")
    elif t >= wt(L, "put") - 0.1:
        pose(c, "trump", arm="point")
    if t < ZOOM_IN:
        flip(c, GRADE_FLIP)                                                  # the F page stays up till the cut
    yield "chart"
    if t < ZOOM_IN:
        grade_page(c, c.page)


@gag(SEC, 5)
def twenty_feet_high(c, L):
    """"In gold, twenty feet high. Insecure? Not at all.": the emblem flips into a gold T (see gold_t), a
    builder's dimension line measures it, 20 FT, and the bulbs flash."""
    t = c.t
    t_tw, t_feet, t_high, t_not = wt(L, "twenty"), wt(L, "feet"), wt(L, "high"), wt(L, r"^Not")
    if t_tw - 0.05 <= t < t_high + 0.45:
        pose(c, "trump", arm="up")
    yield "back"
    p = ramp(t, t_tw, t_high)
    if p > 0:
        x, y0, y1 = 184, EMBLEM_BOX[3] - 2, EMBLEM_BOX[1]
        top = lerp(y0, y1, ease_out(p))
        d = ImageDraw.Draw(c.world)
        d.line([(x - 2, y0), (x + 2, y0)], fill=INK)
        d.line([(x, y0), (x, top)], fill=INK)
        if p >= 1:
            d.line([(x - 2, y1), (x + 2, y1)], fill=INK)
            for yy, s in ((y0 - 1, -1), (y1 + 1, 1)):
                d.line([(x - 2, yy + 2 * s), (x, yy), (x + 2, yy + 2 * s)], fill=INK)
    if t >= t_feet:
        world_text(c.world, 200, 24, "20 FT", fill=C["white"])
    yield "mid"
    if t >= T_GOLD + 2 * FLIP_HALF:
        k = int(t * 7)
        for j in range(2 if t >= t_not else 1):
            a, r = rnd("glint", k, j) * 2 * math.pi, rnd("glint-r", k, j) * 13
            sparkle(c.world, 160 + r * math.cos(a), 27 + r * math.sin(a), 2, C["white"])
        if t >= t_not:
            lx = LETTER_X0 + 17 * int(rnd("lglint", k) * 5) + int(rnd("lglint-x", k) * 8) - 4
            sparkle(c.world, lx, LETTER_Y + 3 + int(rnd("lglint-y", k) * 10), 2, C["white"])


# --- 6-7: the trials ---------------------------------------------------------------------------------------

TRIAL_FLIP = live_from(6)
LINE_Y = 28                                 # the trial's timeline, 2020 to 2026


def snail(img, x, y, p=1.0, color="green"):
    """A marker snail heading right, its foot along y from x: a spiral shell and two eye stalks."""
    sx, sy = x + 7, y - 6
    shell = [(sx + (5.5 - 4.8 * k / 30) * math.cos(k * 2 * math.pi * 2.2 / 30 + math.pi / 2),
              sy + (5.5 - 4.8 * k / 30) * math.sin(k * 2 * math.pi * 2.2 / 30 + math.pi / 2)) for k in range(31)]
    foot = [(x, y), (x + 16, y), (x + 18, y - 3), (x + 17, y - 5)]
    segs = [foot, shell, [(x + 16, y - 4), (x + 15, y - 9)], [(x + 18, y - 4), (x + 20, y - 8)]]
    for i, seg in enumerate(segs):
        stroke(img, seg, color, p * len(segs) - i)


def battery(page, x, y, t):
    """A battery on its last bar, the bar blinking."""
    stroke(page, [(x, y), (x + 14, y), (x + 14, y + 7), (x, y + 7), (x, y)], "black")
    ImageDraw.Draw(page).rectangle((x + 15, y + 2, x + 16, y + 5), fill=P.mk("black"))
    if int(t * 3) % 2 == 0:
        ImageDraw.Draw(page).rectangle((x + 2, y + 2, x + 3, y + 5), fill=RED)


def trial_page(c, page):
    """BIBI'S TRIAL: 2020 to 2026, a snail inching along from the start, no verdict in sight, low energy."""
    t = c.t
    page_title(page, "BIBI'S TRIAL", "black", age=t - TRIAL_FLIP - 0.1, underline_color="red")
    t_yrs, t_trial, t_verd, t_low = T(6, "years"), T(6, "trial"), T(6, "verdict"), T(6, r"^Low")
    p = (t - t_yrs + 0.3) / 0.4
    stroke(page, [(6, LINE_Y), (84, LINE_Y)], "black", p)
    for k in range(7):
        if p * 7 > k:
            stroke(page, [(6 + 13 * k, LINE_Y - 2), (6 + 13 * k, LINE_Y + 2)], "black")
    if p >= 1:
        write(page, (2, LINE_Y + 5), "2020", "black")
        write(page, (89, LINE_Y + 5), "2026", "black", anchor="ra")
    if t >= t_trial - 0.1:
        x = 4 + int(max(0.0, t - t_trial - 0.4) / 0.8)                       # a pixel a beat, more or less
        snail(page, x, LINE_Y - 1, (t - t_trial + 0.1) / 0.35)
    if t >= t_verd - 0.15:
        q = (t - t_verd + 0.15) / 0.25
        stroke(page, [(84, LINE_Y), (84, LINE_Y - 13)], "black", q * 2)
        stroke(page, [(84, LINE_Y - 13), (77, LINE_Y - 11), (84, LINE_Y - 9)], "red", q * 2 - 1)
        write(page, (89, LINE_Y + 13), "VERDICT?", "red", age=t - t_verd, anchor="ra", bold=True)
    if t >= t_low:
        battery(page, 5, LINE_Y + 13, t)


def weeks_note(page, t):
    """Under Bibi's trial, Trump's own: MINE: 6 WKS, ticked."""
    t0 = T(7, "took")
    if t >= t0:
        write(page, (4, 51), "MINE: 6 WKS", "blue", age=t - t0, bold=True)
        check(page, 66, 54, "green", p=(t - t0 - 0.55) / 0.2)


@gag(SEC, 6)
def six_years_on_trial(c, L):
    """"Six years on trial, still no verdict? Low energy. Very slow.": a timeline from 2020 to 2026 with a
    snail inching along it, a VERDICT? flag at the far end and a battery on its last blinking bar."""
    flip(c, TRIAL_FLIP)
    yield "chart"
    trial_page(c, c.page)


LED_RED, LED_AMBER, LED_DIM = (255, 70, 60), (255, 190, 60), (40, 30, 26)


def scoreboard(c, img, box):
    """The left screen as a stadium scoreboard: GUILTY, 34 / 34 as the counts come in, PERFECT GAME!"""
    t = c.t
    x0, y0, x1, y1 = box
    screen_fill(img, box, (10, 8, 12))
    d = ImageDraw.Draw(img)
    for yy in range(y0 + 1, y1, 2):                                         # the unlit LED grid
        d.point([(xx, yy) for xx in range(x0 + 1, x1, 2)], fill=LED_DIM)
    cx = (x0 + x1) // 2
    pixel.text(img, (cx, y0 + 3), "GUILTY", PRESS, LED_RED, shadow=None, anchor="ma")
    t1, t_for, t2, t_perf = T(7, "thirty"), T(7, r"^for"), T(7, "thirty", 1), T(7, "Perfect")
    if t >= t1:
        pixel.text(img, (cx - 6, y0 + 14), "34", PRESS16, LED_AMBER, shadow=None, anchor="ra")
    if t >= t_for:
        pixel.text(img, (cx, y0 + 14), "/", PRESS16, LED_AMBER, shadow=None, anchor="ma")
    if t >= t2:
        pixel.text(img, (cx + 7, y0 + 14), "34", PRESS16, LED_AMBER, shadow=None, anchor="la")
    if t >= t_perf and int((t - t_perf) * 6) % 2 == 0:
        pixel.text(img, (cx, y0 + 36), "PERFECT GAME!", SILK, C["gold_hi"], shadow=None, anchor="ma")


def confetti_fall(img, t, t0, n=80):
    """Confetti let go at t0 over the whole hall, fluttering down."""
    d = ImageDraw.Draw(img)
    colors = (C["gold"], C["red"], C["blue"], C["white"], C["green"])
    for i in range(n):
        age = t - t0 - rnd("cf-d", i) * 0.5
        if age < 0:
            continue
        y = -3 + age * (34 + 22 * rnd("cf-v", i))
        if y > 160:
            continue
        x = rnd("cf-x", i) * W + math.sin(age * 5 + i) * 3
        if int(age * 8 + i) % 2:
            d.rectangle((x, y, x + 1, y), fill=colors[i % 5])
        else:
            d.point((x, y), fill=colors[i % 5])


@gag(SEC, 7)
def perfect_score(c, L):
    """"Mine took six weeks: thirty-four for thirty-four. Perfect score! Let's go!": MINE: 6 WKS goes under
    Bibi's snail; Trump's screen becomes a scoreboard, GUILTY 34/34, PERFECT GAME!; confetti, a stadium
    wave, and Trump celebrates with both fists up."""
    t = c.t
    t_34, t_perf, t_go = wt(L, "thirty"), wt(L, "Perfect"), wt(L, r"^go")
    flip(c, TRIAL_FLIP)
    if t >= t_34 - 0.05:
        c.screens["L"] = scoreboard
    if t_perf - 0.05 <= t < t_go - 0.05:
        pose(c, "trump", arm="fist")
    elif t >= t_go - 0.05:
        pose(c, "trump", arm="fist", far="up")
    for k, (_, _, i) in enumerate(ROW):                                      # the wave, left to right
        a = t - (t_perf + 0.055 * k)
        if 0 <= a < 0.45:
            c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), math.sin(math.pi * a / 0.45))
        if t >= t_go:
            c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), max(0.0, 1 - (t - t_go) / 0.9))
    yield "chart"
    trial_page(c, c.page)
    weeks_note(c.page, t)
    yield "front"
    if t >= t_perf:
        confetti_fall(c.world, t, t_perf)


# --- 8: the bottle deposits ----------------------------------------------------------------------------------

MACHINE_X, FLOOR_Y = 112, 153               # the bottle-return machine's left edge; the floor line for props
N_BOTTLES, BOTTLE_GAP, BOTTLE_FLIGHT = 8, 0.1, 0.22


def receipt(img, x, y, length):
    """A receipt spooling out of a slot at (x, y): down to the floor, then folding along it to the left."""
    if length <= 0:
        return
    d = ImageDraw.Draw(img)
    drop = min(length, FLOOR_Y - y)
    d.rectangle((x - 1, y, x + 5, y + drop), fill=INK)
    d.rectangle((x, y, x + 4, y + drop), fill=C["white"])
    run = length - drop
    if run > 0:
        pts = [(x + 2 - k, FLOOR_Y - 1 + (1 if (k // 6) % 2 else 0)) for k in range(int(run) + 1)]
        d.line(pts, fill=INK, width=5)
        d.line(pts, fill=C["white"], width=3)
    for k in range(2, int(min(drop, length)), 3):                            # the printing
        d.line([(x + 1, y + k), (x + 1 + (k * 7) % 3, y + k)], fill=(150, 150, 160))


@gag(SEC, 8)
def respect_the_hustle(c, L):
    """"Sara cashed the bottle deposits. Bibi, I respect the hustle.": a cart heaped with empties rolls in
    on its own to a bottle-return machine and feeds it, +10c a bottle, and a receipt spools out; Trump
    gives it a thumbs-up."""
    t = c.t
    t_dep, t_resp = wt(L, "deposits"), wt(L, "respect")
    flip(c, TRIAL_FLIP)
    if t >= t_resp - 0.05:
        pose(c, "trump", arm="thumb")
    yield "chart"
    trial_page(c, c.page)
    weeks_note(c.page, t)
    yield "mid"
    a = t - (L.t0 - 0.12)                                                   # the machine drops in and settles
    drop = -60 * (1 - ease_in(a / 0.15)) if a < 0.15 else -2 * math.sin(math.pi * (a - 0.15) / 0.12) if a < 0.27 else 0
    paste(c.world, A.machine(), MACHINE_X, FLOOR_Y + 1 + round(drop), "lb")
    cart = A.cart()
    p = ramp(t, L.t0 - 0.12, t_dep)
    x_stop = MACHINE_X - cart.width + 3
    x = lerp(-cart.width - 4, x_stop, ease_out(p))
    bump = round(math.sin(min(1.0, (t - t_dep) / 0.25) * math.pi) * -2) if t >= t_dep else 0
    paste(c.world, cart, int(x), FLOOR_Y + bump, "lb")
    hole = (MACHINE_X + 11, FLOOR_Y - 21)
    landed = None
    for k in range(N_BOTTLES):                                               # the bottles go in, one by one
        a = t - (t_dep + 0.05 + BOTTLE_GAP * k)
        if 0 <= a < BOTTLE_FLIGHT:
            q = a / BOTTLE_FLIGHT
            src = (x_stop + 12 + (k % 4) * 3, FLOOR_Y - 32)
            bx, by = lerp(src[0], hole[0], q), lerp(src[1], hole[1], q) - 12 * 4 * q * (1 - q)
            spr = A.bottle(k).rotate(-q * 270, resample=Image.NEAREST, expand=True)
            paste(c.world, spr, bx, by, "mm")
        elif a >= BOTTLE_FLIGHT:
            landed = a - BOTTLE_FLIGHT
    if landed is not None and landed < 0.45:                                 # +10c, one bottle at a time
        world_text(c.world, MACHINE_X + 13, FLOOR_Y - 49 - min(4, int(landed * 40)), "+10¢", fill=C["green"])
    receipt(c.world, MACHINE_X + 9, FLOOR_Y - 8, 60 * ramp(t, t_dep + 0.4, t_resp + 0.4))


# --- 9: the meme coin ---------------------------------------------------------------------------------------

COIN_FLIP = live_from(9)
PEAK = (60, 9)                              # where the coin's line tops out, on the chart


def coin_page(c, page):
    """$TRUMP: the line lies flat, goes to the moon on "made a fortune", and drops off the page on "never"."""
    t = c.t
    write(page, (4, 3), "$TRUMP", "green", age=t - COIN_FLIP - 0.1, bold=True)
    stroke(page, [(6, 12), (6, 50), (86, 50)], "black", (t - COIN_FLIP - 0.3) / 0.35)
    t_meme, t_made, t_fort, t_never = T(9, "meme"), T(9, "made"), T(9, "fortune"), T(9, "never")
    stroke(page, [(6, 46), (16, 45), (24, 46), (30, 45)], "green", (t - t_meme) / 0.3)
    if t >= t_made:
        stroke(page, [(30, 45), (38, 38), (43, 40), (52, 22), (56, 25), PEAK], "green", (t - t_made) / 0.35,
               width=2)
    if t >= t_fort:
        q = (t - t_fort) / 0.3
        ring(page, 80, 9, 5, color="black", p=q)                             # the moon, and a dotted way there
        ring(page, 82, 7, 4, color="black", p=q - 0.2)
        d = ImageDraw.Draw(page)
        for k in range(int(clamp(q, 0, 1) * 4)):
            d.point((PEAK[0] + 4 + 4 * k, PEAK[1] - 1), fill=P.mk("black"))
    if t >= t_never:
        stroke(page, [PEAK, (61, 30), (63, 58)], "red", (t - t_never) / 0.18, width=2)


def coin_rain(c, t0, t1, n=24):
    """$TRUMP coins raining down between t0 and t1, bouncing and piling up on the rostrum's corners (the
    middle stays clear for the folded arms)."""
    out = []
    for i in range(n):
        ts = t0 + (t1 - t0) * i / n + rnd("cr-t", i) * 0.08
        age = c.t - ts
        if age < 0:
            continue
        x = (142 if i % 2 else 173) + rnd("cr-x", i) * 6
        land = hall.ROSTRUM_TOP - 4 * ((i // 2) % 3 == 2)
        fall = math.sqrt(2 * (land + 8) / 620.0)
        if age < fall:
            y, frame = -8 + 310 * age * age, int(age * 18 + i) % 4
        else:
            hop = age - fall
            y = land - (5 * math.sin(math.pi * hop / 0.16) if hop < 0.16 else 0)
            frame = 0 if hop >= 0.16 else 1
        out.append((A.coin(frame), x, y))
    return out


@gag(SEC, 9)
def meme_coin(c, L):
    """"I sold a meme coin, made a fortune, never had to lift a muscle.": the chart goes to the moon on
    "fortune" while coins rain onto the rostrum; Trump folds his arms on "never" and lets them pile up (and
    on the chart, behind him, the line drops off the page)."""
    t = c.t
    t_coin, t_never = wt(L, "coin"), wt(L, "never")
    flip(c, COIN_FLIP)
    if t >= t_never - 0.08:
        pose(c, "trump", arm="cross")
        face(c, "trump", eyes="half")
    yield "chart"
    coin_page(c, c.page)
    yield "mid"
    for spr, x, y in coin_rain(c, t_coin - 0.1, t_never + 0.3):
        paste(c.world, spr, x, y, "mb")


# --- 10: you're fired ----------------------------------------------------------------------------------------

FIRE_T = T(10, r"^fired")
SEAT_X = 270                                # the ejector seat, under Bibi
NAMEPLATE_TOP = 130                         # the ISRAEL nameplate's top edge, for Kilroy's fingers


def bibi_flight(t):
    """Bibi's feet (y) through line 10: shot up on "fired!", down again on "stay fired" (behind the desk),
    then peeking over the desk edge and pulling himself back up on "crawl back"."""
    t_stay, t_land, t_always, t_crawl, t_back = (T(10, r"^stay"), T(10, "fired", 1), T(10, "always"),
                                                  T(10, "crawl"), T(10, "back"))
    home, gone, peek = 176, 232, 193                     # peek: eyes just over the nameplate
    if t < FIRE_T:
        return home
    if t < t_stay:
        return home - 280 * ease_out((t - FIRE_T) / 0.32)
    if t < t_land:
        return lerp(home - 280, gone, ease_in((t - t_stay) / (t_land - t_stay)))
    if t < t_always:
        return gone
    if t < t_crawl:
        return lerp(gone, peek, ease_out((t - t_always) / (t_crawl - t_always)))
    return lerp(peek, home, ease_in_out((t - t_crawl) / (t_back + 0.04 - t_crawl)))


def spring(img, x, y_top, y_bottom=150, coils=5, width=14):
    """A big coil spring from y_bottom up to y_top, with a chair seat on top."""
    if y_top >= y_bottom - 2:
        return
    n = coils * 2
    pts = [(x + (width / 2 if k % 2 else -width / 2) if 0 < k < n else x, lerp(y_bottom, y_top, k / n))
           for k in range(n + 1)]
    d = ImageDraw.Draw(img)
    d.line(pts, fill=INK, width=3)
    d.line(pts, fill=C["steel"], width=1)
    d.rectangle((x - 13, y_top - 5, x + 13, y_top), fill=INK)
    d.rectangle((x - 12, y_top - 4, x + 12, y_top - 1), fill=C["chair"])
    d.line([(x - 12, y_top - 4), (x + 12, y_top - 4)], fill=mix(C["chair"], C["white"], 0.4))


def seat_top(t):
    """The ejector seat's top: up on "fired!", boinging, then back down out of sight."""
    a = t - FIRE_T
    if a < 0:
        return 160
    up = 112
    if a < 0.09:
        return lerp(150, up, back_out(a / 0.09))
    if a < 0.9:
        return up + 6 * math.sin((a - 0.09) * 26) * max(0.0, 1 - (a - 0.09) / 0.8)
    return lerp(up, 160, ease_in((a - 0.9) / 0.35))


def bibi_feed(c, img, box):
    """Bibi's live feed, his face following him out of the top of the frame and back up from the bottom."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    dy = round(c.st["bibi"]["y"] - 176)
    feed = V.feed_backdrop(w, h, False).copy()
    if abs(dy) < h:
        b = scaled(V.bust(c, "bibi", w // 2, h // 2, -1), 2)
        feed.paste(b, ((w - b.width) // 2, h - b.height + dy), b)
    d = ImageDraw.Draw(feed)
    tw = pixel.text_width(V.NAME["bibi"], SILK)
    d.rectangle((1, h - 11, tw + 8, h - 2), fill=INK)
    d.rectangle((2, h - 10, tw + 7, h - 3), fill=C["white"])
    d.rectangle((2, h - 10, 3, h - 3), fill=V.TAG_COLOR["bibi"])
    pixel.text(feed, (6, h - 12), V.NAME["bibi"], SILK, INK, shadow=None)
    if int(c.t * 2) % 2 == 0:
        d.ellipse((3, 3, 6, 6), fill=C["red"])
    pixel.text(feed, (9, 1), "LIVE", SILK, C["white"], shadow=(0, 0, 0))
    img.paste(feed, (x0, y0))


@gag(SEC, 10)
def youre_fired(c, L):
    """"Bibi, you're fired!": Bibi's chair turns out to be an ejector seat and fires him out of the top of
    the picture. "But you never stay fired": he drops back down behind the desk. "You always crawl back":
    fingers over the nameplate, a peek over it, and he hauls himself back into his seat, seeing stars."""
    t = c.t
    t_bibi, t_you, t_crawl, t_back = wt(L, r"^Bibi"), wt(L, r"^you$", 1), wt(L, "crawl"), wt(L, "back")
    flip(c, L.t0)                                                            # back to the cover sheet
    if t_bibi - 0.05 <= t < FIRE_T + 0.6:
        pose(c, "trump", arm="point")
    s = c.st["bibi"]
    s["y"] = bibi_flight(t)
    if FIRE_T - 0.05 <= t < t_back + 0.04:
        c.hit_react["bibi"] = False
        c.screens["R"] = bibi_feed
        if t < t_you:
            pose(c, "bibi", arm="up", far="up")
            s.update(eyes="wide", mouth="o", brows="worried")
        else:
            pose(c, "bibi", arm="down", far="down")
            s.update(eyes="open", mouth="frown", brows="worried", dizzy=t >= t_crawl)
    yield "chart"
    V.default_page(c, c.page)
    yield "mid"
    spring(c.world, SEAT_X, seat_top(t))
    if t >= FIRE_T:
        a = t - FIRE_T
        if a < 0.35:                                                         # the launch's speed lines
            d = ImageDraw.Draw(c.world)
            for k in range(4):
                lx, ly = SEAT_X - 9 + 6 * k, 140 - 3 * (k % 3)
                d.line([(lx, ly), (lx, ly - 22)], fill=C["white"])
    t_land = T(10, "fired", 1)
    P.puff(c.world, SEAT_X, 140, t - t_land, size=1.3, seed=10, color=(232, 222, 200), drift=(0, -10), life=0.8)
    if 0 <= t - t_land < 0.12:
        c.add_shake(4)
    yield "front"
    if t_you <= t < t_back:                                                   # hanging on to the nameplate
        for hx in (259, 281):
            paste(c.world, A.fingers(), hx, NAMEPLATE_TOP + 3, "mb")


# --- 11: pull it ---------------------------------------------------------------------------------------------


def taffy(img, root, tip, width0=6, width1=3, sag=4):
    """A strand of hair pulled out like taffy from `root` to `tip`: thick at the root, sagging a little."""
    n = 14
    mx, my = (root[0] + tip[0]) / 2, (root[1] + tip[1]) / 2 + sag
    pts = []
    for k in range(n + 1):
        u = k / n
        pts.append(((1 - u) ** 2 * root[0] + 2 * u * (1 - u) * mx + u * u * tip[0],
                    (1 - u) ** 2 * root[1] + 2 * u * (1 - u) * my + u * u * tip[1]))
    d = ImageDraw.Draw(img)
    for k in range(n):
        w = lerp(width0, width1, k / n)
        d.line([pts[k], pts[k + 1]], fill=INK, width=round(w) + 2)
    for k in range(n):
        w = lerp(width0, width1, k / n)
        d.line([pts[k], pts[k + 1]], fill=C["thair"], width=round(w))
    d.line([(p[0], p[1] - lerp(width0, width1, i / n) / 2 + 0.5) for i, p in enumerate(pts)], fill=C["thair_hi"])


def grabber(img, hand, tip, closed):
    """A reacher-grabber: a steel pole from Bibi's hand to a two-jawed red claw at `tip`."""
    d = ImageDraw.Draw(img)
    d.line([hand, tip], fill=INK, width=4)
    d.line([hand, tip], fill=C["steel"], width=2)
    ang = math.atan2(tip[1] - hand[1], tip[0] - hand[0])
    spread = 0.22 if closed else 0.75
    for s in (-1, 1):
        a = ang + s * spread
        j = (tip[0] + 6 * math.cos(a), tip[1] + 6 * math.sin(a))
        d.line([tip, j], fill=INK, width=4)
        d.line([tip, j], fill=C["red"], width=2)
    d.rectangle((hand[0] - 2, hand[1] - 2, hand[0] + 2, hand[1] + 2), fill=INK)
    d.rectangle((hand[0] - 1, hand[1] - 1, hand[0] + 1, hand[1] + 1), fill=C["red"])


def along(a, b, length):
    """The point `length` pixels from a toward b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    dist = math.hypot(dx, dy) or 1.0
    return a[0] + dx * length / dist, a[1] + dy * length / dist


def wobble_back(a):
    """A strand snapping back: 1 at a=0, then a decaying swing about 0."""
    return math.cos(a * 30) * max(0.0, 1 - a / 0.4)


def anchor_xy(c, who, key, off=(0, 0)):
    """An anchor (as drawn this frame) plus an offset."""
    x, y = c.anchor[who][key]
    return x + off[0], y + off[1]


def hair_page(page, t, t_not, t_real, t_fact):
    """MY HAIR: stamped CERTIFIED REAL on "real" (it slams down), and ticked on "fact"."""
    page_title(page, "MY HAIR", "black", age=t - t_not)
    if t >= t_real:
        k = clamp((t - t_real) / 0.08, 0, 1)
        spr = A.seal(-6)
        paste(page, spr if k >= 1 else scaled(spr, 1.5 - 0.5 * k), page.width // 2, 37, "mm")
    if t >= t_fact - 0.05:
        check(page, 70, 6, "green", p=(t - t_fact + 0.05) / 0.15, width=2, size=11)


@gag(SEC, 11)
def pull_it(c, L):
    """"Like a bad toupee": Bibi gets out a grabber and snaps it at Trump's hair. "Not mine, it's real. Go
    on, pull it.": it reaches over and pulls; the hair stretches like taffy. "Ow!": it snaps back, and so
    does the grabber, into Bibi's face. Meanwhile Trump's chart says MY HAIR, stamped CERTIFIED REAL on "real"
    and ticked on "fact"."""
    t = c.t
    t_toupee, t_not, t_real, t_go = wt(L, "bad"), wt(L, r"^Not"), wt(L, "real"), wt(L, r"^Go$")
    t_pull, t_ow, t_fact = wt(L, r"^pull"), wt(L, r"^Ow"), wt(L, "fact")
    t_bonk = t_ow + 0.12
    tr, bb = c.st["trump"], c.st["bibi"]
    flip(c, t_not - 0.1)
    if t < T(10, "back") + 0.6:
        bb["dizzy"] = True                                                   # still seeing stars from line 10
    holding = t_toupee - 0.1 <= t < t_bonk + 0.25
    if holding:
        pose(c, "bibi", arm="point")
        face(c, "bibi", eyes="half", mouth="smirk", brows="angry")
    if t_bonk <= t < t_bonk + 0.35:
        bb.update(eyes="x", mouth="wide", brows="worried")
    if t >= t_bonk:
        bb["dizzy"] = True
    if t_not - 0.05 <= t < t_real + 0.35:
        pose(c, "trump", arm="up")
    elif t_go - 0.05 <= t < t_pull:
        pose(c, "trump", arm="palm")
    elif t_pull <= t < t_ow:
        pose(c, "trump", arm="down")
        tr.update(eyes="shut", brows="worried", lean=round(4 * ease_out((t - t_pull) / 0.5)))
    elif t_ow <= t < t_ow + 0.45:
        tr.update(eyes="wide", brows="worried", mouth="wide", lean=round(4 * wobble_back(t - t_ow)))
    elif t >= t_fact - 0.1:
        pose(c, "trump", arm="up")
    yield "chart"
    if t >= t_not - 0.1:
        hair_page(c.page, t, t_not, t_real, t_fact)
    else:
        V.default_page(c, c.page)
    yield "front"
    root = anchor_xy(c, "trump", "top", (7, 2))
    hand = c.anchor["bibi"]["hand"]
    head = c.anchor["bibi"]["head"]
    if holding:
        reach = math.hypot(root[0] - hand[0], root[1] - hand[1])
        if t < t_go:
            tip = along(hand, root, 22)
            closed = t_toupee + 0.1 <= t < t_toupee + 0.5 and int((t - t_toupee) * 8) % 2 == 0
        elif t < t_pull:
            tip = along(hand, root, lerp(22, reach, ease_out((t - t_go) / (t_pull - t_go - 0.05))))
            closed = False
        elif t < t_ow:
            k = ease_out((t - t_pull - 0.06) / 0.6) if t >= t_pull + 0.06 else 0.0
            tip = along(hand, root, reach * (1 - 0.35 * k))
            closed = True
            taffy(c.world, root, tip)
        else:
            k = ease_in(clamp((t - t_ow) / 0.12, 0, 1))
            pulled = along(hand, root, reach * 0.65)
            tip = (lerp(pulled[0], head[0] - 5, k), lerp(pulled[1], head[1] + 2, k))
            closed = False
            if t < t_ow + 0.06:
                back = (t - t_ow) / 0.06
                taffy(c.world, root, (lerp(pulled[0], root[0], back), lerp(pulled[1], root[1], back)))
        grabber(c.world, hand, tip, closed)
    if t_bonk <= t < t_bonk + 0.12:
        P.burst(c.world, head[0] - 6, head[1], 3, 7, C["white"], spikes=6)
    if t_real <= t < t_real + 0.4:
        k = int((t - t_real) * 12)
        sparkle(c.world, root[0] - 4 + (k * 5) % 10, root[1] - 1 + (k * 3) % 4, 2, C["white"])
    yield "ui"
    if t_ow <= t < t_ow + 0.6:
        pop_text(c.ui, 132, 68, "OW!", t - t_ow, PRESS16, top=C["red_hi"], bottom=C["red"])

