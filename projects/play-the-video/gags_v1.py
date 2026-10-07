"""Verse 1: Hasan, on his stream. Asmongold's video sits paused in the window, and Hasan keeps pulling
exhibits up over it."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403


# --- 0-1: that gold has grown mold ---------------------------------------------------------------------

@lru_cache(maxsize=None)
def gold_pic(fuzz, mold=False):
    """His name in gold letters; the gold grows mould (fuzz 0-3) and, in the end, says so."""
    p = Pic("night")
    p.silk((PW // 2, 5), "ASMON", "dim", anchor="ma")
    if mold:
        p.big((PW // 2, 16), "MOLD", "mold", "mold_sh")
    else:
        p.big((PW // 2, 16), "GOLD")
    p.mold((16, 14, 16 + 23 * fuzz, 36), 22 * fuzz, 1)
    if mold:
        p.stink(30, 13, 0, 3, 8, 18)
    return p.img


@gag("v1", 0)
def gold_mold(c, L):
    if L.on("^gold"):
        grown = L.age("grown")
        fuzz = 0 if grown < 0 else min(3, 1 + int(grown / 0.11))
        show(c, gold_pic(fuzz, L.on("mold")), "ASMONMOLD" if L.on("mold") else "ASMONGOLD", "LOGO")
    if L.on("mold"):
        pose(c, "hasan", arms="window", eyes="up", brows="up")
    yield "front"
    if L.on("mold"):
        rooms.flies(c.world, *win(c, 50, 22), c.t, 4, 1)


def _bread(p, x):
    p.rbox((x + 3, 14, x + 25, 38), "cream", "brown", 3)
    p.rect((x + 3, 30, x + 25, 38), "cream"); p.line([(x + 3, 30), (x + 3, 38), (x + 25, 38), (x + 25, 30)], "brown")
    p.mold((x + 6, 17, x + 22, 35), 26, 2)


def _bed(p, x):
    p.rect((x + 1, 22, x + 3, 38), "wood_sh")                             # the headboard
    p.rect((x + 3, 30, x + 27, 35), "white"); p.rect((x + 3, 35, x + 27, 37), "wood_sh")
    p.rbox((x + 4, 25, x + 11, 30), "paper", "ink", 2)                    # the pillow
    p.rect((x + 11, 27, x + 27, 34), "bag_hi")                            # the blanket
    p.rect((x + 4, 37, x + 5, 40), "wood_sh"); p.rect((x + 25, 37, x + 26, 40), "wood_sh")
    p.mold((x + 5, 26, x + 26, 34), 24, 3)
    p.stink(x + 10, 21, 0, 3, 7, 5)


def _take(p, x):
    p.rbox((x + 1, 14, x + 27, 31), "white", "ink", 4)
    p.poly([(x + 7, 31), (x + 5, 37), (x + 12, 31)], "white"); p.line([(x + 7, 31), (x + 5, 37), (x + 12, 31)], "ink")
    p.silk((x + 14, 17), "HOT", "live", anchor="ma"); p.silk((x + 14, 24), "TAKE", "ink", anchor="ma")
    p.mold((x + 3, 15, x + 26, 30), 22, 4)
    p.rect((x + 16, 33, x + 28, 40), "yellow"); p.d.rectangle((x + 16, 33, x + 28, 40), outline=INK)   # the price
    p.silk((x + 22, 35), "$", "ink", anchor="ma")


@lru_cache(maxsize=None)
def mold_report(n):
    p = Pic("panel")
    p.header("MOLD FOUND ON", "mold_sh", "white", h=9)
    for i, (draw, name) in enumerate(((_bread, "BREAD"), (_bed, "BED"), (_take, "TAKES"))[:n]):
        x = 4 + 32 * i
        draw(p, x)
        p.silk((x + 14, 45), name, "text", anchor="ma")
    return p.img


@gag("v1", 1)
def mold_on(c, L):
    show(c, mold_report(count(L, "bread", "bedding", "takes")), "ASMONMOLD", "LOGO")
    if L.on("sold"):
        pose(c, "hasan", arms="shrug", brows="up", eyes="open")
    yield "front"


# --- 2-3: body-shame you? ------------------------------------------------------------------------------

@gag("v1", 2)
def body_shame(c, L):
    """The clip plays: Asmongold, asking for it. Hasan stops it there."""
    if not L.on("^I'll"):
        c.window.update(paused=False, progress=0.31 + 0.01 * L.age())
        c.cam_t["asmon"] = c.t
        pose(c, "asmon", arms="palm", eyes="open", brows="up", mouth="open" if int(c.t * 8) % 2 else "closed",
             react=False)
    else:
        c.window.update(progress=0.31 + 0.01 * (L.w("^I'll") - L.t0))
        c.cam_t["asmon"] = L.w("^I'll")
        pose(c, "asmon", arms="palm", eyes="half", brows="up", mouth="open", react=False)
        pose(c, "hasan", arms="clasp", brows="up", eyes="open")          # he cracks his knuckles
    c.window.update(badge="CLIP")
    yield "front"
    if L.on("body") and c.t < when("v1", 3, "hairline"):
        label(c, *win(c, 56, 46), "BODY-SHAME ME", L.age("body"), bg="ink", fg="text")


def _tooth_walks(p, x, y, step):
    """A tooth on legs, its feet at y."""
    p.rect((x, y - 9, x + 5, y - 5), "tooth_y"); p.rect((x, y - 5, x + 1, y - 3), "tooth_y"); p.rect((x + 4, y - 5, x + 5, y - 3), "tooth_y")
    p.d.line([(x - 1, y - 9), (x - 1, y - 3)], fill=INK); p.d.line([(x + 6, y - 9), (x + 6, y - 3)], fill=INK)
    p.d.line([(x, y - 10), (x + 5, y - 10)], fill=INK); p.px((x + 1, y - 8), "white")
    a = 1 if step % 2 else -1
    p.line([(x + 1, y - 2), (x + 1 + a, y)], "ink"); p.line([(x + 4, y - 2), (x + 4 - a, y)], "ink")


def hairline_pic(k, step):
    """His hairline leaves home (k 0 -> 1 across the room), and half his teeth go with it."""
    p = Pic("awall")
    p.rect((0, 43, PW, PH), "adesk"); p.line([(0, 43), (PW, 43)], "adesk_hi")
    p.rect((76, 10, 96, 43), "wood_sh"); p.rect((78, 12, 94, 43), "night")          # the door, open
    p.tag((74, 2), "EXIT", "live", "white")
    x = int(34 + 62 * k)
    y = 30 - (step % 2)
    for i in range(3):                                                     # the teeth, in single file behind it
        tx = x - 12 - 10 * i
        if 0 <= tx < 82:
            _tooth_walks(p, tx, 43 - (step + i) % 2, step + i)
    if x < 80:                                                             # once through the door, gone
        p.poly([(x, y), (x + 1, y - 7), (x + 5, y - 12), (x + 9, y - 6), (x + 13, y - 12), (x + 17, y - 7),
                (x + 18, y), (x + 18, y + 3), (x, y + 3)], "ahair")        # the hairline: an M of hair
        p.line([(x + 1, y - 7), (x + 5, y - 12), (x + 9, y - 6), (x + 13, y - 12), (x + 17, y - 7)], "ahair_hi")
        p.d.line([(x, y + 3), (x, y), (x + 1, y - 7)], fill=INK); p.d.line([(x + 18, y + 3), (x + 18, y), (x + 17, y - 7)], fill=INK)
        for hx in (3, 7, 11, 15):                                          # strands
            p.line([(x + hx, y + 2), (x + hx, y - 3)], "ahair_sh")
        p.px((x + 12, y - 2), "ink"); p.px((x + 15, y - 2), "ink")         # eyes front
        a, b = (2, -2) if step % 2 else (-2, 2)                             # legs
        p.line([(x + 5, y + 3), (x + 5 + a, y + 12)], "ink", 2); p.line([(x + 13, y + 3), (x + 13 + b, y + 12)], "ink", 2)
        p.line([(x + 5 + a, y + 12), (x + 8 + a, y + 12)], "ink"); p.line([(x + 13 + b, y + 12), (x + 16 + b, y + 12)], "ink")
    return p.img


@gag("v1", 3, post=0.3)
def hairline_walks(c, L):
    if L.on("hairline"):
        a = L.age("hairline")
        show(c, hairline_pic(clamp(a / max(0.6, L.end + 0.5 - L.w("hairline")), 0, 1), int(a * 8)), "HAIRLINE", "LIVE")
    if L.on("teeth"):
        pose(c, "hasan", arms="window", eyes="side", brows="up")
    yield "front"


# --- 4-5: arts and crafts ------------------------------------------------------------------------------

def sanding_pic(t, sanding, dads):
    """A tooth, and the sandpaper going over it."""
    p = Pic("panel")
    tt = tooth(26, True)
    p.put(tt, 50, 34)
    if sanding:
        dx = int(round(9 * math.sin(t * 16)))
        p.rbox((30 + dx, 9, 70 + dx, 17), "brown", "ink", 1)
        for i in range(14):
            p.px((32 + dx + int(rnd("sp", i) * 36), 11 + int(rnd("sq", i) * 5)), "brown_hi")
        if dads:
            p.tag((38 + dx, 0), "DAD'S", "yellow", "ink")
        for i in range(8):                                                 # dust
            k = (t * 2.2 + rnd("du", i)) % 1.0
            p.px((36 + int(rnd("dx", i) * 28) + int(8 * k * (rnd("dv", i) - 0.5)), 18 + int(26 * k)), "tooth_y")
    return p.img


@gag("v1", 4)
def sandpaper(c, L):
    if L.on("sanded"):
        show(c, sanding_pic(c.t, True, L.on("Dad")), "DENTISTRY", "DIY")
        if not L.on("with"):
            pose(c, "hasan", arms="pinch", brows="worried", eyes="open")
    yield "front"


@lru_cache(maxsize=None)
def dental_plan(n, star=False):
    """His dental plan, itemised."""
    p = Pic("paper")
    p.header("DENTAL PLAN", "blue", "white", h=9)
    p.silk((4, 12), "NET WORTH", "ink"); p.silk((PW - 4, 12), "$$$$$$", "green_sh", anchor="ra")
    p.line([(3, 20), (PW - 4, 20)], "paper_ln")
    if n == 0:
        p.silk((4, 24), "COVERS:", "ink")
    if n >= 1:                                                             # a glue stick
        p.rbox((11, 23, 18, 42), "white", "ink", 2); p.rect((11, 23, 18, 28), "orange"); p.d.rectangle((11, 23, 18, 28), outline=INK)
        p.silk((15, 45), "GLUE", "ink", anchor="ma")
    if n >= 2:                                                             # safety scissors
        p.d.ellipse((39, 34, 46, 41), outline=col("live"), width=2); p.d.ellipse((48, 34, 55, 41), outline=col("live"), width=2)
        p.line([(43, 34), (52, 22)], "grey_sh", 2); p.line([(51, 34), (42, 22)], "grey_sh", 2)
        p.silk((47, 45), "SNIP", "ink", anchor="ma")
    if n >= 3:                                                             # and the sandpaper
        p.rbox((69, 24, 90, 41), "brown", "ink", 1)
        for i in range(22):
            p.px((71 + int(rnd("sa", i) * 18), 26 + int(rnd("sb", i) * 14)), "brown_hi")
        p.silk((80, 45), "SAND", "ink", anchor="ma")
    if star:                                                               # and what that makes it
        p.rect((0, 43, PW, PH), "live")
        p.silk((PW // 2, 45), "ARTS AND CRAFTS", "white", anchor="ma")
    return p.img


@gag("v1", 5, post=0.4)
def arts_and_crafts(c, L):
    if L.on("dental"):
        n = 0 if not L.on("arts") else min(3, 1 + int(L.age("arts") / 0.14))
        show(c, dental_plan(n, L.on("crafts") and L.age("crafts") > 0.12), "ASMONGOLD", "FILE")
    else:
        show(c, sanding_pic(c.t, True, True), "DENTISTRY", "DIY")
    if L.on("millionaire") and not L.on("dental"):
        pose(c, "hasan", arms="chest", brows="up", eyes="open")
    yield "front"


# --- 6-7: evolve ---------------------------------------------------------------------------------------

def _walker(p, x, stage):
    """One figure of the march of progress, feet at y=44: 0 the ape, 1 the stooping one, 2 Asmongold."""
    if stage == 0:
        p.ell((x, 28, x + 12, 40), "brown_sh"); p.ell((x + 7, 24, x + 14, 31), "brown_sh")
        p.line([(x + 3, 38), (x + 2, 44)], "brown_sh", 2); p.line([(x + 9, 38), (x + 10, 44)], "brown_sh", 2)
        p.line([(x + 11, 31), (x + 13, 43)], "brown_sh", 2)
        p.px((x + 12, 27), "white")
    elif stage == 1:
        p.ell((x + 2, 22, x + 11, 36), "brown"); p.ell((x + 6, 15, x + 13, 23), "askin_sh")
        p.line([(x + 4, 35), (x + 3, 44)], "brown", 2); p.line([(x + 9, 35), (x + 10, 44)], "brown", 2)
        p.line([(x + 10, 25), (x + 14, 34)], "askin_sh", 2)
        p.px((x + 11, 18), "ink"); p.line([(x + 6, 15), (x + 12, 15)], "brown_sh")
    else:
        p.rect((x + 3, 19, x + 11, 34), "tee")                             # the black T-shirt
        p.line([(x + 4, 34), (x + 4, 44)], "night", 2); p.line([(x + 9, 34), (x + 9, 44)], "night", 2)
        p.ell((x + 3, 8, x + 11, 18), "askin")
        p.rect((x + 2, 9, x + 4, 24), "ahair"); p.rect((x + 10, 9, x + 12, 24), "ahair")       # the hair, long
        p.line([(x + 4, 8), (x + 10, 8)], "ahair"); p.rect((x + 5, 15, x + 10, 19), "abeard")
        p.px((x + 9, 12), "ink"); p.line([(x + 11, 22), (x + 14, 29)], "askin", 2)


def evolution(stage, t=0.0):
    """The march of progress, and where a season without a bath takes it. stage 0: the ape to the man, and
    a question mark; 1: the answer; 2: crowned."""
    p = Pic("paper")
    p.header("EVOLUTION", "brown", "white", h=9)
    for i in range(3):
        _walker(p, 3 + 21 * i, i)
        p.line([(18 + 21 * i, 30), (22 + 21 * i, 30)], "ink"); p.pxs([(21 + 21 * i, 29), (21 + 21 * i, 31)], "ink")
    p.line([(0, 45), (PW, 45)], "paper_sh")
    if stage == 0:
        p.d.rectangle((70, 14, 92, 42), outline=col("grey"))
        p.silk((82, 20), "?", "grey_sh", anchor="ma", fnt=SILK16)
    else:
        r = roach_big(int(t * 6) % 2).rotate(90, expand=True)                # upright, like the rest of them
        p.put(r, 82, 29)
        if stage == 2:
            p.put(crown_small(), 82, 8)
    return p.img


@gag("v1", 6)
def evolve(c, L):
    if L.on("evolve"):
        show(c, evolution(0), "SCIENCE", "DAY 105")
    elif L.on("baths"):
        c.window.update(badge="DAY 105")
    if L.on("bold"):
        pose(c, "hasan", arms="acc0" if int(c.t * 5) % 2 else "acc1", brows="up", eyes="open")    # a slow clap
    yield "front"


@gag("v1", 7, post=0.5)
def roach_king(c, L):
    stage = 2 if L.on("Roach") else 1 if L.on("shell") else 0
    show(c, evolution(stage, c.t), "ROACH KING" if stage == 2 else "SCIENCE", "" if stage == 2 else "DAY 105")
    if L.on("Roach"):
        pose(c, "hasan", arms="window", eyes="up", brows="up")
    yield "front"
    if L.on("Roach"):
        alert(c, L.age("Roach") - 0.1, "ALL HAIL", "THE ROACH KING", "roach", 2.2)


# --- 8-9: the rat, the fridge --------------------------------------------------------------------------

def rat_alarm(stage, t):
    """Morning at his place: asleep on the left, the rat on the nightstand. stage 1: the smell arrives;
    2: the nightstand is a chapel of rest."""
    p = Pic("awall_sh")
    p.rect((0, 42, PW, PH), "adesk")
    p.rect((2, 28, 44, 41), "bag_hi"); p.d.rectangle((2, 28, 44, 41), outline=INK)            # the bed
    p.rbox((3, 22, 24, 31), "paper_sh", "ink", 3)                                             # the pillow
    p.ell((8, 14, 22, 28), "askin"); p.d.arc((8, 14, 22, 28), 0, 360, fill=INK)               # his head
    p.poly([(8, 20), (9, 13), (15, 11), (21, 13), (19, 16), (12, 16)], "ahair")               # hair, what's left
    p.rect((4, 18, 9, 30), "ahair"); p.rect((14, 23, 22, 28), "abeard")
    if stage >= 1:
        p.rect((17, 18, 20, 21), "white"); p.px((19, 20), "ink")                              # one eye, wide open
        p.silk((26, 10), "!", "live", fnt=SILK16)
    else:
        p.line([(16, 20), (20, 20)], "ink")
        p.silk((26, 12 - int(t * 2) % 2), "Z", "dim")
    p.rect((58, 30, 92, 42), "wood_sh"); p.d.rectangle((58, 30, 92, 42), outline=INK)         # the nightstand
    p.line([(60, 36), (90, 36)], "wood")
    rooms.rat(p.d, 66, 30)
    p.rect((62, 4, 92, 14), "black"); p.d.rectangle((62, 4, 92, 14), outline=INK)             # the clock
    p.silk((77, 6), "7:00" if int(t * 3) % 2 or stage == 0 else "7 00", "live", anchor="ma")
    n = 3 if stage == 0 else 6
    for i in range(n):                                                                        # the smell, heading west
        k = (t * 0.9 + i / n) % 1.0
        x = 62 - int(36 * k)
        y = 22 + int(round(2 * math.sin(k * 9 + i)))
        if stage or k < 0.4:
            p.line([(x, y), (x + 3, y - 1), (x + 5, y + 1)], "mold")
    if stage == 2:
        for cx in (61, 88):                                                                   # candles
            p.rect((cx, 23, cx + 1, 29), "cream"); p.px((cx, 21 + int(t * 9 + cx) % 2), "gold")
        p.tag((68, 44), "R.I.P.", "ink", "white")
    return p.img


@gag("v1", 8)
def smell_the_rat(c, L):
    stage = 2 if L.on("bedside") else 1 if L.on("smell") else 0
    show(c, rat_alarm(stage, c.t), "MORTUARY" if stage == 2 else "ALARM", "7 AM")
    if L.on("mortuary"):
        pose(c, "hasan", arms="beg", eyes="shut", brows="worried", mouth="closed")              # a moment's silence
    yield "front"


def fridge_pic(stage, t):
    """What's in his fridge. stage 1: it is loot; 2: and what grade."""
    p = Pic("grey_sh")
    p.rect((2, 2, 60, 51), "white"); p.d.rectangle((2, 2, 60, 51), outline=INK)               # the fridge, open
    p.rect((4, 4, 58, 49), "grey_hi")
    for y in (17, 36):
        p.line([(4, y), (58, y)], "grey"); p.line([(4, y + 1), (58, y + 1)], "white")
    p.rect((62, 2, 69, 51), "white"); p.d.rectangle((62, 2, 69, 51), outline=INK)             # its door
    for cx in (8, 16):                                                                        # two cans
        p.rect((cx, 7, cx + 5, 16), "can"); p.rect((cx, 7, cx + 5, 9), "can_hi")
    p.rbox((36, 10, 54, 16), "steel_hi", "ink", 2)                                            # something in foil
    p.rect((30, 41, 52, 48), "box"); p.d.rectangle((30, 41, 52, 48), outline=INK)             # a pizza box, since
    x, y = 19, 28
    if stage:                                                                                 # the glow of good loot
        for i in range(8):
            a = i * math.pi / 4 + t * 2
            p.line([(x + int(9 * math.cos(a)), y + int(7 * math.sin(a))), (x + int(14 * math.cos(a)), y + int(10 * math.sin(a)))],
                   "gold" if stage == 2 else "orange")
    p.ell((x - 6, y - 4, x + 5, y + 5), "roach_sh"); p.d.ellipse((x - 6, y - 4, x + 5, y + 5), outline=INK)   # the head
    p.rect((x - 8, y - 2, x - 6, y + 3), "roach"); p.pxs([(x - 9, y - 1), (x - 9, y + 2)], "roach")           # where it came off
    p.rect((x + 1, y - 2, x + 2, y - 1), "white"); p.rect((x + 1, y + 2, x + 2, y + 3), "white")              # two dead eyes
    p.line([(x + 4, y - 3), (x + 9, y - 8), (x + 13, y - 8)], "ink"); p.line([(x + 4, y + 3), (x + 10, y + 6), (x + 14, y + 5)], "ink")
    if stage:                                                                                 # the tooltip
        p.rect((33, 21, 98, 42), "bg"); p.d.rectangle((33, 21, 98, 42), outline=col("gold" if stage == 2 else "orange"))
        p.silk((36, 24), "ROACH HEAD", "orange")
        if stage == 2:
            p.silk((36, 33), "LEGENDARY", "gold_hi")
        else:
            p.silk((36, 33), "ITEM LVL 1", "dim")
    return p.img


