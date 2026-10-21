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
- A cut-off, a bleep or a buzzer is a post effect. A song model sings "My name is Pew..." as a line
  that trails off, so the interruption never lands. Write the line whole, mark the cut with a stage
  direction, and cut it short once the take is picked and analysed:
  `uv run python -m pixelart.audio.bleep projects/NAME --words 0:12` lists the word times, and
  `... bleep projects/NAME 3.42:4.6` swaps the song for its backing in that span and adds a buzzer.
- A sound effect is a post effect too: the model sings "(Clap, clap!)" as two words. Leave the words in
  the sheet, so the take has room for the sound, and swap each one for a clap by naming the sound on
  its span: `... bleep projects/NAME 3.42:4.6 52.2:52.5:clap 52.5:52.7:clap`. Every run starts again
  from the take as picked, so give all the spans each time. If the sound can't be made, cut the bar
  rather than have it read out.
- A word with two readings ("live", "read", "tear") comes out as whichever the model picks. Give the
  model a spelling it can only say one way in the project's `say.txt` (`bridge, live. = bridge, life.`):
  `generate` and `repaint` read it, and the sheet and the captions keep the real word. To fix one line
  of a take the user otherwise likes, `pixelart.song.repaint ... --window A:B` re-sings that span.
- Write for laughs and rhymes, not a history lesson. Read [lyric-craft.md](lyric-craft.md) before
  drafting. It distils 27 reference songs (ERB, Hamilton, diss tracks, wordplay showcases, comedy rap, UK drill)
  into rules for a bar, joke techniques, a scoring rubric and a workflow. Don't model a sheet on our
  earlier videos: all four fall short of the references, and the guide's failure table quotes them.
- Follow the guide's workflow: one charge per rapper, three times the jokes you need, then score and
  pick. Measure the draft with `uv run python -m pixelart.song.bars projects/NAME/lyrics.txt --bars`
  and fix its flags. Then have the `lyric-critic` agent score it cold, revise, and show the user the
  sheet with the critic's scores.
- Every song needs its own jokes and references. Don't open an earlier project's `lyrics.txt` while
  drafting: the header syntax is above, and a sheet drafted next to an old one picks up its hook and
  its pet words. Check the draft with `uv run python -m pixelart.song.fresh projects/NAME`, which lists
  the names, phrases and words it shares with every earlier sheet (never their lines), and rework
  what it finds. When a character returns from an earlier song, run
  `uv run python -m pixelart.song.fresh --spent OLDNAME` before drafting and treat the references in
  that list as used up: the same famous facts come to mind first.
- When a news story prompts the matchup, it is the occasion, not the song: give it about a fifth of
  the bars (an intro gag, a few bars each, the outro). The rest is the two people's whole careers and
  personas, with brags as well as digs.
- Open on verse 1 and run the verses back to back. An `[Intro]` kept the drums and bass out for 14 to
  40 seconds on every take of Out of Your League, and a hook that only repeats is where viewers
  leave: its three were cut. Put a framing gag in the picture, and say a title line once, in a verse.
