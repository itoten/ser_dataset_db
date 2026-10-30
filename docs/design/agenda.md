# Design discussion: agenda

How this DB should be shaped is being worked out step by step between the project maintainer and Claude. This file is the current summary; the record of each discussion is in [archive/](archive/), one file per date.

Rules for these notes:

- Every discussion is archived in `archive/<date>.md`. This file only summarises where things stand.
- **An item is closed only when it states the question, its background, the decision, and a clear, logical reason for the decision.** Until all four are written, it stays open, however much agreement there is.
- A closed item says whether it has been applied to the DB yet. Open items are numbered by topic (A-1, B-1, ...); closed items are numbered R-1, R-2, ...
- Decisions here do not change the DB by themselves. Changes are made only when the maintainer asks for them.

Last updated: 2026-10-30

## Open

### A. Principles and name

**A-1. Should the DB be a hub that creates no facts of its own?**
- Background: the maintainer proposed that every value must point to an outside source and that the DB is only the place that gathers them. Two things break this today: `measurements/<recipe>.json`, which `tools/measure.py` produces by reading the ESPnet outputs and the audio directly (the DB measures by itself), and the maintainer's decisions (`source_type=user`, whose source is a conversation).
- Leaning: yes, but other principles need thought too, so nothing is applied yet.

**A-2. What is it called: DB or hub?** To be decided soon.

**A-3. When should general information be separated from local information?**
- Background: the aim is a public resource for researchers and students interested in SER. In such a resource, the maintainer's own experiments and whether a recipe exists in the project's ESPnet fork would be out of place.
- Leaning: separate them clearly when the DB is actually prepared for public use; until then they may stay mixed (see the closed item R-1).

### B. Investigation stage

**B-1. Should investigation be recorded as a stage, with the literature check always required?**
- Background: the old `espnet_status` mixed "how far the dataset has been investigated" with other things. Two kinds of investigation exist: checking published papers and pages (literature), and implementing a recipe in ESPnet and learning from the result (implementation). A *stage* is an ordered progression; a *status* is any state.
- Leaning: a stage, with the difference written in the manual. The literature check is always done; if the implementation check comes first, the literature check is added afterwards.
- Still needed: why a stage serves better than two independent columns, given that the order can be reversed in practice.

**B-2. What must be done before a dataset counts as `implementation_checked`?** What the recipe readme must contain, and how complete the training must be.

### C. The recipe readme as the source

**C-1. Should the recipe readme be the authoritative source for the implementation check?**
- Background: today the DB takes recipe findings from DB update reports (`*_db_update.md`) handed over by the recipe sessions, plus its own measurements. Reports freeze at the time they are written and have contained errors. The training outputs (`exp/`) and manifests hold counts and results, but they are local, large and not part of the ESPnet pull request, so readers of a public DB could not check them.
- Leaning: yes. The readme is reviewed with the recipe, can be cited at a commit, and is readable by people. In exchange, every needed fact must be written in it correctly, including the maintainer's listening notes (worth sharing; long readmes are not a problem when AI reads them).
- Open parts: the fields and format the readme must contain (to discuss with the recipe sessions); a warning in DB updates when a readme lacks them; how to verify what Claude reads from a readme (reading by Claude is acceptable instead of a strict parser); whether DB update reports are retired; and other possible sources, which the maintainer wants to look at before deciding.

### D. Implementation

