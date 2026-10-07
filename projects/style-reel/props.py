"""The gag's furniture as Parts, for the styles that draw the puppets: Hasan's house, the tubs, the flag,
the flies. Everything is in board coordinates, 1000 wide by 720 high, and already in place for the time
asked for: a style maps the board onto its screen with placed() and decides what the parts look like.
"""
import math
from dataclasses import replace
from functools import lru_cache

import script as S
import sk
from puppet import PAL, Part

BOARD = (1000, 720)
PAL["prop"] = dict(
    wall=(246, 238, 222), wall_sh=(222, 208, 188), roof=(198, 96, 66), stone=(255, 251, 242), door=(122, 74, 50),
    window=(255, 214, 110), hedge=(84, 150, 88), trunk=(150, 108, 76), frond=(66, 150, 96), pole=(130, 132, 146),
    flag=(216, 40, 50), star=(255, 216, 70), tub=(252, 252, 254), tub_sh=(204, 212, 226), foot=(220, 174, 72),
    water=(140, 204, 240), bubble=(232, 244, 255), fly=(34, 30, 38), wing=(210, 226, 240), stink=(150, 172, 62))
TUB_X = [100 + 160 * i for i in range(6)]            # five, and the half
TUB_Y = 632
TUB_K = 1.12
STAMP = (790, 130, -8)                               # where "5 1/2 BATHS" is stamped, and its tilt
SCORE = dict(title=(500, 96), him=(40, 160, 480, 680), me=(520, 160, 960, 680))


def _p(name, path, col, line=2, shade=False, grp="house"):
    return Part(name, path, col, "prop", grp, line=line, shade=shade)


def _s(name, path, col, w, line=1, grp="house"):
    return Part(name, path, col, "prop", grp, line=line, open=True, w=w)


def placed(parts, m):
    """Parts moved by a matrix (board to screen, say): paths and stroke widths both."""
    k = math.sqrt(abs(m.getScaleX() * m.getScaleY() - m.getSkewX() * m.getSkewY()))
    return [replace(q, path=sk.xf(q.path, m=m), w=q.w * k) for q in parts]


def _palm(x, lean):
    top = (x + lean * 26, 196)
    out = [_s("trunk", sk.curve([(x, 500), (x - lean * 10, 380), (x + lean * 6, 280), top], closed=False), "trunk", 17,
              line=2, grp="palm")]
    for k, a in enumerate((-168, -128, -92, -52, -12, 24)):
        r = math.radians(a)
        tip = (top[0] + 118 * math.cos(r), top[1] + 96 * math.sin(r) + 30)
        mid = (top[0] + 70 * math.cos(r), top[1] + 70 * math.sin(r) - 12)
        nx, ny = -math.sin(r) * 15, math.cos(r) * 15
        leaf = sk.curve([(top[0], top[1], "c"), (mid[0] + nx, mid[1] + ny), (tip[0], tip[1], "c"), (mid[0] - nx, mid[1] - ny)])
        out.append(_p("frond", leaf, "frond", grp="palm"))
    return out


@lru_cache(maxsize=None)
def house():
    """Hasan's house, standing: two wings under tiled roofs, a portico, palms either side."""
    out = _palm(62, -1) + _palm(938, 1)
    for side in (-1, 1):
        def x(v):
            return 500 + side * v
        out.append(_p("wing", sk.rect(x(110), 270, x(392), 482), "wall"))
        out.append(_p("wing_sh", sk.rect(x(110), 270, x(392), 292), "wall_sh", line=0, shade=True))
        out.append(_p("roof", sk.poly([(x(96), 272), (x(136), 214), (x(380), 214), (x(412), 272)]), "roof"))
        for wx in (168, 286):
            arch = sk.union(sk.rect(x(wx), 352, x(wx + 58), 420), sk.oval(x(wx + 29), 352, 29, 30))
            out.append(_p("window", arch, "window", line=1))
            out.append(_s("bar", sk.poly([(x(wx + 29), 324), (x(wx + 29), 420)], closed=False), "wall_sh", 4, line=0))
    out.append(_p("block", sk.rect(358, 214, 642, 482), "wall"))
    out.append(_p("pediment", sk.poly([(332, 216), (500, 118), (668, 216)]), "stone"))
    out.append(_p("oculus", sk.oval(500, 180, 17), "window", line=1))
    out.append(_p("door", sk.union(sk.rect(468, 392, 532, 482), sk.oval(500, 392, 32, 34)), "door", line=1))
    for cx in (386, 440, 540, 594):
        out.append(_p("column", sk.rect(cx, 222, cx + 22, 482, 5), "stone", line=1))
    out.append(_p("steps", sk.rect(424, 480, 576, 500, 4), "stone", line=1))
    for side in (-1, 1):
        for k in range(5):
            out.append(_p("hedge", sk.oval(500 + side * (150 + k * 58), 486, 37, 24), "hedge", line=1, grp="hedge"))
    return tuple(out)


