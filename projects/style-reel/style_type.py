"""Kinetic typography: the lyric is the picture, and there is nobody in it.

Three layouts on one grid, each a poster that builds on the sung words:

    the house   a pediment drops with YOUR in it, MANSION'S rises underneath and lifts it
    the count   the house shrinks to the head of a column; the words stack up under it from the bottom,
                each new row pushing the others up; a huge 5 1/2 lands beside them over a row of tubs,
                counted off inside "five"; then a card slides over the column: "how austere;" in script,
                under a red flag
    the nought  a hard cut to Asmongold's green for the second line: the stack again, the tubs again,
                and a giant 0 that lands on "had" and knocks them out of the frame; flies on "year"

Inter Black does the work, Lobster Two is the sneer, and five colours: ink, bone, Hasan's purple,
Asmongold's green, and red for the flag alone. Nothing drifts: things move when a word lands.
"""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image

import script as S
import sk

NAME = "Kinetic type"

INK, BONE = (18, 16, 24), (243, 239, 228)
PURPLE, GREEN, RED = (150, 96, 255), (96, 226, 48), (236, 50, 50)
W, H = S.W, S.H
LEAD = 0.06                                 # a word is on screen a frame before it is heard, never after
FALL = 0.11                                 # how long a dropped thing is in the air before it lands on its word
L, R, TOP, BOT = 96, 1824, 122, 958         # the grid: side margins, and the band the big type sits in
COL = 1304                                  # the count's right-hand column starts here
CARD = 1262                                 # and the card that covers it
NUM = 742.0                                 # the size of the 5 1/2


def at(name):
    v = S.EV[name]
    return tuple(x - LEAD for x in v) if isinstance(v, tuple) else v - LEAD


W1 = {w: a - LEAD for w, a, _ in S.LINES[0]["words"]}       # line 1's words are all different
T_YOUR, T_MANSION, T_GOT, T_HOW, T_AUSTERE = W1["Your"], W1["mansion's"], W1["got"], W1["how"], W1["austere;"]
T_CUT = at("line2")


# --- type ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def setting(words, font="black", width=None, size=100.0, track=-0.012, space=1.0):
    """Words set on one line, to an ink width if one is given: (size, cap height, [(outline, box)] a word),
    with the line's ink starting at x=0 and its baseline at y=0. A box is (left, top, right, bottom)."""
    def build(sz):
        fnt, x, out = sk.font(font, sz), 0.0, []
        for k, word in enumerate(words):
            glyphs = fnt.textToGlyphs(word)
            path = skia.Path()
            for g, adv in zip(glyphs, fnt.getWidths(glyphs)):
                gp = fnt.getPath(g)
                if gp is not None:
                    path.addPath(gp, x, 0)
                x += adv + track * sz
            out.append(path)
            if k + 1 < len(words):
                x += (fnt.measureText(" ") + track * sz) * space
        return out

    def extent(paths):
        boxes = [p.getBounds() for p in paths]
        return min(b.left() for b in boxes), max(b.right() for b in boxes)

    if width is not None:
        lo, hi = extent(build(100.0))
        size = 100.0 * width / (hi - lo)
    paths = build(size)
    lo, _ = extent(paths)
    paths = [sk.xf(p, x=-lo) for p in paths]
    cap = -sk.text_path("H", sk.font(font, size)).getBounds().top()
    return size, cap, [(p, (b.left(), b.top(), b.right(), b.bottom())) for p in paths for b in [p.getBounds()]]


def squash(age, amount=0.09, rate=13.0, freq=36.0):
    """(sx, sy) of a thing that has just landed: flattened, then ringing back to itself."""
    if age < 0:
        return 1.0, 1.0
    k = amount * math.exp(-rate * age) * math.cos(freq * age)
    return 1 + 0.4 * k, 1 - k


