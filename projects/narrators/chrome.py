"""Screen furniture for the two kinds of footage in the video.

Sir David's sections are his nature documentary: a field camera's viewfinder,
lower-third captions with Latin names, a conservation-status scale, teletext
subtitles and episode titles. Morgan's sections are his films: letterbox bars,
a warm grade with grain and gate weave, subtitles in the lower bar, title
cards, film burn and end credits.

UI-layer functions draw on the 320x180 RGBA UI image (always at base scale);
`film_grade` works on the world image.
"""
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from engine import (C, INK, PRESS, PRESS16, SILK, H, W, clamp, col, dither_rect, ease_in,
                    ease_out, lerp, outline_text, ramp, rnd, text_width)
from pixelart import pixel

BAR = 23                     # letterbox bar height at 2.39:1
TELE_Y = 150                 # top of the teletext subtitle rows


def rect(img, box, color, outline=None):
    d = ImageDraw.Draw(img)
    fill = col(color) + ((255,) if img.mode == "RGBA" else ())
    ol = None if outline is None else col(outline) + ((255,) if img.mode == "RGBA" else ())
    d.rectangle(box, fill=fill, outline=ol)


# --- karaoke words ----------------------------------------------------------------------

def clean_word(w, upper=True):
    w = w.replace("’", "'").replace("“", '"').replace("”", '"')
    return w.upper() if upper else w


def wrap(words, fnt, width):
    rows, cur = [], []
    for i, w in enumerate(words):
        if cur and text_width(" ".join(words[j] for j in cur + [i]), fnt) > width:
            rows.append(cur)
            cur = [i]
        else:
            cur.append(i)
    return rows + [cur] if cur else rows


def sub_rows(rows, now, n=2):
    """The n rows to show: they scroll on a row as the singing reaches the last one shown."""
    k = next((r for r, row in enumerate(rows) if now <= row[-1]), len(rows) - 1)
    k0 = max(0, min(k - n + 1, len(rows) - n))
    return rows[k0:k0 + n]


def teletext_subs(ui, ln, now, y=TELE_Y, sung=C["text"], cur=C["tele"], todo=(190, 186, 200)):
    """Documentary subtitles: blocky words on black boxes, the sung word in teletext yellow."""
    words = [clean_word(w["w"]) for w in ln["words"]]
    rows = sub_rows(wrap(words, PRESS, W - 20), now)
    space = text_width(" ", PRESS)
    y0 = y + (11 if len(rows) == 1 else 0)
    for r, row in enumerate(rows):
        s = " ".join(words[i] for i in row)
        tw = text_width(s, PRESS)
        x = (W - tw) // 2
        yy = y0 + r * 12
        rect(ui, (x - 3, yy - 2, x + tw + 2, yy + 9), "band")
        for i in row:
            fill = sung if i < now else cur if i == now else todo
            pixel.text(ui, (x, yy), words[i], PRESS, fill, shadow=None)
            x += text_width(words[i], PRESS) + space


def film_subs(ui, ln, now, sung=(236, 232, 222), cur=C["gold"], todo=(128, 122, 118)):
    """Film subtitles, set in the lower letterbox bar."""
    words = [clean_word(w["w"]) for w in ln["words"]]
    rows = sub_rows(wrap(words, PRESS, W - 16), now)
    space = text_width(" ", PRESS)
    y = H - BAR + (8 if len(rows) == 1 else 3)
    for row in rows:
        x = (W - text_width(" ".join(words[i] for i in row), PRESS)) // 2
        for i in row:
            fill = sung if i < now else cur if i == now else todo
            pixel.text(ui, (x, y), words[i], PRESS, fill, shadow=None)
            x += text_width(words[i], PRESS) + space
        y += 10


# --- documentary -------------------------------------------------------------------------

