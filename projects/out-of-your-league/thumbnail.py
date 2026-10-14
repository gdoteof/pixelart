"""YouTube thumbnails (1280x720) in the video's pixel style:

    uv run python projects/out-of-your-league/thumbnail.py      # -> thumbs/

Three variants for YouTube Studio's A/B test, each on a different hook from the song, plus a sheet showing
each one at the sizes YouTube displays them. The backdrops are drawn at 320x180 and shown 4x; the figures
and the lettering are placed at whole multiples of their own pixels, so every pixel stays square.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from characters import figure
from engine import C, INK, PRESS, PRESS16, Canvas, H, W
from pixelart import fx, pixel
from pixelart.sprites import outlined

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
BASE = FINAL[0] // W                     # 4: a backdrop pixel


def up(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def sticker(spr, color=C["white"], n=1):
    """The sprite with a border n pixels wide round it: a cut-out, lifted off the backdrop."""
    out = Image.new("RGBA", (spr.width + 2 * n, spr.height + 2 * n), (0, 0, 0, 0))
    out.alpha_composite(spr, (n, n))
    for _ in range(n):
        out = outlined(out, color)
    return out


def put(img, spr, k, x, y, anchor="lt"):
    """Paste a sprite at k times its size; (x, y) is its left or middle, and its top or bottom."""
    spr = up(spr, k)
    x -= spr.width // 2 if anchor[0] == "m" else 0
    y -= spr.height if anchor[1] == "b" else 0
    img.paste(spr, (int(x), int(y)), spr)


def rays(base, ray, cx, cy, n=14, rot=0.0):
    """A backdrop of rays from (cx, cy), at 320x180."""
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    for i in range(n):
        a0, a1 = rot + i * 2 * math.pi / n, rot + (i + 0.5) * 2 * math.pi / n
        d.polygon([(cx, cy), (cx + 500 * math.cos(a0), cy + 500 * math.sin(a0)),
                   (cx + 500 * math.cos(a1), cy + 500 * math.sin(a1))], fill=ray)
    return img


def bust(who, facing=1, arms="desk", rows=120, edge=1, **expr):
    """Her figure down to `rows`, as a cut-out with a white edge."""
    spr, _ = figure(who, arms, facing=facing, **expr)
    return sticker(spr.crop((0, 0, spr.width, rows)), n=edge)


def words(img, x, y, s, k, fnt=PRESS16, top=C["white"], bottom=C["gold_hi"], anchor="lt"):
    """Arcade lettering k times the font's size, by its left or middle and its top."""
    im, pad = fx.big_text_img(s, fnt, tuple(top), tuple(bottom), tuple(INK), ink=tuple(INK))
    put(img, im, k, x - (0 if anchor[0] == "m" else pad * k), y - pad * k, anchor)


# --- A: Twitch is next --------------------------------------------------------------------------------

def twitch_boss():
    """The boss of verse 3, big: a purple speech bubble in a tie, sweating, a crack across its screen."""
    f = Canvas(64, 76)
    f.poly([(36, 56), (44, 56), (46, 68), (40, 75), (34, 68)], "live"); f.line([(39, 60), (38, 68)], "red_hi")   # the tie
    f.poly([(14, 2), (60, 2), (60, 40), (50, 52), (24, 52), (13, 62), (13, 52), (4, 52), (4, 12)], "twitch")
    f.poly([(31, 51), (40, 51), (36, 58)], "white"); f.poly([(40, 51), (49, 51), (44, 58)], "white")            # the collar
    f.poly([(37, 52), (43, 52), (42, 58), (38, 58)], "live")
    f.poly([(16, 8), (54, 8), (54, 38), (48, 46), (10, 46), (10, 14)], "twitch_sh")
    f.line([(15, 4), (58, 4)], "twitch_hi"); f.line([(6, 13), (6, 50)], "twitch_hi")
    f.rect((22, 20, 26, 36), "white"); f.rect((38, 20, 42, 36), "white")                        # its eyes
    f.line([(17, 17), (24, 13), (27, 13)], "white", w=2); f.line([(37, 13), (40, 13), (47, 17)], "white", w=2)
    f.line([(27, 41), (30, 39), (34, 41), (37, 39)], "white")                                    # a mouth that wavers
    f.line([(46, 8), (43, 15), (48, 20), (44, 27), (50, 33)], "twitch_hi")                       # the crack
    f.line([(48, 20), (53, 22)], "twitch_hi")
    return f.done()


def sweat(img, x, y, k):
    d = ImageDraw.Draw(img)
    for dx, dy in ((0, 0), (1, 3), (-2, 5)):
        px, py = x + dx * 4 * k, y + dy * 4 * k
        d.polygon([(px, py - 3 * k), (px + 2 * k, py + k), (px, py + 3 * k), (px - 2 * k, py + k)], fill=INK)
        d.polygon([(px, py - 2 * k), (px + k, py + k), (px, py + 2 * k), (px - k, py + k)], fill=C["sweat"])


