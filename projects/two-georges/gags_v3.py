"""Verse 3: the King hits back (lines v3 0-14).

The Continental dollar crashes and British forgers snow it over Boston; Fort
Washington rises out of the sea and surrenders by teatime; Benedict Arnold
flips his coat and rows over to the other George; Parson Weems's book grows a
cherry tree; sixty years of reign against eight; a mocking bow. Then the verse
turns to Harry Washington, the "property" Washington asked for back, and the
teeth: those lines are played straight, in a dimmed world, with documents.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import video as V
from characters import rim_light
from gagkit import (C, FEET_Y, GEORGE_X, INK, PRESS, PRESS16, SILK, W, WASH_X, Canvas, anchor, back_out, clamp,
                    big_text, bubble, cherry_tree, crown_sprite, debris, dither, ease_in, ease_in_out, ease_out,
                    arrow, face, figure, flag_cloth, fly, gag, label, lerp, line_t, mask, mirror, pan,
                    parchment, paste, paste_rot, pop_dy, ramp, rnd, splash, stamp, teacup,
                    text_width, typed, ui_at, waving, white_flag, wt)

RED, NAVY, GOLD, WHITE = C["red"], C["navy"], C["gold"], C["white"]
GREENBACK = (122, 138, 112)            # the engraved border of a Continental note
MOOD = 0.6                             # how dark the sober lines go


# --- shared helpers ---------------------------------------------------------------------------

def set_shot(c, shot):
    """Take the camera, except while the listener reels from a big hit (see video.reaction)."""
    r = V.reaction(c)
    c.shot = r[0] if r else shot


def sober(c, L, level=MOOD, fade=0.5, start=None):
    """Dim the world, and give Washington a restrained reaction instead of the comic flinch."""
    a = L.t0 - 0.15 if start is None else start
    c.mood = max(c.mood, level * ease_in_out(ramp(c.t, a, a + fade)))
    c.hit_react["washington"] = False
    c.hitfx = False
    w = c.st["washington"]
    w.update(arm="down", mouth="closed", brows="neutral", sweat=False)
    w["eyes"] = "shut" if (c.t - L.t0) % 5.0 > 1.2 else "open"


def keep_in(x, s, fnt=SILK, margin=3):
    """Clamp the centre x of a label so the whole plate stays on screen."""
    half = text_width(s, fnt) // 2 + 4
    return int(clamp(x, half + margin, W - half - margin))


def tag_over(c, x, y, s, age, bg=C["paper"], fg=INK, anchor_="mb"):
    """A small label over a world point, drawn on the UI (so it stays crisp when zoomed)."""
    if age < 0:
        return
    ux, uy = ui_at(c, x, y)
    label(c.ui, (keep_in(ux, s), uy + (pop_dy(age, drop=5) or 0)), s, bg=bg, fg=fg, anchor=anchor_)


def sink_draw(img, spr, x, waterline, rise, t, seed=0):
    """Paste a sprite standing in the sea with its base `rise` pixels above its fully sunk position:
    only the part above the waterline shows, with foam where it meets the water."""
    h = spr.height
    top = waterline - int(round(rise * h))
    vis = waterline - top
    if vis <= 0:
        return
    part = spr.crop((0, 0, spr.width, min(h, vis)))
    img.paste(part, (int(x - spr.width // 2), top), part)
    d = ImageDraw.Draw(img)
    for xx in range(int(x - spr.width // 2) - 2, int(x + spr.width // 2) + 3):
        if (xx // 2 + int(t * 4) + seed) % 3 != 2:
            d.point((xx, waterline), fill=WHITE)


# --- props --------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def banknote():
    """A Continental dollar: a small engraved note with a round seal."""
    s = Canvas(22, 14)
    s.rect((1, 1, 20, 12), "paper")
    s.rect((2, 2, 19, 11), GREENBACK)
    s.rect((3, 3, 18, 10), "paper")
    s.ell((4, 4, 9, 9), GREENBACK)
    s.px((6, 6), "ink")
    s.line([(11, 5), (17, 5)], (96, 96, 84))
    s.line([(11, 8), (15, 8)], (96, 96, 84))
    return s.done()


@lru_cache(maxsize=None)
def note_bundle():
    """A brick of freshly printed notes, tied with string."""
    s = Canvas(24, 12)
    for i in range(3):
        s.rect((1 + i, 5 - 2 * i, 20 + i, 10 - 2 * i), "paper")
        s.line([(1 + i, 10 - 2 * i), (20 + i, 10 - 2 * i)], GREENBACK)
    s.line([(12, 1), (12, 10)], "wax")
    s.ell((6, 2, 9, 4), GREENBACK)
    return s.done()


@lru_cache(maxsize=None)
def press_sprite(frame):
    """A wooden screw press, printing: the platen comes down on frames 2 and 3."""
    s = Canvas(28, 34)
    down = (0, 1, 3, 1)[frame % 4]
    s.rect((3, 2, 6, 31), "wood"); s.rect((21, 2, 24, 31), "wood")
    s.line([(3, 2), (3, 31)], "wood_hi"); s.line([(24, 2), (24, 31)], "wood_sh")
    s.rect((2, 2, 25, 6), "wood_sh"); s.line([(2, 2), (25, 2)], "wood_hi")
    s.rect((13, 6, 14, 12 + down), "iron")
    ang = (-0.6, 0.2, 0.9, 0.2)[frame % 4]
    s.line([(14, 9), (14 + int(9 * math.cos(ang)), 9 + int(6 * math.sin(ang)))], "iron_hi")
    s.rect((8, 13 + down, 19, 15 + down), "iron"); s.line([(8, 13 + down), (19, 13 + down)], "iron_hi")
    s.rect((1, 19, 26, 21), "wood_hi"); s.line([(1, 21), (26, 21)], "wood_sh")
    s.rect((8, 17, 19, 18), "paper")
    s.rect((7, 22, 20, 30), "wood_sh")
    s.rect((1, 31, 8, 32), "wood_sh"); s.rect((19, 31, 26, 32), "wood_sh")
    return s.done()


@lru_cache(maxsize=None)
def fort_sprite():
    """Fort Washington as an island: a rocky knoll under a sloped earthwork with pointed bastions,
    a stockade along the top and guns in the embrasures."""
    s = Canvas(66, 34)
    rock, rock_sh, grass = (112, 104, 116), (78, 72, 90), (92, 124, 78)
    s.ell((1, 20, 64, 46), rock_sh)
    s.ell((4, 19, 60, 40), rock)
    s.ell((6, 17, 58, 30), grass)
    earth, earth_hi, earth_sh = (150, 122, 80), (184, 156, 104), (112, 88, 64)
    s.poly([(4, 24), (10, 13), (56, 13), (62, 24)], earth)            # the glacis, bastions at the ends
    s.poly([(4, 24), (10, 13), (14, 13), (10, 24)], earth_sh)
    s.poly([(56, 13), (62, 24), (58, 24), (54, 13)], earth_hi)
    s.line([(10, 13), (56, 13)], earth_hi)
    s.line([(4, 24), (62, 24)], earth_sh)
    for x in range(12, 55, 3):                                        # the stockade
        s.line([(x, 6), (x, 12)], "wood")
        s.px((x, 5), "wood_hi")
        s.px((x + 1, 12), "wood_sh")
    s.line([(11, 10), (55, 10)], "wood_sh")
    for x in (17, 29, 41, 50):                                        # guns in the embrasures
        s.rect((x, 15, x + 3, 17), "iron")
        s.px((x, 15), "iron_hi")
    s.rect((32, 18, 36, 23), "wood_deep")                             # the sally port
    s.line([(32, 18), (36, 18)], "wood_sh")
    return s.done()


@lru_cache(maxsize=None)
def rowboat_small():
    s = Canvas(30, 10)
    s.poly([(1, 1), (28, 1), (25, 8), (4, 8)], "wood")
    s.line([(1, 1), (28, 1)], "wood_hi")
    s.line([(3, 4), (26, 4)], "wood_sh")
    s.line([(4, 8), (25, 8)], "wood_deep")
    return s.done()


ARNOLD_HAIR = {(214, 214, 224): (124, 82, 56), (168, 168, 186): (90, 56, 44)}
TURNCOAT = {(38, 58, 122): (186, 36, 46), (24, 36, 82): (124, 22, 36), (70, 96, 168): (222, 70, 72)}


@lru_cache(maxsize=None)
def arnold_sprite(facing, red, **pose):
    """Benedict Arnold: Washington's figure with dark hair, in Continental blue or British red."""
    img, _ = figure("washington", 1, **pose)
    a = np.array(img)
    swaps = dict(ARNOLD_HAIR)
    if red:
        swaps.update(TURNCOAT)
    for src, dst in swaps.items():
        m = np.all(a[..., :3] == src, axis=-1) & (a[..., 3] > 0)
        a[m, :3] = dst
    img = rim_light(Image.fromarray(a), 1, amount=0.3)
    return mirror(img) if facing < 0 else img


