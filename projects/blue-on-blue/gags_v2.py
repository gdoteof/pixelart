"""Verse 2: the guest responds. He and Donald are official; the host is the bitter ex in all caps, in his own
merch, a Temu Trump who can't get a call back; Trump sends Zohran songs and Gavin the feds; and he lives
rent-free in the host's head."""
import math

from gagkit import *  # noqa: F403

PHONE_ON_DESK = (191, 120)


@gag("v2", 0)
def twosome(c, L):
    a_don = age(L, "Donald")
    if a_don < 0:
        pose(c, "mamdani", arms="palm", brows="worried", mouth=c.st["mamdani"]["mouth"])
    else:
        hold(c, "mamdani", P.phone_held(), arms="hold")
    yield "ui"
    if a_don > -0.2:
        inset(c, INSET, P.relationship(a_don), "HIS PAGE", k_in(a_don + 0.2, 0.25))


@gag("v2", 1)
def handsome_newscum(c, L):
    a_h, a_n = age(L, "handsome"), age(L, "Newscum")
    if 0 < a_h and a_n < 0:
        pose(c, "mamdani", arms="chest", eyes="shut", mouth="grin", brows="up")
    if a_n > 0:
        pose(c, "newsom", eyes="wide", brows="worried", mouth="o" if a_n < 0.6 else "frown", react=False)
    yield "ui"
    if a_h > 0 and a_n < 0.4:
        hx, hy = c.anchor["mamdani"]["head"]
        x, y = c.to_ui(hx, hy - 4)
        shout(c, 238, 24, "HANDSOME", a_h, size=8)
        P.sparkles(c.ui, x, y + 18, a_h, n=4, r=18, color="gold_hi")
    if a_n > 0:
        ex, ey = c.anchor["newsom"]["eye"]
        stamp(c, ex + 6, ey - 10, "NEWSCUM", a_n, angle=8)


@gag("v2", 2)
def bitter_ex(c, L):
    a_bit, a_bawl, a_booze = age(L, "bitter"), age(L, "bawlin"), age(L, "boozin")
    if a_bawl > -0.1:
        pose(c, "newsom", tears=True, brows="worried", eyes="half", react=False,
             mouth="wide" if a_booze < 0 else "frown")
    if a_booze > -0.1:
        pose(c, "newsom", arms="drink", held=(P.wine_glass(), ("hand_near", 4)))
    yield "ui"
    if a_bit > -0.2:                                                   # his press office, posting like Donald
        inset(c, INSET, P.all_caps(max(0.0, a_bit)), "HIS PRESS OFFICE", k_in(a_bit + 0.2, 0.25))


@gag("v2", 3)
def merch(c, L):
    a_merch, a_cap = age(L, "merch"), age(L, "ball")
    if a_cap > 0:
        pose(c, "newsom", mouth="smile", eyes="open", brows="up", tears=False)
    yield "front"
    if a_cap > 0:
        on_head(c, c.world, "newsom", P.cap("GAVIN"), dy=-3 - int(max(0.0, 0.15 - a_cap) * 40))
    yield "ui"
    if a_merch > -0.2:
        inset(c, INSET, P.merch(a_merch), "HIS MERCH", k_in(a_merch + 0.2, 0.25))


@gag("v2", 4)
def temu_trump(c, L):
    a_temu, a_still, a_back = age(L, "Temu"), age(L, "still"), age(L, "back")
    wig = a_temu > 0
    if wig:
        pose(c, "newsom", mouth="pout" if a_still < 0 else "frown", eyes="squint" if a_still < 0 else "half")
    if a_still > -0.1:
        pose(c, "newsom", arms="ear", held=(P.phone_held(False), ("hand_near", 2)), brows="worried")
    yield "front"
    if wig:
        on_head(c, c.world, "newsom", P.trump_wig(), dy=-4 - int(max(0.0, 0.12 - a_temu) * 60))
        x0, y0, _, _ = head_box(c, "newsom")
        put(c.world, P.price_tag("TEMU $1.99"), x0 + 6, y0 + 12 + int(1.5 * math.sin(L.t * 9)), "rm")
    yield "ui"
    if a_still > 0:
        say(c, "newsom", "RING RING...", a_still, dur=a_still - a_back + 0.05)
    if a_back > 0:
        hx, hy = c.anchor["newsom"]["head"]
        stamp(c, hx + 30, hy + 6, "NO ANSWER", a_back, angle=-10)


