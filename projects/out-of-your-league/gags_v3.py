"""Verse 3: Emiru again, and this one is the receipts. Every picture is a document, a game's screen or a
sign: what Twitch said and what Twitch did. Nothing that happened to her is shown: the jokes are on them."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403


def twitch_boss(p, x, y, hurt=0):
    """The boss, 26 x 28, its feet at (x, y): a purple speech bubble in a tie."""
    p.rect((x - 5, y - 9, x + 5, y), "bg"); p.poly([(x - 1, y - 9), (x + 1, y - 9), (x + 2, y - 3), (x, y - 1), (x - 2, y - 3)], "live")
    p.rbox((x - 13, y - 28, x + 13, y - 8), "twitch", "ink", 3)
    p.poly([(x - 6, y - 8), (x - 6, y - 4), (x - 1, y - 8)], "twitch")
    p.rect((x - 10, y - 25, x + 10, y - 12), "twitch_sh")
    if hurt:
        p.line([(x - 7, y - 22), (x - 3, y - 18)], "white", w=2); p.line([(x - 7, y - 18), (x - 3, y - 22)], "white", w=2)
        p.line([(x + 3, y - 22), (x + 7, y - 18)], "white", w=2); p.line([(x + 3, y - 18), (x + 7, y - 22)], "white", w=2)
    else:
        p.rect((x - 6, y - 23, x - 4, y - 16), "white"); p.rect((x + 4, y - 23, x + 6, y - 16), "white")


# --- 0-1: two bosses ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def checks_pic(stage, n):
    if stage == 0:
        p = Pic("panel")
        for i, who in enumerate(("emiru", "maya")):
            x = 26 + 48 * i
            p.put(mug(who, "open", "neutral", "smirk" if i == 0 else "smile"), x, 30)
            crown(p, x - 5, 5)
            p.tag((x, 44), "BOSS", "gold", "ink", anchor="ma")
        return p.img
    p = Pic("panel")
    p.rect((3, 6, PW - 4, 46), "cream"); p.d.rectangle((3, 6, PW - 4, 46), outline=col("maya_sh"))
    p.rect((3, 6, PW - 4, 13), "maya_sh"); p.silk((7, 8), "ALVEUS: PAYROLL", "white")
    p.silk((7, 18), "PAY:", "wood_sh"); p.silk((30, 18), "EVERYBODY", "ink"); p.line([(29, 25), (92, 25)], "paper_sh")
    p.silk((7, 34), "SIGN:", "wood_sh"); p.line([(36, 41), (92, 41)], "wood_sh")
    sig = [(38, 38), (41, 30), (44, 39), (47, 31), (50, 39), (54, 34), (58, 39), (61, 30), (63, 39), (68, 35), (72, 39),
           (78, 33), (84, 38), (90, 36)]
    if n > 1:
        p.d.line(sig[:n], fill=col("blue_sh"), width=1)
    return p.img


@gag("v3", 0)
def signing_the_checks(c, L):
    stage = 1 if L.on("signing") else 0
    show(c, checks_pic(stage, min(14, int(max(L.age("signing"), 0) / 0.03))), "TWO BOSSES", "HR")
    if not stage and L.on("boss"):
        pose(c, "emiru", arms="thumbs2", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def kill_list(stage, flash):
    p = Pic("rift")
    p.header("BOSSES", "rift_hi", "lol_gold", h=9)
    for i, name in enumerate(("BARON", "DRAGON")):
        y = 11 + 8 * i
        p.silk((5, y), name, "mute"); p.line([(4, y + 2), (4 + silk_w(name) + 2, y + 2)], "mute")
        p.silk((96, y), "SLAIN", "lol_gold", anchor="ra")
    if stage >= 1:
        p.rect((0, 28, PW, 51), "bg")
        twitch_boss(p, 15, 60)                                           # its head and shoulders
        p.silk((32, 31), "TWITCH BOSS", "twitch_hi")
        p.meter((33, 41, 70, 45), 1.0, "twitch", "black")
    if stage >= 2 and flash:
        p.tag((98, 39), "NEXT", "live", "white", anchor="ra")
    return p.img


@gag("v3", 1)
def twitchs_boss_is_next(c, L):
    stage = 2 if L.on("next") else 1 if L.on("Twitch") else 0
    show(c, kill_list(stage, int(max(L.age("next"), 0) * 5) % 2 == 0), "KILL LIST", "PVE")
    if L.on("next"):
        pose(c, "emiru", arms="point", eyes="side", brows="skeptic")
    yield "front"
    jolt(c, L.age("next"), 2)


# --- 2-3: dues -----------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def split_pic(stage):
    p = Pic("panel")
    cx, cy, r = 26, 26, 21
    p.d.pieslice((cx - r, cy - r, cx + r, cy + r), 90, 270, fill=col("twitch"), outline=INK)
    p.d.pieslice((cx - r, cy - r, cx + r, cy + r), 270, 450, fill=col("emiru"), outline=INK)
    p.silk((cx - 10, cy - 2), "50", "white", anchor="ma"); p.silk((cx + 11, cy - 2), "50", "ink", anchor="ma")
    p.tag((53, 5), "TWITCH", "twitch", "white"); p.tag((53, 17), "ME", "emiru", "ink")
    if stage:
        p.silk((53, 32), "MY DUES", "gold"); p.silk((53, 40), "BUY ME:", "text")
    return p.img


@gag("v3", 2)
def half_my_subs(c, L):
    show(c, split_pic(1 if L.on("dues") or L.on("get") else 0), "SUB SPLIT", "50/50")
    if L.on("here"):
        pose(c, "emiru", arms="window", brows="up", eyes="side")
    yield "front"


def stanchion(p, x, y):
    p.rect((x - 1, y - 16, x + 1, y), "gold_sh"); p.ell((x - 3, y - 19, x + 3, y - 14), "gold"); p.rect((x - 4, y, x + 4, y + 1), "gold_sh")


@lru_cache(maxsize=None)
def rope_line(stage):
    p = Pic("grey_sh")
    p.rect((0, 0, PW, 30), "night_hi"); p.rect((0, 30, PW, PH), "grey_sh")                  # a hall, a carpet
    for x in (10, 44, 78):
        p.rect((x, 4, x + 14, 12), "twitch_sh")
    for a, b in ((6, 36), (36, 66)):                                     # the rope
        p.d.arc((a, 16, b, 36), 20, 160, fill=col("red"), width=2)
    for x in (6, 36, 66):
        stanchion(p, x, 44)
    if stage >= 1:                                                       # the guard: head down
        x = 84
        p.rect((x - 5, 34, x - 1, 46), "black"); p.rect((x + 1, 34, x + 5, 46), "black")
        p.rect((x - 7, 16, x + 7, 35), "black"); p.silk((x, 20), "SEC", "yellow", anchor="ma")
        p.ell((x - 5, 6, x + 5, 17), "mskin_sh"); p.rect((x - 5, 5, x + 5, 9), "brown_sh")
        p.px((x - 2, 14), "ink"); p.px((x + 2, 14), "ink")
        p.rect((x - 7, 46, x - 1, 48), "white"); p.rect((x + 1, 46, x + 7, 48), "white")   # the shoes
    if stage >= 2:
        p.pxs([(74, 44), (94, 44), (84, 50), (72, 48), (96, 48)], "gold_hi")
        p.line([(84, 18), (84, 43)], "gold_hi")                          # where he is looking
        p.tag((48, 43), "SHOES", "gold", "ink", anchor="ma")
    return p.img


@gag("v3", 3)
def looking_at_his_shoes(c, L):
    show(c, rope_line(2 if L.on("shoes") else 1 if L.on("guard") else 0), "MEMBER PERKS", "1")
    if L.on("shoes"):
        pose(c, "emiru", eyes="down", brows="up", arms="palm")
    yield "front"


# --- 4-5: immediately ----------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def stroll_pic(stage, k):
    p = Pic("paper")
    p.rect((0, 0, PW, 8), "twitch"); p.silk((4, 2), "STATEMENT", "white")
    p.silk((PW // 2, 13), "REMOVED", "ink", anchor="ma")
    p.press((PW // 2, 20), "IMMEDIATELY", "twitch_sh", anchor="ma")
    if stage:
        p.rect((0, 31, PW, PH), "grey_sh"); p.line([(0, 31), (PW, 31)], "ink")
        for i, x in enumerate((8, 40, 72)):                              # the stands he passed
            p.rect((x, 36, x + 20, 48), "panel"); p.rect((x - 1, 33, x + 21, 36), ("red", "blue", "gold")[i])
        x = 4 + int(k * 88)                                              # nobody in particular, in no hurry
        step = int(k * 16) % 2
        p.ell((x - 2, 34, x + 2, 38), "white"); p.rect((x - 2, 39, x + 2, 45), "white")
        p.line([(x - 1, 45), (x - 2 - step, 49)], "white"); p.line([(x + 1, 45), (x + 2 + step, 49)], "white")
        p.tag((PW - 1, 0), "%d:%02d" % (int(k * 5), int(k * 300) % 60), "live", "white", anchor="ra")
    return p.img


@gag("v3", 4)
def he_strolled_out(c, L):
    stage = 1 if L.on("strolled") else 0
    k = clamp(L.age("strolled") / 1.9, 0, 1) if stage else 0
    show(c, stroll_pic(stage, round(k * 32) / 32), "PRESS RELEASE", "PR")
    if not stage and L.on("immediately"):
        pose(c, "emiru", arms="guns", brows="up", eyes="half")
    yield "front"


@lru_cache(maxsize=None)
def porch_pic(stage, dots):
    p = Pic("panel")
    p.rect((0, 0, 48, PH), "sky_hi"); p.rect((0, 38, 48, PH), "wood_hi")                    # her porch
    p.rect((6, 6, 28, 38), "white"); p.rect((10, 10, 24, 38), "ears_sh"); p.px((22, 25), "gold")
    p.d.rectangle((6, 6, 28, 38), outline=INK)
    p.rect((30, 28, 44, 40), "parcel"); p.rect((36, 28, 38, 40), "tape"); p.d.rectangle((30, 28, 44, 40), outline=INK)
    p.poly([(32, 35), (38, 37), (42, 33)], "parcel_sh")
    p.tag((2, 43), "FOUND", "ok", "ink"); p.tick(37, 44, "ink")
    if stage:
        p.silk((75, 5), "SECURITY", "dim", anchor="ma")
        p.d.ellipse((66, 14, 84, 32), outline=col("line"))
        a = dots * math.pi / 4
        p.ell((75 + int(8 * math.cos(a)) - 2, 23 + int(8 * math.sin(a)) - 2, 75 + int(8 * math.cos(a)) + 2,
               23 + int(8 * math.sin(a)) + 2), "twitch_hi")
        p.tag((75, 43), "LOOKING" + "." * (1 + dots % 3), "twitch", "white", anchor="ma")
    return p.img


@gag("v3", 5)
def amazon_found_my_porch(c, L):
    show(c, porch_pic(1 if L.on("before") else 0, int(c.t * 6) % 8), "TRACKING", "2 DAY")
    if L.on("man"):
        pose(c, "emiru", arms="shrug", brows="up", eyes="half")
    yield "front"
    jolt(c, L.age("man"), 2)


# --- 6-7: the rulebook ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def rulebook(stage):
    p = Pic("panel")
    if stage == 0:
        p.rect((28, 3, 72, 49), "twitch"); p.rect((28, 3, 33, 49), "twitch_sh"); p.d.rectangle((28, 3, 72, 49), outline=INK)
        p.silk((53, 12), "THE", "twitch_hi", anchor="ma"); p.press((53, 20), "RULES", "white", anchor="ma")
        p.rect((60, 3, 64, 12), "gold")
        return p.img
    p.rect((0, 3, PW - 1, 48), "paper"); p.line([(45, 3), (45, 48)], "paper_sh"); p.d.rectangle((0, 3, PW - 1, 48), outline=INK)
    p.silk((3, 7), "IF YOU", "grey_sh"); p.silk((49, 7), "YOU GET", "grey_sh")
    p.line([(2, 14), (97, 14)], "paper_sh")
    if stage >= 2:
        p.silk((3, 18), "GRAB A", "ink"); p.silk((3, 25), "STALKER", "ink")
    if stage >= 3:
        p.rect((46, 19, 97, 28), "live"); p.silk((48, 21), "PERMABAN", "white")
    if stage >= 4:
        p.line([(2, 32), (97, 32)], "paper_sh")
        p.silk((3, 35), "GRAB MY", "ink"); p.silk((3, 42), "FACE", "ink")
    if stage >= 5:
        p.rect((46, 36, 97, 45), "warn"); p.silk((51, 38), "TIMEOUT", "ink")
    return p.img


@gag("v3", 6)
def their_rulebook(c, L):
    show(c, rulebook(1 if L.on("figure") else 0), "TERMS", "TOS")
    if L.on("figure"):
        pose(c, "emiru", arms="chin", eyes="side")
    yield "front"


@gag("v3", 7)
def permaban_timeout(c, L):
    stage = 5 if L.on("timeout") else 4 if L.on("grab", 1) else 3 if L.on("permaban") else 2
    show(c, rulebook(stage), "TERMS", "TOS")
    if L.on("timeout"):
        pose(c, "emiru", arms="shrug", brows="up", eyes="half")
    yield "front"
    jolt(c, L.age("permaban"), 2)
    jolt(c, L.age("timeout"), 3)


# --- 8-9: the boss fight -------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def ban_pic(stage, k):
    p = Pic("panel")
    p.header("BAN LENGTH", "twitch_sh", "white", h=9)
    x0, x1 = 10, 90
    p.rect((x0, 24, x1, 27), "black"); p.rect((x0, 24, x0 + int((x1 - x0) * (0.12 + 0.88 * k)), 27), "live")
    kx = x0 + int((x1 - x0) * (0.12 + 0.88 * k))
    p.rbox((kx - 4, 19, kx + 4, 32), "white", "ink", 2)
    if 0 < k < 1 or stage == 1:                                          # her finger on it
        p.rect((kx - 22, 23, kx - 5, 28), "eskin"); p.rect((kx - 7, 23, kx - 5, 28), "emiru")
        p.d.rectangle((kx - 22, 23, kx - 5, 28), outline=INK)
    p.silk((x0, 13), "30 DAYS", "text" if k < 0.5 else "mute")
    if k < 0.5:
        pass
    else:
        p.line([(x0 - 1, 15), (x0 + 42, 15)], "live")
    if stage >= 2:
        p.verdict(64, 42, "FOREVER")
    if stage >= 3:
        p.tag((PW - 2, 11), "NO BAIL", "ink", "gold", anchor="ra")
    return p.img


@gag("v3", 8)
def turned_to_forever(c, L):
    stage = 3 if L.on("bail") else 2 if L.on("forever") else 1 if L.on("pushed") else 0
    k = clamp(L.age("pushed") / max(0.2, L.age("pushed") - L.age("forever") + 0.01), 0, 1) if stage else 0
    show(c, ban_pic(stage, round(k * 16) / 16), "MOD VIEW", "BAN")
    if L.on("pushed") and not L.on("forever"):
        pose(c, "emiru", arms="reach", brows="skeptic")
    yield "front"
    jolt(c, L.age("forever"), 3)


@lru_cache(maxsize=None)
def boss_fight(phase, said, f):
    p = Pic("rift")
    p.silk((4, 3), "TWITCH", "twitch_hi"); p.silk((96, 3), "PHASE %d" % phase, "lol_gold", anchor="ra")
    p.meter((5, 11, 94, 14), 0.62 if phase == 1 else 0.12, "twitch" if phase == 1 else "live", "black")
    twitch_boss(p, 18 + (f % 2 if phase == 2 else 0), 49, hurt=phase == 2 and said)
    if said:
        s = ("SOCIETY", "DID THIS") if phase == 1 else ("WE", "FAILED.")
        p.rbox((36, 19, 96, 43), "white", "ink", 4); p.poly([(36, 28), (30, 31), (36, 34)], "white")
        p.silk((66, 24), s[0], "ink", anchor="ma"); p.silk((66, 33), s[1], "ink", anchor="ma")
    return p.img


@gag("v3", 9)
def we_failed(c, L):
    phase = 2 if L.on("two") else 1
    said = L.on("failed") if phase == 2 else L.on("blames")
    show(c, boss_fight(phase, bool(said), c.f // 3 % 2), "BOSS FIGHT", "P%d" % phase)
    if L.on("failed"):
        pose(c, "emiru", arms="guns", brows="up", mouth="grin" if L.age("failed") > 0.6 else c.st["emiru"]["mouth"])
    yield "front"
    jolt(c, L.age("two"), 2)
    jolt(c, L.age("failed"), 3)


# --- 10-13: the next one is on her land -------------------------------------------------------------------------

@gag("v3", 10)
def maya_cuts_in(c, L):
    """Maya has a bar, from the call: Emiru puts her up in the window."""
    c.vars["guest_big"] = True                                           # video.draw_view reads this
    pose(c, "emiru", arms="window", eyes="side", brows="up", mouth="grin" if L.on("rail") else "smile")
    yield "front"


@lru_cache(maxsize=None)
def detail_pic(stage):
    p = Pic("panel")
    p.rect((3, 3, PW - 4, 48), "paper"); p.d.rectangle((3, 3, PW - 4, 48), outline=INK)
    p.rect((3, 3, PW - 4, 11), "black"); p.silk((PW // 2, 5), "SECURITY DETAIL", "gold", anchor="ma")
    p.rect((7, 14, 39, 45), "sky_hi"); p.d.rectangle((7, 14, 39, 45), outline=INK)
    p.img.paste(animals.wolf(True).crop((4, 0, 30, 30)), (10, 15), animals.wolf(True).crop((4, 0, 30, 30)))
    p.line([(31, 22), (34, 30), (32, 36)], "black")                       # the earpiece
    p.silk((44, 16), "AGENT:", "grey_sh"); p.silk((44, 23), "HER WOLF", "ink")
    if stage:
        p.silk((44, 33), "TAIL:", "grey_sh"); p.press((72, 31), "YES", "green_sh")
    return p.img


@gag("v3", 11)
def my_details_got_a_tail(c, L):
    show(c, detail_pic(1 if L.on("tail") else 0), "ON DUTY", "K9")
    if L.on("tail"):
        pose(c, "emiru", arms="thumb", brows="up", mouth="grin" if L.age("tail") > 0.4 else c.st["emiru"]["mouth"])
    yield "front"


def con_badge(p, x, color, shade, lines, dead=False):
    """A convention badge on its lanyard, 40 wide, its left edge at x."""
    p.line([(x + 14, 0), (x + 20, 9)], shade, w=2); p.line([(x + 26, 0), (x + 20, 9)], shade, w=2)
    p.rbox((x, 9, x + 40, 47), "paper", "ink", 3); p.rect((x + 1, 10, x + 39, 19), color)
    p.rect((x + 16, 11, x + 24, 12), "black")
    for i, s in enumerate(lines):
        p.silk((x + 20, 23 + 8 * i), s, "ink" if i else shade, anchor="ma")
    if dead:
        p.line([(x + 3, 44), (x + 37, 12)], "live", w=2)


@lru_cache(maxsize=None)
def cons_pic(stage):
    p = Pic("panel")
    con_badge(p, 6, "twitch", "twitch_sh", ("T-CON", "LAST", "ONE"), dead=True)
    if stage:
        con_badge(p, 54, "maya", "maya_sh", ("NEXT:", "HER", "LAND"))
        p.poly([(69, 19), (74, 13), (79, 19)], "red"); p.rect((70, 14, 78, 18), "red")       # the barn, on its header
        p.rect((54 + 1, 10, 54 + 39, 19), "maya"); p.poly([(70, 18), (74, 12), (78, 18)], "red_sh")
    return p.img


@gag("v3", 12)
def next_ones_on_her_land(c, L):
    show(c, cons_pic(1 if L.on("next") else 0), "BADGES", "2")
    if L.on("land"):
        pose(c, "emiru", arms="window", brows="up", eyes="side")
    yield "front"


@lru_cache(maxsize=None)
def door_policy(stage, blink, chew):
    p = Pic("pasture")
    p.sky(22); p.ground(22)
    p.fence(20)
    p.put(animals.winnie(chew), 26, 30)
    p.tag((2, 44), "CUT: 5%", "ink", "ok")
    if stage:
        p.put(animals.emu(blink), 66, 26)
        for x in (82, 91):                                               # hands, up where she can see them
            p.rect((x, 10, x + 6, 24), "eskin_sh"); p.d.rectangle((x, 10, x + 6, 24), outline=INK)
            for i in range(3):
                p.rect((x + 1 + 2 * i, 6, x + 1 + 2 * i, 10), "eskin_sh")
        p.tag((PW - 2, 44), "HANDS?", "gold", "ink", anchor="ra")
    return p.img


@gag("v3", 13)
def the_emu_checks_hands(c, L):
    show(c, door_policy(1 if L.on("emu") else 0, 1 if (c.t % 1.3) < 0.12 else 0, int(c.t * 2.2) % 2), "DOOR POLICY", "NEW")
    if L.on("hands"):
        pose(c, "emiru", arms="up2" if L.age("hands") < 0.7 else "shrug", brows="up", mouth="grin")
    yield "front"
