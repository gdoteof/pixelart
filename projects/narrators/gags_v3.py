"""Verse 3: Sir David goes for the kill (doc mode, EPISODE TWO: EXTINCTION).

The documentary is back and it has done its homework: the Red List (Morgan drops from Least
Concern to Extinct in one diss), the Lucy lecture and an X-ray that confirms the ten
percent, Attenborosaurus, the sat-nav in a Ford Taurus, a nation off plastic against one Ford
rerouted to Tennessee, the pitcher plant that swallows rats (and Morgan), God twice for
Universal, the actual Crown, four planets on a shelf and God asleep after making one; then an
action replay of that couplet with a pundit's pen, seven worlds all flagged, the Se7en box, Hoke's
hands at ten and two, a grave pushing up daisies, the ageing male slinking into the long grass,
and a tender close-up to finish.
"""
from gagkit import (C, CH, INK, PRESS, PRESS16, PRESS24, SILK, H, W, ImageDraw, anchor, blend, blend_poly, char_at,
                    ease_in, ease_in_out, ease_out, gag, lerp, line_t, mask, math, mirror, pan, pixel, place, ramp,
                    scaled, ui_at, wt)
from critters import lion, rat
from props import bubble, crown, globe, label, pop_text, puff, sparkle, stamp
from sets import BACKSEAT
from v3_sets import (BRAIN_AT, CAVITY, FLUID_Y, JURA, PITCHER, PITCH, PLASTIC, SPLIT_X, TAURUS_NAV, WATER_Y, plastic,
                     plesiosaur, red_list, satnav_screen, turtle, xray)
from v3_sets2 import (CROWN_AT, EPITAPH_Y, EXTRA, GOD_SEAT, MOUND, PEN, SHELF_Y, SLOTS, STONE, WHEEL_C, WHEEL_R,
                      arc_letters, butterfly, cardboard_box, cloud_seat, daisy, pen_path, pen_ring, pen_text, planet,
                      spine, sword, vhs_tear, BOX)

BOOK_SHOT = (122, 128, 12)          # Sir David close, holding up the Red List
T_REPLAY = line_t("v3r", 0)


