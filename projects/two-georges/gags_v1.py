"""Verse 1: King George III raps from the London quay, Washington listens on the Boston wharf (v1 0-15).

A running gag holds the verse together: George's "Kneel" in the first line sends a royal
kneeling cushion across the Atlantic. It lies ignored at Washington's feet all verse, and
on the last "Kneel." he punts it into the sea.
"""
from gagkit import (C, FEET_Y, GEORGE_X, HORIZON, INK, PRESS, PRESS16, SILK, TL, H, W, WASH_X, Canvas, Image,
                    ImageDraw, anchor, back_out, big_text, burst, char_sprite, clamp, crown_sprite, debris, dither, ease_in,
                    ease_in_out, ease_out, envelope, flag_cloth, fly, gag, label, lerp, line_t, lru_cache, math,
                    mix, muzzle_flash, np, outlined, pan, parchment, paste, paste_rot, pop_dy, projectile, puff, ramp, rnd, span, splash,
                    sparkle, stamp, strike, teacup, text_width, waving, wobble, wt)

WX, GX, FY = WASH_X, GEORGE_X, FEET_Y
CUSHION = (94, FY)                 # where the kneeling cushion lies on the Boston wharf (centre, bottom)
LIGHT_BLUE = (170, 214, 255)
KRAFT, KRAFT_SH = (214, 176, 120), (168, 128, 88)
GRASS, GRASS_HI, SOIL = (100, 160, 80), (150, 196, 100), (120, 84, 58)
PINE, PINE_HI = (46, 96, 70), (70, 130, 84)
FLAME, FLAME_HI, FLAME_DK = (255, 160, 40), (255, 230, 120), (220, 70, 40)
CLOUD, CLOUD_DK = (92, 84, 118), (64, 58, 90)
TICK_BLUE = (52, 104, 196)


# --- timing -----------------------------------------------------------------------------------

def onset_after(t, gap=0.2, quiet=0.08, loud=0.3, within=2.0):
    """First loud vocal frame after a quiet stretch that starts after t (for words Whisper mistimed)."""
    env, fps = TL.ENV, TL.FPS
    f, end = int(t * fps), min(len(TL.ENV), int((t + within) * fps))
    while f < end and env[f] >= quiet:
        f += 1
    q = f
    while q < end and env[q] < quiet:
        q += 1
    if q - f < gap * fps:
        return None
    while q < end and env[q] < loud:
        q += 1
    return q / fps if q < end else None


def _cushion_times():
    kneel0 = line_t("v1", 0, "Kneel")
    kneel15 = line_t("v1", 15, "Kneel")
    return kneel0 + 0.55, kneel0 + 1.4, kneel15 + 0.3, kneel15 + 0.85   # throw, land, kick, splash


T_THROW, T_LAND, T_KICK, T_SPLASH = _cushion_times()
T_DONE = onset_after(line_t("v1", 15, "Kneel")) or line_t("v1", 15, "done")   # "I'm done" (Whisper is late)


# --- sprites -----------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def cushion():
    """A royal red velvet kneeling cushion: plump, buttoned, gold piping and corner tassels."""
    s = Canvas(24, 12)
    s.ell((2, 2, 21, 9), "red")
    s.rect((4, 2, 19, 9), "red")
    s.ell((5, 2, 17, 5), "red_hi")
    s.line([(4, 9), (19, 9)], "red_sh")
    s.line([(3, 7), (20, 7)], "gold_sh")
    for x0, x1 in ((7, 11), (12, 16)):
        s.line([(x0, 4), (x1, 6)], "red_sh")
    s.px((11, 5), "gold_hi"); s.px((12, 5), "gold")
    for x in (2, 21):
        s.px((x, 8), "gold"); s.px((x, 9), "gold"); s.px((x, 10), "gold_sh")
    return s.done()


@lru_cache(maxsize=None)
def paper_crown():
    """A party-hat crown cut out of brown paper."""
    s = Canvas(22, 13)
    s.poly([(1, 11), (1, 4), (5, 7), (8, 1), (11, 7), (14, 1), (17, 7), (20, 4), (20, 11)], KRAFT)
    s.line([(1, 11), (20, 11)], KRAFT_SH)
    s.line([(2, 9), (19, 9)], KRAFT_SH)
    s.pxs([(8, 2), (14, 2), (4, 6), (19, 6)], (240, 214, 170))
    s.pxs([(6, 10), (10, 10), (14, 10)], "flag_red")
    return s.done()


@lru_cache(maxsize=None)
def money_bag(bow=False):
    s = Canvas(18, 18)
    tan, tan_hi, tan_sh = (196, 168, 112), (226, 204, 150), (150, 120, 80)
    s.ell((1, 5, 16, 16), tan)
    s.rect((6, 2, 11, 6), tan)
    s.ell((3, 6, 8, 11), tan_hi)
    s.line([(4, 15), (13, 15)], tan_sh)
    s.line([(5, 5), (12, 5)], "wood_sh")
    s.text((9, 8), "£", "gold_sh", fnt=PRESS, anchor="ma")
    if bow:
        s.poly([(4, 3), (8, 5), (4, 7)], "white"); s.poly([(13, 3), (9, 5), (13, 7)], "white")
        s.px((8, 5), "white_sh"); s.px((9, 5), "white_sh")
    return s.done()


@lru_cache(maxsize=None)
def parcel(tree=False):
    """A slab of Virginia: turf on top, soil below, a rail fence (and maybe a tree)."""
    s = Canvas(20, 14)
    s.rect((1, 8, 18, 12), SOIL)
    s.rect((1, 6, 18, 8), GRASS)
    s.line([(1, 6), (18, 6)], GRASS_HI)
    s.line([(1, 12), (18, 12)], (90, 60, 46))
    for x in (2, 7, 12, 17):
        s.line([(x, 3), (x, 6)], "wood_hi")
    s.line([(2, 4), (17, 4)], "wood")
    if tree:
        s.ell((10, 0, 16, 5), PINE); s.px((12, 1), PINE_HI)
    return s.done()


@lru_cache(maxsize=None)
def pine():
    s = Canvas(15, 26)
    for (top, bot, half) in ((1, 9, 4), (5, 15, 5), (10, 21, 6)):
        s.poly([(7, top), (7 + half, bot), (7 - half, bot)], PINE)
        s.line([(7, top), (7 + half - 1, bot - 1)], PINE_HI)
    s.rect((6, 22, 8, 24), "wood_sh")
    return s.done()


@lru_cache(maxsize=None)
def baby_flame(frame=0):
    """A newborn fire with a face, swaddled in a white blanket."""
    s = Canvas(16, 20)
    lean = 1 if frame else -1
    s.poly([(8 + lean, 1), (12, 7), (13, 12), (3, 12), (4, 7), (6 + lean, 4)], FLAME)
    s.poly([(8 + lean, 5), (11, 10), (5, 10), (7, 7)], FLAME_HI)
    s.pxs([(6, 9), (10, 9)], "ink")
    s.rect((7, 10, 9, 11), "mouth")
    s.ell((1, 10, 14, 18), "white")
    s.line([(3, 13), (12, 16)], "white_sh")
    s.px((12, 12), "white_sh")
    return s.done()


@lru_cache(maxsize=None)
def cloud(frame=0):
    s = Canvas(46, 16)
    for (x0, y0, x1, y1) in ((2, 5, 16, 14), (10, 1, 26, 13), (22, 3, 36, 14), (32, 6, 44, 14)):
        s.ell((x0, y0, x1, y1), CLOUD)
    s.rect((4, 10, 42, 14), CLOUD_DK)
    s.ell((12, 2, 20, 7), (120, 110, 150))
    return s.done()


@lru_cache(maxsize=None)
def keg(wet=False):
    s = Canvas(14, 16)
    s.rect((3, 1, 10, 14), "wood"); s.rect((2, 3, 11, 12), "wood")
    s.line([(4, 1), (4, 14)], "wood_hi")
    for y in (3, 12):
        s.line([(2, y), (11, y)], "iron")
    s.rect((3, 6, 10, 9), "paper")
    if wet:
        s.rect((3, 1, 10, 2), LIGHT_BLUE)
        s.pxs([(2, 5), (11, 8), (6, 14)], LIGHT_BLUE)
    return s.done()


@lru_cache(maxsize=None)
def book():
    """An open book held up for inspection."""
    s = Canvas(18, 12)
    s.poly([(1, 2), (8, 1), (8, 10), (1, 10)], "white"); s.poly([(9, 1), (16, 2), (16, 10), (9, 10)], "white")
    s.line([(8, 1), (8, 10)], "white_sh")
    for y in (4, 6, 8):
        s.line([(2, y), (6, y)], "dim"); s.line([(10, y), (15, y)], "dim")
    s.line([(1, 10), (16, 10)], "red_sh"); s.line([(0, 2), (0, 10)], "red_sh"); s.line([(17, 2), (17, 10)], "red_sh")
    return s.done()


