"""Verse 4: Bibi's last word. The mugshot mug, the trial-day tummy bug, the golf cam, FIFA's peace
prize, the sticker chart, the gold merch, and the gold pager that beeps."""
from gagkit import *  # noqa: F403

T_PAGER = when("v4", 6, "pager") + 0.4
T_BEEP = when("v4", 7, "beeps")
V4_END = TL.section_end("v4")
MERCH = (("sneakers", P.sneakers, 136), ("Bible", P.bible, 160), ("potty", P.potty, 184))


@gag("v4", 0)
def mugshot_mug(c, L):
    a_m, a_c = age(L, "mugshot"), age(L, "coffee")
    if a_m > -0.2:
        if a_c < 0.2:
            hold_up(c, "bibi", P.mug(), lift=2)
        else:                                                          # a sip, eyes on Donald
            hold(c, "bibi", P.mug(), arms="drink")
            pose(c, "bibi", eyes="side", mouth="closed")
    if a_m > 0:
        pose(c, "trump", mouth="frown", brows="angry", eyes="squint", react=False)
    yield "ui"
    if a_m > -0.2:
        inset(c, (118, 18, 202, 82), P.mug_inset(), "OFFICIAL MERCH", k_in(a_m + 0.2, 0.25))


@gag("v4", 1)
def tummy_bug(c, L):
    a_c, a_t = age(L, "court"), age(L, "tummy")
    if a_c > -0.1:
        pose(c, "bibi", arms="tummy", eyes="half", brows="worried", mouth="frown", flush=2, react=False,
             tint=((150, 196, 110), 0.12))
        pose(c, "trump", eyes="up", mouth="pout")
    yield "mid"
    if a_c > -0.1:
        mx, my = c.anchor["bibi"]["mouth"]
        paste_rot(c.world, P.thermometer(), mx + 5, my + 2, -62)
    yield "ui"
    shout(c, 122, 60, "COUGH", a_t, size=8, dur=0.6)
    shout(c, 130, 50, "COUGH!", a_t - 0.5, size=8, dur=0.7)


@gag("v4", 2)
def fairway(c, L):
    a0, a = age(L, "caddy"), age(L, "kick")
    pose(c, "bibi", arms="point")
    if a > 0:
        pose(c, "trump", eyes="side", sweat=True, mouth="frown", brows="worried", react=False)
    yield "ui"
    if a0 > -0.2:
        inset(c, (118, 18, 202, 82), P.fairway_inset(max(0.0, a + 0.3)), "GOLF CAM", k_in(a0 + 0.2, 0.25))


@gag("v4", 3)
def pele(c, L):
    a_f, a_p = age(L, "FIFA"), age(L, "Pel") + 0.35                     # the ball lands on "Pele"
    if a_f > -0.2:
        hold(c, "trump", P.trophy(), arms="hold")
        pose(c, "trump", mouth="grin", eyes="shut", lean=1)
    hit = a_p - 0.35
    if 0 <= hit < 1.2:
        pose(c, "trump", eyes="wide", mouth="o", brows="worried", react=False)
        c.st["trump"]["dx"] += int(round(2 * max(0.0, 1 - hit / 0.25)))
    yield "front"
    hx, hy = c.anchor["trump"]["head"]
    if a_f > 0.2 and hit < 0:
        P.sparkles(c.world, 229, 98, a_f, n=4, r=18)
    if 0 <= a_p < 0.35:
        fly(c.world, P.ball(), (40, 20), (hx - 4, hy + 4), a_p / 0.35, h=16, rot=2)
    elif 0 <= hit < 0.8:
        fly(c.world, P.ball(), (hx - 4, hy + 4), (340, -10), hit / 0.8, h=24, rot=2)
    yield "ui"
    shout(c, hx - 4, hy - 8, "BONK!", hit, size=8, dur=0.8)


@gag("v4", 4)
def sticker_chart(c, L):
    a_g, a_n = age(L, "good"), age(L, "naughty")
    hold(c, "bibi", P.poster("stars"))
    if a_g > 0:
        pose(c, "trump", eyes="up", mouth="grin", react=False)
    if a_n > 0:
        pose(c, "trump", arms="cross", mouth="pout", eyes="squint", brows="angry", react=False)
    yield "front"
    if a_n > 0:                                                        # a star comes unstuck and drops
        hx, hy = c.anchor["bibi"]["held"]
        sx, sy = hx - 23 + 32, hy - 17 + 21                            # the third star of the second row
        ImageDraw.Draw(c.world).rectangle((sx - 3, sy - 3, sx + 3, sy + 3), fill=C["paper"])
        y = sy + 220 * a_n * a_n
        if y < 150:
            paste_rot(c.world, P.gold_star(3), int(sx + 10 * a_n), int(y), a_n * 300)


@gag("v4", 5)
def gold_merch(c, L):
    pose(c, "trump", arms="thumb", mouth="grin", eyes="squint")
    if age(L, "potty") > 0:
        pose(c, "trump", arms="cross", mouth="frown", eyes="wide", brows="angry", react=False)
    yield "ui"


@span(when("v4", 5, "sneakers"), V4_END)
def merch_on_the_mantel(c, L):
    """Gold sneakers, a gold Bible and a gold potty, on sale on the mantelpiece."""
    yield "back"
    for i, (pat, spr, x) in enumerate(MERCH):
        a = c.t - when("v4", 5, pat)
        s = spr()
        pop_in(c.world, s, x, 84 - s.height // 2, a)
        if 0 < a < 1.5:
            P.sparkles(c.world, x, 76, a, n=2, r=9, seed=i)


@gag("v4", 6)
def gold_pager(c, L):
    a_p, a_s = age(L, "pager"), age(L, "straight")
    if -0.3 < a_p < 0.4:
        hold_up(c, "bibi", P.pager(), lift=2)
    if a_s > -0.3:
        pose(c, "trump", arms="lap", lean=0, bob=0, eyes="wide", mouth="closed", brows="up", react=False)
    yield "front"
    if 0 <= a_p < 0.4:
        fly(c.world, P.pager(), (110, 72), c.anchor["trump"]["chest"], a_p / 0.4, h=18, rot=1)


@span(T_PAGER, V4_END + 0.3)
def pager_pinned(c, L):
    yield "mid"
    x, y = c.anchor["trump"]["chest"]
    lit = c.t >= T_BEEP and int((c.t - T_BEEP) * 6) % 2 == 0
    put(c.world, P.pager(lit=lit), x + 9, y - 9)                      # on his lapel


@gag("v4", 7)
def it_beeps(c, L):
    a_b, a_f = age(L, "beeps"), age(L, "farm")
    if a_b <= 0:                                                       # still sitting up straight
        pose(c, "trump", arms="lap", lean=0, bob=0, eyes="wide", mouth="closed", brows="up", react=False)
    else:
        pose(c, "trump", arms="shrug", eyes="wide", mouth="o", brows="worried", sweat=True, flush=1, react=False)
        c.st["trump"]["dx"] += 1 if int(c.t * 16) % 2 else -1          # trembling
    yield "back"
    if a_f > 0:
        paint_portrait(c.world, P.farm(with_trump=True))
    yield "ui"
    x, y = c.anchor["trump"]["chest"]
    if a_b > 0 and a_f < 0.6:
        shout(c, x + 9, y - 24, "BEEP BEEP", a_b, size=8, top=C["sick"], bottom=C["green"])
