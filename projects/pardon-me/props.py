"""Props and text effects for the gags: the marker kit for the flip chart, paper cards, tweets
("Truths"), stamps, smoke, and the comic text effects bound to this video's ink and fonts.

The marker kit draws progressively, like a hand at work: `p` (0..1) or an `age`
(seconds since the stroke started) says how much of a stroke or a word is down.
Everything takes an image and draws straight onto it (a chart page, the world or
the UI); sprites are cached RGBA images outlined in ink.
"""
import math
from functools import lru_cache, partial

from PIL import Image, ImageDraw

from engine import (C, INK, PRESS, PRESS16, PRESS24, SILK, Canvas, blend, clamp, col, rnd, text_width)
from pixelart import fx, pixel

GOLD, WHITE, RED = C["gold"], C["white"], C["red"]
ORANGE = C["orange"]
MK = {"black": C["mk_black"], "red": C["mk_red"], "blue": C["mk_blue"], "green": C["mk_green"]}

# --- text and comic effects (pixelart.fx in this video's ink) -----------------------------------

big_text = partial(fx.big_text, outline=INK, ink=INK)
pop_text = partial(fx.pop_text, outline=INK, ink=INK)
bubble = partial(fx.bubble, ink=INK, fill=WHITE)
strike = partial(fx.strike, ink=INK, color=RED)
arrow = partial(fx.arrow, ink=INK, color=GOLD)
burst = partial(fx.burst, ink=INK)
sparkle, typed = fx.sparkle, fx.typed


def label(img, xy, s, fnt=SILK, bg=WHITE, fg=INK, pad=2, anchor="la", border=INK):
    """Text on a flat plate with a 1px border."""
    silk = fnt is SILK
    return fx.label(img, xy, s, fnt, bg, fg, pad, anchor, border, th=6 if silk else None, text_dy=-2 if silk else 0)


def stamp(img, cx, cy, s, color=RED, angle=-12, size=16, age=1.0):
    """An ink stamp that slams down; `size` is 8, 16 or 24."""
    fx.stamp(img, cx, cy, s, {8: PRESS, 16: PRESS16, 24: PRESS24}[size], tuple(col(color)), angle, age)


def _rgba(img, c):
    c = tuple(col(c))[:3]
    return c + (255,) if img.mode == "RGBA" else c


# --- the marker kit -----------------------------------------------------------------------------

def mk(c):
    """A marker colour by name (black red blue green) or any palette name / RGB."""
    return MK.get(c, None) or col(c)


def polyline_part(pts, p):
    """The first `p` (0..1) of a polyline, by length."""
    if p >= 1:
        return list(pts)
    if p <= 0 or len(pts) < 2:
        return pts[:1]
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(segs) or 1.0
    want = total * p
    out = [pts[0]]
    for (a, b), s in zip(zip(pts, pts[1:]), segs):
        if want <= s:
            k = want / s if s else 0
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k))
            return out
        out.append(b)
        want -= s
    return out


def stroke(img, pts, color="black", p=1.0, width=1):
    """A marker stroke along `pts`, drawn up to `p` of its length."""
    part = polyline_part([tuple(map(float, q)) for q in pts], clamp(p, 0, 1))
    if len(part) >= 2:
        ImageDraw.Draw(img).line(part, fill=_rgba(img, mk(color)), width=width, joint="curve")
    elif part and p > 0:
        ImageDraw.Draw(img).point(part[0], fill=_rgba(img, mk(color)))


def circle_pts(cx, cy, rx, ry=None, start=-100, turns=1.08, n=40):
    """Points round a hand-drawn ellipse that overshoots its start a little."""
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(math.radians(start + 360 * turns * k / n)),
             cy + ry * math.sin(math.radians(start + 360 * turns * k / n))) for k in range(n + 1)]


def ring(img, cx, cy, rx, ry=None, color="red", p=1.0, width=1):
    """Circle something in marker, drawn round as p goes 0 -> 1."""
    stroke(img, circle_pts(cx, cy, rx, ry), color, p, width)


def underline(img, x0, x1, y, color="red", p=1.0, width=1, wave=0):
    pts = [(x0 + (x1 - x0) * k / 12, y + (wave * math.sin(k * 1.4) if wave else 0)) for k in range(13)]
    stroke(img, pts, color, p, width)


def cross_out(img, box, color="red", p=1.0, width=1):
    """An X through a box: the first stroke over p 0-0.5, the second over 0.5-1."""
    x0, y0, x1, y1 = box
    stroke(img, [(x0, y0), (x1, y1)], color, p * 2, width)
    if p > 0.5:
        stroke(img, [(x1, y0), (x0, y1)], color, (p - 0.5) * 2, width)


def check(img, x, y, color="green", p=1.0, width=1, size=6):
    stroke(img, [(x, y), (x + size * 0.35, y + size * 0.4), (x + size, y - size * 0.6)], color, p, width)