@gag("v1", 9, post=0.3)
def legendary_loot(c, L):
    stage = 2 if L.on("legendary") else 1 if L.on("loot") else 0
    show(c, fridge_pic(stage, c.t), "LOOT" if stage else "FRIDGE", "CAM 2")
    if L.on("legendary"):
        pose(c, "hasan", arms="window", eyes="up", brows="up")
    yield "front"
    if L.on("legendary"):
        fx.sparkle(c.world, *win(c, 19 + int(8 * math.sin(c.t * 9)), 16), 2, col("gold_hi"))


# --- 10-11: react, reactionary ---------------------------------------------------------------------------

def react_pic(t, paid, still):
    """How the money is made: a man, a chair, somebody else's video."""
    p = Pic("awall_sh")
    p.rect((0, 44, PW, PH), "adesk")
    p.rect((56, 30, 96, 33), "adesk_hi"); p.rect((60, 33, 62, 44), "adesk_sh"); p.rect((90, 33, 92, 44), "adesk_sh")   # the desk
    p.rect((62, 8, 92, 28), "black"); p.d.rectangle((62, 8, 92, 28), outline=INK)             # the monitor
    p.rect((64, 10, 90, 26), "hwall"); p.poly([(74, 13), (74, 23), (82, 18)], "live")         # somebody else's video
    p.rect((76, 28, 78, 30), "grey_sh")
    p.rect((14, 20, 18, 44), "night"); p.rect((14, 36, 40, 39), "night"); p.rect((26, 39, 28, 46), "night")   # the chair
    p.line([(18, 46), (36, 46)], "night", 2)
    p.poly([(19, 22), (26, 22), (40, 34), (38, 37), (20, 36)], "tee")                         # him, a long way down it
    p.line([(38, 36), (50, 36), (50, 44)], "night", 3)                                        # legs
    p.ell((17, 11, 28, 22), "askin"); p.rect((16, 12, 19, 28), "ahair"); p.rect((22, 18, 28, 22), "abeard")
    p.line([(23, 15), (26, 15)], "ink")                                                       # eyes shut
    p.d.arc((15, 8, 29, 22), 180, 360, fill=col("phones_hi"))
    if paid:                                                                                  # and it pays
        for i in range(5):
            k = (t * 1.6 + i * 0.2) % 1.0
            p.ell((66 + 5 * i - 2, 28 - int(26 * (1 - k)) - 2, 66 + 5 * i + 2, 28 - int(26 * (1 - k)) + 2), "gold")
        coin_stack(p, 80, 30, 2 + int(t * 3) % 4)
    if still:                                                                                 # he hasn't moved in a while
        p.line([(18, 12), (14, 20)], "grey_hi"); p.line([(20, 11), (14, 20)], "grey_hi"); p.line([(16, 15), (19, 13)], "grey_hi")
        p.silk((33, 8), "Z", "dim"); p.silk((38, 4), "Z", "dim")
    return p.img


