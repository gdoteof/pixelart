"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a video.Ctx and `L` a
pixelart.gags.LineRef (`L.age("word")` is seconds since that word started). Code before the first yield
runs at setup: share a picture in ChatGPT's window (`show`), pose c.st[who], hand someone a prop (`hold`).
Then each `yield "<phase>"` waits for that drawing phase:

    "back"   c.tile[who], behind the figure, in tile pixels (TW x TH)
    "mid"    c.tile[who], in front of the figure and the desk (c.anchor[who] is known by now)
    "front"  c.world, over the tiles and ChatGPT's window
    "ui"     c.ui, under the captions
    "top"    c.ui, over everything

The gag is live from just before its line starts until half a second into the next one.

Layout (world pixels; the frame is the whole 320x180 world and never moves, so UI pixels are the same):
    Felix's tile     call.TILE["felix"] = (4, 13, 104, 133); his head about (30-70, 42-82), facing right
    ChatGPT's window call.SCREEN = (108, 13, 212, 133); the picture it shares is PIC = (110, 25, 210, 121)
    Sam's tile       call.TILE["sam"] = (216, 13, 316, 133); his head about (250-290, 42-82), facing left
    the desks        tile y 100 (world y 113); the name plates cover tile y 108-117 at the left
    the captions     UI y 138-166; the controls y 169-180; the top bar y 0-10
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

import call
import pictures as P
import timeline as TL
import video as V
from call import DESK_Y, PIC, SCREEN, TH, TILE, TW
from characters import FW, figure, head, helmet, mini, orb
from engine import (C, INK, PRESS, PRESS16, SILK, SILK16, H, W, Canvas, arc_pt, back_out, blend, clamp, col, dither,
                    dither_rect, ease_in, ease_in_out, ease_out, fade_to, fly, lerp, mirror, mix, outline_text, paste,
                    paste_rot, paste_scaled, pop_dy, pop_in, ramp, rgba, rnd, scaled, silk, silk_w, text_width, tint,
                    vgrad, wobble)
from pictures import PH, PW, Pic
from pixelart import fx, pixel

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
MEN = V.MEN


def gag(sec, idx, pre=0.12, post=0.5):
    """Register a line's gag. It runs from just before its line until half a second into the next one, so a
    punchline on the last word stays up while the next gag starts (the later gag's poses and picture win)."""
    return GAGS.gag(sec, idx, pre, post)


def hooks(idx, pre=0.12, post=0.5):
    """Register one gag for the same line of both hooks."""
    def reg(fn):
        for sec in TL.HOOKS:
            GAGS.gag(sec, idx, pre, post)(fn)
        return fn
    return reg


# --- timing ---------------------------------------------------------------------------------

def k_in(a, dur=0.2):
    """0 -> 1 over `dur` seconds from age a (clamped)."""
    return clamp(a / dur, 0.0, 1.0)


def when(sec, idx, pat=None, n=0):
    """The time a line starts (or a word in it is sung), for gags that outlive their line."""
    ln = TL.line(sec, idx)
    return ln["t0"] if pat is None else TL.timing.word_time(ln, pat, "t0", n)


def count(L, *pats):
    """How many of the words matching these patterns, in order, have been sung."""
    return sum(1 for p in pats if L.on(p))


class Sung:
    """Stands in for a line once all of it has been sung: for a gag that keeps an earlier line's picture
    up, and so can't ask its own line about that one's words."""

    def __init__(self, t=0.0):
        self.t = t

    def on(self, pat, n=0):
        return True

    def age(self, pat=None, n=0):
        return 9.0


# --- ChatGPT's window ---------------------------------------------------------------------------

def show(c, pic, caption=None, a=0.0, dur=0.16):
    """Share a picture (a Pic or an image, PW x PH) in ChatGPT's window from age `a`: it slides up over
    whatever was there."""
    if a < 0:
        return
    prev = c.screen
    c.screen = dict(pic=getattr(pic, "img", pic), caption=caption, slide=ease_out(k_in(a, dur)), out=0.0,
                    under=prev["pic"] if prev else None)


def swipe(c, a, dur=0.2):
    """Swipe the shared picture off to the left from age `a`: "Next!"."""
    if a < 0 or not c.screen:
        return
    if a >= dur:
        c.screen = None
    else:
        c.screen["out"] = ease_in(a / dur)


def wx(x, y):
    """A point of the shared picture, in the world."""
    return PIC[0] + x, PIC[1] + y


