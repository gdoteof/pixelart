"""A stream's overlay: the video its streamer is watching, his chat, and the captions.

World layout (320x180) on Hasan's stream; Asmongold's is its mirror image, and `box(who, b)` flips a box:
    PREVIEW   (212, 6, 316, 72)    the other man's video in a window: a title bar over a 100x54 picture
    CHAT      (232, 78, 316, 148)  the chat: a header and seven lines
    FEED      (118, 8, 202, 150)   side by side, the two chats run together down the middle of the frame
    ALERT     (98, 4, 206, 27)     an alert dropping in at the top: a subscriber, a donation, an achievement
                                   (it grows away from the window to fit its words)
    the captions                   y 159-180 (UI), with the singer's name on a tab above them

The video in the window is the other man's own webcam, shrunk: `preview_pic` cuts it out of his frame.
"""
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, SILK, H, W, Canvas, col, rgba, silk, silk_w
from pixelart import pixel
from pixelart.anim import k_in

PREVIEW = (212, 6, 316, 72)
PW, PH = 100, 54
CHAT = (232, 78, 316, 148)
CHAT_ROWS = 7
FEED = (118, 8, 202, 150)                                             # side by side, one chat down the middle
ALERT = (98, 4, 206, 27)
CROP = {"hasan": (0, 22, 200, 130), "asmon": (120, 22, 320, 130)}    # the part of a man's frame the window shows
ACCENT = {"hasan": "hasan", "asmon": "asmon", "chat": "chat", "both": "text"}
NAME = {"hasan": "HASANABI", "asmon": "ASMONGOLD", "chat": "CHAT", "both": "BOTH"}
CAP_Y = 159


def box(who, b):
    """A box of Hasan's layout, where it goes on `who`'s stream."""
    x0, y0, x1, y1 = b
    return b if who == "hasan" else (W - x1, y0, W - x0, y1)


def veil(img, b, color, alpha):
    """Darken (or tint) a box of an RGB image: a translucent panel."""
    x0, y0, x1, y1 = b
    part = img.crop((x0, y0, x1, y1))
    img.paste(Image.blend(part, Image.new("RGB", part.size, col(color)), alpha), (x0, y0))


# --- the video he's watching -----------------------------------------------------------------------

def preview_pic(frame, who):
    """`who`'s webcam frame as the other man's window shows it (PW x PH): the middle of it, at half size."""
    part = frame.crop(CROP[who])
    return part.resize((PW, PH), Image.BOX)


def pic_box(host):
    x0, y0, x1, y1 = box(host, PREVIEW)
    return (x0 + 2, y0 + 10, x0 + 2 + PW, y0 + 10 + PH)


def draw_preview(world, host, pic, title, accent, paused=True, progress=0.02, shake=(0, 0), badge=None, mark=None):
    """The window on `host`'s stream: a title bar, the picture (PW x PH), and the player's bar under it.
    `badge` is a short word at the right of the title bar (the time, "LIVE", "CLIP"); `mark` puts that
    man's logo in the picture's corner."""
    x0, y0, x1, y1 = box(host, PREVIEW)
    x0, y0, x1, y1 = x0 + shake[0], y0 + shake[1], x1 + shake[0], y1 + shake[1]
    d = ImageDraw.Draw(world)
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=INK)
    d.rectangle((x0, y0, x1 - 1, y0 + 8), fill=C["bar"])
    d.rectangle((x0, y0, x0 + 2, y0 + 8), fill=col(accent))
    if paused:                                                           # two bars
        d.rectangle((x0 + 5, y0 + 2, x0 + 6, y0 + 6), fill=C["text"]); d.rectangle((x0 + 8, y0 + 2, x0 + 9, y0 + 6), fill=C["text"])
    else:                                                                # a triangle
        d.polygon([(x0 + 5, y0 + 2), (x0 + 5, y0 + 6), (x0 + 9, y0 + 4)], fill=C["text"])
    silk(world, (x0 + 13, y0 + 2), title, "text")
    if badge and x0 + 13 + silk_w(title) + 4 <= x1 - 4 - silk_w(badge):      # only where the title leaves it room
        silk(world, (x1 - 4, y0 + 2), badge, "live" if badge == "LIVE" else "dim", anchor="ra")
    px, py = x0 + 2, y0 + 10
    world.paste(pic.convert("RGB"), (px, py))
    if mark:
        m = logo(mark)
        world.paste(m, (px + PW - 15, py + 2), m)
    if paused:
        icon = pause_icon()
        world.paste(icon, (px + 3, py + PH - 18), icon)
    d = ImageDraw.Draw(world)
    d.rectangle((x0, y0 + 9, x1 - 1, y1 - 1), outline=C["bar"])
    d.rectangle((x0 + 1, y0 + 9, x1 - 2, y1 - 1), outline=C["bar"])
    d.line([(px, py + PH - 2), (px + PW - 1, py + PH - 2)], fill=C["mute"])        # the player's bar
    k = max(2, int(round(PW * min(1.0, progress))))
    d.line([(px, py + PH - 2), (px + k, py + PH - 2)], fill=C["live"])
    d.rectangle((px + k - 1, py + PH - 3, px + k, py + PH - 1), fill=C["white"])
    d.rectangle((x0 - 2, y0 - 2, x1 + 1, y1 + 1), outline=col(accent))


