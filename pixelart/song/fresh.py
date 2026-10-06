"""Check a new lyric sheet against the earlier ones, without reading them.

    python -m pixelart.song.fresh projects/NAME                  # against every other project's sheet
    python -m pixelart.song.fresh projects/NAME --spent alt-f4   # what an earlier sheet used up

Songs on one channel drift towards the same jokes. A returning character pulls the same famous
facts, and a sheet drafted next to an old one picks up its hook and its pet words. This lists what
a draft shares with each earlier sheet as words and short phrases, never as lines, so the earlier
sheets can't turn into a model for the new one:

    names    words capitalised in both sheets: usually the same person or fact used again
    phrases  runs of two to four words in both, with two or more content words ("code red")
    words    the other content words in both, leaving out words that more than a third of the
             earlier sheets use; mostly noise, but a pet word shows up here

--spent lists an earlier sheet's own names and content words, alphabetically. Run it before
drafting when a character returns, and treat the references in it as used up.
"""
import argparse
import re
import textwrap
from pathlib import Path

from pixelart import lyrics
from pixelart.song.bars import FUNCTION

PROJECTS = Path("projects")


def sheet_path(arg):
    """A sheet from a project directory, a project name or a path to the sheet itself."""
    p = Path(arg)
    if p.is_dir():
        return p / "lyrics.txt"
    return p if p.exists() else PROJECTS / arg / "lyrics.txt"


def sung(text):
    """The sung words in order, lower-cased, with the possessive "'s" dropped."""
    out = []
    for sec in lyrics.sections(text):
        for line in sec["lines"]:
            out += [re.sub(r"'s$", "", w.strip("'-")) for w in re.findall(r"[a-z][a-z'-]*", line.lower())]
    return [w for w in out if w]


def is_content(word):
    return len(word) > 2 and word not in FUNCTION


def names(text):
    return {n.lower() for n in lyrics.proper_nouns(text, limit=10 ** 6) if is_content(n.lower())}


def phrases(words):
    """Every run of two to four words that holds two or more content words."""
    return {" ".join(words[i:i + n]) for n in (2, 3, 4) for i in range(len(words) - n + 1)
            if sum(map(is_content, words[i:i + n])) >= 2}


def shared(new, old, everyday=frozenset()):
    """{"names", "phrases", "words"}: what two sheets' texts have in common, each sorted.

    Words in `everyday` are left out of "words", but still count as names and inside phrases.
    """
    a, b = sung(new), sung(old)
    both = {w for w in set(a) & set(b) if is_content(w)}
    named = both & names(new) & names(old)
    runs = phrases(a) & phrases(b)
    runs = {r for r in runs if not any(r != longer and f" {r} " in f" {longer} " for longer in runs)}
    return {"names": sorted(named), "phrases": sorted(runs), "words": sorted(both - named - everyday)}


def everyday_words(texts):
    """Content words that more than a third of these sheets use: the channel's common stock."""
    seen = [set(sung(t)) for t in texts]
    return frozenset(w for w in set().union(*seen) if sum(w in s for s in seen) > max(1, len(seen) // 3))


def print_list(label, items, indent):
    if items:
        lead = f"{label:<9}"
        body = textwrap.fill(", ".join(items), 100 - indent - len(lead), subsequent_indent=" " * (indent + len(lead)))
        print(" " * indent + lead + body)


def main():
    ap = argparse.ArgumentParser(description="What a lyric sheet shares with earlier sheets: words and phrases, never lines.")
    ap.add_argument("sheet", nargs="?", help="project directory, project name or lyric sheet to check")
    ap.add_argument("--against", nargs="+", metavar="SHEET",
                    help="sheets to compare with (default: every other project's lyrics.txt)")
    ap.add_argument("--spent", metavar="SHEET", help="list an earlier sheet's names and content words instead")
    args = ap.parse_args()

    if args.spent:
        text = sheet_path(args.spent).read_text()
        named = names(text)
        print_list("names", sorted(named), 0)
        print_list("words", sorted({w for w in sung(text) if is_content(w)} - named), 0)
        return
    if not args.sheet:
        ap.error("give a sheet to check, or --spent SHEET")

    path = sheet_path(args.sheet)
    new = path.read_text()
    others = [sheet_path(a) for a in args.against] if args.against else sorted(
        p for p in PROJECTS.glob("*/lyrics.txt") if p.parent.name != "_template")
    others = [o for o in others if o.resolve() != path.resolve()]
    everyday = everyday_words([o.read_text() for o in others])
    for other in others:
        found = shared(new, other.read_text(), everyday)
        print(other.parent.name)
        if not any(found.values()):
            print("  nothing shared")
        for label in ("names", "phrases", "words"):
            print_list(label, found[label], 2)


if __name__ == "__main__":
    main()
