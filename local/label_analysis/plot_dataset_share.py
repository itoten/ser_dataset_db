"""How much of each core label comes from which dataset (dataset bias).

Usage: <python with matplotlib> local/label_analysis/plot_dataset_share.py multidataset_ser_01 [open]
With `open`, only datasets of the open license group (not share-alike, nc or other) are counted.
Reads output/<config>/dataset_labels.csv (made by analyze.py); writes dataset_share[_open].png,
dataset_share[_open].csv (per label: top datasets, shares, effective number of datasets) in the same folder.
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
from plot_license_by_label import license_group  # noqa: E402
CORE = ["neutral", "happiness", "anger", "sadness", "surprise", "fear", "disgust"]
ALL = "all 7 labels"
NAMED = 9  # datasets that get their own colour; the rest are grouped
PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860", "#DA8BC3", "#8C8C3C", "#17BECF",
           "#1F3A5F", "#9C4A1A", "#2E7D32", "#7B1E3A", "#B39DDB", "#F2C14E", "#5F6B73"]


def load_raw_licenses():
    with open(HERE.parent.parent / "views" / "datasets_wide.csv", encoding="utf-8", newline="") as f:
        return {r["dataset_id"]: r["license_spdx"] for r in csv.DictReader(f)}


def load_licenses():
    """{dataset_id: license_spdx without the LicenseRef- prefix} from views/datasets_wide.csv."""
    with open(HERE.parent.parent / "views" / "datasets_wide.csv", encoding="utf-8", newline="") as f:
        return {r["dataset_id"]: r["license_spdx"].replace("LicenseRef-", "") for r in csv.DictReader(f)}


def load(config, only_group=None):
    """{label: {dataset: [files, hours]}} for the core labels, plus the ALL row."""
    data = defaultdict(lambda: defaultdict(lambda: [0, 0.0]))
    raw = load_raw_licenses()
    with open(HERE / "output" / config / "dataset_labels.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["label"] in CORE and (only_group is None or license_group(raw[r["dataset_id"]], r["dataset_id"]) == only_group):
                for lab in (r["label"], ALL):
                    data[lab][r["dataset_id"]][0] += int(r["n_files"])
                    data[lab][r["dataset_id"]][1] += float(r["hours"])
    return data


def effective_number(values):
    """1 / sum(share^2): how many equally large datasets would give the same concentration."""
    total = sum(values)
    return 1 / sum((v / total) ** 2 for v in values)


def shared_colors(config, data):
    """Datasets named in this figure and one colour per dataset that is the same in every figure.

    A dataset is named if it is among the NAMED largest (by samples) of the whole pool or of the open pool."""
    ranked = {}
    for group in (None, "open"):
        d = load(config, group)[ALL]
        for name, _ in sorted(d.items(), key=lambda x: -x[1][0])[:NAMED]:
            ranked[name] = None
    full = load(config)[ALL]
    order = sorted(ranked, key=lambda n: -full[n][0])
    colors = dict(zip(order, PALETTE))
    return [n for n in order if n in data[ALL]], colors


def main(config, only_group=None):
    data = load(config, only_group)
    suffix = f"_{only_group}" if only_group else ""
    out = HERE / "output" / config
    named, colors = shared_colors(config, data)
    licenses = load_licenses()
    labels = [ALL] + CORE
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(15, 5.2), gridspec_kw={"wspace": 0.06})
    rows = []
    for ax, (idx, title) in zip(axes, [(0, "Share of samples (%)"), (1, "Share of hours (%)")]):
        left = [0.0] * len(labels)
        for d in named + [None]:
            vals = []
            for lab in labels:
                total = sum(v[idx] for v in data[lab].values())
                part = data[lab][d][idx] if d else total - sum(data[lab][n][idx] for n in named if n in data[lab])
                vals.append(100 * part / total)
            ax.barh(range(len(labels)), vals, left=left, height=0.7, color=colors.get(d, "#BBBBBB"),
                    label=f"{d} ({licenses[d]})" if d else "other datasets")
            for y, l, v in zip(range(len(labels)), left, vals):
                if v >= 7:
                    ax.text(l + v / 2, y, f"{v:.0f}", ha="center", va="center", fontsize=8, color="white" if d else "black")
            left = [l + v for l, v in zip(left, vals)]
        ax.set_title(title, fontsize=10)
        ax.set_xlim(0, 100)
        ax.grid(axis="x", alpha=0.3)
    axes[0].set_yticks(range(len(labels)))
    axes[0].set_yticklabels(labels)
    axes[0].set_ylim(len(labels) - 0.5, -0.5)
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, loc="lower center", ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.16))
    fig.suptitle(f"Which datasets the samples and hours of each label come from ({config}{', open license only' if only_group else ''}; coloured datasets are the "
                 f"{NAMED} largest by samples in either pool, same colour in every figure; grey = the rest)", fontsize=10)
    fig.savefig(out / f"dataset_share{suffix}.png", dpi=150, bbox_inches="tight")

    with open(out / f"dataset_share{suffix}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["label", "n_datasets", "top1", "top1_share_files", "top3_share_files", "effective_n_files",
                    "top1_hours", "top1_share_hours", "effective_n_hours"])
        for lab in labels:
            files = {d: v[0] for d, v in data[lab].items()}
            hours = {d: v[1] for d, v in data[lab].items()}
            top = sorted(files, key=files.get, reverse=True)
            toph = max(hours, key=hours.get)
            w.writerow([lab, len(files), top[0], f"{files[top[0]] / sum(files.values()):.3f}",
                        f"{sum(files[d] for d in top[:3]) / sum(files.values()):.3f}",
                        f"{effective_number(list(files.values())):.1f}", toph,
                        f"{hours[toph] / sum(hours.values()):.3f}", f"{effective_number(list(hours.values())):.1f}"])
    print(out / f"dataset_share{suffix}.png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
