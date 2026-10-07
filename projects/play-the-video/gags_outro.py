"""Outro: the video ends, chat applauds, and both men have thoughts. Pause."""
from gagkit import *  # noqa: F403

L0, L1 = TL.line("outro", 0), TL.line("outro", 1)
START = TL.section_start("outro")
CLAP = TL.timing.word_time(L0, "applause")
PAUSE = TL.timing.word_time(L1, "Pause")
NAMES = ("ZYNGOD", "ROACH77", "LATTE", "BALD4", "MARXBRO", "GRUG", "OATMILK", "RATKING", "KAYA4", "DRPEPR")


def clapping(t):
    """Everybody claps, one after another, until the two of them start up again."""
    out, age = [], 9.0
    for i, name in enumerate(NAMES):
        at = CLAP + 0.25 + 0.16 * i
        if at <= t < L1["t0"] + 9:
            out.append((name + ":", "hasan_hi" if i % 2 == 0 else "asmon_hi", " ".join([":clap:"] * (1 + i % 3))))
            age = t - at
    return out, age


def groans(t):
    out, age = [], 9.0
    for i, (name, text) in enumerate((("ZYNGOD", "NO"), ("ROACH77", "NOOOO"), ("LATTE", "UNPAUSE"), ("BALD4", "PLAY IT"),
                                      ("GRUG", "UNPAUSE"), ("OATMILK", ":skull:"))):
        at = PAUSE + 0.35 + 0.22 * i
        if t >= at:
            out.append((name + ":", "hasan_hi" if i % 2 == 0 else "asmon_hi", text))
            age = t - at
    return out, age


@span(START, 1e6)
def outro(c, L):
    t = c.t
    feed(c, START, [sung(L0, t), clapping(t), sung(L1, t, first=3), groans(t)])
    if t < L1["t0"] - 0.2:                               # the video's over: relief
        over = t >= L0["t0"]
        for who in MEN:
            pose(c, who, arms="acc0" if t >= CLAP and int(t * 6) % 2 else "acc1" if t >= CLAP else "desk",
                 mouth="smile" if over else "closed", eyes="open", brows="up" if over else "neutral")
    elif t < PAUSE:                                      # and then, in unison
        for who in MEN:
            pose(c, who, arms="finger", brows="up", eyes="open")
    else:                                                # stopped, mid-thought, both of them
        for who in MEN:
            pose(c, who, arms="finger", brows="up", eyes="half", mouth="open", bob=0, react=False)
            c.cam_t[who] = PAUSE
    yield "front"
    if t >= PAUSE:
        a = t - PAUSE
        stream.veil(c.world, (0, 0, W, stream.CAP_Y), "bg", 0.35 * k_in(a, 0.2))
        lines, age = c.feed, c.feed_age                  # the chat is the one thing still moving
        stream.draw_chat(c.world, None, lines[-16:], age, chatlog.viewers(None, PAUSE), at=stream.FEED,
                         accent=("hasan", "asmon"))
        icon = stream.pause_icon(4)
        pop_in(c.world, icon, 60, 80, a, 0.12)
        pop_in(c.world, icon, W - 60, 80, a, 0.12)
    yield "top"
    if t >= TL.END_CARD + 0.6:                           # the title, where the words were
        b = t - TL.END_CARD - 0.6
        d = ImageDraw.Draw(c.ui)
        d.rectangle((0, stream.CAP_Y, W, H), fill=(12, 12, 20, 236))
        d.line([(0, stream.CAP_Y), (W // 2, stream.CAP_Y)], fill=C["hasan"] + (255,))
        d.line([(W // 2, stream.CAP_Y), (W, stream.CAP_Y)], fill=C["asmon"] + (255,))
        fx.pop_text(c.ui, W // 2, stream.CAP_Y + 11, "PLAY THE VIDEO", b, PRESS, col("gold"), col("orange"), C["black"],
                    anchor="mm", ink=INK)
