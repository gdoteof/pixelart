"""Verse 2: Morgan's film, THE BBC REDEMPTION (v2 0-21).

Sir David has done seventy years inside the BBC: the new fish in the yard, the cell he gets used to,
the parole he won't take, the mugshot. Then Morgan's credentials against his: the young buck, the
cave-painted baby pictures, a century of tunnelling, the fossil in the museum, the gorilla that
snitches, the light switch, the creation line, Dickie's park, the awards shelf, the ship the nation
named, the comet, the T-rex, the stolen title and crown, and London falling.
"""
from critters import bird, gorilla, lion, penguin, rat, trex
from gagkit import (BAR, C, CH, INK, PRESS, PRESS16, SILK, H, W, Canvas, Image, ImageDraw, anchor, arc_pt, back_out,
                    between, blend, blend_poly, ease_in, ease_in_out, ease_out, gag, lerp, lru_cache, mask, math, mirror,
                    paste, paste_rot, pixel, place, ramp, rnd, scaled, shot_of, text_width, ui_at, wt)
from props import big_text, bubble, crown, label, pop_text, puff, sparkle, stamp, strike, teacup
from sets import leaf_blob
from v2_art import (AT_BARS, BELT_SPEED, BELT_TOP, BEN, BUNK_SEAT, CALENDAR, CHUTE_X, CRET_FLOOR, GATE_FLOOR,
                    GOD_AT_BELT, MUSEUM_FLOOR, SWITCH, PADDOCK_FLOOR, POSTER, STAGE_FLOOR, STATUE, WINDOW, antlers, ash_world,
                    big_ben, boxing_baby, brass_plate, cake, calendar, calendar_page, comet, deckchair, dickie, fish,
                    hull_name, kings_card, rex_bones, light_switch, museum_label, oscar, paste_pivot, placard, statue,
                    tag, torchlight, word_chip, wood_sign)

YARD_WALL = (176, 100)            # where the tally marks go on the yard wall
CUT = 0.12                        # each gag starts just as the one before it stops (the runner's lead), so
                                  # two sets never draw into the same frame


# --- small shared bits ----------------------------------------------------------------------------

def beard(img, c, length, who="david"):
    """A prisoner's beard, grown to `length` pixels below the chin."""
    if length <= 0:
        return
    mx, my = anchor(c, who, "mouth")
    f = c.st[who]["facing"]
    d = ImageDraw.Draw(img)
    top = my - 1
    x0, x1 = (mx - 6, mx + 2) if f > 0 else (mx - 2, mx + 6)
    tip = (mx - 2 * f, top + 3 + length)
    d.polygon([(x0, top), (x1, top), tip], fill=INK)
    d.polygon([(x0 + 1, top), (x1 - 1, top), (tip[0], tip[1] - 1)], fill=(240, 240, 244))
    d.line([(mx - 2 * f, top + 2), (tip[0], tip[1] - 2)], fill=(200, 200, 212))


def fist_on_bar(img, x, y):
    d = ImageDraw.Draw(img)
    d.rectangle((x - 2, y - 2, x + 3, y + 2), fill=INK)
    d.rectangle((x - 1, y - 1, x + 2, y + 1), fill=C["skin"])
    d.point((x, y), fill=C["skin_sh"])


def anger(img, x, y, age):
    """The cartoon vein that throbs on an angry forehead."""
    if age < 0:
        return
    k = 1 + (int(age * 8) % 2)
    d = ImageDraw.Draw(img)
    red = C["red"]
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.line([(x + sx * k, y + sy * (k + 2)), (x + sx * k, y + sy * k), (x + sx * (k + 2), y + sy * k)], fill=red)


def tallies(img, n, x0=YARD_WALL[0], y0=YARD_WALL[1]):
    """n tally marks scratched into the wall, in gates of five, seven gates to a row."""
    d = ImageDraw.Draw(img)
    scratch = (206, 196, 180)
    for k in range(int(n)):
        g, i = divmod(k, 5)
        row, col_ = divmod(g, 7)
        gx, gy = x0 + col_ * 8, y0 + row * 9
        if i < 4:
            d.line([(gx + i * 1.5, gy), (gx + i * 1.5, gy + 6)], fill=scratch)
        else:
            d.line([(gx - 1, gy + 5), (gx + 6, gy + 1)], fill=scratch)


# --- 0: "Seventy years inside the BBC. These walls are funny." ------------------------------------------
# Under the title card: the yard, the new fish, and seventy years of tally marks on the wall.

@gag("v2", 0, pre=0.4)
def seventy_years(c, L):
    c.shot = "wide"
    d_ = c.st["david"]
    d_.update(x=238, y=148, facing=-1, eyes="side")
    seventy = wt(L, "Seventy")
    bbc = wt(L, "BBC")
    yield "back"
    tallies(c.world, 70 * ease_out(ramp(c.t, seventy, seventy + 1.1)))
    if c.t >= bbc:                                   # the tower's lamp finds him
        blend_poly(c.world, [(46, 18), (50, 18), (252, 150), (224, 150)], (255, 250, 220), 0.18)
        blend(c.world, ellipse_mask(238, 149, 16, 4), (255, 250, 220), 0.3)
    yield "front"
    if c.t >= seventy + 0.9:
        pixel.text(c.world, (YARD_WALL[0] + 58, YARD_WALL[1] + 1), "70 YRS", SILK, (206, 196, 180), shadow=None)


def ellipse_mask(x, y, rx, ry):
    return mask(lambda d: d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=255))


# --- 1: "First you hate 'em. Then you get used to 'em." -----------------------------------------------------

@gag("v2", 1, pre=CUT)
def hate_then_used(c, L):
    c.set_scene("v2_cell")
    used = wt(L, "used")
    hate = wt(L, "hate")
    d_ = c.st["david"]
    if c.t < used:
        c.shot = "bars"
        d_.update(x=AT_BARS[0] + 5, y=AT_BARS[1], facing=1, arm="hold", gesture=False)
        if c.t >= hate:
            d_.update(mouth="grit", brows="angry", eyes="open")
            c.vars["rattle"] = 1 if int(c.t * 16) % 2 else -1
            c.add_shake(2)
        else:
            d_.update(mouth="frown", brows="worried")
    else:
        c.shot = "bunk"
        c.vars["cosy"] = True
        d_.update(x=BUNK_SEAT[0], y=BUNK_SEAT[1] + 6, facing=1, body="sit", arm="hold", gesture=False,
                  mouth="smile", eyes="half", brows="neutral", shadow=False)
    yield "front"
    if c.t < used:
        hx, hy = anchor(c, "david", "hand")
        fist_on_bar(c.world, 192 + c.get("rattle", 0), int(hy))
        if c.t >= hate:
            tx, ty = anchor(c, "david", "top")
            anger(c.world, int(tx + 8), int(ty + 2), c.t - hate)
    else:
        hx, hy = anchor(c, "david", "hand")
        paste(c.world, teacup(), hx + 3, hy - 2, "mm")
        if (c.t - used) % 1.2 < 0.6:
            sx, sy = int(hx + 3), int(hy - 8 - (c.t * 8) % 4)
            ImageDraw.Draw(c.world).point((sx, sy), fill=(240, 240, 240))


