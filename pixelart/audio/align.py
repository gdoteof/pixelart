"""Snap transcribed word timings onto the real lyrics.

Whisper mishears names and sometimes invents filler ("yo, yo, yo"), so we run
a fuzzy global alignment between the lyric tokens and the recognised tokens,
keep the timings of matched words and interpolate the rest from their neighbours.

For a song that follows its lyric sheet (anything generated from it), `auto`
aligns the whole sheet against the whole recording in one pass:

    python -m pixelart.audio.align PROJECT    # lyrics.txt + data/*.whisper.json -> data/lyrics_timed.json

When that isn't good enough (chants Whisper can't hear, sections sung out of
order, a Suno render that repeats the hook), write a per-song driver with a
time window per section and hand fixes; see projects/alt-f4/align.py.
Output lines have the shape pixelart.timing expects:
{"section", "speaker", "text", "t0", "t1", "words": [{"w", "t0", "t1"}, ...]}.
"""
import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

MAX_WORD, TYPICAL_WORD = 0.9, 0.35


def norm(word):
    w = word.lower().replace("’", "'")
    return re.sub(r"[^a-z0-9']", "", w).replace("'", "")


def split_words(line):
    """Display words of a lyric line (punctuation-only tokens dropped)."""
    return [w for w in re.split(r"\s+", line.strip()) if re.search(r"[A-Za-z0-9]", w)]


def tokens_of(word, norm=norm):
    """Alignment tokens of one display word: "worst-case" -> ["worst", "case"]."""
    return [t for t in (norm(p) for p in re.split(r"[-/]", word)) if t]


def parse_lyrics(text, speakers):
    """Lines of a lyric sheet with [Section] or [Section - who] / [Section: note] headers.

    `speakers` maps section name -> speaker; headers not in it are ignored and
    their lines stay with the previous section.
    """
    lines, section = [], None
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        m = re.match(r"\[(.+?)\]", raw)
        if m:
            name = m.group(1).split(" - ")[0].split(":")[0].strip()
            if name in speakers:
                section = name
            continue
        lines.append({"section": section, "speaker": speakers[section], "text": raw,
                      "words": split_words(raw)})
    return lines


