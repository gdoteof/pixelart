# pixelart

Pixel-art music videos, drawn procedurally in Python (Pillow + numpy), frame by frame, and encoded with ffmpeg. Each video lives in its own directory under `projects/`. The tooling they share lives in the `pixelart/` package. Finished videos go to the [Pixel Art Rap Battles](https://www.youtube.com/@pixelartrapbattles) channel through the [YouTube uploader](#uploading) ([privacy policy](PRIVACY.md), [terms](TERMS.md)).

| Project | What it is |
| --- | --- |
| [`alt-f4`](projects/alt-f4) | *Sam vs Dario*, a satirical AI-industry rap battle styled as a 16-bit fighting game |
| [`two-georges`](projects/two-georges) | *Two Georges*, King George III vs George Washington, a rap battle across the Atlantic |
| [`narrators`](projects/narrators) | *Attenborough vs. Freeman*, a narrators' rap battle where whoever raps holds the camera: nature documentary vs. film |
| [`smoke-test`](projects/smoke-test) | *Lyrics In, Video Out*, a 30-second demo of the whole pipeline on the template, untouched |
| [`_template`](projects/_template) | Starting point for the next video |

## Layout

```
pixelart/                 shared library and CLIs
  pixel.py                primitives: string sprites, pixel fonts, ordered dither, camera compose
  camera.py               integer-zoom camera over the native world: shots, pans, world -> UI mapping
  anim.py                 deterministic randomness, ramps and easing curves
  sprites.py              sprite canvases with palette names, ink outlines, pasting, scaling, tints and rim light
  fx.py                   comic effects: arcade title text, labels, speech bubbles, stamps, arrows, bursts
  gags.py                 per-lyric-line gags: generators that draw in the render phases they ask for
  timing.py               render-time clocks: tracked beat grid, "which lyric/word is being sung"
  lyrics.py               lyric sheets: [Section - Speaker: note] headers, model tags, sung words
  project.py              the project.py contract, and the loader the CLIs use
  new.py                  python -m pixelart.new NAME                 new project from _template
  render.py               python -m pixelart.render PROJECT          parallel render -> x264 -> mp4 with audio
  preview.py              python -m pixelart.preview PROJECT …       still frames + captioned contact sheet
  sweep.py                python -m pixelart.sweep PROJECT           render every frame, report exceptions
  sheet.py                python -m pixelart.sheet OUT a.png …       contact sheet of any PNGs
  youtube.py              python -m pixelart.youtube PROJECT         upload to YouTube from thumbs/youtube_upload.txt
  song/                   lyrics -> song with local models: generate takes, check and repaint them, pick one
  audio/                  song analysis: analyze runs stems, beats, envelope, transcribe, align
  gpu.py                  CUDA library path for faster-whisper, VRAM size
  fonts/                  Press Start 2P, Silkscreen (SIL OFL)
projects/
  _template/              copy this to start a new video (a working lyric video out of the box)
  alt-f4/
  two-georges/
  narrators/
```

Inside a project:

- `project.py` holds the settings the shared tools read (`FPS`, `END`, `AUDIO`, `render_frame`, and so on). See `pixelart/project.py` for the full contract.
- `lyrics.txt` is the lyric sheet and `style.txt` the one-line style prompt, when the song is generated here.
- `data/` is committed. It holds the song analysis: song provenance, beat grid, transcripts, timed lyrics and loudness envelope. The files are small, and they are either slow to regenerate (they need the ML stack and a GPU) or tuned by hand.
- `audio/` and `build/` are ignored by git. `audio/` holds the song. `build/` holds song takes, stems, render segments and previews.

## Setup

You need [uv](https://docs.astral.sh/uv/) and `ffmpeg` on `PATH`. To point at a different ffmpeg binary, set `FFMPEG=/path/to/ffmpeg`. If you use snap's ffmpeg, keep songs and outputs under `$HOME`, because it cannot read or write `/tmp`.

```sh
uv sync                  # rendering: numpy + Pillow
uv sync --extra audio    # song analysis too: torch (CPU), Demucs, beat_this, faster-whisper + CUDA libs
uv sync --extra audio --extra youtube   # uploading too: the YouTube Data API client
```

Generating songs needs an NVIDIA GPU (tested on 16 GB) and the models, each in its own checkout and venv under `PIXELART_MODELS`, which defaults to `../local-music` next to this repo:

```sh
mkdir -p ../local-music && cd ../local-music
git clone https://github.com/multimodal-art-projection/YuE.git
(cd YuE && uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python .)   # weights download on first use
git clone https://github.com/ace-step/ACE-Step-1.5.git
(cd ACE-Step-1.5 && uv sync && uv run acestep-download && uv run acestep-download --model acestep-v15-xl-turbo)
```

The downloads total about 50 GB. Don't run a large model download and `uv sync` at the same time: the sync's wheel downloads starve and stall. `pixelart/song/models.py` has the per-model settings, including what a 16 GB card needs.

## Pipeline: lyrics -> song -> video

```sh
uv run python -m pixelart.new my-video                      # projects/my-video from _template
# write projects/my-video/lyrics.txt (lyric sheet) and style.txt (genre, voices, tempo)
uv run python -m pixelart.song.generate projects/my-video   # takes from YuE2 + ACE-Step XL, then a lyric check
# listen to build/takes/listen/*.m4a, read build/takes/report.md, pick one:
uv run python -m pixelart.song.pick projects/my-video acestep-xl-s2 --title "My Video"
uv run python -m pixelart.audio.analyze projects/my-video   # stems, beats, envelope, transcripts, timed lyrics
uv run python -m pixelart.render projects/my-video          # baseline lyric video -> projects/my-video/video.mp4
```

Then make it your own: replace `video.py`, iterating with `preview` and `sweep` (see below).

**Songs.** `lyrics.txt` uses `[Section]`, `[Section - Speaker]` or `[Section - Speaker: note]` headers. The models only get plain section tags, so put voices and delivery in `style.txt` as well. Each take is scored by how much of the lyric sheet Whisper hears in it. Some seeds come out garbled, so generate a few (`--seeds 1 2 3`) and listen before picking. Songs are capped at four minutes: `generate` estimates the length from the sung word count (about 650 words of rap fit) and refuses a longer lyric sheet unless you pass `--long`. A finished song from elsewhere (Suno, say) skips generation: `pick PROJECT path/to/song.wav`.

The models give a whole song one voice, so a duet or a battle comes out in one voice and one accent. `pixelart.song.repaint` regenerates some sections of a take in a different style and keeps the rest: generate the song in the first character's voice, then repaint the other character's sections (`--speaker "King George III" --style "... posh British accent ..."`). ACE-Step repaints each window with the rest of the take as context, so the beat carries across. `--window A:B` repaints a span in seconds instead, e.g. to redo lines a take dropped. Whisper can't hear accents, so judge repaints by ear.

**Analysis.** `analyze` skips steps whose output exists (`--force` redoes them). Whisper is primed with the proper nouns in `lyrics.txt`, or with the project's `prompt.txt` if it has one. The lyrics are aligned in one pass over the whole song. Whisper tends to start the first word after a pause while the singer is still silent, so word starts that land in a pause move to where the vocal stem gets loud again. The report marks lines that are mostly interpolated with `!`; these are usually chants or ad-libs Whisper can't hear. When that isn't good enough, write a per-song `align.py` with a time window per section and hand timings (`projects/alt-f4/align.py` is a worked example), and `analyze` leaves alignment to it. The single steps are also CLIs: `python -m pixelart.audio.{stems,beats,envelope,transcribe,align,tempo}`.

Demucs applies a random time shift, so regenerated stems (and the loudness envelope built from them) differ a little from run to run. Commit `data/` and treat it as the source of truth once a video depends on it.

Things to check by ear or eye: Suno renders are sometimes spliced mid-song, which makes a fixed-BPM grid drift. Use the tracked beats, and filter any spurious downbeats around the splice. There can also be a click in the last few frames, so set `END` to stop just before it.

## Working loop

```sh
uv run python -m pixelart.preview projects/alt-f4 v2 57:60:0.5 88.5   # times, or a:b:step ranges
uv run python -m pixelart.sweep   projects/alt-f4                      # every frame, ~10 s on 32 cores
uv run python -m pixelart.render  projects/alt-f4                      # ~45 s for 3:20 at 1080p24
```

`render` keeps finished segments in `build/segments` so an interrupted render can resume. After changing code, pass `--fresh`.

## Uploading

<a href="https://www.youtube.com/@pixelartrapbattles"><img src="https://www.gstatic.com/youtube/img/branding/youtubelogo/svg/youtubelogo.svg" alt="YouTube" height="24"></a>

The uploader uses YouTube API Services. By using it you agree to the [YouTube Terms of Service](https://www.youtube.com/t/terms). Its [privacy policy](PRIVACY.md) and [terms](TERMS.md) say what it accesses and stores, and the [Google Privacy Policy](http://www.google.com/policies/privacy) covers Google's side.

```sh
uv run python -m pixelart.youtube projects/two-georges --dry-run              # check the kit against YouTube's limits
uv run python -m pixelart.youtube projects/two-georges                        # upload private once you say yes, set the thumbnail
uv run python -m pixelart.youtube projects/two-georges --set-privacy public
uv run python -m pixelart.youtube projects/two-georges --set-thumbnail        # retry the thumbnail
uv run python -m pixelart.youtube --sign-out                                  # revoke access, delete the saved token
```

The title, description, tags and main thumbnail come from the project's upload kit, `thumbs/youtube_upload.txt`. An `ALTERED CONTENT` section in the kit sets YouTube's altered-content flag. Before anything is sent, the uploader names the channel and asks for a yes (`--yes` answers in advance). The video id is kept in `build/youtube.json`, so running the command again won't upload a duplicate.

Uploading needs a Google Cloud project with the YouTube Data API v3 enabled and an OAuth client of type Desktop. Save the client's JSON as `~/.config/pixelart/youtube_client_secret.json`. The first run opens a browser for consent and saves the token next to it (`PIXELART_CONFIG` moves both). If the consent screen is in Testing, the token expires after 7 days and the browser step comes back. YouTube restricts uploads from a Cloud project that hasn't passed its [API audit](https://support.google.com/youtube/contact/yt_api_form) to private, so upload privately and change the visibility by hand in YouTube Studio. Custom thumbnails need a phone-verified channel ([youtube.com/verify](https://www.youtube.com/verify)); until then the upload goes through without one.

## What to reuse from earlier videos

`pixelart/` only holds code that is independent of any one video's look. The camera (`camera.py`), the gag runner (`gags.py`), the animation helpers (`anim.py`), sprite canvases (`sprites.py`) and the comic text effects (`fx.py`) are shared already. A lot of alt-f4 and two-georges is reusable in spirit but tied to its characters and style, so it stays in those projects. Copy it and adapt it:

- `characters.py`: procedural chibi heads and bodies with pixel-art rules (4-connected outlines, crescent shading, rim light, mirrored facing)
- `props.py`: UI widgets such as speech and thought bubbles, stamps, Win95 windows, gradient "big text", keycaps and confetti
- `gagkit.py` and `video.py`: how a video wires up per-line gags (`pixelart.gags`), shots for the camera, hit reactions and karaoke
- two-georges' `characters.py` and `scene.py`: posable characters as cached sprites with anchors (hand, mouth, head), and a set drawn once and mirrored, animated per frame
- `thumbnail.py`: YouTube thumbnails in the video's style, with a sheet previewing them at YouTube's display sizes

If the same code gets copied into a second project, move it into `pixelart/` instead.
