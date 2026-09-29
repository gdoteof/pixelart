"""The local song models and how to run them.

Each model is its own checkout with its own venv (their torch pins conflict
with each other and with pixelart's), found under PIXELART_MODELS, which
defaults to a `local-music/` directory next to this repo:

    PIXELART_MODELS/YuE            github.com/multimodal-art-projection/YuE
                                   python3.12 -m venv .venv && .venv/bin/pip install .
    PIXELART_MODELS/ACE-Step-1.5   github.com/ace-step/ACE-Step-1.5
                                   uv sync; uv run acestep-download (+ --model acestep-v15-xl-turbo)

PIXELART_YUE2 and PIXELART_ACESTEP override the two paths one at a time.
YuE2 fetches its weights into the Hugging Face cache on first use.

Settings for a 16 GB card (both models assume 24 GB):
- YuE2 gets `--budget <VRAM> --offload-ar`.
- ACE-Step XL gets the PyTorch LM backend with DiT offload, because vLLM keeps
  the LM resident and the 9 GB bf16 DiT then does not fit.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

from pixelart.gpu import vram_gib

REPO = Path(__file__).resolve().parents[2]
MODELS_DIR = Path(os.environ.get("PIXELART_MODELS", REPO.parent / "local-music")).expanduser()
YUE2 = Path(os.environ.get("PIXELART_YUE2", MODELS_DIR / "YuE")).expanduser()
ACESTEP = Path(os.environ.get("PIXELART_ACESTEP", MODELS_DIR / "ACE-Step-1.5")).expanduser()
ACESTEP_RUNNER = Path(__file__).with_name("acestep_runner.py")


class ModelMissing(RuntimeError):
    pass


def _need(path, what):
    if not Path(path).exists():
        raise ModelMissing(f"{what} not found at {path}; see pixelart/song/models.py for setup")


def yue2(lyrics_file, style, seeds, work, log, **_):
    """YuE2-3B: plans a melody-and-chord score (kept as score.abc), then renders it. ~100 s per 3-min take."""
    exe = YUE2 / ".venv" / "bin" / "yue2"
    _need(exe, "YuE2")
    budget = vram_gib() or 24
    lyrics = Path(lyrics_file).read_text()
    for seed in seeds:
        out = work / f"seed{seed}"
        shutil.rmtree(out, ignore_errors=True)          # yue2 refuses to reuse an output directory
        request = work / f"request-seed{seed}.json"
        request.write_text(json.dumps({"id": f"seed{seed}", "style": style, "lyrics": lyrics,
                                       "cot": "full", "seed": seed}, indent=2, ensure_ascii=False))
        cmd = [str(exe), "generate", "--request", str(request), "--output", str(out),
               "--budget", f"{budget:.0f}"] + (["--offload-ar"] if budget < 24 else [])
        if subprocess.run(cmd, cwd=work, stdout=log, stderr=subprocess.STDOUT).returncode == 0:
            audio = next(out.glob("*/audio.flac"), None)
            if audio:
                yield seed, audio, {"score": str(audio.with_name("score.abc"))}


def _acestep(dit, lyrics_file, style, seeds, work, log, bpm=None, duration=None):
    py = ACESTEP / ".venv" / "bin" / "python"
    _need(py, "ACE-Step 1.5")
    _need(ACESTEP / "checkpoints" / dit, f"ACE-Step weights {dit}")
    style_file = work / "style.txt"
    style_file.write_text(style + "\n")
    cmd = [str(py), str(ACESTEP_RUNNER), "--ace", str(ACESTEP), "--lyrics-file", str(lyrics_file),
           "--style-file", str(style_file), "--out", str(work), "--dit", dit,
           "--seeds", *map(str, seeds)]
    if "xl" in dit and (vram_gib() or 0) < 20:
        cmd += ["--lm-backend", "pt", "--offload-dit"]
    if bpm:
        cmd += ["--bpm", str(bpm)]
    if duration:
        cmd += ["--duration", str(duration)]
    subprocess.run(cmd, cwd=work, stdout=log, stderr=subprocess.STDOUT)   # ACE-Step writes .cache/ into its cwd
    for seed in seeds:
        audio = next((work / f"seed{seed}").glob("*.flac"), None)
        if audio:
            yield seed, audio, {}


def acestep(lyrics_file, style, seeds, work, log, **kw):
    """ACE-Step 1.5, 2B turbo DiT: fastest, ~30 s per 3-min take."""
    return _acestep("acestep-v15-turbo", lyrics_file, style, seeds, work, log, **kw)


def acestep_xl(lyrics_file, style, seeds, work, log, **kw):
    """ACE-Step 1.5, 4B XL turbo DiT: clearest diction in testing, ~40 s per 3-min take on 16 GB."""
    return _acestep("acestep-v15-xl-turbo", lyrics_file, style, seeds, work, log, **kw)


MODELS = {"yue2": yue2, "acestep": acestep, "acestep-xl": acestep_xl}
DEFAULT = ("yue2", "acestep-xl")
