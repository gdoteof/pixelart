"""Voxel diorama: the bar as a toy set on a floating island, in real 3D.

Everything is a lattice of cubes (voxel_models.py) drawn by a small software renderer (voxel_engine.py):
a perspective camera, one sun with soft shadows, sky light. The men are jointed figures: a torso that
leans, a head that turns, and arms solved from where the hands should be. Things arrive the way toys do:
the house grows out of its plot, the baths drop out of the sky and bounce. The camera makes one slow move
a line and otherwise stands still.
"""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image, ImageFilter

import script as S
import sk
import voxel_engine as E
import voxel_models as M
from voxel_engine import RX, RY, RZ, SC, Inst, T

NAME = "Voxel diorama"
SS = 3                                      # the picture is drawn at three times its size
W, H = S.W * SS, S.H * SS
SUN = E.Sun((-0.28, 0.62, 0.73), (0, 8, 0), 74, 2048)
LIGHT = E.Light((0.55, 0.58, 0.66), (0.63, 0.58, 0.50))
E.TAPS = [(0.0, 0.0)] + [(r * math.cos(a), r * math.sin(a)) for r, off in ((3.2, 0), (6.4, 0.5))
                         for a in (np.arange(6) + off) * math.pi / 3]
EV = S.EV
SEAT = 5                                    # the height of a chair's seat
K = 1.12                                    # the men are a size bigger than their furniture
TUB_X = [-23 + 8 * i for i in range(6)]     # the baths' row, and the half
TUB_Z = -6
HOUSE = (0, 0, -17)
DIST = 196.0                                # the camera's distance, and where the picture is sharp
CONTACT = 0.3                               # how dark the shade behind a near thing's edge gets
BLOOM = 0.8                                 # how much the lit things spill


def track(keys, t, ease=S.smooth):
    """A value that moves between keys: [(start, seconds, value), ...], the first being where it begins."""
    v = np.asarray(keys[0][2], float)
    for t0, dur, val in keys[1:]:
        if t <= t0:
            break
        v = v + (np.asarray(val, float) - v) * ease((t - t0) / dur)
    return v


def camera(t):
    yaw = float(track([(0, 0, -6.0), (67.95, 2.5, -1.5), (70.95, 2.3, 4.5)], t))
    pitch = math.radians(22.5)
    target = np.array([0.0, 10.0, -1.0])
    y = math.radians(yaw)
    eye = target + DIST * np.array([math.sin(y) * math.cos(pitch), math.sin(pitch), math.cos(y) * math.cos(pitch)])
    return E.Camera(eye, target, 21.5, W, H)


# --- the men ------------------------------------------------------------------------------------

def _aim(d):
    """A turn that points a bone (which hangs down its own -y) along d."""
    y = -np.asarray(d, float)
    y /= np.linalg.norm(y)
    x = np.cross(y, (0.0, 0.0, 1.0))
    if np.linalg.norm(x) < 1e-3:
        x = np.array([1.0, 0.0, 0.0])
    x /= np.linalg.norm(x)
    m = np.eye(4)
    m[:3, 0], m[:3, 1], m[:3, 2] = x, y, np.cross(x, y)
    return m


def arm(who, body, side, wrist, hand="fist"):
    """The three pieces of an arm reaching from its shoulder to a wrist, both in the torso's own space."""
    s = np.array(M.PIVOT[who]["shoulders"][0 if side < 0 else 1], float)
    a, b = M.PIVOT[who]["arm"]
    w = np.asarray(wrist, float)
    d = w - s
    n = np.linalg.norm(d)
    reach = min(max(n, abs(a - b) + 0.05), a + b - 0.05)
    d /= n
    w = s + d * reach
    along = (a * a - b * b + reach * reach) / (2 * reach)
    pole = np.array([side * 0.8, -1.0, -0.6])                       # the elbow goes out, down and back
    pole -= d * (pole @ d)
    pole /= np.linalg.norm(pole)
    e = s + d * along + pole * math.sqrt(max(0.0, a * a - along * along))
    fore = _aim(w - e)
    return [Inst(M.limb(who, "upper"), body @ T(*s) @ _aim(e - s)),
            Inst(M.limb(who, "fore"), body @ T(*e) @ fore),
            Inst(M.limb(who, "hand", hand), body @ T(*w) @ (np.eye(4) if hand == "thumb" else fore))]


