"""A streamer's overlay, drawn in a 320x180 world: the window in the corner, the chat, alerts, captions.

A video about people who stream binds one to its palette and its cast, and re-exports the methods:

    UI = StreamUI(KIT, (W, H), seats={"hasan": "left", "asmon": "right"},
                  accent={"hasan": "hasan", "asmon": "asmon", "chat": "chat", "both": "text"},
                  names={"hasan": "HASANABI", "asmon": "ASMONGOLD", "chat": "CHAT", "both": "BOTH"},
                  crop={"hasan": (0, 22, 200, 130), "asmon": (120, 22, 320, 130)}, logo=logo)

World layout on the stream of someone who sits on the left; `box(who, b)` flips a box for anyone else:
    PREVIEW   (212, 6, 316, 72)    a window: a title bar over a PW x PH picture (100 x 54)
    CHAT      (232, 78, 316, 148)  the chat: a header and seven lines
    FEED      (118, 8, 202, 150)   side by side, the two chats run together down the middle of the frame
    ALERT     (98, 4, 206, 27)     an alert dropping in at the top: a subscriber, a donation, an achievement
                                   (it grows away from the window to fit its words)
    the captions                   y 159-180 (UI), with the singer's name on a tab above them

The palette needs "bar", "bg", "text", "dim", "mute", "live", "white", "line" and "gold" for the panels
and the captions, each accent colour with its "_hi", and the colours the emotes and alert icons use
("yellow", "mouth", "tear", "orange", "green", "green_sh", "red", "gold_hi", "gold_sh", "grey", "grey_hi",
"brown").
"""
import math

from PIL import Image, ImageDraw

from pixelart import pixel
from pixelart.anim import k_in, rnd
from pixelart.kit import SILK, silk_w

NAME_COLORS = ("chat", "pink", "sky", "orange", "red_hi", "green_hi", "blue_hi", "gold_hi")