def flag(t):
    """The red flag: run up the pole from "austere", and flying."""
    up = S.ease_out(S.since("austere", t) / 0.45)
    if t < S.EV["austere"]:
        return []
    y0 = 112 + (22 - 112) * up
    wave = [9 * math.sin(7 * t + k * 1.3) for k in range(3)]
    cloth = sk.curve([(503, y0, "c"), (540, y0 - 5 + wave[0]), (584, y0 + wave[1], "c"), (586, y0 + 54 + wave[2], "c"),
                      (540, y0 + 48 + wave[0]), (503, y0 + 56, "c")])
    star = sk.poly([(537 + (12 if k % 2 == 0 else 5) * math.sin(k * math.pi / 5),
                     y0 + 27 + wave[0] * 0.6 - (12 if k % 2 == 0 else 5) * math.cos(k * math.pi / 5)) for k in range(10)])
    return [_s("pole", sk.poly([(500, 120), (500, 14)], closed=False), "pole", 6, line=2, grp="flag"),
            _p("flag", cloth, "flag", grp="flag"), _p("star", star, "star", line=0, grp="flag")]


@lru_cache(maxsize=None)
def tub(half=False):
    """A clawfoot bath with its bubbles, standing on (0, 40); or the left half of one, leaking."""
    out = []
    for fx in (-42, 42):
        out.append(_p("foot", sk.oval(fx, 38, 12, 9), "foot", line=1, grp="tub"))
    for bx, by, br in ((-34, -36, 13), (-10, -43, 16), (16, -37, 13), (36, -31, 9)):
        out.append(_p("bubble", sk.oval(bx, by, br), "bubble", line=1, grp="tub"))
    body = sk.curve([(-64, -18, "c"), (64, -18, "c"), (59, 12), (40, 35), (-40, 35), (-59, 12)])
    out.append(_p("tub", body, "tub", grp="tub"))
    out.append(_p("tub_sh", sk.minus(body, sk.xf(body, 0, -13)), "tub_sh", line=0, shade=True, grp="tub"))
    out.append(_p("rim", sk.rect(-71, -29, 71, -14, 7), "tub", grp="tub"))
    out.append(_s("tap", sk.poly([(57, -26), (57, -50), (40, -50)], closed=False), "pole", 6, line=2, grp="tub"))
    if not half:
        return tuple(out)
    keep = sk.poly([(-120, -90), (9, -90), (-3, -44), (11, -12), (-5, 14), (9, 46), (9, 90), (-120, 90)])
    cut = []
    for q in out:                                        # the left half of everything but the tap
        if q.open:
            continue
        path = sk.intersect(q.path, keep)
        if not path.isEmpty():
            cut.append(replace(q, path=path))
    for k, (dx, dy) in enumerate(((16, -6), (20, 18), (14, 40))):
        cut.append(_p("drop", sk.oval(dx, dy, 5 - k * 0.6, 7 - k * 0.6), "water", line=1, grp="tub"))
    return tuple(cut)


