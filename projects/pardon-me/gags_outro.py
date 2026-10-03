"""The outro and the end card: the verdict, played as one scene.

"Order! Order!": the hall, still on its feet after verse 4, sits down in two waves, and the second bang
knocks the flip chart flat. Behind it stands the dead escalator, OUT OF ORDER. The screens turn into the
voting board and on "verdict" both men duck for cover. "Both of them are asking for a pardon": they
pop up with cardboard pleas while the votes come in, YES 1 (their own), NO 192, and on "pardon" the
Assembly pardons two turkeys instead, unanimously. "Adjourned": the hall files out and the lights go
down. "Please take the stairs": the two trudge up the dead escalator, Trump still at it under the end
titles, and it starts up again the moment he's off it.
"""
import art
import art_ends as A
from gagkit import (C, INK, PRESS, PRESS24, SILK, TL, V, Image, ImageDraw, back_out, bubble, confetti, ease_in,
                    ease_in_out, ease_out, flip, gag, hall, lerp, line_t, math, outline_text, paste, paste_rot,
                    pop_text, pose, ramp, rnd, span)

T_ORDER1, T_ORDER2 = line_t("outro", 0, "order"), line_t("outro", 0, "order", 1)
T_THE, T_VERDICT = line_t("outro", 0, "the"), line_t("outro", 0, "verdict")
T_BOTH, T_ASKING, T_PARDON = line_t("outro", 1), line_t("outro", 1, "asking"), line_t("outro", 1, "pardon")
T_THIS, T_ADJOURNED = line_t("outro", 2), line_t("outro", 2, "adjourned")
T_PLEASE, T_STAIRS = line_t("outro", 2, "please"), line_t("outro", 2, "stairs")
END = TL.section_start("end")
CAST = ("trump", "bibi")


# --- the front row ------------------------------------------------------------------------------------

LEAVE = sorted(range(len(hall.DELEGATES)), key=lambda i: rnd("leave", i))   # the order they file out in
BANGS = (T_ORDER1, T_ORDER2, T_PARDON, T_ADJOURNED)


def delegates(c):
    """Cheering on their feet as verse 4 left them, they sit down in two waves on the gavel, jump at
    every bang, and file out after "adjourned"."""
    t = c.t
    for _, _, i in hall.DELEGATES:
        sit = T_ORDER1 if rnd("sit", i) < 0.5 else T_ORDER2
        if t < sit:
            c.crowd["stand"][i] = 1.0
            c.crowd["react"][i] = 0.7 + 0.3 * math.sin(t * 14 + i)
        else:
            c.crowd["stand"][i] = 1 - ease_out(ramp(t, sit, sit + 0.15))
        leave = T_ADJOURNED + 0.2 + LEAVE.index(i) * 0.16
        if t >= leave:
            c.crowd["stand"][i] = ease_out(ramp(t, leave, leave + 0.2))
            if t >= leave + 0.3:
                c.crowd["gone"].add(i)
    for g in BANGS:
        if 0 <= t - g < 0.3:
            for _, _, i in hall.DELEGATES:
                c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), 1 - (t - g) / 0.3)


# --- the two men: ducking, pleading, leaving -----------------------------------------------------------

DUCK = {"trump": 17, "bibi": 28}          # how far each sinks to peek over his placard or the rostrum
FOOT_X = A.ESC_X + A.ESC["land"] + A.ESC["run"] + 4     # onto the escalator's foot
TOP_X = A.ESC_X + A.ESC["land"]                         # off its top step
# each man's walk out: when he sets off, from where, then (x, speed) legs: to the foot, up, off the top
WALKS = {"bibi": (T_PLEASE + 0.15, 160, 166, ((FOOT_X, 70), (TOP_X, 42), (-40, 70))),
         "trump": (T_PLEASE + 0.25, 270, 176, ((FOOT_X, 90), (TOP_X, 36), (12, 50)))}


def walk(who, t):
    """(x, leg, time into the leg) along `who`'s walk out; leg 0 the floor, 1 the escalator, 2 the top."""
    t0, x, _, legs = WALKS[who]
    for k, (x1, v) in enumerate(legs):
        dur = abs(x1 - x) / v
        if t < t0 + dur:
            return x + (x1 - x) * max(0.0, t - t0) / dur, k, t - t0
        t0, x = t0 + dur, x1
    return x, len(legs), t - t0


