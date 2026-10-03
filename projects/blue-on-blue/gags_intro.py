"""Intro: the host welcomes his guest, and warns him how the love story ends."""
from gagkit import *  # noqa: F403

MID = (160, 74)                     # between the two heads, under the neon sign


@gag("intro", 0, pre=1.0)
def welcome(c, L):
    a = L.t - L.t0
    if a < 0.15:                                                       # the lights come up as the show starts
        c.onair = False
        c.neon_lit = False
    elif a < 0.6:
        c.neon_flicker = True
    if age(L, "guest") > -0.1:                                         # "my guest": the host's hand, offered
        pose(c, "newsom", arms="palm", brows="up")
    else:
        pose(c, "newsom", arms="steeple")
    am = age(L, "mayor")
    if am > -0.2:
        pose(c, "mamdani", arms="wave", mouth="grin", eyes="shut" if am < 1.2 else "open", brows="up")
    yield "ui"
    if am > 0:
        P.sparkles(c.ui, *c.to_ui(240, 66), am, n=4, r=14)


@gag("intro", 1)
def love_story(c, L):
    a_love, a_end = age(L, "love"), age(L, "ends")
    pose(c, "newsom", arms="steeple", eyes="half", brows="angry", lean=3, mouth="smirk" if not V.singing(c, "newsom")
         else c.st["newsom"]["mouth"])
    if a_end > 0:
        pose(c, "mamdani", brows="up", eyes="side")
    yield "ui"
    if a_love < 0:
        return
    x, y = c.to_ui(*MID)
    if a_end < 0:
        pop_in(c.ui, scaled(P.heart(4), 2), x, y, a_love, dur=0.2)
        return
    k = min(1.0, a_end / 0.6)                                          # the heart cracks and the halves fall
    spr = scaled(P.heart(4, broken=min(1.0, a_end / 0.15)), 2)
    put(c.ui, spr, x, y + int(30 * k * k))
