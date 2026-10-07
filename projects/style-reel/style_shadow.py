"""Shadow theatre: black card puppets against a lamp-lit paper screen.

The two men are rod puppets in profile, jointed at the neck, the shoulders, the elbows and the jaw, and
all the detail is light cut through the card: an eye, strands of hair, stubble as pin-pricks, the house's
windows, the lettering. Nothing is drawn in a second colour except the flag, which is a piece of red gel.
How soft an edge is says how far the card is from the paper: things come up from below out of focus and
sharpen as they are pressed to the screen, and Hasan goes soft when he backs away from the smell.

The picture is light times what the card lets through: every sheet of card is drawn in black on a white
canvas (its cuts punched back out of it), blurred by its distance, and the lamp is multiplied by the result.
"""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image, ImageFilter

import script as S
import sk

NAME = "Shadow theatre"
W, H = S.W, S.H
GROUND = 930                                # the top of the playboard: everything stands behind it
E = S.EV
AMBIENT = 0.035                             # what reaches the paper where the card is in the way
TAU = 2 * math.pi


# --- geometry -----------------------------------------------------------------------------------

def tr(x, y):
    return np.array([[1.0, 0.0, x], [0.0, 1.0, y], [0.0, 0.0, 1.0]])


def rot(deg, cx=0.0, cy=0.0):
    """Clockwise on screen, about a point."""
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return tr(cx, cy) @ np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]) @ tr(-cx, -cy)


def scl(sx, sy=None, cx=0.0, cy=0.0):
    sy = sx if sy is None else sy
    return tr(cx, cy) @ np.array([[sx, 0.0, 0.0], [0.0, sy, 0.0], [0.0, 0.0, 1.0]]) @ tr(-cx, -cy)


def skm(m):
    return skia.Matrix.MakeAll(m[0, 0], m[0, 1], m[0, 2], m[1, 0], m[1, 1], m[1, 2], 0, 0, 1)


def at(m, x, y):
    v = m @ np.array([x, y, 1.0])
    return float(v[0]), float(v[1])


def letters(s, fnt, x, y, track=0.0, align="m"):
    """A string's outlines as one path, letter-spaced: lettering to cut out of a sign."""
    glyphs = fnt.textToGlyphs(s)
    widths = fnt.getWidths(glyphs)
    total = sum(widths) + track * (len(glyphs) - 1)
    x -= total / 2 if align == "m" else total if align == "r" else 0
    out = skia.Path()
    for g, w in zip(glyphs, widths):
        gp = fnt.getPath(g)
        if gp is not None:
            out.addPath(gp, x, y)
        x += w + track
    return out


def ring(x, y, r=8.0):
    """A pin joint: a ring pricked round the pivot. It is cut in both of the sheets the pin holds, and a ring
    about the pivot is the same ring however the joint turns, so the lamp always finds its way through."""
    return sk.oval(x, y, r), 2.6


# --- card ---------------------------------------------------------------------------------------

BLACK = sk.fill((0, 0, 0))
CUT = skia.Paint(AntiAlias=True, Color=skia.ColorBLACK, BlendMode=skia.BlendMode.kDstOut)


def _slit(w):
    p = sk.stroke((0, 0, 0), w)
    p.setBlendMode(skia.BlendMode.kDstOut)
    return p


def card(c, piece, m=None):
    """One sheet of card: its outline in black, with its cuts and slits let back through it. A cut goes
    through this sheet only, so where another sheet lies behind it no light comes."""
    path, cuts, slits = piece
    c.save()
    if m is not None:
        c.concat(skm(m))
    c.saveLayer(path.getBounds().makeOutset(6, 6), None)
    c.drawPath(path, BLACK)
    for q in cuts:
        c.drawPath(q, CUT)
    for q, w in slits:
        c.drawPath(q, _slit(w))
    c.restore()
    c.restore()


def soft(c, sigma, density=1.0):
    """Open a layer for everything at one distance from the paper: it comes back blurred by `sigma`, and
    thinned to `density` (a card carried right back to the lamp casts no shadow at all)."""
    p = skia.Paint()
    p.setAlphaf(S.clamp(density))
    if sigma > 0.05:
        p.setImageFilter(skia.ImageFilters.Blur(sigma, sigma))
    c.saveLayer(None, p)


def withdrawn(t, t0, dur=0.34):
    """How far a card has been drawn back off the paper since t0: (0..1, blur added, scale, density)."""
    d = S.smooth(S.ramp(t, t0, dur))
    return d, 16 * d, 1 + 0.22 * d, 1 - d ** 1.4


def rod(c, a, b, w=4.0, alpha=0.92):
    c.drawLine(a[0], a[1], b[0], b[1], sk.stroke((0, 0, 0), w, alpha))


# --- movement -----------------------------------------------------------------------------------

def swing(x):
    """How a jointed thing arrives: past the mark, back, and still."""
    return S.elastic(S.clamp(x) ** 1.2, 1.2, 5.0)


def loose(x):
    return S.elastic(S.clamp(x) ** 1.1, 1.9, 3.6)


def track(t, v0, keys, lag=0.0, slow=1.0, ease=swing):
    """A joint's angle at t: it rests at v0, and each key (start, value, seconds) swings it to a new value.
    `lag` and `slow` make the same moves late and long: what the far end of a limb does."""
    cur = None
    for ts, v, dur in keys:
        ts += lag
        if t < ts:
            break
        start = v0 if cur is None else cur[1] + (cur[2] - cur[1]) * ease((ts - cur[0]) / cur[3])
        cur = (ts, start, v, dur * slow)
    if cur is None:
        return v0
    return cur[1] + (cur[2] - cur[1]) * ease((t - cur[0]) / cur[3])


def rise(t, t0, dur=0.36, s=1.5):
    return 0.0 if t < t0 else S.back((t - t0) / dur, s)


