# ser_dataset_db

A database of speech emotion recognition (SER) datasets, kept as CSV files under git. It is a tertiary source: it does not offer the truth about a dataset, but the way to the primary sources (papers, distribution pages, license files) where the truth can be checked.

## Mission and principles

**Mission**: to lower the cost for researchers of investigating datasets, by collecting up-to-date information on datasets usable for SER research as comprehensively as possible, in a database where anyone can check the primary source of every value.

**Principles** (none ranks above the others):

- **Verifiability**: every value can be checked by anyone against a primary source. Information without a source is not recorded.
- **Coverage**: collect as many datasets and as much information about them as possible. What one investigation misses is added by later investigations and by information from people.
- **Currency**: keep taking in new information and re-check old information. Every value records when it was checked, so readers can judge how current it is.
- **Transparency**: show who checked what and when, and in particular whether a value was verified by a person or only investigated by AI. State what is unknown and the limits of the DB.
- **Neutrality**: record facts only. The DB gives no judgements such as "should this dataset be used" or "is this good data", and when sources disagree it does not decide which to trust; that is left to the reader.

**How**: a source and the place in it for every value; the verification state of every value; repeated re-verification; and a design for AI. Dataset information is almost always on the web, so the way to the primary source can be written precisely; AI can build that way, and whoever checks only needs to look at the primary source it leads to. The DB is meant to be read through AI, so information is not cut for the sake of human readability; the generated views are an aid, not the main way to read it.

**For readers**: check the primary source before relying on a value, and cite the primary source, not this DB. The DB is not legal advice.

**Current position**: the DB is used for one researcher's work, and is designed for future public release. Background, challenges and the reasoning behind these principles are in `docs/manual.md` section 2; the discussion that led to them is in `docs/design/`.

- **`data/*.csv` is authoritative.** Everything in `views/` is generated from it.
- It covers datasets that are (or may be) usable for speech emotion recognition (SER). Scope: the axis is SER; emotion is taken in a broad sense that includes sentiment, and data such as speaking style, intent and dialogue acts is collected as material for SER research. Datasets only for EEG or ASR are out of scope.
- This is an independent git repository, separate from the ESPnet fork that holds the recipes. The database records what sources state; what a project decides to use, and why, is not here (see `local/`).

## Where to look first

| You want | Look at |
|---|---|
| All datasets at a glance | `views/datasets_wide.csv` (generated; one row per dataset, with the source URLs and the stage of checking) |
| Disagreements between sources | `views/discrepancies.csv` (generated) |
| Where a value comes from | `data/evidence.csv` (filter by `dataset_id` and `field`), then `data/sources.csv` by `source_id` |
| Problems found in a release | `data/issues.csv` |
| How many files each label has | `data/label_counts.csv` |
| Meaning, type and allowed nulls of a column | `schema/columns.csv`; allowed values in `schema/enums.csv`; table keys in `schema/tables.csv` |
| A beginner's guide with a glossary | `docs/manual.md` (English), `docs/manual.ja.md` (Japanese translation; always update both together) |
| How the DB was designed: decisions with their reasons | `docs/design/agenda.md`, `docs/design/archive/` |
| How to maintain the DB (workflow for Claude Code) | `.claude/skills/maintaining-ser-dataset-db/SKILL.md` |
| Your own decisions that build on the DB (which datasets you use, license groups, ...) | `local/` (git-ignored; see `local/README.md`) |

## Tables

