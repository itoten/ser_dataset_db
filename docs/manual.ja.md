# SER データセット DB 入門ガイド(日本語訳)

> 原文 [manual.md](manual.md)(英語)の日本語訳。原文と同じ構成で、**更新するときは両方を同時に更新する**(18.2)。
> 表中のパスは DB のフォルダ(リポジトリの最上位)からの相対パス。

このガイドは DB を最初から説明する。用語は使う前に説明する。数値はすべて、第 11 節の日付に `data/*.csv` から数え直したもの(メンテナンス用 skill の `doc_counts.py` で更新する)。

## 1. 30 秒でわかる DB

### 1.1 一文で言うと

**「感情(およびその他のパラ言語情報)ラベルを持つ音声データセットについて、公開されている情報の台帳」**。どの表計算ソフトでも開ける CSV ファイルの集まりで、履歴は `git` で管理している。

### 1.2 数字で見ると

| 項目 | 値 |
|---|---|
| 登録データセット数 | **322**(元のスプレッドシート 84 + その後の追加 238) |
| ESPnet に実装済み | 101 |
| 実装の候補 | 134 |
| 判断待ち | 7 |
| 保留 | 34 |
| 除外(理由つき) | 46 |
| 根拠(evidence)の行数 | 4,987 |
| 言語コード | 76 |

### 1.3 何が役に立つか

- **すべての値に出典がある**: 「ライセンスは CC-BY-4.0」と書くだけでなく、どのページのどの文言を、いつ、誰が確認したかを 1 行ずつ記録している。
- **推測しない**: 分からないことは「分からない」と記録する(欠損値の書き方の規則は第 7 節)。URL やタイトルを作り上げることはしない。
- **機械が検査する**: `validate.py` が形式と根拠の抜けを自動で検査し、通らないコミットは拒否される。
- **実装とつながっている**: 実際に作った ESPnet のレシピ(実験の設定一式)の件数・時間・ラベルを実測して保存している。

## 2. なぜ作ったか

### 2.1 背景

音声感情認識(SER)の研究では、言語・規模・ライセンス・入手方法の違う数十のデータセットを使う。「このコーパスは商用で使えるか」「日本語の感情データは何があるか」と聞かれるたびにウェブを調べ直すのは、時間とトークンの無駄になる。

### 2.2 目的

1. **質問にすぐ答える**: データセットの言語・規模・ライセンス・入手方法・ラベル・実装状況を、検索せずに引ける。
2. **次に実装するものを選ぶ**: 許諾が緩く、直接ダウンロードでき、まだ実装していないものを一覧から選べる。
3. **信頼できる研究**: クロスコーパス評価(第 3 節)で、どのデータを学習に、どのデータを評価に使ったかの根拠を示す。ライセンスの扱いを誤ると結果が公表できなくなるので、特に注意する。

### 2.3 経緯

もとは Google スプレッドシート「ser_database」(84 行)だった。スプレッドシートは 2026-10-12 に凍結し、原本は [sheet_import/](../sheet_import/README.md) に保存している。以降は CSV が正で、スプレッドシートは更新しない。2026-10-14 に、サーベイ・既存の一覧・ホスティングサービスの検索から 158 件、さらに意図・対話行為のデータセット 12 件などを追加して 307 行になり、その後も追加している。

## 3. 用語集

### 3.1 研究の用語

| 用語 | やさしい説明 |
|---|---|
| **SER**(音声感情認識) | 声から感情(怒り・喜び・悲しみなど)を機械に認識させること |
| **コーパス / データセット** | 研究用に整理した音声データの集まり。ここでは同じ意味で使う |
| **ラベル** | 録音に付けられた「答え」。例: 「angry」 |
| **離散(カテゴリ)感情** | 感情を、怒り・喜びのような少数の箱のどれかで表すこと |
| **次元感情** | 感情を数値、典型的には valence(快‐不快)と arousal(覚醒度)で表すこと。軸は `dimensional_attributes` に書く |
| **発話(utterance)** | ひとまとまりの音声。データ量は発話数で数える |
| **話者(speaker)** | 話している人 |
| **演技(acted)** | 俳優などが感情を込めて演じた音声 |
| **自然発話(spontaneous)** | 会話・ポッドキャスト・動画などから集めた自然な音声。現実に近いがラベル付けが難しい |
| **意図 / 対話行為** | 感情ではなく、話者がしたかったこと(「アラームをセットして」)や発話の機能(質問・依頼・同意)。DB は感情以外のパラ言語情報も扱うので含めている |
| **パラ言語情報** | 言葉以外に声が運ぶ情報(感情・話し方・意図・センチメントなど) |
| **センチメント(極性)** | 感情の向き。ポジティブ/ネガティブなど |
| **TTS** | 音声合成。TTS 用に録られた感情コーパスも含める |
| **ASR** | 音声認識。ASR 専用のデータは対象外 |
| **クロスコーパス評価** | あるデータセットで学習し、別のデータセットで評価して、モデルがデータセットをまたいで通用するかを見ること |
| **完全 OOD 評価** | 学習で一度も使っていないコーパスだけで評価すること |

### 3.2 ESPnet の用語

| 用語 | やさしい説明 |
|---|---|
| **ESPnet / ESPnet3** | 音声処理のオープンソース研究ソフトウェア。このプロジェクトが SER を追加している |
| **レシピ(recipe)** | 1 つのデータセットで学習・評価するための設定一式。フォルダ `egs3/<name>/cls` |
| **`cls`** | 分類(classification)用のシステム名 |
| **実装済み(implemented)** | そのコーパスのレシピがある |
| **ベンチマーク** | 複数のコーパスを組み合わせた評価の枠組み。そのレシピは `multi_corpus` |

### 3.3 データ管理の用語

| 用語 | やさしい説明 |
|---|---|
| **CSV** | カンマ区切りの表ファイル。Excel・Google スプレッドシート・LibreOffice で開ける |
| **正(authoritative)のデータ** | 原本と宣言したデータ: `data/*.csv`。`views/` はそこから生成されるので、`views/` を直接編集しない |
| **git / コミット** | ファイル変更の履歴を記録するソフトウェアと、記録された 1 回の変更。いつ何が変わったかを後で見られ、戻すこともできる |
| **リモート** | リポジトリのオンラインのコピー(ここでは GitHub) |
| **フック** | コミットの直前に自動で走る検査。通らないとコミットが拒否される |
| **キー(ID)** | 行を特定する名前。例: `dataset_id`(`ravdess`)。一度決めたら変えない |
| **外部キー** | 別の表のキーを指す列。例: `evidence.dataset_id` は `datasets` の行を指す |
| **スキーマ** | 設計: 列名・型・意味。`schema/` にある |
| **sha256** | ファイルの中身から計算する指紋。2 つのファイルが同一かの確認に使う |

### 3.4 出典の用語