def draw_arnold(img, x, feet_y, facing, red, squash=1.0, **pose):
    spr = arnold_sprite(facing, red, **pose)
    if squash < 0.999:
        w = max(1, int(round(spr.width * squash)))
        spr = spr.resize((w, spr.height), Image.NEAREST)
    img.paste(spr, (int(round(x - spr.width / 2)), int(round(feet_y - 52))), spr)


@lru_cache(maxsize=None)
def book_cover():
    """Weems's 'Life of Washington', leather-bound, with room at the foot for the 1806 selling point."""
    s = Canvas(64, 76)
    s.rect((3, 1, 62, 74), (118, 48, 42))
    s.rect((1, 1, 5, 74), (86, 34, 34))
    s.rect((7, 3, 59, 72), (136, 58, 48))
    s.line([(9, 3), (59, 3)], "gold_sh"); s.line([(9, 72), (59, 72)], "gold_sh")
    for txt, y in (("THE LIFE", 5), ("OF", 13), ("WASHINGTON", 21)):
        s.text((33, y), txt, "gold", anchor="ma")
    s.line([(16, 31), (50, 31)], "gold_sh")
    s.text((33, 33), "M.L. WEEMS", "gold_hi", anchor="ma")
    s.text((33, 41), "1806 ED.", "paper_sh", anchor="ma")
    s.ell((28, 56, 38, 64), "gold_sh")                           # a tooled rosette
    s.px((33, 60), "gold_hi")
    return s.done()


@lru_cache(maxsize=None)
def book_floating():
    """The same book, closed and small, for the sea."""
    s = Canvas(22, 10)
    s.rect((1, 2, 20, 8), (118, 48, 42)); s.rect((1, 1, 20, 2), "paper")
    s.line([(4, 5), (17, 5)], "gold_sh")
    return s.done()


