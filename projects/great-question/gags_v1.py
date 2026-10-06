"""Verse 1: Sam, softly, on Felix. ChatGPT pulls up an exhibit for every bar: three toy blocks, a résumé
that says the same three words, the hot dogs and the toys, a match history with nothing but defeats (a
barrel, a label, a baby, Disney, a bridge), the Lost Boys, Neverland, and then the bot Felix built: a Qwen
in a wig, Alibaba's, flat-packed. Felix wears Peter Pan's cap for the middle of it."""
from gagkit import *  # noqa: F403


# --- small things ---------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def pacifier():
    f = Canvas(15, 11)
    f.d.ellipse((8, 2, 13, 8), outline=f.c("blue"))                    # the ring
    f.ell((3, 1, 9, 9), "pink")                                        # the shield
    f.ell((1, 3, 4, 7), "cream")                                       # the teat
    f.px((6, 3), "white")
    return f.done()


@lru_cache(maxsize=None)
def hot_dog():
    f = Canvas(36, 17)
    f.d.rounded_rectangle((3, 6, 32, 14), 4, fill=f.c("brown_hi"))     # the bun
    f.line([(6, 13), (29, 13)], "brown")
    f.d.rounded_rectangle((1, 3, 34, 9), 3, fill=f.c("red"))           # the sausage
    f.line([(3, 4), (32, 4)], "red_hi")
    for i in range(7):                                                 # the mustard
        f.line([(4 + 4 * i, 5), (6 + 4 * i, 7), (8 + 4 * i, 5)], "yellow")
    return f.done()


@lru_cache(maxsize=None)
def gamepad():
    f = Canvas(34, 21)
    f.ell((1, 7, 12, 19), "grey_sh"); f.ell((21, 7, 32, 19), "grey_sh")                # the grips
    f.d.rounded_rectangle((1, 3, 32, 14), 5, fill=f.c("grey_sh"))
    f.line([(6, 4), (27, 4)], "grey")
    f.rect((7, 7, 8, 11), "black"); f.rect((5, 9, 10, 9), "black")                      # the pad
    f.rect((24, 6, 25, 7), "red_hi"); f.rect((27, 9, 28, 10), "blue_hi")
    f.rect((21, 9, 22, 10), "green_hi"); f.rect((24, 12, 25, 13), "yellow")
    f.rect((14, 8, 15, 9), "grey"); f.rect((18, 8, 19, 9), "grey")
    return f.done()


@lru_cache(maxsize=None)
def rosette(label, color="gold", fnt_press=True, r=12):
    """A prize rosette with a word in the middle."""
    hi, sh = {"gold": ("gold_hi", "gold_sh"), "blue": ("blue_hi", "blue_sh"), "red": ("red_hi", "red_sh")}[color]
    f = Canvas(2 * r + 7, 2 * r + 17)
    cx = cy = r + 3
    f.poly([(cx - 7, cy + 5), (cx - 9, cy + r + 12), (cx - 5, cy + r + 9), (cx - 1, cy + r + 12), (cx, cy + 5)], sh)
    f.poly([(cx, cy + 5), (cx + 1, cy + r + 12), (cx + 5, cy + r + 9), (cx + 9, cy + r + 12), (cx + 7, cy + 5)], sh)
    for i in range(12):                                                # the pleats
        a = i * math.pi / 6
        x, y = cx + math.cos(a) * (r - 2), cy + math.sin(a) * (r - 2)
        f.ell((x - 3, y - 3, x + 3, y + 3), color)
    f.ell((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), "cream")
    if fnt_press:
        f.d.text((cx + 1, cy - 4), label, font=PRESS, fill=f.c(sh), anchor="ma")
    else:
        f.silk((cx, cy - 2), label, sh, anchor="ma")
    f.px((cx - r + 3, cy - r + 5), hi)
    return f.done()


@lru_cache(maxsize=None)
def kid(k):
    """One of the audience: a small round head."""
    skin = ("baby", "fskin_sh", "brown_hi", "sskin")[k % 4]
    hair = ("brown", "black", "gold", "red_sh", "brown_sh")[k % 5]
    f = Canvas(11, 12)
    f.ell((1, 2, 9, 10), skin)
    f.poly([(1, 5), (2, 2), (5, 1), (8, 2), (9, 5), (6, 3), (3, 4)], hair)
    f.px((4, 6), "eye"); f.px((7, 6), "eye")
    f.line([(4, 8), (6, 8)], "mouth")
    return f.done()