| 用語 | やさしい説明 |
|---|---|
| **一次資料** | 作者自身が公開した情報(論文・公式の配布ページ・LICENSE ファイル) |
| **二次資料** | 他の人が書いた情報(まとめサイト・再アップロードのページ・サーベイ) |
| **Hugging Face(HF)** | 機械学習のデータやモデルを置くサービス |
| **Kaggle** | データサイエンスのコンペのサービス。データも共有されていて、無料アカウントと API トークンでダウンロードできる |
| **Zenodo / figshare / Mendeley Data** | DOI つきで研究データを公開できる無料サービス |
| **DOI** | 論文やデータの恒久的な識別子 |
| **ISO 639-3** | 3 文字の言語コード: `eng` 英語、`jpn` 日本語、`cmn` 中国語(北京官話)、`mul` 内訳のない複数言語、`zxx` 言語内容なし |
| **KuralHub** | 言語別の SER データセットのサーベイ。第三者の資料なので、これだけで裏づけられた値は未確認として扱う |

### 3.5 ライセンスの用語

ライセンスは、データをどこまで使ってよいかを定めたもの。ここでの説明は一般的なもので、法的助言ではない。

| 用語 | やさしい説明 |
|---|---|
| **CC(クリエイティブ・コモンズ)** | 利用条件を決まった記号で表す仕組み |
| **BY** | 作者のクレジットを表示すれば使える(帰属表示) |
| **NC** | 非商用のみ。商用製品には使えない |
| **SA** | 派生物も同じ条件で共有しなければならない |
| **ND** | 改変禁止 |
| **CC0** | 権利放棄。自由に使える |
| **ODbL / ODC-By** | データベース用のライセンス。帰属表示または同条件共有を求める |
| **MIT / Apache-2.0** | 寛容なソフトウェアライセンス(帰属表示すれば自由に使える) |
| **GPL** | 同じ条件での共有を強く求めるソフトウェアライセンス。データでは珍しい |
| **SPDX 識別子** | ライセンスの公式な短い名前(例: `CC-BY-4.0`)。表記ゆれを避けるために使う |
| **LicenseRef-...** | SPDX にない独自条件に付ける、この DB 独自の名前(第 9 節) |
| **コピーレフト** | 同じ条件での共有を求めること(SA、GPL) |
| **寛容(permissive)** | ほぼ自由に使える。あっても帰属表示まで |
| **再配布** | 受け取ったデータを他の人に渡す、または別の場所で公開すること。許されないことが多い |

## 4. DB の中身

### 4.1 フォルダの地図

```
ser_dataset_db/
├── README.md                  開発者向けの要約(AI アシスタントが最初に読む)
├── docs/manual.md, manual.ja.md  このガイド(英語版と日本語版)
├── data/                      * 正のデータ(CSV 8 ファイル)
├── schema/                    列の定義・許される値・表のキー
├── views/                     読むためのコピー(data/ から生成)
├── measurements/              レシピの実測結果(JSON)。text_link/ には 5.4.2 用の書き起こし確認がある
├── reports/                   単一データセットの詳しい調査と検証
├── sheet_import/              凍結した元のスプレッドシート
├── tools/                     検査・更新・実測のプログラム
├── .env.example               マシン固有設定のひな形(.env にコピーして使う。git 管理外)
├── LICENSE                    MIT。この DB とツール用(記述対象のデータセットには適用されない)
└── .claude/skills/            Claude Code 用のメンテナンス手順
```

### 4.2 8 つの表(`data/`)

| ファイル | 1 行が表すもの | 行数 |
|---|---|---|
| datasets.csv | **1 つのデータセット**(中心の表) | 322 |
| evidence.csv | datasets の 1 つの値の**出典** | 4,987 |
| aliases.csv | 別名(正式名・略称・旧名・レシピ名など) | 375 |
| relations.csv | データセット同士の関係 | 44 |
| recipes.csv | 1 つの ESPnet レシピ | 102 |
| recipe_labels.csv | レシピ × ラベル | 656 |
| benchmark_membership.csv | ベンチマークに含まれるレシピ | 16 |
| annotations.csv | データセット × 感情ラベル以外のアノテーション(書き起こし・話者の属性・対話行為など) | 284(`aesdd` 1、`akace` 2、`albemo` 3、`anad` 3、`ased` 4、`asvpesd` 4、`audiospeechsentiment` 2、`banglamood` 1、`banglaser` 4、`banspemo` 2、`baser` 4、`berst` 9、`brytserc` 1、`cafe` 2、`casia` 3、`cbesd` 5、`cremad` 4、`csemotions` 2、`dailytalk` 6、`dusha` 4、`eesc` 6、`emis` 5、`emns` 4、`emodb` 4、`emogator` 2、`emospeech_keywords` 5、`emotale` 5、`emotional_ema` 8、`emotiontalk` 6、`emouerj` 3、`emovoicedb` 5、`emozionalmente` 4、`enterface05` 4、`eseravd` 3、`harper_valley_bank` 19、`hikia` 1、`hindi_ser_vishlb` 4、`iemocap` 4、`iesc` 4、`javanese_ser_2black0` 3、`jlcorpus` 4、`jnv` 6、`jvnv` 4、`kbes` 1、`legov2` 6、`lithuanian_emotion_db` 2、`maserc` 4、`mav` 3、`mcaespps` 2、`mderma` 1、`meld` 5、`mesd` 1、`mess` 1、`msppodcast` 2、`multidialog` 2、`quechua` 3、`ravdess` 1、`resd` 3、`rml_emotion` 4、`saraiki_ser` 1、`ses_ed` 3、`ses_sd` 3、`shemo` 2、`sitb_osed` 4、`subesco` 5、`syntact` 6、`talromur3` 5、`telugu_emotion_kaggle` 4、`thaiser` 3、`thorsten` 2、`ua_ser` 6、`urduser` 2、`usc_emo_mri` 5、`utemo` 4、`vivae` 2、`whiser` 5、`ysed` 2。今後も増える) |

関係の種類別: `contains` 15、`distinct_from`(名前は似ているが別のデータセット)12、`subset_of` 7、`possibly_same_as`(同一の疑い)4、`version_of` 3。102 レシピのうち、101 は単一コーパス(`single_corpus`)、1 は複数コーパスを組み合わせたもの(`multi_corpus`)。

### 4.3 表のつながり

```
datasets ──(dataset_id)── evidence     各値の出典
   │       ──(dataset_id)── aliases      別名
   │       ──(dataset_id)── relations    他のデータセットとの関係
   │       ──(dataset_id)── annotations  感情以外のアノテーション(各行に独自の出典)
   └── recipes(dataset_id) ── recipe_labels (ラベルごとの件数)
          └── benchmark_membership (ベンチマークの構成)
```

### 4.4 1 行とは何か

- 1 行は原典(最初に公開されたもの)のデータセット。Hugging Face や Kaggle などへの単なる再アップロードは行にせず、原典の別名(aliases)に入れる。
- 中身が違うもの(再分割・サブセット・新しいラベル)は別の行にして、`relations` でつなぐ。
- 2 つの行が実は同じだと分かったら、一方を `excluded`(重複)にして `possibly_same_as` でつなぐ。ID は削除しない。
- 音声のないデータセット(テキストのみ・特徴量のみ)は、調べた結果を残すために `excluded` として残す。

