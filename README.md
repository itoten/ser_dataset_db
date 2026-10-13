# ser_dataset_db

音声感情認識(SER)データセットのローカルデータベース。CSV を git で版管理する。AI(Claude など)が読んで使うことを第一に作ってあり、情報量と正確性を優先する。

- **正本は `data/*.csv`**。元になった Google スプレッドシート「ser_database」(84行)は 2026-10-12 時点で凍結し、原本を `sheet_import/` に保存している(出所と sha256 は `sheet_import/README.md`)。シートは今後更新しない。
- 対象は SER に使える(使えるかもしれない)データセット全般。ESPnet に実装したかどうかは `espnet_status` で区別する。EEG・ASR 専用のデータセットは対象外。
- 独立した git リポジトリで、リモートはない。`espnet/` フォークや `projects/` とは関係なく、ここに書いた内容は `espnet/` のリポジトリには載らない。

## まず読むもの

| 知りたいこと | 見るもの |
|---|---|
| データセットを一覧で見たい | `views/datasets_wide.csv`(生成物。1行=1データセット、先頭15列はシートと同名) |
| 値の食い違い・不一致 | `views/discrepancies.csv`(生成物) |
| ある値の根拠 | `data/evidence.csv` を `dataset_id` と `field` で絞る |
| 列の意味・型・null の種類 | `schema/columns.csv`、選択肢は `schema/enums.csv`、表のキーは `schema/tables.csv` |
| ESPnet レシピの実測値 | `data/recipes.csv`、`measurements/<recipe>.json` |

## テーブル

| ファイル | 1行が表すもの | キー |
|---|---|---|
| `data/datasets.csv` | 1データセット(正本) | `dataset_id` |
| `data/evidence.csv` | `datasets` の1つの値の根拠 | `evidence_id` = `<dataset_id>/<field>/<NN>` |
| `data/aliases.csv` | 別名(シート上の名前、公式名、旧ラベル、レシピ名など) | `dataset_id`, `alias` |
| `data/relations.csv` | データセット間の関係(版違い・部分集合・別物・同一の疑い) | `dataset_id`, `relation`, `other_dataset_id` |
| `data/recipes.csv` | 1つの egs3 レシピ(`egs3/<recipe>/cls`)。自動列と手書き列がある | `recipe` |
| `data/recipe_labels.csv` | レシピ×ラベル。レシピが捨てたラベルも残す | `recipe`, `label` |
| `data/benchmark_membership.csv` | マルチコーパスのレシピを構成するレシピ | `benchmark_recipe`, `member_recipe`, `role` |

- `recipes.dataset_id` が `datasets` に結びつく。マルチコーパスのレシピは `NA`(個別のレシピが各データセットに結びつく)。`msppodcast_full8` は `msppodcast` の別構成(`single_corpus_variant`)。
- 状態: `espnet_status` は `implemented`(egs3 にレシピあり)/ `candidate` / `needs_decision` / `deferred` / `excluded`。`implemented` 以外は `status_reason_codes`(`;` 区切り)に理由を持ち、`implemented` では `NA`。補足は `status_note`、確認日は `status_checked_on`。
- 行の由来: `in_sheet`(元のシートにあった行か)。シート外の行は `sheet_verified=NA`。`sheet_verified` はシートの Verified 列(人が手作業で確認したか)を原文のまま残したもので、判断には使わない。

## 規約

- **欠損の書き方**: 空欄=未確認。`unknown`=確認したが資料にない、`NA`=該当しない、`none`=無いと確認済み。どれが使えるかは列ごとに `schema/columns.csv` の `nulls` にある。
- **複数値**は `;` 区切り(`labels_discrete_reported`、`languages`、`status_reason_codes` など)。
- **ID**は `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`。実装済みは egs3 のレシピ名と同一。一度コミットした ID は変えない(変えるなら旧 ID を `aliases` に `former_label` で残す)。
- **CSV の形**: UTF-8・BOM なし・LF・行はキー順。直接編集したら `python3 tools/db.py fmt`。
- **ライセンス**: `license_spdx` は資料にある表記を SPDX 識別子(または `LicenseRef-…`)に写したもの。`license_class` は識別子から機械的に決めた区分で、法的な解釈ではない。使う前に `license_note` と一次資料を読むこと。