def walk_end(who):
    """When `who` comes to the end of his walk."""
    t0, x, _, legs = WALKS[who]
    for x1, v in legs:
        t0, x = t0 + abs(x1 - x) / v, x1
    return t0


T_TOP = walk_end("trump")             # Trump at the top, off the steps at last
T_RESTART = T_TOP + 0.3               # ...and the escalator starts up behind him
T_GONE = T_RESTART + 0.85             # he storms off


def exit_pose(c, who):
    """Walking off to the left, and up the dead escalator step by step."""
    t = c.t
    t0, x0, y0, _ = WALKS[who]
    if who == "trump" and t >= T_RESTART:                 # it runs now: he turns back, fuming, then goes
        x = 12 - max(0.0, t - T_GONE) * 70
        going = t >= T_GONE
        step = int(t * 6) % 2
        pose(c, who, x=x, y=A.feet_on_escalator(x), facing=-1 if going else 1, layer="podium",
             body=("walk1" if step else "walk2") if going else "stand", arm="down" if going else "fist",
             far="down", eyes="wide" if t < T_RESTART + 0.25 else "squint", brows="angry", mouth="grit",
             flush=2, sweat=False, lean=0, bob=0)
        return
    x, leg, _ = walk(who, t)
    if leg == 0:
        y = lerp(y0, 166, ramp(x, x0, x0 - 40))           # out from behind the desk
    else:
        y = A.feet_on_escalator(x)
    moving = leg < len(WALKS[who][3])
    hz = 6 if leg != 1 else 3.5                           # a slow trudge on the steps
    step = int((t - t0) * hz) % 2
    climbing = leg == 1
    tired = who == "trump" and climbing
    pose(c, who, x=x, y=y, facing=-1, layer="podium",
         body=("walk1" if step else "walk2") if moving else "stand", bob=step if moving else 0,
         lean=1 if climbing else 0, arm="down", far="down",
         eyes="half" if climbing else "open", brows="worried" if tired else "neutral",
         mouth=("open" if int(t * 4) % 2 else "o") if tired else "frown", flush=1 if tired else 0,
         sweat=tired or (climbing and x < 70))


def men(c):
    """Both men from the gavel to the end card, as a function of time."""
    t = c.t
    for who in CAST:
        c.hit_react[who] = False
    c.st["bibi"]["hat"] = "mortar"                        # verse 4's professor keeps his mortarboard
    if t >= T_PLEASE:
        for who in CAST:
            if t < WALKS[who][0]:
                pose(c, who, arm="down", far="down", eyes="half", brows="worried", mouth="frown")
            else:
                exit_pose(c, who)
        return
    if t < T_VERDICT:                                     # Trump still fuming, Bibi still smug
        cool = ramp(t, T_ORDER1, T_ORDER1 + 0.6)
        pose(c, "trump", arm="cross", far="down", eyes="squint", brows="angry", mouth="grit",
             flush=2 if cool < 0.5 else 1, tint=((236, 40, 40), 0.25 * (1 - cool)) if cool < 1 else None)
        pose(c, "bibi", arm="shrug", far="out", eyes="open", brows="up", mouth="smirk")
        crash = T_ORDER2 + 0.38
        if crash <= t < crash + 0.45:                     # the chart going over behind him
            pose(c, "bibi", arm="palm", eyes="wide", brows="worried", mouth="o")
        for g in (T_ORDER1, T_ORDER2):
            if 0 <= t - g < 0.15:
                for who in CAST:
                    c.st[who]["eyes"] = "shut"
    elif t < T_THIS:
        if t < T_BOTH:                                    # "verdict": duck!
            k = ease_in(ramp(t, T_VERDICT, T_VERDICT + 0.1))
        else:                                             # "both of them": up they pop, pleading
            k = 1 - back_out(ramp(t, T_BOTH, T_BOTH + 0.2))
        for who in CAST:
            c.st[who]["dy"] = round(DUCK[who] * k)
            c.st[who]["tint"] = None
        if t < T_BOTH:
            shiver = (1 if int(t * 16) % 2 else -1) if t > T_VERDICT + 0.15 else 0
            for who in CAST:                              # (Bibi a step left, so his eyes clear the mics)
                pose(c, who, arm="cross" if who == "trump" else "palm", far="down", eyes="wide", brows="worried",
                     mouth="grit", sweat=True, dx=shiver - (4 if who == "bibi" else 0))
        elif t < T_PARDON:
            pose(c, "trump", arm="hold", far="hold", eyes="wide", brows="worried", mouth="pout", sweat=False)
            pose(c, "bibi", arm="hold", far="hold", eyes="wide", brows="worried", mouth="frown", sweat=False)
        else:                                             # the turkeys get it: jaws drop
            for who in CAST:
                pose(c, who, arm="hold", far="hold", eyes="wide", brows="up", mouth="wide" if who == "trump" else "o")
    else:                                                 # the session's over: two long faces
        for who in CAST:
            pose(c, who, arm="down", far="down", eyes="half", brows="worried", mouth="frown", tint=None, dy=0,
                 sweat=False)
        if 0 <= t - T_ADJOURNED < 0.2:
            for who in CAST:
                c.st[who]["eyes"] = "shut"


