"""The hook: the delegates' chant. Their placards read PARDON ME? and both men, delighted, point at
themselves; then the placards turn to PARDON YOU! and each points at the other. "Two defendants, one
mic": mugshots on the screens, a tug of war over the one microphone, and the verdict stamped
OVERDUE. Then the chant again with a pardoned turkey strolling through, the gavel banging in vain,
until one last bang and everybody sits down.
"""
import art
import art_ends as A
from gagkit import (C, INK, PRESS, PRESS16, V, ImageDraw, anchor, back_out, bubble, ease_in_out, ease_out, gag, hall,
                    lerp, line_t, math, paste, place, pose, ramp, rnd, stamp, wt)

HOLDERS = (1, 4, 7, 13)                 # the delegates holding placards (clear of the rostrum)
LEFT = (1, 4, 7)                        # in the second chant, leaving the right side to the turkey
PARDONS = [w["t0"] for i in (3, 4) for w in V.TL.line("hook", i)["words"] if w["w"].lower().startswith("pardon")]
QUIET = 121.99                          # the bang that finally brings the room to order (a beat after the chant)
LUNGE_X = 199                           # where Trump grabs for the mic, right of the rostrum
MIC_BASE = (164, 130)
MIC_REST = (166, 117)


# --- the crowd -----------------------------------------------------------------------------------

def pump(t, times, dur=0.28):
    """1.0 on each of `times`, falling to 0 over `dur`."""
    for w in reversed(times):
        if 0 <= t - w < dur:
            return 1 - (t - w) / dur
    return 0.0


def chant(c, times, stand=1.0, holders=HOLDERS):
    """The front rows on their feet, hands up on every "Pardon"."""
    k = pump(c.t, times)
    for _, _, i in hall.DELEGATES:
        c.crowd["stand"][i] = stand
        if i not in holders:
            c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), stand * (0.35 + 0.65 * k))


def placards(c, img, lines, times, up=1.0, flip_t=None, old=None, late=None, holders=HOLDERS):
    """The placards held up over the front rows, jumping on each of `times`. From `flip_t` they turn
    round from `old` to `lines`. `up` (0..1) raises them; `late` = (i, up) holds one delegate's apart."""
    for x, y, i in hall.DELEGATES:
        if i not in holders:
            continue
        u = late[1] if late and late[0] == i else up
        if u <= 0:
            continue
        spr = A.placard(lines, stick=22)
        if flip_t is not None and c.t < flip_t + 0.16:
            p = (c.t - flip_t) / 0.16
            if p < 0.5:
                spr = A.placard(old, stick=22)
            w = max(1, int(spr.width * abs(math.cos(p * math.pi)))) if p >= 0 else spr.width
            spr = spr.resize((w, spr.height))
        jump = round(5 * pump(c.t - rnd("lag", i) * 0.05, times))
        stand = c.crowd["stand"].get(i, 0.0)
        head = y - round(stand * 10)
        top = head + 1 + round((1 - u) * 50) - jump
        paste(img, spr, x, top, "mb")


def holders_hands(c, holders=HOLDERS):
    """The placard holders raise both hands to their sticks."""
    for i in holders:
        c.crowd["react"][i] = max(c.crowd["react"].get(i, 0.0), 0.75)


# --- the President -------------------------------------------------------------------------------

def order(c, img, t, s="ORDER!", fnt=PRESS, dur=0.55):
    """The President's speech bubble from a slam at t."""
    age = c.t - t
    if 0 <= age < dur:
        dy = round((1 - back_out(min(1.0, age / 0.12))) * 4)
        bubble(img, 196, 47 + dy, s, tail=(166, 54), fnt=fnt, anchor="mb")


# --- the men ------------------------------------------------------------------------------------

def say(c, img, who, s, t0, t1):
    """A small speech bubble over `who` from t0 to t1."""
    if t0 <= c.t < t1:
        mx, my = anchor(c, who, "mouth")
        dy = round((1 - back_out(min(1.0, (c.t - t0) / 0.12))) * 3)
        side = 1 if c.st[who]["facing"] > 0 else -1
        bubble(img, mx + side * 22, my - 9 + dy, s, tail=(mx + side * 5, my - 1), fnt=PRESS, anchor="mb")