@lru_cache(maxsize=None)
def red_flag():
    f = Canvas(22, 30)
    f.rect((2, 1, 3, 29), "wood_hi")
    f.poly([(4, 2), (20, 4), (14, 8), (20, 12), (4, 13)], "live")
    f.pxs([(9, 6), (10, 6), (9, 7), (10, 7), (8, 8), (11, 8)], "gold")
    return f.done()


@gag("v1", 10)
def react_for_pay(c, L):
    if L.on("react"):
        show(c, react_pic(c.t, L.on("paid"), L.on("stationary")), "REACTS", "LIVE")
    yield "front"


@gag("v1", 11, post=0.7)
def reactionary(c, L):
    if L.age() >= 0 and not L.on("^you"):
        hold_up(c, "hasan", red_flag(), 6)
        pose(c, "hasan", brows="angry", eyes="open")
    elif L.on("^you"):
        pose(c, "hasan", arms="window", eyes="up", brows="up" if not L.on("Reactionary") else "angry")
    if L.on("Reactionary"):
        c.window.update(title="REACT ANDY")
        c.chat += [("MARXBRO:", "hasan_hi", "REACT ANDY"), ("LATTE:", "hasan_hi", ":skull: :skull:")]
    yield "front"
    if L.on("Reactionary") and c.t < when("v1", 12) - 0.1:
        label(c, *win(c, 54, 44), "REACTIONARY", L.age("Reactionary"), bg="live", fg="white")


