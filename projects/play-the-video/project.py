"""Project settings read by the pixelart tools (see pixelart/project.py for the contract)."""
from pathlib import Path

ROOT = Path(__file__).parent
FPS = 24
SONG = ROOT / "audio" / "song.wav"
AUDIO = SONG if SONG.exists() else None
# The last word is "Pause." (190.3-190.7 s), and the song obeys: it stops dead before the next beat, with the
# take's ad-libs ("oh, oh, pause") still to come, and the picture holds while chat complains into the quiet.
AUDIO_END = 190.9
END = 194.0
OUTPUT = ROOT / "play-the-video.mp4"


# The renderer needs the song analysis in data/ (or falls back to draft timing), so it loads on first
# use: `analyze` can load this project before that analysis exists.
def render_frame(t):
    import video
    return video.render_frame(t)


def label(t):
    import video
    return video.label(t)