# --- 2: "Enough time passes, you get so you depend on 'em." ---------------------------------------------------
# A time-lapse in the cell: days flicker, the beard grows, cobwebs. Then parole: the door slides open
# and he hugs the bars and won't go.

BEARD_FULL = 18


def cobwebs(img, p):
    if p <= 0:
        return
    d = ImageDraw.Draw(img)
    web = (220, 220, 228)
    for (cx, cy, sx, sy) in ((0, 12, 1, 1), (W, 12, -1, 1)):
        r = int(30 * p)
        for k in range(5):
            a = k * math.pi / 8
            d.line([(cx, cy), (cx + sx * math.cos(a) * r, cy + sy * math.sin(a) * r)], fill=web)
        for rr in range(8, r, 8):
            pts = [(cx + sx * math.cos(k * math.pi / 8) * rr, cy + sy * math.sin(k * math.pi / 8) * rr)
                   for k in range(5)]
            d.line(pts, fill=web)


@gag("v2", 2, pre=CUT)
def time_passes(c, L):
    c.set_scene("v2_cell")
    c.shot = (156, 102, 12)
    passes = wt(L, "passes")
    depend = wt(L, "depend")
    p = ramp(c.t, L.t0, depend - 0.1)
    if c.t < depend:
        c.vars["sun"] = -40 + 80 * ((p * 3) % 1)
        c.mood = 0.55 * (0.5 - 0.5 * math.cos(2 * math.pi * 3 * p)) if p < 1 else 0
    c.vars["door"] = ease_out(ramp(c.t, depend, depend + 0.35))
    d_ = c.st["david"]
    d_.update(x=117, y=AT_BARS[1], facing=1, arm="hold", gesture=False)
    if c.t >= depend + 0.2:
        d_.update(mouth="frown", brows="worried", eyes="wide", sweat=True)
        d_["facing"] = 1 if int(c.t * 6) % 2 else -1          # shaking his head: no, no, no
    else:
        d_.update(mouth="closed", eyes="half")
    yield "back"
    if c.t >= depend:                                    # the corridor light through the open door
        k = c.get("door")
        blend_poly(c.world, [(146, 16), (146 + 60 * k, 16), (150 + 76 * k, 136), (140, 136)], (255, 248, 220), 0.35)
    yield "mid"
    beard(c.world, c, BEARD_FULL * ease_in_out(ramp(c.t, L.t0, depend)))
    yield "front"
    cobwebs(c.world, ramp(c.t, passes, depend))
    hx, hy = anchor(c, "david", "hand")
    fist_on_bar(c.world, 128, int(hy))
    yield "ui"
    if c.t >= depend + 0.15:
        stamp(c.ui, 236, 44, "PAROLE GRANTED", color=(60, 150, 80), angle=8, size=8, age=c.t - depend - 0.15)
    if c.t < depend:
        n = int(p * 3 * 365)
        pixel.text(c.ui, (W - 12, 28), f"DAY {n + 1}", SILK, C["text"], shadow=INK, anchor="ra")


# --- 3: "That's institutionalized." ---------------------------------------------------------------------------

@gag("v2", 3, pre=CUT)
def institutionalized(c, L):
    c.set_scene("v2_mug")
    c.shot = "mug"
    word = wt(L, "institution")
    d_ = c.st["david"]
    d_.update(mouth="frown", eyes="half", brows="worried")
    for tf in (L.t0, word):
        if 0 <= c.t - tf < 0.12:
            c.add_flash(0.85 * (1 - (c.t - tf) / 0.12))
    yield "mid"
    beard(c.world, c, BEARD_FULL)
    hx, hy = anchor(c, "david", "hand")
    paste(c.world, placard("B.B.C.", "No. 1952"), hx + 1, hy + 4, "mm")
    yield "ui"
    stamp(c.ui, 160, 50, "INSTITUTIONALIZED", color=C["red"], angle=-7, size=16, age=c.t - word)


# --- 4: "I'm eighty-nine years old, and I'm the young buck in this booth." -------------------------------------

@gag("v2", 4, pre=CUT)
def young_buck(c, L):
    c.shot = (114, 114, 12)
    eighty = wt(L, "eighty")
    buck = wt(L, "young")
    m = c.st["morgan"]
    m["rim"], m["rim_color"] = 0.5 * ramp(c.t, eighty + 0.2, eighty + 0.5), (255, 170, 80)
    if c.t >= buck:
        m.update(arm="up", brows="up", mouth="grin" if m["mouth"] == "closed" else m["mouth"])
    yield "front"
    if c.t >= eighty:
        rise = int((1 - back_out(ramp(c.t, eighty, eighty + 0.3))) * 30)
        blaze = ramp(c.t, eighty + 0.25, eighty + 0.5) * (1.35 if c.t >= buck else 1.0)
        cake(c.world, 128, 140 + rise, c.t, blaze)
    if c.t >= buck:
        tx, ty = anchor(c, "morgan", "top")
        age = c.t - buck
        drop = int((1 - back_out(ramp(age, 0, 0.22))) * -10)
        a = antlers()
        paste(c.world, a, tx + 1, ty + 3 + drop, "mb")
        if age < 0.3:
            for k in range(4):
                sparkle(c.world, int(tx - 14 + k * 9), int(ty - 12 - (k % 2) * 4), 2, (255, 250, 210))


# --- 5: "Your baby pictures? Cave paintings. That ain't a diss, that's the truth." ------------------------------

@gag("v2", 5, pre=CUT)
def baby_pictures(c, L):
    c.set_scene("v2_cave")
    cave_w = wt(L, "Cave")
    diss = wt(L, "diss")
    if c.t < cave_w:
        c.shot = "wall"
        p = ramp(c.t, L.t0, cave_w)
        lx, ly = lerp(270, 150, ease_in_out(p)), 84 + 10 * math.sin(p * 5)
    else:
        c.shot = (140, 92, 18)
        lx, ly = 140, 90
    c.vars["torch"] = (lx, ly)
    yield "front"
    lx, ly = c.get("torch")
    if c.t < cave_w:
        hx, hy = anchor(c, "morgan", "hand")
        blend_poly(c.world, [(hx, hy - 1), (hx, hy + 1), (lx + 20, ly + 20), (lx - 20, ly - 20)], (255, 230, 170), 0.18)
    torchlight(c.world, lx, ly, 22 if c.t < cave_w else 40)
    yield "ui"
    if c.t >= diss - 0.3:
        lab = museum_label("BABY DAVID, c. 40,000 BC", "OCHRE ON ROCK. ARTIST UNKNOWN")
        age = c.t - (diss - 0.3)
        x = int(lerp(-lab.width, 12, ease_out(ramp(age, 0, 0.25))))
        c.ui.paste(lab, (x, 128), lab)


# --- 6: "Get busy livin' or get busy dyin'? You been busy for a century." -------------------------------------
# Andy's poster comes down and Sir David is behind it with a rock hammer; the calendar runs from
# the year he was born to now, and the King's card arrives.

