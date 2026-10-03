"""Measure how lyric bars rhyme and scan, to write and revise lyric sheets against.

    python -m pixelart.song.bars projects/NAME/lyrics.txt          # one summary row
    python -m pixelart.song.bars projects/NAME/lyrics.txt --bars   # every bar, with flags
    python -m pixelart.song.bars projects/*/lyrics.txt ~/claude/lyrics-corpus/*/*.txt
    printf '%s\n' "first bar" "second bar" | python -m pixelart.song.bars - --bars

Works on lyric sheets and on plain lyrics. Pronunciations come from CMUdict; words it lacks
get a rough guess from their spelling. Rhymes are matched on vowel sounds alone, the way rap
rhymes ("scenario" / "radio" rhyme on two syllables). The summary columns:

    words   sung words, counted as song.generate counts them (about 650 fit in four minutes)
    syl     syllables per bar (mean and spread)
    long    share of bars over 16 syllables, which a song model rushes or garbles
    end2    share of bars whose end rhymes on 2+ syllables with a bar up to 3 lines away
    chain3  share of bars in a run of 3+ consecutive bars ending on the same two vowels
    RD      rhyme density (Malmi et al. 2016, "DopeLearning"): the mean over words of the
            longest vowel run ending at that word that also ends at one of the 15 words before it
    inner2  words per bar, besides the last, that rhyme on 2+ syllables with a nearby word
    MATTR   vocabulary variety: distinct words per 50-word window
    thats   "that's" / "that ain't" tags per 100 bars (the reference songs use about one)
    nums    number words per 100 words: dates and figures usually mean a history lesson
    names   distinct capitalised names per 100 bars: each one is a fact the listener must know

--bars lists every bar with its syllables, end-rhyme length and inner rhymes, and flags the
bars worth a second look:

    LONG      over 16 syllables
    UNRHYMED  rhymes with no bar up to 3 lines away
    UNEVEN    6+ syllables longer or shorter than the bar it rhymes with
    CLICHE    a stock rhyme pair, such as fire/desire
    THATS     a "that's X" tag, which usually labels a joke instead of landing it
    PROSE     two or more sentences of 3+ words: a setup and its punch crammed into one bar
    TAG       ends on a sentence of four words or fewer after the punch, as in "Seventeen
              percent. Precise." A short answer to a question just before it isn't a tag.
              Neither PROSE nor TAG applies to a line the song repeats, such as a chant.
    NUMBER    a number word: is it the joke, or a fact the joke needs?

A flag only points at a bar to read again. Whether the bar is funny is still a judgement call.
"""
import argparse
import json
import re
import statistics
import sys
from functools import cache
from pathlib import Path

from pixelart import lyrics

VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"}
SAME_VOWEL = {"AO": "AA"}   # cot/caught: rap delivery rarely keeps them apart
WINDOW = 15                 # words looked back for rhyme density, as in DopeLearning
NEIGHBOURS = 3              # bars either side that an end rhyme may pair with
LONG = 16                   # syllables
UNEVEN = 6                  # syllables between a bar and the bar it rhymes with
TAG = re.compile(r"\bthat(?:'s| is| ain't| was)\b", re.I)

# Stock rhyme families: the second word is the one every listener sees coming.
CLICHES = [set(family.split()) for family in """
    fire desire higher liar
    night light fight right tonight bright
    game fame name shame same flame
    crown down town
    throne alone own bone stone
    flow go know show slow
    beat heat street defeat elite
    real deal feel
    sky high fly die lie
    rhyme time prime crime
    king ring thing bling
    gold bold cold old told
    pain rain gain chain
    heart apart start
    true through you do
    fall all call wall
""".strip().splitlines()]

# Rough spelling-to-vowel rules for words CMUdict lacks (names, slang); longer spellings first.
SPELLINGS = [("igh", "AY"), ("eau", "OW"), ("ee", "IY"), ("ea", "IY"), ("oo", "UW"), ("ou", "AW"),
             ("ow", "OW"), ("oi", "OY"), ("oy", "OY"), ("ai", "EY"), ("ay", "EY"), ("ei", "EY"),
             ("ey", "EY"), ("ie", "IY"), ("au", "AA"), ("aw", "AA"), ("oa", "OW"), ("ue", "UW"),
             ("ew", "UW"), ("a", "AE"), ("e", "EH"), ("i", "IH"), ("o", "AA"), ("u", "AH"), ("y", "IY")]

# A vowel before consonant + silent e says its name: "throne", "bite", "cute".
LONG_VOWELS = {"a": "EY", "e": "IY", "i": "AY", "o": "OW", "u": "UW"}

