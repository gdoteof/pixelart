"""When things happen: the beat grid, sections, lyric lines, punchlines and vocal loudness.

All times are seconds into audio/song.wav. The song is a steady 75 BPM (one
lyric line per bar, most of the way), but the beat tracker switches to
counting eighth notes after about 150 s, so the grid here is fitted to the
tracked beats of the first half and extended at a fixed period.
"""
import json

import numpy as np

from engine import ROOT
from pixelart import timing

FPS = 24
DATA = ROOT / "data"
DURATION = json.loads((DATA / "song.json").read_text())["duration"]


def _grid():
    """A fixed-period grid fitted to every tracked beat, whether the tracker heard quarters or eighths."""
    raw = json.loads((DATA / "beat_this.json").read_text())
    beats, downs = np.asarray(raw["beats"]), np.asarray(raw["downbeats"])

    def spread(per):
        ang = 2 * np.pi * beats / (per / 2)
        return np.hypot(np.cos(ang).mean(), np.sin(ang).mean()), np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())

    pers = np.arange(0.790, 0.810, 0.00002)
    per = pers[int(np.argmax([spread(p)[0] for p in pers]))]
    t0 = (spread(per)[1] / (2 * np.pi)) * (per / 2) % (per / 2)
    # the quarter-note beats are the eighths the tracker marks in the first minute, where it hears quarters
    early = beats[beats < 60]
    on = np.mean(np.abs(((early - t0) / per) % 1.0 - 0.5) > 0.25)
    t0 = t0 if on >= 0.5 else t0 + per / 2
    grid = t0 + per * np.arange(0, int((DURATION - t0) / per) + 3)
    # which beat of four the tracker calls the downbeat, by majority
    votes = np.zeros(4)
    for d in downs:
        votes[int(round((d - t0) / per)) % 4] += 1
    ph = int(np.argmax(votes))
    bars = grid[ph::4]
    return grid, bars, per


BEATS, BARS, PERIOD = _grid()
CLOCK = timing.BeatClock(BEATS, BARS)
beat_info, since_beat, bar_info = CLOCK.beat_info, CLOCK.since_beat, CLOCK.bar_info


def beat_phase(t):
    """(beat index, phase in [0, 1))."""
    i, ph, _ = CLOCK.beat_info(t)
    return i, ph


def half(t):
    """(eighth-note index, phase) on the 150 BPM pulse."""
    i, ph, _ = CLOCK.beat_info(t)
    return 2 * i + (ph >= 0.5), (ph * 2) % 1.0


def next_beat(t):
    i = np.searchsorted(BEATS, t)
    return float(BEATS[min(i, len(BEATS) - 1)])


# --- lyric lines ----------------------------------------------------------------

SEC = {"Intro": "intro", "Verse 1": "v1", "Verse 2": "v2", "Verse 3": "v3", "Verse 4": "v4", "Outro": "outro"}
WHO = {"David Attenborough": "david", "Morgan Freeman": "morgan"}


def _load_lines():
    raw = json.loads((DATA / "lyrics_timed.json").read_text())
    counters, lines = {}, []
    for gi, ln in enumerate(raw):
        sec = SEC[ln["section"]] + ("r" if ln.get("replay") else "")
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


# --- sections ---------------------------------------------------------------------
# Who holds the camera: Sir David's sections are his nature documentary ("doc"),
# Morgan's are his films ("film"). The instrumental after Verse 4 is the film's
# end credits, and the outro plays after them like a post-credits scene.

ORDER = ("intro", "v1", "v2", "v3", "v4", "credits", "outro", "end")
MODE = {"intro": "doc", "v1": "doc", "v2": "film", "v3": "doc", "v3r": "doc", "v4": "film", "credits": "film",
        "outro": "film", "end": "film"}
RAPPER = {"intro": "david", "v1": "david", "v2": "morgan", "v3": "david", "v3r": "david", "v4": "morgan",
          "outro": "morgan"}
OTHER = {"david": "morgan", "morgan": "david"}


def _sections():
    """A verse starts just before its first word; the credits start after Verse 4's last word."""
    firsts = {s: lines_of(s)[0]["t0"] for s in ("intro", "v1", "v2", "v3", "v4", "outro")}
    starts = {"intro": 0.0, "v1": firsts["v1"] - 1.2, "v2": firsts["v2"] - 0.35, "v3": firsts["v3"] - 0.3,
              "v4": firsts["v4"] - 1.0, "credits": last_word(lines_of("v4")[-1]) + 1.6,
              "outro": firsts["outro"] - 3.0, "end": last_word(LINES[-1]) + 1.6}
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
    if name == "v3r":
        rs = lines_of("v3r")
        return rs[0]["t0"] - 0.12, rs[-1]["t1"]
    for n, a, b in SECTIONS:
        if n == name:
            return a, b
    raise KeyError(name)


def section_end(name):
    return section_bounds(name)[1]


def mode_at(t):
    return MODE[section_at(t)[0]]


# --- punchlines -------------------------------------------------------------------
# Every verse line lands on the other narrator at its last word; these land hard.

KILL_SHOTS = {
    ("v1", 3), ("v1", 7), ("v1", 11), ("v1", 13), ("v1", 15), ("v1", 17),
    ("v2", 3), ("v2", 5), ("v2", 7), ("v2", 9), ("v2", 13), ("v2", 15), ("v2", 17), ("v2", 21),
    ("v3", 1), ("v3", 3), ("v3", 9), ("v3", 13), ("v3", 15), ("v3", 17),
    ("v4", 1), ("v4", 3), ("v4", 5), ("v4", 7), ("v4", 9), ("v4", 11), ("v4", 15), ("v4", 17),
}
VERSES = ("v1", "v2", "v3", "v4")


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


# --- vocal loudness (drives mouths) ---------------------------------------------------

ENV = np.load(DATA / "vocal_env.npy")


def loudness(t):
    return timing.frame_value(ENV, t, FPS)


if __name__ == "__main__":
    print(f"grid: {len(BEATS)} beats, period {PERIOD:.4f}s ({60 / PERIOD:.2f} BPM), first bar {BARS[0]:.3f}s")
    for s in SECTIONS:
        print(f"{s[0]:8s} {s[1]:7.2f} {s[2]:7.2f}")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big")
    for ln in LINES:
        if ln["idx"] == 0:
            b = (ln["t0"] - BARS[0]) / (4 * PERIOD)
            print(f"  {ln['sec']:6s} first line at {ln['t0']:.2f}s = bar {b:.2f}")