def health_bar(img, box, k, label):
    """A boss's health bar, nearly empty."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 8, y0 - 8, x1 + 8, y1 + 8), fill=INK)
    d.rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), fill=C["white"])
    d.rectangle(box, fill=C["black"])
    d.rectangle((x0, y0, x0 + int((x1 - x0) * k), y1), fill=C["live"])
    d.rectangle((x0, y0, x0 + int((x1 - x0) * k), y0 + (y1 - y0) // 3), fill=C["red_hi"])
    words(img, x0 - 4, y0 - 44, label, 3, PRESS, top=C["gold_hi"], bottom=C["gold"])


def thumb_twitch():
    """Emiru points across the frame at a boss on its last sliver of health: the one with Twitch's face."""
    img = up(rays((52, 24, 104), (74, 38, 140), 240, 124, rot=0.1), BASE)
    put(img, sticker(twitch_boss(), n=1), 5, 968, 716, "mb")
    sweat(img, 1158, 380, 5)
    put(img, bust("emiru", arms="point", eyes="half", brows="angry", mouth="smirk"), 6, -84, -6)
    words(img, 676, 26, "TWITCH", 6, top=C["white"], bottom=C["twitch_hi"])
    words(img, 676, 136, "IS NEXT", 5, top=C["gold_hi"], bottom=C["gold"])
    health_bar(img, (688, 276, 1228, 296), 0.09, "BOSS")
    return img


# --- B: the new bodyguard -----------------------------------------------------------------------------

def bodyguard():
    """Maya's wolf, on Emiru's detail: shades, an earpiece, a black suit."""
    f = Canvas(64, 84)
    f.poly([(4, 83), (8, 68), (22, 60), (42, 60), (56, 68), (60, 83)], "black")                 # the suit
    f.poly([(24, 60), (40, 60), (32, 74)], "white")                                              # the shirt
    f.line([(23, 61), (31, 76), (26, 83)], "grey_sh"); f.line([(41, 61), (33, 76), (38, 83)], "grey_sh")
    f.poly([(30, 62), (34, 62), (35, 66), (33, 68), (35, 82), (32, 83), (29, 82), (31, 68), (29, 66)], "black")
    f.poly([(9, 24), (14, 1), (27, 15)], "wolf_sh"); f.poly([(13, 20), (15, 7), (23, 16)], "eblush")    # the ears
    f.poly([(55, 24), (50, 1), (37, 15)], "wolf_sh"); f.poly([(51, 20), (49, 7), (41, 16)], "eblush")
    f.poly([(9, 23), (17, 14), (27, 11), (37, 11), (47, 14), (55, 23), (61, 37), (55, 44), (48, 52), (41, 60),
            (23, 60), (16, 52), (9, 44), (3, 37)], "wolf")                                       # the head, cheeks ruffed
    f.poly([(27, 11), (37, 11), (36, 24), (32, 28), (28, 24)], "wolf_sh")                        # the blaze
    f.poly([(3, 37), (9, 34), (12, 40), (9, 44)], "wolf_hi"); f.poly([(61, 37), (55, 34), (52, 40), (55, 44)], "wolf_hi")
    f.poly([(24, 36), (40, 36), (45, 47), (40, 58), (24, 58), (19, 47)], "wolf_hi")              # the muzzle
    f.ell((27, 44, 37, 51), "black"); f.px((30, 46), "grey_hi"); f.px((31, 46), "grey_hi")      # the nose
    f.line([(32, 51), (32, 54)], "wolf_sh"); f.line([(26, 54), (29, 56), (32, 54), (35, 56), (38, 54)], "wolf_sh")
    f.rect((10, 25, 29, 35), "black"); f.rect((35, 25, 54, 35), "black")                         # the shades
    f.rect((29, 26, 35, 28), "black"); f.line([(5, 27), (10, 27)], "black"); f.line([(54, 27), (59, 27)], "black")
    f.poly([(11, 34), (11, 36), (27, 36), (28, 34)], "black"); f.poly([(36, 34), (37, 36), (53, 36), (53, 34)], "black")
    f.line([(13, 32), (19, 27)], "grey_hi"); f.line([(17, 32), (21, 28)], "grey"); f.line([(38, 32), (44, 27)], "grey_hi")
    f.line([(42, 32), (46, 28)], "grey")
    for i, y in enumerate(range(38, 62, 2)):                                                     # the earpiece's coil
        f.px((59 + i % 2, y), "white"); f.px((60 - i % 2, y + 1), "grey_hi")
    return f.done()


