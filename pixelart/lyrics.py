"""Lyric sheets: the one text file a song starts from.

A sheet is plain lines of lyrics under bracketed section headers:

    [Verse 1 - Sam Altman: calm, smug, deep male voice]
    Dario, you're living out your worst-case scenario
    ...
    [Hook - Crowd Chant]
    Code red! Red line!
    [crowd roars]

A header is `[Section]`, `[Section - Speaker]` or `[Section - Speaker: performance note]`,
where Section starts with a structure word (Intro, Verse, Chorus, Hook, Bridge, ...).
Any other bracketed line, like `[crowd roars]`, is a stage direction: it is not
sung and belongs to no section.

Song models want only plain structure tags (`model_lyrics`); alignment and the
video want the sung lines with their section and speaker (`lines`).
"""
import re

# First word of a section header -> the tag song models understand.
MODEL_TAGS = {
    "intro": "Intro", "verse": "Verse", "prechorus": "Pre-Chorus", "chorus": "Chorus",
    "hook": "Chorus", "refrain": "Chorus", "postchorus": "Chorus", "bridge": "Bridge",
    "breakdown": "Bridge", "interlude": "Interlude", "break": "Break", "drop": "Drop",
    "reprise": "Chorus", "outro": "Outro", "instrumental": "Instrumental", "skit": "Interlude",
}


def parse_header(line):
    """(section, speaker, note) for a section header line, else None.

    "[Verse 1 - Sam Altman: calm, smug]" -> ("Verse 1", "Sam Altman", "calm, smug")
    """
    m = re.fullmatch(r"\s*\[(.+?)\]\s*", line)
    if not m:
        return None
    body = m.group(1)
    head, _, note = body.partition(":")
    section, _, speaker = head.partition(" - ")
    section = section.strip()
    first = re.sub(r"[^a-z]", "", section.lower().split()[0]) if section else ""
    if first not in MODEL_TAGS:
        return None
    return section, speaker.strip() or None, note.strip() or None


def is_direction(line):
    """A bracketed line that is not a section header, e.g. "[crowd roars]"."""
    return bool(re.fullmatch(r"\s*\[.*\]\s*", line)) and parse_header(line) is None


def sections(text):
    """[{"section", "speaker", "note", "lines": [sung line, ...]}, ...] in sheet order.

    Lines before the first header go in a section named None.
    """
    out, cur = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or is_direction(line):
            continue
        header = parse_header(line)
        if header:
            cur = {"section": header[0], "speaker": header[1], "note": header[2], "lines": []}
            out.append(cur)
            continue
        if cur is None:
            cur = {"section": None, "speaker": None, "note": None, "lines": []}
            out.append(cur)
        cur["lines"].append(line)
    return out


def model_lyrics(text):
    """The sheet as song-model input: plain structure tags, speakers, notes and directions dropped."""
    blocks = []
    for sec in sections(text):
        if not sec["lines"]:
            continue
        tag = "Verse"
        if sec["section"]:
            first = re.sub(r"[^a-z]", "", sec["section"].lower().split()[0])
            tag = MODEL_TAGS[first]
        blocks.append(f"[{tag}]\n" + "\n".join(sec["lines"]))
    return "\n\n".join(blocks) + "\n"


def sung_words(text):
    """Every sung word, lower-cased with punctuation stripped, for intelligibility checks."""
    words = []
    for sec in sections(text):
        for line in sec["lines"]:
            words += re.findall(r"[a-z0-9']+", line.lower().replace("-", " "))
    return words


# Words capitalised only because they start a sentence mid-line ("...Delhi! So tonight").
COMMON = set("""a an and are as ask at be but by can do don't for from get go he her here his how i i'd
i'll i'm i've if in is it it's just let let's like man my nah no not now oh of on or our say she so
that that's the their then there they this to too uh up we well what when where who why will with
yeah yes yo you you're your""".split())


def proper_nouns(text, limit=30):
    """Capitalised names and jargon from the sung lines, to prime speech recognition.

    Skips each line's first word and common words that are capitalised only
    because a sentence starts mid-line. Keep the list short: long, irrelevant
    bias lists make recognisers worse.
    """
    seen = []
    for sec in sections(text):
        for line in sec["lines"]:
            for w in re.findall(r"[A-Za-z0-9][\w'-]*", line)[1:]:
                w = re.sub(r"'s$", "", w.strip("'-"))
                if w.lower() in COMMON or not (w[0].isupper() or any(c.isdigit() for c in w)):
                    continue
                if w not in seen:
                    seen.append(w)
    return seen[:limit]


def whisper_prompt(text):
    """Proper nouns as a Whisper initial prompt ("Sam Altman, Anthropic, ..."), or None if there are none."""
    names = proper_nouns(text)
    return ", ".join(names) + "." if names else None
