"""YouTube thumbnails (1280x720) in the video's pixel style:

    uv run python projects/pardon-me/thumbnail.py      # -> thumbs/

Three variants for YouTube Studio's Test & Compare, plus a sheet showing each one at the sizes YouTube
displays them. The world is 320x180, so 1280x720 is an exact 4x and every pixel stays square.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

import art
import hall
import video as V
from characters import figure
from engine import C, INK, PRESS, PRESS16, PRESS24, SILK, H, W, mix, scaled, text_width
from pixelart import pixel
from pixelart.camera import Cam, compose
from props import big_text, burst, stamp

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
BASE = FINAL[0] // W                     # 4: the whole world fills the thumbnail


def view():
    return Cam(W / 2, H / 2, BASE, world=(W, H), out=FINAL)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def bust(who, scale, facing, w=34, h=36, **pose):
    """Head and shoulders, cropped from the full figure and scaled up."""
    spr, a = figure(who, facing, **pose)
    hx, hy = a["head"]
    x0, y0 = int(hx - w / 2), int(hy - 12)
    return scaled(spr.crop((x0, y0, x0 + w, y0 + h)), scale)


def plate(ui, cx, y, s, bg, fg=C["white"], fnt=PRESS16):
    """A name plate in the arcade font, centred on cx."""
    tw = text_width(s, fnt)
    x0 = cx - tw // 2 - 5
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + tw + 10, y + fnt.size + 6), fill=INK)
    d.rectangle((x0, y, x0 + tw + 9, y + fnt.size + 5), fill=bg)
    pixel.text(ui, (x0 + 5, y + 3), s, fnt, fg, shadow=None)


def title(ui, s, y=4, fnt=PRESS24):
    big_text(ui, (W // 2, y), s, fnt, top=C["white"], bottom=C["gold_hi"], anchor="ma")


# --- A: the booking photos ----------------------------------------------------------------------------

def booking_wall(img, x0, x1):
    """A booking-photo height chart: pale wall, a rule every 12 px, feet marked on the left."""
    d = ImageDraw.Draw(img)
    d.rectangle((x0, 0, x1, H), fill=(184, 194, 210))
    for k, y in enumerate(range(H - 8, 0, -12)):                     # a rule every 3 inches from 4'0"
        d.line([(x0, y), (x1, y)], fill=(132, 142, 164) if k % 2 else (156, 166, 186))
        inches = 48 + 3 * k
        if k % 2 == 0 and y > 40:
            pixel.text(img, (x0 + 3, y - 7), f"{inches // 12}'{inches % 12}", SILK, (110, 120, 142), shadow=None)


def booking_board(ui, cx, y, top, bottom):
    """The board held under the chin: a name in white, the charge in gold."""
    w = max(text_width(top, PRESS16), text_width(bottom, PRESS)) + 14
    x0 = cx - w // 2
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + w, y + 31), fill=INK)
    d.rectangle((x0, y, x0 + w - 1, y + 30), fill=(30, 32, 40))
    d.rectangle((x0 + 2, y + 2, x0 + w - 3, y + 28), outline=(70, 72, 84))
    pixel.text(ui, (cx, y + 4), top, PRESS16, C["white"], shadow=None, anchor="ma")
    pixel.text(ui, (cx, y + 21), bottom, PRESS, C["gold_hi"], shadow=None, anchor="ma")


def thumb_mugshots():
    """Two booking photos side by side under PARDON ME?: the whole video in one look."""
    world = Image.new("RGB", (W, H))
    booking_wall(world, 0, W // 2 - 1)
    booking_wall(world, W // 2, W)
    ImageDraw.Draw(world).rectangle((W // 2 - 2, 0, W // 2 + 1, H), fill=INK)
    trump = bust("trump", 4, 1, mouth="pout", brows="angry", eyes="squint")
    bibi = bust("bibi", 4, -1, mouth="frown", brows="angry", eyes="open")
    world.paste(trump, (W // 4 - trump.width // 2 + 2, H - trump.height + 8), trump)
    world.paste(bibi, (3 * W // 4 - bibi.width // 2 - 2, H - bibi.height + 8), bibi)
    ui = blank()
    title(ui, "PARDON ME?")
    booking_board(ui, W // 4, 144, "TRUMP", "34 COUNTS")
    booking_board(ui, 3 * W // 4, 144, "BIBI", "3 CASES")
    return world, ui, view()


# --- B: the face-off at the UN ----------------------------------------------------------------------------

def thumb_faceoff():
    """UN blue, the emblem behind, the two of them yelling at each other across a VS."""
    world = Image.new("RGB", (W, H), C["screen_bg"])
    d = ImageDraw.Draw(world)
    cx, cy = W // 2, 96
    for i in range(24):                                               # rays from the emblem
        a0, a1 = i * 2 * math.pi / 24, (i + 0.5) * 2 * math.pi / 24
        d.polygon([(cx, cy), (cx + 400 * math.cos(a0), cy + 400 * math.sin(a0)),
                   (cx + 400 * math.cos(a1), cy + 400 * math.sin(a1))], fill=mix(C["screen_bg"], C["screen_hi"], 0.35))
    hall.emblem(world, cx, cy, 46, fg=mix(C["screen_hi"], C["un"], 0.55), bg=mix(C["screen_bg"], C["screen_hi"], 0.5))
    trump = bust("trump", 4, 1, w=40, mouth="wide", brows="angry", eyes="squint", arm="point")
    bibi = bust("bibi", 4, -1, w=40, mouth="wide", brows="angry", eyes="open", arm="point")
    world.paste(trump, (-14, H - trump.height + 10), trump)
    world.paste(bibi, (W - bibi.width + 14, H - bibi.height + 10), bibi)
    ui = blank()
    title(ui, "UN RAP BATTLE", y=5, fnt=PRESS16)
    burst(ui, W // 2, 104, 17, 30, C["gold"], spikes=12, rot=0.2)
    burst(ui, W // 2, 104, 10, 19, C["white"], spikes=12, rot=0.45)
    big_text(ui, (W // 2, 96), "VS", PRESS16, top=C["red_hi"], bottom=C["red"], anchor="ma")
    plate(ui, 62, 150, "TRUMP", C["tie"])
    plate(ui, W - 62, 150, "BIBI", C["btie_sh"])
    return world, ui, view()


# --- C: the turkey pardon --------------------------------------------------------------------------------

def thumb_turkey():
    """The hall, and at the rostrum a turkey in Trump's hair asking for its pardon; Bibi holds the gavel."""
    world = hall.backdrop().copy()
    for frame in (hall.SCREEN_L, hall.SCREEN_R):                      # both screens on the UN Web TV slate
        x0, y0, x1, y1 = hall.screen_inner(frame)
        world.paste(V.feed_backdrop(x1 - x0, y1 - y0, frame is hall.SCREEN_L), (x0, y0))
    hall.president(world)
    hall.ledge_front(world)
    hall.rostrum(world, mics=True)
    turkey = scaled(art.turkey("trump", gobble=True), 3)
    world.paste(turkey, (W // 2 - turkey.width // 2 + 6, hall.ROSTRUM_TOP - turkey.height + 26), turkey)
    hall.rostrum(world, mics=False)
    bibi = bust("bibi", 3, -1, w=40, mouth="grin", brows="up", eyes="half", arm="up")
    world.paste(bibi, (W - bibi.width + 6, H - bibi.height + 4), bibi)
    ui = blank()
    title(ui, "PARDON ME?")
    stamp(ui, 100, 116, "DENIED", C["red"], angle=-14, size=24)
    return world, ui, view()


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
    for name, fn in (("A_mugshots", thumb_mugshots), ("B_faceoff", thumb_faceoff), ("C_turkey", thumb_turkey)):
        img = finish(*fn())
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
