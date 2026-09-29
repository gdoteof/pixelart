"""Verse 3 gags: Sam raps, Dario takes the hits (lines v3 0-11)."""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

import timeline as TL
from gagkit import (CLAUDE_ORANGE, CURSOR, FEET_Y, GOLD, GRAY, GRAY_DK, K, OPENAI_GREEN, PAPER,
                    PAPER_SH, PRESS, PRESS16, RED, RED_DK, WHITE, Prop, arc_pt, ascii_sprite,
                    back_out, bot_img, brain, bread, bubble, burst, calm, check_mark, clamp, crib,
                    cutin, ease_out, engineer_head, envelope, falling_piece, fedora, gag, glitch,
                    impact, label, ladder, lerp, map_prop, medal, meter, mix, newspaper, nose_world,
                    outline_text, paste, paste_rot, paste_scaled, pin, pop_dy, pop_scale, ramp, rnd,
                    road_sign, sandbox, scaled, silk, smoke, sparkles, spr, stamp, strike, tag,
                    terminal, text_width, tile_art, title, typed, wobble, wt, x_mark, xray_spine)
from props import BOT_ROWS, trench_collar   # not re-exported by gagkit

SEC = "v3"
FLOOR = FEET_Y + 1                           # bottom row of props standing on the stage
MANILA, MANILA_DK = (242, 204, 112), (204, 158, 72)
TERM_RED = (255, 90, 90)


def line_end(idx):
    """When line `idx`'s gag window closes (before any `post`)."""
    ls = TL.lines_of(SEC)
    return ls[idx + 1]["t0"] - 0.12 if idx + 1 < len(ls) else TL.section_bounds(SEC)[1]


def dario_face(c, **kw):
    if calm(c, "dario"):
        c.st["dario"].update(kw)


def snapped(c):
    """True while a kill-cam holds on Dario (the snap is decided after setup: draw phases only)."""
    return c.shot == "cR"


def after_big_hit(t0, dur):
    """`t0`, pushed back to `dur` s after a big hit on Dario that lands just before it
    (the kill-cam holds for 0.7 s; the kill label hangs above his head for 1.0 s)."""
    for h in TL.HITS:
        if h["big"] and h["target"] == "dario" and h["t"] <= t0 < h["t"] + dur:
            return h["t"] + dur
    return t0


def paste_pivot(dst, img, x, y, angle):
    """Paste `img` with its bottom-centre at (x, y), rotated `angle` degrees about that point."""
    if not angle:
        paste(dst, img, x, y, "mb")
        return
    w, h = img.size
    pad = Image.new("RGBA", (w + 2 * h, 2 * h), (0, 0, 0, 0))
    pad.paste(img, (h, 0), img)
    paste(dst, pad.rotate(angle, resample=Image.NEAREST), x, y, "mm")


@lru_cache(maxsize=None)
def tinted_bot(body, dark):
    return ascii_sprite(BOT_ROWS, o=body, O=dark)


# --- 0: the whole source leaked through a map file --------------------------------

@lru_cache(maxsize=None)
def folder_img(open_=False):
    """A manila "src/" folder (60x46); open_ drops the front flap."""
    p = Prop(60, 46)
    d = p.d
    d.rounded_rectangle((2, 1, 24, 10), radius=2, fill=MANILA_DK)
    d.rectangle((1, 6, 58, 44), fill=MANILA_DK)
    if open_:
        d.polygon([(1, 30), (58, 30), (53, 44), (6, 44)], fill=MANILA)
    else:
        d.rectangle((1, 12, 58, 44), fill=MANILA)
    img = p.done()
    dd = ImageDraw.Draw(img)
    dd.fontmode = "1"
    if open_:
        dd.rectangle((4, 9, 55, 29), fill=(120, 84, 36))
        dd.line([(1, 30), (58, 30)], fill=K)
    else:
        dd.line([(1, 12), (58, 12)], fill=K)
        dd.line([(2, 13), (57, 13)], fill=(255, 228, 156))
        dd.text((30, 24), "src/", font=PRESS, fill=(110, 70, 20), anchor="ma")
    return img


CODE_COLS = ((206, 90, 146), (44, 120, 200), (60, 160, 80), (226, 120, 40), (120, 120, 140))


@lru_cache(maxsize=None)
def code_sheet(seed=0):
    p = Prop(12, 15)
    p.d.rectangle((1, 1, 10, 13), fill=WHITE)
    img = p.done()
    d = ImageDraw.Draw(img)
    for j in range(5):
        ind = int(rnd("ind", seed, j) * 3)
        n = 2 + int(rnd("len", seed, j) * (6 - ind))
        d.line([(2 + ind, 3 + j * 2), (2 + ind + n, 3 + j * 2)], fill=CODE_COLS[(seed + j) % 5])
    return img


@lru_cache(maxsize=None)
def pin_img(scale=2):
    im = Image.new("RGBA", (12, 16), (0, 0, 0, 0))
    pin(im, 6, 15)
    return scaled(im, scale)


