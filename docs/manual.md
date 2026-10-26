# The SER dataset DB: a beginner's guide

This guide explains the database from scratch. Terms are explained before they are used. All figures were recounted from `data/*.csv` on the date given in section 11 (they are refreshed by `doc_counts.py`, see the maintenance skill).

## 1. The DB in 30 seconds

### 1.1 In one sentence

**"A ledger of the public information about speech datasets that carry emotion (and other paralinguistic) labels."** It is a set of CSV files that open in any spreadsheet program, with its history managed by `git`.

### 1.2 In numbers

| Item | Value |
|---|---|
| Datasets registered | **322** (84 from the original spreadsheet + 238 added later) |
| Implemented in ESPnet | 93 |
| Candidates for implementation | 141 |
| Awaiting a decision | 7 |
| Deferred | 35 |
| Excluded (with reasons) | 46 |
| Evidence rows (sources of values) | 4,277 |
| Language codes | 70 |

### 1.3 What makes it useful

- **Every value has a source**: it does not just say "the license is CC-BY-4.0" but records, row by row, which page, which wording, when and by whom it was checked.
- **No guessing**: what is unknown is recorded as unknown (there are rules for writing missing values, section 7). URLs and titles are never made up.
- **Machine-checked**: `validate.py` checks format and missing evidence automatically; a commit is refused if it fails.
- **Linked to the implementation**: counts, hours and labels of the ESPnet recipes (experiment set-ups) actually built are measured and stored.

## 2. Why it exists

### 2.1 Background

Speech emotion recognition (SER) research uses dozens of datasets with different languages, sizes, licenses and access routes. Searching the web again each time someone asks "can this corpus be used commercially?" or "what emotional data is there in Japanese?" wastes time and tokens.

### 2.2 Goals

1. **Answer questions at once**: language, size, license, access, labels and implementation status of a dataset can be looked up without searching.
2. **Choose what to implement next**: datasets that are permissively licensed, directly downloadable and not yet implemented can be picked from a list.
3. **Reliable research**: for cross-corpus evaluation (section 3), the DB shows the basis for which data was used for training and which for evaluation. Licenses get particular care, because mishandling them can make results unpublishable.

### 2.3 Origin

It started as a Google spreadsheet, "ser_database" (84 rows). The spreadsheet was frozen on 2026-10-12 and the original is kept in [sheet_import/](../sheet_import/README.md); since then the CSV files are authoritative and the spreadsheet is not updated. On 2026-10-14, 158 datasets from surveys, existing lists and searches of hosting services, plus 12 intent and dialogue-act datasets and others, were added, bringing it to 307 rows; more have been added since.

## 3. Glossary

### 3.1 Research terms

| Term | Plain explanation |
|---|---|
| **SER** (speech emotion recognition) | Getting machines to recognise emotions (anger, joy, sadness, ...) from the voice |
| **Corpus / dataset** | A collection of speech data organised for research. Used interchangeably here |
| **Label** | The "answer" attached to a recording, e.g. "angry" |
| **Discrete (categorical) emotion** | Representing emotion as one of a few boxes such as anger or joy |
| **Dimensional emotion** | Representing emotion as numbers, typically valence (pleasant-unpleasant) and arousal (activation). The axes are listed in `dimensional_attributes` |
| **Utterance** | A stretch of speech. Data sizes are counted in utterances |
| **Speaker** | The person talking |
| **Acted** | Speech performed with emotion by actors or others |
| **Spontaneous** | Natural speech collected from conversations, podcasts, videos, etc. Closer to real life, but harder to label |
| **Intent / dialogue act** | Not emotion, but what the speaker wanted to do ("set an alarm") or the function of an utterance (question, request, agreement). Included because the DB also covers non-emotion paralinguistic information |
| **Paralinguistic information** | Information carried by the voice beyond the words (emotion, speaking style, intent, sentiment, ...) |
| **Sentiment (polarity)** | The direction of feeling, such as positive or negative |
| **TTS** | Text-to-speech synthesis. Emotional corpora recorded for TTS are included |
| **ASR** | Automatic speech recognition. Data only for ASR is out of scope |
| **Cross-corpus evaluation** | Training on one dataset and evaluating on another, to see whether a model generalises across datasets |
| **Fully out-of-domain evaluation** | Evaluating only on corpora never seen in training |

### 3.2 ESPnet terms

| Term | Plain explanation |
|---|---|
| **ESPnet / ESPnet3** | Open-source research software for speech processing, to which this project adds SER |
| **Recipe** | The full set-up for training and evaluating on one dataset, in the folder `egs3/<name>/cls` |
| **`cls`** | The system name for classification |
| **Implemented** | A recipe exists for the corpus |
| **Benchmark** | An evaluation framework combining several corpora; such recipes are `multi_corpus` |

### 3.3 Data-management terms

| Term | Plain explanation |
|---|---|
| **CSV** | A comma-separated table file; opens in Excel, Google Sheets or LibreOffice |
| **Authoritative data** | The data declared to be the original: `data/*.csv`. `views/` is generated from it, so never edit `views/` directly |
| **git / commit** | Software that records the history of file changes, and one recorded change. You can see later what changed when, and go back |
| **Remote** | The online copy of the repository (here on GitHub) |
| **Hook** | A check that runs automatically just before a commit; the commit is refused if it fails |
| **Key (ID)** | A name that identifies a row, e.g. `dataset_id` (`ravdess`). Never changed once set |
| **Foreign key** | A column that points to a key in another table, e.g. `evidence.dataset_id` points to a `datasets` row |
| **Schema** | The design: column names, types and meanings, in `schema/` |
| **sha256** | A fingerprint computed from a file's contents, used to check whether two files are identical |

