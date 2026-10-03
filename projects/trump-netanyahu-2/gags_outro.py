"""Outro: the decision. Both men beg for it, the envelope is opened, and the Nobel Peace Prize goes to
the one guest with no wars, no trial and no drones: the turkey Trump pardoned in Verse 1."""
from gagkit import *  # noqa: F403

T_WIN = when("outro", 1, "turkey")
END0 = TL.section_start("end")
T_END = TL.DURATION
TABLE_TOP = office.TABLE[1]


def hopeful(c, who, k=1.0):
    """Hands clasped, leaning in, eyes on the envelope."""
    pose(c, who, arms="beg", eyes="wide", brows="up", lean=3 + int(2 * k), react=False,
         mouth="o" if who == "trump" else "smirk")


def envelope_hand(c):
    pose(c, "announcer", arms="read", facing=1)


@gag("outro", 0, pre=0.6)
def decision(c, L):
    a = L.t - L.t0
    c.press = clamp((a + 0.6) / 0.6, 0, 1)
    c.press_mood = "cheer"
    envelope_hand(c)
    for who in V.SEATED:
        hopeful(c, who, k_in(age(L, "decision"), 0.4))
    if age(L, "decision") > 0:
        flash_press(c, "decision", 5, age(L, "decision"))
    yield "front"
    x, y = c.anchor["announcer"]["hand_near"]
    put(c.world, P.envelope(), x, y - 5)


@gag("outro", 1)
def the_turkey(c, L):
    a = c.t - T_WIN
    c.press = 1.0
    c.press_mood = "gasp" if a > 0 else "cheer"
    if a < 0:
        envelope_hand(c)
        for who in V.SEATED:
            hopeful(c, who)
            c.st[who]["sweat"] = age(L, "goes") > 0
    else:
        pose(c, "announcer", arms="wave", facing=1, mouth="grin", eyes="open")
        for who in V.SEATED:
            pose(c, who, arms="shrug", eyes="wide", brows="up", mouth="wide", lean=0, react=False)
        flash_press(c, "turkey", 8, a)
        if a < 0.1:
            c.add_flash(0.35, C["gold_hi"])
    yield "back"
    if a > 0:
        paint_portrait(c.world, P.turkey_portrait())
        P.sparkles(c.world, 160, 48, a, n=5, r=20)
    yield "front"
    if a < 0:
        x, y = c.anchor["announcer"]["hand_near"]
        put(c.world, P.envelope(), x, y - 5)
    yield "ui"
    shout(c, 160, 30, "GOBBLE!", a - 0.35, size=8, dur=1.4)


def the_record(c, ticks, a_p):
    """The laureate's record, ticked off as it is sung, and the pardon stamped on it. Donald takes the
    credit for the pardon: it was his, in Verse 1."""
    c.press = 1.0
    c.press_mood = "gasp"
    pose(c, "announcer", arms="mic", mouth=c.st["announcer"]["mouth"])
    pose(c, "trump", arms="cross", mouth="pout", eyes="squint", brows="angry", react=False)
    pose(c, "bibi", arms="lap", mouth="frown", eyes="side", brows="worried", react=False)
    if a_p > 0:
        pose(c, "trump", arms="thumb", mouth="grin", eyes="squint", brows="neutral", lean=2)


@gag("outro", 2)
def no_wars(c, L):
    a_p = age(L, "pardon")
    the_record(c, sum(age(L, w) > 0 for w in ("wars", "trial")), a_p)
    yield "back"
    paint_portrait(c.world, P.turkey_portrait())
    yield "ui"
    inset(c, (118, 18, 202, 82), P.checklist(sum(age(L, w) > 0 for w in ("wars", "trial"))), "THE LAUREATE",
          k_in(L.t - L.t0 + 0.12, 0.25))
    if a_p > 0:
        fx.stamp(c.ui, 160, 54, "PARDONED", fnt=SILK16, color=C["red"], angle=-12, age=a_p)


@gag("outro", 3)
def no_drones(c, L):
    a_p = age(L, "pardon")
    the_record(c, 3, a_p)
    yield "back"
    paint_portrait(c.world, P.turkey_portrait())
    yield "ui"
    inset(c, (118, 18, 202, 82), P.checklist(2 + (age(L, "drones") > 0)), "THE LAUREATE")
    fx.stamp(c.ui, 160, 54, "PARDONED", fnt=SILK16, color=C["red"], angle=-12)


def turkey_at(c):
    """The laureate struts in from the right, hops onto the coffee table, and takes its bows."""
    a = c.t - (END0 + 0.4)
    if a < 0:
        return None
    if a < 1.2:
        return lerp(340, 160, ease_out(a / 1.2)), TABLE_TOP + 10, False
    if a < 1.5:
        p = (a - 1.2) / 0.3
        return 160, lerp(TABLE_TOP + 10, TABLE_TOP - 17, p) - 10 * math.sin(p * math.pi), False
    return 160, TABLE_TOP - 17, True


@span(END0, T_END + 1.0)
def gobble(c, L):
    a = c.t - END0
    s = c.st["announcer"]
    s["dy"] = int(80 * ease_in(clamp(a / 0.5, 0, 1)))                # he ducks out of the shot
    if a > 0.5:
        s["hidden"] = True
    c.press = 0.6
    c.press_mood = "gobble"
    pose(c, "trump", arms="cross", mouth="pout", eyes="side", brows="angry", react=False)
    pose(c, "bibi", arms="cross", mouth="frown", eyes="half", react=False)
    if c.beat_i % 4 == 0 and c.ph < 0.5:
        flash_press(c, ("gobble", c.beat_i), 3, c.ph)
    yield "back"
    paint_portrait(c.world, P.turkey_portrait())
    yield "mid"
    at = turkey_at(c)
    if at:
        x, y, up = at
        bow = up and c.beat_i % 2 == 0 and c.ph < 0.45
        tk = mirror(P.turkey("open" if bow else "closed", medal=True))
        paste_rot(c.world, tk, int(x), int(y + (2 if bow else 0)), 14 if bow else 0)
    yield "ui"
    if a > 1.6:
        right = c.beat_i % 2 == 1
        shout(c, 240 if right else 80, 100, "GOBBLE!", c.ph * TL.PERIOD, size=16, world=False,
              top=C["gold_hi"], bottom=C["orange"], dur=TL.PERIOD)
    t_card = T_END - 3.4
    if c.t > t_card:
        V.card(c, "TURKEY WINS", "THE NOBEL PEACE PRIZE FIGHT, ROUND 2", k_in(c.t - t_card, 0.25))
