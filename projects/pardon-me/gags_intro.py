"""The intro: the President opens the session to an empty rostrum and a RESERVED desk, the screens put
up both men's rap sheets, a stampede of lawyers crosses the floor, then the two walk in to their
places: Trump waving, Bibi with an armful of rolled-up posters. "Visual aids": Bibi hoists his
armful, Trump holds up one Sharpie, and the chart turns to the title page.
"""
import art_ends as A
from gagkit import (C, PRESS, V, anchor, back_out, flip, gag, hall, lerp, line_t, math, paste, paste_rot, place,
                    pop_text, pose, ramp, rnd, span, sparkle, wt)

T_LAWYERS = line_t("intro", 1, "lawyers")


# --- shared bits ------------------------------------------------------------------------------------

def jolt(c, times, dur=0.35):
    """The delegates jump at each gavel slam: hands up, half out of their seats."""
    for g in times:
        age = c.t - g
        if 0 <= age < dur:
            for _, _, i in hall.DELEGATES:
                k = (1 - age / dur) * (0.7 + 0.3 * rnd("jolt", g, i))
                c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), k)
                c.crowd["stand"][i] = max(c.crowd["stand"].get(i, 0.0), 0.4 * k)


def cut(a, b, t, seed):
    """A screen showing `a` until t, two frames of static, then `b`."""
    def fn(c, img, box):
        if c.t < t:
            a(c, img, box)
        elif c.t < t + 0.08:
            A.static(img, box, (seed, int(c.t * 24)))
        else:
            b(c, img, box)
    return fn


def un_left(c, img, box):
    A.un_card(c, img, box)


def un_right(c, img, box):
    A.un_card(c, img, box, mirror=True)


def sheet(who, count, t0):
    return lambda c, img, box: A.rap_sheet(img, box, who, count, c.t - t0)


def live(who, facing):
    return lambda c, img, box: V.live_feed(c, img, box, who, facing)


def bundle(img, gx, gy, angle):
    """Paste Bibi's armful of posters rotated by `angle` degrees with its grip at (gx, gy)."""
    spr = A.poster_bundle(9, 70)
    _, hy = A.bundle_grip(spr)
    d = spr.height / 2 - hy                            # from the grip up to the sprite's centre
    a = math.radians(angle)
    paste_rot(img, spr, gx + d * math.sin(a), gy + d * math.cos(a), angle)


def hide(c, *who):
    for w in who:
        place(c, w, hidden=True)


# --- "In the General Assembly!" ------------------------------------------------------------------

@gag("intro", 0)
def cold_open(c, L):
    hide(c, "trump", "bibi")
    c.placard = "RESERVED"
    c.screens["L"], c.screens["R"] = un_left, un_right
    slams = [0.05, wt(L, "Assembly")]
    c.gavel = slams
    jolt(c, slams)
    flip(c, -1.0)
    yield "chart"
    A.agenda(c.page, c.t - 0.15)


# --- "Two world leaders with one thing in common: lawyers." --------------------------------------

@gag("intro", 1)
def rap_sheets(c, L):
    hide(c, "trump", "bibi")
    c.placard = "RESERVED"
    two, leaders = wt(L, "Two"), wt(L, "leaders")
    c.screens["L"] = cut(un_left, sheet("trump", "4 INDICTMENTS", two), two, 1)
    c.screens["R"] = cut(un_right, sheet("bibi", "3 CASES", leaders), leaders, 2)
    flip(c, -1.0)
    yield "chart"
    A.agenda(c.page, 99)


# The herd: (lag behind the leader in px, feet y, speed px/s, variant)
HERD = [(k * 9 + rnd("lag", k) * 14, 131 + int(rnd("fy", k) * 8), 235 + rnd("v", k) * 45, k) for k in range(18)]


def lawyer_x(lag, speed, age):
    return -14 - lag + speed * age


@span(T_LAWYERS - 0.02, T_LAWYERS + 2.2)
def stampede(c, L):
    """A herd of tiny lawyers sprints across the floor in front of the rostrum, kicking up dust."""
    age = c.t - T_LAWYERS
    for lag, fy, speed, k in HERD:                     # the delegates below duck as the herd passes
        x = lawyer_x(lag, speed, age)
        for dx, _, i in hall.DELEGATES:
            if abs(dx - x) < 7:
                c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), 0.55)
    yield "mid"
    for lag, fy, speed, k in sorted(HERD, key=lambda h: h[1]):
        for j in range(4):                              # dust kicked up every 0.1 s
            slot = int(age / 0.1) - j
            pt = slot * 0.1
            px = lawyer_x(lag, speed, pt)
            if pt >= 0 and -10 < px < 330:
                A.dust(c.world, px + 2, fy - 1, age - pt, size=0.8, seed=(k, slot))
    for lag, fy, speed, k in sorted(HERD, key=lambda h: h[1]):
        x = lawyer_x(lag, speed, age)
        if -16 < x < 336:
            f = int(c.t * 14 + k) % 2
            paste(c.world, A.lawyer(f, k), x, fy - (1 if f else 0), "mb")


