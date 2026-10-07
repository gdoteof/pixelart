"""Where they stream from: Hasan's bedroom in West Hollywood and Asmongold's house in Austin.

Each room is the whole 320x180 frame, as its owner's webcam sees it. Hasan sits left of centre and turns
to the right, where his overlay goes (the video he's watching, his chat); Asmongold's stream is the mirror
image. So the left half of Hasan's frame and the right half of Asmongold's make one split screen.

    FIG[who]     where his 140x144 figure goes        DESK_Y   the far edge of both desks
    room(who)    the room behind him (RGB)            desk(who)  what stands in front of him (RGBA)
"""
import math
from functools import lru_cache

from PIL import ImageDraw

from engine import C, INK, H, W, Canvas, blend, dither_rect, picture, rnd, vgrad
from pixelart import pixel

DESK_Y = 134
FIG = {"hasan": (32, 20), "asmon": (148, 20)}
FACING = {"hasan": 1, "asmon": -1}
OTHER = {"hasan": "asmon", "asmon": "hasan"}


def glow(img, box, color, alpha=0.2):
    """Soft light on a wall: an ellipse of colour mixed in."""
    blend(img, pixel.mask(lambda m: m.ellipse(box, fill=255), img.size), color, alpha)


def frame(d, box, fill, edge="frame"):
    d.rectangle(box, fill=C[edge], outline=INK)
    x0, y0, x1, y1 = box
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y1 - 2), fill=C[fill])


# --- Hasan's room ---------------------------------------------------------------------------------

def katana(d, x, y, sheath, length=34):
    """A sheathed katana lying on its rack, hilt to the left."""
    d.rectangle((x, y, x + 9, y + 2), fill=C["black"], outline=INK)                  # the hilt
    for i in range(1, 9, 2):
        d.point((x + i, y + 1), fill=C["gold"])
    d.rectangle((x + 10, y - 1, x + 11, y + 3), fill=C["gold"], outline=INK)         # the guard
    d.line([(x + 12, y), (x + length - 4, y), (x + length, y - 1)], fill=INK)        # the sheath, curving up
    d.line([(x + 12, y + 3), (x + length - 4, y + 3), (x + length, y + 2)], fill=INK)
    d.line([(x + 12, y + 1), (x + length - 4, y + 1), (x + length, y)], fill=C[sheath])
    d.line([(x + 12, y + 2), (x + length - 4, y + 2), (x + length, y + 1)], fill=C[sheath + "_sh"])
    d.point((x + length + 1, y), fill=INK)
    d.point((x + 18, y + 1), fill=C["gold"])


def bernie(d, x, y):
    """The cardboard cutout: an old man in a parka and big mittens, arms folded, legs crossed. (x, y) is
    the top of his head."""
    card, parka, sh = C["card"], C["parka"], C["parka_sh"]
    d.polygon([(x + 2, y + 18), (x + 12, y + 14), (x + 24, y + 14), (x + 34, y + 19), (x + 36, y + 44), (x + 30, y + 72),
               (x + 4, y + 72), (x, y + 44)], fill=parka, outline=INK)                # the parka
    d.line([(x + 18, y + 16), (x + 18, y + 44)], fill=sh)
    d.polygon([(x + 30, y + 22), (x + 35, y + 20), (x + 36, y + 44), (x + 31, y + 44)], fill=sh)
    d.rectangle((x + 6, y + 46, x + 30, y + 72), fill=C["grey_sh"], outline=INK)      # the trousers, crossed
    d.line([(x + 8, y + 58), (x + 28, y + 50)], fill=INK)
    d.ellipse((x + 9, y, x + 27, y + 17), fill=C["hskin_hi"], outline=INK)            # the head
    d.rectangle((x + 10, y + 9, x + 26, y + 16), fill=C["blue_hi"], outline=INK)      # the mask
    d.line([(x + 11, y + 6), (x + 25, y + 6)], fill=INK)                              # the glasses
    d.rectangle((x + 12, y + 5, x + 16, y + 8), outline=INK); d.rectangle((x + 20, y + 5, x + 24, y + 8), outline=INK)
    d.line([(x + 9, y + 3), (x + 13, y), (x + 23, y), (x + 27, y + 3)], fill=C["white"])   # what hair there is
    d.point((x + 8, y + 5), fill=C["white"]); d.point((x + 28, y + 5), fill=C["white"])
    for mx in (x + 7, x + 19):                                                         # the mittens
        d.ellipse((mx, y + 34, mx + 11, y + 44), fill=C["mitt"], outline=INK)
        for i in range(2, 10, 3):
            d.point((mx + i, y + 37), fill=C["cream"]); d.point((mx + i + 1, y + 40), fill=C["cream"])
            d.point((mx + i, y + 42), fill=card)
    d.line([(x + 1, y + 73), (x + 35, y + 73)], fill=card)                             # the cardboard's edge
    d.line([(x + 37, y + 20), (x + 37, y + 72)], fill=card)


