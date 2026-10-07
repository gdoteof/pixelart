"""Flat vector: clean shapes, no outlines, two tones to a surface, and smooth eased motion at the full 24
frames a second. The look of a modern explainer or a title sequence."""
from functools import lru_cache

import skia

import acting
import props
import puppet
import script as S
import sk

NAME = "Flat vector"
ASMON_AT, HASAN_AT = (372, 425, 150), (1556, 445, 140)
BOARD = (620, 152, 0.68)                    # the window's content: left, top, pixels to a board unit
GREEN, PURPLE = (96, 226, 48), (150, 96, 255)
DESK_Y = 938


def draw(c, parts, alpha=1.0):
    for q in parts:
        col = puppet.colour(q.who, q.col)
        if q.open:
            c.drawPath(q.path, sk.stroke(col, q.w, alpha))
        else:
            c.drawPath(q.path, sk.fill(col, alpha))


@lru_cache(maxsize=None)
def backdrop():
    """Two rooms, tone on tone: his attic on the left, Hasan's place on the right."""
    s = sk.surface(S.W, S.H)
    c = s.getCanvas()
    left, right = (44, 62, 54), (58, 46, 92)
    c.drawRect(skia.Rect.MakeWH(S.W, S.H), sk.fill(left))
    c.drawPath(sk.poly([(1010, 0), (S.W, 0), (S.W, S.H), (910, S.H)]), sk.fill(right))
    glow = skia.Paint(AntiAlias=True)
    for (x, y), col in (((385, 430), (86, 116, 96)), ((1535, 440), (104, 82, 160))):
        glow.setShader(skia.GradientShader.MakeRadial(center=(x, y), radius=620, colors=[sk.rgb(col, 0.55), sk.rgb(col, 0.0)]))
        c.drawCircle(x, y, 620, glow)
    hi, lo = (58, 80, 70), (34, 50, 44)
    # the attic: a sloping beam, a crooked frame, a bare bulb, the bin bags
    c.drawPath(sk.poly([(0, 0), (560, 0), (0, 250)]), sk.fill(lo))
    c.drawPath(sk.xf(sk.rect(-70, -52, 70, 52, 4), 96, 470, rot=-9), sk.fill(hi))
    c.drawPath(sk.xf(sk.rect(-54, -36, 54, 36, 2), 96, 470, rot=-9), sk.fill(left))
    c.drawLine(640, 0, 640, 96, sk.stroke(lo, 5))
    c.drawPath(sk.oval(640, 118, 20, 26), sk.fill((150, 160, 110)))
    for x, r in ((70, 96), (165, 70)):
        c.drawPath(sk.curve([(x - r, 940), (x - r * 0.8, 940 - r * 0.9), (x, 940 - r * 1.25, "c"), (x + r * 0.8, 940 - r * 0.9),
                             (x + r, 940)]), sk.fill(lo))
    hi, lo = (78, 62, 120), (44, 34, 72)
    # Hasan's: a light strip, shelves with a trophy, a big plant
    c.drawRect(skia.Rect.MakeLTRB(1040, 58, S.W, 68), sk.fill((190, 150, 255)))
    strip = sk.fill((170, 120, 255), 0.35)
    strip.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.drawRect(skia.Rect.MakeLTRB(1040, 40, S.W, 96), strip)
    for y in (250, 420):
        c.drawRect(skia.Rect.MakeLTRB(1770, y, S.W, y + 14), sk.fill(hi))
    c.drawPath(sk.union(sk.rect(1808, 196, 1862, 232, 6), sk.rect(1826, 232, 1844, 250)), sk.fill(hi))
    for k, (dx, dy, rot) in enumerate(((0, 0, -30), (34, -40, 10), (-30, -70, -55), (20, -120, -12), (60, -86, 38))):
        c.drawPath(sk.xf(sk.oval(0, -60, 30, 64), 1292 + dx, 760 + dy, rot=rot), sk.fill(hi if k % 2 else lo))
    c.drawPath(sk.rect(1262, 770, 1330, 940, 8), sk.fill(lo))
    # the desk they share
    c.drawRect(skia.Rect.MakeLTRB(0, DESK_Y, S.W, S.H), sk.fill((22, 20, 28)))
    c.drawRect(skia.Rect.MakeLTRB(0, DESK_Y, S.W, DESK_Y + 6), sk.fill((60, 56, 76)))
    return s.makeImageSnapshot()


def board_xy(x, y):
    return BOARD[0] + x * BOARD[2], BOARD[1] + y * BOARD[2]


def scene_house(c, t):
    w, h = props.BOARD
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(skia.GradientShader.MakeLinear(points=[(0, 0), (0, 500)], colors=[sk.rgb((150, 206, 240)), sk.rgb((236, 232, 214))]))
    c.drawRect(skia.Rect.MakeWH(w, 500), sky)
    c.drawRect(skia.Rect.MakeLTRB(0, 498, w, 536), sk.fill((112, 176, 104)))
    c.drawRect(skia.Rect.MakeLTRB(0, 536, w, h), sk.fill((66, 138, 150)))
    for x in range(0, w + 1, 79):
        c.drawLine(x, 536, x, h, sk.stroke((54, 120, 132), 3))
    for y in (536, 598, 660):
        c.drawLine(0, y, w, y, sk.stroke((54, 120, 132), 3))
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, w, 500))
    draw(c, props.house_at(t))
    c.restore()
    draw(c, props.flag(t))
    draw(c, props.tubs(t))
    k = S.pop(t, S.EV["baths"], 0.22, 2.6)
    if k > 0:
        x, y, rot = props.STAMP
        c.save()
        c.translate(x, y)
        c.rotate(rot)
        c.scale(k, k)
        c.drawPath(sk.rect(-186, -58, 186, 58, 16), sk.fill((255, 255, 255)))
        c.drawPath(sk.rect(-186, -58, 186, 58, 16), sk.stroke((216, 40, 50), 9))
        sk.text(c, "5½ BATHS", 0, 28, sk.font("black", 76), sk.fill((216, 40, 50)), "m")
        c.restore()


