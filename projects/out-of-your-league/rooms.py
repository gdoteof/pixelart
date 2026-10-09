"""Where they are: Emiru's room, Maya's set at the sanctuary, the sanctuary's gate, and its gift shop.

Each is the whole 320x180 frame. On her own stream Emiru sits left of centre and turns to the right, where
her overlay goes; Maya's stream is the mirror image. At the gate and in the shop the two share the frame,
one at each side, with the window between them.

    FIG[who]     where her 140x144 figure goes on her own stream      PAIR[who]   and in a shared frame
    DESK_Y       the far edge of every desk, the fence's top rail and the shop's counter
    BACK[place]() the place behind them (RGB)                         FRONT[place]() what stands in front (RGBA)
    alive(img, place, t)  what moves there: the cow, the hawk, the emu
"""
import math
from functools import lru_cache

from PIL import ImageDraw

import animals
from engine import C, INK, H, W, Canvas, blend, dither_rect, mirror, picture, rnd, silk, vgrad
from pixelart import pixel

DESK_Y = 134
FIG = {"emiru": (32, 20), "maya": (148, 20)}
PAIR = {"emiru": (8, 20), "maya": (172, 20)}
FACING = {"emiru": 1, "maya": -1}
OTHER = {"emiru": "maya", "maya": "emiru"}


def glow(img, box, color, alpha=0.2):
    """Soft light on a wall: an ellipse of colour mixed in."""
    blend(img, pixel.mask(lambda m: m.ellipse(box, fill=255), img.size), color, alpha)


# --- Emiru's room ----------------------------------------------------------------------------------

WIGS = (("pink", "long"), ("blue", "bob"), ("gold", "tails"), ("white", "long"), ("red", "bob"),
        ("teal", "tails"), ("lilac", "bob"), ("orange", "long"), ("green", "bob"))


def wig(d, x, y, color, style):
    """A foam head on its stand, in a wig: (x, y) is the middle of the stand's foot."""
    d.rectangle((x - 1, y - 5, x + 1, y - 1), fill=C["foam_sh"])
    d.ellipse((x - 4, y - 16, x + 4, y - 5), fill=C["foam"], outline=INK)
    hair, dark = C[color], pixel.mix(C[color], INK, 0.35)
    d.pieslice((x - 6, y - 19, x + 6, y - 7), 180, 360, fill=hair, outline=INK)
    d.rectangle((x - 5, y - 13, x + 5, y - 12), fill=hair)                             # the fringe
    if style == "long":
        d.rectangle((x - 6, y - 13, x - 4, y - 2), fill=hair); d.rectangle((x + 4, y - 13, x + 6, y - 2), fill=hair)
        d.line([(x - 7, y - 13), (x - 7, y - 2)], fill=INK); d.line([(x + 7, y - 13), (x + 7, y - 2)], fill=INK)
    elif style == "tails":
        d.polygon([(x - 6, y - 15), (x - 10, y - 12), (x - 9, y - 3), (x - 6, y - 8)], fill=hair, outline=INK)
        d.polygon([(x + 6, y - 15), (x + 10, y - 12), (x + 9, y - 3), (x + 6, y - 8)], fill=hair, outline=INK)
    else:
        d.rectangle((x - 6, y - 13, x - 4, y - 7), fill=hair); d.rectangle((x + 4, y - 13, x + 6, y - 7), fill=hair)
    d.line([(x - 3, y - 17), (x + 2, y - 17)], fill=pixel.mix(C[color], C["white"], 0.5))
    d.point((x - 5, y - 10), fill=dark); d.point((x + 5, y - 10), fill=dark)


