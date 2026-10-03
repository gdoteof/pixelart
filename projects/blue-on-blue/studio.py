"""The set of This Is Gavin Newsom: a navy studio wall of acoustic panels with wood slats at the sides,
the show's name in neon between the two hosts, an ON AIR light, a ring light, the bear flag, a portrait
of the host by the host, and the desk with two podcast mics on boom arms.

World layout (320x180):
    the neon sign               NEON = (112, 18, 208, 50); the ON AIR light ONAIR above it
    the host's portrait         PORTRAIT (frame) and PICTURE (what a gag may paint over), top right
    the ring light              RING, centre and radius, on the left; the bear flag FLAG above it
    the hosts                   figure canvases at SEAT_L (Newsom, facing right) / SEAT_R (Mamdani, facing left)
    the desk                    far edge DESK_Y = 120, front edge 128; the lower third hides it below y 142
    the mics                    MIC[who] = (clamp, elbow, back of the mic, tip)
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from characters import head
from engine import C, INK, PRESS, SILK, H, W, Canvas, blend, dither_rect, mask, mirror, rnd, vgrad
from pixelart import pixel

SEAT_L, SEAT_R = (40, 44), (196, 44)
DESK_Y, DESK_FRONT = 120, 128
NEON = (112, 18, 208, 50)
ONAIR = (142, 5, 178, 13)
PORTRAIT = (268, 14, 306, 60)
PICTURE = (271, 17, 303, 57)
RING = (24, 60, 14)
FLAG = (6, 10, 46, 34)
PLANT = (288, 76, 318, 120)
LAPTOP = (120, 99, 146, 120)
PHONE = (184, 121, 198, 125)                        # Mamdani's phone, flat on the desk
MIC = {"newsom": ((118, 120), (114, 101), (106, 94), (95, 87)),
       "mamdani": ((202, 120), (206, 101), (214, 94), (225, 87))}
MUG = {"newsom": (30, 109), "mamdani": (280, 109)}


@lru_cache(maxsize=None)
def glow_mask(which):
    """The soft light around the ring light, the ON AIR box and the neon sign."""
    cx, cy, r = RING
    x0, y0, x1, y1 = NEON
    a0, b0, a1, b1 = ONAIR
    return {"ring": lambda: mask(lambda m: m.ellipse((cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5), fill=255)),
            "neon": lambda: mask(lambda m: m.rounded_rectangle((x0 - 6, y0 - 4, x1 + 6, y1 + 4), 6, fill=255)),
            "onair": lambda: mask(lambda m: m.rectangle((a0 - 4, b0 - 3, a1 + 4, b1 + 3), fill=255))}[which]()


def _box(d, box, col):
    d.rectangle(box, fill=C[col] if isinstance(col, str) else col)


def frame(d, box):
    """A gilded frame: gold with a highlight on top and a bevel inside."""
    x0, y0, x1, y1 = box
    _box(d, (x0 - 1, y0 - 1, x1 + 1, y1 + 1), "ink")
    _box(d, box, "gold")
    d.line([(x0, y0), (x1, y0)], fill=C["gold_hi"]); d.line([(x0, y0), (x0, y1)], fill=C["gold_hi"])
    d.line([(x0, y1), (x1, y1)], fill=C["gold_sh"]); d.line([(x1, y0), (x1, y1)], fill=C["gold_sh"])


def wall(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W, DESK_Y), "wall_hi", "wall", steps=6)
    for x in range(64, 256, 16):                                          # acoustic panels in a grid
        for y in range(4, DESK_Y, 16):
            _box(d, (x + 1, y + 1, x + 14, y + 14), "foam")
            d.line([(x + 1, y + 1), (x + 14, y + 1)], fill=C["foam_hi"])
            d.line([(x + 14, y + 2), (x + 14, y + 14)], fill=C["foam_sh"]); d.line([(x + 1, y + 14), (x + 14, y + 14)], fill=C["foam_sh"])
            for k in range(3):                                           # the wedges
                d.line([(x + 3 + 4 * k, y + 4), (x + 3 + 4 * k, y + 11)], fill=C["foam_sh"])
    for x0, x1 in ((0, 62), (258, W)):                                    # wood slats at the sides
        _box(d, (x0, 0, x1, DESK_Y), "slat_dk")
        for x in range(x0 + 1, x1, 5):
            _box(d, (x, 0, x + 3, DESK_Y), "slat")
            d.line([(x, 0), (x, DESK_Y)], fill=C["slat_hi"]); d.line([(x + 3, 0), (x + 3, DESK_Y)], fill=C["slat_sh"])
    dither_rect(img, (0, 0, W, 30), C["wall_dk"], density=0.35, blend=0.5)    # the light falls off at the top
    # a strip of blue LED along the ceiling
    d.line([(0, 0), (W, 0)], fill=C["neon_glow"])


def bear_flag(d, box):
    """The California Republic flag, on the slats."""
    x0, y0, x1, y1 = box
    _box(d, (x0 - 1, y0 - 1, x1 + 1, y1 + 1), "ink")
    _box(d, box, "flag")
    _box(d, (x0, y1 - 4, x1, y1), "flag_red")
    d.polygon([(x0 + 2, y0 + 2), (x0 + 6, y0 + 2), (x0 + 4, y0 + 6)], fill=C["flag_red"])    # the star, roughly
    cx, cy = (x0 + x1) // 2 + 2, y0 + 12                                 # the bear, walking left
    _box(d, (cx - 9, cy - 2, cx + 6, cy + 4), "bear")
    d.ellipse((cx - 13, cy - 4, cx - 6, cy + 2), fill=C["bear"])
    d.point((cx - 13, cy - 1), fill=C["ink"])
    for lx in (cx - 8, cx - 4, cx + 1, cx + 5):
        d.line([(lx, cy + 4), (lx, cy + 7)], fill=C["bear_sh"])
    d.line([(x0 + 4, cy + 8), (x1 - 4, cy + 8)], fill=C["grass"])


def ring_light(img, on=1.0):
    """The ring light on its stand, lit (on=1), dim (0), or flickering in between."""
    d = ImageDraw.Draw(img)
    cx, cy, r = RING
    d.line([(cx, cy + r), (cx, DESK_Y)], fill=C["stand"], width=2)
    d.line([(cx - 8, DESK_Y), (cx, DESK_Y - 6), (cx + 8, DESK_Y)], fill=C["stand"])
    if on > 0.5:
        blend(img, glow_mask("ring"), "ring_glow", 0.25 * on)
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), outline=C["ink"], width=1)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=C["ring"] if on > 0.5 else C["stand_hi"], width=3)
    d.ellipse((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), outline=C["ink"], width=1)
    d.rectangle((cx - 2, cy + r - 1, cx + 2, cy + r + 2), fill=C["stand"])


def plant(d):
    x0, y0, x1, y1 = PLANT
    cx = (x0 + x1) // 2
    d.polygon([(cx - 9, y1 - 18), (cx + 9, y1 - 18), (cx + 7, y1), (cx - 7, y1)], fill=C["ink"])
    d.polygon([(cx - 8, y1 - 17), (cx + 8, y1 - 17), (cx + 6, y1 - 1), (cx - 6, y1 - 1)], fill=C["pot"])
    d.line([(cx + 5, y1 - 16), (cx + 4, y1 - 2)], fill=C["pot_sh"])
    d.line([(cx, y1 - 18), (cx - 1, y0 + 14)], fill=C["plant_sh"], width=2)
    for k, (lx, ly, s) in enumerate([(-10, 8, 1), (8, 4, -1), (-8, 20, 1), (10, 18, -1), (-4, 0, 1), (6, 30, -1),
                                     (-10, 32, 1)]):
        x, y = cx + lx, y0 + ly
        d.ellipse((x - 6, y - 3, x + 6, y + 4), fill=C["ink"])
        d.ellipse((x - 5, y - 2, x + 5, y + 3), fill=C["plant"] if k % 2 else C["plant_hi"])
        d.line([(x - 4 * s, y), (x + 4 * s, y + 1)], fill=C["plant_sh"])


@lru_cache(maxsize=None)
@lru_cache(maxsize=None)
def portrait_pic(mood="smile", who="newsom"):
    """The host, by the host: Newsom's own portrait, in oils. Or, rehung, the landlord-in-chief."""
    x0, y0, x1, y1 = PICTURE
    w, h = x1 - x0 + 1, y1 - y0 + 1
    trump = who == "trump"
    img = Image.new("RGB", (w, h), (110, 34, 44) if trump else (70, 60, 80))
    d = ImageDraw.Draw(img)
    d.ellipse((-6, -4, w + 6, h + 10), fill=(150, 52, 58) if trump else (96, 86, 110))
    d.polygon([(2, h), (6, h - 9), (w - 6, h - 9), (w - 2, h)], fill=C["suit" if trump else "blazer"])  # the shoulders
    d.polygon([(w // 2 - 3, h - 9), (w // 2 + 3, h - 9), (w // 2, h - 3)], fill=C["shirt"])
    if trump:
        d.line([(w // 2, h - 8), (w // 2, h - 1)], fill=C["tie"])
        hd = head("trump", "squint", "neutral", "pout")
    else:
        hd = head("newsom", "open", "up", mood)
    img.paste(hd, (w // 2 - 22, h - 46), hd)
    return img


def neon_text_img(top, bottom, color, glow):
    """The neon sign's lettering on a transparent canvas: a white core, a coloured halo."""
    w, h = NEON[2] - NEON[0], NEON[3] - NEON[1]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pixel.outline_text(img, (w // 2, 2), top, SILK, color, glow, anchor="ma")
    pixel.outline_text(img, (w // 2, 14), bottom, PRESS, color, glow, anchor="ma")
    return img


@lru_cache(maxsize=None)
def neon_sign(word="IS", lit=True, color=None):
    """THIS IS / GAVIN NEWSOM, in neon on a smoked panel. `word` swaps the IS (for WAS)."""
    w, h = NEON[2] - NEON[0], NEON[3] - NEON[1]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 3, fill=(16, 20, 40, 255), outline=INK + (255,))
    d.rounded_rectangle((1, 1, w - 2, h - 2), 3, outline=(40, 48, 84, 255))
    core = C["neon"] if lit else C["neon_dim"]
    glow = C["neon_glow"] if lit else (34, 40, 66)
    img.alpha_composite(neon_text_img(f"THIS {word}", "GAVIN NEWSOM", core, glow), (0, 3))
    if color:                                                             # just the swapped word, in its own colour
        tw = pixel.text_width(f"THIS {word}", SILK)
        x = w // 2 - tw // 2 + pixel.text_width("THIS ", SILK)
        pixel.outline_text(img, (x, 5), word, SILK, color, (120, 30, 40))
    return img


def onair(img, on=True):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = ONAIR
    if on:
        blend(img, glow_mask("onair"), "onair", 0.25)
    _box(d, (x0 - 1, y0 - 1, x1 + 1, y1 + 1), "ink")
    _box(d, ONAIR, "onair" if on else "onair_off")
    d.text(((x0 + x1) // 2 + 1, y0 - 2), "ON AIR", font=SILK, fill=C["white"] if on else C["onair"], anchor="ma")


@lru_cache(maxsize=1)
def backdrop():
    """The studio behind the hosts (RGB, 320x180): the wall, the flag, the portrait, the plant."""
    img = Image.new("RGB", (W, H), C["wall"])
    wall(img)
    d = ImageDraw.Draw(img)
    bear_flag(d, FLAG)
    frame(d, PORTRAIT)
    pic = portrait_pic()
    img.paste(pic, PICTURE[:2])
    px = (PORTRAIT[0] + PORTRAIT[2]) // 2                                 # the brass plaque
    _box(d, (px - 15, PORTRAIT[3] + 3, px + 15, PORTRAIT[3] + 10), "ink")
    _box(d, (px - 14, PORTRAIT[3] + 4, px + 14, PORTRAIT[3] + 9), "gold_sh")
    d.text((px, PORTRAIT[3] + 1), "THE HOST", font=SILK, fill=C["gold_hi"], anchor="ma")
    plant(d)
    _box(d, (0, DESK_Y - 1, W, H), "desk_dk")                            # the floor behind the desk
    return img


def neon(img, word="IS", lit=True, color=None, flicker=False, f=0):
    """Hang the neon sign; `flicker` drops it out on some frames."""
    if flicker and rnd("flick", f) < 0.45:
        lit = False
    spr = neon_sign(word, lit, color)
    if lit:
        blend(img, glow_mask("neon"), "neon_glow", 0.18)
    img.paste(spr, NEON[:2], spr)


# --- the desk, in front of the hosts ---------------------------------------------------------

@lru_cache(maxsize=1)
def desk_sprite():
    """The desk: a long top in perspective and the front panel with its strip of blue light."""
    img = Image.new("RGBA", (W, H - DESK_Y + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = [(6, 0), (W - 7, 0), (W - 1, DESK_FRONT - DESK_Y), (0, DESK_FRONT - DESK_Y)]
    d.polygon(top, fill=C["desk_top"])
    d.line([(6, 0), (W - 7, 0)], fill=C["ink"])
    for x in range(14, W - 10, 26):                                      # the grain
        d.line([(x, 2), (x + 30, 5)], fill=C["desk"])
    y = DESK_FRONT - DESK_Y
    d.rectangle((0, y, W, y + 2), fill=C["desk_edge"])
    d.line([(0, y + 3), (W, y + 3)], fill=C["ink"])
    d.rectangle((0, y + 4, W, H), fill=C["desk_sh"])
    d.line([(0, y + 5), (W, y + 5)], fill=C["neon_glow"])                # the LED strip
    d.line([(0, y + 6), (W, y + 6)], fill=C["blue_sh"])
    for x in range(0, W, 40):
        d.line([(x, y + 8), (x, H)], fill=C["desk_dk"])
    return img


def draw_desk(img):
    spr = desk_sprite()
    img.paste(spr, (0, DESK_Y), spr)


@lru_cache(maxsize=None)
def laptop_sprite(sticker=True):
    """Newsom's laptop, its lid to the camera, with the bear on it."""
    x0, y0, x1, y1 = LAPTOP
    w, h = x1 - x0 + 1, y1 - y0 + 1
    f = Canvas(w, h)
    f.rect((0, 0, w - 1, h - 2), "laptop")
    f.line([(1, 1), (w - 2, 1)], "white")
    f.line([(w - 2, 2), (w - 2, h - 3)], "laptop_sh")
    f.rect((0, h - 2, w - 1, h - 1), "laptop_sh")
    if sticker:
        f.ell((w // 2 - 5, h // 2 - 4, w // 2 + 5, h // 2 + 3), "flag")
        f.rect((w // 2 - 3, h // 2 - 2, w // 2 + 2, h // 2 + 1), "bear")
    return f.done()


@lru_cache(maxsize=None)
def phone_flat(lit=False):
    """Mamdani's phone, flat on the desk: dark, or lit up with a message."""
    w, h = PHONE[2] - PHONE[0] + 1, PHONE[3] - PHONE[1] + 1
    f = Canvas(w, h)
    f.poly([(2, 0), (w - 1, 0), (w - 3, h - 1), (0, h - 1)], "phone")
    if lit:
        f.poly([(3, 1), (w - 3, 1), (w - 4, h - 2), (2, h - 2)], "screen_hi")
        f.line([(4, 2), (w - 6, 2)], "white")
    return f.done()


@lru_cache(maxsize=None)
def mug(who):
    f = Canvas(10, 11)
    f.rect((0, 1, 7, 10), "mug"); f.ell((5, 3, 9, 8), "mug"); f.d.ellipse((6, 4, 8, 7), fill=(0, 0, 0, 0))
    f.line([(1, 1), (6, 1)], "coffee")
    f.line([(6, 2), (6, 9)], "mug_sh")
    if who == "newsom":
        f.px((3, 5), "flag_red"); f.px((2, 6), "bear")
    else:
        f.pxs([(2, 5), (3, 5), (4, 5)], "blue")
    return f.done()


def draw_mic(img, who, lit=False):
    """A podcast mic on its boom arm: the clamp at the desk's edge, the arm, the elbow, the mic."""
    d = ImageDraw.Draw(img)
    clamp, elbow, back, tip = MIC[who]
    d.line([clamp, elbow], fill=C["ink"], width=3); d.line([elbow, back], fill=C["ink"], width=3)
    d.line([clamp, elbow], fill=C["boom"], width=1); d.line([elbow, back], fill=C["boom"], width=1)
    d.rectangle((clamp[0] - 2, clamp[1] - 2, clamp[0] + 2, clamp[1] + 1), fill=C["boom"], outline=C["ink"])
    dx, dy = tip[0] - back[0], tip[1] - back[1]
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    px, py = -uy * 3.5, ux * 3.5
    body = [(back[0] + px, back[1] + py), (tip[0] + px, tip[1] + py), (tip[0] - px, tip[1] - py), (back[0] - px, back[1] - py)]
    d.polygon(body, fill=C["micbody"], outline=C["ink"])
    gx, gy = tip[0] - ux * 4, tip[1] - uy * 4                            # the windscreen at the business end
    d.ellipse((gx - 4, gy - 4, gx + 4, gy + 4), fill=C["grille"], outline=C["ink"])
    d.line([(gx - 2, gy - 1), (gx + 2, gy - 1)], fill=C["micbody_hi"]); d.line([(gx - 2, gy + 1), (gx + 2, gy + 1)], fill=C["micbody_hi"])
    mx, my = (back[0] + tip[0]) / 2, (back[1] + tip[1]) / 2
    d.line([(mx + px * 0.6, my + py * 0.6), (mx + ux * 3 + px * 0.6, my + uy * 3 + py * 0.6)], fill=C["micbody_hi"])
    if lit:
        d.point((round(back[0] + ux * 2), round(back[1] + uy * 2)), fill=C["onair"])


def desk_items(img, laptop=True, phone_lit=False, phone_dx=0, mugs=True):
    if laptop:
        spr = laptop_sprite()
        img.paste(spr, LAPTOP[:2], spr)
    if mugs:
        for who, (x, y) in MUG.items():
            m = mug(who) if who == "newsom" else mirror(mug(who))
            img.paste(m, (x, y), m)
    p = phone_flat(phone_lit)
    img.paste(p, (PHONE[0] + phone_dx, PHONE[1]), p)


if __name__ == "__main__":
    from engine import ROOT, scaled
    img = backdrop().copy()
    ring_light(img)
    neon(img)
    onair(img)
    draw_desk(img)
    desk_items(img)
    for who in MIC:
        draw_mic(img, who)
    out = ROOT / "build" / "studio.png"
    scaled(img, 4).save(out)
    print(out)
