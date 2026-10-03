"""Sprites for the Verse 2 gags (Bibi has the floor): the framed Nobel letter, the thrift-shop medal and its
tag, the magnifier, the archive clip's mini Trump and teleprompter, the desk machines that walk out, penguins
and the drive-thru, the hand mirror, the red button, the diet soda and its tray, the eyedropper, the wattle,
the basting brush and the turkeys. Each is a cached RGBA image outlined in ink.

    uv run python projects/pardon-me/art_v2.py     # -> build/art_v2.png, a sheet of them all
"""
from functools import cache

import art
from engine import INK, SILK, C, Canvas, mix, outlined, text_width, tint
from PIL import Image, ImageDraw

CREAM, CREAM_SH = (246, 240, 222), (214, 204, 180)
BRASS, BRASS_SH = (214, 170, 80), (160, 116, 44)
GLASS, GLASS_HI = (170, 214, 236), (236, 248, 255)
SODA = (196, 200, 210)
PENGUIN_BK, PENGUIN_BELLY, PENGUIN_FEET = (36, 38, 52), (246, 246, 240), (246, 160, 40)


# --- the framed letter ------------------------------------------------------------------------

@cache
def framed_letter():
    """Bibi's Nobel letter in a heavy gold frame (52x44): a header, scribbled lines, the red LOL JK, and a
    brass PENDING plate on the bottom rail."""
    w, h = 52, 44
    s = Canvas(w, h)
    s.rect((1, 1, w - 2, h - 2), "gold_sh")
    s.rect((1, 1, w - 3, h - 3), "gold")
    s.line([(1, 1), (w - 3, 1)], "gold_hi")
    s.line([(1, 1), (1, h - 3)], "gold_hi")
    s.rect((4, 4, w - 5, h - 9), INK)
    s.rect((5, 5, w - 6, h - 10), CREAM)
    s.line([(5, h - 10), (w - 6, h - 10)], CREAM_SH)
    s.text((9, 3), "NOBEL", INK)
    for y, x1 in ((13, 41), (16, 37), (19, 43)):                      # the body of the letter, too small to read
        for x in range(9, x1, 2):
            s.px((x, y), (120, 116, 130))
    s.text((11, 21), "LOL JK", "mk_red")
    for x, y in ((3, 3), (w - 4, 3)):                                  # corner rosettes
        s.px((x, y), "gold_hi")
    pw = text_width("PENDING", SILK) + 6                              # the brass plate on the bottom rail
    px0 = (w - pw) // 2
    s.rect((px0 - 1, h - 12, px0 + pw, h - 2), INK)
    s.rect((px0, h - 11, px0 + pw - 1, h - 3), BRASS)
    s.line([(px0, h - 3), (px0 + pw - 1, h - 3)], BRASS_SH)
    s.text((px0 + 3, h - 13), "PENDING", (70, 46, 20))
    return s.done()


@cache
def neck_medal():
    """A gold medal on a short ribbon, worn round the neck: 16x19, the straps' tops at y 0."""
    s = Canvas(16, 19)
    s.poly([(2, 0), (5, 0), (8, 7), (6, 8)], "blue")
    s.poly([(13, 0), (10, 0), (7, 7), (9, 8)], (60, 90, 170))
    s.ell((2, 6, 13, 17), "gold_sh")
    s.ell((3, 7, 12, 16), "gold")
    s.ell((5, 9, 9, 14), "gold_sh")                                    # the profile in relief
    s.px((9, 10), "gold_sh")
    s.px((4, 8), "gold_hi")
    s.px((3, 10), "gold_hi")
    return s.done()


@cache
def price_tag():
    """A thrift-shop price tag on a string: USED, $2."""
    s = Canvas(32, 18)
    s.poly([(5, 1), (30, 1), (30, 16), (5, 16), (1, 8)], "white")
    s.line([(5, 16), (30, 16)], "paper_sh")
    s.px((5, 8), INK)
    s.text((7, -1), "USED", "mk_red")
    s.text((12, 7), "$2", INK)
    return s.done()


