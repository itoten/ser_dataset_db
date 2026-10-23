# CASIA: 出典と入手経路の調査(DB 管理セッションによる検証つきの保存版)

このファイルは `recipe_reports/2026-10-23_casia_db_update.md`(レシピ側セッションの報告)の全文に、DB 管理セッションの検証結果を先頭に足したもの。DB の `casia` の根拠行はここを `via` に指す。報告の本文は一字も直していない。資料の原本は `espnet_work/recipe_review/casia_scripts/sources/` にあり、このリポジトリには含まれない(SHA-256 は報告 §9)。

## 0. DB 管理セッションの検証(2026-10-23)

報告の事実は、原本または一次資料を自分で開いて照合した。人手の判断(ito さんの判断)は検証していない。

| 報告の主張 | 検証の方法 | 結果 |
|---|---|---|
| ChineseLDC の資源ページ(2020-05-01 保存): 単位 自動化所、4 人・6 感情・9,600 句(300 同文 + 100 異文)、授権費 5,000 / 15,000 / 35,000 / 105,000 元、加入 2008-06-11、更新 2010-10-09 | Wayback を取り直して全文を読んだ。保存版の SHA-256 も一致 | 一致。ページ下部の著作権表示は「中国中文信息学会」で、報告 §3.1 が書く 2024 年のトップページ(「中国科学院自动化研究所」)とは違う(2024 年の保存版を読んで確認。年代で変わった) |
| 2005 年のカタログ: 12,000 句・六種情緒・300 同文 + 200 異文(intro)、5 感情・各 500 句・計 10,000 句・w1/w2/m1/m2・16 kHz 16 bit(label)、SNR 約 35 dB(report) | 保存版の 3 本を読んだ(ハッシュ一致を確認) | 一致。3 本とも聴取検証の記述なし(「検証していない」ではなく「記述がない」) |
| Tao ら 2008 は女性 1 人の音声合成用コーパスの論文で "emotion" が 1 度も出ない | PDF を Wayback から取り直し(SHA-256 一致)、全文検索 | 一致。"emotion" は 0 回 |
| EmoBox の README と論文が AI Studio 209512 にリンク、論文の引用 [10] が Tao ら 2008 | GitHub の README と arXiv 2406.07162 を取り直して確認 | 一致(表: Act / Mandarin / 6 / 4 / 1200 / 0.6、[10] = Tao, Liu, Zhang, Jia) |
| 他の論文の引用(arXiv 2103.16456 は「Blizzard Challenge, 2005」、2310.03992 は Zhang と Jia のみの 2008、2001.05908 は出典なし) | arXiv の PDF を取り直して引用箇所を検索 | 一致 |
| AI Studio 209512: 公開者「千鹤」、2023-04-16 13:58:22、ライセンス欄「其他」、組織欄に自動化所、CASIA.zip 54.89 MB、説明に rid=76 のリンク | ブラウザでページを開いて読んだ | 一致 |
| HF ミラー `Bill13579/casia-mirror`: 2025-06-29 作成、LICENSE が 0 バイト | HF の API とヘッダーで確認 | 一致(`license:other` のタグ付き) |
| ミラーの展開物と AI Studio の表示 20 ファイルがサイズ・更新日時で一致 | 手元の `~/data/casia` の 20 ファイルを照合 | **20 / 20 一致**。ハッシュでの照合はしていない(報告のとおり) |
| 1,200 本版の中身: 1,200 本・4 人・6 感情各 200・文番号 201〜250・16 kHz モノラル・0.6352 時間 | `~/data/casia` を数え直した | 一致(ファイル名から話者 4 人 × 各感情 50 本、1,200 の重複ファイル名なし) |

検証していないこと: 2024 年時点の ChineseLDC の条件(サイトに接続できない)、ミラーと AI Studio の zip のハッシュ一致、文番号 206〜250 の書き起こし、Whisper の書き起こし(201〜205)、`recipe_review/mistakes.md` の記述。

DB 管理セッションが §6 に答えた内容:
1. レシピは ito さんの判断(2026-10-23)で残されたので、`espnet_status` は `implemented`(レシピがあるという意味)とし、警告は `status_note` と `known_issues` の先頭に置く。
2. E1〜E3 の `source_type` は `primary`(配布団体のカタログ)。作成者の研究室自身の文書ではない点を根拠行の note に書く。
3. `n_utt_reported` は最新の 9,600(2010 年版)を採り、2005 年版の 12,000 と 10,000 は `conflicting` の別行に残す。`labels_discrete_reported` は 6 感情の一覧(AI Studio の説明)を採り、2005 年の 5 感情は `conflicting` の別行に残す。
4. 1,200 本版は別の dataset 行にせず、notes に書く。

