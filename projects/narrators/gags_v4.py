"""Verse 4: Morgan's picture, DRIVING MR. DAVID. Hoke drives Sir David home (the cemetery), then every
line cuts to the reel: the ferns' privacy, seventy years in a bush, the captain of his soul, a mole's
sweet nothings, a case closed, a spider's grace, the cave, the sloth, the Earth on its deathbed, the
headstones he has outlived, the rain on his reign, the bucket list, the birds that fly free and the
dodo that can't.
"""
import sets as S
import v4_art as A
from critters import bird
from gagkit import (C, CH, FILM_TOP, INK, PRESS, PRESS16, V, H, Image, ImageDraw, W, anchor,
                    back_out, blend, blend_poly, ease_in, ease_in_out, ease_out, gag, lerp, mask,
                    line_t, math, mirror, pan, paste, paste_rot, paste_scaled, pixel, ramp, rnd, tint, ui_at, wt)
from gags_links import END_CARD
from props import bubble, burst, checkbox, crown, field_camera, pop_text, puff, sparkle, stamp, teacup

SEC = "v4"


def cut(c, name, **knobs):
    """Cut to one of the verse's sets and re-pose the pair for it (the verse posed them for the car)."""
    c.set_scene(name, **knobs)
    V.pose_rapper(c, "morgan")
    V.pose_listener(c, "david")


def iris(c, cx, cy, r):
    """The silent-film iris: black outside a circle on the UI."""
    if r > 400:
        return
    m = Image.new("L", (W, H), 255)
    if r > 0:
        ImageDraw.Draw(m).ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    c.ui.paste((0, 0, 0, 255), (0, 0, W, H), m)


def newsreel(c):
    """Drain the colour out of the world (the film grade then warms it into old stock)."""
    c.world.paste(c.world.convert("L").convert("RGB"))


def caption(c, s, x=8, y=FILM_TOP + 4, fnt=PRESS, color=C["text"], anchor_="la"):
    """An intertitle-style caption just inside the letterbox."""
    pixel.text(c.ui, (x, y), s, fnt, color, shadow=INK, anchor=anchor_)


def hearts(img, x, y, t, t0, n=6, every=0.22, seed=0):
    for k in range(n):
        age = t - (t0 + k * every)
        if 0 <= age < 1.1:
            hx = x + math.sin(age * 5 + k) * 4 + (rnd("ht", seed, k) - 0.5) * 8
            paste_scaled(img, A.heart(), hx, y - age * 26, min(1.0, 0.5 + age * 2), "mm")


# --- 0: "Pushin' up daisies? Hoke drove twenty-five years, never scratched the car." -------------------
# Under the title card: daisies spring up all along the verge (and one on Sir David's head); then the
# car gleams, and a tag: SCRATCHES: 0.

CAR_BODY = [(84, 146), (86, 126), (104, 118), (196, 118), (212, 116), (234, 122), (240, 146)]


@gag(SEC, 0, pre=0.99)                  # from the clapper's snap: the road under the title card
def pushing_daisies(c, L):
    c.shot = "road"
    daisies, scratched = wt(L, "daisies"), wt(L, "scratched")
    yield "back"
    if c.t >= daisies - 0.1:
        off = (c.t - daisies) * S.car_speed(c) * 1.2
        for k in range(36):
            x0 = k * 12 + 6 * rnd("dz", k)
            grow = back_out(ramp(c.t, daisies + 0.25 * rnd("dz-t", k), daisies + 0.25 * rnd("dz-t", k) + 0.2))
            x = (x0 - off) % 432 - 56
            paste_scaled(c.world, A.daisy(5 + k % 3), x, 134 + (k % 2) * 2, grow, "mb")
    yield "front"
    if c.t >= daisies:
        hx, hy = anchor(c, "david", "top")
        paste_scaled(c.world, A.daisy(7), hx + 1, hy + 3, back_out(ramp(c.t, daisies, daisies + 0.25)), "mb")
    g = ramp(c.t, scratched - 0.05, scratched + 0.4)
    if 0 < g < 1:
        bob = c.get("car_bob_y", 0)
        gx = lerp(60, 250, g)
        body = mask(lambda d: d.polygon([(x, y + bob) for x, y in CAR_BODY], fill=255))
        band = mask(lambda d: d.polygon([(gx, 150), (gx + 9, 150), (gx + 25, 112), (gx + 16, 112)], fill=255))
        blend(c.world, body * band, (255, 255, 255), 0.75)
    if c.t >= scratched + 0.25:
        for k, (x, y) in enumerate(((118, 126), (170, 122), (224, 128))):
            if int(c.t * 8 + k * 3) % 4 < 3:
                sparkle(c.world, x, y + c.get("car_bob_y", 0), 2 if int(c.t * 8 + k) % 2 else 1, (255, 255, 255))
    yield "ui"
    if c.t >= scratched:
        tx, ty = ui_at(c, 196, 128)
        CH.callout(c.ui, c.t - scratched, "SCRATCHES: 0", tx, ty, 268, 104, C["gold_hi"])


# --- 1: "Hop in the back, David. I'll drive you home. It ain't far." --------------------------------------
# He turns round to thumb at the back seat; a sign goes by, HOME 1/2 MI; cut: the car parked under the
# arch of RESTHAVEN cemetery, beside a fresh plot marked RESERVED.

PARK_OFF = 22.5                  # the scenery offset where the car stops (a pole hides behind the arch)
GATE_X = 164


def cemetery(img):
    gate = A.cemetery_gate()
    paste(img, gate, GATE_X, 128, "mb")
    for x, rows, w in ((20, (), 12), (266, (), 14), (300, (), 12)):
        paste(img, A.tombstone(rows, w, 16, "cross" if x % 2 else None, (140, 140, 150)), x, 130, "mb")
    d = ImageDraw.Draw(img)
    d.polygon([(28, 136), (70, 136), (66, 132), (32, 132)], fill=(40, 30, 26))          # the open grave
    d.ellipse((66, 126, 84, 136), fill=A.SOIL)                                          # its heap of earth
    d.line([(80, 116), (84, 131)], fill=(120, 90, 60), width=2)                        # a spade stuck in
    d.rectangle((77, 113, 84, 116), fill=(150, 150, 160))
    paste(img, A.road_sign(("RESERVED", "SIR D."), (120, 40, 44), post=8), 48, 132, "mb")


