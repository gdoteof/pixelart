"""Verse 2 gags: Bibi has the rostrum and the flip chart, Trump heckles from the delegation desk (lines v2 0-13).

The chart carries the diagrams (the plan, the bomb, the letter, the islands, the lies, the redacted button, the
paint chip); the screens carry the clips and the close-ups (the escalator, the drive-thru, the lower thirds, the
spit-take, the turkeys); the desk and the wall carry the props. The desk is drawn here (c.desk = False) so props
can sit between Trump and it, and so the machines that walk out in line 5 stay gone. A chart page stays up until
the next page flips over it, so each payoff stays readable after its word.
"""
import art
import art_v2 as A
from gagkit import (
    INK,
    PRESS,
    PW,
    SILK,
    TL,
    C,
    Image,
    ImageDraw,
    V,
    anchor,
    arc_pt,
    back_out,
    blend,
    bubble,
    check,
    clamp,
    col,
    cross_out,
    dither,
    ease_in,
    ease_in_out,
    ease_out,
    face,
    flip,
    gag,
    hall,
    line_t,
    lru_cache,
    marker_arrow,
    mask,
    math,
    mix,
    np,
    paste_rot,
    pixel,
    pose,
    ramp,
    ring,
    rnd,
    scaled,
    span,
    sparkle,
    stroke,
    text_width,
    wobble,
    write,
    wt,
)


def pixel_text(img, xy, s, color, fnt=SILK):
    """Screen text with a hard shadow, like the live feed's."""
    pixel.text(img, xy, s, fnt, color, shadow=(0, 0, 0))

SEC_END = TL.section_end("v2")


def lt(idx, pat=None, n=0):
    """Start of a v2 line, or of a word in it."""
    return line_t("v2", idx, pat, n)


def win(idx):
    """When line idx's gag takes over (the runner starts a gag 0.12 s before its line)."""
    return lt(idx) - 0.12


# --- 0. "You had concepts of a plan. I brought a diagram. Look here:" ----------------------------------------

