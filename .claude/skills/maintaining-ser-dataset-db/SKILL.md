---
name: maintaining-ser-dataset-db
description: Maintains the speech emotion recognition (SER) dataset database, a public git repository of CSV tables in which every value carries an evidence row pointing to a source document. Reads new or rebuilt ESPnet recipes and their readmes, checks dataset facts against primary sources, registers datasets, sources, label sets, issues and evidence, validates, and commits. Use when told that a recipe was made or rebuilt, asks to add or check a dataset, asks to reconcile another team's research notes with the DB, or asks about a dataset's license, access, size, labels or sources.
---

# Maintaining the SER dataset DB

The DB is a **tertiary source**: it does not offer the truth about a dataset, but the way to the
sources where the truth can be checked: papers, distribution pages and license files published by
the dataset's authors (primary), and, for what only opening the release shows, the recipe
readme's `## The data` section (implementation). Each dataset is one row of `data/datasets.csv`;
each value of the columns that take evidence has a row in `data/evidence.csv` that points at a
document in `data/sources.csv`. `tools/validate.py` enforces the rules and runs as a pre-commit
hook.

All paths below are relative to the repository root. `<skill dir>` is this skill's directory
(`${CLAUDE_SKILL_DIR}` in Claude Code).

## First time in the repository

Read `README.md` (mission, principles, tables, evidence rules), then
[references/data-model.md](references/data-model.md). Then run:

```bash
python3 tools/validate.py     # must end with "0 error(s)"; a warning about sources without a publisher is normal
```

What you need to know about the surroundings:

- **Recipes** live in a separate toolkit repository (ESPnet), under `egs3/<recipe>/cls/` on a
  dedicated branch. `tools/egs3.py` says where that repository is expected and which branch is
  read. Read recipe files from the branch, not the working tree:
  `git -C <recipe repo> show <branch>:egs3/<recipe>/cls/readme.md`. The branch is published on
  the public fork `itoten/espnet`; only commits that are on the fork can be cited.
- **`local/`** is git-ignored and belongs to the user: which datasets they use and why, license
  groupings, label mappings. The DB's tools never read it, and you never write facts there.
- **The design is recorded** in `docs/design/` (decisions with their reasons). Change rules,
  columns or existing rows only when the project maintainer asks.

## Mission and principles

Mission: lower researchers' cost of investigating datasets. Five principles, none ranking above
the others (the README explains them):

- **Verifiability**: every value can be checked by anyone against a primary source.
- **Coverage**: as many datasets and as much information about them as possible.
- **Currency**: keep taking in new information and re-check old information.
- **Transparency**: show who checked what and when (a person, or only AI), and what is unknown.
- **Neutrality**: record facts only; no judgements such as "should be used", no choosing between
  disagreeing sources.

## Rules

1. **The DB creates no facts of its own.** Every value comes from a source someone else
   published. Do not count or measure anything yourself (no file counts, duplicate searches,
   transcriptions, listening). Values that need counting stay empty until the recipe readme
   states them.
2. **Every value has a source.** Evidence rows point at a source in `sources.csv`. Free-text
   columns (`notes`, `license_note`, `language_note`, `source_rights_note`) name their source in
   the text (`[aesdd_page]`); a fact no source states does not belong there.
3. **Source types.** `primary` is published by the dataset's authors or their organisation.
   `implementation` is the `## The data` section of a recipe readme, cited at a commit on the
   public fork; it is written by the recipe author and is a practical reference, not a research
   result. `secondary` (mirror, re-upload, survey, database) only when the primary source cannot
   be accessed; write why in `note`. The same URL may be primary for one dataset and secondary
   for another: two sources.
4. **A recipe readme is cited only for what the documentation does not state** and only opening
   the release shows (counts of the release, duplicates, what the files contain). If a paper,
   page or card states the same thing, cite that source even when the readme repeats it. Cite the
   readme with `commit <12 characters>; <heading>` as the locator. If the commit is not on the
   fork yet, leave the value empty and say so in the reply.
