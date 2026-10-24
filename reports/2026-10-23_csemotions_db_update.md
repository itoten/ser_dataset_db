# CSEMOTIONS: DB update report (saved with verification)

This file is the full DB update report written by the recipe author (originally `recipe_reports/2026-10-23_csemotions_db_update.md`, in Japanese), translated into English, with the DB maintainer's verification added on top. The evidence rows of `csemotions` point here through `via`. Apart from the translation, the report text is unchanged. The decisions to treat the license as `open` and not to apply the ESD condition in the NOTICE are the project maintainer's (2026-10-23).

## 0. Verification by the DB maintainer (2026-10-23)

| Claim in the report | How it was checked | Result |
|---|---|---|
| The Hugging Face card says Apache-2.0; the NOTICE at pinned commit 19498e62... says ESD (MIT, research use only) is incorporated; the card does not mention ESD; the old name AIDC-AI/CSEMOTIONS redirects to ATH-MaaS/CSEMOTIONS | Re-fetched the Hugging Face API, NOTICE, README and redirect | Matches (same commit SHA) |
| 4,160 clips, 10 speakers, 10.198 h, 1.75-34.2 s, 48 kHz mono **16-bit** (the card says 24-bit), 15 clips over 30 s | Recounted the 8 parquet files of the release | Matches (4,160 clips, 10.1978 h, 1.752-34.212 s, PCM_16 only, 15 over 30 s). The card's 24-bit does not match the data |
| 1,296 distinct sentences, 1,293 read by several speakers, each sentence under only one emotion | Counted the `text` column | Matches (1,296 / 1,293 / 0 sentences across emotions) |
| Split: train 7 speakers 2,932 / valid female002 378 / test male003, male004 850; 848 of 849 test sentences and all 378 valid sentences also appear in train | Recomputed from the parquet files | Matches |
| No audio overlap with ESD (compared with 35,000 clips) | Re-checked with a different method: all 35,000 ESD clips against all 4,160 CSEMOTIONS clips, filtered by duration (+/-30 ms) and envelope correlation > 0.9, then confirmed by whole-waveform correlation | 0 candidates. Matches the report (partial overlaps were not compared, as in the report) |
| No sentence overlap with ESD's 350 Mandarin sentences (max 0.19) | Recomputed the character-bigram Jaccard between the saved Whisper transcripts of 350 sentences and the 1,296 CSEMOTIONS sentences | 0 exact matches, max 0.185. The computation reproduces; the Whisper transcripts themselves were not verified |
| ESD: the GitHub LICENSE is MIT; the README asks for a signed form and says research use only. ESD has 350 parallel sentences and 10 Mandarin speakers | Re-fetched from GitHub | Matches |
| The Marco-Voice report (arXiv 2508.02038) describes CSEMOTIONS as a new proprietary dataset and lists ESD as separate training data | Re-fetched the paper and read the relevant section | Matches. However, the paper says "**each speaker reading a curated set of 100 Chinese and English prompts**", while the data has 1,296 distinct Mandarin sentences (300-400 per speaker), which does not match the paper (a discrepancy not in the report) |

Additional findings (not in the report):
- The column names on the Hugging Face card (transcript / speaker_id / gender / prompt_id) differ from the actual columns (audio / text / emotion / speaker).
- The DB row for ESD (`esd`) is already recorded as `research_only` / `signed_agreement` based on its README (answer to question 2 in §6). The disagreement with its MIT LICENSE is outside the scope of this registration.

