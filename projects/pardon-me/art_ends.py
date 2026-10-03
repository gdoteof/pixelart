"""Sprites and screen cards for the intro, the hook, the outro and the end card: the stampeding
lawyers, Bibi's armful of rolled-up posters, the delegates' placards, the UN title card, the rap
sheets, the mugshot boards and the voting board. Sprites are cached RGBA images outlined in ink;
the screen cards are `fn(c, img, box)` callables for `c.screens`.

    uv run python projects/pardon-me/art_ends.py     # -> build/art_ends.png, a sheet of the sprites
"""
import math
from functools import lru_cache
from types import SimpleNamespace

from PIL import Image, ImageDraw

import hall
import video as V
from characters import figure
from engine import C, INK, PRESS, SILK, Canvas, mix, outlined, rnd, text_width
from props import new_page, page_title, stick_figure, write

UN_BLUE, UN_DEEP = C["un_sh"], (30, 64, 128)


# --- the stampede: tiny lawyers with briefcases -----------------------------------------------------

LAWYER_SKIN = ((236, 190, 160), (214, 160, 124), (168, 112, 76), (112, 74, 52))
LAWYER_HAIR = ((40, 32, 30), (110, 74, 44), (170, 170, 180), (222, 184, 96), (26, 22, 28))
LAWYER_SUIT = ((52, 56, 72), (40, 50, 92), (78, 78, 88), (66, 46, 54))
LAWYER_TIE = ((214, 38, 48), (84, 140, 220), (60, 170, 90), (246, 200, 70))
CASE = (122, 78, 50)


@lru_cache(maxsize=64)
def lawyer(frame=0, v=0):
    """A tiny lawyer sprinting right with a briefcase, about 13x17; `frame` 0/1 is the stride."""
    skin = LAWYER_SKIN[v % 4]
    hair = LAWYER_HAIR[(v * 3 + 1) % 5]
    suit = LAWYER_SUIT[(v * 7 + 2) % 4]
    tie = LAWYER_TIE[(v * 5 + 3) % 4]
    sh = mix(suit, (0, 0, 0), 0.35)
    s = Canvas(15, 19)
    if frame == 0:                                   # full stride: back leg out behind, front leg reaching
        s.line([(6, 11), (3, 15)], sh)
        s.rect((1, 15, 3, 16), "shoe")
        s.line([(7, 11), (10, 14)], suit)
        s.rect((10, 14, 12, 15), "shoe")
    else:                                            # legs passing under the body
        s.line([(6, 11), (5, 15)], sh)
        s.rect((4, 15, 6, 16), "shoe")
        s.line([(7, 11), (8, 13)], suit)
        s.line([(8, 13), (7, 15)], suit)
        s.rect((7, 15, 9, 16), "shoe")
    s.rect((5, 6, 9, 11), suit)                      # the jacket, leaning into the run
    s.px((10, 7), suit)
    s.rect((7, 6, 8, 7), "white")
    s.px((8, 8), tie)
    s.ell((6, 1, 10, 5), skin)                       # head
    s.rect((6, 1, 9, 2), hair)
    s.px((6, 3), hair)
    s.px((9, 3), "eye")
    if frame == 0:                                   # the briefcase swings forward, then back
        s.line([(8, 8), (11, 9)], suit)
        s.rect((10, 9, 13, 12), CASE)
        s.line([(10, 9), (13, 9)], mix(CASE, (255, 255, 255), 0.3))
        s.line([(6, 8), (4, 9)], sh)
    else:
        s.line([(7, 8), (6, 10)], suit)
        s.rect((3, 10, 6, 13), CASE)
        s.line([(3, 10), (6, 10)], mix(CASE, (255, 255, 255), 0.3))
        s.line([(8, 8), (10, 8)], sh)
    return s.done()