@lru_cache(maxsize=None)
def sticker():
    """A starburst sticker: NOW WITH CHERRY TREE!"""
    im = Image.new("RGBA", (56, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    pts = []
    for i in range(24):
        a = i * math.pi / 12
        r = (27, 23)[i % 2], (17, 14)[i % 2]
        pts.append((28 + math.cos(a) * r[0], 18 + math.sin(a) * r[1]))
    d.polygon(pts, fill=C["gold"] + (255,), outline=INK + (255,))
    for j, s in enumerate(("NOW WITH", "CHERRY", "TREE!")):
        d.text((28, 6 + j * 8), s, font=SILK, fill=C["red_sh"] + (255,), anchor="ma")
    return im


@lru_cache(maxsize=None)
def tree_sprite(fallen=False):
    t = cherry_tree()
    return t.rotate(80, resample=Image.NEAREST, expand=True) if fallen else t


@lru_cache(maxsize=None)
def column(h, who):
    """A column of years rising out of the sea, in the King's red or the General's blue, with a band
    for every decade."""
    body, shade, hi, cap = (("red", "red_sh", "red_hi", "gold") if who == "george" else
                            ("navy", "navy_sh", "navy_hi", "buff"))
    s = Canvas(24, h + 6)
    s.rect((3, 4, 20, h + 4), body)
    s.rect((3, 4, 6, h + 4), shade)
    s.line([(17, 5), (17, h + 4)], hi)
    for y in range(h + 4 - 16, 5, -16):
        s.line([(3, y), (20, y)], cap)
    s.rect((1, 1, 22, 4), cap)
    s.line([(1, 4), (22, 4)], "ink")
    return s.done()


@lru_cache(maxsize=None)
def plow_sprite():
    """A farmer's plough: two handles, a long beam, and the iron share and mouldboard."""
    s = Canvas(36, 20)
    s.line([(2, 2), (16, 15)], "wood_sh", 2)                       # the far handle
    s.line([(5, 1), (19, 14)], "wood", 2)                          # the near handle
    s.line([(12, 11), (34, 11)], "wood", 2)                        # the beam
    s.line([(12, 10), (34, 10)], "wood_hi")
    s.poly([(15, 12), (24, 12), (28, 18), (13, 18)], "iron")       # the mouldboard and share
    s.line([(15, 12), (24, 12)], "iron_hi")
    s.poly([(24, 16), (31, 18), (24, 18)], "steel")
    s.rect((33, 9, 34, 13), "iron")                                # the hitch
    return s.done()


@lru_cache(maxsize=None)
def falling_crown():
    return crown_sprite()


@lru_cache(maxsize=None)
def transport_ship():
    """A three-masted transport under full sail, bow to the right, sailing east."""
    s = Canvas(40, 32)
    hull, sail, sail_lit = (56, 40, 60), (222, 206, 200), (255, 232, 190)
    s.poly([(3, 23), (37, 23), (33, 29), (7, 29)], hull)
    s.line([(5, 25), (35, 25)], (120, 84, 70))
    for x, top in ((10, 5), (19, 2), (28, 5)):
        s.line([(x, top), (x, 23)], hull)
    for x, top, w in ((10, 7, 7), (19, 4, 8), (28, 7, 7)):
        s.poly([(x - w // 2 - 1, top), (x + w // 2 + 1, top), (x + w // 2 + 2, top + 7), (x - w // 2, top + 7)], sail)
        s.poly([(x - w // 2, top + 9), (x + w // 2 + 2, top + 9), (x + w // 2 + 2, top + 15), (x - w // 2, top + 15)], sail)
        s.line([(x + w // 2 + 1, top), (x + w // 2 + 2, top + 15)], sail_lit)
    s.poly([(28, 12), (37, 22), (28, 22)], sail)
    return s.done((40, 26, 52))


@lru_cache(maxsize=None)
def dentures(wood=True, gap=2):
    """A set of false teeth, front on and chattering: a row of big teeth under the top gum and over
    the bottom one, wooden (the folklore) or ivory (the fact)."""
    s = Canvas(32, 22 + gap)
    gum, gum_sh, gum_hi = (214, 118, 130), (164, 76, 96), (238, 156, 164)
    tooth, edge = (("wood_hi", "wood") if wood else ((244, 238, 218), (196, 184, 160)))
    s.rect((2, 1, 29, 5), gum); s.line([(3, 1), (28, 1)], gum_hi)
    s.rect((4, 6, 27, 14 + gap), "mouth")
    for i, x in enumerate(range(4, 27, 4)):
        s.rect((x, 6, x + 2, 10), tooth); s.px((x + 2, 10), edge)
        s.rect((x, 11 + gap, x + 2, 14 + gap), tooth); s.px((x, 11 + gap), edge)
        if wood:
            s.px((x + 1, 8), "wood"); s.px((x + 1, 13 + gap), "wood")
    s.rect((2, 15 + gap, 29, 19 + gap), gum_sh); s.line([(3, 19 + gap), (28, 19 + gap)], "wood_deep")
    return s.done()


@lru_cache(maxsize=None)
def hippo(mouth):
    """A hippopotamus surfacing, seen from the front: 0 closed, 1 open showing its ivory."""
    s = Canvas(36, 30)
    body, shade, pink = (132, 112, 146), (100, 84, 116), (220, 128, 146)
    s.ell((6, 1, 12, 7), shade); s.ell((24, 1, 30, 7), shade)
    s.ell((7, 2, 11, 6), pink); s.ell((25, 2, 29, 6), pink)
    s.ell((5, 3, 31, 18), body)
    s.ell((9, 4, 14, 9), "white"); s.ell((22, 4, 27, 9), "white")
    s.px((12, 6), "eye"); s.px((24, 6), "eye")
    if mouth:
        s.ell((3, 12, 33, 22), body)
        s.rect((6, 17, 30, 27), pink)
        s.ell((3, 23, 33, 29), shade)
        for x in (8, 26):
            s.rect((x, 16, x + 2, 21), "white")
        for x in (9, 25):
            s.rect((x, 23, x + 2, 27), "white"); s.px((x + 1, 22), "white")
    else:
        s.ell((2, 11, 34, 28), body)
        s.line([(8, 23), (28, 23)], shade)
    s.ell((11, 13, 15, 16), shade); s.ell((21, 13, 25, 16), shade)
    return s.done()


@lru_cache(maxsize=None)
def hippo_ears():
    """Just the ears and eyes above the water, for the wreckage that follows."""
    s = Canvas(24, 8)
    body, shade, pink = (132, 112, 146), (100, 84, 116), (220, 128, 146)
    s.ell((1, 1, 6, 6), shade); s.ell((17, 1, 22, 6), shade)
    s.px((3, 3), pink); s.px((19, 3), pink)
    s.ell((4, 3, 19, 7), body)
    s.px((8, 4), "eye"); s.px((15, 4), "eye")
    return s.done()


# --- 0: "Currency"? Your money crashed so hard it's a phrase ------------------------------------

CHART = (112, 56, 208, 98)


def chart_line(p, crash):
    """Value of the Continental dollar as a polyline: a slow slide, then the crash through the frame."""
    x0, y0, x1, y1 = CHART
    w, h = x1 - x0, y1 - y0
    pts = [(x0 + 5 + w * f, y0 + 12 + h * g) for f, g in
           ((0, 0), (0.1, -0.03), (0.2, 0.06), (0.3, 0.04), (0.42, 0.14), (0.52, 0.12), (0.62, 0.22))]
    ex, ey = pts[-1]
    if crash > 0:
        pts.append((ex + 6 * crash, ey + (y1 + 14 - ey) * crash))
    n = max(1, int(round(p * (len(pts) - 1 - (crash > 0)))))
    return pts[:n + 1] + (pts[-1:] if crash > 0 else [])


@gag("v3", 0)
def currency_crash(c, L):
    """A price chart of the Continental dollar in the sky: it slides, then crashes through the frame,
    and a note tumbles into the Atlantic."""
    t_money, t_crash = wt(L, "money"), wt(L, "crashed")
    set_shot(c, "wide")
    g = c.st["george"]
    if c.t >= t_crash:
        g.update(arm="chop")
    yield "front"
    if c.t < t_money - 0.2:
        return
    d = ImageDraw.Draw(c.world)
    x0, y0, x1, y1 = CHART
    age = c.t - (t_money - 0.2)
    drop = int(round((1 - back_out(min(1.0, age / 0.3))) * 40))     # rises from the sea, clear of the card
    shake = int(round(math.sin(c.t * 60) * 2)) if 0 <= c.t - t_crash < 0.3 else 0
    oy = drop
    d.rectangle((x0 - 1 + shake, y0 - 1 + oy, x1 + 1 + shake, y1 + 1 + oy), fill=INK)
    d.rectangle((x0 + shake, y0 + oy, x1 + shake, y1 + oy), fill=C["paper"])
    d.fontmode = "1"
    d.text(((x0 + x1) // 2 + shake, y0 - 1 + oy), "CONTINENTAL $", font=SILK, fill=INK, anchor="ma")
    d.line([(x0 + 3 + shake, y0 + 8 + oy), (x0 + 3 + shake, y1 - 3 + oy), (x1 - 3 + shake, y1 - 3 + oy)],
           fill=C["paper_sh"])
    d.text((x0 + 4 + shake, y1 - 11 + oy), "1776", font=SILK, fill=C["paper_sh"])
    d.text((x1 - 4 + shake, y1 - 11 + oy), "1780", font=SILK, fill=C["paper_sh"], anchor="ra")
    p = ramp(c.t, t_money, t_crash)
    crash = ramp(c.t, t_crash, t_crash + 0.18)
    pts = [(x + shake, y + oy) for x, y in chart_line(p, crash)]
    if len(pts) > 1:
        d.line(pts, fill=C["flag_red"], width=2)
    if crash >= 1:
        # the line punches through the bottom of the chart: a torn hole
        hx = int(chart_line(1, 1)[-2][0]) + 4 + shake
        d.polygon([(hx - 5, y1 + oy - 1), (hx - 2, y1 + oy - 4), (hx + 1, y1 + oy - 2), (hx + 4, y1 + oy - 5),
                   (hx + 6, y1 + oy + 1)], fill=INK)
    # a note tumbles from the crash point into the sea
    fall = c.t - t_crash
    if 0 <= fall < 0.55:
        p = fall / 0.55
        x, y = lerp(chart_line(1, 1)[-2][0] + 4, 166, p), lerp(y1, 130, ease_in(p))
        paste_rot(c.world, banknote(), x, y, fall * 700)
    if 0.55 <= fall < 1.4:
        splash(c.world, 166, 130, fall - 0.55, size=1.0, seed=3)


# --- 1: "not worth a Continental." My forgers printed it for days --------------------------------

PRESS_X, PRESS_FEET = 292, 115
N_NOTES = 30


def note_path(i, t_start):
    """(launch time, landing point) of the i-th forged note."""
    launch = t_start + i * 0.03
    if i % 3 == 0:                                   # a third fall short into the sea
        land = (118 + rnd("nx", i) * 90, 122 + rnd("ny", i) * 20)
    elif i in ON_WASH:                               # some settle on the General himself
        land = ON_WASH[i]
    else:                                            # the rest pile up on the wharf
        x = 4 + rnd("nx", i) * 94
        land = (x, 113 + rnd("ny", i) * 2 if WASH_X - 12 < x < WASH_X + 12 else 108 + rnd("ny", i) * 7)
    return launch, land


ON_WASH = {4: (WASH_X + 1, 63), 11: (WASH_X + 6, 92)}
BLOW = (line_t("v3", 3, "Own"), line_t("v3", 4) - 0.12)     # the pile blows away west on 'Own it'



def draw_notes(c, t_start):
    """The forged notes: out of the press, over the sea, fluttering down onto Boston, and blown off
    west at the end of the next line but one."""
    blow = ramp(c.t, *BLOW)
    for i in range(N_NOTES):
        launch, (lx, ly) = note_path(i, t_start)
        age = c.t - launch
        if age < 0:
            continue
        dur = 0.8 + rnd("nd", i) * 0.3
        a = (PRESS_X - 4, PRESS_FEET - 18)
        if age < dur:
            p = age / dur
            x, y = a[0] + (lx - a[0]) * p, a[1] + (ly - a[1]) * p - 46 * 4 * p * (1 - p)
            x += math.sin(age * 9 + i) * 3 * p
            paste_rot(c.world, banknote(), x, y, (age * 400 + i * 40) % 360)
        elif ly >= 118:                              # into the water
            splash(c.world, int(lx), int(ly), age - dur, size=0.5, seed=i)
        else:
            q = clamp(blow * 1.6 - rnd("nb", i) * 0.6, 0, 1)
            x, y = lx - 160 * q * q, ly - 30 * q + math.sin(q * 12 + i) * 4 * q
            paste_rot(c.world, banknote(), x, y, (i * 37) % 60 - 30 + 500 * q)


@gag("v3", 1)
def not_worth(c, L):
    """The phrase itself, big; then George's screw press on the London quay prints so many forged
    Continentals that they snow across the Atlantic onto Boston."""
    t_not, t_forgers = wt(L, "not"), wt(L, "forgers")
    t_print = wt(L, "printed")
    set_shot(c, "wide")
    g = c.st["george"]
    if c.t >= t_forgers:
        g.update(arm="point")
    if c.t >= t_print + 0.6:
        face(c, "washington", eyes="side" if c.f % 16 < 8 else "open", brows="worried")
    yield "back"
    rise = ease_out(ramp(c.t, t_forgers - 0.5, t_forgers - 0.1))
    if rise > 0:
        spr = press_sprite(int((c.t - t_print) * 10) % 4 if c.t >= t_print else 0)
        top = PRESS_FEET - int(spr.height * rise)
        part = spr.crop((0, 0, spr.width, PRESS_FEET - top + 2))
        c.world.paste(part, (PRESS_X - spr.width // 2, top), part)
    yield "front"
    draw_notes(c, t_print)
    t_bundle = t_print + 0.5
    if c.t >= t_bundle:
        fly(c.world, note_bundle(), (PRESS_X - 8, PRESS_FEET - 20), (208, 131), min(1.0, (c.t - t_bundle) / 0.6), 18)
        if c.t - t_bundle >= 0.6:
            splash(c.world, 208, 132, c.t - t_bundle - 0.6, size=1.3, seed=7)
    yield "ui"
    if c.t >= t_print + 0.3:
        tag_over(c, PRESS_X, PRESS_FEET - 36, "FORGERY DEPT.", c.t - t_print - 0.3, bg=C["red"], fg=C["gold"])
    age = c.t - t_not
    if age >= 0 and c.t < t_forgers + 0.2:
        out = ease_in(ramp(c.t, t_forgers - 0.1, t_forgers + 0.2))
        y = 22 - int(out * 60)
        big_text(c.ui, (W // 2, y + (pop_dy(age, drop=12) or 0)), "NOT WORTH A", PRESS16, anchor="ma",
                 top=C["paper"], bottom=C["paper_sh"])
        big_text(c.ui, (W // 2, y + 20 + (pop_dy(age - 0.3, drop=12) or 0)), "CONTINENTAL", PRESS16, anchor="ma")


debris(line_t("v3", 1, "printed") + 1.2, note_bundle, 208, 132, seed=11, drift=-0.4)


# --- 2: And your record, General? The fort that had your name on it -------------------------------

FORT_X, FORT_WL = 140, 122


def fort_top():
    return FORT_WL - int(round(0.62 * fort_sprite().height))


def draw_fort(c, rise, flag="grand_union", flag_h=1.0):
    img = c.world
    spr = fort_sprite()
    sink_draw(img, spr, FORT_X, FORT_WL, rise * 0.62, c.t, seed=2)
    top = FORT_WL - int(round(rise * 0.62 * spr.height))
    if rise < 0.2:
        return
    pole_x, pole_top = FORT_X - 12, top - 14
    d = ImageDraw.Draw(img)
    d.line([(pole_x, pole_top), (pole_x, top + 6)], fill=INK)
    d.point((pole_x, pole_top - 1), fill=C["gold"])
    fl = waving(flag_cloth(flag), c.t, phase=0.4, amp=1.0)
    fy = int(pole_top + (1 - flag_h) * 14)
    img.paste(fl, (pole_x + 1, fy - 1), fl)


def fort_name(c, age):
    """FORT WASHINGTON on a plank across the earthwork (on the UI so it reads at any zoom)."""
    if age < 0:
        return
    ux, uy = ui_at(c, FORT_X + 2, fort_top() + 15)
    label(c.ui, (ux, uy + (pop_dy(age, drop=10) or 0)), "FORT WASHINGTON", bg=C["wood_hi"], fg=INK,
          anchor="mm")


FORT_SHOT = (160, 100, 9)


@gag("v3", 2)
def fort_rises(c, L):
    """George sneers 'your record, General?', and Fort Washington rises out of the sea, flag flying,
    its name on a plank across the earthwork."""
    t_rec, t_fort, t_name = wt(L, "record"), wt(L, "fort"), wt(L, "name")
    t_print = line_t("v3", 1, "printed")
    if c.t < t_fort - 0.25:
        set_shot(c, "london")
        c.st["george"].update(arm="point", brows="up", eyes="shut" if c.t > t_rec + 0.3 else "open")
    else:
        set_shot(c, FORT_SHOT)
        face(c, "washington", eyes="side", brows="worried" if c.t > t_name else "neutral")
    yield "back"
    rise = ease_out(ramp(c.t, t_fort - 0.2, t_fort + 0.5))
    if rise > 0:
        draw_fort(c, rise)
        if c.t - (t_fort - 0.2) < 0.9:
            for k in range(6):
                splash(c.world, FORT_X - 26 + k * 10, FORT_WL, c.t - (t_fort - 0.2) - k * 0.03, size=0.6, seed=k)
    yield "front"
    draw_notes(c, t_print)
    yield "ui"
    fort_name(c, c.t - t_name)


# --- 3: surrendered twenty-eight hundred men by teatime. Own it. -----------------------------------

@gag("v3", 3)
def by_teatime(c, L):
    """The fort's colours come down and a white flag goes up as a counter ticks to 2,800 men; cut to
    George taking his tea, little finger out; on 'Own it' SURRENDERED is stamped over the fort and
    the forged money blows away."""
    t_sur, t_men, t_tea, t_own = wt(L, "surrendered"), wt(L, "men"), wt(L, "teatime"), wt(L, "Own")
    t_print = line_t("v3", 1, "printed")
    if c.t < t_tea - 0.15:
        set_shot(c, FORT_SHOT)
        face(c, "washington", eyes="side", brows="worried", mouth="frown")
    elif c.t < t_own - 0.1:
        set_shot(c, "london")
    else:
        set_shot(c, "wide")
    g = c.st["george"]
    if c.t >= t_tea - 0.15:
        g.update(arm="hold", eyes="shut", brows="up")
        if c.t > t_own + 0.4:
            g.update(mouth="smirk")
    yield "back"
    down = ramp(c.t, t_sur, t_sur + 0.35)
    up = ramp(c.t, t_sur + 0.4, t_men)
    if c.t < t_sur + 0.4:
        draw_fort(c, 1.0, "grand_union", 1.0 - down)
    else:
        draw_fort(c, 1.0, "white", up)
    yield "front"
    draw_notes(c, t_print)
    if c.t >= t_tea - 0.15:
        hx, hy = anchor(c, "george", "hand")
        paste(c.world, teacup(), hx - 1, hy + 1, "mm")
        d = ImageDraw.Draw(c.world)
        for k in range(3):                                       # steam
            ph = (c.t * 1.3 + k / 3) % 1.0
            d.point((int(hx - 2 + math.sin(ph * 6 + k) * 2), int(hy - 5 - ph * 8)), fill=C["white_sh"])
    yield "ui"
    if c.t < t_tea - 0.15:
        fort_name(c, 1.0)
    age = c.t - (t_sur + 0.2)
    if age >= 0 and c.t < t_tea - 0.15:
        n = int(2800 * ease_out(ramp(c.t, t_sur + 0.3, t_men + 0.3))) // 100 * 100
        ux, _ = ui_at(c, FORT_X, 0)
        big_text(c.ui, (ux, 22 + (pop_dy(age) or 0)), f"{n:,} MEN", PRESS16, anchor="ma",
                 top=C["white"], bottom=C["white_sh"])
        if c.t >= t_men:
            label(c.ui, (ux, 46 + (pop_dy(c.t - t_men, drop=5) or 0)), "TAKEN PRISONER", bg=C["band"],
                  fg=C["gold"], anchor="mt")
    if t_tea - 0.15 <= c.t < t_own - 0.1:
        ux, _ = ui_at(c, GEORGE_X, 0)
        age = c.t - t_tea
        big_text(c.ui, (ux - 64, 30 + (pop_dy(age) or 0)), "TEATIME", PRESS16, anchor="mt",
                 top=C["white"], bottom=C["paper_sh"])
        label(c.ui, (ux - 64, 52 + (pop_dy(age - 0.2, drop=6) or 0)), "16 NOV. 1776", bg=C["band"], fg=C["gold"],
              anchor="mt")
    if c.t >= t_own:
        ux, uy = ui_at(c, FORT_X, fort_top() + 6)
        stamp(c.ui, ux, uy, "SURRENDERED", color=C["flag_red"], angle=-10, size=8 if c.cam.k < 9 else 16,
              age=c.t - t_own)


# --- 4: Your favorite, Benedict Arnold, flipped his coat to red. -----------------------------------

ARNOLD_BOSTON = 36


@gag("v3", 4)
def turncoat(c, L):
    """Arnold marches in beside Washington with a gold FAVORITE star; on 'flipped' he spins on the
    spot and comes round in a red coat. The fort sinks back into the sea, leaving its white flag."""
    t_fav, t_ben, t_flip = wt(L, "favorite"), wt(L, "Benedict"), wt(L, "flipped")
    set_shot(c, "wide")
    if c.t >= t_ben:
        face(c, "washington", eyes="side" if c.t < t_flip else "wide", brows="neutral" if c.t < t_flip else "worried",
             mouth="closed" if c.t < t_flip else "o")
    yield "back"
    sink = 1.0 - ease_in(ramp(c.t, L.t0, L.t0 + 0.7))
    if sink > 0:
        draw_fort(c, sink, "white", 1.0)
    walk = ease_out(ramp(c.t, t_fav, t_ben + 0.2))
    if walk > 0:
        x = lerp(-14, ARNOLD_BOSTON, walk)
        spin = ramp(c.t, t_flip, t_flip + 0.45)
        squash = abs(math.cos(spin * math.pi * 2)) if 0 < spin < 1 else 1.0
        red = spin >= 0.25
        facing = -1 if 0.25 <= spin < 0.75 else 1
        step = int(c.t * 8) % 2 if walk < 1 else 0
        draw_arnold(c.world, x, FEET_Y - step, facing, red, squash=max(0.12, squash),
                    arm="palm" if c.t < t_flip else "hip", mouth="smirk" if red else "closed",
                    brows="up" if red else "neutral", eyes="shut" if red and spin >= 1 else "open")
    yield "ui"
    if walk > 0.6:
        ux, uy = ui_at(c, ARNOLD_BOSTON, FEET_Y - 50)
        age = c.t - (t_ben + 0.1)
        if c.t < t_flip:
            big_text(c.ui, (keep_in(ux, "FAVORITE", PRESS), uy - 14 + (pop_dy(c.t - t_fav) or 0)), "FAVORITE", PRESS,
                     anchor="mb")
        if age >= 0:
            label(c.ui, (keep_in(ux, "B. ARNOLD"), uy - 2), "B. ARNOLD", bg=C["paper"], anchor="mb")
        if c.t >= t_flip + 0.3:
            label(c.ui, (keep_in(ux, "COAT: FLIPPED"), uy + 1 + (pop_dy(c.t - t_flip - 0.3, drop=5) or 0)),
                  "COAT: FLIPPED", bg=C["red"], fg=C["gold"], anchor="mt")


debris(line_t("v3", 4) + 0.7, white_flag, 136, 120, seed=5, drift=0.15)


# --- 5: Your best general saw us both and picked the other George instead. ---------------------------

ARNOLD_LONDON = 225


def arnold_in_london(c, x=ARNOLD_LONDON, **pose):
    p = dict(arm="hip", mouth="smirk", brows="up", eyes="open")
    p.update(pose)
    draw_arnold(c.world, x, FEET_Y, -1, True, **p)


@gag("v3", 5)
def other_george(c, L):
    """Arnold, now in red, looks at one George, then the other, hops in a rowboat and rows across to
    the King, who welcomes him with a pat; his rank board changes armies."""
    t_saw, t_both, t_george = wt(L, "saw"), wt(L, "both"), wt(L, "George")
    set_shot(c, "wide")
    g = c.st["george"]
    if c.t >= t_george - 0.1:
        g.update(arm="palm", eyes="shut", brows="up", mouth="smile")
    if t_saw <= c.t < t_george:
        face(c, "washington", eyes="side", brows="worried")
    t_boat, t_land = t_both + 0.12, t_george - 0.3
    yield "back"
    if c.t < t_boat:
        p = ease_in_out(ramp(c.t, L.t0, t_saw))
        look = 1 if c.t < t_saw or c.t >= t_both else -1          # back at one George, then the other
        x = lerp(ARNOLD_BOSTON, 97, p)
        draw_arnold(c.world, x, FEET_Y - (int(c.t * 8) % 2 if 0 < p < 1 else 0), look, True,
                    arm="down", mouth="closed", eyes="open", brows="up" if c.t >= t_both else "neutral")
    elif c.t < t_land:
        p = ease_in_out(ramp(c.t, t_boat, t_land))
        bx = lerp(106, 211, p)
        wl = 127 + int(round(math.sin(p * math.pi) * 5))
        stroke = int(c.t * 8) % 2
        draw_arnold(c.world, bx, wl + 3, 1, True, arm="chop" if stroke else "palm", mouth="grit", eyes="open")
        paste(c.world, rowboat_small(), bx, wl + 4, "mb")
        d = ImageDraw.Draw(c.world)
        for k in range(4):
            d.line([(bx - 18 - k * 7, wl + 3 + k % 2), (bx - 15 - k * 7, wl + 3 + k % 2)], fill=WHITE)
    else:
        hop = ramp(c.t, t_land, t_land + 0.25)
        x = lerp(211, ARNOLD_LONDON, hop)
        y = lerp(127, FEET_Y, hop) - 10 * math.sin(hop * math.pi)
        draw_arnold(c.world, x, y, -1, True, arm="hip" if hop >= 1 else "wave", mouth="smirk", brows="up")
        sink = ramp(c.t, t_land + 0.2, t_land + 0.9)              # he doesn't need it back
        if sink < 1:
            sink_draw(c.world, rowboat_small(), int(211 - (c.t - t_land) * 10), 129, 1 - sink, c.t, seed=3)
    yield "ui"
    if c.t < t_boat:
        ux, uy = ui_at(c, lerp(ARNOLD_BOSTON, 97, ease_in_out(ramp(c.t, L.t0, t_saw))), FEET_Y - 50)
        label(c.ui, (keep_in(ux, "B. ARNOLD"), uy - 2), "B. ARNOLD", bg=C["paper"], anchor="mb")
    elif c.t >= t_land:
        ux, uy = ui_at(c, ARNOLD_LONDON - 12, FEET_Y - 22)
        age = c.t - t_land
        label(c.ui, (ux, uy - 1 + (pop_dy(age, drop=5) or 0)), "B. ARNOLD", bg=C["paper"], anchor="rb")
        label(c.ui, (ux, uy + 1 + (pop_dy(age - 0.15, drop=5) or 0)), "BRIG. GEN., BRITISH ARMY",
              bg=C["red"], fg=C["gold"], anchor="rt")
    if c.t >= t_george - 0.05:
        age = c.t - t_george
        big_text(c.ui, (W // 2, 22 + (pop_dy(age) or 0)), "THE OTHER", PRESS, anchor="ma",
                 top=C["white"], bottom=C["gold"])
        big_text(c.ui, (W // 2, 33 + (pop_dy(age - 0.1) or 0)), "GEORGE", PRESS16, anchor="ma")
        if age > 0.2:
            hx, hy = ui_at(c, *anchor(c, "george", "top"))
            arrow(c.ui, W // 2 + 44, 42, hx - 8, hy - 4, C["gold"], width=2, head=5)


# --- 6: The cherry tree? A parson made it up to sell a book. ------------------------------------------

TREE_X = 30
BOOK = (150, 70)


def arnold_idle(c):
    arnold_in_london(c, eyes="shut" if (c.t % 3.3) < 0.12 else "open")


@gag("v3", 6)
def parson_weems(c, L):
    """A cherry tree springs up on the Boston wharf; on 'parson' Weems's Life of Washington lands in
    the sky over the Atlantic, and on 'sell' a sticker slaps on the cover: NOW WITH CHERRY TREE!"""
    t_cherry, t_parson, t_sell = wt(L, "cherry"), wt(L, "parson"), wt(L, "sell")
    set_shot(c, "wide")
    if c.t >= t_cherry + 0.2:
        face(c, "washington", eyes="side", brows="up")
    yield "back"
    arnold_idle(c)
    grow = back_out(ramp(c.t, t_cherry, t_cherry + 0.3)) if c.t >= t_cherry else 0
    if grow > 0.05:
        tr = tree_sprite()
        tr = tr.resize((tr.width, max(1, int(tr.height * grow))), Image.NEAREST)
        paste(c.world, tr, TREE_X, FEET_Y + 1, "mb")
    yield "ui"
    if c.t >= t_parson:
        age = c.t - t_parson
        ux, uy = ui_at(c, *BOOK)
        cover = book_cover()
        s = back_out(min(1.0, age / 0.25))
        if s < 0.99:
            cover = cover.resize((max(1, int(cover.width * s)), max(1, int(cover.height * s))), Image.NEAREST)
        paste(c.ui, cover, ux, uy - 16, "mt")
        if c.t >= t_sell:
            st = sticker()
            a = c.t - t_sell
            ss = back_out(min(1.0, a / 0.14)) if a < 0.14 else 1.0
            st2 = st.resize((max(1, int(st.width * ss)), max(1, int(st.height * ss))), Image.NEAREST)
            paste_rot(c.ui, st2, ux + 24, uy + 49, 10)


# --- 7: The one story of you not lying? It's a lie. Go look. ------------------------------------------

@gag("v3", 7)
def its_a_lie(c, L):
    """Out of the book pops the famous line, I CANNOT TELL A LIE; FICTION is stamped across it and the
    cherry tree keels over; on 'Go look' George flicks the book into the sea (it floats there after).
    Arnold strolls off behind the King."""
    t_one, t_lie, t_go = wt(L, "one"), wt(L, "lie"), wt(L, "Go")
    set_shot(c, "wide")
    g = c.st["george"]
    if c.t >= t_go:
        g.update(arm="point", eyes="shut", brows="up")
    yield "back"
    leave = ramp(c.t, t_lie, t_go + 0.6)
    if leave < 1:
        x = lerp(ARNOLD_LONDON, 340, ease_in(leave))
        draw_arnold(c.world, x, FEET_Y - (int(c.t * 8) % 2 if 0 < leave else 0), 1 if leave > 0 else -1, True,
                    arm="hip", mouth="smirk", brows="up")
    fall = ramp(c.t, t_lie, t_lie + 0.35)
    tr = tree_sprite(fallen=fall >= 1)
    if 0 < fall < 1:
        tr = tree_sprite().rotate(80 * ease_in(fall), resample=Image.NEAREST, expand=True)
    paste(c.world, tr, TREE_X - (4 if fall >= 1 else 0), FEET_Y + 1, "mb")
    yield "front"
    t_toss = t_go + 0.15
    if c.t >= t_toss:
        p = min(1.0, (c.t - t_toss) / 0.55)
        if p < 1:
            fly(c.world, book_floating(), (BOOK[0], BOOK[1] + 18), (196, 145), p, 20, spin=1.2)
        else:
            splash(c.world, 196, 146, c.t - t_toss - 0.55, size=1.2, seed=9)
    yield "ui"
    if c.t < t_toss:
        ux, uy = ui_at(c, *BOOK)
        paste(c.ui, book_cover(), ux, uy - 16, "mt")
        if c.t < t_one:
            paste_rot(c.ui, sticker(), ux + 24, uy + 49, 10)
    if t_one <= c.t < t_toss:
        age = c.t - t_one
        ux, uy = ui_at(c, *BOOK)
        faded = c.t >= t_lie                                   # the quote greys out under the stamp
        box = bubble(c.ui, ux, uy - 20 + (pop_dy(age) or 0), ['"I CANNOT', 'TELL A LIE."'],
                     tail=(ux, uy - 2), anchor="mb", ink=(150, 146, 170) if faded else INK)
        if faded:
            stamp(c.ui, (box[0] + box[2]) // 2, (box[1] + box[3]) // 2, "FICTION", color=C["flag_red"], angle=-14,
                  size=16, age=c.t - t_lie)


debris(line_t("v3", 7, "Go") + 0.7, book_floating, 196, 146, seed=17, drift=-0.3)


# --- 8: I reigned for sixty years. You did eight, then ran home to the plow. ----------------------------

COL_WL = 138
G_COL, W_COL = 190, 158
PLOW_X = 42


def draw_columns(c, g_rise, w_rise):
    for x, rise, who, full in ((G_COL, g_rise, "george", 96), (W_COL, w_rise, "washington", 13)):
        if rise <= 0:
            continue
        spr = column(full, who)
        sink_draw(c.world, spr, x, COL_WL, rise * (full + 4) / (full + 6), c.t, seed=who == "george")


@gag("v3", 8)
def sixty_vs_eight(c, L):
    """Two columns rise from the sea as a bar chart: the King's sixty years tower into the sky, the
    General's eight barely clear the waves; then a plough slides onto the Boston wharf."""
    t_reign, t_eight, t_ran = wt(L, "reigned"), wt(L, "eight"), wt(L, "ran")
    set_shot(c, "wide")
    g = c.st["george"]
    if c.t >= t_reign:
        g.update(arm="fist" if c.t < t_eight else "point", brows="up")
    if c.t >= t_eight:
        face(c, "washington", eyes="side", brows="worried")
    yield "back"
    g_rise = ease_out(ramp(c.t, t_reign, t_reign + 0.8))
    w_rise = back_out(ramp(c.t, t_eight, t_eight + 0.3)) if c.t >= t_eight else 0
    draw_columns(c, g_rise, w_rise)
    slide = ease_out(ramp(c.t, t_ran, t_ran + 0.5))
    if slide > 0:
        paste(c.world, plow_sprite(), lerp(-24, PLOW_X, slide), FEET_Y + 1, "mb")
    yield "ui"
    if g_rise > 0.9:
        ux, uy = ui_at(c, G_COL, COL_WL - 100)
        big_text(c.ui, (ux, uy - 20), "60 YEARS", PRESS, anchor="mb", top=C["white"], bottom=C["gold"])
        label(c.ui, (ux, uy - 9), "1760-1820", bg=C["red"], fg=C["gold"], anchor="mb")
    if c.t >= t_eight + 0.15:
        ux, uy = ui_at(c, W_COL, COL_WL - 17)
        age = c.t - t_eight - 0.15
        big_text(c.ui, (ux - 6, uy - 20 + (pop_dy(age) or 0)), "8 YEARS", PRESS, anchor="mb", top=C["white"],
                 bottom=C["buff"])
        label(c.ui, (ux - 6, uy - 9 + (pop_dy(age) or 0)), "1789-1797", bg=C["navy"], fg=C["buff"], anchor="mb")
    if slide > 0.6:
        ux, uy = ui_at(c, PLOW_X, FEET_Y - 18)
        label(c.ui, (keep_in(ux, "MOUNT VERNON"), uy + (pop_dy(c.t - t_ran - 0.3, drop=5) or 0)), "MOUNT VERNON",
              bg=C["paper"], anchor="mb")


# --- 9: Couldn't hold a crown, so you called quitting "noble." Take a bow. ------------------------------

@gag("v3", 9)
def take_a_bow(c, L):
    """A crown floats down to Washington, slips through his hands and plops into the harbour; NOBLE
    appears in sarcastic quotes; on 'Take a bow' a spotlight finds him while George sweeps a bow."""
    t_hold, t_crown, t_noble, t_take, t_bow = (wt(L, "hold"), wt(L, "crown"), wt(L, "noble"), wt(L, "Take"),
                                               wt(L, "bow"))
    t_drop = t_crown + 0.1
    set_shot(c, (92, 100, 12) if c.t < t_drop + 0.9 else "wide")
    w = c.st["washington"]
    if t_hold - 0.3 <= c.t < t_crown + 0.5:
        w.update(arm="hold", eyes="wide" if c.t > t_crown else "open", mouth="o" if c.t > t_crown else "closed",
                 brows="up")
    elif t_crown + 0.5 <= c.t < t_take:
        face(c, "washington", eyes="side", brows="worried", mouth="frown")
    g = c.st["george"]
    bow = ramp(c.t, t_take, t_take + 0.3) * (1 - ramp(c.t, t_bow + 0.35, t_bow + 0.6))
    if bow > 0:
        g.update(rot=26 * ease_in_out(bow), arm="palm", eyes="shut", mouth="smile", shadow=False)
    yield "front"
    hx, hy = anchor(c, "washington", "hand")
    cr = falling_crown()
    if c.t < t_hold:
        p = ease_out(ramp(c.t, L.t0, t_hold))
        paste(c.world, cr, hx, lerp(40, hy - 1, p), "mb")
    elif c.t < t_drop:
        wob = int(round(math.sin(c.t * 40) * 1.5)) if c.t > t_crown - 0.15 else 0
        paste(c.world, cr, hx + wob, hy - 1, "mb")
    else:
        p = (c.t - t_drop) / 0.5
        if p < 1:
            fly(c.world, cr, (hx, hy - 4), (112, 140), p, 14, spin=1.5)
        else:
            splash(c.world, 112, 140, c.t - t_drop - 0.5, size=1.0, seed=4)
    if c.t >= t_take:
        # a stage spotlight on Washington
        k = ease_out(ramp(c.t, t_take, t_take + 0.15))
        m = mask(lambda d: d.polygon([(WASH_X - 4, -4), (WASH_X + 4, -4), (WASH_X + 20, FEET_Y + 2),
                                       (WASH_X - 20, FEET_Y + 2)], fill=255))
        dither(c.world, m * 0.35 * k, (255, 240, 200), blend=0.6)
    yield "ui"
    if c.t >= t_noble:
        ux, uy = ui_at(c, WASH_X, FEET_Y - 62)
        age = c.t - t_noble
        big_text(c.ui, (ux + 8, uy - 8 + (pop_dy(age) or 0)), '"NOBLE"', PRESS16, anchor="mb",
                 top=C["gold_hi"], bottom=C["gold"])


debris(line_t("v3", 9, "crown") + 0.6, falling_crown, 112, 140, seed=23, drift=0.1)


# --- 10: And spare me "liberty." Your man Harry ran to me and sailed off free, ---------------------------

SHIP_WL = 121


def ship_x(t):
    a, b = line_t("v3", 10, "Harry"), line_t("v3", 12)
    return lerp(112, 196, ease_in_out(ramp(t, a, b)))


def draw_transport(c):
    x = ship_x(c.t)
    y = SHIP_WL + int(round(math.sin(c.t * 1.6) * 0.8))
    sp = transport_ship()
    paste(c.world, sp, x, y + 3, "mb")
    d = ImageDraw.Draw(c.world)
    for xx in range(int(x) - 17, int(x) + 18):                      # the waterline, and a wake astern
        if (xx + int(c.t * 6)) % 3:
            d.point((xx, y), fill=WHITE)
    for k in range(4):
        d.line([(x - 24 - k * 6, y + k % 2), (x - 21 - k * 6, y + k % 2)], fill=WHITE)
    return x, y


def document(ui, box, title, lines, age, seal=False):
    """A parchment document dropping in on the UI layer."""
    if age < 0:
        return None
    dy = pop_dy(age, drop=10) or 0
    x0, y0, x1, y1 = box
    return parchment(ui, (x0, y0 + dy, x1, y1 + dy), title=title, lines=lines, seal=seal)


@gag("v3", 10)
def harry(c, L):
    """The world dims. A transport ship leaves the coast and sails east into the sun; over it, a
    plain record of Harry Washington: escaped Mount Vernon to the British in 1776, sailed from New
    York a free man in 1783."""
    t_lib, t_harry, t_free = wt(L, "liberty"), wt(L, "Harry"), wt(L, "free")
    sober(c, L)
    set_shot(c, "wide")
    c.card = False
    g = c.st["george"]
    g.update(arm="down", brows="neutral")
    yield "back"
    if c.t >= t_harry - 0.3:
        draw_transport(c)
    yield "ui"
    if c.t >= t_lib:
        ux, uy = ui_at(c, WASH_X, FEET_Y - 58)
        pixel_quote(c.ui, ux + 16, uy - 6, '"LIBERTY"', c.t - t_lib)
    if c.t >= t_harry:
        document(c.ui, (150, 18, 312, 66), "HARRY WASHINGTON",
                 ["1776: FLED MOUNT VERNON", "  TO THE BRITISH", "1783: SAILED FROM NEW YORK,",
                  "  A FREE MAN"][:2 + 2 * (c.t >= t_free - 0.4)], c.t - t_harry)


def pixel_quote(ui, x, y, s, age):
    """A word in quotation marks, plain white on a dark plate: quoted, not mocked."""
    if age < 0:
        return
    label(ui, (x, y + (pop_dy(age, drop=4) or 0)), s, bg=C["band"], fg=C["text"], anchor="mb", fnt=PRESS)


# --- 11: while you begged to get back your "property." --------------------------------------------------

@gag("v3", 11)
def property_(c, L):
    """Washington's 1783 demand to Sir Guy Carleton for the return of the people who had escaped to
    the British; Carleton's answer, REFUSED, stamped across it. The ship sails on."""
    t_begged, t_back = wt(L, "begged"), wt(L, "back")
    sober(c, L, start=L.t0 - 1.0)
    set_shot(c, "wide")
    c.st["george"].update(arm="down", brows="neutral")
    yield "back"
    draw_transport(c)
    yield "ui"
    box = document(c.ui, (80, 18, 246, 70), "TO SIR GUY CARLETON",
                   ["1783", "~", "~", "RE: THE RETURN OF", 'MY "PROPERTY"'], c.t - t_begged)
    if box and c.t >= t_back + 0.2:
        stamp(c.ui, box[2] - 38, box[3] - 9, "REFUSED", color=C["flag_red"], angle=-8, size=8,
              age=c.t - t_back - 0.2)


# --- 12: Your teeth ain't wood, that's folklore. It's hippo ivory beneath, --------------------------------

HIPPO_X, HIPPO_WL = 160, 130


@gag("v3", 12)
def hippo_ivory(c, L):
    """George's jab gets its comic beat back: a set of 'wooden' dentures chatters in the sky until
    FOLKLORE is stamped on them and they turn to ivory; on 'hippo' a hippopotamus surfaces in the
    middle of the Atlantic and grins."""
    t_teeth, t_folk, t_hippo = wt(L, "teeth"), wt(L, "folklore"), wt(L, "hippo")
    c.mood = MOOD * (1 - ease_in_out(ramp(c.t, L.t0 - 0.15, L.t0 + 0.4)))
    set_shot(c, "boston" if c.t < t_hippo - 0.1 else "sea")
    g = c.st["george"]
    if c.t >= t_teeth:
        g.update(arm="point")
    face(c, "washington", mouth="grit" if c.t < t_teeth else "o", brows="worried" if c.t < t_folk else "up",
         eyes="wide" if t_teeth <= c.t < t_folk else "open")
    yield "back"
    rise = ease_out(ramp(c.t, t_hippo - 0.1, t_hippo + 0.35))
    if rise > 0:
        spr = hippo(1 if c.t > t_hippo + 0.45 else 0)
        sink_draw(c.world, spr, HIPPO_X, HIPPO_WL, rise * 0.8, c.t, seed=6)
        if c.t - t_hippo < 0.8:
            splash(c.world, HIPPO_X - 14, HIPPO_WL, c.t - t_hippo, size=1.0, seed=1)
            splash(c.world, HIPPO_X + 14, HIPPO_WL, c.t - t_hippo - 0.05, size=1.0, seed=2)
    yield "front"
    if t_teeth <= c.t < t_hippo - 0.1:
        # the teeth jump out of the General's mouth and chatter in the air beside him
        mx, my = anchor(c, "washington", "mouth")
        p = back_out(ramp(c.t, t_teeth, t_teeth + 0.25))
        ivory = c.t >= t_folk + 0.15
        gap = (c.f % 4) if not ivory else 1
        x, y = lerp(mx, mx + 26, p), lerp(my, my - 10, p)
        paste(c.world, dentures(not ivory, gap), x, y, "mm")
    yield "ui"
    if t_teeth + 0.15 <= c.t < t_hippo - 0.1:
        mx, my = anchor(c, "washington", "mouth")
        ux, uy = ui_at(c, mx + 26, my - 23)
        uy += pop_dy(c.t - t_teeth - 0.15, drop=5) or 0
        words = "WOODEN TEETH?" if c.t < t_folk else " " * 13      # the stamp lands on a blank plate
        box = label(c.ui, (ux, uy), words, bg=C["paper"], anchor="mb", fnt=PRESS)
        if c.t >= t_folk:
            stamp(c.ui, ux, (box[1] + box[3]) // 2, "FOLKLORE", color=C["flag_red"], angle=8, size=8,
                  age=c.t - t_folk)
    if c.t >= t_hippo + 0.3:
        ux, uy = ui_at(c, HIPPO_X, HIPPO_WL - 24)
        label(c.ui, (ux, uy - 6 + (pop_dy(c.t - t_hippo - 0.3, drop=6) or 0)), "HIPPO IVORY", bg=C["paper"],
              anchor="mb", fnt=PRESS)


# --- 13: and nine you bought from people that you owned, --------------------------------------------------

@gag("v3", 13)
def nine_teeth(c, L):
    """Dark again, close on Washington. A page of his accounts is written out line by line: May 1784,
    paid for nine teeth."""
    t_nine, t_bought = wt(L, "nine"), wt(L, "bought")
    sober(c, L, level=MOOD, fade=0.35)
    set_shot(c, "boston")
    c.card = False
    c.st["george"].update(arm="down", brows="neutral")
    yield "ui"
    age = c.t - (L.t0 - 0.05)
    if age >= 0:
        x0, y0, x1, y1 = 168, 26, 312, 84
        parchment(c.ui, (x0, y0, x1, y1), title="ACCOUNTS", lines=[], rolled=False)
        d = ImageDraw.Draw(c.ui)
        d.fontmode = "1"
        ink = (70, 40, 20)
        d.text((x0 + 5, y0 + 15), "MOUNT VERNON, MAY 1784", font=SILK, fill=ink)
        for yy in range(y0 + 26, y1 - 2, 9):
            d.line([(x0 + 4, yy + 7), (x1 - 4, yy + 7)], fill=C["paper_sh"])
        d.text((x0 + 5, y0 + 28), typed("PAID FOR NINE TEETH", c.t - t_nine, cps=22), font=SILK, fill=ink)
        if c.t >= t_bought + 0.3:
            d.text((x0 + 5, y0 + 37), typed("TO ENSLAVED PEOPLE", c.t - t_bought - 0.3, cps=24), font=SILK,
                   fill=ink)


# --- 14: so every time you said "freedom," George, you said it with their teeth. ----------------------------

@gag("v3", 14)
def with_their_teeth(c, L):
    """No stamp, no punch: Washington's own word, FREEDOM, hangs in a speech bubble while the camera
    creeps in on him and the sea goes still. George lowers the mic."""
    t_free, t_their = wt(L, "freedom"), wt(L, "their")
    sober(c, L, level=MOOD, fade=0.3)
    c.mood = MOOD + 0.2 * ease_in_out(ramp(c.t, t_free + 0.4, t_their))
    c.calm = ramp(c.t, L.t0, t_free + 0.5)
    c.card = False
    pan(c, "two", "boston", L.t0, 5.2, ease=ease_in_out)
    g = c.st["george"]
    g.update(arm="down", brows="neutral")
    if c.t > t_their + 0.3:
        g.update(mic=False)
    w = c.st["washington"]
    if c.t >= t_their:
        w.update(eyes="shut")
    yield "ui"
    if c.t >= t_free:
        mx, my = anchor(c, "washington", "mouth")
        ux, uy = ui_at(c, mx + 2, my - 2)
        bubble(c.ui, ux + 22, max(28, uy - 18) + (pop_dy(c.t - t_free, drop=5) or 0), '"FREEDOM"',
               tail=(ux + 3, uy - 2), anchor="mb")