def marker_arrow(img, a, b, color="red", p=1.0, width=1, head=4):
    """An arrow from a to b, the head drawn once the shaft arrives."""
    stroke(img, [a, b], color, p / 0.8 if p < 0.8 else 1.0, width)
    if p >= 0.8:
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        hp = (p - 0.8) / 0.2
        for s in (-1, 1):
            tip = (b[0] - head * math.cos(ang + s * 0.6), b[1] - head * math.sin(ang + s * 0.6))
            stroke(img, [b, tip], color, hp, width)


def write(img, xy, s, color="black", age=1e9, cps=22.0, fnt=SILK, anchor="la", bold=False):
    """Hand-lettered marker text that writes itself at `cps` characters a second from age 0.
    Returns the box of the whole text (written or not), so things can be placed round it."""
    shown = s if age >= 1e8 else s[:max(0, int(age * cps))]
    x, y = xy
    w = text_width(s, fnt)
    h = 6 if fnt is SILK else fnt.size
    x -= {"l": 0, "m": w // 2, "r": w}[anchor[0]]
    y -= {"a": 0, "t": 0, "m": h // 2, "b": h}[anchor[1]]
    if shown and age >= 0:
        d = ImageDraw.Draw(img)
        d.fontmode = "1"
        dy = -2 if fnt is SILK else 0
        d.text((x, y + dy), shown, font=fnt, fill=_rgba(img, mk(color)))
        if bold:
            d.text((x + 1, y + dy), shown, font=fnt, fill=_rgba(img, mk(color)))
    return (x, y, x + w + (1 if bold else 0), y + h)


def write_lines(img, x, y, lines, color="black", age=1e9, cps=22.0, fnt=SILK, anchor="la", gap=9, bold=False):
    """Several lines of marker text, each starting when the one before is done."""
    used = 0.0
    for i, s in enumerate(lines):
        write(img, (x, y + i * gap), s, color, age - used / cps, cps, fnt, anchor, bold)
        used += len(s)


# --- the flip chart -------------------------------------------------------------------------------

def new_page(w, h):
    """A blank flip-chart sheet: off-white, with faint blue rules near the top."""
    img = Image.new("RGB", (w, h), C["paper"])
    d = ImageDraw.Draw(img)
    for x in range(0, w, 2):
        d.point((x, 2), fill=C["paper_ln"])
    d.line([(0, h - 1), (w, h - 1)], fill=C["paper_sh"])
    return img


def page_title(img, s, color="black", age=1e9, y=3, underline_color=None, fnt=SILK):
    """A page heading, centred and underlined."""
    w = img.width
    box = write(img, (w // 2, y), s, color, age, fnt=fnt, anchor="ma", bold=True)
    if underline_color and age > len(s) / 22.0:
        underline(img, box[0] - 1, box[2] + 1, box[3] + 2, underline_color, (age - len(s) / 22.0) / 0.25)
    return box


# --- doodles: marker drawings used on more than one page ----------------------------------------------

def bomb_doodle(img, cx, cy, r, p=1.0, color="black", fuse=True, spark_t=0.0):
    """The cartoon bomb: a round body, a cap and a curly fuse (Bibi, the UN, 2012)."""
    stroke(img, circle_pts(cx, cy, r, start=-60, turns=1.02), color, p / 0.6, 1)
    if p > 0.6:
        q = (p - 0.6) / 0.4
        stroke(img, [(cx + r * 0.45, cy - r * 0.9), (cx + r * 0.7, cy - r * 1.2), (cx + r * 1.0, cy - r * 0.95),
                     (cx + r * 0.75, cy - r * 0.65)], color, q * 2, 1)
        if fuse and q > 0.5:
            fx_, fy = cx + r * 0.85, cy - r * 1.1
            stroke(img, [(fx_, fy), (fx_ + 2, fy - 3), (fx_ + 5, fy - 3), (fx_ + 6, fy - 6)], color, (q - 0.5) * 2, 1)
            if q >= 1 and spark_t:
                d = ImageDraw.Draw(img)
                k = int(spark_t * 12) % 2
                for a in range(0, 360, 90):
                    rr = 2 + k
                    d.point((fx_ + 6 + rr * math.cos(math.radians(a + 45 * k)),
                             fy - 6 + rr * math.sin(math.radians(a + 45 * k))), fill=_rgba(img, "mk_red"))


def stick_figure(img, x, y, color="black", p=1.0, h=14, arms="down", hair=None):
    """A stick figure with its feet at (x, y). `hair` adds a scribble: "trump" (a swoop) or "bibi" (grey)."""
    head = h * 0.3
    hy = y - h
    pts = [
        circle_pts(x, hy + head / 2, head / 2, n=14),
        [(x, hy + head), (x, y - h * 0.35)],
        [(x, y - h * 0.35), (x - h * 0.22, y)], [(x, y - h * 0.35), (x + h * 0.22, y)],
    ]
    if arms == "up":
        pts += [[(x, hy + head + 2), (x - h * 0.3, hy)], [(x, hy + head + 2), (x + h * 0.3, hy)]]
    elif arms == "out":
        pts += [[(x - h * 0.35, hy + head + 3), (x + h * 0.35, hy + head + 3)]]
    else:
        pts += [[(x, hy + head + 2), (x - h * 0.25, y - h * 0.4)], [(x, hy + head + 2), (x + h * 0.25, y - h * 0.4)]]
    n = len(pts)
    for i, seg in enumerate(pts):
        stroke(img, seg, color, (p * n - i), 1)
    if hair and p >= 1:
        if hair == "trump":
            stroke(img, [(x - head / 2, hy + 1), (x, hy - 2), (x + head / 2 + 3, hy - 1), (x + head / 2 + 1, hy + 1)],
                   "orange", 1.0, 2)
        elif hair == "bibi":
            stroke(img, [(x - head / 2, hy + 2), (x - 1, hy - 1), (x + head / 2 - 1, hy)], (150, 150, 166), 1.0, 2)


# --- props shared by several gags ------------------------------------------------------------------

@lru_cache(maxsize=64)
def card_sprite(w, h, color="paper"):
    """A blank poster card held up at the rostrum."""
    s = Canvas(w, h)
    s.rect((0, 0, w - 1, h - 1), color)
    s.rect((0, h - 2, w - 1, h - 1), "paper_sh")
    return s.done()


def truth_post(img, x, y, lines, age=1e9, handle="@realDonaldTrump", w=128, likes=None):
    """A "Truth" (social post) card at (x, y): avatar, handle, the text typing in. Returns its box."""
    fnt = SILK
    h = 18 + 8 * len(lines) + (9 if likes is not None else 0)
    d = ImageDraw.Draw(img)
    d.rectangle((x - 1, y - 1, x + w, y + h), fill=_rgba(img, INK))
    d.rectangle((x, y, x + w - 1, y + h - 1), fill=_rgba(img, "white"))
    d.rectangle((x, y, x + w - 1, y + 2), fill=_rgba(img, (92, 74, 230)))
    d.ellipse((x + 3, y + 5, x + 11, y + 13), fill=_rgba(img, "thair"))
    d.ellipse((x + 4, y + 8, x + 10, y + 14), fill=_rgba(img, "tskin"))
    pixel.text(img, (x + 14, y + 4), handle, fnt, _rgba(img, INK)[:3], shadow=None)
    used = 0
    for i, s in enumerate(lines):
        shown = s[:max(0, int((age * 30) - used))]
        used += len(s)
        if shown:
            pixel.text(img, (x + 4, y + 15 + i * 8), shown, fnt, _rgba(img, INK)[:3], shadow=None)
    if likes is not None:
        pixel.text(img, (x + 4, y + h - 9), likes, fnt, (120, 110, 140), shadow=None)
    return (x, y, x + w, y + h)


def puff(img, x, y, age, size=1.0, seed=0, color=(214, 204, 220), drift=(-10, -6), life=1.6):
    """A puff of smoke or dust that billows out and thins (flat tints, no dither)."""
    if not 0 <= age < life:
        return
    r = (3 + 8 * min(1.0, age / 0.4)) * size
    fade = clamp(1.0 - age / life, 0, 1)
    for i in range(5):
        a = rnd("pf", seed, i) * 2 * math.pi
        cx = x + math.cos(a) * r * 0.6 + drift[0] * age
        cy = y + math.sin(a) * r * 0.4 + drift[1] * age
        rr = r * (0.5 + 0.4 * rnd("pr", seed, i))
        m = pixel.mask(lambda d: d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=255), img.size)
        blend(img, m, color, 0.75 * fade)


def speed_lines(img, cx, cy, r0, color=WHITE, n=24, seed=0, width=1):
    """Manga speed lines converging on (cx, cy), starting r0 out."""
    d = ImageDraw.Draw(img)
    for k in range(n):
        a = k * 2 * math.pi / n + rnd("sl", seed, k) * 0.2
        r1 = r0 + 30 + rnd("sl-l", seed, k) * 60
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)],
               fill=_rgba(img, color), width=width)


def confetti(img, box, t, seed=0, n=40, colors=("gold", "red", "blue", "white", "green")):
    """Confetti falling through a box."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = x0 + rnd("cf", seed, i) * (x1 - x0) + math.sin(t * 3 + i) * 3
        y = y0 + ((rnd("cy", seed, i) * (y1 - y0) + t * (30 + 20 * rnd("cv", seed, i))) % (y1 - y0))
        c = colors[i % len(colors)]
        if int(t * 8 + i) % 2:
            d.rectangle((x, y, x + 1, y), fill=_rgba(img, c))
        else:
            d.point((x, y), fill=_rgba(img, c))
