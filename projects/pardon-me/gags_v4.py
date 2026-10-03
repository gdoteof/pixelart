"""Verse 4: Bibi's closing verse, the knockout. He lectures from the flip chart; Trump heckles from the desk.

Lines 0-1 audit Trump: a pie chart of what's real (a sliver of hair, the rest FAKE), then a pop quiz,
WHICH IS REAL?, answered E) NONE, and Bibi wears a mortarboard from there on. Lines 2-4 put the hurricane
forecast up: the Sharpie loop goes on, reaches ALABAMA and turns into a small pink brain. In line 4 the
right screen replays a foot nudging a golf ball into the cup and the caddie pops up behind the desk with
his plea deal; line 5 is the scorecard, 34 on hole three. Line 6 diagrams the Nobel letter going over and
a 17% tariff coming back, line 7 puts 17% on a heart until it cracks and turns THE ART OF THE DEAL into
STEAL, line 8 is the final diagram: a red line with TRUMP in gold letters under it, graded F. Line 9 is
the mic drop (Bibi caps the marker and lets it fall, the verse's one close shot), then the escalator cam
on the right screen stops dead, OUT OF ORDER, and Trump steams while the hall gets to its feet.
In the gaps Trump answers back: PERFECT SCORE!, IT'S DISCOUNTED!, and at last nothing at all.
"""
import art
import art_v4 as A4
import hall
from characters import figure
from gagkit import (C, INK, PRESS, PRESS16, SILK, Image, ImageDraw, anchor, back_out, bubble, check, circle_pts,
                    clamp, cross_out, ease_in, ease_out, face, flip, gag, line_t, lru_cache, marker_arrow, math,
                    outline_text, page_title, paste, paste_rot, pop_dy, pose, ramp, ring, rnd, sparkle, stick_figure,
                    stroke, underline, write)
from timeline import section_end


def W(idx, pat=None, n=0):
    """When a word of verse 4's line `idx` starts (the line itself without a pattern)."""
    return line_t("v4", idx, pat, n)


# line 0: the pie chart
L0, T0_REAL, T0_ONLY, T0_THING = W(0), W(0, "real"), W(0, "only"), W(0, "thing")
T0_ABOUT, T0_THAT, T0_IS = W(0, "about"), W(0, "that"), W(0, r"^is", 1)
# line 1: the pop quiz
L1, T1_LETS, T1_POP, T1_QUIZ = W(1), W(1, "let"), W(1, "pop"), W(1, "quiz")
QUIZ = [("A) TAN", W(1, "tan")), ("B) HEIGHT", W(1, "height")), ("C) MONEY", W(1, "money")),
        ("D) DEGREE", W(1, "degree"))]
# lines 2-3: the hurricane map
T2_BOMB, T2_YOU, T2_SHARPIE = W(2, "bomb"), W(2, "^you", 1), W(2, "sharpie")
T3_LOOP, T3_ALABAMA, T3_SHAPE = W(3, "loop"), W(3, "alabama"), W(3, "shape")
T3_YOUR, T3_BRAIN = W(3, "your"), W(3, "brain")
# line 4: the caddie
T4_GOLF, T4_SO, T4_CADDIE, T4_COPPED, T4_PLEA = W(4, "golf"), W(4, "^so"), W(4, "caddie"), W(4, "copped"), \
    W(4, "plea")
# line 5: the scorecard
L5, T5_SCORE, T5_HOLE, T5_THREE = W(5), W(5, "score"), W(5, "hole"), W(5, "three")
# line 6: the Nobel for a tariff
L6, T6_BACKED, T6_YOU, T6_NOBEL = W(6), W(6, "backed"), W(6, "^you", 0), W(6, "nobel")
T6_SENT, T6_TARIFF, T6_BACK, T6_SOME, T6_DEAL = W(6, "sent"), W(6, "tariff"), W(6, r"^back\."), W(6, "some"), \
    W(6, "deal")
