"""A song's timeline for a lyric video: a fixed beat grid, the timed lyric lines, and the sections.

Inputs are a project's data/ files (pixelart.song.pick and pixelart.audio.analyze write them):

    song.json          {"duration": seconds, ...}
    beat_this.json     {"beats": [...], "downbeats": [...]}
    lyrics_timed.json  [{"section", "speaker", "text", "t0", "t1", "words": [{"w", "t0", "t1"}, ...]}, ...]

Before a take is picked there is no timing yet; `draft_lines` lays the lyric sheet out on an even grid
so the video can be built and previewed in the meantime. `Song` loads whichever there is.
"""
import json
import math
from pathlib import Path

import numpy as np

from pixelart import lyrics, timing


def fit_grid(beats, downbeats, duration, bpm_guess):
    """One fixed beat period fitted to every tracked beat: (beat times, bar starts, period).

    Songs from the models hold a steady tempo, and a fixed grid doesn't flinch when the tracker
    switches between quarters and eighths. The bar phase is the one most downbeats agree with.
    """
    beats, downbeats = np.asarray(beats, float), np.asarray(downbeats, float)
    guess = 60.0 / bpm_guess

    def spread(per):
        ang = 2 * np.pi * beats / per
        return np.hypot(np.cos(ang).mean(), np.sin(ang).mean()), np.arctan2(np.sin(ang).mean(), np.cos(ang).mean())

    pers = np.arange(guess * 0.97, guess * 1.03, 0.00002)
    per = pers[int(np.argmax([spread(p)[0] for p in pers]))]
    t0 = (spread(per)[1] / (2 * np.pi)) * per % per
    grid = t0 + per * np.arange(0, int((duration - t0) / per) + 3)
    votes = np.zeros(4)
    for d in downbeats:
        votes[int(round((d - t0) / per)) % 4] += 1
    ph = int(np.argmax(votes))
    return grid, grid[ph::4], per


def load_lines(raw, sec_map, who_map):
    """Timed lines with short names: each gets sec (sec_map[section]), idx (its number within the
    section), gi (its number in the song) and who (who_map[speaker])."""
    counters, out = {}, []
    for gi, ln in enumerate(raw):
        sec = sec_map[ln["section"]]
        idx = counters.get(sec, 0)
        counters[sec] = idx + 1
        out.append({**ln, "sec": sec, "idx": idx, "gi": gi, "who": who_map[ln["speaker"]]})
    return out


def last_word(ln):
    """When the last word of a line is sung (its t1 can stretch over the gap that follows)."""
    return ln["words"][-1]["t0"]


def section_spans(lines, order, duration, lead=0.9, gap=0.3, tail=1.6):
    """[(name, start, end), ...] for the sections in `order`, whose last entry is an end card with no
    lines. A section starts `lead` seconds before its first word (but not before `gap` after the last
    word before it); the first starts at 0, and the end card `tail` seconds after the last word."""
    def lines_of(s):
        return [ln for ln in lines if ln["sec"] == s]

    starts = {order[0]: 0.0}
    for s in order[1:-1]:
        before = [ln for ln in lines if order.index(ln["sec"]) < order.index(s)]
        starts[s] = max(lines_of(s)[0]["t0"] - lead, last_word(before[-1]) + gap)
    starts[order[-1]] = last_word(lines[-1]) + tail
    return [(a, starts[a], starts[b] if b else duration + 1) for a, b in zip(order, order[1:] + ("",))]


def cut_spans(lines, order, duration, lead=0.12, tail=1.6):
    """`section_spans` for a video that cuts to a new frame with each section. A take sings its verses
    back to back, so the cut lands on the new section's first word, as its caption comes up (`lead`
    before it). Where the song leaves a gap the section starts in it: once the line before is over, and
    no more than 0.9 s before its own first word."""
    starts = {order[0]: 0.0}
    for sec in order[1:-1]:
        first = next(ln for ln in lines if ln["sec"] == sec)
        before = lines[first["gi"] - 1]
        starts[sec] = max(first["t0"] - 0.9, min(before["t1"] + 0.05, first["t0"] - lead))
    starts[order[-1]] = last_word(lines[-1]) + tail
    return [(a, starts[a], starts[b] if b else duration + 1) for a, b in zip(order, order[1:] + ("",))]