def wobble(t, t0, amp, freq=2.6, damp=4.5):
    """A thing on a stick settling after it arrives."""
    a = t - t0
    return 0.0 if a < 0 else amp * math.exp(-damp * a) * math.sin(TAU * freq * a)


# --- hands and arms -----------------------------------------------------------------------------

@lru_cache(maxsize=None)
def hand(kind):
    """A hand hanging from the wrist at (0, 0): "point", "open" or "fist"."""
    palm = sk.oval(0, 17, 13, 18)
    thumb = sk.capsule((8, 10), (21, 25), 5.5, 4.5)
    if kind == "point":
        return sk.union(palm, thumb, sk.capsule((1, 28), (3, 62), 5.6, 4.4), sk.oval(-7, 31, 8, 8))
    if kind == "open":
        fingers = [sk.capsule((x0, 28), (x1, y1), 4.8, 3.8)
                   for x0, x1, y1 in ((-9, -19, 55), (-3, -7, 63), (4, 5, 63), (9, 16, 55))]
        return sk.union(palm, sk.capsule((9, 8), (27, 20), 5.5, 4.4), *fingers)
    return sk.union(sk.oval(0, 19, 15, 19), thumb)


@lru_cache(maxsize=None)
def arm_pieces(who):
    """(upper arm, forearm) as sheets hanging down from their joints."""
    if who == "asmon":
        L1, L2 = 130, 115
        upper = sk.union(sk.capsule((0, 0), (0, L1), 17, 13), sk.capsule((0, 0), (0, 58), 22, 21))   # and the sleeve
        hem = (sk.poly([(-20, 60), (20, 60)], False), 2.4)
        return ((upper, (), (hem, ring(0, 0, 8), ring(0, L1, 6))),
                (sk.capsule((0, 0), (0, L2), 13, 9.5), (), (ring(0, 0, 6),)))
    L1, L2 = 140, 122
    upper = sk.union(sk.capsule((0, 0), (0, L1), 41, 31), sk.oval(2, 12, 45, 42), sk.oval(5, 62, 36, 44))
    fore = sk.union(sk.capsule((0, 0), (0, L2), 31, 21), sk.oval(4, 34, 30, 40))
    return (upper, (), (ring(0, 0, 11), ring(0, L1, 9))), (fore, (), (ring(0, 0, 9),))


ARM = {"asmon": (130, 115, 1.25), "hasan": (140, 122, 1.45)}


def draw_arm(c, who, root, shoulder, a1, a2, kind):
    """An arm from the shoulder: a1 swings the upper arm forward from hanging, a2 bends the elbow on from
    there. Returns where the wrist is on the stage, for the rod."""
    L1, L2, hs = ARM[who]
    upper, fore = arm_pieces(who)
    m1 = root @ tr(*shoulder) @ rot(-a1)
    m2 = m1 @ tr(0, L1) @ rot(-a2)
    card(c, (sk.xf(hand(kind), 0, L2 - 4, hs), (), ()), m2)
    card(c, fore, m2)
    card(c, upper, m1)
    return at(m2, 0, L2 + 6)


# --- Asmongold ----------------------------------------------------------------------------------

AS = dict(neck=(30, -455), head=(50, -600), jaw=(-8, 44), tail=(-100, 58), sh_f=(104, -360), sh_b=(-96, -360))


@lru_cache(maxsize=None)
def asmon_head():
    skull = sk.curve([(20, -144), (52, -134), (78, -112), (92, -78), (97, -45), (100, -30), (90, -16), (104, 10), (122, 36),
                      (134, 51, "c"), (118, 61), (102, 60, "c"), (107, 72), (101, 81, "c"), (52, 85, "c"),
                      (54, 120), (10, 140), (-60, 130), (-100, 60), (-112, -20), (-100, -90), (-50, -132)])
    hair = sk.curve([(24, -141, "c"), (20, -157), (-18, -166), (-62, -156), (-112, -114), (-134, -40), (-130, 40),
                     (-104, 76, "c"), (-60, 60), (-20, 20), (-10, -60), (4, -120)])           # it starts well back
    band = sk.capsule((-24, -40), (-20, -166), 11)                      # the headphones: over the top,
    cup = sk.oval(-24, -4, 36, 42)                                      # and the cup on the ear
    eye = sk.xf(sk.minus(sk.curve([(-18, 1), (-6, -6), (9, -5), (18, 4), (6, 9), (-9, 7)]), sk.oval(6, -4, 6.5, 8)),
                66, -24, rot=10)
    slits = [(sk.oval(-24, -4, 23, 28), 4.5), (sk.oval(-24, -4, 9, 11), 2.5),
             (sk.poly([(-36, -46), (-33, -150)], False), 2.4), (sk.poly([(-13, -46), (-9, -150)], False), 2.4),
             (sk.curve([(53, -11), (65, -5), (79, -10)], False), 2.0),               # the bag under the eye
             (sk.curve([(-48, -146), (-94, -112), (-118, -44), (-116, 36)], False), 2.6),   # strands, going back
             (sk.curve([(-46, -128), (-80, -96), (-98, -40), (-98, 36)], False), 2.2),
             (sk.curve([(-50, -108), (-70, -70), (-78, -20)], False), 2.0),
             (sk.curve([(14, -150), (2, -155), (-8, -155)], False), 2.2), ring(*AS["jaw"], 5.5)]
    return sk.union(skull, hair, band, cup), (eye,), tuple(slits)