@gag(SEC, 1)
def drive_you_home(c, L):
    ill, it = wt(L, "I'll"), wt(L, "^It$")
    m = c.st["morgan"]
    c.shot = "car" if c.t < ill else "road"
    if c.t < ill - 0.2:
        m.update(facing=-1, arm="point", brows="up")       # turned round in his seat, thumbing at the back
    parked = c.t >= it
    if parked:
        c.vars.update(car_speed=PARK_OFF / c.t, car_bob=False)
        m.update(arm="point")
    yield "back"
    img = c.world
    if ill <= c.t < it:
        paste(img, A.road_sign(("HOME", "1/2 MI"), icon="arrow"), 340 - (c.t - ill) * 90, 128, "mb")
    if parked:
        cemetery(img)
    if c.t >= ill:
        S.car_body(img, bob=c.get("car_bob_y", 0), lower=False)
    yield "front"
    if parked and c.t < it + 0.1:
        c.add_flash(0.5, (255, 255, 255))


# --- 2: "The Private Life of Plants? Man, give the ferns some privacy." -------------------------------------
# Sir David crouched on a fern with his camera; a fiddlehead unrolls for him; the ferns curl up shyly,
# and a privacy screen slams down between them.

@gag(SEC, 2)
def fern_privacy(c, L):
    cut(c, "v4_ferns")
    plants, ferns, privacy = wt(L, "Plants"), wt(L, "ferns"), wt(L, "privacy")
    c.shot = (148, 120, 12)
    d = c.st["david"]
    d.update(arm="hold", brows="up", mouth="grin" if c.t < ferns else "o")
    if c.t >= privacy:
        d.update(mouth="frown", brows="worried")
    drop = ease_in(ramp(c.t, privacy - 0.14, privacy))
    if 0 <= c.t - privacy < 0.25:
        c.add_shake(3 * (1 - (c.t - privacy) / 0.25))
    yield "back"
    x, y = A.FERN
    A.fern_clump(c.world, x, y, c.t, curl=ease_out(ramp(c.t, ferns, ferns + 0.3)),
                 fiddle=ease_out(ramp(c.t, plants - 0.3, plants + 0.4)) * (1 - ramp(c.t, ferns, ferns + 0.2)),
                 shy=ramp(c.t, ferns, ferns + 0.1) * (1 - ramp(c.t, privacy, privacy + 0.1)))
    yield "front"
    hx, hy = anchor(c, "david", "hand")
    paste(c.world, field_camera(), hx + 4, hy - 2, "mm")
    if drop > 0:
        paste(c.world, A.folding_screen(), x - 2, lerp(40, 150, drop), "mb")
        puff(c.world, x - 2, 148, c.t - privacy, 0.9, seed=2, color=(150, 120, 90), drift=(0, -4), life=0.8)


# --- 3: "You been creepin' in the bushes with a lens since the Eisenhower presidency." ----------------------
# A bush tiptoes across the lawn; up pops Sir David; his lens telescopes out; on "Eisenhower" the picture
# is a 1953 newsreel (I LIKE IKE on the tree); on "presidency", colour: 73 YEARS LATER, same bush, same
# pose, now under cobwebs with a bird's nest on his head.

@gag(SEC, 3)
def since_eisenhower(c, L):
    cut(c, "v4_bushes")
    creep, bushes, lens, eis, pres = (wt(L, "creepin"), wt(L, "bushes"), wt(L, "lens"), wt(L, "Eisenhower"),
                                      wt(L, "presidency"))
    old = eis <= c.t < pres
    c.vars["ike"] = old
    c.shot = (150, 104, 12)
    walk = ramp(c.t, creep - 0.1, bushes)
    bx = lerp(A.BUSH[0] + 36, A.BUSH[0], walk)
    tiptoe = 2 * abs(math.sin(c.t * 18)) if 0 < walk < 1 else 0
    d = c.st["david"]
    if c.t < bushes:
        d["hidden"] = True
    pop = back_out(ramp(c.t, bushes, bushes + 0.2))
    d.update(x=bx, y=A.BUSH[1], body="stand", facing=-1, arm="hold", dy=-13 * pop + 12 * (1 - pop), mouth="closed",
             eyes="side" if c.t < pres else d["eyes"], brows="up")
    yield "mid"
    A.bush(c.world, bx, A.BUSH[1] - tiptoe, 76, 44, c.t, rustle=1.0 if 0 < walk < 1 or 0 < pop < 1 else 0.0)
    yield "front"
    img = c.world
    ex, ey = anchor(c, "david", "eye")
    if c.t >= bushes:
        length = int(8 + 58 * ease_out(ramp(c.t, lens, lens + 0.35)))
        lens_img = mirror(A.long_lens(length))
        paste(img, lens_img, ex + 4, ey + 5, "rm")                # held under his eye, so we see him peek
        if c.t >= lens and c.t < lens + 0.35:
            sparkle(img, ex + 4 - lens_img.width, ey + 5, 3, (255, 255, 255))
    if c.t >= pres:                                     # 73 years later
        tx, ty = anchor(c, "david", "top")
        paste(img, A.nest(), tx + 1, ty + 4, "mb")
        A.cobweb(img, ex - 30, ey + 2, 16)
        A.cobweb(img, tx - 6, ty + 4, 12)
    if old:
        newsreel(c)
        if c.f % 3 == 0:
            blend(img, 1.0, (0, 0, 0), 0.12)
    yield "ui"
    if old:
        caption(c, "1953", x=W - 8, y=FILM_TOP + 5, fnt=PRESS16, color=(236, 232, 220), anchor_="ra")
    elif c.t >= pres:
        caption(c, "73 YEARS LATER", y=FILM_TOP + 5, color=C["gold_hi"])


# --- 4: "I played Mandela: master of my fate, the captain of my soul." ----------------------------------------
# The stadium: he waves to the crowd as a wave rolls round; the card stunt flips to INVICTUS; a captain's
# cap drops onto his head; on "soul" he lifts the cup in a shower of gold.

