"""Time the ALT-F4 lyrics: align the Whisper transcripts onto lyrics.txt.

    python align.py   (reads data/*.whisper.json, writes data/lyrics_timed.json)

The generic aligner is pixelart.audio.align; this file holds what is specific
to this song: its section layout, number spellings, the hand-timed hook and
intro fixes. Whisper mishears names ("rag-dax", "Carpenter's"), which the
fuzzy alignment absorbs.
"""
import json
import re
from pathlib import Path

from pixelart.audio import align as A

ROOT = Path(__file__).parent
DATA = ROOT / "data"
LYRICS = ROOT / "lyrics.txt"

SPEAKERS = {"Intro": "host", "Verse 1": "sam", "Verse 2": "dario", "Hook": "crowd",
            "Verse 3": "sam", "Verse 4": "dario", "Outro": "host"}
NUMBERS = {"52": "fiftytwo", "69": "sixtynine", "70": "seventy", "17": "seventeen",
           "f4": "f4"}


def norm(word):
    w = A.norm(word)
    return NUMBERS.get(w, w)


def tokens_of(word):
    # "Alt-F4" -> ["alt", "f4"], but "fifty-two" -> ["fiftytwo"] to match "52"
    if re.fullmatch(r"(?i)fifty-two|sixty-nine", word.strip(".,!?\"'")):
        return [norm(word.replace("-", ""))]
    return A.tokens_of(word, norm)


# Where each section sits in the recording (seconds), found from the transcripts
# and the vocal-stem loudness. The hook is a chant Whisper can't hear, so its
# lines are timed by hand from bar-by-bar transcription instead.
WINDOWS = {"Intro": (1.4, 15.5), "Verse 1": (24.9, 57.5), "Verse 2": (57.4, 88.2),
           "Verse 3": (108.0, 140.6), "Verse 4": (140.4, 172.5), "Outro": (172.5, 183.1)}

CHANT = "Code red! Red line!"
HANDS = "Wouldn't hold hands, so they're throwing hands tonight!"
HOOK_LINES = [  # (text, t0, t1, section)
    (CHANT, 88.30, 90.85, "Hook"), (CHANT, 90.95, 93.50, "Hook"), (HANDS, 93.60, 98.30, "Hook"),
    (CHANT, 98.85, 101.45, "Hook"), (CHANT, 101.50, 104.10, "Hook"), (HANDS, 104.15, 108.20, "Hook"),
    (CHANT, 182.95, 185.70, "Reprise"), (CHANT, 185.75, 188.50, "Reprise"),
    (HANDS, 189.20, 192.90, "Reprise"), (CHANT, 193.00, 194.60, "Reprise"),
]


# Whisper stretches words across the intro's pauses; these onsets are read off
# the vocal-stem loudness instead.
INTRO_FIXES = {"Yo!": (1.58, 1.85), "They": (3.04, 3.2), "wouldn't": (4.42, 4.66),
               "So": (7.71, 7.84), "tonight": (7.84, 8.28), "they're": (8.36, 8.62),
               "throwing": (8.70, 8.92), "hands!": (8.92, 9.4)}


def fix_intro(timed):
    for line in timed:
        if line["section"] != "Intro":
            continue
        for w in line["words"]:
            if w["w"] in INTRO_FIXES:
                w["t0"], w["t1"] = INTRO_FIXES[w["w"]]
        line["t0"], line["t1"] = line["words"][0]["t0"], line["words"][-1]["t1"]


def main():
    transcripts = [json.loads((DATA / n).read_text())
                   for n in ("vocals.whisper.json", "song.whisper.json")]
    lines = A.parse_lyrics(LYRICS.read_text(), SPEAKERS)
    timed, got, total = [], 0, 0
    for section, (t_from, t_to) in WINDOWS.items():
        sec_lines = [l for l in lines if l["section"] == section]
        out, matched, n = A.build(transcripts, sec_lines, t_from, t_to, tokens_of)
        timed += out
        got, total = got + matched, total + n
    for text, t0, t1, section in HOOK_LINES:
        timed.append({"section": section, "speaker": "crowd", "text": text, "t0": t0, "t1": t1,
                      "words": A.even_words(text, t0, t1, norm)})
    fix_intro(timed)
    timed.sort(key=lambda l: l["t0"])
    print(f"matched {got}/{total} sung lyric words")
    for line in timed:
        print(f"{line['t0']:7.2f}-{line['t1']:7.2f} {line['speaker']:5s} {line['text']}")
    (DATA / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))


if __name__ == "__main__":
    main()
