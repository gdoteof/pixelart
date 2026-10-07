"""Skia, the way the styles use it: a canvas, smooth paths from a few points, text, and the way out to PIL.

Skia is not a dependency of the repo: run the reel with `uv run --with skia-python`.
"""
import math
from functools import lru_cache

import numpy as np
import skia
from PIL import Image

FONTS = {
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "medium": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "cond": "/usr/share/fonts/truetype/roboto/unhinted/RobotoCondensed-Bold.ttf",
    "heavy": "/usr/share/fonts/truetype/lato/Lato-Black.ttf",
    "comic": "/usr/share/fonts/opentype/comic-neue/ComicNeue-Bold.otf",
    "script": "/usr/share/fonts/opentype/lobstertwo/LobsterTwo-BoldItalic.otf",
    "lobster": "/usr/share/fonts/opentype/lobster/lobster.otf",
    "slab": "/usr/share/fonts/opentype/roboto/slab/RobotoSlab-Bold.otf",
    "hand": "/usr/share/fonts/opentype/tlwg/Purisa-Bold.otf",
    "book": "/usr/share/fonts/opentype/urw-base35/URWBookman-Demi.otf",
    "chancery": "/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
}


# --- canvas -------------------------------------------------------------------------------------

def surface(w, h, clear=None):
    s = skia.Surface(w, h)
    if clear is not None:
        s.getCanvas().clear(rgb(clear))
    return s


def array(surf):
    """The surface as an (h, w, 4) uint8 RGBA array."""
    return surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)


def image(surf):
    """The surface as an RGB PIL image."""
    return Image.fromarray(array(surf)[..., :3])


def from_array(a):
    """An (h, w, 3 or 4) uint8 array as a skia.Image."""
    a = np.asarray(a)
    if a.shape[2] == 3:
        a = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
    return skia.Image.fromarray(np.ascontiguousarray(a), colorType=skia.kRGBA_8888_ColorType)


# --- paint --------------------------------------------------------------------------------------

def rgb(c, a=1.0):
    """A colour from (r, g, b), (r, g, b, a) or "#rrggbb", with alpha 0..1."""
    if isinstance(c, str):
        c = tuple(int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    if len(c) == 4:
        a *= c[3] / 255
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(round(255 * max(0.0, min(1.0, a)))))


def fill(c, a=1.0, **kw):
    return skia.Paint(AntiAlias=True, Color=rgb(c, a), **kw)