# Abbreviations are said letter by letter ("UN" -> you-en): the vowel of each letter's name.
LETTERS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", [("EY",), ("IY",), ("IY",), ("IY",), ("IY",), ("EH",),
               ("IY",), ("EY",), ("AY",), ("EY",), ("EY",), ("EH",), ("EH",), ("EH",), ("OW",), ("IY",),
               ("UW",), ("AA",), ("EH",), ("IY",), ("UW",), ("IY",), ("AH", "@", "UW"), ("EH",), ("AY",), ("IY",)]))

ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
        "fifteen sixteen seventeen eighteen nineteen").split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
# "one" is left out: it is mostly a pronoun ("the one you're holding").
NUMBER_WORDS = (set(ONES) | set(TENS[2:]) | {"hundred", "thousand", "million", "billion", "trillion"}) - {"one"}


def number_words(n):
    """How a number is said: 34 -> thirty four, 1776 -> seventeen seventy six."""
    if n < 20:
        return [ONES[n]]
    if n < 100:
        return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    if n < 1000:
        return [ONES[n // 100], "hundred"] + (number_words(n % 100) if n % 100 else [])
    if n < 10000:
        return number_words(n // 100) + (number_words(n % 100) if n % 100 else ["hundred"])
    return [ONES[int(d)] for d in str(n)]


INITIALISM = re.compile(r"[A-Z]{2,3}s?")
SAID_AS_WORDS = {"PAC", "GIF", "RAM", "ROM", "LOL", "SIM"}


def words(bar):
    """The sung words of a bar, lower-cased; ad-libs in parentheses are dropped.

    An all-caps word of two or three letters (or its plural) in a line that isn't shouted is
    said letter by letter, so it becomes its letters, upper-cased: "the UN" -> ["the", "U", "N"],
    "BBs" -> ["B", "B"]. The few said as words ("PAC", "GIF") stay words.
    """
    bar = re.sub(r"\(.*?\)", " ", bar).replace("-", " ")
    shouted = bar.isupper()
    out = []
    for tok in re.findall(r"[A-Za-z0-9']+", bar):
        tok = tok.strip("'")
        if tok.isdigit():
            out += number_words(int(tok))
        elif INITIALISM.fullmatch(tok) and not shouted and tok.rstrip("s") not in SAID_AS_WORDS:
            out += list(tok.rstrip("s"))
        elif tok:
            out.append(tok.lower())
    return out


@cache
def cmu():
    import cmudict
    return cmudict.dict()


def vowel_sounds(phones):
    """ARPAbet phones -> vowels without stress. Unstressed AH0 and IH0, and AH2 ("Qatar"), are all
    the schwa "@"."""
    out = []
    for phone in phones:
        base = phone.rstrip("012")
        if phone in ("AH0", "AH2", "IH0"):
            out.append("@")
        elif base in VOWELS:
            out.append(SAME_VOWEL.get(base, base))
    return out


def guess(word):
    """Vowels from spelling. A silent e makes the vowel before it long ("enthrone"). A last syllable
    spelled with a lone a, e, i or u is taken as unstressed ("misanthropic" ends like CMUdict's
    "topic"); a final o is long ("Amerigo"), and so is a final ey after another syllable ("Boney")."""
    w = re.sub(r"[^a-z]", "", word)
    if len(w) > 4 and w.endswith("ed") and w[-3] not in "tdaeiouy":
        w = w[:-1]                           # a silent -ed: "doxxed", "enthroned" -> "enthrone"
    long_vowel = None
    if len(w) > 3 and w.endswith("e") and w[-2] not in "aeiouyl":
        if w[-3] in LONG_VOWELS and w[-4] not in "aeiou":
            long_vowel = LONG_VOWELS[w[-3]]
        w = w[:-1]
    out, spelled, i = [], [], 0
    while i < len(w):
        hit = next(((s, v) for s, v in SPELLINGS if w.startswith(s, i)), None)
        if hit and not (hit[0] == "y" and i == 0):
            out.append(hit[1])
            spelled.append(hit[0])
            i += len(hit[0])
        else:
            i += 1
    if long_vowel and out:
        out[-1] = long_vowel
    elif len(out) > 1 and spelled[-1] in ("a", "e", "i", "u"):
        out[-1] = "@"
    elif spelled and spelled[-1] == "o" and w.endswith("o"):
        out[-1] = "OW"
    elif len(out) > 1 and spelled[-1] == "ey" and w.endswith("ey"):
        out[-1] = "IY"
    return tuple(out) or ("AH",)


@cache
def vowels(word):
    """The vowel sounds of a word, one per syllable."""
    if word in LETTERS:
        return LETTERS[word]
    d = cmu()
    variants = [(word, ())]
    if word.endswith("in"):
        variants.append((word + "g", ()))    # rappin' -> rapping
    if word.endswith("'s"):
        variants.append((word[:-2], ()))
    if word.endswith("ed"):                  # tariffed -> tariff; after t or d, -ed is a syllable
        for stem in (word[:-2], word[:-1]):
            variants.append((stem, ("@",) if stem.rstrip("e").endswith(("t", "d")) else ()))
    for v, extra in variants:
        if v in d:
            return tuple(vowel_sounds(d[v][0])) + extra
    for k in range(3, len(word) - 2):        # compounds: "littest" -> "lit" + "test"
        if word[:k] in d and word[k:] in d:
            return tuple(vowel_sounds(d[word[:k]][0]) + vowel_sounds(d[word[k:]][0]))
    return guess(word)


def song_bars(text):
    """[(section label, bar), ...] for a lyric sheet or plain lyrics (label None without headers)."""
    out = []
    for sec in lyrics.sections(text):
        label = None
        if sec["section"]:
            label = sec["section"] + (f" - {sec['speaker']}" if sec["speaker"] else "")
        out += [(label, line) for line in sec["lines"] if words(line)]
    return out


# A full stop that ends an initial or a title, not a sentence: "Wile E. Coyote", "Mr. Security".
ABBREVIATION = re.compile(r"(?:\b[A-Z]|\b(?:Mr|Mrs|Ms|Dr|St|Jr|Sr|vs))\.$")


def sentences(bar):
    out = []
    for piece in re.split(r"(?<=[.!?])\s+", bar.strip()):
        if out and ABBREVIATION.search(out[-1]):
            out[-1] += " " + piece
        else:
            out.append(piece)
    return [s for s in out if words(s)]


def is_question(sentence):
    return sentence.rstrip(" \"'’”)").endswith("?")


def tail_match(a, b):
    """How many vowels match going backwards from the ends of a and b."""
    k = 0
    while k < min(len(a), len(b)) and a[-1 - k] == b[-1 - k]:
        k += 1
    return k


def mattr(ws, window=50):
    if len(ws) <= window:
        return len(set(ws)) / max(1, len(ws))
    return statistics.mean(len(set(ws[i:i + window])) / window for i in range(len(ws) - window + 1))


def analyse(text):
    """Summary numbers for a song, plus one record per bar (see the module docstring)."""
    bars = song_bars(text)
    toks = [(b, w, vowels(w)) for b, (_, line) in enumerate(bars) for w in words(line)]

    # Rhyme length of every word against the WINDOW words before it, over the song's vowel string.
    seq, ends = [], []
    for _, _, v in toks:
        seq += v
        ends.append(len(seq) if v else None)

    def run(p, q):
        k = 0
        while k < p - q and k < q and seq[p - 1 - k] == seq[q - 1 - k]:
            k += 1
        return k

    rhyme = []
    for i, (_, w, v) in enumerate(toks):
        best = 0
        if v:
            for j in range(max(0, i - WINDOW), i):
                if ends[j] and toks[j][1] != w:
                    best = max(best, run(ends[i], ends[j]))
        rhyme.append(best)

    bar_vowels = [[] for _ in bars]
    bar_words = [[] for _ in bars]
    bar_rhyme = [[] for _ in bars]
    for (b, w, v), r in zip(toks, rhyme):
        bar_vowels[b] += v
        bar_words[b].append(w)
        bar_rhyme[b].append(r)
    counts = {}
    for _, line in bars:
        key = " ".join(words(line))
        counts[key] = counts.get(key, 0) + 1

    recs = []
    for a, (label, line) in enumerate(bars):
        end, partner = 0, None
        for c in range(max(0, a - NEIGHBOURS), min(len(bars), a + NEIGHBOURS + 1)):
            if c != a and bar_words[c][-1] != bar_words[a][-1]:
                k = tail_match(bar_vowels[a], bar_vowels[c])
                if k > end:
                    end, partner = k, c
        syl = len(bar_vowels[a])
        repeated = counts[" ".join(bar_words[a])] > 1
        flags = []
        if syl > LONG:
            flags.append("LONG")
        if not repeated and end == 0:
            flags.append("UNRHYMED")
        if (partner is not None and not repeated and counts[" ".join(bar_words[partner])] == 1
                and abs(syl - len(bar_vowels[partner])) >= UNEVEN):
            flags.append("UNEVEN")
        if partner is not None and any({bar_words[a][-1], bar_words[partner][-1]} <= f for f in CLICHES):
            flags.append("CLICHE")
        if TAG.search(line):
            flags.append("THATS")
        sents = [] if repeated else sentences(line)   # a repeated line is a chant: short bursts are its job
        if (len(sents) > 1 and len(words(sents[-1])) <= 4 and not is_question(sents[-2])
                and any(len(words(x)) >= 3 for x in sents[:-1])):
            flags.append("TAG")
        elif sum(len(words(x)) >= 3 for x in sents) >= 2:
            flags.append("PROSE")
        if NUMBER_WORDS & set(bar_words[a]):
            flags.append("NUMBER")
        recs.append({"label": label, "text": line, "syl": syl, "end": end, "partner": partner,
                     "inner2": sum(1 for r in bar_rhyme[a][:-1] if r >= 2), "flags": flags})

    # Runs of consecutive bars ending on the same two vowels (a repeated line breaks a run).
    tails = [tuple(v[-2:]) if len(v) >= 2 and counts[" ".join(w)] == 1 else None
             for v, w in zip(bar_vowels, bar_words)]
    chained, a = 0, 0
    while a < len(tails):
        b = a
        while tails[a] and b + 1 < len(tails) and tails[b + 1] == tails[a]:
            b += 1
        if b - a >= 2:
            chained += b - a + 1
        a = b + 1

    syls = [r["syl"] for r in recs]
    return {
        "bars": len(recs),
        "words": len(lyrics.sung_words(text)),
        "syl": statistics.mean(syls),
        "syl_sd": statistics.pstdev(syls),
        "long": sum(s > LONG for s in syls) / len(recs),
        "end2": sum(r["end"] >= 2 for r in recs) / len(recs),
        "chain3": chained / len(recs),
        "RD": statistics.mean(r for r, (_, _, v) in zip(rhyme, toks) if v),
        "inner2": statistics.mean(r["inner2"] for r in recs),
        "MATTR": mattr([w for _, w, _ in toks]),
        "thats": 100 * sum(len(TAG.findall(line)) for _, line in bars) / len(recs),
        "nums": 100 * sum(w in NUMBER_WORDS for _, w, _ in toks) / len(toks),
        "names": 100 * len(lyrics.proper_nouns(text, limit=None)) / len(recs),
        "flagged": sum(bool(r["flags"]) for r in recs) / len(recs),
        "per_bar": recs,
    }


def name_of(path):
    if path == "-":
        return "stdin"
    p = Path(path).resolve()
    return p.parent.name if p.name == "lyrics.txt" else f"{p.parent.name}/{p.stem}"


COLUMNS = [("bars", "{:>4.0f}"), ("words", "{:>5.0f}"), ("syl", "{:>5.1f}"), ("syl_sd", "{:>5.1f}"), ("long", "{:>5.0%}"),
           ("end2", "{:>5.0%}"), ("chain3", "{:>6.0%}"), ("RD", "{:>5.2f}"), ("inner2", "{:>6.2f}"), ("MATTR", "{:>5.2f}"),
           ("thats", "{:>5.0f}"), ("nums", "{:>4.1f}"), ("names", "{:>5.0f}"), ("flagged", "{:>7.0%}")]


def print_table(results):
    width = max(len(r["name"]) for r in results) + 2
    print(f"{'':{width}}" + " ".join(f"{c:>{len(f.format(0))}}" for c, f in COLUMNS))
    groups = {}
    for r in results:
        groups.setdefault(r["name"].split("/")[0] if "/" in r["name"] else "our sheets", []).append(r)
    for group, rows in groups.items():
        for r in rows:
            print(f"{r['name']:{width}}" + " ".join(f.format(r[c]) for c, f in COLUMNS))
        if len(rows) > 1:
            med = {c: statistics.median(r[c] for r in rows) for c, _ in COLUMNS}
            print(f"{'  median ' + group:{width}}" + " ".join(f.format(med[c]) for c, f in COLUMNS))
        print()


def print_bars(result):
    print(f"== {result['name']}   (syl = syllables, end = end-rhyme syllables, in = inner 2+ rhymes)")
    label = object()
    for r in result["per_bar"]:
        if r["label"] != label:
            label = r["label"]
            print(f"[{label}]" if label else "")
        print(f"  {r['syl']:3} {r['end']:2} {r['inner2']:2}  {r['text']}" + (f"   <- {' '.join(r['flags'])}" if r["flags"] else ""))
    print()


def main():
    ap = argparse.ArgumentParser(description="Rhyme and scansion numbers for lyric sheets or plain lyrics.")
    ap.add_argument("files", nargs="+", help="lyric sheets or plain lyrics, one bar per line; - reads stdin")
    ap.add_argument("--bars", action="store_true", help="list every bar with its numbers and flags")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    results = []
    for f in args.files:
        res = analyse(sys.stdin.read() if f == "-" else Path(f).read_text())
        res["name"] = name_of(f)
        results.append(res)
    if args.json:
        print(json.dumps(results, indent=1))
        return
    if args.bars:
        for res in results:
            print_bars(res)
    print_table(results)


if __name__ == "__main__":
    main()