CLIP = {"bibi": hall.ROSTRUM_TOP + 1, "trump": hall.DESK_TOP + 1}   # the signs are held up from behind these


def pleas(c):
    """The cardboard pleas: up from behind the rostrum and the desk on "asking", sagging on "pardon",
    lowered out of sight on "This session"."""
    t = c.t
    if not T_ASKING - 0.05 <= t < T_THIS + 0.3:
        return
    for who, dx in (("trump", -1), ("bibi", 1)):
        hx, hy = grip(c, who)
        x, y = hx + 2 * dx, hy + 5                                     # the sign's bottom edge
        y += round((1 - back_out(ramp(t, T_ASKING - 0.05, T_ASKING + 0.12))) * 26)
        spr = A.cardboard(("PARDON", "ME?"))
        if t >= T_PARDON:
            sag = ease_out(ramp(t, T_PARDON + 0.1, T_PARDON + 0.3))
            spr = spr.rotate(-dx * 14 * sag, resample=Image.NEAREST, expand=True)
            y += round(4 * sag)
        if t >= T_THIS:
            y += round(ease_in(ramp(t, T_THIS, T_THIS + 0.25)) * 34)
        top = y - spr.height
        if CLIP[who] > top:
            paste(c.world, spr.crop((0, 0, spr.width, min(spr.height, CLIP[who] - top))),
                  x - spr.width // 2, top, "lt")


def grip(c, who):
    """Between the two hands: where a sign held in both is gripped."""
    a = c.anchor.get(who)
    if not a:
        return 0, 0
    return (a["hand"][0] + a["far"][0]) / 2, (a["hand"][1] + a["far"][1]) / 2


# --- the flip chart goes over, the escalator behind it -------------------------------------------------

FALL = 0.32                       # how long the chart takes to go over
FALLEN = T_ORDER2 + 0.06 + FALL   # ...and when it is down
SIGN_U = 56                       # the OUT OF ORDER sign hangs from the handrail over this column


def chart_down(c, img):
    """From the second bang: the floor patched where the easel's back leg stood, the escalator, its sign,
    and the chart toppling backwards with a puff of dust."""
    t = c.t
    if t < T_ORDER2:
        return
    img.paste(img.crop((73, 126, 78, 172)), (65, 126))          # the carpet repeats every 8 px
    phase = int((t - T_RESTART) * 16) % 8 if t >= T_RESTART else 0
    paste(img, A.escalator(phase), A.ESC_X, A.ESC_Y, "lt")
    spr, ex, ey = A.easel()
    a = t - T_ORDER2 - 0.06
    if a < FALL:
        out_of_order(c, img)                                      # behind the chart until it's down
        k = math.cos(math.pi / 2 * ease_in(max(0.0, a) / FALL))
        h = max(1, round(spr.height * k))
        paste(img, spr.resize((spr.width, h), Image.NEAREST), ex, ey + spr.height - h, "lt")
    else:
        for j in range(7):
            A.dust(img, ex + 8 + j * 15, 166, a - FALL - 0.03 * (j % 3), size=1.6, seed=(9, j), life=0.7)


def out_of_order(c, img):
    """The sign hung level off the sloping handrail: set swinging by the bang, dropping off when the
    escalator starts up."""
    t = c.t
    x = A.ESC_X + SIGN_U
    sign = A.sign2("OUT OF", "ORDER")
    top = A.ESC_Y + round(A.rail_y(SIGN_U + 12)) + 4
    if t >= T_RESTART:
        a = t - T_RESTART
        if a < 0.6:
            paste_rot(img, sign, x + 10 * a, top + sign.height // 2 + 360 * a * a, -200 * a)
        return
    swing = 7 * math.sin((t - T_ORDER2) * 11) * math.exp(-(t - T_ORDER2) * 2.5)
    d = ImageDraw.Draw(img)
    for s in (-12, 12):                                          # two cords up to the rail
        d.line([(x + s, A.ESC_Y + A.rail_y(SIGN_U + s) + 1), (x + s + swing * 0.15, top + 1)], fill=INK)
    paste_rot(img, sign, x + swing * 0.3, top + sign.height // 2, swing)


# --- the screens: the voting board -------------------------------------------------------------------

def channel(schedule, seed):
    """A screen cutting down a schedule [(t, fn(c, img, box)), ...], through two frames of static each."""
    def fn(c, img, box):
        k, t0, f = max((k, t0, f) for k, (t0, f) in enumerate(schedule) if c.t >= t0 or k == 0)
        if k and c.t < t0 + 0.08 and f is not switch_off:
            A.static(img, box, (seed, k, int(c.t * 24)))
        else:
            f(c, img, box)
    return fn


def switch_off(c, img, box):
    """The screen goes dark: the picture collapses to a bright line, then nothing."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x1 - 1, y1 - 1), fill=(10, 12, 22))
    off = SWITCH_OFF[0 if x0 < 160 else 1]
    a = c.t - off
    if a < 0.18:
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        half = round((x1 - x0) / 2 * (1 - a / 0.18) ** 2)
        d.line([(cx - half, cy), (cx + half, cy)], fill=(226, 236, 255))
        d.line([(cx - half // 2, cy + 1), (cx + half // 2, cy + 1)], fill=(120, 140, 190))


def live(who, facing):
    return lambda c, img, box: V.live_feed(c, img, box, who, facing)


def voting(seed):
    return lambda c, img, box: A.voting_board(c, img, box, T_THE + 0.15, T_VERDICT - 0.1, seed)


def tally(who):
    """The man's pardon: his own vote first, then the rest coming in against it."""
    def fn(c, img, box):
        lit = ease_in_out(ramp(c.t, T_BOTH + 0.3, T_ASKING + 0.4))
        A.result_board(img, box, who, 1, round(192 * lit), lit, blink=int(c.t * 5) % 2 == 0)
    return fn


def turkeys_win(seed):
    def fn(c, img, box):
        A.turkey_board(c, img, box, T_PARDON)
        if c.t - T_PARDON < 2.0:
            confetti(img, box, c.t - T_PARDON, seed=seed, n=26)
    return fn


def notice(*lines, arrow=None):
    return lambda c, img, box: A.notice(img, box, lines, arrow=arrow)


SWITCH_OFF = (END + 0.6, T_GONE + 0.3)      # the left screen goes dark once the end card is up, the right last
SCREEN_L = channel([(0, live("bibi", 1)), (T_THE, voting(1)), (T_BOTH, tally("BIBI")), (T_PARDON, turkeys_win(1)),
                    (T_ADJOURNED, notice("SESSION", "ADJOURNED")), (SWITCH_OFF[0], switch_off)], 31)
SCREEN_R = channel([(0, live("trump", -1)), (line_t("outro", 0) - 0.12, live("trump", -1)), (T_THE, voting(2)),
                    (T_BOTH, tally("TRUMP")), (T_PARDON, turkeys_win(2)),
                    (T_PLEASE, notice("PLEASE TAKE", "THE STAIRS", arrow="l")), (SWITCH_OFF[1], switch_off)], 32)


# --- the pardoned turkeys, up on the dais -----------------------------------------------------------------

TURKEYS = ((127, 1, 0.0), (193, -1, 0.09))      # x, facing, how late each pops up


def turkeys(c, img):
    """Two turkeys pop up behind the ledge either side of the President, gobbling, in a shower of confetti."""
    t = c.t
    if t < T_PARDON:
        return
    clip = hall.LEDGE_Y - 3
    for x, facing, late in TURKEYS:
        a = t - T_PARDON - late
        if a < 0:
            continue
        y = 69 + round((1 - back_out(ramp(a, 0, 0.25))) * 34)
        gobble = int(a * 7) % 2 == 0 if a < 1.3 else int(a * 2 + late * 20) % 4 == 0
        spr = art.turkey(None, facing, gobble)
        top = y - spr.height
        if clip > top:
            paste(img, spr.crop((0, 0, spr.width, min(spr.height, clip - top))), x - spr.width // 2, top, "lt")
    a = t - T_PARDON
    if a < 2.2:
        confetti(img, (104, 0, 216, 62), a, seed=7, n=round(36 - 14 * max(0.0, a - 1)))


# --- the scene, line by line ------------------------------------------------------------------------------

def setup(c):
    delegates(c)
    men(c)
    c.screens["L"], c.screens["R"] = SCREEN_L, SCREEN_R
    if c.t < T_ORDER2:
        flip(c, line_t("outro", 0) - 0.12)                 # verse 4's last page goes, the cover sheet's back
    else:
        c.chart = False
    if c.t >= T_STAIRS:
        c.mood = 0.55 * ease_in_out(ramp(c.t, T_STAIRS, END)) + 0.3 * ramp(c.t, END, END + 1.2)


def scene(c):
    setup(c)
    yield "back"
    chart_down(c, c.world)
    turkeys(c, c.world)
    yield "chart"
    if c.page is not None:
        V.default_page(c, c.page)
    yield "mid"
    if c.t >= FALLEN:                                      # the near handrail, over whoever is on the steps
        paste(c.world, A.escalator_rail(), A.ESC_X, A.ESC_Y, "lt")
        out_of_order(c, c.world)
    yield "front"
    pleas(c)
    if T_RESTART + 0.15 <= c.t < T_GONE:                   # Trump at the top as it starts up behind him
        hx, hy = c.anchor["trump"]["head"]
        bubble(c.world, hx + 18, hy - 12, "?!", tail=(hx + 8, hy - 4), fnt=PRESS)


@gag("outro", 0)
def order_order(c, L):
    """Order! Order! The Assembly has reached a verdict."""
    yield from scene(c)


@gag("outro", 1)
def asking_for_a_pardon(c, L):
    """Both of them are asking for a pardon."""
    c.gavel = [T_PARDON]
    yield from scene(c)


@gag("outro", 2)
def take_the_stairs(c, L):
    """This session is adjourned. Please take the stairs."""
    c.gavel = [T_ADJOURNED]
    yield from scene(c)


# --- the end card -----------------------------------------------------------------------------------------

TX = 207                                  # the titles' centre, clear of the escalator
T_TITLE = END + 0.5                       # once Trump has climbed clear of them
T_FINAL = END + 1.6                       # the last bang of the gavel


@span(END, TL.DURATION + 1)
def end_card(c, L):
    """The titles over the dark, empty hall, Trump still on the stairs."""
    c.gavel = [T_FINAL]
    yield from scene(c)
    yield "ui"
    a = c.t - T_TITLE
    pop_text(c.ui, TX, 67, "PARDON ME", a, fnt=PRESS24)
    pop_text(c.ui, TX, 96, "TRUMP vs. BIBI", a - 0.3, fnt=PRESS)
    if a > 0.6:
        outline_text(c.ui, (TX, 105), "A UN GENERAL ASSEMBLY RAP BATTLE", SILK, C["white"], INK, "ma")
    pop_text(c.ui, TX, 118, "SESSION ADJOURNED", c.t - T_FINAL, fnt=PRESS, top=C["red_hi"], bottom=C["red"])