@lru_cache(maxsize=1)
def hasan_room():
    img, d = picture(W, H, "hwall")
    vgrad(img, (0, 0, W, DESK_Y), "hwall_hi", "hwall", steps=3)
    d = ImageDraw.Draw(img)
    d.rectangle((238, 0, W, DESK_Y), fill=C["hwall_sh"])                               # the alcove with the shelves
    d.line([(238, 0), (238, DESK_Y)], fill=C["grey"])
    # the neon, top left
    glow(img, (-10, -8, 70, 48), "neon", 0.1)
    glow(img, (0, 0, 58, 38), "neon", 0.12)
    d = ImageDraw.Draw(img)
    for pts in ([(10, 26), (10, 10), (20, 10), (20, 26)], [(10, 18), (20, 18)],          # A
                [(26, 26), (26, 10), (34, 10), (36, 13), (34, 18), (26, 18)], [(34, 18), (37, 22), (34, 26), (26, 26)],  # B
                [(43, 10), (43, 26)], [(40, 10), (46, 10)], [(40, 26), (46, 26)]):       # I
        d.line(pts, fill=C["neon"], width=3)
    for pts in ([(10, 26), (10, 10), (20, 10), (20, 26)], [(10, 18), (20, 18)],
                [(26, 26), (26, 10), (34, 10), (36, 13), (34, 18), (26, 18)], [(34, 18), (37, 22), (34, 26), (26, 26)],
                [(43, 10), (43, 26)], [(40, 10), (46, 10)], [(40, 26), (46, 26)]):
        d.line(pts, fill=C["neon_hi"])
    # the prints on the wall: a framed front page, and a big bright one
    frame(d, (126, 12, 152, 48), "paper")
    d.rectangle((129, 15, 149, 18), fill=C["black"])
    d.rectangle((129, 21, 149, 33), fill=C["grey"]); d.rectangle((131, 23, 139, 33), fill=C["grey_sh"])
    d.line([(141, 25), (147, 25)], fill=C["grey_hi"])
    for y in (36, 39, 42, 45):
        d.line([(129, y), (149 - (4 if y == 45 else 0), y)], fill=C["grey"])
    frame(d, (160, 8, 204, 58), "cream", "frame_g")
    d.rectangle((163, 11, 201, 55), fill=C["red"])
    d.ellipse((168, 15, 196, 43), fill=C["gold"]); d.ellipse((174, 21, 190, 37), fill=C["red_sh"])
    d.polygon([(163, 55), (176, 38), (188, 55)], fill=C["blue"]); d.polygon([(182, 55), (192, 44), (201, 55)], fill=C["blue_sh"])
    # the shelves in the alcove, lit from under each one
    d.rectangle((244, 0, W, DESK_Y), fill=C["shelf"])
    for y in (22, 52, 82, 112):
        d.rectangle((244, y, W, y + 3), fill=C["shelf_hi"])
        d.line([(246, y + 4), (W, y + 4)], fill=C["ledw"])
    for y in (22, 52, 82, 112):
        dither_rect(img, (246, y + 5, W, y + 11), C["ledw"], density=0.35, blend=0.4)
    d = ImageDraw.Draw(img)
    d.rectangle((252, 36, 264, 51), fill=C["red"], outline=INK); d.point((255, 39), fill=C["gold"])        # a flag
    d.ellipse((276, 38, 289, 51), fill=C["orange"], outline=INK); d.line([(276, 44), (289, 44)], fill=INK)   # a basketball
    d.rectangle((298, 34, 312, 51), fill=C["stone"], outline=INK)                                          # a bust
    d.rectangle((250, 72, 268, 81), fill=C["white"], outline=INK); d.rectangle((250, 79, 272, 81), fill=C["black"])   # a cap
    d.rectangle((282, 66, 296, 81), fill=C["gold_sh"], outline=INK)
    d.rectangle((252, 98, 262, 111), fill=C["blue"], outline=INK); d.rectangle((264, 94, 272, 111), fill=C["red_sh"], outline=INK)
    d.rectangle((274, 100, 284, 111), fill=C["green_sh"], outline=INK)
    # the bed, down the left wall
    d.rectangle((0, 110, 58, DESK_Y), fill=C["bed"], outline=INK)
    for x in range(4, 58, 8):
        d.rectangle((x, 111, x + 2, DESK_Y), fill=C["bed_st"])
    d.rectangle((0, 100, 24, 112), fill=C["white"], outline=INK)                        # the pillow
    d.line([(3, 109), (20, 109)], fill=C["bed_sh"])
    d.line([(0, 110), (58, 110)], fill=INK)
    # the swords on their rack, and the cutout
    d.rectangle((140, 112, 188, DESK_Y), fill=C["wood"], outline=INK)                   # the console
    d.line([(141, 113), (187, 113)], fill=C["wood_hi"]); d.line([(164, 116), (164, DESK_Y)], fill=C["wood_sh"])
    for x in (145, 180):                                                               # the rack's posts
        d.rectangle((x, 80, x + 2, 112), fill=C["black"], outline=INK)
    d.rectangle((142, 110, 186, 112), fill=C["black"])
    katana(d, 144, 84, "red")
    katana(d, 144, 93, "grey")
    katana(d, 144, 102, "red")
    bernie(d, 194, 76)
    return img


