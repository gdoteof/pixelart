"""Verse 2: Washington raps from Boston and the King takes it on the London quay (v2 lines 0-14).

This verse leaves four things floating in the Atlantic: the King's straw hat, his powder keg,
a crate of boxed-up Hessians and the Olive Branch Petition, still sealed and marked SEEN.
"""
import timeline as TL
from gagkit import (BOSTON_EDGE, C, FEET_Y, GEORGE_X, INK, PRESS16, PRESS24, SILK, WASH_X, W, Canvas, Image,
                    ImageDraw, anchor, back_out, big_text, burst, char_sprite, debris, ease_in, ease_in_out,
                    ease_out, flagpole, float_on_water, gag, label, lerp, line_t, lru_cache, math, mix,
                    muzzle_flash, np, pan, paste, paste_rot, pop_dy, pop_text, projectile, puff, ramp, rnd,
                    scaled, sparkle, splash, stamp, tint, ui_at, wt)
from characters import figure
from props import envelope

GOLD, WHITE, RED = C["gold"], C["white"], C["flag_red"]
SILVER, SILVER_SH, SILVER_DK = (206, 212, 226), (150, 156, 176), (96, 100, 122)
TICK = (52, 104, 196)
SMOKE = (206, 184, 160)


def pop(age, **kw):
    """pop_dy, but 0 rather than None before it starts."""
    return pop_dy(age, **kw) or 0


def hit(idx):
    return TL.hit_of(TL.line("v2", idx))["t"]


def cam(c, L, shot):
    """Take the camera for line L, but let the reaction shot of a big hit play: this line's own
    (the default cut to London), and the tail of the previous line's, which the next line would cut off."""
    h = TL.hit_of(L.ln)
    if h["big"] and 0 <= c.t - h["t"] < 0.9:
        return
    i = L.ln["idx"]
    if i > 0:
        p = TL.hit_of(TL.line("v2", i - 1))
        if p["big"] and 0 <= c.t - p["t"] < 0.5:
            c.shot = "london"
            return
    c.take_shot(L, shot)


def at(c, who, key):
    x, y = anchor(c, who, key)
    return int(round(x)), int(round(y))


def gild(img, color, amount):
    """tint() that keeps the ink outline dark (for statues and coins)."""
    a = np.array(img)
    ink = (a[..., 0] == INK[0]) & (a[..., 1] == INK[1]) & (a[..., 2] == INK[2])
    out = np.array(tint(img, color, amount))
    out[ink] = a[ink]
    return Image.fromarray(out)


def spin_x(spr, t, hz=3.0):
    """A coin spinning about its vertical axis."""
    s = abs(math.cos(t * hz * math.pi))
    return spr.resize((max(1, int(round(spr.width * s))), spr.height), Image.NEAREST)


# --- props --------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def pocket_watch(shut):
    s = Canvas(12, 13)
    s.rect((5, 1, 6, 2), "gold_sh")
    s.ell((1, 3, 10, 12), "gold")
    if shut:
        s.ell((3, 5, 8, 10), "gold_sh"); s.ell((4, 6, 8, 10), "gold"); s.px((4, 6), "gold_hi")
    else:
        s.ell((2, 4, 9, 11), "white")
        s.line([(5, 8), (5, 5)], "ink"); s.line([(5, 8), (7, 8)], "ink")
    return s.done()


HORSES = {"chestnut": ((150, 86, 52), (104, 58, 40), (70, 40, 32)),
          "grey": ((214, 212, 220), (160, 158, 176), (110, 106, 124)),
          "gold": (C["gold"], C["gold_sh"], (170, 110, 30))}


@lru_cache(maxsize=None)
def horse(coat="chestnut", saddle=True):
    """A horse facing right, 38x28; hooves on row 25, saddle top on row 7."""
    body, sh, mane = HORSES[coat]
    s = Canvas(38, 28)
    for x in (11, 24):
        s.rect((x, 16, x + 1, 24), sh)
    for x in (14, 27):
        s.rect((x, 16, x + 1, 24), body)
    for x in (11, 14, 24, 27):
        s.rect((x, 24, x + 1, 25), mane)
    s.ell((8, 8, 30, 18), body)
    s.line([(11, 17), (27, 17)], sh)
    s.poly([(25, 11), (28, 4), (32, 5), (30, 14)], body)
    s.poly([(28, 3), (34, 5), (35, 9), (31, 10), (28, 7)], body)
    s.px((34, 8), mane)
    s.px((31, 5), "eye")
    s.pxs([(28, 2), (29, 1)], body)
    s.line([(25, 10), (28, 3)], mane); s.line([(26, 11), (29, 4)], mane)
    s.line([(8, 10), (4, 18)], mane); s.line([(9, 11), (5, 19)], mane)
    if saddle:
        s.rect((15, 7, 22, 11), "navy"); s.line([(15, 11), (22, 11)], "buff")
    return s.done()


@lru_cache(maxsize=None)
def big_horse(coat):
    return scaled(horse(coat), 1.25)


@lru_cache(maxsize=None)
def straw_hat():
    s = Canvas(20, 9)
    s.ell((1, 4, 18, 7), (226, 192, 104))
    s.ell((5, 1, 14, 6), (238, 208, 120))
    s.line([(5, 5), (14, 5)], RED)
    s.pxs([(3, 6), (8, 7), (13, 6), (16, 5)], (180, 146, 70))
    return s.done()


@lru_cache(maxsize=None)
def pitchfork():
    s = Canvas(9, 30)
    s.line([(4, 8), (4, 28)], "wood")
    s.line([(1, 7), (7, 7)], "steel_sh")
    for x in (1, 4, 7):
        s.line([(x, 1), (x, 7)], "steel")
    return s.done()


@lru_cache(maxsize=None)
def dung():
    s = Canvas(8, 7)
    s.ell((1, 2, 6, 5), (110, 70, 40)); s.ell((2, 1, 5, 3), (110, 70, 40)); s.px((3, 2), (150, 100, 60))
    return s.done()


@lru_cache(maxsize=None)
def thermometer(level):
    s = Canvas(8, 22)
    s.rect((2, 1, 5, 16), "white")
    s.ell((1, 14, 6, 20), RED)
    s.rect((3, 17 - level, 4, 16), RED)
    for y in (4, 8, 12):
        s.px((5, y), "white_sh")
    return s.done()


@lru_cache(maxsize=None)
def snowflake():
    s = Canvas(9, 9)
    for a, b in (((4, 1), (4, 7)), ((1, 4), (7, 4)), ((2, 2), (6, 6)), ((2, 6), (6, 2))):
        s.line([a, b], (210, 236, 255))
    return s.done()


@lru_cache(maxsize=None)
def carriage():
    s = Canvas(22, 11)
    s.poly([(2, 3), (19, 3), (19, 6), (2, 7)], "wood")
    s.line([(2, 3), (19, 3)], "wood_hi")
    for x in (6, 15):
        s.ell((x - 3, 4, x + 3, 10), "wood_sh"); s.px((x, 7), "iron")
    return s.done()


def cannon(img, x, y, droop, recoil=0):
    """A cannon on the quay pointing west, its barrel wilting by `droop` (0 stiff, 1 limp).
    (x, y) is the rear of the carriage on the ground; returns the muzzle."""
    x += recoil
    paste(img, carriage(), x, y + 1, "rb")
    d = ImageDraw.Draw(img)
    n = 18
    px, py = x - 6.0, y - 8.0
    pts = [(px, py)]
    for i in range(n):
        a = droop * 1.35 * (i / n) ** 1.6          # radians below the horizontal, growing toward the tip
        px -= math.cos(a)
        py += math.sin(a)
        pts.append((px, py))
    for col, grow in ((INK, 1), (C["iron"], 0)):
        for i, (ax, ay) in enumerate(pts):
            r = 2.6 - 1.0 * i / n + grow
            d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=col)
    for i, (ax, ay) in enumerate(pts[:-1]):
        d.point((ax, ay - 1.6 + i * 0.05), fill=C["iron_hi"])
    return pts[-1]