def hold_book(c, img, open_=False, stamped=False, dy=0):
    """The Red List in Sir David's near hand; returns where its centre is."""
    hx, hy = anchor(c, "david", "hand")
    b = red_list(open_, stamped)
    img.paste(b, (int(hx + 8 - b.width // 2), int(hy - b.height // 2 - 2 + dy)), b)
    return hx + 8, hy - 2 + dy


def streak(ui, x0, x1, y):
    """Speed lines trailing something that zips along to x1."""
    d = ImageDraw.Draw(ui)
    for k, dy in enumerate((-3, 0, 3)):
        d.line([(x0 + k * 4, y + dy), (x1 - 4, y + dy)], fill=(255, 255, 255, 255))


# --- "Quotin' Shawshank? Cute. You played Red. Well, I know the Red List," ------------------------

@gag("v3", 0, pre=0.12)
def red_list_out(c, L):
    played, red, red_list_t = wt(L, "played"), wt(L, "^Red", 0), wt(L, "^Red", 1)
    s = c.st["david"]
    if c.t >= wt(L, "Cute"):
        s["brows"] = "up"
    if played <= c.t < red_list_t:
        c.shot = (206, 98, 12)
        c.st["morgan"].update(outfit="prison", arm="cross", mouth="frown")
    elif c.t >= red_list_t:
        c.shot = BOOK_SHOT
        s["arm"] = "hold"
    yield "front"
    if c.t >= red_list_t:
        hold_book(c, c.world, dy=-int(6 * max(0.0, 1 - (c.t - red_list_t) / 0.12)))
    yield "ui"
    if red <= c.t < red_list_t:
        tx, ty = ui_at(c, 201, 120)
        CH.callout(c.ui, c.t - red, "AS RED, 1994", tx, ty, 252, 120)


# --- "And you just went from Least Concern to Extinct in one diss." ---------------------------------

@gag("v3", 1, pre=0.12)
def least_concern_to_extinct(c, L):
    opened, lc, ex, diss = wt(L, "just"), wt(L, "Least"), wt(L, "Extinct"), wt(L, "diss")
    c.shot = BOOK_SHOT
    s = c.st["david"]
    s["arm"] = "hold"
    shut = c.t < opened or c.t >= diss
    if c.t >= ex:
        s["brows"] = "angry"
    if 0 <= c.t - diss < 0.25:
        c.add_shake(9 * (1 - (c.t - diss) / 0.25))
    yield "front"
    bx, by = hold_book(c, c.world, open_=not shut, stamped=c.t >= ex + 0.35)
    puff(c.world, bx, by - 6, c.t - diss, size=0.8, seed=3, color=(236, 226, 210), drift=(0, -8), life=0.7)
    yield "ui"
    if c.t >= lc:
        k = ease_in(ramp(c.t, ex, ex + 0.32))
        level = 6 * k
        flash = 1.0 if 0 <= c.t - ex - 0.32 < 0.5 and int(c.t * 12) % 2 == 0 else 0.0
        CH.status_scale(c.ui, level, y=24, flash=flash)
        if 0.05 < k < 1:                                  # the marker zips across
            x = int(91 + round(level) * 20 + 9)
            streak(c.ui, x - 30, x - 9, 30)
        stamp(c.ui, 160, 62, "EXTINCT", color=C["red"], angle=-8, size=16, age=c.t - ex - 0.35)


# --- "You sold the world that Lucy myth, 'ten percent of the brain.'" -------------------------------

@gag("v3", 2, pre=0.12)
def lucy_lecture(c, L):
    sold, ten = wt(L, "sold"), wt(L, "ten")
    c.set_scene("v3_lecture", lit_at=ten)
    c.shot = "hall" if c.t < ten - 0.1 else "screen"
    m = c.st["morgan"]
    m.update(arm="point", brows="up", mouth="open" if int(c.t * 5) % 2 else "closed")
    yield "front"
    if c.t >= ten:
        age = c.t - ten
        lx, ly = BRAIN_AT[0] - 24 + round(math.sin(age * 23) * 1.5), BRAIN_AT[1] - 8
        d = ImageDraw.Draw(c.world)
        d.rectangle((lx - 1, ly - 1, lx + 1, ly + 1), fill=(255, 40, 40))       # the laser pointer
        d.point((lx, ly), fill=(255, 220, 220))
        if age > 0.25:
            pixel.text(c.world, (BRAIN_AT[0] + 32, BRAIN_AT[1] - 20), "10%", PRESS16, C["red"], shadow=None)
            pixel.text(c.world, (BRAIN_AT[0] + 32, BRAIN_AT[1] - 2), "IN USE", PRESS, (60, 56, 70), shadow=None)
    yield "ui"
    CH.lower_third(c.ui, c.t - sold, "PROF. MORGANUS FREEMANII", "LECTURING, UNPROVOKED", out_at=ten - sold - 0.3)


# --- "It's false, but every verse you spit's a strong case for the claim." -------------------------

@gag("v3", 3, pre=0.12)
def ten_percent_confirmed(c, L):
    false_t, every, strong, claim = wt(L, "false"), wt(L, "every"), wt(L, "strong"), wt(L, "claim")
    if c.t < every:
        c.set_scene("v3_lecture", lit_at=0.0)
        c.shot = "screen"
        c.st["morgan"].update(arm="point", mouth="o", brows="worried")
        yield "ui"
        sx, sy = ui_at(c, BRAIN_AT[0], BRAIN_AT[1] + 4)
        stamp(c.ui, sx, sy, "FALSE", color=C["red"], angle=-10, size=24, age=c.t - false_t)
        return
    c.shot = (224, 108, 18)
    c.inset = False
    c.st["morgan"].update(arm="cross", mouth="open" if int(c.t * 6) % 2 else "closed", eyes="half")
    yield "front"
    xray(c, lit=1.0 - 0.7 * ramp(c.t, claim, claim + 0.4), upto=lerp(76, 180, ramp(c.t, every, every + 0.6)))
    yield "ui"
    pixel.text(c.ui, (13, 24), "X-RAY", SILK, (170, 240, 255), shadow=INK)
    if c.t >= strong:
        x0, y0 = 196, 64
        CH.rect(c.ui, (x0 - 4, y0 - 4, x0 + 94, y0 + 20), "band")
        pixel.text(c.ui, (x0, y0 - 2), "BRAIN ACTIVITY", SILK, C["text"], shadow=None)
        pct = 10 if c.t < claim else max(2, int(round(10 - 8 * ramp(c.t, claim, claim + 0.4))))
        d = ImageDraw.Draw(c.ui)
        d.rectangle((x0, y0 + 8, x0 + 60, y0 + 14), outline=C["text"] + (255,))
        d.rectangle((x0 + 1, y0 + 9, x0 + 1 + int(58 * pct / 100), y0 + 13), fill=(255, 200, 60, 255))
        pixel.text(c.ui, (x0 + 65, y0 + 7), f"{pct}%", SILK, (255, 200, 60), shadow=None)
    stamp(c.ui, 236, 112, "CONFIRMED", color=(90, 220, 120), angle=-8, size=16, age=c.t - claim)


# --- "Wanna talk Jurassic? They named a beast for me: Attenborosaurus." ---------------------------

@gag("v3", 4, pre=0.12)
def attenborosaurus(c, L):
    jur, beast, name = wt(L, "Jurassic"), wt(L, "beast"), wt(L, "Attenboro")
    if c.t < jur:
        c.shot = "present"
        c.st["david"]["arm"] = "fist"
        return
    c.set_scene("v3_jurassic")
    c.shot = "sea" if c.t < beast else "beast"
    yield "back"
    rise = ease_out(ramp(c.t, beast - 0.45, beast + 0.25))
    spr = plesiosaur(mouth=c.t >= name and int(c.t * 6) % 2 == 0)
    x, base = 150, WATER_Y + 26
    top = int(base - spr.height + 44 * (1 - rise))
    c.world.paste(spr, (x - spr.width // 2, top), spr)
    under = mask(lambda m: m.rectangle((x - spr.width // 2 - 1, WATER_Y + 1, x + spr.width // 2 + 1, H), fill=255))
    blend(c.world, under, JURA["sea"], 0.62)                      # the sea over whatever is still in it
    if rise > 0:
        d = ImageDraw.Draw(c.world)
        nx = x + 20
        r = 6 + 10 * rise + 3 * math.sin(c.t * 4)
        d.arc((nx - r, WATER_Y - 2, nx + r, WATER_Y + 3), 180, 360, fill=JURA["sea_hi"])
        d.line([(nx - r - 4, WATER_Y + 1), (nx + r + 4, WATER_Y + 1)], fill=(236, 244, 240))
    yield "ui"
    CH.lower_third(c.ui, c.t - jur, "EARLY JURASSIC", "195 MILLION YEARS AGO", out_at=name - jur - 0.35)
    CH.lower_third(c.ui, c.t - name, "ATTENBOROSAURUS", "NAMED FOR SIR DAVID. SPOT THE HAIR.")


# --- "They put your voice in a sat-nav for some bloke in a Ford Taurus." --------------------------

@gag("v3", 5, pre=0.12)
def ford_taurus(c, L):
    voice, satnav, bloke, ford = wt(L, "voice"), wt(L, "sat-nav"), wt(L, "bloke"), wt(L, "Ford")
    c.set_scene("v3_taurus", nav_top="TURN LEFT")
    c.shot = "cab" if c.t < satnav or bloke <= c.t < ford else "nav" if c.t < bloke else "badge"
    yield "ui"
    if voice <= c.t < bloke:
        x0, y0, x1, _ = TAURUS_NAV
        ux, uy = ui_at(c, (x0 + x1) / 2, y0)
        bubble(c.ui, ux + 30, uy - 8, ["IN FOUR HUNDRED FEET,", "TURN LEFT."], tail=(ux + 4, uy + 2), fnt=SILK,
               line_h=8, text_dy=-2)
    if bloke <= c.t < ford:
        CH.callout(c.ui, c.t - bloke, "SOME BLOKE", 155, 12, 206, 30)
    CH.lower_third(c.ui, c.t - ford, "FORD TAURUS", "NOT TO BE CONFUSED WITH BOS TAURUS", y=26)


# --- "'Recalculating.' That's the legacy? That's the pedigree?" -----------------------------------

@gag("v3", 6, pre=0.12)
def recalculating(c, L):
    legacy, pedigree = wt(L, "legacy"), wt(L, "pedigree")
    lines = []
    if c.t >= legacy:
        lines.append(("LEGACY: NOT FOUND", (255, 110, 100)))
    if c.t >= pedigree:
        lines.append(("PEDIGREE: NOT FOUND", (255, 110, 100)))
    c.set_scene("v3_satnav", nav_top="RECALCULATING...", nav_lines=lines, nav_spin=True)
    c.shot = "nav" if c.t < pedigree else "close"
    yield "ui"


# --- "I got a nation off of plastic. You reroute a Ford to Tennessee." -----------------------------

@gag("v3", 7, pre=0.12)
def plastic_vs_tennessee(c, L):
    plastic_t, reroute, tenn = wt(L, "plastic"), wt(L, "reroute"), wt(L, "Tennessee")
    c.set_scene("v3_split")
    yield "front"
    img = c.world
    d = ImageDraw.Draw(img)
    for k, (x, y, kind) in enumerate(PLASTIC):
        gone = plastic_t + 0.08 * k
        if c.t < gone:
            spr = plastic(kind)
            img.paste(spr, (x - spr.width // 2, y - spr.height // 2 + round(math.sin(c.t * 3 + k))), spr)
        elif c.t < gone + 0.3:
            sparkle(img, x, y, 3 - int((c.t - gone) * 8), (255, 255, 255))
    if c.t >= plastic_t + 0.6:
        tu = turtle(int(c.t * 4) % 2)
        img.paste(tu, (int(-20 + (c.t - plastic_t - 0.6) * 60), 84), tu)
    # the Ford, and a route that should go home but swings off to Tennessee
    car = (SPLIT_X + 24, 150)
    d.rectangle((car[0] - 4, car[1] - 3, car[0] + 4, car[1] + 2), fill=(90, 140, 220))
    d.rectangle((car[0] - 2, car[1] - 5, car[0] + 2, car[1] - 3), fill=(150, 190, 240))
    home, tn = (SPLIT_X + 122, 146), (SPLIT_X + 108, 74)
    d.polygon([(home[0] - 5, home[1] - 2), (home[0], home[1] - 7), (home[0] + 5, home[1] - 2)], fill=C["red"], outline=INK)
    d.rectangle((home[0] - 4, home[1] - 2, home[0] + 4, home[1] + 4), fill=C["white"], outline=INK)
    k = ease_in_out(ramp(c.t, reroute, tenn))
    end = (lerp(home[0], tn[0], k), lerp(home[1], tn[1], k))
    mid = (lerp(car[0] + 30, car[0] + 60, k), lerp(car[1] - 10, 80, k))
    d.line([car, mid, end], fill=(230, 60, 160), width=3)
    if c.t >= tenn:
        drop = int(10 * (1 - ease_out(ramp(c.t, tenn, tenn + 0.15))))
        d.line([(tn[0], tn[1] - drop), (tn[0], tn[1] - 12 - drop)], fill=INK, width=1)
        d.ellipse((tn[0] - 4, tn[1] - 18 - drop, tn[0] + 4, tn[1] - 10 - drop), fill=(230, 50, 60), outline=INK)
    yield "ui"
    for x, name, colr in ((80, "SIR DAVID", C["docbar"]), (240, "MORGAN", (230, 60, 160))):
        tw = pixel.text_width(name, PRESS)
        CH.rect(c.ui, (x - tw // 2 - 4, 26, x + tw // 2 + 3, 37), "band")
        pixel.text(c.ui, (x - tw // 2, 28), name, PRESS, colr, shadow=None)
    if c.t >= plastic_t:
        label(c.ui, (80, 134), "A NATION OFF PLASTIC", anchor="mm")
    if c.t >= reroute:
        label(c.ui, (240, 134), "ONE FORD, REROUTED", anchor="mm")
    if c.t >= tenn:
        pop_text(c.ui, tn[0], tn[1] - 32, "TENNESSEE", c.t - tenn, fnt=PRESS, anchor="ma")


# --- "There's a pitcher plant that bears my name and swallows rats whole," ------------------------

@gag("v3", 8, pre=0.12)
def pitcher_eats_rat(c, L):
    bears, swallows, rats, whole = wt(L, "bears"), wt(L, "swallows"), wt(L, "rats"), wt(L, "whole")
    c.set_scene("v3_pitcher")
    c.shot = "plant" if c.t < swallows - 0.2 else "mouth"
    if 0 <= c.t - rats < 0.5:
        c.vars["lid"] = 0 if int((c.t - rats) * 14) % 2 else 2
    yield "front"
    px_, py_ = PITCHER
    # the rat scurries in, climbs the urn, teeters on the rim, and in it goes
    path = [(60, 150), (px_ - 30, 150), (px_ - 26, py_ - 40), (px_ - 12, py_ - 64), (px_, py_ - 56)]
    times = [L.t0 + 0.1, bears, swallows - 0.25, swallows + 0.2, rats]
    if c.t < rats:
        seg = min(len(times) - 2, sum(1 for tt in times[1:-1] if c.t >= tt))
        p = ramp(c.t, times[seg], times[seg + 1])
        x = lerp(path[seg][0], path[seg + 1][0], p)
        y = lerp(path[seg][1], path[seg + 1][1], p)
        r = rat(int(c.t * 8) % 2)
        if seg in (1, 2):
            r = r.rotate(60, expand=True)
        c.world.paste(r, (int(x - r.width / 2), int(y - r.height)), r)
    yield "ui"
    CH.lower_third(c.ui, c.t - bears, "NEPENTHES ATTENBOROUGHII", "CARNIVOROUS. NAMED FOR SIR DAVID.", y=26)
    mx, my = ui_at(c, px_ + 22, py_ - 66)
    pop_text(c.ui, mx, my - 8, "GULP", c.t - whole, fnt=PRESS16, anchor="ma")


# --- "And like the rat, Morgan, you're already slidin' down the bowl." ------------------------------

T_BOWL_OUT = line_t("v3", 10, "God") - 0.12            # the splash holds over the next line's "You played..."


@gag("v3", 9, pre=0.12, post=T_BOWL_OUT - (line_t("v3", 10) - 0.12))
def down_the_bowl(c, L):
    rat_t, morgan_t, slide, bowl = wt(L, "rat"), wt(L, "Morgan"), wt(L, "slidin"), wt(L, "bowl")
    c.set_scene("v3_pitcher_x")
    c.shot = "all"
    if c.t >= morgan_t:
        # already slipping, then gone: a slow creep down the waxy wall, faster from "slidin'"
        p = 0.18 * ramp(c.t, morgan_t, slide) + 0.82 * ease_in(ramp(c.t, slide, bowl))
        path = [(102, 66), (92, 98), (100, 126), (124, FLUID_Y + 4)]
        seg = min(2, int(p * 3))
        q = p * 3 - seg
        x = lerp(path[seg][0], path[seg + 1][0], q)
        y = lerp(path[seg][1], path[seg + 1][1], q)
        sunk = int(26 * ease_out(ramp(c.t, bowl, bowl + 0.4)))
        place(c, "morgan", x=x, y=y + sunk, facing=1, shadow=False, rot=0 if p < 0.02 else 24)
        c.st["morgan"].update(arm="up" if int(c.t * 6) % 2 else "wave", brows="worried", eyes="wide", mouth="o")
    yield "front"
    img = c.world
    rx = 186 + round(math.sin(c.t * 2) * 6)
    r = rat(int(c.t * 6) % 2)
    img.paste(r, (rx - r.width // 2, FLUID_Y - 5 + round(math.sin(c.t * 5))), r)
    if c.t >= bowl:                                         # the fluid closes over him
        m = mask(lambda mm: mm.polygon(CAVITY, fill=255))
        m[:FLUID_Y + 1] = 0
        blend(img, m, PITCH["fluid"], 0.8)
        a = c.t - bowl
        d = ImageDraw.Draw(img)
        for k in range(8):
            ang = math.pi * (0.1 + 0.8 * k / 7)
            v = 30 + 10 * (k % 3)
            sx = 124 + math.cos(ang) * v * a
            sy = FLUID_Y - math.sin(ang) * v * a + 90 * a * a
            if sy <= FLUID_Y and a < 0.8:
                d.rectangle((int(sx), int(sy), int(sx) + 1, int(sy) + 1), fill=PITCH["fluid_hi"])
    yield "ui"
    ux, uy = ui_at(c, rx, FLUID_Y - 8)
    CH.callout(c.ui, c.t - rat_t, "THE RAT", ux, uy, ux + 22, uy - 28)
    if morgan_t <= c.t < bowl + 0.3:
        mx, my = ui_at(c, *anchor(c, "morgan", "top"))
        CH.callout(c.ui, c.t - morgan_t, "MORGAN", mx, my, mx + 46, my + 20)
    gx, gy = ui_at(c, 124, FLUID_Y - 30)
    pop_text(c.ui, gx, gy, "GULP", c.t - bowl - 0.1, fnt=PRESS16, anchor="ma")


# --- "You played God twice, Bruce then Evan, both for Universal." -------------------------------------

GODS = ((92, 136), (228, 136))
LOGO = (160, 84)
T_LOGO_OUT = line_t("v3", 11, "got") - 0.28          # the logo holds over the next line's "I..."


def glow(img, x, y, r, color=(255, 246, 214), alpha=0.1):
    """A soft halo of light, in flat steps."""
    for k in range(3):
        rr = r * (1 - k * 0.28)
        blend(img, mask(lambda m: m.ellipse((x - rr, y - rr * 1.2, x + rr, y + rr * 1.2), fill=255)), color, alpha)


@gag("v3", 10, pre=0.12, post=T_LOGO_OUT - (line_t("v3", 11) - 0.12))
def god_twice(c, L):
    if c.t < T_BOWL_OUT:
        return
    god, twice, bruce, evan = wt(L, "God"), wt(L, "twice"), wt(L, "Bruce"), wt(L, "Evan")
    both, for_ = wt(L, "both"), wt(L, "for")
    c.set_scene("v3_space")
    pan(c, "gods", "logo", both, 0.4)
    (x1, y1), (x2, y2) = GODS
    bob = round(math.sin(c.t * 2.6) * 1.5)
    arm = "up" if c.t >= both else "palm"
    place(c, "morgan", x=x1, y=y1 + bob, facing=1, outfit="god", shadow=False, hidden=c.t < god)
    c.st["morgan"].update(arm=arm, mouth="smile", brows="up", eyes="open")
    yield "back"
    img = c.world
    if c.t >= god:
        glow(img, x1 + 2, y1 - 26, 24)
    if c.t >= twice:
        glow(img, x2 - 2, y2 - 26, 24)
        char_at(img, "morgan", x2, y2 - bob, facing=-1, outfit="god", arm=arm, mouth="smile", brows="up")
    rise = ease_out(ramp(c.t, both, for_ + 0.1))
    if rise > 0:
        g = globe(26, int(c.t * 6) % 16)
        img.paste(g, (LOGO[0] - g.width // 2, int(lerp(H + 30, LOGO[1], rise)) - g.height // 2), g)
    yield "ui"
    for (x, y), name, year, t0 in ((GODS[0], "BRUCE", "2003", bruce), (GODS[1], "EVAN", "2007", evan)):
        ux, uy = ui_at(c, x, y - 64)
        pop_text(c.ui, ux, uy, name, c.t - t0, fnt=PRESS, anchor="ma")
        if c.t >= t0 + 0.12:
            pixel.text(c.ui, (ux, uy + 11), year, SILK, C["text"], shadow=INK, anchor="ma")
    gx, gy = ui_at(c, *LOGO)
    r = 26 * c.cam.k / 6
    arc_letters(c.ui, "UNIVERSAL", gx, gy + 6, r + 44, 7, math.pi - 0.25, 0.25, c.t - for_, fnt=PRESS16)


# --- "I got knighted twice by the actual Crown, and that weren't a rehearsal." -------------------------

def keyframe(t, keys):
    """Ease between (time, (x, y)) keys."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t < t1:
            q = ease_in_out(ramp(t, t0, t1))
            return lerp(p0[0], p1[0], q), lerp(p0[1], p1[1], q)
    return keys[-1][1]


@gag("v3", 11, pre=0.12)
def the_actual_crown(c, L):
    if c.t < T_LOGO_OUT:
        return
    kn, tw, actual, crown_t, that, reh = (wt(L, p) for p in ("knighted", "twice", "actual", "Crown", "that",
                                                              "rehearsal"))
    c.set_scene("v3_throne")
    if actual - 0.1 <= c.t < that:
        pan(c, "knight", "crown", actual - 0.1, 0.3)
    else:
        c.shot = "knight"
    yield "front"
    img = c.world
    hx, hy = anchor(c, "david", "head")
    cx, cy = CROWN_AT[0], CROWN_AT[1] + round(math.sin(c.t * 3) * 2)
    cr = scaled(crown(14), 2)
    img.paste(cr, (cx - cr.width // 2, cy - cr.height // 2), cr)
    if (c.t * 2.5) % 1.0 < 0.3:
        sparkle(img, cx + 9, cy - 8, 2, (255, 255, 255))
    # the sword: raised, a tap on one shoulder, over the head, the other shoulder, raised again
    up, a, over, b = (hx + 12, hy - 16), (hx - 1, hy + 13), (hx - 2, hy - 18), (hx - 7, hy + 12)
    tip = keyframe(c.t, [(kn - 0.3, up), (kn, a), (kn + 0.12, (hx + 8, hy - 6)), (tw - 0.12, over), (tw, b),
                         (tw + 0.25, over), (tw + 0.6, up)])
    sword(img, tip, (cx + 4, cy + 8))
    yield "ui"
    for t0, year, (px_, py_) in ((kn, "1985", (hx - 22, hy - 21)), (tw, "2022", (hx + 22, hy - 21))):
        if c.t < actual - 0.1:
            ux, uy = ui_at(c, px_, py_)
            pop_text(c.ui, ux, uy, year, c.t - t0, fnt=PRESS16, anchor="ma")
    if crown_t <= c.t < that:
        ux, uy = ui_at(c, cx, cy + 10)
        CH.callout(c.ui, c.t - crown_t, "THE ACTUAL CROWN", ux, uy, ux - 50, 128)
    stamp(c.ui, 164, 104, "NOT A REHEARSAL", color=C["red"], angle=-6, size=16, age=c.t - reh)


# --- "Blue, Frozen, Green and Earth: four planets on my shelf." ----------------------------------------

@gag("v3", 12, pre=0.12)
def four_planets(c, L):
    words = [wt(L, w) for w in ("Blue", "Frozen", "Green", "Earth")]
    four, shelf = wt(L, "four"), wt(L, "shelf")
    c.set_scene("v3_study", planets=sum(c.t >= w for w in words))
    for k, w in enumerate(words):
        c.vars[f"drop{k}"] = 14 * (1 - ease_out(ramp(c.t, w, w + 0.14)))
    pan(c, "shelf", "room", four, 0.35)
    c.st["david"]["hidden"] = c.t < four                     # the collector steps in for the wide
    yield "front"
    for k, w in enumerate(words):
        if 0 <= c.t - w < 0.3:
            sparkle(c.world, SLOTS[k] + 7, SHELF_Y - 40, 3 - int((c.t - w) * 8), (255, 255, 255))
    if shelf <= c.t < shelf + 0.45:                          # a gleam runs along the shelf
        x = lerp(10, 310, ramp(c.t, shelf, shelf + 0.45))
        blend_poly(c.world, [(x, 48), (x + 8, 48), (x - 4, 104), (x - 12, 104)], (255, 250, 220), 0.4)


# --- "You made one, Morgan, then you had to take a nap yourself." --------------------------------------

def nap(c, one, had, take, nap_t):
    """God's day off: Morgan-God on his cloud holds up the one planet he made, yawns, and flops."""
    c.set_scene("v3_space")
    c.hit_react["morgan"] = False
    c.inset = False
    x, y = GOD_SEAT
    m = c.st["morgan"]
    down = c.t >= take + 0.22
    if down:
        place(c, "morgan", x=x - 16, y=y - 6, body="lie", facing=1, outfit="god", shadow=False)
        m.update(eyes="shut", mouth="o" if int(c.t * 1.5) % 2 else "closed")
    else:
        place(c, "morgan", x=x, y=y, body="sit", facing=1, outfit="god", shadow=False,
              rot=40 * ease_in(ramp(c.t, take, take + 0.22)))
        m.update(arm="hold" if c.t >= one else "palm", eyes="half" if c.t >= had else "open", brows="neutral",
                 mouth="wide" if had <= c.t < had + 0.4 else "smile")
    cloud = cloud_seat()
    yield "back"
    if down:
        c.world.paste(cloud, (x - cloud.width // 2, y - cloud.height + 4), cloud)
    yield "mid"
    if not down:
        c.world.paste(cloud, (x - cloud.width // 2 + 2, y - cloud.height + 6), cloud)
    yield "front"
    if c.t >= one:                                           # the one planet he made
        g = globe(4, int(c.t * 4) % 16)
        if down:
            px_, py_ = x - 36, y - 16 + round(math.sin(c.t * 2) * 2)
        else:
            hx, hy = anchor(c, "morgan", "hand")
            px_, py_ = hx + 2, hy - 7 - 4 * (1 - ease_out(ramp(c.t, one, one + 0.15)))
        c.vars["planet_at"] = (px_, py_)
        c.world.paste(g, (int(px_ - g.width / 2), int(py_ - g.height / 2)), g)
        if c.t - one < 0.3:
            sparkle(c.world, int(px_ + 5), int(py_ - 5), 3 - int((c.t - one) * 8), (255, 255, 255))
    yield "ui"
    if c.t >= nap_t:                                         # z z Z
        hx, hy = ui_at(c, *anchor(c, "morgan", "top"))
        for k, fnt in enumerate((SILK, PRESS, PRESS16)):
            if c.t - nap_t >= k * 0.22:
                age = (c.t - nap_t - k * 0.22) % 1.2
                pixel.text(c.ui, (int(hx + 2 + age * 8 + k * 8), int(hy - 12 - age * 10 - k * 12)), "Z", fnt,
                           (230, 230, 255), shadow=INK)


@gag("v3", 13, pre=0.12)
def god_needs_a_nap(c, L):
    if c.t >= T_REPLAY - 0.12:                               # the action replay takes over from here
        return
    one, had, take, nap_t = wt(L, "one"), wt(L, "had"), wt(L, "take"), wt(L, "nap")
    c.set_scene("v3_space")
    pan(c, "cloud", "nap", nap_t - 0.2, 0.3)
    yield from nap(c, one, had, take, nap_t)


# --- the action replay (v3r): the same couplet again, rewound and marked up by a pundit's pen ------------

T12, T13 = line_t("v3", 12), line_t("v3", 13)
NAP13 = tuple(line_t("v3", 13, p) for p in ("one", "had", "take", "nap"))
REW = 0.42                                                   # how long the tape rewinds
SHIFT = T_REPLAY - T12                                       # replay time -> the original's time


def replay_screen(c, t_src, rewinding):
    """The replay's screen furniture: the viewfinder showing the original's clock (spinning back while the
    tape rewinds), and a tag. Call in the "ui" phase after setting c.hud = c.rec = False."""
    CH.viewfinder(c.ui, t_src, rec=False)
    if rewinding:
        pixel.text(c.ui, (12, 12), "REW", PRESS, C["text"], shadow=INK)
        d = ImageDraw.Draw(c.ui)
        d.polygon([(44, 15), (49, 12), (49, 19)], fill=C["text"] + (255,))
        d.polygon([(50, 15), (55, 12), (55, 19)], fill=C["text"] + (255,))
    else:
        CH.vhs_rewind(c.ui, c.t, 0.5)


@gag("v3r", 0, pre=0.12)
def replay_shelf(c, L):
    worlds, one, wonders, all_ = wt(L, "Worlds"), wt(L, "One"), wt(L, "wonders"), wt(L, "all")
    seven = wt(L, "seven", 1)
    t_rew0 = L.t0 - 0.12
    rewinding = c.t < t_rew0 + REW
    c.hud = c.rec = c.inset = False
    if c.t < L.t0:                                           # the tape runs back through the nap...
        c.shot = "nap"
        yield from nap(c, *NAP13)
    else:                                                    # ...to the shelf, and plays it again
        c.set_scene("v3_study", planets=4)
        c.shot = "wide"
        yield "ui"
    if rewinding:
        vhs_tear(c.world, c.t, 1.0 - 0.6 * ramp(c.t, t_rew0 + REW - 0.15, t_rew0 + REW))
    p = ramp(c.t, t_rew0, t_rew0 + REW)
    replay_screen(c, lerp(t_rew0, T12, p) if rewinding else c.t - SHIFT, rewinding)
    if rewinding:
        return
    ui = c.ui
    for k, x in enumerate(SLOTS):                            # the pundit counts them: 1 2 3 4...
        ux, uy = ui_at(c, x - 3, SHELF_Y - 62)
        pen_text(ui, ux, uy, str(k + 1), c.t - worlds - k * 0.09)
    ex, ey = ui_at(c, SLOTS[3], SHELF_Y - 30)                # ...rings the one planet...
    pen_ring(ui, ex, ey, 17, 25, ramp(c.t, one, one + 0.3), seed=4)
    for k, x in enumerate(EXTRA):                            # ...and draws in three more: 5 6 7
        t0 = seven + k * 0.1
        px_, py_ = ui_at(c, x, SHELF_Y - 36)
        pen_ring(ui, px_, py_, 9, 9, ramp(c.t, t0, t0 + 0.14), seed=k)
        pen_path(ui, [(px_ - 7, py_ + 12), (px_ + 7, py_ + 12), (px_ + 3, py_ + 22), (px_ - 3, py_ + 22),
                      (px_ - 7, py_ + 12)], ramp(c.t, t0 + 0.08, t0 + 0.22))
        pen_text(ui, px_ - 3, py_ - 26, str(k + 5), c.t - t0)
    if c.t >= wonders:
        for k, x in enumerate(SLOTS + EXTRA):
            if (c.t * 3 + k * 0.37) % 1.0 < 0.4:
                sparkle(ui, *ui_at(c, x + 8, SHELF_Y - 44), 2, PEN)
    x0, y0 = ui_at(c, 26, SHELF_Y + 3)                       # all of them, on the shelf
    x1, _ = ui_at(c, 312, SHELF_Y + 3)
    pen_path(ui, [(x0, y0 + 1), (x1, y0 - 1)], ramp(c.t, all_, all_ + 0.35), width=3)
    pen_text(ui, 30, SHELF_Y + 24, "ALL 7, ON MY SHELF", c.t - all_ - 0.05, cps=40)


@gag("v3r", 1, pre=0.12)
def replay_nap(c, L):
    if c.t >= line_t("v3", 14) - 0.12:
        return
    one, morgan_t, then, take, nap_t = (wt(L, p) for p in ("one", "Morgan", "then", "take", "nap"))
    c.hud = c.rec = c.inset = False
    c.shot = "cloud"
    yield from nap(c, one, wt(L, "had"), take, nap_t)
    replay_screen(c, c.t - (L.t0 - T13), False)
    ui = c.ui
    if c.t >= one:                                           # this one planet, here
        gx, gy = ui_at(c, *c.get("planet_at"))
        pen_ring(ui, gx, gy, 12, 12, ramp(c.t, one, one + 0.25), seed=2)
        pen_text(ui, gx + 12, gy - 22, "1", c.t - one)
    if morgan_t <= c.t < take:                               # this fella
        hx, hy = ui_at(c, *anchor(c, "morgan", "head"))
        pen_path(ui, [(hx - 64, hy + 14), (hx - 40, hy + 6), (hx - 16, hy + 2)], ramp(c.t, morgan_t, morgan_t + 0.25))
        pen_text(ui, hx - 100, hy + 8, "GOD", c.t - morgan_t - 0.1)
    if c.t >= nap_t:                                         # and down he goes
        hx, hy = ui_at(c, *anchor(c, "morgan", "head"))
        pen_ring(ui, hx, hy, 22, 18, ramp(c.t, nap_t, nap_t + 0.3), seed=7)
        pen_text(ui, hx + 26, hy + 16, "NAP", c.t - nap_t - 0.15, fnt=PRESS16)


# --- "Seven Worlds, One Planet: seven wonders, all of 'em mine." ----------------------------------------

EARTH_AT, EARTH_R = (160, 152), 30
ORBIT = (160, 104, 136, 30)                                  # centre and radii of the seven worlds' orbit
WORLD_KINDS = ("blue", "frozen", "green", "sand", "lava", "gas", "earth")


def worlds_at(t):
    cx, cy, rx, ry = ORBIT
    out = []
    for k, kind in enumerate(WORLD_KINDS):
        a = t * 0.5 + k * 2 * math.pi / 7
        out.append((k, kind, cx + math.cos(a) * rx, cy + math.sin(a) * ry, math.sin(a) >= 0))
    return out


def little_flag(img, x, y, color=C["red"]):
    d = ImageDraw.Draw(img)
    d.line([(x, y), (x, y - 9)], fill=INK)
    d.polygon([(x + 1, y - 9), (x + 7, y - 7), (x + 1, y - 5)], fill=color, outline=INK)


@gag("v3", 14, pre=0.12)
def seven_worlds(c, L):
    worlds, one, all_, mine = wt(L, "Worlds"), wt(L, "One"), wt(L, "all"), wt(L, "mine")
    seven = wt(L, "seven", 1)
    c.set_scene("v3_space")
    c.st["morgan"]["hidden"] = True
    place(c, "david", x=EARTH_AT[0] - 4, y=EARTH_AT[1] - EARTH_R, facing=1, mic="fluffy", shadow=False)
    if c.t >= mine:
        c.st["david"].update(arm="hold", gesture=False, brows="up")
    pan(c, "gods", "mine", mine - 0.1, 0.25)
    if 0 <= c.t - mine < 0.2:
        c.add_shake(5)
    orbit = worlds_at(c.t)

    def draw_world(img, k, kind, x, y):
        g = planet(kind, 6, int(c.t * 3 + k * 2) % 16)
        img.paste(g, (int(x - g.width / 2), int(y - g.height / 2)), g)
        if c.t >= seven + k * 0.06 and (c.t * 4 + k * 0.3) % 1.0 < 0.3:
            sparkle(img, int(x + 5), int(y - 5), 2, (255, 255, 255))
        if c.t >= all_ + k * 0.06:
            little_flag(img, int(x), int(y - 6))

    yield "back"
    for k, kind, x, y, front in orbit:
        if not front:
            draw_world(c.world, k, kind, x, y)
    if c.t >= one:
        glow(c.world, EARTH_AT[0], EARTH_AT[1] - 4, 44, (140, 190, 255), 0.06)
    g = globe(EARTH_R, int(c.t * 2) % 16)
    c.world.paste(g, (EARTH_AT[0] - g.width // 2, EARTH_AT[1] - g.height // 2), g)
    yield "front"
    for k, kind, x, y, front in orbit:
        if front:
            draw_world(c.world, k, kind, x, y)
    if c.t >= mine:                                          # and his flag, in his planet
        fx, fy = int(anchor(c, "david", "hand")[0]) + 1, EARTH_AT[1] - EARTH_R + 4
        up = ease_out(ramp(c.t, mine, mine + 0.15))
        top = int(fy - 30 * up)
        d = ImageDraw.Draw(c.world)
        d.line([(fx, fy), (fx, top)], fill=INK, width=2)
        if up >= 1:
            wave = round(math.sin(c.t * 8))
            d.polygon([(fx + 1, top), (fx + 30, top + 1 + wave), (fx + 30, top + 12 + wave), (fx + 1, top + 11)],
                      fill=C["white"], outline=INK)
            pixel.text(c.world, (fx + 16, top + 2 + wave), "MINE", SILK, C["red"], shadow=None, anchor="ma")
    yield "ui"
    CH.lower_third(c.ui, c.t - worlds, "SEVEN WORLDS", "ONE PLANET. ONE OWNER.", out_at=mine - worlds - 0.3)


# --- "You made Seven. What's in the box, Morgan? It's your spine." -------------------------------------

@gag("v3", 15, pre=0.12)
def whats_in_the_box(c, L):
    seven, what, morgan_t, its, spine_t = (wt(L, p) for p in ("Seven", "What", "Morgan", "It's", "spine"))
    c.set_scene("v3_desert")
    pan(c, "wide", "box", what, 0.6)
    m = c.st["morgan"]
    if c.t >= spine_t:                                       # no spine: down he goes
        place(c, "morgan", x=150, y=156, body="lie", facing=1, hat="fedora")
        m.update(eyes="shut", mouth="o")
    else:
        m.update(arm="hold" if c.t >= morgan_t else "down", brows="worried",
                 eyes="wide" if c.t >= its else "open", mouth="o" if c.t >= its else "frown")
    yield "front"
    img = c.world
    opened = 0 if c.t < morgan_t else 1 if c.t < morgan_t + 0.2 else 2
    bx, by = BOX
    box = cardboard_box(opened)
    img.paste(box, (bx - 14, by - box.height + 2), box)
    if opened == 2:                                          # something in there glows
        blend_poly(img, [(bx - 10, by - 18), (bx + 12, by - 22), (bx + 30, by - 70), (bx - 24, by - 70)],
                   (255, 240, 190), 0.18 + 0.06 * math.sin(c.t * 9))
    if c.t >= its:                                           # and up it rises
        sp = spine()
        rise = ease_out(ramp(c.t, its, spine_t + 0.1))
        img.paste(sp, (bx - sp.width // 2 + 1, int(by - 18 - 30 * rise)), sp)
        if (c.t * 5) % 1.0 < 0.4:
            sparkle(img, bx + 8, int(by - 40 - 30 * rise), 2, (255, 255, 255))
    if c.t >= spine_t:
        puff(img, 150, 156, c.t - spine_t, size=0.8, seed=9, color=(232, 214, 170), drift=(0, -6), life=0.8)
    yield "ui"
    if seven <= c.t < what + 0.1:                           # the title, a little shaky
        a = c.t - seven
        jx, jy = round(math.sin(c.f * 2.3) * 1), round(math.cos(c.f * 1.7) * 1)
        pixel.text(c.ui, (160 + jx, 40 + jy - int(6 * max(0.0, 1 - a / 0.1))), "SE EN", PRESS24, C["text"],
                   shadow=INK, anchor="ma")
        pixel.text(c.ui, (160 + jx, 40 + jy - int(6 * max(0.0, 1 - a / 0.1))), "7", PRESS24, C["red"],
                   shadow=INK, anchor="ma")


# --- "You were Hoke in Driving Miss Daisy, hands at ten and two." --------------------------------------

def miss_daisy(img, x, y):
    """Miss Daisy herself, in the back seat: a daisy in a pot, in her pearls."""
    d = ImageDraw.Draw(img)
    d.polygon([(x - 5, y - 8), (x + 5, y - 8), (x + 4, y), (x - 4, y)], fill=(190, 100, 70), outline=INK)
    d.line([(x, y - 8), (x - 1, y - 30)], fill=(70, 140, 60), width=2)
    d.line([(x - 1, y - 18), (x - 6, y - 22)], fill=(70, 140, 60))
    for k in range(10):
        a = k * math.pi / 5
        d.ellipse((x - 1 + math.cos(a) * 5 - 2, y - 36 + math.sin(a) * 5 - 2, x - 1 + math.cos(a) * 5 + 2,
                   y - 36 + math.sin(a) * 5 + 2), fill=(252, 252, 252), outline=INK)
    d.ellipse((x - 4, y - 39, x + 2, y - 33), fill=(246, 200, 50), outline=INK)
    for k in range(5):                                       # her pearls
        d.point((x - 4 + k * 2, y - 26 + abs(k - 2) // 2), fill=(250, 246, 236))


@gag("v3", 16, pre=0.12)
def ten_and_two(c, L):
    hoke, daisy_t, hands, ten, two = (wt(L, p) for p in ("Hoke", "Daisy", "hands", "ten", "two"))
    if c.t < hands:
        c.set_scene("car")
        c.st["david"]["hidden"] = True
        c.shot = "car"
        yield "back"
        miss_daisy(c.world, BACKSEAT[0] + 2, BACKSEAT[1] - 12)
        yield "ui"
        CH.lower_third(c.ui, c.t - hoke, "HOKE COLBURN", "DRIVING MISS DAISY, 1989", y=26, out_at=daisy_t - hoke - 0.3)
        ux, uy = ui_at(c, BACKSEAT[0], BACKSEAT[1] - 50)
        CH.callout(c.ui, c.t - daisy_t, "MISS DAISY", ux, uy, ux + 50, uy - 26)
        return
    c.set_scene("v3_wheel")
    c.shot = "wheel"
    yield "ui"
    cx, cy = WHEEL_C
    shown = {10: ten, 11: lerp(ten, two, 0.3), 12: lerp(ten, two, 0.55), 1: lerp(ten, two, 0.8), 2: two,
             9: two + 0.08, 3: two + 0.08}
    for n, t0 in shown.items():                              # the wheel is a clock, ticking from ten to two
        a = math.radians(n * 30)
        x, y = ui_at(c, cx + (WHEEL_R + 14) * math.sin(a), cy - (WHEEL_R + 14) * math.cos(a))
        if n in (10, 2):
            pop_text(c.ui, x, y - 8, str(n), c.t - t0, fnt=PRESS16, anchor="ma")
        elif c.t >= t0:
            pixel.text(c.ui, (x, y - 4), str(n), PRESS, C["text"], shadow=INK, anchor="ma")


# --- "Next stop: pushin' up daisies. Don't fret, mate. I'll narrate you." -------------------------------

DAISIES = ((-27, 2, 15), (-16, -1, 21), (-6, 3, 17), (5, -2, 24), (16, 1, 18), (27, -1, 22))


@gag("v3", 17, pre=0.12)
def pushing_up_daisies(c, L):
    stop, push, daisies, dont, mate, narrate = (wt(L, p) for p in ("Next", "pushin", "daisies", "Don't", "mate",
                                                                   "narrate"))
    c.set_scene("v3_grave")
    c.shot = "wide" if c.t < push else "stone" if c.t < dont else "both"
    dv = c.st["david"]
    dv["hidden"] = c.t < dont
    if c.t >= mate:
        dv.update(arm="palm" if c.t < narrate else "down", brows="up")
    yield "front"
    img = c.world
    mx, my = MOUND
    for k, (dx, dy, h) in enumerate(DAISIES):                # up they come, in time-lapse
        t0 = push + k * 0.045
        if c.t >= t0:
            grow = ease_out(ramp(c.t, t0, t0 + 0.28))
            spr = daisy(max(1, int(h * grow)), c.t >= daisies - 0.04 + k * 0.02)
            img.paste(spr, (mx + dx - 4, my + dy - spr.height + 2), spr)
    if c.t >= narrate:                                       # the stonemason adds a credit
        x = STONE[0]
        pixel.text(img, (x, EPITAPH_Y), "NARRATED BY", SILK, (60, 58, 70), shadow=None, anchor="ma")
        pixel.text(img, (x, EPITAPH_Y + 9), "SIR DAVID", SILK, (60, 58, 70), shadow=None, anchor="ma")
        if c.t - narrate < 0.35:
            sparkle(img, x + 28, EPITAPH_Y + 4, 3 - int((c.t - narrate) * 8), (255, 255, 255))
    yield "ui"
    if stop <= c.t < daisies + 0.4:                          # his own voice, announcing it
        w, h = 84, 50
        scr = satnav_screen(w, h, c.t, top="NEXT STOP:", face=1, lines=[("CEMETERY", (255, 110, 100))])
        x0, y0 = 16, 26 - int(40 * (1 - ease_out(ramp(c.t, stop, stop + 0.15))))
        CH.rect(c.ui, (x0 - 3, y0 - 3, x0 + w + 2, y0 + h + 2), "band")
        c.ui.paste(scr, (x0, y0))
    if push <= c.t < dont:                                   # the nature doc's favourite trick
        x = 22 + pixel.text_width("TIME-LAPSE", SILK)
        CH.rect(c.ui, (19, 128, x + 17, 139), "band")
        pixel.text(c.ui, (22, 130), "TIME-LAPSE", SILK, C["text"], shadow=None)
        d = ImageDraw.Draw(c.ui)
        for ax in (x + 3, x + 9):
            d.polygon([(ax, 130), (ax + 4, 133), (ax, 136)], fill=C["text"] + (255,))


# --- "And so, the ageing male, outcompeted, slinks back into the long grass." --------------------------

@gag("v3", 18, pre=0.12)
def the_long_grass(c, L):
    ageing, out, slinks, grass = (wt(L, p) for p in ("ageing", "outcompeted", "slinks", "grass"))
    c.set_scene("v3_dusk")
    c.shot = "plain" if c.t < slinks else "grass"
    m = c.st["morgan"]
    walk = c.t < out
    x = 186 + 4 * (c.t - L.t0) if walk else 186 + 4 * (out - L.t0) - 26 * ease_in_out(ramp(c.t, slinks, grass))
    sink = 26 * ease_in(ramp(c.t, slinks + 0.2, grass + 0.1))
    place(c, "morgan", x=x, y=158, dy=sink, facing=1 if walk else -1, shadow=False,
          body=("walk1" if int(c.t * 3) % 2 else "walk2") if walk else "stand" if c.t < slinks else "crouch")
    m.update(arm="down" if walk else "palm" if c.t < slinks else "down", brows="worried",
             eyes="half" if walk else "wide", mouth="closed" if walk else "o", lean=1 if walk else 0)
    dv = c.st["david"]
    dv.update(gesture=False, arm="down", eyes="side" if c.t < out else "open")
    yield "mid"
    if c.t >= out - 0.5:                                     # the new male arrives, and says so
        lx = lerp(W + 10, 268, ease_out(ramp(c.t, out - 0.5, out)))
        roar = out <= c.t < out + 0.5
        spr = mirror(lion("roar" if roar else "shut"))
        c.world.paste(spr, (int(lx - spr.width / 2), 160 - spr.height), spr)
        if roar:
            c.add_shake(3)
    yield "front"
    if c.t >= grass:                                         # all that's left: a butterfly
        a = c.t - grass
        bx = 160 + a * 10 + math.sin(a * 6) * 4
        by = 146 - a * 14 + math.sin(a * 9) * 2
        spr = butterfly(int(c.t * 8) % 2)
        c.world.paste(spr, (int(bx), int(by)), spr)
    yield "ui"
    CH.lower_third(c.ui, c.t - ageing, "MORGANUS FREEMANII", "ADULT MALE. AGEING.", y=26, out_at=out - ageing - 0.3)


# --- "It isn't cruelty. It is simply nature." ----------------------------------------------------------

@gag("v3", 19, pre=0.12)
def simply_nature(c, L):
    cruelty, simply, nature = wt(L, "cruelty"), wt(L, "simply"), wt(L, "nature")
    c.set_scene("v3_dusk", sun=(80, 116), tree=300)
    c.st["morgan"]["hidden"] = True
    place(c, "david", x=70, y=160, body="stand", facing=1, mic="fluffy", z=1, shadow=False, gesture=False, arm="down",
          rim=0.7, rim_color=(255, 196, 120))
    dv = c.st["david"]
    dv.update(eyes="half" if c.t < simply else "open", brows="worried" if c.t < simply else "neutral")
    if c.t >= nature + 0.25:
        dv["mouth"] = "smile"
    c.shot = (72, 126, 24)
    c.inset = False
    yield "front"
    img = c.world
    ex, ey = anchor(c, "david", "eye")
    if c.t >= cruelty + 0.1:                                 # one tear
        ty = ey + 2 + min(9.0, (c.t - cruelty - 0.1) * 8)
        ImageDraw.Draw(img).rectangle((ex - 1, int(ty), ex - 1, int(ty) + 1), fill=(170, 220, 255))
    mx, my = anchor(c, "david", "mic")                       # and a butterfly settles on the mic
    land = ease_out(ramp(c.t, L.t0, simply))
    bx, by = lerp(mx + 40, mx - 3, land) + math.sin(c.t * 7) * 3 * (1 - land), lerp(my - 30, my - 9, land)
    spr = butterfly(int(c.t * (8 if land < 1 else 1.5)) % 2)
    img.paste(spr, (int(bx), int(by)), spr)
