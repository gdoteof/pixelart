"""Word-level timestamps with faster-whisper on the GPU.

    python -m pixelart.audio.transcribe AUDIO OUT.json [--prompt "Names, Jargon, ..."]

Transcribe both the vocal stem and the full mix: they fail in different
places, and pixelart.audio.align takes the first sane match from either.
ctranslate2 needs the pip CUDA libraries on the loader path, set before Python starts:

    SP=.venv/lib/python3.12/site-packages/nvidia
    LD_LIBRARY_PATH=$SP/cublas/lib:$SP/cudnn/lib uv run python -m pixelart.audio.transcribe ...
"""
import argparse
import json


def transcribe(src, prompt=None, model="large-v3", device="cuda", log=print):
    """[{"w", "t0", "t1", "p"}, ...] for every recognised word.

    `prompt` primes Whisper with names and jargon from the lyrics, which keeps it
    from inventing spellings for them.
    """
    from faster_whisper import WhisperModel
    segments, _ = WhisperModel(model, device=device, compute_type="float16").transcribe(
        str(src),
        language="en",
        word_timestamps=True,
        initial_prompt=prompt,
        condition_on_previous_text=False,
        vad_filter=False,
        beam_size=5,
    )
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({"w": w.word.strip(), "t0": round(w.start, 3), "t1": round(w.end, 3),
                          "p": round(w.probability, 3)})
        if log:
            log(f"[{seg.start:7.2f} {seg.end:7.2f}] {seg.text.strip()}")
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--prompt")
    ap.add_argument("--model", default="large-v3")
    args = ap.parse_args()
    words = transcribe(args.src, args.prompt, args.model, log=lambda s: print(s, flush=True))
    with open(args.out, "w") as f:
        f.write(json.dumps(words, indent=0))
    print("wrote", args.out, len(words), "words")


if __name__ == "__main__":
    main()