@lru_cache(maxsize=None)
def iron_ball():
    s = Canvas(7, 7)
    s.ell((1, 1, 5, 5), "iron"); s.px((2, 2), "iron_hi")
    return s.done()


@lru_cache(maxsize=None)
def powder_keg():
    s = Canvas(16, 16)
    s.rect((3, 1, 12, 14), "wood"); s.rect((1, 3, 14, 12), "wood")
    s.line([(4, 1), (4, 14)], "wood_hi")
    for y in (3, 12):
        s.line([(1, y), (14, y)], "iron")
    s.rect((2, 6, 13, 10), "paper")
    s.pxs([(5, 8), (7, 7), (8, 8), (10, 7)], "ink")
    return s.done()


@lru_cache(maxsize=None)
def calendar(year):
    im = Image.new("RGBA", (38, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 2, 37, 39), fill=INK)
    d.rectangle((1, 3, 36, 38), fill=C["paper"])
    d.rectangle((1, 3, 36, 11), fill=RED)
    d.line([(1, 38), (36, 38)], fill=C["paper_sh"])
    d.text((19, 3), "JULY", font=SILK, fill=WHITE, anchor="ma")
    d.text((19, 13), "4", font=PRESS16, fill=INK, anchor="ma")
    d.text((19, 30), year, font=SILK, fill=(120, 70, 50), anchor="ma")
    for x in (8, 28):
        d.rectangle((x, 0, x + 1, 4), fill=C["iron"])
    return im


@lru_cache(maxsize=None)
def olive_letter(tag=False):
    """The Olive Branch Petition: sealed, with a sprig; with `tag`, a SEEN read-receipt on a string."""
    env = envelope(22, 15, seal=True, sprig=True)
    if not tag:
        return env
    im = Image.new("RGBA", (38, 30), (0, 0, 0, 0))
    im.paste(env, (12, 12), env)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.line([(15, 13), (11, 9)], fill=C["paper_sh"])
    d.rectangle((0, 0, 25, 9), fill=INK)
    d.rectangle((1, 1, 24, 8), fill=WHITE)
    d.text((2, 0), "SEEN", font=SILK, fill=TICK)
    for ox in (17, 20):
        for dx, dy in ((0, 5), (1, 6), (2, 5), (3, 4), (4, 3)):
            d.point((ox + dx, dy), fill=TICK)
    return im


@lru_cache(maxsize=None)
def big_hessian(step=0):
    return scaled(hessian(step), 1.5)


@lru_cache(maxsize=None)
def hessian(step=0):
    """A Hessian grenadier: brass-fronted mitre cap, blue coat with red facings, musket shouldered."""
    s = Canvas(16, 29)
    for x, dy in ((5, step), (8, -step)):
        s.rect((x, 21, x + 1, 26 + dy), "white")
        s.rect((x, 25 + dy, x + 1, 26 + dy), "boot")
    s.rect((4, 12, 10, 21), (46, 70, 150))
    s.rect((9, 12, 10, 21), (200, 40, 50))
    s.line([(4, 18), (10, 18)], "white")
    s.rect((5, 6, 10, 12), "skin"); s.px((9, 8), "eye"); s.line([(8, 10), (10, 10)], (80, 60, 60))
    s.poly([(4, 6), (10, 6), (8, 1), (6, 1)], "gold")
    s.px((7, 3), "gold_hi")
    s.line([(12, 3), (12, 21)], "wood_sh"); s.px((12, 2), "steel")
    s.rect((11, 14, 12, 15), "skin")
    return s.done()


@lru_cache(maxsize=None)
def hessian_crate():
    """A Hessian, boxed up and gift-wrapped for Boxing Day: only his mitre cap pokes out."""
    s = Canvas(24, 21)
    s.poly([(9, 6), (15, 6), (13, 1), (11, 1)], "gold")
    s.px((12, 3), "gold_hi")
    s.rect((2, 6, 21, 19), "wood"); s.line([(2, 6), (21, 6)], "wood_hi"); s.line([(2, 19), (21, 19)], "wood_sh")
    s.rect((11, 6, 12, 19), RED); s.rect((2, 12, 21, 13), RED)
    s.poly([(11, 12), (6, 9), (6, 15)], RED); s.poly([(12, 12), (17, 9), (17, 15)], RED)
    s.pxs([(7, 11), (16, 11)], (240, 120, 120))
    return s.done()


