"""Read the public DB tables that the local classifications use."""
import csv
from pathlib import Path

LOCAL = Path(__file__).resolve().parent
ROOT = LOCAL.parent


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def datasets():
    """dataset_id -> row of views/datasets_wide.csv (current values, derived columns included)."""
    return {r["dataset_id"]: r for r in rows(ROOT / "views/datasets_wide.csv")}


def annotations():
    return rows(ROOT / "data/annotations.csv")


def evidence():
    return rows(ROOT / "data/evidence.csv")


def write(path, header, records):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        w.writeheader()
        w.writerows(records)
