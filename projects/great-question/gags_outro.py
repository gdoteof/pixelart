"""The outro: ChatGPT can't name a winner, so Felix calls in his own model to say its name. It says "Great
question!" first, and then what it is. Sam has a button for that; ChatGPT sends round the notes."""
from gagkit import *  # noqa: F403
from gags_hook import chip
from gags_intro import banned
from gags_v4 import rig_label

JOIN = when("outro", 0) - 0.1                   # "Ajax,": it joins the call
MY = when("outro", 0, "my")
SAY = when("outro", 0, "Say")
WAIT = TL.last_word(TL.line("outro", 0)) + 0.5
GREAT = when("outro", 1)                        # "Great question!": he has heard that before
DISTILLED = when("outro", 1, "distilled")       # the helmet comes off
CHATGPT = when("outro", 1, "ChatGPT")           # and the paint
BAN3 = float(next(b for b in TL.SONG.bars if b > TL.LAST_WORD_END))   # the bar after its last word: bleep's third buzzer
NOTES = BAN3 + 1.0


def ajax_pic(c):
    """Ajax in the window: bronze, helmeted, home-made. Then what is under that."""
    t = c.t
    told, off = t >= CHATGPT, t - DISTILLED
    p = Pic("black")
    p.grad((0, 0, PW, PH), *(("panel_hi", "panel") if told else ("brown_sh", "black")))
    talk = V.talk_level(c)
    p.orb(50, 38, 17, "sorry" if t >= BAN3 else "happy", talk, "gpt" if told else "ajax", min(2, talk))
    if 0 <= t - CHATGPT < 0.2:
        fx.burst(p.img, 50, 38, 21, 31, col("white"), 12, t * 4, INK)
    if off < 0:
        p.put(helmet(17), 50, 32)
    else:                                                              # it tips off and is gone
        fly(p.img, helmet(17), (50, 32), (108, 100), off / 0.7, lift=24, turns=0.6)
    p.press((51, 63), "CHATGPT" if told else "AJAX", "gpt_glow" if told else "ajax_hi", anchor="ma", shadow="ink")
    if t < GREAT:
        p.tag((50, 78), "100% HOME-MADE", "ajax_sh", "white", "ma")
    elif off < 0:
        chip(p, 75, ["GREAT QUESTION!"], -1, t - GREAT)
    else:
        p.tag((50, 78 + (pop_dy(off, 0.12, 5) or 0)), "100% DISTILLED", "live", "white", "ma")
    return p


@lru_cache(maxsize=None)
def notes():
    """What ChatGPT sends round afterwards."""
    p = Pic("panel")
    p.grad((0, 0, PW, PH), "panel_hi", "panel")
    p.header("CALL NOTES", "gpt_sh", "white")
    for i, s in enumerate(("1. YOU HATE HIM", "2. HE HATES YOU", "3. WHO WON?")):
        p.silk((10, 17 + 9 * i), s, "text")
    p.big((51, 45), "GREAT", fnt=PRESS)
    p.big((51, 57), "QUESTION!", fnt=PRESS)
    p.line([(14, 73), (86, 73)], "line")
    p.put(mini("felix"), 34, 84); p.silk((50, 81), "VS", "dim", anchor="ma"); p.put(mini("sam", "smile", -1), 66, 84)
    return p.img


@span(JOIN, 1e6)
def ajax_joins(c, L):
    t = c.t
    told, out = t >= CHATGPT, t >= BAN3
    # --- the window: Ajax, then ChatGPT (2), then the notes
    if t < NOTES:
        c.gpt.update(kind="gpt" if told else "ajax", title="CHATGPT (2)" if told else "AJAX")
    show(c, ajax_pic(c), "SAM'S OWN A.I." if told else "FELIX'S OWN A.I.", t - JOIN, 0.2)
    show(c, notes(), "AUTO-SUMMARY", t - NOTES, 0.25)
    c.people = 2 if out else 4
    if told:
        c.vars["voice"] = "gpt2"                                       # the captions know, too
    c.rack_lit = not out
    toast(c, "AJAX JOINED", t - JOIN - 0.15, 2.2)
    toast(c, "AJAX RENAMED ITSELF CHATGPT (2)", t - CHATGPT - 0.25, BAN3 - CHATGPT - 0.35)
    toast(c, "PEWDIEPIE (3) WAS REMOVED BY SAM ALTMAN", t - BAN3, 9.0, "live")
    # --- Felix: the proud owner, until it speaks
    if out:                                                            # frozen on his last frame, again
        pose(c, "felix", arms="facepalm", eyes="shut", brows="worried", mouth="frown", grey=1.0, react=False, bob=0)
        if t - BAN3 < 0.25:
            c.st["felix"]["shake"] = 3
        jolt(c, t - BAN3, 3, 0.2)
    elif t < MY:
        pose(c, "felix", arms="point", brows="up")
    elif t < SAY - 0.15:
        pose(c, "felix", arms="chest", brows="up")
    elif t < WAIT:
        pose(c, "felix", arms="palm", brows="up")
    elif t < GREAT + 0.35:
        pose(c, "felix", arms="cross", brows="up", eyes="side", mouth="grin")
    elif t < DISTILLED:                                                # the smile goes first
        pose(c, "felix", arms="cross", brows="up", eyes="wide", mouth="closed", sweat=t > GREAT + 0.9)
    elif t < CHATGPT + 0.45:
        pose(c, "felix", arms="hush", brows="worried", eyes="wide", mouth="o", sweat=True)
    else:
        pose(c, "felix", arms="facepalm", brows="worried", eyes="shut", mouth="frown")
    # --- Sam: he knows that voice
    a = t - BAN3
    if -0.45 <= a < 0:
        pose(c, "sam", arms="reach", eyes="down", mouth="smirk")
    elif 0 <= a < 0.6:
        pose(c, "sam", arms="press", eyes="open", mouth="smirk", brows="up")
        c.vars["ban"] = True
    elif a >= 0.6:
        pose(c, "sam", arms="clasp", eyes="open", mouth="smile", brows="neutral")
    elif t >= CHATGPT + 0.3:
        pose(c, "sam", arms="clasp", eyes="half", mouth="smile", brows="up")
    elif t >= GREAT + 0.35:
        pose(c, "sam", arms="chin", eyes="side", brows="up", mouth="smirk" if t >= DISTILLED else "closed")
    jolt(c, t - CHATGPT, 2, 0.2)
    yield "mid"
    if not out:
        rig_label(c)
    yield "front"
    if out:
        over_tile(c, "felix", lambda img: banned(img, 3, t - BAN3))
