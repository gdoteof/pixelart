"""Verse 1: Trump has the floor. Bibi is a toy gun he keeps loaded, a cartoon coyote, a man with a
laundry bag; Trump has the jet, the letter on the fridge, and the pardon."""
from gagkit import *  # noqa: F403

BIBI_HEAD = (88, 66)
TRUMP_HANDS = (229, 96)


@gag("v1", 0)
def bb_gun(c, L):
    a = age(L, "loud")
    hold(c, "trump", mirror(P.bb_gun()), arms="hold")
    pose(c, "trump", eyes="squint")
    if 0 < a < 0.5:
        pose(c, "bibi", eyes="blink", brows="angry", react=False)
    yield "mid"
    if 0 <= a < 0.45:
        x, y = arc_pt(min(1.0, a / 0.25), (212, 94), BIBI_HEAD, 6)
        ImageDraw.Draw(c.world).ellipse((x - 1, y - 1, x + 1, y + 1), fill=C["steel"])
    yield "ui"
    shout(c, 205, 82, "PEW!", a, size=8, dur=0.6)


@gag("v1", 1)
def ammo(c, L):
    a, a_ok = age(L, "ammo"), age(L, "shoot")
    landed = a > 0.45
    if a_ok > -0.2:
        hold(c, "trump", P.folder("OK TO", "SHOOT"))
        pose(c, "trump", mouth="pout" if a_ok > 0.3 else c.st["trump"]["mouth"])
    elif a < 0:
        hold(c, "trump", P.crate(), arms="hold")
    if landed:
        hold(c, "bibi", P.crate(), arms="hold")
        pose(c, "bibi", mouth="frown" if a_ok > 0 else "smirk")
    yield "mid"
    if 0 <= a <= 0.45:
        fly(c.world, P.crate(), TRUMP_HANDS, (90, 96), a / 0.45, h=26, rot=-0.5)


@gag("v1", 2)
def cartoon_bomb(c, L):
    a = age(L, "cartoon")
    if a > -0.3:
        hold(c, "bibi", P.poster("bomb"))
        pose(c, "bibi", mouth="smirk" if not V.singing(c, "bibi") else c.st["bibi"]["mouth"], eyes="half")
    if age(L, "drew") > 0:
        pose(c, "trump", arms="point", mouth="grin", eyes="shut")
    if 0 < age(L, "whole") < 0.6:
        flash_press(c, "un", 4, age(L, "whole"))
    yield "ui"


def soot(c, img, who, k):
    """Wile E. after the bang: blackened, two blinking eyes, hair standing up."""
    x0, y0, x1, y1 = head_box(c, who)
    d = ImageDraw.Draw(img)
    for i in range(7):
        x = x0 + 8 + i * 4
        d.line([(x, y0 + 4), (x + (i % 3) - 1, y0 - 3 - (i % 2) * 2)], fill=C["ink"], width=2)
    ex, ey = c.anchor[who]["eye"]
    if int(k * 6) % 4 != 3:
        d.rectangle((ex - 1, ey - 1, ex + 1, ey + 1), fill=C["white"])
        d.rectangle((ex + 8, ey - 1, ex + 9, ey + 1), fill=C["white"])


@gag("v1", 3)
def acme(c, L):
    a_acme, a_boom = age(L, "Acme"), age(L, "Netanyahu")
    burnt = a_boom > 0.1
    hold(c, "bibi", P.poster("bomb") if not burnt else tint(P.poster("bomb"), C["ink"], 0.7))
    if burnt:
        c.st["bibi"].update(tint=((44, 36, 40), 0.8), react=False, mouth="o", eyes="open")
        c.add_shake(5 * max(0.0, 1 - a_boom / 0.3))
        if a_boom < 0.12:
            c.add_flash(0.4, C["gold_hi"])
    if a_boom > 0.2:
        pose(c, "trump", arms="point", mouth="grin", eyes="shut")
    yield "mid"
    if a_acme > 0:                                                     # an Acme crate lands on the table
        drop = min(1.0, a_acme / 0.3)
        y = lerp(-20, 124, ease_in(drop))
        put(c.world, P.crate("ACME", stamp=None), 160, y)
    hx, hy = c.anchor["bibi"]["held"]                                  # the board's centre
    if -1.2 < a_boom < 0:                                              # the fuse burns down
        p = 1 + a_boom / 1.2
        P.sparkles(c.world, hx + 6 - 5 * p, hy - 16 + 5 * p, c.t * 3, n=3, r=3)
    if 0 <= a_boom < 0.35:
        P.bang(c.world, hx, hy - 4, 10 + 40 * min(1.0, a_boom / 0.12), rot=a_boom * 3)
    if burnt:
        for k in range(3):
            P.puff(c.world, 70 + k * 18, 52 - min(30, a_boom * 30) - k * 4, 6 + k, seed=k)
        soot(c, c.world, "bibi", a_boom)


@gag("v1", 4)
def cigars(c, L):
    a = age(L, "box")
    if age(L, "They") < 0.4:
        c.st["bibi"].update(tint=((44, 36, 40), 0.8 * max(0.0, 1 - age(L, "They") / 0.4)))
    if a > -0.3:
        hold(c, "trump", P.cigar_box(), arms="hold")
        pose(c, "trump", eyes="shut" if a > 0.4 else "squint", mouth="grin" if a > 0.4 else c.st["trump"]["mouth"])
    yield "ui"


