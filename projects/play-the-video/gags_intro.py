"""Intro: Hasan's stream is starting soon. Then it starts: Asmongold has made a video about him, chat wants
it played, and he gets one second in before he has notes."""
from gagkit import *  # noqa: F403

L0, L1 = TL.line("intro", 0), TL.line("intro", 1)
LIVE_AT = max(0.6, L0["t0"] - 1.6)                  # the holding card comes down
PLAY = TL.timing.word_time(L0, "Play")
PAUSE = L1["t0"]
INTRO_END = TL.section_end("intro")


@lru_cache(maxsize=None)
def soon_card():
    """What a stream shows before it starts."""
    img = Image.new("RGB", (W, H), C["hasan_sh"])
    vgrad(img, (0, 0, W, H), "hasan_sh", "night", steps=6)
    d = ImageDraw.Draw(img)
    for i in range(0, W + H, 16):                                    # diagonal bands
        d.line([(i, 0), (i - H, H)], fill=C["hasan"], width=1)
    silk(img, (W // 2, 44), "STREAM STARTING SOON", "hasan_hi", anchor="ma")
    fx.big_text(img, (W // 2, 62), "PLAY THE", PRESS16, col("gold"), col("orange"), C["black"], anchor="ma", ink=INK)
    fx.big_text(img, (W // 2, 84), "VIDEO", PRESS16, col("gold"), col("orange"), C["black"], anchor="ma", ink=INK)
    silk(img, (W // 2, 114), "HASANABI  VS.  ASMONGOLD", "text", anchor="ma")
    return img


@lru_cache(maxsize=None)
def thumbnail():
    """Asmongold's upload, as it waits to be played: his face, and a title in the house style."""
    cam = rooms.ROOM["asmon"]().copy()
    spr, _ = figure("asmon", "point", facing=-1, eyes="wide", brows="up", mouth="wide")
    cam.paste(spr, FIG["asmon"], spr)
    cam.paste(rooms.DESK["asmon"](), (0, 0), rooms.DESK["asmon"]())
    pic = stream.preview_pic(cam, "asmon")
    stream.veil(pic, (0, 0, 46, PH), "bg", 0.6)
    silk(pic, (3, 6), "HASAN", "yellow"); silk(pic, (3, 15), "IS", "white"); silk(pic, (3, 24), "DONE", "live")
    return pic


def play_button(img, x, y):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - 11, y - 8, x + 11, y + 8), 3, fill=C["live"], outline=INK)
    d.polygon([(x - 3, y - 4), (x - 3, y + 4), (x + 4, y)], fill=C["white"])


@span(0.0, INTRO_END)
def intro(c, L):
    t = c.t
    if t < LIVE_AT:
        c.overlay = c.subs = False
    if t < PLAY:                                                     # the video, waiting
        c.window.update(pic=thumbnail(), title="ASMONGOLD", badge="0:00", paused=False, progress=0.0)
        if t >= L0["t0"]:
            video = t - TL.timing.word_time(L0, "video")
            pose(c, "hasan", arms="window" if video >= 0 else "palm", brows="up", eyes="up" if video >= 0 else "open")
    elif t < PAUSE:                                                  # it plays: the logo, for about a second
        c.cam_t["asmon"] = t
        c.window.update(paused=False, progress=0.02 * (t - PLAY) / (PAUSE - PLAY), badge="0:00")
        pose(c, "asmon", arms="palm", eyes="open", brows="up", mouth="open" if int(t * 8) % 2 else "closed")
        pose(c, "hasan", arms="chin", eyes="up", brows="skeptic", mouth="closed")
    else:                                                            # and that's enough of that
        a = t - PAUSE
        if a < 0.9:
            pose(c, "hasan", arms="chop", brows="angry", eyes="open", bob=0)
        if a < 0.25:
            c.window["shake"] = 2
    yield "front"
    if t < LIVE_AT:
        c.world.paste(soon_card(), (0, 0))
        dots = int(t * 3) % 4
        silk(c.world, (W // 2, 132), "." * dots, "hasan_hi", anchor="ma")
        return
    x, y = win(c, PW // 2, PH // 2)
    if t < PLAY:
        play_button(c.world, x, y - 2)
    elif t < PAUSE and t - PLAY < 0.5:                                # the logo sting
        m = scaled(stream.logo("asmon"), 3)
        pop_in(c.world, m, x, y, t - PLAY, 0.12)
    elif PAUSE <= t < PAUSE + 0.7:
        icon = stream.pause_icon(2)
        pop_in(c.world, icon, x, y, t - PAUSE, 0.1)