Not verified: the listening check (the maintainer's 28 clips), the intent of the NOTICE (no explanation from the authors), whether part of a clip contains ESD audio, the correctness of the Whisper transcripts of ESD, and the absence of a description of emotion-label validation in the paper (searched by keyword, not read in full).

---

# CSEMOTIONS: DB update report

- Written: 2026-10-23 (to the DB maintainer)
- dataset_id: `csemotions` (recipe `egs3/csemotions/cls`, first commit d0bacb999e2; readme update 838c0bf1ea0, local)
- Review: the maintainer's decision (2026-10-23): **the license is `open` (Apache-2.0)**. State that the NOTICE says ESD (research use only) is incorporated, and record the reasons for judging it open anyway. The data has no problems, is large and promising.
- Detailed basis: `recipe_review/csemotions.md`; measurements in `recipe_review/csemotions_scripts/`
- Figures re-measured from the release files on 2026-10-20. The sentence comparison with ESD and sentence sharing across splits were measured additionally on 2026-10-23
- Listening (the maintainer, 2026-10-23): listened to 4 clips (different speakers) for each of the 7 emotions and judged that paralinguistic information is clearly present. Since a model may still judge from the meaning of the sentences, a mild warning was added to the readme.
- Health check: `ok` (2026-10-20 20:44:37-20:55:33, GPU 1, 2 epochs; the scores are smoke-test values and say nothing about learning quality). The recipe's data was not changed

## 1. Conclusion

| Item | Content |
|---|---|
| Status | `candidate` -> `implemented` |
| Whole set and what the recipe uses | All 4,160 clips (only the 15 train clips over 30 s are dropped by `remove_long_short`) |
| License | `open` (Apache-2.0, card). The ESD condition in the NOTICE is not applied, since no ESD material was found (§3) |
| Facts to record | Sentences and emotions are one-to-one (each of the 1,296 sentences appears under one emotion only). Bit depth is 16-bit, not the card's 24-bit |

## 2. Proposed updates to datasets.csv

| Column | Current value | Proposal | Basis |
|---|---|---|---|
| espnet_status | candidate | implemented | recipe d0bacb999e2 |
| status_reason_codes | unexamined | NA | - |
| source_url | https://huggingface.co/datasets/AIDC-AI/CSEMOTIONS | https://huggingface.co/datasets/ATH-MaaS/CSEMOTIONS (the old name redirects here) | HF |
| license_spdx / license_class | Apache-2.0 / open | unchanged | card (maintainer's decision) |
| license_note | (empty) | proposal below | NOTICE, §3 |
| n_files_release_measured | (empty) | 4160 | measured |
| n_speakers_measured | (empty) | 10 | measured (`speaker` column) |
| label_source | (empty) | `human` (emotions portrayed by voice actors, `emotion` column) | card |
| label_verification | (empty) | `NA` (no listening check described) | card |
| status_note | "...the NOTICE file says it incorporates ESD (research use only); which part is unverified." | "The recipe uses all 4,160 clips. The ESD condition (research use only) in the NOTICE is not applied because no overlap with ESD was found in sound or sentences; treated as Apache-2.0 (maintainer's decision 2026-10-23)." | §3 |
| notes | current text | replace with the proposal below | - |
| report_path | (empty) | recipe_reports/2026-10-23_csemotions_db_update.md | - |
| status_checked_on / last_updated_on | - | 2026-10-23 | - |

### Proposed license_note
"The card says Apache-2.0. The repository's NOTICE (pinned commit 19498e62...) says it incorporates Emotional-Speech-Data (ESD, MIT) that \"can only be used for research purpose\", but does not say which clips. A check on 2026-10-23 found no clip with the same length and matching waveform among all 35,000 ESD clips, and no sentence close to ESD's 350 Mandarin sentences (transcribed with Whisper; at most 19% character-bigram overlap). The Marco-Voice report describes CSEMOTIONS as new recordings by 10 voice actors and lists ESD as separate training data. The NOTICE may come from the whole project (which also trained on ESD), but the authors do not explain it. Treated as open by the maintainer's decision."

### Proposed notes
"Alibaba AIDC-AI. Released with the Marco-Voice technical report (arXiv 2508.02038). Studio recordings of 10 professional voice actors (5 male, 5 female), 7 emotions (neutral, happy, angry, sad, surprise, playfulness, fearful), 4,160 clips, 10.198 h (measured), 1.75-34.2 s, 48 kHz mono **16-bit** (the card says 24-bit). The `text` column holds the script sentence; 1,293 of 1,296 sentences are read by several speakers. **Each sentence appears under one emotion only, so the emotion can also be read from the meaning** (listening shows the voice differs by emotion too, but a model may rely on linguistic information). No duplicates. The paper's evaluation prompts are 100 per emotion (English and Chinese)."

### Proposed evidence rows

| field | value | source_type | source_ref | locator |
|---|---|---|---|---|
| n_files_release_measured | 4160 | measured | measurements/csemotions.json (or the recipe's measurement) | row count of the 8 parquet files |
| n_speakers_measured | 10 | measured | same | `speaker` column |
| status_reason_codes (adding a superseding row) | NA | project_doc | recipe_reports/2026-10-23_csemotions_db_update.md | §1 |

## 3. Why the ESD condition is not applied (what was checked)

| Check | Method | Result | File |
|---|---|---|---|
| Audio overlap | All 35,000 clips of the ESD recipe (Mandarin and English) against the 4,160 CSEMOTIONS clips, matched by length (+/-20 ms) and waveform correlation (`tools/cross_dup.py`) | **0** near-identical pairs. Partial overlaps were not compared | `cross_esd.out` |
| Sentence overlap | ESD's Mandarin part uses the same 350 sentences for all speakers and emotions. The 350 neutral clips of speaker 0001 were transcribed with Whisper large-v3 and compared with the 1,296 CSEMOTIONS sentences by character-bigram Jaccard | **0** close sentences (max 0.19) | `esd_text_overlap.out`, `esd_0001_neutral_whisper.tsv` |
| Design | - | ESD: 5 emotions, 350 parallel sentences each. CSEMOTIONS: 7 emotions (including playfulness, fearful), different sentences per emotion | - |
| Paper | Read the text of the Marco-Voice report (arXiv 2508.02038) | Describes CSEMOTIONS as "a proprietary emotional speech dataset", studio recordings of 10 experienced voice actors. Lists ESD alongside as separate training data. Says the evaluation prompts were built "across both ESD and CSEMOTIONS" emotion classes. Nothing says ESD was mixed into the data | `sources/marcovoice_2508.02038.pdf`, `marcovoice.txt` |
| NOTICE | Fetched and read the NOTICE at the pinned commit | Says ESD is incorporated, research use only; does not say which clips. The card (README) does not mention ESD | `NOTICE_19498e62...`, `README_19498e62....md` |

- ESD itself: the GitHub LICENSE is MIT. The README (`sources/esd_README.md`, fetched 2026-10-23) asks users to "complete a License and send it" and says "This database can only be used for research purpose." The NOTICE wording is the same as this README sentence. How to treat the ESD row needs a separate check (outside this report).

## 4. Whole set and what the recipe uses

| | Whole set | Recipe |
|---|---|---|
| Clips | 4,160 | 4,160 (train 2,917 after `remove_long_short`) |
| Hours | 10.198 | same (the 15 train clips over 30 s are dropped by `remove_long_short`) |
| Speakers | 10 | by speaker: train 7 speakers 2,932 / valid female002 378 / test male003, male004 850 |
| Sentence sharing | - | 848 of 849 test sentences and all 378 valid sentences are also read in train |

- `max_epochs` = max(30, ceil(3000 / ceil(2917 / 32))) = 33 (matches the setting).

## 5. recipes.csv

| Column | Value |
|---|---|
| recipe | egs3/csemotions/cls |
| first_commit | d0bacb999e2 |
| Remarks | reason for the license decision added to the readme (838c0bf1ea0, local). max_epochs 33 |

## 6. Questions

1. May `license_note` describe the reasoning at this length (if too long, refer to it through report_path)?
2. `license_class` of the ESD row (`esd`): the LICENSE is MIT (open), but the README requires sending a form and says research use only. Outside this report, but needs checking together with the CSEMOTIONS decision.

## 7. Not verified

- Listening covered only 4 clips per emotion (different speakers, 28 in total, `csemotions_scripts/listen/`).
- Whether part of a clip contains ESD audio (only same-length comparisons were made).
- The intent of the NOTICE (no explanation from the authors).
