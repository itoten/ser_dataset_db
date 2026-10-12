# sheet_import

Googleスプレッドシート「ser_database」の原本を、取得したまま保存したもの。**編集しない**(バイト一致を保つ)。

| 項目 | 値 |
|---|---|
| ファイル | `2026-10-12_ser_database_SER_Datasets.csv` |
| シートID | `16KIVViHe7JhMWdzGQHBBqLPWhHceW6i9MU5pccB5Jao` |
| タブ | SER Datasets(`gid=0`) |
| 取得日 | 2026-10-12(itotenさんがシートからCSVでダウンロード) |
| sha256 | `f94d19e2ae5416d8ed1fc5feab593167908b87f6f228ab8e2215960014fab619` |
| 大きさ | 44221 バイト、ヘッダ + 84行、15列 |
| 改行 | CRLF、末尾に改行なし、BOMなし |
| 列 | `Verified, Dataset, License, Language, Source, Total Hours, Utterances, Speakers, Discrete Emotions, Dimensional Emotions, Other Annotations, Source URL, Notes, Paper URL, ESPnet Implemented` |

- `Verified` 列は、人が手作業で情報を確認したかどうか(itotenさんの説明)。
- `ESPnet Implemented` 列は取得時点でitotenさんが入れたもの。「Polish (EmoBox)」行は FALSE だが、実際は egs3 の `polishemo` と同じコーパス(EmoBox README が出典に同じ MOST Wiedzy のページを挙げている)。
- 原本のまま残すので、この食い違いは原本では直さない。

## DBへの取り込み規則(`tools/import_sheet.py` で1回だけ実行、S10で削除予定)

シートの84行は、1行が1つの `datasets` 行になる(行の合併はない。Polish (EmoBox) は `polishemo` として1行)。

| シートの列 | 取り込み先 | 変換 |
|---|---|---|
| Verified | `sheet_verified` | そのまま。判断には使わない |
| Dataset | `name`、`aliases`(`sheet_name`) | `dataset_id` は egs3 レシピ名が対応する34件+Polishはその名前、それ以外は小文字英数字のみの slug。`€motion`→`emotion_origlia2010`、`CH-SIMS v2.0`→`chsims2`、`Belfast Database`→`belfast` |
| License | `license_spdx`、`license_class` | 対応表で SPDX 識別子へ。`license_class` は `enums.csv` の derived から決まる |
| Language | `languages` | ISO 639-3。`Multilingual`→`mul`、`Other`→`unknown`、`Mexican Spanish`→`spa`(元の表記は `language_note`) |
| Source | `recording_context` | 対応表で enum 値へ |
| Total Hours / Utterances / Speakers | `hours_reported` / `n_utt_reported` / `n_speakers_reported` | そのまま |
| Discrete Emotions | `labels_discrete_reported` | 小文字の語をカンマ区切りで並べた形のものだけ `;` 区切りに。文章はそのまま `labels_discrete_note` |
| Dimensional Emotions | `dimensional_attributes` | 同上(文章は `dimensional_note`)。`None`→`none` |
| Other Annotations | `annotations_other` | そのまま。`None`→`none` |
| Source URL / Paper URL | `source_url` / `paper_url` | そのまま |
| Notes | `sheet_notes` | そのまま |
| ESPnet Implemented | (取り込まない) | `espnet_status` は egs3(gitブランチ)との照合で決める(S7)。誤りを含むため |

- 型付きの値は `evidence` 行(`source_type=sheet`、場所は「line N, column X」)を持つ。文章のまま残した列は evidence を持たない。
- 前後の空白は取り除いた(Notes の1件)。それ以外の値は改変していない。
- `espnet_status` は取り込み直後の仮の値 `deferred`(理由 `not_individually_checked`)。S7以降で実際の状態に更新する。
