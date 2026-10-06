# Great Question

PewDiePie vs. Sam Altman, with ChatGPT as the referee. The occasion is Ajax, the model PewDiePie built
at home, and the two account bans he says it earned him (October 2026). Most of the song is the two
careers.

- Song: `lyrics.txt` + `style.txt` -> `python -m pixelart.song.generate`, then `pick`. `audio/` is not committed.
- Look: not designed yet
- Render: `uv run python -m pixelart.render projects/great-question`

## Notes

- **Status:** the lyrics and style are drafted, scored twice by the lyric-critic and revised from the
  user's notes. No takes yet.
- **The intro's bans are a post effect.** The model sings the whole catchphrase twice. Once a take is
  picked, cut the vocal stem at "Pew" in the first line and after "My name is" in the second, and lay
  a buzzer over each gap. Altman's first words ("Pew. Die. Pie") then finish the sentence. The stage
  directions in `lyrics.txt` mark the two cuts.
- **Charges:** Altman's is that PewDiePie is a children's entertainer who never grew up (Peter Pan, the
  Lost Boys, Neverland). PewDiePie's is that Altman is all thumbnail and no video.
- **Voices:** four. The hook is ChatGPT, and the last line is Ajax answering in ChatGPT's voice, which
  is the joke. The song models sing one voice, so the others need `pixelart.song.repaint` once a take
  is picked.
- **Length:** 614 sung words, about 3:47 by `generate`'s estimate. The hook is six bars, twice.
- **The news story** takes about a fifth of the bars: the intro, the end of Verse 1, the top of
  Verse 2, the Ajax couplet in Verse 4 and the outro.
- **Altman was in alt-f4.** That song's references were treated as used up
  (`pixelart.song.fresh --spent alt-f4`).

What the bars refer to, for the video's gags:

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
