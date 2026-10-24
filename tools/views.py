"""Generate views/datasets_wide.csv and views/discrepancies.csv from data/.

Usage: python3 tools/views.py      (rewrite both files)
validate.py regenerates them in memory and fails if the files on disk differ.
"""

import sys

import csvio
import db as dbmod

SHEET_COLS = ["Verified", "Dataset", "License", "Language", "Source", "Total Hours", "Utterances", "Speakers",
              "Discrete Emotions", "Dimensional Emotions", "Other Annotations", "Source URL", "Notes", "Paper URL",
              "ESPnet Implemented"]
EXTRA_COLS = ["dataset_id", "status", "reasons", "license_class", "access_method", "raw_audio_available", "recipe",
              "n_total_recipe", "hours_total_recipe", "n_files_release_measured", "n_speakers_measured",
              "common7_covered", "common7_missing", "extra_labels", "label_source", "label_verification", "speech_production", "label_basis", "label_basis_note",
              "annotation_items",
              "benchmarks", "report_path", "status_note", "notes",
              "license_checked_on", "license_source_type", "license_checked_by", "access_checked_on",
              "oldest_checked_on", "latest_checked_on"]
DISC_COLS = ["dataset_id", "field", "kind", "datasets_value", "datasets_source_type", "other_value",
             "other_source_type", "other_source_ref", "note"]
COMMON7 = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
DISC_KEYS = ("dataset_id", "field", "kind", "other_value", "other_source_ref")


def semi(v):
    return v.replace(";", ", ")


def wide(db):
    recipes = db["recipes"][1]
    labels = db["recipe_labels"][1]
    members = db["benchmark_membership"][1]
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
        recs = sorted((r for r in recipes if r["dataset_id"] == i), key=lambda r: r["recipe"])
        names = [r["recipe"] for r in recs]
        covered, extra = set(), set()
        for lab in labels:
            if lab["recipe"] in names and lab["mapping_type"] != "dropped_by_recipe":
                if lab["common7"] in COMMON7:
                    covered.add(lab["common7"])
                else:
                    extra.add(lab["label"])
        bench = sorted({f"{m['benchmark_recipe']}:{m['role']}" for m in members if m["member_recipe"] in names})
        main = recs[0] if recs else None
        row = {
            "Verified": d["sheet_verified"], "Dataset": d["name"], "License": d["license_spdx"],
            "Language": semi(d["languages"]), "Source": d["recording_context"], "Total Hours": d["hours_reported"],
            "Utterances": d["n_utt_reported"], "Speakers": d["n_speakers_reported"],
            "Discrete Emotions": semi(d["labels_discrete_reported"]), "Dimensional Emotions": semi(d["dimensional_attributes"]),
            "Other Annotations": d["annotations_other"], "Source URL": d["source_url"], "Notes": d["sheet_notes"],
            "Paper URL": d["paper_url"], "ESPnet Implemented": "TRUE" if d["espnet_status"] == "implemented" else "FALSE",
            "dataset_id": i, "status": d["espnet_status"], "reasons": d["status_reason_codes"],
            "license_class": d["license_class"], "access_method": d["access_method"],
            "raw_audio_available": d["raw_audio_available"], "recipe": ";".join(names),
            "n_total_recipe": main["n_total"] if main else "", "hours_total_recipe": main["hours_total"] if main else "",
            "n_files_release_measured": d["n_files_release_measured"], "n_speakers_measured": d["n_speakers_measured"],
            "common7_covered": f"{len(covered)}/7" if names else "",
            "common7_missing": ";".join(c for c in COMMON7 if c not in covered) if names else "",
            "extra_labels": ";".join(sorted(extra)), "label_source": d["label_source"],
            "label_verification": d["label_verification"], "speech_production": d["speech_production"],
            "label_basis": d["label_basis"], "label_basis_note": d["label_basis_note"], "annotation_items": ";".join(sorted(items.get(i, []))),
            "benchmarks": ";".join(bench),
            "report_path": d["report_path"], "status_note": d["status_note"], "notes": d["notes"],
            "license_checked_on": lic["checked_on"] if lic else "", "license_source_type": lic["source_type"] if lic else "",
            "license_checked_by": lic["checked_by"] if lic else "", "access_checked_on": acc["checked_on"] if acc else "",
            "oldest_checked_on": dates[0] if dates else "", "latest_checked_on": dates[-1] if dates else "",
        }
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
        if e["source_ref"] == "tools/import_sheet.py" and e["field"] in ("espnet_status", "status_reason_codes"):
            continue
        if e["value"] in (c["value"], "unknown"):
            continue
        out.append({"dataset_id": e["dataset_id"], "field": e["field"], "kind": e["status"],
                    "datasets_value": c["value"], "datasets_source_type": c["source_type"], "other_value": e["value"],
                    "other_source_type": e["source_type"], "other_source_ref": e["source_ref"], "note": e["note"]})
    recipes = {r["dataset_id"]: r for r in db["recipes"][1] if r["recipe_kind"] == "single_corpus"}
    pairs = [("n_speakers_reported", "n_speakers_measured", "reported_vs_release_measured"),
             ("n_utt_reported", "n_files_release_measured", "reported_vs_release_measured")]
    for i, d in ds.items():
        for a, b, kind in pairs:
            if d[a].isdigit() and d[b].isdigit() and d[a] != d[b]:
                out.append({"dataset_id": i, "field": f"{a} vs {b}", "kind": kind, "datasets_value": d[a],
                            "datasets_source_type": "see evidence", "other_value": d[b], "other_source_type": "measured",
                            "other_source_ref": b, "note": ""})
        r = recipes.get(i)
        if r and d["n_utt_reported"].isdigit() and r["n_total"].isdigit() and d["n_utt_reported"] != r["n_total"]:
            out.append({"dataset_id": i, "field": "n_utt_reported vs recipe n_total", "kind": "reported_vs_recipe_measured",
                        "datasets_value": d["n_utt_reported"], "datasets_source_type": "see evidence",
                        "other_value": r["n_total"], "other_source_type": "measured",
                        "other_source_ref": f"recipes.n_total ({r['recipe']})",
                        "note": "a mismatch is normal: recipes filter by length and label"})
    return out


def build(db):
    """Return {relative path: canonical file text}."""
    return {
        "views/datasets_wide.csv": csvio.format_rows(SHEET_COLS + EXTRA_COLS, wide(db), ("dataset_id",)),
        "views/discrepancies.csv": csvio.format_rows(DISC_COLS, discrepancies(db), DISC_KEYS),
    }


def main():
    for path, text in build(dbmod.load()).items():
        (csvio.ROOT / path).write_bytes(text.encode("utf-8"))
        print("wrote", path, text.count("\n") - 1, "rows")


if __name__ == "__main__":
    main()