# line 7: 17% on friendship, the art of the steal
L7, T7_FRIEND, T7_SEV2, T7_FRIEND2 = W(7), W(7, "friend"), W(7, "seventeen", 1), W(7, "friend", 1)
T7_THATS, T7_ART, T7_STEAL = W(7, "that's"), W(7, "art"), W(7, "steal")
# line 8: the final diagram
T8_DIAGRAM, T8_RED, T8_LINE = W(8, "diagram"), W(8, "red"), W(8, "line")
T8_YOUR, T8_UNDER, T8_IT = W(8, "your"), W(8, "under"), W(8, r"^it\.")
# line 9: the mic drop and the escalator
L9, T9_ME, T9_YOU, T9_NOW = W(9), W(9, "me"), W(9, "you"), W(9, "now")
T9_TAKE, T9_ESC, T9_OH, T9_IT, T9_QUIT = W(9, "take"), W(9, "escalator"), W(9, "oh"), W(9, "^it"), W(9, "quit")
T9_HIT = T9_QUIT + 0.04
# the knockout holds past the verse's end, right up to where the outro's first gag takes over (its 0.12 s lead)
END9 = line_t("outro", 0) - 0.12 - section_end("v4")

# the gaps, when Trump answers back
GAP5 = (W(5, "three") + 0.75, W(6) - 0.2)
GAP6 = (W(6, "deal") + 0.75, W(7) - 0.25)
GAP8 = (W(8, r"^it\.") + 0.55, W(9) - 0.2)


# --- shared helpers ------------------------------------------------------------------------------------

def pages(c, *spec):
    """Put up the latest page of `spec` [(t, draw), ...] whose time has come (no flip animation for one
    that went up earlier); returns its draw function, or None."""
    cur = None
    for t, fn in spec:
        if c.t >= t:
            cur = (t, fn)
    if cur is None:
        return None
    flip(c, cur[0])
    return cur[1]


def professor(c):
    """From the pop quiz on, Bibi lectures in a mortarboard."""
    if c.t >= T1_POP:
        c.st["bibi"]["hat"] = "mortar"


def heckle(c, t0, t1, arm=None, **kw):
    """Setup for Trump answering back from the desk between t0 and t1: a pose, and his mouth going for
    the first 0.7 s. Returns the bubble's age, or None outside the window."""
    if not t0 <= c.t < t1:
        return None
    age = c.t - t0
    c.hit_react["trump"] = False
    if arm:
        pose(c, "trump", arm=arm, **kw)
    if age < 0.7:
        c.st["trump"]["mouth"] = ("open", "wide", "o", "open", "closed")[int(age * 12) % 5]
    return age


def say(c, s, age, dx=-20):
    """Trump's speech bubble over the desk, popping in."""
    hx, hy = anchor(c, "trump", "head")
    dy = pop_dy(age, 0.15, 6) or 0
    bubble(c.world, hx + dx, hy - 17 + dy, [s], tail=(hx - 7, hy - 9), fnt=SILK, pad=3, line_h=8, text_dy=-4)


# --- line 0: what's real ---------------------------------------------------------------------------------

PIE = (25, 35, 18)                       # the pie chart's centre and radius, on the page
SLIVER = (-66, -48)                      # the hair's slice, in degrees clockwise from east


def pie_pt(a, r=None):
    cx, cy, R = PIE
    r = R if r is None else r
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


@lru_cache(maxsize=1)
def pie_mask():
    """Where the hatching goes: the pie outside the hair's sliver."""
    cx, cy, R = PIE
    m = Image.new("L", (90, 58), 0)
    ImageDraw.Draw(m).pieslice((cx - R + 1, cy - R + 1, cx + R - 1, cy + R - 1), SLIVER[1] + 3, SLIVER[0] + 357,
                               fill=255)
    return m


