"""Stacked bars of the license group of each core label (share of samples, samples, hours).

Usage: <python with matplotlib> local/label_analysis/plot_license_by_label.py multidataset_ser_01
Reads output/<config>/dataset_labels.csv (made by analyze.py) and the license of each dataset from
views/datasets_wide.csv; writes license_by_label.png and license_by_label.csv in the same folder.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
DB = HERE.parent.parent
ALL = "all 7 labels"
CORE = ["neutral", "happiness", "anger", "sadness", "surprise", "fear", "disgust"]
SHARE_ALIKE = {"CC-BY-SA-4.0", "GPL-3.0-only", "GPL-3.0-or-later", "ODbL-1.0", "LicenseRef-golos-public"}
GROUPS = [("open", "Open (CC0/CC BY/MIT...)", "#55A868"),
          ("nc", "Non-commercial / research only / share-alike (evaluation only)", "#C44E52"),
          ("other", "Other terms (pending)", "#999999")]
NC = {"CC-BY-NC-3.0", "CC-BY-NC-4.0", "CC-BY-NC-ND-4.0", "CC-BY-NC-SA-2.0", "CC-BY-NC-SA-3.0-DE", "CC-BY-NC-SA-4.0",
      "LicenseRef-custom-research-only", "LicenseRef-proprietary-restricted"}


# DB license "conflicting": the group follows the DB's license_note (EmoDB: CC BY 4.0 on Zenodo, checked by the maintainer;
# NonverbalTTS: annotations CC BY-NC-SA and audio under NC sources; TurEV-DB: the stricter README terms, CC BY-NC-ND).
CONFLICTING_AS = {"emodb": "open", "nonverbaltts": "nc", "turevdb": "nc"}


def license_group(spdx, dataset_id=None):
    if spdx == "conflicting":
        return CONFLICTING_AS[dataset_id]
    if spdx in SHARE_ALIKE:
        return "nc"  # share-alike is used for evaluation only (meeting 2026-11-05), like NC
    if spdx in NC:
        return "nc"
    if spdx == "LicenseRef-other":
        return "other"
    return "open"


def load_licenses():
    with open(DB / "views" / "datasets_wide.csv", encoding="utf-8", newline="") as f:
        return {r["dataset_id"]: r["license_spdx"] for r in csv.DictReader(f)}




def draw(ax, labels, get, fmt, percent):
    """Stacked horizontal bars of the license groups for `labels`; numbers inside the segments."""
    ys = range(len(labels))
    left = [0.0] * len(labels)
    totals = [sum(get(g, lab) for g, _, _ in GROUPS) for lab in labels]
    scale = 100 if percent else max(totals)
    for g, name, color in GROUPS:
        vals = [get(g, lab) for lab in labels]
        if percent:
            vals = [100 * v / t for v, t in zip(vals, totals)]
        ax.barh(ys, vals, left=left, color=color, label=name, height=0.7)
        for y, l, v in zip(ys, left, vals):
            if v >= 0.035 * scale:
                ax.text(l + v / 2, y, f"{v:.0f}" if percent else fmt(v), ha="center", va="center", fontsize=8, color="white")
        left = [l + v for l, v in zip(left, vals)]
    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels)
    ax.set_ylim(len(labels) - 0.5, -0.5)
    ax.set_xlim(0, 100 if percent else max(totals) * 1.02)
    ax.grid(axis="x", alpha=0.3)


LABELS = [ALL] + CORE


def main(config):
    out = HERE / "output" / config
    licenses = load_licenses()
    tot = {g: defaultdict(lambda: [0, 0.0]) for g, _, _ in GROUPS}
    ids = {g: defaultdict(set) for g, _, _ in GROUPS}
    with open(out / "dataset_labels.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["label"] in CORE:
                g = license_group(licenses[r["dataset_id"]], r["dataset_id"])
                for lab in (r["label"], ALL):
                    ids[g][lab].add(r["dataset_id"])
                    t = tot[g][lab]
                    t[0] += int(r["n_files"])
                    t[1] += float(r["hours"])
    GROUPS[:] = [x for x in GROUPS if ids[x[0]]]  # drop a license group no kept dataset has
    with open(out / "license_by_label.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["label", "group", "n_datasets", "n_files", "hours"])
        for lab in LABELS:
            for g, _, _ in GROUPS:
                w.writerow([lab, g, len(ids[g][lab]), tot[g][lab][0], f"{tot[g][lab][1]:.1f}"])

    metrics = [("Samples (files)", lambda g, lab: tot[g][lab][0], lambda v: f"{v / 1000:.0f}k"),
               ("Hours", lambda g, lab: tot[g][lab][1], lambda v: f"{v:.0f}"),
               ("Datasets", lambda g, lab: len(ids[g][lab]), lambda v: f"{v:.0f}")]
    fig = plt.figure(figsize=(18, 11))
    grid = fig.add_gridspec(3, 3, height_ratios=[1, 7, 8.5], hspace=0.28, wspace=0.08)
    for col, (title, get, fmt) in enumerate(metrics):
        # absolute values: the "all 7 labels" row has its own axis so that it does not dwarf the labels
        for row, labels in enumerate([[ALL], CORE]):
            ax = fig.add_subplot(grid[row, col])
            draw(ax, labels, get, fmt, percent=False)
            if col == 0:
                ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x / 1000:.0f}k"))
            ax.set_title(title if row == 0 else "", fontsize=10)
            if col:
                ax.set_yticklabels([])
        ax = fig.add_subplot(grid[2, col])
        draw(ax, LABELS, get, fmt, percent=True)
        ax.set_title(f"Share of {title.split(' (')[0].lower()} (%)", fontsize=10)
        if col:
            ax.set_yticklabels([])
    fig.legend(*fig.axes[0].get_legend_handles_labels(), loc="lower center", ncol=4, fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.06))
    fig.suptitle(f"License group of the 7 core labels ({config})", fontsize=11, y=0.93)
    fig.savefig(out / "license_by_label.png", dpi=150, bbox_inches="tight")
    print(out / "license_by_label.png")


if __name__ == "__main__":
    main(sys.argv[1])
