"""Verse 2 gags: Dario raps, Sam takes the hits (lines v2 0-11)."""
import re

from gagkit import (CURSOR, FEET_Y, FPS, GOLD, H, K, NEON_CYAN, NEON_EXTRA, NEON_PINK, OPENAI_GREEN,
                    PRESS, PRESS16, PRESS24, RED, TL, W, WHITE, Image, ImageDraw, Prop, arc_pt,
                    arrow, ascii_sprite, bevel, big_text, blink, burst, calm, caption, char_sprite,
                    chicken, clamp, dither, dither_poly, dither_rect, ease_out, falling_piece,
                    flames, gag, glitch, glow, grow_mask, impact, keycap, lerp, lru_cache, math, np,
                    outline_text, paper, paste, paste_rot, paste_scaled, pencil_scribble, pentagon,
                    pop_dy, pop_scale, poster_frame, ramp, render_head, rnd, scaled, silk, smoke,
                    sparkles, spr, stamp, tag, text_width, thought, title, uncle_sam_hat, waveform,
                    win95, win_client, wt, x_mark)
from scene import NEON_GLYPHS, draw_popup  # not re-exported by gagkit

GLASS = (92, 40, 80)                 # an unlit neon tube (as on the venue sign)
MINT = (170, 240, 210)
SKY, SKY_DK, CLOUD = (120, 196, 255), (70, 140, 230), (246, 250, 255)
SILVER, SILVER_DK = (214, 220, 236), (132, 140, 166)
AMBER, AMBER_DIM = (255, 176, 40), (72, 42, 22)
DOOR_LIGHT = (255, 244, 200)
SEPIA = (200, 170, 120)
WIN_BLUE = (0, 0, 128)
UI_FLOOR = 146                       # the karaoke band starts here


# --- shared bits ------------------------------------------------------------------

def v2_line(idx):
    return next(ln for ln in TL.LINES if ln["sec"] == "v2" and ln["idx"] == idx)


def word_t(idx, pat, n=0):
    """Word time in another v2 line (for props that carry over from one line to the next)."""
    return [w["t0"] for w in v2_line(idx)["words"] if re.search(pat, w["w"], re.I)][n]


def cut_t(L):
    """When the next line's gag takes over the camera."""
    return v2_line(L.ln["idx"] + 1)["t0"] - 0.12


def hit_time(L):
    for h in TL.HITS:
        if h["line"] == L.ln["gi"]:
            return h["t"]
    return L.words[-1]["t0"] + 0.04


def take_shot(c, L, shot, lock=False):
    """Cut to `shot` once this line owns the camera (the previous gag keeps it until then)."""
    if c.t >= L.t0 - 0.12:
        c.shot = shot
        c.lock_shot = c.lock_shot or lock


def face(c, who, **kw):
    """Expression changes that give way to a fresh hit reaction."""
    if calm(c, who):
        c.st[who].update(kw)


FLICK_ON = (1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1)
FLICK_DIE = (1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0)


def flick(age, pattern):
    """Neon flicker frame by frame (the last entry holds); None before it starts."""
    if age < 0:
        return None
    return bool(pattern[min(int(age * FPS), len(pattern) - 1)])


@lru_cache(maxsize=None)
def txt(s, fnt=PRESS16, top=WHITE, bottom=GOLD):
    """big_text as a sprite, for letters that fly about."""
    im = Image.new("RGBA", (text_width(s, fnt) + 14, fnt.size + 14), (0, 0, 0, 0))
    big_text(im, (6, 6), s, fnt, top=top, bottom=bottom)
    return im.crop(im.getbbox())


def click_fx(ui, x, y, age):
    """Little ticks radiating from a mouse click."""
    if not 0 <= age < 0.16:
        return
    d = ImageDraw.Draw(ui)
    r0, r1 = 4 + age * 30, 7 + age * 40
    for k in range(6):
        a = k * math.pi / 3 + 0.4
        d.line([(x + r0 * math.cos(a), y + r0 * math.sin(a)),
                (x + r1 * math.cos(a), y + r1 * math.sin(a))], fill=WHITE)


def sparks(img, x, y, age, n=12, seed=0):
    """Sparks spraying out of a blown neon tube."""
    if not 0 <= age < 0.6:
        return
    d = ImageDraw.Draw(img)
    for i in range(n):
        vx = (rnd("spx", seed, i) - 0.5) * 90
        vy = -25 - rnd("spy", seed, i) * 45
        px, py = x + vx * age, y + vy * age + 150 * age * age
        d.line([(px - vx * 0.03, py - (vy + 150 * age) * 0.03), (px, py)],
               fill=(WHITE, GOLD, (255, 140, 40))[i % 3])


def fall_ui(ui, x, y, age, **kw):
    """falling_piece on the UI layer, dropping out of sight behind the karaoke band."""
    layer = Image.new("RGBA", ui.size, (0, 0, 0, 0))
    falling_piece(layer, x, y, age, **kw)
    ui.alpha_composite(layer.crop((0, 0, ui.width, UI_FLOOR)))


def polyline_part(pts, p):
    """The first fraction p (by length) of a polyline."""
    lens = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    left = sum(lens) * clamp(p, 0.0, 1.0)
    out = [pts[0]]
    for (a, b), n in zip(zip(pts, pts[1:]), lens):
        if left <= n:
            u = left / n if n else 1.0
            out.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u)))
            break
        out.append(b)
        left -= n
    return out


# --- neon ---------------------------------------------------------------------------

GLYPHS = dict(NEON_GLYPHS, **NEON_EXTRA)
GLYPHS["I"] = [[(2, 0), (8, 0)], [(5, 0), (5, 15)], [(2, 15), (8, 15)]]


def neon_text(img, s, x0, top, color, lit, adv=15, frame=None, frame_on=True):
    """Neon letters: indices in `lit` glow, the rest are dark glass (world layer)."""
    tubes = {True: Image.new("L", (W, H), 0), False: Image.new("L", (W, H), 0)}
    draws = {k: ImageDraw.Draw(v) for k, v in tubes.items()}
    for i, ch in enumerate(s):
        for stroke in GLYPHS[ch]:
            draws[i in lit].line([(x0 + i * adv + px, top + py) for px, py in stroke], fill=255)
    if frame:
        ft = Image.new("L", (W, H), 0)
        ImageDraw.Draw(ft).rounded_rectangle(frame, radius=3, outline=255)
        if frame_on:
            glow(img, ft, NEON_CYAN, radius=3, strength=1.5)
        else:
            dither(img, np.asarray(ft, np.float32) / 255.0, (34, 60, 70))
    dither(img, np.asarray(tubes[False], np.float32) / 255.0, GLASS)
    if lit:
        glow(img, tubes[True], color)


