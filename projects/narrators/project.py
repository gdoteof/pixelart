"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
import json
from pathlib import Path

from video import FPS, label, render_frame  # noqa: F401

ROOT = Path(__file__).parent
SONG = ROOT / "audio" / "song.wav"
AUDIO = SONG if SONG.exists() else None
# data/song.json is written by `python -m pixelart.song.pick`; lower END to cut a click at the tail.
_song = ROOT / "data" / "song.json"
END = json.loads(_song.read_text())["duration"] if _song.exists() else 8.0
OUTPUT = ROOT / "narrators.mp4"
