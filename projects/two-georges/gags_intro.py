"""Intro: the Town Crier, in a rowboat in the middle of the Atlantic, introduces the Georges."""
from gagkit import (BOSTON_EDGE, C, GEORGE_X, LONDON_EDGE, PRESS16, PRESS24, W, WASH_X,
                    Canvas, ImageDraw, arrow, big_text, ease_in, ease_out, gag, label, lerp, lru_cache, mirror,
                    math, pan, paste, pop_dy, ramp, sea_color, wt)

BOAT_X, BOAT_Y = 160, 131          # the rowboat's centre and waterline
CREW_Y = BOAT_Y - 3                # the crier's feet


@lru_cache(maxsize=None)
def rowboat(part):
    """The crier's rowboat: 'back' (inside and far gunwale) and 'front' (the near side of the hull)."""
    s = Canvas(40, 12)
    if part == "back":
        s.poly([(3, 3), (36, 3), (33, 6), (6, 6)], "wood_sh")
        s.line([(3, 3), (36, 3)], "wood_hi")
        return s.done(None)
    s.poly([(1, 3), (38, 3), (34, 10), (5, 10)], "wood")
    s.line([(1, 3), (38, 3)], "wood_hi")
    s.line([(4, 7), (35, 7)], "wood_sh")
    s.line([(5, 10), (34, 10)], "wood_deep")
    s.rect((30, 4, 32, 6), "gold")                     # a brass plate on the bow
    return s.done()


@lru_cache(maxsize=None)
def oar():
    s = Canvas(24, 6)
    s.line([(1, 1), (16, 3)], "wood_hi")
    s.poly([(15, 2), (22, 2), (22, 4), (15, 4)], "wood")
    return s.done()


def boat_pos(c, t_leave):
    """The boat bobs in place, then rows off south (toward the viewer and out of the frame)."""
    bob = int(round(math.sin(c.t * 2.2) * 1.0))
    go = ease_in(ramp(c.t, t_leave, t_leave + 1.6))
    return BOAT_X + int(18 * go), BOAT_Y + bob + int(60 * go)


def crier_in_boat(c, t_leave=12.0, facing=1):
    s = c.st["crier"]
    x, y = boat_pos(c, t_leave)
    s.update(hidden=False, x=x, y=y - 3, facing=facing, shadow=False, rim=0.4)
    return x, y


def draw_boat_back(c, x, y):
    b = rowboat("back")
    paste(c.world, b, x, y - 1, "mb")


