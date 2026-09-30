"""An integer-zoom camera over a small native-resolution world.

The world (e.g. 320x180) is shown at `k` screen pixels per world pixel. `k`
is always an integer so every world pixel stays square; the UI layer is the
same size as the world and always shown at the base scale (out / world).
Pans are smooth (whole screen pixels), zooms step from one integer to the next.
"""
from PIL import Image

from pixelart.anim import ease_in_out, lerp


class Cam:
    def __init__(self, cx, cy, k, world=(320, 180), out=(1920, 1080)):
        self.world, self.out = world, out
        self.scale = out[0] // world[0]
        self.k = int(k)
        W, H = world
        vw, vh = out[0] / self.k, out[1] / self.k
        self.x0 = min(max(cx - vw / 2, 0), W - vw)
        self.y0 = min(max(cy - vh / 2, 0), H - vh)
        self.vw, self.vh = vw, vh
        self.cx, self.cy = self.x0 + vw / 2, self.y0 + vh / 2

    @property
    def f(self):
        """UI pixels per world pixel (1 in the base shot, 2 at double zoom...)."""
        return self.k / self.scale

    def ui(self, x, y):
        """Where world point (x, y) appears on the UI layer."""
        f = self.f
        return (x - self.x0) * f, (y - self.y0) * f

    def world_pt(self, ux, uy):
        """The world point under UI point (ux, uy)."""
        f = self.f
        return ux / f + self.x0, uy / f + self.y0

    def visible(self, box, margin=0):
        x0, y0, x1, y1 = box
        return (x1 >= self.x0 - margin and x0 <= self.x0 + self.vw + margin
                and y1 >= self.y0 - margin and y0 <= self.y0 + self.vh + margin)


def between(a, b, p, ease=ease_in_out, **kw):
    """A camera part way from shot a to shot b, each (cx, cy, k): the centre glides, the zoom steps."""
    q = ease(p)
    return Cam(lerp(a[0], b[0], q), lerp(a[1], b[1], q), round(lerp(a[2], b[2], q)), **kw)


def compose(world, ui, cam, shake=(0, 0)):
    """Final frame: the world through `cam`, nudged by `shake` screen pixels, with the UI on top."""
    ow, oh = cam.out
    k = cam.k
    sx, sy = int(round(cam.x0 * k)) + shake[0], int(round(cam.y0 * k)) + shake[1]
    wx, wy = sx // k, sy // k
    wx1, wy1 = (sx + ow) // k + 1, (sy + oh) // k + 1
    part = world.crop((wx, wy, wx1, wy1)).resize(((wx1 - wx) * k, (wy1 - wy) * k), Image.NEAREST)
    frame = part.crop((sx - wx * k, sy - wy * k, sx - wx * k + ow, sy - wy * k + oh))
    if ui is not None:
        big = ui.resize((ow, oh), Image.NEAREST)
        frame.paste(big, (0, 0), big)
    return frame
