"""Verse 2: Bibi's answer. Trump is a toddler: drawings on the fridge, gold stars, nap time, Jell-O,
a bonnet, ketchup on the wall, a bottle, both hands on the cup, and London's giant baby."""
from gagkit import *  # noqa: F403

T_STAR = when("v2", 6, "star") + 0.45
T_BONNET = when("v2", 7, "toddler")
T_KETCHUP = when("v2", 8, "ketchup")
T_BALLOON = when("v2", 10, "giant")
END_HOOK = TL.section_end("hook")
T_AWAY = when("v3", 0) + 0.6


@gag("v2", 0)
def fridge_again(c, L):
    pose(c, "bibi", arms="point")
    a = age(L, "smile")
    if a > 0:
        pose(c, "trump", mouth="grin", eyes="shut")
    yield "ui"
    from gags_v1 import fridge_inset
    fridge_inset(c, 1.0, 1.0, k_in(age(L, "fridge") + 0.2, 0.25))


@gag("v2", 1)
def epstein_files(c, L):
    a, a_files = age(L, "drawing"), age(L, "Epstein")
    if a_files > -0.3:
        hold(c, "bibi", P.binder("EPSTEIN", "FILES"))
        pose(c, "trump", eyes="wide", mouth="o", brows="worried", sweat=True, flush=1, react=False, lean=0)
        flash_press(c, "files", 8, a_files)
    yield "ui"
    if a > -0.2:
        inset(c, (118, 18, 202, 82), P.redacted_page(a), "THE FILES", k_in(a + 0.2, 0.25))


@gag("v2", 2)
def golden_dome(c, L):
    a = age(L, "colored")
    if age(L, "Iron") > -0.3:
        hold(c, "bibi", P.poster("dome"))
    if a > -0.1:
        hold_up(c, "trump", P.crayon(), lift=2)
        pose(c, "trump", mouth="grin", eyes="squint")
    yield "ui"


@gag("v2", 3)
def nap_time(c, L):
    a_job, a_nap = age(L, "job"), age(L, "nap")
    pose(c, "bibi", arms="palm" if a_nap < 0 else "finger")
    if a_job > 0.3 and a_nap < 0:
        pose(c, "trump", mouth="grin", eyes="shut", lean=1)
    if a_nap > 0:
        pose(c, "trump", eyes="shut", mouth="o", bob=4, lean=3, arms="between", react=False)
    yield "mid"
    if 0 <= a_job < 0.4:
        fly(c.world, P.gold_star(), (110, 92), (226, 92), a_job / 0.4, h=18)
    elif a_job >= 0.4:
        put(c.world, P.gold_star(), 224, 100)
    if a_nap > 0:
        hx, hy = c.anchor["trump"]["head"]
        P.zzz(c.world, hx - 18, hy + 4, a_nap)


@span(when("v2", 3, "Jell"), TL.section_end("v2"))
def jello(c, L):
    """Dessert, on the coffee table, wobbling."""
    a = c.t - when("v2", 3, "Jell")
    yield "mid"
    put(c.world, P.jello(), 160, 126 + wobble(a, 2, 25, 0.6) - int(30 * (1 - ease_out(min(1.0, a / 0.2)))))


@gag("v2", 4)
def soldier(c, L):
    a = age(L, "soldier")
    if age(L, "shoulder") > -0.2:
        pose(c, "bibi", arms="shoulder", mouth=c.st["bibi"]["mouth"], brows="angry")
    pose(c, "trump", eyes="shut" if a < 0.6 else "side", mouth="o" if a < 0.6 else "pout")
    yield "back"
    if a > 0:
        paint_portrait(c.world, P.soldier_painting())
        P.sparkles(c.world, 160, 48, a, n=3, r=16)


@gag("v2", 5)
def bone_spurs(c, L):
    a = age(L, "note")
    if a > -0.3:
        hold(c, "bibi", P.poster("bonespur"))
    if age(L, "spurs") > 0:
        pose(c, "trump", eyes="side", mouth="frown", brows="worried", lean=0)
    if age(L, "older") > 0:
        pose(c, "trump", mouth="pout", eyes="squint")
    yield "ui"


