"""Verse 4: Felix answers. Big Brother, like the show nobody watches; his wife's retired channel, three times
OpenAI's; funding rounds against a child's drawing; the three words the bot can't say (on the blocks from
verse 1); what the patients prescribed their doctor (fifty thousand printers); Ajax on Odysseus and the
wooden horse already in Sam's office; and a lesson from the apology guru, demonstrated on camera, for the
day the bot stages a coup."""
from gagkit import *  # noqa: F403


# --- small things ---------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def crayon_drawing():
    """What his boy drew: a house, the sun, and a dad with yellow hair."""
    f = Canvas(40, 32)
    f.rect((1, 1, 38, 30), "paper")
    f.rect((1, 24, 38, 30), "green_hi")
    f.ell((28, 3, 35, 10), "yellow"); f.line([(31, 12), (31, 14)], "yellow"); f.line([(26, 7), (24, 7)], "yellow")
    f.d.rectangle((5, 14, 17, 24), outline=f.c("red")); f.line([(4, 14), (11, 8), (18, 14)], "red")
    f.rect((10, 19, 12, 24), "blue")
    f.line([(25, 16), (25, 23)], "ink"); f.line([(22, 19), (28, 19)], "ink")                # dad
    f.line([(25, 23), (23, 27)], "ink"); f.line([(25, 23), (27, 27)], "ink")
    f.ell((23, 11, 27, 15), "fskin"); f.line([(22, 11), (28, 10)], "yellow")
    f.line([(32, 20), (32, 24)], "ink"); f.line([(30, 22), (34, 22)], "ink")                # and him
    f.line([(32, 24), (31, 27)], "ink"); f.line([(32, 24), (33, 27)], "ink")
    f.ell((30, 16, 34, 20), "fskin")
    return f.done()


@lru_cache(maxsize=None)
def head_mirror():
    """A doctor's head mirror on its band, facing right."""
    f = Canvas(40, 16)
    f.line([(6, 12), (20, 9), (34, 11)], "black", w=2)
    f.ell((23, 1, 35, 13), "steel"); f.ell((26, 4, 32, 10), "steel_hi"); f.px((29, 7), "grey_sh")
    return f.done()


@lru_cache(maxsize=None)
def printer(page=0):
    """A desktop printer; `page` 0-3 is how far the sheet has come out."""
    f = Canvas(26, 26)
    if page:
        h = 3 + 3 * page
        f.rect((6, 12 - h, 19, 12), "paper")
        if page > 1:
            f.line([(8, 12 - h + 3), (17, 12 - h + 3)], "red")
        if page > 2:
            f.line([(8, 12 - h + 6), (15, 12 - h + 6)], "red")
    f.d.rounded_rectangle((1, 11, 24, 23), 2, fill=f.c("grey_hi"))
    f.rect((4, 11, 21, 13), "grey_sh")
    f.rect((3, 19, 22, 21), "grey"); f.px((20, 16), "green")
    return f.done()


@lru_cache(maxsize=None)
def wood_horse(k=1.0):
    """A wooden horse on wheels, facing left: a gift. About 48 x 48, times `k` (drawn at that size, not
    scaled up, so its lines stay one pixel wide)."""
    def pt(x, y):
        return int(round(x * k)), int(round((y + 4) * k))

    def box(x0, y0, x1, y1):
        return pt(x0, y0) + pt(x1, y1)

    dot = int(k) - 1
    f = Canvas(int(48 * k) + 2, int(48 * k) + 1)
    f.rect(box(12, 16, 40, 30), "wood")                                # the body
    for x in (18, 25, 32):
        f.line([pt(x, 16), pt(x, 30)], "wood_sh")
    f.poly([pt(12, 18), pt(6, 4), pt(14, 2), pt(20, 16)], "wood")      # the neck
    f.poly([pt(2, 4), pt(14, 1), pt(15, 8), pt(3, 10)], "wood_hi")     # the head
    f.poly([pt(11, 1), pt(13, -3), pt(15, 2)], "wood_sh")              # an ear
    ex, ey = pt(6, 5)
    f.rect((ex, ey, ex + dot, ey + dot), "ink")
    f.line([pt(16, 3), pt(21, 15)], "brown_sh", w=int(2 * k))          # the mane
    f.poly([pt(40, 17), pt(46, 22), pt(41, 24)], "brown_sh")           # the tail
    for x in (14, 20, 32, 38):
        f.rect(box(x, 30, x + 2, 36), "wood_sh")
    f.rect(box(8, 36, 44, 38), "wood_sh")                              # the cart
    f.ell(box(10, 36, 18, 43), "brown_sh"); f.ell(box(34, 36, 42, 43), "brown_sh")
    for x in (14, 38):
        hx, hy = pt(x, 39.5)
        f.rect((hx, hy, hx + dot, hy + dot), "wood_hi")
    f.rect(box(24, 20, 30, 26), "brown_sh")                            # a hatch
    return f.done()


