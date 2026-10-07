"""Comic book: a printed page of three panels. Black ink over flat colour, Ben-Day dots for the shadows,
a lettered balloon, sound effects. It moves like a motion comic: poses snap and hold, new things pop,
and only the mouth keeps time."""
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

NAME = "Comic book"
INK = (22, 18, 24)
PANEL_A, PANEL_B, PANEL_H = (40, 40, 632, 1040), (656, 40, 1264, 478), (1288, 40, 1880, 1040)
ASMON_AT, HASAN_AT = (322, 440, 166), (1584, 470, 156)
TINT = {"skin": 1.0}
COLOURS = {
    ("hasan", "hair"): (20, 18, 30), ("hasan", "hair_hi"): (74, 110, 190), ("hasan", "fade"): (70, 62, 80),
    ("hasan", "top"): (250, 248, 240), ("hasan", "skin"): (236, 170, 118), ("hasan", "skin_sh"): (190, 110, 70),
    ("hasan", "stub"): (176, 122, 92), ("hasan", "chain"): (255, 204, 40),
    ("asmon", "hair"): (150, 84, 40), ("asmon", "hair_sh"): (104, 56, 30), ("asmon", "hair_hi"): (214, 140, 70),
    ("asmon", "beard"): (118, 62, 30), ("asmon", "skin"): (250, 216, 190), ("asmon", "skin_sh"): (222, 150, 120),
    ("asmon", "top"): (30, 30, 44), ("asmon", "phones"): (24, 22, 34), ("asmon", "phones_hi"): (90, 120, 200),
    ("prop", "wall"): (255, 244, 214), ("prop", "roof"): (226, 78, 44), ("prop", "window"): (255, 214, 60),
    ("prop", "hedge"): (60, 170, 80), ("prop", "frond"): (40, 160, 90), ("prop", "tub"): (255, 255, 255),
    ("prop", "tub_sh"): (120, 170, 220), ("prop", "flag"): (230, 30, 40), ("prop", "wall_sh"): (220, 180, 130),
}


def col_of(q):
    return COLOURS.get((q.who, q.col)) or puppet.colour(q.who, q.col)


@lru_cache(maxsize=64)
def dots(colour, cell=11, r=0.36):
    """A shader of Ben-Day dots in a colour, on the slant."""
    n = cell * 4
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.hypot((xx % cell) - (cell - 1) / 2, (yy % cell) - (cell - 1) / 2)
    a = np.clip((cell * r - d) * 1.6 + 0.5, 0, 1)
    tile = np.zeros((n, n, 4), np.uint8)
    tile[..., :3] = colour
    tile[..., 3] = (a * 255).astype(np.uint8)
    m = skia.Matrix()
    m.setRotate(35)
    return sk.from_array(tile).makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat,
                                          skia.SamplingOptions(skia.FilterMode.kLinear), m)


def inked(c, parts, seed=0, weight=1.0):
    """Flat colour, dots for shadow, and a black line that is not quite steady."""
    for i, q in enumerate(parts):
        col = col_of(q)
        if q.open:
            c.drawPath(q.path, sk.stroke(INK if q.line else col, q.w * (1.25 if q.line else 1.0)))
        elif q.shade:
            paint = skia.Paint(AntiAlias=True)
            paint.setShader(dots(col))
            c.drawPath(q.path, paint)
        else:
            c.drawPath(q.path, sk.fill(col))
            if q.line:
                pen = sk.stroke(INK, (6.5 if q.line == 2 else 3.4) * weight)
                pen.setPathEffect(skia.DiscretePathEffect.Make(26, 0.9, seed * 131 + i))
                if q.mask is not None:
                    c.save()
                    c.clipPath(q.mask, skia.ClipOp.kDifference, True)
                    c.drawPath(q.path, pen)
                    c.restore()
                else:
                    c.drawPath(q.path, pen)


