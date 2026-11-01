"""Generate views/datasets_wide.csv and views/discrepancies.csv from data/.

Usage: python3 tools/views.py      (rewrite both files)
validate.py regenerates them in memory and fails if the files on disk differ.
"""

import sys

import csvio
import db as dbmod

EXTRA_COLS = ["annotation_items", "license_checked_on", "license_source_type", "license_checked_by",
              "access_checked_on", "oldest_checked_on", "latest_checked_on"]
DISC_COLS = ["dataset_id", "field", "kind", "datasets_value", "datasets_source_type", "other_value",
             "other_source_type", "other_source_ref", "note"]
DISC_KEYS = ("dataset_id", "field", "kind", "other_value", "other_source_ref")


def semi(v):
    return v.replace(";", ", ")


def wide(db):
    items = {}
    for a in db["annotations"][1]:
        items.setdefault(a["dataset_id"], []).append(a["item"])
    canon = {}
    for e in db["evidence"][1]:
        if e["is_canonical"] == "true":
            canon.setdefault(e["dataset_id"], {})[e["field"]] = e
    out = []
    for d in db["datasets"][1]:
        i = d["dataset_id"]
        ce = canon.get(i, {})
        lic, acc = ce.get("license_spdx"), ce.get("access_method")
        dates = sorted(e["checked_on"] for e in ce.values())
        row = dict(d)
        row.update({
            "annotation_items": ";".join(sorted(items.get(i, []))),
            "license_checked_on": lic["checked_on"] if lic else "", "license_source_type": lic["source_type"] if lic else "",
            "license_checked_by": lic["checked_by"] if lic else "", "access_checked_on": acc["checked_on"] if acc else "",
            "oldest_checked_on": dates[0] if dates else "", "latest_checked_on": dates[-1] if dates else "",
        })
        out.append(row)
    return out


def discrepancies(db):
    ev = db["evidence"][1]
    ds = {d["dataset_id"]: d for d in db["datasets"][1]}
    canon = {(e["dataset_id"], e["field"]): e for e in ev if e["is_canonical"] == "true"}
    out = []
    for e in ev:
        if e["is_canonical"] == "true":
            continue
        c = canon.get((e["dataset_id"], e["field"]))
        if c is None:
            continue
        if e["value"] in (c["value"], "unknown"):
            continue
        out.append({"dataset_id": e["dataset_id"], "field": e["field"], "kind": e["status"],
                    "datasets_value": c["value"], "datasets_source_type": c["source_type"], "other_value": e["value"],
                    "other_source_type": e["source_type"], "other_source_ref": e["source_ref"], "note": e["note"]})
    pairs = [("n_speakers_reported", "n_speakers_measured", "reported_vs_release_measured"),
             ("n_utt_reported", "n_files_release_measured", "reported_vs_release_measured")]
    for i, d in ds.items():
        for a, b, kind in pairs:
            if d[a].isdigit() and d[b].isdigit() and d[a] != d[b]:
                out.append({"dataset_id": i, "field": f"{a} vs {b}", "kind": kind, "datasets_value": d[a],
                            "datasets_source_type": "see evidence", "other_value": d[b], "other_source_type": "measured",
                            "other_source_ref": b, "note": ""})
    return out


def build(db):
    """Return {relative path: canonical file text}."""
    return {
        "views/datasets_wide.csv": csvio.format_rows(db["datasets"][0] + EXTRA_COLS, wide(db), ("dataset_id",)),
        "views/discrepancies.csv": csvio.format_rows(DISC_COLS, discrepancies(db), DISC_KEYS),
    }


def main():
    for path, text in build(dbmod.load()).items():
        (csvio.ROOT / path).write_bytes(text.encode("utf-8"))
        print("wrote", path, text.count("\n") - 1, "rows")


if __name__ == "__main__":
    main()
