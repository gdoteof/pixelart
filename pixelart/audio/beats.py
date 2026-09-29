"""Beat and downbeat tracking with beat_this, saved as JSON for pixelart.timing.BeatClock.

    python -m pixelart.audio.beats SONG OUT.json [--device cuda]

Tracked beats follow tempo drift and splices (Suno renders are sometimes
stitched mid-song), which a fixed-BPM grid does not. Expect to hand-filter a
few spurious downbeats around splices and at the tail.
"""
import argparse
import json

import numpy as np


def track(song, device="cpu", checkpoint="final0", dbn=False):
    from beat_this.inference import File2Beats
    beats, downbeats = File2Beats(checkpoint_path=checkpoint, device=device, dbn=dbn)(str(song))
    return [round(float(b), 3) for b in beats], [round(float(d), 3) for d in downbeats]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("song")
    ap.add_argument("out")
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    beats, downbeats = track(args.song, args.device)
    with open(args.out, "w") as f:
        json.dump({"beats": beats, "downbeats": downbeats}, f)
    ibi = np.diff(beats)
    print(f"{len(beats)} beats, {len(downbeats)} downbeats, median {60 / np.median(ibi):.2f} bpm -> {args.out}")


if __name__ == "__main__":
    main()