@lru_cache(maxsize=None)
def revenue_stamp(poison=False):
    """A Stamp Act revenue stamp: a red embossed seal with the crown."""
    s = Canvas(20, 20)
    s.ell((1, 1, 18, 18), "wax")
    s.ell((3, 3, 16, 16), "red_hi")
    s.ell((4, 4, 15, 15), "wax")
    s.rect((6, 7, 13, 9), "gold"); s.pxs([(6, 5), (6, 6), (9, 4), (9, 5), (9, 6), (13, 5), (13, 6)], "gold")
    s.rect((6, 11, 13, 12), "gold_sh")
    if poison:
        s.ell((5, 4, 14, 12), "white"); s.rect((7, 12, 12, 14), "white")
        s.rect((7, 7, 8, 8), "ink"); s.rect((11, 7, 12, 8), "ink")
        s.pxs([(8, 13), (10, 13)], "ink")
        s.line([(2, 16), (17, 3)], "white"); s.line([(2, 3), (17, 16)], "white")
    return s.done()


@lru_cache(maxsize=None)
def cannon():
    """A naval gun on its carriage, muzzle to the left."""
    s = Canvas(22, 11)
    s.poly([(1, 3), (15, 2), (18, 3), (18, 6), (15, 7), (1, 6)], "iron")
    s.line([(2, 3), (15, 2)], "iron_hi")
    s.rect((0, 3, 1, 6), "iron")
    s.rect((9, 6, 20, 8), "wood"); s.line([(9, 6), (20, 6)], "wood_hi")
    s.ell((10, 7, 14, 10), "wood_sh"); s.ell((16, 7, 20, 10), "wood_sh")
    return s.done()


@lru_cache(maxsize=None)
def invoice_roll():
    s = Canvas(12, 8)
    s.rect((1, 1, 10, 6), "paper"); s.line([(1, 6), (10, 6)], "paper_sh")
    s.ell((4, 2, 7, 5), "wax")
    return s.done()


@lru_cache(maxsize=None)
def invoice_sheet():
    """The bill for the Seven Years' War, as held up by the man it was sent to."""
    lines = ["FOR: 1 WAR", "PAYABLE BY:", "THE COLONIES"]
    w = max(text_width("INVOICE", PRESS), *(text_width(s_, SILK) for s_ in lines)) + 8
    h = 60
    im = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
    parchment(im, (3, 3, w + 2, h + 2), title="INVOICE", lines=lines, rolled=True)
    return im


@lru_cache(maxsize=None)
def invoice_float():
    im = Image.new("RGBA", (26, 14), (0, 0, 0, 0))
    parchment(im, (2, 3, 23, 12), lines=["~"], rolled=True)
    return im