def similarity(a, b):
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def align(lyr, rec, gap=-0.6):
    """Needleman-Wunsch over token lists; returns {lyric_index: rec_index}."""
    n, m = len(lyr), len(rec)
    score = [[0.0] * (m + 1) for _ in range(n + 1)]
    back = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        score[i][0] = i * gap
        back[i][0] = 1
    for j in range(1, m + 1):
        score[0][j] = j * gap * 0.5   # leading filler in the recording is cheap
        back[0][j] = 2
    for i in range(1, n + 1):
        li = lyr[i - 1]
        si, sp = score[i], score[i - 1]
        for j in range(1, m + 1):
            s = similarity(li, rec[j - 1])
            diag = sp[j - 1] + (2.0 * s - 1.0 if s >= 0.5 else -1.5)
            up = sp[j] + gap
            left = si[j - 1] + gap * 0.5  # extra recognised words (ad-libs) are cheap
            best = max(diag, up, left)
            si[j] = best
            back[i][j] = 0 if best == diag else (1 if best == up else 2)
    pairs, i, j = {}, n, m
    while i > 0 or j > 0:
        b = back[i][j]
        if i > 0 and j > 0 and b == 0:
            if similarity(lyr[i - 1], rec[j - 1]) >= 0.5:
                pairs[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif i > 0 and (j == 0 or b == 1):
            i -= 1
        else:
            j -= 1
    return pairs


def match_times(rec_words, flat_words, t_from, t_to, tokens_of=tokens_of):
    """Per lyric word: (t0, t1) from one transcript, or None where it didn't match."""
    rec = [w for w in rec_words if t_from <= w["t1"] and w["t0"] < t_to]
    rec_tokens, rec_owner = [], []
    for k, w in enumerate(rec):
        for t in tokens_of(w["w"]):
            rec_tokens.append(t)
            rec_owner.append(k)
    lyr_tokens, lyr_owner = [], []
    for fi, word in enumerate(flat_words):
        for t in tokens_of(word):
            lyr_tokens.append(t)
            lyr_owner.append(fi)
    times = [None] * len(flat_words)
    for ti, rj in align(lyr_tokens, rec_tokens).items():
        fi, w = lyr_owner[ti], rec[rec_owner[rj]]
        t0, t1 = w["t0"], w["t1"]
        if t1 - t0 > MAX_WORD:            # Whisper stretches words that follow a pause
            t0 = t1 - TYPICAL_WORD
        t0 = max(t0, t_from)
        times[fi] = [t0, t1] if times[fi] is None else [min(times[fi][0], t0), max(times[fi][1], t1)]
    return times


def interpolate(times, t_from, t_to):
    n, k = len(times), 0
    while k < n:
        if times[k] is not None:
            k += 1
            continue
        e = k
        while e < n and times[e] is None:
            e += 1
        lo = times[k - 1][1] if k > 0 else max(t_from, (times[e][0] if e < n else t_to) - TYPICAL_WORD * (e - k))
        hi = times[e][0] if e < n else min(t_to, lo + TYPICAL_WORD * (e - k))
        step = max(hi - lo, 0.05 * (e - k)) / (e - k)
        for q in range(k, e):
            times[q] = [lo + step * (q - k), lo + step * (q - k + 1)]
        k = e
    return times


def drop_strays(times, flat, slack=2.0, per_word=0.6):
    """Unmatch words whose time is far from the rest of their line.

    A line is sung in one go, so a word matched seconds away from its line's
    median (e.g. to a stray "your" Whisper heard inside a chant) is a false match.
    """
    by_line = {}
    for fi, (li, _) in enumerate(flat):
        by_line.setdefault(li, []).append(fi)
    dropped = 0
    for fis in by_line.values():
        hit = [fi for fi in fis if times[fi] is not None]
        if len(hit) < 3:
            continue
        mid = sorted(times[fi][0] for fi in hit)[len(hit) // 2]
        limit = slack + per_word * len(fis)
        for fi in hit:
            if abs(times[fi][0] - mid) > limit:
                times[fi] = None
                dropped += 1
    return dropped


def build(transcripts, lines, t_from, t_to, tokens_of=tokens_of, detail=False, strays=False):
    """Align lyric lines against several transcripts; per word keep the first sane match.

    With `strays`, matches far from the rest of their line are discarded (see
    drop_strays). Returns (timed lines, matched word count, total word count),
    plus with `detail` a per-line list of how many words were matched rather
    than interpolated.
    """
    flat = [(li, word) for li, line in enumerate(lines) for word in line["words"]]
    words = [w for _, w in flat]
    per = [match_times(rec, words, t_from, t_to, tokens_of) for rec in transcripts]
    times, matched = [], 0
    for fi in range(len(flat)):
        pick = next((p[fi] for p in per if p[fi] is not None), None)
        matched += pick is not None
        times.append(pick)
    if strays:
        matched -= drop_strays(times, flat)
    # Keep time monotonic: a match that lands before its predecessor is discarded.
    last = t_from
    for fi, t in enumerate(times):
        if t is not None:
            if t[0] < last - 0.05:
                times[fi] = None
                matched -= 1
            else:
                last = t[1]
    hits = [t is not None for t in times]
    times = interpolate(times, t_from, t_to)
    out = []
    for li, line in enumerate(lines):
        ws = [(word, times[fi]) for fi, (l2, word) in enumerate(flat) if l2 == li]
        out.append({**{k: line[k] for k in ("section", "speaker", "text")},
                    "t0": round(ws[0][1][0], 3), "t1": round(ws[-1][1][1], 3),
                    "words": [{"w": w, "t0": round(t[0], 3), "t1": round(t[1], 3)} for w, t in ws]})
    if detail:
        per_line = [sum(hits[fi] for fi, (l2, _) in enumerate(flat) if l2 == li) for li in range(len(lines))]
        return out, matched, len(flat), per_line
    return out, matched, len(flat)


def even_words(text, t0, t1, norm=norm):
    """Word timings for a line timed by hand: spread over [t0, t1] in proportion to word length."""
    ws = split_words(text)
    weights = [max(2, len(norm(w))) for w in ws]
    total, acc, out = sum(weights), 0.0, []
    for w, wt in zip(ws, weights):
        a = t0 + (t1 - t0) * acc / total
        acc += wt
        out.append({"w": w, "t0": round(a, 3), "t1": round(t0 + (t1 - t0) * acc / total, 3)})
    return out


def snap_onsets(timed, env, fps, quiet=0.08, loud=0.3, gap=0.2, slack=0.4, lead=0.02):
    """Move word starts that Whisper put in a pause forward to where the singing resumes.

    Whisper tends to start a word as soon as the previous one ends, so the first
    word after a pause "starts" in the silence. `env` is the per-video-frame
    vocal loudness (pixelart.audio.envelope). A word whose start is followed by
    at least `gap` seconds of quiet moves to the first loud frame after it
    (looking up to `slack` seconds past its end), and later words are pushed
    along if it now overlaps them. Edits `timed` in place; returns the number
    of words moved.
    """
    flat = [w for line in timed for w in line["words"]]
    n, run = len(env), max(1, int(round(gap * fps)))
    moved = 0
    for i, w in enumerate(flat):
        f0 = int(round(w["t0"] * fps))
        f_end = min(n, int((w["t1"] + slack) * fps))
        if i + 1 < len(flat):
            f_end = min(f_end, int((flat[i + 1]["t1"] - 0.05) * fps))
        f = f0
        while f < f_end and env[f] >= quiet:          # the tail of the previous word
            f += 1
        if f - f0 > 0.1 * fps:                        # quiet only after a real stretch of this word
            continue
        q = f
        while q < f_end and env[q] < quiet:
            q += 1
        if q - f < run:
            continue
        while q < f_end and env[q] < loud:
            q += 1
        if q >= f_end:
            continue
        t = round(q / fps - lead, 3)
        if t <= w["t0"] + 1 / fps:
            continue
        w["t0"] = t
        w["t1"] = round(max(w["t1"], t + 0.12), 3)
        moved += 1
        for later in flat[i + 1:]:                    # keep the words in order
            if later["t0"] >= flat[flat.index(later) - 1]["t0"] + 0.08:
                break
            later["t0"] = round(flat[flat.index(later) - 1]["t0"] + 0.08, 3)
            later["t1"] = round(max(later["t1"], later["t0"] + 0.1), 3)
    for line in timed:
        line["t0"], line["t1"] = line["words"][0]["t0"], line["words"][-1]["t1"]
    return moved


def sheet_lines(text):
    """Sung lines of a lyric sheet (pixelart.lyrics format), ready for `build`."""
    from pixelart import lyrics
    return [{"section": sec["section"], "speaker": sec["speaker"], "text": line, "words": split_words(line)}
            for sec in lyrics.sections(text) for line in sec["lines"]]


def auto(sheet, transcripts, duration, env=None, fps=None):
    """Time a whole lyric sheet against whole-song transcripts in one pass.

    With the vocal loudness envelope (`env`, sampled at `fps`), word starts that
    Whisper put in pauses are moved to where the singing resumes (snap_onsets).
    Returns (timed lines, report), where report lists each line's matched word
    count so weak spots can be checked by ear and fixed by hand.
    """
    lines = sheet_lines(sheet)
    timed, matched, total, per_line = build(transcripts, lines, 0.0, duration, detail=True, strays=True)
    snapped = snap_onsets(timed, env, fps) if env is not None else 0
    report = {"matched": matched, "total": total, "snapped": snapped,
              "lines": [{"t0": ln["t0"], "section": ln["section"], "text": ln["text"],
                         "matched": m, "words": len(ln["words"])} for ln, m in zip(timed, per_line)]}
    return timed, report


def main():
    ap = argparse.ArgumentParser(description="Auto-align PROJECT/lyrics.txt onto its Whisper transcripts.")
    ap.add_argument("project")
    ap.add_argument("--duration", type=float, help="song length in seconds (default: data/song.json)")
    args = ap.parse_args()
    root = Path(args.project)
    data = root / "data"
    duration = args.duration or json.loads((data / "song.json").read_text())["duration"]
    transcripts = [json.loads((data / n).read_text()) for n in ("vocals.whisper.json", "song.whisper.json")
                   if (data / n).exists()]
    env = fps = None
    if (data / "vocal_env.npy").exists():
        import numpy as np
        from pixelart.project import load
        env, fps = np.load(data / "vocal_env.npy"), load(root).fps
    timed, report = auto((root / "lyrics.txt").read_text(), transcripts, duration, env, fps)
    (data / "lyrics_timed.json").write_text(json.dumps(timed, indent=1))
    print_report(report)
    print(f"-> {data / 'lyrics_timed.json'}")


def print_report(report, weak=0.5):
    """Print the timed lines, marking those with under `weak` of their words matched."""
    print(f"matched {report['matched']}/{report['total']} sung words "
          f"({100 * report['matched'] / max(1, report['total']):.0f}%); lines marked ! are mostly interpolated")
    if report.get("snapped"):
        print(f"{report['snapped']} word starts moved out of pauses onto the vocal onsets")
    for ln in report["lines"]:
        flag = "!" if ln["matched"] < weak * ln["words"] else " "
        print(f"{flag} {ln['t0']:7.2f}  {ln['matched']:2d}/{ln['words']:<2d} {ln['section'] or '':10.10s} {ln['text']}")


if __name__ == "__main__":
    main()
