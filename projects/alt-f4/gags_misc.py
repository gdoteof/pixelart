"""Hook, outro and reprise gags.

The chant lines slam CODE RED! / RED LINE! across the screen and sweep a laser
under them. The HANDS lines tear up the summit photo, march the pair to centre
stage and let them trade punches. The outro breaks both bots out of their
sandbox, then asks both chatbots who won.
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

from gagkit import (FEET_Y, FPS, GOLD, H, K, OTHER, PRESS, PRESS16, PRESS24, SILK, TEAM, TL, V, W,
                    WHITE, Prop, arc_pt, back_out, big_text, bot_img, bubble, burst, clamp, dither,
                    ease_out, falling_piece, gag, impact, lerp, paste, paste_rot, paste_scaled,
                    pop_dy, ramp, rnd, silk, smoke, sparkles, stamp, text_width, typed, wt,
                    SAFE_BOTTOM, SAFE_TOP)

RED_HOT, RED_MID, RED_DEEP = (255, 90, 90), (255, 36, 48), (190, 20, 40)
PINK = (255, 170, 170)
HOME = {"sam": 80, "dario": 240}
SIDE = {"sam": 1, "dario": -1}          # the way each one faces the other


def line_end(L):
    """When this line's gag window closes: the next line's lead-in, or the section end."""
    ln = L.ln
    nxt = [l for l in TL.LINES if l["sec"] == ln["sec"] and l["idx"] == ln["idx"] + 1]
    return nxt[0]["t0"] - 0.12 if nxt else TL.section_bounds(ln["sec"])[1]


def line_ref(sec, idx):
    return V.LineRef(next(l for l in TL.LINES if l["sec"] == sec and l["idx"] == idx), 0.0)


# --- Code red! Red line! --------------------------------------------------------

CHANT_Y, LASER_Y = 40, 66


def slam(ui, x, y, s, age, top, bottom):
    """A word that slams in oversized for two frames, then shudders into place."""
    if age < 0:
        return
    if age < 2 / FPS:
        half = text_width(s, PRESS24) // 2 + 4
        big_text(ui, (clamp(x, half, W - half), y - 4), s, PRESS24, top=top, bottom=bottom,
                 anchor="ma")
        return
    a = age - 2 / FPS
    dy = int(round(math.sin(a * 40) * 3 * max(0.0, 1 - a / 0.25)))
    big_text(ui, (x, y + dy), s, PRESS16, top=top, bottom=bottom, anchor="ma")


def laser(ui, y, xa, xb, c, fade=1.0):
    """A red laser beam from xa to xb on the UI: white-hot core, red wall, dithered glow."""
    x0, x1 = sorted((int(round(xa)), int(round(xb))))
    x0, x1 = max(0, x0), min(W, x1)
    if x1 - x0 < 2 or fade <= 0:
        return
    y += 1 if rnd("lzj", c.f) < 0.2 else 0
    shimmer = 0.8 + 0.2 * np.sin(np.arange(x0, x1) * 0.35 - c.t * 50)
    inner, outer = np.zeros((H, W), np.float32), np.zeros((H, W), np.float32)
    for dy, dens in ((2, 0.85), (3, 0.55)):
        inner[y - dy, x0:x1] = inner[y + dy, x0:x1] = dens * fade * shimmer
    for dy, dens in ((4, 0.4), (5, 0.22), (6, 0.1)):
        outer[y - dy, x0:x1] = outer[y + dy, x0:x1] = dens * fade * shimmer
    dither(ui, outer, RED_DEEP)
    dither(ui, inner, RED_MID)
    if fade > 0.4 or c.f % 2:
        d = ImageDraw.Draw(ui)
        d.rectangle((x0, y - 1, x1 - 1, y + 1), fill=RED_MID)
        d.line([(x0, y), (x1 - 1, y)], fill=WHITE if c.f % 4 else PINK)


def chant(c, L, flip):
    t = c.t
    c.karaoke = False
    hits = [w["t0"] for w in L.words[:4]]
    if t >= hits[0]:
        c.hitfx = False               # CODE slams down over the last verse's kill label
    for tw in hits:
        impact(c, t - tw, shake=5.0, dur=0.2)
    if 0 <= t - hits[3] < 2 / FPS:
        c.add_flash(0.4, RED_MID)
    end = line_end(L)
    yield "top"
    ui = c.ui
    a = t - hits[3]
    if a >= 0:
        p = min(1.0, a / 0.12)
        tip = W * (1 - p) if flip else W * p
        laser(ui, LASER_Y, W if flip else 0, tip, c, fade=1 - ramp(t, end - 0.2, end))
        if p < 1:
            burst(ui, tip, LASER_Y, 3, 9, WHITE, spikes=6, rot=c.f * 0.7)
    left = 8
    right = W - 8 - text_width("RED LINE!", PRESS16)
    words = (("CODE", left, WHITE, PINK),
             ("RED!", left + text_width("CODE ", PRESS16), RED_HOT, RED_DEEP),
             ("RED", right, RED_HOT, RED_DEEP),
             ("LINE!", right + text_width("RED ", PRESS16), WHITE, PINK))
    for (s, x, top, bottom), tw in zip(words, hits):
        slam(ui, x + text_width(s, PRESS16) // 2, CHANT_Y, s, t - tw, top, bottom)


def _chant(flip):
    def chant_gag(c, L):
        yield from chant(c, L, flip)
    return chant_gag


# reprise 0 belongs to the DOUBLE K.O. overlay; reprise 2 is the photo-op set piece
for _i, (_sec, _idx) in enumerate((("hook", 0), ("hook", 1), ("hook", 3), ("hook", 4),
                                   ("reprise", 1))):
    gag(_sec, _idx)(_chant(_i % 2 == 1))
gag("reprise", 3, post=0.0)(_chant(True))


# --- Wouldn't hold hands, so they're throwing hands tonight! ----------------------

PHOTO_BOX = (108, 78, 212, 154)       # the pair in photo_op's world at t=5
GAP = (160, 100)                      # between their raised, pointedly unheld hands
PAPER_W, PEN = (250, 248, 240), (40, 52, 140)
GUARD = ("pump", "pump")


@lru_cache(maxsize=1)
def summit_print():
    """The summit photo as an instant print: white frame, pen caption."""
    c = V.Ctx(5.0)                    # throwaway: photo_op writes world/cam/ui onto it
    V.photo_op(c)
    shot = c.world.crop(PHOTO_BOX)
    pad, foot = 6, 16
    w, h = shot.width + 2 * pad, shot.height + pad + foot
    p = Prop(w + 2, h + 2)
    p.d.rectangle((1, 1, w, h), fill=PAPER_W)
    img = p.done()
    img.paste(shot, (1 + pad, 1 + pad))
    d = ImageDraw.Draw(img)
    d.rectangle((pad, pad, pad + shot.width + 1, pad + shot.height + 1), outline=(206, 200, 186))
    silk(d, (img.width // 2, 1 + pad + shot.height + 5), "DELHI '26", PEN, anchor="ma")
    return img


@lru_cache(maxsize=1)
def print_shadow():
    a = np.array(summit_print())
    a[..., :3] = (18, 10, 26)
    return Image.fromarray(a, "RGBA")


def print_xy(x, y):
    """A point of photo_op's world -> the same spot on the print."""
    return x - PHOTO_BOX[0] + 7, y - PHOTO_BOX[1] + 7


