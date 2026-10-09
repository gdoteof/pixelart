"""A stream's overlay: the window where its streamer pulls things up, her chat, her friend on a call, and
the captions.

The drawing is pixelart.streamui's, bound here to this video's palette and its two women. Emiru sits on
the left of her frame with the overlay on her right; Maya's stream is the mirror image, and `box(who, b)`
flips a box of Emiru's layout. "pair" is the frame the two share, with the window between them:
    PREVIEW   (212, 6, 316, 72)    the window: a title bar over a 100x54 picture
    CHAT      (232, 78, 316, 148)  the chat: a header and seven lines
    TILE      (4, 8, 54, 54)       the other one, on a call: her face from her own webcam, and her name
    ALERT     (98, 4, 206, 27)     an alert dropping in at the top: a subscriber, a donation
    the captions                   y 159-180 (UI), with the singer's name on a tab above them
"""
from functools import lru_cache

from PIL import Image, ImageDraw

from engine import C, INK, KIT, H, W, Canvas, col, silk
from pixelart.streamui import StreamUI

CROP = {"emiru": (4, 18, 204, 126), "maya": (116, 18, 316, 126)}      # the part of her frame a window shows
FACE = {"emiru": (37, 18, 133, 90), "maya": (187, 18, 283, 90)}       # and the part the call tile does
ACCENT = {"emiru": "emiru", "maya": "maya", "both": "chat", "pair": "chat"}
NAME = {"emiru": "EMIRU", "maya": "MAYA", "both": "EMIRU + MAYA"}
NAME_COLORS = ("emiru_hi", "maya_hi", "chat", "pink", "sky", "orange", "red_hi", "green_hi", "blue_hi", "gold_hi")
TILE = (4, 8, 54, 54)
TICKER = (108, 76, 212, 86)          # in the shared frame: the newest chat message, under the window


@lru_cache(maxsize=None)
def logo(who):
    """Her mark, as it sits in the corner of her videos (13x13)."""
    f = Canvas(13, 13)
    if who == "emiru":                                                   # a cat's head, pink
        f.poly([(1, 5), (1, 0), (5, 3)], "emiru"); f.poly([(11, 5), (11, 0), (7, 3)], "emiru")
        f.ell((1, 3, 11, 11), "emiru"); f.pxs([(4, 6), (8, 6)], "white"); f.px((6, 8), "emiru_sh")
    else:                                                                # a leaf, green
        f.poly([(2, 10), (2, 5), (6, 1), (11, 2), (10, 7), (6, 10)], "maya"); f.line([(2, 11), (9, 4)], "maya_sh")
    return f.done()


def _cat(f):
    f.poly([(1, 4), (1, 0), (4, 2)], "ears"); f.poly([(7, 4), (7, 0), (4, 2)], "ears")
    f.ell((1, 2, 7, 7), "ears"); f.pxs([(3, 4), (5, 4)], "ink"); f.px((4, 6), "ears_sh")


def _cow(f):
    f.rect((1, 2, 7, 6), "angus"); f.rect((2, 5, 6, 7), "muzzle"); f.pxs([(3, 3), (5, 3)], "ink")
    f.pxs([(0, 2), (8, 2)], "angus_sh"); f.pxs([(3, 6), (5, 6)], "ink")


def _leaf(f):
    f.poly([(1, 7), (1, 4), (4, 1), (7, 1), (7, 4), (4, 7)], "maya"); f.line([(1, 7), (6, 2)], "maya_sh")


def _clap(f):
    f.rect((2, 3, 4, 7), "eskin"); f.rect((4, 2, 6, 6), "mskin"); f.pxs([(1, 1), (7, 1), (4, 0)], "yellow")


UI = StreamUI(KIT, (W, H), seats={"emiru": "left", "maya": "right", "pair": "centre"}, accent=ACCENT, names=NAME,
              crop=CROP, logo=logo, emotes={"cat": _cat, "cow": _cow, "leaf": _leaf, "clap": _clap},
              name_colors=NAME_COLORS, dark_tabs=("maya", "both"), chat_alpha=1.0)
PREVIEW, PW, PH, CHAT, CHAT_ROWS, ALERT, CAP_Y = UI.PREVIEW, UI.PW, UI.PH, UI.CHAT, UI.CHAT_ROWS, UI.ALERT, UI.CAP_Y
box, veil, preview_pic, pic_box, draw_preview, reactions = (UI.box, UI.veil, UI.preview_pic, UI.pic_box,
                                                            UI.draw_preview, UI.reactions)
emote, chat_rows, draw_chat, alert_icon, draw_alert, draw_captions = (UI.emote, UI.chat_rows, UI.draw_chat,
                                                                      UI.alert_icon, UI.draw_alert, UI.draw_captions)


def tile_pic(frame, who):
    """`who`'s face as her friend's call shows it (48 x 36): cut from her own webcam frame, at half size."""
    return frame.crop(FACE[who]).resize((48, 36), Image.BOX)


def draw_tile(world, host, pic, guest, talking, t):
    """The friend on a call, in the corner of `host`'s stream: her face, her name, and a ring in her colour
    that lights when she has something to say."""
    x0, y0, x1, y1 = box(host, TILE)
    d = ImageDraw.Draw(world)
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=INK)
    world.paste(pic, (x0 + 1, y0 + 1))
    d.rectangle((x0, y0 + 37, x1 - 1, y1 - 1), fill=C["bar"])
    silk(world, (x0 + 4, y0 + 40), NAME[guest], "text")
    for i in range(3):                                                   # a level meter by her name
        k = 1 + int(2.5 * abs(((t * 9 + i * 1.7) % 2) - 1)) if talking else 0
        d.rectangle((x1 - 12 + 3 * i, y1 - 4 - k, x1 - 11 + 3 * i, y1 - 3), fill=C["ok" if talking else "mute"])
    d.rectangle((x0 - 2, y0 - 2, x1 + 1, y1 + 1), outline=col(ACCENT[guest] + ("_hi" if talking else "")))
    if talking:
        d.rectangle((x0 - 3, y0 - 3, x1 + 2, y1 + 2), outline=col(ACCENT[guest]))


def draw_ticker(world, message, age):
    """The newest chat message on one line, where there is no room for a chat."""
    x0, y0, x1, y1 = TICKER
    if not message:
        return
    name, color, text = message
    veil(world, (x0 - 2, y0, x1 + 2, y1), "bg", 0.72)
    rows = chat_rows([(name, color, text)], x1 - x0 - 4)
    pane = Image.new("RGBA", (x1 - x0, 8), (0, 0, 0, 0))
    for x, word, c in rows[0]:
        if c is None:
            pane.alpha_composite(emote(word.strip(":")), (x, 0))
        else:
            silk(pane, (x, 1), word, c)
    world.paste(pane, (x0 + 1, y0 + 1 + (2 if age < 0.08 else 0)), pane)