def draw(c, path, box, x, y, paint, kind="slam", age=0.0, lift=0.0, near=0.28):
    """Draw a set word with its ink's left edge at x and its baseline at y, `age` seconds after its time.

    slam   comes at the page from in front, `near` bigger, and flattens on it
    pop    grows from nothing with a little overshoot
    rise   comes up from behind its own baseline (`lift` is how far below it starts)
    drop   falls from above, lands on its time and flattens
    """
    if age < (-FALL if kind == "drop" else 0):
        return
    l, t, r, b = box
    cx = (l + r) / 2
    c.save()
    c.translate(x, y)
    if kind == "rise":
        c.clipRect(skia.Rect.MakeLTRB(l - 40, t - 60, r + 40, b + 3))
        c.translate(0, (lift or (b - t) * 1.1) * (1 - S.back(age / 0.15, 1.5)))
    elif kind == "slam":
        k = 1 + near * (1 - S.ease_in(age / 0.06, 2)) if age < 0.06 else 1.0
        sx, sy = squash(age - 0.06, 0.07)
        c.translate(cx, 0)
        c.scale(sx, sy)                                           # flattened against its baseline
        c.translate(0, (t + b) / 2)
        c.scale(k, k)                                             # having come at the page from in front
        c.translate(-cx, -(t + b) / 2)
    elif kind == "pop":
        k = S.back(age / 0.16, 2.2)
        c.translate(cx, (t + b) / 2)
        c.scale(k, k)
        c.translate(-cx, -(t + b) / 2)
    elif kind == "drop":
        sx, sy = squash(age, 0.16, 11.0, 30.0)
        c.translate(cx, -1150 * (1 - S.ease_in(1 + age / FALL, 2)) if age < 0 else 0)
        c.scale(sx, sy)
        c.translate(-cx, 0)
    c.drawPath(path, paint)
    c.restore()


def tag(c, colour):
    """Who is rapping, small, in the top margin."""
    fnt = sk.font("cond", 30)
    c.drawRect(skia.Rect.MakeLTRB(L, 62, L + 20, 82), sk.fill(colour))
    x = L + 34
    for ch in "ASMONGOLD":
        c.drawString(ch, x, 83, fnt, sk.fill(colour))
        x += fnt.measureText(ch) + 4.5


# --- pictograms ---------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def tub_parts(half=False):
    """A bath in a 200x140 box, its feet on y=140: (the solid parts, the line under the rim, the foam)."""
    body = skia.Path()
    body.moveTo(16, 56)
    body.lineTo(184, 56)
    body.cubicTo(184, 100, 166, 122, 138, 122)
    body.lineTo(62, 122)
    body.cubicTo(34, 122, 16, 100, 16, 56)
    body.close()
    solid = sk.union(body, sk.rect(0, 42, 200, 60, 9),
                     sk.xf(sk.rect(-9, -12, 9, 12, 5), 54, 129, rot=18), sk.xf(sk.rect(-9, -12, 9, 12, 5), 146, 129, rot=-18),
                     sk.rect(166, 6, 178, 46, 3), sk.rect(142, 6, 178, 18, 6), sk.rect(142, 6, 153, 28, 4))
    line = sk.rect(30, 68, 170, 74, 3)
    foam = skia.Path()
    for x, y, r in ((34, 26, 15), (60, 14, 10), (80, 30, 11), (104, 20, 8)):
        foam.addCircle(x, y, r)
    if half:
        saw = sk.poly([(-20, -20), (100, -20), (90, 20), (110, 48), (90, 76), (110, 104), (96, 150), (-20, 150)])
        solid, line, foam = sk.intersect(solid, saw), sk.intersect(line, saw), sk.intersect(foam, saw)
    return solid, line, foam


def tub(c, cx, base, width, fg, bg, half=False, k=1.0, rot=0.0, sx=1.0, sy=1.0, edge=0.0):
    """A bath `width` wide standing on `base`, centred on cx; k scales it about its feet. An `edge` is a
    margin of the background kept round it, for a bath that passes in front of other ink."""
    if k <= 0:
        return
    solid, line, foam = tub_parts(half)
    s = width / 200
    c.save()
    c.translate(cx, base)
    c.rotate(rot, 0, -70 * s)
    c.scale(s * k * sx, s * k * sy)
    c.translate(-100, -140)
    if edge:
        c.drawPath(solid, sk.stroke(bg, 2 * edge))
        c.drawPath(foam, sk.stroke(bg, 5.5 + 2 * edge))
    c.drawPath(solid, sk.fill(fg))
    c.drawPath(line, sk.fill(bg))
    c.drawPath(foam, sk.stroke(fg, 5.5))
    c.restore()


