"""Lyrics -> song with local open-weight models, before any analysis or drawing.

    generate   python -m pixelart.song.generate PROJECT    lyrics.txt + style.txt -> build/takes/
    check      python -m pixelart.song.check PROJECT       lyric intelligibility of each take (Whisper)
    pick       python -m pixelart.song.pick PROJECT TAKE   the chosen take (or any file) -> audio/song.wav

The models (YuE2, ACE-Step 1.5) each live in their own checkout and venv,
outside this repo, and run as subprocesses; see pixelart.song.models.
"""
