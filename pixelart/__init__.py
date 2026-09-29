"""Shared tooling for procedurally drawn pixel-art music videos.

pixel      drawing primitives: palettes-as-strings sprites, pixel fonts, ordered dither, camera compose
timing     render-time clocks: beat grid and timed-lyric lookups
project    loads a project directory (projects/<name>/project.py)
render     python -m pixelart.render <project>      parallel render + mux to mp4
preview    python -m pixelart.preview <project> ...  still frames + contact sheet
sweep      python -m pixelart.sweep <project>       render every frame, report exceptions
sheet      python -m pixelart.sheet out.png a.png…  contact sheet of PNGs
audio/     offline song analysis (stems, beats, tempo, transcription, lyric alignment, loudness)
"""
