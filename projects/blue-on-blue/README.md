# Blue on Blue

Zohran Mamdani vs. Gavin Newsom, staged where Newsom has his talks: on his own podcast, *This Is Gavin
Newsom*. In March 2026 Newsom warned Mamdani in public, "I know how this love story ends, Zohran," so the
battle is a love triangle. Newsom is Trump's bitter ex, Mamdani is the new crush, and Trump calls in on
speakerphone for the last word.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Timing: `uv run python projects/blue-on-blue/align.py` (the automatic alignment plus the hand fixes below).
- Render: `uv run python -m pixelart.render projects/blue-on-blue` -> `blue-on-blue.mp4`
- Thumbnails: `uv run python projects/blue-on-blue/thumbnail.py` -> `thumbs/`, with the upload kit in
  `thumbs/youtube_upload.txt`.

## The song

- The lyrics follow lyric-craft.md. The lyric-critic scored the first draft at a median of 10/12, and its
  three fixes are in.
- The take is `yue2-s2` (YuE2, seed 2), picked by ear. One voice raps all four parts.
- Where the take departs from the sheet:
  - The hook is sung eight and a half times instead of twice (59.2-80.9 s), and it swaps "Newscum" and
    "Has-been" in its own order. `align.py` times all 17 chants as sung, and the video shows them that way.
  - The outro is three voices: Trump's "Zohran! Handsome!", Mamdani's "Hi! Gavin says hi." and Trump's
    "Who?" at 117.7 s. The aligner put "Who?" at 143 s, so `align.py` splits the outro into three lines.
  - The last line is sung "This *is* Gavin Newsom". The neon sign over the desk swaps IS for WAS on the
    beat, so the joke lands on screen.
  - V1's "(Thank you.)" is hard to hear, so Mamdani says it in a speech bubble.
  - The chant carries on after the outro, so the video ends at 124 s with a 3.5 s fade instead of running
    to the end of the take (144 s).

## The video

The podcast set: two hosts at one desk, mics on booms, a ring light, an ON AIR sign and a neon THIS IS /
GAVIN NEWSOM. The wide two-shot is home. The camera cuts to a close-up only twice: to the neon for THIS WAS,
and to Newsom's face after "Who?". Everything else plays inside the wide frame: props in the hosts' hands
and on the desk, and a broadcast inset over the neon (TikToks, Truth Social posts, texts from Donnie, the
road to Texas). The stream's furniture is part of the joke: a LIVE bug whose viewer count climbs to 3.4M
and then falls to 3, chapter cards, and a chat ticker.

- `studio.py` is the set, `characters.py` the three heads and the seated bodies, `props.py` the props and
  inset pictures, and `video.py` the frame: poses, mannerisms, the hits and the UI.
- `gags_*.py` hold one gag per lyric line, per section (`gagkit.py` has the helpers). The hook is a single
  span gag: the live chat takes over the middle of the screen. Newsom turns on slow mode, bans people,
  watches Trump post in his chat and turns the chat off, and then Trump has it turned back on.
- Once Mamdani says he loves the landlord-in-chief, the host's portrait is Trump's for the rest of the
  video, and its plaque reads LANDLORD.