### 3.4 Source terms

| Term | Plain explanation |
|---|---|
| **Primary source** | Information published by the authors themselves (paper, official distribution page, LICENSE file) |
| **Secondary source** | Information written by others (summary sites, re-upload pages, surveys) |
| **Hugging Face (HF)** | A service hosting machine-learning data and models |
| **Kaggle** | A data-science competition service where data is also shared; downloadable with a free account and an API token |
| **Zenodo / figshare / Mendeley Data** | Free services for publishing research data, with DOIs |
| **DOI** | A permanent identifier for papers and data |
| **ISO 639-3** | Three-letter language codes: `eng` English, `jpn` Japanese, `cmn` Mandarin, `mul` several languages without a breakdown, `zxx` no linguistic content |
| **KuralHub** | A survey of SER datasets by language. It is a third-party source, so values supported only by it count as not yet confirmed |

### 3.5 License terms

A license states how far data may be used. The explanations here are general, not legal advice.

| Term | Plain explanation |
|---|---|
| **CC (Creative Commons)** | A system that expresses conditions of use with fixed symbols |
| **BY** | Usable if the author is credited (attribution) |
| **NC** | Non-commercial use only; no use in commercial products |
| **SA** | Derived works must be shared under the same terms |
| **ND** | No modification |
| **CC0** | Rights waived; free to use |
| **ODbL / ODC-By** | Licenses for databases, requiring attribution or share-alike |
| **MIT / Apache-2.0** | Permissive software licenses (free use with attribution) |
| **GPL** | A software license that strongly requires sharing under the same terms; rare for data |
| **SPDX identifier** | The official short name of a license (e.g. `CC-BY-4.0`), used to avoid spelling variants |
| **LicenseRef-...** | The DB's own names for custom terms that SPDX does not cover (section 9) |
| **Copyleft** | Requiring users to share under the same terms (SA, GPL) |
| **Permissive** | Almost free use, with attribution at most |
| **Redistribution** | Passing received data to others or publishing it elsewhere; often not allowed |

## 4. What is in the DB

### 4.1 Folder map

```
ser_dataset_db/
├── README.md                  summary for developers (read first by AI assistants)
├── docs/manual.md             this document
├── data/                      * authoritative data (8 CSV files)
├── schema/                    column definitions, allowed values, table keys
├── views/                     copies for reading (generated from data/)
├── measurements/              measured results of recipes (JSON); text_link/ holds transcript checks for 5.4.2
├── reports/                   detailed investigations of single datasets, with verification
├── sheet_import/              the frozen original spreadsheet
├── tools/                     programs for checking, updating and measuring
├── .env.example               template for machine-specific settings (copy to .env, git-ignored)
├── LICENSE                    MIT, for this database and its tools (not for the datasets it describes)
└── .claude/skills/            the maintenance workflow for Claude Code
```

### 4.2 The 8 tables (`data/`)

| File | One row is | Rows |
|---|---|---|
| [datasets.csv](../data/datasets.csv) | **one dataset** (the central table) | 322 |
| [evidence.csv](../data/evidence.csv) | the **source** of one value in datasets | 4,277 |
| [aliases.csv](../data/aliases.csv) | another name (official name, short name, former name, recipe name, ...) | 375 |
| [relations.csv](../data/relations.csv) | a relation between datasets | 44 |
| [recipes.csv](../data/recipes.csv) | one ESPnet recipe | 94 |
| [recipe_labels.csv](../data/recipe_labels.csv) | recipe x label | 596 |
| [benchmark_membership.csv](../data/benchmark_membership.csv) | a recipe that is part of a benchmark | 16 |
| [annotations.csv](../data/annotations.csv) | dataset x annotation other than emotion labels (transcripts, speaker traits, dialogue acts, ...) | 178 (`anad` 3, `audiospeechsentiment` 2, `baser` 4, `berst` 9, `brytserc` 1, `casia` 3, `cbesd` 5, `csemotions` 2, `dailytalk` 6, `eesc` 6, `emis` 5, `emogator` 2, `emospeech_keywords` 5, `emotale` 5, `emotional_ema` 8, `emouerj` 3, `emovoicedb` 5, `eseravd` 3, `harper_valley_bank` 19, `hindi_ser_vishlb` 4, `iesc` 4, `javanese_ser_2black0` 3, `jnv` 6, `legov2` 6, `lithuanian_emotion_db` 2, `maserc` 4, `mav` 3, `rml_emotion` 4, `saraiki_ser` 1, `ses_ed` 3, `ses_sd` 3, `sitb_osed` 4, `syntact` 6, `talromur3` 5, `telugu_emotion_kaggle` 4, `ua_ser` 6, `usc_emo_mri` 5, `utemo` 4, `whiser` 5; more to come) |

Relations by type: `contains` 15, `distinct_from` (similar names, different datasets) 12, `subset_of` 7, `possibly_same_as` (suspected identity) 4, `version_of` 3. Of the 94 recipes, 93 are for a single corpus (`single_corpus`) and 1 combines several corpora (`multi_corpus`).

### 4.3 How the tables connect

```
datasets ──(dataset_id)── evidence     source of each value
   │       ──(dataset_id)── aliases      other names
   │       ──(dataset_id)── relations    relations to other datasets
   │       ──(dataset_id)── annotations  non-emotion annotations (each row has its own source)
   └── recipes(dataset_id) ── recipe_labels (counts per label)
          └── benchmark_membership (make-up of benchmarks)
```

