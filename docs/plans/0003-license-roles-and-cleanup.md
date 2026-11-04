# 0003 ライセンスによる役割の選択と、local の片づけ

状態: 計画(未着手)
関連: [discussions/0002](../discussions/0002-separate-implementation-and-use.md)(8 節)、[discussions/0003](../discussions/0003-license-classes.md)
最終更新: 2026-11-04

データセットの選別の道具(`local/dataset_filtering/`)は済み。ここでは、その続きと、`local/` の片づけをまとめる。

## 1. 学習・評価の役割を、選べるように実装する

- 選別を通ったデータセットに、ライセンスの区分から学習・評価の役割をつける。SA、GPL、ODbL、research_only などの扱いは、設定で選べるようにする(例: SA を学習に入れる案 1、モデルを CC BY-SA 4.0 で出す案 2、入れない案)。
- 区分は `open` / `nc` / `unclear`(+ 未確認)が決定済み。SA・GPL・ODbL・独自の継承を別の区分(例: `sa`)に分けるかは、議論 0003 の 8.4 を決めてから。
- 置き場所は `local/`。`dataset_filtering` の新しい段にするか、別の出力にするかは実装のときに決める。

## 2. 決めてから進めること

- GPL と ODbL の扱い(原文は議論 0003 の 3.3・3.4 で読んだ)。CREMA-D は DbCL の本文を読む。
- `other` の 5 件(`atthack`、`basis_global_emotions`、`galgame_speech_ser`、`hindi_ser_vishlb`、`qlean_japanese_emotional`)の文言を読んで、`open` / `nc` / `unclear` のどれにするか。
- NC のデータを評価だけに使うか。

## 3. DB の作業(判別不明を減らす)

選別で判別不明のまま通した 9 件の、`speech_production`(録音のしかた)とラベルの付け手を資料で確かめる。KazEmoTTS(約 75 時間)が量の大部分を占める。資料にない(`unknown`)ものは、論文の本文などを当たる。DB への登録は、DB 管理の手順(出典と根拠の行)で行う。

## 4. `local/` の片づけ

- 古い `dataset_use.csv`、`license_class.csv`、`license_class.py` を消す。未調査 152 件のメモは `dataset_use.csv` にしかないので、候補を決めるときの材料に残すかを先に決める。
- 確認 PR を作る古いスクリプト(`verification_tools/`)は、[計画 0002](0002-verification-pr-tool.md) の道具ができてから消す。
- `local/license/`(区分の定義と対応表)は、1 の役割の実装で使う。
