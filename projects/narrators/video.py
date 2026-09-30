"""Frame renderer for Attenborough vs. Freeman.

Whoever raps holds the camera. Sir David's sections are his nature documentary
("doc"): Morgan is the specimen, observed in a vocal booth that someone has
left in the jungle, and the screen is a field camera's viewfinder with lower
thirds and teletext subtitles. Morgan's sections are his films ("film"): Sir
David is cast as the doomed lead, under letterbox bars and a warm grade, with
the subtitles in the bar. The switches between the two are hijacks
(gags_links.py).

render_frame(t) builds one 1920x1080 frame: a 320x180 world seen through an
integer-zoom camera (pixelart.camera), plus a 320x180 UI layer shown at 6x.
The per-line gags (gags*.py, see pixelart.gags) hook into its phases:

    <setup>   scene, shot, poses and flags: gags change `c` here
    "back"    world, over the set but behind the characters
    "mid"     world, over the set's mid layer (glass, mist), behind the foreground cast (z=1)
    "front"   world, in front of the characters and the set's own front layers
    "ui"      UI layer, under the subtitles and the screen furniture
    "top"     UI layer, over everything
"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import chrome as CH
import timeline as TL
from characters import figure, mouth_for
from engine import C, INK, SILK, H, W, blend, dither, mask, rnd, scaled, tint
from pixelart import pixel
from pixelart.camera import Cam, compose
from pixelart.gags import Gags
from sets import SETS

FPS = TL.FPS
PHASES = ("back", "mid", "front", "ui", "top")
GAGS = Gags(PHASES)
CAST = ("david", "morgan")
POSE = ("body", "mouth", "eyes", "brows", "arm", "mic", "hat", "outfit", "glasses", "flush", "lean", "bob")
# placement and costume come from the set (and reset when the scene changes); the pose keys don't
PLACE = dict(x=160, y=150, facing=1, hidden=True, body="stand", hat="none", outfit=None, glasses=False, mic=False,
             dx=0, dy=0, rot=0.0, shadow=True, tint=None, z=0, gesture=True, rim=0.0, rim_color=(255, 214, 160))
HOME = {"intro": "habitat", "v1": "habitat", "v3": "habitat", "v2": "yard", "v4": "car", "credits": "black",
        "outro": "heaven", "end": "heaven"}


def default_state():
    return dict(PLACE, mouth="closed", eyes="open", brows="neutral", arm="down", flush=0, lean=0, bob=0,
                sweat=False, dizzy=False)


# --- per-frame context ---------------------------------------------------------------------

class Ctx:
    def __init__(self, t):
        self.t = t
        self.f = int(round(t * FPS))
        self.sec, self.sa, self.sb = TL.section_at(t)
        self.mode = TL.MODE[self.sec]
        self.ln = TL.line_at(t)
        self.beat_i, self.ph, self.per = TL.beat_info(t)
        self.rapper = TL.RAPPER.get(self.sec)
        self.st = {w: default_state() for w in CAST}
        self.vars = {}
        film = self.mode == "film"
        self.subs = True
        self.hud = True                  # doc: the viewfinder
        self.rec = True
        self.bars = 1.0 if film else 0.0
        self.grade = 1.0 if film else 0.0
        self.grain = 1.0 if film else 0.0
        self.weave = 1.0 if film else 0.0
        self.handheld = 0.0 if film else 1.0
        self.hitfx = True
        self.hit_react = {"david": True, "morgan": True}
        self.inset = True
        self.mood = 0.0
        self.flash, self.flash_color = 0.0, C["white"]
        self.shake = 0.0
        self.shot = "wide"
        self.cam = self.world = self.ui = None
        self.anchor = {}
        self.scene = None
        self.set_scene(HOME[self.sec])

    def get(self, key, default=None):
        return self.vars.get(key, default)

    def set_scene(self, name, **knobs):
        """Cut to a set: everyone is placed (or hidden) as that set casts them."""
        self.scene = name
        for who in CAST:
            s = self.st[who]
            s.update(PLACE)
            cast = SETS[name].cast.get(who)
            if cast is not None:
                s.update(cast)
                s["hidden"] = cast.get("hidden", False)
        self.vars.update(knobs)

    def to_ui(self, x, y):
        return self.cam.ui(x, y)

    def add_shake(self, amount):
        self.shake = max(self.shake, amount)

    def add_flash(self, amount, color=C["white"]):
        if amount > self.flash:
            self.flash, self.flash_color = amount, color


# --- posing ----------------------------------------------------------------------------------

GESTURES = {"david": ["palm", "point", "chop", "palm", "point", "down", "chop", "palm"],
            "morgan": ["palm", "point", "down", "palm", "chop", "point", "down", "fist"]}


def singing(c, who):
    ln = c.ln
    return ln is not None and ln["who"] == who and ln["t0"] - 0.05 <= c.t <= TL.last_word(ln) + 0.45


def pose_rapper(c, who):
    s = c.st[who]
    if s["gesture"]:
        s["arm"] = GESTURES[who][int(rnd(who, c.beat_i // 2) * 8)]
    s["bob"] = 1 if c.ph < 0.3 else 0
    if singing(c, who):
        s["mouth"] = mouth_for(TL.loudness(c.t))
    s["brows"] = "angry" if s["mouth"] == "wide" else "up" if who == "david" else "neutral"


def pose_listener(c, who):
    s = c.st[who]
    if s["gesture"]:
        s["arm"] = "cross"
    s["mouth"] = "smirk" if who == "morgan" else "closed"
    s["eyes"] = "half" if who == "morgan" and (c.beat_i // 4) % 3 == 0 else "open"


def blink_eyes(c):
    for who, s in c.st.items():
        period, off = {"david": (3.1, 0.7), "morgan": (3.7, 1.9)}[who]
        if s["eyes"] in ("open", "half") and (c.t + off) % period < 0.1:
            s["eyes"] = "blink"


def apply_hits(c):
    """The target flinches as each line lands, and reels from the big ones."""
    for who in CAST:
        h = TL.last_hit(c.t, target=who, window=1.2)
        if not h or not c.hit_react[who]:
            continue
        age = c.t - h["t"]
        s = c.st[who]
        big = h["big"]
        if age < (0.9 if big else 0.35):
            s["eyes"] = "wide" if big else s["eyes"]
            s["brows"] = "worried"
            s["mouth"] = "wide" if big and age < 0.3 else "o" if big else s["mouth"]
            if big and age < 0.5 and s["gesture"]:
                s["arm"] = "palm"
        if big:
            s["sweat"] = True
        kb = (3 if big else 1) * max(0.0, 1 - age / 0.4)
        s["dx"] += int(round(kb * -s["facing"]))


def hit_shake(c):
    for h in TL.HITS:
        age = c.t - h["t"]
        if 0 <= age < 0.35 and h["big"]:
            c.add_shake((8 if c.mode == "doc" else 6) * (1 - age / 0.35))


def verse_setup(c):
    r = c.rapper
    for who in CAST:
        if who == r:
            pose_rapper(c, who)
        else:
            pose_listener(c, who)
    c.shot = default_shot(c)


def default_shot(c):
    cycle = SETS[c.scene].cycle
    ln = c.ln
    if not cycle:
        return "wide"
    if ln is None or ln["sec"] != c.sec:
        return cycle[0]
    return cycle[ln["idx"] % len(cycle)]


# --- drawing characters -----------------------------------------------------------------------

@lru_cache(maxsize=1)
def sweat_drop():
    return pixel.sprite([".k.", "kbk", "kbk", ".k."], {"k": INK, "b": C["sweat"]})


def shadow_under(img, x, y, w=9):
    dither(img, mask(lambda d: d.ellipse((x - w, y - 1, x + w, y + 2), fill=255)) * 0.6, (0, 0, 0), blend=0.3)


def sprite_of(c, who):
    """(sprite, anchors) for a character as posed this frame."""
    s = c.st[who]
    pose = {k: s[k] for k in POSE}
    spr, a = figure(who, s["facing"], rim=s["rim"], rim_color=s["rim_color"], **pose)
    if s["tint"]:
        spr = tint(spr, *s["tint"])
    return spr, a


def draw_char(c, img, who):
    s = c.st[who]
    if s["hidden"]:
        return None
    spr, a = sprite_of(c, who)
    x, y = int(round(s["x"] + s["dx"])), int(round(s["y"] + s["dy"]))
    ox, oy = x - a["feet"][0], y - a["feet"][1]
    if s["shadow"] and not s["rot"]:
        shadow_under(img, x, y + 1)
    if s["rot"]:
        m = 30
        layer = Image.new("RGBA", (spr.width + 2 * m, spr.height + 2 * m), (0, 0, 0, 0))
        layer.paste(spr, (m, m), spr)
        layer = layer.rotate(s["rot"], resample=Image.NEAREST, center=(m + a["feet"][0], m + a["feet"][1]))
        img.paste(layer, (ox - m, oy - m), layer)
    else:
        img.paste(spr, (ox, oy), spr)
    anchors = {k: (px + ox, py + oy) for k, (px, py) in a.items()}
    if s["sweat"] and not s["rot"]:
        hx, hy = anchors["head"]
        d = sweat_drop()
        img.paste(d, (int(hx - s["facing"] * 8) - 1, int(hy - 6 + int(c.t * 6) % 3)), d)
    if s["dizzy"]:
        hx, hy = anchors["head"]
        dd = ImageDraw.Draw(img)
        for k in range(3):
            ang = c.t * 7 + k * 2 * math.pi / 3
            dd.point((int(hx + 10 * math.cos(ang)), int(hy - 12 + 3 * math.sin(ang))), fill=C["gold"])
    c.anchor[who] = anchors
    return anchors


def draw_cast(c, layer):
    for who in sorted(CAST, key=lambda w: c.st[w]["y"]):
        if c.st[who]["z"] == layer:
            draw_char(c, c.world, who)


# --- reactions ---------------------------------------------------------------------------------
# A big punchline cuts in a reaction shot of its target, wherever the gag has taken the picture:
# a hidden camera's night-vision inset in the documentary, an iris in the film.

def close_enough(c, who):
    s = c.st[who]
    if s["hidden"] or c.cam.k < 12 or who not in c.anchor:
        return False
    hx, hy = c.anchor[who]["head"]
    return c.cam.visible((hx - 4, hy - 4, hx + 4, hy + 4))


def reaction_shot(c, who, w=58, h=46):
    """The target's head and shoulders at 2x, on a plain backdrop."""
    s = c.st[who]
    spr, a = sprite_of(c, who)
    hx, hy = a["head"]
    cw, ch = w // 2, h // 2
    crop = spr.crop((int(hx - cw / 2), int(hy - ch / 2 - 1), int(hx + cw / 2), int(hy + ch / 2 - 1)))
    bg = Image.new("RGBA", crop.size, (58, 58, 70, 255) if c.mode == "doc" else (70, 50, 44, 255))
    bg.alpha_composite(crop)
    if s["sweat"]:
        bg.alpha_composite(sweat_drop(), (int(cw / 2 - s["facing"] * 8), 3 + int(c.t * 6) % 3))
    return scaled(bg, 2)


