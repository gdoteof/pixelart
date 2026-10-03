"""Intro: a ring announcer works the Oval Office like a prize fight."""
from gagkit import *  # noqa: F403


def spotlight(img, x, color, k):
    """A coloured stage light falling on a chair from above."""
    if k > 0:
        blend_poly(img, [(x - 12, 0), (x + 12, 0), (x + 44, 150), (x - 44, 150)], color, 0.2 * k)


def gloves(c, img, who, color):
    g = P.glove(color)
    for k in ("hand_near", "hand_far"):
        x, y = c.anchor[who][k]
        put(img, g, x, y - 2)


@gag("intro", 0, pre=0.6)
def live(c, L):
    a = age(L, "Nobel")
    if a > 0:
        pose(c, "trump", lean=3, eyes="wide", mouth="o")
        pose(c, "bibi", eyes="wide", mouth="open", lean=1)
    yield "back"
    if a > 0:
        paint_portrait(c.world, P.nobel_painting())
        P.sparkles(c.world, 160, 48, a, n=5, r=20)
    if 0 <= a < 0.1:
        c.add_flash(0.25)


@gag("intro", 1)
def red_corner(c, L):
    s = c.st["announcer"]
    s.update(arms="point", facing=1)
    a = age(L, "Department")
    if a > 0:
        hold(c, "trump", P.folder("DEPT OF", "WAR"))
        pose(c, "trump", mouth="grin", eyes="squint")
        flash_press(c, "dow", 4, a)
    yield "back"
    spotlight(c.world, 230, C["red"], k_in(age(L, "red"), 0.3))


@gag("intro", 2)
def eight_wars(c, L):
    a = age(L, "eight")
    hold(c, "trump", P.folder("8 WARS", "ENDED") if a > -0.4 else P.folder("DEPT OF", "WAR"))
    pose(c, "trump", mouth="pout" if a < 0 else "grin")
    c.st["announcer"].update(arms="mic", eyes="side" if age(L, "says") > 0 else "open")
    yield "back"
    spotlight(c.world, 230, C["red"], 1.0)


@gag("intro", 3)
def blue_corner(c, L):
    c.st["announcer"].update(arms="point", facing=-1)
    a = age(L, "fighting")
    pose(c, "bibi", arms="fist" if a > 0 else "wave", mouth="smirk" if a < 0 else "grit", brows="angry" if a > 0 else "neutral")
    if a > 0:
        flash_press(c, "fight", 3, a)
    yield "back"
    spotlight(c.world, 92, C["blue"], k_in(age(L, "blue"), 0.3))


# The band plays alone for eleven seconds after the intro: the bell, the handshake (the yank, the pats),
# and Donald playing to the cameras, all on the beat.
T_CRIMES = when("intro", 4, "crimes")
T_BELL = TL.next_beat(T_CRIMES + 1.0)
B = TL.PERIOD
T_SHAKE = T_BELL + B                                                   # the close-up slides in
T_YANKS = (T_SHAKE + B, T_SHAKE + 5 * B)
T_PATS = tuple(T_SHAKE + (2 + 0.5 * k) * B for k in range(4))
T_LET_GO = T_SHAKE + 6 * B
T_CAMERAS = T_LET_GO + B
T_V1 = TL.section_start("v1")


@gag("intro", 4)
def clean_fight(c, L):
    if c.t >= T_BELL:
        return
    a_crimes = age(L, "crimes")
    c.st["announcer"].update(arms="clear" if a_crimes < 0 else "point", facing=1 if a_crimes < 0 else -1)
    gloved = age(L, "biting") > -0.3
    if gloved:
        pose(c, "trump", arms="fist", mouth="grit", lean=1)
        pose(c, "bibi", arms="fist", mouth="grit", brows="angry")
    if a_crimes > 0:
        pose(c, "bibi", eyes="side", mouth="frown", brows="worried", sweat=True, react=False)
        pose(c, "trump", arms="shrug", mouth="pout", eyes="side")
        flash_press(c, "crimes", 5, a_crimes)
    yield "back"
    spotlight(c.world, 230, C["red"], 1.0)
    spotlight(c.world, 92, C["blue"], 1.0)
    yield "mid"
    if gloved:
        gloves(c, c.world, "trump", "red")
        if a_crimes <= 0:
            gloves(c, c.world, "bibi", "blue")


