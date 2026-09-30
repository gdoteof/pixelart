"""Verse 1: Sir David's documentary on Morganus freemanii (v1 0-17).

Sir David presents from the ferns with his furry field mic; Morgan is the
specimen in the vocal booth, filmed like wildlife: a throat-pouch mating display,
camera-trap stills of the same six days, a zoo enclosure, a franchise of identical
posters. Then the cutaways: the Serengeti, 70s archive footage, a children's book
read front to back, God on a cheque, Darwin in the corner, a character-select
screen, a lyrebird doing Morgan's voice, an ice floe of emperors, a church organ,
and the booth turning into a morgue.
"""
from critters import lion, penguin
from gagkit import (C, CH, INK, PRESS, PRESS16, SILK, H, W, Canvas, Image, ImageDraw, anchor, back_out, blend,
                    blend_poly, clamp, ease_in, ease_in_out, ease_out, figure, gag, lerp, line_t, lru_cache, math, mirror, mix,
                    np, paste, pixel, ramp, rnd, scaled, scene, text_width, ui_at, vgrad, wt)
from props import big_text, bubble, checkbox, label, pop_text, puff, ring, sparkle, stamp
from sets import BOOTH, BOOTH_CX, BOOTH_FLOOR, MORGAN_BOOTH, frond

BX0, BY0, BX1, BY1 = BOOTH
INSIDE = (BX0 + 4, BY0 + 4, BX1 - 4, BY1 - 4)         # the booth's foam-lined interior
FROG_RED, FROG_RED_SH, FROG_RED_HI = (226, 40, 52), (160, 22, 40), (255, 140, 140)
TELE = (212, 110, 18)                                   # telephoto on the specimen, the prize out of frame
BOOTH_SHOT = (198, 102, 12)                             # the booth, with room on the left for signage


# --- shared bits ----------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def bust(who, scale=2, w=30, h=28, facing=1, **pose):
    """Head and shoulders of a character, scaled up for screens, posters and tiles."""
    spr, a = figure(who, facing, **pose)
    hx, hy = a["head"]
    x0, y0 = int(hx - w / 2), int(hy - 12)
    return scaled(spr.crop((x0, y0, x0 + w, y0 + h)), scale)


def recolor(img, mapping):
    """A copy of a sprite with exact colours swapped (hair dyed, suits re-tailored)."""
    a = np.array(img)
    out = a.copy()
    for src, dst in mapping.items():
        m = (a[..., 0] == src[0]) & (a[..., 1] == src[1]) & (a[..., 2] == src[2]) & (a[..., 3] > 0)
        out[m, :3] = dst
    return Image.fromarray(out)


def panel(ui, box, fill=(12, 10, 16), border=C["text"]):
    d = ImageDraw.Draw(ui)
    x0, y0, x1, y1 = (int(v) for v in box)
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK + (255,))
    d.rectangle((x0, y0, x1, y1), fill=tuple(fill) + (255,), outline=tuple(border) + (255,) if border else None)


def morgan_mouth(c):
    return anchor(c, "morgan", "mouth")


def presenting(c, arm="point"):
    """Sir David presents to camera, gesturing at the booth."""
    s = c.st["david"]
    s["arm"] = arm
    s["gesture"] = False


# --- 0: "Watch the male puff his chest in a slow mating display," ----------------------------------

