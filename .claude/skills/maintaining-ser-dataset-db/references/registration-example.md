# Worked example: registering an implemented dataset

A complete pass through the registration workflow for a made-up corpus, `toyemo`. Copy the
shapes, not the values.

## Contents
- The situation
- What verification found
- The registration script
- Saving a long report inside the repository
- Commit message
- Reply to the requester

## The situation

The DB row `toyemo` is a `candidate` (`unexamined`). A DB update report arrives. It says:

- The recipe `egs3/toyemo/cls` exists (first commit `abc1234`); the maintainer decided to keep it.
- Kaggle `someone/toyemo`, version 2, CC BY 4.0 (the maintainer looked at the page).
- 1,200 WAV files, 8 actors, 6 emotions, 1.10 hours, 44.1 kHz.
- 12 pairs of byte-identical files; the maintainer listened and decided to keep one file of each
  pair, so the recipe uses 1,188 files.
- Labels are the emotion each actor was asked to portray.
- Question: should `n_utt_reported` stay 1,240 (the description) or become 1,200?

## What verification found

- Kaggle API: CC BY 4.0, version 2. The description says "1,240 utterances" in one sentence and
  "8 actors × 6 emotions × 25 sentences" in another; 8 × 6 × 25 = 1,200.
- `audio_audit.py inventory`: 1,200 WAV files, all 44.1 kHz mono 16-bit, 1.0972 h in total
  (the report's 1.10 h rounds this), 12 byte-identical pairs.
- `audio_audit.py dups`: the same 12 pairs, plus one more pair with different bytes
  (correlation 0.997) that the report missed, with two different emotion labels.
- `measurements/toyemo.json`: 1,188 clips; train / valid / test = 832 / 118 / 238.

## The registration script

Saved in a scratch directory as `r_toyemo.py` and run once with the system Python
(`python3 r_toyemo.py`). If it fails halfway nothing is written; fix it and run again.

```python
import sys
sys.path.insert(0, "<skill dir>/scripts")
from reglib import Reg

KG = "https://www.kaggle.com/datasets/someone/toyemo"
AUDIT = "the release files, audio_audit.py inventory (2026-01-31)"
# report_path is resolved from the directory that contains the repository, hence the repo name prefix.
R = Reg("toyemo", today="2026-01-31", report="ser_dataset_db/reports/2026-01-31_toyemo_db_update.md")

# Status: the recipe exists and the maintainer keeps it.
R.ev("espnet_status", "implemented", "measured", "data/recipes.csv; egs3/toyemo/cls on the recipe branch",
     "recipe directory exists", note="first commit abc1234; duplicate removal def5678")
R.ev("status_reason_codes", "NA", "measured", "data/recipes.csv", "implemented rows have no reason code")
R.set(status_note="6 classes. Uses 1,188 of the 1,200 files: one file of each of 12 byte-identical pairs is "
                  "left out (maintainer's decision after listening, 2026-01-30).",
      status_checked_on=R.today)

# Counts: the description contradicts itself, so keep both values.
R.ev("n_utt_reported", "1200", "primary", KG, "8 actors x 6 emotions x 25 sentences",
     note="The same description also says 1,240 utterances; its own design gives 1,200 and the release has 1,200 files")
R.conflicting("n_utt_reported", "1240", "primary", KG, "comprises 1,240 utterances",
              note="contradicts the design formula in the same description")
R.ev("n_files_release_measured", "1200", "measured", AUDIT, "1,200 .wav files", note="matches the report")
R.ev("n_speakers_measured", "8", "measured", AUDIT, "speaker field of the file names")

# Labels and license.
R.ev("label_source", "human", "primary", KG, "actors portrayed the given emotion")
R.ev("label_verification", "NA", "primary", KG, "no listening test described; labels are the instructed emotion")
R.ev("license_spdx", "CC-BY-4.0", "user", KG, "license field on the page", by="user",
     note="checked on the page by the maintainer (2026-01-30); the API shows the same")
R.set(release_version="Kaggle version 2 (2025-11-02)",
      notes="Acted speech by 8 actors, 6 emotions, 25 sentences. 1,200 WAV files, 44.1 kHz mono 16-bit, "
            "1.0972 h. 12 byte-identical pairs. One further pair has the same sound with different bytes "
            "(Angry_031 / Sad_112, correlation 0.997) under two different labels; it was not in the report.")

# Recipe tables (needs measurements/toyemo.json from tools/measure.py).
R.recipe(report_path="reviews/toyemo.md",  # must exist, same base directory as above
         official_split_exists="false",
         split_method="speaker_independent", split_unit="speaker (train 6, valid 1, test 1)",
         speaker_overlap="false",
         recipe_exclusions_note="12 files: the second file of each byte-identical pair (maintainer, 2026-01-30)",
         known_issues="One near-identical pair with different labels (Angry_031 / Sad_112) is still used",
         baseline_status="not_run", notes="health check ok on 2026-01-29 (2 epochs)")
R.labels({"angry": ("anger", "angry", "spelling_fix"), "happy": ("joy", "happy", "synonym_rename"),
          "sad": ("sadness", "sad", "synonym_rename"), "neutral": ("neutral", "neutral", "identity"),
          "fear": ("fear", "fear", "identity"), "surprise": ("surprise", "surprise", "identity")})
R.ann([("speaker_id", "actor code in the file name (8 actors)", "human", "speaker", "true",
        "measured", AUDIT, "file names", "used for the speaker-independent split"),
       ("sentence_id", "sentence number 1-25; the texts are not distributed", "human", "utterance", "false",
        "primary", KG, "file naming section", "")])
R.alias("ToyEmo Corpus", "official_name", KG)
R.save()
```

Then the finishing loop from SKILL.md: `tools/views.py`, `doc_counts.py --write`,
`tools/validate.py`, fix, repeat.

## Saving a long report inside the repository

When an investigation does not fit in `notes` (provenance, access history, several sources),
copy the incoming report to `reports/<date>_<dataset_id>_db_update.md`, leave its text
unchanged, and put this section on top:

```markdown
# <Dataset>: DB update report (saved with verification)

This file is the incoming report, unchanged, with the DB maintainer's verification added on top.
Evidence rows for `<dataset_id>` point here through `via`.

## 0. Verification by the DB maintainer (<date>)

| Claim in the report | How it was checked | Result |
|---|---|---|
| ... | ... | matches / differs: ... |

Not verified: ...

How the report's questions were answered: ...

---
```

## Commit message

```
Register toyemo as implemented (1,188 of 1,200 files)

The report's counts were re-measured from the release and match, except that the
near-duplicate search found one more pair (Angry_031 / Sad_112) with different labels;
it is recorded in notes and known_issues. The Kaggle description gives both 1,240 and
1,200 utterances; 1,200 follows its own design and the release, so it is canonical and
1,240 is kept as a conflicting row.
```

State what was wrong or uncertain and what the evidence was, not only what changed.

## Reply to the requester

```markdown
Registered toyemo as implemented (commit 1a2b3c4, validate: 0 errors). The recipe uses
1,188 of the 1,200 files.

Verified: license and version (Kaggle API), 1,200 files / 8 speakers / 1.0972 h / formats
(release files), the 12 byte-identical pairs, the recipe counts (measurements).

Differs from the report:
- One more near-identical pair, with different labels: Angry_031 / Sad_112 (corr 0.997).
  Recorded in notes and known_issues; the recipe still uses both files.

Not verified: the sentence texts (not distributed).

Your question: n_utt_reported is 1,200 (the description's own design), with 1,240 kept as a
conflicting row.

Open: should the recipe also drop the pair above? That is your call.
```
