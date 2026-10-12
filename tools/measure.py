"""Measure the built corpus of each single-corpus egs3 recipe and write measurements/<recipe>.json.

Run with the espnet environment (needs soundfile and the pixi.toml output paths):
    cd /home/tenshi/projects/espnet && pixi run python ../espnet_work/ser_dataset_db/tools/measure.py --all
"""

import argparse
import collections
import hashlib
import json
import os
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import egs3  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "measurements"


def lines(path):
    return [ln.rstrip("\n") for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()


def measure(recipe):
    cfg = egs3.load_yaml(f"egs3/{recipe}/cls/dataset/config.yaml")
    var = cfg["builder"]["output_env_var"]
    out_dir = Path(os.environ[var]) if var in os.environ else None
    if out_dir is None or not (out_dir / "manifest").is_dir():
        return None
    result = {"recipe": recipe, "output_env_var": var, "output_dir": str(out_dir),
              "measured_on": date.today().isoformat(), "splits": {}}
    fmt = collections.Counter()
    all_durs = []
    with ThreadPoolExecutor(16) as pool:
        for split in cfg["builder"]["manifest_paths"]:
            mpath = out_dir / "manifest" / f"{split}.tsv"
            rows = [ln.split("\t") for ln in lines(mpath)]
            assert all(len(r) == 3 for r in rows), mpath
            infos = list(pool.map(lambda r: sf.info(r[1]), rows))
            durs = [i.duration for i in infos]
            for i in infos:
                fmt[f"{i.samplerate}Hz/{i.channels}ch/{i.subtype}"] += 1
            all_durs += durs
            fpath = out_dir / "manifest_filtered" / f"{split}.tsv"
            result["splits"][split] = {
                "manifest_sha1": sha1(mpath),
                "n": len(rows),
                "n_filtered": len(lines(fpath)) if fpath.is_file() else None,
                "labels": dict(sorted(collections.Counter(r[2] for r in rows).items())),
                "hours": round(sum(durs) / 3600, 4),
                "under_0.5s": sum(d < 0.5 for d in durs),
                "over_30s": sum(d > 30 for d in durs),
                "unique_utt": len({r[0] for r in rows}),
            }
    result["audio_format"] = dict(sorted(fmt.items()))
    result["duration_sec"] = {
        "min": round(min(all_durs), 3), "max": round(max(all_durs), 3),
        "median": round(statistics.median(all_durs), 3),
    }
    result["n_total"] = len(all_durs)
    result["hours_total"] = round(sum(all_durs) / 3600, 4)
    tl = out_dir / "token_list"
    result["token_list"] = [t for t in tl.read_text().split() if t != "<unk>"] if tl.is_file() else None
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recipes", nargs="*")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    names = args.recipes
    if args.all:
        names = [r for r in egs3.recipes()
                 if egs3.derive(r)["recipe_kind"] != "multi_corpus"]
    OUT.mkdir(exist_ok=True)
    for r in names:
        res = measure(r)
        if res is None:
            print(f"SKIP {r}: output not built on this machine")
            continue
        (OUT / f"{r}.json").write_text(
            json.dumps(res, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{r}: n_total={res['n_total']} hours={res['hours_total']}", flush=True)


if __name__ == "__main__":
    main()