# --- 12-13: mayors, roaches ------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def election_pic(n):
    p = Pic("panel")
    p.header("ELECTION NIGHT", "live", "white", h=9)
    for i in range(3):
        y = 13 + 13 * i
        p.rect((4, y, 95, y + 10), "panel_hi")
        p.silk((7, y + 3), "HIS PICK", "text")
        if i < n:
            p.tick(62, y + 2, "ok"); p.silk((75, y + 3), "WON", "ok")
    return p.img


@lru_cache(maxsize=None)
def mayor():
    """A mayor, hand-picked: the chain of office, the sash, the wave."""
    f = Canvas(18, 28)
    f.rect((5, 11, 12, 21), "night"); f.line([(5, 11), (12, 20)], "live", 2)          # the suit, the sash
    f.line([(6, 21), (6, 26)], "night", 2); f.line([(11, 21), (11, 26)], "night", 2)
    f.ell((5, 3, 12, 10), "hskin_sh"); f.rect((5, 2, 12, 4), "grey_sh")
    f.px((10, 6), "ink"); f.line([(9, 8), (11, 8)], "white")
    f.line([(12, 13), (16, 8)], "night", 2); f.rect((15, 6, 17, 8), "hskin_sh")       # waving
    f.line([(7, 11), (8, 13), (10, 11)], "gold")
    return f.done()