def singer(d, x, y):
    """The sewing machine, 46 x 26: (x, y) is the left end of its base."""
    d.rectangle((x, y - 5, x + 44, y), fill=C["black"], outline=INK)
    d.rectangle((x + 32, y - 24, x + 42, y - 5), fill=C["black"], outline=INK)             # the pillar
    d.rectangle((x + 4, y - 25, x + 42, y - 17), fill=C["black"], outline=INK)             # the arm
    d.rectangle((x + 4, y - 17, x + 12, y - 9), fill=C["black"], outline=INK)              # the head
    d.line([(x + 8, y - 9), (x + 8, y - 5)], fill=C["steel"])                              # the needle
    d.ellipse((x + 41, y - 26, x + 48, y - 15), fill=C["steel"], outline=INK)              # the wheel
    d.point((x + 44, y - 21), fill=C["steel_sh"])
    d.line([(x + 14, y - 21), (x + 30, y - 21)], fill=C["gold"])                           # the gold lettering
    d.line([(x + 16, y - 19), (x + 28, y - 19)], fill=C["gold_sh"])
    d.line([(x + 6, y - 2), (x + 38, y - 2)], fill=C["gold_sh"])
    d.rectangle((x + 20, y - 31, x + 24, y - 26), fill=C["pink"], outline=INK)             # a spool
    d.line([(x + 22, y - 26), (x + 9, y - 16)], fill=C["pink"])


@lru_cache(maxsize=1)
def emiru_room():
    img, d = picture(W, H, "ewall")
    vgrad(img, (0, 0, W, DESK_Y), "ewall_hi", "ewall", steps=3)
    dither_rect(img, (0, 4, W, 14), C["eled"], density=0.3, blend=0.35)                # the strip lights
    dither_rect(img, (0, 14, W, 24), C["eled"], density=0.12, blend=0.3)
    glow(img, (60, 30, 140, 140), "ewall_hi", 0.25)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 2), fill=C["eled"]); d.line([(0, 3), (W, 3)], fill=C["ears_hi"])
    # the wig wall: two white shelves of them
    for y in (42, 80):
        d.rectangle((124, y, 234, y + 2), fill=C["eshelf"], outline=INK)
        d.line([(125, y + 4), (233, y + 4)], fill=C["ewall_sh"])
    for i, (color, style) in enumerate(WIGS):
        wig(d, 136 + 19 * (i % 5), 42 if i < 5 else 80, color, style)
    # the sewing corner: the machine on its table, and a dress form in a foam breastplate
    d.rectangle((126, 114, 198, 118), fill=C["eshelf"], outline=INK)
    d.rectangle((130, 118, 133, DESK_Y), fill=C["eshelf_sh"]); d.rectangle((191, 118, 194, DESK_Y), fill=C["eshelf_sh"])
    d.polygon([(128, 113), (152, 110), (158, 113), (146, 116), (136, 124), (129, 130), (126, 126)], fill=C["knit"],
              outline=INK)
    singer(d, 146, 113)
    d.rectangle((214, 112, 216, DESK_Y), fill=C["steel_sh"])                           # the form's pole
    d.ellipse((211, 76, 219, 84), fill=C["form_sh"], outline=INK)
    d.polygon([(205, 84), (225, 84), (229, 92), (226, 104), (222, 114), (208, 114), (204, 104), (201, 92)],
              fill=C["form"], outline=INK)
    d.polygon([(205, 86), (225, 86), (228, 93), (225, 103), (215, 108), (205, 103), (202, 93)], fill=C["steel"],
              outline=INK)
    d.line([(207, 89), (212, 100)], fill=C["steel_hi"]); d.line([(215, 87), (215, 107)], fill=C["steel_sh"])
    d.line([(219, 89), (223, 99)], fill=C["steel_hi"])
    d.ellipse((199, 84, 207, 91), fill=C["steel"], outline=INK); d.ellipse((223, 84, 231, 91), fill=C["steel"], outline=INK)
    # her chair, behind her
    d.polygon([(64, DESK_Y), (62, 90), (67, 66), (78, 56), (106, 56), (117, 66), (122, 90), (120, DESK_Y)],
              fill=C["chair"], outline=INK)
    d.polygon([(70, DESK_Y), (68, 90), (73, 70), (82, 62), (102, 62), (111, 70), (116, 90), (114, DESK_Y)],
              fill=C["chair_hi"])
    # on the left wall: a shelf of plush things
    d.rectangle((0, 86, 50, 88), fill=C["eshelf"], outline=INK)
    d.ellipse((6, 68, 26, 86), fill=C["white"], outline=INK)                           # something round and fluffy
    d.point((12, 76), fill=INK); d.point((19, 76), fill=INK); d.rectangle((14, 80, 17, 82), fill=C["pink"])
    d.polygon([(8, 70), (6, 63), (12, 68)], fill=C["brown_hi"], outline=INK)
    d.polygon([(24, 70), (26, 63), (20, 68)], fill=C["brown_hi"], outline=INK)
    d.ellipse((30, 72, 46, 86), fill=C["ears"], outline=INK)                           # a cat
    d.polygon([(31, 75), (31, 67), (37, 72)], fill=C["ears"], outline=INK)
    d.polygon([(45, 75), (45, 67), (39, 72)], fill=C["ears"], outline=INK)
    d.point((35, 78), fill=INK); d.point((41, 78), fill=INK); d.point((38, 80), fill=C["ears_sh"])
    return img


