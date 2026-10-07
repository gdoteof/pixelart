"""The hooks: chat has had enough. The two streams sit side by side with one chat down the middle, typing
the hook as it's sung; then we see where chat is watching from, which is work."""
from gagkit import *  # noqa: F403
import office

CUTS = {0: (0, 3, 4, 6), 1: (0,), 2: (0, 4), 3: (0, 4), 4: (0,), 5: (0,)}       # where a new chatter takes over
TWIN_CUTS = (0, 2, 4, 6)                                                       # hook 2, line 4: a chatter each
SPELL = {"MENOPAUSE.": "MEN-O-PAUSE."}                                         # chat spells the joke out


def cuts(sec, idx):
    return TWIN_CUTS if (sec, idx) == ("hook2", 4) else CUTS[idx]


def script(c, sec):
    """The hook so far, as the chat between the two streams types it."""
    parts = []
    for ln in TL.lines_of(sec):
        msgs, age = sung(ln, c.t, cuts(sec, ln["idx"]), first=2 * ln["idx"])
        parts.append(([(n, col_, " ".join(SPELL.get(w, w) for w in text.split())) for n, col_, text in msgs], age))
    feed(c, TL.section_start(sec), parts)


def flap(c, who):
    """Talking at chat, over chat: the jaw going, a new point every half second."""
    k = int(c.t * 9 + (who == "asmon")) % 3
    pose(c, who, mouth=("open", "wide", "closed")[k], brows="angry" if who == "hasan" else "up",
         arms=("palm", "point", "shrug", "chop")[int(c.t * 2 + (who == "asmon")) % 4], eyes="open")


def freeze(c, who, at):
    """Stopped like a video: the frame he was on at `at`, held."""
    k = int(at * 9 + (who == "asmon")) % 3
    pose(c, who, mouth=("open", "wide", "o")[k], brows="angry" if who == "hasan" else "up",
         arms=("palm", "point", "shrug", "chop")[int(at * 2 + (who == "asmon")) % 4], eyes="half", bob=0, react=False)
    c.cam_t[who] = at