def shirt_pic(t, picking):
    """His shirt, in close-up, and what lives on it."""
    p = Pic("tee")
    p.d.arc((30, -22, 70, 10), 0, 180, fill=col("tee_hi"), width=2)                           # the collar
    p.line([(8, 0), (2, 53)], "tee_hi"); p.line([(92, 0), (98, 53)], "tee_hi")
    for i, (x, y, f) in enumerate(((22, 36, 1), (70, 44, -1), (48, 20, 1))):
        if picking and i == 2:
            continue
        r = roach_big(int(t * 8 + i) % 2)
        p.put(r if f > 0 else r.transpose(Image.FLIP_LEFT_RIGHT), x + int(3 * math.sin(t * 2 + i)), y)
    if picking:                                                                               # one comes off
        lift = min(10, int(picking * 30))
        r = roach_big(int(t * 14) % 2).rotate(-70, expand=True)
        p.put(r, 52, 22 - lift)
        p.poly([(99, 2 - lift), (62, 4 - lift), (56, 8 - lift), (62, 12 - lift), (99, 16 - lift)], "askin")   # finger
        p.poly([(99, 22 - lift), (66, 22 - lift), (57, 16 - lift), (64, 30 - lift), (99, 34 - lift)], "askin_sh")   # and thumb
        p.d.line([(99, 2 - lift), (62, 4 - lift), (56, 8 - lift), (62, 12 - lift), (99, 16 - lift)], fill=INK)
        p.d.line([(99, 22 - lift), (66, 22 - lift), (57, 16 - lift), (64, 30 - lift), (99, 34 - lift)], fill=INK)
    return p.img


@gag("v1", 12)
def red_alert(c, L):
    show(c, election_pic(count(L, "endorsements", "win", "elections")), "RESULTS", "LIVE")
    if L.on("red"):
        pose(c, "hasan", arms="chest", brows="up", eyes="open")
    yield "front"
    if L.on("red"):
        alert(c, L.age("red"), "RED ALERT", "HASAN'S PICK WINS", "bell", 2.4, accent="red")


@gag("v1", 13)
def mayors_and_roaches(c, L):
    if not L.on("^you"):
        show(c, election_pic(3), "RESULTS", "LIVE")
        if L.on("pick"):
            hold_up(c, "hasan", mayor(), 4)
            pose(c, "hasan", brows="up", eyes="open")
    else:
        show(c, shirt_pic(c.t, max(0.0, L.age("roaches"))), "ASMONGOLD", "ZOOM")
        pose(c, "hasan", arms="window" if L.on("shirt") else "pinch", eyes="up" if L.on("shirt") else "open", brows="up")
    yield "front"