# --- the pictures -----------------------------------------------------------------------------------

def the_show(L):
    """Big Brother, the show. Nobody's watching."""
    p = Pic("night")
    p.rbox((6, 6, 93, 60), "wood", "ink", 4)                           # the television
    p.rect((11, 11, 78, 55), "black")
    p.ell((27, 16, 63, 42), "eye_w"); p.ell((37, 20, 53, 38), "sam"); p.ell((41, 24, 49, 34), "ink")
    p.silk((45, 46), "BIG BROTHER", "white", anchor="ma")
    for y in (18, 30, 42):
        p.ell((82, y, 89, y + 7), "grey_sh")                           # dials
    p.line([(40, 6), (30, -2)], "steel"); p.line([(58, 6), (68, -2)], "steel")
    a = L.age("nobody")
    p.silk((30, 70), "VIEWERS:", "dim", anchor="ma")
    if a >= 0:
        p.press((66, 66 + (pop_dy(a, 0.12, 6) or 0)), "0", "live", fnt=PRESS16)
        x, hop = (a * 40) % 130 - 15, abs(int(4 * math.sin(a * 9)))     # tumbleweed
        p.d.ellipse((x - 6, 82 - hop, x + 6, 94 - hop), outline=p.c("wood_hi"))
        p.d.arc((x - 4, 84 - hop, x + 4, 92 - hop), 0, 200, fill=p.c("wood"))
        p.d.arc((x - 3, 85 - hop, x + 5, 91 - hop), 150, 330, fill=p.c("wood_hi"))
    return p


def channels(L):
    """Subscribers: her retired channel, and his company's."""
    p = Pic("white")
    p.header("SUBSCRIBERS", "red", "white")
    p.line([(10, 78), (92, 78)], "ink")
    a1, a2, a3 = L.age("dead"), L.age("triples"), L.age("clocking")
    if L.on("wife"):
        h = int(54 * ease_out(k_in(L.age("wife"), 0.4)))
        p.box((20, 78 - h, 44, 78), "pink")
        p.silk((32, 82), "MARZIA", "ink", anchor="ma")
        if a1 >= 0:                                                    # cobwebs: it retired in 2018
            p.line([(20, 30), (30, 24)], "grey"); p.line([(20, 36), (36, 24)], "grey"); p.line([(24, 24), (22, 34)], "grey")
            p.silk((32, 89), "(RETIRED)", "grey", anchor="ma")
    if a2 >= 0:
        h = int(18 * ease_out(k_in(a2, 0.3)))
        p.box((60, 78 - h, 84, 78), "sam")
        p.silk((72, 82), "OPENAI", "ink", anchor="ma")
    if a3 >= 0:
        p.press((74, 34 + (pop_dy(a3, 0.12, 6) or 0)), "3x", "red", anchor="ma", fnt=PRESS16, shadow="ink")
        p.line([(50, 24), (54, 24), (54, 60), (50, 60)], "red")
    return p


def rounds(L):
    """He raises rounds."""
    p = Pic("panel")
    p.silk((50, 6), "FUNDING ROUNDS", "dim", anchor="ma")
    n = min(8, int(k_in(L.age("rounds"), 0.5) * 8)) if L.on("rounds") else 0
    for i in range(n):
        x, y = 8 + 11 * i, 78 - 6 * i
        p.rect((x, y, x + 9, 84), "sam_sh" if i % 2 else "sam")
        p.d.rectangle((x, y, x + 9, 84), outline=p.c("ink"))
        p.silk((x + 5, y - 7), "ABCDEFGH"[i], "sam_hi", anchor="ma")
    if n == 8:
        p.put(P.coin(4), 89, 22); p.put(P.coin(4), 90, 18)
    p.line([(4, 85), (96, 85)], "line")
    return p


