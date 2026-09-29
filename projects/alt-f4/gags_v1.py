"""Verse 1 gags: Sam raps, Dario takes the hits (lines v1 0-11)."""
from gagkit import (CLAUDE_ORANGE, FEET_Y, GOLD, H, K, OPENAI_GREEN, PAPER, PRESS, PRESS16, RED,
                    RED_DK, TL, W, WALL_BOTTOM, WHITE, Image, ImageDraw, Prop, arrow, big_text,
                    blink, bot_img, bubble, burst, calm, char_sprite, check_mark, clamp, cutin, dither,
                    ease_out, falling_piece, fraud_guy, gag, grandma_head, impact, label, laurel, lerp,
                    lru_cache, mask, math, meter, mix, np, outline_text, paper, paste, paste_scaled,
                    pop_dy, pop_scale, radio, ramp, rnd, scaled, scroll, shelter, signal_bars, silk,
                    sparkles, spirit_level, spr, stamp, strike, tag, title, win95, wobble, wt, x_mark)
from props import bomb  # not re-exported by gagkit

CREAM = (240, 238, 230)
NAVY = (24, 34, 96)


# --- shared bits ------------------------------------------------------------------

def v1_line(idx):
    return next(ln for ln in TL.LINES if ln["sec"] == "v1" and ln["idx"] == idx)


def hit_time(L):
    for h in TL.HITS:
        if h["line"] == L.ln.get("gi"):
            return h["t"]
    return L.words[-1]["t0"] + 0.04


def head_top(c, who):
    """Centre x and hair-top y of a head in world pixels (follows knockback and bob)."""
    x0, y0, _, _ = c.head_box(who)
    return x0 + (18 if c.st[who]["facing"] == 1 else 17), y0


def shaken(age, amp=3):
    return wobble(age, amp) if age >= 0 else 0


# Nurse cap: lands on Dario in v1-3, stays on through v1-4 until the next hit knocks it off.

def draw_cap(c, t_drop, t_land):
    t = c.t
    if t < t_drop:
        return
    cap = spr("NURSE_CAP")
    cx, top = head_top(c, "dario")
    by = top + 4
    if t < t_land:
        p = ramp(t, t_drop, t_land)
        paste(c.world, cap, cx, by - 70 * (1 - p * p), "mb")
    elif t - t_land < 0.08:
        paste(c.world, cap.resize((18, 6), Image.NEAREST), cx, by, "mb")
    else:
        paste(c.world, cap, cx, by, "mb")


# Grandma cut-in (v1-2 and v1-3).

GRANNY_C = (120, 90, 160)
PANEL_W, PANEL_H = 84, 70
PANEL_L = (144, 44)        # L shot: right of Sam
PANEL_C = (10, 56)         # cR close-up: left of Dario, label clear of the karaoke tag
BUBBLE_L = (236, 84)       # speech bubble (lb anchor) beside the panel in the L shot
TAIL_L = (230, 100)


@lru_cache(maxsize=None)
def granny(mouth):
    return scaled(grandma_head(mouth), 2)


