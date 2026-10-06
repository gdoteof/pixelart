"""When things happen: the beat grid, sections, lyric lines, punchlines, the cuts and vocal loudness.

All times are seconds into audio/song.wav. Until a take is picked and analysed, pixelart.songtime lays the
lyric sheet out on an even grid at the song's tempo, so the video can be previewed.
"""
from engine import ROOT
from pixelart import songtime, timing

FPS = 24
BPM = 94
ORDER = ("intro", "v1", "v2", "hook1", "v3", "v4", "hook2", "outro", "end")
WHO = {"PewDiePie": "felix", "Sam Altman": "sam", "ChatGPT": "gpt", "Ajax": "ajax"}
RAPPER = {"intro": "felix", "v1": "sam", "v2": "felix", "hook1": "gpt", "v3": "sam", "v4": "felix", "hook2": "gpt"}
OTHER = {"felix": "sam", "sam": "felix"}
VERSES = ("v1", "v2", "v3", "v4")
HOOKS = ("hook1", "hook2")

SONG = songtime.Song(ROOT, BPM, ORDER, WHO, FPS)
LINES, DURATION, DRAFT = SONG.lines, SONG.duration, SONG.draft
beat_info, since_beat, bar_info, next_beat = SONG.beat_info, SONG.since_beat, SONG.bar_info, SONG.next_beat
lines_of, line, line_at = SONG.lines_of, SONG.line, SONG.line_at
section_at, section_bounds, section_start, section_end = (SONG.section_at, SONG.section_bounds, SONG.section_start,
                                                          SONG.section_end)
last_word = songtime.last_word
word_index = timing.word_index

# What pixelart.audio.bleep did to the take: the buzzers over the intro's two bans (and a third, over the
# last one, on the bar after the last word), and the handclaps.
CUTS = SONG.meta.get("cuts", [])
BUZZ = [c["t0"] for c in CUTS if c["sound"] == "buzzer"]
CLAPS = [c["t0"] + 0.02 for c in CUTS if c["sound"] == "clap"]
LAST_WORD_END = LINES[-1]["t1"]              # the last word is held
END_CARD = LAST_WORD_END + 0.25


def is_sound(word):
    """A word in asterisks is a sound laid over the song (a buzzer, a clap), not a sung word."""
    return word.startswith("*") and word.endswith("*")


# --- punchlines -------------------------------------------------------------------------------
# Every verse line lands on the other man at its last word; these land hard.

KILL_SHOTS = {("v1", i) for i in (3, 7, 9, 13)} | {("v2", i) for i in (1, 3, 5, 9, 13)} \
    | {("v3", i) for i in (1, 3, 5, 12)} | {("v4", i) for i in (1, 3, 5, 7, 11)}


def _hits():
    return [{"t": last_word(ln) + 0.04, "target": OTHER[ln["who"]], "attacker": ln["who"],
             "big": (ln["sec"], ln["idx"]) in KILL_SHOTS, "line": ln}
            for ln in LINES if ln["sec"] in VERSES]


HITS = _hits()


def last_hit(t, target=None, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window and (target is None or h["target"] == target)]
    return past[-1] if past else None


def loudness(t):
    """The vocals' loudness in [0, 1], to drive mouths: silent where the vocals were cut out."""
    if any(c["t0"] <= t < c["t1"] for c in CUTS):
        return 0.0
    return SONG.loudness(t)


if __name__ == "__main__":
    print(("DRAFT timing (no song analysed yet); " if DRAFT else "")
          + f"{len(SONG.beats)} beats, period {SONG.period:.4f}s ({60 / SONG.period:.2f} BPM), duration {DURATION:.1f}s")
    for s in SONG.sections:
        print(f"{s[0]:8s} {s[1]:7.2f} {s[2]:7.2f}  {len(lines_of(s[0]))} lines")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big; buzzers", BUZZ, "claps", CLAPS)