@lru_cache(maxsize=1)
def emiru_desk():
    f = Canvas(W, H)
    f.rect((0, DESK_Y, W, H), "edesk")
    f.line([(0, DESK_Y), (W, DESK_Y)], "edesk_hi")
    f.rect((0, DESK_Y + 20, W, H), "edesk_sh")
    f.rect((106, DESK_Y + 6, 164, DESK_Y + 14), "white")                                # the keyboard, in pink keys
    f.d.rectangle((106, DESK_Y + 6, 164, DESK_Y + 14), outline=INK + (255,))
    for i, x in enumerate(range(109, 162, 3)):
        f.px((x, DESK_Y + 8), ("ears", "ears_sh", "lilac", "ears")[i % 4])
        f.px((x + 1, DESK_Y + 11), ("lilac", "ears", "ears_sh", "ears")[i % 4])
    f.ell((172, DESK_Y + 7, 180, DESK_Y + 14), "white"); f.px((176, DESK_Y + 8), "ears")   # the mouse
    # the can that pays the bills
    f.rect((188, DESK_Y - 13, 194, DESK_Y + 4), "can_silver")
    f.rect((188, DESK_Y - 13, 191, DESK_Y - 5), "can_blue"); f.rect((191, DESK_Y - 5, 194, DESK_Y + 4), "can_blue")
    f.rect((190, DESK_Y - 6, 192, DESK_Y - 4), "red"); f.px((191, DESK_Y - 7), "yellow")
    f.line([(188, DESK_Y - 14), (194, DESK_Y - 14)], "steel")
    # the glue gun, on its stand
    f.poly([(200, DESK_Y - 4), (216, DESK_Y - 4), (220, DESK_Y - 1), (216, DESK_Y + 2), (208, DESK_Y + 2), (206, DESK_Y + 10),
            (200, DESK_Y + 10)], "teal")
    f.poly([(220, DESK_Y - 2), (226, DESK_Y - 1), (220, DESK_Y + 1)], "orange")
    f.rect((194, DESK_Y - 3, 200, DESK_Y - 1), "white")
    f.line([(208, DESK_Y + 3), (210, DESK_Y + 6)], "orange")
    f.line([(202, DESK_Y - 2), (214, DESK_Y - 2)], "teal_sh")
    f.px((227, DESK_Y + 1), "white"); f.px((227, DESK_Y + 3), "white")
    # the mic on its arm, from the left
    f.line([(0, DESK_Y + 4), (20, DESK_Y - 20)], "white", w=3)
    f.rect((18, DESK_Y - 28, 40, DESK_Y - 18), "white")
    f.rect((36, DESK_Y - 29, 46, DESK_Y - 17), "ears")
    f.line([(39, DESK_Y - 27), (39, DESK_Y - 19)], "ears_sh"); f.line([(43, DESK_Y - 27), (43, DESK_Y - 19)], "ears_sh")
    return f.done()


# --- Maya's set --------------------------------------------------------------------------------------

def planks(img, box, base="barn", gap=11):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=C[base])
    for i, x in enumerate(range(x0, x1, gap)):
        d.line([(x, y0), (x, y1)], fill=C[base + "_sh"])
        if i % 3 == 1:
            d.line([(x + 3, y0), (x + 3, y1)], fill=C[base + "_hi"])
        k = y0 + int(rnd("knot", x) * (y1 - y0))
        d.ellipse((x + 4, k, x + 7, k + 2), fill=C[base + "_sh"])