## 5. `datasets` 表の読み方

### 5.1 最初に見る列

1 行に約 45 列あるので、まずは次の列を見る。

| 列 | 意味 | 例(ravdess) |
|---|---|---|
| `dataset_id` | 不変の ID | `ravdess` |
| `name` | 名前 | RAVDESS |
| `espnet_status` | 状態(第 8 節) | `implemented` |
| `languages` | 言語(ISO 639-3、`;` 区切り) | `eng` |
| `recording_context` | 録音の状況や媒体 | `acted` |
| `speech_production` | 音声の作られ方(5.4.1) | `acted` |
| `label_basis` | ラベルの付け方(5.4.1) | `intended` |
| `text_emotion_link` / `lexical_confound` | 発話テキストとラベルの関係、言葉だけでどこまでラベルが当たるか(5.4.2) | `parallel` / `none` |
| `license_spdx` / `license_class` | ライセンスとその分類(第 9 節) | `CC-BY-NC-SA-4.0` / `noncommercial` |
| `access_method` | 入手方法(第 10 節) | `direct_download` |
| `raw_audio_available` | 生の音声が配布されているか | `true` |
| `n_utt_reported` / `hours_reported` / `n_speakers_reported` | 出典に書かれた発話数・時間・話者数 | 1440 / 1.5 / 24 |
| `labels_discrete_reported` | 出典にあるカテゴリ感情ラベル | calm;happy;sad;angry;... |
| `dimensional_attributes` | 次元感情の軸、なければ `none` | `none` |

### 5.2 「reported」と「measured」

- `*_reported`: **論文や配布ページに書かれた数値**(公表値)。
- `*_measured`: **ダウンロードして自分たちで数えた数値**(実測値)。

両者は食い違うことがあり、その差自体が有用な情報になる。レシピは非常に短いクリップなどを落とすので、レシピの件数と公表の件数は普通は違う。食い違いは [views/discrepancies.csv](../views/discrepancies.csv) に一覧がある。

### 5.3 備考の列

- `status_note`: 状態についての備考(なぜ候補なのか、注意点)
- `license_note`: ライセンス文言の要点
- `language_note`: 方言や、言語の値をどう決めたか
- `label_basis_note`: ラベルの付け方の詳細(5.4.1)
- `lexical_confound_note`: `lexical_confound` の値の根拠(5.4.2)
- `paralinguistic_signal_note`: 何を聴いて何が聞こえたか(5.4.3)
- `human_accuracy_note`、`source_rights_note`: 聴取評価の設計、素材の権利について作者が述べていること(5.4.4)
- `notes`: こちらで書いた備考
- `sheet_notes`、`annotations_other`、`sheet_verified`: **スプレッドシートの原文**。変更しない。`sheet_verified` はスプレッドシートの「手で確認済み」の印で、判断には使わない

### 5.4 ラベルは誰が付けたか(`label_source`、`label_verification`)

主要なラベル(`labels_discrete_reported` と `dimensional_attributes` にあるもの)を誰が付けたかを記録する。どちらも値ごとに根拠の行がある。空欄は未確認。

- `label_source`: `human`(人だけ)/ `automatic`(モデルなどだけ)/ `mixed`(自動ラベルを人が確認、または混在)/ `synthesis_specified`(合成音声で、ラベルは合成器に指定した感情)
- `label_verification`: 人がラベルを確認したか: `human_reviewed`(出典に、人が自動ラベルを確認したとある)/ `listener_validated`(指示したラベルを聴取評価で確認、または絞り込んだ。ラベルは指示したままのもの)/ `none`(出典に、確認はなかったとある)/ `unknown`(出典に何も書かれていない)/ `NA`(確認する対象がない。例: ラベルが聴取者自身の判断)
- 例: `harper_valley_bank` は自動(論文に、ラベルは API から得たとある)で、確認についての記述はない(`unknown`)。`nonverbaltts` は emotion2vec+ の分類を注釈者が確認したもの(`mixed`、`human_reviewed`)。
- 自動ラベルだからといって `candidate` から外さない(8.3)。そのようなラベルで学習するか評価だけに使うかはレシピ側の判断で、`recipes.notes` に書く。
- レシピの審査が済んだデータセットについて記入する。それ以外は審査の中で、一次資料から 1 件ずつ記入する。

### 5.4.1 音声の作られ方とラベルの付け方(`speech_production`、`label_basis`)

「音声がどう作られたか」と「ラベルがどう付けられたか」は別のことなので、別の列に記録する。演技の音声に、聴取者が知覚したラベルが付くことも、その逆もある。知覚ラベルは特に価値が高いので、検索できる形で記録する。

| 列 | 値(複数あてはまる場合は `;` 区切り) |
|---|---|
| `speech_production` | `acted`(演技: 指示された感情を演じた。台本のある映画・ドラマの演技を含む)/ `elicited`(刺激や課題で誘発)/ `spontaneous`(自然発話)/ `read`(感情の指示なしの読み上げ)/ `synthetic`(合成) |
| `label_basis` | `intended`(話者が演じるよう指示された感情)/ `perceived`(聴取者が知覚した感情)/ `self_reported`(話者自身の報告)/ `context_inferred`(場面・台本・言葉の意味からの推定)/ `automatic`(モデルの推定)。感情ラベルがなければ `none` |
| `label_basis_note` | 自由記述: 評定者の人数、評定者が見聞きしたもの(音声のみ・映像つき・書き起こし)、評定の統合方法(多数決・平均)、主となるラベルセット、聴取評価の詳細 |
| `recipes.label_basis_used` | 複数の方法で作られたラベルを配布しているデータセットで、レシピが実際に使うラベルの種類 |

- `recording_context` は状況や媒体(スタジオ・YouTube・テレビ・映画など)の列として残す。そこから音声の作られ方を推測しない。
- 指示したラベルを聴取評価で確認した場合、または一致したクリップだけを残した場合、ラベルは `intended` のままで、`label_verification=listener_validated` とする。
- レシピの審査中に記入する。審査前の行は空欄(未確認)。

### 5.4.2 テキストとラベル(`text_emotion_link`、`lexical_confound`)

話された言葉だけでラベルが分かってしまうと、モデルは声ではなく言葉を学習してしまう(ショートカット学習)。ラベルが言葉だけに従うデータセットは除外する(`labels_from_text_content`)。本物のパラ言語情報があって、言葉と多少の相関があるだけのデータセットは、注意しながら使ってよい。この列はその相関に印を付けて、実際のデータを確認するきっかけにするためのもので、それだけでは何も決めない。