def _scribble():
    """A hopeless tangle: big loops wandering about the middle of the page, never closing on anything."""
    pts, a = [], 0.0
    cx, cy = 34.0, 37.0
    for k in range(90):
        a += 0.7 + 0.5 * rnd("scrib", k)
        cx = clamp(cx + (rnd("scr-x", k // 6) - 0.5) * 3, 24, 46)
        cy = clamp(cy + (rnd("scr-y", k // 6) - 0.5) * 2, 31, 41)
        r = 6 + 8 * rnd("scr-r", k // 3)
        pts.append((clamp(cx + r * math.cos(a), 10, 62), clamp(cy + r * 0.75 * math.sin(a), 21, 53)))
    return pts


SCRIBBLE = _scribble()
PLAN_T = win(0)                             # the concepts page goes up as the line starts
DIAGRAM_T = lt(0, "diagram") - 0.08         # the neat page flips over it


def concepts_page(pg, t):
    t0 = PLAN_T + 0.1
    write(pg, (PW // 2, 4), "CONCEPTS", "black", t - t0, cps=30, anchor="ma", bold=True)
    write(pg, (PW // 2, 12), "OF A PLAN", "black", t - t0 - 8 / 30, cps=30, anchor="ma", bold=True)
    ts = lt(0, "concepts")
    stroke(pg, SCRIBBLE, "orange", (t - ts) / (lt(0, "plan") - ts))
    tl = lt(0, "plan")
    marker_arrow(pg, (66, 44), (55, 40), "red", (t - tl) / 0.12)
    write(pg, (74, 44), "TRUMP", "red", t - tl - 0.08, cps=40, anchor="ma")


def diagram_head(pg, t):
    age = t - DIAGRAM_T - 0.06
    box = write(pg, (PW // 2, 3), "DIAGRAM", "blue", age, cps=40, anchor="ma", bold=True)
    for y in (11, 13):                                            # ruled with a ruler, not a scribble
        stroke(pg, [(box[0] - 4, y), (box[2] + 4, y)], "blue", (age - 0.18) / 0.12)


@gag("v2", 0)
def concepts_of_a_plan(c, L):
    """Trump's plan is an orange scribble; Bibi's diagram gets a ruled heading, and he points at it."""
    flip(c, PLAN_T)
    flip(c, DIAGRAM_T)
    if c.t >= wt(L, "look"):
        pose(c, "bibi", facing=-1, arm="point")
    yield "chart"
    if c.t < DIAGRAM_T:
        concepts_page(c.page, c.t)
    else:
        diagram_head(c.page, c.t)


# --- 1. "Here's the bomb, here's the fuse, and here's your brain. It's crystal clear." --------------------------

BOMB = (24, 37, 14)                         # centre and radius on the page
HEAD = (72, 32, 7)                          # Trump's head, and the brain in it


def filled_bomb(pg, cx, cy, r, p):
    """The famous cartoon bomb, coloured in with marker: outline, fill (top down), cap, fuse."""
    stroke(pg, [(cx + r * math.cos(a / 24 * 2 * math.pi), cy + r * math.sin(a / 24 * 2 * math.pi))
                for a in range(25)], "black", p / 0.3)
    d = ImageDraw.Draw(pg)
    q = clamp((p - 0.3) / 0.45, 0, 1)
    for y in range(cy - r, cy - r + round(2 * r * q) + 1):
        hw = math.sqrt(max(0.0, r * r - (y - cy) ** 2))
        d.line([(cx - hw, y), (cx + hw, y)], fill=C["mk_black"])
    if q >= 1:
        d.arc((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), 200, 250, fill=C["white"])
    if p > 0.75:
        k = cx + r * 0.62, cy - r * 0.78                                   # the cap, up and to the right
        d.polygon([(k[0] - 3, k[1] - 1), (k[0] + 1, k[1] - 5), (k[0] + 5, k[1] - 1), (k[0] + 1, k[1] + 3)],
                  fill=C["mk_black"])
        f0 = (k[0] + 2, k[1] - 4)
        stroke(pg, [f0, (f0[0] + 1, f0[1] - 3), (f0[0] + 4, f0[1] - 4), (f0[0] + 5, f0[1] - 7)], "black",
               (p - 0.8) / 0.2)


def fuse_tip():
    cx, cy, r = BOMB
    return cx + r * 0.62 + 7, cy - r * 0.78 - 11


def bomb_page(pg, t):
    diagram_head(pg, t)
    cx, cy, r = BOMB
    t_bomb, t_fuse, t_brain = lt(1, "bomb"), lt(1, "fuse"), lt(1, "brain")
    filled_bomb(pg, cx, cy, r, (t - lt(1) + 0.04) / (t_bomb - lt(1) + 0.1))
    write(pg, (cx, cy - 2), "BOMB", "white", t - t_bomb, cps=30, anchor="ma", bold=True)
    fx, fy = fuse_tip()
    marker_arrow(pg, (fx + 9, fy + 1), (fx + 2, fy + 1), "black", (t - t_fuse + 0.1) / 0.12)
    write(pg, (fx + 11, fy - 2), "FUSE", "black", t - t_fuse, cps=30)
    hx, hy, hr = HEAD                                                    # here's your brain: a head, and a dot in it
    th = lt(1, "here", 2) - 0.04
    ring(pg, hx, hy, hr, hr + 1, "black", (t - th) / 0.16)
    if t >= th + 0.16:
        stroke(pg, [(hx - hr - 1, hy - 2), (hx - 3, hy - hr - 3), (hx + hr + 2, hy - hr), (hx + hr + 4, hy - 3)],
               "orange", (t - th - 0.16) / 0.1, width=2)
    tb = t_brain - 0.04
    if t >= tb:
        pg.putpixel((hx + 1, hy + 1), C["mk_black"])
    marker_arrow(pg, (hx - 9, hy + 16), (hx - 1, hy + 4), "blue", (t - tb) / 0.1)
    write(pg, (60, hy + 18), "YOUR BRAIN", "blue", t - tb - 0.06, cps=60, anchor="ma")
    tr = lt(1, "crystal") - 0.04
    stroke(pg, [(cx - r - 6, cy - 7), (cx + r + 6, cy - 7)], "red", (t - tr) / (lt(1, "clear") - tr + 0.04),
           width=2)


@gag("v2", 1)
def bomb_fuse_brain(c, L):
    """The famous cartoon bomb, labelled word by word; Trump's brain is the dot. The red line on "crystal clear"."""
    flip(c, DIAGRAM_T)
    heres = [wt(L, "here", k) for k in range(3)]
    if c.t < wt(L, "it's"):
        near = any(0 <= c.t - h < 0.35 for h in heres)
        pose(c, "bibi", facing=-1, arm="point" if near or c.t < heres[0] else "palm")
    else:
        pose(c, "bibi", facing=1, arm="up")
    yield "chart"
    bomb_page(c.page, c.t)


# --- 2. "I wrote that Nobel letter as a joke. You hung it in the hall." --------------------------------------------

LETTER_T = lt(2, "nobel") - 0.1
LETTER = ("DEAR NOBEL,", "GIVE DONALD", "THE PRIZE.")
HUNG_T = lt(2, "hung")


def letter_page(pg, t):
    age = t - LETTER_T - 0.05
    used = 0.0
    for i, s in enumerate(LETTER):
        write(pg, (6, 4 + 8 * i), s, "black", age - used, cps=60)
        used += len(s) / 60
    write(pg, (52, 29), "- BIBI", "blue", age - used, cps=60)
    tj = lt(2, "joke") - 0.25
    write(pg, (6, 42), "P.S.", "red", t - tj, cps=30)
    write(pg, (28, 40), "LOL JK", "red", t - tj - 0.12, cps=26, fnt=PRESS)


@gag("v2", 2)
def nobel_letter(c, L):
    """The bomb page stays up until "Nobel"; then the letter, with its P.S. on "joke"."""
    flip(c, DIAGRAM_T)
    flip(c, LETTER_T)
    yield "chart"
    if c.t < LETTER_T:
        bomb_page(c.page, c.t)
    else:
        letter_page(c.page, c.t)


@span(HUNG_T - 0.05, SEC_END)
def framed_over_the_emblem(c, L):
    """Trump hangs the letter in the hall, over the UN emblem, for the rest of the verse."""
    yield "back"
    age = c.t - HUNG_T
    spr = A.framed_letter()
    drop = 1 - back_out(clamp(age / 0.22, 0, 1))
    x = 160 - spr.width // 2 + wobble(age - 0.2, amp=2, freq=22, decay=0.6)
    y = 1 - round(drop * 48)
    d = ImageDraw.Draw(c.world)
    d.line([(160, y - 3), (x + 12, y + 3)], fill=INK)                       # the wire, from a nail
    d.line([(160, y - 3), (x + spr.width - 13, y + 3)], fill=INK)
    c.world.paste(spr, (x, y), spr)


# --- the desk: props go between Trump and the desk, and the machines can leave ------------------------------

WALKOUT_T = lt(5, "walked")
MIC_AT, LAPTOP_AT = (hall.DESK[0] + 1, hall.DESK_TOP - 12), (hall.DESK[2] - 35, hall.DESK_TOP - 8)


def desk_body(c):
    """The delegation desk as hall.desk draws it, without its machines or the placard."""
    x0, y0, x1, y1 = hall.DESK
    d = ImageDraw.Draw(c.world)
    d.rectangle((x0 - 1, y0 - 1, x1, y1), fill=INK)
    d.rectangle((x0, y0, x1, y0 + 4), fill=C["desk"])
    d.line([(x0, y0), (x1, y0)], fill=C["desk_hi"])
    d.rectangle((x0, y0 + 5, x1, y1), fill=C["desk_sh"])
    d.line([(x0, y0 + 5), (x1, y0 + 5)], fill=INK)
    for x in range(x0 + 14, x1, 26):
        d.line([(x, y0 + 8), (x, y1)], fill=mix(C["desk_sh"], INK, 0.3))


def placard(c):
    spr = hall.placard_sprite(c.placard or V.COUNTRY[c.heckler])
    c.world.paste(spr, (hall.PLACARD[0] - spr.width // 2, hall.PLACARD[1] - spr.height), spr)


def draw_desk(c, mic=True, laptop=True):
    """The whole desk (gags set c.desk = False and call this in "front", after whatever sits behind it)."""
    desk_body(c)
    if mic:
        spr = A.desk_mic()
        c.world.paste(spr, MIC_AT, spr)
    if laptop:
        spr = A.laptop()
        c.world.paste(spr, LAPTOP_AT, spr)
    placard(c)


def bare_desk(c):
    """The desk after the walkout (lines 6-13)."""
    draw_desk(c, mic=False, laptop=False)


def magnifier_on_hand(c, cx, cy, r=10):
    """A magnifying glass over Trump's hand at (cx, cy): the cuff comes up huge, the hand stays tiny."""
    cx, cy = int(cx), int(cy)
    view = A.lens_view(r)
    c.world.paste(view, (cx - r, cy - r), view)
    blend(c.world, mask(lambda d: d.ellipse((cx - r + 2, cy - r + 2, cx - r + 5, cy - r + 5), fill=255)),
          (255, 255, 255), 0.6)
    lens = A.magnifier(r)
    c.world.paste(lens, (cx - r - 2, cy - r - 2), lens)


# --- 3. "Now you've got a secondhand medal for the smallest hands of all." --------------------------------------

MEDAL_T = lt(3, "secondhand")
SNAP_T = TL.hit_of(TL.line("v2", 3))["t"]          # the cheap ribbon gives on the punchline


@gag("v2", 3, post=0.5)
def secondhand_medal(c, L):
    """A thrift-shop medal ($2, used) drops round Trump's neck; he rises to wear it, shows off a hand so small
    it needs a magnifying glass, and the ribbon snaps on the punchline."""
    c.desk = False
    t = c.t
    up = ramp(t, MEDAL_T, MEDAL_T + 0.15) * (1 - ramp(t, SNAP_T + 0.2, SNAP_T + 0.4))
    s = c.st["trump"]
    s["dy"] = -round(10 * ease_out(up))
    if MEDAL_T + 0.15 <= t < SNAP_T:
        face(c, "trump", mouth="grin" if t < wt(L, "smallest") else "smirk", eyes="squint", brows="up")
    hand_t = wt(L, "smallest") - 0.08
    if hand_t <= t < SNAP_T:
        pose(c, "trump", arm="palm")
    flip(c, win(3))
    yield "chart"
    V.default_page(c, c.page)
    yield "front"
    neck = anchor(c, "trump", "head")
    nx, ny = neck[0] - 3, neck[1] + 11
    med = A.neck_medal()
    tag = A.price_tag()
    if t >= MEDAL_T:
        fall = 1 - ease_out(ramp(t, MEDAL_T, MEDAL_T + 0.16))
        gone = ramp(t, SNAP_T, SNAP_T + 0.25) ** 2
        mx = nx - med.width // 2
        my = ny - round(fall * 60) + round(gone * 50)
        sway = wobble(t - MEDAL_T - 0.16, amp=2, freq=18, decay=0.8)
        tx, ty = mx + med.width + 1 + sway, my + 1
        d = ImageDraw.Draw(c.world)
        d.line([(mx + 12, my + 2), (tx + 5, ty + 8)], fill=C["white"])
        c.world.paste(tag, (tx, ty), tag)
        c.world.paste(med, (mx, my), med)
    draw_desk(c)
    if hand_t <= t < SNAP_T:
        hx, hy = anchor(c, "trump", "hand")
        k = ease_out(ramp(t, hand_t, hand_t + 0.12))
        magnifier_on_hand(c, hx - 1, hy - 2 + round((1 - k) * 30))


# --- 4. "Last time you came here, the escalator stopped, the prompter quit." ---------------------------------------
# Trump's screen runs archive footage of his last visit: the escalator stalls under him, then the teleprompter.

STOP_T = lt(4, "stopped")
PROMPTER_T = lt(4, "prompter") - 0.1
QUIT_T = lt(4, "quit")


def archive_tone(clip):
    """Old footage: washed out, warm, with scanlines."""
    a = np.asarray(clip, dtype=np.float32)
    grey = a.mean(axis=2, keepdims=True)
    a = a * 0.45 + grey * 0.55
    a = a * np.array((1.06, 0.98, 0.84), np.float32) + 8
    a[::2] *= 0.9
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def escalator_shot(clip, t):
    w, h = clip.size
    d = ImageDraw.Draw(clip)
    d.rectangle((0, 0, w, h), fill=(200, 196, 186))
    d.rectangle((0, h - 6, w, h), fill=(150, 140, 130))
    for x in range(4, w, 16):                                        # the lobby's tall windows
        d.rectangle((x, 3, x + 9, h - 12), fill=(176, 196, 214))
    esc = art.escalator(64, 24)
    ex, ey = 4, h - esc.height
    clip.paste(esc, (ex, ey), esc)
    foot, top = (ex + 12, ey + esc.height - 4), (ex + 52, ey + esc.height - 28)
    ride = clamp((t - lt(4, "escalator") + 0.3) / 1.25, 0, 1)
    if t >= STOP_T:
        ride = clamp((STOP_T - lt(4, "escalator") + 0.3) / 1.25, 0, 1)
    fx, fy = foot[0] + (top[0] - foot[0]) * ride, foot[1] + (top[1] - foot[1]) * ride
    if 0 < ride and t < STOP_T:                                       # speed ticks while it runs
        for k in range(3):
            o = 4 + k * 4 + int(t * 30) % 4
            d.line([(fx - 6 - o, fy - 10 + o * 0.6), (fx - 4 - o, fy - 11 + o * 0.6)], fill=(250, 250, 250))
    lurch = 0 <= t - STOP_T < 0.22
    tr = A.mini_trump(lurch)
    clip.paste(tr, (int(fx) - 7 + (2 if lurch else 0), int(fy) - 20), tr)
    if t >= STOP_T:
        x, y = int(fx) + 8, int(fy) - 21 - int(t * 8) % 2
        d.rectangle((x - 1, y - 1, x + 2, y + 8), fill=INK)
        d.rectangle((x, y, x + 1, y + 4), fill=C["red"])
        d.rectangle((x, y + 6, x + 1, y + 7), fill=C["red"])


def prompter_shot(clip, t, walk=None):
    """The podium and the teleprompter that gives up on him. `walk` (x offset, leg phase) takes it away."""
    w, h = clip.size
    d = ImageDraw.Draw(clip)
    d.rectangle((0, 0, w, h), fill=(210, 168, 92))
    for x in range(0, w, 8):
        d.line([(x, 0), (x, h)], fill=(190, 148, 76))
    d.rectangle((0, h - 7, w, h), fill=(60, 84, 120))
    tr = A.mini_trump()
    clip.paste(tr, (16, h - 29), tr)
    pod = A.mini_podium()
    clip.paste(pod, (13, h - 17), pod)
    text, color = ("ERROR", "red") if t < QUIT_T else ("I QUIT", "white")
    if t < PROMPTER_T + 0.12:
        text, color = "...GREAT", "white"
    pr = A.teleprompter(text, color)
    px, py = 46, h - pr.height - 4
    if walk is not None:
        dx, phase, lift = walk
        px += int(dx)
        py -= lift
        if lift:
            A.legs(clip, px + pr.width // 2, h - 4, phase, n=2, spread=6, h=lift + 1)
    clip.paste(pr, (px, py), pr)


def archive_feed(c, img, box, walk=None):
    x0, y0, x1, y1 = box
    clip = Image.new("RGB", (x1 - x0, y1 - y0))
    if c.t < PROMPTER_T:
        escalator_shot(clip, c.t)
    else:
        prompter_shot(clip, c.t, walk)
    clip = archive_tone(clip)
    pixel_text(clip, (3, 1), "ARCHIVE 2025", C["gold_hi"])
    if 0 <= c.t - lt(4) < 0.1 or 0 <= c.t - PROMPTER_T < 0.08:      # the cut to old tape
        dither(clip, 0.5, (230, 230, 230))
    jolt = 1 if 0 <= c.t - STOP_T < 0.12 and int(c.t * 48) % 2 else 0
    img.paste(clip, (x0, y0 + jolt))


@gag("v2", 4)
def escalator_archive(c, L):
    """The archive: the escalator stops dead under him (he lurches), then the prompter says ERROR, I QUIT."""
    c.screens["R"] = archive_feed
    yield "back"


# --- 5. "Even the machines at the UN walked out on your bit." -------------------------------------------------------
# The desk's microphone and laptop sprout legs and walk off; on the screen, the teleprompter walks out of the clip.

LEGS_T = lt(5, "machines")
LAPTOP_GO = lt(5, "at")                     # the laptop leaves first, the mic on "walked out"


def legs_out(t):
    """The legs' length as they pop out."""
    return round(5 * back_out(clamp((t - LEGS_T) / 0.14, 0, 1))) if t >= LEGS_T else 0


def walker(c, spr, x, t_go, speed, t, seed):
    """A machine on its new legs, walking off to the right from t_go."""
    lift = legs_out(t)
    gone = max(0.0, t - t_go) * speed
    walking = t >= t_go
    bob = (int(t * 12 + seed) % 2) if walking else 0
    x = x + int(gone)
    y = hall.DESK_TOP - lift - spr.height + 1 - bob
    A.legs(c.world, x + spr.width // 2, hall.DESK_TOP, int(t * 12 + seed) if walking else 0, n=2,
           spread=max(6, spr.width // 2), h=lift + 1)
    c.world.paste(spr, (x, y), spr)


@gag("v2", 5)
def machines_walk_out(c, L):
    """Legs pop out of the mic and the laptop on "machines"; the laptop leaves first (BRB), the mic on
    "walked out"; on the screen the teleprompter walks out of the archive clip."""
    c.desk = False
    t = c.t
    lift = legs_out(t)
    c.screens["R"] = lambda c, img, box: archive_feed(c, img, box, (max(0.0, t - WALKOUT_T) * 90,
                                                                     int(t * 12) if t >= WALKOUT_T else 0, lift))
    if t >= LAPTOP_GO:
        face(c, "trump", eyes="side", brows="worried", mouth="o")
    yield "front"
    desk_body(c)
    if t < LEGS_T:
        for spr, at in ((A.laptop(), LAPTOP_AT), (A.desk_mic(), MIC_AT)):
            c.world.paste(spr, at, spr)
        placard(c)
        return
    placard(c)
    walker(c, A.laptop_front("BRB" if t >= LAPTOP_GO else None), 284, LAPTOP_GO, 55, t, 0)
    walker(c, A.stand_mic(), 216, WALKOUT_T, 150, t, 1)


# --- 6. "You tariffed the McDonald Islands: population, penguins." -------------------------------------------------

ISLAND_T = win(6)
ISLAND = [(22, 31), (27, 25), (37, 23), (47, 21), (58, 23), (67, 28), (68, 33), (60, 37), (48, 38), (34, 38),
          (25, 36), (22, 31)]
PENGUINS = ((44, 33), (52, 32), (60, 33))


def penguin_doodle(pg, x, y, age):
    """A marker penguin, feet at (x, y), popping up."""
    if age < 0:
        return
    h = 10 if age > 0.08 else 6
    d = ImageDraw.Draw(pg)
    d.ellipse((x - 3, y - h, x + 3, y - 1), fill=C["mk_black"])
    d.ellipse((x - 1, y - h + 4, x + 2, y - 2), fill=C["paper"])
    d.point((x + 1, y - h + 2), fill=C["paper"])
    d.line([(x + 3, y - h + 3), (x + 4, y - h + 3)], fill=C["orange"])
    d.line([(x - 2, y), (x - 1, y)], fill=C["orange"])
    d.line([(x + 1, y), (x + 2, y)], fill=C["orange"])


def island_page(pg, t):
    age = t - ISLAND_T - 0.05
    stroke(pg, ISLAND, "black", age / 0.35)
    for i, (x, y) in enumerate(((6, 21), (72, 17), (6, 40), (76, 41), (11, 31), (78, 28))):    # the sea
        stroke(pg, [(x, y), (x + 2, y - 1), (x + 4, y), (x + 6, y - 1)], "blue", (age - 0.2 - 0.04 * i) / 0.1)
    tf = lt(6, "tariffed")
    if t >= tf:                                                          # a pin flag: the tariff
        stroke(pg, [(32, 33), (32, 13)], "black", (t - tf) / 0.08)
        if t >= tf + 0.08:
            d = ImageDraw.Draw(pg)
            d.rectangle((33, 13, 52, 20), fill=C["mk_red"])
            write(pg, (35, 13), "10%", "white", t - tf - 0.1, cps=30)
    write(pg, (PW // 2, 3), "McDONALD IS.", "black", t - lt(6, "mcdonald") + 0.05, cps=26, anchor="ma", bold=True)
    tp = lt(6, "population")
    write(pg, (9, 44), "POP:", "black", t - tp, cps=30, bold=True)
    tq = lt(6, "penguins")
    write(pg, (33, 44), "PENGUINS", "blue", t - tq, cps=36, bold=True)
    for i, (x, y) in enumerate(PENGUINS):
        penguin_doodle(pg, x, y, t - tq + 0.08 - 0.1 * i)


@gag("v2", 6)
def penguin_tariff(c, L):
    """A map of the McDonald Islands: a 10% tariff flag planted, and the population turns out to be penguins."""
    c.desk = False
    flip(c, ISLAND_T)
    yield "chart"
    island_page(c.page, c.t)
    yield "front"
    bare_desk(c)


# --- 7. "You thought it was a drive-thru. Asked a penguin for a Big Mac with onions." -------------------------------
# Trump's screen goes live from the islands: a drive-thru hut with a penguin in a paper hat at the window and
# a menu of fish. Trump orders from his desk; the order comes back down on his head.

DRIVE_T = lt(7, "drive")
MENU_T = DRIVE_T + 0.5
FISH_T = TL.hit_of(TL.line("v2", 7))["t"]


def drive_thru_feed(c, img, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    t = c.t
    clip = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(clip)
    d.rectangle((0, 0, w, h), fill=(150, 196, 236))                  # polar sky, ice
    d.rectangle((0, h - 10, w, h), fill=(236, 244, 250))
    d.line([(0, h - 10), (w, h - 10)], fill=(200, 220, 236))
    on = t >= DRIVE_T and (t - DRIVE_T > 0.4 or int(t * 10) % 2 == 0)
    booth = A.drive_thru_booth(on)
    bx, by = 3, h - booth.height + 2
    clip.paste(booth, (bx, by), booth)
    lean = 2 if t >= lt(7, "penguin") else 0
    flap = (t >= DRIVE_T and int(t * 4) % 2 == 0 and t < MENU_T + 0.6) or lean > 0
    peng = A.penguin(cap=True, flap=flap)
    clip.paste(peng, (bx + 8 + lean, by + 18), peng)
    d.rectangle((bx + 7, by + 34, bx + 23, by + 36), fill=C["steel"])            # the counter, over its feet
    d.line([(bx + 7, by + 37), (bx + 23, by + 37)], fill=INK)
    if t >= MENU_T:
        menu = A.menu_board()
        k = ease_out(ramp(t, MENU_T, MENU_T + 0.2))
        clip.paste(menu, (w - menu.width - 3, h - menu.height - 1 + int((1 - k) * 40)), menu)
    pixel_text(clip, (w - 22, 1), "LIVE", C["white"])
    img.paste(clip, (x0, y0))


@gag("v2", 7, post=0.55)
def drive_thru(c, L):
    """On "drive-thru" the screen's hut lights up; the menu board says FISH, ONLY FISH; Trump orders a BIG MAC
    + ONIONS from his desk anyway, and on the punchline a fish lands on his head."""
    c.desk = False
    flip(c, ISLAND_T)
    t = c.t
    if t < L.ln["t1"] + 0.6:
        c.screens["R"] = drive_thru_feed
    ask = lt(7, "asked")
    if ask <= t < FISH_T:
        pose(c, "trump", arm="up")
        face(c, "trump", mouth="open" if int(t * 8) % 2 else "pout", brows="up")
    yield "chart"
    if t < win(8):
        island_page(c.page, t)
    yield "front"
    bare_desk(c)
    if lt(7, "big") - 0.05 <= t < FISH_T + 0.3:
        hx, hy = anchor(c, "trump", "mouth")
        lines = ["1 BIG MAC"] + (["+ ONIONS"] if t >= lt(7, "onions") - 0.05 else [])
        bubble(c.world, 226, 96, lines, tail=(hx - 4, hy - 3), fnt=SILK, pad=3, anchor="mb", line_h=8, text_dy=-2)
    if t >= FISH_T - 0.25:
        top = anchor(c, "trump", "top")
        land = (top[0] + 1, top[1] + 1)
        p = clamp((t - FISH_T + 0.25) / 0.25, 0, 1)
        if p < 1:
            x, y = arc_pt(p, (238, 40), land, 18)
            paste_rot(c.world, A.fish(), x, y, -360 * p)
        else:
            slide = ease_in(ramp(t, FISH_T + 0.45, FISH_T + 0.75))
            x, y = land[0] + int(slide * 14), land[1] + int(slide * 40) + wobble(t - FISH_T, amp=1, freq=40)
            fish = A.fish(-20 if slide else 0)
            c.world.paste(fish, (int(x) - fish.width // 2, int(y) - fish.height + 2), fish)


# --- 8. "They call me Mr. Security. Donald, you're Mr. Insecurity:" ------------------------------------------------
# Lower thirds on both close-ups: shades drop onto Bibi ("deal with it"), Trump checks his hair in a hand mirror.

SEC_T = lt(8, "security")
MIRROR_T = lt(8, "donald")
FEED_EYE = (42, 19)                         # the near eye on either close-up, in screen coordinates
FEED_MOUTH = (38, 37)                       # Trump's mouth on his close-up


def feed_clip(c, box, who, facing):
    """A live feed drawn into its own screen-sized image, so a gag can draw on it without spilling over."""
    x0, y0, x1, y1 = box
    clip = Image.new("RGB", (x1 - x0, y1 - y0))
    V.live_feed(c, clip, (0, 0, x1 - x0, y1 - y0), who, facing)
    return clip


@lru_cache(maxsize=None)
def lower_third_img(text, tab):
    w = text_width(text, SILK) + 10
    img = Image.new("RGBA", (w + 1, 11), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w, 10), fill=INK)
    d.rectangle((1, 1, w - 1, 9), fill=C["white"])
    d.rectangle((1, 1, 3, 9), fill=col(tab))
    d.fontmode = "1"
    d.text((6, -1), text, font=SILK, fill=INK)
    return img


def lower_third(clip, text, tab, age):
    """A news lower third that wipes in from the left over a close-up's name plate."""
    if age < 0:
        return
    plate = lower_third_img(text, tab)
    k = ease_out(clamp(age / 0.15, 0, 1))
    part = plate.crop((0, 0, max(1, int(plate.width * k)), plate.height))
    clip.paste(part, (1, clip.height - 12), part)


def profile_shades(img, eye, facing, k=1, drop=0):
    """Dark glasses seen side-on: a lens over the eye and the arm back to the ear (k scales the pixels)."""
    ex, ey = eye
    ey -= drop
    d = ImageDraw.Draw(img)
    if facing > 0:
        lens = (ex - k, ey - k, ex + 3 * k - 1, ey + 2 * k - 1)
    else:
        lens = (ex - 3 * k + 1, ey - k, ex + k, ey + 2 * k - 1)
    d.rectangle(lens, fill=(14, 12, 18))
    arm_end = ex - 9 * k if facing > 0 else ex + 9 * k
    d.rectangle((min(ex, arm_end), ey - k, max(ex, arm_end), ey - 1), fill=(14, 12, 18))
    glint = (lens[0] + k, lens[1] + k) if facing > 0 else (lens[2] - 2 * k + 1, lens[1] + k)
    d.rectangle((glint[0], glint[1], glint[0] + k - 1, glint[1] + k - 1), fill=(120, 120, 140))


def shade_drop(t):
    """How far above the eye the shades still are (they fall into place on "Security")."""
    return round((1 - ease_out(clamp((t - SEC_T + 0.05) / 0.16, 0, 1))) * 22)


def security_feed(c, img, box):
    clip = feed_clip(c, box, "bibi", 1)
    if c.t >= SEC_T - 0.05:
        profile_shades(clip, FEED_EYE, 1, k=2, drop=2 * shade_drop(c.t))
    lower_third(clip, "MR. SECURITY", "btie_sh", c.t - lt(8, "mr"))
    img.paste(clip, box[:2])


def insecurity_feed(c, img, box):
    clip = feed_clip(c, box, "trump", -1)
    if c.t >= MIRROR_T:
        m = scaled(A.hand_mirror(), 2)
        k = ease_out(clamp((c.t - MIRROR_T) / 0.15, 0, 1))
        clip.paste(m, (3, 8 + round((1 - k) * 40)), m)
    lower_third(clip, "MR. INSECURITY", "tie", c.t - lt(8, "mr", 1))
    img.paste(clip, box[:2])


@gag("v2", 8, post=0.6)
def mister_security(c, L):
    """MR. SECURITY: shades drop onto Bibi (and his close-up) on "Security". MR. INSECURITY: Trump frets at
    his hair in a hand mirror. The lower thirds stay up into the next line, long enough to read."""
    c.desk = False
    flip(c, win(8))
    t = c.t
    c.screens["L"] = security_feed
    c.screens["R"] = insecurity_feed
    if t >= MIRROR_T:
        pose(c, "trump", arm="pinch")
        face(c, "trump", eyes="open", brows="worried", mouth="pout" if int(t * 3) % 2 else "frown")
        c.st["trump"]["sweat"] = t >= lt(8, "insecurity")
    yield "chart"
    if t < win(9):
        V.default_page(c, c.page)
    yield "front"
    bare_desk(c)
    if t >= SEC_T - 0.05:
        profile_shades(c.world, anchor(c, "bibi", "eye"), c.st["bibi"]["facing"], drop=shade_drop(t))
    if t >= MIRROR_T:
        m = A.hand_mirror()
        hx, hy = anchor(c, "trump", "hand")
        c.world.paste(m, (hx - m.width // 2 - 1, hy - m.height + 3), m)


# --- 9. "you lie about your crowds, your height, your hands and your maturity." --------------------------------------

LIES_T = win(9)
LIES = (("CROWDS", "crowds"), ("HEIGHT", "height"), ("HANDS", "hands"), ("MATURITY", "maturity"))
HEIGHT_T = lt(9, "height")


def lies_page(pg, t):
    write(pg, (PW // 2, 3), "HE LIES ABOUT:", "red", t - LIES_T - 0.05, cps=40, anchor="ma", bold=True)
    for i, (label, word) in enumerate(LIES):
        y = 14 + 10 * i
        tw = lt(9, word)
        ta = LIES_T + 0.3 + 0.12 * i
        stroke(pg, [(8, y), (14, y), (14, y + 6), (8, y + 6), (8, y)], "black", (t - ta) / 0.1)
        write(pg, (19, y), label, "black", t - ta - 0.05, cps=50, bold=True)
        check(pg, 9, y + 2, "red", (t - tw + 0.04) / 0.1, width=2, size=7)


def height_board(img, t):
    """A police line-up board behind Trump: the 6'3" he claims is a long way over his head."""
    x0, x1, y0, y1 = 236, 302, 63, 124
    drop = round((1 - ease_out(clamp((t - HEIGHT_T + 0.1) / 0.15, 0, 1))) * 70)
    d = ImageDraw.Draw(img)
    d.rectangle((x0 - 1, y0 - 1 - drop, x1 + 1, y1 - drop), fill=INK)
    d.rectangle((x0, y0 - drop, x1, y1 - drop), fill=(214, 218, 226))
    for k, y in enumerate(range(y0 + 6, y1, 6)):
        d.line([(x0, y - drop), (x0 + (8 if k % 2 else 14), y - drop)], fill=INK)
        d.line([(x1 - (8 if k % 2 else 14), y - drop), (x1, y - drop)], fill=INK)
    mark = y0 + 6 - drop
    d.line([(x0, mark), (x1, mark)], fill=C["mk_red"])
    pixel.outline_text(img, (x0 + 16, mark - 6), "6'3\"", SILK, C["mk_red"], C["white"])
    if t >= HEIGHT_T + 0.25:
        cross_out(img, (x0 + 15, mark - 5, x0 + 36, mark + 3), "red", (t - HEIGHT_T - 0.25) / 0.15, width=2)


@gag("v2", 9)
def lies_checklist(c, L):
    """HE LIES ABOUT: four boxes ticked on their words; on "height" a line-up board drops in behind Trump with
    his 6'3" claim far over his head, crossed out."""
    c.desk = False
    flip(c, LIES_T)
    t = c.t
    if t >= HEIGHT_T:
        face(c, "trump", eyes="side", brows="worried")
    yield "back"
    if t >= HEIGHT_T - 0.1:
        height_board(c.world, t)
    yield "chart"
    lies_page(c.page, t)
    yield "front"
    bare_desk(c)


# --- 10. "The big red button on your desk? It brings a Diet Coke." ---------------------------------------------------
# A game-show button rises out of Trump's desk; he slams it, DING, and a silver tray comes up with a diet soda.

BUTTON_T = lt(10, "big")
SLAM_T = lt(10, "it") + 0.06
TRAY_T = lt(10, "brings") + 0.04
GRAB_T = lt(10, "coke")
BUTTON_X = 248                              # the button's centre: behind the placard, under Trump's chin
TRAY_X = 212                                # the tray's left end: the desk's left corner
HOLD = (-6, -3)                             # where the can's centre sits from Trump's mouth while he sips


def rise(t, t0, depth, dur=0.18):
    """How far below its place something springing up out of the desk still is."""
    return round((1 - back_out(clamp((t - t0) / dur, 0, 1))) * depth)


def ding(img, x, y, age):
    """A bell-ding: gold rays and the word."""
    if not 0 <= age < 0.45:
        return
    d = ImageDraw.Draw(img)
    r0, r1 = 3 + age * 14, 6 + age * 22
    for k in range(8):
        a = k * math.pi / 4
        d.line([(x + r0 * math.cos(a), y + r0 * math.sin(a)), (x + r1 * math.cos(a), y + r1 * math.sin(a))],
               fill=C["gold_hi"])
    pixel.text(img, (x - 30, y - 14 - int(age * 10)), "DING!", SILK, C["gold_hi"], shadow=(0, 0, 0))


def red_button(c, t, sink=0):
    """The button on its stalk, risen out of the desk (drawn before the desk, so the desk hides the stalk)."""
    b = A.red_button(pressed=SLAM_T <= t < SLAM_T + 0.25)
    y = hall.DESK_TOP - 26 + rise(t, BUTTON_T - 0.05, 27) + sink
    c.world.paste(b, (BUTTON_X - b.width // 2, y), b)
    return y


def soda_tray(c, t, can=True, sink=0):
    """The silver tray come up out of the desk's left corner, with the can on it until Trump grabs it."""
    tray = A.silver_tray()
    y = hall.DESK_TOP - 18 + rise(t, TRAY_T, 30, 0.22) + sink
    c.world.paste(tray, (TRAY_X, y), tray)
    if can:
        s = A.soda_can()
        c.world.paste(s, (TRAY_X + 9, y - s.height + 2), s)


def tray_can_feed(c, img, box):
    """Trump's close-up: the diet soda comes up into the shot on "brings", DIET in big letters."""
    clip = feed_clip(c, box, "trump", -1)
    can = A.feed_can()
    y = clip.height - can.height + 2 + rise(c.t, TRAY_T, 40, 0.22)
    clip.paste(can, (4, y), can)
    img.paste(clip, box[:2])


@gag("v2", 10, post=0.4)
def diet_button(c, L):
    """A big red button springs out of Trump's desk on "big"; he eyes it, slams it on "It", DING, and a silver
    tray comes up with a diet soda (DIET on his close-up). He grabs it on "Coke". The LIES page stays up."""
    c.desk = False
    flip(c, LIES_T)
    t = c.t
    after = t >= win(11)                                              # the post window: everything sinks back
    if TRAY_T <= t < win(11):
        c.screens["R"] = tray_can_feed
    if lt(10, "desk") <= t < SLAM_T - 0.3:
        face(c, "trump", eyes="wide", mouth="grin", brows="up")
    elif SLAM_T - 0.3 <= t < SLAM_T:
        pose(c, "trump", arm="fist")
        face(c, "trump", eyes="squint", mouth="grit", brows="angry")
    elif SLAM_T <= t < SLAM_T + 0.2:
        pose(c, "trump", arm="chop")
    elif GRAB_T <= t < win(11):
        pose(c, "trump", arm="fist")
        face(c, "trump", eyes="squint", mouth="grin", brows="up")
    yield "chart"
    if not after:
        lies_page(c.page, t)
    yield "front"
    sink = round(ease_in(ramp(t, win(11), win(11) + 0.3)) * 32)
    if t >= BUTTON_T - 0.05:
        by = red_button(c, t, sink)
    if t >= TRAY_T:
        soda_tray(c, t, can=t < GRAB_T, sink=sink)
    if not after:
        bare_desk(c)
    if t >= BUTTON_T - 0.05 and not after:
        if lt(10, "button") <= t < SLAM_T and int(t * 6) % 2 == 0:
            sparkle(c.world, BUTTON_X - 3, by + 2, 2, C["white"])
        if SLAM_T <= t < SLAM_T + 0.2:
            f = A.slam_fist()
            c.world.paste(f, (BUTTON_X - 5, by - 4), f)
        ding(c.world, BUTTON_X, by + 3, t - SLAM_T)
    if GRAB_T <= t < win(11) + 0.4:                                   # the can hops up to his lips
        mx, my = anchor(c, "trump", "mouth")
        p = clamp((t - GRAB_T) / 0.14, 0, 1)
        x, y = arc_pt(ease_out(p), (TRAY_X + 13, hall.DESK_TOP - 24), (mx + HOLD[0], my + HOLD[1]), 10)
        paste_rot(c.world, A.soda_can(), x, y, -110 * p)


# --- 11. "Mine? I neither confirm nor deny. But it isn't soda, folks." ------------------------------------------------
# Bibi's button is a page of redactions; Trump sips his soda through it and spits it out on the punchline.

MINE_T = win(11)
SPIT_T = TL.hit_of(TL.line("v2", 11))["t"]
BARS = (17, "neither"), (23, "confirm"), (29, "deny")


@lru_cache(maxsize=None)
def silk_stamp(text, color, angle):
    """A rubber stamp in the small font: a ruled box round the word, speckled where the ink missed, tilted."""
    w, h = text_width(text, SILK) + 9, 11
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    ink = tuple(col(color)) + (255,)
    d.rectangle((0, 0, w - 1, h - 1), outline=ink)
    d.text((5, -1), text, font=SILK, fill=ink)
    arr = np.array(im)
    gone = np.random.default_rng(7).random(arr.shape[:2]) < 0.06
    arr[gone, 3] = 0
    return Image.fromarray(arr, "RGBA").rotate(angle, resample=Image.NEAREST, expand=True)


def classified_page(pg, t):
    write(pg, (PW // 2, 3), "MY BUTTON:", "blue", t - lt(11, "mine") + 0.05, cps=40, anchor="ma", bold=True)
    tb = lt(11, "mine") + 0.25
    stroke(pg, [(12, 12), (78, 12), (78, 33), (12, 33), (12, 12)], "black", (t - tb) / 0.25)
    d = ImageDraw.Draw(pg)
    for y, word in BARS:                                              # redacted, line by line
        tw = lt(11, word) - 0.04
        if t >= tw:
            x1 = 16 + int(58 * ease_out(clamp((t - tw) / 0.12, 0, 1)))
            d.rectangle((16, y - 2, x1, y + 1), fill=C["mk_black"])
    ts = lt(11, "deny") + 0.1
    if t >= ts:
        st = silk_stamp("CLASSIFIED", "mk_red", 4)
        dy = round(max(0.0, 1 - (t - ts) / 0.08) * -10)
        pg.paste(st, (PW // 2 - st.width // 2, 35 + dy), st)
    write(pg, (PW // 2, 49), "(NOT SODA)", "blue", t - lt(11, "soda") + 0.06, cps=50, anchor="ma")


def sip_angle(t):
    """The can tipped to his lips, rocking a little as he sips."""
    return -104 - 10 * math.sin(t * 6.0)


def spray(img, x, y, age, k=1, n=36, cola=(84, 46, 24)):
    """A spit-take: a fan of cola and foam flying up and to the left, then falling (k scales pixels and speed)."""
    if not 0 <= age < 0.7:
        return
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = math.pi + math.radians(-6 + 46 * rnd("spit", i))
        v = (50 + 100 * rnd("spit-v", i)) * k
        px = round(x + math.cos(a) * v * age)
        py = round(y - math.sin(a - math.pi) * v * age + 110 * k * age * age)
        tone = cola if i % 2 else (246, 240, 228)
        s = k if i % 3 else 2 * k
        d.rectangle((px, py, px + s - 1, py + s - 1), fill=tone)


def sip_feed(c, img, box):
    """Trump's close-up: the DIET can at his lips, then the spit-take, twice the size."""
    clip = feed_clip(c, box, "trump", -1)
    age = c.t - SPIT_T
    can = A.feed_can()
    if age < 0.3:                                                     # dropped in shock
        clip.paste(can, (4, clip.height - can.height + 2 + round(max(0.0, age) ** 2 * 900)), can)
    mx, my = FEED_MOUTH
    spray(clip, mx - 4, my - 2, age, k=2, n=40, cola=(176, 112, 64))
    img.paste(clip, box[:2])


@gag("v2", 11, post=0.5)
def classified(c, L):
    """MY BUTTON: drawn, then redacted bar by bar on "neither confirm nor deny" and stamped CLASSIFIED, with a
    footnote: (NOT SODA). Trump, sipping his diet soda, does a spit-take on the punchline."""
    c.desk = False
    flip(c, MINE_T)
    t = c.t
    after = t >= win(12)
    c.screens["R"] = sip_feed
    if t < SPIT_T:
        pose(c, "trump", arm="fist")
        face(c, "trump", eyes="half" if t < lt(11, "soda") else "wide", mouth="pout",
             brows="neutral" if t < lt(11, "soda") else "up")
    yield "chart"
    if not after:
        classified_page(c.page, t)
    yield "front"
    mx, my = anchor(c, "trump", "mouth")
    age = t - SPIT_T
    if 0 <= age < 0.3:                                                # he drops it, behind the desk
        paste_rot(c.world, A.soda_can(), mx + HOLD[0], my + HOLD[1] + 4 + 500 * age * age, -20)
    if not after:
        bare_desk(c)
    if age < 0:
        paste_rot(c.world, A.soda_can(), mx + HOLD[0], my + HOLD[1], sip_angle(t))
    spray(c.world, mx - 2, my, age)


# --- 12. "Pardon me like a turkey? Donald, I have seen your tan." -----------------------------------------------------
# On "turkey" Bibi's close-up is a turkey with his hair. Then a paint chip: an eyedropper samples Trump's cheek
# on "seen" and carries the colour over to the last chip on "tan": TRUMP TANGERINE.

TURKEY_T = lt(12, "turkey") - 0.06
CHIP_T = lt(12, "donald") - 0.1
DROP_T = lt(12, "have") - 0.1               # the eyedropper comes down
SEEN_T = lt(12, "seen")
TAN_T = lt(12, "tan")
CHIPS = ((13, 22, C["bskin_hi"], "PEACH"), (23, 32, (232, 176, 128), "TAN"))
LAST_CHIP = (4, 33, 30, 51)                 # the Trump chip, page coordinates


def turkey_feed(c, img, box):
    """Bibi's close-up, except it is a turkey with his hair, gobbling."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    clip = V.feed_backdrop(w, h, True).copy()                         # (it is cached: don't draw on it)
    bird = A.turkey_bust("bibi", int(c.t * 8) % 2 == 0)
    clip.paste(bird, ((w - bird.width) // 2 - 4, 2), bird)
    lower_third(clip, "BIBI", "btie_sh", 1.0)
    if c.t - TURKEY_T < 0.06 or c.t > CHIP_T + 0.32:                  # the cut in and out
        dither(clip, 0.5, (230, 230, 230))
    img.paste(clip, (x0, y0))


def chip_page(pg, t):
    age = t - CHIP_T - 0.05
    write(pg, (PW // 2, 3), "PAINT CHIP", "black", age, cps=40, anchor="ma", bold=True)
    d = ImageDraw.Draw(pg)
    if age >= 0.15:
        d.rectangle((3, 12, 31, 52), outline=C["mk_black"])
        for y0, y1, color, name in CHIPS:
            d.rectangle((4, y0, 30, y1), fill=color)
            write(pg, (35, y0 + 2), name, "black", age - 0.2, cps=40)
        x0, y0, x1, y1 = LAST_CHIP
        d.rectangle((x0, y0, x1, y1), outline=C["paper_sh"])
        write(pg, (35, 40), "?", "black", age - 0.4, cps=40)
    if t >= TAN_T - 0.05:
        x0, y0, x1, y1 = LAST_CHIP
        k = ease_out(clamp((t - TAN_T + 0.05) / 0.12, 0, 1))
        d.rectangle((x0, y0, x1, y0 + int((y1 - y0) * k)), fill=C["tskin"])
        d.rectangle((35, 38, 40, 46), fill=C["paper"])                # the "?" gives way to the name
        write(pg, (35, 36), "TRUMP", "red", t - TAN_T - 0.04, cps=40, bold=True)
        write(pg, (35, 44), "TANGERINE", "red", t - TAN_T - 0.16, cps=40, bold=True)


def pipette(c, t):
    """The eyedropper: comes down on "have", sucks up Trump's cheek on "seen", flies to the chart and fills
    the last chip on "tan", then leaves."""
    if not DROP_T <= t < TAN_T + 0.35:
        return
    ex, ey = anchor(c, "trump", "eye")
    cheek = (ex - 1, ey + 6)
    chip = (hall.CHART[0] + 20, hall.CHART[1] + 40)
    fly0, fly1 = SEEN_T + 0.12, TAN_T - 0.05
    full = SEEN_T + 0.06 <= t < TAN_T
    squeeze = SEEN_T - 0.02 <= t < SEEN_T + 0.06 or TAN_T - 0.05 <= t < TAN_T + 0.05
    if t < SEEN_T - 0.02:                                             # coming down to hover by his cheek
        k = ease_out(clamp((t - DROP_T) / 0.2, 0, 1))
        x, y = cheek[0] - 3, cheek[1] - 6 - (1 - k) * 60
    elif t < fly0:                                                    # in
        x, y = cheek
    elif t < fly1:
        x, y = arc_pt(ease_in_out((t - fly0) / (fly1 - fly0)), cheek, chip, 34)
    elif t < TAN_T + 0.12:
        x, y = chip
    else:                                                             # and away, up off the top
        k = ease_in(clamp((t - TAN_T - 0.12) / 0.2, 0, 1))
        x, y = chip[0] + k * 20, chip[1] - k * 130
    spr = A.eyedropper(C["tskin"] if full else None, squeeze).transpose(Image.FLIP_LEFT_RIGHT)
    c.world.paste(spr, (int(x) - 17, int(y) - 17), spr)


@gag("v2", 12, post=0.35)
def tangerine(c, L):
    """"Pardon me like a turkey?": Bibi's close-up turns into a turkey with his hair. Then a paint chip
    (PEACH, TAN, ?), and an eyedropper samples Trump's cheek for the last one: TRUMP TANGERINE."""
    c.desk = False
    flip(c, MINE_T)
    flip(c, CHIP_T)
    t = c.t
    if TURKEY_T <= t < CHIP_T + 0.4:
        c.screens["L"] = turkey_feed
    if t < lt(12, "donald"):
        pose(c, "bibi", arm="shrug", far="out")
    elif t < TAN_T + 0.3:
        pose(c, "bibi", facing=1, arm="point")
    if SEEN_T - 0.02 <= t < SEEN_T + 0.4:
        face(c, "trump", eyes="wide", brows="up", mouth="o")
    yield "chart"
    if t < CHIP_T:
        classified_page(c.page, t)
    elif t < win(13):
        chip_page(c.page, t)
    yield "front"
    if t < win(13):
        bare_desk(c)
    pipette(c, t)


# --- 13. "The only bird here basted orange is you, my man." -----------------------------------------------------------
# Trump turns into the bird: a wattle on "bird", a basting brush on "basted", an orange glaze on "orange"; his
# screen goes to the kitchen, where the roast with his hair comes out on "man".

BIRD_T = lt(13, "bird")
BASTE_T = lt(13, "basted")
ORANGE_T = lt(13, "orange")
MAN_T = lt(13, "man") - 0.04
GLAZE = (226, 112, 30)


def glaze_k(t):
    return ease_out(ramp(t, BASTE_T + 0.05, ORANGE_T + 0.15))


def basting(t):
    """The brush going back and forth (0..1) while he is basted."""
    return 0.5 + 0.5 * math.sin((t - BASTE_T) * 2 * math.pi / 0.36)


def kitchen_feed(c, img, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    t = c.t
    clip = Image.new("RGB", (w, h), (236, 236, 228))
    d = ImageDraw.Draw(clip)
    for y in range(0, h, 7):                                          # kitchen tiles
        d.line([(0, y), (w, y)], fill=(200, 210, 220))
    for x in range(0, w, 7):
        d.line([(x, 0), (x, h)], fill=(200, 210, 220))
    d.rectangle((0, h - 6, w, h), fill=(150, 108, 66))                # the counter
    d.line([(0, h - 6), (w, h - 6)], fill=(196, 152, 98))
    if t < MAN_T:
        bird = A.turkey_glazed(round(glaze_k(t), 1))
        bx, by = w // 2 - bird.width // 2, h - 5 - bird.height
        clip.paste(bird, (bx, by), bird)
        if BASTE_T <= t < ORANGE_T + 0.25:
            brush = scaled(A.basting_brush(-20), 2)
            clip.paste(brush, (bx + 6 + int(basting(t) * 18), by + 6 + int(basting(t) * 6)), brush)
        pixel_text(clip, (3, 1), "KITCHEN CAM", C["white"])
    else:                                                             # served
        roast = A.roast_big()
        k = back_out(clamp((t - MAN_T) / 0.15, 0, 1))
        clip.paste(roast, ((w - roast.width) // 2, 1 + round((1 - k) * 30)), roast)
        for i, sx in enumerate((10, w - 12)):                         # steam off the drumsticks
            for j in range(3):
                yy = 14 - ((t * 18 + j * 5 + i * 3) % 15)
                d = ImageDraw.Draw(clip)
                d.point((sx + int(2 * math.sin(t * 9 + j + i)), yy), fill=(250, 250, 250))
    img.paste(clip, (x0, y0))


@gag("v2", 13)
def basted_orange(c, L):
    """A wattle sprouts under Trump's chin on "bird"; a brush bastes him on "basted" and he glazes orange
    on "orange"; on "man" his screen serves the roast turkey with his hair."""
    c.desk = False
    flip(c, CHIP_T)
    t = c.t
    g = glaze_k(t)
    if g > 0:
        c.st["trump"]["tint"] = (GLAZE, 0.3 * g)
        c.st["trump"]["rim"] = 0.8 * g
    if t >= BIRD_T - 0.05:
        c.screens["R"] = kitchen_feed
    if BASTE_T <= t < ORANGE_T + 0.25:
        face(c, "trump", eyes="shut", brows="worried", mouth="grit")
    yield "chart"
    chip_page(c.page, t)
    yield "front"
    bare_desk(c)
    if t >= BIRD_T:
        wat = A.wattle()
        mx, my = anchor(c, "trump", "mouth")
        k = ease_out(clamp((t - BIRD_T) / 0.12, 0, 1))
        part = wat.crop((0, 0, wat.width, max(1, int(wat.height * k))))
        c.world.paste(part, (mx - 3, my + 4), part)
    if BASTE_T <= t < ORANGE_T + 0.25:
        top = anchor(c, "trump", "top")
        brush = A.basting_brush(-20)
        c.world.paste(brush, (int(top[0] - 16 + basting(t) * 14), int(top[1] - 4 + basting(t) * 6)), brush)
