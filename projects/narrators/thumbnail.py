"""YouTube thumbnails (1280x720) in the video's pixel style:

    uv run python projects/narrators/thumbnail.py      # -> thumbs/

Three variants for YouTube Studio's Test & Compare, plus a sheet showing each one at the sizes YouTube
displays them. The world is 320x180, so 1280x720 is an exact 4x and every pixel stays square.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import chrome as CH
import video as V
from characters import figure
from engine import C, INK, PRESS, PRESS16, PRESS24, H, W, scaled, text_width
from pixelart.camera import Cam, compose
from props import big_text, burst, globe
from sets import SETS

OUT = Path(__file__).parent / "thumbs"
FINAL = (1280, 720)
BASE = FINAL[0] // W                     # 4: the whole world fills the thumbnail


def cam(cx, cy, zoom=1):
    return Cam(cx, cy, BASE * zoom, world=(W, H), out=FINAL)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def frame_at(t, **overrides):
    """The video's own frame at time t without its subtitles, as (world, ui, cam) at thumbnail scale."""
    def quiet(c):
        c.subs = False
        c.inset = False
        for k, v in overrides.items():
            setattr(c, k, v)
    c = V.build_frame(t, quiet)
    k = c.cam.k * BASE / c.cam.scale
    assert k == int(k), "the shot's zoom has no whole-pixel equivalent at thumbnail scale"
    return c.world, c.ui, Cam(c.cam.cx, c.cam.cy, int(k), world=(W, H), out=FINAL)


def set_world(name, t):
    """A home set's background at time t, with nobody in it."""
    return SETS[name].back(V.Ctx(t))


def bust(who, scale, facing, w=30, h=28, **pose):
    """Head and shoulders, cropped from the full figure and scaled up."""
    spr, a = figure(who, facing, **pose)
    hx, hy = a["head"]
    x0, y0 = int(hx - w / 2), int(hy - 12)
    return scaled(spr.crop((x0, y0, x0 + w, y0 + h)), scale)


def plate(ui, x, y, s, bg, fg, anchor="l", fnt=PRESS):
    """A name plate in the arcade font."""
    tw = text_width(s, fnt)
    x0 = {"l": x, "m": x - tw // 2 - 4, "r": x - tw - 8}[anchor]
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x0 + tw + 8, y + fnt.size + 4), fill=INK)
    d.rectangle((x0, y, x0 + tw + 7, y + fnt.size + 3), fill=bg)
    d.fontmode = "1"
    d.text((x0 + 4, y + 2), s, font=fnt, fill=fg)


def vs(ui, x, y, big=False):
    if big:
        burst(ui, x, y, 24, 42, C["gold"], spikes=12, rot=0.2)
        burst(ui, x, y, 15, 27, C["white"], spikes=12, rot=0.45)
        big_text(ui, (x + 1, y - 12), "VS", PRESS24, top=C["red_hi"], bottom=C["red"], anchor="ma")
        return
    burst(ui, x, y, 17, 30, C["gold"], spikes=12, rot=0.2)
    burst(ui, x, y, 10, 19, C["white"], spikes=12, rot=0.45)
    big_text(ui, (x, y - 8), "VS", PRESS16, top=C["red_hi"], bottom=C["red"], anchor="ma")


# --- A: the fight -------------------------------------------------------------------------------

def health_bar(ui, x0, x1, y, fill, name, left):
    """A fighting game's life bar, drained from the middle, with the fighter's name under it."""
    d = ImageDraw.Draw(ui)
    d.rectangle((x0 - 1, y - 1, x1 + 1, y + 7), fill=INK)
    d.rectangle((x0, y, x1, y + 6), fill=(170, 28, 36))
    w = int((x1 - x0) * fill)
    a, b = (x0, x0 + w) if left else (x1 - w, x1)
    d.rectangle((a, y, b, y + 6), fill=C["gold_hi"])
    d.line([(a, y + 1), (b, y + 1)], fill=(255, 250, 200))
    d.fontmode = "1"
    tx = x0 if left else x1 - text_width(name, PRESS)
    ImageDraw.Draw(ui).text((tx + 1, y + 10), name, font=PRESS, fill=INK)
    ImageDraw.Draw(ui).text((tx, y + 9), name, font=PRESS, fill=C["text"])


