"""Generate song takes from a project's lyrics.txt and style.txt.

    python -m pixelart.song.generate PROJECT [--models yue2 acestep-xl] [--seeds 1 2] [--force] [--no-check]

lyrics.txt is a lyric sheet (pixelart.lyrics): speakers and performance notes
in its headers are for the video and the alignment. The models only get plain
structure tags, so put voice and delivery directions in style.txt as well.
style.txt is one line of genre, instruments, vocal character and tempo; a
"NN BPM" in it is passed to ACE-Step as the tempo. ACE-Step also needs a
length (left to itself it can pick 18 s for a full verse and chorus), so
without --duration it gets an estimate from the word count; YuE2 sizes the
song itself. Songs are capped at four minutes: a lyric sheet whose estimate
runs longer is refused before any GPU time is spent (--long overrides).

Each take lands in PROJECT/build/takes/:
    <model>-s<seed>.flac        the model's audio, untouched
    <model>-s<seed>.json        how it was made
    listen/<model>-s<seed>.m4a  loudness-matched (-14 LUFS) for A/B listening
Existing takes are kept (pass --force to redo them). Afterwards the lyric
check (pixelart.song.check) scores every take; skip it with --no-check.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pixelart import lyrics
from pixelart.ffmpeg import FFMPEG
from pixelart.song.models import DEFAULT, MODELS, ModelMissing


def listen_copy(src, dst):
    """Loudness-matched AAC copy, so a louder take doesn't win an A/B by being louder."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
                    "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
                    "-movflags", "+faststart", "-metadata", f"title={dst.stem}", str(dst)], check=True)


MAX_SECONDS = 240


def estimate_duration(n_words, style):
    """Seconds for a song with this many sung words: rap is denser than singing, plus intro and outro."""
    per_second = 2.8 if re.search(r"\brap|hip.?hop|trap\b", style, re.I) else 2.0
    return round(max(30.0, n_words / per_second + 8.0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--models", nargs="+", default=list(DEFAULT), choices=sorted(MODELS))
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--duration", type=float, help="ACE-Step only: target seconds (default: from word count)")
    ap.add_argument("--force", action="store_true", help="regenerate takes that already exist")
    ap.add_argument("--long", action="store_true", help=f"allow a song longer than {MAX_SECONDS // 60} minutes")
    ap.add_argument("--no-check", action="store_true", help="skip the Whisper lyric check afterwards")
    args = ap.parse_args()

    root = Path(args.project).resolve()
    sheet_file, style_file = root / "lyrics.txt", root / "style.txt"
    for f in (sheet_file, style_file):
        if not f.exists():
            raise SystemExit(f"missing {f}")
    sheet = sheet_file.read_text()
    style = " ".join(style_file.read_text().split())
    bpm = re.search(r"(\d{2,3})\s*bpm", style, re.I)
    bpm = int(bpm.group(1)) if bpm else None

    takes = root / "build" / "takes"
    (takes / "logs").mkdir(parents=True, exist_ok=True)
    model_lyrics = takes / "model_lyrics.txt"
    model_lyrics.write_text(lyrics.model_lyrics(sheet))
    sheet_sha = hashlib.sha256(sheet.encode()).hexdigest()[:16]
    n_words = len(lyrics.sung_words(sheet))
    estimate = estimate_duration(n_words, style)
    if estimate > MAX_SECONDS and not args.long:
        cut = n_words - int(n_words * (MAX_SECONDS - 8) / (estimate - 8))
        raise SystemExit(f"{n_words} sung words come to about {estimate // 60}:{estimate % 60:02d}, over the "
                         f"{MAX_SECONDS // 60}-minute limit: cut about {cut} words (or pass --long)")
    duration = args.duration or estimate
    print(f"style: {style}\nlyrics: {n_words} sung words -> {model_lyrics}\n"
          f"ACE-Step length: {duration:.0f}s{'' if args.duration else ' (estimated; override with --duration)'}",
          flush=True)

    made = 0
    for name in args.models:
        seeds = [s for s in args.seeds if args.force or not (takes / f"{name}-s{s}.flac").exists()]
        if not seeds:
            print(f"{name}: takes for seeds {args.seeds} exist", flush=True)
            continue
        work = takes / "work" / name
        work.mkdir(parents=True, exist_ok=True)
        log_path = takes / "logs" / f"{name}.log"
        print(f"{name}: seeds {seeds} (log: {log_path})", flush=True)
        start = time.time()
        with open(log_path, "a") as log:
            log.write(f"\n=== {datetime.now().isoformat(timespec='seconds')} seeds {seeds}\n")
            log.flush()
            try:
                for seed, audio, extra in MODELS[name](model_lyrics, style, seeds, work, log,
                                                       bpm=bpm, duration=duration):
                    take = f"{name}-s{seed}"
                    shutil.copyfile(audio, takes / f"{take}.flac")
                    (takes / f"{take}.json").write_text(json.dumps({
                        "take": take, "model": name, "seed": seed, "style": style, "lyrics_sha256": sheet_sha,
                        "source": str(audio), "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        **extra}, indent=2) + "\n")
                    listen_copy(audio, takes / "listen" / f"{take}.m4a")
                    made += 1
                    print(f"  {take} ({time.time() - start:.0f}s)", flush=True)
            except ModelMissing as e:
                print(f"  skipped: {e}", flush=True)
        missing = [s for s in seeds if not (takes / f"{name}-s{s}.flac").exists()]
        if missing:
            print(f"  FAILED seeds {missing}: see {log_path}", flush=True)

    print(f"{made} new takes in {takes}; listen in {takes / 'listen'}", flush=True)
    if not args.no_check and any(takes.glob("*.flac")):
        subprocess.run([sys.executable, "-m", "pixelart.song.check", str(root)])


if __name__ == "__main__":
    main()