| File | One row is | Key |
|---|---|---|
| `data/datasets.csv` | one dataset | `dataset_id` |
| `data/evidence.csv` | the source of one value of `datasets` (or of a label set attribute) | `evidence_id` = `<dataset_id>/<field>/<NN>` |
| `data/sources.csv` | one source document: paper, page, card, license file, release files, recipe readme | `source_id` |
| `data/dataset_sources.csv` | a source that introduces a dataset (paper, distribution, card, mirror, readme) | `dataset_id`, `source_id`, `role` |
| `data/annotations.csv` | a label set (emotion categories, emotion attributes, speaking style, ...) or another annotation (transcript, speaker, ratings, ...) of a dataset | `dataset_id`, `item`, `name` |
| `data/label_counts.csv` | the number of files of one label of a label set, as a source states it | `dataset_id`, `item`, `label`, `source_id` |
| `data/issues.csv` | one problem of a release as distributed | `dataset_id`, `issue_no` |
| `data/aliases.csv` | another name of a dataset | `dataset_id`, `alias` |
| `data/relations.csv` | a relation between datasets (version, subset, different dataset, suspected identity, shared sentences) | `dataset_id`, `relation`, `other_dataset_id` |
| `data/label_normalization.csv` | a spelling or word-form variant of a label name and its normalised form | `source_label` |

## What a dataset row holds

- **Identity and access**: `name`, `full_title`, `languages`, `license_spdx` (a classification of the stated terms, not a legal interpretation; `license_note` only where the identifier cannot convey the terms), `access_method` (what the documentation says), `access_observed` and `access_observed_on` (what happened when the data was requested or downloaded).
- **Size**: the documentation's values `n_files_reported`, `hours_reported`, `n_speakers_reported`, and the values of the whole release as distributed, before any filtering, `n_files_release`, `hours_release`, `n_speakers_release`. The two sit side by side and may differ; the DB does not choose. Files per label are in `label_counts.csv`.
- **How it was made**: `speech_production` (acted / improvised / elicited / spontaneous / read / synthetic), `material_origin` (recorded for the dataset, film or TV, web video, ...), `vocal_content` (speech / nonverbal / both), `spoken_text_design` (how the spoken text relates to the labels: the same sentences in every emotion, scripted dialogue, no script, ...).
- **Labels**: the label sets are rows of `annotations.csv` (`item` = `emotion_categories`, `emotion_attributes`, `speaking_style`, `sentiment`, `intent`) with their `labels`, `scale`, who made them (`annotator`), on what basis (`label_basis`: intended / perceived / self-reported / context-inferred / automatic) and whether people checked them (`label_verification`). Never infer one of these from another. The columns `emotion_categories`, `emotion_attributes`, `main_label_set_type`, `main_labels`, `label_source`, `label_basis` and `label_verification` of `datasets.csv` are derived from the main label set by `tools/derive.py`; do not edit them.
- **Other facts**: `official_split`, `listening_test` (`reported` / `not_stated`: only that a listening test exists; its result and design are in the source), `source_rights_note` (what sources say about the rights in third-party material, quoted), `language_note`, `notes`.
- **Checking**: `documents_checked` and `implementation_checked` in `views/datasets_wide.csv` say whether a primary source or a recipe readme backs the dataset's values.

## Conventions

- **Missing values**: empty = not checked. `unknown` = checked, but the sources do not say; `NA` = does not apply; `none` = checked, there is none; `conflicting` = sources disagree. Which are allowed per column is in the `nulls` column of `schema/columns.csv`.
- **Multiple values** are `;`-separated (`languages`, `speech_production`, `labels`, ...).
- **IDs** match `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`. A committed ID never changes (if it must, keep the old ID in `aliases` as `former_label`). Implemented datasets use the egs3 recipe name.
- **CSV format**: UTF-8, no BOM, LF, rows in key order. After editing by hand, run `python3 tools/db.py fmt`.
- **Language**: all text in the DB and its documents is English (dataset names and quotations keep their original language).
- **Public repository**: everything committed here, including commit messages, is public. Write no personal names, e-mail addresses or machine-specific paths; refer to people by role ("the project maintainer") and to local data by environment variable. `tools/validate.py` rejects absolute home paths.

## Evidence rules

Every value of the columns that take evidence (see `evidence=yes` in `schema/columns.csv`) has at least one row in `evidence.csv`, and every row points at a source in `sources.csv`.