@lru_cache(maxsize=None)
def asmon_jaw():
    jaw = sk.curve([(-34, 30), (52, 82, "c"), (100, 78, "c"), (106, 94), (100, 104), (109, 118),
                    (122, 140, "c"), (109, 146, "c"), (124, 170, "c"), (107, 174, "c"), (118, 198, "c"), (99, 198, "c"),
                    (104, 226, "c"), (87, 208, "c"), (79, 228, "c"), (67, 204, "c"), (55, 216, "c"), (47, 190, "c"),
                    (31, 198, "c"), (27, 172, "c"), (9, 174, "c"), (2, 150), (-20, 128), (-44, 96), (-46, 56)])
    hairs = [((96, 132), (100, 160)), ((84, 124), (90, 186)), ((70, 128), (78, 196)), ((56, 130), (62, 188)),
             ((42, 132), (44, 170)), ((28, 134), (26, 158)), ((104, 164), (108, 188))]
    return jaw, (), tuple((sk.poly(list(h), False), 2.0) for h in hairs) + (ring(*AS["jaw"], 5.5),)


@lru_cache(maxsize=None)
def asmon_tail():
    """The hair down his back: a sheet of its own, hung from the nape, so it swings after the head."""
    tail = sk.curve([(-36, -34), (30, -40), (38, 40), (22, 120), (2, 196), (-6, 236, "c"), (-20, 206, "c"),
                     (-30, 246, "c"), (-44, 212, "c"), (-58, 250, "c"), (-68, 210, "c"), (-86, 236, "c"),
                     (-88, 186, "c"), (-76, 110), (-58, 30)])
    strands = [sk.curve([(x, -24), (x + 6, 50), (x - 8, 130), (x - 24, 198)], False) for x in (-22, -2, 16)]
    return tail, (), tuple((s, 2.4) for s in strands)


@lru_cache(maxsize=None)
def asmon_torso():
    body = sk.curve([(8, -500), (64, -492), (72, -394), (122, -374), (130, -340), (110, -200), (100, 120, "c"),
                     (-92, 120, "c"), (-102, -200), (-120, -340), (-112, -374), (-30, -394)])
    neckline = sk.curve([(-26, -388), (22, -364), (70, -388)], False)
    return body, (), ((neckline, 2.6), ring(*AS["neck"], 6.5), ring(*AS["sh_f"], 8), ring(*AS["sh_b"], 8))


# --- Hasan --------------------------------------------------------------------------------------

HA = dict(neck=(22, -470), head=(35, -592), jaw=(-14, 36), sh_f=(170, -385), sh_b=(-162, -385))


@lru_cache(maxsize=None)
def hasan_head():
    skull = sk.curve([(44, -112), (76, -96), (92, -62), (99, -44), (102, -34), (92, -20), (112, 12), (124, 30),
                      (129, 41, "c"), (114, 51), (102, 50, "c"), (108, 62), (102, 71, "c"), (56, 75, "c"),
                      (58, 108), (10, 124), (-66, 112), (-104, 50), (-112, -24), (-98, -84), (-50, -116)])
    quiff = sk.curve([(46, -110, "c"), (70, -132), (96, -160), (90, -196), (50, -216), (-14, -208), (-72, -182),
                      (-110, -130), (-122, -66), (-112, -14, "c"), (-96, -30), (-60, -90), (0, -112)])
    eye = sk.xf(sk.minus(sk.curve([(-17, 2), (-8, -7), (10, -7), (18, -1), (8, 7), (-8, 7)]), sk.oval(7, -5, 6.5, 8.5)),
                68, -23, rot=-6)
    lip = [sk.oval(x, y, 2.0) for x, y in ((84, 58), (93, 57), (76, 62), (88, 65), (68, 64))]
    slits = [(sk.curve([(52, -41), (70, -44), (90, -38)], False), 2.6),             # over the heavy brow
             (sk.curve([(70, -124), (84, -160), (62, -194), (10, -200)], False), 2.8),   # the hair, swept up and back
             (sk.curve([(44, -120), (44, -160), (6, -182), (-56, -168)], False), 2.4),
             (sk.curve([(10, -124), (-30, -146), (-84, -122)], False), 2.2),
             (sk.curve([(-10, -30), (-26, -24), (-28, -6), (-16, 6)], False), 2.4),      # the ear
             (sk.curve([(-12, -18), (-18, -10), (-14, -2)], False), 1.8), ring(*HA["jaw"], 5.5)]
    return sk.union(skull, quiff), (eye, *lip), tuple(slits)


@lru_cache(maxsize=None)
def hasan_jaw():
    jaw = sk.curve([(-36, 24), (56, 72, "c"), (101, 68, "c"), (106, 82), (99, 93), (108, 107), (108, 128),
                    (97, 142, "c"), (40, 150), (2, 138, "c"), (-22, 100), (-44, 56)])
    dots = []
    for row in range(8):                                                # stubble: pin-pricks along the jaw
        for col in range(14):
            x, y = 2 + col * 8.5 + (4 if row % 2 else 0), 84 + row * 8.0
            edge = all(jaw.contains(x + dx, y + dy) for dx, dy in ((7, 0), (-7, 0), (0, 7), (0, -7)))
            if edge and x - 0.9 * (y - 84) > 4:                          # the cheek above the beard line stays whole
                dots.append(sk.oval(x, y, 1.9))
    return jaw, tuple(dots), (ring(*HA["jaw"], 5.5),)


@lru_cache(maxsize=None)
def hasan_torso():
    body = sk.curve([(-22, -520), (66, -506), (74, -450), (150, -424), (190, -400), (192, -330), (152, -180),
                     (126, -60), (130, 120, "c"), (-118, 120, "c"), (-114, -60), (-142, -180), (-184, -330),
                     (-182, -400), (-142, -424), (-40, -454)])
    neckline = sk.curve([(-38, -448), (-22, -392), (18, -364), (58, -392), (72, -446)], False)
    armholes = [sk.curve([(s * 116 + 4, -428), (s * 112 + 4, -380), (s * 134 + 4, -330), (s * 178 + 4, -302)], False)
                for s in (-1, 1)]
    chain_line = sk.curve([(-26, -446), (-10, -404), (18, -386), (46, -404), (60, -444)], False)
    chain = [sk.oval(*sk.along(chain_line, i / 15)[0], 2.3) for i in range(16)]
    pendant = sk.poly([(18, -380), (25, -370), (18, -358), (11, -370)])
    return body, (*chain, pendant), ((neckline, 2.8), (armholes[0], 2.6), (armholes[1], 2.6), ring(*HA["neck"], 7),
                                     ring(*HA["sh_f"], 11), ring(*HA["sh_b"], 11))


