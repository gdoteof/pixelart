"""Verse 3: Hasan again, now in the suit. Four bars of posters for his own good life, then back to the
exhibits."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403


# --- 0-3: the good life, as policy ---------------------------------------------------------------------

def poster(top, bottom, draw=None, strip="gold", ink="red_sh"):
    """A propaganda poster: red, a sunburst, and a slogan in two parts."""
    p = Pic("red")
    for i in range(0, 12, 2):
        a0, a1 = math.pi * i / 12, math.pi * (i + 1) / 12
        p.poly([(50, 46), (50 + 99 * math.cos(a0), 46 - 99 * math.sin(a0)),
                (50 + 99 * math.cos(a1), 46 - 99 * math.sin(a1))], "red_hi")
    if draw:
        draw(p)
    p.press((PW // 2, 3), top, "gold", anchor="ma", shadow="red_sh")
    p.rect((0, 43, PW, PH), strip); p.silk((PW // 2, 45), bottom, ink, anchor="ma")
    return p


def _villa(p):
    villa(p, 27, 13)


def _suit(p):
    """A Mao suit on a tailor's dummy, with the tape that measured it."""
    x = 38
    p.rect((49, 36, 50, 43), "wood_sh")
    body = [(x, 21), (x + 6, 15), (x + 18, 15), (x + 24, 21), (x + 23, 39), (x + 1, 39)]
    p.poly(body, "mao"); p.d.line(body + body[:1], fill=INK)
    p.rect((x + 9, 13, x + 15, 16), "mao_sh"); p.d.rectangle((x + 9, 13, x + 15, 16), outline=INK)   # the collar
    p.line([(x + 12, 17), (x + 12, 38)], "mao_sh")
    for y in (20, 25, 30, 35):
        p.px((x + 12, y), "gold")
    for bx, by in ((x + 3, 22), (x + 15, 22), (x + 3, 31), (x + 15, 31)):                          # four pockets
        p.rect((bx, by, bx + 6, by + 4), "mao_sh"); p.line([(bx, by), (bx + 6, by)], "mao_hi")
    for pts in ([(x + 8, 16), (x + 4, 28), (x + 5, 41)], [(x + 16, 16), (x + 20, 30), (x + 19, 41)]):   # the tape
        p.line(pts, "yellow", 2)
        for k in range(1, 6):
            p.px((pts[1][0], 16 + 4 * k), "ink")


def _porsche(p):
    p.put(porsche(), 50, 31)


def _leather(p):
    """A leather jacket."""
    x = 36
    for sx in (1, -1):                                                                            # the sleeves
        cx = x + 14
        p.poly([(cx - 14 * sx, 20), (cx - 20 * sx, 38), (cx - 15 * sx, 40), (cx - 10 * sx, 24)], "black")
    body = [(x, 20), (x + 7, 14), (x + 21, 14), (x + 28, 20), (x + 26, 41), (x + 2, 41)]
    p.poly(body, "black"); p.d.line(body + body[:1], fill=col("grey_sh"))
    p.poly([(x + 9, 14), (x + 14, 27), (x + 11, 31), (x + 6, 19)], "grey_sh")                       # the lapels
    p.poly([(x + 19, 14), (x + 14, 27), (x + 17, 31), (x + 22, 19)], "grey_sh")
    p.line([(x + 14, 27), (x + 14, 41)], "steel"); p.line([(x + 18, 33), (x + 23, 33)], "steel")    # zips
    p.line([(x + 3, 23), (x + 3, 37)], "grey"); p.px((x + 24, 24), "grey")


def _lounger(p):
    """A lounger by the pool, and something with an umbrella in it."""
    p.rect((0, 35, PW, 43), "sky"); p.line([(6, 38), (20, 38)], "sky_hi"); p.line([(64, 40), (84, 40)], "sky_hi")
    p.line([(26, 33), (50, 33)], "white", 3); p.line([(50, 33), (63, 20)], "white", 3)              # the lounger
    p.line([(30, 34), (30, 39)], "grey_hi"); p.line([(48, 34), (48, 39)], "grey_hi")
    p.poly([(72, 24), (82, 24), (77, 31)], "gold"); p.line([(77, 31), (77, 35)], "white")           # the drink
    p.line([(74, 35), (80, 35)], "white")
    p.line([(79, 24), (83, 15)], "white"); p.poly([(78, 17), (84, 12), (89, 18)], "pink")