def tubs(t):
    """The tubs that have been counted by t: each drops in, squashes and stands."""
    out = []
    for i, x in enumerate(TUB_X):
        t0 = S.EV["tubs"][i] if i < 5 else S.EV["half"]
        if t < t0:
            continue
        age = (t - t0) / 0.26
        k = S.back(age, 2.4)
        squash = 0.22 * math.sin(min(1.0, age) * math.pi) * (1 - min(1.0, age))
        m = sk.matrix(x, TUB_Y - 40 - 46 * (1 - S.ease_out(age)), sx=TUB_K * k * (1 + squash), sy=TUB_K * k * (1 - squash),
                      about=(0.0, 40.0))
        out += placed(tub(i == 5), m)
    return out


def house_at(t):
    """The house as it comes up from the ground on "mansion's"."""
    if t < S.EV["mansion"]:
        return []
    age = S.since("mansion", t) / 0.42
    rise = (1 - S.ease_out(age)) * 470
    wob = 1 + 0.06 * math.sin(min(1.0, age) * math.pi * 2.5) * (1 - min(1.0, age))
    return placed(house(), sk.matrix(0, rise, sx=2 - wob, sy=wob, about=(500.0, 500.0)))


def me_score(t):
    """What the scoreboard says for Asmongold: "?" until he owns up, a blur of digits, then nought."""
    if t < S.EV["ive"]:
        return "?"
    if t < S.EV["had"]:
        return "9753186420"[int((t - S.EV["ive"]) * S.FPS / 2) % 10]
    return "0"


def flies(t):
    """[(x, y, wing 0..1, heading)] in heads from the middle of Asmongold's head: one from "I've", five by "year"."""
    homes = [(-1.05, -1.25), (1.0, -1.0), (0.15, -1.75), (-1.35, -0.25), (1.3, 0.2)]
    out = []
    for i, (cx, cy) in enumerate(homes):
        t0 = S.EV["ive"] + (0.0, 0.34, 0.62, 0.78, 0.92)[i]
        if t < t0:
            continue
        w = 5.2 + 0.9 * i
        x = cx + 0.34 * math.cos(w * t + i) + 0.10 * math.sin(2.3 * w * t)
        y = cy + 0.20 * math.sin(1.7 * w * t + 2 * i)
        k = S.ease_out((t - t0) / 0.4)
        x0, y0 = -3.4 - 0.3 * i, cy - 1.0 + 0.5 * i     # in from off the left of the frame
        x, y = x0 + (x - x0) * k, y0 + (y - y0) * k
        heading = math.degrees(math.atan2(math.cos(1.7 * w * t + 2 * i), -math.sin(w * t + i)))
        out.append((x, y, 0.5 + 0.5 * math.sin(60 * t + i), heading))
    return out


def fly(x, y, s, wing, heading=0.0):
    """One fly at a screen point, s pixels to the head."""
    m = sk.matrix(x, y, s, rot=heading * 0.25)
    body = sk.oval(0, 0, 0.075, 0.055)
    wings = [sk.xf(sk.oval(0, -0.075, 0.05, 0.085 - 0.04 * wing), rot=side * (28 + 30 * wing), about=(0.0, -0.01)) for side in (-1, 1)]
    return placed([_p("wing", wings[0], "wing", line=1, grp="fly"), _p("wing", wings[1], "wing", line=1, grp="fly"),
                   _p("fly", body, "fly", line=1, grp="fly")], m)


def stink(t):
    """[(open path in heads from the middle of Asmongold's head, strength 0..1)]: the smell, from "year"."""
    if t < S.EV["year"] - 0.25:
        return []
    out = []
    for i, (x, y) in enumerate(((-1.42, -0.55), (1.45, -0.75), (-0.55, -1.75), (0.75, -1.9))):
        age = t - (S.EV["year"] - 0.25) - 0.12 * i
        if age <= 0:
            continue
        rise = (age * 0.45) % 0.9
        pts = [(x + 0.085 * math.sin(k * 1.5 + i - t * 6), y - rise - k * 0.16) for k in range(6)]
        out.append((sk.curve(pts, closed=False), S.clamp(age / 0.3) * (1 - rise / 0.9) ** 0.6))
    return out