# --- acting -------------------------------------------------------------------------------------

A_ARM1 = (18, [(67.62, 80, 0.55), (68.66, 112, 0.5), (69.60, 126, 0.45), (70.02, 62, 0.5), (70.70, 108, 0.55),
               (72.30, 38, 0.5), (73.02, 95, 0.5)])
A_ARM2 = (28, [(67.62, 24, 0.6), (68.66, 10, 0.5), (69.60, 8, 0.45), (70.02, 78, 0.5), (70.70, 12, 0.55),
               (72.30, -100, 0.5), (73.02, 30, 0.55)])
A_BARM1 = (-8, [(70.02, -38, 0.5), (70.70, -10, 0.5), (73.02, -48, 0.55)])
A_BARM2 = (-14, [(70.02, -125, 0.5), (70.70, -16, 0.5), (73.02, -118, 0.6)])
A_HEAD = (0, [(68.05, 5, 0.4), (68.66, -9, 0.4), (70.02, 2, 0.4), (70.70, -7, 0.4), (72.30, 4, 0.4), (73.02, -13, 0.5)])
A_LEAN = (0, [(67.62, 3, 0.6), (70.02, -2, 0.6), (70.70, 2.5, 0.6), (72.30, 0, 0.5), (73.02, -4, 0.6)])

H_ARM1 = (12, [(68.05, 34, 0.55), (70.20, 14, 0.6), (73.02, 80, 0.42)])
H_ARM2 = (24, [(68.05, 92, 0.6), (70.20, 34, 0.6), (73.02, 92, 0.45)])
H_BARM1 = (-36, [(73.02, -84, 0.5)])
H_BARM2 = (100, [(73.02, -28, 0.55)])
H_HEAD = (0, [(68.05, -5, 0.4), (69.60, -10, 0.4), (70.20, 9, 0.5), (70.74, -7, 0.5), (72.62, -12, 0.3), (73.02, -20, 0.4)])
H_LEAN = (0, [(68.05, -2, 0.5), (70.20, 3, 0.6), (70.74, 0, 0.5), (72.62, -3, 0.3), (73.02, -10, 0.45)])
H_AWAY = (0, [(73.02, 1, 0.5)])                                          # backing off the paper


def asmon(c, t):
    lean = track(t, *A_LEAN) + 0.6 * math.sin(TAU * t / 2.9)
    head = track(t, *A_HEAD) - 2.2 * S.thump(t, 9) * S.singing(t)
    bob = 5 * S.thump(t, 8) if S.singing(t) else 0.0
    jaw = 20 * S.mouth(t)["h"]
    tail = 1.3 * (track(t, *A_HEAD, lag=0.10, slow=1.7, ease=loose) - head) \
        + 2.0 * (track(t, *A_LEAN, lag=0.12, slow=1.7, ease=loose) - lean) + 1.2 * math.sin(TAU * t / 2.3 + 1)
    front = "open" if 70.02 <= t < 70.70 or t >= 73.02 else "fist" if 72.30 <= t < 73.02 else "point"
    back = "open" if 70.02 <= t < 70.70 or t >= 73.02 else "fist"
    press = 1 - 0.5 * S.smooth(S.ramp(t, 73.0, 0.4))                     # he comes up to the paper for the brag

    soft(c, 1.5 * press)
    root = tr(300, GROUND + bob) @ rot(lean)
    hm = root @ rot(head, *AS["neck"]) @ tr(*AS["head"])
    wrists = [draw_arm(c, "asmon", root, AS["sh_b"], track(t, *A_BARM1), track(t, *A_BARM2, lag=0.07, ease=loose), back)]
    card(c, asmon_tail(), hm @ tr(*AS["tail"]) @ rot(tail))
    card(c, asmon_torso(), root)
    card(c, asmon_jaw(), hm @ rot(jaw, *AS["jaw"]))
    card(c, asmon_head(), hm)
    wrists.append(draw_arm(c, "asmon", root, AS["sh_f"], track(t, *A_ARM1), track(t, *A_ARM2, lag=0.07, ease=loose), front))
    for k, (x, y) in enumerate(wrists):
        rod(c, (x, y), (x + (60 if k else -40), H + 60), 3.6)
    c.restore()


def hasan(c, t):
    lean = track(t, *H_LEAN) + 0.5 * math.sin(TAU * t / 3.3 + 2)
    head = track(t, *H_HEAD) + 2.0 * sum(math.exp(-((t - u - 0.06) / 0.05) ** 2) for u in E["tubs"])
    away = track(t, *H_AWAY, ease=S.smooth)
    jaw = track(t, 0, [(72.66, 5, 0.25), (73.02, 15, 0.35)])
    a2 = track(t, *H_ARM2, lag=0.06, ease=loose)
    if t > 73.3:
        a2 += 11 * math.sin(TAU * 4.5 * (t - 73.3)) * S.smooth(S.ramp(t, 73.3, 0.15))    # fanning the air
    front = "open" if 68.05 <= t < 70.20 or t >= 73.02 else "fist"

    soft(c, 1.5 + 2.0 * away)
    root = tr(1610, GROUND) @ scl(-(1 + 0.035 * away), 1 + 0.035 * away) @ rot(lean)
    hm = root @ rot(head, *HA["neck"]) @ tr(*HA["head"])
    wrists = [draw_arm(c, "hasan", root, HA["sh_b"], track(t, *H_BARM1), track(t, *H_BARM2, lag=0.06, ease=loose),
                       "open" if t >= 73.02 else "fist")]
    card(c, hasan_torso(), root)
    card(c, hasan_jaw(), hm @ rot(jaw, *HA["jaw"]))
    card(c, hasan_head(), hm)
    wrists.append(draw_arm(c, "hasan", root, HA["sh_f"], track(t, *H_ARM1), a2, front))
    for k, (x, y) in enumerate(wrists):
        rod(c, (x, y), (x + (-70 if k else 40), H + 60), 4.2)
    c.restore()


