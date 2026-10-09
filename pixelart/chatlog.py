"""What stream chats type, and when.

Each host's stream has a chat of its own. It idles along on its regulars' habits and erupts when its
streamer lands a punchline; gags add scripted lines with `add`. `tail(host, t)` is what is on screen at t.

    LOG = ChatLog(hosts=("hasan", "asmon"), duration=DURATION, names=NAMES, idle=IDLE, hit_words=HIT,
                  hits=HITS, base={"hasan": 31200, "asmon": 58900}, name_colors=NAME_COLORS)

`names` and `idle` are per host: who the regulars are and what they type when nothing is happening.
`hits` are the punchlines, each {"t", "attacker", "big"}: the attacker's chat answers each one with
`hit_words`. A word like :skull: is an emote. `base` is each stream's viewer count.
"""
from bisect import bisect_right

from pixelart.anim import rnd


class ChatLog:
    def __init__(self, hosts, duration, names, idle, hit_words, hits, base, name_colors, rows=7):
        self.hosts, self.names, self.base, self.name_colors, self.rows = tuple(hosts), names, base, name_colors, rows
        self._log = {h: [] for h in self.hosts}
        self._sorted = {h: True for h in self.hosts}
        for host in self.hosts:
            t, i = 0.4, 0
            while t < duration:                                              # the regulars
                pool = idle[host]
                self.add(host, t, self._who(host, i), pool[int(rnd("idle", host, i) * len(pool))])
                t += 0.7 + 1.5 * rnd("gap", host, i)
                i += 1
            for h in hits:                                                   # and what a punchline sets off
                if h["attacker"] != host:
                    continue
                n = 4 if h["big"] else 2
                for j in range(n):
                    self.add(host, h["t"] + 0.15 + 0.22 * j + 0.1 * rnd("hitgap", h["t"], j),
                             self._who(host, "hit", h["t"], j), hit_words[int(rnd("hit", h["t"], j) * len(hit_words))])

    def add(self, host, t, name, text, color=None):
        """`name` types `text` in `host`'s chat at time t."""
        color = color or self.name_colors[int(rnd("namecolor", name) * len(self.name_colors))]
        self._log[host].append((t, name + ":" if name else "", color, text))
        self._sorted[host] = False

    def _who(self, host, *key):
        names = self.names[host]
        return names[int(rnd("name", host, *key) * len(names))]

    def _messages(self, host):
        if not self._sorted[host]:
            self._log[host].sort(key=lambda m: m[0])
            self._sorted[host] = True
        return self._log[host]

    def tail(self, host, t, n=None):
        """(the last n messages as (name, colour, text), seconds since the newest arrived)."""
        log = self._messages(host)
        i = bisect_right(log, (t, chr(0x10FFFF)))
        part = log[max(0, i - (n or self.rows)):i]
        return [(m[1], m[2], m[3]) for m in part], (t - part[-1][0] if part else 9.0)

    def both(self, t, n=16):
        """Every host's chat run together, for when the streams share the frame."""
        log = []
        for host in self.hosts:
            m = self._messages(host)
            i = bisect_right(m, (t, chr(0x10FFFF)))
            log += m[max(0, i - n):i]
        part = sorted(log, key=lambda m: m[0])[-n:]
        return [(m[1], m[2], m[3]) for m in part], (t - part[-1][0] if part else 9.0)

    def count(self, host, t):
        """How many are watching `host`'s stream."""
        return self.base[host] + int(900 * rnd("viewers", host, int(t / 3))) + int(t) * 7

    def viewers(self, host, t):
        """The viewer count in the chat's header, wandering a little. `host` None counts every stream."""
        if host is None:
            return f"{sum(self.count(h, t) for h in self.hosts) / 1000:.1f}K"
        return f"{self.count(host, t) / 1000:.1f}K"
