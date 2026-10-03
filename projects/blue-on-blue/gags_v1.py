"""Verse 1: Newsom has notes. The guest is a TikTok Trotsky who texts the rich and sexts Donnie; Trump calls
him a hottie, tours his mansion, pats his head and then sues him; and the host hugged Trump first."""
from gagkit import *  # noqa: F403

MAM_DESK = (238, 118)                # in front of Mamdani on the desk
RIGHT_EDGE = 330


@gag("v1", 0)
def tiktok_trotsky(c, L):
    a, a_t = age(L, "campaign"), age(L, "Trotsky")
    if a > -0.3:
        hold(c, "newsom", P.phone_held(), arms="hold")
    if 0 < age(L, "cute") < 1.0:
        pose(c, "mamdani", arms="wave", eyes="shut", mouth="grin")
    if a_t > 0.2:
        pose(c, "mamdani", eyes="side", brows="up", mouth="smile")
    yield "ui"
    inset(c, INSET, P.tiktok(max(0.0, a), filt=a_t > 0), "HIS TIKTOK", k_in(a + 0.2, 0.25))


@gag("v1", 1)
def sexting_donnie(c, L):
    a_tax, a_sext = age(L, "Tax"), age(L, "sexting")
    if -0.2 < a_tax and a_sext < 0:
        hold_up(c, "mamdani", P.placard("TAX THE", "RICH"))
        pose(c, "mamdani", mouth="grin", brows="up")
    if a_sext > -0.15:
        buzz(c, a_sext + 0.15)
        pose(c, "mamdani", eyes="side", flush=1, mouth="smile")
    yield "ui"
    if a_sext > -0.15:
        msgs = [("l", "HEY HANDSOME")] + ([("r", "STOP IT")] if a_sext > 0.5 else [])
        inset(c, INSET, P.imessage(msgs, typing=a_sext > 0.9), "HIS PHONE", k_in(a_sext + 0.15, 0.2))


@gag("v1", 2)
def commie_hottie(c, L):
    a, a_sw, a_hot = age(L, "Trump"), age(L, "switched"), age(L, "hottie")
    pose(c, "newsom", arms="point" if a_hot > 0 else c.st["newsom"]["arms"])
    if a_hot > 0:
        pose(c, "mamdani", mouth="grin", eyes="shut", brows="up", flush=1)
    yield "ui"
    post = P.truth_post(["ZOHRAN IS A", "COMMUNIST!"], strike=1 if a_sw > 0 else None,
                        fix="HOTTIE!" if a_hot > 0 else None)
    inset(c, INSET, post, "THE PRESIDENT", k_in(a + 0.2, 0.25))


@gag("v1", 3)
def caddie(c, L):
    a_dont, a_says = age(L, "Don't"), age(L, "says")
    if a_dont < 0.9:                                                   # he takes the compliment: "Thank you."
        pose(c, "mamdani", arms="chest", eyes="shut", mouth="grin" if a_dont > 0.5 else "open")
    if a_dont > 0 and a_says < 0:
        pose(c, "newsom", arms="finger", brows="angry")
    yield "ui"
    say(c, "mamdani", "THANK YOU.", a_dont + 0.3, dur=1.2)
    if a_says > -0.2:
        inset(c, INSET, P.golf(a_says), "THE CADDIE", k_in(a_says + 0.2, 0.25))


@gag("v1", 4)
def sugar_daddy(c, L):
    a_h, a_s = age(L, "housing"), age(L, "sugar")
    if a_h > -0.1 and a_s < 0:
        pose(c, "mamdani", arms="beg", eyes="up", brows="up", mouth="smile")
    if a_s > -0.1:
        pose(c, "mamdani", arms="desk", eyes="shut", mouth="grin", brows="up")
    yield "front"
    if a_s > -0.1:                                                     # the novelty cheque, propped on the desk
        pop_in(c.world, P.big_check(), 240, 107, a_s + 0.1)
    yield "ui"
    if a_s > 0:
        P.sparkles(c.ui, *c.to_ui(240, 100), a_s, n=5, r=34, color="gold_hi")


@gag("v1", 5)
def stood_up(c, L):
    a, a_sw = age(L, "stood"), age(L, "swing")
    if a_sw > 0:
        pose(c, "mamdani", mouth="grin", brows="up")
    yield "ui"
    if a_sw < 0:
        inset(c, INSET, P.stood_up(max(0.0, a)), "THE PLANET", k_in(a + 0.2, 0.25))
    else:
        inset(c, INSET, P.lobby(a_sw), "YOUR LOBBY")


