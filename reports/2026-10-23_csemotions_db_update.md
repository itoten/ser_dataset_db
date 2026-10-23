# CSEMOTIONS: DB 更新用レポート(DB 管理セッションによる検証つきの保存版)

このファイルは `recipe_reports/2026-10-23_csemotions_db_update.md`(レシピ側セッションの報告)の全文に、DB 管理セッションの検証結果を先頭に足したもの。DB の `csemotions` の根拠行は、ここを `via` に指す。報告の本文は一字も直していない。ライセンスを `open` とする判断と、NOTICE の ESD の条件を適用しない判断は ito さんのもの(2026-10-23)。

## 0. DB 管理セッションの検証(2026-10-23)

| 報告の主張 | 検証の方法 | 結果 |
|---|---|---|
| HF のカードは Apache-2.0、固定コミット 19498e62… の NOTICE が ESD(MIT、研究目的のみ)を取り込むと書く。カードに ESD の記述はない。旧名 AIDC-AI/CSEMOTIONS は ATH-MaaS/CSEMOTIONS にリダイレクト | HF の API・NOTICE・README・リダイレクトを取り直した | 一致(コミット SHA も同じ) |
| 4,160 本、10 人、10.198 時間、1.75〜34.2 秒、48 kHz モノラル **16 bit**(カードは 24 bit)、30 秒超 15 本 | `~/data/csemotions` の parquet 8 本を数え直した | 一致(4,160 本、10.1978 時間、1.752〜34.212 秒、PCM_16 のみ、30 秒超 15 本)。カードの 24 bit は実態と違う |
| 文は 1,296 種類、1,293 が複数の話者、どの文も 1 つの感情にしか出ない | `text` 列を集計 | 一致(1,296 / 1,293 / 感情をまたぐ文 0) |
| 分割: train 7 人 2,932 / valid female002 378 / test male003・male004 850、test の文 849 のうち 848、valid の 378 文すべてが train にもある | 手元の parquet から再計算 | 一致 |
| ESD の音との重なり 0(35,000 本と比較) | 自分で別の方法で再検査: ESD の全 35,000 本と CSEMOTIONS の全 4,160 本を、長さ(±30 ms)と包絡の相関 0.9 超で絞り、全体の波形相関で確認 | 候補 0 件。報告と一致(一部どうしの比較はしていない点も同じ) |
| ESD の中国語 350 文との文の重なりなし(最大 0.19) | 保存済みの Whisper 書き起こし 350 文と CSEMOTIONS の 1,296 文で、文字ペアの Jaccard を再計算 | 完全一致 0、最大 0.185。計算は再現した。書き起こしそのもの(Whisper)は検証していない |
| ESD: GitHub の LICENSE は MIT、README は誓約書の送付と「研究目的のみ」を求める。ESD は 350 並行文・10 人の中国語話者 | GitHub から取り直した | 一致 |
| Marco-Voice 報告(arXiv 2508.02038)は CSEMOTIONS を新規の proprietary なデータセット、ESD を別の学習データとして挙げる | 論文を取り直して該当節を読んだ | 一致。ただし論文は「**各話者が 100 の中英プロンプトを読む**」と書くが、実データの中国語の文は 1,296 種類(話者あたり 3 百〜4 百)で、論文の記述と合わない(報告にない食い違い) |

追加で分かったこと(報告にない):
- HF のカードの列名(transcript / speaker_id / gender / prompt_id)は、実際の列(audio / text / emotion / speaker)と違う。
- ESD の DB 行(`esd`)は、すでに `research_only` / `signed_agreement` と README に基づいて記録されている(報告 §6 の 2 への答え)。LICENSE が MIT である点との食い違いは、この登録の範囲外。

検証していないこと: 聴取(ito さんの 28 本)、NOTICE の意図(作者の説明なし)、クリップの一部に ESD の音が入っているか、ESD の Whisper 書き起こしの正しさ、論文に感情ラベルの検証の記述がないこと(索引で該当語を探したが、本文の全読はしていない)。

---

# CSEMOTIONS: DB 更新用レポート

