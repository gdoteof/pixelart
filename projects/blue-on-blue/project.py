"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
from pathlib import Path

ROOT = Path(__file__).parent
FPS = 24
SONG = ROOT / "audio" / "song.wav"
AUDIO = SONG if SONG.exists() else None
# The take's last line ("Who?") ends at 118.3 s, then the chant runs on to 137 s: end under the end card.
END = 124.0
FADE = 3.5
OUTPUT = ROOT / "blue-on-blue.mp4"


# The renderer needs the song analysis in data/ (or falls back to draft timing), so it loads on first
# use: `analyze` can load this project before that analysis exists.
def render_frame(t):
    import video
    return video.render_frame(t)


def label(t):
    import video
    return video.label(t)
