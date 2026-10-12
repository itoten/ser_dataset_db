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
