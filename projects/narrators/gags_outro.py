"""The outro, after the credits: God (Morgan) in heaven with the planet he won.

"And that was the day David Attenborough learned" - God on his throne, the trophy on his knee.
"that nature is beautiful. Nature is cruel." - an insert: the planet in God's hand with Sir
David standing on top of it; birds for "beautiful", then God shakes it for "cruel".
"I would know. I made it." - God to camera, with his maker's mark on the planet.
Then the last word goes to the man with the camera: REC blinks on, the film's letterbox
falls away, and Sir David is crouched on a cloud narrating God, until God notices.
"""
import re

from critters import bird
from characters import figure
from gagkit import (C, CH, INK, PRESS, TL, H, W, Canvas, Image, ImageDraw, anchor, blend, char_at,
                    ease_in, ease_out, gag, lerp, lru_cache, math, mirror, pan, pixel,
                    place, ramp, rnd, scene, span, ui_at, wt)
from props import globe, sparkle, trophy
from sets import HEAVEN, HEAVEN_FLOOR, cloud, heaven

T_OUTRO = TL.section_bounds("outro")[0]
T_END = TL.section_bounds("end")[0]
L0, L1, L2 = TL.lines_of("outro")
THRONE = (160, HEAVEN_FLOOR + 10)         # the foot of the throne; God sits on it facing left
FADE_IN = (T_OUTRO + 0.2, T_OUTRO + 1.6)
INSERT = (TL.last_word(L0) + 0.9, L2["t0"] - 0.12)     # the planet in God's hand
REC_ON = T_END + 0.7                      # the documentary takes the last word
ZAP = T_END + 4.4                          # ...until God notices the camera
CARD = ZAP + 0.9
CARD_LATE = CARD + 2.2


# --- the throne ------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def throne():
    s = Canvas(46, 62)
    s.rect((6, 2, 39, 44), "gold")                        # the tall back
    s.rect((9, 5, 36, 42), "red")
    s.rect((11, 7, 34, 40), "red_hi")
    s.line([(11, 40), (34, 40)], "red_sh")
    for x in (6, 39):
        s.ell((x - 3, 0, x + 3, 6), "gold_hi")            # finials
    s.poly([(17, 2), (23, -2), (29, 2)], "gold")
    s.rect((2, 38, 44, 44), "gold")                       # the seat and its arms
    s.rect((4, 36, 11, 40), "gold_sh"); s.rect((35, 36, 42, 40), "gold_sh")
    s.rect((4, 44, 8, 60), "gold_sh"); s.rect((38, 44, 42, 60), "gold_sh")
    s.rect((8, 44, 38, 48), "gold")
    s.line([(2, 38), (44, 38)], "gold_hi")
    s.px((23, 22), "gold_hi")
    return s.done()


def seat_god(c):
    """God on his throne, the planet on his knee."""
    m = c.st["morgan"]
    m.update(body="sit", arm="hold", gesture=False, facing=-1, x=THRONE[0] - 2, y=THRONE[1] - 10, shadow=False)


# --- the insert: the planet in God's hand --------------------------------------------------------------

BIG_R = 40
PLANET_C = (164, 114)          # the big globe's centre in the insert


@lru_cache(maxsize=16)
def big_planet(phase):
    return globe(BIG_R, phase)


