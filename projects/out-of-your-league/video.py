"""Frame renderer for Out of Your League: Emiru and Maya Higa, each on her own stream, then together.

A verse is the stream of whoever raps it: her webcam, full screen, in the place she streams from, under
her overlay. The window in the corner is what she has pulled up for the bar she's on; her chat runs under
it; and the other one is on a call in the opposite corner, laughing along. For the last verse the two are
at the sanctuary's gate, leaning on the fence with the window between them, and the song ends over the
counter of the gift shop. The frame never moves: the cuts are from one place to the next.

render_frame(t) builds one 1920x1080 frame: a 320x180 world plus a 320x180 UI layer, shown at 6x. Per-line
gags (gags_*.py, see gagkit.py) hook into its phases:

    <setup>  poses, props, what the window shows: gags change `c` here (c.st[who], c.window...)
    "back"   each woman's webcam frame, behind her figure: c.cam[who], 320x180 (in a shared frame the two
             are one picture)
    "mid"    each webcam frame, in front of the figure and her desk (c.anchor[who] is known by now)
    "front"  the world: the frame as cut together, over the overlay's window and chat
    "ui"     UI layer, under the captions
    "top"    UI layer, over everything
"""
import math

from PIL import Image

import chatlog
import pictures
import rooms
import stream
import timeline as TL
from characters import FW, figure
from engine import C, SILK, H, W, blend, col, rgba, rnd
from pixelart.camera import Cam, compose, shake_offset
from pixelart.figure import pick
from pixelart.gags import Gags

