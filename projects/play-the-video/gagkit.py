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
from engine import (C, INK, KIT, PRESS, PRESS16, SILK, SILK16, H, W, Canvas, arc_pt, back_out, blend, clamp, col, dither,
                    dither_rect, ease_in, ease_in_out, ease_out, fade_to, fly, k_in, lerp, mirror, mix, outline_text,
                    paste, paste_rot, paste_scaled, pop_dy, pop_in, ramp, rgba, rnd, scaled, silk, silk_w, text_width,
                    tint, vgrad, wobble)
from pixelart import fx, pixel
from pixelart.gagkit import GagKit
from pixelart.gags import Sung, count
from rooms import DESK_Y, FIG
from stream import PH, PW

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
MEN = V.MEN

K = GagKit(GAGS, TL.SONG, KIT, stream.UI)
# Registration, timing and placement: see pixelart.gagkit for what each does.
gag, when, pose, hold, hold_up, show, alert, win = K.gag, K.when, K.pose, K.hold, K.hold_up, K.show, K.alert, K.win
say, label, shout, stamp, jolt = K.say, K.label, K.shout, K.stamp, K.jolt


# --- the chat ----------------------------------------------------------------------------------------

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