def asmon(t):
    cx, cz = M.AX, M.CZ - 3
    seat, neck = M.PIVOT["asmon"]["seat"], M.PIVOT["asmon"]["neck"]
    body = T(cx, SEAT, cz) @ RY(14) @ SC(K) @ T(-seat[0], 0, -seat[2])
    rest_l, rest_r = (0.9, 4.8, 9.4), (8.1, 4.8, 9.4)
    point, shrug_l, shrug_r = (15.5, 12.0, 2.5), (-3.4, 8.8, 6.4), (12.4, 8.8, 6.4)
    mine, proud = (5.4, 5.6, 6.6), (13.6, 12.6, 7.0)
    right = track([(0, 0, rest_r), (67.60, 0.30, point), (70.02, 0.26, shrug_r), (70.76, 0.30, rest_r),
                   (72.30, 0.26, mine), (73.02, 0.24, proud)], t, S.back)
    left = track([(0, 0, rest_l), (70.02, 0.26, shrug_l), (70.76, 0.30, rest_l)], t, S.back)
    hand = "point" if 67.6 < t < 70.0 else "thumb" if t > 73.0 else "fist"
    yaw = float(track([(0, 0, 6.0), (67.55, 0.3, 24.0), (70.74, 0.3, 2.0), (73.05, 0.25, 10.0)], t))
    pitch = float(track([(0, 0, 0.0), (73.05, 0.22, -8.0)], t, S.back))
    roll = float(track([(0, 0, 0.0), (70.08, 0.2, -9.0), (70.74, 0.25, 0.0)], t, S.back))
    bob = (0.55 if S.singing(t) else 0.3) * S.thump(t, 6.0)
    m = S.mouth(t)
    gape, wide, teeth = 0, 3, False
    if S.SING0 - 0.05 <= t <= S.SING1 + 0.1:
        gape = int(min(3, round(m["h"] * 3.7)))
        wide = 1 if m["w"] < 0.58 else 5 if m["w"] > 1.02 else 3
        teeth = m["teeth"] > 0.55
        if gape == 0 and m["f"] > 0.5:
            gape, teeth = 1, True
    if t > 73.2:                                                    # and a grin to finish
        gape, wide, teeth = 1, 5, True
    blink = any(a <= t < a + 0.1 for a in (67.3, 70.8, 74.1))
    head = body @ T(neck[0], neck[1] + bob, neck[2]) @ RY(yaw - 14) @ RX(pitch) @ RZ(roll) @ T(-5.5, 0, -4.5)
    return [Inst(M.torso("asmon"), body), Inst(M.head_asmon(gape, wide, teeth, 1, blink), head),
            *arm("asmon", body, -1, left), *arm("asmon", body, 1, right, hand)]


def hasan(t):
    cx, cz = M.HX, M.CZ - 3
    seat, neck = M.PIVOT["hasan"]["seat"], M.PIVOT["hasan"]["neck"]
    lean = track([(0, 0, (0.0, 0.0)), (73.08, 0.3, (-12.0, -9.0))], t, S.back)
    body = T(cx, SEAT, cz) @ RY(-14) @ RX(lean[0]) @ RZ(lean[1]) @ SC(K) @ T(-seat[0], 0, -seat[2])
    rest_l, rest_r = (3.4, 4.9, 10.4), (13.6, 4.9, 10.4)
    ward, pinch = (-7.5, 12.0, 6.5), (13.2, 15.6, 9.0)
    left = track([(0, 0, rest_l), (73.12, 0.26, ward)], t, S.back)
    right = track([(0, 0, rest_r), (73.10, 0.26, pinch)], t, S.back)
    yaw = float(track([(0, 0, -10.0), (68.15, 0.28, -40.0), (69.3, 0.4, -14.0), (71.95, 0.3, -30.0), (73.08, 0.22, 16.0)], t))
    pitch = float(track([(0, 0, 0.0), (73.08, 0.25, -10.0)], t, S.back))
    roll = float(track([(0, 0, 0.0), (70.26, 0.2, 7.0), (70.9, 0.3, 0.0)], t, S.back))
    face = "smug" if t < 70.24 else "flat" if t < EV["year"] + 0.04 else "ugh"
    bob = 0.3 * S.thump(t, 6.0)
    head = body @ T(neck[0], neck[1] + bob, neck[2]) @ RY(yaw + 14) @ RX(pitch) @ RZ(roll) @ T(-6.5, 0, -4.5)
    return [Inst(M.torso("hasan"), body), Inst(M.head_hasan(face, -1), head),
            *arm("hasan", body, -1, left, "palm" if t > 73.16 else "fist"), *arm("hasan", body, 1, right)]


