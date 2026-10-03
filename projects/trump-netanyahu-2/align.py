"""Lyric timing for Trump vs. Netanyahu Round 2: the automatic alignment plus hand fixes.

    uv run python projects/trump-netanyahu-2/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it. The take departs from the
lyric sheet in two places, fixed here from the Whisper words of the mix and the
vocal envelope:

- After the intro's last word (23.4 s) the band plays alone for eleven seconds,
  and Verse 1 comes in at 35.1 s. Whisper misses the start of the verse in the
  vocal stem, so the aligner pins "Bibi" to the end of the intro and squeezes
  the next three lines. Their words are timed by hand from the mix.
- The outro sings its last line twice, dropping an item each time: "No wars, no
  trial, and he still got a pardon" (180.3-183.9 s), then "No wars, no
  drones..." (186.0-190.6 s). Both passes are shown as they are sung.
"""
import json
from pathlib import Path

import numpy as np

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24

VERSE1 = [
    ("Bibi, like the BB gun: little, plastic, loud;",
     [("Bibi,", 35.08), ("like", 35.30), ("the", 35.40), ("BB", 35.62), ("gun:", 35.96), ("little,", 36.22),
      ("plastic,", 36.46), ("loud;", 36.86)], 37.1),
    ("I supply your ammo; you only shoot when you're allowed.",
     [("I", 37.16), ("supply", 37.38), ("your", 37.66), ("ammo;", 37.92), ("you", 38.32), ("only", 38.54),
      ("shoot", 38.76), ("when", 39.08), ("you're", 39.26), ("allowed.", 39.42)], 39.7),
    ("The whole UN saw a cartoon bomb you drew;",
     [("The", 39.72), ("whole", 40.17), ("UN", 40.34), ("saw", 40.76), ("a", 40.92), ("cartoon", 41.10),
      ("bomb", 41.62), ("you", 41.90), ("drew;", 42.05)], 42.32),
    ("Acme failed you again, Wile E. Netanyahu.",
     [("Acme", 42.36), ("failed", 42.84), ("you", 43.10), ("again,", 43.28), ("Wile", 43.78), ("E.", 43.92),
      ("Netanyahu.", 44.10)], 44.9),
]
OUTRO = [
    ("No wars, no trial, and he still got a pardon.",
     [("No", 180.29), ("wars,", 180.48), ("no", 180.98), ("trial,", 181.42), ("and", 182.06), ("he", 182.36),
      ("still", 182.60), ("got", 182.86), ("a", 183.12), ("pardon.", 183.30)], 183.9),
    ("No wars, no drones, and he still got a pardon.",
     [("No", 186.04), ("wars,", 186.33), ("no", 186.62), ("drones,", 188.00), ("and", 188.55), ("he", 189.08),
      ("still", 189.34), ("got", 189.58), ("a", 189.82), ("pardon.", 189.95)], 190.6),
]


def timed_words(words, end):
    """[{"w", "t0", "t1"}] from (word, start) pairs: each word runs to the next one's start."""
    starts = [t for _, t in words] + [end]
    return [{"w": w, "t0": t, "t1": round(min(starts[i + 1], t + A.MAX_WORD), 3)} for i, (w, t) in enumerate(words)]


def set_words(line, words, end, text=None):
    line["words"] = timed_words(words, end)
    line["t0"], line["t1"] = line["words"][0]["t0"], line["words"][-1]["t1"]
    if text:
        line["text"] = text


def apply_fixes(timed):
    by_text = {ln["text"]: ln for ln in timed}
    for text, words, end in VERSE1:
        set_words(by_text[text], words, end)
    last = by_text["No wars, no trial, no drones, and he still got a pardon."]
    text, words, end = OUTRO[0]
    set_words(last, words, end, text)
    again = {"section": last["section"], "speaker": last["speaker"], "text": OUTRO[1][0]}
    set_words(again, *OUTRO[1][1:])
    timed.insert(timed.index(last) + 1, again)


def main():
    transcripts = [json.loads((DATA / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")]
    duration = json.loads((DATA / "song.json").read_text())["duration"]
    env = np.load(DATA / "vocal_env.npy")
    timed, report = A.auto((ROOT / "lyrics.txt").read_text(), transcripts, duration, env, FPS)
    apply_fixes(timed)
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    A.print_report(report)
    print(f"Verse 1's first {len(VERSE1)} lines and the outro's repeat fixed -> {DATA / 'lyrics_timed.json'}")


if __name__ == "__main__":
    main()