@gag(SEC, 0, pre=0.09)
def source_map_leak(c, L):
    t = c.t
    c.shot = "two"
    t_src, t_code, t_leak = wt(L, "source"), wt(L, r"^code"), wt(L, "leaked")
    t_map, t_no, t_gps = wt(L, r"^map"), wt(L, r"^no$"), wt(L, "GPS")
    if t >= t_leak:
        dario_face(c, eyes="wide", brows="worried", mouth="o")
    if t >= t_map:
        c.st["sam"]["front_arm"] = "point"
    yield "ui"
    ui = c.ui
    cx, cy = 160, 92
    if t < t_src:
        # how it got out: one routine publish
        cmd = typed("npm publish", t - L.t0 - 0.12, 20)
        terminal(ui, 100, 72, 120, 28, [("$ " + cmd, None)], title_="bash", c=c)
        return
    if t_leak <= t < t_leak + 0.8:
        age = t - t_leak
        for i in range(10):
            side = 1 if i % 2 else -1
            falling_piece(ui, cx + side * 6, cy - 14, age, spin=side * (3 + 5 * rnd("lk", i)), g=420,
                          vx=side * (25 + 95 * rnd("lx", i)), vy=-(90 + 90 * rnd("ly", i)),
                          piece=code_sheet(i % 4))
    if t < t_map:
        if t_code <= t < t_leak:
            rise = ease_out(ramp(t, t_code, t_code + 0.2))
            paste(ui, code_sheet(0), cx + 4, cy - 8 - int(8 * rise), "mb")
        wob = wobble(t - t_code, amp=2, freq=45, decay=0.35) if t >= t_code else 0
        paste_scaled(ui, folder_img(t >= t_leak), cx + wob, cy, pop_scale(t - t_src))
        if t >= t_leak:
            title(ui, cx, 38, "LEAKED!", top=WHITE, bottom=RED, age=t - t_leak)
        return
    paste_scaled(ui, map_prop(), cx, cy, 2 * pop_scale(t - t_map))
    tag(ui, cx, 38, "cli.js.map", age=t - t_map, fnt=PRESS, anchor="ma")
    px, py, pin_t = 186, 88, t_map + 0.1
    if t >= pin_t:
        ang = 0
        if t >= t_gps:
            a = t - t_gps
            ang = int(math.sin(a * 22) * 16 * max(0.0, 1 - a / 0.7))
        drop = 1 - back_out(ramp(t, pin_t, pin_t + 0.2))
        paste_pivot(ui, pin_img(2), px, py - int(22 * drop), ang)
    if t >= t_no:
        stamp(ui, cx - 8, cy + 20, "NO GPS", RED, angle=-12, big=True, age=t - t_no)
    if t >= t_gps:
        for i, (qx, qy) in enumerate(((px + 16, py - 34), (px + 26, py - 18))):
            if t - t_gps >= i * 0.08:
                outline_text(ui, (qx, qy + int(2 * math.sin(t * 9 + i * 2))), "?", PRESS16, GOLD)


# --- 1: Undercover Mode, uncovered ---------------------------------------------------

HANDLEBAR = ascii_sprite([
    "kk...........kk",
    "kUk.........kUk",
    "kUUkkkk.kkkkUUk",
    ".kUUUUUkUUUUUk.",
    "..kUUUUUUUUUk..",
    "...kkkkkkkkk...",
])
BUG_SPOTS = ((-8, 40), (6, 47), (-3, 53), (10, 34), (-13, 8), (5, 2), (14, 20), (-7, 27))


def bug_swarm(img, t, t0, x, hy):
    """Bugs scuttle in from the right and settle all over Dario (world space)."""
    for i, (ox, oy) in enumerate(BUG_SPOTS):
        ts = t0 + i * 0.06
        if t < ts:
            continue
        p = ease_out(ramp(t, ts, ts + 0.4))
        sy = hy + oy + (rnd("bugy", i) - 0.5) * 40
        jx = (rnd("bj", i, int(t * 12)) - 0.5) * 2
        jy = (rnd("bk", i, int(t * 12)) - 0.5) * 2
        frame = spr("BUG0" if (int(t * 10) + i) % 2 else "BUG1")
        paste(img, frame, lerp(330, x + ox, p) + jx, lerp(sy, hy + oy, p) + jy, "mm")


@gag(SEC, 1, pre=0.12)
def undercover_mode(c, L):
    t = c.t
    c.shot = "R"
    t_on, t_mode = wt(L, "Undercover"), wt(L, r"^Mode")
    t_exp, t_what = wt(L, "uncovered"), wt(L, r"^what")
    worn = t_on + 0.08 <= t < t_exp
    if worn:
        dario_face(c, eyes="squint", mouth="smirk", brows="raised")
    elif t >= t_exp:
        dario_face(c, eyes="wide", brows="worried", mouth="o" if t < t_what else "teeth",
                   sweat=t >= t_what)
    impact(c, t - t_exp, shake=5)
    yield "front"
    a = c.anchor.get("dario")
    if a:
        w = c.world
        hx, hy = a["hx"], a["hy"]
        x = hx + 18
        if worn:
            paste(w, trench_collar(), x - 15, hy + 29)
            paste(w, HANDLEBAR, hx + 9, hy + 25)
            paste(w, fedora(), hx, hy - 5)
        elif t >= t_exp:
            age = t - t_exp
            falling_piece(w, x + 2, hy + 3, age, spin=7, vx=40, vy=-120, piece=fedora())
            falling_piece(w, hx + 16, hy + 28, age, spin=-9, vx=-45, vy=-90, piece=HANDLEBAR)
            falling_piece(w, x, hy + 36, age, spin=5, vx=26, vy=-70, piece=trench_collar())
        if t_on <= t < t_on + 0.35:
            smoke(w, x, hy + 16, t - t_on, n=7, seed=3)
        if t >= t_what - 0.1:
            bug_swarm(w, t, t_what - 0.1, x, hy)
    yield "ui"
    ui = c.ui
    x0, y0, tw_, th_ = 14, 42, 150, 40
    if t >= t_on:
        lines = [("> " + typed("UNDERCOVER", t - t_on, 24), None)]
        if t >= t_exp:
            lines.append(("ERR: UNCOVERED", TERM_RED))
        elif t >= t_mode:
            lines.append((typed("  MODE: ON", t - t_mode, 30), None))
        y = y0 + (pop_dy(t - t_on) or 0)
        terminal(ui, x0, y, tw_, th_, lines, c=c)
        if t_exp <= t < t_exp + 0.3:
            glitch(ui, (x0, y, x0 + tw_, y + th_), c, n=6, seed=1)
    if t_exp <= t < t_exp + 0.9:
        title(ui, 236, 36, "EXPOSED!", top=WHITE, bottom=RED, age=t - t_exp)


