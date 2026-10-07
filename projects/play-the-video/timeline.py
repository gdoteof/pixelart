"""When things happen: the beat grid, sections, lyric lines, punchlines and vocal loudness.

All times are seconds into audio/song.wav. Until a take is picked and analysed, pixelart.songtime lays the
lyric sheet out on an even grid at the song's tempo, so the video can be previewed.
"""
import project
from engine import ROOT
from pixelart import songtime, timing

FPS = 24
BPM = 88
ORDER = ("intro", "v1", "v2", "hook1", "v3", "v4", "hook2", "outro", "end")
WHO = {"Hasan": "hasan", "Asmongold": "asmon", "Chat": "chat", "Both": "both"}
# Whose stream is on screen: his webcam, full screen. "split" is both, side by side.
VIEW = {"intro": "hasan", "v1": "hasan", "v2": "asmon", "hook1": "split", "v3": "hasan", "v4": "asmon",
        "hook2": "split", "outro": "split", "end": "split"}
OTHER = {"hasan": "asmon", "asmon": "hasan"}
MEN = ("hasan", "asmon")
VERSES = ("v1", "v2", "v3", "v4")
HOOKS = ("hook1", "hook2")

LEAD = 0.12         # a line's caption and its gag come up this long before its first word: and so does a cut

SONG = songtime.Song(ROOT, BPM, ORDER, WHO, FPS)
LINES, DURATION, DRAFT = SONG.lines, SONG.duration, SONG.draft


def _sections():
    """Where each section starts. The take sings its verses back to back, so the cut to the next stream
    lands on the new rapper's first word, as its caption comes up. Where the song leaves a gap the section
    starts in it: once the last word before it is over, and no more than 0.9 s before its own first."""
    starts = {ORDER[0]: 0.0}
    for sec in ORDER[1:-1]:
        first = SONG.lines_of(sec)[0]
        before = LINES[first["gi"] - 1]
        starts[sec] = max(first["t0"] - 0.9, min(before["t1"] + 0.05, first["t0"] - LEAD))
    starts[ORDER[-1]] = songtime.last_word(LINES[-1]) + 1.6
    return [(a, starts[a], starts[b] if b else DURATION + 1) for a, b in zip(ORDER, ORDER[1:] + ("",))]


if not DRAFT:
    SONG.sections = _sections()
beat_info, since_beat, bar_info, next_beat = SONG.beat_info, SONG.since_beat, SONG.bar_info, SONG.next_beat
lines_of, line, line_at = SONG.lines_of, SONG.line, SONG.line_at
section_at, section_bounds, section_start, section_end = (SONG.section_at, SONG.section_bounds, SONG.section_start,
                                                          SONG.section_end)
last_word = songtime.last_word
word_index = timing.word_index
loudness = SONG.loudness
LAST_WORD_END = LINES[-1]["t1"]
MAO_AT = section_start("v3")        # from his second verse on, Hasan is in the Mao suit he brags about in its first bar
# The last word is "Pause.", and the song does: the sound stops dead there and the picture with it.
STOP = LAST_WORD_END + 0.2 if DRAFT else getattr(project, "AUDIO_END", LAST_WORD_END + 0.2)
END_CARD = STOP + 0.9               # the title comes up, in the quiet


# --- punchlines -------------------------------------------------------------------------------
# A verse is couplets: the second bar of each lands on its last word. Most land on the other man, and
# KILL_SHOTS land hard. The bars in OWN_GOALS are the rapper's own confessions and brags: his chat
# laughs, but the man in the window has nothing to flinch at.

KILL_SHOTS = {("v1", i) for i in (5, 7, 11, 13)} | {("v2", i) for i in (3, 7, 11, 13)} \
    | {("v3", i) for i in (5, 7, 11)} | {("v4", i) for i in (5, 7, 11)}
OWN_GOALS = {("v2", 9), ("v3", 1), ("v3", 3), ("v4", 1)}


def _hits():
    return [{"t": last_word(ln) + 0.04, "target": None if (ln["sec"], ln["idx"]) in OWN_GOALS else OTHER[ln["who"]],
             "attacker": ln["who"], "big": (ln["sec"], ln["idx"]) in KILL_SHOTS, "line": ln}
            for ln in LINES if ln["sec"] in VERSES and ln["idx"] % 2 == 1]


HITS = _hits()


def last_hit(t, target=None, window=1e9):
    past = [h for h in HITS if h["t"] <= t and t - h["t"] < window and (target is None or h["target"] == target)]
    return past[-1] if past else None


if __name__ == "__main__":
    print(("DRAFT timing (no song analysed yet); " if DRAFT else "")
          + f"{len(SONG.beats)} beats, period {SONG.period:.4f}s ({60 / SONG.period:.2f} BPM), duration {DURATION:.1f}s")
    for s in SONG.sections:
        print(f"{s[0]:8s} {s[1]:7.2f} {s[2]:7.2f}  {len(lines_of(s[0]))} lines")
    print(f"the song stops at {STOP:.2f}, the title comes up at {END_CARD:.2f}, the video ends at {project.END:.2f}")
    print(len(LINES), "lines,", len(HITS), "hits,", sum(h["big"] for h in HITS), "big")
