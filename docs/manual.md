# The SER dataset DB: a beginner's guide

This guide explains the database from scratch. Terms are explained before they are used. The figures were recounted from `data/*.csv` on the date given in section 14 (`doc_counts.py` refreshes them, see the maintenance skill).

## 1. The DB in 30 seconds

### 1.1 In one sentence

**"A tertiary source that leads to the sources of datasets usable for SER research."** It does not offer the truth about a dataset, but the way to the papers, distribution pages and license files where it can be checked. It is a set of CSV files that open in any spreadsheet program, with its history managed by `git`.

### 1.2 In numbers

| Item | Value |
|---|---|
| Datasets registered | 318 |
| Datasets with a primary source behind their values (`documents_checked`) | 276 |
| Datasets with a recipe readme behind their release counts (`implementation_checked`) | 102 |
| Evidence rows (sources of values) | 3,680 |
| Source documents | 795 |
| Label counts (files per label) | 680 |
| Issues found in releases | 325 |

### 1.3 What makes it useful

- **Every value has a source**: it does not just say "the license is CC-BY-4.0" but records, row by row, which document, which place in it, when and by whom it was checked.
- **No guessing**: what is unknown is recorded as unknown (7). URLs and titles are never made up.
- **Disagreements stay visible**: when two sources disagree, both are kept and the value says `conflicting`; the DB does not pick one.
- **Machine-checked**: `validate.py` checks format, sources and evidence automatically; a commit is refused if it fails.
- **Release facts from the implementation**: the number of files, speakers and hours of each release, files per label and problems found while building the ESPnet recipes (experiment set-ups) are copied from the recipe readmes.

## 2. Why it exists

### 2.1 Background

In today's AI research, centred on deep learning, the scale of the data cannot be ignored, and multi-corpus research, which combines several datasets, has become an important method. Researchers therefore keep looking for larger and more numerous datasets.

But datasets are created, redistributed and withdrawn every day. Information changes so fast that a list of datasets made by someone becomes useless within a few years, and whether what it says is still correct has to be checked again anyway. The information researchers must follow keeps growing, and investigating datasets has itself become very costly.

With recent AI, information can be searched more comprehensively than with a search engine. But if every researcher investigates separately each time a new study starts, everyone spends the same effort and the same tokens to obtain the same information.

What is needed is a tertiary source through which up-to-date information on the world's datasets can be reached easily: a "Wikipedia of datasets".

### 2.2 Challenges

1. **Coverage without collaborators.** Wikipedia's coverage rests on the collaboration of many people. A narrow research field such as SER cannot expect that. As many datasets as possible, and their information, must be collected with few people.
2. **Keeping up with information that keeps changing.** Datasets appear, are redistributed and disappear, and terms such as licenses can change at the authors' will. Collected information soon becomes outdated, yet most lists do not even say when their information was valid.
3. **Correctness cannot be guaranteed.** Whoever investigates makes mistakes: people err, and AI hallucinates. However careful one is, "absolutely correct information" cannot be offered. Moreover, most existing lists give no sources, so readers cannot notice the errors and end up investigating everything again themselves.

### 2.3 Mission

To lower the cost for researchers of investigating datasets, by collecting up-to-date information on datasets usable for SER research as comprehensively as possible, in a database where anyone can check the primary source of every value.

### 2.4 Principles

None ranks above the others.

| Principle | Meaning |
|---|---|
| **Verifiability** | Every value can be checked by anyone against a primary source. What this DB offers is not "the truth" but the way to it. Information without a source is not recorded. Readers are advised to always check the primary source. |
| **Coverage** | Collect as many datasets and as much information about them as possible. What one investigation misses is added by later investigations and by information from people, aiming at coverage beyond any other list. |
| **Currency** | Keep taking in new information and re-check old information. Every value records when it was checked, so readers can judge how current it is. |
| **Transparency** | Show who checked what and when, and in particular whether a value was verified by a person or only investigated by AI. Within one DB, values differ in how certain they are; if this is invisible, readers cannot tell how far to trust each value. State what is unknown and the limits of the DB. |
| **Neutrality** | Record facts only, and give no judgements such as "should this dataset be used" or "is this good data". Whether a dataset is usable depends on the purpose of the research, and a written judgement makes readers follow it without looking at the primary sources. When sources disagree, the DB does not decide which to trust; that is left to the reader. |

