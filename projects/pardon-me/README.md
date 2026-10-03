# Pardon Me

Donald Trump vs. Benjamin Netanyahu, a funky old-school rap battle on the floor of the UN General
Assembly. Both men are famous for holding up props at podiums (the cartoon bomb with its red line, the
Sharpie hurricane map, the tariff board), so the battle is fought with **visual aids**:

- **Whoever raps has the floor.** He stands at the rostrum with a flip chart on an easel beside him, and
  most of his punchlines are drawn on it in marker, live. The other man heckles from his delegation desk
  in the front row, behind a country placard. When the floor changes hands they cross the hall and swap
  places.
- **The two big screens are UN Web TV.** The left one carries the rapper's live close-up and the right one
  the heckler's, so every reaction is on screen without moving the camera. Gags take the screens over for
  archive clips, chyrons, scans and mugshots.
- **The President of the Assembly** sits on the dais behind the rostrum and bangs his gavel on every
  "Order!" and before each verse. The delegates in the front rows stand, cheer, "oooh" at the big
  punchlines and walk out.

The wide shot is home: the whole hall is in view for nearly the whole song, every gag plays inside it,
and the camera cuts in on the rapper only briefly.

- 320×180 native resolution, drawn procedurally, scaled up 6× (nearest-neighbour) to 1920×1080, 24 fps,
  3:52.
- Every lyric line has its own gag (`gags_*.py`), timed to its words.

## Song

ACE-Step 1.5 XL, made with the repo's song tools in three passes. The whole song was generated in Trump's
voice (`style.txt`: a brash, nasal New York rapper). Then Bibi's verses were repainted as a deep, slow,
formal statesman with an Israeli accent (the style is recorded in `data/song.json`), and Verse 4 was
repainted once more on its own:

```sh
uv run python -m pixelart.song.generate projects/pardon-me --models acestep-xl --seeds 1 2 3 4 --duration 232
uv run python -m pixelart.song.repaint  projects/pardon-me acestep-xl-s4 --speaker "Benjamin Netanyahu" \
    --name bibi --style "$BIBI" --seeds 1 2 3 4
uv run python -m pixelart.song.repaint  projects/pardon-me acestep-xl-s4+bibi-s3 --window 178.1:217.7 \
    --name v4 --style "$BIBI" --seeds 5 6 7 8 9 10 11 12 13 14 15 16
uv run python -m pixelart.song.pick     projects/pardon-me acestep-xl-s4+bibi-s3+v4-s15 --title "Pardon Me"
uv run python -m pixelart.audio.analyze projects/pardon-me
uv run python projects/pardon-me/align.py
```

`$BIBI` is the repaint style saved in `data/song.json`. Why these takes:

- Base `acestep-xl-s4`: the most natural pace (about 50 s a verse) at 89% lyric coverage. `s3` scored
  slightly better but raced through Verse 4 in 28 s.
- Repaint `bibi-s3`: the best Verse 2 (89%) and hook (88%) of the four. Its Verse 4 came out garbled.
- Verse 4 repaint `v4-s15`: the only one of twelve seeds that sings every line of Verse 4 (87% mean
  coverage). It sings "Seventeen percent on friendship?" twice, which the video keeps.

The repaint changes the accent and the delivery, not the pitch: a pitch check of the vocal stem put
Bibi's verses at about the same median pitch as Trump's.

### Timing quirks

- The song runs at 94 BPM, not the 96 in the style. `timeline.py` fits one fixed grid to Beat This!'s
  beats: a period of 0.638 s, with the first bar at 0.697 s.
- The take departs from the lyric sheet in three places, and `align.py` fixes each by hand:
  - The intro opens on a short burst that Whisper hears as "In the", then "General Assembly". The first
    line is shown as "In the General Assembly!", with no "Order! Order".
  - The hook sings "Pardon me? Pardon me!" where the sheet has "Pardon me? Pardon you!". After its last
    line the delegates chant "Pardon me!" seven more times (116.7-122.1 s), kept as two more hook lines
    marked `"chant": true`.
  - Verse 4 sings "Seventeen percent on friendship?" twice before "That's the Art of the Steal."
- Verse 3's last word and Verse 4's first are less than a second apart, so the swap walk overlaps the start
  of Verse 4's first line.

## Rendering

The song is not in git. Put it at `audio/song.wav`. Then, from the repo root:

```sh
uv run python -m pixelart.render  projects/pardon-me              # -> projects/pardon-me/pardon-me.mp4
uv run python -m pixelart.preview projects/pardon-me v2 66:80:2
uv run python -m pixelart.sweep   projects/pardon-me              # every frame, for exceptions
uv run python projects/pardon-me/characters.py                    # -> build/cast.png
uv run python projects/pardon-me/hall.py                          # -> build/hall.png
uv run python projects/pardon-me/art.py                           # -> build/art.png (and art_v1.py ... art_ends.py)
uv run python projects/pardon-me/thumbnail.py                     # -> thumbs/ (YouTube thumbnails)
uv run python -m pixelart.youtube projects/pardon-me --dry-run    # check the upload kit
```

To load only some gag modules while you work on them, set `GAGS_ONLY=gags_v1,gags_hook`.

## Files

| File | Role |
| --- | --- |
| `project.py` | Settings read by the pixelart tools (the renderer loads on first use, so `analyze` runs before `data/` exists) |
| `engine.py` | Canvas size, palette, fonts and drawing helpers |
| `timeline.py` | Beat grid, sections and who holds the floor, lyric lines, punchline hits, vocal loudness |
| `video.py` | The frame renderer: staging, the swap walks, the screens' live feeds, the gavel, the flip chart, karaoke and section cards |
| `hall.py` | The General Assembly hall: the wall, emblem, screens, dais, rostrum, easel, desk and placard, the President and the delegates |
| `characters.py` | Trump and Bibi: poses, expressions, outfits and hats |
| `props.py` | The marker kit for the flip chart, cards, Truth Social posts, stamps, confetti; text effects |
| `art.py` | Sprites more than one section uses: turkeys, the medal, the escalator, signs, markers |
| `gagkit.py` | Helpers for the gag modules |
| `gags.py` | Loads the gag modules |
| `gags_intro.py`, `gags_v1.py` ... `gags_v4.py`, `gags_hook.py`, `gags_outro.py` | One gag per lyric line, section by section, and the end card |
| `art_v1.py` ... `art_v4.py`, `art_ends.py` | The sprites that only one section's gags use (`art_ends.py`: the intro, hook, outro and end card) |
| `thumbnail.py` | YouTube thumbnails, built from the video's own drawing code |
| `thumbs/youtube_upload.txt` | The YouTube upload kit: title, description with chapters and lyrics, tags |
| `align.py` | Hand fixes to the lyric timing |
