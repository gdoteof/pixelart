"""Score how intelligibly each take sings its lyrics.

    python -m pixelart.song.check PROJECT      -> build/takes/report.md

Transcribes every build/takes/*.flac with faster-whisper (cached per take in
<take>.transcript.json) and compares it with lyrics.txt:
    coverage  share of sung lyric words heard, in order (higher is better)
    WER       word error rate (lower is better); ad-libs and repeats count against it
These measure diction and lyric adherence only, not whether the take is any
good: listen before picking. Needs `uv sync --extra audio` and a CUDA GPU.
"""
import argparse
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from pixelart import lyrics


def wer(ref, hyp):
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i]
        for j, h in enumerate(hyp, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r != h)))
        prev = cur
    return prev[-1] / max(1, len(ref))


def coverage(ref, hyp):
    blocks = SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks()
    return sum(b.size for b in blocks) / max(1, len(ref))


def words_of(text):
    return re.findall(r"[a-z0-9']+", text.lower().replace("-", " "))


def main():
    from pixelart.gpu import ensure_cuda_libs
    ensure_cuda_libs()
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    takes = root / "build" / "takes"
    sheet = (root / "lyrics.txt").read_text()
    ref = lyrics.sung_words(sheet)
    prompt = lyrics.whisper_prompt(sheet)

    from pixelart.audio.transcribe import transcribe
    rows = []
    for audio in sorted(takes.glob("*.flac")):
        cache = audio.with_suffix(".transcript.json")
        if not cache.exists() or cache.stat().st_mtime < audio.stat().st_mtime:
            print(f"transcribing {audio.name}", flush=True)
            cache.write_text(json.dumps(transcribe(audio, prompt, log=None)))
        hyp = words_of(" ".join(w["w"] for w in json.loads(cache.read_text())))
        meta_file = audio.with_suffix(".json")
        meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
        rows.append({"take": audio.stem, "model": meta.get("model", "?"),
                     "coverage": coverage(ref, hyp), "wer": wer(ref, hyp), "words": len(hyp)})

    rows.sort(key=lambda r: (-r["coverage"], r["wer"]))
    lines = [f"# Takes for {root.name}", "",
             f"Lyric check against lyrics.txt ({len(ref)} sung words). Coverage: share of lyric words heard "
             "in order. WER: word error rate. Diction only; listen before picking "
             f"(`build/takes/listen/`).", "",
             "| Take | Model | Coverage | WER | Words heard |", "|---|---|---|---|---|"]
    lines += [f"| {r['take']} | {r['model']} | {100 * r['coverage']:.1f}% | {100 * r['wer']:.1f}% | {r['words']} |"
              for r in rows]
    (takes / "report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[4:]))
    print(f"-> {takes / 'report.md'}")


if __name__ == "__main__":
    main()
