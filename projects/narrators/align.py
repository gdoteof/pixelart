"""Lyric timing for Attenborough vs. Freeman: the automatic alignment plus hand fixes.

    uv run python projects/narrators/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it. The take departs from the
lyric sheet in two places, fixed here from the vocal stem's Whisper words and
loudness:

- The intro never sings "The other narrated heaven." (the vocal is silent from
  9.75 to 11.0 s), so that line keeps only "One narrated all of life on Earth."
- The Verse 3 repaint sings a couplet twice. After "...take a nap yourself."
  it goes round again as "Seven Worlds, One Planet: seven wonders, all on my
  shelf. / You made one, Morgan, then you had to take a nap yourself." before
  the written "Seven Worlds, One Planet: seven wonders, all of 'em mine." Those
  two extra lines go in with "replay": true (the video shows them as an action
  replay), and the written line is moved to where it is really sung.
"""
import json
from pathlib import Path

import numpy as np

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24

INTRO_LINE = "One narrated all of life on Earth."
INTRO_WORDS = [("One", 7.38), ("narrated", 7.90), ("all", 8.42), ("of", 8.60), ("life", 8.80), ("on", 9.10),
               ("Earth.", 9.30)]
INTRO_END = 9.62

SEVEN_WORLDS = [("Seven", 212.08), ("Worlds,", 212.66), ("One", 212.96), ("Planet:", 213.18), ("seven", 213.58),
                ("wonders,", 213.94), ("all", 214.34), ("of", 214.64), ("'em", 214.80), ("mine.", 214.94)]
SEVEN_END = 215.40

REPLAY = [
    ("Seven Worlds, One Planet: seven wonders, all on my shelf.",
     [("Seven", 205.64), ("Worlds,", 206.22), ("One", 206.68), ("Planet:", 206.96), ("seven", 207.46),
      ("wonders,", 207.78), ("all", 208.26), ("on", 208.52), ("my", 208.62), ("shelf.", 208.74)], 209.00),
    ("You made one, Morgan, then you had to take a nap yourself.",
     [("You", 209.02), ("made", 209.32), ("one,", 209.52), ("Morgan,", 209.76), ("then", 210.36), ("you", 210.56),
      ("had", 210.72), ("to", 210.94), ("take", 211.06), ("a", 211.36), ("nap", 211.50), ("yourself.", 211.76)],
     212.00),
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
    set_words(by_text["One narrated all of life on Earth. The other narrated heaven."], INTRO_WORDS, INTRO_END,
              INTRO_LINE)
    seven = by_text["Seven Worlds, One Planet: seven wonders, all of 'em mine."]
    set_words(seven, SEVEN_WORLDS, SEVEN_END)
    at = timed.index(seven)
    for k, (text, words, end) in enumerate(REPLAY):
        line = {"section": seven["section"], "speaker": seven["speaker"], "text": text, "replay": True}
        set_words(line, words, end)
        timed.insert(at + k, line)


def main():
    transcripts = [json.loads((DATA / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")]
    duration = json.loads((DATA / "song.json").read_text())["duration"]
    env = np.load(DATA / "vocal_env.npy")
    timed, report = A.auto((ROOT / "lyrics.txt").read_text(), transcripts, duration, env, FPS)
    apply_fixes(timed)
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    A.print_report(report)
    print(f"intro trimmed, Verse 3 re-timed, {len(REPLAY)} replay lines added -> {DATA / 'lyrics_timed.json'}")


if __name__ == "__main__":
    main()