@lru_cache(maxsize=None)
def logo(who):
    """The channel's mark, as it sits in the corner of its videos (13x13)."""
    f = Canvas(13, 13)
    if who == "hasan":                                                   # an H on purple
        f.d.rounded_rectangle((1, 1, 11, 11), 2, fill=rgba("hasan"))
        f.rect((3, 3, 4, 9), "white"); f.rect((8, 3, 9, 9), "white"); f.rect((4, 5, 8, 6), "white")
    else:                                                                # an A on green
        f.poly([(6, 1), (11, 4), (11, 9), (6, 11), (1, 9), (1, 4)], "asmon_sh")
        f.line([(4, 9), (6, 3), (8, 9)], "white"); f.line([(5, 7), (7, 7)], "white")
    return f.done()


def reactions(world, host, age, seed, kinds=("lul", "skull", "fire", "lul", "skull", "clap")):
    """What chat throws at the man in the window when a big one lands: emotes drifting up his picture."""
    if not 0 <= age < 2.2:
        return
    import math

    from engine import rnd
    x0, y0, x1, y1 = pic_box(host)
    part = world.crop((x0, y0, x1, y1 - 3)).convert("RGBA")
    for j in range(7):
        a = age - j * 0.12
        if not 0 <= a < 1.5:
            continue
        x = 8 + int(rnd("rx", seed, j) * (PW - 26)) + int(3 * math.sin(a * 5 + j))
        e = emote(kinds[j % len(kinds)])
        part.alpha_composite(e, (x, int((PH - 10) * (1 - a / 1.5))))
    world.paste(part.convert("RGB"), (x0, y0))


@lru_cache(maxsize=4)
def pause_icon(n=1):
    f = Canvas(13 * n, 13 * n)
    f.rect((2 * n, 1 * n, 5 * n - 1, 11 * n), "white")
    f.rect((7 * n, 1 * n, 10 * n - 1, 11 * n), "white")
    return f.done()


# --- the chat ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def emote(kind):
    """A little picture a chatter posts instead of a word (7x7)."""
    f = Canvas(9, 9)
    if kind == "lul":                                                    # crying with laughter
        f.ell((1, 1, 7, 7), "yellow"); f.pxs([(2, 3), (3, 2), (5, 2), (6, 3)], "ink")
        f.rect((3, 5, 5, 6), "mouth"); f.pxs([(1, 4), (7, 4)], "tear")
    elif kind == "skull":
        f.ell((1, 1, 7, 6), "white"); f.rect((3, 5, 5, 7), "white")
        f.pxs([(3, 3), (5, 3)], "ink"); f.px((4, 7), "ink")
    elif kind == "fire":
        f.poly([(4, 1), (7, 4), (6, 7), (2, 7), (1, 4), (3, 3)], "orange"); f.pxs([(4, 5), (4, 6), (3, 6)], "yellow")
    elif kind == "roach":
        f.ell((2, 2, 6, 6), "roach"); f.pxs([(1, 2), (1, 6), (7, 2), (7, 6), (4, 1)], "roach_sh")
    elif kind == "clap":
        f.rect((2, 3, 4, 7), "hskin"); f.rect((4, 2, 6, 6), "askin"); f.pxs([(1, 1), (7, 1), (4, 0)], "yellow")
    elif kind == "frog":
        f.ell((1, 2, 7, 7), "green"); f.pxs([(2, 3), (6, 3)], "white"); f.line([(3, 6), (5, 6)], "green_sh")
    elif kind == "heart":
        f.rect((1, 2, 3, 4), "red"); f.rect((5, 2, 7, 4), "red"); f.rect((2, 4, 6, 5), "red"); f.rect((3, 6, 5, 6), "red")
        f.px((4, 7), "red")
    return f.img


