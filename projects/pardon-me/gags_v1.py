"""Verse 1: Trump has the floor, Bibi heckles from the desk (v1 0-13).

Trump's visual aids: Bibi's biggest fan blows his hair off; a report card for the
Nobel letter; cigars plus champagne, and a tip jar; a gift-wrapped jumbo jet and a
word too big for the page; dirty laundry pressed at Blair House and aired over the
hall; five ballot boxes and a man hanging by one hair; a head scan; the tariff
board; a NO with hearts on; the cartoon bomb as kindergarten art; an ACME crate;
and a pardoned turkey whose outlook is murky.
"""
import art
import art_v1 as A
import hall
from gagkit import (C, INK, PRESS, PRESS16, SILK, SILK16, V, Image, ImageDraw, anchor, back_out, blend, bomb_doodle,
                    bubble, burst, clamp, ease_in, ease_out, face, figure, flip, fly, gag, hit_t, label, lerp, line_t,
                    lru_cache, marker_arrow, math, np, paste, paste_rot, pixel, pose, puff, ramp, ring, rnd, sparkle,
                    stroke, text_width, underline, write, wt)

# where a font's capitals sit when `write` puts text at y: (offset from y, height)
CAPS = {SILK: (2, 5), PRESS: (0, 7), SILK16: (7, 10), PRESS16: (0, 14)}


def W(idx, pat, n=0):
    """When a word of verse 1's line `idx` starts."""
    return line_t("v1", idx, pat, n)


def keep_page(c, since):
    """Leave an earlier page up (no flip animation): the caller redraws it in its "chart" phase."""
    c.page_flip = since


def ink_poly(img, pts, fill):
    """A filled polygon with a 1px ink outline, straight onto the world."""
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=tuple(C[fill] if isinstance(fill, str) else fill), outline=INK)


def pop_scale(img, spr, x, y, age, dur=0.18, anchor="mb"):
    """Paste a sprite that pops in (overshoots, then settles) from age 0."""
    if age < 0:
        return
    k = back_out(min(1.0, age / dur))
    if k < 0.98:
        w, h = max(1, int(spr.width * k)), max(1, int(spr.height * k))
        spr = spr.resize((w, h), Image.NEAREST)
    paste(img, spr, x, y, anchor)


# --- 0: "Bibi! Beautiful Bibi! Many people say you're my biggest fan." ------------------------------

FAN_UP, FAN_BLOW = W(0, "biggest"), W(0, "fan")
FAN_OFF = W(1, "wrote")                 # the fan winds down as the letter goes up
FAN_AT = (206, 106)                     # where the hub stops, beside the desk


def fan_spin(t):
    """The blades' turn (in 10-degree steps), slow while spinning up and flat out once it blows."""
    up = 2.0 * 24 * (min(t, FAN_BLOW) - FAN_UP)
    full = 5.0 * 24 * max(0.0, min(t, FAN_OFF) - FAN_BLOW)
    down = 1.5 * 24 * max(0.0, t - FAN_OFF)
    return int(up + full + down) % 12


def draw_fan(c):
    t = c.t
    if t < FAN_UP:
        return
    rise = back_out(ramp(t, FAN_UP, FAN_UP + 0.25))
    sink = ease_in(ramp(t, FAN_OFF + 0.2, FAN_OFF + 0.55))
    dy = round((1 - rise) * 80 + sink * 80)
    if dy >= 80:
        return
    hx, hy = FAN_AT[0], FAN_AT[1] + dy
    head = A.fan_head(fan_spin(t), FAN_BLOW - 0.15 <= t < FAN_OFF + 0.1)
    fx, fy = A.FAN_C
    d = ImageDraw.Draw(c.world)
    d.rectangle((hx + 9, hy + 22, hx + 13, hy + 80), fill=INK)              # the pole, down behind the desk
    d.rectangle((hx + 10, hy + 22, hx + 12, hy + 80), fill=C["steel_sh"])
    d.line([(hx + 10, hy + 22), (hx + 10, hy + 80)], fill=C["steel"])
    c.world.paste(head, (hx - fx, hy - fy), head)


