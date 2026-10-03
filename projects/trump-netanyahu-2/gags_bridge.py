"""Bridge: the 2009 winner walks in. He won his for a speech, hands Donald a pacifier, points out who
nominated whom, then lists the troops and the drones, and leaves on the slogan and a mic drop."""
from gagkit import *  # noqa: F403

T_ON, T_OFF = V.OBAMA_ON
T_EXIT = T_OFF - 1.6
DOOR, MARK = V.SPOTS["door"], (160, 166)
T_PACI = when("bridge", 1, "pacifier") + 0.35


def walk(c, who, p0, p1, a, dur):
    """Walk from p0 to p1 (feet), stepping, over `dur` seconds from age a. True while walking."""
    s = c.st[who]
    k = clamp(a / dur, 0, 1)
    s["spot"] = (lerp(p0[0], p1[0], ease_in_out(k)), lerp(p0[1], p1[1], ease_in_out(k)))
    if 0 < k < 1:
        s["facing"] = 1 if p1[0] >= p0[0] else -1
        s["legs"] = ("step0", "step1")[int(a * 5) % 2]
        s["bob"] = int(a * 10) % 2
        return True
    return False


@span(T_ON, T_OFF)
def obama_walks(c, L):
    """In from the left-hand door while the card is up; out the same way after the mic drop."""
    if c.t < T_EXIT:
        walk(c, "obama", DOOR, MARK, c.t - T_ON, 1.4)
        if c.t - T_ON < 1.4:
            pose(c, "obama", arms="wave", mouth="grin", eyes="open")
            for who in V.SEATED:
                pose(c, who, eyes="side" if who == "trump" else "open", mouth="o", brows="up", react=False)
    else:
        walk(c, "obama", MARK, DOOR, c.t - T_EXIT, 1.4)
        pose(c, "obama", arms="wave", mouth="grin")
    yield "ui"


@span(T_ON + 0.6, when("bridge", 1))
def lift_the_bars(c, L):
    pose(c, "bibi", mouth="grin", eyes="half") if c.t > when("bridge", 0) + 1.3 else None
    yield "ui"


@gag("bridge", 0)
def won_mine(c, L):
    a = age(L, "mine")
    if a > -0.2:
        hold_up(c, "obama", P.medal(), lift=2)
        pose(c, "obama", mouth=c.st["obama"]["mouth"], eyes="half")
        flash_press(c, "mine", 6, a)
    if age(L, "speech") > 0:
        for who in V.SEATED:
            pose(c, who, eyes="wide", mouth="o", brows="angry", react=False)
    yield "front"
    if a > 0:
        hx, hy = c.anchor["obama"]["held"]
        P.sparkles(c.world, hx, hy, a, n=4, r=12)


@gag("bridge", 1)
def pacifier(c, L):
    a_clear, a_p = age(L, "clear"), age(L, "pacifier")
    if a_clear > -0.1 and a_p < -0.3:
        pose(c, "obama", arms="clear", brows="up")
    if a_p > -0.3:
        pose(c, "obama", arms="point")
    yield "front"                                                      # (Obama is drawn after "mid")
    if 0 <= a_p < 0.35:
        hx, hy = c.anchor["obama"]["hand_far"]
        fly(c.world, mirror(P.pacifier()), (hx, hy), c.anchor["trump"]["mouth"], a_p / 0.35, h=14, rot=1)


@span(T_PACI, TL.section_end("bridge") + 0.3)
def binky(c, L):
    """Donald, pacified: it stays in until Bibi's next verse, and he fumes around it."""
    pose(c, "trump", mouth="pout", brows="angry", eyes="squint", flush=1, react=False)
    yield "mid"
    mx, my = c.anchor["trump"]["mouth"]
    put(c.world, mirror(P.pacifier()), mx - 1, my + 1)


@gag("bridge", 2)
def nominates(c, L):
    a_n, a_s = age(L, "nominates"), age(L, "bomb")
    if a_n > -0.2 and a_s < 0:
        hold_up(c, "bibi", P.letter(), lift=2)
        pose(c, "bibi", mouth="grin", eyes="half", react=False)
    if a_s > 0.4:
        hold_up(c, "bibi", P.gift_bomb(), lift=0)
        pose(c, "bibi", mouth="grin", eyes="shut", flush=1, react=False)
    pose(c, "obama", arms="point" if a_n > 0 else c.st["obama"]["arms"], facing=-1 if a_n > 0 else 1)
    yield "front"
    if 0 <= a_s < 0.4:
        fly(c.world, P.gift_bomb(), (226, 90), (100, 70), a_s / 0.4, h=24)
        fly(c.world, P.letter(), (100, 70), (226, 80), a_s / 0.4, h=-14)


@gag("bridge", 3)
def troops(c, L):
    a_p, a_t = age(L, "prize"), age(L, "troops")
    if a_p > -0.2:
        hold_up(c, "obama", P.medal(), lift=2)
        pose(c, "obama", mouth=c.st["obama"]["mouth"])
    yield "front"
    for k in range(2):
        a = a_t - 0.35 * k
        if 0 <= a < 1.8:
            put(c.world, P.chopper(), lerp(-40, 360, a / 1.8), 14 + 10 * k + int(2 * math.sin(c.t * 9)))


@gag("bridge", 4)
def drone_war(c, L):
    a_d, a_y = age(L, "drone"), age(L, "Yes")
    if a_y > -0.2:
        hold(c, "obama", P.sign("YES WE", "CAN"))
        pose(c, "obama", mouth=c.st["obama"]["mouth"], brows="up")
    yield "front"
    if 0 <= a_d < 2.0:
        put(c.world, mirror(P.drone()), lerp(360, -50, a_d / 2.0), 22 + int(2 * math.sin(c.t * 4)))


@gag("bridge", 5)
def mic_drop(c, L):
    a = L.t - L.t0
    left = TL.section_end("bridge") - c.t                              # all done before Verse 4's card
    c.press = clamp(min(a / 0.4, left / 0.5), 0.0, 1.0)
    c.press_mood = "cheer"
    if left > 0:
        flash_press(c, "yes", 6, a)
    t_drop = end_of(L) + 0.25
    if c.t < t_drop:
        hold_up(c, "obama", P.mic(), lift=-4)
        pose(c, "obama", mouth="grin", eyes="half")
    else:
        pose(c, "obama", arms="shrug", mouth="grin", eyes="shut")
    yield "front"
    a_d = c.t - t_drop
    if a_d >= 0:
        x, y0 = c.anchor["obama"]["hand_far"]
        y = min(160, y0 + 400 * a_d * a_d)
        put(c.world, P.mic(), x, y)
        if y >= 160 and a_d < 0.6:
            c.add_shake(2)
    yield "ui"
    shout(c, 160, 22, "YES WE CAN!", a, size=16, world=False, dur=a + left - 0.1, top=C["white"], bottom=C["blue"])
    if a_d > 0.35:
        shout(c, 112, 112, "BOOM.", a_d - 0.35, size=8, world=False, dur=1.2)
