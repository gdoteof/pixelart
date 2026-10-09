"""Verse 1: Emiru, on her stream, with Maya on a call. Every gangster brag is true, once you see what she
pulls up in the window: the heat on her hip is a glue gun, the bodies are ranked, the athlete is sitting."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403

WIG_COLORS = ("pink", "blue", "gold", "white", "red", "teal", "lilac", "orange", "green", "ears")


# --- 0-1: the E stands for equity ------------------------------------------------------------------------

@lru_cache(maxsize=None)
def egirl_pic(stage):
    p = Pic("panel")
    p.big((PW // 2, 3), "E-GIRL", "emiru_hi", "emiru")
    if stage >= 1:
        p.line([(22, 12), (97, 12)], "live", w=2)                         # strike the girl, keep the E
        p.big((PW // 2, 23), "EQUITY", "gold_hi", "gold")
    if stage >= 2:
        p.tag((PW // 2, 43), "CO-OWNER: OTK", "gold", "ink", anchor="ma")
    return p.img


@gag("v1", 0)
def e_for_equity(c, L):
    stage = 2 if L.age("equity") > 0.35 else 1 if L.on("stands") else 0
    show(c, egirl_pic(stage), "DEFINITIONS", "E")
    if L.on("cute") and not L.on("stands"):
        pose(c, "emiru", arms="shrug", brows="up", eyes="half")
    if L.on("equity"):
        pose(c, "emiru", arms="thumb", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def cap_table(stage):
    p = Pic("paper")
    p.header("CAP TABLE", "ink", "gold", h=9)
    p.silk((4, 13), "EMIRU", "ink"); p.meter((36, 13, 72, 18), 0.8, "emiru", "paper_sh"); p.tick(84, 12, "green_sh")
    p.line([(3, 22), (96, 22)], "paper_sh")
    p.silk((4, 26), "PLAINTIFF", "ink"); p.meter((56, 26, 80, 31), 0.0, "emiru", "paper_sh")
    p.silk((96, 26), "0%", "live", anchor="ra")
    if stage:
        p.verdict(50, 43, "EX-EMPLOYEE")
    return p.img


@gag("v1", 1)
def ex_employee(c, L):
    show(c, cap_table(1 if L.on("ex-employee") else 0), "RECEIPTS", "DOC")
    if L.on("ex-employee"):
        pose(c, "emiru", arms="window", eyes="side", brows="up")
    yield "front"
    jolt(c, L.age("ex-employee"), 2)


# --- 2-4: the one true Emily, forty wigs --------------------------------------------------------------------

@lru_cache(maxsize=None)
def time_clock(n, emily):
    p = Pic("panel")
    p.header("OTK: TIME CLOCK", "bar", "gold", h=9)
    for i in range(3):                                                   # the kings, punching in
        x = 8 + 31 * i
        p.rbox((x, 13, x + 23, 33), "paper" if i < n else "panel_hi", "ink", 2)
        if i < n:
            crown(p, x + 6, 15)
            p.silk((x + 12, 26), "IN", "green_sh", anchor="ma")
    p.silk((8, 37), "ONE TRUE", "text")
    if emily:
        p.silk((56, 37), "KING", "mute"); p.line([(55, 39), (80, 39)], "live")
        p.press((56, 43), "EMILY", "emiru_hi", shadow="ink")
    else:
        p.silk((56, 37), "KING", "gold")
    return p.img


@gag("v1", 2)
def one_true_emily(c, L):
    n = 3 if L.on("clock") else 0
    if L.on("clock") and L.age("clock") < 0.45:
        n = 1 + int(L.age("clock") / 0.15)
    show(c, time_clock(n, L.on("Emily")), "PAYROLL", "LIVE")
    if L.on("Emily"):
        pose(c, "emiru", arms="chest", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def wig_select(n, locked):
    p = Pic("rift")
    p.silk((PW // 2, 3), "CHOOSE YOUR WIG", "lol_gold", anchor="ma")
    for i in range(10):
        x, y = 5 + 19 * (i % 5), 11 + 15 * (i // 5)
        p.rect((x, y, x + 13, y + 13), "rift_hi")
        if i < n:
            wig_icon(p, x + 1, y, WIG_COLORS[i], i % 3)
        p.d.rectangle((x - 1, y - 1, x + 14, y + 14), outline=col("lol_gold" if (locked and i == 0) else "line"))
    p.rbox((8, 41, 70, 50), "lol_teal" if locked else "rift_hi", "lol_gold", 2)
    p.silk((39, 43), "LOCKED IN" if locked else "LOCK IN", "ink" if locked else "lol_gold", anchor="ma")
    if n >= 10:
        p.silk((95, 43), "x40", "gold", anchor="ra")
    return p.img


@gag("v1", 3)
def forty_wigs(c, L):
    n = 0 if not L.on("forty") else min(10, 2 + int(L.age("forty") / 0.06))
    show(c, wig_select(n, L.on("identity")), "CHAMP SELECT", "0:07")
    if L.on("^lock") and L.age("^lock") < 0.4:
        pose(c, "emiru", arms="click", eyes="down")
    yield "front"


@lru_cache(maxsize=None)
def lineup(stage):
    p = Pic("paper_sh")
    for i, y in enumerate(range(6, 40, 6)):                              # the height lines
        p.line([(0, y), (PW, y)], "grey_hi" if i % 2 else "grey")
    p.rect((0, 40, PW, PH), "grey_sh")
    for i in range(5):
        x = 6 + 19 * i
        p.rect((x + 4, 30, x + 7, 40), "foam_sh")
        wig_icon(p, x, 18, WIG_COLORS[(i * 3) % 10], i % 3)
        p.silk((x + 6, 42), str(i + 1), "paper", anchor="ma")
    if stage >= 1:
        p.tag((PW // 2, 4), "NO FACE: NO CASE", "ink", "paper", anchor="ma")
    if stage >= 2:
        p.verdict(50, 46, "NO FELONY")
    return p.img


@gag("v1", 4)
def no_felony(c, L):
    show(c, lineup(2 if L.on("felony") else 1 if L.on("case") else 0), "THE LINEUP", "5")
    if L.on("felony"):
        pose(c, "emiru", arms="shrug", brows="up", eyes="shut" if L.age("felony") < 0.8 else "open")
    yield "front"
    jolt(c, L.age("felony"), 2)


# --- 5-8: the armoury ----------------------------------------------------------------------------------------

def tooltip(p, name, rows, color="lol_gold"):
    """An item's card, the way the shop in a game shows one: a name, then its numbers."""
    p.panel((0, 0, PW - 1, PH - 3), color, "rift")
    p.silk((36, 4), name, color)
    for i, (k, v, cc) in enumerate(rows):
        p.silk((36, 15 + 9 * i), k, "dim"); p.silk((96, 15 + 9 * i), v, cc, anchor="ra")
    p.d.rectangle((3, 3, 31, 31), outline=col(color)); p.rect((4, 4, 30, 30), "rift_hi")


