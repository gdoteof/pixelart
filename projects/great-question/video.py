"""Frame renderer for Great Question: PewDiePie vs. Sam Altman on a video call, moderated by ChatGPT.

Felix's webcam is the left tile and Sam's the right; ChatGPT's window sits between them and shares a
picture for every bar, eager to help. The call app carries the lyrics (the live captions under the
tiles), the speaker's border and the system messages. The frame never moves: there is one shot.

render_frame(t) builds one 1920x1080 frame: a 320x180 world plus a 320x180 UI layer, shown at 6x. Per-line
gags (gags_*.py, see gagkit.py) hook into its phases:

    <setup>  poses, props and the shared picture: gags change `c` here (c.st[who], c.screen, c.gpt...)
    "back"   each tile's own canvas, behind its figure: c.tile[who], in tile pixels
    "mid"    each tile's canvas, in front of the figure and the desk (c.anchor[who] is known by now)
    "front"  the world, over the tiles and ChatGPT's window
    "ui"     UI layer, under the captions
    "top"    UI layer, over everything
"""
import math
from functools import lru_cache

from PIL import Image, ImageDraw

import call
import timeline as TL
from characters import FW, figure
from engine import C, INK, SILK, H, W, Canvas, blend, col, rgba, rnd, silk, silk_w
from pixelart import pixel
from pixelart.camera import Cam, compose
from pixelart.gags import Gags

