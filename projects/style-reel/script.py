"""The bar every style draws: one couplet of Play the Video (verse 2, Asmongold on Hasan), and its gag.

    Your mansion's got five and a half baths: how austere;
    five and a half more than I've had all year.

All times are seconds of the song. A clip opens on a beat of backing before the couplet (T0) and holds for
a bar after it (T1). What happens when is in EV, so that every style stages the same joke on the same
words: the house, the tubs counted off inside the word "five", the half, the red flag on "austere", then
the scoreboard, and nought for Asmongold on "had" with the flies arriving for "year".

A style is a module style_<name>.py with frame(t): a pure function of song time that returns the
1920x1080 picture (a PIL image or an array), so that frames render in parallel and in any order.
"""
import bisect
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
W, H, FPS = 1920, 1080, 24
FRAMES = 184
T0 = 66.94
T1 = T0 + FRAMES / FPS                      # 74.607
SING0, SING1 = 67.70, 73.52                 # the couplet's first and last sound

LINES = [
    dict(who="asmon", text="Your mansion's got five and a half baths: how austere;", words=[
        ("Your", 67.70, 68.10), ("mansion's", 68.10, 68.60), ("got", 68.60, 68.72), ("five", 68.72, 69.08),
        ("and", 69.08, 69.26), ("a", 69.26, 69.36), ("half", 69.36, 69.66), ("baths:", 69.66, 69.94),
        ("how", 70.06, 70.22), ("austere;", 70.22, 70.74)]),
    dict(who="asmon", text="five and a half more than I've had all year.", words=[
        ("five", 70.74, 71.04), ("and", 71.04, 71.42), ("a", 71.42, 71.54), ("half", 71.54, 71.90),
        ("more", 71.90, 72.10), ("than", 72.10, 72.38), ("I've", 72.38, 72.68), ("had", 72.68, 72.84),
        ("all", 72.84, 73.08), ("year.", 73.08, 73.52)]),
]
for _line in LINES:
    _line["t0"], _line["t1"] = _line["words"][0][1], _line["words"][-1][2]
WORDS = [w for line in LINES for w in line["words"]]

BEATS = [66.26, 66.94, 67.60, 68.28, 68.96, 69.64, 70.32, 71.00, 71.68, 72.36, 73.02, 73.70, 74.38, 75.06]
DOWNBEATS = [68.28, 71.00, 73.70]
BEAT = 0.678                                # seconds, at 88.5 BPM

EV = dict(
    mansion=68.10,                          # "mansion's": the house comes up
    tubs=(68.72, 68.79, 68.86, 68.93, 69.00),   # one, two, three, four, five, inside the word "five"
    half=69.36,                             # "half": half a tub
    baths=69.66,                            # "baths": the count is stamped, 5 1/2 BATHS
    austere=70.22,                          # "austere": the red flag goes up over the house
    line2=70.74,                            # the scoreboard: BATHS THIS YEAR, HIM 5 1/2, ME ?
    more=71.90,
    ive=72.38,                              # "I've": his number starts to roll, the first fly turns up
    had=72.68,                              # "had": ME 0
    year=73.08,                             # "year": the flies and the smell; Hasan recoils
)


# --- time ---------------------------------------------------------------------------------------

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ramp(t, t0, dur):
    """0 before t0, 1 from t0 + dur, a straight line between."""
    return clamp((t - t0) / dur) if dur > 0 else float(t >= t0)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x, p=3):
    return 1 - (1 - clamp(x)) ** p


def ease_in(x, p=3):
    return clamp(x) ** p


def back(x, s=1.9):
    """Ease out past 1 and settle: how a thing pops in."""
    x = clamp(x) - 1
    return 1 + x * x * ((s + 1) * x + s)


def elastic(x, wobbles=2.5, damp=5.0):
    """Ease to 1 with a decaying wobble."""
    x = clamp(x)
    return 1 - math.exp(-damp * x) * math.cos(wobbles * 2 * math.pi * x) if x < 1 else 1.0


def bounce(x):
    """Fall to 1 and bounce, like a dropped thing."""
    x = clamp(x)
    for a, b, c in ((1 / 2.75, 0.0, 0.0), (2 / 2.75, 1.5 / 2.75, 0.75), (2.5 / 2.75, 2.25 / 2.75, 0.9375),
                    (1.0, 2.625 / 2.75, 0.984375)):
        if x < a or a == 1.0:
            x -= b
            return 7.5625 * x * x + c
    return 1.0


def pop(t, t0, dur=0.24, s=1.9):
    """A thing's scale as it pops in at t0: 0 before, overshooting to 1."""
    return 0.0 if t < t0 else back((t - t0) / dur, s)


def on(name, t):
    return t >= EV[name]


def since(name, t):
    return t - EV[name]


