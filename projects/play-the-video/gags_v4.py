"""Verse 4: Asmongold again. He opens with a tour of his own room, which he is proud of; then it's back to
the window."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403
from gags_v2 import click


def tooltip(c, x, y, title, sub, a, color="gold", dur=None, side=1):
    """A game's tooltip on a thing in the room, from age a: its bottom corner (the left one, or the right
    one with side=-1) at a world point, with a tick from there toward the thing."""
    if a < 0 or (dur is not None and a > dur):
        return
    w = max(silk_w(title), silk_w(sub)) + 7
    x0 = int(x) if side > 0 else int(x) - w
    y0 = int(y) - 20 + (pop_dy(a, 0.12, 4) or 0)
    d = ImageDraw.Draw(c.world)
    d.rectangle((x0, y0, x0 + w, y0 + 19), fill=C["bg"], outline=col(color))
    silk(c.world, (x0 + 4, y0 + 3), title, color)
    silk(c.world, (x0 + 4, y0 + 11), sub, "dim")
    cx = x0 if side > 0 else x0 + w
    d.line([(cx, y0 + 19), (cx - 3 * side, y0 + 23)], fill=col(color))


# --- 0-1: the tour ----------------------------------------------------------------------------------------

@gag("v4", 0)
def rats_rot(c, L):
    pose(c, "asmon", arms="palm" if not L.on("roaches") else "desk", eyes="half", brows="neutral")
    yield "mid"
    if L.on("roaches"):                                              # a column of them, along the desk
        a = L.age("roaches")
        for i in range(8):
            x = W + 6 - 170 * a + 13 * i
            if -8 < x < W + 8:
                rooms.roach(c.cam["asmon"], x, DESK_Y + 4 + 3 * (i % 2), c.t, i, -1)
    yield "front"
    tooltip(c, 146, 91, "RAT", "ROTTING", L.age("Rats"), dur=L.w("roaches") - L.w("Rats"))
    tooltip(c, 118, 158, "ROACHES", "KITCHEN STAFF", L.age("roaches"))


@gag("v4", 1)
def blood_dried(c, L):
    pose(c, "asmon", arms="thumb" if not L.on("something") else "desk", eyes="half" if not L.on("twitching") else "side",
         brows="neutral")
    if L.on("twitching"):
        c.chat += [("RATKING:", "asmon_hi", "CHECK THE BED"), ("GRUG:", "asmon_hi", "BRO")]
    yield "back"
    if L.on("something"):                                            # the shape under the blanket
        k = int(round(2 + 2 * math.sin(c.t * 34))) if int(c.t * 3) % 2 == 0 else 0
        lump = [(284, 113), (290, 100 - k), (304, 96 - k), (W, 100 - k), (W, 124), (286, 124)]
        d = ImageDraw.Draw(c.cam["asmon"])
        d.polygon(lump, fill=C["grey_sh"], outline=INK)
        d.line([(292, 103 - k), (303, 99 - k), (314, 102 - k)], fill=C["grey"])
    yield "front"
    tooltip(c, 183, 57, "BLOOD", "DRIED", L.age("blood"), "red_hi", dur=L.w("something") - L.w("blood"), side=-1)
    tooltip(c, 317, 94, "???", "TWITCHING", L.age("something"), "purple", side=-1)


# --- 2-3: no staff, more views -------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def staff_pic(n):
    """Who he pays to look like this."""
    p = Pic("panel")
    p.header("MY STAFF", "asmon_sh", "white", h=9)
    for i, s in enumerate(("TAILOR", "TRAINER", "UNCLE IN TV")[:n]):
        y = 12 + 13 * i
        p.rect((3, y, 96, y + 10), "panel_hi")
        p.silk((6, y + 3), s, "text")
        p.cross(90, y + 5, "live", 3)
    return p.img


@gag("v4", 2)
def no_staff(c, L):
    show(c, staff_pic(count(L, "tailor", "trainer", "uncle")), "ASMONGOLD", "TEAM")
    click(c, L)
    yield "front"


def views_pic(k, mine, his):
    """Where the viewers are."""
    p = Pic("bg")
    p.header("VIEWERS", "panel_hi", "gold", h=9)
    h1, h2 = int(22 * k), int(22 * k * his / mine)
    p.rect((16, 41 - h1, 36, 41), "asmon"); p.rect((64, 41 - h2, 84, 41), "hasan")
    p.line([(4, 42), (95, 42)], "line")
    if k >= 1:
        p.silk((26, 12), f"{mine / 1000:.0f}K", "asmon_hi", anchor="ma"); p.silk((74, 41 - h2 - 8), f"{his / 1000:.0f}K", "hasan_hi", anchor="ma")
    p.silk((26, 44), "LANDFILL", "text", anchor="ma"); p.silk((74, 44), "MANSION", "text", anchor="ma")
    return p.img


@gag("v4", 3, post=0.7)
def more_views(c, L):
    show(c, views_pic(clamp(L.age("views") / 0.35, 0, 1) if L.on("views") else 0.0, chatlog.count("asmon", c.t),
                      chatlog.count("hasan", c.t)), "ASMONGOLD", "STATS")
    if L.on("it"):
        pose(c, "asmon", arms="shrug", eyes="half", brows="neutral", mouth="closed")
    yield "front"


# --- 4-5: the tank ----------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def role_pic(n):
    """Three kinds of tank, and which of them he is."""
    p = Pic("panel")
    p.header("ROLE CHECK", "asmon_sh", "white", h=9)
    for i, (s, ok) in enumerate((("TANKIE", True), ("TANK TOP", True), ("CAN TANK", False))[:n]):
        y = 12 + 13 * i
        p.rect((3, y, 96, y + 10), "panel_hi")
        p.silk((6, y + 3), s, "text")
        if ok:
            p.tick(87, y + 2, "ok")
        else:
            p.cross(90, y + 5, "live", 3)
    return p.img


@gag("v4", 4)
def cant_tank(c, L):
    show(c, role_pic(count(L, "Tankie", "^tank$", "can't")), "HASANABI", "ROLE")
    click(c, L)
    yield "front"


@lru_cache(maxsize=None)
def ragequit_pic(stage):
    """One L. stage 0: full health; 1: it lands; 2: he is gone."""
    if stage == 2:
        p = Pic("black")
        p.press((PW // 2, 9), "RAGE QUIT", "live", anchor="ma")
        p.silk((PW // 2, 26), "HASAN HAS LEFT", "dim", anchor="ma"); p.silk((PW // 2, 35), "THE GAME", "dim", anchor="ma")
        return p.img
    p = Pic("bg")
    p.silk((4, 3), "HASAN", "hasan_hi"); p.meter((38, 4, 94, 7), 0.0 if stage else 1.0, "ok", "red_sh")
    face = ("wide", "angry", "grit") if stage else ("half", "neutral", "smirk")
    p.put(mug("hasan", *face), 20, 31)
    p.panel((40, 13, 97, 49), "line", "panel")
    p.silk((43, 15), "CHAT", "dim")
    if stage:
        p.silk((43, 27), "TEEN42:", "sky"); p.press((87, 25), "L", "white")
        p.silk((66, 38), "-100%", "live", anchor="ma")
    return p.img


@gag("v4", 5, post=0.9)
def rage_quits(c, L):
    stage = 2 if L.on("rage") else 1 if L.on("L,") else 0
    show(c, ragequit_pic(stage), "HASANABI", "LIVE" if stage < 2 else "GONE")
    click(c, L)
    if L.on("rage"):
        pose(c, "asmon", arms="shrug", eyes="half", brows="up", mouth="smirk")
    yield "front"


# --- 6-7: the richest man, the teens -------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def ladder_pic(fake):
    """The ladder, and what he said about the top of it."""
    p = Pic("bg")
    p.header("LADDER", "panel_hi", "gold", h=9)
    p.panel((2, 12, 97, 24), "gold", "panel")
    p.silk((5, 15), "#1 RICHEST MAN", "gold_hi")
    for i in range(2):
        y = 28 + 10 * i
        p.rect((2, y, 97, y + 7), "panel"); p.silk((5, y + 1), f"#{i + 2}", "mute"); p.rect((22, y + 3, 50 - 9 * i, y + 4), "mute")
    if fake:
        p.line([(4, 18), (95, 18)], "live")
        p.rect((54, 27, 96, 45), "live"); p.d.rectangle((54, 27, 96, 45), outline=INK)
        p.press((75, 32), "FAKE", "white", anchor="ma")
    return p.img


@gag("v4", 6)
def rank_was_fake(c, L):
    show(c, ladder_pic(L.on("fake")), "ASMONGOLD", "CLIP")
    click(c, L)
    if L.on("fake"):
        pose(c, "asmon", arms="point", eyes="half", brows="up")
    yield "front"


@gag("v4", 7, post=0.8)
def katanas_shake(c, L):
    """The clip plays: Hasan, and somebody's child."""
    if L.on("scream"):
        c.window.update(paused=False, badge="CLIP", progress=0.62 + 0.01 * L.age("scream"))
        c.window["shake"] = max(c.window["shake"], 2 if L.on("katanas") else 1)
        c.cam_t["hasan"] = c.t
        pose(c, "hasan", arms="chop" if int(c.t * 6) % 2 else "fist", eyes="squint", brows="angry", mouth="wide",
             react=False, shake=2 if L.on("katanas") else 1)
    yield "front"
    if L.on("teens") and c.t < when("v4", 8) - TL.LEAD:            # until the next bar's picture takes the window
        label(c, *win(c, 54, 46), "VS. A TEENAGER", L.age("teens"), bg="ink", fg="text")


