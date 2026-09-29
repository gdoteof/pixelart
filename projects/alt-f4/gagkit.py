"""Shared toolkit for the per-line gags: registration, timing helpers and extra props.

A gag is a generator `fn(c, L)` (c: video.Ctx, L: video.LineRef). Code before
the first `yield` runs at setup time; each `yield "<phase>"` hands control back
until that drawing phase comes round (see video.py).
"""
import inspect
import math
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import timeline as TL
import video as V
from characters import HH, HW, SKIN, SKIN_SH, draw_character, render_head
from characters import _grow as grow_mask
from engine import (CLAUDE_ORANGE, GOLD, H, NEON_CYAN, NEON_PINK, OPENAI_GREEN, W, dither,
                    dither_poly, dither_rect, mask, mix, outline_text, text_width)
from props import (BELL, BLUE, BLUE_DK, BUG, DIZZY, GRAY, GRAY_DK, HAND_UP, HEART, HEART_CRACK,
                   MUSTACHE, NOSE_CLOWN, PAPER, PAPER_SH, PRESS16, PRESS24, RED, RED_DK, SPARKLE,
                   SPARKLE_S, STAR5, SWEAT_BIG, TEAM, WHITE, Z_ROWS, Prop, ascii_sprite, back_out,
                   big_text, book, bot, bread, brain, bubble, bubble_sheet, calendar, cannon,
                   caption, chart_frame, chat_window, check_mark, chicken, confetti, crib, cutin,
                   ease_out, envelope, fedora, flames, gavel, grandma_head, hugging_face, keycap,
                   label, ladder, laurel, loot_bag, map_prop, medal, newspaper, paper, paste,
                   pentagon, pin, police_tape, radio, road_sign, sandbox, scroll, shelter,
                   signal_bars, smoke, stamp, thought, tile_art, tile_grid, uncle_sam_hat,
                   waveform, win95, x_mark)
from scene import CURSOR, FEET_Y, K, PRESS, SILK, WALL_BOTTOM, bevel, burst, glow, silk

FPS = TL.FPS
rnd, clamp, lerp, ramp, scaled, pop_dy = V.rnd, V.clamp, V.lerp, V.ramp, V.scaled, V.pop_dy
text_img = V.text_img
OTHER = V.OTHER
TEAM_C = V.TEAM                      # who -> team colour
SAFE_TOP, SAFE_BOTTOM = 34, 146      # UI rows clear of the HUD and the karaoke band

GAGS = {}


def gag(sec, idx, pre=0.15, post=0.0):
    """Register a per-line gag generator for lyric line `idx` of section `sec`."""
    def reg(fn):
        assert inspect.isgeneratorfunction(fn), f"{fn.__name__} must be a generator"
        GAGS[(sec, idx)] = (fn, pre, post)
        return fn
    return reg


# --- timing -----------------------------------------------------------------

def wt(L, pat, n=0, which="t0"):
    """Time of the n-th word of line L matching regex `pat` (case-insensitive)."""
    k = 0
    for w in L.words:
        if re.search(pat, w["w"], re.I):
            if k == n:
                return w[which]
            k += 1
    raise KeyError(f"{pat!r} #{n} not in {L.ln['text']!r}")


def calm(c, who, window=0.6):
    """True unless `who` has just taken a hit (so gags don't stomp the hit reaction)."""
    return TL.last_hit(c.t, target=who, window=window) is None


def blink(c, hz=4.0):
    return int(c.t * hz * 2) % 2 == 0


def wobble(age, amp=2.0, freq=30.0, decay=0.4):
    if age < 0:
        return 0
    return int(round(math.sin(age * freq) * amp * max(0.0, 1 - age / decay)))


def pop_scale(age, dur=0.16):
    return 0.0 if age < 0 else max(0.0, back_out(age / dur))