def stroke(c, w, a=1.0, cap="round", join="round", **kw):
    caps = {"round": skia.Paint.kRound_Cap, "butt": skia.Paint.kButt_Cap, "square": skia.Paint.kSquare_Cap}
    joins = {"round": skia.Paint.kRound_Join, "miter": skia.Paint.kMiter_Join, "bevel": skia.Paint.kBevel_Join}
    return skia.Paint(AntiAlias=True, Color=rgb(c, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                      StrokeCap=caps[cap], StrokeJoin=joins[join], **kw)


# --- paths --------------------------------------------------------------------------------------

def poly(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def curve(pts, closed=True, tension=0.5):
    """A smooth path through the points (a Catmull-Rom spline). A point given as (x, y, "c") is a corner."""
    xy = [(float(p[0]), float(p[1])) for p in pts]
    corner = [len(p) > 2 for p in pts]
    n = len(xy)
    path = skia.Path()
    path.moveTo(*xy[0])

    def at(i):
        return xy[i % n] if closed else xy[max(0, min(n - 1, i))]

    def tangent(i):
        if corner[i % n] if closed else corner[max(0, min(n - 1, i))]:
            return 0.0, 0.0
        (ax, ay), (bx, by) = at(i - 1), at(i + 1)
        return (bx - ax) * tension / 3, (by - ay) * tension / 3

    for i in range(n if closed else n - 1):
        (x0, y0), (x1, y1) = at(i), at(i + 1)
        (ux, uy), (vx, vy) = tangent(i), tangent(i + 1)
        path.cubicTo(x0 + ux, y0 + uy, x1 - vx, y1 - vy, x1, y1)
    if closed:
        path.close()
    return path


def mirror(half):
    """A symmetric outline from its right half, given from the top of the centre line to the bottom."""
    left = [(-p[0], *p[1:]) for p in reversed(half) if abs(p[0]) > 1e-9]
    return list(half) + left


def oval(cx, cy, rx, ry=None, rot=0.0):
    ry = rx if ry is None else ry
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return xf(p, rot=rot, about=(cx, cy)) if rot else p


def rect(x0, y0, x1, y1, r=0.0):
    p = skia.Path()
    box = skia.Rect.MakeLTRB(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
    if r:
        p.addRRect(skia.RRect.MakeRectXY(box, r, r))
    else:
        p.addRect(box)
    return p


def union(*paths):
    out = paths[0]
    for p in paths[1:]:
        out = skia.Op(out, p, skia.kUnion_PathOp) or out
    return out


def intersect(a, b):
    return skia.Op(a, b, skia.kIntersect_PathOp) or skia.Path()


def minus(a, b):
    return skia.Op(a, b, skia.kDifference_PathOp) or a


def capsule(p0, p1, r0, r1=None):
    """A limb: the hull of a circle of radius r0 at p0 and one of r1 at p1."""
    r1 = r0 if r1 is None else r1
    (x0, y0), (x1, y1) = p0, p1
    d = math.hypot(x1 - x0, y1 - y0)
    a, b = oval(x0, y0, r0), oval(x1, y1, r1)
    if d < 1e-6 or d <= abs(r0 - r1):
        return a if r0 >= r1 else b
    th, ph = math.atan2(y1 - y0, x1 - x0), math.acos((r0 - r1) / d)
    quad = poly([(x0 + r0 * math.cos(th + ph), y0 + r0 * math.sin(th + ph)),
                 (x1 + r1 * math.cos(th + ph), y1 + r1 * math.sin(th + ph)),
                 (x1 + r1 * math.cos(th - ph), y1 + r1 * math.sin(th - ph)),
                 (x0 + r0 * math.cos(th - ph), y0 + r0 * math.sin(th - ph))])
    return union(a, b, quad)


def matrix(x=0.0, y=0.0, s=1.0, rot=0.0, sx=None, sy=None, about=(0.0, 0.0)):
    """Scale and turn about a point, then move by (x, y)."""
    m = skia.Matrix()
    m.setTranslate(x + about[0], y + about[1])
    m.preRotate(rot)
    m.preScale(s if sx is None else sx, s if sy is None else sy)
    m.preTranslate(-about[0], -about[1])
    return m


def xf(path, x=0.0, y=0.0, s=1.0, rot=0.0, sx=None, sy=None, about=(0.0, 0.0), m=None):
    """A copy of the path, scaled and turned (degrees) about a point, then moved."""
    out = skia.Path(path)
    out.transform(m if m is not None else matrix(x, y, s, rot, sx, sy, about))
    return out


def along(path, frac):
    """((x, y), angle in degrees) at a fraction of the way along a path."""
    pm = skia.PathMeasure(path, False)
    pos, tan = pm.getPosTan(pm.getLength() * max(0.0, min(1.0, frac)))
    return (pos.x(), pos.y()), math.degrees(math.atan2(tan.y(), tan.x()))


def part(path, a, b):
    """The stretch of a path from fraction a to fraction b: a line that draws itself."""
    pm = skia.PathMeasure(path, False)
    out = skia.Path()
    n = pm.getLength()
    pm.getSegment(n * max(0.0, a), n * min(1.0, b), out, True)
    return out


# --- text ---------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _typeface(name):
    return skia.Typeface.MakeFromFile(FONTS.get(name, name))


@lru_cache(maxsize=256)
def font(name, size):
    f = skia.Font(_typeface(name), size)
    f.setSubpixel(True)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def text_width(s, fnt):
    return fnt.measureText(s)


def text(canvas, s, x, y, fnt, paint, align="l"):
    """Draw a string with its baseline at y: align "l" starts at x, "m" centres on it, "r" ends at it."""
    w = fnt.measureText(s)
    canvas.drawString(s, x - (w / 2 if align == "m" else w if align == "r" else 0), y, fnt, paint)
    return w


def text_path(s, fnt, x=0.0, y=0.0, align="l"):
    """The outlines of a string as one path, for lettering that is stroked, warped or cut out."""
    glyphs = fnt.textToGlyphs(s)
    widths = fnt.getWidths(glyphs)
    x -= sum(widths) / 2 if align == "m" else sum(widths) if align == "r" else 0
    out = skia.Path()
    for g, w in zip(glyphs, widths):
        gp = fnt.getPath(g)
        if gp is not None:
            out.addPath(gp, x, y)
        x += w
    return out


# --- textures -----------------------------------------------------------------------------------

def grain(w, h, seed=0, scale=1, lo=0.0, hi=1.0):
    """White noise in [lo, hi], (h, w) float32, in blocks of `scale` pixels."""
    rng = np.random.default_rng(seed)
    g = rng.random(((h + scale - 1) // scale, (w + scale - 1) // scale), np.float32)
    if scale > 1:
        g = np.repeat(np.repeat(g, scale, 0), scale, 1)[:h, :w]
    return lo + (hi - lo) * g


def cloud(w, h, seed=0, cell=64, octaves=4):
    """Smooth value noise in [0, 1], (h, w) float32: paper fibre, stains, uneven ink."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for _ in range(octaves):
        gh, gw = h // cell + 2, w // cell + 2
        small = Image.fromarray((rng.random((gh, gw)) * 255).astype(np.uint8))
        big = small.resize((gw * cell, gh * cell), Image.BICUBIC).crop((0, 0, w, h))
        out += amp * np.asarray(big, np.float32) / 255
        total += amp
        amp *= 0.5
        cell = max(2, cell // 2)
    return out / total
