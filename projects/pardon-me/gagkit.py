"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a
video.Ctx and `L` a pixelart.gags.LineRef. Code before the first yield runs at
setup: pick c.shot, pose c.st[who], put a new page on the flip chart
(`flip(c, t)`), take over a screen (`c.screens["L"] = fn`), stand up the
delegates (`c.crowd`). Then each `yield "<phase>"` waits for that drawing phase:

    "back"   world: over the wall, the screens and the dais, behind everyone
    "chart"  the flip chart's page: draw on c.page in chart coordinates (PW x PH, origin top-left)
    "mid"    world: in front of the rostrum and the rapper, behind the desk and the heckler
    "front"  world: in front of everything, the front rows included
    "ui"     UI layer, under the karaoke
    "top"    UI layer, over everything

The gag is live from just before its line starts until the next line starts.

Layout (world pixels; the wide shot shows the whole 320x180 world):
    the flip chart's paper  hall.CHART = (22, 70, 112, 128): 90x58
    left screen (inner)     hall.screen_inner(hall.SCREEN_L) ~ (11, 11, 96, 60): the rapper's close-up
    right screen (inner)    hall.screen_inner(hall.SCREEN_R) ~ (225, 11, 310, 60): the heckler's close-up
    the rostrum             hall.ROSTRUM = (140, 130, 180, 170); the rapper stands at x 160, chest-up above y 130
    the dais and President  hall.DAIS = (106, 60, 214, 124), President at (160, 66)
    the delegation desk     hall.DESK = (212, 142, 320, 180); the heckler's head is about (262-278, 97-125)
    the front rows          heads along y 156-180, x 0-210 (hall.DELEGATES)
The karaoke takes the UI's bottom rows (about y 140-178); keep UI text above y 136.
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import hall
import props as P
import timeline as TL
import video as V
from characters import figure, mouth_for
from engine import (C, INK, PRESS, PRESS16, PRESS24, SILK, SILK16, SCALE, H, W, Canvas, arc_pt, back_out, blend,
                    blend_poly, clamp, col, dither, dither_poly, dither_rect, ease_in, ease_in_out, ease_out, fade_to,
                    lerp, mask, mirror, mix, new_world, outline_text, outlined, paste, paste_rot, paste_scaled, pop_dy,
                    ramp, rim_light, rnd, scaled, text, text_width, tint, vgrad, wobble)
from pixelart import pixel
from pixelart.camera import Cam, between
from props import (big_text, bomb_doodle, bubble, burst, card_sprite, check, circle_pts, confetti, cross_out, label,
                   marker_arrow, mk, page_title, polyline_part, pop_text, puff, ring, sparkle, speed_lines, stamp,
                   stick_figure, strike, stroke, truth_post, typed, underline, write, write_lines)

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
PW, PH = hall.CHART_W, hall.CHART_H          # the flip chart's page, in chart coordinates
SCREEN_L = hall.screen_inner(hall.SCREEN_L)
SCREEN_R = hall.screen_inner(hall.SCREEN_R)


def gag(sec, idx, pre=0.12, post=0.0):
    """Register a line's gag. By default it starts as the previous line's gag stops (the runner stops a gag
    0.12 s before the next line), so neighbouring gags never draw in the same frame."""
    return GAGS.gag(sec, idx, pre, post)


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


# --- the flip chart ---------------------------------------------------------------------------

def flip(c, t):
    """Put a fresh page up on the flip chart at time t (the old sheet flips over the top). Call at setup;
    then draw the page in the "chart" phase. Before t the chart shows whatever it showed."""
    if c.t >= t:
        c.page_flip = t


def chart_pt(x, y):
    """A chart-page point in world pixels."""
    return hall.CHART[0] + x, hall.CHART[1] + y


# --- placement --------------------------------------------------------------------------------

def anchor(c, who, key="head"):
    """A character's anchor point in world pixels (feet, head, mouth, eye, nose, hand, far, top, chest), from
    its current pose. Valid in any phase; after the characters are drawn it matches c.anchor[who]."""
    if who in c.anchor:
        return c.anchor[who][key]
    s = c.st[who]
    _, a = V.sprite_of(c, who)
    fx, fy = a["feet"]
    px, py = a[key]
    return px - fx + s["x"] + s["dx"], py - fy + s["y"] + s["dy"]


def place(c, who, **kw):
    """Move `who` and set pose keys (x, y, facing, layer: podium desk floor front, hidden, arm, mouth...)."""
    c.st[who].update(kw)
    c.st[who]["hidden"] = kw.get("hidden", False)


def pose(c, who, **kw):
    """Set pose keys and stop the automatic gestures, so the pose holds."""
    c.st[who].update(kw)
    c.st[who]["gesture"] = False


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
    x, y = arc_pt(p, a, b, lift)
    if spin:
        paste_rot(img, spr, x, y, spin * p * 360)
    else:
        paste(img, spr, x, y, "mm")
    return x, y


def world_text(img, x, y, s, fnt=SILK, fill=C["text"], anchor="ma"):
    outline_text(img, (int(x), int(y)), s, fnt, fill, INK, anchor)


@lru_cache(maxsize=None)
def char_sprite(who, facing=1, **pose_kw):
    """A character sprite outside the usual drawing (for cut-ins, portraits, statues)."""
    return figure(who, facing, **pose_kw)[0]


def char_at(img, who, x, y, facing=1, **pose_kw):
    """Paste a character with its feet at (x, y); returns its anchors in world pixels."""
    spr, a = figure(who, facing, **pose_kw)
    fx, fy = a["feet"]
    img.paste(spr, (int(x - fx), int(y - fy)), spr)
    return {k: (px - fx + x, py - fy + y) for k, (px, py) in a.items()}


@lru_cache(maxsize=None)
def bust(who, scale=1, w=34, h=30, facing=1, **pose_kw):
    """Head and shoulders of a character (w x h sprite pixels around the head), scaled, for screens and cards."""
    spr, a = figure(who, facing, **pose_kw)
    hx, hy = a["head"]
    x0, y0 = int(hx - w / 2), int(hy - h / 2 + 3)
    return scaled(spr.crop((x0, y0, x0 + w, y0 + h)), scale)


def screen_fill(img, box, color=(16, 20, 34)):
    """Blank a screen's inner box (to draw your own content on it)."""
    ImageDraw.Draw(img).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=col(color))
