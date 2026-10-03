"""Hook: the chat has opinions. The live chat takes over the middle of the screen and chants HANDSOME at the
guest and NEWSCUM at the host, eight and a half times. Mamdani waves and thanks it each time. Newsom turns on
slow mode, bans people, watches Trump turn up in his own chat, and turns the chat off, which doesn't help."""
from gagkit import *  # noqa: F403

HOOK = TL.lines_of("hook")
T0, T1 = TL.section_bounds("hook")
PANEL = (110, 14, 210, 139)
ROW = 7
NAMES = ("zoe_nyc", "dsa_dan", "bearbro", "pam", "renter", "lol_ca", "mike", "subway", "kai", "bodega", "gina", "sam")
FILLER = ("W", "<3", "LMAO", "ZOHRAN!!", "GAVIN WHO", "L", "RATIO", "HE'S CRYING", "W MAYOR", "OMG")


def word_t(ln, pat):
    for w in ln["words"]:
        if pat in w["w"]:
            return w["t0"]
    return None


T_SLOW = HOOK[4]["t0"] + 0.6
T_TRUMP = HOOK[10]["t0"] + 0.15                     # Donald turns up in the chat
T_OFF = HOOK[12]["t0"] - 0.1                        # the host turns the chat off...
T_ASK = HOOK[13]["t0"] + 0.4                        # ...Donald asks for it back...
T_BACK = HOOK[14]["t0"] - 0.2                       # ...and it's back on


def _messages():
    """Every chat message in the hook: (time, name, text, colour); name None for the moderator."""
    out = []
    for i, ln in enumerate(HOOK):
        for pat, msg, col_, n in (("Handsome", "HANDSOME!", "gold", 3), ("Newscum", "NEWSCUM!", "pink", 3),
                                  ("Has-been", "HAS-BEEN!", "pink", 3), ("Boo", "BOO!", "dim", 2)):
            t = word_t(ln, pat)
            if t is None:
                continue
            for j in range(n):
                k = int(rnd("who", i, pat, j) * len(NAMES))
                out.append((t + 0.09 * j, NAMES[k], msg, col_))
        t = ln["t0"] + 0.5 * (ln["t1"] - ln["t0"]) + 0.4
        out.append((t, NAMES[int(rnd("fn", i) * len(NAMES))], FILLER[i % len(FILLER)], "chat_text"))
    out = [m for m in out if not T_OFF <= m[0] < T_BACK]
    out += [(T_SLOW, None, "SLOW MODE: ON", "duck"),
            (HOOK[6]["t0"] + 0.5, None, "RENTER WAS BANNED", "duck"),
            (HOOK[8]["t0"] + 0.5, None, "DSA_DAN WAS BANNED", "duck"),
            (T_TRUMP, "realDonaldTrump", "HANDSOME!!", "red_hi"),
            (T_OFF, None, "CHAT IS OFF", "duck"),
            (T_ASK, "realDonaldTrump", "TURN IT ON", "red_hi"),
            (T_BACK, None, "CHAT IS BACK ON", "duck")]
    return sorted(out, key=lambda m: m[0])


MESSAGES = _messages()


def draw_panel(c, t):
    x0, y0, x1, y1 = PANEL
    d = ImageDraw.Draw(c.ui)
    k = k_in(t - (T0 + V.CARD_TIME), 0.3)                              # once the chapter card has gone
    if t > T1 - 0.3:
        k = min(k, k_in(T1 - t, 0.3))
    if k <= 0:
        return
    off = int((1 - ease_out(k)) * -140)
    y0, y1 = y0 + off, y1 + off
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=INK + (255,))
    d.rectangle((x0, y0, x1, y1), fill=(14, 16, 30, 236))
    d.rectangle((x0, y0, x1, y0 + 8), fill=C["tt_pink"] + (255,))
    V.ui_text(c.ui, (x0 + 3, y0 + 2), "LIVE CHAT")
    V.ui_text(c.ui, (x1 - 3, y0 + 2), V.fmt_count(V.viewers_at(t)), anchor="ra")
    shown = [m for m in MESSAGES if m[0] <= t]
    rows = (y1 - y0 - 12) // ROW
    for r, (tm, name, msg, col_) in enumerate(shown[-rows:]):
        y = y0 + 11 + r * ROW
        if name is None:                                               # the moderator: a yellow system line
            V.ui_text(c.ui, (x0 + 3, y), msg, fill=C[col_])
            continue
        nc = C["tie_hi"] if name == "realDonaldTrump" else V.chat_color(name)
        label = (name if name != "realDonaldTrump" else "DONALD") + ":"
        V.ui_text(c.ui, (x0 + 3, y), label, fill=nc)
        V.ui_text(c.ui, (x0 + 5 + pixel.text_width(label, SILK), y), msg, fill=C[col_])