# --- 8-9: cosplay -----------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def cosplay_pic(n):
    """The entry form."""
    p = Pic("panel")
    p.header("COSPLAY CONTEST", "blue", "white", h=9)
    p.panel((3, 12, 37, 50), "line", "panel_hi")
    p.poly([(6, 50), (9, 44), (15, 41), (26, 41), (32, 44), (35, 50)], "mao")                 # the collar of it
    p.put(mug("hasan", "open", "neutral", "grin"), 20, 30)
    for i, (s, colr) in enumerate((("AS: MAO", "gold_hi"), ("FOR:", "dim"), ("COLLEGE", "text"), ("KIDS", "text"))[:n]):
        p.silk((42, 13 + 9 * i), s, colr)
    return p.img


@gag("v4", 8)
def cosplay(c, L):
    n = 4 if L.on("kids") else 3 if L.on("college") else 2 if L.on("for") else 1 if L.on("Mao") else 0
    show(c, cosplay_pic(n), "HASANABI", "ENTRY")
    click(c, L)
    yield "front"


def leap_pic(k):
    """From the stage to the valet. k: how far through the leap he is."""
    p = Pic("night")
    p.header("THE GREAT LEAP", "live", "gold", h=9)
    p.rect((0, 46, PW, PH), "stone_sh")
    p.rect((2, 34, 30, 46), "wood"); p.rect((2, 32, 30, 34), "wood_hi")                        # the stage
    p.rect((4, 13, 5, 32), "steel_sh"); p.rect((6, 13, 24, 21), "red"); p.pxs([(14, 16), (15, 16), (16, 16), (15, 15), (15, 17)], "gold")
    p.rect((68, 26, 69, 46), "steel_sh"); p.tag((54, 18), "VALET", "white", "ink")             # the valet stand
    p.put(porsche(), 102, 39)
    for i in range(1, 9):                                                                    # the arc of it
        q = i / 9
        if q < k:
            p.px((int(16 + 42 * q), int(31 + 14 * q - 13 * math.sin(math.pi * q))), "gold")
    x, y = int(16 + 42 * k), int(31 + 14 * k - 13 * math.sin(math.pi * k))
    p.rect((x - 2, y - 7, x + 2, y - 1), "mao"); p.d.rectangle((x - 3, y - 8, x + 3, y), outline=INK)     # him, in the suit
    p.rect((x - 2, y - 12, x + 2, y - 8), "hskin"); p.rect((x - 2, y - 13, x + 2, y - 11), "hhair")
    if 0 < k < 1:
        p.line([(x - 2, y), (x - 4, y + 3)], "mao_sh"); p.line([(x + 2, y), (x + 5, y + 2)], "mao_sh")
        p.line([(x - 3, y - 6), (x - 6, y - 9)], "mao"); p.line([(x + 3, y - 6), (x + 6, y - 9)], "mao")
    else:
        p.rect((x - 2, y, x - 1, y + 3), "mao_sh"); p.rect((x + 1, y, x + 2, y + 3), "mao_sh")
    return p.img


