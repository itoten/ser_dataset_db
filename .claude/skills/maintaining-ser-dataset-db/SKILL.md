---
name: maintaining-ser-dataset-db
description: Maintains the speech emotion recognition (SER) dataset database, a git repository of CSV tables in which every value carries an evidence row (source, date, strength). Verifies incoming DB update reports against primary sources and the audio files, then registers recipes and datasets, records evidence, keeps the README and manual counts in sync, validates, and commits. Use when someone hands over a *_db_update.md report or its path, asks to add or reclassify a dataset, asks to reconcile another team's research notes with the DB, or asks about a dataset's license, access, size, labels or status.
---

# Maintaining the SER dataset DB

The DB is a ledger of speech emotion (and other paralinguistic) datasets. Each dataset is one
row in `data/datasets.csv`; every important value has a row in `data/evidence.csv` saying where
it came from. `tools/validate.py` enforces the rules and runs as a pre-commit hook. Correctness
matters more than coverage: when something is not known, the DB says so.

All paths below are relative to the repository root. `<skill dir>` is this skill's directory
(`${CLAUDE_SKILL_DIR}` in Claude Code).

## First time in the repository

Read `README.md`, then [references/data-model.md](references/data-model.md). Then run:

```bash
python3 tools/validate.py     # must end with "0 error(s)"; a warning about unregistered recipes is normal
```

What you need to know about the surroundings:

- **Recipes** live in a separate toolkit repository (ESPnet), under `egs3/<recipe>/cls/` on a
  dedicated branch. `tools/egs3.py` says where that repository is expected and which branch is
  read. Read recipe files from the branch, not the working tree:
  `git -C <recipe repo> show <branch>:egs3/<recipe>/cls/dataset/config.yaml`.
- **Audio** for a recipe: its `dataset/config.yaml` names an environment variable
  (`source_env_var`); its value in the toolkit's environment is the corpus directory.
- **Two Pythons**: the DB tools run with the system `python3` (needs PyYAML only).
  `tools/measure.py` and `<skill dir>/scripts/audio_audit.py` need numpy and soundfile, so run
  them in the toolkit's environment; `tools/measure.py`'s docstring shows the command.

## Principles

1. **Check every factual claim yourself.** Reports from other sessions or people are useful
   leads, but they contain miscounts and unsourced statements. Open the source, count the files.
   How: [references/verifying-claims.md](references/verifying-claims.md).
2. **Decisions belong to the project maintainer** (the person who owns the research project;
   their decisions reach you through the conversation or are quoted in a report). Their listening checks, license checks and
   use/exclude decisions are recorded as given (`source_type=user`). Do not change a status,
   exclude data, or decide something they have postponed. Propose instead.
3. **Write only what a source or a measurement supports.** No invented URLs, titles or numbers.
   Never cite a file you did not open. Unverified means "left out" or "marked not verified".
   This holds for every column, including judgement-like ones such as `lexical_confound`:
   without a clear source, leave the cell empty rather than filling in a plausible value.
4. **Never delete history.** A new value gets a new evidence row; the old one becomes
   superseded. Conflicting sources stay visible.
5. **Keep "the whole release" and "what the recipe uses" apart** in every count and note.
6. **Everything is public.** Files and commit messages are published worldwide. No personal
   names (refer to roles), e-mail addresses or machine-specific paths (use environment variable
   names such as `$EESC_OUTPUT`; machine settings go in the git-ignored `.env`).
7. **Stay within the request.** Large sweeps (re-checking every license, re-probing every URL)
   are proposed, not started.

## Choose the workflow

- A DB update report (`*_db_update.md`) or its path → **Register a report** below.
- "Add this dataset" / a survey of new datasets → **Add a dataset**.
- Another team's research notes that touch the DB → **Reconcile external notes**.
- A question about a dataset → **Answer a question**.
- "Bring the counts up to date" → only **Finish**.

## Register a report

A DB update report is a Markdown handoff, usually named `<date>_<dataset_id>_db_update.md`,
written by whoever implemented or reviewed a recipe. It proposes DB values, lists what the
maintainer decided, and may ask questions. Treat its proposals as claims to check.

Copy this checklist and tick it off:

```
- [ ] 1. Read the report, the current DB row and the recipe
- [ ] 2. Sort claims: maintainer decisions vs. facts to check
- [ ] 3. Check the facts (sources + audio)
- [ ] 4. Measure the recipe (tools/measure.py)
- [ ] 5. Decide the status the maintainer's decision implies
- [ ] 6. Write and run the registration script (reglib)
- [ ] 7. Save the report in the repo if it is long
- [ ] 8. Finish: views, counts, validate, commit
- [ ] 9. Reply: verified / differs / not verified / questions answered / open
```

**1. Read.** The report; the dataset's row in `views/datasets_wide.csv` and its evidence rows
(`grep '^<id>/' data/evidence.csv`); any review notes and measurement files the report points
to; the recipe's `dataset/config.yaml`, readme and commit history on the recipe branch.

**2. Sort the claims** into maintainer decisions (record as given) and facts (check each).

**3. Check the facts.** At minimum: open the distributor page or API and compare license,
version, counts, speakers and label set; establish from the paper how the audio was produced
(acted, elicited, spontaneous, read, synthetic) and, separately, how the labels were made
(instructed, perceived by raters, self-reported, inferred from context, automatic); run
`audio_audit.py inventory` on the corpus and compare files, formats, durations and
byte-identical groups; if the report counts duplicates, run `audio_audit.py dups` yourself.
Note every difference: you will report it.