- 作成: 2026-10-23(DB 管理セッション宛)
- 対象 dataset_id: `csemotions`(レシピ `egs3/csemotions/cls`、最初のコミット d0bacb999e2。readme の更新 838c0bf1ea0、ローカル)
- 審査: ito さんの判断(2026-10-23): **ライセンスは `open`(Apache-2.0)**。NOTICE が ESD(研究目的のみ)の取り込みを記すことを明記し、そのうえで open と判断する理由も残す。データに問題はなく、規模が大きく有望。
- 詳しい根拠: `recipe_review/csemotions.md`、計測は `recipe_review/csemotions_scripts/`
- 数値は 2026-10-20 に実データ(`~/data/csemotions`)から取り直したもの。ESD との文の比較と分割の文の共有は 2026-10-23 に追加で計測
- 聴取(ito さん 2026-10-23): 7 感情 × 4 本(別の話者)を聴き、パラ言語情報はしっかりあると判断。ただし文の意味でモデルが判断する可能性があるので、readme に軽い警告を書いた。
- 健康診断: `ok`(2026-10-20 20:44:37〜20:55:33、GPU 1、2 エポック。スコアは動作確認の値で学習の質を表さない)。レシピのデータは変えていない

## 1. 結論

| 項目 | 内容 |
|---|---|
| 状態 | `candidate` → `implemented` |
| 全体とレシピ使用分 | 4,160 本すべて(`remove_long_short` で train の 30 秒超 15 本だけ落ちる) |
| ライセンス | `open`(Apache-2.0、カード)。NOTICE の ESD の条件は、ESD の素材が見つからないので適用しない(§3) |
| 記録する事実 | 文と感情が一対一(1,296 文のどれも 1 つの感情にしか出ない)。ビット深度はカードの 24 bit ではなく 16 bit |

## 2. datasets.csv の更新提案

| 列 | DB の今の値 | 提案 | 根拠 |
|---|---|---|---|
| espnet_status | candidate | implemented | レシピ d0bacb999e2 |
| status_reason_codes | unexamined | NA | — |
| source_url | https://huggingface.co/datasets/AIDC-AI/CSEMOTIONS | https://huggingface.co/datasets/ATH-MaaS/CSEMOTIONS(旧名はここにリダイレクトされる) | HF |
| license_spdx / license_class | Apache-2.0 / open | 変更なし | カード(ito さんの判断) |
| license_note | (空) | 下の案 | NOTICE、§3 |
| n_files_release_measured | (空) | 4160 | 実測 |
| n_speakers_measured | (空) | 10 | 実測(`speaker` 列) |
| label_source | (空) | `human`(声優が演じた感情、`emotion` 列) | カード |
| label_verification | (空) | `NA`(聴取による確認の記述なし) | カード |
| status_note | 「…NOTICE ファイルが ESD(研究目的のみ)を取り込んでいると書いており、どの部分かは未確認。」 | 「レシピは全 4,160 本を使う。NOTICE の ESD(研究目的のみ)は、音・文とも ESD との重なりが見つからないため適用せず、Apache-2.0 として扱う(ito さんの判断 2026-10-23)。」 | §3 |
| notes | 今の文 | 下の案で置き換え | — |
| report_path | (空) | recipe_reports/2026-10-23_csemotions_db_update.md | — |
| status_checked_on / last_updated_on | — | 2026-10-23 | — |

### license_note の案
「カードは Apache-2.0。リポジトリの NOTICE(固定コミット 19498e62…)は、Emotional-Speech-Data(ESD、MIT)を取り込み『研究目的にのみ使える』と書くが、どのクリップかは示さない。2026-10-23 の確認で、ESD の全 35,000 本と同じ長さで波形が一致するクリップはなく、ESD の中国語 350 文(Whisper で書き起こし)と近い文もない(最大でも文字ペアの重なり 19%)。Marco-Voice の報告は CSEMOTIONS を 10 人の声優の新規録音とし、ESD を別の学習データとして挙げる。NOTICE はプロジェクト全体(ESD でも学習)から来た可能性があるが、作者の説明はない。ito さんの判断で open とした。」

### notes の案
「Alibaba AIDC-AI。Marco-Voice の技術報告(arXiv 2508.02038)と同時公開。プロの声優 10 人(男女各 5)のスタジオ録音、7 感情(neutral、happy、angry、sad、surprise、playfulness、fearful)、4,160 本、10.198 時間(実測)、1.75〜34.2 秒、48 kHz・モノラル・**16 bit**(カードは 24 bit)。`text` 列に台本の文があり、1,296 種類の文の 1,293 が複数の話者で読まれる。**どの文も 1 つの感情にしか出ず、文の意味からも感情が分かる**(聴くと声の調子にも感情の違いがあるが、モデルが言語情報で判断する可能性はある)。重複なし。論文の評価用プロンプトは感情ごとに 100(英語・中国語)。」

