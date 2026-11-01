---
name: maintaining-ser-dataset-db
description: Maintains the speech emotion recognition (SER) dataset database, a public git repository of CSV tables in which every value carries an evidence row pointing to a primary source. Reads new or rebuilt ESPnet recipes and their readmes, checks dataset facts against primary sources, then registers recipes and datasets, records evidence, keeps the README and manual counts in sync, validates, and commits. Use when told that a recipe was made or rebuilt, asks to add or reclassify a dataset, asks to reconcile another team's research notes with the DB, or asks about a dataset's license, access, size, labels or status.
---

# Maintaining the SER dataset DB

The DB is a **tertiary source**: it does not offer the truth about a dataset, but the way to the
primary sources (papers, distribution pages, license files, recipe readmes) where the truth can
be checked. Each dataset is one row in `data/datasets.csv`; the main values have a row in
`data/evidence.csv` saying which source states them. `tools/validate.py` enforces the rules and
runs as a pre-commit hook.

All paths below are relative to the repository root. `<skill dir>` is this skill's directory
(`${CLAUDE_SKILL_DIR}` in Claude Code).

## First time in the repository

Read `README.md` (mission and principles first), then
[references/data-model.md](references/data-model.md). Then run:

```bash
python3 tools/validate.py     # must end with "0 error(s)"; a warning about unregistered recipes is normal
```

What you need to know about the surroundings:

- **Recipes** live in a separate toolkit repository (ESPnet), under `egs3/<recipe>/cls/` on a
  dedicated branch. `tools/egs3.py` says where that repository is expected and which branch is
  read. Read recipe files from the branch, not the working tree:
  `git -C <recipe repo> show <branch>:egs3/<recipe>/cls/readme.md`. The branch is published on
  the public fork `itoten/espnet`; only commits that are on the fork can be cited.
- **Two Pythons**: the DB tools run with the system `python3` (needs PyYAML only).
  `tools/measure.py` needs the toolkit's environment; its docstring shows the command.
- **The design is being discussed.** The open questions and decisions are in
  `docs/design/agenda.md` and `docs/design/archive/`. Decisions there do not change the DB by
  themselves: change rules, columns or existing rows only when the project maintainer asks.

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
   published. In particular:
   - **Do not count or measure anything yourself** to fill a dataset value (no file counts,
     duplicate searches, transcriptions or listening). Values that need counting (files and
     speakers in the release, sentence overlap, how well the voice carries the emotion, ...) stay
     empty (not checked) until the recipe's readme states them; then cite the readme.
   - A **recipe readme** is a primary source only for what can be known solely by implementing
     the recipe (counts in the release, duplicates, what the files contain). If a paper, page or
     card states the same thing, cite that source, even when the readme repeats it: there the
     readme is only restating it. Cite the readme at a commit on the public fork:
     `https://github.com/itoten/espnet/blob/<commit>/egs3/<recipe>/cls/readme.md`. If the commit
     is not on the fork yet, leave the value empty and say so in the reply.
2. **Evidence types for new rows: `primary`, and `secondary` only as an exception.**
   - `primary`: the authors' or their organisation's paper, official page, LICENSE, official
     release files, or the recipe readme.
   - `secondary`: only when the primary source cannot be accessed (paywall, page gone, no
     response); write why in `note`. Redistributions by others (mirrors, re-uploads) are
     `secondary`; when it is unclear whether one is official, say so in `note`.
   - Do not add `measured`, `project_doc`, `user` or `sheet` rows (they are being phased out;
     the exceptions are under "Interim" below). Internal notes and reports are leads, never the
     source: put them in `via` at most.
3. **Every evidence row must point at a statement about the dataset.** Before saving a row, ask:
   does the source (and `locator`) say something about the dataset itself? A policy, an
   instruction, a decision to add a value to a column, "treated like dataset X", a counting
   convention, or a choice between disagreeing sources is not evidence of a dataset fact.
4. **Do not judge.** When sources disagree, record what each says (`conflicting` rows; for
   licenses the cell becomes `conflicting`); do not pick one. When wording is ambiguous, record
   it as written; do not interpret it. Free text (`status_note`, `notes`, ...) states facts and
   caveats, never advice such as "should not be used" or "poor data".
5. **Empty, `unknown`, `none`, `NA` mean different things.** Empty = not checked yet;
   `unknown` = a source was read and does not say (cite the source you read, with "not stated" in
   `locator`); `none` = checked, there is none; `NA` = does not apply. A failed attempt at one
   moment (timeout, 404) is `unknown` with the date in the note.