def flag(c, x, y0, y1, t, t0):
    """A red flag on a pole from y0 up to y1 at x: the pole comes up, then the flag runs out."""
    age = t - t0
    if age < 0:
        return
    top = y0 + (y1 - y0) * S.ease_out(age / 0.1)
    c.drawLine(x, y0, x, top, sk.stroke(INK, 7, cap="butt"))
    c.drawCircle(x, top, 8, sk.fill(INK))
    run = S.back((age - 0.08) / 0.16, 1.4) if age > 0.08 else 0.0
    if run <= 0:
        return
    w, h, n = 116 * run, 68, 14
    edge = [(x + 3 + w * i / n, 5 * (i / n) * math.sin(i / n * 5.2 - t * 13.0)) for i in range(n + 1)]
    c.drawPath(sk.poly([(px, top + 12 + dy) for px, dy in edge] + [(px, top + 12 + h + dy) for px, dy in reversed(edge)]),
               sk.fill(RED))


# --- line 1: the house, then the count ---------------------------------------------------------------

ROOF_W, ROOF_H, BAR = R - L, 250, 16
PLINTH = 754                                # the top of the steps
WORD_Y = PLINTH - 8                         # MANSION'S stands just above them
HOUSE_TOP = 282                             # the apex, once the word has lifted the roof
HOUSE_K = (R - COL) / ROOF_W                # the house as the head of the column


def house(c, t):
    """The pediment with YOUR in it, MANSION'S under it, the steps: at full size, in the frame's own
    coordinates. The roof comes down on the steps; the word comes up out of them and carries it."""
    _, cap, [(word, _)] = setting(("MANSION'S",), width=ROOF_W - 160)
    rise = S.back((t - T_MANSION) / 0.2, 1.5) if t >= T_MANSION else 0.0
    base = PLINTH - (PLINTH - (WORD_Y - cap - 8)) * rise          # the underside of the roof's slab
    grow = S.ease_out((t - (S.T0 + 0.04)) / 0.3)                  # the steps draw out from the middle
    for inset, y in ((40, PLINTH), (0, PLINTH + 28)):
        half = (ROOF_W / 2 - inset) * grow
        if half > 0:
            c.drawRect(skia.Rect.MakeLTRB(W / 2 - half, y, W / 2 + half, y + 20), sk.fill(BONE))
    if t >= T_MANSION:
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(0, 0, W, PLINTH - 2))
        c.drawPath(sk.xf(word, x=L + 80, y=WORD_Y + (cap + 14) * (1 - rise)), sk.fill(BONE))
        c.restore()
    age = t - T_YOUR
    if age < -FALL:
        return
    _, sy = squash(age, 0.2, 10.0, 28.0)
    c.save()
    c.translate(W / 2, base + (-900 * (1 - S.ease_in(1 + age / FALL, 2)) if age < 0 else 0))
    c.scale(1.0, sy)                                              # it is as wide as the grid already
    c.drawRect(skia.Rect.MakeLTRB(-ROOF_W / 2, -BAR, ROOF_W / 2, 0), sk.fill(BONE))
    c.drawPath(sk.poly([(-ROOF_W / 2, -BAR), (0, -BAR - ROOF_H), (ROOF_W / 2, -BAR)]), sk.fill(PURPLE))
    _, _, [(your, ybox)] = setting(("YOUR",), size=150.0)
    c.drawPath(sk.xf(your, x=-(ybox[0] + ybox[2]) / 2, y=-BAR - 30), sk.fill(INK))
    c.restore()


def count_rows():
    """The column under the house, top to bottom: (words, their times, ink width or None for a small row)."""
    w = {word: a - LEAD for word, a, _ in S.LINES[0]["words"]}
    return [(("GOT",), (w["got"],), None),
            (("FIVE",), (w["five"],), R - COL),
            (("AND", "A"), (w["and"], w["a"]), None),
            (("HALF",), (w["half"],), R - COL),
            (("BATHS:",), (w["baths:"],), R - COL)]


