"""Render-time clocks: where in the beat/bar we are, and which lyric is being sung.

Inputs come from the offline analysis in pixelart.audio: a beat/downbeat list
(pixelart.audio.beats) and timed lyric lines (pixelart.audio.align), where each
line is {"text", "t0", "t1", "words": [{"w", "t0", "t1"}, ...], ...}.
All times are seconds into the song.
"""
import re
from bisect import bisect_right

import numpy as np


class BeatClock:
    """A tracked beat grid. Tracked beats (not a fixed BPM) survive tempo drift and splices."""

    def __init__(self, beats, downbeats=()):
        self.beats = np.asarray(beats, dtype=float)
        self.downbeats = np.asarray(downbeats, dtype=float)

    def beat_info(self, t):
        """(beat index, phase in [0, 1), beat length) at time t, extrapolating at the ends."""
        beats = self.beats
        i = bisect_right(beats, t) - 1
        if i < 0:
            per = beats[1] - beats[0]
            k = int(np.floor((t - beats[0]) / per))
            return k, (t - beats[0]) / per - k, per
        if i >= len(beats) - 1:
            per = beats[-1] - beats[-2]
            k = int(np.floor((t - beats[-1]) / per))
            return len(beats) - 1 + k, (t - beats[-1]) / per - k, per
        per = beats[i + 1] - beats[i]
        return i, (t - beats[i]) / per, per

    def since_beat(self, t):
        """Seconds since the most recent beat."""
        _, ph, per = self.beat_info(t)
        return ph * per

    def bar_info(self, t):
        """(bar index, beat-within-bar) using the tracked downbeats; bar -1 before the first."""
        i = bisect_right(self.downbeats, t) - 1
        if i < 0:
            return -1, 0
        b0 = bisect_right(self.beats, self.downbeats[i] - 0.02)
        b = bisect_right(self.beats, t) - 1
        return i, max(0, b - b0)


def line_at(lines, t, lead=0.12, hold=0.9):
    """The lyric line on screen at t: from just before its first word until the
    next line takes over (or `hold` seconds after its last word)."""
    cur = None
    for i, ln in enumerate(lines):
        if ln["t0"] - lead <= t:
            nxt = lines[i + 1]["t0"] - lead if i + 1 < len(lines) else 1e9
            if t < min(nxt, ln["t1"] + hold):
                cur = ln
        else:
            break
    return cur


def word_index(line, t):
    """Index of the word being sung (len(words) once the line is done, -1 before)."""
    ws = line["words"]
    if t < ws[0]["t0"]:
        return -1
    for i, w in enumerate(ws):
        nxt = ws[i + 1]["t0"] if i + 1 < len(ws) else w["t1"]
        if t < max(nxt, w["t0"] + 0.05):
            return i
    return len(ws)


def word_time(line, pattern, which="t0"):
    """Start (or end) time of the first word in `line` matching a regex."""
    for w in line["words"]:
        if re.search(pattern, w["w"], re.I):
            return w[which]
    raise KeyError(f"{pattern!r} not in {line['text']!r}")


def frame_value(env, t, fps):
    """Sample a per-video-frame array (e.g. a loudness envelope) at time t, clamped to its ends."""
    f = int(round(t * fps))
    return float(env[min(max(f, 0), len(env) - 1)])
