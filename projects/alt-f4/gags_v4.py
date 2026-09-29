"""Verse 4 gags: Dario raps, Sam takes the hits (lines v4 0-11)."""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import timeline as TL
from gagkit import (arc_pt, falling_piece, wobble, CLAUDE_ORANGE, FEET_Y, GOLD, GRAY_DK, K, OPENAI_GREEN, PRESS, PRESS16, PRESS24,
                    RED, RED_DK, SILK, SKIN, SKIN_SH, WHITE, W, Prop, arrow, ascii_sprite, back_out,
                    blink, book, bot_img, bubble, burst, calendar, calm, cannon, char_sprite,
                    chart_frame, dither, ease_out, gag, hugging_face, impact, keycap, label, lerp,
                    loot_bag, mask, meter, mix, outline_text, paste, paste_rot, paste_scaled,
                    pencil_scribble, police_tape, pop_dy, pop_scale, ramp, rnd, scaled, silk, smoke,
                    sparkles, spr, stamp, strike, tag, text_width, title, typed, wt)

SEC = "v4"

NOTE = ascii_sprite([
    "...kkkk",
    "...kwwk",
    "...kwkk",
    "...kwk.",
    ".kkkwk.",
    "kwwwwk.",
    "kwwwwk.",
    ".kkkk..",
])
LEAF = ascii_sprite([
    "..kk.",
    ".kllk",
    "kllk.",
    ".kk..",
])
OPEN_HAND = ascii_sprite([   # a raised open palm (HAND_UP's lone finger reads as a rude one)
    ".......kk.......",
    "....kkksskkk....",
    "...kssksskssk...",
    "...ksskssksskkk.",
    "...ksskssksskssk",
    "...ksskssksskssk",
    "...ksskssksskssk",
    "...ksskssksskssk",
    "...kssSssSssSssk",
    ".kkkssssssssssSk",
    "ksskssssssssssSk",
    ".kssssssssssssSk",
    "..ksssssssssssSk",
    "..ksssssssssssSk",
    "...ksssssssssSk.",
    "....kssssssSk...",
    "...kbbbbbbbBk...",
    "...kbbbbbbbBk...",
    "...kbbbbbbbBk...",
    "...kkkkkkkkkk...",
])


def line_end(idx):
    """When line `idx`'s gag window closes (before any `post`)."""
    ls = TL.lines_of(SEC)
    return ls[idx + 1]["t0"] - 0.12 if idx + 1 < len(ls) else TL.section_bounds(SEC)[1]


def big_hit_t(L):
    """When this line's big (kill-cam) hit lands, or None."""
    return next((h["t"] for h in TL.HITS if h["line"] == L.ln["gi"] and h["big"]), None)


def cam_free_at(L):
    """When the kill-cam snap from a big hit just before line L lets go (L.t0 if none)."""
    h = TL.last_hit(L.t0, window=0.7)
    return h["t"] + 0.7 if h and h["big"] and h["attacker"] != "both" else L.t0


def sam_face(c, **kw):
    if calm(c, "sam"):
        c.st["sam"].update(kw)


def whistle(ui, x, y, t, t0):
    """Innocent whistling: notes drifting up and away from (x, y)."""
    for i in range(3):
        a = t - t0 - i * 0.22
        if a < 0:
            continue
        a %= 0.66
        paste(ui, NOTE, x + a * 16 + i * 2, y - a * 26, "mb")


