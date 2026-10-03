"""Verse 3: Trump's comeback. The model, Daddy, the candy, the apology call he held the phone for, the
caddy, two weeks, the beautiful bone spurs, and two bookings: Oslo for him, The Hague for Bibi."""
from gagkit import *  # noqa: F403

T_BARS = when("v3", 10, "cell")
T_LIFT = when("bridge", 0) + 0.8


@gag("v3", 0)
def model(c, L):
    a = age(L, "Model")
    pose(c, "trump", arms="thumb" if a > 0 else "pinch", mouth="grin" if age(L, "Thank") > 0 else "o",
         eyes="squint", lean=1)
    if age(L, "models") > 0:
        flash_press(c, "models", 8, age(L, "models"))
    yield "front"
    if a > 0:
        P.sparkles(c.world, 230, 66, a, n=5, r=22)


@gag("v3", 1)
def daddy(c, L):
    a_d, a_b = age(L, "Daddy"), age(L, "bottles")
    if age(L, "warm") > -0.2:
        hold_up(c, "trump", P.bottle(), lift=2)
        pose(c, "trump", mouth=c.st["trump"]["mouth"], eyes="squint")
    if a_b > 0.35:
        c.st["trump"].update(held=None, arms="thumb")
        hold_up(c, "bibi", P.bottle(), lift=2)
        pose(c, "bibi", mouth="frown", brows="angry", eyes="half", react=False)
    yield "mid"
    if 0 <= a_b <= 0.35:
        fly(c.world, P.bottle(), (220, 82), (106, 82), a_b / 0.35, h=20, rot=1)
    yield "ui"
    shout(c, 230, 40, "DADDY!", a_d, dur=1.3, top=C["gold_hi"], bottom=C["red"])


@gag("v3", 2)
def candy(c, L):
    a = age(L, "bunker")
    pose(c, "bibi", arms="beg", eyes="wide", mouth="o" if not V.singing(c, "bibi") else "o", brows="worried", react=False)
    if a > -0.2:
        hold(c, "trump", mirror(P.bunker_buster()), arms="hold")
        pose(c, "trump", mouth=c.st["trump"]["mouth"], eyes="squint")
    yield "front"
    if age(L, "candy") > 0:
        P.sparkles(c.world, 229, 94, age(L, "candy"), n=4, r=26, seed=2)


def cord(img, a, b, t):
    """The phone's curly cord, strung across the room."""
    d = ImageDraw.Draw(img)
    n = 40
    pts = []
    for i in range(n + 1):
        p = i / n
        x, y = lerp(a[0], b[0], p), lerp(a[1], b[1], p) + 18 * math.sin(p * math.pi)
        y += 1.5 * math.sin(p * 70 + t * 3)
        pts.append((x, y))
    d.line(pts, fill=(160, 152, 130))


@gag("v3", 3)
def say_sorry(c, L):
    a_s, a_d = age(L, "sorry"), age(L, "Daddy")
    hold(c, "trump", P.phone(receiver=False), arms="hold")
    pose(c, "trump", mouth=c.st["trump"]["mouth"] if a_d < 0.2 else "grin", eyes="squint")
    pose(c, "bibi", arms="phone", mouth="frown", eyes="half", brows="worried", react=False)
    if a_d > 0:
        pose(c, "trump", arms="thumb")
        c.st["trump"]["held"] = None
    yield "mid"
    rx, ry = c.anchor["bibi"]["hand_near"]
    put(c.world, P.receiver(), rx + 1, ry - 2)
    if a_d < 0:
        cord(c.world, (rx + 2, ry + 6), (229, 98), c.t)
    yield "ui"
    if a_s > 0 and a_d < 0:
        say(c, "bibi", "SORRY...", 0.0, dy=-2)
    shout(c, 236, 40, "DADDY!", a_d, size=8, dur=1.2, top=C["gold_hi"], bottom=C["red"])


def club(img, gx, gy, ang):
    """The golf club, its grip in the fist at (gx, gy), swung `ang` degrees from hanging straight down."""
    r = math.radians(ang)
    dx, dy = -1, 14                                                    # grip to the sprite's centre
    cx = gx + dx * math.cos(r) + dy * math.sin(r)
    cy = gy - dx * math.sin(r) + dy * math.cos(r)
    paste_rot(img, P.golf_club(), int(round(cx)), int(round(cy)), ang)


