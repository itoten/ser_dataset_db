"""Fill the automatic columns of data/recipes.csv from the espnet branch and measurements/.

Usage: python3 tools/sync.py
Creates a row for every egs3 recipe that has none; hand-written columns are never touched.
Recipes whose output was not built have NA in every measured column.
"""

import json

import csvio
import db as dbmod
import egs3

MEASURED = [
    "token_list", "n_train", "n_valid", "n_test", "n_test2", "n_train_filtered",
    "n_valid_filtered", "n_total", "hours_total", "dur_min_sec", "dur_max_sec",
    "dur_median_sec", "audio_format", "measured_on", "measurement_file",
]


def measured(recipe):
    path = csvio.ROOT / "measurements" / f"{recipe}.json"
    if not path.is_file():
        return {c: "NA" for c in MEASURED}
    m = json.loads(path.read_text(encoding="utf-8"))
    sp = m["splits"]

    def n(split, key="n"):
        v = sp.get(split, {}).get(key)
        return "NA" if v is None else str(v)

    return {
        "token_list": ";".join(t for t in m["token_list"] if t != "<unk>"),
        "n_train": n("train"), "n_valid": n("valid"), "n_test": n("test"), "n_test2": n("test2"),
        "n_train_filtered": n("train", "n_filtered"), "n_valid_filtered": n("valid", "n_filtered"),
        "n_total": str(m["n_total"]), "hours_total": str(m["hours_total"]),
        "dur_min_sec": str(m["duration_sec"]["min"]), "dur_max_sec": str(m["duration_sec"]["max"]),
        "dur_median_sec": str(m["duration_sec"]["median"]),
        "audio_format": ";".join(f"{k}:{v}" for k, v in sorted(m["audio_format"].items())),
        "measured_on": m["measured_on"], "measurement_file": f"measurements/{recipe}.json",
    }


def membership(recipe):
    """benchmark_membership rows implied by a multi-corpus recipe's dataset/config.yaml."""
    b = egs3.load_yaml(f"egs3/{recipe}/cls/dataset/config.yaml")["builder"]
    ref = f"egs3/{recipe}/cls/dataset/config.yaml"
    full = "eval_sets" in b
    out = []

    def row(member, role, splits, names, set_name, note=""):
        out.append({
            "benchmark_recipe": recipe, "member_recipe": member, "role": role,
            "splits_used": ";".join(splits), "eval_set_names": ";".join(names) or "NA",
            "set_name": set_name, "source_ref": ref, "note": note,
        })

    for c in b["train_corpora"]:
        n = c["data_src"].split("/")[0]
        if full:
            row(n, "train", ["train", "valid", "test"], [], "Open License set")
        else:
            row(n, "train", ["train", "valid"], [], "Open License set")
            row(n, "eval", ["test"], [n], "NA", "own test split of a training corpus")
    for c in b.get("eval_only_corpora", []):
        n = c["data_src"].split("/")[0]
        row(n, "eval", c["splits"], [f"{n}_{s}" for s in c["splits"]], "NA")
    for c in b.get("eval_sets", []):
        n = c["data_src"].split("/")[0]
        if n == "msppodcast":
            continue
        row(n, "eval", c["splits"], [c["name"]], "Non-Commercial set")
    msp = [c for c in b.get("eval_sets", []) if c["data_src"].startswith("msppodcast/")]
    if msp:
        row("msppodcast", "eval", [c["splits"][0] for c in msp], [c["name"] for c in msp], "NA")
    return out


def main():
    db = dbmod.load()
    header, rows = db["recipes"]
    have = {r["recipe"]: r for r in rows}
    for name in egs3.recipes():
        row = have.get(name)
        if row is None:
            row = {c: "" for c in header}
            rows.append(row)
        d = egs3.derive(name)
        for c in ["recipe"] + egs3.SYNC_COLUMNS:
            row[c] = d[c]
        row.update(measured(name))
    bm_header, bm_rows = db["benchmark_membership"]
    bm_rows[:] = [r for rec in egs3.recipes() if egs3.derive(rec)["recipe_kind"] == "multi_corpus"
                  for r in membership(rec)]
    for r in bm_rows:
        r.update({c: r.get(c, "") for c in bm_header})
    dbmod.save(db)


if __name__ == "__main__":
    main()
