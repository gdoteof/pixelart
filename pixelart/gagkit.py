"""Helpers for the per-line gags of a video staged as a stream (pixelart.gags, pixelart.streamui).

A project binds one to its gag registry, its song, its palette and its overlay, and its own gagkit.py
re-exports the methods next to whatever else its gags draw with:

    K = GagKit(GAGS, SONG, KIT, UI)
    gag, when, pose, hold, show, say = K.gag, K.when, K.pose, K.hold, K.show, K.say

    @gag("v1", 3)
    def crown(c, L):
        show(c, crown_pic(), "EXHIBIT")          # setup: a picture in the host's window
        pose(c, "hasan", arms="point")
        yield "front"
        say(c, 120, 60, "MINE", L.age("crown"))

The frame context `c` is the video's own. These helpers expect of it: `c.st[who]`, a dict of pose fields
with "arms", "held" and "gesture" (whether the automatic gestures may move the arms); `c.window`, a dict
with pic, title, badge, paused, progress and shake; `c.host`, whose overlay is on screen; `c.world`, the
frame being drawn; and `c.add_shake(amount)`.
"""
from PIL import ImageDraw

from pixelart import fx, timing
from pixelart.anim import pop_dy
from pixelart.kit import PRESS, PRESS16, silk_w


class GagKit:
    def __init__(self, gags, song, kit, ui):
        self.gags, self.song, self.kit, self.ui = gags, song, kit, ui

    def gag(self, sec, idx, pre=0.12, post=0.5):
        """Register a line's gag. It runs from just before its line until half a second into the next one,
        so a punchline on the last word stays up while the next gag starts (the later gag's poses win). A
        section's last line runs to the end of the section and no further, and its first doesn't start
        before the cut to it: the frame either side is somebody else's."""
        song = self.song
        last = (sec, idx + 1) not in {(ln["sec"], ln["idx"]) for ln in song.lines}
        if idx == 0:
            pre = min(pre, song.line(sec, 0)["t0"] - song.section_start(sec))
        return self.gags.gag(sec, idx, pre, 0.0 if last else post)

    def when(self, sec, idx, pat=None, n=0):
        """The time a line starts (or a word in it is sung), for gags that outlive their line."""
        ln = self.song.line(sec, idx)
        return ln["t0"] if pat is None else timing.word_time(ln, pat, "t0", n)

    @staticmethod
    def pose(c, who, **kw):
        """Set pose fields and stop the automatic gestures from overriding the arms."""
        s = c.st[who]
        if "arms" in kw:
            s["gesture"] = False
        s.update(kw)

    @staticmethod
    def hold(c, who, prop, arms="show", at=None):
        """Have `who` hold a prop in front of them: a sheet shown to the camera by its bottom corners
        ("show"), or something smaller in both hands at the chest ("hold")."""
        s = c.st[who]
        s["arms"], s["held"], s["gesture"] = arms, (prop, at or ("hands_top" if arms == "show" else "hands")), False

    @staticmethod
    def hold_up(c, who, prop, lift=0):
        """One hand raises a prop: the far hand, the prop's bottom in the fist."""
        s = c.st[who]
        s["arms"], s["gesture"] = "hold1", False
        s["held"] = (prop, ("hand_far", prop.height // 2 - 2 + lift))

    # --- the window ----------------------------------------------------------------------------------

    @staticmethod
    def show(c, pic, title=None, badge="CLIP", a=0.0):
        """Put a picture in the host's window from age `a`, in place of what it was showing. It starts
        clean, whatever the gag before it was doing to the window (playing a video, shaking it)."""
        if a < 0:
            return
        c.window.update(pic=getattr(pic, "img", pic), title=title, badge=badge, paused=False, progress=0.02, shake=0)

    def alert(self, c, a, title, text=None, icon="star", dur=2.6, host=None, accent=None):
        """An alert on the host's stream from age `a`: call it in a phase that draws on c.world."""
        self.ui.draw_alert(c.world, host or c.host, a, title, text, icon, dur, accent)

    def win(self, c, x, y):
        """A point of the window's picture, in the world."""
        x0, y0, _, _ = self.ui.pic_box(c.host)
        return x0 + x, y0 + y

    # --- words over the picture ------------------------------------------------------------------------

    def say(self, c, x, y, lines, a, dur=None, fnt=PRESS, tail=None, img=None):
        """A speech bubble with its bottom centre at a world point, from age a (until a reaches dur)."""
        if a < 0 or (dur is not None and a > dur):
            return
        lines = [lines] if isinstance(lines, str) else list(lines)
        pop = pop_dy(a, 0.12, 5) or 0
        kw = dict(text_dy=0) if fnt is PRESS else dict(text_dy=-3, line_h=8)
        fx.bubble(img or c.world, int(x), int(y + pop), lines, tail=tail, fnt=fnt, fill=self.kit.col("white"),
                  ink=self.kit.ink, **kw)

    def label(self, c, x, y, s, a, dur=None, bg="white", fg="ink", img=None):
        """A plate with a few words on it, popping in centred on a world point from age a."""
        if a < 0 or (dur is not None and a > dur):
            return
        img = img or c.world
        w = silk_w(s) + 6
        x0, y0 = int(x - w // 2), int(y - 5 + (pop_dy(a, 0.12, 4) or 0))
        d = ImageDraw.Draw(img)
        d.rectangle((x0 - 1, y0 - 1, x0 + w, y0 + 9), fill=self.kit.ink)
        d.rectangle((x0, y0, x0 + w - 1, y0 + 8), fill=self.kit.col(bg))
        self.kit.silk(img, (x0 + 3, y0 + 2), s, fg)

    def shout(self, c, x, y, s, a, size=16, top="gold", bottom="orange", dur=None, img=None):
        """Arcade text popping in at a world point from age a (until a reaches dur)."""
        if a < 0 or (dur is not None and a > dur):
            return
        col = self.kit.col
        fx.pop_text(img or c.world, int(x), int(y), s, a, PRESS16 if size == 16 else PRESS, col(top), col(bottom),
                    col("black"), anchor="mm", ink=self.kit.ink)

    def stamp(self, c, x, y, s, a, color="red", angle=-12, fnt=PRESS, img=None):
        """A rubber stamp slammed onto a world point at age 0."""
        if a < 0:
            return
        fx.stamp(img or c.world, int(x), int(y), s, fnt=fnt, color=self.kit.col(color), angle=angle, age=a)

    @staticmethod
    def jolt(c, a, amount=4, dur=0.3):
        """Shake the whole frame as something lands."""
        if 0 <= a < dur:
            c.add_shake(amount * (1 - a / dur))
