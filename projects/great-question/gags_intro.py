"""Intro: Felix says hello and gets as far as "PewDie-" before Sam bans his account. He appeals, comes back
as "PewDiePie (2)" and is banned again, sooner. He sits out the rest of the call as "PewDiePie (3)"."""
from gagkit import *  # noqa: F403
from pixelart.gags import LineRef

BAN1, BAN2 = TL.BUZZ[:2]
BACK1 = when("intro", 1) - 0.3                      # he rejoins, appeal in hand
BACK2 = when("v1", 0) - 0.7                         # and again, as the verse starts
INTRO_END = when("v1", 0) + 0.5


@lru_cache(maxsize=None)
def title_card():
    """What the window shares before anything is said: the bill."""
    p = Pic("panel")
    p.grad((0, 0, PW, PH), "panel_hi", "panel")
    p.silk((PW // 2, 7), "TONIGHT'S CALL", "dim", anchor="ma")
    p.press((PW // 2, 20), "PEWDIEPIE", "felix_hi", anchor="ma", shadow="ink")
    p.big((PW // 2, 35), "VS")
    p.press((PW // 2, 58), "SAM ALTMAN", "sam_hi", anchor="ma", shadow="ink")
    p.line([(14, 73), (86, 73)], "line")
    p.orb(14, 84, 5)
    p.silk((23, 79), "MODERATED BY", "dim")
    p.silk((23, 86), "CHATGPT", "text")
    return p.img


@lru_cache(maxsize=None)
def appeal():
    return P.sheet(40, 30, "APPEAL", "blue", n=3, tick=True)


BANS = (("ACCOUNT BANNED", "APPEAL", "text"), ("BANNED (AGAIN)", "APPEAL: DENIED", "live"),
        ("BANNED (X3)", "APPEAL: LOL", "live"))


def banned(img, n, a):
    """The dialog over a banned man's tile (TW x TH): his first ban, his second, and the one at the end."""
    title, appeal_, color = BANS[n - 1]
    d = ImageDraw.Draw(img)
    dy = pop_dy(a, 0.14, 8) or 0
    x0, y0, x1, y1 = 7, 30 + dy, 92, 88 + dy
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK)
    d.rectangle((x0, y0, x1, y1), fill=C["bar"])
    d.rectangle((x0, y0, x1, y0 + 12), fill=C["live"])
    silk(img, (TW // 2, y0 + 4), title, "white", anchor="ma")
    d.ellipse((x0 + 6, y0 + 19, x0 + 22, y0 + 35), outline=C["live"], width=2)        # no entry
    d.line([(x0 + 9, y0 + 32), (x0 + 19, y0 + 22)], fill=C["live"], width=2)
    silk(img, (x0 + 28, y0 + 19), "REASON:", "dim")
    silk(img, (x0 + 28, y0 + 27), "DISTILLING", "text")
    half = max(28, silk_w(appeal_) // 2 + 5)                           # the button, as wide as its answer
    d.rectangle((TW // 2 - half, y0 + 43, TW // 2 + half - 1, y0 + 53), fill=C["panel_hi"], outline=C["line"])
    silk(img, (TW // 2, y0 + 46), appeal_, color, anchor="ma")


@span(0.0, 1e6)
def call_state(c, L):
    """Who is in the call, and under which name: each ban costs Felix an account."""
    t = c.t
    c.st["felix"]["name"] = "PEWDIEPIE" if t < BACK1 else "PEWDIEPIE (2)" if t < BACK2 else "PEWDIEPIE (3)"
    if BAN1 <= t < BACK1 or BAN2 <= t < BACK2:
        c.people = 2
    yield "top"


@span(0.0, INTRO_END)
def bans(c, L):
    t = c.t
    L0, L1 = LineRef(TL.line("intro", 0), t), LineRef(TL.line("intro", 1), t)
    if c.screen is None:
        show(c, title_card(), "RAP BATTLE", 1.0)
    elif c.screen["under"] is None:                                    # the verse's first exhibit slides over it
        c.screen["under"] = title_card()
    out = BAN1 <= t < BACK1 or BAN2 <= t < BACK2
    if out:                                                            # frozen on his last frame
        pose(c, "felix", arms="chest", eyes="wide", brows="up", mouth="o", grey=1.0, react=False, bob=0)
        a = t - (BAN1 if t < BACK1 else BAN2)
        if a < 0.25:
            c.st["felix"]["shake"] = 3
        jolt(c, a, 3, 0.2)
    elif t < BAN1:
        if not L0.on("bros"):
            pose(c, "felix", arms="wave", brows="up")
        elif L0.age("My") < -0.2:                                      # the fist at the camera
            pose(c, "felix", arms="bro", brows="up", eyes="shut" if L0.age("bros") < 0.7 else "open", mouth="grin")
        else:
            pose(c, "felix", arms="chest", brows="up")
    elif t < BAN2:
        if not L1.on("I'm"):
            hold(c, "felix", appeal())
            pose(c, "felix", brows="up", eyes="open")
        elif L1.age("My") < -0.1:
            pose(c, "felix", arms="up2", brows="up", eyes="shut" if L1.on("bros") else "open")
        else:
            pose(c, "felix", arms="chest", brows="up")
    else:                                                              # back again, and not amused
        pose(c, "felix", arms="cross", brows="angry", mouth="frown", eyes="side")
    for ban, bored in ((BAN1, False), (BAN2, True)):                   # Sam, and the button on his desk
        a = t - ban
        if -0.45 <= a < 0:
            pose(c, "sam", arms="reach", eyes="half" if bored else "down", mouth="closed")
        elif 0 <= a < 0.6:
            pose(c, "sam", arms="press", eyes="half" if bored else "open", mouth="smirk",
                 brows="neutral" if bored else "up")
            c.vars["ban"] = True
        elif 0.6 <= a < 1.3:
            pose(c, "sam", arms="clasp", mouth="smile", eyes="open")
    toast(c, "PEWDIEPIE WAS REMOVED BY SAM ALTMAN", t - BAN1, BACK1 - BAN1 - 0.05, "live")
    toast(c, "PEWDIEPIE (2) JOINED", t - BACK1, 1.6)
    toast(c, "PEWDIEPIE (2) WAS REMOVED BY SAM ALTMAN", t - BAN2, BACK2 - BAN2 - 0.05, "live")
    toast(c, "PEWDIEPIE (3) JOINED", t - BACK2, 0.9)
    yield "front"
    if out:
        again = t >= BAN2
        over_tile(c, "felix", lambda img: banned(img, 2 if again else 1, t - (BAN2 if again else BAN1)))