NAME_COLORS = ("hasan_hi", "asmon_hi", "chat", "pink", "sky", "orange", "red_hi", "green_hi", "blue_hi", "gold_hi")


def chat_rows(messages, width):
    """Lay messages out as rows of (x, word or emote, colour) runs: a name, then what it typed, which goes on
    a row of its own (indented) when it doesn't fit beside the name, and wraps."""
    space = silk_w(" ")
    rows = []
    for name, color, text in messages:
        words = text.split()
        sizes = [8 if w.startswith(":") and w.endswith(":") else silk_w(w) for w in words]
        row, x = [], 0
        if name:
            row.append((0, name, color))
            x = silk_w(name) + 3
            if x + sum(sizes) + space * (len(words) - 1) > width:
                rows.append(row)
                row, x = [], 6
        for word, ww in zip(words, sizes):
            if x > 6 and x + ww > width:
                rows.append(row)
                row, x = [], 6
            row.append((x, word, None if word.startswith(":") and word.endswith(":") else "text"))
            x += ww + space
        rows.append(row)
    return rows


def draw_chat(world, host, messages, age, viewers, title="CHAT", at=None, accent=None):
    """A chat panel showing the tail of `messages` ((name, colour, text), oldest first); `age` is seconds
    since the newest arrived, and slides it in. It is `host`'s panel, or any box `at`."""
    x0, y0, x1, y1 = at or box(host, CHAT)
    veil(world, (x0, y0, x1, y1), "bg", 0.78)
    d = ImageDraw.Draw(world)
    d.rectangle((x0, y0, x1 - 1, y0 + 8), fill=C["bar"])
    for i, a in enumerate(accent or (ACCENT[host],)):
        d.rectangle((x0 + 3 * i, y0, x0 + 3 * i + 2, y0 + 8), fill=col(a))
    silk(world, (x0 + 5 + 3 * (len(accent or "x") - 1), y0 + 2), title, "text")
    silk(world, (x1 - 3, y0 + 2), viewers, "dim", anchor="ra")
    d.ellipse((x1 - 8 - silk_w(viewers), y0 + 3, x1 - 6 - silk_w(viewers), y0 + 5), fill=C["live"])
    width = x1 - x0 - 6
    rows = chat_rows(messages, width)
    h = (y1 - y0 - 13) // 8 * 8
    pane = Image.new("RGBA", (x1 - x0 - 4, h), (0, 0, 0, 0))
    slide = int(round((1 - k_in(age, 0.12)) * 8 * len(chat_rows(messages[-1:], width)))) if messages else 0
    y = h - 8 * len(rows) + slide
    for row in rows:
        if 0 <= y < h:
            for x, word, color in row:
                if color is None:
                    e = emote(word.strip(":"))
                    pane.alpha_composite(e, (x, max(0, y - 1)))
                else:
                    silk(pane, (x, y + 1), word, color)
        y += 8
    world.paste(pane, (x0 + 3, y0 + 11), pane)


