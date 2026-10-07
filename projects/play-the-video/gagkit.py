"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a video.Ctx and `L` a
pixelart.gags.LineRef (`L.age("word")` is seconds since that word started). Code before the first yield
runs at setup: pose c.st[who], hand someone a prop (`hold`), put a picture in the window (`show`).
Then each `yield "<phase>"` waits for that drawing phase:

    "back"   c.cam[who], his webcam frame (320x180), behind his figure
    "mid"    c.cam[who], in front of the figure and his desk (c.anchor[who] is known by now)
    "front"  c.world, the frame as cut together, over the window and the chat
    "ui"     c.ui, under the captions
    "top"    c.ui, over everything

The gag is live from just before its line starts until half a second into the next one.
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

import chatlog
import rooms
import stream
import timeline as TL
import video as V
from characters import FW, figure, head
from engine import (C, INK, PRESS, PRESS16, SILK, SILK16, H, W, Canvas, arc_pt, back_out, blend, clamp, col, dither,
                    dither_rect, ease_in, ease_in_out, ease_out, fade_to, fly, k_in, lerp, mirror, mix, outline_text,
                    paste, paste_rot, paste_scaled, pop_dy, pop_in, ramp, rgba, rnd, scaled, silk, silk_w, text_width,
                    tint, vgrad, wobble)
from pixelart import fx, pixel
from pixelart.gags import Sung, count
from rooms import DESK_Y, FIG
from stream import PH, PW

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
MEN = V.MEN


def gag(sec, idx, pre=0.12, post=0.5):
    """Register a line's gag. It runs from just before its line until half a second into the next one, so a
    punchline on the last word stays up while the next gag starts (the later gag's poses win). A section's
    last line runs to the end of the section and no further: the next one is somebody else's stream."""
    last = (sec, idx + 1) not in {(ln["sec"], ln["idx"]) for ln in TL.LINES}
    if idx == 0:                                 # nor does a section's first line start before the cut to it
        pre = min(pre, TL.line(sec, 0)["t0"] - TL.section_start(sec))
    return GAGS.gag(sec, idx, pre, 0.0 if last else post)


def when(sec, idx, pat=None, n=0):
    """The time a line starts (or a word in it is sung), for gags that outlive their line."""
    ln = TL.line(sec, idx)
    return ln["t0"] if pat is None else TL.timing.word_time(ln, pat, "t0", n)


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


# --- the window, and the chat ----------------------------------------------------------------------

def show(c, pic, title=None, badge="CLIP", a=0.0):
    """Put a picture (PW x PH) in the host's window from age `a`, in place of the other man's video. It
    starts clean, whatever the gag before it was doing to the video (playing it, shaking it)."""
    if a < 0:
        return
    c.window.update(pic=getattr(pic, "img", pic), title=title, badge=badge, paused=False, progress=0.02, shake=0)


def alert(c, a, title, text=None, icon="star", dur=2.6, host=None, accent=None):
    """An alert on the host's stream from age `a`: call it in the "front" phase."""
    stream.draw_alert(c.world, host or c.host, a, title, text, icon, dur, accent)


def win(c, x, y):
    """A point of the window's picture, in the world."""
    x0, y0, _, _ = stream.pic_box(c.host)
    return x0 + x, y0 + y


CHATTERS = (("ZYNGOD", "hasan_hi"), ("ROACH77", "asmon_hi"), ("LATTE", "hasan_hi"), ("BALD4", "asmon_hi"),
            ("MARXBRO", "hasan_hi"), ("GRUG", "asmon_hi"), ("OATMILK", "hasan_hi"), ("RATKING", "asmon_hi"))


def sung(ln, t, cuts=(0,), names=CHATTERS, first=0):
    """A sung line as chat messages, typed as they are sung: a new message starts at each word index in
    `cuts`. Returns ([(name, colour, text), ...], seconds since the newest one started)."""
    words = ln["words"]
    out, age = [], 9.0
    for k, a in enumerate(cuts):
        b = cuts[k + 1] if k + 1 < len(cuts) else len(words)
        if t < words[a]["t0"]:
            break
        name, color = names[(first + k) % len(names)]
        out.append((name + ":", color, " ".join(w["w"] for w in words[a:b] if w["t0"] <= t).upper()))
        age = t - words[a]["t0"]
    return out, age


def feed(c, t0, parts):
    """Script the chat down the middle of the split screen: what both chats were saying at t0, then `parts`,
    each a (messages, age) pair from `sung`."""
    lines, age = list(chatlog.both(t0, 6)[0]), 9.0
    for msgs, a in parts:
        if msgs:
            lines += msgs
            age = a
    c.feed, c.feed_age = lines, age


# --- words over the picture ------------------------------------------------------------------------

def say(c, x, y, lines, a, dur=None, fnt=PRESS, tail=None, img=None):
    """A speech bubble with its bottom centre at a world point, from age a (until a reaches dur)."""
    if a < 0 or (dur is not None and a > dur):
        return
    lines = [lines] if isinstance(lines, str) else list(lines)
    pop = pop_dy(a, 0.12, 5) or 0
    kw = dict(text_dy=0) if fnt is PRESS else dict(text_dy=-3, line_h=8)
    fx.bubble(img or c.world, int(x), int(y + pop), lines, tail=tail, fnt=fnt, fill=C["white"], ink=INK, **kw)


def label(c, x, y, s, a, dur=None, bg="white", fg="ink", img=None):
    """A plate with a few words on it, popping in centred on a world point from age a."""
    if a < 0 or (dur is not None and a > dur):
        return
    img = img or c.world
    w = silk_w(s) + 6
    x0, y0 = int(x - w // 2), int(y - 5 + (pop_dy(a, 0.12, 4) or 0))
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1, x0 + w, y0 + 9), fill=INK)
    d.rectangle((x0, y0, x0 + w - 1, y0 + 8), fill=col(bg))
    silk(img, (x0 + 3, y0 + 2), s, fg)


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


def jolt(c, a, amount=4, dur=0.3):
    """Shake the whole frame as something lands."""
    if 0 <= a < dur:
        c.add_shake(amount * (1 - a / dur))