@gag("v3", 4)
def caddy(c, L):
    a_sw, a_bag = age(L, "swing"), age(L, "bag")
    if a_bag > -0.2:
        hold(c, "bibi", P.golf_bag(), arms="lap", at="lap")
        pose(c, "bibi", mouth="frown", eyes="half", brows="worried", react=False)
    pose(c, "trump", arms="fist", mouth=c.st["trump"]["mouth"], eyes="squint")
    if 0.2 < a_sw < 1.2:
        pose(c, "bibi", eyes="up")
    yield "mid"
    hx, hy = c.anchor["trump"]["hand_far"]
    club(c.world, hx, hy, lerp(150, -130, ease_in_out(clamp(a_sw / 0.3, 0, 1))))
    if 0.15 <= a_sw < 0.95:                                            # the ball, over Bibi's head
        x, y = arc_pt((a_sw - 0.15) / 0.8, (204, 108), (-10, 30), 40)
        ImageDraw.Draw(c.world).ellipse((x - 1, y - 1, x + 1, y + 1), fill=C["white"], outline=INK)
    yield "ui"
    shout(c, 214, 46, "FORE!", a_sw - 0.15, size=8, dur=1.0)
    if age(L, "caddy") > 0:
        x, y = c.to_ui(92, 132)
        fx.label(c.ui, (int(x), int(y)), "CADDY", SILK, bg=C["white"], fg=C["ink"], anchor="ma", th=5, text_dy=-4)


@gag("v3", 5)
def weeks_away(c, L):
    hold(c, "bibi", P.poster("weeks"))
    yield "front"
    p = clamp((L.t - wt(L, "decades")) / max(0.5, end_of(L) - wt(L, "decades")), 0, 1)
    year = 1992 + int(round(33 * ease_in_out(p)))
    bx, by = c.anchor["bibi"]["hand_near"]
    ax, ay = c.anchor["bibi"]["hand_far"]
    cx, cy = (bx + ax) // 2, (by + ay) // 2 - 8
    ImageDraw.Draw(c.world).rectangle((cx - 12, cy - 2, cx + 12, cy + 6), fill=C["paper"])
    ImageDraw.Draw(c.world).text((cx, cy - 3), str(year), font=SILK, fill=C["mk_red"], anchor="ma")


@gag("v3", 6)
def two_days(c, L):
    a_w, a_b, a_d = age(L, "weeks"), age(L, "bombed"), age(L, "days")
    if a_w > -0.2:
        hold(c, "trump", P.folder("2 WEEKS") if a_d < 0 else P.folder("2 DAYS"))
    if 0 < a_d < 0.5:
        flash_press(c, "days", 6, a_d)
    yield "front"
    if 0 <= a_b < 1.4:
        x = lerp(350, -60, a_b / 1.4)
        put(c.world, mirror(P.b2()), x, 16)
        if a_b < 0.15:
            c.add_shake(2)


@gag("v3", 7)
def bone_spurs(c, L):
    a = age(L, "spurs")
    if a > -0.3:
        hold(c, "trump", P.xray())
        pose(c, "trump", mouth=c.st["trump"]["mouth"], eyes="squint", lean=1)
    yield "front"
    if age(L, "impressed") > 0:
        P.sparkles(c.world, 229, 88, age(L, "impressed"), n=4, r=20)


@gag("v3", 8)
def which_foot(c, L):
    a, a_best = age(L, "foot"), age(L, "best")
    pose(c, "trump", arms="shrug", brows="up", mouth=c.st["trump"]["mouth"], eyes="side" if a > 0 else "squint")
    yield "ui"
    if a > -0.2:
        pic = P.feet_inset(best=True) if a_best > 0 else P.feet_inset(which=c.beat_i % 2)
        inset(c, (118, 18, 202, 82), pic, "WHICH FOOT?", k_in(a + 0.2, 0.25))


@gag("v3", 9)
def booked(c, L):
    if age(L, "booked") > -0.3:
        hold(c, "trump", P.two_tickets(), arms="hold")
        pose(c, "trump", mouth=c.st["trump"]["mouth"], eyes="squint")
    yield "ui"


@gag("v3", 10)
def the_hague(c, L):
    a_o = age(L, "Oslo")
    if a_o > -0.2:
        hold_up(c, "trump", P.ticket("OSLO"), lift=2)
        pose(c, "trump", mouth=c.st["trump"]["mouth"], eyes="squint")
    a = c.t - T_BARS
    if a > 0:
        pose(c, "bibi", eyes="wide", mouth="o", brows="worried", sweat=True, react=False)
    yield "front"
    if a_o > 0:
        P.sparkles(c.world, 222, 70, a_o, n=3, r=12)


@span(T_BARS, T_LIFT + 0.6)
def bars(c, L):
    a = c.t - T_BARS
    if 0 <= a < 0.12:
        c.add_flash(0.3)
    c.add_shake(6 * max(0.0, 1 - max(0.0, a - 0.15) / 0.3) if a > 0.15 else 0)
    yield "mid"
    y = lerp(-80, 50, ease_in(min(1.0, a / 0.15)))
    if c.t > T_LIFT:
        y = lerp(50, -90, ease_in(min(1.0, (c.t - T_LIFT) / 0.6)))
    put(c.world, P.bars(), 90, y, anchor="mt")
    yield "ui"
    if 0.15 < a < 1.1:
        shout(c, 90, 40, "CLANG!", a - 0.15, size=8, dur=0.9, top=C["white"], bottom=C["steel"])