@cache
def magnifier(r=9):
    """A magnifying glass, lens centre at (r + 2, r + 2), the handle down to the left. The lens is left
    clear: the gag draws what it magnifies."""
    n = 2 * r + 14
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = r + 2
    d.line([(cx - r * 0.7, cy + r * 0.7), (cx - r * 0.7 - 9, cy + r * 0.7 + 9)], fill=INK + (255,), width=5)
    d.line([(cx - r * 0.7, cy + r * 0.7), (cx - r * 0.7 - 9, cy + r * 0.7 + 9)], fill=C["red_sh"] + (255,), width=3)
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), outline=INK + (255,), width=3)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=C["steel"] + (255,), width=1)
    return outlined(img)


@cache
def lens_view(r=10):
    """What the magnifier shows over Trump's hand: a cuff blown up to giant size, and the hand still tiny.
    Circular, (2r + 1) square, the sleeve coming in from the right."""
    n = 2 * r + 1
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, n, n), fill=mix(C["wall_hi"], (255, 255, 255), 0.35) + (255,))
    d.rectangle((r + 2, r - 6, n, r + 6), fill=C["suit"] + (255,))               # the sleeve, magnified
    d.line([(r + 2, r - 6), (n, r - 6)], fill=C["suit_hi"] + (255,))
    d.rectangle((r - 1, r - 5, r + 1, r + 5), fill=C["shirt"] + (255,))          # the cuff
    d.line([(r - 1, r + 5), (r + 1, r + 5)], fill=C["shirt_sh"] + (255,))
    d.rectangle((r - 3, r - 1, r - 2, r + 1), fill=C["tskin"] + (255,))          # the hand: still tiny
    for y in (r - 1, r, r + 1):
        d.point((r - 4, y), fill=C["tskin"] + (255,))
    d.point((r - 2, r - 2), fill=C["tskin"] + (255,))
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
    img.putalpha(m)
    return img


# --- the archive clip ------------------------------------------------------------------------------------

@cache
def mini_trump(lurch=False):
    """Trump at a twelfth of his size, for the archive footage: the swoop, the tan, the long red tie."""
    s = Canvas(14, 22)
    s.rect((4, 10, 10, 18), "suit")                                    # jacket
    s.rect((6, 10, 8, 12), "shirt")
    s.rect((7, 11, 7, 16), "tie")
    s.rect((4, 18, 6, 20), "suit_sh")
    s.rect((8, 18, 10, 20), "suit_sh")
    s.ell((4, 3, 10, 10), "tskin")                                    # head
    s.px((8, 6), "tring")
    s.px((9, 6), "tring")
    s.rect((3, 1, 10, 4), "thair")                                     # the swoop, forward
    s.rect((9, 2, 12, 4), "thair")
    s.px((5, 1), "thair_hi")
    s.px((10, 2), "thair_hi")
    s.px((9, 8), "mouth")
    img = s.done()
    return img.rotate(-14, resample=Image.NEAREST, expand=False) if lurch else img


