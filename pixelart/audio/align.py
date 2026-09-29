"""Snap transcribed word timings onto the real lyrics.

Whisper mishears names and sometimes invents filler ("yo, yo, yo"), so we run
a fuzzy global alignment between the lyric tokens and the recognised tokens,
keep the timings of matched words and interpolate the rest from their neighbours.

A song supplies the lyric sheet, a time window per section (where it sits in
the recording) and any tokeniser tweaks or hand fixes; see
projects/alt-f4/align.py. Output lines have the shape pixelart.timing expects:
{"section", "speaker", "text", "t0", "t1", "words": [{"w", "t0", "t1"}, ...]}.
"""
import re
from difflib import SequenceMatcher

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


def build(transcripts, lines, t_from, t_to, tokens_of=tokens_of):
    """Align lyric lines against several transcripts; per word keep the first sane match.

    Returns (timed lines, matched word count, total word count).
    """
    flat = [(li, word) for li, line in enumerate(lines) for word in line["words"]]
    words = [w for _, w in flat]
    per = [match_times(rec, words, t_from, t_to, tokens_of) for rec in transcripts]
    times, matched = [], 0
    for fi in range(len(flat)):
        pick = next((p[fi] for p in per if p[fi] is not None), None)
        matched += pick is not None
        times.append(pick)
    # Keep time monotonic: a match that lands before its predecessor is discarded.
    last = t_from
    for fi, t in enumerate(times):
        if t is not None:
            if t[0] < last - 0.05:
                times[fi] = None
                matched -= 1
            else:
                last = t[1]
    times = interpolate(times, t_from, t_to)
    out = []
    for li, line in enumerate(lines):
        ws = [(word, times[fi]) for fi, (l2, word) in enumerate(flat) if l2 == li]
        out.append({**{k: line[k] for k in ("section", "speaker", "text")},
                    "t0": round(ws[0][1][0], 3), "t1": round(ws[-1][1][1], 3),
                    "words": [{"w": w, "t0": round(t[0], 3), "t1": round(t[1], 3)} for w, t in ws]})
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
