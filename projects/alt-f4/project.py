"""ALT-F4: a 16-bit fighting-game rap battle (see README.md). Loaded by the pixelart tools."""
from pathlib import Path

import timeline as TL
from video import render_frame  # noqa: F401

ROOT = Path(__file__).parent
FPS = TL.FPS
END = 199.75          # the song has a click at 199.76 s; stop just before it
AUDIO = ROOT / "audio" / "song.wav"
OUTPUT = ROOT / "alt-f4.mp4"


def label(t):
    ln = TL.line_at(t)
    return ln["text"] if ln else ""
