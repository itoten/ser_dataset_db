# sheet_import

The original of the Google spreadsheet "ser_database", stored exactly as downloaded. **Do not edit it** (its bytes must stay identical).

| Item | Value |
|---|---|
| File | `2026-10-12_ser_database_SER_Datasets.csv` |
| Sheet ID | `16KIVViHe7JhMWdzGQHBBqLPWhHceW6i9MU5pccB5Jao` |
| Tab | SER Datasets (`gid=0`) |
| Downloaded | 2026-10-12 (downloaded as CSV from the sheet by the project maintainer) |
| sha256 | `f94d19e2ae5416d8ed1fc5feab593167908b87f6f228ab8e2215960014fab619` |
| Size | 44221 bytes, header + 84 rows, 15 columns |
| Line endings | CRLF, no trailing newline, no BOM |
| Columns | `Verified, Dataset, License, Language, Source, Total Hours, Utterances, Speakers, Discrete Emotions, Dimensional Emotions, Other Annotations, Source URL, Notes, Paper URL, ESPnet Implemented` |

- The `Verified` column says whether someone checked the information by hand (the maintainer's explanation).
- The `ESPnet Implemented` column was filled in by the maintainer at download time. The "Polish (EmoBox)" row says FALSE, but it is in fact the same corpus as the egs3 recipe `polishemo` (the EmoBox README cites the same MOST Wiedzy page as its source).
- The original is kept as is, so this discrepancy is not corrected in it.

## Import rules (applied once by an import script; the script was deleted and survives in git history, commit 041d798)

Each of the 84 rows became one `datasets` row (no rows were merged; Polish (EmoBox) is the single row `polishemo`).

| Spreadsheet column | Imported into | Conversion |
|---|---|---|
| Verified | `sheet_verified` | As is. Not used for decisions |
| Dataset | `name`, `aliases` (`sheet_name`) | `dataset_id` is the egs3 recipe name for the 34 rows with a matching recipe and for Polish; otherwise a slug of lower-case letters and digits. `€motion` -> `emotion_origlia2010`, `CH-SIMS v2.0` -> `chsims2`, `Belfast Database` -> `belfast` |
| License | `license_spdx`, `license_class` | Mapped to SPDX identifiers with a table. `license_class` follows from `derived` in `enums.csv` |
| Language | `languages` | ISO 639-3. `Multilingual` -> `mul`, `Other` -> `unknown`, `Mexican Spanish` -> `spa` (the original wording in `language_note`) |
| Source | `recording_context` | Mapped to enum values with a table |
| Total Hours / Utterances / Speakers | `hours_reported` / `n_utt_reported` / `n_speakers_reported` | As is |
| Discrete Emotions | `labels_discrete_reported` | Only comma-separated lists of lower-case words became `;`-separated lists; prose stayed as is in `labels_discrete_note` |
| Dimensional Emotions | `dimensional_attributes` | Same (prose in `dimensional_note`). `None` -> `none` |
| Other Annotations | `annotations_other` | As is. `None` -> `none` |
| Source URL / Paper URL | `source_url` / `paper_url` | As is |
| Notes | `sheet_notes` | As is |
| ESPnet Implemented | (not imported) | `espnet_status` is decided by comparison with egs3 (the git branch), because this column contains errors |

- Typed values have `evidence` rows (`source_type=sheet`, location "line N, column X"). Columns kept as prose have no evidence.
- Leading and trailing spaces were removed (one Notes value). No other value was altered.
- `espnet_status` was set to the provisional value `deferred` (reason `not_individually_checked`) right after the import, and later updated to the actual status.