def dust(img, x, y, age, size=1.0, seed=0, life=0.5):
    """A small puff of carpet dust that pops up and shrinks away."""
    if not 0 <= age < life:
        return
    p = age / life
    d = ImageDraw.Draw(img)
    r0 = size * (2.5 + 3 * math.sin(min(1.0, p * 1.6) * math.pi / 2)) * (1 - p * 0.6)
    for k in range(3):
        a = rnd("dust", seed, k) * math.pi + math.pi
        cx = x + math.cos(a) * r0 * 0.8 - p * 4 * size
        cy = y + math.sin(a) * r0 * 0.5 - p * 3 * size
        r = r0 * (0.55 + 0.3 * rnd("dr", seed, k))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(204, 196, 206))
        if r > 2:
            d.ellipse((cx - r + 1, cy - r + 1, cx + r - 2, cy + r - 2), fill=(228, 222, 230))


# --- Bibi's visual aids: an armful of rolled-up posters ----------------------------------------------

ROLL_COLORS = ((250, 250, 244), (236, 232, 214), (214, 230, 246), (250, 226, 226), (236, 246, 222))


@lru_cache(maxsize=64)
def poster_bundle(n=9, length=58):
    """A bundle of rolled-up posters held under one arm, splayed at the top, bound with a red band.
    Drawn upright; about 30 x (length + 6). The point to hold it by is returned by `bundle_grip`."""
    w, h = 34, length + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bx, by = w // 2, h - 4                           # where the rolls meet at the bottom
    rolls = []
    for i in range(n):
        f = i / (n - 1) - 0.5
        top = (bx + f * 24 + (rnd("roll", i) - 0.5) * 3, 4 + rnd("rolltop", i) * 10 + abs(f) * 8)
        bot = (bx + f * 7, by - rnd("rollbot", i) * 3)
        rolls.append((top, bot, ROLL_COLORS[i % len(ROLL_COLORS)]))
    for top, bot, col in sorted(rolls, key=lambda r: r[0][1]):
        d.line([top, bot], fill=INK + (255,), width=5)
        d.line([top, bot], fill=col + (255,), width=3)
    for top, bot, col in rolls:                     # the open ends: a little spiral of paper
        x, y = round(top[0]), round(top[1])
        d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=col + (255,))
        d.point((x, y), fill=(150, 150, 160, 255))
    band = by - 16                                   # the rubber band round the middle
    d.line([(bx - 7, band + 1), (bx + 7, band - 1)], fill=INK + (255,), width=3)
    d.line([(bx - 6, band + 1), (bx + 6, band - 1)], fill=C["red"] + (255,), width=1)
    return outlined(img, INK)


def bundle_grip(spr):
    """The point of the bundle sprite that sits in the crook of the arm."""
    return spr.width // 2, spr.height - 18


@lru_cache(maxsize=64)
def sharpie():
    """A fat black permanent marker, nib up, about 7x18: Trump's visual aid."""
    s = Canvas(7, 19)
    s.rect((2, 1, 4, 2), (60, 60, 70))                # the nib
    s.rect((1, 3, 5, 17), (34, 34, 42))               # barrel
    s.line([(2, 4), (2, 16)], (90, 90, 104))          # shine
    s.rect((1, 8, 5, 11), "white")                    # the label band
    s.line([(2, 9), (4, 9)], (34, 34, 42))
    s.rect((1, 16, 5, 17), (70, 70, 84))              # the end cap
    return s.done()


# --- the delegates' placards -------------------------------------------------------------------------

