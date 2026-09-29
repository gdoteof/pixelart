"""YouTube thumbnails (1280x720) in the video's pixel style: uv run python thumbnail.py

Writes three variants for YouTube Studio's Test & Compare, plus a preview sheet
showing each one at the sizes YouTube actually displays them.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import video as V
from characters import draw_character, render_head
from engine import GOLD, H, W, dither, mask, mix, text_width
from props import PRESS16, PRESS24, WHITE, big_text, keycap
from scene import CURSOR, K, PRESS, burst, draw_popup, health_bar

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
GREEN_BG, GREEN_HI = (10, 86, 68), (26, 138, 108)
ORANGE_BG, ORANGE_HI = (150, 62, 40), (206, 104, 64)


def up(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def text_sprite(s, fnt=PRESS24, k=2, top=GOLD, bottom=(255, 90, 30), thick=2, shadow=2):
    """Arcade text on its own canvas, scaled k times with hard pixels."""
    pad = thick + shadow + 1
    im = Image.new("RGBA", (text_width(s, fnt) + 2 * pad + 2, fnt.size + 2 * pad + 4), (0, 0, 0, 0))
    big_text(im, (pad, pad), s, fnt, top=top, bottom=bottom, thick=thick, shadow=shadow)
    return up(im, k)


def paste_c(dst, src, cx, cy):
    dst.paste(src, (int(cx - src.width / 2), int(cy - src.height / 2)), src)


def character(who, k, crop=(4, 22, 76, 90), **pose):
    """A character drawn on its own canvas (feet at 40, 96), cropped to a bust and scaled."""
    layer = Image.new("RGBA", (80, 100), (0, 0, 0, 0))
    draw_character(layer, who, 40, 96, **pose)
    return up(layer.crop(crop), k)


def split_background(split_top=184, split_bottom=136, rays=True):
    img = Image.new("RGB", (W, H), K)
    d = ImageDraw.Draw(img)
    left = [(0, 0), (split_top, 0), (split_bottom, H), (0, H)]
    right = [(split_top, 0), (W, 0), (W, H), (split_bottom, H)]
    d.polygon(left, fill=GREEN_BG)
    d.polygon(right, fill=ORANGE_BG)
    if rays:
        cx, cy = 160, 96

        def ray_fn(dd):
            for i in range(20):
                a0 = i * 2 * math.pi / 20
                a1 = a0 + math.pi / 20
                dd.polygon([(cx, cy), (cx + 400 * math.cos(a0), cy + 400 * math.sin(a0)),
                            (cx + 400 * math.cos(a1), cy + 400 * math.sin(a1))], fill=255)
        ray = mask(ray_fn)
        dither(img, ray * mask(lambda dd: dd.polygon(left, fill=255)) * 0.55, GREEN_HI)
        dither(img, ray * mask(lambda dd: dd.polygon(right, fill=255)) * 0.55, ORANGE_HI)
    return img


def hud_bars(ui, sam_hp, dario_hp, names=True):
    health_bar(ui, 8, 6, 132, 9, sam_hp, min(1.0, sam_hp + 0.25), V.TEAM["sam"], anchor_left=True)
    health_bar(ui, W - 140, 6, 132, 9, dario_hp, min(1.0, dario_hp + 0.2), V.TEAM["dario"],
               anchor_left=False)
    if names:
        big_text(ui, (8, 19), "SAM", PRESS16, top=WHITE, bottom=(170, 255, 220), thick=2, shadow=2)
        big_text(ui, (W - 8, 19), "DARIO", PRESS16, top=WHITE, bottom=(255, 210, 180), thick=2,
                 shadow=2, anchor="ra")


# --- A: the face-off --------------------------------------------------------------

def thumb_vs():
    world = split_background()
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(world).line([(184, 0), (136, H)], fill=WHITE, width=3)
    sam = character("sam", 3, facing=1, mouth="shout", brows="angry", eyes="open",
                    back_arm="mic", front_arm="point")
    dario = character("dario", 3, facing=-1, mouth="shout", brows="angry", eyes="open",
                      back_arm="mic", front_arm="point")
    # head tops sit at y 28 on the character canvas -> (28 - 22) * 3 = 18 px into the sprite
    ui.paste(sam, (66 - 108, 30 - 18), sam)
    ui.paste(dario, (254 - 108, 30 - 18), dario)
    burst(ui, 160, 104, 30, 60, GOLD, spikes=14, rot=0.2)
    burst(ui, 160, 104, 16, 34, WHITE, spikes=14, rot=0.45)
    paste_c(ui, text_sprite("VS", PRESS24, 2), 160, 104)
    hud_bars(ui, 0.34, 0.41)
    return world, ui


# --- B: the ALT-F4 joke ----------------------------------------------------------

def taskbar(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 13, W, H), fill=(192, 192, 192))
    d.line([(0, H - 13), (W, H - 13)], fill=WHITE)
    d.rectangle((2, H - 11, 38, H - 2), fill=(192, 192, 192), outline=K)
    d.line([(2, H - 11), (37, H - 11)], fill=WHITE)
    d.line([(2, H - 11), (2, H - 3)], fill=WHITE)
    d.fontmode = "1"
    d.text((7, H - 10), "Start", font=PRESS, fill=K)


def popup_sprite(k=2):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    w, h = draw_popup(canvas, 10, 10, "BOARD.EXE", "Close Sam?", ["YES", "YES"], focus=0,
                      cursor=False)
    # swap the warning triangle for Sam's panicking face
    d = ImageDraw.Draw(canvas)
    d.rectangle((16, 25, 31, 37), fill=(192, 192, 192))
    face = render_head("sam", "o", "worried", "wide").crop((6, 8, 30, 34)).resize((13, 14), Image.NEAREST)
    canvas.paste(face, (17, 24), face)
    return up(canvas.crop((10, 10, 10 + w + 4, 10 + h + 4)), k), w, h


def thumb_altf4():
    world = Image.new("RGB", (W, H), (0, 128, 128))
    dither(world, 0.08, (0, 150, 150))
    taskbar(world)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pop, w, h = popup_sprite(2)
    px, py = 8, 10
    ui.paste(pop, (px, py), pop)
    keys = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kw = keycap(keys, 2, 2, "ALT")
    big_text(keys, (kw + 6, 5), "+", PRESS16, top=WHITE, bottom=(200, 230, 255), thick=1, shadow=1)
    fw = keycap(keys, kw + 22, 2, "F4", pressed=2)
    keys = up(keys.crop((0, 0, kw + fw + 26, 28)), 2)
    ui.paste(keys, (12, 118), keys)
    dario = character("dario", 2, facing=-1, mouth="smirk", brows="smug", eyes="open",
                      back_arm="down", front_arm="point")
    ui.paste(dario, (262 - 72, 64 - 12), dario)
    bx = (w - 66) // 2
    cur = up(CURSOR, 2)
    ui.paste(cur, (px + (bx + 20) * 2, py + 41 * 2), cur)
    return world, ui


# --- C: the cross-counter -------------------------------------------------------

def fist(d, x, y, f):
    """A chunky side-view fist (11 x 11 px) with its knuckles pointing along f."""
    from characters import SKIN, SKIN_SH
    d.rounded_rectangle([x - 6, y - 6, x + 6, y + 6], radius=3, fill=K)
    d.rounded_rectangle([x - 5, y - 5, x + 5, y + 5], radius=2, fill=SKIN)
    d.line([(x - 4, y + 4), (x + 4, y + 4)], fill=SKIN_SH)
    front = (x, x + 5) if f == 1 else (x - 5, x)
    for yy in (y - 2, y + 1):
        d.line([(front[0], yy), (front[1], yy)], fill=K)
    tx = x - 3 * f
    d.rounded_rectangle([min(tx, tx - 4 * f), y - 1, max(tx, tx - 4 * f), y + 3], radius=1, fill=K)
    d.line([(min(tx, tx - 3 * f), y + 1), (max(tx, tx - 3 * f), y + 1)], fill=SKIN)


def punch_arm(d, who, shoulder, elbow, hand, f):
    from characters import LOOKS, _limb
    look = LOOKS[who]
    _limb(d, [shoulder, elbow, hand], look["top"], look["top_shade"])
    fist(d, hand[0], hand[1], f)


def thumb_ko():
    world = V.venue_variant(True, V.ALL_NEON, True).copy()
    dither(world, 0.2, (255, 30, 40), blend=0.35)
    V.spotlights(world, ("sam", "dario"))
    y = V.FEET_Y
    for who, x, facing in (("sam", 131, 1), ("dario", 189, -1)):
        draw_character(world, who, x, y, facing=facing, mouth="shout", brows="worried",
                       eyes="wide", back_arm="down", front_arm="down")
    for sx in (117, 198):
        world.paste(V.SWEAT, (sx, 82), V.SWEAT)
    for cx in (148, 172):
        burst(world, cx, 99, 6, 15, GOLD, spikes=11, rot=cx)
        burst(world, cx, 99, 3, 8, WHITE, spikes=11, rot=cx + 0.3)
    d = ImageDraw.Draw(world)
    punch_arm(d, "sam", (140, 108), (156, 116), (170, 100), 1)
    punch_arm(d, "dario", (180, 108), (164, 116), (150, 100), -1)
    cam = (107, 70, 214, 130)         # 107 x 60 world px -> 3x zoom on the two faces
    world = world.crop(cam).resize((W, H), Image.NEAREST)
    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hud_bars(ui, 0.0, 0.0, names=False)
    paste_c(ui, text_sprite("K.O.!", PRESS24, 2, top=(255, 120, 110), bottom=(200, 24, 40)), 150, 158)
    return world, ui


# --- output --------------------------------------------------------------------

def finish(world, ui):
    frame = world.convert("RGBA")
    frame.alpha_composite(ui)
    return frame.convert("RGB").resize(FINAL, Image.NEAREST)


def preview_sheet(thumbs):
    """Each thumbnail at YouTube's feed size (360 wide) and sidebar size (168 wide)."""
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
    for name, fn in (("A_vs", thumb_vs), ("B_altf4", thumb_altf4), ("C_ko", thumb_ko)):
        img = finish(*fn())
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
