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

## The registration script

Saved in a scratch directory as `r_toyemo.py` and run once with the system Python
(`python3 r_toyemo.py`). If it fails halfway nothing is written; fix it and run again.

```python
import sys
sys.path.insert(0, "<skill dir>/scripts")
from reglib import Reg

R = Reg("toyemo", today="2026-01-31")

# Sources first. publisher: authors -> primary, third_party -> secondary, recipe_author -> implementation.
KG = R.source("toyemo_page", "https://www.kaggle.com/datasets/someone/toyemo", "distribution_page", "authors",
              describes_version="version 2")
PAPER = R.source("toyemo_paper", "https://example.org/toyemo-paper.pdf", "paper", "authors")
README = R.source("toyemo_readme", "https://github.com/itoten/espnet/blob/ser/cross-corpus/egs3/toyemo/cls/readme.md",
                  "readme", "recipe_author", describes_version="Kaggle version 2")
R.link(KG, "distribution"); R.link(PAPER, "paper"); R.link(README, "readme")

# Published facts from primary sources.
R.ev("n_files_reported", "1200", KG, "8 actors x 6 emotions x 25 sentences ... 1,200 utterances")
R.ev("n_speakers_reported", "8", KG, "8 actors")
R.ev("license_spdx", "CC-BY-4.0", KG, "license field: CC BY 4.0", by="user",
     note="the maintainer also checked the page on 2026-01-30")
R.ev("label_source", "human", PAPER, "actors portrayed six target emotions")
R.ev("speech_production", "acted", PAPER, "actors portrayed six target emotions")
R.ev("label_basis", "intended", PAPER, "label = the emotion the actor was asked to portray")
R.set(label_basis_note="Labels are the instructed emotion (paper, section 2).")
R.ev("label_verification", "none", PAPER,
     "listening test measured recognition only; no clips were removed or relabelled")

# Findings only the implementation can show: cite the readme, with the commit in the locator.
R.ev("spoken_text_design", "parallel", README,
     "commit def5678abcde; Not stated in the documentation: the same 25 sentences are spoken in every emotion")
R.ev("n_files_release", "1200", README, "commit def5678abcde; Size of the release")
R.ev("n_speakers_release", "8", README, "commit def5678abcde; Size of the release")
R.ev("hours_release", "1.10", README, "commit def5678abcde; Size of the release")
R.ev("access_observed", "obtained", README, "commit def5678abcde; Access")
R.set(access_observed_on="2026-01-29")
R.set(notes="Acted speech by 8 actors, 6 emotions, 25 sentences (Kaggle page). The recipe readme "
            "reports 12 pairs of byte-identical files (commit def5678abcde).")

# A listening test: that it exists and where it is described, not its result (rule 6).
R.ann([("listening_test", "listening test of recognition of the intended emotion; results in the paper",
        "human", "utterance", PAPER, "section 4", ""),
       ("speaker_id", "actor code in the file name (8 actors)", "human", "speaker", KG, "file naming section", ""),
       ("sentence_id", "sentence number 1-25", "human", "utterance", KG, "file naming section", "")])
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
