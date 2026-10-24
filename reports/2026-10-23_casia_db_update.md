# CASIA: investigation of origin and access route (saved with verification)

This file is the full report written by the recipe author (originally `recipe_reports/2026-10-23_casia_db_update.md`, in Japanese), translated into English, with the DB maintainer's verification added on top. The evidence rows of `casia` point here through `via`. Apart from the translation, the report text is unchanged. The source documents themselves are kept outside this repository, in the recipe author's review folder (`recipe_review/casia_scripts/sources/`; SHA-256 in §9).

## 0. Verification by the DB maintainer (2026-10-23)

The report's facts were checked against the originals or primary sources, opened directly. Human decisions (the project maintainer's) were not re-checked.

| Claim in the report | How it was checked | Result |
|---|---|---|
| ChineseLDC resource page (archived 2020-05-01): institution: Institute of Automation; 4 speakers, 6 emotions, 9,600 sentences (300 identical + 100 different texts); license fees CNY 5,000 / 15,000 / 35,000 / 105,000; added 2008-06-11; updated 2010-10-09 | Re-fetched from the Wayback Machine and read in full; the SHA-256 of the saved copy also matches | Matches. The copyright line at the bottom of that page says 中国中文信息学会 (Chinese Information Processing Society of China), which differs from the 2024 top page cited in §3.1 (中国科学院自动化研究所, Institute of Automation) (checked by reading the 2024 snapshot; it changed over time) |
| 2005 catalogue: 12,000 sentences, six emotions, 300 identical + 200 different texts (intro); 5 emotions, 500 sentences each, 10,000 in total, w1/w2/m1/m2, 16 kHz 16-bit (label); SNR about 35 dB (report) | Read the three saved documents (hashes match) | Matches. None of the three describes a listening check ("not described", not "not done") |
| Tao et al. 2008 is a paper on a single-female-speaker speech-synthesis corpus, and "emotion" never appears in it | Re-fetched the PDF from the Wayback Machine (SHA-256 matches) and searched the full text | Matches. "emotion" occurs 0 times |
| The EmoBox README and paper link to AI Studio 209512; the paper's reference [10] is Tao et al. 2008 | Re-fetched the GitHub README and arXiv 2406.07162 | Matches (table: Act / Mandarin / 6 / 4 / 1200 / 0.6; [10] = Tao, Liu, Zhang, Jia) |
| Citations in other papers (arXiv 2103.16456: "Blizzard Challenge, 2005"; 2310.03992: only Zhang and Jia, 2008; 2001.05908: no source) | Re-fetched the arXiv PDFs and searched the citations | Matches |
| AI Studio 209512: uploader 千鹤, 2023-04-16 13:58:22, license field 其他 (other), Institute of Automation in the organisation field, CASIA.zip 54.89 MB, link to rid=76 in the description | Opened the page in a browser and read it | Matches |
| Hugging Face mirror `Bill13579/casia-mirror`: created 2025-06-29, LICENSE is 0 bytes | Checked via the Hugging Face API and headers | Matches (tagged `license:other`) |
| The extracted mirror and the 20 files shown on AI Studio match in size and modification time | Compared the 20 files in the local copy of the data | **20 / 20 match**. Not compared by hash (as the report says) |
| Content of the 1,200-clip version: 1,200 clips, 4 speakers, 6 emotions x 200, sentence numbers 201-250, 16 kHz mono, 0.6352 h | Recounted the release files | Matches (4 speakers x 50 per emotion from file names; no duplicate file names among the 1,200) |

Not verified: ChineseLDC's terms as of 2024 (the site cannot be reached), hash identity of the mirror and the AI Studio zip, transcripts of sentence numbers 206-250, the Whisper transcripts (201-205), the content of `recipe_review/mistakes.md`.