@cache
def teleprompter(text, color="white", tilt=0):
    """A presidential teleprompter: a glass pane on a pole, with `text` on the glass."""
    tw = text_width(text, SILK) if text else 20
    w = max(26, tw + 8)
    s = Canvas(w + 2, 34)
    s.rect((w // 2, 14, w // 2 + 1, 31), "steel_sh")                 # the pole and the foot
    s.rect((w // 2 - 5, 31, w // 2 + 6, 32), "steel_sh")
    s.rect((1, 1, w, 14), (40, 60, 70))                               # the dark glass
    s.line([(1, 1), (w, 1)], (90, 130, 140))
    if text:
        s.text((1 + (w - tw) // 2, 2), text, color)
    img = s.done()
    return img.rotate(tilt, resample=Image.NEAREST, expand=True) if tilt else img


@cache
def mini_podium():
    s = Canvas(16, 16)
    s.rect((1, 2, 14, 14), "marble")
    s.rect((1, 1, 14, 3), "desk")
    s.ell((5, 6, 10, 11), "gold_sh")
    return s.done()


# --- walking machines ---------------------------------------------------------------------------------------

@cache
def desk_mic():
    """The delegation desk's gooseneck microphone on its base, exactly as hall.desk draws it: paste it at
    (DESK x0 + 1, DESK top - 12)."""
    s = Canvas(21, 13)
    s.rect((1, 10, 19, 12), "black")
    s.line([(9, 10), (15, 2)], INK, 2)
    return s.img.copy()


@cache
def laptop(screen="steel_sh", text=None):
    """The desk's laptop, lid up, from the side: a 16x8 slab (as hall.desk draws it)."""
    s = Canvas(19, 10)
    s.rect((1, 1, 17, 8), INK)
    s.rect((2, 2, 16, 7), screen)
    if text:
        s.text((3, -2), text, "white")
    return s.img.copy()


@cache
def laptop_front(text=None):
    """The laptop, turned to face us on its own two feet: a 22x15 lid and keyboard; `text` on its screen."""
    s = Canvas(24, 17)
    s.rect((2, 1, 21, 12), "steel_sh")
    s.rect((3, 2, 20, 11), "btie_sh" if text else (40, 50, 70))
    if text:
        s.text((3 + (18 - text_width(text, SILK)) // 2, 1), text, "white")
    s.poly([(2, 13), (21, 13), (23, 15), (0, 15)], "steel")
    s.line([(3, 14), (20, 14)], "steel_sh")
    return s.done()


@cache
def stand_mic():
    """The desk microphone, sat up straight: a mesh head on a short stem and a heavy base, 12x17."""
    s = Canvas(12, 17)
    s.rect((1, 13, 10, 15), "black")
    s.rect((5, 7, 6, 13), "steel_sh")
    s.ell((3, 1, 8, 8), (70, 72, 86))
    s.pxs([(4, 3), (6, 3), (5, 5), (7, 5), (4, 6)], (130, 134, 150))
    return s.done()


def legs(img, x, y, phase, n=2, spread=6, color=INK, h=4):
    """Little cartoon legs under a walking prop: feet at y, alternating with `phase`."""
    d = ImageDraw.Draw(img)
    for i in range(n):
        lx = x + (i - (n - 1) / 2) * spread
        k = 1 if (i + int(phase)) % 2 else -1
        d.line([(lx, y - h), (lx + k * 2, y)], fill=color, width=1)
        d.line([(lx + k * 2, y), (lx + k * 2 + 2, y)], fill=color, width=1)


# --- penguins and the drive-thru ----------------------------------------------------------------------------

@cache
def penguin(cap=False, flap=False, facing=1):
    """A little penguin, about 12x16; `cap` puts it in a paper fast-food hat, `flap` raises a flipper."""
    s = Canvas(16, 20)
    s.ell((3, 4, 12, 18), PENGUIN_BK)
    s.ell((5, 8, 11, 18), PENGUIN_BELLY)
    s.ell((4, 3, 11, 10), PENGUIN_BK)
    s.rect((7, 5, 7, 6), "white")                                      # the eye
    s.px((8, 6), INK)
    s.poly([(11, 6), (14, 7), (11, 8)], PENGUIN_FEET)                 # the beak
    if flap:
        s.poly([(3, 9), (0, 5), (1, 4), (4, 8)], PENGUIN_BK)
    else:
        s.poly([(3, 9), (1, 15), (3, 15), (5, 11)], PENGUIN_BK)
    s.rect((5, 18, 7, 19), PENGUIN_FEET)
    s.rect((9, 18, 11, 19), PENGUIN_FEET)
    if cap:
        s.poly([(3, 3), (5, 0), (11, 0), (12, 3)], "white")           # a paper hat with a red band
        s.line([(3, 3), (12, 3)], "red")
        s.line([(4, 2), (11, 2)], "red")
    img = s.done()
    return img.transpose(Image.FLIP_LEFT_RIGHT) if facing < 0 else img


@cache
def drive_thru_booth(lit=True):
    """A little drive-thru hut on the ice: a DRIVE THRU sign on its red roof and a lit serving window (the
    penguin goes in it at (7..23, 17..31)). 38x46."""
    s = Canvas(38, 46)
    s.rect((3, 18, 34, 45), (226, 222, 214))                         # the walls
    s.rect((3, 41, 34, 45), (196, 190, 182))
    s.poly([(0, 19), (37, 19), (34, 14), (3, 14)], "red")             # the roof
    s.line([(3, 14), (34, 14)], "red_hi")
    s.rect((8, 1, 29, 13), (190, 40, 48) if lit else (110, 40, 48))   # the sign on the roof
    s.rect((12, 13, 13, 14), "steel_sh")
    s.rect((24, 13, 25, 14), "steel_sh")
    fg = (255, 240, 200) if lit else (170, 120, 110)
    s.text((9, -1), "DRIVE", fg)
    s.text((10, 6), "THRU", fg)
    s.rect((7, 21, 23, 35), (250, 226, 150))                          # the window, lit
    return s.done()


@cache
def menu_board(rows=("MENU", "FISH", "ONLY", "FISH")):
    """A drive-thru menu board on legs."""
    w = max(text_width(r, SILK) for r in rows) + 8
    h = 7 * len(rows) + 4
    s = Canvas(w + 2, h + 6)
    s.rect((1, 1, w, h), (36, 40, 52))
    for i, r in enumerate(rows):
        s.text((1 + (w - text_width(r, SILK)) // 2, -1 + 7 * i), r, "gold" if i == 0 else "white")
    s.rect((4, h + 1, 5, h + 4), "steel_sh")
    s.rect((w - 4, h + 1, w - 3, h + 4), "steel_sh")
    return s.done()


@cache
def fish(angle=0):
    """A silver fish, 12x7."""
    s = Canvas(14, 9)
    s.ell((1, 2, 10, 7), (150, 184, 210))
    s.ell((3, 2, 9, 4), (210, 230, 244))
    s.poly([(9, 4), (13, 1), (13, 8)], (110, 144, 180))
    s.px((3, 4), INK)
    img = s.done()
    return img.rotate(angle, resample=Image.NEAREST, expand=True) if angle else img


# --- Mr. Security, Mr. Insecurity -----------------------------------------------------------------------------

@cache
def hand_mirror(facing=-1):
    """A gold hand mirror turned to the camera, with Trump's reflection in it (yellow over orange): 11x17."""
    s = Canvas(11, 17)
    s.ell((1, 1, 9, 10), "gold_sh")
    s.ell((2, 2, 8, 9), GLASS)
    s.rect((3, 3, 7, 4), "thair")                                     # the reflection: the hair...
    s.px((7, 5), "thair")
    s.rect((4, 5, 6, 8), "tskin")                                     # ...over an orange face
    s.px((3, 6), "tskin")
    s.px((5, 6), INK)
    s.px((3, 8), GLASS_HI)
    s.rect((5, 11, 6, 15), "gold_sh")
    img = s.done()
    return img.transpose(Image.FLIP_LEFT_RIGHT) if facing > 0 else img


# --- the red button and the soda --------------------------------------------------------------------------------

@cache
def red_button(pressed=False):
    """A big red game-show button on a steel housing and a stalk, 20x16 (the dome sinks when pressed)."""
    s = Canvas(20, 16)
    s.rect((8, 10, 11, 15), "steel_sh")                               # the stalk it rises on
    if pressed:                                                       # squashed down into its housing
        s.ell((3, 4, 16, 10), "red_sh")
        s.ell((3, 4, 16, 8), "red")
        s.line([(6, 5), (8, 5)], "red_hi")
    else:
        s.ell((3, 1, 16, 10), "red_sh")
        s.ell((3, 1, 16, 8), "red")
        s.line([(6, 2), (8, 2)], "red_hi")
        s.px((5, 3), "red_hi")
    s.rect((1, 7, 18, 10), "steel_sh")
    s.line([(1, 7), (18, 7)], "steel")
    return s.done()


@cache
def slam_fist():
    """Trump's fist coming down on something, the sleeve running back down to his shoulder: 14x12.
    The bottom of the fist is at (4, 8)."""
    s = Canvas(14, 12)
    s.line([(7, 5), (12, 10)], "suit", 4)
    s.line([(5, 4), (7, 6)], "shirt", 2)
    s.rect((1, 2, 6, 8), "tskin")
    s.line([(1, 2), (5, 2)], "tskin_hi")
    for x in (2, 4):
        s.line([(x, 3), (x, 5)], "tskin_sh")
    return s.done()


@cache
def soda_can(big=1):
    """A plain silver diet soda can with a red band (no logo): 7x11, or scaled up `big` times."""
    s = Canvas(9, 13)
    s.rect((1, 1, 7, 11), SODA)
    s.line([(1, 1), (7, 1)], "steel_sh")
    s.rect((1, 5, 7, 7), "red")
    s.line([(2, 2), (2, 10)], "white")
    img = s.done()
    return img.resize((img.width * big, img.height * big), Image.NEAREST) if big > 1 else img


@cache
def feed_can():
    """The diet soda as the close-up camera sees it: 22x30, DIET on its red band, a bendy straw."""
    s = Canvas(24, 34)
    s.rect((1, 5, 22, 32), SODA)
    s.rect((1, 5, 22, 7), "steel_sh")
    s.rect((1, 30, 22, 32), "steel_sh")
    s.rect((1, 14, 22, 22), "red")
    s.line([(4, 8), (4, 29)], "white")
    s.text((3, 13), "DIET", "white")
    s.line([(14, 5), (14, 1)], "white", 2)                            # the straw
    s.line([(14, 1), (18, 1)], "white", 2)
    return s.done()


@cache
def wattle(k=1):
    """A turkey's red wattle, to hang under a chin: 4x6 (k scales the pixels)."""
    s = Canvas(6, 8)
    s.ell((1, 1, 4, 6), (214, 40, 48))
    s.px((2, 2), (240, 96, 96))
    img = s.done()
    return img.resize((img.width * k, img.height * k), Image.NEAREST) if k > 1 else img


@cache
def turkey_glazed(k):
    """art.turkey with Trump's hair, facing left, glazed orange by k (0..1; pass it rounded, it is cached)."""
    img = art.turkey("trump", facing=-1)
    return tint(img, (226, 112, 30), 0.45 * k) if k > 0 else img


@cache
def turkey_bust(hair, gobble=False):
    """art.turkey at twice the size, facing right, for a live feed (crop it to the screen)."""
    img = art.turkey(hair, facing=1, gobble=gobble)
    return img.resize((img.width * 2, img.height * 2), Image.NEAREST)


@cache
def roast_big():
    """art.roast_turkey with Trump's hair, at twice the size (80x52), for the payoff on his screen."""
    img = art.roast_turkey("trump")
    return img.resize((img.width * 2, img.height * 2), Image.NEAREST)


@cache
def silver_tray():
    """A silver serving tray, side on: 26x5."""
    s = Canvas(26, 5)
    s.rect((1, 1, 24, 3), "steel")
    s.line([(1, 1), (24, 1)], "white")
    s.line([(3, 3), (22, 3)], "steel_sh")
    return s.done()


# --- the eyedropper and the basting brush --------------------------------------------------------------------------

@cache
def eyedropper(color=None, squeeze=False):
    """A colour-picker pipette, tip at the bottom left (1, 16): a glass tube (filled with `color`) and a red
    rubber bulb, squashed while it sucks."""
    s = Canvas(19, 19)
    s.line([(2, 16), (10, 8)], GLASS, 4)
    s.line([(3, 15), (9, 9)], color or GLASS_HI, 2)
    s.px((1, 17), INK)
    s.line([(10, 8), (12, 6)], "steel_sh", 4)                         # the collar
    if squeeze:
        s.ell((12, 2, 16, 6), "red")
        s.px((13, 3), "red_hi")
    else:
        s.ell((11, 1, 17, 7), "red")
        s.ell((14, 4, 17, 7), "red_sh")
        s.px((13, 2), "red_hi")
    return s.done()


@cache
def basting_brush(angle=0):
    """A pastry brush dripping orange glaze, bristles at the left: 20x7."""
    s = Canvas(22, 9)
    s.rect((9, 3, 20, 5), "desk")
    s.line([(9, 3), (20, 3)], "desk_hi")
    s.rect((6, 2, 8, 6), "steel")
    s.rect((1, 2, 5, 6), (250, 196, 96))
    s.rect((1, 4, 5, 6), C["orange"])
    img = s.done()
    return img.rotate(angle, resample=Image.NEAREST, expand=True) if angle else img


if __name__ == "__main__":
    from engine import ROOT
    items = [framed_letter(), neck_medal(), price_tag(), magnifier(), lens_view(), mini_trump(), mini_trump(True),
             teleprompter("ERROR", "red"), teleprompter("I QUIT"), mini_podium(), desk_mic(), laptop(),
             laptop_front("BRB"), stand_mic(), drive_thru_booth(), menu_board(), penguin(True, True), fish(),
             hand_mirror(), red_button(), red_button(True), slam_fist(), soda_can(), feed_can(), silver_tray(),
             eyedropper(), eyedropper(C["tskin"], True), wattle(), basting_brush(), turkey_bust("bibi"),
             turkey_glazed(1.0), roast_big()]
    sheet = Image.new("RGB", (sum(i.width + 6 for i in items) + 6, 72), (196, 150, 70))
    x = 6
    for i in items:
        sheet.paste(i, (x, 68 - i.height), i)
        x += i.width + 6
    out = ROOT / "build" / "art_v2.png"
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.NEAREST).save(out)
    print(out)