# --- the house and what comes up over it --------------------------------------------------------

def _arch(x, y, w, h):
    """A round-headed opening standing on y."""
    return sk.union(sk.rect(x - w / 2, y - h + w / 2, x + w / 2, y), sk.oval(x, y - h + w / 2, w / 2))


def _glazed(opening, x, y, w, h, across=1):
    """A window: the opening less its glazing bars."""
    bars = [sk.rect(x - 1.6, y - h, x + 1.6, y)]
    bars += [sk.rect(x - w / 2, y - h * k / (across + 1) - 1.6, x + w / 2, y - h * k / (across + 1) + 1.6)
             for k in range(1, across + 1)]
    for b in bars:
        opening = sk.minus(opening, b)
    return opening


@lru_cache(maxsize=None)
def mansion():
    walls = [sk.rect(-270, -170, 270, 60), sk.rect(-150, -240, 150, 60),
             sk.poly([(-176, -238), (0, -306), (176, -238)]), sk.rect(-176, -250, 176, -236),
             sk.rect(-286, -184, -140, -168), sk.rect(140, -184, 286, -168),
             sk.rect(-22, -338, 22, -296), sk.oval(0, -338, 27, 17), sk.rect(-2.5, -430, 2.5, -338),
             sk.rect(-240, -214, -214, -170), sk.rect(206, -208, 232, -170),
             sk.rect(-246, -222, -208, -212), sk.rect(200, -216, 238, -206)]
    walls += [sk.oval(s * x, -4, r, r * 0.62) for s in (-1, 1) for x, r in ((196, 34), (240, 40), (290, 30))]
    for s in (-1, 1):                                                   # a clipped bay tree each side
        walls += [sk.oval(s * 318, -44, 22), sk.rect(s * 318 - 3, -30, s * 318 + 3, 30)]
    cuts = [_arch(x, -16, 54, 150) for x in (-84, 0, 84)]                # the loggia
    cuts += [_glazed(sk.rect(x - 21, -226, x + 21, -188), x, -188, 42, 38) for x in (-84, 0, 84)]
    cuts += [_glazed(_arch(s * x, -44, 36, 96), s * x, -44, 36, 96, 2) for s in (-1, 1) for x in (178, 236)]
    cuts += [_glazed(sk.oval(0, -266, 15), 0, -251, 30, 30)]
    cuts += [sk.rect(s * x - 3.5, -182, s * x + 3.5, -172) for s in (-1, 1) for x in range(152, 280, 14)]   # balustrades
    slits = [(sk.poly([(-150, -176), (150, -176)], False), 2.2), (sk.poly([(-22, -302), (22, -302)], False), 2.0)]
    return sk.union(*walls), tuple(cuts), tuple(slits)


@lru_cache(maxsize=None)
def palm(lean):
    """A palm on (0, 0), its crown at (lean, -250)."""
    h = 250
    spine = sk.curve([(0, 0), (lean * 0.15, -h * 0.4), (lean * 0.6, -h * 0.8), (lean, -h)], False)
    left, right = [], []
    for i in range(13):
        (x, y), a = sk.along(spine, i / 12)
        nx, ny = math.cos(math.radians(a + 90)), math.sin(math.radians(a + 90))
        w = 8.5 - 3.6 * i / 12 + (1.4 if i % 2 else 0)                    # the rings of the trunk
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    parts = [sk.poly(left + right[::-1]), sk.oval(lean - 6, -h + 4, 7), sk.oval(lean + 7, -h + 6, 6.5)]
    for k, a in enumerate((-172, -146, -118, -92, -66, -38, -10, 22, 160)):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        length = 82 - 8 * abs(math.sin(math.radians(a + 90))) * (k % 2)
        tip = (lean + length * ca, -h + length * sa + 34 + 16 * abs(ca))
        mid = (lean + 0.55 * length * ca, -h + 0.55 * length * sa - 10)
        top, under = [], []
        for i in range(13):
            u = i / 12
            x = (1 - u) ** 2 * lean + 2 * u * (1 - u) * mid[0] + u * u * tip[0]
            y = (1 - u) ** 2 * -h + 2 * u * (1 - u) * mid[1] + u * u * tip[1]
            top.append((x, y - 2.2 * (1 - u)))
            under.append((x + (2 if i % 2 else 0) * ca, y + (4 if i % 2 == 0 else 5 + 17 * (1 - 0.55 * u))))   # leaflets
        parts.append(sk.poly(top + under[::-1]))
    return sk.union(*parts), (), ()