@gag("v2", 6)
def gold_star(c, L):
    a = age(L, "star")
    if a > -0.4:
        hold_up(c, "bibi", P.gold_star(5), lift=0)
    if a > 0.45:
        pose(c, "trump", eyes="up", mouth="grin", lean=1)
    yield "mid"
    if 0 <= a < 0.45:
        sx, sy = c.anchor["bibi"]["hand_far"]
        fly(c.world, P.gold_star(5), (sx, sy - 6), forehead(c, "trump"), a / 0.45, h=16)


@span(T_STAR, END_HOOK)
def star_on_forehead(c, L):
    yield "mid"
    put(c.world, P.gold_star(), *forehead(c, "trump"))


@gag("v2", 7)
def toddler(c, L):
    if age(L, "eighty") > 0:
        pose(c, "trump", eyes="wide", brows="up")
    if age(L, "toddler") > 0:
        pose(c, "trump", mouth="pout", eyes="squint", brows="angry")
    yield "ui"


@span(T_BONNET, END_HOOK)
def bonnet(c, L):
    a = c.t - T_BONNET
    yield "mid"
    drop = -30 * (1 - ease_out(min(1.0, a / 0.25)))
    on_head(c, c.world, "trump", P.bonnet(), dy=int(drop) - 3)


@span(T_KETCHUP, TL.section_end("v2"))
def ketchup(c, L):
    a = c.t - T_KETCHUP
    yield "back"
    if a < 0.15:
        put(c.world, P.ketchup(0), 268, 62)
        P.bang(c.world, 268, 60, 6 + 40 * a, rot=a)
    else:
        put(c.world, P.ketchup(min(1.0, (a - 0.15) / 2.0)), 268, 62)


@gag("v2", 8)
def bottle(c, L):
    a = age(L, "cry")
    if age(L, "ketchup") > 0:
        pose(c, "trump", arms="chop", mouth="grit", brows="angry")
        c.add_shake(3 * max(0.0, 1 - age(L, "ketchup") / 0.25))
    if a > -0.1:
        hold_up(c, "trump", P.bottle(), lift=2)
        pose(c, "trump", mouth="wide", eyes="shut", brows="worried", react=False)
    yield "mid"
    if a > 0:
        ex, ey = c.anchor["trump"]["eye"]
        for k in range(2):
            p = (a * 2 + k * 0.5) % 1.0
            ImageDraw.Draw(c.world).rectangle((ex - 4 - 6 * k, ey + 2 + int(14 * p), ex - 3 - 6 * k, ey + 4 + int(14 * p)),
                                              fill=C["sweat"])
    yield "ui"
    shout(c, 236, 48, "WAAH!", a, size=8, dur=1.2, top=C["white"], bottom=C["sweat"])


@gag("v2", 9)
def two_hands(c, L):
    a_ramp = age(L, "down")
    if age(L, "hands") > -0.2:
        hold(c, "trump", P.sippy(), arms="drink")
        pose(c, "trump", eyes="squint", mouth="o", lean=1)
    yield "ui"
    if a_ramp > -0.2:
        inset(c, (118, 18, 202, 82), P.ramp_inset(a_ramp + 0.2), "THE RAMP, 2020", k_in(a_ramp + 0.2, 0.25))


def balloon_at(c):
    """Where London's giant baby is: in from the left, over Trump by "model", away at Verse 3."""
    a = c.t - T_BALLOON
    if a < 0 or c.t > T_AWAY + 1.5:
        return None
    x = lerp(-40, 236, ease_in_out(min(1.0, a / 1.6)))
    y = 26 + 2 * math.sin(c.t * 2.2)
    if c.t > T_AWAY:
        y -= 90 * ease_in(min(1.0, (c.t - T_AWAY) / 1.5))
    return x, y


@span(T_BALLOON, T_AWAY + 1.5)
def balloon(c, L):
    yield "back"
    xy = balloon_at(c)
    if xy:                                                             # the tether runs down behind Trump
        x, y = xy
        ImageDraw.Draw(c.world).line([(x, y + 26), (x - 6, y + 70)], fill=C["steel_sh"])
    yield "front"
    if xy:
        put(c.world, P.baby_balloon(), x, y)


@gag("v2", 10)
def model(c, L):
    a = age(L, "model")
    if age(L, "giant") > 0:
        pose(c, "trump", eyes="up", mouth="frown", brows="worried", lean=0)
    if a > 0:
        pose(c, "trump", eyes="squint", mouth="pout", brows="angry", arms="cross")
        flash_press(c, "model", 6, a)
    yield "ui"
