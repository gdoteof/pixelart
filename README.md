# pixelart

Pixel-art music videos, drawn procedurally in Python (Pillow + numpy), frame by frame, and encoded with ffmpeg. Each video lives in its own directory under `projects/`. The tooling they share lives in the `pixelart/` package.

| Project | What it is |
| --- | --- |
| [`alt-f4`](projects/alt-f4) | *Sam vs Dario*, a satirical AI-industry rap battle styled as a 16-bit fighting game |
| [`_template`](projects/_template) | Starting point for the next video |

## Layout

```
pixelart/                 shared library and CLIs
  pixel.py                primitives: string sprites, pixel fonts, ordered dither, camera compose
  timing.py               render-time clocks: tracked beat grid, "which lyric/word is being sung"
  project.py              the project.py contract, and the loader the CLIs use
  render.py               python -m pixelart.render PROJECT     parallel render -> x264 -> mp4 with audio
  preview.py              python -m pixelart.preview PROJECT …  still frames + captioned contact sheet
  sweep.py                python -m pixelart.sweep PROJECT      render every frame, report exceptions
  sheet.py                python -m pixelart.sheet OUT a.png …  contact sheet of any PNGs
  audio/                  one-off song analysis: stems, beats, tempo, transcribe, align, envelope
  fonts/                  Press Start 2P, Silkscreen (SIL OFL)
projects/
  _template/              copy this to start a new video
  alt-f4/
```

Inside a project:

- `project.py` holds the settings the shared tools read (`FPS`, `END`, `AUDIO`, `render_frame`, and so on). See `pixelart/project.py` for the full contract.
- `data/` is committed. It holds the song analysis: beat grid, transcripts, timed lyrics and loudness envelope. The files are small, and they are either slow to regenerate (they need the ML stack and a GPU) or tuned by hand.
- `audio/` and `build/` are ignored by git. `audio/` holds the song. `build/` holds stems, render segments and previews.

## Setup

You need [uv](https://docs.astral.sh/uv/) and `ffmpeg` on `PATH`. To point at a different ffmpeg binary, set `FFMPEG=/path/to/ffmpeg`. If you use snap's ffmpeg, keep songs and outputs under `$HOME`, because it cannot read or write `/tmp`.

```sh
uv sync                  # rendering: numpy + Pillow
uv sync --extra audio    # song analysis too: torch (CPU), Demucs, beat_this, faster-whisper + CUDA libs
```

## Starting a new video

1. `cp -r projects/_template projects/my-video`, then render it once to check the setup: `uv run python -m pixelart.preview projects/my-video hello 0 0.25 0.5`
2. Put the song at `projects/my-video/audio/song.wav`, then set `AUDIO` and `END` in `project.py`.
3. Analyse the song (see the next section) and swap the template's fixed 120 BPM clock for `data/beat_this.json`.
4. Draw. Iterate with `preview` and `sweep`, then `render`.

Project modules import each other by bare name (`import timeline`), and the loader puts the project directory on `sys.path`. To run a project script directly, use `uv run python projects/my-video/some_script.py`.

## Analysing a song

Run each step once per song. Write the outputs to `data/`. Everything except `tempo` and `envelope` needs `uv sync --extra audio`.

```sh
P=projects/my-video
uv run python -m pixelart.audio.tempo  $P/audio/song.wav                       # quick BPM look, numpy only
uv run python -m pixelart.audio.stems  $P/audio/song.wav $P/build/stems        # vocals / no_vocals (Demucs, CPU)
uv run python -m pixelart.audio.beats  $P/audio/song.wav $P/data/beat_this.json
uv run python -m pixelart.audio.envelope $P/build/stems/htdemucs/song/vocals.wav $P/data/vocal_env.npy \
    --fps 24 --duration 200

# Word timings from both the vocal stem and the full mix (they fail in different places).
# ctranslate2 needs the pip CUDA libs on the loader path:
SP=.venv/lib/python3.12/site-packages/nvidia
export LD_LIBRARY_PATH=$SP/cublas/lib:$SP/cudnn/lib
uv run python -m pixelart.audio.transcribe $P/build/stems/htdemucs/song/vocals.wav $P/data/vocals.whisper.json \
    --prompt "Proper Nouns, Jargon, From The Lyrics"
uv run python -m pixelart.audio.transcribe $P/audio/song.wav $P/data/song.whisper.json --prompt "…"
```

Then snap the transcribed timings onto the real lyrics with `pixelart.audio.align`. Every song needs a small driver script, because you have to say where each section sits in the recording and hand-time anything Whisper can't hear, such as chants and ad-libs. `projects/alt-f4/align.py` is a worked example to copy.

Demucs applies a random time shift, so regenerated stems (and the loudness envelope built from them) differ a little from run to run. Commit `data/` and treat it as the source of truth once a video depends on it.

Things to check by ear or eye: Suno renders are sometimes spliced mid-song, which makes a fixed-BPM grid drift. Use the tracked beats, and filter any spurious downbeats around the splice. There can also be a click in the last few frames, so set `END` to stop just before it.

## Working loop

```sh
uv run python -m pixelart.preview projects/alt-f4 v2 57:60:0.5 88.5   # times, or a:b:step ranges
uv run python -m pixelart.sweep   projects/alt-f4                      # every frame, ~10 s on 32 cores
uv run python -m pixelart.render  projects/alt-f4                      # ~45 s for 3:20 at 1080p24
```

`render` keeps finished segments in `build/segments` so an interrupted render can resume. After changing code, pass `--fresh`.

## What to reuse from earlier videos

`pixelart/` only holds code that is independent of any one video's look. A lot of alt-f4 is reusable in spirit but tied to its characters and style, so it stays in that project. Copy it and adapt it:

- `characters.py`: procedural chibi heads and bodies with pixel-art rules (4-connected outlines, crescent shading, rim light, mirrored facing)
- `props.py`: UI widgets such as speech and thought bubbles, stamps, Win95 windows, gradient "big text", keycaps and confetti
- `gagkit.py` and `video.py`: per-lyric-line gags written as generators that `yield` the drawing phase they want next (back / front / crowd / ui / top), plus a camera with integer zoom
- `thumbnail.py`: YouTube thumbnails in the video's style, with a sheet previewing them at YouTube's display sizes

If the same code gets copied into a second project, move it into `pixelart/` instead.