# --- "Donald Trump! Benjamin Netanyahu! Bring your visual aids!" ---------------------------------

BIBI_IN = 0.5          # Bibi starts walking this long before "Benjamin"


@gag("intro", 2)
def enter_the_leaders(c, L):
    t_in = L.t0 - 0.12
    trump_t, bibi_t, netan = wt(L, "Trump"), wt(L, "Benjamin"), wt(L, "Netanyahu")
    bring, vis = wt(L, "Bring"), wt(L, "visual")
    slam = next(g for g in V.GAVEL if g > L.t0)       # the chair recognizes the first speaker
    t = c.t
    step = int(t * 6) % 2

    # Trump strides in from the left, waving, and plants at the rostrum on his name
    if t < trump_t:
        p = ramp(t, t_in, trump_t)
        x = lerp(-28, 160, 1 - (1 - p) ** 1.6)
        place(c, "trump", x=x, y=166, facing=1, layer="podium")
        pose(c, "trump", body="walk1" if step else "walk2", bob=step, arm="wave" if int(t * 5) % 2 else "up",
             far="down", mouth="grin", eyes="squint", brows="up")
    elif t < bring:
        pose(c, "trump", arm="thumb", far="down", mouth="grin" if t < trump_t + 1.2 else "smirk", eyes="squint")
    else:
        pose(c, "trump", arm="fist", far="down", mouth="grin", eyes="squint", brows="up")

    # Bibi walks in from the right behind the desk, his visual aids under his arm
    arrive = netan + 0.15
    b0 = bibi_t - BIBI_IN
    if t < b0:
        hide(c, "bibi")
    else:
        p = ramp(t, b0, arrive)
        place(c, "bibi", x=lerp(348, 270, p), y=176 - (step if p < 1 else 0), facing=-1, layer="desk")
        walking = p < 1
        pose(c, "bibi", body=("walk1" if step else "walk2") if walking else "stand", arm="down", far="down",
             mouth="closed", brows="neutral", eyes="open")
        if walking:
            c.st["bibi"]["brows"] = "up"
        elif t < arrive + 0.35:
            pose(c, "bibi", arm="palm")
        if t >= bring:
            pose(c, "bibi", arm="up", mouth="smirk", brows="up")
        if slam <= t < slam + 0.45:
            pose(c, "bibi", arm="palm", mouth="o", eyes="wide", brows="worried")
    c.placard = "RESERVED" if t < arrive else "ISRAEL"

    c.screens["L"] = cut(sheet("trump", "4 INDICTMENTS", -99), live("trump", 1), trump_t, 3)
    c.screens["R"] = cut(sheet("bibi", "3 CASES", -99), live("bibi", -1), netan, 4)
    jolt(c, [slam])
    flip(c, vis if t >= vis else -1.0)

    yield "chart"
    if t >= vis:
        A.title_page(c.page)
    else:
        A.agenda(c.page, 99)

    yield "mid"
    if t >= b0:                                       # the armful of posters, under his far arm
        cx, cy = anchor(c, "bibi", "chest")
        lift = 7 * back_out(ramp(t, bring, bring + 0.2)) if t >= bring else 0
        drop = ramp(t, slam, slam + 0.2) ** 2 * 70 if t >= slam else 0
        sway = (3 if step else -3) if t < arrive else 0
        bundle(c.world, cx + 9, cy + 3 - lift + drop, -18 + sway)

    yield "front"
    if arrive <= t < arrive + 0.6:                    # RESERVED gets tossed over his shoulder
        a = t - arrive
        spr = hall.placard_sprite("RESERVED")
        paste_rot(c.world, spr, 270 + a * 110, 135 - 70 * a + 160 * a * a, -a * 900)
    if t >= bring:                                    # Trump's visual aid: one Sharpie
        hx, hy = anchor(c, "trump", "hand")
        k = back_out(ramp(t, bring, bring + 0.15))
        paste(c.world, A.sharpie(), hx + 1, hy + 6 - int(5 * k), "mb")
        if 0.15 < t - bring < 0.6:
            sparkle(c.world, int(hx + 5), int(hy - 13), 2 if int(t * 10) % 2 else 1, C["white"])

    yield "top"
    if t >= vis:
        age = t - vis
        pop_text(c.ui, 160, 7, "PARDON ME", age)
        if age > 0.18:
            pop_text(c.ui, 160, 27, "TRUMP vs. BIBI", age - 0.18, fnt=PRESS)