---

# CASIA: DB 更新用レポート(出典と入手経路の調査)

- 作成: 2026-10-23(DB 管理セッション宛)
- 対象 dataset_id: `casia`(レシピ `egs3/casia/cls`、最初のコミット 1556c1c8ce4)
- 依頼: ito さん(2026-10-23)「ここまで確認してきたことも踏まえ DB に登録しよう。全部は載り切らないかもしれないからレポートとしても残しておこう」
- 詳しい根拠: `recipe_review/casia.md` の §0a。取得した資料はすべて `recipe_review/casia_scripts/sources/` に保存した(§9 に一覧と SHA-256)
- **この報告の書き方**: 自分で開いて読んだ資料だけを根拠にする。資料ごとに「読めた範囲」を書き、推定には「〜とみられる」と書いて事実と分ける。Web 検索ツールの要約文は根拠にしていない(§8 の経緯)。
- **まだ決まっていないこと**: レシピを使い続けるかと DB の `espnet_status` は、ito さんが決めていない。§6 に選択肢として書き、§2 の提案には含めない。

## 1. 結論

| 項目 | 分かったこと | 確かさ |
|---|---|---|
| コーパスの作成元 | 中国科学院自動化所(CASIA)。配布団体 ChineseLDC のカタログが「开发单位 中国科学院自动化所、开发时间 2005 年」と書く | ChineseLDC の記載(作成者の文書は未発見) |
| ChineseLDC と自動化所 | ChineseLDC のサイトの著作権表示が「中国科学院自动化研究所」、連絡先が自動化所の所在地(2024 年の保存版) | ChineseLDC のサイト自身の記載 |
| 全体の規模 | 4 人・6 感情・9,600 発話(300 の同じ文 + 100 の違う文)。ChineseLDC の資源ページ(2010-10-09 更新)。2005 年のカタログは 12,000 / 10,000・5 感情で食い違う | 版により違う |
| 入手条件 | **ChineseLDC での有償の利用許諾**: 国内非営利 5,000 元、国内営利 15,000 元、国外非営利 35,000 元、国外営利 105,000 元(2020-05-01 保存のページ) | 2024 年時点の条件は未確認 |
| **SER 論文が引く出典** | **"Design of Speech Corpus for Mandarin Text to Speech"(Tao ら 2008)は、女性話者 1 人の音声合成用コーパスの論文で、感情コーパスの記述がない**。EmoBox を含む SER の論文が、これを CASIA 感情コーパスの出典として引いている | 論文本文を読んで確認 |
| **広く使われる 1,200 本版の出どころ** | 百度 AI Studio に**個人(表示名「千鹤」)が 2023-04-16 に公開した再アップロード**。EmoBox の README はここにリンクする。レシピの HF ミラーはこれと同じファイルとみられる | AI Studio のページを読み、20 ファイルを照合 |
| 再配布の許可 | 無償の再配布を認める記述は、見つけたどの資料にもない | — |

要するに、**CASIA(感情)は、作成者による論文がなく、SER 研究では別の論文が出典として引かれ、ベンチマークで使われる 1,200 本版は有償の許諾を経ない個人の再アップロードが元になっている**。

## 2. datasets.csv の更新提案

`espnet_status` と `status_reason_codes` は §6 で決まってから更新する(今は `needs_decision` / `access_unofficial_mirror_only` のまま)。

