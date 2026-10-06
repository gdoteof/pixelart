"""Verse 2: Felix, cheerfully, on Sam. The forty thieves and the cave that won't open; Meme Review and the
guest who only visits Sam with papers; the two polo shirts of 2008; the adult mode that was promised and
shelved; the monster he warns about and plugs in; the hypercar and the begging; what its badge means in
Swedish; the hostage tape; and the thumbnail with no video behind it. Three of them he swipes away: "Next!"."""
from gagkit import *  # noqa: F403


# --- small things ---------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def thief():
    f = Canvas(11, 11)
    f.ell((1, 2, 9, 9), "sskin")
    f.rect((2, 0, 8, 1), "sam_sh"); f.rect((1, 1, 9, 3), "sam_sh")        # a beanie in company colours
    f.rect((1, 5, 9, 6), "black")                                        # the mask
    f.px((3, 5), "white"); f.px((7, 5), "white")
    return f.done()


@lru_cache(maxsize=None)
def sack(label="DATA"):
    f = Canvas(31, 25)
    f.poly([(11, 1), (19, 1), (17, 6), (13, 6)], "brown_hi")           # the neck
    f.ell((2, 5, 28, 23), "brown_hi")
    f.line([(12, 6), (18, 6)], "brown_sh")
    f.silk((15, 12), label, "brown_sh", anchor="ma")
    return f.done()


@lru_cache(maxsize=None)
def young_sam():
    """Sam on a keynote stage in 2008: a pink polo over a green one, both collars up."""
    f = Canvas(36, 74)
    f.rect((12, 50, 17, 68), "blue_sh"); f.rect((19, 50, 24, 68), "blue_sh")        # jeans
    f.rect((11, 68, 17, 70), "white"); f.rect((19, 68, 25, 70), "white")
    f.rect((7, 33, 10, 47), "sskin"); f.rect((26, 33, 29, 47), "sskin")             # arms
    f.rect((7, 30, 11, 37), "polo1"); f.rect((25, 30, 29, 37), "polo1")
    f.rect((11, 30, 25, 50), "polo1")
    f.rect((11, 49, 25, 51), "polo2")                                               # the one underneath, at the hem
    f.poly([(16, 30), (20, 30), (18, 38)], "polo2")                                 # and at the neck
    f.line([(18, 38), (18, 44)], "polo1_sh")
    body = f.done()
    h = scaled(mini("sam"), 2)
    body.alpha_composite(h, (5, 2))
    g = Canvas(36, 74)                                                              # both collars, up round the jaw
    g.poly([(10, 31), (10, 21), (14, 26), (16, 31)], "polo1"); g.poly([(26, 31), (26, 21), (22, 26), (20, 31)], "polo1")
    g.poly([(14, 31), (13, 24), (16, 27), (17, 31)], "polo2"); g.poly([(22, 31), (23, 24), (20, 27), (19, 31)], "polo2")
    body.alpha_composite(g.done())
    return body


@lru_cache(maxsize=None)
def hypercar():
    """A low Swedish hypercar, side on, facing right."""
    f = Canvas(68, 24)
    f.poly([(2, 9), (9, 9), (9, 11), (2, 11)], "steel_sh")                           # the wing
    f.poly([(2, 16), (5, 11), (22, 9), (33, 4), (46, 4), (56, 9), (64, 12), (65, 17), (2, 17)], "steel")
    f.poly([(34, 5), (45, 5), (52, 9), (27, 9)], "night")                            # the canopy
    f.line([(36, 6), (40, 6)], "night_hi")
    f.line([(6, 13), (62, 13)], "steel_hi"); f.rect((2, 16, 65, 18), "steel_sh")
    f.line([(24, 10), (24, 16)], "steel_sh"); f.line([(52, 10), (52, 16)], "steel_sh")
    for x in (10, 47):
        f.ell((x, 12, x + 10, 22), "black"); f.ell((x + 3, 15, x + 7, 19), "grey_hi")
    f.rect((62, 13, 64, 14), "yellow"); f.rect((2, 12, 3, 14), "red")
    f.rect((58, 11, 60, 12), "orange")                                               # the badge on the bonnet
    return f.done()


