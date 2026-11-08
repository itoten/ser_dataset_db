# dataset_filtering

Filters the datasets of the DB for an experiment. Each experiment is one config; the code is shared.

    python3 local/dataset_filtering/run.py config/<experiment>.yaml

## Layout

| Path | Contents |
|---|---|
| `run.py` | Reads a config and runs `FilterPipeline` |
| `config/<experiment>.yaml` | Description, and the filter steps in order with their parameters (exclusion lists go here) |
| `src/database.py` | `DatasetDatabase` (loads the DB) and `Dataset` (one dataset's columns and annotations) |
| `src/dataset_filter.py` | `DatasetFilter`: one method per filter. Add new filters here |
| `src/filter_pipeline.py` | `FilterPipeline`: loads the DB, runs the steps in order, hands the results to `ReportWriter` |
| `src/report_writer.py` | `ReportWriter`: writes the outputs |
| `output/<experiment>/` | Generated. Do not edit |

## Outputs (`output/<experiment>/`)

- `summary.md`: the config's description, counts per step, and for each step its parameters (such as the
  exclusion list) and the datasets it removed or left unverified.
- `result.csv`: one row per dataset in the DB: `status` (kept / kept_unverified / removed), `removed_by`, `reason`, `unverified`.
- `filter.log`: every verdict of every step for every dataset, with its reason (tab separated).

## How filters decide

A filter returns keep, remove, or unverified (the DB does not say: the dataset is kept and marked).
A dataset stops at the first step that removes it. `unknown_values` in the config says which DB values
mean "not known". A filter may refuse to leave things unverified (`remove_unclear_license` removes unknown licenses).

## Adding a filter

1. Add a method to `DatasetFilter` in `src/dataset_filter.py`: `def name(self, dataset, <params>)` returning
   `keep(...)`, `remove(...)` or `unverified(...)`. Its docstring appears in summary.md.
2. Add `- filter: <name>` with its `params` (and optionally `name` and `note`) to a config.
   Quote YAML values that contain ` #`, or YAML reads the rest as a comment.
