"""Recompute every count quoted in README.md and docs/manual.md from data/*.csv and rewrite it.

    python3 <skill dir>/scripts/doc_counts.py            # dry run: print each change
    python3 <skill dir>/scripts/doc_counts.py --write    # apply the changes

Each rule is a regular expression for one known sentence or table row of the documents. The
documents are written in Japanese, so the patterns are too. A rule whose text is not found is
reported as MISSING and the script exits with status 1: the sentence was reworded, so update the
rule (or the document) instead of leaving a stale number behind. Breakdowns that need judgement
(the exclusion breakdown in manual section 8.2) are printed for a manual check, not rewritten.
"""

import argparse
import collections
import csv
import re
import sys
from datetime import date
from pathlib import Path


def _find_root():
    for p in Path(__file__).resolve().parents:
        if (p / "tools" / "validate.py").is_file() and (p / "data" / "datasets.csv").is_file():
            return p
    raise SystemExit("doc_counts: could not find the DB root (a parent with tools/validate.py)")


ROOT = _find_root()


def load(name):
    with open(ROOT / "data" / f"{name}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def n(x):
    return f"{x:,}"


def stats():
    d = load("datasets")
    e = load("evidence")
    r = load("recipes")
    s = {}
    st = collections.Counter(x["espnet_status"] for x in d)
    s["status"] = st
    s["n_datasets"] = len(d)
    s["in_sheet"] = sum(x["in_sheet"] == "true" for x in d)
    s["n_evidence"] = len(e)
    s["src"] = collections.Counter(x["source_type"] for x in e)
    s["ev_last"] = max(x["checked_on"] for x in e)
    s["rows"] = {t: len(load(t)) for t in ["datasets", "evidence", "aliases", "relations", "recipes",
                                           "recipe_labels", "benchmark_membership", "annotations"]}
    s["ann_by"] = sorted(collections.Counter(x["dataset_id"] for x in load("annotations")).items())
    s["rel"] = collections.Counter(x["relation"] for x in load("relations"))
    s["kind"] = collections.Counter(x["recipe_kind"] for x in r)
    s["baseline"] = collections.Counter(x["baseline_status"] for x in r)
    s["unexamined"] = sum("unexamined" in x["status_reason_codes"].split(";") for x in d)
    s["lic"] = collections.Counter(x["license_class"] for x in d)
    s["acc"] = collections.Counter(x["access_method"] for x in d)
    s["st_lic"] = collections.Counter((x["espnet_status"], x["license_class"]) for x in d)
    s["impl_open"] = s["st_lic"][("implemented", "open")]
    s["cand_open_direct"] = sum(x["espnet_status"] == "candidate" and x["license_class"] == "open"
                                and x["access_method"] == "direct_download" for x in d)
    s["rc"] = collections.Counter(x["recording_context"] for x in d)
    s["raw"] = collections.Counter(x["raw_audio_available"] for x in d)
    s["dim"] = sum(x["dimensional_attributes"] not in ("", "none", "NA", "unknown") for x in d)
    langs = collections.Counter()
    for x in d:
        for c in x["languages"].split(";"):
            if c:  # 'unknown' is counted as a code, matching how the manual has always counted
                langs[c] += 1
    s["langs"] = langs
    s["blank"] = {k: sum(x[k] == "" for x in d) for k in ["license_spdx", "access_method", "recording_context"]}
    s["excl_codes"] = collections.Counter(c for x in d if x["espnet_status"] == "excluded"
                                          for c in x["status_reason_codes"].split(";"))
    return s


LIC_COLS = ["open", "noncommercial", "research_only", "restricted", "other", "none_stated", "unknown",
            "conflicting", ""]
# Start of each description cell in manual sections 9.2 and 10, so that every rule matches exactly one table row.
LIC_DESC = {"open": "制限が緩い", "noncommercial": "非商用限定", "research_only": "学術・研究目的に限定",
            "restricted": "制限つき・有償", "other": "上記以外", "none_stated": "ライセンスの記載が見つからない",
            "unknown": "調べたが決まらない", "conflicting": "資料の間で食い違う"}
ACC_DESC = {"direct_download": "認証なしで", "free_account_required": "無料アカウント",
            "gated_click_through": "同意などのクリック", "request_form_or_email": "申請フォーム",
            "signed_agreement": "署名した同意書", "paid_or_membership": "有償・会員制",
            "unofficial_mirror_only": "非公式のミラー", "unavailable": "入手できない", "unknown": "不明"}
RC_JA = {"acted": "演技", "spontaneous_conversation": "自発的会話", "multi_source_web": "複数ウェブ由来",
         "youtube": "YouTube", "affect_elicitation": "感情誘発", "movie_film": "映画", "tv_show": "テレビ番組",
         "read_speech": "朗読", "other": "その他", "human_agent_interaction": "人と機械の対話", "synthetic": "合成",
         "podcast": "ポッドキャスト", "talk_show": "トーク番組", "non_speech_vocalization": "非言語の発声",
         "child_robot_interaction": "子どもとロボットの対話", "unknown": "不明"}


def rules(s, today):
    st = s["status"]
    md = today[5:]
    ann = "、".join(f"`{k}` {v}" for k, v in s["ann_by"])
    ann_readme = "、".join(f"`{k}` の{v}行" for k, v in s["ann_by"])
    rel_order = ["contains", "distinct_from", "subset_of", "possibly_same_as", "version_of"]
    rel_ja = {"contains": "含む", "distinct_from": "名前が似た別物", "subset_of": "一部",
              "possibly_same_as": "同一の疑い", "version_of": "版違い"}
    rel = "、".join(f"`{k}`({rel_ja[k]}){s['rel'][k]}" for k in sorted(rel_order, key=lambda k: -s["rel"][k]))
    src = "、".join(f"{k} {n(v)}" for k, v in s["src"].most_common())
    rc_items = [(k, v) for k, v in s["rc"].most_common() if k and v >= 4]
    rc = "、".join(f"{RC_JA.get(k, k)} {v}" for k, v in rc_items)

    def lic_row(status):
        vals = [s["st_lic"][(status, c)] for c in LIC_COLS]
        return f"| {status} | " + " | ".join(str(v) for v in vals) + f" | {st[status]} |"

    def lang_sub(m):
        text = re.sub(r"コードで\d+種類", f"コードで{len(s['langs'])}種類", m.group(0))
        text = re.sub(r"\((\w{3})\)(\d+)件", lambda mm: f"({mm.group(1)}){s['langs'][mm.group(1)]}件", text)

        def pair(mm):
            a, b = s["langs"][mm.group(1)], s["langs"][mm.group(2)]
            if a != b:
                print(f"NOTE     languages: {mm.group(1)}={a}, {mm.group(2)}={b} differ; rewrite the '各' phrase by hand")
            return re.sub(r"各\d+件$", f"各{a}件", mm.group(0))
        return re.sub(r"\((\w{3})\)・[^(、]+\((\w{3})\)各\d+件", pair, text)

    R = [
        # README
        ("README.md", r"\d+データセット\(シート由来\d+・シート外\d+\)。`implemented` \d+、`candidate` \d+、`deferred` \d+、`needs_decision` \d+、`excluded` \d+。",
         f"{s['n_datasets']}データセット(シート由来{s['in_sheet']}・シート外{s['n_datasets'] - s['in_sheet']})。`implemented` {st['implemented']}、`candidate` {st['candidate']}、`deferred` {st['deferred']}、`needs_decision` {st['needs_decision']}、`excluded` {st['excluded']}。"),
        ("README.md", r"## 現状\(\d{4}-\d{2}-\d{2}\)", f"## 現状({today})"),
        ("README.md", r"現在は (`[a-z0-9_]+` の\d+行、)*`[a-z0-9_]+` の\d+行で、", f"現在は {ann_readme}で、"),
        ("README.md", r"`deferred` の\d+件。", f"`deferred` の{st['deferred']}件。"),
        # manual 1.2
        ("docs/manual.md", r"\| 登録データセット数 \| \*\*\d+件\*\*\(元のシート由来\d+件 \+ 新たに調べて足した\d+件\) \|",
         f"| 登録データセット数 | **{s['n_datasets']}件**(元のシート由来{s['in_sheet']}件 + 新たに調べて足した{s['n_datasets'] - s['in_sheet']}件) |"),
        ("docs/manual.md", r"\| ESPnet に実装済み \| \d+件 \|", f"| ESPnet に実装済み | {st['implemented']}件 |"),
        ("docs/manual.md", r"\| 次の実装候補 \| \d+件 \|", f"| 次の実装候補 | {st['candidate']}件 |"),
        ("docs/manual.md", r"\| 判断待ち \| \d+件 \|", f"| 判断待ち | {st['needs_decision']}件 |"),
        ("docs/manual.md", r"\| 保留 \| \d+件 \|", f"| 保留 | {st['deferred']}件 |"),
        ("docs/manual.md", r"\| 除外\(理由つき\) \| \d+件 \|", f"| 除外(理由つき) | {st['excluded']}件 |"),
        ("docs/manual.md", r"\| 値ごとの「根拠」の記録 \| [\d,]+行 \|", f"| 値ごとの「根拠」の記録 | {n(s['n_evidence'])}行 |"),
        ("docs/manual.md", r"\| 登場する言語コード \| \d+種類 \|", f"| 登場する言語コード | {len(s['langs'])}種類 |"),
        # manual 4.2
        ("docs/manual.md", r"(\*\*1つのデータセット\*\*\(中心になる表\) \| )\d+ \|", rf"\g<1>{s['rows']['datasets']} |"),
        ("docs/manual.md", r"(datasets の1つの値の\*\*根拠\*\* \| )[\d,]+ \|", rf"\g<1>{n(s['rows']['evidence'])} |"),
        ("docs/manual.md", r"(別名\(公式名・略称・旧名・レシピ名など\) \| )\d+ \|", rf"\g<1>{s['rows']['aliases']} |"),
        ("docs/manual.md", r"(データセット同士の関係 \| )\d+ \|", rf"\g<1>{s['rows']['relations']} |"),
        ("docs/manual.md", r"(ESPnet の1レシピ \| )\d+ \|", rf"\g<1>{s['rows']['recipes']} |"),
        ("docs/manual.md", r"(レシピ×ラベル \| )\d+ \|", rf"\g<1>{s['rows']['recipe_labels']} |"),
        ("docs/manual.md", r"(ベンチマークを構成するレシピ \| )\d+ \|", rf"\g<1>{s['rows']['benchmark_membership']} |"),
        ("docs/manual.md", r"(書き起こし・話者特性・対話行為など\) \| )\d+\((`[a-z0-9_]+` \d+、)*`[a-z0-9_]+` \d+。",
         rf"\g<1>{s['rows']['annotations']}({ann}。"),
        ("docs/manual.md", r"関係の内訳は [^。]+。", f"関係の内訳は {rel}。"),
        ("docs/manual.md", r"レシピ\d+件のうち\d+件は1コーパス用\(`single_corpus`\)、\d+件が複数コーパスを合わせたもの\(`multi_corpus`\)。",
         f"レシピ{s['rows']['recipes']}件のうち{s['kind']['single_corpus']}件は1コーパス用(`single_corpus`)、{s['kind']['multi_corpus']}件が複数コーパスを合わせたもの(`multi_corpus`)。"),
        # manual 6
        ("docs/manual.md", r"確認日\(`checked_on`\)は全[\d,]+行に入っている\(2026-10-10〜\d{2}-\d{2}\)",
         f"確認日(`checked_on`)は全{n(s['n_evidence'])}行に入っている(2026-10-10〜{s['ev_last'][5:]})"),
        ("docs/manual.md", r"現在の根拠[\d,]+行の内訳は、[^。]+。", f"現在の根拠{n(s['n_evidence'])}行の内訳は、{src}。"),
        # manual 8
        ("docs/manual.md", r"(\| `implemented` \| ESPnet にレシピがある \| )\d+ \|", rf"\g<1>{st['implemented']} |"),
        ("docs/manual.md", r"(\| `candidate` \| 追加の候補。[^|]+\| )\d+ \|", rf"\g<1>{st['candidate']} |"),
        ("docs/manual.md", r"(\| `needs_decision` \| [^|]+\| )\d+ \|", rf"\g<1>{st['needs_decision']} |"),
        ("docs/manual.md", r"(\| `deferred` \| 保留。[^|]+\| )\d+ \|", rf"\g<1>{st['deferred']} |"),
        ("docs/manual.md", r"(\| `excluded` \| 明確な理由があって扱わない \| )\d+ \|", rf"\g<1>{st['excluded']} |"),
        ("docs/manual.md", r"現在の除外\d+件の内訳は", f"現在の除外{st['excluded']}件の内訳は"),
        ("docs/manual.md", r"`unexamined`\(まだ実装を検討していない\)が最多で\d+件",
         f"`unexamined`(まだ実装を検討していない)が最多で{s['unexamined']}件"),
        # manual 9.2 / 10
        *[("docs/manual.md", rf"(\| `{c}` \| {LIC_DESC[c]}[^|]*\| )\d+ \|", rf"\g<1>{s['lic'][c]} |") for c in LIC_DESC],
        ("docs/manual.md", r"(\| \(空欄\) \| まだ調べていない \| )\d+ \|", rf"\g<1>{s['lic']['']} |"),
        *[("docs/manual.md", rf"(\| `{a}` \| {ACC_DESC[a]}[^|]*\| )\d+ \|", rf"\g<1>{s['acc'][a]} |") for a in ACC_DESC],
        ("docs/manual.md", r"(\| \(空欄\) \| 未確認 \| )\d+ \|", rf"\g<1>{s['acc']['']} |"),
        # manual 11
        ("docs/manual.md", r"## 11\. 現在の数字\(\d{4}-\d{2}-\d{2}\)", f"## 11. 現在の数字({today})"),
        *[("docs/manual.md", rf"\| {k} \|( \d+ \|){{10}}", lic_row(k)) for k in
          ["implemented", "candidate", "needs_decision", "deferred", "excluded"]],
        ("docs/manual.md", r"実装済み\d+件のうち、オープンな条件\(`open`\)は\d+件",
         f"実装済み{st['implemented']}件のうち、オープンな条件(`open`)は{s['impl_open']}件"),
        ("docs/manual.md", r"候補\d+件のうち、ライセンスが `open` で `direct_download`\(すぐ取れる\)なものは\d+件",
         f"候補{st['candidate']}件のうち、ライセンスが `open` で `direct_download`(すぐ取れる)なものは{s['cand_open_direct']}件"),
        ("docs/manual.md", r"\*\*録音の状況\*\*\(`recording_context`、\d+件は未調査\): [^。]+ など。",
         f"**録音の状況**(`recording_context`、{s['blank']['recording_context']}件は未調査): {rc} など。"),
        ("docs/manual.md", r"\*\*言語\*\*: コードで\d+種類。[^\n]+", lang_sub),
        ("docs/manual.md", r"\*\*生音声の有無\*\*: 配布あり \d+、なし \d+、不明 \d+、未確認 \d+。",
         f"**生音声の有無**: 配布あり {s['raw']['true']}、なし {s['raw']['false']}、不明 {s['raw']['unknown']}、未確認 {s['raw']['']}。"),
        ("docs/manual.md", r"\*\*次元感情のラベルがあるもの\*\*: \d+件。", f"**次元感情のラベルがあるもの**: {s['dim']}件。"),
        ("docs/manual.md", r"実施済み\(`evaluated`\)\d+、未実施\(`not_run`\)\d+",
         f"実施済み(`evaluated`){s['baseline']['evaluated']}、未実施(`not_run`){s['baseline']['not_run']}"),
        # manual 15-16
        ("docs/manual.md", r"\*\*保留\(`deferred`\)\d+件\*\*", f"**保留(`deferred`){st['deferred']}件**"),
        ("docs/manual.md", r"ライセンスが空欄\d+件、入手方法が空欄\d+件、録音の状況が空欄\d+件",
         f"ライセンスが空欄{s['blank']['license_spdx']}件、入手方法が空欄{s['blank']['access_method']}件、録音の状況が空欄{s['blank']['recording_context']}件"),
        ("docs/manual.md", r"根拠つき台帳。\d+件、根拠[\d,]+行。", f"根拠つき台帳。{s['n_datasets']}件、根拠{n(s['n_evidence'])}行。"),
        ("docs/manual.md", r"ESPnet の\d+レシピを実測して", f"ESPnet の{s['rows']['recipes']}レシピを実測して"),
        ("docs/manual.md", r"保留\d+件の調査", f"保留{st['deferred']}件の調査"),
        ("docs/manual.md", r"`access_method`=direct_download → \d+件", f"`access_method`=direct_download → {s['cand_open_direct']}件"),
        ("docs/manual.md", r"根拠[\d,]+行のうち[\d,]+行\)", f"根拠{n(s['n_evidence'])}行のうち{n(s['src']['primary'])}行)"),
        ("docs/manual.md", r"実装済み\d+件、候補\d+件。候補のうちライセンスがオープンですぐ取れるものは\d+件",
         f"実装済み{st['implemented']}件、候補{st['candidate']}件。候補のうちライセンスがオープンですぐ取れるものは{s['cand_open_direct']}件"),
        ("docs/manual.md", r"\| 除外したものは \| \d+件。", f"| 除外したものは | {st['excluded']}件。"),
        ("docs/manual.md", r"元のシート\d+件に、総説・各種ホスティングサービス・文献から\d+件を足した。",
         f"元のシート{s['in_sheet']}件に、総説・各種ホスティングサービス・文献から{s['n_datasets'] - s['in_sheet']}件を足した。"),
    ]
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args()
    s = stats()
    texts = {p: (ROOT / p).read_text(encoding="utf-8") for p in ["README.md", "docs/manual.md"]}
    missing = 0
    for path, pat, rep in rules(s, a.today):
        ms = list(re.finditer(pat, texts[path]))
        if not ms:
            print(f"MISSING  {path}: /{pat[:70]}/")
            missing += 1
            continue
        new = re.sub(pat, rep, texts[path])
        if new != texts[path]:
            for m in ms:
                after = re.sub(pat, rep, m.group(0))
                if after != m.group(0):
                    print(f"CHANGE   {path}: {m.group(0)[:90]}\n      -> {after[:90]}")
            texts[path] = new
    print("\nCheck by hand (manual 8.2 exclusion breakdown, reason code -> rows):",
          dict(s["excl_codes"].most_common()))
    if a.write:
        for p, t in texts.items():
            (ROOT / p).write_text(t, encoding="utf-8")
        print("written")
    else:
        print("dry run (use --write to apply)")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
