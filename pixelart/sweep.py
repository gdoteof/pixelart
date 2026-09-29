"""Render every frame without encoding, to catch exceptions and find slow frames.

    python -m pixelart.sweep PROJECT [--workers N]

Exits non-zero if any frame raised; prints one traceback per distinct error.
"""
import argparse
import os
import sys
import time
import traceback
from multiprocessing import Pool

from pixelart.project import load


def work(job):
    root, frames = job
    p = load(root)
    errs, slow = [], (0.0, None)
    for f in frames:
        t = f / p.fps
        a = time.time()
        try:
            img = p.render_frame(t)
            assert img.size == p.size and img.mode == "RGB", (img.size, img.mode)
        except Exception:
            errs.append((t, traceback.format_exc(limit=4)))
        dt = time.time() - a
        if dt > slow[0]:
            slow = (dt, t)
    return errs, slow, len(frames)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 4))
    args = ap.parse_args()
    p = load(args.project)
    n = p.frames
    jobs = [(str(p.root), list(range(i, n, 64))) for i in range(64)]
    a = time.time()
    with Pool(args.workers) as pool:
        res = pool.map(work, jobs)
    errs = [e for r in res for e in r[0]]
    slow = max((r[1] for r in res), key=lambda s: s[0])
    print(f"{sum(r[2] for r in res)} frames in {time.time() - a:.0f}s, {len(errs)} errors, "
          f"slowest {slow[0]:.3f}s at t={slow[1]:.3f}")
    seen = set()
    for t, tb in errs:
        key = tb.strip().splitlines()[-1]
        if key not in seen:
            seen.add(key)
            print(f"--- t={t:.3f}\n{tb}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