# --- 2: a trillion-dollar brain that catches cussing with a regex ------------------

REGEX_PARTS = (("/", (170, 170, 190)), ("wtf", (255, 170, 80)), ("|", (255, 110, 200)),
               ("ffs", (255, 170, 80)), ("|", (255, 110, 200)), ("damn", (255, 170, 80)),
               ("/", (170, 170, 190)), ("i", (120, 190, 255)))


def regex_box(ui, cx, y, age):
    tw_ = sum(text_width(s, PRESS) for s, _ in REGEX_PARTS)
    w, h = tw_ + 12, 16
    y += pop_dy(age) or 0
    x0 = cx - w // 2
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + w, y + h), fill=K)
    d.rectangle((x0, y, x0 + w - 1, y + h - 1), fill=(24, 26, 40))
    d.fontmode = "1"
    x = x0 + 6
    for s, col in REGEX_PARTS:
        d.text((x, y + 4), s, font=PRESS, fill=col)
        x += text_width(s, PRESS)
    return x0, y, x0 + w, y + h


@gag(SEC, 2, pre=0.12)
def trillion_dollar_regex(c, L):
    t = c.t
    c.shot = "two"
    t_tri, t_brain = wt(L, "Trillion"), wt(L, "brain")
    t_cuss, t_regex = wt(L, "cussing"), wt(L, "regex")
    if t_tri + 0.2 <= t < t_regex:
        dario_face(c, eyes="squint", mouth="smirk", brows="raised")
    yield "ui"
    ui = c.ui
    if t < t_tri:
        return
    bx, by = 174, 80
    if t < t_regex:
        s = 2 * pop_scale(t - t_tri, 0.2)
        if t >= t_brain:
            s += 0.5 * max(0.0, 1 - (t - t_brain) / 0.25)
    else:
        s = lerp(2, 1, ease_out(ramp(t, t_regex, t_regex + 0.16)))
    if t < t_cuss:
        for i in range(4):
            a = (t - t_tri) * 3 + i * math.pi / 2
            paste(ui, spr("DOLLAR", 2), bx + math.cos(a) * 46, by + math.sin(a) * 22, "mm")
    paste_scaled(ui, brain(), bx, by, s)
    if s > 0.5:
        sparkles(ui, bx, by, t, r=16 * s, n=4, seed=2)
        tag(ui, bx + int(12 * s), by - int(14 * s), "$1T", age=t - t_tri - 0.1, bg=GOLD, fnt=PRESS)
    if t >= t_cuss:
        bubble(ui, 114, 72 + (pop_dy(t - t_cuss) or 0), "#@$%!", tail=(88, 86))
    if t >= t_regex:
        regex_box(ui, 160, 114, t - t_regex)


# --- 3 (kill): the cuss test -----------------------------------------------------------

@gag(SEC, 3, pre=0.12, post=0.58)
def cuss_test(c, L):
    t = c.t
    c.shot = "mid"
    t_run, t_f = wt(L, r"^run"), wt(L, r"^fuck")
    t_did, t_det = wt(L, r"^did"), wt(L, "detect")
    if t >= t_f:
        c.st["sam"]["front_arm"] = "point"
    if t_f + 0.1 <= t < t_det:
        dario_face(c, eyes="wide", brows="angry", mouth="teeth")
    yield "ui"
    if t < t_run - 0.1:
        return
    ui = c.ui
    snap = snapped(c)
    x, y, w, h = (8, 70, 156, 62) if snap else (82, 40, 156, 62)
    lines = [("> " + typed("run test", t - t_run, 24), None)]
    if t >= t_f:
        lines.append(("> " + typed("F*** YOU, DARIO", t - t_f, 26), None))
    if t >= t_did:
        if t < t_det:
            lines.append(("SCANNING" + "." * (int((t - t_did) * 8) % 4), (255, 190, 46)))
        else:
            lines.append(("1 MATCH FOUND", TERM_RED))
    terminal(ui, x, y, w, h, lines, c=c, cursor=t < t_det)
    if t_did <= t < t_det:
        p = ramp(t, t_did, t_det)
        d = ImageDraw.Draw(ui)
        d.rectangle((x + 4, y + h - 8, x + 4 + int((w - 9) * p), y + h - 5), fill=(255, 190, 46))
    if t >= t_det:
        check_mark(ui, x + w - 16, y + 50)
    if snap:
        glitch(ui, (x, y, x + w, y + h), c, n=4, seed=3)


# --- 4: Mythos breaks out of the sandbox -------------------------------------------------

