"""When things happen: the beat grid, sections, lyric lines, punchlines and vocal loudness.

All times are seconds into audio/song.wav. Until a take is picked and analysed, pixelart.songtime lays the
lyric sheet out on an even grid at the song's tempo, so the video can be previewed.
"""
from engine import ROOT
from pixelart import songtime, timing

FPS = 24
BPM = 90          # the style asked for 92; the take plays at 90
ORDER = ("v1", "v2", "v3", "v4", "outro", "end")
WHO = {"Emiru": "emiru", "Maya": "maya", "Both": "both"}
# What is on screen: one woman's stream, her webcam full screen, or a place the two of them share.
VIEW = {"v1": "emiru", "v2": "maya", "v3": "emiru", "v4": "gate", "outro": "shop", "end": "shop"}
WOMEN = ("emiru", "maya")
OTHER = {"emiru": "maya", "maya": "emiru"}
VERSES = ("v1", "v2", "v3", "v4")
CHAT = {"emiru": "emiru", "maya": "maya", "gate": "pair", "shop": "pair"}    # whose chat a view shows

LEAD = 0.12         # a line's caption and its gag come up this long before its first word: and so does a cut

SONG = songtime.Song(ROOT, BPM, ORDER, WHO, FPS)
LINES, DURATION, DRAFT = SONG.lines, SONG.duration, SONG.draft
if not DRAFT:       # the take sings its verses back to back: cut on the new verse's first word
    SONG.sections = songtime.cut_spans(LINES, ORDER, DURATION, LEAD)
beat_info, since_beat, bar_info, next_beat = SONG.beat_info, SONG.since_beat, SONG.bar_info, SONG.next_beat
lines_of, line, line_at = SONG.lines_of, SONG.line, SONG.line_at
section_at, section_bounds, section_start, section_end = (SONG.section_at, SONG.section_bounds, SONG.section_start,
                                                          SONG.section_end)
last_word = songtime.last_word
word_index = timing.word_index
loudness = SONG.loudness
LAST_WORD_END = LINES[-1]["t1"]
END_CARD = section_start("end")


# --- punchlines -------------------------------------------------------------------------------
# The bar that closes each run of rhymes lands on its last word, and chat answers it. Nobody on screen
# is the target: whoever isn't rapping laughs. BIG are the ones a chat loses it over.

PUNCH = {"v1": (1, 4, 8, 10, 12, 14), "v2": (1, 3, 6, 8, 10, 12, 14), "v3": (1, 3, 5, 7, 9, 11, 13),
         "v4": (1, 3, 5, 7, 9, 11, 12, 13, 15)}
BIG = {"v1": (1, 8, 10, 12, 14), "v2": (1, 3, 6, 10, 12, 14), "v3": (1, 5, 7, 9, 11, 13), "v4": (1, 3, 7, 11, 12, 13, 15)}


def _hits():
    return [{"t": last_word(ln) + 0.04, "attacker": CHAT[VIEW[ln["sec"]]], "who": ln["who"],
             "big": ln["idx"] in BIG[ln["sec"]], "line": ln}
            for ln in LINES if ln["idx"] in PUNCH.get(ln["sec"], ())]


HITS = _hits()


def last_hit(t, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window]
    return past[-1] if past else None


if __name__ == "__main__":
    print(("DRAFT timing (no song analysed yet); " if DRAFT else "")
          + f"{len(SONG.beats)} beats, period {SONG.period:.4f}s ({60 / SONG.period:.2f} BPM), duration {DURATION:.1f}s")
    for s in SONG.sections:
        print(f"{s[0]:8s} {s[1]:7.2f} {s[2]:7.2f}  {len(lines_of(s[0]))} lines")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big; the end card comes up at",
          round(END_CARD, 2))
