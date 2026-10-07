"""Frame renderer for Play the Video: Hasan and Asmongold, each on his own stream, reacting to the other's.

The frame is the stream of whoever is rapping: his webcam, full screen, in the room he streams from, under
his overlay. The window in the corner is the video he's watching, which is the other man's stream, paused;
under it is his chat. For the hooks the two streams sit side by side and chat does the talking. The frame
never moves: the cuts are from one stream to the other.

render_frame(t) builds one 1920x1080 frame: a 320x180 world plus a 320x180 UI layer, shown at 6x. Per-line
gags (gags_*.py, see gagkit.py) hook into its phases:

    <setup>  poses, props, what the window shows, the view: gags change `c` here (c.st[who], c.window...)
    "back"   each man's webcam frame, behind his figure: c.cam[who], 320x180
    "mid"    each webcam frame, in front of the figure and his desk (c.anchor[who] is known by now)
    "front"  the world: the frame as cut together, over the overlay's window and chat
    "ui"     UI layer, under the captions
    "top"    UI layer, over everything
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

import chatlog
import office
import rooms
import stream
import timeline as TL
from characters import FW, figure
from engine import C, INK, SILK, H, W, blend, col, rgba, rnd
from pixelart import pixel
from pixelart.camera import Cam, compose, shake_offset
from pixelart.figure import pick
from pixelart.gags import Gags

FPS = TL.FPS
PHASES = ("back", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
MEN = TL.MEN
OTHER = TL.OTHER
STATE = ("arms", "lean", "bob", "eyes", "brows", "mouth", "flush")
REST_MOUTH = {"hasan": "smile", "asmon": "closed"}
CAM = Cam(W / 2, H / 2, 6)


def default_state(who):
    return dict(hidden=False, dx=0, dy=0, arms="desk", lean=1, bob=0, eyes="open", brows="neutral",
                mouth=REST_MOUTH[who], flush=0, held=None, gesture=True, react=True, sweat=False, tears=False,
                outfit=None, hat=None, shake=0, facing=rooms.FACING[who], grey=0.0)


# --- per-frame context -----------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.view = TL.VIEW[self.sec]                      # whose stream is on screen, or "split"
        self.st = {w: default_state(w) for w in MEN}
        self.vars = {}
        self.subs = True                                   # the captions
        self.overlay = True                                # the window and the chat
        self.hitfx = True                                  # flinches and reactions on punchlines
        # The window on the host's stream: the other man's video, paused where the host stopped it, unless
        # a gag shows a picture there (pic, with its title) or lets the video play.
        self.window = dict(pic=None, title=None, badge=None, paused=True, progress=0.02, shake=0)
        self.cam_t = {w: t for w in MEN}                   # each webcam's own clock: a paused video's stands still
        self.chat = []                                     # extra chat lines from gags: (name, colour, text)
        self.feed = None                                   # side by side: what the chat down the middle says, if a
        self.feed_age = 9.0                                # gag scripts it (and how long since its newest line)
        self.office = None                                 # the view from a viewer's desk: see office.py
        self.flash, self.flash_color = 0.0, C["white"]
        self.shake = 0.0
        self.world = self.ui = None
        self.cam, self.anchor = {}, {}

    @property
    def host(self):
        return self.view if self.view in MEN else None

    @property
    def guest(self):
        return OTHER[self.view] if self.view in MEN else None

    def get(self, key, default=None):
        return self.vars.get(key, default)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color

    def at(self, who, name="head"):
        """A point on someone in his webcam frame (which, for whoever is on screen, is the world): an anchor
        of a figure drawn this frame (from the "mid" phase on)."""
        return self.anchor[who][name]

    def to_ui(self, x, y):
        return CAM.ui(x, y)


# --- mannerisms --------------------------------------------------------------------------------
# A rapper changes gesture every two beats. Hasan performs: the open palm, the point, the chop, a fist, a
# hand on his chest. Asmongold barely moves: hands on the desk, a shrug, a finger, a hand in his hair.

TALK = {"hasan": (("palm", 3), ("point", 3), ("shrug", 2), ("chop", 2), ("finger", 2), ("chest", 2), ("fist", 1),
                  ("guns", 1)),
        "asmon": (("desk", 3), ("palm", 3), ("shrug", 3), ("finger", 2), ("hair", 2), ("point", 2), ("chin", 1))}
# The frame each man's video was stopped on, by the section it sits through: nobody pauses on a good one.
PAUSED = {"intro": dict(arms="palm", eyes="half", brows="up", mouth="open"),
          "v1": dict(arms="palm", eyes="half", brows="up", mouth="open"),
          "v2": dict(arms="point", eyes="squint", brows="angry", mouth="wide"),
          "v3": dict(arms="hair", eyes="shut", brows="worried", mouth="o"),
          "v4": dict(arms="finger", eyes="up", brows="up", mouth="grit")}


def singing(c, who):
    ln = c.ln
    if ln is None or ln["who"] not in (who, "both"):
        return False
    return ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.45 and TL.loudness(c.t) > 0.1


def mouth_for(who, loud):
    if loud < 0.12:
        return REST_MOUTH[who]
    if loud < 0.4:
        return "open"
    if loud < 0.72:
        return "grin" if who == "hasan" else "open"
    return "wide"


def pose_rapper(c, who):
    s = c.st[who]
    ln = c.ln
    mine = ln is not None and ln["who"] == who
    if s["gesture"]:
        s["arms"] = pick(TALK[who], c.beat_i // 2, who, "gesture")
        if mine and (ln["sec"], ln["idx"]) in TL.KILL_SHOTS:
            if TL.last_word(ln) - 0.15 <= c.t <= TL.last_word(ln) + 0.9:    # the punchline: point at him
                s["arms"] = "point"
    s["bob"] = 2 if c.ph < 0.3 else 0
    s["lean"] = 3 if who == "hasan" else 1
    s["mouth"] = mouth_for(who, TL.loudness(c.t)) if singing(c, who) else REST_MOUTH[who]
    if who == "hasan":
        s["brows"] = "up" if s["arms"] in ("shrug", "palm", "chest") else "angry" if s["arms"] in ("point", "chop", "fist") \
            else "skeptic"
        s["eyes"] = "side" if s["arms"] in ("point", "guns") else "open"
    else:
        s["brows"] = "up" if s["arms"] in ("shrug", "palm") else "neutral"
        s["eyes"] = "half" if s["arms"] in ("desk", "hair", "chin") and c.beat_i % 4 == 3 else \
            "side" if s["arms"] == "point" else "open"


def pose_paused(c, who):
    """The other man, in the window: stopped mid-word on the frame the host paused at."""
    s = c.st[who]
    s.update(PAUSED.get(c.sec, PAUSED["v1"]))
    s["gesture"] = False
    s["lean"] = 1
    c.cam_t[who] = TL.section_start(c.sec)


def pose_listener(c, who):
    """Side by side, while chat has the floor."""
    s = c.st[who]
    bar = c.beat_i // 4
    s["lean"] = 1
    if who == "hasan":
        if s["gesture"]:
            s["arms"] = ("cross", "chin", "cross", "desk")[(bar // 2) % 4]
        s["mouth"] = "smirk" if bar % 4 != 3 else "closed"
        s["eyes"] = "side" if bar % 3 == 1 else "open"
        s["brows"] = "skeptic" if bar % 2 else "neutral"
    else:
        if s["gesture"]:
            s["arms"] = ("desk", "hair", "chin", "desk")[(bar // 2) % 4]
        s["mouth"] = "closed"
        s["eyes"] = "half" if bar % 3 == 0 else "side" if bar % 3 == 1 else "open"
        s["brows"] = "neutral"


def blink_eyes(c):
    for who, s in c.st.items():
        if who == c.guest and c.window["paused"]:
            continue
        period, off = {"hasan": (3.1, 0.7), "asmon": (4.3, 2.2)}[who]
        if s["eyes"] in ("open", "half", "side") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The target flinches as each line lands, and reels from the big ones: even in a paused video."""
    for who in MEN:
        h = TL.last_hit(c.t, target=who, window=1.6)
        s = c.st[who]
        if not h or not s["react"]:
            continue
        if c.ln is not None and c.ln["who"] == who and h["line"]["gi"] < c.ln["gi"]:
            continue                                                      # it's his verse now: he has the floor
        age, big = c.t - h["t"], h["big"]
        if age < (1.3 if big else 0.6):
            s["eyes"] = "wide" if big else "side"
            s["brows"] = "worried"
            s["mouth"] = "o" if big and age < 0.5 else "frown"
            if big:
                s["flush"] = 1
                s["sweat"] = True
                if age < 0.7 and s["gesture"]:
                    s["arms"] = "facepalm" if who == "hasan" else "desk"
        if age < 0.3:
            if who == c.guest:
                c.window["shake"] = max(c.window["shake"], 2 if big else 1)
            else:
                s["shake"] = max(s["shake"], 2 if big else 1)
            if big:
                c.add_shake(3 * (1 - age / 0.3))


