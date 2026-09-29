"""Shared tooling for procedurally drawn pixel-art music videos.

pixel      drawing primitives: palettes-as-strings sprites, pixel fonts, ordered dither, camera compose
timing     render-time clocks: beat grid and timed-lyric lookups
lyrics     lyric sheets: section/speaker headers, song-model tags, sung words
project    loads a project directory (projects/<name>/project.py)
new        python -m pixelart.new <name>            new project from projects/_template
render     python -m pixelart.render <project>      parallel render + mux to mp4
preview    python -m pixelart.preview <project> ...  still frames + contact sheet
sweep      python -m pixelart.sweep <project>       render every frame, report exceptions
sheet      python -m pixelart.sheet out.png a.png…  contact sheet of PNGs
song/      lyrics -> song with local models (generate takes, check their lyrics, pick one)
audio/     offline song analysis (stems, beats, tempo, transcription, lyric alignment, loudness)
gpu        CUDA library path for faster-whisper, VRAM size
"""
