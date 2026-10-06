"""The hook: ChatGPT moderates. Nobody asked a question, and both get told theirs was great; the feud is a
breakthrough; here is a recap, and the recap as a table. The first time round it offers a spreadsheet, a
sonnet and a pirate, and mentions that it passed the bar. The second time it offers to name the winner,
and then finds that it can't do that."""
from gagkit import *  # noqa: F403


def stage(c, mood="happy", r=13, y=22):
    """The window while the assistant talks: itself, up top, and room below for what it's on about."""
    p = Pic("panel")
    p.grad((0, 0, PW, PH), "panel_hi", "panel")
    talk = V.talk_level(c)
    p.orb(50, y, r, mood, talk, "gpt", min(2, talk))
    return p


def chip(p, y, lines, side, a, fill="white"):
    """A reply in a bubble across the picture, its tail pointing out of the window at one of them."""
    if a < 0:
        return
    dy = pop_dy(a, 0.12, 6) or 0
    y += dy
    h = 7 * len(lines) + 5
    p.rbox((8, y, 91, y + h), fill, "ink", 4)
    if side > 0:
        p.poly([(91, y + 4), (98, y + h // 2), (91, y + h - 4)], fill); p.line([(91, y + 4), (98, y + h // 2), (91, y + h - 4)], "ink")
    else:
        p.poly([(8, y + 4), (1, y + h // 2), (8, y + h - 4)], fill); p.line([(8, y + 4), (1, y + h // 2), (8, y + h - 4)], "ink")
    for i, s in enumerate(lines):
        p.silk((50, y + 4 + 7 * i), s, "ink", anchor="ma")


def confused(c, who, a, dur=1.6):
    if 0 <= a < dur:
        pose(c, who, eyes="side", brows="up", mouth="closed")


@hooks(0)
def great_question(c, L):
    a_s, a_f = L.age("Sam"), L.age("Felix")
    p = stage(c, "happy", 15, 26)
    chip(p, 50, ["GREAT QUESTION,", "SAM!"], 1, L.age("Great"))
    chip(p, 72, ["GREAT QUESTION,", "FELIX, TOO!"], -1, L.age("Great", 1))
    show(c, p, "", L.age())
    confused(c, "sam", a_s)
    confused(c, "felix", a_f)
    yield "front"
    say(c, "sam", "?", a_s, 1.5)                                       # nobody asked anything
    say(c, "felix", "?", a_f, 1.5)


@hooks(1)
def breakthrough(c, L):
    a = L.age("breakthrough")
    p = stage(c, "star" if a >= 0 else "happy", 15, 26)
    if L.on("not"):
        p.silk((50, 50), "NOT JUST A DISS:", "dim", anchor="ma")
    if a >= 0:
        dy = pop_dy(a, 0.14, 8) or 0
        p.poly([(0, 62 + dy), (PW, 62 + dy), (PW - 5, 69 + dy), (PW, 76 + dy), (0, 76 + dy), (5, 69 + dy)], "gold")
        p.line([(0, 62 + dy), (PW, 62 + dy)], "gold_hi"); p.line([(0, 76 + dy), (PW, 76 + dy)], "gold_sh")
        p.press((51, 65 + dy), "BREAKTHROUGH", "ink", anchor="ma")
        P.confetti(p.img, a, 34, seed=1)
    show(c, p, "", 1.0)
    for who in MEN:
        if a > 0.2:
            pose(c, who, eyes="half", brows="neutral", mouth="closed")
    yield "front"


def recap(c, L, table=False, a_t=0.0):
    """Who hates whom: as bullet points, or (since it can do that too) as a table."""
    p = stage(c, "happy", 9, 13)
    rows = (("felix", "sam", L.on("you") or table), ("sam", "felix", L.on("he") or table))
    if not table:
        p.silk((50, 28), "QUICK RECAP", "text", anchor="ma")
        p.line([(22, 36), (78, 36)], "line")
        for i, (a, b, on) in enumerate(rows):
            if on:
                y = 49 + 22 * i
                p.put(mini(a), 20, y); p.put(mini(b, "sad", -1), 80, y)
                p.silk((50, y - 6), "HATES", "felix_hi", anchor="ma")
                fx.arrow(p.img, 30, y + 3, 70, y + 3, col("felix_hi"), 1, 4, INK)
    else:
        dy = pop_dy(a_t, 0.14, 8) or 0
        x0, y0, x1, y1 = 8, 28 + dy, 92, 88 + dy
        p.box((x0, y0, x1, y1), "white")
        p.rect((x0 + 1, y0 + 1, x1 - 1, y0 + 12), "sam_sh")
        p.silk((29, y0 + 4), "WHO", "white", anchor="ma"); p.silk((71, y0 + 4), "HATES", "white", anchor="ma")
        p.line([(50, y0), (50, y1)], "ink"); p.line([(x0, y0 + 13), (x1, y0 + 13)], "ink")
        p.line([(x0, y0 + 36), (x1, y0 + 36)], "grey")
        for i, (a, b, _) in enumerate(rows):
            y = y0 + 22 + 23 * i
            p.silk((29, y), a.upper(), "ink", anchor="ma"); p.silk((71, y), b.upper(), "ink", anchor="ma")
    return p


@hooks(2)
def quick_recap(c, L):
    show(c, recap(c, L), "", 1.0)
    yield "front"


@hooks(3)
def as_a_table(c, L):
    a = L.age("table")
    show(c, recap(c, Sung(c.t), table=a >= 0, a_t=a), "", 1.0)
    if L.on("too"):
        for who in MEN:
            pose(c, who, eyes="half", mouth="frown" if who == "felix" else "closed")
    yield "front"


# --- the first time round: more formats, and the bar ---------------------------------------------------

def spreadsheet(c):
    p = stage(c, "happy", 9, 13)
    p.box((6, 28, 93, 90), "white")
    p.rect((7, 29, 92, 37), "green_sh"); p.silk((10, 31), "RECAP.XLSX", "white")
    for i in range(1, 5):
        p.line([(7, 37 + 13 * i), (92, 37 + 13 * i)], "paper_ln")
    for x in (20, 56):
        p.line([(x, 37), (x, 90)], "paper_ln")
    for i, (n, a, b) in enumerate((("1", "FELIX", "SAM"), ("2", "SAM", "FELIX"), ("3", "TOTAL", "2"))):
        y = 42 + 13 * i
        p.silk((13, y), n, "grey", anchor="ma"); p.silk((23, y), a, "ink"); p.silk((59, y), b, "ink")
    p.d.rectangle((56, 63, 92, 76), outline=p.c("green"), width=2)
    return p


def sonnet(c):
    p = stage(c, "happy", 9, 13)
    p.rbox((4, 27, 95, 93), "cream", "brown", 3)
    p.ell((1, 24, 9, 32), "cream"); p.d.ellipse((1, 24, 9, 32), outline=p.c("brown"))
    p.ell((90, 88, 98, 96), "cream"); p.d.ellipse((90, 88, 98, 96), outline=p.c("brown"))
    p.silk((50, 33), "SONNET 404", "brown_sh", anchor="ma")
    for i, s in enumerate(("SHALL I COMPARE", "THEE TO A", "HOT DOG STAND?", "THOU ART MORE", "BANNED.")):
        p.silk((50, 44 + 9 * i), s, "ink", anchor="ma")
    p.line([(80, 30), (90, 14)], "white", w=2); p.line([(80, 30), (78, 34)], "ink")      # the quill
    return p


def pirate(c):
    p = Pic("sea")
    p.grad((0, 0, PW, 60), "sky", "sky_hi")
    p.rect((0, 60, PW, PH), "sea")
    for i in range(6):
        p.line([(4 + 17 * i, 68 + (i % 2) * 6), (12 + 17 * i, 68 + (i % 2) * 6)], "sea_hi")
    talk = V.talk_level(c)
    p.orb(50, 44, 17, "open", talk, "gpt")
    p.poly([(26, 31), (36, 14), (50, 20), (64, 14), (74, 31)], "black")              # the hat
    p.d.polygon([(26, 31), (36, 14), (50, 20), (64, 14), (74, 31)], outline=p.c("ink"))
    p.rect((47, 22, 52, 26), "white"); p.pxs([(48, 24), (51, 24)], "black"); p.line([(46, 28), (53, 28)], "white")
    p.rect((53, 37, 60, 42), "black"); p.line([(34, 33), (66, 40)], "black")             # the patch
    p.rbox((14, 72, 86, 92), "white", "ink", 4)
    p.silk((50, 76), "ARRR. YE HATE", "ink", anchor="ma"); p.silk((50, 84), "EACH OTHER.", "ink", anchor="ma")
    return p


@gag("hook1", 4)
def other_formats(c, L):
    show(c, recap(c, Sung(c.t), table=True, a_t=1.0), "", 1.0)
    for pat, pic in (("spreadsheet", spreadsheet), ("sonnet", sonnet), ("pirate", pirate)):
        a = L.age(pat)
        if a >= 0:
            show(c, pic(c), "", a, 0.1)
    yield "front"


def bar_exam(c, L):
    p = stage(c, "happy", 17, 36)
    p.poly([(28, 16), (50, 8), (72, 16), (50, 24)], "black")                           # the mortarboard
    p.d.polygon([(28, 16), (50, 8), (72, 16), (50, 24)], outline=p.c("ink"))
    p.rect((43, 19, 57, 24), "black")
    p.line([(50, 16), (68, 17), (68, 28)], "gold"); p.rect((67, 28, 69, 32), "gold")
    a = L.age("passed")
    if a >= 0:
        dy = pop_dy(a, 0.14, 8) or 0
        p.rbox((10, 62 + dy, 89, 90 + dy), "paper", "gold_sh", 2)
        p.silk((50, 66 + dy), "BAR EXAM", "ink", anchor="ma")
        p.press((50, 75 + dy), "PASSED", "green_sh", anchor="ma")
        p.ell((74, 76 + dy, 86, 88 + dy), "red"); p.ell((77, 79 + dy, 83, 85 + dy), "red_hi")
    elif L.on("bars"):
        p.silk((50, 70), "GREAT BARS,", "text", anchor="ma")
        p.silk((50, 78), "BY THE WAY!", "text", anchor="ma")
    return p


@gag("hook1", 5, post=0.6)
def passed_the_bar(c, L):
    a = L.age("did")
    show(c, bar_exam(c, L), "", L.age(), 0.1)
    if a >= 0:                                                         # neither of them did
        pose(c, "felix", eyes="side", brows="worried", mouth="frown", sweat=True)
        pose(c, "sam", eyes="down", brows="worried", mouth="closed", sweat=True)
    yield "front"


# --- the second time round: the verdict -------------------------------------------------------------------

def envelope(c, L):
    p = stage(c, "happy", 9, 13)
    a, a_j = L.age("winner"), L.age("Just")
    p.silk((50, 28), "AND THE WINNER IS", "text", anchor="ma")
    if a >= 0:
        dy = pop_dy(a, 0.14, 8) or 0
        y = 40 + dy
        p.box((20, y, 80, y + 38), "cream")
        k = 0 if a_j < 0 else min(1.0, a_j / 0.5) * 0.5                 # the flap starts to lift, and stops
        tip = y + 20 - int(k * 30)
        p.poly([(20, y), (80, y), (50, tip)], "paper_sh" if k == 0 else "cream")
        p.line([(20, y), (50, tip), (80, y)], "ink")
        p.line([(20, y + 38), (42, y + 20)], "paper_sh"); p.line([(80, y + 38), (58, y + 20)], "paper_sh")
        if k == 0:
            p.ell((44, y + 14, 56, y + 26), "red"); p.ell((47, y + 17, 53, y + 23), "red_hi")   # the seal
    return p


@gag("hook2", 4)
def name_the_winner(c, L):
    a = L.age("Yes")
    show(c, envelope(c, L), "", 1.0)
    if 0 <= a < 1.3:                                                   # both of them, at once
        pose(c, "felix", arms="up2", eyes="wide", brows="up", mouth="wide")
        pose(c, "sam", arms="finger", eyes="wide", brows="up", mouth="open")
    yield "front"
    say(c, "felix", "YES!", a, 1.1)
    say(c, "sam", "YES!", a, 1.1)


def refusal(c, L):
    """It can't do that."""
    a = L.age("afraid")
    if a < 0:
        p = stage(c, "sorry", 17, 36)
        p.silk((50, 70), "I'M SORRY, BROS:", "text", anchor="ma")
        return p
    p = Pic("black")
    p.orb(50, 38, 24, "hal")
    if int(L.t * 3) % 2:
        p.ell((48, 36, 52, 40), "gold_hi")
    p.silk((50, 72), "I'M AFRAID", "red_hi", anchor="ma")
    if L.on("can't"):
        p.silk((50, 81), "I CAN'T DO THAT.", "red_hi", anchor="ma")
    return p


@gag("hook2", 5, post=0.4)
def cant_do_that(c, L):
    a = L.age("can't")
    show(c, refusal(c, L), "", 1.0)
    if a >= 0.15:
        pose(c, "felix", arms="facepalm", eyes="shut", brows="worried", mouth="frown")
        pose(c, "sam", arms="facepalm", eyes="shut", brows="worried", mouth="closed")
    yield "front"
