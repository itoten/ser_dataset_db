# ser_dataset_db

A database of speech emotion recognition (SER) datasets, kept as CSV files under git. It is built first of all to be read and used by AI assistants (such as Claude), so it favours completeness and accuracy, and every important value carries its source.

- **`data/*.csv` is authoritative.** The Google spreadsheet it grew from ("ser_database", 84 rows) was frozen on 2026-10-12 and the original is kept in `sheet_import/` (origin and sha256 in `sheet_import/README.md`). The spreadsheet is no longer updated.
- It covers all datasets that are (or may be) usable for SER. Whether a dataset is implemented as an ESPnet recipe is recorded in `espnet_status`. Datasets only for EEG or ASR are out of scope.
- This is an independent git repository, separate from the ESPnet fork that holds the recipes; nothing written here goes into that repository.

## Where to look first

| You want | Look at |
|---|---|
| All datasets at a glance | `views/datasets_wide.csv` (generated; one row per dataset; the first 15 columns have the spreadsheet's names) |
| Disagreements between values | `views/discrepancies.csv` (generated) |
| The source of a value | `data/evidence.csv`, filtered by `dataset_id` and `field` |
| Meaning, type and allowed nulls of a column | `schema/columns.csv`; allowed values in `schema/enums.csv`; table keys in `schema/tables.csv` |
| Measured values of ESPnet recipes | `data/recipes.csv`, `measurements/<recipe>.json` |
| A beginner's guide with a glossary | `docs/manual.md` |
| A detailed investigation of one dataset (with verification; referenced from evidence `via`) | `reports/<date>_<dataset_id>_db_update.md` |
| How to maintain the DB (workflow for Claude Code) | `.claude/skills/maintaining-ser-dataset-db/SKILL.md` |

## Tables

| File | One row is | Key |
|---|---|---|
| `data/datasets.csv` | one dataset (authoritative) | `dataset_id` |
| `data/evidence.csv` | the source for one value in `datasets` | `evidence_id` = `<dataset_id>/<field>/<NN>` |
| `data/aliases.csv` | another name (spreadsheet name, official name, former label, recipe name, ...) | `dataset_id`, `alias` |
| `data/relations.csv` | a relation between datasets (version, subset, different dataset, suspected identity) | `dataset_id`, `relation`, `other_dataset_id` |
| `data/recipes.csv` | one egs3 recipe (`egs3/<recipe>/cls`), with automatic and hand-written columns | `recipe` |
| `data/recipe_labels.csv` | recipe x label; labels the recipe drops are kept too | `recipe`, `label` |
| `data/benchmark_membership.csv` | a member recipe of a multi-corpus recipe | `benchmark_recipe`, `member_recipe`, `role` |
| `data/annotations.csv` | dataset x non-emotion annotation; each row carries its own source | `dataset_id`, `item` |

- `recipes.dataset_id` links to `datasets`. Multi-corpus recipes have `NA` (their member recipes link to the datasets).
- Status: `espnet_status` is `implemented` (an egs3 recipe exists) / `candidate` / `needs_decision` / `deferred` / `excluded`. Every status except `implemented` has reasons in `status_reason_codes` (`;`-separated); `implemented` has `NA`. Notes go in `status_note`; the date checked in `status_checked_on`.
- Who made the labels: `datasets.label_source` (`human` / `automatic` / `mixed` / `synthesis_specified`: synthetic audio labelled with the emotion given to the synthesiser) and `label_verification` (`human_reviewed`: people reviewed automatic labels / `listener_validated`: instructed labels confirmed by a listening test / `none` / `unknown` / `NA`). Each value has an evidence row. Empty means not checked; filled during recipe review. `recipe_labels.label_type` is `categorical` / `polarity` / `intent` / `dimensional` / `other` (empty for `recanvo`, not checked). Polarity and intent labels have `common7=none`.
- How the audio was produced and how the labels were made are recorded separately. `speech_production` (`acted` / `elicited` / `spontaneous` / `read`: reading without an emotion instruction / `synthetic`; `;`-separated) says how the audio was produced; `label_basis` (`intended`: the emotion the speaker was told to portray / `perceived`: the emotion listeners perceived / `self_reported` / `context_inferred`: from context or the meaning of the words / `automatic`: a model; `;`-separated) says how the main labels were made. Acted speech can carry perceived labels, so never infer one from the other. Number of raters, what they saw or heard and how ratings were combined go in `label_basis_note`. Both columns have evidence rows. `recording_context` stays as the column for the setting or medium. Which kind of label a recipe actually uses is `recipes.label_basis_used`. Instructed labels confirmed by a listening test have `label_verification=listener_validated`. These are filled from primary sources during each recipe review (rows not yet reviewed are empty = not checked).
- Whether the words give the label away (shortcut learning) is flagged separately. `text_emotion_link` (`parallel` / `neutral_text` / `emotion_specific_text` / `unrelated_text` / `dialogue_script` / `unscripted`; `;`-separated) says how the spoken text relates to the labels; `lexical_confound` (`full` / `strong` / `moderate` / `weak` / `possible` / `none`) is a rough flag of how far the words alone give the label away, with its basis in `lexical_confound_note`. Both have evidence rows and are filled only from a clear source (a design statement or a measurement), never by guessing. `possible` and above mean: check the actual data before relying on it.
- Annotations other than emotion labels go in `annotations.csv`, one item per row (annotator, unit, whether the recipe uses it, and a source). `annotations_other` keeps the spreadsheet's original text. Currently: `anad` 3, `audiospeechsentiment` 2, `baser` 4, `berst` 9, `brytserc` 1, `casia` 3, `cbesd` 5, `csemotions` 2, `dailytalk` 6, `eesc` 6, `emis` 5, `emogator` 2, `emotional_ema` 8, `emouerj` 3, `eseravd` 3, `harper_valley_bank` 19, `rml_emotion` 4, `syntact` 6, `telugu_emotion_kaggle` 4, `usc_emo_mri` 5; more are added from primary sources when recipes are registered.
- Row origin: `in_sheet` (whether the row was in the original spreadsheet). Rows not from the spreadsheet have `sheet_verified=NA`. `sheet_verified` keeps the spreadsheet's Verified column (whether someone checked by hand) as is and is not used for decisions.

## Conventions

- **Missing values**: empty = not checked. `unknown` = checked, but the sources do not say; `NA` = does not apply; `none` = checked, there is none. Which are allowed per column is in the `nulls` column of `schema/columns.csv`.
- **Multiple values** are `;`-separated (`labels_discrete_reported`, `languages`, `status_reason_codes`, ...).
- **IDs** match `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`. Implemented datasets use the egs3 recipe name. A committed ID never changes (if it must, keep the old ID in `aliases` as `former_label`).
- **CSV format**: UTF-8, no BOM, LF, rows in key order. After editing by hand, run `python3 tools/db.py fmt`.
- **Licenses**: `license_spdx` maps the wording in the sources to an SPDX identifier (or `LicenseRef-...`). `license_class` is derived mechanically from the identifier and is not a legal interpretation. Read `license_note` and the primary source before using a dataset.
- **Language**: all text in the DB and its documents is English (dataset names and quotations keep their original language).

## Evidence rules

These `datasets` columns carry an evidence row for each value: `languages`, `recording_context`, `vocal_content`, `license_spdx`, `access_method`, `raw_audio_available`, `n_utt_reported`, `hours_reported`, `n_speakers_reported`, `n_files_release_measured`, `n_speakers_measured`, `labels_discrete_reported`, `dimensional_attributes`, `espnet_status`, `status_reason_codes`, `label_source`, `label_verification`, `speech_production`, `label_basis`, `text_emotion_link`, `lexical_confound`. URL and free-text columns do not.

- Each column has exactly one row with `is_canonical=true`, and its value equals the cell in `datasets`.
- Strength of `source_type`: `user` > `measured` > `primary` (the original text of a primary source) > `project_doc` (internal notes of this project) > `secondary` > `sheet`. `locator` marks the place in the source (25 words at most); `via` says which document led us there.
- When a new fact appears, the old row is kept and marked `superseded`, and a new row is added. When sources disagree and cannot be decided, keep two or more `conflicting` rows and set the `datasets` cell to `conflicting` (e.g. the licenses of EmoDB and TurEV-DB).
- `*_measured` columns take only `measured` evidence; `*_reported` columns cannot use `measured` (published and measured values sit side by side in separate columns).
- Write nothing the sources do not say. Never guess URLs or titles.
- The date checked is `checked_on` of each evidence row (filled for every row) and is summarised in `views/datasets_wide.csv` (`license_checked_on`, `oldest_checked_on`, ...). For rows from the spreadsheet (`sheet`), the date is the import date, not a date on which the content was checked.
- The only basis for measured values (counts, hours, speakers) is `measurements/<recipe>.json` and measurements of the downloaded files.

## Validation and updates

```bash
python3 tools/validate.py             # reads egs3 from the recipe branch and compares with measurements
python3 tools/validate.py --offline   # does not read the recipe repository
python3 tools/views.py                # regenerates views/
python3 tools/db.py get|set|add|fmt   # view or edit one row
```

- Run with the system Python 3 (with PyYAML). pandas is not used.
- `git config core.hooksPath tools/hooks` makes `tools/validate.py` run before every commit. Do not use `--no-verify`.
- egs3 recipes are read from the recipe branch of the ESPnet repository, not from its working tree (the location and branch are set in one place, `tools/egs3.py`).
- Measurements: run `tools/measure.py --all` in the toolkit's environment (see its docstring), then `python3 tools/sync.py` to update the automatic columns of `recipes.csv`; people fill the hand-written columns.
- `validate.py` checks format, types and allowed values, keys and foreign keys, duplicate aliases, the evidence rules, agreement of the implementation status with egs3 (recipes on the branch but not registered only produce a warning), agreement of `recipes.csv` / `recipe_labels.csv` with `measurements/*.json`, and that `views/` is up to date. It does not check whether `measurements/` still matches the local outputs.
- Every value change needs an evidence row. Make one commit per dataset or per checking session, and write in the message what was wrong and what the evidence was.

## What counts as one row

- One row per original (first published) dataset. Plain re-uploads on Hugging Face, Kaggle, etc. are not rows; they go into the original's `aliases`. Datasets whose content differs from the original (re-splits, subsets, new labels) are separate rows linked with `relations`.
- Corpora built for TTS are included if they have emotion labels. Datasets without audio (text only, features only) are kept as `excluded` to record what was found.
- When two rows turn out to be the same, mark one `excluded` (`duplicate_entry`) and link them with `possibly_same_as` in `relations`. IDs are never deleted.

## Current state (2026-10-24)

322 datasets (84 from the spreadsheet, 238 added later). `implemented` 74, `candidate` 160, `deferred` 35, `needs_decision` 7, `excluded` 46. All 28 corpora in Table I of the MSP-Podcast paper (arXiv 2509.09791v1) are included.

- The survey of 2026-10-14 added 158 datasets from surveys (SuperKogito's list, EmoBox, KuralHub, etc.) and searches of Hugging Face, Zenodo, Kaggle, Mendeley, figshare and GitHub.
- On the same day the status policy was revised and all excluded rows were reviewed (see "Status policy" below).
- The scope is not limited to emotion: data on paralinguistic information in general (emotion, speaking style, intent, dialogue act, sentiment, ...) is collected. 12 intent and dialogue-act datasets were added (`candidate`, reason `unexamined`): SLURP, Timers and Such, Fluent Speech Commands, Snips/Sonos, STOP, MInDS-14, Speech-MASSIVE, ITALIC, DIHANA, SpokenWOZ, Harper Valley Bank, SLUE-HVB. Not yet surveyed: CATSLU, dialogue acts such as MRDA, SwDA and AMI, ATIS audio, SLURP in other languages, intent data in other languages.

Status policy (project maintainer's decision, 2026-10-14):

- **`excluded` needs a clear reason**: no audio (`text_only`, `no_raw_audio_features_only`, `no_audio_paper_only`, `no_audio_code_only`), a redistribution of other data (`redistribution_of_existing_corpus`), a duplicate (`duplicate_entry`), labels unusable for classification (e.g. speaker IDs), unobtainable because of regional restrictions, and so on.
- Not reasons to exclude: size, manual access steps (application, signature, login, purchase; the maintainer can be asked to do them), Kaggle (a free account and token suffice), the kind of label (sentiment, intent, dimensional values, speaking style), automatic labels, synthetic speech. These stay `candidate`, with limitations and caveats in `status_note`. Overlap between sentiment and discrete emotions (anger vs negative) and continuous labels that the current system cannot handle are decided at implementation time.
- `candidate`: has audio and labels usable for classification, and can probably be obtained. `unexamined` means implementation has not been considered.
- `needs_decision`: matters only the maintainer can decide, such as terms of use and cost (commercial vendor data, distribution of video links only, the MER2026 application wording, ...).
- `deferred`: could not be confirmed (the distributor does not respond, no access route found, ...). Becomes `candidate` or `excluded` once confirmed.
- Size, number of raters, unclear provenance and similar are written in `status_note` as analysis caveats (e.g. `legov2` has one rater and 302 calls; `expresso` and `mlend_numerals` mix in non-emotion styles; `humyn_indian_emotional` has 16 clips).

Known caveats:

- Evidence for status, license and access is mostly primary sources (distribution pages, APIs, papers) or measurements. The check of 2026-10-14 re-confirmed at the distributor the rows whose only evidence was the spreadsheet or working notes (rows whose values changed appear next to their old values in `views/discrepancies.csv`).
- Kaggle datasets were checked with listings and labels from the authenticated API. `hindi_ser_vishlb` (8 emotion classes, 3,200 clips) and `telugu_emotion_kaggle` (5 classes, 458 clips), which had been excluded on the assumption that they needed no authentication, were returned to candidate in the review.
- Not confirmed in primary sources:
  - 28 rows supported only by KuralHub (a third-party survey). Their `status_note` says access was not checked in a primary source. Many are data from older papers, listed as "on request".
  - Rows that could not be checked because the distributor did not respond, etc.: `amigos` (HTTP 503 on 2026-10-14), `casia` (no connection), `cheavd`, `belfast`, `emotion_origlia2010`, `usoms`, `eyase`.
  - The `deferred` rows (35).
- Disagreements between published and measured values are in `views/discrepancies.csv`. Recipes filter by length and label, so `n_utt_reported` and the recipe's count often differ, which is normal.