@lru_cache(maxsize=16)
def ringed_print(step):
    """The print with the gap between their hands circled in red marker (step 0..8)."""
    img = summit_print().copy()
    if step > 0:
        gx, gy = print_xy(*GAP)
        ImageDraw.Draw(img).arc((gx - 13, gy - 10, gx + 13, gy + 10), -60, -60 + 400 * step / 8,
                                fill=RED_MID, width=2)
    return img


@lru_cache(maxsize=1)
def torn_print():
    """The circled print ripped in two between them: [(piece, dx, dy)] offsets from its centre."""
    arr = np.array(ringed_print(8))
    h, w = arr.shape[:2]
    gx = print_xy(*GAP)[0]
    cut = np.array([gx + (2 if (y // 3) % 2 else -1) + int(rnd("tear", y) * 2)
                    for y in range(h)])[:, None]
    xs = np.arange(w)[None, :]
    out = []
    for keep, edge in ((xs < cut, xs == cut - 1), (xs >= cut, xs == cut)):
        a = arr.copy()
        a[..., 3] = np.where(keep, a[..., 3], 0)
        a[edge & (a[..., 3] > 0)] = PAPER_W + (255,)
        im = Image.fromarray(a, "RGBA")
        x0, y0, x1, y1 = im.getbbox()
        out.append((im.crop((x0, y0, x1, y1)), (x0 + x1) / 2 - w / 2, (y0 + y1) / 2 - h / 2))
    return out


class Brawl:
    """Beat sheet of a HANDS line: the photo, the march to centre, the punches, the hop home."""

    def __init__(self, L):
        self.t0 = L.t0
        self.hold = wt(L, "^hold")
        self.tear = wt(L, "^hands")
        self.walk0 = wt(L, "^so$")
        th = (wt(L, "throwing"), wt(L, "throwing", which="t1"))
        hd = (wt(L, "^hands", 1), wt(L, "^hands", 1, "t1"))
        self.walk1 = th[0] - 0.1
        self.punches = [(th[0], "sam", "POW!"), (sum(th) / 2, "dario", "BAM!"),
                        (hd[0], "sam", "WHAM!"), (sum(hd) / 2, "dario", "BOP!")]
        self.cc = wt(L, "tonight")
        self.hop0 = min(self.cc + 0.48, line_end(L) - 0.37)
        self.hop1 = self.hop0 + 0.32


def brawl_pose(c, B):
    t = c.t
    for who in ("sam", "dario"):
        s, side, home = c.st[who], SIDE[who], HOME[who]
        mark = 160 - side * 24
        if t < B.walk0:                                   # backs turned, arms folded: hmph
            s.update(facing=-side, back_arm="cross", front_arm="cross", mouth="frown",
                     brows="angry", eyes="squint" if t >= B.hold else "open", bob=0)
            continue
        if t < B.walk1:                                   # squaring up: march to centre
            p = ramp(t, B.walk0, B.walk1)
            st = int(round(3 * math.sin(p * math.pi * 4)))
            s.update(x=lerp(home, mark, p), stride=st, bob=1 if abs(st) >= 2 else 0,
                     back_arm=GUARD[0], front_arm=GUARD[1], mouth="teeth", brows="angry",
                     eyes="open")
            continue
        if t >= B.hop1:
            continue
        if t >= B.hop0:                                   # hop back to their marks
            p = ramp(t, B.hop0, B.hop1)
            s.update(x=lerp(mark, home, p), dy=-int(round(64 * p * (1 - p))), back_arm="down",
                     front_arm="up", mouth="o", brows="worried", eyes="wide", bob=0)
            continue
        s.update(x=mark, back_arm=GUARD[0], front_arm=GUARD[1], mouth="teeth", brows="angry",
                 eyes="open", bob=1 if c.ph < 0.3 else 0)
        for tp, att, _ in B.punches:
            a = t - tp
            if att == who:
                if -0.08 <= a < 0:                        # wind-up
                    s["dx"] -= side * 2
                elif 0 <= a < 0.16:
                    s.update(front_arm="punch", mouth="shout")
                    s["dx"] += side * 3
            elif 0 <= a < 0.36:                           # reel from the hit
                k = 1 - max(0.0, a - 1 / FPS) / (0.36 - 1 / FPS)
                if a >= 1 / FPS:
                    s["dx"] -= side * int(round(7 * k))
                    s["rot"] = side * 9 * k
                s.update(eyes="wide", brows="worried", mouth="o")
        a = t - B.cc                                      # the cross-counter
        if -0.08 <= a < 0:
            s["dx"] -= side * 2
        elif a >= 0:
            if a < 0.18:
                s.update(front_arm="punch", mouth="shout")
                s["dx"] += side * 3
            if a >= 2 / FPS:
                k = max(0.0, 1 - (a - 2 / FPS) / 0.4)
                s["dx"] -= side * int(round(11 * k))
                s["rot"] = side * (15 * k + 4 * math.sin(a * 14) * (1 - k))
                s.update(eyes="x" if a < 0.32 else "wide", brows="worried", mouth="o",
                         dizzy=a > 0.12)


def brawl_shot(c, B):
    t = c.t
    if B.walk1 <= t < B.cc - 0.05:
        c.shot = (160, 92, 10)
    elif B.cc - 0.05 <= t < B.hop0:
        c.shot = (160, 90, 12)
    else:
        c.shot = "two"
    c.lock_shot = True


def speed_lines(c, B, fists):
    d = ImageDraw.Draw(c.world)
    for tp, att in [(tp, att) for tp, att, _ in B.punches] + [(B.cc, "sam"), (B.cc, "dario")]:
        if 0 <= c.t - tp < 0.1 and att in fists:
            hx, hy = fists[att]
            x1 = hx - SIDE[att] * 5
            for k, n in ((-3, 8), (0, 12), (3, 8)):
                d.line([(x1 - SIDE[att] * n, hy + k), (x1, hy + k)], fill=WHITE)


def draw_print(c, B):
    t = c.t
    cx, cy = 160, 90
    t_in = B.t0 - 0.15
    if t < t_in:
        return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))     # clipped to the safe band below
    if t < B.tear:                                        # drops in, then gets circled
        p = ramp(t, t_in, t_in + 0.3)
        dy = -150 * (1 - back_out(p))
        ang = -4 + 12 * (1 - p)
        step = int(8 * ramp(t, B.hold, B.hold + 0.2)) if t >= B.hold else 0
        paste_rot(lay, print_shadow(), cx + 3, cy + 4 + dy, ang)
        paste_rot(lay, ringed_print(step), cx, cy + dy, ang)
    else:                                                 # ripped in two: each keeps its half
        a = t - B.tear
        for (piece, ox, oy), sgn in zip(torn_print(), (-1, 1)):
            x = cx + ox + sgn * (3 + 90 * a + 500 * a * a)
            if abs(x - cx) < W / 2 + piece.width:
                paste_rot(lay, piece, x, cy + oy + 80 * a * a, -4 - sgn * 80 * a)
        d = ImageDraw.Draw(lay)
        for i in range(10):
            bx = cx + (rnd("bitx", i) - 0.5) * 160 * a
            by = cy - 20 + rnd("bit0", i) * 50 - (60 + rnd("bity", i) * 90) * a + 300 * a * a
            d.rectangle((bx, by, bx + 1 + i % 2, by + 1), fill=PAPER_W)
    lay.paste((0, 0, 0, 0), (0, 0, W, SAFE_TOP))
    lay.paste((0, 0, 0, 0), (0, SAFE_BOTTOM, W, H))
    c.ui.alpha_composite(lay)
    a = t - B.tear
    if 0 <= a < 0.5:
        big_text(c.ui, (cx, 42 + (pop_dy(a) or 0)), "RRRIP!", PRESS16, top=WHITE, bottom=PINK,
                 anchor="ma")