These principles are the basis for the rules (this manual, `schema/`, `tools/validate.py`) and the procedures (the maintenance skill). The decisions that follow from them are recorded with their reasons in [design/](design/agenda.md).

### 2.5 How

Dataset information is almost always on the web and open to anyone (papers, distribution pages, license files). So the way to the primary source can be written precisely. Building that way can be left to AI, and whoever checks needs to look not at the way but only at the source it leads to. This makes coverage and verifiability possible together with few people. The main methods:

| Method | What it means |
|---|---|
| **A source for every value** | For each value, record the source document, the place in it, and the date checked. |
| **Verification state** | For each value, record whether AI only investigated it or a person checked it (`checked_by`), and whether it has a public source at all (`provisional`). |
| **Repeated re-verification** | Regularly re-check that values match their sources and that the sources still say the same. |
| **A design for AI** | Assume AI is used to investigate, verify and read the DB. Information is not cut for the sake of human readability; the generated views are an aid, not the main way to read it. |

### 2.6 For readers

- Check the primary source before relying on a value, and cite the primary source, not this DB.
- Whether you may use a dataset is for you to judge from the primary sources. The DB is not legal advice.
- Decisions that depend on your purpose (which datasets you use, how you group licenses or labels) are yours; keep them in the git-ignored `local/` folder (12.3).

## 3. Glossary

### 3.1 Research terms

| Term | Plain explanation |
|---|---|
| **SER** (speech emotion recognition) | Getting machines to recognise emotions (anger, joy, sadness, ...) from the voice |
| **Corpus / dataset** | A collection of speech data organised for research. Used interchangeably here |
| **Label** | The "answer" attached to a recording, e.g. "angry" |
| **Categorical emotion** | Representing emotion as one of a few boxes such as anger or joy (label set `emotion_categories`) |
| **Dimensional emotion** | Representing emotion as numbers, typically valence (pleasant-unpleasant) and arousal (activation) (label set `emotion_attributes`) |
| **Utterance** | A stretch of speech. Data sizes are counted in files or utterances |
| **Acted / improvised / elicited / spontaneous / read** | How the voice was produced: performed with an instructed emotion; performed without a script; induced by a task or stimulus; natural speech; read without an emotion instruction |
| **Intent / dialogue act** | Not emotion, but what the speaker wanted to do ("set an alarm") or the function of an utterance (question, request, agreement). Included because the DB also covers non-emotion paralinguistic information |
| **Paralinguistic information** | Information carried by the voice beyond the words (emotion, speaking style, intent, sentiment, ...) |
| **Sentiment (polarity)** | The direction of feeling, such as positive or negative |
| **TTS / ASR** | Text-to-speech synthesis / automatic speech recognition. Emotional corpora recorded for TTS are included; data only for ASR is out of scope |
| **Listening test** | A test in which people listen to the recordings and answer, for example, which emotion they hear |

### 3.2 ESPnet terms

| Term | Plain explanation |
|---|---|
| **ESPnet / ESPnet3** | Open-source research software for speech processing, to which this project adds SER |
| **Recipe** | The full set-up for training and evaluating on one dataset, in the folder `egs3/<name>/cls` |
| **Recipe readme** | The `readme.md` of a recipe. Its `## The data` section is written by the recipe author about the whole release as distributed, and is what the DB cites for release counts |

### 3.3 Data-management terms

