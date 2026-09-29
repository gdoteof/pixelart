"""Render a project to mp4: python -m pixelart.render PROJECT [--workers N] [--chunk F] [--end S] [--out PATH] [--fresh]

Frames are rendered by a process pool in chunks; each chunk is piped as raw RGB
into its own ffmpeg/x264 segment under PROJECT/build/segments (finished
segments are kept, so an interrupted render resumes; pass --fresh after code
changes). The segments are then concatenated and muxed with the project's audio.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from multiprocessing import Pool

from pixelart.ffmpeg import FFMPEG
from pixelart.project import load

X264 = ["-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "16",
        "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-color_range", "tv", "-threads", "2"]


def seg_path(p, i):
    return p.build / "segments" / f"seg_{i:04d}.mp4"


def render_chunk(job):
    root, i, f0, f1 = job
    p = load(root)
    out = seg_path(p, i)
    tmp = out.with_suffix(".tmp.mp4")
    w, h = p.size
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(p.fps), "-i", "-", *X264, str(tmp)]
    t_start = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for f in range(f0, f1):
            img = p.render_frame(f / p.fps)
            if img.size != p.size or img.mode != "RGB":
                img = img.convert("RGB").resize(p.size)
            proc.stdin.write(img.tobytes())
    except BaseException:
        proc.stdin.close()
        proc.wait()
        tmp.unlink(missing_ok=True)
        raise
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed on segment {i}")
    tmp.rename(out)
    return i, f1 - f0, time.time() - t_start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 4))
    ap.add_argument("--chunk", type=int, default=48)
    ap.add_argument("--end", type=float, help="seconds to render (default: the project's END)")
    ap.add_argument("--out", help="default: the project's OUTPUT")
    ap.add_argument("--fresh", action="store_true", help="discard finished segments first")
    args = ap.parse_args()

    p = load(args.project)
    seg_dir = p.build / "segments"
    if args.fresh and seg_dir.exists():
        shutil.rmtree(seg_dir)
    seg_dir.mkdir(parents=True, exist_ok=True)
    for tmp in seg_dir.glob("*.tmp.mp4"):
        tmp.unlink()
    end = p.end if args.end is None else args.end
    n = int(round(end * p.fps))
    jobs = [(str(p.root), i, f0, min(n, f0 + args.chunk)) for i, f0 in enumerate(range(0, n, args.chunk))]
    todo = [j for j in jobs if not seg_path(p, j[1]).exists()]
    print(f"{n} frames in {len(jobs)} segments, {len(todo)} to render with {args.workers} workers",
          flush=True)

    t0, done = time.time(), 0
    with Pool(args.workers) as pool:
        for i, nf, dt in pool.imap_unordered(render_chunk, todo):
            done += 1
            el = time.time() - t0
            print(f"segment {i:4d}: {nf} frames in {dt:5.1f}s  [{done}/{len(todo)}, {el:6.0f}s elapsed]",
                  flush=True)

    listing = seg_dir / "concat.txt"
    listing.write_text("".join(f"file '{seg_path(p, j[1]).name}'\n" for j in jobs))
    dur = n / p.fps
    out = args.out or str(p.output)
    cmd = [FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing)]
    if p.audio:
        cmd += ["-i", str(p.audio), "-map", "0:v", "-map", "1:a",
                "-af", f"afade=t=out:st={dur - 0.08:.3f}:d=0.08", "-c:a", "aac", "-b:a", "320k"]
    cmd += ["-c:v", "copy", "-t", f"{dur:.3f}", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"wrote {out} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