| 列 | 値 |
|---|---|
| `text_emotion_link`(`;` 区切り) | `parallel`(すべての感情で同じ文)/ `neutral_text`(意味的に中立な文)/ `emotion_specific_text`(内容が感情に合っている)/ `unrelated_text`(感情と無関係に割り当てた文)/ `dialogue_script`(映画・ドラマ・書かれた対話のせりふ)/ `unscripted`(会話・放送・即興) |
| `lexical_confound` | `full`(テキストがラベルを決める: 各文は 1 つの感情にしかない)/ `strong`(大半の発話)/ `moderate`(かなりの部分)/ `weak`(少しの部分、または弱い関連)/ `possible`(直接の証拠はないが、疑う文書化された理由がある。例: 台本なしの発話、文脈や書き起こしを見て付けたラベル)/ `none`(設計上あり得ない: 並列・中立・感情と無関係な文、または言葉がない) |
| `lexical_confound_note` | 自由記述: 値の根拠(出典にある設計、文とラベルの件数、テキストだけの分類器)と範囲(例: 「英語半分のみ」) |

- 値には明確な出典が必要: 論文や公式文書の設計の記述、または実測(書き起こしで感情ごとの文を数える)。推測で埋めない。実測は任意で、費用がかかることがある: 出典が何も言っておらず、安く確認する方法もなければ `unknown`(確認したが出典に書かれていない)と書き、相関を疑う文書化された理由があれば `lexical_confound=possible` にして理由を `lexical_confound_note` に書く。データセットをまだ見ていないときだけ空欄にする。
- 相関の可能性が少しでも(`possible` 以上)あれば記録する。この印が後でデータを見るきっかけになるため。`none` は設計上あり得ないと言えるときだけ使う。
- Whisper の書き起こしは実測だが、人が確認していないことを根拠(evidence)のメモに書く。実測の出力は `measurements/text_link/` に置く。
- レシピの審査中に記入する。審査前の行は空欄(未確認)。

### 5.4.3 声に表現が出ているか(`paralinguistic_signal`)

ラベルが正しくても、声にはラベルどおりの表現があまり出ていないことがある(感情ごとにせりふを平坦に読む、教室のアマチュアの話者など)。そういうデータは、声から学習してほしいモデルを誤らせることがある。この列は聴取で分かったことを記録するもので、使うかどうかは決めない。

| 値 | 意味 |
|---|---|
| `clear` | 声にラベルどおりの表現が出ている(聴取評価、または maintainer の試聴で確認) |
| `varies` | 話者やクラスによって、はっきりしたものと弱いものがある |
| `weak` | 聴いた範囲では表現が弱い |
| `doubtful` | 声に、ラベルの感情の表現がないかもしれない(例: せりふの平坦な読み上げ) |

- 聴取からだけ記入する(聴取評価、または maintainer の試聴を `source_type=user` で記録)。聴いたクリップ数と聴いた内容は `paralinguistic_signal_note` に書く。軽い試聴(数クリップ)はそのように記録し、実測とはしない。
- 空欄は未判断。ラベルの出どころ・録音の状況・文から埋めない。

### 5.4.4 人間の正解率と素材の権利(`human_accuracy`、`source_rights`)

`human_accuracy` は 0〜1 の数値で、聴取評価で聴取者がラベルの感情を言い当てた割合。モデルがどのくらいまで期待できるかの目安になる。出典が報告しているとき(論文・配布物、または配布された評定ファイルの集計 = `source_type=measured`)だけ記録する。

- `human_accuracy_note` には設計を書く: 聴取者とクリップの数、提示した選択肢と偶然水準、どのクリップを試したか(全部か一部か)、個々の回答が配布されているか。出典同士で数値が食い違うときは、そう書く。
- 一致度の統計量(Fleiss の κ など)は正解率ではない。`label_verification` の根拠のメモに書く。
- 異なる評価を 1 つの数値に平均しない。出典が報告する 1 つを記録して、説明を書く。

`source_rights` は、元の音声に対する権利を、`license_spdx` / `license_class`(作者が述べるライセンスを記述し続ける)とは別に記録する。

| 値 | 意味 |
|---|---|
| `own` | 作者が素材を自分で録音した(第三者の素材ではない) |
| `cleared` | 第三者の素材で、論文や公式ページの引用できる記述(許諾・元素材のオープンライセンス・法的見解)により使ってよいと示されている。根拠(evidence)に引用する |
| `asserted` | 第三者の素材。作者は共有してよいと言う(倫理声明・フェアユース・利用規約・著作権の問題なし)が、確認できる根拠(出典の一覧・個別のライセンス・許諾)を示していない |
| `unaddressed` | 第三者の素材で、出典が素材の権利について何も述べていない |
| `unknown` | 素材そのものの出どころが不明 |

- `asserted`、`unaddressed`、`unknown` は、素材の権利を確認する必要があることを意味する。`views/source_rights_check.csv` がこれらのデータセットを一覧にする。対応する保留リストは、プロジェクトがリポジトリの外で管理している。
- カードや記録に書かれたライセンス(CC BY など)があっても、素材が `cleared` にはならない: それは作成者自身の仕事に対するもの。`cleared` には、元素材についての記述が必要。
- フェアユースの見解による `cleared`(MELD)は述べられたとおりに記録し、フェアユースの見解は商用利用の許諾ではないとメモに書く。
- `source_rights_note` には、出典が述べていること(場所つきの引用または言い換え)と、足りないもの(出典・個別ライセンス・同意・非商用の記述)を書く。空欄は未検討。

### 5.5 感情ラベル以外のアノテーション(`annotations.csv`)

書き起こし・話者の属性・対話行為・音質・アンケートなど、感情ラベル以外の情報を、データセット × 項目で 1 行ずつ記録する。`datasets.annotations_other`(スプレッドシートの文)は変更せず残し、新しい情報はこの表に入れる。

- 列: `item`、`description`、`annotator`(`human` / `automatic` / `mixed` / `unknown`)、`unit`(`utterance` / `segment` / `word` / `recording` / `conversation` / `speaker` / `dataset`)、`used_in_recipe`
- 各行が自分の出典(`source_type`、`source_ref`、`locator`、`checked_on`、`checked_by`)を持つ。`evidence.csv` は `datasets` の列の値用なので、アノテーションの出典は混ぜない。
- `used_in_recipe=true` は `implemented` のデータセットだけに許される(検証器が検査する)。
- 項目はレシピ登録のときに、一次資料で確認できたものから追加する。

### 5.6 ラベルの種類(`recipe_labels.label_type`)

`categorical`(カテゴリ感情・話し方など)/ `polarity`(センチメント)/ `intent`(意図・対話行為)/ `dimensional` / `other`。極性と意図のラベルは共通 7 ラベルに対応づけない: `common7=none`、`mapping_type=outside_common7`。`recanvo` の 21 行は、ラベルが感情と依頼・意図にまたがるため、空欄(未確認)にしている。

### 5.7 全列の定義

全列の型・意味・許される欠損値は [schema/columns.csv](../schema/columns.csv)、許される値は [schema/enums.csv](../schema/enums.csv)、表のキーは [schema/tables.csv](../schema/tables.csv) にある。

## 6. 根拠(Evidence)

### 6.1 なぜ根拠を残すか

値だけでは、後で「それは本当か」に答えられない。そこで重要な値のすべてに、出典・確認した日・確認した人・強さを記録する**根拠の行**を付ける。

### 6.2 根拠の行の中身

