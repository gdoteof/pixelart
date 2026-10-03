"""A song's timeline for a lyric video: a fixed beat grid, the timed lyric lines, and the sections.

Inputs are a project's data/ files (pixelart.song.pick and pixelart.audio.analyze write them):

    song.json          {"duration": seconds, ...}
    beat_this.json     {"beats": [...], "downbeats": [...]}
    lyrics_timed.json  [{"section", "speaker", "text", "t0", "t1", "words": [{"w", "t0", "t1"}, ...]}, ...]

Before a take is picked there is no timing yet; `draft_lines` lays the lyric sheet out on an even grid
so the video can be built and previewed in the meantime.
"""
import numpy as np

from pixelart import lyrics


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