def hatch(page, p, color="red"):
    """Red marker hatching over the FAKE part of the pie, scribbled in from top left as p goes 0 -> 1."""
    lines = list(range(-60, 70, 3))
    n = int(len(lines) * clamp(p, 0, 1))
    if n <= 0:
        return
    layer = Image.new("RGBA", page.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for b in lines[:n]:
        d.line([(0, b), (90, b + 90 * 0.7)], fill=C["mk_red"] + (255,))
    a = layer.getchannel("A")
    layer.putalpha(Image.composite(a, Image.new("L", a.size, 0), pie_mask()))
    page.paste(layer, (0, 0), layer)


def page_pie(pg, t):
    cx, cy, R = PIE
    page_title(pg, "WHAT'S REAL?", "black", t - L0, y=2, underline_color="blue")
    stroke(pg, circle_pts(cx, cy, R, start=-90, turns=1.0, n=48), "black", ramp(t, T0_REAL, T0_REAL + 0.3))
    if t >= T0_ONLY:
        k = ramp(t, T0_ONLY, T0_ONLY + 0.12)
        for a in SLIVER:
            stroke(pg, [(cx, cy), pie_pt(a)], "black", k)
    if t >= T0_ONLY + 0.12:
        wedge = [(cx, cy)] + [pie_pt(SLIVER[0] + (SLIVER[1] - SLIVER[0]) * i / 6) for i in range(7)]
        ImageDraw.Draw(pg).polygon(wedge, fill=C["mk_green"], outline=C["mk_black"])
    if t >= T0_THING:
        mid = (SLIVER[0] + SLIVER[1]) / 2
        stroke(pg, [pie_pt(mid, R - 3), pie_pt(mid, R + 4), (52, 16)], "green", ramp(t, T0_THING, T0_THING + 0.1))
        write(pg, (55, 13), "HAIR", "green", t - T0_THING - 0.08, cps=30, bold=True)
        check(pg, 78, 18, "green", ramp(t, T0_THING + 0.25, T0_THING + 0.4), size=6)
    hatch(pg, ramp(t, T0_ABOUT, T0_THAT))
    if t >= T0_THAT:
        stroke(pg, [pie_pt(25, R * 0.55), (44, 42), (52, 42)], "red", ramp(t, T0_THAT, T0_THAT + 0.1))
        write(pg, (55, 38), "FAKE", "red", t - T0_THAT - 0.08, cps=26, fnt=PRESS)


@gag("v4", 0)
def hair_real(c, L):
    pg = pages(c, (L0, page_pie))
    if 179.5 <= c.t < T0_ABOUT + 0.2:                       # he takes it as a compliment
        pose(c, "trump", arm="up")
        face(c, "trump", mouth="smirk", eyes="squint")
    yield "chart"
    if pg:
        pg(c.page, c.t)


# --- line 1: the pop quiz --------------------------------------------------------------------------------

def page_quiz(pg, t):
    write(pg, (45, 2), "WHICH IS REAL?", "black", t - L1, cps=40, anchor="ma", bold=True)
    if t > L1 + 0.4:
        underline(pg, 8, 82, 10, "blue", ramp(t, L1 + 0.4, L1 + 0.6))
    for i, (s, t0) in enumerate(QUIZ):
        write(pg, (20, 12 + 8 * i), s, "black", t - t0 + 0.04, cps=32)
    write(pg, (45, 46), "E) NONE", "red", t - T1_LETS, cps=24, fnt=PRESS, anchor="ma")
    ring(pg, 45, 50, 33, 7, "red", ramp(t, T1_QUIZ - 0.06, T1_QUIZ + 0.16), width=1)


@gag("v4", 1)
def pop_quiz(c, L):
    pg = pages(c, (L0, page_pie), (L1, page_quiz))
    professor(c)
    yield "chart"
    if pg:
        pg(c.page, c.t)
    yield "mid"
    if 0 <= c.t - T1_POP < 0.35:                            # the mortarboard goes on
        hx, hy = anchor(c, "bibi", "top")
        k = int((c.t - T1_POP) * 20) % 2
        sparkle(c.world, hx - 9, hy - 3 - k, 2, C["gold_hi"])
        sparkle(c.world, hx + 12, hy - 1 + k, 1, C["gold_hi"])


# --- lines 2-4: the hurricane map, the Sharpie loop, the brain ----------------------------------------------

LOOP = [(51, 29), (45, 33), (37, 34), (30, 32), (27, 27), (30, 22), (37, 21), (44, 22), (49, 25)]
WRINKLES = [[(30, 28), (33, 25), (36, 28), (39, 25)], [(32, 31), (35, 29), (38, 31), (42, 28), (46, 30)],
            [(33, 24), (37, 25), (41, 23), (45, 25)], [(41, 27), (44, 29), (47, 27)]]
BRAIN, BRAIN_SH = (246, 172, 188), (196, 96, 128)


def smooth(pts, closed=True, n=6):
    """A Catmull-Rom curve through pts (closed by default), for hand-drawn loops."""
    P = list(pts) + (pts[:3] if closed else [])
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i:i + 4]
        for k in range(n):
            s = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * s
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * s * s
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * s ** 3) for j in (0, 1)))
    return out + out[:1]


