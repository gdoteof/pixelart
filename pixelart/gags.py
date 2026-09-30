"""Per-lyric-line gags: generators that draw in the render phases they ask for.

A gag is a generator function `fn(c, L)`: `c` is the video's per-frame context
and `L` a LineRef for the lyric line it belongs to. Code before its first
`yield` runs at setup time, before anything is drawn, so it can change the
shot, poses and so on. Each `yield "<phase>"` hands control back until the
renderer reaches that drawing phase:

    @gags.gag("v1", 3)
    def crown_drop(c, L):
        c.shot = "london"          # setup
        yield "front"              # world, in front of the characters
        draw_crown(c.world, ...)
        yield "ui"                 # UI layer
        ...

The renderer calls `run(phase)` for each of its phases in order. The phase
names are the video's own; `Gags(phases)` fixes their order.
"""
import inspect

from pixelart import timing


class LineRef:
    """A lyric line as seen by its gag: word times, and ages relative to now."""

    def __init__(self, ln, t):
        self.ln, self.t = ln, t
        self.t0, self.t1 = ln["t0"], ln["t1"]
        self.words = ln["words"]

    def w(self, pat, which="t0"):
        return timing.word_time(self.ln, pat, which)

    def age(self, pat=None):
        """Seconds since the first word matching `pat` (or the line) started; negative before."""
        return self.t - (self.w(pat) if pat else self.t0)

    def on(self, pat):
        return self.t >= self.w(pat)


class GagRunner:
    """Steps a frame's gag generators through the drawing phases in order."""

    def __init__(self, gens, phases):
        self.phases = phases
        self.wait = []
        for g in gens:
            try:
                self.wait.append([g, next(g)])
            except StopIteration:
                pass

    def run(self, phase):
        idx = self.phases.index(phase)
        for item in self.wait:
            g, ph = item
            while ph is not None and self.phases.index(ph) <= idx:
                try:
                    ph = next(g)
                except StopIteration:
                    ph = None
            item[1] = ph


class Gags:
    """A registry of gags keyed by (section, line index), and which are live at time t.

    A line's gag runs from `pre` seconds before the line starts until the next
    line in the same section starts (minus `lead`), or to the end of the
    section for its last line, plus `post`.
    """

    def __init__(self, phases):
        self.phases = tuple(phases)
        self.table = {}
        self.extra = []          # (start, end, fn) gags not tied to one line
        self._windows = None

    def gag(self, sec, idx, pre=0.15, post=0.0):
        def reg(fn):
            assert inspect.isgeneratorfunction(fn), f"{fn.__name__} must be a generator"
            assert (sec, idx) not in self.table, f"two gags for {sec} line {idx}"
            self.table[(sec, idx)] = (fn, pre, post)
            self._windows = None
            return fn
        return reg

    def span(self, start, end):
        """Register a gag for a stretch of time instead of a line; it gets L=None."""
        def reg(fn):
            assert inspect.isgeneratorfunction(fn), f"{fn.__name__} must be a generator"
            self.extra.append((start, end, fn))
            self._windows = None
            return fn
        return reg

    def windows(self, lines, section_end, lead=0.12):
        """[(start, end, fn, line)] for every registered gag; `lines` carry 'sec' and 'idx'."""
        if self._windows is None:
            by = {(ln["sec"], ln["idx"]): ln for ln in lines}
            out = []
            for key, (fn, pre, post) in self.table.items():
                ln = by[key]
                nxt = by.get((ln["sec"], ln["idx"] + 1))
                end = nxt["t0"] - lead if nxt else section_end(ln["sec"])
                out.append((ln["t0"] - pre, end + post, fn, ln))
            out += [(a, b, fn, None) for a, b, fn in self.extra]
            self._windows = out          # registration order: a later gag's setup wins
        return self._windows

    def runner(self, c, t, lines, section_end, more=()):
        """A GagRunner over the gags live at t, plus any extra generators in `more`."""
        gens = [fn(c, LineRef(ln, t) if ln else None)
                for a, b, fn, ln in self.windows(lines, section_end) if a <= t < b]
        return GagRunner(gens + list(more), self.phases)
