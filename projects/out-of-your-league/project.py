"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
from pathlib import Path

from video import FPS, label, render_frame  # noqa: F401

ROOT = Path(__file__).parent
SONG = ROOT / "audio" / "song.wav"
AUDIO = SONG if SONG.exists() else None
# The last word ends at 168.8 s and the take plays on for another 18 s: stop here and fade the beat out.
END = 173.0
FADE = 3.0
OUTPUT = ROOT / "out-of-your-league.mp4"
