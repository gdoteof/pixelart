"""When things happen: the beat grid, sections, lyric lines, punchlines and vocal loudness.

All times are seconds into audio/song.wav. The song holds a steady tempo, so
the grid is one fixed period fitted to every tracked beat (the tracker can
switch between quarters and eighths without moving it).
"""
import json

import numpy as np

from engine import ROOT
from pixelart import timing

FPS = 24
DATA = ROOT / "data"
DURATION = json.loads((DATA / "song.json").read_text())["duration"]
BPM_GUESS = 94


def _grid():
    """A fixed-period grid fitted to the tracked beats: (beats, bars, period)."""
    raw = json.loads((DATA / "beat_this.json").read_text())
    beats, downs = np.asarray(raw["beats"]), np.asarray(raw["downbeats"])
    guess = 60.0 / BPM_GUESS

    def spread(per):
        ang = 2 * np.pi * beats / per
        return np.hypot(np.cos(ang).mean(), np.sin(ang).mean()), np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())

    pers = np.arange(guess * 0.97, guess * 1.03, 0.00002)
    per = pers[int(np.argmax([spread(p)[0] for p in pers]))]
    t0 = (spread(per)[1] / (2 * np.pi)) * per % per
    grid = t0 + per * np.arange(0, int((DURATION - t0) / per) + 3)
    votes = np.zeros(4)
    for d in downs:
        votes[int(round((d - t0) / per)) % 4] += 1
    ph = int(np.argmax(votes))
    return grid, grid[ph::4], per


BEATS, BARS, PERIOD = _grid()
CLOCK = timing.BeatClock(BEATS, BARS)
beat_info, since_beat, bar_info = CLOCK.beat_info, CLOCK.since_beat, CLOCK.bar_info


def beat_phase(t):
    """(beat index, phase in [0, 1))."""
    i, ph, _ = CLOCK.beat_info(t)
    return i, ph


def next_beat(t):
    i = np.searchsorted(BEATS, t)
    return float(BEATS[min(i, len(BEATS) - 1)])


# --- lyric lines ----------------------------------------------------------------------------

SEC = {"Intro": "intro", "Verse 1": "v1", "Verse 2": "v2", "Hook": "hook", "Verse 3": "v3", "Verse 4": "v4",
       "Outro": "outro"}
WHO = {"Donald Trump": "trump", "Benjamin Netanyahu": "bibi", "UN Announcer": "announcer", "Delegates": "delegates"}


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


# --- sections ---------------------------------------------------------------------------------
# Whoever raps has the floor at the rostrum; the other heckles from the delegation desk.

ORDER = ("intro", "v1", "v2", "hook", "v3", "v4", "outro", "end")
RAPPER = {"v1": "trump", "v2": "bibi", "v3": "trump", "v4": "bibi"}
OTHER = {"trump": "bibi", "bibi": "trump"}
# who holds the floor (stands at the rostrum) in each section, rappers or not
FLOOR = {"intro": "trump", "v1": "trump", "v2": "bibi", "hook": "bibi", "v3": "trump", "v4": "bibi",
         "outro": "bibi", "end": "bibi"}
VERSES = ("v1", "v2", "v3", "v4")


def _sections():
    """A section starts a beat before its first word; the end card starts after the last word."""
    firsts = {s: lines_of(s)[0]["t0"] for s in ORDER[:-1] if lines_of(s)}
    starts = {"intro": 0.0}
    for s in ORDER[1:-1]:
        before = [ln for ln in LINES if ORDER.index(ln["sec"]) < ORDER.index(s)]
        starts[s] = max(firsts[s] - 0.9, last_word(before[-1]) + 0.3)
    starts["end"] = last_word(LINES[-1]) + 1.6
    out = []
    for a, b in zip(ORDER, ORDER[1:] + ("",)):
        out.append((a, starts[a], starts[b] if b else DURATION + 1))
    return out


SECTIONS = _sections()


def section_at(t):
    for name, a, b in SECTIONS:
        if a <= t < b:
            return name, a, b
    return SECTIONS[-1] if t >= SECTIONS[-1][1] else SECTIONS[0]


def section_bounds(name):
    for n, a, b in SECTIONS:
        if n == name:
            return a, b
    raise KeyError(name)


def section_end(name):
    return section_bounds(name)[1]


def section_start(name):
    return section_bounds(name)[0]


# --- punchlines -------------------------------------------------------------------------------
# Every verse line lands on the other man at its last word; the couplet closers land hard.

KILL_SHOTS = {(s, i) for s in VERSES for i in range(1, 16, 2)}


def _hits():
    hits = []
    for ln in LINES:
        if ln["sec"] not in VERSES:
            continue
        hits.append({"t": last_word(ln) + 0.04, "target": OTHER[ln["who"]], "attacker": ln["who"],
                     "big": (ln["sec"], ln["idx"]) in KILL_SHOTS, "line": ln})
    return hits


HITS = _hits()


def last_hit(t, target=None, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window and (target is None or h["target"] == target)]
    return past[-1] if past else None


def hit_of(ln):
    return next((h for h in HITS if h["line"] is ln), None)


# --- vocal loudness (drives mouths) -----------------------------------------------------------------

ENV = np.load(DATA / "vocal_env.npy")


def loudness(t):
    return timing.frame_value(ENV, t, FPS)


if __name__ == "__main__":
    print(f"grid: {len(BEATS)} beats, period {PERIOD:.4f}s ({60 / PERIOD:.2f} BPM), first bar {BARS[0]:.3f}s")
    for s in SECTIONS:
        print(f"{s[0]:8s} {s[1]:7.2f} {s[2]:7.2f}")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big")
    for ln in LINES:
        print(f"  {ln['sec']:5s} {ln['idx']:2d} {ln['t0']:7.2f} {ln['t1']:7.2f}  {ln['text']}")