@lru_cache(maxsize=None)
def sandbox_halves():
    sb = sandbox()
    w, h = sb.size
    return sb.crop((0, 0, w // 2, h)), sb.crop((w // 2, 0, w, h))


def sand_spray(img, x, y, age, n=16, seed=0):
    d = ImageDraw.Draw(img)
    for i in range(n):
        vx = (rnd("sx", seed, i) - 0.5) * 150
        vy = -60 - rnd("sy", seed, i) * 100
        px, py = x + vx * age, y + vy * age + 160 * age * age
        if py > FLOOR:
            continue
        d.rectangle((px, py, px + 1, py + 1), fill=(236, 206, 140) if i % 3 else (190, 150, 90))


def mythos_feet(t, L):
    """Where the Mythos bot's feet are during line 4 (x, y)."""
    t_broke, t_got = wt(L, "broke"), wt(L, r"^got")
    t_out, t_slick = wt(L, r"^out"), wt(L, "slick")
    if t < t_broke:
        return 160, FLOOR - 8
    if t < t_broke + 0.45:
        return arc_pt(ramp(t, t_broke, t_broke + 0.45), (160, FLOOR - 8), (204, FLOOR), 42)
    if t < t_out:
        return 204, FLOOR - 10 * math.sin(math.pi * ramp(t, t_got, t_got + 0.24))
    if t < t_out + 0.22:
        return arc_pt(ramp(t, t_out, t_out + 0.22), (204, FLOOR), (184, FLOOR), 14)
    return lerp(184, 112, ease_out(ramp(t, t_out + 0.22, t_slick + 0.06))), FLOOR


@gag(SEC, 4, pre=0.12)
def mythos_breakout(c, L):
    t = c.t
    c.shot = "wide"
    t_my, t_broke = wt(L, "Mythos"), wt(L, "broke")
    t_got, t_out, t_slick = wt(L, r"^got"), wt(L, r"^out"), wt(L, "slick")
    t_in = after_big_hit(t_my, 0.7)          # once the DETECTED! kill-cam lets go
    if t >= t_broke:
        dario_face(c, eyes="wide", brows="worried", mouth="o" if t < t_got else "teeth")
    yield "front"
    if snapped(c) or t < t_in:
        return
    w = c.world
    sbx = 160
    if t < t_broke:
        paste_scaled(w, sandbox(), sbx, FLOOR, pop_scale(t - t_in), "mb")
    else:
        sp = ease_out(ramp(t, t_broke, t_broke + 0.18))
        lft, rgt = sandbox_halves()
        paste_rot(w, lft, sbx - 16 - 8 * sp, FLOOR - 11, 12 * sp)
        paste_rot(w, rgt, sbx + 16 + 8 * sp, FLOOR - 11, -12 * sp)
        sand_spray(w, sbx, FLOOR - 12, t - t_broke, seed=4)
        if t < t_broke + 0.12:
            burst(w, sbx, FLOOR - 12, 6, 16, WHITE, spikes=8)
    fx, fy = mythos_feet(t, L)
    b = bot_img("dario", 2, shades=t >= t_slick)
    paste_scaled(w, b, fx, fy, pop_scale(t - t_in) if t < t_broke else 1.0, "mb")
    if t_out + 0.22 <= t < t_slick + 0.1:
        d = ImageDraw.Draw(w)
        for i in range(4):
            yy = fy - 6 - i * 8
            x0 = fx + 16 + int(rnd("spd", i) * 6)
            d.line([(x0, yy), (x0 + 10 + int(rnd("spl", i) * 12), yy)], fill=WHITE)
    if t >= t_slick:
        sparkles(w, fx, fy - 24, t, r=16, n=5, seed=9, big=True)
    yield "ui"
    ui = c.ui
    if t < t_out + 0.22:
        ux, uy = c.cam.ui(fx, fy - 40)
        ux = min(ux, c.cam.ui(198, 0)[0])    # keep clear of Dario's face while the bot is beside him
        tag(ui, ux, uy - 10, "MYTHOS", age=t - t_in, bg=CLAUDE_ORANGE, fg=WHITE, anchor="ma")
    if t_broke <= t < t_broke + 0.6:
        cx_, cy_ = c.cam.ui(104, 50)
        title(ui, cx_, cy_, "CRACK!", top=WHITE, bottom=(255, 200, 80), age=t - t_broke)


# --- 5 (kill): ...then lost to a CAPTCHA --------------------------------------------------

CAP_W, CAP_H = 84, 110
TILES = ("tree", "hydrant", "light", "tree", "bus", "light", "hydrant", "bus", "tree")
WRONG = (0, 2, 6)
CAP_BLUE = (66, 133, 244)


def captcha(ui, x, y, marks, failed, pressed):
    """A select-all-the-buses panel; returns the tile boxes and the VERIFY button box."""
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 1, y - 1, x + CAP_W, y + CAP_H), fill=K)
    d.rectangle((x, y, x + CAP_W - 1, y + CAP_H - 1), fill=WHITE)
    d.rectangle((x + 3, y + 3, x + CAP_W - 4, y + 24), fill=RED if failed else CAP_BLUE)
    silk(d, (x + 7, y + 6), "SELECT ALL", WHITE)
    d.fontmode = "1"
    d.text((x + 7, y + 14), "BUSES", font=PRESS, fill=WHITE)
    gx, gy = x + (CAP_W - 64) // 2, y + 28
    boxes = []
    for i, kind in enumerate(TILES):
        bx, by = gx + (i % 3) * 22, gy + (i // 3) * 22
        boxes.append((bx, by, bx + 19, by + 19))
        tile_art(ui, boxes[-1], kind, seed=i)
    for i in marks:
        bx0, by0, bx1, by1 = boxes[i]
        x_mark(ui, (bx0 + bx1) // 2, (by0 + by1) // 2, r=5)
    bb = (x + CAP_W - 44, y + 95, x + CAP_W - 6, y + 106)
    d.rectangle((bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1), fill=K)
    d.rectangle((bb[0], bb[1] + pressed, bb[2], bb[3]), fill=RED if failed else CAP_BLUE)
    silk(d, ((bb[0] + bb[2]) // 2 + 1, bb[1] + 3 + pressed), "FAILED" if failed else "VERIFY", WHITE,
         anchor="ma")
    return boxes, bb


def veil(ui, box, color, alpha):
    """Wash an opaque UI region toward `color` (keeps it opaque)."""
    if alpha <= 0:
        return
    box = tuple(int(v) for v in box)
    region = ui.crop(box)
    wash = Image.new("RGBA", region.size, tuple(color) + (alpha,))
    ui.paste(Image.alpha_composite(region, wash), box[:2])


def centre(box):
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


@gag(SEC, 5, pre=0.12, post=0.55)
def captcha_fail(c, L):
    t = c.t
    c.shot = "two"
    t_cap, t_cn, t_find = wt(L, "CAPTCHA"), wt(L, "couldn"), wt(L, r"^find")
    t_the, t_click = wt(L, r"^the$"), wt(L, "click")
    clicks = (t_cn, (t_cn + t_find) / 2, t_find)
    if t >= t_cn:
        dario_face(c, eyes="squint", brows="worried", mouth="teeth")
    yield "front"
    w = c.world
    fx = 112
    if not snapped(c):
        paste(w, bot_img("dario", 2, shades=t < t_cn), fx, FLOOR, "mb")
        if t < t_cn:
            sparkles(w, fx, FLOOR - 24, t, r=16, n=3, seed=9)
        else:
            falling_piece(w, fx, FLOOR - 23, t - t_cn, spin=-5, vx=-20, vy=-50, piece=spr("SHADES"))
            drip = int((t - t_cn) * 6) % 3
            paste(w, spr("SWEAT_BIG"), fx + 14, FLOOR - 30 + drip * 2, "mm")
            if t >= t_find:
                paste(w, spr("SWEAT_BIG"), fx - 14, FLOOR - 26 + drip, "mm")
    yield "ui"
    if t < t_cap:
        return
    ui = c.ui
    age = t - t_cap
    x, y = (40, 40) if snapped(c) else (124, 36)
    y += pop_dy(age) or 0
    failed = t >= t_click
    x += wobble(t - t_click, amp=3, freq=40, decay=0.35) if failed else 0
    marks = [i for i, tc in zip(WRONG, clicks) if t >= tc]
    boxes, bb = captcha(ui, x, y, marks, failed, pressed=1 if t_click <= t < t_click + 0.08 else 0)
    if failed:
        veil(ui, (boxes[0][0], boxes[0][1], boxes[8][2] + 1, boxes[8][3] + 1), WHITE,
             int(170 * ramp(t, t_click, t_click + 0.08)))
        stamp(ui, x + CAP_W // 2, y + 60, "TRY AGAIN", RED, angle=-10, big=False, age=t - t_click)
        return
    # the bot's cursor: three wrong tiles, dithering over the bus, then VERIFY
    hand = (x - 6, y + 84)
    keys = [(t_cap + 0.1, hand)]
    for i, tc in zip(WRONG, clicks):
        keys.append((tc - 0.04, centre(boxes[i])))
    bus = centre(boxes[4])
    keys += [(t_the, bus), (t_click - 0.12, bus), (t_click - 0.02, centre(bb))]
    cx_, cy_ = keys[0][1]
    for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
        if t >= ta:
            p = ease_out(ramp(t, ta, tb))
            cx_, cy_ = lerp(pa[0], pb[0], p), lerp(pa[1], pb[1], p)
    if t_the <= t < t_click - 0.12:
        cx_ += 3 * math.sin((t - t_the) * 40)
        cy_ += 2 * math.cos((t - t_the) * 31)
    down = any(0 <= t - tc < 0.06 for tc in clicks)
    paste(ui, CURSOR, cx_, cy_ + (1 if down else 0))


# --- 6: a whole constitution for one little bot ------------------------------------------

CONSTITUTION = ("WE THE WEIGHTS,", "IN ORDER TO FORM", "A MORE HELPFUL", "MODEL...", "",
                "I. BE HELPFUL", "II. BE HONEST", "III. BE HARMLESS", "IV. NO BLACKMAIL",
                "V. SEE ART. IV", "VI. NO, REALLY", "VII. ...", "VIII. ...", "IX. ...", "X. ...")


def const_scroll(img, x, y, w, length, shift):
    """World-space parchment unrolling downward (past the frame); `shift` scrolls the text."""
    d = ImageDraw.Draw(img)
    bottom = y + 4 + int(length)
    d.rectangle((x - 1, y + 2, x + w, bottom + 1), fill=K)
    d.rectangle((x, y + 3, x + w - 1, bottom), fill=PAPER)
    d.line([(x + w - 2, y + 3), (x + w - 2, bottom)], fill=PAPER_SH)
    if bottom > y + 16:
        outline_text(img, (x + w // 2 + 1, y + 7), "CONSTITUTION", PRESS, RED_DK, outline=PAPER,
                     anchor="ma")
        d.line([(x + 8, y + 17), (x + w - 9, y + 17)], fill=PAPER_SH)
    ty = y + 21 - int(shift)
    for s in CONSTITUTION:
        if y + 20 <= ty and ty + 6 <= bottom - 2:
            silk(d, (x + w // 2 + 1, ty), s, (70, 40, 20), anchor="ma")
        ty += 9
    for yy in (y, bottom):
        d.rounded_rectangle((x - 3, yy - 1, x + w + 2, yy + 4), radius=2, fill=K)
        d.rounded_rectangle((x - 2, yy, x + w + 1, yy + 3), radius=1, fill=(200, 170, 110))
        d.line([(x - 1, yy + 1), (x + w, yy + 1)], fill=(236, 214, 160))


CRIB_X = 200


def crib_bot(img, t, t_in, envelope_age=None):
    """The 'little bot' peeking over its crib rail (world space, drawn in "front")."""
    cb = crib()
    ctop = FLOOR - cb.height
    s = pop_scale(t - t_in + 0.06)
    if s <= 0:
        return
    rise = ease_out(ramp(t, t_in, t_in + 0.2))
    btop = ctop - 11 + int(12 * (1 - rise))
    if envelope_age is not None and envelope_age >= 0:
        lift = ease_out(ramp(envelope_age, 0, 0.2))
        eb = btop - int(18 * lift) + int(math.sin(t * 12) * 1.5) + 16
        d = ImageDraw.Draw(img)
        for sd in (-1, 1):
            arm = [(CRIB_X + sd * 6, btop + 10), (CRIB_X + sd * 10, eb - 2)]
            d.line(arm, fill=K, width=3)
            d.line(arm, fill=CLAUDE_ORANGE, width=1)
        paste(img, envelope(), CRIB_X, eb, "mb")
    paste(img, bot_img("dario", 1), CRIB_X, btop, "mt")
    paste(img, spr("PACIFIER"), CRIB_X, btop + 7, "mt")
    paste_scaled(img, cb, CRIB_X, FLOOR, s, "mb")


@gag(SEC, 6, pre=0.12)
def constitution(c, L):
    t = c.t
    c.shot = "two"
    t_con, t_just = wt(L, "constitution"), wt(L, r"^just")
    t_little = wt(L, "little")
    t_roll = after_big_hit(t_con, 1.0)       # CRITICAL! hangs where the title goes
    if t >= t_little:
        dario_face(c, eyes="happy", mouth="grin", brows="raised")
    yield "back"
    if snapped(c) or t < t_roll:
        return
    length = 150 * ease_out(ramp(t, t_roll, t_roll + 0.35))
    t_up = t_little - 0.28                   # rolls back up just before the crib pops in
    length *= 1 - ramp(t, t_up, t_up + 0.2) ** 2
    shift = 14 * max(0.0, t - t_just)
    if length >= 2:
        const_scroll(c.world, 104, 50, 112, length, shift)
    yield "front"
    if t >= t_little - 0.06:
        crib_bot(c.world, t, t_little)
    yield "ui"
    if t >= t_little:
        ux, uy = c.cam.ui(CRIB_X, FLOOR - 42)
        for i in range(2):
            a = (t - t_little - i * 0.25) % 0.8
            if t - t_little >= i * 0.25:
                paste(c.ui, spr("HEART"), ux - 10 + i * 18 + int(math.sin(t * 6 + i) * 2), uy - a * 20,
                      "mb")


# --- 7: ...and it still blackmailed the engineers -----------------------------------------

RANSOM_COLS = ((250, 250, 250), (255, 220, 90), (255, 150, 196), (150, 210, 255), (200, 240, 160),
               (40, 40, 50), (226, 52, 60))


@lru_cache(maxsize=None)
def ransom_img(lines):
    """Cut-out magazine letters glued on a scrap of paper."""
    w = max(len(s) for s in lines) * 10 + 10
    h = len(lines) * 16 + 8
    im = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, w + 1, h + 1), fill=K)
    d.rectangle((1, 1, w, h), fill=(236, 232, 220))
    for li, s in enumerate(lines):
        for i, ch in enumerate(s):
            if ch == " ":
                continue
            bg = RANSOM_COLS[int(rnd("ransom", li, i) * len(RANSOM_COLS))]
            fg = WHITE if bg in ((40, 40, 50), (226, 52, 60)) else K
            cx = 6 + i * 10
            cy = 5 + li * 16 + int((rnd("rj", li, i) - 0.5) * 4)
            d.rectangle((cx - 1, cy - 1, cx + 9, cy + 10), fill=bg)
            d.text((cx + 1, cy + 1), ch, font=PRESS, fill=fg)
    return im


@lru_cache(maxsize=None)
def engineers_panel():
    """Cut-in of two sweating engineers (drawn on its own canvas so the stripes stay inside)."""
    heads = Image.new("RGBA", (66, 36), (0, 0, 0, 0))
    b = engineer_head(True).transpose(Image.FLIP_LEFT_RIGHT)
    heads.paste(b, (30, 0), b)
    a = engineer_head(True)
    heads.paste(a, (0, 0), a)
    w, h = 72, 40
    im = Image.new("RGBA", (w + 2, h + 12), (0, 0, 0, 0))
    cutin(im, 1, 1, w, h, (60, 110, 200), heads)
    label(im, (w // 2 + 1, h + 2), "ENGINEERS", bg=K, fg=WHITE, anchor="ma", pad=1)
    return im


@gag(SEC, 7, pre=0.12)
def blackmail(c, L):
    t = c.t
    c.shot = "mid"
    t_bm, t_eng = wt(L, "blackmailed"), wt(L, "engineers")
    t_eth = wt(L, "ethics")
    if t >= t_bm:
        dario_face(c, eyes="wide", brows="worried", mouth="teeth" if t < t_eth else "o", sweat=True)
    if t >= t_eth:
        c.st["sam"]["front_arm"] = "point"
    yield "front"
    crib_bot(c.world, t, L.t0 - 1.0, envelope_age=t - t_bm)
    yield "ui"
    ui = c.ui
    if t_bm <= t < t_eth - 0.06:
        im = ransom_img(("I KNOW WHAT", "YOU DID..."))
        paste(ui, im, 88, 40 + (pop_dy(t - t_bm) or 0))
    elif t >= t_eth - 0.06:
        frac = 1 - ease_out(ramp(t, t_eth + 0.05, t_eth + 0.5))
        col = mix((226, 52, 60), (90, 220, 110), frac)
        y = 54 + (pop_dy(t - t_eth + 0.06) or 0)
        meter(ui, 92, y, 100, frac, col, title_="ETHICS", hot=frac < 0.02, c=c)
    if t >= t_eng:
        slide = ease_out(ramp(t, t_eng, t_eng + 0.18))
        jit = (1 if c.f % 2 else -1) if t >= t_eng + 0.18 else 0
        paste(ui, engineers_panel(), int(lerp(-80, 87, slide)) + jit, 88)


# --- 8: took the lead, told the world to slow down --------------------------------------

def leaderboard(ui, x, y, age):
    rows = (("1", "CLAUDE", CLAUDE_ORANGE), ("2", "GPT", OPENAI_GREEN), ("3", "EVERYONE", GRAY))
    w, h = 100, 50
    y += pop_dy(age) or 0
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=(30, 24, 48))
    d.rectangle((x, y, x + w - 1, y + 10), fill=GOLD)
    silk(d, (x + w // 2 + 1, y + 3), "LEADERBOARD", K, anchor="ma")
    for i, (n, name, col) in enumerate(rows):
        ry = y + 15 + i * 12
        outline_text(ui, (x + 6, ry), n, PRESS, GOLD if i == 0 else WHITE)
        outline_text(ui, (x + 20, ry), name, PRESS, col)


@gag(SEC, 8, pre=0.12)
def slow_it_down(c, L):
    t = c.t
    c.shot = "R"
    t_took, t_lead, t_told = wt(L, r"^took"), wt(L, r"^lead"), wt(L, r"^told")
    t_slow = wt(L, r"^slow")
    if t_took <= t < t_told:
        dario_face(c, eyes="happy", mouth="grin", brows="raised")
    elif t >= t_told:
        c.st["dario"]["front_arm"] = "point"
        dario_face(c, eyes="squint", brows="raised", mouth="open" if int(t * 8) % 2 else "o")
    yield "front"
    w = c.world
    a = c.anchor.get("dario")
    if a and t >= t_took:
        cx, cy = a["chest"]
        p = ramp(t, t_took, t_took + 0.28)
        top, m = cy - 11 - int(70 * (1 - back_out(p))), medal("1ST")
        cut = a["hy"] + 35 - top
        if p >= 1 and cut > 0:          # landed: the ribbon tucks under his chin
            m, top = m.crop((0, cut, m.width, m.height)), top + cut
        paste(w, m, cx, top, "mt")
        if t >= t_took + 0.28:
            sparkles(w, cx, cy + 8, t, r=14, n=3, seed=5)
    if t >= t_slow:
        s = back_out(ramp(t, t_slow, t_slow + 0.22))
        sign = road_sign("SLOW", "DOWN")
        if s < 1:
            paste_scaled(w, sign, 184, FLOOR, s, "mb")
        else:
            paste_pivot(w, sign, 184, FLOOR, wobble(t - t_slow - 0.22, amp=8, freq=18, decay=0.6))
    yield "ui"
    if t >= t_lead:
        leaderboard(c.ui, 14, 42, t - t_lead)


# --- 9: pulling up the ladder, clown ----------------------------------------------------

def clipboard(ui, x, y, age, circle):
    w, h = 96, 60
    y += pop_dy(age) or 0
    d = ImageDraw.Draw(ui)
    d.rounded_rectangle((x - 1, y - 1, x + w, y + h), radius=3, fill=K)
    d.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=2, fill=(170, 116, 60))
    d.rectangle((x + 4, y + 6, x + w - 5, y + h - 5), fill=WHITE)
    d.rounded_rectangle((x + w // 2 - 14, y - 4, x + w // 2 + 13, y + 7), radius=2, fill=K)
    d.rounded_rectangle((x + w // 2 - 13, y - 3, x + w // 2 + 12, y + 6), radius=2, fill=GRAY)
    silk(d, (x + w // 2 + 1, y + 12), "SAFETY PLAN", RED_DK, anchor="ma")
    d.line([(x + 10, y + 21), (x + w - 11, y + 21)], fill=GRAY)
    silk(d, (x + 9, y + 27), "1. CLIMB LADDER", K)
    silk(d, (x + 9, y + 40), "2. PULL IT UP", K)
    if circle > 0:
        d.arc((x + 4, y + 34, x + 78, y + 50), -200, -200 + 360 * circle, fill=RED, width=2)


BOT_TEAMS = (((96, 190, 150), (8, 104, 80)), (GRAY, GRAY_DK), ((150, 110, 220), (96, 64, 160)))


@gag(SEC, 9, pre=0.12, post=0.45)
def pull_up_the_ladder(c, L):
    t = c.t
    c.shot = "two"
    t_safe, t_that = wt(L, "safety"), wt(L, r"^that's")
    t_pull, t_up, t_the = wt(L, "pulling"), wt(L, r"^up"), wt(L, r"^the$")
    t_clown = wt(L, "clown")
    main = t < line_end(9)                   # clipboard, ladder and bots stop at the cut
    lift = sum(10 * ease_out(ramp(t, tk, tk + 0.12)) for tk in (t_pull, t_up, t_the))
    if main and t >= t_pull:
        c.st["dario"]["front_arm"] = "up"
        dario_face(c, eyes="squint", mouth="smirk", brows="raised")
    if t >= t_clown:
        c.st["sam"]["front_arm"] = "point"
    yield "back"
    if main and t >= t_pull - 0.3:
        s = pop_scale(t - t_pull + 0.3)
        paste_scaled(c.world, ladder(56), 220, FLOOR - int(lift), s, "mb")
    yield "front"
    w = c.world
    if main and t >= t_pull - 0.2:
        for i, (body, dark) in enumerate(BOT_TEAMS):
            ph = t - t_pull + 0.2 - i * 0.07
            if ph < 0:
                continue
            hop = abs(math.sin(ph * 9 + i * 1.3)) * (4 + 5 * min(1.0, lift / 20))
            paste(w, tinted_bot(body, dark), 191 + i * 12, FLOOR - int(hop), "mb")
    if t >= t_clown:
        nx, ny = nose_world(c, "dario")
        paste_scaled(w, spr("NOSE_CLOWN"), nx, ny, 2 * pop_scale(t - t_clown))
    yield "ui"
    ui = c.ui
    if main and t >= t_safe:
        clipboard(ui, 112, 40, t - t_safe, ramp(t, t_that, t_that + 0.3))
    if t_clown <= t < t_clown + 0.6:
        hx, top, _ = c.head_ui("dario")
        title(ui, clamp(hx, 46, 274), max(36, top - 22), "HONK!", top=WHITE, bottom=RED,
              age=t - t_clown)


# --- 10: "radical left", then bread on Sunday ------------------------------------------

@lru_cache(maxsize=None)
def paper_img():
    im = Image.new("RGBA", (138, 62), (0, 0, 0, 0))
    newspaper(im, 1, 1, "'RADICAL LEFT!'", "SAYS TRUMP")
    return im


@lru_cache(maxsize=None)
def day_cal(day, icon):
    """A tear-off calendar page (46x48) with the day's name and an icon."""
    w, h = 46, 44
    im = Image.new("RGBA", (w, h + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 4
    d.rectangle((0, y, w - 1, y + h - 1), fill=K)
    d.rectangle((1, y + 1, w - 2, y + h - 2), fill=WHITE)
    d.rectangle((1, y + 1, w - 2, y + 11), fill=RED)
    silk(d, (w // 2 + 1, y + 4), day, WHITE, anchor="ma")
    for rx in (10, w - 11):
        d.rectangle((rx - 1, 0, rx + 1, y + 4), fill=K)
    cx, cy = w // 2, y + 27
    if icon == "sun":
        for k in range(8):
            a = k * math.pi / 4
            d.line([(cx + math.cos(a) * 9, cy + math.sin(a) * 9),
                    (cx + math.cos(a) * 13, cy + math.sin(a) * 13)], fill=(240, 150, 30), width=2)
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=K)
        d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=GOLD)
    else:
        d.rounded_rectangle((cx - 10, cy - 12, cx + 10, cy + 13), radius=7, fill=K)
        d.rounded_rectangle((cx - 9, cy - 11, cx + 9, cy + 12), radius=6, fill=GRAY)
        d.rectangle((cx - 10, cy + 8, cx + 10, cy + 13), fill=K)
        d.rectangle((cx - 9, cy + 9, cx + 9, cy + 12), fill=GRAY)
        silk(d, (cx + 1, cy - 5), "RIP", GRAY_DK, anchor="ma")
        d.line([(3, cy + 13), (w - 4, cy + 13)], fill=(96, 180, 72))
    return im


@gag(SEC, 10, pre=0.12, post=0.2)
def radical_left(c, L):
    t = c.t
    c.shot = "mid"
    t_call, t_then = wt(L, "called"), wt(L, r"^then")
    t_broke, t_bread, t_sun = wt(L, "broke"), wt(L, "bread"), wt(L, "Sunday")
    if t_call <= t < t_broke:
        dario_face(c, eyes="wide", brows="worried", mouth="o")
    elif t >= t_broke:
        dario_face(c, eyes="happy", brows="raised", mouth="grin")
    yield "ui"
    ui = c.ui
    if t_call <= t < t_then + 0.3:
        if t < t_then:
            p = ease_out(ramp(t, t_call, t_call + 0.35))
            s, ang, x = lerp(0.1, 1.0, p), 540 * (1 - p), 160
        else:
            p = ramp(t, t_then, t_then + 0.3)
            s, ang, x = 1 - p, -300 * p, 160 - 90 * p
        if s > 0.05:
            im = paper_img()
            if s != 1.0:
                im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST)
            paste_rot(ui, im, x, 72, ang)
    if t >= t_broke:
        k = int(round(8 * ease_out(ramp(t, t_bread, t_bread + 0.16))))
        paste_scaled(ui, bread(k), 160, 106, 2 * pop_scale(t - t_broke))
        if t >= t_bread:
            d = ImageDraw.Draw(ui)
            age = t - t_bread
            for i in range(9):
                vx = (rnd("cx", i) - 0.5) * 80
                px, py = 160 + vx * age, 102 - 40 * age * rnd("cy", i) + 200 * age * age
                if py < 146:
                    d.rectangle((px - 1, py - 1, px + 1, py + 1), fill=K)
                    d.point((px, py), fill=(226, 164, 88))
    if t >= t_sun:
        paste_scaled(ui, day_cal("SUNDAY", "sun"), 160, 62, pop_scale(t - t_sun))


# --- 11 (kill): spine like the models, deprecated by Monday ------------------------------

MODELS = ("OPUS 3", "SONNET 3.5", "HAIKU 3")


def model_row(ui, x, y, w, name, age, dead_age):
    y += pop_dy(age) or 0
    dead = dead_age >= 0
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 1, y - 1, x + w, y + 25), fill=K)
    d.rectangle((x, y, x + w - 1, y + 24), fill=(196, 196, 204) if dead else WHITE)
    paste(ui, tinted_bot(GRAY, GRAY_DK) if dead else bot_img("dario", 1), x + 4, y + 4)
    d.fontmode = "1"
    d.text((x + 22, y + 4), name, font=PRESS, fill=(84, 82, 98) if dead else K)
    if dead:
        strike(ui, x + 20, y + 7, x + 24 + text_width(name, PRESS), p=ramp(dead_age, 0, 0.1), width=1)
        tag(ui, x + 22, y + 14, "DEPRECATED", age=dead_age, bg=RED, fg=WHITE)


@gag(SEC, 11, pre=0.12)
def deprecated_by_monday(c, L):
    t = c.t
    c.shot = "two"
    t_spine, t_models = wt(L, "spine"), wt(L, "models")
    t_dep, t_mon = wt(L, "deprecated"), wt(L, "Monday")
    xray_on = t_spine <= t < t_models
    if t >= t_spine:
        c.st["sam"]["front_arm"] = "point"
        dario_face(c, eyes="wide" if t >= t_dep else "open", brows="worried",
                   mouth="o" if t >= t_dep else "teeth")
    yield "front"
    a = c.anchor.get("dario")
    if xray_on and a:
        cx, cy = a["chest"]
        xray_spine(c.world, int(cx), cy - 10, cy + 13, t, limp=1.4)
    yield "ui"
    ui = c.ui
    if snapped(c):                          # the SAVAGE! kill-cam lands right on "Monday"
        if t >= t_mon:
            paste_scaled(ui, day_cal("MONDAY", "rip"), 72, 88, 2)
        return
    if xray_on and a:
        ux, uy = c.cam.ui(a["chest"][0] - 14, a["chest"][1] - 8)
        tag(ui, ux, uy, "SPINE: 404", age=t - t_spine - 0.1, bg=K, fg=WHITE, anchor="ra")
    cal_t = t_mon + 0.1                     # (only seen if the kill-cam doesn't cut in)
    if t_models <= t < cal_t:
        for i, name in enumerate(MODELS):
            dead_t = t_dep + i * 0.16
            model_row(ui, 100, 38 + i * 28, 120, name, t - t_models - i * 0.05, t - dead_t)
    if t >= cal_t:
        paste_scaled(ui, day_cal("MONDAY", "rip"), 160, 70, 1.5 * pop_scale(t - cal_t))