| 列 | DB の今の値 | 提案 | 根拠(§3 の番号) |
|---|---|---|---|
| source_url | https://globalaccentchinese.com/literature.php | http://www.chineseldc.org/resource_info.php?rid=76(今はこの環境から接続できない。保存版は §9) | E1。今の値は根拠がない(§7) |
| license_spdx | LicenseRef-proprietary-restricted(根拠はシート) | 値は同じ。根拠を `primary` の行(E1)に置き換え、シートの行は `superseded` | E1 |
| license_class | restricted | 変更なし(派生列) | — |
| access_method | (空) | `paid_or_membership`(ChineseLDC の有償の許諾)。非公式の再配布の存在は notes に書く | E1 |
| n_utt_reported | 1200(シート) | `conflicting`: 9,600(E1、2010 年版)、12,000(E2、2005 年の資源簡介)、10,000(E3、2005 年の標注規範)。シートの 1200 は 1,200 本版の数なので `superseded`(note に「1,200 本版の数」) | E1〜E3 |
| n_speakers_reported | 4(シート) | 4(E1、E3。E3 は男女 2 人ずつ) | E1、E3 |
| labels_discrete_reported | anger;fear;happiness;sadness;surprise;neutral(シート) | `conflicting`: 6 感情(E1 は数だけ。一覧は E4 の再アップロードの説明: neutral、happy、sad、angry、fearful、surprised)と 5 感情(E3: 高兴、悲哀、生气、惊吓、中性) | E1、E3、E4 |
| hours_reported | 0.6(シート) | 全体の時間は資料にない → `unknown`。0.6 は 1,200 本版の値(実測 0.6352)で `superseded` | — |
| n_files_release_measured | (空) | 1200(レシピの入手物 = HF ミラー) | 実測 |
| n_speakers_measured | (空) | 4 | 実測(ファイル名) |
| label_source | (空) | `human`(俳優が感情を演じて読む。E3) | E3 |
| label_verification | (空) | `unknown`(聴取テストの記述は資料にない) | — |
| paper_url | (空) | 空のまま(**作成者による論文が見つからない**)。SER 論文が引く Tao ら 2008 は別のコーパスの論文なので入れない | §4 |
| status_note | 「99_final_report は…」 | 下の案 | — |
| notes | (空) | 下の案 | — |
| report_path | (空) | recipe_reports/2026-10-23_casia_db_update.md | — |
| status_checked_on / last_updated_on | — | 2026-10-23 | — |

### status_note の案
「ChineseLDC(CLDC-SPC-2005-010)で有償の許諾。広く使われる 1,200 本版(EmoBox など)は個人による再アップロード(百度 AI Studio 209512、2023)が元で、レシピの HF ミラーも同じとみられる。SER 論文が出典に引く Tao ら 2008 は音声合成コーパスの論文で感情コーパスの出典ではない。レシピを使うかは未決(2026-10-23)。」

### notes の案
「中国科学院自動化所の『CASIA汉语情感语料库』(ChineseLDC CLDC-SPC-2005-010、2005 年開発)。プロの話者 4 人(男女 2 人ずつ)が同じ文と感情に合った文を感情を付けて読む演技音声、16 kHz・16 bit。規模は版で違う(2005 年のカタログ: 6 感情・12,000 / 5 感情・10,000、2010 年更新の資源ページ: 6 感情・9,600)。**作成者による論文は見つからない。SER の論文は "Design of Speech Corpus for Mandarin Text to Speech"(Tao, Liu, Zhang, Jia, Blizzard Challenge 2008)を出典に引くが、これは女性話者 1 人・5,000 文の音声合成用コーパスの論文で感情の記述はない**(引用も著者・年が論文ごとに違う)。EmoBox などが使う 1,200 本版(4 人 × 6 感情 × 文番号 201〜250。201〜205 は同じ文を感情で読み分けたものと確認)は、作成元でない個人が百度 AI Studio に再アップロードしたもの(2023-04-16)。無償の再配布を認める記述は見つからない(2026-10-23 調査)。」

### 根拠行(evidence)の追加案

| ID 案 | field | value | source_type | source_ref | locator | via |
|---|---|---|---|---|---|---|
| E1 | license_spdx / access_method / n_utt_reported / n_speakers_reported | LicenseRef-proprietary-restricted / paid_or_membership / 9600 / 4 | primary | http://www.chineseldc.org/resource_info.php?rid=76 | Wayback 2020-05-01 保存。摘要と授权费の欄 | web.archive.org/web/20200501144342/… |
| E2 | n_utt_reported | 12000 | primary | http://www.chineseldc.org/doc/CLDC-SPC-2005-010/intro.htm | Wayback 2005-12-14。（5）开发规模 | web.archive.org |
| E3 | n_utt_reported / n_speakers_reported / labels_discrete_reported / label_source | 10000 / 4 / 5 感情 / human | primary | http://www.chineseldc.org/doc/CLDC-SPC-2005-010/label.htm | Wayback 2005-12-14。1、语料内容 | web.archive.org |
| E4 | labels_discrete_reported | neutral;happy;sad;angry;fearful;surprised | secondary | https://aistudio.baidu.com/datasetdetail/209512 | 説明文(個人の再アップロード) | EmoBox README |