| 列 | 意味 |
|---|---|
| `value` | その根拠が裏づける値 |
| `source_type` | 出典の種類(強さ順、6.3) |
| `source_ref` | 出典(URL・ファイルパス) |
| `locator` | 出典のどこか(短い引用や場所。25 語まで) |
| `checked_on` / `checked_by` | 確認した日と確認した人(`claude` / `user` / `script`) |
| `is_canonical` | 現在の値の根拠なら `true`。データセット × 列ごとにちょうど 1 つ |
| `status` | `current` / `superseded`(新しい根拠に置き換えられた)/ `conflicting`(出典が食い違い、未決) |

根拠が必要な列: `languages`、`recording_context`、`vocal_content`、`license_spdx`、`access_method`、`raw_audio_available`、`n_utt_reported`、`hours_reported`、`n_speakers_reported`、`n_files_release_measured`、`n_speakers_measured`、`labels_discrete_reported`、`dimensional_attributes`、`espnet_status`、`status_reason_codes`、`label_source`、`label_verification`、`speech_production`、`label_basis`、`text_emotion_link`、`lexical_confound`、`paralinguistic_signal`、`human_accuracy`、`source_rights`。

### 6.2.1 確認した日の記録

4,987 行の根拠のすべてに確認日(`checked_on`、2026-10-10〜10-30)がある。ただし**この日付は出典を見た日**であって、今も正しいことの保証ではない。配布ページやライセンスは変わることがある。元のスプレッドシート由来の行(`source_type`=`sheet`)の 2026-10-12 は取り込みの日で、誰かが中身を確認した日ではない。

一覧 [views/datasets_wide.csv](../views/datasets_wide.csv) には、データセットごとに次の列がある(根拠から生成)。

| 列 | 意味 |
|---|---|
| `license_checked_on` / `license_source_type` / `license_checked_by` | ライセンスの根拠の日付・種類・確認者 |
| `access_checked_on` | 入手方法を確認した日 |
| `oldest_checked_on` / `latest_checked_on` | その行の現在の根拠のうち、最も古い日付と最も新しい日付 |

古い日付と `sheet` の出典は、再確認の優先度が高い。

### 6.3 出典の強さ

強い順。

| 順位 | `source_type` | 内容 |
|---|---|---|
| 1 | `user` | プロジェクトの maintainer の判断と説明 |
| 2 | `measured` | 自分たちが数えた値や、試したアクセス |
| 3 | `primary` | 作者の論文・公式ページ・LICENSE |
| 4 | `project_doc` | 出どころを特定できない社内文書 |
| 5 | `secondary` | 第三者の記述(Kaggle・再アップロードのページ・サーベイ) |
| 6 | `sheet` | 元のスプレッドシートの値 |

4,987 行の根拠の内訳: primary 2,490、project_doc 681、measured 587、sheet 572、user 384、secondary 273。

### 6.4 新しい事実が出てきたとき

古い根拠は残して `superseded` にし、新しい行を足す。履歴が残るので、「前はこうだったが、この出典で訂正された」と説明できる。同じ強さの出典が食い違い、どちらも優先できないときは、`conflicting` の行を 2 つ以上残し、datasets のセルも `conflicting` にする(例: EmoDB・Baum-1・TurEV-DB のライセンス)。理由を述べて一方を優先できるときは、それを canonical にし、もう一方は canonical でない `conflicting` の行として残す。

### 6.5 実例(RAVDESS のライセンス)

| 根拠 | 値 | 出典の種類 | 状態 |
|---|---|---|---|
| `ravdess/license_spdx/01` | CC-BY-NC-SA-4.0 | sheet(元のスプレッドシート) | superseded |
| `ravdess/license_spdx/02` | CC-BY-NC-SA-4.0 | primary(Zenodo のレコード) | **current / canonical** |

値は同じでも、スプレッドシートの値が一次資料に置き換えられたことが記録から分かる。

### 6.6 原則

- 出典が述べていないことは書かない。URL やタイトルを推測で作らない。
- 実測値を「reported」の列の根拠に使わない(逆も同様)。
- 実測の件数・時間・話者数の根拠は、`measurements/<recipe>.json` とダウンロードしたファイル自体だけ。

## 7. 欠損値の書き方(空欄・unknown・NA・none)

「値がない」には 4 種類あり、**決して混ぜない**。

| 書き方 | 意味 | 例 |
|---|---|---|
| (空欄) | **まだ確認していない** | ライセンスを調べていない |
| `unknown` | 確認したが、出典が何も言っていない、または判断できない | 配布元がライセンスを示していない |
| `NA` | あてはまらない | 実装していないデータセットのレシピ列 |
| `none` | 確認した結果、ない | 次元ラベルがないことを確認した |

各列がどれを受け付けるかは、`schema/columns.csv` の `nulls` 列で決まっている。ライセンスにはさらに `none_stated`(ライセンスの記述が見つからない)という値がある。

## 8. 状態(`espnet_status`)

### 8.1 5 つの状態

| 状態 | 意味 | 件数 |
|---|---|---|
| `implemented` | ESPnet のレシピがある | 101 |
| `candidate` | 追加の候補: 分類に使える音声とラベルがあり、おそらく入手できる | 134 |
| `needs_decision` | プロジェクトの maintainer にしか決められない(費用・利用条件・申請の文面) | 7 |
| `deferred` | 未確認: 配布元が応答しない、入手経路が不明など | 34 |
| `excluded` | 明確な理由があり、使わない | 46 |

### 8.2 明確な理由だけが `excluded` を正当化する

除外してよいのは、次の場合だけ。

- 音声がない(テキストのみ・論文のみ・特徴量のみ・コードのみ)
- 他のデータセットの再配布(`redistribution_of_existing_corpus`)、または行の重複
- ラベルが分類に使えない
- ラベルが声ではなく話された内容(文の意味)に従う(`labels_from_text_content`)。聴いて確認し、maintainer が決めた場合のみ
- 国籍や居住地の制限のため入手できない
- 配布が許されていない

除外 46 行の内訳: テキストのみ 11、既存コーパスの再配布 10、論文のみ 9、地域制限 7、特徴量のみ 6、その他(ラベルが不適切、特定不能、重複、コードのみ、配布不可、配布元に連絡がつかない、…)。1 つの行に複数の理由があることがある。

### 8.3 除外の理由にならないもの(重要)

2026-10-14 に maintainer が決めた方針。次は**除外の理由にならない**。

- 規模(小さい・大きい)
- 手作業の入手手順(申請・署名・ログイン・購入)。maintainer に頼める
- Kaggle にあること(無料アカウントとトークンで足りる)
- ラベルの種類(センチメント・意図・次元値・話し方)
- 自動ラベル、合成音声

これらは `candidate` のままにして、注意点を `status_note` に書く。手間がかかるからといって落とすのではなく、手間がかかることを記録して、後で決められるようにするのが狙い。

### 8.4 理由コード(`status_reason_codes`)

`implemented` 以外のすべての行に理由コード(`;` 区切り)がある。一覧と意味は [schema/enums.csv](../schema/enums.csv) の `reason_code` の行。1 つの行に複数のコードが付くことがあるので、下の件数の合計は行数より多くなる。

