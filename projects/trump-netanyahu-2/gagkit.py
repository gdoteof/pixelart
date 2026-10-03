"""Shared toolkit for the per-line gags: registration, timing and placement helpers, re-exports.

A gag is a generator `fn(c, L)` registered with `@gag(sec, idx)`; `c` is a video.Ctx and `L` a
pixelart.gags.LineRef. Code before the first yield runs at setup: pick c.shot, pose c.st[who], hand
someone a prop (`hold`), raise the press pool (c.press). Then each `yield "<phase>"` waits for that
drawing phase:

    "back"   world: on the room, behind the chairs and the men (the portrait: `paint_portrait`)
    "mid"    world: in front of the seated men (their anchors are in c.anchor by now)
    "front"  world: in front of everything in the room
    "ui"     UI layer, under the lower third
    "top"    UI layer, over everything

The gag is live from just before its line starts until the next line starts.

Layout (world pixels; the wide shot shows the whole 320x180 world):
    the portrait's picture   office.PICTURE = (145, 22, 175, 74), in a gold frame
    Bibi's head              about (68-108, 49-89), facing right; his lap about (90, 124)
    Trump's head             about (210-250, 51-91), facing left; his lap about (229, 124)
    the mantel shelf         y 84, x 125-195; the little table top (148-172, 132)
    the lower third          UI y 142-169, the ticker 170-180: keep UI text above y 138
"""
# ruff: noqa: F401  (a re-export hub: the gag modules import from here)
import math
import re
from functools import lru_cache

from PIL import Image, ImageDraw

import office
import props as P
import timeline as TL
import video as V
from characters import FW, HEAD_CHIN, NECK, head
from engine import (C, INK, PRESS, PRESS16, SILK, SILK16, H, W, Canvas, arc_pt, back_out, blend, blend_poly, clamp, col,
                    dither,
                    ease_in, ease_in_out, ease_out, fade_to, lerp, mirror, mix, outline_text, outlined, paste,
                    paste_rot, paste_scaled, pop_dy, ramp, rnd, scaled, tint, wobble)
from pixelart import fx, pixel
from pixelart.camera import Cam

FPS = TL.FPS
GAGS = V.GAGS
span = GAGS.span
PIC = office.PICTURE
SEAT = {"bibi": office.SEAT_L, "trump": office.SEAT_R}


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


# --- posing and props ------------------------------------------------------------------------

def hold(c, who, prop, arms="show", at=None, lock=True):
    """Have `who` hold a prop in front of him: a board or folder shown to the cameras by its bottom
    corners ("show"), or something smaller in both hands at the chest ("hold")."""
    s = c.st[who]
    at = at or ("hands_top" if arms == "show" else "hands")
    s["arms"], s["held"] = arms, (prop, at)
    if lock:
        s["gesture"] = False


def hold_up(c, who, prop, lift=0):
    """One hand raises a prop overhead-ish: the far hand, the prop's bottom in the fist."""
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
    """A world anchor of a character drawn this frame (only from the "mid" phase on)."""
    return c.anchor[who][name]


def head_box(c, who):
    """The head canvas (40x40) of a drawn character, in world pixels."""
    hx, hy = c.anchor[who]["head"]
    return hx - 20, hy, hx + 20, hy + 40


def on_head(c, img, who, spr, dy=0):
    """Paste a head-sized sprite (a bonnet, a crown) over who's head, facing his way."""
    x0, y0, _, _ = head_box(c, who)
    s = c.st[who]
    spr = spr if s["facing"] > 0 else mirror(spr)
    img.paste(spr, (x0, y0 + dy), spr)


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


# --- the portrait over the fireplace ----------------------------------------------------------------

def paint_portrait(img, pic):
    """Hang a picture (RGB or RGBA, any size: it is cropped to fill) in the Washington frame."""
    x0, y0, x1, y1 = PIC
    w, h = x1 - x0 + 1, y1 - y0 + 1
    if pic.size != (w, h):
        sx, sy = w / pic.width, h / pic.height
        s = max(sx, sy)
        pic = pic.resize((max(w, int(pic.width * s)), max(h, int(pic.height * s))), Image.NEAREST)
        ox, oy = (pic.width - w) // 2, (pic.height - h) // 2
        pic = pic.crop((ox, oy, ox + w, oy + h))
    img.paste(pic.convert("RGB"), (x0, y0))


def portrait_canvas(color=(60, 52, 44)):
    x0, y0, x1, y1 = PIC
    return Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1), col(color))


# --- the UI: insets, bubbles, pops -----------------------------------------------------------------

def inset(c, box, pic, caption=None, k=1.0):
    """A broadcast inset in the UI: a picture (RGB/RGBA, scaled to fit with nearest neighbour) in a gold
    frame, with a caption tab. k < 1 slides it in from the side it sits on."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if c.cards and c.sec in V.CARDS:                                   # wait for the section card to leave
        k = min(k, k_in(c.t - (c.sa + V.CARD_TIME), 0.25))
    if k <= 0:
        return
    off = int((1 - ease_out(clamp(k, 0, 1))) * (w + 12)) * (-1 if x0 < W // 2 else 1)
    x0, x1 = x0 + off, x1 + off
    d = ImageDraw.Draw(c.ui)
    d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), fill=INK + (255,))
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=C["gold"] + (255,))
    im = pic if pic.size == (w, h) else pic.resize((w, h), Image.NEAREST)
    c.ui.paste(im.convert("RGBA"), (x0, y0))
    if caption:
        tw = pixel.text_width(caption, SILK) + 6
        d.rectangle((x0 - 1, y1 + 2, x0 + tw, y1 + 10), fill=C["red"] + (255,))
        V.ui_text(c.ui, (x0 + 2, y1 + 4), caption)


def say(c, who, lines, a, tail_dx=0, dy=-4, dur=None):
    """A speech bubble over who's head from age a (and until a reaches dur)."""
    if a < 0 or (dur is not None and a > dur):
        return
    hx, hy = c.anchor[who]["head"]
    x, y = c.to_ui(hx, hy)
    s = c.st[who]
    bx = x + 22 * (1 if s["facing"] > 0 else -1)
    fx.bubble(c.ui, int(bx), int(y + dy), list(lines) if not isinstance(lines, str) else [lines],
              tail=(int(x + 6 * s["facing"] + tail_dx), int(y + 10)), fnt=PRESS, fill=C["white"], ink=INK)


def shout(c, x, y, s, a, size=16, top=None, bottom=None, world=True, dur=None):
    """Comic-book text popping in at a world point (or a UI point with world=False)."""
    if a < 0 or (dur is not None and a > dur):
        return
    if world:
        x, y = c.to_ui(x, y)
    P.word_pop(c.ui, int(x), int(y), s, a, size=size, top=top, bottom=bottom)


def flash_press(c, seed, n=6, a=0.0):
    V.press_flashes(c, seed, n, a)


# --- things that stay put across lines -----------------------------------------------------------

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


def forehead(c, who):
    """Where a sticker goes on who's forehead (world), once he's drawn."""
    ex, ey = c.anchor[who]["eye"]
    s = c.st[who]
    return ex + 4 * s["facing"], ey - 9
