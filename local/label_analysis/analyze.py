"""Which emotion labels the datasets left by a dataset_filtering config have, and how many files each.

Usage: python3 local/label_analysis/analyze.py multidataset_ser_01
Reads output/<config>/result.csv of dataset_filtering, data/label_counts.csv, data/annotations.csv and
data/label_normalization.csv of the DB. Writes output/<config>/: dataset_labels.csv, label_summary.csv, summary.md.
Only labels that mean the same are merged: the DB's label_normalization.csv (spelling, word form), then
label_merge.csv here (abbreviations, translations, typos, index prefixes such as "01_angry", codes with a
documented meaning). Labels that differ in meaning (joy / happiness) stay separate: mapping them is a
project decision made later.
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_ROOT = HERE.parent.parent
FILTERING_OUTPUT = DB_ROOT / "local/dataset_filtering/output"
MIN_DATASETS_SHOWN = 3  # labels in fewer datasets are listed only in label_summary.csv


def load_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_kept_ids(config):
    result = load_csv(FILTERING_OUTPUT / config / "result.csv")
    return [r["dataset_id"] for r in result if r["status"] != "removed"]


def load_normalization():
    return {r["source_label"]: r["normalized"] for r in load_csv(DB_ROOT / "data/label_normalization.csv")}


def load_merge_rules():
    """(dataset_id or '*', label) -> merged label. A rule for one dataset wins over a rule for all ('*')."""
    return {(r["dataset_id"], r["label"]): r["merged_label"] for r in load_csv(HERE / "label_merge.csv")}


def merge(dataset_id, label, rules):
    label = rules.get((dataset_id, label)) or rules.get(("*", label)) or label
    return label


def strip_index_prefix(label):
    """'01_Angry' and '01 adoration' (a running number in front of the label) -> 'Angry', 'adoration'."""
    return re.sub(r"^\d{2}[ _](?=[A-Za-z])", "", label)


def normalize(label, table):
    """The DB's normalised form of the label, trying the exact spelling first, then the lower case."""
    for key in (label, label.strip().lower()):
        if key in table:
            return table[key]
    return label.strip().lower().replace(" ", "_")


def collect_dataset_labels(kept_ids, table, rules):
    """One row per (dataset, label): the files counted for the label, or none if the DB has no count."""
    counts = defaultdict(list)
    for r in load_csv(DB_ROOT / "data/label_counts.csv"):
        counts[r["dataset_id"]].append(r)
    annotations = {a["dataset_id"]: a for a in load_csv(DB_ROOT / "data/annotations.csv")
                   if a["item"] == "emotion_categories"}
    rows = []
    for d in kept_ids:
        listed = [x for x in annotations[d]["labels"].split(";") if x]
        counted = [r for r in counts[d] if r["item"] == "emotion_categories"]
        if counted:
            note = ""
        else:
            # the counts are under another label set (RASA: speaking_style); keep the rows naming an emotion label
            counted = [r for r in counts[d] if r["label"].lower() in {x.lower() for x in listed}]
            note = "counted under another label set" if counted else "no count in the DB"
        if counted:
            for r in counted:
                rows.append(label_row(d, r["label"], int(r["n"]), note, table, rules, r.get("hours", "")))
        else:
            rows += [label_row(d, x, "", note, table, rules, "") for x in listed]
    return rows


def label_row(dataset_id, source_label, n_files, note, table, rules, hours):
    db_label = normalize(strip_index_prefix(source_label), table)
    return {"dataset_id": dataset_id, "source_label": source_label, "db_label": db_label,
            "label": merge(dataset_id, db_label, rules), "n_files": n_files, "hours_measured": hours, "note": note}


