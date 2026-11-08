"""How much of each core label comes from which language (language bias), in the style of plot_dataset_share.py.

Usage: <python with matplotlib> local/label_analysis/plot_language.py multidataset_ser_01 [open]
A dataset with several languages counts as "multilingual"; one with no language in the DB as "not in DB".
Reads output/<config>/dataset_labels.csv; writes language[_open].png and .csv (shares per label).
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plot_dataset_share import ALL, CORE, NAMED, PALETTE  # noqa: E402
from plot_license_by_label import license_group  # noqa: E402

NOT_IN_DB = "not in DB"
NAMES = {"eng": "English", "rus": "Russian", "cmn": "Mandarin Chinese", "ben": "Bengali", "tha": "Thai", "isl": "Icelandic",
         "ory": "Odia", "zxx": "no linguistic content", "que": "Quechua", "ita": "Italian", "kaz": "Kazakh", "deu": "German",
         "spa": "Spanish", "fra": "French", "ind": "Indonesian", "pol": "Polish", "fas": "Persian", "jpn": "Japanese",
         "tur": "Turkish", "ara": "Arabic", "jav": "Javanese", "skr": "Saraiki", "ukr": "Ukrainian", "est": "Estonian",
         "mar": "Marathi", "ell": "Greek", "kan": "Kannada", "tel": "Telugu", "sqi": "Albanian", "por": "Portuguese"}
# PROVISIONAL, for this analysis only (not written to the DB, no source checked yet): languages the DB leaves empty.
PROVISIONAL = {"msppodcast": "eng", "meld": "eng", "cremad": "eng", "legov2": "eng", "enterface05": "eng", "mesd": "spa"}


def language_of(row):
    langs = [x for x in row["languages"].split(";") if x] or ([PROVISIONAL[row["dataset_id"]]] if row["dataset_id"] in PROVISIONAL else [])
    return langs[0] if len(langs) == 1 else ("multilingual" if langs else NOT_IN_DB)


def load(config, only_group=None):
    """{label: {language: [files, hours]}} for the core labels, plus the ALL row."""
    wide = {r["dataset_id"]: r for r in csv.DictReader(open(HERE.parent.parent / "views/datasets_wide.csv", encoding="utf-8"))}
    data = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
    for r in csv.DictReader(open(HERE / "output" / config / "dataset_labels.csv", encoding="utf-8")):
        w = wide[r["dataset_id"]]
        if r["label"] in CORE and (only_group is None or license_group(w["license_spdx"], r["dataset_id"]) == only_group):
            for lab in (r["label"], ALL):
                data[lab][language_of(w)][0] += int(r["n_files"])
                data[lab][language_of(w)][1] += float(r["hours"])
    return data


def main(config, only_group=None):
    data = load(config, only_group)
    suffix = f"_{only_group}" if only_group else ""
    ranked = {}
    for group in (None, "open"):
        d = load(config, group)[ALL]
        for name, _ in sorted(d.items(), key=lambda x: -x[1][0])[:NAMED]:
            ranked[name] = None
    full = load(config)[ALL]
    order = sorted(ranked, key=lambda n: -full[n][0])
    colors = dict(zip(order, PALETTE))
    colors[NOT_IN_DB] = "#E4E4E4"
    named = [n for n in order if n in data[ALL]]
    labels = [ALL] + CORE
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(15, 5.2), gridspec_kw={"wspace": 0.06})
    rows = []
    for ax, (idx, title) in zip(axes, [(0, "Share of samples (%)"), (1, "Share of hours (%)")]):
        left = [0.0] * len(labels)
        for lang in named + [None]:
            vals = []
            for lab in labels:
                total = sum(v[idx] for v in data[lab].values())
                part = data[lab][lang][idx] if lang else total - sum(data[lab][n][idx] for n in named if n in data[lab])
                vals.append(100 * part / total)
            ax.barh(range(len(labels)), vals, left=left, height=0.7, color=colors.get(lang, "#BBBBBB"),
                    hatch="//" if lang == NOT_IN_DB else None, edgecolor="white" if lang == NOT_IN_DB else None,
                    label=NAMES.get(lang, lang) if lang else "other languages")
            for y, l, v in zip(range(len(labels)), left, vals):
                if v >= 7:
                    ax.text(l + v / 2, y, f"{v:.0f}", ha="center", va="center", fontsize=8,
                            color="white" if lang and lang != NOT_IN_DB else "black")
            if idx == 0:
                rows += [[lab, lang or "other", round(v, 1)] for lab, v in zip(labels, vals)]
            left = [l + v for l, v in zip(left, vals)]
        ax.set_title(title, fontsize=10)
        ax.set_xlim(0, 100)
        ax.grid(axis="x", alpha=0.3)
    axes[0].set_yticks(range(len(labels)))
    axes[0].set_yticklabels(labels)
    axes[0].set_ylim(len(labels) - 0.5, -0.5)
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=6, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.08))
    fig.suptitle(f"Which languages the samples and hours of each label come from ({config}{', open license only' if only_group else ''}; "
                 f"multilingual = datasets with 2+ languages; grey = the rest)\n"
                 "Provisional (no language in the DB): English for MSP-Podcast, MELD, CREMA-D, LEGOv2, eNTERFACE05; Spanish for MESD", fontsize=10, y=1.06)
    out = HERE / "output" / config
    fig.savefig(out / f"language{suffix}.png", dpi=150, bbox_inches="tight")
    with open(out / f"language{suffix}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["label", "language", "share_samples_percent"])
        w.writerows(rows)
    print(out / f"language{suffix}.png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
