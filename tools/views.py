"""Generate views/datasets_wide.csv and views/discrepancies.csv from data/.

Usage: python3 tools/views.py      (rewrite both files)
validate.py regenerates them in memory and fails if the files on disk differ.
"""

import sys

import csvio
import db as dbmod

EXTRA_COLS = ["documents_checked", "implementation_checked", "paper_url", "distribution_url", "card_url", "mirror_url", "readme_url", "other_url",
              "annotation_items", "license_checked_on", "license_source_type", "license_checked_by",
              "access_checked_on", "oldest_checked_on", "latest_checked_on"]
DISC_COLS = ["dataset_id", "field", "kind", "datasets_value", "datasets_source_type", "other_value",
             "other_source_type", "other_source_ref", "note"]
DISC_KEYS = ("dataset_id", "field", "kind", "other_value", "other_source_ref")


def semi(v):
    return v.replace(";", ", ")


def src_url(sources, sid):
    r = sources.get(sid)
    return (r["url"] or r["source_id"]) if r else ""


def wide(db):
    sources = {r["source_id"]: r for r in db["sources"][1]}
    urls = {}
    for r in db["dataset_sources"][1]:
        urls.setdefault((r["dataset_id"], r["role"]), []).append(src_url(sources, r["source_id"]))
    stage = {}
    DOC_FIELDS = {"languages", "license_spdx", "speech_production", "label_basis", "emotion_categories.label_basis",
                  "emotion_categories.annotator", "n_files_reported", "access_method"}
    for e in db["evidence"][1]:
        if e["status"] not in ("current", "conflicting"):
            continue
        ty = sources.get(e["source_id"], {}).get("source_type", "")
        st = stage.setdefault(e["dataset_id"], set())
        if ty == "primary" and e["field"] in DOC_FIELDS:
            st.add("documents")
        if ty == "implementation":
            st.add("implementation")
    items = {}
    for a in db["annotations"][1]:
        items.setdefault(a["dataset_id"], []).append(a["item"])
    canon = {}
    for e in sorted(db["evidence"][1], key=lambda e: e["evidence_id"]):
        if e["status"] in ("current", "conflicting", "provisional"):
            canon.setdefault(e["dataset_id"], {})[e["field"]] = e
    out = []
    for d in db["datasets"][1]:
        i = d["dataset_id"]
        ce = canon.get(i, {})
        lic, acc = ce.get("license_spdx"), ce.get("access_method")
        dates = sorted(e["checked_on"] for e in ce.values())
        row = dict(d)
        row.update({
            "documents_checked": "true" if "documents" in stage.get(i, ()) else "false",
            "implementation_checked": "true" if "implementation" in stage.get(i, ()) else "false",
            **{f"{role}_url": ";".join(urls.get((i, role), [])) for role in ("paper", "distribution", "card", "mirror", "readme", "other")},
            "annotation_items": ";".join(sorted(items.get(i, []))),
            "license_checked_on": lic["checked_on"] if lic else "", "license_source_type": sources.get(lic["source_id"], {}).get("source_type", "") if lic else "",
            "license_checked_by": lic["checked_by"] if lic else "", "access_checked_on": acc["checked_on"] if acc else "",
            "oldest_checked_on": dates[0] if dates else "", "latest_checked_on": dates[-1] if dates else "",
        })
        out.append(row)
    return out


def discrepancies(db):
    sources = {r["source_id"]: r for r in db["sources"][1]}
    ds = {d["dataset_id"]: d for d in db["datasets"][1]}
    out = []
    for e in db["evidence"][1]:
        if e["status"] != "conflicting":
            continue
        out.append({"dataset_id": e["dataset_id"], "field": e["field"], "kind": "conflicting",
                    "datasets_value": "conflicting", "datasets_source_type": "see evidence",
                    "other_value": e["value"], "other_source_type": sources.get(e["source_id"], {}).get("source_type", ""),
                    "other_source_ref": src_url(sources, e["source_id"]), "note": e["note"]})
    pairs = [("n_speakers_reported", "n_speakers_release", "reported_vs_release"),
             ("n_files_reported", "n_files_release", "reported_vs_release")]
    for i, d in ds.items():
        for a, b, kind in pairs:
            if d[a].isdigit() and d[b].isdigit() and d[a] != d[b]:
                out.append({"dataset_id": i, "field": f"{a} vs {b}", "kind": kind, "datasets_value": d[a],
                            "datasets_source_type": "see evidence", "other_value": d[b], "other_source_type": "implementation",
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