- E1〜E3 は ChineseLDC の文書なので `primary` とした。ただし作成者(研究室)自身の文書ではない点を note に書く(§6 の質問 3)。
- 保存版の URL は §9。

## 3. 根拠(読んだ資料と、読めた範囲)

### 3.1 ChineseLDC(配布団体)のカタログ

| # | 資料 | 読めた範囲 | 書かれていること |
|---|---|---|---|
| E2 | CLDC-SPC-2005-010 intro.htm(2005-12-14 保存) | 全文 | 资源名称「汉语情感语料库」、开发单位 自動化所、开发时间 2005 年、**四个专业发音人、六种情绪、共 12,000 句**、300 句相同文本と 200 句不同文本 |
| E3 | 同 label.htm(標注規範、2005-12-14 保存) | 本文(図は除く) | **5 種の感情**(高兴、悲哀、生气、惊吓、中性)。各感情 500 句 = 前 300 句は同じ文、後 200 句は文の意味から感情が分かる文。録音者は男女 2 人ずつ(w1、w2、m1、m2)、1 人 2,500 句、**計 10,000 句**、16 kHz・16 bit・PCM。音節境界と F0 の tag ファイル付き |
| — | 同 report.htm(技術文書、2005-12-14 保存) | 本文 | label と同じ 5 感情・500 句の設計。録音環境の SNR 約 35 dB。目的は感情状態による韻律・音響の分析、感情認識と感情合成の研究 |
| E1 | resource_info.php?rid=76(2020-05-01 保存。2019-11-25 と 2020-01-24 の保存も同じ内容のハッシュ) | 全文 | 资源名称「**CASIA汉语情感语料库**」、序列号 CLDC-SPC-2005-010、**4 人・6 感情・9,600 句(300 句相同文本 + 100 句不同文本)**、加入 2008-06-11、更新 2010-10-09、**授权费**(§1 の表) |
| — | トップページ(2024-11-26 保存) | 全文 | 「**版权所有：中国科学院自动化研究所**」。連絡先 北京市海淀区中关村东路 95 号 智能化大厦 514 室。お知らせ「自動化所の組み込み音声合成システムは CASIA汉语情感语料库 などを学習に使った」。CLDC は中国中文信息学会の委員会が発起した非営利の団体と自己紹介 |
| — | 資源一覧(2023-12-06、2024-06-15 保存) | 1 ページ目 | 「CASIA汉语情感语料库」が載っている(資源総数 99) |

- 9,600 = 4 × 6 × 400、12,000 = 4 × 6 × 500、10,000 = 4 × 5 × 500 で、各版の中では計算が合う。版が変わった理由は書かれていない。
- 価格の載った資源ページの保存は 2020-05-01 が最後。2023 年の保存(URL に余計な文字が付いたもの)は中身が空で、**2024 年時点の条件は確認できていない**。
- サイトはこの環境(大学のネットワーク)から接続できない(タイムアウト)。止まっているのか、地域・ネットワークの制限かは分からない。

### 3.2 SER 論文が出典に引く論文(別のコーパス)

- **Tao, Liu, Zhang, Jia "Design of Speech Corpus for Mandarin Text to Speech"**。自動化所 NLPR のサイトの PDF(`nlpr.ia.ac.cn/2008papers/gjhy/gh166.pdf`)を Wayback Machine(2024-05-03 保存)で取得し、**全文を読んだ**(PDF の作成日 2008-08-27)。
  - 要旨: 音声合成研究のための CASIA の Mandarin コーパス。プロの女性話者がスタジオで録音、音素文脈のバランスを取った 5,000 文、約 7 時間。Blizzard Challenge 2008 の共通コーパスとして配布。
  - 話者の選び方: 男女 8 人の候補から 30 歳の女性 1 人を選んだ。
  - **"emotion" という語は 1 度も出てこない。**
- Blizzard 2008 の主催者の論文(Karaiskos, King, Clark, Mayo、ISCA Archive の PDF を読んだ): 2008 年は第 4 回。Mandarin のデータは「自動化所 NLPR が出した 6.5 時間の女性話者 1 人のデータ」。
- 同じ著者らの "The WISTON Text to Speech System for Blizzard 2008"(ISCA Archive の PDF を読んだ): Mandarin のデータは CASIA 提供の 4,500 発話・約 8.5 時間の中立な読み上げ、ライセンスの参照先は `www.speakit.cn/corpus/license.html`(ChineseLDC ではない)。
- Blizzard 2008 の論文一覧(festvox.org の公式ページと ISCA Archive の一覧)に "Design of Speech Corpus…" は載っていない。発表の形は分からない。