def hold(t, n=2):
    """`t` held to every nth frame of the clip: animation on twos, on threes."""
    f = math.floor((t - T0) * FPS / n + 1e-6) * n
    return T0 + f / FPS


def frame_no(t):
    return int(round((t - T0) * FPS))


def beat(t):
    """(index into BEATS of the last beat at or before t, how far to the next one, 0..1)."""
    i = clamp(bisect.bisect_right(BEATS, t) - 1, 0, len(BEATS) - 2)
    return i, clamp((t - BEATS[i]) / (BEATS[i + 1] - BEATS[i]))


def thump(t, decay=7.0):
    """1 on every beat, dying away after it."""
    i, _ = beat(t)
    return math.exp(-decay * max(0.0, t - BEATS[i]))


def rnd(*key):
    """A fixed random number in [0, 1) for a key: the same on every frame and in every worker."""
    h = 2166136261
    for part in key:
        for ch in repr(part):
            h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    h ^= h >> 15
    h = (h * 2246822519) & 0xFFFFFFFF
    h ^= h >> 13
    return (h & 0xFFFFFF) / 0x1000000


# --- the voice ----------------------------------------------------------------------------------

ENV_FPS = 120
ENV_T0 = T0 - 0.5
_env = None


def vocal(t):
    """How loud the voice is at t, 0..1 (data/env.npy, made by prep.py)."""
    global _env
    if _env is None:
        _env = np.load(ROOT / "data" / "env.npy")
    x = (t - ENV_T0) * ENV_FPS
    i = int(math.floor(x))
    if i < 0 or i + 1 >= len(_env):
        return 0.0
    return float(_env[i] + (_env[i + 1] - _env[i]) * (x - i))


# Mouth shapes: (width, opening, upper teeth showing, tongue, lower lip tucked under the teeth).
VISEMES = {
    "X": (0.80, 0.00, 0.0, 0.0, 0.0),       # at rest
    "M": (0.74, 0.00, 0.0, 0.0, 0.0),       # m b p: pressed shut
    "A": (0.95, 1.00, 0.6, 0.5, 0.0),       # ah: wide open
    "E": (1.05, 0.55, 0.8, 0.3, 0.0),       # eh
    "I": (1.18, 0.30, 1.0, 0.0, 0.0),       # ee: a wide slot of teeth
    "O": (0.60, 0.85, 0.2, 0.2, 0.0),       # oh: round
    "U": (0.46, 0.40, 0.0, 0.0, 0.0),       # oo, w, r: small and round
    "F": (0.86, 0.22, 1.0, 0.0, 1.0),       # f v: teeth on the lip
    "L": (0.90, 0.50, 0.6, 1.0, 0.0),       # l th n d t: the tongue up
    "S": (1.00, 0.18, 1.0, 0.0, 0.0),       # s z sh: teeth together
}
SHAPES = ["UO", "MAES", "EOL", "FAEF", "EL", "E", "AAF", "MALS", "AU", "OSLIE",
          "FAEF", "EL", "E", "AAF", "MOU", "LEL", "AEF", "AL", "OL", "IEU"]


def _mouth_keys():
    keys = [(SING0 - 0.10, "X")]
    for (_, a, b), shapes in zip(WORDS, SHAPES):
        if a - keys[-1][0] > 0.2:
            keys.append((a - 0.07, "X"))
        n = len(shapes)
        keys += [(a + (b - a) * (i + 0.35) / n, s) for i, s in enumerate(shapes)]
    keys.append((SING1 + 0.10, "X"))
    return keys


_KEYS = _mouth_keys()
_KEY_T = [k[0] for k in _KEYS]


def mouth(t):
    """The singer's mouth at t: dict(w, h, teeth, tongue, f). The shape follows the words, sound by sound,
    and the opening follows how loud the voice is."""
    i = bisect.bisect_right(_KEY_T, t) - 1
    if i < 0 or i + 1 >= len(_KEYS):
        v = VISEMES["X"]
    else:
        (ta, a), (tb, b) = _KEYS[i], _KEYS[i + 1]
        k = smooth((t - ta) / (tb - ta))
        v = tuple(p + (q - p) * k for p, q in zip(VISEMES[a], VISEMES[b]))
    w, h, teeth, tongue, f = v
    return dict(w=w, h=h * (0.45 + 0.55 * vocal(t)), teeth=teeth, tongue=tongue, f=f)


def singing(t):
    return SING0 <= t <= SING1


def caption(t):
    """(the line on screen at t or None, [(word, state)]): state is 0 not yet sung, 1 being sung, 2 sung."""
    if t < LINES[0]["t0"] - 0.3:
        return None, []
    line = LINES[0] if t < LINES[1]["t0"] - 0.06 else LINES[1]
    return line, [(w, 0 if t < a else 1 if t < b else 2) for w, a, b in line["words"]]
