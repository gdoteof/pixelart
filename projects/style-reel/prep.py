"""Cut the reel's bar out of Play the Video: the audio under every clip, and the envelope for the mouths.

    uv run python projects/style-reel/prep.py

Needs Play the Video's stems (its `analyze` step). The verses of that take run back to back, so the voice
is let in for the couplet alone, over the backing: otherwise the clip opens on the back half of one word
and closes on the front half of another.
"""
import numpy as np

import script as S
from pixelart.audio.envelope import loudness_envelope
from pixelart.ffmpeg import decode_stereo, encode

SR = 48000
STEMS = S.ROOT.parent / "play-the-video" / "build" / "stems" / "htdemucs" / "song"
GATE = (S.SING0 - 0.07, S.SING0 - 0.01, S.SING1 - 0.01, S.SING1 + 0.07)     # closed, open, open, closed


def gate(times):
    a, b, c, d = GATE
    return np.clip(np.minimum((times - a) / (b - a), (d - times) / (d - c)), 0, 1)


def main():
    i, j = int(S.T0 * SR), int(S.T1 * SR)
    times = np.arange(i, j) / SR
    backing = decode_stereo(STEMS / "no_vocals.wav", SR)[i:j]
    voice = decode_stereo(STEMS / "vocals.wav", SR)[i:j]
    mix = backing + voice * gate(times)[:, None]
    fade = np.minimum(np.clip((times - S.T0) / 0.06, 0, 1), np.clip((S.T1 - times) / 0.6, 0, 1))
    out = S.ROOT / "build" / "audio.wav"
    out.parent.mkdir(exist_ok=True)
    encode(mix * fade[:, None], SR, out)

    env = loudness_envelope(STEMS / "vocals.wav", S.ENV_FPS, S.T1 + 1.0)
    k = int(round(S.ENV_T0 * S.ENV_FPS))
    env = env[k:k + int((S.T1 + 0.5 - S.ENV_T0) * S.ENV_FPS)]
    env = env * gate(S.ENV_T0 + np.arange(len(env)) / S.ENV_FPS)
    (S.ROOT / "data").mkdir(exist_ok=True)
    np.save(S.ROOT / "data" / "env.npy", env.astype(np.float32))
    print(f"{out} ({len(mix) / SR:.2f}s), data/env.npy ({len(env)} values at {S.ENV_FPS}/s, mean {env.mean():.2f})")


if __name__ == "__main__":
    main()