### 3.3 SER 論文の書き方(本文を読んだもの)

| 論文 | CASIA の説明 | 出典の書き方 |
|---|---|---|
| EmoBox(arXiv 2406.07162。掲載先は PDF に書かれていない) | 表: Act、Mandarin、6 感情、4 人、1,200、0.6 時間 | [10] **J. Tao, F. Liu, M. Zhang, H. Jia**, "Design of speech corpus for Mandarin text to speech", The Blizzard Challenge Workshop, 2008 |
| arXiv 2103.16456(Deep Self-Learning) | 9,600 発話、4 人(男女 2 人ずつ)、6 感情。実験は 300 文の 7,200 発話 | [26] J. Tao, F. Liu, M. Zhang, H. Jia, …, Proc. the 4th Workshop on Blizzard Challenge, **2005**(第 4 回は 2008 年。年が誤り) |
| arXiv 2310.03992(LIDAN) | 4 人(男女 2 人ずつ)、**1,200 サンプル、各話者 300 文**(数が合わない) | [27] **J. Zhang and H. Jia**, …, The blizzard challenge 2008 workshop, 2008(4 人の著者のうち 2 人) |
| arXiv 2001.05908 | 自動化所が録音。プロの話者 4 人、6 種類の感情(列挙は 5 つで fear がない)、計 9,600 | **出典なし** |
| 南京大学学报(自然科学版)55(5), 765〜(2019)「跨语言语料库的语音情感识别对比研究」 | 自動化所の汉语情感语料库、4 人・6 感情、各感情 50 句(同じ文) | [25] Pan, Tao, Li, "The CASIA audio emotion recognition method for audio/visual emotion challenge 2011", ACII 2011(AVEC 2011 の手法論文。本文は未読。コーパスの論文ではないとみられる) |

- 調べたのは 5 本だけ。SER 研究全体でどう引かれているかの集計はしていない。

### 3.4 1,200 本版の出どころ

- **EmoBox**(GitHub `emo-box/EmoBox`、コミット 39c306b): README の表の CASIA のリンク先は **百度 AI Studio データセット 209512**。入手のコードはなく、`downloads/casia/<話者>/<感情>/<番号>.wav` に置くよう指示するだけ(`EmoBox/preprocess/scripts/casia.py`、`data/casia/casia.json`)。
- **AI Studio 209512**(2026-10-23 にブラウザで開いて読んだ。控えは `sources/aistudio_209512_read_2026-10-23.txt`):
  - 題名「CASIA汉语情感音频语料库-1200音频版本」。説明「4 人(男 2、女 2)の約 1,200 の音声、6 感情」と、ChineseLDC の rid=76 へのリンク。
  - **公開者は個人ユーザー(表示名「千鹤」)**、2023-04-16 13:58:22。ライセンスの欄は「其他」。組織の欄に自動化所の名前があるが、公開者は自動化所ではない。
  - `CASIA.zip` 54.89 MB。ファイルの日付は 2005 年。
- **レシピの HF ミラー**(`Bill13579/casia-mirror`、2025-06-29 作成、LICENSE ファイルは 0 バイト):
  - 展開したファイルと AI Studio に表示された 20 ファイルで、**サイズと更新日時(秒まで)が 20 本すべて一致**。展開した `CASIA/` の日時は 2023-04-16 13:55:20(AI Studio の公開の約 3 分前)。
  - → **HF ミラーは AI Studio の zip(またはその元)の再アップロードとみられる**。ハッシュでの照合はしていない。
- 1,200 本の中身(実測): 話者は人名 4 人(liuchanhg、ZhaoZuoxiang、zhaoquanyin、wangzhe)、6 感情、文番号 201〜250。201〜205 を Whisper large-v3 で書き起こすと、**どの感情・話者でも同じ文**(201「就是下雨也去」、202「我马上拿来」など、`casia_scripts/transcribe_ids.out`)。
  - ChineseLDC の 2005 年の標注規範では話者のフォルダが w1・w2・m1・m2、感情は 5 つ。1,200 本版の話者名と 6 感情はこれと合わない。どの版から切り出したかは分からない。
  - 2005 年の標注規範は「前 300 句が同じ文」と書くが、1,200 本版は 201〜250 番が同じ文。番号の付け方が版で違うとみられる(確かめていない)。

