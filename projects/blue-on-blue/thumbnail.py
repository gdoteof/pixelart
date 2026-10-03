"""YouTube thumbnails (1280x720) in the video's pixel style:

    uv run python projects/blue-on-blue/thumbnail.py      # -> thumbs/

Three variants for YouTube Studio's Test & Compare, plus a sheet showing each one at the sizes YouTube
displays them. The world is 320x180, so 1280x720 is an exact 4x and every pixel stays square.
"""
from pathlib import Path

from PIL import Image, ImageDraw

import props as P
import studio
from characters import figure
from engine import C, INK, PRESS, PRESS16, H, W, mirror, scaled, text_width
from pixelart import fx, pixel
from pixelart.camera import Cam, compose

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
BASE = FINAL[0] // W                     # 4: the whole world fills the thumbnail
PRESS24 = pixel.font(size=24)


def view():
    return Cam(W / 2, H / 2, BASE, world=(W, H), out=FINAL)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def bust(who, scale, facing, w=64, h=60, tears=False, hat=None, **pose):
    """Head and shoulders, cropped from the seated figure and scaled up. Drawn facing right and mirrored
    for facing=-1, like the video's figures. `hat` is a sprite set on the head."""
    spr, a = figure(who, facing=1, phones=False, **pose)
    spr = spr.copy()
    hx, hy = a["head"]
    if hat is not None:
        spr.alpha_composite(hat, (hx - hat.width // 2, max(0, hy - hat.height + 6)))
    if tears:
        ex, ey = a["eye"]
        d = ImageDraw.Draw(spr)
        d.line([(ex, ey + 2), (ex, ey + 8)], fill=C["tear"])
        d.point((ex, ey + 10), fill=C["tear"])
    x0, y0 = int(hx - w / 2 + 6), int(hy - 6 - (6 if hat is not None else 0))
    out = scaled(spr.crop((x0, y0, x0 + w, y0 + h)), scale)
    return out if facing > 0 else mirror(out)


def plate(ui, cx, y, s, bg, fg=C["white"], fnt=PRESS16):
    """A name plate in the arcade font, centred on cx."""
    tw = text_width(s, fnt)
    x0 = cx - tw // 2 - 5
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + tw + 10, y + fnt.size + 6), fill=INK)
    d.rectangle((x0, y, x0 + tw + 9, y + fnt.size + 5), fill=bg)
    pixel.text(ui, (x0 + 5, y + 3), s, fnt, fg, shadow=None)


def room(word="IS", color=None):
    world = studio.backdrop().copy()
    studio.ring_light(world, 1.0)
    studio.onair(world, True)
    if word:
        studio.neon(world, word, True, color)
    return world


def framed(ui, pic, x, y, caption=None):
    """A picture in the broadcast inset's lit frame, with a caption tab."""
    d = ImageDraw.Draw(ui)
    x1, y1 = x + pic.width, y + pic.height
    d.rectangle((x - 2, y - 2, x1 + 1, y1 + 1), fill=INK)
    d.rectangle((x - 1, y - 1, x1, y1), fill=C["neon_glow"])
    ui.paste(pic.convert("RGBA"), (x, y))
    if caption:
        tw = text_width(caption, PRESS) + 6
        d.rectangle((x - 1, y1 + 1, x + tw, y1 + 11), fill=INK)
        d.rectangle((x, y1 + 2, x + tw - 1, y1 + 10), fill=C["blue_sh"])
        pixel.text(ui, (x + 3, y1 + 3), caption, PRESS, C["white"], shadow=None)


# --- A: the love triangle ---------------------------------------------------------------------------

def thumb_triangle():
    """Donnie on the phone, calling the mayor handsome: the guest smitten, the host jealous."""
    world = room(None)
    newsom = bust("newsom", 2, 1, arms="cross", eyes="side", brows="angry", mouth="grit")
    mamdani = bust("mamdani", 2, -1, arms="chest", eyes="heart", brows="up", mouth="grin", flush=1)
    world.paste(newsom, (-6, H - newsom.height + 2), newsom)
    world.paste(mamdani, (W - mamdani.width + 6, H - mamdani.height + 2), mamdani)
    ui = blank()
    framed(ui, P.trump_call(arms="acc1", mouth="open", eyes="squint"), 118, 64, "DONNIE <3")
    P.word_pop(ui, W // 2, 36, "HANDSOME!", 1.0, size=16)
    fx.big_text(ui, (W // 2, 4), "BLUE ON BLUE", PRESS24, top=C["white"], bottom=C["neon"], anchor="ma")
    plate(ui, 56, 156, "NEWSOM", C["blazer_sh"])
    plate(ui, 262, 156, "MAMDANI", C["mtie_sh"])
    return world, ui, view()


# --- B: Newscum ------------------------------------------------------------------------------------

def thumb_newscum():
    """The host, stamped NEWSCUM; the guest, crowned and laughing."""
    world = room()
    newsom = bust("newsom", 3, 1, arms="clasp", eyes="wide", brows="worried", mouth="o", tears=True)
    mamdani = bust("mamdani", 2, -1, arms="chest", eyes="shut", brows="up", mouth="grin", hat=P.crown())
    world.paste(mamdani, (W - mamdani.width + 10, H - mamdani.height), mamdani)
    world.paste(newsom, (-34, H - newsom.height + 4), newsom)
    ui = blank()
    fx.stamp(ui, 92, 112, "NEWSCUM", PRESS24, C["red"], angle=-10)
    P.word_pop(ui, 244, 18, "HANDSOME!", 1.0, size=16)
    return world, ui, view()


# --- C: This Was Gavin Newsom --------------------------------------------------------------------------

def thumb_was():
    """The neon sign, now in the past tense: the host in tears under it, the guest delighted."""
    world = room(None)
    sign = scaled(studio.neon_sign("WAS", True, C["neon_red"]), 2)
    newsom = bust("newsom", 2, 1, arms="clasp", eyes="half", brows="worried", mouth="frown", tears=True)
    mamdani = bust("mamdani", 2, -1, arms="desk", eyes="shut", brows="up", mouth="grin")
    world.paste(newsom, (-6, H - newsom.height), newsom)
    world.paste(mamdani, (W - mamdani.width + 6, H - mamdani.height), mamdani)
    ui = blank()
    ui.alpha_composite(sign, (W // 2 - sign.width // 2, 17))
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
    for name, fn in (("A_triangle", thumb_triangle), ("B_newscum", thumb_newscum), ("C_was", thumb_was)):
        img = compose(*fn())
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