def impact(c, age, shake=8.0, flash=0.0, dur=0.3):
    """Screen shake (and optional flash) for an impact that happened `age` seconds ago."""
    if 0 <= age < dur:
        c.add_shake(shake * (1 - age / dur))
    if flash and 0 <= age < 2 / FPS:
        c.add_flash(flash)


def arc_pt(p, a, b, lift):
    """Point along a parabolic hop from a to b that rises `lift` pixels at the middle."""
    return lerp(a[0], b[0], p), lerp(a[1], b[1], p) - lift * 4 * p * (1 - p)


# --- drawing helpers --------------------------------------------------------

def paste_scaled(dst, img, x, y, s=1.0, anchor="mm"):
    if s <= 0.04:
        return
    if s != 1.0:
        img = img.resize((max(1, int(round(img.width * s))), max(1, int(round(img.height * s)))),
                         Image.NEAREST)
    paste(dst, img, x, y, anchor)


def paste_rot(dst, img, x, y, angle, anchor="mm"):
    if angle:
        img = img.rotate(angle, resample=Image.NEAREST, expand=True)
    paste(dst, img, x, y, anchor)


@lru_cache(maxsize=None)
def spr(name, scale=1, **pal):
    rows = {"STAR5": STAR5, "SPARKLE": SPARKLE, "SPARKLE_S": SPARKLE_S, "HEART": HEART,
            "HEART_CRACK": HEART_CRACK, "BELL": BELL, "BUG0": BUG[0], "BUG1": BUG[1],
            "HAND_UP": HAND_UP, "MUSTACHE": MUSTACHE, "NOSE_CLOWN": NOSE_CLOWN,
            "SWEAT_BIG": SWEAT_BIG, "Z": Z_ROWS, "DIZZY": DIZZY}.get(name) or EXTRA_SPRITES[name]
    img = ascii_sprite(rows, **pal)
    return scaled(img, scale) if scale != 1 else img


@lru_cache(maxsize=None)
def bot_img(team="dario", scale=2, shades=False, chain=False, mask_=False, flip=False):
    img = bot(team, shades, chain, mask_)
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return scaled(img, scale) if scale != 1 else img


def title(ui, x, y, s, fnt=PRESS16, top=WHITE, bottom=GOLD, age=0.0, anchor="ma", blink_after=None,
          c=None):
    """Arcade title text that drops in (pop) when it first appears."""
    if age < 0:
        return 0
    if blink_after is not None and c is not None and age > blink_after and not blink(c, 5):
        return 0
    return big_text(ui, (x, y + (pop_dy(age) or 0)), s, fnt, top=top, bottom=bottom, anchor=anchor)


def tag(ui, x, y, s, age=0.0, bg=WHITE, fg=K, fnt=None, anchor="la", pad=2):
    if age < 0:
        return None
    return label(ui, (x, y + (pop_dy(age) or 0)), s, bg=bg, fg=fg, fnt=fnt, anchor=anchor, pad=pad)


def strike(ui, x0, y, x1, p=1.0, color=RED, width=3):
    """A hand-drawn strike-through line, drawn left to right as p goes 0 -> 1."""
    if p <= 0:
        return
    d = ImageDraw.Draw(ui)
    xe = x0 + (x1 - x0) * min(1.0, p)
    d.line([(x0, y + 1), (xe, y - 1)], fill=K, width=width + 2)
    d.line([(x0, y + 1), (xe, y - 1)], fill=color, width=width)


def arrow(ui, x0, y0, x1, y1, color=GOLD, width=3, head=6):
    d = ImageDraw.Draw(ui)
    a = math.atan2(y1 - y0, x1 - x0)
    tip = [(x1, y1), (x1 - head * math.cos(a - 0.5), y1 - head * math.sin(a - 0.5)),
           (x1 - head * math.cos(a + 0.5), y1 - head * math.sin(a + 0.5))]
    d.line([(x0, y0), (x1, y1)], fill=K, width=width + 2)
    d.polygon([(x + (x - x1) * 0.25, y + (y - y1) * 0.25) for x, y in tip], fill=K)
    d.line([(x0, y0), (x1 - 2 * math.cos(a), y1 - 2 * math.sin(a))], fill=color, width=width)
    d.polygon(tip, fill=color)