## 根拠(evidence)の規則

`datasets` の次の列は値ごとに根拠行を持つ: `languages`, `recording_context`, `vocal_content`, `license_spdx`, `access_method`, `raw_audio_available`, `n_utt_reported`, `hours_reported`, `n_speakers_reported`, `n_files_release_measured`, `n_speakers_measured`, `labels_discrete_reported`, `dimensional_attributes`, `espnet_status`, `status_reason_codes`。URL 列と文章列は持たない。

- 1つの列につき `is_canonical=true` の行がちょうど1つあり、その値が `datasets` のセルと一致する。
- `source_type` の強さ: `user` > `measured` > `primary`(一次資料の原文) > `project_doc`(このプロジェクトの調査メモ。`new_corpora/` のレポートなど) > `secondary` > `sheet`。`locator` は場所の目印(25語以内)、`via` はどの文書を経由して知ったか。
- 新しい事実が出たら古い行を消さずに `superseded` にして新しい行を足す。資料同士が食い違い決められないときは `conflicting` の行を2つ以上残し、`datasets` のセルを `conflicting` にする(例: EmoDB と TurEV-DB のライセンス)。
- `*_measured` の列は `measured` の根拠だけ、`*_reported` の列は `measured` を使えない(公表値と実測値は別の列で並べる)。
- 資料にないことは書かない。URL・題名を推測で作らない。
- 実測値(件数・時間・話者数)の唯一の根拠は `measurements/<recipe>.json` とダウンロードしたファイルの実測。

## 検証と更新

```bash
/usr/bin/python3 tools/validate.py             # egs3 をブランチから読み、実測との照合まで行う
/usr/bin/python3 tools/validate.py --offline   # espnet リポジトリを読まない
/usr/bin/python3 tools/views.py                # views/ を作り直す
/usr/bin/python3 tools/db.py get|set|add|fmt   # 1行の閲覧・編集
```

- システムの Python 3.10(`/usr/bin/python3`、PyYAML あり)で動かす。pandas は使わない。
- `git config core.hooksPath tools/hooks` により、コミット前に `tools/validate.py` が走る。`--no-verify` は使わない。
- egs3 のレシピは作業ツリーではなく `espnet` の `ser/cross-corpus` ブランチから読む(ブランチ名は `tools/egs3.py` の1か所)。
- 実測は `cd espnet && pixi run python ../espnet_work/ser_dataset_db/tools/measure.py --all`、続けて `python3 tools/sync.py` で `recipes.csv` の自動列を更新し、手書き列を人が埋める。
- `validate.py` は、形式・型と選択肢・キーと外部キー・別名の重複・根拠の規則・実装状態と egs3 の一致・`recipes.csv` / `recipe_labels.csv` と `measurements/*.json` の一致・`views/` が最新かを検査する。`measurements/` と手元の出力(`~/data/...`)が今も一致するかは検査しない。
- 値を変えるときは必ず根拠行を足す。1データセットまたは1回の確認作業ごとに1コミットとし、メッセージには何が問題だったかと根拠を書く。

## 現状(2026-10-12)

137データセット(シート由来84・シート外53)。`implemented` 53、`excluded` 81、`candidate` 1(`whiser`)、`needs_decision` 1(`casia`)、`deferred` 1(`narrative_dialogue`)。MSP-Podcast 論文(arXiv 2509.09791v1)の Table I の28コーパスは全て含む。除外のうち、シートが「申請制」と記すだけで個別には確認していないものは `status_reason_codes` が `access_*` で `status_note` に「個別には確認していない」とある。

既知の注意:

- 実装済み35件は一次資料・実測と照合済み(S7)。それ以外のシート由来の行は、シートの記載か調査メモに基づく値が多く、一次資料で再確認していない。
- シート外の除外候補の URL は調査時の検索結果で名前が一致したもので、今回アクセスし直してはいない。
- 公表値と実測値が食い違う箇所は `views/discrepancies.csv` にある。レシピは長さやラベルで絞るため、`n_utt_reported` とレシピの件数が一致しないのは普通のことが多い。
