"""Recompute every count quoted in README.md and docs/manual.md from data/*.csv and rewrite it.

    python3 <skill dir>/scripts/doc_counts.py            # dry run: print each change
    python3 <skill dir>/scripts/doc_counts.py --write    # apply the changes

Each rule is a regular expression for one known sentence or table row of the documents. A rule
whose text is not found is reported as MISSING and the script exits with status 1: the sentence
was reworded, so update the rule (or the document) instead of leaving a stale number behind.
Breakdowns that need judgement (the exclusion breakdown in manual section 8.2) are printed for a
manual check, not rewritten.
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

LIC_COLS = ["open", "noncommercial", "research_only", "restricted", "other", "none_stated", "unknown",
            "conflicting", ""]
# Start of each description cell in manual sections 9.2 and 10, so that every rule matches exactly one row.
LIC_DESC = {"open": "permissive", "noncommercial": "non-commercial only", "research_only": "custom terms limited",
            "restricted": "restricted or paid", "other": "other than the above",
            "none_stated": "no license statement found", "unknown": "examined but undecidable",
            "conflicting": "sources disagree"}
ACC_DESC = {"direct_download": "directly downloadable", "free_account_required": "free account",
            "gated_click_through": "consent click", "request_form_or_email": "request by application",
            "signed_agreement": "signed agreement required", "paid_or_membership": "paid or membership",
            "unofficial_mirror_only": "only unofficial mirrors", "unavailable": "cannot be obtained",
            "unknown": "unknown"}
STATUS_DESC = {"implemented": "an ESPnet recipe exists", "candidate": "candidate for addition",
               "needs_decision": "only the project maintainer", "deferred": "not confirmed",
               "excluded": "not used, for a clear reason"}
RC_EN = {"acted": "acted", "spontaneous_conversation": "spontaneous conversation",
         "multi_source_web": "multi-source web", "youtube": "YouTube", "affect_elicitation": "affect elicitation",
         "movie_film": "film", "tv_show": "TV show", "read_speech": "read speech", "other": "other",
         "human_agent_interaction": "human-agent interaction", "synthetic": "synthetic", "podcast": "podcast",
         "talk_show": "talk show", "non_speech_vocalization": "non-speech vocalisation",
         "child_robot_interaction": "child-robot interaction", "unknown": "unknown"}
REL_EN = {"contains": "`contains` {}", "distinct_from": "`distinct_from` (similar names, different datasets) {}",
          "subset_of": "`subset_of` {}", "possibly_same_as": "`possibly_same_as` (suspected identity) {}",
          "version_of": "`version_of` {}"}


def load(name):
    with open(ROOT / "data" / f"{name}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def n(x):
    return f"{x:,}"


def stats():
    d, e, r = load("datasets"), load("evidence"), load("recipes")
    s = {"status": collections.Counter(x["espnet_status"] for x in d), "n_datasets": len(d),
         "in_sheet": sum(x["in_sheet"] == "true" for x in d), "n_evidence": len(e),
         "src": collections.Counter(x["source_type"] for x in e), "ev_last": max(x["checked_on"] for x in e)}
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
    s["basis_filled"] = sum(x["label_basis"] != "" for x in d)
    s["perceived"] = sum("perceived" in x["label_basis"].split(";") for x in d)
    s["user_lic"] = sorted({x["dataset_id"] for x in e if x["field"] == "license_spdx"
                            and x["checked_by"] == "user" and x["is_canonical"] == "true"})
    s["excl_codes"] = collections.Counter(c for x in d if x["espnet_status"] == "excluded"
                                          for c in x["status_reason_codes"].split(";"))
    return s


def rules(s, today):
    st = s["status"]
    added = s["n_datasets"] - s["in_sheet"]
    ann = ", ".join(f"`{k}` {v}" for k, v in s["ann_by"])
    rel = ", ".join(REL_EN[k].format(s["rel"][k]) for k in sorted(REL_EN, key=lambda k: -s["rel"][k]))
    src = ", ".join(f"{k} {n(v)}" for k, v in s["src"].most_common())
    rc = ", ".join(f"{RC_EN.get(k, k)} {v}" for k, v in s["rc"].most_common() if k and v >= 4)
    users = ", ".join(f"`{u}`" for u in s["user_lic"])

    def lic_row(status):
        vals = [s["st_lic"][(status, c)] for c in LIC_COLS]
        return f"| {status} | " + " | ".join(str(v) for v in vals) + f" | {st[status]} |"

    def lang_sub(m):
        text = re.sub(r"\d+ codes", f"{len(s['langs'])} codes", m.group(0))
        text = re.sub(r"\((\w{3})\) (\d+)(?! each)", lambda mm: f"({mm.group(1)}) {s['langs'][mm.group(1)]}", text)

        def pair(mm):
            a, b = s["langs"][mm.group(1)], s["langs"][mm.group(2)]
            if a != b:
                print(f"NOTE     languages: {mm.group(1)}={a}, {mm.group(2)}={b} differ; rewrite the 'each' phrase by hand")
            return re.sub(r"\d+ each$", f"{a} each", mm.group(0))
        return re.sub(r"\((\w{3})\) and [^(,]+\((\w{3})\) \d+ each", pair, text)

    R = [
        # README
        ("README.md", r"\d+ datasets \(\d+ from the spreadsheet, \d+ added later\)\. `implemented` \d+, `candidate` \d+, `deferred` \d+, `needs_decision` \d+, `excluded` \d+\.",
         f"{s['n_datasets']} datasets ({s['in_sheet']} from the spreadsheet, {added} added later). `implemented` {st['implemented']}, `candidate` {st['candidate']}, `deferred` {st['deferred']}, `needs_decision` {st['needs_decision']}, `excluded` {st['excluded']}."),
        ("README.md", r"## Current state \(\d{4}-\d{2}-\d{2}\)", f"## Current state ({today})"),
        ("README.md", r"Currently: (`[a-z0-9_]+` \d+, )*`[a-z0-9_]+` \d+;", f"Currently: {ann};"),
        ("README.md", r"The `deferred` rows \(\d+\)\.", f"The `deferred` rows ({st['deferred']})."),
        # manual 1.2
        ("docs/manual.md", r"\| Datasets registered \| \*\*\d+\*\* \(\d+ from the original spreadsheet \+ \d+ added later\) \|",
         f"| Datasets registered | **{s['n_datasets']}** ({s['in_sheet']} from the original spreadsheet + {added} added later) |"),
        ("docs/manual.md", r"\| Implemented in ESPnet \| \d+ \|", f"| Implemented in ESPnet | {st['implemented']} |"),
        ("docs/manual.md", r"\| Candidates for implementation \| \d+ \|", f"| Candidates for implementation | {st['candidate']} |"),
        ("docs/manual.md", r"\| Awaiting a decision \| \d+ \|", f"| Awaiting a decision | {st['needs_decision']} |"),
        ("docs/manual.md", r"\| Deferred \| \d+ \|", f"| Deferred | {st['deferred']} |"),
        ("docs/manual.md", r"\| Excluded \(with reasons\) \| \d+ \|", f"| Excluded (with reasons) | {st['excluded']} |"),
        ("docs/manual.md", r"\| Evidence rows \(sources of values\) \| [\d,]+ \|", f"| Evidence rows (sources of values) | {n(s['n_evidence'])} |"),
        ("docs/manual.md", r"\| Language codes \| \d+ \|", f"| Language codes | {len(s['langs'])} |"),
        # manual 4.2
        ("docs/manual.md", r"(\(the central table\) \| )\d+ \|", rf"\g<1>{s['rows']['datasets']} |"),
        ("docs/manual.md", r"(of one value in datasets \| )[\d,]+ \|", rf"\g<1>{n(s['rows']['evidence'])} |"),
        ("docs/manual.md", r"(former name, recipe name, \.\.\.\) \| )\d+ \|", rf"\g<1>{s['rows']['aliases']} |"),
        ("docs/manual.md", r"(\| a relation between datasets \| )\d+ \|", rf"\g<1>{s['rows']['relations']} |"),
        ("docs/manual.md", r"(\| one ESPnet recipe \| )\d+ \|", rf"\g<1>{s['rows']['recipes']} |"),
        ("docs/manual.md", r"(\| recipe x label \| )\d+ \|", rf"\g<1>{s['rows']['recipe_labels']} |"),
        ("docs/manual.md", r"(\| a recipe that is part of a benchmark \| )\d+ \|", rf"\g<1>{s['rows']['benchmark_membership']} |"),
        ("docs/manual.md", r"(speaker traits, dialogue acts, \.\.\.\) \| )\d+ \((`[a-z0-9_]+` \d+, )*`[a-z0-9_]+` \d+;",
         rf"\g<1>{s['rows']['annotations']} ({ann};"),
        ("docs/manual.md", r"Relations by type: [^.]+\.", f"Relations by type: {rel}."),
        ("docs/manual.md", r"Of the \d+ recipes, \d+ are for a single corpus \(`single_corpus`\) and \d+ combines? several corpora \(`multi_corpus`\)\.",
         f"Of the {s['rows']['recipes']} recipes, {s['kind']['single_corpus']} are for a single corpus (`single_corpus`) and {s['kind']['multi_corpus']} combines several corpora (`multi_corpus`)."),
        # manual 6
        ("docs/manual.md", r"Every one of the [\d,]+ evidence rows has a date checked \(`checked_on`, 2026-10-10 to \d{2}-\d{2}\)",
         f"Every one of the {n(s['n_evidence'])} evidence rows has a date checked (`checked_on`, 2026-10-10 to {s['ev_last'][5:]})"),
        ("docs/manual.md", r"The [\d,]+ evidence rows by source type: [^.]+\.", f"The {n(s['n_evidence'])} evidence rows by source type: {src}."),
        # manual 8
        *[("docs/manual.md", rf"(\| `{k}` \| {re.escape(v)}[^|]*\| )\d+ \|", rf"\g<1>{st[k]} |") for k, v in STATUS_DESC.items()],
        ("docs/manual.md", r"The \d+ excluded rows break down as", f"The {st['excluded']} excluded rows break down as"),
        ("docs/manual.md", r"\(implementation not yet considered\), on \d+ rows", f"(implementation not yet considered), on {s['unexamined']} rows"),
        # manual 9.2 / 10
        *[("docs/manual.md", rf"(\| `{c}` \| {re.escape(v)}[^|]*\| )\d+ \|", rf"\g<1>{s['lic'][c]} |") for c, v in LIC_DESC.items()],
        ("docs/manual.md", r"(\| \(empty\) \| not investigated yet \| )\d+ \|", rf"\g<1>{s['lic']['']} |"),
        *[("docs/manual.md", rf"(\| `{a}` \| {re.escape(v)}[^|]*\| )\d+ \|", rf"\g<1>{s['acc'][a]} |") for a, v in ACC_DESC.items()],
        ("docs/manual.md", r"(\| \(empty\) \| not checked \| )\d+ \|", rf"\g<1>{s['acc']['']} |"),
        # manual 11
        ("docs/manual.md", r"## 11\. Current figures \(\d{4}-\d{2}-\d{2}\)", f"## 11. Current figures ({today})"),
        *[("docs/manual.md", rf"\| {k} \|( \d+ \|){{10}}", lic_row(k)) for k in STATUS_DESC],
        ("docs/manual.md", r"Of the \d+ implemented datasets, \d+ have open terms",
         f"Of the {st['implemented']} implemented datasets, {s['st_lic'][('implemented', 'open')]} have open terms"),
        ("docs/manual.md", r"Of the \d+ candidates, \d+ are `open` and `direct_download`",
         f"Of the {st['candidate']} candidates, {s['cand_open_direct']} are `open` and `direct_download`"),
        ("docs/manual.md", r"\*\*Recording context\*\* \(`recording_context`; \d+ not checked\): [^.]+, and others\.",
         f"**Recording context** (`recording_context`; {s['blank']['recording_context']} not checked): {rc}, and others."),
        ("docs/manual.md", r"\*\*Languages\*\*: \d+ codes\.[^\n]+", lang_sub),
        ("docs/manual.md", r"\*\*Raw audio\*\*: distributed \d+, not distributed \d+, unknown \d+, not checked \d+\.",
         f"**Raw audio**: distributed {s['raw']['true']}, not distributed {s['raw']['false']}, unknown {s['raw']['unknown']}, not checked {s['raw']['']}."),
        ("docs/manual.md", r"\*\*Datasets with dimensional emotion labels\*\*: \d+\.", f"**Datasets with dimensional emotion labels**: {s['dim']}."),
        ("docs/manual.md", r"done \(`evaluated`\) \d+, not run \(`not_run`\) \d+",
         f"done (`evaluated`) {s['baseline']['evaluated']}, not run (`not_run`) {s['baseline']['not_run']}"),
        ("docs/manual.md", r"filled for \d+ datasets; perceived labels \(`perceived`, alone or with others\) on \d+",
         f"filled for {s['basis_filled']} datasets; perceived labels (`perceived`, alone or with others) on {s['perceived']}"),
        # manual 14-16
        ("docs/manual.md", r"license evidence checked by the maintainer exists for \d+ datasets \([^)]*\)",
         f"license evidence checked by the maintainer exists for {len(s['user_lic'])} datasets ({users})"),
        ("docs/manual.md", r"\*\*The \d+ `deferred` rows\*\*", f"**The {st['deferred']} `deferred` rows**"),
        ("docs/manual.md", r"license empty for \d+, access method empty for \d+, recording context empty for \d+",
         f"license empty for {s['blank']['license_spdx']}, access method empty for {s['blank']['access_method']}, recording context empty for {s['blank']['recording_context']}"),
        ("docs/manual.md", r"\d+ datasets, [\d,]+ evidence rows\.", f"{s['n_datasets']} datasets, {n(s['n_evidence'])} evidence rows."),
        ("docs/manual.md", r"the \d+ ESPnet recipes are measured", f"the {s['rows']['recipes']} ESPnet recipes are measured"),
        ("docs/manual.md", r"investigating the \d+ deferred rows", f"investigating the {st['deferred']} deferred rows"),
        ("docs/manual.md", r"`access_method`=direct_download -> \d+ rows", f"`access_method`=direct_download -> {s['cand_open_direct']} rows"),
        ("docs/manual.md", r"\([\d,]+ of [\d,]+ evidence rows\)", f"({n(s['src']['primary'])} of {n(s['n_evidence'])} evidence rows)"),
        ("docs/manual.md", r"\d+ implemented, \d+ candidates\. Of the candidates, \d+ are openly licensed",
         f"{st['implemented']} implemented, {st['candidate']} candidates. Of the candidates, {s['cand_open_direct']} are openly licensed"),
        ("docs/manual.md", r"\| What was excluded\? \| \d+\.", f"| What was excluded? | {st['excluded']}."),
        ("docs/manual.md", r"\d+ datasets from surveys, hosting services and the literature were added to the spreadsheet's \d+",
         f"{added} datasets from surveys, hosting services and the literature were added to the spreadsheet's {s['in_sheet']}"),
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
        for m in ms:
            after = re.sub(pat, rep, m.group(0))
            if after != m.group(0):
                print(f"CHANGE   {path}: {m.group(0)[:90]}\n      -> {after[:90]}")
        texts[path] = re.sub(pat, rep, texts[path])
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