@gag(SEC, 4)
def invictus(c, L):
    cut(c, "v4_stadium")
    master, captain, soul = wt(L, "master"), wt(L, "captain"), wt(L, "soul")
    m = c.st["morgan"]
    if c.t < master:
        c.vars["wave"] = lerp(-40, 360, ramp(c.t, L.t0 - 0.1, master - 0.1))
        m.update(arm="wave")
    if c.t >= master:
        c.vars.update(cards="INVICTUS", flip=ease_in_out(ramp(c.t, master, master + 0.45)))
    c.shot = (160, 96, 6) if c.t < captain else (150, 118, 12)
    if c.t >= soul:
        m.update(arm="up", mouth="grin", eyes="shut")
    yield "front"
    img = c.world
    tx, ty = anchor(c, "morgan", "top")
    if c.t >= captain - 0.2:
        p = ease_in(ramp(c.t, captain - 0.2, captain))
        paste(img, A.captain_hat(), tx + 2, lerp(ty - 70, ty + 4, p), "mb")
    if c.t >= soul:
        hx, hy = anchor(c, "morgan", "hand")
        glow = ramp(c.t, soul, soul + 0.15) * (1 - 0.5 * ramp(c.t, soul + 0.3, soul + 0.8))
        blend(img, mask(lambda d: d.ellipse((hx - 22, hy - 22, hx + 22, hy + 22), fill=255)), C["gold_hi"],
              0.25 * glow)
        paste(img, A.gold_cup(), hx, hy + 3, "mb")
        dd = ImageDraw.Draw(img)
        for k in range(70):                                     # confetti
            age = c.t - soul - rnd("cf", k) * 0.5
            if age > 0:
                x = 76 + rnd("cf-x", k) * 150 + math.sin(age * 6 + k) * 4
                y = 78 + age * (36 + 30 * rnd("cf-v", k))
                col = (0, 150, 90) if k % 3 == 0 else C["gold_hi"] if k % 3 == 1 else (255, 255, 255)
                dd.rectangle((x, y, x + 1, y + (k % 2)), fill=col)


# --- 5: "You were face-down in the dirt, whisperin' sweet nothings to a mole." -------------------------------
# Timber: Sir David falls flat on his face; whispers into a molehill, hearts rising; the mole comes up,
# blushes, and kisses him.

@gag(SEC, 5)
def sweet_nothings(c, L):
    cut(c, "v4_dirt")
    fdown, whisper, sweet, nothings, mole_t = (wt(L, "face-down"), wt(L, "whisperin"), wt(L, "sweet"),
                                               wt(L, "nothings"), wt(L, "mole"))
    c.shot = (182, 116, 12)
    d = c.st["david"]
    fall = ramp(c.t, fdown - 0.15, fdown + 0.1)
    if fall < 1:
        d.update(body="stand", rot=-90 * ease_in(fall), y=138, arm="down", eyes="shut" if fall > 0 else "open")
    else:
        d.update(mouth="o" if whisper <= c.t < mole_t and int(c.t * 8) % 2 else "smile", eyes="shut",
                 flush=2 if c.t >= mole_t else 1 if c.t >= sweet else 0)
    if 0 <= c.t - fdown - 0.1 < 0.25:
        c.add_shake(4 * (1 - (c.t - fdown - 0.1) / 0.25))
    yield "back"
    A.molehill(c.world)
    mx, my = A.MOLEHILL
    if c.t >= sweet - 0.1:
        rise = ease_out(ramp(c.t, sweet - 0.1, sweet + 0.2))
        spr = A.mole("kiss" if c.t >= mole_t else "peek", blush=c.t >= nothings)
        lean = 6 * ease_out(ramp(c.t, mole_t - 0.1, mole_t + 0.05))
        paste(c.world, spr, mx - lean, my - 8 + 12 * (1 - rise), "mb")
    yield "front"
    img = c.world
    if c.t >= fdown:
        puff(img, 176, 138, c.t - fdown - 0.1, 1.3, seed=5, color=(170, 130, 96), drift=(0, -8), life=1.0)
    hx, hy = anchor(c, "david", "head")
    if c.t >= whisper:
        hearts(img, hx + 8, hy - 6, c.t, whisper, n=6, every=0.2, seed=5)
    if c.t >= mole_t:
        paste_scaled(img, A.heart(), mx - 12, my - 26 - (c.t - mole_t) * 10, 1 + back_out(ramp(c.t, mole_t, mole_t + 0.2)),
                     "mm")
    yield "ui"
    if c.t >= mole_t:
        x, y = ui_at(c, mx - 8, my - 44)
        pop_text(c.ui, x, y, "SMOOCH!", c.t - mole_t, fnt=PRESS, top=(255, 170, 190), bottom=(236, 70, 100))


# --- 6: "Along Came a Spider: I caught the killer, closed the case." --------------------------------------------
# Noir: the detective's office, blinds, the lamp. A spider creeps across his desk; he slams a glass over
# it; THE KILLER; the file snaps shut; CASE CLOSED.