def floats(c, t):
    """Hearts float up for every HANDSOME, skulls for every BOO."""
    for i, ln in enumerate(HOOK):
        for pat, kinds in (("Handsome", ("heart", "heart", "laugh")), ("Boo", ("skull", "skull", "laugh"))):
            te = word_t(ln, pat)
            if te is None:
                continue
            for j in range(4):
                a = t - te - j * 0.1
                if 0 <= a < 1.4:
                    x = 296 + int(rnd("hx", i, pat, j) * 16) + int(3 * math.sin(a * 5 + j))
                    c.floats.append((kinds[j % 3], x, 140 - a * 75))


@GAGS.span(T0 - 0.2, T1 + 0.2)
def the_chat(c, L):
    t = c.t
    now = TL.line_at(t, lead=0.0, hold=0.6)
    i = HOOK.index(now) if now in HOOK else (0 if t < HOOK[0]["t0"] else len(HOOK) - 1)
    ln = HOOK[i]
    t_h = word_t(ln, "Handsome")
    t_thx = word_t(ln, "(Thank")
    t_x = word_t(ln, "Newscum") or word_t(ln, "Has-been")
    t_boo = word_t(ln, "Boo")
    # the guest: a wave for every HANDSOME, a hand on his heart for every thank-you
    m = c.st["mamdani"]
    if t_thx is not None and t >= t_thx - 0.05:
        pose(c, "mamdani", arms="chest", eyes="shut", brows="up",
             mouth=V.mouth_for("mamdani", TL.loudness(t)) if t < ln["t1"] + 0.1 else "grin")
    elif t_h is not None:
        pose(c, "mamdani", arms="wave", eyes="shut" if t - t_h < 0.5 else "open", mouth="grin", brows="up")
    else:
        pose(c, "mamdani", arms="clasp", mouth="grin")
    m["bob"] = 1 if c.ph < 0.3 else 0
    # the host: flinches, then fights the chat
    n = c.st["newsom"]
    if t < HOOK[4]["t0"]:
        if t_x is not None and t >= t_x:
            pose(c, "newsom", arms="clasp", brows="worried", mouth="o" if t_boo and t >= t_boo else "frown", eyes="half")
        else:
            pose(c, "newsom", arms="clasp", mouth="smile", eyes="side")
    elif t < T_TRUMP:                                                  # moderating
        pose(c, "newsom", arms="type", eyes="side", brows="angry", mouth="grit" if int(t * 3) % 2 else "frown")
    elif t < T_OFF - 0.4:                                              # Donald, in his chat
        pose(c, "newsom", arms="type", eyes="wide", brows="worried", mouth="o")
    elif t < T_OFF:
        pose(c, "newsom", arms="type", eyes="side", brows="angry", mouth="grit")
    elif t < T_ASK:                                                    # peace at last
        pose(c, "newsom", arms="clasp", eyes="shut", brows="neutral", mouth="smile")
    elif t < T_BACK + 0.5:
        pose(c, "newsom", arms="clasp", eyes="wide", brows="worried", mouth="o")
    else:
        pose(c, "newsom", arms="facepalm", eyes="shut", brows="worried", mouth="frown")
    n["react"] = False
    m["react"] = False
    floats(c, t)
    yield "ui"
    draw_panel(c, t)
