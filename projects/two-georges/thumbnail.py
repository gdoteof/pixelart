"""YouTube thumbnails (1280x720) in the video's pixel style:

    uv run python projects/two-georges/thumbnail.py      # -> thumbs/

Three variants for YouTube Studio's Test & Compare, plus a sheet showing each one at the sizes YouTube
displays them. The world is 320x180, so 1280x720 is an exact 4x and every pixel stays square.
"""
from pathlib import Path

from PIL import Image, ImageDraw

import ships
import video as V
from characters import figure
from engine import C, INK, PRESS, PRESS16, PRESS24, H, W, paste, scaled, text_width
from gags_v2 import quarter_face
from pixelart.camera import Cam, compose
from props import big_text, burst
from scene import GEORGE_X, shores

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
BASE = FINAL[0] // W                     # 4: the whole world fills the thumbnail


def cam(cx, cy, zoom=1):
    return Cam(cx, cy, BASE * zoom, world=(W, H), out=FINAL)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def plate(ui, x, y, s, bg, fg, anchor="l"):
    """A name plate like the video's speaker chips, in the 8 px arcade font."""
    tw = text_width(s, PRESS)
    x0 = {"l": x, "m": x - tw // 2 - 4, "r": x - tw - 8}[anchor]
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + tw + 8, y + 12), fill=INK)
    d.rectangle((x0, y, x0 + tw + 7, y + 11), fill=bg)
    d.line([(x0 + 1, y + 1), (x0 + tw + 6, y + 1)], fill=fg)
    d.fontmode = "1"
    d.text((x0 + 4, y + 2), s, font=PRESS, fill=fg)


def title(ui, y=5):
    big_text(ui, (W // 2, y), "TWO GEORGES", PRESS24, anchor="ma")


def vs(ui, x, y):
    burst(ui, x, y, 17, 30, C["gold"], spikes=12, rot=0.2)
    burst(ui, x, y, 10, 19, C["white"], spikes=12, rot=0.45)
    big_text(ui, (x, y - 8), "VS", PRESS16, top=C["red"], bottom=C["flag_red"], anchor="ma")


# --- A: the face-off across the Atlantic ----------------------------------------------------------

def thumb_faceoff():
    """Both Georges three times life size, shouting across the ocean at sunset."""
    world = shores(31.0, 0.0, 0.0)
    V.mood_overlay(world, 0.18)                          # a touch darker, so the two of them pop
    w, _ = figure("washington", 1, rim=0.7, mic=True, mouth="wide", brows="angry", eyes="open", arm="point")
    g, _ = figure("george", -1, rim=0.7, mic=True, mouth="wide", brows="angry", eyes="open", arm="point")
    w, g = scaled(w, 3), scaled(g, 3)
    world.paste(w, (-8, 46), w)                          # heads just below the two flags
    world.paste(g, (W - g.width + 8, 46), g)
    ui = blank()
    title(ui)
    vs(ui, W // 2, 110)
    plate(ui, 6, 162, "GEORGE WASHINGTON", C["navy"], C["buff"])
    plate(ui, W - 6, 162, "KING GEORGE III", C["red"], C["gold"], anchor="r")
    return world, ui, cam(W / 2, H / 2)


# --- B: the sea battle ------------------------------------------------------------------------------

def thumb_duel():
    """Verse 4's ship duel: a broadside in flight between Alfred and Royal George, both Georges on deck."""
    c = V.Ctx(208.0)                                     # Alfred's broadside, a moment after it fires
    c.scene = "ships"
    c.ship = dict(rg=1, al=0, fires=False)
    ships.place(c)
    for who, facing in (("washington", 1), ("george", -1)):
        c.st[who].update(facing=facing, mic=True, mouth="wide", brows="angry", eyes="open", arm="point", rim=0.6)
    world = ships.world(c)
    c.world = world
    for who in ("washington", "george"):
        V.draw_char(c, world, who)
    ships.front(c)
    view = cam(161, 92, 2)                               # the gap between the two decks, 2x
    ui = blank()
    title(ui)
    vs(ui, W // 2, 96)
    return world, ui, view


# --- C: the quarter ---------------------------------------------------------------------------------

def thumb_quarter():
    """Verse 2's last line: the King finds Washington's face on the money."""
    world = shores(114.0, 0.0, 0.0)
    g, a = figure("george", -1, rim=0.6, mouth="o", eyes="wide", brows="worried", arm="palm", hat="askew", flush=1)
    world.paste(g, (GEORGE_X - a["feet"][0], 115 - a["feet"][1]), g)
    drop = V.sweat_drop()
    hx, hy = GEORGE_X - a["feet"][0] + a["head"][0], 115 - a["feet"][1] + a["head"][1]
    world.paste(drop, (int(hx) + 8, int(hy) - 7), drop)
    world.paste(drop, (int(hx) + 11, int(hy) - 2), drop)
    view = cam(226, 84, 2)
    ui = blank()
    coin = quarter_face(116)
    paste(ui, coin, 88, 98, "mm")
    big_text(ui, (W // 2, 6), "I'M THE CURRENCY", PRESS16, top=C["white"], bottom=C["buff"], anchor="ma")
    plate(ui, W - 6, 162, "KING GEORGE III", C["red"], C["gold"], anchor="r")
    return world, ui, view


# --- output --------------------------------------------------------------------------------------------

def finish(world, ui, view):
    return compose(world, ui, view)


def preview_sheet(thumbs):
    """Each thumbnail at YouTube's feed size (360 wide), sidebar size (168 wide) and a larger 400."""
    sheet = Image.new("RGB", (1000, 30 + 260 * len(thumbs)), (15, 15, 15))
    d = ImageDraw.Draw(sheet)
    for i, (name, img) in enumerate(thumbs):
        y = 30 + i * 260
        d.text((10, y - 20), name, fill=(240, 240, 240))
        sheet.paste(img.resize((360, 202), Image.LANCZOS), (10, y))
        sheet.paste(img.resize((168, 94), Image.LANCZOS), (390, y))
        sheet.paste(img.resize((400, 225), Image.LANCZOS), (580, y))
    return sheet


def main():
    OUT.mkdir(exist_ok=True)
    made = []
    for name, fn in (("A_faceoff", thumb_faceoff), ("B_duel", thumb_duel), ("C_quarter", thumb_quarter)):
        img = finish(*fn())
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