def viewfinder(ui, t, rec=True, label=None, blink=True):
    """A field camera's viewfinder: corner brackets, REC, timecode and battery."""
    white = C["text"]
    d = ImageDraw.Draw(ui)
    m, L = 8, 10
    for (x, y, sx, sy) in ((m, m, 1, 1), (W - 1 - m, m, -1, 1), (m, 140, 1, -1), (W - 1 - m, 140, -1, -1)):
        d.line([(x, y), (x + sx * L, y)], fill=white + (255,))
        d.line([(x, y), (x, y + sy * L)], fill=white + (255,))
    if rec and (not blink or int(t * 2) % 2 == 0):
        d.ellipse((m + 5, m + 5, m + 10, m + 10), fill=C["rec"] + (255,))
    if rec:
        pixel.text(ui, (m + 14, m + 4), "REC", SILK, white, shadow=INK)
    f = int(t * 24)
    tc = f"{f // 86400 % 24:02d}:{f // 1440 % 60:02d}:{f // 24 % 60:02d}:{f % 24:02d}"
    pixel.text(ui, (W - m - 5 - text_width(tc, SILK), m + 4), tc, SILK, white, shadow=INK)
    bx = W - m - 18
    d.rectangle((bx, m + 14, bx + 11, m + 19), outline=white + (255,))
    d.rectangle((bx + 12, m + 16, bx + 12, m + 17), fill=white + (255,))
    d.rectangle((bx + 2, m + 16, bx + 7, m + 17), fill=white + (255,))
    if label:
        pixel.text(ui, (m + 5, m + 16), label, SILK, white, shadow=INK)


def lower_third(ui, age, title, sub=None, y=112, x=10, accent=C["docbar"], out_at=None):
    """A documentary caption that wipes in from the left: a title bar and an optional second line."""
    if age < 0:
        return
    p = ease_out(ramp(age, 0, 0.35))
    q = 0.0 if out_at is None else ease_in(ramp(age, out_at, out_at + 0.3))
    tw = text_width(title, PRESS)
    sw = text_width(sub, SILK) if sub else 0
    w = max(tw, sw) + 12
    shown = int(w * p * (1 - q))
    if shown <= 2:
        return
    layer = Image.new("RGBA", (w, 24), (0, 0, 0, 0))
    rect(layer, (0, 0, w - 1, 12), "band")
    rect(layer, (0, 0, 2, 12), accent)
    pixel.text(layer, (7, 2), title, PRESS, C["text"], shadow=None)
    if sub:
        rect(layer, (0, 13, sw + 12, 22), (34, 30, 40))
        pixel.text(layer, (7, 13), sub, SILK, accent, shadow=None)
    layer = layer.crop((0, 0, shown, 24))
    ui.paste(layer, (x, y), layer)


