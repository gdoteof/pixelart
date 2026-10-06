"""Cut the vocals out of a span of the song and drop a buzzer, a bleep or a clap in.

    python -m pixelart.audio.bleep PROJECT --words 0:12          # the words Whisper heard in a span, with times
    python -m pixelart.audio.bleep PROJECT 3.42:4.60 8.10:9.40   # cut the vocals in each span and buzz
    python -m pixelart.audio.bleep PROJECT 3.42:4.60 52.06:52.36:clap 52.36:52.60:clap
                                   [--sound buzzer|bleep|clap|none] [--length 0.45] [--gain 0]

A song model can't perform an interruption: it sings "My name is Pew..." as a line that trails
off. So the lyric sheet holds the whole line, and this cuts it short once the take is picked and
analysed. A model can't make a sound effect either: "(Clap, clap!)" comes out as a voice saying
the words. Leave the words in the sheet, so the take has room for the sound, and swap each word
for a clap here.

Inside each span the song is swapped for its accompaniment (the Demucs no_vocals stem that
`analyze` wrote), so the beat carries on under the gap, and the span's sound starts on the cut.
A span is START:END in seconds, or START:END:SOUND to name its sound; --sound is the sound of
the others (`none` only cuts). Spans that touch make one cut with a sound at the start of each,
which is how two claps replace "clap, clap".

The take as picked is kept in audio/song.take.wav and every run starts from it, so the spans can
be retimed. Nothing moves in time: the timings in data/ still hold, and the words inside the spans
are just gone. The spans are recorded in data/song.json as "cuts", for the video to stamp on.
Run it after `analyze`: stems separated from a song that is already cut have the buzzer in them.
"""
import argparse
import json
import shutil
import wave
from pathlib import Path

import numpy as np

from pixelart.ffmpeg import decode_stereo, encode

CUT, RETURN = 0.004, 0.04   # seconds to fade the vocals out at the cut, and back in after the span
NEAR = 3                    # seconds either side of a span that set the sound's level
LEVEL = {"buzzer": -3.0, "bleep": -3.0, "clap": -2.0}   # dB: a sound's loudest 50 ms against the song near it
SOUNDS = (*LEVEL, "none")


def clap(sr, k=0):
    """One handclap, drum-machine style: band-passed noise in three quick slaps and a longer tail.
    `k` picks the noise, so two claps in a row are not the same sample twice."""
    n = int(0.3 * sr)
    t = np.arange(n) / sr
    spectrum = np.fft.rfft(np.random.default_rng(k).standard_normal(n))
    octaves = np.log2(np.maximum(np.fft.rfftfreq(n, 1 / sr), 1.0) / 1400)
    noise = np.fft.irfft(spectrum * np.exp(-0.5 * (octaves / 0.75) ** 2), n)   # a wide band around 1.4 kHz
    slap = 0.011
    env = np.where(t < 3 * slap, np.exp(-(t % slap) / 0.004), np.exp(-(t - 3 * slap) / 0.045))
    tail = int(0.02 * sr)
    env[-tail:] *= np.linspace(1, 0, tail)
    return noise * env


def tone(sound, seconds, sr, k=0):
    """The sound as samples: a game-show buzzer (two square waves a tritone apart) or the 1 kHz
    censor bleep, `seconds` long, or one handclap, which has its own length."""
    if sound == "clap":
        return clap(sr, k)
    n = int(seconds * sr)
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


def loudest(y, sr, window=0.05):
    """RMS of the loudest `window` seconds of a sound."""
    k = max(1, min(len(y), int(window * sr)))
    power = np.cumsum(np.concatenate([[0.0], y ** 2]))
    return np.sqrt((power[k:] - power[:-k]).max() / k)


