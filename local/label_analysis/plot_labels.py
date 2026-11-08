"""Horizontal bar charts of every emotion label: files, hours and datasets.

Usage: <python with matplotlib> local/label_analysis/plot_labels.py multidataset_ser_01
Reads output/<config>/label_summary.csv (made by analyze.py); writes labels.pdf (A4 pages), labels.png and labels_wide.png (landscape).
"""
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).resolve().parent
LABELS_PER_PAGE = 48
PANELS = [("n_files", "Samples (files)", "#4C72B0"),
          ("hours", "Hours", "#55A868"),
          ("n_datasets", "Datasets", "#C44E52")]


def load_summary(config):
    with open(HERE / "output" / config / "label_summary.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["n_files"], r["hours"], r["n_datasets"] = int(r["n_files"]), float(r["hours"]), int(r["n_datasets"])
    return sorted(rows, key=lambda r: (-r["n_files"], r["label"]))


def draw_page(rows, title, size):
    fig, axes = plt.subplots(1, 3, sharey=True, figsize=size, gridspec_kw={"wspace": 0.08, "left": 0.2, "right": 0.97, "top": 0.94, "bottom": 0.04})
    ys = range(len(rows))
    for ax, (key, name, color) in zip(axes, PANELS):
        values = [r[key] for r in rows]
        ax.barh(ys, values, color=color, height=0.75)
        for y, v in zip(ys, values):
            ax.text(v, y, f" {v:,.0f}" if key != "hours" else f" {v:,.1f}", va="center", fontsize=6)
        ax.set_title(name, fontsize=9)
        ax.set_xlim(0, max(values) * 1.35 if values else 1)
        ax.tick_params(axis="x", labelsize=6)
        ax.grid(axis="x", alpha=0.3)
    axes[0].set_yticks(list(ys))
    axes[0].set_yticklabels([r["label"] for r in rows], fontsize=7)
    axes[0].set_ylim(len(rows) - 0.5, -0.5)  # first label on top, no empty margin
    fig.suptitle(title, fontsize=10)
    return fig


def draw_wide(rows, title):
    """Landscape version: one column per label, the three metrics stacked."""
    n = len(rows)
    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(max(14, 0.32 * n), 11),
                             gridspec_kw={"hspace": 0.08, "left": 0.05, "right": 0.99, "top": 0.95, "bottom": 0.22})
    xs = range(n)
    for ax, (key, name, color) in zip(axes, PANELS):
        values = [r[key] for r in rows]
        ax.bar(xs, values, color=color, width=0.75)
        for x, v in zip(xs, values):
            ax.text(x, v, f"{v:,.0f}" if key != "hours" else f"{v:,.1f}", ha="center", va="bottom", fontsize=5, rotation=90)
        ax.set_ylabel(name, fontsize=9)
        ax.set_ylim(0, max(values) * 1.18 if values else 1)
        ax.tick_params(axis="y", labelsize=7)
        ax.grid(axis="y", alpha=0.3)
    axes[-1].set_xticks(list(xs))
    axes[-1].set_xticklabels([r["label"] for r in rows], rotation=60, ha="right", fontsize=7)
    axes[-1].set_xlim(-0.7, n - 0.3)
    fig.suptitle(title, fontsize=11)
    return fig


def main(config):
    rows = load_summary(config)
    pages = [rows[i:i + LABELS_PER_PAGE] for i in range(0, len(rows), LABELS_PER_PAGE)]
    out = HERE / "output" / config
    with PdfPages(out / "labels.pdf") as pdf:
        for i, page in enumerate(pages, 1):
            title = f"Emotion labels of {config} ({len(rows)} labels, sorted by samples) page {i}/{len(pages)}"
            fig = draw_page(page, title, (8.27, 11.69))
            pdf.savefig(fig)
            plt.close(fig)
    fig = draw_page(rows, f"Emotion labels of {config} ({len(rows)} labels, sorted by samples)", (11, 0.2 * len(rows) + 1.5))
    fig.savefig(out / "labels.png", dpi=110)
    fig = draw_wide(rows, f"Emotion labels of {config} ({len(rows)} labels, sorted by samples)")
    fig.savefig(out / "labels_wide.png", dpi=110)
    print(f"{len(rows)} labels, {len(pages)} pages -> {out}")


if __name__ == "__main__":
    main(sys.argv[1])