- **Sources.** A source has a `source_type`: `primary` (published by the dataset's authors or their organisation: paper, page, license file, release files), `implementation` (the `## The data` section of an ESPnet recipe readme, cited at a commit on the public fork `itoten/espnet`: what only obtaining and opening the release shows; written by the recipe author, a practical reference and not a research result), or `secondary` (a mirror, re-upload, survey or database; only when the primary source cannot be accessed). The same URL can be a primary source for one dataset and a secondary one for another; these are two sources. A source whose publisher is not yet checked has an empty `source_type` and is listed in the validator's warning.
- **A recipe readme is cited only for what the documentation does not state** and only opening the release shows (counts of the release, duplicates, what the files contain). When a paper, page or card states the same thing, that source is cited even if the readme repeats it.
- **Deciding a value.** All `current` rows of a field agree on the value of the cell. If sources disagree the rows are `conflicting` and the cell is `conflicting`: the DB does not choose between sources. A `provisional` row is a value without a public source (it came from earlier records); it stays until a primary source or the readme replaces it. A newer fact marks the older row `superseded`; history is never deleted.
- **`*_release` columns** take only `implementation` sources; `*_reported` columns take none. The DB does not count anything by itself.
- **`checked_on` and `checked_by`.** Every row has the date checked and who checked: `claude` (AI investigation) or `user` (the project maintainer opened the source). Rows checked by `user` are in the git history of pull requests named `verify/...`.
- **`locator`** marks the place in the source (25 words at most). For a readme it starts with `commit <12 characters>; <heading>`.
- Write nothing the sources do not say. Never guess URLs or titles.
- Free-text columns (`notes`, `license_note`, `language_note`, `source_rights_note`) have no evidence rows: each statement names its source in the text, for example `[aesdd_page]`; the validator requires a valid tag on every sentence. A fact in free text that no source states does not belong there.

## Validation and updates

```bash
python3 tools/validate.py     # format, types, keys, evidence, sources, derived columns, views
python3 tools/derive.py       # recompute the derived columns of datasets.csv from annotations.csv
python3 tools/views.py        # regenerate views/
python3 tools/db.py get|set|add|fmt   # view or edit one row
```

- Run with the system Python 3 (with PyYAML). pandas is not used.
- `git config core.hooksPath tools/hooks` makes `tools/validate.py` run before every commit. Do not use `--no-verify`.
- Recipes are read from the recipe branch of the ESPnet repository (`tools/egs3.py`) only to find the commit of a readme. Machine-specific settings such as the location of that repository go in `.env` (git-ignored; copy `.env.example`).
- Every value change needs an evidence row. Make one commit per dataset or per checking session, and write in the message what was wrong and what the evidence was.
- Human verification: the maintainer opens the source of a batch of values in a pull request (`verify/<date>-<n>`) and merges it; the rows in it then have `checked_by=user`.

## What counts as one row

- One row per original (first published) dataset. Plain re-uploads on Hugging Face, Kaggle, etc. are not rows; they go into the original's `aliases` and, as mirrors, into its sources. Datasets whose content differs from the original (re-splits, subsets, new labels) are separate rows linked with `relations`.
- Corpora built for TTS are included if they have emotion labels. Datasets without audio (text only, features only) are included to record what was found; `access_observed` says what happened.
- When two rows turn out to be the same, link them with `possibly_same_as` in `relations`. IDs are never deleted.
- A version of a dataset that its authors publish under another name or DOI is a separate row linked by `version_of`; other versions are one row, and `sources.describes_version` says which version each source describes.

## Known limits

- Most values have the evidence of an AI investigation; a person has opened the source of few of them (`checked_by=user`). Check the primary source before relying on a value.
- `provisional` rows (names, titles, and values from before sources were required) are not yet backed by a source. `views/datasets_wide.csv` shows the stage of every dataset.
- The recipe readmes were written by the recipe author; their numbers are as reliable as that author's counting.

## License

MIT (see [LICENSE](LICENSE)). The license covers this database and its tools. It does not cover the datasets described here: each keeps its own terms, recorded in `license_spdx` and `license_note`.
