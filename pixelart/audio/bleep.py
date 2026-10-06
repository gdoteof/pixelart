"""Cut the vocals out of a span of the song and drop a buzzer or a bleep in.

    python -m pixelart.audio.bleep PROJECT --words 0:12          # the words Whisper heard in a span, with times
    python -m pixelart.audio.bleep PROJECT 3.42:4.60 8.10:9.40   # cut the vocals in each span and buzz
                                   [--sound buzzer|bleep|none] [--length 0.45] [--gain -3]

A song model can't perform an interruption: it sings "My name is Pew..." as a line that trails
off. So the lyric sheet holds the whole line, and this cuts it short once the take is picked and
analysed. Inside each span the song is swapped for its accompaniment (the Demucs no_vocals stem
that `analyze` wrote), so the beat carries on under the gap, and the sound starts on the cut.

The take as picked is kept in audio/song.take.wav and every run starts from it, so the spans can
be retimed. Nothing moves in time: the timings in data/ still hold, and the words inside the spans
are just gone. The spans are recorded in data/song.json as "cuts", for the video to stamp on.
Run it after `analyze`: stems separated from a song that is already cut have the buzzer in them.
"""
import argparse
import json
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

from pixelart.ffmpeg import FFMPEG

CUT, RETURN = 0.004, 0.04   # seconds to fade the vocals out at the cut, and back in after the span
SOUNDS = ("buzzer", "bleep", "none")


def decode(path, sr):
    """The whole file as float32 stereo samples at `sr` Hz, shape (n, 2)."""
    raw = subprocess.run([FFMPEG, "-v", "quiet", "-i", str(path), "-f", "f32le", "-ac", "2",
                          "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2)


def encode(samples, sr, path):
    """Write float32 stereo samples as 24-bit PCM, the format `pick` writes."""
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2",
                    "-ar", str(sr), "-i", "-", "-c:a", "pcm_s24le", str(path)],
                   input=samples.astype(np.float32).tobytes(), check=True)


def tone(sound, n, sr):
    """`n` samples of the sound: a game-show buzzer (two square waves a tritone apart) or the
    1 kHz censor bleep."""
    t = np.arange(n) / sr
    if sound == "bleep":
        y = np.sin(2 * np.pi * 1000 * t)
    else:
        y = 0.55 * np.sign(np.sin(2 * np.pi * 110 * t)) + 0.45 * np.sign(np.sin(2 * np.pi * 155.56 * t))
        k = max(1, sr // 6000)   # round the square edges a little, or they alias
        y = np.convolve(y, np.ones(k) / k, mode="same")
    edge = min(n // 2, int(0.004 * sr)), min(n // 2, int(0.025 * sr))
    y[:edge[0]] *= np.linspace(0, 1, edge[0])
    y[n - edge[1]:] *= np.linspace(1, 0, edge[1])
    return y


def cut(song, backing, sr, spans, sound="buzzer", length=0.45, gain=-3.0):
    """`song` with the vocals cut in each (start, end) span: the backing plays there instead, and
    `sound` starts on the cut, `gain` dB louder than the song's overall level (RMS)."""
    n = min(len(song), len(backing))
    out = song.copy()
    level = np.sqrt(np.mean(song ** 2)) * 10 ** (gain / 20)
    for start, end in spans:
        a, b = int(start * sr), min(n, int(end * sr))
        if not 0 <= a < b:
            raise SystemExit(f"span {start}:{end} is outside the song or empty")
        mix = np.ones(b - a)   # how much of the backing replaces the song
        fade_in, fade_out = min(b - a, int(CUT * sr)), min(b - a, int(RETURN * sr))
        mix[:fade_in] = np.linspace(0, 1, fade_in)
        mix[b - a - fade_out:] *= np.linspace(1, 0, fade_out)
        out[a:b] = song[a:b] * (1 - mix[:, None]) + backing[a:b] * mix[:, None]
        if sound != "none":
            m = min(b - a, int(length * sr))
            y = tone(sound, m, sr)
            out[a:a + m] += (y / np.sqrt(np.mean(y ** 2)) * level)[:, None]
    clipped = int((np.abs(out) > 1).sum())
    if clipped:
        print(f"note: {clipped} samples clipped; lower --gain")
    return np.clip(out, -1, 1)


def parse_span(text):
    a, _, b = text.partition(":")
    return float(a), float(b)


def main():
    ap = argparse.ArgumentParser(description="Cut the vocals out of spans of a project's song, with a buzzer or a bleep.")
    ap.add_argument("project")
    ap.add_argument("spans", nargs="*", type=parse_span, metavar="START:END", help="seconds, e.g. 3.42:4.6")
    ap.add_argument("--words", type=parse_span, metavar="START:END",
                    help="list the words Whisper heard in this span instead, to find the cut points")
    ap.add_argument("--sound", choices=SOUNDS, default="buzzer")
    ap.add_argument("--length", type=float, default=0.45, help="seconds of buzzer or bleep (default 0.45)")
    ap.add_argument("--gain", type=float, default=-3.0, help="its level against the song's, in dB (default -3)")
    args = ap.parse_args()

    root = Path(args.project).resolve()
    song, data = root / "audio" / "song.wav", root / "data"
    if args.words:
        heard = json.loads((data / "vocals.whisper.json").read_text())
        for w in heard:
            if args.words[0] <= w["t0"] <= args.words[1]:
                print(f"{w['t0']:7.2f} {w['t1']:7.2f}  {w['w']}")
        return
    if not args.spans:
        ap.error("give the spans to cut, or --words START:END to find them")

    backing = root / "build" / "stems" / "htdemucs" / song.stem / "no_vocals.wav"
    if not backing.exists():
        raise SystemExit(f"no {backing}: run `python -m pixelart.audio.analyze {args.project}` first")
    take = song.with_name("song.take.wav")
    if not take.exists():
        shutil.copy2(song, take)
    with wave.open(str(take)) as w:
        sr = w.getframerate()
    out = cut(decode(take, sr), decode(backing, sr), sr, args.spans, args.sound, args.length, args.gain)
    encode(out, sr, song)

    meta_file = data / "song.json"
    meta = json.loads(meta_file.read_text())
    meta["cuts"] = [{"t0": a, "t1": b, "sound": args.sound} for a, b in args.spans]
    meta_file.write_text(json.dumps(meta, indent=2) + "\n")
    spans = ", ".join(f"{a:g}-{b:g}s" for a, b in args.spans)
    print(f"{song}: vocals cut at {spans} ({args.sound}); the take as picked is {take.name}")


if __name__ == "__main__":
    main()