# --- drawing a webcam frame ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def start_cam(c, who):
    img = rooms.ROOM[who]().copy()
    t = c.cam_t[who]
    if who == "asmon":
        rooms.roaches(img, t)
        rooms.flies(img, 151, 84, t)
    else:
        rooms.neon_flicker(img, t)
    c.cam[who] = img


def draw_figure(c, who):
    s = c.st[who]
    img = c.cam[who]
    spr, a = figure(who, facing=s["facing"], held=s["held"], outfit=s["outfit"], **{k: s[k] for k in STATE})
    pad = (spr.width - FW) // 2                                           # figure() pads for a wide held prop
    fx, fy = rooms.FIG[who]
    x, y = fx + int(round(s["dx"])) - pad, fy + int(round(s["dy"])) - pad
    anchors = {k: (px + x, py + y) for k, (px, py) in a.items()}
    c.anchor[who] = anchors
    if not s["hidden"]:
        img.paste(spr, (x, y), spr)
        hx, hy = anchors["head"]
        if s["hat"]:                                                      # a sprite drawn facing right, 60 wide
            hat, dy = s["hat"]
            hat = hat if s["facing"] > 0 else hat.transpose(Image.FLIP_LEFT_RIGHT)
            img.paste(hat, (hx - hat.width // 2, hy + dy), hat)
        if s["sweat"]:
            d = sweat_drop()
            img.paste(d, (int(hx - s["facing"] * 27), int(hy + 10 + int(c.cam_t[who] * 6) % 3)), d)
        if s["tears"]:                                                    # down the near cheek
            ex, ey = anchors["eye"]
            dd = ImageDraw.Draw(img)
            dd.line([(ex, ey + 4), (ex, ey + 12)], fill=C["tear"], width=2)
            dd.point((ex, ey + 13 + int(c.t * 10) % 2), fill=C["tear"])
    desk = rooms.DESK[who]()
    img.paste(desk, (0, 0), desk)


def shaken(img, amount, key, bg="bg"):
    if not amount:
        return img
    a = rnd("camshake", key) * 2 * math.pi
    moved = Image.new("RGB", img.size, C[bg])
    moved.paste(img, (int(round(math.cos(a) * amount)), int(round(math.sin(a) * amount))))
    return moved


# --- cutting the frame together -------------------------------------------------------------------------

def draw_view(c):
    """The world: the host's webcam with his overlay on it, or both webcams side by side with one chat
    between them, or (c.office) that split screen on a monitor at somebody's work."""
    if c.office is not None:
        both = Ctx.__new__(Ctx)
        both.__dict__.update(c.__dict__)
        both.world, both.office = Image.new("RGB", (W, H), C["bg"]), None
        draw_view(both)
        office.draw(c.world, both.world, c.t, **c.office)
        return
    if c.view == "split":
        c.world.paste(shaken(c.cam["hasan"], c.st["hasan"]["shake"], ("hasan", c.f)).crop((0, 0, W // 2, H)), (0, 0))
        c.world.paste(shaken(c.cam["asmon"], c.st["asmon"]["shake"], ("asmon", c.f)).crop((W // 2, 0, W, H)), (W // 2, 0))
        d = ImageDraw.Draw(c.world)
        d.rectangle((W // 2 - 1, 0, W // 2, H), fill=INK)
        if c.overlay:
            lines, age = (c.feed, c.feed_age) if c.feed is not None else chatlog.both(c.t)
            stream.draw_chat(c.world, None, lines[-16:], age, chatlog.viewers(None, c.t), at=stream.FEED,
                             accent=("hasan", "asmon"))
        return
    host, guest = c.host, c.guest
    c.world.paste(shaken(c.cam[host], c.st[host]["shake"], (host, c.f)), (0, 0))
    if not c.overlay:
        return
    w = c.window
    pic = w["pic"] if w["pic"] is not None else stream.preview_pic(c.cam[guest], guest)
    a = rnd("winshake", c.f) * 2 * math.pi
    off = (int(round(math.cos(a) * w["shake"])), int(round(math.sin(a) * w["shake"])))
    badge = w["badge"] or ("0:01" if w["paused"] else "LIVE")
    stream.draw_preview(c.world, host, pic, w["title"] or stream.NAME[guest], stream.ACCENT[guest], w["paused"],
                        w["progress"], off, badge, guest if w["pic"] is None else None)
    if c.hitfx and w["pic"] is None:
        for h in TL.HITS:
            if h["big"] and h["target"] == guest:
                stream.reactions(c.world, host, c.t - h["t"], h["t"])
    lines, age = chatlog.tail(host, c.t)
    stream.draw_chat(c.world, host, lines + c.chat, 9.0 if c.chat else age, chatlog.viewers(host, c.t))


def draw_captions(c):
    ln = c.ln
    if not ln or not c.subs:
        return
    words = [w["w"] for w in ln["words"]]
    side = c.host if ln["who"] in ("chat", "both") else ln["who"]
    stream.draw_captions(c.ui, words, TL.word_index(ln, c.t), ln["who"], side)


# --- the frame ------------------------------------------------------------------------------------------

def setup(c):
    if c.t >= TL.MAO_AT:                                                # Hasan's second video: he has changed
        c.st["hasan"]["outfit"] = "mao"
    for who in MEN:
        if c.view == "split":
            c.st[who]["dx"] = -8 * rooms.FACING[who]                     # apart, to make room for the chat
            if c.ln is not None and c.ln["who"] == "both":
                pose_rapper(c, who)
            else:
                pose_listener(c, who)
        elif who == c.host:
            pose_rapper(c, who)
        else:
            pose_paused(c, who)


def build_frame(t, tweak=None):
    """Draw the frame at time t. Returns the context, with its world and ui ready to compose.
    `tweak(c)`, if given, runs after the gags' setup (thumbnails use it to turn the overlay off)."""
    import gags  # noqa: F401  (registers the per-line gags into GAGS)
    c = Ctx(t)
    setup(c)
    runner = GAGS.runner(c, t, TL.LINES, TL.section_end)
    if tweak:
        tweak(c)
    blink_eyes(c)
    if c.hitfx:
        apply_hits(c)
    c.world = Image.new("RGB", (W, H), C["bg"])
    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for who in MEN:
        start_cam(c, who)
    runner.run("back")
    for who in MEN:
        draw_figure(c, who)
    runner.run("mid")
    draw_view(c)
    runner.run("front")
    if c.flash > 0:
        blend(c.world, 1.0, c.flash_color, min(1.0, c.flash))
    runner.run("ui")
    draw_captions(c)
    runner.run("top")
    return c


def render_frame(t):
    c = build_frame(t)
    return compose(c.world, c.ui, CAM, shake_offset(c.shake, c.f))


def label(t):
    ln = TL.line_at(t)
    return f"{ln['sec']}.{ln['idx']} {ln['text']}" if ln else TL.section_at(t)[0]


__all__ = ["FPS", "render_frame", "label", "build_frame", "GAGS", "Ctx", "col", "rgba", "SILK"]