@gag("v2", 5)
def picked_me(c, L):
    a_ex, a_me = age(L, "ex-wife"), age(L, "me")
    if a_me > 0:
        pose(c, "mamdani", arms="chest", eyes="shut", mouth="grin")
    yield "ui"
    if a_ex > -0.2:
        inset(c, INSET, P.two_photos(0.0 if a_me < -0.3 else 1.0), "WHO PICKED WHO", k_in(a_ex + 0.2, 0.25))


@lru_cache(maxsize=1)
def siren_fade():
    """The police lights wash in from the left and fade out across the studio."""
    import numpy as np
    row = np.clip(1.0 - np.arange(W, dtype=np.float32) / 190.0, 0, 1) ** 1.5
    return np.tile(row, (H, 1))


@gag("v2", 6)
def songs_and_feds(c, L):
    a_sing, a_feds = age(L, "sings"), age(L, "feds")
    if a_sing > -0.1 and a_feds < 0:
        pose(c, "mamdani", eyes="shut", mouth="grin", brows="up", bob=1 if int(L.t * 4) % 2 else 0)
        c.phone_lit = True
    if a_feds > 0:
        pose(c, "newsom", eyes="wide", brows="worried", mouth="o", arms="shrug", react=False)
    yield "mid"
    if a_feds > -0.6:                                                  # the Guard marches along the desk
        for j in range(5):
            x = -12 + (a_feds + 0.6) * 90 - j * 14
            if -10 < x < 150:
                step = 1 if int((L.t + j * 0.1) * 8) % 2 else 0
                put(c.world, P.soldier(), x, studio.DESK_Y + 1 - step, "mb")
    yield "front"
    if a_sing > 0 and a_feds < 0.4:                                     # love songs from the phone
        for j in range(6):
            p = (a_sing * 0.9 + j / 6) % 1.0
            x, y = arc_pt(p, PHONE_ON_DESK, (238, 60), 10)
            spr = P.note(j % 2) if j % 3 else P.heart(2)
            put(c.world, spr, x + 4 * math.sin(p * 8 + j), y)
    if 0 < a_feds < 1.6:                                               # the sirens
        blend(c.world, siren_fade(), C["red"] if int(a_feds * 6) % 2 else C["blue"], 0.3)


@gag("v2", 7)
def tonight(c, L):
    a_text, a_bed = age(L, "texts"), age(L, "bed")
    if a_text > -0.1:
        buzz(c, a_text + 0.1)
        if a_bed < 0:
            pose(c, "mamdani", eyes="side", flush=1, mouth="smile")
    if a_bed > 0:
        pose(c, "newsom", eyes="shut", brows="neutral", mouth="closed", arms="clasp", react=False)
    yield "front"
    if a_bed > 0:
        on_head(c, c.world, "newsom", P.nightcap(), dy=-6)
        hx, hy = c.anchor["newsom"]["head"]
        P.zzz(c.world, hx + 18, hy + 4, a_bed)
    yield "ui"
    if a_text > -0.2:
        msgs = [("l", "TONIGHT? ;)")] + ([("r", "<3")] if a_text > 0.7 else [])
        inset(c, INSET, P.imessage(msgs), "HIS PHONE", k_in(a_text + 0.2, 0.25))


@gag("v2", 8, post=0.25)
def rent_free(c, L):
    a_l, a_rent = age(L, "lounged"), age(L, "rent-free")
    if a_rent > -0.1:
        pose(c, "newsom", eyes="up", brows="worried", mouth="frown", arms="clasp", react=False)
    yield "ui"
    if a_l > -0.2 and a_rent < 0:
        inset(c, INSET, P.lounge(a_l), "HIS PLACE", k_in(a_l + 0.2, 0.25))
    if a_rent > 0:
        think(c, "newsom", P.rent_free_head(), a_rent)
