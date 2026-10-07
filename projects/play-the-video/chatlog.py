"""What the two chats type, and when.

Each stream has a chat of its own. It idles along on its regulars' habits and erupts when its streamer
lands a punchline; gags add scripted lines with `add`. `tail(host, t)` is what is on screen at t.
"""
from bisect import bisect_right

import timeline as TL
from engine import rnd
from stream import CHAT_ROWS, NAME_COLORS

NAMES = {"hasan": ("ZYNGOD", "KAYA4", "MARXBRO", "LATTE", "UNIONJ", "DSAKEV", "POGPOT", "TANKTOP", "RENT0", "LEFTY",
                   "OATMILK", "PARASOC"),
         "asmon": ("ROACH77", "DRPEPR", "BALD4", "TMOG", "LOOTBOX", "GRUG", "RATKING", "WOWDAD", "NPC42", "STEAK",
                   "BURRITO", "DUNGEON")}
IDLE = {"hasan": ("W", "REAL", "TRUE", "LMAO", "FACTS", ":lul:", ":fire:", "W TAKE", "SO TRUE", ":heart:", "KAYA W",
                  "CHAT?", "OMG", "PREACH", "UNPAUSE"),
        "asmon": ("W", "BASED", "TRUE", "LUL", ":lul:", "DUDE", "REAL", "FACTS", ":roach:", ":frog:", "GG", "YEP", "LOGIC",
                  "PLAY IT", "UNPAUSE")}
HIT = (":skull:", "LMAO", "OOF", "COOKED", "RIP", ":lul: :lul:", "DONE", ":fire: :fire:", "NO WAY", "OUCH", ":skull: :skull:",
       "GET HIM", "OH NO", "DEAD", "L", "WOW")

_log = {"hasan": [], "asmon": []}
_sorted = {"hasan": True, "asmon": True}


def add(host, t, name, text, color=None):
    """`name` types `text` in `host`'s chat at time t. A word like :skull: is an emote."""
    color = color or NAME_COLORS[int(rnd("namecolor", name) * len(NAME_COLORS))]
    _log[host].append((t, name + ":" if name else "", color, text))
    _sorted[host] = False


def _who(host, *key):
    names = NAMES[host]
    return names[int(rnd("name", host, *key) * len(names))]


def _fill():
    for host in TL.MEN:
        t, i = 0.4, 0
        while t < TL.DURATION:                                           # the regulars
            pool = IDLE[host]
            add(host, t, _who(host, i), pool[int(rnd("idle", host, i) * len(pool))])
            t += 0.7 + 1.5 * rnd("gap", host, i)
            i += 1
        for h in TL.HITS:                                                # and what a punchline sets off
            if h["attacker"] != host:
                continue
            n = 4 if h["big"] else 2
            for j in range(n):
                add(host, h["t"] + 0.15 + 0.22 * j + 0.1 * rnd("hitgap", h["t"], j), _who(host, "hit", h["t"], j),
                    HIT[int(rnd("hit", h["t"], j) * len(HIT))])


_fill()


def _messages(host):
    if not _sorted[host]:
        _log[host].sort(key=lambda m: m[0])
        _sorted[host] = True
    return _log[host]


def tail(host, t, n=CHAT_ROWS):
    """(the last n messages as (name, colour, text), seconds since the newest arrived)."""
    log = _messages(host)
    i = bisect_right(log, (t, chr(0x10FFFF)))
    part = log[max(0, i - n):i]
    return [(m[1], m[2], m[3]) for m in part], (t - part[-1][0] if part else 9.0)


def both(t, n=16):
    """The two chats run together, for when the streams are side by side."""
    log = []
    for host in TL.MEN:
        m = _messages(host)
        i = bisect_right(m, (t, chr(0x10FFFF)))
        log += m[max(0, i - n):i]
    part = sorted(log, key=lambda m: m[0])[-n:]
    return [(m[1], m[2], m[3]) for m in part], (t - part[-1][0] if part else 9.0)


def viewers(host, t):
    """The viewer count in the chat's header, wandering a little. `host` None counts both streams."""
    if host is None:
        return f"{sum(count(h, t) for h in TL.MEN) / 1000:.1f}K"
    return f"{count(host, t) / 1000:.1f}K"


def count(host, t):
    """How many are watching `host`'s stream."""
    base = {"hasan": 31200, "asmon": 58900}[host]
    return base + int(900 * rnd("viewers", host, int(t / 3))) + int(t) * 7
