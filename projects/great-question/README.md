# Great Question

PewDiePie vs. Sam Altman on a video call, with ChatGPT as the moderator. The occasion is Ajax, the model
PewDiePie built at home, and the two account bans he says it earned him (October 2026). Most of the
song is the two careers.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Look: one fixed shot of a three-way video call. Felix's webcam is the left tile and Sam's the right;
  ChatGPT's window sits between them and shares a picture for every bar. The call app carries the rest:
  live captions for the lyrics, a border on whoever has the floor, system messages for the bans.
- Render: `uv run python -m pixelart.render projects/great-question` -> `great-question.mp4` (3:15)
- Upload: `thumbs/youtube_upload.txt` (no thumbnails yet)

## The song

- **Take:** `yue2-s2`, picked by ear, with one bar sung again. YuE2 sang "live" (on air) as the verb, so
  `say.txt` gives the models "life" there, and `pixelart.song.repaint ... --window 25.47:33.1` (ACE-Step
  XL, seed 4: `yue2-s2+live-s4`) re-sang "lost all of Disney ... Felix: language. King of the Lost
  Boys ...". The window is brought back to the loudness of what it replaced.
- **One voice.** The sheet has four parts (Felix, Sam, ChatGPT, Ajax) and the take sings them all in
  one voice. The captions, the speaker's border and the name tab say who has the floor.
- **Post effects.** A song model can't be interrupted and can't clap, so three things are laid over the
  take with `pixelart.audio.bleep` (the take as picked stays in `audio/song.take.wav`):

  ```sh
  uv run python -m pixelart.audio.bleep projects/great-question \
      3.27:3.80 7.96:8.02:none 8.02:10.23 52.15:52.195:none 52.195:52.515:clap 52.515:52.725:clap \
      189.295:189.995 --length 0.7
  ```

  - the intro's two bans: the catchphrase is cut at "PewDie-" and at "My name is-", with a buzzer on
    each cut. Altman's first words ("Pew. Die. Pie") then finish the sentence.
  - Verse 2's "(Clap, clap!)": the two sung words are swapped for two handclaps.
  - a third buzzer on the bar after the last word, for the video's last gag (below). It isn't in the
    lyric sheet. Drop the last span to take the sound out; the picture doesn't depend on it.
- **Timing:** `align.py` is the automatic alignment plus hand fixes (the intro as it is heard after the
  cuts, three bars Whisper misheard, the held last word). In `data/lyrics_timed.json` a word in
  asterisks (`*BZZT*`, `*CLAP*`) is a sound, not a sung word: the captions show it in another colour
  once it sounds.
- **Length:** 614 words in the sheet; the take runs 3:15. The hook is six bars, twice.
- **Charges:** Altman's is that PewDiePie is a children's entertainer who never grew up (Peter Pan, the
  Lost Boys, Neverland). PewDiePie's is that Altman is all thumbnail and no video.
- **The news story** takes about a fifth of the bars: the intro, the end of Verse 1, the top of
  Verse 2, the Ajax couplet in Verse 4 and the outro.
- **Altman was in alt-f4.** That song's references were treated as used up
  (`pixelart.song.fresh --spent alt-f4`).

## The video

- **The frame never moves.** The world is the whole 320x180 frame at 6x, so a world pixel and a UI pixel
  are the same thing. Everything that changes is inside a tile or the window.
- **An exhibit a bar.** ChatGPT shares a picture for each line (a match history, a prescription, a
  security camera), captioned like evidence. "(Next!)" swipes the picture away. In the hook the window
  is ChatGPT itself, telling both men that theirs was a great question.
- **The BAN button** on Sam's desk is how the intro's bans happen, and it stays there. Each ban costs
  Felix an account, so he sits out the call as "PewDiePie (3)".
- **Punchlines** (`KILL_SHOTS` in `timeline.py`) make the target flinch and send reactions up the edge
  of his tile. Nothing else shakes.
- **Things that stay:** the wooden horse rolls into Sam's office on "that horse is in your house" and
  is still behind him at the end. Verse 1's toy blocks come back in Verse 4.
- **The ending:** Ajax joins in a bronze helmet, says "Great question!" and then what it is. The helmet
  comes off, it renames itself "ChatGPT (2)", and Sam presses the button a third time. ChatGPT sends
  round the call notes: "3. Who won? Great question!"

The code: `video.py` builds the frame and poses the two men, `call.py` draws the app and the rooms,
`characters.py` the figures (on `pixelart.figure`) and the orb, `timeline.py` the song's clock.
`gagkit.py` and `pictures.py` are what the gags draw with, and there is one `gags_<section>.py` per
section, each with its pictures next to the gags that show them.

What the bars refer to:

| bar | reference |
|---|---|
| the two buzzers | the two bans, with his appeal between them |
| hot dogs | he sold hot dogs after leaving university in 2011 |
| a barrel, a label, a baby | the barrels in his Amnesia videos, T-Series and Cocomelon |
| five bucks of banter | the paid-sign video of 2017, after which Disney's Maker Studios dropped him |
| the bridge | his 2017 livestream |
| Neverland | he moved to Japan in 2022 |
| a Qwen in a wig | Ajax is a fine-tune of Alibaba's Qwen |
| Meme review | his show; Elon Musk hosted an episode, and is suing OpenAI |
| the polos | Altman wore two polo shirts with popped collars on stage at Apple's WWDC in 2008 |
| promised us porno | in October 2025 Altman said ChatGPT would allow erotica for verified adults; OpenAI shelved it in March 2026 |
| the Koenigsegg | Altman's Swedish hypercar |
| passed the bar | GPT-4 passed the bar exam in 2023 |
| the pixel artist | image models and illustrators; the video is pixel art |
| the Minecraft horse | the funeral in his 2019 Minecraft series |
| his wife's channel | retired in 2018, and still about three times the size of OpenAI's |
| the printers | in 2018 fans hacked about 50,000 printers to print "subscribe to PewDiePie" |
| Ajax and Odysseus | the model, and the self-hosted workspace it runs in |
| the apology guru | his 2017 apology video, and the genre |