@lru_cache(maxsize=16)
def _stamp_lines_img(lines, color, angle):
    lh, pad = 18, 5
    w = max(text_width(s_, PRESS16) for s_ in lines) + 2 * pad + 4
    h = len(lines) * lh + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w - 1, h - 1), outline=color + (255,), width=2)
    for i, s_ in enumerate(lines):
        d.text((w // 2 + 1, pad + 2 + i * lh), s_, font=PRESS16, fill=color + (255,), anchor="ma")
    arr = np.array(im)
    holes = np.array([[rnd("ink", len(lines), x, y) < 0.12 for x in range(w)] for y in range(h)])
    arr[holes, 3] = 0
    return Image.fromarray(arr, "RGBA").rotate(angle, resample=Image.NEAREST, expand=True)


def stamp_lines(img, cx, cy, lines, color=RED, angle=8, age=1.0):
    """Like props.stamp, but stacks several lines of text inside one frame."""
    if age < 0:
        return
    im = _stamp_lines_img(tuple(lines), color, angle)
    paste(img, im, cx, cy + int(round(max(0.0, 1 - age / 0.1) * -14)), "mm")


def dust(img, x, y, age, n=6, seed=0, spread=22):
    if not 0 <= age < 0.45:
        return
    d = ImageDraw.Draw(img)
    for i in range(n):
        side = -1 if i % 2 == 0 else 1
        dx = side * (5 + age * spread * (0.6 + rnd("dust", seed, i)))
        r = max(1.0, 4.5 - age * 8)
        cy = y - 2 - age * 14 * rnd("dusty", seed, i)
        d.ellipse((x + dx - r - 1, cy - r - 1, x + dx + r + 1, cy + r + 1), fill=K)
        d.ellipse((x + dx - r, cy - r, x + dx + r, cy + r), fill=(214, 204, 196))


# --- 0: the agents rob Hugging Face ------------------------------------------

@gag(SEC, 0, pre=0.09)
def answer_key_heist(c, L):
    t = c.t
    c.shot = "two"
    t_ag, t_hug = wt(L, "agents"), wt(L, "Hugging")
    t_steal, t_ans = wt(L, "steal"), wt(L, "answer")
    grab = t_steal + 0.1
    hf_x, bag_x = 196, 170
    if t < t_steal:
        bx = lerp(-12, 142, ease_out(ramp(t, t_ag - 0.1, t_hug + 0.25)))
    elif t < grab:
        bx = lerp(142, bag_x - 12, ramp(t, t_steal, grab))
    else:
        bx = lerp(bag_x - 12, -30, ramp(t, grab + 0.06, grab + 0.66))
    flee = t >= grab
    if t >= t_steal:
        sam_face(c, eyes="happy", mouth="o", brows="raised")
    yield "back"
    w = c.world
    if t >= t_hug:
        s = min(1.0, pop_scale(t - t_hug))
        paste_scaled(w, hugging_face(robbed=flee), hf_x, FEET_Y + 1, s, "mb")
        if not flee:
            paste_scaled(w, loot_bag(), bag_x, FEET_Y + 2, s, "mb")
    yield "front"
    step = int(t * 12) % 2
    b = bot_img("sam", 2, mask_=True, flip=flee)
    fy = FEET_Y + 1 - (2 if flee and step else step)
    paste(w, b, bx, fy, "mb")
    if flee:
        paste(w, loot_bag(), bx + 1, fy - b.height + 6, "mb")
    yield "ui"
    ui = c.ui
    if t >= t_hug:
        ux, uy = c.cam.ui(hf_x, FEET_Y - 34)
        if not flee:
            tag(ui, ux - 7, uy - 13, "HUGGING FACE", age=t - t_hug, bg=GOLD, anchor="ma")  # clear of Dario's glasses
        else:
            bubble(ui, ux + 6, uy - 4, "HEY!", tail=(ux - 2, uy + 10))
    if flee:
        ux, uy = c.cam.ui(bx + 1, fy - b.height - 20)
        if ux > 20:
            tag(ui, ux, uy - 11, "ANSWER KEY", age=t - grab, bg=(150, 120, 80), fg=GOLD, anchor="ma")
    if t >= t_steal and not c.st["sam"]["hidden"]:
        mx, my = c.cam.ui(90, 99)
        whistle(ui, mx, my, t, t_steal)


# --- 1: AGI? No: cheating on the SAT -------------------------------------------

@lru_cache(maxsize=8)
def answer_sheet(filled):
    rows, w = 6, 64
    h = 12 + rows * 7
    img = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w + 1, h + 1), fill=K)
    d.rectangle((1, 1, w, h), fill=(236, 244, 236))
    silk(d, (w // 2 + 2, 3), "SAT ANSWERS", (40, 90, 60), anchor="ma")
    for r in range(rows):
        silk(d, (4, 12 + r * 7), str(r + 1), (40, 90, 60))
        pick = int(rnd("sat", r) * 5)
        for col in range(5):
            cx, cy = 15 + col * 10, 14 + r * 7
            d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), outline=(40, 90, 60),
                      fill=(20, 20, 30) if (col == pick and r < filled) else None)
    return img


@gag(SEC, 1, pre=0.12)
def cheating_on_the_sat(c, L):
    t = c.t
    c.shot = "two"
    t_gen, t_that = wt(L, "general"), wt(L, "that's")
    t_cheat, t_sat = wt(L, "cheating"), wt(L, "SAT")
    if t >= t_cheat:
        sam_face(c, eyes="squint", brows="worried", mouth="smirk", sweat=True)
    yield "ui"
    ui = c.ui
    if t >= t_gen:
        title(ui, 160, 36, "AGI?", PRESS24, top=WHITE, bottom=(170, 200, 255), age=t - t_gen)
        tw = text_width("AGI?", PRESS24)
        if t >= t_that:
            strike(ui, 160 - tw // 2 - 8, 48, 160 + tw // 2 + 8, ramp(t, t_that, t_that + 0.12), width=3)
    if t >= t_cheat:
        age = t - t_cheat
        sc = 1.25
        sw, sh = int(66 * sc), int(56 * sc)
        x0, y0 = 160 - sw // 2, 70 + (pop_dy(age) or 0)
        peek = ease_out(ramp(t, t_cheat + 0.1, t_cheat + 0.35))
        if peek > 0.05:
            b = bot_img("sam", 2, mask_=True)
            paste(ui, b, lerp(150, x0 + sw + 4, peek), 144 - int(3 * peek), "mb")
        filled = min(6, int(ramp(t, t_cheat + 0.08, t_sat - 0.08) * 6.99))
        paste_scaled(ui, answer_sheet(filled), x0, y0, sc, "lt")
        if filled < 6 and t < t_sat:
            r = filled
            pick = int(rnd("sat", r) * 5)
            px = x0 + (15 + pick * 10) * sc
            py = y0 + (14 + r * 7) * sc
            paste(ui, spr("PEN", 2), px - 2, py - 19)
    if t >= t_sat:
        stamp(ui, 160, 104, "CHEATER", RED, angle=-12, big=True, age=t - t_sat)
        impact(c, t - t_sat, shake=4)


# --- 2 (kill): the chart crime ---------------------------------------------------

@gag(SEC, 2, pre=0.12, post=0.3)
def chart_crime(c, L):
    t = c.t
    c.shot = "L"
    t_chart, t_crime = wt(L, "chart"), wt(L, "crime")
    t_52, t_over, t_69 = wt(L, "Fifty"), wt(L, "over"), wt(L, "sixty")
    if t >= t_crime:
        sam_face(c, eyes="wide", brows="worried", mouth="grin", sweat=True)
    yield "ui"
    if t < t_chart:
        return
    ui = c.ui
    d = ImageDraw.Draw(ui)
    x, y, w, h = 196, 40, 112, 96
    y += pop_dy(t - t_chart) or 0
    chart_frame(ui, x, y, w, h)
    silk(d, (x + w // 2 + 4, y + 3), "BENCHMARK %", GRAY_DK, anchor="ma")
    base = y + h - 8
    grow = ease_out(ramp(t, t_crime, t_crime + 0.35))
    bars = ((x + 22, 64, OPENAI_GREEN, "52.8", "GPT-5", t_52),
            (x + 66, 20, (184, 184, 198), "69.1", "o3", t_69))
    for bx, bh, col, val, name, tv in bars:
        silk(d, (bx + 14, base + 2), name, K, anchor="ma")
        if t < t_crime:
            continue
        top = base - max(1, int(bh * grow))
        d.rectangle((bx - 1, top - 1, bx + 28, base), fill=K)
        d.rectangle((bx, top, bx + 27, base - 1), fill=col)
        d.line([(bx, top), (bx + 27, top)], fill=mix(col, WHITE, 0.5))
        d.line([(bx + 27, top), (bx + 27, base - 1)], fill=mix(col, K, 0.3))
        hot = t >= tv
        fg = RED if hot and blink(c, 5) else K
        outline_text(ui, (bx + 14, top - 11), val, PRESS, fg, outline=(250, 248, 240), anchor="ma")
    if t_over <= t < t_69 + 0.25:
        # "drawn over": the short bar should be the tall one
        arrow(ui, x + 94, base - 20, x + 94, base - 64, color=RED, width=2, head=5)
    if t >= t_69:
        police_tape(ui, x - 10, y + 16, x + w + 10, y + h - 30, "CHART CRIME",
                    phase=int((t - t_69) * 30) % 60)


# --- 3 (kill): bars that look bigger than they are -------------------------------

def magnifier(ui, cx, cy, r=11):
    d = ImageDraw.Draw(ui)
    hx0, hy0 = cx + r * 0.7, cy + r * 0.7
    d.line([(hx0, hy0), (hx0 + 11, hy0 + 11)], fill=K, width=6)
    d.line([(hx0 + 1, hy0 + 1), (hx0 + 10, hy0 + 10)], fill=(140, 84, 44), width=3)
    glass = mask(lambda dd: dd.ellipse((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), fill=255))
    dither(ui, glass * 0.22, (200, 236, 255))
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), outline=K, width=4)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(210, 214, 226), width=2)
    d.arc((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), 200, 250, fill=WHITE)


