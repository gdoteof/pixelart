"""Verse 3: Sam, on what he is and Felix was. The puppet and the feed that ranks it; the pixel artist's grave
and the Minecraft horse's; the Let's Play screaming and the quiet hundred billion; subscribers and
dependents; the account that is waiting for Felix's boy; and what the Lost Boys tell their chatbot now:
rashes, budgets, baby names, grudges, searches, messages to their mothers. Big bro, meet Big Brother."""
from gagkit import *  # noqa: F403


# --- small things ---------------------------------------------------------------------------------

def puppet(up):
    """Felix as a marionette, one of two dance steps. Returns the sprite and where its strings tie on."""
    f = Canvas(42, 58)
    f.rect((16, 28, 26, 42), "hood")
    arms = (((16, 30), (8, 21)), ((26, 30), (34, 37))) if up else (((16, 30), (8, 37)), ((26, 30), (34, 21)))
    legs = (((18, 42), (13, 53)), ((24, 42), (30, 49))) if up else (((18, 42), (12, 49)), ((24, 42), (29, 53)))
    for a, b in arms:
        f.line([a, b], "hood", w=3); f.rect((b[0] - 1, b[1] - 1, b[0] + 1, b[1] + 1), "fskin")
    for a, b in legs:
        f.line([a, b], "blue_sh", w=3); f.rect((b[0] - 2, b[1], b[0] + 2, b[1] + 1), "white")
    img = f.done()
    img.alpha_composite(scaled(mini("felix", "smile"), 2), (8, 2))
    return img, [arms[0][1], (21, 4), arms[1][1]]