@gag("v4", 9)
def great_leap(c, L):
    t0 = L.w("from")
    show(c, leap_pic(clamp((c.t - t0) / max(0.4, L.end - t0), 0, 1)), "HASANABI", "LIVE")
    yield "front"


# --- 10-11: the hairline --------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def quest_pic(stage):
    """His daily quest."""
    p = Pic("bg")
    p.header("DAILY QUEST", "panel_hi", "gold", h=9)
    p.rbox((7, 21, 23, 47), "orange", "ink", 2)                                               # the bottle
    p.rect((8, 16, 22, 21), "white"); p.d.rectangle((8, 16, 22, 21), outline=INK)
    p.rect((8, 28, 22, 39), "white"); p.line([(10, 31), (20, 31)], "grey"); p.line([(10, 34), (17, 34)], "grey")
    if stage >= 1:                                                                           # today's
        p.rbox((27, 13, 37, 18), "white", "ink", 2); p.rect((32, 14, 36, 17), "live")
    p.silk((42, 13), "KEEP HAIR", "gold_hi")
    p.silk((42, 23), "PILL: 1/1" if stage else "PILL: 0/1", "ok" if stage else "text")
    if stage >= 2:
        p.silk((42, 34), "SURGEON:", "text"); p.silk((42, 43), "DODGED", "ok")
    return p.img