@lru_cache(maxsize=1)
def hasan_desk():
    f = Canvas(W, H)
    f.rect((0, DESK_Y, W, H), "hdesk")
    f.line([(0, DESK_Y), (W, DESK_Y)], "hdesk_hi")
    f.rect((0, DESK_Y + 20, W, H), "hdesk_sh")
    f.rect((112, DESK_Y + 6, 170, DESK_Y + 14), "black")                               # the keyboard, lit
    for i, x in enumerate(range(114, 169, 3)):
        f.px((x, DESK_Y + 8), ("hasan", "hasan_hi", "neon", "pink")[i % 4])
        f.px((x + 1, DESK_Y + 11), ("neon", "hasan", "pink", "hasan_hi")[i % 4])
    f.ell((178, DESK_Y + 7, 186, DESK_Y + 14), "black"); f.px((182, DESK_Y + 8), "hasan")   # the mouse
    f.poly([(194, DESK_Y - 12), (204, DESK_Y - 12), (203, DESK_Y + 4), (195, DESK_Y + 4)], "brown_sh")   # the cold brew
    f.rect((193, DESK_Y - 14, 205, DESK_Y - 12), "white"); f.line([(200, DESK_Y - 22), (199, DESK_Y - 13)], "green")
    f.pxs([(196, DESK_Y - 8), (201, DESK_Y - 4), (197, DESK_Y - 1)], "brown_hi")
    f.rect((16, DESK_Y + 6, 28, DESK_Y + 10), "white"); f.ell((18, DESK_Y + 4, 26, DESK_Y + 8), "blue_hi")     # a tin
    # the mic on its arm, from the left
    f.line([(0, DESK_Y + 4), (20, DESK_Y - 22)], "black", w=3)
    f.rect((18, DESK_Y - 30, 42, DESK_Y - 20), "black")
    f.rect((38, DESK_Y - 31, 46, DESK_Y - 19), "grey_sh")
    f.line([(40, DESK_Y - 29), (40, DESK_Y - 21)], "grey"); f.line([(43, DESK_Y - 29), (43, DESK_Y - 21)], "grey")
    f.line([(20, DESK_Y - 28), (36, DESK_Y - 28)], "hdesk_hi")
    return f.done()


# --- Asmongold's room -------------------------------------------------------------------------------