def sparkles(img, cx, cy, t, r=18, n=4, seed=0, big=False):
    for i in range(n):
        ph = (t * 1.7 + i / n + rnd("spk", seed, i) * 0.3) % 1.0
        if ph > 0.7:
            continue
        a = rnd("spa", seed, i) * 2 * math.pi + i
        rr = r * (0.6 + 0.4 * rnd("spr", seed, i))
        s = spr("SPARKLE" if big and ph < 0.35 else "SPARKLE_S")
        paste(img, s, cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.7, "mm")


def glow_box(img, box, color, density=0.35):
    """Soft dithered glow around a rectangle (works on world and UI layers)."""
    x0, y0, x1, y1 = box
    m = mask(lambda d: d.rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), radius=5, fill=255))
    dither(img, m * density, color, blend=0.5 if img.mode == "RGB" else 1.0)


# --- characters as sprites ----------------------------------------------------

@lru_cache(maxsize=128)
def char_sprite(who, facing=1, mouth="closed", brows="neutral", eyes="open", back_arm="down",
                front_arm="down"):
    """A character drawn on its own 80x100 RGBA canvas, feet at (40, 96)."""
    layer = Image.new("RGBA", (80, 100), (0, 0, 0, 0))
    draw_character(layer, who, 40, 96, facing=facing, mouth=mouth, brows=brows, eyes=eyes,
                   back_arm=back_arm, front_arm=front_arm)
    return layer


def head_world(c, who):
    """(centre x, top y, bottom y) of a character's head in world pixels (any phase)."""
    x0, y0, x1, y1 = c.head_box(who)
    return (x0 + x1) / 2, y0, y1


def nose_world(c, who):
    s = c.st[who]
    x0, y0, _, _ = c.head_box(who)
    nx = x0 + (19 if s["facing"] == 1 else HW - 1 - 19)
    return nx, y0 + 25


# --- extra sprites --------------------------------------------------------------

EXTRA_SPRITES = {
    "NURSE_CAP": [
        "....kkkkkkkk....",
        "...kwwwwwwwwk...",
        "..kwwwwrrwwwwk..",
        "..kwwwrrrrwwwk..",
        "..kwwwwrrwwwwk..",
        ".kwwwwwwwwwwwwk.",
        "kWWWWWWWWWWWWWWk",
        ".kkkkkkkkkkkkkk.",
    ],
    "HALO": [
        "..kkkkkkkkkkkk..",
        ".kyyyyyyyyyyyyk.",
        "kyYk........kYyk",
        ".kyyyyyyyyyyyyk.",
        "..kkkkkkkkkkkk..",
    ],
    "SHADES": [
        "kkkkkkkkkkkkkkkkk",
        "kdddddkkkkkdddddk",
        ".kdddk.....kdddk.",
        "..kkk.......kkk..",
    ],
    "PACIFIER": [".kkk.", "kpppk", ".kPk.", "..k.."],
    "MOON": [
        "...kkkk...",
        ".kkyyyk...",
        "kyyyk.....",
        "kyyk......",
        "kyyk......",
        "kyyyk.....",
        ".kkyyyk...",
        "...kkkk...",
    ],
    "DOLLAR": [
        "..kk..",
        ".kyyk.",
        "kyykkk",
        ".kyyk.",
        "kkkyyk",
        ".kyyk.",
        "..kk..",
    ],
    "PEN": [
        "..........kk",
        ".........kbk",
        "........kbk.",
        ".......kbk..",
        "......kbk...",
        ".....kbk....",
        "....kGk.....",
        "...kGk......",
        "..kkk.......",
        ".kk.........",
    ],
}


# --- neon text ------------------------------------------------------------------