# --- "Pardon me? Pardon me!" ------------------------------------------------------------------------

@gag("hook", 0, pre=0.9)
def pardon_me(c, L):
    p1, _, p2, me2 = (w["t0"] for w in L.words)
    rise = L.t0 - 0.62                                # up on the beat before the chant
    stand = ease_out(ramp(c.t, rise, rise + 0.25))
    chant(c, [p1, p2], stand)
    if stand > 0.5:
        holders_hands(c)
    c.gavel = [107.94, 108.58]
    for who in ("bibi", "trump"):                     # me? ME!
        if c.t >= p1:
            pose(c, who, arm="hold", far="down", eyes="wide", brows="up", mouth="o" if c.t < p2 else "grin")
            c.hit_react[who] = False
    yield "front"
    placards(c, c.world, ("PARDON", "ME?"), [p1, p2], up=ease_out(ramp(c.t, rise + 0.1, rise + 0.4)))
    say(c, c.world, "bibi", "ME?" if c.t < p2 else "ME!", p1 + 0.1, me2 + 0.9)
    say(c, c.world, "trump", "ME?" if c.t < p2 else "ME!", p1 + 0.2, me2 + 0.9)
    yield "ui"
    order(c, c.ui, 108.58)


@gag("hook", 1)
def pardon_you(c, L):
    p1, me1, p2, me2 = (w["t0"] for w in L.words)
    chant(c, [p1, p2])
    holders_hands(c)
    c.gavel = [110.5, 111.14]
    for who in ("bibi", "trump"):                     # each one points at the other: HIM!
        if c.t >= p1 + 0.1:
            pose(c, who, arm="point", far="down", eyes="open", brows="angry", mouth="wide" if c.t < me1 else "grit")
            c.hit_react[who] = False
    yield "front"
    placards(c, c.world, ("PARDON", "YOU!"), [p1, p2], flip_t=p1 - 0.08, old=("PARDON", "ME?"))
    say(c, c.world, "bibi", "HIM!", p1 + 0.25, me2 + 1.0)
    say(c, c.world, "trump", "HIM!", p1 + 0.3, me2 + 1.0)
    yield "ui"
    for g in c.gavel:
        order(c, c.ui, g)


# --- "Two defendants, one mic, and the verdict's overdue!" ---------------------------------------------

def mic(img, head, t_glint=None, t=0.0):
    """The rostrum's one microphone on its gooseneck, bent from the base to `head`."""
    d = ImageDraw.Draw(img)
    bx, by = MIC_BASE
    hx, hy = head
    mx, my = (bx + hx) / 2 - (hy - by) * 0.15, (by + hy) / 2
    pts = [(lerp(lerp(bx, mx, k), lerp(mx, hx, k), k), lerp(lerp(by, my, k), lerp(my, hy, k), k))
           for k in (i / 8 for i in range(9))]
    d.line(pts, fill=INK, width=3)
    d.line(pts, fill=C["steel_sh"])
    d.rectangle((hx - 2, hy - 4, hx + 2, hy + 1), fill=INK)
    d.rectangle((hx - 1, hy - 3, hx + 1, hy), fill=(70, 70, 80))
    d.point((hx, hy - 3), fill=C["steel"])
    if t_glint is not None and 0 <= t - t_glint < 0.35:
        k = 1 + int((t - t_glint) * 12) % 2
        d.line([(hx + 3, hy - 6 - k), (hx + 3, hy - 6 + k)], fill=C["white"])
        d.line([(hx + 3 - k, hy - 6), (hx + 3 + k, hy - 6)], fill=C["white"])