def dashed_box(ui, box, color, dash=3):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(ui)
    for x in range(x0, x1, dash * 2):
        for yy in (y0, y1):
            d.line([(x, yy), (min(x + dash - 1, x1), yy)], fill=color)
    for y in range(y0, y1, dash * 2):
        for xx in (x0, x1):
            d.line([(xx, y), (xx, min(y + dash - 1, y1))], fill=color)


@gag(SEC, 3, pre=0.12, post=0.1)
def inflated_bars(c, L):
    t = c.t
    c.shot = "L"
    t_bars, t_are = wt(L, "bars"), wt(L, r"^are")
    t_sam, t_design = wt(L, r"^Sam"), wt(L, "design")
    pop_t = t_design - 0.05
    if t < t_bars:
        s = 1.0
    elif t < pop_t:
        s = 1.0 + 0.45 * back_out(ramp(t, t_bars, t_bars + 0.3)) + 0.025 * math.sin((t - t_bars) * 14)
    else:
        s = lerp(1.45, 1.0, ease_out(ramp(t, pop_t, pop_t + 0.1)))
    c.hud["bar_scale"]["sam"] = s
    right = 37 + 104 * s
    c.hud["bar_scale"]["dario"] = min(1.0, (W - 37 - right - 6) / 104)
    if t_bars <= t < t_are:
        sam_face(c, mouth="grin", brows="smug")
    elif t >= t_are:
        sam_face(c, eyes="wide", brows="worried", mouth="o", sweat=True)
    yield "ui"
    ui = c.ui
    if t_bars <= t < pop_t:
        age = t - t_bars
        mx = lerp(70, 37 + 104 * s - 26, ease_out(ramp(t, t_bars + 0.1, t_bars + 0.6)))
        magnifier(ui, mx, 11 + (pop_dy(age) or 0))
    if t_sam <= t < pop_t:
        col = RED if blink(c, 4) else WHITE
        dashed_box(ui, (35, 4, 142, 15), col)
        tag(ui, 70, 37, "ACTUAL SIZE", age=t - t_sam, bg=RED, fg=WHITE)
        arrow(ui, 104, 36, 104, 19, color=RED, width=2, head=4)
    if pop_t <= t < pop_t + 0.35:
        age = t - pop_t
        bx = 37 + 104 + 4
        burst(ui, bx, 10, 3 + age * 20, 8 + age * 34, WHITE, spikes=10, rot=age * 3)
        if age < 0.25:
            outline_text(ui, (bx + 12, 20 - int(age * 20)), "PSSSHH", SILK, WHITE)


# --- 4: feel the AGI / felt your lies --------------------------------------------

def pinocchio(img, a, n):
    """A nose `n` px long growing out of Sam's face (world space, facing right)."""
    x0, y0 = a["hx"] + 19, a["hy"] + 24
    x1 = x0 + int(n)
    d = ImageDraw.Draw(img)
    d.rectangle((x0 + 2, y0 - 1, x1 + 1, y0 + 3), fill=K)
    d.ellipse((x1 - 1, y0 - 1, x1 + 3, y0 + 3), fill=K)
    d.rectangle((x0, y0, x1, y0 + 2), fill=SKIN)
    d.ellipse((x1, y0, x1 + 2, y0 + 2), fill=SKIN)
    d.line([(x0 + 1, y0 + 2), (x1, y0 + 2)], fill=SKIN_SH)
    if n > 14:
        img.paste(LEAF, (int(x0 + n * 0.6), y0 - 4), LEAF)