def far_fence(d, x0, x1, y, step=14):
    for x in range(x0, x1, step):
        d.rectangle((x, y - 6, x + 1, y + 2), fill=C["wood_sh"])
    d.line([(x0, y - 4), (x1, y - 4)], fill=C["wood_hi"]); d.line([(x0, y - 1), (x1, y - 1)], fill=C["wood_hi"])


def tree(d, x, y, r=9):
    d.rectangle((x - 1, y - 2, x + 1, y + 6), fill=C["wood_sh"])
    d.ellipse((x - r, y - r - 4, x + r, y + 2), fill=C["tree"])
    d.ellipse((x - r + 2, y - r - 2, x + r - 4, y - 3), fill=C["tree_sh"])


OPENING = (110, 22, 198, 106)        # the barn's doorway on to the pasture


@lru_cache(maxsize=1)
def maya_room():
    img, d = picture(W, H, "barn")
    planks(img, (0, 0, W, DESK_Y))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 5), fill=C["beam"]); d.line([(0, 6), (W, 6)], fill=INK)
    # the doorway on to the pasture
    x0, y0, x1, y1 = OPENING
    vgrad(img, (x0, y0, x1, 64), "sky", "sky_hi", steps=4)
    d = ImageDraw.Draw(img)
    d.polygon([(x0, 62), (x0 + 20, 54), (x0 + 44, 60), (x0 + 66, 52), (x1, 58), (x1, 68), (x0, 68)], fill=C["hills"])
    tree(d, x0 + 12, 60, 8); tree(d, x1 - 10, 58, 9); tree(d, x0 + 40, 62, 6)
    d.rectangle((x0, 66, x1, y1), fill=C["pasture"])
    for y in (70, 78, 88, 98):
        d.line([(x0, y), (x1, y)], fill=C["pasture_hi" if y % 4 else "pasture_sh"])
    far_fence(d, x0, x1, 74)
    d.rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), outline=INK)
    d.rectangle((x0 - 2, y0 - 2, x1 + 2, y1 + 2), outline=C["beam"], width=2)
    d.rectangle((x0, y0, x1, y1), outline=INK)
    # the sign over it
    d.rectangle((127, 8, 181, 18), fill=C["maya_sh"], outline=INK)
    silk(img, (154, 11), "ALVEUS", "white", anchor="ma")
    # hay, and a sack of feed
    d = ImageDraw.Draw(img)
    d.rectangle((92, 112, 128, DESK_Y), fill=C["hay"], outline=INK)
    for y in (117, 123, 129):
        d.line([(93, y), (127, y)], fill=C["hay_sh"])
    d.line([(104, 112), (104, DESK_Y)], fill=C["wood_sh"]); d.line([(116, 112), (116, DESK_Y)], fill=C["wood_sh"])
    d.polygon([(134, DESK_Y), (133, 116), (138, 111), (156, 111), (160, 116), (159, DESK_Y)], fill=C["cream"], outline=INK)
    d.rectangle((138, 118, 155, 126), fill=C["maya_sh"])
    # the perch, to her right
    d.rectangle((296, 96, 298, DESK_Y), fill=C["wood_sh"], outline=INK)
    d.rectangle((282, 93, 312, 96), fill=C["wood"], outline=INK)
    return img


@lru_cache(maxsize=1)
def feeder():
    """The feeder chat pays to fill: a hopper on a post, and a trough under its spout."""
    f = Canvas(20, 38)
    f.rect((9, 14, 11, 36), "steel_sh")
    f.poly([(2, 1), (18, 1), (16, 13), (4, 13)], "maya_sh"); f.line([(3, 2), (17, 2)], "maya")
    f.rect((7, 5, 12, 9), "white"); f.px((9, 7), "maya_sh")
    f.poly([(4, 13), (1, 18), (5, 18), (8, 13)], "steel")
    f.rect((0, 30, 12, 34), "steel"); f.line([(1, 31), (11, 31)], "hay")
    return f.done()


