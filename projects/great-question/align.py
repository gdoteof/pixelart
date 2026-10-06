"""Lyric timing for Great Question: the automatic alignment plus hand fixes.

    uv run python projects/great-question/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it. The fixes, from the vocal stem's onsets:

- The intro is written as it is heard once `pixelart.audio.bleep` has cut it: the first line stops at
  "PewDie" and the second at "is", each with a buzzer. The two sung "clap"s in Verse 2 are handclaps.
  A word in asterisks is a sound, not a sung word: the video shows it in another colour.
- Verse 1 opens with the name said fast ("PewDiePie:") at 10.2 s, not spread over the buzzer's gap.
- Whisper misheard three bars ("a Qwen in a wig", "Pew-D-I-Y", "Ali Baba's") and put their words late.
- The last word is held: "ChatGPT" runs to 189.1 s.
"""
import json
from pathlib import Path

import numpy as np

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24

# line number in the song: (how the line starts, its words if they change, each word's start, the line's end)
FIXES = {
    0: ("How's it going", "How's it going, bros? My name is PewDie- *BZZT*",
        [0.02, 0.20, 0.36, 0.68, 2.40, 2.52, 2.66, 2.92, 3.27], 3.80),
    1: ("I appealed it", "I appealed it! I'm back, bros! My name is- *BZZT*",
        [4.94, 5.04, 5.56, 6.36, 6.60, 6.96, 7.40, 7.60, 7.84, 8.02], 8.72),
    2: ("Pew. Die. Pie", None, [10.24, 10.38, 10.58, 10.80, 11.20, 11.58, 11.74, 11.96, 12.16], 12.42),
    13: ("a Qwen in a wig", None, [38.68, 38.74, 38.90, 39.00, 39.14, 39.38, 39.76, 39.92], 40.56),
    15: ("flat-packed", None, [42.98, 43.94, 44.10, 44.32, 45.30], 45.92),
    16: ("Mine's Ali", None, [46.00, 46.56, 46.92, 47.54, 47.64, 47.82, 47.90, 48.16], 48.60),
    18: ("Meme review", "Meme review! *CLAP* *CLAP* Elon was my guest;",
         [50.96, 51.60, 52.20, 52.52, 52.73, 52.84, 53.02, 53.22], 53.44),
    33: ("Want that as a table", None, [89.18, 89.42, 89.60, 89.80, 89.92, 90.24, 90.40, 90.52, 90.70, 91.32], 91.60),
    67: ("Ajax, my own", None, [178.76, 179.36, 179.96, 180.26, 181.48, 181.60, 181.78, 181.94, 182.14], 182.42),
    68: ("Great question! I'm", None, [183.80, 184.04, 185.74, 185.86, 186.40], 189.10),
}


def retime(line, text, starts, end):
    """Give a line new word starts (and new words, if `text` is given): each word runs to the next one's
    start, the last to `end`, and none longer than a held note."""
    words = text.split() if text else [w["w"] for w in line["words"]]
    assert len(words) == len(starts), (line["text"], words, starts)
    ends = list(starts[1:]) + [end]
    last = len(words) - 1
    line["words"] = [{"w": w, "t0": t, "t1": round(e if i == last else min(e, t + A.MAX_WORD), 3)}
                     for i, (w, t, e) in enumerate(zip(words, starts, ends))]
    line["t0"], line["t1"] = starts[0], end
    if text:
        line["text"] = text


def apply_fixes(timed):
    for i, (start, text, starts, end) in FIXES.items():
        assert timed[i]["text"].startswith(start), (i, timed[i]["text"])
        retime(timed[i], text, starts, end)
    for a, b in zip(timed, timed[1:]):                                   # no line runs into the next
        a["t1"] = min(a["t1"], max(b["t0"], a["words"][-1]["t0"] + 0.05))
        a["words"][-1]["t1"] = min(a["words"][-1]["t1"], a["t1"])


def main():
    transcripts = [json.loads((DATA / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")]
    duration = json.loads((DATA / "song.json").read_text())["duration"]
    env = np.load(DATA / "vocal_env.npy")
    timed, report = A.auto((ROOT / "lyrics.txt").read_text(), transcripts, duration, env, FPS)
    apply_fixes(timed)
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    A.print_report(report)
    print(f"{len(FIXES)} lines fixed by hand -> {DATA / 'lyrics_timed.json'}")


if __name__ == "__main__":
    main()