# --- v2-0: the OPENAI sign blows its AI; only the OPEN (mouth) is left -------------------

SIGN_X, SIGN_TOP = 108, 76
SIGN_BOARD = (102, 70, 200, 98)
SIGN_FRAME = (104, 72, 198, 96)


@gag("v2", 0)
def open_sign(c, L):
    t = c.t
    t_thing, t_open = wt(L, r"^thing"), wt(L, r"^open$")
    t_is, t_your = wt(L, r"^is$"), wt(L, r"^your")
    take_shot(c, L, "cL" if t >= t_open else "two", lock=t >= t_open)
    if t < t_thing:
        c.st["sam"]["front_arm"] = "up"             # ta-da: presenting his sign
        face(c, "sam", mouth="grin", brows="raised")
    elif t < t_open:
        face(c, "sam", mouth="o", brows="worried", eyes="wide")
    else:
        face(c, "sam", mouth=("open", "o", "shout", "o")[int(t * 12) % 4], brows="raised")
    yield "back"
    if t < L.t0:
        return
    ImageDraw.Draw(c.world).rounded_rectangle(SIGN_BOARD, radius=3, fill=(22, 14, 30), outline=K)
    on = flick(t - L.t0, FLICK_ON)
    dead = flick(t - t_thing, FLICK_DIE) is False
    lit = set()
    if on:
        lit = {0, 1, 2, 3} if dead else {0, 1, 2, 3, 4, 5}
    neon_text(c.world, "OPENAI", SIGN_X, SIGN_TOP, NEON_PINK, lit, frame=SIGN_FRAME, frame_on=on)
    sparks(c.world, SIGN_X + 4 * 15 + 12, SIGN_TOP + 5, t - t_thing, seed=3)
    yield "ui"
    a = c.anchor.get("sam")
    if t < t_is or a is None:
        return
    mx, my = c.to_ui(*a["mouth"])
    x0, y0 = 204, 112
    p = ease_out(ramp(t, t_is, t_is + 0.12))
    arrow(c.ui, x0, y0, lerp(x0, mx + 12, p), lerp(y0, my + 2, p), color=GOLD, width=3, head=7)
    if t >= t_your:
        caption(c.ui, 224, 104 + (pop_dy(t - t_your) or 0), "24/7", anchor="ma")


# --- v2-1: NONPROFIT drops an N, the halo drops too, the chart heads south -----------------

PLATE = (82, 33, 238, 61)
ZIGZAG = [(100, 68), (118, 82), (128, 76), (146, 98), (158, 92), (174, 120), (186, 114), (200, 140)]