@lru_cache(maxsize=None)
def icon(kind):
    """What Felix lost to, 13x13."""
    f = Canvas(15, 15)
    if kind == "barrel":
        f.d.rounded_rectangle((3, 1, 11, 13), 2, fill=f.c("brown"))
        f.rect((2, 4, 12, 10), "brown")
        f.line([(2, 4), (12, 4)], "steel_sh"); f.line([(2, 10), (12, 10)], "steel_sh")
        f.line([(5, 2), (5, 12)], "brown_sh"); f.line([(9, 2), (9, 12)], "brown_hi")
    elif kind == "label":                                              # a record
        f.ell((1, 1, 13, 13), "black")
        f.d.ellipse((3, 3, 11, 11), outline=f.c("grey_sh"))
        f.ell((5, 5, 9, 9), "red"); f.px((7, 7), "white")
    elif kind == "baby":
        f.ell((2, 3, 12, 13), "baby")
        f.line([(6, 1), (8, 2), (7, 4)], "brown")                      # one curl
        f.px((5, 7), "eye"); f.px((9, 7), "eye")
        f.ell((6, 9, 8, 11), "pink"); f.pxs([(3, 9), (11, 9)], "flush")
    elif kind == "disney":                                             # a castle
        f.rect((3, 7, 11, 13), "blue_hi")
        f.rect((1, 5, 3, 13), "blue"); f.rect((11, 5, 13, 13), "blue"); f.rect((6, 3, 8, 13), "blue")
        f.poly([(0, 5), (2, 1), (4, 5)], "red"); f.poly([(10, 5), (12, 1), (14, 5)], "red")
        f.poly([(5, 3), (7, 0), (9, 3)], "red")
        f.rect((6, 10, 8, 13), "night")
    elif kind == "bridge":
        f.rect((1, 6, 13, 8), "stone")
        f.d.arc((2, 7, 12, 18), 180, 360, fill=f.c("stone_sh"))
        f.rect((1, 8, 2, 13), "stone_sh"); f.rect((12, 8, 13, 13), "stone_sh")
        f.line([(1, 5), (13, 5)], "stone_sh")
        f.line([(3, 12), (11, 12)], "sea_hi")
    return f.done()


@lru_cache(maxsize=None)
def crown():
    f = Canvas(21, 13)
    f.poly([(1, 11), (1, 3), (6, 7), (10, 1), (14, 7), (19, 3), (19, 11)], "gold")
    f.line([(1, 11), (19, 11)], "gold_sh"); f.line([(2, 9), (18, 9)], "gold_hi")
    f.px((10, 6), "red"); f.px((5, 9), "blue_hi"); f.px((15, 9), "blue_hi")
    return f.done()


@lru_cache(maxsize=None)
def cake(n="9"):
    f = Canvas(31, 36)
    f.d.text((8, 4), n, font=PRESS16, fill=f.c("red"))                 # the candle is the number
    f.poly([(15, 0), (13, 2), (15, 4), (17, 2)], "orange"); f.px((15, 2), "yellow")
    f.d.rounded_rectangle((3, 20, 27, 33), 2, fill=f.c("pink"))
    f.rect((3, 20, 27, 23), "white")
    for x in (5, 10, 15, 20, 25):                                      # the icing, dripping
        f.rect((x, 23, x + 1, 25), "white")
    f.line([(4, 30), (26, 30)], "red_hi")
    return f.done()


@lru_cache(maxsize=None)
def pan_cap():
    """Peter Pan's cap, facing right: green, pointed, one red feather."""
    f = Canvas(36, 19)
    f.poly([(3, 16), (8, 7), (20, 3), (33, 10), (28, 16)], "pan")
    f.poly([(3, 16), (28, 16), (30, 13), (6, 13)], "pan_sh")
    f.line([(9, 8), (20, 5)], "green_hi")
    f.poly([(13, 8), (4, 0), (9, 1), (16, 6)], "red")                  # the feather
    f.line([(13, 8), (5, 1)], "red_hi")
    return f.done()


