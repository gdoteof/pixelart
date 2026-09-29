"""Per-video-frame loudness in [0, 1], e.g. of the vocal stem to drive mouths.

    python -m pixelart.audio.envelope VOCALS.wav OUT.npy --fps 24 --duration 199.89
"""
import argparse

import numpy as np

from pixelart.ffmpeg import decode_mono


def loudness_envelope(wav, fps, duration, window=0.045, floor_db=-36.0, range_db=18.0, sr=16000):
    """RMS over a `window`-second slice centred on each frame, mapped from
    [floor_db, floor_db + range_db] dBFS onto [0, 1]."""
    y = decode_mono(wav, sr)
    n = int(duration * fps) + 2
    win = int(window * sr)
    env = np.zeros(n, np.float32)
    for f in range(n):
        c = int(f / fps * sr)
        seg = y[max(0, c - win // 2): c + win // 2]
        if len(seg):
            env[f] = np.sqrt(np.mean(seg ** 2))
    db = 20 * np.log10(env + 1e-6)
    return np.clip((db - floor_db) / range_db, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, required=True)
    ap.add_argument("--duration", type=float, required=True)
    args = ap.parse_args()
    env = loudness_envelope(args.wav, args.fps, args.duration)
    np.save(args.out, env)
    print(f"{len(env)} frames, mean {env.mean():.3f} -> {args.out}")


if __name__ == "__main__":
    main()