def stack(c, t, rows, x, bottom, gap, colour, rule=None, small=68.0):
    """Rows of type that pile up from `bottom`: every word comes up from behind its own baseline, and a
    row's first word shoves the rows before it up the column."""
    made = [times[0] for _, times, _ in rows]
    sets = [setting(words, width=width) if width else setting(words, size=small) for words, _, width in rows]
    for i, ((words, times, width), (size, cap, parts)) in enumerate(zip(rows, sets)):
        if t < made[i]:
            continue
        y = bottom - sum((sets[j][1] + gap) * S.back((t - made[j]) / 0.13, 1.2)
                         for j in range(i + 1, len(rows)) if t >= made[j])
        for (path, box), tw in zip(parts, times):
            draw(c, path, box, x, y, sk.fill(colour), "rise", t - tw, lift=cap * 1.15)
        if rule and not width:                                    # a small row is filled out with a bar
            x0 = x + parts[-1][1][2] + 0.3 * cap
            grow = S.ease_out((t - times[-1] - 0.04) / 0.14)
            if grow > 0:
                c.drawRect(skia.Rect.MakeLTRB(x0, y - cap * 0.64, x0 + (rule[0] - x0) * grow, y - cap * 0.36), sk.fill(rule[1]))


def line1(c, t):
    c.clear(sk.rgb(INK))
    tag(c, GREEN)
    # the house: whole, until "got" sends it up to the head of the column
    k = S.ease_out((t - T_GOT) / 0.14) if t >= T_GOT else 0.0
    s = 1 + (HOUSE_K - 1) * k
    c.save()
    c.translate(L + (COL - L) * k, HOUSE_TOP + (TOP - HOUSE_TOP) * k)
    c.scale(s, s)
    c.translate(-L, -HOUSE_TOP)
    house(c, t)
    c.restore()
    if t < T_GOT:
        return
    stack(c, t, count_rows(), COL, BOT, 26, BONE, rule=(R, PURPLE))

    # the number: 5 on "five", the half on "half", each a stamp; underlined on "baths"
    _, _, [(five, fbox), (half, hbox)] = setting(("5", "½"), size=NUM, track=-0.004, space=0.0)
    base, pulse = TOP + 0.728 * NUM, 1 + 0.012 * S.thump(t)
    c.save()
    c.translate(L, base)
    c.scale(pulse, pulse)
    draw(c, five, fbox, 0, 0, sk.fill(PURPLE), "slam", t - at("tubs")[0], near=0.14)
    draw(c, half, hbox, 0, 0, sk.fill(PURPLE), "slam", t - at("half"), near=0.14)
    c.restore()
    under = S.ease_out((t - at("baths")) / 0.1)
    if under > 0:
        c.drawRect(skia.Rect.MakeLTRB(L, base + 34, L + (hbox[2]) * under, base + 54), sk.fill(BONE))
    slot = (CARD - 40 - L) / 6
    for i in range(6):
        t0 = at("tubs")[i] if i < 5 else at("half")
        hop = 10 * S.thump(t, 9.0) if t - t0 > 0.25 else 0.0
        tub(c, L + slot * (i + 0.5), BOT - hop, slot - 24, BONE, INK, half=i == 5, k=S.pop(t, t0, 0.18, 2.4))

    # the aside: a card comes across the column, in another voice
    if t >= T_HOW:
        x0 = W - (W - CARD) * S.ease_out((t - T_HOW) / 0.1)
        c.save()
        c.clipRect(skia.Rect.MakeLTRB(x0, 0, W, H))
        c.clear(sk.rgb(BONE))
        c.translate(x0 - CARD, 0)
        card(c, t)
        c.restore()


