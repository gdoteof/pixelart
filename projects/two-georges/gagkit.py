"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a
video.Ctx and `L` a pixelart.gags.LineRef. Code before the first yield runs at
setup (change c.shot, c.st[who] poses, c.mood...), then each `yield "<phase>"`
waits for that drawing phase: "back" (world, behind the characters), "front"
(world, in front), "ui" (UI layer under the karaoke band) and "top" (UI, over
everything). The gag is live from just before its line starts until the next
line starts, so a gag that spills into the next line should hand over the camera.

World coordinates are the 320x180 set; UI coordinates are the screen at 320x180,
so a world point is drawn on the UI with c.to_ui(x, y) (it moves with the camera).
Rows 147-180 of the UI are the karaoke band; keep UI gags above SAFE_BOTTOM.
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import timeline as TL
import video as V
from characters import crown_sprite, figure, tricorn_sprite
from engine import (C, INK, PRESS, PRESS16, PRESS24, SILK, SILK16, SCALE, H, W, Canvas, arc_pt, back_out,
                    clamp, dither, dither_poly, dither_rect, ease_in, ease_in_out, ease_out, fade_to, lerp,
                    mask, mirror, mix, outline_text, outlined, paste, paste_rot, paste_scaled, pop_dy, ramp,
                    rnd, scaled, text, text_width, wobble)
from pixelart.camera import Cam, between
from props import (GOLD, ORANGE, RED, WHITE, arrow, barrel, big_text, big_text_img, bottle, bubble, burst,
                   cannonball, cherry_tree, coin, envelope, float_on_water, hatchet, label, muzzle_flash,
                   parchment, planet, pop_text, projectile, puff, quill, scroll_sprite, splash, sparkle, stamp,
                   strike, tea_crate, teacup, typed, white_flag)
from scene import (BOSTON_EDGE, FEET_Y, GEORGE_X, HORIZON, LONDON_EDGE, SUN, WASH_X, P, flag_cloth, flagpole,
                   sea_band, waving)

FPS = TL.FPS
GAGS, DEBRIS, SHOTS, SCENES = V.GAGS, V.DEBRIS, V.SHOTS, V.SCENES
gag, span = GAGS.gag, GAGS.span
SAFE_TOP, SAFE_BOTTOM = 18, 138          # UI rows clear of the shore labels and the speaker chip
SEA_X = (106, 214)                        # open water between the wharf and the quay
HOME = {"washington": (WASH_X, FEET_Y), "george": (GEORGE_X, FEET_Y)}


# --- timing ---------------------------------------------------------------------------------

def wt(L, pat, n=0, which="t0"):
    """Time of the n-th word of line L matching regex `pat` (case-insensitive)."""
    k = 0
    for w in L.words:
        if re.search(pat, w["w"], re.I):
            if k == n:
                return w[which]
            k += 1
    raise KeyError(f"{pat!r} #{n} not in {L.ln['text']!r}")


def line_t(sec, idx, pat=None, n=0):
    """Start of another line (or of a word in it), for gags that carry over between lines."""
    ln = TL.line(sec, idx)
    if pat is None:
        return ln["t0"]
    k = 0
    for w in ln["words"]:
        if re.search(pat, w["w"], re.I):
            if k == n:
                return w["t0"]
            k += 1
    raise KeyError(pat)


def end_t(L):
    """When the line's last word is sung."""
    return L.words[-1]["t0"]


def hit_t(L):
    """When the line lands on the listener (the hit reaction fires)."""
    return TL.hit_of(L.ln)["t"]


def blink(c, hz=4.0):
    return int(c.t * hz * 2) % 2 == 0


def calm(c, who, window=0.6):
    """True unless `who` has just taken a hit (so gags don't stomp the hit reaction)."""
    return TL.last_hit(c.t, target=who, window=window) is None


# --- placement --------------------------------------------------------------------------------

def anchor(c, who, key="head"):
    """A character's anchor point in world pixels (head, mouth, eye, hand, mic, top, feet), from its
    current pose. Valid in any phase; after the characters are drawn it matches c.anchor[who]."""
    s = c.st[who]
    if who in c.anchor:
        return c.anchor[who][key]
    pose = {k: s[k] for k in ("mouth", "eyes", "brows", "arm", "mic", "hat", "flush", "lean", "bob", "bell")}
    _, a = figure(who, s["facing"], **pose)
    x, y = s["x"] + s["dx"], s["y"] + s["dy"]
    fx, fy = a["feet"]
    px, py = a[key]
    return px - fx + x, py - fy + y


def face(c, who, **kw):
    """Set expression parts unless a fresh hit reaction is showing."""
    if calm(c, who):
        c.st[who].update(kw)


def ui_at(c, x, y):
    """World point -> UI point (ints)."""
    ux, uy = c.to_ui(x, y)
    return int(round(ux)), int(round(uy))


def fly(img, spr, a, b, p, lift=20, spin=0.0):
    """Paste sprite `spr` part way (p in [0, 1]) along an arc from a to b; returns its position."""
    if not 0 <= p <= 1:
        return None
    x, y = projectile(p, a, b, lift)
    if spin:
        paste_rot(img, spr, x, y, spin * p * 360)
    else:
        paste(img, spr, x, y, "mm")
    return x, y


def debris(t0, img_fn, x, y, t1=1e9, seed=0, drift=0.0, sink=3):
    """Leave something floating in the Atlantic from t0 on: `img_fn()` returns its sprite
    (use an lru_cached prop), (x, y) is its centre and waterline. Register at import time."""
    DEBRIS.append(dict(t0=t0, t1=t1, img=img_fn, x=x, y=y, seed=seed, drift=drift, sink=sink))


def sea_color(y):
    return P["sea"][sea_band(y)]


def pan(c, a, b, t0, dur, ease=ease_in_out):
    """Glide the camera from shot a to shot b (names or (cx, cy, k)) starting at t0."""
    sa = SHOTS[a] if isinstance(a, str) else a
    sb = SHOTS[b] if isinstance(b, str) else b
    c.shot = between(sa, sb, ramp(c.t, t0, t0 + dur), ease)


def world_text(img, x, y, s, fnt=SILK, fill=WHITE, anchor="ma"):
    outline_text(img, (int(x), int(y)), s, fnt, fill, INK, anchor)


@lru_cache(maxsize=None)
def char_sprite(who, facing=1, **pose):
    """A character sprite outside the usual drawing (for cut-ins, portraits, statues)."""
    return figure(who, facing, **pose)[0]


def tint(img, color, amount=1.0):
    """A copy of an RGBA sprite pushed toward `color` (for statues, silhouettes, ghosts)."""
    a = np.array(img).astype(np.float32)
    a[..., :3] = a[..., :3] * (1 - amount) + np.array(color, np.float32) * amount
    return Image.fromarray(a.round().astype(np.uint8))
