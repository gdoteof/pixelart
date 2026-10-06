"""Locating ffmpeg, and decoding and writing audio through it.

Set FFMPEG to override the binary. A snap-packaged ffmpeg can only read and
write under $HOME, so keep songs and build output inside the repo, not /tmp.
"""
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np

FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def decode_mono(path, sr):
    """The whole file as mono float32 samples at `sr` Hz."""
    raw = subprocess.run([FFMPEG, "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "1",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def decode_stereo(path, sr):
    """The whole file as float32 stereo samples at `sr` Hz, shape (n, 2)."""
    raw = subprocess.run([FFMPEG, "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "2",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def encode(samples, sr, path):
    """Write float32 stereo samples as 24-bit audio: FLAC for a .flac path, else PCM (what `pick` writes)."""
    codec = ["flac", "-sample_fmt", "s32", "-bits_per_raw_sample", "24"] if Path(path).suffix == ".flac" else ["pcm_s24le"]
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2",
                    "-ar", str(sr), "-i", "-", "-c:a", *codec, str(path)],
                   input=np.asarray(samples, np.float32).tobytes(), check=True)
