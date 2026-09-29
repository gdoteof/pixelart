"""Frame renderer for the ALT-F4 video.

render_frame(t) builds one 1920x1080 frame: a 320x180 world seen through an
integer-zoom camera, plus a 320x180 UI layer shown at 6x.

Per-line gags (gags.py) are generators that yield the phase they draw in next:

    <setup code>        runs first: may change the shot, poses, HUD, crowd...
    yield "back"        world, behind the characters
    yield "front"       world, in front of the characters
    yield "crowd"       world, in front of the crowd
    yield "ui"          UI layer, under the karaoke band and hit FX
    yield "top"         UI layer, over everything
"""
import math
import random
import re
import zlib
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import timeline as TL
from characters import HH, HW, SKIN, SKIN_SH, _grow, draw_character, render_head
from engine import (CLAUDE_ORANGE, GOLD, H, NEON_CYAN, NEON_PINK, OPENAI_GREEN, SCALE, W, dither,
                    dither_poly, dither_rect, mask, mix, outline_text, text_width)
from props import (DIZZY, PRESS16, PRESS24, RED, WHITE, Prop, ascii_sprite, back_out, big_text,
                   bubble, caption, confetti, ease_out, label, paste)
from scene import (CURSOR, DARIO_X, FEET_Y, K, NEON_GLYPHS, PRESS, SAM_X, SILK, SWEAT,
                   WALL_BOTTOM, bevel, burst, draw_lyrics, draw_popup, draw_speaker, draw_stage,
                   draw_wall, health_bar, neon_sign, silk, spray)

FPS = TL.FPS
TEAM = {"sam": OPENAI_GREEN, "dario": CLAUDE_ORANGE}
RAPPER = {"v1": "sam", "v3": "sam", "v2": "dario", "v4": "dario"}
OTHER = {"sam": "dario", "dario": "sam"}
ALL_NEON = frozenset(range(6))
PHASES = ("back", "front", "crowd", "ui", "top")


def rnd(*key):
    """Deterministic pseudo-random number in [0, 1), identical in every worker process."""
    return zlib.crc32(repr(key).encode()) / 2 ** 32


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def lerp(a, b, p):
    return a + (b - a) * p


def ramp(t, a, b):
    """0 before a, 1 after b, linear in between."""
    return clamp((t - a) / (b - a), 0.0, 1.0)


def scaled(img, n):
    return img.resize((int(img.width * n), int(img.height * n)), Image.NEAREST)


def rot_pt(px, py, cx, cy, deg):
    """Where (px, py) lands when an image is rotated by `deg` (PIL's CCW) about (cx, cy)."""
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return cx + dx * math.cos(a) + dy * math.sin(a), cy - dx * math.sin(a) + dy * math.cos(a)


# --- camera -----------------------------------------------------------------

SHOTS = {
    "wide": (160, 90, 6), "two": (160, 100, 7), "L": (120, 96, 9), "R": (200, 96, 9),
    "cL": (104, 94, 12), "cR": (216, 94, 12), "xL": (84, 92, 18), "xR": (236, 92, 18),
    "crowd": (160, 140, 8), "sign": (160, 44, 9), "mid": (160, 98, 9),
}


class Cam:
    def __init__(self, cx, cy, k):
        self.k = int(k)
        vw, vh = W * SCALE / self.k, H * SCALE / self.k
        self.x0 = min(max(cx - vw / 2, 0), W - vw)
        self.y0 = min(max(cy - vh / 2, 0), H - vh)
        self.cx, self.cy = self.x0 + vw / 2, self.y0 + vh / 2

    def ui(self, x, y):
        f = self.k / SCALE
        return (x - self.x0) * f, (y - self.y0) * f

    @property
    def f(self):
        return self.k / SCALE


def compose(world, ui, cam, shake=(0, 0)):
    ow, oh, k = W * SCALE, H * SCALE, cam.k
    sx, sy = int(round(cam.x0 * k)) + shake[0], int(round(cam.y0 * k)) + shake[1]
    wx, wy = sx // k, sy // k
    wx1, wy1 = (sx + ow) // k + 1, (sy + oh) // k + 1
    part = world.crop((wx, wy, wx1, wy1)).resize(((wx1 - wx) * k, (wy1 - wy) * k), Image.NEAREST)
    frame = part.crop((sx - wx * k, sy - wy * k, sx - wx * k + ow, sy - wy * k + oh))
    if ui is not None:
        big = ui.resize((ow, oh), Image.NEAREST)
        frame.paste(big, (0, 0), big)
    return frame


# --- per-frame context ------------------------------------------------------

def default_state(who):
    sam = who == "sam"
    return dict(x=SAM_X if sam else DARIO_X, y=FEET_Y, facing=1 if sam else -1, mouth="closed",
                brows="neutral", eyes="open", back_arm="down", front_arm="down", bob=0, stride=0,
                hidden=False, rot=0.0, pivot=0, dx=0, dy=0, sweat=False, dizzy=False)


class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = RAPPER.get(self.sec)
        self.st = {w: default_state(w) for w in ("sam", "dario")}
        self.shot = "two"
        self.lock_shot = False
        self.hud = dict(show=True, slide=1.0, fill=1.0, badge=("VERSE", "1"), combo=True,
                        bar_scale={"sam": 1.0, "dario": 1.0}, name_scale={"sam": 1.0, "dario": 1.0},
                        hp=None)
        self.karaoke = True
        self.crowd = "normal"
        self.venue = dict(lit=True, neon=ALL_NEON, live=True)
        self.spot = (self.rapper,) if self.rapper else ()
        self.wash = TEAM.get(self.rapper)
        self.alarm = False
        self.pump = True
        self.flash = 0.0
        self.flash_color = WHITE
        self.shake = 0.0
        self.hitfx = True
        self.extra = []          # section-level gag generators
        self.cam = None
        self.world = None
        self.ui = None
        self.anchor = {}

    # geometry helpers, valid in every phase after setup
    def to_ui(self, x, y):
        return self.cam.ui(x, y)

    def head_box(self, who):
        s = self.st[who]
        x, y = s["x"] + s["dx"], s["y"] + s["dy"] + s["bob"]
        hx = x - HW // 2 + (1 if s["facing"] == 1 else 0)
        hy = y - 68
        return hx, hy, hx + HW, hy + HH

    def head_ui(self, who):
        """(centre x, top y, bottom y) of a character's head in UI pixels."""
        x0, y0, x1, y1 = self.head_box(who)
        cx, top = self.to_ui((x0 + x1) / 2, y0 + 3)
        return cx, top, self.to_ui(0, y1)[1]

    def feet_ui(self, who):
        s = self.st[who]
        return self.to_ui(s["x"] + s["dx"], s["y"] + s["dy"])

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=WHITE):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color


class LineRef:
    """A lyric line as seen by its gag: word times and ages relative to now."""

    def __init__(self, ln, t):
        self.ln, self.t = ln, t
        self.t0, self.t1 = ln["t0"], ln["t1"]
        self.words = ln["words"]

    def w(self, pat, which="t0"):
        return TL.word_time(self.ln, pat, which)

    def age(self, pat=None):
        return self.t - (self.w(pat) if pat else self.t0)

    def on(self, pat):
        return self.t >= self.w(pat)


