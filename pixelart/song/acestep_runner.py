"""Generate takes with ACE-Step 1.5. Runs inside ACE-Step's own venv, not pixelart's.

    $ACESTEP/.venv/bin/python acestep_runner.py --ace $ACESTEP --lyrics-file L --style-file S \
        --out DIR --dit acestep-v15-xl-turbo --seeds 1 2

Writes DIR/seed<N>/<id>.flac and DIR/seed<N>/run.json. Standalone on purpose:
pixelart is not installed in that venv. pixelart.song.models builds the command.

With --src-audio and one or more --repaint START:END windows it regenerates
only those windows of the source, one after another, keeping the rest of the
audio as context; the style file then describes the repainted parts.
"""
import argparse
import json
import shutil
import sys
import time
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--ace", required=True, help="ACE-Step-1.5 checkout (with checkpoints/)")
parser.add_argument("--lyrics-file", required=True)
parser.add_argument("--style-file", required=True)
parser.add_argument("--out", required=True)
parser.add_argument("--dit", default="acestep-v15-turbo")
parser.add_argument("--lm", default="acestep-5Hz-lm-1.7B")
parser.add_argument("--seeds", type=int, nargs="+", default=[1])
parser.add_argument("--language", default="en")
parser.add_argument("--bpm", type=int)
parser.add_argument("--duration", type=float, default=-1, help="seconds; -1 lets the LM choose from the lyrics")
parser.add_argument("--lm-backend", default="vllm", choices=["vllm", "pt"],
                    help="pt moves the LM to CPU after planning; vllm keeps ~4.7 GB on the GPU")
parser.add_argument("--offload-dit", action="store_true", help="move the DiT to CPU between uses")
parser.add_argument("--src-audio", help="repaint: the audio to regenerate parts of")
parser.add_argument("--repaint", action="append", default=[], metavar="START:END",
                    help="repaint: a window in seconds (3-90 s long); repeat for several, applied in order")
parser.add_argument("--quantization", default="none",
                    choices=["none", "int8_weight_only", "fp8_weight_only", "w8a8_dynamic"])
args = parser.parse_args()

ace = Path(args.ace).resolve()
sys.path.insert(0, str(ace))
from acestep.handler import AceStepHandler  # noqa: E402
from acestep.inference import GenerationConfig, GenerationParams, generate_music  # noqa: E402
from acestep.llm_inference import LLMHandler  # noqa: E402

style = Path(args.style_file).read_text().strip()
lyrics = Path(args.lyrics_file).read_text()
out = Path(args.out)
quantized = args.quantization != "none"

dit = AceStepHandler()
status, ok = dit.initialize_service(
    project_root=str(ace), config_path=args.dit, device="cuda",
    offload_to_cpu=True, offload_dit_to_cpu=args.offload_dit,
    quantization=args.quantization if quantized else None,
    compile_model=quantized,  # ACE-Step's quantized path requires torch.compile
)
print(status, flush=True)
if not ok:
    sys.exit(1)
lm = LLMHandler()
status, ok = lm.initialize(checkpoint_dir=str(ace / "checkpoints"), lm_model_path=args.lm,
                           backend=args.lm_backend, device="cuda", offload_to_cpu=True)
print(status, flush=True)
if not ok:
    sys.exit(1)

turbo = "turbo" in args.dit
windows = [tuple(float(t) for t in w.split(":")) for w in args.repaint]
if windows and not args.src_audio:
    sys.exit("--repaint needs --src-audio")
failed = 0
for seed in args.seeds:
    seed_dir = out / f"seed{seed}"
    shutil.rmtree(seed_dir, ignore_errors=True)
    config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[seed], audio_format="flac")
    common = dict(caption=style, lyrics=lyrics, vocal_language=args.language, bpm=args.bpm, seed=seed,
                  shift=3.0 if turbo else 1.0, inference_steps=8 if turbo else 50)
    # text2music is one step; repaint is one step per window, each on the previous step's output
    steps = [(seed_dir, GenerationParams(task_type="text2music", duration=args.duration, **common))]
    if windows:
        steps = [(seed_dir / f"step{i}", dict(start=a, end=b)) for i, (a, b) in enumerate(windows)]
    start = time.perf_counter()
    src, audio = args.src_audio, None
    for step_dir, params in steps:
        if isinstance(params, dict):
            params = GenerationParams(task_type="repaint", src_audio=src, repainting_start=params["start"],
                                      repainting_end=params["end"], chunk_mask_mode="explicit", **common)
        result = generate_music(dit, lm, params, config, save_dir=str(step_dir))
        if not result.success:
            break
        src = audio = result.audios[0]["path"]
    elapsed = time.perf_counter() - start
    if not result.success:
        print(f"seed {seed} failed: {result.error}", flush=True)
        failed += 1
        continue
    if windows:  # the last step's audio is the take
        final = seed_dir / Path(audio).name
        shutil.copyfile(audio, final)
        audio = str(final)
    (seed_dir / "run.json").write_text(json.dumps({
        "dit": args.dit, "lm": args.lm, "lm_backend": args.lm_backend, "offload_dit": args.offload_dit,
        "quantization": args.quantization, "seed": seed, "bpm": args.bpm, "duration": args.duration,
        "src_audio": args.src_audio, "repaint": windows,
        "seconds": round(elapsed, 1), "audio": [audio],
    }, indent=2) + "\n")
    print(f"seed {seed}: {audio} ({elapsed:.0f}s)", flush=True)
sys.exit(1 if failed else 0)
