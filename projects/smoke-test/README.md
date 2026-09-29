# Lyrics In, Video Out

A 30-second demo of the whole pipeline: a lyric sheet and a style line go in, and a lyric video comes out, with no hand edits. It is `projects/_template` as-is, running on a song generated locally.

- Song: `lyrics.txt` + `style.txt` -> ACE-Step 1.5 XL turbo, seed 2 (`data/song.json`). `audio/` is not committed.
- Look: the template's baseline lyric video. Karaoke lines and speaker tags come from `data/lyrics_timed.json`, section cards from the lyric sheet's headers, and the star hops on the tracked beats and glows with the vocal envelope.
- Render: `uv run python -m pixelart.render projects/smoke-test`

## How it was made

```sh
uv run python -m pixelart.new smoke-test
# wrote lyrics.txt and style.txt
uv run python -m pixelart.song.generate projects/smoke-test --seeds 1          # then --seeds 2 3 and 4 for more takes
uv run python -m pixelart.song.pick projects/smoke-test acestep-xl-s2 --title "Lyrics In, Video Out"
uv run python -m pixelart.audio.analyze projects/smoke-test
uv run python -m pixelart.render projects/smoke-test
```

## Notes

- Takes vary a lot by seed. The lyric check heard 94% of the words in ACE-Step XL seed 2 (6% WER), but only "Thank you." in seed 1: Whisper's usual hallucination on unintelligible vocals. YuE2 seed 1 covered every word but repeated the chorus (24% WER).
- Left to choose the length itself, ACE-Step's planner gave this verse and chorus 18 s and cut most of the verse. `generate` now passes a length estimated from the word count.
- Auto-alignment matched 48 of the 50 sung words.