LOOP_FOOT = (50, 27)                     # where the loop leaves the cone; it swells out from here


@lru_cache(maxsize=None)
def loop_curve(k=20):
    """The Sharpie loop at k/20 of its full reach."""
    fx, fy = LOOP_FOOT
    return smooth([(fx + (x - fx) * k / 20, fy + (y - fy) * k / 20) for x, y in LOOP])


def page_map(pg, t):
    pg.paste(A4.forecast_map(), (0, 0))
    spin = A4.storm_icon(int(t * 10) % 8)
    pg.paste(spin, (A4.STORM[0] - 6, A4.STORM[1] - 6), spin)
    loop = loop_curve(11 + round(9 * ease_out(ramp(t, T3_LOOP, T3_ALABAMA + 0.1))))   # "one loop to Alabama"
    if t >= T3_BRAIN:                                         # it was a brain all along
        ImageDraw.Draw(pg).polygon(loop, fill=BRAIN)
        for i, w in enumerate(WRINKLES):
            stroke(pg, w, BRAIN_SH, ramp(t, T3_BRAIN + 0.04 * i, T3_BRAIN + 0.12 + 0.04 * i))
    stroke(pg, loop, "black", ramp(t, T2_SHARPIE, T2_SHARPIE + 0.38), width=2)
    if t >= T3_SHAPE:
        stroke(pg, loop, "red", ramp(t, T3_SHAPE, T3_SHAPE + 0.3), width=1)
    if t >= T3_ALABAMA - 0.05:
        box = write(pg, (3, 10), "ALABAMA", "black", t - T3_ALABAMA + 0.05, cps=30, bold=True)
        if t >= T3_YOUR:
            stroke(pg, [(box[0] - 1, box[1] + 4), (box[2] + 1, box[1] + 3)], "red", ramp(t, T3_YOUR, T3_YOUR + 0.12),
                   width=2)
    if t >= T3_BRAIN:
        write(pg, (3, 39), "YOUR BRAIN", "red", t - T3_BRAIN, cps=34, bold=True)
        write(pg, (3, 48), "(ACTUAL SIZE)", "black", t - T3_BRAIN - 0.3, cps=34)


@gag("v4", 2)
def sharpie(c, L):
    pg = pages(c, (L1, page_quiz), (T2_YOU, page_map))
    professor(c)
    if T2_BOMB - 0.15 <= c.t < T2_YOU:                       # "you call my bomb a CARTOON?"
        pose(c, "bibi", arm="palm")
        face(c, "bibi", brows="angry")
    elif T2_YOU <= c.t < T2_YOU + 1.4:                       # presenting the map behind him
        pose(c, "bibi", arm="palm", far="out")
    yield "chart"
    if pg:
        pg(c.page, c.t)


@gag("v4", 3)
def alabama(c, L):
    pg = pages(c, (T2_YOU, page_map))
    professor(c)
    yield "chart"
    if pg:
        pg(c.page, c.t)


# --- line 4: the foot wedge and the caddie -----------------------------------------------------------------

CADDIE_X = 291                         # the caddie's left edge, behind the desk's right end
T_DUCK = L5 + 0.75                     # when he ducks back down


def caddie_draw(c):
    up = back_out(ramp(c.t, T4_CADDIE - 0.14, T4_CADDIE + 0.08)) - ease_in(ramp(c.t, T_DUCK, T_DUCK + 0.22))
    if up <= 0.01:
        return
    spr = A4.caddie(-1)
    top = 142 + 2 - round(up * 48)
    c.world.paste(spr, (CADDIE_X, top), spr)
    paper = A4.plea_deal()
    lift = ease_out(ramp(c.t, T4_COPPED, T4_PLEA))
    py = top + 32 - round(lift * 16) - (2 if 0 <= c.t - T4_PLEA < 0.12 else 0)
    c.world.paste(paper, (CADDIE_X, py), paper)


