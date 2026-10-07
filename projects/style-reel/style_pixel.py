"""The baseline: the same bar as it is in the finished video, cut out of play-the-video.mp4."""
import subprocess

from PIL import Image

import script as S
from pixelart.ffmpeg import FFMPEG

NAME = "Pixel art"
SRC = S.ROOT.parent / "play-the-video" / "play-the-video.mp4"
CACHE = S.ROOT / "build" / "pixel"


def _extract():
    CACHE.mkdir(parents=True, exist_ok=True)
    first = round(S.T0 * S.FPS)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{first / S.FPS:.4f}", "-i", str(SRC),
                    "-frames:v", str(S.FRAMES + 1), str(CACHE / "f%04d.png")], check=True)


if not (CACHE / f"f{S.FRAMES:04d}.png").exists():      # once, on import: the frames render in parallel
    _extract()


def frame(t):
    return Image.open(CACHE / f"f{S.frame_no(t) + 1:04d}.png").convert("RGB")