FPS = TL.FPS
PHASES = ("back", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
MEN = ("felix", "sam")
STATE = ("arms", "lean", "bob", "eyes", "brows", "mouth", "flush")
NAME = {"felix": "PEWDIEPIE", "sam": "SAM ALTMAN", "gpt": "CHATGPT", "ajax": "AJAX", "gpt2": "CHATGPT (2)"}
ROLE = {"felix": "YOUTUBER", "sam": "CEO, OPENAI", "gpt": "MODERATOR", "ajax": "FELIX'S OWN A.I.",
        "gpt2": "SAM'S OWN A.I."}                         # what Ajax turns out to be: a gag sets c.vars["voice"]
TAG = {"felix": C["felix"], "sam": C["sam_sh"], "gpt": C["gpt_sh"], "ajax": C["ajax_sh"], "gpt2": C["gpt_sh"]}
REST_MOUTH = {"felix": "smile", "sam": "closed"}
CAM = Cam(W / 2, H / 2, 6)
SOUND_COLOR = {"BZZT": "live", "CLAP": "gold"}


def default_state(who):
    s = dict(hidden=False, dx=0, dy=0, arms="desk", lean=1, bob=0, eyes="open", brows="neutral", mouth="closed",
             flush=0, held=None, gesture=True, react=True, sweat=False, tears=False, outfit=None, hat=None,
             name=NAME[who], muted=False, grey=0.0, shake=0, facing=call.FACING[who])
    s.update(arms="desk", mouth="smile") if who == "felix" else s.update(arms="clasp")
    return s


# --- per-frame context -----------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = TL.RAPPER.get(self.sec)
        self.speaker = self.rapper if self.sec in TL.RAPPER else self.ln["who"] if self.ln else None   # has the floor
        self.st = {w: default_state(w) for w in MEN}
        self.vars = {}
        self.subs = True                                   # the captions
        self.tag = True                                    # the speaker's name tab
        self.chrome = True                                 # the top bar and the controls
        self.hitfx = True                                  # flinches and reactions on punchlines
        self.screen = None                                 # what ChatGPT's window shares: see gagkit.show
        self.gpt = dict(kind="gpt", mood="happy", title="CHATGPT", caption=None, talk=None)
        self.title, self.people = "GREAT QUESTION", 3
        self.toasts = []                                   # system messages: (text, k, colour)
        self.rack_lit = False
        self.flash, self.flash_color = 0.0, C["white"]
        self.shake = 0.0
        self.world = self.ui = None
        self.cam = CAM
        self.tile, self.anchor = {}, {}

    def get(self, key, default=None):
        return self.vars.get(key, default)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color

    def at(self, who, name="head"):
        """A world point on someone: an anchor of a figure drawn this frame (from the "mid" phase on)."""
        x, y = self.anchor[who][name]
        return x + call.TILE[who][0], y + call.TILE[who][1]

    def to_ui(self, x, y):
        return self.cam.ui(x, y)


# --- mannerisms --------------------------------------------------------------------------------
# A rapper changes gesture every two beats. Felix performs for a camera: the open palm, the point, the
# shrug, the finger guns, a fist. Sam explains, quietly: the steeple, the open palm, a raised finger, the
# pinch. Listening, Felix leans back with his arms crossed; Sam clasps his hands and waits.

TALK = {"felix": (("palm", 3), ("point", 3), ("shrug", 2), ("guns", 2), ("finger", 1), ("fist", 1), ("chop", 1)),
        "sam": (("steeple", 4), ("finger", 3), ("pinch", 3), ("point", 2), ("chest", 2))}   # his hands stay off the button


def pick(who, slot):
    """The gesture for a two-beat slot: weighted, and never the same twice running."""
    opts = TALK[who]
    total = sum(w for _, w in opts)

    def draw(k):
        r = rnd(who, "gesture", k) * total
        for g, w in opts:
            r -= w
            if r < 0:
                return g
        return opts[-1][0]

    g = draw(slot)
    if g == draw(slot - 1):
        g = draw(slot + 1000)
    return g


def singing(c, who):
    ln = c.ln
    if ln is None or ln["who"] != who:
        return False
    end = ln["t1"] if who in ("gpt", "ajax") else TL.last_word(ln) + 0.45
    return ln["t0"] - 0.05 <= c.t <= end and TL.loudness(c.t) > 0.1


def mouth_for(who, loud):
    if loud < 0.12:
        return REST_MOUTH[who]
    if loud < 0.4:
        return "open"
    if loud < 0.72:
        return "grin" if who == "felix" else "open"
    return "wide"


def pose_rapper(c, who):
    s = c.st[who]
    ln = c.ln
    mine = ln is not None and ln["who"] == who
    if s["gesture"]:
        s["arms"] = pick(who, c.beat_i // 2)
        if mine and (ln["sec"], ln["idx"]) in TL.KILL_SHOTS:
            if TL.last_word(ln) - 0.15 <= c.t <= TL.last_word(ln) + 0.9:    # the punchline: point at him
                s["arms"] = "point"
    s["bob"] = 1 if c.ph < 0.3 else 0
    s["lean"] = 2
    s["mouth"] = mouth_for(who, TL.loudness(c.t)) if singing(c, who) else REST_MOUTH[who]
    if who == "felix":
        s["brows"] = "up" if s["arms"] in ("shrug", "palm", "guns") else "angry" if s["arms"] in ("point", "chop") else "neutral"
        s["eyes"] = "shut" if s["arms"] == "guns" and c.ph < 0.5 else "open"
    else:
        s["brows"] = "up" if s["arms"] in ("chest", "finger") else "neutral"
        s["eyes"] = "half" if s["arms"] in ("steeple", "pinch") and c.beat_i % 4 == 3 else "open"


def pose_listener(c, who):
    s = c.st[who]
    bar = c.beat_i // 4
    s["lean"] = 1
    hook = c.sec in TL.HOOKS or c.sec == "outro"
    if who == "felix":
        if s["gesture"]:
            s["arms"] = ("cross", "desk", "chin", "cross")[(bar // 2) % 4]
        s["mouth"] = "smile" if bar % 4 != 3 else "smirk"
        s["eyes"] = "side" if hook or bar % 5 == 2 else "open"
        s["brows"] = "up" if hook else "neutral"
    else:
        if s["gesture"]:
            s["arms"] = ("clasp", "clasp", "chin", "desk")[(bar // 2) % 4]
        s["mouth"] = "closed" if bar % 3 else "smile"
        s["eyes"] = "side" if hook or bar % 6 == 4 else "open"
        s["brows"] = "up" if hook and bar % 2 else "neutral"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"felix": (3.3, 0.7), "sam": (4.1, 2.2)}[who]       # Sam hardly blinks
        if s["eyes"] in ("open", "half", "side") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The target flinches as each line lands, and reels from the big ones."""
    for who in MEN:
        h = TL.last_hit(c.t, target=who, window=1.4)
        s = c.st[who]
        if not h or not s["react"]:
            continue
        age, big = c.t - h["t"], h["big"]
        if age < (1.1 if big else 0.4):
            s["eyes"] = "wide" if big else s["eyes"]
            s["brows"] = "worried"
            s["mouth"] = "o" if big and age < 0.5 else "frown"
            if big:
                s["flush"] = 1
                s["sweat"] = True
                if age < 0.6 and s["gesture"]:
                    s["arms"] = "facepalm" if who == "felix" else "desk"
        if age < 0.3:
            s["shake"] = max(s["shake"], 2 if big else 1)
            if big:
                c.add_shake(4 * (1 - age / 0.3))
        s["dx"] += int(round((2 if big else 1) * max(0.0, 1 - age / 0.35) * -s["facing"]))   # knocked back


# --- reactions: what a punchline leaves in the target's tile ----------------------------------------

@lru_cache(maxsize=None)
def react_icon(kind):
    f = Canvas(9, 9)
    if kind == "laugh":
        f.ell((0, 0, 8, 8), "yellow"); f.line([(2, 3), (3, 2)], "ink"); f.line([(5, 2), (6, 3)], "ink")
        f.poly([(2, 5), (6, 5), (4, 7)], "mouth"); f.pxs([(1, 4), (7, 4)], "tear")
    elif kind == "skull":
        f.ell((0, 0, 8, 6), "white"); f.rect((2, 5, 6, 8), "white")
        f.rect((2, 3, 3, 4), "ink"); f.rect((5, 3, 6, 4), "ink"); f.pxs([(3, 7), (5, 7)], "ink")
    elif kind == "fire":
        f.poly([(4, 0), (8, 5), (7, 8), (1, 8), (0, 5), (2, 3), (3, 5)], "orange")
        f.poly([(4, 4), (6, 7), (2, 7)], "yellow")
    elif kind == "fist":
        f.rect((1, 2, 7, 7), "fskin"); f.line([(1, 4), (7, 4)], "fskin_sh"); f.pxs([(2, 2), (4, 2), (6, 2)], "fskin_sh")
    elif kind == "100":
        f.silk((0, 2), "L", "live")
    return f.done()


REACT = {"felix": ("laugh", "skull", "fire", "laugh"), "sam": ("laugh", "fist", "fire", "skull")}


def draw_reactions(c, who):
    """Big punchlines send reactions up the inside edge of the target's tile for two seconds."""
    tile = c.tile[who]
    for h in TL.HITS:
        age = c.t - h["t"]
        if not h["big"] or h["target"] != who or not 0 <= age < 2.2:
            continue
        kinds = REACT[who]
        for j in range(6):
            a = age - j * 0.13
            if not 0 <= a < 1.5:
                continue
            x = 84 + int(rnd("rx", h["t"], j) * 6) + int(3 * math.sin(a * 5 + j))      # up the right-hand edge
            spr = react_icon(kinds[j % len(kinds)])
            tile.paste(spr, (x, int(100 - a * 62)), spr)


# --- drawing the tiles ------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def start_tile(c, who):
    tile = call.ROOM[who]().copy()
    if who == "felix":
        call.rack_lights(tile, c.t, c.rack_lit)
    else:
        call.ban_button(tile, c.get("ban"))
    c.tile[who] = tile


def draw_figure(c, who):
    s = c.st[who]
    tile = c.tile[who]
    spr, a = figure(who, facing=s["facing"], held=s["held"], outfit=s["outfit"], **{k: s[k] for k in STATE})
    pad = (spr.width - FW) // 2                                           # figure() pads for a wide held prop
    x, y = call.FIG[0] + int(round(s["dx"])) - pad, call.FIG[1] + int(round(s["dy"])) - pad
    anchors = {k: (px + x, py + y) for k, (px, py) in a.items()}
    c.anchor[who] = anchors
    if s["hidden"]:
        return
    tile.paste(spr, (x, y), spr)
    hx, hy = anchors["head"]
    if s["hat"]:                                                          # a sprite drawn facing right, 40 wide
        hat, dy = s["hat"]
        hat = hat if s["facing"] > 0 else hat.transpose(Image.FLIP_LEFT_RIGHT)
        tile.paste(hat, (hx - hat.width // 2, hy + dy), hat)
    if s["sweat"]:
        d = sweat_drop()
        tile.paste(d, (int(hx - s["facing"] * 18), int(hy + 6 + int(c.t * 6) % 3)), d)
    if s["tears"]:                                                        # down the near cheek
        ex, ey = anchors["eye"]
        dd = ImageDraw.Draw(tile)
        dd.line([(ex, ey + 3), (ex, ey + 8)], fill=C["tear"])
        dd.point((ex, ey + 9 + int(c.t * 10) % 2), fill=C["tear"])
    desk = call.DESK[who]()
    tile.paste(desk, (0, 0), desk)


def finish_tile(c, who):
    s = c.st[who]
    tile = c.tile[who]
    if c.hitfx:
        draw_reactions(c, who)
    speaking = c.speaker == who and not s["grey"]
    call.name_plate(tile, s["name"], call.ACCENT[who], TL.loudness(c.t) if singing(c, who) else 0.0, s["muted"])
    if s["grey"] > 0:
        tile = call.greyed(tile, min(1.0, s["grey"]))
    x0, y0 = call.TILE[who][:2]
    if s["shake"]:
        a = rnd("tshake", who, c.f) * 2 * math.pi
        moved = Image.new("RGB", tile.size, C["bg"])
        moved.paste(tile, (int(round(math.cos(a) * s["shake"])), int(round(math.sin(a) * s["shake"]))))
        tile = moved
    c.tile[who] = tile
    c.world.paste(tile, (x0, y0))
    call.frame_tile(c.world, who, speaking)


def talk_level(c):
    """How wide the assistant's mouth is right now (0-3), from the vocals, while it has a line."""
    if not (singing(c, "gpt") or singing(c, "ajax")):
        return 0
    loud = TL.loudness(c.t)
    return 0 if loud < 0.12 else 1 if loud < 0.4 else 2 if loud < 0.72 else 3


def draw_window(c):
    """ChatGPT's window: the assistant itself, listening or talking, and over it what a gag shares. A
    shared picture slides up into place (slide 0 -> 1) over whatever was there, and is swiped off to the
    left (out 0 -> 1)."""
    g = c.gpt
    kind = g["kind"]
    talking = c.speaker in ("gpt", "ajax")
    talk = g["talk"] if g["talk"] is not None else talk_level(c)
    view = call.idle_pic(g["mood"], talk, min(2, talk) if talk else 0, kind, 0 if talking else int(c.t * 2.5) % 4)
    caption = g["caption"] if g["caption"] is not None else ("" if talking else "LISTENING")
    s = c.screen
    if s:
        view = (s["under"] if s["under"] is not None and s["slide"] < 1 else view).convert("RGB").copy()
        dx, dy = -int(round(s["out"] * (call.PW + 2))), int(round((1 - s["slide"]) * call.PH))
        view.paste(s["pic"].convert("RGB"), (dx, dy))
        if s["slide"] > 0.5 and s["out"] < 0.5:
            caption = s["caption"] or ""
    call.draw_screen(c.world, view, g["title"], caption, talking, kind)


# --- the UI: the captions, and the speaker's tab -------------------------------------------------------

def show_word(w):
    return w.strip("*") if TL.is_sound(w) else w


def wrap(words, width):
    rows, row, x = [], [], 0
    space = silk_w(" ")
    for i, w in enumerate(words):
        ww = silk_w(w)
        if row and x + space + ww > width:
            rows.append(row)
            row, x = [], 0
        x += (space if row else 0) + ww
        row.append(i)
    return rows + [row] if row else rows


def draw_lower_third(c):
    ln = c.ln
    if not ln or not c.subs:
        return
    d = ImageDraw.Draw(c.ui)
    raw = [w["w"] for w in ln["words"]]
    words = [show_word(w) for w in raw]
    now = TL.word_index(ln, c.t)
    rows = wrap(words, W - 16)[:2]
    y0 = 148
    d.rectangle((0, y0, W, y0 + 18), fill=(12, 14, 24, 240))
    who = c.get("voice", ln.get("who"))
    d.line([(0, y0), (W, y0)], fill=TAG.get(who, C["line"]) + (255,))
    space = silk_w(" ")
    for r, row in enumerate(rows):
        x, y = 8, y0 + 3 + 8 * r + (4 if len(rows) == 1 else 0)
        for i in row:
            if TL.is_sound(raw[i]):                                      # a buzzer or a clap: only once it sounds
                if i <= now:
                    silk(c.ui, (x, y), words[i], SOUND_COLOR.get(words[i], "gold"))
            else:
                silk(c.ui, (x, y), words[i], "gold" if i == now else "text" if i < now else (150, 158, 188))
            x += silk_w(words[i]) + space
    if c.tag and who in NAME:
        name, role = NAME[who], ROLE[who]
        nw, rw = silk_w(name) + 8, silk_w(role) + 8
        d.rectangle((6, y0 - 10, 6 + nw, y0 - 1), fill=TAG[who] + (255,))
        silk(c.ui, (10, y0 - 8), name, "text")
        d.rectangle((6 + nw, y0 - 10, 6 + nw + rw, y0 - 1), fill=(232, 234, 242, 255))
        silk(c.ui, (10 + nw, y0 - 8), role, "ink")


def shake_offset(c):
    if c.shake < 0.5:
        return (0, 0)
    a = rnd("shake", c.f) * 2 * math.pi
    return (int(round(math.cos(a) * c.shake)), int(round(math.sin(a) * c.shake)))


# --- the frame ------------------------------------------------------------------------------------------

def setup(c):
    for who in MEN:
        if c.rapper == who or (c.ln is not None and c.ln["who"] == who and c.sec == "outro"):
            pose_rapper(c, who)
        else:
            pose_listener(c, who)


def build_frame(t, tweak=None):
    """Draw the frame at time t. Returns the context, with its world and ui ready to compose.
    `tweak(c)`, if given, runs after the gags' setup (thumbnails use it to turn the UI off)."""
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
        start_tile(c, who)
    runner.run("back")
    for who in MEN:
        draw_figure(c, who)
    runner.run("mid")
    for who in MEN:
        finish_tile(c, who)
    draw_window(c)
    runner.run("front")
    if c.flash > 0:
        blend(c.world, 1.0, c.flash_color, min(1.0, c.flash))
    runner.run("ui")
    if c.chrome:
        call.draw_topbar(c.ui, t, c.title, c.people)
        call.draw_controls(c.ui)
    for text, k, color in c.toasts:
        call.toast(c.ui, text, k, color)
    draw_lower_third(c)
    runner.run("top")
    return c


def render_frame(t):
    c = build_frame(t)
    return compose(c.world, c.ui, c.cam, shake_offset(c))


def label(t):
    ln = TL.line_at(t)
    return f"{ln['sec']}.{ln['idx']} {ln['text']}" if ln else TL.section_at(t)[0]


__all__ = ["FPS", "render_frame", "label", "build_frame", "GAGS", "Ctx", "col", "rgba", "SILK"]