| Term | Plain explanation |
|---|---|
| **CSV** | A comma-separated table file; opens in Excel, Google Sheets or LibreOffice |
| **Authoritative data** | The data declared to be the original: `data/*.csv`. `views/` is generated from it, so never edit `views/` directly |
| **git / commit** | Software that records the history of file changes, and one recorded change. You can see later what changed when, and go back |
| **Pull request** | A proposed change on GitHub that someone reviews and merges; used here to record that the maintainer checked values |
| **Hook** | A check that runs automatically just before a commit; the commit is refused if it fails |
| **Key (ID)** | A name that identifies a row, e.g. `dataset_id` (`ravdess`). Never changed once set |
| **Foreign key** | A column that points to a key in another table, e.g. `evidence.dataset_id` points to a `datasets` row |
| **Schema** | The design: column names, types and meanings, in `schema/` |
| **Derived column** | A column computed from other tables by `tools/derive.py`; never edited by hand |

### 3.4 Source terms

| Term | Plain explanation |
|---|---|
| **Primary source** | Published by the dataset's authors or their organisation (paper, official distribution page, LICENSE file, release files) |
| **Implementation source** | The `## The data` section of a recipe readme: written by the recipe author after downloading and opening the release; a practical reference, not a research result |
| **Secondary source** | Written by others (summary sites, re-upload pages, surveys); used only when the primary source cannot be accessed |
| **Provisional** | A value kept from earlier records that has no public source yet |
| **Hugging Face (HF) / Kaggle / Zenodo / figshare / Mendeley Data** | Services where datasets are published |
| **DOI** | A permanent identifier for papers and data |
| **ISO 639-3** | Three-letter language codes: `eng` English, `jpn` Japanese, `cmn` Mandarin, `mul` several languages without a breakdown, `zxx` no linguistic content |

### 3.5 License terms

A license states how far data may be used. The explanations here are general, not legal advice.

| Term | Plain explanation |
|---|---|
| **CC (Creative Commons)** | A system that expresses conditions of use with fixed symbols |
| **BY / NC / SA / ND** | Credit the author / non-commercial only / derived works shared under the same terms / no modification |
| **CC0** | Rights waived; free to use |
| **MIT / Apache-2.0 / GPL** | Software licenses: permissive (credit) / permissive with patent terms / share under the same terms |
| **SPDX identifier** | The official short name of a license (e.g. `CC-BY-4.0`), used to avoid spelling variants |
| **LicenseRef-...** | The DB's own names for custom terms that SPDX does not cover (10) |
| **Redistribution** | Passing received data to others or publishing it elsewhere; often not allowed |

## 4. What is in the DB

### 4.1 Folder map

| Place | Content |
|---|---|
| `data/` | The authoritative tables (CSV) |
| `views/` | Generated from `data/`: `datasets_wide.csv` (one row per dataset), `discrepancies.csv` |
| `schema/` | Definitions: `columns.csv`, `enums.csv`, `tables.csv` |
| `tools/` | Checking and editing tools (`validate.py`, `derive.py`, `views.py`, `db.py`) |
| `docs/` | This guide (English and Japanese) and the design record in `docs/design/` |
| `local/` | Your own working space; git-ignored except its README |
| `.claude/skills/` | The procedure for maintaining the DB with Claude Code |

### 4.2 The tables (`data/`)

| File | One row is |
|---|---|
| `datasets.csv` | one dataset |
| `evidence.csv` | the source of one value |
| `sources.csv` | one source document |
| `dataset_sources.csv` | a source that introduces a dataset (paper, distribution, card, mirror, readme) |
| `annotations.csv` | a label set or another annotation of a dataset |
| `label_counts.csv` | files per label of a label set, as a source states it |
| `issues.csv` | one problem of a release as distributed |
| `aliases.csv` | another name of a dataset |
| `relations.csv` | a relation between datasets (version, subset, different dataset, suspected identity, shared sentences) |
| `label_normalization.csv` | a spelling or word-form variant of a label name and its normalised form |

### 4.3 How the tables connect

`datasets` is the centre. `evidence`, `annotations`, `label_counts`, `issues`, `aliases`, `relations` and `dataset_sources` carry the `dataset_id` of a dataset. `evidence`, `annotations`, `label_counts`, `issues`, `aliases`, `relations` and `dataset_sources` point at a document of `sources` by `source_id`.