@lru_cache(maxsize=1)
def maya_desk():
    f = Canvas(W, H)
    f.rect((0, DESK_Y, W, H), "mdesk")
    f.line([(0, DESK_Y), (W, DESK_Y)], "mdesk_hi")
    f.rect((0, DESK_Y + 20, W, H), "mdesk_sh")
    for x in (60, 150, 240):
        f.line([(x, DESK_Y + 1), (x, H)], "mdesk_sh")
    f.rect((156, DESK_Y + 6, 210, DESK_Y + 14), "black")                                # the keyboard
    for x in range(158, 209, 3):
        f.px((x, DESK_Y + 8), "grey_sh"); f.px((x + 1, DESK_Y + 11), "grey_sh")
    f.ell((140, DESK_Y + 7, 148, DESK_Y + 14), "black"); f.px((144, DESK_Y + 8), "maya")    # the mouse
    f.rect((116, DESK_Y - 8, 126, DESK_Y + 4), "olive"); f.line([(117, DESK_Y - 7), (117, DESK_Y + 3)], "olive_hi")   # a mug
    f.line([(127, DESK_Y - 5), (129, DESK_Y - 3), (127, DESK_Y)], "olive")
    f.pxs([(120, DESK_Y - 3), (121, DESK_Y - 4), (122, DESK_Y - 3), (121, DESK_Y - 2)], "white")
    f.poly([(94, DESK_Y + 4), (98, DESK_Y - 2), (108, DESK_Y - 2), (112, DESK_Y + 3), (110, DESK_Y + 10), (96, DESK_Y + 10)],
           "glove")                                                                      # the glove, off duty
    f.line([(98, DESK_Y + 1), (108, DESK_Y + 1)], "glove_hi"); f.line([(100, DESK_Y + 6), (108, DESK_Y + 6)], "glove_sh")
    f.rect((108, DESK_Y + 4, 114, DESK_Y + 8), "glove_sh")
    # the mic on its arm, from the right
    f.line([(W, DESK_Y + 4), (300, DESK_Y - 20)], "black", w=3)
    f.rect((280, DESK_Y - 28, 302, DESK_Y - 18), "black")
    f.ell((268, DESK_Y - 31, 286, DESK_Y - 15), "grey_sh")
    f.pxs([(272, DESK_Y - 26), (276, DESK_Y - 22), (280, DESK_Y - 27), (274, DESK_Y - 19), (279, DESK_Y - 18)], "grey")
    return f.done()


# --- the gate ------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def gate():
    img, d = picture(W, H, "sky")
    vgrad(img, (0, 0, W, 92), "sky", "sky_lo", steps=5)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 84), (40, 74), (90, 80), (140, 72), (200, 78), (260, 70), (W, 80), (W, 96), (0, 96)], fill=C["hills"])
    for x, y, r in ((14, 86, 11), (40, 88, 8), (92, 86, 10), (118, 88, 7), (206, 86, 9), (232, 88, 11), (270, 86, 8),
                    (300, 88, 10)):
        tree(d, x, y, r)
    d.rectangle((0, 92, W, H), fill=C["pasture"])
    for i, y in enumerate((96, 102, 110, 120, 132)):
        d.line([(0, y), (W, y)], fill=C["pasture_hi" if i % 2 else "pasture_sh"])
    d.polygon([(142, DESK_Y + 2), (184, DESK_Y + 2), (168, 104), (158, 104)], fill=C["dirt"])   # the track to the barn
    d.line([(150, 124), (176, 124)], fill=C["dirt_sh"]); d.line([(155, 112), (171, 112)], fill=C["dirt_sh"])
    # the barn, up the track
    d.polygon([(146, 104), (146, 90), (163, 82), (180, 90), (180, 104)], fill=C["red_sh"], outline=INK)
    d.polygon([(143, 91), (163, 80), (183, 91), (183, 88), (163, 77), (143, 88)], fill=C["grey_sh"], outline=INK)
    d.rectangle((158, 94, 168, 104), fill=C["beam"]); d.line([(158, 94), (168, 104)], fill=C["cream"])
    d.line([(168, 94), (158, 104)], fill=C["cream"]); d.rectangle((158, 94, 168, 104), outline=C["cream"])
    far_fence(d, 0, 142, 104, 16); far_fence(d, 186, W, 104, 16)
    # the gate itself: its posts at the edges of the frame, its beam across the top
    for x0 in (0, W - 8):
        d.rectangle((x0, 0, x0 + 7, DESK_Y), fill=C["wood"], outline=INK)
        d.line([(x0 + 2, 6), (x0 + 2, DESK_Y)], fill=C["wood_hi"])
    d.rectangle((0, 0, W, 4), fill=C["wood"]); d.line([(0, 5), (W, 5)], fill=INK)
    d.line([(8, 2), (W - 9, 2)], fill=C["wood_hi"])
    # the house rules, on a board hung at each side
    for x, rows in ((12, ("PLEASE DON'T", "TAP THE GLASS")), (222, ("KEEP YOUR HANDS", "INSIDE THE CHAT"))):
        d.line([(x + 8, 5), (x + 8, 8)], fill=INK); d.line([(x + 78, 5), (x + 78, 8)], fill=INK)
        d.rectangle((x, 8, x + 86, 26), fill=C["cream"], outline=INK)
        d.rectangle((x + 1, 9, x + 85, 25), outline=C["maya_sh"])
        for i, s in enumerate(rows):
            silk(img, (x + 43, 11 + 7 * i), s, "maya_sh", anchor="ma")
    return img


