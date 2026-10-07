"""Paper cut-out: every shape is a piece of coloured paper with a scissored edge, lying on the pieces under
it and casting a small shadow. Shot on twos, like stop motion: the pieces are nudged by hand between
frames, so nothing sits perfectly still, and the lyric is laid down a strip at a time."""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image

import acting
import props
import puppet
import script as S
import sk

NAME = "Paper cut-out"
ASMON_AT, HASAN_AT = (372, 440, 150), (1556, 455, 140)
BOARD = (622, 140, 0.676)
DESK_Y = 950
FLAT = {"iris", "pupil", "glint", "teeth", "tongue", "cup_hi", "star", "bubble", "drop"}     # too small to lift
GROUP = {"face": "head", "hair": "head", "hair_back": "head"}
COLOURS = {
    ("hasan", "skin"): (224, 168, 124), ("hasan", "top"): (244, 240, 228), ("hasan", "hair"): (44, 38, 44),
    ("asmon", "skin"): (240, 212, 190), ("asmon", "top"): (48, 46, 58), ("asmon", "hair"): (150, 96, 58),
    ("asmon", "beard"): (118, 74, 46), ("asmon", "hair_sh"): (112, 70, 44),
    ("prop", "wall"): (248, 236, 210), ("prop", "roof"): (206, 92, 62), ("prop", "tub"): (250, 250, 250),
}


def col_of(q, i):
    r, g, b = COLOURS.get((q.who, q.col)) or puppet.colour(q.who, q.col)
    k = 0.96 + 0.08 * S.rnd("tint", q.who, q.name, i)     # no two sheets of paper are quite the same
    return min(255, r * k), min(255, g * k), min(255, b * k)


def piece(c, path, col, seed, lift=1.0, shadow=True, rough=1.3):
    """One piece of paper: a rough-cut shape and the shadow it casts on what is under it."""
    edge = skia.DiscretePathEffect.Make(17, rough, seed)
    if shadow:
        sh = sk.fill((40, 26, 14), 0.36)
        sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4.5 * lift))
        sh.setPathEffect(edge)
        c.save()
        c.translate(5 * lift, 7 * lift)
        c.drawPath(path, sh)
        c.restore()
    paint = sk.fill(col)
    paint.setPathEffect(edge)
    c.drawPath(path, paint)


def nudge(parts, th, amount=1.0):
    """The pieces as the animator left them this frame: each group a hair off where it should be."""
    f = S.frame_no(th)
    out, cache = [], {}
    for q in parts:
        g = (q.who, GROUP.get(q.grp, q.grp))
        if g not in cache:
            b = q.path.getBounds()
            cache[g] = sk.matrix((S.rnd("nx", g, f) - 0.5) * 3.4 * amount, (S.rnd("ny", g, f) - 0.5) * 3.4 * amount,
                                 rot=(S.rnd("nr", g, f) - 0.5) * 0.9 * amount, about=(b.centerX(), b.centerY()))
        out.append((q, sk.xf(q.path, m=cache[g])))
    return out


def lay(c, parts, th, seed=0, lift=1.0, amount=1.0):
    for i, (q, path) in enumerate(nudge(parts, th, amount)):
        col = col_of(q, i)
        if q.open:
            c.drawPath(path, sk.stroke(col, q.w * 1.15))
        elif q.shade:
            piece(c, path, col, seed * 977 + i, lift, shadow=False, rough=0.8)
        else:
            piece(c, path, col, seed * 977 + i, lift * (0.5 if q.grp == "face" else 1.0), shadow=q.name not in FLAT)


@lru_cache(maxsize=None)
def fibre():
    """Paper grain to multiply over everything: soft mottling, tooth, and a few stray fibres."""
    g = 0.93 + 0.07 * sk.cloud(S.W, S.H, 11, cell=10, octaves=3) + sk.grain(S.W, S.H, 4, 1, -0.03, 0.03)
    s = sk.surface(S.W, S.H, (255, 255, 255))
    c = s.getCanvas()
    for k in range(420):
        x, y, a = S.rnd("fx", k) * S.W, S.rnd("fy", k) * S.H, S.rnd("fa", k) * math.pi
        n = 8 + 22 * S.rnd("fl", k)
        c.drawLine(x, y, x + n * math.cos(a), y + n * math.sin(a), sk.stroke((0, 0, 0), 1.0, 0.10))
    return (g * (sk.array(s)[..., 0].astype(np.float32) / 255))[..., None]


