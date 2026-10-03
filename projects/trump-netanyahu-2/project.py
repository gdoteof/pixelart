"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
FPS = 24
SONG = ROOT / "audio" / "song.wav"
AUDIO = SONG if SONG.exists() else None
# data/song.json is written by `python -m pixelart.song.pick`; lower END to cut a click at the tail.
_song = ROOT / "data" / "song.json"
END = json.loads(_song.read_text())["duration"] if _song.exists() else 205.0
OUTPUT = ROOT / "trump-vs-netanyahu-round-2.mp4"


# The renderer needs the song analysis in data/ (or falls back to draft timing), so it loads on first
# use: `analyze` can load this project before that analysis exists.
def render_frame(t):
    import video
    return video.render_frame(t)


def label(t):
    import video
    return video.label(t)