@gag("hook", 2)
def one_mic(c, L):
    two, defs = wt(L, "Two"), wt(L, "defendants")
    one, t_mic, over = wt(L, "one"), wt(L, "mic"), wt(L, "overdue")
    t = c.t
    chant(c, [two, one, t_mic, over], holders=())
    c.mics = False
    c.screens["L"] = lambda c, img, box: A.mugshot(c, img, box, "bibi", "DEFENDANT #1", flash_t=two)
    c.screens["R"] = lambda c, img, box: A.mugshot(c, img, box, "trump", "DEFENDANT #2", flash_t=defs)
    dash_end, fling_end = t_mic + 0.2, over + 0.4
    for who in ("bibi", "trump"):
        c.hit_react[who] = False
    tug = t_mic <= t < over
    wob = 1 if int(t * 9) % 2 else -1
    head = MIC_REST
    # Trump dashes over from the desk, grabs, and is flung back by the spring when it snaps
    if t < t_mic:
        pose(c, "trump", arm="cross", mouth="pout", eyes="squint")
        if t >= one:
            pose(c, "trump", arm="down", eyes="open", brows="up", mouth="o")
    elif t < over:
        p = ease_out(ramp(t, t_mic, dash_end))
        place(c, "trump", x=lerp(270, LUNGE_X, p), y=lerp(176, 166, p), facing=-1, layer="podium")
        pose(c, "trump", arm="point", far="down", mouth="grit", brows="angry", eyes="open",
             body="walk1" if p < 1 else "stand", lean=2 * wob if tug and t >= dash_end else 0)
        c.st["trump"]["sweat"] = t >= dash_end
        head = (180 + (2 * wob if t >= dash_end else 0), 121)
    else:
        p = ramp(t, over, fling_end)
        x, y = lerp(LUNGE_X, 270, ease_out(p)), lerp(166, 176, p) - 26 * 4 * p * (1 - p)
        place(c, "trump", x=x, y=y, facing=-1, layer="podium" if p < 0.5 else "desk")
        c.st["trump"]["rot"] = -360 * ease_in_out(p) if p < 1 else 0.0
        pose(c, "trump", arm="palm", far="out", mouth="wide" if p < 1 else "o", eyes="x" if p >= 1 else "wide",
             brows="worried")
        c.st["trump"]["dizzy"] = p >= 1
    # Bibi lunges for it from the rostrum and staggers back
    if t < t_mic:
        pose(c, "bibi", arm="down", eyes="open", brows="up" if t >= one else "neutral", mouth="closed")
    elif t < over:
        pose(c, "bibi", arm="point", far="down", mouth="grit", brows="angry", lean=1 + 2 * wob)
        c.st["bibi"]["sweat"] = t >= dash_end
    else:
        rec = max(0.0, 1 - (t - over) / 0.35)
        pose(c, "bibi", arm="palm", far="out", mouth="o", eyes="x" if t > over + 0.35 else "wide",
             brows="worried", lean=-round(3 * rec))
        c.st["bibi"]["dizzy"] = t > over + 0.2
    if t >= over:                                     # the gooseneck springs home
        age = t - over
        k = math.cos(age * 28) * math.exp(-age * 5)
        head = (MIC_REST[0] + (180 - MIC_REST[0]) * k, MIC_REST[1] + (121 - MIC_REST[1]) * k)
    if over <= t < over + 0.5:
        for _, _, i in hall.DELEGATES:
            c.crowd["react"][i] = 1.0 - (t - over) / 0.5
    yield "mid"
    mic(c.world, (round(head[0]), round(head[1])), one, t)
    if tug and t >= dash_end:                         # strain marks over the two of them
        d = ImageDraw.Draw(c.world)
        r0 = 4 + int(t * 10) % 2
        for who, side in (("bibi", -1), ("trump", 1)):
            hx, hy = anchor(c, who, "top")
            for k in range(3):
                a = math.radians(-90 + side * 25 + (k - 1) * 30)
                d.line([(hx + side * 6 + math.cos(a) * r0, hy - 2 + math.sin(a) * r0),
                        (hx + side * 6 + math.cos(a) * (r0 + 3), hy - 2 + math.sin(a) * (r0 + 3))], fill=INK)
    yield "top"
    verdict = wt(L, "verdict")
    if t >= verdict:                                  # the verdict's library card, and the stamp
        card = A.due_card()
        dy = round((1 - back_out(min(1.0, (t - verdict) / 0.15))) * -50)
        paste(c.ui, card, 160, 4 + dy, "mt")
    if t >= over:
        stamp(c.ui, 160, 33, "OVERDUE", angle=-14, size=16, age=t - over)


