"""Contact sheets: python -m pixelart.sheet OUT.png a.png b.png ...

A 2-column grid of half-size (960x540) tiles, each with a caption strip.
"""
import sys

from PIL import Image, ImageDraw


def contact_sheet(tiles, out, cols=2, tile=(960, 540)):
    """`tiles` is [(path or PIL image, caption), ...]."""
    tw, th = tile
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + 20)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (src, caption) in enumerate(tiles):
        im = src if isinstance(src, Image.Image) else Image.open(src)
        x, y = (i % cols) * tw, (i // cols) * (th + 20)
        sheet.paste(im.convert("RGB").resize((tw, th), Image.BILINEAR), (x, y + 20))
        d.text((x + 6, y + 4), caption, fill=(255, 255, 0))
    sheet.save(out)
    return out


if __name__ == "__main__":
    out, files = sys.argv[1], sys.argv[2:]
    contact_sheet([(f, f.split("/")[-1]) for f in files], out)
