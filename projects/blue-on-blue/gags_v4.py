"""Verse 4: the guest closes. The host's state is driving to Texas, billionaires and businesses and exes
first; come January he's jobless, jealous and losing; a lame duck with a ring light and nobody watching; and
next year the show is called This Was Gavin Newsom."""
from gagkit import *  # noqa: F403

NEWSOM_DESK = (96, 116)


def convoy(t):
    """The road to Texas over both lines: a U-Haul, then the billionaires, the businesses and the exes."""
    starts = [("U-HAUL", when("v4", 0, "state")), ("U-HAUL", when("v4", 0, "Texas")),
              ("$$$", when("v4", 1, "billionaires")), ("HQ", when("v4", 1, "businesses")), ("EX", when("v4", 1, "exes"))]
    return [(label, t - t0) for label, t0 in starts if t - t0 < 2.6]


@gag("v4", 0)
def to_texas(c, L):
    a = age(L, "state")
    if a > 0.3:
        pose(c, "newsom", eyes="side", brows="worried", mouth="frown", react=False)
    yield "ui"
    if a > -0.3:
        inset(c, INSET, P.road_to_texas(L.t, convoy(L.t)), "I-10 EAST", k_in(a + 0.3, 0.25))


@gag("v4", 1)
def billionaires_exes(c, L):
    a_ex = age(L, "exes")
    pose(c, "newsom", eyes="side", brows="worried", mouth="frown" if a_ex < 0 else "o", react=a_ex > 0)
    yield "ui"
    inset(c, INSET, P.road_to_texas(L.t, convoy(L.t)), "I-10 EAST")


@gag("v4", 2)
def january(c, L):
    a_jan, a_job, a_jeal, a_lose = age(L, "January"), age(L, "jobless"), age(L, "jealous"), age(L, "losin")
    if a_job > -0.1:
        hold(c, "newsom", P.desk_box(), arms="show")
        pose(c, "newsom", eyes="half", brows="worried", mouth="frown", react=False)
    if a_jeal > 0:
        pose(c, "newsom", flush=2, eyes="side")
    yield "front"
    if a_lose > 0:
        ex, ey = c.anchor["newsom"]["eye"]
        pop_in(c.world, P.l_sticker(), ex + 5, ey - 10, a_lose, dur=0.12)
    yield "ui"
    if a_jan > 0:
        x, y = c.to_ui(32, 30)
        pop_in(c.ui, P.calendar(), x, y, a_jan)


@gag("v4", 3)
def lame_duck(c, L):
    a_duck, a_ring, a_list = age(L, "duck"), age(L, "ring"), age(L, "listeners")
    pose(c, "newsom", eyes="half", brows="worried", mouth="frown", react=False)
    if 0 < a_ring < 0.9:
        pose(c, "newsom", eyes="squint", mouth="grit")
    if a_list > 0:                                                     # nobody's watching any more
        k = k_in(a_list, 0.7)
        c.viewers = int(round(math.exp(lerp(math.log(2_870_000), math.log(3), ease_in_out(k)))))
        for j in range(6):
            aa = a_list - j * 0.15
            if 0 <= aa < 1.6:
                c.floats.append(("zzz", 298 + int(rnd("z", j) * 14), 140 - aa * 60))
    yield "back"
    if 0 < a_ring < 0.9:                                               # the ring light, full in his face
        k = 1 - a_ring / 0.9
        blend(c.world, 1.0, "ring_glow", 0.35 * k)
    yield "front"
    if a_duck > -0.1:                                                  # the lame duck hops onto the desk
        p = clamp((a_duck + 0.1) / 0.35, 0, 1)
        x, y = arc_pt(p, (-20, 100), (NEWSOM_DESK[0] + 22, NEWSOM_DESK[1] - 4), 30)
        hop = abs(math.sin(L.t * 7)) * 2 if p >= 1 else 0
        put(c.world, P.rubber_duck(), x, y - hop)


@gag("v4", 4, post=0.2)
def this_was(c, L):
    a_this, a_was = age(L, "This"), age(L, "Was")
    c.viewers = 3
    if a_this > 0:
        pose(c, "newsom", eyes="up", brows="worried", mouth="o", arms="clasp", react=False)
    if 0 <= a_this and a_was < 0:
        c.neon_flicker = True
    if a_was >= 0:
        c.neon_word, c.neon_color = "WAS", C["neon_red"]
        if a_was < 0.1:
            c.add_flash(0.25, C["neon_red"])
    if -0.15 < a_this and L.t < L.t1:
        c.shot = "neon"
    yield "front"
    if 0 <= a_was < 0.6:
        x0, y0, x1, y1 = studio.NEON
        for j in range(6):
            p = a_was / 0.6
            sx = 146 + int(rnd("spx", j) * 14) + int((rnd("sdx", j) - 0.5) * 30 * p)
            sy = 21 + int(p * p * 50 * (0.6 + rnd("sdy", j)))
            ImageDraw.Draw(c.world).point((sx, sy), fill=C["gold_hi"] if j % 2 else C["white"])
