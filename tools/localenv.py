"""Machine-specific settings, read from `.env` at the repository root.

`.env` is git-ignored; copy `.env.example` and fill it in. Values already set in the
environment win over the file. Nothing machine-specific belongs in tracked files.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load():
    path = ROOT / ".env"
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), os.path.expanduser(value.strip().strip('"').strip("'")))


def espnet_repo():
    """The ESPnet checkout holding the recipes: ESPNET_REPO, else a sibling `espnet` directory."""
    load()
    if os.environ.get("ESPNET_REPO"):
        return Path(os.environ["ESPNET_REPO"])
    return ROOT.parent.parent / "espnet"