@gag("v4", 10)
def pill_a_day(c, L):
    show(c, quest_pic(count(L, "day", "dodge")), "HASANABI", "DAILY")
    click(c, L)
    yield "front"


@lru_cache(maxsize=None)
def future_mug():
    """Hasan, some years on: where the hair was, and what is left of it."""
    h = head("hasan", "wide", "worried", "o").copy()
    d = ImageDraw.Draw(h)
    d.ellipse((16, 2, 51, 27), fill=col("hskin") + (255,))
    d.ellipse((24, 5, 41, 12), fill=col("hskin_hi") + (255,))
    d.arc((16, 2, 51, 27), 180, 360, fill=INK + (255,))
    for x in (21, 28, 35, 43):                                                               # the survivors
        d.line([(x, 4), (x + 1, 9)], fill=col("hhair") + (255,))
    m = h.convert("RGBa").resize((30, 30), Image.BOX).convert("RGBA")
    m.putalpha(m.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    return m


@lru_cache(maxsize=None)
def future_pic(stage):
    p = Pic("night")
    p.header("HAIRLINE: 2046" if stage else "HAIRLINE: 2026", "panel_hi", "sky_hi", h=9)
    for i in range(14):
        p.px((int(rnd("sx", i) * PW), 11 + int(rnd("sy", i) * 38)), "night_hi")
    p.put(future_mug() if stage else mug("hasan", "up", "worried", "closed"), 50, 31)
    return p.img


@gag("v4", 11)
def ghost_of_hairline_future(c, L):
    ghost = L.on("Ghost")                                 # the hook comes in on the last word: the reveal can't wait for it
    show(c, future_pic(1 if ghost else 0), "HASANABI", "2046" if ghost else "LIVE")
    if ghost:
        pose(c, "asmon", arms="up2", eyes="wide", brows="up", mouth="o")
        c.chat += [("ROACH77:", "asmon_hi", "OOOOOO"), ("BALD4:", "asmon_hi", "ONE OF US")]
    else:
        pose(c, "asmon", arms="point", eyes="half", brows="up")
    yield "mid"
    if ghost:                                                         # the lights go cold
        pixel.blend(c.cam["asmon"], 1.0, col("sky_hi"), 0.3 + 0.08 * math.sin(c.t * 9))
    yield "front"
    if ghost:
        ax, ay = c.at("asmon", "head")
        tooltip(c, ax - 24, ay + 12, "HAIRLINE", "YOURS, SOON", L.age("Ghost"), "sky_hi", side=-1)
