"""Per-line gags, registered into video.GAGS by the section modules.

GAGS_ONLY=gags_v1,gags_intro limits which modules load (handy while one is being worked on).
"""
import importlib
import os

MODULES = ("gags_intro", "gags_v1", "gags_v2", "gags_v3", "gags_v4", "gags_outro")
_only = [m for m in os.environ.get("GAGS_ONLY", "").split(",") if m]
for _name in MODULES:
    if _only and _name not in _only:
        continue
    try:
        importlib.import_module(_name)
    except ModuleNotFoundError as e:
        if e.name != _name:
            raise
