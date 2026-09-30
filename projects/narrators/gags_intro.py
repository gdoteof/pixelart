"""The intro: Sir David's cold open. The camera boots up in the jungle, the vocal booth's light
flickers on, the two silverbacks are tagged, all of life on Earth marches past, the prize is
shown, and the specimen is identified (his two freckles are the spots). Then the show's title.
"""
from critters import bird, gorilla, lion, penguin, rat, trex, whale
from gagkit import (C, CH, INK, SILK, W, anchor, blend, ease_out, gag, math, mirror, pan, pixel, ramp, span,
                    ui_at, wt)
from props import ring, sparkle
from sets import MORGAN_BOOTH, STUMP

BOOT = (0.35, 1.45)                  # the camera powers up: black, standby, then the picture
TITLE0 = 19.3


def crouch_whisper(c):
    """Sir David crouched in the ferns, whispering to camera."""
    s = c.st["david"]
    s.update(body="crouch", arm="whisper", mic=False)
    s["brows"] = "up"


@span(0.0, 1.69)
def camera_boot(c, L):
    c.shot = (160, 96, 6)
    c.vars["booth_light"] = 0.0
    c.rec = c.t > 1.2
    crouch_whisper(c)
    c.subs = False
    yield "front"
    dark = 1 - ease_out(ramp(c.t, *BOOT))
    if dark > 0:
        blend(c.world, 1.0, (0, 0, 0), dark)
    yield "top"
    if c.t < 1.2 and int(c.t * 3) % 2 == 0:
        pixel.text(c.ui, (22, 12), "STBY", SILK, C["text"], shadow=INK)


@gag("intro", 0, pre=1.0)
def harsh_light(c, L):
    # a slow push through the clearing towards the booth
    pan(c, (160, 96, 6), (156, 108, 9), L.t0, 3.4)
    crouch_whisper(c)
    harsh = wt(L, "harsh")
    k = ramp(c.t, harsh, harsh + 0.45)
    flicker = 1.0 if k >= 1 else (1.0 if (int(c.t * 24) * 7) % 3 == 0 else 0.15) * k
    c.vars["booth_light"] = flicker if c.t >= harsh else 0.0
    c.vars["on_air"] = c.t >= wt(L, "booth")
    two = wt(L, "two")
    circle = wt(L, "circle")
    m = c.st["morgan"]
    if c.t >= circle:                                   # the specimen paces his booth
        ph = (c.t - circle) * 0.9
        m["x"] = MORGAN_BOOTH[0] + 7 * math.sin(ph * math.pi)
        m["facing"] = 1 if math.cos(ph * math.pi) > 0 else -1
        m["body"] = "walk1" if int(c.t * 4) % 2 else "walk2"
        m["arm"] = "down"
    yield "top"
    if c.t >= two:
        hm = anchor(c, "morgan", "top")
        hd = anchor(c, "david", "top")
        mx, my = ui_at(c, *hm)
        dx, dy = ui_at(c, *hd)
        CH.callout(c.ui, c.t - wt(L, "old"), "SILVERBACK #1", mx, my, mx + 26, my - 22)
        CH.callout(c.ui, c.t - wt(L, "silverbacks"), "SILVERBACK #2", dx, dy, dx - 4, dy - 30)


# --- "One narrated all of life on Earth." ----------------------------------------------------------

PARADE = [(lambda f: penguin(f), 0.0), (lambda f: gorilla("walk"), 0.55), (lambda f: lion(), 1.15),
          (lambda f: rat(f), 1.7), (lambda f: trex("open" if f else "shut", f), 2.0), (lambda f: penguin(1 - f), 2.9)]


