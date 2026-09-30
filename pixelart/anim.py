"""Small animation helpers: deterministic randomness, clamping, ramps and easing curves.

Frames render in parallel worker processes in any order, so anything random
must be a pure function of its key (`rnd`), never of call order.
"""
import math
import zlib


def rnd(*key):
    """Deterministic pseudo-random number in [0, 1), identical in every worker process."""
    return zlib.crc32(repr(key).encode()) / 2 ** 32


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def lerp(a, b, p):
    return a + (b - a) * p


def ramp(t, a, b):
    """0 before a, 1 after b, linear in between."""
    return clamp((t - a) / (b - a), 0.0, 1.0)


def ease_out(p):
    p = clamp(p, 0.0, 1.0)
    return 1 - (1 - p) ** 3


def ease_in(p):
    p = clamp(p, 0.0, 1.0)
    return p ** 3


def ease_in_out(p):
    p = clamp(p, 0.0, 1.0)
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def back_out(p, s=1.8):
    """Overshoots a little past 1, then settles: for things that pop into place."""
    p = clamp(p, 0.0, 1.0) - 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def pop_dy(age, dur=0.15, drop=8):
    """Pop-in offset in pixels: drops `drop` pixels from above with a small bounce; None before it starts."""
    if age < 0:
        return None
    return int(round((1 - back_out(age / dur)) * -drop))


def wobble(age, amp=2.0, freq=30.0, decay=0.4):
    """A decaying jiggle in pixels, for things that have just been hit."""
    if age < 0:
        return 0
    return int(round(math.sin(age * freq) * amp * max(0.0, 1 - age / decay)))


def arc_pt(p, a, b, lift):
    """Point along a parabolic hop from a to b that rises `lift` pixels at the middle."""
    return lerp(a[0], b[0], p), lerp(a[1], b[1], p) - lift * 4 * p * (1 - p)