def granny_panel(c, x, y, mouth):
    x, y = int(round(x)), int(round(y))
    cutin(c.ui, x, y, PANEL_W, PANEL_H, GRANNY_C, granny(mouth))
    label(c.ui, (x + PANEL_W // 2, y + PANEL_H + 3), "GRANDMA", bg=K, fg=WHITE, anchor="ma", pad=1)


def chatter(c):
    return "open" if int(c.t * 9) % 2 == 0 else "closed"


# --- v1-0: worst-case scenario ------------------------------------------------------

@gag("v1", 0)
def worst_case(c, L):
    t = c.t
    t_you, t_out = wt(L, r"^you"), wt(L, r"^out")
    t_worst, t_scen = wt(L, r"worst"), wt(L, r"scenario")
    if L.t0 - 0.1 <= t < t_you:
        c.st["sam"]["front_arm"] = "point"
    c.shot = "R" if t >= t_out else "two"
    if t >= t_worst and calm(c, "dario"):
        c.st["dario"].update(eyes="wide", brows="worried", mouth="o", sweat=True)
    impact(c, t - t_scen, shake=4)
    yield "ui"
    if t < t_out:
        return
    hx, _, _ = c.head_ui("dario")
    if t < t_worst:
        frac = lerp(0.12, 0.35, ramp(t, t_out, t_worst))
    else:
        frac = lerp(0.35, 1.0, ease_out(ramp(t, t_worst, t_scen)))
    col = mix(GOLD, RED, ramp(frac, 0.35, 1.0))
    x = int(hx - 44) + shaken(t - t_scen)
    meter(c.ui, x, 46 + (pop_dy(t - t_out) or 0), 64, frac, col, "P(DOOM)", hot=frac > 0.995, c=c)


# --- v1-1: the doomsday voice on the radio ---------------------------------------------

RADIO_X = 282


@gag("v1", 1)
def doom_radio(c, L):
    t = c.t
    t_every, t_doom, t_radio = wt(L, r"every"), wt(L, r"doomsday"), wt(L, r"radio")
    c.shot = "wide"
    if t >= t_every:
        c.crowd = "phones"
    if t_doom <= t < t_radio + 0.25 and calm(c, "dario"):
        c.st["dario"]["mouth"] = ("open", "o", "closed", "o")[int(t * 10) % 4]
    yield "front"
    t_in = t_doom - 0.05
    if t < t_in:
        return
    age = t - t_in
    img, x, y = radio(), RADIO_X, FEET_Y + 1
    s = pop_scale(age)
    if s == 1.0 and c.ph < 0.2:
        paste(c.world, img.resize((img.width + 2, img.height - 1), Image.NEAREST), x, y, "mb")
    else:
        paste_scaled(c.world, img, x, y, s, "mb")
    if age > 0.15:
        gx, gy = x - 15 + 8, y - 22 + 13          # the speaker grill
        d = ImageDraw.Draw(c.world)
        for k in range(3):
            r = 6 + (age * 16 + k * 5) % 15
            col = mix(WHITE, (110, 100, 140), (r - 6) / 15)
            d.arc((gx - r, gy - r * 0.8, gx + r, gy + r * 0.8), 140, 220, fill=col)
    yield "ui"
    ux, uy = c.cam.ui(x, y - 22)
    tag(c.ui, ux, uy - 13, "DOOM FM", age - 0.1, bg=RED, fg=WHITE, anchor="ma")


# --- v1-2: ask your grandma -----------------------------------------------------------

@gag("v1", 2)
def grandma(c, L):
    t = c.t
    t_gran, t_say, t_first = wt(L, r"grandma"), wt(L, r"^say"), wt(L, r"first")
    c.shot = "L"
    yield "ui"
    if t < t_gran - 0.05:
        return
    p = ease_out(ramp(t, t_gran - 0.05, t_gran + 0.2))
    talking = t_say <= t < t_first + 0.2
    granny_panel(c, lerp(W + 2, PANEL_L[0], p), PANEL_L[1],
                 chatter(c) if talking else "grin" if t >= t_say else "closed")
    if t >= t_say:
        age = t - t_say
        bubble(c.ui, BUBBLE_L[0], BUBBLE_L[1] + (pop_dy(age) or 0), "CHATGPT!", tail=TAIL_L,
               anchor="lb")
        heart = spr("HEART")
        for i in range(3):
            a = age - 0.15 - i * 0.22
            if 0 <= a < 0.9:
                paste(c.ui, heart, 214 + i * 7 + math.sin(a * 9 + i) * 3, 58 - a * 34, "mm")


# --- v1-3: "Claudia? Is she a nurse?" (kill) ---------------------------------------------

@gag("v1", 3, post=0.3)
def claudia(c, L):
    t = c.t
    t_claude, t_claudia = wt(L, r"^claude"), wt(L, r"claudia")
    t_is, t_she, t_nurse = wt(L, r"^is$"), wt(L, r"^she$"), wt(L, r"nurse")
    t_next = v1_line(4)["t0"] - 0.15
    close = t >= t_she
    c.shot = "cR" if close else "L"
    if close and calm(c, "dario"):
        c.st["dario"].update(eyes="wide", brows="worried", mouth="o")
    yield "front"
    if close and t < t_next:
        draw_cap(c, t_she, t_she + 0.14)
    yield "ui"
    if close:
        px, py = PANEL_C[0] - 180 * ease_out(ramp(t, L.t1 + 0.08, L.t1 + 0.3)), PANEL_C[1]
    else:
        px, py = PANEL_L
    if t < t_claude:
        mouth = "grin"
    elif t < t_claudia:
        mouth = "o"
    elif t < t_nurse + 0.2:
        mouth = chatter(c)
    else:
        mouth = "closed"
    granny_panel(c, px, py, mouth)
    if t < t_claude:
        return
    if t < t_claudia:
        lines, t_b = ["?"], t_claude
    elif t < t_is:
        lines, t_b = ["CLAUDIA?"], t_claudia
    else:
        lines, t_b = ["IS SHE A", "NURSE?"], t_is
    dy = pop_dy(t - t_b) or 0
    if close:
        # low enough to stay clear of the kill label that lands on the punchline
        bubble(c.ui, px + PANEL_W, py + 42 + dy, lines, tail=(px + PANEL_W - 2, py + 54), anchor="lb")
    else:
        bubble(c.ui, BUBBLE_L[0], BUBBLE_L[1] + dy, lines, tail=TAIL_L, anchor="lb")


# --- v1-4: Anthropic -> MISanthropic ------------------------------------------------------

@gag("v1", 4)
def misanthropic(c, L):
    t = c.t
    t_anth, t_man, t_mis = wt(L, r"^anthropic"), wt(L, r"^man"), wt(L, r"misanthropic")
    t_hit = hit_time(L)
    c.shot = "two"
    if t_man <= t < t_mis:
        c.st["sam"]["front_arm"] = "shrug"
    impact(c, t - t_mis, shake=5)
    yield "front"
    if t < t_hit:
        draw_cap(c, -1.0, -1.0)
    else:
        cx, top = head_top(c, "dario")
        falling_piece(c.world, cx, top, t - t_hit, spin=10, g=500, vx=80, vy=-140,
                      piece=spr("NURSE_CAP"))
    yield "ui"
    t_show = t_anth + 0.12
    if t < t_show:
        return
    ax = 88 + int(round(24 * ease_out(ramp(t, t_mis, t_mis + 0.1))))
    age = t - t_mis
    title(c.ui, ax, 40, "ANTHROPIC", top=CREAM, bottom=CLAUDE_ORANGE, age=t - t_show, anchor="la")
    if age >= 0:
        dy = int(round(-24 * max(0.0, 1 - age / 0.07)))
        big_text(c.ui, (ax - 48, 40 + dy), "MIS", PRESS16, top=(255, 150, 130), bottom=RED)


# --- v1-5: scared of your own shadow ---------------------------------------------------------

SHADOW_SHOT = (190, 82, 7)
SH_X, SH_FEET, SH_S = 272, 145, 1.5
SHADOW_INK = (8, 4, 14)


@lru_cache(maxsize=None)
def shadow_mask(monster):
    """Dario's silhouette cast big on the back wall; the monster version has horns and raised arms."""
    arms = "up" if monster else "down"
    body = char_sprite("dario", -1, back_arm=arms, front_arm=arms)
    a = Image.fromarray(((np.asarray(body)[:, :, 3] > 0) * 255).astype(np.uint8), "L")
    a = a.resize((int(80 * SH_S), int(100 * SH_S)), Image.NEAREST)
    full = Image.new("L", (W, H), 0)
    ox, oy = int(round(SH_X - 40 * SH_S)), int(round(SH_FEET - 96 * SH_S))
    full.paste(a, (ox, oy))
    if monster:
        d = ImageDraw.Draw(full)
        d.polygon([(254, 53), (264, 49), (250, 34)], fill=255)
        d.polygon([(279, 49), (289, 53), (293, 34)], fill=255)
    m = np.asarray(full, np.float32) / 255.0
    m[WALL_BOTTOM + 1:] = 0
    return m


def monster_face(img, t):
    eyes = ((261, 73, 268, 76), (286, 73, 279, 76))
    glow_m = mask(lambda d: [d.ellipse((min(x0, x1) - 3, 69, max(x0, x1) + 3, 80), fill=255)
                             for x0, _, x1, _ in eyes])
    dither(img, glow_m * (0.45 + 0.15 * math.sin(t * 25)), (255, 40, 40), blend=0.5)
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in eyes:
        d.line([(x0, y0), (x1, y1)], fill=(255, 50, 40), width=2)
        d.point(((x0 + x1) // 2, (y0 + y1) // 2), fill=(255, 236, 200))
    d.polygon([(261, 85), (287, 85), (282, 92), (266, 92)], fill=(90, 8, 20))
    for i in range(7):
        x = 263 + i * 3.4
        d.polygon([(x, 85), (x + 3, 85), (x + 1.5, 88)], fill=WHITE)
        if i < 6:
            d.polygon([(x + 1.5, 92), (x + 4.5, 92), (x + 3, 89)], fill=WHITE)


@gag("v1", 5)
def own_shadow(c, L):
    t = c.t
    t_shadow, t_apoc = wt(L, r"shadow"), wt(L, r"apocalypse")
    t_your, t_only, t_topic = wt(L, r"^your", 1), wt(L, r"only"), wt(L, r"topic")
    c.shot = SHADOW_SHOT
    c.spot = ("sam", "dario")
    s = c.st["dario"]
    if t_shadow + 0.12 <= t < hit_time(L) and calm(c, "dario"):
        s.update(facing=1, eyes="wide", brows="worried", sweat=True,
                 mouth="shout" if t >= t_apoc else "o")
        if t >= t_apoc:
            s.update(back_arm="up", front_arm="up")
        s["dx"] += 1 if c.f % 2 else -1
    impact(c, t - t_apoc, shake=5)
    yield "back"
    dens = ramp(t, t_shadow - 0.02, t_shadow + 0.12) * (1 - ramp(t, t_topic - 0.2, t_topic + 0.2))
    if dens > 0:
        monster = t >= t_apoc
        dither(c.world, shadow_mask(monster) * dens, SHADOW_INK, blend=0.8)
        if monster and dens > 0.6:
            monster_face(c.world, t)
    yield "ui"
    t_card = t_your - 0.05
    if t < t_card:
        return
    x, y = 84, 46 + (pop_dy(t - t_card) or 0)
    paper(c.ui, x, y, 100, 44, title="TODAY'S TOPICS")
    d = ImageDraw.Draw(c.ui)
    for i, tt in enumerate((t_your, t_only, t_topic - 0.1)):
        if t >= tt:
            silk(d, (x + 12, y + 16 + i * 9), f"{i + 1}. APOCALYPSE", (160, 20, 36))


# --- v1-6: built a bomb, sold the shelter ---------------------------------------------------

BOMB_X, SHELTER_X = 205, 279


@gag("v1", 6)
def bomb_shelter(c, L):
    t = c.t
    t_bomb, t_shelter = wt(L, r"^bomb"), wt(L, r"shelter")
    t_list, t_mark, t_morals = wt(L, r"^that"), wt(L, r"marketing"), wt(L, r"morals")
    c.shot = "two"
    c.st["dario"]["dx"] -= 5
    impact(c, t - t_bomb, shake=5)
    impact(c, t - t_morals, shake=6)
    yield "front"
    t_drop = t_bomb - 0.22
    if t >= t_drop:
        p = ramp(t, t_drop, t_bomb)
        paste(c.world, bomb(int(t * 10) % 2), BOMB_X, lerp(10, FEET_Y + 1, p * p), "mb")
    if t >= t_shelter - 0.05:
        paste_scaled(c.world, shelter(), SHELTER_X, FEET_Y + 1, pop_scale(t - t_shelter + 0.05), "mb")
    yield "ui"
    ui = c.ui
    if t >= t_bomb:
        ux, uy = c.cam.ui(BOMB_X, FEET_Y - 22)
        tag(ui, ux, uy - 14, "AGI", t - t_bomb, bg=RED, fg=WHITE, anchor="ma")
    if t >= t_shelter:
        _, uy = c.cam.ui(SHELTER_X, FEET_Y - 26)
        tag(ui, 316, uy - 14, "$200/MO", t - t_shelter, bg=GOLD, fg=K, anchor="ra")
    if t < t_list:
        return
    x, y = 98, 40 + (pop_dy(t - t_list) or 0)
    paper(ui, x, y, 124, 40, title="SAFETY PLAN")
    d = ImageDraw.Draw(ui)
    for i, (s, tt) in enumerate((("MARKETING", t_mark), ("MORALS", t_morals))):
        by = y + 15 + i * 11
        d.rectangle((x + 8, by, x + 16, by + 8), fill=K)
        d.rectangle((x + 9, by + 1, x + 15, by + 7), fill=WHITE)
        silk(d, (x + 22, by + 1), s, K)
        if t >= tt:
            (check_mark if i == 0 else x_mark)(ui, x + 12, by + 4)


# --- v1-7: not a prophet, a pitch deck in borrowed laurels -----------------------------------

def deck_window(ui, x, y, chart_age):
    box = win95(ui, x, y, 152, 94, "pitch_deck.ppt")
    d = ImageDraw.Draw(ui)
    d.rectangle(box, fill=WHITE)
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    d.fontmode = "1"
    d.text((cx, y0 + 4), "COUNTRY OF", font=PRESS, fill=NAVY, anchor="ma")
    d.text((cx, y0 + 14), "GENIUSES*", font=PRESS, fill=NAVY, anchor="ma")
    gx0, gy0, gx1, gy1 = x0 + 10, y0 + 27, x1 - 10, y1 - 13
    d.line([(gx0, gy0), (gx0, gy1), (gx1, gy1)], fill=K)
    n = 28
    pts = []
    for i in range(int(n * ramp(chart_age, 0, 0.45)) + 1):
        u = i / n
        v = 0.08 + 0.03 * math.sin(u * 17) if u < 0.7 else 0.08 + ((u - 0.7) / 0.3) ** 2 * 0.92
        pts.append((gx0 + 2 + u * (gx1 - gx0 - 4), gy1 - 2 - v * (gy1 - gy0 - 4)))
    if len(pts) > 1:
        d.line(pts, fill=CLAUDE_ORANGE, width=2)
    silk(d, (x1 - 3, y1 - 8), "*COMING SOON", RED, anchor="ra")


@gag("v1", 7)
def pitch_deck(c, L):
    t = c.t
    t_prophet, t_youre = wt(L, r"prophet"), wt(L, r"^you.re")
    t_pitch, t_deck = wt(L, r"pitch"), wt(L, r"deck")
    t_borrowed, t_laurels = wt(L, r"borrowed"), wt(L, r"laurels")
    t_fall = t_prophet + 0.05
    c.shot = "R"
    s = c.st["dario"]
    if calm(c, "dario"):
        if t < t_fall:
            s.update(eyes="happy", brows="neutral", mouth="smirk")
        elif t < t_youre + 0.2:
            s.update(eyes="wide", brows="worried", mouth="o")
    yield "front"
    hx, top = head_top(c, "dario")
    halo = spr("HALO", 2)
    if t < t_fall:
        y = top - 8 + round(math.sin(t * 7))
        paste(c.world, halo, hx, y, "mm")
        sparkles(c.world, hx, y, t, r=16, n=4, seed=7)
    else:
        falling_piece(c.world, hx, top - 8, t - t_fall, spin=8, g=700, vx=75, vy=-60, piece=halo)
    if t >= t_borrowed:
        p = ramp(t, t_borrowed, t_borrowed + 0.2)
        laurel(c.world, hx, lerp(top - 50, top - 4, p * p), 34)
    yield "ui"
    ui = c.ui
    if t < t_pitch + 0.12:
        title(ui, 104, 44, "PROPHET", age=t - (L.t0 - 0.1))
        strike(ui, 44, 52, 166, ramp(t, t_prophet, t_prophet + 0.15))
    if t >= t_pitch - 0.08:
        p = ease_out(ramp(t, t_pitch - 0.08, t_pitch + 0.12))
        deck_window(ui, int(lerp(-170, 18, p)), 38, t - t_deck)
    if t >= t_laurels:
        lx, ly = c.cam.ui(hx + 15, top + 3)
        age = t - t_laurels
        swing = math.sin(age * 8) * 5 * max(0.25, 1 - age)
        tx, ty = lx + 10 + swing, ly + 13
        d = ImageDraw.Draw(ui)
        d.line([(lx, ly), (tx, ty)], fill=K, width=3)
        d.line([(lx, ly), (tx, ty)], fill=(236, 226, 190))
        label(ui, (tx - 3, ty), "BORROWED", bg=PAPER, fg=K)


# --- v1-8: models named after poems; the bars need help ------------------------------------

BOOKS = (("HAIKU", (52, 132, 92), 58, -4), ("SONNET", (66, 86, 170), 66, 5),
         ("OPUS", (150, 46, 66), 74, -1))


@lru_cache(maxsize=None)
def spine(name, color, w):
    h = 14
    p = Prop(w + 2, h + 2)
    d = p.d
    d.rectangle((1, 1, w, h), fill=color)
    d.line([(1, 1), (w, 1)], fill=mix(color, WHITE, 0.35))
    d.rectangle((1, h - 1, w, h), fill=mix(color, K, 0.35))
    for bx in (5, w - 5):
        d.rectangle((bx, 1, bx + 1, h), fill=(206, 150, 30))
    img = p.done()
    silk(ImageDraw.Draw(img), (w // 2 + 1, 5), name, GOLD, anchor="ma")
    return img


@gag("v1", 8)
def poem_books(c, L):
    t = c.t
    drops = (wt(L, r"models"), wt(L, r"after"), wt(L, r"poems"))
    t_bars = wt(L, r"bars")
    c.shot = "two"
    if drops[0] <= t < drops[2] + 0.4:
        c.st["sam"]["front_arm"] = "point"
    yield "ui"
    ui = c.ui
    for i, ((name, col, w, off), td) in enumerate(zip(BOOKS, drops)):
        if t < td - 0.1:
            continue
        rest = 112 - 14 * i
        y = lerp(20, rest, ramp(t, td - 0.1, td) ** 2)
        paste(ui, spine(name, col, w), 160 + off, y, "mb")
    if t >= t_bars:
        hx, top, _ = c.head_ui("dario")
        bx, by = int(hx) - 12, max(36, int(top) - 26) + (pop_dy(t - t_bars) or 0)
        signal_bars(ui, bx, by, n=1, color=RED if blink(c, 3) else (120, 30, 40))
        label(ui, (bx + 28, by + 5), "BARS", bg=K, fg=WHITE)


# --- v1-9: the haiku that can't ship itself --------------------------------------------------

@gag("v1", 9)
def haiku(c, L):
    t = c.t
    rows = (("TINY MODEL HERE", wt(L, r"haiku"), 5),
            ("SEVENTEEN SYLLABLES LONG", wt(L, r"syllables"), 7),
            ("STILL CAN'T SHIP ITSELF", wt(L, r"still"), 5))
    t_ship = wt(L, r"^ship")
    c.shot = "R"
    yield "ui"
    t0 = rows[0][1] - 0.12
    if t < t0:
        return
    x, y, w = 16, 42, 152
    scroll(c.ui, x, y, w, [s if t >= tt else "" for s, tt, _ in rows], ease_out(ramp(t, t0, t0 + 0.3)),
           title="HAIKU")
    for i, (_, tt, n) in enumerate(rows):
        if t >= tt:
            outline_text(c.ui, (x + w + 7, y + 20 + i * 9 + (pop_dy(t - tt) or 0)), str(n), PRESS, GOLD)
    if t >= t_ship:
        stamp(c.ui, x + w // 2, y + 38, "DELAYED", RED, angle=-10, big=True, age=t - t_ship)


# --- v1-10 / v1-11: the yes-bot and its hype-man era ------------------------------------------

BOT_X, GUY_X = 136, 188


@gag("v1", 10)
def yes_bot(c, L):
    t = c.t
    t_bot, t_abs, t_fraud = wt(L, r"^bot"), wt(L, r"absolutely"), wt(L, r"fraud")
    c.shot = "wide"
    impact(c, t - t_fraud, shake=5)
    yield "front"
    if t >= t_bot - 0.05:
        nod = 1 if t >= t_abs and c.ph < 0.3 else 0
        paste_scaled(c.world, bot_img("dario", 2), BOT_X, FEET_Y + 1 + nod, pop_scale(t - t_bot + 0.05), "mb")
        paste_scaled(c.world, fraud_guy(), GUY_X, FEET_Y + 1, pop_scale(t - t_bot - 0.05), "mb")
    yield "ui"
    if t_bot + 0.15 <= t < t_abs:
        bubble(c.ui, GUY_X, 66 + (pop_dy(t - t_bot - 0.15) or 0), ["I'M A", "GENIUS"], tail=(GUY_X - 2, 72))
    elif t >= t_abs:
        bubble(c.ui, BOT_X + 10, 64 + (pop_dy(t - t_abs) or 0), ["YOU'RE ABSOLUTELY", "RIGHT!"],
               tail=(BOT_X, 106))
    if t >= t_fraud:
        stamp(c.ui, GUY_X, 104, "FRAUD", RED, angle=-12, big=False, age=t - t_fraud)


@gag("v1", 11, post=0.35)
def hype_man(c, L):
    t = c.t
    t_align, t_hype = wt(L, r"alignment"), wt(L, r"hype")
    t_hit = hit_time(L)
    hype = t >= t_hype
    if c.sec == "v1":
        c.shot = "wide"
        if hype:
            c.crowd = "hype"
    yield "front"
    w = c.world
    bot = bot_img("dario", 2, shades=hype, chain=hype)
    if t < t_hit:
        bounce = -3 if hype and c.ph < 0.3 else 0
        paste(w, bot, BOT_X, FEET_Y + 1 + bounce, "mb")
        paste(w, fraud_guy(), GUY_X, FEET_Y + 1, "mb")
        if hype:
            sparkles(w, BOT_X, FEET_Y - 20, t, r=22, n=5, seed=3, big=True)
            usd = spr("DOLLAR")
            for i in range(7):
                ph = ((t - t_hype) * 0.9 + rnd("usd", i)) % 1.0
                paste(w, usd, BOT_X - 34 + rnd("usdx", i) * 68 + math.sin(t * 5 + i) * 3, 44 + ph * 92, "mm")
    else:
        age = t - t_hit
        falling_piece(w, BOT_X, FEET_Y - 16, age, spin=-11, g=420, vx=-160, vy=-230, piece=bot)
        falling_piece(w, GUY_X, FEET_Y - 36, age, spin=-7, g=420, vx=-190, vy=-190, piece=fraud_guy())
    yield "ui"
    ui = c.ui
    if t < t_hype:
        stamp(ui, GUY_X, 104, "FRAUD", RED, angle=-12, big=False)
    if t_align <= t < t_hype:
        off = 0.95 * ease_out(ramp(t, t_align + 0.1, t_align + 0.55)) + 0.04 * math.sin(t * 37)
        y = 40 + (pop_dy(t - t_align) or 0)
        ImageDraw.Draw(ui).rounded_rectangle((96, y - 4, 223, y + 19), radius=3, fill=(22, 18, 36),
                                             outline=K)
        spirit_level(ui, 100, y, 120, clamp(off, -1.0, 1.0))
    elif hype and t < t_hit:
        title(ui, 160, 38, "HYPE MAN", top=GOLD, bottom=(255, 138, 40), age=t - t_hype)
        arrow(ui, 148, 60, BOT_X + 1, 100 + (-3 if c.ph < 0.3 else 0))