5. **Do not judge.** When sources disagree, add `conflicting` rows; the cell becomes
   `conflicting`; do not pick one. When wording is ambiguous, record it as written. Free text
   states facts, never advice ("should not be used", "poor data"). A fact that lets a reader
   judge ("each sentence is spoken in only one emotion") is written; the judgement ("may be
   confounded") is not.
6. **Empty, `unknown`, `none`, `NA` mean different things.** Empty = not checked; `unknown` = a
   source was read and does not say (cite the source you read, with "not stated" in `locator`);
   `none` = checked, there is none; `NA` = does not apply. A failed attempt at one moment
   (timeout, 404) is `unknown` with the date in the note.
7. **Listening tests: record that one exists, not its result.** `listening_test` is `reported`
   when a source describes a human listening test of the recordings (or the release distributes
   ratings, a `listener_ratings` annotation) and `not_stated` when the sources read say nothing.
   Do not write accuracy or agreement figures into a column: they depend on the number of
   classes, audio only or with video, how answers were combined and which clips were rated.
   Readers go to the source.
8. **Write only what a source supports.** No invented URLs, titles or numbers. Never cite a file
   you did not open. Reports from other sessions contain mistakes: check every claim against the
   source ([references/verifying-claims.md](references/verifying-claims.md)).
9. **Never delete history.** A new value gets a new evidence row; the old one becomes
   `superseded`. A `provisional` row (a value without a public source) is superseded when a real
   source is added.
10. **Keep "the whole release" and "what the recipe uses" apart.** The DB records the release as
    distributed, before any filtering; splits, filters and results are the recipe's business.
11. **Everything is public.** Files and commit messages are published worldwide. No personal
    names (refer to "the project maintainer"), e-mail addresses or machine-specific paths (use
    environment variable names; machine settings go in the git-ignored `.env`).
12. **Stay within the request.** Large sweeps (re-checking every license, re-probing every URL)
    and design changes are proposed, not started.

## Choose the workflow

- "A new recipe was made" / "this recipe was rebuilt" (a recipe name, maybe a commit) →
  **Register a recipe** below.
- "Add this dataset" / a survey of new datasets → **Add a dataset**.
- Another team's research notes that touch the DB → **Reconcile external notes**.
- A question about a dataset → **Answer a question**.
- "Check the sources of ..." (replace provisional values, check URLs, replace secondary
  sources) → **Check sources**.

## Register a recipe

Recipe sessions build recipes on their own and do not hand over a report. When you are told that
a recipe was made or rebuilt, read the recipe and its readme yourself.

```
- [ ] 1. Read the recipe, its readme and the current DB rows
- [ ] 2. Check that the readme commit is on the public fork
- [ ] 3. Check the dataset facts in primary sources
- [ ] 4. Take the findings of the implementation from the readme's "## The data" section only
- [ ] 5. Write and run the registration script (reglib)
- [ ] 6. Finish: views, validate, commit, push
- [ ] 7. Reply: registered / verified / left empty and why / open questions
```

**1. Read.** The recipe's `readme.md` and commit history on the recipe branch; the dataset's row
in `views/datasets_wide.csv`, its evidence rows (`grep '^<id>/' data/evidence.csv`), its
annotations, issues and label counts.

**2. Public fork.** Find the commit that last changed the readme and check that it is on the
public fork (`git -C <recipe repo> branch -r --contains <commit>`). If it is not, nothing from
the readme can be cited yet: register what primary sources support and say so in the reply.

**3. Dataset facts.** Open the distributor page or API and the paper and check license, version,
published counts (including counts per label), speakers and label sets; establish separately how
the audio was produced (acted, improvised, elicited, spontaneous, read, synthetic) and how the
labels were made (instructed, perceived by raters, self-reported, inferred from context,
automatic); look for a listening test. Citations in other sections of the readme are leads to
these sources, not sources themselves.

**4. Findings of the implementation.** Read only the readme's `## The data` section: access (how
and when the release was obtained), size of the whole unfiltered release (files, speakers,
hours), files per label, issues in the release, facts the documentation does not state, ratings
in the release. Cite the readme at its fork commit and only for what the documentation does not
state (rule 4). If the section is missing or lacks an item, leave the value empty and list it in
the reply so the recipe author can add it.

**5. Register.** Write a short script in a scratch directory that uses
`<skill dir>/scripts/reglib.py` and run it once. A complete example:
[references/registration-example.md](references/registration-example.md). Include:
- the sources (`R.source`, `R.link`), then evidence from them for every value you checked:
  license, published counts, `speech_production`, `material_origin`, the design of the spoken
  text only from a design statement; disagreeing sources as `R.conflicting`;
- the label sets (`R.label_set`) with who made them and how (`R.ev("emotion_categories.label_basis", ...)`),
  and the other annotations (`R.ann`), each from a source;
- `R.issue` for each problem the readme reports, `R.label_count` for each label count;
- cells without evidence rows (`notes`, `license_note`, `language_note`, `source_rights_note`):
  facts only, each naming its source;
- aliases and relations only when a source states them.