# --- the set ------------------------------------------------------------------------------------

def _dust(out, t, t0, x, z, n=6, spread=1.0, name="dust"):
    """A ring of specks thrown out along the ground from a landing at t0."""
    u = (t - t0) / 0.34
    if not 0 <= u < 1:
        return
    for i in range(n):
        a = 2 * math.pi * (i + S.rnd("dust", x, i)) / n
        r = spread * (2.4 + 5.5 * S.ease_out(u, 2))
        out.append(Inst(M.cube(name), T(x + r * math.cos(a) * 1.4, 0.5 + 1.8 * math.sin(math.pi * u), z + r * math.sin(a))
                        @ SC(1.0 * (1 - u)) @ RY(40 * i), cast=False))


def _fly(i, t, hx, hy, hz):
    """Where fly i is at t, circling a head, and the angle it has got to."""
    a = (5.0 + 3.0 * S.rnd("fw", i)) * (t - 66) * (1 if i % 2 else -1) + 6.28 * S.rnd("fa", i)
    r = 11.0 + 3.5 * S.rnd("fr", i) + 1.2 * math.sin(3.1 * t + i)
    tilt = (1 if i % 3 else -1) * (8 + 4 * S.rnd("ft", i))          # over his head in front, or under his chin
    return (hx + r * math.cos(a), hy + 1 + tilt * math.sin(a) + 1.2 * math.sin(7.3 * t + 2 * i), hz + 4 + 0.6 * r * math.sin(a)), a


def _drop(t, land):
    """A thing that falls out of the sky to land at `land` and bounce: (height, squash) or None before it."""
    fall = 0.24
    if t < land - fall:
        return None
    if t < land:
        return 46 * (1 - ((t - (land - fall)) / fall) ** 2), 1.12
    u = t - land
    hop = 3.2 * abs(math.sin(math.pi * u / 0.2)) * math.exp(-7.5 * u) if u < 0.6 else 0.0
    return hop, 1 - 0.34 * math.exp(-11 * u) * math.cos(2 * math.pi * u / 0.2)


