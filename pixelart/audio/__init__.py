"""Offline song analysis, run once per song; results go in the project's data/ dir.

    analyze     all of the below for a project, skipping what exists
    stems       vocals / accompaniment split (Demucs)            needs the `audio` extra
    beats       beat + downbeat tracking (beat_this)             needs the `audio` extra
    transcribe  word-level timestamps (faster-whisper, CUDA)     needs the `audio` extra
    align       snap transcribed word timings onto the real lyrics
    envelope    per-video-frame loudness (drives mouths, pulses)
    tempo       quick numpy-only BPM / beat-phase estimate

Heavy dependencies are imported inside functions, so importing this package is cheap.
"""