@gag("v2", 6, pre=CUT)
def busy_for_a_century(c, L):
    c.set_scene("v2_cell")
    c.shot = (204, 94, 9)
    livin = wt(L, "livin")
    you = wt(L, "You")
    century = wt(L, "century")
    tunnel = ramp(c.t, livin - 0.2, century)
    c.vars["tunnel"] = 0.2 + 0.8 * tunnel if c.t >= livin - 0.2 else 0
    d_ = c.st["david"]
    d_.update(x=224, y=AT_BARS[1], facing=1, gesture=False, mouth="grit", brows="angry")
    d_["arm"] = "up" if int(c.t * 8) % 2 else "fist"
    yield "mid"
    beard(c.world, c, BEARD_FULL + 14 * ramp(c.t, you, century))
    yield "front"
    p = ramp(c.t, you - 0.1, century)
    year = 1926 + int(round(100 * ease_in(p)))
    calendar(c.world, year, 1 + int(c.t * 37) % 28)
    if 0 < p < 1:
        for k in range(6):                                          # pages flying off the calendar
            age = (c.t * 3 + k / 6) % 1
            seed = int(c.t * 3 + k / 6)
            x = CALENDAR[0] + 12 - age * (40 + 30 * rnd("pg", seed, k))
            y = CALENDAR[1] + 10 - 30 * age + 60 * age * age
            c.world.paste(calendar_page(seed), (int(x), int(y)), calendar_page(seed))
    hx, hy = anchor(c, "david", "hand")
    if c.t >= livin - 0.2:
        puff(c.world, POSTER[0] + 12, POSTER[1] + 26, (c.t * 2.5) % 1, size=0.5, seed=int(c.t * 2.5),
             color=(170, 160, 150), drift=(8, 10), life=1.0)
        rub = int(10 * tunnel)
        ImageDraw.Draw(c.world).polygon([(236 - rub - 6, 136), (236, 136 - rub * 0.6), (236 + rub + 6, 136)],
                                        fill=(120, 112, 106))
    yield "ui"
    if c.t >= century:
        age = c.t - century
        k = back_out(ramp(age, 0, 0.25))
        card = kings_card()
        if k < 0.999:
            card = card.resize((max(1, int(card.width * k)), max(1, int(card.height * k))), Image.NEAREST)
        paste(c.ui, card, 86, 88, "mm")


# --- 7: "You ain't the narrator no more, David. You're the fossil in the documentary." -------------------------

@lru_cache(maxsize=None)
def lectern():
    s = Canvas(22, 30)
    s.poly([(1, 1), (20, 4), (18, 8), (3, 6)], "wood_hi")
    s.rect((8, 7, 13, 26), "wood")
    s.rect((4, 26, 17, 28), "wood_sh")
    return s.done()


