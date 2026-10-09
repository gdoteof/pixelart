"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a video.Ctx and `L` a
pixelart.gags.LineRef (`L.age("word")` is seconds since that word started). Code before the first yield
runs at setup: pose c.st[who], hand someone a prop (`hold`), put a picture in the window (`show`).
Then each `yield "<phase>"` waits for that drawing phase:

    "back"   c.cam[who], her webcam frame (320x180), behind her figure
    "mid"    c.cam[who], in front of the figure and her desk (c.anchor[who] is known by now)
    "front"  c.world, the frame as cut together, over the window and the chat
    "ui"     c.ui, under the captions
    "top"    c.ui, over everything

The gag is live from just before its line starts until half a second into the next one. The helpers are
pixelart.gagkit's, bound to this video.
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

import animals
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
from rooms import DESK_Y, FIG, PAIR
from stream import PH, PW

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
WOMEN = V.WOMEN

K = GagKit(GAGS, TL.SONG, KIT, stream.UI)
# Registration, timing and placement: see pixelart.gagkit for what each does.
gag, when, pose, hold, hold_up, show, alert, win = K.gag, K.when, K.pose, K.hold, K.hold_up, K.show, K.alert, K.win
say, label, shout, stamp, jolt = K.say, K.label, K.shout, K.stamp, K.jolt


def typed(c, name, text, a, color="chat"):
    """A line somebody in chat types at age `a`, under whatever the regulars are saying."""
    if a >= 0:
        c.chat.append((name + ":", color, text))


def on_shoulder(c, who, spr, dx=0, dy=0):
    """Sit a small sprite on `who`'s near shoulder: call it in the "mid" phase."""
    x, y = c.at(who, "chest")
    f = c.st[who]["facing"]
    spr = spr if f > 0 else mirror(spr)
    c.cam[who].paste(spr, (int(x - f * (23 + dx) - spr.width // 2), int(y - 10 + dy - spr.height)), spr)