def callout(ui, age, s, tx, ty, x, y, color=C["text"], fnt=SILK):
    """A freeze-frame label: `s` on a black tag centred at (x, y), with a leader line drawn out to the
    target (tx, y) as it appears."""
    if age < 0:
        return
    p = ease_out(ramp(age, 0, 0.18))
    d = ImageDraw.Draw(ui)
    c4 = col(color) + (255,)
    ex, ey = lerp(x, tx, p), lerp(y, ty, p)
    d.line([(x + 1, y + 1), (ex + 1, ey + 1)], fill=INK + (255,))
    d.line([(x, y), (ex, ey)], fill=c4)
    if p >= 1:
        d.rectangle((tx - 1, ty - 1, tx + 1, ty + 1), fill=c4)
    tw = text_width(s, fnt)
    top = y - 10 if ty > y else y
    rect(ui, (x - tw // 2 - 3, top, x + tw // 2 + 3, top + 9), "band")
    pixel.text(ui, (x - tw // 2, top + (0 if fnt is SILK else 1)), s, fnt, col(color), shadow=None)


def zoom_bar(ui, z, y=12):
    """The viewfinder's zoom indicator, W to T, with z in [0, 1]."""
    x0 = W // 2 - 32
    d = ImageDraw.Draw(ui)
    pixel.text(ui, (x0 - 8, y - 1), "W", SILK, C["text"], shadow=INK)
    pixel.text(ui, (x0 + 66, y - 1), "T", SILK, C["text"], shadow=INK)
    d.rectangle((x0, y + 1, x0 + 63, y + 5), outline=C["text"] + (255,))
    n = int(round(clamp(z, 0, 1) * 15))
    for k in range(n):
        d.rectangle((x0 + 2 + k * 4, y + 3, x0 + 3 + k * 4, y + 3), fill=C["text"] + (255,))


STATUSES = [("LC", "LEAST CONCERN", (76, 170, 92)), ("NT", "NEAR THREATENED", (150, 190, 70)),
            ("VU", "VULNERABLE", (236, 196, 50)), ("EN", "ENDANGERED", (240, 140, 50)),
            ("CR", "CRITICALLY ENDANGERED", (220, 60, 50)), ("EW", "EXTINCT IN THE WILD", (120, 40, 90)),
            ("EX", "EXTINCT", (30, 24, 30))]


def status_scale(ui, level, x=None, y=20, label=True, flash=0.0):
    """The IUCN Red List scale as seven lozenges, with `level` (float, 0 = LC ... 6 = EX) lit."""
    cell, gap = 18, 2
    total = 7 * cell + 6 * gap
    x = (W - total) // 2 if x is None else x
    d = ImageDraw.Draw(ui)
    k = int(round(clamp(level, 0, 6)))
    for i, (code, name, c) in enumerate(STATUSES):
        cx = x + i * (cell + gap)
        on = i == k
        fill = c if on else pixel.mix(c, (40, 36, 48), 0.65)
        d.rectangle((cx, y, cx + cell - 1, y + 11), fill=fill + (255,), outline=INK + (255,))
        pixel.text(ui, (cx + cell // 2, y + 2), code, SILK, (255, 255, 255) if on else (150, 146, 160), shadow=None,
                   anchor="ma")
        if on and flash > 0:
            d.rectangle((cx - 2, y - 2, cx + cell + 1, y + 13), outline=C["text"] + (255,))
    if label:
        name = STATUSES[k][1]
        pixel.text(ui, (x + total // 2, y + 15), name, SILK, C["text"], shadow=INK, anchor="ma")


def episode_title(ui, age, big, small, dur=3.2):
    """The documentary's title: a clean fade-up of white type, held, then gone."""
    if not 0 <= age < dur:
        return
    a = ramp(age, 0, 0.4) * (1 - ramp(age, dur - 0.5, dur))
    if a <= 0:
        return
    layer = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
    outline_text(layer, (W // 2, 8), big, PRESS16, C["text"], INK, anchor="ma")
    outline_text(layer, (W // 2, 32), small, PRESS, C["docbar"], INK, anchor="ma")
    fade_layer(layer, a)
    ui.paste(layer, (0, 44), layer)


def fade_layer(layer, a):
    """Knock out pixels of an RGBA layer with an ordered dither so it looks `a` opaque."""
    if a >= 1:
        return
    arr = np.array(layer)
    thr = pixel.bayer(arr.shape[0], arr.shape[1])
    arr[..., 3] = np.where(thr < a, arr[..., 3], 0)
    layer.paste(Image.fromarray(arr))


def channel_bug(ui, text_s="PLANET BEEF"):
    """The documentary's corner bug."""
    x = W - 8 - text_width(text_s, SILK)
    dither_rect(ui, (x - 4, 8, W - 5, 18), C["band"], density=0.5)
    pixel.text(ui, (x, 8), text_s, SILK, (220, 224, 236), shadow=None)


# --- film ----------------------------------------------------------------------------

def letterbox(ui, amount=1.0, color=(0, 0, 0)):
    """Black bars top and bottom; `amount` 0-1 slides them in."""
    h = int(round(BAR * clamp(amount, 0, 1)))
    if h <= 0:
        return
    d = ImageDraw.Draw(ui)
    d.rectangle((0, 0, W, h - 1), fill=tuple(color) + (255,))
    d.rectangle((0, H - h, W, H), fill=tuple(color) + (255,))


@lru_cache(maxsize=1)
def _vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    return np.clip((r - 0.75) / 0.6, 0, 1).astype(np.float32) * 0.55


def film_grade(world, t, warm=1.0, grain=1.0, vignette=1.0):
    """A warm film grade with a dithered vignette, grain speckle and the odd scratch."""
    a = np.asarray(world, dtype=np.float32)
    if warm:
        lum = a.mean(axis=2, keepdims=True)
        shadow = np.clip(1 - lum / 140, 0, 1)
        a = a * np.array([1.06, 1.0, 0.86], np.float32) + np.array([8, 3, -6], np.float32) * warm
        a = a + shadow * np.array([-4, 2, 10], np.float32) * warm             # cool the shadows a touch
        a = (a - 128) * 1.06 + 128
    if vignette:                                  # flat steps of shade toward the corners
        v = (np.floor(_vignette() / 0.55 * 8) / 8 * 0.34 * vignette)[..., None]
        a = a * (1 - v) + np.array((6, 4, 8), np.float32) * v
    out = Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8))
    if grain:
        f = int(t * 24)
        rng = np.random.default_rng(f)
        arr = np.asarray(out).copy()
        n = int(220 * grain)
        ys, xs = rng.integers(0, H, n), rng.integers(0, W, n)
        delta = rng.choice([-22, 16], n)[:, None]
        arr[ys, xs] = np.clip(arr[ys, xs].astype(np.int16) + delta, 0, 255).astype(np.uint8)
        if rnd("scratch", f // 2) < 0.07:
            x = int(rnd("scratch-x", f // 2) * W)
            arr[:, x] = np.clip(arr[:, x].astype(np.int16) + 38, 0, 255).astype(np.uint8)
        out = Image.fromarray(arr)
    world.paste(out)


def gate_weave(t, amount=1.0):
    """A projector's gentle jitter, in screen pixels."""
    f = int(t * 24)
    return (int(round((rnd("wx", f // 3) - 0.5) * 2 * amount)), int(round((rnd("wy", f // 2) - 0.5) * 4 * amount)))


def film_title(ui, age, title, byline=None, dur=3.4, y=58):
    """A movie title card: gold letters with a dark outline, a byline above, fading in and out."""
    if not 0 <= age < dur:
        return
    a = ramp(age, 0, 0.5) * (1 - ramp(age, dur - 0.6, dur))
    layer = Image.new("RGBA", (W, 64), (0, 0, 0, 0))
    if byline:
        pixel.text(layer, (W // 2, 4), byline, SILK, (230, 222, 206), shadow=INK, anchor="ma")
    rows = title.split("\n")
    yy = 16
    for r in rows:
        outline_text(layer, (W // 2, yy), r, PRESS16, C["gold_hi"], INK, anchor="ma")
        yy += 20
    fade_layer(layer, a)
    ui.paste(layer, (0, y), layer)


@lru_cache(maxsize=4)
def _blotchy(seed):
    """A smooth random field in [-0.5, 0.5] over the canvas (two octaves of upscaled noise), for ragged edges."""
    rng = np.random.default_rng(seed)
    field = np.zeros((H, W), np.float32)
    for (gw, gh), amp in (((16, 9), 0.65), ((40, 23), 0.35)):
        g = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        field += (np.asarray(g, np.float32) / 255 - 0.5) * amp
    return field


def film_burn(ui, p, seed=0):
    """Celluloid melting in the gate: orange-white blotches spreading from a few points, p in [0, 1].
    Flat bands with ragged edges (no dither, which turns to a checkerboard when scaled up)."""
    if p <= 0:
        return
    yy, xx = np.mgrid[0:H, 0:W]
    ragged = _blotchy(seed) * 30                        # each blotch's edge wanders by up to 15 px
    heat = np.zeros((H, W), np.float32)
    for k in range(4):
        cx, cy = rnd("burn", seed, k) * W, rnd("burn-y", seed, k) * H
        r = (30 + 160 * p) * (0.6 + 0.8 * rnd("burn-r", seed, k))
        heat = np.maximum(heat, 1 - (np.hypot(xx - cx, (yy - cy) * 1.3) + ragged) / max(r, 1))
    heat = np.clip(heat * (0.4 + 1.6 * p), 0, 1)
    arr = np.array(ui)
    for lo, color in ((0.05, (70, 18, 8)), (0.14, (150, 40, 12)), (0.3, (240, 110, 30)), (0.52, (255, 214, 120)),
                      (0.74, (255, 250, 230))):
        arr[heat > lo] = color + (255,)
    ui.paste(Image.fromarray(arr))


def leader(ui, age, n0=3, per=0.8):
    """A film-leader countdown: a sweep round a circle, counting down from n0, one number a beat."""
    if age < 0 or age >= n0 * per:
        return
    k = int(age / per)
    p = (age / per) % 1.0
    n = n0 - k
    d = ImageDraw.Draw(ui)
    d.rectangle((0, 0, W, H), fill=(150, 140, 124, 255))
    cx, cy, r = W // 2, H // 2, 62
    d.pieslice((cx - 160, cy - 160, cx + 160, cy + 160), -90, -90 + 360 * p, fill=(118, 108, 94, 255))
    for rr in (r, r - 8):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(250, 246, 236, 255))
    d.line([(0, cy), (W, cy)], fill=(40, 34, 30, 255))
    d.line([(cx, 0), (cx, H)], fill=(40, 34, 30, 255))
    big = pixel.font(size=48)
    outline_text(ui, (cx, cy - 22), str(n), big, (30, 26, 24), (250, 246, 236), anchor="ma")


def credits_roll(ui, age, lines, speed=14.0, top=BAR + 2, bottom=H - BAR - 2):
    """End credits scrolling up between the letterbox bars: `lines` are (role, name) pairs or headers."""
    y = bottom - age * speed
    for item in lines:
        if y > bottom + 12:
            break
        if y > top - 12:
            if isinstance(item, tuple):
                role, name = item
                pixel.text(ui, (W // 2 - 6, int(y)), role, SILK, (190, 182, 170), shadow=None, anchor="ra")
                pixel.text(ui, (W // 2 + 6, int(y)), name, SILK, (246, 240, 226), shadow=None, anchor="la")
            elif item:
                pixel.text(ui, (W // 2, int(y)), item, PRESS, C["gold_hi"], shadow=None, anchor="ma")
        y += 12 if isinstance(item, tuple) else 16
    # keep the bars clean
    letterbox(ui, 1.0)


def static_noise(ui, amount, seed):
    """TV static over the whole screen (the documentary taking the channel back)."""
    if amount <= 0:
        return
    rng = np.random.default_rng(seed)
    v = rng.integers(0, 255, (H, W)).astype(np.uint8)
    arr = np.array(ui)
    sel = rng.random((H, W)) < amount
    arr[sel, 0] = v[sel]
    arr[sel, 1] = v[sel]
    arr[sel, 2] = v[sel]
    arr[sel, 3] = 255
    ui.paste(Image.fromarray(arr))


def vhs_rewind(ui, t, amount=1.0):
    """Tracking lines and a REPLAY tag, for the documentary's action replay."""
    d = ImageDraw.Draw(ui)
    f = int(t * 24)
    for k in range(3):
        y = int((rnd("vhs", f, k) * 1.2 - 0.1) * H)
        h = 2 + int(rnd("vhs-h", f, k) * 3)
        y0, y1 = max(0, y), min(H, y + h)
        if y1 > y0:
            ui.alpha_composite(Image.new("RGBA", (W, y1 - y0), (230, 230, 240, int(90 * amount))), (0, y0))
    if int(t * 2) % 2 == 0:
        pixel.text(ui, (12, 12), "REPLAY", PRESS, C["text"], shadow=INK)
        d.polygon([(64, 12), (64, 19), (69, 15)], fill=C["text"] + (255,))
        d.polygon([(69, 12), (69, 19), (74, 15)], fill=C["text"] + (255,))