**4. Measure.** `tools/measure.py <recipe>` writes `measurements/<recipe>.json`, the counts of
what the recipe actually uses. The recipe tables are filled from it.

**5. Status.** The recipe exists and the maintainer keeps it → `implemented`
(`status_reason_codes=NA`, with a `recipes.csv` row). The maintainer decided not to use the
data → `excluded` with a clear reason code, or `deferred`; no `recipes.csv` row (validate.py
then warns that the recipe is unregistered; mention it in the reply). If no reason code fits,
add one to `schema/enums.csv` and the manual. The full rules: [references/data-model.md](references/data-model.md).

**6. Register.** Write a short script in a scratch directory that uses
`<skill dir>/scripts/reglib.py` and run it once. A complete example, including every table:
[references/registration-example.md](references/registration-example.md). Include:
- evidence for `espnet_status`, `status_reason_codes`, the checked counts
  (`n_files_release_measured`, `n_speakers_measured`, or `unknown` when they cannot be counted),
  `label_source`, `label_verification`, `speech_production` and `label_basis` (with details in
  `label_basis_note`), `text_emotion_link` and `lexical_confound` (with the basis in
  `lexical_confound_note`), and any published value or license that changed;
  disagreeing sources as `conflicting` rows;
- cells without evidence: `status_note`, `notes`, `license_note`, `release_version`,
  `status_checked_on`;
- for implemented datasets: `R.recipe(...)` with the hand-written columns, `R.labels({...})`
  keyed by the recipe's own label names, and `R.ann([...])` with every non-emotion annotation;
- aliases and relations only when a source states them;
- dates: `checked_on` and `status_checked_on` are the day you checked; a maintainer's decision
  keeps the date it was made (write it in the note).

The script stages everything and writes only in `save()`, so a failed run changes nothing.
After a successful run, running it again would add the rows twice: restore `data/` from git
first (check `git diff` so nothing else is lost).

**7. Long reports.** If the investigation does not fit in `notes`, copy the report to
`reports/<date>_<dataset_id>_db_update.md` unchanged, add a verification section on top (the
template is in the example file), and pass it as `Reg(..., report="<repo name>/reports/<file>")`.

**8–9.** Finish (below), then reply.

## Add a dataset

1. Search the DB first (`grep -i` the name in `views/datasets_wide.csv` and `data/aliases.csv`);
   a re-upload of a known corpus becomes an alias, not a row.
2. `python3 tools/db.py add datasets dataset_id=<id> name=<name> ...`, then add evidence rows
   from primary sources with `reglib` (status `candidate`, reason `unexamined` unless a clear
   exclusion reason applies).
3. Finish.

## Reconcile external notes

Treat each statement as a claim: check it against the source, register what holds, and list in
the reply what was wrong in the notes and why. Relations or identities that the notes only
suspect go into `notes`, not `relations`.

## Answer a question

Look in the DB before searching the web: the row in `views/datasets_wide.csv`, its evidence rows
in `data/evidence.csv`, and `views/discrepancies.csv`. Answer with the source and its strength;
if the only support is `sheet`, `project_doc` or `secondary`, say that it needs confirming.
Search outside only for empty, `unknown` or contested values, and offer to record what you find.

## Finish

Run this loop until validation passes:

```bash
python3 tools/views.py
python3 <skill dir>/scripts/doc_counts.py          # review the listed changes
python3 <skill dir>/scripts/doc_counts.py --write
python3 tools/validate.py                          # fix every error, then run the loop again
```

- `doc_counts.py` rewrites every count quoted in `README.md` and `docs/manual.md`. A `MISSING`
  line means a sentence was reworded: update the rule in the script or fix the text by hand.
  The exclusion breakdown it prints must be compared by hand.
- If you changed a rule or added a code or column, update the README and manual text too.

Commit one dataset (or one checking session) per commit. Stage files by name, never with
`git add -A` or `git add .`. Write the message in English: what was wrong or uncertain, what the
evidence was, what changed (example in the example file). If the pre-commit hook fails, nothing
was committed: fix, stage again and make a new commit; do not amend and never bypass the hook.
Push following the team's practice; never force-push or rewrite published history.

## Reply

Keep it short, in this order: what was registered (status, what the recipe uses, commit,
validation result); what was verified; **what differs from the report** and how it was
resolved; what could not be verified; answers to the report's questions; what is left for the
maintainer to decide (including changes needed in other repositories, which you do not make).
State nothing as fact that you did not check.

## Common errors

Messages from `tools/validate.py` (and reglib) and what they mean:

| Message contains | Fix |
|---|---|
| `field ... does not take evidence` | URL and text columns have no evidence rows; set the cell with `R.set` |
| `*_reported fields cannot use measured` / `*_measured fields need source_type measured` | published values need `primary`/`secondary`; your own counts go to the `*_measured` columns |
| `canonical row uses a weaker source than another row; note is required` | add a `note` saying why the weaker source wins |
| `canonical value ... != datasets value` | the cell and the canonical row disagree; set both through `R.ev` |
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
- `scripts/audio_audit.py`: inventory and duplicate search for a corpus (run it).
- [references/data-model.md](references/data-model.md): tables, missing values, evidence, statuses, enums.
- [references/verifying-claims.md](references/verifying-claims.md): how to check sources and audio.
- [references/registration-example.md](references/registration-example.md): full script, saved-report header, commit message, reply.
