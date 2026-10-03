"""When things happen: the beat grid, sections, lyric lines, punchlines and vocal loudness.

All times are seconds into audio/song.wav. Until a take is picked and analysed (no data/lyrics_timed.json
yet), the lyric sheet is laid out on an even grid at the song's tempo so the video can be previewed.
"""
import json
import math

import numpy as np

from engine import ROOT
from pixelart import songtime, timing

FPS = 24
DATA = ROOT / "data"
BPM_GUESS = 92
DRAFT = not (DATA / "lyrics_timed.json").exists()

SEC = {"Intro": "intro", "Verse 1": "v1", "Verse 2": "v2", "Hook": "hook", "Verse 3": "v3", "Verse 4": "v4",
       "Outro": "outro"}
WHO = {"Gavin Newsom": "newsom", "Zohran Mamdani": "mamdani", "Live Chat": "chat", "Donald Trump": "trump"}
ORDER = ("intro", "v1", "v2", "hook", "v3", "v4", "outro", "end")
RAPPER = {"intro": "newsom", "v1": "newsom", "v2": "mamdani", "v3": "newsom", "v4": "mamdani"}
OTHER = {"newsom": "mamdani", "mamdani": "newsom"}
VERSES = ("v1", "v2", "v3", "v4")

if DRAFT:
    RAW = songtime.draft_lines((ROOT / "lyrics.txt").read_text(), BPM_GUESS)
    DURATION = RAW[-1]["t1"] + 8.0
    PERIOD = 60.0 / BPM_GUESS
    BEATS = np.arange(0.0, DURATION + 4 * PERIOD, PERIOD)
    BARS = BEATS[::4]
    ENV = None
else:
    RAW = json.loads((DATA / "lyrics_timed.json").read_text())
    DURATION = json.loads((DATA / "song.json").read_text())["duration"]
    _beats = json.loads((DATA / "beat_this.json").read_text())
    BEATS, BARS, PERIOD = songtime.fit_grid(_beats["beats"], _beats["downbeats"], DURATION, BPM_GUESS)
    ENV = np.load(DATA / "vocal_env.npy")

CLOCK = timing.BeatClock(BEATS, BARS)
beat_info, since_beat, bar_info = CLOCK.beat_info, CLOCK.since_beat, CLOCK.bar_info


def next_beat(t):
    i = np.searchsorted(BEATS, t)
    return float(BEATS[min(i, len(BEATS) - 1)])


# --- lyric lines ----------------------------------------------------------------------------

LINES = songtime.load_lines(RAW, SEC, WHO)
last_word = songtime.last_word
word_index = timing.word_index
word_time = timing.word_time


def lines_of(sec):
    return [ln for ln in LINES if ln["sec"] == sec]


def line(sec, idx):
    return next(ln for ln in LINES if ln["sec"] == sec and ln["idx"] == idx)


def line_at(t, lead=0.12, hold=0.9):
    return timing.line_at(LINES, t, lead, hold)


# --- sections ---------------------------------------------------------------------------------

SECTIONS = songtime.section_spans(LINES, ORDER, DURATION)


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


def section_start(name):
    return section_bounds(name)[0]


def section_end(name):
    return section_bounds(name)[1]


# --- punchlines -------------------------------------------------------------------------------
# Every verse line lands on the other man at its last word; these land hard.

KILL_SHOTS = {("v1", i) for i in (1, 2, 5, 8, 9)} | {("v2", i) for i in (1, 4, 6, 7, 8)} \
    | {("v3", i) for i in (2, 4, 5, 7)} | {("v4", i) for i in (1, 2, 4)}


def _hits():
    return [{"t": last_word(ln) + 0.04, "target": OTHER[ln["who"]], "attacker": ln["who"],
             "big": (ln["sec"], ln["idx"]) in KILL_SHOTS, "line": ln}
            for ln in LINES if ln["sec"] in VERSES]


HITS = _hits()


def last_hit(t, target=None, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window and (target is None or h["target"] == target)]
    return past[-1] if past else None


# --- vocal loudness (drives the mouths) -------------------------------------------------------------

def loudness(t):
    if ENV is not None:
        return timing.frame_value(ENV, t, FPS)
    ln = line_at(t, lead=0.0, hold=0.0)                     # draft: a syllable-ish pulse while a line is sung
    if not ln or not ln["t0"] <= t <= ln["t1"]:
        return 0.0
    return 0.45 + 0.45 * math.sin(t * 2 * math.pi * 4.3)


if __name__ == "__main__":
    print(("DRAFT timing (no song analysed yet); " if DRAFT else "")
          + f"{len(BEATS)} beats, period {PERIOD:.4f}s ({60 / PERIOD:.2f} BPM), duration {DURATION:.1f}s")
    for s in SECTIONS:
        print(f"{s[0]:8s} {s[1]:7.2f} {s[2]:7.2f}")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big")