def draw_boat_front(c, x, y):
    b = rowboat("front")
    paste(c.world, b, x, y + 2, "mb")
    d = ImageDraw.Draw(c.world)
    sea = sea_color(y + 3)
    for xx in range(x - 21, x + 21):
        d.point((xx, y + 2), fill=sea if (xx + c.f // 3) % 3 else C["white"])
    for side in (-1, 1):                               # oars shipped along the sides
        o = oar() if side > 0 else mirror(oar())
        paste(c.world, o, x + side * 14, y - 1, "mm")


def ringing(c, times, dur=0.5):
    """True while the bell is being rung after any of `times`."""
    return any(0 <= c.t - t < dur for t in times) and c.f % 4 < 2


@gag("intro", 0, pre=1.0)
def hear_ye(c, L):
    """Close on the crier ringing his bell; pull out over 'three thousand miles of sea' to the two shores,
    with a surveyor's dimension line across the ocean."""
    x, y = crier_in_boat(c)
    t_three, t_sea = wt(L, "Three"), wt(L, "sea")
    c.st["crier"].update(bell="ring" if ringing(c, [wt(L, "Hear"), wt(L, "hear")], 0.35) else True,
                         mouth="wide" if c.t < t_three else "open")
    c.shot = (160, 104, 12)
    if c.t >= t_three - 0.1:
        pan(c, (160, 104, 12), "wide", t_three - 0.1, 0.9)
    for who in ("washington", "george"):
        c.st[who]["mic"] = False
    yield "back"
    draw_boat_back(c, x, y)
    yield "front"
    draw_boat_front(c, x, y)
    age = c.t - t_sea
    if age >= 0:
        p = ease_out(age / 0.5)
        y_line = 70
        a, b = BOSTON_EDGE + 4, LONDON_EDGE - 4
        mid = (a + b) / 2
        d = ImageDraw.Draw(c.world)
        for xx in (a, b):
            d.line([(xx, y_line - 4), (xx, y_line + 4)], fill=C["white"])
        arrow(c.world, mid, y_line, lerp(mid, a, p), y_line, C["white"], width=1, head=4)
        arrow(c.world, mid, y_line, lerp(mid, b, p), y_line, C["white"], width=1, head=4)
        if age > 0.3:
            label(c.world, (mid, y_line - 12 + (pop_dy(age - 0.3, drop=4) or 0)), "3,000 MILES", bg=C["paper"],
                  anchor="mt")


@gag("intro", 1)
def east_and_west(c, L):
    """'In the East, the King' pans to London; 'In the West, the General' pans back to Boston."""
    x, y = crier_in_boat(c)
    t_east, t_west = wt(L, "East"), wt(L, "West")
    c.st["crier"].update(facing=1 if c.t < t_west - 0.3 else -1, arm="point", mouth="open")
    c.shot = "wide"
    if c.t >= t_east - 0.35:
        pan(c, "wide", "london", t_east - 0.35, 0.45)
    if c.t >= t_west - 0.35:
        pan(c, "london", "boston", t_west - 0.35, 0.55)
    g, w = c.st["george"], c.st["washington"]
    g.update(eyes="shut", brows="up", mouth="smirk", arm="hip")
    w.update(arm="cross", brows="neutral", mouth="closed")
    if c.t >= t_west:
        w.update(arm="wave" if c.t - t_west < 0.8 else "cross")
    yield "back"
    draw_boat_back(c, x, y)
    yield "front"
    draw_boat_front(c, x, y)
    yield "ui"
    if t_east <= c.t < t_west - 0.3:
        age = c.t - t_east - 0.25
        if age >= 0:
            ux, uy = c.to_ui(GEORGE_X, 66)
            big_text(c.ui, (ux, uy + (pop_dy(age) or 0)), "THE KING", PRESS16, anchor="mb")
            label(c.ui, (ux, uy + 4), "GEORGE III, BY THE GRACE OF GOD", bg=C["red"], fg=C["gold"], anchor="mt")
    if c.t >= t_west:
        age = c.t - t_west - 0.3
        if age >= 0:
            ux, uy = c.to_ui(WASH_X, 66)
            big_text(c.ui, (ux, uy + (pop_dy(age) or 0)), "THE GENERAL", PRESS16, top=C["white"],
                     bottom=C["buff"], anchor="mb")
            label(c.ui, (ux, uy + 4), "COMMANDER-IN-CHIEF, CONTINENTAL ARMY", bg=C["navy"], fg=C["buff"],
                  anchor="mt")


@gag("intro", 2)
def two_georges(c, L):
    """Back to the wide shot: the title slams in, both Georges take up their mics, and on 'Let's go!'
    the crier rings the bell like a prize-fight and rows for his life."""
    t_two, t_one, t_go = wt(L, "Two"), wt(L, "One"), wt(L, "Let's")
    x, y = crier_in_boat(c, t_leave=t_go + 0.7)
    cr = c.st["crier"]
    cr.update(facing=1 if (c.f // 6) % 2 else -1, arm="point" if c.t < t_go else "down", mouth="open")
    if c.t >= t_go:
        cr.update(bell="ring" if c.f % 4 < 2 else True, mouth="wide", eyes="wide")
    c.shot = "wide"
    for who in ("washington", "george"):
        s = c.st[who]
        if c.t >= t_go:
            s.update(mic=True, arm="fist" if c.t - t_go < 1.2 else "point", mouth="closed",
                     brows="angry" if who == "washington" else "up")
        else:
            s.update(arm="cross")
    c.karaoke = c.t < L.words[-1]["t1"] + 0.6
    yield "back"
    draw_boat_back(c, x, y)
    yield "front"
    draw_boat_front(c, x, y)
    if c.t >= t_go and c.t - t_go < 1.2:                  # DING DING
        d = ImageDraw.Draw(c.world)
        bx, by = x + 6 * cr["facing"], y - 52
        for k in range(3):
            r = 4 + k * 3 + (c.f % 3)
            d.arc((bx - r, by - r, bx + r, by + r), 200, 340, fill=C["gold_hi"])
    yield "ui"
    if c.t >= t_two:
        age = c.t - t_two
        out = ease_in(ramp(c.t, 12.6, 13.1))
        y0 = 26 - int(out * 70)
        big_text(c.ui, (W // 2, y0 + (pop_dy(age, drop=14) or 0)), "TWO GEORGES", PRESS24, anchor="ma")
        if c.t >= t_one:
            label(c.ui, (W // 2, y0 + 30 + (pop_dy(c.t - t_one, drop=6) or 0)), "ONE CONTINENT",
                  bg=C["paper"], anchor="mt")
        if c.t >= t_go:
            label(c.ui, (W // 2, y0 + 44 + (pop_dy(c.t - t_go, drop=6) or 0)), "A TRANSATLANTIC RAP BATTLE",
                  bg=C["band"], fg=C["gold"], anchor="mt")
