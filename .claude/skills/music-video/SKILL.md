---
name: music-video
description: Run the lyrics -> song -> pixel-art music video pipeline in the pixelart repo (~/claude/pixelart-repo) - write a lyric sheet and style, generate song takes locally with YuE2 and ACE-Step, check and pick a take, analyse beats/stems/word timings, render a baseline lyric video, then design a custom one. Use when the user wants a song or music video made from lyrics, wants to turn a Suno/finished song into a video, asks for more takes of a song, or mentions the pixelart pipeline.
---

# Lyrics -> song -> music video

The toolkit is the pixelart repo at `~/claude/pixelart-repo` (public: github.com/gdoteof/pixelart). Read its
`CLAUDE.md` and `README.md` before changing code. Run every command from the repo root with `uv run`.
The song models live outside the repo in `~/claude/local-music/` (`PIXELART_MODELS`), each with its own venv.

The user makes the creative calls: lyrics, style, which take, the look of the video. Draft options and
make recommendations, but stop and let them decide at each checkpoint below.

## 1. Project, lyrics, style

```sh
uv run python -m pixelart.new NAME        # projects/NAME from projects/_template
```

- `lyrics.txt`: a lyric sheet. Headers are `[Section]`, `[Section - Speaker]` or `[Section - Speaker: note]`,
  where Section starts with Intro/Verse/Pre-Chorus/Chorus/Hook/Bridge/Outro/...; other bracketed lines like
  `[crowd roars]` are stage directions, not sung. Speakers and sections feed the video (speaker tags,
  section cards); `pixelart/lyrics.py` has the rules.
- `style.txt`: one line of genre, instruments, vocal character, delivery and tempo ("... 91 BPM").
  The models only see plain section tags, so per-verse voice notes are lost. Put the voices in the style
  too, and expect one vocalist unless the user accepts that.
- When the song features real people, agree on content limits with the user first. Check memory for
  limits set on earlier projects. The repo is public, so ask whether the limits go in the project
  README or stay private in memory (alt-f4 keeps them private).

**Checkpoint:** the user approves the lyrics and style.

## 2. Generate takes

```sh
uv run python -m pixelart.song.generate projects/NAME     # YuE2 + ACE-Step XL, seeds 1 2
uv run python -m pixelart.song.generate projects/NAME --models acestep-xl --seeds 3 4 5   # more takes
```

- Takes go to `build/takes/`. Loudness-matched m4a copies go to `build/takes/listen/`, and
  `build/takes/report.md` ranks the takes by lyric coverage and WER (Whisper).
- A 3-minute song takes about 100 s per YuE2 take and about 40 s per ACE-Step XL take, plus model loading.
  Only one GPU job at a time: the desktop already holds about 2.7 GB of the 16 GB card.
- Some seeds come out duds: garbled vocals, or Whisper hearing only "Thank you." When that happens,
  generate more seeds rather than rewriting the style.
- ACE-Step's length is estimated from the word count; override it with `--duration`.
- The report measures diction, not quality.

**Checkpoint:** give the user the `listen/` path and the report, then let them pick by ear.

## 3. Pick and analyse

```sh
uv run python -m pixelart.song.pick projects/NAME acestep-xl-s2 --title "Song Title"   # or a path to a Suno file
uv run python -m pixelart.audio.analyze projects/NAME     # stems, beats, envelope, transcripts, auto-align
```

- `analyze` needs `uv sync --extra audio` (done once per checkout). It skips steps whose output already
  exists; use `--force` to redo them.
- It prints the timed lyric lines. Lines marked `!` are mostly interpolated. Usually these are chants,
  ad-libs or crowd parts Whisper can't hear, so check them against the audio.
- If many lines are off, write a per-song `align.py` with section windows and hand timings
  (`projects/alt-f4/align.py` is the worked example). `analyze` then leaves alignment to it.
- `data/` is the source of truth once a video depends on it; `audio/` and `build/` are not committed.

## 4. Baseline video

```sh
uv run python -m pixelart.render projects/NAME            # -> projects/NAME/video.mp4
```

The template already makes a working lyric video: karaoke lines, speaker tags, section cards, and a
star that hops on beats and glows with the vocals. Show it to the user early.

## 5. Custom video

Design the look with the user. Then replace `video.py`, reusing what fits from `projects/alt-f4`:
characters, props, per-line gag generators, the camera and thumbnails.

The loop:
- `uv run python -m pixelart.preview projects/NAME tag 12 30:40:2`, then read the contact sheet image
  to check every change visually.
- `uv run python -m pixelart.sweep projects/NAME` to catch exceptions on any frame.
- `render --fresh` after code changes.

If you copy code from alt-f4 into a second project, move it into `pixelart/` instead.

## 6. Wrap up

- Update the project README with which take was picked and why, and the timing quirks. Add the content
  limits too if the user agreed to publish them.
- Make thumbnails and the upload kit (`thumbs/youtube_upload.txt`) if the video is going on YouTube.
  `python -m pixelart.youtube PROJECT --dry-run` checks the kit, and without `--dry-run` it uploads
  privately after a yes at its prompt: pass `--yes` only when the user has asked for this upload. The
  user makes it public in YouTube Studio, so don't change its privacy.
- Ask before committing or pushing: the repo is public.
