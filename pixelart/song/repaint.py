"""Regenerate some sections of a take with a different style, keeping the rest.

    python -m pixelart.song.repaint PROJECT TAKE (--speaker NAME | --section NAME ... | --window A:B ...)
                                    --style "..." [--name TAG] [--seeds 1 2] [--pad 0.4] [--no-check]

Song models give one voice to a whole song, so a duet or a battle between two
characters tends to come out in one voice and one accent. Generate the song
in the first character's voice, then repaint the other character's sections
with a style that describes theirs. ACE-Step repaints each window with the
rest of the take as context, so the beat, key and mix carry across.

The section windows come from the take's Whisper transcript (written by
pixelart.song.check), matched against lyrics.txt. Each repainted take lands
next to the others as build/takes/<TAKE>+<TAG>-s<seed>.flac, with a listen
copy and a line in the lyric check report.

--window repaints explicit spans in seconds instead, e.g. to redo a few lines
that a take mumbled or dropped. A take can be repainted again, so fixes stack
up as <TAKE>+<TAG>-s<seed>+<TAG2>-s<seed2>.

The model gets the sheet as it is now, with say.txt's spellings, so a window
can also re-sing a line that was reworded or respelt since the take was made.
Cut a window in the gaps between lines: the vocal stem shows where they are.

ACE-Step hands the take back a decibel down, with each window a little quieter
than what it replaced. So the take goes back around the windows at its own
level, sample for sample, and each window is brought to the loudness of the
audio it replaced (`fit_levels`).
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

from pixelart import lyrics
from pixelart.ffmpeg import decode_stereo, encode
from pixelart.song.check import words_of
from pixelart.song.generate import listen_copy
from pixelart.song.models import MODELS, ModelMissing

MIN_WINDOW, MAX_WINDOW = 3.0, 90.0  # ACE-Step's repaint limits, in seconds
SR = 48000                          # ACE-Step's sample rate
SPLICE = 0.025                      # seconds ACE-Step crossfades the source back in at a window's edges


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if len(x) else 0.0


def fit_levels(src, new, windows, out):
    """Write `new` (ACE-Step's repaint of `src`) to `out` with the source back at its own level
    around the windows, and each window at the loudness of what it replaced. Returns each
    window's gain in dB, or None when the audio outside the windows isn't the source any more."""
    a, b = decode_stereo(src, SR), decode_stereo(new, SR)
    n = min(len(a), len(b))
    edge = int(SPLICE * SR)
    spans = [(max(0, int(s * SR)), min(n, int(e * SR))) for s, e in windows]
    kept = np.ones(n, bool)
    for i, j in spans:
        kept[max(0, i - 8 * edge):j + 8 * edge] = False
    gain = float((b[:n][kept] * a[:n][kept]).sum() / max(1e-12, (a[:n][kept] ** 2).sum()))   # ACE-Step's own
    if gain <= 0 or rms(b[:n][kept] - gain * a[:n][kept]) > 0.05 * rms(gain * a[:n][kept]):
        shutil.copyfile(new, out)
        return None
    fitted, gains = a.copy(), []
    for i, j in spans:
        window = b[i:j] / gain
        k = min(max(rms(a[i:j]) / max(rms(window), 1e-9), 0.5), 2.0, 0.999 / max(float(np.abs(window).max()), 1e-9))
        lo, hi = max(0, i - edge), min(n, j + edge)
        ramp = np.full(hi - lo, k)
        ramp[:i - lo] = np.linspace(1, k, i - lo)
        ramp[j - lo:] = np.linspace(k, 1, hi - j)
        fitted[lo:hi] = b[lo:hi] / gain * ramp[:, None]
        gains.append(round(20 * float(np.log10(k)), 2))
    encode(fitted, SR, out)
    return gains


def section_spans(sheet, transcript, min_block=3):
    """{section index: (first word start, last word end)} for the sections heard in the transcript.

    Only runs of at least `min_block` matching words count, so a stray "you"
    or "the" matched in the wrong verse can't stretch a span.
    """
    ref = [(w, i) for i, sec in enumerate(lyrics.sections(sheet))
           for line in sec["lines"] for w in words_of(line)]
    hyp = [(w, word["t0"], word["t1"]) for word in transcript for w in words_of(word["w"])]
    matcher = SequenceMatcher(None, [w for w, _ in ref], [w for w, *_ in hyp], autojunk=False)
    spans = {}
    for block in matcher.get_matching_blocks():
        if block.size < min_block:
            continue
        for k in range(block.size):
            sec = ref[block.a + k][1]
            t0, t1 = hyp[block.b + k][1:]
            a, b = spans.get(sec, (t0, t1))
            spans[sec] = (min(a, t0), max(b, t1))
    return spans


def windows_for(sheet, transcript, chosen, pad):
    """Repaint windows [(start, end)] for the chosen section indexes, padded but not into their neighbours."""
    spans = section_spans(sheet, transcript)
    heard = sorted(spans)
    out = []
    for i in chosen:
        if i not in spans:
            raise SystemExit(f"section {i + 1} isn't heard clearly enough in this take to find its window")
        start, end = spans[i]
        before = [spans[j][1] for j in heard if j < i]
        after = [spans[j][0] for j in heard if j > i]
        start = max(start - pad, before[-1] if before else 0.0)
        end = min(end + pad, after[0] if after else end + pad)
        out.append((round(start, 2), round(end, 2)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("take", help="a take name from build/takes, e.g. acestep-xl-s1")
    pick = ap.add_mutually_exclusive_group(required=True)
    pick.add_argument("--speaker", help="repaint every section sung by this speaker (as named in lyrics.txt)")
    pick.add_argument("--section", nargs="+", help="repaint these sections, e.g. 'Verse 1' 'Verse 3'")
    pick.add_argument("--window", nargs="+", metavar="A:B", help="repaint these spans, in seconds")
    ap.add_argument("--style", required=True, help="style for the repainted sections: genre, voice, accent")
    ap.add_argument("--name", default="repaint", help="tag for the new takes (default: repaint)")
    ap.add_argument("--model", default="acestep-xl", choices=["acestep", "acestep-xl"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[1])
    ap.add_argument("--pad", type=float, default=0.4, help="seconds added around each section's words")
    ap.add_argument("--no-check", action="store_true", help="skip the Whisper lyric check afterwards")
    args = ap.parse_args()

    root = Path(args.project).resolve()
    takes = root / "build" / "takes"
    src = takes / f"{args.take}.flac"
    cache = src.with_suffix(".transcript.json")
    if not src.exists():
        raise SystemExit(f"no take {src}")
    sheet = (root / "lyrics.txt").read_text()
    secs = lyrics.sections(sheet)
    if args.window:
        windows = [tuple(float(v) for v in w.split(":")) for w in args.window]
        spans = [{"start": a, "end": b} for a, b in windows]
    else:
        if args.speaker:
            chosen = [i for i, s in enumerate(secs) if (s["speaker"] or "").lower() == args.speaker.lower()]
        else:
            names = [n.lower() for n in args.section]
            chosen = [i for i, s in enumerate(secs) if (s["section"] or "").lower() in names]
        if not chosen:
            raise SystemExit("no sections match; speakers: "
                             + ", ".join(sorted({s["speaker"] for s in secs if s["speaker"]})))
        if not cache.exists():
            raise SystemExit(f"no transcript for {args.take}; run: python -m pixelart.song.check {args.project}")
        windows = windows_for(sheet, json.loads(cache.read_text()), chosen, args.pad)
        spans = [{"section": secs[i]["section"], "speaker": secs[i]["speaker"], "start": a, "end": b}
                 for i, (a, b) in zip(chosen, windows)]
    for sp in spans:
        a, b = sp["start"], sp["end"]
        where = f"{sp['section']} ({sp['speaker']})" if "section" in sp else "window"
        print(f"{where}: {a:.1f}-{b:.1f}s", flush=True)
        if not MIN_WINDOW <= b - a <= MAX_WINDOW:
            raise SystemExit(f"window is {b - a:.0f}s; ACE-Step repaints {MIN_WINDOW:.0f}-{MAX_WINDOW:.0f}s at a time")

    base = json.loads(src.with_suffix(".json").read_text())
    (takes / "model_lyrics.txt").write_text(lyrics.for_model(root))
    work = takes / "work" / f"{args.take}+{args.name}"
    work.mkdir(parents=True, exist_ok=True)
    log_path = takes / "logs" / f"{args.take}+{args.name}.log"
    print(f"{args.model}: repainting seeds {args.seeds} (log: {log_path})", flush=True)
    start = time.time()
    with open(log_path, "a") as log:
        log.write(f"\n=== {datetime.now().isoformat(timespec='seconds')} seeds {args.seeds} windows {windows}\n")
        log.flush()
        try:
            for seed, audio, _ in MODELS[args.model](takes / "model_lyrics.txt", args.style, args.seeds, work, log,
                                                     src_audio=src, repaint=windows):
                take = f"{args.take}+{args.name}-s{seed}"
                gains = fit_levels(src, audio, windows, takes / f"{take}.flac")
                (takes / f"{take}.json").write_text(json.dumps({
                    "take": take, "model": args.model, "seed": seed, "style": args.style,
                    "base": args.take, "base_style": base.get("style"),
                    "repainted": base.get("repainted", []) + [dict(sp, gain_db=g) for sp, g in
                                                                 zip(spans, gains or [None] * len(spans))],
                    "lyrics_sha256": base.get("lyrics_sha256"), "source": str(audio),
                    "created": datetime.now(timezone.utc).isoformat(timespec="seconds")}, indent=2) + "\n")
                listen_copy(takes / f"{take}.flac", takes / "listen" / f"{take}.m4a")
                print(f"  {take} ({time.time() - start:.0f}s)", flush=True)
        except ModelMissing as e:
            raise SystemExit(str(e))
    missing = [s for s in args.seeds if not (takes / f"{args.take}+{args.name}-s{s}.flac").exists()]
    if missing:
        print(f"  FAILED seeds {missing}: see {log_path}", flush=True)
    if not args.no_check:
        subprocess.run([sys.executable, "-m", "pixelart.song.check", str(root)])


if __name__ == "__main__":
    main()