@lru_cache(maxsize=None)
def ice_floe(k):
    w = 10 + int(rnd("floe", k) * 14)
    s = Canvas(w + 4, 7)
    s.poly([(1, 3), (3, 1), (w // 2, 1 + int(rnd("floe-a", k) * 2)), (w, 1), (w + 2, 3), (w, 5), (3, 5)],
           (226, 236, 250))
    s.line([(3, 4), (w, 4)], (176, 196, 230))
    return s.done((110, 130, 180))


@lru_cache(maxsize=None)
def rowboat(part):
    """A rowboat like the crier's: 'back' (inside, far gunwale) and 'front' (near side of the hull)."""
    s = Canvas(40, 12)
    if part == "back":
        s.poly([(3, 3), (36, 3), (33, 6), (6, 6)], "wood_sh")
        s.line([(3, 3), (36, 3)], "wood_hi")
        return s.done(None)
    s.poly([(1, 3), (38, 3), (34, 10), (5, 10)], "wood")
    s.line([(1, 3), (38, 3)], "wood_hi")
    s.line([(4, 7), (35, 7)], "wood_sh")
    s.line([(5, 10), (34, 10)], "wood_deep")
    return s.done()


@lru_cache(maxsize=None)
def big_boat(part):
    return scaled(rowboat(part), 1.6)


@lru_cache(maxsize=None)
def rower(stroke):
    """A Continental soldier hunched at the oars (two frames of the stroke)."""
    s = Canvas(16, 15)
    s.rect((3, 7, 9, 13), "navy"); s.line([(3, 7), (9, 7)], "navy_hi")
    s.ell((5, 2, 10, 7), "skin")
    s.poly([(3, 3), (12, 3), (10, 0), (5, 0)], "hat")
    if stroke:
        s.line([(8, 10), (14, 13)], "wood_hi")
    else:
        s.line([(8, 9), (14, 8)], "wood_hi")
    return s.done()


@lru_cache(maxsize=None)
def clock_face():
    s = Canvas(22, 22)
    s.ell((1, 1, 20, 20), "gold")
    s.ell((3, 3, 18, 18), "white")
    for k in range(12):
        a = k * math.pi / 6
        s.px((int(round(10.5 + 6 * math.sin(a))), int(round(10.5 - 6 * math.cos(a)))), "ink")
    s.line([(10, 10), (7, 12)], "ink")        # hour hand on eight
    s.line([(10, 10), (10, 5)], "ink")        # minute hand on twelve
    return s.done()


@lru_cache(maxsize=None)
def statue_img():
    """George III on horseback, in gilded lead: the Bowling Green statue without its pedestal."""
    rider = char_sprite("george", 1, mouth="closed", eyes="shut", brows="up", arm="point").crop((0, 0, 40, 38))
    rider = gild(rider, GOLD, 0.55)
    h = gild(horse("gold", saddle=False), GOLD, 0.2)
    im = Image.new("RGBA", (44, 52), (0, 0, 0, 0))
    im.paste(rider, (2, 0), rider)
    im.paste(h, (3, 24), h)
    return im


@lru_cache(maxsize=None)
def hot_statue(k):
    return tint(statue_img(), (255, 140, 50), k / 4 * 0.6)


@lru_cache(maxsize=None)
def pedestal():
    s = Canvas(34, 14)
    s.rect((1, 1, 32, 12), (214, 208, 220))
    s.rect((1, 1, 32, 2), (240, 236, 244))
    s.line([(1, 12), (32, 12)], (160, 154, 176))
    s.rect((6, 5, 27, 9), (190, 184, 200))
    return s.done()


@lru_cache(maxsize=None)
def cauldron_img():
    s = Canvas(40, 24)
    s.line([(8, 18), (5, 23)], "iron"); s.line([(31, 18), (34, 23)], "iron")
    s.ell((3, 4, 36, 22), "iron")
    s.ell((7, 8, 16, 14), "iron_hi")
    s.rect((2, 3, 37, 7), "iron")
    s.line([(2, 3), (37, 3)], "iron_hi")
    s.ell((4, 1, 35, 6), (255, 180, 60))
    s.ell((9, 2, 24, 4), (255, 236, 150))
    return s.done()


@lru_cache(maxsize=None)
def small_coin(heads=True):
    s = Canvas(7, 7)
    s.ell((1, 1, 5, 5), SILVER)
    s.px((3, 3), SILVER_DK if heads else SILVER_SH)
    s.px((2, 2), WHITE)
    return s.done()


@lru_cache(maxsize=None)
def quarter_face(size=116):
    """The quarter, blown up: Washington's profile facing left, LIBERTY above, QUARTER DOLLAR below."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.ellipse((0, 0, size - 1, size - 1), fill=INK)
    d.ellipse((1, 1, size - 2, size - 2), fill=SILVER_SH)
    d.ellipse((4, 4, size - 5, size - 5), fill=SILVER)
    for k in range(60):                                 # reeded rim
        a = k * math.pi / 30
        r = size / 2 - 2.5
        d.point((size / 2 - 0.5 + r * math.cos(a), size / 2 - 0.5 + r * math.sin(a)), fill=SILVER_DK)
    head = char_sprite("washington", -1, hat="off", mouth="closed", eyes="open", brows="neutral").crop((2, 6, 38, 40))
    arr = np.array(gild(head, (236, 240, 248), 0.7))
    ink = (arr[..., 0] == INK[0]) & (arr[..., 1] == INK[1]) & (arr[..., 3] > 0)
    arr[ink, :3] = SILVER_DK
    head = scaled(Image.fromarray(arr), 2)
    paste(im, head, size // 2 + 2, size - 29, "mb")
    d.text((size // 2, 10), "LIBERTY", font=SILK, fill=SILVER_DK, anchor="ma")
    d.text((size // 2, size - 27), "QUARTER DOLLAR", font=SILK, fill=SILVER_DK, anchor="ma")
    return im


@lru_cache(maxsize=None)
def quartered_house():
    """A Boston house with an uninvited redcoat quartered in it: his face at the window, boots out the door."""
    s = Canvas(32, 32)
    s.rect((3, 12, 28, 30), (168, 120, 124))
    for y in range(15, 30, 3):
        s.line([(3, y), (28, y)], (146, 100, 110))
    s.poly([(1, 12), (15, 2), (30, 12)], (112, 70, 82))
    s.line([(1, 12), (15, 2)], (170, 104, 104))
    s.rect((22, 3, 25, 8), (120, 80, 80))
    s.rect((6, 15, 13, 22), (60, 44, 60))
    s.ell((7, 16, 11, 20), "skin"); s.px((10, 18), "eye")
    s.poly([(6, 17), (13, 17), (11, 14), (8, 14)], "hat")
    s.rect((7, 21, 12, 22), "red")
    s.rect((18, 19, 25, 30), (40, 28, 36))
    s.rect((18, 27, 24, 30), "boot"); s.rect((22, 28, 29, 30), "boot")
    s.rect((19, 24, 23, 27), "white")
    return s.done()


# --- timings, and what this verse leaves in the water -----------------------------------------------

BALL_T = [line_t("v2", 1, "Four"), line_t("v2", 1, "through"), line_t("v2", 1, "^my"), line_t("v2", 1, "coat")]
HOLES = [(-3, -22), (4, -17), (-1, -12), (5, -25)]         # from Washington's feet

HAT_LAND, KEG_LAND, CRATE_LAND, LETTER_AT = (152, 128), (176, 134), (128, 142), (202, 124)
T_HAT_OFF = hit(3)                                         # the straw hat blows off as line 3 lands
T_HAT_LAND = T_HAT_OFF + 0.6
T_KEG_OFF = hit(4)                                         # the powder keg jumps off the quay at the big hit
T_KEG_LAND = T_KEG_OFF + 0.55
T_CRATE_OFF = line_t("v2", 10, "hundred")
T_CRATE_LAND = T_CRATE_OFF + 0.5
T_LETTER_DOWN = line_t("v2", 7, "plead")
T_LETTER_ARRIVE = line_t("v2", 8, "take")
T_SEEN = line_t("v2", 8, "^read")
LETTER_SEED = 3

debris(T_HAT_LAND, straw_hat, *HAT_LAND, seed=5, sink=2)
debris(T_KEG_LAND, powder_keg, *KEG_LAND, seed=8, sink=5)
debris(T_CRATE_LAND, hessian_crate, *CRATE_LAND, seed=11, sink=6)
debris(T_SEEN, lambda: olive_letter(True), *LETTER_AT, seed=LETTER_SEED, sink=4)

CANNON_X = 238           # rear of the King's cannon carriage, on the quay
KEG_X = 268
STACK_X = 46             # the crates of Hessians, on the wharf


def arc_into_sea(c, spr, t0, t1, a, b, lift, spin, seed):
    """Something flying from a into the sea at b (its waterline), spinning, then the splash."""
    p = (c.t - t0) / (t1 - t0)
    if 0 <= p < 1:
        x, y = projectile(p, a, (b[0], b[1] - spr.height // 2), lift)
        paste_rot(c.world, spr, x, y, spin * p)
    elif p >= 1:
        splash(c.world, b[0], b[1], c.t - t1, 1.2, seed=seed)


def hat_flight(c):
    arc_into_sea(c, straw_hat(), T_HAT_OFF, T_HAT_LAND, (GEORGE_X - 2, 72), HAT_LAND, 22, 720, 5)


def keg_flight(c):
    arc_into_sea(c, powder_keg(), T_KEG_OFF, T_KEG_LAND, (KEG_X, FEET_Y - 8), KEG_LAND, 34, -540, 8)


def crate_flight(c):
    arc_into_sea(c, hessian_crate(), T_CRATE_OFF, T_CRATE_LAND, (STACK_X, FEET_Y - 40), CRATE_LAND, 30, -400, 11)


# --- 0: "You done?" -----------------------------------------------------------------------------

@gag("v2", 0, pre=0.6)
def you_done(c, L):
    """Close on Washington, who has been timing the King's verse on a pocket watch; it snaps shut."""
    t_done = wt(L, "done")
    w = c.st["washington"]
    w.update(arm="hold", mic=False)
    if c.t < L.t0:
        w.update(mouth="closed", brows="up", eyes="side" if c.t > L.t0 - 0.35 else "open")
    else:
        w.update(brows="up")
    c.take_shot(None, "bostonx")
    shut = c.t >= t_done + 0.08
    yield "front"
    hx, hy = at(c, "washington", "hand")
    paste(c.world, pocket_watch(shut), hx + 6, hy + 13, "mb")
    yield "ui"
    a = c.t - t_done - 0.08
    if 0 <= a < 0.8:
        ux, uy = ui_at(c, hx + 8, hy - 10)
        label(c.ui, (ux, uy + pop(a, drop=4)), "CLICK.", bg=C["paper"], anchor="lb")


# --- 1: "Four balls through my coat on the Monongahela," ---------------------------------------

def draw_holes(c):
    w = c.st["washington"]
    x, y = int(w["x"] + w["dx"]), int(w["y"] + w["dy"])
    d = ImageDraw.Draw(c.world)
    for (hx, hy), tb in zip(HOLES, BALL_T):
        if c.t >= tb:
            d.rectangle((x + hx, y + hy, x + hx + 1, y + hy + 1), fill=(16, 12, 22))
            d.point((x + hx + 2, y + hy - 1), fill=C["navy_hi"])


@gag("v2", 1)
def four_balls(c, L):
    """Four musket balls whip through Washington's coat, one per beat; he glances down, unbothered."""
    cam(c, L, "boston")
    w = c.st["washington"]
    for tb in BALL_T:
        if 0 <= c.t - tb < 0.3:
            w.update(eyes="side")
    t_mon = wt(L, "^on")
    yield "front"
    x, y = int(w["x"] + w["dx"]), int(w["y"] + w["dy"])
    d = ImageDraw.Draw(c.world)
    for k, ((hx, hy), tb) in enumerate(zip(HOLES, BALL_T)):
        age = c.t - tb
        if -0.12 <= age < 0.1:
            bx, by = x + hx - age * 900, y + hy
            d.line([(bx, by), (bx + 14, by)], fill=(255, 236, 190))
            d.rectangle((bx - 1, by - 1, bx, by), fill=C["iron"])
        if 0 <= age < 0.3:
            for j in range(5):
                a = rnd("lint", k, j) * math.pi - math.pi / 2
                r = 2 + age * 30
                d.point((x + hx - math.cos(a) * r, y + hy + math.sin(a) * r * 0.7), fill=C["navy_hi"])
    draw_holes(c)
    yield "ui"
    for k, ((hx, hy), tb) in enumerate(zip(HOLES, BALL_T)):
        if c.t >= tb:
            ux, uy = ui_at(c, x + hx + (-12 if k % 2 == 0 else 12), y + hy - 4)
            pop_text(c.ui, ux, uy, str(k + 1), c.t - tb, PRESS16, top=WHITE, bottom=C["steel_sh"])
    if c.t >= t_mon:
        label(c.ui, (W // 2, 24 + pop(c.t - t_mon)), "BATTLE OF THE MONONGAHELA, 1755", bg=C["paper"],
              anchor="mt")


# --- 2: "two horses shot from under me, and I'm still here to tell ya:" -------------------------

RIDE_DY = -12


@gag("v2", 2)
def two_horses(c, L):
    """He sits on a chestnut: BANG, it's gone in a puff and he hangs in the air a beat before dropping.
    A grey slides in under him: BANG, same again. He dusts himself off. Still here."""
    cam(c, L, "boston")
    s1, t2, s2, t_still = wt(L, "shot"), wt(L, "under"), wt(L, "^me"), wt(L, "still")
    w = c.st["washington"]
    slide = ease_out(ramp(c.t, t2 - 0.25, t2 + 0.05))
    horses = []
    if c.t < s1:
        horses.append(("chestnut", WASH_X))
    if t2 - 0.25 <= c.t < s2:
        horses.append(("grey", int(lerp(-20, WASH_X, slide))))
    if c.t < s1 + 0.15:
        dy = RIDE_DY
    elif c.t < t2 - 0.25:
        dy = int(lerp(RIDE_DY, 0, ease_in(ramp(c.t, s1 + 0.15, s1 + 0.3))))
    elif c.t < s2 + 0.15:
        dy = int(RIDE_DY * slide)
    else:
        dy = int(lerp(RIDE_DY, 0, ease_in(ramp(c.t, s2 + 0.15, s2 + 0.3))))
    w["dy"] += dy
    if any(0 <= c.t - s < 0.15 for s in (s1, s2)):
        w.update(eyes="wide", brows="up", arm="palm")
    elif c.t >= t_still:
        w.update(arm="fist" if c.t - t_still < 0.7 else w["arm"], brows="angry")
    yield "front"
    img = c.world
    for coat, hx in horses:
        paste(img, big_horse(coat), hx, FEET_Y + 4, "mb")
    d = ImageDraw.Draw(img)
    for s in (s1, s2):
        a = c.t - s
        if 0 <= a < 0.06:
            d.line([(170, FEET_Y - 12), (WASH_X + 10, FEET_Y - 12)], fill=(255, 236, 190))
        if 0 <= a < 1.2:
            for k in range(3):
                puff(img, WASH_X - 8 + k * 8, FEET_Y - 10 + (k % 2) * 3, a - k * 0.04, size=1.0,
                     seed=int(s * 10) + k, color=SMOKE, drift=(-4 + k * 4, -8))
    draw_holes(c)
    yield "ui"
    for k, s in enumerate((s1, s2)):
        a = c.t - s
        if 0 <= a < 0.55:
            ux, uy = ui_at(c, WASH_X + 26 + k * 6, 84)
            pop_text(c.ui, ux, uy, "BANG!", a, PRESS16, top=WHITE, bottom=GOLD)
    if c.t >= t_still:
        a = c.t - t_still
        label(c.ui, (228, 30 + pop(a)), "HORSES: 2", bg=C["paper"], anchor="mt")
        if a > 0.3:
            label(c.ui, (228, 44 + pop(a - 0.3)), "WASHINGTON: STILL HERE", bg=C["navy"], fg=C["buff"],
                  anchor="mt")


# --- 3: "Farmer George, you spread manure, but you can't make me sweat." -----------------------

@gag("v2", 3)
def farmer_george(c, L):
    """'Farmer George', the King's nickname: straw hat, pitchfork, a sign. He flings manure west and it
    all drops in the sea. Washington's thermometer falls to a snowflake. At the hit the hat blows off."""
    cam(c, L, "two")
    g = c.st["george"]
    t_farm, t_spread, t_sweat = L.t0, wt(L, "spread"), wt(L, "sweat")
    g.update(hat="off", arm="hold", mic=False)
    if c.t < t_spread:
        g.update(mouth="smirk", eyes="open", brows="up")
    else:
        g.update(mouth="grit", eyes="open", brows="angry")
    w = c.st["washington"]
    if c.t >= t_sweat - 0.2:
        w.update(eyes="shut", mouth="smirk" if c.t > t_sweat + 0.3 else w["mouth"])
    yield "front"
    img = c.world
    if c.t < T_HAT_OFF:
        tx, ty = at(c, "george", "top")
        paste(img, straw_hat(), tx, ty + 8, "mb")
    hat_flight(c)
    hx, hy = at(c, "george", "hand")
    swing = 25 * max(0.0, math.sin((c.t - t_spread) * 2 * math.pi / 0.34)) if c.t >= t_spread else 0.0
    paste_rot(img, pitchfork(), hx, hy - 8, swing)
    for k in range(5):
        tl = t_spread + k * 0.34
        land = (196 - k * 11, 118 + (k % 3) * 7)
        p = (c.t - tl) / 0.7
        if 0 <= p < 1:
            x, y = projectile(p, (hx - 6, hy - 18), land, 22)
            paste(img, dung(), x, y, "mm")
        elif p >= 1:
            splash(img, *land, c.t - tl - 0.7, 0.7, seed=k)
    d = ImageDraw.Draw(img)
    hx2, hy2 = at(c, "george", "head")
    for k in range(3):                                                  # flies
        a = c.t * (8 + k) + k * 2.1
        d.point((hx2 + 12 * math.cos(a), hy2 - 4 + 5 * math.sin(a * 1.4)), fill=INK)
    level = max(1, 12 - int(11 * ramp(c.t, t_spread, t_sweat)))
    tx, ty = WASH_X - 20, 86
    paste(img, thermometer(level), tx, ty, "mm")
    if c.t >= t_sweat:
        paste(img, snowflake(), tx, ty - 17 + int(round(math.sin(c.t * 3))), "mm")
    yield "ui"
    if c.t >= t_farm:
        ux, uy = ui_at(c, GEORGE_X, 58)
        label(c.ui, (ux, uy + pop(c.t - t_farm)), "FARMER GEORGE", bg=(226, 192, 104), anchor="mb")
    if c.t >= t_sweat:
        ux, uy = ui_at(c, tx, ty - 24)
        label(c.ui, (ux, uy + pop(c.t - t_sweat)), "COOL", bg=(210, 236, 255), anchor="mb")


# --- 4: "You're all powder and no ball. I haven't felt it yet." --------------------------------

@gag("v2", 4)
def powder_no_ball(c, L):
    """The King's cannon goes off: a huge cloud of powder smoke, and the ball dribbles out of the muzzle
    and plops into the sea. The barrel wilts. Washington hasn't felt a thing."""
    t_pow, t_ball, t_felt = wt(L, "powder"), wt(L, "^ball"), wt(L, "felt")
    cam(c, L, "london" if c.t < t_felt - 0.1 else "boston")
    g = c.st["george"]
    if c.t < t_ball + 0.3:
        g.update(arm="point", eyes="open", brows="angry" if c.t < t_pow else "up", mouth="smirk")
    else:
        g.update(arm="palm", eyes="open", brows="worried", mouth="o")
    w = c.st["washington"]
    if c.t >= t_felt - 0.1:
        w.update(arm="shrug" if c.t < wt(L, "yet") else w["arm"], brows="up")
    yield "back"
    img = c.world
    if c.t < T_KEG_OFF:
        paste(img, powder_keg(), KEG_X, FEET_Y, "mb")
    keg_flight(c)
    yield "front"
    hat_flight(c)
    rise = ease_out(ramp(c.t, L.t0 - 0.15, L.t0 + 0.15))
    droop = ease_in_out(ramp(c.t, t_ball + 0.15, t_ball + 0.8))
    recoil = int(round(3 * max(0.0, 1 - (c.t - t_pow) / 0.2))) if c.t >= t_pow else 0
    mx, my = cannon(img, CANNON_X, FEET_Y - 1 + int((1 - rise) * 40), droop, recoil)
    if c.t >= t_pow:
        a = c.t - t_pow
        muzzle_flash(img, int(mx), int(my), a, facing=-1, size=2.0)
        for k in range(6):
            puff(img, mx - 4 - k * 8, my - 3 - (k % 2) * 5, a - k * 0.04, size=1.3, seed=40 + k, drift=(-10, -5))
    pb = c.t - t_ball
    if 0 <= pb < 0.25:                                # rolls out of the muzzle...
        paste(img, iron_ball(), mx - 1 - pb * 16, my, "mm")
    elif 0.25 <= pb < 0.55:                           # ...and drops straight into the sea
        q = (pb - 0.25) / 0.3
        paste(img, iron_ball(), mx - 5, my + q * q * 24, "mm")
    elif pb >= 0.55:
        splash(img, int(mx - 5), int(my + 24), pb - 0.55, 0.8, seed=4)
    yield "ui"
    a = c.t - t_ball - 0.55
    if 0 <= a < 1.2:
        ux, uy = ui_at(c, mx - 6, my + 30)
        label(c.ui, (ux, uy + pop(a, drop=4)), "plip.", bg=C["paper"], anchor="mt")
    if t_pow <= c.t < t_felt - 0.1:
        ux, uy = ui_at(c, KEG_X, FEET_Y - 20)
        label(c.ui, (ux, uy + pop(c.t - t_pow, drop=4)), "POWDER", bg=C["paper"], anchor="mb")
    if c.t >= t_felt:
        ux, uy = ui_at(c, WASH_X, 72)
        label(c.ui, (ux + 36, uy + pop(c.t - t_felt)), "DAMAGE: 0", bg=C["navy"], fg=C["buff"], anchor="mb")


# --- 5: "Sure, I lost the Fourth of July in fifty-four. It's true." ---------------------------

CAL = (126, 80)


@gag("v2", 5)
def lost_the_fourth(c, L):
    """A calendar page, JULY 4 1754: Fort Necessity. LOST. He shrugs: it's true."""
    t_lost, t_54, t_true = wt(L, "lost"), wt(L, "fifty"), wt(L, "true")
    cam(c, L, "boston")
    w = c.st["washington"]
    if c.t >= t_true - 0.15:
        w.update(arm="shrug", brows="up", mouth="smirk" if c.t > t_true + 0.3 else w["mouth"])
    yield "back"
    keg_flight(c)
    if c.t < T_KEG_OFF + 0.6:                          # the wilted cannon, for the reaction shot
        cannon(c.world, CANNON_X, FEET_Y - 1, 1.0)
    yield "front"
    age = c.t - L.t0 + 0.1
    if age >= 0:
        paste(c.world, calendar("1754"), CAL[0], CAL[1] + pop(age, drop=10), "mm")
    yield "ui"
    ux, uy = ui_at(c, *CAL)
    if c.t >= t_lost:
        stamp(c.ui, ux, uy + 8, "LOST", color=RED, angle=14, size=16, age=c.t - t_lost)
    if c.t >= t_54:
        label(c.ui, (ux, uy + 46 + pop(c.t - t_54)), "FORT NECESSITY", bg=C["paper"], anchor="mt")


# --- 6: "Now the whole world spends the Fourth celebrating losing you." -------------------------

SHELLS = [(60, 36, (230, 60, 70), 0.0), (130, 24, WHITE, 0.3), (200, 40, (90, 140, 255), 0.55),
          (270, 28, (230, 60, 70), 0.85), (100, 52, GOLD, 1.1), (170, 18, (90, 140, 255), 1.35),
          (30, 22, WHITE, 1.6), (232, 54, GOLD, 1.8), (150, 44, (230, 60, 70), 2.05), (292, 48, WHITE, 2.25)]


def firework(img, x, y, age, color, n=22, speed=52.0, seed=0):
    """A shell that burst at (x, y) `age` seconds ago: streaks falling under gravity, then twinkles."""
    if not 0 <= age < 1.4:
        return
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = 2 * math.pi * i / n + rnd("fw", seed) * 6
        v = speed * (0.75 + 0.25 * rnd("fv", seed, i))

        def pos(tt):
            k = (1 - math.exp(-2.6 * tt)) / 2.6
            return x + math.cos(a) * v * k, y + math.sin(a) * v * k + 16 * tt * tt

        p1 = pos(age)
        if age < 0.85:
            d.line([pos(max(0.0, age - 0.12)), p1], fill=color)
            d.point(p1, fill=WHITE if age < 0.25 else color)
        elif rnd("tw", seed, i, int(age * 16)) < 0.5:
            d.point(p1, fill=color)
    if age < 0.08:
        burst(img, x, y, 2, 6, WHITE, spikes=6)


def rocket(img, a, b, p, lift=30):
    if not 0 <= p < 1:
        return
    d = ImageDraw.Draw(img)
    d.line([projectile(max(0.0, p - 0.08), a, b, lift), projectile(p, a, b, lift)], fill=C["gold_hi"])
    d.point(projectile(p, a, b, lift), fill=WHITE)


@gag("v2", 6)
def fireworks(c, L):
    """The page flips to JULY 4, 1776 and the whole sky goes off over both shores; the last rocket crosses
    the Atlantic and bursts right over the King."""
    t_whole, t_lose = wt(L, "whole"), wt(L, "losing")
    t_hit = hit(6)
    cam(c, L, "boston" if c.t < t_whole - 0.1 else "wide")
    w = c.st["washington"]
    if c.t >= t_whole:
        w.update(arm="wave" if c.beat_i % 2 else "fist", brows="up")
    g = c.st["george"]
    if c.t >= t_whole + 0.6:
        g.update(eyes="open", brows="worried", mouth="frown", arm="cross")
    yield "back"
    img = c.world
    d = ImageDraw.Draw(img)
    for i, (x, y, col, dl) in enumerate(SHELLS):
        tb = t_whole + dl
        p = (c.t - (tb - 0.3)) / 0.3
        if 0 <= p < 1:
            yy = lerp(100, y, ease_out(p))
            d.line([(x, yy), (x, yy + 4)], fill=mix(col, WHITE, 0.5))
        firework(img, x, y, c.t - tb, col, seed=i)
    rocket(img, (90, 96), (GEORGE_X - 8, 60), (c.t - t_lose) / (t_hit - t_lose))
    firework(img, GEORGE_X - 8, 60, c.t - t_hit, GOLD, n=28, speed=60, seed=99)
    yield "front"
    flip = ramp(c.t, L.t0 - 0.1, L.t0 + 0.15)
    if c.t < t_whole + 0.3:
        cal = calendar("1776" if flip >= 0.5 else "1754")
        sq = abs(1 - 2 * flip)
        if sq < 1:
            cal = cal.resize((cal.width, max(1, int(cal.height * sq))), Image.NEAREST)
        paste(img, cal, CAL[0], CAL[1], "mm")
    yield "ui"
    if c.t >= t_whole:
        big_text(c.ui, (W // 2, 22 + pop(c.t - t_whole, drop=10)), "JULY 4, 1776", PRESS16, top=WHITE,
                 bottom=(230, 70, 80), anchor="ma")


# --- 7-8: the Olive Branch Petition ----------------------------------------------------------------

def draw_letter_on_water(c):
    if not T_LETTER_DOWN + 0.25 <= c.t < T_SEEN:
        return
    p = ease_in_out(ramp(c.t, T_LETTER_DOWN + 0.25, T_LETTER_ARRIVE))
    x, y = lerp(BOSTON_EDGE + 10, LETTER_AT[0], p), lerp(132, LETTER_AT[1], p)
    float_on_water(c.world, olive_letter(False), int(x), int(y), c.t, seed=LETTER_SEED, sink=4)


def kneel(c, img, sink=6):
    """Washington on his knees: his sprite cut off at the boots and set lower, knees on the planks."""
    w = c.st["washington"]
    pose = {k: w[k] for k in ("mouth", "eyes", "brows", "arm", "mic", "hat", "flush", "lean", "bob", "bell")}
    spr, a = figure("washington", w["facing"], rim=w["rim"], **pose)
    spr = spr.crop((0, 0, spr.width, 44))
    x, y = int(w["x"] + w["dx"]), int(w["y"] + w["dy"])
    ox, oy = x - a["feet"][0], y - a["feet"][1] + sink
    img.paste(spr, (ox, oy), spr)
    d = ImageDraw.Draw(img)
    d.rectangle((ox + 13, oy + 43, ox + 27, oy + 46), fill=INK)
    d.rectangle((ox + 14, oy + 44, ox + 26, oy + 45), fill=C["buff"])
    return {k: (px + ox, py + oy) for k, (px, py) in a.items()}


@gag("v2", 7)
def olive_branch(c, L):
    """'Left on read'? He raises an eyebrow, then goes down on his knees with the Olive Branch Petition
    and sets it on the water, where it drifts east toward London."""
    t_olive, t_knees = wt(L, "Olive"), wt(L, "knees")
    cam(c, L, "boston")
    w = c.st["washington"]
    if c.t < t_olive:
        w.update(brows="up", eyes="side" if c.t < wt(L, "We") else w["eyes"])
    else:
        w.update(arm="hold" if c.t < T_LETTER_DOWN + 0.1 else "palm", brows="worried", mic=False)
    kneeling = c.t >= t_knees - 0.05
    if kneeling:
        w["hidden"] = True
    yield "back"
    img = c.world
    draw_letter_on_water(c)
    if kneeling:
        c.anchor["washington"] = kneel(c, img)
    yield "front"
    if t_olive - 0.1 <= c.t < T_LETTER_DOWN + 0.25:
        hx, hy = at(c, "washington", "hand")
        p = ease_in_out(ramp(c.t, T_LETTER_DOWN - 0.1, T_LETTER_DOWN + 0.25))
        x, y = lerp(hx + 4, BOSTON_EDGE + 10, p), lerp(hy - 2, 132, p) - 10 * math.sin(p * math.pi)
        paste(img, olive_letter(False), x, y, "mm")
    yield "ui"
    if L.t0 <= c.t < t_olive:
        hx, hy = at(c, "washington", "top")
        ux, uy = ui_at(c, hx + 4, hy - 4)
        pop_text(c.ui, ux, uy - 16, "?", c.t - L.t0, PRESS16, top=WHITE, bottom=C["dim"])
    if c.t >= t_olive:
        label(c.ui, (W // 2, 24 + pop(c.t - t_olive)), "OLIVE BRANCH PETITION · JULY 1775", bg=C["paper"],
              anchor="mt")


@gag("v2", 8)
def continent_on_read(c, L):
    """The petition bobs up to the London quay, still sealed. The King turns his back on it, nose in
    the air (he refused to receive it). On 'read' it gets its receipt: SEEN."""
    t_take, t_cont = wt(L, "wouldn't"), wt(L, "continent")
    cam(c, L, "wide")
    g = c.st["george"]
    turned = t_take - 0.1 <= c.t < T_SEEN + 0.06
    if turned:
        g.update(facing=1, eyes="shut", brows="up", mouth="smirk", arm="cross", rim=0.0)
    w = c.st["washington"]
    if c.t >= wt(L, "^left"):
        w.update(arm="point")
    yield "back"
    draw_letter_on_water(c)
    yield "ui"
    if turned and c.t < t_cont:
        ux, uy = ui_at(c, GEORGE_X + 6, 62)
        label(c.ui, (ux, uy + pop(c.t - t_take)), "HMPH.", bg=WHITE, anchor="mb")
    if T_LETTER_ARRIVE <= c.t < T_SEEN:
        ux, uy = ui_at(c, LETTER_AT[0], LETTER_AT[1] - 12)
        label(c.ui, (ux, uy + pop(c.t - T_LETTER_ARRIVE)), "UNOPENED", bg=C["paper"], anchor="mb")
    if c.t >= t_cont:
        label(c.ui, (W // 2, 24 + pop(c.t - t_cont)), "THE KING REFUSED TO RECEIVE IT", bg=C["paper"],
              anchor="mt")
    a = c.t - T_SEEN
    if 0 <= a < 0.4:
        ux, uy = ui_at(c, LETTER_AT[0] - 6, LETTER_AT[1] - 14)
        burst(c.ui, ux, uy, 3, 6 + a * 20, (160, 200, 255), spikes=8)


# --- 9: "You rented Hessians. I crossed the ice and hit 'em at eight a.m." ---------------------

BOAT_Y = 136
SEA_SHOT = (160, 104, 12)


@gag("v2", 9)
def crossing(c, L):
    """'You rented Hessians': three grenadiers march onto the King's quay, stamped RENTED. Cut to the icy
    river: Washington stands at the bow among the floes, the flag astern, and a clock shows eight."""
    t_hess, t_cross, t_ice, t_eight = wt(L, "rented"), wt(L, "crossed"), wt(L, "^ice"), wt(L, "eight")
    crossing_ = c.t >= t_cross - 0.1
    if crossing_:
        c.shot = SEA_SHOT
    else:
        cam(c, L, "london")
    bx = int(round(lerp(104, 150, ease_in_out(ramp(c.t, t_cross - 0.1, L.t1 + 0.6)))))
    bob = int(round(math.sin(c.t * 2.4)))
    w = c.st["washington"]
    if crossing_:
        w.update(x=bx + 16, y=BOAT_Y - 4 + bob, shadow=False, arm="point", brows="angry", mic=False)
    g = c.st["george"]
    if t_hess <= c.t < t_cross:
        g.update(arm="palm", mouth="smirk", eyes="side", brows="up")
    yield "back"
    img = c.world
    if crossing_:
        for k in range(16):
            fx = 96 + (k * 41) % 150 - (c.t - t_cross) * 10
            fy = 104 + (k * 11) % 46
            if abs(fy - BOAT_Y) < 7 and abs(fx - bx) < 32:
                continue
            float_on_water(img, ice_floe(k), int(fx), int(fy), c.t, seed=k, sink=1, amp=0.5)
        paste(img, big_boat("back"), bx, BOAT_Y + bob - 1, "mb")
        flagpole(img, bx - 26, BOAT_Y - 30 + bob, BOAT_Y + bob, "grand_union", c.t, flip=True)
        for k, rx in enumerate((bx - 16, bx - 5)):
            paste(img, rower((int(c.t * 2.4) + k) % 2), rx, BOAT_Y + bob + 1, "mb")
    yield "front"
    if crossing_:
        paste(img, big_boat("front"), bx, BOAT_Y + bob + 4, "mb")
        d = ImageDraw.Draw(img)
        for k in range(36):
            sx = 80 + (rnd("snow-x", k) * 170 - c.t * 12) % 170
            sy = 60 + (rnd("snow-y", k) * 92 + c.t * 22) % 92
            d.point((sx, sy), fill=WHITE)
    else:
        for k in range(3):
            t_in = t_hess + k * 0.18
            arrive = ease_out(ramp(c.t, t_in, t_in + 0.45))
            if arrive > 0:
                hx = int(lerp(340, 274 + k * 19, arrive))
                paste(img, big_hessian(1 if arrive < 1 and (c.f // 3 + k) % 2 else 0), hx, FEET_Y + 1, "mb")
    yield "ui"
    if not crossing_ and c.t >= t_hess:
        ux, uy = ui_at(c, 287, 68)
        label(c.ui, (ux, uy + pop(c.t - t_hess)), "HESSIANS FOR HIRE", bg=C["paper"], anchor="mb")
        if c.t >= t_hess + 0.35:
            stamp(c.ui, ux, uy + 74, "RENTED", color=RED, angle=10, size=16, age=c.t - t_hess - 0.35)
    if crossing_ and c.t >= t_ice:
        label(c.ui, (W // 2, 24 + pop(c.t - t_ice)), "THE DELAWARE · CHRISTMAS NIGHT, 1776", bg=C["paper"],
              anchor="mt")
    if crossing_ and c.t >= t_eight - 0.1:
        a = c.t - t_eight + 0.1
        cx, cy = 290, 50
        paste(c.ui, clock_face(), cx, cy + pop(a), "mm")
        label(c.ui, (cx, cy + 14 + pop(a)), "8:00 A.M.", bg=C["band"], fg=GOLD, anchor="mt")


# --- 10: "Boxing Day in Trenton? I boxed up nine hundred of 'em." -------------------------------

STACK = [(-10, 0), (10, 0), (-10, -15), (10, -15), (0, -30)]
T_LOB = line_t("v2", 10, "^of")


def crate_lob(c):
    """One more crate, lobbed from the stack across the Atlantic onto the King's head at the big hit
    (which lands after line 10's gag has handed over, so line 11 draws the end of it too)."""
    t_hit = hit(10)
    p = (c.t - T_LOB) / (t_hit - T_LOB)
    if 0 <= p < 1:
        x, y = projectile(p, (STACK_X + 10, FEET_Y - 25), (GEORGE_X - 2, 72), 44)
        paste_rot(c.world, hessian_crate(), x, y, -p * 360)
    elif p >= 1 and c.t - t_hit < 0.5:
        a = c.t - t_hit
        x, y = projectile(a / 0.5, (GEORGE_X - 2, 70), (GEORGE_X + 30, FEET_Y - 8), 16)
        paste_rot(c.world, hessian_crate(), x, y, -360 - a * 500)
        if a < 0.12:
            burst(c.world, GEORGE_X - 2, 68, 3, 10, WHITE, spikes=8)
    elif c.t - t_hit < 1.2:
        paste(c.world, hessian_crate(), GEORGE_X + 30, FEET_Y + 1, "mb")


@gag("v2", 10)
def boxing_day(c, L):
    """Trenton on Boxing Day: gift-wrapped crates stack up on the wharf, a Hessian cap poking out of each.
    x900. The top one topples into the sea; another is lobbed all the way to London, onto the King."""
    t_900, t_lob = wt(L, "nine"), T_LOB
    cam(c, L, "two")
    pops = [wt(L, "Boxing"), wt(L, "Day"), wt(L, "Trenton"), wt(L, "boxed"), wt(L, "^up")]
    w = c.st["washington"]
    if c.t >= t_lob - 0.1:
        w.update(arm="point")
    yield "back"
    img = c.world
    for k, ((dx, dy), tp) in enumerate(zip(STACK, pops)):
        if c.t < tp - 0.05 or (k == 4 and c.t >= T_CRATE_OFF) or (k == 3 and c.t >= t_lob):
            continue
        paste(img, hessian_crate(), STACK_X + dx, FEET_Y + 1 + dy + pop(c.t - tp + 0.05, drop=12), "mb")
    yield "front"
    crate_flight(c)
    crate_lob(c)
    yield "ui"
    if c.t >= L.t0:
        label(c.ui, (W // 2, 24 + pop(c.t - L.t0)), "TRENTON · 26 DEC 1776", bg=C["paper"], anchor="mt")
    if c.t >= t_900:
        ux, uy = ui_at(c, STACK_X + 14, 50)
        pop_text(c.ui, ux, uy, "×900", c.t - t_900, PRESS16, top=WHITE, bottom=GOLD)


# --- 11: "You never came to fight yourself, so we melted down your statue:" ---------------------

STATUE_X = 42
POT_Y = FEET_Y + 1                       # the cauldron stands on the wharf
MELT_Y = POT_Y - 21                      # its molten surface


def draw_cauldron(c, img, t0, sinking=None):
    """The cauldron on its fire, rising into place at t0; `sinking` = (depth px, heat 0-1) sinks the
    statue into it."""
    rise = ease_out(ramp(c.t, t0, t0 + 0.2))
    if rise <= 0:
        return
    dy = int((1 - rise) * 30)
    d = ImageDraw.Draw(img)
    for k in range(9):
        fx = STATUE_X - 12 + k * 3
        h = 3 + int(4 * abs(math.sin(c.t * 9 + k * 1.3)))
        d.line([(fx, POT_Y + dy), (fx, POT_Y + dy - h)], fill=(255, 150, 40) if k % 2 else (255, 220, 90))
    if sinking:
        depth, heat = sinking
        spr = hot_statue(int(round(heat * 4)))
        top = MELT_Y + dy + 4 + depth - spr.height
        keep = MELT_Y + dy + 1 - top
        if keep > 0:
            paste(img, spr.crop((0, 0, spr.width, min(spr.height, keep))), STATUE_X, top, "mt")
    paste(img, cauldron_img(), STATUE_X, POT_Y + dy, "mb")
    for k in range(4):
        a = (c.t * 1.6 + k / 4) % 1
        d.point((STATUE_X - 9 + k * 6, MELT_Y + dy - 3 - a * 7), fill=C["gold_hi"] if a < 0.5 else C["gold_sh"])


def splash_gold(img, x, y, age):
    if not 0 <= age < 0.5:
        return
    d = ImageDraw.Draw(img)
    for k in range(10):
        a = math.pi * (0.1 + 0.8 * rnd("gs", k))
        v = 40 + 30 * rnd("gv", k)
        d.point((x + math.cos(a) * v * age, y - math.sin(a) * v * age + 120 * age * age),
                fill=GOLD if k % 2 else C["gold_hi"])


@gag("v2", 11)
def melted_statue(c, L):
    """The King never once set foot in America; his gilded statue on Bowling Green did. On 'melted' it
    drops off its pedestal into a cauldron and sinks away, glowing."""
    t_never, t_melt, t_stat = wt(L, "never"), wt(L, "melted"), wt(L, "statue")
    cam(c, L, "two")
    g = c.st["george"]
    if c.t < t_melt:
        g.update(arm="cross", eyes="shut", brows="up", mouth="smirk")
    else:
        g.update(eyes="wide", brows="worried", mouth="o", arm="palm")
    yield "back"
    img = c.world
    if c.t < hit(10) + 1.2:
        crate_lob(c)
    rise = ease_out(ramp(c.t, L.t0 - 0.1, L.t0 + 0.25))
    base = FEET_Y + 1 + int((1 - rise) * 60)
    t_drop = t_melt - 0.2
    if c.t < t_drop:
        paste(img, pedestal(), STATUE_X, base, "mb")
        paste(img, statue_img(), STATUE_X, base - 12, "mb")
    else:
        fall = ease_in(ramp(c.t, t_drop, t_drop + 0.2))
        sink = ramp(c.t, t_drop + 0.2, t_stat + 0.1)
        if fall < 1:
            spr = statue_img()
            bottom = lerp(base - 12, MELT_Y + 6, fall)
            keep = int(MELT_Y + 1 - (bottom - spr.height))
            if keep > 0:
                paste(img, spr.crop((0, 0, spr.width, min(spr.height, keep))), STATUE_X, bottom - spr.height, "mt")
            draw_cauldron(c, img, t_drop - 0.2)
        else:
            draw_cauldron(c, img, t_drop - 0.2, sinking=(int(2 + sink * 50), sink))
        splash_gold(img, STATUE_X, MELT_Y, c.t - (t_drop + 0.2))
    yield "ui"
    if c.t >= t_never:
        ux, uy = ui_at(c, GEORGE_X, 64)
        label(c.ui, (ux - 20, uy + pop(c.t - t_never)), "NEVER SET FOOT IN AMERICA", bg=C["paper"],
              anchor="mb")
    if c.t >= t_melt:
        label(c.ui, (W // 2, 24 + pop(c.t - t_melt)), "BOWLING GREEN, N.Y. · 9 JULY 1776", bg=C["paper"],
              anchor="mt")


# --- 12: "forty-two thousand bullets, George. We fired you back at you." -----------------------

N_BALLS = 96


@gag("v2", 12)
def bullets(c, L):
    """The statue became 42,088 cartridges: they pour out of the cauldron in a golden hail over the
    Atlantic onto the London quay; the counter runs up and the King's crown gets knocked askew."""
    t_back, t_hit = wt(L, "fired"), hit(12)
    t0, t1 = L.t0, t_hit - 1.05
    cam(c, L, "wide")
    g = c.st["george"]
    if c.t >= t0 + 0.9:
        g.update(eyes="wide", brows="worried", mouth="o", arm="palm", sweat=True)
    if c.t >= t_back:
        g.update(hat="askew")
    yield "back"                                       # the hail flies behind the characters
    img = c.world
    draw_cauldron(c, img, -1.0)
    d = ImageDraw.Draw(img)
    src = (STATUE_X + 2, MELT_Y - 2)
    for i in range(N_BALLS):
        tl = t0 + (t1 - t0) * i / N_BALLS + rnd("bt", i) * 0.1
        tgt = (224 + rnd("bx", i) * 66, 66 + rnd("by", i) * 48)
        lift = 22 + rnd("bl", i) * 18
        p = (c.t - tl) / 0.8
        if 0 <= p < 1:
            x0, y0 = projectile(max(0.0, p - 0.05), src, tgt, lift)
            x, y = projectile(p, src, tgt, lift)
            d.line([(x0, y0), (x, y)], fill=C["gold_sh"])
            d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=INK)
            d.rectangle((x - 1, y, x, y), fill=C["gold_hi"])
            d.point((x + 1, y), fill=GOLD)
        elif 1 <= p < 1.25:
            sparkle(img, int(tgt[0]), int(tgt[1]), 1, C["gold_hi"])
    yield "ui"
    n = int(42088 * ease_out(ramp(c.t, t0, t1 + 0.5)))
    big_text(c.ui, (W // 2, 18), f"{n:,}", PRESS24, top=C["gold_hi"], bottom=GOLD, anchor="ma")
    label(c.ui, (W // 2, 45), "MUSKET CARTRIDGES, CAST FROM ONE KING", bg=C["band"], fg=GOLD, anchor="mt")


# --- 13-14: the quarter -----------------------------------------------------------------------------

HOUSE_X = 30


@gag("v2", 13)
def quarters(c, L):
    """'Quarters in our houses': a redcoat quartered in a Boston house, boots out the front door.
    'Here's a quarter': Washington flips a coin and it spins all the way across to the King's hand."""
    t_q, t_flip = wt(L, "quarters"), wt(L, "quarter", 1)
    t_catch = t_flip + 1.0
    cam(c, L, "boston")
    if c.t >= t_flip + 0.15:
        pan(c, "boston", "london", t_flip + 0.15, 0.85)
    w, g = c.st["washington"], c.st["george"]
    if t_flip - 0.4 <= c.t < t_flip + 0.5:
        w.update(arm="palm" if c.t >= t_flip else "hold", brows="up")
    g["hat"] = "askew"                                  # since the 42,088 cartridges
    if c.t >= t_catch - 0.3:
        g.update(arm="hold", mic=False, eyes="open", brows="up", mouth="o")
    yield "back"
    if c.t >= t_q - 0.1:
        paste(c.world, quartered_house(), HOUSE_X, FEET_Y + 1 + pop(c.t - t_q + 0.1, drop=14), "mb")
    yield "front"
    img = c.world
    p = (c.t - t_flip) / (t_catch - t_flip)
    wh, gh = at(c, "washington", "hand"), at(c, "george", "hand")
    if 0 <= p < 1:
        x, y = projectile(p, (wh[0] + 2, wh[1] - 4), (gh[0], gh[1] - 3), 34)
        paste(img, spin_x(small_coin(int(c.t * 8) % 2 == 0), c.t, 4.0), x, y, "mm")
        if p < 0.25 and c.f % 2:
            sparkle(img, int(x) + 3, int(y) - 4, 2, WHITE)
    elif p >= 1:
        paste(img, small_coin(), gh[0], gh[1] - 3, "mm")
    yield "ui"
    if c.t >= t_q:
        ux, uy = ui_at(c, HOUSE_X, FEET_Y - 34)
        label(c.ui, (ux, uy + pop(c.t - t_q)), "QUARTERING ACT", bg=C["paper"], anchor="mb")


@gag("v2", 14, post=0.45)
def my_face(c, L):
    """The King looks at the coin, and there, blown up, is Washington's profile on the quarter.
    'I'm the currency of this land': it rains quarters on the London quay."""
    t_face, t_cur = wt(L, "face"), wt(L, "currency")
    t_hit = hit(14)
    c.shot = "london"
    g = c.st["george"]
    g.update(arm="hold", mic=False, hat="askew")
    if c.t < t_face:
        g.update(eyes="open", brows="up", mouth="closed")
    else:
        g.update(eyes="wide", brows="worried", mouth="o")
    if c.t >= t_cur:
        g.update(sweat=True)
    yield "front"
    img = c.world
    gh = at(c, "george", "hand")
    paste(img, small_coin(), gh[0], gh[1] - 3, "mm")
    if c.t >= t_cur:
        d = ImageDraw.Draw(img)
        for k in range(64):
            age = c.t - (t_cur + rnd("qt", k) * 1.1)
            if age < 0:
                continue
            x = 196 + rnd("qx", k) * 124
            y = 30 + age * 40 + 150 * age * age
            if y < FEET_Y - 2:
                paste(img, spin_x(small_coin(k % 2 == 0), age + k, 3.0), x, y, "mm")
            else:
                d.rectangle((x - 2, FEET_Y - 1, x + 2, FEET_Y), fill=SILVER)
                d.point((x - 1, FEET_Y - 1), fill=WHITE)
    yield "ui"
    a = c.t - t_face
    if a >= 0:
        s = back_out(a / 0.22) if a < 0.22 else 1.0
        out = ease_in(ramp(c.t, t_hit - 0.45, t_hit - 0.1))
        paste(c.ui, scaled(quarter_face(), max(0.05, s)), 78 - int(out * 150), 80, "mm")