### 4.4 What counts as one row

One row per original (first published) dataset. Plain re-uploads are not rows; they are aliases and mirror sources. Datasets whose content differs from the original (re-splits, subsets, new labels) are separate rows linked with `relations`. A version that its authors publish under another name or DOI is a row of its own (`version_of`); other versions are one row, and each source's `describes_version` says which release it describes.

## 5. Reading the `datasets` table

### 5.1 Columns to look at first

| Column | Meaning | Example |
|---|---|---|
| `name`, `full_title`, `languages` | name, title, ISO 639-3 codes | `RAVDESS` / `eng` |
| `license_spdx` | the stated terms as an SPDX identifier (10) | `CC-BY-NC-SA-4.0` |
| `access_method` / `access_observed` | how the documentation says to obtain it / what happened when it was requested or downloaded | `request_form_or_email` / `obtained` |
| `n_files_reported`, `hours_reported`, `n_speakers_reported` | what the documentation says | `1440` |
| `n_files_release`, `hours_release`, `n_speakers_release` | the whole release as distributed, before any filtering (recipe readme) | `1440` |
| `speech_production`, `material_origin`, `vocal_content` | how the voice was produced, where the audio comes from, speech or non-verbal | `acted` / `recorded_for_dataset` / `speech` |
| `spoken_text_design` | how the spoken text relates to the labels | `parallel` |
| `emotion_categories`, `emotion_attributes`, `main_label_set_type`, `main_labels`, `label_source`, `label_basis`, `label_verification` | the main label set and how it was made (derived from `annotations.csv`) | `angry;happy;sad` / `human` / `intended` |
| `official_split`, `listening_test` | an official partition exists; a listening test is reported | `false` / `reported` |

### 5.2 Documentation versus release

The documentation (paper, page) and the release as distributed often disagree: versions, rounding, files the authors left out. Both are recorded side by side (`*_reported` and `*_release`, `access_method` and `access_observed`) and the DB does not choose. Counts after a recipe's own filtering or splitting are not recorded.

### 5.3 Note columns

`notes`, `language_note`, `license_note` and `source_rights_note` are free text: facts and caveats only, each statement naming its source in brackets (`[aesdd_page]`). `license_note` is used only where the identifier cannot convey the terms; `source_rights_note` quotes what sources say about the rights in third-party material. The DB gives no verdict.

### 5.4 Label sets

A label set is a row of `annotations.csv` whose `item` equals its `name`: `emotion_categories`, `emotion_attributes`, `speaking_style`, `sentiment`, `intent`. It has its `labels` in the source's own words, the `scale` (granularity) as the source states it, `perceived_from` (what listeners saw or heard), and three attributes, each with its own evidence rows:

| Attribute | Values |
|---|---|
| `annotator` | `human`, `automatic`, `mixed`, `synthesis_specified` (synthetic audio labelled with the emotion given to the synthesiser) |
| `label_basis` | `intended` (the emotion the speaker was told to portray), `perceived` (the emotion listeners perceived), `self_reported`, `context_inferred` (from the scene, script or meaning of the words), `automatic` |
| `label_verification` | `human_reviewed`, `listener_validated` (instructed labels confirmed by a listening test), `none`, `unknown`, `NA` |

Never infer one attribute from another: acted speech can carry perceived labels. A dataset can have several label sets (instructed and perceived emotion, categories and dimensions, emotion and speaking style); the datasets columns show the main one.

### 5.5 Files per label

`label_counts.csv` has the number of files for each label of a label set, in the source's own label words. A paper's table and the recipe readme can both give counts for the same label. They do not have to agree, and both stay. `label_normalization.csv` maps only spelling (case, spaces) and word forms (angry/anger); a mapping that changes the meaning (joy to happy) is a project decision and does not belong in the DB.

### 5.6 Other annotations

