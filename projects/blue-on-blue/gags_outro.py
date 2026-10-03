"""Outro: Donnie calls. Trump is on speakerphone for Zohran; Zohran tells him Gavin says hi; Trump says
"Who?"; the lights go out on This Was Gavin Newsom. Then the end card."""
from gagkit import *  # noqa: F403

T_END = TL.section_start("end")


def on_the_line(c):
    """Zohran holds the phone up on speaker; Trump is in the inset."""
    hold(c, "mamdani", P.phone_held(), arms="hold")


@gag("outro", 0, pre=0.0)
def donnie_calls(c, L):
    a = L.t - L.t0
    buzz(c, a, dur=0.5)
    on_the_line(c)
    pose(c, "mamdani", eyes="open", mouth="grin", brows="up")
    pose(c, "newsom", eyes="side", brows="worried", mouth="frown", arms="clasp", react=False)
    talking = TL.loudness(L.t) > 0.12 and L.t <= L.t1 + 0.2
    mouth = V.mouth_for("trump", TL.loudness(L.t)) if talking else "pout"
    yield "ui"
    arms = ("acc0", "acc1", "acc2", "acc1")[int(L.t * 4) % 4]
    inset(c, INSET, P.trump_call(arms=arms, mouth=mouth, eyes="squint"), "DONNIE <3", k_in(a, 0.25))
    if a > 0:
        shout(c, 160, 96, "ZOHRAN!", a, size=8, world=False, dur=1.4)
    if a > 1.36:
        shout(c, 160, 96, "HANDSOME!", a - 1.36, size=8, world=False)


@gag("outro", 1)
def gavin_says_hi(c, L):
    a_hi, a_gav = age(L, "Hi"), age(L, "Gavin")
    on_the_line(c)
    if a_gav > -0.1:
        pose(c, "newsom", arms="wave", eyes="wide", brows="up", mouth="grin", lean=3, react=False)
    else:
        pose(c, "newsom", eyes="side", brows="worried", mouth="frown", arms="clasp", react=False)
    yield "ui"
    inset(c, INSET, P.trump_call(arms="desk", mouth="smile" if a_hi < 0.4 else "pout", eyes="squint"), "DONNIE <3")


@gag("outro", 2, post=0.0)
def who(c, L):
    a = L.t - L.t0
    on_the_line(c)
    pose(c, "mamdani", eyes="side", mouth="grin", brows="up")
    if a < 0.15:
        pose(c, "newsom", arms="wave", eyes="wide", brows="up", mouth="grin", lean=3, react=False)
    else:
        pose(c, "newsom", arms="clasp", eyes="half", brows="worried", mouth="frown", lean=0, react=False)
    if a > 0.3:
        c.shot = "newsom"
    c.neon_word, c.neon_color = "WAS", C["neon_red"]
    if a > 0.6:
        c.neon_lit = False
    yield "ui"
    if c.shot == "wide":                                               # the close-up is his face alone
        inset(c, INSET, P.trump_call(arms="shrug", mouth="o", eyes="squint", brows="up"), "DONNIE <3")
        shout(c, 160, 96, "WHO?", a, size=16, world=False)


@GAGS.span(T_END - 0.01, 200.0)
def end_card(c, L):
    a = c.t - T_END
    c.neon_word, c.neon_color, c.neon_lit = "WAS", C["neon_red"], False
    c.onair = False
    c.ring = 0.0
    c.subs = c.tag = c.bug = c.ticker = False
    pose(c, "newsom", arms="clasp", eyes="half", brows="worried", mouth="frown", react=False)
    pose(c, "mamdani", arms="desk", eyes="shut", mouth="grin", react=False)
    yield "front"
    blend(c.world, 1.0, (8, 10, 24), 0.55 * k_in(a, 0.5))
    yield "top"
    k = k_in(a - 0.2, 0.3)
    if k <= 0:
        return
    d = ImageDraw.Draw(c.ui)
    y = 46 - int((1 - ease_out(k)) * 20)
    pixel.outline_text(c.ui, (160, y), "BLUE ON BLUE", PRESS16, C["neon"], C["neon_glow"], anchor="ma")
    V.ui_text(c.ui, (160, y + 24), "ZOHRAN MAMDANI  VS  GAVIN NEWSOM", fill=C["white"], anchor="ma")
    if a > 0.8:
        V.ui_text(c.ui, (160, y + 34), "WITH DONALD TRUMP, ON SPEAKERPHONE", fill=C["dim"], anchor="ma")
    if a > 1.4:
        d.rounded_rectangle((112, y + 48, 208, y + 62), 3, fill=(16, 20, 40, 255), outline=INK + (255,))
        pixel.outline_text(c.ui, (160, y + 52), "THIS WAS GAVIN NEWSOM", SILK, C["neon_red"], (120, 30, 40), anchor="ma")
