"""Render one style of the reel.

    uv run --with skia-python python projects/style-reel/reel.py flat             # build/clips/flat.mp4
    uv run --with skia-python python projects/style-reel/reel.py flat --sheet     # twelve frames on one sheet
    uv run --with skia-python python projects/style-reel/reel.py flat --sheet 69.4 72.7 73.3
    uv run --with skia-python python projects/style-reel/reel.py flat --frame 69.4            # one, full size
    uv run --with skia-python python projects/style-reel/reel.py flat --frame 69.4 --crop 0 0 960 540

Times are seconds of the song (script.T0 to script.T1). A clip is 1920x1080 at 24 frames a second with the
bar's audio; build/web/ gets a 720p copy for the page.
"""
import argparse
import importlib
import subprocess
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT.parent.parent)]

import script as S  # noqa: E402
from pixelart.ffmpeg import FFMPEG  # noqa: E402

SHEET = [67.25, 67.95, 68.45, 68.98, 69.5, 69.9, 70.5, 71.2, 72.0, 72.75, 73.25, 74.2]
POSTER = 73.4                               # the frame the page shows for a clip before it plays
BUILD = ROOT / "build"
_style = None


def load(name):
    global _style
    _style = importlib.import_module(f"style_{name}")
    return _style


def picture(t):
    """The style's frame at t as an RGB image of the full size."""
    img = _style.frame(t)
    if not isinstance(img, Image.Image):
        img = Image.fromarray(np.asarray(img)[..., :3])
    img = img.convert("RGB")
    return img if img.size == (S.W, S.H) else img.resize((S.W, S.H), Image.LANCZOS)


def _write(job):
    i, path = job
    picture(S.T0 + i / S.FPS).save(path, compress_level=1)
    return i


def render(name, workers):
    frames = BUILD / "frames" / name
    frames.mkdir(parents=True, exist_ok=True)
    for old in frames.glob("*.png"):
        old.unlink()
    start = time.time()
    jobs = [(i, frames / f"f{i:04d}.png") for i in range(S.FRAMES)]
    with get_context("fork").Pool(workers) as pool:
        for _ in pool.imap_unordered(_write, jobs, chunksize=2):
            pass
    took = time.time() - start
    (BUILD / "clips").mkdir(exist_ok=True)
    (BUILD / "web").mkdir(exist_ok=True)
    clip, web = BUILD / "clips" / f"{name}.mp4", BUILD / "web" / f"{name}.mp4"
    src = ["-framerate", str(S.FPS), "-i", str(frames / "f%04d.png"), "-i", str(BUILD / "audio.wav")]
    common = ["-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart"]
    quiet = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y"]
    subprocess.run([*quiet, *src, "-c:v", "libx264", "-preset", "slow", "-crf", "15", *common, str(clip)], check=True)
    subprocess.run([*quiet, *src, "-vf", "scale=1280:720:flags=lanczos", "-c:v", "libx264", "-preset", "slow",
                    "-crf", str(getattr(_style, "WEB_CRF", 21)), *common, str(web)], check=True)
    poster = Image.open(frames / f"f{S.frame_no(POSTER):04d}.png").convert("RGB").resize((960, 540), Image.LANCZOS)
    poster.save(BUILD / "web" / f"{name}.jpg", quality=86)
    print(f"{name}: {S.FRAMES} frames in {took:.1f}s ({took / S.FRAMES * workers:.2f}s a frame per worker) -> "
          f"{clip} ({clip.stat().st_size / 1e6:.1f} MB), {web} ({web.stat().st_size / 1e6:.1f} MB)")


def sheet(name, times, workers, cols=4):
    with get_context("fork").Pool(min(workers, len(times))) as pool:
        frames = pool.map(picture, times)
    tw, th = 640, 360
    rows = -(-len(frames) // cols)
    out = Image.new("RGB", (cols * tw, rows * th), (20, 20, 24))
    draw = ImageDraw.Draw(out)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 18)
    for k, (t, f) in enumerate(zip(times, frames)):
        x, y = k % cols * tw, k // cols * th
        out.paste(f.resize((tw, th), Image.LANCZOS), (x, y))
        draw.rectangle((x, y, x + 74, y + 24), fill=(0, 0, 0))
        draw.text((x + 5, y + 2), f"{t:.2f}", font=font, fill=(255, 255, 0))
    path = BUILD / "sheets" / f"{name}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path)


def one(name, t, crop):
    img = picture(t)
    if crop:
        img = img.crop(tuple(crop))
        k = min(1920 / img.width, 1080 / img.height)
        img = img.resize((int(img.width * k), int(img.height * k)), Image.LANCZOS)
    path = BUILD / "sheets" / f"{name}_{t:.2f}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("style")
    ap.add_argument("--sheet", nargs="*", type=float, metavar="T", help="a contact sheet (of these times)")
    ap.add_argument("--frame", type=float, metavar="T", help="one frame at full size")
    ap.add_argument("--crop", nargs=4, type=int, metavar=("X0", "Y0", "X1", "Y1"), help="with --frame: this part, enlarged")
    ap.add_argument("--workers", type=int, default=24)
    args = ap.parse_args()
    load(args.style)
    if args.frame is not None:
        one(args.style, args.frame, args.crop)
    elif args.sheet is not None:
        sheet(args.style, args.sheet or SHEET, args.workers)
    else:
        render(args.style, args.workers)


if __name__ == "__main__":
    main()