@gag("v1", 5)
def jumbo_jet(c, L):
    a_sad, a_jet = age(L, "Sad"), age(L, "jumbo")
    if a_jet > -0.2:
        hold(c, "trump", mirror(P.jet()), arms="hold")
        pose(c, "trump", eyes="squint", lean=3)
        if 0 < a_jet < 0.5:
            flash_press(c, "jet", 5, a_jet)
    else:
        pose(c, "trump", arms="shrug", mouth="pout", brows="up")
    yield "front"
    if a_jet > 0.3:
        P.sparkles(c.world, 229, 92, a_jet, n=4, r=24, seed=1)
    yield "ui"
    shout(c, 230, 46, "SAD!", a_sad, dur=1.0, top=C["white"], bottom=C["steel"])


@gag("v1", 6)
def heart_letter(c, L):
    a = age(L, "heart")
    if age(L, "letter") > -0.3:
        hold_up(c, "trump", P.letter(), lift=4)
    if a > 0:
        pose(c, "bibi", flush=1, mouth="smirk", eyes="shut")
    yield "front"
    if a > 0:
        for k in range(3):
            p = (a * 0.7 + k / 3) % 1.0
            put(c.world, P.heart(), 96 + 10 * math.sin(p * 6 + k), 70 - 30 * p)


def fridge_inset(c, a_letter, a_bomb, k):
    pic = Image.new("RGB", (84, 64), (226, 220, 206))
    fr = P.fridge()
    pic.paste(fr, (20, 0), fr)
    if a_letter > 0:                                                   # the letter on the freezer door
        pic.paste(P.letter(), (24, 1), P.letter())
        ImageDraw.Draw(pic).ellipse((40, 0, 43, 3), fill=C["red"])            # a magnet
    if a_bomb > 0:                                                     # the bomb art below it
        b = P.poster("bomb").resize((30, 22), Image.NEAREST)
        pic.paste(b, (27, 33), b)
        ImageDraw.Draw(pic).ellipse((40, 31, 43, 34), fill=C["blue"])
    inset(c, (118, 18, 202, 82), pic, "TRUMP'S FRIDGE", k)


@gag("v1", 7)
def on_the_fridge(c, L):
    a0 = age(L, "fridge")
    pose(c, "trump", arms="thumb", mouth=c.st["trump"]["mouth"])
    yield "ui"
    if a0 > -0.3:
        fridge_inset(c, 1.0, age(L, "bomb"), k_in(a0 + 0.3, 0.25) if L.t < end_of(L) + 0.5 else 1.0)


@gag("v1", 8)
def laundry(c, L):
    a = age(L, "laundry")
    if a > -0.2:
        hold(c, "bibi", P.laundry(), arms="hold")
        pose(c, "bibi", eyes="side", mouth="closed", brows="worried", react=False)
        pose(c, "trump", lean=0, mouth="frown")
    yield "front"
    if a > 0:
        P.stink(c.world, 90, 82, a)


@gag("v1", 9)
def whose_cigar(c, L):
    a, a_who = age(L, "cigar"), age(L, "who")
    hold(c, "bibi", P.laundry(), arms="hold")
    if a > -0.2:
        hold_up(c, "trump", P.cigar(), lift=1)
        pose(c, "trump", brows="up", eyes="open" if a_who < 0 else "squint")
    if a_who > 0:
        pose(c, "bibi", sweat=True, flush=1, eyes="side", mouth="o", react=False)
    yield "ui"
    shout(c, 240, 40, "?", a_who, dur=1.2, top=C["white"], bottom=C["gold"])


def turkey_walk(c, img, t_in, x_to=150, t_out=None, medal=False):
    """The turkey struts in from the right and stops in front of the table (and leaves at t_out)."""
    a = c.t - t_in
    if a < 0:
        return None
    x = lerp(340, x_to, ease_out(min(1.0, a / 0.9)))
    if t_out is not None and c.t > t_out:
        x = lerp(x_to, 340, ease_in(min(1.0, (c.t - t_out) / 0.9)))
    hop = 1 if int(c.t * 8) % 2 else 0
    tk = P.turkey("open" if int(c.t * 3) % 3 == 0 else "closed", medal=medal)
    tk = mirror(tk)
    put(img, tk, x, 142 - hop)
    return x


@gag("v1", 10)
def pardon(c, L):
    a = age(L, "pardon")
    if a > -0.2:
        hold(c, "trump", P.folder("PARDON"))
        pose(c, "trump", mouth=c.st["trump"]["mouth"])
    if 0 < age(L, "live") < 0.6:
        flash_press(c, "tv", 6, age(L, "live"))
    yield "mid"
    turkey_walk(c, c.world, wt(L, "turkey") - 0.5)


@gag("v1", 11)
def farm_upstate(c, L):
    a = age(L, "farm")
    if a > 0:
        pose(c, "trump", arms="wave", mouth=c.st["trump"]["mouth"], eyes="squint")
    yield "back"
    if a > 0:
        paint_portrait(c.world, P.farm())
    yield "mid"
    turkey_walk(c, c.world, L.t0 - 5, t_out=end_of(L) + 0.3)
    yield "ui"
    a_vp = age(L, "VP")
    if a_vp > 0:
        x, y = c.to_ui(166, 52)
        fx.arrow(c.ui, int(x + 22), int(y - 14), int(x + 4), int(y - 2), color=C["gold"])
        fx.label(c.ui, (int(x + 20), int(y - 24)), "VP", SILK, bg=C["white"], fg=C["ink"], th=5, text_dy=-4)