| コード | 意味 | candidate | needs_decision | deferred | excluded |
|---|---|---|---|---|---|
| `unexamined` | 実装をまだ検討していない | 74 | 0 | 15 | 0 |
| `first_review_done` | 一次資料を読み、妨げる理由は見つからなかった。使うかは未決 | 6 | 0 | 1 | 0 |
| `not_individually_checked` | スプレッドシート取り込み時の仮の理由 | 0 | 0 | 2 | 0 |
| `access_*` | 申請・署名・ゲート・支払い・直接ダウンロードなし・地域制限 | 48 | 4 | 9 | 8 |
| `labels_*` | ラベルがカテゴリ感情でない、話し方である、自動である、またはテキストに従う | 9 | 1 | 0 | 4 |
| その他 | 音声なし、再配布、重複、特定不能、連絡がつかない、出どころ不明、配布不可、リンクのみ | 1 | 3 | 7 | 44 |

`first_review_done` が付くのは、一次審査で妨げる理由が見つからなかった行だけ。妨げる理由が見つかった行にはその理由のコードが付くので、審査済みの行数はこのコードだけからは読み取れない。審査は `status_note` と根拠の行に記録されている。

## 9. ライセンス

### 9.1 2 つの列

- `license_spdx`: 出典にある条件を SPDX 識別子に対応づけたもの。
- `license_class`: 識別子から**機械的に**導いた大まかな分類。法的判断ではない。

### 9.2 `license_class` の値と件数

| 分類 | 意味 | 件数 |
|---|---|---|
| `open` | 寛容(あっても帰属表示まで): CC-BY・CC0・MIT など | 98 |
| `noncommercial` | 非商用のみ(CC-BY-NC など) | 39 |
| `research_only` | 学術・研究利用に限る独自条件 | 55 |
| `restricted` | 制限つき、または有料 | 12 |
| `other` | 上記以外 | 4 |
| `none_stated` | ライセンスの記述が見つからない | 24 |
| `unknown` | 調べたが判断できない | 24 |
| `conflicting` | 出典が食い違う | 2 |
| (空欄) | まだ調べていない | 64 |

### 9.3 独自条件に使う名前

SPDX にない条件には次のいずれかを付け、文言の要点を `license_note` に書く。

- `LicenseRef-custom-research-only`: 独自の、学術・研究利用に限る条件
- `LicenseRef-proprietary-restricted`: 支払いや契約などの独占的な条件
- `LicenseRef-other`: それ以外
- `LicenseRef-golos-public`: Golos/Dusha の「帰属表示と条件留保つきの公開ライセンス」。CC BY-SA 4.0 を改変したもので、非商用の条項はない(分類は `open`、maintainer の判断)
- `LicenseRef-citation-request`: ライセンス文はなく、論文の引用の依頼だけがある。maintainer がそのデータセットについてこれを利用条件として扱うと決めた(分類は `open`。決定と文言は `license_note` にある)

### 9.4 データセットを使う前に

- `license_class` が `open` でも、**データのライセンス**と**同梱コードのライセンス**は違うことがある。必ず `license_note` と一次資料を読む。
- 「研究のみ」「非商用」の範囲(論文発表・モデルの公開・再配布)は、条件によって違う。DB は解釈しない。
- 再アップロードした人(Kaggle など)が書いたライセンスは、必ずしも作者の条件ではない。

## 10. 入手方法(`access_method`)

| 値 | 意味 | 件数 |
|---|---|---|
| `direct_download` | 認証なしで直接ダウンロードできる | 131 |
| `free_account_required` | 無料アカウント(登録)が必要 | 17 |
| `gated_click_through` | 同意のクリックなどが必要 | 7 |
| `request_form_or_email` | 申請フォームまたはメールで依頼 | 59 |
| `signed_agreement` | 署名した合意書が必要 | 30 |
| `paid_or_membership` | 有料、または会員 | 9 |
| `unofficial_mirror_only` | 非公式のミラーしかない | 0 |
| `unavailable` | 入手できない | 7 |
| `unknown` | 不明 | 12 |
| (空欄) | 未確認 | 50 |

大まかには、`direct_download`・`free_account_required`・`gated_click_through` は「今すぐ入手できる」、`request_form_or_email` と `signed_agreement` は「手続きが必要」。

## 11. 現在の数値(2026-10-30)

### 11.1 状態 × ライセンス分類

| 状態 | open | NC | research | restricted | other | none stated | unknown | conflicting | 未確認 | 合計 |
|---|---|---|---|---|---|---|---|---|---|---|
| implemented | 66 | 13 | 12 | 1 | 1 | 5 | 3 | 0 | 0 | 101 |
| candidate | 18 | 22 | 32 | 9 | 3 | 14 | 3 | 2 | 31 | 134 |
| needs_decision | 2 | 1 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 7 |
| deferred | 0 | 0 | 7 | 0 | 0 | 1 | 7 | 0 | 19 | 34 |
| excluded | 12 | 3 | 2 | 0 | 0 | 4 | 11 | 0 | 14 | 46 |

(NC は noncommercial。)

この表から分かること:

- 実装済み 101 件のうち、66 件は条件が open(`open`)。
- 候補 134 件のうち、11 件は `open` かつ `direct_download`(今すぐ入手可能)。次に実装する最初のグループ。

### 11.2 データの性質

- **録音の状況**(`recording_context`; 67 件は未確認): 演技 115、自然な会話 23、複数のウェブ由来 21、YouTube 14、テレビ番組 14、感情誘発 13、映画 12、読み上げ 8、合成 8、その他 8、人とエージェントの対話 7、ポッドキャスト 4、ほか。
- **言語**: 76 コード。英語(eng)89、中国語(cmn)36、韓国語(kor)16、スペイン語(spa)とドイツ語(deu)が各 14、フランス語(fra)12、日本語(jpn)11、多言語(mul)16。
- **生の音声**: 配布あり 186、配布なし 29、不明 4、未確認 103。
- **次元感情ラベルを持つデータセット**: 30。
- **ESPnet レシピの学習・評価**: 実施済み(`evaluated`)17、未実施(`not_run`)85。
- **音声の作られ方とラベルの付け方**(レシピ審査中に記入): 127 データセットで記入済み。知覚ラベル(`perceived`、単独または他と併用)は 47。
- **意図・対話行為のデータ**: 12(SLURP、Timers and Such、Fluent Speech Commands、Snips/Sonos、STOP、MInDS-14、Speech-MASSIVE、ITALIC、DIHANA、SpokenWOZ、Harper Valley Bank、SLUE-HVB)。
- **網羅の確認**: MSP-Podcast の論文(arXiv 2509.09791v1)の Table I にある 28 コーパスはすべて含まれている。

### 11.3 データの集め方

2026-10-14 に、サーベイ(SuperKogito の一覧、EmoBox、KuralHub など)、Hugging Face・Zenodo・Kaggle・Mendeley・figshare・GitHub・OpenSLR の検索、文献で知られているコーパスから 158 件を追加した。追加した行は、入手条件・ライセンス・ラベルを可能な限り一次資料で確認した。

