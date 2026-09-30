"""Outro (instrumental): the light goes. Alfred sails home west, George stays with his wreck as night
falls and it settles lower in the water, three epilogue cards give what happened next, then the title,
THE END, and a fade to black ahead of the music's own fade (274-278 s)."""
from PIL import Image

import ships
from gagkit import (C, PRESS16, PRESS24, SILK, big_text, ease_in_out, label,
                    pop_dy, pop_text, ramp, span)
from gags_v4 import at_sea, crown_fall, doc

T0, T1 = 245.74, 281.0
SAIL = (247.0, 258.5)                     # Alfred gets under way and leaves the frame, west
CARDS = [
    (250.0, 254.4, ["WASHINGTON RESIGNED HIS COMMISSION", "IN DECEMBER 1783, AND STEPPED DOWN",
                    "AFTER TWO TERMS AS PRESIDENT IN 1797."]),
    (254.6, 259.0, ["GEORGE III REIGNED FOR 59 YEARS,", "THE LONGEST OF ANY BRITISH KING.",
                    "(HIS SON RULED AS REGENT FROM 1811.)"]),
    (259.2, 263.4, ["HERSCHEL'S PLANET", "KEPT THE NAME URANUS."]),
]
TITLE, THE_END = 264.2, 267.4
FADE = (273.4, 277.0)


@span(T0, T1)
def home(c, L):
    t = c.t
    c.karaoke = False
    go = ease_in_out(ramp(t, *SAIL))
    night = ramp(t, 247.0, 262.0)
    at_sea(c, "duel",
           alfred_x=-240 * go, dark=0.6 * night, stars=ramp(t, 254.0, 264.0),
           sink=6 * ramp(t, 249.0, 272.0), volleys=False, fires=t < 266.0)
    if 258.8 <= t < 263.6:
        c.shot = ships.SHIP_SHOTS["rgwide"]
    c.mood = 0.45 * night
    c.hit_react = {"washington": False, "george": False}
    c.hitfx = False
    w, g = c.st["washington"], c.st["george"]
    for s in (w, g):
        s.update(mic=False, mouth="closed", bob=0, arm="down")
    # Washington raises a hand to George once, then turns for home.
    if t < 247.6:
        w.update(arm="wave" if t >= 246.4 else "down", brows="neutral")
    else:
        w.update(facing=-1)
    g.update(hat="off", brows="worried", eyes="side" if t < 252 else "open")
    if t >= 250:
        g.update(eyes="shut" if (t - 250) % 6 < 0.15 else "open")
    yield "front"
    if t < 246.2:
        crown_fall(c, 244.58)
    yield "ui"
    for a, b, lines in CARDS:
        if a <= t < b:
            age = t - a
            out = ramp(t, b - 0.35, b)
            y = 14 + (pop_dy(age, 0.25, 10) or 0) - int(out * 90)
            doc(c.ui, 160, y, lines, fnt=SILK)
    if t >= TITLE:
        age = t - TITLE
        pop_text(c.ui, 160, 14, "TWO GEORGES", age, PRESS24, dur=0.3)
        if t >= TITLE + 0.8:
            label(c.ui, (160, 46 + (pop_dy(t - TITLE - 0.8, 0.2, 6) or 0)), "A TRANSATLANTIC RAP BATTLE",
                  bg=C["band"], fg=C["gold"], anchor="mt")
        if t >= THE_END:
            big_text(c.ui, (160, 150 + (pop_dy(t - THE_END, 0.25, 8) or 0)), "THE END", PRESS16,
                     top=C["white"], bottom=C["buff"], anchor="ma")
    yield "top"
    p = ramp(t, *FADE)
    if p > 0:
        c.ui.paste(Image.alpha_composite(c.ui, Image.new("RGBA", c.ui.size, (0, 0, 0, round(255 * p)))))