6. **Listening tests: record that one exists and where, not its result.** If a source (or,
   through the readme, the release files) describes a human perception or listening test,
   record its existence and where it is described. Do not put its result in a column as a single
   number: accuracy depends on the number of classes, audio only or with video, how answers were
   combined and which clips were rated, so numbers from different tests mislead when set side by
   side. Readers are pointed to the source. How to record it until the columns are rebuilt: see
   "Interim".
7. **Every value has a source**, including names, versions, URLs and free text. Where a column
   takes no evidence rows yet, name the source in the text itself (see "Interim").
8. **Write only what a source supports.** No invented URLs, titles or numbers. Never cite a file
   you did not open. Reports from other sessions contain mistakes: check every claim against the
   primary source ([references/verifying-claims.md](references/verifying-claims.md)).
9. **Never delete history.** A new value gets a new evidence row; the old one becomes
   superseded. Conflicting sources stay visible.
10. **Keep "the whole release" and "what the recipe uses" apart** in every count and note.
11. **Everything is public.** Files and commit messages are published worldwide. No personal
    names (refer to "the project maintainer"), e-mail addresses or machine-specific paths (use
    environment variable names such as `$EESC_OUTPUT`; machine settings go in the git-ignored
    `.env`).
12. **Stay within the request.** Large sweeps (re-checking every license, re-probing every URL)
    and design changes are proposed, not started.

## Interim: decided but not yet implemented

Some decisions need a design that does not exist yet. Until it does, follow this table, and do
not invent a new mechanism. The plan is tracked outside this repository by the maintainer.

| Situation | Decided direction | Until then |
|---|---|---|
| `espnet_status` / `status_reason_codes` (applying the status policy, use or exclusion decisions) | moves out of the public facts (local information) | record the maintainer's decision as before (`source_type=user`); only for these two columns |
| `espnet_status=implemented` (a recipe exists) | derived from the branch on the public fork | `measured` row citing the recipe directory on the branch, as in the example |
| Recipe tables (`recipes.csv`, `recipe_labels.csv`, `measurements/`) | numbers come from the recipe readme | keep running `tools/measure.py` and `tools/sync.py` (the validator requires them); write no dataset evidence from them |
| The maintainer checked a source (human verification) | a record of DB work, kept apart from `source_type` | `primary` row citing the page, `checked_by=user`, the checked words in `locator`, the date (and an archive URL if one was made) in `note` |
| A readme figure for a `*_measured` column (files, speakers in the release) | cited from the readme | those columns accept only `measured` rows: leave them empty and give the readme's figure, with its link, in `notes` |
| The maintainer's listening findings (`paralinguistic_signal`) | from the recipe readme, as its author's view | leave empty unless a readme or a published listening test states it |
| Existing `measured`, `project_doc`, `user`, `secondary` rows | replaced by primary sources or emptied | leave them as they are unless asked to migrate them |
| A listening test (rule 6) | a column saying whether a test exists, plus the path to the source; no single accuracy number | add an `annotations` row, item `listening_test`, citing the source that describes it (`primary`, the describing words in `locator`); keep `label_verification` as before; add no new `human_accuracy` values (existing ones stay) |
| `source_rights` | codes only whether the material is third-party (recorded for the dataset, or taken from films, broadcasts, the web); what sources say about rights is quoted; no "needs checking" | for new entries use only `own` (a source says it was recorded for the dataset); for third-party material leave the code empty and quote what the sources say about it, with the source named, in `source_rights_note` |
| Columns without evidence rows (names, `release_version`, URLs, free text) | every value cites a source through a list of sources (`sources.csv`, not built yet) | name the source in the text (`v2 (Kaggle page)`; "… 20 listeners (paper, section 3)") and put no fact in free text that no source states |

## Choose the workflow

- "A new recipe was made" / "this recipe was rebuilt" (a recipe name, maybe a commit) →
  **Register a recipe** below.
- "Add this dataset" / a survey of new datasets → **Add a dataset**.
- Another team's research notes that touch the DB → **Reconcile external notes**.
- A question about a dataset → **Answer a question**.
- "Bring the counts up to date" → only **Finish**.

## Register a recipe

Recipe sessions build recipes on their own and do not hand over a report. When you are told
that a recipe was made or rebuilt, go and read the recipe and its readme yourself. Older
`*_db_update.md` reports may still exist; they are leads at most, never sources.