@lru_cache(maxsize=None)
def plate_img(s):
    x0, y0, x1, y1 = PLATE
    im = Image.new("RGBA", (x1 - x0 + 1, y1 - y0 + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=3, fill=K)
    d.rounded_rectangle((1, 1, im.width - 2, im.height - 2), radius=2, fill=OPENAI_GREEN)
    d.rectangle((3, 3, im.width - 4, im.height - 4), fill=(18, 66, 56))
    big_text(im, (6, 6), s, PRESS16, top=WHITE, bottom=MINT)
    return im


def chart_arrow(ui, pts, p, color=RED):
    part = polyline_part(pts, p)
    if len(part) < 2 or math.dist(part[0], part[-1]) < 2:
        return
    d = ImageDraw.Draw(ui)
    d.line(part, fill=K, width=5, joint="curve")
    if len(part) > 2:
        d.line(part[:-1], fill=color, width=3, joint="curve")
    arrow(ui, *part[-2], *part[-1], color=color, width=3, head=7)


@gag("v2", 1, post=0.3)
def no_profit(c, L):
    t = c.t
    t_non, t_no = wt(L, r"^nonprofit"), wt(L, r"^no$")
    t_head, t_south = wt(L, r"^heading"), wt(L, r"^south")
    live = t < cut_t(L)               # the post window only lets the plate finish falling
    if live:
        take_shot(c, L, "two")
        if t < t_no:
            face(c, "sam", eyes="happy", mouth="smirk", brows="raised")
        else:
            face(c, "sam", mouth="frown", brows="worried")
        if t >= t_head:
            c.st["sam"]["sweat"] = True
    yield "front"
    a = c.anchor.get("sam")
    if a and t >= L.t0:
        halo, cx, y = spr("HALO"), a["hx"] + 18, a["hy"] - 4
        if t < t_no:
            paste(c.world, halo, cx, y - int(t * 3) % 2, "mm")
        else:
            falling_piece(c.world, cx, y, t - t_no, spin=4, g=300, vx=-20, vy=-50, piece=halo)
    yield "ui"
    ui = c.ui
    if t >= t_non:
        img = plate_img("NONPROFIT" if t < t_no else "NO PROFIT")
        cx, cy = (PLATE[0] + PLATE[2]) / 2, (PLATE[1] + PLATE[3]) / 2
        if t < t_south:
            paste(ui, img, cx, cy + (pop_dy(t - t_non) or 0), "mm")
        else:
            fall_ui(ui, cx, cy, t - t_south, spin=-1.5, g=1400, vx=24, vy=0, piece=img)
    if t >= t_no:
        fall_ui(ui, 128, 47, t - t_no, spin=2.5, g=900, vx=16, vy=10,
                piece=txt("N", PRESS16, WHITE, MINT))
    if t_head <= t and live:
        chart_arrow(ui, ZIGZAG, ramp(t, t_head, t_south - 0.06))


# --- v2-2: ALT + MAN? Nah: ALT + F4 -------------------------------------------------------

@lru_cache(maxsize=None)
def cap_img(s, pressed=0, crossed=False):
    w = max(26, text_width(s, PRESS) + 14)
    im = Image.new("RGBA", (w + 1, 25), (0, 0, 0, 0))
    keycap(im, 0, 0, s, pressed)
    if crossed:
        x_mark(im, w // 2, 12, r=8)
    return im


def dashed_box(ui, box, color=WHITE):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(ui)
    for x in range(x0, x1, 4):
        d.line([(x, y0), (min(x + 1, x1), y0)], fill=color)
        d.line([(x, y1), (min(x + 1, x1), y1)], fill=color)
    for y in range(y0, y1, 4):
        d.line([(x0, y), (x0, min(y + 1, y1))], fill=color)
        d.line([(x1, y), (x1, min(y + 1, y1))], fill=color)


@gag("v2", 2)
def alt_f4(c, L):
    t = c.t
    t_nah, t_youre, t_f4 = wt(L, r"^nah"), wt(L, r"^you"), wt(L, r"^alt-f4")
    t_man = L.t0 + 0.26
    take_shot(c, L, "cL" if t >= t_f4 else "two", lock=True)
    if t < t_nah:
        face(c, "sam", mouth="grin", brows="raised")
    elif t < t_f4:
        face(c, "sam", mouth="frown", brows="worried")
    yield "ui"
    ui = c.ui
    if t < t_f4:
        # two-shot: ALT + MAN, then MAN gets crossed out and dropped for a mystery key
        if t >= L.t0:
            pr = 2 if L.t0 + 0.08 <= t < L.t0 + 0.2 else 0
            paste_scaled(ui, cap_img("ALT", pr), 133, 62, pop_scale(t - L.t0), "mm")
        if t < t_man:
            return
        paste(ui, txt("+"), 160, 62, "mm")
        crossed = t >= t_nah
        if t < t_nah + 0.14:
            pr = 2 if t_man + 0.08 <= t < t_man + 0.2 else 0
            paste_scaled(ui, cap_img("MAN", pr, crossed), 187, 62, pop_scale(t - t_man), "mm")
        else:
            fall_ui(ui, 187, 62, t - t_nah - 0.14, spin=3, g=1200, vx=40, vy=-30,
                    piece=cap_img("MAN", 0, True))
        if t >= t_youre + 0.1 and blink(c, 3):
            dashed_box(ui, (170, 50, 200, 74))
            paste(ui, txt("?"), 185, 62, "mm")
        return
    # close-up: ALT + F4 slams home
    age = t - t_f4
    land = 0.06
    pr = 3 if land <= age < land + 0.12 else 0
    if land <= age < 0.3:
        a = age - land
        burst(ui, 244, 70, 10 + a * 40, 18 + a * 50, GOLD, spikes=10, rot=a * 3)
    paste(ui, cap_img("ALT", pr), 219, 70, "mm")
    paste(ui, txt("+"), 246, 70, "mm")
    fy = lerp(-20, 70, ramp(age, 0, land) ** 2)
    paste(ui, cap_img("F4", pr), 269, fy, "mm")
    if age >= 0.25:
        tag(ui, 244, 90, "CLOSE WINDOW", age - 0.25, bg=(255, 255, 214), anchor="ma")


# --- v2-3: BOARD.EXE closes Sam's window, then shows him the door --------------------------

POPUP_XY = (102, 44)
DOOR_AT = (46, FEET_Y + 1)          # door sprite anchor (mb) in the world


@lru_cache(maxsize=None)
def board_popup(focus=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    w, h = draw_popup(im, 0, 0, "BOARD.EXE", "Close Sam?", ["YES", "YES"], focus=focus, cursor=False)
    return im.crop((0, 0, w + 3, h + 3))


@lru_cache(maxsize=None)
def door_back():
    """The bright doorway, drawn behind anything that flies through it (26x62)."""
    im = Image.new("RGBA", (26, 62), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((3, 12, 22, 61), fill=DOOR_LIGHT)
    d.rectangle((7, 16, 18, 61), fill=(255, 252, 236))
    return im


@lru_cache(maxsize=None)
def door_front(open_q):
    """Frame, EXIT sign and the door leaf; open_q runs 0 (shut) .. 8 (wide open)."""
    im = Image.new("RGBA", (26, 62), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 9, 25, 61), fill=K)
    d.rectangle((1, 10, 24, 61), fill=(128, 88, 60))
    d.line([(2, 11), (23, 11)], fill=(168, 124, 88))
    d.rectangle((3, 12, 22, 61), fill=(0, 0, 0, 0))
    d.rectangle((1, 0, 24, 8), fill=K)
    d.rectangle((2, 1, 23, 7), fill=(30, 170, 80))
    silk(d, (13, 2), "EXIT", WHITE, anchor="ma")
    wl = int(round(20 * math.cos(open_q / 8 * math.pi / 2)))
    if wl > 0:
        d.rectangle((3, 12, 2 + wl, 61), fill=K)
        d.rectangle((3, 12, 1 + wl, 61), fill=(150, 104, 70))
        for py in (16, 38):
            d.rectangle((5, py, max(5, wl - 1), py + 16), outline=(118, 80, 54))
        if wl > 8:
            d.rectangle((wl - 2, 36, wl - 1, 37), fill=GOLD)
    return im


@lru_cache(maxsize=None)
def sam_flyer():
    im = char_sprite("sam", -1, "shout", "worried", "wide", "up", "up")
    return im.crop(im.getbbox())


@gag("v2", 3, post=0.4)
def board_door(c, L):
    t = c.t
    t_board, t_closed = wt(L, r"^board"), wt(L, r"^closed")
    t_your2, t_window = wt(L, r"^your", 1), wt(L, r"^window")
    t_and, t_showed = wt(L, r"^and$"), wt(L, r"^showed")
    t_the, t_door = wt(L, r"^the$"), wt(L, r"^door")
    t_hit = hit_time(L)
    t_slam = t_hit + 0.16
    take_shot(c, L, "L" if t >= t_and else "wide", lock=t >= t_and)
    sam = c.st["sam"]
    if t >= t_hit:
        sam["hidden"] = True
    elif t >= t_showed:
        sam["facing"], sam["sweat"] = -1, True
        face(c, "sam", eyes="wide", brows="worried", mouth="o")
    if t >= t_showed:
        c.st["dario"]["front_arm"] = "point"
    impact(c, t - t_slam, shake=9)
    yield "back"
    if t >= t_and:
        if t < t_slam:
            open_p = ease_out(ramp(t, t_the, t_door))
        else:
            open_p = 1 - ramp(t, t_slam, t_slam + 0.04)
        s = pop_scale(t - t_and)
        if open_p > 0:
            x, y = DOOR_AT
            dither_poly(c.world, [(x - 10, y - 1), (x + 9, y - 1), (x + 30, y + 5), (x - 16, y + 5)],
                        DOOR_LIGHT, density=0.5 * open_p, blend=0.5)
        paste_scaled(c.world, door_back(), *DOOR_AT, s, "mb")
        fp = ramp(t, t_hit, t_hit + 0.18)
        if t_hit <= t and fp < 1:
            x, y = arc_pt(fp, (80, 107), (46, 116), 12)
            fl = sam_flyer()
            fl = fl.resize((max(1, int(fl.width * lerp(1, 0.2, fp))),
                            max(1, int(fl.height * lerp(1, 0.2, fp)))), Image.NEAREST)
            paste_rot(c.world, fl, x, y, fp * 330)
        paste_scaled(c.world, door_front(int(round(open_p * 8))), *DOOR_AT, s, "mb")
    yield "ui"
    ui = c.ui
    if t < t_and:
        if t_board <= t < t_window:
            img = board_popup(0 if t >= t_closed else None)
            x, y = POPUP_XY
            p = ramp(t, t_your2, t_window)
            hh = max(1, int(round(img.height * (1 - p))))
            if p > 0:
                img = img.resize((img.width, hh), Image.NEAREST)
            paste(ui, img, x, y + (pop_dy(t - t_board) or 0) + (53 - hh) // 2)
            cp = ease_out(ramp(t, t_board, t_board + 0.24))
            cx, cy = lerp(250, 141, cp), lerp(124, 84, cp)
            paste(ui, CURSOR, cx, cy)
            click_fx(ui, cx, cy, t - t_closed)
        if t >= t_window:
            smoke(ui, 160, 70, t - t_window, n=7, seed=5)
        return
    age = t - t_hit
    if 0 <= age < 0.3:
        bx, by = 122, 85
        burst(ui, bx, by, (10 + age * 30) * 1.5, (22 + age * 40) * 1.5, GOLD, spikes=12, rot=age * 4)
        burst(ui, bx, by, (5 + age * 16) * 1.5, (11 + age * 22) * 1.5, WHITE, spikes=12, rot=age * 4 + .3)
    if t >= t_slam + 0.02:
        title(ui, 49, 46, "SLAM!", top=WHITE, bottom=(255, 120, 90), age=t - t_slam - 0.02)


# --- v2-4: 5 DAYS LATER... he's back, like a pop-up ad ------------------------------------------

AD_W, AD_H = 110, 76


def days_later(ui, t, t_later):
    d = ImageDraw.Draw(ui)
    d.rectangle((0, 0, W, H), fill=(70, 36, 120))
    cx, cy, rot = 160, 100, t * 0.8
    for k in range(12):
        a0 = rot + k * math.pi / 6
        a1 = a0 + math.pi / 12
        d.polygon([(cx, cy), (cx + 400 * math.cos(a0), cy + 400 * math.sin(a0)),
                   (cx + 400 * math.cos(a1), cy + 400 * math.sin(a1))], fill=(104, 60, 170))
    big_text(ui, (160, 84), "5 DAYS", PRESS24, top=WHITE, bottom=GOLD, anchor="ma")
    title(ui, 160, 116, "LATER...", top=WHITE, bottom=(255, 170, 220), age=t - t_later)


def setup_window(ui, frac):
    x0, y0, x1, y1 = win95(ui, 16, 58, 120, 44, "SETUP.EXE")
    d = ImageDraw.Draw(ui)
    silk(d, (x0 + 4, y0 + 3), "REINSTALLING CEO...", K)
    bevel(d, (x0 + 3, y0 + 12, x1 - 3, y0 + 22), raised=False)
    for i in range(int(clamp(frac, 0, 1) * 14)):
        d.rectangle((x0 + 6 + i * 7, y0 + 15, x0 + 11 + i * 7, y0 + 19), fill=WIN_BLUE)


@lru_cache(maxsize=None)
def sam_pop_sprite():
    return char_sprite("sam", 1, "grin", "raised", "happy", "up", "up").crop((0, 0, 80, 97))


def sam_ad(ui, x, y, c, age=1.0):
    """The pop-up ad starring Sam; its close button sits at (x + AD_W - 9, y + 7)."""
    if age < 0:
        return
    x, y = int(round(x)), int(round(y + (pop_dy(age) or 0)))
    x0, y0, x1, y1 = win_client(ui, x, y, AD_W, AD_H, "ADVERTISEMENT", fill=(255, 250, 214))
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    d.text((x + AD_W // 2, y0 + 3), "CEO AGAIN!", font=PRESS,
           fill=RED if blink(c, 4) else (40, 40, 170), anchor="ma")
    head = render_head("sam", "grin", "raised", "happy")
    ui.paste(head, (x0 + 2, y0 + 13), head)
    silk(d, (x + 76, y0 + 16), "LIMITED", RED, anchor="ma")
    silk(d, (x + 76, y0 + 24), "TIME!", RED, anchor="ma")
    bevel(d, (x + 47, y0 + 35, x + 104, y0 + 48))
    silk(d, (x + 76, y0 + 39), "CLICK HERE", (0, 0, 160), anchor="ma")


@gag("v2", 4, pre=0.0)
def pop_up_ad(c, L):
    t = c.t
    t_card, t_later, t_you = L.t0 + 0.22, wt(L, r"^later"), wt(L, r"^you$")
    t_pop, t_ad = wt(L, r"^pop-up"), wt(L, r"^ad$")
    t_card_end = t_you + 0.04
    if t >= t_card:
        take_shot(c, L, "two", lock=True)
    if t_card <= t < t_card_end:
        c.hitfx = False
    sam = c.st["sam"]
    if t < t_pop + 0.16:
        sam["hidden"] = True
    else:
        sam["back_arm"] = sam["front_arm"] = "up"
        face(c, "sam", mouth="grin", brows="raised", eyes="happy")
    yield "front"
    if t_pop <= t < t_pop + 0.16:
        paste_scaled(c.world, sam_pop_sprite(), 80, FEET_Y + 1, pop_scale(t - t_pop), "mb")
    yield "ui"
    ui = c.ui
    if t_card <= t < t_card_end:
        days_later(ui, t, t_later)
    elif t_card_end <= t < t_pop:
        setup_window(ui, ramp(t, t_card_end, t_pop - 0.1))
    if t >= t_pop:
        age = t - t_pop
        if age < 0.3:
            burst(ui, 68, 46, 8 + age * 30, 20 + age * 50, WHITE, spikes=10, rot=age * 3)
        title(ui, 68, 38, "POP!", top=WHITE, bottom=(255, 140, 200), age=age)
    sam_ad(ui, 104, 40, c, t - t_ad)


# --- v2-5: can't close you, Sam (the X runs away), then the ads multiply ---------------------------

AD_HOPS = ((104, 40), (120, 56), (98, 44))
CASCADE = (((100, 36), "WIN!!!", ("FREE AGI!", "CLICK NOW"), (255, 236, 120)),
           ((112, 52), "HOT DEALS", ("HOT GPUS", "NEAR YOU"), (255, 196, 214)),
           ((124, 68), "VIDEO AD", ("SKIP AD", "IN 99..."), (206, 236, 255)),
           ((136, 84), "SPONSORED", ("ADS BY", "CHATGPT"), (214, 255, 204)))


def close_xy(p):
    return p[0] + AD_W - 9, p[1] + 7


def mini_ad(ui, x, y, title_, lines, fill, age):
    y += pop_dy(age) or 0
    x0, y0, x1, _ = win_client(ui, x, y, 92, 40, title_, fill=fill)
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    for i, s in enumerate(lines):
        d.text(((x0 + x1) // 2 + 1, y0 + 2 + i * 10), s, font=PRESS, fill=K, anchor="ma")


def keyframes(t, keys):
    """Eased position along (time, (x, y)) keyframes."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (ta, a), (tb, b) in zip(keys, keys[1:]):
        if t < tb:
            p = ease_out(ramp(t, ta, tb))
            return lerp(a[0], b[0], p), lerp(a[1], b[1], p)
    return keys[-1][1]


@gag("v2", 5)
def cant_close(c, L):
    t = c.t
    t_close, t_you, t_sam = wt(L, r"^close"), wt(L, r"^you,"), wt(L, r"^sam")
    t_ads, t_never = wt(L, r"^ads"), wt(L, r"^never")
    take_shot(c, L, "two")
    face(c, "sam", mouth="grin", brows="smug")
    yield "ui"
    ui = c.ui
    t_ad = word_t(4, r"^ad$")
    hops = ((t_close, AD_HOPS[0], AD_HOPS[1]), (t_you, AD_HOPS[1], AD_HOPS[2]))
    pos = AD_HOPS[0]
    for th, a, b in hops:
        if t >= th:
            p = ease_out(ramp(t, th, th + 0.05))
            pos = (lerp(a[0], b[0], p), lerp(a[1], b[1], p))
    if t < t_sam:
        sam_ad(ui, *pos, c, t - t_ad)
    elif t < t_sam + 0.45:
        smoke(ui, pos[0] + AD_W // 2, pos[1] + AD_H // 2, t - t_sam, n=8, seed=9)
    if t < t_ads:
        keys = [(L.t0 - 0.1, (292, 138)), (t_close - 0.04, close_xy(AD_HOPS[0])),
                (t_you - 0.04, close_xy(AD_HOPS[1])), (t_sam - 0.06, close_xy(AD_HOPS[2]))]
        cx, cy = keyframes(t, keys)
        paste(ui, CURSOR, cx, cy)
        click_fx(ui, cx, cy, t - t_sam)
    for i, ((x, y), title_, lines, fill) in enumerate(CASCADE):
        age = t - t_ads - i * 0.12
        if age >= 0:
            mini_ad(ui, x, y, title_, lines, fill, age)
    if t >= t_never:
        stamp(ui, 170, 100, "NEVER*", RED, angle=-12, age=t - t_never)
        tag(ui, 170, 125, "*LAST RESORT", t - t_never - 0.12, bg=WHITE, fg=RED, fnt=PRESS,
            anchor="ma")


# --- v2-6: she said NO (off-screen), so he built a Sky --------------------------------------

def speech(ui, box, s, tail, fnt=PRESS16, age=1.0):
    """Speech bubble in a big font; its tail may point off-screen."""
    if age < 0:
        return
    dy = pop_dy(age) or 0
    x0, y0, x1, y1 = box[0], box[1] + dy, box[2], box[3] + dy
    tx, ty = tail[0], tail[1] + dy
    d = ImageDraw.Draw(ui)
    base = [(x0 + 7, y1 - 2), (x0 + 21, y1 - 2)]
    d.polygon(base + [(tx, ty)], fill=K)
    d.rounded_rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), radius=5, fill=K)
    d.rounded_rectangle((x0, y0, x1, y1), radius=4, fill=WHITE)
    ix, iy = lerp(tx, x0 + 14, 0.14), lerp(ty, y1, 0.14)
    d.polygon([(x0 + 9, y1 - 1), (x0 + 19, y1 - 1), (ix, iy)], fill=WHITE)
    tw = text_width(s, fnt)
    d.fontmode = "1"
    d.text(((x0 + x1 - tw) // 2 + 1, (y0 + y1) // 2 - 7), s, font=fnt, fill=K)


def sky_widget(ui, x, y, t, age):
    if age < 0:
        return
    y += pop_dy(age) or 0
    w, h = 92, 48
    d = ImageDraw.Draw(ui)
    d.rounded_rectangle((x - 1, y - 1, x + w, y + h), radius=5, fill=K)
    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=4, fill=SKY)
    d.rectangle((x + 1, y + 1, x + w - 2, y + 10), fill=(30, 60, 140))
    silk(d, (x + 5, y + 3), "VOICE: SKY", WHITE)
    if int(t * 4) % 2:
        d.ellipse((x + w - 9, y + 3, x + w - 5, y + 7), fill=RED)
    for box in ((x + 60, y + 21, x + 74, y + 31), (x + 66, y + 16, x + 82, y + 31),
                (x + 76, y + 22, x + 88, y + 31)):
        d.ellipse(box, fill=CLOUD)
    big_text(ui, (x + 6, y + 15), "SKY", PRESS16, top=WHITE, bottom=(200, 230, 255))
    waveform(ui, x + 7, y + 34, 80, 10, t, color=WHITE, bars=14)


@gag("v2", 6)
def sky_voice(c, L):
    t = c.t
    t_told, t_no, t_so = wt(L, r"^told"), wt(L, r"^no"), wt(L, r"^so$")
    t_sky, t_sounds = wt(L, r"^sky"), wt(L, r"^sounds")
    take_shot(c, L, "L")
    sam = c.st["sam"]
    if t_told <= t < t_so + 0.2:
        sam["facing"] = -1
    if t_no <= t < t_so + 0.2:
        face(c, "sam", eyes="wide", brows="raised", mouth="o")
    elif t >= t_so + 0.2:
        face(c, "sam", mouth="smirk", brows="smug")
    yield "ui"
    ui = c.ui
    if t_no <= t < t_sky:
        speech(ui, (4, 40, 68, 68), "NO.", (-10, 86), age=t - t_no)
    sky_widget(ui, 146, 44, t, t - t_sky)
    if t >= t_sounds:
        caption(ui, 198, 98 + (pop_dy(t - t_sounds) or 0), "SOUNDS FAMILIAR?", anchor="ma")


# --- v2-7: sora.mp4 crashes and burns; Chicken Little; the sky is falling ---------------------

SORA_WIN = (104, 40, 112, 70)
CHICKENS = ((0, 240), (1, 300))     # (which word starts the run, speed px/s), running right to left


def sunset_clip(ui, box, t):
    """A looping 'AI video' in the player: sunset over the sea, with a play bar."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(ui)
    hz = y0 + 30
    for i, col in enumerate(((250, 110, 116), (255, 140, 106), (255, 174, 110), (255, 208, 136))):
        d.rectangle((x0, y0 + i * 8, x1, min(hz, y0 + i * 8 + 7)), fill=col)
    sy = hz - 2 + int(round(math.sin(t * 2.5)))
    d.ellipse(((x0 + x1) // 2 - 10, sy - 10, (x0 + x1) // 2 + 10, sy + 10), fill=(255, 244, 170))
    d.rectangle((x0, hz, x1, y1 - 8), fill=(44, 72, 150))
    for k in range(3):
        wy, off = hz + 3 + k * 4, int(t * 14 + k * 4) % 10
        for wx in range(x0 - 10 + off, x1, 10):
            d.line([(max(x0, wx), wy), (min(x1, wx + 4), wy)], fill=(130, 180, 240))
    d.rectangle((x0, y1 - 7, x1, y1), fill=(24, 24, 34))
    d.polygon([(x0 + 3, y1 - 5), (x0 + 3, y1 - 1), (x0 + 6, y1 - 3)], fill=WHITE)
    d.line([(x0 + 10, y1 - 3), (x1 - 4, y1 - 3)], fill=(90, 90, 110))
    d.line([(x0 + 10, y1 - 3), (x0 + 10 + int((x1 - x0 - 14) * (t * 0.3 % 1)), y1 - 3)], fill=RED)


def spinner(ui, cx, cy, t):
    d = ImageDraw.Draw(ui)
    k0 = int(t * 12) % 8
    for k in range(8):
        a = k * math.pi / 4
        px, py = int(round(cx + 8 * math.cos(a))), int(round(cy + 8 * math.sin(a)))
        col = (80, 80, 100) if (k0 - k) % 8 > 2 else (WHITE, (200, 200, 220), (150, 150, 170))[(k0 - k) % 8]
        d.rectangle((px - 2, py - 2, px + 2, py + 2), fill=K)
        d.rectangle((px - 1, py - 1, px + 1, py + 1), fill=col)


@lru_cache(maxsize=None)
def sky_chunk(seed, w, h):
    """A jagged piece of blue sky (with a cloud on it) that has come loose."""
    pts = []
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.3
        r = 0.7 + 0.3 * rnd("skc", seed, k)
        pts.append((w / 2 - 0.5 + math.cos(a) * r * (w / 2 - 1.5),
                    h / 2 - 0.5 + math.sin(a) * r * (h / 2 - 1.5)))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    fill = Image.new("RGBA", (w, h), SKY + (255,))
    d = ImageDraw.Draw(fill)
    d.rectangle((0, 0, w, h // 4), fill=SKY_DK)
    cx, cy = w * 0.42, h * 0.58
    for ex, ey, r in ((-6, 1, 4), (0, -2, 5), (6, 1, 4)):
        d.ellipse((cx + ex - r, cy + ey - r * 0.7, cx + ex + r, cy + ey + r * 0.7), fill=CLOUD)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(fill, (0, 0), m)
    arr = np.array(img)
    a = arr[:, :, 3] > 0
    arr[grow_mask(a) & ~a] = tuple(K) + (255,)
    return Image.fromarray(arr, "RGBA")


@gag("v2", 7, post=0.3)
def sky_falling(c, L):
    t = c.t
    t_sora, t_crash, t_burn = wt(L, r"^sora"), wt(L, r"^crashed"), wt(L, r"^burned")
    runs = (wt(L, r"^chicken"), wt(L, r"^little"))
    t_sky, t_falling = wt(L, r"^sky"), wt(L, r"^falling")
    t_land, t_bonk = t_sky + 0.26, hit_time(L) - 0.02
    t_cut = cut_t(L)
    take_shot(c, L, "wide")
    if t >= t_sky:
        face(c, "sam", eyes="wide", brows="worried", mouth="o")
    impact(c, t - t_land, shake=6)
    yield "front"
    world = c.world
    chick_x = []
    for i, v in CHICKENS:
        age = t - runs[i]
        x = 340 - v * age
        if age >= 0 and x > -20:
            fr = int(age * 14) % 2
            paste(world, chicken(fr), x, FEET_Y + 2 - fr, "mb")
            chick_x.append(x)
    if t_sky <= t < t_cut:
        p = ramp(t, t_sky, t_land)
        paste_rot(world, sky_chunk(1, 34, 22), 150, lerp(-30, FEET_Y - 10, p * p), -8 + 40 * (1 - p))
    a = c.anchor.get("sam")
    if a and t >= t_falling:
        cx, top = a["hx"] + 18, a["hy"] - 4
        chunk = sky_chunk(2, 28, 18)
        if t < t_bonk:
            p = ramp(t, t_falling, t_bonk)
            paste_rot(world, chunk, cx, lerp(-30, top, p * p), 20 * (1 - p))
        else:
            falling_piece(world, cx, top, t - t_bonk, spin=-5, g=520, vx=-70, vy=-110, piece=chunk)
    yield "ui"
    ui = c.ui
    if t_sora <= t < runs[0]:
        x, y, w, h = SORA_WIN
        y += pop_dy(t - t_sora) or 0
        crashed = t >= t_crash
        box = win95(ui, x, y, w, h, "NOT RESPONDING" if crashed else "SORA.MP4", active=not crashed)
        sunset_clip(ui, box, min(t, t_crash))
        if crashed:
            dither_rect(ui, (box[0], box[1], box[2] + 1, box[3] + 1), WHITE, density=0.4)
            glitch(ui, box, c, n=5, seed=7)
            spinner(ui, (box[0] + box[2]) // 2, (box[1] + box[3]) // 2 - 4, t)
        if t >= t_burn:
            q = ramp(t, t_burn, t_burn + 0.2)
            dither_rect(ui, (x, y, x + w, y + h), (70, 26, 10), density=0.4 * q)
            flames(ui, x + 4, y + h + 1, w - 8, t, h=int(lerp(6, 36, q)))
    if 0 <= t - runs[0] < 0.5:
        smoke(ui, 160, 74, t - runs[0], n=9, seed=11)
    if blink(c, 6):
        for x in chick_x:
            ux, uy = c.to_ui(x, FEET_Y - 17)
            outline_text(ui, (ux, uy), "!", PRESS, RED, anchor="ma")
    if t >= t_bonk:
        hx, top, _ = c.head_ui("sam")
        title(ui, clamp(hx, 48, 272), max(36, top - 28), "BONK!", top=WHITE, bottom=SKY, age=t - t_bonk)


# --- v2-8: Dario told the Pentagon NO; Sam signed up the SAME NIGHT ---------------------------

@lru_cache(maxsize=None)
def pen_img():
    return spr("PEN")


@gag("v2", 8)
def same_night(c, L):
    t = c.t
    t_pent, t_no = wt(L, r"^pentagon"), wt(L, r"^no")
    t_you, t_signed, t_up = wt(L, r"^you$"), wt(L, r"^signed"), wt(L, r"^up$")
    t_same = wt(L, r"^same")
    take_shot(c, L, "two")
    if t >= t_same:
        c.venue["lit"] = False
    if t_you <= t < t_up + 0.1:
        c.st["sam"]["front_arm"] = "point"
        face(c, "sam", mouth="grin", brows="raised", eyes="happy")
    elif t >= t_up + 0.1:
        face(c, "sam", mouth="smirk", brows="smug")
    yield "ui"
    ui = c.ui
    if t_pent <= t < t_same:
        pentagon(ui, 200, 62 + (pop_dy(t - t_pent) or 0), r=18)
        tag(ui, 200, 84, "PENTAGON", t - t_pent, bg=(34, 46, 34), fg=(214, 232, 200), anchor="ma")
        stamp(ui, 201, 64, "NO", RED, angle=-14, age=t - t_no)
    if t >= t_same:
        age = t - t_same
        paste_scaled(ui, spr("MOON", 3), 200, 52, pop_scale(age), "mm")
        sparkles(ui, 196, 54, t, r=24, n=6, seed=4, big=True)
        caption(ui, 160, 118 + (pop_dy(age) or 0), "SAME NIGHT", anchor="ma")
    if t >= t_you:
        x, y = 100, 44 + (pop_dy(t - t_you) or 0)
        paper(ui, x, y, 56, 64, lines=8, title="CONTRACT")
        ex, ey = pencil_scribble(ui, x + 6, y + 52, 40, ramp(t, t_signed, t_up))
        if t_signed - 0.1 <= t < t_up + 0.15:
            paste(ui, pen_img(), ex - 1, ey - 9)
        stamp(ui, x + 30, y + 30, "SIGNED", (40, 150, 70), angle=8, big=False, age=t - t_up)


# --- v2-9: Uncle Sam wants YOU (for the Pentagon); FIGHT! -------------------------------------------

GOATEE = [".kkkkk.", "khhhhhk", "khhhhhk", ".khhhk.", "..khk..", "...k..."]
POSTER_SHOT = (80, 86.6, 11)


@lru_cache(maxsize=None)
def goatee():
    return ascii_sprite(GOATEE)


@gag("v2", 9, post=0.3)
def uncle_sam(c, L):
    t = c.t
    t_sam, t_enl, t_picked = wt(L, r"^sam"), wt(L, r"^enlisted"), wt(L, r"^picked")
    t_fight, t_hit = wt(L, r"^fight"), hit_time(L)
    poster = t_enl <= t < t_picked
    take_shot(c, L, POSTER_SHOT if poster else "two", lock=poster)
    if poster:
        sam = c.st["sam"]
        sam["front_arm"], sam["back_arm"] = "point", "hip"
        face(c, "sam", brows="angry", mouth="frown", eyes="open")
        c.hud["show"] = False
    if t >= t_fight:
        c.st["dario"]["front_arm"] = "punch"
    yield "front"
    a = c.anchor.get("sam")
    if a and t >= L.t0:
        hat = uncle_sam_hat()
        cx, by = a["hx"] + 18, a["hy"] + 9
        if t < t_hit:
            p = ramp(t, L.t0, L.t0 + 0.2)
            if 0 <= t - L.t0 - 0.2 < 0.08:           # squash as it lands
                hat = hat.resize((hat.width + 2, hat.height - 3), Image.NEAREST)
            paste(c.world, hat, cx, by - 70 * (1 - p * p), "mb")
        else:
            falling_piece(c.world, cx - 4, by - 13, t - t_hit, spin=-7, g=500, vx=-45, vy=-120, piece=hat)
        if t >= t_sam:
            mx, my = a["mouth"]
            if t < t_hit:
                paste(c.world, goatee(), mx, my + 3, "mt")
            else:
                falling_piece(c.world, mx - 2, my + 6, t - t_hit, spin=9, g=500, vx=-70, vy=-60,
                              piece=goatee())
    yield "crowd"
    if poster:
        dither(c.world, 0.35, SEPIA, blend=0.35)
    yield "ui"
    if t_fight <= t < cut_t(L):
        age = t - t_fight
        if age < 0.3:
            burst(c.ui, 160, 68, 10 + age * 40, 22 + age * 60, (255, 90, 30), spikes=12, rot=age * 3)
        title(c.ui, 160, 60, "FIGHT!", top=GOLD, bottom=(255, 80, 40), age=age)
    yield "top"
    if poster:
        poster_frame(c.ui, "I WANT YOU", "FOR THE PENTAGON", t - t_enl)


# --- v2-10: "serve the rich?" a cloche of cash; the rich got TASTE ★★★★★ -----------------------------

TASTE_BOX = (96, 36, 200, 68)


@lru_cache(maxsize=None)
def cloche_parts():
    p = Prop(30, 6)
    p.d.rounded_rectangle((1, 1, 28, 4), radius=1, fill=SILVER)
    p.d.line([(3, 1), (26, 1)], fill=WHITE)
    p.d.line([(3, 4), (26, 4)], fill=SILVER_DK)
    plate = p.done()
    p = Prop(26, 18)
    p.d.chord((1, 3, 24, 29), 180, 360, fill=SILVER)
    p.d.rectangle((11, 1, 14, 3), fill=SILVER)
    p.d.arc((4, 6, 21, 27), 200, 250, fill=WHITE)
    p.d.line([(2, 16), (23, 16)], fill=SILVER_DK)
    return plate, p.done()


@lru_cache(maxsize=None)
def star_img(r=7):
    n = 2 * r + 3
    p = Prop(n, n)
    c0 = (n - 1) / 2
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = -math.pi / 2 + k * math.pi / 5
        pts.append((c0 + rr * math.cos(a), c0 + 1 + rr * math.sin(a)))
    p.d.polygon(pts, fill=GOLD)
    img = p.done()
    ImageDraw.Draw(img).point([(c0 - 1, c0 - 1), (c0, c0 - 2)], fill=WHITE)
    return img


@gag("v2", 10, post=0.38)
def rich_taste(c, L):
    t = c.t
    t_serve, t_rich = wt(L, r"^serve"), wt(L, r"^rich")
    t_well, t_taste = wt(L, r"^well"), wt(L, r"^taste")
    take_shot(c, L, "R" if t < t_well else "two")
    if t >= t_serve:
        c.st["dario"]["front_arm"] = "shrug"
    yield "front"
    a = c.anchor.get("dario")
    if a and t >= t_serve:
        world = c.world
        hx, hy = a["hands"][1]
        plate, dome = cloche_parts()
        px, py = hx - 12, hy - 1                     # tray balanced out past the fingertips
        s = pop_scale(t - t_serve)
        paste_scaled(world, plate, px, py, s, "mb")
        if s >= 0.9:
            top = py - plate.height + 2
            if t >= t_rich:
                for i, dx in enumerate((-8, 0, 8)):
                    paste(world, spr("DOLLAR"), px + dx, top + 1 - (i == 1), "mb")
                sparkles(world, px, top - 7, t, r=13, n=4, seed=2)
            lift = ease_out(ramp(t, t_rich, t_rich + 0.1))
            paste_rot(world, dome, px + 6 * lift, top + 1 - dome.height / 2 - 9 * lift, -25 * lift)
    yield "ui"
    if t >= t_taste:
        age = t - t_taste
        dy = pop_dy(age) or 0
        x0, y0, x1, y1 = TASTE_BOX
        d = ImageDraw.Draw(c.ui)
        d.rounded_rectangle((x0 - 1, y0 - 1 + dy, x1 + 1, y1 + 1 + dy), radius=4, fill=K)
        d.rounded_rectangle((x0, y0 + dy, x1, y1 + dy), radius=3, fill=WHITE)
        d.fontmode = "1"
        d.text(((x0 + x1) // 2 + 1, y0 + 4 + dy), "TASTE", font=PRESS, fill=K, anchor="ma")
        for i in range(5):
            paste_scaled(c.ui, star_img(), x0 + 12 + i * 20, y0 + 21 + dy,
                         pop_scale(age - 0.08 - i * 0.05), "mm")


# --- v2-11: IPO in October (ding!) vs. going public in your dreams ---------------------------------

LED_XY, LED_COLS, LED_ROWS = (42, 46), 118, 7


@lru_cache(maxsize=None)
def led_mask(s):
    m = Image.new("L", (max(1, text_width(s, PRESS)), 8), 0)
    d = ImageDraw.Draw(m)
    d.fontmode = "1"
    d.text((0, 0), s, font=PRESS, fill=255)
    return np.asarray(m) > 127


def led_sign(ui, msgs, t):
    """Amber dot-matrix board; each (t0, text) slides in from the right and parks centred."""
    grid = np.zeros((LED_ROWS, LED_COLS), bool)
    live = [(t0, s) for t0, s in msgs if t >= t0]
    if live:
        t0, s = live[-1]
        m = led_mask(s)[:LED_ROWS]
        off = int(round(max((LED_COLS - m.shape[1]) // 2, LED_COLS - (t - t0) * 420)))
        n = min(m.shape[1], LED_COLS - off)
        if n > 0:
            grid[:m.shape[0], off:off + n] = m[:, :n]
    arr = np.zeros((LED_ROWS * 2 + 1, LED_COLS * 2 + 1, 4), np.uint8)
    arr[..., :3], arr[..., 3] = (10, 8, 12), 255
    arr[1::2, 1::2, :3] = np.where(grid[..., None], AMBER, AMBER_DIM)
    img = Image.fromarray(arr, "RGBA")
    x, y = LED_XY
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 3, y - 3, x + img.width + 2, y + img.height + 2), fill=K)
    d.rectangle((x - 2, y - 2, x + img.width + 1, y + img.height + 1), fill=(70, 70, 84))
    ui.paste(img, (x, y))
    return x + img.width // 2, y + img.height + 3


def bell(ui, x, y, age):
    """A bell hanging from (x, y) that swings after being rung `age` s ago (plus 'DING!')."""
    th = 0.5 * math.sin(age * 22) * max(0.0, 1 - age / 0.8) if age >= 0 else 0.0
    rx, ry = x + 7 * math.sin(th), y + 7 * math.cos(th)
    d = ImageDraw.Draw(ui)
    d.line([(x, y), (rx, ry)], fill=K, width=2)
    img = spr("BELL", 2)
    paste_rot(ui, img, rx + 10 * math.sin(th), ry + 10 * math.cos(th), math.degrees(th))
    if 0 <= age < 0.3:
        for side in (-1, 1):
            for k in range(3):
                a = math.radians(-35 + k * 35)
                r0, r1 = 15 + age * 20, 21 + age * 26
                d.line([(x + side * r0 * math.cos(a), ry + 10 + r0 * math.sin(a)),
                        (x + side * r1 * math.cos(a), ry + 10 + r1 * math.sin(a))], fill=WHITE, width=2)
    if 0 <= age < 0.6:
        title(ui, x, ry + 26, "DING!", top=WHITE, bottom=GOLD, age=age)


@lru_cache(maxsize=None)
def snore_z():
    """White Z with a dark rim, 2x (the stock one is black and vanishes against the wall)."""
    z = np.array(spr("Z", k=WHITE))
    arr = np.zeros((z.shape[0] + 2, z.shape[1] + 2, 4), np.uint8)
    arr[1:-1, 1:-1] = z
    a = arr[:, :, 3] > 0
    arr[grow_mask(a) & ~a] = tuple(K) + (255,)
    return scaled(Image.fromarray(arr, "RGBA"), 2)


@gag("v2", 11)
def ipo_dreams(c, L):
    t = c.t
    t_public, t_october = wt(L, r"^public"), wt(L, r"^october")
    t_youre, t_public2 = wt(L, r"^you"), wt(L, r"^public", 1)
    t_your, t_hit = wt(L, r"^your$"), hit_time(L)
    take_shot(c, L, "L" if t >= t_youre else "wide" if t >= t_public else "two")
    asleep = t >= t_youre and calm(c, "sam")
    if asleep:
        s = c.st["sam"]
        k = int((t - t_youre) * 2.5) % 2
        s.update(eyes="blink", brows="neutral", mouth="o" if k else "closed", bob=k)
    yield "ui"
    ui = c.ui
    if t_public <= t < t_youre:
        bx, by = led_sign(ui, ((t_public, "ANTHROPIC IPO"), (t_october, "OCTOBER")), t)
        rung = [tr for tr in (t_public, t_october) if t >= tr]
        bell(ui, bx, by, t - rung[-1])
    if asleep:
        hx, top, _ = c.head_ui("sam")
        z = snore_z()
        for k in range(3):
            ph = (t - t_youre) * 1.1 - k / 3
            if ph >= 0:
                ph %= 1
                paste_scaled(ui, z, lerp(hx - 16, hx - 46, ph), lerp(top + 2, top - 24, ph),
                             lerp(0.5, 1.25, ph), "mm")
        if t >= t_public2:
            lines = ["IPO!", "$$$"] if t >= t_your else ["IPO!"]
            small = Image.new("RGBA", (W // 2, H // 2), (0, 0, 0, 0))
            thought(small, 96, 44, lines, (hx / 2 + 6, top / 2))
            big = scaled(small, 2)
            ui.paste(big, (0, pop_dy(t - t_public2) or 0), big)
    if 0 <= t - t_hit < 0.24:
        age = t - t_hit
        burst(ui, 204, 64, 6 + age * 40, 12 + age * 58, WHITE, spikes=10, rot=age * 4)