@lru_cache(maxsize=None)
def tombstone(lines, w=44, h=46, color="stone"):
    f = Canvas(w + 2, h + 2)
    f.d.rounded_rectangle((1, 1, w, h + 8), 10, fill=f.c(color))
    f.d.rectangle((0, h + 1, w + 2, h + 10), fill=(0, 0, 0, 0))
    f.d.arc((3, 3, w - 2, 30), 180, 270, fill=f.c("white"))
    f.line([(w - 2, 12), (w - 2, h)], "stone_sh")
    for i, s in enumerate(lines):
        f.silk((1 + w // 2, 10 + 9 * i), s, "ink", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def block_horse(ghost=False):
    """A horse made of blocks, facing right."""
    f = Canvas(36, 30)
    body, dark, mane = ("white", "sky_hi", "white") if ghost else ("brown", "brown_sh", "black")
    f.rect((4, 10, 24, 19), body)                                      # the body
    f.rect((22, 3, 27, 14), body)                                      # the neck
    f.rect((24, 1, 33, 8), body)                                       # the head
    f.rect((30, 6, 33, 8), dark)
    f.rect((21, 2, 23, 12), mane)
    f.rect((1, 10, 3, 18), mane)                                       # the tail
    for x in (5, 9, 18, 22):
        f.rect((x, 20, x + 2, 28), dark if x in (9, 18) else body)
    f.px((29, 4), "ink")
    return f.done()


@lru_cache(maxsize=None)
def cursor():
    f = Canvas(11, 15)
    f.poly([(1, 1), (1, 11), (4, 8), (6, 13), (8, 12), (6, 7), (9, 7)], "white")
    return f.done()


@lru_cache(maxsize=None)
def fist():
    """A bro fist, knuckles first."""
    f = Canvas(34, 30)
    f.d.rounded_rectangle((3, 4, 30, 26), 5, fill=f.c("fskin"))
    for x in (9, 16, 23):
        f.line([(x, 5), (x, 14)], "fskin_sh")
    f.line([(4, 15), (29, 15)], "fskin_sh")
    f.d.rounded_rectangle((1, 14, 12, 22), 3, fill=f.c("fskin"))        # the thumb
    f.line([(4, 25), (29, 25)], "fskin_dk")
    return f.done()


# --- the pictures -----------------------------------------------------------------------------------

def marionette(c, L):
    """He dances for the thumbnail; the strings go up to someone else's hand."""
    p = Pic("night")
    p.box((6, 20, 93, 92), "red_sh", "red")                            # a thumbnail's frame
    p.rect((9, 23, 90, 89), "night_hi")
    spr, ties = puppet(c.beat_i % 2 == 0)
    x0, y0 = 29, 30 + (1 if c.ph < 0.3 else 0)
    bar_y = 9 + (1 if c.ph < 0.3 else 0)
    for tx_, ty_ in ties:                                              # the strings
        p.line([(x0 + tx_, y0 + ty_), (26 + (tx_ - 8) * 48 // 26, bar_y + 3)], "cream")
    p.img.alpha_composite(spr, (x0, y0))
    a = L.age("dictate")
    p.rect((22, bar_y + 1, 78, bar_y + 3), "wood")                      # the crossbar
    if a >= 0:                                                         # and the hand on it
        p.rect((42, bar_y - 9, 58, bar_y - 2), "sweater"); p.rect((44, bar_y - 3, 56, bar_y + 4), "sskin")
        p.line([(47, bar_y + 4), (47, bar_y + 1)], "sskin_sh"); p.line([(51, bar_y + 4), (51, bar_y + 1)], "sskin_sh")
    p.poly([(80, 82), (80, 88), (86, 85)], "white")                    # the play mark
    return p


def feed(L):
    """A feed, and what it does with him."""
    p = Pic("white")
    p.header("RECOMMENDED", "red", "white")
    a = L.age("I'm")
    k = ease_in_out(k_in(a, 0.45)) if a >= 0 else 0.0
    cards = (("PEWDIEPIE", "felix"), ("CAT FALLS", "orange"), ("A.I. NEWS", "sam"), ("10 HOUR LOOP", "purple"))
    for i in (1, 2, 3, 0):
        title, color = cards[i]
        y = int(round(14 + 60 * k)) if i == 0 else int(round(14 + 20 * i - 20 * k))
        mine = i == 0
        down = mine and k >= 1
        p.rect((3, y, 96, y + 17), "paper_sh" if down else "paper")
        p.box((5, y + 2, 27, y + 15), "grey" if down else color)
        if mine:
            p.put(mini("felix", "sad" if down else "smile"), 16, y + 9)
        else:
            p.poly([(13, y + 5), (13, y + 12), (20, y + 8)], "white")
        p.silk((31, y + 3), title, "grey" if down else "ink")
        p.silk((31, y + 10), "HIDDEN" if down else ("#1" if mine and k == 0 else "FOR YOU"), "live" if mine else "grey")
        if mine and 0 < k < 1:
            p.put(cursor(), 88, y + 12)
    return p


def pixel_grave(L):
    p = Pic("night")
    p.grad((0, 0, PW, 70), "night", "purple_sh")
    p.ell((66, 6, 84, 24), "cream")                                    # the moon
    p.rect((0, 70, PW, PH), "grass_sh")
    for x in (8, 22, 80, 92):
        p.line([(x, 70), (x, 66)], "grass")
    p.put(tombstone(("R.I.P.", "THE", "PIXEL", "ARTIST")), 40, 72, "mb")
    p.line([(70, 72), (78, 50)], "steel", w=2); p.rect((77, 46, 80, 50), "red")     # the stylus, left behind
    for i, color in enumerate(("red", "yellow", "pink")):              # pixel flowers
        x = 62 + 9 * i
        p.rect((x, 76, x + 2, 78), color); p.line([(x + 1, 79), (x + 1, 84)], "green")
    return p


def horse_funeral(L):
    """A funeral in a world made of blocks."""
    p = Pic("sky")
    p.grad((0, 0, PW, 60), "sky", "sky_hi")
    for x in range(0, PW, 10):                                         # grass blocks
        p.rect((x, 60, x + 9, 64), "grass"); p.rect((x, 65, x + 9, PH), "brown")
        p.line([(x, 60), (x, PH)], "brown_sh")
    p.line([(0, 80), (PW, 80)], "brown_sh")
    p.rect((66, 20, 86, 40), "green_sh"); p.rect((74, 40, 78, 60), "wood_sh")       # a tree, squarely
    p.rect((30, 54, 60, 60), "brown_sh")                                # the mound
    p.rect((12, 34, 28, 46), "wood"); p.d.rectangle((12, 34, 28, 46), outline=p.c("ink"))  # the sign
    p.rect((19, 46, 21, 60), "wood_sh")
    p.silk((20, 37), "RIP", "ink", anchor="ma")
    p.rect((62, 55, 64, 60), "green"); p.rect((61, 52, 65, 55), "red")              # a poppy
    a = L.age("horse")
    if L.on("Minecraft"):
        p.tag((50, 84), "JOERGEN, 2019", "ink", "white", "ma")
    if a >= 0:                                                         # the dear departed
        rise = int(min(14, a * 20))
        g = block_horse(True)
        p.put(g, 46, 40 - rise + int(2 * math.sin(L.t * 4)))
        p.d.ellipse((50, 20 - rise, 62, 24 - rise), outline=p.c("gold"))
    return p


def lets_play(L):
    """An old Let's Play: a dark corridor, a facecam, the meter in the red."""
    p = Pic("black")
    p.poly([(20, 14), (80, 14), (64, 48), (36, 48)], "night")           # the corridor
    p.poly([(0, 0), (20, 14), (36, 48), (0, 70)], "night_hi"); p.poly([(PW, 0), (80, 14), (64, 48), (PW, 70)], "night_hi")
    p.rect((44, 26, 56, 48), "black"); p.pxs([(47, 34), (52, 34)], "red")  # a door, and what's behind it
    a = L.age("screamed")
    loud = a >= 0
    p.box((3, 56, 37, 92), "felix_sh", "white")                        # the facecam
    p.put(scaled(mini("felix", "yell" if loud else "smile"), 2), 20, 75)
    for i in range(8):                                                 # the meter
        lit = loud and (i < 6 or int(L.t * 12) % 2)
        color = ("green", "green", "green", "green", "yellow", "yellow", "red", "red")[i] if lit else "grey_sh"
        p.rect((90, 86 - 9 * i, 96, 92 - 9 * i), color)
    if loud:
        n = min(9, 2 + int(a * 14))
        p.press((42, 62 + int(2 * math.sin(L.t * 30))), "A" * min(6, n), "yellow", shadow="red")
        p.press((42, 73 + int(2 * math.sin(L.t * 30 + 1))), "A" * max(0, min(6, n - 3)) + ("!" if n > 8 else ""),
                "orange", shadow="red")
    if L.on("grown"):
        p.tag((3, 46), "AGE: 23", "white", "ink")
    p.tag((3, 3), "LET'S PLAY", "live", "white")
    return p


def hundred_billion(L):
    p = Pic("white")
    p.rect((0, 0, PW, 4), "sam")
    a, a_v = L.age("hundred"), L.age("never")
    p.silk((50, 10), "RAISED", "grey", anchor="ma")
    if a >= 0:
        n = min(100, int(a * 400))
        p.press((50, 20), f"${n}", "sam_sh", anchor="ma", fnt=PRESS16)
        if L.on("billion"):
            p.press((50, 40 + (pop_dy(L.age("billion"), 0.12, 5) or 0)), "BILLION", "ink", anchor="ma")
    p.line([(8, 56), (92, 56)], "paper_ln")
    if a_v >= 0:                                                       # the other dial
        p.silk((8, 62), "VOLUME", "grey")
        p.rbox((8, 74, 92, 80), "paper_sh", "grey", 3)
        k = 1 - ease_out(k_in(a_v, 0.5))
        x = int(12 + k * 60)
        p.rect((9, 75, x, 79), "sam")
        p.ell((x - 4, 71, x + 4, 83), "white"); p.d.ellipse((x - 4, 71, x + 4, 83), outline=p.c("ink"))
        p.silk((92, 62), str(1 + int(k * 9)), "ink", anchor="ra")
    return p


def dependents(L):
    p = Pic("panel")
    p.line([(50, 6), (50, 90)], "line")
    a1, a2 = L.age("subscribers"), L.age("dependents")
    if a1 >= 0:
        dy = pop_dy(a1, 0.12, 6) or 0
        p.poly([(18, 30 + dy), (20, 18 + dy), (30, 18 + dy), (32, 30 + dy)], "felix")   # a bell
        p.rect((16, 30 + dy, 34, 32 + dy), "felix"); p.ell((23, 32 + dy, 27, 36 + dy), "felix_hi")
        p.silk((25, 44), "SUB-", "felix_hi", anchor="ma"); p.silk((25, 51), "SCRIBERS", "felix_hi", anchor="ma")
        p.silk((25, 64), "CAN", "dim", anchor="ma"); p.silk((25, 71), "LEAVE", "text", anchor="ma")
    if a2 >= 0:
        dy = pop_dy(a2, 0.12, 6) or 0
        for i in range(3):                                             # a chain
            p.d.ellipse((64 + 7 * i, 20 + dy, 74 + 7 * i, 32 + dy), outline=p.c("sam_hi"), width=2)
        p.silk((75, 44), "DEPEN-", "sam_hi", anchor="ma"); p.silk((75, 51), "DENTS", "sam_hi", anchor="ma")
        p.silk((75, 64), "CAN'T", "text", anchor="ma")
    return p


def account(L):
    """An account, waiting."""
    p = Pic("white")
    p.header("CREATE ACCOUNT", "sam_sh", "white")
    p.silk((8, 18), "NAME", "grey")
    p.box((8, 26, 91, 38), "paper", "grey")
    a = L.age("log")
    if L.on("boy"):
        p.silk((11, 30), fx.typed("PEWDIEPIE JR.", L.age("boy"), 26), "ink")
    p.silk((8, 44), "STATUS", "grey")
    if a >= 0:
        p.tag((8, 52), "PENDING", "warn", "ink")
    a_p = L.age("patient")
    if L.on("day"):                                                    # an hourglass
        x, y = 74, 66
        p.rect((x - 9, y - 14, x + 9, y - 12), "wood"); p.rect((x - 9, y + 12, x + 9, y + 14), "wood")
        p.poly([(x - 7, y - 12), (x + 7, y - 12), (x, y)], "sky_hi"); p.poly([(x - 7, y + 12), (x + 7, y + 12), (x, y)], "sky_hi")
        p.poly([(x - 4, y - 8), (x + 4, y - 8), (x, y - 1)], "gold")
        p.poly([(x - 6, y + 12), (x + 6, y + 12), (x, y + 8)], "gold")
        if int(L.t * 8) % 2:
            p.px((x, y + 3), "gold")
        p.d.polygon([(x - 7, y - 12), (x + 7, y - 12), (x, y), (x + 7, y + 12), (x - 7, y + 12), (x, y)], outline=p.c("ink"))
    if a_p >= 0:
        p.silk((8, 70), "NO RUSH.", "sam_sh")
        p.silk((8, 78), "I CAN WAIT.", "sam_sh")
    return p


def therapy(L):
    """The Lost Boys, grown up, on the couch."""
    p = Pic("cream")
    p.rect((0, 70, PW, PH), "wood")
    p.box((62, 8, 90, 30), "white", "wood"); p.line([(66, 22), (72, 14), (78, 20), (86, 12)], "sam")   # a certificate
    p.d.rounded_rectangle((4, 54, 66, 72), 4, fill=p.c("green_sh"), outline=p.c("ink"))      # the couch
    p.d.rounded_rectangle((2, 44, 18, 66), 4, fill=p.c("green_sh"), outline=p.c("ink"))
    p.rect((6, 72, 9, 78), "wood_sh"); p.rect((59, 72, 62, 78), "wood_sh")
    if L.on("grew"):                                                   # one of them, grown, still in the cap
        p.rect((24, 48, 52, 56), "blue"); p.rect((50, 50, 64, 55), "grey_sh")
        p.ell((10, 40, 26, 56), "fskin_sh"); p.rect((12, 50, 24, 55), "brown")      # a beard now
        p.poly([(9, 44), (14, 34), (26, 40)], "pan"); p.line([(14, 36), (9, 31)], "red")
        p.px((16, 46), "ink"); p.px((21, 46), "ink")
    a = L.age("patients")
    p.d.rounded_rectangle((70, 44, 96, 72), 4, fill=p.c("brown"), outline=p.c("ink"))        # the other chair
    p.orb(83, 50, 9, "happy" if a < 0 else "open", 0)
    p.d.ellipse((76, 45, 82, 51), outline=p.c("ink")); p.d.ellipse((84, 45, 90, 51), outline=p.c("ink"))  # glasses
    p.line([(82, 48), (84, 48)], "ink")
    p.box((74, 62, 86, 74), "paper", "ink"); p.line([(76, 66), (84, 66)], "paper_ln"); p.line([(76, 69), (82, 69)], "paper_ln")
    if a >= 0:
        p.tag((50, 84), "SESSION 412", "ink", "white", "ma")
    return p


def rashes_budgets(L):
    p = Pic("panel")
    a_r, a_b = L.age("rashes"), L.age("budgets")
    if L.on("rate"):
        p.box((4, 4, 95, 44), "paper", "line")
        p.d.rounded_rectangle((8, 14, 52, 30), 6, fill=p.c("fskin"), outline=p.c("ink"))     # an arm, photographed
        for x, y in ((18, 19), (24, 24), (31, 18), (36, 23), (43, 20), (28, 21)):
            p.rect((x, y, x + 1, y + 1), "red")
        p.silk((8, 35), "IMG_0412.JPG", "grey")
        if a_r >= 0:
            p.silk((74, 12), "RASH:", "ink", anchor="ma")
            p.press((75, 21 + (pop_dy(a_r, 0.12, 5) or 0)), "7/10", "red", anchor="ma")
    if L.on("balance"):
        p.box((4, 50, 95, 92), "white", "line")
        for i, (name, n) in enumerate((("RENT", "900"), ("FOOD", "300"), ("SKINS", "0"))):
            y = 54 + 9 * i
            p.silk((8, y), name, "ink"); p.silk((60, y), n, "ink", anchor="ra")
            if i == 2:
                p.line([(7, y + 2), (62, y + 2)], "red")
        p.line([(6, 81), (62, 81)], "grey")
        if a_b >= 0:
            p.silk((8, 84), "BALANCED", "green_sh")
            p.tick(80, 62, "green"); p.tick(80, 63, "green")
    return p


def babies_grudges(L):
    p = Pic("panel")
    a_b, a_g = L.age("babies"), L.age("grudges")
    if L.on("name"):
        p.box((4, 4, 95, 46), "paper", "line")
        p.silk((50, 8), "BABY NAMES", "pink", anchor="ma")
        for i, name in enumerate(("1. LIAM", "2. NOAH", "3. SAM")):
            y = 17 + 9 * i
            best = i == 2 and a_b >= 0
            if best:
                p.rect((8, y - 2, 90, y + 6), "sam_hi")
                p.heart(78, y - 1, "red")
            p.silk((12, y), name, "ink")
    if L.on("bury"):
        p.rect((4, 52, 95, 92), "night"); p.rect((4, 80, 95, 92), "grass_sh")
        p.put(tombstone(("HERE LIES", "A GRUDGE"), 52, 24), 40, 82, "mb")
        if a_g >= 0:
            p.line([(78, 84), (86, 60)], "wood", w=2); p.poly([(83, 56), (90, 58), (88, 66), (82, 62)], "steel")   # the shovel
    return p


def searches_mothers(L):
    p = Pic("panel")
    a_s, a_m = L.age("searches"), L.age("mothers")
    if L.on("see"):
        p.box((4, 4, 95, 48), "white", "line")
        p.silk((8, 8), "HISTORY", "grey")
        blink = int(L.t * 3) % 5 == 0
        p.ell((76, 6, 92, 16), "white"); p.d.ellipse((76, 6, 92, 16), outline=p.c("ink"))          # it watches
        if blink:
            p.rect((77, 10, 91, 12), "sskin")
        else:
            p.ell((81, 8, 87, 14), "sam"); p.rect((83, 10, 85, 12), "ink")
        rows = ("AM I NORMAL", "RASH PHOTO", "OLD PEWDIEPIE") if a_s >= 0 else ()
        for i, s in enumerate(rows):
            y = 20 + 9 * i
            p.d.ellipse((8, y - 1, 13, y + 4), outline=p.c("grey")); p.line([(13, y + 4), (15, y + 6)], "grey")
            p.silk((19, y), s, "ink")
    if L.on("message"):
        p.d.rounded_rectangle((6, 54, 95, 84), 6, fill=p.c("sam_sh"), outline=p.c("ink"))
        p.silk((51, 59), "HAPPY BIRTHDAY", "white", anchor="ma")
        p.silk((45, 67), "MOM!", "white", anchor="ma"); p.heart(61, 67, "red_hi")
        if a_m >= 0:
            p.silk((51, 76), "(BY CHATGPT)", "sam_hi", anchor="ma")
            p.silk((95, 87), "TO: MOM", "dim", anchor="ra")
    return p


def big_bro(L):
    p = Pic("felix_sh")
    for i in range(0, PW + PH, 14):
        p.poly([(i, 0), (i + 7, 0), (i + 7 - PH, PH), (i - PH, PH)], "felix")
    p.put(scaled(fist(), 2), 50, 42 + (1 if int(L.t * 6) % 2 else 0))
    p.press((51, 78), "BIG BRO", "white", anchor="ma", shadow="ink")
    return p


def big_brother(a):
    """The poster."""
    p = Pic("black")
    p.grad((0, 0, PW, PH), "red_sh", "black")
    dy = pop_dy(a, 0.14, 10) or 0
    p.poly([(4, 18 + dy), (12, 4 + dy), (26, 8 + dy), (38, 2 + dy), (52, 9 + dy), (66, 3 + dy), (82, 8 + dy), (96, 20 + dy),
            (90, 24 + dy), (72, 19 + dy), (54, 25 + dy), (34, 19 + dy), (16, 25 + dy)], "shair")               # the fringe
    for x in (27, 73):                                                 # the eyes
        p.ell((x - 17, 28 + dy, x + 17, 54 + dy), "eye_w"); p.d.ellipse((x - 17, 28 + dy, x + 17, 54 + dy), outline=p.c("ink"))
        p.ell((x - 8, 33 + dy, x + 8, 49 + dy), "eye_g"); p.ell((x - 4, 37 + dy, x + 4, 45 + dy), "eye")
        p.rect((x - 6, 35 + dy, x - 4, 37 + dy), "white")
        p.line([(x - 18, 22 + dy), (x + 16, 21 + dy)], "shair", w=3)    # the brow
    p.press((51, 64), "BIG BROTHER", "white", anchor="ma", shadow="ink")
    p.silk((50, 77), "IS HELPING YOU", "sam_hi", anchor="ma")
    p.silk((50, 86), "(ALL OF YOU)", "dim", anchor="ma")
    return p


# --- the gags ---------------------------------------------------------------------------------------

@gag("v3", 0)
def dance_for_the_thumbnail(c, L):
    show(c, marionette(c, L), "THE THUMBNAIL", L.age())
    yield "front"


@gag("v3", 1)
def the_algorithm(c, L):
    show(c, feed(L), "THE FEED", L.age())
    yield "front"


@gag("v3", 2)
def killed_the_pixel_artist(c, L):
    show(c, pixel_grave(L), "THIS VIDEO: A.I.", L.age())
    if L.on("feel"):
        pose(c, "sam", arms="shrug", mouth="smile", brows="up")
    yield "front"


@gag("v3", 3)
def minecraft_horse(c, L):
    show(c, horse_funeral(L), "IN MEMORIAM", L.age())
    if L.on("wept"):
        pose(c, "felix", arms="wipe", tears=True, brows="worried", mouth="frown", eyes="shut", react=False)
    yield "front"


@gag("v3", 4)
def screamed_through(c, L):
    show(c, lets_play(L), "2012", L.age())
    yield "front"


@gag("v3", 5)
def never_raise_my_voice(c, L):
    show(c, hundred_billion(L), "FUNDING", L.age())
    if L.on("never"):
        pose(c, "sam", arms="hush", eyes="half", brows="up")
    yield "front"


@gag("v3", 6)
def raising_dependents(c, L):
    show(c, dependents(L), "RETENTION", L.age())
    yield "front"


@gag("v3", 7)
def your_own_boy(c, L):
    show(c, account(L), "FUTURE USERS", L.age())
    if L.on("patient"):
        pose(c, "sam", arms="clasp", mouth="smile", eyes="half")
        pose(c, "felix", brows="angry", eyes="open", mouth="frown")
    yield "front"


@gag("v3", 8)
def my_patients(c, L):
    show(c, therapy(L), "OFFICE HOURS", L.age())
    yield "front"


@gag("v3", 9)
def rashes_and_budgets(c, L):
    show(c, rashes_budgets(L), "TODAY'S CHATS", L.age())
    yield "front"


@gag("v3", 10)
def babies_and_grudges(c, L):
    show(c, babies_grudges(L), "TODAY'S CHATS", L.age())
    yield "front"


@gag("v3", 11)
def searches_and_mothers(c, L):
    show(c, searches_mothers(L), "TODAY'S CHATS", L.age())
    yield "front"


@gag("v3", 12, post=1.0)
def big_bro_big_brother(c, L):
    a = L.age("big", 1)
    show(c, searches_mothers(Sung(c.t)), "TODAY'S CHATS", 1.0)         # the last chat stays up until the fist
    show(c, big_bro(L), "THEN", L.age("big"))
    if a >= 0:
        show(c, big_brother(a), "NOW", a, 0.08)
        jolt(c, a, 3, 0.25)
    if L.on("Felix") and a < 0:
        pose(c, "sam", arms="point")
    yield "front"
