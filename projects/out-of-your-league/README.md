# Out of Your League

Emiru and Maya Higa on the same side: a duo track, not a battle. Two friends trade bars over a 90s
boom-bap beat, dead straight, and every gangster brag is swapped for something true about them: the cash cow is
a cow, the shooters work for National Geographic, the gun on the hip is hot glue. The disses go
outward, at the people and companies they have really had words with.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Look: two streams, then one place. A verse is the stream of whoever raps it, her webcam full screen under
  her overlay, with the other one on a call in the corner. The last verse puts the two at the sanctuary's
  gate, and the song ends over the counter of the gift shop.
- Render: `uv run python -m pixelart.render projects/out-of-your-league` -> `out-of-your-league.mp4` (2:53)
- Upload: `thumbs/youtube_upload.txt` (no thumbnails yet)

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

## The video

- **Whoever raps has the screen.** The world is the whole 320x180 frame at 6x and the camera never
  moves. Verse 1 and verse 3 are Emiru's stream: the wig wall, the sewing table with the Singer, the
  dress form in a foam breastplate. Verse 2 is Maya's, from the barn, with Winnie at the feeder in the
  doorway and the hawk on a perch. Emiru sits left with her overlay on the right; Maya's stream is the
  mirror image.
- **The other one is on a call.** She is live in a tile in the corner, cut from her own webcam frame:
  she nods along, and laughs when a punchline lands. For Maya's one bar in verse 3, Emiru puts her up in
  the window.
- **Every bar has a picture, and it goes in the window.** The joke of the song is a gangster brag that
  turns out to be true and harmless, so the picture is what the brag really is: the heat on her hip as
  an item's tooltip (hot glue, hair trigger), the bodies as a ranked scoreboard, the cash cow at her
  feeder, the killers on call as two scorpions in bows. Some of them come out of the window: the glue
  gun and the scissors in Emiru's hand, the hawk on Maya's glove, the chinchilla on her shoulder.
- **Verse 3 is receipts.** Every picture there is a document, a sign or a game's screen: what Twitch
  said and what Twitch did. Nothing that happened to her is drawn.
- **Verse 4 is the gate.** Both of them lean on the fence with the window hanging between them and the
  rule boards either side; Winnie and the emu are in the field behind, and the tortoise crosses it when
  her bar comes. There is no room for a chat, so the newest message runs on one line under the window.
- **The chats** are functions of time, one per stream and one for the pair: the regulars idle, and a
  punchline sets them off.
- **Drawn to flatter.** The two heads are near-frontal, with big lined eyes, small noses and glossy
  hair, on a face code of their own (`characters.py`); the figures under them are `pixelart.figure`'s.
- **The end:** the two wave from behind the counter with the title in the window, and the beat fades.

The code: `video.py` builds the frame and poses the two women, `stream.py` binds the overlay
(`pixelart.streamui`) and adds the call tile and the one-line chat, `rooms.py` the four places,
`characters.py` the figures, `animals.py` who lives at the sanctuary, `chatlog.py` what the chats type,
`timeline.py` the song's clock. `gagkit.py` is what the gags are written with (`pixelart.gagkit`),
`pictures.py` the canvas for the window and the things drawn in more than one verse, and there is one
`gags_<section>.py` per section.
