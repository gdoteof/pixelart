"""Verse 2: Asmongold, on his stream. Hasan's video sits paused in the window, and Asmongold clicks things up
over it: whatever he pulls up looks like a game's interface."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403


def click(c, L, *pats):
    """He clicks the next thing up: a tap of the mouse as the line (or each of these words) starts."""
    ages = [L.age(p) for p in pats] or [L.age()]
    if any(0 <= a < 0.28 for a in ages):
        pose(c, "asmon", arms="click", eyes="down")


# --- 0-1: has an alibi ---------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def handle_pic(stage):
    """His handle, read again."""
    p = Pic("hasan_sh")
    p.press((PW // 2, 9), "HASANABI", "white", anchor="ma", shadow="ink")
    if stage:
        p.line([(PW // 2, 21), (PW // 2, 27)], "white")
        p.pxs([(PW // 2 - 2, 25), (PW // 2 - 1, 26), (PW // 2 + 1, 26), (PW // 2 + 2, 25)], "white")
        if stage == 1:
            p.press((PW // 2, 33), "HAS AN ABI", "yellow", anchor="ma", shadow="ink")
        else:
            x = (PW - 96) // 2
            p.press((x, 33), "HAS AN A", "yellow", shadow="ink")
            p.press((x + 64, 33), "LI", "live", shadow="ink")
            p.press((x + 80, 33), "BI", "yellow", shadow="ink")
    return p.img


@gag("v2", 0)
def has_an_alibi(c, L):
    stage = 2 if L.on("alibi") else 1 if L.on("^.has$") else 0
    show(c, handle_pic(stage), "HASANABI", "NAME")
    click(c, L)
    if L.on("alibi"):
        pose(c, "asmon", arms="shrug", eyes="half", brows="up")
    yield "front"


def dog_face(p, x, y):
    """Kaya, from the front (10 x 9)."""
    p.rect((x + 1, y + 1, x + 8, y + 8), "dog")
    p.rect((x, y, x + 2, y + 4), "dog_sh"); p.rect((x + 7, y, x + 9, y + 4), "dog_sh")       # the ears
    p.rect((x + 3, y + 5, x + 6, y + 8), "dog_dk")                                          # the muzzle
    p.px((x + 3, y + 3), "ink"); p.px((x + 6, y + 3), "ink")


@lru_cache(maxsize=None)
def alibis(n):
    """The alibis, as he reaches for them."""
    p = Pic("panel")
    p.header("HASAN'S ALIBIS", "hasan", "white", h=9)
    for i, s in enumerate(("OUT OF CONTEXT", "IT WAS SATIRE", "THE DOG LIED")[:n]):
        y = 12 + 14 * i
        p.rect((3, y, 96, y + 11), "panel_hi")
        p.silk((6, y + 3), s, "text")
        if i < 2:
            p.tick(87, y + 2, "ok")
        else:
            dog_face(p, 85, y + 1)
    return p.img


@gag("v2", 1)
def three_alibis(c, L):
    show(c, alibis(count(L, "Out", "Satire", "dog")), "HASANABI", "LOG")
    click(c, L, "Out", "Satire", "dog")
    if L.on("lie"):
        pose(c, "asmon", arms="shrug", eyes="half", brows="up")
    yield "front"


# --- 2-3: cancel rent, eat the rich ----------------------------------------------------------------------

@lru_cache(maxsize=None)
def rent_pic(stage):
    """What he chants, and where he goes afterwards. stage 1: home; 2: what home cost."""
    p = Pic("sky")
    p.rect((0, 45, PW, PH), "grass"); p.line([(0, 45), (PW, 45)], "grass_sh")
    p.rect((21, 26, 22, 50), "wood_hi")                                                    # the placard, on its stick
    p.rbox((1, 3, 42, 26), "white", "ink", 1)
    p.silk((22, 6), "CANCEL", "live", anchor="ma"); p.silk((22, 15), "RENT", "live", anchor="ma")
    p.rbox((18, 36, 26, 44), "hskin", "ink", 2)                                            # in his fist
    p.line([(19, 39), (25, 39)], "hskin_sh")
    if stage >= 1:
        p.line([(46, 32), (51, 32)], "ink"); p.pxs([(50, 31), (50, 33), (49, 30), (49, 34)], "ink")
        villa(p, 50, 12)
    if stage >= 2:
        p.tag((57, 2), "$2.74M", "gold", "ink")
        p.rect((60, 46, 61, 51), "wood_sh"); p.tag((52, 41), "SOLD", "live", "white")
    return p.img


@gag("v2", 2)
def cancel_rent(c, L):
    stage = 2 if L.on("gentrify") else 1 if L.on("home") else 0
    show(c, rent_pic(stage), "HASANABI", "IRL")
    click(c, L, "home")
    yield "front"


@lru_cache(maxsize=None)
def eat_pic(stage):
    """Dinner is served. stage 1: and it has a name."""
    p = Pic("night")
    p.header("EAT THE RICH", "live", "white", h=9)
    p.ell((22, 38, 78, 53), "white"); p.d.ellipse((22, 38, 78, 53), outline=INK)             # the plate
    p.ell((29, 41, 71, 50), "paper_sh")
    p.rect((11, 22, 12, 50), "steel")                                                       # a fork
    for x in (8, 11, 14):
        p.rect((x, 14, x, 22), "steel")
    p.line([(8, 22), (14, 22)], "steel")
    p.rect((87, 26, 88, 50), "steel")                                                       # a knife
    p.poly([(86, 14), (90, 18), (90, 28), (86, 28)], "steel_hi")
    face = ("wide", "worried", "o") if stage else ("side", "neutral", "closed")
    p.put(mug("hasan", *face), 50, 30)
    if stage:
        p.line([(68, 20), (62, 24)], "gold"); p.tag((66, 12), "RICH", "gold", "ink")
    return p.img


@gag("v2", 3, post=0.7)
def eat_the_rich(c, L):
    show(c, eat_pic(1 if L.on("self") else 0), "MENU", "TODAY")
    click(c, L)
    if L.on("self"):
        pose(c, "asmon", arms="point", eyes="half", brows="up", mouth="smirk")
    yield "front"


# --- 4-5: boosted ----------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def party_pic(stage):
    """The party frame: who is carrying whom. stage 1: boosted; 2: what he earned himself."""
    p = Pic("bg")
    p.header("BOOSTED BY UNCLE" if stage else "PARTY", "panel_hi", "gold", h=9)
    rows = (("UNCLE", "60", 1.0, "ok"), ("HASAN", "60" if stage else "1", 1.0 if stage else 0.06, "gold" if stage else "live"))
    for i, (name, lv, k, colr) in enumerate(rows):
        y = 12 + 15 * i
        p.panel((2, y, 97, y + 12), "line", "panel")
        p.silk((5, y + 1), name, "text")
        p.silk((95, y + 1), "LV " + lv, "gold" if lv == "60" else "dim", anchor="ra")
        p.meter((5, y + 9, 94, y + 10), k, colr)
    if stage == 2:
        p.silk((PW // 2, 43), "XP EARNED: 0", "live", anchor="ma")
    return p.img


@gag("v2", 4)
def boosted(c, L):
    stage = 2 if L.on("never") else 1 if L.on("booster") else 0
    show(c, party_pic(stage), "HASANABI", "LV ?")
    click(c, L)
    yield "front"


def baby_pic(stage, t):
    """Pay-to-win since Pampers. stage 1: the pocket-money rebel."""
    p = Pic("hwall")
    p.header("PAY TO WIN", "panel_hi", "gold", h=9)
    p.rect((0, 47, PW, PH), "bed_st")
    cx = 30
    if stage:                                                                               # the fist goes up
        p.line([(cx - 7, 32), (cx - 14, 23)], "hskin", 3)
        p.rbox((cx - 18, 17, cx - 12, 23), "hskin", "ink", 1)
    p.line([(cx + 7, 32), (cx + 15, 25)], "hskin", 3)                                        # the arm with the card
    p.ell((cx - 8, 29, cx + 8, 43), "hskin"); p.d.ellipse((cx - 8, 29, cx + 8, 43), outline=INK)
    p.ell((cx - 13, 42, cx - 4, 48), "hskin"); p.ell((cx + 4, 42, cx + 13, 48), "hskin")     # legs
    p.poly([(cx - 9, 37), (cx + 9, 37), (cx + 6, 46), (cx - 6, 46)], "white")                # the nappy
    p.d.line([(cx - 9, 37), (cx + 9, 37), (cx + 6, 46), (cx - 6, 46), (cx - 9, 37)], fill=INK); p.px((cx, 39), "gold")
    p.ell((cx - 9, 13, cx + 9, 30), "hskin"); p.d.ellipse((cx - 9, 13, cx + 9, 30), outline=INK)   # the head
    p.rect((cx - 6, 13, cx + 6, 15), "hhair"); p.rect((cx - 3, 11, cx + 2, 13), "hhair")
    p.rect((cx - 6, 19, cx - 3, 19), "hhair"); p.rect((cx + 2, 19, cx + 5, 19), "hhair")     # the brows, already
    p.rect((cx - 5, 21, cx - 4, 23), "eye"); p.rect((cx + 3, 21, cx + 4, 23), "eye")
    p.ell((cx - 2, 25, cx + 2, 28), "pink"); p.px((cx, 26), "white")                         # a dummy
    p.rbox((cx + 12, 15, cx + 27, 25), "gold", "ink", 1)                                     # the card
    p.rect((cx + 13, 18, cx + 26, 19), "ink"); p.rect((cx + 14, 21, cx + 18, 23), "gold_hi")
    if stage:
        p.ell((cx - 11, 9, cx + 8, 16), "red"); p.d.arc((cx - 11, 9, cx + 8, 16), 180, 360, fill=INK)   # the beret
        p.px((cx - 2, 8), "red"); p.pxs([(cx - 5, 12), (cx - 4, 12), (cx - 6, 12), (cx - 5, 11), (cx - 5, 13)], "gold")
        p.ell((62, 27, 88, 43), "pink"); p.d.ellipse((62, 27, 88, 43), outline=INK)             # the piggy bank
        p.rect((87, 32, 91, 38), "pink"); p.d.rectangle((87, 32, 91, 38), outline=INK); p.pxs([(89, 34), (89, 36)], "ink")
        p.poly([(80, 28), (83, 23), (85, 29)], "pink"); p.px((82, 32), "ink")
        p.rect((66, 43, 68, 46), "pink"); p.rect((81, 43, 83, 46), "pink")
        p.rect((70, 27, 77, 27), "ink")
        k = (t * 1.6) % 1.0                                                                 # this week's allowance
        p.ell((71, 10 + int(14 * k), 76, 15 + int(14 * k)), "gold"); p.d.ellipse((71, 10 + int(14 * k), 76, 15 + int(14 * k)), outline=INK)
    return p.img


@gag("v2", 5)
def pocket_money(c, L):
    show(c, baby_pic(1 if L.on("pocket") else 0, c.t), "HASANABI", "AGE 0")
    click(c, L)
    yield "front"


# --- 6-7: a skin ------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def shop_pic(stage):
    """The item shop. stage 1: one skin picked out; 2: bought."""
    p = Pic("bg")
    p.header("ITEM SHOP", "panel_hi", "gold", h=9)
    for i, bg in enumerate(("red", "green_sh", "purple_sh")):
        x = 5 + 32 * i
        p.rect((x, 12, x + 26, 34), bg)
        p.d.rectangle((x, 12, x + 26, 34), outline=col("gold_hi" if i == 0 and stage else "line"))
    star = [(18 + 8 * math.sin(a * math.pi / 5) * (1 if a % 2 == 0 else 0.42),
             23 - 8 * math.cos(a * math.pi / 5) * (1 if a % 2 == 0 else 0.42)) for a in range(10)]
    p.poly(star, "gold")                                                                    # a red star
    p.silk((50, 15), "$", "gold_hi", anchor="ma", fnt=SILK16)                               # a dollar
    p.put(crown_small(), 82, 23)                                                            # a crown
    if stage >= 1:
        p.silk((PW // 2, 37), "SOCIALIST SKIN", "gold_hi", anchor="ma")
        p.silk((PW // 2, 46), "COSMETIC ONLY", "dim", anchor="ma")
        p.poly([(22, 26), (22, 35), (25, 32), (28, 37), (30, 36), (27, 31), (31, 31)], "white")   # the pointer
        p.d.line([(22, 26), (22, 35), (25, 32), (28, 37), (30, 36), (27, 31), (31, 31), (22, 26)], fill=INK)
    else:
        p.silk((PW // 2, 41), "SKINS", "dim", anchor="ma")
    if stage >= 2:                                                                          # bought
        p.rect((22, 13, 30, 21), "bg"); p.tick(23, 14, "ok")
    return p.img


@gag("v2", 6)
def just_a_skin(c, L):
    stage = 2 if L.on("picked") else 1 if L.on("skin") else 0
    show(c, shop_pic(stage), "HASANABI", "SHOP")
    click(c, L, "picked")
    yield "front"


@lru_cache(maxsize=None)
def inspect_pic(stage):
    """Inspecting him. stage 1: what he wears on his head; 2: and over it."""
    p = Pic("bg")
    p.header("INSPECT: HASAN", "panel_hi", "gold", h=9)
    p.panel((3, 12, 37, 52), "line", "panel")
    p.poly([(6, 52), (9, 45), (15, 42), (26, 42), (32, 45), (35, 52)], "hskin")              # shoulders
    p.poly([(13, 52), (15, 43), (26, 43), (28, 52)], "tank")                                 # and the top
    p.put(mug("hasan", "half", "skeptic", "smirk"), 20, 31)
    if stage >= 1:
        p.put(crown_small(), 20, 15)
    for i, (slot, item, colr) in enumerate((("HEAD", "PRINCE", "gold_hi"), ("CHEST", "PROLE TOP", "text"))[:stage]):
        y = 14 + 19 * i
        p.silk((41, y), slot, "dim")
        p.silk((41, y + 8), item, colr)
    return p.img


@gag("v2", 7, post=0.7)
def prince_in_a_top(c, L):
    stage = 2 if L.on("proletarian") else 1 if L.on("prince") else 0
    show(c, inspect_pic(stage), "HASANABI", "GEAR")
    click(c, L)
    if L.on("top"):
        pose(c, "asmon", arms="point", eyes="half", brows="up", mouth="smirk")
    yield "front"


# --- 8-9: baths -------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def baths_pic(n, half):
    p = Pic("hwall")
    p.header("LISTING: BATHS", "blue", "white", h=9)
    for i in range(n):
        tub(p, 6 + 32 * (i % 3), 16 + 19 * (i // 3))
    if half:
        tub(p, 6 + 32 * 2, 35, half=True)
    return p.img


@gag("v2", 8)
def five_and_a_half(c, L):
    n = min(5, 1 + int(L.age("five") / 0.07)) if L.on("five") else 0
    show(c, baths_pic(n, L.on("half")), "HASANABI", "HOME")
    click(c, L)
    yield "front"


@lru_cache(maxsize=None)
def baths_score(stage):
    """Baths this year: his, and mine."""
    p = Pic("bg")
    p.header("BATHS THIS YEAR", "panel_hi", "gold", h=9)
    p.panel((3, 12, 48, 51), "hasan", "panel"); p.panel((51, 12, 96, 51), "asmon", "panel")
    p.silk((26, 15), "HIM", "hasan_hi", anchor="ma"); p.silk((74, 15), "ME", "asmon_hi", anchor="ma")
    p.silk((26, 24), "5.5", "white", anchor="ma", fnt=SILK16)
    p.silk((74, 24), "0" if stage else "?", "live" if stage else "dim", anchor="ma", fnt=SILK16)
    return p.img


@gag("v2", 9, post=0.7)
def more_than_ive_had(c, L):
    show(c, baths_score(1 if L.on("more") else 0), "ASMONGOLD", "STATS")
    if L.on("more"):
        pose(c, "asmon", arms="shrug", eyes="half", brows="neutral", mouth="closed")
    if L.on("year"):
        c.chat += [("GRUG:", "asmon_hi", "BRO"), ("ROACH77:", "asmon_hi", "SHOWER??"), ("BALD4:", "asmon_hi", ":skull:")]
    yield "front"
    if L.on("year"):
        alert(c, L.age("year") - 0.1, "ACHIEVEMENT", "0 BATHS ALL YEAR", "cup", 2.4)


# --- 10-11: electric ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def kaya(pose="sit", step=0, wide=False):
    """His dog, facing right (34 x 28), her feet on the bottom row."""
    f = Canvas(34, 28)
    b = 27
    if pose == "sit":
        f.line([(7, b - 3), (2, b - 6)], "dog", 2)                                          # the tail
        f.ell((5, b - 14, 20, b), "dog"); f.rect((14, b - 16, 20, b), "dog")                # haunch and chest
        f.rect((18, b - 9, 20, b), "dog_sh"); f.rect((18, b - 1, 22, b), "dog")             # a front leg
        hx, hy = 13, b - 27
    else:
        s = 1 if step % 2 else 0
        f.line([(6, b - 14), (2, b - 19)], "dog", 2)
        f.ell((4, b - 17, 25, b - 7), "dog")
        for x, d in ((7, s), (11, -s), (19, -s), (23, s)):
            f.rect((x + d, b - 8, x + d + 1, b), "dog" if x in (7, 19) else "dog_sh")
        hx, hy = 20, b - 27
    f.ell((hx, hy, hx + 11, hy + 11), "dog")                                                # the head
    f.poly([(hx + 1, hy), (hx + 5, hy - 1 if hy else 0), (hx + 4, hy + 6)], "dog_sh")         # an ear
    f.rect((hx + 8, hy + 5, hx + 13, hy + 9), "dog_dk"); f.px((hx + 13, hy + 5), "ink")      # the muzzle
    if wide:
        f.rect((hx + 5, hy + 2, hx + 7, hy + 4), "white"); f.px((hx + 6, hy + 3), "ink")
    else:
        f.px((hx + 6, hy + 3), "ink")
    f.rect((hx + 2, hy + 10, hx + 8, hy + 11), "live"); f.rect((hx + 4, hy + 12, hx + 6, hy + 14), "black")   # the collar
    return f.done()


@lru_cache(maxsize=None)
def electric_pic(stage):
    """Two things he owns that run on electricity."""
    p = Pic("hwall")
    p.rect((0, 40, PW, PH), "stone")
    p.put(porsche(), 28, 30)
    p.bolt(24, 5, 1, "yellow"); p.d.line([(27, 5), (24, 10), (26, 10), (25, 14)], fill=INK)
    p.silk((28, 44), "ELECTRIC", "ink", anchor="ma")
    if stage:
        p.put(kaya("sit"), 76, 26)
        p.bolt(72, 2, 1, "yellow"); p.d.line([(75, 2), (72, 7), (74, 7), (73, 11)], fill=INK)
        p.silk((76, 44), "ELECTRIC", "ink", anchor="ma")
    return p.img


@gag("v2", 10)
def electric(c, L):
    show(c, electric_pic(1 if L.on("pup") else 0), "HASANABI", "GARAGE")
    click(c, L, "pup")
    yield "front"


def bed_pic(k, thumb, zap, t):
    """Her bed, and what happens one step past it. k: how far off it she is; thumb: on the button; zap."""
    p = Pic("hwall")
    p.rect((0, 45, PW, PH), "wood"); p.line([(0, 45), (PW, 45)], "wood_sh")
    p.rbox((2, 37, 42, 48), "bed_st", "ink", 4); p.rbox((6, 35, 38, 43), "bed", "ink", 3)      # the bed
    x = 22 + int(38 * k)
    y = 43 if k < 0.35 else 46
    if zap:
        p.put(kaya("stand", 0, wide=True), x, y - 6 - int(2 * math.sin(t * 40)), "mb")
        for i in range(3):
            a = t * 30 + i * 2.1
            p.bolt(x - 8 + 9 * i + int(2 * math.sin(a)), y - 40 + int(3 * math.cos(a)), 1, "yellow")
        p.tag((x - 14, 2), "BZZT", "yellow", "ink")
    elif k <= 0:
        p.put(kaya("sit"), x, y, "mb")
    else:
        p.put(kaya("stand", int(t * 8)), x, y, "mb")
    p.rbox((79, 5, 95, 33), "black", "ink", 2)                                              # the remote
    p.ell((83, 9, 91, 17), "yellow" if zap else "live" if thumb else "red_sh")
    p.rect((83, 22, 91, 23), "grey_sh"); p.rect((83, 26, 91, 27), "grey_sh")
    ty = 12 if thumb else 20                                                                # and his thumb
    p.poly([(99, ty + 4), (88, ty + 2), (85, ty + 5), (88, ty + 9), (99, ty + 12)], "hskin")
    p.d.line([(99, ty + 4), (88, ty + 2), (85, ty + 5), (88, ty + 9), (99, ty + 12)], fill=INK)
    return p.img


@gag("v2", 11, post=0.9)
def light_her_up(c, L):
    t0, t1 = L.w("steps"), L.w("and")
    zap = L.on("light") and L.age("light") < 0.45
    back = L.on("light") and not zap                                                        # and she is back on it
    k = 0.0 if back else clamp((c.t - t0) / (t1 - t0), 0, 1)
    show(c, bed_pic(k, L.on("you") and not back, zap, c.t), "KAYA", "PUP CAM")
    click(c, L)
    if L.on("light"):
        pose(c, "asmon", arms="palm", eyes="half", brows="up", mouth="closed")
    yield "front"


# --- 12-13: the swivel --------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def chair(who, talk=False, back=False):
    """A gaming chair with its streamer in it, from the front (or the back): 30 x 42, the base on the bottom."""
    f = Canvas(30, 42)
    stripe = who
    f.rect((14, 33, 15, 38), "steel_sh")                                                    # the post, the base
    f.line([(5, 41), (14, 38), (24, 41)], "steel_sh"); f.rect((3, 40, 5, 41), "black"); f.rect((24, 40, 26, 41), "black")
    f.d.rounded_rectangle((3, 4, 26, 30), 5, fill=f.c("black"), outline=f.c("ink"))          # the back
    f.rect((6, 8, 8, 28), stripe); f.rect((21, 8, 23, 28), stripe)
    f.d.rounded_rectangle((1, 28, 28, 34), 2, fill=f.c("black"), outline=f.c("ink"))         # the seat
    if back:
        f.rect((11, 6, 18, 10), stripe)
        return f.done()
    body = "tank" if who == "hasan" else "tee_hi"
    f.poly([(7, 30), (9, 22), (20, 22), (22, 30)], body)                                    # him
    m = mug(who, "open", "neutral", "open" if talk else "closed", k=3)
    f.img.alpha_composite(m, (5, 3))
    return f.done()


@lru_cache(maxsize=None)
def chairs_pic(stage, talk):
    """Two men, two chairs. stage 1: what comes out; 2: the sum."""
    p = Pic("bg")
    p.put(chair("hasan", bool(stage) and talk), 24, 32); p.put(chair("asmon", bool(stage) and not talk), 76, 32)
    if stage >= 1:
        p.tag((11, 1), "BLAH", "hasan", "ink") if talk else p.tag((63, 1), "BLAH", "asmon", "ink")
    if stage >= 2:
        p.rect((44, 26, 56, 28), "gold"); p.rect((44, 32, 56, 34), "gold")
    return p.img


@gag("v2", 12)
def same_delusion(c, L):
    stage = 2 if L.on("same") else 1 if L.on("drivel") else 0
    show(c, chairs_pic(stage, int(c.t * 5) % 2 == 0), "BOTH OF US", "LIVE")
    click(c, L)
    if L.on("same"):
        pose(c, "asmon", arms="shrug", eyes="half", brows="up")
    yield "front"


def swivel_pic(a):
    """His revolution: a turn of the chair, counted."""
    p = Pic("bg")
    turns = a * 1.5
    ang = 2 * math.pi * (turns % 1.0)
    spr = chair("hasan", back=math.cos(ang) < 0)
    w = max(4, int(round(spr.width * abs(math.cos(ang)))))
    p.put(spr.resize((w, spr.height), Image.NEAREST), 50, 32)
    p.d.arc((26, 42, 74, 53), 200, 520, fill=col("gold"))                                   # round it goes
    p.poly([(26, 44), (30, 46), (25, 49)], "gold")
    p.header(f"REVOLUTIONS: {int(turns)}", "live", "white", h=9)
    return p.img


@gag("v2", 13)
def whole_revolution(c, L):
    if L.on("swivel"):
        show(c, swivel_pic(L.age("swivel")), "HASANABI", "LIVE")
    if L.on("revolution"):
        pose(c, "asmon", arms="cross" if L.age("revolution") > 0.5 else "point", eyes="half", brows="up")
    yield "front"