@lru_cache(maxsize=None)
def plane():
    f = Canvas(21, 11)
    f.d.rounded_rectangle((2, 4, 18, 7), 2, fill=f.c("white"))
    f.poly([(8, 5), (4, 9), (7, 9), (12, 6)], "steel")                 # the wing
    f.poly([(2, 5), (1, 1), (4, 1), (6, 5)], "red")                    # the tail
    f.pxs([(12, 5), (14, 5), (16, 5)], "sky")
    return f.done()


@lru_cache(maxsize=None)
def box_bot():
    """A robot built at home: two cardboard boxes, a colander, tape."""
    f = Canvas(44, 56)
    f.line([(12, 30), (4, 38), (7, 44)], "steel", w=2)                 # the arms: dryer hose
    f.line([(32, 30), (40, 38), (37, 44)], "steel", w=2)
    f.rect((12, 26, 32, 50), "brown_hi")                               # the body
    f.rect((12, 26, 32, 28), "cream"); f.line([(22, 26), (22, 50)], "brown")
    f.ell((15, 33, 19, 37), "red"); f.ell((24, 33, 28, 37), "green")   # dials, in marker
    f.rect((15, 42, 29, 45), "black"); f.pxs([(17, 43), (20, 44), (23, 43), (26, 44)], "green_hi")
    f.rect((14, 9, 30, 24), "brown_hi")                                # the head
    f.rect((14, 9, 30, 10), "cream")
    f.ell((16, 12, 21, 17), "white"); f.ell((23, 12, 28, 17), "white")  # googly eyes
    f.px((19, 15), "ink"); f.px((24, 13), "ink")
    f.line([(18, 21), (26, 21)], "ink")
    f.d.chord((14, 1, 30, 15), 180, 360, fill=f.c("steel"))            # the colander
    f.pxs([(18, 5), (22, 4), (26, 5)], "steel_sh")
    f.line([(22, 1), (22, -2)], "steel")
    f.rect((14, 50, 19, 54), "brown"); f.rect((25, 50, 30, 54), "brown")
    return f.done()


@lru_cache(maxsize=None)
def wig():
    """Felix's hair and headphones, to sit on an orb of radius 20."""
    f = Canvas(52, 30)
    f.poly([(5, 28), (3, 16), (8, 7), (18, 2), (32, 1), (44, 5), (49, 13), (45, 18), (38, 12), (26, 11), (15, 14),
            (10, 22), (9, 28)], "fhair")
    f.line([(44, 8), (30, 5), (16, 8)], "fhair_hi"); f.line([(40, 12), (27, 9), (15, 12)], "fhair_sh")
    f.line([(9, 24), (11, 12), (18, 4)], "phones", w=2)
    f.ell((2, 17, 12, 29), "phones"); f.ell((4, 19, 10, 27), "felix"); f.ell((5, 21, 9, 25), "phones")
    return f.done()


