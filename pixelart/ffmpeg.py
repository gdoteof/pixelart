"""Locating ffmpeg and decoding audio through it.

Set FFMPEG to override the binary. A snap-packaged ffmpeg can only read and
write under $HOME, so keep songs and build output inside the repo, not /tmp.
"""
import os
import shutil
import subprocess

import numpy as np

FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def decode_mono(path, sr):
    """The whole file as mono float32 samples at `sr` Hz."""
    raw = subprocess.run([FFMPEG, "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)
