# Verifying claims

How to check a claim before it goes into the DB. Use sources you opened. A web-search summary is
not a source: it cannot be cited and has mixed up different corpora before. The DB does not count
or measure by itself (SKILL.md rule 1): a value either has a source that states it, or
stays empty (or provisional).

## Contents
- Sort the claims first
- Distributor pages and APIs
- Pages that are gone or render with JavaScript
- Papers
- The recipe readme
- When something looks wrong
- Recording what you checked

## Sort the claims first

Whatever the origin of a statement (a note, another session, a recipe readme, your own memory),
put it in one of three groups:

1. **Decisions by a project** ("use this dataset", "exclude these files", "keep the recipe").
   They are not dataset facts and do not belong in the DB; they belong in the user's `local/`.
2. **Facts about the dataset**: license wording, version, published counts, speakers, label sets,
   how the audio was produced and how the labels were made, listening tests, URLs, dates. Check
   each one in a primary source. Notes written by other sessions or people contain mistakes:
   miscounts, a search summary mistaken for a primary source, guesses written as facts.
3. **Findings of the implementation**: counts of the release, duplicates, formats, sentence
   overlap, observations from listening. Record them only as stated in the `## The data` section
   of the recipe readme (cited at its fork commit). A finding that is only in a note stays out of
   the DB; list it in the reply so the recipe author can add it to the readme. If a paper or page
   also states it, cite that source instead: the readme is cited only for what nothing but the
   implementation can show.

## Distributor pages and APIs

| Host | Read | Look at |
|---|---|---|
| Kaggle | `curl -sL https://www.kaggle.com/api/v1/datasets/view/<owner>/<slug>` (JSON) | `licenseName`, `currentVersionNumber`, `lastUpdated`, `creatorName`, `description` |
| Hugging Face | `curl -sL https://huggingface.co/api/datasets/<repo>`; raw files at `https://huggingface.co/datasets/<repo>/raw/<revision>/<file>`; `curl -sIL https://huggingface.co/datasets/<repo>` for renames | `sha` (pin it), license tag, `cardData`, file list, README, LICENSE, NOTICE |
| Zenodo | `curl -sL https://zenodo.org/api/records/<id>` | `metadata.license`, `metadata.version`, `files` |
| figshare | `curl -sL https://api.figshare.com/v2/articles/<id>` (and `.../versions`) | `license`, `version`, dates, `description` (HTML), `files` |
| GitHub | `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<file>` | README terms vs. LICENSE file |

The license can differ between the license field, the LICENSE file, the README text and a
NOTICE file (for example: LICENSE says MIT while the README says "research use only, send a
signed form"). Read all of them; record each as written (`conflicting` rows when they disagree)
and describe the difference in `license_note`. A re-uploader's license field is not the authors'
terms.

A number shown on a page as it stands (e.g. a file count displayed by the host) can be cited from
that page as `primary`. Do not compute a value the page does not print.

Descriptions contradict themselves more often than you would expect: two different utterance
counts in one description, a design formula whose product is not the number printed next to it.
Record both statements; do not pick one by your own reasoning (data-model.md, "Conflicting
sources").

## Pages that are gone or render with JavaScript

- Wayback Machine: `https://web.archive.org/web/<timestamp>/<url>`; append `id_` to the
  timestamp (`.../web/20200501144342id_/<url>`) for the raw page. Page content can change between
  snapshots, so name the snapshot date in `locator`. An archived copy of the official page is
  still the primary source.
- Pages that render with JavaScript return an empty shell to curl. Open them in a browser tool and
  read the rendered text (`document.body.innerText`).
- Do not weaken TLS checks (`curl -k`) to read a page. If a page cannot be read, the value stays
  empty, or `unknown` with the date of the attempt in the note.

## Papers

- arXiv: `curl -sL https://arxiv.org/pdf/<id> -o paper.pdf && pdftotext paper.pdf paper.txt`,
  then `grep -n -i` for the dataset name and read the surrounding lines.
- The paper cited for a dataset is not always about that dataset. Check the title and abstract
  before citing it, and before registering it as the dataset's paper.
- When the paper and the release disagree (number of prompts, speakers, classes), record both.
- Read the references section for how others cite it; differing authors or years across papers
  are a sign the citation is borrowed.

## The recipe readme

- Read it from the recipe branch: `git -C <recipe repo> show <branch>:egs3/<recipe>/cls/readme.md`.
- Find the commit that last changed it (`git log -1 --format=%H <branch> -- egs3/<recipe>/cls/readme.md`)
  and check that the commit is on the public fork (`git branch -r --contains <commit>`). Cite
  `https://github.com/itoten/espnet/blob/<commit>/egs3/<recipe>/cls/readme.md`.
- The readme's author is responsible for its numbers. Record what it states, in its own scope
  (whole release vs. what the recipe uses).

## When something looks wrong

If a note's claim, a readme's number and a primary source disagree, do not resolve it by
counting yourself. Record what the primary sources say, leave the rest empty, and tell the
maintainer what disagrees and where, so the recipe author can check and correct the readme.

## Recording what you checked

- A statement in a primary source: `primary`, with the quoted words in `locator` (25 words at
  most). Note when the document comes from a distributor or consortium rather than from the
  authors.
- A source you read that does not say: value `unknown`, `primary` row citing what you read,
  "not stated" in `locator`. Only after reading the whole document: an abstract, a landing page,
  a bot-check or script shell, or a pattern search that found nothing is not a reading, and the cell
  stays empty.
- The maintainer checked the source too: the same `primary` row with `checked_by=user` and the
  date in `note`.
- Not checked: leave it out. Never put a file you did not open into `source_ref`.