def golf_screen(c, img, box):
    A4.golf_replay(img, box, c.t, T4_SO, T4_SO + 0.4)


@gag("v4", 4)
def caddie(c, L):
    pg = pages(c, (T2_YOU, page_map))
    professor(c)
    if T4_GOLF - 0.1 <= c.t < T4_CADDIE + 0.15:
        c.screens["R"] = golf_screen
    if c.t >= T4_PLEA - 0.1:
        face(c, "trump", eyes="side")
    yield "chart"
    if pg:
        pg(c.page, c.t)
    yield "mid"
    caddie_draw(c)


# --- line 5: the scorecard ------------------------------------------------------------------------------

GRID_X = (1, 26, 42, 58, 74, 89)
GRID_Y = (13, 23, 33, 48)
SCORE_ROWS = (("HOLE", "1", "2", "3", "4"), ("PAR", "4", "3", "4", "5"), ("DJT", "1", "1", "", "1"))
PRINT = (120, 130, 160)


def page_score(pg, t):
    write(pg, (45, 2), "SCORECARD", "black", t - L5 + 0.1, cps=40, anchor="ma", bold=True)
    d = ImageDraw.Draw(pg)
    for y in GRID_Y:
        d.line([(GRID_X[0], y), (GRID_X[-1], y)], fill=PRINT)
    for x in GRID_X:
        d.line([(x, GRID_Y[0]), (x, GRID_Y[-1])], fill=PRINT)
    d.rectangle((GRID_X[0] + 1, GRID_Y[0] + 1, GRID_X[-1] - 1, GRID_Y[1] - 1), fill=(222, 236, 222))
    for r, row in enumerate(SCORE_ROWS):
        y = GRID_Y[r] + (2 if r < 2 else 5)
        for i, s in enumerate(row):
            if not s:
                continue
            x = GRID_X[0] + 2 if i == 0 else (GRID_X[i] + GRID_X[i + 1]) // 2 + 1
            write(pg, (x, y), s, "black" if i == 0 or r < 2 else "blue", anchor="la" if i == 0 else "ma")
    cx, cy = (GRID_X[3] + GRID_X[4]) // 2, (GRID_Y[2] + GRID_Y[3]) // 2
    write(pg, (cx + 1, cy - 3), "34", "blue", t - L5, cps=14, fnt=PRESS, anchor="ma")
    if t >= T5_SCORE:
        underline(pg, GRID_X[0] + 2, GRID_X[1] - 3, GRID_Y[3] - 2, "red", ramp(t, T5_SCORE, T5_SCORE + 0.15))
    ring(pg, cx + 1, cy + 1, 12, 9, "red", ramp(t, T5_THREE - 0.08, T5_THREE + 0.16), width=2)
    if t >= T5_THREE + 0.3:
        write(pg, (cx + 1, GRID_Y[3] + 3), "+30", "red", t - T5_THREE - 0.3, cps=20, anchor="ma", bold=True)


@gag("v4", 5)
def hole_three(c, L):
    pg = pages(c, (T2_YOU, page_map), (L5 - 0.06, page_score))
    professor(c)
    age = heckle(c, *GAP5, arm="pinch")
    yield "chart"
    if pg:
        pg(c.page, c.t)
    yield "mid"
    caddie_draw(c)
    yield "front"
    if age is not None:
        say(c, "PERFECT SCORE!", age)


# --- line 6: a Nobel over, a tariff back --------------------------------------------------------------------

def heart_pts(cx, cy, w, h, n=40):
    """A heart outline (the classic parametric one), starting at its top notch."""
    pts = []
    for k in range(n + 1):
        a = 2 * math.pi * k / n
        x = 16 * math.sin(a) ** 3
        y = 13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)
        pts.append((cx + x * w / 32, cy - y * h / 30))
    return pts


def envelope(pg, x, y, p):
    """A letter in an envelope with a red heart on it."""
    if p <= 0:
        return
    stroke(pg, [(x, y), (x + 11, y), (x + 11, y + 7), (x, y + 7), (x, y)], "black", p / 0.6)
    if p > 0.6:
        stroke(pg, [(x, y), (x + 5.5, y + 4), (x + 11, y)], "black", (p - 0.6) / 0.4)
    if p >= 1:
        ImageDraw.Draw(pg).polygon(heart_pts(x + 5.5, y + 4, 6, 5, 16), fill=C["mk_red"])