@gag("v3", 0)
def for_the_masses(c, L):
    if L.on("Mao"):
        show(c, poster("MAO SUITS", "MADE TO MEASURE", _suit).img, "HASANABI", "AD")
        pose(c, "hasan", arms="chest", eyes="shut", brows="up", mouth="grin")                       # the suit, modelled
    else:
        show(c, poster("MANSION", "FOR THE MASSES", _villa).img, "HASANABI", "AD")
        pose(c, "hasan", arms="palm", eyes="open", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def porsche_poster(private):
    if not private:
        return poster("PORSCHE", "FOR THE PEOPLE", _porsche).img
    p = poster("PORSCHE", "PRIVATE PARKING", _porsche, "black", "white")
    p.rect((8, 28, 10, 43), "grey_hi")                                                              # the barrier
    for i in range(10):
        p.rect((10 + 8 * i, 26, 17 + 8 * i, 29), "live" if i % 2 == 0 else "white")
    p.d.rectangle((10, 25, 90, 30), outline=INK)
    return p.img


@gag("v3", 1)
def for_the_people(c, L):
    show(c, porsche_poster(L.on("parked")), "HASANABI", "AD")
    if L.on("private"):
        pose(c, "hasan", arms="hush", eyes="side", brows="up")
        c.chat += [("OATMILK:", "hasan_hi", "WAIT"), ("ZYNGOD:", "hasan_hi", "COMRADE??")]
    else:
        pose(c, "hasan", arms="palm", eyes="open", brows="up")
    yield "front"


@gag("v3", 2)
def for_the_lefties(c, L):
    if L.on("leisure"):
        show(c, poster("LEISURE", "LABOR'S TREASURE", _lounger).img, "HASANABI", "AD")
        pose(c, "hasan", arms="shrug", eyes="shut", brows="up", mouth="grin")
    else:
        show(c, poster("LEATHER", "FOR THE LEFTIES", _leather).img, "HASANABI", "AD")
    yield "front"


@lru_cache(maxsize=None)
def marx_pic(stage):
    """The book, and what it says on page one."""
    if stage == 0:
        p = Pic("red_sh")
        p.rbox((22, 3, 78, 51), "red", "ink", 2)
        p.d.rectangle((27, 7, 74, 47), outline=col("gold"))
        p.press((51, 13), "MARX", "gold", anchor="ma", shadow="red_sh")
        p.silk((51, 28), "THE", "gold", anchor="ma"); p.silk((51, 36), "BASICS", "gold", anchor="ma")
        p.rect((22, 4, 24, 50), "red_sh")
        return p.img
    p = Pic("paper")
    p.rect((0, 0, 4, PH), "red"); p.line([(5, 0), (5, PH)], "paper_sh")                              # the spine
    p.silk((PW - 4, 3), "PAGE 1", "grey_sh", anchor="ra")
    if stage == 1:
        p.lines((12, 14, 92, 46), 5, "paper_ln", 7)
    else:
        p.press((53, 16), "TREAT", "live", anchor="ma"); p.press((53, 28), "YOURSELF", "live", anchor="ma")
        p.heart(53, 43, "live")
    return p.img


@lru_cache(maxsize=None)
def red_book():
    f = Canvas(18, 24)
    f.d.rounded_rectangle((1, 1, 16, 22), 1, fill=f.c("red"), outline=f.c("ink"))
    f.rect((2, 2, 3, 21), "red_sh"); f.rect((6, 5, 13, 6), "gold"); f.rect((6, 9, 13, 9), "gold")
    return f.done()


@gag("v3", 3, post=0.8)
def page_one(c, L):
    stage = 2 if L.on("Treat") else 1 if L.on("page") else 0
    show(c, marx_pic(stage), "MARX", "P. 1" if stage else "BOOK")
    hold_up(c, "hasan", red_book(), 4)
    pose(c, "hasan", brows="up", eyes="shut" if stage == 2 else "open", mouth="grin" if stage == 2 else "closed")
    if L.on("Yourself"):
        c.chat += [("LATTE:", "hasan_hi", "PAGE ONE??"), ("MARXBRO:", "hasan_hi", "NOT IN MY COPY")]
    yield "front"


# --- 4-5: flagged ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def passport_pic(stage):
    """His travel record. stage 1: the Feds; 2: Britain; 3: the title it earns him."""
    p = Pic("cream")
    if stage >= 3:
        p.header("ENEMY OF WEALTH", "live", "white", h=9)
    else:
        p.header("PASSPORT", "night", "gold", h=9)
    p.rbox((3, 12, 35, 50), "paper_sh", "ink", 1)
    p.put(mug("hasan", "open", "up" if stage >= 3 else "neutral", "grin" if stage >= 3 else "closed"), 19, 31)
    for i, (name, word, colr) in enumerate((("USA", "FLAGGED", "blue"), ("UK", "BARRED", "live"))[:stage]):
        y = 14 + 19 * i
        p.d.rectangle((39, y, 96, y + 15), outline=col(colr)); p.d.rectangle((41, y + 2, 94, y + 13), outline=col(colr))
        p.silk((68, y + 7), word, colr, anchor="ma")
        p.tag((43, y - 4), name, colr, "white")
    return p.img


@gag("v3", 4)
def enemy_of_wealth(c, L):
    show(c, passport_pic(count(L, "Feds", "Britain", "enemy")), "HASANABI", "ID")
    if L.on("enemy"):
        pose(c, "hasan", arms="fist", brows="angry", eyes="open")
    else:
        pose(c, "hasan", arms="chest", brows="up", eyes="open")
    yield "front"


@lru_cache(maxsize=None)
def health_pic(n):
    """The notice on his door."""
    p = Pic("yellow")
    p.header("BOARD OF HEALTH", "black", "yellow", h=9)
    p.rbox((3, 12, 36, 49), "white", "ink", 1)
    p.silk((20, 14), "GRADE", "ink", anchor="ma")
    p.big((20, 23), "F", "live", "red_sh")
    for i, s in enumerate(("RATS", "ROACHES", "MOLD")[:n]):
        y = 14 + 12 * i
        p.silk((42, y + 2), s, "ink")
        p.rect((87, y, 95, y + 8), "white"); p.d.rectangle((87, y, 95, y + 8), outline=INK); p.tick(88, y + 1, "live")
    return p.img


@gag("v3", 5, post=0.8)
def board_of_health(c, L):
    if L.on("by"):                                        # up until the next bar has a picture of its own
        show(c, health_pic(min(3, 1 + int(L.age("by") / 0.16))), "HIS DOOR", "NOTICE")
        pose(c, "hasan", arms="window", eyes="up", brows="up")
    yield "front"
    if L.on("flagged") and not L.on("by"):
        label(c, *win(c, 54, 44), "FLAGGED", L.age("flagged"), bg="live", fg="white")


# --- 6-7: Turkey -----------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def pass_pic(stage):
    """A health tip, and the ticket it comes with."""
    p = Pic("sky")
    p.header("HEALTH TIP", "ok", "ink", h=9)
    p.rbox((3, 12, 96, 50), "white", "ink", 2)
    p.rect((4, 13, 95, 21), "blue"); p.silk((7, 15), "BOARDING PASS", "white")
    for y in range(23, 49, 3):
        p.px((72, y), "grey")
    p.silk((7, 25), "TO: TURKEY", "ink")
    plane = [(77, 31), (86, 31), (92, 28), (90, 33), (86, 34), (81, 38), (79, 38), (82, 34), (77, 33)]
    p.poly(plane, "blue"); p.poly([(80, 31), (78, 26), (80, 26), (84, 31)], "blue")
    for i, x in enumerate(range(76, 94, 2)):
        p.line([(x, 41), (x, 47)], "ink" if i % 3 else "grey")
    if stage >= 2:
        p.silk((7, 33), "FOR: HAIR", "live")
    if stage >= 3:
        p.silk((7, 41), "1 TRIP = ?", "ink")
    return p.img


@gag("v3", 6)
def fly_to_turkey(c, L):
    if L.on("fly"):                                       # the take sings "Board of Health tip" in one breath:
        show(c, pass_pic(count(L, "fly", "hair", "math")), "ASMONGOLD", "TRIP")       # the notice stays up till here
    if L.on("math"):
        pose(c, "hasan", arms="finger", eyes="open", brows="up")
    yield "front"


def _plugs(p, x):
    """The top of his head, with the new stock planted in rows."""
    p.ell((x + 4, 14, x + 24, 44), "askin"); p.d.arc((x + 4, 14, x + 24, 44), 180, 360, fill=INK)
    p.rect((x + 3, 27, x + 5, 36), "ahair"); p.rect((x + 23, 27, x + 25, 36), "ahair")
    for r in range(3):
        for q in range(5):
            p.px((x + 8 + 3 * q + (r % 2), 18 + 3 * r), "ahair_dk")


def _tan(p, x):
    """The sun, and what it does for him."""
    p.ell((x + 8, 14, x + 20, 26), "gold"); p.d.ellipse((x + 8, 14, x + 20, 26), outline=col("orange"))
    for i in range(8):
        a = i * math.pi / 4
        p.line([(x + 14 + 8 * math.cos(a), 20 + 8 * math.sin(a)), (x + 14 + 10 * math.cos(a), 20 + 10 * math.sin(a))], "gold")
    for i, colr in enumerate(("askin_hi", "askin", "hskin", "hskin_sh")):
        p.rect((x + 2 + 6 * i, 31, x + 7 + 6 * i, 36), colr)
    p.d.rectangle((x + 1, 30, x + 26, 37), outline=INK)


def _bath(p, x):
    tub(p, x + 2, 23, bg="panel")
    p.stink(x + 7, 19, 0, 3, 7, 5, "white")


@lru_cache(maxsize=None)
def trip_pic(n, first=False):
    """One trip, three things done."""
    p = Pic("panel")
    p.header("ONE TRIP", "blue", "white", h=9)
    for i, (draw, name) in enumerate(((_plugs, "PLUGS"), (_tan, "TAN"), (_bath, "BATH"))[:n]):
        x = 4 + 32 * i
        draw(p, x)
        p.rect((x, 38, x + 28, 47), "panel")
        p.silk((x + 14, 45), name, "text", anchor="ma")
    if first:
        p.tag((69, 10), "1ST!", "live", "white")
    return p.img


@gag("v3", 7, post=0.9)
def one_trip(c, L):
    show(c, trip_pic(count(L, "plugs", "tan", "bath") if L.on("plugs") else 0, L.on("bath") and L.age("bath") > 0.15),
         "ASMONGOLD", "DEAL")
    if L.on("first"):
        pose(c, "hasan", arms="window", eyes="up", brows="up")
    yield "front"


# --- 8-9: the landlord -----------------------------------------------------------------------------------

def roast_pic(t):
    """What he does to slumlords."""
    p = Pic("night")
    p.header("SLUMLORD ROAST", "orange", "ink", h=9)
    for i in range(10):                                                                             # the fire
        h = 6 + int(5 * (0.5 + 0.5 * math.sin(t * 11 + i * 1.7)))
        x = 16 + 7 * i
        p.poly([(x, 52), (x + 3, 50 - h - 4), (x + 7, 52)], "orange"); p.poly([(x + 2, 52), (x + 3, 51 - h), (x + 5, 52)], "yellow")
    p.rect((10, 20, 11, 50), "wood_hi"); p.rect((88, 20, 89, 50), "wood_hi"); p.line([(7, 25), (92, 25)], "steel")   # the spit
    p.ell((30, 15, 64, 36), "black"); p.d.ellipse((30, 15, 64, 36), outline=col("grey_sh"))          # him, on it
    p.rect((42, 21, 54, 30), "white"); p.line([(48, 21), (48, 30)], "live")
    p.ell((61, 17, 75, 33), "askin_sh"); p.d.ellipse((61, 17, 75, 33), outline=INK)
    p.rect((75, 19, 84, 31), "black"); p.rect((73, 15, 75, 35), "black")                             # the top hat
    p.d.ellipse((66, 21, 70, 25), outline=col("gold")); p.px((68, 28), "ink"); p.line([(64, 29), (70, 30)], "ink")
    p.line([(30, 28), (22, 34)], "black", 2); p.ell((16, 32, 26, 42), "gold_sh"); p.silk((21, 34), "$", "ink", anchor="ma")
    return p.img


@lru_cache(maxsize=None)
def shack_pic(stage):
    """His place: stage 1, and who owns it and who rents it."""
    p = Pic("night_hi")
    p.rect((0, 45, PW, PH), "grime")
    wall = [(5, 45), (8, 24), (40, 22), (42, 45)]
    p.poly(wall, "wood"); p.d.line(wall + wall[:1], fill=INK)
    roof = [(2, 26), (23, 10), (46, 24)]
    p.poly(roof, "wood_sh"); p.d.line(roof + roof[:1], fill=INK)
    p.rect((19, 32, 27, 45), "wood_sh"); p.px((25, 39), "gold")
    p.rect((10, 29, 16, 35), "gold_sh"); p.line([(10, 29), (16, 35)], "ink")
    p.line([(30, 28), (38, 30)], "wood_hi"); p.line([(31, 36), (39, 34)], "wood_hi"); p.rect((30, 12, 36, 15), "box")
    p.tag((50, 1), "FOR RENT", "white", "ink")
    if stage:
        p.silk((52, 14), "LANDLORD", "dim"); p.silk((52, 22), "= YOU", "gold")
        p.silk((52, 32), "TENANT", "dim"); p.silk((52, 40), "= YOU", "gold")
    return p.img


@gag("v3", 8)
def roast_slumlords(c, L):
    if L.on("^you"):
        show(c, shack_pic(1 if L.on("yourself") else 0), "ASMONGOLD", "HOME")
        pose(c, "hasan", arms="window", eyes="up", brows="up")
    else:
        show(c, roast_pic(c.t), "HASANABI", "LIVE")
        pose(c, "hasan", arms="chest", brows="angry", eyes="open")
    yield "front"


@lru_cache(maxsize=None)
def deposit_pic(denied):
    """A letter from his landlord."""
    p = Pic("paper")
    p.silk((6, 4), "FROM: ME", "ink"); p.silk((6, 12), "TO: ME", "ink")
    p.line([(5, 20), (94, 20)], "paper_ln")
    p.silk((6, 24), "RE: DEPOSIT", "ink")
    if denied:
        p.rect((12, 32, 87, 47), "live"); p.d.rectangle((12, 32, 87, 47), outline=INK)
        p.press((50, 36), "DENIED", "white", anchor="ma")
    else:
        p.lines((6, 34, 90, 46), 2, "paper_ln", 7)
    return p.img


@gag("v3", 9)
def deposit_back(c, L):
    show(c, deposit_pic(L.on("deposit")), "ASMONGOLD", "MAIL")
    if L.on("deposit"):
        pose(c, "hasan", arms="shrug", eyes="open", brows="up", mouth="grin")
    yield "front"


# --- 10-11: the raid -------------------------------------------------------------------------------------

CLASSES = ("orange", "pink", "sky", "yellow", "white", "blue_hi", "purple", "green", "brown_hi")


def raid_frame(n, title="gold"):
    """A raid frame: forty in it, or however many are left."""
    p = Pic("bg")
    p.header(f"RAID {n}/40", "panel_hi", title, h=9)
    for i in range(40):
        x, y = 2 + 12 * (i % 8), 11 + 8 * (i // 8)
        if i < n:
            p.rect((x, y, x + 10, y + 6), CLASSES[int(rnd("class", i) * len(CLASSES))])
            p.rect((x, y + 5, x + 10, y + 6), "ok")
            if i == 0:                                                                              # the leader's crown
                p.pxs([(x + 3, y + 1), (x + 5, y + 1), (x + 7, y + 1)], "ink"); p.rect((x + 3, y + 2, x + 7, y + 3), "ink")
        else:
            p.rect((x, y, x + 10, y + 6), "panel")
    return p


@lru_cache(maxsize=None)
def raid_pic(n):
    return raid_frame(n).img


@lru_cache(maxsize=None)
def bug_can():
    """The other Raid (30 x 38)."""
    f = Canvas(30, 38)
    f.rect((11, 0, 17, 3), "black"); f.rect((17, 1, 20, 2), "black")
    f.rect((8, 3, 21, 7), "grey_sh")
    f.d.rounded_rectangle((2, 7, 27, 37), 2, fill=f.c("red"), outline=f.c("ink"))
    f.rect((3, 13, 26, 23), "yellow"); f.rect((4, 9, 5, 35), "red_hi")
    silk(f.img, (15, 16), "RAID", "red_sh", anchor="ma")
    f.rect((9, 28, 20, 29), "red_sh"); f.rect((9, 32, 17, 32), "red_sh")
    return f.done()


def can_pic(stage, t):
    """What is left of the raid."""
    p = raid_frame(1 if stage else 0, "live")
    if stage >= 2:
        p.rect((18, 10, 82, 53), "bg")
        p.put(bug_can(), 36, 32)
        for i in range(14):                                                                         # the spray
            k = (t * 1.8 + rnd("mist", i)) % 1.0
            p.px((47 + int(26 * k), 15 + int((rnd("my", i) - 0.5) * 16 * k) + int(6 * k * k)), "white")
        p.put(roach_big(0).transpose(Image.FLIP_TOP_BOTTOM), 72, 42); p.cross(68, 30, "live", 3)
    return p.img


@gag("v3", 10)
def raid_leader(c, L):
    if L.on("ran"):
        a, dur = L.age("ran"), max(0.5, L.end - L.w("ran"))
        show(c, raid_pic(int(clamp(a / dur, 0, 1) * 40)), "ASMONGOLD", "2006")
    if L.on("forty"):
        pose(c, "hasan", arms="palm", eyes="open", brows="up")
    yield "front"


@gag("v3", 11)
def raid_in_a_can(c, L):
    stage = 2 if L.on("can") else 1 if L.on("Raid") else 0
    show(c, can_pic(stage, c.t), "ASMONGOLD", "2026")
    if L.on("comes"):
        hold_up(c, "hasan", bug_can(), 6)
        pose(c, "hasan", eyes="up", brows="up", mouth="grin")
    yield "front"
