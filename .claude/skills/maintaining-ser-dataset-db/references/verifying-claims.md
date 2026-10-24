# Verifying claims

How to check a claim yourself before it goes into the DB. Use sources you opened and files you
measured. A web-search summary is not a source: it cannot be cited and has mixed up different
corpora before.

## Contents
- Sort the claims first
- Distributor pages and APIs
- Pages that are gone or render with JavaScript
- Papers
- The audio itself
- Duplicates and near-duplicates
- When your result matches the report exactly
- Recording what you checked

## Sort the claims first

Go through the report and put every statement in one of two groups:

1. **Decisions and human checks by the project maintainer**: "listened to the 58 pairs and they
   are the same sound", "checked the license on the page", "keep the recipe", "exclude these
   files", "do not use this dataset". Record these as they are, with `source_type=user` and
   `checked_by=user`. You cannot redo a listening test, and the decision is not yours to change.
2. **Everything else**: counts, durations, speaker numbers, formats, duplicate counts, license
   wording, what a card or paper says, how labels were made, URLs, dates, commit IDs. Check each
   one. Reports written by other sessions or people contain mistakes: miscounts, a search summary
   mistaken for a primary source, guesses written as facts.

## Distributor pages and APIs

| Host | Read | Look at |
|---|---|---|
| Kaggle | `curl -sL https://www.kaggle.com/api/v1/datasets/view/<owner>/<slug>` (JSON, no login needed) | `licenseName`, `currentVersionNumber`, `lastUpdated`, `creatorName`, `description` |
| Hugging Face | `curl -sL https://huggingface.co/api/datasets/<repo>`; raw files at `https://huggingface.co/datasets/<repo>/raw/<revision>/<file>`; `curl -sIL https://huggingface.co/datasets/<repo>` for renames | `sha` (pin it), license tag, `cardData`, file list, README, LICENSE, NOTICE |
| Zenodo | `curl -sL https://zenodo.org/api/records/<id>` | `metadata.license`, `metadata.version`, `files` |
| figshare | `curl -sL https://api.figshare.com/v2/articles/<id>` (and `.../versions`) | `license`, `version`, dates, `description` (HTML), `files` with size and md5 |
| GitHub | `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<file>` | README terms vs. LICENSE file |

The license can differ between the license field, the LICENSE file, the README text and a
NOTICE file (for example: LICENSE says MIT while the README says "research use only, send a
signed form"). Read all of them and write the difference into `license_note`. A re-uploader's
license field is not the authors' terms.

Descriptions contradict themselves more often than you would expect: two different utterance
counts in one description, a design formula whose product is not the number printed next to
it, a card that says 24-bit while every file is 16-bit, column names on the card that do not
exist in the data. Compute and compare instead of copying.

## Pages that are gone or render with JavaScript

- Wayback Machine: `https://web.archive.org/web/<timestamp>/<url>`; append `id_` to the
  timestamp (`.../web/20200501144342id_/<url>`) for the raw page. Page content can change between
  snapshots (copyright holders, prices, counts), so name the snapshot date in `locator`.
- If a report saved copies of sources with SHA-256 hashes, hash the saved copy and compare it
  with a fresh download before relying on it. Old Chinese pages may need `gb18030` decoding.
- Pages that render with JavaScript (some dataset portals) return an empty shell to curl. Open
  them in a browser tool and read the rendered text (`document.body.innerText`).

## Papers

- arXiv: `curl -sL https://arxiv.org/pdf/<id> -o paper.pdf && pdftotext paper.pdf paper.txt`,
  then `grep -n -i` for the dataset name and read the surrounding lines.
- The paper cited for a dataset is not always about that dataset. Count the obvious keyword
  (e.g. how often "emotion" occurs) before trusting a citation.
- When the paper and the release disagree (number of prompts, speakers, classes), record both.
- Read the references section for how others cite it; differing authors or years across papers
  are a sign the citation is borrowed.

## The audio itself

Find the corpus on disk through the recipe: `dataset/config.yaml` of the recipe names an
environment variable (`source_env_var`) whose value in the toolkit's environment is the corpus
directory. Then run, with a Python that has numpy and soundfile:

```bash
python <skill dir>/scripts/audio_audit.py inventory <corpus dir>
```

It prints files per extension, readable clips, formats (sample rate, channels, subtype), the
duration range and total hours, and byte-identical groups. Compare every number with the report
and with the distributor's description. Also count, with a few lines of Python, what the file
names or metadata files encode (speakers, genders, ages, emotions, sentence IDs) and whether any
speaker appears in more than one split.

The recipe's own counts (after its filters and exclusions) are in `measurements/<recipe>.json`
after running `tools/measure.py <recipe>` (see its docstring for the environment it needs).
Keep "the whole release" and "what the recipe uses" apart everywhere.

## Duplicates and near-duplicates

```bash
python <skill dir>/scripts/audio_audit.py dups <corpus dir> --out pairs.tsv
python <skill dir>/scripts/audio_audit.py dups <corpus dir> --against <other corpus dir>
```

- Byte-identical files come from `inventory`. For each group, check whether its files share a
  label, folder, speaker and split; groups that cross labels or splits matter most.
- `dups` finds the same sound with different bytes. Every listed pair crossing a label, a
  speaker or a split is worth reporting. Borderline pairs need a human to listen.
- Partial overlaps (the same recording cut at different points) are not found by this method.
  Say so instead of claiming there are none.

## When your result matches the report exactly

An exact match is reassuring only if you used a different method or looser settings than the
report. If your search had a tight filter, rerun it looser, or list which pairs each method
found and look at the difference. One registration missed a true duplicate pair because the
candidate filter was too strict, and then reported "same result as the report".

## Recording what you checked

- A measured value you confirmed: canonical `measured` row, with a note such as "re-measured from
  the release files on 2026-01-31; matches the report".
- A distributor statement: `primary`, with the quoted words in `locator`. Note when the document
  comes from a distributor or consortium rather than from the authors.
- A maintainer decision: `user`, `checked_by=user`.
- Not checked: leave it out, or say "not verified" in the evidence note or in the verification
  section of the saved report. Never put a file you did not open into `source_ref`.