@gag("intro", 1)
def life_on_earth(c, L):
    c.shot = (150, 118, 9)
    s = c.st["david"]
    s.update(body="stand", arm="palm" if c.t < wt(L, "life") else "point", mic=False)
    t_go = L.t0 + 0.2
    yield "mid"
    f = int(c.t * 6) % 2
    for k, (spr_fn, delay) in enumerate(PARADE):
        age = c.t - t_go - delay
        if age < 0:
            continue
        spr = mirror(spr_fn(f))                         # they march right to left, towards Sir David
        x = 330 - age * 95
        if x < -spr.width:
            continue
        y = 152 + (k % 2) * 2 - (1 if f and k % 2 else 0)
        c.world.paste(spr, (int(x), y - spr.height), spr)
    wage = c.t - t_go - 0.6                             # and a blue whale swims through the canopy
    if wage >= 0:
        wsp = mirror(whale(int(c.t * 2) % 2))
        c.world.paste(wsp, (int(340 - wage * 70), int(62 + 4 * math.sin(wage * 2))), wsp)
    for k in range(3):
        bage = c.t - t_go - 0.3 * k
        if bage >= 0:
            b = mirror(bird(int(c.t * 8 + k) % 2, color=[(236, 80, 60), (70, 150, 230), (250, 200, 60)][k]))
            c.world.paste(b, (int(330 - bage * 130 - k * 9), int(70 + k * 9 + 3 * math.sin(bage * 9))), b)
    yield "ui"
    CH.lower_third(c.ui, c.t - wt(L, "narrated"), "SIR DAVID ATTENBOROUGH", "NARRATOR, LIFE ON EARTH (1979)",
                   y=26, out_at=2.6)


# --- "Only one leaves with the planet." ----------------------------------------------------------

@gag("intro", 2)
def the_planet(c, L):
    planet = wt(L, "planet")
    x, y = STUMP[0], STUMP[1] - 30
    c.shot = (x, y + 4, 12) if c.t < planet else (x, y + 2, 18)
    crouch_whisper(c)
    yield "front"
    if c.t >= planet:
        age = c.t - planet
        for k in range(4):
            a = k * math.pi / 2 + age * 2
            r = 12 + 2 * math.sin(age * 6 + k)
            sparkle(c.world, int(x + math.cos(a) * r), int(y - 6 + math.sin(a) * r), 1 + (k % 2), (255, 250, 220))
    yield "ui"
    CH.lower_third(c.ui, c.t - wt(L, "leaves"), "THE PLANET", "ONE AVAILABLE. NO RETURNS.", y=112)


# --- "Observe: Morganus freemanii. The lesser-spotted baritone." ---------------------------------

@gag("intro", 3)
def morganus_freemanii(c, L):
    spotted = wt(L, "lesser")
    title = TITLE0
    if c.t < spotted:
        c.shot = (205, 110, 18)
    elif c.t < title:
        c.shot = (207, 104, 24)
    else:
        pan(c, (207, 104, 24), (160, 90, 6), title, 1.6)
    m = c.st["morgan"]
    m["mouth"] = "o" if spotted <= c.t < title and int(c.t * 3) % 2 == 0 else m["mouth"]
    if c.t >= spotted:
        m["brows"] = "up"
        m["eyes"] = "side" if c.t < title else m["eyes"]
    crouch_whisper(c)
    yield "top"
    if c.t < title:
        CH.zoom_bar(c.ui, 0.66 if c.t < spotted else 1.0)
        CH.lower_third(c.ui, c.t - wt(L, "Morganus"), "MORGANUS FREEMANII",
                       "THE LESSER-SPOTTED BARITONE" if c.t >= spotted else None, y=30,
                       out_at=title - wt(L, "Morganus") - 0.3)
    if spotted <= c.t < title:                         # the spots, all two of them, ringed in red
        fx, fy = MORGAN_BOOTH
        for k, (sx, sy) in enumerate(((27, 19), (29, 18))):
            age = c.t - spotted - 0.25 * k
            if age < 0:
                continue
            ux, uy = ui_at(c, fx - 20 + sx + 0.5, fy - 52 + sy + 0.5)
            ring(c.ui, ux, uy, 4 if age > 0.1 else 7)
        if c.t >= spotted + 0.7:
            ux, uy = ui_at(c, fx + 10, fy - 36)
            CH.callout(c.ui, c.t - spotted - 0.7, "SPOTS: 2", ux, uy, ux + 34, uy + 20, color=C["red_hi"])
    if c.t >= spotted + 1.3 and c.t < title + 0.2:
        pixel.text(c.ui, (W - 150, 112), "IUCN STATUS", SILK, C["text"], shadow=INK)
        CH.status_scale(c.ui, 0, x=W - 150, y=120)
    CH.episode_title(c.ui, c.t - (title + 0.4), "PLANET BEEF", "EPISODE ONE: SILVERBACKS", dur=3.8)

