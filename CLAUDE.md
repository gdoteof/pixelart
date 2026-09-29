# pixelart

Procedural pixel-art music videos. Start with `README.md` for the layout and commands. For the whole
lyrics -> song -> video pipeline, use the `music-video` skill (`.claude/skills/music-video/SKILL.md`).

## Environment

- **Python:** run everything with `uv run` from the repo root. `uv sync --extra audio` adds the analysis
  stack: CPU torch, Demucs, beat_this and faster-whisper with the CUDA libraries. The CLIs that need
  CUDA libraries on `LD_LIBRARY_PATH` re-exec themselves (`pixelart/gpu.py`).
- **ffmpeg:** it may be the snap build, which can only read and write under `$HOME`. Keep audio and
  build output inside the repo, not in `/tmp`. Set `FFMPEG` to use another binary.
- **Song models:** YuE2 and ACE-Step 1.5 live in `../local-music/` (`PIXELART_MODELS`), each in its own
  venv, and `pixelart/song/models.py` drives them as subprocesses. Their 16 GB settings (YuE2
  `--budget/--offload-ar`, ACE-Step XL with the PyTorch LM backend and DiT offload) are encoded there.
- **GPU:** run one GPU job at a time. The song models, Whisper and anything else on the card share
  about 13 GB once the desktop's share is taken.

## Conventions

- `pixelart/` holds only code that is independent of any one video's look. Per-video code stays in
  `projects/<name>/`, and modules there import each other flat.
- `projects/<name>/data/` is committed and tuned by hand once a video depends on it: don't regenerate
  it casually. Media (`*.wav`, `*.flac`, `*.mp4`, ...) and `build/` are gitignored.
- The repo is public: ask before committing or pushing, and keep private notes (such as content limits
  that the user doesn't want published) out of committed files.
- Check visual changes by rendering previews and looking at the contact sheet, not by reasoning about
  coordinates.
