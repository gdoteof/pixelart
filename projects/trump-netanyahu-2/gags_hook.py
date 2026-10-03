"""Hook: the press pool picks sides. Half of them chant BB GUN at Bibi, half TRUMP BABY at Trump."""
from gagkit import *  # noqa: F403

HOOK = TL.section_bounds("hook")


@span(*HOOK)
def press_pool(c, L):
    a = c.t - HOOK[0]
    left = HOOK[1] - c.t
    c.press = min(1.0, a / 0.5, max(0.0, left / 0.5))
    c.press_mood = "chant"
    yield "ui"


def chant(c, L, words, x, top, bottom):
    """The press pool's chant, a word to a row, over the side it is aimed at."""
    a = L.t - L.t0
    for i, w in enumerate(reversed(words)):
        shout(c, x, 112 - 18 * i, w, a - 0.08 * (len(words) - 1 - i), size=16, top=top, bottom=bottom,
              world=False, dur=2.0)


@gag("hook", 0)
def bb_gun(c, L):
    a = age(L, "pew")
    hold(c, "bibi", P.bb_gun(), arms="hold")
    pose(c, "bibi", mouth="grit", brows="angry", eyes="squint")
    yield "mid"
    if a > 0:
        for k in range(2):
            p = (a * 2.5 + k * 0.5) % 1.0
            x, y = lerp(108, 220, p), lerp(94, 76, p)
            ImageDraw.Draw(c.world).ellipse((x - 1, y - 1, x + 1, y + 1), fill=C["steel"])
    yield "ui"
    chant(c, L, ("BB GUN!",), 80, C["btie_hi"], C["blue"])
    shout(c, 120, 66, "PEW PEW", a, size=8, dur=1.2)


@gag("hook", 1)
def trump_baby(c, L):
    a = age(L, "waah")
    pose(c, "trump", mouth="wide", eyes="shut", brows="worried", arms="fist", react=False)
    yield "ui"
    chant(c, L, ("TRUMP", "BABY!"), 240, C["tskin_hi"], C["orange"])
    shout(c, 236, 66, "WAAH!", a, size=8, dur=1.2, top=C["white"], bottom=C["sweat"])


@gag("hook", 2)
def bb_gun_again(c, L):
    a = age(L, "pew")
    hold(c, "bibi", P.bb_gun(), arms="hold")
    pose(c, "bibi", mouth="grit", brows="angry", eyes="squint")
    flash_press(c, "hook2", 4, a)
    yield "mid"
    if a > 0:
        for k in range(3):
            p = (a * 2.5 + k / 3) % 1.0
            x, y = lerp(108, 220, p), lerp(94, 76, p)
            ImageDraw.Draw(c.world).ellipse((x - 1, y - 1, x + 1, y + 1), fill=C["steel"])
    yield "ui"
    chant(c, L, ("BB GUN!",), 80, C["btie_hi"], C["blue"])
    shout(c, 120, 66, "PEW PEW!", a, size=8, dur=1.2)


@gag("hook", 3)
def trump_baby_2(c, L):
    a = age(L, "waah")
    pose(c, "trump", mouth="wide", eyes="shut", brows="worried", arms="dance0" if int(c.t * 4) % 2 else "dance1",
         react=False)
    flash_press(c, "hook3", 6, a)
    yield "ui"
    chant(c, L, ("TRUMP", "BABY!"), 240, C["tskin_hi"], C["orange"])
    shout(c, 236, 66, "WAAH!", a, size=8, dur=1.2, top=C["white"], bottom=C["sweat"])