def panel(c, box, colour, corner, dot):
    """A panel's ground: flat colour, with dots that swell towards one corner."""
    x0, y0, x1, y1 = box
    c.drawRect(skia.Rect.MakeLTRB(*box), sk.fill(colour))
    w, h = x1 - x0, y1 - y0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cell, a = 15.0, math.radians(30)
    u, v = xx * math.cos(a) + yy * math.sin(a), -xx * math.sin(a) + yy * math.cos(a)
    d = np.hypot((u % cell) - cell / 2, (v % cell) - cell / 2)
    far = np.hypot(xx - corner[0] * w, yy - corner[1] * h) / math.hypot(w, h)
    alpha = np.clip((cell * 0.62 * np.clip(1.05 - far * 1.5, 0, 1) - d) * 1.5 + 0.5, 0, 1)
    tile = np.zeros((h, w, 4), np.uint8)
    tile[..., :3] = dot
    tile[..., 3] = (alpha * 255).astype(np.uint8)
    c.drawImage(sk.from_array(tile), x0, y0)


@lru_cache(maxsize=None)
def page():
    """The page under everything: paper, and the grounds of the two portrait panels."""
    s = sk.surface(S.W, S.H, (246, 238, 214))
    c = s.getCanvas()
    panel(c, PANEL_A, (96, 190, 150), (0.0, 0.0), (40, 130, 110))
    panel(c, PANEL_H, (168, 130, 240), (1.0, 0.0), (110, 70, 190))
    return s.makeImageSnapshot()


@lru_cache(maxsize=None)
def paper():
    """What printing does to it: fibre, a little yellow at the edges. Multiplied over the page."""
    g = 0.90 + 0.10 * sk.cloud(S.W, S.H, 5, cell=220) + sk.grain(S.W, S.H, 2, 1, -0.035, 0.035)
    yy, xx = np.mgrid[0:S.H, 0:S.W].astype(np.float32)
    edge = np.clip(np.hypot((xx - S.W / 2) / S.W, (yy - S.H / 2) / S.H) * 1.5 - 0.35, 0, 1)
    rgb = np.stack([g * (1 - 0.05 * edge), g * (1 - 0.09 * edge), g * (1 - 0.22 * edge)], -1)
    return np.clip(rgb, 0, 1.02)


def border(c, box, seed):
    pen = sk.stroke(INK, 9, join="miter", cap="square")
    pen.setPathEffect(skia.DiscretePathEffect.Make(60, 1.4, seed))
    c.drawPath(sk.rect(*box), pen)


def burst(cx, cy, r0, r1, n, seed):
    """A star of n points: for a shout or a stamp."""
    pts = []
    for k in range(n * 2):
        a = k * math.pi / n + 0.2
        r = (r1 * (0.9 + 0.25 * S.rnd(seed, k))) if k % 2 == 0 else r0
        pts.append((cx + r * math.cos(a) * 1.35, cy + r * math.sin(a), "c"))
    return sk.curve(pts)


