# Two Georges

King George III and George Washington in a four-verse rap battle across the Atlantic. The King raps from
the London quay and the General from a Boston wharf, with the sunset between them. There is a gag for
each lyric line, and the things they throw at each other stay floating in the sea. For the last verse
they board their ships (Alfred and Royal George) and the battle becomes a sea duel. The outro gives
what happened next.

- 320×180 native resolution, drawn procedurally, scaled up 6× (nearest-neighbour) to 1920×1080, 24 fps, 4:40.
- Boston (west) is always on the left and London (east) on the right, as on a map.
- The lyrics stick to the record (Fort Necessity, the Olive Branch Petition, Herschel's planet, the Nicola
  letter, Washington's will...), and so do the dates and captions in the gags. Wood-teeth
  and cherry-tree style myths are labelled as myths.

## Song

ACE-Step 1.5 XL, made with the repo's song tools in three passes. The whole song was generated in
Washington's American voice (`style.txt`). The King's verses were then repainted in a posh British voice
(its style is recorded in `data/song.json`). Finally the span 160.9–169.8 s was repainted again because
that take had dropped the King's last lines:

```sh
uv run python -m pixelart.song.generate projects/two-georges --models acestep-xl --seeds 1 2 3
uv run python -m pixelart.song.repaint  projects/two-georges acestep-xl-s2 --speaker "King George III" \
    --name gb --style "$BRITISH" --seeds 1 2
uv run python -m pixelart.song.repaint  projects/two-georges acestep-xl-s2+gb-s1 --window 160.9:169.8 \
    --name fix --style "$BRITISH" --seeds 1 2 3 4
uv run python -m pixelart.song.pick     projects/two-georges acestep-xl-s2+gb-s1+fix-s4 --title "Two Georges"
uv run python -m pixelart.audio.analyze projects/two-georges
```

`$BRITISH` is the repaint style saved in `data/song.json`. `acestep-xl-s2+gb-s1` was picked by ear from the
repainted takes. Its `fix` repaints put the dropped lines back, and `fix-s4` scored best of the four in
the lyric check. The Town Crier's intro came out in a second voice without being asked.

## Rendering

The song is not in git. Put it at `audio/song.wav`. Then, from the repo root:

```sh
uv run python -m pixelart.render  projects/two-georges            # -> projects/two-georges/two-georges.mp4
uv run python -m pixelart.preview projects/two-georges v2 70:115:3
uv run python -m pixelart.sweep   projects/two-georges            # every frame, for exceptions
uv run python projects/two-georges/characters.py                  # -> build/cast.png
uv run python projects/two-georges/thumbnail.py                   # -> thumbs/
```

To load only some gag modules while you work on them, set `GAGS_ONLY=gags_v1,gags_v2`.

## Files

| File | Role |
| --- | --- |
| `project.py` | Settings read by the pixelart tools |
| `engine.py` | Canvas size, palette, fonts and drawing helpers |
| `timeline.py` | Beat clock, sections, lyric lines, punchline hits, vocal loudness |
| `characters.py` | The King, the General and the Town Crier: poses, expressions, hats and crowns |
| `scene.py` | The two shores, the animated sea, flags, weather, ships and gulls in the background |
| `ships.py` | The Verse 4 ship duel: Alfred and Royal George, damage stages, volleys, nightfall |
| `props.py` | Gag props (documents, stamps, cannonballs, tea...) and things that float |
| `video.py` | Frame renderer: shots, posing, hit reactions, karaoke, verse cards, debris, mood |
| `gagkit.py`, `gags*.py` | Per-lyric-line gags (generators that yield their drawing phase), one module per section |
| `thumbnail.py` | YouTube thumbnails (`thumbs/`, with the title, description and tags in `thumbs/youtube_upload.txt`) |
| `align.py` | This song's lyric timing: the automatic alignment plus hand fixes |
| `lyrics.txt`, `style.txt` | The lyric sheet and the base song style |
| `data/` | Beat grid, Whisper transcripts, timed lyrics, vocal envelope, song metadata |

## Tone

It's a roast, but the lines about slavery aren't played for laughs. Those are Verse 3 lines 10, 11, 13
and 14 (Harry Washington, "property", the teeth) and Verse 4 lines 0–3 (the slave trade, Washington's
will). On them:
- the world dims;
- the listener doesn't flinch and the screen doesn't shake;
- the gags are documents, dates and quotes, not slapstick.

The debris from the first three verses sinks as Verse 4 opens, so the sea is clear for those lines. The
King's illness gets the same restraint: his restraining chair is shown empty, as a museum caption, and he
is never shown in it.

## Timing quirks

- The beat tracker hears the 142 BPM drill beat in half time (about 71 BPM). `timeline.half` gives the fast pulse.
- `pixelart.audio.align` moves word starts that Whisper put in pauses onto the vocal onsets.
- In Verse 1 line 15, Whisper heard the reverb tail as two more "I'm done"s, and the aligner took the
  last one. `align.py` puts it back at 66.7 s.
- Washington's last word in Verse 2 is at 116.58 s and the King comes in at 116.86 s, so a verse starts
  no earlier than just after the previous verse's last word (`timeline._sections`).
- The vocals end at about 245 s and the rest is an instrumental outro. The music fades out between 274
  and 278 s, and the picture fades to black between 273.4 and 277 s, just ahead of it.
