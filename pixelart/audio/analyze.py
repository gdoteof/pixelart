"""Run the whole song analysis for a project, skipping steps whose output exists.

    python -m pixelart.audio.analyze PROJECT [--only stems,beats,...] [--force]

Needs `uv sync --extra audio`. Steps and outputs:

    stems       build/stems/htdemucs/song/{vocals,no_vocals}.wav    Demucs, CPU, ~1-2 min
    beats       data/beat_this.json                                  beat_this, CPU
    envelope    data/vocal_env.npy                                   vocal loudness per video frame
    transcribe  data/vocals.whisper.json, data/song.whisper.json     faster-whisper, CUDA
    align       data/lyrics_timed.json                               auto-align lyrics.txt (pixelart.audio.align)

Whisper is primed with the proper nouns in lyrics.txt, or with prompt.txt if the
project has one. A project with its own align.py (hand-timed sections, like
alt-f4) keeps it: the align step then only reminds you to run it.
"""
import argparse
import json
import time

import numpy as np

from pixelart.project import load

STEPS = ("stems", "beats", "envelope", "transcribe", "align")


def song_duration(p):
    meta = p.root / "data" / "song.json"
    if meta.exists():
        return json.loads(meta.read_text())["duration"]
    from pixelart.ffmpeg import decode_mono
    return len(decode_mono(p.audio, 16000)) / 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--only", help=f"comma-separated subset of {','.join(STEPS)}")
    ap.add_argument("--force", action="store_true", help="redo steps even if their output exists")
    args = ap.parse_args()
    steps = args.only.split(",") if args.only else list(STEPS)
    unknown = set(steps) - set(STEPS)
    if unknown:
        ap.error(f"unknown steps: {', '.join(sorted(unknown))}")

    p = load(args.project)
    if p.audio is None or not p.audio.exists():
        raise SystemExit(f"{p.root.name} has no song yet: python -m pixelart.song.pick {args.project} TAKE")
    data, build = p.root / "data", p.build
    data.mkdir(exist_ok=True)
    stem_dir = build / "stems" / "htdemucs" / p.audio.stem
    vocals = stem_dir / "vocals.wav"
    lyrics_file = p.root / "lyrics.txt"
    whisper_out = {"vocals": data / "vocals.whisper.json", "song": data / "song.whisper.json"}
    outputs = {"stems": [vocals], "beats": [data / "beat_this.json"], "envelope": [data / "vocal_env.npy"],
               "transcribe": list(whisper_out.values()), "align": [data / "lyrics_timed.json"]}
    todo = [s for s in steps if args.force or not all(f.exists() for f in outputs[s])]
    if "transcribe" in todo:
        from pixelart.gpu import ensure_cuda_libs
        ensure_cuda_libs()   # re-execs this command once, before any work is done
    duration = song_duration(p)
    print(f"{p.root.name}: {p.audio.name}, {duration:.1f}s; steps to run: {', '.join(todo) or 'none'}", flush=True)

    def step(name):
        print(f"--- {name}", flush=True)
        return time.time()

    if "stems" in todo:
        t = step("stems")
        from pixelart.audio.stems import separate
        separate(p.audio, build / "stems")
        print(f"{vocals} ({time.time() - t:.0f}s)")

    if "beats" in todo:
        t = step("beats")
        from pixelart.audio.beats import track
        beats, downbeats = track(p.audio)
        (data / "beat_this.json").write_text(json.dumps({"beats": beats, "downbeats": downbeats}))
        bpm = 60 / np.median(np.diff(beats))
        print(f"{len(beats)} beats, {len(downbeats)} downbeats, median {bpm:.1f} bpm ({time.time() - t:.0f}s)")

    if "envelope" in todo:
        t = step("envelope")
        from pixelart.audio.envelope import loudness_envelope
        env = loudness_envelope(vocals, p.fps, duration)
        np.save(data / "vocal_env.npy", env)
        print(f"{len(env)} frames at {p.fps} fps, mean {env.mean():.3f} ({time.time() - t:.0f}s)")

    if "transcribe" in todo:
        t = step("transcribe")
        from pixelart.audio.transcribe import transcribe
        prompt_file = p.root / "prompt.txt"
        if prompt_file.exists():
            prompt = prompt_file.read_text().strip()
        elif lyrics_file.exists():
            from pixelart.lyrics import whisper_prompt
            prompt = whisper_prompt(lyrics_file.read_text())
        else:
            prompt = None
        print(f"prompt: {prompt}")
        for name, src in (("vocals", vocals), ("song", p.audio)):
            words = transcribe(src, prompt, log=None)
            whisper_out[name].write_text(json.dumps(words, indent=0))
            print(f"{whisper_out[name].name}: {len(words)} words")
        print(f"({time.time() - t:.0f}s)")

    if "align" in todo:
        step("align")
        from pixelart.audio import align
        if (p.root / "align.py").exists():
            print(f"{p.root.name} has its own align.py; run it: uv run python {p.root / 'align.py'}")
        elif not lyrics_file.exists():
            print("no lyrics.txt, skipping")
        else:
            transcripts = [json.loads(f.read_text()) for f in whisper_out.values()]
            timed, report = align.auto(lyrics_file.read_text(), transcripts, duration)
            (data / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
            align.print_report(report)


if __name__ == "__main__":
    main()