def page_deal(pg, t):
    k = ramp(t, L6, T6_BACKED + 0.1)
    stick_figure(pg, 11, 55, "black", k, h=22, hair="bibi")
    stick_figure(pg, 79, 55, "black", k, h=22, hair="trump")
    marker_arrow(pg, (19, 31), (70, 31), "black", ramp(t, T6_YOU, T6_NOBEL))
    envelope(pg, 22, 21, ramp(t, T6_NOBEL - 0.25, T6_NOBEL + 0.05))
    write(pg, (37, 21), "NOBEL", "black", t - T6_NOBEL, cps=30, bold=True)
    marker_arrow(pg, (70, 43), (20, 43), "red", ramp(t, T6_SENT, T6_BACK))
    write(pg, (45, 46), "17% TARIFF", "red", t - T6_TARIFF, cps=30, anchor="ma", bold=True)
    write(pg, (45, 2), "SOME DEAL.", "black", t - T6_SOME, cps=30, anchor="ma", bold=True)
    if t >= T6_DEAL:
        underline(pg, 18, 72, 11, "red", ramp(t, T6_DEAL, T6_DEAL + 0.2), wave=1)


@gag("v4", 6)
def nobel_tariff(c, L):
    pg = pages(c, (L5 - 0.06, page_score), (L6 - 0.06, page_deal))
    professor(c)
    age = heckle(c, *GAP6, arm="up")
    yield "chart"
    if pg:
        pg(c.page, c.t)
    yield "front"
    if age is not None:
        say(c, "IT'S DISCOUNTED!", age, dx=-24)


# --- line 7: 17% on friendship, the art of the steal ---------------------------------------------------------

HEART = (25, 33, 32, 28)


def page_heart(pg, t):
    cx, cy, w, h = HEART
    pts = heart_pts(cx, cy, w, h)
    if t >= T7_FRIEND2:                                       # the second time round, it cracks
        k = ramp(t, T7_FRIEND2, T7_FRIEND2 + 0.2)
        gap = round(k * 2)
        left = [(x - gap if x <= cx else x, y) for x, y in pts]
        right = [(x + gap if x > cx else x, y) for x, y in pts]
        crack = [(cx, cy - 4), (cx - 3, cy), (cx + 2, cy + 4), (cx - 2, cy + 8), (cx + 1, cy + 12), (cx, cy + 15)]
        stroke(pg, [p for p in left if p[0] <= cx], "red")
        stroke(pg, [p for p in right if p[0] >= cx], "red")
        stroke(pg, [(x - gap, y) for x, y in crack], "black", k * 1.5)
        stroke(pg, [(x + gap, y) for x, y in crack], "black", k * 1.5)
    else:
        stroke(pg, pts, "red", ramp(t, L7 - 0.12, L7 + 0.2))
    # the price tag on a string, 17%
    if t >= L7:
        p = ramp(t, L7, L7 + 0.2)
        stroke(pg, [(36, 23), (44, 19), (52, 19), (58, 21)], "black", p)
        tag = [(58, 21), (62, 16), (84, 16), (84, 27), (62, 27), (58, 21)]
        stroke(pg, tag, "black", p)
        write(pg, (66, 18), "17%", "black", t - L7 - 0.1, cps=14, bold=True)
    if t >= T7_SEV2:
        cross_out(pg, (65, 18, 85, 25), "red", ramp(t, T7_SEV2, T7_SEV2 + 0.15))
        write(pg, (64, 33), "17%", "red", t - T7_SEV2 - 0.1, cps=8, fnt=PRESS16, anchor="ma")
    write(pg, (45, 2), "FRIENDSHIP?", "black", t - T7_FRIEND, cps=30, anchor="ma", bold=True)