@lru_cache(maxsize=1)
def fence():
    """The paddock fence they lean on."""
    f = Canvas(W, H)
    f.rect((0, DESK_Y - 2, W, DESK_Y + 4), "wood")
    f.line([(0, DESK_Y - 2), (W, DESK_Y - 2)], "wood_hi"); f.line([(0, DESK_Y + 4), (W, DESK_Y + 4)], "wood_sh")
    f.rect((0, DESK_Y + 16, W, DESK_Y + 21), "wood"); f.line([(0, DESK_Y + 16), (W, DESK_Y + 16)], "wood_hi")
    for x in (2, 154, 306):
        f.rect((x, DESK_Y - 8, x + 11, H), "wood_sh"); f.line([(x + 2, DESK_Y - 7), (x + 2, H)], "wood")
        f.rect((x + 4, DESK_Y, x + 6, DESK_Y + 2), "steel_sh"); f.rect((x + 4, DESK_Y + 18, x + 6, DESK_Y + 19), "steel_sh")
    return f.done()


# --- the gift shop ---------------------------------------------------------------------------------------

def tee(d, x, y, color, mark):
    """A T-shirt on a hanger, 26 wide."""
    d.line([(x + 13, y - 4), (x + 13, y)], fill=C["steel_sh"])
    d.polygon([(x + 8, y), (x + 18, y), (x + 26, y + 5), (x + 23, y + 10), (x + 20, y + 8), (x + 20, y + 26), (x + 6, y + 26),
               (x + 6, y + 8), (x + 3, y + 10), (x, y + 5)], fill=C[color], outline=INK)
    d.line([(x + 10, y + 1), (x + 13, y + 3), (x + 16, y + 1)], fill=INK)
    d.rectangle((x + 11, y + 11, x + 15, y + 15), fill=C[mark])


@lru_cache(maxsize=1)
def shop():
    img, d = picture(W, H, "shopwall")
    vgrad(img, (0, 0, W, DESK_Y), "shopwall", "shopwall_sh", steps=3)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 8):                                                           # pegboard
        for y in range(10, DESK_Y, 8):
            d.point((x + 4, y), fill=C["shopwall_sh"])
    d.rectangle((0, 0, W, 4), fill=C["wood"]); d.line([(0, 5), (W, 5)], fill=INK)
    # shirts either side, the shelf of plush animals between
    for x, color, mark in ((10, "olive", "white"), (40, "ears", "white"), (72, "black", "maya"),
                           (222, "white", "maya_sh"), (252, "olive", "white"), (284, "ears", "white")):
        tee(d, x, 14, color, mark)
        tee(d, x, 60, ("ears", "white", "olive", "olive", "black", "white")[x % 6], "maya")
    d.rectangle((106, 104, 214, 107), fill=C["wood"], outline=INK)
    d.line([(107, 109), (213, 109)], fill=C["shopwall_sh"])
    for spr, x in ((animals.wolf(), 110), (animals.tortoise(), 140), (mirror(animals.winnie()), 172)):
        img.paste(spr, (x, 104 - spr.height), spr)
    d = ImageDraw.Draw(img)
    for x in (120, 156, 196):                                                          # price tags
        d.rectangle((x, 98, x + 6, 103), fill=C["paper"], outline=INK)
    return img