@gag(SEC, 4, pre=0.12, post=0.45)
def feel_the_agi(c, L):
    t = c.t
    c.shot = "two"
    t_feel, t_agi = wt(L, "feel"), wt(L, "AGI")
    t_the = wt(L, r"^the$")
    t_he, t_felt, t_your, t_lies = wt(L, r"^he$"), wt(L, "felt"), wt(L, "your"), wt(L, "lies")
    end = line_end(4)
    if t_feel <= t < t_he:
        sam_face(c, eyes="happy", mouth="grin")
    elif t >= t_lies:
        sam_face(c, eyes="wide", brows="worried", mouth="o", sweat=True)
    nose = 26 * ease_out(ramp(t, t_your - 0.05, t_lies + 0.3)) * (1 - ramp(t, end + 0.3, end + 0.45))
    yield "front"
    if nose >= 1 and "sam" in c.anchor and not c.st["sam"]["rot"]:
        pinocchio(c.world, c.anchor["sam"], nose)
    yield "ui"
    if not t_feel <= t < end:
        return
    ui = c.ui
    cracks = (t_he, t_felt, t_your)
    for i, (hx, t_in) in enumerate(zip((116, 160, 204), (t_feel, t_the, t_agi))):
        if t < t_in:
            continue
        cracked = t >= cracks[i]
        base = 3.0 + (0.4 if c.ph < 0.18 and not cracked else 0.0)
        sc = base * min(1.0, pop_scale(t - t_in))
        dy = 0 if cracked else math.sin(t * 5 + i) * 2
        if cracked and t < cracks[i] + 0.2:
            dy += math.sin((t - cracks[i]) * 60) * 2
        img = spr("HEART_CRACK") if cracked else spr("HEART")
        paste_scaled(ui, img, hx, 88 + dy, sc, "mm")
    if t < t_lies:
        title(ui, 160, 40, "FEEL THE AGI", PRESS16, top=(255, 200, 225), bottom=(255, 96, 170),
              age=t - t_feel)
    else:
        title(ui, 160, 36, "LIES!", PRESS24, top=(255, 110, 110), bottom=(200, 20, 40), age=t - t_lies)
        impact(c, t - t_lies, shake=5)


# --- 5: seventy pages, a novel not a vibe ------------------------------------------

@lru_cache(maxsize=None)
def memo_book():
    img = book("70 PAGES", w=46, h=30, color=(64, 72, 156), pages=8)
    silk(ImageDraw.Draw(img), (25, 19), "RE: SAM", WHITE, anchor="ma")
    return img


@gag(SEC, 5, pre=0.12)
def seventy_pages(c, L):
    t = c.t
    c.shot = (112, 74, 9)
    t_70, t_you = wt(L, "seventy"), wt(L, r"^you$")
    t_novel, t_not = wt(L, "novel"), wt(L, r"^not")
    land = t_novel
    lift = land - 0.26
    if t >= land:
        c.st["sam"].update(eyes="x", brows="worried", mouth="o")
        if t < land + 0.1:
            c.st["sam"]["dy"] += 2
        impact(c, t - land, shake=9)
    elif t >= t_70:
        sam_face(c, eyes="wide", brows="worried", mouth="closed")
    yield "front"
    if t < t_70:
        return
    w = c.world
    img = memo_book()
    if t < lift:
        s = min(1.0, pop_scale(t - t_70, dur=0.2))
        cx, cy = 166, 80 + math.sin(t * 6) * 2
        paste_scaled(w, img, cx, cy, s, "mm")
        sparkles(w, cx, cy, t, r=34, n=4, seed=5)
    else:
        s = c.st["sam"]
        hx = s["x"] + s["dx"] + 1
        top = c.anchor["sam"]["hy"] + 4 if "sam" in c.anchor else FEET_Y - 64
        if t < land:
            p = ramp(t, lift, land) ** 2
            bx, by = lerp(166, hx, p), lerp(80 + img.height / 2, top, p) - 12 * math.sin(math.pi * p)
            paste_rot(w, img, bx, by - img.height / 2, -40 * p)
        else:
            rot = 8 + (math.sin((t - land) * 40) * 6 * max(0.0, 1 - (t - land) / 0.3))
            r_img = img.rotate(rot, resample=Image.NEAREST, expand=True)
            paste(w, r_img, hx, top + 3, "mb")
    yield "ui"
    ui = c.ui
    if t >= land:
        age = t - land
        if age < 0.8 or blink(c, 6):
            title(ui, 222, 44, "THUD!", PRESS16, top=WHITE, bottom=(200, 200, 220), age=age)
        tag(ui, 222, 70, "A NOVEL", age=age - 0.05, bg=GOLD, fg=K, anchor="ma")
    if t >= t_not:
        stamp_lines(ui, 240, 112, ("NOT A", "VIBE"), RED, angle=8, age=t - t_not)
        impact(c, t - t_not, shake=4)


# --- 6: your founding member is on my payroll -----------------------------------------

@lru_cache(maxsize=None)
def check_img():
    w, h = 124, 64
    img = Image.new("RGBA", (w, h), K + (255,))
    dd = ImageDraw.Draw(img)
    dd.rectangle((1, 1, w - 2, h - 2), fill=(214, 236, 214))
    dd.rectangle((3, 3, w - 4, h - 4), outline=(150, 194, 156))
    for x in range(8, w - 8, 8):
        dd.point([(x, 17), (x + 4, 18), (x, 37), (x + 4, 38)], fill=(186, 220, 190))
    silk(dd, (7, 7), "ANTHROPIC PBC", (40, 80, 50))
    dd.rectangle((w - 40, 5, w - 7, 15), fill=WHITE, outline=K)
    silk(dd, (w - 23, 7), "$$$$$", (30, 120, 60), anchor="ma")
    silk(dd, (7, 23), "PAY TO:", K)
    dd.line([(47, 31), (w - 7, 31)], fill=K)
    silk(dd, (7, 46), "X", (120, 150, 124))     # sign here
    dd.line([(7, 51), (58, 51)], fill=K)
    return img