# --- "Pardon me! Pardon me! Pardon me! Pardon me!" ----------------------------------------------------

SLAMS = [117.30, 118.64, 119.94, 121.16]
TURKEY_T0 = 116.62


def chanting_men(c):
    """Both defendants chant along, fists up on every "Pardon"."""
    k = pump(c.t, PARDONS, 0.35)
    for who in ("bibi", "trump"):
        c.hit_react[who] = False
        pose(c, who, arm="fist" if k > 0 else "point", far="down", mouth="wide" if k > 0.4 else "open",
             brows="up", eyes="squint" if who == "trump" else "open")


FREEZE = 0.9                            # how long the turkey stands caught after the last bang


def turkey_x(t):
    """The pardoned turkey struts in from the right, behind the desk, to the rostrum; at the last bang
    it freezes, turns round and tiptoes back out the way it came."""
    x0 = 345 - (min(t, QUIET) - TURKEY_T0) * 34
    return x0 if t < QUIET + FREEZE else x0 + (t - QUIET - FREEZE) * 55


def draw_turkey(c, img):
    x = turkey_x(c.t)
    if not -40 < x < 340:
        return
    gob = pump(c.t, PARDONS, 0.25) > 0
    frozen = QUIET <= c.t < QUIET + FREEZE
    leaving = c.t >= QUIET + FREEZE
    step = 0 if frozen else int(c.t * (3 if leaving else 5)) % 2
    spr = art.turkey(None, 1 if leaving else -1, gob and not (frozen or leaving))
    paste(img, spr, x, 146 - step * (2 if leaving else 1), "mb")


@gag("hook", 3)
def chant_one(c, L):
    chant(c, PARDONS, holders=LEFT)
    holders_hands(c, LEFT)
    chanting_men(c)
    c.gavel = list(SLAMS)
    yield "mid"
    draw_turkey(c, c.world)
    yield "front"
    placards(c, c.world, ("PARDON", "ME!"), PARDONS, holders=LEFT)
    yield "ui"
    for i, g in enumerate(SLAMS):
        order(c, c.ui, g, "ORDER" + "!" * (i + 1))


@gag("hook", 4, post=line_t("v3", 0) - 0.12 - V.TL.section_end("hook"))
def chant_two(c, L):
    t = c.t
    calm = t >= QUIET
    sit = ease_in_out(ramp(t, QUIET, QUIET + 0.25))
    late = 7                                          # one delegate keeps his placard up a beat too long
    late_up = 1.0 - ease_in_out(ramp(t, QUIET + 1.6, QUIET + 1.9))
    if not calm:
        chant(c, PARDONS, holders=LEFT)
        holders_hands(c, LEFT)
        if t < V.SWAPS[1][0]:
            chanting_men(c)
    else:
        for _, _, i in hall.DELEGATES:
            c.crowd["stand"][i] = (1 - sit) if i != late else max(1 - sit, late_up)
        c.crowd["react"][late] = 0.75 * late_up
        if t < V.SWAPS[1][0]:
            for who in ("bibi", "trump"):
                c.hit_react[who] = False
            if t < QUIET + 0.6:
                for who in ("bibi", "trump"):
                    pose(c, who, arm="down", far="down", eyes="wide", brows="up", mouth="o")
    c.gavel = list(SLAMS) + [QUIET]
    if QUIET <= t < QUIET + 0.15:
        c.add_shake(3)
    yield "mid"
    draw_turkey(c, c.world)
    yield "front"
    if not calm:
        placards(c, c.world, ("PARDON", "ME!"), PARDONS, holders=LEFT)
    else:
        placards(c, c.world, ("PARDON", "ME!"), [], up=1 - sit, late=(late, late_up), holders=LEFT)
    yield "ui"
    for i, g in enumerate(SLAMS):
        order(c, c.ui, g, "ORDER" + "!" * (i + 1))
    if QUIET <= t < QUIET + 1.2:
        age = t - QUIET
        dy = round((1 - back_out(min(1.0, age / 0.12))) * 6)
        bubble(c.ui, 204, 52 + dy, "ORDER!", tail=(166, 54), fnt=PRESS16, anchor="mb")

