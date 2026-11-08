"""Runs one config: loads the DB, applies the chosen filters in order, writes the outputs."""
from dataclasses import dataclass, field

from .database import DatasetDatabase
from .dataset_filter import FILTER_NAMES, DatasetFilter, Outcome
from .report_writer import ReportWriter


@dataclass
class FilterStep:
    """One entry of `filters` in the config."""

    filter: str
    params: dict = field(default_factory=dict)
    note: str = ""
    name: str = ""

    def __post_init__(self):
        self.name = self.name or self.filter


@dataclass
class FilterResult:
    """What happened to one dataset: (step name, Verdict) for every step it reached."""

    dataset: object
    verdicts: list = field(default_factory=list)

    @property
    def removed_by(self):
        name, verdict = self.verdicts[-1]
        return name if verdict.outcome is Outcome.REMOVE else ""

    @property
    def unverified_by(self):
        return [name for name, v in self.verdicts if v.outcome is Outcome.UNVERIFIED]

    @property
    def status(self):
        if self.removed_by:
            return "removed"
        return "kept_unverified" if self.unverified_by else "kept"


class FilterPipeline:
    def __init__(self, config, db_root, output_dir):
        self.config = config
        self.steps = [FilterStep(**entry) for entry in config["filters"]]
        self.database = DatasetDatabase(db_root, config.get("unknown_values", ["", "unknown"]))
        self.writer = ReportWriter(output_dir)
        self.validate_steps()

    def validate_steps(self):
        """Stop on a filter name that does not exist, or a listed dataset_id not in the DB."""
        known_ids = self.database.ids()
        for step in self.steps:
            if step.filter not in FILTER_NAMES:
                raise SystemExit(f"unknown filter '{step.filter}'; available: {', '.join(FILTER_NAMES)}")
            listed = {e["dataset_id"] for e in step.params.get("datasets", [])}
            if listed - known_ids:
                raise SystemExit(f"{step.name}: not in the DB: {sorted(listed - known_ids)}")

    def run(self):
        dataset_filter = DatasetFilter()
        results = []
        for dataset in self.database.datasets:
            result = FilterResult(dataset)
            for step in self.steps:
                verdict = getattr(dataset_filter, step.filter)(dataset, **step.params)
                result.verdicts.append((step.name, verdict))
                if verdict.outcome is Outcome.REMOVE:
                    break
            results.append(result)
        self.writer.write(self, results)
        return results