@gag(SEC, 6, pre=0.12)
def payroll(c, L):
    t = c.t
    c.shot = "two"
    t_found, t_my = wt(L, "founding"), wt(L, r"^my$")
    t_pay, t_now = wt(L, "payroll"), wt(L, r"^now")
    t_k, t_mine = wt(L, "Karpathy"), wt(L, "mine")
    if t >= t_pay:
        c.st["dario"]["front_arm"] = "point" if t < t_mine else "pump"
    if t >= t_k:
        sam_face(c, eyes="wide", brows="worried", mouth="o")
    yield "ui"
    ui = c.ui
    if t >= t_found:
        team = t >= t_my
        tag(ui, 160, 38, "FOUNDING MEMBER", age=t - t_found,
            bg=CLAUDE_ORANGE if team else OPENAI_GREEN, fg=WHITE, anchor="ma")
        if team and t < t_my + 0.3:
            sparkles(ui, 160, 42, t, r=40, n=5, seed=6, big=True)
    if t < t_pay:
        return
    p = ease_out(ramp(t, t_pay - 0.05, t_pay + 0.2))
    x = int(lerp(W + 10, 94, p))
    y = 54 + wobble(t - t_pay - 0.2, amp=2, freq=30, decay=0.3)
    paste(ui, check_img(), x, y)
    name = typed("KARPATHY", t - t_k, cps=20)
    if name:
        outline_text(ui, (x + 50, y + 21), name, PRESS, (30, 30, 110), outline=(214, 236, 214))
    if t >= t_now:
        pencil_scribble(ui, x + 15, y + 47, 42, ramp(t, t_now, t_now + 0.3), color=(30, 30, 110))
    if t >= t_mine:
        # Slammed over the check's lower-right corner, clear of the payee's name.
        stamp(ui, x + 86, y + 62, "MINE", RED, angle=8, big=True, age=t - t_mine)
        impact(c, t - t_mine, shake=5)


# --- 7 (kill): lowercase Sam, the upper hand -------------------------------------------

@gag(SEC, 7, pre=0.12, post=0.45)
def upper_hand(c, L):
    t = c.t
    c.shot = "two"
    t_low, t_i = wt(L, "lowercase"), wt(L, r"^I$")
    t_up, t_hand = wt(L, "upper"), wt(L, "hand")
    end = line_end(7)
    t_hit = big_hit_t(L) or end
    back = ease_out(ramp(t, end + 0.05, end + 0.4))
    shrink = back_out(ramp(t, t_low, t_low + 0.25))
    c.hud["name_scale"]["sam"] = lerp(lerp(1.0, 0.75, shrink), 1.0, back)   # smallest still legible
    grow = back_out(ramp(t, t_up, t_up + 0.2))
    c.hud["name_scale"]["dario"] = lerp(lerp(1.0, 2.0, grow), 1.0, back)
    if t_up <= t < end:
        c.st["dario"]["front_arm"] = "up"
    if t_low <= t < t_up:
        sam_face(c, mouth="smirk", brows="worried")
    elif t_up <= t < end:
        sam_face(c, eyes="wide", mouth="o", brows="worried")
    yield "ui"
    if t >= end:
        return
    ui = c.ui
    if t_low <= t < t_up:
        arrow(ui, 46, 41, 46, 30, color=(190, 255, 220), width=2, head=4)
        tag(ui, 30, 43, "lowercase", age=t - t_low, bg=(24, 40, 44), fg=(190, 255, 220), fnt=PRESS)
    if t_i <= t < t_hit:
        pressed = 2 if t >= t_up else 0
        kx, ky = 92, 66 + (pop_dy(t - t_i) or 0)
        keycap(ui, kx, ky, "CAPS LOCK", pressed=pressed, led=t >= t_up)
        if t_up <= t < t_up + 0.25:
            burst(ui, kx + 43, ky + 12, 10 + (t - t_up) * 50, 20 + (t - t_up) * 80, GOLD, spikes=12)
            keycap(ui, kx, ky, "CAPS LOCK", pressed=pressed, led=True)
    if t >= t_hand:
        rise = back_out(ramp(t, t_hand, t_hand + 0.25))
        hand = scaled(OPEN_HAND, 3)
        hy = lerp(150, 52, rise) + math.sin(t * 8) * 1.5
        paste(ui, hand, 204, hy, "mt")
        sparkles(ui, 204, hy + 20, t, r=30, n=5, seed=7, big=True)
        if rise > 0.9:
            tag(ui, 204, hy + 62, "UPPER HAND", age=t - t_hand - 0.2, bg=CLAUDE_ORANGE, fg=WHITE,
                anchor="ma")


# --- 8: families in court, engagement ------------------------------------------------

@lru_cache(maxsize=None)
def gavel_img():
    p = Prop(70, 70)
    d = p.d
    d.rectangle((33, 14, 36, 35), fill=(176, 116, 64))
    d.rounded_rectangle((23, 3, 45, 14), radius=2, fill=(140, 84, 44))
    d.rectangle((28, 3, 29, 14), fill=GOLD)
    d.rectangle((39, 3, 40, 14), fill=GOLD)
    return p.done()


def gavel_angle(t, bangs, up=24.0, down=-84.0, swing=0.09):
    """Raised until the first bang; between bangs it lifts again; after the last it rests."""
    if t < bangs[0] - swing:
        return up
    for i, tb in enumerate(bangs):
        if t < tb:
            return lerp(up, down, ramp(t, tb - swing, tb))
        nxt = bangs[i + 1] - swing if i + 1 < len(bangs) else None
        if nxt is None:
            return down + 6 * max(0.0, 1 - (t - tb) / 0.12)
        if t < nxt:
            return lerp(down, up, ease_out(ramp(t, tb + 0.03, nxt)))
    return down