## 4. 影響(SER 研究と、このプロジェクト)

- **SER 研究**: CASIA は EmoBox などのベンチマークに入り、広く使われている。しかし、(1) 作成者による論文がなく、(2) 別のコーパスの論文が出典として引かれ、(3) ベンチマークの 1,200 本版は有償の許諾を経ない個人の再アップロードが元。データの来歴と利用の正当性が確かめられない。
- **このプロジェクト**: レシピ `egs3/casia/cls` は、この再アップロード(HF ミラー)からダウンロードする。upstream に出すと、許諾の確認できない再配布物を取るコードを配ることになる。
- **DB のほかの行**: シートの CASIA の行の数(1,200 本・0.6 時間)は 1,200 本版の値で、コーパス全体の値ではなかった。ほかのデータセットでも、EmoBox の表の数をそのまま公表値にしていないか、確かめていない。

## 5. データセット全体とレシピ使用分

| | 全体(ChineseLDC) | レシピ使用(1,200 本版、実測) |
|---|---|---|
| 発話 | 9,600(2010 年版)。2005 年版は 12,000 / 10,000 | 1,200 |
| 話者 | 4(男女 2 人ずつ) | 4(人名。性別はファイル名にない) |
| 感情 | 6(2005 年の標注規範は 5) | 6、各 200 |
| 文 | 同じ文 300 + 違う文 100(2010 年版) | 文番号 201〜250 の 50 文。同じ文を感情で読み分けた部分(5 文で確認) |
| 時間 | 資料にない | 0.6352 時間 |
| 形式 | 16 kHz・16 bit・PCM | 16 kHz・モノラル・16 bit |
| 分割 | なし | 話者単位: train 2 人 600 / valid 1 人 300 / test 1 人 300 |

## 6. ito さん・DB 管理セッションに決めてほしいこと

**ito さんの判断(2026-10-23)**: レシピは残す。readme の冒頭に「非公式で使うべきでない」警告と問題の概要を書いた(espnet コミット、ローカル)。ChineseLDC には問い合わせない(これ以上深追いしない)。下の 1 と 5 はこれで決まり。

1. **レシピを使い続けるか**(ito さん。審査レポート §8 の 1):
   - (ア) 使う(今の HF ミラーから取る)。
   - (イ) レシピを残すが、取得は手元にデータがある人だけに限る(ダウンロードのコードを外す)。
   - (ウ) 使わない(レシピをリポジトリに含めない)。
   - 判断の材料: 有償の許諾のあるコーパスの再配布物であること(§3.4)、2024 年時点の条件は未確認であること。
2. **`espnet_status` と理由コード**: (1) に合わせて決める。`needs_decision` のままなら理由に `access_paid_or_membership` を足す。使わないなら `excluded` + `not_distributable` または `access_paid_or_membership`(README の規則では有償だけでは除外理由にならないので、理由の書き方を DB 管理セッションで決める)。
3. **E1〜E3 の `source_type`**: ChineseLDC は自動化所が運営に関わる配布団体(サイトの著作権表示)だが、作成者の研究室の文書ではない。`primary` でよいか。
4. **`n_utt_reported` と `labels_discrete_reported` を `conflicting` にするか**: 版の違い(2005 年と 2010 年)として、新しい 2010 年版を正とする書き方もある。
5. **問い合わせ**: ChineseLDC(service@chineseldc.org、2024 年のページの連絡先)に現在の条件と 1,200 本版の扱いを問い合わせるか(ito さんの判断。送るなら ito さんから)。
6. **relations**: AI Studio の 1,200 本版を別の行にして `subset_of casia` でつなぐか、notes だけにするか。

## 7. 未確認・限界

- 作成者(研究室)自身による、このコーパスの論文・配布の文書。
- 2024 年時点の ChineseLDC の条件(価格のページの保存が 2020 年まで)。サイトはこの環境から接続できない。
- 1,200 本版と HF ミラーのハッシュでの一致(サイズと日時の 20 本だけで照合)。
- 1,200 本版が ChineseLDC のどの版から切り出されたか(話者名・6 感情が 2005 年の文書と合わない)。
- 文番号 206〜250 の書き起こし(201〜205 だけ確認)。
- **DB の今の Source URL(globalaccentchinese.com/literature.php)**: 2026-10-20 はつながらず、2026-10-23 に Wayback Machine の保存版を開こうとすると、大学のネットワークが「malware」の分類で遮断した。**中身は見ていない**。どの資料からこの URL が入ったかも確かめていない(シート由来)。
- Pan, Tao, Li(ACII 2011)の本文。
- SER 研究全体での引用のされ方(5 本のみ確認)。
- 南京大学学報 2019 は HTML を取得して該当箇所を読んだ。