@gag(SEC, 6)
def case_closed(c, L):
    cut(c, "v4_office")
    caught, killer, closed, case = wt(L, "caught"), wt(L, "killer"), wt(L, "closed"), wt(L, "case")
    c.shot = (150, 102, 12)
    m = c.st["morgan"]
    if caught - 0.15 <= c.t < caught + 0.3:
        m.update(arm="fist", brows="angry")
    if 0 <= c.t - caught < 0.2:
        c.add_shake(4 * (1 - (c.t - caught) / 0.2))
    yield "front"
    img = c.world
    dy = A.DESK_Y
    sx = lerp(236, 136, ramp(c.t, L.t0, caught - 0.12))
    if c.t < caught:
        paste(img, A.spider(1, int(c.t * 12) % 2), sx, dy + 3, "mb")
    else:
        paste(img, A.spider(1, int(c.t * 20) % 2 if c.t < killer + 0.5 else 0), sx, dy + 3, "mb")
    gl = ease_in(ramp(c.t, caught - 0.12, caught))
    if gl > 0:
        paste(img, A.tumbler(), sx, lerp(dy - 60, dy + 4, gl), "mb")
    paste(img, A.case_file(c.t >= closed), 96, dy + 6, "mb")
    for k in range(7):                                          # the blinds' shadow over everything
        y = 30 + k * 16
        blend_poly(img, [(0, y + 40), (W, y - 30), (W, y - 24), (0, y + 46)], (0, 0, 0), 0.16)
    yield "ui"
    if killer <= c.t < closed + 0.2:
        tx, ty = ui_at(c, sx, dy - 6)
        CH.callout(c.ui, c.t - killer, "THE KILLER", tx, ty, tx + 36, ty - 30, (255, 90, 90))
    if c.t >= case:
        stamp(c.ui, W // 2, 84, "CASE CLOSED", size=16, age=c.t - case, angle=-10)


# --- 7: "You watched a spider eat her husband, zoomed in, and called it "grace."" -------------------------------
# Dusk, an orb web. A little suitor in a top hat brings her a rose: CHOMP. His hat drifts down. Crash zoom
# on the widow as she burps up a leg; cut to Sir David, moved, in a golden glow: "...grace."

@gag(SEC, 7)
def spider_grace(c, L):
    cut(c, "v4_web")
    eat, husband, zoomed, called, grace = wt(L, "eat"), wt(L, "husband"), wt(L, "zoomed"), wt(L, "called"), wt(L, "grace")
    c.hit_react["david"] = False
    wx, wy = A.WEB
    if c.t < zoomed:
        c.shot = (wx - 6, wy + 2, 12)
    elif c.t < called:
        pan(c, (wx - 6, wy + 2, 12), (wx, wy + 2, 24), zoomed, 0.35, ease_out)
    else:
        c.shot = (76, 128, 18)
    d = c.st["david"]
    d.update(arm="palm" if c.t >= called else "hold", eyes="shut" if c.t >= called else "open",
             mouth="smile" if c.t >= grace + 0.1 or c.t < grace else "o", brows="up",
             rim=0.7 if c.t >= called else 0.0, rim_color=(255, 214, 130))
    yield "back"
    img = c.world
    A.web(img, wx, wy, 52, torn=c.t >= eat)
    mx, my = lerp(248, wx + 14, ramp(c.t, L.t0, eat - 0.15)), lerp(20, wy - 16, ramp(c.t, L.t0, eat - 0.15))
    if c.t < eat:
        ImageDraw.Draw(img).line([(250, 0), (mx, my)], fill=(220, 220, 230))
        paste(img, A.spider(1, int(c.t * 10) % 2, hat=True, flower=True), mx, my, "mm")
        pose = "lunge" if c.t >= eat - 0.12 else "walk"
    else:
        pose = "burp" if c.t >= zoomed + 0.35 else "smug"
        if c.t >= eat and c.t < eat + 1.6:                      # his hat and rose drift down
            p = ramp(c.t, eat, eat + 1.6)
            paste_rot(img, A.top_hat(), mx + math.sin(p * 9) * 6, lerp(my, 150, p), math.sin(p * 11) * 30)
            paste_rot(img, A.rose(), mx - 6 + math.sin(p * 7) * 4, lerp(my, 150, min(1, p * 1.3)), 70 * p)
    paste(img, A.spider(2, 0, pose), wx, wy, "mm")
    if c.t >= called:
        hx, hy = anchor(c, "david", "head")
        blend(img, mask(lambda dd: dd.ellipse((hx - 22, hy - 22, hx + 22, hy + 22), fill=255)), (255, 226, 160),
              0.35 * ramp(c.t, called, called + 0.3))
    yield "front"
    if c.t < eat + 0.25 and c.t >= eat:
        burst(c.world, mx, my, 6, 13, C["red_hi"], spikes=9)
    yield "ui"
    if eat <= c.t < husband + 0.5:
        x, y = ui_at(c, mx, my - 16)
        pop_text(c.ui, x, y, "CHOMP!", c.t - eat, fnt=PRESS16)
    if zoomed <= c.t < called:
        CH.zoom_bar(c.ui, ramp(c.t, zoomed, zoomed + 0.35), y=FILM_TOP + 5)
    if c.t >= grace - 0.05:
        hx, hy = anchor(c, "david", "mouth")
        x, y = ui_at(c, hx, hy)
        bubble(c.ui, x + 30, y - 22, "...GRACE.", tail=(x + 6, y - 4), fnt=PRESS)


# --- 8: "I'm Lucius Fox. I built the Batmobile, the suit, the cave." ----------------------------------------------
# A dark cave. He presents; a spotlight slams on the finned black car, another on the armoured suit;
# then the whole cave lights up and the bats pour out.

def spotlight(img, x, top, bottom, w, a):
    if a > 0:
        blend_poly(img, [(x - 5, top), (x + 5, top), (x + w, bottom), (x - w, bottom)], (255, 250, 220), 0.3 * a)
        blend(img, mask(lambda d: d.ellipse((x - w, bottom - 6, x + w, bottom + 4), fill=255)), (255, 250, 220),
              0.35 * a)


@gag(SEC, 8)
def the_cave(c, L):
    cut(c, "v4_cave")
    built, batmobile, suit, cave = wt(L, "built"), wt(L, "Batmobile"), wt(L, "suit"), wt(L, "cave")
    c.vars["lights"] = ease_out(ramp(c.t, cave, cave + 0.2))
    if c.t < batmobile - 0.15:
        c.shot = (96, 110, 12)
    elif c.t < cave:
        pan(c, (96, 110, 12), (232, 110, 12), batmobile - 0.15, 0.2, ease_out)
    else:
        c.shot = (160, 96, 6)
    m = c.st["morgan"]
    if c.t >= built:
        m.update(arm="palm", facing=1)
    if 0 <= c.t - cave < 0.3:
        c.add_shake(5 * (1 - (c.t - cave) / 0.3))
    yield "back"
    img = c.world
    lit_car = ramp(c.t, batmobile, batmobile + 0.05)
    lit_suit = ramp(c.t, suit, suit + 0.05)
    spotlight(img, A.CAVE_CAR[0], 0, A.CAVE_CAR[1], 50, max(lit_car, c.get("lights")))
    spotlight(img, A.CAVE_SUIT[0], 0, A.CAVE_SUIT[1], 20, max(lit_suit, c.get("lights")))
    for spr, (x, y), lit in ((A.armoured_car(), A.CAVE_CAR, lit_car), (A.armour_suit(), A.CAVE_SUIT, lit_suit)):
        k = max(lit, c.get("lights"))
        paste(img, spr if k >= 1 else tint(spr, (8, 8, 14), 0.7 * (1 - k)), x, y, "mb")
    yield "front"
    if c.t >= cave:
        for k in range(24):                                     # the bats pour out
            age = c.t - cave - rnd("bat", k) * 0.4
            if age > 0:
                x = 150 + rnd("bat-x", k) * 60 + age * (80 + 90 * rnd("bat-v", k)) * (1 if k % 2 else -1)
                y = 60 + rnd("bat-y", k) * 30 - age * 60 + math.sin(age * 20 + k) * 3
                paste(c.world, A.bat(int(c.t * 12 + k) % 2), x, y, "mm")


# --- 9: "You sat nine days in a hide to watch a sloth misbehave." ------------------------------------------------
# A hide under the sloth's branch. Time-lapse: the days flash by (DAY 1 ... DAY 9), tally marks pile up on the
# hide; the sloth does not move. Then it grins, and drops one right on his lens. Two eyes light up in the slot.

LENS_MID = (A.SLOT[2] - 3, A.SLOT[1] - 1)               # the lens pokes out of the slot at 32 degrees
LENS_TIP = (LENS_MID[0] + 15, LENS_MID[1] - 10)


@gag(SEC, 9)
def nine_days(c, L):
    cut(c, "v4_hide")
    c.inset = False
    nine, watch, misbehave = wt(L, "nine"), wt(L, "watch"), wt(L, "misbehave")
    lapse = ramp(c.t, nine, watch - 0.1)
    day = 1 + int(8 * lapse) if c.t >= nine else 1
    c.vars["day"] = day
    if c.t < watch:
        c.shot = (160, 100, 6)
    else:
        pan(c, (160, 100, 6), (156, 90, 9), watch, 0.3, ease_out)
    yield "back"
    img = c.world
    if 0 < lapse < 1:                                           # night falls and lifts, nine times
        night = 0.5 - 0.5 * math.cos(lapse * 8 * 2 * math.pi)
        blend(img, 1.0, A.NIGHT, 0.62 * night)
    sx, sy = A.SLOTH_AT
    smug = c.t >= misbehave - 0.1
    paste(img, A.sloth("smug" if smug else "hang", blink=(not smug) and int(c.t * 2) % 5 == 0), sx, sy, "lt")
    hx, hy = A.HIDE
    paste(img, A.hide_hut(), hx, hy, "mb")
    d = ImageDraw.Draw(img)
    for k in range(day):                                        # tally marks scratched on the hide
        x = hx - 22 + k * 3 + (2 if k >= 5 else 0)
        if k == 4:
            d.line([(x - 12, hy - 14), (x + 1, hy - 19)], fill=(236, 226, 200))
        else:
            d.line([(x, hy - 19), (x, hy - 14)], fill=(236, 226, 200))
    # his lens pokes out of the slot, up at the sloth
    x0, y0, x1, y1 = A.SLOT
    paste_rot(img, A.long_lens(30), *LENS_MID, 32)
    delight = c.t >= misbehave + 0.35
    for ex in (x0 + 10, x0 + 17):                               # his eyes in the slot
        if delight:
            d.rectangle((ex - 1, y0 + 1, ex + 2, y0 + 4), fill=(255, 255, 255))
            d.rectangle((ex + 1, y0 + 1, ex + 2, y0 + 2), fill=INK)
        elif int(c.t * 3) % 7:
            d.rectangle((ex, y0 + 2, ex + 2, y0 + 4), fill=(255, 255, 255))
            d.point((ex + 2, y0 + 2), fill=INK)
    if c.t >= misbehave:                                        # plop
        p = ease_in(ramp(c.t, misbehave, misbehave + 0.3))
        px, py = lerp(sx + 37, LENS_TIP[0], p), lerp(sy + 30, LENS_TIP[1] - 2, p)
        paste(img, A.poo(), px, py, "mb")
        if p >= 1:
            for k in range(3):                                  # stink lines
                y = py - 10 - ((c.t * 12 + k * 4) % 10)
                d.line([(px - 4 + k * 4 + math.sin(c.t * 9 + k) * 1.5, y), (px - 4 + k * 4, y - 3)],
                       fill=(140, 160, 80))
    yield "ui"
    if c.t >= L.t0 - 0.1 and c.t < watch + 0.2:
        caption(c, f"DAY {day}", color=C["gold_hi"])
    if c.t >= misbehave + 0.3:
        x, y = ui_at(c, *LENS_TIP)
        y -= 26
        pop_text(c.ui, x, y, "PLOP", c.t - misbehave - 0.3, fnt=PRESS16)
        ex, ey = ui_at(c, A.SLOT[0] + 14, A.SLOT[1] - 6)
        if c.t >= misbehave + 0.35:
            pop_text(c.ui, ex, ey - 10, "!!", c.t - misbehave - 0.35, fnt=PRESS, top=(255, 255, 255),
                     bottom=C["gold"])


# --- 10: "Decades tellin' everybody the planet's on its final breath," -------------------------------------------
# The Earth in a hospital bed, oxygen mask and drip; the years flick by in the corner; Sir David at the
# bedside whispers his gravest; the heart monitor ticks on at a healthy 72. On "final breath" the planet
# fogs its mask with a long bored sigh and rolls its eyes.

@gag(SEC, 10)
def final_breath(c, L):
    cut(c, "v4_ward")
    everybody, planet, final, breath = wt(L, "everybody"), wt(L, "planet"), wt(L, "final"), wt(L, "breath")
    if c.t < planet:
        c.shot = (170, 104, 9)
    else:
        pan(c, (170, 104, 9), (184, 112, 18), planet, 0.3, ease_out)
    d = c.st["david"]
    d.update(arm="whisper", brows="worried", mouth="o" if int(c.t * 6) % 3 else "closed")
    yield "back"
    img = c.world
    bx, by = A.BED_HEAD
    rolled = c.t >= breath
    A.planet_patient(img, bx, by, 11, c.t, eyes="roll" if rolled else "shut" if c.t >= final else "half",
                     fog=ramp(c.t, final, breath) * (1 - ramp(c.t, breath + 0.4, breath + 0.9)))
    yield "front"
    if c.t >= breath:
        bx, by = A.BED_HEAD
        puff(c.world, bx + 2, by + 8, c.t - breath, 0.6, seed=8, color=(236, 240, 250), drift=(10, -6), life=0.9)
    yield "ui"
    if c.t < planet:
        year = 1970 + int(56 * ramp(c.t, L.t0, everybody + 0.5))
        caption(c, str(year), color=(236, 232, 220))
    if c.t >= breath + 0.1:
        x, y = ui_at(c, A.BED_HEAD[0] + 14, A.BED_HEAD[1] - 14)
        pop_text(c.ui, x, y, "*SIGH*", c.t - breath - 0.1, fnt=PRESS, top=(255, 255, 255), bottom=(200, 210, 230))


# --- 11: "Meanwhile you outlived the Concorde, the Queen, and the concept of death." ---------------------------------
# A churchyard. Sir David strolls through with his tea. Up come the headstones: CONCORDE, THE QUEEN (born
# the same year as him), and one for DEATH itself, the Reaper's empty robe slung over it, scythe leaning.

GRAVE_STONES = {"concorde": (("CONCORDE", "1969-2003"), 60, 42, "jet"),
                "queen": (("THE QUEEN", "1926-2022"), 60, 42, "crown"),
                "death": (("DEATH", "THE CONCEPT", "?-2026"), 72, 50, None)}


@gag(SEC, 11)
def outlived(c, L):
    cut(c, "v4_graveyard")
    concorde, queen, concept, death = wt(L, "Concorde"), wt(L, "Queen"), wt(L, "concept"), wt(L, "death")
    c.shot = (160, 96, 6)
    d = c.st["david"]
    stroll = ramp(c.t, L.t0 - 0.1, concorde + 0.3)
    d.update(x=lerp(40, 78, stroll), body=("walk1", "walk2")[int(c.t * 5) % 2] if stroll < 1 else "stand",
             arm="hold", mouth="o" if int(c.t * 3) % 2 else "smile", brows="up", eyes="half")
    yield "back"
    img = c.world
    for key, t0 in (("concorde", concorde), ("queen", queen), ("death", concept)):
        if c.t >= t0 - 0.05:
            rows, w, h, icon = GRAVE_STONES[key]
            x, y = A.GRAVES[key]
            rise = ease_out(ramp(c.t, t0 - 0.05, t0 + 0.2))
            stone = A.tombstone(rows, w, h, icon, (160, 160, 172) if key != "death" else (120, 118, 128),
                                text_y=24 if key == "death" else None)
            part = stone.crop((0, 0, stone.width, max(1, int(stone.height * rise))))
            paste(img, part, x, y, "mb")
            puff(img, x, y, c.t - t0, 1.0, seed=len(key), color=(130, 150, 110), drift=(0, -6), life=0.7)
    if c.t >= death - 0.2:
        x, y = A.GRAVES["death"]
        p = ease_in(ramp(c.t, death - 0.2, death))
        paste(img, A.reaper_robe(), x, lerp(y - 110, y - 26, p), "mb")
        paste_rot(img, A.scythe(), x + 40, y - 20, -14 * ease_out(ramp(c.t, death, death + 0.3)))
    yield "front"
    hx, hy = anchor(c, "david", "hand")
    paste(c.world, teacup(), hx + 2, hy, "mm")
    if c.t < concept:                                           # whistling a little tune
        mx, my = anchor(c, "david", "mouth")
        for k in range(2):
            age = (c.t * 1.4 + k * 0.5) % 1.0
            paste(c.world, A.note(k), mx + 4 + age * 10, my - 6 - age * 12, "mm")
    if 0 <= c.t - death < 0.2:
        c.add_shake(4)


# --- 12: "Respect. But this mic ain't a monarchy, and your reign is through." ----------------------------------------
# Sir David enthroned, crowned, holding a mic with its own little crown. Hoke bows. The mic's crown pops
# off on "monarchy"; on "reign", a rain cloud rolls over the throne and soaks him.

@gag(SEC, 12)
def reign_is_through(c, L):
    cut(c, "v4_throne")
    respect, monarchy, reign, through = wt(L, "Respect"), wt(L, "monarchy"), wt(L, "reign"), wt(L, "through")
    c.shot = (160, 106, 9) if c.t < reign else (200, 104, 12)
    m, d = c.st["morgan"], c.st["david"]
    if c.t < respect + 0.7:
        m.update(arm="palm", lean=2, eyes="shut")                     # a respectful bow
    d.update(mic=True, arm="mic", mouth="smirk", eyes="half", brows="up")
    wet = ramp(c.t, reign + 0.1, reign + 0.4)
    if c.t >= reign:
        d.update(mouth="frown", brows="worried", eyes="open", hat="none" if c.t >= through else "crown")
    yield "front"
    img = c.world
    mx, my = anchor(c, "david", "mic")
    if c.t < monarchy:
        paste(img, A.little_crown(), mx, my - 3, "mb")
    elif c.t < monarchy + 0.9:
        p = ramp(c.t, monarchy, monarchy + 0.9)
        paste_rot(img, A.little_crown(), mx + 30 * p, my - 3 - 40 * p + 60 * p * p, -500 * p)
    if c.t >= through:                                          # the sodden crown slips down over his eyes
        tx, ty = anchor(c, "david", "top")
        p = ease_in(ramp(c.t, through, through + 0.2))
        paste_rot(img, crown(), tx + 1 - 2 * p, ty + 2 + 7 * p, -14 * p)
    if c.t >= reign - 0.25:
        tx, ty = anchor(c, "david", "top")
        cx = lerp(tx + 120, tx, ease_out(ramp(c.t, reign - 0.25, reign)))
        A.rain_cloud(img, cx, ty - 22, c.t, w=48, rain=wet)
        if wet > 0:
            blend(img, mask(lambda dd: dd.ellipse((tx - 24, A.THRONE_AT[1] - 3, tx + 24, A.THRONE_AT[1] + 4),
                                                  fill=255)), (120, 160, 220), 0.5 * wet)
    yield "ui"
    if monarchy <= c.t < monarchy + 0.8:
        x, y = ui_at(c, mx, my - 18)
        pop_text(c.ui, x, y, "POP", c.t - monarchy, fnt=PRESS, top=(255, 255, 255), bottom=C["gold"])


# --- 13: "I made The Bucket List. You're a hundred. So let's review:" ------------------------------------------------
# A birthday do: a bucket marked BUCKET LIST on the table and a cake with 100 candles. The list pops out of
# the bucket; on "hundred" the candles go up like a bonfire; he puts his reading glasses on to review.

@gag(SEC, 13)
def bucket_list(c, L):
    cut(c, "v4_party")
    bucket_t, list_t, hundred, review = wt(L, "Bucket"), wt(L, "List"), wt(L, "hundred"), wt(L, "review")
    if c.t < hundred - 0.1:
        c.shot = (160, 100, 6) if c.t < bucket_t - 0.05 else (150, 100, 12)
    elif c.t < review - 0.2:
        c.shot = (226, 104, 12)
    else:
        c.shot = (110, 108, 12)
    m, d = c.st["morgan"], c.st["david"]
    m.update(x=96)
    if c.t >= review - 0.2:
        m.update(glasses=True, arm="hold", eyes="half")
    d.update(x=268, mouth="grin" if c.t < hundred else "o", eyes="open" if c.t < hundred else "wide",
             brows="up" if c.t < hundred else "worried")
    yield "back"
    img = c.world
    bx, by = A.BUCKET_AT
    if list_t <= c.t < review - 0.2:                            # the list rises out of the bucket
        paste(img, A.scroll(24), bx + 2, by - 14 - 22 * back_out(ramp(c.t, list_t, list_t + 0.25)), "mb")
    paste(img, A.bucket(), bx, by, "mb")
    kx, ky = A.CAKE_AT
    A.birthday_cake(img, kx, ky, c.t, inferno=ease_out(ramp(c.t, hundred, hundred + 0.3)))
    if c.t >= hundred:
        blend(img, mask(lambda dd: dd.ellipse((kx - 60, ky - 90, kx + 60, ky + 10), fill=255)), (255, 150, 60),
              0.2 + 0.05 * math.sin(c.t * 30))
    yield "front"
    img = c.world
    tx, ty = anchor(c, "david", "top")
    paste(img, A.party_hat(), tx + 1, ty + 3, "mb")
    if c.t >= review - 0.2:
        hx, hy = anchor(c, "morgan", "hand")
        paste(img, A.scroll(24), hx + 10, hy - 4, "mt")
    if c.t >= hundred:
        puff(img, kx, ky - 70, (c.t - hundred) % 0.9, 1.4, seed=int((c.t - hundred) / 0.9), color=(90, 86, 96),
             drift=(-6, -18), life=0.9)
    yield "ui"
    if hundred <= c.t < review - 0.2:
        x, y = ui_at(c, kx - 20, ky - 52)
        pop_text(c.ui, x, y, "WHOOMPH!", c.t - hundred, fnt=PRESS16, top=(255, 230, 120), bottom=(250, 110, 40))


# --- 14-15: the list itself --------------------------------------------------------------------------------------------
# "Swim with a blue whale": check. "Meet a mountain gorilla": check. -- the pen ticks each, a snapshot
# clipped beside it. "Beat Morgan Freeman"? The pen hovers... Nah (a cutaway: Morgan shakes his head).
# That box stays unchecked: a padlock snaps shut on it.

def item_box(k):
    return A.LIST_BOX_X, A.LIST_ITEMS[k][1]


def tick_path(k, p):
    """Where the nib is while ticking box k (p 0-1), matching props.checkbox's stroke."""
    x, y = item_box(k)
    m1, m2, m3 = (x + 2, y + 4), (x + 3, y + 7), (x + 12, y - 3)
    if p < 0.4:
        q = p / 0.4
        return lerp(m1[0], m2[0], q), lerp(m1[1], m2[1], q)
    q = (p - 0.4) / 0.6
    return lerp(m2[0], m3[0], q), lerp(m2[1], m3[1], q)


def draw_pen(img, x, y, t, shake=0.0):
    x += math.sin(t * 60) * shake
    paste(img, A.pen(), x + 1, y + 1, "mb")


def ticks(img, t, t1, t2):
    for k, tk in enumerate((t1, t2, None)):
        x, y = item_box(k)
        checkbox(img, x, y, ramp(t, tk - 0.1, tk + 0.12) if tk else 0.0)
    for k, (tk, kind) in enumerate(((t1, "whale"), (t2, "gorilla"))):
        if t >= tk + 0.1:
            y = item_box(k)[1]
            p = back_out(ramp(t, tk + 0.1, tk + 0.3))
            paste_rot(img, A.polaroid(kind), 240, y + 6 - 20 * (1 - p), -8 + 16 * k)


@gag(SEC, 14)
def checks(c, L):
    cut(c, "v4_list")
    t1, t2 = wt(L, "check"), wt(L, "check", 1)
    c.shot = (160, 88, 6)
    yield "back"
    img = c.world
    ticks(img, c.t, t1, t2)
    yield "front"
    img = c.world
    if c.t < t1 - 0.1:
        a = ramp(c.t, L.t0 - 0.15, t1 - 0.3)
        x, y = lerp(260, tick_path(0, 0)[0], ease_out(a)), lerp(170, tick_path(0, 0)[1], ease_out(a))
    elif c.t < t1 + 0.12:
        x, y = tick_path(0, ramp(c.t, t1 - 0.1, t1 + 0.12))
    elif c.t < t2 - 0.1:
        a = ease_in_out(ramp(c.t, t1 + 0.3, t2 - 0.3))
        x0, y0 = tick_path(0, 1)
        x1, y1 = tick_path(1, 0)
        x, y = lerp(x0, x1, a), lerp(y0, y1, a) - 10 * math.sin(math.pi * a)
    else:
        x, y = tick_path(1, ramp(c.t, t2 - 0.1, t2 + 0.12))
    draw_pen(img, x, y, c.t)


@gag(SEC, 15)
def unchecked(c, L):
    beat, nah, stays, unchecked_t = wt(L, "Beat"), wt(L, "Nah"), wt(L, "stays"), wt(L, "unchecked")
    aside = nah - 0.05 <= c.t < wt(L, "That") - 0.02
    if aside:                                                   # cutaway: Hoke shakes his head
        cut(c, "v4_party")
        c.inset = False
        c.shot = (96, 112, 18)
        m = c.st["morgan"]
        m.update(x=96, facing=1 if int((c.t - nah) * 8) % 2 else -1, arm="point", eyes="half", glasses=True)
        c.st["david"]["hidden"] = True
    else:
        cut(c, "v4_list")
        c.shot = (160, 88, 6) if c.t < beat + 0.3 else (140, 112, 12)
    t_prev = line_prev_checks(L)
    yield "back"
    if aside:
        return
    img = c.world
    ticks(img, c.t, *t_prev)
    x, y = item_box(2)
    if c.t >= stays - 0.1:
        p = ease_in(ramp(c.t, stays - 0.1, stays + 0.05))
        paste(img, A.padlock(c.t >= unchecked_t - 0.05), x + 5, lerp(y - 60, y + 12, p), "mb")
        if 0 <= c.t - stays - 0.05 < 0.2:
            c.add_shake(3)
    yield "front"
    img = c.world
    if c.t < nah:                                               # the pen hovers, trembling
        a = ease_out(ramp(c.t, L.t0 - 0.15, beat + 0.4))
        px, py = lerp(170, x + 4, a), lerp(110, y - 2, a)
        draw_pen(img, px, py, c.t, shake=ramp(c.t, beat + 0.4, nah) * 1.5)
    elif c.t < nah + 0.5:
        p = ease_in(ramp(c.t, wt(L, "That") - 0.02, wt(L, "That") + 0.3))
        draw_pen(img, x + 4 + 200 * p, y - 2 - 60 * p, c.t)
    yield "ui"
    if c.t >= unchecked_t:
        sx, sy = ui_at(c, x + 96, y + 20)
        stamp(c.ui, sx, sy, "NEVER", size=16, age=c.t - unchecked_t, angle=8)


def line_prev_checks(L):
    return line_t(SEC, 14, "check"), line_t(SEC, 14, "check", 1)


# --- 16: "Some birds ain't meant to be caged. Their feathers just too bright." ---------------------------------------
# Shawshank: a cell, GILDA on the wall, a barred window. Red holds up a gold birdcage of bright birds; opens
# it on "caged"; they hop out on "feathers", and on "bright" burst out through the bars into the sun.

BIRD_COLS = [((236, 80, 60), (250, 200, 60)), ((60, 150, 236), (120, 230, 250)), ((250, 210, 60), (250, 120, 60)),
             ((120, 210, 90), (240, 240, 120)), ((220, 90, 200), (255, 180, 240))]


def cage_spot(c):
    hx, hy = anchor(c, "morgan", "hand")
    return int(hx + 8), int(hy - 22)


@gag(SEC, 16)
def too_bright(c, L):
    cut(c, "v4_cell")
    caged, feathers, bright = wt(L, "caged"), wt(L, "feathers"), wt(L, "bright")
    c.shot = (214, 96, 9) if c.t < feathers else (176, 90, 6)
    m = c.st["morgan"]
    m.update(arm="hold", facing=1)
    if c.t >= bright:
        m.update(eyes="shut", mouth="smile", arm="up")
    c.vars["sun"] = ramp(c.t, bright - 0.05, bright + 0.1)
    yield "back"
    img = c.world
    sun = c.get("sun")
    wx0, wy0, wx1, wy1 = A.CELL_WINDOW
    if sun > 0:                                                 # the sun pours in through the bars
        blend_poly(img, [(wx0, wy0), (wx1, wy0), (wx1 - 60, 180), (wx0 - 110, 180)], (255, 240, 190),
                   0.25 * sun * (1 - 0.4 * ramp(c.t, bright + 0.3, bright + 1.0)))
    yield "front"
    img = c.world
    cx, top = cage_spot(c)
    if c.t < bright:
        A.birdcage(img, cx, top, ease_out(ramp(c.t, caged, caged + 0.25)))
    for k, (body, wing) in enumerate(BIRD_COLS):
        home = (cx - 8 + (k % 3) * 6, top + 20 + (k // 3) * 6)
        out = feathers + k * 0.1
        if c.t < out:
            paste_scaled(img, bird(int(c.t * 6 + k) % 2, body, wing), *home, 0.6, "mm")
        else:
            p = ramp(c.t, out, bright + 0.1)
            door = (cx + 16, top + 20)
            if p < 1:                                           # hop out to the door and flutter up by the bars
                x, y = lerp(home[0], door[0] + 10 + k * 5, p), lerp(home[1], wy1 - 10 - k * 4, p) - 8 * math.sin(p * 3)
            else:                                               # out through the bars and away
                q = c.t - bright - 0.1
                x, y = wx0 + 10 + k * 13 + q * (40 + 12 * k), wy1 - 12 - k * 5 - q * (90 + 20 * k)
            paste(img, bird(int(c.t * 12 + k) % 2, body, wing), x, y, "mm")
    if c.t >= bright:
        for k in range(10):
            x = wx0 + rnd("sp", k) * (wx1 - wx0)
            y = wy0 + rnd("sp-y", k) * (wy1 - wy0) - (c.t - bright) * 30
            if int(c.t * 10 + k) % 3:
                sparkle(img, x, y, 2, (255, 255, 230))
    if bright <= c.t < bright + 0.12:
        c.add_flash(0.55, (255, 244, 200))


# --- 17: "But you're a dodo, David: big, slow, and you can't take flight." ---------------------------------------------
# Tilt down from the empty window to the floor: a dodo, with Sir David's hair and brows. Big (a push in),
# slow (a slow-motion waddle); it flaps and hops at the window, and lands flat on its beak. Iris out.

DODO_X, DODO_Y = 112, 152


def dodo_state(c, L):
    """(x, y, pose, step, facing) for the dodo at time t."""
    david, can, flight = wt(L, "David"), wt(L, "can't"), wt(L, "flight")
    t = c.t
    if t < can:
        slow = t >= wt(L, "slow")
        rate = 1.6 if slow else 5
        x = DODO_X + (t - wt(L, "slow")) * 8 if slow else DODO_X
        return x, DODO_Y, "stand", int(t * rate) % 2, 1 if t >= david else -1
    x0 = DODO_X + (can - wt(L, "slow")) * 8
    if t < flight:
        p = ramp(t, can, flight)
        hop = abs(math.sin(p * math.pi * 3))
        return x0 + p * 40, DODO_Y - 14 * hop, "flap", 0, 1
    return x0 + 44, DODO_Y, "flop", 0, 1


@gag(SEC, 17)
def dodo(c, L):
    if c.t >= END_CARD:
        return
    cut(c, "v4_cell")
    c.inset = False
    dodo_t, big, can, flight = wt(L, "dodo"), wt(L, "big"), wt(L, "can't"), wt(L, "flight")
    x, y, pose, step, facing = dodo_state(c, L)
    if c.t < dodo_t:
        pan(c, (230, 70, 9), (x + 8, 124, 12), L.t0 - 0.2, 0.6, ease_in_out)
    elif c.t < big:
        c.shot = (x + 8, 124, 12)
    elif c.t < can:
        c.shot = (x + 10, 128, 18)
    else:
        c.shot = (170, 110, 9)
    m = c.st["morgan"]
    m.update(arm="cross", eyes="half", facing=-1)
    yield "front"
    img = c.world
    spr = A.dodo_david(pose, step)
    if facing < 0:
        spr = mirror(spr)
    paste(img, spr, x, y, "mb")
    if c.t >= flight:
        puff(img, x + 24, y - 1, c.t - flight, 0.7, seed=17, color=(150, 146, 140), drift=(10, -5), life=0.6)
        if c.t < flight + 0.2:
            c.add_shake(5 * (1 - (c.t - flight) / 0.2))
        for k in range(3):                                      # seeing stars
            a = c.t * 6 + k * 2.1
            sparkle(img, x + 8 + math.cos(a) * 9, y - 20 + math.sin(a) * 3, 1, C["gold"])
    yield "ui"
    if dodo_t <= c.t < big:
        tx, ty = ui_at(c, x + 4, y - 30)
        CH.callout(c.ui, c.t - dodo_t, "RAPHUS DAVIDUS", tx, ty, tx - 40, ty - 16, C["gold_hi"])
    if c.t >= flight + 0.15:
        sx, _ = ui_at(c, x + 6, y)
        stamp(c.ui, sx, FILM_TOP + 40, "EXTINCT", size=16, age=c.t - flight - 0.15, angle=-8)
    r = lerp(190, 0, ease_in_out(ramp(c.t, flight + 0.3, END_CARD - 0.04)))
    if r < 190:
        cx, cy = ui_at(c, x + 6, y - 12)
        iris(c, cx, cy, r)