@gag(SEC, 8, pre=0.12)
def order_in_court(c, L):
    t = c.t
    c.shot = "two"
    t_court, t_say = wt(L, "court"), wt(L, "say")
    t_you, t_eng = wt(L, r"^you$"), wt(L, "engagement")
    if t >= t_court:
        sam_face(c, eyes="wide", brows="worried", mouth="frown", sweat=True)
    if t >= t_you:
        c.st["dario"]["front_arm"] = "point"
    # The gavel lives in two-shot screen space, so it waits out line 7's kill-cam.
    t_in = max(t_court - 0.3, cam_free_at(L))
    bangs = (max(t_court, t_in + 0.14), t_say)
    yield "ui"
    if t < t_in:
        return
    ui = c.ui
    d = ImageDraw.Draw(ui)
    px, py = 128, 96
    app = ease_out(ramp(t, t_in, t_in + 0.12))
    ox = int((1 - app) * -60)
    # sound block under where the gavel head lands
    bx, by = px + 26 + ox, py + 10
    d.rectangle((bx - 13, by - 1, bx + 13, by + 7), fill=K)
    d.rectangle((bx - 12, by, bx + 12, by + 6), fill=(130, 78, 40))
    d.line([(bx - 12, by), (bx + 12, by)], fill=(176, 116, 64))
    ang = gavel_angle(t, bangs)
    g = gavel_img().rotate(ang, resample=Image.NEAREST, center=(35, 35))
    paste(ui, g, px - 35 + ox, py - 35)
    for tb in bangs:
        if 0 <= t - tb < 0.2:
            burst(ui, bx, by - 2, 4 + (t - tb) * 30, 10 + (t - tb) * 50, WHITE, spikes=8, rot=tb)
            impact(c, t - tb, shake=5)
    if t_say <= t < t_eng:   # not before: line 7's UPPERCUT! label holds the top-left until then
        title(ui, 160, 40, "ORDER!", PRESS16, top=WHITE, bottom=(236, 200, 160), age=t - t_say)
    if t >= t_eng:
        frac = lerp(0.3, 1.0, ease_out(ramp(t, t_eng, t_eng + 0.6)))
        meter(ui, 104, 124, 92, frac, OPENAI_GREEN, "ENGAGEMENT", hot=frac > 0.97, c=c)


# --- 9: not a bug, it's the business model -------------------------------------------------