# --- alerts ------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def alert_icon(kind):
    """A 15x15 picture for an alert: star (a subscriber), coin (a donation), cup (an achievement), hammer (a
    ban), bell, or any emote's name."""
    f = Canvas(15, 15)
    if kind == "star":
        f.poly([(7, 0), (9, 5), (14, 5), (10, 8), (12, 14), (7, 10), (2, 14), (4, 8), (0, 5), (5, 5)], "gold")
        f.line([(7, 3), (7, 8)], "gold_hi")
    elif kind == "coin":
        f.ell((1, 1, 13, 13), "gold"); f.ell((3, 3, 11, 11), "gold_hi")
        f.line([(7, 4), (7, 10)], "gold_sh"); f.line([(5, 5), (9, 5)], "gold_sh"); f.line([(5, 9), (9, 9)], "gold_sh")
    elif kind == "cup":
        f.poly([(3, 1), (11, 1), (10, 7), (8, 9), (6, 9), (4, 7)], "gold"); f.rect((6, 9, 8, 11), "gold_sh")
        f.rect((4, 12, 10, 13), "gold"); f.line([(5, 2), (5, 6)], "gold_hi")
        f.line([(2, 2), (1, 4), (3, 6)], "gold_sh"); f.line([(12, 2), (13, 4), (11, 6)], "gold_sh")
    elif kind == "hammer":
        f.rect((1, 2, 10, 6), "grey_hi"); f.rect((1, 5, 10, 6), "grey"); f.line([(6, 7), (12, 13)], "brown", 2)
    elif kind == "bell":
        f.poly([(7, 1), (10, 3), (11, 9), (13, 11), (1, 11), (3, 9), (4, 3)], "gold"); f.rect((6, 12, 8, 13), "gold_sh")
        f.line([(6, 3), (5, 9)], "gold_hi")
    else:
        e = emote(kind)
        return e.resize((e.width * 2, e.height * 2), Image.NEAREST).crop((0, 0, 15, 15))
    return f.done()


def draw_alert(world, host, age, title, text=None, icon="star", dur=2.6, accent=None):
    """An alert on `host`'s stream, from age 0 for `dur` seconds: it drops in at the top of his frame and
    lifts out again. An icon, a title in his colour, and a line under it."""
    if not 0 <= age < dur:
        return
    w = 24 + max(silk_w(title), silk_w(text or "")) + 6                # as wide as its words, growing away from
    x0, y0, x1, y1 = ALERT                                             # the window
    x0, y0, x1, y1 = box(host, (min(x0, x1 - w), y0, x1, y1))
    if host != "hasan":
        x1 = max(x1, x0 + w)
    k = min(k_in(age, 0.14), 1 - k_in(age - (dur - 0.14), 0.14))
    y0 -= int(round((1 - k) * (y1 + 2)))
    y1 = y0 + (ALERT[3] - ALERT[1])
    if y1 <= 0:
        return
    accent = accent or ACCENT[host]
    d = ImageDraw.Draw(world)
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=INK)
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=C["bar"])
    d.rectangle((x0, y0, x0 + 1, y1 - 1), fill=col(accent)); d.rectangle((x1 - 2, y0, x1 - 1, y1 - 1), fill=col(accent))
    im = alert_icon(icon)
    bob = -1 if int(age * 6) % 2 == 0 and age < 0.9 else 0
    world.paste(im, (x0 + 5, max(-15, y0 + 4 + bob)), im)
    if text is None:
        silk(world, (x0 + 24, y0 + 8), title, accent + "_hi")
    else:
        silk(world, (x0 + 24, y0 + 3), title, accent + "_hi")
        silk(world, (x0 + 24, y0 + 12), text, "text")


# --- the captions -----------------------------------------------------------------------------------

def draw_captions(ui, words, now, who, side=None, sound=lambda w: False):
    """The line being sung, along the bottom: sung words bright, the current one gold. `who` names the tab,
    which sits on the side of the frame its singer does."""
    d = ImageDraw.Draw(ui)
    rows = pixel.wrap(words, W - 16, SILK)[:2]
    y0 = CAP_Y
    d.rectangle((0, y0, W, H), fill=(12, 12, 20, 236))
    accent = col(ACCENT.get(who, "line"))
    d.line([(0, y0), (W, y0)], fill=accent + (255,))
    space = silk_w(" ")
    for r, row in enumerate(rows):
        x, y = 8, y0 + 4 + 8 * r + (4 if len(rows) == 1 else 0)
        for i in row:
            silk(ui, (x, y), words[i], "gold" if i == now else "text" if i < now else (146, 150, 178))
            x += silk_w(words[i]) + space
    if who in NAME:
        name = NAME[who]
        nw = silk_w(name) + 8
        x = W - 6 - nw if (side or who) == "asmon" else 6
        d.rectangle((x, y0 - 10, x + nw, y0 - 1), fill=accent + (255,))
        silk(ui, (x + 4, y0 - 8), name, "ink" if who in ("asmon", "chat", "both") else "text")