Transcripts, speaker traits, ratings and so on are rows of `annotations.csv` with an `item` from a fixed vocabulary (`speaker_id`, `speaker_gender`, `transcript`, `sentence_id`, `session_id`, `take`, `intensity`, `listener_ratings`, `listening_test`, `segmentation`, `acoustic_features`, `split`, `video`, `physiological`, `other`) and the release's own name in `name`. Each row has its own source.

### 5.7 Listening tests

`listening_test` says only that a human listening test exists (`reported`) or that the sources read say nothing (`not_stated`). Its result and design (listeners, options, whether video was shown) depend on the test and cannot be compared across datasets, so they stay in the source. If a release distributes the ratings, they appear as a `listener_ratings` annotation.

### 5.8 Problems of a release

`issues.csv` lists what was found when the release was opened: broken or empty files, duplicates, missing or mismatched labels, differences from the documentation, silent or non-speech files, unusual audio, and observations from listening. Each row is one problem in the recipe author's words, with the number of files if given and the readme location. Observations from listening are the author's observations ("Observation by the recipe author (date)"), not measurements.

### 5.9 All column definitions

`schema/columns.csv` defines every column (type, allowed missing values, whether it takes evidence); `schema/enums.csv` lists every allowed value with its meaning.

## 6. Sources and evidence

### 6.1 Why keep evidence

A value without a source cannot be checked, and a list that cannot be checked is not trusted. Every value of the columns that take evidence has at least one row in `evidence.csv`.

### 6.2 What a source and an evidence row hold

A **source** (`sources.csv`) is a document: URL or DOI, title, `kind` (paper, distribution_page, dataset_card, license_file, release_files, readme, mirror, survey, other), `publisher` (authors, third_party, recipe_author), `source_type` (primary, secondary, implementation), the version of the dataset it describes, why it is about this dataset, and when it was checked. A source with an empty publisher has not been checked yet; the validator lists them. The same document can be a primary source for one dataset and a secondary one for another, which makes two sources.

An **evidence row** (`evidence.csv`) says: this value of this field is stated in this source, at this place (`locator`), checked on this date, by `claude` (AI investigation) or `user` (the project maintainer opened the source), with a `status`.

### 6.3 Deciding a value

| Rows of the field | The cell is |
|---|---|
| `current` rows, all with the same value | that value |
| two or more `conflicting` rows with different values | `conflicting` |
| one `provisional` row | its value, which has no public source yet |

The old row of a replaced value is marked `superseded` and kept: history is never deleted.

### 6.4 Where the recipe readme fits

A recipe readme is cited only for what the documentation does not state and only opening the release shows: counts of the release, duplicates, what the files contain. It is cited at a commit on the public fork, with `commit <hash>; <heading>` as the locator. When a paper or page states the same thing, that source is cited even if the readme repeats it.

### 6.5 Provisional values

A `provisional` row is a value kept from earlier records that has no public source: names, titles, and values that once came from internal notes or the DB's own measurements. It is shown as such and is replaced as soon as a source is checked.

### 6.6 Human verification

The maintainer checks batches of values (about 20 rows, starting with licenses) in a pull request named `verify/<date>-<n>`: open the link, compare the quoted words, merge. The rows of a merged pull request have `checked_by=user`; this is the only way that value is set (the validator rejects a `user` row whose note has no pull request number). The batches include the licenses that are `none_stated`, `unknown` or `conflicting`: a person checks those too.

## 7. Writing missing values

| Written as | Means |
|---|---|
| (empty) | not checked yet |
| `unknown` | checked, but the sources do not say or it cannot be decided |
| `NA` | does not apply |
| `none` | checked, and there is none |
| `conflicting` | sources disagree |

Which of them a column accepts is in the `nulls` column of `schema/columns.csv`. Multiple values are separated by `;`.

## 8. Derived columns