**D-1. How is "implemented" judged, and what results does the DB hold?**
- Background: whether `recipes.csv` has a row and whether measurements exist can be checked automatically. The "health check" (2 epochs only) is not a concept that should exist: ideally every dataset is trained properly and the readme reports the results and the data used.
- Leaning: no health-check column in the DB. Short runs are written in the readme with their epoch count and replaced when full training is done (the recipe sessions' job), so over the coming months the results change while the data amounts stay the same. Whether the DB keeps results (Macro-F1 and so on), and in which columns, is open.

### E. Dataset status

**E-1. Should the DB record whether a dataset is usable?**
- Background: the old statuses (`candidate`, `needs_decision`, `deferred`, `excluded`) mix facts about a dataset with decisions for experiments. A usable / conditional / unusable scale was proposed.
- Leaning: do not create status columns lightly. Problems are endless, so a column for every state would grow the table without end, and a status invites people to filter datasets without reading the primary sources. Usability depends on the purpose (audio with broken labels can still serve self-supervised learning). Some facts do deserve their own columns; where to draw the line needs careful discussion. Whether to use a dataset is for the person who has looked at everything.

### F. Use decisions

**F-1. Should decisions about using a dataset live in `local/dataset_use.csv`?**
- Background: use decisions change with each experiment, cannot be given a source in the DB's sense (it is often unclear whether a person or an AI made them), can only be made after an implementation check, and are not wanted in git. At present hardly any explicit decisions exist. A place is still needed for "waiting for the license" or "checked, but on hold".
- Leaning: a CSV inside the repository under `local/`, git-ignored, with the pre-commit hook refusing tracked files there. Draft columns: `dataset_id`, `experiment` (`*` for all), `use` (`train_eval` / `train` / `eval` / `none` / `hold` / `undecided`), `waiting_for` (`license` / `distributor` / `origin` / `listening` / `other`), `reason`, `decided_on`, `decided_by` (`maintainer` / `claude`).

### G. Deferred tasks

- **G-1.** Remove every trace of the original spreadsheet from the current files (the git history stays). Open: 429 current values in 83 datasets rest only on spreadsheet evidence; blank them, re-source them from primary sources, or both.
- **G-2.** The manual has no section on `recipes.csv` (its columns are described only in `schema/columns.csv`).

## Closed

### R-1. Separate general and local information now?
- Background: the DB holds local information (the maintainer's experiments, recipes in the project's ESPnet fork) next to general information about datasets. That would be out of place in a public resource.
- Decision (2026-10-30): not now. Local information may stay mixed in.
- Reason: experiments have priority, and separating the two properly needs design work (A-3) that is not ready. Mixing does no harm while the main users are the project itself.
- Applied: nothing to apply.

### R-2. What does `implemented` mean?
- Background: the recipe branch had single-corpus recipes for 102 datasets, but only 95 were `implemented`. Five recipes had passed their health check yet were recorded as `deferred`, `excluded` or `needs_decision`, because one column had to say both "a recipe exists" and "we use the data".
- Decision (2026-10-30): `implemented` means only that a recipe exists in ESPnet. Whether the data is used is a separate matter.
- Reason: the two are different questions with different answers. A recipe can exist for data the project decides not to use, and one column cannot state both truthfully.
- Applied: yes for six datasets (commit 1802789); `bari_emospeech` waits for its corpus to be downloaded again and measured.

### R-3. Names of the investigation stages
- Background: if investigation is recorded as a stage (B-1), its values need English names. Candidates were `listed` / `documents_checked` / `data_checked`, `none` / `literature` / `implementation`, `unreviewed` / `desk_reviewed` / `hands_on_reviewed`, and `listed` / `surveyed` / `examined`.
- Decision (2026-10-30): `listed` / `documents_checked` / `implementation_checked`.
- Reason: the implementation check means implementing the recipe in ESPnet and training it, and finding problems that only show up then (clips long enough to harm training, chance-level results after proper training). `data_checked` reads as downloading and looking at the files, which says too little. `recipe_checked` was also acceptable, but `implementation_checked` is understood at once from the value alone. The `*_checked` form matches `documents_checked`.
- Applied: no (depends on B-1).

### R-4. Remove the original spreadsheet, and when?
- Decision (2026-10-30): remove every trace from the current files later, as a separate task; keep the git history.
- Reason: the spreadsheet origin is not wanted in a public resource, but the discussion on the DB's shape comes first. Rewriting the history of a public repository would change every commit hash and cannot reach existing clones.
- Applied: no (task G-1).

### R-5. Manual languages
- Decision (2026-10-30): keep an English manual and a Japanese translation (`docs/manual.ja.md`) and always update both together.
- Reason: the project works in Japanese; a translation kept outside the repository would drift as soon as the English text changed.
- Applied: yes (commit d6264c9).

### R-6. Keep the design discussion in the repository
- Decision (2026-10-30): the agenda and the archive of every discussion live in `docs/design/`.
- Reason: how the DB was designed is itself important information for everyone who uses it.
- Applied: yes (this folder).
