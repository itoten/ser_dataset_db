"""The filters a config can choose from: one method of DatasetFilter per filter.

Like the stages of an ESPnet system, a config lists method names in order. Each method takes one
Dataset plus the `params` written in the config, and returns a Verdict:
  keep        the dataset passes
  remove      the DB says the dataset fails
  unverified  the DB does not say; the dataset is kept and marked
To add a filter, add a method here (its docstring is shown in summary.md).
"""
from dataclasses import dataclass
from enum import Enum


class Outcome(Enum):
    KEEP = "keep"
    REMOVE = "remove"
    UNVERIFIED = "unverified"


@dataclass
class Verdict:
    outcome: Outcome
    reason: str = ""


def keep(reason=""):
    return Verdict(Outcome.KEEP, reason)


def remove(reason):
    return Verdict(Outcome.REMOVE, reason)


def unverified(reason):
    return Verdict(Outcome.UNVERIFIED, reason)


class DatasetFilter:
    """Every public method is a filter."""

    def keep_implemented(self, dataset):
        """Keeps datasets that have an ESPnet recipe (implementation_checked is true)."""
        if dataset.value("implementation_checked") == "true":
            return keep("recipe readme registered as a source")
        return remove("no recipe")

    def remove_listed(self, dataset, datasets):
        """Removes the datasets listed in the config, each with its reason."""
        entry = next((e for e in datasets if e["dataset_id"] == dataset.id), None)
        return remove(entry["reason"]) if entry else keep()

    def keep_with_label_set(self, dataset, label_set):
        """Keeps datasets that have the label set (annotations item) with labels other than 'none'."""
        if not dataset.annotations:
            return unverified("no annotation registered in the DB")
        if any(a["item"] == label_set and a["labels"] != "none" for a in dataset.annotations):
            return keep(f"has {label_set}")
        return remove(f"no {label_set}; annotations: " + ";".join(sorted(dataset.annotation_items())))

    def remove_synthetic(self, dataset, synthetic_values, synthetic_label_source):
        """Removes synthetic speech, and labels that are the emotion requested from a synthesiser."""
        columns = ("speech_production", "material_origin")
        values = set().union(*(dataset.values(c) for c in columns))
        described = " / ".join(f"{c}={dataset.value(c) or 'empty'}" for c in columns)
        if values & set(synthetic_values):
            return remove(described)
        if dataset.value("label_source") == synthetic_label_source:
            return remove(f"label_source={synthetic_label_source}")
        if all(dataset.is_unknown(v) for v in values):
            return unverified(described)
        return keep(described)

    def remove_automatic_labels(self, dataset, automatic_label_source, human_checked_verification):
        """Removes fully automatic labels; automatic labels checked by people are kept."""
        source, verification = dataset.value("label_source"), dataset.value("label_verification")
        described = f"label_source={source or 'empty'} / label_verification={verification or 'empty'}"
        if dataset.is_unknown(source):
            return unverified(described)
        if source == automatic_label_source and verification != human_checked_verification:
            return remove(described)
        return keep(described)

    def remove_unclear_license(self, dataset, unclear_licenses):
        """Removes datasets with no clear license, including unknown ones (never unverified)."""
        spdx = dataset.value("license_spdx")
        if not spdx:
            return remove("license_spdx empty (not checked in the DB)")
        if spdx in unclear_licenses:
            return remove(f"license_spdx={spdx}")
        return keep(f"license_spdx={spdx}")


FILTER_NAMES = sorted(name for name in vars(DatasetFilter) if not name.startswith("_"))