### 4.4 What counts as one row

- One row is the original (first published) dataset. Plain re-uploads on Hugging Face, Kaggle and the like are not rows; they go into the original's aliases.
- Anything whose content differs (re-split, subset, new labels) is a separate row linked with `relations`.
- When two rows turn out to be the same, one becomes `excluded` (duplicate) and they are linked with `possibly_same_as`. IDs are never deleted.
- Datasets without audio (text only, features only) are kept as `excluded` to record what was found.

## 5. Reading the `datasets` table

### 5.1 Columns to look at first

Each row has about 45 columns; start with these.

| Column | Meaning | Example (ravdess) |
|---|---|---|
| `dataset_id` | stable ID | `ravdess` |
| `name` | name | RAVDESS |
| `espnet_status` | status (section 8) | `implemented` |
| `languages` | languages (ISO 639-3, `;`-separated) | `eng` |
| `recording_context` | recording setting or medium | `acted` |
| `speech_production` | how the audio was produced (5.4.1) | `acted` |
| `label_basis` | how the labels were made (5.4.1) | `intended` |
| `text_emotion_link` / `lexical_confound` | how the spoken text relates to the labels, and how far the words alone give the label away (5.4.2) | `parallel` / `none` |
| `license_spdx` / `license_class` | license and its class (section 9) | `CC-BY-NC-SA-4.0` / `noncommercial` |
| `access_method` | how to obtain it (section 10) | `direct_download` |
| `raw_audio_available` | whether raw audio is distributed | `true` |
| `n_utt_reported` / `hours_reported` / `n_speakers_reported` | utterances, hours and speakers stated by the sources | 1440 / 1.5 / 24 |
| `labels_discrete_reported` | categorical emotion labels in the sources | calm;happy;sad;angry;... |
| `dimensional_attributes` | axes of dimensional emotion, or `none` | `none` |

### 5.2 "Reported" vs "measured"

- `*_reported`: figures **stated by the paper or distribution page** (published values).
- `*_measured`: figures **we counted after downloading** (measured values).

They can differ, and the difference itself is useful information. Recipes drop very short clips and the like, so recipe counts and published counts usually differ. Disagreements are listed in [views/discrepancies.csv](../views/discrepancies.csv).

### 5.3 Note columns

- `status_note`: notes on the status (why it is a candidate, what to watch out for)
- `license_note`: gist of the license wording
- `language_note`: dialects and how the language value was decided
- `label_basis_note`: details of how labels were made (5.4.1)
- `lexical_confound_note`: what the `lexical_confound` value is based on (5.4.2)
- `paralinguistic_signal_note`: what was listened to and what was heard (5.4.3)
- `notes`: our own notes
- `sheet_notes`, `annotations_other`, `sheet_verified`: **original text of the spreadsheet**; never changed. `sheet_verified` is the spreadsheet's mark for "checked by hand" and is not used for decisions

### 5.4 Who made the labels (`label_source`, `label_verification`)

Records who assigned the main labels (those in `labels_discrete_reported` and `dimensional_attributes`). Both have evidence rows for each value. Empty means not checked.