@lru_cache(maxsize=None)
def table():
    """The animation table: kraft paper, a sheet of colour behind each man, a cardboard desk."""
    s = sk.surface(S.W, S.H, (190, 156, 116))
    c = s.getCanvas()
    piece(c, sk.xf(sk.rect(-40, 30, 880, 1000), rot=-1.6, about=(400, 500)), (118, 156, 122), 1, 1.4)
    piece(c, sk.xf(sk.rect(1050, 20, 1960, 1000), rot=1.2, about=(1500, 500)), (150, 126, 190), 2, 1.4)
    for k, (x, y, r, col) in enumerate(((150, 170, 54, (236, 200, 84)), (1790, 200, 46, (236, 200, 84)))):
        star = sk.poly([(x + (r if j % 2 == 0 else r * 0.45) * math.sin(j * math.pi / 5),
                         y - (r if j % 2 == 0 else r * 0.45) * math.cos(j * math.pi / 5)) for j in range(10)])
        piece(c, sk.xf(star, rot=12 * (1 if k else -1), about=(x, y)), col, 5 + k, 0.8)
    return s.makeImageSnapshot()


def desk(c):
    piece(c, sk.rect(-20, DESK_Y, S.W + 20, S.H + 20), (132, 96, 62), 9, 1.2)
    for x in range(0, S.W, 13):
        c.drawLine(x, DESK_Y + 4, x, S.H, sk.stroke((104, 74, 46), 2, 0.5))


def scene_house(c, t, th):
    w, h = props.BOARD
    c.drawRect(skia.Rect.MakeWH(w, h), sk.fill((168, 206, 226)))
    piece(c, sk.rect(-20, 498, w + 20, h + 20), (126, 176, 112), 21, 0.8)
    piece(c, sk.rect(-20, 546, w + 20, h + 20), (86, 144, 160), 22, 0.8)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, w, 500))
    lay(c, props.house_at(t), th, 3, 0.8, 0.5)
    c.restore()
    lay(c, props.flag(t), th, 4, 0.8, 0.5)
    lay(c, props.tubs(t), th, 5, 0.9, 0.6)
    if t >= S.EV["baths"]:
        x, y, rot = props.STAMP
        k = 1.25 if S.frame_no(th) - S.frame_no(S.hold(S.EV["baths"], 2)) < 2 else 1.0
        c.save()
        c.translate(x, y)
        c.rotate(rot + 2)
        c.scale(k, k)
        piece(c, sk.rect(-178, -56, 178, 56), (206, 52, 56), 31, 1.0)
        sk.text(c, "5½ BATHS", 0, 27, sk.font("slab", 70), sk.fill((252, 244, 226)), "m")
        c.restore()


def scene_score(c, t, th):
    w, h = props.BOARD
    c.drawRect(skia.Rect.MakeWH(w, h), sk.fill((58, 54, 76)))
    piece(c, sk.xf(sk.rect(90, 30, 910, 132), rot=-1.0, about=(500, 80)), (238, 202, 86), 41, 0.9)
    sk.text(c, "BATHS THIS YEAR", 500, 108, sk.font("slab", 74), sk.fill((52, 44, 40)), "m")
    for key, name, tint, rot in (("him", "HIM", (176, 150, 222), -1.5), ("me", "ME", (150, 200, 150), 1.5)):
        x0, y0, x1, y1 = props.SCORE[key]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        piece(c, sk.xf(sk.rect(x0, y0 + 10, x1, y1), rot=rot, about=(cx, cy)), (248, 242, 228), 42 + len(name), 1.0)
        piece(c, sk.xf(sk.rect(x0 + 110, y0 + 34, x1 - 110, y0 + 118), rot=rot, about=(cx, cy)), tint, 44 + len(name), 0.6)
        sk.text(c, name, cx, y0 + 100, sk.font("slab", 62), sk.fill((52, 44, 40)), "m")
    x0, y0, x1, y1 = props.SCORE["him"]
    sk.text(c, "5½", (x0 + x1) / 2, y1 - 96, sk.font("slab", 270), sk.fill((98, 70, 170)), "m")
    x0, y0, x1, y1 = props.SCORE["me"]
    me = props.me_score(th)
    landed = t >= S.EV["had"]
    k = 1.3 if landed and S.frame_no(th) - S.frame_no(S.hold(S.EV["had"], 2)) < 2 else 1.0
    c.save()
    c.translate((x0 + x1) / 2, y1 - 96)
    c.scale(k, k)
    c.rotate(-5 if landed else 0)
    sk.text(c, me, 0, 0, sk.font("slab", 280), sk.fill((206, 52, 56) if landed else (150, 146, 140)), "m")
    c.restore()


