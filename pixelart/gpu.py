"""GPU plumbing shared by the CLIs that use CUDA.

faster-whisper's ctranslate2 loads cuBLAS/cuDNN from the pip `nvidia-*` wheels,
and the dynamic loader only reads LD_LIBRARY_PATH at process start, so
`ensure_cuda_libs()` re-executes the current command with the path set.
"""
import os
import subprocess
import sys
from pathlib import Path


def ensure_cuda_libs(subdirs=("cublas", "cudnn")):
    """Re-exec this process with the pip CUDA libraries on LD_LIBRARY_PATH, once."""
    try:
        import nvidia
    except ImportError:
        return
    libs = [str(Path(p) / s / "lib") for p in nvidia.__path__ for s in subdirs if (Path(p) / s / "lib").is_dir()]
    current = [d for d in os.environ.get("LD_LIBRARY_PATH", "").split(":") if d]
    if not libs or all(d in current for d in libs):
        return
    env = {**os.environ, "LD_LIBRARY_PATH": ":".join(libs + current)}
    os.execve(sys.executable, sys.orig_argv, env)


def vram_gib(index=0):
    """Total memory of a CUDA device in GiB (from nvidia-smi), or None without one."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits",
                              f"--id={index}"], capture_output=True, text=True, check=True).stdout
        return int(out.strip()) / 1024
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None