def page_book(pg, t):
    book = A4.book_cover()
    pg.paste(book, (1, 2), book)
    if t >= T7_ART:
        cross_out(pg, (16, 22, 38, 30), "red", ramp(t, T7_ART, T7_ART + 0.25), width=2)
    if t >= T7_STEAL - 0.1:
        write(pg, (68, 22), "STEAL", "red", t - T7_STEAL + 0.1, cps=30, fnt=PRESS, anchor="ma")
        marker_arrow(pg, (40, 26), (49, 26), "red", ramp(t, T7_STEAL - 0.1, T7_STEAL + 0.05))
        underline(pg, 48, 88, 32, "red", ramp(t, T7_STEAL + 0.2, T7_STEAL + 0.4))


@gag("v4", 7)
def art_of_the_steal(c, L):
    pg = pages(c, (L7 - 0.12, page_heart), (T7_THATS, page_book))
    professor(c)
    yield "chart"
    if pg:
        pg(c.page, c.t)


# --- line 8: the final diagram ------------------------------------------------------------------------------

def page_final(pg, t):
    page_title(pg, "FINAL DIAGRAM", "blue", t - T8_DIAGRAM, y=2)
    stroke(pg, [(4, 29), (86, 30)], "red", ramp(t, T8_RED, T8_LINE + 0.12), width=3)
    n = int(clamp((t - T8_YOUR) / 0.06, 0, 5))
    if n:                                                     # his name, in gold letters, like on his towers
        outline_text(pg, (20, 35), "TRUMP"[:n], PRESS, C["gold"], INK)
    if t >= T8_UNDER:
        marker_arrow(pg, (11, 19), (14, 40), "red", ramp(t, T8_UNDER, T8_UNDER + 0.18))
    if t >= T8_IT - 0.05:
        write(pg, (76, 38), "F", "red", 1e9, fnt=PRESS16, anchor="ma")
        ring(pg, 77, 45, 10, 10, "red", ramp(t, T8_IT - 0.05, T8_IT + 0.15), width=1)


@gag("v4", 8)
def red_line(c, L):
    pg = pages(c, (T7_THATS, page_book), (T8_DIAGRAM, page_final))
    professor(c)
    age = heckle(c, *GAP8, arm="down")
    if age is not None:
        face(c, "trump", eyes="wide", brows="worried")
        c.st["trump"]["mouth"] = "o"
        c.st["trump"]["sweat"] = True
    yield "chart"
    if pg:
        pg(c.page, c.t)
    yield "front"
    if age is not None:
        say(c, "...", age, dx=-8)


# --- line 9: the mic drop, the escalator, the knockout ------------------------------------------------------

@lru_cache(maxsize=1)
def release_pt():
    """Where Bibi's raised fist lets go of the marker (world pixels)."""
    _, a = figure("bibi", 1, arm="fist", hat="mortar")
    fx, fy = hall.PODIUM_SPOT
    return fx - a["feet"][0] + a["hand"][0], fy - a["feet"][1] + a["hand"][1] + 3


def marker_fall(c, hand):
    """The marker after Bibi lets go: it drops onto the rostrum, bounces once and lies there."""
    hx, hy = hand
    rest = 127
    dt = c.t - T9_YOU
    fall = math.sqrt(2 * (rest - hy) / 700.0)
    if dt < fall:
        x, y, ang = hx + 6 * dt / fall, hy + 350 * dt * dt, -dt / fall * 450
    else:
        b = dt - fall
        hop = max(0.0, 4 * math.sin(math.pi * b / 0.16)) if b < 0.16 else 0.0
        x, y, ang = hx + 6 + min(b, 0.16) * 20, rest - hop, -90
    spr = art.marker("mk_red", True)
    paste_rot(c.world, spr, x, y, ang)
    if 0 <= dt - fall < 0.12:
        d = ImageDraw.Draw(c.world)
        for s in (-1, 1):
            d.line([(x + s * 5, y + 1), (x + s * 9, y - 2)], fill=C["white"])


