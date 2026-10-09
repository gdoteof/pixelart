"""A stream's overlay: the video its streamer is watching, his chat, and the captions.

The drawing is pixelart.streamui's, bound here to this video's palette and its two men. Hasan sits on the
left of his frame with the overlay on his right; Asmongold's stream is the mirror image, and `box(who, b)`
flips a box of Hasan's layout:
    PREVIEW   (212, 6, 316, 72)    the other man's video in a window: a title bar over a 100x54 picture
    CHAT      (232, 78, 316, 148)  the chat: a header and seven lines
    FEED      (118, 8, 202, 150)   side by side, the two chats run together down the middle of the frame
    ALERT     (98, 4, 206, 27)     an alert dropping in at the top: a subscriber, a donation, an achievement
    the captions                   y 159-180 (UI), with the singer's name on a tab above them

The video in the window is the other man's own webcam, shrunk: `preview_pic` cuts it out of his frame.
"""
from functools import lru_cache

from engine import KIT, H, W, Canvas, rgba
from pixelart.streamui import StreamUI

CROP = {"hasan": (0, 22, 200, 130), "asmon": (120, 22, 320, 130)}    # the part of a man's frame the window shows
ACCENT = {"hasan": "hasan", "asmon": "asmon", "chat": "chat", "both": "text"}
NAME = {"hasan": "HASANABI", "asmon": "ASMONGOLD", "chat": "CHAT", "both": "BOTH"}
NAME_COLORS = ("hasan_hi", "asmon_hi", "chat", "pink", "sky", "orange", "red_hi", "green_hi", "blue_hi", "gold_hi")


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


def _roach(f):
    f.ell((2, 2, 6, 6), "roach"); f.pxs([(1, 2), (1, 6), (7, 2), (7, 6), (4, 1)], "roach_sh")


def _clap(f):
    f.rect((2, 3, 4, 7), "hskin"); f.rect((4, 2, 6, 6), "askin"); f.pxs([(1, 1), (7, 1), (4, 0)], "yellow")


UI = StreamUI(KIT, (W, H), seats={"hasan": "left", "asmon": "right"}, accent=ACCENT, names=NAME, crop=CROP, logo=logo,
              emotes={"roach": _roach, "clap": _clap}, name_colors=NAME_COLORS, dark_tabs=("asmon", "chat", "both"))
PREVIEW, PW, PH, CHAT, CHAT_ROWS, FEED, ALERT, CAP_Y = (UI.PREVIEW, UI.PW, UI.PH, UI.CHAT, UI.CHAT_ROWS, UI.FEED,
                                                        UI.ALERT, UI.CAP_Y)
box, veil, preview_pic, pic_box, draw_preview, reactions = (UI.box, UI.veil, UI.preview_pic, UI.pic_box,
                                                            UI.draw_preview, UI.reactions)
pause_icon, emote, chat_rows, draw_chat, alert_icon, draw_alert, draw_captions = (
    UI.pause_icon, UI.emote, UI.chat_rows, UI.draw_chat, UI.alert_icon, UI.draw_alert, UI.draw_captions)