def _limb(d, a, b, w, color):
    """A thick round-ended stroke with an ink edge."""
    d.line([a, b], fill=INK, width=w + 2)
    for p in (a, b):
        d.ellipse((p[0] - (w + 2) / 2, p[1] - (w + 2) / 2, p[0] + (w + 2) / 2, p[1] + (w + 2) / 2), fill=INK)
    d.line([a, b], fill=color, width=w)
    for p in (a, b):
        d.ellipse((p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=color)


def gods_palm(img, cx, cy, r):
    """God's forearm coming in from the right, in the white suit, and the palm under the planet."""
    d = ImageDraw.Draw(img)
    fore = [(cx + r * 0.55, cy + r * 0.62), (W + 20, cy + r * 0.1), (W + 20, cy + r * 1.02), (cx + r * 0.75, cy + r * 1.08)]
    d.polygon(fore, fill=(196, 194, 206))
    d.polygon([(cx + r * 1.3, cy + r * 0.5), (W + 20, cy + r * 0.16), (W + 20, cy + r * 0.5),
               (cx + r * 1.3, cy + r * 0.74)], fill=C["wsuit"])                                  # the lit top
    d.polygon(fore, outline=INK)
    for k in range(3):                                                                         # creases
        x = cx + r * (1.6 + 0.5 * k)
        d.line([(x, cy + r * 0.62), (x + 6, cy + r * 0.9)], fill=(170, 168, 180))
    cuff = [(cx + r * 0.95, cy + r * 0.5), (cx + r * 1.2, cy + r * 0.46), (cx + r * 1.28, cy + r * 1.02),
            (cx + r * 1.03, cy + r * 1.06)]
    d.polygon(cuff, fill=C["white"], outline=INK)
    d.ellipse((cx - r * 0.35, cy + r * 0.55, cx + r * 1.05, cy + r * 1.12), fill=INK)          # the palm
    d.ellipse((cx - r * 0.35 + 1, cy + r * 0.55 + 1, cx + r * 1.05 - 1, cy + r * 1.12 - 1), fill=C["mskin"])


def gods_fingers(img, cx, cy, r):
    """Four fingers curled round the bottom of the planet and a thumb up its side (drawn over it)."""
    d = ImageDraw.Draw(img)
    skin, skin_sh = C["mskin"], C["mskin_sh"]
    for k in range(4):                                  # knuckles along the palm, tips up the planet's face
        base = (cx - r * 0.2 + k * r * 0.24, cy + r * 0.98)
        tip = (cx - r * 0.62 + k * r * 0.2, cy + r * (0.52 + 0.05 * k))
        _limb(d, base, tip, 7, skin)
        d.line([(tip[0] - 2, tip[1] + 5), (tip[0] + 2, tip[1] + 5)], fill=skin_sh)
    _limb(d, (cx + r * 0.78, cy + r * 0.72), (cx + r * 0.92, cy + r * 0.2), 8, skin)       # thumb


def insert_world(c):
    img = heaven(c)
    blend(img, 1.0, (255, 246, 226), 0.35)            # soft focus: heaven far behind
    return img


scene("o_insert", shots={"planet": (160, 90, 6)})(insert_world)


def wt_line(ln, pat):
    return next(w["t0"] for w in ln["words"] if re.search(pat, w["w"], re.I))


def shake_of(c):
    """God shaking the planet for "cruel": a hard side to side, settling."""
    cruel = wt_line(L1, "cruel")
    age = c.t - cruel + 0.12
    if not 0 <= age < 1.3:
        return 0, 0.0
    amp = 7 * (1 - age / 1.3)
    return int(round(math.sin(age * 38) * amp)), age


# --- the scene ------------------------------------------------------------------------------------

@span(T_OUTRO, L0["t0"] - 0.15)
def heaven_opens(c, L):
    """The post-credits scene fades up on heaven."""
    seat_god(c)
    c.shot = (160, 96, 6)
    c.inset = False
    yield "back"
    th = throne()
    c.world.paste(th, (THRONE[0] - th.width // 2, THRONE[1] - th.height + 4), th)
    yield "front"
    god_trophy(c)
    blend(c.world, 1.0, (0, 0, 0), 1 - ease_out(ramp(c.t, *FADE_IN)))


CUP = (124, HEAVEN_FLOOR + 6)       # the empty trophy, beside the throne


def god_trophy(c):
    """The planet in God's hand, and the cup it came out of standing by the throne."""
    tr = trophy(0, planet=False)
    c.world.paste(tr, (CUP[0] - tr.width // 2, CUP[1] - tr.height), tr)
    hx, hy = anchor(c, "morgan", "hand")
    g = globe(6, int(c.t * 3) % 16)
    c.world.paste(g, (int(hx - g.width // 2 - 1), int(hy - g.height + 2)), g)


def planet_in_hand(c):
    """Where the planet sits in God's hand (world pixels)."""
    hx, hy = anchor(c, "morgan", "hand")
    return hx - 1, hy - 5


@gag("outro", 0)
def the_day_he_learned(c, L):
    seat_god(c)
    pan(c, (160, 96, 6), (156, 110, 12), L.t0, TL.last_word(L.ln) - L.t0 + 0.6)
    if c.t >= INSERT[0]:
        c.set_scene("o_insert")
        c.shot = "planet"
    yield "back"
    if c.scene == "heaven":
        th = throne()
        c.world.paste(th, (THRONE[0] - th.width // 2, THRONE[1] - th.height + 4), th)
    else:
        planet_insert(c)
    yield "front"
    if c.scene == "heaven":
        god_trophy(c)


def planet_insert(c):
    """The planet held up in God's hand, with Sir David standing on top of it."""
    dx, age = shake_of(c)
    cx, cy = PLANET_C[0] + dx, PLANET_C[1]
    gods_palm(c.world, cx, cy, BIG_R)
    g = big_planet(int(c.t * 1.5) % 16)
    c.world.paste(g, (cx - g.width // 2, cy - g.height // 2), g)
    gods_fingers(c.world, cx, cy, BIG_R)
    cruel = wt_line(L1, "cruel")
    if c.t < cruel - 0.12:                             # standing on the top of the world, presenting
        lovely = c.t > wt_line(L1, "beautiful")
        pose = dict(arm="palm" if lovely else "whisper", mouth="smile" if lovely else "closed")
        char_at(c.world, "david", cx - 2, cy - BIG_R - 1, facing=1, mic="fluffy", **pose)
    else:                                              # ...shaken off, and hanging on to the rim by his fingers
        spr, a = figure("david", -1, arm="up", mouth="wide", eyes="wide", brows="worried")
        swing = math.sin((c.t - cruel) * 7) * 14 * max(0.2, 1 - (c.t - cruel) / 2.5)
        hx, hy = a["hand"]
        layer = Image.new("RGBA", (spr.width + 40, spr.height + 40), (0, 0, 0, 0))
        layer.paste(spr, (20, 20), spr)
        layer = layer.rotate(swing, resample=Image.NEAREST, center=(20 + hx, 20 + hy))
        gx, gy = cx + int(BIG_R * 0.93), cy - int(BIG_R * 0.36)          # where his hands grip the planet
        c.world.paste(layer, (int(gx - 20 - hx), int(gy - 20 - hy)), layer)


@gag("outro", 1)
def beautiful_and_cruel(c, L):
    c.set_scene("o_insert")
    seat_god(c)
    c.st["morgan"]["hidden"] = True
    beautiful = wt(L, "beautiful")
    cruel = wt(L, "cruel")
    c.shot = "planet"
    dx, age = shake_of(c)
    if 0 < age < 0.5:
        c.add_shake(8 * (1 - age / 0.5))
    yield "back"
    planet_insert(c)
    yield "front"
    cx, cy = PLANET_C
    if beautiful <= c.t < cruel - 0.1:                 # "beautiful": birds circle, flowers pop, it sparkles
        age_b = c.t - beautiful
        for k in range(4):
            a = age_b * 1.6 + k * math.pi / 2
            bx = cx + math.cos(a) * (BIG_R + 16)
            by = cy - 10 + math.sin(a) * (BIG_R * 0.55)
            spr = bird(int(c.t * 8 + k) % 2, color=[(236, 80, 60), (70, 150, 230), (250, 200, 60), (160, 90, 220)][k])
            spr = spr if math.sin(a) > 0 else mirror(spr)
            c.world.paste(spr, (int(bx), int(by)), spr)
        for k in range(6):
            if (c.t * 3 + k) % 2 < 1.3:
                sparkle(c.world, int(cx - BIG_R + rnd("sp", k) * BIG_R * 2), int(cy - BIG_R * 0.6 + rnd("sq", k) * BIG_R),
                        1 + k % 2, (255, 255, 240))
    if c.t >= cruel - 0.12:                            # "cruel": snow flurry off the shaken globe
        a = c.t - cruel + 0.12
        for k in range(40):
            x = cx - BIG_R * 1.2 + rnd("sn", k) * BIG_R * 2.4 + dx * 0.5 + math.sin(a * 3 + k) * 4
            y = cy - BIG_R + (rnd("sn-y", k) * BIG_R * 2 + a * 30) % (BIG_R * 2.2)
            ImageDraw.Draw(c.world).point((int(x), int(y)), fill=(255, 255, 255))


@gag("outro", 2)
def i_made_it(c, L):
    seat_god(c)
    made = wt(L, "made")
    m = c.st["morgan"]
    c.shot = (152, 112, 18)
    if c.t >= wt(L, "would"):
        m["eyes"] = "side"
    if c.t >= made + 0.35:
        m["mouth"] = "smirk"
        m["eyes"] = "half"
        m["brows"] = "up"
    yield "back"
    th = throne()
    c.world.paste(th, (THRONE[0] - th.width // 2, THRONE[1] - th.height + 4), th)
    yield "front"
    god_trophy(c)
    if c.t >= made + 0.3 and int(c.t * 6) % 3 != 0:    # a twinkle in the Almighty's eye
        ex, ey = anchor(c, "morgan", "eye")
        sparkle(c.world, int(ex) - 3, int(ey) - 2, 2, (255, 255, 255))
    yield "ui"
    if c.t >= made:
        ux, uy = ui_at(c, *planet_in_hand(c))
        CH.callout(c.ui, c.t - made, "MADE IN HEAVEN", ux, uy, ux - 46, uy - 34, color=C["gold_hi"])


# --- the last word: the documentary was rolling all along ---------------------------------------------

@span(T_END, TL.DURATION + 1)
def last_word(c, L):
    seat_god(c)
    m = c.st["morgan"]
    doc = REC_ON <= c.t < ZAP + 0.35
    if c.t < REC_ON:
        c.shot = (152, 112, 18) if c.t < T_END + 0.3 else (160, 100, 6)
        m.update(mouth="smirk", eyes="half", brows="up")
    else:
        c.shot = (160, 100, 6)
        place(c, "david", x=62, y=164, facing=1, body="crouch", arm="whisper", mic="fluffy", z=1, shadow=False)
        c.st["david"].update(mouth="o" if int(c.t * 5) % 2 else "closed", brows="up", eyes="side")
        m.update(mouth="closed", eyes="open")
        if c.t >= ZAP - 1.4:                            # God notices the camera; the camera zooms in on him
            m.update(facing=-1, eyes="side", brows="angry", mouth="frown", arm="point")
            pan(c, (160, 100, 6), (150, 118, 12), ZAP - 1.4, 0.5)
    if doc:                                             # the documentary's chrome takes the frame back
        c.mode = "doc"
        c.bars = 1 - ease_in(ramp(c.t, REC_ON, REC_ON + 0.25))
        c.grade = c.grain = c.weave = 0.0
        c.handheld = 1.0
    c.inset = False
    if c.t >= ZAP:
        c.set_scene("black")
        c.subs = False
        c.hud = False
        c.bars = 0.0
    yield "back"
    if c.scene == "heaven":
        th = throne()
        c.world.paste(th, (THRONE[0] - th.width // 2, THRONE[1] - th.height + 4), th)
    yield "front"
    if c.scene == "heaven":
        god_trophy(c)
        d = ImageDraw.Draw(c.world)                    # a cloud for Sir David to hide behind
        cloud(d, 8, 164, 112, 18, HEAVEN["cloud"], ("hide", 0))
        if ZAP - 0.3 <= c.t < ZAP:                      # the bolt, straight down the lens
            hx, hy = anchor(c, "morgan", "hand")
            tx, ty = c.cam.world_pt(W / 2, H / 2 + 10)
            pts = [(hx, hy)]
            for k in range(1, 7):
                p = k / 6
                pts.append((lerp(hx, tx, p) + (rnd("bolt", k, c.f) - 0.5) * 12, lerp(hy, ty, p)))
            d.line(pts, fill=(255, 250, 200), width=3)
            d.line(pts, fill=(255, 255, 255), width=1)
            c.add_flash(0.7, (255, 250, 220))
    yield "top"
    if c.scene != "black" and REC_ON - 0.25 <= c.t < REC_ON + 0.15:
        CH.static_noise(c.ui, 0.6, seed=c.f)
    if doc and c.t >= REC_ON + 0.5:
        CH.lower_third(c.ui, c.t - (REC_ON + 0.5), "MORGANUS FREEMANII (DEUS)", "IN HIS NATURAL HABITAT", y=30,
                       out_at=ZAP - REC_ON - 1.4)
    if ZAP - 0.1 <= c.t < ZAP + 0.35:
        CH.static_noise(c.ui, 1.0, seed=c.f)
    if c.t >= CARD:
        a = ramp(c.t, CARD, CARD + 0.5) * (1 - ramp(c.t, TL.DURATION - 0.5, TL.DURATION - 0.05))
        if a > 0:
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            pixel.text(layer, (W // 2, 70), "NO NARRATORS WERE HARMED", PRESS, C["text"], shadow=None, anchor="ma")
            pixel.text(layer, (W // 2, 84), "IN THE MAKING OF THIS FILM.", PRESS, C["text"], shadow=None, anchor="ma")
            if c.t >= CARD_LATE:
                pixel.text(layer, (W // 2, 106), "ONE WAS OUTCOMPETED.", PRESS, C["gold"], shadow=None, anchor="ma")
            CH.fade_layer(layer, a)
            c.ui.alpha_composite(layer)