@lru_cache(maxsize=None)
def tub(half):
    """A roll-top bath on claw feet, tap end to the left, with its suds; or the tap end of one, sawn off."""
    parts = [sk.curve([(-76, -24, "c"), (-73, 0), (-56, 21), (0, 27), (56, 21), (73, 0), (76, -24, "c")]),
             sk.capsule((-86, -26), (86, -26), 7),
             sk.capsule((-64, -28), (-64, -54), 4.4), sk.capsule((-64, -54), (-55, -65), 4.4),       # the swan neck
             sk.capsule((-55, -65), (-43, -60), 4.4), sk.capsule((-43, -60), (-41, -50), 4.4, 5.2),
             sk.capsule((-64, -40), (-76, -40), 3.0), sk.oval(-78, -40, 5.5)]
    for s in (-1, 1):
        parts.append(sk.curve([(s * 56, 16), (s * 38, 24), (s * 43, 36), (s * 58, 44), (s * 70, 39), (s * 60, 31)]))
    suds = ((14, -44, 15), (38, -38, 11), (-10, -40, 10), (26, -62, 9), (56, -35, 8), (2, -58, 7), (-26, -35, 7))
    parts += [sk.oval(x, y, r) for x, y, r in suds]
    path = sk.union(*parts)
    cuts = [sk.oval(x - r * 0.3, y - r * 0.3, r * 0.26) for x, y, r in suds[:4]]
    slits = [(sk.curve([(-58, -8), (-44, 9), (-12, 15)], False), 3.0)]
    if half:
        saw = [(-200, -200), (2, -200), (2, -80), (10, -34), (-3, -23), (9, -12), (-3, -1), (9, 10), (-3, 21), (6, 34),
               (-200, 80)]
        drips = [sk.union(sk.oval(x, y, r), sk.poly([(x - r * 0.8, y - r * 0.5), (x, y - r * 2.4), (x + r * 0.8, y - r * 0.5)]))
                 for x, y, r in ((20, 26, 4.5), (30, 6, 3.2), (17, 48, 3.4))]
        path = sk.union(sk.intersect(path, sk.poly(saw)), *drips)
    return path, tuple(cuts), tuple(slits)


TUBS = [(772, 292), (960, 292), (1148, 292), (866, 412), (1054, 412)]
HALF = (1222, 412)
FONT = "book"


@lru_cache(maxsize=None)
def banner():
    """5 1/2 BATHS, on a swallow-tailed strip hung from the top of the stage by two threads."""
    strip = sk.union(sk.rect(-196, 40, 196, 116),
                     sk.poly([(-190, 40), (-248, 40), (-224, 78), (-248, 116), (-190, 116)]),
                     sk.poly([(190, 40), (248, 40), (224, 78), (248, 116), (190, 116)]))
    words = letters("5½ BATHS", sk.font(FONT, 58), 0, 99, 5)
    edge = [(sk.poly([(-186, y), (186, y)], False), 1.8) for y in (47, 109)]
    return strip, (words,), tuple(edge)


@lru_cache(maxsize=None)
def board():
    """The scoreboard, hung from (0, 0): BATHS THIS YEAR, HIM 5 1/2, and ME. His number is cut by the caller:
    it turns over."""
    plaque = sk.union(sk.rect(-285, 34, 285, 350, 20), sk.oval(0, 40, 168, 30),
                      sk.rect(-240, 16, -220, 50, 4), sk.rect(220, 16, 240, 50, 4))
    cuts = [letters("BATHS THIS YEAR", sk.font(FONT, 44), 0, 96, 6),
            letters("HIM", sk.font(FONT, 34), -142, 176, 8), letters("ME", sk.font(FONT, 34), 142, 176, 8),
            letters("5½", sk.font(FONT, 136), -142, 306, 2)]
    slits = [(sk.rect(-271, 48, 271, 336, 12), 2.2), (sk.poly([(-236, 122), (236, 122)], False), 2.4),
             (sk.poly([(0, 142), (0, 322)], False), 2.4)]
    return plaque, tuple(cuts), tuple(slits)


@lru_cache(maxsize=None)
def numeral(ch):
    return letters(ch, sk.font(FONT, 136), 0, 0)


def house(c, t):
    """The mansion and its palms: up from behind the playboard on "mansion's"."""
    if t < E["mansion"]:
        return
    up = rise(t, E["mansion"], 0.52, 1.1)
    soft(c, 1.3 + 5.0 * (1 - S.clamp(up)))
    for x, lean, late in ((795, -20, 0.10), (1125, 20, 0.17)):
        k = rise(t, E["mansion"] + late, 0.5, 1.4)
        sway = wobble(t, E["mansion"] + late + 0.2, 5.0, 1.7, 2.6) + 0.8 * math.sin(TAU * t / 3.1 + x)
        card(c, palm(lean), tr(x, GROUND - 60 + (1 - k) * 420) @ rot(sway))
    card(c, mansion(), tr(960, GROUND + (1 - up) * 460))
    c.restore()


def flag(c, t):
    """The red flag, run up the pole on "austere": the one piece of colour, a gel with a star cut in it."""
    if t < E["austere"]:
        return
    k = S.ease_out(S.ramp(t, E["austere"], 0.42), 2)
    x0, y0 = 962.5, GROUND - 344 - 84 * k
    top, bottom = [], []
    for i in range(17):
        u = i / 16
        dy = (4 + 9 * u) * math.sin(TAU * (1.3 * u - 2.1 * t)) * u ** 0.6
        top.append((x0 + 98 * u, y0 + dy - 3 * u))
        bottom.append((x0 + 98 * u, y0 + 62 + dy + 2 * u))
    star = [(x0 + 30 + r * math.sin(TAU * i / 10), y0 + 27 - r * math.cos(TAU * i / 10) + 4 * math.sin(TAU * (0.4 - 2.1 * t)))
            for i in range(10) for r in ((15, 6.2)[i % 2],)]
    soft(c, 1.1)
    c.saveLayer(None, skia.Paint(BlendMode=skia.BlendMode.kMultiply))
    c.drawPath(sk.poly(top + bottom[::-1]), sk.fill((232, 44, 30), 0.93))
    c.drawPath(sk.poly(star), CUT)
    c.restore()
    c.restore()