def cut(song, backing, sr, spans, sound="buzzer", length=0.45, gain=0.0):
    """`song` with the vocals cut in each span: the backing plays there instead, and the span's
    sound starts on the cut. A span is (start, end) or (start, end, sound), and `sound` is the
    sound of the spans that name none. `gain` dB is added to every sound's usual LEVEL."""
    n = min(len(song), len(backing))
    out = song.copy()
    ranges = []
    for start, end, *named in spans:
        a, b = int(start * sr), min(n, int(end * sr))
        if not 0 <= a < b:
            raise SystemExit(f"span {start}:{end} is outside the song or empty")
        ranges.append((a, b, named[0] if named and named[0] else sound))
    cuts = []   # spans that touch are one cut
    for a, b, _ in sorted(ranges):
        if cuts and a <= cuts[-1][1]:
            cuts[-1][1] = max(cuts[-1][1], b)
        else:
            cuts.append([a, b])
    for a, b in cuts:
        mix = np.ones(b - a)   # how much of the backing replaces the song
        fade_in, fade_out = min(b - a, int(CUT * sr)), min(b - a, int(RETURN * sr))
        mix[:fade_in] = np.linspace(0, 1, fade_in)
        mix[b - a - fade_out:] *= np.linspace(1, 0, fade_out)
        out[a:b] = song[a:b] * (1 - mix[:, None]) + backing[a:b] * mix[:, None]
    for k, (a, b, name) in enumerate(ranges):
        if name == "none":
            continue
        near = song[max(0, a - NEAR * sr):b + NEAR * sr]   # a quiet intro gets a quiet buzzer
        level = np.sqrt(np.mean(near ** 2)) * 10 ** ((LEVEL[name] + gain) / 20)
        y = tone(name, min(length, (b - a) / sr), sr, k)[:len(out) - a]
        out[a:a + len(y)] += (y / loudest(y, sr) * level)[:, None]
    clipped = int((np.abs(out) > 1).sum())
    if clipped:
        print(f"note: {clipped} samples clipped; lower --gain")
    return np.clip(out, -1, 1)


def parse_span(text):
    a, b, *sound = text.split(":")
    if len(sound) > 1 or (sound and sound[0] not in SOUNDS):
        raise argparse.ArgumentTypeError(f"{text!r}: a span is START:END or START:END:SOUND, SOUND one of "
                                         + ", ".join(SOUNDS))
    return float(a), float(b), sound[0] if sound else None


def main():
    ap = argparse.ArgumentParser(description="Cut the vocals out of spans of a project's song, with a buzzer, "
                                             "a bleep or a clap.")
    ap.add_argument("project")
    ap.add_argument("spans", nargs="*", type=parse_span, metavar="START:END[:SOUND]",
                    help="seconds, e.g. 3.42:4.6 or 52.06:52.36:clap")
    ap.add_argument("--words", type=parse_span, metavar="START:END",
                    help="list the words Whisper heard in this span instead, to find the cut points")
    ap.add_argument("--sound", choices=SOUNDS, default="buzzer", help="for the spans that don't name one")
    ap.add_argument("--length", type=float, default=0.45, help="seconds of buzzer or bleep (default 0.45)")
    ap.add_argument("--gain", type=float, default=0.0, help="dB louder (or, negative, quieter) than usual")
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
    spans = [(a, b, sound or args.sound) for a, b, sound in args.spans]
    out = cut(decode_stereo(take, sr), decode_stereo(backing, sr), sr, spans, length=args.length, gain=args.gain)
    encode(out, sr, song)

    meta_file = data / "song.json"
    meta = json.loads(meta_file.read_text())
    meta["cuts"] = [{"t0": a, "t1": b, "sound": sound} for a, b, sound in spans]
    meta_file.write_text(json.dumps(meta, indent=2) + "\n")
    listed = ", ".join(f"{a:g}-{b:g}s ({sound})" for a, b, sound in spans)
    print(f"{song}: vocals cut at {listed}; the take as picked is {take.name}")


if __name__ == "__main__":
    main()