def bag(d, x, y, w=22, h=18):
    """A full bin bag, knotted at the top. (x, y) is its bottom left."""
    d.polygon([(x, y), (x + 1, y - h + 6), (x + w // 2 - 3, y - h + 1), (x + w // 2, y - h - 2), (x + w // 2 + 3, y - h + 1),
               (x + w - 1, y - h + 6), (x + w, y)], fill=C["bag"], outline=INK)
    d.line([(x + 4, y - h + 7), (x + 7, y - 4)], fill=C["bag_hi"])
    d.line([(x + w - 6, y - h + 8), (x + w - 8, y - 6)], fill=C["bag_hi"])
    d.point((x + w // 2, y - h), fill=C["bag_hi"])


def can(d, x, y, tipped=False):
    """A can of the usual. (x, y) is its bottom left."""
    if tipped:
        d.rectangle((x, y - 4, x + 8, y), fill=C["can"], outline=INK)
        d.line([(x + 1, y - 3), (x + 6, y - 3)], fill=C["can_hi"]); d.line([(x + 8, y - 3), (x + 8, y - 1)], fill=C["steel"])
    else:
        d.rectangle((x, y - 9, x + 5, y), fill=C["can"], outline=INK)
        d.line([(x + 1, y - 8), (x + 1, y - 2)], fill=C["can_hi"]); d.line([(x + 1, y - 9), (x + 4, y - 9)], fill=C["steel"])
        d.point((x + 3, y - 5), fill=C["white"])


def rat(d, x, y):
    """The rat on the windowsill, some days dead: on its back, feet up, tail over the edge."""
    d.ellipse((x, y - 7, x + 16, y), fill=C["rat"], outline=INK)
    d.ellipse((x + 12, y - 8, x + 21, y - 1), fill=C["rat"], outline=INK)               # the head
    d.line([(x + 4, y - 5), (x + 11, y - 5)], fill=C["rat_sh"])
    for fx in (x + 3, x + 7, x + 11):
        d.line([(fx, y - 7), (fx, y - 10)], fill=C["rat_pink"])
    d.line([(x + 16, y - 6), (x + 18, y - 4)], fill=INK); d.line([(x + 18, y - 6), (x + 16, y - 4)], fill=INK)   # x for an eye
    d.point((x + 21, y - 4), fill=C["rat_pink"])
    d.line([(x, y - 3), (x - 4, y - 1), (x - 5, y + 5), (x - 3, y + 9)], fill=C["rat_pink"])   # the tail


@lru_cache(maxsize=1)
def asmon_room():
    img, d = picture(W, H, "awall")
    vgrad(img, (0, 0, W, DESK_Y), "awall_sh", "awall", steps=4)
    glow(img, (84, 0, 228, 122), "awall_hi", 0.22)                                      # the one lamp
    glow(img, (104, 18, 208, 102), "awall_hi", 0.3)
    d = ImageDraw.Draw(img)
    for x, y, r in ((118, 100, 9), (190, 112, 7), (286, 70, 10), (300, 84, 6), (112, 62, 5), (268, 40, 6)):   # damp
        d.ellipse((x - r, y - r // 2, x + r, y + r // 2), fill=C["stain"])
    d.line([(280, 30), (284, 44), (281, 52), (286, 66)], fill=C["grime"])               # a crack
    # the low ceiling, sloping down to the left
    d.polygon([(0, 0), (W, 0), (W, 12), (0, 50)], fill=C["aceil"])
    d.line([(0, 50), (W, 12)], fill=INK)
    for k in (0.25, 0.5, 0.75):
        d.line([(0, 50 * k), (W, 12 * k)], fill=C["aceil_hi"])
    # the window, its blind half down, and what lies on the sill
    d.rectangle((126, 44, 176, 96), fill=C["wood_sh"], outline=INK)
    d.rectangle((129, 47, 173, 92), fill=C["night"])
    d.rectangle((150, 47, 151, 92), fill=C["wood_sh"])
    d.point((160, 80), fill=C["night_hi"]); d.point((166, 72), fill=C["white"]); d.point((137, 84), fill=C["night_hi"])
    for i, y in enumerate(range(48, 70, 3)):                                           # the slats
        d.line([(129, y), (173, y + (i if i > 3 else 0))], fill=C["blind"])
        d.line([(129, y + 1), (173, y + 1 + (i if i > 3 else 0))], fill=C["blind_sh"])
    d.line([(168, 47), (171, 78)], fill=C["blind_sh"])                                  # a slat hanging loose
    d.rectangle((122, 96, 180, 99), fill=C["wood"], outline=INK)                        # the sill
    rat(d, 140, 95)
    # the wall where he wipes his gums
    for x, y0, y1 in ((186, 58, 82), (189, 54, 96), (192, 60, 88), (195, 64, 76)):
        d.line([(x, y0), (x, y1)], fill=C["blood"])
    d.line([(190, 62), (190, 90)], fill=C["blood_sh"]); d.ellipse((185, 52, 196, 60), fill=C["blood"])
    d.point((189, 98), fill=C["blood"]); d.point((193, 92), fill=C["blood_sh"])
    # a cobweb, top right
    for pts in ([(W, 14), (296, 30)], [(W, 26), (300, 22)], [(W, 38), (304, 18)], [(306, 17), (302, 26), (308, 32), (W, 34)]):
        d.line(pts, fill=C["grey"])
    # the heap by the window: bags, boxes, cans
    d.rectangle((108, 118, 142, 124), fill=C["box"], outline=INK); d.rectangle((110, 124, 146, 130), fill=C["box"], outline=INK)
    d.line([(109, 121), (141, 121)], fill=C["box_sh"]); d.ellipse((120, 125, 128, 129), fill=C["red"])
    bag(d, 144, DESK_Y, 26, 24); bag(d, 166, DESK_Y, 22, 16); bag(d, 116, 118, 20, 16)
    can(d, 186, DESK_Y, True); can(d, 104, 118); can(d, 196, DESK_Y - 1)
    # the bed, to the right: a bare mattress, a grey blanket, and a shape under it
    d.rectangle((262, 112, W, DESK_Y), fill=C["blind"], outline=INK)                    # the mattress
    for x in range(266, W, 7):
        d.line([(x, 114), (x, DESK_Y)], fill=C["blind_sh"])
    d.rectangle((264, 102, 284, 113), fill=C["cream"], outline=INK)                     # the pillow
    d.ellipse((268, 105, 276, 110), fill=C["stain"])
    d.polygon([(284, 113), (290, 100), (304, 96), (W, 100), (W, 124), (286, 124)], fill=C["grey_sh"], outline=INK)
    d.line([(292, 103), (303, 99), (314, 102)], fill=C["grey"])
    d.line([(288, 118), (W, 118)], fill=C["grey"])
    return img


@lru_cache(maxsize=1)
def asmon_desk():
    f = Canvas(W, H)
    f.rect((0, DESK_Y, W, H), "adesk")
    f.line([(0, DESK_Y), (W, DESK_Y)], "adesk_hi")
    f.rect((0, DESK_Y + 20, W, H), "adesk_sh")
    f.rect((150, DESK_Y + 6, 204, DESK_Y + 14), "black")                                # the keyboard
    for x in range(152, 203, 3):
        f.px((x, DESK_Y + 8), "grey_sh"); f.px((x + 1, DESK_Y + 11), "grey_sh")
    for x, y in ((120, DESK_Y + 12), (128, DESK_Y + 15), (112, DESK_Y + 16)):           # the cans
        f.rect((x, y - 10, x + 5, y), "can"); f.line([(x + 1, y - 9), (x + 1, y - 2)], "can_hi")
        f.line([(x + 1, y - 10), (x + 4, y - 10)], "steel")
    f.rect((134, DESK_Y + 12, 143, DESK_Y + 16), "can"); f.line([(135, DESK_Y + 13), (141, DESK_Y + 13)], "can_hi")
    f.poly([(214, DESK_Y + 8), (232, DESK_Y + 5), (236, DESK_Y + 11), (218, DESK_Y + 15)], "steel")   # a burrito, in foil
    f.line([(216, DESK_Y + 9), (232, DESK_Y + 7)], "steel_hi"); f.poly([(232, DESK_Y + 5), (238, DESK_Y + 6), (236, DESK_Y + 11)], "box")
    f.pxs([(244, DESK_Y + 12), (248, DESK_Y + 9), (208, DESK_Y + 16), (196, DESK_Y + 17), (252, DESK_Y + 15)], "box")   # crumbs
    # the mic on its arm, from the right, in its foam
    f.line([(W, DESK_Y + 4), (300, DESK_Y - 22)], "black", w=3)
    f.rect((280, DESK_Y - 30, 302, DESK_Y - 20), "black")
    f.ell((268, DESK_Y - 33, 286, DESK_Y - 17), "tee_sh")
    f.pxs([(272, DESK_Y - 28), (276, DESK_Y - 24), (280, DESK_Y - 29), (274, DESK_Y - 21), (279, DESK_Y - 20)], "tee_hi")
    return f.done()


ROOM = {"hasan": hasan_room, "asmon": asmon_room}
DESK = {"hasan": hasan_desk, "asmon": asmon_desk}


# --- what moves ---------------------------------------------------------------------------------------

def roach(img, x, y, t, seed=0, facing=1):
    """A cockroach, legs going."""
    d = ImageDraw.Draw(img)
    x, y = int(round(x)), int(round(y))
    d.ellipse((x - 3, y - 1, x + 3, y + 1), fill=C["roach"], outline=C["roach_sh"])
    d.point((x + 3 * facing, y), fill=C["roach_sh"])
    step = int(t * 12 + seed) % 2
    for i, lx in enumerate((-2, 0, 2)):
        d.point((x + lx, y - 2 - ((i + step) % 2)), fill=C["roach_sh"])
        d.point((x + lx, y + 2 + ((i + step + 1) % 2)), fill=C["roach_sh"])
    d.line([(x + 4 * facing, y - 1), (x + 6 * facing, y - 2 - step)], fill=C["roach_sh"])   # the feelers
    d.line([(x + 4 * facing, y + 1), (x + 6 * facing, y + 2 + step)], fill=C["roach_sh"])


def roaches(img, t, n=5):
    """The residents of Asmongold's wall, going about their evening: each scuttles a stretch, then waits."""
    for i in range(n):
        x0, y0 = 112 + rnd("rx", i) * 84, 58 + rnd("ry", i) * 62
        if 122 <= x0 <= 180 and 40 <= y0 <= 100:                                        # not across the window
            y0 = 104 + rnd("ry2", i) * 12
        span, per = 14 + rnd("rs", i) * 30, 5.0 + rnd("rp", i) * 5
        ph = (t / per + rnd("ro", i)) % 1.0
        k = min(1.0, ph / 0.35) if ph < 0.5 else 1.0 - min(1.0, (ph - 0.5) / 0.35)      # out, wait, back, wait
        moving = ph < 0.35 or 0.5 <= ph < 0.85
        roach(img, x0 + span * k, y0, t if moving else 0, i, 1 if ph < 0.5 else -1)


def flies(img, x, y, t, n=3, seed=0):
    """Flies circling a point."""
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = t * (3.1 + i) + i * 2.1 + seed
        d.point((int(x + 7 * math.cos(a) + 3 * math.sin(a * 2.3)), int(y + 4 * math.sin(a * 1.3))), fill=INK)


def neon_flicker(img, t):
    """Hasan's neon dips for a frame now and then."""
    if rnd("neon", int(t * 6)) < 0.04:
        blend(img, pixel.mask(lambda m: m.rectangle((4, 4, 52, 32), fill=255), img.size), "hwall", 0.45)


if __name__ == "__main__":
    from PIL import Image

    from characters import figure
    from engine import ROOT, scaled
    sheet = Image.new("RGB", (W, 2 * H + 4), (0, 0, 0))
    for i, (who, arms, mouth) in enumerate((("hasan", "point", "grin"), ("asmon", "shrug", "open"))):
        img = ROOM[who]().copy()
        if who == "asmon":
            roaches(img, 3.0)
            flies(img, 150, 84, 3.0)
        spr, _ = figure(who, arms, facing=FACING[who], mouth=mouth, lean=2)
        img.paste(spr, FIG[who], spr)
        img.paste(DESK[who](), (0, 0), DESK[who]())
        sheet.paste(img, (0, i * (H + 4)))
    out = ROOT / "build" / "rooms.png"
    out.parent.mkdir(exist_ok=True)
    scaled(sheet, 4).save(out)
    print(out)