def scene_score(c, t):
    w, h = props.BOARD
    c.drawRect(skia.Rect.MakeWH(w, h), sk.fill((24, 22, 34)))
    sk.text(c, "BATHS THIS YEAR", 500, 118, sk.font("black", 84), sk.fill((255, 214, 64)), "m")
    for key, name, tint, edge in (("him", "HIM", (46, 34, 84), PURPLE), ("me", "ME", (22, 54, 30), GREEN)):
        x0, y0, x1, y1 = props.SCORE[key]
        c.drawPath(sk.rect(x0, y0, x1, y1, 22), sk.fill(tint))
        c.drawPath(sk.rect(x0, y0, x1, y1, 22), sk.stroke(edge, 8))
        sk.text(c, name, (x0 + x1) / 2, y0 + 92, sk.font("black", 70), sk.fill(edge), "m")
    x0, y0, x1, y1 = props.SCORE["him"]
    sk.text(c, "5½", (x0 + x1) / 2, y1 - 110, sk.font("black", 290), sk.fill((255, 255, 255)), "m")
    x0, y0, x1, y1 = props.SCORE["me"]
    me = props.me_score(t)
    k = S.pop(t, S.EV["had"], 0.24, 3.0) if me == "0" and t >= S.EV["had"] else 1.0
    c.save()
    c.translate((x0 + x1) / 2, y1 - 110)
    c.scale(k, k)
    col = (255, 84, 72) if t >= S.EV["had"] else (150, 160, 150) if me == "?" else (220, 230, 220)
    sk.text(c, me, 0, 0, sk.font("black", 290), sk.fill(col), "m")
    c.restore()


def board(c, t):
    x, y, k = BOARD
    w, h = props.BOARD[0] * k, props.BOARD[1] * k
    bar = 46
    second = t >= S.EV["line2"]
    frame = sk.rect(x - 7, y - bar - 7, x + w + 7, y + h + 7, 14)
    shadow = sk.fill((0, 0, 0), 0.45)
    shadow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
    c.drawPath(sk.xf(frame, 0, 18), shadow)
    c.drawPath(frame, sk.fill((244, 242, 250)))
    c.drawPath(sk.rect(x, y - bar, x + w, y - 4, 8), sk.fill(GREEN if second else PURPLE))
    ink = (16, 28, 12) if second else (255, 255, 255)
    sk.text(c, "ASMONGOLD  ·  STATS" if second else "HASANABI  ·  HOME", x + 16, y - 17, sk.font("black", 25), sk.fill(ink))
    sk.text(c, "●  LIVE", x + w - 14, y - 17, sk.font("black", 22), sk.fill(ink), "r")
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x, y, w, h), doAntiAlias=True)
    slide = S.ease_out(S.since("line2", t) / 0.2) if second else 0.0
    if slide < 1:
        c.save()
        c.translate(x - slide * w, y)
        c.scale(k, k)
        scene_house(c, t)
        c.restore()
    if second:
        c.save()
        c.translate(x + (1 - slide) * w, y)
        c.scale(k, k)
        scene_score(c, t)
        c.restore()
    c.restore()


def caption(c, t):
    line, words = S.caption(t)
    if not line:
        return
    fnt = sk.font("black", 56)
    space = sk.text_width(" ", fnt) * 1.1
    widths = [sk.text_width(w, fnt) for w, _ in words]
    x = S.W / 2 - (sum(widths) + space * (len(words) - 1)) / 2
    for (w, state), wd in zip(words, widths):
        col, a = ((255, 255, 255), 0.4) if state == 0 else (GREEN, 1.0) if state == 1 else ((255, 255, 255), 1.0)
        sk.text(c, w, x, 1028, fnt, sk.fill(col, a))
        x += wd + space


def frame(t):
    s = sk.surface(S.W, S.H)
    c = s.getCanvas()
    c.drawImage(backdrop(), 0, 0)
    board(c, t)
    a_pose, h_pose = acting.pose("asmon", t), acting.pose("hasan", t)
    c.save()
    c.clipRect(skia.Rect.MakeLTRB(0, 0, S.W, DESK_Y))
    draw(c, puppet.figure("asmon", a_pose, ASMON_AT))
    draw(c, puppet.figure("hasan", h_pose, HASAN_AT))
    c.restore()
    ax, ay, sc = ASMON_AT
    for path, strength in props.stink(t):
        c.drawPath(sk.xf(path, ax, ay, sc), sk.stroke(puppet.colour("prop", "stink"), 0.07 * sc, 0.85 * strength))
    for fx, fy, wing, heading in props.flies(t):
        draw(c, props.fly(ax + fx * sc, ay + fy * sc, sc * 1.25, wing, heading))
    caption(c, t)
    return sk.image(s)