def split_rays(left, right, cx=160, cy=96):
    img = rays(*left, cx, cy, rot=0.12)
    img.paste(rays(*right, cx, cy, rot=0.12).crop((cx, 0, W, H)), (cx, 0))
    return img


def arrow(img, pts, color=C["live"], width=22, head=46):
    """A fat arrow along the points, its head at the last one."""
    d = ImageDraw.Draw(img)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    a = math.atan2(y1 - y0, x1 - x0)

    def tip(size, back=0.0):
        bx, by = x1 - back * math.cos(a), y1 - back * math.sin(a)
        return [(bx + size * 0.3 * math.cos(a), by + size * 0.3 * math.sin(a))] + [
            (bx - size * math.cos(a + s * 0.62), by - size * math.sin(a + s * 0.62)) for s in (1, -1)]

    for ink, w, t in ((INK, width + 16, tip(head + 16, -8)), (color, width, tip(head))):
        d.line(pts[:-1] + [(x1 - head * 0.6 * math.cos(a), y1 - head * 0.6 * math.sin(a))], fill=ink, width=w, joint="curve")
        d.polygon(t, fill=ink)


def thumb_bodyguard():
    """The two of them either side of the wolf from verse 3, who has the shades and the earpiece on."""
    img = up(split_rays(((150, 44, 98), (186, 62, 122)), ((42, 108, 50), (62, 138, 60))), BASE)
    put(img, bust("emiru", rows=100, eyes="open", brows="up", mouth="grin"), 6, -124, 124)
    put(img, bust("maya", facing=-1, rows=100, eyes="open", brows="up", mouth="grin"), 6, 564, 124)
    put(img, sticker(bodyguard(), n=1), 6, 640, 724, "mb")
    words(img, 640, 22, "NEW BODYGUARD", 5, anchor="mt")
    arrow(img, [(1000, 150), (900, 240), (826, 306)])
    return img


# --- C: Kai, straight to voicemail ----------------------------------------------------------------------

def phone():
    """Maya's phone, ringing: the caller's name, and her thumb on the red button."""
    f = Canvas(96, 134)
    f.rect((2, 6, 93, 127), "black"); f.rect((6, 2, 89, 131), "black")
    f.rect((6, 10, 89, 123), "night"); f.rect((6, 10, 89, 20), "bar")
    f.rect((38, 5, 57, 6), "grey_sh")
    f.silk((48, 12), "INCOMING CALL", "dim", anchor="ma")
    f.ell((16, 70, 40, 94), "live"); f.ell((56, 70, 80, 94), "ok")
    f.line([(22, 82), (34, 82)], "white", w=3)                                                   # hang up
    f.poly([(62, 82), (66, 86), (75, 77), (75, 81), (66, 90), (62, 86)], "white")                # pick up
    f.d.ellipse((13, 67, 43, 97), outline=f.c("white"), width=2)
    return f.done()


def banner(s, k, fill=C["live"], fg=C["white"], fnt=PRESS16, angle=-8):
    """A word on a slab of colour, tilted: a verdict."""
    tw = pixel.text_width(s, fnt)
    im = Image.new("RGBA", (tw + 14, fnt.size + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.rectangle((0, 0, im.width - 1, im.height - 1), fill=INK)
    d.rectangle((2, 2, im.width - 3, im.height - 3), fill=C["white"])
    d.rectangle((4, 4, im.width - 5, im.height - 5), fill=fill)
    d.text((8, 7), s, font=fnt, fill=INK); d.text((7, 6), s, font=fnt, fill=fg)
    return up(im, k).rotate(angle, resample=Image.NEAREST, expand=True)


def thumb_voicemail():
    """Kai Cenat is calling; Maya has sent him to voicemail, and Emiru can't believe it."""
    img = up(rays((250, 196, 44), (255, 224, 96), 160, 100, n=16, rot=0.05), BASE)
    put(img, bust("emiru", eyes="wide", brows="up", mouth="o", arms="desk"), 6, -150, 30)
    put(img, bust("maya", facing=-1, eyes="half", brows="skeptic", mouth="smirk"), 6, 590, 30)
    put(img, sticker(phone(), n=1), 5, 640, 706, "mb")
    words(img, 640, 150, "KAI", 5, anchor="mt")
    words(img, 640, 244, "CENAT", 5, anchor="mt")
    b = banner("VOICEMAIL", 4)
    img.paste(b, (640 - b.width // 2, 618 - b.height // 2), b)
    return img


# --- output ---------------------------------------------------------------------------------------------

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
    for name, fn in (("A_twitch", thumb_twitch), ("B_bodyguard", thumb_bodyguard), ("C_voicemail", thumb_voicemail)):
        img = fn()
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
