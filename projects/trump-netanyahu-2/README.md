# Trump vs Netanyahu Round 2

The rematch of [Pardon Me](../pardon-me/). Donald Trump and Benjamin Netanyahu are both campaigning for
the Nobel Peace Prize, so they fight for it where they really meet: side by side in the gold armchairs in
the Oval Office, the way every visiting leader sits for the cameras. Cable news carries it live as a
prize fight, and Barack Obama, who already has one, drops in for the bridge.

- **The sit-down.** Both men stay in their armchairs in front of the fireplace for the whole song. The
  rapper holds up his visual aids (folders, posters, letters, tickets) and the other one reacts.
- **The broadcast.** A LIVE bug, a lower third naming whoever has the mic, the lyrics in the crawl band,
  a ticker of headlines, and section cards ("DEVELOPING: NETANYAHU HITS BACK"). Gags play in the wide
  shot or in a broadcast inset (the handshake, the golf cam, the official merch), and the portrait
  over the mantel changes to suit.
- **The fight.** A ring announcer opens it with the bell, a yank-and-pat handshake and a pose for the
  cameras. He comes back to read the decision. The press pool rises in the foreground to chant the hook
  and to watch the decision.
- **The prize.** It goes to the turkey Trump pardons in Verse 1: no wars, no trial, no drones. The men
  sulk and the turkey gobbles on the coffee table under the end card.

The caricatures are built from each man's mannerisms:
- **Trump:** tiny hands in huge sleeves, the orange tan with pale rings round the eyes, the hair wave,
  the squint and pout, the accordion hands, the pinch and the double thumbs-up.
- **Bibi:** the stern brow, the chin rest and the side-eye.
- **Obama:** the ears, the grin and the tan suit.

The wide shot is home, and the camera cuts in on the rapper only briefly.

- 320×180 native resolution, drawn procedurally, scaled up 6× (nearest-neighbour) to 1920×1080, 24 fps,
  3:25.
- Every lyric line has its own gag (`gags_*.py`), timed to its words.

## Song

ACE-Step 1.5 XL, made with the repo's song tools in three passes. The whole song was generated in Trump's
voice (`style.txt`: a brash, raspy New York rapper). Then Bibi's verses were repainted as a deep, slow,
formal statesman with an Israeli accent, and the bridge as Obama, a mellow baritone with professorial
pauses:

```sh
uv run python -m pixelart.song.generate projects/trump-netanyahu-2 --models acestep-xl --seeds 1 2 3 4 5 6 --duration 205
uv run python -m pixelart.song.repaint  projects/trump-netanyahu-2 acestep-xl-s4 --speaker "Benjamin Netanyahu" \
    --name bibi --style "$BIBI" --seeds 1 2 3 4 5 6
uv run python -m pixelart.song.repaint  projects/trump-netanyahu-2 acestep-xl-s4+bibi-s2 --speaker "Barack Obama" \
    --name obama --style "$OBAMA" --seeds 1 2 3 4 5 6
uv run python -m pixelart.song.pick     projects/trump-netanyahu-2 acestep-xl-s4+bibi-s2+obama-s1 \
    --title "Trump vs Netanyahu Round 2"
uv run python -m pixelart.audio.analyze projects/trump-netanyahu-2
uv run python projects/trump-netanyahu-2/align.py
```

`$BIBI` and `$OBAMA` are the repaint styles saved in `data/song.json` (`base_style` and `style`). Why
these takes:

- **Base `acestep-xl-s4`:** picked by ear from the six seeds. The report's diction scores for the six were
  within four points of each other (89.5-93.1% lyric coverage).
- **Bibi `bibi-s2`:** the best diction across both of his verses (Verse 2 94%, Verse 4 97% coverage).
  `s5` and `s4` came within a point or two, so either could stand in if one sounds better.
- **Obama `obama-s1`:** 98% coverage over the bridge. `s4` scored the same but sings "Afghanistan" twice.

The listening copies of every take are in `build/takes/listen/`, and `build/takes/report.md` ranks them.

### Timing quirks

- The song holds the 92 BPM it was asked for. `timeline.py` fits one fixed grid to Beat This!'s beats, a
  period of 0.652 s (`pixelart/songtime.py`).
- After the intro's last word (23.4 s) the band plays alone for eleven seconds, and Verse 1 starts at
  35.1 s. The video fills the gap with the bell, the handshake (the yanks and pats land on the beat) and a
  pose for the cameras. The aligner squeezed Verse 1's first lines into the end of the gap, so `align.py`
  times them by hand.
- The outro sings its last line twice, dropping one item each time: "No wars, no trial, and he still got
  a pardon", then "No wars, no drones, and he still got a pardon". `align.py` splits the sheet's one line
  into the two that are sung.
- The hook is chanted, so Whisper hears only half its words. Its lines keep the aligner's interpolated
  times, which match the chant.
- The band plays on for fourteen seconds after the last word (190.6-205 s). The turkey takes the coffee
  table and gobbles under the end card.

## Rendering

The song is not in git. Put it at `audio/song.wav`. Then, from the repo root:

```sh
uv run python -m pixelart.render  projects/trump-netanyahu-2      # -> trump-vs-netanyahu-round-2.mp4
uv run python -m pixelart.preview projects/trump-netanyahu-2 v2 66:80:2
uv run python -m pixelart.sweep   projects/trump-netanyahu-2      # every frame, for exceptions
uv run python projects/trump-netanyahu-2/characters.py            # -> build/heads.png, build/cast.png
uv run python projects/trump-netanyahu-2/office.py                # -> build/office.png
uv run python projects/trump-netanyahu-2/props.py                 # -> build/props.png
uv run python projects/trump-netanyahu-2/thumbnail.py             # -> thumbs/ (YouTube thumbnails)
uv run python -m pixelart.youtube projects/trump-netanyahu-2 --dry-run   # check the upload kit
```

To load only some gag modules while you work on them, set `GAGS_ONLY=gags_v1,gags_hook`.

## Files

| File | Role |
| --- | --- |
| `project.py` | Settings read by the pixelart tools (the renderer loads on first use, so `analyze` runs before `data/` exists) |
| `engine.py` | Canvas size, palette and fonts |
| `timeline.py` | Beat grid, sections, lyric lines, punchline hits, vocal loudness (draft timing before a take is picked) |
| `video.py` | The frame renderer: the sit-down, the standing guests, the press pool, the broadcast graphics, karaoke and section cards |
| `office.py` | The Oval Office: the wall, the portraits, the fireplace and mantel, the armchairs and the coffee table |
| `characters.py` | Trump, Bibi, Obama and the announcer: heads, expressions, seated and standing poses, gestures, held props |
| `props.py` | Everything the gags hold up, hand over, throw or show in an inset |
| `gagkit.py` | Helpers for the gag modules |
| `gags.py` | Loads the gag modules |
| `gags_intro.py`, `gags_v1.py` ... `gags_v4.py`, `gags_hook.py`, `gags_bridge.py`, `gags_outro.py` | One gag per lyric line, section by section, and the ending |
| `thumbnail.py` | YouTube thumbnails, built from the video's own drawing code |
| `thumbs/youtube_upload.txt` | The YouTube upload kit: title, description with chapters and lyrics, tags |
| `align.py` | Hand fixes to the lyric timing |
