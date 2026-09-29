"""When things happen: the beat clock, sections, lyric lines and punchline hits.

All times are seconds into audio/song.wav. Beats come from the beat_this tracker
(the Suno render is spliced at ~85.5 s, so a fixed-tempo grid drifts), the
lyric timings from Whisper aligned onto the real lyrics (align.py).
"""
import json
from functools import lru_cache

import numpy as np

from engine import ROOT
from pixelart import timing
from pixelart.audio.envelope import loudness_envelope

FPS = 24
DURATION = 199.89
DATA = ROOT / "data"
SONG = ROOT / "audio" / "song.wav"
VOCALS = ROOT / "build" / "stems" / "htdemucs" / "song" / "vocals.wav"

_beats = json.loads((DATA / "beat_this.json").read_text())
BEATS = np.array(_beats["beats"])
# The tracker marks a spurious downbeat inside the splice and two at the tail.
DOWNBEATS = np.array([b for b in _beats["downbeats"] if abs(b - 87.2) > 0.05 and b < 194.0])
CLOCK = timing.BeatClock(BEATS, DOWNBEATS)
beat_info = CLOCK.beat_info
since_beat = CLOCK.since_beat
bar_info = CLOCK.bar_info


# --- sections ---------------------------------------------------------------

SECTIONS = [
    ("cold", 0.0, 1.45),
    ("intro", 1.45, 15.45),
    ("hype", 15.45, 25.55),
    ("v1", 25.55, 57.45),
    ("v2", 57.45, 88.2),
    ("hook", 88.2, 108.15),
    ("v3", 108.15, 140.55),
    ("v4", 140.55, 172.6),
    ("outro", 172.6, 182.92),
    ("reprise", 182.92, 194.6),
    ("end", 194.6, DURATION + 1),
]
SECTION_OF_LYRIC = {"Intro": "intro", "Verse 1": "v1", "Verse 2": "v2", "Hook": "hook",
                    "Verse 3": "v3", "Verse 4": "v4", "Outro": "outro", "Reprise": "reprise"}
VERSE_NO = {"v1": "1", "v2": "2", "v3": "3", "v4": "4"}


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


# --- lyric lines ------------------------------------------------------------

def _load_lines():
    raw = json.loads((DATA / "lyrics_timed.json").read_text())
    counters = {}
    lines = []
    for gi, ln in enumerate(raw):
        sec = SECTION_OF_LYRIC[ln["section"]]
        idx = counters.get(sec, 0)
        counters[sec] = idx + 1
        lines.append({**ln, "sec": sec, "idx": idx, "gi": gi})
    return lines


LINES = _load_lines()


def lines_of(sec):
    return [ln for ln in LINES if ln["sec"] == sec]


def line_at(t, lead=0.12, hold=0.9):
    return timing.line_at(LINES, t, lead, hold)


word_index = timing.word_index
word_time = timing.word_time


# --- punchline hits ---------------------------------------------------------

KILL_SHOTS = {("v1", 3), ("v1", 11), ("v2", 2), ("v2", 3), ("v2", 11), ("v3", 3), ("v3", 5),
              ("v3", 11), ("v4", 2), ("v4", 3), ("v4", 7), ("v4", 11)}
TARGET = {"v1": "dario", "v3": "dario", "v2": "sam", "v4": "sam"}
FINAL_KO = 182.95


def _build_hits():
    hits = []
    for who in ("sam", "dario"):
        verses = [v for v, tgt in TARGET.items() if tgt == who]
        entries = []
        for ln in LINES:
            if ln["sec"] in verses:
                big = (ln["sec"], ln["idx"]) in KILL_SHOTS
                weight = 2.4 if big else (1.4 if ln["idx"] % 2 else 1.0)
                entries.append((ln["words"][-1]["t0"] + 0.04, weight, big, ln))
        total = sum(e[1] for e in entries)
        for t, wgt, big, ln in entries:
            hits.append({"t": t, "target": who, "dmg": 0.9 * wgt / total, "big": big,
                         "attacker": "dario" if who == "sam" else "sam", "line": ln["gi"]})
        hits.append({"t": FINAL_KO, "target": who, "dmg": 0.1 + 1e-6, "big": True,
                     "attacker": "both", "line": None})
    return sorted(hits, key=lambda h: h["t"])


HITS = _build_hits()


def hp(who, t):
    return max(0.0, 1.0 - sum(h["dmg"] for h in HITS if h["target"] == who and h["t"] <= t))


def hp_recent(who, t, hold=0.7, drain=0.45):
    """The red 'recent damage' chunk: lingers, then drains down to the real HP."""
    now = hp(who, t)
    past = [h for h in HITS if h["target"] == who and h["t"] <= t]
    if not past:
        return now
    last = past[-1]
    age = t - last["t"]
    before = hp(who, last["t"] - 1e-4)
    if age < hold:
        return before
    if age < hold + drain:
        return before + (now - before) * (age - hold) / drain
    return now


def last_hit(t, target=None, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window
            and (target is None or h["target"] == target)]
    return past[-1] if past else None


def combo(t, attacker):
    """Consecutive hits landed by `attacker` in the current verse up to t."""
    sec, _, _ = section_at(t)
    if TARGET.get(sec) is None or (attacker == "sam") != (TARGET[sec] == "dario"):
        return 0
    a, _ = section_bounds(sec)
    return sum(1 for h in HITS if h["attacker"] == attacker and a <= h["t"] <= t)


# --- vocal loudness (drives mouths) ----------------------------------------

@lru_cache(maxsize=1)
def vocal_env():
    """Per-video-frame vocal loudness in [0, 1] from the Demucs vocal stem (cached in data/)."""
    path = DATA / "vocal_env.npy"
    if path.exists():
        return np.load(path)
    lvl = loudness_envelope(VOCALS, FPS, DURATION)
    np.save(path, lvl)
    return lvl


def loudness(t):
    return timing.frame_value(vocal_env(), t, FPS)


if __name__ == "__main__":
    print("beats", len(BEATS), "downbeats", len(DOWNBEATS))
    for sec in ("v1", "v2", "v3", "v4"):
        ls = lines_of(sec)
        print(sec, len(ls), "lines", f"{ls[0]['t0']:.2f}-{ls[-1]['t1']:.2f}")
    for who in ("sam", "dario"):
        print(who, "hp at 57/88/140/172/183:",
              [round(hp(who, x), 2) for x in (57.5, 88.2, 140.6, 172.6, 183.0)])
    env = vocal_env()
    print("vocal env frames", len(env), "mean", env.mean().round(3))