Copy this checklist and tick it off:

```
- [ ] 1. Read the recipe, its readme and the current DB row
- [ ] 2. Check that the readme commit is on the public fork
- [ ] 3. Check the dataset facts in primary sources
- [ ] 4. Take the findings of the implementation from the readme's "## The data" section only
- [ ] 5. Recipe tables (tools/measure.py) and status (interim rules)
- [ ] 6. Write and run the registration script (reglib)
- [ ] 7. Finish: views, counts, validate, commit, push
- [ ] 8. Reply: registered / verified / left empty and why / open questions
```

**1. Read.** The recipe's `dataset/config.yaml`, `readme.md` and commit history on the recipe
branch (`git -C <recipe repo> show <branch>:egs3/<recipe>/cls/readme.md`); the dataset's row in
`views/datasets_wide.csv` and its evidence rows (`grep '^<id>/' data/evidence.csv`).

**2. Public fork.** Find the commit that last changed the readme and check that it is on the
public fork (`git -C <recipe repo> branch -r --contains <commit>`). If it is not, nothing from
the readme can be cited yet: register what primary sources support and say so in the reply.

**3. Dataset facts.** Open the distributor page or API and the paper and check license, version,
published counts (including counts per label), speakers and label set; establish separately how
the audio was produced (acted, elicited, spontaneous, read, synthetic) and how the labels were
made (instructed, perceived by raters, self-reported, inferred from context, automatic); look for
a listening test. Citations in other sections of the readme are leads to these sources, not
sources themselves.

**4. Findings of the implementation.** Read only the readme's `## The data` section: access
(how and when the release was obtained), size of the whole unfiltered release (files, speakers,
hours), files per label, issues in the release, facts the documentation does not state, ratings
in the release. Cite the readme at its fork commit, and only for what the documentation does not
state (rule 1). If the section is missing or lacks an item, leave the value empty and list it in
the reply so the recipe author can add it.

**5. Recipe tables and status.** `tools/measure.py <recipe>` writes `measurements/<recipe>.json`,
which fills the recipe tables (interim rule; these tables are to be removed). The recipe exists
on the branch → `implemented` (`status_reason_codes=NA`, with a `recipes.csv` row). Decisions not
to use a dataset come from the maintainer directly → `excluded` with a clear reason code, or
`deferred`. If no reason code fits, ask the maintainer before adding one. The full rules:
[references/data-model.md](references/data-model.md).

**6. Register.** Write a short script in a scratch directory that uses
`<skill dir>/scripts/reglib.py` and run it once. A complete example:
[references/registration-example.md](references/registration-example.md). Include:
- evidence from primary sources for every value you checked: license, published counts,
  `label_source`, `label_verification`, `speech_production`, `label_basis` (details in
  `label_basis_note`), the design of the spoken text only from a design statement;
  disagreeing sources as `conflicting` rows;
- a listening test, if any source describes one, as an `annotations` row (interim rule);
- values stated in the readme's `## The data` section, cited at its fork commit;
- status rows under the interim rule;
- cells without evidence: `status_note`, `notes`, `license_note`, `release_version`,
  `status_checked_on` (facts only, each naming its source; no advice);
- for implemented datasets: `R.recipe(...)` with the hand-written columns, `R.labels({...})`
  keyed by the recipe's own label names, and `R.ann([...])` with every non-emotion annotation
  that a primary source or the readme describes;
- aliases and relations only when a source states them;
- dates: `checked_on` and `status_checked_on` are the day you checked; a maintainer's decision
  keeps the date it was made (write it in the note).

The script stages everything and writes only in `save()`, so a failed run changes nothing.
After a successful run, running it again would add the rows twice: restore `data/` from git
first (check `git diff` so nothing else is lost).

**7–8.** Finish (below), then reply.

## Add a dataset

1. Search the DB first (`grep -i` the name in `views/datasets_wide.csv` and `data/aliases.csv`);
   a re-upload of a known corpus becomes an alias, not a row.
2. `python3 tools/db.py add datasets dataset_id=<id> name=<name> ...`, fill the URL columns with
   the primary pages (open each and check it is about this dataset), then add evidence rows from
   primary sources with `reglib` (status `candidate`, reason `unexamined` unless a clear exclusion
   reason applies).
3. Finish.

## Reconcile external notes

Treat each statement as a claim: check it against the primary source, register what holds, and
list in the reply what was wrong in the notes and why. Relations or identities that the notes only
suspect go into `notes`, not `relations`.

