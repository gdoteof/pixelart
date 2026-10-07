"""Where chat is watching from: a desk at work, the stream on the second monitor with the sound off.

`draw(world, stream_img, t, ...)` draws the whole frame: a cubicle from behind its occupant, a spreadsheet
on the main monitor and, on the second one, `stream_img` (the 320x180 split screen) at a third of its size.

    MAIN    (38, 46, 144, 106)    the main monitor's screen: work
    SECOND  (176, 46, 282, 106)   the second monitor's screen: the stream, 106x60
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, H, W, Canvas, picture, rnd, silk, vgrad

MAIN = (38, 46, 144, 106)
SECOND = (176, 46, 282, 106)
WALL_TOP = 30                       # the top of the cubicle wall: the boss shows above it
DESK_Y = 126


@lru_cache(maxsize=4)
def sheet_pic(w, h, seed=0, title="Q3_FINAL_V7"):
    """A spreadsheet, as dull as they come."""
    img, d = picture(w, h, "white")
    d.rectangle((0, 0, w, 7), fill=C["green_sh"])
    silk(img, (3, 1), title, "white")
    d.rectangle((0, 8, w, 13), fill=C["grey_hi"])
    for x in range(10, w, 16):
        d.line([(x, 8), (x, h)], fill=C["grey_hi"])
    for y in range(14, h, 6):
        d.line([(0, y), (w, y)], fill=C["grey_hi"])
    d.rectangle((0, 14, 9, h), fill=C["grey_hi"])
    for r, y in enumerate(range(16, h - 4, 6)):
        for k, x in enumerate(range(12, w - 8, 16)):
            n = int(rnd("cell", seed, r, k) * 9)
            if n < 7:
                d.line([(x + 1, y + 1), (x + 3 + n, y + 1)], fill=C["grey_sh"] if n else C["red"])
                d.line([(x + 1, y + 2), (x + 3 + n, y + 2)], fill=C["grey_sh"] if n else C["red"])
    return img


@lru_cache(maxsize=1)
def backdrop():
    """The cubicle with nothing switched on: the wall, what's pinned to it, the desk and the two monitors."""
    img, d = picture(W, H, "stone")
    vgrad(img, (0, 0, W, WALL_TOP), "cream", "paper_sh", steps=3)               # the office beyond: the far wall
    d = ImageDraw.Draw(img)
    for x in (30, 150, 270):                                                   # strip lights
        d.rectangle((x, 3, x + 44, 6), fill=C["white"], outline=C["grey_hi"])
    d.ellipse((230, 10, 246, 26), fill=C["white"], outline=INK)                # the clock: not five yet
    d.line([(238, 18), (238, 13)], fill=INK); d.line([(238, 18), (242, 20)], fill=INK)
    d.rectangle((0, WALL_TOP, W, DESK_Y), fill=C["stone"])                     # the cubicle wall, in grey felt
    d.rectangle((0, WALL_TOP, W, WALL_TOP + 3), fill=C["grey_sh"]); d.line([(0, WALL_TOP), (W, WALL_TOP)], fill=INK)
    for x in range(0, W, 4):
        for y in range(WALL_TOP + 6, DESK_Y, 4):
            if (x // 4 + y // 4) % 2:
                d.point((x, y), fill=C["stone_sh"])
    d.line([(160, WALL_TOP + 4), (160, DESK_Y)], fill=C["stone_sh"])
    # pinned up: a calendar, a note, a certificate
    d.rectangle((4, 44, 28, 72), fill=C["white"], outline=INK); d.rectangle((4, 44, 28, 51), fill=C["red"])
    for i in range(12):
        d.point((8 + (i % 4) * 5, 56 + (i // 4) * 5), fill=C["grey"])
    d.rectangle((12, 60, 15, 63), outline=C["red"])
    d.rectangle((292, 50, 312, 68), fill=C["yellow"], outline=INK)
    d.line([(295, 55), (308, 55)], fill=C["brown_sh"]); d.line([(295, 59), (305, 59)], fill=C["brown_sh"])
    d.line([(295, 63), (309, 63)], fill=C["brown_sh"])
    d.rectangle((288, 78, 316, 100), fill=C["paper"], outline=C["gold_sh"])
    d.ellipse((298, 84, 306, 92), fill=C["gold"]); d.line([(292, 96), (312, 96)], fill=C["grey"])
    # the desk
    d.rectangle((0, DESK_Y, W, H), fill=C["cream"])
    d.line([(0, DESK_Y), (W, DESK_Y)], fill=INK); d.rectangle((0, DESK_Y + 1, W, DESK_Y + 2), fill=C["white"])
    # the monitors
    for x0, y0, x1, y1 in (MAIN, SECOND):
        d.rectangle((x0 - 4, y0 - 4, x1 + 3, y1 + 6), fill=C["black"], outline=INK)
        d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=C["bg"])
        cx = (x0 + x1) // 2
        d.rectangle((cx - 5, y1 + 7, cx + 5, DESK_Y - 3), fill=C["grey_sh"], outline=INK)
        d.rectangle((cx - 16, DESK_Y - 3, cx + 16, DESK_Y), fill=C["grey_sh"], outline=INK)
        d.point((x1 - 2, y1 + 3), fill=C["ok"])
    # on the desk: the keyboard, the mouse, a mug, a plant that has given up
    d.rectangle((44, DESK_Y + 8, 112, DESK_Y + 18), fill=C["grey_hi"], outline=INK)
    for x in range(47, 110, 4):
        for y in (DESK_Y + 10, DESK_Y + 13, DESK_Y + 16):
            d.point((x, y), fill=C["grey_sh"])
    d.ellipse((214, DESK_Y + 9, 224, DESK_Y + 19), fill=C["grey_hi"], outline=INK)
    d.rectangle((16, DESK_Y - 8, 28, DESK_Y + 6), fill=C["white"], outline=INK)                 # the mug
    d.arc((26, DESK_Y - 5, 34, DESK_Y + 3), 270, 90, fill=INK); d.line([(18, DESK_Y - 6), (26, DESK_Y - 6)], fill=C["brown_sh"])
    d.rectangle((296, DESK_Y - 6, 310, DESK_Y + 6), fill=C["orange_sh"], outline=INK)            # the plant's pot
    d.line([(303, DESK_Y - 6), (300, DESK_Y - 18)], fill=C["brown"]); d.line([(303, DESK_Y - 6), (308, DESK_Y - 14)], fill=C["brown"])
    d.point((299, DESK_Y - 19), fill=C["green_sh"]); d.point((309, DESK_Y - 15), fill=C["brown_hi"])
    return img


@lru_cache(maxsize=1)
def worker():
    """Whoever sits here, from behind: we never see their face, and neither does the boss."""
    f = Canvas(96, 70)
    f.poly([(6, 69), (10, 48), (26, 38), (70, 38), (86, 48), (90, 69)], "blue_sh")           # shoulders, in a work shirt
    f.line([(48, 40), (48, 69)], "night")
    f.rect((38, 30, 58, 42), "hskin_sh")                                                    # the neck
    f.ell((28, 2, 68, 38), "brown_sh")                                                      # the back of a head
    f.line([(34, 12), (40, 6), (52, 4)], "brown")
    f.rect((24, 18, 29, 28), "hskin_sh"); f.rect((67, 18, 72, 28), "hskin_sh")              # the ears
    return f.done()


@lru_cache(maxsize=1)
def boss():
    """The boss, from the chest up, as he shows above the cubicle wall: looking right at you."""
    f = Canvas(40, 40)
    f.poly([(2, 39), (5, 26), (14, 22), (26, 22), (35, 26), (38, 39)], "grey_sh")           # the suit
    f.poly([(16, 22), (24, 22), (20, 30)], "white"); f.poly([(19, 24), (21, 24), (22, 34), (20, 37), (18, 34)], "red")
    f.rect((15, 16, 25, 23), "askin_sh")
    f.ell((10, 0, 30, 20), "askin")                                                         # bald, and proud of it
    f.rect((9, 9, 11, 13), "askin"); f.rect((29, 9, 31, 13), "askin")
    f.line([(11, 5), (13, 3)], "grey"); f.line([(29, 5), (27, 3)], "grey")
    f.rect((14, 9, 17, 10), "ink"); f.rect((23, 9, 26, 10), "ink")                          # the eyes
    f.line([(13, 7), (18, 8)], "ink"); f.line([(27, 7), (22, 8)], "ink")
    f.line([(16, 15), (24, 15)], "mouth")
    f.rect((16, 12, 24, 13), "grey_sh")                                                     # a moustache
    return f.done()


def mute_icon(img, x, y, n=1, color="live"):
    """A speaker, struck out."""
    d = ImageDraw.Draw(img)
    d.rectangle((x, y + 3 * n, x + 2 * n, y + 6 * n), fill=C["white"], outline=INK)
    d.polygon([(x + 2 * n, y + 3 * n), (x + 6 * n, y), (x + 6 * n, y + 9 * n), (x + 2 * n, y + 6 * n)], fill=C["white"], outline=INK)
    d.line([(x + 8 * n, y + 2 * n), (x + 12 * n, y + 7 * n)], fill=C[color], width=n)
    d.line([(x + 12 * n, y + 2 * n), (x + 8 * n, y + 7 * n)], fill=C[color], width=n)


def draw(world, stream_img, t, muted=True, minimized=0.0, boss_x=None, typing=False, alert=0.0, cursor=None):
    """The desk at time t. `minimized` 0 -> 1 drops the stream into the taskbar and puts a second spreadsheet
    up; `boss_x` is where the boss's head is above the wall (None: he's elsewhere); `typing` makes the
    occupant look busy; `alert` 0 -> 1 sits them bolt upright."""
    world.paste(backdrop(), (0, 0))
    d = ImageDraw.Draw(world)
    if boss_x is not None:                                                # behind the wall: only his top half shows
        b = boss()
        y = WALL_TOP - 30 + int(2 * abs(math.sin(t * 7)))                 # walking
        part = b.crop((0, 0, 40, WALL_TOP - y))
        world.paste(part, (int(boss_x) - 20, y), part)
    x0, y0, x1, y1 = MAIN
    world.paste(sheet_pic(x1 - x0, y1 - y0), (x0, y0))
    d = ImageDraw.Draw(world)
    if cursor is not None or typing:                                      # the cell being filled in
        k = int(t * 6) % 5 if typing else cursor
        cx, cy = x0 + 10 + 16 * (k % 4), y0 + 14 + 6 * (2 + k % 3)
        d.rectangle((cx, cy, cx + 16, cy + 6), outline=C["green"])
    x0, y0, x1, y1 = SECOND
    mini = stream_img.crop((1, 0, W - 1, H)).resize((x1 - x0, y1 - y0), Image.BOX)
    if minimized <= 0:
        world.paste(mini, (x0, y0))
    else:
        world.paste(sheet_pic(x1 - x0, y1 - y0, 1, "BUDGET_2027"), (x0, y0))
        if minimized < 1:                                                 # on its way down to the taskbar
            k = 1 - minimized
            w, h = max(8, int((x1 - x0) * k)), max(5, int((y1 - y0) * k))
            small = mini.resize((w, h), Image.NEAREST)
            world.paste(small, (x0 + 4 + int((x1 - x0 - 8 - w) * minimized * 0.1), y1 - 7 - h + int(4 * minimized)))
        d = ImageDraw.Draw(world)
        d.rectangle((x0, y1 - 7, x1 - 1, y1 - 1), fill=C["bar"])           # the taskbar, and what's hiding in it
        d.rectangle((x0 + 3, y1 - 6, x0 + 7, y1 - 2), fill=C["hasan"]); d.rectangle((x0 + 9, y1 - 6, x0 + 13, y1 - 2), fill=C["asmon"])
    d = ImageDraw.Draw(world)
    if muted and minimized <= 0:
        mute_icon(world, x1 - 17, y1 - 13)
    w = worker()
    wy = H - 84 - int(round(5 * alert))
    world.paste(w, (112, wy), w)
    if typing:                                                            # keys going down
        for i in range(3):
            kx = 47 + 4 * int(rnd("key", int(t * 14), i) * 16)
            d.point((kx, DESK_Y + 10 + 3 * (i % 3)), fill=C["white"])
