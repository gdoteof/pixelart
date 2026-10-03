"""The General Assembly hall, the one set: gold wall, UN emblem, two big screens, the dais, the
rostrum, the flip chart on its easel, the delegation desk and the delegates in the front rows.

The wide shot (the whole 320x180 world) is home. Whoever raps stands at the rostrum
(centre); the other one heckles from the delegation desk (front right); the rapper's
visual aids go on the flip chart (left). The screens over the chart and the desk show
UN Web TV's close-ups of the rapper and of the heckler.

Static layers are drawn once and cached; video.py lays the per-frame parts over them.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, SILK, H, W, Canvas, col, dither, mask, mix, rnd, vgrad
from pixelart import pixel

# --- layout (world pixels) -----------------------------------------------------------------

WALL_BOTTOM = 124                       # where the gold wall meets the floor
EMBLEM = (160, 27, 17)                  # the UN emblem: centre and radius
SCREEN_L = (8, 8, 98, 62)               # outer frames of the two big screens
SCREEN_R = (222, 8, 312, 62)
SCREEN_IN = 3                           # frame thickness
DAIS = (106, 60, 214, WALL_BOTTOM)      # the green marble wall behind the rostrum
LEDGE_Y = 66                            # the President's desk ledge on the dais
PRESIDENT = (160, 66)                   # where the President of the Assembly sits (bottom centre of his bust)
ROSTRUM = (140, 130, 180, 170)          # the speaker's rostrum
ROSTRUM_TOP = 130
PODIUM_SPOT = (160, 166)                # the rapper's feet (hidden behind the rostrum)
CHART = (22, 70, 112, 128)              # the flip chart's paper
CHART_W, CHART_H = CHART[2] - CHART[0], CHART[3] - CHART[1]
DESK = (212, 142, 320, 180)             # the delegation desk (top surface at y 142)
DESK_TOP = 142
DESK_SPOT = (270, 190)                  # the heckler's feet (well below the desk)
PLACARD = (270, 141)                    # bottom centre of the country placard on the desk
FRONT_ROW_Y = 166                       # the delegates' heads in the front rows


# --- the wall ---------------------------------------------------------------------------------

def wall(img):
    vgrad(img, (0, 0, W, WALL_BOTTOM), C["wall_hi"], C["wall"], steps=6, soft=0.5)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 12):                                   # gold-leaf panels
        d.line([(x, 0), (x, WALL_BOTTOM)], fill=C["wall_sh"])
        d.line([(x + 1, 0), (x + 1, WALL_BOTTOM)], fill=C["wall_hi"])
    for y in range(0, WALL_BOTTOM, 24):
        dither(img, mask(lambda dd, y=y: dd.rectangle((0, y + 20, W, y + 23), fill=255)) * 0.4, C["wall_sh"],
               blend=0.4)
    vgrad(img, (0, WALL_BOTTOM - 10, W, WALL_BOTTOM), C["wall"], C["wall_dk"], steps=3)


def emblem(img, cx, cy, r, fg=None, bg=None):
    """The UN emblem: a polar world map in a wreath of olive branches."""
    fg = col(fg or "gold_hi")
    bg = col(bg or "wall_dk")
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), fill=INK)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    rm = int(r * 0.58)
    d.ellipse((cx - rm, cy - rm, cx + rm, cy + rm), outline=fg)              # the globe
    rh = rm // 2
    d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), outline=fg)              # a parallel
    d.line([(cx - rm, cy), (cx + rm, cy)], fill=fg)                          # meridians
    d.line([(cx, cy - rm), (cx, cy + rm)], fill=fg)
    if r >= 12:
        for a in (45, 135):
            dx, dy = rm * 0.7 * math.cos(math.radians(a)), rm * 0.7 * math.sin(math.radians(a))
            d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=fg)
    # the olive branches round the globe, open at the top
    leaves = 6 if r >= 12 else 4
    for side in (-1, 1):
        for i in range(leaves):
            a = math.radians(90 + side * (35 + i * 140 / leaves))
            px, py = cx + (r - 3) * math.cos(a), cy + (r - 3) * math.sin(a)
            d.point((round(px), round(py)), fill=fg)
            d.point((round(px + side * 0.0), round(py - 1)), fill=fg)


def screen_frame(img, box):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK)
    d.rectangle((x0, y0, x1, y1), fill=C["black"])
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), outline=(60, 60, 72))
    d.rectangle((x0 + SCREEN_IN, y0 + SCREEN_IN, x1 - SCREEN_IN, y1 - SCREEN_IN), fill=C["screen"])


def screen_inner(box):
    x0, y0, x1, y1 = box
    return (x0 + SCREEN_IN, y0 + SCREEN_IN, x1 - SCREEN_IN + 1, y1 - SCREEN_IN + 1)


def marble(img, box, seed=0):
    """Green marble: flat base, dithered cloud, a few pale veins."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=C["marble"])
    m = mask(lambda dd: dd.rectangle(box, fill=255), img.size)
    import numpy as np
    yy, xx = np.mgrid[0:img.height, 0:img.width]
    cloud = (np.sin(xx * 0.21 + seed) * np.sin(yy * 0.17 + seed * 2) + np.sin((xx + yy) * 0.08 + seed)) * 0.25 + 0.3
    dither(img, m * np.clip(cloud, 0, 1) * 0.6, C["marble_sh"], blend=0.6)
    for i in range(int((x1 - x0) * (y1 - y0) / 500) + 1):
        vx = x0 + rnd("vein", seed, i) * (x1 - x0)
        vy = y0 + rnd("veiny", seed, i) * (y1 - y0)
        pts = [(vx, vy)]
        for k in range(4):
            vx += 3 + rnd("vx", seed, i, k) * 5
            vy += (rnd("vy", seed, i, k) - 0.5) * 6
            pts.append((min(vx, x1), min(max(vy, y0), y1)))
        d.line(pts, fill=C["marble_vein"])