def fill_hours(rows):
    """Sets r["hours"] and r["hours_basis"] (measured or estimated) for each (dataset, label).

    Measured: the hours of the label in label_counts.csv. A label without them gets an estimate: the
    hours of the dataset (hours_release) not covered by measured labels, split by the share of files
    (assumes equally long clips)."""
    release = {r["dataset_id"]: r["hours_release"] for r in load_csv(DB_ROOT / "views/datasets_wide.csv")}
    measured, rest_files = defaultdict(float), defaultdict(int)
    for r in rows:
        if r["hours_measured"] != "":
            measured[r["dataset_id"]] += float(r["hours_measured"])
        else:
            rest_files[r["dataset_id"]] += r["n_files"] or 0
    for r in rows:
        d = r["dataset_id"]
        if r["hours_measured"] != "":
            r["hours"], r["hours_basis"] = float(r["hours_measured"]), "measured"
        else:
            h = release[d]
            left = max(float(h) - measured[d], 0.0) if h else 0.0
            r["hours"] = left * (r["n_files"] or 0) / rest_files[d] if rest_files[d] else 0.0
            r["hours_basis"] = "estimated"


def summarize_labels(rows):
    by_label = defaultdict(lambda: {"datasets": set(), "files": 0, "hours": 0.0, "spellings": set()})
    for r in rows:
        s = by_label[r["label"]]
        s["datasets"].add(r["dataset_id"])
        s["spellings"].add(r["source_label"])
        s["files"] += r["n_files"] or 0
        s["hours"] += r["hours"]
    out = [{"label": k, "n_datasets": len(v["datasets"]), "n_files": v["files"], "hours": round(v["hours"], 1),
            "source_spellings": ";".join(sorted(v["spellings"])), "datasets": ";".join(sorted(v["datasets"]))}
           for k, v in by_label.items()]
    return sorted(out, key=lambda x: (-x["n_datasets"], -x["n_files"], x["label"]))


def write_summary(path, config, kept_ids, rows, summary):
    uncounted = sorted({r["dataset_id"] for r in rows if r["note"] == "no count in the DB"})
    per_dataset = defaultdict(set)
    for r in rows:
        per_dataset[r["dataset_id"]].add(r["label"])
    lines = [f"# Emotion labels of the datasets left by {config}", "",
             "Generated by analyze.py. Do not edit. Labels that mean the same are merged (label_merge.csv); hours are measured where the DB has them (hours_basis).", "",
             f"- Datasets: {len(kept_ids)}; distinct labels: {len(summary)}; labels in one dataset only: "
             f"{sum(1 for s in summary if s['n_datasets'] == 1)}",
             f"- Files counted: {sum(r['n_files'] or 0 for r in rows)}",
             f"- Datasets with no file count in the DB (only their label list is used): {len(uncounted)}"
             + (f" ({', '.join(uncounted)})" if uncounted else ""), "",
             f"## Labels used by at least {MIN_DATASETS_SHOWN} datasets", "",
             "| label | datasets | files | hours | spellings in the sources |", "|---|---|---|---|---|"]
    lines += [f"| {s['label']} | {s['n_datasets']} | {s['n_files']} | {s['hours']} | {s['source_spellings']} |"
              for s in summary if s["n_datasets"] >= MIN_DATASETS_SHOWN]
    sizes = sorted(len(v) for v in per_dataset.values())
    lines += ["", "## Number of labels per dataset", "",
              f"min {sizes[0]}, median {sizes[len(sizes) // 2]}, max {sizes[-1]}", ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(config):
    kept_ids = load_kept_ids(config)
    rows = collect_dataset_labels(kept_ids, load_normalization(), load_merge_rules())
    fill_hours(rows)
    summary = summarize_labels(rows)
    out = FILTERING_OUTPUT.parent.parent / "label_analysis/output" / config
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "dataset_labels.csv", ["dataset_id", "source_label", "db_label", "label", "n_files", "hours", "hours_basis", "note"], rows)
    write_csv(out / "label_summary.csv", ["label", "n_datasets", "n_files", "hours", "source_spellings", "datasets"], summary)
    write_summary(out / "summary.md", config, kept_ids, rows, summary)
    print((out / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main(sys.argv[1])
