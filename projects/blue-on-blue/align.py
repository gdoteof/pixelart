"""Lyric timing for Blue on Blue: the automatic alignment plus hand fixes.

    uv run python projects/blue-on-blue/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it. The take (yue2-s2) departs from the
lyric sheet in two places, fixed here from the Whisper words of the vocal stem and the mix:

- The hook is sung eight and a half times, not twice (59.2-80.9 s), and it swaps between
  "Newscum" and "Has-been" in its own order; the sixth pass drops "(Thank you!)". Every
  pass is shown as it is sung.
- The outro is three voices: Trump's "Zohran! Handsome!", Mamdani's "Hi! Gavin says hi."
  and Trump's "Who?". The sheet gives them all to Trump on two lines, and the aligner puts
  "Who?" at the end of the song (143 s); the take sings it at 117.7 s.
"""
import json
from pathlib import Path

import numpy as np

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24

THANKS, SCUM, BEEN = "Handsome! (Thank you!)", "Newscum! (Boo!)", "Has-been! (Boo!)"
# (line, [(word, start)], end): the hook as sung, from the vocal stem's word starts
HOOK = [
    (THANKS, [59.24, 59.82, 60.10], 60.50), (SCUM, [60.54, 61.18], 61.70),
    (THANKS, [61.86, 62.38, 62.70], 63.05), (BEEN, [63.08, 63.70], 64.30),
    (THANKS, [64.42, 64.96, 65.26], 65.60), (BEEN, [65.62, 66.26], 66.90),
    (THANKS, [66.96, 67.48, 67.76], 68.15), (SCUM, [68.18, 68.80], 69.40),
    (THANKS, [69.52, 70.06, 70.32], 70.70), (SCUM, [70.74, 71.38], 72.00),
    ("Handsome!", [72.40], 72.90), (SCUM, [72.92, 73.92], 74.50),
    (THANKS, [74.64, 75.18, 75.46], 75.85), (SCUM, [75.86, 76.48], 77.10),
    (THANKS, [77.16, 77.70, 78.00], 78.38), (SCUM, [78.40, 79.02], 79.60),
    (THANKS, [79.72, 80.24, 80.48], 80.90),
]
OUTRO = [
    ("Donald Trump", "Zohran! Handsome!", [113.26, 114.62], 115.70),
    ("Zohran Mamdani", "Hi! Gavin says hi.", [116.00, 116.20, 117.02, 117.44], 117.70),
    ("Donald Trump", "Who?", [117.72], 118.30),
]


def timed_words(text, starts, end):
    """[{"w", "t0", "t1"}] for a line's words from their starts: each runs to the next one's start."""
    words = text.split()
    assert len(words) == len(starts), (text, starts)
    ends = list(starts[1:]) + [end]
    return [{"w": w, "t0": t, "t1": round(min(ends[i], t + A.MAX_WORD), 3)} for i, (w, t) in enumerate(zip(words, starts))]


def make_line(section, speaker, text, starts, end):
    words = timed_words(text, starts, end)
    return {"section": section, "speaker": speaker, "text": text, "t0": words[0]["t0"], "t1": words[-1]["t1"],
            "words": words}


def apply_fixes(timed):
    hook = [ln for ln in timed if ln["section"] == "Hook"]
    outro = [ln for ln in timed if ln["section"] == "Outro"]
    i = timed.index(hook[0])
    sung = [make_line("Hook", hook[0]["speaker"], text, starts, end) for text, starts, end in HOOK]
    timed[i:i + len(hook)] = sung
    j = timed.index(outro[0])
    timed[j:j + len(outro)] = [make_line("Outro", who, text, starts, end) for who, text, starts, end in OUTRO]


def main():
    transcripts = [json.loads((DATA / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")]
    duration = json.loads((DATA / "song.json").read_text())["duration"]
    env = np.load(DATA / "vocal_env.npy")
    timed, report = A.auto((ROOT / "lyrics.txt").read_text(), transcripts, duration, env, FPS)
    apply_fixes(timed)
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    A.print_report(report)
    print(f"hook ({len(HOOK)} chants) and outro ({len(OUTRO)} lines) fixed -> {DATA / 'lyrics_timed.json'}")


if __name__ == "__main__":
    main()