@lru_cache(maxsize=None)
def flat_box(w=62, h=16):
    """A flat cardboard box, taped, with the product's name on it."""
    f = Canvas(w + 12, h + 12)
    f.poly([(1, 9), (9, 1), (w + 9, 1), (w + 1, 9)], "brown_hi")       # the top
    f.poly([(w + 1, 9), (w + 9, 1), (w + 9, h + 1), (w + 1, h + 9)], "brown_sh")
    f.rect((1, 9, w + 1, h + 9), "brown_hi")
    f.rect((1, 9, w + 1, h + 9), (196, 150, 100))
    f.poly([(w // 2 - 2, 9), (w // 2 + 6, 1), (w // 2 + 11, 1), (w // 2 + 3, 9)], "cream")   # tape
    f.rect((w // 2 - 2, 9, w // 2 + 3, h + 9), "cream")
    return f.done()


def umlaut(img, x, y, color):
    """The two dots over an A whose glyph starts at x and whose top is at y."""
    d = ImageDraw.Draw(img)
    d.point((x + 1, y - 2), fill=col(color)); d.point((x + 3, y - 2), fill=col(color))


# --- the pictures -----------------------------------------------------------------------------------

def nursery(L):
    """Three words a toddler can say."""
    p = Pic("sky_hi")
    p.rect((0, 58, PW, PH), "cream"); p.line([(0, 58), (PW, 58)], "paper_sh")
    for i, (word, color) in enumerate((("Pew", "red"), ("Die", "blue"), ("Pie", "yellow"))):
        a = L.age(word)
        if a >= 0:
            p.put(P.block(word.upper(), color, depth=2), 17 + 33 * i, 58 + (pop_dy(a, 0.12, 14) or 0), "mb")
    a = L.age("toddler")
    if a >= 0:
        p.put(pacifier(), 30, 77 + (pop_dy(a, 0.12, 6) or 0))
        p.tag((43, 73), "AGES 2+", "red", "white")
    return p


def resume(L):
    p = Pic("paper")
    p.header("RESUME", "blue_sh")
    x = PW // 2 - silk_w("RESUME") // 2
    for n in (1, 5):                                                   # the accents
        ex = x + silk_w("RESUME"[:n])
        p.line([(ex + 2, 1), (ex + 3, 0)], "white")
    for i, (pat, label) in enumerate((("name", "NAME"), ("fan", "FAN BASE"), ("r.sum", "EXPERIENCE"))):
        y = 16 + 27 * i
        p.silk((6, y), label, "grey")
        p.line([(6, y + 20), (94, y + 20)], "paper_ln")
        a = L.age(pat)
        if a >= 0:
            p.press((6, y + 9), fx.typed("PEW DIE PIE", a, 45), "ink")
    return p


def odd_jobs(L):
    """He sold hot dogs; then he played with toys for a wage."""
    p = Pic("cream")
    a_h, a_t, a_w = L.age("hot"), L.age("toys"), L.age("wage")
    p.line([(0, 47), (PW, 47)], "paper_sh")
    if a_h >= 0:
        p.put(hot_dog(), 50, 24 + (pop_dy(a_h, 0.12, 8) or 0))
        p.tag((50, 36), "2011: HOT DOGS", "red_sh", "white", "ma")
    if a_t >= 0:
        p.put(gamepad(), 50, 66 + (pop_dy(a_t, 0.12, 8) or 0))
        p.tag((50, 82), "SINCE: TOYS", "blue_sh", "white", "ma")
    if a_w >= 0:                                                       # and it pays: a pile either side
        for i in range(8):
            if a_w > 0.05 * i:
                p.put(P.coin(3), 16 if i % 2 else 84, 74 - 4 * (i // 2))
    return p


def babysitter(L):
    p = Pic("night")
    p.grad((0, 0, PW, PH), "night_hi", "night")
    a = L.age("babysitter")
    p.put(rosette("#1", "gold"), 50, 26)
    p.silk((50, 49), "THE BEST-PAID", "gold_hi", anchor="ma")
    if a >= 0:
        p.press((50, 58), "BABYSITTER", "white", anchor="ma", shadow="ink")
        for i in range(8):                                             # the children in his care
            if a > 0.05 * i:
                p.put(kid(i), 9 + 12 * i, 80 + (1 if i % 2 else 0))
    if L.on("YouTube"):
        p.silk((50, 88), "x 110,000,000", "gold_hi", anchor="ma")
    return p


# what he lost to, the small print, when the row arrives and when its small print does
HISTORY = (("barrel", "AMNESIA", when("v1", 4, "barrel"), None),
           ("label", "T-SERIES, 2019", when("v1", 4, "label"), None),
           ("baby", "COCOMELON", when("v1", 5, "baby"), when("v1", 5, "cradle")),
           ("disney", "$5 JOKE, 2017", when("v1", 6, "Disney"), when("v1", 6, "five")),
           ("bridge", "LIVE, 2017", when("v1", 7, "bridge"), when("v1", 7, "live")))


def history(t):
    """Felix's match history: every row a defeat."""
    p = Pic("panel")
    p.header("MATCH HISTORY", "bar", "text")
    n = sum(1 for row in HISTORY if t >= row[2])
    for i, (kind, small, t0, t1) in enumerate(HISTORY[:n]):
        new = i == n - 1
        y = 13 + 16 * i + ((pop_dy(t - t0, 0.12, 7) or 0) if new else 0)
        p.rect((2, y, 97, y + 14), "panel_hi" if new else "bar")
        p.rect((2, y, 3, y + 14), "live")
        p.put(icon(kind), 12, y + 7)
        p.silk((22, y + 2), kind.upper(), "text")
        p.silk((95, y + 2), "DEFEAT", "felix_hi", anchor="ra")
        if t >= (t1 or t0):
            p.silk((22, y + 8), small, "dim")
    return p, n


def warning(a):
    """What the window says about his language."""
    p = Pic("panel")
    p.grad((0, 0, PW, PH), "panel_hi", "panel")
    dy = pop_dy(a, 0.14, 8) or 0
    p.rbox((6, 14 + dy, 93, 80 + dy), (70, 50, 30), "warn")
    p.poly([(50, 20 + dy), (38, 40 + dy), (62, 40 + dy)], "warn")       # the triangle
    p.rect((49, 26 + dy, 50, 33 + dy), "ink"); p.rect((49, 36 + dy, 50, 37 + dy), "ink")
    p.silk((50, 46 + dy), "THIS CONTENT", "text", anchor="ma")
    p.silk((50, 54 + dy), "MAY VIOLATE OUR", "text", anchor="ma")
    p.silk((50, 62 + dy), "USAGE POLICIES.", "text", anchor="ma")
    p.silk((50, 71 + dy), "FELIX: LANGUAGE.", "warn", anchor="ma")
    return p


def lost_boys(L):
    """The clubhouse: no grown-ups."""
    p = Pic("pan_sh")
    for x, w in ((4, 9), (84, 11)):                                    # tree trunks
        p.rect((x, 0, x + w, PH), "brown_sh"); p.line([(x + 2, 0), (x + 2, PH)], "brown")
    p.rect((0, 82, PW, PH), "grass_sh")
    p.rect((19, 60, 22, 84), "wood_sh"); p.rect((77, 60, 80, 84), "wood_sh")
    p.box((10, 24, 89, 60), "wood")
    p.line([(11, 36), (88, 36)], "wood_sh"); p.line([(11, 48), (88, 48)], "wood_sh")
    p.put(crown(), 50, 17 + (pop_dy(L.age("King"), 0.14, 8) or 0))
    p.silk((50, 28), "KING OF THE", "cream", anchor="ma")
    p.press((50, 38), "LOST BOYS", "gold", anchor="ma", shadow="wood_sh")
    p.silk((50, 51), "NO GROWN-UPS", "cream", anchor="ma")
    a = L.age("nine")
    if a >= 0:
        p.put(cake(), 38, 77 + (pop_dy(a, 0.12, 8) or 0))
        p.tag((56, 78), "AGAIN", "red", "white")
    return p


def neverland(L):
    """He jetted to Japan and renamed it."""
    p = Pic("sky")
    p.grad((0, 0, PW, 46), "sky", "sky_hi")
    p.rect((0, 46, PW, PH), "sea")
    for i in range(6):
        p.line([(6 + 17 * i, 50 + (i % 2) * 3), (13 + 17 * i, 50 + (i % 2) * 3)], "sea_hi")
    p.ell((40, 34, 98, 62), "grass"); p.ell((54, 28, 84, 50), "grass_sh")   # the island
    p.rect((40, 48, 98, 62), "sea"); p.line([(42, 47), (96, 47)], "cream")
    p.line([(68, 12), (68, 30)], "ink")                                # the flag
    p.box((69, 12, 85, 23), "white"); p.ell((74, 15, 80, 21), "red")
    a_j = L.age("jetted")
    if 0 <= a_j < 1.2:                                                 # the jet comes in
        k = ease_out(a_j / 1.0)
        p.put(plane(), lerp(-12, 52, k), lerp(8, 30, k))
        for i in range(4):
            p.px((lerp(-12, 52, k) - 12 - 4 * i, lerp(8, 30, k) - 2 - i), "white")
    p.rect((48, 64, 51, 92), "wood_sh")                                # the signpost
    p.box((8, 62, 92, 90), "wood")
    p.press((50, 66), "JAPAN", "cream", anchor="ma", shadow="wood_sh")
    a_r, a_n = L.age("renamed"), L.age("Neverland")
    if a_r >= 0:
        p.line([(26, 70), (26 + int(48 * k_in(a_r, 0.2)), 69)], "red_hi", w=2)
    if a_n >= 0:
        p.press((50, 78 + (pop_dy(a_n, 0.12, 5) or 0)), "NEVERLAND", "gold", anchor="ma", shadow="wood_sh")
    return p


def bot_fair(L):
    """Peter Pan built a bot. Nice try."""
    p = Pic("cream")
    p.rect((0, 76, PW, PH), "paper_sh")
    p.put(box_bot(), 36, 49)
    if int(L.t * 6) % 6 == 0:                                          # it twitches
        p.line([(31, 22), (33, 20)], "warn"); p.line([(40, 22), (38, 20)], "warn")
    a = L.age("Nice")
    if a >= 0:
        dy = pop_dy(a, 0.12, 8) or 0
        p.put(rosette("", "blue", r=17), 75, 42 + dy)
        p.silk((76, 28 + dy), "NICE", "blue_sh", anchor="ma")
        p.silk((76, 35 + dy), "TRY", "blue_sh", anchor="ma")
    p.tag((50, 84), "HOME-MADE A.I.", "ink", "white", "ma")
    return p


def qwen_wig(L):
    """A Qwen in a wig, lip-syncing."""
    p = Pic("night")
    p.poly([(38, 0), (62, 0), (88, PH), (12, PH)], "night_hi")          # the spotlight
    a = L.age("lip")
    talk = (1 + int(L.t * 9) % 3) if a >= 0 else 0
    p.orb(50, 46, 20, "open", talk, "qwen")
    p.put(wig(), 49, 33)
    p.rect((48, 70, 51, 86), "steel_sh"); p.ell((45, 62, 54, 71), "grey")  # a mic
    p.tag((4, 4), "QWEN", "purple", "white")
    if a >= 0:
        p.rect((6, 76, 93, 93), "bar")
        p.poly([(11, 80), (11, 89), (18, 84)], "gpt_glow")
        p.silk((24, 78), "NOW PLAYING:", "dim")
        p.silk((24, 86), "CHATGPT.MP3", "text")
    return p


def listing(L):
    """Where the bot came from: a marketplace listing."""
    p = Pic("white")
    p.rect((0, 0, PW, 12), "orange")
    p.press((50, 2), "ALIBABA", "white", anchor="ma", shadow="red_sh")
    p.box((5, 17, 39, 51), "paper_sh", "grey")
    p.orb(22, 34, 12, "open", 0, "qwen")
    p.silk((44, 18), "A.I. MODEL", "ink")
    p.silk((44, 26), "(QWEN)", "purple_sh")
    p.silk((44, 36), "WEIGHTS:", "grey")
    p.silk((44, 44), "FREE", "green_sh")
    for i in range(5):                                                 # five stars
        x = 6 + 8 * i
        p.poly([(x + 3, 56), (x + 4, 59), (x + 7, 59), (x + 5, 61), (x + 6, 64), (x + 3, 62), (x, 64), (x + 1, 61),
                (x - 1, 59), (x + 2, 59)], "gold")
    p.silk((50, 58), "(9,999)", "grey")
    p.silk((6, 68), "MIN. ORDER: 1", "grey")
    a = L.age("my")
    p.rbox((14, 78, 85, 91), "orange" if a < 0 or a > 0.15 else "red", "ink")
    p.silk((50, 82), "ADD TO CART", "white", anchor="ma")
    return p


def manual(a):
    """The assembly instructions."""
    p = Pic("white")
    p.rect((0, 0, PW, 15), "blue")
    p.press((50, 4), "AJAX", "yellow", anchor="ma")
    umlaut(p.img, 50 - 16, 4, "yellow")
    # the man from every manual: a round head, a smile, an Allen key
    p.d.ellipse((10, 22, 24, 36), outline=p.c("ink")); p.px((15, 27), "ink"); p.px((20, 27), "ink")
    p.line([(15, 31), (17, 32), (19, 31)], "ink")
    p.line([(17, 36), (17, 54)], "ink"); p.line([(17, 54), (11, 66)], "ink"); p.line([(17, 54), (23, 66)], "ink")
    p.line([(17, 42), (8, 48)], "ink"); p.line([(17, 42), (28, 40)], "ink")
    p.line([(28, 40), (28, 34), (33, 34)], "steel_sh", w=2)            # the key
    p.silk((36, 20), "1x", "ink"); p.d.ellipse((50, 18, 62, 30), outline=p.c("ink"))
    p.silk((36, 36), "1x", "ink"); p.d.chord((50, 34, 64, 50), 180, 360, outline=p.c("ink"))
    p.line([(57, 42), (57, 47)], "ink")
    p.silk((36, 56), "400x", "ink")
    for i in range(3):
        p.line([(66 + 7 * i, 56), (66 + 7 * i, 62)], "ink"); p.line([(64 + 7 * i, 56), (68 + 7 * i, 56)], "ink")
    p.d.ellipse((72, 20, 92, 40), outline=p.c("ink"))                  # a thought: ?
    p.press((79, 26), "?", "ink")
    p.line([(8, 72), (92, 72)], "paper_ln")
    p.silk((50, 77), "IKEA SCI-FI", "blue_sh", anchor="ma")
    p.silk((50, 85), "SOME ASSEMBLY", "grey", anchor="ma")
    return p


def flatpack(L):
    """Flat-packed and shipped from Shanghai."""
    p = Pic("sea_hi")
    p.rect((0, 62, PW, PH), "stone"); p.line([(0, 62), (PW, 62)], "stone_sh")
    a_s = L.age("shipped")
    x = 50 + (int((1 - ease_out(k_in(a_s + 0.15, 0.3))) * 100) if a_s < 0.2 else 0)
    p.put(flat_box(84, 18), x, 46)
    p.press((x - 40, 43), "AJAX", "brown_sh")
    umlaut(p.img, x - 40, 43, "brown_sh")
    if a_s >= 0.1:                                                     # the shipping label
        p.box((x + 8, 40, x + 38, 55), "white")
        p.silk((x + 11, 42), "FROM:", "grey")
        p.silk((x + 11, 48), "CHINA", "ink")
    if L.on("Shanghai"):
        p.tag((50, 70), "ORIGIN: SHANGHAI", "ink", "white", "ma")
        p.tag((50, 81), "SELF-ASSEMBLY", "red_sh", "white", "ma")
    return p


# --- the gags ---------------------------------------------------------------------------------------

@gag("v1", 0)
def three_words(c, L):
    show(c, nursery(L), "EXHIBIT A", L.age())
    yield "front"


@gag("v1", 1)
def whole_resume(c, L):
    show(c, resume(L), "EXHIBIT B", L.age())
    yield "front"


@gag("v1", 2)
def hot_dogs_then_toys(c, L):
    show(c, odd_jobs(L), "CAREER", L.age())
    yield "front"


@gag("v1", 3)
def best_paid_babysitter(c, L):
    show(c, babysitter(L), "CAREER", L.age())
    yield "front"


def board(c, a):
    p, n = history(c.t)
    show(c, p, f"WON 0   LOST {n}", a)


@gag("v1", 4)
def lost_to_a_barrel(c, L):
    board(c, L.age())
    yield "front"


@gag("v1", 5)
def lost_to_a_baby(c, L):
    board(c, 1.0)
    yield "front"


@gag("v1", 6)
def lost_disney(c, L):
    board(c, 1.0)
    yield "front"


@gag("v1", 7)
def language(c, L):
    a = L.age("Felix")
    board(c, 1.0)
    if a >= 0:
        show(c, warning(a), "CONTENT WARNING", a)
        pose(c, "sam", arms="finger", brows="up", eyes="half")
    if L.age("language") > 0.3:
        pose(c, "felix", eyes="down")
    yield "front"


CAP_ON, CAP_OFF = when("v1", 8, "King"), when("v1", 11)


@span(CAP_ON, CAP_OFF)
def peter_pan(c, L):
    """Felix in Peter Pan's cap, from the Lost Boys until the bot."""
    a = c.t - CAP_ON
    pose(c, "felix", hat=(pan_cap(), -9 + (pop_dy(a, 0.14, 12) or 0)), brows="angry", eyes="side")
    yield "front"


@gag("v1", 8)
def king_of_the_lost_boys(c, L):
    show(c, lost_boys(L), "THE FANS", L.age())
    yield "front"


@gag("v1", 9)
def renamed_it_neverland(c, L):
    show(c, neverland(L), "HOME", L.age())
    yield "front"


@gag("v1", 10)
def nice_try(c, L):
    show(c, bot_fair(L), "SCIENCE FAIR", L.age())
    yield "front"


@gag("v1", 11)
def qwen_in_a_wig(c, L):
    show(c, qwen_wig(L), "AJAX, UNMASKED", L.age())
    yield "front"


@gag("v1", 12)
def ikea_sci_fi(c, L):
    a = L.age("IKEA")
    show(c, listing(L), "SOURCE", L.age())
    if a >= 0:
        show(c, manual(a), "INSTRUCTIONS", a)
    yield "front"


@gag("v1", 13, post=1.0)
def pew_d_i_y(c, L):
    a = L.age("Pew")
    show(c, flatpack(L), "DELIVERY", L.age())
    yield "front"
    shout(c, 160, 44, "PEW-", a)
    shout(c, 160, 64, "D-I-Y", a - 0.12)
