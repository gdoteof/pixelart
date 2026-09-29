"""Make a take (or any audio file, e.g. a Suno download) the project's song.

    python -m pixelart.song.pick PROJECT TAKE|FILE [--title "Song Title"] [--force]

Writes audio/song.wav (24-bit PCM, source sample rate) and data/song.json,
which records where the song came from and its duration; the template's
project.py reads END and the title from it. The next step is
`python -m pixelart.audio.analyze PROJECT`.

Replacing a song that already has analysis in data/ needs --force, and then
the analysis must be redone with `analyze --force`.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pixelart.ffmpeg import FFMPEG, decode_mono

ANALYSIS = ("beat_this.json", "vocal_env.npy", "vocals.whisper.json", "song.whisper.json", "lyrics_timed.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("take", help="a take name from build/takes (e.g. yue2-s1) or a path to an audio file")
    ap.add_argument("--title", help="shown in the video (default: the project directory's name)")
    ap.add_argument("--force", action="store_true", help="replace a song that already has analysis")
    args = ap.parse_args()

    root = Path(args.project).resolve()
    takes = root / "build" / "takes"
    src = Path(args.take).expanduser()
    meta = {}
    if not src.is_file():
        src = takes / f"{args.take}.flac"
        if not src.is_file():
            names = sorted(p.stem for p in takes.glob("*.flac"))
            raise SystemExit(f"no take {args.take!r}; takes: {', '.join(names) or 'none'}")
        meta = json.loads(src.with_suffix(".json").read_text())
    src = src.resolve()

    song, data = root / "audio" / "song.wav", root / "data"
    song_meta = data / "song.json"
    analysed = [n for n in ANALYSIS if (data / n).exists()]
    if song.exists() and analysed and not args.force:
        old = json.loads(song_meta.read_text()).get("source") if song_meta.exists() else song.name
        raise SystemExit(f"{root.name} already has a song ({old}) with analysis ({', '.join(analysed)}); "
                         "pass --force to replace it, then re-run analyze with --force")

    song.parent.mkdir(exist_ok=True)
    data.mkdir(exist_ok=True)
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-map", "0:a:0",
                    "-c:a", "pcm_s24le", str(song)], check=True)
    duration = round(len(decode_mono(song, 16000)) / 16000, 3)
    sheet = root / "lyrics.txt"
    record = {
        "title": args.title or root.name.replace("-", " ").replace("_", " ").title(),
        "source": meta.get("take") or src.name,
        "duration": duration,
        "picked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **{k: meta[k] for k in ("model", "seed", "style", "lyrics_sha256") if k in meta},
    }
    if sheet.exists() and "lyrics_sha256" not in record:
        record["lyrics_sha256"] = hashlib.sha256(sheet.read_bytes()).hexdigest()[:16]
    song_meta.write_text(json.dumps(record, indent=2) + "\n")
    print(f"{record['source']} -> {song} ({duration:.1f}s); wrote {song_meta}")
    print(f"next: uv run python -m pixelart.audio.analyze {args.project}"
          + (" --force" if analysed else ""))


if __name__ == "__main__":
    main()