def three_more_words(c, L):
    """Three words his boy has learned and the bot can't say, on the blocks from the nursery."""
    p = Pic("sky_hi")
    p.rect((0, 62, PW, PH), "cream"); p.line([(0, 62), (PW, 62)], "paper_sh")
    spots = ((26, 36, "I", "red", 16), (63, 36, "DON'T", "blue", None), (50, 60, "KNOW", "yellow", None))
    for (x, y, word, color, w), pat in zip(spots, ('"I', "don't", "know")):
        a = L.age(pat)
        if a >= 0:
            p.put(P.block(word, color, depth=2, w=w), x, y + (pop_dy(a, 0.12, 14) or 0), "mb")
        elif L.on("three"):
            bw = (w or text_width(word, PRESS) + 4)
            p.d.rectangle((x - bw // 2, y - 21, x + bw // 2, y - 1), outline=p.c("grey"))
    a_b = L.age("bot")
    if a_b >= 0:                                                       # meanwhile, the bot
        dy = pop_dy(a_b, 0.12, 6) or 0
        p.orb(11, 81 + dy, 7, "open", 1 + int(L.t * 8) % 2)
        p.rbox((22, 70 + dy, 97, 92 + dy), "white", "ink", 4)
        p.silk((60, 74 + dy), "CERTAINLY!", "ink", anchor="ma")
        p.silk((60, 82 + dy), "IT'S 7.", "ink", anchor="ma")
    return p


def prescription(L):
    """What the patients prescribed the doctor."""
    p = Pic("paper")
    p.rect((0, 0, PW, 14), "sam_sh")
    p.silk((50, 5), "DR. S. ALTMAN", "white", anchor="ma")
    p.press((8, 20), "Rx", "sam_sh", fnt=PRESS16)
    p.silk((44, 21), "FROM:", "grey"); p.silk((44, 29), "PATIENTS", "ink")
    p.lines((8, 50, 92, 0), 4, gap=10)
    a = L.age("read")
    for row in range(3):                                               # their handwriting is no better than his
        n = int(clamp((a - 0.25 * row) * 60, 0, 40 - 9 * (row == 2)))
        pts = [(8 + 2 * i, 47 + 10 * row - (3 if i % 2 else 0) - int(2 * rnd("rx", row, i))) for i in range(n)]
        if len(pts) > 1:
            p.line(pts, "blue_sh")
    if L.on("prescribe"):
        p.tag((8, 82), "SIGNED: ALL OF THEM", "sam_sh", "white")
    return p


def printers(L):
    """Fifty thousand printers, 2018."""
    p = Pic("panel")
    a_p, a_s = L.age("printers"), L.age("subscribe")
    a = L.age("print", 1)
    for i in range(6):
        x, y = 20 + 30 * (i % 3), 24 + 28 * (i // 3)
        page = 0 if a < 0 else min(3, 1 + int((a - 0.04 * i) * 12)) if a > 0.04 * i else 0
        p.put(printer(page), x, y)
    if a_p >= 0:
        p.tag((50, 68), "50,000 PRINTERS", "ink", "white", "ma")
    if a_s >= 0:
        dy = pop_dy(a_s, 0.12, 6) or 0
        p.rbox((6, 78 + dy, 93, 93 + dy), "paper", "ink", 2)
        p.press((50, 82 + dy), "SUBSCRIBE", "red", anchor="ma")
    return p


def hobby(c, L):
    """Ajax, on a rig called Odysseus."""
    p = Pic("night")
    p.grad((0, 0, PW, PH), "brown_sh", "black")
    a, a_r = L.age("Ajax"), L.age("Odysseus")
    p.silk((50, 6), "MY HOBBY", "ajax_hi", anchor="ma")
    if a >= 0:
        dy = pop_dy(a, 0.14, 8) or 0
        p.orb(50, 46 + dy, 14, "happy", 0, "ajax")
        p.put(helmet(14), 50, 40 + dy)
        p.press((51, 67), "AJAX", "ajax_hi", anchor="ma", shadow="ink")
    if a_r >= 0:
        fx.arrow(p.img, 19, 86, 5, 86, col("led_c"), 2, 5, INK)
        p.silk((23, 83), "RIG: ODYSSEUS", "led_c")
    return p


def lobby_cam(L):
    """Security camera, the lobby: a delivery nobody has looked at."""
    p = Pic("grey_hi")
    p.rect((0, 0, PW, 56), "wall"); p.rect((0, 56, PW, PH), "stone")
    p.line([(0, 56), (PW, 56)], "stone_sh")
    p.box((6, 14, 30, 56), "window", "ink"); p.line([(18, 14), (18, 56)], "white")       # glass doors
    p.box((70, 20, 94, 36), "white", "grey"); p.silk((82, 25), "A.I.", "sam_sh", anchor="ma")
    a_h, a_o = L.age("horse"), L.age("oblivious")
    if a_h >= 0:
        k = ease_out(k_in(a_h, 0.6))
        p.put(wood_horse(), int(lerp(-30, 50, k)), 80, "mb")
        if L.on("house"):
            p.tag((97, 42), "FOR: SAM", "gold", "ink", "ra")
    p.tag((3, 3), "CAM 02  LOBBY", "black", "white")
    if int(L.t * 2) % 2:
        p.ell((90, 4, 94, 8), "live")
    if a_o >= 0:
        dy = pop_dy(a_o, 0.12, 6) or 0
        p.rbox((6, 82 + dy, 93, 93 + dy), "black", "ok", 2)
        p.silk((46, 85 + dy), "THREATS: NONE", "ok", anchor="ma")
        p.tick(82, 84 + dy, "ok")
    return p


def tutorial(L):
    """A masterclass."""
    p = Pic("felix_sh")
    for i in range(0, PW + PH, 14):
        p.poly([(i, 0), (i + 7, 0), (i + 7 - PH, PH), (i - PH, PH)], "felix")
    p.press((51, 8), "HOW TO", "white", anchor="ma", shadow="ink")
    p.press((51, 20), "APOLOGIZE", "yellow", anchor="ma", shadow="ink")
    p.put(scaled(mini("felix", "sad"), 3), 30, 60)
    if L.on("apology"):
        p.tag((48, 44), "WITH THE", "ink", "white")
        p.tag((48, 54), "GURU", "gold", "ink")
    p.rbox((60, 70, 90, 88), "red", "white", 4); p.poly([(71, 74), (71, 84), (81, 79)], "white")
    return p


STEPS = (("HOODIE ON", when("v4", 9, "hoodie")), ("HEAD DOWN", when("v4", 9, "head")),
         ("HIT THE FLOOR", when("v4", 9, "hit")), ("LOOK BLUE", when("v4", 9, "look")),
         ('"I\'VE GROWN"', when("v4", 10, "say")), ('"TRULY SORRY"', when("v4", 10, "truly")),
         ("TEAR, ON CUE", when("v4", 10, "squeeze")))


def checklist(t):
    """The steps of an apology video, ticked off as he demonstrates them."""
    p = Pic("paper")
    p.header("THE APOLOGY", "felix_sh", "white")
    for i, (s, t0) in enumerate(STEPS):
        if t < t0:
            break
        y = 15 + 11 * i + (pop_dy(t - t0, 0.1, 4) or 0)
        p.silk((4, y), f"{i + 1}.", "grey")
        p.silk((14, y), s, "ink")
        p.tick(89, y - 2, "green")
    return p


def front_page(L):
    """The day his bot stages a coup."""
    p = Pic("paper")
    p.silk((50, 4), "THE DAILY PROMPT", "ink", anchor="ma")
    p.line([(4, 11), (95, 11)], "ink"); p.line([(4, 13), (95, 13)], "ink")
    a = L.age("coup")
    if L.on("bot"):
        p.press((50, 17), "BOT STAGES", "ink", anchor="ma")
    if a >= 0:
        p.press((51, 28 + (pop_dy(a, 0.12, 6) or 0)), "COUP", "red", anchor="ma", fnt=PRESS16, shadow="ink")
    p.box((6, 48, 54, 92), "grey_hi", "ink")                           # the photograph: a balcony
    p.rect((7, 78, 53, 91), "stone"); p.line([(7, 78), (53, 78)], "stone_sh")
    for x in range(10, 52, 6):
        p.line([(x, 80), (x, 90)], "stone_sh")
    p.orb(30, 66, 11, "happy" if a < 0 else "flat", 0)
    if L.on("stages"):                                                 # in a general's cap
        p.rect((18, 52, 42, 57), "green_sh"); p.rect((16, 57, 44, 59), "black")
        p.d.rectangle((18, 52, 42, 57), outline=p.c("ink")); p.rect((28, 53, 32, 56), "gold")
    p.lines((60, 50, 94, 0), 8, gap=5, short=(3, 7))
    return p


# --- the gags ---------------------------------------------------------------------------------------

@gag("v4", 0)
def like_the_show(c, L):
    show(c, the_show(L), "TELEVISION", L.age())
    yield "front"


@gag("v4", 1)
def dead_channel(c, L):
    show(c, channels(L), "FOR SCALE", L.age())
    yield "front"


@gag("v4", 2)
def raising_a_boy(c, L):
    show(c, rounds(L), "HIS", L.age())
    if L.on("I'm"):
        hold(c, "felix", crayon_drawing())
        pose(c, "felix", brows="up", eyes="shut" if L.on("bro") else "open")
        if c.screen:
            c.screen["caption"] = "HIS, AND MINE"
    yield "front"


@gag("v4", 3)
def i_dont_know(c, L):
    show(c, three_more_words(c, L), "AGES 2+", L.age())
    yield "front"


DOC = (when("v4", 4, "Doc"), when("v4", 6) - 0.2)


@span(*DOC)
def doctor(c, L):
    """Sam, in a head mirror, for as long as he's the doctor."""
    a = c.t - DOC[0]
    pose(c, "sam", hat=(head_mirror(), -3 + (pop_dy(a, 0.14, 8) or 0)))
    yield "front"


@gag("v4", 4)
def read_the_prescription(c, L):
    show(c, prescription(L), "PRESCRIPTION", L.age())
    yield "front"


@gag("v4", 5)
def print_subscribe(c, L):
    a = L.age("print", 1)
    show(c, printers(L), "2018", L.age())
    yield "mid"
    if a >= 0:                                                         # and the one on his desk
        page = min(3, 1 + int(a * 8))
        spr = printer(page)
        c.tile["sam"].paste(spr, (56, 82), spr)
    yield "front"


@gag("v4", 6)
def ajax_on_odysseus(c, L):
    show(c, hobby(c, L), "HOME LAB", L.age())
    lit = L.on("rig")
    c.rack_lit = lit
    yield "mid"
    if L.on("Odysseus"):
        rig_label(c)
    yield "front"


def rig_label(c):
    """The name on Felix's rack, while it is lit. From "mid" on."""
    tile = c.tile["felix"]
    ImageDraw.Draw(tile).rectangle((2, 22, 50, 31), fill=C["black"], outline=C["led_c"])
    silk(tile, (5, 24), "ODYSSEUS", "led_c")


HORSE = when("v4", 7, "house")


@span(HORSE, 1e6)
def horse_in_the_house(c, L):
    """The wooden horse, in Sam's office from here to the end of the call. He never looks round."""
    if c.t < when("v4", 8) + 0.4:
        pose(c, "sam", eyes="open", brows="neutral", mouth="smile", react=False)
    yield "back"
    spr = wood_horse(2.0)
    c.tile["sam"].paste(spr, (int(lerp(TW, 2, ease_out(k_in(c.t - HORSE, 0.6)))), 9), spr)
    call.ban_button(c.tile["sam"], c.get("ban"))                       # the button stays in front of it
    yield "front"


@gag("v4", 7)
def oblivious(c, L):
    show(c, lobby_cam(L), "SECURITY", L.age())
    yield "front"


@gag("v4", 8)
def apology_guru(c, L):
    show(c, tutorial(L), "A MASTERCLASS", L.age())
    yield "front"


LESSON = (STEPS[0][1], when("v4", 11) - 0.05)


@span(*LESSON)
def demonstration(c, L):
    """Felix demonstrates: the hood, the head, the floor, the light, the lines, the tear."""
    t = c.t
    n = sum(1 for _, t0 in STEPS if t >= t0)
    dy = 0
    if n >= 2:
        dy += 3
    if n >= 3:
        dy += int(15 * ease_out(k_in(t - STEPS[2][1], 0.25)))
    said = 4 <= n < 7 and TL.loudness(t) > 0.15
    pose(c, "felix", outfit="hood", arms="clasp" if n < 3 else "desk", dy=dy, lean=0, bob=0,
         eyes="open" if n < 2 else "shut" if n >= 7 else "down", brows="worried",
         mouth="open" if said else "frown", tears=t >= when("v4", 10, "tear"), react=False)
    yield "mid"
    if n >= 4:                                                         # the lights, down and blue
        blend(c.tile["felix"], 1.0, "blue", 0.38 * k_in(t - STEPS[3][1], 0.3))
    yield "front"
    say(c, "felix", "I'VE GROWN.", t - when("v4", 10, "grown"), 0.5, SILK)
    say(c, "felix", "TRULY SORRY.", t - when("v4", 10, "sorry"), 0.6, SILK)


@gag("v4", 9)
def hoodie_on(c, L):
    show(c, checklist(c.t), "LESSON 1", L.age())
    yield "front"


@gag("v4", 10)
def a_tear_on_cue(c, L):
    show(c, checklist(c.t), "LESSON 1", 1.0)
    yield "front"


@gag("v4", 11, post=1.0)
def stages_a_coup(c, L):
    show(c, front_page(L), "ONE DAY", L.age())
    if L.on("coup"):
        pose(c, "felix", arms="point", brows="up")
    yield "front"