@lru_cache(maxsize=64)
def placard(lines, color="white", fg="ink", stick=12):
    """A hand-lettered protest placard on a stick: `lines` is a tuple of strings (SILK)."""
    w = max(text_width(s, SILK) for s in lines) + 5
    h = 4 + 7 * len(lines)
    s = Canvas(w + 2, h + stick + 2)
    s.rect((w // 2 - 1 + 1, h, w // 2 + 1, h + stick), "desk_sh")
    s.rect((1, 1, w, h), color)
    s.rect((1, h - 1, w, h), "paper_sh")
    for i, txt in enumerate(lines):
        write(s.img, (w // 2 + 1, 3 + 7 * i), txt, fg, fnt=SILK, anchor="ma")
    return s.done()


# --- the flip chart's pages ----------------------------------------------------------------------

def agenda(page, age):
    """AGENDA, ITEM 1: WHO WINS, ITEM 2: LUNCH, and the two contenders squaring off in stick figures."""
    page_title(page, "AGENDA", "blue", age, y=3, underline_color="red")
    write(page, (6, 16), "ITEM 1: WHO WINS", "black", age - 0.55)
    write(page, (6, 25), "ITEM 2: LUNCH", "black", age - 1.35)
    p = (age - 1.95) / 0.5
    if p > 0:
        stick_figure(page, 28, 53, "black", p, h=15, arms="out", hair="trump")
        stick_figure(page, 62, 53, "black", p, h=15, arms="out", hair="bibi")
        write(page, (page.width // 2, 43), "VS", "red", age - 2.4, fnt=SILK, anchor="ma", bold=True)


def title_page(page):
    page_title(page, "PARDON ME", "red", fnt=PRESS, y=8, underline_color="black")
    write(page, (page.width // 2, 25), "TRUMP vs. BIBI", "blue", fnt=SILK, anchor="ma", bold=True)
    write(page, (page.width // 2, 37), "A RAP BATTLE", "black", fnt=SILK, anchor="ma")
    write(page, (page.width // 2, 45), "AT THE UN", "black", fnt=SILK, anchor="ma")


# --- signs -------------------------------------------------------------------------------------------

@lru_cache(maxsize=64)
def sign2(top, bottom, color="red", fg="white", stand=0):
    """A small two-line printed sign; `stand` adds a post of that height under it."""
    w = max(text_width(top, SILK), text_width(bottom, SILK)) + 8
    s = Canvas(w, 18 + stand)
    s.rect((0, 0, w - 1, 16), color)
    s.line([(1, 1), (w - 2, 1)], mix(C[color] if isinstance(color, str) else color, (255, 255, 255), 0.3))
    write(s.img, (w // 2, 3), top, fg, fnt=SILK, anchor="ma")
    write(s.img, (w // 2, 10), bottom, fg, fnt=SILK, anchor="ma")
    if stand:
        s.rect((w // 2 - 1, 17, w // 2, 16 + stand), "steel_sh")
        s.rect((w // 2 - 4, 16 + stand, w // 2 + 3, 17 + stand), "steel_sh")
    return s.done()


# --- screen cards ------------------------------------------------------------------------------------

def _box(box):
    x0, y0, x1, y1 = box
    return x0, y0, x1 - x0, y1 - y0


def static(img, box, seed):
    """A frame of TV static: the cut between two feeds."""
    x0, y0, w, h = _box(box)
    px = img.load()
    for y in range(y0, y0 + h):
        band = rnd("band", seed, y // 3) * 60
        for x in range(x0, x0 + w):
            v = int(rnd("st", seed, x, y) * 180 + band)
            px[x, y] = (v, v, min(255, v + 20))


def un_card(c, img, box, lines=("GENERAL", "ASSEMBLY"), band="81ST SESSION", mirror=False):
    """The General Assembly's title card in UN blue: the emblem, the title and the session."""
    x0, y0, w, h = _box(box)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=UN_BLUE)
    for k in range(0, h, 4):                                  # a soft sheen down the card
        d.line([(x0, y0 + k), (x0 + w - 1, y0 + k)], fill=mix(UN_BLUE, C["un"], 0.25))
    ex = x0 + (w - 16 if mirror else 16)
    hall.emblem(img, ex, y0 + 19, 12, fg=C["white"], bg=UN_DEEP)
    tx = x0 + (29 if mirror else w - 29)
    for i, s in enumerate(lines):
        write(img, (tx, y0 + 7 + 10 * i), s, C["white"], fnt=SILK, anchor="ma", bold=i == 1)
    d.rectangle((x0, y0 + h - 12, x0 + w - 1, y0 + h - 1), fill=UN_DEEP)
    d.line([(x0, y0 + h - 12), (x0 + w - 1, y0 + h - 12)], fill=C["un_hi"])
    write(img, (x0 + w // 2, y0 + h - 9), band, C["white"], fnt=SILK, anchor="ma")


@lru_cache(maxsize=64)
def mug(who, facing=1, w=30, h=28, top=1, **pose):
    """A character's head and shoulders, cropped from the hair's top: for photos and mugshots."""
    spr, a = figure(who, facing, **pose)
    hx = a["head"][0] + 3 * facing
    y0 = a["top"][1] - top
    x0 = int(hx - w / 2)
    return spr.crop((x0, y0, x0 + w, y0 + h))


def rap_sheet(img, box, who, count, age):
    """A RAP SHEET card: the file photo, the name, the count in a red band. Types in from `age` 0."""
    x0, y0, w, h = _box(box)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=(22, 26, 44))
    d.rectangle((x0, y0, x0 + w - 1, y0 + 9), fill=C["red_sh"])
    write(img, (x0 + w // 2, y0 + 2), "RAP SHEET", C["white"], fnt=SILK, anchor="ma", bold=True)
    facing = 1 if who == "trump" else -1
    pose = {"brows": "angry", "mouth": "frown"} if who == "trump" else {"brows": "angry", "eyes": "half"}
    photo = mug(who, facing, 29, 28, **pose)
    px, py = x0 + 3, y0 + 11
    d.rectangle((px - 1, py - 1, px + photo.width, py + photo.height), fill=C["white"])
    d.rectangle((px, py, px + photo.width - 1, py + photo.height - 1), fill=(150, 160, 178))
    for k in range(py + 3, py + photo.height, 5):            # the height chart behind the photo
        d.line([(px, k), (px + photo.width - 1, k)], fill=(176, 184, 200))
    img.paste(photo, (px, py), photo)
    name, country = ("TRUMP", "USA") if who == "trump" else ("BIBI", "ISRAEL")
    rx = x0 + 37
    if age >= 0:
        write(img, (rx, y0 + 14), name, C["white"], age=age, cps=30, fnt=SILK, bold=True)
        write(img, (rx, y0 + 24), country, C["dim"], age=age - 0.2, cps=30, fnt=SILK)
    if age >= 0.35:
        k = min(1.0, (age - 0.35) / 0.12)
        bw = int(w * k)
        d.rectangle((x0, y0 + h - 11, x0 + bw - 1, y0 + h - 1), fill=C["red"])
        if k >= 1:
            write(img, (x0 + w // 2, y0 + h - 8), count, C["white"], fnt=SILK, anchor="ma", bold=True)


def posed_mug(c, who, facing, w, h, top=1):
    """mug() of `who` as posed this frame (so the expression keeps acting)."""
    s = c.st[who]
    pose = {k: s[k] for k in V.POSE}
    pose.update(bob=0, lean=0, body="stand")
    return mug(who, facing, w, h, top, **pose)


def mugshot(c, img, box, who, number, flash_t=None):
    """A mugshot board: the face as it is posed now against a height chart, holding a name board."""
    x0, y0, w, h = _box(box)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=(196, 202, 214))
    for k in range(2, h, 6):                                  # the height chart
        y = y0 + h - 1 - k
        d.line([(x0, y), (x0 + w - 1, y)], fill=(150, 156, 172))
        if (k - 2) % 12 == 6:
            mark = f"{5 + (k - 2) // 12}'"
            write(img, (x0 + 2, y - 6), mark, (110, 116, 134), fnt=SILK)
            write(img, (x0 + w - 2, y - 6), mark, (110, 116, 134), fnt=SILK, anchor="ra")
    facing = 1 if box[0] < 160 else -1
    face = posed_mug(c, who, facing, 40, 44)
    img.paste(face, (x0 + (w - face.width) // 2, y0 + 3), face)
    bw, bh = text_width(number, SILK) + 8, 11                # the name board at the chest
    bx, by = x0 + (w - bw) // 2, y0 + h - bh - 2
    d.rectangle((bx - 1, by - 1, bx + bw, by + bh), fill=INK)
    d.rectangle((bx, by, bx + bw - 1, by + bh - 1), fill=(30, 30, 38))
    write(img, (bx + bw // 2, by + 3), number, C["white"], fnt=SILK, anchor="ma")
    if flash_t is not None and 0 <= c.t - flash_t < 0.12:     # the camera flash
        d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=(250, 250, 250))


@lru_cache(maxsize=64)
def due_card():
    """A library book's DATE DUE card, every date long gone."""
    w, h = 74, 54
    s = Canvas(w + 2, h + 2)
    s.rect((1, 1, w, h), (244, 234, 200))
    s.rect((1, 1, w, 10), (226, 210, 166))
    write(s.img, (w // 2 + 1, 3), "DATE DUE", INK, fnt=SILK, anchor="ma", bold=True)
    for k in range(4):
        y = 13 + 10 * k
        s.line([(2, y + 8), (w - 1, y + 8)], (196, 180, 150))
        write(s.img, (8, y + 1), ("MAY 2020", "MAY 2022", "MAY 2024", "MAY 2026")[k], (168, 140, 196), fnt=SILK)
    s.line([(w // 2 - 2, 11), (w // 2 - 2, h)], (214, 120, 120))
    return s.done()


# --- the voting board ----------------------------------------------------------------------------------

VOTE = {"yes": (60, 210, 90), "no": (226, 56, 52), "abstain": (246, 200, 70), "off": (52, 58, 78)}
NAMES = (120, 130, 160)


def board(img, box, head, color=(26, 34, 70)):
    """The GA's electronic voting board: a dark panel under a header of one or two lines.
    Returns the panel's (x0, y0, w, h) under the header."""
    x0, y0, w, h = _box(box)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=(12, 16, 32))
    hh = 3 + 7 * len(head)
    d.rectangle((x0, y0, x0 + w - 1, y0 + hh - 1), fill=color)
    d.line([(x0, y0 + hh - 1), (x0 + w - 1, y0 + hh - 1)], fill=mix(color, (255, 255, 255), 0.3))
    for i, line in enumerate(head):
        write(img, (x0 + w // 2, y0 + 2 + 7 * i), line, C["white"], fnt=SILK, anchor="ma", bold=i == len(head) - 1)
    return x0, y0 + hh + 1, w, h - hh - 1


def lamps(img, panel, rows, color_of, label=None, gap=4):
    """Rows of member states, four to a row: a lamp and a blurred name each. `color_of(i)` is the lamp's
    colour; `label` = (i, text) prints one name for real (give it gap=6 to clear the row under it)."""
    x0, y0, w, _ = panel
    d = ImageDraw.Draw(img)
    cw = (w - 4) // 4
    for row in range(rows):
        for col in range(4):
            i = row * 4 + col
            x, y = x0 + 3 + col * cw, y0 + 1 + row * gap
            if label and i == label[0] + 1:
                continue                                       # the real name runs on over this one
            d.rectangle((x, y, x + 1, y + 1), fill=color_of(i))
            if label and i == label[0]:
                write(img, (x + 4, y - 2), label[1], C["white"], fnt=SILK)
            else:
                d.line([(x + 4, y + 1), (x + 9 + round(rnd("nm", i) * 8), y + 1)], fill=NAMES)


def voting_board(c, img, box, t0, t1, seed):
    """VOTING: every member's lamp flickers on between t0 and t1, yes, no or abstain."""
    title = "VOTING" + "." * (int(c.t * 4) % 4)
    panel = board(img, box, (title,))

    def color_of(i):
        on = t0 + rnd("on", seed, i) * (t1 - t0)
        if c.t < on or (c.t - on < 0.15 and int((c.t - on) * 30) % 2):
            return VOTE["off"]
        r = rnd("vote", seed, i)
        return VOTE["yes" if r < 0.4 else "no" if r < 0.8 else "abstain"]
    lamps(img, panel, 9, color_of)


def result_board(img, box, who, yes, no, lit=1.0, blink=False):
    """PARDON <WHO>?: one green lamp, the man's own vote, named; the rest red as they come in (`lit` of
    them); the totals."""
    x0, _, w, _ = panel = board(img, box, ("PARDON", who + "?"), color=(96, 24, 34))

    def color_of(i):
        if i == 0:
            return (200, 255, 210) if blink else VOTE["yes"]
        return VOTE["no"] if rnd("lit", who, i) < lit else VOTE["off"]
    lamps(img, panel, 2, color_of, label=(0, who), gap=6)
    y = panel[1] + 11
    write(img, (x0 + w // 2, y), f"YES {yes}", VOTE["yes"], fnt=PRESS, anchor="ma")
    write(img, (x0 + w // 2, y + 10), f"NO {no}", VOTE["no"], fnt=PRESS, anchor="ma")


def turkey_board(c, img, box, t0):
    """PARDON TURKEYS?: every lamp goes green in a sweep from t0, YES 193, and UNANIMOUS flashing."""
    x0, _, w, _ = panel = board(img, box, ("PARDON", "TURKEYS?"), color=(24, 110, 52))
    lamps(img, panel, 2, lambda i: VOTE["yes"] if c.t - t0 > 0.03 * i else VOTE["off"], gap=6)
    y = panel[1] + 11
    n = min(193, int(193 * (c.t - t0) / 0.3))
    write(img, (x0 + w // 2, y), f"YES {n}", VOTE["yes"], fnt=PRESS, anchor="ma")
    if c.t - t0 > 0.3:
        col = C["gold"] if int((c.t - t0) * 6) % 2 else C["white"]
        write(img, (x0 + w // 2, y + 11), "UNANIMOUS", col, fnt=SILK, anchor="ma", bold=True)


def notice(img, box, lines, color=UN_BLUE, fg=C["white"], arrow=None):
    """A plain UN notice on a screen: white text on blue, and an optional arrow under it ("l": this way,
    to the left)."""
    x0, y0, w, h = _box(box)
    d = ImageDraw.Draw(img)
    d.rectangle((x0, y0, x0 + w - 1, y0 + h - 1), fill=color)
    n = len(lines)
    top = y0 + (h - 10 * n - (10 if arrow else 0)) // 2 + 1
    cx = x0 + w // 2
    for i, s in enumerate(lines):
        write(img, (cx, top + 10 * i), s, fg, fnt=SILK, anchor="ma", bold=True)
    if arrow == "l":
        y = top + 10 * n + 4
        d.line([(cx + 14, y), (cx - 10, y)], fill=fg, width=3)
        d.polygon([(cx - 16, y), (cx - 9, y - 6), (cx - 9, y + 6)], fill=fg)


@lru_cache(maxsize=8)
def cardboard(lines):
    """A scrap of cardboard with a hand-lettered plea, held up in both hands."""
    w = max(text_width(s, SILK) for s in lines) + 7
    h = 5 + 7 * len(lines)
    s = Canvas(w + 2, h + 2)
    s.rect((1, 1, w, h), (206, 166, 112))
    s.line([(2, h), (w - 1, h)], (176, 134, 84))
    s.img.putpixel((w, 1), (0, 0, 0, 0))                       # a torn corner
    for i, txt in enumerate(lines):
        write(s.img, (w // 2 + 1, 3 + 7 * i), txt, INK, fnt=SILK, anchor="ma", bold=True)
    return s.done()


# --- the flip chart, knocked over --------------------------------------------------------------------

@lru_cache(maxsize=1)
def easel():
    """The flip chart on its easel, cover sheet up, as one sprite to knock over. Returns (sprite, x, y),
    its top-left in the world."""
    world = Image.new("RGBA", (hall.W, hall.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(world)
    x0, y0, _, y1 = hall.CHART
    d.line([(67, y1), (67, 168)], fill=INK, width=3)          # the back leg (also painted in the backdrop)
    d.line([(67, y1), (67, 168)], fill=C["desk_sh"])
    page = new_page(hall.CHART_W, hall.CHART_H)
    V.default_page(SimpleNamespace(floor="bibi"), page)
    world.paste(page, (x0, y0))
    d.rectangle((x0 - 1, y0, x0 + page.width, y0 + page.height), outline=INK)
    hall.easel_front(world)
    box = world.getbbox()
    return world.crop(box), box[0], box[1]


# --- the exit escalator ------------------------------------------------------------------------------

ESC = {"land": 28, "run": 92, "foot": 16, "rise": 64, "rail": 24, "n": 12}
ESC_W = ESC["land"] + ESC["run"] + ESC["foot"]
ESC_TOP = ESC["rail"] + 6                                     # tread levels in the sprite: the top landing
ESC_FOOT = ESC_TOP + ESC["rise"]                              # and the foot
ESC_X, ESC_Y = 0, V.SPOTS["rostrum"][1] - ESC_FOOT            # its top-left in the world: the foot on the floor


def tread(u, phase=0.0):
    """Tread height under sprite column u; `phase` 0..1 moves the steps up the incline by a fraction."""
    land, run, n = ESC["land"], ESC["run"], ESC["n"]
    if u < land:
        return ESC_TOP
    if u >= land + run:
        return ESC_FOOT
    sx, sy = run / n, ESC["rise"] / n
    k = math.floor((u - land) / sx + phase)
    return min(ESC_FOOT, max(ESC_TOP, round(ESC_TOP + (k - phase) * sy)))


def rail_y(u):
    """The handrail's height over sprite column u."""
    land, run = ESC["land"], ESC["run"]
    p = min(1.0, max(0.0, (u - land) / run))
    return ESC_TOP - ESC["rail"] + p * ESC["rise"]


@lru_cache(maxsize=16)
def escalator(phase=0):
    """The UN's exit escalator in side view at the cast's scale, rising to the left off the frame: a top
    landing, the incline and a foot landing on the floor, steel steps over the truss, a glass balustrade,
    the black handrail. `phase` (0-7) moves the steps up an eighth of a step at a time, when it runs."""
    land, run, rise = ESC["land"], ESC["run"], ESC["rise"]
    w, h = ESC_W, ESC_FOOT + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    glass = [(0, rail_y(0))] + [(u, rail_y(u)) for u in (land, land + run)] + [(w - 3, rail_y(w))]
    glass += [(w - 3, ESC_FOOT), (land + run, ESC_FOOT), (land, ESC_TOP), (0, ESC_TOP)]
    d.polygon(glass, fill=(160, 214, 240, 150))
    for k in (0.3, 0.62):                                      # a glint on the glass
        u = land + run * k
        d.line([(u, rail_y(u) + 5), (u + 9, rail_y(u + 9) + 15)], fill=(236, 246, 252, 200))
    for u in range(w):
        y = tread(u, phase / 8)
        line = ESC_TOP + min(1.0, max(0.0, (u - land) / run)) * rise
        d.line([(u, y), (u, line + 1)], fill=C["steel"] + (255,))          # the step
        d.line([(u, line + 2), (u, line + 7)], fill=C["steel_sh"] + (255,))  # the truss under it
        d.point((u, y), fill=(236, 238, 246, 255))                          # the tread's edge
    rail = [(0, rail_y(0)), (land, rail_y(land)), (land + run, rail_y(land + run)), (w - 4, rail_y(w))]
    d.line(rail, fill=INK + (255,), width=4)
    d.line(rail, fill=(52, 52, 62, 255), width=2)
    d.arc((w - 8, rail_y(w) - 1, w - 1, rail_y(w) + 6), 270, 90, fill=INK + (255,), width=3)
    return outlined(img, INK)


@lru_cache(maxsize=1)
def escalator_rail():
    """The near handrail alone, to draw over whoever is on the escalator."""
    land, run = ESC["land"], ESC["run"]
    img = Image.new("RGBA", (ESC_W, ESC_FOOT + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rail = [(0, rail_y(0)), (land, rail_y(land)), (land + run, rail_y(land + run)), (ESC_W - 4, rail_y(ESC_W))]
    d.line(rail, fill=INK + (255,), width=4)
    d.line(rail, fill=(52, 52, 62, 255), width=2)
    return img


def feet_on_escalator(x, phase=0.0):
    """World y for feet at world x on the escalator (or the floor beyond its foot)."""
    return ESC_Y + tread(x - ESC_X, phase)


# --- the sprite sheet ------------------------------------------------------------------------------------

if __name__ == "__main__":
    from engine import ROOT
    items = [lawyer(0, v) for v in range(4)] + [lawyer(1, v) for v in range(4)]
    items += [poster_bundle(), placard(("PARDON", "ME?")), placard(("PARDON", "YOU!")),
              sign2("OUT OF", "ORDER"), cardboard(("PARDON", "ME?")), escalator(), easel()[0]]
    sheet = Image.new("RGB", (sum(i.width + 6 for i in items) + 6, 110), (196, 150, 70))
    x = 6
    for i in items:
        sheet.paste(i, (x, 104 - i.height), i)
        x += i.width + 6
    out = ROOT / "build" / "art_ends.png"
    sheet.resize((sheet.width * 5, sheet.height * 5), Image.NEAREST).save(out)
    print(out)
