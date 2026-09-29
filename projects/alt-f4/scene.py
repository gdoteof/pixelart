"""Venue, crowd, HUD and gag overlays for the ALT-F4 video, all at 320x180."""
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from characters import draw_character, render_head
from engine import (CLAUDE_ORANGE, GOLD, H, NEON_CYAN, NEON_PINK, OPENAI_GREEN, PAL, ROOT, W,
                    compose, dither, dither_poly, dither_rect, font, mask, mix, outline_text,
                    sprite, text_width)

K = PAL["k"]
PRESS = font(size=8)
SILK = font("Silkscreen-Regular.ttf", 8)

WALL_BOTTOM = 120
STAGE_FRONT = 146
FEET_Y = 141
SAM_X, DARIO_X = 80, 240


# --- venue ------------------------------------------------------------------

def draw_wall(img):
    rng = random.Random(4)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, WALL_BOTTOM], fill=(24, 16, 32))
    bh, bw = 6, 14
    tones = [(52, 33, 58), (47, 30, 54), (56, 36, 60), (44, 28, 51), (60, 35, 55)]
    for row in range((WALL_BOTTOM - 1) // bh + 1):
        y = row * bh
        off = (row % 2) * (bw // 2)
        for col in range(-1, W // bw + 2):
            x = col * bw - off
            c = rng.choice(tones)
            d.rectangle([x + 1, y + 1, x + bw - 1, min(y + bh - 1, WALL_BOTTOM)], fill=c)
            d.line([(x + 1, y + 1), (x + bw - 2, y + 1)], fill=mix(c, (255, 255, 255), 0.07))
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((xx - W / 2) / 190.0) ** 2 + ((yy - 70) / 120.0) ** 2)
    shade = np.clip((dist - 0.35) * 1.8, 0, 0.9) + np.clip((24 - yy) / 40.0, 0, 0.5)
    shade[WALL_BOTTOM + 1:] = 0
    dither(img, np.clip(shade, 0, 1), (12, 8, 20), blend=0.6)


def silk(d, xy, s, fill, anchor="la"):
    """Silkscreen text with its cap tops at xy[1] (the font carries 4px of headroom)."""
    d.fontmode = "1"
    d.text((xy[0], xy[1] - 4), s, font=SILK, fill=fill, anchor=anchor)


def spray(img, xy, s, color, density=0.9):
    dither(img, mask(lambda d: silk(d, xy, s, 255)) * density, color, blend=0.75)


def glow(img, tube, color, radius=4, strength=2.0, core_tint=0.6):
    """Neon look from a 1px tube mask: hot core, saturated wall, dithered halo."""
    ring_img = tube.filter(ImageFilter.MaxFilter(3))
    core = np.asarray(tube, np.float32) / 255.0
    ring = np.asarray(ring_img, np.float32) / 255.0
    halo = np.asarray(ring_img.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255.0
    dither(img, np.clip(halo * strength, 0, 0.85) * (ring == 0), color, blend=0.4)
    dither(img, ring, color)
    dither(img, core, mix(color, (255, 255, 255), core_tint))


NEON_GLYPHS = {
    "A": [[(0, 15), (0, 4), (5, 0), (10, 4), (10, 15)], [(0, 9), (10, 9)]],
    "L": [[(1, 0), (1, 15), (10, 15)]],
    "T": [[(0, 0), (10, 0)], [(5, 0), (5, 15)]],
    "-": [[(2, 8), (8, 8)]],
    "F": [[(10, 0), (1, 0), (1, 15)], [(1, 7), (8, 7)]],
    "4": [[(8, 15), (8, 0), (0, 10), (10, 10)]],
}


def neon_sign(img, s, cx, top, color, off=()):
    adv = 15
    x0 = cx - (len(s) * adv - 4) // 2
    tube = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(tube)
    for i, ch in enumerate(s):
        if i not in off:
            for stroke in NEON_GLYPHS[ch]:
                d.line([(x0 + i * adv + px, top + py) for px, py in stroke], fill=255)
    glow(img, tube, color)


def draw_stage(img):
    rng = random.Random(9)
    d = ImageDraw.Draw(img)
    top = WALL_BOTTOM + 1
    d.rectangle([0, top, W - 1, STAGE_FRONT], fill=(84, 54, 42))
    y, gap = top, 2
    while y <= STAGE_FRONT:
        d.line([(0, y), (W - 1, y)], fill=(56, 34, 28))
        nxt = y + gap
        for _ in range(4):
            sx = rng.randint(0, W)
            d.line([(sx, y + 1), (sx, min(nxt - 1, STAGE_FRONT))], fill=(64, 40, 32))
        y, gap = nxt, gap + 1
    d.line([(0, top), (W - 1, top)], fill=(30, 20, 26))
    d.rectangle([0, STAGE_FRONT + 1, W - 1, STAGE_FRONT + 8], fill=(14, 10, 20))
    for i, x in enumerate(range(3, W, 6)):
        d.point((x, STAGE_FRONT + 3), fill=OPENAI_GREEN if (i // 2) % 2 else CLAUDE_ORANGE)


def draw_speaker(img, x, y, pump=0):
    d = ImageDraw.Draw(img)
    w, h = 26, 44
    d.rectangle([x, y, x + w, y + h], fill=K)
    d.rectangle([x + 1, y + 1, x + w - 1, y + h - 1], fill=(44, 40, 52))
    d.line([(x + 1, y + 1), (x + w - 1, y + 1)], fill=(72, 66, 84))
    cx = x + w // 2
    for cy, r in ((y + 11, 6), (y + 29, 9)):
        rr = r + pump
        d.ellipse([cx - rr - 1, cy - rr - 1, cx + rr + 1, cy + rr + 1], fill=K)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(30, 28, 36))
        d.ellipse([cx - rr + 2, cy - rr + 2, cx + rr - 2, cy + rr - 2], fill=(54, 50, 62))
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(20, 18, 26))


def draw_spotlights(img, active):
    for who, sx, tx in (("sam", 64, SAM_X), ("dario", W - 64, DARIO_X)):
        on = who == active
        pts = [(sx - 4, 0), (sx + 4, 0), (tx + 30, FEET_Y + 3), (tx - 30, FEET_Y + 3)]
        dither_poly(img, pts, (255, 244, 220), density=0.3 if on else 0.14, blend=0.3)
        pool = mask(lambda d: d.ellipse([tx - 32, FEET_Y - 6, tx + 32, FEET_Y + 5], fill=255))
        dither(img, pool * (0.55 if on else 0.3), (255, 236, 200), blend=0.3)


# --- crowd ------------------------------------------------------------------

def draw_person(d, x, y, r, color, rim, kind, led):
    d.rounded_rectangle([x - 2 * r, y + r + 1, x + 2 * r, H + 12], radius=r, fill=rim)
    d.rounded_rectangle([x - 2 * r, y + r + 2, x + 2 * r, H + 12], radius=r, fill=color)
    if kind == "hands":
        for f in (-1, 1):
            hx, hy = x + f * (2 * r + 1), y - 2 * r - 2
            d.line([(x + f * r * 3 // 2, y + r + 3), (hx, hy)], fill=color, width=3)
            d.ellipse([hx - 2, hy - 2, hx + 2, hy + 2], fill=rim)
            d.ellipse([hx - 2, hy - 1, hx + 2, hy + 2], fill=color)
    if kind == "phone":
        px, py = x + r + 3, y - r - 10
        d.line([(x + r, y + r + 3), (px, py + 6)], fill=color, width=3)
        d.rectangle([px - 2, py - 1, px + 2, py + 6], fill=K)
        d.rectangle([px - 1, py, px + 1, py + 5], fill=(190, 220, 255))
    if kind == "robot":
        d.rectangle([x - r, y - r, x + r, y + r], fill=rim)
        d.rectangle([x - r, y - r + 1, x + r, y + r], fill=color)
        d.line([(x, y - r - 4), (x, y - r)], fill=rim)
        d.point((x, y - r - 5), fill=led)
        d.line([(x - r + 2, y), (x - 1, y)], fill=led)
        d.line([(x + 1, y), (x + r - 2, y)], fill=led)
    else:
        d.ellipse([x - r, y - r, x + r, y + r], fill=rim)
        d.ellipse([x - r, y - r + 1, x + r, y + r + 1], fill=color)


def draw_crowd(img, beat=0.0):
    rng = random.Random(11)
    d = ImageDraw.Draw(img)
    rows = [(154, 5, (30, 21, 42), (86, 62, 108), (9, 14)),
            (165, 7, (13, 9, 20), (60, 44, 80), (13, 19))]
    for y0, r, color, rim, step in rows:
        x = rng.randint(-8, 0)
        while x < W + 12:
            kind = rng.choices(["human", "robot", "phone", "hands"], [6, 2, 2, 2])[0]
            led = rng.choice([(255, 60, 60), NEON_CYAN, (120, 255, 120)])
            phase = rng.random()
            bob = 2 if (beat + phase) % 1.0 < 0.5 else 0
            draw_person(d, x, y0 + rng.randint(-2, 3) + bob, r, color, rim, kind, led)
            x += rng.randint(*step)


# --- HUD --------------------------------------------------------------------

def health_bar(img, x0, y0, w, h, hp, recent, color, anchor_left=True):
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - 2, y0 - 2, x0 + w + 1, y0 + h + 1], fill=K)
    d.rectangle([x0 - 1, y0 - 1, x0 + w, y0 + h], fill=(236, 206, 120))
    d.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], fill=(52, 18, 30))

    def span(frac):
        n = int(round(w * frac))
        return (x0, x0 + n - 1) if anchor_left else (x0 + w - n, x0 + w - 1)

    if recent > hp:
        a, b = span(recent)
        if b >= a:
            d.rectangle([a, y0, b, y0 + h - 1], fill=(232, 56, 48))
    a, b = span(hp)
    if b >= a:
        d.rectangle([a, y0, b, y0 + h - 1], fill=color)
        d.line([(a, y0), (b, y0)], fill=mix(color, (255, 255, 255), 0.5))
        d.line([(a, y0 + h - 1), (b, y0 + h - 1)], fill=mix(color, (0, 0, 0), 0.35))


def draw_hud(img, sam_hp, sam_recent, dario_hp, dario_recent, verse="2"):
    d = ImageDraw.Draw(img)
    for who, x, col, facing in (("sam", 2, OPENAI_GREEN, 1), ("dario", W - 32, CLAUDE_ORANGE, -1)):
        d.rectangle([x, 2, x + 29, 31], fill=K)
        d.rectangle([x + 1, 3, x + 28, 30], fill=col)
        d.rectangle([x + 2, 4, x + 27, 29], fill=(30, 22, 40))
        face = render_head(who, facing=facing).crop((5, 4, 31, 30))
        img.paste(face, (x + 2, 4), face)
    bw = 104
    health_bar(img, 37, 6, bw, 8, sam_hp, sam_recent, OPENAI_GREEN, anchor_left=True)
    health_bar(img, W - 37 - bw, 6, bw, 8, dario_hp, dario_recent, CLAUDE_ORANGE,
               anchor_left=False)
    outline_text(img, (37, 19), "sam", PRESS, (255, 255, 255))
    outline_text(img, (W - 37, 19), "DARIO", PRESS, (255, 255, 255), anchor="ra")
    cx = W // 2
    d.rectangle([cx - 15, 2, cx + 15, 25], fill=K)
    d.rectangle([cx - 14, 3, cx + 14, 24], fill=(40, 28, 56))
    outline_text(img, (cx, 1), "VERSE", SILK, (200, 190, 230), anchor="ma")
    outline_text(img, (cx, 14), verse, PRESS, GOLD, anchor="ma")


# --- gags -------------------------------------------------------------------

CURSOR = sprite([
    "k.........",
    "kk........",
    "kwk.......",
    "kwwk......",
    "kwwwk.....",
    "kwwwwk....",
    "kwwwwwk...",
    "kwwwwwwk..",
    "kwwwwwwwk.",
    "kwwwwwkkkk",
    "kwwkwwk...",
    "kwk.kwwk..",
    "kk..kwwk..",
    "k....kwwk.",
    ".....kwwk.",
    "......kk..",
], {"k": (0, 0, 0), "w": (255, 255, 255)})


def bevel(d, box, raised=True):
    x0, y0, x1, y1 = box
    lt, rb = ((255, 255, 255), (0, 0, 0)) if raised else ((0, 0, 0), (255, 255, 255))
    d.rectangle(box, fill=(192, 192, 192))
    d.line([(x0, y1), (x0, y0), (x1, y0)], fill=lt)
    d.line([(x0 + 1, y1), (x1, y1), (x1, y0 + 1)], fill=rb)
    d.line([(x0 + 2, y1 - 1), (x1 - 1, y1 - 1), (x1 - 1, y0 + 2)], fill=(128, 128, 128))


def draw_popup(img, x, y, title, message, buttons, focus=None, cursor=True):
    w = max(96, text_width(message, PRESS) + 36)
    h = 50
    d = ImageDraw.Draw(img)
    dither_rect(img, (x + 3, y + 3, x + w + 3, y + h + 3), K, density=0.5)
    bevel(d, (x, y, x + w - 1, y + h - 1))
    for i in range(w - 6):
        d.line([(x + 3 + i, y + 3), (x + 3 + i, y + 12)],
               fill=mix((0, 0, 128), (16, 132, 208), i / (w - 7)))
    silk(d, (x + 6, y + 5), title, (255, 255, 255))
    bx = x + w - 13
    bevel(d, (bx, y + 4, bx + 8, y + 11))
    d.line([(bx + 2, y + 6), (bx + 5, y + 9)], fill=(0, 0, 0))
    d.line([(bx + 5, y + 6), (bx + 2, y + 9)], fill=(0, 0, 0))

    ix, iy = x + 8, y + 17
    d.polygon([(ix + 5, iy), (ix + 10, iy + 10), (ix, iy + 10)], fill=(0, 0, 0))
    d.polygon([(ix + 5, iy + 2), (ix + 8, iy + 9), (ix + 2, iy + 9)], fill=(255, 220, 0))
    d.line([(ix + 5, iy + 4), (ix + 5, iy + 6)], fill=(0, 0, 0))
    d.point((ix + 5, iy + 8), fill=(0, 0, 0))
    d.text((x + 24, y + 19), message, font=PRESS, fill=(0, 0, 0))

    bw_, gap = 30, 6
    total = len(buttons) * bw_ + (len(buttons) - 1) * gap
    bx = x + (w - total) // 2
    for i, label in enumerate(buttons):
        box = (bx, y + 34, bx + bw_ - 1, y + 45)
        if i == focus:
            d.rectangle(box, fill=(0, 0, 0))
            bevel(d, (box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1))
            for px in range(box[0] + 4, box[2] - 3, 2):
                d.point([(px, box[1] + 3), (px, box[3] - 3)], fill=(0, 0, 0))
        else:
            bevel(d, box)
        silk(d, ((box[0] + box[2]) // 2 + 1, box[1] + 4), label, (0, 0, 0), anchor="ma")
        if i == focus and cursor:
            img.paste(CURSOR, (box[2] - 7, box[1] + 7), CURSOR)
        bx += bw_ + gap
    return w, h


SWEAT = sprite([
    "..k..",
    ".kbk.",
    "kbbbk",
    "kbwbk",
    ".kkk.",
], {"k": PAL["k"], "b": (140, 200, 255), "w": (255, 255, 255)})


# --- lyrics -----------------------------------------------------------------

def draw_lyrics(img, lines, current, speaker, color):
    """Karaoke lines: sung words take the speaker's colour, the live word pops in gold."""
    y0 = H - 4 - len(lines) * 11
    dither_rect(img, (0, y0 - 4, W, H), K, density=0.75)
    tag_w = text_width(speaker, SILK) + 8
    d = ImageDraw.Draw(img)
    d.rectangle([6, y0 - 13, 6 + tag_w, y0 - 4], fill=K)
    d.rectangle([7, y0 - 12, 5 + tag_w, y0 - 5], fill=color)
    silk(d, (10, y0 - 11), speaker, K)
    idx = 0
    for li, words in enumerate(lines):
        x = (W - text_width(" ".join(words), PRESS)) // 2
        y = y0 + li * 11
        for word in words:
            if idx < current:
                c, dy = color, 0
            elif idx == current:
                c, dy = GOLD, -1
            else:
                c, dy = (214, 208, 224), 0
            outline_text(img, (x, y + dy), word, PRESS, c)
            x += text_width(word + " ", PRESS)
            idx += 1


# --- keycap gag -------------------------------------------------------------

def draw_keycap(img, x, y, label, pressed=0):
    d = ImageDraw.Draw(img)
    w = max(26, text_width(label, PRESS) + 14)
    h = 24
    y += pressed
    d.rounded_rectangle([x, y, x + w, y + h - pressed], radius=4, fill=K)
    d.rounded_rectangle([x + 1, y + 1, x + w - 1, y + h - 1 - pressed], radius=3, fill=(132, 132, 150))
    d.rounded_rectangle([x + 3, y + 2, x + w - 3, y + h - 7], radius=2, fill=(232, 232, 242))
    d.line([(x + 4, y + 2), (x + w - 4, y + 2)], fill=(255, 255, 255))
    outline_text(img, (x + w // 2 + 1, y + 6), label, PRESS, (40, 36, 60), outline=(232, 232, 242),
                 anchor="ma")
    return w


def burst(img, cx, cy, r0, r1, color, spikes=12, rot=0.0):
    import math
    pts = []
    for i in range(spikes * 2):
        a = rot + math.pi * i / spikes
        r = r1 if i % 2 == 0 else r0
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.8))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=K)
    inner = [(cx + (x - cx) * 0.86, cy + (y - cy) * 0.86) for x, y in pts]
    d.polygon(inner, fill=color)


# --- shots ------------------------------------------------------------------

_VENUE = None


def venue():
    """Static backdrop (wall, sign, stage, speakers), built once."""
    global _VENUE
    if _VENUE is None:
        img = Image.new("RGB", (W, H), K)
        draw_wall(img)
        spray(img, (14, 58), "AGI SOON", (70, 140, 132))
        spray(img, (266, 62), "p(doom)?", (170, 146, 64))
        spray(img, (116, 104), "404", (160, 80, 120))
        neon_sign(img, "ALT-F4", W // 2, 31, NEON_PINK)
        tube = Image.new("L", (W, H), 0)
        silk(ImageDraw.Draw(tube), (W // 2, 52), "LIVE @ THE SANDBOX", 255, anchor="ma")
        halo = np.asarray(tube.filter(ImageFilter.GaussianBlur(2)), np.float32) / 255.0
        dither(img, np.clip(halo * 1.5, 0, 0.6), NEON_CYAN, blend=0.35)
        dither(img, np.asarray(tube, np.float32) / 255.0, NEON_CYAN)
        draw_stage(img)
        draw_speaker(img, 4, WALL_BOTTOM - 36)
        draw_speaker(img, W - 31, WALL_BOTTOM - 36)
        _VENUE = img
    return _VENUE.copy()


def world_frame(active, sam, dario, beat=0.0):
    img = venue()
    draw_spotlights(img, active)
    hy = draw_character(img, "sam", SAM_X, FEET_Y, facing=1, **sam)["hy"]
    draw_character(img, "dario", DARIO_X, FEET_Y, facing=-1, **dario)
    draw_crowd(img, beat)
    return img, hy


def wide_shot():
    world, sam_hy = world_frame(
        "dario",
        dict(mouth="frown", brows="worried", back_arm="cross", front_arm="cross"),
        dict(mouth="shout", brows="angry", back_arm="mic", front_arm="point"))
    world.paste(SWEAT, (SAM_X - 16, sam_hy + 10), SWEAT)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_popup(ui, 104, 58, "board.exe", "Close sam?", ["YES", "YES"], focus=1)
    draw_hud(ui, 0.58, 0.72, 0.9, 0.9)
    draw_lyrics(ui, [["YOUR", "OWN", "BOARD", "CLOSED", "YOUR", "WINDOW"],
                     ["AND", "SHOWED", "YOU", "THE", "DOOR"]],
                current=5, speaker="DARIO", color=CLAUDE_ORANGE)
    return compose(world, ui)


def closeup_shot():
    world, _ = world_frame(
        "dario",
        dict(mouth="o", brows="raised", eyes="wide", back_arm="down", front_arm="down"),
        dict(mouth="shout", brows="angry", back_arm="mic", front_arm="point"))
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    burst(ui, 70, 72, 30, 46, GOLD, spikes=11, rot=0.2)
    x = 24
    x += draw_keycap(ui, x, 58, "ALT") + 6
    outline_text(ui, (x, 66), "+", PRESS, (255, 255, 255))
    draw_keycap(ui, x + 14, 58, "F4", pressed=3)
    draw_hud(ui, 0.66, 0.72, 0.9, 0.9)
    draw_lyrics(ui, [["ALT-MAN?", "NAH,", "YOU'RE", "ALT-F4"]], current=3, speaker="DARIO",
                color=CLAUDE_ORANGE)
    return compose(world, ui, cx=DARIO_X - 18, cy=98, k=12)


if __name__ == "__main__":
    wide_shot().save(ROOT / "stills" / "style_wide.png")
    closeup_shot().save(ROOT / "stills" / "style_closeup.png")
    print("ok")