## 8. この調査の経緯(報告の誤りの訂正を含む)

- 2026-10-20 の審査レポートで、CASIA の規模と「音声合成のために作った」を「二次資料(論文の中の紹介)」と書いた。実際は Web 検索ツールが返した要約文で、出典を特定できていなかった。ito さんの指摘で分かった。
- 「音声合成のために作った」は、§3.2 の音声合成コーパスの論文と取り違えたもので、感情コーパスの根拠ではなかった。取り下げた。
- 調査の途中で、9,600 を「出どころ不明」と書いたが、ChineseLDC の 2010 年版の資源ページの数だった。また ChineseLDC を「公式」と書いたが、作成元が自ら指定した証拠はない。どちらも訂正済み。
- 記録: `recipe_review/mistakes.md`(2026-10-23 の項)。

## 9. 保存した資料(`recipe_review/casia_scripts/sources/`)

| ファイル | 元の場所 | SHA-256(先頭 16 桁) |
|---|---|---|
| cldc/CLDC-SPC-2005-010_intro.htm | web.archive.org/web/20051214160150/http://www.chineseldc.org:80/doc/CLDC-SPC-2005-010/intro.htm | 6cd769e0faec7b1e |
| cldc/CLDC-SPC-2005-010_label.htm | web.archive.org/web/20051214151014/http://www.chineseldc.org:80/doc/CLDC-SPC-2005-010/label.htm | fb0ef60fbf1d66f8 |
| cldc/CLDC-SPC-2005-010_report.htm | web.archive.org/web/20051214172403/http://www.chineseldc.org:80/doc/CLDC-SPC-2005-010/report.htm | e186551374393a8b |
| cldc/resource_info_rid76_2020.html | web.archive.org/web/20200501144342/http://www.chineseldc.org/resource_info.php?rid=76 | acf61f3ae110971a |
| cldc/home_2024.html | web.archive.org/web/20241126183355/http://www.chineseldc.org/ | 3c82d191d0798f99 |
| cldc/resource_list_20240615040043.html | web.archive.org/web/20240615040043/http://www.chineseldc.org/resource_list.php?begin=0&count=20 | 2e979f1214be1c8e |
| nlpr_gh166.pdf(+ .txt) | web.archive.org/web/20240503152623/https://nlpr.ia.ac.cn/2008papers/gjhy/gh166.pdf | 8a19684c35be17a5 |
| karaiskos08_blizzard.pdf(+ .txt) | https://www.isca-archive.org/blizzard_2008/karaiskos08_blizzard.pdf | c6c20864f5b38567 |
| tao08_blizzard.pdf(+ .txt) | https://www.isca-archive.org/blizzard_2008/tao08_blizzard.pdf | 70aef7b80d03acce |
| blizzard2008.html | http://www.festvox.org/blizzard/blizzard2008.html | — |
| emobox_2406.07162.pdf(+ emobox.txt) | https://arxiv.org/pdf/2406.07162 | 88d5f1115f9b5a5b |
| emobox/README.md、casia.py、casia.json、corpus.cfg | GitHub emo-box/EmoBox コミット 39c306b | README 799589fc313f102c |
| arxiv_2001.05908.pdf / arxiv_2103.16456.pdf / arxiv_2310.03992.pdf(+ .txt) | https://arxiv.org/pdf/<ID>(2026-10-23 取得の最新版) | 344e4844 / 91dc502c / 80dfbccd |
| nju2019.html | https://jns.nju.edu.cn/article/2019/0469-5097/0469-5097-2019-55-5-765.shtml | — |
| aistudio_209512_read_2026-10-23.txt | https://aistudio.baidu.com/datasetdetail/209512 を読んだ控え(ページそのものは保存していない) | — |
| cldc/CLDC-SPC-*_intro.htm(ほか) | ChineseLDC の 2005〜2008 年のカタログ(感情コーパスを探すために取得) | — |