@lru_cache(maxsize=None)
def placard(text_="TYRANNY!"):
    w = text_width(text_, SILK) + 8
    s = Canvas(w + 2, 26)
    s.rect((w // 2, 12, w // 2 + 1, 24), "wood")
    s.rect((1, 1, w, 12), "paper")
    s.line([(1, 12), (w, 12)], "paper_sh")
    s.text((w // 2 + 1, -1), text_, "flag_red", fnt=SILK, anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def letter_pile(n):
    """Washington's letters stacking up unopened on the London quay."""
    im = Image.new("RGBA", (24, 26), (0, 0, 0, 0))
    e = envelope(14, 9, seal=True)
    for i in range(n):
        x = 1 + int(rnd("lp", i) * 6)
        paste(im, e, x, 26 - 11 - i * 3, "lt")
    return im


@lru_cache(maxsize=None)
def letter_bundle():
    s = Canvas(18, 12)
    for i, (x, y) in enumerate(((1, 4), (4, 2), (3, 6))):
        s.rect((x, y, x + 12, y + 5), "paper"); s.line([(x, y + 5), (x + 12, y + 5)], "paper_sh")
    s.line([(9, 2), (9, 11)], "flag_red"); s.line([(1, 7), (16, 7)], "flag_red")
    return s.done()


@lru_cache(maxsize=None)
def slip(text_="REJECT", angle=-8):
    """A red rubber stamp on its own paper slip, tilted (so it reads over busy backgrounds)."""
    tw = text_width(text_, PRESS)
    im = Image.new("RGBA", (tw + 14, 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((1, 1, tw + 12, 16), fill=C["paper"] + (255,), outline=INK + (255,))
    d.rectangle((3, 3, tw + 10, 14), outline=C["flag_red"] + (255,))
    d.text((7, 5), text_, font=PRESS, fill=C["flag_red"] + (255,))
    return im.rotate(angle, resample=Image.NEAREST, expand=True)


@lru_cache(maxsize=None)
def musket():
    s = Canvas(28, 8)
    s.line([(1, 5), (8, 4)], "wood", 2)
    s.line([(8, 4), (26, 2)], "iron")
    s.line([(8, 5), (20, 4)], "wood_sh")
    s.px((10, 3), "steel")
    return s.done()


@lru_cache(maxsize=None)
def candle(frame=0):
    s = Canvas(8, 15)
    s.rect((2, 7, 5, 12), "white"); s.line([(2, 12), (5, 12)], "white_sh")
    s.rect((1, 12, 6, 13), "gold_sh")
    s.px((3, 6), "ink")
    fx = 3 + frame
    s.poly([(fx, 1), (5, 4), (4, 6), (2, 6), (2, 4)], FLAME)
    s.px((3, 4), FLAME_HI); s.px((3, 5), FLAME_HI)
    return s.done()


@lru_cache(maxsize=None)
def mic_prop():
    s = Canvas(6, 11)
    s.rect((2, 4, 3, 9), "mic")
    s.ell((1, 1, 4, 4), "mic_hi"); s.px((2, 2), "white")
    return s.done()


@lru_cache(maxsize=None)
def white_flag_float():
    s = Canvas(20, 8)
    s.line([(1, 5), (18, 5)], "wood_sh")
    s.poly([(2, 1), (11, 2), (10, 5), (2, 5)], "white")
    return s.done()


def redcoat_washington():
    """Washington as he dreamt of himself: in a British officer's red coat, saluting."""
    img = char_sprite("washington", 1, arm="wave", eyes="shut", mouth="smile")
    a = np.array(img)
    swap = {C["navy"]: C["red"], C["navy_sh"]: C["red_sh"], C["navy_hi"]: C["red_hi"]}
    for src, dst in swap.items():
        a[np.all(a[..., :3] == src, axis=-1), :3] = dst
    return Image.fromarray(a)


_REDCOAT = None


def redcoat_sprite():
    global _REDCOAT
    if _REDCOAT is None:
        _REDCOAT = redcoat_washington()
    return _REDCOAT


# --- small drawing helpers ------------------------------------------------------------------------

def heart(img, x, y, col=(236, 90, 110)):
    d = ImageDraw.Draw(img)
    x, y = int(x), int(y)
    d.point([(x - 1, y), (x + 1, y), (x - 2, y + 1), (x - 1, y + 1), (x, y + 1), (x + 1, y + 1), (x + 2, y + 1),
             (x - 1, y + 2), (x, y + 2), (x + 1, y + 2), (x, y + 3)], fill=col)


def ticks(img, x, y, col=TICK_BLUE):
    """Two read-receipt ticks, 11x5 from (x, y)."""
    d = ImageDraw.Draw(img)
    for ox in (0, 5):
        d.line([(x + ox, y + 2), (x + ox + 2, y + 4), (x + ox + 6, y)], fill=col)


def rain_under(img, x0, x1, y0, y1, t, density=1.0, seed=0):
    d = ImageDraw.Draw(img)
    n = int((x1 - x0) * 0.6 * density)
    for i in range(n):
        x = x0 + rnd("rv", seed, i) * (x1 - x0)
        yy = y0 + (rnd("rvy", seed, i) * (y1 - y0) + t * 160) % (y1 - y0)
        d.line([(x, yy), (x - 1, yy + 4)], fill=LIGHT_BLUE)


def firework(img, x, y, age, col, seed=0, n=14, r=16):
    """A rocket burst: sparks flying out and drooping, then fading."""
    if not 0 <= age < 1.1:
        return
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = i * 2 * math.pi / n + rnd("fw", seed) * 0.5
        rr = r * ease_out(age / 0.5)
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr + 14 * age * age
        if age < 0.8 or (i + int(age * 20)) % 2:
            d.rectangle((int(px), int(py), int(px) + 1, int(py) + 1), fill=col)
            if age < 0.45:
                d.point((int(px - math.cos(a) * 2), int(py - math.sin(a) * 2)), fill=mix(col, (255, 255, 255), 0.5))


def rocket(img, x, y0, y1, p):
    """A rocket climbing from y0 to y1 with a spark trail (p in [0, 1])."""
    if not 0 <= p < 1:
        return
    d = ImageDraw.Draw(img)
    y = lerp(y0, y1, ease_out(p))
    d.line([(x, y), (x, y + 5)], fill=C["gold"])
    d.point((x, y - 1), fill=C["gold_hi"])


def dust(img, x, y, age, seed=0):
    if not 0 <= age < 0.4:
        return
    d = ImageDraw.Draw(img)
    for i in range(6):
        a = math.pi * (i / 5)
        r = 2 + age * 20
        d.point((int(x + math.cos(a) * r), int(y - math.sin(a) * r * 0.4)), fill=(220, 200, 170))


def cushion_on_wharf(img, t):
    paste(img, cushion(), CUSHION[0], CUSHION[1] + 1, "mb")


def reaction_shot(c, L, who="washington"):
    """The default cut to the listener after a big hit (for gags that hold the camera)."""
    if c.t >= TL.hit_of(L.ln)["t"]:
        c.shot = "boston" if who == "washington" else "london"


# --- the running gag: the kneeling cushion ---------------------------------------------------------

@span(T_LAND, T_KICK)
def cushion_waits(c, L):
    """The cushion lies ignored on the Boston wharf all verse."""
    yield "front"
    cushion_on_wharf(c.world, c.t)


# --- line gags ------------------------------------------------------------------------------------

@gag("v1", 0, pre=0.6)
def kneel(c, L):
    """'Kneel': George points at the ground and lobs a royal kneeling cushion across the Atlantic. It
    lands at Washington's feet on 'Crown'; he looks down at it, then back up, unmoved."""
    t_kneel, t_word = wt(L, "Kneel"), wt(L, "word")
    g, w = c.st["george"], c.st["washington"]
    c.shot = "london"
    if c.t >= T_THROW - 0.1:
        pan(c, "london", "wide", T_THROW - 0.1, 0.7)
    if c.t >= T_LAND + 0.25:
        pan(c, "wide", "boston", T_LAND + 0.25, 0.6)
    if t_kneel <= c.t < T_THROW:
        g.update(arm="chop", brows="up")
    elif T_THROW <= c.t < T_THROW + 0.35:
        g.update(arm="wave")
    w.update(arm="cross", mouth="closed")
    if c.t >= T_LAND:
        w.update(eyes="blink" if c.t < t_word else "open", brows="up", mouth="frown" if c.t < t_word else "closed")
    yield "front"
    if T_THROW <= c.t < T_LAND:
        p = (c.t - T_THROW) / (T_LAND - T_THROW)
        x, y = projectile(p, (GX - 16, 98), (CUSHION[0], CUSHION[1] - 3), 46)
        paste_rot(c.world, cushion(), x, y, int(p * 720) % 360)
    elif c.t >= T_LAND:
        age = c.t - T_LAND
        bounce = int(round(abs(math.sin(age * 14)) * 3 * max(0.0, 1 - age / 0.35)))
        paste(c.world, cushion(), CUSHION[0], CUSHION[1] + 1 - bounce, "mb")
        dust(c.world, CUSHION[0], CUSHION[1], age)
        if c.t >= t_word - 0.4:
            dy = pop_dy(c.t - t_word + 0.4, drop=4) or 0
            ImageDraw.Draw(c.world).line([(CUSHION[0] + 9, CUSHION[1] - 5), (CUSHION[0] + 18, 101 + dy)], fill=INK)
            label(c.world, (CUSHION[0] + 22, 101 + dy), "KNEEL HERE", bg=C["paper"], anchor="mb")
    yield "ui"
    if t_kneel <= c.t < T_THROW + 0.2:
        ux, uy = c.to_ui(GX - 36, 104)
        big_text(c.ui, (ux, uy + (pop_dy(c.t - t_kneel) or 0)), "KNEEL.", PRESS16, anchor="mb")


@gag("v1", 1)
def first_of_nothing(c, L):
    """A kraft-paper crown drops on Washington under a sign, GEORGE I ... OF NOTHING; on 'I'm George
    the Third' the King gets a gilded GEORGE III; on the hit, the paper crown flops off."""
    t_first, t_noth, t_third = wt(L, "First"), wt(L, "Nothing"), wt(L, "George", 1)
    t_hit = TL.hit_of(L.ln)["t"]
    t_cut = t_third - 0.15
    c.take_shot(L, "boston" if c.t < t_cut else "london")
    reaction_shot(c, L)
    w, g = c.st["washington"], c.st["george"]
    if c.t >= t_first:
        w.update(brows="up", mouth="frown")
    if c.t >= t_cut:
        g.update(arm="fist" if c.t < t_hit else g["arm"], eyes="open", brows="up")
    yield "front"
    wx, wy = anchor(c, "washington", "top")
    if c.t >= t_first:
        age = c.t - t_first
        if c.t < t_hit + 0.05:
            y = wy + 4 - int(24 * (1 - ease_out(min(1.0, age / 0.3))))
            paste(c.world, paper_crown(), wx, y, "mb")
        else:
            age2 = c.t - t_hit
            x, y = projectile(min(1.0, age2 / 0.6), (wx, wy - 2), (wx - 16, FY - 4), 10)
            paste_rot(c.world, paper_crown(), x, y, int(-age2 * 500) if age2 < 0.6 else 150)
        text_ = "GEORGE I" + (" OF NOTHING" if c.t >= t_noth else "")
        label(c.world, (WX + 1, 52 + (pop_dy(age, drop=4) or 0)), text_, bg=KRAFT, fg=INK, anchor="mt")
    if c.t >= t_third - 0.1:
        age = c.t - t_third + 0.1
        gx, gy = GX - 2, 51
        big_text(c.world, (gx, gy + (pop_dy(age, drop=6) or 0)), "GEORGE III", PRESS, anchor="ma")
        for k, (ox, oy) in enumerate(((-46, 2), (44, 0), (-38, 12), (40, 13))):
            if (c.f // 3 + k) % 3:
                sparkle(c.world, gx + ox, gy + oy, 1 + (c.f + k) % 2, C["gold_hi"])


@gag("v1", 2)
def married_it(c, L):
    """A sack of money thumps onto the wharf on 'fortune'; on 'married it' it sprouts a wedding bow,
    hearts float up and a JUST MARRIED 1759 ribbon unfurls over Washington."""
    t_fort, t_marr = wt(L, "fortune"), wt(L, "married")
    c.take_shot(L, "boston")
    w = c.st["washington"]
    w.update(brows="angry", mouth="closed")
    if c.t >= t_marr:
        w.update(eyes="side", mouth="frown")
    yield "front"
    draw_bag(c, t_fort, bow=c.t >= t_marr)
    if c.t >= t_marr:
        age = c.t - t_marr
        for k in range(5):
            ph = (age * 0.8 + k * 0.23) % 1.0
            heart(c.world, 30 + k * 11 + math.sin(ph * 6 + k) * 2, 104 - ph * 40)
        ribbon(c.world, WX + 4, 52, "JUST MARRIED - 1759", age)


def draw_bag(c, t_drop, bow=False, x=36):
    if c.t < t_drop:
        return
    age = c.t - t_drop
    y = FY + 1 - int(60 * (1 - ease_in(min(1.0, age / 0.25)))) if age < 0.25 else FY + 1
    squash = age >= 0.25 and age < 0.35
    im = money_bag(bow)
    if squash:
        im = im.resize((im.width + 2, im.height - 2), Image.NEAREST)
    paste(c.world, im, x, y, "mb")
    dust(c.world, x, FY, age - 0.25)


def ribbon(img, x, y, s, age):
    if age < 0:
        return
    w = int((text_width(s, SILK) + 10) * ease_out(age / 0.4))
    if w < 6:
        return
    d = ImageDraw.Draw(img)
    x0, x1 = int(x - w // 2), int(x + w // 2)
    d.rectangle((x0 - 1, y - 1, x1 + 1, y + 8), fill=INK)
    d.rectangle((x0, y, x1, y + 7), fill=C["white"])
    d.polygon([(x0 - 5, y + 2), (x0, y + 2), (x0, y + 9), (x0 - 5, y + 9), (x0 - 3, y + 5)], fill=C["white_sh"],
              outline=INK)
    d.polygon([(x1 + 5, y + 2), (x1, y + 2), (x1, y + 9), (x1 + 5, y + 9), (x1 + 3, y + 5)], fill=C["white_sh"],
              outline=INK)
    if age > 0.3:
        d.fontmode = "1"
        d.text((int(x), y - 2), s, font=SILK, fill=(200, 60, 90), anchor="ma")


@gag("v1", 3)
def carry_it(c, L):
    """Parcels of Virginia land stack onto the money bag on 'acres'; a measuring rod pops up to
    6 FT 2 IN on 'tall'; on 'carry it' Washington hoists the whole teetering pile overhead."""
    t_acres, t_tall, t_carry = wt(L, "acres"), wt(L, "tall"), wt(L, "carry")
    carrying = c.t >= t_carry - 0.1
    c.take_shot(L, "boston" if not carrying else (80, 68, 12))
    w = c.st["washington"]
    if carrying:
        w.update(arm="fist", brows="worried", mouth="grit", mic=False)
        c.hit_react["washington"] = False
    yield "front"
    stack_x = 36
    if not carrying:
        draw_bag(c, -1, bow=True, x=stack_x)
        for k in range(3):
            tk = t_acres + k * 0.18
            if c.t >= tk:
                age = c.t - tk
                y = FY - 14 - k * 7 - int(40 * (1 - ease_in(min(1.0, age / 0.2))))
                paste(c.world, parcel(tree=k == 2), stack_x, y, "mb")
        if t_acres <= c.t < t_tall:
            label(c.world, (46, 55 + (pop_dy(c.t - t_acres, drop=4) or 0)), "MARTHA'S ACRES", bg=GRASS_HI,
                  anchor="mt")
    else:
        age = c.t - t_carry + 0.1
        lift = ease_out(min(1.0, age / 0.3))
        sway = math.sin(c.t * 7) * 3 * lift
        bx = lerp(stack_x, WX + 8, lift) + sway
        by = lerp(FY + 1, 70, lift)
        paste_rot(c.world, money_bag(True), bx, by - 8, int(sway * 2))
        for k in range(3):
            paste_rot(c.world, parcel(tree=k == 2), bx + sway * (k + 1) * 0.4, by - 21 - k * 7,
                      int(sway * (k + 2)))
    if c.t >= t_tall:
        age = c.t - t_tall
        rod_x = WX - 15
        top = FY - int((FY - 66) * ease_out(min(1.0, age / 0.35)))
        d = ImageDraw.Draw(c.world)
        d.rectangle((rod_x - 1, top, rod_x + 1, FY), fill=INK)
        d.line([(rod_x, top + 1), (rod_x, FY - 1)], fill=C["paper"])
        for y in range(FY - 4, top, -4):
            d.line([(rod_x + 1, y), (rod_x + 3, y)], fill=INK)
        if age > 0.35:
            label(c.world, (rod_x - 3, top + 1), "6 FT 2 IN", bg=C["paper"], anchor="rm")


@gag("v1", 4)
def volley_in_the_woods(c, L):
    """'Twenty-two' tags Washington AGE 22; pines spring up behind him and one volley goes off in
    them (JUMONVILLE GLEN, 1754); on 'lit' the camera pulls out as the spark runs east along the
    horizon, setting fires all the way to London: THE SEVEN YEARS' WAR."""
    t_22, t_volley, t_woods, t_lit, t_empire = (wt(L, "Twenty"), wt(L, "volley"), wt(L, "woods"), wt(L, "lit"),
                                                wt(L, "empire"))
    c.take_shot(L, "boston")
    if c.t >= t_lit - 0.15:
        pan(c, "boston", "wide", t_lit - 0.15, 0.5)
    w = c.st["washington"]
    if c.t >= t_volley + 0.1:
        w.update(eyes="side" if c.t < t_lit else "wide", brows="worried" if c.t >= t_lit else "neutral",
                 mouth="o" if c.t < t_woods else "frown")
    trees = [(12, FY + 1), (25, FY - 1), (38, FY + 1), (51, FY)]
    t_bang = t_volley + 0.1
    yield "back"
    for i, (x, y) in enumerate(trees):
        age = c.t - (t_volley - 0.4 + i * 0.07)
        if age >= 0:
            im = pine()
            h = max(1, int(im.height * back_out(min(1.0, age / 0.2))))
            paste(c.world, im.resize((im.width, h), Image.NEAREST), x, y, "mb")
    for i, (x, y, h) in enumerate(FIRES):
        t_fire = lerp(t_lit + 0.25, t_empire + 0.1, i / (len(FIRES) - 1))
        if c.t >= t_fire:
            blaze(c.world, x, y, c.t - t_fire, seed=i, h=h)
    yield "front"
    if c.t >= t_22:
        label(c.world, (WX + 13, 74 + (pop_dy(c.t - t_22, drop=4) or 0)), "AGE 22", bg=C["paper"], anchor="lm")
    if t_bang <= c.t < t_bang + 1.5:
        age = c.t - t_bang
        for i, (x, y) in enumerate(trees[:3]):
            muzzle_flash(c.world, x + 5, y - 9, age - i * 0.02, facing=1, size=1.0)
            puff(c.world, x + 8, y - 15, age, size=0.35, seed=i, drift=(6, -14))
    if t_bang + 0.25 <= c.t < t_empire:
        label(c.world, (62, 53 + (pop_dy(c.t - t_bang - 0.25, drop=4) or 0)), "JUMONVILLE GLEN, 1754",
              bg=C["paper"], anchor="mt")
    if t_lit <= c.t < t_empire + 0.3:
        x, y = along(SPARK_PATH, ramp(c.t, t_lit, t_empire + 0.1))
        d = ImageDraw.Draw(c.world)
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=C["gold_hi"], outline=FLAME)
        for k in range(5):
            d.point((int(x - 3 - k * 2), int(y + (k % 2) - 1)), fill=FLAME if k < 3 else FLAME_DK)
    yield "ui"
    if c.t >= t_empire:
        age = c.t - t_empire
        big_text(c.ui, (W // 2, 20 + (pop_dy(age, drop=10) or 0)), "THE SEVEN", PRESS16,
                 top=FLAME_HI, bottom=FLAME_DK, anchor="ma")
        big_text(c.ui, (W // 2, 38 + (pop_dy(age - 0.08, drop=10) or 0)), "YEARS' WAR", PRESS16,
                 top=FLAME_HI, bottom=FLAME_DK, anchor="ma")


# the fuse from the woods to the ends of the empire, and the fires it lights (x, base y, height)
SPARK_PATH = [(56, 104), (100, 112), (108, HORIZON), (212, HORIZON), (226, 112), (300, 112)]
FIRES = [(88, 113, 9), (120, HORIZON, 6), (148, HORIZON, 7), (176, HORIZON, 6), (204, HORIZON, 7),
         (228, 113, 10), (282, 113, 12), (306, 113, 11)]


def blaze(img, x, y, age, seed=0, h=8):
    """A flickering fire with a smoke wisp, growing to height h over a fifth of a second."""
    if age < 0:
        return
    d = ImageDraw.Draw(img)
    hh = h * min(1.0, age / 0.2)
    if hh < 1:
        return
    fr = int(age * 12)
    wob = (rnd("bz", seed, fr) - 0.5) * 3
    half = max(2, h * 0.35)
    tips = [(x - half, y), (x - half * 0.5 + wob * 0.5, y - hh * 0.6), (x + wob, y - hh),
            (x + half * 0.4 + wob * 0.3, y - hh * 0.55), (x + half, y)]
    d.polygon(tips, fill=FLAME_DK, outline=INK)
    d.polygon([(x - half * 0.6, y), (x + wob * 0.8, y - hh * 0.75), (x + half * 0.6, y)], fill=FLAME)
    d.polygon([(x - half * 0.3, y), (x + wob * 0.5, y - hh * 0.4), (x + half * 0.3, y)], fill=FLAME_HI)
    for k in range(3):
        sy = y - hh - 2 - ((age * 10 + k * 3.5) % 10)
        d.point((int(x + wob + (k - 1) + math.sin(age * 4 + k) * 1.5), int(sy)), fill=(110, 96, 112))


def along(pts, p):
    """Point at fraction p (by length) along a polyline."""
    lens = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    left = sum(lens) * clamp(p, 0.0, 1.0)
    for (a, b), n in zip(zip(pts, pts[1:]), lens):
        if left <= n:
            u = left / n if n else 1.0
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        left -= n
    return pts[-1]


def flicker(img, x, y, age, seed=0, big=False):
    """A small fire burning on the horizon (or on the shore)."""
    d = ImageDraw.Draw(img)
    h = int((6 if big else 4) * min(1.0, age / 0.2))
    if h <= 0:
        return
    wob = int(rnd("fl", seed, int(age * 10)) * 3) - 1
    d.polygon([(x - 3, y), (x + 3, y), (x + wob, y - h)], fill=FLAME)
    d.polygon([(x - 1, y), (x + 1, y), (x + wob, y - h + 2)], fill=FLAME_HI)
    if big:
        for k in range(3):
            sy = y - h - 2 - ((age * 12 + k * 4) % 10)
            d.point((x + wob + (k - 1), int(sy)), fill=(120, 100, 110))


@gag("v1", 5)
def father_of_a_fire(c, L):
    """A gilded portrait frame drops around Washington: FATHER OF HIS COUNTRY. George rolls his eyes on
    'Please'; on 'fire' the frame bursts into flames, the plaque burns to FATHER OF A FIRE and a
    swaddled baby fire lands in Washington's arms."""
    t_father, t_please, t_fire = wt(L, "Father"), wt(L, "Please"), wt(L, "fire")
    shot = "boston"
    if t_please - 0.1 <= c.t < t_please + 0.45:
        shot = "london"
    c.take_shot(L, shot)
    g, w = c.st["george"], c.st["washington"]
    if t_please - 0.1 <= c.t < t_please + 0.6:
        g.update(eyes="shut", brows="up", mouth="smirk")
    c.hit_react["washington"] = False
    if c.t >= t_father:
        w.update(brows="up", mouth="smirk", arm="hip")
    if c.t >= t_fire:
        w.update(arm="hold", eyes="wide", brows="worried", mouth="o", sweat=True)
    yield "front"
    if c.t < t_father:
        return
    age = c.t - t_father
    x0, y0, x1, y1 = WX - 20, 62, WX + 22, FY + 2
    drop = int(-70 * (1 - ease_out(min(1.0, age / 0.3))))
    d = ImageDraw.Draw(c.world)
    for inset, col in ((0, INK), (1, C["gold_sh"]), (2, C["gold"]), (3, C["gold_hi"]), (4, C["gold_sh"]), (5, INK)):
        d.rectangle((x0 + inset, y0 + inset + drop, x1 - inset, y1 - inset + drop), outline=col)
    on_fire = c.t >= t_fire
    if on_fire:
        fa = c.t - t_fire
        spots = [(lerp(x0, x1, u / 5), y0 + 1) for u in range(6)] + [(x, y) for y in (80, 98) for x in (x0, x1)]
        for i, (fx, fy) in enumerate(spots):
            blaze(c.world, int(fx), int(fy), fa - i * 0.015, seed=i + 30, h=7 + (i % 3) * 2)
        paste(c.world, baby_flame(int(c.t * 6) % 2), WX + 13, 101, "mb")
    plaque = "FATHER OF A FIRE" if on_fire else "FATHER OF HIS COUNTRY"
    label(c.world, ((x0 + x1) // 2, y0 + drop - 2), plaque, bg=FLAME if on_fire else C["gold"], fg=INK, anchor="mb")


def storm_state(t):
    """Where the Fort Necessity storm cloud is: it crosses from London, pours on Washington through
    lines 6-7, then blows back east at the start of line 8."""
    a = line_t("v1", 6) - 0.2
    arrive = line_t("v1", 6, "poured")
    leave = line_t("v1", 8)
    if t < a or t > leave + 1.0:
        return None
    cx, cy = WX + 6, 52
    if t < arrive:
        p = ease_in_out(ramp(t, a, arrive))
        return lerp(262, cx, p), lerp(34, cy, p), 0.0
    if t < leave:
        return cx, cy + math.sin(t * 2) * 0.8, 1.0
    p = ease_in(ramp(t, leave, leave + 1.0))
    return lerp(cx, 262, p), lerp(cy, 34, p), 1.0 - p


@span(line_t("v1", 6) - 0.2, line_t("v1", 8) + 1.0)
def storm(c, L):
    """The cloud and its downpour, and the Fort Necessity stockade around Washington (lines 6-7)."""
    st = storm_state(c.t)
    t_fort, t_end = line_t("v1", 6, "Fort"), line_t("v1", 8)
    fort = t_fort <= c.t < t_end + 0.4
    yield "back"
    if fort:
        stockade(c.world, c.t - t_fort, c.t - t_end, back=True)
    yield "front"
    if st:
        x, y, pour = st
        paste(c.world, cloud(), x, y, "mm")
        if pour > 0:
            rain_under(c.world, x - 20, x + 20, y + 6, FY, c.t, density=pour, seed=1)
    if fort:
        stockade(c.world, c.t - t_fort, c.t - t_end, back=False)
        fort_sign(c.world, c.t - t_fort, c.t - t_end)


def fort_sign(img, age, out_age):
    """A plank sign on a post at the left of the stockade: FORT / NECESSITY."""
    if out_age > 0.2:
        return
    if age < 0.1:
        return
    x, y = 30, 57 + (pop_dy(age - 0.1, drop=10) or 0)
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y + 16, x + 1, FY), fill=C["wood_sh"], outline=INK)
    d.rectangle((x - 27, y - 1, x + 27, y + 17), fill=INK)
    d.rectangle((x - 26, y, x + 26, y + 16), fill=C["wood_hi"])
    d.line([(x - 26, y + 8), (x + 26, y + 8)], fill=C["wood"])
    d.fontmode = "1"
    d.text((x, y - 1), "FORT", font=SILK, fill=INK, anchor="ma")
    d.text((x, y + 7), "NECESSITY", font=SILK, fill=INK, anchor="ma")


def stockade(img, age, out_age, back):
    """Fort Necessity: a ring of sharpened stakes rising around Washington, sinking away after."""
    rise = ease_out(min(1.0, age / 0.3)) * (1 - ease_in(clamp(out_age / 0.4, 0, 1)) if out_age > 0 else 1)
    d = ImageDraw.Draw(img)
    xs = range(WX - 24, WX + 26, 4)
    for i, x in enumerate(xs):
        h = (14 if back else 7) + (i % 2)
        top = FY + 1 - int(h * rise) - (0 if back else -2)
        base = FY - 2 if back else FY + 3
        if top >= base:
            continue
        col = C["wood"] if back else C["wood_hi"]
        d.rectangle((x - 1, top, x + 1, base), fill=col, outline=INK)
        d.point((x, top - 1), fill=INK)


@gag("v1", 6)
def fort_necessity(c, L):
    """London's rain cloud crosses the Atlantic and pours on Washington; a stockade springs up around him
    (the storm span draws them); his powder keg fills with rain on 'powder soaking wet'."""
    t_powder, t_wet = wt(L, "powder"), wt(L, "wet")
    c.shot = "wide" if c.t < wt(L, "poured") else "boston"
    c.take_shot(L, c.shot)
    w = c.st["washington"]
    if c.t >= wt(L, "poured"):
        w.update(brows="worried", mouth="frown", eyes="blink" if int(c.t * 3) % 3 == 0 else "open")
    yield "front"
    if c.t >= t_powder - 0.2:
        age = c.t - t_powder + 0.2
        kx = WX - 24
        paste(c.world, keg(wet=c.t >= t_wet), kx, FY + 1 - int(30 * (1 - ease_out(min(1.0, age / 0.2)))), "mb")
        wet = c.t >= t_wet
        label(c.world, (kx, 97 + (pop_dy(age, drop=4) or 0)), "SOAKED" if wet else "POWDER",
              bg=LIGHT_BLUE if wet else C["paper"], anchor="mb")
        if wet:
            d = ImageDraw.Draw(c.world)
            for k in range(3):
                yy = FY - 12 + ((c.t - t_wet) * 30 + k * 5) % 12
                d.point((kx - 5 + k * 5, int(yy)), fill=LIGHT_BLUE)


@gag("v1", 7)
def reign(c, L):
    """Still pouring: on 'reign' the rain splashing off Washington's hat forms a little crown of water,
    and a sign pops up: LONG MAY IT RAIN."""
    t_reign = wt(L, "reign")
    c.take_shot(L, "boston")
    reaction_shot(c, L)
    w = c.st["washington"]
    w.update(brows="worried", mouth="frown", eyes="blink" if int(c.t * 3) % 3 == 0 else "open")
    yield "front"
    if c.t >= t_reign:
        age = c.t - t_reign
        hx, hy = anchor(c, "washington", "top")
        hy += 2
        d = ImageDraw.Draw(c.world)
        grow_ = ease_out(min(1.0, age / 0.2))
        for k in range(5):
            x = hx - 8 + k * 4
            h = int((4 + (k % 2) * 3) * grow_) + (c.f // 2 + k) % 2
            d.line([(x - 1, hy), (x - 1, hy - h)], fill=INK)
            d.line([(x + 1, hy), (x + 1, hy - h)], fill=INK)
            d.line([(x, hy), (x, hy - h)], fill=LIGHT_BLUE)
            d.rectangle((x - 1, hy - h - 3, x + 1, hy - h - 1), fill=INK)
            d.point((x, hy - h - 2), fill=C["white"])
        d.rectangle((hx - 10, hy - 1, hx + 10, hy + 1), fill=INK)
        d.line([(hx - 9, hy), (hx + 9, hy)], fill=LIGHT_BLUE)
        if age > 0.2:
            dy = pop_dy(age - 0.2, drop=4) or 0
            label(c.world, (132, 52 + dy), "LONG MAY", bg=LIGHT_BLUE, anchor="mt")
            label(c.world, (132, 63 + dy), "IT RAIN", bg=LIGHT_BLUE, anchor="mt")


@gag("v1", 8)
def fourth_of_july(c, L):
    """The storm blows back home; a tiny column of soaked soldiers marches out of the fort as a calendar
    page drops, JULY 4, 1754; on 'Look it up, boy' George holds up a book: HISTORY."""
    t_march, t_fourth, t_look = wt(L, "marched"), wt(L, "Fourth"), wt(L, "Look")
    c.take_shot(L, "boston" if c.t < t_look - 0.15 else "london")
    g = c.st["george"]
    if t_march <= c.t < t_look:
        c.st["washington"].update(arm="wave", brows="worried", mouth="closed")
    if c.t >= t_look - 0.15:
        g.update(arm="hold", mic=True, brows="up", eyes="open", mouth=g["mouth"])
    yield "front"
    if c.t >= t_march:
        age = c.t - t_march
        for k in range(4):
            x = WX - 22 - age * 16 + k * 7
            if x < -6:
                continue
            soldier(c.world, int(x), FY + 1, int(age * 6 + k) % 2)
    if c.t >= t_fourth:
        age = c.t - t_fourth
        cx, cy = 118, 56 + (pop_dy(age, drop=12) or 0)
        parchment(c.world, (cx - 16, cy, cx + 16, cy + 24), rolled=False)
        d = ImageDraw.Draw(c.world)
        d.rectangle((cx - 16, cy, cx + 16, cy + 5), fill=C["flag_red"])
        d.fontmode = "1"
        d.text((cx, cy + 5), "JULY 4", font=SILK, fill=INK, anchor="ma")
        d.text((cx, cy + 13), "1754", font=SILK, fill=INK, anchor="ma")
    if c.t >= t_look - 0.15:
        hx, hy = GX - 19, 92
        paste(c.world, book(), hx, hy, "mm")
        label(c.world, (hx - 12, hy + (pop_dy(c.t - t_look, drop=4) or 0)), "HISTORY", bg=C["paper"], anchor="rm")


def soldier(img, x, y, step):
    """A 7px-tall Virginia militiaman marching left, musket on his shoulder."""
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y - 7, x + 1, y - 3), fill=C["navy"], outline=None)
    d.point((x, y - 8), fill=C["skin"])
    d.line([(x - 1, y - 9), (x + 1, y - 9)], fill=C["hat"])
    d.point((x - 1 + step, y - 2), fill=C["buff"]); d.point((x + 1 - step, y - 2), fill=C["buff"])
    d.point((x - 1 + step, y - 1), fill=C["boot"]); d.point((x + 1 - step, y - 1), fill=C["boot"])
    d.line([(x + 2, y - 5), (x + 2, y - 11)], fill=C["iron"])
    for yy in range(y - 4, y - 1):
        d.point((x + 3, yy), fill=LIGHT_BLUE if (yy + step) % 3 == 0 else C["navy_sh"])


@gag("v1", 9)
def white_flag(c, L):
    """Rockets go up over Boston for 'Independence Day': red, white, blue... and the last one bursts
    as a white flag, while a white flag pops into Washington's hand. George raises a teacup: 'Enjoy.'
    After the hit Washington flings the flag into the sea."""
    t_indep, t_white, t_enjoy = wt(L, "Independence"), wt(L, "white"), wt(L, "Enjoy")
    t_flag = wt(L, "flag")
    t_throw, t_splash = t_flag + 0.05, t_flag + 0.5
    c.take_shot(L, "boston" if c.t < t_enjoy - 0.1 else "london")
    w, g = c.st["washington"], c.st["george"]
    c.hit_react["washington"] = False
    if t_indep - 0.3 <= c.t < t_white:
        w.update(eyes="open", brows="up", mouth="o")
    if t_white <= c.t < t_throw:
        w.update(arm="wave", eyes="side", brows="worried", mouth="frown")
    elif t_throw <= c.t < t_throw + 0.35:
        w.update(arm="point", brows="angry", mouth="grit")
    if c.t >= t_enjoy - 0.1:
        g.update(arm="hold", eyes="shut", brows="up", mouth="smirk", mic=True)
    yield "back"
    bursts = [(t_indep - 0.3, 30, 58, C["flag_red"]), (t_indep, 124, 52, C["white"]),
              (t_indep + 0.3, 146, 64, (110, 150, 255))]
    for i, (ts, x, y, col) in enumerate(bursts):
        age = c.t - ts
        rocket(c.world, x, 104, y, age / 0.4)
        firework(c.world, x, y, age - 0.4, col, seed=i, r=18)
    fx, fy = 108, 58
    tw = t_white - 0.35
    rocket(c.world, fx, 104, fy, (c.t - tw) / 0.35)
    if tw + 0.35 <= c.t < t_enjoy:
        age = c.t - tw - 0.35
        s_ = ease_out(min(1.0, age / 0.2))
        if s_ > 0.1:
            fl = waving(flag_cloth("white"), c.t, amp=1.0)
            im = fl.resize((max(1, int(fl.width * s_ * 1.5)), max(1, int(fl.height * s_ * 1.5))), Image.NEAREST)
            paste(c.world, im, fx, fy, "mm")
        d = ImageDraw.Draw(c.world)
        for k in range(10):
            a = k * math.pi / 5
            r = 12 + age * 12
            if (k + int(age * 10)) % 3:
                d.point((int(fx + math.cos(a) * r), int(fy + math.sin(a) * r * 0.7 + 8 * age * age)), fill=C["white"])
    yield "front"
    if t_white <= c.t < t_throw:
        hx, hy = anchor(c, "washington", "hand")
        d = ImageDraw.Draw(c.world)
        d.rectangle((hx - 1, hy - 17, hx + 1, hy + 3), fill=INK)
        d.line([(hx, hy - 16), (hx, hy + 2)], fill=C["wood_hi"])
        fl = waving(flag_cloth("white"), c.t, amp=1.0)
        paste(c.world, outline_(fl), hx + 1, hy - 17, "lt")
    elif t_throw <= c.t < t_splash:
        fly(c.world, white_flag_float(), (WX + 12, 64), (118, 124), (c.t - t_throw) / (t_splash - t_throw),
            lift=26, spin=1.5)
    elif c.t >= t_splash:
        splash(c.world, 118, 126, c.t - t_splash, size=1.0, seed=9)
    if c.t >= t_enjoy - 0.1:
        paste(c.world, teacup(), GX - 16, 94, "mm")
        d = ImageDraw.Draw(c.world)
        for k in range(2):
            yy = 86 - ((c.t * 8 + k * 3) % 6)
            d.point((GX - 18 + k * 3, int(yy)), fill=(230, 230, 240))
        if (c.f // 2) % 3 == 0:
            sparkle(c.world, GX - 22, 89, 2, C["white"])


def outline_(img):
    a = Image.new("RGBA", (img.width + 2, img.height + 2), (0, 0, 0, 0))
    a.paste(img, (1, 1), img)
    return outlined(a, INK)


@gag("v1", 10)
def stamp_act(c, L):
    """'I paid for the war': George unrolls a long bill, WAR DEBT; 'sent a Stamp' fires a Stamp Act
    revenue stamp across the sea, where it slaps onto Washington's chest; on 'poison' a skull and
    crossbones takes over the stamp."""
    t_paid, t_stamp, t_poison = wt(L, "paid"), wt(L, "Stamp"), wt(L, "poison")
    shot = "london" if c.t < t_stamp - 0.25 else "wide"
    if c.t >= t_stamp + 0.45:
        shot = "boston"
    c.take_shot(L, shot)
    g, w = c.st["george"], c.st["washington"]
    if t_paid <= c.t < t_stamp:
        g.update(arm="hold", brows="up")
    elif t_stamp - 0.25 <= c.t < t_stamp + 0.3:
        g.update(arm="wave", brows="angry")
    flight = (t_stamp - 0.2, t_stamp + 0.45)
    if c.t >= flight[1]:
        w.update(brows="angry", mouth="grit", eyes="wide" if c.t < flight[1] + 0.3 else "open")
    yield "front"
    if t_paid <= c.t < t_stamp + 0.3:
        age = c.t - t_paid
        hx, hy = GX - 18, 92
        n = int(min(1.0, age / 0.6) * 18)
        d = ImageDraw.Draw(c.world)
        d.rectangle((hx - 7, hy, hx + 7, hy + 4 + n), fill=C["paper"], outline=INK)
        for yy in range(hy + 3, hy + 3 + n, 3):
            d.line([(hx - 5, yy), (hx + 3, yy)], fill=C["paper_sh"])
        label(c.world, (hx - 10, hy + 2), "WAR DEBT", bg=C["paper"], fg=C["flag_red"], anchor="rm")
    if flight[0] <= c.t < flight[1]:
        p = (c.t - flight[0]) / (flight[1] - flight[0])
        fly(c.world, revenue_stamp(), (GX - 14, 88), (WX + 4, 92), p, lift=30, spin=2.0)
    elif c.t >= flight[1]:
        age = c.t - flight[1]
        paste(c.world, revenue_stamp(poison=c.t >= t_poison), WX + 4, 93 + wobble(age, 2), "mm")
        label(c.world, (WX + 4, 53), "STAMP ACT, 1765", bg=C["paper"], anchor="mt")
        if c.t >= t_poison:
            label(c.world, (WX + 4, 64 + (pop_dy(c.t - t_poison, drop=4) or 0)), "POISON", bg=INK,
                  fg=(150, 230, 120), anchor="mt")


def invoice_times():
    t_col = line_t("v1", 11, "colonial")
    t_fire = t_col + 0.65
    t_smack = t_fire + 0.55
    t_toss = TL.line("v1", 12)["t0"] - 0.12 - 0.45
    return t_col, t_fire, t_smack, t_toss, t_toss + 0.4


T_COL, T_FIRE, T_SMACK, T_TOSS, T_INV_SPLASH = invoice_times()
INVOICE_AT = (140, 134)


@gag("v1", 11)
def invoice(c, L):
    """Washington waves a TYRANNY! placard; George wheels out a cannon and fires a rolled bill across
    the Atlantic. It smacks into Washington's hands and unrolls: INVOICE, FOR: 1 WAR, PAYABLE BY: THE
    COLONIES; 'invoice' stamps it DUE. He balls it up and throws it in the sea, where it floats."""
    t_tyr, t_inv = wt(L, "tyranny"), wt(L, "invoice")
    gun_x = GX - 24
    shot = "boston"
    if T_COL - 0.1 <= c.t < T_FIRE - 0.05:
        shot = "london"
    elif T_FIRE - 0.05 <= c.t < T_SMACK:
        shot = "wide"
    c.take_shot(L, shot)
    w, g = c.st["washington"], c.st["george"]
    if t_tyr <= c.t < T_SMACK:
        w.update(arm="hold", mouth="wide" if c.t < T_COL else "closed", brows="angry")
    elif T_SMACK <= c.t < T_TOSS:
        w.update(arm="hold", eyes="wide" if c.t < t_inv else "open", brows="worried", mouth="o")
    elif c.t >= T_TOSS:
        w.update(arm="point", brows="angry", mouth="grit")
    if T_COL <= c.t < T_FIRE + 0.4:
        g.update(arm="point", brows="up", eyes="open")
    yield "back"
    if c.t >= T_COL:
        roll = ease_out(min(1.0, (c.t - T_COL) / 0.4))
        recoil = int(4 * max(0.0, 1 - (c.t - T_FIRE) / 0.3)) if c.t >= T_FIRE else 0
        paste(c.world, cannon(), gun_x + int((1 - roll) * 30) + recoil, FY + 1, "mb")
    yield "front"
    if t_tyr <= c.t < T_SMACK:
        paste(c.world, placard(), WX + 14, 88 + (pop_dy(c.t - t_tyr, drop=6) or 0), "mb")
    if c.t >= T_FIRE:
        age = c.t - T_FIRE
        muzzle_flash(c.world, gun_x - 12, FY - 5, age, facing=-1, size=1.4)
        puff(c.world, gun_x - 12, FY - 6, age, size=0.8, seed=3, drift=(8, -6))
        fly(c.world, invoice_roll(), (gun_x - 12, FY - 6), (WX + 14, 88), age / (T_SMACK - T_FIRE), lift=34,
            spin=2.0)
    if T_SMACK <= c.t < T_TOSS:
        age = c.t - T_SMACK
        im = invoice_sheet()
        h = max(1, int(im.height * ease_out(min(1.0, age / 0.15))))
        paste(c.world, im.resize((im.width, h), Image.NEAREST), WX + 9, 52, "lt")
        stamp(c.world, WX + 52, 103, "DUE", size=8, age=c.t - t_inv, angle=-10)
    elif T_TOSS <= c.t < T_INV_SPLASH:
        fly(c.world, invoice_float(), (WX + 14, 84), (INVOICE_AT[0], INVOICE_AT[1] - 2),
            (c.t - T_TOSS) / (T_INV_SPLASH - T_TOSS), lift=18, spin=1.0)
    elif c.t >= T_INV_SPLASH:
        splash(c.world, *INVOICE_AT, c.t - T_INV_SPLASH, size=0.8, seed=11)


@gag("v1", 12)
def redcoat(c, L):
    """A daydream bubble over Washington: himself in a British red coat, saluting, hearts all round.
    On 'Wrote letters' envelopes start flying from his hand across the sea to George's feet."""
    t_begged, t_wrote, t_pined = wt(L, "begged"), wt(L, "Wrote"), wt(L, "pined")
    c.take_shot(L, "boston" if c.t < t_wrote - 0.1 else "wide")
    w, g = c.st["washington"], c.st["george"]
    if t_begged <= c.t < t_wrote:
        w.update(eyes="shut", mouth="smile", brows="up", arm="cross")
    if c.t >= t_wrote:
        w.update(arm="wave" if int((c.t - t_wrote) * 4) % 2 == 0 else "point", mouth="closed", brows="worried")
        g.update(eyes="shut", brows="up")
    yield "front"
    if t_begged <= c.t < t_wrote + 0.2:
        age = c.t - t_begged
        s = back_out(min(1.0, age / 0.2))
        bx, by = 124, 68
        if s > 0.2:
            d = ImageDraw.Draw(c.world)
            rx, ry = 22 * s, 22 * s
            d.ellipse((bx - rx - 1, by - ry - 1, bx + rx + 1, by + ry + 1), fill=INK)
            d.ellipse((bx - rx, by - ry, bx + rx, by + ry), fill=(236, 230, 246))
            for k, r in enumerate((2, 3)):
                px, py = 88 + k * 7, 74 - k * 4
                d.ellipse((px - r - 1, py - r - 1, px + r + 1, py + r + 1), fill=INK)
                d.ellipse((px - r, py - r, px + r, py + r), fill=(236, 230, 246))
            if s > 0.9:
                spr = redcoat_sprite()
                small = spr.resize((spr.width * 3 // 4, spr.height * 3 // 4), Image.NEAREST)
                paste(c.world, small, bx - 2, by + 19, "mb")
                for k in range(3):
                    ph = (age * 0.9 + k / 3) % 1.0
                    heart(c.world, bx - 14 + k * 12, by - 6 - ph * 10)
    if c.t >= t_wrote:
        draw_letters(c, t_wrote, t_pined + 0.3)
    splash(c.world, *INVOICE_AT, c.t - T_INV_SPLASH, size=0.8, seed=11)


LETTERS_AT = (GX - 17, FY + 1)          # the pile on the London quay, at George's feet


def letter_times(t0, t1):
    n = 6
    return [lerp(t0, t1, i / (n - 1)) for i in range(n)]


def draw_letters(c, t0, t1, n_max=None, pile_only=False):
    times = letter_times(t0, t1)
    landed = 0
    for i, ts in enumerate(times):
        p = (c.t - ts) / 0.55
        if p >= 1:
            landed += 1
        elif p >= 0 and not pile_only:
            fly(c.world, envelope(10, 7), (WX + 14, 84), (LETTERS_AT[0] - 4 + i * 2, LETTERS_AT[1] - 6), p,
                lift=34, spin=1.0)
    if landed:
        paste(c.world, letter_pile(landed), LETTERS_AT[0], LETTERS_AT[1], "mb")
    return landed


@gag("v1", 13)
def left_on_read(c, L):
    """The stack of letters at George's feet gets a tag, LORD LOUDOUN, 1757, then READ with two blue
    ticks while George sips his tea. 'Commission: declined': a King's commission unrolls beside
    Washington and DECLINED slams onto it. After the hit, George boots the stack into the sea."""
    t_loud, t_read, t_comm, t_decl = wt(L, "Loudoun"), wt(L, "read"), wt(L, "Commission"), wt(L, "declined")
    t_hit = TL.hit_of(L.ln)["t"]
    t_kick = t_hit + 0.25
    t_land = t_kick + 0.45
    shot = "london"
    if t_comm - 0.1 <= c.t < t_kick - 0.1:
        shot = "boston"
    elif c.t >= t_kick - 0.1:
        shot = (200, 104, 9)
    c.take_shot(L, shot)
    g, w = c.st["george"], c.st["washington"]
    if t_read - 0.1 <= c.t < t_comm:
        g.update(arm="hold", eyes="shut", brows="up", mouth="smirk")
    if t_kick - 0.1 <= c.t < t_kick + 0.3:
        g.update(lean=-2, arm="point", brows="angry", mouth="smirk")
    if t_comm <= c.t < t_decl:
        w.update(eyes="wide", brows="up", mouth="smile")
    yield "front"
    lx, ly = LETTERS_AT
    if c.t < t_kick:
        draw_letters(c, line_t("v1", 12, "Wrote"), line_t("v1", 12, "pined") + 0.3, pile_only=True)
        if c.t >= t_loud:
            label(c.world, (211, 53 + (pop_dy(c.t - t_loud, drop=4) or 0)), "LORD LOUDOUN, 1757",
                  bg=C["paper"], anchor="mt")
        if c.t >= t_read:
            dy = pop_dy(c.t - t_read, drop=4) or 0
            ImageDraw.Draw(c.world).line([(214, 74 + dy), (lx - 2, ly - 24)], fill=INK)
            box = label(c.world, (211, 65 + dy), "READ    ", bg=C["white"], fg=TICK_BLUE, anchor="mt")
            ticks(c.world, box[2] - 14, box[1] + 3)
        if t_read - 0.1 <= c.t < t_comm:
            paste(c.world, teacup(), GX - 16, 94, "mm")
    elif c.t < t_land:
        fly(c.world, letter_bundle(), (lx, FY - 6), (186, 138), (c.t - t_kick) / (t_land - t_kick), lift=20, spin=1.2)
    else:
        splash(c.world, 186, 140, c.t - t_land, size=0.9, seed=13)
    if t_comm <= c.t < t_kick:
        age = c.t - t_comm
        h = int(46 * ease_out(min(1.0, age / 0.2)))
        x0, y0 = WX + 9, 52
        if h > 6:
            commission(c.world, (x0, y0, x0 + 78, y0 + h), full=h >= 46)
        age_d = c.t - t_decl
        if age_d >= 0:
            paste(c.world, slip("DECLINED", -10), x0 + 38, y0 + 38 - int(max(0.0, 1 - age_d / 0.1) * 14), "mm")


def commission(img, box, full=True):
    """A King's commission: parchment, COMMISSION, HIS MAJESTY'S ARMY, a scribble, the royal seal."""
    x0, y0, x1, y1 = box
    parchment(img, box, rolled=True, seal=full)
    if not full:
        return
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    cx = (x0 + x1) // 2
    d.text((cx, y0 + 2), "COMMISSION", font=SILK, fill=(70, 40, 20), anchor="ma")
    d.line([(x0 + 6, y0 + 11), (x1 - 6, y0 + 11)], fill=C["paper_sh"])
    d.text((cx, y0 + 12), "HIS MAJESTY'S", font=SILK, fill=(70, 40, 20), anchor="ma")
    d.text((cx, y0 + 20), "ARMY", font=SILK, fill=(70, 40, 20), anchor="ma")


@gag("v1", 14)
def reject(c, L):
    """A sign hangs over Washington: REBEL - hero stuff - until 'reject' stamps REJECT across it.
    'with a gun': a musket drops into his arms and he looks down at it."""
    t_rebel, t_reject, t_gun = wt(L, "rebel"), wt(L, "reject"), wt(L, "gun")
    c.take_shot(L, "boston")
    w = c.st["washington"]
    if c.t >= t_rebel:
        w.update(brows="up", mouth="smirk", arm="hip")
    if c.t >= t_reject:
        w.update(brows="angry", mouth="frown")
    if c.t >= t_gun - 0.1:
        w.update(arm="hold", eyes="side", brows="worried", mouth="closed")
    yield "front"
    if c.t >= t_rebel:
        age = c.t - t_rebel
        sx, sy = 120, 56 + (pop_dy(age, drop=10) or 0)
        d = ImageDraw.Draw(c.world)
        if c.t < t_reject:
            for k in range(8):
                a = k * math.pi / 4 + age * 0.8
                r0, r1 = 26, 30 + (c.f + k) % 3
                d.line([(sx + math.cos(a) * r0, sy + 6 + math.sin(a) * r0 * 0.5),
                        (sx + math.cos(a) * r1, sy + 6 + math.sin(a) * r1 * 0.5)], fill=C["gold_hi"])
        d.rectangle((sx - 23, sy - 1, sx + 23, sy + 13), fill=INK)
        d.rectangle((sx - 22, sy, sx + 22, sy + 12), fill=C["gold"])
        d.rectangle((sx - 20, sy + 2, sx + 20, sy + 10), fill=C["navy"])
        d.fontmode = "1"
        d.text((sx + 1, sy + 3), "REBEL", font=PRESS, fill=C["white"], anchor="ma")
        if c.t >= t_reject:
            strike(c.world, sx - 22, sy + 7, sx + 22, p=(c.t - t_reject) / 0.12, width=1)
            age_r = c.t - t_reject - 0.1
            if age_r >= 0:
                paste(c.world, slip("REJECT"), sx, sy + 28 - int(max(0.0, 1 - age_r / 0.1) * 14), "mm")
    if c.t >= t_gun - 0.1:
        age = c.t - t_gun + 0.1
        y = 92 - int(30 * (1 - ease_out(min(1.0, age / 0.2))))
        paste_rot(c.world, musket(), WX + 10, y, 20)


@gag("v1", 15)
def im_done(c, L):
    """'I'm the Crown': George holds his crown up in a blaze of gold. 'the help that got ideas': a candle
    lights above Washington's head. 'Kneel.': George points at the cushion and Washington punts it into
    the sea. 'I'm done.': George drops the mic, turns his back and folds his arms."""
    t_crown, t_help, t_ideas, t_kneel = wt(L, "Crown"), wt(L, "help"), wt(L, "ideas"), wt(L, "Kneel")
    t_drop = T_DONE + 0.35
    shot = "london"
    if t_help - 0.1 <= c.t < t_kneel - 0.1:
        shot = "boston"
    elif T_KICK - 0.15 <= c.t < T_SPLASH + 0.1:
        shot = (112, 100, 12)
    c.take_shot(L, shot)
    g, w = c.st["george"], c.st["washington"]
    c.hit_react["washington"] = False
    if t_crown - 0.1 <= c.t < t_help:
        g.update(arm="fist", hat="off", brows="up", eyes="open")
    if t_help <= c.t < t_kneel:
        w.update(brows="up", eyes="open", mouth="smirk" if c.t >= t_ideas else "closed")
    if t_kneel <= c.t < T_DONE:
        g.update(arm="chop", brows="angry", mouth=g["mouth"])
    if T_KICK - 0.15 <= c.t < T_KICK + 0.3:
        w.update(lean=2, dx=3 if c.t >= T_KICK - 0.05 else 0, arm="fist", brows="angry", mouth="grit")
    elif T_KICK + 0.3 <= c.t:
        w.update(arm="cross", brows="angry", mouth="smirk")
    if c.t >= t_drop - 0.2:
        g.update(mic=False, arm="down" if c.t < t_drop + 0.4 else "cross")
    if c.t >= t_drop + 0.4:
        g.update(facing=1, eyes="shut", brows="up", mouth="smirk")
    yield "back"
    if t_crown - 0.1 <= c.t < t_help:
        age = c.t - t_crown + 0.1
        d = ImageDraw.Draw(c.world)
        cx, cy = GX - 13, 64
        for k in range(10):
            a = k * math.pi / 5 + c.t * 1.5
            r0, r1 = 8, 12 + 4 * ease_out(min(1.0, age / 0.2))
            d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)],
                   fill=C["gold_hi"] if k % 2 else C["gold"])
    yield "front"
    if t_crown - 0.1 <= c.t < t_help:
        paste(c.world, crown_sprite(), GX - 13, 68, "mb")
    if c.t >= t_ideas - 0.05 and c.t < t_kneel + 0.3:
        age = c.t - t_ideas + 0.05
        cx, cy = WX + 2, 58 + (pop_dy(age, drop=6) or 0)
        dither(c.world, glow_mask(cx, cy - 4, 12 + (c.f % 2)), C["gold_hi"], blend=0.35)
        paste(c.world, candle(c.f // 3 % 2), cx, cy + 4, "mb")
    if c.t < T_KICK:
        cushion_on_wharf(c.world, c.t)
    if T_KICK - 0.05 <= c.t < T_KICK + 0.15:                      # the kick
        d = ImageDraw.Draw(c.world)
        r = 7 + int((c.t - T_KICK + 0.05) * 30)
        d.arc((CUSHION[0] - 8 - r, FY - 6 - r, CUSHION[0] - 8 + r, FY - 6 + r), 20, 80, fill=C["white"], width=2)
        if c.t < T_KICK + 0.08:
            burst(c.world, CUSHION[0] - 2, FY - 5, 3, 7, C["gold_hi"], spikes=7)
    if T_KICK <= c.t < T_SPLASH:
        p = (c.t - T_KICK) / (T_SPLASH - T_KICK)
        fly(c.world, cushion(), (CUSHION[0], FY - 3), (164, 120), p, lift=26, spin=2.0)
    elif c.t >= T_SPLASH:
        splash(c.world, 164, 122, c.t - T_SPLASH, size=1.2, seed=15)
    if c.t >= t_drop:
        age = c.t - t_drop
        y0, y1 = 88, FY - 1
        p = min(1.0, age / 0.3)
        y = lerp(y0, y1, ease_in(p))
        bounce = int(abs(math.sin((age - 0.3) * 16)) * 3 * max(0.0, 1 - (age - 0.3) / 0.4)) if age > 0.3 else 0
        paste_rot(c.world, mic_prop(), GX - 14, int(y) - bounce, 90 if age > 0.3 else int(age * 300))
    yield "ui"
    if t_drop + 0.3 <= c.t < t_drop + 1.3:
        ux, uy = c.to_ui(GX - 22, FY - 4)
        big_text(c.ui, (ux, uy + (pop_dy(c.t - t_drop - 0.3) or 0)), "CLUNK.", PRESS, top=C["white"],
                 bottom=C["dim"], anchor="rb")


@lru_cache(maxsize=8)
def _glow(r):
    ys, xs = np.mgrid[-r:r + 1, -r:r + 1]
    return np.clip(1 - np.hypot(xs, ys) / r, 0, 1).astype(np.float32)


def glow_mask(cx, cy, r):
    m = np.zeros((H, W), np.float32)
    g = _glow(r)
    x0, y0 = int(cx) - r, int(cy) - r
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + 2 * r + 1), min(H, y0 + 2 * r + 1)
    if xb > xa and yb > ya:
        m[ya:yb, xa:xb] = g[ya - y0:yb - y0, xa - x0:xb - x0]
    return m


# --- wreckage of the argument ------------------------------------------------------------------------

debris(line_t("v1", 9, "flag") + 0.5, white_flag_float, 118, 126, seed=1, drift=0.15)
debris(T_INV_SPLASH, invoice_float, *INVOICE_AT, seed=2, drift=-0.1)
debris(TL.hit_of(TL.line("v1", 13))["t"] + 0.7, letter_bundle, 186, 140, seed=3, drift=-0.12)
debris(T_SPLASH, cushion, 164, 122, seed=4, drift=0.1)