def dais(img):
    x0, y0, x1, y1 = DAIS
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1), fill=INK)
    marble(img, (x0, y0, x1, y1), seed=3)
    # the President's desk ledge, and the three high-backed chairs behind it
    for cx in (130, 160, 190):
        d.rectangle((cx - 7, y0 - 14, cx + 7, y0), fill=INK)
        d.rectangle((cx - 6, y0 - 13, cx + 6, y0), fill=C["chair_sh"])
        d.rectangle((cx - 5, y0 - 12, cx + 5, y0 - 1), fill=C["chair"])
    d.rectangle((x0 - 4, LEDGE_Y - 3, x1 + 4, LEDGE_Y + 3), fill=INK)
    d.rectangle((x0 - 3, LEDGE_Y - 2, x1 + 3, LEDGE_Y + 2), fill=C["desk"])
    d.line([(x0 - 3, LEDGE_Y - 2), (x1 + 3, LEDGE_Y - 2)], fill=C["desk_hi"])
    d.line([(x0 - 3, LEDGE_Y + 2), (x1 + 3, LEDGE_Y + 2)], fill=C["desk_sh"])
    # gold trim down the sides
    for x in (x0 + 2, x1 - 2):
        d.line([(x, LEDGE_Y + 4), (x, y1)], fill=C["gold_sh"])