def escalator_cam(c, img, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cam = A4.lobby(w, h).copy()
    esc = art.escalator(56, 22)
    ex, ey = w - esc.width - 1, h - esc.height + 2
    cam.paste(esc, (ex, ey), esc)
    fl, top, xa, xb = esc.height - 4, esc.height - 26, 12, 56 - 12
    # Trump walks on at the foot and rides up, until it stops dead
    stop = T9_OH
    ride = clamp(c.t, T9_ESC, stop) - T9_ESC
    walk = clamp(c.t, T9_TAKE, T9_ESC) - T9_TAKE
    fx = ex - 10 + walk * 36 + ride * 14              # far enough up that the sign won't hide him
    if fx < ex + xa:
        fy = ey + fl
    else:
        fy = ey + fl - (min(fx, ex + xb) - ex - xa) / (xb - xa) * (fl - top)
    lurch = 0 <= c.t - stop < 0.35
    spr = A4.mini_trump(int(c.t * 8) % 2 if c.t < T9_ESC else 0, lurch)
    paste(cam, spr, int(fx) + (2 if lurch else 0), int(fy) + 1, "mb")
    if c.t >= T9_QUIT - 0.12:
        sign = A4.out_of_order()
        dy = pop_dy(c.t - T9_QUIT + 0.12, 0.18, 30) or 0
        paste(cam, sign, 21, h + dy, "mb")
    d = ImageDraw.Draw(cam)
    if int(c.t * 2) % 2 == 0:
        d.ellipse((3, 3, 6, 6), fill=C["red"])
    A4.stext(cam, 9, 2, "LIVE", "white")
    img.paste(cam, (x0, y0))


def steam(c):
    """Trump fuming: little clouds of steam out of both sides of his head, rising and swelling."""
    hx, hy = anchor(c, "trump", "head")
    d = ImageDraw.Draw(c.world)
    k = 0
    while T9_HIT + 0.08 * k <= c.t:
        age = c.t - T9_HIT - 0.08 * k
        if age < 0.5:
            s = 1 if k % 2 else -1
            p = ease_out(age / 0.5)
            r = 1 + 3 * p
            x = hx + s * (11 + 7 * p) + (rnd("steam", k) - 0.5) * 3
            y = hy - 10 - 20 * p
            d.ellipse((x - r - 1, y - r - 1, x + r + 1, y + r + 1), fill=(170, 174, 192))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(246, 246, 250))
        k += 1


@gag("v4", 9, post=END9)
def escalator(c, L):
    pg = pages(c, (T8_DIAGRAM, page_final))
    professor(c)
    hold = c.t < T9_YOU
    if c.t < T9_YOU:
        pose(c, "bibi", arm="fist")
    elif c.t < T9_TAKE:
        pose(c, "bibi", arm="wave")
        face(c, "bibi", brows="up")
    elif c.t < T9_OH:
        pose(c, "bibi", arm="point")
    elif c.t < T9_IT:
        pose(c, "bibi", arm="up")
    else:
        pose(c, "bibi", arm="shrug", far="out")
        if c.t >= T9_HIT:
            c.st["bibi"]["mouth"] = "smirk"
    if T9_ME + 0.08 <= c.t < T9_TAKE - 0.15:               # the mic drop: the one close shot
        c.shot = "rapper"
    if c.t >= T9_TAKE - 0.08:
        c.screens["R"] = escalator_cam
    if c.t >= T9_HIT:                                         # knocked out: steaming, the hall on its feet
        c.hit_react["trump"] = False
        pose(c, "trump", arm="cross", flush=2, brows="angry", mouth="grit", eyes="squint")
        c.st["trump"]["dx"] = 1 if int(c.t * 24) % 2 else -1
        c.st["trump"]["tint"] = ((236, 40, 40), 0.25 * ramp(c.t, T9_HIT, T9_HIT + 0.3))
        for _, _, i in hall.DELEGATES:
            a = T9_HIT + 0.05 + 0.03 * (i * 5 % 14)
            c.crowd["stand"][i] = ease_out(ramp(c.t, a, a + 0.25))
            c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0),
                                      ramp(c.t, a, a + 0.2) * (0.7 + 0.3 * math.sin(c.t * 14 + i)))
    yield "chart"
    if pg:
        pg(c.page, c.t)
    yield "mid"
    hand = anchor(c, "bibi", "hand")
    if hold:
        spr = art.marker("mk_red", c.t >= T9_ME)
        paste(c.world, spr, hand[0], hand[1] + 3, "mm")
        if 0 <= c.t - T9_ME < 0.1:
            sparkle(c.world, hand[0] + 1, hand[1] - 5, 2, C["white"])
    else:
        marker_fall(c, release_pt())
    yield "front"
    if c.t >= T9_HIT:
        steam(c)

