# The Last Commit

A capstan shanty about training the thing that takes your job, sung slow and steady: a shantyman on
the verses, all hands on the refrains and the choruses. This is the first song here that isn't a rap
battle; the lyrics came finished, from the user.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Styles: `style.txt` (stomps and concertina), `styles/acappella.txt` (voices, stomps and claps only),
  `styles/folkband.txt` (fiddle, accordion, bodhran, gang vocals).
- Render: `uv run python -m pixelart.render projects/last-commit`

## Notes

- The models only get plain `[Verse]` and `[Chorus]` tags, so the call and response (a solo line, then
  the crew's refrain line) and the a cappella final chorus are asked for in the style line alone.
  Verse 7's "slower" and the final chorus's "unaccompanied" are notes for the video; no take is
  expected to follow them.
- ACE-Step gets an explicit length (`--duration 190` at 72 BPM, `170` at 80 BPM): the word-count
  estimate assumes pop phrasing, and a shanty holds its lines longer.
