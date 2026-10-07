"""Join the clips into one reel, a title card before each: projects/style-reel/style-reel.mp4.

    uv run python projects/style-reel/combine.py

Uses the frames reel.py left in build/frames/, so render the styles first; a style with no frames is left out.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT.parent.parent)]

import script as S  # noqa: E402
from page import STYLES  # noqa: E402
from pixelart.ffmpeg import FFMPEG, decode_stereo, encode  # noqa: E402

BUILD = ROOT / "build"
CARD = 1.0                                  # seconds of title card before each clip
SR = 48000
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"


def card(i, n, style, path):
    im = Image.new("RGB", (S.W, S.H), (14, 14, 20))
    d = ImageDraw.Draw(im)
    d.rectangle((160, 372, 172, 688), fill=(96, 226, 48))
    d.text((212, 366), f"{i} / {n}", font=ImageFont.truetype(INTER.format("Bold"), 40), fill=(96, 226, 48))
    d.text((206, 420), style["name"], font=ImageFont.truetype(INTER.format("Black"), 150), fill=(244, 242, 236))
    d.text((212, 624), style["base"], font=ImageFont.truetype(INTER.format("Medium"), 50), fill=(150, 150, 168))
    im.save(path)


def main():
    styles = [s for s in STYLES if (BUILD / "frames" / s["id"] / f"f{S.FRAMES - 1:04d}.png").exists()]
    cards = BUILD / "cards"
    cards.mkdir(exist_ok=True)
    bar = decode_stereo(BUILD / "audio.wav", SR)[:round(S.FRAMES / S.FPS * SR)]
    quiet = np.zeros((round(CARD * SR), 2), bar.dtype)
    encode(np.concatenate([part for _ in styles for part in (quiet, bar)]), SR, BUILD / "reel.wav")

    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y"]
    chain = []
    for i, s in enumerate(styles):
        card(i + 1, len(styles), s, cards / f"{s['id']}.png")
        cmd += ["-loop", "1", "-framerate", str(S.FPS), "-t", str(CARD), "-i", str(cards / f"{s['id']}.png")]
        cmd += ["-framerate", str(S.FPS), "-i", str(BUILD / "frames" / s["id"] / "f%04d.png")]
        chain += [f"[{2 * i}:v]format=yuv420p,setsar=1[c{i}]", f"[{2 * i + 1}:v]format=yuv420p,setsar=1[v{i}]"]
    joined = "".join(f"[c{i}][v{i}]" for i in range(len(styles)))
    chain.append(f"{joined}concat=n={2 * len(styles)}:v=1:a=0[v]")
    out = ROOT / "style-reel.mp4"
    cmd += ["-i", str(BUILD / "reel.wav"), "-filter_complex", ";".join(chain), "-map", "[v]", "-map", f"{2 * len(styles)}:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    secs = len(styles) * (CARD + S.FRAMES / S.FPS)
    print(f"{out}: {len(styles)} styles ({', '.join(s['id'] for s in styles)}), {secs:.0f}s, {out.stat().st_size / 1e6:.0f} MB")


if __name__ == "__main__":
    main()