### 根拠行(evidence)の追加案

| field | value | source_type | source_ref | locator |
|---|---|---|---|---|
| n_files_release_measured | 4160 | measured | measurements/csemotions.json(またはレシピの実測) | parquet 8 本の行数 |
| n_speakers_measured | 10 | measured | 同上 | `speaker` 列 |
| status_reason_codes(superseded の追加) | NA | project_doc | recipe_reports/2026-10-23_csemotions_db_update.md | §1 |

## 3. ESD の条件を適用しない理由(確認したこと)

| 確認 | 方法 | 結果 | ファイル |
|---|---|---|---|
| 音の重なり | ESD のレシピの全 35,000 本(中国語・英語)と CSEMOTIONS の 4,160 本を、長さ(±20 ms)と波形の相関で突き合わせ(`tools/cross_dup.py`) | ほぼ同じ音の組 **0**。クリップの一部どうしの比較はしていない | `cross_esd.out` |
| 文の重なり | ESD の中国語は全話者・全感情で同じ 350 文。話者 0001 の neutral 350 本を Whisper large-v3 で書き起こし、CSEMOTIONS の 1,296 文と文字ペア(bigram)の Jaccard で比較 | 近い文 **0**(最大 0.19) | `esd_text_overlap.out`、`esd_0001_neutral_whisper.tsv` |
| 構成 | — | ESD は 5 感情・各 350 の並行文。CSEMOTIONS は 7 感情(playfulness、fearful を含む)、文は感情ごとに別 | — |
| 論文 | Marco-Voice 報告(arXiv 2508.02038)の本文を読んだ | CSEMOTIONS を「独自の感情音声データセット」、10 人の経験ある声優のスタジオ録音とする。ESD は別の学習データとして並べて挙げる。評価用プロンプトは「ESD と CSEMOTIONS の両方の感情クラスにまたがって」作ったと書く。データに ESD を混ぜた記述はない | `sources/marcovoice_2508.02038.pdf`、`marcovoice.txt` |
| NOTICE | 固定コミットの NOTICE を取得して読んだ | ESD を取り込み、研究目的のみ、と書く。どのクリップかは書かない。カード(README)には ESD の記述がない | `NOTICE_19498e62…`、`README_19498e62….md` |

- ESD 自体: GitHub の LICENSE は MIT。README(`sources/esd_README.md`、2026-10-23 に取得)は「ライセンスの書類に記入して送付」し、「このデータベースは研究目的にのみ使える」と書く。NOTICE の文言はこの README の一文と同じ。ESD の行の扱いは別に確認が要る(このレポートの範囲外)。

## 4. データセット全体とレシピ使用分

| | 全体 | レシピ使用 |
|---|---|---|
| クリップ | 4,160 | 4,160(train は `remove_long_short` 後 2,917) |
| 時間 | 10.198 | 同じ(train の 30 秒超 15 本は `remove_long_short` で落ちる) |
| 話者 | 10 | 話者単位: train 7 人 2,932 / valid female002 378 / test male003・male004 850 |
| 文の共有 | — | test の 849 文のうち 848、valid の 378 文すべてが train でも読まれる |

- `max_epochs` = max(30, ceil(3000 / ceil(2917 / 32))) = 33(設定と一致)。

## 5. recipes.csv

| 列 | 値 |
|---|---|
| recipe | egs3/csemotions/cls |
| first_commit | d0bacb999e2 |
| 備考 | readme にライセンスの判断の理由を追記(838c0bf1ea0、ローカル)。max_epochs 33 |

## 6. 質問

1. `license_note` に判断の経緯をここまで書いてよいか(長い場合は report_path で参照する形にする)。
2. ESD の行(`esd`)の `license_class`: LICENSE は MIT(open)だが、README は書類の送付と「研究目的のみ」を求める。今回の範囲外だが、CSEMOTIONS の判断と合わせて確認が要る。

## 7. 未確認

- 聴取は 7 感情 × 4 本(別の話者、計 28 本、`csemotions_scripts/listen/`)だけ。
- クリップの一部に ESD の音が入っているか(同じ長さの比較だけ)。
- NOTICE の意図(作者の説明なし)。