def _hook(sec):
    t0, t1 = TL.section_bounds(sec)
    L0, L1, L2, L3, L4, L5 = (TL.line(sec, i) for i in range(6))
    paused = TL.timing.word_time(L1, "paused")
    work = L2["t0"] - 0.25                                   # the cut to the desk
    back = L4["t0"] - 0.25 if sec == "hook2" else t1         # hook 2 comes back for its ending

    @span(t0, t1)
    def hook(c, L):
        t = c.t
        script(c, sec)
        desk = work <= t < back
        if desk:
            c.office = dict(muted=True)
            for who in MEN:                                  # still at it, on a monitor nobody is listening to
                flap(c, who)
            if sec == "hook1" and t >= L4["t0"] - 0.3:       # the boss does his rounds
                a = TL.timing.word_time(L4, "boss") - 0.35
                gone = L5["t0"] - 0.1
                mini = TL.timing.word_time(L4, "minimized")
                if a <= t < gone:
                    c.office["boss_x"] = lerp(W + 26, -26, (t - a) / (gone - a))
                if mini - 0.1 <= t < gone:                   # seen coming: the stream goes into the taskbar
                    c.office.update(minimized=k_in(t - mini + 0.1, 0.18), typing=True, alert=k_in(t - mini + 0.1, 0.1))
                elif t >= gone:
                    c.office.update(minimized=max(0.0, 1 - k_in(t - gone, 0.15)))
        elif t < work:
            for who in MEN:
                if t < L1["t0"] - 0.1:                       # chat shouts; they look over at it
                    hit = any(0 <= t - w["t0"] < 0.3 for w in L0["words"] if "npause" in w["w"])
                    pose(c, who, eyes="side", brows="worried" if hit else "neutral", mouth="frown" if hit else "closed",
                         arms="desk")
                    if hit:
                        c.st[who]["shake"] = 1
                elif t < paused:                             # and carry on talking
                    flap(c, who)
                else:                                        # grown men, paused
                    freeze(c, who, paused)
        yield "front"
        if not desk:
            if L1["t0"] <= t < work:
                a = t - paused
                icon = stream.pause_icon(3)
                pop_in(c.world, icon, 58, 84, a, 0.12)
                pop_in(c.world, icon, W - 58, 84, a, 0.12)
            return
        x0, y0, x1, y1 = office.SECOND
        cx = (x0 + x1) // 2
        label(c, cx, y0 - 12, "SECOND MONITOR", t - TL.timing.word_time(L3, "second"), 1.5, "asmon", "ink")
        sound = t - TL.timing.word_time(L3, "sound")
        if 0 <= sound < 1.2 and int(sound * 6) % 2 == 0:
            office.mute_icon(c.world, x1 - 30, y1 - 24, 2)
        lurk = TL.timing.word_time(L3, "lurk")
        label(c, 160, 92, "LURKING", t - lurk, L4["t0"] - 0.15 - lurk, "ink", "text")
        if sec == "hook1" and t >= L5["t0"]:
            shout(c, 160, 84, "?", t - TL.timing.word_time(L5, "winning"), dur=TL.timing.word_time(L5, "you") - L5["t0"])
            if t >= TL.timing.word_time(L5, "mute") - 0.05:
                office.mute_icon(c.world, cx - 19, (y0 + y1) // 2 - 14, 3)

    return hook


def _twins(sec):
    """Hook 2's last two bars, side by side again: the same man twice, and what tells them apart."""
    L4, L5 = TL.line(sec, 4), TL.line(sec, 5)
    words = [TL.timing.word_time(L4, "Twin", n=i) for i in range(3)]
    played = TL.timing.word_time(L4, "played")
    one = L5["t0"]
    bathed = TL.timing.word_time(L5, "bathed")
    MOVES = ("cross", "type", "facepalm")                       # the same chair, the same job, the same ban

    @span(L4["t0"] - 0.25, TL.section_end(sec))
    def twins(c, L):
        t = c.t
        k = sum(t >= w for w in words) - 1
        if t < played:
            arms = MOVES[k] if k >= 0 else "desk"
        elif t < one:
            arms = "shrug"
        elif t < bathed:
            arms = "chest"
        else:
            arms = None
        for who in MEN:                                         # they move as one
            if arms:
                pose(c, who, arms=arms, eyes="open", brows="up" if t >= played else "neutral", mouth="closed", bob=0,
                     lean=1)
        if arms is None:
            pose(c, "hasan", arms="cross", mouth="grin", brows="up", eyes="shut", bob=0)
            pose(c, "asmon", arms="shrug", mouth="closed", brows="up", eyes="half", bob=0)
        yield "front"
        if k == 2 and t < played:                               # twin bans
            for x, tilt in ((34, -12), (W - 34, 12)):
                stamp(c, x, 30, "BANNED", t - words[2], "live", tilt)
        if t >= bathed:
            a = t - bathed
            hx, hy = c.at("hasan", "head")
            for i in range(7):                                  # one sparkles
                if int(t * 8 + i) % 3:
                    ang = i * 0.9 + t * 0.7
                    fx.sparkle(c.world, int(hx + 34 * math.cos(ang) - 4), int(hy + 30 + 30 * math.sin(ang * 1.3)),
                               2 + i % 2, col("white" if i % 2 else "gold_hi"))
            ax, ay = c.at("asmon", "head")
            d = ImageDraw.Draw(c.world)
            for i in range(3):                                  # one doesn't
                x = ax - 22 + 22 * i
                pts = [(x + int(round(2.5 * math.sin(y * 0.6 + t * 6 + i))), ay - 2 - y) for y in range(0, 18, 2)]
                d.line(pts[:max(2, int(len(pts) * min(1.0, a / 0.4)))], fill=C["mold"], width=2)
            rooms.flies(c.world, ax, ay + 6, t, 5, 2)

    return twins


for _sec in TL.HOOKS:
    _hook(_sec)
_twins("hook2")
