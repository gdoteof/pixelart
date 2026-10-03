"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a video.Ctx and `L` a
pixelart.gags.LineRef. Code before the first yield runs at setup: pick c.shot, pose c.st[who], hand
someone a prop (`hold`), light the phone, swap the neon. Then each `yield "<phase>"` waits for that
drawing phase:

    "back"   world: on the wall, behind the hosts (the host's portrait: `paint_portrait`)
    "mid"    world: in front of the hosts and the desk (their anchors are in c.anchor by now)
    "front"  world: in front of everything in the studio
    "ui"     UI layer, under the lower third
    "top"    UI layer, over everything

The gag is live from just before its line starts until the next line starts.

Layout (world pixels; the wide shot shows the whole 320x180 world):
    the neon sign            studio.NEON = (112, 18, 208, 50), between the heads; insets go over it
    Newsom's head            about (59-99, 49-89), facing right; his hands on the desk about (70-92, 118)
    Mamdani's head           about (221-261, 49-89), facing left; his hands on the desk about (230-250, 118)
    the host's portrait      studio.PICTURE = (271, 17, 303, 57), top right
    the desk                 far edge y 120; the lower third covers UI y 142-169, the chat ticker 170-180
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

import props as P
import studio
import timeline as TL
import video as V
from characters import FW, HEAD_CHIN, NECK, figure, head
from engine import (C, INK, PRESS, PRESS16, SILK, SILK16, H, W, Canvas, arc_pt, back_out, blend, blend_poly, clamp, col,
                    dither, ease_in, ease_in_out, ease_out, fade_to, lerp, mirror, mix, outline_text, outlined, paste,
                    paste_rot, paste_scaled, pop_dy, ramp, rnd, scaled, silk, tint, wobble)
from pixelart import fx, pixel
from pixelart.camera import Cam

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
PIC = studio.PICTURE
INSET = (118, 18, 202, 82)                 # the broadcast inset, over the neon sign between the heads


def gag(sec, idx, pre=0.12, post=0.5):
    """Register a line's gag. It runs from just before its line until half a second into the next one, so a
    punchline on the last word stays up while the next gag starts (the later gag's poses win)."""
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


def age(L, pat, n=0):
    """Seconds since that word started (negative before)."""
    return L.t - wt(L, pat, n)


def end_of(L):
    """When the line's last word is sung."""
    return L.words[-1]["t0"]


def k_in(a, dur=0.2):
    """0 -> 1 over `dur` seconds from age a (clamped)."""
    return clamp(a / dur, 0.0, 1.0)


def when(sec, idx, pat=None, n=0):
    """The time a line starts (or a word in it is sung), for gags that outlive their line."""
    ln = TL.line(sec, idx)
    if pat is None:
        return ln["t0"]
    k = 0
    for w in ln["words"]:
        if re.search(pat, w["w"], re.I):
            if k == n:
                return w["t0"]
            k += 1
    raise KeyError(f"{pat!r} not in {ln['text']!r}")


# --- posing and props ------------------------------------------------------------------------

def hold(c, who, prop, arms="show", at=None, lock=True):
    """Have `who` hold a prop in front of him: a board or a phone shown to the camera by its bottom corners
    ("show"), or something smaller in both hands at the chest ("hold")."""
    s = c.st[who]
    at = at or ("hands_top" if arms == "show" else "hands")
    s["arms"], s["held"] = arms, (prop, at)
    if lock:
        s["gesture"] = False


def hold_up(c, who, prop, lift=0):
    """One hand raises a prop: the far hand, the prop's bottom in the fist."""
    s = c.st[who]
    s["arms"], s["gesture"] = "hold1", False
    s["held"] = (prop, ("hand_far", prop.height // 2 - 2 + lift))


def pose(c, who, **kw):
    """Set pose fields and stop the automatic gestures from overriding the arms."""
    s = c.st[who]
    if "arms" in kw:
        s["gesture"] = False
    s.update(kw)


def anchor(c, who, name):
    """A world anchor of a host drawn this frame (only from the "mid" phase on)."""
    return c.anchor[who][name]


def head_box(c, who):
    """The head canvas (40x40) of a drawn host, in world pixels."""
    hx, hy = c.anchor[who]["head"]
    return hx - 20, hy, hx + 20, hy + 40


def on_head(c, img, who, spr, dy=0, dx=0):
    """Paste a head-sized sprite (a cap, a crown, a wig) over who's head, facing his way. The sprite is drawn
    facing right on a 40-wide canvas whose top sits at the top of the head canvas."""
    x0, y0, _, _ = head_box(c, who)
    s = c.st[who]
    spr = spr if s["facing"] > 0 else mirror(spr)
    img.paste(spr, (x0 + dx * s["facing"] + (40 - spr.width if s["facing"] < 0 else 0), y0 + dy), spr)


def face_pt(c, who, x, y):
    """A point on who's head given in head-canvas pixels (facing right), in world pixels."""
    x0, y0, _, _ = head_box(c, who)
    s = c.st[who]
    return (x0 + x, y0 + y) if s["facing"] > 0 else (x0 + 39 - x, y0 + y)


def put(img, spr, x, y, anchor="mm"):
    paste(img, spr, int(round(x)), int(round(y)), anchor)


def pop_in(img, spr, x, y, a, dur=0.18, anchor="mm"):
    """A sprite that pops in (overshoots and settles) from age 0; nothing before."""
    if a < 0:
        return
    s = back_out(min(1.0, a / dur)) if a < dur else 1.0
    if s <= 0.05:
        return
    paste_scaled(img, spr, int(round(x)), int(round(y)), s, anchor)


def fly(img, spr, p0, p1, p, h=20, rot=0.0):
    """A sprite thrown along an arc from p0 to p1 (p from 0 to 1), spinning by `rot` turns."""
    if not 0 <= p <= 1:
        return
    x, y = arc_pt(p, p0, p1, h)
    if rot:
        paste_rot(img, spr, int(round(x)), int(round(y)), rot * 360 * p)
    else:
        put(img, spr, x, y)


# --- the host's portrait, top right -----------------------------------------------------------------

def paint_portrait(img, pic):
    """Hang a picture (RGB or RGBA, any size: it is cropped to fill) in the host's frame."""
    x0, y0, x1, y1 = PIC
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if pic.size != (w, h):
        sx, sy = w / pic.width, h / pic.height
        s = max(sx, sy)
        pic = pic.resize((max(w, int(pic.width * s)), max(h, int(pic.height * s))), Image.NEAREST)
        ox, oy = (pic.width - w) // 2, (pic.height - h) // 2
        pic = pic.crop((ox, oy, ox + w, oy + h))
    img.paste(pic.convert("RGB"), (x0, y0))


# --- the UI: insets, bubbles, pops -----------------------------------------------------------------

def inset(c, box, pic, caption=None, k=1.0, frame_col="neon_glow"):
    """A picture-in-picture in the UI (RGB/RGBA, scaled to fit with nearest neighbour), in a lit frame, with
    a caption tab. k < 1 slides it in from the top."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if c.cards and c.sec in V.CARDS:                                   # wait for the chapter card to leave
        k = min(k, k_in(c.t - (c.sa + V.CARD_TIME), 0.25))
    if k <= 0:
        return
    off = -int((1 - ease_out(clamp(k, 0, 1))) * (y1 + 12))
    y0, y1 = y0 + off, y1 + off
    d = ImageDraw.Draw(c.ui)
    d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=INK + (255,))
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=col(frame_col) + (255,))
    im = pic if pic.size == (w, h) else pic.resize((w, h), Image.NEAREST)
    c.ui.paste(im.convert("RGBA"), (x0, y0))
    if caption:
        tw = pixel.text_width(caption, SILK) + 6
        d.rectangle((x0 - 1, y1 + 2, x0 + tw, y1 + 10), fill=C["blue_sh"] + (255,))
        V.ui_text(c.ui, (x0 + 2, y1 + 4), caption)


def inset_k(L, a0, out=None):
    """Slide an inset in from word age a0 (shown from 0.2 s before it), and keep it up for the line."""
    return k_in(a0 + 0.2, 0.25)


def say(c, who, lines, a, tail_dx=0, dy=-4, dur=None):
    """A speech bubble over who's head from age a (and until a reaches dur)."""
    if a < 0 or (dur is not None and a > dur):
        return
    hx, hy = c.anchor[who]["head"]
    x, y = c.to_ui(hx, hy)
    s = c.st[who]
    bx = x + 20 * (1 if s["facing"] > 0 else -1)
    fx.bubble(c.ui, int(bx), int(y + dy), list(lines) if not isinstance(lines, str) else [lines],
              tail=(int(x + 6 * s["facing"] + tail_dx), int(y + 10)), fnt=PRESS, fill=C["white"], ink=INK)


def think(c, who, pic, a, dy=-6, dur=None):
    """A thought bubble with a picture in it, over who's head."""
    if a < 0 or (dur is not None and a > dur):
        return
    hx, hy = c.anchor[who]["head"]
    x, y = c.to_ui(hx, hy)
    s = c.st[who]
    w, h = pic.size
    cx = int(x + 26 * s["facing"])
    top = int(y + dy - h - 8)
    d = ImageDraw.Draw(c.ui)
    k = min(1.0, a / 0.2)
    if k < 1:
        top += int((1 - k) * 6)
    d.ellipse((x + 4 * s["facing"] - 2, y - 3, x + 4 * s["facing"] + 2, y + 1), fill=C["white"] + (255,), outline=INK + (255,))
    d.ellipse((x + 12 * s["facing"] - 3, y - 9, x + 12 * s["facing"] + 3, y - 3), fill=C["white"] + (255,), outline=INK + (255,))
    d.rounded_rectangle((cx - w // 2 - 4, top - 4, cx + w // 2 + 4, top + h + 4), 6, fill=C["white"] + (255,),
                        outline=INK + (255,))
    c.ui.paste(pic.convert("RGBA"), (cx - w // 2, top), pic.convert("RGBA"))


def shout(c, x, y, s, a, size=16, top=None, bottom=None, world=True, dur=None):
    """Comic-book text popping in at a world point (or a UI point with world=False)."""
    if a < 0 or (dur is not None and a > dur):
        return
    if world:
        x, y = c.to_ui(x, y)
    P.word_pop(c.ui, int(x), int(y), s, a, size=size, top=top, bottom=bottom)


def stamp(c, x, y, s, a, color=None, world=True, angle=-12):
    """A rubber stamp slammed onto a point (world or UI)."""
    if a < 0:
        return
    if world:
        x, y = c.to_ui(x, y)
    fx.stamp(c.ui, int(x), int(y), s, fnt=PRESS, color=col(color or "red"), angle=angle, age=a)


def buzz(c, a, dur=0.8):
    """Mamdani's phone lights up and buzzes on the desk."""
    if 0 <= a < dur:
        c.phone_lit = True
        c.phone_dx = (1 if int(a * 30) % 2 else -1) if a < 0.4 else 0
    elif a >= dur:
        c.phone_lit = True