## Answer a question

Look in the DB before searching the web: the row in `views/datasets_wide.csv`, its evidence rows
in `data/evidence.csv`, and `views/discrepancies.csv`. Answer with the primary source the row
points to (the DB itself is not the source); if the support is not `primary`, say that it needs
confirming. Search outside only for empty, `unknown` or contested values, and offer to record
what you find.

## Finish

Run this loop until validation passes:

```bash
python3 tools/views.py
python3 <skill dir>/scripts/doc_counts.py          # review the listed changes
python3 <skill dir>/scripts/doc_counts.py --write
python3 tools/validate.py                          # fix every error, then run the loop again
```

- `doc_counts.py` rewrites every count quoted in `README.md` and `docs/manual.md`, and checks
  `docs/manual.ja.md` against it. A `MISSING` line means a sentence was reworded: update the rule
  in the script or fix the text by hand. The exclusion breakdown it prints must be compared by hand.
- `docs/manual.ja.md` is the Japanese translation of `docs/manual.md`. Whenever you edit the
  English manual, make the same change in the Japanese one in the same commit. `doc_counts.py`
  prints a `PARITY` line for every section whose numbers differ from the English manual; fix those
  by hand.
- If a rule, code or column changed (only on the maintainer's request), update the README and
  manual text (both languages) too.

Commit one dataset (or one checking session) per commit. Stage files by name, never with
`git add -A` or `git add .`. Write the message in English: what was wrong or uncertain, what the
evidence was, what changed (example in the example file). If the pre-commit hook fails, nothing
was committed: fix, stage again and make a new commit; do not amend and never bypass the hook.
Normal pushes need no confirmation; never force-push or rewrite published history.

## Reply

Keep it short, in this order: what was registered (status, commit, validation result); what was
verified and in which primary source; where the readme and a primary source disagree and how it
was recorded; what was left empty and why (not in a primary source, not in the readme's
`## The data` section, readme commit not public); what is left for the maintainer to decide (including changes needed in other repositories, which you do not make).
State nothing as fact that you did not check.

## Common errors

Messages from `tools/validate.py` (and reglib) and what they mean:

| Message contains | Fix |
|---|---|
| `field ... does not take evidence` | URL and text columns have no evidence rows; set the cell with `R.set` |
| `*_reported fields cannot use measured` / `*_measured fields need source_type measured` | published values need `primary` (or `secondary`); leave `*_measured` columns empty (rule 1) |
| `canonical row uses a weaker source than another row; note is required` | add a `note` saying why the canonical row is the current one (e.g. it replaces an older source) |
| `canonical value ... != datasets value` | the cell and the canonical row disagree; set both through `R.ev` |
| `license_class ... != derived` | `license_class` follows `license_spdx`; when emptying `license_spdx`, empty `license_class` too |
| `not in enum ...` | use a value from `schema/enums.csv` (e.g. `mapping_type`: `identity`, `spelling_fix`, `synonym_rename`, `outside_common7`, `dropped_by_recipe`) |
| `status_reason_codes must be NA exactly when implemented` | `NA` for implemented rows, at least one reason code otherwise |
| `implemented but recipes.csv has no recipe` / `is not an implemented dataset` | only implemented datasets have recipe rows, and every implemented one needs one |
| `used_in_recipe is true but the dataset is not implemented` | use `NA` for datasets that are not implemented |
| `path not found (relative to ...)` | `report_path` is resolved from the directory containing the repository: write `<repo name>/reports/...` |
| `leading/trailing space or newline` | trim the cell (reglib trims evidence notes only) |
| `labels: token_list is ...` (reglib) | spec keys must be the recipe's labels, not the corpus's spelling |
| warning: `recipes on ... are not registered yet` | expected while recipes wait for review, and for recipes of non-implemented datasets |

## Files in this skill

- `scripts/reglib.py`: stages DB changes for one dataset and saves them (import it).
- `scripts/doc_counts.py`: recomputes the counts in README and manual (run it).
- `scripts/audio_audit.py`: inventory and duplicate search for a corpus. It is for recipe authors,
  whose readme then states the results; the DB does not record its output (rule 1).
- [references/data-model.md](references/data-model.md): tables, missing values, evidence, statuses, enums.
- [references/verifying-claims.md](references/verifying-claims.md): how to check claims in primary sources.
- [references/registration-example.md](references/registration-example.md): full script, commit message, reply.