- Aim for about 3:30, give or take 25 seconds: 530-570 sung words for rap (Round 2 is 534 words and
  3:25; Blue on Blue's 337 words came out at 2:24, too short). Four minutes is the cap: `generate`
  refuses a sheet that runs longer, so cut verses rather than passing `--long`.
- `style.txt`: one line of genre, instruments, vocal character, delivery and tempo ("... 91 BPM").
  The models only see plain section tags, so per-verse voice notes are lost. Put the voices in the style
  too, and expect one vocalist unless the user accepts that. Ask for a sincere, confident delivery, not
  a comedic one: the music plays the straight man.
- When the rapper is a woman, name her voice first ("female rapper, bright confident young woman's
  voice, high clear female vocals"). "Cool low voice" and "deadpan menace" got a man's voice.
- The tempo sets the flow: the models put one bar of the sheet in one bar of music. At 140 BPM that
  is 1.7 seconds for eleven syllables, too fast to follow; 90 to 100 BPM gives about 2.5 seconds.
- When the song features real people, follow the user's standing rule on content limits in memory.
  Don't ask about limits again for each project, and don't carry rules over from an earlier one.
  The repo is public, so limits stay in memory, not in the project README.

**Checkpoint:** the user approves the lyrics and style.

## 2. Generate takes

```sh
uv run python -m pixelart.song.generate projects/NAME     # YuE2 + ACE-Step XL, seeds 1 2
uv run python -m pixelart.song.generate projects/NAME --models acestep-xl --seeds 3 4 5   # more takes
uv run python -m pixelart.song.generate projects/NAME --style club    # styles/club.txt -> <model>-club-s<seed>
```

- Takes go to `build/takes/`. Loudness-matched m4a copies go to `build/takes/listen/`, and
  `build/takes/report.md` ranks the takes by lyric coverage and WER (Whisper).
- A 3-minute song takes about 100 s per YuE2 take and about 40 s per ACE-Step XL take, plus model loading.
  Only one GPU job at a time: the desktop already holds about 2.7 GB of the 16 GB card.
- Some seeds come out duds: garbled vocals, or Whisper hearing only "Thank you." When that happens,
  generate more seeds rather than rewriting the style.
- ACE-Step's length is estimated from the word count; override it with `--duration`.
- The report measures diction, not quality. Before handing takes over, also check each one line by
  line (ACE-Step XL drops whole verses on most seeds, so run four or more), when its first word and
  its bass land, and whether the voice is the one asked for: about half of ACE-Step's takes of a
  female style came out male.
- YuE2 often opens with ten to twenty seconds of wordless singing. Cut it before `pick`, a bar before
  the first word, and give the cut file its own take name and JSON (`base`, `trim_start`).
- Offer two or three styles when the first doesn't land: one line each in `styles/NAME.txt`.

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
  When only some words are off (a held word, an echo, the first word after a pause), keep the
  automatic alignment and move those: `pixelart.audio.align.hand_fixed` and `set_starts`
  (`projects/play-the-video/align.py`).
- The whole-song transcript mishears crowd and chant parts. Before calling a punchline word mis-sung,
  transcribe that bar alone from the vocal stem, with and without the line as a prompt. Give the user
  the timestamps either way: their ear decides.
- `data/` is the source of truth once a video depends on it; `audio/` and `build/` are not committed.
- `bleep` records its spans in `data/song.json` as `cuts`, for the video to stamp on. In
  `data/lyrics_timed.json` a word in asterisks (`*BZZT*`, `*CLAP*`) is a sound laid over the song, not
  a sung word: captions show it without the asterisks, in another colour, once it sounds
  (`projects/great-question/align.py` writes them, `video.py` draws them).

## 4. Baseline video

```sh
uv run python -m pixelart.render projects/NAME            # -> projects/NAME/video.mp4
```

The template already makes a working lyric video: karaoke lines, speaker tags, section cards, and a
star that hops on beats and glows with the vocals. Show it to the user early.

## 5. Custom video

Design the look with the user. Then replace `video.py`, reusing what fits from `projects/alt-f4`:
characters, props, per-line gag generators, the camera and thumbnails. `projects/great-question` is
a worked example of one fixed frame: two seated figures (`pixelart.figure`: a torso, a head and arms
posed by named gestures) either side of a screen that shows a picture for every bar, with
`timeline.py` built on `pixelart.songtime.Song` and one `gags_<section>.py` per section.

Keep the camera calm, so it's always clear what the viewer is looking at. Alt-F4 reads best of the
three videos: it cuts often, but between a few fixed framings, and it stays in a wide shot with both
rappers and the gag in view for over 90% of the song. Two Georges and Narrators were zoomed in for
about half their running time and glided back and forth between the rapper and the gag. Narrators also
drifted constantly (handheld sway, gate weave). Both came out jumpy and hard to follow. So:
- The wide shot is home. Zoom in only on the rapper who's rapping, and only briefly.
- Play gags inside the wide frame, or in an inset. Don't fly the camera over to them.
- Cut rather than glide. Shake only on hits, never as constant drift.

End a few seconds after the last line. Song models often repeat a closing line or play on for ten
seconds or more, and filling that tail drags (Round 2's ending ran 34 seconds). Set `END` in
`project.py` a few seconds after the last word, and `FADE` to fade the song out under the end card.
`AUDIO_END` stops the sound before the picture ends (Play the Video stops dead on its last word).

The loop:
- `uv run python -m pixelart.preview projects/NAME tag 12 30:40:2`, then read the contact sheet image
  to check every change visually.
- `uv run python -m pixelart.sweep projects/NAME` to catch exceptions on any frame. Run it before every
  render: a gag that is still alive during the next line, and asks that line about its own words,
  fails only on those frames.
- Read text at its real size. A sheet of twelve full frames is scaled down until small print can't be
  judged, so crop to the picture being checked and enlarge it (six frames, or 24 crops, per sheet).
- A take sings its verses back to back, with none of the gaps a draft grid has. After retiming, look
  at the first and last half second of every bar: the gag before is still alive there, and what it
  draws over the frame (a label, a clip's progress bar, a shake) lands on the next bar's picture.
- `render --fresh` after code changes.

If you copy code from alt-f4 into a second project, move it into `pixelart/` instead.

## 6. Wrap up

- Update the project README with which take was picked and why, and the timing quirks. Content limits
  stay in memory, out of the README.
- Make thumbnails and the upload kit (`thumbs/youtube_upload.txt`) if the video is going on YouTube.
  `python -m pixelart.youtube PROJECT --dry-run` checks the kit, and without `--dry-run` it uploads
  privately after a yes at its prompt: pass `--yes` only when the user has asked for this upload. The
  user makes it public in YouTube Studio, so don't change its privacy.
- Ask before committing or pushing: the repo is public.