def draft_lines(text, bpm, start=4.0, gap_bars=2):
    """Stand-in timing for a lyric sheet before there is a song: one bar per line, words spread evenly
    over its first three beats, `gap_bars` bars between sections. Same shape as lyrics_timed.json."""
    bar = 4 * 60.0 / bpm
    t, out = start, []
    for sec in lyrics.sections(text):
        for line in sec["lines"]:
            words = line.split()
            step = 0.75 * bar / len(words)
            ws = [{"w": w, "t0": round(t + i * step, 3), "t1": round(t + (i + 1) * step, 3)} for i, w in enumerate(words)]
            out.append({"section": sec["section"], "speaker": sec["speaker"], "text": line,
                        "t0": ws[0]["t0"], "t1": ws[-1]["t1"], "words": ws})
            t += bar
        t += gap_bars * bar
    return out


def number_lines(raw, order, who_map):
    """Timed lines with short names, like `load_lines`, for a sheet that repeats a section name: each
    run of lines under one section name takes the next name in `order`, so a hook that is sung twice
    is "hook1" and "hook2". Two headers in a row with the same section name are one run."""
    out, counters, k, prev = [], {}, -1, None
    for gi, ln in enumerate(raw):
        if ln["section"] != prev:
            k, prev = k + 1, ln["section"]
        sec = order[k]
        idx = counters.get(sec, 0)
        counters[sec] = idx + 1
        out.append({**ln, "sec": sec, "idx": idx, "gi": gi, "who": who_map[ln["speaker"]]})
    return out


class Song:
    """A project's song as its renderer needs it: the beat grid, the timed lyric lines, the sections
    and the vocal loudness, read from data/. Until a take is picked and analysed (no
    data/lyrics_timed.json), the lyric sheet is laid out on an even grid at `bpm`, so the video can
    be built and previewed.

    `order` names the sections in song order (see `number_lines`), ending with the end card, which
    has no lines. `who` maps the sheet's speakers to short names.
    """

    def __init__(self, root, bpm, order, who, fps=24):
        root = Path(root)
        data = root / "data"
        self.fps, self.order = fps, tuple(order)
        self.draft = not (data / "lyrics_timed.json").exists()
        if self.draft:
            raw = draft_lines((root / "lyrics.txt").read_text(), bpm)
            self.meta = {}
            self.duration = raw[-1]["t1"] + 8.0
            self.period = 60.0 / bpm
            self.beats = np.arange(0.0, self.duration + 4 * self.period, self.period)
            self.bars = self.beats[::4]
            self.env = None
        else:
            raw = json.loads((data / "lyrics_timed.json").read_text())
            self.meta = json.loads((data / "song.json").read_text())
            self.duration = self.meta["duration"]
            tracked = json.loads((data / "beat_this.json").read_text())
            self.beats, self.bars, self.period = fit_grid(tracked["beats"], tracked["downbeats"], self.duration, bpm)
            self.env = np.load(data / "vocal_env.npy")
        clock = timing.BeatClock(self.beats, self.bars)
        self.beat_info, self.since_beat, self.bar_info = clock.beat_info, clock.since_beat, clock.bar_info
        self.lines = number_lines(raw, self.order, who)
        self.sections = section_spans(self.lines, self.order, self.duration)

    def next_beat(self, t):
        i = np.searchsorted(self.beats, t)
        return float(self.beats[min(i, len(self.beats) - 1)])

    def lines_of(self, sec):
        return [ln for ln in self.lines if ln["sec"] == sec]

    def line(self, sec, idx):
        return next(ln for ln in self.lines if ln["sec"] == sec and ln["idx"] == idx)

    def line_at(self, t, lead=0.12, hold=0.9):
        return timing.line_at(self.lines, t, lead, hold)

    def section_at(self, t):
        """(name, start, end) of the section playing at t."""
        for name, a, b in self.sections:
            if a <= t < b:
                return name, a, b
        return self.sections[-1] if t >= self.sections[-1][1] else self.sections[0]

    def section_bounds(self, name):
        for n, a, b in self.sections:
            if n == name:
                return a, b
        raise KeyError(name)

    def section_start(self, name):
        return self.section_bounds(name)[0]

    def section_end(self, name):
        return self.section_bounds(name)[1]

    def loudness(self, t):
        """The vocals' loudness in [0, 1] at t, to drive mouths."""
        if self.env is not None:
            return timing.frame_value(self.env, t, self.fps)
        ln = self.line_at(t, lead=0.0, hold=0.0)                # draft: a syllable-ish pulse while a line is sung
        if not ln or not ln["t0"] <= t <= ln["t1"]:
            return 0.0
        return 0.45 + 0.45 * math.sin(t * 2 * math.pi * 4.3)