NEON_EXTRA = {
    "O": [[(1, 0), (9, 0), (10, 1), (10, 14), (9, 15), (1, 15), (0, 14), (0, 1), (1, 0)]],
    "P": [[(1, 15), (1, 0), (9, 0), (10, 1), (10, 6), (9, 7), (1, 7)]],
    "E": [[(10, 0), (1, 0), (1, 15), (10, 15)], [(1, 7), (8, 7)]],
    "N": [[(1, 15), (1, 0), (10, 15), (10, 0)]],
}


def neon_word(img, s, x0, top, color, adv=15, frame=None, frame_color=NEON_CYAN):
    """Neon tubes spelling `s` (glyphs O P E N plus the sign's own) with an optional frame box."""
    from scene import NEON_GLYPHS
    glyphs = dict(NEON_GLYPHS, **NEON_EXTRA)
    tube = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(tube)
    for i, ch in enumerate(s):
        for stroke in glyphs[ch]:
            d.line([(x0 + i * adv + px, top + py) for px, py in stroke], fill=255)
    if frame:
        ft = Image.new("L", (W, H), 0)
        ImageDraw.Draw(ft).rounded_rectangle(frame, radius=3, outline=255)
        glow(img, ft, frame_color, radius=3, strength=1.5)
    glow(img, tube, color)


# --- prop builders ----------------------------------------------------------------

@lru_cache(maxsize=None)
def fraud_guy(tagged=False):
    """A generic shady grifter: trench coat, fedora, shades, briefcase of cash (40x74)."""
    p = Prop(40, 74)
    d = p.d
    coat, coat_dk = (196, 166, 110), (150, 120, 76)
    for lx in (13, 22):
        d.rectangle((lx, 58, lx + 4, 69), fill=(50, 46, 56))
        d.rectangle((lx - 2, 69, lx + 5, 72), fill=(30, 26, 30))
    d.polygon([(12, 30), (28, 30), (33, 60), (7, 60)], fill=coat)
    d.polygon([(10, 31), (14, 31), (9, 52), (5, 51)], fill=coat)
    d.polygon([(26, 31), (30, 31), (35, 51), (31, 52)], fill=coat)
    d.rectangle((8, 45, 32, 47), fill=coat_dk)
    d.line([(20, 32), (20, 59)], fill=coat_dk)
    d.polygon([(12, 30), (20, 40), (17, 30)], fill=(236, 236, 236))
    d.polygon([(28, 30), (20, 40), (23, 30)], fill=(236, 236, 236))
    d.ellipse((11, 12, 29, 31), fill=SKIN)
    d.rounded_rectangle((12, 4, 28, 14), radius=4, fill=(70, 56, 46))
    d.rounded_rectangle((5, 12, 35, 15), radius=2, fill=(60, 48, 40))
    d.rectangle((29, 50, 39, 58), fill=(120, 80, 40))
    img = p.done()
    dd = ImageDraw.Draw(img)
    dd.line([(13, 11), (27, 11)], fill=(30, 24, 20))
    dd.rectangle((12, 18, 19, 21), fill=K)
    dd.rectangle((21, 18, 28, 21), fill=K)
    dd.line([(19, 19), (21, 19)], fill=K)
    dd.point([(13, 19), (22, 19)], fill=(120, 140, 200))
    dd.line([(16, 26), (25, 26)], fill=K)
    dd.line([(17, 27), (24, 27)], fill=WHITE)
    dd.line([(15, 25), (16, 26)], fill=K)
    dd.line([(26, 25), (25, 26)], fill=K)
    silk(dd, (34, 51), "$", GOLD, anchor="ma")
    return img