The script stages everything and writes only in `save()` (which also recomputes the derived
columns), so a failed run changes nothing. After a successful run, running it again would add
the rows twice: restore `data/` from git first (check `git diff` so nothing else is lost).

## Add a dataset

1. Search the DB first (`grep -i` the name in `views/datasets_wide.csv` and `data/aliases.csv`);
   a re-upload of a known corpus becomes an alias and a mirror source, not a row.
2. `python3 tools/db.py add datasets dataset_id=<id> name=<name>`, then register it with
   `reglib`: the sources of the dataset (open each and check it is about this dataset), then the
   name and the values you can check in them.
3. Finish.

## Reconcile external notes

Treat each statement as a claim: check it against the primary source, register what holds, and
list in the reply what was wrong in the notes and why. Relations or identities that the notes only
suspect go into `notes`, not `relations`.

## Answer a question

Look in the DB before searching the web: the row in `views/datasets_wide.csv`, its evidence rows
in `data/evidence.csv` and sources in `data/sources.csv`, and `views/discrepancies.csv`. Answer
with the primary source the row points to (the DB itself is not the source). If the support is a
`provisional` row, a `secondary` source or an `implementation` source, say so: it needs
confirming, or it is a practical reference. Search outside only for empty, `unknown`,
`conflicting` or provisional values, and offer to record what you find.

## Check sources

For `provisional` rows, `secondary` sources and sources without a publisher: open the source,
confirm that it is about this dataset (`identity_basis`), fill `title`, `publisher`, `source_type`
and `checked_on`, and replace provisional values by rows that cite it (`R.ev` supersedes the
provisional row). Save a web-archive copy in `archive_url` when you can. Work in batches of about
ten datasets and commit each batch.

## Finish

```bash
python3 tools/views.py
python3 tools/validate.py          # fix every error, then run again
```

Commit one dataset (or one checking session) per commit. Stage files by name, never with
`git add -A` or `git add .`. Write the message in English: what was wrong or uncertain, what the
evidence was, what changed. If the pre-commit hook fails, nothing was committed: fix, stage again
and make a new commit; do not amend and never bypass the hook. Normal pushes need no
confirmation; never force-push or rewrite published history.

If a rule, code or column changed (only on the maintainer's request), update the README and the
manual (both languages, same commit) too.

## Human verification

When the maintainer should confirm values, put them in a pull request named `verify/<date>-<n>`
(about 20 rows, `license_spdx` first): change `checked_by` to `user` and add the PR number to the
`note`, push the branch, and open the PR with a table of dataset, value, the link and the quoted
words. You never merge; the maintainer merges, and the merge is the confirmation.

## Reply

Keep it short, in this order: what was registered (commit, validation result); what was
verified and in which primary source; where the readme and a primary source disagree and how it
was recorded; what was left empty and why; what is left for the maintainer to decide (including
changes needed in other repositories, which you do not make). State nothing as fact that you did
not check.

## Common errors

Messages from `tools/validate.py` (and reglib) and what they mean:

| Message contains | Fix |
|---|---|
| `field ... does not take evidence` | free-text and URL-free columns have no evidence rows; set the cell with `R.set` |
| `a current row needs a source` / `unknown source_id` | add the source with `R.source` first |
| `*_release fields need a source of type implementation` / `*_reported fields cannot use an implementation source` | release counts come from the readme, documentation counts from papers and pages |
| `current rows disagree` | make them `R.conflicting` or supersede the older one |
| `current and conflicting rows together` | add the disagreeing source with `R.conflicting` (it converts the current rows) |
| `conflicting rows need at least two different values` | one source cannot conflict with itself; use `R.ev` |
| `a provisional row next to current rows` | `R.ev` supersedes provisional rows; do not add them by hand |
| `not in enum ...` | use a value from `schema/enums.csv` |
| `derived from annotations` | run `python3 tools/derive.py`; never edit the derived columns |
| `the dataset has no label set ...` | add the label set (`R.label_set`) before its label counts |
| `same url and source_type as ...` | the source exists; use its id |
| `leading/trailing space or newline` | trim the cell |

## Files in this skill

- `scripts/reglib.py`: stages DB changes for one dataset and saves them (import it).
- `scripts/doc_counts.py`: prints the figures quoted in the manual and checks that the Japanese
  manual agrees with the English one (run it).
- [references/data-model.md](references/data-model.md): tables, missing values, evidence, enums.
- [references/verifying-claims.md](references/verifying-claims.md): how to check claims in primary sources.
- [references/registration-example.md](references/registration-example.md): full script, commit message, reply.
