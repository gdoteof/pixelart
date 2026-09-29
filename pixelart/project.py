"""Loading a video project: a directory (usually projects/<name>/) with a project.py.

project.py is the contract between a project and the shared tools:

    FPS = 24                              frames per second
    END = 199.75                          seconds to render
    AUDIO = ROOT / "audio" / "song.wav"   muxed into the render; None for a silent video
    OUTPUT = ROOT / "name.mp4"            optional, defaults to <dir name>.mp4
    SIZE = (1920, 1080)                   optional, output frame size
    def render_frame(t): ...              PIL RGB image of SIZE for time t (seconds)
    def label(t): ...                     optional, caption for preview sheets

Project modules import each other flat (`import timeline`), so the project
directory goes on sys.path; only one project is loaded per process.
"""
import importlib
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Project:
    root: Path
    fps: int
    end: float
    size: tuple
    audio: Path | None
    output: Path
    render_frame: Callable
    label: Callable

    @property
    def build(self):
        return self.root / "build"

    @property
    def frames(self):
        return int(round(self.end * self.fps))


@lru_cache(maxsize=None)
def load(path):
    root = Path(path).resolve()
    if not (root / "project.py").is_file():
        raise SystemExit(f"{root} is not a project (no project.py)")
    sys.path.insert(0, str(root))
    mod = importlib.import_module("project")
    if Path(mod.__file__).resolve().parent != root:
        raise RuntimeError(f"imported {mod.__file__} instead of {root}/project.py")
    audio = getattr(mod, "AUDIO", None)
    return Project(root=root, fps=mod.FPS, end=mod.END, size=tuple(getattr(mod, "SIZE", (1920, 1080))),
                   audio=Path(audio) if audio else None,
                   output=Path(getattr(mod, "OUTPUT", root / f"{root.name}.mp4")),
                   render_frame=mod.render_frame, label=getattr(mod, "label", lambda t: ""))
