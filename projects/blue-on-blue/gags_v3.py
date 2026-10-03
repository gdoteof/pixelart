"""Verse 3: Gavin is fine, actually. The guest is the king of rent-free: he froze the rent and moved into a
mansion for free; he hates landlords and loves the landlord-in-chief; he's had more dates with Trump than
Melania, and Melania is glad; he's a fad with a crush who can't run for president, or a bus."""
from gagkit import *  # noqa: F403

MAM_DESK = (236, 116)


@gag("v3", 0)
def king_rent_free(c, L):
    a_k, a_r = age(L, "king"), age(L, "rent-free")
    if a_k > 0:
        pose(c, "mamdani", eyes="shut", mouth="grin", brows="up")
    yield "front"
    if a_k > 0:
        on_head(c, c.world, "mamdani", P.crown(), dy=-12 - int(max(0.0, 0.15 - a_k) * 60))
    yield "ui"
    if a_r > 0:
        shout(c, 240, 24, "RENT FREE", a_r, size=8)


@gag("v3", 1)
def froze_the_rent(c, L):
    a_froze, a_moved, a_free = age(L, "froze"), age(L, "moved"), age(L, "free")
    yield "front"
    if a_froze > 0:                                                    # the crown stays on, and the rent freezes
        on_head(c, c.world, "mamdani", P.crown(), dy=-12)
        pop_in(c.world, P.ice_block(), MAM_DESK[0] - 26, MAM_DESK[1] - 8, a_froze)
        if a_froze < 0.5:
            P.sparkles(c.world, MAM_DESK[0] - 26, MAM_DESK[1] - 10, a_froze, n=4, r=14, color="ice_hi")
    yield "ui"
    if a_moved > -0.2:
        boxes = clamp(int((a_moved + 0.2) / 0.15), 0, 6)
        inset(c, INSET, P.mansion(a_moved, who="mamdani", boxes=boxes), "GRACIE MANSION", k_in(a_moved + 0.2, 0.25))
    if a_free > 0:
        stamp(c, 186, 66, "FREE", a_free, world=False, angle=-14)


@gag("v3", 2)
def landlord_in_chief(c, L):
    a_loathe, a_love = age(L, "loathe"), age(L, "love")
    if a_loathe > -0.2 and a_love < 0:
        hold_up(c, "mamdani", P.placard("NO", "LANDLORDS"))
        pose(c, "mamdani", brows="angry", mouth="open" if V.singing(c, "newsom") else "frown")
    if a_love > 0:
        pose(c, "mamdani", eyes="heart", mouth="grin", brows="up", arms="chest", flush=1)
    yield "ui"
    if 0 < a_love < 1.2:
        P.sparkles(c.ui, *c.to_ui(287, 38), a_love, n=5, r=18, color="gold_hi")


T_REHUNG = when("v3", 2, "love")


@GAGS.span(T_REHUNG, 200.0)
def rehung(c, L):
    """From "love" on, the host's portrait is the landlord-in-chief's, and the plaque says so."""
    yield "back"
    paint_portrait(c.world, studio.portrait_pic(who="trump"))
    x0, _, x1, y1 = studio.PORTRAIT
    px, d = (x0 + x1) // 2, ImageDraw.Draw(c.world)
    w = max(pixel.text_width(s, SILK) for s in ("THE HOST", "LANDLORD")) // 2 + 2   # covers the old plaque
    d.rectangle((px - w - 1, y1 + 2, px + w + 1, y1 + 11), fill=INK)
    d.rectangle((px - w, y1 + 3, px + w, y1 + 10), fill=C["gold_sh"])
    d.text((px, y1 + 1), "LANDLORD", font=SILK, fill=C["gold_hi"], anchor="ma")


@gag("v3", 3)
def in_brief(c, L):
    a_brief, a_ex, a_you = age(L, "brief"), age(L, "ex"), age(L, "you")
    if -0.3 < a_brief and a_ex < 0.2:
        hold(c, "newsom", P.folder("IN", "BRIEF"), arms="show")
    yield "ui"
    if a_ex > -0.2:
        inset(c, INSET, P.family(0.0 if a_you < 0 else 1.0), "THE FAMILY", k_in(a_ex + 0.2, 0.25))


@gag("v3", 4)
def more_dates(c, L):
    a_d, a_mel = age(L, "dates"), age(L, "Melania")
    if a_mel > 0:
        pose(c, "mamdani", eyes="shut", mouth="grin", flush=1)
    yield "ui"
    if a_d > -0.3:
        inset(c, INSET, P.dates_chart(max(0.0, a_d + 0.3)), "THE DATA", k_in(a_d + 0.3, 0.25))


@gag("v3", 5, post=0.1)
def melania_glad(c, L):
    a, a_glad = age(L, "Melania"), age(L, "glad")
    yield "ui"
    inset(c, INSET, P.melania(0.0 if a_glad < 0 else 1.0), "MAR-A-LAGO", k_in(a + 0.3, 0.25))


@gag("v3", 6)
def future_and_fad(c, L):
    a_f, a_crush = age(L, "future"), age(L, "crush")
    if a_f > -0.2:
        hold_up(c, "newsom", P.placard("NEWSOM", "2028", bg="blue"))
        pose(c, "newsom", mouth=c.st["newsom"]["mouth"] if V.singing(c, "newsom") else "smile", brows="up")
    if a_crush > 0:
        pose(c, "mamdani", eyes="heart", mouth="grin", brows="up", flush=1)
    yield "ui"
    if a_crush > 0:
        think(c, "mamdani", P.crush_heart(), a_crush)


@gag("v3", 7)
def cant_run(c, L):
    a_pres, a_even = age(L, "president"), age(L, "even")
    if a_pres > -0.3 and a_even < 0:
        hold_up(c, "newsom", P.placard("MAMDANI", "2028", bg="white", fg="mk_blue"))
        pose(c, "newsom", mouth=c.st["newsom"]["mouth"] if V.singing(c, "newsom") else "smirk")
    if a_pres > 0.3:
        pose(c, "mamdani", mouth="o", brows="worried", eyes="wide")
    yield "ui"
    if a_pres > 0 and a_even < 0:                                      # a red sash across the sign
        x, y = c.to_ui(*c.anchor["newsom"]["held"])
        x += 6                                                         # off his face, onto the sign's edge
        fx.label(c.ui, (int(x), int(y) - 3 + (1 if a_pres < 0.08 else 0)), "INELIGIBLE", fnt=SILK, bg=C["red"],
                 fg=C["white"], border=INK, anchor="mm", th=6, text_dy=-3)
    if a_even > -0.2:
        inset(c, INSET, P.bus(max(0.0, a_even)), "THE FREE BUS", k_in(a_even + 0.2, 0.25))