@lru_cache(maxsize=None)
def pouch(r):
    """A frigatebird's inflated red throat pouch."""
    w, h = 2 * r + 3, int(2 * r * 0.9) + 3
    s = Canvas(w, h)
    s.ell((1, 1, w - 2, h - 2), FROG_RED)
    s.ell((w // 2 - 1, h // 2, w - 2, h - 2), FROG_RED_SH)
    s.ell((2, 2, w - 3, h - 4), FROG_RED)
    s.ell((3, 3, 3 + r // 2 + 1, 3 + r // 2), FROG_RED_HI)
    s.px((4, 4), (255, 230, 230))
    for k in range(r // 3):                                 # the veins of a well-stretched pouch
        s.px((w // 2 + k, h // 2 + (k % 2)), FROG_RED_SH)
    return s.done()


@gag("v1", 0)
def mating_display(c, L):
    puff_t, slow = wt(L, "puff"), wt(L, "slow")
    m = c.st["morgan"]
    if c.t < puff_t:
        c.shot = "present"
        presenting(c, "point")
    else:
        c.shot = TELE
        m.update(arm="hip", brows="up", eyes="half", mouth="smirk", lean=-1, gesture=False)
    yield "mid"
    if c.t >= puff_t:
        age = c.t - puff_t
        grow = ease_out(ramp(age, 0, 0.9))
        speed = 9.0 if c.t < slow else 2.2                 # slow motion, as promised
        phase = age * 9.0 if c.t < slow else (slow - puff_t) * 9.0 + (c.t - slow) * speed
        r = int(round(2 + 6 * grow + 0.7 * math.sin(phase)))
        mx, my = morgan_mouth(c)
        p = pouch(max(2, r))
        c.world.paste(p, (int(mx - 4), int(my + 4)), p)
    yield "top"
    if c.t >= slow:
        if int(c.t * 3) % 2 == 0:
            pixel.text(c.ui, (22, 25), "SLOW MOTION  1/4x", SILK, C["tele"], shadow=INK)
    if c.t >= puff_t:
        CH.lower_third(c.ui, c.t - puff_t - 0.3, "FIG. 1: MATING DISPLAY",
                       "INTERESTED FEMALES: 0" if c.t >= slow + 0.2 else None, y=36)


# --- 1: "Same pitch, same pace, same wise old man every day." --------------------------------------

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT")


@lru_cache(maxsize=None)
def trail_still(w=88, h=54):
    """A camera-trap still: the specimen in his booth, in the grey of an infrared flash."""
    img = Image.new("RGB", (w, h), (54, 54, 60))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 4):                              # the foam wedges behind him
        for x in range((y // 4) % 2 * 2, w, 4):
            d.point((x, y), fill=(44, 44, 50))
    b = bust("morgan", 2, 30, 26, 1, hat="headphones", eyes="half", mouth="smirk", arm="cross")
    img.paste(b, (w // 2 - b.width // 2, h - b.height), b)
    arr = np.asarray(img).astype(np.float32)
    lum = arr.mean(axis=2, keepdims=True)
    arr = lum * np.array([0.95, 1.0, 0.95]) * 1.15 + 6
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


@gag("v1", 1)
def camera_trap(c, L):
    c.shot = TELE
    pops = [wt(L, "Same"), wt(L, "pitch"), wt(L, "same", 1), wt(L, "same", 2), wt(L, "old"), wt(L, "every")]
    day = wt(L, "day")
    yield "ui"
    if c.t < pops[0] - 0.05:
        return
    tw, th, gap = 88, 50, 5
    x0 = (W - (3 * tw + 2 * gap)) // 2
    y0 = 37
    panel(c.ui, (x0 - 5, y0 - 13, x0 + 3 * tw + 2 * gap + 4, y0 + 2 * th + gap + 4), (16, 16, 20), None)
    pixel.text(c.ui, (x0, y0 - 12), "CAMERA TRAP 04  -  6 DAYS", SILK, C["tele"], shadow=None)
    still = trail_still(tw, th)
    for k, name in enumerate(DAYS):
        age = c.t - pops[k]
        if age < 0:
            continue
        x, y = x0 + (k % 3) * (tw + gap), y0 + (k // 3) * (th + gap)
        c.ui.paste(still, (x, y))
        if age < 0.06:                                   # the IR flash
            ImageDraw.Draw(c.ui).rectangle((x, y, x + tw - 1, y + th - 1), fill=(236, 240, 236, 255))
        ImageDraw.Draw(c.ui).rectangle((x, y + th - 9, x + tw - 1, y + th - 1), fill=(0, 0, 0, 255))
        pixel.text(c.ui, (x + 3, y + th - 10), f"{name} 09:00  18C", SILK, (236, 236, 236), shadow=None)
    if c.t >= day:
        stamp(c.ui, W // 2, y0 + th + gap // 2, "NO CHANGE DETECTED", C["red"], angle=-6, size=16, age=c.t - day)


# --- 2: "He's a zoo animal, pacin' in the same small cage," ----------------------------------------

@lru_cache(maxsize=None)
def zoo_sign():
    rows = ("MORGANUS", "FREEMANII", "DO NOT FEED")
    w = max(text_width(r, SILK) for r in rows) + 8
    s = Canvas(w + 2, 46)
    s.rect((w // 2 - 1, 24, w // 2 + 2, 45), "wood_sh")                  # the post
    s.rect((1, 1, w, 26), (60, 96, 70))
    s.rect((2, 2, w - 1, 25), (74, 116, 84))
    s.text((w // 2 + 1, 1), rows[0], "paper", anchor="ma")
    s.text((w // 2 + 1, 9), rows[1], "gold_hi", anchor="ma")
    s.text((w // 2 + 1, 17), rows[2], (190, 220, 190), anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def padlock():
    s = Canvas(9, 11)
    s.line([(2, 5), (2, 1), (6, 1), (6, 5)], "steel_sh")
    s.rect((1, 5, 7, 10), "gold")
    s.px((4, 7), "ink")
    s.line([(1, 5), (7, 5)], "gold_hi")
    return s.done()


def bars(img, drop, color=(46, 44, 52), hi=(110, 108, 120)):
    """Zoo bars over the front of the booth, `drop` 0-1 of the way down."""
    x0, y0, x1, y1 = INSIDE
    bottom = int(y0 + (y1 - y0) * drop)
    if bottom <= y0:
        return
    d = ImageDraw.Draw(img)
    for x in range(x0 + 2, x1, 6):
        d.rectangle((x, y0 - 2, x + 1, bottom), fill=color)
        d.point((x, y0 - 2), fill=hi)
    d.rectangle((x0 - 2, y0 - 3, x1 + 2, y0 - 1), fill=color)
    if drop >= 1:
        d.rectangle((x0 - 2, y1 - 1, x1 + 2, y1 + 1), fill=color)


@gag("v1", 2)
def zoo_animal(c, L):
    c.shot = (BOOTH_SHOT[0] - 14, BOOTH_SHOT[1], BOOTH_SHOT[2])     # room for the enclosure sign
    c.st["david"]["hidden"] = True                     # he's behind the camera for this one
    zoo, pacing, cage = wt(L, "zoo"), wt(L, "pacin"), wt(L, "cage")
    m = c.st["morgan"]
    if c.t >= pacing:                                   # back and forth, back and forth
        ph = (c.t - pacing) * 1.4
        m["x"] = MORGAN_BOOTH[0] + 9 * math.sin(ph * math.pi) - 2
        m["facing"] = 1 if math.cos(ph * math.pi) > 0 else -1
        m["body"] = "walk1" if int(c.t * 5) % 2 else "walk2"
        m.update(arm="down", gesture=False, eyes="half", mouth="frown")
    drop = ease_in(ramp(c.t, zoo, zoo + 0.3))
    if 0 <= c.t - (zoo + 0.3) < 0.15:
        c.add_shake(4)
    if 0 <= c.t - cage < 0.12:
        c.add_shake(3)
    yield "mid"
    bars(c.world, drop)
    if c.t >= wt(L, "animal"):
        dy = int((1 - back_out(ramp(c.t, wt(L, "animal"), wt(L, "animal") + 0.25))) * 30)
        sg = zoo_sign()
        c.world.paste(sg, (BX0 - sg.width + 1, 101 - dy), sg)
    if c.t >= cage:
        pl = padlock()
        c.world.paste(pl, (BOOTH_CX + 2, 104 + int(wobble_y(c.t - cage))), pl)


def wobble_y(age):
    return math.sin(age * 30) * 2 * max(0.0, 1 - age / 0.4)


# --- 3: "Same mentor, same monologue, same velvet, same page." (kill) -------------------------------

POSTERS = [("THE MENTOR", None, (30, 44, 90)), ("THE MENTOR 2", "MONOLOGUE", (96, 30, 40)),
           ("THE MENTOR 3", "VELVET", (40, 80, 56)), ("THE MENTOR 4", "SAME PAGE", (78, 46, 104))]


@lru_cache(maxsize=None)
def mentor_poster(k, w=54, h=84):
    title, sub, color = POSTERS[k]
    img = Image.new("RGBA", (w, h), color + (255,))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    for y in range(0, h, 2):                                  # a glow behind the star
        r = int(22 - abs(y - 40) * 0.5)
        if r > 0:
            d.line([(w // 2 - r, y), (w // 2 + r, y)], fill=mix(color, (255, 220, 160), 0.18))
    pixel.text(img, (w // 2, 3), "FREEMAN", SILK, (236, 226, 200), shadow=None, anchor="ma")
    b = bust("morgan", 1, 30, 28, 1, eyes="half", mouth="smile", brows="up")
    img.alpha_composite(b, (w // 2 - b.width // 2, 16))
    d.rectangle((0, 46, w, h), fill=mix(color, (0, 0, 0), 0.45) + (255,))
    pixel.text(img, (w // 2, 50), title.replace("THE ", ""), SILK, C["gold_hi"], shadow=INK, anchor="ma")
    pixel.text(img, (w // 2, 43), "THE", SILK, (236, 226, 200), shadow=None, anchor="ma")
    if sub:
        pixel.text(img, (w // 2, 60), sub, SILK, (236, 226, 200), shadow=None, anchor="ma")
    pixel.text(img, (w // 2, h - 12), "WISE.", SILK, (150, 146, 160), shadow=None, anchor="ma")
    d.rectangle((0, 0, w - 1, h - 1), outline=INK + (255,))
    return img


@gag("v1", 3)
def the_mentor(c, L):
    c.shot = "wide"
    c.mood = 0.8
    pops = [wt(L, "mentor"), wt(L, "monologue"), wt(L, "velvet"), wt(L, "page")]
    stamps = wt(L, "page") + 0.05
    yield "ui"
    w, gap = 54, 6
    x0 = 12
    for k, t0 in enumerate(pops):
        age = c.t - t0 + 0.12
        if age < 0:
            continue
        dy = int((1 - back_out(ramp(age, 0, 0.22))) * -40)
        x = x0 + k * (w + gap)
        img = mentor_poster(k)
        c.ui.paste(img, (x, 30 + dy), img)
    if c.t >= stamps:
        stamp(c.ui, x0 + 2 * (w + gap) - gap // 2, 74, "SAME.", C["red"], angle=-10, size=24, age=c.t - stamps)


# --- 4: "I was out in the Serengeti, lion breathin' down my neck," -----------------------------------

SAV = {"sky": (238, 148, 84), "sky2": (255, 206, 132), "sun": (255, 238, 184), "hill": (196, 120, 84),
       "grass": (214, 170, 92), "grass_sh": (178, 134, 70), "grass_hi": (240, 206, 128), "tree": (70, 46, 46)}
SAV_GROUND = 128
CROUCH_AT = (172, 160)


@lru_cache(maxsize=1)
def serengeti_static():
    img = Image.new("RGB", (W, H), SAV["sky"])
    vgrad(img, (0, 0, W, SAV_GROUND), SAV["sky"], SAV["sky2"], steps=5)
    d = ImageDraw.Draw(img)
    d.ellipse((222, 64, 282, 124), fill=SAV["sun"])
    for k in range(6):                                            # a far line of hills
        x = k * 64 - 20
        d.ellipse((x, 108, x + 90, 150), fill=SAV["hill"])
    d.rectangle((0, SAV_GROUND, W, H), fill=SAV["grass"])
    # the acacia: a flat umbrella of a crown on a bent trunk
    d.polygon([(58, SAV_GROUND + 2), (62, 96), (70, 80), (74, 82), (67, 98), (66, SAV_GROUND + 2)], fill=SAV["tree"])
    d.line([(66, 90), (84, 78)], fill=SAV["tree"], width=2)
    d.line([(64, 88), (44, 80)], fill=SAV["tree"], width=2)
    for k in range(7):
        x = 22 + k * 12
        d.ellipse((x, 70 - (k % 2) * 3, x + 22, 82), fill=SAV["tree"])
    for k in range(120):
        x, y = rnd("sav", k) * W, SAV_GROUND + 3 + rnd("sav-y", k) * (H - SAV_GROUND - 3)
        d.line([(x, y), (x + 1, y - 3 - int(rnd("sav-h", k) * 3))], fill=SAV["grass_hi"] if k % 3 else SAV["grass_sh"])
    return img


def savanna_grass(img, t, y0=168, n=40, seed="blades"):
    """Tall grass right in front of the lens, swaying."""
    d = ImageDraw.Draw(img)
    for k in range(n):
        x = rnd(seed, k) * (W + 20) - 10
        h = 16 + rnd(seed, "h", k) * 22
        sway = math.sin(t * 1.6 + k) * 3
        d.line([(x, H), (x + sway, H - h)], fill=SAV["grass_sh"] if k % 2 else SAV["grass"], width=2)


def serengeti(c):
    img = serengeti_static().copy()
    blend(img, 1.0, (255, 200, 120), 0.06 + 0.03 * math.sin(c.t * 0.8))       # heat shimmer of colour
    return img


def serengeti_near(c):
    savanna_grass(c.world, c.t)


scene("v1_serengeti", near=serengeti_near,
      shots={"david": (150, 132, 12), "close": (156, 128, 18)},
      cast={"david": dict(x=CROUCH_AT[0], y=CROUCH_AT[1], facing=1, body="crouch", hat="pith", z=1)})(serengeti)


@gag("v1", 4)
def serengeti_lion(c, L):
    c.set_scene("v1_serengeti")
    lion_t, breath, neck = wt(L, "lion"), wt(L, "breathin"), wt(L, "neck")
    c.shot = "david" if c.t < breath else "close"
    s = c.st["david"]
    s.update(arm="whisper", gesture=False, brows="up")
    if c.t >= neck:
        s["eyes"] = "side"
    # the lion pads up behind him until its nose is at his collar
    arrive = lion_t + 0.1
    lx = lerp(-40, 116, ease_out(ramp(c.t, L.t0 + 0.3, arrive)))
    c.vars["lion_x"] = lx
    breathing = c.t >= breath
    if breathing:
        s["dx"] = 1 if int(c.t * 5) % 2 else 0
    yield "back"
    sp = lion("open" if breathing and int(c.t * 2.5) % 2 == 0 else "shut")
    step = 1 if c.t < arrive and int(c.t * 8) % 2 else 0
    c.world.paste(sp, (int(lx), CROUCH_AT[1] - sp.height + 1 - step), sp)
    yield "front"
    if breathing:
        nx, ny = lx + 47, CROUCH_AT[1] - sp.height + 12
        for k in range(3):
            age = (c.t - breath - k * 0.27) % 0.8
            puff(c.world, nx - 1, ny + 2, age, size=0.35, seed=k, color=(255, 250, 240), drift=(4, -12), life=0.7)
    yield "ui"
    CH.lower_third(c.ui, c.t - L.t0 - 0.25, "THE SERENGETI", "SIR DAVID, NOT BOTHERED", y=36)
    if c.t >= neck:
        hx, hy = ui_at(c, lx + 30, CROUCH_AT[1] - sp.height + 2)
        CH.callout(c.ui, c.t - neck, "LION (VERY CLOSE)", hx, hy, hx - 20, hy - 22)


# --- 5: "You were on The Electric Company spellin' "cat" for a cheque." -------------------------

HAIR_70S = {C["mhair"]: (40, 30, 30), C["mhair_sh"]: (62, 46, 40)}
SUIT_70S = {C["suit"]: (190, 116, 50), C["suit_sh"]: (150, 86, 40), C["suit_hi"]: (220, 150, 80),
            C["tie"]: (240, 206, 90), C["tie_hi"]: (255, 230, 140)}


@lru_cache(maxsize=None)
def young_morgan(arm="point", mouth="open"):
    """Morgan in the seventies: dark hair, a mustard suit."""
    spr, _ = figure("morgan", 1, arm=arm, mouth=mouth, brows="up")
    return recolor(spr, {**HAIR_70S, **SUIT_70S})


@lru_cache(maxsize=None)
def seventies_screen(w, h, letters, cat=False, frame=0):
    """The kids' show on the telly: rainbow stripes, the host with a pointer, the word spelt out."""
    img = Image.new("RGB", (w, h), (250, 226, 150))
    d = ImageDraw.Draw(img)
    bands = [(236, 96, 40), (246, 150, 40), (250, 200, 60), (120, 170, 80), (70, 130, 190)]
    for k, bc in enumerate(bands):
        d.ellipse((-30 - k * 12, h - 20 - k * 12, w * 0.6 + k * 12, h + 60 + k * 12), outline=bc, width=5)
    host = young_morgan("point", "open" if frame else "grin")
    img.paste(host, (4, h - host.height + 8), host)
    d.fontmode = "1"
    x = 52
    for i, ch in enumerate("CAT"):
        if i < letters:
            d.rectangle((x - 1, 14, x + 21, 38), fill=INK)
            d.rectangle((x, 15, x + 20, 37), fill=[(236, 60, 60), (60, 140, 220), (250, 190, 40)][i])
            d.text((x + 3, 18), ch, font=PRESS16, fill=(255, 255, 255))
        x += 26
    if cat:
        cx, cy = 88, 48
        d.ellipse((cx, cy, cx + 20, cy + 12), fill=(250, 170, 70))
        d.polygon([(cx + 13, cy - 2), (cx + 15, cy + 2), (cx + 11, cy + 2)], fill=(250, 170, 70))
        d.polygon([(cx + 18, cy - 2), (cx + 20, cy + 2), (cx + 16, cy + 2)], fill=(250, 170, 70))
        d.ellipse((cx + 11, cy, cx + 22, cy + 9), fill=(250, 170, 70))
        d.point((cx + 15, cy + 4), fill=INK); d.point((cx + 19, cy + 4), fill=INK)
    return img


@lru_cache(maxsize=None)
def cheque(amount="$12.50"):
    s = Canvas(136, 46)
    s.rect((1, 1, 134, 44), (226, 238, 214))
    s.rect((1, 1, 134, 8), (150, 190, 150))
    s.text((5, 1), "FIRST NATIONAL BANK", "ink")
    s.text((5, 12), "PAY TO: MORGAN FREEMAN", "ink")
    s.text((5, 21), "FOR: SPELLING 'CAT'", "ink")
    s.rect((94, 28, 130, 38), "white")
    s.text((97, 29), amount, "ink")
    s.line([(5, 39), (60, 37)], "sea")
    return s.done()


@gag("v1", 5)
def electric_company(c, L):
    c.set_scene("black")
    c.shot = "wide"
    spell, cat, chq = wt(L, "spellin"), wt(L, "cat"), wt(L, "cheque")
    yield "ui"
    ImageDraw.Draw(c.ui).rectangle((0, 0, W, H), fill=(34, 28, 30, 255))
    for k in range(9):                                                # the wallpaper of the archive
        ImageDraw.Draw(c.ui).line([(k * 40 - 20, 0), (k * 40 + 60, H)], fill=(44, 36, 38, 255), width=8)
    letters = 0 if c.t < spell else 1 + int((c.t - spell) / max(0.05, (cat - spell) / 2.2))
    screen = seventies_screen(142, 88, min(3, letters), c.t >= cat + 0.15, int(c.t * 6) % 2)
    tv_box = (64, 30, 64 + 142 + 22, 30 + 88 + 8)
    from props import tv
    tv(c.ui, tv_box, screen)
    d = ImageDraw.Draw(c.ui)
    d.rectangle((tv_box[0] + 10, tv_box[3] + 1, tv_box[0] + 16, tv_box[3] + 10), fill=(70, 50, 40, 255))
    d.rectangle((tv_box[2] - 16, tv_box[3] + 1, tv_box[2] - 10, tv_box[3] + 10), fill=(70, 50, 40, 255))
    CH.lower_third(c.ui, c.t - L.t0 - 0.2, "ARCHIVE FOOTAGE", "PUBLIC TELEVISION, 1971", y=24, out_at=2.2)
    if c.t >= chq:
        age = c.t - chq
        y = int(lerp(H, 70, back_out(ramp(age, 0, 0.3))))
        img = cheque()
        c.ui.paste(img, (W - img.width - 18, y), img)
        pop_text(c.ui, W - 86, y - 22, "KA-CHING!", age, fnt=PRESS16, top=C["gold_hi"], bottom=C["gold"])


# --- 6-7: "Easy Reader? Easy, reader. I'll read you front to back:" / "Chapter one: a deep voice. ..." -------

BOOK_YELLOW, BOOK_RED, PAPER, PAPER_SH = (250, 214, 70), (214, 50, 50), (246, 238, 214), (214, 202, 172)
BOOK = (106, 28, 214, 136)                     # the closed book on screen (UI)
SPREAD = (54, 30, 266, 136)                    # the open book


def book_cover(ui, box, back=False):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK + (255,))
    d.rectangle((x0, y0, x1, y1), fill=BOOK_YELLOW + (255,))
    spine_x = x1 - 6 if back else x0
    d.rectangle((spine_x, y0, spine_x + 6, y1), fill=BOOK_RED + (255,))
    cx = (x0 + x1) // 2 + (-3 if back else 3)
    if back:
        pixel.text(ui, (cx, y0 + 10), "THE END", PRESS, BOOK_RED, shadow=None, anchor="ma")
        pixel.text(ui, (cx, y0 + 26), "ALSO AVAILABLE:", SILK, INK, shadow=None, anchor="ma")
        pixel.text(ui, (cx, y0 + 34), "NOTHING.", SILK, INK, shadow=None, anchor="ma")
        for k in range(18):                                      # barcode
            if rnd("bar", k) > 0.35:
                d.line([(cx - 18 + 2 * k, y1 - 26), (cx - 18 + 2 * k, y1 - 10)], fill=INK + (255,))
        return
    big_text(ui, (cx, y0 + 6), "EASY", PRESS16, top=BOOK_RED, bottom=(170, 30, 40), anchor="ma")
    big_text(ui, (cx, y0 + 26), "READER", PRESS16, top=BOOK_RED, bottom=(170, 30, 40), anchor="ma")
    host = young_morgan("palm", "grin")
    ui.alpha_composite(host, (cx - host.width // 2, y1 - host.height - 2))
    d.ellipse((x1 - 30, y0 + 44, x1 - 4, y0 + 70), fill=(60, 130, 220, 255), outline=INK + (255,))
    pixel.text(ui, (x1 - 17, y0 + 50), "AGES", SILK, (255, 255, 255), shadow=None, anchor="ma")
    pixel.text(ui, (x1 - 17, y0 + 58), "3-5", SILK, (255, 255, 255), shadow=None, anchor="ma")


def open_book(ui, box, left, right, turn=None):
    """An open book: `left` and `right` are lists of (text, font, colour) rows. `turn` in (0, 1) shows a
    page mid-flip, right to left."""
    x0, y0, x1, y1 = box
    mid = (x0 + x1) // 2
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    d.rectangle((x0 - 3, y0 - 1, x1 + 3, y1 + 3), fill=INK + (255,))
    d.rectangle((x0 - 2, y0, x1 + 2, y1 + 2), fill=BOOK_RED + (255,))
    for (a, b) in ((x0, mid - 1), (mid + 1, x1)):
        d.rectangle((a, y0 + 1, b, y1), fill=PAPER + (255,))
    d.rectangle((mid - 3, y0 + 1, mid + 3, y1), fill=PAPER_SH + (255,))
    d.line([(mid, y0 + 1), (mid, y1)], fill=INK + (255,))
    for rows, px in ((left, x0 + 8), (right, mid + 8)):
        y = y0 + 8
        for s, fnt, colr in rows:
            if s == "<img>":
                continue
            pixel.text(ui, (px, y), s, fnt, colr, shadow=None)
            y += fnt.size + 5
    if turn is not None and 0 < turn < 1:
        w = int((x1 - mid) * math.cos(turn * math.pi))
        a, b = sorted((mid, mid + w))
        d.polygon([(a, y0 - 2 if w > 0 else y0 + 1), (b, y0 + 1), (b, y1), (a, y1 + (2 if w > 0 else 0))],
                  fill=PAPER + (255,), outline=INK + (255,))


def reading_room(c):
    """The book is shown over the clearing, dimmed: an insert shot."""
    c.shot = "present"
    c.mood = 0.55
    presenting(c, "hold")


@gag("v1", 6)
def easy_reader(c, L):
    reading_room(c)
    front, back = wt(L, "front"), wt(L, "back")
    yield "ui"
    age = c.t - L.t0 + 0.1
    if age < 0:
        return
    dy = int((1 - back_out(ramp(age, 0, 0.25))) * 60)
    x0, y0, x1, y1 = BOOK
    box = (x0, y0 + dy, x1, y1 + dy)
    if c.t < front:
        book_cover(c.ui, box)
    elif c.t < back:                                    # riffling through, front to back
        p = ramp(c.t, front, back)
        k = int(p * 6)
        open_book(c.ui, SPREAD, [], [], turn=(p * 6) % 1.0)
        pixel.text(c.ui, ((SPREAD[0] + SPREAD[2]) // 2, SPREAD[3] - 12), f"PAGE {k * 2 + 1}", SILK, INK, shadow=None,
                   anchor="ma")
    else:
        book_cover(c.ui, box, back=True)
    if wt(L, "Easy", 1) <= c.t < front:                 # "Easy, reader."
        bubble(c.ui, 70, 60, "EASY.", tail=(62, 86))


@gag("v1", 7)
def chapter_two(c, L):
    reading_room(c)
    deep = wt(L, "deep")
    ch2, its, act = wt(L, "Chapter", 1), wt(L, "that's"), wt(L, "act")
    shut = act + 0.06
    yield "ui"
    if c.t < shut:
        if c.t < ch2:
            left = [("CHAPTER", PRESS, BOOK_RED), ("ONE", PRESS16, BOOK_RED)]
            right = [("A DEEP", PRESS, INK), ("VOICE.", PRESS, INK)] if c.t >= deep else []
            open_book(c.ui, SPREAD, left, right)
            if c.t >= deep:                             # the illustration: a deep voice going "mmm"
                b = bust("morgan", 2, 30, 26, 1, mouth="o", eyes="shut", brows="up")
                c.ui.alpha_composite(b, (SPREAD[0] + 14, SPREAD[3] - b.height - 1))
                pixel.text(c.ui, (SPREAD[0] + 76, SPREAD[3] - 40), "MMMM.", PRESS, (120, 80, 140), shadow=None)
        else:
            left = [("CHAPTER", PRESS, BOOK_RED), ("TWO", PRESS16, BOOK_RED)]
            right = [("THAT'S IT.", PRESS, INK)] if c.t >= its else []
            if c.t >= wt(L, "That's", 1):
                right += [("", PRESS, INK), ("THAT'S THE", PRESS, INK), ("ACT.", PRESS, INK)]
            turn = ramp(c.t, ch2 - 0.05, ch2 + 0.2)
            open_book(c.ui, SPREAD, left, right, turn=turn if turn < 1 else None)
    else:                                               # slammed shut: THE END
        age = c.t - shut
        x0, y0, x1, y1 = BOOK
        jolt = int(math.sin(age * 40) * 3 * max(0.0, 1 - age / 0.3))
        book_cover(c.ui, (x0, y0 + jolt, x1, y1 + jolt), back=True)
        for k in range(4):
            puff(c.ui, x0 + 10 + k * 22, y1 + 2, age, size=0.5, seed=k, color=(230, 220, 190), drift=((k - 1.5) * 12, -4),
                 life=0.6)


# --- 8: "You played God for Jim Carrey and you cashed it, fair enough," ------------------------------

@lru_cache(maxsize=None)
def banknote(flip=0):
    s = Canvas(12, 7 if not flip else 5)
    if flip:
        s.rect((1, 1, 10, 3), (126, 176, 110))
        return s.done()
    s.rect((1, 1, 10, 5), (150, 196, 130))
    s.rect((4, 2, 7, 4), (110, 160, 100))
    s.px((5, 3), (200, 230, 180))
    return s.done()


@lru_cache(maxsize=None)
def coin():
    """A gold dollar, to replace a halo."""
    s = Canvas(13, 13)
    s.ell((1, 1, 11, 11), "gold")
    s.ell((2, 2, 10, 10), "gold_hi")
    s.ell((3, 3, 10, 10), "gold")
    s.pxs([(6, 3), (5, 4), (6, 4), (7, 4), (5, 5), (5, 6), (6, 6), (7, 6), (7, 7), (5, 8), (6, 8), (7, 8), (6, 9)],
          "gold_sh")
    return s.done()


def halo(img, x, y, t):
    d = ImageDraw.Draw(img)
    bob = int(round(math.sin(t * 3)))
    d.ellipse((x - 7, y - 2 + bob, x + 7, y + 2 + bob), outline=C["gold_hi"])
    d.ellipse((x - 6, y - 1 + bob, x + 6, y + 1 + bob), outline=C["gold"])


def money_rain(img, t, t0, box, n=10, seed="note", speed=85, back=None):
    """Banknotes fluttering down inside `box`, starting from its top at t0 and looping."""
    x0, y0, x1, y1 = box
    for k in range(n):
        if back is not None and (k % 2 == 0) != back:
            continue
        run = (t - t0) * speed - rnd(seed, k) * 50
        if run < 0:
            continue
        y = y0 - 6 + run % (y1 - y0)
        x = x0 + 4 + rnd(seed, "x", k) * (x1 - x0 - 16) + math.sin(run * 0.15 + k) * 4
        paste(img, banknote(int(run / 7 + k) % 2), x, y, "mm")


@gag("v1", 8)
def god_for_hire(c, L):
    god, carrey, cashed, fair, enough = wt(L, "God"), wt(L, "Jim"), wt(L, "cashed"), wt(L, "fair"), wt(L, "enough")
    m, s = c.st["morgan"], c.st["david"]
    if c.t < fair:
        c.shot = "booth"
        s["hidden"] = True
    else:                                               # Sir David catches a stray note, and keeps it
        c.shot = "present"
        presenting(c, "shrug")
        s["brows"] = "up"
        if c.t >= enough:
            s["eyes"] = "side"
    if c.t >= god:
        m.update(outfit="god", arm="up" if c.t < cashed else "palm", mouth="smile", eyes="half", gesture=False,
                 hat="none", rim=0.8, rim_color=(255, 236, 170))
        c.vars["booth_light"] = 1.6
    yield "back"
    if c.t >= god:                                      # heaven's light fills the booth
        x0, y0, x1, y1 = INSIDE
        blend_poly(c.world, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (255, 226, 150),
                   0.35 * ease_out(ramp(c.t, god, god + 0.3)))
    if c.t >= cashed:
        money_rain(c.world, c.t, cashed, INSIDE, back=True)
    yield "mid"
    if c.t >= god:
        hx, hy = anchor(c, "morgan", "top")
        if c.t < cashed:
            halo(c.world, hx, hy - 3, c.t)
        else:                                           # the halo spins round into a dollar
            spin = abs(math.cos((c.t - cashed) * 7))
            cn = coin()
            cn = cn.resize((max(1, int(cn.width * spin)), cn.height), Image.NEAREST)
            paste(c.world, cn, hx, hy - 8 + math.sin(c.t * 3), "mm")
        if c.t < god + 0.3:
            d = ImageDraw.Draw(c.world)
            for k in range(8):
                a = k * math.pi / 4
                r1 = 12 + 30 * ramp(c.t, god, god + 0.3)
                d.line([(hx + math.cos(a) * 12, hy + 10 + math.sin(a) * 12),
                        (hx + math.cos(a) * r1, hy + 10 + math.sin(a) * r1)], fill=C["gold_hi"])
    if c.t >= cashed:
        money_rain(c.world, c.t, cashed, INSIDE, back=False)
    yield "front"
    if c.t >= fair:                                     # one note escapes the booth
        hx, hy = anchor(c, "david", "hand")
        p = ease_in_out(ramp(c.t, fair, enough))
        nx, ny = lerp(BX0 + 6, hx, p), lerp(BY0 + 30, hy - 2, p) - math.sin(p * math.pi) * 10
        paste(c.world, banknote(int(c.t * 10) % 2 if p < 1 else 0), nx + math.sin(p * 9) * 3 * (1 - p), ny, "mm")
    yield "ui"
    if carrey <= c.t < fair:
        CH.lower_third(c.ui, c.t - carrey, "GOD (FOR HIRE)", "BRUCE ALMIGHTY, 2003", y=36, out_at=cashed - carrey - 0.1)
    if cashed <= c.t < fair:
        pop_text(c.ui, W // 2, 34, "CHA-CHING!", c.t - cashed, fnt=PRESS16, top=C["gold_hi"], bottom=C["gold"])


# --- 9: "But I got Darwin in my corner, and the fossils call your bluff." -------------------------------

BONE, BONE_SH, BONE_DK = (232, 222, 192), (190, 176, 146), (140, 126, 104)
VISOR, VISOR_SH = (60, 170, 90), (36, 120, 64)
FELT, FELT_SH, FELT_HI = (40, 112, 64), (28, 84, 48), (60, 140, 84)


@lru_cache(maxsize=None)
def darwin(thumb=False):
    """Charles Darwin, head and shoulders: the dome, the great white beard, a towel for the corner."""
    s = Canvas(44, 46)
    s.poly([(4, 45), (8, 30), (36, 30), (40, 45)], (40, 36, 44))                  # frock coat
    s.poly([(16, 30), (28, 30), (22, 40)], "white")                               # collar
    s.rect((6, 30, 12, 44), (236, 236, 244))                                      # the towel on his shoulder
    s.line([(6, 36), (12, 36)], (180, 60, 60))
    s.ell((10, 4, 34, 28), "skin")                                                # the dome
    s.ell((12, 6, 20, 12), "skin_hi")
    s.ell((8, 12, 14, 22), "hair"); s.ell((30, 12, 36, 22), "hair")               # side fringe
    s.poly([(12, 18), (32, 18), (34, 30), (28, 40), (22, 42), (16, 40), (10, 30)], "hair")   # the beard
    s.line([(16, 24), (20, 36)], "hair_sh"); s.line([(26, 24), (24, 36)], "hair_sh")
    s.line([(15, 14), (19, 13)], "hair_sh"); s.line([(25, 13), (29, 14)], "hair_sh")          # brows
    s.pxs([(17, 16), (27, 16)], "eye")
    s.rect((20, 17, 23, 20), "skin_sh")                                           # nose
    s.line([(19, 22), (25, 22)], "hair_sh")
    if thumb:
        s.rect((34, 24, 39, 30), "skin"); s.rect((36, 19, 38, 24), "skin")        # thumbs up
        s.rect((33, 30, 40, 36), (40, 36, 44))
    return s.done()


@lru_cache(maxsize=None)
def fossil(kind):
    """Card players from the fossil record, each in a green dealer's visor."""
    if kind == "ammonite":
        s = Canvas(22, 24)
        s.ell((2, 5, 20, 23), BONE)
        for r, col_ in ((7, BONE_SH), (5, BONE), (3, BONE_SH), (1, BONE_DK)):
            s.ell((11 - r, 14 - r, 11 + r, 14 + r), col_)
        for k in range(10):
            a = k * math.pi / 5
            s.line([(11 + math.cos(a) * 5, 14 + math.sin(a) * 5), (11 + math.cos(a) * 8, 14 + math.sin(a) * 8)],
                   BONE_DK)
        s.pxs([(7, 11), (14, 11)], "eye")
        s.poly([(3, 6), (19, 6), (21, 9), (1, 9)], VISOR); s.line([(3, 6), (19, 6)], VISOR_SH)
        return s.done()
    if kind == "trilobite":
        s = Canvas(18, 26)
        s.ell((1, 4, 16, 12), BONE)
        s.ell((3, 8, 14, 25), BONE)
        s.line([(8, 9), (8, 24)], BONE_SH); s.line([(9, 9), (9, 24)], BONE_SH)
        for y in range(12, 24, 2):
            s.line([(4, y), (13, y)], BONE_DK)
        s.pxs([(5, 7), (12, 7)], "eye")
        s.poly([(2, 2), (15, 2), (17, 5), (0, 5)], VISOR); s.line([(2, 2), (15, 2)], VISOR_SH)
        return s.done()
    s = Canvas(30, 22)                                                             # a raptor skull
    s.poly([(1, 10), (8, 5), (18, 6), (29, 11), (26, 14), (12, 14), (6, 17), (1, 16)], BONE)
    s.poly([(6, 16), (22, 15), (20, 19), (8, 20)], BONE)
    s.ell((6, 7, 12, 12), BONE_DK)                                                 # the eye socket
    s.px((9, 9), "eye")
    s.ell((14, 8, 17, 11), BONE_SH)
    for x in range(10, 26, 3):
        s.px((x, 14), "tooth"); s.px((x - 1, 15), "tooth")
    s.poly([(3, 2), (16, 1), (20, 5), (1, 6)], VISOR); s.line([(3, 2), (16, 1)], VISOR_SH)
    return s.done()


@lru_cache(maxsize=None)
def card(rank, suit):
    s = Canvas(12, 16)
    s.rect((1, 1, 10, 14), "white")
    red = suit == "d"
    s.text((2, -1), rank, "red" if red else "ink")
    if red:
        s.poly([(6, 7), (9, 10), (6, 13), (3, 10)], "red")
    else:
        s.ell((4, 7, 7, 10), "ink"); s.ell((2, 9, 5, 12), "ink"); s.ell((6, 9, 9, 12), "ink")
        s.line([(5, 11), (5, 13)], "ink")
    return s.done()


@lru_cache(maxsize=None)
def card_back():
    s = Canvas(12, 16)
    s.rect((1, 1, 10, 14), (60, 80, 170))
    s.rect((3, 3, 8, 12), (90, 110, 200))
    return s.done()


@lru_cache(maxsize=None)
def chips(n, color):
    s = Canvas(10, 4 + 2 * n)
    for k in range(n):
        y = 2 + 2 * (n - 1 - k)
        s.ell((1, y, 8, y + 3), color)
        s.line([(2, y + 3), (7, y + 3)], mix(color, INK, 0.4))
    return s.done()


POKER = (72, 40, 270, 146)                      # the card room, in UI pixels (clear of Darwin's corner)
PLAYERS = [("raptor", 104, (220, 60, 60)), ("ammonite", 150, (60, 110, 220)), ("trilobite", 188, (240, 240, 240))]


def card_room(c, t_in, call, bluff):
    """The fossil record, at a poker table, calling Morgan's bluff."""
    ui = c.ui
    x0, y0, x1, y1 = POKER
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    grow = ease_out(ramp(c.t, t_in, t_in + 0.18))
    top = int(lerp(y1, y0, grow))
    d.rectangle((x0 - 1, top - 1, x1 + 1, y1 + 1), fill=INK + (255,))
    d.rectangle((x0, top, x1, y1), fill=(22, 26, 24, 255))
    if grow < 1:
        return
    lamp_x = (x0 + x1) // 2
    blend_poly(ui, [(lamp_x - 10, y0 + 8), (lamp_x + 10, y0 + 8), (x1 - 6, 114), (x0 + 6, 114)], (255, 226, 160), 0.12)
    d.line([(lamp_x, y0), (lamp_x, y0 + 4)], fill=(60, 60, 60, 255))
    d.polygon([(lamp_x - 10, y0 + 9), (lamp_x - 5, y0 + 4), (lamp_x + 5, y0 + 4), (lamp_x + 10, y0 + 9)],
              fill=VISOR_SH + (255,), outline=INK + (255,))
    d.line([(lamp_x - 6, y0 + 10), (lamp_x + 6, y0 + 10)], fill=(255, 246, 206, 255))
    # the players, and Morgan at the end of the table
    for k, (kind, x, chip) in enumerate(PLAYERS):
        spr = scaled(fossil(kind), 2)
        bob = 1 if int(c.t * 4 + k) % 2 else 0
        ui.alpha_composite(spr, (x - spr.width // 2, 114 - spr.height + 6 + bob))
    mf = bust("morgan", 2, 30, 28, -1, eyes="side" if c.t >= bluff else "half",
              brows="worried" if c.t >= bluff else "neutral", mouth="grit" if c.t >= bluff else "smirk")
    ui.alpha_composite(mf, (x1 - mf.width - 2, 114 - mf.height + 4))
    if c.t >= bluff:
        sx, sy = x1 - 46, 70 + int(c.t * 8) % 3
        d.ellipse((sx, sy, sx + 3, sy + 5), fill=C["sweat"] + (255,), outline=INK + (255,))
    d.rectangle((x0, 110, x1, y1), fill=FELT + (255,))
    d.rectangle((x0, 110, x1, 113), fill=C["wood"] + (255,))
    d.line([(x0, 113), (x1, 113)], fill=C["wood_sh"] + (255,))
    blend_poly(ui, [(x0 + 30, 118), (x1 - 30, 118), (x1 - 50, 140), (x0 + 50, 140)], FELT_HI, 0.4)
    pixel.text(ui, (x0 + 58, 135), "THE FOSSIL RECORD", SILK, C["gold"], shadow=None, anchor="ma")   # printed on the felt
    pot_x, pot_y = x0 + 86, 126
    for k, (kind, x, chip) in enumerate(PLAYERS):
        p = ease_in_out(ramp(c.t, call + 0.08 * k, call + 0.08 * k + 0.2))
        st = chips(4, chip)
        ui.alpha_composite(st, (int(lerp(x - 5, pot_x - 14 + 10 * k, p)), int(lerp(116, pot_y, p))))
    # Morgan's hand, face down until the fossils call
    flip = ramp(c.t, bluff, bluff + 0.14)
    for k, (rank, suit) in enumerate((("7", "d"), ("2", "c"))):
        spr = scaled(card(rank, suit) if flip >= 0.5 else card_back(), 2)
        if 0 < flip < 1:
            spr = spr.resize((max(1, int(spr.width * abs(1 - 2 * flip))), spr.height), Image.NEAREST)
        cx = x1 - 50 + k * 26
        ui.alpha_composite(spr, (cx - spr.width // 2, 114 + k))
    for k, (kind, x, chip) in enumerate(PLAYERS):
        if c.t >= call + 0.08 * k:
            bubble(ui, x, 62 - 8 * (k % 2), "CALL.", tail=(x, 74), fnt=SILK, line_h=8, text_dy=-2, pad=3)


@gag("v1", 9, post=0.34)                     # held into line 10, so the reveal can sit
def darwins_corner(c, L):
    c.shot = "clearing"
    dar, corner, fos, call, your = wt(L, "Darwin"), wt(L, "corner"), wt(L, "fossils"), wt(L, "call"), wt(L, "your")
    bluff = wt(L, "bluff")
    presenting(c, "point" if c.t < fos else "palm")
    t_in = fos - 0.08
    if c.t >= t_in:
        c.mood = 0.7
    yield "ui"
    if c.t >= dar:                                      # Darwin, literally in the corner of the screen
        age = c.t - dar
        img = darwin(c.t >= corner)
        name = "CORNERMAN" if c.t >= corner else "C. DARWIN"
        w = max(img.width, text_width("CORNERMAN", SILK) + 4)
        x = 8 + int((1 - back_out(ramp(age, 0, 0.25))) * -70)
        y = 38
        panel(c.ui, (x, y, x + w, y + img.height + 10), (70, 58, 50), C["gold"])
        sep = Image.new("RGBA", (w - 1, img.height), (164, 140, 108, 255))
        sep.alpha_composite(img, ((w - 1 - img.width) // 2, 0))
        c.ui.paste(sep, (x + 1, y + 1))
        pixel.text(c.ui, (x + w // 2 + 1, y + img.height + 1), name, SILK, C["gold_hi"], shadow=None, anchor="ma")
    if c.t >= t_in:
        card_room(c, t_in, call, your)
    if c.t >= bluff:
        stamp(c.ui, POKER[2] - 40, 98, "BLUFF", C["red"], angle=-8, size=16, age=c.t - bluff)


# --- 10-11: "It's natural selection every time I clear my throat," / "And you've never been selected, mate. ..."

ROSTER = [("DAVID", "david"), ("LION", "lion"), ("APE", "ape"), ("WHALE", "whale"),
          ("T-REX", "trex"), ("RAT", "rat"), ("PENGUIN", "penguin"), ("MORGAN", "morgan")]
TILE, TGAP = 36, 4
GRID_X, GRID_Y = (W - (4 * TILE + 3 * TGAP)) // 2, 60
P1_BOX, P2_BOX = (8, 60, 74, 136), (W - 74, 60, W - 8, 136)
ROULETTE = [1, 4, 2, 6, 3, 5, 1, 2, 4, 3, 6, 5]


@lru_cache(maxsize=None)
def portrait(key, big=False, grey=False):
    """A roster portrait: head and shoulders, the critters cropped to their heads."""
    from critters import gorilla, rat, trex, whale
    if key == "david":
        img = bust("david", 1, 30, 28, 1, brows="up", mouth="smile")
    elif key == "ahem":                                  # Sir David, clearing his throat
        img = bust("david", 1, 30, 28, 1, brows="up", mouth="o", eyes="shut")
    elif key == "morgan":
        img = bust("morgan", 1, 30, 28, 1, eyes="half", mouth="smirk")
    else:
        spr, box, n = {"lion": (lion(), (24, 0, 48, 26), 1), "ape": (gorilla("stand", "smug"), (1, 0, 33, 26), 1),
                       "whale": (whale(), (60, 2, 92, 30), 1), "trex": (trex(), (32, 0, 64, 26), 1),
                       "rat": (rat(), (6, 0, 22, 10), 2), "penguin": (penguin(), (0, 0, 16, 24), 1)}[key]
        img = scaled(spr.crop(box), n)
    if grey:
        a = np.array(img).astype(np.float32)
        a[..., :3] = a[..., :3].mean(axis=2, keepdims=True) * 0.7 + 30
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return scaled(img, 2) if big else img


def tile_xy(k):
    return GRID_X + (k % 4) * (TILE + TGAP), GRID_Y + (k // 4) * (TILE + TGAP)


def cobweb(ui, x, y, size, p, color=(214, 214, 224, 255)):
    """A cobweb in the top-right corner at (x, y), spun as p goes 0 -> 1."""
    d = ImageDraw.Draw(ui)
    if p <= 0:
        return
    spokes = [(x - size, y), (x - size * 0.8, y + size * 0.55), (x - size * 0.45, y + size * 0.9), (x, y + size)]
    for sx, sy in spokes:
        d.line([(x, y), (lerp(x, sx, p), lerp(y, sy, p))], fill=color)
    for r in (0.35, 0.65, 0.95):
        if p > r:
            pts = [(lerp(x, sx, r), lerp(y, sy, r)) for sx, sy in spokes]
            d.line(pts, fill=color)


def spider(ui, x, y, t):
    d = ImageDraw.Draw(ui)
    d.line([(x, y - 30), (x, y)], fill=(214, 214, 224, 255))
    for k in (-1, 1):
        for j in range(3):
            wig = int(t * 8 + j) % 2
            d.line([(x, y + j), (x + k * 3, y + j - 1 + wig), (x + k * 4, y + j + 1)], fill=INK + (255,))
    d.ellipse((x - 2, y - 1, x + 2, y + 4), fill=INK + (255,))


def select_screen(c, nat, sel, hover, chosen=None, chosen_t=0.0, grey=None, web=0.0, zero_t=None, spider_t=None,
                  ahem=False):
    ui = c.ui
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    d.rectangle((0, 0, W, H), fill=(16, 18, 42, 255))
    off = int(c.t * 24) % 16
    for x in range(-H, W + 16, 16):
        d.line([(x + off, H), (x + off + H, 0)], fill=(22, 26, 58, 255), width=5)
    # the title
    full = text_width("NATURAL SELECTION", PRESS16)
    tx = W // 2 - full // 2
    if c.t >= nat:
        pop_text(ui, tx, 32, "NATURAL", c.t - nat, anchor="la", top=C["gold_hi"], bottom=(240, 130, 40))
        pop_text(ui, tx + text_width("NATURAL ", PRESS16), 32, "SELECTION", c.t - sel, anchor="la",
                 top=C["gold_hi"], bottom=(240, 130, 40))
    # the roster
    for k, (name, key) in enumerate(ROSTER):
        x, y = tile_xy(k)
        is_grey = grey is not None and k == 7 and c.t >= grey
        d.rectangle((x - 1, y - 1, x + TILE, y + TILE), fill=INK + (255,))
        d.rectangle((x, y, x + TILE - 1, y + TILE - 1), fill=((46, 46, 52) if is_grey else (40, 52, 120)) + (255,))
        img = portrait(key, grey=is_grey)
        ui.alpha_composite(img, (x + (TILE - img.width) // 2, y + TILE - 8 - img.height))
        d.rectangle((x, y + TILE - 8, x + TILE - 1, y + TILE - 1), fill=(0, 0, 0, 255))
        pixel.text(ui, (x + TILE // 2, y + TILE - 9), name, SILK, (120, 120, 120) if is_grey else C["text"],
                   shadow=None, anchor="ma")
        if is_grey:
            cobweb(ui, x + TILE - 2, y + 1, 20, web)
    if spider_t is not None and c.t >= spider_t:
        x, y = tile_xy(7)
        spider(ui, x + 24, int(y + lerp(-6, 14, ease_out(ramp(c.t, spider_t, spider_t + 0.3)))), c.t)
    if hover is not None:
        x, y = tile_xy(hover)
        locked = chosen is not None and c.t >= chosen_t
        colr = (C["gold_hi"] if int(c.t * 10) % 2 else C["gold"]) if locked else C["red_hi"]
        d.rectangle((x - 3, y - 3, x + TILE + 2, y + TILE + 2), outline=colr + (255,), width=2)
        pixel.text(ui, (x - 2, y - 11), "1P", SILK, colr, shadow=INK)
    # the players' panels
    panel(ui, P1_BOX, (48, 18, 28), C["red_hi"])
    pixel.text(ui, (P1_BOX[0] + 3, P1_BOX[1] + 1), "1P", SILK, C["red_hi"], shadow=None)
    cx1 = (P1_BOX[0] + P1_BOX[2]) // 2 + 1
    picked = chosen is not None and c.t >= chosen_t
    if hover is not None:
        name, key = ROSTER[hover]
        big = portrait("ahem" if ahem else key, True)
        ui.alpha_composite(big, (cx1 - big.width // 2, P1_BOX[3] - 12 - big.height))
        if not picked:
            pixel.text(ui, (cx1, P1_BOX[3] - 10), name, PRESS, C["text"], shadow=INK, anchor="ma")
    if ahem:
        label(ui, (P1_BOX[2] - 2, P1_BOX[1] + 3), "AHEM.", fnt=SILK, anchor="ra")
    if picked:
        if c.t - chosen_t < 0.08:
            d.rectangle(P1_BOX, fill=(255, 255, 255, 255))
        gold = C["gold_hi"] if int(c.t * 6) % 2 == 0 or c.t - chosen_t > 0.8 else C["gold"]
        label(ui, (cx1, P1_BOX[3] - 11), "SELECTED!", fnt=SILK, bg=gold, fg=INK, anchor="ma")
    panel(ui, P2_BOX, (18, 24, 54), (90, 140, 255))
    pixel.text(ui, (P2_BOX[0] + 3, P2_BOX[1] + 1), "2P", SILK, (90, 140, 255), shadow=None)
    if zero_t is not None and c.t >= zero_t:
        big = portrait("morgan", True, grey=True)
        ui.alpha_composite(big, ((P2_BOX[0] + P2_BOX[2]) // 2 - big.width // 2 + 1, P2_BOX[3] - 22 - big.height))
        cobweb(ui, P2_BOX[2] - 2, P2_BOX[1] + 2, 26, ramp(c.t, zero_t, zero_t + 0.3))
        pixel.text(ui, ((P2_BOX[0] + P2_BOX[2]) // 2 + 1, P2_BOX[3] - 20), "TIMES", SILK, (150, 150, 160),
                   shadow=None, anchor="ma")
        pixel.text(ui, ((P2_BOX[0] + P2_BOX[2]) // 2 + 1, P2_BOX[3] - 12), "PICKED: 0", SILK, C["red_hi"],
                   shadow=None, anchor="ma")
    elif int(c.t * 2.5) % 2 == 0:
        pixel.text(ui, ((P2_BOX[0] + P2_BOX[2]) // 2 + 1, 92), "PRESS", PRESS, C["text"], shadow=INK, anchor="ma")
        pixel.text(ui, ((P2_BOX[0] + P2_BOX[2]) // 2 + 1, 102), "START", PRESS, C["text"], shadow=INK, anchor="ma")


@gag("v1", 10)
def natural_selection(c, L):
    c.shot = "wide"
    nat, sel, every = wt(L, "natural"), wt(L, "selection"), wt(L, "every")
    clear, throat = wt(L, "clear"), wt(L, "throat")
    if c.t < nat - 0.08:                                # the fossils' reveal is still on screen
        return
    yield "ui"
    if c.t < every:
        hover = 1
    elif c.t < clear:                                   # the roulette, never once stopping on Morgan
        hover = ROULETTE[int((c.t - every) / 0.08) % len(ROULETTE)]
    else:
        hover = 0
    select_screen(c, nat, sel, hover, chosen=0, chosen_t=throat, ahem=clear <= c.t < throat + 0.15)


PROMPT = ["[DEEP VOICE]", "\"MMM.\"", "[WISE PAUSE]", "\"AND THAT'S", "WHEN I KNEW.\"", "[SMILE,", "SAGELY]",
          "[END OF", "PERSONALITY]"]
PROMPTER = (226, 44, 312, 112)


def prompter(ui, t, t0, t1, hot):
    x0, y0, x1, y1 = PROMPTER
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    mid = (x0 + x1) // 2
    d.rectangle((mid - 2, y1, mid + 2, 146), fill=(40, 40, 46, 255), outline=INK + (255,))       # the stand
    d.rectangle((mid - 14, 142, mid + 14, 146), fill=(40, 40, 46, 255), outline=INK + (255,))
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK + (255,))
    d.rectangle((x0, y0, x1, y1), fill=(70, 70, 78, 255))
    sx0, sy0, sx1, sy1 = x0 + 4, y0 + 4, x1 - 4, y1 - 4
    screen = Image.new("RGBA", (sx1 - sx0, sy1 - sy0), (6, 6, 8, 255))
    read_y = (sy1 - sy0) // 2
    n = len(PROMPT) - 1
    p = n * ease_in_out(ramp(t, t0, t1)) if t < t1 else n
    for i, row in enumerate(PROMPT):
        y = read_y + int(round((i - p) * 9)) - 3
        if -8 < y < screen.height:
            colr = C["red_hi"] if i >= n - 1 and t >= hot else (236, 236, 236) if abs(i - p) < 0.6 else (130, 130, 136)
            pixel.text(screen, (screen.width // 2, y), row, SILK, colr, shadow=None, anchor="ma")
    ImageDraw.Draw(screen).polygon([(0, read_y - 3), (3, read_y), (0, read_y + 3)], fill=C["tele"] + (255,))
    ui.paste(screen, (sx0, sy0))


@gag("v1", 11)
def never_selected(c, L):
    never, sel, mate, you = wt(L, "never"), wt(L, "selected"), wt(L, "mate"), wt(L, "^You$")
    wrote = wt(L, "wrote")
    if c.t < you:
        c.shot = "wide"
        c.inset = False                                 # the roster is his reaction
    else:                                               # meanwhile, in the booth: Morgan reads his lines
        c.shot = "booth"
        c.st["david"]["hidden"] = True
        m = c.st["morgan"]
        m.update(eyes="side", brows="up", gesture=False, arm="hold")
        if c.t < wrote + 0.05:
            m["mouth"] = "open" if int(c.t * 9) % 2 else "o"
    yield "ui"
    if c.t < you:
        select_screen(c, -1, -1, 0, chosen=0, chosen_t=-1, grey=never, web=ramp(c.t, never, never + 0.35),
                      zero_t=sel, spider_t=mate)
    else:
        prompter(c.ui, c.t, you + 0.05, wrote, wrote)


# --- 12-13: "A lyrebird can mimic chainsaws, camera shutters, car alarms." / "I heard one do your voice once. ..."

LY = {"sky": (70, 96, 84), "sky2": (122, 142, 114), "far": (100, 122, 104), "trunk": (206, 200, 186),
      "trunk_sh": (164, 156, 140), "trunk_hi": (232, 228, 214), "litter": (104, 78, 56), "litter_sh": (82, 60, 44),
      "litter_hi": (138, 104, 70), "mound": (122, 92, 64)}
LYB = {"body": (122, 88, 62), "body_sh": (96, 68, 50), "belly": (156, 124, 92), "plume_sh": (176, 180, 194),
       "lyre": (130, 88, 58), "lyre_hi": (236, 206, 150), "leg": (70, 58, 50), "beak": (64, 60, 62)}
LY_GROUND = 140
BIRD_AT = (200, 151)                                    # the lyrebird's feet, on its display mound
HIDE_AT = (118, 158)                                    # Sir David, crouched in the leaf litter
MMM = (120, 80, 150)                                    # the colour of a deep voice


@lru_cache(maxsize=1)
def lyre_static():
    img = Image.new("RGB", (W, H), LY["sky"])
    vgrad(img, (0, 0, W, LY_GROUND), LY["sky"], LY["sky2"], steps=6)
    d = ImageDraw.Draw(img)
    for k in range(9):                                            # far trunks in the mist
        x = 12 + k * 37 + int(rnd("far", k) * 14)
        d.rectangle((x, 0, x + 4 + int(rnd("far-w", k) * 4), LY_GROUND), fill=LY["far"])
    for x, h in ((74, 58), (148, 72), (284, 50)):                 # tree ferns
        d.rectangle((x - 1, LY_GROUND - h, x + 1, LY_GROUND), fill=(58, 48, 40))
        for k in range(7):
            frond(d, x, LY_GROUND - h, 26, math.pi * (0.08 + 0.84 * k / 6), C["leaf_sh"] if k % 2 else C["leaf"],
                  width=3)
    for x, w in ((20, 18), (246, 22), (306, 14)):                 # the big pale eucalypts
        d.rectangle((x, 0, x + w, LY_GROUND + 6), fill=LY["trunk"])
        d.rectangle((x + w - 4, 0, x + w, LY_GROUND + 6), fill=LY["trunk_sh"])
        for k in range(6):
            y = int(rnd("bark", x, k) * LY_GROUND)
            d.ellipse((x + 3, y, x + 9, y + 14), fill=LY["trunk_sh"])
        d.line([(x + 2, 0), (x + 2, LY_GROUND)], fill=LY["trunk_hi"])
    d.rectangle((0, LY_GROUND, W, H), fill=LY["litter"])
    for k in range(260):
        x, y = rnd("lit", k) * W, LY_GROUND + rnd("lit-y", k) * (H - LY_GROUND)
        d.line([(x, y), (x + 2, y)], fill=LY["litter_hi"] if k % 3 == 0 else LY["litter_sh"])
    bx, by = BIRD_AT
    d.ellipse((bx - 28, by - 5, bx + 28, by + 5), fill=LY["mound"])
    d.line([(bx - 20, by - 4), (bx + 20, by - 4)], fill=LY["litter_hi"])
    return img


def lyre(c):
    img = lyre_static().copy()
    for k, x in enumerate((96, 180)):                             # light coming down through the canopy
        s = 0.07 + 0.03 * math.sin(c.t * 0.9 + k)
        blend_poly(img, [(x, 0), (x + 22, 0), (x + 60, LY_GROUND + 20), (x + 26, LY_GROUND + 20)], (255, 248, 214), s)
    return img


def lyre_near(c):
    from sets import foreground_ferns
    foreground_ferns(c.world, c.t)


scene("v1_lyre", near=lyre_near,
      shots={"two": (160, 128, 12), "bird": (196, 126, 18), "david": (132, 134, 18)},
      cast={"david": dict(x=HIDE_AT[0], y=HIDE_AT[1], facing=1, body="crouch", mic="fluffy", z=1)})(lyre)


@lru_cache(maxsize=None)
def lyrebird(frame=0, beak=False, phones=False):
    """A superb lyrebird mid-display, facing left: the silver plumes thrown up over its back in a fan,
    framed by the two banded lyre feathers."""
    t = Canvas(58, 50)                                  # the tail: fine lines, no outline
    bx, by = 40, 34                                     # the rump, where the tail springs from
    n = 17
    for i in range(n):
        a = math.radians(26 + i * (130 / (n - 1)))
        r = 32 + (i % 2) * 2
        sway = math.sin(frame * 1.7 + i) * 1.2
        mx, my = bx + math.cos(a) * r * 0.55, by - math.sin(a) * r * 0.6 - 3
        tx, ty = bx + math.cos(a) * r + sway, by - math.sin(a) * r * 0.9
        t.line([(bx, by), (mx, my), (tx, ty)], "white" if i % 2 else LYB["plume_sh"])
    for a0, side in ((30, 1), (152, -1)):               # the lyre feathers, curling out at the tips
        a = math.radians(a0)
        pts = [(bx, by)]
        for k in range(1, 6):
            p = k / 5
            aa = a + side * 0.25 * math.sin(p * math.pi)
            pts.append((bx + math.cos(aa) * 34 * p, by - math.sin(aa) * 34 * p * 0.95))
        pts.append((pts[-1][0] + side * 4, pts[-1][1] + 1))
        t.line(pts, LYB["lyre"], w=2)
        for k in (2, 3, 4):
            t.px((int(pts[k][0]), int(pts[k][1])), LYB["lyre_hi"])
    s = Canvas(58, 50)
    s.ell((17, 27, 43, 41), LYB["body"])
    s.ell((19, 33, 36, 41), LYB["belly"])
    s.ell((25, 28, 40, 35), LYB["body_sh"])
    s.ell((11, 23, 21, 33), LYB["body"])                # neck
    s.ell((6, 18, 15, 27), LYB["body"])                 # head
    s.poly([(2, 22), (7, 21), (7, 24)], LYB["beak"])
    if beak:
        s.poly([(2, 25), (7, 23), (7, 25)], LYB["beak"])
    s.px((9, 21), "eye")
    s.line([(25, 40), (24, 48)], LYB["leg"]); s.line([(30, 40), (31, 48)], LYB["leg"])
    s.line([(21, 48), (25, 48)], LYB["leg"]); s.line([(29, 48), (33, 48)], LYB["leg"])
    if phones:                                          # borrowed from the booth
        s.line([(7, 20), (9, 16), (13, 16), (15, 19)], "ink")
        s.rect((12, 20, 14, 24), "mic")
    img = t.done(outline=None)
    img.alpha_composite(s.done())
    return img


BEAK = (3, 23)                                          # in the sprite


def draw_lyrebird(c, singing=False, phones=False):
    bx, by = BIRD_AT
    spr = lyrebird(int(c.t * 5) % 4, singing and int(c.t * 10) % 2 == 0, phones)
    c.world.paste(spr, (bx - 29, by - 49), spr)
    return bx - 29 + BEAK[0], by - 49 + BEAK[1]


@lru_cache(maxsize=None)
def sound_icon(kind):
    if kind == "chainsaw":
        s = Canvas(19, 10)
        s.rect((8, 4, 17, 6), (156, 156, 166))
        for x in range(9, 18, 2):
            s.px((x, 3), (90, 90, 100)); s.px((x, 7), (90, 90, 100))
        s.rect((1, 2, 8, 8), (240, 130, 30))
        s.line([(2, 1), (6, 1)], (60, 60, 60))
        return s.done()
    if kind == "camera":
        s = Canvas(15, 11)
        s.rect((1, 3, 13, 9), (40, 40, 46))
        s.rect((3, 1, 6, 3), (40, 40, 46))
        s.ell((5, 4, 9, 8), (140, 140, 150))
        s.px((7, 6), (20, 20, 24)); s.px((11, 4), "white")
        return s.done()
    s = Canvas(20, 11)                                  # a car, alarm blaring
    s.rect((1, 5, 18, 8), (220, 50, 50))
    s.poly([(5, 5), (7, 2), (13, 2), (15, 5)], (220, 50, 50))
    s.rect((8, 3, 12, 4), (160, 200, 230))
    s.ell((3, 7, 6, 10), (30, 30, 34)); s.ell((13, 7, 16, 10), (30, 30, 34))
    return s.done()


def sound_bubble(ui, x, y, kind, s, tail, age):
    """A speech bubble holding a picture of the noise, then the noise. Returns the icon's top-left."""
    if age < 0:
        return None
    k = back_out(ramp(age, 0, 0.14))
    box = bubble(ui, x, y + int((1 - k) * 6), "     " + s, tail=tail, fnt=SILK, line_h=8, text_dy=-2, pad=3)
    ic = sound_icon(kind)
    at = (box[0] + 3, box[1] + (box[3] - box[1] - ic.height) // 2)
    ui.alpha_composite(ic, at)
    return at


@gag("v1", 12)
def lyrebird_mimic(c, L):
    c.set_scene("v1_lyre")
    bird, chain, cam, car = wt(L, "lyrebird"), wt(L, "chainsaws"), wt(L, "camera"), wt(L, "car")
    c.shot = "david" if c.t < bird else "two"
    s = c.st["david"]
    s.update(arm="whisper", gesture=False, brows="up", eyes="side" if c.t >= chain else "open")
    yield "back"
    beak = draw_lyrebird(c, singing=c.t >= chain)
    yield "ui"
    CH.lower_third(c.ui, c.t - bird, "SUPERB LYREBIRD", "MENURA NOVAEHOLLANDIAE", y=36, out_at=chain - bird - 0.3)
    bx, by = ui_at(c, *beak)
    for k, (t0, kind, s_, x) in enumerate(((chain, "chainsaw", "BRRRM!", 92), (cam, "camera", "KA-CHIK!", 160),
                                            (car, "car", "WEE-OO!", 234))):
        if c.t >= t0:
            hot = k == 2 or c.t < (cam, car)[k]
            at = sound_bubble(c.ui, x, 58, kind, s_, (bx - 2, by - 4) if hot else None, c.t - t0)
            if kind == "car" and at and int(c.t * 8) % 2:          # the alarm's flashing lamp
                ImageDraw.Draw(c.ui).rectangle((at[0] + 9, at[1] - 2, at[0] + 11, at[1] + 1),
                                               fill=(255, 220, 60, 255), outline=INK + (255,))


@gag("v1", 13)
def more_charm(c, L):
    c.set_scene("v1_lyre")
    do, voice, honest = wt(L, "do"), wt(L, "voice"), wt(L, "Honestly")
    more, charm = wt(L, "more"), wt(L, "charm")
    c.shot = "bird" if do <= c.t < honest else "two"
    s = c.st["david"]
    s.update(arm="whisper", gesture=False, brows="up")
    if c.t >= honest:
        s.update(eyes="side", mouth="smirk" if s["mouth"] == "closed" else s["mouth"])
    phones = c.t >= wt(L, "your")
    yield "back"
    beak = draw_lyrebird(c, singing=voice <= c.t < honest, phones=phones)
    yield "front"
    if c.t >= charm:                                    # preening
        bx, by = BIRD_AT
        for k in range(5):
            if int(c.t * 6 + k) % 3 == 0:
                sparkle(c.world, bx - 10 + int(rnd("sp", k) * 40), by - 44 + int(rnd("sp-y", k) * 30), 2,
                        (255, 250, 220))
    yield "ui"
    if voice <= c.t < honest:                           # the impression
        bx, by = ui_at(c, *beak)
        age = c.t - voice
        k = back_out(ramp(age, 0, 0.14))
        box = bubble(c.ui, bx - 26, by - 18 + int((1 - k) * 6), "MMMM.", tail=(bx - 2, by - 2), fnt=PRESS16,
                     ink=INK, pad=5, line_h=16)
        for j in range(3):                              # the notes sink, they're that low
            nx = box[2] + 4 + j * 8
            ny = box[1] + 4 + int((age * 30 + j * 7) % 20)
            ImageDraw.Draw(c.ui).ellipse((nx, ny, nx + 3, ny + 2), fill=MMM + (255,))
            ImageDraw.Draw(c.ui).line([(nx + 3, ny + 1), (nx + 3, ny - 5)], fill=MMM + (255,))
    if c.t >= honest:                                   # the charm meter
        x0, y0, x1, y1 = 12, 34, 150, 76
        age = c.t - honest
        if age < 0.12:
            y1 = int(lerp(y0, y1, age / 0.12))
        panel(c.ui, (x0, y0, x1, y1), (20, 16, 26), C["gold"])
        if age >= 0.12:
            pixel.text(c.ui, (x0 + 4, y0 + 3), "CHARM", PRESS, C["gold_hi"], shadow=None)
            rows = (("FREEMAN", 0.28 * ease_out(ramp(c.t, honest + 0.1, honest + 0.5)), (150, 150, 170)),
                    ("LYREBIRD", 1.3 * ease_in(ramp(c.t, more - 0.1, charm)), C["gold_hi"]))
            d = ImageDraw.Draw(c.ui)
            for k, (name, fill, colr) in enumerate(rows):
                y = y0 + 16 + k * 12
                pixel.text(c.ui, (x0 + 4, y - 1), name, SILK, C["text"], shadow=None)
                bx0, bx1 = x0 + 50, x1 - 6
                d.rectangle((bx0, y, bx1, y + 6), fill=(50, 44, 60, 255), outline=INK + (255,))
                if fill > 0:
                    end = int(bx0 + 1 + (bx1 - bx0 - 2) * fill)
                    d.rectangle((bx0 + 1, y + 1, end, y + 5), fill=colr + (255,), outline=INK + (255,)
                                if end > bx1 else None)
            if c.t >= charm:                            # off the scale
                pop_text(c.ui, x1 + 26, y0 + 20, "MAX!", c.t - charm, fnt=PRESS16, top=C["gold_hi"],
                         bottom=(240, 130, 40), anchor="la")


# --- 14-15: "You did one flick with penguins, now you're struttin' on my floe?" / "Them emperors waddle ..." -

FL = {"sky": (112, 142, 196), "sky2": (240, 200, 196), "sun": (255, 240, 214), "berg": (214, 230, 244),
      "berg_sh": (160, 186, 214), "sea": (34, 64, 104), "sea_hi": (76, 116, 156), "sea_dk": (24, 44, 76),
      "ice": (240, 246, 252), "ice_sh": (176, 204, 228), "ice_dk": (120, 160, 196)}
FL_HORIZON = 100
FLOE_Y = 136                                            # where feet stand on the floe
FLAG_AT = (192, FLOE_Y + 1)                             # planted right in front of him
COLONY = [(56, 1, 0), (74, -1, -5), (98, 1, 1), (150, -1, -4), (168, 1, 2), (212, -1, -3), (236, 1, 1),
          (262, -1, -2)]


@lru_cache(maxsize=1)
def floe_static():
    img = Image.new("RGB", (W, H), FL["sky"])
    vgrad(img, (0, 0, W, FL_HORIZON), FL["sky"], FL["sky2"], steps=6)
    d = ImageDraw.Draw(img)
    d.ellipse((58, 84, 90, 116), fill=FL["sun"])
    d.rectangle((0, FL_HORIZON, W, H), fill=FL["sea"])
    for x0, w, h in ((-10, 70, 14), (80, 40, 8), (190, 90, 18), (292, 50, 10)):   # bergs on the horizon
        d.polygon([(x0, FL_HORIZON), (x0 + 8, FL_HORIZON - h), (x0 + w - 12, FL_HORIZON - h + 2),
                   (x0 + w, FL_HORIZON)], fill=FL["berg"])
        d.line([(x0 + w - 12, FL_HORIZON - h + 2), (x0 + w, FL_HORIZON)], fill=FL["berg_sh"], width=2)
    top = [(30, 134), (52, 127), (120, 124), (200, 124), (270, 127), (294, 134)]
    front = [(294, 134), (290, 144), (240, 147), (120, 147), (44, 146), (30, 134)]
    d.polygon(top + front[1:], fill=FL["ice"])
    d.polygon([(30, 134), (294, 134), (290, 144), (240, 147), (120, 147), (44, 146)], fill=FL["ice_sh"])
    d.polygon(top + [(294, 134), (30, 134)], fill=FL["ice"])
    d.line([(44, 146), (120, 147), (240, 147), (290, 144)], fill=FL["ice_dk"])
    for k in range(12):                                            # scuffs in the snow
        x = 50 + rnd("scuff", k) * 220
        d.line([(x, 129 + (k % 4)), (x + 4, 129 + (k % 4))], fill=FL["ice_sh"])
    d.polygon([(40, 147), (290, 145), (300, 150), (30, 151)], fill=FL["sea_dk"])   # its shadow in the water
    return img


def floe(c):
    img = floe_static().copy()
    d = ImageDraw.Draw(img)
    for k in range(26):                                            # glints on the swell
        x = (rnd("glint", k) * W + c.t * (6 + 4 * (k % 3))) % W
        y = FL_HORIZON + 4 + rnd("glint-y", k) * (H - FL_HORIZON - 6)
        if 144 < y < 152 and 30 < x < 296:
            continue
        d.line([(x, y), (x + 3 + k % 4, y)], fill=FL["sea_hi"])
    return img


def floe_near(c):
    d = ImageDraw.Draw(c.world)
    for k in range(40):                                            # a thin snow
        x = (rnd("snow", k) * (W + 40) + c.t * 12 + math.sin(c.t + k) * 4) % (W + 40) - 20
        y = (rnd("snow-y", k) * H + c.t * (18 + 10 * (k % 3))) % H
        d.point((x, y), fill=(250, 252, 255))


scene("v1_floe", near=floe_near, shots={"floe": (160, 110, 9), "colony": (150, 112, 12)},
      cast={"morgan": dict(x=128, y=FLOE_Y, facing=1, outfit="tux", hat="none")})(floe)


@lru_cache(maxsize=None)
def flag():
    w = text_width("SIR DAVID'S", SILK) + 10
    s = Canvas(w + 6, 46)
    s.rect((2, 2, 3, 45), (120, 110, 100))
    s.rect((4, 3, w + 4, 21), "white")
    s.rect((4, 3, w + 4, 4), "red"); s.rect((4, 20, w + 4, 21), "red")
    s.text((w // 2 + 5, 4), "SIR DAVID'S", "ink", anchor="ma")
    s.text((w // 2 + 5, 11), "KEEP OFF!", "red", anchor="ma")
    return s.done()


def plant_flag(c, t0):
    """The flag drops out of the sky and into the ice with a jolt."""
    if c.t < t0 - 0.12:
        return
    fx_, fy = FLAG_AT
    drop = ease_in(ramp(c.t, t0 - 0.12, t0))
    f = flag()
    c.world.paste(f, (fx_ - 3, int(lerp(fy - 120, fy, drop)) - f.height + 2), f)
    if c.t >= t0:
        d = ImageDraw.Draw(c.world)
        for k in range(4):                                         # cracks in the ice
            a = math.pi * (0.1 + 0.27 * k)
            L_ = 5 + 4 * ramp(c.t, t0, t0 + 0.1)
            d.line([(fx_, fy), (fx_ + math.cos(a) * L_ * 1.6, fy - math.sin(a) * L_ * 0.4 + 1)], fill=FL["ice_dk"])
        if c.t - t0 < 0.2:
            c.add_shake(5 * (1 - (c.t - t0) / 0.2))
            puff(c.world, fx_, fy, c.t - t0, size=0.5, seed=3, color=(250, 252, 255), drift=(0, -6), life=0.5)


def penguin_at(img, x, y, facing, frame, tux=False, slide=False):
    spr = penguin(frame, tux)
    if slide:                                                      # tobogganing, on its belly
        spr = spr.rotate(-90, expand=True)
    if facing < 0:
        spr = mirror(spr)
    img.paste(spr, (int(x - spr.width // 2), int(y - spr.height + 1)), spr)


@gag("v1", 14)
def my_floe(c, L):
    c.set_scene("v1_floe")
    flick, strut, floe_t = wt(L, "flick"), wt(L, "struttin"), wt(L, "floe")
    m = c.st["morgan"]
    m.update(gesture=False, brows="up", eyes="half")
    mx = 118 + 60 * ease_in_out(ramp(c.t, strut, floe_t - 0.1))
    m["x"] = mx
    if strut <= c.t < floe_t - 0.1:                                # chest out, shoulders back
        m.update(body="walk1" if int(c.t * 6) % 2 else "walk2", arm="hip", lean=-1, mouth="smirk")
    else:
        m.update(arm="hip" if c.t >= strut else "cross", mouth="smirk")
    if c.t >= floe_t:
        m.update(eyes="wide", brows="worried")
    c.shot = "floe" if c.t < strut or c.t >= wt(L, "my") else (int(clamp(mx, 110, 200)), 112, 12)
    yield "back"
    for k, (x, facing, dy) in sorted(enumerate(COLONY), key=lambda kv: kv[1][2]):
        if c.t >= strut and abs(x - mx) < 70:                      # everyone turns to watch him go by
            facing = 1 if mx > x else -1
        penguin_at(c.world, x, FLOE_Y + dy, facing, int(c.t * 2 + k) % 5 == 0, tux=c.t >= flick)
    yield "front"
    plant_flag(c, floe_t)
    yield "ui"
    CH.lower_third(c.ui, c.t - flick, "PENGUIN FILMS MADE", "FREEMAN: 1.  SIR DAVID: ALL OF THEM.", y=36,
                   out_at=wt(L, "my") - flick - 0.3)


def march_x(k, t, t0, out):
    """Penguin k of the procession: waddles in from the left, then drops to its belly and slides off."""
    x = 116 - k * 27 + (min(t, out) - t0) * 44
    if t > out:
        x += (t - out) * 320
    return x


@gag("v1", 15)
def seventy_miles(c, L):
    c.set_scene("v1_floe")
    c.shot = "floe"
    emp, sev, outp, flow = wt(L, "emperors"), wt(L, "seventy"), wt(L, "outpace"), wt(L, "flow")
    m = c.st["morgan"]
    walk = ramp(c.t, L.t0, flow)
    m.update(x=140 + 14 * walk, gesture=False, arm="down", brows="worried", mouth="o", lean=1,
             body=("walk1" if int(c.t * 2.5) % 2 else "walk2") if c.t < flow else "stand")
    m["sweat"] = c.t >= sev
    yield "back"
    plant_flag(c, L.t0 - 1)
    for k in range(6):
        x = march_x(k, c.t, L.t0 - 0.15, outp + 0.04 * k)
        if -20 < x < W + 20:
            sliding = c.t > outp + 0.04 * k
            penguin_at(c.world, x, FLOE_Y + (4 if sliding else 0), 1, int(c.t * 7 + k) % 2, slide=sliding)
            if sliding:
                puff(c.world, x - 12, FLOE_Y, (c.t - outp) % 0.4, size=0.3, seed=k, color=(250, 252, 255),
                     drift=(-10, -4), life=0.4)
    yield "ui"
    if c.t < emp - 0.1:
        return
    x0, y0, x1, y1 = 34, 34, 236, 70
    panel(c.ui, (x0, y0, x1, y1), (14, 18, 34), C["text"])
    d = ImageDraw.Draw(c.ui)
    pixel.text(c.ui, (x0 + 4, y0 + 1), "THE MARCH: 70 MILES", SILK, C["tele"], shadow=None)
    tx0, tx1 = x0 + 52, x1 - 46
    for k in range(7):                                             # a chequered finish line
        for j in range(2):
            if (k + j) % 2 == 0:
                d.rectangle((tx1 + 2 + j * 2, y0 + 12 + k * 3, tx1 + 3 + j * 2, y0 + 14 + k * 3),
                            fill=(255, 255, 255, 255))
    pen = 70 * ease_in_out(ramp(c.t, emp, outp))
    mor = 0.2 * ramp(c.t, emp, flow)
    for k, (name, miles, colr, fmt) in enumerate((("EMPERORS", pen, (236, 236, 240), "{:.0f} MI"),
                                                   ("FREEMAN", mor, C["red_hi"], "{:.1f} MI"))):
        y = y0 + 17 + k * 11
        pixel.text(c.ui, (x0 + 4, y - 4), name, SILK, colr, shadow=None)
        d.rectangle((tx0, y - 1, tx1, y), fill=(60, 66, 90, 255))
        px_ = int(tx0 + (tx1 - tx0) * miles / 70)
        d.rectangle((tx0, y - 1, px_, y), fill=colr + (255,))
        d.rectangle((px_ - 2, y - 3, px_ + 2, y + 2), fill=colr + (255,), outline=INK + (255,))
        pixel.text(c.ui, (x1 - 3, y - 4), fmt.format(miles), SILK, colr, shadow=None, anchor="ra")


# --- 16-17: "Got a voice like a church organ, big and warm and low," / "But this booth's a morgue now, ..." -----

CHAPEL = (208, 98, 9)                                   # the whole booth, roof sign and all
CHAPEL_LOW = (208, 106, 9)                              # ...after the camera sinks on "low"
LOW16 = line_t("v1", 16, "low")
PIPE, PIPE_HI, PIPE_SH, PIPE_DK = (214, 184, 110), (248, 228, 164), (160, 128, 70), (70, 52, 30)
GLASS = [(214, 50, 60), (60, 90, 200), (240, 190, 60), (60, 160, 90)]
STEEL, STEEL_SH, STEEL_HI = (168, 176, 186), (118, 126, 138), (214, 220, 228)
COLD = (190, 236, 244)


def organ_pipes(img, rise, big=0.0):
    """Organ pipes up behind the booth, tallest in the middle; `rise` 0-1 brings them up from the
    ground, `big` stretches them further."""
    d = ImageDraw.Draw(img)
    floor = BOOTH_FLOOR + 3
    for i, x in enumerate(range(144, 274, 7)):
        dist = abs(x + 2 - BOOTH_CX) / 66
        full = (118 - 52 * dist) * (1 + 0.3 * big)
        r = ease_out(clamp(rise * 1.6 - dist * 0.6, 0, 1))
        if r <= 0:
            continue
        top = floor - full * r
        behind = BX0 - 5 < x < BX1 + 1
        bottom = BY0 - 12 if behind else floor
        if top >= bottom:
            continue
        d.rectangle((x, top, x + 4, bottom), fill=PIPE)
        d.line([(x + 1, top + 1), (x + 1, bottom)], fill=PIPE_HI)
        d.line([(x + 4, top), (x + 4, bottom)], fill=PIPE_SH)
        d.rectangle((x - 1, top - 1, x + 5, top), fill=PIPE_SH)
        if not behind and bottom - top > 26:                         # the pipe's mouth
            my = bottom - 16
            d.polygon([(x, my), (x + 4, my), (x + 3, my + 3), (x + 1, my + 3)], fill=PIPE_DK)


def rose_window(img, cx, cy, r, p):
    """A round stained-glass window on the booth's back wall, fading in by p."""
    if p <= 0:
        return
    win = Image.new("RGB", (2 * r + 3, 2 * r + 3), (0, 0, 0))
    d = ImageDraw.Draw(win)
    d.ellipse((0, 0, 2 * r + 2, 2 * r + 2), fill=INK)
    for k in range(8):
        d.pieslice((1, 1, 2 * r + 1, 2 * r + 1), k * 45, k * 45 + 45, fill=GLASS[k % 4], outline=INK)
    d.ellipse((r - 3, r - 3, r + 5, r + 5), fill=C["gold_hi"], outline=INK)
    m = Image.new("L", win.size, 0)
    ImageDraw.Draw(m).ellipse((0, 0, 2 * r + 2, 2 * r + 2), fill=int(255 * clamp(p, 0, 1)))
    img.paste(win, (cx - r - 1, cy - r - 1), m)


@gag("v1", 16, post=0.4)                      # held into line 17, so "LOW" gets its tick
def church_organ(c, L):
    c.shot = CHAPEL
    c.st["david"]["hidden"] = True
    voice = wt(L, "voice")
    church, organ, big, warm, low = wt(L, "church"), wt(L, "organ"), wt(L, "big"), wt(L, "warm"), wt(L, "low")
    if c.t >= low:                                      # the camera sinks with the note
        c.shot = (CHAPEL[0], CHAPEL[1] + int((CHAPEL_LOW[1] - CHAPEL[1]) * ease_out(ramp(c.t, low, low + 0.2))),
                  CHAPEL[2])
    m = c.st["morgan"]
    if voice <= c.t < church:                           # a low hum
        m.update(mouth="o", eyes="half", gesture=False)
    if c.t >= church:
        m.update(eyes="shut", brows="up", gesture=False, arm="palm", rim=0.6, rim_color=(255, 214, 160))
        if not c.st["morgan"]["mouth"] in ("open", "wide"):
            m["mouth"] = "o"
    if 0 <= c.t - organ - 0.3 < 0.2 or 0 <= c.t - big < 0.25:
        c.add_shake(3)
    yield "back"
    rose_window(c.world, BOOTH_CX + 4, BY0 + 24, 11, ramp(c.t, church, church + 0.2))
    if c.t >= church:                                   # coloured light across the booth
        for k, col_ in enumerate(GLASS[:3]):
            x = BOOTH_CX - 6 + k * 6
            blend_poly(c.world, [(x, BY0 + 24), (x + 5, BY0 + 24), (x - 8 + k * 6, BY1 - 5), (x - 18 + k * 6, BY1 - 5)],
                       col_, 0.16 * ramp(c.t, church, church + 0.3))
    organ_pipes(c.world, ramp(c.t, organ, organ + 0.45), ease_out(ramp(c.t, big, big + 0.3)))
    if c.t >= warm:
        blend(c.world, 1.0, (255, 170, 90), 0.14 * ramp(c.t, warm, warm + 0.3))
    yield "mid"
    if voice <= c.t < church:                           # a low hum, rolling out towards the mic
        mx, my = morgan_mouth(c)
        for k in range(2):
            age = (c.t - voice - k * 0.3) % 0.6
            if c.t - voice - k * 0.3 >= 0:
                ring(c.world, mx + 7, my, 3 + age * 14, mix(C["gold_hi"], (255, 255, 255), 0.3))
    yield "ui"
    if c.t < big - 0.1:
        return
    x0, y0, x1, y1 = 10, 36, 96, 86
    panel(c.ui, (x0, y0, x1, y1), (14, 16, 24), C["text"])
    pixel.text(c.ui, (x0 + 4, y0 + 2), "VOCAL ANALYSIS", SILK, C["tele"], shadow=None)
    for k, (name, t0) in enumerate((("BIG", big), ("WARM", warm), ("LOW", low))):
        y = y0 + 14 + k * 12
        if c.t >= t0 - 0.1:
            checkbox(c.ui, x0 + 6, y, ramp(c.t, t0, t0 + 0.2), size=8)
            pixel.text(c.ui, (x0 + 22, y), name, PRESS, C["text"], shadow=None)


@lru_cache(maxsize=None)
def morgue_wall():
    """Steel drawers where the foam was."""
    x0, y0, x1, y1 = INSIDE
    img = Image.new("RGBA", (x1 - x0 + 1, y1 - y0 + 1), STEEL_SH + (255,))
    d = ImageDraw.Draw(img)
    cols, rows = 3, 3
    dw, dh = (img.width - 4) // cols, (img.height - 10) // rows
    for r in range(rows):
        for q in range(cols):
            x, y = 2 + q * dw, 2 + r * dh
            d.rectangle((x, y, x + dw - 2, y + dh - 2), fill=STEEL + (255,), outline=INK + (255,))
            d.line([(x + 1, y + 1), (x + dw - 3, y + 1)], fill=STEEL_HI + (255,))
            d.rectangle((x + dw // 2 - 3, y + dh // 2 - 1, x + dw // 2 + 2, y + dh // 2), fill=(60, 64, 72, 255))
            d.rectangle((x + 3, y + 4, x + 7, y + 6), fill=(250, 250, 244, 255))   # the name card
    d.rectangle((0, img.height - 8, img.width, img.height), fill=(94, 100, 110, 255))  # the floor, hosed down
    return img


@lru_cache(maxsize=None)
def sheet():
    s = Canvas(28, 42)
    s.ell((8, 0, 20, 12), "white")
    s.poly([(5, 8), (23, 8), (27, 41), (1, 41)], "white")
    for x0, x1 in ((9, 6), (14, 14), (19, 22)):
        s.line([(x0, 12), (x1, 40)], "white_sh")
    return s.done()


@lru_cache(maxsize=None)
def my_toe_tag():
    rows = ("MORGAN F.", "CAUSE: BARS")
    w = max(text_width(r, SILK) for r in rows) + 18
    s = Canvas(w, 23)
    s.poly([(7, 2), (w - 3, 2), (w - 3, 20), (7, 20), (2, 11)], (226, 206, 150))
    s.line([(7, 20), (w - 3, 20)], (184, 160, 110))
    s.ell((5, 9, 8, 12), "white")
    s.text(((w + 8) // 2, 1), rows[0], "ink", anchor="ma")
    s.text(((w + 8) // 2, 9), rows[1], "red", anchor="ma")
    return s.done()


def morgue_sign(img, lit):
    x0, y0, x1, _ = BOOTH
    d = ImageDraw.Draw(img)
    d.rectangle((x0 + 10, y0 - 10, x1 - 10, y0 - 3), fill=(40, 60, 70) if not lit else (220, 244, 250))
    pixel.text(img, ((x0 + x1) // 2, y0 - 11), "MORGUE", SILK, (30, 50, 60) if lit else (70, 90, 100), shadow=None,
               anchor="ma")


@gag("v1", 17)
def toe_tag_time(c, L):
    c.st["david"]["hidden"] = True
    c.inset = False                                     # the sheet is his reaction
    c.hit_react["morgan"] = False
    morgue, morgan, toe = wt(L, "morgue"), wt(L, "Morgan"), wt(L, "Toe")
    time_, go = wt(L, "Time"), wt(L, "go")
    m = c.st["morgan"]
    cold = c.t >= morgue
    if c.t < morgan:
        if c.t >= LOW16 + 0.2:                          # line 16 is still settling the camera until then
            c.shot = CHAPEL_LOW
    elif c.t < toe:
        c.shot = "tele"
    elif c.t < time_:
        c.shot = (MORGAN_BOOTH[0] + 16, BOOTH_FLOOR - 10, 24)
    else:
        c.shot = CHAPEL_LOW
    if cold:
        m.update(eyes="wide", brows="worried", mouth="o", gesture=False, arm="down")
        c.vars["booth_light"] = 0.0
        flick = ramp(c.t, morgue, morgue + 0.3)
        if flick < 1 and int(flick * 7) % 2 == 0:
            c.mood = 0.9
        if c.t >= go:                                   # lights out
            c.mood = 0.6 + 0.4 * ramp(c.t, go, go + 0.05)
    else:
        m.update(eyes="shut", brows="up", gesture=False, arm="palm")
    yield "back"
    if not cold:                                        # the church, lingering
        rose_window(c.world, BOOTH_CX + 4, BY0 + 24, 11, 1 - ramp(c.t, L.t0 + 0.4, morgue))
        organ_pipes(c.world, 1 - ramp(c.t, morgue - 0.3, morgue), 1.0)
    else:
        c.world.paste(morgue_wall(), (INSIDE[0], INSIDE[1]))
        x0, y0, x1, y1 = INSIDE
        on = c.t < go and (c.t >= morgue + 0.3 or int(ramp(c.t, morgue, morgue + 0.3) * 7) % 2)
        if on:
            ImageDraw.Draw(c.world).line([(x0 + 8, y0 + 1), (x1 - 8, y0 + 1)], fill=(236, 252, 255))
            blend_poly(c.world, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], COLD, 0.18)
        morgue_sign(c.world, on)
    yield "mid"
    if c.t >= time_:                                    # and a sheet over him
        hx, hy = anchor(c, "morgan", "top")
        drop = ease_in(ramp(c.t, time_, time_ + 0.12))
        sh = sheet()
        paste(c.world, sh, hx - 1, hy - 3 - (1 - drop) * 70 + (1 if 0 < c.t - time_ - 0.12 < 0.06 else 0), "mt")
    if cold and c.t < go:
        blend(c.world, 1.0, (120, 200, 220), 0.12)
    yield "ui"
    if toe <= c.t < time_:                              # the tag, swinging from his shoe
        tg = scaled(my_toe_tag(), 2)
        age = c.t - toe
        drop = ease_out(ramp(age, 0, 0.12))
        sx, sy = ui_at(c, MORGAN_BOOTH[0] + 7, MORGAN_BOOTH[1] - 1)
        hx_, hy_ = sx + 20, int(sy - 34 + (1 - drop) * -60)
        ang = 14 * math.sin(age * 14) * math.exp(-age * 4)
        rt = tg.rotate(ang, resample=Image.NEAREST, center=(12, tg.height // 2), expand=False)
        ImageDraw.Draw(c.ui).line([(sx, sy), (hx_ + 12, hy_ + tg.height // 2)], fill=(240, 240, 240, 255), width=2)
        c.ui.alpha_composite(rt, (hx_, hy_))