class GagRunner:
    def __init__(self, gens):
        self.wait = []
        for g in gens:
            try:
                self.wait.append([g, next(g)])
            except StopIteration:
                pass

    def run(self, phase):
        idx = PHASES.index(phase)
        for item in self.wait:
            g, ph = item
            while ph is not None and PHASES.index(ph) <= idx:
                try:
                    ph = next(g)
                except StopIteration:
                    ph = None
            item[1] = ph


def _line_windows():
    from gags import GAGS
    out = []
    by = {(ln["sec"], ln["idx"]): ln for ln in TL.LINES}
    for key, (fn, pre, post) in GAGS.items():
        ln = by[key]
        same = [l for l in TL.LINES if l["sec"] == ln["sec"] and l["idx"] == ln["idx"] + 1]
        end = same[0]["t0"] - 0.12 if same else TL.section_bounds(ln["sec"])[1]
        out.append((ln["t0"] - pre, end + post, fn, ln))
    return out


_WINDOWS = None


def active_gags(c):
    global _WINDOWS
    if _WINDOWS is None:
        _WINDOWS = _line_windows()
    gens = [fn(c, LineRef(ln, c.t)) for a, b, fn, ln in _WINDOWS if a <= c.t < b]
    return gens + [g(c) for g in c.extra]


# --- venue ------------------------------------------------------------------

