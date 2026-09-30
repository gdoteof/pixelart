"""Verse 4: Washington's closing verse.

Lines 0-3 stay on the shores and are sober: the world dims, an iron chain hangs across the Atlantic, and
the facts come on documents and dates. Line 4 turns it: two small ships sail up to the wharf and the quay,
the Georges jump aboard, and on "war" the video cuts to the ship duel (ships.py). From line 5 on the
Georges trade broadsides and Royal George comes apart a stage at a time: holed sails, the main topmast
with the Hanover family tree chopped away, then dismasted and burning after the big broadside. The last
lines slow down to the history of Washington giving power back, and end on George's crown going over the side.
"""
import numpy as np

import ships
from gagkit import (C, INK, PRESS, PRESS16, PRESS24, SILK, W, Canvas, Image, ImageDraw, arrow, back_out,
                    between, big_text, bubble, burst, crown_sprite, ease_in, ease_in_out, ease_out, envelope,
                    face, gag, hatchet, label, lerp, lru_cache, math, mirror, mix, parchment, paste, paste_rot,
                    pop_dy, pop_text, ramp, rnd, scaled, sparkle, splash, stamp, strike, teacup, text_width,
                    tint, ui_at, anchor, planet, coin, wt, end_t, cherry_tree, line_t)
from pixelart import pixel

SS = ships.SHIP_SHOTS
INKB = (70, 40, 20)                       # ink on parchment


# --- shared helpers -------------------------------------------------------------------------------

def shot(c, s):
    c.shot = SS[s] if isinstance(s, str) and s in SS else s


def glide(c, a, b, t0, dur, ease=ease_in_out):
    a = SS.get(a, a) if isinstance(a, str) else a
    b = SS.get(b, b) if isinstance(b, str) else b
    c.shot = between(a, b, ramp(c.t, t0, t0 + dur), ease)


def at_sea(c, s="duel", **ship):
    """Set up a frame on the ship set: both Georges on deck, the crier gone, an explicit shot."""
    c.scene = "ships"
    c.ship = ship
    ships.place(c)
    shot(c, s)


def sober(c, mood=0.5):
    c.hit_react["george"] = False
    c.hitfx = False
    c.mood = mood
    c.calm = 0.5


def doc(img, cx, y, lines, title=None, sign=None, pad=6, fnt=SILK):
    """A parchment document centred on cx with its top at y; returns its box."""
    widths = [text_width(s, fnt) for s in lines]
    if title:
        widths.append(text_width(title, PRESS))
    if sign:
        widths.append(text_width(sign, SILK))
    w = max(widths) + 2 * pad
    lh = 8 if fnt is SILK else fnt.size + 2
    h = 5 + (11 if title else 0) + lh * len(lines) + (9 if sign else 0)
    x0 = int(cx - w / 2)
    parchment(img, (x0, int(y), x0 + w, int(y) + h), rolled=True)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    yy = int(y) + 3
    if title:
        d.text((int(cx), yy), title, font=PRESS, fill=INKB, anchor="ma")
        yy += 11
    for s in lines:
        d.text((int(cx), yy - (2 if fnt is SILK else 0)), s, font=fnt, fill=INKB, anchor="ma")
        yy += lh
    if sign:
        d.text((x0 + w - 5, yy - 1), sign, font=SILK, fill=C["red_sh"], anchor="ra")
    return (x0, int(y), x0 + w, int(y) + h)


def plate(img, cx, y, lines, bg=C["band"], fg=C["text"], border=C["band_edge"], fnt=SILK, first=None):
    """A dark caption plate with one or more centred lines (the first can be in its own colour)."""
    w = max(text_width(s, fnt) for s in lines) + 8
    lh = 8 if fnt is SILK else fnt.size + 2
    h = lh * len(lines) + 4
    x0 = int(cx - w / 2)
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    d.rectangle((x0 - 1, y - 1, x0 + w + 1, y + h + 1), fill=INK)
    d.rectangle((x0, y, x0 + w, y + h), fill=bg, outline=border)
    for i, s in enumerate(lines):
        d.text((int(cx) + 1, y + 2 + i * lh - (2 if fnt is SILK else 0)), s, font=fnt,
               fill=(first if first and i == 0 else fg), anchor="ma")
    return (x0, y, x0 + w, y + h)


def slide_in(age, out_age=None, dist=60):
    """Vertical offset for a caption that drops in (and later lifts out)."""
    if age < 0:
        return None
    dy = pop_dy(age, 0.2, 10) or 0
    if out_age is not None and out_age > 0:
        dy -= int(ease_in(out_age / 0.35) * dist)
    return dy


def on_ui(c, x, y):
    return ui_at(c, x, y)


# --- the shores: chain, slave ships, tea -------------------------------------------------------------

CHAIN_A, CHAIN_B, CHAIN_SAG = (99, 120), (220, 120), 21


def chain(img, t, t_in, t_out=None):
    """An iron chain slung across the Atlantic from the wharf to the quay: it drops in, and later sinks."""
    if t < t_in:
        return
    dy = -int((1 - back_out(ramp(t, t_in, t_in + 0.45), 1.2)) * 70)
    if t_out is not None:
        dy += int(ease_in(ramp(t, t_out, t_out + 0.7)) * 50)
    d = ImageDraw.Draw(img)
    (ax, ay), (bx, by) = CHAIN_A, CHAIN_B
    n = int((bx - ax) / 5)
    pts = []
    for i in range(n + 1):
        s = i / n
        x = lerp(ax, bx, s)
        y = lerp(ay, by, s) + CHAIN_SAG * 4 * s * (1 - s) + dy + math.sin(t * 1.3 + s * 3) * 0.6
        pts.append((int(round(x)), int(round(y))))
    for i, (x, y) in enumerate(pts):                          # links: rings face-on, then edge-on bars
        if y > 150:
            continue
        if i % 2 == 0:
            d.ellipse((x - 3, y - 2, x + 3, y + 2), outline=INK)
            d.ellipse((x - 2, y - 1, x + 2, y + 1), outline=C["steel_sh"])
            d.line((x - 1, y - 1, x + 1, y - 1), fill=C["steel"])
            if i % 4 == 0:
                d.point((x - 1, y - 1), fill=C["glint"])
        else:
            d.rectangle((x - 2, y - 1, x + 2, y + 1), fill=INK)
            d.line((x - 1, y, x + 1, y), fill=C["steel"])
    for x, y in (CHAIN_A, CHAIN_B):                           # the ring bolts it hangs from
        d.rectangle((x - 1, y - 2 + min(dy, 0), x + 1, y + min(dy, 0)), fill=C["iron"])


