"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
from pathlib import Path

ROOT = Path(__file__).parent
FPS = 24
SONG = ROOT / "audio" / "song.wav"
AUDIO = SONG if SONG.exists() else None
# The last word ("ChatGPT.", held) ends at 189.1 s, the last ban lands on the next bar and the backing plays
# on to 194.9 s: fade out under the call notes.
END = 194.9
FADE = 2.6
OUTPUT = ROOT / "great-question.mp4"


# The renderer needs the song analysis in data/ (or falls back to draft timing), so it loads on first
# use: `analyze` can load this project before that analysis exists.
def render_frame(t):
    import video
    return video.render_frame(t)


def label(t):
    import video
    return video.label(t)