## 12. DB の使い方(引く)

### 12.1 いちばん簡単: 表計算ソフトで開く

[views/datasets_wide.csv](../views/datasets_wide.csv) を Excel・Google スプレッドシート・LibreOffice で開く。1 行が 1 データセットで、フィルターで絞り込める。主な列:

- `dataset_id`: ID
- `status`: 状態(= `espnet_status`)
- `reasons`: 理由コード
- `license_class`、`access_method`、`raw_audio_available`
- `speech_production`、`label_basis`、`label_basis_note`
- `text_emotion_link`、`lexical_confound`、`lexical_confound_note`
- `paralinguistic_signal`、`paralinguistic_signal_note`
- `human_accuracy`、`human_accuracy_note`
- `source_rights`、`source_rights_note`
- `recipe`、`n_total_recipe`、`hours_total_recipe`: 実装済みのデータセットについて、レシピとその実測の件数・時間
- `common7_covered`、`common7_missing`: 共通 7 ラベル(angry、disgust、fear、happy、neutral、sad、surprise)のうちデータにあるもの、ないもの
- `benchmarks`: 所属するベンチマーク

最初の 15 列(Verified から ESPnet Implemented まで)は、元のスプレッドシートの名前のまま。

> `views/` は生成されたコピー。ここでの編集は、次に生成し直したときに失われる。`data/` を直す。

### 12.2 例 1: データセットを調べる

ターミナルで DB のフォルダに入って:

```bash
grep -i ravdess views/datasets_wide.csv
```

1 行の全項目を縦に見るには:

```bash
python3 tools/db.py get datasets ravdess
```

### 12.3 例 2: 値の出典を見る

`data/evidence.csv` を開き、`dataset_id` = `ravdess` かつ `field` = `license_spdx` で絞る。出典の URL(`source_ref`)・確認日・確認者が出る。

```bash
grep '^ravdess/license_spdx' data/evidence.csv
```

### 12.4 例 3: 食い違いを見る

[views/discrepancies.csv](../views/discrepancies.csv) に、DB の現在の値と他の出典の値が並んで出ている。スプレッドシートやサーベイの値が一次資料で訂正された行では、古い値がここに出る。

### 12.5 例 4: AI アシスタントに聞く

このプロジェクトで作業するアシスタントは、ウェブを検索する前にこの DB を引く。「日本語の感情データは何がある?」「まだ実装していない、オープンライセンスのデータセットは?」と聞けば、答えは DB から出る。重要な判断では、`source_type` が `sheet`・`project_doc`・`secondary` の根拠は裏取りが必要だと、答えに添えるべきである。

## 13. メンテナンス(更新と検査)

### 13.1 日常のコマンド

DB のフォルダで、システムの Python で実行する。

| コマンド | すること |
|---|---|
| `python3 tools/validate.py` | ESPnet のブランチ・レシピ・実測を含め、すべてを検査する |
| `python3 tools/validate.py --offline` | ESPnet を読まず、DB だけを検査する |
| `python3 tools/views.py` | `views/` を生成し直す |
| `python3 tools/db.py get\|set\|add\|fmt` | 行の表示・変更・追加、CSV の整形 |

実測には `tools/measure.py` を使い、`tools/sync.py` がそれをレシピの表に写す(手順は README の「Validation and updates」)。届いた報告の検証を含むメンテナンス全体の流れは、`.claude/skills/maintaining-ser-dataset-db/SKILL.md` にある。

普段は手で実行しない、その他のプログラム:

| ファイル | することは |
|---|---|
| `tools/csvio.py` | すべての CSV を決まった 1 つの形式で読み書きする(他のツールが使う) |
| `tools/egs3.py` | どのブランチをチェックアウトしていても、`git show` で ESPnet のブランチ `ser/cross-corpus` からレシピを読む |
| `tools/localenv.py` | マシン固有の設定(例: `ESPNET_REPO`)を `.env` から読む |
| `tools/hooks/pre-commit` | コミットのたびに走る検査 |
| `.claude/skills/.../scripts/reglib.py` | 1 つのデータセットの変更(根拠・セルの値・レシピの行・ラベル・アノテーション)をまとめ、`tools/db.py` 経由で保存する |
| `.claude/skills/.../scripts/audio_audit.py` | コーパスの音声を独立に検査する: ファイルの一覧、形式、長さ、同一・ほぼ同一のファイル |
| `.claude/skills/.../scripts/doc_counts.py` | このガイドと README の数値を数え直す |

### 13.2 検査の内容

- CSV の形式(UTF-8、行の順序)、列の型、許される値
- キーと外部キー(存在しない行を指す行がない)
- 根拠の規則(値ごとに canonical な根拠が 1 つ、実測値と公表値を混ぜない、…)
- `implemented` の行が ESPnet のレシピと合っているか
- `recipes.csv` と `recipe_labels.csv` が `measurements/*.json` と合っているか
- `annotations.csv` が存在するデータセットを指すか、`used_in_recipe=true` が実装済みだけか、`label_source` なしに `label_verification` が設定されていないか
- `views/` が最新か

### 13.3 変更の規則

- 値を変えるたびに根拠の行を付ける。
- 1 コミットは 1 データセット、または 1 回の確認作業。コミットメッセージ(英語)には、**何が間違っていたか**と根拠を書く。
- フックがコミットのたびに自動で検査し、通らないコミットは拒否される。検査を飛ばさない(`--no-verify` 禁止)。
- ファイルは名前を指定して stage する。`git add -A` や `git add .` は使わない。
- コミット済みの `dataset_id` は変えない(どうしても変えるなら、古い ID を別名として残す)。

### 13.4 レシピ作成者との分担

レシピの実装中に分かったこと(ラベルの問題、分割の癖など)は、DB に直接書かない。DB 更新レポートとして DB の担当者に渡し、担当者が一次資料と音声で検証してから、根拠つきで記録する。例外は、`measure.py` と `sync.py` が作る自動の実測値とレシピ表の更新。

## 14. ライセンスの人による確認

### 14.1 なぜ

ライセンスの根拠の大半は Claude や自動処理が集めたもの(`checked_by` が `claude` か `script`)で、API の項目やカードから機械的に取ったものもあるので、人による確認が望ましい。

### 14.2 どうするか

一括で確認するのではなく、**レシピを実装して審査するたびに、maintainer がそのデータセットのライセンスのページを見る**。結果は `checked_by=user` の根拠の行として足す。現在、maintainer が確認したライセンスの根拠があるのは 9 データセット(`akace`、`emodb`、`emotale`、`emotiontalk`、`iesc`、`rasa`、`recanvo`、`uftbesd`、`visec`)。

## 15. 限界(正直に)

報告では、できていないことも書く。

### 15.1 まだ確認していないこと

