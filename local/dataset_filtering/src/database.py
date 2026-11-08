"""Read-only access to the DB tables that the filters look at."""
import csv
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


def load_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@dataclass
class Dataset:
    """One dataset: its row of views/datasets_wide.csv and its rows of data/annotations.csv."""

    columns: dict
    annotations: list = field(default_factory=list)
    unknown_values: frozenset = frozenset({"", "unknown"})

    @property
    def id(self):
        return self.columns["dataset_id"]

    @property
    def name(self):
        return self.columns["name"]

    def value(self, column):
        return self.columns[column]

    def values(self, column):
        """The column split on ';' (the DB stores several values that way)."""
        return {v.strip() for v in self.columns[column].split(";")}

    def is_unknown(self, value):
        """True when the value means the DB does not say (set by `unknown_values` in the config)."""
        return value in self.unknown_values

    def annotation_items(self):
        return {a["item"] for a in self.annotations}


class DatasetDatabase:
    """The DB repository, loaded once."""

    def __init__(self, root, unknown_values):
        self.root = Path(root)
        annotations = {}
        for row in load_csv(self.root / "data/annotations.csv"):
            annotations.setdefault(row["dataset_id"], []).append(row)
        unknown = frozenset(unknown_values)
        self.datasets = [Dataset(row, annotations.get(row["dataset_id"], []), unknown)
                         for row in load_csv(self.root / "views/datasets_wide.csv")]

    def ids(self):
        return {d.id for d in self.datasets}

    def load_commit(self):
        """The DB commit the results were made from."""
        out = subprocess.run(["git", "-C", str(self.root), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True)
        return out.stdout.strip() or "unknown"
