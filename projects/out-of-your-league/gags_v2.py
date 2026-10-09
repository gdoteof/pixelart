"""Verse 2: Maya, on her stream from the barn, with Emiru on a call. The brags are a gangster's and every
one is the sanctuary: the beef is a cow, the glove holds a hawk, the snake in her circle is called Noodle."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403


# --- 0-1: the beef ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def winnie_card(stage, chew):
    p = Pic("cream")
    if stage == 0:
        p.rect((0, 0, PW, PH), "night")
        p.big((PW // 2, 8), "WANT", "red_hi", "red"); p.big((PW // 2, 27), "BEEF?", "red_hi", "red")
        return p.img
    p.header("FIELD GUIDE", "maya_sh", "white", h=9)
    p.rect((1, 12, 52, 47), "pasture"); p.rect((1, 12, 52, 28), "sky_hi"); p.d.rectangle((1, 12, 52, 47), outline=INK)
    p.put(animals.winnie(chew), 27, 32)
    p.tag((55, 12), "WINNIE", "angus", "white")
    if stage >= 2:
        p.silk((56, 25), "HERD:", "wood_sh"); p.press((97, 23), "1", "live", anchor="ra")
    if stage >= 3:
        p.silk((56, 34), "RED", "angus"); p.silk((56, 41), "ANGUS", "angus")
    return p.img


@gag("v2", 0)
def want_beef(c, L):
    stage = 3 if L.on("Red") else 2 if L.on("one") else 1 if L.on("Meet") else 0
    show(c, winnie_card(stage, int(c.t * 2.2) % 2), "BEEF", "MOO")
    if L.on("Meet") and not L.on("one"):
        pose(c, "maya", arms="window", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def cash_cow(stage, n, chew):
    p = Pic("sky_hi")
    p.sky(30); p.ground(30)
    p.fence(27)
    p.put(animals.winnie(chew), 30, 32)
    x = 68                                                               # the feeder chat pays into
    p.rect((x + 3, 20, x + 6, 44), "steel_sh"); p.rect((x - 4, 10, x + 13, 26), "maya_sh")
    p.d.rectangle((x - 4, 10, x + 13, 26), outline=INK)
    p.rect((x - 1, 13, x + 10, 19), "bg"); p.silk((x + 5, 14), "$5", "ok", anchor="ma")
    p.poly([(x - 4, 27), (x - 10, 32), (x - 4, 32)], "steel")
    if stage >= 1:
        p.rbox((36, 2, 62, 13), "white", "ink", 3); p.poly([(44, 13), (48, 13), (44, 17)], "white")     # she moos
        p.press((49, 4), "MOO", "ink", anchor="ma")
    if stage >= 2:
        for i in range(min(n, 6)):                                       # and it rains
            p.coin(84 + (i % 3) * 6 - 3 * (i // 3), 8 + 7 * (i // 3) + 3 * (i % 2), 3)
        p.pxs([(x - 9, 34), (x - 7, 36), (x - 11, 37), (x - 8, 39)], "hay")
        p.tag((2, 44), "$%d,%03d" % (41 + n // 2, (n * 137) % 1000), "ink", "ok")
    if stage >= 3:
        p.tag((PW - 2, 44), "FAMOUS", "gold", "ink", anchor="ra")
    return p.img


@gag("v2", 1)
def cash_cow_famous(c, L):
    stage = 3 if L.on("famous") else 2 if L.on("pays") else 1 if L.on("moos") else 0
    show(c, cash_cow(stage, int(max(L.age("pays"), 0) * 6), int(c.t * 2.2) % 2), "FEEDER CAM", "LIVE")
    typed(c, "WINNIEMOO", "$5 MOO", L.age("pays"), "ok")
    typed(c, "MOOMOO", "$5 :cow:", L.age("pays") - 0.4, "ok")
    typed(c, "HAYBALE", "$5 FEED HER", L.age("cash"), "ok")
    yield "front"
    say(c, 168, 74, "MOO", L.age("moos"), 0.9)
    alert(c, L.age("pays"), "WINNIEMOO: $5", "FEEDER: 1 SNACK", icon="coin", dur=2.4)


# --- 2-3: famous ------------------------------------------------------------------------------------------

def glove_pic(p, x, y, color, shade, sparkle):
    """A glove, fingers up, 18 x 26, its top left at (x, y)."""
    for i in range(4):
        p.rect((x + 2 + 4 * i, y + (2 if i in (0, 3) else 0), x + 4 + 4 * i, y + 12), color)
    p.rect((x + 1, y + 10, x + 16, y + 20), color); p.rect((x + 3, y + 20, x + 14, y + 25), shade)
    p.poly([(x + 16, y + 12), (x + 20, y + 9), (x + 21, y + 12), (x + 16, y + 18)], color)
    if sparkle:
        p.pxs([(x + 3, y + 4), (x + 8, y + 2), (x + 12, y + 6), (x + 5, y + 13), (x + 11, y + 15), (x + 14, y + 11),
               (x + 7, y + 18)], "white")
        p.pxs([(x - 2, y + 1), (x + 20, y + 3), (x - 3, y + 15)], "gold_hi")


@lru_cache(maxsize=None)
def one_glove(stage):
    p = Pic("night")
    p.poly([(14, 0), (38, 0), (48, 46), (4, 46)], "night_hi")                              # a spotlight
    p.rect((0, 46, PW, PH), "black")
    glove_pic(p, 17, 10, "white", "grey_hi", True)
    p.tag((2, 43), "HIS", "ink", "dim")
    if stage >= 1:
        p.rect((52, 0, PW, PH), "sky_hi"); p.rect((52, 38, PW, PH), "pasture")
        glove_pic(p, 58, 24, "glove", "glove_sh", False)
        p.tag((PW - 2, 43), "MINE", "maya", "ink", anchor="ra")
    if stage >= 2:
        p.put(animals.hawk(), 68, 12)
    return p.img


@gag("v2", 2)
def mine_holds_a_hawk(c, L):
    stage = 2 if L.on("hawk") else 1 if L.on("glove") else 0
    show(c, one_glove(stage), "ONE GLOVE", "VS")
    if L.on("mine"):                                                     # and here she is
        c.bird = False
        c.st["maya"]["outfit"] = "glove"
        hold_up(c, "maya", mirror(animals.hawk(1 if L.on("hawk") else 0, 1 if 0 <= L.age("mine") < 0.25 else 0)), 3)
        pose(c, "maya", eyes="side", brows="up", mouth="grin" if L.age("hawk") > 0.4 else c.st["maya"]["mouth"])
    yield "front"


@lru_cache(maxsize=None)
def ted_pic(stage):
    p = Pic("black")
    if stage == 0:
        p.rect((0, 0, PW, PH), "panel")
        for i, (x, y) in enumerate(((12, 8), (52, 4), (30, 26), (66, 30))):                 # talk, talk, talk
            p.rbox((x, y, x + 30, y + 13), "white" if i % 2 else "grey_hi", "ink", 3)
            p.silk((x + 15, y + 4), "TALK", "ink", anchor="ma")
        return p.img
    p.poly([(30, 0), (70, 0), (92, 52), (8, 52)], "night_hi")
    p.ell((14, 36, 86, 58), "red"); p.ell((20, 39, 80, 56), "red_hi")                       # the round red rug
    p.put(mug("maya", "open", "up", "grin"), 50, 28)
    p.rect((44, 42, 56, 50), "olive")
    p.press((4, 3), "TALK", "red", shadow="ink")
    p.rect((64, 4, 96, 24), "white"); p.d.rectangle((64, 4, 96, 24), outline=col("grey"))   # her slide
    p.put(animals.chinchilla(), 80, 14)
    p.silk((80, 27), "1/40", "dim", anchor="ma")
    return p.img


@gag("v2", 3)
def ted_talk(c, L):
    show(c, ted_pic(1 if L.on("give") else 0), "KEYNOTE", "18:00")
    if L.on("give"):
        pose(c, "maya", arms="chest", brows="up")
    yield "front"


# --- 4-6: the crew -----------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def backyard(stage):
    p = Pic("sky")
    p.sky(26); p.ground(26)
    p.rect((0, 12, PW, 13), "tree"); p.ell((4, 4, 26, 20), "tree"); p.ell((70, 2, 98, 20), "tree_sh")
    p.put(animals.wolf(), 22, 30); p.put(mirror(animals.wolf()), 78, 30)
    if stage >= 1:
        for x in (8, 44, 58, 92):                                        # spring
            p.px((x, 44), "pink"); p.px((x + 1, 43), "yellow"); p.px((x - 1, 43), "pink"); p.line([(x, 45), (x, 47)], "tree")
        p.heart(48, 16, "red")
        p.tag((PW // 2, 2), "SPRING", "pink", "ink", anchor="ma")
    if stage >= 2:
        for i, x in enumerate((40, 50, 60)):                              # and three more
            p.put(scaled(animals.wolf(), 0.5), x, 41 - (i % 2))
    p.fence(46, step=14)
    return p.img


@gag("v2", 4)
def wolves_breeding(c, L):
    show(c, backyard(2 if L.on("breeding") else 1 if L.on("spring") else 0), "BACKYARD", "CAM 2")
    yield "front"


def snake_coil(p, x, y, fed):
    """A ball python coiled up, about 34 x 18, centred on (x, y): `fed` gives her a lump to show for it."""
    pts = []
    for i in range(0, 41):                                               # two turns, winding in
        a = i / 40 * 4 * math.pi
        r = 1 - 0.62 * i / 40
        pts.append((x + 15 * r * math.cos(a), y + 3 + 7 * r * math.sin(a)))
    head = [(x + 15, y + 3), (x + 18, y - 3), (x + 17, y - 8)]
    for color, w in ((INK, 7), ("snake", 5)):
        p.d.line(pts, fill=col(color) if isinstance(color, str) else color, width=w, joint="curve")
        p.d.line(head, fill=col(color) if isinstance(color, str) else color, width=w, joint="curve")
    for i in range(2, 40, 4):                                            # her blotches
        px_, py_ = pts[i]
        p.rect((int(px_) - 1, int(py_) - 1, int(px_), int(py_)), "snake_sh")
    if fed:
        fx_, fy_ = pts[4]
        p.ell((int(fx_) - 4, int(fy_) - 4, int(fx_) + 4, int(fy_) + 4), "snake")
        p.d.ellipse((int(fx_) - 4, int(fy_) - 4, int(fx_) + 4, int(fy_) + 4), outline=INK)
    p.ell((x + 13, y - 13, x + 21, y - 6), "snake"); p.d.ellipse((x + 13, y - 13, x + 21, y - 6), outline=INK)   # her head
    p.px((x + 18, y - 10), "ink"); p.line([(x + 21, y - 9), (x + 24, y - 10)], "red"); p.px((x + 25, y - 11), "red")


@lru_cache(maxsize=None)
def circle_pic(stage):
    p = Pic("panel")
    p.header("MY CIRCLE", "bar", "maya_hi", h=9)
    cx, cy = 50, 30
    p.d.ellipse((cx - 40, cy - 17, cx + 40, cy + 19), outline=col("line"))
    for i, (dx, dy) in enumerate(((-40, 2), (-24, -13), (24, -13), (40, 2))):
        x, y = cx + dx, cy + dy
        p.ell((x - 6, y - 6, x + 6, y + 6), ("emiru", "sky", "gold", "purple")[i]); p.d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=INK)
        p.ell((x - 2, y - 4, x + 2, y), "white"); p.rect((x - 3, y + 1, x + 3, y + 4), "white")
    snake_coil(p, cx - 2, cy + 3, stage >= 2)
    if stage >= 1:
        p.tag((cx, cy + 14), "NOODLE", "snake", "ink", anchor="ma")
    if stage >= 2:
        p.tag((cx, cy - 20), "FED", "ok", "ink", anchor="ma")
    return p.img


@gag("v2", 5)
def snake_in_my_circle(c, L):
    show(c, circle_pic(2 if L.on("feeding") else 1 if L.on("Noodle") else 0), "FRIENDS", "5")
    yield "front"


@lru_cache(maxsize=None)
def vitals(stage, f):
    p = Pic("bg")
    p.header("VITALS", "bar", "ok", h=9)
    p.put(animals.chinchilla(), 14, 22)
    p.silk((28, 14), "CHINCHILLA", "text")
    for x in range(4, 96):                                               # a heartbeat, scrolling
        k = (x + f * 4) % 24
        y = 38 + {8: -2, 9: -9, 10: 6, 11: -3}.get(k, 0)
        p.px((x, y), "ok")
        if k in (9, 10):
            p.line([(x, 38), (x, y)], "ok")
    if stage >= 1:
        p.silk((28, 22), "BREATHING", "ok"); p.tick(86, 20, "ok")
    return p.img


@gag("v2", 6)
def still_breathing(c, L):
    show(c, vitals(1 if L.on("still") else 0, c.f // 2 % 6), "SHOULDER CAM", "BPM")
    if L.on("breathing"):
        pose(c, "maya", eyes="side", brows="up")
    yield "mid"
    on_shoulder(c, "maya", animals.chinchilla(1 if (c.t % 1.7) < 0.12 else 0), dy=int(pop_dy(L.age(), 0.14, 6) or 0))
    yield "front"


# --- 7-8: booked ------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def kai_call(stage, ring):
    p = Pic("bg")
    p.rbox((1, 1, PW - 2, PH - 4), "panel", "line", 4)
    p.silk((PW // 2, 4), "INCOMING CALL", "dim", anchor="ma")
    p.press((PW // 2, 11), "KAI CENAT", "white", anchor="ma", shadow="ink")
    p.silk((PW // 2, 23), "RE: PROFESSOR?", "gold", anchor="ma")
    if stage < 2:
        round_btn(p, 34, 39, "live", "no"); round_btn(p, 66, 39, "ok", "yes")
        if ring:
            p.d.arc((58, 31, 76, 47), -60, 60, fill=col("ok"))
        if stage == 1:
            p.d.ellipse((27, 32, 41, 46), outline=col("white"))             # her thumb is on the red one
    else:
        p.verdict(PW // 2, 39, "VOICEMAIL", "live", "bg")
    return p.img


@gag("v2", 7)
def straight_to_voicemail(c, L):
    stage = 2 if L.on("voicemail") else 1 if L.on("Straight") else 0
    show(c, kai_call(stage, int(c.t * 5) % 2), "PHONE", "CALL")
    if L.on("Straight") and L.age("Straight") < 0.5:
        pose(c, "maya", arms="click", eyes="down")
    yield "front"


def whale_tail(p, x, y):
    """A sperm whale's flukes going under, 30 wide, centred on x, the waterline at y."""
    p.poly([(x - 3, y), (x - 2, y - 10), (x - 15, y - 17), (x - 8, y - 19), (x, y - 14), (x + 8, y - 19), (x + 15, y - 17),
            (x + 2, y - 10), (x + 3, y)], "stone_sh")
    p.line([(x - 12, y - 17), (x - 3, y - 13)], "stone"); p.line([(x + 12, y - 17), (x + 3, y - 13)], "stone")
    p.pxs([(x - 6, y - 1), (x + 6, y - 2), (x - 9, y + 1), (x + 9, y)], "white")