@lru_cache(maxsize=None)
def slaver():
    """A far-off ship in silhouette, under a red ensign, bow west."""
    s = tint(mirror(ships.small_ship("royal")), (26, 20, 44), 0.92)
    s = s.resize((s.width // 2, s.height // 2), Image.NEAREST)
    d = ImageDraw.Draw(s)
    d.rectangle((11, 0, 15, 2), fill=C["flag_red"] + (255,))
    return s


@lru_cache(maxsize=None)
def tea_table():
    """A small table with a sugar bowl."""
    s = Canvas(22, 16)
    s.rect((1, 5, 20, 6), "wood_hi")
    s.line([(3, 7), (3, 15)], "wood_sh"); s.line([(18, 7), (18, 15)], "wood_sh")
    s.line([(3, 12), (18, 12)], "wood_sh")
    s.poly([(4, 1), (12, 1), (11, 4), (5, 4)], "white")      # the sugar bowl
    s.line([(5, 3), (11, 3)], "sash")
    s.pxs([(6, 0), (8, 0), (10, 0)], "white")
    s.px((7, 0), "white_sh")
    return s.done()


@lru_cache(maxsize=None)
def coin_stack_coin():
    return coin("george", 4)


# --- Verse 4, line by line ----------------------------------------------------------------------------

@gag("v4", 0, pre=0.6)
def chains(c, L):
    """Sober. The light drops, an iron chain falls across the ocean between the two shores on 'chains',
    and a line of dark ships under red ensigns crosses the horizon on 'ships'."""
    sober(c, 0.5 * ramp(c.t, 169.2, 170.2))
    c.shot = "wide"
    t_chain, t_ships = wt(L, "chains"), wt(L, "ships")
    w, g = c.st["washington"], c.st["george"]
    w.update(arm="down" if c.t < t_chain else "point")
    g.update(arm="down", mouth="closed", brows="neutral", eyes="open")
    yield "back"
    for i in range(5):                                         # the convoy, crossing east to west
        x = 206 + i * 38 - (c.t - (t_ships - 1.2)) * 24
        if c.t >= t_ships - 1.2 and 112 < x < 206:
            paste(c.world, slaver(), x, 100 + (i % 2), "mb")
    chain(c.world, c.t, t_chain)
    yield "ui"
    if c.t >= t_ships + 0.2:
        age = c.t - t_ships - 0.2
        plate(c.ui, 160, 104 + (pop_dy(age, 0.2, 4) or 0), ["BRITISH SLAVE SHIPS"], fg=C["dim"])


@gag("v4", 1)
def sugar(c, L):
    """George at his tea on the quay. 'Liverpool' puts up a caption and a stack of coins; he stirs his cup
    through the line, the sugar bowl is labelled on 'sugar', and on 'tea' the spoon stops."""
    sober(c, 0.5)
    c.shot = "london"
    t_liv, t_rich, t_stir, t_sugar, t_tea = (wt(L, "Liverpool"), wt(L, "rich"), wt(L, "stirred"),
                                              wt(L, "sugar"), wt(L, "tea"))
    g = c.st["george"]
    g.update(arm="hold", mouth="closed", brows="neutral", eyes="open" if c.t < t_tea + 0.1 else "side")
    table_x, table_y = 226, 115
    yield "back"
    chain(c.world, c.t, 0)
    paste(c.world, tea_table(), table_x, table_y, "mb")
    yield "front"
    hx, hy = anchor(c, "george", "hand")
    cup = mirror(teacup())
    paste(c.world, cup, hx - 2, hy + 1, "mb")
    d = ImageDraw.Draw(c.world)
    cx, cy = hx - 3, hy - 7
    if c.t < t_tea:                                            # the spoon, going round
        a = c.t * 11 if c.t >= t_stir - 0.4 else 0.0
        d.line((cx + round(math.cos(a) * 2), cy + 5, cx + 1 + round(math.cos(a) * 1), cy - 1), fill=C["steel"])
    else:
        d.line((cx, cy + 5, cx + 2, cy - 1), fill=C["steel"])
    lump = ramp(c.t, t_sugar + 0.1, t_sugar + 0.45)
    if 0 < lump < 1:                                           # a lump of sugar from the bowl to the cup
        bx, by = table_x - 4, table_y - 16
        x = lerp(bx, cx, lump)
        y = lerp(by, cy + 2, lump) - 8 * 4 * lump * (1 - lump)
        d.rectangle((x, y, x + 1, y + 1), fill=C["white"])
    yield "ui"
    if c.t >= t_liv:
        age = c.t - t_liv
        dy = pop_dy(age, 0.2, 6) or 0
        plate(c.ui, 100, 6 + dy, ["LIVERPOOL", "BRITAIN'S LEADING SLAVE-TRADE PORT"], first=C["gold"])
        n = int(clamp01((c.t - t_rich) / 0.5) * 6) if c.t >= t_rich else 0
        for i in range(n):
            paste(c.ui, scaled(coin_stack_coin(), 2), 214 + (i % 2), 30 - i * 5, "mm")
    if c.t >= t_sugar - 0.1:
        ux, uy = on_ui(c, table_x - 3, table_y - 15)
        label(c.ui, (ux, uy - 8 + (pop_dy(c.t - t_sugar + 0.1, 0.2, 4) or 0)), "SUGAR: WEST INDIES",
              bg=C["paper"], anchor="mb")


def clamp01(v):
    return min(1.0, max(0.0, v))


WILL = ["UPON THE DECEASE OF MY WIFE, IT IS MY", "WILL & DESIRE THAT ALL THE SLAVES WHICH",
        "I HOLD IN MY OWN RIGHT, SHALL RECEIVE", "THEIR FREEDOM."]


def timeline(img, t, t0, t1, t2, t_out=None):
    """1799 to 1833 as a chain: Washington's will, George III's death, the Abolition Act."""
    if t < t0:
        return
    dy = 0
    if t_out is not None and t >= t_out:
        dy = -int(ease_in(ramp(t, t_out, t_out + 0.4)) * 80)
    y = 40 + dy
    x0, x1 = 70, 250
    xs = {1799: x0, 1820: x0 + (x1 - x0) * 21 / 34, 1833: x1}
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    reach = lerp(x0, x1, ease_out(ramp(t, t0, t2)) if t2 > t0 else 1.0)
    for x in range(x0, int(reach) + 1, 4):                    # the chain, running on past his death
        if (x - x0) % 8 == 0:
            d.ellipse((x - 2, y - 1, x + 2, y + 1), outline=C["iron_hi"])
        else:
            d.line((x - 1, y, x + 1, y), fill=C["steel_sh"])
    marks = [(1799, t0, ["WASHINGTON'S", "WILL"], C["buff"]), (1820, t1, ["GEORGE III", "DIES"], C["gold"]),
             (1833, t2, ["SLAVERY", "ABOLITION ACT"], C["white"])]
    for year, tm, words, col in marks:
        if t < tm:
            continue
        x = int(xs[year])
        pd = pop_dy(t - tm, 0.18, 5) or 0
        d.line((x, y - 4, x, y + 4), fill=col)
        big_text(img, (x, y - 18 + pd), str(year), PRESS, top=col, bottom=mix(col, INK, 0.3), anchor="ma")
        for i, s in enumerate(words):
            outline_label(img, x, y + 7 + i * 8 + pd, s)


def outline_label(img, x, y, s):
    from engine import outline_text
    outline_text(img, (int(x), int(y) - 2), s, SILK, C["text"], INK, "ma")


@gag("v4", 2)
def the_will(c, L):
    """'My will freed mine': the passage from Washington's will, as written (it took effect on his wife's
    death). 'Your empire kept its chains after you were dead': a chain runs along a timeline from 1799
    past George III's death in 1820 to the Slavery Abolition Act of 1833."""
    sober(c, 0.5)
    c.shot = "wide"
    t_will, t_kept, t_after, t_dead = wt(L, "will"), wt(L, "kept"), wt(L, "after"), wt(L, "dead")
    w, g = c.st["washington"], c.st["george"]
    w.update(arm="palm" if c.t < t_kept else "point")
    g.update(arm="down", mouth="closed", brows="neutral")
    if c.t >= t_dead:
        g.update(eyes="side")
    yield "back"
    chain(c.world, c.t, 0)
    yield "ui"
    if c.t >= t_will - 0.1:
        age = c.t - t_will + 0.1
        dy = slide_in(age, c.t - (t_kept - 0.2), 90)
        if dy is not None and dy > -80:
            doc(c.ui, 160, 4 + dy, WILL, title="LAST WILL", sign="G. WASHINGTON, 1799")
    timeline(c.ui, c.t, t_kept + 0.05, t_after, t_dead)


@gag("v4", 3)
def preach(c, L):
    """Washington points; on 'crown' the shot closes on George's crown with a glint, and on 'head' George
    looks away. The chain sinks as the line ends."""
    sober(c, 0.5)
    t_free, t_crown, t_head = wt(L, "freedom"), wt(L, "crown"), wt(L, "head")
    c.shot = "two" if c.t < t_crown - 0.05 else "londonx"
    w, g = c.st["washington"], c.st["george"]
    w.update(arm="point" if c.t >= wt(L, "preach") else "down")
    g.update(arm="down", mouth="closed", brows="neutral", eyes="open")
    if c.t >= t_crown + 0.5:
        g.update(eyes="side")
    if c.t >= t_head:
        g.update(brows="worried", eyes="shut" if c.t < t_head + 0.5 else "side")
    yield "back"
    chain(c.world, c.t, 0, t_out=L.t1 - 0.8)
    yield "ui"
    timeline(c.ui, c.t, 0, 0, 0, t_out=t_free - 0.3)
    if 0 <= c.t - t_crown < 0.5:
        hx, hy = anchor(c, "george", "top")
        ux, uy = on_ui(c, hx + 3, hy + 1)
        s = 2 + int(3 * math.sin(math.pi * (c.t - t_crown) / 0.5))
        sparkle(c.ui, ux, uy, s, C["gold_hi"])


# --- line 4: the turn ----------------------------------------------------------------------------------

A_Y0 = 100                                     # the small ships' top row (waterline 146)


def small_positions(c):
    p = ease_out(ramp(c.t, 185.30, 186.15))
    xa = lerp(-72, 96, p)
    xr = lerp(326, 158, p)
    bob = int(round(math.sin(c.t * 3.0)))
    return xa, xr, bob


def hop(c, who, a, b, t0, dur=0.42):
    p = ramp(c.t, t0, t0 + dur)
    s = c.st[who]
    if p <= 0:
        return
    s.update(x=lerp(a[0], b[0], p), y=lerp(a[1], b[1], p) - 16 * 4 * p * (1 - p), shadow=False)


@gag("v4", 4)
def still_won(c, L):
    """The turn. A plain chart: battles won, a longer bar of battles lost, CORRECT stamped on 'Correct'.
    Then a third bar, WAR, runs full while two small ships sail up to the wharf and the quay, the Georges
    jump aboard on 'still won', and on 'war' a flash cuts to the ship duel."""
    t_lost, t_won_q, t_corr, t_still, t_war = (wt(L, "lost"), wt(L, "won"), wt(L, "Correct"), wt(L, "still"),
                                                wt(L, "war"))
    c.hit_react["george"] = False
    c.hitfx = False
    if c.t >= t_war:
        at_sea(c, "duel")
        c.add_flash(max(0.0, 1 - (c.t - t_war) / 0.25))
        yield "ui"
        war_won(c, t_war)
        return
    c.mood = 0.5 * (1 - ramp(c.t, L.t0, L.t0 + 0.6))
    c.shot = "wide"
    xa, xr, bob = small_positions(c)
    w, g = c.st["washington"], c.st["george"]
    w.update(arm="point" if c.t < t_corr else "fist")
    g.update(arm="cross", brows="up", mouth="smirk" if c.t < t_corr else "frown")
    hop(c, "washington", (w["x"], w["y"]), (96 + 40, A_Y0 + 36), t_still - 0.1)
    hop(c, "george", (g["x"], g["y"]), (158 + 43, A_Y0 + 36), t_still)
    yield "back"
    al, rg = ships.small_ship("alfred"), mirror(ships.small_ship("royal"))
    for x, s, sgn in ((xa, al, -1), (xr, rg, 1)):
        paste(c.world, s, x, A_Y0 + bob, "lt")
        moving = 0 < ramp(c.t, 185.30, 186.15) < 1
        if moving:                                          # a wake behind the stern
            d = ImageDraw.Draw(c.world)
            sx = x + (0 if sgn < 0 else 66)
            for k in range(5):
                d.line((sx + sgn * (3 + k * 5), 146 + (k % 2), sx + sgn * (5 + k * 5), 146 + (k % 2)),
                       fill=C["white"])
    yield "front"
    for x, s in ((xa, al), (xr, rg)):                      # the near side of each hull hides their boots
        part = s.crop((0, 35, 66, 54))
        c.world.paste(part, (int(x), A_Y0 + 35 + bob), part)
    yield "ui"
    chart(c, t_lost, t_won_q, t_corr, t_still, t_war)


def chart(c, t_lost, t_won, t_corr, t_still, t_war):
    """A bar chart without a scale: battles won, battles lost (longer), and the war."""
    ui = c.ui
    x0, y0 = 96, 22
    d = ImageDraw.Draw(ui)
    d.fontmode = "1"
    age = c.t - (t_lost - 0.2)
    if age < 0:
        return
    dy = pop_dy(age, 0.2, 8) or 0
    rows = [("WON", C["green_hi"], 44, t_won - 0.1), ("LOST", C["red_hi"], 78, t_lost + 0.1)]
    if c.t >= t_still - 0.3:
        rows.append(("WAR", C["gold"], 96, t_still))
    h = 14 + 10 * len(rows)
    d.rectangle((x0 - 1, y0 - 1 + dy, x0 + 129, y0 + h + 1 + dy), fill=INK)
    d.rectangle((x0, y0 + dy, x0 + 128, y0 + h + dy), fill=C["band"], outline=C["band_edge"])
    d.text((x0 + 64, y0 + 3 + dy), "BATTLES", font=PRESS, fill=C["gold"], anchor="ma")
    for i, (name, col, full, ts) in enumerate(rows):
        y = y0 + 14 + i * 10 + dy
        d.text((x0 + 4, y - 2), name, font=SILK, fill=C["text"])
        n = int(full * ease_out(ramp(c.t, ts, ts + (0.5 if name != "WAR" else t_war - ts))))
        if n > 0:
            d.rectangle((x0 + 26, y, x0 + 26 + n, y + 5), fill=col)
            d.line((x0 + 26, y, x0 + 26 + n, y), fill=mix(col, (255, 255, 255), 0.4))
    if t_corr <= c.t < t_still - 0.3:
        stamp(ui, x0 + 64, y0 + h + 14 + dy, "CORRECT.", C["green_hi"], angle=-6, size=16, age=c.t - t_corr)


def war_won(c, t_war):
    age = c.t - t_war
    if 0 <= age < 1.3:
        y = 26 - int(ease_in(ramp(age, 1.0, 1.3)) * 60)
        pop_text(c.ui, 160, y, "WAR: WON", age, PRESS24, top=C["gold_hi"], bottom=C["gold"])


# --- at sea ------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def colonies_map():
    s = Canvas(42, 26)
    s.rect((1, 1, 40, 24), "paper")
    s.line([(1, 24), (40, 24)], "paper_sh"); s.line([(40, 1), (40, 24)], "paper_sh")
    land = [(2, 8), (17, 8), (21, 11), (18, 14), (22, 17), (19, 20), (22, 23), (2, 23)]
    s.poly(land, (170, 190, 120))
    s.d.line(land[1:-1], fill=Canvas.c((110, 140, 70)))
    for x, y in ((27, 12), (31, 17), (35, 21)):
        s.line([(x, y), (x + 2, y)], (150, 170, 200))
    s.text((21, 0), "AMERICA", "ink", anchor="ma")
    return s.done()


@gag("v4", 5)
def lost_a_continent(c, L):
    """The duel opens: Royal George fires first and misses. On 'continent' George is left holding a map of
    America, and his own broadside's blast tears it out of his hands and away west. On 'fighting for?'
    Alfred fires back and holes Royal George's sails and hull."""
    t_cont, t_what = wt(L, "continent"), wt(L, "What")
    at_sea(c, "duel")
    if t_cont - 0.5 <= c.t < t_what - 0.1:
        shot(c, "royal")
    g, w = c.st["george"], c.st["washington"]
    t_map = t_cont - 0.5
    t_gone = t_cont + 0.12
    if t_map <= c.t < t_gone:
        g.update(arm="hold", mouth="smirk", brows="up")
    elif c.t >= t_gone:
        face(c, "george", mouth="o", brows="worried", eyes="wide" if c.t < t_gone + 0.6 else "open")
        g.update(arm="palm" if c.t < t_gone + 0.6 else "cross")
    if c.t >= t_what:
        w.update(arm="point")
    yield "back"
    yield "front"
    if t_map <= c.t < t_gone:
        hx, hy = anchor(c, "george", "hand")
        paste(c.world, colonies_map(), hx - 8, hy - 4, "mt")
    elif t_gone <= c.t < t_gone + 1.2:
        p = (c.t - t_gone) / 1.2
        hx, hy = anchor(c, "george", "hand")
        x = hx - 6 - ease_in(p) * 120 - p * 10
        y = hy - 10 - math.sin(p * math.pi) * 34 + p * 6
        m = colonies_map()
        m = m.resize((m.width, max(4, int(m.height * abs(math.cos(p * 7))))), Image.NEAREST)
        paste_rot(c.world, m, x, y, math.sin(p * 9) * 25)
    yield "ui"
    war_won(c, line_start_war())


def line_start_war():
    return line_t("v4", 4, "war")


@gag("v4", 6)
def cannot_tell_a_lie(c, L):
    """A cherry tree pops up on Alfred's deck, stamped MYTH (with its source: Parson Weems's biography,
    1806). 'Fine' is a shrug, 'I cannot tell a lie' a raised palm, and on 'true' he produces a hatchet."""
    t_cherry, t_myth, t_fine, t_cannot, t_true = (wt(L, "cherry"), wt(L, "myth"), wt(L, "Fine"),
                                                  wt(L, "cannot"), wt(L, "true"))
    at_sea(c, "alfred" if c.t < t_cannot - 0.1 else "wx")
    w = c.st["washington"]
    if t_fine <= c.t < t_cannot - 0.2:
        w.update(arm="shrug", mouth="smirk" if c.t > t_fine + 0.3 else w["mouth"], brows="up")
    elif t_cannot - 0.2 <= c.t < t_true:
        w.update(arm="palm")
    elif c.t >= t_true:
        w.update(arm="hold", brows="angry")
    yield "back"
    tree_on_deck(c, t_cherry)
    yield "front"
    if c.t >= t_true:
        hx, hy = anchor(c, "washington", "hand")
        paste(c.world, hatchet(), hx + 2, hy - 4 + (pop_dy(c.t - t_true, 0.15, 4) or 0), "mm")
    yield "ui"
    if c.t >= t_myth and c.t < t_cannot - 0.1:
        tx, ty = on_ui(c, *TREE)
        stamp(c.ui, tx, ty - 34, "MYTH", C["red"], angle=-12, size=16, age=c.t - t_myth)
        if c.t >= t_myth + 0.3:
            plate(c.ui, 70, 30 + (pop_dy(c.t - t_myth - 0.3, 0.2, 4) or 0),
                  ["FIRST TOLD BY", "PARSON WEEMS, 1806"], fg=C["text"])


TREE = (98, 116)                              # the cherry tree's foot on Alfred's deck


def tree_on_deck(c, t_in):
    if c.t < t_in:
        return
    s = ships.state(c)
    dy = pop_dy(c.t - t_in, 0.2, 10) or 0
    paste(c.world, cherry_tree(False), TREE[0] + s["alfred_x"], TREE[1] + ships.bob("al", c.t) + dy, "mb")


# The main topmast with the Hanover tree painted on its topsail: everything Royal George loses at 197.14.
TOPMAST_BOX, TOPMAST_PIVOT = (206, 0, 272, 62), (239, 60)
FORE_BOX, FORE_PIVOT = (140, 0, 232, 98), (201, 100)
MIZZEN_BOX, MIZZEN_PIVOT = (248, 0, 316, 98), (279, 100)


@lru_cache(maxsize=None)
def rig_piece(a, b, box):
    """The part of Royal George's rig drawn at damage a but gone (or changed) at damage b, inside box."""
    la, lb = np.array(ships.royal_george(a)[0]), np.array(ships.royal_george(b)[0])
    gone = (la[..., 3] > 0) & ((lb[..., 3] == 0) | (la[..., :3] != lb[..., :3]).any(-1))
    keep = np.zeros(gone.shape, bool)
    x0, y0, x1, y1 = box
    keep[y0:y1, x0:x1] = True
    out = la.copy()
    out[~(gone & keep)] = 0
    return Image.fromarray(out)


def topple(img, piece, pivot, t, t0, dur, angle, drop, dy=0):
    """Rotate a rig piece about its foot and drop it into the sea (cut off at the waterline)."""
    p = ramp(t, t0, t0 + dur)
    if not 0 < p < 1:
        return
    q = ease_in(p)
    im = piece.rotate(angle * q, resample=Image.NEAREST, center=pivot, translate=(0, drop * q + dy))
    im = im.crop((0, 0, W, ships.WL + 2))
    img.paste(im, (0, 0), im)


def topmast_fall(c):
    """The main topmast comes down on 'two' and splashes into the gap."""
    t0 = ships.MAST_CHOP
    rd = ships.bob("rg", c.t)
    topple(c.world, rig_piece(1, 2, TOPMAST_BOX), TOPMAST_PIVOT, c.t, t0, 0.65, 100, 95, rd)
    for i, (x, dt) in enumerate(((198, 0.42), (222, 0.5), (182, 0.58))):
        splash(c.world, x, ships.WL + 3, c.t - t0 - dt, 1.6, seed=i)


@lru_cache(maxsize=None)
def hanover_doc():
    im = Image.new("RGBA", (92, 64), (0, 0, 0, 0))
    parchment(im, (3, 3, 88, 60), rolled=True)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.text((46, 3), "HOUSE OF HANOVER", font=SILK, fill=C["red_sh"], anchor="ma")
    names = ["GEORGE I", "GEORGE II", "FREDERICK", "GEORGE III"]
    for i, n in enumerate(names):
        y = 14 + i * 11
        d.text((46, y - 2), n, font=SILK, fill=INKB, anchor="ma")
        if i < 3:
            d.line((46, y + 5, 46, y + 8), fill=C["gold_sh"])
    return im


@lru_cache(maxsize=None)
def hanover_halves():
    """The family tree torn down the middle: (left, right)."""
    im = np.array(hanover_doc())
    h, w = im.shape[:2]
    left = np.zeros_like(im)
    right = np.zeros_like(im)
    for y in range(h):
        cut = 46 + (2 if (y // 3) % 2 else -2) + (1 if y % 3 == 1 else 0)
        left[y, :cut] = im[y, :cut]
        right[y, cut:] = im[y, cut:]
    return Image.fromarray(left), Image.fromarray(right)


@gag("v4", 7)
def family_tree(c, L):
    """'I never chopped a cherry tree' with a nod back at the tree on deck; then 'I chopped your' - he
    throws the hatchet across the gap, it bites into the main mast on 'tree', and on 'two' the topmast
    carrying the Hanover tree comes down into the sea while the family tree on screen tears in half."""
    t_cherry, t_chop, t_family, t_tree = wt(L, "cherry"), wt(L, "chopped", 1), wt(L, "family"), wt(L, "tree", 1)
    at_sea(c, "alfred" if c.t < t_chop - 0.2 else "duel")
    w = c.st["washington"]
    if c.t < t_chop - 0.3:
        w.update(arm="hold")
        if t_cherry - 0.4 <= c.t < t_chop - 0.3:
            w.update(facing=-1, brows="up")
    elif c.t < t_chop + 0.25:
        w.update(arm="chop", brows="angry")
    else:
        w.update(arm="point")
    if c.t >= t_tree:
        face(c, "george", eyes="wide", brows="worried", mouth="o")
    yield "back"
    tree_on_deck(c, 0)
    a = anchor(c, "washington", "hand")
    target = (TOPMAST_PIVOT[0] - 2, TOPMAST_PIVOT[1] - 1 + ships.bob("rg", c.t))
    p = ramp(c.t, t_chop + 0.05, t_tree)
    if 0 < p < 1:
        x = lerp(a[0], target[0], p)
        y = lerp(a[1], target[1], p) - 26 * 4 * p * (1 - p)
        paste_rot(c.world, hatchet(), x, y, -p * 1080)
    elif p >= 1:
        hatchet_stuck(c, t_tree)
        if c.t - t_tree < 0.12:
            burst(c.world, target[0], target[1], 3, 7, C["gold_hi"], 8)
    topmast_fall(c)
    yield "front"
    if c.t < t_chop - 0.3:
        hx, hy = anchor(c, "washington", "hand")
        paste(c.world, hatchet(), hx + 2 * w["facing"], hy - 4, "mm")
    yield "ui"
    tree_card(c, t_family)


def hatchet_stuck(c, t_hit=0.0):
    """Washington's hatchet, left buried in Royal George's main mast (or what is left of it)."""
    top = TOPMAST_PIVOT[1] - 1 if ships.state(c)["rg"] < 3 else 63
    y = top + ships.bob("rg", c.t) + wobble_y(c.t - t_hit)
    paste_rot(c.world, hatchet(), TOPMAST_PIVOT[0] - 6, y, 30)


def wobble_y(age):
    return int(round(math.sin(age * 40) * 2 * max(0.0, 1 - age / 0.3))) if age >= 0 else 0


def tree_card(c, t_in, t_out=None):
    if c.t < t_in:
        return
    t_two = ships.MAST_CHOP
    x, y = 62, 6 + (pop_dy(c.t - t_in, 0.2, 8) or 0)
    if c.t < t_two:
        paste(c.ui, hanover_doc(), x, y, "mt")
        return
    age = c.t - t_two
    if age > 1.4:
        return
    left, right = hanover_halves()
    sep = int(ease_out(min(1.0, age / 0.3)) * 10)
    fall = int(max(0.0, age - 0.5) ** 2 * 160)
    paste_rot(c.ui, left, x - sep, y + 32 + fall, age * 20 if age > 0.5 else 0, "mm")
    paste_rot(c.ui, right, x + sep, y + 32 + fall, -age * 20 if age > 0.5 else 0, "mm")


@lru_cache(maxsize=None)
def clock_face():
    s = Canvas(27, 27)
    s.ell((1, 1, 25, 25), "paper")
    s.d.ellipse((1, 1, 25, 25), outline=Canvas.c("gold_sh"))
    for k in range(12):
        a = k * math.pi / 6
        s.px((13 + round(math.cos(a) * 10), 13 + round(math.sin(a) * 10)), "ink")
    return s.done()


def foam_surge(c, t0):
    """Surf boiling up white around Royal George's hull, with spray thrown off the top."""
    age = c.t - t0
    if not 0 <= age < 1.4:
        return
    h = 10 * math.sin(math.pi * min(1.0, age / 1.4))
    d = ImageDraw.Draw(c.world)
    rd = ships.bob("rg", c.t)
    f = int(c.t * 12)
    for x in range(166, 318):
        top = int(ships.WL + 2 - h * (0.6 + 0.4 * math.sin(x * 0.37 + c.t * 7)) + rd)
        d.line((x, top, x, ships.WL + 4), fill=ships.P["foam"])
        d.point((x, top), fill=C["white"])
        if rnd("fs", x, f) < 0.25 * h / 10:
            d.point((x, top - 2 - int(rnd("fh", x, f) * 6)), fill=C["white"])


@gag("v4", 8)
def mind_went(c, L):
    """Quiet, and about the history. The topmast finishes going under; on 'mind went' a caption dates the
    King's first great illness (1788); a clock spins through 'talked for hours'; and on 'foamed' surf
    boils up around his ship."""
    t_mind, t_talked, t_foamed = wt(L, "mind"), wt(L, "talked"), wt(L, "foamed")
    at_sea(c, "duel" if c.t < t_mind + 0.1 or c.t >= t_foamed - 0.15 else "royal")
    c.hit_react["george"] = False
    c.hitfx = False
    g = c.st["george"]
    g.update(arm="down", mouth="closed", brows="worried", eyes="open" if c.t < t_talked else "side")
    yield "back"
    hatchet_stuck(c)
    topmast_fall(c)
    yield "front"
    foam_surge(c, t_foamed - 0.1)
    yield "ui"
    tree_card(c, 0)
    if t_mind + 0.1 <= c.t < t_foamed - 0.15:
        age = c.t - t_mind - 0.1
        plate(c.ui, 70, 24 + (pop_dy(age, 0.2, 6) or 0), ["1788", "THE KING FALLS ILL"], first=C["gold"],
              fnt=SILK)
    if t_talked - 0.1 <= c.t < t_foamed - 0.15:
        age = c.t - t_talked + 0.1
        cx, cy = 70, 62 + (pop_dy(age, 0.2, 6) or 0)
        paste(c.ui, clock_face(), cx, cy, "mm")
        d = ImageDraw.Draw(c.ui)
        spin = min(c.t, t_foamed) - t_talked
        am, ah = spin * 14 - math.pi / 2, spin * 14 / 12 - math.pi / 2 + 1.0
        d.line((cx, cy, cx + round(math.cos(am) * 9), cy + round(math.sin(am) * 9)), fill=INK)
        d.line((cx, cy, cx + round(math.cos(ah) * 6), cy + round(math.sin(ah) * 6)), fill=C["red_sh"])


@lru_cache(maxsize=None)
def chair(strapped=False, throne=False):
    """A plain high-backed wooden armchair, front on; straps and a cushion as the line goes on."""
    s = Canvas(32, 46)
    s.rect((5, 2, 7, 34), "wood"); s.rect((24, 2, 26, 34), "wood")
    s.rect((4, 1, 27, 4), "wood_hi")
    for x in (11, 15, 19):
        s.rect((x, 5, x + 1, 26), "wood_sh")
    s.rect((3, 27, 28, 31), "wood")
    s.line([(3, 27), (28, 27)], "wood_hi")
    s.rect((1, 18, 7, 20), "wood_hi"); s.rect((24, 18, 30, 20), "wood_hi")
    s.rect((1, 21, 2, 27), "wood"); s.rect((29, 21, 30, 27), "wood")
    for x in (4, 26):
        s.rect((x, 31, x + 1, 44), "wood_sh")
    s.line([(4, 39), (27, 39)], "wood_sh")
    if throne:
        s.rect((7, 24, 24, 27), "red"); s.line([(7, 24), (24, 24)], "red_hi")
        s.rect((4, 1, 27, 2), "gold")
    if strapped:
        for y, x0, x1 in ((12, 6, 26), (19, 1, 7), (19, 24, 30), (36, 3, 7), (36, 24, 28)):
            s.rect((x0, y, x1, y + 1), (70, 44, 36))
            s.px(((x0 + x1) // 2, y), "gold")
    return s.done()


@gag("v4", 9)
def willis(c, L):
    """About the history, not the illness: a museum-style plate of a period restraining chair, the kind
    Dr Francis Willis used on the King in 1788-89. The straps go on at 'strapped'; on 'enthroned' it gets a
    red cushion and a crown drops onto its back. George stays still on his deck."""
    t_doc, t_strap, t_maj, t_enth = wt(L, "Doctor"), wt(L, "strapped"), wt(L, "Majesty"), wt(L, "enthroned")
    at_sea(c, "duel" if c.t < t_doc - 0.05 else "royal")
    c.hit_react["george"] = False
    c.hitfx = False
    g = c.st["george"]
    g.update(arm="down", mouth="closed", brows="worried", eyes="side" if c.t < t_maj else "shut")
    yield "back"
    hatchet_stuck(c)
    yield "front"
    foam_surge(c, line_foamed())
    yield "ui"
    if c.t < t_doc - 0.1:
        return
    age = c.t - t_doc + 0.1
    dy = pop_dy(age, 0.2, 8) or 0
    x0, y0 = 4, 10 + dy
    cx = x0 + 50
    parchment(c.ui, (x0, y0, x0 + 100, y0 + 126), rolled=True)
    spr = chair(c.t >= t_strap, c.t >= t_enth)
    paste(c.ui, scaled(spr, 2), cx, y0 + 6, "mt")
    d = ImageDraw.Draw(c.ui)
    d.fontmode = "1"
    for i, s in enumerate(("DR. FRANCIS WILLIS", "TREATED THE KING", "1788-89")):
        d.text((cx, y0 + 99 + i * 8), s, font=SILK, fill=INKB if i < 2 else C["red_sh"], anchor="ma")
    if c.t >= t_enth - 0.25:
        p = ease_in(ramp(c.t, t_enth - 0.25, t_enth + 0.05))
        cr = scaled(crown_sprite(), 2)
        paste(c.ui, cr, cx, lerp(y0 - 30, y0 + 8, p), "mb")
        if 0 <= c.t - t_enth - 0.05 < 0.4:
            sparkle(c.ui, cx + 16, y0 + 2, 3, C["gold_hi"])


def line_foamed():
    return line_t("v4", 8, "foamed") - 0.1


@lru_cache(maxsize=None)
def chamber_pot():
    s = Canvas(10, 8)
    s.poly([(1, 1), (8, 1), (7, 6), (2, 6)], "white")
    s.line([(1, 3), (8, 3)], "sash")
    s.d.arc((6, 1, 10, 5), 270, 90, fill=Canvas.c("white"))
    return s.done()


STERN = (300, 118)                            # Royal George's quarter gallery, where the officers' heads were


@gag("v4", 10, post=0.0)
def blue_blood(c, L):
    """A chamber pot tips out of Royal George's quarter gallery and pours blue into the sea. 'Blue blood'
    goes up as a heading; 'Nah' strikes BLOOD out, and 'bladder' stamps BLADDER. Then the break: Alfred's
    full broadside, four volleys, and Royal George is dismasted - fore and mizzen masts topple into the
    sea, fires break out, and George is left with his crown knocked askew."""
    t_piss, t_blue, t_bb, t_nah, t_blad = (wt(L, "piss"), wt(L, "blue"), wt(L, "blue", 1), wt(L, "Nah"),
                                           wt(L, "bladder"))
    t_fire = 207.92
    t_mast = 209.2
    if c.t < t_bb - 0.15:
        at_sea(c, "stern")
    elif c.t < t_blad + 0.25:
        at_sea(c, "royal")
    elif c.t < t_mast - 0.45:
        at_sea(c, "duel")
    else:
        at_sea(c, "rgwide")
        if c.t >= 210.2:
            glide(c, "rgwide", "sky", 210.2, 0.8)
    w, g = c.st["washington"], c.st["george"]
    if t_fire - 0.3 <= c.t < t_mast:
        w.update(arm="point" if c.t < t_fire else "fist", mic=False, mouth="wide" if c.t < t_fire + 0.3
                 else "grit", brows="angry")
    if c.t >= t_mast:
        g.update(hat="askew")
        face(c, "george", eyes="wide" if c.t < t_mast + 0.8 else "open", brows="worried",
             mouth="o" if c.t < t_mast + 0.8 else "frown")
        g["sweat"] = True
        c.add_shake(8 * max(0.0, 1 - (c.t - t_mast) / 0.4))
        c.add_flash(0.85 if c.t - t_mast < 0.09 else 0.0, C["gold_hi"])
    yield "back"
    hatchet_stuck(c)
    rd = ships.bob("rg", c.t)
    topple(c.world, rig_piece(2, 3, FORE_BOX), FORE_PIVOT, c.t, t_mast, 0.75, 85, 70, rd)
    topple(c.world, rig_piece(2, 3, MIZZEN_BOX), MIZZEN_PIVOT, c.t, t_mast + 0.05, 0.8, -80, 60, rd)
    for i, (x, dt) in enumerate(((150, 0.62), (170, 0.7), (306, 0.72))):
        splash(c.world, x, ships.WL + 3, c.t - t_mast - dt, 2.0, seed=10 + i)
    pour(c, t_piss, t_blue)
    yield "ui"
    if t_bb - 0.05 <= c.t < t_fire:
        age = c.t - t_bb + 0.05
        y = 12 + (pop_dy(age, 0.2, 10) or 0)
        wb = text_width("BLUE ", PRESS16)
        wt_ = text_width("BLUE BLOOD", PRESS16)
        x0 = 160 - wt_ // 2
        big_text(c.ui, (x0, y), "BLUE BLOOD", PRESS16, top=C["sash"], bottom=C["sash_sh"])
        if c.t >= t_nah:
            strike(c.ui, x0 + wb - 2, y + 8, x0 + wt_ + 2, ramp(c.t, t_nah, t_nah + 0.2), C["red"], 3)
        if c.t >= t_blad:
            stamp(c.ui, 240, 74, "BLADDER", C["gold"], angle=-8, size=16, age=c.t - t_blad)


def pour(c, t_pot, t_pour):
    """The pot at the quarter gallery window, tipping; a blue stream; a blue patch spreading on the sea."""
    if c.t < t_pot or c.t > t_pot + 3.2:
        return
    rd = ships.bob("rg", c.t)
    x, y = STERN[0], STERN[1] + rd
    tip = ease_out(ramp(c.t, t_pot, t_pour))
    paste_rot(c.world, chamber_pot(), x - 3, y, -110 * tip)
    d = ImageDraw.Draw(c.world)
    blue = C["sash"]
    if c.t >= t_pour:
        age = c.t - t_pour
        if age < 1.6:
            for k in range(int(ships.WL - y)):
                yy = y + 2 + k
                xx = x - 6 - k * 0.15 + math.sin(yy * 0.7 + c.t * 20) * 0.6
                d.point((xx, yy), fill=blue if k % 3 else C["sash_sh"])
        r = min(14.0, 3 + age * 9)
        m = pixel.mask(lambda dd: dd.ellipse((x - 8 - r, ships.WL + 1, x - 8 + r, ships.WL + 1 + r * 0.35),
                                             fill=255), (W, 180))
        pixel.dither(c.world, m * 0.6, blue, blend=0.8, phase=1)


@lru_cache(maxsize=None)
def telescope():
    s = Canvas(24, 20)
    s.line([(3, 15), (19, 4)], "wood", 3)
    s.line([(4, 14), (19, 4)], "wood_hi")
    s.rect((18, 2, 21, 5), "gold")
    s.line([(10, 11), (5, 19)], "wood_sh"); s.line([(10, 11), (15, 19)], "wood_sh")
    return s.done()


PLANET = (196, 22)


def sky_state(c, stars=0.35):
    c.ship = dict(c.ship or {}, stars=stars)


@gag("v4", 11)
def georgium_sidus(c, L):
    """Up into the dusk sky: a small blue-green planet. 'Herschel' names the discoverer (1781); on 'named'
    his name for it goes up - GEORGIUM SIDUS - and on 'George's Star' the translation."""
    t_hers, t_planet, t_named, t_gs = wt(L, "Herschel"), wt(L, "planet"), wt(L, "named"), wt(L, "George")
    at_sea(c, "sky")
    sky_state(c)
    if c.t < 211.0:
        glide(c, "rgwide", "sky", 210.2, 0.8)
    yield "back"
    planet_draw(c, t_planet - 0.2)
    yield "ui"
    if c.t >= t_hers:
        age = c.t - t_hers
        dy = pop_dy(age, 0.2, 6) or 0
        paste(c.ui, telescope(), 22, 112 + dy, "mb")
        plate(c.ui, 88, 104 + dy, ["WILLIAM HERSCHEL", "FINDS A PLANET, 1781"], first=C["gold"])
    planet_labels(c, t_named, t_gs, None)


def planet_draw(c, t_in):
    if c.t < t_in:
        return
    p = ease_out(ramp(c.t, t_in, t_in + 0.4))
    x, y = PLANET
    spr = planet(ring=False)
    paste_scaled(c.world, spr, x, y, max(0.1, p))
    if p < 1 or int(c.t * 3) % 4 == 0:
        sparkle(c.world, x + 7, y - 5, 2, C["white"])


def paste_scaled(img, spr, x, y, s):
    paste(img, scaled(spr, s) if s != 1 else spr, x, y, "mm")


def planet_labels(c, t_named, t_gs, t_renamed):
    if c.t < t_named:
        return
    ux, uy = on_ui(c, PLANET[0], PLANET[1] + 10)
    if uy < 12:                                                # panned away
        return
    if t_renamed is None or c.t < t_renamed:
        age = c.t - t_named
        box = label(c.ui, (ux, uy + 2 + (pop_dy(age, 0.2, 4) or 0)), "GEORGIUM SIDUS", bg=C["paper"],
                    fnt=PRESS, anchor="mt")
        if c.t >= t_gs:
            label(c.ui, (ux, box[3] + 4), "\"GEORGE'S STAR\"", bg=C["band"], fg=C["gold"], anchor="mt")
        if t_renamed is not None and c.t >= t_renamed - 0.35:
            strike(c.ui, box[0] - 2, (box[1] + box[3]) // 2, box[2] + 2, ramp(c.t, t_renamed - 0.35, t_renamed - 0.1),
                   C["red"], 2)
    else:
        age = c.t - t_renamed
        pop_text(c.ui, ux, uy + 2, "URANUS", age, PRESS16, top=C["white"], bottom=(150, 220, 226))


@lru_cache(maxsize=None)
def pin():
    s = Canvas(11, 15)
    s.ell((1, 1, 9, 9), "red")
    s.poly([(2, 7), (8, 7), (5, 13)], "red")
    s.ell((3, 3, 6, 6), "white")
    s.px((3, 2), "red_hi")
    return s.done()


@gag("v4", 12)
def uranus(c, L):
    """'The world renamed it Uranus': the label is struck through and flips to URANUS. 'That's exactly
    where you are': the camera drops from the planet to George, and a map pin lands on him: YOU ARE HERE."""
    t_ren, t_that, t_where = wt(L, "renamed"), wt(L, "That"), wt(L, "where")
    at_sea(c, "sky")
    sky_state(c)
    if c.t >= t_that - 0.1:
        glide(c, "sky", "royal", t_that - 0.1, 0.6)
    yield "back"
    planet_draw(c, 0)
    yield "ui"
    planet_labels(c, 0, 0, t_ren + 0.3)
    if c.t >= t_where:
        hx, hy = anchor(c, "george", "top")
        ux, uy = on_ui(c, hx, hy)
        age = c.t - t_where
        drop = int((1 - ease_in(min(1.0, age / 0.2))) * -60)
        paste(c.ui, scaled(pin(), 2), ux - 2, uy - 4 + drop, "mb")
        if age > 0.2:
            label(c.ui, (ux + 12, uy - 18), "YOU ARE HERE", bg=C["red"], fg=C["white"], fnt=PRESS, anchor="lm")


@gag("v4", 13)
def abdication(c, L):
    """'In '82 you drafted your abdication': a parchment headed ABDICATION, DRAFT, 1782, fills with lines
    and crossings-out. 'Tried to give the crown away': George lifts his crown off and holds it out west."""
    t_82, t_draft, t_give, t_crown = wt(L, "82"), wt(L, "drafted"), wt(L, "give"), wt(L, "crown")
    at_sea(c, "royal")
    g = c.st["george"]
    if c.t >= t_give:
        g.update(hat="off", arm="hold", brows="worried", mouth="frown")
    yield "front"
    if c.t >= t_give:
        hx, hy = anchor(c, "george", "hand")
        lift = ease_out(ramp(c.t, t_give, t_crown))
        paste(c.world, crown_sprite(), hx - 3 - int(4 * lift), hy - 2 - int(3 * lift), "mb")
    yield "ui"
    if t_82 - 0.1 <= c.t < t_give + 0.3:
        age = c.t - t_82 + 0.1
        x0, y0 = 12, 20 + (pop_dy(age, 0.2, 8) or 0) - int(ease_in(ramp(c.t, t_give - 0.1, t_give + 0.3)) * 120)
        parchment(c.ui, (x0, y0, x0 + 98, y0 + 86), rolled=True)
        d = ImageDraw.Draw(c.ui)
        d.fontmode = "1"
        d.text((x0 + 49, y0 + 3), "ABDICATION", font=PRESS, fill=INKB, anchor="ma")
        d.text((x0 + 49, y0 + 13), "DRAFT, 1782", font=SILK, fill=C["red_sh"], anchor="ma")
        n = int(ramp(c.t, t_draft, t_give) * 7)
        for i in range(n):
            y = y0 + 26 + i * 7
            for x in range(x0 + 6, x0 + 92 - (i * 13) % 20, 3):
                d.line([(x, y + 3 + (x % 2)), (x + 2, y + 3 - (x % 3 == 0))], fill=mix(C["paper"], INKB, 0.6))
            if i in (1, 4):
                d.line((x0 + 5, y + 3, x0 + 88 - (i * 13) % 20, y + 2), fill=INKB)


@gag("v4", 14)
def banish(c, L):
    """'Same spring, they offered one to me': a letter arrives at Alfred from Washington's own camp - Col.
    Lewis Nicola, May 1782, urging a king - with a crown drawn on it. On 'Banish these thoughts' his reply
    goes up in his own words, and on 'No way' he pushes it away and the letter goes into the sea."""
    t_off, t_me, t_ban, t_no = wt(L, "offered"), wt(L, "^me"), wt(L, "Banish"), wt(L, "^No")
    at_sea(c, "alfred")
    w = c.st["washington"]
    if t_me <= c.t < t_no:
        w.update(arm="hold", brows="neutral")
    elif c.t >= t_no:
        w.update(arm="palm", brows="angry", mouth=w["mouth"] if c.t < t_no + 0.4 else "grit")
    yield "front"
    hx, hy = anchor(c, "washington", "hand")
    spr = letter_crown()
    if t_off <= c.t < t_me:
        p = ease_out(ramp(c.t, t_off, t_me))
        paste_rot(c.world, spr, lerp(24, hx + 4, p), lerp(60, hy - 2, p) + math.sin(p * 9) * 3, (1 - p) * 40)
    elif t_me <= c.t < t_no:
        paste(c.world, spr, hx + 4, hy - 2, "mm")
    elif c.t >= t_no:
        p = ramp(c.t, t_no, t_no + 0.55)
        if p < 1:
            x = hx + 4 + p * 26
            y = hy - 2 - 10 * math.sin(p * math.pi) + p * p * 40
            paste_rot(c.world, spr, x, y, -p * 200)
        splash(c.world, int(hx + 30), ships.WL + 4, c.t - t_no - 0.55, 1.0, seed=5)
    yield "ui"
    if c.t >= t_off:
        age = c.t - t_off
        plate(c.ui, 74, 20 + (pop_dy(age, 0.2, 6) or 0), ["MAY 1782: COL. LEWIS NICOLA", "URGES A KING"],
              first=C["gold"])
    if c.t >= t_ban - 0.05:
        age = c.t - t_ban + 0.05
        doc(c.ui, 74, 50 + (pop_dy(age, 0.2, 8) or 0), ["\"...BANISH THESE THOUGHTS", "FROM YOUR MIND.\""],
            sign="G. WASHINGTON, MAY 1782", fnt=SILK)
        if c.t >= t_no:
            stamp(c.ui, 74, 100, "NO WAY.", C["red"], angle=-10, size=16, age=c.t - t_no)


@lru_cache(maxsize=None)
def letter_crown():
    e = envelope(24, 16, seal=True).copy()
    cr = crown_sprite()
    cr = cr.resize((max(1, cr.width // 2), max(1, cr.height // 2)), Image.NEAREST)
    e.paste(cr, (4, 3), cr)
    return e


@lru_cache(maxsize=None)
def easel():
    s = Canvas(28, 38)
    s.line([(14, 2), (4, 37)], "wood_sh"); s.line([(14, 2), (24, 37)], "wood_sh"); s.line([(14, 6), (15, 37)], "wood")
    s.rect((2, 4, 25, 22), "paper")
    s.line([(2, 22), (25, 22)], "wood")
    s.line([(1, 23), (26, 23)], "wood_hi")
    return s.done()


@lru_cache(maxsize=None)
def mount_vernon():
    """A little painting of Mount Vernon: the long white house, red roof and cupola, lawn."""
    s = Canvas(22, 17)
    s.rect((0, 0, 21, 16), (150, 190, 230))
    s.rect((0, 12, 21, 16), (90, 150, 80))
    s.rect((4, 7, 17, 12), "white")
    s.poly([(3, 7), (18, 7), (16, 4), (5, 4)], "red")
    s.rect((10, 1, 11, 4), "white"); s.px((10, 0), "red")
    for x in (6, 9, 12, 15):
        s.px((x, 9), "wood_deep")
    return s.done(None)


EASEL = (218, 106)


@gag("v4", 15)
def painter(c, L):
    """'Then the war was won': TREATY OF PARIS, 1783. 'You asked your painter': an easel stands on Royal
    George's deck, labelled BENJAMIN WEST, the King's history painter, and George asks: WHAT WILL HE DO?"""
    t_war, t_asked, t_painter, t_what = wt(L, "war"), wt(L, "asked"), wt(L, "painter"), wt(L, "what")
    at_sea(c, "duel" if c.t < t_asked - 0.3 else "royal")
    g = c.st["george"]
    if c.t >= t_what - 0.2:
        g.update(arm="shrug", brows="up", mouth="o")
    yield "back"
    easel_draw(c, t_painter - 0.3)
    yield "ui"
    if t_war <= c.t < t_asked - 0.3:
        age = c.t - t_war
        plate(c.ui, 160, 30 + (pop_dy(age, 0.2, 8) or 0), ["TREATY OF PARIS, 1783", "THE WAR IS OVER"],
              first=C["gold"], fnt=PRESS)
    if c.t >= t_painter:
        ex, ey = on_ui(c, EASEL[0], EASEL[1] - 38)
        plate(c.ui, 230, 14 + (pop_dy(c.t - t_painter, 0.2, 6) or 0),
              ["BENJAMIN WEST", "HISTORY PAINTER TO THE KING"], first=C["gold"])
    if c.t >= t_what - 0.1:
        mx, my = anchor(c, "george", "mouth")
        ux, uy = on_ui(c, mx - 2, my)
        bubble(c.ui, ux - 44, uy - 24 + (pop_dy(c.t - t_what + 0.1, 0.15, 4) or 0), ["WHAT WILL", "HE DO?"],
               tail=(ux - 4, uy - 4))


def easel_draw(c, t_in, painted_at=None):
    if c.t < t_in:
        return
    rd = ships.bob("rg", c.t)
    dy = pop_dy(c.t - t_in, 0.2, 8) or 0
    x, y = EASEL[0], EASEL[1] + rd + dy
    paste(c.world, easel(), x, y, "mb")
    if painted_at is not None and c.t >= painted_at:
        p = ramp(c.t, painted_at, painted_at + 0.5)
        mv = mount_vernon()
        wv = max(1, int(mv.width * p))
        paste(c.world, mv.crop((0, 0, wv, mv.height)), x - 12, y - 34, "lt")


@gag("v4", 16)
def farm(c, L):
    """West's answer, in a bubble from beside the easel: HE'LL GO BACK TO HIS FARM. On 'farm' the canvas
    paints itself - Mount Vernon. On '(yes, you)' the shot widens and Washington points straight at George."""
    t_west, t_farm, t_and, t_yes = wt(L, "West"), wt(L, "farm"), wt(L, "And"), wt(L, "yes")
    at_sea(c, "royal" if c.t < t_and - 0.1 else "two")
    w, g = c.st["washington"], c.st["george"]
    if c.t >= t_and:
        w.update(arm="point", brows="up")
        face(c, "george", eyes="wide" if c.t >= t_yes else "open", brows="up", mouth="o" if c.t >= t_yes else "closed")
    else:
        g.update(eyes="side", brows="up", mouth="closed")
    yield "back"
    easel_draw(c, 0, t_farm - 0.2)
    yield "ui"
    if t_west + 0.1 <= c.t < t_and - 0.1:
        ex, ey = on_ui(c, EASEL[0] + 6, EASEL[1] - 38)
        bubble(c.ui, ex - 2, ey - 6, ["HE'LL GO BACK", "TO HIS FARM."], tail=(ex + 4, ey + 4), fill=C["paper"],
               anchor="lb")
    if c.t >= t_farm and c.t < t_and - 0.1:
        ex, ey = on_ui(c, EASEL[0], EASEL[1])
        label(c.ui, (ex, ey + 2), "MOUNT VERNON", bg=C["band"], fg=C["gold"], anchor="mt")
    if c.t >= t_yes - 0.05:
        a = on_ui(c, *anchor(c, "washington", "hand"))
        b = on_ui(c, *anchor(c, "george", "head"))
        p = ease_out(ramp(c.t, t_yes - 0.05, t_yes + 0.2))
        arrow(c.ui, a[0] + 6, a[1] - 8, lerp(a[0] + 6, b[0] - 14, p), lerp(a[1] - 8, b[1] - 6, p), C["gold"], 2, 6)
        if p >= 1:
            label(c.ui, ((a[0] + b[0]) // 2, min(a[1], b[1]) - 28), "YES, YOU", bg=C["gold"], fnt=PRESS, anchor="mb")


@lru_cache(maxsize=None)
def laurel():
    s = Canvas(30, 14)
    for side in (-1, 1):
        for k in range(6):
            a = math.pi * (0.1 + k * 0.14)
            x = 15 + side * math.cos(a) * 12
            y = 11 - math.sin(a) * 9
            s.ell((x - 2, y - 1, x + 1, y + 1), (80, 150, 70))
            s.px((round(x), round(y) - 1), (140, 200, 110))
    return s.done()


QUOTE = ["\"IF HE DOES THAT, HE WILL BE", "THE GREATEST MAN IN THE WORLD.\""]


@gag("v4", 17)
def greatest_man(c, L):
    """George's own words, typed out in a speech bubble as they're quoted back at him. On 'greatest man'
    the shot finds Washington with a laurel wreath settling over his hat; on 'world' (the kill) back to
    George, reeling."""
    t_if, t_great, t_world = wt(L, "If"), wt(L, "greatest"), wt(L, "world")
    hit = t_world + 0.04
    if c.t < t_great - 0.05:
        at_sea(c, "royal")
    elif c.t < hit:
        at_sea(c, "alfred")
    else:
        at_sea(c, "gx")
    w = c.st["washington"]
    if c.t >= t_great:
        w.update(arm="hip", brows="up", mouth="smirk" if w["mouth"] == "closed" else w["mouth"])
    yield "front"
    if c.t >= t_great:
        hx, hy = anchor(c, "washington", "top")
        p = ease_out(ramp(c.t, t_great, t_great + 0.5))
        paste(c.world, laurel(), hx - 1, lerp(hy - 30, hy - 2, p), "mb")
        if int(c.t * 8) % 2:
            sparkle(c.world, hx + 12, hy - 8, 2, C["gold_hi"])
    yield "ui"
    if t_if - 0.1 <= c.t < t_great - 0.05:
        mx, my = anchor(c, "george", "mouth")
        ux, uy = on_ui(c, mx, my)
        n = int((c.t - t_if + 0.1) * 26)
        full = " ".join(QUOTE)
        shown = full[:n]
        lines = [shown[:len(QUOTE[0])], shown[len(QUOTE[0]) + 1:]] if len(shown) > len(QUOTE[0]) else [shown]
        lines = [s for s in lines if s] or [" "]
        bubble(c.ui, 100, 6, lines, tail=(ux - 4, uy - 6), fill=C["paper"], fnt=SILK, anchor="mt")


@lru_cache(maxsize=None)
def sword():
    s = Canvas(30, 9)
    s.rect((9, 3, 27, 4), "steel"); s.line([(9, 3), (27, 3)], "white")
    s.px((28, 4), "steel")
    s.rect((7, 1, 8, 7), "gold")
    s.rect((2, 3, 6, 4), "wood_deep")
    s.px((1, 3), "gold"); s.px((1, 4), "gold")
    return s.done()


@gag("v4", 18)
def sword_back(c, L):
    """'So I handed back my sword': Washington holds his sword out hilt first and lowers it on 'sword'.
    The caption: he resigned his commission, Annapolis, December 23, 1783."""
    t_hand, t_sword = wt(L, "handed"), wt(L, "sword")
    at_sea(c, "alfred")
    w = c.st["washington"]
    w.update(arm="hold", brows="neutral")
    yield "front"
    hx, hy = anchor(c, "washington", "hand")
    lower = ease_in_out(ramp(c.t, t_sword - 0.1, t_sword + 0.4))
    paste_rot(c.world, mirror(sword()), hx + 8, hy - 1 + lower * 8, -80 * lower)
    yield "ui"
    if c.t >= t_hand - 0.1:
        age = c.t - t_hand + 0.1
        plate(c.ui, 70, 20 + (pop_dy(age, 0.2, 8) or 0), ["DECEMBER 23, 1783", "RESIGNS HIS COMMISSION",
                                                          "ANNAPOLIS, MARYLAND"], first=C["gold"], fnt=SILK)


@gag("v4", 19)
def presidency(c, L):
    """'Then I handed back the presidency': he takes his hat off and bows his head a little. Caption: 1797,
    steps down after two terms."""
    t_hand, t_pres = wt(L, "handed"), wt(L, "presidency")
    at_sea(c, "wx")
    w = c.st["washington"]
    if c.t >= t_pres - 0.2:
        w.update(hat="off", arm="down", brows="neutral")
    yield "ui"
    if c.t >= t_hand - 0.1:
        age = c.t - t_hand + 0.1
        plate(c.ui, 52, 30 + (pop_dy(age, 0.2, 8) or 0), ["1797", "STEPS DOWN", "AFTER TWO TERMS", "AS PRESIDENT"],
              first=C["gold"])


@gag("v4", 20)
def your_words(c, L):
    """'Your words, George': the quote on a card, attributed as it has come down to us - George III,
    as told by Benjamin West. 'Not mine': Washington points across at him."""
    t_words, t_not = wt(L, "words"), wt(L, "Not")
    at_sea(c, "two")
    w, g = c.st["washington"], c.st["george"]
    w.update(hat="on", arm="point" if c.t >= t_not else "down")
    g.update(arm="down", brows="worried", mouth="closed", eyes="open" if c.t < t_not + 0.3 else "side")
    yield "ui"
    if c.t >= t_words - 0.2:
        age = c.t - t_words + 0.2
        doc(c.ui, 160, 8 + (pop_dy(age, 0.25, 10) or 0), QUOTE, sign="GEORGE III, AS TOLD BY BENJAMIN WEST",
            fnt=PRESS)


@gag("v4", 21)
def got_right(c, L):
    """The closer, quiet and hard: no shake, no flinch. Close on George as it's said; on 'right' his crown
    slides off his head, and a wider shot catches the small splash as it goes into the sea."""
    t_first, t_right = wt(L, "First"), wt(L, "right")
    t_slip = t_right + 0.04
    at_sea(c, "gx" if c.t < t_slip + 0.45 else "duel")
    c.hitfx = False
    c.hit_react["george"] = False
    c.karaoke = c.t < end_t(L) + 0.6
    g = c.st["george"]
    g.update(arm="down", mouth="closed", brows="worried", eyes="open")
    if c.t >= t_first:
        g.update(eyes="side")
    if c.t >= t_slip:
        g.update(hat="off", eyes="shut" if c.t < t_slip + 1.0 else "side", mouth="frown")
    yield "front"
    if c.t >= t_slip:
        crown_fall(c, t_slip)


def crown_fall(c, t0):
    """George's crown slides off the back of his head and drops past the hull into the sea."""
    hx, hy = ships.G_FEET[0], ships.G_FEET[1] - 47 + ships.bob("rg", c.t)
    age = c.t - t0
    t_hit = 0.7
    if age < t_hit:
        x = hx - 3 - age * 14
        y = hy + 170 * age * age + 6 * age
        y = min(y, ships.WL + 2)
        paste_rot(c.world, crown_sprite(), x, y, age * 70)
    else:
        splash(c.world, int(hx - 3 - t_hit * 14), ships.WL + 3, age - t_hit, 1.4, seed=21)
