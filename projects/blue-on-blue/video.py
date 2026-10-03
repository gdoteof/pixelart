"""Frame renderer: a baseline lyric video that works for any analysed song.
Replace freely, keeping render_frame(t) -> 1920x1080 RGB image.

It reads what `python -m pixelart.audio.analyze` writes to data/, and each file
is optional, so a fresh project renders before it has a song:
    song.json          title
    beat_this.json     the star hops on every beat and the sky flashes on downbeats
    vocal_env.npy      the star glows with the vocal loudness
    lyrics_timed.json  karaoke lyrics, a speaker tag, and a card at each new section

The world is drawn at 320x180 and shown through pixel.compose, which upscales
it 6x with nearest-neighbour; the UI layer (text, HUD) is drawn at the same
native size on a transparent image and laid over the top.
"""
import json
from bisect import bisect_right
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from pixelart import pixel, timing
from pixelart.timing import BeatClock

ROOT = Path(__file__).parent
DATA = ROOT / "data"
FPS = 24
W, H = 320, 180
INK = (22, 14, 30)
GOLD = (255, 214, 64)
ORANGE = (255, 138, 40)
WHITE = (255, 255, 255)
DIM = (170, 160, 190)


def _data(name):
    path = DATA / name
    if not path.exists():
        return None
    return np.load(path) if path.suffix == ".npy" else json.loads(path.read_text())


SONG = _data("song.json") or {}
TITLE = (SONG.get("title") or ROOT.name.replace("-", " ").replace("_", " ").strip()).upper()
_beats = _data("beat_this.json")
CLOCK = (BeatClock(_beats["beats"], _beats["downbeats"]) if _beats
         else BeatClock(np.arange(0.0, 600.0, 0.5), np.arange(0.0, 600.0, 2.0)))   # 120 BPM until analysed
ENV = _data("vocal_env.npy")
LINES = _data("lyrics_timed.json") or []
FIRST_LYRIC = LINES[0]["t0"] if LINES else 1e9
LAST_LYRIC = LINES[-1]["t1"] if LINES else 1e9

# A card when the section changes: (time, section, speaker).
CARDS = []
for _ln in LINES:
    if _ln.get("section") and (not CARDS or CARDS[-1][1] != _ln["section"]):
        CARDS.append((_ln["t0"], _ln["section"], _ln.get("speaker")))
CARD_TIMES = [c[0] for c in CARDS]

PAL = {"k": INK, "y": GOLD, "o": ORANGE, "w": WHITE}
STAR = pixel.sprite([
    "......k......",
    ".....kyk.....",
    ".....kyk.....",
    "kkkkkywykkkkk",
    ".kyyyywyyyyk.",
    "..kyyyyyyok..",
    "...kyyyyok...",
    "..kyyokyyok..",
    ".kyok...kook.",
    ".kkk.....kkk.",
], PAL)
BIG = pixel.font(size=16)
TEXT = pixel.font(size=8)
SMALL = pixel.font("Silkscreen-Regular.ttf", 8)
SKY = np.linspace(0.0, 0.9, H, dtype=np.float32)[:, None].repeat(W, axis=1)
YY, XX = np.mgrid[0:H, 0:W]


def wrap(words, fnt, width):
    """Greedy rows of word indices that fit `width` pixels."""
    rows, row, x = [], [], 0
    space = pixel.text_width(" ", fnt)
    for i, w in enumerate(words):
        ww = pixel.text_width(w, fnt)
        if row and x + space + ww > width:
            rows.append(row)
            row, x = [], 0
        x += (space if row else 0) + ww
        row.append(i)
    return rows + [row] if row else rows


def draw_lyrics(ui, t):
    line = timing.line_at(LINES, t)
    if not line:
        return
    words = [w["w"] for w in line["words"]]
    now = timing.word_index(line, t)
    rows = wrap(words, TEXT, W - 16)[-3:]
    y = H - 12 - 12 * len(rows)
    space = pixel.text_width(" ", TEXT)
    for row in rows:
        x = (W - sum(pixel.text_width(words[i], TEXT) for i in row) - space * (len(row) - 1)) // 2
        for i in row:
            fill, dy = (GOLD, 0) if i < now else (ORANGE, -1) if i == now else (DIM, 0)
            pixel.outline_text(ui, (x, y + dy), words[i], TEXT, fill, INK)
            x += pixel.text_width(words[i], TEXT) + space
        y += 12
    if line.get("speaker"):
        pixel.outline_text(ui, (8, H - 16 - 12 * len(rows) - 10), line["speaker"].upper(), SMALL, WHITE, INK)


def draw_card(ui, t):
    """Title before the first lyric and after the last, and the section name for a moment when it changes."""
    if t < FIRST_LYRIC - 0.3 or t > LAST_LYRIC + 1.5:
        rows = wrap(TITLE.split(), BIG, W - 24)
        y = 34 - 10 * len(rows)
        for row in rows:
            pixel.outline_text(ui, (W // 2, y), " ".join(TITLE.split()[i] for i in row), BIG, GOLD, INK,
                               anchor="ma")
            y += 20
        return
    k = bisect_right(CARD_TIMES, t) - 1
    if k >= 0 and t - CARDS[k][0] < 1.8:
        pixel.outline_text(ui, (W // 2, 14), CARDS[k][1].upper(), BIG, GOLD, INK, anchor="ma")


def render_frame(t):
    world = Image.new("RGB", (W, H), (34, 22, 64))
    pixel.dither(world, SKY, (120, 40, 110), blend=0.6)
    d = CLOCK.downbeats
    since_down = t - d[bisect_right(d, t) - 1] if len(d) and t >= d[0] else 9.0
    if since_down < 0.3:
        pixel.dither(world, 0.35 * (1 - since_down / 0.3), (255, 214, 120), blend=0.35)
    ImageDraw.Draw(world).rectangle((0, 120, W, H), fill=(40, 28, 52))

    _, phase, _ = CLOCK.beat_info(t)
    x, y = W // 2 - STAR.width // 2, 108 - STAR.height - int(40 * 4 * phase * (1 - phase))
    if ENV is not None:
        loud = timing.frame_value(ENV, t, FPS)
        r = 6 + 14 * loud
        cx, cy = x + STAR.width / 2, y + STAR.height / 2
        glow = np.clip(1 - np.hypot(XX - cx, YY - cy) / r, 0, 1) * loud
        pixel.dither(world, glow, GOLD, blend=0.5)
    world.paste(STAR, (x, y), STAR)

    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_card(ui, t)
    draw_lyrics(ui, t)
    return pixel.compose(world, ui)


def label(t):
    line = timing.line_at(LINES, t)
    return line["text"] if line else ""
