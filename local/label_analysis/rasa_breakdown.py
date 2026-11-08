"""RASA's six emotion styles by language and speaker gender (samples and hours).

Usage: <python with matplotlib, soundfile> local/label_analysis/rasa_breakdown.py
Reads the recipe's manifest ($RASA_MANIFEST, default: data/rasa_espnet3/manifest in the home folder; ids look like rasa-ASM_F_ANGER_00001).
Writes output/rasa/rasa_by_language.csv and rasa_by_language.png.
"""
import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import soundfile as sf

HERE = Path(__file__).resolve().parent
MANIFEST = Path(os.environ.get("RASA_MANIFEST", Path.home() / "data/rasa_espnet3/manifest"))
EMOTIONS = ["happy", "anger", "fear", "surprise", "disgust", "sad"]
COLORS = ["#E3B23C", "#C44E52", "#8172B2", "#4C9FB5", "#55A868", "#4C72B0"]


def main():
    n = defaultdict(int)
    hours = defaultdict(float)
    for split in ("train", "valid", "test"):
        for utt, path, label in csv.reader(open(MANIFEST / f"{split}.tsv", encoding="utf-8"), delimiter="\t"):
            if label not in EMOTIONS:
                continue
            lang, gender = utt.split("-", 1)[1].split("_")[:2]
            key = (lang, gender, label)
            n[key] += 1
            hours[key] += sf.info(path).duration / 3600
    out = HERE / "output/rasa"
    out.mkdir(parents=True, exist_ok=True)
    langs = sorted({k[0] for k in n}, key=lambda l: -sum(v for k, v in n.items() if k[0] == l))
    with open(out / "rasa_by_language.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["language", "gender", "label", "n_files", "hours"])
        for k in sorted(n):
            w.writerow([*k, n[k], round(hours[k], 3)])
    fig, axes = plt.subplots(2, 1, figsize=(12, 9), gridspec_kw={"hspace": 0.35})
    # top: samples per language, stacked by emotion
    bottom = [0] * len(langs)
    for emo, c in zip(EMOTIONS, COLORS):
        vals = [sum(n[(l, g, emo)] for g in "FM") for l in langs]
        axes[0].bar(langs, vals, bottom=bottom, color=c, label=emo)
        bottom = [b + v for b, v in zip(bottom, vals)]
    axes[0].set_title("Emotion samples per language (RASA, six emotion styles)", fontsize=10)
    axes[0].legend(ncol=6, fontsize=8)
    # bottom: hours per language, female vs male
    xs = range(len(langs))
    for off, g, c, name in ((-0.2, "F", "#C44E52", "female"), (0.2, "M", "#4C72B0", "male")):
        vals = [sum(hours[(l, g, e)] for e in EMOTIONS) for l in langs]
        axes[1].bar([x + off for x in xs], vals, width=0.4, color=c, label=name)
    axes[1].set_xticks(list(xs))
    axes[1].set_xticklabels(langs)
    axes[1].set_title("Emotion hours per language by speaker gender", fontsize=10)
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(axis="y", alpha=0.3)
    fig.savefig(out / "rasa_by_language.png", dpi=110, bbox_inches="tight")
    tot = sum(n.values())
    for g in "FM":
        print(g, sum(v for k, v in n.items() if k[1] == g), round(sum(v for k, v in hours.items() if k[1] == g), 1))
    print("total", tot, round(sum(hours.values()), 1), len(langs), "languages")
    for l in langs:
        print(l, sum(v for k, v in n.items() if k[0] == l), round(sum(v for k, v in hours.items() if k[0] == l), 1))


if __name__ == "__main__":
    main()
