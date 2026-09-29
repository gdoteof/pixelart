"""Per-line visual gags, registered into gagkit.GAGS by the section modules.

GAGS_ONLY=gags_v1,gags_misc limits which modules load (handy while one is being worked on).
"""
import importlib
import os

from gagkit import GAGS  # noqa: F401  (re-exported for video.py)

MODULES = ("gags_v1", "gags_v2", "gags_v3", "gags_v4", "gags_misc")
_only = [m for m in os.environ.get("GAGS_ONLY", "").split(",") if m]
for _name in MODULES:
    if _only and _name not in _only:
        continue
    try:
        importlib.import_module(_name)
    except ModuleNotFoundError as e:
        if e.name != _name:
            raise