def draw_fan_plate(c):
    """The fan's name plate, drawn in front so the desk's microphone doesn't cross it."""
    if not FAN_UP <= c.t < FAN_OFF + 0.55:
        return
    rise = back_out(ramp(c.t, FAN_UP, FAN_UP + 0.25))
    sink = ease_in(ramp(c.t, FAN_OFF + 0.2, FAN_OFF + 0.55))
    dy = round((1 - rise) * 80 + sink * 80)
    top = FAN_AT[1] + dy + 23
    if top >= 141:
        return
    plate = A.fan_plate()
    part = plate.crop((0, 0, plate.width, min(plate.height, 141 - top)))
    c.world.paste(part, (FAN_AT[0] + 11 - plate.width // 2, top), part)


def wind(c, strength):
    """Streaks of air from the fan across the rostrum, Trump and the chart."""
    if strength <= 0:
        return
    d = ImageDraw.Draw(c.world)
    age = c.t - FAN_BLOW
    for i in range(22):
        if rnd("wk", i) > strength:
            continue
        speed = 420 + 260 * rnd("ws", i)
        run = age * speed - rnd("wo", i) * 140
        if run < 0:
            continue
        x = FAN_AT[0] - 12 - run % 210
        y = 84 + rnd("wy", i) * 50 + 2 * math.sin(c.t * 9 + i)
        n = 8 + 16 * rnd("wl", i)
        color = C["white"] if i % 3 else A.BLADE
        d.line([(x, y), (x + n, y)], fill=color)
        if i % 4 == 0:
            d.arc((x - 4, y - 3, x + 2, y + 3), 90, 300, fill=color)


def blown_hair(c, gust):
    """Trump's comb-over lifted off the brow and streaming back in the gale."""
    tx, ty = anchor(c, "trump", "top")

    def P(x, y):                                                           # design grid -> world
        return (tx + x - 16, ty + y)
    flap = 2 * math.sin(c.t * 40) * gust
    ink_poly(c.world, [P(14, 1), P(22, 2), P(27, 5), P(24, 7), P(19, 9), P(15, 7)], "tskin_hi")     # the bare brow
    pts = [P(26, 3), P(18, -1), P(6, -3), P(-4, -2 + flap), P(-12, -4 + 2 * flap), P(-16, 1 + flap),
           P(-8, 3 - flap), P(2, 4), P(14, 5)]
    ink_poly(c.world, pts, "thair")
    d = ImageDraw.Draw(c.world)
    d.line([P(18, 1), P(4, -1), P(-8, 0 + flap)], fill=C["thair_hi"])
    d.line([P(12, 4), P(-2, 2)], fill=C["thair_sh"])


def blown_tie(c, gust):
    """The long red tie flies out over his shoulder."""
    cx, cy = anchor(c, "trump", "chest")
    kx, ky = cx, cy - 8                                                      # the knot
    pts_top, pts_bot = [], []
    for k in range(7):
        s = k / 6
        x = kx - 3 - 20 * s * gust
        y = ky + 1 - 4 * s * gust + 2.5 * math.sin(c.t * 34 - k * 1.1) * s
        w = 1.5 + 1.2 * s
        pts_top.append((x, y - w))
        pts_bot.append((x, y + w))
    ink_poly(c.world, [(kx, ky - 1)] + pts_top + pts_bot[::-1] + [(kx, ky + 2)], "tie")
    ImageDraw.Draw(c.world).line(pts_top[1:], fill=C["tie_hi"])


def glam_feed(c, img, box):
    """Bibi's live feed in a beauty filter: a pink haze, twinkles and a new caption."""
    V.live_feed(c, img, box, "bibi", -1)
    x0, y0, x1, y1 = box
    blend(img, glam_mask(box), (255, 150, 200), 0.55)
    age = c.t - W(0, "Beautiful")
    for k in range(6):
        if age < 0.08 * k:
            continue
        sx = x0 + 6 + rnd("gx", k) * (x1 - x0 - 12)
        sy = y0 + 6 + rnd("gy", k) * (y1 - y0 - 20)
        size = 1 + int((c.t * 6 + k) % 3)
        sparkle(img, int(sx), int(sy), size, C["white"])
    label(img, (x0 + 2, y1 - 12), "BEAUTIFUL BIBI", SILK, bg=(255, 196, 226), fg=INK)


@lru_cache(maxsize=4)
def glam_mask(box):
    x0, y0, x1, y1 = box
    m = np.zeros((180, 320), np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    r = np.hypot((xx - cx) / ((x1 - x0) / 2), (yy - cy) / ((y1 - y0) / 2))
    m[y0:y1, x0:x1] = np.clip((r - 0.55) / 0.45, 0, 1)
    return m


def gust_at(t):
    return ramp(t, FAN_BLOW, FAN_BLOW + 0.1) * (1 - ramp(t, FAN_OFF - 0.1, FAN_OFF + 0.25))


@gag("v1", 0)
def biggest_fan(c, L):
    if wt(L, "Beautiful") <= c.t < FAN_UP:
        c.screens["R"] = glam_feed
    gust = gust_at(c.t)
    if gust > 0:
        c.st["trump"]["lean"] = -2
        c.st["trump"]["eyes"] = "squint"
    yield "mid"
    draw_fan(c)
    if gust > 0:
        wind(c, gust)
        blown_tie(c, gust)
        blown_hair(c, gust)
    yield "front"
    draw_fan_plate(c)


# --- 1: "You wrote the Nobel people for me. Smartest letter. Tremendous plan." -----------------------

LETTER_UP = W(1, "You") + 0.12          # the gale blows the cover sheet over


def letter_page(page, t):
    """Bibi's letter to the Nobel committee, graded by Trump."""
    write(page, (3, 3), "DEAR NOBEL,", "blue", t - W(1, "wrote"), cps=34, bold=True)
    write(page, (3, 13), "GIVE TRUMP", "black", t - W(1, "people"), cps=34)
    write(page, (3, 21), "THE PRIZE!", "black", t - W(1, "for"), cps=34)
    sig = write(page, (3, 31), "LOVE, BIBI", "blue", t - W(1, "me"), cps=34)
    if t >= W(1, "me") + 0.3:
        h = A.heart(3)
        page.paste(h, (sig[2] + 2, 30), h)
    smart = W(1, "Smartest")
    if t >= smart:
        write(page, (77, 15), "A+", "red", 1e9, fnt=PRESS16, anchor="ma")
        ring(page, 76, 22, 14, 12, "red", (t - smart - 0.1) / 0.35)
    if t >= W(1, "Tremendous"):
        write(page, (3, 46), "TREMENDOUS!", "red", t - W(1, "Tremendous"), cps=30, bold=True)
    hit = W(1, "plan") + 0.04
    if t >= hit:
        k = back_out(min(1.0, (t - hit) / 0.15))
        star = A.gold_star(7)
        if k < 0.98:
            star = star.resize((max(1, int(star.width * k)), max(1, int(star.height * k))), Image.NEAREST)
        page.paste(star, (79 - star.width // 2, 46 - star.height // 2), star)


@gag("v1", 1)
def nobel_letter(c, L):
    flip(c, LETTER_UP)
    if wt(L, "Smartest") <= c.t < wt(L, "Tremendous"):
        pose(c, "trump", facing=-1, arm="point")
    gust = gust_at(c.t)
    if gust > 0:
        c.st["trump"]["lean"] = -2
    yield "chart"
    if c.t >= LETTER_UP:
        letter_page(c.page, c.t)
    yield "mid"
    draw_fan(c)
    if gust > 0:
        wind(c, gust)
        blown_tie(c, gust)
        blown_hair(c, gust)
    yield "front"
    draw_fan_plate(c)


# --- 2: "Indicted for cigars and champagne? Bibi, that's a tip for a waiter." --------------------------

CIGAR_UP = W(2, "Indicted")


def doodle_cigar(page, x, y):
    d = ImageDraw.Draw(page)
    d.rectangle((x, y, x + 30, y + 7), fill=C["mk_black"])
    d.rectangle((x + 1, y + 1, x + 29, y + 6), fill=(150, 96, 52))
    d.line([(x + 1, y + 1), (x + 29, y + 1)], fill=(190, 130, 76))
    d.line([(x + 1, y + 6), (x + 29, y + 6)], fill=(116, 70, 40))
    d.rectangle((x + 21, y + 1, x + 24, y + 6), fill=C["mk_red"])
    d.rectangle((x - 3, y + 1, x, y + 6), fill=(140, 140, 150))            # ash, and a curl of smoke
    d.point((x - 3, y + 3), fill=C["orange"])
    stroke(page, [(x - 4, y), (x - 7, y - 4), (x - 3, y - 8), (x - 6, y - 12)], (150, 150, 160))


def doodle_bottle(page, x, y):
    """A champagne bottle, (x, y) its foil top."""
    d = ImageDraw.Draw(page)
    d.polygon([(x - 2, y), (x + 2, y), (x + 2, y + 6), (x + 5, y + 10), (x + 5, y + 24), (x - 5, y + 24),
               (x - 5, y + 10), (x - 2, y + 6)], fill=(40, 110, 64), outline=C["mk_black"])
    d.rectangle((x - 2, y, x + 2, y + 5), fill=C["gold"], outline=C["mk_black"])
    d.rectangle((x - 4, y + 13, x + 4, y + 18), fill=C["paper"])
    d.line([(x + 3, y + 11), (x + 3, y + 22)], fill=(90, 170, 110))


def cigar_page(page, t):
    write(page, (45, 3), "INDICTED FOR:", "black", t - CIGAR_UP, cps=40, anchor="ma", bold=True)
    if t >= W(2, "cigars"):
        doodle_cigar(page, 8, 27)
    if t >= W(2, "and"):
        write(page, (41, 27), "+", "black", fnt=PRESS)
    if t >= W(2, "champagne"):
        doodle_bottle(page, 58, 17)
    if t >= W(2, "champagne") + 0.35:
        write(page, (78, 21), "?", "red", fnt=PRESS16, anchor="ma")


def drop_in(img, spr, x, y, age, fall=18, dur=0.2):
    """Paste a sprite (bottom centre at x, y) that drops in from above and bounces; nothing before age 0."""
    if age < 0:
        return
    dy = round((1 - back_out(min(1.0, age / dur))) * -fall)
    paste(img, spr, x, y + dy, "mb")


@gag("v1", 2)
def tip_jar(c, L):
    if c.t < CIGAR_UP:
        keep_page(c, LETTER_UP)
    else:
        flip(c, CIGAR_UP)
    yield "chart"
    if c.t < CIGAR_UP:
        letter_page(c.page, c.t)
    else:
        cigar_page(c.page, c.t)
    yield "front"
    drop_in(c.world, A.tip_jar(), 236, 144, c.t - wt(L, "tip"))
    if c.t >= wt(L, "waiter"):
        cx, cy = anchor(c, "bibi", "chest")
        drop_in(c.world, A.bow_tie(), cx, cy - 4, c.t - wt(L, "waiter"), fall=6, dur=0.12)


# --- 3: "Qatar gave me a jumbo jet! Think bigger, Bibi! Think greater!" ------------------------------

THINK_UP = W(3, "Think")


def jet_pos(t):
    arrive, land = W(3, "jumbo"), W(3, "jet") + 0.3
    leave = W(4, "You") - 0.7
    if t < arrive:
        return None
    if t < land:
        x = 380 - 220 * ease_out((t - arrive) / (land - arrive))
    elif t < leave:
        x = 160
    else:
        x = 160 - 260 * ease_in((t - leave) / 0.55)
    return x, 27 + round(math.sin(t * 3))


def big_word(page, s, step, y, color="red"):
    """A marker word centred at height y, in one of four sizes (step 0-3); the page clips it."""
    fnt = (SILK, PRESS, SILK16, PRESS16)[step]
    top, h = CAPS[fnt]
    write(page, (45, y - h // 2 - top), s, color, fnt=fnt, anchor="ma", bold=step in (0, 2))


def think_page(page, t):
    write(page, (45, 3), "THINK", "blue", t - THINK_UP, cps=30, anchor="ma", bold=True)
    big = W(3, "bigger")
    if t >= big:
        big_word(page, "BIGGER", min(3, int((t - big) / 0.12)), 24)
    great = W(3, "greater")
    if t >= great:
        write(page, (3, 44), "JET", "black", fnt=PRESS)
        write(page, (38, 40), ">", "red", fnt=PRESS16, anchor="ma")
        write(page, (49, 44), "CIGAR", "black", fnt=PRESS)


@gag("v1", 3)
def jumbo_jet(c, L):
    if c.t < THINK_UP:
        keep_page(c, CIGAR_UP)
    else:
        flip(c, THINK_UP)
    yield "back"
    pos = jet_pos(c.t)
    if pos:
        jet = A.jumbo_jet()
        x, y = pos
        c.world.paste(jet, (int(x - jet.width // 2), int(y - jet.height // 2)), jet)
        if x == 160:
            for k in range(4):
                if int(c.t * 8 + k * 3) % 4 == 0:
                    sparkle(c.world, int(x - 36 + rnd("js", k) * 72), int(y - 14 + rnd("jy", k) * 28), 2,
                            C["gold_hi"])
    yield "chart"
    if c.t < THINK_UP:
        cigar_page(c.page, c.t)
    else:
        think_page(c.page, c.t)


# --- 4: "You brought your dirty laundry to my guest house to get pressed." ------------------------------

CASE_AT = (233, 145)                    # bottom centre of the suitcase on the desk
LAUNDRY = (("shirt", (215, 146)), ("sock", (228, 155)), ("vest", (249, 146)), ("boxers", None))
AIR_T = W(5, "air")                     # the laundry goes up on the line
LAUNDRY_END = W(6, "Five") - 0.12


def laundry_spot(c, kind, at):
    """Where a piece lands (bottom centre): its spot on the desk, or Bibi's head for the boxers."""
    if at is not None:
        return at
    x, y = anchor(c, "bibi", "top")
    return x - 1, y + 5


def draw_laundry(c):
    """Bibi's suitcase on the desk: dropped, burst open, the laundry flung about, then ironed."""
    t = c.t
    brought, dirty, pressed = W(4, "brought"), W(4, "dirty"), W(4, "pressed")
    if not brought <= t < LAUNDRY_END:
        return
    img = c.world
    opened = t >= dirty
    drop_in(img, A.suitcase(opened), CASE_AT[0], CASE_AT[1], t - brought)
    if not opened:
        return
    if t < AIR_T:
        for k, (kind, at) in enumerate(LAUNDRY):
            p = (t - dirty - 0.05 * k) / 0.3
            if p < 0:
                continue
            spr = A.laundry(kind)
            end = laundry_spot(c, kind, at)
            if p < 1:
                fly(img, spr, (CASE_AT[0], CASE_AT[1] - 14), (end[0], end[1] - spr.height // 2), p, lift=18,
                    spin=1)
            else:
                paste(img, spr, end[0], end[1], "mb")
        for j in range(3):                                                    # the stink
            x0 = CASE_AT[0] - 9 + 9 * j
            rise = (t * 9 + j * 4) % 8
            pts = [(x0 + 2 * math.sin(t * 7 + j + k * 1.3), 129 - rise - 4 * k) for k in range(4)]
            stroke(img, pts, (120, 176, 70))
    if t >= pressed - 0.12:
        k = ease_in(ramp(t, pressed - 0.12, pressed))
        x, y = CASE_AT[0] + 1, round(lerp(100, CASE_AT[1] - 13, k))
        paste(img, A.iron(), x, y, "mb")
        for j in range(3):
            puff(img, x - 6 + 6 * j, y - 4, t - pressed - 0.05 * j, 0.6, seed=j, color=(240, 242, 250),
                 drift=(-4 + 4 * j, -14), life=0.9)


def draw_sign(c):
    """The guest house's sign drops in on chains over Bibi."""
    at = W(4, "guest")
    if not at <= c.t < LAUNDRY_END:
        return
    spr = A.blair_sign()
    k = back_out(min(1.0, (c.t - at) / 0.25))
    x = 271 - spr.width // 2
    y = round(66 - (1 - k) * 40)
    d = ImageDraw.Draw(c.world)
    for cx in (x + 8, x + spr.width - 9):
        d.line([(cx, 62), (cx, y + 1)], fill=INK, width=3)
        for cy in range(63, y + 1, 3):
            d.point((cx, cy), fill=C["steel"])
    c.world.paste(spr, (x, y), spr)


@gag("v1", 4)
def dirty_laundry(c, L):
    flip(c, L.t0)                                                            # back to the cover sheet
    yield "back"
    draw_sign(c)
    yield "chart"
    V.default_page(c, c.page)
    yield "front"
    draw_laundry(c)


# --- 5: "Bibi, that's what the press is for. They'll air it with the rest." ------------------------------

PRESS_T = W(5, "press")
SNAPS = ((9, 0.0), (12, 0.14), (10, 0.3), (13, 0.46))                  # (front-row seat, when its flash goes)
LINE_A, LINE_B, SAG = (99, 14), (221, 14), 9
HANG = ("shirt", "boxers", "sock", "vest", "shirt", "sock", "boxers")


def rope_y(x):
    u = (x - LINE_A[0]) / (LINE_B[0] - LINE_A[0])
    return LINE_A[1] + SAG * 4 * u * (1 - u)


def clothesline(c):
    """The laundry, aired: pegged out on a line strung between the two screens."""
    t = c.t
    if t < AIR_T:
        return
    p = ease_out(ramp(t, AIR_T, AIR_T + 0.3))
    xe = LINE_A[0] + (LINE_B[0] - LINE_A[0]) * p
    d = ImageDraw.Draw(c.world)
    pts = [(x, rope_y(x)) for x in range(LINE_A[0], int(xe) + 1, 4)] + [(xe, rope_y(xe))]
    d.line(pts, fill=(240, 236, 222))
    for k, kind in enumerate(HANG):
        x = LINE_A[0] + (k + 0.8) * (LINE_B[0] - LINE_A[0]) / (len(HANG) + 0.6)
        if x > xe:
            continue
        spr = A.laundry(kind)
        sway = round(1.2 * math.sin(t * 6 + k * 1.7))
        y = int(rope_y(x))
        c.world.paste(spr, (int(x - spr.width // 2) + sway, y - 1), spr)
        d.point((int(x) + sway - 2, y), fill=C["desk_sh"])
        d.point((int(x) + sway + 2, y), fill=C["desk_sh"])


def breaking_feed(c, img, box):
    """Bibi's live feed under a BREAKING NEWS chyron."""
    V.live_feed(c, img, box, "bibi", -1)
    x0, _, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y1 - 16, x1 - 1, y1 - 1), fill=INK)
    d.rectangle((x0, y1 - 15, x1 - 1, y1 - 9), fill=C["red"])
    pixel.text(img, (x0 + 3, y1 - 18), "BREAKING", SILK, C["white"], shadow=None)
    pixel.text(img, (x0 + 4, y1 - 18), "BREAKING", SILK, C["white"], shadow=None)
    d.rectangle((x0, y1 - 8, x1 - 1, y1 - 1), fill=C["white"])
    news = "DIRTY LAUNDRY AIRED AT UN  +++  "
    tw = text_width(news, SILK)
    off = int((c.t - PRESS_T) * 40) % tw
    strip = Image.new("RGB", (x1 - x0, 7), C["white"])
    for k in range(3):
        pixel.text(strip, (k * tw - off, -4), news, SILK, INK, shadow=None)
    img.paste(strip, (x0, y1 - 8))


def photographers(c):
    """Delegates up on their feet, cameras held high overhead; the flashguns go off."""
    t = c.t
    if not PRESS_T - 0.1 <= t < AIR_T + 0.5:
        return
    d = ImageDraw.Draw(c.world)
    cam = A.press_camera()
    for i, dt in SNAPS:
        x, y, _ = hall.DELEGATES[i]
        lift = c.crowd["stand"].get(i, 0.0)
        y -= round(lift * 10)
        cy = round(y + 6 - lift * 24)                                   # the camera, up on raised arms
        for side in (-1, 1):
            d.line([(x + side * 6, y + 12), (x + side * 4, cy + 2)], fill=INK, width=3)
            d.line([(x + side * 6, y + 12), (x + side * 4, cy + 2)], fill=hall.DELEGATE_TONES[i % 4])
        c.world.paste(cam, (x - cam.width // 2, cy - cam.height + 3), cam)
        age = t - PRESS_T - dt
        if 0 <= age < 0.09:
            burst(c.world, x - 2, cy - cam.height + 4, 3, 10, C["white"], spikes=8, rot=rnd("fl", i))


@gag("v1", 5)
def air_it(c, L):
    flip(c, L.t0 - 0.2)
    if c.t >= PRESS_T:
        c.screens["R"] = breaking_feed
    for i, dt in SNAPS:
        c.crowd["stand"][i] = ramp(c.t, PRESS_T - 0.1, PRESS_T + 0.05) * (1 - ramp(c.t, AIR_T + 0.3, AIR_T + 0.5))
        if 0 <= c.t - PRESS_T - dt < 0.05:
            c.add_flash(0.18)
    yield "back"
    draw_sign(c)
    clothesline(c)
    yield "chart"
    V.default_page(c, c.page)
    yield "front"
    draw_laundry(c)
    photographers(c)


# --- 6: "Five elections in four years, and you hung on by a hair." -----------------------------------------

BALLOT_UP = W(6, "Five")


def ballot_box(page, x, y, age):
    """A ballot box (11x11) in marker, a ballot going into its slot."""
    if age < 0:
        return
    p = min(1.0, age / 0.12)
    stroke(page, [(x, y + 3), (x + 10, y + 3), (x + 10, y + 13), (x, y + 13), (x, y + 3)], "blue", p)
    if p >= 1:
        d = ImageDraw.Draw(page)
        d.rectangle((x + 1, y + 4, x + 9, y + 12), fill=(214, 228, 250))
        d.line([(x + 3, y + 5), (x + 7, y + 5)], fill=C["mk_black"])
        d.rectangle((x + 3, y - 2, x + 7, y + 4), fill=C["white"], outline=C["mk_black"])
        d.point((x + 4, y), fill=C["mk_red"])
        d.point((x + 6, y), fill=C["mk_red"])
        d.point((x + 5, y + 1), fill=C["mk_red"])


def hanging_bibi(page, t, since):
    """A stick-figure Bibi hanging on to one long grey hair with both hands, legs kicking."""
    p = min(1.0, (t - since) / 0.2)
    sway = 1.8 * math.sin((t - since) * 4.2)
    hx, hy = 78 + sway, 24
    gx, gy = hx, hy - 12                                                    # where his hands grip the hair
    stroke(page, [(78, 0), (78 + sway * 0.5, 6), (gx, gy)], (96, 96, 112), p * 2)
    if p < 0.5:
        return
    for side in (-1, 1):                                                    # arms up, round his head
        stroke(page, [(hx + side, hy + 7), (hx + side * 7, hy), (gx + side, gy + 1)], "black", 1)
    d = ImageDraw.Draw(page)
    d.ellipse((hx - 5, hy - 5, hx + 5, hy + 5), fill=C["paper"], outline=C["mk_black"])
    d.arc((hx - 5, hy - 5, hx + 5, hy + 5), 120, 240, fill=C["bhair_sh"], width=2)      # grey round the back
    d.arc((hx - 5, hy - 5, hx + 5, hy + 5), 300, 360, fill=C["bhair_sh"], width=2)
    d.point((hx - 2, hy - 1), fill=C["mk_black"])
    d.point((hx + 2, hy - 1), fill=C["mk_black"])
    d.rectangle((hx - 1, hy + 2, hx + 1, hy + 3), fill=C["mk_red"])                    # a little o of panic
    kick = 2 * math.sin(t * 13)
    stroke(page, [(hx, hy + 5), (hx, hy + 16)], "black", 1)
    stroke(page, [(hx, hy + 16), (hx - 4 + kick, hy + 24)], "black", 1)
    stroke(page, [(hx, hy + 16), (hx + 4 + kick, hy + 24)], "black", 1)


def hair_page(page, t):
    write(page, (3, 2), "5 ELECTIONS", "black", t - BALLOT_UP, cps=44, bold=True)
    span5 = (W(6, "in") - BALLOT_UP) / 5
    for k in range(5):
        ballot_box(page, 3 + 13 * k, 13, t - BALLOT_UP - span5 * k)
    four = W(6, "four")
    if t >= four:
        p = (t - four) / 0.25
        stroke(page, [(3, 29), (3, 32), (66, 32), (66, 29)], "red", p)
        write(page, (3, 35), "4 YRS", "red", t - four - 0.15, cps=30, bold=True)
    hung = W(6, "hung")
    if t >= hung:
        hanging_bibi(page, t, hung)
    hair = W(6, "hair")
    if t >= hair:
        write(page, (3, 47), "1 HAIR", "red", t - hair, cps=30, bold=True)
        marker_arrow(page, (37, 49), (75, 10), "red", (t - hair - 0.1) / 0.3)


@gag("v1", 6)
def by_a_hair(c, L):
    flip(c, BALLOT_UP)
    yield "back"
    clothesline(c)
    draw_sign(c)
    yield "chart"
    if c.t >= BALLOT_UP:
        hair_page(c.page, c.t)
    yield "front"
    draw_laundry(c)


# --- 7: "That's impressive, Bibi, for a guy with not a lot up there." --------------------------------------

SCAN_T = W(7, "That")


def scan_feed(c, img, box):
    """Bibi's live feed under a head scan: a sweeping line, then the readings."""
    V.live_feed(c, img, box, "bibi", -1)
    x0, y0, x1, y1 = box
    t = c.t
    ph = ((t - SCAN_T) % 0.9) / 0.9
    sy = int(y0 + 2 + ph * (y1 - y0 - 20))
    m = np.zeros((180, 320), np.float32)
    m[y0:sy, x0:x1] = 1.0
    blend(img, m, (60, 230, 120), 0.22)
    d = ImageDraw.Draw(img)
    for gx in range(x0 + 4, x1, 8):
        for gy in range(y0 + 4, sy, 8):
            d.point((gx, gy), fill=(140, 255, 170))
    d.line([(x0, sy), (x1 - 1, sy)], fill=(170, 255, 190))
    d.line([(x0, sy + 1), (x1 - 1, sy + 1)], fill=(60, 200, 110))
    if int(t * 3) % 2 == 0 and t < W(7, "there") + 0.04:
        pixel.text(img, (x1 - 51, y0 - 2), "SCANNING", SILK, (170, 255, 190), shadow=INK)
    d.rectangle((x0, y1 - 17, x1 - 1, y1 - 1), fill=(10, 24, 18))
    d.line([(x0, y1 - 17), (x1 - 1, y1 - 17)], fill=(60, 200, 110))
    if t >= W(7, "lot"):
        pixel.text(img, (x0, y1 - 21), "HAIR:", SILK, (170, 255, 190), shadow=None)
        pixel.text(img, (x0 + 33, y1 - 21), "3%", SILK, (255, 210, 90), shadow=None)
    if t >= W(7, "up"):
        pixel.text(img, (x0, y1 - 13), "BRAIN:", SILK, (170, 255, 190), shadow=None)
        if t < W(7, "there") + 0.04:
            dots = "." * (1 + int(t * 8) % 3)
            pixel.text(img, (x0 + 33, y1 - 13), dots, SILK, (255, 210, 90), shadow=None)
        elif t < W(7, "there") + 0.5 or int(t * 5) % 3:
            pixel.text(img, (x0 + 33, y1 - 13), "NOT FOUND", SILK, (255, 90, 90), shadow=None)


@gag("v1", 7)
def scan(c, L):
    keep_page(c, BALLOT_UP)
    if c.t >= SCAN_T - 0.1:
        c.screens["R"] = scan_feed
    if c.t >= wt(L, "up"):
        pose(c, "trump", arm="up")
    yield "chart"
    hair_page(c.page, c.t)


# --- 8: "I put a tariff on my best friend. Seventeen percent. Precise." --------------------------------------

BOARD_AT = (176, 79)                    # top-left of the board, held up beside his head
HEART_PINK = (255, 96, 160)


def board_row_y(k):
    return BOARD_AT[1] + 1 + 13 + 9 * k


@gag("v1", 8)
def tariff_board(c, L):
    flip(c, L.t0)
    if c.t < wt(L, "tariff") - 0.1:
        c.screens["R"] = scan_feed                                          # the scan's verdict stays up a beat
    up = wt(L, "tariff")
    if c.t >= up - 0.1:
        pose(c, "trump", arm="hold", far="hold")
    if c.t >= wt(L, "Precise"):
        pose(c, "trump", arm="pinch", far="hold")
    if wt(L, "Seventeen") <= c.t < hit_t(L) + 0.5:
        c.shot = "rapper"
    yield "back"
    if c.t >= up - 0.1:
        k = ease_out(ramp(c.t, up - 0.1, up + 0.06))
        board = A.tariff_board()
        x, y = BOARD_AT[0], round(BOARD_AT[1] + (1 - k) * 50)
        c.world.paste(board, (x, y), board)
        img = c.world
        ry = board_row_y(3) + y - BOARD_AT[1]
        best = wt(L, "best")
        if c.t >= best:
            ring(img, x + 32, ry + 3, 31, 6, "red", (c.t - best) / 0.3)
        if c.t >= wt(L, "friend"):
            pop_scale(img, A.heart(3, HEART_PINK), x + 38, ry + 7, c.t - wt(L, "friend"), dur=0.22)
        sev = wt(L, "Seventeen")
        if c.t >= sev:
            underline(img, x + 43, x + 61, ry + 8, "red", (c.t - sev) / 0.2)
        if c.t >= wt(L, "percent"):
            underline(img, x + 43, x + 61, ry + 10, "red", (c.t - wt(L, "percent")) / 0.2)
    yield "chart"
    V.default_page(c, c.page)


# --- 9: "You flew in to beg me. I said no. But I said it nice." ------------------------------------------------

def plane_path(t, t0, t1):
    """Down from the top right over Bibi's head to a landing on his desk."""
    u = ease_out(clamp((t - t0) / (t1 - t0), 0, 1))
    p0, p1, p2 = (345, 34), (232, 54), (233, 141)
    x = (1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * p1[0] + u * u * p2[0]
    y = (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * p1[1] + u * u * p2[1]
    dx = 2 * (1 - u) * (p1[0] - p0[0]) + 2 * u * (p2[0] - p1[0])
    dy = 2 * (1 - u) * (p1[1] - p0[1]) + 2 * u * (p2[1] - p1[1])
    ang = 0.0 if u >= 0.97 else -math.degrees(math.atan2(dy, -dx))
    return x, y, max(-50.0, min(50.0, ang))


def no_page(page, t):
    no = W(9, "no")
    write(page, (45, 8), "NO.", "red", t - no, cps=14, fnt=PRESS16, anchor="ma", bold=True)
    spots = ((10, 6), (80, 8), (8, 30), (82, 29))
    for k, (x, y) in enumerate(spots):
        age = t - W(9, "But") - 0.12 * k
        if age >= 0:
            pop_scale(page, A.heart(5), x, y + 13, age)
    nice = W(9, "nice")
    if t >= nice:
        write(page, (45, 30), "(NICELY)", "red", t - nice, cps=48, anchor="ma")
        write(page, (45, 44), "XOXO, DJT", "blue", t - nice - 0.2, cps=40, anchor="ma", bold=True)


@gag("v1", 9)
def said_it_nice(c, L):
    no = wt(L, "no")
    flip(c, no)
    beg = wt(L, "beg")
    if beg - 0.08 <= c.t < no + 0.2:
        pose(c, "bibi", arm="hold", far="hold")
        face(c, "bibi", brows="worried", mouth="o", eyes="wide")
    if no <= c.t < wt(L, "But"):
        pose(c, "trump", arm="palm")
    if c.t >= wt(L, "nice") - 0.2:
        pose(c, "trump", arm="thumb")
    yield "chart"
    if c.t >= no:
        no_page(c.page, c.t)
    yield "front"
    t0 = wt(L, "flew")
    if c.t >= t0:
        x, y, ang = plane_path(c.t, t0, wt(L, "to") + 0.05)
        paste_rot(c.world, A.small_plane(), x, y - 5, ang, "mm")
        land = wt(L, "to") + 0.05
        if c.t >= land:
            puff(c.world, x + 8, y - 2, c.t - land, 0.5, seed=9, color=(236, 230, 214), drift=(10, -3), life=0.6)
    if beg <= c.t < no + 0.1:
        bubble(c.world, 270, 90, "PLEASE?", tail=(265, 101))


# --- 10: "You drew a cartoon bomb with a marker at the UN." -----------------------------------------------------

BOMB_UP = W(10, "drew")


def kid_write(page, x, y, s, age, cps=24):
    """Uneven crayon capitals, each letter its own height and colour: a child's hand."""
    cols = ("red", "blue", "green", "black")
    for i, ch in enumerate(s[:max(0, int(age * cps))]):
        dy = int(rnd("kid", i) * 3) - 1
        write(page, (x, y + dy), ch, cols[i % 4], bold=True)
        x += text_width(ch, SILK) + (1 if ch == " " else 0)


def bomb_page(page, t):
    """Trump's copy of the 2012 poster, done up as kindergarten art."""
    cart = W(10, "cartoon")
    p = ramp(t, cart, W(10, "bomb") + 0.3)
    if p > 0:
        bomb_doodle(page, 33, 30, 13, p=p, color="black", fuse=True)
    m = W(10, "marker")
    if t >= m:
        q = (t - m) / 0.35
        stroke(page, [(12, 22), (56, 22)], "red", q, width=2)
        if q < 1.3:
            mx = 12 + 44 * min(1.0, q)
            pen = A_marker()
            page.paste(pen, (int(mx) - 1, 22 - pen.height), pen)
    un = W(10, "at")
    if t >= un:
        kid_write(page, 4, 47, "BY BIBI, AGE 62", t - un, cps=28)
    hit = W(10, "UN") + 0.04
    if t >= hit:
        pop_scale(page, A.gold_star(7), 76, 27, t - hit)
        write(page, (76, 30), "GOOD", "blue", t - hit - 0.06, cps=40, anchor="ma", bold=True)
        write(page, (76, 38), "JOB!", "blue", t - hit - 0.16, cps=40, anchor="ma", bold=True)


@lru_cache(maxsize=1)
def A_marker():
    return art.marker("mk_red", False, -35)


@lru_cache(maxsize=1)
def archive_card(w, h):
    """UN footage from 2012: Bibi at the rostrum holding up his poster, gone sepia."""
    img = Image.new("RGB", (w, h), C["marble"])
    hall.marble(img, (0, 0, w - 1, h - 1), seed=5)
    spr, a = figure("bibi", 1, arm="fist", mouth="open", brows="angry")
    hx, hy = a["head"]
    img.paste(spr, (24 - hx, 21 - hy), spr)
    d = ImageDraw.Draw(img)
    px0, py0, px1, py1 = 41, 3, 72, 36
    d.rectangle((px0 - 1, py0 - 1, px1 + 1, py1 + 1), fill=INK)
    d.rectangle((px0, py0, px1, py1), fill=C["white"])
    cx, cy, r = 56, 23, 9
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK)
    d.rectangle((cx + 3, cy - r - 3, cx + 7, cy - r + 1), fill=INK)
    d.line([(cx + 5, cy - r - 3), (cx + 8, cy - r - 6), (cx + 11, cy - r - 5)], fill=INK)
    d.line([(px0 + 3, cy - 6), (px1 - 3, cy - 6)], fill=C["red"], width=2)
    a = np.asarray(img, dtype=np.float32).mean(axis=2, keepdims=True) / 255.0
    lo, hi = np.array((46, 32, 22), np.float32), np.array((240, 218, 172), np.float32)
    return Image.fromarray((lo + (hi - lo) * a).round().astype(np.uint8))


def archive_feed(c, img, box):
    """The right screen runs the 2012 footage: sepia, scratched, flickering."""
    x0, y0, x1, y1 = box
    card = archive_card(x1 - x0, y1 - y0)
    img.paste(card, (x0, y0))
    f = c.f
    if f % 3 == 0:
        blend(img, archive_mask(box), (0, 0, 0), 0.12)
    d = ImageDraw.Draw(img)
    for k in range(14):
        gx = x0 + int(rnd("gr", f, k) * (x1 - x0))
        gy = y0 + int(rnd("gy", f, k) * (y1 - y0))
        d.point((gx, gy), fill=(30, 22, 16) if k % 2 else (250, 236, 200))
    sx = x0 + int(rnd("scr", f // 2) * (x1 - x0))
    d.line([(sx, y0), (sx, y1 - 1)], fill=(220, 200, 160))
    label(img, (x0 + 2, y0 + 2), "ARCHIVE 2012", SILK, bg=(36, 26, 18), fg=(240, 218, 172), border=(36, 26, 18))


@lru_cache(maxsize=2)
def archive_mask(box):
    x0, y0, x1, y1 = box
    m = np.zeros((180, 320), np.float32)
    m[y0:y1, x0:x1] = 1.0
    return m


@gag("v1", 10)
def cartoon_bomb(c, L):
    if c.t < BOMB_UP:
        keep_page(c, W(9, "no"))
    else:
        flip(c, BOMB_UP)
    if c.t >= BOMB_UP:
        c.screens["R"] = archive_feed
    if wt(L, "cartoon") <= c.t < wt(L, "with"):
        pose(c, "trump", facing=-1, arm="point")
    yield "chart"
    if c.t < BOMB_UP:
        no_page(c.page, c.t)
    else:
        bomb_page(c.page, c.t)


# --- 11: "Wile E. Netanyahu! Beep beep! Acme let you down again." -----------------------------------------------

CRATE_AT = (233, 145)
WILE_T, BEEP_T, ACME_T = W(11, "Wile"), W(11, "Beep"), W(11, "Acme")
BONK_T, DOWN_T = W(11, "you"), W(11, "down")
CRATE_GONE = W(12, "I") + 0.35         # the crate vanishes in a puff once Bibi is back up
STREAK_Y = 131                         # the Road Runner's lane: just under Bibi's chin, over the rostrum top
DUST = (226, 210, 170)


def genius_feed(c, img, box):
    """Bibi's live feed with a second caption over his name: the coyote's job title."""
    V.live_feed(c, img, box, "bibi", -1)
    x0, _, _, y1 = box
    label(img, (x0 + 2, y1 - 22), "SUPER GENIUS", SILK, bg=(250, 214, 90), fg=INK)


def road_runner(c, img):
    """"Beep beep!": a blue blur zips left to right under Bibi's nose and leaves its dust hanging in the air."""
    age = c.t - BEEP_T
    if not 0 <= age < 1.1:
        return
    run, xa, xb = 0.3, -30, 350
    head = xa + (xb - xa) * min(1.0, age / run)
    for j in range(10):
        x = 6 + 34 * j
        born = (x - xa) / (xb - xa) * run
        if age >= born:
            puff(img, x, STREAK_Y + 1, age - born, 0.55, seed=j, color=DUST, drift=(-3, -4), life=0.8)
    if age < run:
        d = ImageDraw.Draw(img)
        for k, dy in enumerate((-4, -1, 2, 5)):
            tail = head - 40 - 30 * rnd("rr", k)
            d.line([(tail, STREAK_Y + dy), (head - 6 - abs(dy), STREAK_Y + dy)],
                   fill=C["white"] if k % 2 else (190, 200, 240))
        d.ellipse((head - 10, STREAK_Y - 6, head + 2, STREAK_Y + 6), fill=(70, 90, 200), outline=INK)
        d.line([(head - 6, STREAK_Y - 5), (head - 13, STREAK_Y - 9)], fill=(70, 90, 200), width=2)   # the crest
        d.polygon([(head + 1, STREAK_Y - 2), (head + 6, STREAK_Y - 1), (head + 1, STREAK_Y + 1)], fill=C["gold"])


def draw_crate(c, img):
    """The ACME crate: dropped on the desk, its lid blown off, the glove out on its spring; gone in a puff."""
    t = c.t
    if t < WILE_T:
        return
    if t >= CRATE_GONE:
        puff(img, CRATE_AT[0], CRATE_AT[1] - 12, t - CRATE_GONE, 1.3, seed=4, color=DUST, drift=(0, -6), life=0.6)
        return
    opened = t >= ACME_T
    drop_in(img, A.acme_crate(not opened), CRATE_AT[0], CRATE_AT[1], t - WILE_T, fall=40, dur=0.25)
    if opened:
        age = t - ACME_T
        if age < 1.0:
            paste_rot(img, A.crate_lid(), CRATE_AT[0] - 10 - 30 * age, CRATE_AT[1] - 24 - 60 * age + 90 * age * age,
                      200 * age, "mm")
        spring_glove(c, img, ACME_T, BONK_T)


def dizzy_stars(c, img):
    """Three little stars circling Bibi's head."""
    hx, hy = anchor(c, "bibi", "head")
    star = A.gold_star(3)
    for k in range(3):
        ang = c.t * 6 + k * 2 * math.pi / 3
        img.paste(star, (int(hx + 15 * math.cos(ang)) - 5, int(hy - 17 + 3 * math.sin(ang)) - 5), star)


@gag("v1", 11)
def acme(c, L):
    keep_page(c, BOMB_UP)                                                  # the kindergarten bomb stays up
    if c.t >= wt(L, "Netanyahu"):
        c.screens["R"] = genius_feed
    b = c.st["bibi"]
    if BEEP_T + 0.08 <= c.t < ACME_T - 0.08:
        pose(c, "bibi", facing=1)                                          # his head whips round after the blur
        face(c, "bibi", eyes="wide", mouth="o")
    if c.t >= BONK_T:
        c.hit_react["bibi"] = False
        b.update(eyes="x", mouth="o", brows="worried", gesture=False, arm="cross")
        b["dy"] += round(12 * ease_out(ramp(c.t, DOWN_T, DOWN_T + 0.2)))
        b["dx"] += round(3 * max(0.0, 1 - (c.t - BONK_T) / 0.25))
    yield "chart"
    bomb_page(c.page, c.t)
    yield "front"
    img = c.world
    road_runner(c, img)
    draw_crate(c, img)
    if c.t >= BONK_T:
        dizzy_stars(c, img)


def spring_glove(c, img, start, bonk):
    """The spring-loaded boxing glove: out of the crate, into Bibi's face, and back."""
    t = c.t
    base = (CRATE_AT[0] + 4, CRATE_AT[1] - 20)
    target = (252, 112)
    if t < start + 0.1:
        return
    if t < bonk:
        p = ease_in(ramp(t, start + 0.1, bonk))
    else:
        p = 1 - 0.75 * ease_out(ramp(t, bonk + 0.15, bonk + 0.45))
    gx, gy = lerp(base[0], target[0], p), lerp(base[1], target[1], p)
    n = 9
    pts = []
    for k in range(n + 1):
        u = k / n
        px, py = lerp(base[0], gx - 4, u), lerp(base[1], gy, u)
        off = 3 * (1 if k % 2 else -1) if 0 < k < n else 0
        pts.append((px + off * 0.6, py + off * 0.8))
    d = ImageDraw.Draw(img)
    d.line(pts, fill=INK, width=3)
    d.line(pts, fill=C["steel"])
    glove = A.boxing_glove(1)
    img.paste(glove, (int(gx) - glove.width + 3, int(gy) - glove.height // 2), glove)
    if bonk <= t < bonk + 0.12:
        burst(img, target[0] + 4, target[1] - 2, 4, 9, C["white"], spikes=7)


# --- 12: "I asked your president to pardon you, like I pardon every turkey." ------------------------------------

PARDON_UP = W(12, "asked")
TURKEY_T = W(12, "pardon", 1)


def signature(page, x, y, w, p):
    """The famous signature: a tall, spiky seismograph in black marker."""
    pts = []
    for k in range(int(w / 2.2)):
        h = 4 + 7 * rnd("sig", k)
        pts.append((x + k * 2.2, y - (h if k % 2 else 0) + 2 * rnd("sb", k)))
    stroke(page, pts, "black", p)
    if p >= 1:
        stroke(page, [(x - 2, y + 4), (x + w + 2, y + 2)], "black", 1)


def pardon_page(page, t):
    write(page, (3, 3), "DEAR PRESIDENT", "blue", t - PARDON_UP, cps=40, bold=True)
    write(page, (3, 12), "HERZOG,", "blue", t - W(12, "president"), cps=30, bold=True)
    write(page, (3, 24), "PARDON BIBI!", "red", t - W(12, "pardon"), cps=34, bold=True)
    you = W(12, "you", 1)                                                  # "you," (not "your")
    if t >= you:
        signature(page, 8, 46, 56, (t - you) / 0.3)


@lru_cache(maxsize=2)
def turkey_bust(gobble):
    """The pardon turkey (with Bibi's hair) for a TV close-up: art.turkey doubled, facing left."""
    bird = art.turkey("bibi", -1, gobble)
    return bird.resize((bird.width * 2, bird.height * 2), Image.NEAREST)


def turkey_feed(c, img, box):
    """The right screen cuts to a turkey pardon, in close-up. The turkey has Bibi's hair."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    img.paste(V.feed_backdrop(w, h, False), (x0, y0))
    t = c.t
    gob = any(g <= t < g + 0.22 for g in GOBBLES)
    stuffed = t >= STUFF_T
    bird = turkey_bust(gob and not stuffed)
    bx, by = x0 + 20, y0 + 11 + (1 if gob else 0)
    crop = bird.crop((0, 0, min(bird.width, x1 - bx), min(bird.height, y1 - by)))
    img.paste(crop, (bx, by), crop)
    d = ImageDraw.Draw(img)
    ex, ey = bx + 15, by + 9                                                # his eye, looking anxious
    d.rectangle((ex, ey, ex + 3, ey + 3), fill=C["white"])
    d.rectangle((ex, ey + 1, ex + 1, ey + 3), fill=INK)
    d.line([(ex - 1, ey - 1), (ex + 4, ey - 3)], fill=(70, 70, 76), width=2)
    if stuffed:                                                             # a wad of stuffing, into the beak
        k = min(1.0, (t - STUFF_T) / 0.12)
        st = A.stuffing()
        img.paste(st, (int(lerp(x0 + 1, bx - 7, k)), by + 11), st)
        if t >= STUFF_T + 0.12:
            pixel.text(img, (x0 + 57, y0 + 13), "MMPH", SILK, C["white"], shadow=INK)
    label(img, (x0 + 2, y0 + 2), "BIBI (TURKEY)", SILK, bg=C["white"], fg=INK)
    age = t - W(12, "turkey")
    if age >= 0:                                                            # PARDONED, slammed across his chest
        paste(img, A.pardon_stamp(), x0 + 47, y0 + 37 - round(max(0.0, 1 - age / 0.08) * 10), "mm")


@gag("v1", 12)
def pardon(c, L):
    if c.t < PARDON_UP:
        keep_page(c, BOMB_UP)
    else:
        flip(c, PARDON_UP)
    b = c.st["bibi"]
    rise = 1 - ease_out(ramp(c.t, L.t0 - 0.12, L.t0 + 0.45))
    if rise > 0:
        b["dy"] += round(12 * rise)
    if c.t < L.t0 + 0.7:
        b.update(eyes="x", brows="worried")
        c.hit_react["bibi"] = False
    if c.t >= TURKEY_T:
        c.screens["R"] = turkey_feed
    yield "chart"
    if c.t < PARDON_UP:
        bomb_page(c.page, c.t)
    else:
        pardon_page(c.page, c.t)
    yield "front"
    draw_crate(c, c.world)
    if c.t < L.t0 + 0.7:
        dizzy_stars(c, c.world)


# --- 13: "Gobble gobble, Bibi. Stuff it. Your verdict's looking murky." -----------------------------------------

GOBBLES = (W(13, "Gobble"), W(13, "gobble", 1))
STUFF_T = W(13, "Stuff")
BALL_UP = W(13, "Your")


def eight_ball(page, t):
    """A Magic 8-Ball, shaken; the answer floats up through the murk."""
    cx, cy, r = 47, 32, 23
    shake = W(13, "looking")
    if t < BALL_UP:
        return
    k = back_out(min(1.0, (t - BALL_UP) / 0.18))
    rr = max(2, int(r * k))
    dx = round(2 * math.sin(t * 50)) if shake - 0.05 <= t < shake + 0.25 else 0
    cx += dx
    d = ImageDraw.Draw(page)
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(24, 24, 32))
    d.arc((cx - rr + 3, cy - rr + 3, cx + rr - 3, cy + rr - 3), 200, 250, fill=(120, 120, 140))
    if k < 0.98:
        return
    if t < shake:
        d.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=C["white"])
        write(page, (cx + 1, cy - 4), "8", "black", fnt=PRESS, anchor="ma")
        return
    wr = 16
    d.ellipse((cx - wr, cy - wr, cx + wr, cy + wr), fill=(18, 30, 92))
    d.polygon([(cx - 13, cy - 7), (cx + 13, cy - 7), (cx, cy + 12)], fill=(46, 78, 196))
    murk = 1 - ramp(t, W(13, "murky") - 0.05, W(13, "murky") + 0.3)
    write(page, (cx, cy - 6), "MURKY", "white", fnt=SILK, anchor="ma", bold=True)
    if murk > 0:
        m = np.zeros((page.height, page.width), np.float32)
        yy, xx = np.mgrid[0:page.height, 0:page.width]
        m[np.hypot(xx - cx, yy - cy) < wr - 1] = 0.35 + 0.65 * murk
        pixel.dither(page, m, (18, 30, 92), phase=int(t * 12) % 4)


def ball_page(page, t):
    write(page, (2, 2), "VERDICT?", "black", t - W(13, "verdict"), cps=30, bold=True)
    eight_ball(page, t)


@gag("v1", 13)
def murky(c, L):
    if c.t < BALL_UP:
        keep_page(c, PARDON_UP)
    else:
        flip(c, BALL_UP)
    if c.t < 64.72:
        c.screens["R"] = turkey_feed
    if STUFF_T <= c.t < STUFF_T + 0.5:
        pose(c, "trump", arm="chop")
    yield "chart"
    if c.t < BALL_UP:
        pardon_page(c.page, c.t)
    else:
        ball_page(c.page, c.t)
