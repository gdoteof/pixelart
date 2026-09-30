"""The links between sections: the hijacks where the other narrator takes the camera, the film
titles, and the end credits.

    V1 -> V2   Morgan's film burns through the documentary; the letterbox slams in: THE BBC REDEMPTION
    V2 -> V3   the documentary jams the signal: static, then REC again: EPISODE TWO: EXTINCTION
    V3 -> V4   a clapperboard snaps shut on the documentary: DRIVING MR. DAVID
    V4 ->      THE END, and the credits roll over the instrumental (the outro plays after them)
"""
from gagkit import (BAR, CH, PRESS16, SILK, TL, H, W, ImageDraw, clamp, ease_in,
                    ease_out, lerp, pixel, ramp, rnd, span)
from props import clapperboard

T_V2 = TL.section_bounds("v2")[0]
T_V3 = TL.section_bounds("v3")[0]
T_V4 = TL.section_bounds("v4")[0]
T_CREDITS = TL.section_bounds("credits")[0]
T_OUTRO = TL.section_bounds("outro")[0]
LAST_V4 = TL.last_word(TL.lines_of("v4")[-1])


def bars_slam(c, t0, dur=0.14):
    """The letterbox bars slam in from nothing at t0 (with a jolt as they land)."""
    k = ramp(c.t, t0, t0 + dur)
    c.bars = ease_in(k)
    if 0 <= c.t - (t0 + dur) < 0.2:
        c.add_shake(7 * (1 - (c.t - t0 - dur) / 0.2))


# --- V1 -> V2: the film burns through ------------------------------------------------------------

BURN0 = T_V2 - 0.42


@span(BURN0, T_V2 + 4.2)
def burn_to_film(c, L):
    c.inset = c.inset and c.t > T_V2 + 0.6
    if c.t >= T_V2:
        bars_slam(c, T_V2 + 0.02)
        if c.t < T_V2 + 0.1:
            c.add_flash(0.9, (255, 240, 200))
    yield "top"
    if c.t < T_V2 + 0.05:
        CH.film_burn(c.ui, ramp(c.t, BURN0, T_V2) ** 0.7, seed=3)
        if c.t >= T_V2 - 0.05:
            ImageDraw.Draw(c.ui).rectangle((0, 0, W, H), fill=(255, 250, 236, 255))
    CH.film_title(c.ui, c.t - (T_V2 + 0.35), "THE BBC\nREDEMPTION", "MORGAN FREEMAN in", dur=3.6, y=40)


# --- V2 -> V3: the documentary takes the channel back ----------------------------------------------

STATIC = (T_V3 - 0.35, T_V3 + 0.28)


@span(STATIC[0] - 0.2, T_V3 + 4.0)
def static_to_doc(c, L):
    c.inset = c.inset and not STATIC[0] < c.t < STATIC[1] + 0.3
    if c.t < T_V3:
        c.bars = 1 - ease_in(ramp(c.t, T_V3 - 0.3, T_V3))
    yield "top"
    a, b = STATIC
    amount = ramp(c.t, a, T_V3 - 0.05) if c.t < T_V3 else 1 - ramp(c.t, T_V3 + 0.1, b)
    if amount > 0:
        CH.static_noise(c.ui, clamp(amount * 1.2, 0, 1), seed=c.f)
        if 0.25 < amount:
            y = int(rnd("roll", c.f) * H)
            ImageDraw.Draw(c.ui).rectangle((0, y, W, y + 3), fill=(236, 236, 240, 255))
    if T_V3 - 0.05 <= c.t < T_V3 + 0.25:                      # the channel's ident card, through the static
        d = ImageDraw.Draw(c.ui)
        d.rectangle((0, 72, W, 112), fill=(14, 16, 28, 255))
        d.line([(0, 72), (W, 72)], fill=(236, 236, 240, 255))
        d.line([(0, 112), (W, 112)], fill=(236, 236, 240, 255))
        pixel.text(c.ui, (W // 2, 80), "PLANET BEEF", PRESS16, (255, 255, 255), shadow=(0, 0, 0), anchor="ma")
        pixel.text(c.ui, (W // 2, 100), "PLEASE STAND BY", SILK, (255, 232, 40), shadow=(0, 0, 0), anchor="ma")
    CH.episode_title(c.ui, c.t - (T_V3 + 0.5), "EPISODE TWO", "EXTINCTION", dur=3.2)


# --- V3 -> V4: the clapperboard ---------------------------------------------------------------------

CLAP_IN = T_V4 - 0.7


@span(CLAP_IN, T_V4 + 4.4)
def clapper_to_film(c, L):
    c.inset = c.inset and not CLAP_IN < c.t < T_V4 + 0.6
    if c.t >= T_V4:
        bars_slam(c, T_V4 + 0.02)
    yield "top"
    age = c.t - CLAP_IN
    if age < 0.95:
        drop = ease_out(ramp(age, 0, 0.25))
        leave = ease_in(ramp(age, 0.8, 0.95))
        y = lerp(-50, 86, drop) + leave * 150
        open_ = 1 - ease_in(ramp(c.t, T_V4 - 0.1, T_V4))          # snaps shut on the downbeat
        clapperboard(c.ui, W // 2, y, ["PROD: DRIVING MR. DAVID", "SCENE 1   TAKE 1", "DIR: M. FREEMAN"], open_)
    CH.film_title(c.ui, c.t - (T_V4 + 0.5), "DRIVING\nMR. DAVID", "A FREEMAN PICTURE", dur=3.6, y=40)


# --- the end, and the credits -----------------------------------------------------------------------

END_CARD = LAST_V4 + 0.9
ROLL0 = END_CARD + 1.9

CREDITS = [
    "DRIVING MR. DAVID", "",
    ("DIRECTED BY", "MORGAN FREEMAN"), ("WRITTEN BY", "MORGAN FREEMAN"), ("NARRATED BY", "MORGAN FREEMAN"),
    ("DRIVEN BY", "MORGAN FREEMAN"), "",
    "CAST",
    ("THE NARRATOR", "MORGAN FREEMAN"), ("GOD", "MORGAN FREEMAN"), ("THE PRESIDENT", "MORGAN FREEMAN"),
    ("THE OTHER NARRATOR", "SIR DAVID"), ("THE FOSSIL", "SIR DAVID"), ("THE DODO", "SIR DAVID"),
    ("SILVERBACK #2", "A SILVERBACK"), ("THE MOLE", "UNCREDITED"), ("THE SLOTH", "MISBEHAVING"),
    ("THE LYREBIRD", "MORGAN FREEMAN*"), "",
    ("TEA", "SIR DAVID"), ("BOATY MCBOATFACE", "AS ITSELF"), ("SEVENTY MILES", "EMPEROR PENGUINS"), "",
    "NO FERNS WERE GIVEN", "ANY PRIVACY IN THE", "MAKING OF THIS FILM", "",
    ("* VOICE", "A LYREBIRD"),
]


@span(LAST_V4 + 0.5, T_OUTRO + 0.05)
def the_end(c, L):
    if c.t >= END_CARD:
        c.set_scene("black")
        c.subs = False
        c.inset = False
    yield "top"
    CH.film_title(c.ui, c.t - END_CARD, "THE END", None, dur=1.9, y=66)
    if c.t >= ROLL0:
        speed = (len(CREDITS) * 12.5 + (H - 2 * BAR) + 10) / (T_OUTRO - 0.4 - ROLL0)
        CH.credits_roll(c.ui, c.t - ROLL0, CREDITS, speed=speed)
    elif c.t >= END_CARD:
        CH.letterbox(c.ui, 1.0)
