"""Start a new video project from projects/_template.

    python -m pixelart.new NAME      -> projects/NAME/ (lyrics.txt, style.txt, project.py, video.py, README.md)

Then write lyrics.txt and style.txt and run `python -m pixelart.song.generate projects/NAME`,
or bring a finished song with `python -m pixelart.song.pick projects/NAME path/to/song.wav`.
"""
import re
import shutil
import sys
from pathlib import Path

PROJECTS = Path(__file__).resolve().parent.parent / "projects"


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", sys.argv[1]):
        raise SystemExit("usage: python -m pixelart.new NAME   (lower-case letters, digits, - and _)")
    dst = PROJECTS / sys.argv[1]
    if dst.exists():
        raise SystemExit(f"{dst} already exists")
    shutil.copytree(PROJECTS / "_template", dst,
                    ignore=shutil.ignore_patterns("build", "audio", "data", "__pycache__", "*.mp4"))
    print(f"created {dst}; next: edit lyrics.txt and style.txt")


if __name__ == "__main__":
    main()