@lru_cache(maxsize=None)
def glue_card(n):
    p = Pic("rift")
    tooltip(p, "HOT GLUE", (("HEAT", "380 F", "orange"), ("TRIGGER", "HAIR", "live"), ("AMMO", "X12", "text"))[:n])
    p.put(glue_gun(), 17, 17)
    p.silk((4, 43), "CARRY: HIP", "mute")
    return p.img


@gag("v1", 5)
def heat_on_my_hip(c, L):
    show(c, glue_card(count(L, "hip", "glue", "trigger")), "ARMOURY", "1/3")
    if L.on("glue"):
        hold_up(c, "emiru", glue_gun(), 2)
        pose(c, "emiru", eyes="side", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def singer_pic(stage, f):
    p = Pic("night")
    for i in range(7 if stage else 0):                                    # speed lines
        y = 6 + 6 * i
        x = (i * 37 + f * 23) % 60
        p.line([(x, y), (x + 26, y)], "night_hi")
    x, y = 8 + (f % 2 if stage else 0), 38                               # the machine, at full pelt
    p.rect((x, y - 5, x + 44, y), "black"); p.rect((x + 32, y - 22, x + 42, y - 5), "black")
    p.rect((x + 4, y - 23, x + 42, y - 16), "black"); p.rect((x + 4, y - 16, x + 12, y - 9), "black")
    p.line([(x + 8, y - 9), (x + 8, y - 5 + (f % 2) * 2)], "steel")
    p.ell((x + 41, y - 24, x + 48, y - 14), "steel")
    p.silk((x + 23, y - 22), "SINGER", "gold", anchor="ma")
    p.rect((0, y + 1, PW, y + 2), "wood_hi")
    p.rect((x - 4 + (f * 5) % 30, y - 3, x + 20 + (f * 5) % 30, y - 1), "knit")       # the seam, flying
    cx, cy = 78, 30                                                      # the dial
    p.d.pieslice((cx - 16, cy - 16, cx + 16, cy + 16), 180, 360, fill=col("bg"), outline=col("lol_gold"))
    a = math.radians(200 + (140 if stage else 20) + (3 * (f % 2) if stage else 0))
    p.line([(cx, cy), (cx + int(13 * math.cos(a)), cy + int(13 * math.sin(a)))], "live", w=2)
    p.silk((cx, cy + 3), "MAX" if stage else "0", "live" if stage else "dim", anchor="ma")
    if stage >= 2:
        p.tag((PW - 3, 43), "FULL SPEED", "live", "white", anchor="ra")
    return p.img


@gag("v1", 6)
def whipping_a_singer(c, L):
    stage = 2 if L.on("speed") else 1 if L.on("floor") else 0
    show(c, singer_pic(stage, c.f % 12 if stage else 0), "WHIP", "MPH")
    if L.on("whipping"):
        pose(c, "emiru", arms="guns", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def vest_card(n):
    p = Pic("rift")
    tooltip(p, "FOAM VEST", (("ARMOR", "+0", "dim"), ("DRIP", "+99", "ok"), ("COAT", "SILVER", "steel_hi"))[:n], "steel_hi")
    p.poly([(9, 8), (25, 8), (28, 14), (25, 24), (17, 28), (9, 24), (6, 14)], "steel")
    p.line([(11, 11), (15, 22)], "steel_hi"); p.line([(17, 9), (17, 27)], "steel_sh"); p.line([(21, 11), (24, 20)], "steel_hi")
    if n >= 3:                                                           # the can that did it
        p.rect((87, 41, 92, 49), "steel"); p.rect((88, 39, 90, 41), "black")
        p.pxs([(84, 39), (82, 41), (85, 42), (81, 38), (83, 44)], "steel_hi")
    p.silk((4, 43), "EVA FOAM, 6 MM", "mute")
    return p.img


@gag("v1", 7)
def vest_on_my_chest(c, L):
    show(c, vest_card(count(L, "chest", "foam", "silver")), "ARMOURY", "2/3")
    if L.on("chest") and not L.on("foam"):
        pose(c, "emiru", arms="chest")
    yield "front"


@lru_cache(maxsize=None)
def stitches_pic(stage):
    p = Pic("ewall")
    p.ell((2, 1, 62, 50), "wood_hi"); p.d.ellipse((2, 1, 62, 50), outline=INK)       # the hoop
    p.ell((6, 5, 58, 46), "cream"); p.d.ellipse((6, 5, 58, 46), outline=col("wood_sh"))
    p.rect((29, 0, 35, 3), "steel")
    for i, s in enumerate(("SNITCHES", "GET", "STITCHES")):
        p.silk((32, 13 + 9 * i), s, "live", anchor="ma")
    p.pxs([(12, 14), (52, 14), (12, 38), (52, 38)], "emiru")
    if stage:
        p.silk((81, 4), "HATERS", "ink", anchor="ma"); p.silk((81, 11), "GET", "ink", anchor="ma")
        p.put(scissors(1 if stage == 1 else 0), 81, 34)
    return p.img


@gag("v1", 8)
def haters_get_scissors(c, L):
    a = L.age("scissors")
    show(c, stitches_pic(0 if not L.on("haters") else 1 if int(max(a, 0) * 7) % 2 == 0 else 2), "HOME DECOR", "DIY")
    if L.on("scissors"):
        hold_up(c, "emiru", scissors(int(a * 7) % 2 == 0), 2)
        pose(c, "emiru", mouth="grin" if a > 0.5 else c.st["emiru"]["mouth"], brows="up")
    yield "front"


# --- 9-10: League returned the favor -----------------------------------------------------------------------

def champ_frame(p, x, y, who=True, eyes="open", mouth="smile"):
    """A champion's portrait, 34 x 34, in the gold frame a game gives one."""
    p.rect((x, y, x + 33, y + 33), "rift_hi")
    if who:
        p.put(mug("emiru", eyes, "neutral", mouth), x + 17, y + 18)
    p.d.rectangle((x, y, x + 33, y + 33), outline=col("lol_gold"))
    p.d.rectangle((x - 1, y - 1, x + 34, y + 34), outline=INK)


@lru_cache(maxsize=None)
def favor_pic(stage):
    p = Pic("rift")
    p.rect((5, 3, 35, 35), "rift_hi"); p.d.rectangle((5, 3, 35, 35), outline=col("lol_gold"))
    p.ell((13, 7, 27, 21), "lol_teal"); p.poly([(10, 35), (13, 22), (27, 22), (30, 35)], "lol_teal")    # some champion
    p.poly([(11, 10), (9, 3), (16, 7)], "lol_gold"); p.poly([(29, 10), (31, 3), (24, 7)], "lol_gold")
    p.put(mug("emiru", "open", "neutral", "smile"), 80, 20)
    y = 13
    p.line([(40, y), (56, y)], "emiru", w=2); p.poly([(56, y - 4), (61, y), (56, y + 4)], "emiru")      # she dresses as it
    if stage:
        y = 26
        p.line([(45, y), (61, y)], "lol_gold", w=2); p.poly([(45, y - 4), (40, y), (45, y + 4)], "lol_gold")   # and back
    p.silk((PW // 2, 39), "I WORE THEIRS", "emiru_hi", anchor="ma")
    if stage:
        p.silk((PW // 2, 46), "THEY DREW MINE", "lol_gold", anchor="ma")
    return p.img


@gag("v1", 9)
def returned_the_favor(c, L):
    show(c, favor_pic(1 if L.on("returned") else 0), "PATCH NOTES", "NEW")
    yield "front"


@lru_cache(maxsize=None)
def pick_pic(stage):
    p = Pic("rift")
    champ_frame(p, 4, 4, True, "open", "smile" if stage < 2 else "smirk")
    if stage < 2:
        p.silk((4, 43), "NEW CHAMPION", "lol_gold")
    p.rbox((46, 9, 95, 22), "lol_teal" if stage >= 1 else "rift_hi", "lol_gold", 2)
    p.silk((52, 13), "PICK", "ink" if stage >= 1 else "lol_gold")
    if stage >= 1:
        p.tick(84, 12, "ink")
    p.rbox((46, 28, 95, 41), "rift_hi", "mute" if stage < 2 else "live", 2)
    p.silk((52, 32), "DATE", "mute")
    if stage >= 2:
        p.cross(88, 34, "live"); p.line([(50, 34), (76, 34)], "live")
        p.silk((3, 43), "NOT IN THIS PATCH", "live")
    return p.img


@gag("v1", 10)
def pick_her(c, L):
    show(c, pick_pic(2 if L.on("date") else 1 if L.on("pick") else 0), "CHAMP SELECT", "0:03")
    if L.on("face") and not L.on("pick"):
        pose(c, "emiru", arms="chin", eyes="side")
    if L.on("date"):
        pose(c, "emiru", arms="finger", brows="up", eyes="half")
    yield "front"
    jolt(c, L.age("date"), 2)


# --- 11-12: bodies on my paper ------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def bodies_pic(stage):
    p = Pic("paper")
    p.header("INCIDENT REPORT", "blue_sh", "white", h=9)
    p.silk((4, 13), "BODIES", "ink"); p.press((96, 12), "14", "live", anchor="ra")
    p.line([(3, 22), (96, 22)], "paper_sh")
    if stage:
        p.silk((4, 26), "TIME", "ink"); p.press((96, 25), "4:51 AM", "ink", anchor="ra")
        p.line([(3, 35), (96, 35)], "paper_sh")
        p.silk((4, 39), "SUSPECT", "ink"); p.silk((96, 39), "CAT EARS", "ink", anchor="ra")
    return p.img


@gag("v1", 11)
def bodies_on_my_paper(c, L):
    show(c, bodies_pic(1 if L.on("dawn") or L.on("most") else 0), "POLICE", "FILE")
    yield "front"


@lru_cache(maxsize=None)
def ranked_pic(stage, secs):
    p = Pic("rift")
    p.header("RANKED: VICTORY", "rift_hi", "lol_gold", h=9)
    p.put(mug("emiru", "open", "neutral", "smirk", 3), 12, 20)
    p.silk((28, 11), "K / D / A", "dim"); p.press((28, 18), "14/2/8", "gold_hi", shadow="ink")
    for i in range(7):                                                   # the bodies
        x = 6 + 13 * i
        if stage >= 2:                                                   # are back on their feet
            p.rect((x + 2, 35, x + 6, 40), "blue_hi"); p.ell((x + 1, 30, x + 7, 36), "blue_hi"); p.px((x + 3, 33), "ink")
            p.px((x + 5, 33), "ink")
        else:
            p.ell((x + 1, 32, x + 7, 38), "grey_hi"); p.rect((x + 3, 38, x + 5, 40), "grey_hi")
            p.px((x + 3, 34), "ink"); p.px((x + 5, 34), "ink")
    if stage >= 1:
        p.tag((PW // 2, 42), "RESPAWN 0:%02d" % secs if stage < 2 else "ALL RESPAWNED", "live" if stage < 2 else "ok",
              "white" if stage < 2 else "ink", anchor="ma")
    return p.img


@gag("v1", 12)
def they_respawn(c, L):
    stage = 2 if L.on("respawn") else 1 if L.on("ranked") else 0
    show(c, ranked_pic(stage, max(0, 3 - int(max(L.age("ranked"), 0) * 3))), "MATCH HISTORY", "W")
    if L.on("officer") and not L.on("ranked"):
        pose(c, "emiru", arms="palm", brows="up", eyes="half")
    if L.on("respawn"):
        pose(c, "emiru", arms="shrug", brows="up")
    yield "front"
    jolt(c, L.age("respawn"), 2)


# --- 13-14: the athlete stays home ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def athlete_pic(stage, slats):
    p = Pic("can_blue")
    p.grad((0, 0, PW, PH), "can_blue", "night", steps=4)
    p.put(can(True), 18, 13)
    p.silk((38, 4), "ATHLETE", "can_silver"); p.press((38, 11), "EMIRU", "white", shadow="ink")
    p.silk((6, 26), "SPORT:", "can_silver"); p.silk((44, 26), "SITTING", "yellow")
    if stage >= 1:
        p.press((6, 35), "1 BILLION", "gold_hi", shadow="ink"); p.silk((6, 45), "VIEWS", "can_silver")
    for i in range(slats):                                               # the blinds, coming down
        p.rect((0, 6 * i, PW, 6 * i + 4), "cream"); p.line([(0, 6 * i + 4), (PW, 6 * i + 4)], "paper_sh")
    return p.img


@gag("v1", 13)
def red_bulls_athlete(c, L):
    slats = 0 if not L.on("blinds") else min(9, int(L.age("blinds") / 0.07))
    if L.age("closed") > 0.5:
        slats = 9
    show(c, athlete_pic(1 if L.on("billion") else 0, slats), "SPONSOR", "AD")
    if not L.on("billion"):
        hold_up(c, "emiru", can(), 2)
    yield "front"


@lru_cache(maxsize=None)
def kansas_pic(stage, f):
    p = Pic("sky")
    p.sky(34)
    p.ground(34, "hay", "hay_sh")                                        # wheat, to the horizon
    for x in range(0, PW, 5):
        p.line([(x, 36 + (x * 7) % 5), (x + 1, 34 + (x * 7) % 5)], "hay_sh")
    tx = 78 + int(2 * math.sin(f * 0.8))                                 # a twister, a long way off
    for i in range(8):
        w = 9 - i
        p.rect((tx - w + int(2 * math.sin(f * 0.9 + i)), 10 + 3 * i, tx + w + int(2 * math.sin(f * 0.9 + i)), 12 + 3 * i), "grey")
    p.rect((8, 20, 34, 38), "white"); p.poly([(5, 21), (21, 9), (37, 21)], "red_sh")                    # home
    p.rect((17, 28, 24, 38), "wood"); p.rect((27, 24, 32, 29), "night_hi")
    p.d.rectangle((8, 20, 34, 38), outline=INK)
    if stage >= 1:                                                       # the heels, clicked together
        k = f % 2
        p.put(heel(), 50 + 2 * k, 43); p.put(mirror(heel()), 68 - 2 * k, 43)
        if k:
            p.pxs([(59, 33), (55, 36), (63, 36), (59, 29), (52, 31), (66, 31)], "gold_hi")
    if stage >= 2:
        p.tag((21, 3), "LIVE", "live", "white", anchor="ma")
        p.tag((68, 3), "STAYING IN", "ink", "gold", anchor="ma")
    return p.img


@gag("v1", 14)
def stay_home(c, L):
    stage = 2 if L.on("stay") else 1 if L.on("click") else 0
    show(c, kansas_pic(stage, c.f // 3 % 16), "WICHITA, KS", "HOME")
    if L.on("stay"):
        pose(c, "emiru", arms="thumbs2", brows="up", mouth="grin" if L.age("home") > 0.4 else c.st["emiru"]["mouth"])
    yield "front"
