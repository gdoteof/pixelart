"""Lyric timing for Two Georges: the automatic alignment plus a few hand fixes.

    uv run python projects/two-georges/align.py     # -> data/lyrics_timed.json

`pixelart.audio.align.auto` does nearly all of it (whole sheet in one pass,
word starts snapped out of pauses onto the vocal onsets). The fixes below are
words it matched to the wrong place, read off the vocal-stem loudness.
"""
import json
from pathlib import Path

import numpy as np

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24

# (section, line index within the section, word index) -> (t0, t1)
FIXES = {
    # Whisper heard the reverb tail as "I'm done. I'm done." twice more and the
    # aligner took the last one; the King says it once, at 66.7 s.
    ("Verse 1", 15, 10): (66.66, 66.92),
    ("Verse 1", 15, 11): (66.95, 67.30),
}


def apply_fixes(timed):
    seen = {}
    for line in timed:
        idx = seen[line["section"]] = seen.get(line["section"], -1) + 1
        for wi, w in enumerate(line["words"]):
            if (line["section"], idx, wi) in FIXES:
                w["t0"], w["t1"] = FIXES[(line["section"], idx, wi)]
        line["t0"], line["t1"] = line["words"][0]["t0"], line["words"][-1]["t1"]


def main():
    transcripts = [json.loads((DATA / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")]
    duration = json.loads((DATA / "song.json").read_text())["duration"]
    env = np.load(DATA / "vocal_env.npy")
    timed, report = A.auto((ROOT / "lyrics.txt").read_text(), transcripts, duration, env, FPS)
    apply_fixes(timed)
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    A.print_report(report)
    print(f"{len(FIXES)} words fixed by hand -> {DATA / 'lyrics_timed.json'}")


if __name__ == "__main__":
    main()