def floor(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0, WALL_BOTTOM, W, H), fill=C["carpet"])
    vgrad(img, (0, WALL_BOTTOM, W, H), C["carpet_sh"], C["carpet"], steps=4, soft=0.5)
    for y in range(WALL_BOTTOM + 4, H, 7):                     # the carpet's woven rows
        for x in range((y // 7) % 2 * 4, W, 8):
            d.point((x, y), fill=C["carpet_hi"])
    d.rectangle((0, WALL_BOTTOM, W, WALL_BOTTOM + 1), fill=C["wall_dk"])
    # the raised platform the rostrum stands on
    d.rectangle((118, 160, 202, 172), fill=INK)
    marble(img, (119, 161, 201, 171), seed=7)
    d.line([(119, 161), (201, 161)], fill=C["marble_hi"])


@lru_cache(maxsize=1)
def backdrop():
    """Everything behind the President and the rapper: wall, emblem, screens (blank), dais, floor."""
    img = Image.new("RGB", (W, H), C["wall"])
    wall(img)
    floor(img)
    emblem(img, *EMBLEM)
    for box in (SCREEN_L, SCREEN_R):
        screen_frame(img, box)
    dais(img)
    # the easel's back legs, behind the chart
    d = ImageDraw.Draw(img)
    d.line([(67, CHART[3]), (67, 168)], fill=INK, width=3)
    d.line([(67, CHART[3]), (67, 168)], fill=C["desk_sh"])
    return img


# --- the rostrum, the easel, the desk ------------------------------------------------------------

@lru_cache(maxsize=1)
def rostrum_sprite():
    x0, y0, x1, y1 = ROSTRUM
    w, h = x1 - x0 + 3, y1 - y0 + 3
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base = Image.new("RGB", (w, h), C["marble"])
    marble(base, (0, 0, w - 1, h - 1), seed=11)
    img.paste(base, (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w - 1, h - 1), outline=INK)
    d.rectangle((1, 1, w - 2, 4), fill=C["desk"])               # the reading slope
    d.line([(1, 1), (w - 2, 1)], fill=C["desk_hi"])
    d.line([(1, 5), (w - 2, 5)], fill=INK)
    d.line([(2, 6), (2, h - 2)], fill=C["marble_hi"])
    d.line([(w - 3, 6), (w - 3, h - 2)], fill=C["marble_sh"])
    plaque = Image.new("RGB", (w, h), (0, 0, 0))
    emblem(plaque, w // 2, 18, 8, fg="gold_hi", bg="gold_sh")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((w // 2 - 9, 9, w // 2 + 9, 27), fill=255)
    img.paste(plaque, (0, 0), m)
    return img


def rostrum(img, mics=True):
    spr = rostrum_sprite()
    x0, y0 = ROSTRUM[0] - 1, ROSTRUM[1] - 1
    img.paste(spr, (x0, y0), spr)
    if mics:
        d = ImageDraw.Draw(img)
        for mx, lean in ((154, -1), (166, 1)):                  # two goosenecks
            pts = [(mx, ROSTRUM_TOP), (mx + lean, ROSTRUM_TOP - 7), (mx + lean * 3, ROSTRUM_TOP - 12)]
            d.line(pts, fill=INK, width=3)
            d.line(pts, fill=C["steel_sh"])
            tip = pts[-1]
            d.rectangle((tip[0] - 1, tip[1] - 3, tip[0] + 1, tip[1]), fill=INK)
            d.point((tip[0], tip[1] - 2), fill=C["steel"])


def easel_front(img):
    """The front legs and the clip bar of the flip chart, drawn over its paper."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = CHART
    for (a, b) in (((x0 + 10, y1), (x0 + 2, 170)), ((x1 - 10, y1), (x1 - 2, 170))):
        d.line([a, b], fill=INK, width=4)
        d.line([a, b], fill=C["desk"], width=2)
    d.rectangle((x0 - 3, y0 - 4, x1 + 3, y0), fill=INK)
    d.rectangle((x0 - 2, y0 - 3, x1 + 2, y0 - 1), fill=C["steel_sh"])
    d.line([(x0 - 2, y0 - 3), (x1 + 2, y0 - 3)], fill=C["steel"])
    d.rectangle((x0 - 2, y1, x1 + 2, y1 + 3), fill=INK)        # the tray
    d.rectangle((x0 - 1, y1 + 1, x1 + 1, y1 + 2), fill=C["desk_sh"])
    for i, c in enumerate(("mk_black", "mk_red", "mk_blue")):  # spare markers in the tray
        d.rectangle((x1 - 22 + i * 6, y1, x1 - 18 + i * 6, y1 + 1), fill=C[c])


@lru_cache(maxsize=4)
def placard_sprite(country):
    w = pixel.text_width(country, SILK) + 8
    s = Canvas(w, 11)
    s.rect((0, 0, w - 1, 8), "white")
    s.rect((0, 8, w - 1, 9), "paper_sh")
    s.text((4, 0), country, "ink")
    return s.done()


def desk(img, country=None):
    x0, y0, x1, y1 = DESK
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=INK)
    d.rectangle((x0, y0, x1, y0 + 4), fill=C["desk"])
    d.line([(x0, y0), (x1, y0)], fill=C["desk_hi"])
    d.rectangle((x0, y0 + 5, x1, y1), fill=C["desk_sh"])
    d.line([(x0, y0 + 5), (x1, y0 + 5)], fill=INK)
    for x in range(x0 + 14, x1, 26):                           # front panels
        d.line([(x, y0 + 8), (x, y1)], fill=mix(C["desk_sh"], INK, 0.3))
    d.rectangle((x0 + 2, y0 - 2, x0 + 20, y0), fill=C["black"])     # a microphone base and a laptop
    d.line([(x0 + 10, y0 - 2), (x0 + 16, y0 - 10)], fill=INK, width=2)
    d.rectangle((x1 - 34, y0 - 7, x1 - 18, y0), fill=INK)
    d.rectangle((x1 - 33, y0 - 6, x1 - 19, y0 - 1), fill=C["steel_sh"])
    if country:
        spr = placard_sprite(country)
        img.paste(spr, (PLACARD[0] - spr.width // 2, PLACARD[1] - spr.height), spr)


# --- the President of the Assembly ---------------------------------------------------------------

@lru_cache(maxsize=16)
def president_sprite(arm="down", mouth="closed"):
    """The President of the General Assembly, seen from the chest up behind the ledge: grey hair, glasses,
    gavel."""
    skin, skin_sh, hair = (214, 160, 124), (180, 126, 96), (176, 176, 186)
    s = Canvas(24, 22)
    s.poly([(4, 12), (18, 12), (20, 21), (2, 21)], (70, 74, 86))      # jacket
    s.poly([(9, 12), (13, 12), (11, 17)], "white")
    s.line([(11, 13), (11, 17)], (40, 90, 160))
    s.ell((5, 1, 17, 13), skin)                                        # head
    s.rect((5, 6, 6, 10), skin_sh)
    s.ell((5, 0, 17, 5), hair)                                         # grey hair
    s.rect((5, 2, 6, 7), hair); s.rect((16, 2, 17, 6), hair)
    s.line([(8, 7), (10, 7)], INK); s.line([(12, 7), (14, 7)], INK)    # glasses
    s.px((11, 7), INK); s.px((9, 8), "eye"); s.px((13, 8), "eye")
    if mouth == "open":
        s.rect((10, 10, 12, 11), "mouth")
    else:
        s.line([(10, 10), (12, 10)], "mouth")
    if arm == "up":                                                    # gavel raised
        s.line([(18, 14), (21, 6)], (70, 74, 86), 2)
        s.rect((20, 4, 22, 6), skin)
        s.line([(21, 4), (21, 0)], "desk_sh")
        s.rect((19, 0, 23, 2), "desk")
    else:                                                              # gavel down on the block
        s.line([(17, 14), (21, 19)], (70, 74, 86), 2)
        s.rect((20, 18, 22, 20), skin)
        s.line([(22, 19), (23, 15)], "desk_sh")
        s.rect((21, 13, 23, 16), "desk")
    return s.done()


def president(img, arm="down", mouth="closed"):
    spr = president_sprite(arm, mouth)
    x, y = PRESIDENT
    img.paste(spr, (x - spr.width // 2, y - spr.height + 1), spr)


def ledge_front(img):
    """The front lip of the dais ledge, over the President's lap."""
    x0, _, x1, _ = DAIS
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 4, LEDGE_Y - 1, x1 + 4, LEDGE_Y + 3), fill=INK)
    d.rectangle((x0 - 3, LEDGE_Y, x1 + 3, LEDGE_Y + 2), fill=C["desk"])
    d.line([(x0 - 3, LEDGE_Y + 2), (x1 + 3, LEDGE_Y + 2)], fill=C["desk_sh"])


# --- the delegates in the front rows ------------------------------------------------------------------

DELEGATE_TONES = [(52, 44, 60), (60, 50, 66), (46, 40, 56), (66, 56, 70)]
DELEGATES = [(x, FRONT_ROW_Y + (4 if i % 2 else 0) + int(rnd("dy", i) * 3), i)
             for i, x in enumerate(range(6, 206, 15))]


def delegate(d, x, y, i, stand=0.0, gone=False, react=0.0, t=0.0):
    """One delegate seen from behind: head and shoulders over a chair back. `stand` lifts them up,
    `react` throws their hands up."""
    if gone:
        d.rectangle((x - 7, y + 4, x + 7, H), fill=INK)
        d.rectangle((x - 6, y + 5, x + 6, H), fill=C["chair_sh"])
        return
    tone = DELEGATE_TONES[i % len(DELEGATE_TONES)]
    rim = mix(tone, (140, 120, 90), 0.5)
    y = y - int(round(stand * 10))
    d.ellipse((x - 9, y + 7, x + 9, y + 24), fill=INK)
    d.ellipse((x - 8, y + 8, x + 8, y + 24), fill=tone)
    d.ellipse((x - 5, y - 1, x + 5, y + 10), fill=INK)
    d.ellipse((x - 4, y, x + 4, y + 9), fill=mix(tone, (20, 16, 22), 0.4))
    d.arc((x - 4, y, x + 4, y + 9), 200, 330, fill=rim)
    if react > 0:
        lift = int(round(react * 9))
        for side in (-1, 1):
            hx = x + side * (9 + int(react * 2))
            d.line([(x + side * 6, y + 12), (hx, y + 8 - lift)], fill=INK, width=3)
            d.line([(x + side * 6, y + 12), (hx, y + 8 - lift)], fill=tone)
            d.ellipse((hx - 2, y + 6 - lift, hx + 2, y + 10 - lift), fill=INK)
            d.point((hx, y + 8 - lift), fill=rim)


def delegates(img, t, stand=None, gone=(), react=None):
    """The front rows. `stand` and `react` map a delegate index to an amount (0-1); `gone` empties seats."""
    d = ImageDraw.Draw(img)
    for x, y, i in DELEGATES:
        delegate(d, x, y, i, stand=(stand or {}).get(i, 0.0), gone=i in gone, react=(react or {}).get(i, 0.0), t=t)


if __name__ == "__main__":
    from engine import ROOT
    img = backdrop().copy()
    president(img)
    ledge_front(img)
    rostrum(img)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = CHART
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=C["paper"])
    easel_front(img)
    desk(img, "ISRAEL")
    delegates(img, 0.0)
    out = ROOT / "build" / "hall.png"
    img.resize((W * 4, H * 4), Image.NEAREST).save(out)
    print(out)
