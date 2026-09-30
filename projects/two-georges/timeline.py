"""When things happen: beats, sections, lyric lines, punchlines and vocal loudness.

All times are seconds into audio/song.wav. The beat tracker hears the drill beat
in half time (about 71 BPM, one beat every 0.84 s), which is the right speed
for head nods; `half` gives the 142 BPM hi-hat pulse for anything snappier.
"""
import json

import numpy as np

from engine import ROOT
from pixelart import timing

FPS = 24
DATA = ROOT / "data"
DURATION = json.loads((DATA / "song.json").read_text())["duration"]

_beats = json.loads((DATA / "beat_this.json").read_text())
CLOCK = timing.BeatClock(_beats["beats"], _beats["downbeats"])
beat_info, since_beat, bar_info = CLOCK.beat_info, CLOCK.since_beat, CLOCK.bar_info


def half(t):
    """(half-beat index, phase) on the 142 BPM pulse."""
    i, ph, _ = CLOCK.beat_info(t)
    return 2 * i + (ph >= 0.5), (ph * 2) % 1.0


# --- lyric lines ------------------------------------------------------------

SEC = {"Intro": "intro", "Verse 1": "v1", "Verse 2": "v2", "Verse 3": "v3", "Verse 4": "v4"}
WHO = {"Town Crier": "crier", "King George III": "george", "George Washington": "washington"}


def _load_lines():
    raw = json.loads((DATA / "lyrics_timed.json").read_text())
    counters, lines = {}, []
    for gi, ln in enumerate(raw):
        sec = SEC[ln["section"]]
        idx = counters.get(sec, 0)
        counters[sec] = idx + 1
        lines.append({**ln, "sec": sec, "idx": idx, "gi": gi, "who": WHO[ln["speaker"]]})
    return lines


LINES = _load_lines()


def lines_of(sec):
    return [ln for ln in LINES if ln["sec"] == sec]


def line(sec, idx):
    return next(ln for ln in LINES if ln["sec"] == sec and ln["idx"] == idx)


def line_at(t, lead=0.12, hold=0.9):
    return timing.line_at(LINES, t, lead, hold)


word_index = timing.word_index
word_time = timing.word_time


def last_word(ln):
    """When the last word of a line is sung (its t1 can stretch over the gap that follows)."""
    return ln["words"][-1]["t0"]


# --- sections -----------------------------------------------------------------

def _sections():
    """A verse starts 0.6 s before its first word, or just after the previous verse's last word
    when the next rapper comes straight in (verse 3 starts 0.3 s after verse 2 ends)."""
    starts = [("intro", 0.0)]
    prev = "intro"
    for sec in ("v1", "v2", "v3", "v4"):
        first = lines_of(sec)[0]["t0"]
        starts.append((sec, min(max(first - 0.6, last_word(lines_of(prev)[-1]) + 0.2), first - 0.05)))
        prev = sec
    starts.append(("outro", last_word(LINES[-1]) + 1.2))
    out = []
    for (name, a), nxt in zip(starts, starts[1:] + [("end", DURATION + 1)]):
        out.append((name, a, nxt[1]))
    return out


SECTIONS = _sections()
RAPPER = {"intro": "crier", "v1": "george", "v2": "washington", "v3": "george", "v4": "washington"}
OTHER = {"george": "washington", "washington": "george"}
VERSE_NO = {"v1": "I", "v2": "II", "v3": "III", "v4": "IV"}


def section_at(t):
    for name, a, b in SECTIONS:
        if a <= t < b:
            return name, a, b
    return SECTIONS[-1]


def section_bounds(name):
    for n, a, b in SECTIONS:
        if n == name:
            return a, b
    raise KeyError(name)


def section_end(name):
    return section_bounds(name)[1]


# --- punchlines -----------------------------------------------------------------
# Every verse line lands on the listener at its last word; these land hard.

KILL_SHOTS = {
    ("v1", 1), ("v1", 5), ("v1", 7), ("v1", 9), ("v1", 11), ("v1", 13), ("v1", 15),
    ("v2", 4), ("v2", 6), ("v2", 8), ("v2", 10), ("v2", 12), ("v2", 14),
    ("v3", 1), ("v3", 3), ("v3", 5), ("v3", 7), ("v3", 9), ("v3", 14),
    ("v4", 3), ("v4", 5), ("v4", 7), ("v4", 9), ("v4", 10), ("v4", 12), ("v4", 17), ("v4", 21),
}


def _hits():
    hits = []
    for ln in LINES:
        if ln["sec"] not in VERSE_NO:
            continue
        hits.append({"t": last_word(ln) + 0.04, "target": OTHER[ln["who"]], "attacker": ln["who"],
                     "big": (ln["sec"], ln["idx"]) in KILL_SHOTS, "line": ln})
    return hits


HITS = _hits()


def last_hit(t, target=None, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window and (target is None or h["target"] == target)]
    return past[-1] if past else None


def hit_of(ln):
    return next(h for h in HITS if h["line"] is ln)


# --- vocal loudness (drives mouths) -------------------------------------------

ENV = np.load(DATA / "vocal_env.npy")


def loudness(t):
    return timing.frame_value(ENV, t, FPS)


if __name__ == "__main__":
    for s in SECTIONS:
        print(f"{s[0]:6s} {s[1]:7.2f} {s[2]:7.2f}")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big")
