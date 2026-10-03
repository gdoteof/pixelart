"""Lyric timing for Pardon Me: the automatic alignment plus hand fixes.

    uv run python projects/pardon-me/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it. The take departs from the
lyric sheet in a few places, fixed here from the Whisper words of the vocal
stem and the mix, and the vocal loudness:

- The intro opens on a short burst (0.0-0.55 s) that Whisper hears as "In the",
  then "General Assembly" at 1.6 s: there is no "Order! Order!" to show, so the
  first line is "In the General Assembly!".
- The hook chants "Pardon me, pardon me" where the sheet has "Pardon me? Pardon
  you!", and after its last line the delegates go round again: "Pardon me!"
  seven more times (116.7-122.1 s). Those go in as two more hook lines.
- Verse 4 sings "Seventeen percent on friendship?" twice before "That's the Art
  of the Steal."
"""
import json
from pathlib import Path

import numpy as np

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24

INTRO = ("In the General Assembly!", [("In", 0.0), ("the", 0.36), ("General", 1.62), ("Assembly!", 2.08)], 2.92)
HOOK = [
    ("Pardon me? Pardon me!", [("Pardon", 106.78), ("me?", 107.14), ("Pardon", 107.42), ("me!", 107.78)], 108.3),
    ("Pardon me? Pardon me!", [("Pardon", 109.24), ("me?", 109.60), ("Pardon", 110.00), ("me!", 110.32)], 110.9),
]
CHANT = [
    ("Pardon me! Pardon me! Pardon me! Pardon me!",
     [("Pardon", 116.74), ("me!", 117.30), ("Pardon", 117.64), ("me!", 117.98), ("Pardon", 118.34), ("me!", 118.64),
      ("Pardon", 118.98), ("me!", 119.26)], 119.5),
    ("Pardon me! Pardon me! Pardon me!",
     [("Pardon", 119.60), ("me!", 119.94), ("Pardon", 120.94), ("me!", 121.16), ("Pardon", 121.54), ("me!", 121.80)],
     122.3),
]
STEAL = ("Seventeen percent on friendship? Seventeen percent on friendship? That's the Art of the Steal.",
         [("Seventeen", 202.30), ("percent", 202.82), ("on", 203.10), ("friendship?", 203.50),
          ("Seventeen", 204.00), ("percent", 204.75), ("on", 205.30), ("friendship?", 205.70),
          ("That's", 206.08), ("the", 206.62), ("Art", 206.74), ("of", 206.98), ("the", 207.10), ("Steal.", 207.18)],
         207.45)


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
    text, words, end = INTRO
    set_words(by_text["Order! Order in the General Assembly!"], words, end, text)
    hooks = [ln for ln in timed if ln["section"] == "Hook"]
    for ln, (text, words, end) in zip(hooks, HOOK):
        set_words(ln, words, end, text)
    at = timed.index(hooks[-1]) + 1
    for k, (text, words, end) in enumerate(CHANT):
        line = {"section": "Hook", "speaker": hooks[-1]["speaker"], "text": text, "chant": True}
        set_words(line, words, end)
        timed.insert(at + k, line)
    text, words, end = STEAL
    set_words(by_text["Seventeen percent on friendship? That's the Art of the Steal."], words, end, text)


def main():
    transcripts = [json.loads((DATA / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")]
    duration = json.loads((DATA / "song.json").read_text())["duration"]
    env = np.load(DATA / "vocal_env.npy")
    timed, report = A.auto((ROOT / "lyrics.txt").read_text(), transcripts, duration, env, FPS)
    apply_fixes(timed)
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    A.print_report(report)
    print(f"intro, hook and Verse 4 fixed, {len(CHANT)} chant lines added -> {DATA / 'lyrics_timed.json'}")


if __name__ == "__main__":
    main()