def baths(c, t):
    """The count: five tubs up on sticks inside the word "five", half a one on "half", then the banner."""
    gone = E["line2"] - 0.04
    for i, ((x, y), t0) in enumerate(zip(TUBS + [HALF], (*E["tubs"], E["half"]))):
        if t < t0:
            continue
        up = rise(t, t0, 0.34, 1.8)
        d, blur, grow, density = withdrawn(t, gone + 0.02 * i)
        if d >= 1:
            continue
        yy = y + (1 - up) * (GROUND + 90 - y) + 30 * d
        lean = wobble(t, t0 + 0.12, 7.0, 2.8, 4.0) + 0.7 * math.sin(TAU * t / 2.1 + i * 1.7)
        soft(c, 1.2 + 4.5 * (1 - S.clamp(up)) + blur, density)
        m = tr(x, GROUND + 60) @ rot(lean) @ tr(0, yy - GROUND - 60) @ scl(0.86 * grow)   # the stick is held below
        rod(c, at(m, 0, 24), (x, GROUND + 60), 4.0)
        card(c, tub(i == 5), m)
        c.restore()

    if t >= E["baths"]:
        d, blur, grow, density = withdrawn(t, gone)
        if d < 1:
            a = t - E["baths"]
            y = -230 * (1 - S.bounce(a / 0.5))
            sway = wobble(t, E["baths"] + 0.1, 2.4, 1.9, 3.2)
            soft(c, 1.2 + blur, density)
            m = tr(960, 58 + y) @ rot(sway) @ scl(grow, grow, 0, 78)
            for sx in (-176, 176):
                rod(c, at(m, sx, 42), at(m, sx, -80), 2.2)
            card(c, banner(), m)
            c.restore()


def scoreboard(c, t):
    """BATHS THIS YEAR, let down on two threads for the second line. His number rolls from "I've" and
    turns over to nought on "had"."""
    if t < E["line2"]:
        return
    a = t - E["line2"]
    down = S.back(a / 0.55, 1.2)
    sway = wobble(t, E["line2"] + 0.12, 2.0, 1.5, 2.6)
    m = tr(960, 72 - 540 * (1 - down)) @ rot(sway)
    plaque, cuts, slits = board()
    if t < E["had"]:
        k = S.ramp(t, E["had"] - 0.09, 0.09)
        roll = 12 * math.sin(TAU * 3.1 * (t - E["ive"])) * S.smooth(S.ramp(t, E["ive"], 0.12)) if t > E["ive"] else 0.0
        glyph, sy = numeral("?"), 1 - k
    else:
        glyph, sy, roll = numeral("0"), S.back(S.ramp(t, E["had"], 0.22), 2.4), 0.0
    me = sk.xf(glyph, m=skm(tr(142, 306) @ rot(roll, 0, -48) @ scl(1, max(sy, 0.02), 0, -48)))
    soft(c, 1.2 + 4.0 * (1 - S.clamp(down)))
    for sx in (-230, 230):
        rod(c, at(m, sx, 20), at(m, sx, -520), 2.2)
    card(c, (plaque, cuts + (me,), slits), m)
    c.restore()


# --- the flies and the smell --------------------------------------------------------------------

FLIES = [(0.00, 150, 110, 1.9, 2.7, 0.3), (0.52, 190, 90, 2.3, 1.7, 1.9), (0.66, 120, 140, 1.6, 2.9, 3.4),
         (0.78, 210, 120, 2.6, 2.1, 5.0), (0.90, 90, 80, 3.1, 2.4, 0.9), (1.02, 170, 150, 1.4, 3.3, 4.2)]


def flies(c, t):
    """They find him on "I've", and the rest are there by "year": each on its own wire from below."""
    for k, (late, ax, ay, fx, fy, ph) in enumerate(FLIES):
        t0 = E["ive"] + late
        if t < t0:
            continue
        a = t - t0
        up = S.ease_out(a / 0.45, 2)
        x = 400 + ax * math.sin(TAU * fx * a / 2.2 + ph) + 24 * math.sin(TAU * 5.3 * a + k)
        y = 290 + ay * math.sin(TAU * fy * a / 2.2 + ph * 1.7) + (1 - up) * 560
        depth = 0.5 + 0.5 * math.sin(TAU * a * 0.9 + k * 2.1)
        soft(c, 0.9 + 2.6 * depth)
        size = 1.8 + 0.4 * depth
        wire = sk.curve([(x, y), (x - 20 + 10 * math.sin(a * 5 + k), y + 150), (330 + k * 22, GROUND + 40)], False)
        c.drawPath(wire, sk.stroke((0, 0, 0), 1.5, 0.5))
        flap = 1 if (S.frame_no(t) + k) % 2 else -1
        body = sk.union(sk.oval(x, y, 8 * size, 5.5 * size), sk.oval(x + 8 * size, y - 1, 4 * size))
        wings = [sk.xf(sk.oval(x - 2, y - 9 * size, 4.2 * size, 10 * size), rot=s * (28 + 22 * flap), about=(x - 2, y - 2))
                 for s in (-1, 1)]
        c.drawPath(body, BLACK)
        for w in wings:
            c.drawPath(w, sk.fill((0, 0, 0), 0.55))
        c.restore()


def smell(c, t):
    """What comes off him, from "year": ribbons of tissue, so they only grey the light."""
    t0 = E["year"] - 0.06
    if t < t0:
        return
    soft(c, 2.6)
    for k, (x, y0, tall) in enumerate(((150, 560, 300), (250, 300, 190), (470, 540, 250), (560, 600, 300))):
        a = t - t0 - 0.07 * k
        if a <= 0:
            continue
        grow = S.ease_out(a / 0.6, 2)
        pts = []
        for i in range(15):
            u = i / 14
            yy = y0 - u * tall * grow
            pts.append((x + (9 + 9 * u) * math.sin(TAU * (1.6 * u - 1.1 * t) + k * 1.9) - 14 * u, yy))
        c.drawPath(sk.curve(pts, False), sk.stroke((0, 0, 0), 15 - 2 * k, 0.5))
    c.restore()


