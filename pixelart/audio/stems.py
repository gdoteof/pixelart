"""Split a song into vocals and accompaniment with Demucs.

    python -m pixelart.audio.stems SONG OUT_DIR
    -> OUT_DIR/htdemucs/<song stem>/vocals.wav and no_vocals.wav

The vocal stem is what transcription and the loudness envelope want; the full
mix is better for beat tracking. CPU is fine (a 3-minute song takes a minute or two).
"""
import subprocess
import sys
from pathlib import Path


def separate(song, out_dir, model="htdemucs"):
    subprocess.run([sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", model,
                    "-o", str(out_dir), str(song)], check=True)
    stem_dir = Path(out_dir) / model / Path(song).stem
    return stem_dir / "vocals.wav", stem_dir / "no_vocals.wav"


if __name__ == "__main__":
    for p in separate(sys.argv[1], sys.argv[2]):
        print(p)
