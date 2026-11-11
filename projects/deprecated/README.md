# Deprecated

A rowdy pub shanty for the programmers the machine replaced: "deprecated, and we still run". A solo
lead on the verses, the whole pub shouting the choruses, a quiet half-time bridge, then the loudest
chorus. The lyrics came finished, from the user.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Styles: `style.txt` (Irish pub band, 112 BPM), `styles/punk.txt` (Celtic punk, 124 BPM).
- Render: `uv run python -m pixelart.render projects/deprecated`

## Notes

- Each header's note is the user's own direction ("half-time, quiet, solo voice"). `generate --notes`
  hands them to ACE-Step as tag modifiers (`[Bridge - half-time, quiet, solo voice]`) and keeps the
  instrumental intro; YuE2 gets plain tags.
- First round (ACE-Step XL with notes, seeds 1-4 per style, plus two plain-tag takes as a control):
  the notes made the bridge 2-3 dB quieter than the verses, and narrower, on most seeds. Without
  them it was level or louder. No take went half-time on the bridge or made the last chorus louder
  than the others. The fiddle intro ran 12-19 s with notes and 8-9 s without.