def scene(t):
    out = [Inst(M.island(), T())]
    for i, (x, y, z, k) in enumerate([(-62, 19, -46, 2.6), (40, 27, -64, 3.0), (-16, 33, -90, 3.2), (72, 6, -30, 2.2)]):
        out.append(Inst(M.cloud(i), T(x + 1.1 * (t - S.T0), y, z) @ SC(k), cast=False))
    # the house grows out of its plot, with its palms, and goes back into it for the scoreboard
    gone = S.ease_in(S.ramp(t, EV["line2"] - 0.14, 0.2), 2)
    for name, delay, x, z in (("house", 0.0, 0, 0), ("palm0", 0.1, -26, 3), ("palm1", 0.17, 24, 3)):
        k = S.pop(t, EV["mansion"] - 0.05 + delay, 0.36) * (1 - gone)
        if k < 0.02:
            continue
        grow = T(HOUSE[0] + x, 0, HOUSE[2] + z) @ SC(0.88 + 0.12 * min(k, 1), k, 0.88 + 0.12 * min(k, 1))
        if name != "house":
            out.append(Inst(M.palm(int(name[-1])), grow @ RZ(1.6 * math.sin(1.9 * t + 2 * x))))
            continue
        out.append(Inst(M.mansion(), grow))
        if S.on("austere", t):
            rise = S.back(S.ramp(t, EV["austere"], 0.42), 1.2)
            out.append(Inst(M.flag(int(t * 12) % 8), grow @ T(1, 15 + 8 * rise, -1)))
    _dust(out, t, EV["mansion"], 0, HOUSE[2] + 9, 12, 2.6)
    # the baths, counted off, and the half
    away = 1 - S.ease_in(S.ramp(t, EV["line2"] - 0.2, 0.2), 2)
    for i, land in enumerate(list(EV["tubs"]) + [EV["half"]]):
        d = _drop(t, land)
        if d is None:
            continue
        y, q = d
        half = i == 5
        wob = 9 * math.exp(-5 * (t - land)) * math.sin(2 * math.pi * (t - land) / 0.3) if half and t > land else 0.0
        x, z = TUB_X[i] + 3, TUB_Z + 4.5
        out.append(Inst(M.tub(half), T(x, y, z) @ RZ(wob) @ SC(1 / math.sqrt(q), q, 1 / math.sqrt(q)) @ T(-3, 0, -4.5)))
        _dust(out, t, land, x, z, 6)
        k = S.pop(t, land + 0.04, 0.22) * away
        if k > 0.02:
            out.append(Inst(M.tag("12345½"[i]), T(x, 9.4, z - 2) @ SC(0.42 * k), cast=False))
    # the count, flipped up at the lawn's edge
    if S.on("baths", t):
        k = S.back(S.ramp(t, EV["baths"], 0.3), 2.4)
        out.append(Inst(M.plaque(), T(0, 0.2, 26.5) @ RX(-90 + 32 * k) @ SC(0.72)))
    # the scoreboard
    if t > EV["line2"] + 0.04:
        k = S.pop(t, EV["line2"] + 0.04, 0.36)
        hit = t - EV["had"]
        bump = 0.07 * math.exp(-9 * hit) * math.cos(2 * math.pi * hit / 0.22) if hit > 0 else 0.0
        me = "?" if t < EV["ive"] else "0" if hit >= 0 else "7391486253"[int((t - EV["ive"]) * S.FPS / 2) % 10]
        out.append(Inst(M.scoreboard(me), T(0, 0, HOUSE[2]) @ SC(0.6 * (1 + bump), 0.6 * k * (1 + bump), 0.6)))
        _dust(out, t, EV["line2"] + 0.1, 0, HOUSE[2] + 3, 12, 3.0)
    out += asmon(t) + hasan(t)
    # the flies find him, and then the smell
    hx, hy, hz = M.AX + 0.5, 24.0, M.CZ - 2.5
    for i in range(7):
        t0 = EV["ive"] + (0.0 if i == 0 else 0.5 + 0.09 * i)
        if t < t0:
            continue
        k = S.pop(t, t0, 0.2)
        for wake in range(4):
            pos, a = _fly(i, t - 0.022 * wake, hx, hy, hz)
            if wake:
                out.append(Inst(M.cube("fly"), T(*pos) @ SC(k * (0.42 - 0.09 * wake)), cast=False))
            else:
                out.append(Inst(M.fly(S.frame_no(t) % 2), T(*pos) @ RY(-math.degrees(a) - (90 if i % 2 else -90)) @ SC(0.56 * k), cast=False))
    reek = t - EV["year"]
    if reek > 0:
        grow = S.ease_out(reek / 0.4, 2)
        for j, (dx, y0, tall) in enumerate(((-13.0, 17.0, 15.0), (13.5, 18.0, 15.0), (-4.5, 35.0, 10.0), (4.5, 36.0, 10.0))):
            for i in range(7):
                u = (i / 7 + 0.5 * reek + 0.37 * j) % 1.0
                x = hx + dx + 1.5 * math.sin(2 * math.pi * 1.5 * u + 1.7 * j)
                out.append(Inst(M.cube("stink", True), T(x, y0 + tall * u * grow, hz) @ SC(1.25 * grow * math.sin(math.pi * u) ** 0.5 + 0.01), cast=False))
    return out


# --- the picture --------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def sky():
    y = np.linspace(0, 1, S.H, dtype=np.float32)[:, None, None]
    x = np.linspace(0, 1, S.W, dtype=np.float32)[None, :, None]
    top, low = np.array([92, 160, 236], np.float32), np.array([206, 232, 250], np.float32)
    g = top + (low - top) * np.clip(y * 1.15, 0, 1) ** 1.3
    glow = np.exp(-(((x - 0.16) * 1.6) ** 2 + ((y - 0.1) * 2.2) ** 2) * 3.0)      # the sun's side of the sky
    return g + glow * np.array([38, 30, 8], np.float32)