How the DB maintainer answered §6:
1. The maintainer decided (2026-10-23) to keep the recipe, so `espnet_status` is `implemented` (meaning a recipe exists), with the warning at the start of `status_note` and `known_issues`.
2. `source_type` of E1-E3 is `primary` (the distributor's catalogue). The evidence notes say it is not a document of the creators' lab.
3. `n_utt_reported` takes the latest value, 9,600 (2010 edition); the 2005 values 12,000 and 10,000 are kept as separate `conflicting` rows. `labels_discrete_reported` takes the list of 6 emotions (AI Studio description), with the 2005 set of 5 emotions kept as a separate `conflicting` row.
4. The 1,200-clip version is described in notes rather than as a separate dataset row.

---

# CASIA: DB update report (investigation of origin and access route)

- Written: 2026-10-23 (to the DB maintainer)
- dataset_id: `casia` (recipe `egs3/casia/cls`, first commit 1556c1c8ce4)
- Request: the maintainer (2026-10-23): "Register this in the DB, taking into account everything checked so far. It may not all fit, so keep it as a report too."
- Detailed basis: §0a of `recipe_review/casia.md`. All documents obtained are saved in `recipe_review/casia_scripts/sources/` (list and SHA-256 in §9)
- **How this report is written**: only documents actually opened and read are used as evidence. For each, the part that could be read is stated, and inferences are marked "appears to" to separate them from facts. Summaries returned by a web-search tool are not used as evidence (background in §8).
- **Not yet decided**: whether to keep using the recipe and the DB `espnet_status` have not been decided by the maintainer. They are listed as options in §6 and not included in the proposals of §2.

## 1. Conclusion

| Item | Finding | Certainty |
|---|---|---|
| Creator of the corpus | Institute of Automation, Chinese Academy of Sciences (CASIA). The catalogue of the distributor ChineseLDC says "开发单位 中国科学院自动化所, 开发时间 2005 年" (developer: Institute of Automation; developed in 2005) | ChineseLDC's statement (no document by the creators found) |
| ChineseLDC and the Institute | The copyright line of the ChineseLDC site says 中国科学院自动化研究所, and its contact address is the Institute's (2024 snapshot) | The ChineseLDC site's own statement |
| Size of the whole corpus | 4 speakers, 6 emotions, 9,600 utterances (300 identical + 100 different sentences), per the ChineseLDC resource page (updated 2010-10-09). The 2005 catalogue says 12,000 / 10,000 and 5 emotions, which disagrees | Differs by edition |
| Access terms | **Paid license from ChineseLDC**: domestic non-commercial CNY 5,000, domestic commercial 15,000, foreign non-commercial 35,000, foreign commercial 105,000 (page archived 2020-05-01) | Terms as of 2024 unverified |
| **Source cited by SER papers** | **"Design of Speech Corpus for Mandarin Text to Speech" (Tao et al. 2008) is a paper on a single-female-speaker speech-synthesis corpus and does not describe an emotion corpus.** SER papers, including EmoBox, cite it as the source of the CASIA emotion corpus | Confirmed by reading the paper |
| **Origin of the widely used 1,200-clip version** | A **re-upload by an individual (display name 千鹤) to Baidu AI Studio on 2023-04-16**. The EmoBox README links to it. The recipe's Hugging Face mirror appears to hold the same files | Read the AI Studio page and compared 20 files |
| Permission to redistribute | None of the documents found allows free redistribution | - |

In short: **the CASIA emotion corpus has no paper by its creators, SER research cites a different paper as its source, and the 1,200-clip version used in benchmarks derives from an individual's re-upload made without the paid license.**

## 2. Proposed updates to datasets.csv

`espnet_status` and `status_reason_codes` are updated once §6 is decided (for now they stay `needs_decision` / `access_unofficial_mirror_only`).

| Column | Current value | Proposal | Basis (numbers in §3) |
|---|---|---|---|
| source_url | https://globalaccentchinese.com/literature.php | http://www.chineseldc.org/resource_info.php?rid=76 (cannot be reached from this environment now; archived copies in §9) | E1. The current value has no basis (§7) |
| license_spdx | LicenseRef-proprietary-restricted (basis: spreadsheet) | Same value. Replace the evidence with a `primary` row (E1) and mark the spreadsheet row `superseded` | E1 |
| license_class | restricted | unchanged (derived column) | - |
| access_method | (empty) | `paid_or_membership` (paid license from ChineseLDC). Mention the unofficial redistributions in notes | E1 |
| n_utt_reported | 1200 (spreadsheet) | `conflicting`: 9,600 (E1, 2010 edition), 12,000 (E2, 2005 resource overview), 10,000 (E3, 2005 annotation guide). The spreadsheet's 1200 is the 1,200-clip version's count, so `superseded` (note: "count of the 1,200-clip version") | E1-E3 |
| n_speakers_reported | 4 (spreadsheet) | 4 (E1, E3; E3 says 2 male and 2 female) | E1, E3 |
| labels_discrete_reported | anger;fear;happiness;sadness;surprise;neutral (spreadsheet) | `conflicting`: 6 emotions (E1 gives only the number; the list is from the re-upload's description, E4: neutral, happy, sad, angry, fearful, surprised) and 5 emotions (E3: 高兴, 悲哀, 生气, 惊吓, 中性 = joy, sadness, anger, fright, neutral) | E1, E3, E4 |
| hours_reported | 0.6 (spreadsheet) | the sources give no total duration -> `unknown`. 0.6 is the 1,200-clip version's value (measured 0.6352), so `superseded` | - |
| n_files_release_measured | (empty) | 1200 (what the recipe obtains = the Hugging Face mirror) | measured |
| n_speakers_measured | (empty) | 4 | measured (file names) |
| label_source | (empty) | `human` (speakers read while acting the emotion; E3) | E3 |
| label_verification | (empty) | `unknown` (no listening test is described) | - |
| paper_url | (empty) | leave empty (**no paper by the creators was found**). Tao et al. 2008, cited by SER papers, is about another corpus, so it is not used | §4 |
| status_note | "99_final_report says..." | proposal below | - |
| notes | (empty) | proposal below | - |
| report_path | (empty) | recipe_reports/2026-10-23_casia_db_update.md | - |
| status_checked_on / last_updated_on | - | 2026-10-23 | - |

### Proposed status_note
"Paid license through ChineseLDC (CLDC-SPC-2005-010). The widely used 1,200-clip version (EmoBox etc.) derives from an individual's re-upload (Baidu AI Studio 209512, 2023), and the recipe's Hugging Face mirror appears to be the same. Tao et al. 2008, cited by SER papers as the source, is a speech-synthesis corpus paper, not the source of the emotion corpus. Whether to use the recipe is undecided (2026-10-23)."

### Proposed notes
"\"CASIA汉语情感语料库\" (CASIA Chinese emotional speech corpus) of the Institute of Automation, Chinese Academy of Sciences (ChineseLDC CLDC-SPC-2005-010, developed 2005). Acted speech: 4 professional speakers (2 male, 2 female) read identical sentences and emotion-appropriate sentences with emotion; 16 kHz, 16-bit. Size differs by edition (2005 catalogue: 6 emotions, 12,000 / 5 emotions, 10,000; resource page updated 2010: 6 emotions, 9,600). **No paper by the creators was found. SER papers cite \"Design of Speech Corpus for Mandarin Text to Speech\" (Tao, Liu, Zhang, Jia, Blizzard Challenge 2008), but that is a paper on a single-female-speaker, 5,000-sentence speech-synthesis corpus with no mention of emotion** (the citations also differ in authors and year between papers). The 1,200-clip version used by EmoBox and others (4 speakers x 6 emotions x sentence numbers 201-250; 201-205 were confirmed to be the same sentences read in different emotions) is a re-upload to Baidu AI Studio by an individual who is not the creator (2023-04-16). No statement allowing free redistribution was found (investigation of 2026-10-23)."

### Proposed evidence rows

| ID | field | value | source_type | source_ref | locator | via |
|---|---|---|---|---|---|---|
| E1 | license_spdx / access_method / n_utt_reported / n_speakers_reported | LicenseRef-proprietary-restricted / paid_or_membership / 9600 / 4 | primary | http://www.chineseldc.org/resource_info.php?rid=76 | Wayback snapshot of 2020-05-01; summary and license-fee fields | web.archive.org/web/20200501144342/... |
| E2 | n_utt_reported | 12000 | primary | http://www.chineseldc.org/doc/CLDC-SPC-2005-010/intro.htm | Wayback 2005-12-14; (5) 开发规模 (size) | web.archive.org |
| E3 | n_utt_reported / n_speakers_reported / labels_discrete_reported / label_source | 10000 / 4 / 5 emotions / human | primary | http://www.chineseldc.org/doc/CLDC-SPC-2005-010/label.htm | Wayback 2005-12-14; 1、语料内容 (corpus content) | web.archive.org |
| E4 | labels_discrete_reported | neutral;happy;sad;angry;fearful;surprised | secondary | https://aistudio.baidu.com/datasetdetail/209512 | description (an individual's re-upload) | EmoBox README |

- E1-E3 are ChineseLDC documents, so they are `primary`. The note should say they are not documents of the creators' lab (question 3 in §6).
- Archived URLs in §9.

## 3. Evidence (documents read, and how much of each)

### 3.1 The ChineseLDC (distributor) catalogue

| # | Document | Read | What it says |
|---|---|---|---|
| E2 | CLDC-SPC-2005-010 intro.htm (archived 2005-12-14) | full text | Resource name 汉语情感语料库 (Chinese emotional speech corpus); developer: Institute of Automation; developed 2005; **four professional speakers, six emotions, 12,000 sentences in total**; 300 identical-text and 200 different-text sentences |
| E3 | label.htm of the same (annotation guide, archived 2005-12-14) | body (figures excluded) | **5 emotions** (高兴 joy, 悲哀 sadness, 生气 anger, 惊吓 fright, 中性 neutral). 500 sentences per emotion: the first 300 identical texts, the last 200 texts whose meaning reveals the emotion. Speakers: 2 male and 2 female (w1, w2, m1, m2), 2,500 sentences each, **10,000 in total**, 16 kHz, 16-bit PCM. With .tag files of syllable boundaries and F0 |
| - | report.htm of the same (technical document, archived 2005-12-14) | body | The same design of 5 emotions and 500 sentences as label. Recording SNR about 35 dB. Purpose: analysing prosody and acoustics across emotional states; research on emotion recognition and emotional synthesis |
| E1 | resource_info.php?rid=76 (archived 2020-05-01; the 2019-11-25 and 2020-01-24 snapshots have the same content hash) | full text | Resource name "**CASIA汉语情感语料库**", catalogue number CLDC-SPC-2005-010, **4 speakers, 6 emotions, 9,600 sentences (300 identical + 100 different texts)**, added 2008-06-11, updated 2010-10-09, **license fees** (table in §1) |
| - | Top page (archived 2024-11-26) | full text | "**版权所有：中国科学院自动化研究所**" (copyright: Institute of Automation). Contact: Room 514, Intelligence Building, 95 Zhongguancun East Road, Haidian District, Beijing. A notice says the Institute's embedded speech-synthesis system was trained on CASIA汉语情感语料库 among others. CLDC describes itself as a non-profit body initiated by a committee of the Chinese Information Processing Society of China |
| - | Resource list (archived 2023-12-06, 2024-06-15) | first page | "CASIA汉语情感语料库" is listed (99 resources in total) |

- 9,600 = 4 x 6 x 400, 12,000 = 4 x 6 x 500, 10,000 = 4 x 5 x 500: each edition is internally consistent. Why the edition changed is not stated.
- The last archived copy of the resource page with prices is 2020-05-01. A 2023 snapshot (with extra characters in the URL) is empty, so **the terms as of 2024 are unconfirmed**.
- The site cannot be reached from this environment (a university network; timeout). Whether it is down or restricted by region or network is unknown.

### 3.2 The paper SER papers cite (a different corpus)

- **Tao, Liu, Zhang, Jia, "Design of Speech Corpus for Mandarin Text to Speech"**. The PDF on the Institute's NLPR site (`nlpr.ia.ac.cn/2008papers/gjhy/gh166.pdf`) was obtained from the Wayback Machine (snapshot 2024-05-03) and **read in full** (PDF created 2008-08-27).
  - Abstract: the CASIA Mandarin corpus for speech-synthesis research, recorded in a studio by a professional female speaker; 5,000 phonetically balanced sentences, about 7 hours; distributed as the common corpus of the Blizzard Challenge 2008.
  - Speaker selection: one 30-year-old woman chosen from 8 male and female candidates.
  - **The word "emotion" does not appear once.**
- The Blizzard 2008 organisers' paper (Karaiskos, King, Clark, Mayo; PDF from the ISCA Archive, read): 2008 was the 4th edition. The Mandarin data is "6.5 hours of a single female speaker released by NLPR, Institute of Automation".
- "The WISTON Text to Speech System for Blizzard 2008" by the same authors (PDF from the ISCA Archive, read): the Mandarin data is 4,500 utterances, about 8.5 hours of neutral reading provided by CASIA; the license reference is `www.speakit.cn/corpus/license.html` (not ChineseLDC).
- The Blizzard 2008 paper lists (festvox.org's official page and the ISCA Archive) do not include "Design of Speech Corpus...". How it was presented is unknown.

### 3.3 How SER papers describe it (texts read)

| Paper | Description of CASIA | Citation |
|---|---|---|
| EmoBox (arXiv 2406.07162; venue not stated in the PDF) | Table: Act, Mandarin, 6 emotions, 4 speakers, 1,200, 0.6 h | [10] **J. Tao, F. Liu, M. Zhang, H. Jia**, "Design of speech corpus for Mandarin text to speech", The Blizzard Challenge Workshop, 2008 |
| arXiv 2103.16456 (Deep Self-Learning) | 9,600 utterances, 4 speakers (2 male, 2 female), 6 emotions; experiments use the 7,200 utterances of the 300 sentences | [26] J. Tao, F. Liu, M. Zhang, H. Jia, ..., Proc. the 4th Workshop on Blizzard Challenge, **2005** (the 4th edition was 2008; the year is wrong) |
| arXiv 2310.03992 (LIDAN) | 4 speakers (2 male, 2 female), **1,200 samples, 300 sentences per speaker** (numbers inconsistent) | [27] **J. Zhang and H. Jia**, ..., The blizzard challenge 2008 workshop, 2008 (2 of the 4 authors) |
| arXiv 2001.05908 | Recorded by the Institute of Automation; 4 professional speakers, 6 kinds of emotion (only 5 listed, without fear), 9,600 in total | **no citation** |
| Journal of Nanjing University (Natural Science) 55(5), 765- (2019), "A comparative study of cross-lingual corpora for speech emotion recognition" | The Institute's Chinese emotional speech corpus, 4 speakers, 6 emotions, 50 sentences per emotion (identical texts) | [25] Pan, Tao, Li, "The CASIA audio emotion recognition method for audio/visual emotion challenge 2011", ACII 2011 (a method paper for AVEC 2011; text not read; appears not to be a corpus paper) |

- Only 5 papers were checked. How SER research as a whole cites it was not surveyed.

### 3.4 Origin of the 1,200-clip version

- **EmoBox** (GitHub `emo-box/EmoBox`, commit 39c306b): the CASIA link in the README table points to **Baidu AI Studio dataset 209512**. There is no download code; users are told to place files at `downloads/casia/<speaker>/<emotion>/<number>.wav` (`EmoBox/preprocess/scripts/casia.py`, `data/casia/casia.json`).
- **AI Studio 209512** (opened and read in a browser on 2026-10-23; notes in `sources/aistudio_209512_read_2026-10-23.txt`):
  - Title "CASIA汉语情感音频语料库-1200音频版本" (CASIA Chinese emotional audio corpus, 1,200-clip version). Description: "about 1,200 recordings by 4 people (2 male, 2 female), 6 emotions", with a link to ChineseLDC rid=76.
  - **The uploader is an individual user (display name 千鹤)**, 2023-04-16 13:58:22. License field: 其他 (other). The organisation field names the Institute of Automation, but the uploader is not the Institute.
  - `CASIA.zip`, 54.89 MB. File dates are in 2005.
- **The recipe's Hugging Face mirror** (`Bill13579/casia-mirror`, created 2025-06-29, LICENSE file 0 bytes):
  - The extracted files and the 20 files shown on AI Studio **match in size and modification time (to the second) for all 20**. The extracted `CASIA/` is dated 2023-04-16 13:55:20 (about 3 minutes before the AI Studio upload).
  - -> **The Hugging Face mirror appears to be a re-upload of the AI Studio zip (or its source).** Not compared by hash.
- Content of the 1,200 clips (measured): 4 speakers with personal names (liuchanhg, ZhaoZuoxiang, zhaoquanyin, wangzhe), 6 emotions, sentence numbers 201-250. Transcribing 201-205 with Whisper large-v3 gives **the same sentence for every emotion and speaker** (201 "就是下雨也去", 202 "我马上拿来", etc.; `casia_scripts/transcribe_ids.out`).
  - The 2005 annotation guide of ChineseLDC names the speaker folders w1, w2, m1, m2 and has 5 emotions; the speaker names and 6 emotions of the 1,200-clip version do not match it. Which edition it was cut from is unknown.
  - The 2005 guide says "the first 300 sentences are identical texts", while in the 1,200-clip version sentences 201-250 are identical texts. The numbering appears to differ by edition (unverified).

## 4. Impact (on SER research and on this project)

- **SER research**: CASIA is in benchmarks such as EmoBox and widely used. However, (1) there is no paper by its creators, (2) a paper about another corpus is cited as its source, and (3) the benchmarks' 1,200-clip version derives from an individual's re-upload without the paid license. Its provenance and the legitimacy of its use cannot be confirmed.
- **This project**: the recipe `egs3/casia/cls` downloads this re-upload (the Hugging Face mirror). Submitting it upstream would distribute code that fetches a redistribution whose permission cannot be confirmed.
- **Other DB rows**: the spreadsheet's CASIA figures (1,200 clips, 0.6 hours) were those of the 1,200-clip version, not of the whole corpus. Whether other datasets also took EmoBox's table figures as published values has not been checked.

## 5. Whole corpus and what the recipe uses

| | Whole corpus (ChineseLDC) | Recipe (1,200-clip version, measured) |
|---|---|---|
| Utterances | 9,600 (2010 edition); 12,000 / 10,000 in the 2005 editions | 1,200 |
| Speakers | 4 (2 male, 2 female) | 4 (personal names; gender not in file names) |
| Emotions | 6 (5 in the 2005 annotation guide) | 6, 200 each |
| Sentences | 300 identical + 100 different (2010 edition) | 50 sentences, numbers 201-250; the part with the same sentences read in each emotion (confirmed for 5) |
| Hours | not given in the sources | 0.6352 |
| Format | 16 kHz, 16-bit PCM | 16 kHz mono 16-bit |
| Split | none | by speaker: train 2 speakers 600 / valid 1 speaker 300 / test 1 speaker 300 |

## 6. Decisions for the maintainer and the DB maintainer

**The maintainer's decision (2026-10-23)**: keep the recipe. A warning that it is "unofficial and should not be used", with a summary of the problem, was added at the top of the readme (espnet commit, local). ChineseLDC will not be contacted (no further digging). Items 1 and 5 below are settled by this.

1. **Whether to keep using the recipe** (the maintainer; item 1 of §8 in the review report):
   - (a) use it (download from the current Hugging Face mirror).
   - (b) keep the recipe, but only for people who already have the data (remove the download code).
   - (c) do not use it (do not include the recipe in the repository).
   - Considerations: it is a redistribution of a corpus under a paid license (§3.4), and the terms as of 2024 are unconfirmed.
2. **`espnet_status` and reason codes**: decide according to (1). If it stays `needs_decision`, add `access_paid_or_membership` to the reasons. If it is not used, `excluded` with `not_distributable` or `access_paid_or_membership` (the README's rules say payment alone is not a reason to exclude, so the DB maintainer decides how to state the reason).
3. **`source_type` of E1-E3**: ChineseLDC is a distributor in whose operation the Institute takes part (the site's copyright line), but its documents are not the creators' lab documents. Is `primary` acceptable?
4. **Whether `n_utt_reported` and `labels_discrete_reported` should be `conflicting`**: one could instead treat them as editions (2005 and 2010) and take the newer 2010 edition as authoritative.
5. **Inquiry**: whether to ask ChineseLDC (service@chineseldc.org, the contact on the 2024 page) about current terms and the handling of the 1,200-clip version (the maintainer's decision; if sent, the maintainer sends it).
6. **relations**: whether to make the AI Studio 1,200-clip version a separate row linked with `subset_of casia`, or only mention it in notes.

## 7. Unverified and limitations

- A paper or distribution document by the creators (the lab) themselves.
- ChineseLDC's terms as of 2024 (archived price pages only up to 2020). The site cannot be reached from this environment.
- Hash identity of the 1,200-clip version and the Hugging Face mirror (compared only by size and time for 20 files).
- Which ChineseLDC edition the 1,200-clip version was cut from (speaker names and 6 emotions do not match the 2005 documents).
- Transcripts of sentence numbers 206-250 (only 201-205 were checked).
- **The DB's current Source URL (globalaccentchinese.com/literature.php)**: unreachable on 2026-10-20; on 2026-10-23 an attempt to open its Wayback copy was blocked by the university network as "malware". **Its content was not seen.** Which document the URL came from was not checked either (it came from the spreadsheet).
- The text of Pan, Tao, Li (ACII 2011).
- How SER research as a whole cites it (only 5 papers checked).
- The Journal of Nanjing University 2019 article was fetched as HTML and the relevant part read.

## 8. Background of this investigation (including corrections to earlier reports)

- The review report of 2026-10-20 described CASIA's size and "built for speech synthesis" as coming from "a secondary source (an introduction in a paper)". In fact they were summaries returned by a web-search tool, with no identified source. The maintainer pointed this out.
- "Built for speech synthesis" came from confusing it with the speech-synthesis corpus paper of §3.2; it was not evidence about the emotion corpus, and was withdrawn.
- During the investigation, 9,600 was described as "of unknown origin", but it is the figure on ChineseLDC's 2010 resource page. ChineseLDC was also called "official", but there is no evidence that the creators designated it. Both were corrected.
- Record: `recipe_review/mistakes.md` (entry of 2026-10-23).

## 9. Saved documents (`recipe_review/casia_scripts/sources/`)

| File | Original location | SHA-256 (first 16 hex digits) |
|---|---|---|
| cldc/CLDC-SPC-2005-010_intro.htm | web.archive.org/web/20051214160150/http://www.chineseldc.org:80/doc/CLDC-SPC-2005-010/intro.htm | 6cd769e0faec7b1e |
| cldc/CLDC-SPC-2005-010_label.htm | web.archive.org/web/20051214151014/http://www.chineseldc.org:80/doc/CLDC-SPC-2005-010/label.htm | fb0ef60fbf1d66f8 |
| cldc/CLDC-SPC-2005-010_report.htm | web.archive.org/web/20051214172403/http://www.chineseldc.org:80/doc/CLDC-SPC-2005-010/report.htm | e186551374393a8b |
| cldc/resource_info_rid76_2020.html | web.archive.org/web/20200501144342/http://www.chineseldc.org/resource_info.php?rid=76 | acf61f3ae110971a |
| cldc/home_2024.html | web.archive.org/web/20241126183355/http://www.chineseldc.org/ | 3c82d191d0798f99 |
| cldc/resource_list_20240615040043.html | web.archive.org/web/20240615040043/http://www.chineseldc.org/resource_list.php?begin=0&count=20 | 2e979f1214be1c8e |
| nlpr_gh166.pdf (+ .txt) | web.archive.org/web/20240503152623/https://nlpr.ia.ac.cn/2008papers/gjhy/gh166.pdf | 8a19684c35be17a5 |
| karaiskos08_blizzard.pdf (+ .txt) | https://www.isca-archive.org/blizzard_2008/karaiskos08_blizzard.pdf | c6c20864f5b38567 |
| tao08_blizzard.pdf (+ .txt) | https://www.isca-archive.org/blizzard_2008/tao08_blizzard.pdf | 70aef7b80d03acce |
| blizzard2008.html | http://www.festvox.org/blizzard/blizzard2008.html | - |
| emobox_2406.07162.pdf (+ emobox.txt) | https://arxiv.org/pdf/2406.07162 | 88d5f1115f9b5a5b |
| emobox/README.md, casia.py, casia.json, corpus.cfg | GitHub emo-box/EmoBox commit 39c306b | README 799589fc313f102c |
| arxiv_2001.05908.pdf / arxiv_2103.16456.pdf / arxiv_2310.03992.pdf (+ .txt) | https://arxiv.org/pdf/<ID> (latest versions fetched 2026-10-23) | 344e4844 / 91dc502c / 80dfbccd |
| nju2019.html | https://jns.nju.edu.cn/article/2019/0469-5097/0469-5097-2019-55-5-765.shtml | - |
| aistudio_209512_read_2026-10-23.txt | notes on reading https://aistudio.baidu.com/datasetdetail/209512 (the page itself was not saved) | - |
| cldc/CLDC-SPC-*_intro.htm (and others) | ChineseLDC catalogues of 2005-2008 (fetched while searching for the emotion corpus) | - |
