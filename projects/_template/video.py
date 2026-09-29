"""Frame renderer: a placeholder scene showing the moving parts. Replace freely,
keeping render_frame(t) -> 1920x1080 RGB image.

The world is drawn at 320x180 and shown through pixel.compose, which upscales
it 6x with nearest-neighbour; the UI layer (text, HUD) is drawn at the same
native size on a transparent image and laid over the top.
"""
import numpy as np
from PIL import Image, ImageDraw

from pixelart import pixel
from pixelart.timing import BeatClock

W, H = 320, 180
INK = (22, 14, 30)
GOLD = (255, 214, 64)
WHITE = (255, 255, 255)

# A fixed 120 BPM grid until the song is analysed; then load data/beat_this.json:
#   b = json.loads((ROOT / "data" / "beat_this.json").read_text())
#   CLOCK = BeatClock(b["beats"], b["downbeats"])
CLOCK = BeatClock(np.arange(0.0, 600.0, 0.5), np.arange(0.0, 600.0, 2.0))

PAL = {"k": INK, "y": GOLD, "o": (255, 138, 40), "w": WHITE}
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
TITLE = pixel.font(size=16)
SMALL = pixel.font("Silkscreen-Regular.ttf", 8)
SKY = np.linspace(0.0, 0.9, H, dtype=np.float32)[:, None].repeat(W, axis=1)


def render_frame(t):
    world = Image.new("RGB", (W, H), (34, 22, 64))
    pixel.dither(world, SKY, (120, 40, 110), blend=0.6)
    ImageDraw.Draw(world).rectangle((0, 140, W, H), fill=(40, 28, 52))

    beat, phase, _ = CLOCK.beat_info(t)
    bar, in_bar = CLOCK.bar_info(t)
    y = 128 - STAR.height - int(40 * 4 * phase * (1 - phase))   # one hop per beat
    world.paste(STAR, (W // 2 - STAR.width // 2, y), STAR)

    ui = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pixel.outline_text(ui, (W // 2, 20), "NEW VIDEO", TITLE, GOLD, INK, anchor="ma")
    pixel.outline_text(ui, (W // 2, 158), f"{t:5.2f}s  bar {bar}  beat {in_bar + 1}", SMALL, WHITE,
                       INK, anchor="ma")
    return pixel.compose(world, ui)