def card(c, t):
    """The invitation: a flag for a crest, hairlines, and two words written out in script."""
    cx = (CARD + 62 + R) / 2
    for y in (150, 930):
        c.drawLine(CARD + 62, y, R, y, sk.stroke(INK, 3, cap="butt"))
        c.drawPath(sk.xf(sk.rect(-11, -11, 11, 11), cx, y, rot=45), sk.fill(INK))
        c.drawPath(sk.xf(sk.rect(-5, -5, 5, 5), cx, y, rot=45), sk.fill(BONE))
    flag(c, cx - 48, 425, 238, t, T_AUSTERE + 0.02)
    c.save()
    c.rotate(-4, cx, 640)
    for word, t0, dur, size, y in (("how", T_HOW, 0.12, 134.0, 562), ("austere;", T_AUSTERE, 0.2, 160.0, 738)):
        if t < t0:
            continue
        _, _, [(path, (l, top, r, b))] = setting((word,), font="script", size=size, track=0.0)
        x = cx - (l + r) / 2
        c.save()                                                  # written out, left to right
        c.clipRect(skia.Rect.MakeLTRB(x + l - 10, y + top - 20, x + l + (r - l + 20) * S.ramp(t, t0, dur), y + b + 20))
        c.drawPath(sk.xf(path, x=x, y=y), sk.fill(INK))
        c.restore()
    swash = sk.curve([(cx - 236, 792), (cx - 110, 810), (cx + 40, 784), (cx + 180, 798), (cx + 244, 778)], closed=False)
    done = S.ease_out((t - T_AUSTERE - 0.14) / 0.14)
    if done > 0:
        c.drawPath(sk.part(swash, 0, done), sk.stroke(PURPLE, 9))
    c.restore()


# --- line 2: the nought -------------------------------------------------------------------------

GAP2 = 26
ROWS2 = (("FIVE",), ("AND", "A", "HALF"), ("MORE", "THAN"), ("I'VE", "HAD"), ("ALL", "YEAR."))
# The second line's column is as wide as makes its five rows fill the band from TOP to BOT exactly.
STACK2 = 1000 * (BOT - TOP - GAP2 * (len(ROWS2) - 1)) / sum(setting(r, width=1000)[1] for r in ROWS2)
T_HAD = at("had")
T_YEAR = at("year")


def line2_rows():
    times, rows = iter(a - LEAD for _, a, _ in S.LINES[1]["words"]), []
    for words in ROWS2:
        rows.append((words, tuple(next(times) for _ in words), STACK2))
    return rows


@lru_cache(maxsize=None)
def nought():
    size = (BOT - TOP) / 0.747
    _, _, [(path, box)] = setting(("0",), size=size, track=0.0)
    return path, box


def shake(t):
    """The frame's jolt when the nought lands."""
    a = t - T_HAD
    if a < 0:
        return 0.0, 0.0
    k = 16 * math.exp(-16 * a)
    return k * math.cos(a * 95), k * math.sin(a * 71)


def fly(c, x, y, t, seed, k=1.9):
    """A fly as punctuation: a full stop for the body, two apostrophes for wings, beating."""
    beat = 1 if (S.frame_no(t) + seed) % 2 else -1
    for side in (-1, 1):
        wing = sk.xf(sk.oval(0, -13 * k, 7 * k, 14 * k), x=x, y=y - 4 * k, rot=side * (38 + 16 * beat))
        c.drawPath(wing, sk.fill(BONE))
        c.drawPath(wing, sk.stroke(INK, 3.5))
    c.drawPath(sk.oval(x, y, 11 * k, 9 * k), sk.fill(INK))
    c.drawPath(sk.oval(x, y, 11 * k, 9 * k), sk.stroke(BONE, 2.5))


# Where the six tubs go when the nought lands: (direction, speed), each away from the type.
FLUNG = [((-0.45, -1.0), 2500), ((0.7, -1.0), 2700), ((-0.22, -1.0), 2900), ((1.0, -0.3), 2600),
         ((-0.3, 1.0), 2300), ((0.8, 0.9), 2500)]