`emotion_categories`, `emotion_attributes`, `main_label_set_type`, `main_labels`, `label_source`, `label_basis` and `label_verification` of `datasets.csv` are computed from the main label set by `python3 tools/derive.py`, and the validator fails if they differ. The main set is `emotion_categories`, else `emotion_attributes`, else another label set. A set has one `label_basis`; if a release also has labels of another basis (for example listeners' perceived emotion next to the actors' intended emotion), they form a further row named `<basis>_<item>` (such as `perceived_emotion_categories`) with its own annotator, basis and verification.

## 9. Access

`access_method` is what the documentation says: `direct_download`, `free_account_required`, `gated_click_through`, `request_form_or_email`, `signed_agreement`, `paid_or_membership`, `unofficial_mirror_only`, `unavailable`, `unknown`. `access_observed` is what happened when the data was requested or downloaded (`obtained`, or one of those values) and `access_observed_on` is the date. A dataset can be hard to obtain, or its audio not distributed at all; the DB records it and does not rank datasets by it.

## 10. Licenses

### 10.1 Two columns

`license_spdx` is the stated terms as an SPDX identifier. `license_note` says what the identifier cannot (the gist of a custom license). Both describe the data's license, not the rights in third-party material behind it (`material_origin`, `source_rights_note`).

### 10.2 Custom terms

Terms that SPDX does not cover are `LicenseRef-custom-research-only` (research use only), `LicenseRef-proprietary-restricted` (restricted or paid), `LicenseRef-citation-request` (only asks for citation), `LicenseRef-other`, and `none_stated` (no statement found). `conflicting` means sources disagree.

### 10.3 Before using a dataset

The identifier is a classification of wording, not legal advice. Open the primary source, read the terms, and check whether the data's license and the license of bundled code differ. How licenses are grouped for an experiment is your own decision (12.3).

## 11. Checks

`tools/validate.py` checks format, types and allowed values, keys and foreign keys, the source and evidence rules, the derived columns, duplicate names, that `views/` is up to date, and that no machine-specific paths are committed. A pre-commit hook runs it; do not bypass it.

## 12. Using the DB

### 12.1 Looking things up

1. Open `views/datasets_wide.csv` in a spreadsheet and filter it (for example on `license_spdx`, `languages`, `main_label_set_type`).
2. For a value you will rely on, look up its row in `data/evidence.csv` (`dataset_id` and `field`) and open the source in `data/sources.csv`.
3. `views/discrepancies.csv` lists the values on which sources disagree.

### 12.2 For AI

The DB is meant to be read through AI. Read `README.md` first, then the rows you need; answer with the primary source, say when the support is provisional, secondary or an implementation source, and search outside only for empty, `unknown`, `conflicting` or provisional values.

### 12.3 `local/`

`local/` is a git-ignored working space (see its README): which datasets you use and why, how you group licenses, how you map labels. Join your files to the DB by `dataset_id`. The DB's tools never read it.

## 13. Adding and changing data

Changes are made with the maintenance skill (`.claude/skills/maintaining-ser-dataset-db/`): register the sources, then the values with their evidence, run `tools/views.py` and `tools/validate.py`, commit with a message that says what was uncertain and what the evidence was. Everything committed is public.

## 14. Current figures (2026-11-01)

| Item | Value |
|---|---|
| Datasets | 318 |
| Evidence rows: current | 2,543 |
| Evidence rows: conflicting | 13 |
| Evidence rows: provisional | 754 |
| Evidence rows: superseded | 370 |
| Sources: primary | 436 |
| Sources: implementation | 102 |
| Sources: secondary | 47 |
| Sources without a checked publisher | 210 |
| Annotation rows | 549 |
| Dataset sources links | 698 |

## 15. Limits

### 15.1 What the DB does not yet do

- Most values rest on an AI investigation; a person has opened the source of few of them. Check the primary source before relying on a value.
- The 754 provisional rows (names, titles, and values from before sources were required) and the 210 sources without a checked publisher are the main work left; `views/datasets_wide.csv` shows the stage of every dataset.
- The recipe readmes were written by the recipe author; their counts are as reliable as that author's counting.

### 15.2 What the DB will never do

It does not say which datasets to use, does not rank them, and does not choose between disagreeing sources.