@span(T_BELL, T_V1)
def ding_ding(c, L):
    """The bell: the announcer ducks out of the shot, and the press pool edges in."""
    a = c.t - T_BELL
    s = c.st["announcer"]
    s["dy"] = int(80 * ease_in(clamp(a / 0.5, 0, 1)))
    if a > 0.5:
        s["hidden"] = True
    c.press = 0.45 * k_in(a - 0.4, 0.6) * k_in(T_V1 - c.t, 0.6)
    c.press_mood = "cheer"
    yield "back"
    spotlight(c.world, 230, C["red"], 1 - k_in(a, 0.4))
    spotlight(c.world, 92, C["blue"], 1 - k_in(a, 0.4))
    yield "ui"
    shout(c, 160, 28, "DING DING!", a, size=16, world=False, dur=1.2, top=C["gold_hi"], bottom=C["gold_sh"])


def yank_at(t):
    """How far the clasp has been yanked towards Trump (0-1) at time t."""
    k = 0.0
    for ty in T_YANKS:
        a = t - ty
        if 0 <= a < 0.9:
            k = max(k, ease_out(min(1.0, a / 0.12)) * (1 - ease_in_out(clamp((a - 0.45) / 0.45, 0, 1))))
    return k


@span(T_SHAKE - 0.3, T_LET_GO + 0.9)
def handshake(c, L):
    """The handshake, Trump style: he grabs, yanks Bibi half out of his chair, and pats the hand."""
    a = c.t - T_SHAKE
    yank = yank_at(c.t)
    pats = [c.t - tp for tp in T_PATS if 0 <= c.t - tp < 0.25]
    pat = 1.0 - pats[0] / 0.25 if pats else 0.0
    if T_PATS[0] <= c.t < T_PATS[-1] + 0.25:
        pat = max(pat, 0.35)
    let_go = c.t >= T_LET_GO
    pose(c, "trump", arms="chop" if not let_go else "thumb", lean=4, mouth="grit" if yank else "grin", eyes="squint",
         react=False)
    pose(c, "bibi", arms="chop" if not let_go else "palm", lean=3, react=False,
         eyes="wide" if yank or let_go else "half", mouth="o" if yank else "frown" if let_go else "smirk",
         brows="worried" if yank or let_go else "neutral")
    c.st["bibi"]["dx"] += int(round(7 * yank))
    if yank > 0.5:
        flash_press(c, ("yank", int(c.t > T_YANKS[1])), 4, c.t - T_YANKS[0])
    yield "ui"
    approach = ease_out(clamp((a + 0.3) / 0.6, 0, 1))
    k = k_in(a + 0.3, 0.25) * (1 - k_in(c.t - T_LET_GO - 0.4, 0.25))
    pic = P.handshake(40 + int(round(14 * yank)), approach=approach if not let_go else 1 - k_in(c.t - T_LET_GO, 0.2),
                      pat=pat, wince=let_go)
    inset(c, (118, 18, 202, 82), pic, "THE HANDSHAKE", k)
    for ty in T_YANKS:
        shout(c, 182, 26, "YANK!", c.t - ty, size=8, dur=0.6)
    for i, tp in enumerate(T_PATS):
        shout(c, 168 + 8 * i, 92, "PAT", c.t - tp, size=8, dur=0.35)


@span(T_CAMERAS, T_V1)
def for_the_cameras(c, L):
    """Then he turns to the cameras: two thumbs up, the accordion, a wink. Bibi checks his hand."""
    a = c.t - T_CAMERAS
    beat = int(a / B)
    arms = ("thumbs2", "thumbs2", "acc0", "acc2", "acc1", "acc2", "thumbs2", "point", "point")[min(beat, 8)]
    pose(c, "trump", arms=arms, lean=2, mouth="grin" if arms != "point" else "pout",
         eyes="shut" if arms == "point" and int(a * 4) % 4 == 0 else "squint", react=False)
    pose(c, "bibi", arms="chin", eyes="side", mouth="frown", brows="worried", react=False)
    flash_press(c, ("cam", beat), 3 if arms == "thumbs2" else 1, a % B)
    yield "ui"