FPS = TL.FPS
PHASES = ("back", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
WOMEN = TL.WOMEN
OTHER = TL.OTHER
STATE = ("arms", "lean", "bob", "eyes", "brows", "mouth", "flush")
REST_MOUTH = {"emiru": "smile", "maya": "smile"}
CAM = Cam(W / 2, H / 2, 6)


def default_state(who):
    return dict(hidden=False, dx=0, dy=0, arms="desk", lean=1, bob=0, eyes="open", brows="neutral",
                mouth=REST_MOUTH[who], flush=0, held=None, gesture=True, react=True, outfit=None, shake=0,
                facing=rooms.FACING[who])


# --- per-frame context -----------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        if self.ln and self.ln["sec"] != self.sec:         # a line doesn't follow the cut to the next place
            self.ln = None
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.view = TL.VIEW[self.sec]                      # whose stream is on screen, or the place they share
        self.st = {w: default_state(w) for w in WOMEN}
        self.vars = {}
        self.subs = True                                   # the captions
        self.overlay = True                                # the window, the chat and the call
        self.hitfx = True                                  # laughter on punchlines
        # The window on the host's stream: a picture (pic, with its title) for the bar she's on.
        self.window = dict(pic=None, title=None, badge=None, paused=False, progress=0.02, shake=0)
        self.chat = []                                     # extra chat lines from gags: (name, colour, text)
        self.cow = self.bird = True                        # Winnie and the hawk, where they usually are
        self.flash, self.flash_color = 0.0, C["white"]
        self.shake = 0.0
        self.world = self.ui = None
        self.cam, self.anchor = {}, {}

    @property
    def solo(self):
        return self.view in WOMEN

    @property
    def host(self):
        """Whose overlay is on screen: a woman's, or the pair's."""
        return self.view if self.solo else "pair"

    @property
    def guest(self):
        return OTHER[self.view] if self.solo else None

    def get(self, key, default=None):
        return self.vars.get(key, default)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color

    def at(self, who, name="head"):
        """A point on someone in her webcam frame (which, for whoever is on screen, is the world): an anchor
        of a figure drawn this frame (from the "mid" phase on)."""
        return self.anchor[who][name]

    def to_ui(self, x, y):
        return CAM.ui(x, y)


# --- mannerisms --------------------------------------------------------------------------------
# A rapper changes gesture every two beats. Neither folds her arms: Emiru's hands stay clear of her middle.

TALK = {"emiru": (("palm", 3), ("point", 2), ("finger", 2), ("shrug", 2), ("thumb", 1), ("chop", 1), ("fist", 1),
                  ("guns", 1), ("wave", 1)),
        "maya": (("palm", 3), ("point", 2), ("shrug", 2), ("finger", 2), ("chop", 2), ("chest", 1), ("thumb", 1),
                 ("fist", 1))}
LISTEN = {"emiru": ("desk", "chin", "desk", "thumb"), "maya": ("desk", "chin", "desk", "clasp")}


def rapping(c, who):
    return c.ln is not None and c.ln["who"] in (who, "both")


def singing(c, who):
    ln = c.ln
    if not rapping(c, who):
        return False
    return ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.45 and TL.loudness(c.t) > 0.1


def mouth_for(who, loud):
    if loud < 0.12:
        return REST_MOUTH[who]
    if loud < 0.4:
        return "open"
    if loud < 0.72:
        return "grin"
    return "wide"


def pose_rapper(c, who):
    s = c.st[who]
    if s["gesture"]:
        s["arms"] = pick(TALK[who], c.beat_i // 2, who, "gesture")
    s["bob"] = 2 if c.ph < 0.3 else 0
    s["lean"] = 2
    s["mouth"] = mouth_for(who, TL.loudness(c.t)) if singing(c, who) else REST_MOUTH[who]
    s["brows"] = "up" if s["arms"] in ("shrug", "palm", "thumb", "wave") else "neutral"
    s["eyes"] = "side" if s["arms"] in ("point", "guns") else "open"


def pose_listener(c, who):
    """Whoever doesn't have the bar: nodding along, enjoying it."""
    s = c.st[who]
    bar = c.beat_i // 4
    s["lean"] = 1
    s["bob"] = 1 if c.ph < 0.3 else 0
    if s["gesture"]:
        s["arms"] = LISTEN[who][(bar // 2 + (who == "maya")) % 4]
    s["mouth"] = "smile" if bar % 4 != 2 else "smirk"
    s["eyes"] = "side" if bar % 3 == 1 else "open"
    s["brows"] = "up" if bar % 4 == 3 else "neutral"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"emiru": (3.3, 0.9), "maya": (4.1, 2.3)}[who]
        if s["eyes"] in ("open", "half", "side") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """A punchline lands: whoever didn't say it laughs, and hardest at the big ones."""
    h = TL.last_hit(c.t, window=1.2)
    if not h:
        return
    age, big = c.t - h["t"], h["big"]
    for who in WOMEN:
        s = c.st[who]
        if not s["react"] or rapping(c, who) or h["who"] in (who, "both"):
            continue
        if age < (1.0 if big else 0.5):
            s["eyes"] = "shut" if big else "open"
            s["brows"] = "up"
            s["mouth"] = "wide" if big and age < 0.35 else "grin"
            s["bob"] = 2 if int(age * 8) % 2 == 0 else 0
            if big and s["gesture"]:
                s["arms"] = "acc0" if int(age * 6) % 2 == 0 else "acc1"      # a clap


# --- drawing a webcam frame ---------------------------------------------------------------------------

def start_cams(c):
    if c.solo:
        for who in WOMEN:
            img = rooms.BACK[who]().copy()
            rooms.alive(img, who, c.t, c.cow, c.bird)
            c.cam[who] = img
    else:                                                                # one frame, and both of them in it
        img = rooms.BACK[c.view]().copy()
        rooms.alive(img, c.view, c.t, c.cow, c.bird)
        c.cam = {who: img for who in WOMEN}


def draw_figure(c, who):
    s = c.st[who]
    img = c.cam[who]
    spr, a = figure(who, facing=s["facing"], held=s["held"], outfit=s["outfit"], **{k: s[k] for k in STATE})
    pad = (spr.width - FW) // 2                                           # figure() pads for a wide held prop
    fx, fy = (rooms.FIG if c.solo else rooms.PAIR)[who]
    x, y = fx + int(round(s["dx"])) - pad, fy + int(round(s["dy"])) - pad
    if s["shake"]:
        k = rnd("figshake", who, c.f) * 2 * math.pi
        x, y = x + int(round(math.cos(k) * s["shake"])), y + int(round(math.sin(k) * s["shake"]))
    c.anchor[who] = {k: (px + x, py + y) for k, (px, py) in a.items()}
    if not s["hidden"]:
        img.paste(spr, (x, y), spr)


def draw_fronts(c):
    for place in (WOMEN if c.solo else (c.view,)):
        front = rooms.FRONT[place]()
        c.cam[place if c.solo else "emiru"].paste(front, (0, 0), front)


# --- cutting the frame together -------------------------------------------------------------------------

def draw_view(c):
    """The world: the host's webcam under her overlay, or the frame the two share with the window between
    them."""
    host, guest = c.host, c.guest
    c.world.paste(c.cam[c.view if c.solo else "emiru"], (0, 0))
    if not c.overlay:
        return
    w = c.window
    pic, title, badge, accent = w["pic"], w["title"], w["badge"], stream.ACCENT[host]
    if c.get("guest_big") and guest:                                     # the caller has the bar: put her up
        pic, title, badge, accent = stream.preview_pic(c.cam[guest], guest), stream.NAME[guest], "CALL", stream.ACCENT[guest]
    elif pic is None:
        pic, title, badge = pictures.standby(c.view), pictures.STANDBY_TITLE[c.view], "LIVE"
    a = rnd("winshake", c.f) * 2 * math.pi
    off = (int(round(math.cos(a) * w["shake"])), int(round(math.sin(a) * w["shake"])))
    stream.draw_preview(c.world, host, pic, title, accent, w["paused"], w["progress"], off, badge)
    lines, age = chatlog.tail(host, c.t)
    if c.solo:
        stream.draw_tile(c.world, host, stream.tile_pic(c.cam[guest], guest), guest, singing(c, guest), c.t)
        stream.draw_chat(c.world, host, lines + c.chat, 9.0 if c.chat else age, chatlog.viewers(host, c.t))
    else:
        stream.draw_ticker(c.world, (c.chat or lines)[-1] if (c.chat or lines) else None, 9.0 if c.chat else age)


def draw_captions(c):
    ln = c.ln
    if not ln or not c.subs:
        return
    words = [w["w"] for w in ln["words"]]
    stream.draw_captions(c.ui, words, TL.word_index(ln, c.t), ln["who"], "emiru" if ln["who"] == "both" else ln["who"])


# --- the frame ------------------------------------------------------------------------------------------

def setup(c):
    for who in WOMEN:
        if rapping(c, who):
            pose_rapper(c, who)
        else:
            pose_listener(c, who)


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
    start_cams(c)
    runner.run("back")
    for who in WOMEN:
        draw_figure(c, who)
    draw_fronts(c)
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
