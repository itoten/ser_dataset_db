"""Read the egs3 recipes from the espnet fork's git branch (not the working tree).

Reading `git show <branch>:<path>` keeps the database independent of whichever
branch happens to be checked out in the espnet working tree.
"""

import json
import re
import subprocess
from pathlib import Path

import yaml

BRANCH = "ser/cross-corpus"
SYSTEM = "cls"
REPO = Path(__file__).resolve().parent.parent.parent.parent / "espnet"
# Recipes that train on one corpus but are not the plain single-corpus layout.
VARIANTS = {"msppodcast_full8"}
SPLIT_KEY = re.compile(r"split|ratio|seed|official|_speakers")


def git(*args):
    out = subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    )
    return out.stdout


def exists(path):
    r = subprocess.run(
        ["git", "-C", str(REPO), "cat-file", "-e", f"{BRANCH}:{path}"],
        capture_output=True,
    )
    return r.returncode == 0


def read(path):
    return git("show", f"{BRANCH}:{path}")


def load_yaml(path):
    return yaml.safe_load(read(path))


def recipes():
    """Names of every egs3 directory that holds a `cls` system, except TEMPLATE."""
    names = [p.split("/")[1] for p in git("ls-tree", "--name-only", BRANCH, "egs3/").split()]
    return sorted(
        n for n in names if n != "TEMPLATE" and exists(f"egs3/{n}/{SYSTEM}")
    )


def first_commit(recipe):
    """(first 10 hash chars, date) of the commit that first put the cls config.yaml on the branch."""
    out = git(
        "log", BRANCH, "--diff-filter=A", "--reverse", "--format=%H %cs", "--",
        f"egs3/{recipe}/{SYSTEM}/dataset/config.yaml",
    ).split("\n")[0]
    h, d = out.split()
    return h[:10], d


def _get(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def _num(v):
    return "NA" if v is None else str(v)


def derive(recipe):
    """The recipe columns that come straight from the committed egs3 files."""
    base = f"egs3/{recipe}/{SYSTEM}"
    cfg = load_yaml(f"{base}/dataset/config.yaml")
    builder = cfg.get("builder", {})
    if "train_corpora" in builder:
        kind = "multi_corpus"
    elif recipe in VARIANTS:
        kind = "single_corpus_variant"
    else:
        kind = "single_corpus"
    train = load_yaml(f"{base}/conf/training.yaml")
    train3 = (
        load_yaml(f"{base}/conf/training_3gpu.yaml")
        if exists(f"{base}/conf/training_3gpu.yaml")
        else None
    )
    h, d = first_commit(recipe)
    urls = []
    for u in re.findall(r"https?://[^\s\"'<>)]+", read(f"{base}/dataset/config.yaml")):
        u = u.rstrip(".,;")
        if u not in urls:
            urls.append(u)
    split = {k: v for k, v in builder.items() if SPLIT_KEY.search(k) and k != "manifest_paths"}
    return {
        "recipe": recipe,
        "recipe_kind": kind,
        "system": SYSTEM,
        "recipe_path": base,
        "first_commit": h,
        "first_commit_date": d,
        "source_env_var": builder.get("source_env_var") or "NA",
        "output_env_var": builder.get("output_env_var") or "NA",
        "config_urls": ";".join(urls) or "none",
        "split_config": json.dumps(split, ensure_ascii=False, sort_keys=True, separators=(",", ":")) if split else "NA",
        "num_classes": _num(_get(train, "model", "num_classes")),
        "min_wav_duration": _num(_get(train, "remove_long_short", "min_wav_duration")),
        "max_wav_duration": _num(_get(train, "remove_long_short", "max_wav_duration")),
        "max_epochs": _num(_get(train, "trainer", "max_epochs")),
        "max_epochs_3gpu": _num(_get(train3, "trainer", "max_epochs")),
    }


SYNC_COLUMNS = [
    "recipe_kind", "system", "recipe_path", "first_commit", "first_commit_date",
    "source_env_var", "output_env_var", "config_urls", "split_config", "num_classes",
    "min_wav_duration", "max_wav_duration", "max_epochs", "max_epochs_3gpu",
]