@lru_cache(maxsize=None)
def bug_sign(back=False):
    w, h = 144, 58
    img = Image.new("RGBA", (w, h + 22), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.rectangle((w // 2 - 4, h - 2, w // 2 + 4, h + 21), fill=K)
    d.rectangle((w // 2 - 3, h - 2, w // 2 + 3, h + 20), fill=(150, 104, 60))
    board, ink = ((40, 140, 84), WHITE) if back else ((250, 246, 236), K)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=4, fill=K)
    d.rounded_rectangle((2, 2, w - 3, h - 3), radius=3, fill=board)
    if back:
        outline_text(img, (w // 2, 5), "IT'S THE", PRESS, GOLD, anchor="ma")
        outline_text(img, (w // 2 + 1, 18), "BUSINESS", PRESS16, WHITE, anchor="ma")
        outline_text(img, (w // 2 + 1, 37), "MODEL", PRESS16, WHITE, anchor="ma")
        dollar = spr("DOLLAR", 2)
        img.paste(dollar, (8, 36), dollar)
        img.paste(dollar, (w - 20, 36), dollar)
    else:
        d.text((w // 2 + 1, 9), "IT'S NOT", font=PRESS16, fill=ink, anchor="ma")
        d.text((w // 2 + 1, 31), "A BUG", font=PRESS16, fill=ink, anchor="ma")
        bug = scaled(spr("BUG0"), 2)
        img.paste(bug, (w - 26, 32), bug)
    return img


@gag(SEC, 9, pre=0.12)
def business_model(c, L):
    t = c.t
    c.shot = "L"
    t_bug, t_that = wt(L, r"^bug"), wt(L, "that's")
    t_bus = wt(L, "business")
    flip0, flip1 = t_bus - 0.12, t_bus + 0.12
    if t_bug <= t < t_bus:
        sam_face(c, eyes="wide", brows="worried", mouth="o", sweat=True)
    elif t >= t_bus:
        sam_face(c, mouth="grin", brows="raised")
    yield "front"
    if t >= t_bug and "sam" in c.anchor:
        a = c.anchor["sam"]
        hcx, top = a["hx"] + 16, a["hy"]
        p = ease_out(ramp(t, t_bug, t_bug + 1.0))
        chx, chy = a["chest"]
        path = [(chx - 6, chy + 14), (chx - 9, chy - 6), (a["hx"] + 2, top + 16), (hcx, top + 1)]
        seg = min(2, int(p * 3))
        u = p * 3 - seg
        x = lerp(path[seg][0], path[seg + 1][0], u)
        y = lerp(path[seg][1], path[seg + 1][1], u)
        if p >= 1:
            x = hcx + math.sin(t * 3) * 7
        if t < t_bus:
            bug = spr("BUG1" if int(t * 10) % 2 else "BUG0")
            if p < 1 and seg < 2:
                bug = bug.rotate(90, expand=True)
            paste(c.world, bug, x, y, "mb")
        else:
            coin = spr("DOLLAR")
            paste(c.world, coin, x, top + 1 - int(abs(math.sin((t - t_bus) * 10)) * 3), "mb")
            if t < t_bus + 0.2:
                age = t - t_bus
                burst(c.world, x, top - 3, 1 + age * 10, 3 + age * 24, WHITE, spikes=8)
            sparkles(c.world, x, top - 4, t, r=9, n=3, seed=91)
    yield "ui"
    if t < t_bug:
        return
    ui = c.ui
    if flip0 <= t < flip1:
        q = ramp(t, flip0, flip1)
        img = bug_sign(back=q >= 0.5)
        sx = max(0.06, abs(math.cos(math.pi * q)))
        img = img.resize((max(1, int(img.width * sx)), img.height), Image.NEAREST)
    else:
        img = bug_sign(back=t >= flip1)
    wob = int(math.sin((t - t_that) * 25) * 2 * max(0.0, 1 - (t - t_that) / 0.4)) if t >= t_that else 0
    y0 = 42 + (pop_dy(t - t_bug) or 0)
    paste(ui, img, 232 + wob, y0, "mt")
    if t >= flip1:
        sparkles(ui, 232, y0 + 28, t, r=70, n=6, seed=9, big=True)


# --- 10: my lines don't bend ----------------------------------------------------------

def line_path(x0, x1, y, amp, sag, t, wob):
    pts = []
    n = int(x1 - x0)
    for i in range(0, n + 1, 2):
        u = i / max(1, n)
        yy = y + math.sin(u * 9 + t * wob) * amp + math.sin(math.pi * u) * sag
        pts.append((x0 + i, yy))
    return pts


@gag(SEC, 10, pre=0.12)
def lines_dont_bend(c, L):
    t = c.t
    c.shot = "two"
    t_auth, t_at = wt(L, "authoritarian"), wt(L, r"^At$")
    t_lines, t_dont, t_bend = wt(L, "lines"), wt(L, "don't"), wt(L, "bend")
    if t_auth - 0.1 <= t < t_at:
        c.st["dario"]["front_arm"] = "shrug"
        c.st["dario"]["brows"] = "raised"
    elif t >= t_lines:
        c.st["dario"]["front_arm"] = "point"
    if t >= t_dont:
        sam_face(c, eyes="squint", brows="worried", mouth="frown")
    yield "ui"
    ui = c.ui
    d = ImageDraw.Draw(ui)
    if t_auth <= t < t_at + 0.1:
        title(ui, 160, 42, "AUTHORITARIAN?", PRESS16, top=WHITE, bottom=(255, 170, 120), age=t - t_auth)
    if t >= t_lines:
        p = ease_out(ramp(t, t_lines, t_lines + 0.15))
        x0, x1, y = 216, 292, 50
        xe = lerp(x0, x1, p)
        for xx in range(x0, int(xe) + 1, 6):
            d.line([(xx, y + 4), (xx, y + (8 if (xx - x0) % 12 == 0 else 6))], fill=GOLD)
        d.line([(x0, y), (xe, y)], fill=K, width=5)
        d.line([(x0, y), (xe, y)], fill=RED, width=3)
        d.line([(x0, y - 1), (xe, y - 1)], fill=(255, 160, 160))
        tag(ui, 254, 36, "MY LINE", age=t - t_lines, bg=CLAUDE_ORANGE, fg=WHITE, anchor="ma")
        if t >= t_bend:
            sparkles(ui, 292, y, t, r=6, n=2, seed=10, big=True)
    if t >= t_dont:
        amp = lerp(1.5, 4.5, ramp(t, t_dont, t_bend))
        sag = 14 * ease_out(ramp(t, t_bend, t_bend + 0.3))
        pts = line_path(30, 106, 50, amp, sag, t, 14)
        d.line(pts, fill=K, width=5, joint="curve")
        d.line(pts, fill=RED, width=3, joint="curve")
        tag(ui, 68, 36, "YOUR LINE", age=t - t_dont, bg=OPENAI_GREEN, fg=WHITE, anchor="ma")


# --- 11 (kill): fired off the stage ---------------------------------------------------

CANNON_S = 2
FIRED_ON, BACK_ON = 17, 22     # Nov 2023: out on the 17th, back five days later


@lru_cache(maxsize=None)
def cal_page(day):
    w, h = 44, 40
    img = Image.new("RGBA", (w + 2, h + 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.rectangle((0, 4, w + 1, h + 5), fill=K)
    d.rectangle((1, 5, w, h + 4), fill=WHITE)
    d.rectangle((1, 5, w, 15), fill=RED)
    silk(d, (w // 2 + 2, 8), "NOV", WHITE, anchor="ma")
    d.text((w // 2 + 2, 22), str(day), font=PRESS16, fill=K, anchor="ma")
    for rx in (10, w - 8):
        d.rectangle((rx - 1, 0, rx + 1, 8), fill=K)
    return img


@lru_cache(maxsize=None)
def cal_page_big(day, s=1.25):
    img = cal_page(day)
    return img.resize((int(img.width * s), int(img.height * s)), Image.NEAREST)


@gag(SEC, 11, pre=0.12, post=0.4)
def fired_off_stage(c, L):
    t = c.t
    c.shot = "wide"
    c.lock_shot = True
    t_now, t_get, t_fired = wt(L, "Now"), wt(L, "get"), wt(L, "fired")
    t_stage, t_see = wt(L, "stage"), wt(L, "see")
    t_five = wt(L, "five")
    fall0, land = 172.26, 172.54   # back from the sky once "again" is out
    s = c.st["sam"]
    gone = t >= t_fired
    if gone:
        s["hidden"] = True
        if t < land:
            s.update(eyes="wide", mouth="shout", brows="worried")
        else:
            s.update(eyes="x", mouth="o", brows="worried")
    d = c.st["dario"]
    if t_now <= t < t_fired:
        d["front_arm"] = "point"
    elif t_fired <= t < t_fired + 0.6:
        d["front_arm"] = "pump"
    if t_fired <= t < t_fired + 1.3:
        c.crowd = "hype"
    if 0 <= t - t_fired < 2 / 24:
        c.add_flash(0.6)
    impact(c, t - t_fired, shake=14, dur=0.4)
    impact(c, t - land, shake=10, dur=0.3)
    cimg = scaled(cannon(), CANNON_S)
    roll_in = ease_out(ramp(t, t_now - 0.05, t_get))
    roll_out = ramp(t, t_stage + 0.2, t_stage + 0.7) ** 2
    cx = lerp(-cimg.width - 6, 14, roll_in) - roll_out * 140
    cy = FEET_Y + 1 - cimg.height
    muzzle = (cx + 39 * CANNON_S, cy + 7 * CANNON_S)
    yield "back"
    w = c.world
    if roll_in > 0 and cx > -cimg.width:
        recoil = int(-6 * max(0.0, 1 - (t - t_fired) / 0.25)) if t >= t_fired else 0
        paste(w, cimg, cx + recoil, cy)
        if t_get <= t < t_fired:
            sx, sy = cx + 10, cy + 20
            if int(t * 20) % 2:
                burst(w, sx, sy, 1, 4, GOLD, spikes=6, rot=t * 9)
    yield "front"
    if t_fired <= t < t_fired + 0.9:
        age = t - t_fired
        if age < 0.2:
            burst(w, muzzle[0] + 4, muzzle[1] - 2, 6 + age * 60, 14 + age * 90, GOLD, spikes=12)
            burst(w, muzzle[0] + 4, muzzle[1] - 2, 3 + age * 30, 8 + age * 50, WHITE, spikes=12)
        smoke(w, muzzle[0] + 2, muzzle[1] - 4, age, n=6, seed=11)
    if t_fired <= t < t_fired + 0.75:
        p = ramp(t, t_fired, t_fired + 0.7)
        a0, a1 = (84, 95), (272, -64)
        body = char_sprite("sam", 1, "shout", "worried", "wide", "up", "up")
        dw = ImageDraw.Draw(w)
        for k in (4, 3, 2, 1):
            q = p - k * 0.05
            if q > 0:
                tx, ty = arc_pt(q, a0, a1, 24)
                r = 1 + k
                dw.ellipse((tx - r - 1, ty - r - 1, tx + r + 1, ty + r + 1), fill=K)
                dw.ellipse((tx - r, ty - r, tx + r, ty + r), fill=(214, 214, 224))
        x, y = arc_pt(p, a0, a1, 24)
        paste_rot(w, body, x, y, -560 * p)
    if fall0 - 0.3 <= t < land:     # his shadow grows on the spot where he'll land
        q = ramp(t, fall0 - 0.3, land)
        rx, ry = 3 + 13 * q, 1 + 2 * q
        ImageDraw.Draw(w).ellipse((80 - rx, FEET_Y + 1 - ry, 80 + rx, FEET_Y + 1 + ry), fill=(22, 14, 30))
    if fall0 <= t < land:
        p = ramp(t, fall0, land) ** 2
        body = char_sprite("sam", 1, "shout", "worried", "wide", "up", "up")
        yb = lerp(20, FEET_Y + 4, p)
        paste(w, body, 80, yb, "mb")
        dw = ImageDraw.Draw(w)
        for k, sx in enumerate((68, 80, 92)):   # speed lines trailing above him
            y1 = yb - body.height + body.getbbox()[1] - 3 - 4 * (k % 2)
            dw.line((sx, y1 - 16, sx, y1), fill=(230, 230, 240))
    elif t >= land:
        age = t - land
        body = char_sprite("sam", 1, "o", "worried", "x", "down", "down")
        if age < 0.08:
            body = body.resize((body.width + 6, int(body.height * 0.86)), Image.NEAREST)
        paste(w, body, 80, FEET_Y + 4 + 1, "mb")
        dust(w, 80, FEET_Y, age, seed=12)
        for k in range(3):
            ang = t * 7 + k * 2 * math.pi / 3
            star = spr("DIZZY")
            paste(w, star, 81 + 14 * math.cos(ang), FEET_Y - 70 + 4 * math.sin(ang), "mm")
    yield "ui"
    ui = c.ui
    t_title = t_fired + 0.28          # slams in once he has cleared the title band
    if t_title <= t < t_see:
        age = t - t_title
        if age < 0.8 or blink(c, 5):
            title(ui, 160, 36, "FIRED!", PRESS24, top=(255, 230, 120), bottom=(255, 90, 30), age=age)
    if t_see <= t < (big_hit_t(L) or fall0):   # makes way for the OVERKILL! label
        title(ui, 160, 38, "SEE YOU IN", PRESS16, top=WHITE, bottom=(170, 200, 255), age=t - t_see)
    if t_five <= t < fall0:
        flips = [t_five + 0.06 + i * 0.08 for i in range(BACK_ON - FIRED_ON)]
        n = sum(t >= tf for tf in flips)
        cy = 112 + (pop_dy(t - t_five) or 0)
        paste_scaled(ui, cal_page_big(FIRED_ON + n), 160, cy, min(1.0, pop_scale(t - t_five)))
        for i, tf in enumerate(flips[:n]):   # torn pages whip off over the empty left side
            if t - tf < 0.6:
                falling_piece(ui, 160, cy, t - tf, spin=9 + i, g=320, vx=-(340 + 40 * i),
                              vy=-130, piece=cal_page_big(FIRED_ON + i))
        t_tag = flips[-1] + 0.04
        if t >= t_tag:   # left of the calendar: the right side is Dario's face
            tag(ui, 127, 100, "+5 DAYS", age=t - t_tag, bg=GOLD, fg=K, fnt=PRESS, anchor="ra")