def line2(c, t):
    c.clear(sk.rgb(GREEN))
    dx, dy = shake(t)
    c.save()
    c.translate(dx, dy)
    tag(c, INK)
    stack(c, t, line2_rows(), L, BOT, GAP2, INK)

    path, box = nought()
    zx = R - box[2]                                               # the nought's ink ends on the right margin
    zcx, cy = zx + (box[0] + box[2]) / 2, (TOP + BOT) / 2
    landed = t - T_HAD

    def tubs(flying):
        """His five and a half, counted again; then the nought lands on them and they go."""
        for i in range(6):
            t0 = (T_CUT + 0.045 * i) if i < 5 else S.LINES[1]["words"][3][1] - LEAD
            x, base, rot = zcx + (-190 if i % 2 == 0 else 190), TOP + (BOT - TOP) * (i // 2 + 1) / 3 - 34, 0.0
            if flying:
                (ux, uy), speed = FLUNG[i]
                n = math.hypot(ux, uy)
                x, base = x + ux / n * speed * landed, base + uy / n * speed * landed + 900 * landed * landed
                rot = (1 if ux > 0 else -1) * (700 + 500 * S.rnd("spin", i)) * landed
            elif t >= at("ive"):                                  # they know
                x += 6 * (S.rnd("jx", i, S.frame_no(t)) - 0.5)
                base += 4 * (S.rnd("jy", i, S.frame_no(t)) - 0.5)
            hop = 12 * S.thump(t, 9.0) if t - t0 > 0.25 and not flying else 0.0
            tub(c, x, base - hop, 300, INK, GREEN, half=i == 5, k=S.pop(t, t0, 0.18, 2.4), rot=rot,
                edge=5.0 if flying else 0.0)

    if landed < 0:
        tubs(False)
    if landed >= -FALL:
        pulse = 1 + 0.014 * S.thump(t) * (landed > 0.5)
        c.save()
        c.translate(zcx, BOT)
        c.scale(pulse, pulse)
        c.translate(-zcx, -BOT)
        draw(c, path, box, zx, BOT - box[3], sk.fill(INK), "drop", landed)
        c.restore()
    if 0 <= landed < 0.6:
        tubs(True)

    # the flies find him on "year": two in the nought's eye, three round the outside of it
    haunts = [((zcx - 6, cy - 120), (62, 56), (0.0, -1.0)), ((zcx + 8, cy + 135), (60, 52), (0.2, 1.0)),
              ((zx + 30, TOP + 30), (52, 40), (-0.6, -1.0)), ((R - 26, TOP + 56), (38, 46), (1.0, -0.7)),
              ((zx - 20, cy + 306), (40, 44), (-0.4, 1.0))]
    for i, ((ax, ay), (rx, ry), (ux, uy)) in enumerate(haunts):
        age = t - T_YEAR - 0.06 * i
        if age < 0:
            continue
        speed = 5.2 + 1.6 * S.rnd("fs", i)
        away = (1 - S.ease_out(age / 0.32)) * 800                 # it comes in from off the sheet

        def pos(ph, ax=ax, ay=ay, rx=rx, ry=ry, i=i, ox=ux * away, oy=uy * away):
            return (ax + ox + rx * math.cos(ph) + 0.35 * rx * math.cos(2.3 * ph + i),
                    ay + oy + ry * math.sin(1.3 * ph) + 0.4 * ry * math.sin(2.9 * ph))

        ph = t * speed + i * 2.1
        for j in range(1, 8):                                     # the dotted line it leaves
            px, py = pos(ph - j * 0.2)
            c.drawCircle(px, py, max(2.5, 6.5 - 0.5 * j), sk.fill(INK, 0.9 - 0.1 * j))
        fx, fy = pos(ph)
        fly(c, fx, fy, t, i)
    c.restore()


# --- the frame ----------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def grain():
    """A little tooth, the same on every frame: ink on paper, not pixels on glass."""
    return (sk.grain(W, H, 11, 1, -5.0, 5.0) + sk.grain(W, H, 12, 2, -3.0, 3.0))[..., None]


def frame(t):
    surf = sk.surface(W, H)
    c = surf.getCanvas()
    if t < T_CUT:
        line1(c, t)
    else:
        line2(c, t)
    a = sk.array(surf)[..., :3].astype(np.float32) + grain()
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