class StreamUI:
    PREVIEW = (212, 6, 316, 72)
    PW, PH = 100, 54
    CHAT = (232, 78, 316, 148)
    CHAT_ROWS = 7
    FEED = (118, 8, 202, 150)
    ALERT = (98, 4, 206, 27)
    CAP_Y = 159

    def __init__(self, kit, size, seats, accent, names, crop, logo=None, emotes=None, name_colors=NAME_COLORS,
                 dark_tabs=("chat", "both"), chat_alpha=0.78):
        """`seats` says which side of his own frame each streamer sits on ("left": his overlay is on the
        right, as laid out above; "centre" is a frame two of them share, with the overlay between them).
        `accent` and `names` are a palette colour and a display name for each
        speaker; `crop` is the part of each streamer's frame a window shows; `logo(who)` is a 13x13 mark
        for the corner of his videos; `emotes` adds kinds to the chat's (kind -> draw(canvas), on 9x9);
        `dark_tabs` are the speakers whose caption tab is bright enough to want dark letters; `chat_alpha` is
        how much of the room the chat panel hides (a pale room wants more)."""
        self.kit, (self.W, self.H) = kit, size
        self.seats, self.accent, self.names, self.crop = seats, accent, names, crop
        self.logo, self.extra_emotes = logo, dict(emotes or {})
        self.name_colors, self.dark_tabs, self.chat_alpha = tuple(name_colors), tuple(dark_tabs), chat_alpha
        self._emotes, self._icons, self._pause = {}, {}, {}

    def box(self, who, b):
        """A box of the left-seat layout, where it goes on `who`'s stream."""
        x0, y0, x1, y1 = b
        seat = self.seats.get(who)
        if seat == "centre":
            x = (self.W - (x1 - x0)) // 2
            return (x, y0, x + x1 - x0, y1)
        return b if seat == "left" else (self.W - x1, y0, self.W - x0, y1)

    def veil(self, img, b, color, alpha):
        """Darken (or tint) a box of an RGB image: a translucent panel."""
        x0, y0, x1, y1 = b
        part = img.crop((x0, y0, x1, y1))
        img.paste(Image.blend(part, Image.new("RGB", part.size, self.kit.col(color)), alpha), (x0, y0))

    # --- the window -----------------------------------------------------------------------------------

    def preview_pic(self, frame, who):
        """`who`'s webcam frame as someone else's window shows it (PW x PH): the middle of it, at half size."""
        return frame.crop(self.crop[who]).resize((self.PW, self.PH), Image.BOX)

    def pic_box(self, host):
        x0, y0, x1, y1 = self.box(host, self.PREVIEW)
        return (x0 + 2, y0 + 10, x0 + 2 + self.PW, y0 + 10 + self.PH)

    def draw_preview(self, world, host, pic, title, accent, paused=True, progress=0.02, shake=(0, 0), badge=None,
                     mark=None):
        """The window on `host`'s stream: a title bar, the picture (PW x PH), and the player's bar under it.
        `badge` is a short word at the right of the title bar (the time, "LIVE", "CLIP"); `mark` puts that
        streamer's logo in the picture's corner."""
        C, INK, col, silk = self.kit.pal, self.kit.ink, self.kit.col, self.kit.silk
        PW, PH = self.PW, self.PH
        x0, y0, x1, y1 = self.box(host, self.PREVIEW)
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
        if mark and self.logo:
            m = self.logo(mark)
            world.paste(m, (px + PW - 15, py + 2), m)
        if paused:
            icon = self.pause_icon()
            world.paste(icon, (px + 3, py + PH - 18), icon)
        d = ImageDraw.Draw(world)
        d.rectangle((x0, y0 + 9, x1 - 1, y1 - 1), outline=C["bar"])
        d.rectangle((x0 + 1, y0 + 9, x1 - 2, y1 - 1), outline=C["bar"])
        d.line([(px, py + PH - 2), (px + PW - 1, py + PH - 2)], fill=C["mute"])        # the player's bar
        k = max(2, int(round(PW * min(1.0, progress))))
        d.line([(px, py + PH - 2), (px + k, py + PH - 2)], fill=C["live"])
        d.rectangle((px + k - 1, py + PH - 3, px + k, py + PH - 1), fill=C["white"])
        d.rectangle((x0 - 2, y0 - 2, x1 + 1, y1 + 1), outline=col(accent))

    def reactions(self, world, host, age, seed, kinds=("lul", "skull", "fire", "lul", "skull", "clap")):
        """What chat throws at whoever is in the window when a big one lands: emotes drifting up the picture."""
        if not 0 <= age < 2.2:
            return
        x0, y0, x1, y1 = self.pic_box(host)
        part = world.crop((x0, y0, x1, y1 - 3)).convert("RGBA")
        for j in range(7):
            a = age - j * 0.12
            if not 0 <= a < 1.5:
                continue
            x = 8 + int(rnd("rx", seed, j) * (self.PW - 26)) + int(3 * math.sin(a * 5 + j))
            e = self.emote(kinds[j % len(kinds)])
            part.alpha_composite(e, (x, int((self.PH - 10) * (1 - a / 1.5))))
        world.paste(part.convert("RGB"), (x0, y0))

    def pause_icon(self, n=1):
        if n not in self._pause:
            f = self.kit.Canvas(13 * n, 13 * n)
            f.rect((2 * n, 1 * n, 5 * n - 1, 11 * n), "white")
            f.rect((7 * n, 1 * n, 10 * n - 1, 11 * n), "white")
            self._pause[n] = f.done()
        return self._pause[n]

    # --- the chat ---------------------------------------------------------------------------------------

    def emote(self, kind):
        """A little picture a chatter posts instead of a word (7x7): lul skull fire frog heart, and the
        video's own."""
        if kind not in self._emotes:
            f = self.kit.Canvas(9, 9)
            if kind in self.extra_emotes:
                self.extra_emotes[kind](f)
            elif kind == "lul":                                              # crying with laughter
                f.ell((1, 1, 7, 7), "yellow"); f.pxs([(2, 3), (3, 2), (5, 2), (6, 3)], "ink")
                f.rect((3, 5, 5, 6), "mouth"); f.pxs([(1, 4), (7, 4)], "tear")
            elif kind == "skull":
                f.ell((1, 1, 7, 6), "white"); f.rect((3, 5, 5, 7), "white")
                f.pxs([(3, 3), (5, 3)], "ink"); f.px((4, 7), "ink")
            elif kind == "fire":
                f.poly([(4, 1), (7, 4), (6, 7), (2, 7), (1, 4), (3, 3)], "orange"); f.pxs([(4, 5), (4, 6), (3, 6)], "yellow")
            elif kind == "frog":
                f.ell((1, 2, 7, 7), "green"); f.pxs([(2, 3), (6, 3)], "white"); f.line([(3, 6), (5, 6)], "green_sh")
            elif kind == "heart":
                f.rect((1, 2, 3, 4), "red"); f.rect((5, 2, 7, 4), "red"); f.rect((2, 4, 6, 5), "red"); f.rect((3, 6, 5, 6), "red")
                f.px((4, 7), "red")
            self._emotes[kind] = f.img
        return self._emotes[kind]

    def chat_rows(self, messages, width):
        """Lay messages out as rows of (x, word or emote, colour) runs: a name, then what it typed, which goes
        on a row of its own (indented) when it doesn't fit beside the name, and wraps."""
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

    def draw_chat(self, world, host, messages, age, viewers, title="CHAT", at=None, accent=None):
        """A chat panel showing the tail of `messages` ((name, colour, text), oldest first); `age` is seconds
        since the newest arrived, and slides it in. It is `host`'s panel, or any box `at`."""
        C, col, silk = self.kit.pal, self.kit.col, self.kit.silk
        x0, y0, x1, y1 = at or self.box(host, self.CHAT)
        self.veil(world, (x0, y0, x1, y1), "bg", self.chat_alpha)
        d = ImageDraw.Draw(world)
        d.rectangle((x0, y0, x1 - 1, y0 + 8), fill=C["bar"])
        for i, a in enumerate(accent or (self.accent[host],)):
            d.rectangle((x0 + 3 * i, y0, x0 + 3 * i + 2, y0 + 8), fill=col(a))
        silk(world, (x0 + 5 + 3 * (len(accent or "x") - 1), y0 + 2), title, "text")
        silk(world, (x1 - 3, y0 + 2), viewers, "dim", anchor="ra")
        d.ellipse((x1 - 8 - silk_w(viewers), y0 + 3, x1 - 6 - silk_w(viewers), y0 + 5), fill=C["live"])
        width = x1 - x0 - 6
        rows = self.chat_rows(messages, width)
        h = (y1 - y0 - 13) // 8 * 8
        pane = Image.new("RGBA", (x1 - x0 - 4, h), (0, 0, 0, 0))
        slide = int(round((1 - k_in(age, 0.12)) * 8 * len(self.chat_rows(messages[-1:], width)))) if messages else 0
        y = h - 8 * len(rows) + slide
        for row in rows:
            if 0 <= y < h:
                for x, word, color in row:
                    if color is None:
                        pane.alpha_composite(self.emote(word.strip(":")), (x, max(0, y - 1)))
                    else:
                        silk(pane, (x, y + 1), word, color)
            y += 8
        world.paste(pane, (x0 + 3, y0 + 11), pane)

    # --- alerts ------------------------------------------------------------------------------------------

    def alert_icon(self, kind):
        """A 15x15 picture for an alert: star (a subscriber), coin (a donation), cup (an achievement), hammer
        (a ban), bell, or any emote's name."""
        if kind in self._icons:
            return self._icons[kind]
        f = self.kit.Canvas(15, 15)
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
            e = self.emote(kind)
            self._icons[kind] = e.resize((e.width * 2, e.height * 2), Image.NEAREST).crop((0, 0, 15, 15))
            return self._icons[kind]
        self._icons[kind] = f.done()
        return self._icons[kind]

    def draw_alert(self, world, host, age, title, text=None, icon="star", dur=2.6, accent=None):
        """An alert on `host`'s stream, from age 0 for `dur` seconds: it drops in at the top of the frame and
        lifts out again. An icon, a title in the stream's colour, and a line under it."""
        if not 0 <= age < dur:
            return
        C, INK, col, silk = self.kit.pal, self.kit.ink, self.kit.col, self.kit.silk
        w = 24 + max(silk_w(title), silk_w(text or "")) + 6                # as wide as its words, growing away from
        x0, y0, x1, y1 = self.ALERT                                        # the window
        x0, y0, x1, y1 = self.box(host, (min(x0, x1 - w), y0, x1, y1))
        if self.seats.get(host) != "left":
            x1 = max(x1, x0 + w)
        k = min(k_in(age, 0.14), 1 - k_in(age - (dur - 0.14), 0.14))
        y0 -= int(round((1 - k) * (y1 + 2)))
        y1 = y0 + (self.ALERT[3] - self.ALERT[1])
        if y1 <= 0:
            return
        accent = accent or self.accent[host]
        d = ImageDraw.Draw(world)
        d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=INK)
        d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=C["bar"])
        d.rectangle((x0, y0, x0 + 1, y1 - 1), fill=col(accent)); d.rectangle((x1 - 2, y0, x1 - 1, y1 - 1), fill=col(accent))
        im = self.alert_icon(icon)
        bob = -1 if int(age * 6) % 2 == 0 and age < 0.9 else 0
        world.paste(im, (x0 + 5, max(-15, y0 + 4 + bob)), im)
        if text is None:
            silk(world, (x0 + 24, y0 + 8), title, accent + "_hi")
        else:
            silk(world, (x0 + 24, y0 + 3), title, accent + "_hi")
            silk(world, (x0 + 24, y0 + 12), text, "text")

    # --- the captions -----------------------------------------------------------------------------------

    def draw_captions(self, ui, words, now, who, side=None, sound=lambda w: False):
        """The line being sung, along the bottom: sung words bright, the current one gold. `who` names the
        tab, which sits on the side of the frame its singer does."""
        col, silk = self.kit.col, self.kit.silk
        W, H = self.W, self.H
        d = ImageDraw.Draw(ui)
        rows = pixel.wrap(words, W - 16, SILK)[:2]
        y0 = self.CAP_Y
        d.rectangle((0, y0, W, H), fill=(12, 12, 20, 236))
        accent = col(self.accent.get(who, "line"))
        d.line([(0, y0), (W, y0)], fill=accent + (255,))
        space = silk_w(" ")
        for r, row in enumerate(rows):
            x, y = 8, y0 + 4 + 8 * r + (4 if len(rows) == 1 else 0)
            for i in row:
                silk(ui, (x, y), words[i], "gold" if i == now else "text" if i < now else (146, 150, 178))
                x += silk_w(words[i]) + space
        if who in self.names:
            name = self.names[who]
            nw = silk_w(name) + 8
            x = W - 6 - nw if self.seats.get(side or who) == "right" else 6
            d.rectangle((x, y0 - 10, x + nw, y0 - 1), fill=accent + (255,))
            silk(ui, (x + 4, y0 - 8), name, "ink" if who in self.dark_tabs else "text")