@lru_cache(maxsize=None)
def engineer_head(sweat=True):
    """A generic engineer (hard hat, worried face) for a cut-in panel, 36x36."""
    p = Prop(36, 36)
    d = p.d
    d.ellipse((7, 9, 29, 34), fill=SKIN)
    d.chord((5, 2, 31, 26), 180, 360, fill=GOLD)
    d.rectangle((3, 13, 33, 16), fill=(222, 170, 30))
    img = p.done()
    dd = ImageDraw.Draw(img)
    dd.line([(18, 3), (18, 12)], fill=(222, 170, 30))
    for ex in (12, 22):
        dd.rectangle((ex, 20, ex + 2, 23), fill=WHITE)
        dd.point((ex + 1, 22), fill=K)
        dd.line([(ex - 1, 18 + (1 if ex < 18 else 0)), (ex + 3, 18 + (0 if ex < 18 else 1))], fill=K)
    dd.arc((13, 27, 23, 33), 200, 340, fill=K)
    if sweat:
        sw = spr("SWEAT_BIG")
        img.paste(sw, (27, 17), sw)
        img.paste(sw, (4, 22), sw)
    return img


def spirit_level(ui, x, y, w, off, label_="ALIGNMENT"):
    """Bubble level: `off` in [-1, 1] slides the bubble away from centre."""
    d = ImageDraw.Draw(ui)
    d.rounded_rectangle((x - 1, y - 1, x + w, y + 12), radius=3, fill=K)
    d.rounded_rectangle((x, y, x + w - 1, y + 11), radius=2, fill=(60, 110, 200))
    d.rounded_rectangle((x + 6, y + 3, x + w - 7, y + 8), radius=2, fill=(200, 236, 90))
    cx = x + w / 2
    d.line([(cx - 5, y + 2), (cx - 5, y + 9)], fill=K)
    d.line([(cx + 5, y + 2), (cx + 5, y + 9)], fill=K)
    bx = cx + off * (w / 2 - 12)
    d.ellipse((bx - 4, y + 3, bx + 4, y + 8), fill=(240, 255, 200), outline=K)
    outline_text(ui, (x + w // 2, y + 10), label_, SILK, WHITE, anchor="ma")


def meter(ui, x, y, w, frac, color, title_=None, pct=True, hot=False, c=None):
    """Horizontal gauge with a label plate and a percentage."""
    d = ImageDraw.Draw(ui)
    if title_:
        label(ui, (x, y - 11), title_, bg=K, fg=WHITE)
    d.rectangle((x - 2, y - 2, x + w + 1, y + 9), fill=K)
    d.rectangle((x - 1, y - 1, x + w, y + 8), fill=(236, 206, 120))
    d.rectangle((x, y, x + w - 1, y + 7), fill=(40, 24, 40))
    n = int(round(w * clamp(frac, 0, 1)))
    if n > 0:
        d.rectangle((x, y, x + n - 1, y + 7), fill=color)
        d.line([(x, y), (x + n - 1, y)], fill=mix(color, WHITE, 0.5))
    if pct:
        s = f"{int(round(frac * 100))}%"
        col = RED if hot and (c is None or blink(c, 6)) else WHITE
        outline_text(ui, (x + w + 5, y), s, PRESS, col)


def win_client(ui, x, y, w, h, title_, active=True, fill=WHITE):
    box = win95(ui, x, y, w, h, title_, active=active)
    ImageDraw.Draw(ui).rectangle(box, fill=fill)
    return box


def terminal(ui, x, y, w, h, lines, title_="claude-code", cursor=True, c=None, ink=(90, 255, 120)):
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=K)
    d.rectangle((x, y, x + w - 1, y + 9), fill=(60, 60, 76))
    silk(d, (x + 4, y + 2), title_, (220, 220, 230))
    for i, col in enumerate(((255, 96, 86), (255, 190, 46), (40, 200, 64))):
        d.point([(x + w - 6 - i * 4, y + 4), (x + w - 5 - i * 4, y + 4)], fill=col)
    d.rectangle((x, y + 10, x + w - 1, y + h - 1), fill=(10, 12, 18))
    ly = y + 14
    for s, col in lines:
        d.fontmode = "1"
        d.text((x + 4, ly), s, font=PRESS, fill=col or ink)
        ly += 11
    if cursor and c is not None and blink(c, 3) and lines:
        s = lines[-1][0]
        d.rectangle((x + 4 + text_width(s, PRESS) + 1, ly - 11, x + 4 + text_width(s, PRESS) + 6, ly - 4),
                    fill=ink)


def typed(s, age, cps=22.0):
    """The part of `s` typed after `age` seconds."""
    if age < 0:
        return ""
    return s[:int(age * cps) + 1]


def glitch(ui, box, c, n=6, seed=0):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(ui)
    for i in range(n):
        r = rnd("gl", seed, c.f // 2, i)
        yy = y0 + int(r * (y1 - y0 - 4))
        hh = 1 + int(rnd("gh", seed, c.f // 2, i) * 4)
        sh = int((rnd("gs", seed, c.f // 2, i) - 0.5) * 16)
        col = [(255, 0, 90), (0, 255, 200), (255, 255, 255), (40, 40, 60)][i % 4]
        d.rectangle((max(x0, x0 + sh), yy, min(x1, x1 + sh), min(y1, yy + hh)), fill=col)


def xray_spine(img, x, top, bottom, t, limp=1.0):
    """Dark X-ray panel with a noodle spine wobbling inside (world space)."""
    d = ImageDraw.Draw(img)
    d.rectangle((x - 12, top - 1, x + 12, bottom + 1), fill=K)
    d.rectangle((x - 11, top, x + 11, bottom), fill=(20, 40, 90))
    dither_rect(img, (x - 11, top, x + 12, bottom + 1), (60, 100, 180), density=0.25)
    for i, y in enumerate(range(top + 2, bottom - 1, 3)):
        off = math.sin(t * 9 + i * 0.9) * 4 * limp * (i / 6)
        d.rectangle((x + off - 2, y, x + off + 2, y + 1), fill=(236, 240, 255))
    d.ellipse((x - 5, bottom - 5, x + 5, bottom), outline=(236, 240, 255))


def pencil_scribble(ui, x, y, w, p, color=(30, 40, 120)):
    """A cursive-looking signature drawn progressively (p in [0, 1])."""
    d = ImageDraw.Draw(ui)
    pts = []
    n = int(40 * clamp(p, 0, 1))
    for i in range(n):
        u = i / 40
        pts.append((x + u * w, y + math.sin(u * 19) * 3 + math.sin(u * 7) * 1.5))
    if len(pts) > 1:
        d.line(pts, fill=color, width=1)
    return pts[-1] if pts else (x, y)


def poster_frame(ui, top_text, bottom_text, age):
    """Vintage recruiting-poster border over the whole frame."""
    d = ImageDraw.Draw(ui)
    paper_c = (236, 222, 186)
    for box in ((0, 0, W, 30), (0, 0, 14, H), (W - 14, 0, W, H), (0, 138, W, H)):
        d.rectangle(box, fill=paper_c)
    d.rectangle((13, 29, W - 14, 138), outline=K, width=2)
    d.rectangle((16, 32, W - 17, 135), outline=(160, 30, 40))
    dither_rect(ui, (0, 0, W, 30), (200, 180, 140), density=0.18)
    title(ui, W // 2, 7, top_text, PRESS16, top=(210, 40, 50), bottom=(150, 20, 40), age=age)
    outline_text(ui, (W // 2, 143), bottom_text, PRESS, (30, 40, 110), outline=paper_c, anchor="ma")


def falling_piece(img, x, y, age, spin=6.0, g=260.0, vx=30.0, vy=-60.0, piece=None):
    """Ballistic flight of a sprite piece (returns False once it's off-screen)."""
    px = x + vx * age
    py = y + vy * age + 0.5 * g * age * age
    if py > H + 30:
        return False
    if piece is not None:
        paste_rot(img, piece, px, py, age * spin * 57.3 % 360)
    return True
