# Out of Your League

Emiru and Maya Higa on the same side: a duo track, not a battle. Two friends trade bars over a 90s
boom-bap beat, dead straight, and every gangster brag is swapped for something true about them: the cash cow is
a cow, the shooters work for National Geographic, the gun on the hip is hot glue. The disses go
outward, at the people and companies they have really had words with.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Look: not designed yet.
- Render: `uv run python -m pixelart.render projects/out-of-your-league`

## The song

- **Claims, not charges.** Emiru's is that she owns the place and never has to leave the house: equity
  in the org, a champion drawn from her face, costumes she sews herself. Maya's is that her crew is a
  zoo and her money is clean: wolves, a hawk, a tax-exempt sanctuary, and streamers who get a phone
  call when they treat animals as content.
- **Four verses and no hook.** One each, then Emiru on Twitch (its cut of her subs, the guard who
  didn't move at TwitchCon, the ban her bodyguard got against the one her attacker got, the CEO's two
  statements), then a verse the two of them trade every bar or two. A chorus is where viewers leave,
  so the title line is said once, as the last couplet: one is League of Legends, one is in a league
  of her own, and yours is Bronze.
- **No intro.** The song opens on the first bar of verse 1, so the beat is in from the start. The
  sanctuary's welcome sign is the picture's job; the song keeps only the announcement on the way out:
  exit through the gift shop.
- **One voice.** The sheet has three parts (Emiru, Maya, Both). The song models sing them all in one
  voice, so the video has to say who has the floor. The style names a female voice first and leaves
  out "low" and "menace": with those in, the takes came out sounding like a man.
- **`say.txt`** gives the models spellings for the names they would guess at.
- **Take:** `yue2-boombap-s2` (YuE2, seed 2), picked by ear from 24 takes in four styles. `styles/` has
  the lines that were tried: the drill the sheet was first written for, club rap, bubblegum trap and
  the boom bap that won. `generate --style NAME` makes takes from one of them.
- **Tempo.** At 140 BPM YuE2 put a bar of words into every 1.7-second bar, too fast to follow, and
  ACE-Step rapped half-time and ran out of song. At 92 BPM a bar takes 2.6 seconds.
- **Trimmed.** The take opens with 18 seconds of wordless ad-libs, which are cut (`trim_start` in the
  take's JSON), so the first bar lands three seconds in. The words end at 2:49 and the take plays on
  for another 18 seconds: `project.py` stops the video at 2:53 on a fade.
- **Length:** 62 bars, 555 words.