@gag("v1", 6)
def toasts_texts_tours(c, L):
    a_toast, a_text, a_tour = age(L, "toasts"), age(L, "texts"), age(L, "tours")
    if a_toast > -0.1 and a_text < 0:
        hold_up(c, "mamdani", P.wine_glass())
        pose(c, "mamdani", eyes="shut", mouth="grin")
    if a_text > -0.1:
        buzz(c, a_text + 0.1)
    yield "ui"
    if 0 <= a_toast < 0.6:
        shout(c, 240, 30, "CLINK!", a_toast, size=8, dur=0.6)
    if a_tour > -0.2:
        inset(c, INSET, P.mansion(a_tour, gold=max(0.0, a_tour) / 0.9), "GRACIE MANSION", k_in(a_tour + 0.2, 0.25))


@gag("v1", 7)
def pats_and_praise(c, L):
    a_pat, a_pr, a_face, a_fash = age(L, "pats"), age(L, "praises"), age(L, "face"), age(L, "fashion")
    patting = -0.3 < a_pat and a_pr < 0.3
    if patting:
        pose(c, "mamdani", eyes="shut", mouth="grin", brows="up")
    if a_pr > 0:
        pose(c, "mamdani", arms="chest", eyes="shut", mouth="grin", flush=1)
    yield "front"
    if patting:                                                        # Trump's hand, reaching into the studio
        hx, hy = c.anchor["mamdani"]["head"]
        reach = clamp((a_pat + 0.3) / 0.25, 0, 1)
        x = lerp(RIGHT_EDGE, hx - 6, ease_out(reach))
        y = hy - 4 + (2 if int(L.t * 8) % 2 and reach >= 1 else 0)
        paste(c.world, P.tiny_hand(), int(x), int(y), "lt")
    yield "ui"
    if a_face > 0:
        hx, hy = c.anchor["mamdani"]["head"]
        P.sparkles(c.ui, *c.to_ui(hx, hy + 20), a_face, n=4, r=16)
    if a_fash > 0:
        P.sparkles(c.ui, *c.to_ui(236, 106), a_fash, n=5, r=18, color="gold_hi")
    if a_pr > -0.2:
        inset(c, INSET, P.truth_post(["GREAT FACE.", "GREAT SUITS.", "HANDSOME!"], likes="120K"), "THE PRESIDENT",
              k_in(a_pr + 0.2, 0.25))


@gag("v1", 8)
def sue_squeeze_seize(c, L):
    a_sue, a_sq, a_seize, a_man = age(L, "sue"), age(L, "squeeze"), age(L, "seize"), age(L, "Manhattan")
    if a_sue > 0.25:
        pose(c, "mamdani", mouth="o", brows="worried", eyes="wide")
    if a_man > 0:
        c.add_shake(3 * max(0.0, 1 - a_man / 0.3))
    yield "front"
    if a_sue > -0.1:                                                   # the lawsuit lands on his side of the desk
        p = clamp((a_sue + 0.1) / 0.3, 0, 1)
        x, y = lerp(200, MAM_DESK[0] - 18, p), lerp(-20, MAM_DESK[1] - 2, ease_in(p))
        put(c.world, P.lawsuit(), x, y)
    yield "ui"
    if a_sq > -0.2:
        claimed = 0 if a_seize < 0 else min(8, 1 + int(a_seize / 0.07))
        inset(c, INSET, P.skyline(a_sq, claimed), "MANHATTAN", k_in(a_sq + 0.2, 0.25))


@gag("v1", 9)
def hugged_first(c, L):
    a_hug, a_never, a_h = age(L, "hugged"), age(L, "never"), age(L, "handsome")
    sad = a_never > 0
    if sad:
        pose(c, "newsom", arms="clasp", eyes="half", brows="worried", mouth="frown", tears=a_h > -0.2, react=False)
    if a_h > 0 and a_h < 1.2:
        c.shot = "newsom"
    yield "front"
    if sad:                                                            # a little rain cloud of his own
        hx, hy = c.anchor["newsom"]["head"]
        k = clamp(a_never / 0.3, 0, 1)
        put(c.world, P.rain_cloud(), hx + 2, hy - 14 + int((1 - k) * -10))
        d = ImageDraw.Draw(c.world)
        for j in range(5):
            ry = (int(L.t * 40) + j * 7) % 14
            d.line([(hx - 10 + 5 * j, hy - 8 + ry), (hx - 11 + 5 * j, hy - 6 + ry)], fill=C["tear"])
    yield "ui"
    if a_hug > -0.2 and not (a_h > 0 and a_h < 1.2):
        inset(c, INSET, P.tarmac(a_hug), "THE HUG", k_in(a_hug + 0.2, 0.25))
