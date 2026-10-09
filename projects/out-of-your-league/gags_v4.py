"""Verse 4: the two of them at the sanctuary's gate, trading bars. The window hangs between them, Winnie
and the emu are in the field behind, and the tortoise crosses it when her bar comes."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403

EMI, MAYA = "emiru", "maya"


def both(c, **kw):
    for who in WOMEN:
        pose(c, who, **kw)


# --- 0-1: the shooters ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def trail_cam(stage, wave):
    p = Pic("black")
    p.rect((0, 0, PW, PH), "tree_sh")                                    # night vision
    for y in range(0, PH, 2):
        p.line([(0, y), (PW, y)], "tree")
    p.rect((0, 38, PW, PH), "green_sh")
    for x in (10, 34, 70, 90):
        p.rect((x, 6, x + 3, 40), "black")
    x = 54                                                               # somebody who shouldn't be here
    p.ell((x - 5, 14, x + 5, 25), "green_hi"); p.rect((x - 6, 25, x + 6, 43), "green_hi")
    p.px((x - 2, 19), "white"); p.px((x + 2, 19), "white")
    if stage:
        p.line([(x + 6, 27), (x + 12, 18 + 3 * wave), (x + 13 + 2 * wave, 11 + 2 * wave)], "green_hi", w=3)   # waving
    else:
        p.rect((x + 6, 26, x + 9, 38), "green_hi")
    for cx, cy, sx, sy in ((3, 3, 1, 1), (PW - 4, 3, -1, 1), (3, PH - 6, 1, -1), (PW - 4, PH - 6, -1, -1)):
        p.line([(cx, cy), (cx + 6 * sx, cy)], "white"); p.line([(cx, cy), (cx, cy + 6 * sy)], "white")
    p.silk((8, 6), "CAM 3", "white"); p.silk((PW - 8, 6), "03:12", "white", anchor="ra")
    return p.img


@gag("v4", 0)
def wave_at_the_trail_cam(c, L):
    show(c, trail_cam(1 if L.on("Wave") else 0, int(c.t * 5) % 2), "TRAIL CAM", "REC")
    pose(c, MAYA, arms="wave", brows="up")
    if L.on("dramatic"):
        pose(c, EMI, arms="wave", brows="up", mouth="grin")
    yield "front"


def shooter(p, x, y, flip=False):
    """Somebody in camouflage behind a long lens, 30 x 22, feet at (x, y)."""
    s = -1 if flip else 1
    p.rect((x - 5, y - 14, x + 5, y), "tree_sh"); p.ell((x - 4, y - 22, x + 4, y - 13), "tree")
    p.pxs([(x - 3, y - 10), (x + 2, y - 6), (x - 1, y - 3), (x + 3, y - 12)], "pasture_sh")
    p.rect((x + s * 4 - 2, y - 19, x + s * 4 + 3, y - 14), "black")
    lens = (x + s * 6, y - 19, x + s * 22, y - 15) if s > 0 else (x - 22, y - 19, x - 6, y - 15)
    p.rect(lens, "grey_hi"); p.d.rectangle(lens, outline=INK)
    p.rect((x + s * 21 - 1, y - 20, x + s * 21 + 1, y - 14), "black")
    p.line([(x + s * 12, y - 14), (x + s * 9, y)], "black"); p.line([(x + s * 12, y - 14), (x + s * 15, y)], "black")


@lru_cache(maxsize=None)
def nat_geo(stage, flash):
    if stage == 0:
        p = Pic("pasture")
        p.sky(22); p.ground(22)
        p.ell((2, 26, 30, 50), "tree"); p.ell((70, 28, 98, 52), "tree_sh")
        shooter(p, 22, 48); shooter(p, 78, 48, True)
        if flash:
            p.pxs([(50, 28), (48, 30), (52, 30), (50, 32), (46, 26), (54, 26)], "white")
        p.tag((PW // 2, 2), "MY SHOOTERS", "ink", "white", anchor="ma")
        return p.img
    p = Pic("panel")
    p.rect((28, 1, 72, 50), "yellow"); p.rect((32, 5, 68, 46), "sky")                       # the yellow border
    p.put(animals.hawk(1), 50, 27)
    p.rect((32, 38, 68, 46), "black"); p.silk((50, 40), "COVER", "yellow", anchor="ma")
    p.d.rectangle((28, 1, 72, 50), outline=INK)
    p.silk((14, 20), "SHOT", "dim", anchor="ma"); p.silk((14, 27), "BY:", "dim", anchor="ma")
    p.silk((86, 20), "MY", "text", anchor="ma"); p.silk((86, 27), "CREW", "text", anchor="ma")
    return p.img


@gag("v4", 1)
def national_geographic(c, L):
    stage = 1 if L.on("National") else 0
    show(c, nat_geo(stage, int(c.t * 6) % 3 == 0), "SHOOTERS" if not stage else "PUBLISHED", "ISO")
    if L.on("Geographic"):
        pose(c, MAYA, arms="shrug", brows="up", mouth="grin" if L.age("Geographic") > 0.6 else c.st[MAYA]["mouth"])
    yield "front"
    if not stage and L.on("shoot"):
        c.add_flash(0.25 * max(0, 1 - L.age("shoot") / 0.15))


# --- 2-3: fine art ---------------------------------------------------------------------------------------------

def gold_frame(p, box):
    x0, y0, x1, y1 = box
    p.rect(box, "gold"); p.d.rectangle(box, outline=INK)
    p.rect((x0 + 3, y0 + 3, x1 - 3, y1 - 3), "gold_sh")
    p.d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline=col("gold_hi"))
    return x0 + 4, y0 + 4, x1 - 4, y1 - 4


@lru_cache(maxsize=None)
def fine_art(stage):
    p = Pic("ewall")
    p.rect((0, 44, PW, PH), "ewall_sh")
    if stage < 2:
        a, b, c_, d = gold_frame(p, (6, 4, 52, 42))
        p.rect((a, b, c_, d), "cream")
        p.poly([(4, 2), (54, 2), (56, 30), (50, 44), (40, 38), (30, 45), (18, 39), (8, 44), (2, 30)], "white")   # a dust sheet
        p.line([(18, 6), (16, 36)], "grey_hi"); p.line([(34, 5), (36, 40)], "grey_hi"); p.line([(46, 8), (48, 38)], "grey_hi")
        p.press((30, 16), "?", "grey_sh", anchor="ma")
        p.rbox((60, 6, 96, 26), "paper", "ink", 2); p.silk((78, 9), "PAID:", "grey_sh", anchor="ma")
        p.silk((78, 17), "1 CAR", "live", anchor="ma")
        if stage:                                                        # the car it could have been
            p.poly([(62, 44), (62, 38), (68, 37), (72, 32), (86, 32), (90, 37), (96, 38), (96, 44)], "red")
            p.rect((74, 34, 84, 37), "sky_hi"); p.ell((66, 41, 73, 48), "black"); p.ell((85, 41, 92, 48), "black")
            p.cross(79, 39, "ink", 6)
        return p.img
    a, b, c_, d = gold_frame(p, (22, 1, 78, 41))
    p.grad((a, b, c_ + 1, d + 1), "sky_hi", "pink", steps=3)              # the painting: a cat, done with love
    cx, cy = 50, 24
    p.poly([(cx - 11, cy - 4), (cx - 12, cy - 15), (cx - 3, cy - 9)], "orange"); p.poly([(cx + 11, cy - 4), (cx + 12, cy - 15), (cx + 3, cy - 9)], "orange")
    p.ell((cx - 13, cy - 10, cx + 13, cy + 12), "orange"); p.ell((cx - 7, cy + 2, cx + 7, cy + 12), "cream")
    p.rect((cx - 7, cy - 3, cx - 4, cy + 1), "green_sh"); p.rect((cx + 4, cy - 3, cx + 7, cy + 1), "green_sh")
    p.px((cx - 5, cy - 2), "ink"); p.px((cx + 6, cy - 2), "ink"); p.poly([(cx - 1, cy + 3), (cx + 1, cy + 3), (cx, cy + 5)], "pink")
    p.line([(cx - 3, cy + 6), (cx - 1, cy + 8), (cx, cy + 6), (cx + 1, cy + 8), (cx + 3, cy + 6)], "ink")
    for s in (-1, 1):
        p.line([(cx + s * 8, cy + 4), (cx + s * 16, cy + 2)], "white"); p.line([(cx + s * 8, cy + 6), (cx + s * 16, cy + 7)], "white")
    p.tag((PW // 2, 44), "M. HIGA: CAT", "gold", "ink", anchor="ma")
    return p.img


@gag("v4", 2)
def spent_a_car(c, L):
    show(c, fine_art(1 if L.on("car") else 0), "THE COLLECTION", "ART")
    if L.on("ask"):
        pose(c, EMI, arms="window", brows="up", eyes="side")
    yield "front"


@gag("v4", 3)
def painting_of_her_cat(c, L):
    show(c, fine_art(2 if L.on("Maya") else 1), "THE COLLECTION", "ART")
    if L.on("Maya"):
        pose(c, EMI, arms="window", brows="up", eyes="side", mouth="grin" if L.age("cat") > 0.4 else c.st[EMI]["mouth"])
        pose(c, MAYA, arms="chest", brows="up", mouth="grin", eyes="shut" if 0.2 < L.age("cat") < 1.0 else "open")
    yield "front"
    jolt(c, L.age("cat"), 2)


# --- 4-5: clean cash --------------------------------------------------------------------------------------------

def bill(p, x, y):
    p.rect((x, y, x + 22, y + 10), "green_hi"); p.d.rectangle((x, y, x + 22, y + 10), outline=col("green_sh"))
    p.ell((x + 8, y + 2, x + 14, y + 8), "green"); p.px((x + 2, y + 2), "green_sh"); p.px((x + 20, y + 8), "green_sh")


@lru_cache(maxsize=None)
def clean_cash(stage, f):
    p = Pic("sky_hi")
    p.rect((0, 40, PW, PH), "steel")
    p.line([(4, 12), (62, 12)], "ink")                                   # a washing line
    for i, x in enumerate((6, 34)):
        bill(p, x, 13 + (f + i) % 2); p.rect((x + 10, 10, x + 12, 15), "wood")
    for i, (x, y) in enumerate(((10, 30), (26, 34), (44, 29), (56, 35), (20, 27))):          # suds
        p.d.ellipse((x, y - (f + i) % 3, x + 4, y + 4 - (f + i) % 3), outline=col("white"))
    p.pxs([(3, 9), (30, 6), (60, 8)], "white")
    if stage >= 1:                                                       # and the reason nobody can touch them
        p.poly([(68, 6), (96, 6), (96, 28), (82, 42), (68, 28)], "maya_sh"); p.d.polygon([(68, 6), (96, 6), (96, 28), (82, 42), (68, 28)], outline=INK)
        p.silk((82, 11), "501", "white", anchor="ma"); p.silk((82, 19), "C 3", "white", anchor="ma")
    if stage >= 2:
        p.tag((2, 43), "UNTOUCHABLE", "ink", "gold")
    return p.img


@gag("v4", 4)
def clean_cash_baby(c, L):
    stage = 2 if L.on("untouchable") else 1 if L.on("whole") else 0
    show(c, clean_cash(stage, c.f // 4 % 6), "LAUNDRY DAY", "$")
    if L.on("untouchable"):
        pose(c, MAYA, arms="chop", brows="skeptic", eyes="half")
    yield "front"


@lru_cache(maxsize=None)
def tax_receipt(n):
    p = Pic("panel")
    p.rect((6, 0, PW - 7, PH), "paper")
    for x in range(6, PW - 7, 4):
        p.poly([(x, PH - 3), (x + 2, PH - 6), (x + 4, PH - 3)], "panel")
    p.silk((PW // 2, 3), "DONATION", "ink", anchor="ma"); p.line([(10, 10), (89, 10)], "paper_sh")
    rows = (("FROM", "EMIRU", "emiru_sh"), ("FOR", "1 CAT", "ink"), ("TAX", "$0", "green_sh"))
    for i, (k, v, cc) in enumerate(rows[:n]):
        p.silk((11, 14 + 9 * i), k, "grey_sh"); p.silk((88, 14 + 9 * i), v, cc, anchor="ra")
    if n >= 4:
        p.tag((PW // 2, 39), "DEDUCTIBLE", "ok", "ink", anchor="ma")
    return p.img


@gag("v4", 5)
def tax_deductible(c, L):
    show(c, tax_receipt(1 + count(L, "she", "dropped", "tax")), "RECEIPT", "IRS")
    if L.on("tax"):
        pose(c, EMI, arms="thumbs2", brows="up", mouth="grin")
    yield "front"


# --- 6-7: the getaway -------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def getaway(stage, f):
    p = Pic("night")
    if stage == 0:
        p.rect((0, 0, PW, PH), "maya_sh"); p.d.rectangle((2, 2, PW - 3, PH - 5), outline=col("white"))
        p.silk((PW // 2, 8), "HOUSE RULE", "maya_hi", anchor="ma")
        p.press((PW // 2, 18), "WE DON'T", "white", anchor="ma", shadow="ink"); p.press((PW // 2, 30), "RUN.", "white", anchor="ma", shadow="ink")
        return p.img
    p.rect((0, 34, PW, PH), "stone_sh"); p.line([(0, 34), (PW, 34)], "ink")
    for x in range(-8 + (f % 4) * 3, PW, 12):
        p.line([(x, 43), (x + 6, 43)], "yellow")
    x = 14                                                               # the car, its top down, and who is driving
    p.put(animals.tortoise(0, True), x + 38, 19)
    p.poly([(x, 38), (x, 27), (x + 16, 24), (x + 56, 24), (x + 72, 28), (x + 72, 38)], "red")
    p.d.polygon([(x, 38), (x, 27), (x + 16, 24), (x + 56, 24), (x + 72, 28), (x + 72, 38)], outline=INK)
    p.line([(x + 3, 29), (x + 68, 29)], "red_hi"); p.line([(x + 54, 24), (x + 60, 13)], "steel", w=2)     # the windscreen
    p.ell((x + 8, 32, x + 20, 44), "black"); p.ell((x + 52, 32, x + 64, 44), "black")
    p.ell((x + 12, 36, x + 16, 40), "steel"); p.ell((x + 56, 36, x + 60, 40), "steel")
    p.rect((x + 70, 29, x + 72, 32), "yellow")
    p.poly([(x + 2, 22), (x + 12, 22), (x + 13, 26), (x + 1, 26)], "cream"); p.silk((x + 4, 20), "$", "green_sh")   # the bag
    p.tag((PW - 2, 2), "%.1f MPH" % (0.2 + 0.1 * (f % 2)), "ink", "ok", anchor="ra")
    return p.img


@gag("v4", 6)
def we_dont_run(c, L):
    show(c, getaway(0, 0), "POLICY", "1")
    if L.on("important"):
        pose(c, MAYA, arms="finger", brows="up")
    yield "front"


@gag("v4", 7)
def getaway_driver(c, L):
    show(c, getaway(1 if L.on("getaway") else 0, c.f // 6 % 8), "GETAWAY", "SLOW")
    if L.on("tortoise"):
        pose(c, MAYA, arms="shrug", brows="up", mouth="grin" if L.age("tortoise") > 0.6 else c.st[MAYA]["mouth"])
    yield "front"
    jolt(c, L.age("tortoise"), 2)


T_IN, T_OUT = when("v4", 7, "getaway"), when("v4", 9) + 2.0


@span(T_IN, T_OUT)
def the_driver_herself(c, L):
    """And there she goes, across the field behind them, in her cap."""
    yield "back"
    k = (c.t - T_IN) / (T_OUT - T_IN)
    spr = animals.tortoise(int(c.t * 3) % 2, True)
    c.cam[EMI].paste(spr, (int(186 + 34 * k), 114), spr)


# --- 8-9: the fence stays on ---------------------------------------------------------------------------------------

def no_tile(p, i, kind, crossed):
    x = 3 + 24 * i
    p.rbox((x, 8, x + 21, 34), "panel_hi", "ink", 2)
    cx, cy = x + 11, 19
    if kind == "PET":                                                    # a paw
        p.ell((cx - 4, cy - 1, cx + 4, cy + 6), "cream")
        for dx in (-5, -2, 2, 5):
            p.ell((cx + dx - 1, cy - 5 + abs(dx) // 3, cx + dx + 1, cy - 2 + abs(dx) // 3), "cream")
    elif kind == "DOLL":                                                 # a doll
        p.ell((cx - 4, cy - 7, cx + 4, cy), "eskin"); p.poly([(cx - 5, cy + 8), (cx, cy), (cx + 5, cy + 8)], "pink")
        p.px((cx - 2, cy - 4), "ink"); p.px((cx + 2, cy - 4), "ink")
    elif kind == "WIFE":                                                 # a ring
        p.d.ellipse((cx - 5, cy - 2, cx + 5, cy + 8), outline=col("gold"), width=2)
        p.poly([(cx - 3, cy - 3), (cx, cy - 7), (cx + 3, cy - 3)], "sky_hi")
    else:                                                                # a heart, the kind a tattoo has
        p.heart(cx - 5, cy - 3, "red"); p.heart(cx, cy - 3, "red"); p.rect((cx - 4, cy - 1, cx + 4, cy + 2), "red")
        p.poly([(cx - 5, cy + 2), (cx + 5, cy + 2), (cx, cy + 7)], "red")
    p.silk((cx, 37), kind, "text", anchor="ma")
    if crossed:
        p.cross(cx, 19, "live", 8)


@lru_cache(maxsize=None)
def not_yours(n):
    p = Pic("panel")
    p.silk((PW // 2, 1), "I AM NOT YOUR:", "emiru_hi", anchor="ma")
    for i, kind in enumerate(("PET", "DOLL", "WIFE", "MOM")):
        no_tile(p, i, kind, i < n)
    return p.img


@gag("v4", 8)
def not_your_mom(c, L):
    n = count(L, "pet", "doll", "wife", "mom")
    show(c, not_yours(n), "TERMS", "X%d" % max(n, 1))
    pose(c, EMI, arms="finger" if n % 2 else "chop", brows="skeptic", eyes="half")
    yield "front"
    for w in ("pet", "doll", "wife", "mom"):
        jolt(c, L.age(w), 1.5, 0.15)


@lru_cache(maxsize=None)
def fence_on(stage, zap):
    p = Pic("panel")
    p.poly([(14, 8), (30, 8), (36, 20), (22, 38), (8, 20)], "twitch"); p.d.polygon([(14, 8), (30, 8), (36, 20), (22, 38), (8, 20)], outline=INK)
    p.poly([(22, 13), (24, 19), (30, 19), (25, 23), (27, 29), (22, 25), (17, 29), (19, 23), (14, 19), (20, 19)], "gold")
    p.silk((22, 42), "$4.99", "text", anchor="ma")
    if stage:
        p.rect((46, 0, PW, PH), "pasture"); p.rect((46, 0, PW, 20), "sky_hi")
        for x in (52, 72, 92):
            p.rect((x, 10, x + 2, 46), "grey_sh")
        for y in (16, 26, 36):
            p.line([(46, y), (PW, y)], "steel_hi" if zap else "steel")
        if zap:
            p.line([(60, 14), (64, 20), (60, 22), (65, 30)], "yellow", w=2); p.line([(82, 22), (86, 28), (82, 30), (87, 38)], "yellow", w=2)
        p.tag((PW - 2, 43), "FENCE: ON", "live", "white", anchor="ra")
    return p.img


@gag("v4", 9)
def the_fence_stays_on(c, L):
    show(c, fence_on(1 if L.on("fence") else 0, int(c.t * 8) % 2), "SUB PERKS", "T1")
    if L.on("fence"):
        pose(c, MAYA, arms="thumb", brows="up", mouth="grin" if L.age("on") > 0.3 else c.st[MAYA]["mouth"])
    yield "front"


# --- 10-11: killers ----------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def killers(stage, f):
    p = Pic("black")
    if stage < 2:
        p.header("ON CALL", "red_sh", "white", h=9)
        shape = animals.scorpion()
        dark = Image.new("RGBA", shape.size, rgba("bg")); dark.putalpha(shape.getchannel("A"))
        for i, x in enumerate((26, 72)):
            p.rect((x - 18, 12, x + 18, 40), "night"); p.d.rectangle((x - 18, 12, x + 18, 40), outline=col("red_sh"))
            p.put(dark, x, 26)
            p.px((x + 5, 25), "live"); p.px((x + 5, 28), "live")
        if stage:
            p.silk((26, 43), "ARMORED", "live", anchor="ma"); p.silk((72, 43), "UGLY", "live", anchor="ma")
        return p.img
    p.rect((0, 0, PW, PH), "pink"); p.grad((0, 0, PW, PH), "emiru_hi", "pink", steps=3)
    for i, (x, name) in enumerate(((26, "TORTELLINI"), (74, "PUPPY"))):
        if i == 0 or stage >= 3:
            p.put(scaled(animals.scorpion(("red", "blue")[i], (f + i) % 2), 1), x, 20)
            p.heart(x - 2, 4 + (f + i) % 2, "red")
            w = silk_w(name) + 5
            p.tag((min(max(x, w // 2 + 1), PW - w // 2 - 2), 34), name, "white", "ink", anchor="ma")
    p.silk((PW // 2, 45), "EMPEROR SCORPIONS", "ink", anchor="ma")
    return p.img


@gag("v4", 10)
def killers_on_call(c, L):
    show(c, killers(1 if L.on("armored") else 0, 0), "THE MUSCLE", "2")
    pose(c, MAYA, brows="skeptic", eyes="half")
    yield "front"


@gag("v4", 11)
def tortellini_and_puppy(c, L):
    stage = 3 if L.on("Puppy") else 2 if L.on("Tortellini") else 1
    show(c, killers(stage, c.f // 6 % 4), "THE MUSCLE", "2")
    if stage >= 2:
        pose(c, MAYA, arms="beg" if stage == 3 else "chest", brows="up", mouth="grin")
        pose(c, EMI, brows="up", mouth="grin" if stage == 3 else "smile")
    yield "front"
    jolt(c, L.age("Puppy"), 2)


# --- 12-13: touch grass ---------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def bot_lane(stage, chew):
    p = Pic("rift")
    if stage == 0:
        p.rect((0, 0, PW, PH), "bg"); p.rect((2, 30, PW - 3, 46), "rift"); p.d.rectangle((2, 30, PW - 3, 46), outline=col("line"))
        p.silk((5, 8), "[ALL] EMIRU:", "emiru_hi"); p.silk((5, 18), "BOT LANE'S", "text")
        p.silk((5, 35), "FEEDING", "live"); p.rect((49, 34, 50, 41), "text")
        return p.img
    p.rect((0, 0, PW, PH), "pasture_sh")                                  # the map: bottom lane, and lunch
    p.poly([(0, 30), (PW, 30), (PW, 48), (0, 48)], "dirt"); p.line([(0, 30), (PW, 30)], "dirt_sh"); p.line([(0, 48), (PW, 48)], "dirt_sh")
    for x in (6, 30, 84):
        p.ell((x, 4, x + 14, 18), "tree_sh")
    p.rect((80, 20, 90, 30), "blue"); p.poly([(78, 20), (85, 12), (92, 20)], "blue_hi")       # a turret
    p.rect((50, 32, 66, 44), "hay"); p.d.rectangle((50, 32, 66, 44), outline=INK)             # the hay
    p.line([(50, 36), (66, 36)], "hay_sh"); p.line([(50, 40), (66, 40)], "hay_sh")
    p.put(animals.winnie(chew), 26, 32)
    p.tag((PW - 2, 2), "FED", "ok", "ink", anchor="ra")
    return p.img


@gag("v4", 12)
def bot_lanes_feeding(c, L):
    show(c, bot_lane(1 if L.on("brought") else 0, int(c.t * 2.2) % 2), "ALL CHAT" if not L.on("brought") else "BOT LANE", "GG")
    if L.on("brought"):
        pose(c, EMI, arms="facepalm" if L.age("hay") > 0.3 else "palm", eyes="shut" if L.age("hay") > 0.3 else "side")
        pose(c, MAYA, arms="thumbs2", brows="up", mouth="grin")
    yield "front"
    jolt(c, L.age("hay"), 2)


@lru_cache(maxsize=None)
def touch_grass(stage):
    p = Pic("bg")
    p.header("EMI", "bar", "emiru_hi", h=9)
    if stage >= 1:
        bubble(p, (24, 13, 94, 25), "TOUCH GRASS", "maya", "ink", right=True)
    if stage >= 2:
        bubble(p, (5, 31, 81, 43), "WHICH PATCH?", "emiru", "ink")
    return p.img


@gag("v4", 13)
def which_patch(c, L):
    show(c, touch_grass(2 if L.on("Which") else 1 if L.on("Touch") else 0), "TEXTS", "NOW")
    if L.on("Which"):
        pose(c, EMI, arms="shrug", brows="up", eyes="open", mouth="open" if L.age("patch") < 0.3 else "smile")
        pose(c, MAYA, arms="facepalm", eyes="shut", mouth="grin")
    yield "front"
    jolt(c, L.age("patch"), 3)


# --- 14-15: out of your league ----------------------------------------------------------------------------------------

def crest(p, x, color, shade, who):
    p.poly([(x - 20, 4), (x + 20, 4), (x + 20, 30), (x, 46), (x - 20, 30)], color)
    p.d.polygon([(x - 20, 4), (x + 20, 4), (x + 20, 30), (x, 46), (x - 20, 30)], outline=INK)
    p.d.polygon([(x - 17, 7), (x + 17, 7), (x + 17, 29), (x, 42), (x - 17, 29)], outline=col(shade))
    p.put(mug(who, "open", "neutral", "grin"), x, 23)


@lru_cache(maxsize=None)
def two_leagues(n):
    p = Pic("night")
    p.grad((0, 0, PW, PH), "night_hi", "night", steps=3)
    if n >= 1:
        crest(p, 26, "lol_gold", "gold_hi", "emiru")
        p.silk((26, 46), "LEGENDS", "lol_gold", anchor="ma")
    if n >= 2:
        crest(p, 74, "maya", "maya_hi", "maya")
        p.silk((74, 46), "HER OWN", "maya_hi", anchor="ma")
    return p.img


@gag("v4", 14)
def a_league_of_her_own(c, L):
    show(c, two_leagues(1 + (1 if L.on("one's", 1) else 0)), "THE LEAGUES", "2")
    pose(c, EMI, arms="chest" if not L.on("one's", 1) else "palm", brows="up")
    pose(c, MAYA, arms="chest" if L.on("one's", 1) else "desk", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def bronze(stage):
    p = Pic("night")
    if stage == 0:
        return title_pic()
    p.grad((0, 0, PW, PH), "night_hi", "night", steps=3)
    cx = 19                                                              # the rank they gave you
    p.poly([(cx - 16, 8), (cx, 2), (cx + 16, 8), (cx + 12, 34), (cx, 42), (cx - 12, 34)], "brown_hi")
    p.d.polygon([(cx - 16, 8), (cx, 2), (cx + 16, 8), (cx + 12, 34), (cx, 42), (cx - 12, 34)], outline=INK)
    p.poly([(cx - 10, 11), (cx, 7), (cx + 10, 11), (cx + 7, 30), (cx, 36), (cx - 7, 30)], "brown")
    p.line([(cx - 4, 14), (cx - 4, 28)], "brown_hi"); p.silk((cx, 44), "IV", "brown_hi", anchor="ma")
    p.silk((42, 6), "YOUR RANK", "dim"); p.press((42, 15), "BRONZE", "brown_hi", shadow="ink")
    if stage >= 2:
        p.verdict(67, 38, "GO HOME", "live", "night")
    return p.img


@gag("v4", 15)
def yours_is_bronze(c, L):
    stage = 2 if L.on("go") else 1 if L.on("yours") else 0
    show(c, bronze(stage), "RANKED" if stage else "NOW PLAYING", "LP")
    if stage == 0:
        both(c, arms="point", brows="up")
    elif stage == 1:
        both(c, arms="shrug", brows="up", eyes="half")
    else:
        both(c, arms="wave", brows="up", mouth="grin" if L.age("home") > 0.5 else "open")
    yield "front"
    jolt(c, L.age("Bronze"), 2)
    jolt(c, L.age("home"), 3)
