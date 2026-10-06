"""The call: two webcam tiles with ChatGPT's window between them, in a dark call app.

World layout (320x180):
    TILE["felix"]   (4, 13, 104, 133)     Felix's webcam: his room at night, the server rack, the chair
    SCREEN          (108, 13, 212, 133)   ChatGPT's window; PIC = (110, 25, 210, 121) is the picture it shows
    TILE["sam"]     (216, 13, 316, 133)   Sam's webcam: his office by day, the window, the motto
    the top bar     y 0-10 (UI)           the lower third: y 136-167 (UI)        the controls: y 170-179 (UI)

Each tile is drawn on its own TW x TH canvas, so nothing leaks out of it, and pasted into the world. Inside
a tile the figure's canvas sits at FIG and the desk's far edge is at DESK_Y.
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

from characters import orb
from engine import C, INK, W, Canvas, blend, col, dither_rect, picture, rgba, rnd, silk, silk_w, vgrad
from pixelart import pixel

TW, TH = 100, 120
TILE = {"felix": (4, 13, 104, 133), "sam": (216, 13, 316, 133)}
SCREEN = (108, 13, 212, 133)
PIC = (110, 25, 210, 121)
PW, PH = PIC[2] - PIC[0], PIC[3] - PIC[1]
FIG = (8, 24)                       # where a figure's canvas goes in its tile
DESK_Y = 100
FACING = {"felix": 1, "sam": -1}    # both turned towards the middle of the call
ACCENT = {"felix": "felix", "sam": "sam", "gpt": "gpt_glow", "ajax": "ajax"}
RACK = (3, 34, 19, 99)              # Odysseus, in Felix's room
DOOR = (60, 22, 96, 100)            # the doorway behind Sam's shoulder (a gag opens it)


# --- Felix's room -------------------------------------------------------------------------------

def pug(d, x, y):
    """Edgar, asleep on the shelf."""
    d.ellipse((x, y + 2, x + 13, y + 9), fill=C["cream"], outline=INK)
    d.ellipse((x + 9, y, x + 16, y + 7), fill=C["cream"], outline=INK)
    d.rectangle((x + 13, y + 3, x + 16, y + 6), fill=C["black"])
    d.point((x + 12, y + 3), fill=INK)
    d.polygon([(x + 9, y), (x + 10, y - 2), (x + 12, y + 1)], fill=C["brown_sh"])


@lru_cache(maxsize=1)
def felix_room():
    """Felix's room behind him (RGB, TW x TH): the wall, a paper lantern, the play button, the pug, the rack
    called Odysseus and the gaming chair."""
    img, d = picture(TW, TH, "room")
    vgrad(img, (0, 0, TW, DESK_Y), "room_hi", "room", steps=5)
    d = ImageDraw.Draw(img)
    d.line([(0, 1), (TW, 1)], fill=C["led_p"])                           # an LED strip along the ceiling
    dither_rect(img, (0, 2, TW, 9), C["led_p"], density=0.3, blend=0.35)
    d = ImageDraw.Draw(img)
    d.line([(31, 2), (31, 6)], fill=INK)                                 # the lantern
    d.ellipse((23, 6, 39, 24), fill=C["shoji"], outline=INK)
    for y in (10, 14, 18):
        d.line([(25, y), (37, y)], fill=C["shoji_sh"])
    d.line([(29, 7), (33, 7)], fill=C["wood"]); d.line([(29, 23), (33, 23)], fill=C["wood"])
    d.rectangle((70, 9, 94, 29), fill=C["gold_sh"], outline=INK)         # the play button, framed
    d.rectangle((72, 11, 92, 27), fill=C["black"])
    d.rounded_rectangle((76, 14, 88, 24), 2, fill=C["red"])
    d.polygon([(80, 16), (80, 22), (85, 19)], fill=C["white"])
    d.line([(64, 52), (98, 52)], fill=C["wood_hi"]); d.line([(64, 53), (98, 53)], fill=C["wood_sh"])   # the shelf
    pug(d, 74, 42)
    x0, y0, x1, y1 = RACK                                                # the rack
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK)
    d.rectangle(RACK, fill=C["rack"])
    for y in range(y0 + 1, y1 - 6, 9):
        d.rectangle((x0 + 1, y, x1 - 1, y + 7), fill=C["rack_hi"])
        d.line([(x0 + 2, y + 5), (x1 - 2, y + 5)], fill=C["rack"])
    # the chair: the headrest behind his head, the wings and the red stripes down the back
    d.rounded_rectangle((21, 60, 73, TH + 6), 8, fill=C["chair"], outline=INK)
    d.rounded_rectangle((31, 36, 65, 66), 6, fill=C["chair"], outline=INK)
    d.rectangle((24, 68, 27, TH), fill=C["chair_red"]); d.rectangle((67, 68, 70, TH), fill=C["chair_red"])
    d.rectangle((34, 39, 36, 62), fill=C["chair_red"]); d.rectangle((60, 39, 62, 62), fill=C["chair_red"])
    d.line([(33, 38), (63, 38)], fill=C["chair_hi"]); d.line([(23, 63), (71, 63)], fill=C["chair_hi"])
    d.rectangle((29, 68, 65, TH), fill=C["chair_sh"])
    return img


def rack_lights(img, t, lit=False):
    """The rack's LEDs, blinking; `lit` turns them all on."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = RACK
    for i, y in enumerate(range(y0 + 1, y1 - 6, 9)):
        for j in range(4):
            on = lit or rnd("led", i, j, int(t * 5 + i)) < 0.55
            color = (C["led_g"], C["led_c"], C["led_g"], C["led_r"])[j] if on else C["rack"]
            d.point((x0 + 3 + 3 * j, y + 2), fill=color)
    if lit:
        blend(img, pixel.mask(lambda m: m.rectangle((x0 - 3, y0 - 3, x1 + 3, y1 + 3), fill=255), img.size), "led_c", 0.25)


