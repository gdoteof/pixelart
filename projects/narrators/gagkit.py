"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a
video.Ctx and `L` a pixelart.gags.LineRef. Code before the first yield runs at
setup (cut to a set with c.set_scene, pick c.shot, pose c.st[who], flip the
screen furniture), then each `yield "<phase>"` waits for that drawing phase:
"back" (world, behind the characters), "mid" (world, over the set's glass and
mist but behind the foreground cast), "front" (world, in front of everyone),
"ui" (UI layer, under the subtitles) and "top" (UI, over everything). The gag
is live from just before its line starts until the next line starts.

World coordinates are the 320x180 set; UI coordinates are the screen at 320x180,
so a world point is drawn on the UI with c.to_ui(x, y) (it moves with the camera).
The documentary's subtitles take UI rows 148-171 and its viewfinder the corners;
the film's letterbox bars are rows 0-22 and 157-179 (subtitles in the bottom bar).
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import chrome as CH
import timeline as TL
import video as V
from characters import figure, mouth_for
from engine import (C, INK, PRESS, PRESS16, PRESS24, SILK, SILK16, SCALE, H, W, Canvas, arc_pt, back_out, blend,
                    blend_poly, clamp, col, dither, dither_poly, dither_rect, ease_in, ease_in_out, ease_out, fade_to,
                    lerp, mask,
                    mirror, mix, new_world, outline_text, outlined, paste, paste_rot, paste_scaled, pop_dy, ramp,
                    rim_light, rnd, scaled, text, text_width, tint, vgrad, wobble)
from pixelart import pixel
from pixelart.camera import Cam, between
from sets import SETS, scene

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span


def gag(sec, idx, pre=0.12, post=0.0):
    """Register a line's gag. By default it starts as the previous line's gag stops (the runner stops a gag
    0.12 s before the next line), so neighbouring gags never draw in the same frame."""
    return GAGS.gag(sec, idx, pre, post)
BAR = CH.BAR
FILM_TOP, FILM_BOTTOM = BAR, H - BAR      # the picture between the letterbox bars
DOC_SUB_Y = CH.TELE_Y - 2                  # the documentary's subtitles start here


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
    """When the line lands on its target (the hit reaction fires)."""
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
    if who in c.anchor:
        return c.anchor[who][key]
    s = c.st[who]
    _, a = V.sprite_of(c, who)
    fx, fy = a["feet"]
    px, py = a[key]
    return px - fx + s["x"] + s["dx"], py - fy + s["y"] + s["dy"]


def place(c, who, **kw):
    """Show `who` in the current set with these placement and pose keys."""
    c.st[who].update(kw)
    c.st[who]["hidden"] = kw.get("hidden", False)


def face(c, who, **kw):
    """Set expression parts unless a fresh hit reaction is showing."""
    if calm(c, who):
        c.st[who].update(kw)


def ui_at(c, x, y):
    """World point -> UI point (ints)."""
    ux, uy = c.to_ui(x, y)
    return int(round(ux)), int(round(uy))


def projectile(p, a, b, lift):
    return arc_pt(p, a, b, lift)


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


def shot_of(c, name):
    return SETS[c.scene].shots[name] if isinstance(name, str) else name


def pan(c, a, b, t0, dur, ease=ease_in_out):
    """Glide the camera from shot a to shot b (names in the current set, or (cx, cy, k)) from t0."""
    c.shot = between(shot_of(c, a), shot_of(c, b), ramp(c.t, t0, t0 + dur), ease)


def world_text(img, x, y, s, fnt=SILK, fill=C["text"], anchor="ma"):
    outline_text(img, (int(x), int(y)), s, fnt, fill, INK, anchor)


@lru_cache(maxsize=None)
def char_sprite(who, facing=1, **pose):
    """A character sprite outside the usual drawing (for cut-ins, portraits, statues)."""
    return figure(who, facing, **pose)[0]


def char_at(img, who, x, y, facing=1, **pose):
    """Paste a character with its feet at (x, y); returns its anchors in world pixels."""
    spr, a = figure(who, facing, **pose)
    fx, fy = a["feet"]
    img.paste(spr, (int(x - fx), int(y - fy)), spr)
    return {k: (px - fx + x, py - fy + y) for k, (px, py) in a.items()}
