"""Recompute the figures quoted in docs/manual.md from data/*.csv and rewrite them.
The Japanese translation docs/manual.ja.md is rewritten with the same figures (its table rows
are matched by the same rules) and checked against the English manual by number (PARITY lines).

    python3 <skill dir>/scripts/doc_counts.py            # dry run: print each change
    python3 <skill dir>/scripts/doc_counts.py --write    # apply the changes

Each rule matches one table row of section 1.2 or 14 by its label. A rule whose label is not
found is reported as MISSING and the script exits with status 1: the row was reworded, so update
the rule (or the document) instead of leaving a stale number behind.
"""

import argparse
import collections
import csv
import re
import sys
from datetime import date
from pathlib import Path


def _find_root():
    for p in Path(__file__).resolve().parents:
        if (p / "tools" / "validate.py").is_file() and (p / "data" / "datasets.csv").is_file():
            return p
    raise SystemExit("doc_counts: could not find the DB root (a parent with tools/validate.py)")


ROOT = _find_root()


def load(path):
    with open(ROOT / path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def n(v):
    return f"{v:,}"


def stats():
    ev = load("data/evidence.csv")
    src = load("data/sources.csv")
    wide = load("views/datasets_wide.csv")
    return {
        "datasets": len(wide),
        "documents": sum(w["documents_checked"] == "true" for w in wide),
        "implementation": sum(w["implementation_checked"] == "true" for w in wide),
        "evidence": len(ev), "ev": collections.Counter(e["status"] for e in ev),
        "sources": len(src), "ty": collections.Counter(s["source_type"] for s in src),
        "label_counts": len(load("data/label_counts.csv")), "issues": len(load("data/issues.csv")),
        "annotations": len(load("data/annotations.csv")), "links": len(load("data/dataset_sources.csv")),
    }


def rules(s):
    """(English label, Japanese label, value) of each table row; the value is the second cell."""
    return [
        ("Datasets registered", "登録データセット数", n(s["datasets"])),
        ("Datasets with a primary source behind their values (`documents_checked`)", "値の裏づけに一次資料があるデータセット(`documents_checked`)", n(s["documents"])),
        ("Datasets with a recipe readme behind their release counts (`implementation_checked`)", "リリースの数の裏づけに recipe の readme があるデータセット(`implementation_checked`)", n(s["implementation"])),
        ("Evidence rows (sources of values)", "根拠の行数", n(s["evidence"])),
        ("Source documents", "出典の文書", n(s["sources"])),
        ("Label counts (files per label)", "ラベルごとの本数", n(s["label_counts"])),
        ("Issues found in releases", "リリースで見つかった問題", n(s["issues"])),
        ("Datasets", "データセット", n(s["datasets"])),
        ("Evidence rows: current", "根拠の行: current", n(s["ev"]["current"])),
        ("Evidence rows: conflicting", "根拠の行: conflicting", n(s["ev"]["conflicting"])),
        ("Evidence rows: provisional", "根拠の行: provisional", n(s["ev"]["provisional"])),
        ("Evidence rows: superseded", "根拠の行: superseded", n(s["ev"]["superseded"])),
        ("Sources: primary", "出典: primary", n(s["ty"]["primary"])),
        ("Sources: implementation", "出典: implementation", n(s["ty"]["implementation"])),
        ("Sources: secondary", "出典: secondary", n(s["ty"]["secondary"])),
        ("Sources without a checked publisher", "公開元をまだ確かめていない出典", n(s["ty"][""])),
        ("Annotation rows", "アノテーションの行", n(s["annotations"])),
        ("Dataset sources links", "データセットと出典の結び付き", n(s["links"])),
    ]


def numbers(chunk):
    """Numbers of two or more digits."""
    chunk = re.sub(r"\]\([^)]*\)", "]", chunk)
    chunk = re.sub(r"`[^`]*`", "", chunk)
    chunk = re.sub(r"\((?:see )?\d+(?:\.\d+)*\)", "", chunk)
    return sorted(x for x in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", chunk) if len(x.replace(",", "")) >= 2)


def sections(text):
    out, key, buf = {}, "top", []
    for line in text.splitlines():
        m = re.match(r"#{2,3} (\d+(?:\.\d+)*)\.? ", line)
        if m:
            out[key] = "\n".join(buf)
            key, buf = m.group(1), []
        else:
            buf.append(line)
    out[key] = "\n".join(buf)
    return out


def parity(en, ja):
    """Sections of the Japanese manual whose numbers differ from the English manual."""
    a, b = sections(en), sections(ja)
    return [k for k in sorted(set(a) | set(b), key=lambda k: [int(x) for x in k.split(".")] if k != "top" else [])
            if k not in a or k not in b or numbers(a[k]) != numbers(b[k])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args()
    s = stats()
    texts = {p: (ROOT / p).read_text(encoding="utf-8") for p in ["docs/manual.md", "docs/manual.ja.md"]}
    missing = 0
    for en_label, ja_label, value in rules(s):
        for path, label in (("docs/manual.md", en_label), ("docs/manual.ja.md", ja_label)):
            pat = r"^(\| " + re.escape(label) + r" \| )[\d,]+( \|)$"
            if not re.search(pat, texts[path], re.M):
                print(f"MISSING  {path}: {label}")
                missing += 1
                continue
            texts[path] = re.sub(pat, lambda m: m.group(1) + value + m.group(2), texts[path], flags=re.M)
    for path in texts:
        texts[path] = re.sub(r"(Current figures \(|現在の数値\()\d{4}-\d{2}-\d{2}", lambda m: m.group(1) + a.today, texts[path])
    for k in parity(texts["docs/manual.md"], texts["docs/manual.ja.md"]):
        print(f"PARITY   section {k}: numbers differ between the English and Japanese manuals")
    if a.write:
        for p, t in texts.items():
            (ROOT / p).write_text(t, encoding="utf-8")
        print("written")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