def tx(who, x, y):
    """A point of someone's tile, in the world."""
    return TILE[who][0] + x, TILE[who][1] + y


# --- posing and props ------------------------------------------------------------------------

def pose(c, who, **kw):
    """Set pose fields and stop the automatic gestures from overriding the arms."""
    s = c.st[who]
    if "arms" in kw:
        s["gesture"] = False
    s.update(kw)


def hold(c, who, prop, arms="show", at=None):
    """Have `who` hold a prop in front of him: a sheet shown to the camera by its bottom corners ("show"),
    or something smaller in both hands at the chest ("hold")."""
    s = c.st[who]
    s["arms"], s["held"], s["gesture"] = arms, (prop, at or ("hands_top" if arms == "show" else "hands")), False


def hold_up(c, who, prop, lift=0):
    """One hand raises a prop: the far hand, the prop's bottom in the fist."""
    s = c.st[who]
    s["arms"], s["gesture"] = "hold1", False
    s["held"] = (prop, ("hand_far", prop.height // 2 - 2 + lift))


def head_pt(c, who, x=20, y=0):
    """A point on who's head given in head pixels (40x40, facing right), in his tile. From "mid" on."""
    hx, hy = c.anchor[who]["head"]
    return (hx - 20 + x, hy + y) if c.st[who]["facing"] > 0 else (hx + 19 - x, hy + y)


def on_head(c, who, spr, dy=0, dx=0):
    """Paste a sprite drawn facing right over who's head in his tile, turned his way; its top centre goes
    `dy` below the top of the head. From "mid" on."""
    s = c.st[who]
    spr = spr if s["facing"] > 0 else mirror(spr)
    hx, hy = c.anchor[who]["head"]
    c.tile[who].paste(spr, (hx - spr.width // 2 + dx * s["facing"], hy + dy), spr)


# --- words over the picture ------------------------------------------------------------------------

def say(c, who, lines, a, dur=None, fnt=PRESS, dy=0):
    """A speech bubble over who's head from age a (and until a reaches dur). In "front" or later."""
    if a < 0 or (dur is not None and a > dur):
        return
    hx, hy = c.at(who, "head")
    s = c.st[who]
    x0, _, x1, _ = TILE[who]
    lines = [lines] if isinstance(lines, str) else list(lines)
    w = max(text_width(t, fnt) for t in lines) + 10
    bx = clamp(hx + 4 * s["facing"], x0 + w // 2 + 1, x1 - w // 2 - 1)
    pop = pop_dy(a, 0.12, 5) or 0
    kw = dict(text_dy=0) if fnt is PRESS else dict(text_dy=-3, line_h=8)
    fx.bubble(c.world, int(bx), int(hy - 3 + dy + pop), lines, tail=(int(hx + 6 * s["facing"]), int(hy + 4)),
              fnt=fnt, fill=C["white"], ink=INK, **kw)


def shout(c, x, y, s, a, size=16, top="gold", bottom="orange", dur=None, img=None):
    """Arcade text popping in at a world point from age a (until a reaches dur)."""
    if a < 0 or (dur is not None and a > dur):
        return
    fx.pop_text(img or c.world, int(x), int(y), s, a, PRESS16 if size == 16 else PRESS, col(top), col(bottom),
                C["black"], anchor="mm", ink=INK)


def stamp(c, x, y, s, a, color="red", angle=-12, fnt=PRESS, img=None):
    """A rubber stamp slammed onto a world point at age 0."""
    if a < 0:
        return
    fx.stamp(img or c.world, int(x), int(y), s, fnt=fnt, color=col(color), angle=angle, age=a)


def toast(c, s, a, dur=2.2, color="text"):
    """A system message under the top bar from age a for `dur` seconds."""
    if 0 <= a < dur:
        c.toasts.append((s, min(k_in(a, 0.15), k_in(dur - a, 0.15)), color))


def jolt(c, a, amount=4, dur=0.3):
    """Shake the whole frame as something lands."""
    if 0 <= a < dur:
        c.add_shake(amount * (1 - a / dur))


def over_tile(c, who, fn):
    """Draw on a copy of who's tile region of the world, clipped to the tile: fn(img) gets a TW x TH image."""
    x0, y0, x1, y1 = TILE[who]
    part = c.world.crop((x0, y0, x1, y1))
    fn(part)
    c.world.paste(part, (x0, y0))