def board(c, t, th):
    x, y, k = BOARD
    w, h = props.BOARD[0] * k, props.BOARD[1] * k
    f = S.frame_no(th)
    c.save()
    c.rotate((S.rnd("br", f) - 0.5) * 0.3, x + w / 2, y + h / 2)
    piece(c, sk.rect(x - 22, y - 22, x + w + 22, y + h + 22), (250, 246, 236), 51, 1.6)
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h), doAntiAlias=True)
    c.translate(x, y)
    c.scale(k, k)
    if t < S.EV["line2"]:
        scene_house(c, t, th)
    else:
        scene_score(c, t, th)
    c.restore()
    for tx, rot in ((x + 40, -32), (x + w - 40, 28)):      # the tape that holds it up
        c.drawPath(sk.xf(sk.rect(-52, -17, 52, 17), tx, y - 20, rot=rot), sk.fill((226, 208, 160), 0.82))
    c.restore()


def strips(c, t, th):
    """The lyric, a strip of paper to a word, each laid down as it is sung."""
    line, words = S.caption(t)
    if not line:
        return
    fnt = sk.font("slab", 50)
    gap = 14
    widths = [sk.text_width(w, fnt) + 32 for w, _ in words]
    x = S.W / 2 - (sum(widths) + gap * (len(words) - 1)) / 2
    for i, ((w, st), wd) in enumerate(zip(words, widths)):
        t0 = line["words"][i][1]
        if th >= S.hold(t0, 2):
            fresh = S.frame_no(th) - S.frame_no(S.hold(t0, 2)) < 2
            rot = (S.rnd("sr", line["t0"], i) - 0.5) * 5
            cx, cy = x + wd / 2, 1012 + (S.rnd("sy", line["t0"], i) - 0.5) * 10
            c.save()
            c.translate(cx, cy)
            c.rotate(rot)
            if fresh:
                c.scale(1.14, 1.14)
            piece(c, sk.rect(-wd / 2, -36, wd / 2, 36), (244, 206, 88) if st == 1 else (248, 242, 228),
                  int(line["t0"] * 10) + i, 1.6 if fresh else 0.9)
            sk.text(c, w, 0, 17, fnt, sk.fill((46, 40, 38)), "m")
            c.restore()
        x += wd + gap


def frame(t):
    th = S.hold(t, 2)
    s = sk.surface(S.W, S.H)
    c = s.getCanvas()
    c.drawImage(table(), 0, 0)
    board(c, th, th)
    for who, at, seed in (("asmon", ASMON_AT, 1), ("hasan", HASAN_AT, 2)):
        lay(c, puppet.figure(who, acting.pose(who, th), at), th, seed)
    desk(c)
    ax, ay, sc = ASMON_AT
    for path, strength in props.stink(th):
        c.drawPath(sk.xf(path, ax, ay, sc), sk.stroke((126, 150, 60), 0.085 * sc, 1.0))
    for fx, fy, wing, heading in props.flies(th):
        lay(c, props.fly(ax + fx * sc, ay + fy * sc, sc * 1.35, wing, heading), th, 9, 0.5, 0.0)
    strips(c, th, th)
    out = np.asarray(sk.array(s)[..., :3], np.float32) * fibre()
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