@lru_cache(maxsize=1)
def felix_desk():
    """What stands in front of Felix: the desk, the keyboard's glow, the mic on its arm."""
    f = Canvas(TW, TH)
    f.rect((0, DESK_Y, TW, TH), "fdesk")
    f.line([(0, DESK_Y), (TW, DESK_Y)], "fdesk_hi")
    for i, x in enumerate(range(24, 62, 3)):                             # the keyboard: one lit row of keys
        f.px((x, DESK_Y + 4), ("led_r", "led_p", "led_c", "led_g")[i % 4])
    f.line([(23, DESK_Y + 6), (62, DESK_Y + 6)], "rack_hi")
    f.line([(TW, 94), (88, 86)], "phones", w=2)                          # the boom arm
    f.rect((78, 80, 89, 88), "phones")                                   # the mic
    f.ell((74, 80, 81, 88), "grey_sh")
    f.line([(76, 82), (76, 86)], "grey_hi"); f.line([(78, 82), (78, 86)], "grey")
    f.px((87, 82), "felix")
    return f.done()


# --- Sam's office ---------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def sam_office():
    """Sam's office behind him (RGB, TW x TH): the window on the city, a motto, the shelf with the plant."""
    img, d = picture(TW, TH, "wall")
    vgrad(img, (0, 0, TW, DESK_Y), "wall_hi", "wall", steps=4)
    d = ImageDraw.Draw(img)
    d.rectangle((3, 9, 36, 61), fill=C["white"], outline=INK)           # the window
    vgrad(img, (5, 11, 35, 60), "window_hi", "window", steps=4)
    d = ImageDraw.Draw(img)
    for x, top in ((6, 44), (11, 38), (16, 47), (21, 34), (27, 42), (31, 50)):
        d.rectangle((x, top, x + 4, 59), fill=C["city"] if (x // 5) % 2 else C["city_sh"])
        d.point((x + 1, top + 3), fill=C["window_hi"]); d.point((x + 3, top + 7), fill=C["window_hi"])
    d.line([(20, 10), (20, 60)], fill=C["white"]); d.line([(4, 34), (35, 34)], fill=C["white"])
    d.rectangle((2, 61, 37, 63), fill=C["wall_hi"], outline=INK)        # the sill
    d.rectangle((64, 8, 96, 30), fill=C["board"], outline=INK)          # the motto on the wall
    silk(img, (80, 12), "AGI", "ink", anchor="ma")
    silk(img, (80, 20), "SOON", "sam_sh", anchor="ma")
    d.line([(60, 56), (TW, 56)], fill=C["wall_hi"]); d.line([(60, 57), (TW, 57)], fill=C["wall_sh"])   # the shelf
    d.polygon([(87, 55), (86, 47), (96, 47), (95, 55)], fill=C["pot"], outline=INK)                    # the plant
    for lx, ly in ((88, 40), (94, 38), (91, 33), (85, 36), (97, 43)):
        d.ellipse((lx - 3, ly - 3, lx + 3, ly + 3), fill=C["plant"], outline=INK)
        d.point((lx - 1, ly - 1), fill=C["plant_hi"])
    d.rounded_rectangle((27, 62, 79, TH + 6), 7, fill=C["mesh"], outline=INK)                          # his chair
    for y in range(66, TH, 3):
        d.line([(30, y), (76, y)], fill=C["mesh_sh"])
    return img


@lru_cache(maxsize=1)
def sam_desk():
    """What stands in front of Sam: a white desk and a mug."""
    f = Canvas(TW, TH)
    f.rect((0, DESK_Y, TW, TH), "sdesk")
    f.line([(0, DESK_Y), (TW, DESK_Y)], "white")
    f.line([(0, DESK_Y + 9), (TW, DESK_Y + 9)], "sdesk_sh")
    f.rect((84, 92, 92, 102), "white"); f.ell((90, 94, 96, 100), "white")
    f.d.ellipse((91, 95, 95, 99), fill=(0, 0, 0, 0))
    f.line([(85, 93), (91, 93)], "brown_sh")
    f.px((88, 97), "sam")
    return f.done()


BUTTON = (16, 100)                  # the middle of the ban button's foot, on Sam's desk


def ban_button(img, pressed=False):
    """The button on Sam's desk. It bans people."""
    d = ImageDraw.Draw(img)
    x, y = BUTTON
    if pressed:
        for dx, dy in ((-11, -14), (-13, -9), (11, -14), (13, -9), (0, -19)):                  # it lights up
            d.line([(x + dx, y + dy), (x + dx + (dx > 0) - (dx < 0), y + dy - 1)], fill=C["live"])
        d.ellipse((x - 6, y - 11, x + 6, y - 5), fill=C["red_hi"], outline=INK)
    else:
        d.ellipse((x - 6, y - 15, x + 6, y - 5), fill=C["red"], outline=INK)
        d.point((x - 3, y - 12), fill=C["red_hi"]); d.point((x - 2, y - 13), fill=C["red_hi"])
    d.rectangle((x - 9, y - 8, x + 9, y), fill=C["black"], outline=INK)
    silk(img, (x + 1, y - 6), "BAN", "warn", anchor="ma")


ROOM = {"felix": felix_room, "sam": sam_office}
DESK = {"felix": felix_desk, "sam": sam_desk}


# --- the tiles ----------------------------------------------------------------------------------------

def name_plate(tile, name, color, level=0.0, muted=False):
    """The participant's name along the bottom of a tile, with a level meter when they speak."""
    d = ImageDraw.Draw(tile)
    w = silk_w(name) + 17
    d.rectangle((2, TH - 12, 2 + w, TH - 3), fill=C["bg"])
    d.rectangle((2, TH - 12, 4, TH - 3), fill=col(color))
    if muted:                                                            # a mic, struck out
        d.rectangle((8, TH - 10, 9, TH - 7), fill=C["live"]); d.line([(6, TH - 5), (11, TH - 10)], fill=C["live"])
    else:
        for i in range(3):                                               # three bars that jump with the voice
            h = 1 + int(round(level * (4, 6, 3)[i] * (0.6 + 0.4 * math.sin(i * 2.1 + level * 9))))
            d.rectangle((7 + 2 * i, TH - 5 - min(5, max(0, h)), 7 + 2 * i, TH - 5), fill=col(color) if level > 0.1 else C["mute"])
    silk(tile, (15, TH - 10), name, "text")


def frame_tile(world, who, speaking=False, color=None):
    """A tile's border in the world: thin and grey, or thick and in the speaker's colour."""
    d = ImageDraw.Draw(world)
    x0, y0, x1, y1 = TILE[who] if who in TILE else SCREEN
    d.rectangle((x0 - 1, y0 - 1, x1, y1), outline=C["line"])
    if speaking:
        c0 = col(color or ACCENT[who])
        d.rectangle((x0 - 1, y0 - 1, x1, y1), outline=c0)
        d.rectangle((x0 - 2, y0 - 2, x1 + 1, y1 + 1), outline=c0)
    for cx, cy in ((x0 - 1 - speaking, y0 - 1 - speaking), (x1 + speaking, y0 - 1 - speaking),
                   (x0 - 1 - speaking, y1 + speaking), (x1 + speaking, y1 + speaking)):
        d.point((cx, cy), fill=C["bg"])                                  # rounded corners


def greyed(tile, amount=1.0):
    """A tile with its colour drained and dimmed: a camera that has been cut off."""
    g = tile.convert("L").convert("RGB")
    out = Image.blend(tile, g, amount)
    return Image.blend(out, Image.new("RGB", out.size, C["bg"]), 0.45 * amount)


# --- ChatGPT's window -------------------------------------------------------------------------------

@lru_cache(maxsize=64)
def idle_pic(mood="happy", talk=0, ring=0, kind="gpt", dots=0):
    """What the window shows when nothing is shared: the assistant, listening."""
    img, d = picture(PW, PH, "panel")
    vgrad(img, (0, 0, PW, PH), "panel_hi", "panel", steps=4)
    o = orb(15, mood, talk, kind, ring)
    img.paste(o, (PW // 2 - o.width // 2, 40 - o.height // 2), o)
    d = ImageDraw.Draw(img)
    for i in range(3):                                                   # the listening dots
        on = dots % 4 > i
        d.rectangle((PW // 2 - 7 + 6 * i, 70, PW // 2 - 5 + 6 * i, 72), fill=C["gpt_glow"] if on else C["line"])
    return img


def draw_screen(world, pic, title="CHATGPT", caption=None, speaking=False, kind="gpt"):
    """ChatGPT's window: the title bar, the picture it shows (PW x PH) and a caption under it."""
    d = ImageDraw.Draw(world)
    x0, y0, x1, y1 = SCREEN
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=C["panel"])
    d.rectangle((x0, y0, x1 - 1, y0 + 10), fill=C["bar"])
    o = orb(3, "open", 0, kind)
    world.paste(o, (x0 + 2, y0 + 1), o)
    silk(world, (x0 + 14, y0 + 3), title, "text")
    for i in range(3):
        d.point((x1 - 5 - 3 * i, y0 + 5), fill=C["mute"])
    px0, py0, px1, py1 = PIC
    d.rectangle((px0 - 1, py0 - 1, px1, py1), fill=C["bg"])
    if pic is not None:
        world.paste(pic.convert("RGB"), (px0, py0))
    if caption:
        silk(world, ((x0 + x1) // 2, py1 + 3), caption, "dim", anchor="ma")
    frame_tile(world, "screen", speaking, ACCENT[kind])


# --- the app around them ------------------------------------------------------------------------------

def clock(t):
    return f"{int(t) // 60:02d}:{int(t) % 60:02d}"


def draw_topbar(ui, t, title="GREAT QUESTION", people=3):
    d = ImageDraw.Draw(ui)
    d.rectangle((0, 0, W, 10), fill=rgba("bar"))
    if int(t * 2) % 2 == 0:
        d.ellipse((5, 3, 8, 6), fill=rgba("live"))
    silk(ui, (11, 3), "REC " + clock(t), "dim")
    silk(ui, (W // 2, 3), title, "text", anchor="ma")
    s = f"{people} IN CALL"
    silk(ui, (W - 5, 3), s, "dim", anchor="ra")


@lru_cache(maxsize=None)
def control_icon(kind):
    f = Canvas(13, 11)
    f.d.rounded_rectangle((1, 1, 11, 9), 2, fill=rgba("live" if kind == "leave" else "panel_hi"))
    if kind == "mic":
        f.rect((5, 2, 7, 5), "text"); f.line([(4, 5), (4, 6), (8, 6), (8, 5)], "text"); f.px((6, 8), "text")
    elif kind == "cam":
        f.rect((3, 3, 7, 7), "text"); f.poly([(8, 5), (10, 3), (10, 7)], "text")
    elif kind == "share":
        f.rect((3, 3, 9, 7), "text"); f.rect((4, 4, 8, 6), "panel_hi"); f.line([(6, 6), (6, 4)], "ok")
    elif kind == "hand":
        f.rect((5, 4, 8, 8), "gold"); f.pxs([(5, 2), (6, 2), (7, 3), (8, 3)], "gold")
    else:                                                                # leave: a handset, hung up
        f.line([(3, 6), (4, 4), (8, 4), (9, 6)], "white"); f.px((3, 7), "white"); f.px((9, 7), "white")
    return f.img


def draw_controls(ui):
    d = ImageDraw.Draw(ui)
    d.rectangle((0, 169, W, 180), fill=rgba("bar"))
    x = W // 2 - 34
    for kind in ("mic", "cam", "share", "hand", "leave"):
        ui.alpha_composite(control_icon(kind), (x, 169))
        x += 14


def toast(ui, s, k=1.0, color="text", y=15):
    """A system message dropping in under the top bar (k from 0 to 1): "Felix was removed by the host"."""
    if k <= 0:
        return
    w = silk_w(s) + 10
    x0 = W // 2 - w // 2
    y0 = y - int(round((1 - min(1.0, k)) * 12))
    d = ImageDraw.Draw(ui)
    d.rounded_rectangle((x0 - 1, y0 - 1, x0 + w, y0 + 10), 3, fill=rgba("ink"))
    d.rounded_rectangle((x0, y0, x0 + w - 1, y0 + 9), 3, fill=rgba("bar"))
    silk(ui, (W // 2, y0 + 2), s, color, anchor="ma")


if __name__ == "__main__":
    from characters import figure
    from engine import H, ROOT, scaled
    world = Image.new("RGB", (W, H), C["bg"])
    for who, arms in (("felix", "bro"), ("sam", "steeple")):
        tile = ROOM[who]().copy()
        if who == "felix":
            rack_lights(tile, 1.3)
        spr, a = figure(who, arms, facing=FACING[who], mouth="grin" if who == "felix" else "smile", lean=1)
        tile.paste(spr, FIG, spr)
        tile.paste(DESK[who](), (0, 0), DESK[who]())
        name_plate(tile, "PEWDIEPIE" if who == "felix" else "SAM ALTMAN", ACCENT[who], 0.7 if who == "felix" else 0)
        world.paste(tile, TILE[who][:2])
        frame_tile(world, who, who == "felix")
    draw_screen(world, idle_pic("happy", 0, 0, "gpt", 2), caption="LISTENING")
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_topbar(ui, 83.0)
    draw_controls(ui)
    toast(ui, "FELIX WAS REMOVED BY THE HOST", 1.0, "live")
    world.paste(ui, (0, 0), ui)
    out = ROOT / "build" / "call.png"
    scaled(world, 6).save(out)
    print(out)
