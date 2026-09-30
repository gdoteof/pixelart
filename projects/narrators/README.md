# Attenborough vs. Freeman

Sir David Attenborough and Morgan Freeman, the two most famous narrators alive, in a slow boom-bap
rap battle. Whoever is rapping holds the camera:

- **Sir David's verses are his nature documentary.** A field camera's viewfinder (REC, timecode, zoom),
  lower thirds with Latin names, teletext subtitles, handheld telephoto shots. Morgan is the specimen,
  *Morganus freemanii*, observed in a vocal booth someone has left in a jungle clearing. Sir David
  presents from the ferns with a fluffy field mic.
- **Morgan's verses are his films.** Letterbox bars, a warm grade with grain and gate weave, subtitles in
  the bar, title cards. Sir David is cast as the lead: the new fish in *The BBC Redemption* (Verse 2) and
  the passenger in *Driving Mr. David* (Verse 4).
- **The changes of verse are hijacks.** The film burns through the documentary, the documentary jams the
  film with static and takes the channel back, and a clapperboard snaps shut on the documentary.
- **The instrumental before the outro is the film's end credits.** The outro plays after them as a
  post-credits scene in heaven, where God (Morgan) has won the planet trophy from the intro. In the last
  shot Sir David's REC blinks on again.

Every lyric line has its own gag. Big punchlines cut to the target's reaction wherever the gag has taken
the picture: a "CAM 2" hidden-camera inset in the documentary, an iris in the film.

- 320×180 native resolution, drawn procedurally, scaled up 6× (nearest-neighbour) to 1920×1080, 24 fps,
  5:43.
- The references are to the record: Life on Earth, the Red List, *Attenborosaurus*, *Nepenthes
  attenboroughii*, the RRS Sir David Attenborough (Boaty McBoatface), March of the Penguins, the sat-nav
  voice, and the films.

## Song

ACE-Step 1.5 XL, made with the repo's song tools in two passes. The whole song was generated in
Morgan's voice (`style.txt`: a deep, warm American baritone). Then Sir David's sections (intro, Verses 1
and 3) were repainted as a hushed, posh British narrator (the style is recorded in `data/song.json`):

```sh
uv run python -m pixelart.song.generate projects/narrators --models acestep-xl --seeds 1 2 3 4
uv run python -m pixelart.song.repaint  projects/narrators acestep-xl-s1 --speaker "David Attenborough" \
    --name gb --style "$BRITISH" --seeds 1 2 3 4
uv run python -m pixelart.song.pick     projects/narrators acestep-xl-s1+gb-s4 --title "Attenborough vs. Freeman"
uv run python -m pixelart.audio.analyze projects/narrators
uv run python projects/narrators/align.py
```

`$BRITISH` is the repaint style saved in `data/song.json`. Seed 4 was also repainted (`acestep-xl-s4+gb-...`).
`acestep-xl-s1+gb-s4` was picked by ear. It was also the best-scoring repaint in the lyric check (91%
coverage). The two voices differ by accent and delivery more than by pitch: a pitch check of the vocal
stem put them close together, with Sir David's slightly higher. Repaints that asked for a deeper Morgan
(`+deep`) came out higher and less clear, so they were dropped.

### Timing quirks

- The song runs at 75 BPM, not the 78 in the style. Beat This! counts quarter notes for the first half and
  eighth notes after that. `timeline.py` fits one fixed grid to all of its beats: a period of 0.800 s,
  with the first bar at 1.674 s.
- The take departs from the lyric sheet twice, and `align.py` fixes both by hand. The intro never sings
  "The other narrated heaven." Verse 3 sings the "four planets / take a nap" couplet twice. The repeat is
  kept as two lines marked `"replay": true` (section `v3r`), and the video shows them as the
  documentary's action replay.
- The instrumental from about 299 s to 313 s is the end credits. The last word ("I made it") is at 330.8 s,
  and the end card runs to 343 s.

## Rendering

The song is not in git. Put it at `audio/song.wav`. Then, from the repo root:

```sh
uv run python -m pixelart.render  projects/narrators              # -> projects/narrators/narrators.mp4
uv run python -m pixelart.preview projects/narrators v2 90:110:2
uv run python -m pixelart.sweep   projects/narrators              # every frame, for exceptions
uv run python projects/narrators/characters.py                    # -> build/cast.png
uv run python projects/narrators/critters.py                      # -> build/critters.png
uv run python projects/narrators/thumbnail.py                     # -> thumbs/ (YouTube thumbnails)
```

To load only some gag modules while you work on them, set `GAGS_ONLY=gags_links,gags_v1`.

## Files

| File | Role |
| --- | --- |
| `project.py` | Settings read by the pixelart tools |
| `engine.py` | Canvas size, palette, fonts and drawing helpers |
| `timeline.py` | Beat grid, sections and their mode (doc or film), lyric lines, punchline hits, vocal loudness |
| `video.py` | The frame renderer: sets, cast, camera, reaction insets, and each mode's screen furniture |
| `chrome.py` | The two screen languages: viewfinder, lower thirds, IUCN scale, teletext; letterbox, grade, titles, credits |
| `characters.py` | Sir David and Morgan: poses, expressions, outfits (field, prison, god, chauffeur...) and hats |
| `critters.py` | The wildlife: gorilla, penguin, T. rex, whale, lion, rat, birds |
| `sets.py` | The home sets: the jungle clearing with its vocal booth, the prison yard, the car, heaven |
| `props.py` | The planet trophy, globes, TVs, posters, books, the toe tag, the clapperboard; text effects |
| `gagkit.py` | Helpers for the gag modules |
| `gags_links.py` | The hijacks between verses, the film titles and the end credits |
| `gags_intro.py`, `gags_v1.py` ... `gags_v4.py`, `gags_outro.py` | One gag per lyric line, section by section |
| `v2_art.py`, `v3_sets.py`, `v3_sets2.py`, `v4_art.py` | The sets and art that only one verse's gags use |
| `thumbnail.py` | YouTube thumbnails, built from the video's own drawing code |
| `align.py` | Hand fixes to the lyric timing |
