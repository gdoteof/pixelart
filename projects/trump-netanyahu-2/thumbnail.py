"""YouTube thumbnails (1280x720) in the video's pixel style:

    uv run python projects/trump-netanyahu-2/thumbnail.py      # -> thumbs/

Three variants for YouTube Studio's Test & Compare, plus a sheet showing each one at the sizes YouTube
displays them. The world is 320x180, so 1280x720 is an exact 4x and every pixel stays square.
"""
from pathlib import Path

from PIL import Image, ImageDraw

import office
import props as P
from characters import GESTURES, figure
from engine import C, INK, PRESS16, H, W, mirror, scaled, text_width
from pixelart import fx, pixel
from pixelart.camera import Cam, compose

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
BASE = FINAL[0] // W                     # 4: the whole world fills the thumbnail
PRESS24 = pixel.font(size=24)
PRESS32 = pixel.font(size=32)


def view():
    return Cam(W / 2, H / 2, BASE, world=(W, H), out=FINAL)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


GUARD = (((10, 60), (18, 47), "fist"), ((70, 58), (64, 42), "fist"), "front")   # a boxer's guard, fists up


def bust(who, scale, facing, box=None, w=64, h=60, gloves=None, **pose):
    """Head and shoulders (and fists), cropped from the seated figure and scaled up: `box` in sprite pixels,
    or w x h around the head. Drawn facing right and mirrored for facing=-1, like the video's figures."""
    spr, a = figure(who, facing=1, **pose)
    spr = spr.copy()
    if gloves:
        g = P.glove(gloves)
        for k in ("hand_near", "hand_far"):
            x, y = a[k]
            spr.alpha_composite(g, (x - g.width // 2, y - g.height // 2 - 2))
    if box is None:
        hx, hy = a["head"]
        x0, y0 = int(hx - w / 2 + 6), int(hy - 6)
        box = (x0, y0, x0 + w, y0 + h)
    out = scaled(spr.crop(box), scale)
    return out if facing > 0 else mirror(out)


def plate(ui, cx, y, s, bg, fg=C["white"], fnt=PRESS16):
    """A name plate in the arcade font, centred on cx."""
    tw = text_width(s, fnt)
    x0 = cx - tw // 2 - 5
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + tw + 10, y + fnt.size + 6), fill=INK)
    d.rectangle((x0, y, x0 + tw + 9, y + fnt.size + 5), fill=bg)
    pixel.text(ui, (x0 + 5, y + 3), s, fnt, fg, shadow=None)


def title(ui, s, y=4, fnt=PRESS32, top=C["white"], bottom=C["gold_hi"]):
    fx.big_text(ui, (W // 2, y), s, fnt, top=top, bottom=bottom, anchor="ma")


def room():
    world = office.backdrop().copy()
    office.fire(world, 0)
    return world


# --- A: round two, gloves up ----------------------------------------------------------------------------

def thumb_round2():
    """The Oval Office, both men in boxing gloves, squared up and yelling at each other under ROUND 2."""
    GESTURES["guard"] = GUARD
    world = room()
    box = (10, 3, 72, 52)
    bibi = bust("bibi", 3, 1, box, gloves="blue", arms="guard", mouth="wide", brows="angry", eyes="open")
    trump = bust("trump", 3, -1, box, gloves="red", arms="guard", mouth="wide", brows="angry", eyes="open")
    world.paste(bibi, (-36, H - bibi.height), bibi)
    world.paste(trump, (W - trump.width + 36, H - trump.height), trump)
    ui = blank()
    title(ui, "ROUND 2", y=3)
    fx.burst(ui, W // 2, 108, 15, 27, C["gold"], spikes=12, rot=0.2)
    fx.burst(ui, W // 2, 108, 9, 17, C["white"], spikes=12, rot=0.45)
    fx.big_text(ui, (W // 2, 100), "VS", PRESS16, top=C["red_hi"], bottom=C["red"], anchor="ma")
    plate(ui, 48, 160, "BIBI", C["btie_sh"])
    plate(ui, W - 50, 160, "TRUMP", C["tie"])
    return world, ui, view()


# --- B: the handshake ------------------------------------------------------------------------------------

def thumb_handshake():
    """The close-up from the video: Bibi's big hand, Trump's tiny one, the yank, and both faces."""
    world = Image.new("RGB", (W, H), C["wall"])
    shake = scaled(P.handshake(46, pat=0.35), 4)
    world.paste(shake, (W // 2 - shake.width // 2, H - shake.height + 40))
    bibi = bust("bibi", 2, 1, arms="lap", mouth="o", brows="worried", eyes="wide", flush=1)
    trump = bust("trump", 2, -1, arms="lap", mouth="grin", brows="neutral", eyes="squint")
    world.paste(bibi, (-18, -14), bibi)
    world.paste(trump, (W - trump.width + 18, -14), trump)
    ui = blank()
    fx.big_text(ui, (176, 70), "YANK!", PRESS24, top=C["white"], bottom=C["gold_hi"], anchor="ma")
    title(ui, "ROUND 2", y=150, fnt=PRESS16)
    return world, ui, view()


# --- C: the turkey wins ----------------------------------------------------------------------------------

def thumb_turkey():
    """The decision: the turkey on the coffee table in the Nobel medal, both men's jaws on the floor."""
    world = room()
    tk = scaled(mirror(P.turkey("open", medal=True)), 3)
    world.paste(tk, (W // 2 - tk.width // 2, office.TABLE[1] - tk.height + 18), tk)
    bibi = bust("bibi", 2, 1, arms="shrug", mouth="wide", brows="up", eyes="wide")
    trump = bust("trump", 2, -1, arms="shrug", mouth="wide", brows="up", eyes="wide")
    world.paste(bibi, (-20, H - bibi.height + 6), bibi)
    world.paste(trump, (W - trump.width + 20, H - trump.height + 6), trump)
    ui = blank()
    title(ui, "NOBEL PEACE", y=4, fnt=PRESS24)
    title(ui, "PRIZE", y=30, fnt=PRESS24)
    fx.stamp(ui, W // 2, 156, "TURKEY WINS", PRESS16, C["red"], angle=-6)
    return world, ui, view()


# --- output --------------------------------------------------------------------------------------------

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
    for name, fn in (("A_round2", thumb_round2), ("B_handshake", thumb_handshake), ("C_turkey", thumb_turkey)):
        img = compose(*fn())
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