@lru_cache(maxsize=None)
def vignette():
    y = np.linspace(-1, 1, S.H, dtype=np.float32)[:, None]
    x = np.linspace(-1, 1, S.W, dtype=np.float32)[None, :]
    return (1 - 0.16 * np.clip((x * x + y * y) - 0.55, 0, 1))[..., None]


def caption(img, t):
    """The lyric line, clean and over the picture: words turn green as they are sung."""
    line, words = S.caption(t)
    surf = skia.Surface(S.W, S.H)
    canvas = surf.getCanvas()
    canvas.drawImage(sk.from_array(img), 0, 0)
    if line is not None:
        fnt, space = sk.font("black", 46), 14
        widths = [sk.text_width(w, fnt) for w, _ in words]
        total = sum(widths) + space * (len(words) - 1)
        x, y = S.W / 2 - total / 2, 1012
        canvas.drawPath(sk.rect(x - 34, y - 56, x + total + 34, y + 24, 40), sk.fill((16, 20, 40), 0.74))
        tag = sk.font("black", 22)
        tw = sk.text_width("ASMONGOLD", tag)
        canvas.drawPath(sk.rect(x - 34, y - 96, x - 34 + tw + 36, y - 62, 17), sk.fill(M.C["asmon"]))
        sk.text(canvas, "ASMONGOLD", x - 16, y - 71, tag, sk.fill((14, 30, 10)))
        for (word, state), w in zip(words, widths):
            start = next(a for ww, a, b in line["words"] if ww == word and (state != 1 or a <= t < b)) if state == 1 else 0
            lift = 7 * math.exp(-9 * (t - start)) if state == 1 else 0
            col = (236, 238, 248) if state == 0 else M.C["asmon_hi"] if state == 1 else M.C["asmon"]
            sk.text(canvas, word, x, y - lift, fnt, sk.fill(col, 0.62 if state == 0 else 1.0))
            x += w + space
    return sk.image(surf)


def frame(t):
    cam = camera(t)
    base, direct, near, sm = E.render(scene(t), cam, SUN, LIGHT, W, H)
    rgb, alpha, z, glow = E.resolve(base, direct, near, sm, cam, SUN, SS)
    there = alpha > 0.5
    if CONTACT:         # whatever has something close in front of it is darker near that thing's edge
        depth = np.where(there, z, DIST + 30).astype(np.float32)
        low = np.asarray(Image.fromarray(depth).resize((S.W // 8, S.H // 8), Image.BOX))
        for _ in range(2):
            low = np.pad(low, 1, mode="edge")
            low = (low[:-2] + 2 * low[1:-1] + low[2:]) / 4
            low = (low[:, :-2] + 2 * low[:, 1:-1] + low[:, 2:]) / 4
        behind = depth - np.asarray(Image.fromarray(low).resize((S.W, S.H), Image.BICUBIC))
        rgb = rgb * (1 - CONTACT * np.clip((behind - 0.4) / 5.0, 0, 1) * (1 - glow))[..., None]
    img = rgb + sky() * (1 - alpha[..., None])
    # a little of the miniature: the far and the near go soft
    sharp = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    soft = np.asarray(sharp.filter(ImageFilter.GaussianBlur(3.2)), np.float32)
    depth = np.where(there, z, DIST + 80)
    blur = np.clip((np.abs(depth - DIST + 6) - 36.0) / 46.0, 0, 1)[..., None]
    img = np.asarray(sharp, np.float32) * (1 - blur) + soft * blur
    if BLOOM:           # and what is lit from inside spills a little (not the clouds, which are only bright)
        lamp = Image.fromarray(np.clip(img * (glow * (depth < DIST + 20))[..., None], 0, 255).astype(np.uint8))
        img = img + BLOOM * (0.55 * np.asarray(lamp.filter(ImageFilter.GaussianBlur(5)), np.float32)
                             + 0.6 * np.asarray(lamp.filter(ImageFilter.GaussianBlur(20)), np.float32))
    img = np.clip(img * vignette(), 0, 255).astype(np.uint8)
    return caption(img, t)