- `label_source`: `human` (people only) / `automatic` (models etc. only) / `mixed` (automatic labels reviewed by people, or a mix) / `synthesis_specified` (synthetic audio whose label is the emotion specified to the synthesiser)
- `label_verification`: whether people checked the labels: `human_reviewed` (the source says people reviewed automatic labels) / `listener_validated` (instructed labels confirmed or filtered by a listening test; the label stays the instructed one) / `none` (the source says there was no review) / `unknown` (the sources say nothing) / `NA` (nothing to review, e.g. labels that are listeners' own judgements)
- Examples: `harper_valley_bank` is automatic (the paper says the labels came from an API) with no description of verification (`unknown`). `nonverbaltts` is emotion2vec+ classification reviewed by annotators (`mixed`, `human_reviewed`).
- Automatic labels do not remove a dataset from `candidate` (8.3). Whether to train on such labels or only evaluate is a recipe-side decision, recorded in `recipes.notes`.
- Filled for datasets whose recipe review is done; the rest are filled one by one during review, from primary sources.

### 5.4.1 How the audio was produced vs. how the labels were made (`speech_production`, `label_basis`)

"How the audio was produced" and "how the labels were made" are different things and are recorded in separate columns. Acted speech can carry labels that listeners perceived (and vice versa). Perceived labels are especially valuable, so they are recorded in a searchable form.

| Column | Values (`;`-separated when several apply) |
|---|---|
| `speech_production` | `acted` (acting: an instructed emotion portrayed, including scripted film and drama performances) / `elicited` (induced by stimuli or tasks) / `spontaneous` (natural speech) / `read` (reading without an emotion instruction) / `synthetic` |
| `label_basis` | `intended` (the emotion the speaker was told to portray) / `perceived` (the emotion listeners perceived) / `self_reported` (the speaker's own report) / `context_inferred` (from the scene, script or meaning of the words) / `automatic` (a model's estimate); `none` if there are no emotion labels |
| `label_basis_note` | free text: number of raters, what raters saw or heard (audio only, with video, transcript), how ratings were combined (majority, mean), which label set is the main one, listening-test details |
| `recipes.label_basis_used` | which kind of label the recipe actually uses, for datasets that ship labels made in several ways |

- `recording_context` stays as the column for the setting or medium (studio, YouTube, TV, film, ...). Do not infer how speech was produced from it.
- When instructed labels were confirmed by a listening test, or only agreeing clips were kept, the label stays `intended` and `label_verification=listener_validated`.
- Filled during recipe review. Rows not yet reviewed are empty (not checked).

### 5.4.2 Text and labels (`text_emotion_link`, `lexical_confound`)

If the words spoken already give the label away, a model can learn the words instead of the voice (shortcut learning). Datasets whose labels follow only the words are excluded (`labels_from_text_content`). Datasets with real paralinguistic information but some correlation with the words may be used, with care. These columns flag that correlation so that the actual data gets checked; they do not decide anything on their own.

| Column | Values |
|---|---|
| `text_emotion_link` (`;`-separated) | `parallel` (the same sentences in every emotion) / `neutral_text` (semantically neutral sentences) / `emotion_specific_text` (content matches the emotion) / `unrelated_text` (sentences assigned without regard to the emotion) / `dialogue_script` (lines of a film, drama or written dialogue) / `unscripted` (conversations, broadcasts, improvisation) |
| `lexical_confound` | `full` (the text determines the label: each sentence under one emotion only) / `strong` (most utterances) / `moderate` (a substantial part) / `weak` (a small part or a weak link) / `possible` (no direct evidence, but a documented reason to suspect it, e.g. unscripted speech, labels assigned from context or with the transcript visible) / `none` (ruled out by design: parallel, neutral or emotion-independent sentences, or no words) |
| `lexical_confound_note` | free text: what the value is based on (design in a source, sentence-label counts, a text-only classifier) and its scope (e.g. "English half only") |

- A value needs a clear source: a design statement in the paper or official documentation, or a measurement (counting sentences per emotion in transcripts). Never fill a value by guessing. Measuring is optional and can be costly: if the sources are silent and no cheap check exists, write `unknown` (checked, the sources do not say) and, when there is a documented reason to suspect a correlation, set `lexical_confound=possible` with the reason in `lexical_confound_note`. Leave the cell empty only when the dataset has not been looked at.
- Record anything with even a small chance of correlation (`possible` or above), because the flag is what prompts someone to look at the data later. Use `none` only when the design rules it out.
- Whisper transcripts are a measurement, but say in the evidence note that no person checked them. Measurement outputs go under `measurements/text_link/`.
- Filled during recipe review. Rows not yet reviewed are empty (not checked).

### 5.4.3 Does the voice carry the expression? (`paralinguistic_signal`)

Labels can be correct and the voice still carry little of the labelled expression (a flat reading of lines per emotion, amateur speakers in a classroom). Such data can mislead a model that is meant to learn from the voice. This column records what listening found; it does not decide whether to use the data.

| Value | Meaning |
|---|---|
| `clear` | The voice carries the labelled expression (shown by a listening test or by the maintainer's listening) |
| `varies` | Clear for some speakers or classes, weak for others |
| `weak` | The expression is weak in what was heard |
| `doubtful` | The voice may carry no expression of the labelled emotion (e.g. a flat reading of lines) |

- Fill it only from listening (a listening test, or the maintainer's listening, recorded with `source_type=user`). The number of clips heard and what was heard go in `paralinguistic_signal_note`. A light listening (a few clips) is recorded as such and is not a measurement.
- Empty means not judged. Do not fill it from the label source, the recording setting or the sentences.

### 5.5 Annotations other than emotion labels (`annotations.csv`)

Transcripts, speaker traits, dialogue acts, audio quality, questionnaires and other information beyond the emotion label are recorded one row per dataset x item. `datasets.annotations_other` (spreadsheet text) is kept unchanged, and new information goes into this table.

- Columns: `item`, `description`, `annotator` (`human` / `automatic` / `mixed` / `unknown`), `unit` (`utterance` / `segment` / `word` / `recording` / `conversation` / `speaker` / `dataset`), `used_in_recipe`
- Each row carries its own source (`source_type`, `source_ref`, `locator`, `checked_on`, `checked_by`). `evidence.csv` is for values of `datasets` columns, so annotation sources are not mixed into it.
- `used_in_recipe=true` is allowed only for `implemented` datasets (checked by the validator).
- Items are added when recipes are registered, from what primary sources confirm.

### 5.6 Kinds of label (`recipe_labels.label_type`)

`categorical` (categorical emotions, speaking styles, ...) / `polarity` (sentiment) / `intent` (intents, dialogue acts) / `dimensional` / `other`. Polarity and intent labels are not mapped onto the common 7 labels: `common7=none`, `mapping_type=outside_common7`. The 21 rows of `recanvo` are left empty (not checked) because its labels span emotions and requests or intents.

### 5.7 All column definitions

Types, meanings and allowed missing values of every column are in [schema/columns.csv](../schema/columns.csv), allowed values in [schema/enums.csv](../schema/enums.csv), and table keys in [schema/tables.csv](../schema/tables.csv).

## 6. Evidence

### 6.1 Why keep evidence

A value alone cannot answer "is that really true?" later. So every important value gets **an evidence row** recording its source, the date checked, who checked it, and its strength.

### 6.2 What an evidence row holds

| Column | Meaning |
|---|---|
| `value` | the value the evidence supports |
| `source_type` | kind of source (ranked by strength, 6.3) |
| `source_ref` | the source (URL, file path) |
| `locator` | where in the source (a short quote or place, 25 words at most) |
| `checked_on` / `checked_by` | date checked and who checked (`claude` / `user` / `script`) |
| `is_canonical` | `true` for the evidence of the current value; exactly one per dataset x column |
| `status` | `current` / `superseded` (replaced by newer evidence) / `conflicting` (sources disagree, undecided) |

Columns that need evidence: `languages`, `recording_context`, `vocal_content`, `license_spdx`, `access_method`, `raw_audio_available`, `n_utt_reported`, `hours_reported`, `n_speakers_reported`, `n_files_release_measured`, `n_speakers_measured`, `labels_discrete_reported`, `dimensional_attributes`, `espnet_status`, `status_reason_codes`, `label_source`, `label_verification`, `speech_production`, `label_basis`, `text_emotion_link`, `lexical_confound`, `paralinguistic_signal`.

### 6.2.1 Recording when something was checked

Every one of the 4,277 evidence rows has a date checked (`checked_on`, 2026-10-10 to 10-26). But **the date is when the source was looked at**, not a guarantee that it is still true; distribution pages and licenses can change. For rows from the original spreadsheet (`source_type`=`sheet`), the date 2026-10-12 is the import date, not a date when anyone checked the content.

The overview [views/datasets_wide.csv](../views/datasets_wide.csv) adds these columns per dataset (generated from the evidence):

| Column | Meaning |
|---|---|
| `license_checked_on` / `license_source_type` / `license_checked_by` | date, kind and checker of the license evidence |
| `access_checked_on` | date the access method was checked |
| `oldest_checked_on` / `latest_checked_on` | oldest and newest date among the row's current evidence |

Old dates and `sheet` sources have priority for re-checking.

### 6.3 Strength of sources

Strongest first.

| Rank | `source_type` | Content |
|---|---|---|
| 1 | `user` | decisions and explanations of the project maintainer |
| 2 | `measured` | values we counted or access we tried |
| 3 | `primary` | the authors' paper, official page, LICENSE |
| 4 | `project_doc` | internal documents whose source cannot be pinned down |
| 5 | `secondary` | third-party statements (Kaggle, re-upload pages, surveys) |
| 6 | `sheet` | values of the original spreadsheet |

The 4,277 evidence rows by source type: primary 2,100, sheet 572, measured 539, project_doc 435, user 358, secondary 273.

### 6.4 When a new fact appears

The old evidence is kept and marked `superseded`, and a new row is added. The history remains, so one can explain "it used to say this, and this source corrected it". When equally strong sources disagree and neither can be preferred, two or more `conflicting` rows are kept and the datasets cell is also `conflicting` (e.g. the licenses of EmoDB, Baum-1 and TurEV-DB). When one value can be preferred for a stated reason, it becomes canonical and the other stays as a non-canonical `conflicting` row.

### 6.5 A real example (the RAVDESS license)

| Evidence | Value | Source type | Status |
|---|---|---|---|
| `ravdess/license_spdx/01` | CC-BY-NC-SA-4.0 | sheet (original spreadsheet) | superseded |
| `ravdess/license_spdx/02` | CC-BY-NC-SA-4.0 | primary (Zenodo record) | **current / canonical** |

Even though the value is the same, the record shows that the spreadsheet value was replaced by a primary source.

### 6.6 Principles

- Write nothing the sources do not say. Never guess URLs or titles.
- Never use measured values as evidence for "reported" columns (or the reverse).
- The only basis for measured counts, hours and speakers is `measurements/<recipe>.json` and the downloaded files themselves.

## 7. Writing missing values (empty, unknown, NA, none)

"No value" comes in four kinds, which are **never mixed**.

| Written as | Meaning | Example |
|---|---|---|
| (empty) | **not checked yet** | license not investigated |
| `unknown` | checked, but the sources do not say or it cannot be decided | the distributor states no license |
| `NA` | does not apply | recipe columns of a dataset that is not implemented |
| `none` | checked, and there is none | confirmed there are no dimensional labels |

Which ones a column accepts is fixed in the `nulls` column of `schema/columns.csv`. Licenses also have the value `none_stated` (no license statement found).

## 8. Status (`espnet_status`)

### 8.1 The five statuses

| Status | Meaning | Count |
|---|---|---|
| `implemented` | an ESPnet recipe exists | 93 |
| `candidate` | candidate for addition: has audio and labels usable for classification, and can probably be obtained | 141 |
| `needs_decision` | only the project maintainer can decide (cost, terms of use, application wording) | 7 |
| `deferred` | not confirmed: the distributor does not respond, the access route is unknown, etc. | 35 |
| `excluded` | not used, for a clear reason | 46 |

### 8.2 Only clear reasons justify `excluded`

Exclusion is allowed only when:

- there is no audio (text only, paper only, features only, code only)
- it redistributes another dataset (`redistribution_of_existing_corpus`) or duplicates a row
- the labels cannot be used for classification
- the labels follow the spoken content (the meaning of the sentence) rather than the voice (`labels_from_text_content`); only when confirmed by listening and decided by the maintainer
- it cannot be obtained because of nationality or residence restrictions
- distribution is not allowed

The 46 excluded rows break down as: text only 11, paper only 9, redistribution of an existing corpus 9, regional restriction 7, features only 6, and others (unidentifiable, duplicate, code only, not distributable, unsuitable labels, distributor unreachable, ...).

### 8.3 Not reasons to exclude (important)

Policy set by the maintainer on 2026-10-14. These are **not reasons to exclude**:

- size, small or large
- manual access steps (application, signature, login, purchase); the maintainer can be asked to do them
- being on Kaggle (a free account and token suffice)
- the kind of label (sentiment, intent, dimensional values, speaking style)
- automatic labels, synthetic speech

Such datasets stay `candidate`, with caveats in `status_note`. The aim is not to drop something because it is laborious, but to record that it is laborious so it can be decided later.

### 8.4 Reason codes (`status_reason_codes`)

Every row except `implemented` has reason codes (`;`-separated). The most common is `unexamined` (implementation not yet considered), on 158 rows. The list and meanings are the `reason_code` rows of [schema/enums.csv](../schema/enums.csv).

## 9. Licenses

### 9.1 Two columns

- `license_spdx`: the conditions in the sources mapped to an SPDX identifier.
- `license_class`: a rough class derived **mechanically** from the identifier. Not a legal judgement.

### 9.2 `license_class` values and counts

| Class | Meaning | Count |
|---|---|---|
| `open` | permissive (attribution at most): CC-BY, CC0, MIT, ... | 96 |
| `noncommercial` | non-commercial only (CC-BY-NC, ...) | 38 |
| `research_only` | custom terms limited to academic or research use | 55 |
| `restricted` | restricted or paid | 12 |
| `other` | other than the above | 5 |
| `none_stated` | no license statement found | 25 |
| `unknown` | examined but undecidable | 23 |
| `conflicting` | sources disagree | 4 |
| (empty) | not investigated yet | 64 |

### 9.3 Four names for custom terms

Terms not covered by SPDX get one of these, with the gist of the wording in `license_note`:

- `LicenseRef-custom-research-only`: custom academic or research-only terms
- `LicenseRef-proprietary-restricted`: proprietary terms such as payment or contracts
- `LicenseRef-other`: anything else
- `LicenseRef-citation-request`: no license text, only a request to cite the paper, which the project treats as the terms of use by the maintainer's decision for that dataset (class `open`; the decision and the wording are in `license_note`)

### 9.4 Before using a dataset

- Even when `license_class` is `open`, **the data's license** and **the license of bundled code** may differ. Always read `license_note` and the primary source.
- The scope of "research only" or "non-commercial" (publication, releasing models, redistribution) differs between terms. The DB does not interpret it.
- A license written by a re-uploader (on Kaggle etc.) is not necessarily the authors' terms.

## 10. Access methods (`access_method`)

| Value | Meaning | Count |
|---|---|---|
| `direct_download` | directly downloadable without authentication | 131 |
| `free_account_required` | free account (registration) required | 17 |
| `gated_click_through` | consent click or similar required | 7 |
| `request_form_or_email` | request by application form or e-mail | 59 |
| `signed_agreement` | signed agreement required | 30 |
| `paid_or_membership` | paid or membership | 9 |
| `unofficial_mirror_only` | only unofficial mirrors | 0 |
| `unavailable` | cannot be obtained | 7 |
| `unknown` | unknown | 12 |
| (empty) | not checked | 50 |

Roughly, `direct_download`, `free_account_required` and `gated_click_through` are "available now", and `request_form_or_email` and `signed_agreement` "need a procedure".

## 11. Current figures (2026-10-26)

### 11.1 Status x license class

| Status | open | NC | research | restricted | other | none stated | unknown | conflicting | not checked | total |
|---|---|---|---|---|---|---|---|---|---|---|
| implemented | 61 | 10 | 11 | 1 | 2 | 5 | 1 | 2 | 0 | 93 |
| candidate | 20 | 23 | 34 | 9 | 3 | 15 | 4 | 2 | 31 | 141 |
| needs_decision | 2 | 1 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 7 |
| deferred | 0 | 1 | 7 | 0 | 0 | 1 | 7 | 0 | 19 | 35 |
| excluded | 13 | 3 | 1 | 0 | 0 | 4 | 11 | 0 | 14 | 46 |

(NC is noncommercial.)

What this shows:

- Of the 93 implemented datasets, 61 have open terms (`open`).
- Of the 141 candidates, 12 are `open` and `direct_download` (available now): the first group to implement next.

### 11.2 Properties of the data

- **Recording context** (`recording_context`; 67 not checked): acted 115, spontaneous conversation 23, multi-source web 21, YouTube 14, TV show 14, affect elicitation 13, film 12, read speech 8, synthetic 8, other 8, human-agent interaction 7, podcast 4, and others.
- **Languages**: 70 codes. English (eng) 88, Mandarin (cmn) 37, Korean (kor) 16, Spanish (spa) and German (deu) 14 each, French (fra) 12, Japanese (jpn) 11, multilingual (mul) 16.
- **Raw audio**: distributed 186, not distributed 29, unknown 4, not checked 103.
- **Datasets with dimensional emotion labels**: 30.
- **Training and evaluation of ESPnet recipes**: done (`evaluated`) 17, not run (`not_run`) 77.
- **Speech production and label basis** (filled during recipe review): filled for 43 datasets; perceived labels (`perceived`, alone or with others) on 13.
- **Intent and dialogue-act data**: 12 (SLURP, Timers and Such, Fluent Speech Commands, Snips/Sonos, STOP, MInDS-14, Speech-MASSIVE, ITALIC, DIHANA, SpokenWOZ, Harper Valley Bank, SLUE-HVB).
- **Coverage check**: all 28 corpora in Table I of the MSP-Podcast paper (arXiv 2509.09791v1) are included.

### 11.3 How the data was collected

On 2026-10-14, 158 datasets were added from surveys (SuperKogito's list, EmoBox, KuralHub, ...), searches of Hugging Face, Zenodo, Kaggle, Mendeley, figshare, GitHub and OpenSLR, and corpora known from the literature. For added rows, access terms, licenses and labels were checked in primary sources as far as possible.

## 12. Using the DB (looking things up)

### 12.1 The easiest way: open it in a spreadsheet

Open [views/datasets_wide.csv](../views/datasets_wide.csv) in Excel, Google Sheets or LibreOffice. One row per dataset; use filters to narrow it down. Main columns:

- `dataset_id`: ID
- `status`: status (= `espnet_status`)
- `reasons`: reason codes
- `license_class`, `access_method`, `raw_audio_available`
- `speech_production`, `label_basis`, `label_basis_note`
- `text_emotion_link`, `lexical_confound`, `lexical_confound_note`
- `paralinguistic_signal`, `paralinguistic_signal_note`
- `recipe`, `n_total_recipe`, `hours_total_recipe`: for implemented datasets, the recipe and its measured count and hours
- `common7_covered`, `common7_missing`: which of the common 7 labels (angry, disgust, fear, happy, neutral, sad, surprise) the data has or lacks
- `benchmarks`: benchmarks it belongs to

The first 15 columns (Verified to ESPnet Implemented) have the original spreadsheet's names.

> `views/` is a generated copy. Edits there are lost the next time it is regenerated. Fix `data/` instead.

### 12.2 Example 1: look up a dataset

In a terminal, in the DB folder:

```bash
grep -i ravdess views/datasets_wide.csv
```

To see all fields of a row vertically:

```bash
python3 tools/db.py get datasets ravdess
```

### 12.3 Example 2: see the source of a value

Open [data/evidence.csv](../data/evidence.csv) and filter `dataset_id` = `ravdess` and `field` = `license_spdx`. The source URL (`source_ref`), date checked and checker are shown.

```bash
grep '^ravdess/license_spdx' data/evidence.csv
```

### 12.4 Example 3: see disagreements

[views/discrepancies.csv](../views/discrepancies.csv) lists the DB's current value next to values from other sources. Rows where spreadsheet or survey values were corrected from primary sources show the old values here.

### 12.5 Example 4: ask an AI assistant

Assistants working on this project look up this DB before searching the web. Ask "what Japanese emotional data is there?" or "which openly licensed datasets are not yet implemented?" and the answer comes from the DB. For important decisions, the answer should say that evidence whose `source_type` is `sheet`, `project_doc` or `secondary` needs confirming.

## 13. Maintenance (updates and checks)

### 13.1 Everyday commands

Run in the DB folder with the system Python.

| Command | What it does |
|---|---|
| `python3 tools/validate.py` | checks everything, including the ESPnet branch, recipes and measurements |
| `python3 tools/validate.py --offline` | checks only the DB, without reading ESPnet |
| `python3 tools/views.py` | regenerates `views/` |
| `python3 tools/db.py get\|set\|add\|fmt` | view, change or add a row; reformat the CSV files |

Measurements use `tools/measure.py`, and `tools/sync.py` copies them into the recipe table (steps in the README, "Validation and updates"). The full maintenance workflow, including verification of incoming reports, is in `.claude/skills/maintaining-ser-dataset-db/SKILL.md`.

### 13.2 What the checks cover

- CSV format (UTF-8, row order), column types and allowed values
- keys and foreign keys (no rows pointing to missing rows)
- evidence rules (one canonical evidence row per value, no mixing of measured and reported values, ...)
- whether `implemented` rows match the ESPnet recipes
- whether `recipes.csv` and `recipe_labels.csv` match `measurements/*.json`
- whether `annotations.csv` points to existing datasets, `used_in_recipe=true` only for implemented ones, and `label_verification` is not set without `label_source`
- whether `views/` is up to date

### 13.3 Rules for changes

- Every value change gets an evidence row.
- One commit per dataset or per checking session. The commit message (in English) says **what was wrong** and what the evidence was.
- The hook runs the checks automatically before each commit; the commit is refused if they fail. Never skip the checks (`--no-verify`).
- Stage files by name; never `git add -A` or `git add .`.
- Committed `dataset_id`s are never changed (if one must change, keep the old ID as an alias).

### 13.4 Division of work with recipe authors

Findings made while implementing recipes (label problems, split peculiarities, ...) are not written into the DB directly. They are handed to the DB maintainer as a DB update report, and the DB maintainer verifies them against primary sources and the audio before recording them with evidence. The exception is the automatic measurements and recipe-table updates produced by `measure.py` and `sync.py`.

## 14. Human checks of licenses

### 14.1 Why

Most license evidence was gathered by Claude or automated processing (`checked_by` is `claude` or `script`), some of it mechanically from API fields or cards, so human confirmation is desirable.

### 14.2 How

Instead of one bulk check, **each time a recipe is implemented and reviewed, the maintainer looks at that dataset's license page**. The result is added as an evidence row with `checked_by=user`. Current license evidence checked by the maintainer exists for 3 datasets (`iesc`, `recanvo`, `uftbesd`).

## 15. Limitations (honestly)

Reports state what is not done as well as what is.

### 15.1 Not yet confirmed

- **The DB lags behind the ESPnet implementation**: the ESPnet recipe branch has recipes that are not yet in `recipes.csv` (`validate.py` lists them as a warning, not an error; they are registered one by one after review).
- **Minimum clip length changed from 0.5 s to 0.2 s** (ESPnet commit 96a54519743, 2026-10-17). `min_wav_duration` in `recipes.csv` is 0.2 for all recipes, but for recipes registered before the change, `n_train_filtered` and `n_valid_filtered` are still the old measurements (counted with the 0.5 s minimum). Not yet re-measured.
- **Human checks of licenses have barely started** (see 14.2). The licenses in the DB are mostly primary sources checked by Claude.
- **28 rows supported only by a third-party survey (KuralHub)** have not had their access checked in primary sources. Many are data from older papers, listed as "on request".
- **Some distributors did not respond**, so some rows could not be checked (`amigos`, `casia`, `cheavd`, `belfast`, `emotion_origlia2010`, `usoms`, `eyase`).
- **The 35 `deferred` rows** still need their real access routes investigated.
- **Empty (not investigated) values remain**: license empty for 64, access method empty for 50, recording context empty for 67.
- **Not yet surveyed**: CATSLU, dialogue acts such as MRDA, SwDA and AMI, ATIS audio, SLURP in other languages, intent data in other languages.

### 15.2 Limits by nature

- The DB **organises public information**; it is not legal advice. License classes are mechanical classifications.
- "A dataset exists" and "you may use it" are different. Always read the primary source and the original terms before use.
- Whether `measurements/` still matches the local copies of the data is not checked automatically.
- Whether a dataset has emotion labels is sometimes hard to tell from the paper alone; unclear cases were downloaded and checked (e.g. Expresso).

### 15.3 MSP-Podcast terms

MSP-Podcast is for internal non-commercial research only, may not be redistributed, and requires citing Lotfian & Busso (2019). Its standard label set is the 8 classes including contempt.

## 16. Talking points for a progress report

### 16.1 Outline (1-2 minutes)

1. **What was built**: an evidence-backed ledger of SER and paralinguistic datasets. 322 datasets, 4,277 evidence rows.
2. **Why**: to stop re-researching dataset conditions (license, access) every time, and to keep the basis for cross-corpus evaluation.
3. **Reliability measures**: each value records its source, date and checker, and a machine checks the rules. Unknowns are written as unknown, never filled by guessing.
4. **Link to the implementation**: the 94 ESPnet recipes are measured into the DB, distinguishing implemented, candidate and deferred datasets (the recipe branch keeps growing, and new recipes are registered after review; 15.1).
5. **Next**: human license checks with each recipe, investigating the 35 deferred rows, surveying uncovered areas.

### 16.2 Things to show

- Open [views/datasets_wide.csv](../views/datasets_wide.csv) in a spreadsheet and filter it (e.g. `status`=candidate, `license_class`=open, `access_method`=direct_download -> 12 rows).
- An evidence example: filter [data/evidence.csv](../data/evidence.csv) on `ravdess` and `license_spdx` to show how the spreadsheet value was replaced by the Zenodo primary source.

### 16.3 Expected questions

| Question | Answer |
|---|---|
| Why CSV instead of the original spreadsheet? | A spreadsheet cannot hold sources, history or checks. CSV under git keeps the change history and can be checked by machine |
| Is the information correct? | Every value has a source and a date; primary sources (papers, official pages) are the largest group (2,100 of 4,277 evidence rows). Final human checks (licenses) are still in progress |
| How was it collected? | 238 datasets from surveys, hosting services and the literature were added to the spreadsheet's 84; added rows were checked in primary sources |
| How many can be implemented? | 93 implemented, 141 candidates. Of the candidates, 12 are openly licensed and available now |
| What was excluded? | 46. Only for clear reasons: no audio, redistribution of existing data, duplicates, regional restrictions, etc. Effort and size are not reasons |
| Can the licenses be trusted? | The DB records the terms the sources state; it is not a legal interpretation. Read the original before use. Human checks are added one by one with each recipe |
| What next? | Human checks with each recipe, investigating the 35 deferred rows, adding uncovered areas (dialogue acts, intent data in other languages, ...) |

### 16.4 Things not to say

- "Everything has been checked by people" (human license checks cover only a few datasets, 14.2)
- "These licenses allow use" (the classes are mechanical, not legal judgements)
- "It covers every dataset in the world" (it covers what was surveyed; uncovered areas are listed in 15.1)

## 17. Troubleshooting

| Situation | What to do |
|---|---|
| validate fails | The message gives the file, line and cause. Usually missing evidence or a value outside the allowed list. If you cannot fix it, ask Claude |
| Cannot commit | The hook's checks failed. Run the same check by hand and fix the cause. Never bypass it with `--no-verify` |
| `views/` is outdated | Regenerate with `tools/views.py` (the checks also verify it is up to date) |
| Edited a CSV directly | Run `tools/db.py fmt`, then `validate.py` |
| Unsure whether a value is right | Filter `evidence.csv` on `dataset_id` and `field` and check `source_type` and `source_ref` |
| Want to undo a change | Do not run `reset` or similar on your own; ask first (operations that rewrite history need confirmation) |

## 18. Appendix

### 18.1 Main files

| File | Content |
|---|---|
| [README.md](../README.md) | summary for developers: tables, conventions, evidence rules, current state |
| [schema/columns.csv](../schema/columns.csv) | types and meanings of all columns |
| [schema/enums.csv](../schema/enums.csv) | allowed values (status, reasons, licenses, access, ...) |
| [schema/tables.csv](../schema/tables.csv) | file and key of each table |
| [data/](../data/) | authoritative data (8 CSV files) |
| [views/](../views/) | generated overview and disagreement lists |
| [measurements/](../measurements/) | measured results of recipes (JSON) |
| [reports/](../reports/) | saved investigation reports with verification |
| [sheet_import/README.md](../sheet_import/README.md) | origin and fingerprint of the original spreadsheet |
| [tools/](../tools/) | validate, views, db, measure, sync |

### 18.2 Updating this document

The figures are as of the date in section 11. When the DB changes, recount `data/*.csv` (the `doc_counts.py` script of the maintenance skill does this) and update the text.