@lru_cache(maxsize=None)
def badge(n=1):
    """The badge on the bonnet: a shield."""
    f = Canvas(13 * n + 2, 15 * n + 2)
    k = n
    f.poly([(1, 1), (12 * k, 1), (12 * k, 8 * k), (6 * k, 14 * k), (1, 8 * k)], "orange")
    f.poly([(3 * k, 3 * k), (9 * k, 3 * k), (9 * k, 7 * k), (6 * k, 10 * k), (3 * k, 7 * k)], "red")
    f.line([(2 * k, 2 * k), (10 * k, 2 * k)], "gold_hi")
    f.rect((5 * k, 5 * k, 7 * k, 6 * k), "gold")
    return f.done()


@lru_cache(maxsize=None)
def newspaper():
    f = Canvas(38, 30)
    f.rect((1, 1, 36, 28), "paper")
    f.silk((18, 3), "TODAY", "ink", anchor="ma")
    f.line([(3, 10), (34, 10)], "ink")
    f.rect((4, 13, 16, 24), "grey")
    for i in range(4):
        f.line([(19, 13 + 3 * i), (33, 13 + 3 * i)], "paper_ln")
    return f.done()


# --- the pictures -----------------------------------------------------------------------------------

def thieves(L):
    """Ali Baba, and who the forty thieves are."""
    p = Pic("night")
    p.grad((0, 0, PW, PH), "night_hi", "night")
    p.header("ALI BABA AND THE", "red_sh", "gold_hi")
    n = int(40 * k_in(L.age("Then"), 0.55))
    if not L.on("Then"):                                               # Ali Baba himself: Felix, in a fez
        h = scaled(mini("felix"), 3)
        p.put(h, 50, 46)
        p.poly([(40, 26), (44, 14), (58, 14), (62, 26)], "red"); p.d.polygon([(40, 26), (44, 14), (58, 14), (62, 26)],
                                                                             outline=p.c("ink"))
        p.line([(51, 14), (56, 10), (58, 18)], "gold")
        p.tag((50, 74), "ALI BABA (ME)", "gold", "ink", "ma")
    for i in range(n):
        p.put(thief(), 8 + 12 * (i % 8), 20 + 11 * (i // 8))
    a = L.age("forty")
    if a >= 0:
        p.rect((0, 71, PW, PH), "black")
        p.press((50, 75 + (pop_dy(a, 0.12, 6) or 0)), "40 THIEVES", "gold", anchor="ma", shadow="red_sh")
        p.silk((50, 87), "(THAT'S YOU, SAM)", "sam_hi", anchor="ma")
    return p


def cave(L):
    """The cave that is called Open and isn't."""
    p = Pic("night")
    p.poly([(0, PH), (0, 34), (12, 16), (36, 6), (68, 8), (90, 22), (PW, 40), (PW, PH)], "stone_sh")
    p.poly([(12, 16), (36, 6), (40, 12), (20, 22)], "stone"); p.poly([(68, 8), (90, 22), (80, 24), (62, 14)], "stone")
    p.rect((0, 84, PW, PH), "brown_sh")
    a_o, a_f = L.age("Open"), L.age("Felony")
    k = ease_out(k_in(a_o, 0.5)) if a_f < 0 else 1 - ease_in(k_in(a_f, 0.12))
    p.d.pieslice((30, 30, 70, 110), 180, 360, fill=p.c("black"))        # the mouth of the cave
    p.rect((30, 70, 70, 84), "black")
    if k > 0.05:                                                       # what's inside
        p.d.pieslice((34, 36, 66, 104), 180, 360, fill=p.c("brown_sh"))
        p.rect((34, 70, 66, 84), "brown_sh")
        for i in range(7):
            p.put(P.coin(3), 38 + 4 * i, 80 - (i % 3) * 4)
        p.tag((50, 87), "THE WEIGHTS", "gold", "ink", "ma")
    x = 50 + int(k * 40)                                               # the stone, rolled aside
    p.ell((x - 23, 34, x + 23, 86), "stone"); p.d.ellipse((x - 23, 34, x + 23, 86), outline=p.c("ink"))
    p.d.arc((x - 18, 39, x + 18, 81), 200, 300, fill=p.c("stone_sh"))
    p.pxs([(x - 8, 52), (x + 6, 66), (x + 2, 46)], "stone_sh")
    p.box((22, 14, 78, 27), "wood")                                    # the sign over the door
    p.press((50, 17), "OPEN", "cream", anchor="ma", shadow="wood_sh")
    return p


def meme_review(L):
    p = Pic("pink")
    for i in range(0, PW + PH, 16):                                    # stripes
        p.poly([(i, 0), (i + 8, 0), (i + 8 - PH, PH), (i - PH, PH)], (255, 150, 190))
    p.press((51, 9), "MEME", "white", anchor="ma", fnt=PRESS16, shadow="ink")
    p.press((51, 28), "REVIEW", "yellow", anchor="ma", fnt=PRESS16, shadow="ink")
    for i, t0 in enumerate(TL.CLAPS[:2]):                              # the two claps
        a = L.t - t0
        if 0 <= a < 0.5:
            x = 28 + 44 * i
            fx.burst(p.img, x, 58, 13, 20, col("white"), 9, a * 3, INK)
            p.silk((x, 55), "CLAP", "ink", anchor="ma")
    a = L.age("Elon")
    if a >= 0:
        dy = pop_dy(a, 0.12, 8) or 0
        p.rbox((10, 74 + dy, 89, 91 + dy), "bar", "ink")
        p.silk((50, 77 + dy), "SPECIAL GUEST", "dim", anchor="ma")
        p.silk((50, 84 + dy), "ELON MUSK", "text", anchor="ma")
    return p


def summons(L):
    """The only way he visits Sam: with papers."""
    p = Pic("paper")
    p.box((3, 3, 96, 92), "paper", "paper_sh")
    p.press((50, 8), "SUMMONS", "ink", anchor="ma")
    p.line([(12, 19), (88, 19)], "ink")
    p.silk((50, 24), "MUSK", "ink", anchor="ma")
    p.silk((50, 31), "v.", "grey", anchor="ma")
    p.silk((50, 38), "OPENAI", "ink", anchor="ma")
    p.lines((12, 49, 88, 0), 4, short=(3,))
    p.ell((10, 70, 28, 88), "red"); p.ell((14, 74, 24, 84), "red_hi")   # the seal
    p.line([(50, 84), (58, 78), (64, 84), (72, 76), (86, 82)], "blue_sh")  # a signature
    p.stamp(62, 62, "SERVED", L.age("serve"), "red")
    return p


def keynote(L):
    """The photograph: a stage in 2008."""
    p = Pic("black")
    p.grad((0, 0, PW, 70), "night_hi", "night")
    p.box((8, 6, 62, 46), "blue", "ink")                               # the slide behind him
    p.rbox((27, 16, 43, 32), "white", None); p.rect((31, 20, 39, 28), "blue_hi")
    p.rect((0, 70, PW, PH), "wood_sh"); p.line([(0, 70), (PW, 70)], "wood")
    p.put(young_sam(), 66, 86, "mb")
    a1, a2 = L.age("popped"), L.age("collars")
    if L.on("polos"):
        p.tag((4, 52), "POLO 1", "polo1", "ink")
        p.tag((4, 62), "POLO 2", "polo2", "ink")
        p.line([(40, 56), (56, 49)], "polo1"); p.line([(40, 66), (60, 50)], "polo2")
    if a1 >= 0:
        fx.arrow(p.img, 92, 22, 79, 37, col("gold"), 2, 5, INK)
        p.silk((98, 12), "UP", "gold_hi", anchor="ra")
    if a2 >= 0:
        fx.arrow(p.img, 44, 18, 55, 37, col("gold"), 2, 5, INK)
        p.silk((42, 9), "UP", "gold_hi", anchor="ra")
    p.tag((97, 84), "2008", "white", "ink", "ra")
    return p


def adult_mode(L):
    """Promised, then shelved."""
    p = Pic("panel")
    p.header("SETTINGS", "bar", "text")
    a_on, a_off, a_out, a_d = L.age("porno"), L.age("pulled"), L.age("out"), L.age("dollars")
    for i, name in enumerate(("DARK MODE", "ADULT MODE", "MEMORY")):
        y = 15 + 20 * i
        mine = i == 1
        p.rect((3, y, 96, y + 16), "panel_hi" if mine else "bar")
        p.silk((7, y + 6), name, "text" if mine else "dim")
        on = True if not mine else (a_on >= 0 and a_off < 0)
        k = (k_in(a_on, 0.12) if a_off < 0 else 1 - k_in(a_off, 0.12)) if mine else 1.0
        p.rbox((74, y + 4, 92, y + 12), "ok" if on else "mute", "ink", 4)
        x = 76 + int(round(k * 10))
        p.ell((x, y + 5, x + 6, y + 11), "white")
    if a_on >= 0 and a_off < 0:
        p.tag((50, 78), "COMING: DECEMBER", "ok", "ink", "ma")
    if a_d >= 0:                                                       # what it was traded for
        for i in range(9):
            if a_d > 0.03 * i:
                p.put(P.coin(4), 10 + 10 * i, min(86, -6 + (a_d - 0.03 * i) * 260) - (3 if i % 2 else 0))
    p.stamp(50, 82, "SHELVED", a_out, "red_hi", -8)
    return p


def monster(L):
    """He warns about it; then he plugs it in."""
    p = Pic("black")
    a_m, a_w, a_on = L.age("monsters"), L.age("wire"), L.age("weapon")
    on = a_on >= 0
    p.rect((16, 10, 86, 84), "night")                                  # the cage
    p.rect((0, 84, PW, PH), "grey_sh")
    if a_m >= 0:                                                       # the thing in it
        p.ell((28, 22, 76, 86), "purple_sh" if not on else "red_sh")
        p.poly([(30, 40), (22, 26), (36, 32)], "purple_sh" if not on else "red_sh")
        p.poly([(72, 40), (80, 26), (66, 32)], "purple_sh" if not on else "red_sh")
        eye = "red_hi" if on else "yellow"
        p.poly([(38, 44), (48, 48), (38, 50)], eye); p.poly([(66, 44), (56, 48), (66, 50)], eye)
        p.rect((40, 60, 64, 68), "black")
        for i in range(6):                                             # teeth
            p.poly([(40 + 4 * i, 60), (44 + 4 * i, 60), (42 + 4 * i, 64)], "white")
            p.poly([(42 + 4 * i, 68), (46 + 4 * i, 68), (44 + 4 * i, 64)], "white")
    for x in range(16, 88, 10):                                        # the bars
        p.rect((x, 10, x + 1, 84), "steel_sh")
    p.box((16, 8, 86, 12), "steel_sh"); p.box((16, 82, 86, 86), "steel_sh")
    p.rect((30, 1, 70, 9), "warn"); p.silk((50, 3), "DANGER", "ink", anchor="ma")
    if a_w >= 0:                                                       # the cable
        k = ease_out(k_in(a_w, 0.5))
        x = int(lerp(-6, 16, k))
        p.line([(0, 90), (x - 8, 90), (x - 4, 72), (x, 72)], "orange", w=2)
        p.rect((x, 69, x + 5, 75), "steel")
    if on:
        for i in range(4):
            if int(L.t * 14 + i) % 2:
                p.line([(22 + 3 * i, 66 - 4 * i), (26 + 3 * i, 62 - 4 * i)], "yellow")
        p.tag((97, 88), "ONLINE", "ok", "ink", "ra")
    return p


def cruising(L):
    """The hypercar, and the sign held out of its window."""
    p = Pic("sky")
    p.grad((0, 0, PW, 56), "sky", "sky_hi")
    p.ell((-20, 40, 50, 80), "grass"); p.ell((40, 44, 130, 84), "grass_sh")
    p.rect((0, 60, PW, PH), "grey_sh"); p.line([(0, 60), (PW, 60)], "grey")
    off = int(L.t * 90) % 20
    for x in range(-20, PW + 20, 20):                                  # the road going by
        p.rect((x - off + 20, 82, x - off + 30, 83), "yellow")
    p.put(hypercar(), 46, 74 + (1 if int(L.t * 12) % 2 else 0), "mb")
    a = L.age("begging")
    if L.on("constantly"):
        dy = pop_dy(L.age("constantly"), 0.12, 6) or 0
        p.line([(50, 54), (56, 36 + dy)], "brown_sh", w=2)             # an arm's worth of stick
        p.box((10, 8 + dy, 96, 37 + dy), (196, 150, 100))
        p.silk((53, 13 + dy), "SPARE", "ink", anchor="ma")
        p.silk((53, 21 + dy), "$7 TRILLION?", "ink", anchor="ma")
        if a >= 0:
            p.silk((53, 29 + dy), "ANYTHING HELPS", "brown_sh", anchor="ma")
    return p


T_SV, T_BADGE, T_PP = when("v2", 8, "translation"), when("v2", 9, "badge"), when("v2", 9, "small")


def translate(t):
    """Translation's on him: Swedish to English."""
    p = Pic("white")
    p.rect((0, 0, PW, 16), "blue"); p.rect((0, 6, PW, 9), "yellow"); p.rect((28, 0, 32, 16), "yellow")   # the flag
    p.silk((6, 21), "SWEDISH", "blue_sh")
    p.box((4, 28, 95, 46), "paper", "grey")
    if t >= T_SV:
        p.silk((8, 35), fx.typed("KOENIGSEGG", t - T_SV, 30), "ink")
    if t >= T_BADGE:
        p.put(badge(), 86, 37 + (pop_dy(t - T_BADGE, 0.12, 6) or 0))
    p.poly([(46, 49), (54, 49), (50, 54)], "grey")                     # down to
    p.silk((6, 57), "ENGLISH", "blue_sh")
    p.box((4, 64, 95, 90), "paper", "blue")
    if t >= T_PP:
        p.press((50, 73), fx.typed("SMALL PP", t - T_PP, 28), "ink", anchor="ma")
    elif t >= T_SV + 0.4:
        for i in range(3):
            if int(t * 5) % 4 > i:
                p.rect((42 + 6 * i, 76, 44 + 6 * i, 78), "grey")
    return p


def captor(L, smug=False):
    """Who is holding him."""
    p = Pic("black")
    p.grad((0, 0, PW, PH), "night", "black")
    p.ell((22, 12, 78, 68), "gpt_glow"); p.ell((24, 14, 76, 66), "gpt")
    p.d.arc((24, 14, 77, 67), 20, 110, fill=p.c("gpt_sh"))
    look = 5 if not smug else 3
    p.rect((38 + look, 32, 40 + look, 39), "gpt_dk"); p.rect((56 + look, 32, 58 + look, 39), "gpt_dk")
    if smug:
        p.line([(43, 50), (47, 53), (55, 53), (59, 50)], "gpt_dk", w=2)
        p.silk((50, 76), "HE'S FINE.", "text", anchor="ma")
        p.silk((50, 84), "HE LOVES IT HERE.", "dim", anchor="ma")
    else:
        p.line([(44, 52), (58, 52)], "gpt_dk", w=2)
    return p


def thumbnail(L):
    """The thumbnail: "I Built God (Gone Wrong)"."""
    p = Pic("yellow")
    for i in range(12):                                                # the rays
        a0, a1 = i * math.pi / 6, (i + 0.5) * math.pi / 6
        p.poly([(66, 56), (66 + 140 * math.cos(a0), 56 + 140 * math.sin(a0)),
                (66 + 140 * math.cos(a1), 56 + 140 * math.sin(a1))], "orange")
    p.d.ellipse((50, 26, 82, 34), outline=p.c("white"), width=2)        # a halo
    p.orb(66, 58, 15, "open", 0, "gpt", 1)
    if L.on("Built"):
        outline_text(p.img, (4, 4), "I BUILT GOD", PRESS, "white", INK)
    if L.on("Gone"):
        p.rect((2, 15, 72, 25), "red"); p.silk((5, 18), "(GONE WRONG)", "white")
    if L.on("arrow"):
        fx.arrow(p.img, 96, 92, 82, 72, col("red"), 3, 7, INK)
        p.d.ellipse((46, 38, 86, 78), outline=p.c("red"), width=2)
    a = L.age("shocked")
    if a >= 0:
        h = head("sam", "wide", "worried", "o")
        if L.on("pale"):
            h = tint(h, C["white"], 0.4)
        p.put(h, 22, 96 + (pop_dy(a, 0.12, 8) or 0), "mb")
    p.tag((97, 85), "10:01", "black", "white", "ra")
    return p


def unavailable(a):
    p = Pic("black")
    p.rect((0, 0, PW, PH), (40, 40, 46))
    p.rbox((34, 14, 66, 38), "grey_sh", None, 4)                       # a screen with a face on it
    p.rect((42, 21, 44, 24), "black"); p.rect((56, 21, 58, 24), "black")
    p.line([(44, 32), (47, 30), (53, 30), (56, 32)], "black")
    p.press((50, 46), "VIDEO", "white", anchor="ma")
    p.press((50, 57), "UNAVAILABLE", "white", anchor="ma")
    p.silk((50, 72), "THIS VIDEO WAS", "grey_hi", anchor="ma")
    p.silk((50, 80), "NEVER UPLOADED.", "grey_hi", anchor="ma")
    return p


def tape(tile, t):
    """A webcam tile as a hostage tape: handheld, washed out, with the camcorder's clock on it."""
    g = tile.convert("L")
    out = Image.merge("RGB", (g.point(lambda v: int(v * 0.72 + 10)), g.point(lambda v: int(v * 0.9 + 6)),
                              g.point(lambda v: int(v * 0.74 + 14))))
    dx, dy = int(round(2 * math.sin(t * 4.7))), int(round(1.5 * math.sin(t * 6.1 + 1)))
    moved = Image.new("RGB", out.size, C["black"])
    moved.paste(out, (dx, dy))
    band = int(t * 50) % (TH + 30) - 15                                # a tracking fault, rolling down
    if 0 <= band < TH - 3:
        strip = moved.crop((0, band, TW, band + 3))
        moved.paste(strip, (4, band))
    d = ImageDraw.Draw(moved)
    for y in range(0, TH, 2):
        d.line([(0, y), (TW, y)], fill=(0, 0, 0))
    shifted = Image.new("RGB", out.size, C["black"])
    shifted.paste(out, (dx, dy))
    moved = Image.blend(moved, shifted, 0.78)                          # the scan lines, faint
    d = ImageDraw.Draw(moved)
    clock = f"0:00:{int(t) % 60:02d}"
    for x, y, s in ((3, 3, "   REC"), (TW - 6 - silk_w(clock), 3, clock), (3, 90, "DAY 1,043")):   # the camcorder's own text
        d.rectangle((x - 1, y, x + silk_w(s) + 3, y + 8), fill=C["black"])
        silk(moved, (x + 2, y + 2), s, "white")
    if int(t * 2) % 2:
        d.ellipse((5, 5, 9, 9), fill=C["live"])
    return moved


# --- the gags ---------------------------------------------------------------------------------------

def next_(c, L):
    """"Next!": Felix swipes the picture away."""
    a = L.age("Next")
    swipe(c, a)
    if 0 <= a < 0.45:
        pose(c, "felix", arms="chop", brows="up")


@gag("v2", 0)
def forty_thieves(c, L):
    show(c, thieves(L), "A STORY", L.age())
    if L.on("you're"):
        pose(c, "felix", arms="point")
    yield "front"


@gag("v2", 1)
def open_sesame(c, L):
    a_o, a_f = L.age("Open"), L.age("Felony")
    show(c, cave(L), "THE CAVE", L.age())
    if 0 <= a_f < 0.9:
        pose(c, "sam", arms="point", mouth="wide", brows="angry", eyes="open", react=False)
    yield "front"
    say(c, "felix", ["OPEN", "SESAME!"], a_o, 1.3)
    say(c, "sam", "FELONY!", a_f, 1.1)
    stamp(c, *wx(50, 60), "FELONY", a_f, "red", -12, PRESS16)


@gag("v2", 2)
def meme_review_clap_clap(c, L):
    show(c, meme_review(L), "HIS SHOW", L.age())
    t = c.t
    c1, c2 = TL.CLAPS[:2]
    if c1 - 0.4 <= t < c2 + 0.25:                                      # he claps twice
        together = abs(t - c1) < 0.07 or abs(t - c2) < 0.07
        pose(c, "felix", arms="acc0" if together else "acc2", brows="up", eyes="shut" if together else "open")
    yield "mid"
    for t0 in (c1, c2):
        if 0 <= t - t0 < 0.12:
            x, y = c.anchor["felix"]["hand_near"]
            fx.burst(c.tile["felix"], x + 5, y - 2, 5, 11, col("gold_hi"), 7, t * 9, INK)
    yield "front"


@gag("v2", 3)
def serve_you_papers(c, L):
    a = L.age("papers")
    show(c, summons(L), "DELIVERY", L.age())
    next_(c, L)
    if a > 0.3:
        pose(c, "sam", eyes="down", brows="worried")
    yield "front"
    if a >= 0:                                                         # a copy, onto his desk
        spr = P.sheet(16, 20, None, n=4)
        fly(c.world, spr, wx(50, 60), tx("sam", 66, 100), ease_out(k_in(a, 0.35)), lift=22, turns=1)


POLOS = (when("v2", 4, "layered"), when("v2", 5) + 0.3)


@span(*POLOS)
def two_polos(c, L):
    """Sam, dressed as charged."""
    a = c.t - POLOS[0]
    pose(c, "sam", outfit="polos", eyes="down" if 0.5 < a < 1.5 else c.st["sam"]["eyes"], brows="worried")
    yield "mid"
    hx, hy = c.anchor["sam"]["chest"]
    P.sparkles(c.tile["sam"], hx, hy - 6, a, n=6, r=20)


@gag("v2", 4)
def popped_both_collars(c, L):
    show(c, keynote(L), "KEYNOTE, 2008", L.age())
    yield "front"


@gag("v2", 5)
def pulled_out_for_dollars(c, L):
    show(c, adult_mode(L), "ROADMAP", L.age())
    yield "front"


@gag("v2", 6)
def wire_up_the_weapon(c, L):
    show(c, monster(L), "SAFETY", L.age())
    if L.on("whisper") and not L.on("then"):                           # a finger to his lips
        pose(c, "sam", arms="hush", eyes="wide", brows="worried", mouth="o", react=False)
    yield "front"


@gag("v2", 7)
def constantly_begging(c, L):
    show(c, cruising(L), "ON THE ROAD", L.age())
    yield "front"


@gag("v2", 8)
def translation(c, L):
    show(c, translate(c.t), "TRANSLATE", L.age("I'm"))
    if not L.on("I'm"):
        show(c, cruising(Sung(c.t)), "ON THE ROAD", 1.0)
    elif L.age("bro") < 0.3:
        pose(c, "felix", arms="chest", brows="up")
    yield "front"


@gag("v2", 9)
def small_pp(c, L):
    show(c, translate(c.t), "TRANSLATE", 1.0)
    next_(c, L)
    yield "front"


TAPE = (when("v2", 10, "hostage"), when("v2", 11, "Next") + 0.1)


@span(*TAPE)
def hostage_tape(c, L):
    """Sam's webcam, as a tape from wherever they are holding him."""
    t = c.t
    hold(c, "sam", newspaper())
    twice = when("v2", 11, "twice")
    blink = any(0 <= t - (twice + d) < 0.14 for d in (0.42, 0.78))
    pose(c, "sam", eyes="blink" if blink else "open", brows="worried", mouth="closed", sweat=True, react=False,
         lean=0, bob=0)
    yield "mid"
    c.tile["sam"] = tape(c.tile["sam"], t)


@gag("v2", 10)
def like_a_hostage(c, L):
    show(c, captor(L), "", L.age())
    yield "front"


@gag("v2", 11)
def blink_twice(c, L):
    show(c, captor(L, smug=L.on("chatbot")), "", 1.0)
    next_(c, L)
    yield "front"


@gag("v2", 12)
def i_built_god(c, L):
    show(c, thumbnail(L), "RECOMMENDED", L.age())
    yield "front"


@gag("v2", 13, post=1.0)
def all_thumbnail(c, L):
    a_v, a = L.age("video"), L.age("thumbnail")
    show(c, thumbnail(Sung(c.t)), "RECOMMENDED", 1.0)
    if a_v >= 0:
        show(c, unavailable(a_v), "404", a_v)
    yield "mid"
    if a >= 0:                                                         # his own tile, as the thumbnail
        tile = c.tile["sam"]
        hx, hy = c.anchor["sam"]["head"]
        d = ImageDraw.Draw(tile)
        d.ellipse((hx - 25, hy - 5, hx + 23, hy + 45), outline=C["red"], width=2)
        fx.arrow(tile, 6, 12, hx - 22, hy + 6, C["red"], 3, 7, INK)
        dy = pop_dy(a, 0.12, 6) or 0
        d.rectangle((2, 60 + dy, 46, 82 + dy), fill=C["yellow"], outline=INK)
        silk(tile, (24, 63 + dy), "ALL", "ink", anchor="ma")
        silk(tile, (24, 70 + dy), "THUMB-", "red", anchor="ma")
        silk(tile, (24, 76 + dy), "NAIL", "red", anchor="ma")
    yield "front"
