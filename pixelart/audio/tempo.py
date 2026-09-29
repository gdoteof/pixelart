"""Quick tempo and beat-grid estimate from the mix, numpy only (no ML environment needed).

    python -m pixelart.audio.tempo SONG [--json OUT.json]

Good for a first look at a song (BPM, first beat, a loudness sketch of the
arrangement). A fixed grid drifts on renders with tempo wobble or splices; use
pixelart.audio.beats for the grid a video actually runs on.
"""
import argparse
import json

import numpy as np

from pixelart.ffmpeg import decode_mono

SR = 22050
HOP = 256


def onset_envelope(y):
    n_fft = 1024
    win = np.hanning(n_fft).astype(np.float32)
    frames = np.lib.stride_tricks.sliding_window_view(y, n_fft)[::HOP] * win
    mag = np.abs(np.fft.rfft(frames, axis=1))
    logmag = np.log1p(100 * mag)
    flux = np.maximum(0, np.diff(logmag, axis=0)).sum(axis=1)
    flux = np.concatenate([[0], flux])
    flux -= np.convolve(flux, np.ones(16) / 16, mode="same")  # remove slow trend
    return np.maximum(flux, 0)


def tempo(env, lo=60, hi=180):
    fps = SR / HOP
    ac = np.correlate(env - env.mean(), env - env.mean(), mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm = 60 * fps / np.maximum(lags, 1)
    ok = (bpm >= lo) & (bpm <= hi)
    best = lags[ok][np.argmax(ac[ok])]
    # refine with parabolic interpolation
    a, b, c = ac[best - 1], ac[best], ac[best + 1]
    frac = 0.5 * (a - c) / (a - 2 * b + c)
    return 60 * fps / (best + frac), ac, bpm


def beat_phase(env, period_frames):
    best, best_score = 0, -1
    for ph in np.arange(0, period_frames, 0.25):
        idx = np.round(np.arange(ph, len(env) - 1, period_frames)).astype(int)
        score = env[idx].sum()
        if score > best_score:
            best, best_score = ph, score
    return best


def fine_grid(env, lo=88.0, hi=94.0, step=0.005):
    """Joint tempo/phase search maximising onset energy on the beat grid: (score, bpm, first beat s)."""
    fps = SR / HOP
    smooth = np.convolve(env, np.hanning(5) / np.hanning(5).sum(), mode="same")
    best = (-1, 0, 0)
    for bpm in np.arange(lo, hi, step):
        period = fps * 60 / bpm
        phases = np.arange(0, period, 0.5)
        n = int((len(env) - 1 - period) / period)
        idx = np.round(phases[:, None] + np.arange(n)[None, :] * period).astype(int)
        scores = smooth[idx].sum(axis=1)
        i = np.argmax(scores)
        if scores[i] > best[0]:
            best = (scores[i], bpm, phases[i] / fps)
    return best


def grid_quality(env, bpm, first, parts=4):
    """On-beat / off-beat onset ratio per part of the song; a falling ratio means the grid drifts."""
    fps = SR / HOP
    period = fps * 60 / bpm
    idx = np.round(first * fps + np.arange(0, (len(env) - first * fps) / period - 1) * period).astype(int)
    off = np.round(idx + period / 2).astype(int)
    off = off[off < len(env)]
    q = []
    for chunk_on, chunk_off in zip(np.array_split(idx, parts), np.array_split(off, parts)):
        q.append(env[chunk_on].mean() / max(1e-9, env[chunk_off].mean()))
    return q


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("--json", help="write {bpm, first_beat, duration} here")
    args = ap.parse_args()
    y = decode_mono(args.song, SR)
    env = onset_envelope(y)
    fps = SR / HOP
    bpm, ac, bpms = tempo(env)
    ok = (bpms >= 60) & (bpms <= 180)
    cand = sorted(zip(ac[ok], bpms[ok]), reverse=True)[:8]
    print("tempo candidates:", [round(b, 1) for _, b in cand])
    first = beat_phase(env, fps * 60 / bpm) / fps
    print(f"bpm={bpm:.3f} first_beat={first:.3f}s beat_len={60 / bpm:.4f}s")
    print("grid quality by quarter:", [round(q, 2) for q in grid_quality(env, bpm, first)])
    rms = [float(np.sqrt(np.mean(y[i:i + 2 * SR] ** 2))) for i in range(0, len(y), 2 * SR)]
    print("rms/2s:", " ".join(f"{r:.2f}" for r in rms))
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"bpm": bpm, "first_beat": first, "duration": len(y) / SR}, f, indent=1)


if __name__ == "__main__":
    main()