def lettering(c, text, x, y, size, fill, rot=0.0, k=1.0, edge=9, font="comic", skew=-0.18):
    """Sound-effect lettering: slanted, fat outline."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    c.skew(skew, 0)
    path = sk.text_path(text, sk.font(font, size), 0, 0, "m")
    c.drawPath(path, sk.stroke(INK, edge))
    c.drawPath(path, sk.fill(fill))
    c.restore()


def scene_house(c, t):
    w, h = props.BOARD
    c.drawRect(skia.Rect.MakeWH(w, 520), sk.fill((120, 200, 250)))
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(dots((255, 255, 255), 13, 0.30))
    c.drawRect(skia.Rect.MakeLTRB(0, 250, w, 520), sky)
    c.drawRect(skia.Rect.MakeLTRB(0, 498, w, 540), sk.fill((90, 190, 90)))
    c.drawRect(skia.Rect.MakeLTRB(0, 540, w, h + 40), sk.fill((250, 210, 70)))
    floor = skia.Paint(AntiAlias=True)
    floor.setShader(dots((240, 150, 40), 13, 0.30))
    c.drawRect(skia.Rect.MakeLTRB(0, 540, w, h + 40), floor)
    c.drawLine(0, 540, w, 540, sk.stroke(INK, 6))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, w, 500))
    inked(c, props.house_at(t), 3, 0.8)
    c.restore()
    c.drawLine(0, 498, w, 498, sk.stroke(INK, 6))
    inked(c, props.flag(t), 4, 0.8)
    inked(c, props.tubs(t), 5, 0.8)
    k = S.pop(t, S.EV["baths"], 0.16, 3.2)
    if k > 0:
        x, y, rot = props.STAMP
        c.save()
        c.translate(x, y + 6)
        c.rotate(rot)
        c.scale(k, k)
        star = burst(0, 0, 84, 124, 13, 7)
        c.drawPath(star, sk.fill((255, 232, 40)))
        c.drawPath(star, sk.stroke(INK, 8))
        c.restore()
        lettering(c, "5½ BATHS!", x, y + 28, 62, (230, 30, 40), rot, k, 10)


def scene_score(c, t):
    w, h = props.BOARD
    c.drawRect(skia.Rect.MakeWH(w, h + 40), sk.fill((255, 226, 60)))
    if t >= S.EV["had"]:                                  # the nought lands in a burst of lines
        x0, y0, x1, y1 = props.SCORE["me"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 60
        for k in range(44):
            a = k * 2 * math.pi / 44 + 0.3 * S.rnd("ray", k)
            r0 = 330 + 90 * S.rnd("r0", k)
            wd = 0.035 + 0.03 * S.rnd("w", k)
            c.drawPath(sk.poly([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                                (cx + 1400 * math.cos(a - wd), cy + 1400 * math.sin(a - wd)),
                                (cx + 1400 * math.cos(a + wd), cy + 1400 * math.sin(a + wd))]), sk.fill(INK))
    c.drawPath(sk.rect(-10, -10, w + 10, 150), sk.fill(INK))
    lettering(c, "BATHS THIS YEAR", 500, 112, 92, (255, 226, 60), 0, 1, 0, skew=-0.12)
    for key, name, tint in (("him", "HIM", (168, 130, 240)), ("me", "ME", (96, 210, 120))):
        x0, y0, x1, y1 = props.SCORE[key]
        box = sk.rect(x0, y0 + 20, x1, y1 + 30, 6)
        c.drawPath(sk.xf(box, 12, 12), sk.fill(INK))
        c.drawPath(box, sk.fill((255, 255, 255)))
        c.drawPath(box, sk.stroke(INK, 8))
        c.drawPath(sk.rect(x0, y0 + 20, x1, y0 + 130, 6), sk.fill(tint))
        c.drawPath(sk.rect(x0, y0 + 20, x1, y0 + 130, 6), sk.stroke(INK, 8))
        sk.text(c, name, (x0 + x1) / 2, y0 + 106, sk.font("comic", 84), sk.fill(INK), "m")
    x0, y0, x1, y1 = props.SCORE["him"]
    lettering(c, "5½", (x0 + x1) / 2, y1 - 70, 290, (168, 130, 240), 0, 1, 14)
    x0, y0, x1, y1 = props.SCORE["me"]
    me = props.me_score(t)
    k = S.pop(t, S.EV["had"], 0.16, 4.0) if t >= S.EV["had"] else 1.0
    lettering(c, me, (x0 + x1) / 2, y1 - 70, 300, (230, 30, 40) if t >= S.EV["had"] else (150, 150, 150), -6 if t >= S.EV["had"] else 0, k, 14)


def middle(c, t):
    x0, y0, x1, y1 = PANEL_B
    k = (x1 - x0) / props.BOARD[0]
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(*PANEL_B))
    c.translate(x0, y0)
    c.scale(k, k)
    if t < S.EV["line2"]:
        scene_house(c, t)
    else:
        scene_score(c, t)
    c.restore()


def box(c, text, x, y, size=40):
    """A caption box: black on yellow."""
    fnt = sk.font("comic", size)
    w = sk.text_width(text, fnt)
    r = sk.rect(x, y, x + w + 36, y + size * 1.5)
    c.drawPath(sk.xf(r, 6, 6), sk.fill(INK))
    c.drawPath(r, sk.fill((255, 232, 60)))
    c.drawPath(r, sk.stroke(INK, 5))
    sk.text(c, text, x + 18, y + size * 1.1, fnt, sk.fill(INK))


def balloon(c, t):
    """The line, lettered in a balloon under the middle panel, its tail towards the man singing it."""
    line, words = S.caption(t)
    if not line:
        box(c, "MEANWHILE, ON STREAM...", 690, 540, 40)
        return
    x0, y0, x1, y1 = 676, 520, 1246, 1010
    body = sk.rect(x0, y0 + 30, x1, y1 - 30, 150)
    tail = sk.curve([(x0 + 60, 640, "c"), (566, 566, "c"), (x0 + 30, 740, "c")])
    shape = sk.union(body, tail)
    c.drawPath(sk.xf(shape, 9, 10), sk.fill(INK))
    c.drawPath(shape, sk.fill((255, 255, 255)))
    c.drawPath(shape, sk.stroke(INK, 7))
    fnt = sk.font("comic", 58)
    space, rows, row, width = 18, [], [], 0.0
    for w, st in words:
        wd = sk.text_width(w.upper(), fnt)
        if row and width + wd > 430:
            rows.append(row)
            row, width = [], 0.0
        row.append((w.upper(), st, wd))
        width += wd + space
    rows.append(row)
    y = (y0 + y1) / 2 - (len(rows) - 1) * 39 + 20
    for row in rows:
        x = (x0 + x1) / 2 - (sum(wd for *_, wd in row) + space * (len(row) - 1)) / 2
        for w, st, wd in row:
            if st == 1:                                   # the word being sung: red, and inked heavier
                c.drawPath(sk.text_path(w, fnt, x, y), sk.stroke((230, 30, 40), 3.0))
                sk.text(c, w, x, y, fnt, sk.fill((230, 30, 40)))
            else:
                sk.text(c, w, x, y, fnt, sk.fill((160, 160, 160) if st == 0 else INK))
            x += wd + space
        y += 78


def jolt(who, t):
    """A man's scale on the frames after he snaps to a new pose: a pop, then still."""
    age = min((t - k[0] for k in acting.TRACK[who] if t >= k[0]), default=9.0)
    return 1 + 0.045 * max(0.0, 1 - age / 0.13)


