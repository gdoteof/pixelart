"""Whisper word timings for ALT-F4: the vocal stem and the full mix.

    SP=../../.venv/lib/python3.12/site-packages/nvidia
    LD_LIBRARY_PATH=$SP/cublas/lib:$SP/cudnn/lib uv run python transcribe.py

Needs build/stems from `python -m pixelart.audio.stems audio/song.wav build/stems`.
Writes data/vocals.whisper.json and data/song.whisper.json for align.py.
"""
import json
from pathlib import Path

from pixelart.audio.transcribe import transcribe

ROOT = Path(__file__).parent
# Priming with the real names keeps Whisper from inventing spellings.
PROMPT = ("Sam Altman, Dario Amodei, Anthropic, OpenAI, Claude, Claudia, Haiku, Sora, "
          "Scarlett, Pentagon, Mythos, CAPTCHA, regex, Hugging Face, Ilya, Karpathy, AGI.")
SOURCES = {"vocals": ROOT / "build/stems/htdemucs/song/vocals.wav", "song": ROOT / "audio/song.wav"}


if __name__ == "__main__":
    for name, src in SOURCES.items():
        words = transcribe(src, PROMPT, log=lambda s: print(s, flush=True))
        out = ROOT / "data" / f"{name}.whisper.json"
        out.write_text(json.dumps(words, indent=0))
        print("wrote", out, len(words), "words")