def next_cut(t):
    """When the picture can next change: the gag switch 0.12 s before the next line starts."""
    return next((ln["t0"] - 0.12 for ln in TL.LINES if ln["t0"] - 0.12 > t), TL.DURATION)


def reaction_inset(c):
    """The target's reaction to a big hit, in a corner, until the next line's gag takes the picture
    (and not at all if that leaves too little time to register)."""
    h = TL.last_hit(c.t, window=0.9)
    if not h or not h["big"] or not c.inset:
        return
    cut = next_cut(h["t"])
    if c.t >= cut or cut - h["t"] < 0.3:
        return
    who = h["target"]
    if not c.hit_react[who] or close_enough(c, who):
        return
    age = c.t - h["t"]
    img = reaction_shot(c, who)
    ui = c.ui
    d = ImageDraw.Draw(ui)
    if c.mode == "doc":
        a = np.asarray(img.convert("RGB"), dtype=np.float32)
        a = a * 0.8 + np.array((20, 60, 30), np.float32) * 0.2          # a security camera's green cast
        a[::2] *= 0.82                                                    # scanlines
        nv = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        x0, y0 = W - 12 - nv.width, 34
        d.rectangle((x0 - 2, y0 - 2, x0 + nv.width + 1, y0 + nv.height + 1), fill=(10, 10, 14, 255))
        ui.paste(nv, (x0, y0))
        pixel.text(ui, (x0 + 2, y0 + 1), "CAM 2", SILK, (200, 255, 190), shadow=(0, 40, 0))
        if int(c.t * 4) % 2 == 0:
            d.ellipse((x0 + nv.width - 7, y0 + 3, x0 + nv.width - 4, y0 + 6), fill=C["rec"] + (255,))
        if age < 0.08:
            d.rectangle((x0 - 2, y0 - 2, x0 + nv.width + 1, y0 + nv.height + 1), outline=(255, 255, 255, 255))
    else:
        r = 26 if age > 0.06 else 18
        cx, cy = W - 46, CH.BAR + 34
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).ellipse((img.width // 2 - r, img.height // 2 - r, img.width // 2 + r, img.height // 2 + r),
                                  fill=255)
        d.ellipse((cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), fill=(12, 8, 8, 255))
        ui.paste(img, (cx - img.width // 2, cy - img.height // 2), m)
        d.ellipse((cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2), outline=C["gold_sh"] + (255,))


# --- world effects -----------------------------------------------------------------------------

def mood_overlay(img, amount):
    """Darken and cool the whole world by `amount` (0-1) for the sober lines."""
    if amount <= 0:
        return
    a = np.asarray(img, dtype=np.float32)
    k = 0.55 * min(1.0, amount)
    a = a * (1 - k) + np.array((22, 18, 44), np.float32) * k
    lum = a.mean(axis=2, keepdims=True)
    a = a * (1 - 0.35 * k) + lum * 0.35 * k
    img.paste(Image.fromarray(a.round().astype(np.uint8)))


def resolve_shot(c):
    shot = c.shot
    if isinstance(shot, Cam):
        return shot
    if isinstance(shot, str):
        shot = SETS[c.scene].shots.get(shot) or SETS["habitat"].shots["wide"]
    return Cam(*shot)


def camera_offset(c):
    """Shake from the hits, a handheld drift in the documentary, gate weave in the film (screen pixels)."""
    dx = dy = 0
    if c.shake >= 0.5:
        a = rnd("shake", c.f) * 2 * math.pi
        dx, dy = int(round(math.cos(a) * c.shake)), int(round(math.sin(a) * c.shake))
    cam, t = c.cam, c.t
    hx = hy = 0
    if c.handheld and cam.k > 6:
        amp = c.handheld * cam.k / 6
        hx = (math.sin(t * 0.83) * 1.6 + math.sin(t * 2.1 + 1) * 0.5) * amp
        hy = (math.sin(t * 1.17 + 2) * 1.2 + math.sin(t * 2.7) * 0.4) * amp
    if c.weave:
        wx, wy = CH.gate_weave(t, c.weave)
        hx, hy = hx + wx, hy + wy
    if cam.k > 6:                   # keep the drift inside the world
        k = cam.k
        sx, sy = round(cam.x0 * k), round(cam.y0 * k)
        hx = min(max(hx, -sx), round((W - cam.vw) * k) - sx)
        hy = min(max(hy, -sy), round((H - cam.vh) * k) - sy)
    return dx + int(round(hx)), dy + int(round(hy))


def draw_chrome(c):
    ui, ln = c.ui, c.ln
    if c.mode == "doc":
        if c.hud:
            CH.viewfinder(ui, c.t, rec=c.rec)
        if c.subs and ln:
            CH.teletext_subs(ui, ln, TL.word_index(ln, c.t))
    else:
        if c.bars > 0:
            CH.letterbox(ui, c.bars)
        if c.subs and ln:
            if c.bars >= 0.99:
                CH.film_subs(ui, ln, TL.word_index(ln, c.t))
            else:
                CH.teletext_subs(ui, ln, TL.word_index(ln, c.t))


def build_frame(t, tweak=None):
    """Draw the frame at time t. Returns the context, with its world, ui and cam ready to compose.
    `tweak(c)`, if given, runs after the gags' setup (thumbnails use it to turn the subtitles off)."""
    import gags  # noqa: F401  (registers the per-line gags into GAGS)
    c = Ctx(t)
    verse_setup(c)
    runner = GAGS.runner(c, t, TL.LINES, TL.section_end)
    if tweak:
        tweak(c)
    blink_eyes(c)
    apply_hits(c)
    if c.hitfx:
        hit_shake(c)
    c.cam = resolve_shot(c)
    st = SETS[c.scene]
    world = st.back(c)
    c.world = world
    c.ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    runner.run("back")
    draw_cast(c, 0)
    if st.mid:
        st.mid(c)
    runner.run("mid")
    draw_cast(c, 1)
    if st.near:
        st.near(c)
    runner.run("front")
    mood_overlay(world, c.mood)
    if c.flash > 0:
        blend(world, 1.0, c.flash_color, min(1.0, c.flash))
    if c.grade:
        CH.film_grade(world, t, warm=c.grade, grain=c.grain, vignette=c.grade)
    runner.run("ui")
    reaction_inset(c)
    draw_chrome(c)
    runner.run("top")
    return c


def render_frame(t):
    c = build_frame(t)
    return compose(c.world, c.ui, c.cam, camera_offset(c))


def label(t):
    ln = TL.line_at(t)
    return f"{ln['sec']}.{ln['idx']} {ln['text']}" if ln else TL.section_at(t)[0]