- **DB は ESPnet の実装に遅れている**: ESPnet のレシピのブランチには、単一コーパスのレシピが 102 データセット分あるが、そのうち 1 件はまだ `recipes.csv` になく、そのデータセットはまだ `implemented` ではない(`bari_emospeech`: 実測するにはコーパスをもう一度ダウンロードする必要がある)。`validate.py` はこれを警告として挙げる(エラーではない)。待っていた残りの 6 件(`anad`、`audiospeechsentiment`、`multidialog`、`rasa`、`thanushs25_tamil`、`visec`)は 2026-10-30 に登録した。
- **最小クリップ長を 0.5 秒から 0.2 秒に変更した**(ESPnet のコミット 96a54519743、2026-10-17)。`recipes.csv` の `min_wav_duration` はすべてのレシピで 0.2 だが、変更前に登録したレシピでは `n_train_filtered` と `n_valid_filtered` が古い実測のまま(最小 0.5 秒で数えたもの)。まだ測り直していない。
- **ライセンスの人による確認はほとんど始まっていない**(14.2)。DB のライセンスの大半は、Claude が確認した一次資料に基づく。
- **第三者のサーベイ(KuralHub)だけに裏づけられた 28 行**は、入手方法を一次資料で確認していない。古い論文のデータで、「要請があれば」と書かれているものが多い。
- **応答しなかった配布元があり**、確認できなかった行がある(`amigos`、`casia`、`cheavd`、`belfast`、`emotion_origlia2010`、`usoms`、`eyase`)。
- **`deferred` の 34 行**は、本当の入手経路をまだ調べる必要がある。
- **空欄(未調査)の値が残っている**: ライセンスが空欄 64、入手方法が空欄 50、録音の状況が空欄 67。
- **まだ調べていない領域**: CATSLU、MRDA・SwDA・AMI のような対話行為、ATIS の音声、他の言語の SLURP、他の言語の意図データ。

### 15.2 性質上の限界

- DB は**公開情報を整理したもの**で、法的助言ではない。ライセンスの分類は機械的な分類。
- 「データセットが存在する」と「使ってよい」は別のこと。使う前に、必ず一次資料と元の条件を読む。
- `measurements/` が手元のデータのコピーと今も合っているかは、自動では検査しない。
- データセットに感情ラベルがあるかは、論文だけでは判断しにくいことがある。不明なものはダウンロードして確認した(例: Expresso)。

### 15.3 MSP-Podcast の条件

MSP-Podcast は内部の非商用研究のみで、再配布は不可、Lotfian & Busso (2019) の引用が必要。標準のラベルセットは contempt を含む 8 クラス。

## 16. 進捗報告の話題

### 16.1 概要(1〜2 分)

1. **作ったもの**: SER とパラ言語情報のデータセットの、根拠つきの台帳。322 データセット、根拠 4,987 行。
2. **なぜ**: データセットの条件(ライセンス・入手方法)を毎回調べ直さずに済むようにし、クロスコーパス評価の根拠を保つため。
3. **信頼性の仕組み**: 各値が出典・日付・確認者を記録し、機械が規則を検査する。不明なことは推測で埋めず、不明と書く。
4. **実装とのつながり**: 102 の ESPnet レシピを DB に実測して取り込み、実装済み・候補・保留のデータセットを区別している(レシピのブランチは増え続けていて、新しいレシピは審査のあと登録する。15.1)。
5. **次**: レシピごとのライセンスの人による確認、保留 34 行の調査、未調査の領域の調査。

### 16.2 見せるもの

- [views/datasets_wide.csv](../views/datasets_wide.csv) を表計算ソフトで開き、フィルターをかける(例: `status`=candidate、`license_class`=open、`access_method`=direct_download → 11 行)。
- 根拠の例: `data/evidence.csv` を `ravdess` と `license_spdx` で絞り、スプレッドシートの値が Zenodo の一次資料に置き換わった経緯を見せる。

### 16.3 想定される質問

| 質問 | 答え |
|---|---|
| なぜ元のスプレッドシートでなく CSV か | スプレッドシートは出典・履歴・検査を持てない。git 管理の CSV なら変更履歴が残り、機械で検査できる |
| 情報は正しいか | すべての値に出典と日付がある。一次資料(論文・公式ページ)が最大のグループ(根拠 4,987 行のうち 2,490)。人による最終確認(ライセンス)はまだ進行中 |
| どう集めたか | スプレッドシートの 84 件に、サーベイ・ホスティングサービス・文献から 238 件を追加。追加した行は一次資料で確認した |
| 何件実装できるか | 実装済み 101、候補 134。候補のうち 11 件は、オープンライセンスで今すぐ入手できる |
| 何を除外したか | 46 件。明確な理由のみ: 音声なし、既存データの再配布、重複、地域制限など。手間や規模は理由にしない |
| ライセンスは信用できるか | DB は出典が述べる条件を記録している。法的な解釈ではない。使う前に原文を読むこと。人による確認はレシピごとに足している |
| 次は | レシピごとの人による確認、保留 34 行の調査、未調査の領域(対話行為、他の言語の意図データなど)の追加 |

### 16.4 言ってはいけないこと

- 「すべて人が確認した」(ライセンスの人による確認は一部のデータセットだけ、14.2)
- 「これらのライセンスなら使ってよい」(分類は機械的で、法的判断ではない)
- 「世界のデータセットを全部網羅している」(調べた範囲だけ。未調査の領域は 15.1 に列挙)

## 17. 困ったとき

| 状況 | どうするか |
|---|---|
| validate が失敗する | メッセージにファイル・行・原因が出る。多くは根拠の不足か、許される一覧にない値。直せなければ Claude に聞く |
| コミットできない | フックの検査が失敗している。同じ検査を手で走らせて原因を直す。`--no-verify` で回避しない |
| `views/` が古い | `tools/views.py` で生成し直す(検査も最新かを確かめる) |
| CSV を直接編集した | `tools/db.py fmt` を実行してから `validate.py` |
| 値が正しいか分からない | `evidence.csv` を `dataset_id` と `field` で絞り、`source_type` と `source_ref` を確認する |
| 変更を取り消したい | 自分で `reset` などを実行しない。先に聞く(履歴を書き換える操作は確認が必要) |

## 18. 付録

### 18.1 主なファイル

| ファイル | 内容 |
|---|---|
| README.md | 開発者向けの要約: 表・規約・根拠の規則・現在の状態 |
| schema/columns.csv | 全列の型と意味 |
| schema/enums.csv | 許される値(状態・理由・ライセンス・入手方法など) |
| schema/tables.csv | 各表のファイルとキー |
| data/ | 正のデータ(CSV 8 ファイル) |
| views/ | 生成された一覧と食い違いの一覧 |
| measurements/ | レシピの実測結果(JSON) |
| reports/ | 検証つきで保存した調査報告 |
| sheet_import/README.md | 元のスプレッドシートの由来と指紋 |
| tools/ | validate、views、db、measure、sync、およびその補助(13.1) |

### 18.2 この文書の更新

数値は第 11 節の日付時点のもの。DB が変わったら `data/*.csv` を数え直し(メンテナンス skill の `doc_counts.py` がこれを行う)、文章を更新する。**英語版 [manual.md](manual.md) とこの日本語版は、必ず同時に更新する**(片方だけ更新しない)。