@lru_cache(maxsize=16)
def venue_variant(lit=True, neon=ALL_NEON, live=True):
    img = Image.new("RGB", (W, H), K)
    draw_wall(img)
    spray(img, (14, 58), "AGI SOON", (70, 140, 132))
    spray(img, (266, 62), "p(doom)?", (170, 146, 64))
    spray(img, (116, 104), "404", (160, 80, 120))
    draw_stage(img)
    draw_speaker(img, 4, WALL_BOTTOM - 36)
    draw_speaker(img, W - 31, WALL_BOTTOM - 36)
    if not lit:
        img = Image.fromarray((np.asarray(img, np.float32) * 0.3).astype(np.uint8))
    tube = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(tube)
    x0 = W // 2 - (6 * 15 - 4) // 2
    for i, ch in enumerate("ALT-F4"):
        if i not in neon:
            for stroke in NEON_GLYPHS[ch]:
                d.line([(x0 + i * 15 + px, 31 + py) for px, py in stroke], fill=255)
    dither(img, np.asarray(tube, np.float32) / 255.0, (92, 40, 80))
    if neon:
        neon_sign(img, "ALT-F4", W // 2, 31, NEON_PINK, off=tuple(i for i in range(6) if i not in neon))
    tube = Image.new("L", (W, H), 0)
    silk(ImageDraw.Draw(tube), (W // 2, 52), "LIVE @ THE SANDBOX", 255, anchor="ma")
    core = np.asarray(tube, np.float32) / 255.0
    if live:
        halo = np.asarray(tube.filter(ImageFilter.GaussianBlur(2)), np.float32) / 255.0
        dither(img, np.clip(halo * 1.5, 0, 0.6), NEON_CYAN, blend=0.35)
        dither(img, core, NEON_CYAN)
    else:
        dither(img, core, (34, 60, 70))
    return img


def spotlights(img, active):
    for who, sx, tx in (("sam", 64, SAM_X), ("dario", W - 64, DARIO_X)):
        on = who in active
        pts = [(sx - 4, 0), (sx + 4, 0), (tx + 30, FEET_Y + 3), (tx - 30, FEET_Y + 3)]
        dither_poly(img, pts, (255, 244, 220), density=0.3 if on else 0.12, blend=0.3)
        pool = mask(lambda d: d.ellipse([tx - 32, FEET_Y - 6, tx + 32, FEET_Y + 5], fill=255))
        dither(img, pool * (0.55 if on else 0.25), (255, 236, 200), blend=0.3)


def beacons(img, t):
    """Rotating red alarm lights on top of the speakers."""
    d = ImageDraw.Draw(img)
    for i, bx in enumerate((17, W - 18)):
        by = WALL_BOTTOM - 40
        a = t * 5.2 + i * math.pi
        sweep = math.sin(a)
        if math.cos(a) > -0.2:
            tip = (bx + sweep * 150, by - 70 + abs(sweep) * 40)
            spread = 26
            dither_poly(img, [(bx, by), (tip[0] - spread, tip[1]), (tip[0] + spread, tip[1] + 14)],
                        (255, 40, 40), density=0.45, blend=0.45)
        d.rectangle([bx - 5, by + 1, bx + 5, by + 4], fill=K)
        d.chord([bx - 5, by - 6, bx + 5, by + 4], 180, 360, fill=K)
        d.chord([bx - 4, by - 5, bx + 4, by + 3], 180, 360, fill=(255, 60, 60) if math.cos(a) > 0 else (170, 30, 40))
        d.point([(bx - 2, by - 3)], fill=(255, 200, 200))


# --- crowd ------------------------------------------------------------------

def person(d, x, y, r, color, rim, kind, led, screen):
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
        d.rectangle([px - 1, py, px + 1, py + 5], fill=screen)
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


def draw_crowd(img, t, mode="normal"):
    i, ph, per = TL.beat_info(t)
    beat = i + ph
    rng = random.Random(11)
    d = ImageDraw.Draw(img)
    rows = [(154, 5, (30, 21, 42), (86, 62, 108), (9, 14)),
            (165, 7, (13, 9, 20), (60, 44, 80), (13, 19))]
    glows = []
    for y0, r, color, rim, step in rows:
        x = rng.randint(-8, 0)
        while x < W + 12:
            kind = rng.choices(["human", "robot", "phone", "hands"], [6, 2, 2, 2])[0]
            led = rng.choice([(255, 60, 60), NEON_CYAN, (120, 255, 120)])
            phase = rng.random()
            jitter = rng.randint(-2, 3)
            screen = (190, 220, 255)
            if mode == "hype":
                if kind != "robot" and phase < 0.8:
                    kind = "hands"
                bob = 3 if (ph + phase * 0.15) % 1.0 < 0.4 else 0
            elif mode == "phones":
                if kind != "robot":
                    kind = "phone"
                    glows.append((x + r + 3, y0 + jitter - r - 8))
                screen = led = (120, 255, 190)
                bob = 1 if (beat + phase) % 1.0 < 0.5 else 0
            elif mode == "still":
                bob = 0
            else:
                bob = 2 if (beat + phase) % 1.0 < 0.5 else 0
            person(d, x, y0 + jitter + bob, r, color, rim, kind, led, screen)
            x += rng.randint(*step)
    if glows:
        m = mask(lambda dd: [dd.ellipse([gx - 6, gy - 6, gx + 6, gy + 6], fill=255) for gx, gy in glows])
        dither(img, m * 0.35, OPENAI_GREEN, blend=0.5)


# --- characters -------------------------------------------------------------

GESTURES = ["point", "pump", "down", "point", "shrug", "up", "hip", "point"]


def singing(c, who):
    ln = c.ln
    return (ln is not None and ln["speaker"] in (who, "crowd")
            and ln["t0"] - 0.05 <= c.t <= ln["t1"] + 0.12)


def mouth_for(c, who, rest="closed"):
    if not singing(c, who):
        return rest
    v = TL.loudness(c.t)
    return "shout" if v > 0.72 else "open" if v > 0.42 else "o" if v > 0.18 else "closed"


def pose_rapper(c, who):
    s = c.st[who]
    s["back_arm"] = "mic"
    s["front_arm"] = GESTURES[zlib.crc32(f"{who}{c.beat_i // 2}".encode()) % len(GESTURES)]
    s["bob"] = 1 if c.ph < 0.35 else 0
    s["mouth"] = mouth_for(c, who)
    s["brows"] = "angry" if (who == "dario" or s["mouth"] == "shout") else "smug"


def pose_listener(c, who):
    s = c.st[who]
    s["back_arm"] = s["front_arm"] = "cross"
    s["bob"] = 1 if (c.beat_i % 2 == 0 and c.ph < 0.35) else 0
    if who == "sam":
        s["mouth"], s["brows"] = "smirk", "smug"
    else:
        s["mouth"], s["brows"] = "frown", "angry"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = (3.1, 0.9) if who == "sam" else (3.7, 2.2)
        if s["eyes"] == "open" and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    for who in ("sam", "dario"):
        h = TL.last_hit(c.t, target=who, window=0.9)
        if not h or h["attacker"] == "both":
            continue
        age = c.t - h["t"]
        s = c.st[who]
        if age < 0.6:
            s["eyes"], s["brows"] = "wide", "worried"
            s["mouth"] = "shout" if h["big"] and age < 0.3 else "o"
        s["sweat"] = True
        kb = (5 if h["big"] else 3) * max(0.0, 1 - age / 0.4)
        s["dx"] += int(round(kb * (-1 if who == "sam" else 1)))


def hit_shake_flash(c):
    for h in TL.HITS:
        age = c.t - h["t"]
        if h["attacker"] == "both" or age < 0:
            continue
        if age < 0.35:
            c.add_shake((16 if h["big"] else 6) * (1 - age / 0.35))
        if h["big"] and age < 2 / FPS:
            c.add_flash(0.5)


def draw_char(c, img, who):
    s = c.st[who]
    if s["hidden"]:
        return None
    kw = {k: s[k] for k in ("facing", "mouth", "brows", "eyes", "back_arm", "front_arm", "bob",
                            "stride")}
    x, y = int(round(s["x"] + s["dx"])), int(round(s["y"] + s["dy"]))
    if s["rot"]:
        m = 90
        layer = Image.new("RGBA", (W + 2 * m, H + 2 * m), (0, 0, 0, 0))
        a = draw_character(layer, who, x + m, y + m, **kw)
        piv = (x + m, y + m - s["pivot"])
        layer = layer.rotate(s["rot"], resample=Image.NEAREST, center=piv).crop((m, m, m + W, m + H))
        img.paste(layer, (0, 0), layer)
        hc = rot_pt(a["hx"] + HW / 2, a["hy"] + HH / 2, piv[0], piv[1], s["rot"])
        a = dict(hx=a["hx"] - m, hy=a["hy"] - m, top=a["top"] - m,
                 mouth=(a["mouth"][0] - m, a["mouth"][1] - m),
                 hands=[(hx_ - m, hy_ - m) for hx_, hy_ in a["hands"]],
                 chest=(a["chest"][0] - m, a["chest"][1] - m), head_c=(hc[0] - m, hc[1] - m))
    else:
        a = draw_character(img, who, x, y, **kw)
        a = dict(a, head_c=(a["hx"] + HW / 2, a["hy"] + HH / 2))
    if s["sweat"] and not s["rot"]:
        drip = int(c.t * 5) % 3
        sx = a["hx"] + 1 if s["facing"] == 1 else a["hx"] + HW - 6
        img.paste(SWEAT, (sx, a["hy"] + 10 + drip), SWEAT)
    if s["dizzy"]:
        star = ascii_sprite(DIZZY)
        hx, hy = a["head_c"]
        top = hy - (21 if not s["rot"] else 15)
        for k in range(3):
            ang = c.t * 7 + k * 2 * math.pi / 3
            img.paste(star, (int(hx + 15 * math.cos(ang)) - 2, int(top + 4 * math.sin(ang)) - 2), star)
    c.anchor[who] = a
    return a


# --- HUD --------------------------------------------------------------------

def text_img(s, fnt=PRESS, fill=WHITE, outline=K):
    tw = text_width(s, fnt) + 2
    im = Image.new("RGBA", (tw, fnt.size + 3), (0, 0, 0, 0))
    outline_text(im, (1, 1), s, fnt, fill, outline=outline)
    return im


def draw_name(ui, s, x, y, scale, right):
    if scale == 1.0:
        outline_text(ui, (x, y), s, PRESS, WHITE, anchor="ra" if right else "la")
        return
    im = text_img(s)
    im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.NEAREST)
    ui.paste(im, (int(x - im.width) if right else int(x), int(y)), im)


def draw_hud(c):
    o = c.hud
    if not o["show"] or o["slide"] <= 0:
        return
    ui = c.ui
    d = ImageDraw.Draw(ui)
    dy = int(round((1 - ease_out(o["slide"])) * -36))
    for who, x, col, facing in (("sam", 2, OPENAI_GREEN, 1), ("dario", W - 32, CLAUDE_ORANGE, -1)):
        s = c.st[who]
        d.rectangle([x, 2 + dy, x + 29, 31 + dy], fill=K)
        d.rectangle([x + 1, 3 + dy, x + 28, 30 + dy], fill=col)
        d.rectangle([x + 2, 4 + dy, x + 27, 29 + dy], fill=(30, 22, 40))
        face = render_head(who, s["mouth"], s["brows"], s["eyes"], facing).crop((5, 4, 31, 30))
        ui.paste(face, (x + 2, 4 + dy), face)
    top, val = o["badge"]
    cx = W // 2
    fresh = c.t - c.sa < 0.4 and c.sec in RAPPER
    d.rectangle([cx - 15, 2 + dy, cx + 15, 25 + dy], fill=K)
    d.rectangle([cx - 14, 3 + dy, cx + 14, 24 + dy], fill=GOLD if fresh and c.f % 4 < 2 else (40, 28, 56))
    outline_text(ui, (cx, 1 + dy), top, SILK, (200, 190, 230), anchor="ma")
    outline_text(ui, (cx, 14 + dy), val, PRESS, GOLD, anchor="ma")
    bw = 104
    for who, col, left in (("sam", OPENAI_GREEN, True), ("dario", CLAUDE_ORANGE, False)):
        if o["hp"] is not None:
            hp, rec = o["hp"][who]
        else:
            hp, rec = TL.hp(who, c.t), TL.hp_recent(who, c.t)
        hp, rec = hp * o["fill"], rec * o["fill"]
        w = int(round(bw * o["bar_scale"][who]))
        x0 = 37 if left else W - 37 - w
        health_bar(ui, x0, 6 + dy, w, 8, hp, rec, col, anchor_left=left)
    draw_name(ui, "sam", 37, 19 + dy, o["name_scale"]["sam"], False)
    draw_name(ui, "DARIO", W - 37, 19 + dy, o["name_scale"]["dario"], True)
    if o["combo"]:
        for who, x, anchor in (("sam", 37, "la"), ("dario", W - 37, "ra")):
            hits = [h for h in TL.HITS if h["attacker"] == who and 0 <= c.t - h["t"] < 1.6]
            if hits:
                n = TL.combo(hits[-1]["t"], who)
                if n >= 2:
                    age = c.t - hits[-1]["t"]
                    grow = max(0.0, o["name_scale"][who] - 1)
                    yy = 30 + dy + int(11 * grow) + max(0, -(pop_dy(age) or 0))
                    outline_text(ui, (x, yy), f"{n} HITS", PRESS, GOLD if c.f % 6 < 4 else WHITE,
                                 anchor=anchor)


def pop_dy(age, dur=0.15):
    if age < 0:
        return None
    return int(round((1 - back_out(age / dur)) * -8))


# --- karaoke ----------------------------------------------------------------

SPEAKERS = {"sam": ("SAM", OPENAI_GREEN), "dario": ("DARIO", CLAUDE_ORANGE),
            "host": ("HOST", NEON_CYAN), "crowd": ("CROWD", NEON_PINK)}


def clean_word(w):
    return re.sub(r"FUCK", "F***", w.upper().replace("’", "'"))


def wrap(words, width=300):
    lines, cur = [], []
    for w in words:
        if cur and text_width(" ".join(cur + [w]), PRESS) > width:
            lines.append(cur)
            cur = [w]
        else:
            cur = cur + [w]
    if cur:
        lines.append(cur)
    return lines


def draw_karaoke(c):
    ln = c.ln
    if ln is None or not c.karaoke:
        return
    words = [clean_word(w["w"]) for w in ln["words"]]
    tag, col = SPEAKERS[ln["speaker"]]
    draw_lyrics(c.ui, wrap(words), TL.word_index(ln, c.t), tag, col)


# --- hit FX -----------------------------------------------------------------

KILL_LABELS = {("v1", 3): "CRITICAL!", ("v1", 11): "SAVAGE!", ("v2", 2): "CRITICAL!",
               ("v2", 3): "BRUTAL!", ("v2", 11): "SAVAGE!", ("v3", 3): "DETECTED!",
               ("v3", 5): "CRITICAL!", ("v3", 11): "SAVAGE!", ("v4", 2): "CRITICAL!",
               ("v4", 3): "BRUTAL!", ("v4", 7): "UPPERCUT!", ("v4", 11): "OVERKILL!"}
LINE_KEY = {ln["gi"]: (ln["sec"], ln["idx"]) for ln in TL.LINES}


def draw_hit_fx(c):
    ui = c.ui
    for h in TL.HITS:
        age = c.t - h["t"]
        if age < 0 or age > 1.1 or h["attacker"] == "both":
            continue
        who = h["target"]
        s = c.st[who]
        side = -1 if who == "dario" else 1       # the cheek facing the attacker
        if not s["hidden"]:
            hx, top, bot = c.head_ui(who)
            f = c.cam.f
            bx, by = hx + side * 14 * f, (top + bot) / 2
            if h["big"] and age < 0.3:
                burst(ui, bx, by, (10 + age * 30) * f, (22 + age * 40) * f, GOLD, spikes=12, rot=age * 4)
                burst(ui, bx, by, (5 + age * 16) * f, (11 + age * 22) * f, WHITE, spikes=12, rot=age * 4 + 0.3)
            elif not h["big"] and age < 0.16:
                burst(ui, bx, by, 4 * f, 10 * f, WHITE, spikes=8, rot=h["t"])
        if h["big"] and age < 1.0:
            lab = KILL_LABELS.get(LINE_KEY.get(h["line"]), "CRITICAL!")
            fnt = PRESS24 if age < 2 / FPS else PRESS16
            if s["hidden"]:
                x, y = W // 2, 60
            else:
                hx, top, _ = c.head_ui(who)
                tw = text_width(lab, fnt)
                x = clamp(hx, tw // 2 + 6, W - tw // 2 - 6)
                y = clamp(top - 24, 36, 110)
            wob = int(round(math.sin(age * 30) * 2 * max(0.0, 1 - age / 0.4)))
            if age < 0.8 or c.f % 2 == 0:
                big_text(ui, (x, y + wob), lab, fnt, top=WHITE, bottom=GOLD, anchor="ma")


def shake_offset(c):
    if c.shake < 0.5:
        return (0, 0)
    a = rnd("shake", c.f) * 2 * math.pi
    return (int(round(math.cos(a) * c.shake)), int(round(math.sin(a) * c.shake)))


# --- section setups ---------------------------------------------------------

def default_shot(c):
    ln = c.ln
    if ln is None or ln["sec"] != c.sec:
        return "two"
    side = "L" if c.rapper == "sam" else "R"
    return ["two", side, "wide", "c" + side][ln["idx"] % 4]


def verse_setup(c):
    r = c.rapper
    pose_rapper(c, r)
    pose_listener(c, OTHER[r])
    c.hud["badge"] = ("VERSE", TL.VERSE_NO[c.sec])
    c.shot = default_shot(c)


def neon_state(c):
    t = c.t
    if t < 1.58:
        return frozenset()
    fr = int((t - 1.58) * FPS)
    pattern = [1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1]
    if fr < len(pattern):
        return ALL_NEON if pattern[fr] else frozenset()
    if rnd("n4", c.f // 2) < 0.07:
        return ALL_NEON - {5}
    return ALL_NEON


def sign_setup(c):
    for s in c.st.values():
        s["hidden"] = True
    c.hud["show"] = False
    c.crowd = None
    c.spot = ()
    c.wash = None
    c.pump = False
    c.venue = dict(lit=False, neon=neon_state(c), live=c.t >= 2.28)
    c.shot = (160, 44, 9 if c.t < 2.28 else 10)


def hype_setup(c):
    t = c.t
    c.crowd = "hype"
    c.spot = ("sam", "dario")
    c.wash = NEON_PINK
    c.hud.update(badge=("VERSE", "1"), slide=ramp(t, 16.0, 16.4), fill=ramp(t, 16.3, 17.6), combo=False)
    for who, x0, x1 in (("sam", -24, SAM_X), ("dario", W + 24, DARIO_X)):
        s = c.st[who]
        p = ramp(t, 15.5, 17.4)
        s["x"] = lerp(x0, x1, p)
        if 0 < p < 1:
            step = int((t - 15.5) / 0.16) % 4
            s["stride"], s["bob"] = [2, 0, -2, 0][step], step % 2
        else:
            s["bob"] = 1 if c.ph < 0.35 else 0
        if t < 18.6:
            s["back_arm"], s["front_arm"] = ("down", "hip") if who == "sam" else ("cross", "cross")
            s["mouth"], s["brows"] = ("smirk", "smug") if who == "sam" else ("closed", "angry")
        elif t < 21.22:
            s["back_arm"] = "down"
            s["front_arm"] = "pump" if c.ph < 0.5 else "up"
            s["mouth"], s["brows"] = "grin", "angry"
        elif t < 23.84:
            s["back_arm"], s["front_arm"] = "down", "point"
            s["mouth"], s["brows"] = ("shout" if t < 22.2 else "teeth"), "angry"
        else:
            if who == "sam":
                s["back_arm"], s["front_arm"], s["mouth"], s["brows"] = "mic", "point", "smirk", "smug"
            else:
                s["back_arm"] = s["front_arm"] = "cross"
                s["mouth"], s["brows"] = "frown", "angry"
    if t < 17.6:
        c.shot = "wide"
    elif t < 18.6:
        c.shot = "two"
    elif t < 21.22:
        c.shot = "wide"
    elif t < 22.54:
        c.shot = (160, 100, 7)
    elif t < 23.18:
        c.shot = (160, 100, 8)
    elif t < 23.84:
        c.shot = (160, 100, 9)
    else:
        c.shot = "L"
    c.extra.append(hype_titles)


def hype_titles(c):
    t = c.t
    yield "top"
    if 18.6 <= t < 20.6:
        x = W // 2 + (1 - ease_out(ramp(t, 18.6, 18.8))) * -240 + ease_out(ramp(t, 20.4, 20.6)) * 260
        big_text(c.ui, (x, 64), "ROUND 1", PRESS24, top=WHITE, bottom=(170, 200, 255), anchor="ma")
    if 21.22 <= t < 22.6:
        age = t - 21.22
        fnt = PRESS24 if age > 2 / FPS else PRESS16
        if age < 1.1 or c.f % 2 == 0:
            if age < 2 / FPS:
                im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                big_text(im, (W // 2, 60), "FIGHT!", PRESS24, top=GOLD, bottom=(255, 80, 40), anchor="ma")
                im = scaled(im.crop((60, 40, 260, 110)), 1.5)
                c.ui.paste(im, (W // 2 - im.width // 2, 70 - im.height // 2), im)
            else:
                big_text(c.ui, (W // 2, 58), "FIGHT!", fnt, top=GOLD, bottom=(255, 80, 40), anchor="ma")
    if 21.22 <= t < 21.22 + 2 / FPS:
        c.add_flash(0.6)
    if 21.22 <= t < 21.6:
        c.add_shake(16 * (1 - (t - 21.22) / 0.38))


CHANT_SHOTS = ["wide", "cL", "cR", "two", "crowd", "xL", "xR", "two"]


def hook_setup(c):
    c.hud["badge"] = ("HOOK", "!!")
    c.alarm = True
    c.spot = ("sam", "dario")
    c.wash = (255, 40, 50)
    c.crowd = "hype"
    c.shot = CHANT_SHOTS[(c.beat_i // 2) % len(CHANT_SHOTS)]
    for who in ("sam", "dario"):
        s = c.st[who]
        s["back_arm"] = "mic"
        s["front_arm"] = "pump" if c.ph < 0.5 else "up"
        s["bob"] = 1 if c.ph < 0.35 else 0
        s["mouth"] = mouth_for(c, who, rest="teeth")
        s["brows"] = "angry"


def outro_setup(c):
    c.hud["badge"] = ("FINAL", "??")
    c.hud["combo"] = False
    c.spot = ("sam", "dario")
    c.wash = NEON_PINK
    for who in ("sam", "dario"):
        s = c.st[who]
        s["bob"] = 1 if (c.beat_i % 2 == 0 and c.ph < 0.35) else 0
        s["back_arm"], s["front_arm"] = ("down", "hip") if who == "sam" else ("cross", "cross")
        s["mouth"], s["brows"] = ("smirk", "smug") if who == "sam" else ("frown", "angry")
    c.shot = "two"


def ko_angle(age):
    if age < 0.25:
        return 0.0
    a = age - 0.25
    if a < 0.4:
        return 90 * (a / 0.4) ** 2
    return 90 - 10 * abs(math.sin((a - 0.4) * 11)) * math.exp(-(a - 0.4) * 5)


def reprise_setup(c):
    t = c.t
    age = t - TL.FINAL_KO
    c.hud["badge"] = ("K.O.", "")
    c.hud["combo"] = False
    c.alarm = t < 194.6
    c.pump = t < 194.6
    c.crowd = "hype" if t < 194.6 else "still"
    c.spot = ("sam", "dario")
    c.wash = (255, 40, 50) if t < 194.6 else None
    c.karaoke = t < 194.6
    for who in ("sam", "dario"):
        s = c.st[who]
        s["x"] = 112 if who == "sam" else 208
        if age < 0.25:
            s["back_arm"], s["front_arm"] = "down", "punch"
            s["mouth"], s["brows"], s["eyes"] = "shout", "angry", "wide"
        else:
            s["back_arm"], s["front_arm"] = "down", "up"
            s["mouth"], s["brows"], s["eyes"] = "o", "worried", "x"
            s["rot"] = ko_angle(age) * (1 if who == "sam" else -1)
            s["pivot"] = 12
            s["dizzy"] = age > 0.7
    if age < 0.75:
        c.shot = "two"
    elif t < 193.0:
        c.shot = ["wide", "mid", "two", "crowd"][(c.beat_i // 2) % 4]
    else:
        c.shot = "wide"
    if 0 <= age < 2 / FPS:
        c.add_flash(0.9)
    if 0 <= age < 0.5:
        c.add_shake(20 * (1 - age / 0.5))
    c.extra.append(ko_overlay)


def ko_overlay(c):
    t = c.t
    age = t - TL.FINAL_KO
    yield "ui"
    if t < 194.6:
        confetti(c.ui, t, n=70, area=(0, 30, W, 150))
    yield "top"
    if 0 <= age < 2.6:
        fnt = PRESS24 if age > 2 / FPS else PRESS16
        if age < 2.0 or c.f % 2 == 0:
            big_text(c.ui, (W // 2, 52), "DOUBLE", PRESS16, top=WHITE, bottom=(255, 170, 170), anchor="ma")
            big_text(c.ui, (W // 2, 72), "K.O.!", fnt, top=(255, 90, 90), bottom=(190, 20, 40), anchor="ma")


# --- the stage --------------------------------------------------------------

def stage_frame(c):
    sec = c.sec
    if sec == "intro":
        sign_setup(c)
    elif sec == "hype":
        hype_setup(c)
    elif sec in RAPPER:
        verse_setup(c)
    elif sec == "hook":
        hook_setup(c)
    elif sec == "outro":
        outro_setup(c)
    else:
        reprise_setup(c)
    blink_eyes(c)
    if sec in RAPPER or sec in ("outro",):
        apply_hits(c)
        hit_shake_flash(c)
    if sec == "end":
        c.extra.append(end_popup)
    runner = GagRunner(active_gags(c))
    if not c.lock_shot and sec in RAPPER:
        h = TL.last_hit(c.t, window=0.7)
        if h and h["big"] and h["attacker"] != "both":
            c.shot = "cL" if h["target"] == "sam" else "cR"
    c.cam = Cam(*(SHOTS[c.shot] if isinstance(c.shot, str) else c.shot))

    v = c.venue
    world = venue_variant(v["lit"], v["neon"], v["live"]).copy()
    c.world = world
    if c.wash and v["lit"]:
        dens = 0.16 * max(0.0, 1 - c.ph / 0.5)
        if dens > 0.01:
            dither_rect(world, (0, 0, W, WALL_BOTTOM), c.wash, density=dens, blend=0.3)
    if c.pump and v["lit"] and c.ph < 0.18:
        draw_speaker(world, 4, WALL_BOTTOM - 36, pump=1)
        draw_speaker(world, W - 31, WALL_BOTTOM - 36, pump=1)
    if c.alarm:
        beacons(world, c.t)
    if c.spot and v["lit"]:
        spotlights(world, c.spot)
    runner.run("back")
    for who in ("sam", "dario"):
        draw_char(c, world, who)
    runner.run("front")
    if c.crowd:
        draw_crowd(world, c.t, c.crowd)
    runner.run("crowd")
    if c.alarm:
        dither(world, 0.12 + 0.22 * max(0.0, 1 - c.ph / 0.6), (255, 20, 40), blend=0.3)
    if c.flash > 0:
        dither(world, c.flash, c.flash_color)

    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_hud(c)
    runner.run("ui")
    draw_karaoke(c)
    if c.hitfx:
        draw_hit_fx(c)
    runner.run("top")
    return compose(world, c.ui, c.cam, shake_offset(c))


def end_popup(c):
    t = c.t
    yield "top"
    if t < 194.66:
        return
    ui = c.ui
    x, y = 90, 62
    dy = pop_dy(t - 194.66) or 0
    pressed = t >= 195.45
    draw_popup(ui, x, y + dy, "ALT-F4.EXE", "Close ALT-F4?", ["YES", "NO"], focus=None, cursor=False)
    w = max(96, text_width("Close ALT-F4?", PRESS) + 36)
    bx = x + (w - 66) // 2
    box = (bx, y + dy + 34, bx + 29, y + dy + 45)
    d = ImageDraw.Draw(ui)
    if pressed:
        d.rectangle(box, fill=(0, 0, 0))
        bevel(d, (box[0] + 1, box[1] + 1, box[2] - 1, box[3] - 1), raised=False)
        silk(d, ((box[0] + box[2]) // 2 + 2, box[1] + 5), "YES", (0, 0, 0), anchor="ma")
    p = ease_out(ramp(t, 194.9, 195.3))
    cx, cy = lerp(262, (box[0] + box[2]) // 2, p), lerp(160, (box[1] + box[3]) // 2, p)
    ui.paste(CURSOR, (int(cx), int(cy) + (1 if pressed else 0)), CURSOR)


# --- set pieces -------------------------------------------------------------

def black_ui():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def upscale_rgb(img):
    return img.convert("RGB").resize((W * SCALE, H * SCALE), Image.NEAREST)


def cold_open(c):
    t = c.t
    scr = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(scr)
    d.fontmode = "1"
    if t >= 0.3:
        n = int(clamp((t - 0.36) / 0.055, 0, 10))
        d.text((12, 14), "C:\\>" + "ALT-F4.EXE"[:n], font=PRESS, fill=(200, 200, 200))
        cur_on = int(t * 4) % 2 == 0 or 0.36 < t < 0.95
        if t < 0.98:
            if cur_on:
                d.text((12 + text_width("C:\\>" + "ALT-F4.EXE"[:n], PRESS), 14), "_", font=PRESS,
                       fill=(200, 200, 200))
        else:
            d.text((12, 26), "LOADING RAP_BATTLE.DLL...", font=PRESS, fill=(200, 200, 200))
    frame = upscale_rgb(scr)
    if t >= 1.1:
        p = ramp(t, 1.1, 1.45)
        c2 = Ctx(max(t, 1.46))
        c2.t = t
        c2.ln = None
        scene = stage_frame(c2)
        arr = np.asarray(scene).astype(np.float32)
        arr = arr + (255 - arr) * (1 - p) * 0.7
        band = max(6, int(1080 * ease_out(p) ** 1.5))
        out = np.zeros_like(arr)
        y0 = 540 - band // 2
        out[y0:y0 + band] = arr[y0:y0 + band]
        out[max(0, y0 - 3):y0] = 255
        out[y0 + band:y0 + band + 3] = 255
        frame = Image.fromarray(out.clip(0, 255).astype(np.uint8))
    return frame


# summit photo op ----------------------------------------------------------

ROW = [34, 84, 136, 184, 236, 286]
PHOTO_FEET = 150


@lru_cache(maxsize=2)
def summit_backdrop():
    img = Image.new("RGB", (W, H), (16, 22, 52))
    d = ImageDraw.Draw(img)
    for y in range(0, 122):
        d.line([(0, y), (W, y)], fill=mix((24, 34, 86), (12, 16, 40), y / 122))
    for x in range(8, W, 16):
        for y in range(40, 118, 12):
            d.point((x + (y // 12) % 2 * 8, y), fill=(40, 56, 120))
    d.rectangle([0, 8, W, 13], fill=(255, 153, 51))
    d.rectangle([0, 14, W, 19], fill=(236, 236, 236))
    d.rectangle([0, 20, W, 25], fill=(19, 136, 8))
    d.ellipse([155, 14, 165, 19], outline=(0, 0, 128))
    big_text(img, (W // 2, 31), "AI IMPACT SUMMIT", PRESS, top=WHITE, bottom=(200, 210, 255), anchor="ma",
             thick=1, shadow=1)
    d.rectangle([0, 122, W, H], fill=(56, 44, 70))
    for y in range(124, 162, 5):
        d.line([(0, y), (W, y)], fill=(64, 50, 80))
    d.rectangle([0, 162, W, H], fill=(20, 14, 26))
    for i, x in enumerate(range(2, W, 6)):
        col = (255, 150, 30) if i % 2 else (255, 200, 40)
        d.ellipse([x - 2, 159, x + 2, 163], fill=col)
        d.point((x, 165), fill=(40, 120, 40))
    return img


def silhouette(img, x, y, hands, tone=(40, 44, 72), rim=(96, 106, 150)):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([x - 8, y - 17, x - 2, y - 1], fill=tone)
    d.rectangle([x + 2, y - 17, x + 8, y - 1], fill=tone)
    d.rounded_rectangle([x - 12, y - 39, x + 12, y - 14], radius=6, fill=tone)
    d.ellipse([x - 13, y - 67, x + 13, y - 38], fill=tone)
    for f, (hx, hy) in hands:
        d.line([(x + f * 9, y - 33), (hx, hy)], fill=tone, width=6, joint="curve")
        d.ellipse([hx - 3, hy - 3, hx + 3, hy + 3], fill=tone)
    arr = np.array(layer)
    a = arr[:, :, 3] > 0
    arr[_grow(a) & ~a] = K + (255,)
    edge = a & ~np.roll(a, 1, axis=1)
    arr[edge] = rim + (255,)
    lay = Image.fromarray(arr, "RGBA")
    img.paste(lay, (0, 0), lay)


def draw_bandage(img, a):
    d = ImageDraw.Draw(img)
    x, y = int(a["hx"] + 22), int(a["hy"] + 8)
    d.rectangle([x - 1, y - 4, x + 7, y + 4], fill=K)
    d.rectangle([x, y - 3, x + 6, y + 3], fill=(250, 236, 214))
    d.line([(x + 1, y - 2), (x + 5, y + 2)], fill=(210, 180, 160))
    d.line([(x + 5, y - 2), (x + 1, y + 2)], fill=(210, 180, 160))


def photo_op(c, reprise=False):
    t = c.t
    world = summit_backdrop().copy()
    c.world = world
    y = PHOTO_FEET
    meet = [((ROW[i] + ROW[i + 1]) / 2, y - 50) for i in range(5)]
    ends = [(ROW[0] - 25, y - 50), (ROW[5] + 25, y - 50)]
    for i in (0, 1, 4, 5):
        left = meet[i - 1] if i > 0 else ends[0]
        right = meet[i] if i < 5 else ends[1]
        silhouette(world, ROW[i], y, [(-1, left), (1, right)])
    if reprise:
        turned = False
        ex = dict(sam=dict(eyes="happy", mouth="grin", brows="worried"),
                  dario=dict(eyes="happy", mouth="grin", brows="worried"))
        inner = "reach"
    else:
        turned = t >= 6.3
        if t < 5.54:
            ex = dict(sam=dict(eyes="open", mouth="grin", brows="neutral"),
                      dario=dict(eyes="open", mouth="closed", brows="neutral"))
        elif not turned:
            ex = dict(sam=dict(eyes="squint", mouth="frown", brows="angry"),
                      dario=dict(eyes="squint", mouth="frown", brows="angry"))
        else:
            ex = dict(sam=dict(eyes="blink", mouth="frown", brows="angry"),
                      dario=dict(eyes="blink", mouth="frown", brows="angry"))
        inner = "up"
    anchors = {}
    for who, x in (("sam", ROW[2]), ("dario", ROW[3])):
        facing = (1 if who == "sam" else -1) * (-1 if turned else 1)
        if turned:
            arms = dict(front_arm="reach", back_arm="down")
        else:
            arms = dict(back_arm="reach", front_arm=inner)
        anchors[who] = draw_character(world, who, x, y, facing=facing, **ex[who], **arms)
    if reprise:
        for who in ("sam", "dario"):
            draw_bandage(world, anchors[who])
            a = anchors[who]
            star = ascii_sprite(DIZZY)
            for k in range(3):
                ang = t * 7 + k * 2 * math.pi / 3
                world.paste(star, (int(a["hx"] + 18 + 15 * math.cos(ang)) - 2,
                                   int(a["hy"] - 6 + 4 * math.sin(ang)) - 2), star)
    rng = random.Random(3)
    d = ImageDraw.Draw(world)
    for x in range(-6, W + 12, 22):
        hx = x + rng.randint(-4, 4)
        hy = 170 + rng.randint(-2, 3)
        d.ellipse([hx - 7, hy - 7, hx + 7, hy + 7], fill=(10, 8, 16))
        d.rounded_rectangle([hx - 12, hy + 4, hx + 12, H + 8], radius=5, fill=(10, 8, 16))
        d.rectangle([hx - 6, hy - 12, hx + 6, hy - 4], fill=(24, 24, 30))
        d.rectangle([hx - 2, hy - 10, hx + 2, hy - 6], fill=(70, 80, 110))
        if rnd("pap", x, c.f // 2) < 0.06:
            burst(world, hx + 4, hy - 14, 3, 9, WHITE, spikes=8, rot=c.f)

    flashes = (190.12, 191.89) if reprise else (4.42, 5.26)
    for ft in flashes:
        if 0 <= t - ft < 0.25:
            c.add_flash(1.0 - (t - ft) / 0.25)
    if reprise:
        shot = (160, 96, 6) if t < 190.6 else (160, 104, 9) if t < 191.9 else (160, 100, 12)
    else:
        shot = (160, 90, 6) if t < 5.54 else (160, 100, 9) if t < 6.2 else (160, 98, 12)
    c.cam = Cam(*shot)
    if c.flash > 0:
        dither(world, c.flash, WHITE)

    ui = c.ui = black_ui()
    d = ImageDraw.Draw(ui)
    for (x0, y0), (dx, dy) in (((6, 36), (1, 1)), ((313, 36), (-1, 1)), ((6, 140), (1, -1)),
                               ((313, 140), (-1, -1))):
        d.line([(x0, y0), (x0 + dx * 10, y0)], fill=WHITE, width=1)
        d.line([(x0, y0), (x0, y0 + dy * 10)], fill=WHITE, width=1)
    if int(t * 2) % 2 == 0:
        d.ellipse([12, 8, 17, 13], fill=(255, 40, 40))
    silk(d, (21, 8), "REC", WHITE)
    caption(ui, 10, 124, "TAKE 2" if reprise else "NEW DELHI")
    stamp_txt = "'26  LATER" if reprise else "'26  2  19"
    outline_text(ui, (W - 10, 126), stamp_txt, PRESS, (255, 150, 40), outline=(90, 30, 0), anchor="ra")
    if not reprise:
        if 4.8 <= t < 6.3:
            p = ease_out(ramp(t, 4.8, 5.0))
            cx, cy = c.cam.ui(160, y - 50)
            r = (16 + (1 - p) * 30) * c.cam.f
            for w_, col in ((5, K), (3, (255, 40, 40))):
                d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], outline=col, width=w_)
            big_text(ui, (cx + r + 4, cy - r - 4), "?!", PRESS16, top=(255, 90, 90), bottom=(200, 20, 30))
        if t >= 6.3:
            age = t - 6.3
            for who in ("sam", "dario"):
                a = anchors[who]
                hx, hy = c.cam.ui(a["hx"] + HW / 2, a["hy"])
                off = (pop_dy(age) or 0)
                side = -1 if who == "sam" else 1
                bubble(ui, hx + side * 22, hy + 8 + off, "HMPH!", tail=(hx + side * 6, hy + 20))
    else:
        if t >= 190.12:
            big_text(ui, (W // 2, 48), "FRIENDS?", PRESS16, top=WHITE, bottom=(255, 170, 200), anchor="ma")
    draw_karaoke(c)
    return compose(world, ui, c.cam, shake_offset(c))


# fists --------------------------------------------------------------------

@lru_cache(maxsize=4)
def big_fist(who):
    sleeve, cuff = ((58, 60, 70), (38, 40, 48)) if who == "sam" else ((150, 190, 236), (236, 242, 250))
    p = Prop(124, 60)
    d = p.d
    d.rectangle((0, 15, 74, 45), fill=sleeve)
    d.line([(0, 43), (74, 43)], fill=mix(sleeve, (0, 0, 0), 0.3), width=3)
    d.rectangle((66, 12, 77, 48), fill=cuff)
    d.rounded_rectangle((74, 10, 106, 50), radius=6, fill=SKIN)
    for i in range(4):
        y0 = 10 + i * 10
        d.rounded_rectangle((94, y0, 117, y0 + 9), radius=4, fill=SKIN)
    d.rounded_rectangle((80, 38, 106, 49), radius=4, fill=SKIN)
    img = p.done()
    dd = ImageDraw.Draw(img)
    for i in range(1, 4):
        y0 = 10 + i * 10
        dd.line([(96, y0 - 1), (116, y0 - 1)], fill=K)
    dd.rounded_rectangle((80, 37, 106, 49), radius=4, outline=K)
    for i in range(4):
        dd.line([(113, 12 + i * 10), (115, 14 + i * 10)], fill=(255, 226, 200))
        dd.line([(96, 17 + i * 10), (112, 17 + i * 10)], fill=SKIN_SH)
    dd.line([(77, 12), (77, 48)], fill=K)
    if who == "dario":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def fists(c):
    t = c.t
    world = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(world)
    split = [(172, 0), (148, H)]
    d.polygon([(0, 0), split[0], split[1], (0, H)], fill=(10, 86, 68))
    d.polygon([split[0], (W, 0), (W, H), split[1]], fill=(150, 66, 42))
    hit = 8.92
    for i in range(14):
        yy = (i * 13 + int(t * 300)) % H
        d.line([(0, yy), (150, yy)], fill=(16, 110, 88))
        d.line([(170, (yy + 6) % H), (W, (yy + 6) % H)], fill=(176, 84, 54))
    d.line(split, fill=WHITE, width=3)
    if t < 8.7:
        p = ease_out(ramp(t, 7.7, 8.1))
        gap = lerp(170, 110, p) + math.sin(t * 40) * 2 * ramp(t, 8.2, 8.7)
    elif t < hit:
        gap = lerp(110, 0, ramp(t, 8.7, hit) ** 2)
    else:
        gap = 0 + max(0.0, 1 - (t - hit) / 0.3) * math.sin((t - hit) * 60) * 3
    cy = 92
    sf, df = big_fist("sam"), big_fist("dario")
    world.paste(sf, (int(W // 2 - gap / 2 - 117), cy - 30), sf)
    world.paste(df, (int(W // 2 + gap / 2 - 6), cy - 30), df)
    ui = c.ui = black_ui()
    if t >= hit:
        age = t - hit
        if age < 0.45:
            burst(world, W // 2, cy, 18 + age * 60, 44 + age * 90, GOLD, spikes=14, rot=age * 2)
            burst(world, W // 2, cy, 10 + age * 40, 24 + age * 60, WHITE, spikes=14, rot=age * 2 + 0.2)
        r = 20 + age * 260
        dd = ImageDraw.Draw(world)
        dd.ellipse([W // 2 - r, cy - r * 0.6, W // 2 + r, cy + r * 0.6], outline=WHITE, width=2)
        fnt = PRESS24
        big_text(ui, (W // 2, 30 + (pop_dy(age) or 0)), "POW!", fnt, top=GOLD, bottom=(255, 90, 30), anchor="ma")
        if age < 2 / FPS:
            c.add_flash(0.8)
        c.add_shake(18 * max(0.0, 1 - age / 0.4))
    if c.flash > 0:
        dither(world, c.flash, WHITE)
    draw_karaoke(c)
    return compose(world, ui, Cam(160, 90, 6), shake_offset(c))


# VS screen ----------------------------------------------------------------

@lru_cache(maxsize=4)
def vs_sprite(who):
    layer = Image.new("RGBA", (110, 92), (0, 0, 0, 0))
    if who == "sam":
        draw_character(layer, "sam", 55, 88, facing=1, mouth="smirk", brows="smug",
                       back_arm="down", front_arm="hip")
    else:
        draw_character(layer, "dario", 55, 88, facing=-1, mouth="frown", brows="angry",
                       back_arm="cross", front_arm="cross")
    return scaled(layer, 2)


def vs_screen(c):
    t = c.t
    world = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(world)
    d.polygon([(0, 0), (176, 0), (144, H), (0, H)], fill=(8, 70, 56))
    d.polygon([(176, 0), (W, 0), (W, H), (144, H)], fill=(120, 52, 34))
    off = int(t * 40) % 16
    for k in range(-20, 40):
        x = k * 16 + off
        d.line([(x, 0), (x - 90, H)], fill=(12, 84, 68))
        d.line([(x + 8, 0), (x + 98, H)], fill=(136, 62, 40))
    d.line([(176, 0), (144, H)], fill=WHITE, width=3)
    ui = c.ui = black_ui()
    for who, t_in, name, sub, team, side in (("sam", 9.62, "SAM", "ALTMAN", "OPENAI", -1),
                                             ("dario", 12.72, "DARIO", "AMODEI", "ANTHROPIC", 1)):
        if t < t_in:
            continue
        p = ease_out(ramp(t, t_in, t_in + 0.3))
        spr = vs_sprite(who)
        cx = (80 if who == "sam" else 240) + side * (1 - p) * 200
        world.paste(spr, (int(cx - 110), 20), spr)
        name_t = 9.78 if who == "sam" else 13.31
        sub_t = 11.2 if who == "sam" else 14.2
        nx = 10 if who == "sam" else W - 10
        anchor = "la" if who == "sam" else "ra"
        label(ui, (nx, 14), "1P" if who == "sam" else "2P", bg=TEAM[who], fg=WHITE, anchor=anchor, pad=2)
        label(ui, (nx, 28), team, bg=K, fg=WHITE, anchor=anchor, pad=2)
        if t >= name_t:
            big_text(ui, (nx, 118 + (pop_dy(t - name_t) or 0)), name, PRESS24,
                     top=WHITE, bottom=mix(TEAM[who], WHITE, 0.4), anchor=anchor)
        if t >= sub_t:
            big_text(ui, (nx, 146 + (pop_dy(t - sub_t) or 0)), sub, PRESS16,
                     top=mix(TEAM[who], WHITE, 0.5), bottom=TEAM[who], anchor=anchor)
    if t >= 14.64:
        age = t - 14.64
        sc = 3 if age < 1 / FPS else 2
        base = Image.new("RGBA", (70, 40), (0, 0, 0, 0))
        big_text(base, (35, 8), "VS", PRESS24, top=GOLD, bottom=(255, 90, 30), anchor="ma")
        im = scaled(base, sc)
        ui.paste(im, (W // 2 - im.width // 2, 80 - im.height // 2), im)
        if age < 2 / FPS:
            c.add_flash(0.7)
        c.add_shake(14 * max(0.0, 1 - age / 0.35))
    if 9.62 <= t < 9.62 + 2 / FPS:
        c.add_flash(0.6)
    if 15.18 <= t < 15.18 + 2 / FPS:
        c.add_flash(0.5)
    if c.flash > 0:
        dither(world, c.flash, WHITE)
    return compose(world, ui, Cam(160, 90, 6), shake_offset(c))


# shutdown -----------------------------------------------------------------

@lru_cache(maxsize=1)
def last_stage_frame():
    return stage_frame(Ctx(195.58))


def shutdown(c):
    t = c.t
    out = np.zeros((H * SCALE, W * SCALE, 3), np.float32)
    if t < 196.35:
        src = np.asarray(last_stage_frame(), np.float32)
        p = ramp(t, 195.6, 195.9)
        q = ramp(t, 195.9, 196.15)
        fade = 1 - ramp(t, 196.15, 196.35)
        hgt = max(4, int(1080 * (1 - p) ** 2))
        wid = max(8, int(1920 * (1 - q) ** 2))
        img = Image.fromarray(src.astype(np.uint8)).resize((wid, hgt), Image.BILINEAR)
        arr = np.asarray(img, np.float32)
        arr = arr + (255 - arr) * min(1.0, p * 1.2)
        y0, x0 = 540 - hgt // 2, 960 - wid // 2
        out[y0:y0 + hgt, x0:x0 + wid] = arr * fade
        return Image.fromarray(out.clip(0, 255).astype(np.uint8))
    scr = Image.new("RGB", (W, H), (0, 0, 0))
    if t >= 196.6:
        col = (255, 136, 0)
        d = ImageDraw.Draw(scr)
        d.fontmode = "1"
        d.text((W // 2, 80), "It's now safe to turn off", font=PRESS, fill=col, anchor="ma")
        d.text((W // 2, 94), "your computer.", font=PRESS, fill=col, anchor="ma")
    return upscale_rgb(scr)


# --- dispatcher -------------------------------------------------------------

def render_frame(t):
    c = Ctx(t)
    if t < 1.45:
        return cold_open(c)
    if t < 2.96:
        return stage_frame(c)
    if t < 7.7:
        return photo_op(c)
    if t < 9.62:
        return fists(c)
    if t < 15.45:
        return vs_screen(c)
    if 189.2 <= t < 192.95:
        return photo_op(c, reprise=True)
    if t >= 195.6:
        return shutdown(c)
    return stage_frame(c)
