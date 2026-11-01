# Worked example: registering an implemented dataset

A complete pass through the registration workflow for a made-up corpus, `toyemo`. Copy the
shapes, not the values.

## Contents
- The situation
- What checking found
- The registration script
- Commit message
- Reply to the requester

## The situation

The DB row `toyemo` is a `candidate` (`unexamined`). The maintainer says: "the recipe toyemo was
made". You read `egs3/toyemo/cls` on the recipe branch. Its readme (last changed in commit
`def5678`, which is on the public fork) has a `## The data` section saying:

- checked on 2026-01-29 against Kaggle version 2; direct download, no login;
- 1,200 WAV files, 8 speakers, 1.10 hours, over the whole release;
- 200 files for each of the six labels;
- issues: 12 pairs of byte-identical files (MD5);
- not stated in the documentation: the same 25 sentences are spoken in every emotion (from the
  distributed transcripts).

Another section of the readme mentions a listening test and cites the paper.

## What checking found

- Kaggle API: CC BY 4.0, version 2. The description says "8 actors × 6 emotions × 25 sentences"
  and "1,200 utterances".
- The paper (the authors' own): actors portrayed six emotions; section 4 reports a listening test
  of how often listeners recognised the intended emotion. The DB records that the test exists and
  where; its numbers stay in the paper (rule 6).
- Neither the page nor the paper says whether the sentences are the same in every emotion, so for
  that the readme's `## The data` section is the source; had the paper said it, the paper would
  be cited even though the readme repeats it (rule 1). The same holds for the file count and the
  duplicates, which only the release shows.
- The paper gives no count per label, so the readme's counts per label are the only ones.
- `measurements/toyemo.json` (from `tools/measure.py`): 1,188 clips; train / valid / test =
  832 / 118 / 238.

## The registration script

Saved in a scratch directory as `r_toyemo.py` and run once with the system Python
(`python3 r_toyemo.py`). If it fails halfway nothing is written; fix it and run again.

```python
import sys
sys.path.insert(0, "<skill dir>/scripts")
from reglib import Reg

KG = "https://www.kaggle.com/datasets/someone/toyemo"
PAPER = "https://example.org/toyemo-paper.pdf"
README = "https://github.com/itoten/espnet/blob/def5678/egs3/toyemo/cls/readme.md"
R = Reg("toyemo", today="2026-01-31")

# Status (interim rule): the recipe exists on the branch.
R.ev("espnet_status", "implemented", "measured", "data/recipes.csv; egs3/toyemo/cls on the recipe branch",
     "recipe directory exists", note="first commit abc1234")
R.ev("status_reason_codes", "NA", "measured", "data/recipes.csv", "implemented rows have no reason code")
R.set(status_note="6 classes. The recipe uses 1,188 of the 1,200 files: one file of each of 12 "
                  "byte-identical pairs is left out (recipe readme).",
      status_checked_on=R.today)

# Published facts from primary sources.
R.ev("n_utt_reported", "1200", "primary", KG, "8 actors x 6 emotions x 25 sentences ... 1,200 utterances")
R.ev("n_speakers_reported", "8", "primary", KG, "8 actors")
R.ev("license_spdx", "CC-BY-4.0", "primary", KG, "license field: CC BY 4.0", by="user",
     note="the maintainer also checked the page on 2026-01-30")
R.ev("label_source", "human", "primary", PAPER, "actors portrayed six target emotions")
R.ev("speech_production", "acted", "primary", PAPER, "actors portrayed six target emotions")
R.ev("label_basis", "intended", "primary", PAPER, "label = the emotion the actor was asked to portray")
R.set(label_basis_note="Labels are the instructed emotion (paper, section 2).")

# A listening test (rule 6): record that it exists and where, not its result.
R.ev("label_verification", "none", "primary", PAPER,
     "listening test measured recognition only; no clips were removed or relabelled")

# Findings only the implementation can show: cite the readme at its fork commit.
R.ev("text_emotion_link", "parallel", "implementation", README, "the same 25 sentences are spoken in every emotion")
R.ev("lexical_confound", "none", "implementation", README, "the same 25 sentences are spoken in every emotion")
R.set(lexical_confound_note="The same 25 sentences in every emotion (recipe readme, from the distributed transcripts).")
R.ev("n_files_release_measured", "1200", "implementation", README, "1,200 WAV files over the whole release")
R.ev("n_speakers_measured", "8", "implementation", README, "8 speakers")
R.set(release_version="version 2, 2025-11-02 (Kaggle page)",
      notes="Acted speech by 8 actors, 6 emotions, 25 sentences (Kaggle page). The recipe readme (commit def5678) "
            "reports 12 pairs of byte-identical files.")

# Recipe tables (interim rule: needs measurements/toyemo.json from tools/measure.py).
R.recipe(official_split_exists="false",
         split_method="speaker_independent", split_unit="speaker (train 6, valid 1, test 1)",
         speaker_overlap="false",
         recipe_exclusions_note="12 files: the second file of each byte-identical pair (maintainer, 2026-01-30)",
         label_basis_used="intended",
         baseline_status="not_run", notes="health check ok on 2026-01-29 (2 epochs)")
R.labels({"angry": ("anger", "angry", "spelling_fix"), "happy": ("joy", "happy", "synonym_rename"),
          "sad": ("sadness", "sad", "synonym_rename"), "neutral": ("neutral", "neutral", "identity"),
          "fear": ("fear", "fear", "identity"), "surprise": ("surprise", "surprise", "identity")})
R.ann([("listening_test", "listening test of recognition of the intended emotion; results in the paper",
        "human", "utterance", "false", "primary", PAPER, "section 4", ""),
       ("speaker_id", "actor code in the file name (8 actors)", "human", "speaker", "true",
        "primary", KG, "file naming section", "used for the speaker-independent split"),
       ("sentence_id", "sentence number 1-25", "human", "utterance", "false",
        "primary", KG, "file naming section", "")])
R.alias("ToyEmo Corpus", "official_name", KG)
R.save()
```

Then the finishing loop from SKILL.md: `tools/views.py`, `doc_counts.py --write`,
`tools/validate.py`, fix, repeat.

## Commit message

```
Register toyemo as implemented (1,188 of 1,200 files)

License, published counts and label basis come from the Kaggle page and the paper; the
paper's listening test is recorded as an annotation pointing to section 4 of the paper.
Sentence overlap, the release file count and the duplicates come from the readme's
"The data" section at def5678, because no primary source states them.
```

State what was uncertain and what the evidence was, not only what changed.

## Reply to the requester

```markdown
Registered toyemo as implemented (commit 1a2b3c4, validate: 0 errors). The recipe uses
1,188 of the 1,200 files.

Verified in primary sources: license and version (Kaggle), 8 speakers and 1,200 utterances
(Kaggle), acted speech with instructed labels and the listening test (paper).
From the readme's "The data" section (def5678): 1,200 files, 12 byte-identical pairs, the same
sentences in every emotion.

Left empty: total hours and counts per label have no column yet (planned); they stay in the
readme until then.
```