@lru_cache(maxsize=None)
def booked_pic(stage, f):
    if stage == 0:
        p = Pic("paper")
        p.header("THIS MONTH", "red", "white", h=9)
        for i in range(21):
            x, y = 4 + 13 * (i % 7), 12 + 13 * (i // 7)
            p.rect((x, y, x + 11, y + 11), "paper_sh"); p.cross(x + 5, y + 5, "live", 3)
        return p.img
    p = Pic("sky")
    p.sky(24, "sky", "sky_hi")
    p.rect((0, 24, PW, PH), "sea"); p.rect((0, 34, PW, PH), "sea_sh")
    for x in range(0, PW, 9):
        p.line([(x + (f % 3), 28), (x + 4 + (f % 3), 28)], "sea_hi"); p.line([(x + 5 - (f % 3), 40), (x + 8 - (f % 3), 40)], "sea")
    whale_tail(p, 66, 27 + (f % 2))
    p.poly([(8, 25), (34, 25), (30, 31), (11, 31)], "white"); p.d.polygon([(8, 25), (34, 25), (30, 31), (11, 31)], outline=INK)   # the boat
    p.put(mug("maya", "open", "up", "grin", 3), 21, 16)
    if stage >= 2:
        p.tag((PW // 2, 44), "BOOKED SOLID", "ink", "gold", anchor="ma")
    return p.img


@gag("v2", 8)
def saving_sperm_whales(c, L):
    stage = 2 if L.on("whales") else 1 if L.on("out") else 0
    show(c, booked_pic(stage, c.f // 4 % 6 if stage else 0), "CALENDAR" if stage == 0 else "DOMINICA", "BUSY")
    if L.on("sorry") and not L.on("booked"):
        pose(c, "maya", arms="shrug", brows="up", eyes="half")
    yield "front"


# --- 9-10: Jason -------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def alpaca(blink=0):
    """An alpaca, facing right (26 x 34): mostly neck and fluff."""
    f = Canvas(28, 36)
    f.rect((6, 26, 8, 34), "cream"); f.rect((16, 26, 18, 34), "cream")
    f.ell((2, 15, 22, 29), "white"); f.ell((4, 21, 20, 29), "cream")
    f.rect((16, 6, 22, 20), "white"); f.line([(17, 8), (17, 18)], "cream")
    f.ell((14, 0, 25, 9), "white"); f.rect((21, 5, 27, 9), "cream")                       # the head, the topknot, the muzzle
    f.poly([(15, 2), (16, -2), (18, 1)], "white")
    f.px((27, 7), "ink"); f.line([(24, 9), (26, 9)], "wood_sh")
    if blink:
        f.line([(21, 4), (22, 4)], "ink")
    else:
        f.rect((21, 3, 22, 4), "ink")
    return f.done()


@lru_cache(maxsize=None)
def alpaca_receipt(n):
    p = Pic("panel")
    p.rect((34, 0, PW - 3, PH), "paper")
    for x in range(34, PW - 3, 4):                                       # the torn edge
        p.poly([(x, PH - 3), (x + 2, PH - 6), (x + 4, PH - 3)], "panel")
    p.put(alpaca(), 17, 30)
    p.silk((65, 3), "RENTAL", "ink", anchor="ma"); p.line([(38, 10), (93, 10)], "paper_sh")
    rows = (("ALPACA", "X1"), ("FOR", "JASON"), ("IDEAS", "0"))
    for i, (k, v) in enumerate(rows[:n]):
        p.silk((38, 14 + 9 * i), k, "grey_sh"); p.silk((93, 14 + 9 * i), v, "live" if i == 2 else "ink", anchor="ra")
    return p.img


@gag("v2", 9)
def jason_rents_an_alpaca(c, L):
    show(c, alpaca_receipt(count(L, "rents", "alpaca", "ideas") or 0), "RECEIPT", "PAID")
    if L.on("thin"):
        pose(c, "maya", arms="pinch", eyes="half", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def brain_clip(stage):
    p = Pic("bg")
    if stage < 2:
        p.put(mug("maya", "half" if stage else "open", "skeptic", "open" if stage == 0 else "closed"), 22, 28)
        p.rbox((40, 6, 96, 30), "white", "ink", 4); p.poly([(40, 20), (34, 24), (40, 26)], "white")
        p.silk((68, 11), "USE YOUR", "ink", anchor="ma"); p.press((68, 18), "BRAIN.", "ink", anchor="ma")
        if stage == 1:
            p.tag((68, 38), "CALL ENDED", "live", "white", anchor="ma")
    else:
        p.header("TOP CLIPS", "bar", "gold", h=9)
        p.rect((4, 13, 40, 34), "panel_hi"); p.put(mug("maya", "half", "skeptic", "closed", 3), 22, 24)
        p.d.rectangle((4, 13, 40, 34), outline=col("gold"))
        p.press((45, 13), "#1", "gold_hi", shadow="ink")
        p.silk((45, 24), "HIS BEST", "text"); p.silk((45, 31), "WORK", "text")
        p.tag((4, 40), "2.1M VIEWS", "ink", "gold")
    return p.img


@gag("v2", 10)
def use_your_brain(c, L):
    stage = 2 if L.on("best") else 1 if L.on("hung") else 0
    show(c, brain_clip(stage), "CLIP" if stage < 2 else "LEADERBOARD", "CALL" if stage < 2 else "#1")
    if not L.on("hung"):
        pose(c, "maya", arms="finger", brows="skeptic", eyes="half")
    elif stage == 1:
        pose(c, "maya", arms="click", eyes="down")
    yield "front"
    jolt(c, L.age("hung"), 2)


# --- 11-12: Lacy -------------------------------------------------------------------------------------------

def gecko(p, x, y, color="maya", flip=False):
    """A gecko from above, 14 x 8, centred on (x, y)."""
    s = -1 if flip else 1
    p.ell((x - 5, y - 2, x + 3, y + 2), color); p.ell((x + s * 3 - 2, y - 3, x + s * 3 + 3, y + 2), color)
    p.line([(x - s * 4, y), (x - s * 8, y + 2), (x - s * 9, y - 1)], color)
    for dx in (-3, 2):
        p.line([(x + dx, y - 2), (x + dx - 1, y - 4)], color); p.line([(x + dx, y + 2), (x + dx - 1, y + 4)], color)
    p.px((x + s * 4, y - 2), "ink"); p.px((x, y), "yellow"); p.px((x - 2, y - 1), "yellow")


@lru_cache(maxsize=None)
def gecko_tank(days, stage):
    p = Pic("panel")
    p.rect((2, 6, 48, 46), "tree_sh"); p.rect((2, 36, 48, 46), "dirt")                      # the tank
    p.line([(6, 36), (16, 20), (30, 24)], "wood", w=2); p.ell((30, 30, 44, 40), "stone")
    gecko(p, 18, 17); gecko(p, 37, 29, "orange", True)
    p.d.rectangle((2, 6, 48, 46), outline=col("steel")); p.rect((2, 3, 48, 6), "black")
    p.silk((75, 3), "DAYS", "dim", anchor="ma")
    for i in range(min(days, 7)):                                        # the tally
        if i in (4,):
            continue
        p.line([(62 + 4 * i, 11), (62 + 4 * i, 22)], "text")
    if days >= 5:
        p.line([(60, 20), (76, 13)], "text")
    if days >= 7:
        p.silk((75, 26), "A WEEK", "live", anchor="ma")
    if stage:
        p.rbox((52, 34, 98, 50), "ok", "ink", 3)
        p.silk((75, 36), "MAYA", "ink", anchor="ma"); p.silk((75, 43), "CALLING", "ink", anchor="ma")
    return p.img


@gag("v2", 11)
def lacys_geckos(c, L):
    days = 0 if not L.on("did") else min(7, 1 + int(L.age("did") / 0.07))
    show(c, gecko_tank(days, 1 if L.on("called") else 0), "LACY'S TANK", "DAY %d" % max(days, 1))
    if L.on("called"):
        pose(c, "maya", arms="ear", eyes="side", brows="skeptic")
    yield "front"


@lru_cache(maxsize=None)
def oath_pic(stage, blink):
    p = Pic("bg")
    p.rect((0, 0, PW, PH), "panel")
    # somebody with his hand up: nobody's face, a shape in a hoodie
    p.poly([(26, 52), (28, 34), (38, 28), (52, 28), (62, 34), (64, 52)], "grey_sh"); p.ell((36, 10, 54, 30), "grey")
    p.rect((66, 14, 72, 40), "grey_sh")
    p.rect((64, 4, 74, 16), "eskin_sh")
    for i in range(4):
        p.rect((64 + 3 * i, 0, 65 + 3 * i, 5), "eskin_sh")
    p.d.rectangle((2, 2, PW - 3, PH - 5), outline=col("text"))                              # the viewfinder
    if blink:
        p.ell((6, 6, 10, 10), "live")
    p.silk((13, 6), "REC", "live")
    if stage >= 1:
        p.tag((3, 40), "NO MORE PETS", "ink", "text")
    if stage >= 2:
        p.verdict(72, 30, "LIFE")
    return p.img


@gag("v2", 12)
def he_got_life(c, L):
    stage = 2 if L.on("life") else 1 if L.on("more") else 0
    show(c, oath_pic(stage, int(c.t * 2) % 2), "SWORN IN", "REC")
    if L.on("hand") and not L.on("camera"):
        pose(c, "maya", arms="wave", brows="neutral", mouth="closed")
    if L.on("life"):
        pose(c, "maya", arms="shrug", brows="up")
    yield "front"
    jolt(c, L.age("life"), 2)


# --- 13-14: I wish you would --------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def night_fence(n, hand):
    p = Pic("night")
    p.rect((0, 0, PW, 30), "night"); p.rect((0, 30, PW, PH), "black")
    p.ell((78, 4, 90, 16), "paper"); p.ell((82, 3, 92, 13), "night")                        # a moon
    for i, (x, y) in enumerate(((56, 20), (78, 25), (40, 27), (88, 36), (64, 36))[:n]):     # and who is awake
        p.poly([(x - 5, y + 9), (x - 4, y - 3), (x - 2, y - 7), (x, y - 3), (x + 6, y - 3), (x + 8, y - 7), (x + 10, y - 3),
                (x + 11, y + 9)], "night_hi")
        p.rect((x, y, x + 1, y + 1), "gold_hi"); p.rect((x + 5, y, x + 6, y + 1), "gold_hi")
        p.px((x + 1, y + 1), "gold"); p.px((x + 6, y + 1), "gold")
    for x in range(2, PW, 7):                                            # chain link
        p.line([(x, 8), (x, 46)], "grey_sh")
    for y in range(10, 46, 6):
        p.line([(0, y), (PW, y)], "grey_sh")
    p.rect((30, 4, 32, 48), "steel_sh")
    if hand:                                                             # a hand, having a think
        p.rect((0, 30, 12 + hand, 35), "eskin_sh")
        for i in range(3):
            p.rect((12 + hand, 29 + 2 * i, 17 + hand, 30 + 2 * i), "eskin_sh")
    return p.img


@gag("v2", 13)
def reach_for_my_wolves(c, L):
    n = 1 + count(L, "wolves", "night", "think", "could")
    hand = 0 if not L.on("Reach") else 8 if not L.on("think") else max(0, 8 - int(L.age("think") / 0.08))
    show(c, night_fence(n, hand if L.on("Reach") and not L.on("could") else 0), "NIGHT CAM", "3 AM")
    if L.on("think"):
        pose(c, "maya", arms="chin", eyes="half", brows="up", mouth="smirk")
    yield "front"


@lru_cache(maxsize=None)
def wish_pic(stage):
    p = Pic("blue_sh")
    p.grad((0, 0, PW, PH), "blue", "blue_sh", steps=4)
    if stage == 0:
        p.poly([(50, 2), (53, 10), (61, 10), (55, 15), (57, 23), (50, 18), (43, 23), (45, 15), (39, 10), (47, 10)], "white")
        p.line([(50, 18), (40, 34)], "white", w=2)                        # a star on a wand
        p.poly([(10, 46), (14, 34), (86, 34), (90, 46)], "wood_hi"); p.d.polygon([(10, 46), (14, 34), (86, 34), (90, 46)], outline=INK)
        p.silk((50, 38), "M. HIGA: BOARD", "ink", anchor="ma")
        return p.img
    p.pxs([(8, 6), (90, 10), (20, 44), (84, 42), (50, 3), (70, 46)], "white")
    p.silk((PW // 2, 5), "I WISH", "white", anchor="ma")
    p.big((PW // 2, 13), "YOU", "gold_hi", "gold"); p.big((PW // 2, 30), "WOULD", "gold_hi", "gold")
    return p.img


@gag("v2", 14)
def i_wish_you_would(c, L):
    show(c, wish_pic(1 if L.on("wish", 1) else 0), "BOARD SEAT", "WISH")
    if L.on("wish", 1):
        pose(c, "maya", arms="palm" if L.age("would") < 0 else "shrug", brows="up", eyes="half",
             mouth="smirk" if L.age("would") > 0.5 else c.st["maya"]["mouth"])
    yield "front"
    jolt(c, L.age("would"), 3)