# --- the stage ----------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def stage():
    """The fixed card in front of everything: the scalloped pelmet across the top, the playboard below."""
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    scallops = [sk.oval(x, 44, 37) for x in range(-12, W + 60, 72)]
    holes = [sk.oval(x, 58, 6.5) for x in range(-12, W + 60, 72)] + [sk.oval(x, 26, 3.2) for x in range(24, W + 60, 72)]
    card(c, (sk.union(sk.rect(-10, -10, W + 10, 44), *scallops), tuple(holes),
             ((sk.poly([(0, 14), (W, 14)], False), 2.0),)))
    ends = [sk.poly([(x, 941), (x + 9, 950), (x, 959), (x - 9, 950)]) for x in (70, W - 70)]
    card(c, (sk.rect(-10, GROUND, W + 10, H + 10), tuple(ends), ((sk.poly([(96, 950), (W - 96, 950)], False), 2.2),)))
    return surf.makeImageSnapshot()


def shadows(t):
    """What the card lets through at t: (H, W, 3) in 0..1, white where the lamp reaches the paper."""
    surf = sk.surface(W, H, (255, 255, 255))
    c = surf.getCanvas()
    house(c, t)
    flag(c, t)
    baths(c, t)
    scoreboard(c, t)
    asmon(c, t)
    hasan(c, t)
    flies(c, t)
    smell(c, t)
    c.drawImage(stage(), 0, 0)
    return sk.array(surf)[..., :3].astype(np.float32) / 255


# --- the lamp and the paper ---------------------------------------------------------------------

STOPS = [0.0, 0.30, 0.62, 0.95, 1.40]
GLOW = [(1.00, 1.00, 0.93, 0.58, 0.15), (0.93, 0.80, 0.56, 0.27, 0.06), (0.72, 0.46, 0.22, 0.08, 0.02)]


@lru_cache(maxsize=1)
def _grid():
    ys, xs = np.mgrid[0:H:4, 0:W:4].astype(np.float32)
    return xs + 2, ys + 2


@lru_cache(maxsize=1)
def paper():
    """What the paper does to the light: blotches, a fine mottle, and its long fibres. (H, W) about 1."""
    rng = np.random.default_rng(7)
    surf = sk.surface(W, H, (128, 128, 128))
    c = surf.getCanvas()
    for _ in range(1500):
        x, y, a, n = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, TAU), rng.uniform(20, 150)
        bend = rng.uniform(-0.5, 0.5)
        line = sk.curve([(x, y), (x + n / 2 * math.cos(a + bend), y + n / 2 * math.sin(a + bend)),
                         (x + n * math.cos(a), y + n * math.sin(a))], False)
        tone = (0, 0, 0) if rng.random() < 0.6 else (255, 255, 255)
        c.drawPath(line, sk.stroke(tone, rng.uniform(0.7, 1.9), rng.uniform(0.08, 0.3)))
    fibre = sk.array(surf)[..., 0].astype(np.float32) / 128 - 1
    seam = np.zeros((H, W), np.float32)                                  # where two sheets overlap
    seam[:, 1318:1362] = -0.055
    return (0.88 + 0.15 * sk.cloud(W, H, 11, 230, 4) + 0.09 * (sk.cloud(W, H, 12, 22, 3) - 0.5) + 0.42 * fibre
            + 0.03 * (sk.grain(W, H, 5) - 0.5) + seam).astype(np.float32)


def lamp(t):
    """The lit paper with nothing in front of it: a hot centre falling away to the corners, never quite still."""
    k = 1 + 0.020 * math.sin(TAU * 2.3 * t) + 0.012 * math.sin(TAU * 6.1 * t + 1.3) + 0.008 * math.sin(TAU * 11.7 * t + 0.4)
    xs, ys = _grid()
    r = np.hypot((xs - 960 - 6 * math.sin(TAU * 1.7 * t)) / 1050, (ys - 430 - 4 * math.sin(TAU * 2.9 * t + 2)) / 700)
    chans = [np.asarray(Image.fromarray(np.interp(r, STOPS, g).astype(np.float32), mode="F").resize((W, H), Image.BILINEAR))
             for g in GLOW]
    return np.stack(chans, -1) * (paper() * k)[..., None]


# --- the words ----------------------------------------------------------------------------------

UNSUNG, SUNG, NOW, HALO = (150, 76, 28), (236, 154, 66), (255, 240, 196), (255, 168, 60)


def words(c, t):
    """The line, cut along the playboard: the lamp comes through a word as it is sung."""
    line, state = S.caption(t)
    if line is None:
        return
    size = 58
    fnt = sk.font(FONT, size)
    gap = fnt.measureText(" ") * 1.15
    total = sum(fnt.measureText(w) for w, _ in state) + gap * (len(state) - 1)
    if total > W - 200:
        size = size * (W - 200) / total
        fnt = sk.font(FONT, round(size, 1))
        gap = fnt.measureText(" ") * 1.15
        total = sum(fnt.measureText(w) for w, _ in state) + gap * (len(state) - 1)
    x = (W - total) / 2
    for (word, st), (_, a, b) in zip(state, line["words"]):
        if st == 1:
            halo = sk.fill(HALO, 0.75)
            halo.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
            c.drawString(word, x, 1026, fnt, halo)
        lit = S.smooth(S.ramp(t, a - 0.03, 0.08))
        tone = tuple(u + (v - u) * lit for u, v in zip(UNSUNG, NOW if st == 1 else SUNG))
        c.drawString(word, x, 1026, fnt, sk.fill(tone))
        x += fnt.measureText(word) + gap


# --- the frame ----------------------------------------------------------------------------------

def frame(t):
    img = lamp(t) * (AMBIENT + (1 - AMBIENT) * shadows(t))
    out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    bloom = out.resize((W // 8, H // 8), Image.BOX).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
    img = img + 0.13 * np.asarray(bloom, np.float32) / 255                # the lamp spills round the card
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.drawImage(sk.from_array((np.clip(img, 0, 1) * 255).astype(np.uint8)), 0, 0)
    words(c, t)
    return sk.image(surf)