def thumb_fight():
    """A fighting game's VS screen: the two narrators face to face, and the planet between their life bars."""
    world = Image.new("RGB", (W, H), (16, 18, 42))
    d = ImageDraw.Draw(world)
    d.polygon([(0, 0), (W // 2 + 30, 0), (W // 2 - 30, H), (0, H)], fill=(70, 20, 32))          # 1P red, 2P blue
    d.polygon([(W // 2 + 30, 0), (W, 0), (W, H), (W // 2 - 30, H)], fill=(20, 30, 86))
    for x in range(-H, W + 16, 14):                                                             # speed stripes
        d.line([(x, H), (x + H // 3, 0)], fill=(96, 30, 44) if x < W // 2 - 20 else (30, 44, 116), width=4)
    david = bust("david", 5, 1, mouth="wide", brows="angry", eyes="open", arm="point")
    morgan = bust("morgan", 5, -1, mouth="smirk", brows="up", eyes="half")
    world.paste(david, (-6, H - david.height), david)
    world.paste(morgan, (W - morgan.width + 6, H - morgan.height), morgan)
    ui = blank()
    health_bar(ui, 8, 138, 8, 0.62, "ATTENBOROUGH", True)
    health_bar(ui, W - 138, W - 8, 8, 0.58, "FREEMAN", False)
    g = globe(9, 3)
    ui.alpha_composite(g, (W // 2 - g.width // 2, 3))
    vs(ui, W // 2, 100, big=True)
    return world, ui, cam(W / 2, H / 2)


# --- B: whoever raps holds the camera ---------------------------------------------------------------

def tear_mask(x_top, x_bottom, seed=7):
    """1 left of a ragged diagonal from (x_top, 0) to (x_bottom, H), 0 right of it."""
    rng = np.random.default_rng(seed)
    jag = np.cumsum(rng.integers(-2, 3, H)).astype(np.float32)
    jag -= np.linspace(0, jag[-1], H)                       # the ends stay put
    edge = np.linspace(x_top, x_bottom, H) + jag
    return (np.arange(W)[None, :] < edge[:, None]).astype(np.uint8) * 255, edge


def thumb_split():
    """Sir David's documentary on the left, Morgan's film on the right, torn apart down the middle."""
    doc = set_world("habitat", 24.0)
    film = set_world("yard", 100.0)
    d_spr, _ = figure("david", 1, mic="fluffy", arm="whisper", mouth="o", brows="up", eyes="open")
    m_spr, _ = figure("morgan", -1, outfit="prison", mic=True, arm="point", mouth="smirk", eyes="half", brows="up")
    d_spr, m_spr = scaled(d_spr, 3), scaled(m_spr, 3)
    doc.paste(d_spr, (-4, H - d_spr.height + 14), d_spr)
    film.paste(m_spr, (W - m_spr.width + 6, H - m_spr.height + 14), m_spr)
    CH.film_grade(film, 3.0, warm=1.0, grain=1.0, vignette=1.0)
    m, edge = tear_mask(W // 2 + 60, W // 2 - 50)
    world = film.copy()
    world.paste(doc, (0, 0), Image.fromarray(m))
    d = ImageDraw.Draw(world)
    for y in range(H):                                       # the torn edge
        x = int(edge[y])
        d.line([(x - 1, y), (x + 1, y)], fill=(250, 244, 226))
    ui = blank()
    film_ui = blank()                                        # the film's letterbox, right of the tear only
    CH.letterbox(film_ui, 1.0)
    film_ui.putalpha(Image.fromarray(np.minimum(np.asarray(film_ui.getchannel("A")), 255 - m)))
    ui.alpha_composite(film_ui)
    ud = ImageDraw.Draw(ui)
    big_text(ui, (4, 4), "ATTENBOROUGH", PRESS16, top=(236, 255, 236), bottom=(120, 210, 150), anchor="la")
    ud.ellipse((9, 30, 16, 37), fill=C["rec"])               # the documentary's REC light
    ud.fontmode = "1"
    ud.text((20, 30), "REC", font=PRESS, fill=C["text"])
    ud.line([(6, H - 7), (20, H - 7)], fill=C["text"])       # a viewfinder corner
    ud.line([(6, H - 7), (6, H - 21)], fill=C["text"])
    big_text(ui, (W - 8, H - 21), "FREEMAN", PRESS16, top=C["gold_hi"], bottom=C["gold"], anchor="ra")
    vs(ui, W // 2, H // 2 - 2)
    return world, ui, cam(W / 2, H / 2)


# --- C: planet beef -----------------------------------------------------------------------------------

def thumb_planet():
    """The outro's insert: the planet in God's hand, Sir David standing on top of it."""
    world, ui, view = frame_at(320.5, bars=0.0)
    big_text(ui, (W // 2, 8), "PLANET BEEF", PRESS24, top=C["white"], bottom=C["gold_hi"], anchor="ma")
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
    for name, fn in (("A_fight", thumb_fight), ("B_split", thumb_split), ("C_planet", thumb_planet)):
        img = finish(*fn())
        path = OUT / f"thumb_{name}.png"
        img.save(path, optimize=True)
        made.append((name, img))
        print(path, f"{path.stat().st_size / 1024:.0f} KB")
    preview_sheet(made).save(OUT / "preview_sizes.png")


if __name__ == "__main__":
    main()
