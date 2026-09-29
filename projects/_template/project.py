"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
from pathlib import Path

from video import render_frame  # noqa: F401

ROOT = Path(__file__).parent
FPS = 24
END = 8.0             # seconds; set to the song length (minus any tail click) once there is a song
AUDIO = None          # ROOT / "audio" / "song.wav"
OUTPUT = ROOT / "video.mp4"