@lru_cache(maxsize=1)
def counter():
    f = Canvas(W, H)
    f.rect((0, DESK_Y, W, H), "wood")
    f.line([(0, DESK_Y), (W, DESK_Y)], "wood_hi")
    f.rect((0, DESK_Y + 20, W, H), "wood_sh")
    f.rect((154, DESK_Y - 4, 166, DESK_Y + 2), "black")                                 # the announcer's mic
    f.line([(160, DESK_Y - 4), (160, DESK_Y - 20)], "steel_sh", w=2)
    f.ell((155, DESK_Y - 28, 165, DESK_Y - 18), "grey_sh")
    f.pxs([(158, DESK_Y - 25), (161, DESK_Y - 22), (162, DESK_Y - 26), (158, DESK_Y - 21)], "grey")
    f.px((160, DESK_Y - 1), "live")
    f.rect((176, DESK_Y - 14, 200, DESK_Y + 3), "paper")                                # the link, on a card
    f.d.rectangle((176, DESK_Y - 14, 200, DESK_Y + 3), outline=INK + (255,))
    for i in range(20):
        if rnd("qr", i) < 0.55:
            f.rect((180 + 4 * (i % 5), DESK_Y - 11 + 3 * (i // 5), 181 + 4 * (i % 5), DESK_Y - 10 + 3 * (i // 5)), "ink")
    f.rect((120, DESK_Y - 10, 132, DESK_Y + 3), "steel_hi")                             # a jar of pins
    f.d.rectangle((120, DESK_Y - 10, 132, DESK_Y + 3), outline=INK + (255,))
    f.pxs([(123, DESK_Y - 4), (127, DESK_Y - 6), (129, DESK_Y - 1), (124, DESK_Y)], "ears")
    f.pxs([(125, DESK_Y - 2), (128, DESK_Y - 4), (122, DESK_Y - 7)], "maya")
    return f.done()


BACK = {"emiru": emiru_room, "maya": maya_room, "gate": gate, "shop": shop}
FRONT = {"emiru": emiru_desk, "maya": maya_desk, "gate": fence, "shop": counter}


# --- what moves ---------------------------------------------------------------------------------------

def alive(img, place, t, cow=True, bird=True):
    """Who is about in a place at time t. Gags that bring an animal in front of the camera take it out of
    the background: `cow` and `bird` say whether Winnie and the hawk are where they usually are."""
    if place == "maya":
        if cow:
            w = animals.winnie(int(t * 2.2) % 2, 1 if (t % 5.3) < 0.3 else 0)
            img.paste(w, (120, 72), w)
            fd = feeder()
            img.paste(fd, (172, 66), fd)
        if bird:
            hk = mirror(animals.hawk(1 if (t % 6.1) < 1.4 else 0))
            img.paste(hk, (280, 64), hk)
    elif place == "gate":
        if cow:
            w = mirror(animals.winnie(int(t * 2.2) % 2, 1 if (t % 4.7) < 0.3 else 0))
            img.paste(w, (110, 96), w)
        e = animals.emu(1 if (t % 3.7) < 0.15 else 0)
        img.paste(e, (166, 90 + int(round(1.5 * math.sin(t * 1.3)))), e)


if __name__ == "__main__":
    from PIL import Image

    from characters import figure
    from engine import ROOT, scaled
    sheet = Image.new("RGB", (2 * W + 4, 2 * H + 4), (0, 0, 0))
    for i, place in enumerate(BACK):
        img = BACK[place]().copy()
        alive(img, place, 3.0)
        for who in ("emiru", "maya"):
            if place in (who, "gate", "shop"):
                spr, _ = figure(who, "palm" if who == "emiru" else "desk", facing=FACING[who], mouth="grin", lean=2)
                img.paste(spr, (PAIR if place in ("gate", "shop") else FIG)[who], spr)
        img.paste(FRONT[place](), (0, 0), FRONT[place]())
        sheet.paste(img, ((i % 2) * (W + 4), (i // 2) * (H + 4)))
    out = ROOT / "build" / "rooms.png"
    out.parent.mkdir(exist_ok=True)
    scaled(sheet, 3).save(out)
    print(out)
