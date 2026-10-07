"""Lyric timing for Play the Video: the automatic alignment plus hand fixes.

    uv run python projects/play-the-video/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it (590 of 601 words matched). The fixes are read off
the vocal stem's loudness, where the transcripts put a word in a pause, on an echo or on the wrong
syllable:

- The last line: "Okay," is sung half a second before the transcripts have it, then a full second
  of nothing, and "Pause." lands on the downbeat at 190.3 s.
- Long words. The aligner takes a word of over 0.9 s for one stretched across a pause and keeps
  its end: "Reactionary." is simply long, and starts at 39.6 s.
- Echoes and doubles. The take sings "A lie!" twice (the line is timed on the first), and "Health"
  once where the sheet ends one bar on it and starts the next: both bars get the one word.
- First words after a held one. "Rats", "Mansion" and "Chat," start where the voice comes back in,
  not where the word before them stops.
"""
from pathlib import Path

from pixelart.audio import align as A

ROOT = Path(__file__).parent
FPS = 24

# line number in the song: (how the line starts, {word: its start}, the line's end if that moves too)
FIXES = {
    0: ("Chat, Asmon", {"Play": 2.36, "it": 2.52}, 2.68),
    2: ("Asmongold?", {"that": 9.52}, None),
    8: ("You skipped", {"to": 25.48, "evolve": 25.70, "bold": 26.64, "swing": 26.86}, 27.08),
    13: ("I'm a revolutionary", {"Reactionary": 39.62}, 40.66),
    15: ("I pick mayors", {}, 46.00),
    17: ('"Out of context!"', {"A": 51.24, "lie": 51.42}, 52.10),
    20: ("Why? Uncle", {"Uncle": 57.36}, None),
    29: ("the swivel", {}, 83.72),
    35: ("who's winning?", {}, 100.37),
    36: ("Mansion for", {"Mansion": 100.49}, None),
    37: ("Porsche for", {"parked": 104.46, "for#2": 104.78}, None),
    41: ("you got flagged", {"by": 115.93, "the": 116.08, "Health": 116.62}, 116.90),
    42: ("Health tip", {"Health": 116.70}, None),
    47: ("now the only", {"can": 132.30}, 132.87),
    48: ("Rats rot", {"Rats": 132.98, "rot": 133.25}, None),
    59: ("look up, Hasan", {"Hasan": 163.07, "I'm": 163.74}, 165.18),
    60: ("Play the video!", {"Play": 165.26}, None),
    62: ("Paid to watch", {"Paid": 170.98}, None),
    65: ("one guy, two", {}, 182.17),
    66: ("The video's finally", {"Chat": 184.83, "applause": 185.39}, 186.21),
    67: ("Okay, I've", {"Okay": 187.11, "I've": 188.44, "got": 188.56, "some": 188.68, "thoughts": 188.80, "on": 189.04,
                         "that": 189.26, "Pause": 190.29}, 190.72),
}


def apply_fixes(timed):
    for i, (start, starts, end) in FIXES.items():
        assert timed[i]["text"].startswith(start), (i, timed[i]["text"])
        A.set_starts(timed[i], starts, end)
    for a, b in zip(timed, timed[1:]):                                   # no line runs into the next
        a["t1"] = min(a["t1"], max(b["t0"], a["words"][-1]["t0"] + 0.05))
        a["words"][-1]["t1"] = min(a["words"][-1]["t1"], a["t1"])


if __name__ == "__main__":
    A.hand_fixed(ROOT, apply_fixes, FPS)
    print(f"{len(FIXES)} lines fixed by hand -> {ROOT / 'data' / 'lyrics_timed.json'}")