@lru_cache(maxsize=None)
def sign_board(text_, w=None):
    w = w or text_width(text_, SILK) + 10
    s = Canvas(w + 2, 14)
    s.rect((1, 1, w, 12), (40, 44, 60))
    s.text((w // 2 + 1, 2), text_, "gold_hi", anchor="ma")
    return s.done()


@lru_cache(maxsize=None)
def film_camera():
    s = Canvas(26, 40)
    s.rect((4, 4, 18, 14), "black"); s.ell((2, 0, 10, 6), "mic"); s.ell((10, 0, 18, 6), "mic")
    s.rect((18, 7, 24, 11), "mic_hi")
    s.line([(11, 14), (4, 38)], "wood_sh"); s.line([(11, 14), (11, 38)], "wood_sh"); s.line([(11, 14), (18, 38)], "wood_sh")
    s.px((6, 9), "red")
    return s.done()


@gag("v2", 7, pre=CUT)
def the_fossil(c, L):
    c.set_scene("v2_museum")
    fossil = wt(L, "fossil")
    no = wt(L, "no")
    d_ = c.st["david"]
    if c.t < fossil:
        c.shot = (98, 112, 12)
        if c.t >= no:
            d_.update(mouth="frown", brows="worried", eyes="half", arm="down")
        else:
            d_.update(mouth="o" if int(c.t * 5) % 2 else "closed", brows="up")
    else:
        c.shot = (200, 104, 12)
        c.vars["fossil"] = True
    yield "back"
    if c.t < fossil:
        paste(c.world, sign_board("NARRATOR"), 98, 88, "mm")
    else:
        paste(c.world, film_camera(), 150, MUSEUM_FLOOR, "mb")
    yield "front"
    if c.t < fossil:
        paste(c.world, lectern(), 114, MUSEUM_FLOOR, "mb")
        if c.t >= no:
            strike(c.world, 78, 88, 118, ramp(c.t, no, no + 0.3))
    yield "ui"
    if c.t >= fossil:
        lab = museum_label("SIR DAVID ATTENBOROUGH", "FOSSIL. HOLOCENE. PLEASE DO NOT TAP THE GLASS")
        x = int(lerp(-lab.width, 10, ease_out(ramp(c.t, fossil + 0.15, fossil + 0.4))))
        c.ui.paste(lab, (x, 126), lab)


# --- 8: "Why you always whisperin'? Scared a gorilla gon' snitch?" -------------------------------------------
# Back in the ferns of his own documentary, whispering to the camera; the silverback behind him has
# been listening, and gets on the phone to the guards.

GORILLA_AT = (108, 146)


@gag("v2", 8, pre=CUT)
def gorilla_snitch(c, L):
    c.set_scene("habitat", prize=False, booth_light=0.0, on_air=False, mist=0.3)
    c.shot = (90, 118, 12)
    whis = wt(L, "whisperin")
    scared = wt(L, "Scared")
    gor = wt(L, "gorilla")
    snitch = wt(L, "snitch")
    place(c, "david", x=76, y=150, facing=1, body="crouch", mic="fluffy", arm="whisper", gesture=False, z=1)
    d_ = c.st["david"]
    if c.t < scared:
        d_.update(mouth="o" if int(c.t * 6) % 3 == 0 else "closed", eyes="half", brows="up")
    else:
        d_.update(eyes="side", brows="worried", mouth="closed", sweat=c.t >= gor)
    yield "back"
    pose = "phone" if c.t >= gor else "stand" if c.t >= scared else "sit"
    lean = 4 if whis <= c.t < scared else 0                       # he leans in to listen
    gx0, gy0 = paste(c.world, mirror(gorilla(pose, "smug" if c.t >= gor else "calm")), GORILLA_AT[0] - lean,
                     GORILLA_AT[1], "mb")
    if pose == "phone":                                           # the phone's screen, lit up
        blend(c.world, ellipse_mask(gx0 + 4, gy0 + 4, 4, 5), (160, 224, 255), 0.45)
    d = ImageDraw.Draw(c.world)
    for k in range(4):                                            # the ferns he's sitting in
        leaf_blob(d, GORILLA_AT[0] - 14 + k * 9, GORILLA_AT[1] - 3, 9, (36, 84, 56) if k % 2 else (46, 100, 64),
                  ("gb", k), n=5)
    yield "ui"
    if whis <= c.t < scared + 0.2:
        tx, ty = ui_at(c, *anchor(c, "david", "top"))
        bubble(c.ui, tx + 16, ty - 6, "...the silverback...", tail=(tx + 6, ty + 4), fnt=SILK, line_h=8, text_dy=-2,
               pad=3)
    if c.t >= snitch:
        gx, gy = ui_at(c, GORILLA_AT[0] + 4, GORILLA_AT[1] - 42)
        pop = back_out(ramp(c.t, snitch, snitch + 0.12))
        if pop > 0.3:
            bubble(c.ui, gx + 8, gy - 6, "HELLO, GUARDS?", tail=(gx + 2, gy + 4))


# --- 9: "God don't whisper, David. I said "Let there be light" and hit the switch." ---------------------------
# The void before anything: God in one spotlight, and the switch on the dark with LIGHT on the tape.

@gag("v2", 9, pre=CUT)
def let_there_be_light(c, L):
    c.set_scene("v2_void")
    c.shot = "god"
    god = wt(L, "God")
    whisper = wt(L, "whisper")
    david = wt(L, "David")
    said = wt(L, "said")
    switch = wt(L, "switch")
    m = c.st["morgan"]
    m.update(x=150 if c.t < switch - 0.1 else 153, gesture=False, arm="down")
    if whisper <= c.t < david:
        m.update(lean=2)
        c.add_shake(2)
    elif david <= c.t < said:
        m["arm"] = "point"
    elif c.t >= said:
        m["arm"] = "point"
        m["brows"] = "neutral"
    if c.t >= switch:
        c.add_flash(0.95 * ramp(c.t, switch + 0.05, switch + 0.2), (255, 250, 230))
    c.st["david"].update(eyes="shut", brows="worried", mouth="grit")    # for the reaction shot: dazzled
    if c.t < god:
        m["hidden"] = True
    yield "back"
    if c.t < god:                                                 # nothing yet, not even the spotlight
        c.world.paste((12, 10, 16), (0, 0, W, H))
    yield "mid"
    if c.t >= said - 0.15:
        on = c.t >= switch
        sx, sy = SWITCH
        if on:                                                    # the light, bursting out from behind the plate
            for k in range(12):
                a = k * math.pi / 6
                r0, r1 = 20, 20 + 90 * ramp(c.t, switch, switch + 0.15)
                blend_poly(c.world, [(sx + math.cos(a) * r0, sy + math.sin(a) * r0),
                                     (sx + math.cos(a + 0.12) * r1, sy + math.sin(a + 0.12) * r1),
                                     (sx + math.cos(a - 0.12) * r1, sy + math.sin(a - 0.12) * r1)],
                           (255, 250, 220), 0.6)
        paste(c.world, light_switch(on), sx, sy, "mm")


# --- 10: "I made the creatures that you film. Day five, day six, that's me." ---------------------------------
# The lights come up on creation: a production line in the clouds. God tags everything that comes
# off it, and on "that's me" he stamps the lens.

DAY5 = [(110.2 + k * 0.9, "fish" if k % 2 == 0 else "bird", k) for k in range(9)]
DAY6 = [(117.84, "gorilla", 0), (118.7, "lion", 1), (119.5, "penguin", 2)]
FISH_COLORS = [(90, 170, 220), (240, 140, 60), (120, 200, 160), (230, 90, 120)]
BIRD_COLORS = [((236, 80, 60), (250, 200, 60)), ((70, 130, 230), (120, 220, 240)), ((90, 190, 90), (250, 240, 90))]


def creature(kind, k, t):
    if kind == "fish":
        return fish(FISH_COLORS[k % 4], int(t * 8) % 2)
    if kind == "bird":
        col_, wing = BIRD_COLORS[k % 3]
        return bird(int(t * 10) % 2, col_, wing)
    if kind == "gorilla":
        return gorilla("sit", "calm")
    if kind == "lion":
        return lion("shut")
    if kind == "penguin":
        return penguin(int(t * 4) % 2)
    return rat(int(t * 6) % 2)


def belt_creatures(c, schedule, stop=None):
    """Draw what's on the belt: each thing drops out of the chute at its time and rides to the right,
    getting its tag as it passes God. With `stop`, the belt stopped at that time (and the birds that
    had been tagged are long gone)."""
    tt = c.t if stop is None else min(c.t, stop)
    for t0, kind, k in schedule:
        if tt < t0:
            continue
        x = CHUTE_X + (tt - t0) * BELT_SPEED
        if x > 340:
            continue
        spr = creature(kind, k, c.t)
        drop = 1 - ease_in(ramp(tt, t0, t0 + 0.15))
        y = BELT_TOP - int(drop * 16)
        if kind == "fish":
            y -= int(abs(math.sin(c.t * 9 + k)) * 3)
        tagged = x > GOD_AT_BELT[0] + 4
        if kind == "bird" and tagged:                             # the birds take off once they're tagged
            if stop is not None:
                continue
            fly_p = x - GOD_AT_BELT[0] - 4
            y -= int(fly_p * 1.6)
            x += fly_p * 0.4
        paste(c.world, spr, x, y, "mb")
        if tagged:
            paste(c.world, tag(), x - spr.width // 2 + 1, y - spr.height + 3, "lb")


@gag("v2", 10, pre=CUT)
def creation_line(c, L):
    c.set_scene("v2_factory", day=5)
    c.shot = "line"
    day6 = wt(L, "day", 1)
    thats = wt(L, "that's")
    if c.t >= day6:
        c.vars["day"] = 6
    if c.t < L.t0 + 0.4:                                          # the light from the switch, fading up on it all
        c.add_flash(1 - ramp(c.t, L.t0, L.t0 + 0.4), (255, 250, 230))
    m = c.st["morgan"]
    m.update(gesture=False)
    near = [x for t0, _, _ in DAY5 + DAY6 if c.t >= t0
            for x in [CHUTE_X + (c.t - t0) * BELT_SPEED] if -8 < x - GOD_AT_BELT[0] < 4]
    m["arm"] = "chop" if near else "up"
    if c.t >= thats:                                              # the close-up: he turns and stamps the lens
        c.shot = "god"
        m.update(facing=1, arm="chop" if c.t - thats < 0.1 else "fist", brows="up", z=1, y=GOD_AT_BELT[1] + 4)
        if c.t - thats < 0.12:
            c.add_shake(5)
    yield "mid"
    belt_creatures(c, DAY5 + DAY6)
    yield "ui"
    if c.t >= thats:
        stamp(c.ui, 160, 140, "MADE BY M.F.", color=C["red"], angle=-6, size=16, age=c.t - thats)


# --- 11: "You strolled in on day seven with a camera and a cup of tea." ----------------------------------------
# Day seven: the line's shut and God is asleep in a deckchair; Sir David wanders in, sets up his
# camera on everything that was made while he wasn't there, and has a cup of tea.

@gag("v2", 11, pre=CUT)
def day_seven(c, L):
    c.set_scene("v2_factory", day=7, belt_stop=True, closed=True)
    c.shot = "line"
    strolled = wt(L, "strolled")
    camera = wt(L, "camera")
    cup = wt(L, "cup")
    tea = wt(L, "tea")
    place(c, "morgan", x=262, y=150, facing=-1, body="sit", eyes="shut", mouth="closed", arm="down", gesture=False,
          outfit="god", z=1)
    walk = ramp(c.t, strolled - 0.4, camera - 0.2)
    x = lerp(52, 116, walk)
    place(c, "david", x=x, y=150, facing=1, gesture=False, z=1, arm="down", mouth="smile", eyes="open")
    d_ = c.st["david"]
    if 0 < walk < 1:
        d_["body"] = "walk1" if int(c.t * 6) % 2 else "walk2"
    if c.t >= camera:
        d_.update(lean=1, eyes="half")
    if c.t >= cup:
        d_.update(arm="hold", eyes="shut" if c.t >= tea else "half", mouth="closed", lean=0)
    yield "mid"
    belt_creatures(c, DAY5 + DAY6, stop=119.2)
    paste(c.world, deckchair(), 262, 151, "mb")
    yield "front"
    tx, ty = anchor(c, "morgan", "top")
    for k in range(3):                                            # Z z z
        age = (c.t * 0.8 + k / 3) % 1
        pixel.text(c.world, (int(tx - 4 - age * 10), int(ty - 4 - age * 18)), "Z", SILK,
                   (250, 250, 255), shadow=INK)
    if c.t >= camera - 0.1:
        drop = int((1 - back_out(ramp(c.t, camera - 0.1, camera + 0.1))) * -20)
        paste(c.world, film_camera(), 138, 150 + drop, "mb")
    if c.t >= cup:
        sip = c.t >= tea
        px_, py_ = anchor(c, "david", "mouth") if sip else anchor(c, "david", "hand")
        paste(c.world, teacup(), px_ + (4 if sip else 2), py_ + (2 if sip else -3), "mm")
        if (c.t * 2) % 1 < 0.6:
            ImageDraw.Draw(c.world).point((int(px_ + 3), int(py_ - 8 - (c.t * 8) % 4)), fill=(240, 240, 240))
    yield "ui"
    if c.t < L.t0 + 0.6:                                          # the stamp's still on the lens from the cut
        stamp(c.ui, 160, 140, "MADE BY M.F.", color=C["red"], angle=-6, size=16, age=1.0)


# --- 12: "Your brother Dickie ran Jurassic Park and spared no expense," -----------------------------------------
# The gates of the park, and the brothers in front of them: Dickie in the cream suit with the amber
# cane. The gates swing open; on "spared no expense" it rains money.

DICKIE_AT = (136, GATE_FLOOR)


@lru_cache(maxsize=None)
def banknote(frame=0):
    s = Canvas(9, 6) if frame == 0 else Canvas(5, 8)
    if frame == 0:
        s.rect((0, 0, 8, 5), (130, 180, 110)); s.rect((3, 1, 5, 4), (80, 130, 70))
    else:
        s.rect((0, 0, 4, 7), (110, 160, 96)); s.rect((1, 3, 3, 4), (70, 120, 60))
    return s.img


def money_rain(img, t, t0, seed=0, n=40, top=40, bottom=160):
    """Banknotes fluttering down between world rows top and bottom, from t0 on."""
    age = t - t0
    if age < 0:
        return
    for k in range(n):
        start = rnd("mr", seed, k) * 0.5
        a = age - start
        if a < 0:
            continue
        speed = 50 + 40 * rnd("my", seed, k)
        y = top - 10 + (a * speed + rnd("mo", seed, k) * 40) % (bottom - top + 10)
        x = rnd("mx", seed, k) * W + 6 * math.sin(a * 5 + k)
        note = banknote(int(a * 6 + k) % 2)
        img.paste(note, (int(x), int(y)), note)


@gag("v2", 12, pre=CUT)
def dickies_park(c, L):
    c.set_scene("v2_gate")
    c.shot = "gate"
    dickie_w = wt(L, "Dickie")
    jur = wt(L, "Jurassic")
    park = wt(L, "Park")
    spared = wt(L, "spared")
    c.vars["gate_open"] = ease_in_out(ramp(c.t, jur, park + 0.35))
    place(c, "david", x=186, y=GATE_FLOOR, facing=-1, arm="down", gesture=False,
          eyes="side" if c.t >= spared else "open", mouth="frown" if c.t >= spared else "closed")
    if c.t >= spared:
        c.shot = between_shots(c, "gate", (156, 104, 9), spared, 0.4)
    yield "mid"
    pose = dict(arm="up", mouth="grin", brows="up") if c.t >= spared else dict(arm="down", mouth="smile", brows="up")
    spr, a = dickie(1, cane="aloft" if c.t >= spared else "ground", **pose)
    fx_, fy_ = a["feet"]
    c.world.paste(spr, (int(DICKIE_AT[0] - fx_), int(DICKIE_AT[1] - fy_)), spr)
    yield "front"
    money_rain(c.world, c.t, spared, seed=12, n=70, top=56)
    yield "ui"
    if dickie_w <= c.t < jur + 0.2:
        x, y = ui_at(c, DICKIE_AT[0], DICKIE_AT[1] - 52)
        label(c.ui, (x, y - 10), "DICKIE", anchor="mb")
    if c.t >= spared:
        pop_text(c.ui, 160, 46, "SPARED NO EXPENSE", c.t - spared, top=(255, 214, 90), bottom=(230, 90, 40))


def between_shots(c, a, b, t0, dur):
    return between(shot_of(c, a), shot_of(c, b), ramp(c.t, t0, t0 + dur), ease_in_out)


# --- 13: "But the oldest fossil on that island's you, and you ain't even fenced." ------------------------------
# The T. rex paddock: ten thousand volts round the dinosaur. Outside it, whispering to camera with
# a sign pointing at him, the oldest fossil on the island, with no fence at all.

@gag("v2", 13, pre=CUT)
def unfenced(c, L):
    c.set_scene("v2_paddock")
    oldest = wt(L, "oldest")
    island = wt(L, "island")
    aint = wt(L, "ain't")
    fenced = wt(L, "fenced")
    if c.t < oldest:
        c.shot = "island"
    elif c.t < aint:
        c.shot = between_shots(c, "island", "david", oldest - 0.1, 0.35)
    else:
        c.shot = between_shots(c, "david", "island", aint, 0.3)
    d_ = c.st["david"]
    d_.update(mouth="o" if int(c.t * 5) % 3 == 0 else "closed", eyes="half", brows="up")
    yield "back"
    rex = scaled(mirror(trex("roar" if island <= c.t < island + 0.5 or c.t >= fenced else "shut",
                             int(c.t * 2) % 2)), 2)
    paste(c.world, rex, 238, PADDOCK_FLOOR - 4, "mb")
    yield "front"
    if c.t >= oldest:
        rise = int((1 - back_out(ramp(c.t, oldest, oldest + 0.2))) * 30)
        wob = int(round(math.sin(c.t * 20))) if island <= c.t < island + 0.4 else 0
        sign = wood_sign(("OLDEST", "FOSSIL"), -1)
        paste(c.world, sign, 136 + wob, PADDOCK_FLOOR + rise, "mb")
    yield "ui"
    if c.t >= fenced:
        x, y = ui_at(c, 104, 100)
        stamp(c.ui, max(84, x + 30), max(BAR + 16, y - 20), "NO FENCE NEEDED", color=C["red"], angle=-8, size=8,
              age=c.t - fenced)


# --- 14: "Dickie won an Oscar, and so did I: Million Dollar Baby." -----------------------------------------------
# The awards stage, house lights down: one spotlight for Dickie and his Oscar, one for Morgan and
# his, and one for the baby in the boxing gloves sitting on a million dollars.

DICKIE_STAGE = 100


@gag("v2", 14, pre=CUT)
def two_oscars(c, L):
    c.set_scene("v2_stage")
    c.shot = "stage"
    oscar_w = wt(L, "Oscar")
    so = wt(L, "so")
    million = wt(L, "Million")
    baby = wt(L, "Baby")
    spots = [DICKIE_STAGE]
    m = c.st["morgan"]
    m.update(gesture=False, arm="down")
    if c.t >= so:
        spots.append(214)
        m.update(arm="up", brows="up")
    else:
        m.update(eyes="side")
    if c.t >= million:
        spots.append(160)
    c.vars["spots"] = spots
    yield "back"
    raised = c.t >= oscar_w
    spr, a = dickie(1, cane="ground" if not raised else None, arm="up" if raised else "down",
                    mouth="grin" if raised else "smile", brows="up")
    fx_, fy_ = a["feet"]
    ox, oy = int(DICKIE_STAGE - fx_), int(STAGE_FLOOR - fy_)
    c.world.paste(spr, (ox, oy), spr)
    if raised:
        hx, hy = a["hand"]
        paste(c.world, oscar(), ox + hx, oy + hy + 2, "mb")
        if (c.t - oscar_w) % 0.5 < 0.25:
            sparkle(c.world, int(ox + hx + 3), int(oy + hy - 20), 2, (255, 250, 210))
    yield "mid"
    if c.t >= million:
        rise = int((1 - back_out(ramp(c.t, million, million + 0.3))) * 44)
        bb = boxing_baby()
        jab = 2 if c.t >= baby and int(c.t * 10) % 2 else 0
        paste(c.world, bb, 160 + jab, STAGE_FLOOR + rise, "mb")
    yield "front"
    if c.t >= so:
        hx, hy = anchor(c, "morgan", "hand")
        paste(c.world, oscar(), hx, hy + 2, "mb")
        if (c.t - so) % 0.5 < 0.25:
            sparkle(c.world, int(hx + 3), int(hy - 20), 2, (255, 250, 210))
    yield "ui"
    if c.t >= million:
        pop_text(c.ui, 160, 36, "$1,000,000", c.t - million, top=(170, 230, 140), bottom=(80, 160, 90))


# --- 15: "You got a shelf full of BAFTAs? That's adorable. That's British for "maybe."" -------------------------
# The study: a long shelf of gold masks and Sir David, proud of every one. Morgan brings his one
# Oscar; the masks go unsure of themselves.

@lru_cache(maxsize=None)
def heart():
    s = Canvas(9, 8)
    s.ell((0, 0, 4, 4), (230, 70, 100)); s.ell((4, 0, 8, 4), (230, 70, 100))
    s.poly([(0, 3), (8, 3), (4, 7)], (230, 70, 100))
    s.px((2, 1), (255, 170, 190))
    return s.done()


@gag("v2", 15, pre=CUT)
def baftas(c, L):
    c.set_scene("v2_study")
    shelf = wt(L, "shelf")
    adorable = wt(L, "adorable")
    thats = wt(L, "That's")
    british = wt(L, "British")
    maybe = wt(L, "maybe")
    d_ = c.st["david"]
    m = c.st["morgan"]
    if c.t < thats:
        c.shot = between_shots(c, (96, 104, 12), (206, 104, 12), shelf - 0.3, thats - shelf + 0.1)
        m["hidden"] = True
        d_.update(arm="palm", mouth="smile", brows="up", eyes="half")
    else:
        c.shot = "two"
        walk_in = ramp(c.t, thats - 0.1, thats + 0.3)
        m.update(x=lerp(236, 196, ease_out(walk_in)), arm="up", gesture=False, mouth="smirk",
                 body="walk1" if 0 < walk_in < 1 and int(c.t * 8) % 2 else "stand")
        d_.update(arm="down", mouth="frown" if c.t >= british else "smile", brows="worried" if c.t >= british else "up")
    c.vars["shrug"] = 1.0 if c.t >= british else 0.0
    yield "front"
    if c.t >= thats:
        hx, hy = anchor(c, "morgan", "hand")
        paste(c.world, oscar(), hx, hy + 2, "mb")
    if adorable <= c.t < british + 0.2:
        tx, ty = anchor(c, "david", "top")
        for k in range(4):
            age = (c.t - adorable) * 0.9 + k * 0.25
            if age % 1 < 0.9:
                paste(c.world, heart(), tx - 12 + k * 8 + 3 * math.sin(age * 6), ty - 2 - (age % 1) * 22, "mm")
    yield "ui"
    if c.t >= maybe:
        stamp(c.ui, 160, 52, "MAYBE", color=(40, 70, 170), angle=-9, size=16, age=c.t - maybe)


# --- 16: "They let the nation name a ship for you, put it to a public vote." ----------------------------------------
# A brand-new polar ship with a blank name on the bow, Sir David proud on the quay, and the public
# vote coming in.

VOTES_DAVID = 3707
VOTES_BOATY = 124109


def vote_board(ui, age, reveal=0.0, count=1.0, y=28):
    """The public vote: Sir David's name against a mystery entry that is winning by a mile."""
    if age < 0:
        return
    x = int(lerp(-170, 8, ease_out(ramp(age, 0, 0.3))))
    w, h = 162, 42
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 1, y - 1, x + w + 1, y + h + 1), fill=INK + (255,))
    d.rectangle((x, y, x + w, y + h), fill=(20, 30, 60, 255))
    d.rectangle((x, y, x + w, y + 9), fill=(196, 40, 40, 255))
    pixel.text(ui, (x + w // 2, y + 1), "NAME THE SHIP: PUBLIC VOTE", SILK, (255, 255, 255), shadow=None, anchor="ma")
    rows = (("SIR DAVID A.", VOTES_DAVID), ("BOATY MCBOATFACE" if reveal else "???", VOTES_BOATY))
    for i, (name, n) in enumerate(rows):
        yy = y + 13 + i * 14
        shown = int(n * count)
        pixel.text(ui, (x + 4, yy), name, SILK, (236, 236, 240) if i == 0 else (255, 214, 90), shadow=None)
        pixel.text(ui, (x + w - 4, yy), f"{shown:,}", SILK, (236, 236, 240), shadow=None, anchor="ra")
        bw = int((w - 8) * shown / VOTES_BOATY)
        d.rectangle((x + 4, yy + 8, x + 4 + max(1, bw), yy + 10), fill=((120, 170, 230) if i == 0 else (255, 214, 90)) + (255,))


@gag("v2", 16, pre=CUT)
def name_a_ship(c, L):
    c.set_scene("v2_dock")
    c.shot = "ship"
    public = wt(L, "public")
    vote = wt(L, "vote")
    d_ = c.st["david"]
    d_.update(mouth="smile", brows="up", eyes="half")
    if c.t >= vote:
        d_.update(eyes="open", brows="worried", mouth="closed")
    yield "back"
    hull_name(c.world, "", 0.0, int(round(math.sin(c.t * 1.4))))
    yield "ui"
    vote_board(c.ui, c.t - public, count=ease_in(ramp(c.t, vote, vote + 0.9)))


# --- 17: "The people said "Boaty McBoatface." That's the review. That's the quote." -----------------------------
# The name goes on the bow. Then the poster: one star, and the pull quote from the British public.

def review_card(ui, stars_age, quote_age, y=28):
    if stars_age < 0:
        return
    x = int(lerp(-180, 8, ease_out(ramp(stars_age, 0, 0.25))))
    w, h = 172, 58
    d = ImageDraw.Draw(ui)
    d.rectangle((x - 1, y - 1, x + w + 1, y + h + 1), fill=INK + (255,))
    d.rectangle((x, y, x + w, y + h), fill=(14, 12, 18, 255))
    for k in range(5):                                            # one star out of five
        cx, cy = x + w // 2 - 32 + k * 16, y + 11
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 6 if i % 2 == 0 else 2.6
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
        if k == 0:
            d.polygon(pts, fill=C["gold"] + (255,))
        else:
            d.polygon(pts, outline=(120, 110, 90, 255))
    if quote_age >= 0:
        k = back_out(ramp(quote_age, 0, 0.15))
        big_text(ui, (x + w // 2, y + 22), '"BOATY MCBOATFACE"', PRESS, anchor="ma", scale=max(0.2, k) if k < 0.999 else 1.0)
        pixel.text(ui, (x + w // 2, y + 42), "- THE BRITISH PUBLIC", SILK, (220, 214, 200), shadow=None, anchor="ma")
        for side in (-1, 1):                                      # laurels
            lx = x + w // 2 + side * 80
            for j in range(4):
                ImageDraw.Draw(ui).ellipse((lx - 2 - side * j, y + 20 + j * 7, lx + 2 - side * j, y + 25 + j * 7),
                                          fill=C["gold_sh"] + (255,))


@gag("v2", 17, pre=CUT)
def boaty(c, L):
    c.set_scene("v2_dock")
    boaty_w = wt(L, "Boaty")
    mcb = wt(L, "McBoatface")
    thats = wt(L, "That's")
    review = wt(L, "review")
    name = "BOATY MCBOATFACE"
    if boaty_w <= c.t < thats:
        c.shot = "hull"
    else:
        c.shot = "ship"
    d_ = c.st["david"]
    d_.update(mouth="frown", brows="worried", eyes="open", arm="down")
    if c.t >= thats:
        d_.update(eyes="half")
    yield "back"
    p = 0.0 if c.t < boaty_w else 5 / 16 * ramp(c.t, boaty_w, boaty_w + 0.2) + 11 / 16 * ramp(c.t, mcb, mcb + 0.35)
    hull_name(c.world, name, p, int(round(math.sin(c.t * 1.4))))
    yield "ui"
    if c.t < thats:
        vote_board(c.ui, 5.0, reveal=c.t >= boaty_w)
    review_card(c.ui, c.t - review + 0.3, c.t - wt(L, "That's", 1))       # the quote lands on "That's the quote"


# --- 18: "I was President in Deep Impact when the comet hit the ground." -----------------------------------------
# The Oval Office: the President at the podium, and in the window behind him, the comet.

@gag("v2", 18, pre=CUT)
def deep_impact(c, L):
    c.set_scene("v2_oval")
    c.shot = "podium"
    president = wt(L, "President")
    comet_w = wt(L, "comet")
    hit = wt(L, "hit")
    m = c.st["morgan"]
    m.update(gesture=False, arm="palm" if c.t < hit else "down")
    c.vars["sky"] = 1.0 if c.t >= hit else 0.0
    if c.t >= hit:
        c.add_flash(max(0.0, 0.9 - (c.t - hit) * 2.2), (255, 244, 220))
        c.add_shake(6 * max(0.0, 1 - (c.t - hit) / 0.45))
    yield "back"
    if c.t < hit:
        p = ramp(c.t, L.t0, hit)
        wx0, wy0, wx1, wy1 = WINDOW
        win = c.world.crop(WINDOW)
        comet(win, lerp(94, 62, p), lerp(44, 62, p), 1.5 + 12 * p ** 2)
        c.world.paste(win, (wx0, wy0))
    yield "ui"
    CH.lower_third(c.ui, c.t - president, "THE PRESIDENT", "MORGAN FREEMAN, DEEP IMPACT (1998)", y=BAR + 4, x=8,
                   out_at=comet_w - president - 0.2)


# --- 19: "You'd have crouched beside the T-rex whisperin', "Isn't that profound."" -----------------------------
# The Cretaceous, the last afternoon of it: Sir David crouched by the T. rex, whispering, while the
# asteroid grows in the sky. On "profound" it lands, and all that's left is ash and his microphone.

@gag("v2", 19, pre=CUT)
def isnt_that_profound(c, L):
    c.set_scene("v2_cret")
    c.shot = "pair"
    isnt = wt(L, "Isn't")
    profound = wt(L, "profound")
    after = c.t >= profound + 0.12
    d_ = c.st["david"]
    d_.update(mouth="o" if int(c.t * 5) % 3 == 0 else "closed", eyes="half", brows="up")
    if after:
        d_["hidden"] = True
    if profound <= c.t < profound + 0.3:
        c.add_flash(1.0 - ramp(c.t, profound + 0.12, profound + 0.3) * 0.9, (255, 250, 236))
        c.add_shake(8)
    yield "back"
    if after:
        c.world.paste(ash_world())
        paste(c.world, scaled(mirror(rex_bones()), 2), 234, CRET_FLOOR + 2, "mb")
    else:
        p = ramp(c.t, L.t0, profound)
        asteroid(c.world, lerp(132, 96, p), lerp(66, 84, p), 1 + 19 * p ** 2.5)
        paste(c.world, scaled(mirror(trex("open" if isnt <= c.t else "shut", 0)), 2), 234, CRET_FLOOR + 2, "mb")
    yield "front"
    if after:
        d = ImageDraw.Draw(c.world)
        d.ellipse((96, CRET_FLOOR - 8, 144, CRET_FLOOR + 10), fill=(186, 178, 172))       # the ash mound
        d.ellipse((104, CRET_FLOOR - 12, 136, CRET_FLOOR), fill=(196, 188, 182))
        d.line([(122, CRET_FLOOR - 12), (125, CRET_FLOOR - 26)], fill=INK, width=3)        # his fluffy mic
        d.line([(122, CRET_FLOOR - 12), (125, CRET_FLOOR - 26)], fill=C["mic"])
        for k in range(14):                                                                # all fur
            a = k * 2 * math.pi / 14
            r = 7 + (k % 2) * 2
            d.line([(127, CRET_FLOOR - 31), (127 + math.cos(a) * r, CRET_FLOOR - 31 + math.sin(a) * r * 0.8)],
                   fill=INK, width=3)
        d.ellipse((120, CRET_FLOOR - 37, 134, CRET_FLOOR - 25), fill=C["fluff"])
        for k in range(14):
            a = k * 2 * math.pi / 14
            r = 6 + (k % 2) * 2
            d.line([(127, CRET_FLOOR - 31), (127 + math.cos(a) * r, CRET_FLOOR - 31 + math.sin(a) * r * 0.8)],
                   fill=C["fluff_hi"] if k % 3 == 0 else C["fluff"])
        puff(c.world, 120, CRET_FLOOR - 10, (c.t - profound) % 1.2, size=0.8, seed=19, color=(150, 146, 146),
             drift=(4, -10), life=1.2)
    yield "ui"
    if isnt <= c.t < profound + 0.1:
        tx, ty = ui_at(c, *anchor(c, "david", "top"))
        s = "isn't that pro-" if c.t >= profound - 0.05 else "...isn't that..."
        bubble(c.ui, tx + 8, ty - 6, s, tail=(tx + 4, ty + 4), fnt=SILK, line_h=8, text_dy=-2, pad=3)
    if c.t >= profound + 0.45:                                    # still whispering, from under the ash
        tx, ty = ui_at(c, 116, CRET_FLOOR - 12)
        bubble(c.ui, tx - 6, ty - 26, "...found.", tail=(tx, ty - 4), fnt=SILK, line_h=8, text_dy=-2, pad=3)


def asteroid(img, x, y, r):
    """The asteroid, coming in from the top left with its fire behind it."""
    d = ImageDraw.Draw(img)
    for k in range(6, 0, -1):
        rr = r * (1 - k * 0.1)
        cx, cy = x - k * r * 0.7, y - k * r * 0.6
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr),
                  fill=[(255, 250, 220), (255, 226, 150), (255, 190, 90), (250, 150, 60), (220, 110, 60),
                        (180, 90, 70)][k - 1])
    blend(img, mask(lambda m: m.ellipse((x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5), fill=255)),
          (255, 190, 90), 0.45)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(90, 70, 60))
    d.ellipse((x - r * 0.6, y - r * 0.6, x, y), fill=(130, 100, 80))
    d.arc((x - r, y - r, x + r, y + r), 130, 300, fill=(255, 150, 60), width=max(1, int(r / 5)))


# --- 20: "They call me Freeman 'cause I free you of your title, of your crown." -----------------------------------
# The hall of names: MORGAN FREEMAN on one brass plate, SIR DAVID ATTENBOROUGH on the other. The
# FREE in FREEMAN lights up; the SIR comes off David's plate onto Morgan's, and the crown follows.

M_PLATE = (104, 76)
D_PLATE = (212, 76)


@gag("v2", 20, pre=CUT)
def free_man(c, L):
    c.set_scene("v2_hall")
    c.shot = "both"
    freeman = wt(L, "Freeman")
    free = wt(L, "^free$")
    title = wt(L, "title")
    crown_w = wt(L, "crown")
    sir_lands = title + 0.45
    crown_lands = crown_w + 0.45
    m = c.st["morgan"]
    d_ = c.st["david"]
    if free <= c.t < crown_w + 0.3:
        m.update(arm="point", gesture=False)
    if c.t >= crown_lands:
        m.update(hat="crown", mouth="grin" if m["mouth"] == "closed" else m["mouth"])
    if c.t >= crown_w:
        d_.update(hat="none", eyes="wide", brows="worried", mouth="o")
    elif c.t >= title:
        d_.update(mouth="o", brows="up")
    else:
        d_.update(mouth="closed", brows="up", eyes="half")
    yield "back"
    m_rows = [["SIR ", "MORGAN"] if c.t >= sir_lands else ["MORGAN"], ["FREE", "MAN"]]
    brass_plate(c.world, M_PLATE[0], M_PLATE[1], m_rows, lit={"FREE"} if c.t >= freeman else ())
    boxes = brass_plate(c.world, D_PLATE[0], D_PLATE[1], [["SIR ", "DAVID"], ["ATTENBOROUGH"]],
                        gone={"SIR "} if c.t >= title else ())
    c.vars["sir_from"] = boxes["SIR "]
    yield "front"
    if title <= c.t < sir_lands:                                   # SIR flies over to the other plate
        p = ramp(c.t, title, sir_lands)
        x0, y0, _, _ = c.get("sir_from")
        chip = word_chip("SIR")
        tx = M_PLATE[0] - (text_width("SIR MORGAN", PRESS)) // 2
        x, y = arc_pt(ease_in_out(p), (x0 + 12, y0 + 4), (tx + 12, M_PLATE[1] - 1), 26)
        paste_rot(c.world, chip, x, y, 360 * p)
    if crown_w <= c.t < crown_lands:
        p = ramp(c.t, crown_w, crown_lands)
        sx, sy = anchor(c, "david", "top")
        ex, ey = anchor(c, "morgan", "top")
        x, y = arc_pt(ease_in_out(p), (sx, sy), (ex, ey), 30)
        paste_rot(c.world, crown(), x, y, -540 * p)


# --- 21: "London Has Fallen. I was there. Now watch Attenborough go down." ------------------------------------------
# London burning at dusk (Morgan's other film), Big Ben going over, the President in front. Then
# the bronze of Sir David on the embankment topples on "go down", before the static takes the channel.

@gag("v2", 21, pre=CUT)
def london_has_fallen(c, L):
    c.set_scene("v2_london")
    c.shot = "skyline"
    fallen = wt(L, "Fallen")
    watch = wt(L, "watch")
    go = wt(L, "^go$")
    down = wt(L, "down")
    m = c.st["morgan"]
    m.update(gesture=False, arm="point" if c.t >= watch else "mic")
    if 0 <= c.t - (fallen + 0.45) < 0.3:
        c.add_shake(4)
    if 0 <= c.t - down < 0.3:
        c.add_shake(6)
    yield "back"
    ben = ease_in(ramp(c.t, fallen - 0.05, fallen + 0.45))
    paste_pivot(c.world, big_ben(), BEN[0] - 5, BEN[1], 5, 91, 88 * ben)          # over, onto Parliament
    if ben >= 1:
        puff(c.world, BEN[0] - 56, BEN[1] - 6, c.t - fallen - 0.45, size=1.6, seed=21, color=(120, 100, 110),
             drift=(-6, -8), life=1.6)
    yield "mid"
    fall = ease_in(ramp(c.t, go - 0.05, down))
    spr, (fx_, fy_) = statue()
    paste_pivot(c.world, spr, STATUE[0] - 14, STATUE[1], fx_ - 14, fy_, 90 * fall)
    if c.t >= down:
        puff(c.world, STATUE[0] - 70, STATUE[1] - 4, c.t - down, size=1.8, seed=22, color=(170, 150, 130),
             drift=(-4, -10), life=1.2)
    yield "ui"
    if c.t < fallen + 0.9:
        k = back_out(ramp(c.t, L.t0 + 0.1, L.t0 + 0.3))
        if k > 0:
            big_text(c.ui, (160, 36), "LONDON HAS FALLEN", PRESS16, anchor="ma", scale=max(0.2, k) if k < 0.999 else 1.0,
                     top=(255, 230, 190), bottom=(230, 90, 50))
