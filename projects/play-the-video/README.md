# Play the Video

Asmongold vs. Hasan Piker, each on his own stream, each watching the other one's video and pausing it to
answer. There is no news story behind it: the song is the two careers and the two rooms. Chat sings the
hook, from work.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Look: each man where he streams from, full screen while he raps, with his stream's overlay on top: the
  other man's video paused in a corner window, the chat, alerts. The hooks put the two streams side by
  side, then show where chat is watching from.
- Render: `uv run python -m pixelart.render projects/play-the-video` -> `play-the-video.mp4` (3:14)
- Upload: `thumbs/youtube_upload.txt` (no thumbnails yet)

## The song

- **Take:** `acestep-xl-s3`, picked by ear out of eight (five YuE2, three ACE-Step XL). It is used as
  picked: nothing is sung again and nothing is laid over it. The lyric check ranked it last of the eight
  (81% of the words heard in order); that report measures diction, and the pick is made by ear.
- **Charges:** Hasan's is that Asmongold is the roach king of a house he owns and won't clean.
  Asmongold's is that Hasan's socialism is a skin he bought in the shop. Chat's is that they are one man
  with two webcams.
- **One voice.** The sheet has four parts (Hasan, Asmongold, Chat, Both). The song models sing them all
  in one voice, so the frame says who has the floor: whose stream it is, the name tab, the captions.
- **Timing:** `align.py` is the automatic alignment plus hand fixes, checked word by word against both
  transcripts and the vocal stem. Where the take and the sheet part ways:
  - It starts singing on the first frame, so the "stream starting soon" card gets two thirds of a second.
  - The verses run back to back with no bars between them. `timeline.py` cuts to the next stream an
    eighth of a second before its first word, once the last word before it is over, and a section's
    first gag never starts ahead of that cut.
  - "A lie!" is sung twice (the caption goes with the first), and "Board of Health. / Health tip:" is
    sung with one "Health", which the two bars share: the notice stays in the window until "fly".
  - After the last word, "Pause.", the take plays on for seventeen seconds of ad-libs. `AUDIO_END` in
    `project.py` stops the sound dead at 3:10.9, just before the next beat, and the picture stops with
    it. Take `AUDIO_END` out and set `FADE` for an ordinary fade under the title instead.
- **The crowd voice** of the hooks is the muddiest part of the take. Whisper hears "menopause" as
  "mental power" in the whole song; on the bar alone, primed with the line, it reads "menopause" both
  times. The chat between the two streams spells it out (MEN-O-PAUSE).
- **Length:** 68 bars, 601 words. The take is 88.5 BPM and runs 3:28 with its ad-libs; the video is 3:14.

## The video

- **Whoever raps has the screen.** The world is the whole 320x180 frame at 6x and the camera never
  moves: a verse is one man's stream, and the cut to the next verse is the cut to the other stream.
  Hasan sits left of centre with his overlay on the right; Asmongold's stream is the mirror image.
- **The other man is a paused video.** The window in the corner is his own webcam frame, shrunk, stopped
  at 0:01 with his logo in the corner. He can't answer, but a punchline shakes the window and sends
  emotes up over it.
- **Every bar has a picture, and it goes in the window.** The host pulls something up over the paused
  video for as long as the bar lasts, then the video is back. Hasan's are files, camera feeds and, for
  the four bars about his own good life, propaganda posters. Asmongold's look like a game's interface:
  party frames, an item shop, tooltips. His last verse opens with tooltips on the things in his own
  room.
- **The chat** is a function of time: the regulars idle, a punchline sets them off, and gags script
  lines. When the song changes stream, the one we left raids the one we join.
- **The hooks** are chat's. The two streams sit side by side with one chat down the middle typing the
  hook as it is sung; then the frame is a desk at somebody's work, with a spreadsheet on the main monitor
  and the stream, muted, on the second.
- **The ending:** the video is over, chat applauds, and both men have thoughts on that. Pause: the
  sound stops on the word, both men freeze under a pause icon each, and chat, the one thing still
  moving, types UNPAUSE into three seconds of silence while the title comes up.

The code: `video.py` builds the frame and poses the two men, `stream.py` draws the overlay (the window,
the chat, alerts, captions), `rooms.py` the two rooms, `characters.py` the figures (on `pixelart.figure`
at one and a half times its size), `office.py` the desk in the hooks, `chatlog.py` what the chats type,
`timeline.py` the song's clock, `align.py` the lyric timing. `gagkit.py` is what the gags are written
with, `pictures.py` the canvas for the window and the things drawn in more than one verse, and there is
one `gags_<section>.py` per section.