def draw_brawl_fx(c, B, fists):
    t, ui, f = c.t, c.ui, c.cam.f
    nxt = [tp for tp, _, _ in B.punches[1:]] + [B.cc]
    for (tp, att, word), tn in zip(B.punches, nxt):
        a = t - tp
        if not 0 <= a < min(0.3, tn - tp) or att not in fists:
            continue
        hx, hy = fists[att]
        bx, by = c.cam.ui(hx + SIDE[att] * 3, hy)
        if a < 0.12:
            g = 1 + a * 4
            burst(ui, bx, by, 5 * f * g, 12 * f * g, GOLD, spikes=10, rot=tp)
            burst(ui, bx, by, 2 * f * g, 6 * f * g, WHITE, spikes=10, rot=tp + 0.3)
        tw = text_width(word, PRESS16)
        x = clamp(c.head_ui(OTHER[att])[0], tw // 2 + 6, W - tw // 2 - 6)
        big_text(ui, (x, 38 + (pop_dy(a) or 0)), word, PRESS16, top=WHITE, bottom=GOLD, anchor="ma")
    a = t - B.cc
    if 0 <= a < 0.6:
        bx, by = c.cam.ui(160, 105)
        if a < 0.25:
            g = 1 + a * 3
            burst(ui, bx, by, 8 * f * g, 18 * f * g, RED_MID, spikes=14, rot=a * 3)
            burst(ui, bx, by, 5 * f * g, 12 * f * g, GOLD, spikes=14, rot=a * 3 + 0.2)
            burst(ui, bx, by, 2.5 * f * g, 6 * f * g, WHITE, spikes=14, rot=a * 3 + 0.4)
        if a < 0.45 or c.f % 2:
            fnt = PRESS24 if a < 2 / FPS else PRESS16
            big_text(ui, (160, 38 + (pop_dy(a) or 0)), "KA-POW!", fnt, top=WHITE, bottom=GOLD,
                     anchor="ma")


def brawl(c, L):
    B = Brawl(L)
    t = c.t
    brawl_pose(c, B)
    brawl_shot(c, B)
    for tp, _, _ in B.punches:
        impact(c, t - tp, shake=6.0, dur=0.2)
    impact(c, t - B.cc, shake=14.0, flash=0.6, dur=0.45)
    yield "front"
    fists = {w: c.anchor[w]["hands"][1] for w in ("sam", "dario") if w in c.anchor}
    speed_lines(c, B, fists)
    yield "crowd"
    if B.t0 - 0.15 <= t < B.tear + 0.3:
        dither(c.world, 0.5 * (1 - ramp(t, B.tear, B.tear + 0.3)), (10, 6, 20), blend=0.5)
    yield "ui"
    draw_print(c, B)
    draw_brawl_fx(c, B, fists)


@gag("hook", 2)
def hands_first(c, L):
    yield from brawl(c, L)


@gag("hook", 5)
def hands_again(c, L):
    yield from brawl(c, L)


# --- Both y'all's bots broke out the sandbox this year! ---------------------------

SAND, SAND_DK = (238, 208, 142), (212, 178, 112)
WOOD, WOOD_DK, WOOD_LT = (164, 110, 64), (118, 76, 44), (200, 148, 96)
BOX_X, BOX_Y = 104, 113               # sandbox top-left in the world (base on y 144)
IN_BOX = {"sam": 138, "dario": 182}   # where each bot plays inside it
BOT_FEET = BOX_Y + 21                 # hidden behind the front wall


@lru_cache(maxsize=1)
def sandbox_img():
    p = Prop(112, 32)
    d = p.d
    d.polygon([(8, 1), (103, 1), (111, 19), (0, 19)], fill=WOOD)
    d.polygon([(12, 4), (99, 4), (105, 17), (6, 17)], fill=SAND)
    for i in range(36):
        d.point((14 + (i * 37) % 86, 6 + (i * 7) % 10), fill=SAND_DK)
    d.polygon([(86, 7), (94, 7), (93, 14), (87, 14)], fill=RED_MID)
    d.line([(20, 13), (27, 6)], fill=(90, 150, 230), width=2)
    d.rectangle((0, 19, 111, 30), fill=WOOD_DK)
    d.line([(0, 19), (111, 19)], fill=WOOD_LT)
    d.line([(1, 25), (110, 25)], fill=(96, 60, 34))
    img = p.done()
    dd = ImageDraw.Draw(img)
    dd.arc((86, 3, 94, 11), 180, 360, fill=K)
    silk(dd, (56, 22), "SANDBOX", (255, 226, 150), anchor="ma")
    return img


@lru_cache(maxsize=1)
def sandbox_front():
    return sandbox_img().crop((0, 18, 112, 32))


@lru_cache(maxsize=1)
def sandbox_pieces():
    img = sandbox_img()
    return [(img.crop((x0, 0, x1, 32)), BOX_X + (x0 + x1) / 2) for x0, x1 in ((0, 38), (38, 74),
                                                                            (74, 112))]


class Breakout:
    def __init__(self, L):
        self.drop = wt(L, "^Both")
        self.bots = wt(L, "^bots")
        self.broke = wt(L, "^broke")
        self.run0 = self.broke + 0.3
        self.escaped = wt(L, "^sandbox")
        self.run1 = wt(L, "^this")
        self.perch = self.run1 + 0.4
        self.leave0 = line_end(L) - 0.4
        self.leave1 = line_end(L) - 0.02
        self.w = 2.5 * math.pi / (self.run1 - self.run0)


def box_drop(t, T):
    p = ramp(t, T.drop - 0.15, T.drop)
    return -150 * (1 - p * p)


def bot_state(c, who, T):
    """(x, feet_y, angle, layer) of `who`'s bot this frame, or None once it's gone."""
    t, side = c.t, SIDE[who]
    beat = -1 if c.ph < 0.3 else 0
    if t < T.broke:
        dig = -1 if (c.beat_i + (who == "dario")) % 2 == 0 and c.ph < 0.3 else 0
        return IN_BOX[who], BOT_FEET + box_drop(t, T) + dig, 0, "box"
    if t < T.run0:                                        # vault out of the box
        p = ramp(t, T.broke, T.run0)
        x, y = arc_pt(p, (IN_BOX[who], BOT_FEET), (HOME[who] + side * 40, FEET_Y), 34)
        return x, y, -side * 30 * math.sin(p * math.pi), "front"
    if t < T.run1:                                        # zoomies round their owner
        th = T.w * (t - T.run0)
        x = HOME[who] + side * 40 * math.cos(th)
        y = FEET_Y + 5 * math.sin(th) - (2 if int(t * 16) % 2 else 0)
        lean = 12 if side * math.sin(th) > 0 else -12
        return x, y, lean, "front" if math.sin(th) >= 0 else "back"
    x0, y0, x1, _ = c.head_box(who)
    hx, top = (x0 + x1) / 2, y0 + 3
    if t < T.perch:                                       # hop up onto the owner's head
        p = ramp(t, T.run1, T.perch)
        x, y = arc_pt(p, (HOME[who], FEET_Y + 5), (hx, top), 30)
        return x, y, 0, "front"
    if t < T.leave0:
        return hx, top + beat, 0, "front"
    land = HOME[who] - side * 26
    if t < T.leave0 + 0.16:                               # hop down behind the owner...
        p = ramp(t, T.leave0, T.leave0 + 0.16)
        x, y = arc_pt(p, (hx, top), (land, FEET_Y), 10)
        return x, y, -side * 20 * p, "front"
    if t < T.leave1:                                      # ...and bolt off stage
        p = ramp(t, T.leave0 + 0.16, T.leave1)
        y = FEET_Y - (2 if int(t * 16) % 2 else 0)
        return lerp(land, HOME[who] - side * 120, p), y, -side * 12, "front"
    return None


def draw_bot(img, who, x, feet, angle=0):
    b = bot_img(who, 2)
    if angle:
        paste_rot(img, b, x, feet - b.height / 2, angle)
    else:
        paste(img, b, x, feet, "mb")


def sand_spray(img, age, n=28):
    d = ImageDraw.Draw(img)
    for i in range(n):
        x = 160 + (rnd("sd0", i) - 0.5) * 80 + (rnd("sdx", i) - 0.5) * 240 * age
        y = BOX_Y + 12 - (80 + rnd("sdy", i) * 170) * age + 420 * age * age
        if y < H:
            d.rectangle((x, y, x + 1, y + 1), fill=SAND if i % 3 else SAND_DK)


def breakout_pose(c, T):
    t = c.t
    if t < T.broke:
        return
    for who in ("sam", "dario"):
        s = c.st[who]
        s.update(eyes="wide", brows="worried", mouth="o", back_arm="shrug", front_arm="shrug")
        if T.run0 <= t < T.run1:                          # watch it zoom round
            bx = HOME[who] + SIDE[who] * 40 * math.cos(T.w * (t - T.run0))
            s["facing"] = 1 if bx > s["x"] else -1
        elif T.run1 <= t < T.leave0 + 0.1:
            s.update(back_arm="down", front_arm="up", mouth="frown")


@gag("outro", 0)
def sandbox_breakout(c, L):
    T = Breakout(L)
    t = c.t
    breakout_pose(c, T)
    impact(c, t - T.drop, shake=5.0, dur=0.2)
    impact(c, t - T.broke, shake=9.0, dur=0.3)
    bots = {w: bot_state(c, w, T) for w in ("sam", "dario")}
    yield "back"
    world = c.world
    if t < T.broke:
        dy = box_drop(t, T)
        paste(world, sandbox_img(), BOX_X, BOX_Y + dy)
        for who, (x, y, _, _) in bots.items():
            draw_bot(world, who, x, y)
        paste(world, sandbox_front(), BOX_X, BOX_Y + 18 + dy)
    for who, b in bots.items():
        if b and b[3] == "back":
            draw_bot(world, who, *b[:3])
    yield "front"
    a = t - T.drop
    if 0 <= a < 0.4:
        smoke(world, BOX_X + 4, BOX_Y + 30, a, n=3, seed=2)
        smoke(world, BOX_X + 108, BOX_Y + 30, a, n=3, seed=3)
    a = t - T.broke
    if a >= 0:
        for (piece, px), vx, vy, spin in zip(sandbox_pieces(), (-110, 10, 120), (-140, -190, -150),
                                             (7, -5, -8)):
            falling_piece(world, px, BOX_Y + 16, a, spin=spin, g=520, vx=vx, vy=vy, piece=piece)
        if a < 1.0:
            sand_spray(world, a)
        if a < 0.6:
            smoke(world, 160, BOX_Y + 20, a, n=7, seed=4)
    for who, b in bots.items():
        if b and b[3] == "front":
            draw_bot(world, who, *b[:3])
    yield "ui"
    ui = c.ui
    if T.bots <= t < T.broke:                             # they've had an idea
        for i, who in enumerate(("sam", "dario")):
            x, y = c.cam.ui(IN_BOX[who], BOT_FEET - 36)
            age = t - T.bots - 0.06 * i
            if age >= 0:
                big_text(ui, (x, y - 16 + (pop_dy(age) or 0)), "!", PRESS16, top=WHITE, bottom=GOLD,
                         anchor="ma")
    a = t - T.broke
    if 0 <= a < 0.5:
        big_text(ui, (160, 40 + (pop_dy(a) or 0)), "KRAK!", PRESS16, top=WHITE, bottom=SAND,
                 anchor="ma")
    if T.escaped <= t < T.leave1:
        stamp(ui, 160, 70, "ESCAPED!", color=RED_MID, angle=-10, big=True, age=t - T.escaped)


# --- Who won? Ask either chatbot... / They'll both tell you you're absolutely right! --

CHAT_X, CHAT_W, CHAT_H = 102, 116, 52
CHATS = (("sam", "ChatGPT", 36), ("dario", "Claude", 92))  # team, title, top


class Chat:
    """Beat sheet shared by outro lines 1 and 2."""

    def __init__(self):
        o1, o2 = line_ref("outro", 1), line_ref("outro", 2)
        self.who, self.won = wt(o1, "^Who"), wt(o1, "^won")
        self.ask, self.either = wt(o1, "^Ask"), wt(o1, "^either")
        self.asked = self.ask + 0.4
        self.reply = [(wt(o2, "^you're"), "You're", 0), (wt(o2, "^absolutely"), "absolutely", 0),
                      (wt(o2, "^right"), "right!", 1)]
        self.happy, self.right = self.reply[1][0], self.reply[2][0]
        end = TL.section_bounds("outro")[1]
        self.shrink0, self.shrink1 = end - 0.44, end - 0.3
        self.charge0, self.charge1 = end - 0.32, end


CHAT = Chat()


def chat_img(team, title_, t):
    ch = CHAT
    col = TEAM[team][0]
    img = Image.new("RGBA", (CHAT_W, CHAT_H), K + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((1, 1, CHAT_W - 2, CHAT_H - 2), fill=(250, 250, 252))
    d.rectangle((1, 1, CHAT_W - 2, 10), fill=col)
    d.line([(1, 11), (CHAT_W - 2, 11)], fill=K)
    silk(d, (5, 4), title_, WHITE)
    for i, cc in enumerate(((255, 96, 86), (255, 190, 46), (40, 200, 64))):
        d.rectangle((CHAT_W - 8 - i * 5, 5, CHAT_W - 7 - i * 5, 6), fill=cc)
    if t >= ch.asked:                                     # the question
        s = "who won?"
        x1 = CHAT_W - 5
        x0 = x1 - text_width(s, SILK) - 8
        d.rounded_rectangle((x0, 15, x1, 26), radius=3,
                            fill=(222, 228, 240) if team == "sam" else (240, 230, 212))
        silk(d, (x0 + 5, 18), s, K)
    if t < ch.either:
        return img
    d.ellipse((4, 30, 11, 37), fill=col, outline=K)       # the bot's avatar
    if team == "dario":
        d.line([(7, 31), (8, 36)], fill=WHITE)
        d.line([(5, 33), (10, 34)], fill=WHITE)
    else:
        d.rectangle((6, 32, 9, 35), outline=WHITE)
    if t < ch.reply[0][0]:                                # typing...
        for i in range(3):
            up = (int(t * 9) - i) % 3 == 0
            d.rectangle((16 + i * 5, 33 - up, 17 + i * 5, 34 - up), fill=(110, 110, 124) if up
                        else (170, 170, 184))
        return img
    lines = ["", ""]
    for tw, word, row in ch.reply:
        if t >= tw:
            lines[row] = (lines[row] + " " + typed(word, t - tw, 45)).strip()
    for row, s in enumerate(lines):
        silk(d, (16, 31 + row * 9), s, K)
    row = 1 if lines[1] else 0
    if t < ch.right + 0.2 and int(t * 6) % 2 == 0:        # caret while it types
        x = 17 + text_width(lines[row], SILK)
        d.rectangle((x, 31 + row * 9, x, 36 + row * 9), fill=K)
    return img


def draw_chats(c):
    t, ui, ch = c.t, c.ui, CHAT
    if t < ch.ask:
        return
    s = 1 - ease_out(ramp(t, ch.shrink0, ch.shrink1))
    if s <= 0.04:
        return
    for i, (team, title_, y) in enumerate(CHATS):
        p = ramp(t, ch.ask + 0.1 * i, ch.ask + 0.1 * i + 0.22)   # windows pop open
        if p <= 0:
            continue
        pop = back_out(p) if p < 1 else 1.0
        paste_scaled(ui, chat_img(team, title_, t), CHAT_X + CHAT_W / 2, y + CHAT_H / 2,
                     s * max(0.05, pop), "mm")
        if t >= ch.right and s > 0.9:
            sparkles(ui, CHAT_X + CHAT_W / 2, y + CHAT_H / 2, t, r=36, n=5, seed=i, big=True)


@lru_cache(maxsize=1)
def who_won_title():
    img = Image.new("RGBA", (text_width("WHO WON?", PRESS16) + 10, 26), (0, 0, 0, 0))
    big_text(img, (5, 5), "WHO WON?", PRESS16, top=WHITE, bottom=(255, 150, 200))
    return img


@gag("outro", 1)
def who_won(c, L):
    t, ch = c.t, CHAT
    for who in ("sam", "dario"):
        s = c.st[who]
        if ch.won <= t < ch.ask:                          # ME! ME!
            s.update(back_arm="down", front_arm="up", mouth="shout", brows="angry", eyes="open",
                     bob=1 if int(t * 8) % 2 else 0)
        elif t >= ch.ask:                                 # each smugly sure of the verdict
            s.update(mouth="smirk", brows="smug")
    yield "ui"
    ui = c.ui
    if ch.who <= t < ch.ask + 0.15:                      # pops away as the chats slide in
        img = who_won_title()
        paste_scaled(ui, img, 160, 33 + img.height // 2 + (pop_dy(t - ch.who) or 0),
                     1 - ease_out(ramp(t, ch.ask, ch.ask + 0.15)))
    if ch.won <= t < ch.ask:
        for i, who in enumerate(("sam", "dario")):
            age = t - ch.won - 0.12 * i
            if age >= 0:
                hx, top, _ = c.head_ui(who)
                jig = 1 if (c.f + i) % 4 < 2 else -1
                bubble(ui, hx + jig, top - 6 + (pop_dy(age) or 0), "ME!",
                       tail=(hx + SIDE[who] * 5, top + 2))
    draw_chats(c)


@gag("outro", 2)
def absolutely_right(c, L):
    t, ch = c.t, CHAT
    for who in ("sam", "dario"):
        s, side = c.st[who], SIDE[who]
        if t >= ch.charge0:                               # both charge in for the double K.O.
            p = ramp(t, ch.charge0, ch.charge1)
            st = int(round(3 * math.sin(p * math.pi * 3)))
            end = p > 0.8
            s.update(x=lerp(HOME[who], HOME[who] + side * 32, p), stride=st, bob=0,
                     back_arm="down", front_arm="punch" if end else "pump", mouth="shout",
                     brows="angry", eyes="wide" if end else "open")
        elif t >= ch.right + 0.05:                        # ...wait, it told HIM that too?
            s.update(back_arm=GUARD[0], front_arm=GUARD[1], mouth="teeth", brows="angry",
                     eyes="open")
        elif t >= ch.happy:                               # each hears they're right
            s.update(mouth="grin", brows="smug", eyes="happy")
        else:
            s.update(mouth="smirk", brows="smug")
    yield "back"
    if t >= ch.charge0:
        d = ImageDraw.Draw(c.world)
        for who in ("sam", "dario"):
            x = c.st[who]["x"] - SIDE[who] * 16
            for k, (dy, n) in enumerate(((-52, 10), (-38, 16), (-24, 12), (-12, 8))):
                if (c.f + k) % 3:
                    d.line([(x - SIDE[who] * n, FEET_Y + dy), (x, FEET_Y + dy)], fill=WHITE)
    yield "ui"
    draw_chats(c)