def frame(t):
    th = S.hold(t, 2)
    s = sk.surface(S.W, S.H)
    c = s.getCanvas()
    c.drawImage(page(), 0, 0)
    middle(c, th)
    for who, at, rect, seed in (("asmon", ASMON_AT, PANEL_A, 1), ("hasan", HASAN_AT, PANEL_H, 2)):
        x0, y0, x1, y1 = rect
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0, y0, x1, y1))
        if who == "hasan" and th >= S.EV["year"]:         # he pulls away: speed lines across his panel
            for k in range(26):
                yy = y0 + 20 + (y1 - y0 - 40) * S.rnd("sl", k)
                xx = x0 + (x1 - x0) * (0.1 + 0.9 * S.rnd("sx", k))
                c.drawLine(x0, yy, xx - 120, yy, sk.stroke((255, 255, 255), 3 + 4 * S.rnd("sw", k), 0.8))
        k = jolt(who, th)
        c.translate(at[0], y1)
        c.scale(k, k)
        c.translate(-at[0], -y1)
        inked(c, puppet.figure(who, acting.pose(who, th, snap=True), at), seed)
        c.restore()
    for rect, seed in ((PANEL_A, 11), (PANEL_B, 12), (PANEL_H, 13)):
        border(c, rect, seed)
    c.save()                                              # his hand breaks out of the panel, over the gutter
    c.clipRect(skia.Rect.MakeLTRB(PANEL_A[2] + 4, PANEL_A[1], PANEL_A[2] + 150, PANEL_A[3]))
    inked(c, [q for q in puppet.figure("asmon", acting.pose("asmon", th, snap=True), ASMON_AT) if q.grp == "arm_r"], 1)
    c.restore()
    box(c, "ASMONGOLD", 58, 966, 34)
    box(c, "HASAN", 1306, 966, 34)
    ax, ay, sc = ASMON_AT
    for path, strength in props.stink(th):
        c.drawPath(sk.xf(path, ax, ay, sc), sk.stroke(INK, 0.075 * sc, 1.0))
        c.drawPath(sk.xf(path, ax, ay, sc), sk.stroke((170, 210, 60), 0.04 * sc, 1.0))
    for fx, fy, wing, heading in props.flies(th):
        inked(c, props.fly(ax + fx * sc, ay + fy * sc, sc * 1.4, wing, heading), 9, 0.6)
    if th >= S.EV["year"]:
        lettering(c, "BZZZ", 190, 215, 84, (190, 230, 60), -12, S.pop(th, S.EV["year"], 0.14, 3.0), 10)
    if S.EV["had"] <= th:
        lettering(c, "?!" if th < S.EV["year"] else "UGH!", 1700, 250, 104, (255, 232, 40), 10,
                  S.pop(th, S.EV["had"] if th < S.EV["year"] else S.EV["year"], 0.14, 3.0), 12)
    balloon(c, t)
    out = np.asarray(sk.array(s)[..., :3], np.float32) * paper()
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
