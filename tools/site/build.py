"""Build a browsable, read-only HTML page of the DB (cache/site/index.html).

Usage: python3 tools/site/build.py

The page embeds the data of data/*.csv (datasets, their child rows, evidence and sources) as
JSON in tools/site/template.html. Nothing from local/ is included.
"""

import csv
import datetime
import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "cache" / "site" / "index.html"


def rows(name):
    with open(ROOT / "data" / f"{name}.csv", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def by_ds(name):
    out = defaultdict(list)
    for r in rows(name):
        out[r["dataset_id"]].append(r)
    return out


def semi(s):
    return [x for x in s.split(";") if x]


def main():
    view = {r["dataset_id"]: r for r in csv.DictReader(open(ROOT / "views" / "datasets_wide.csv", encoding="utf-8"))}
    norm = {r["source_label"]: r["normalized"] for r in rows("label_normalization")}
    srcs = rows("sources")
    sidx = {s["source_id"]: i for i, s in enumerate(srcs)}
    S = [[s["source_id"], s["url"], s["title"], s["kind"], s["source_type"]] for s in srcs]
    ev, links, anns = by_ds("evidence"), by_ds("dataset_sources"), by_ds("annotations")
    issues, counts, rels, aliases = by_ds("issues"), by_ds("label_counts"), by_ds("relations"), by_ds("aliases")
    D = []
    for d in rows("datasets"):
        i, v = d["dataset_id"], view[d["dataset_id"]]
        cats = semi(d["emotion_categories"])
        D.append({
            "id": i, "name": d["name"], "full": d["full_title"], "lang": d["languages"], "langn": d["language_note"],
            "vc": d["vocal_content"], "mo": d["material_origin"], "lic": d["license_spdx"], "licn": d["license_note"],
            "am": d["access_method"], "ao": d["access_observed"], "aoo": d["access_observed_on"],
            "nf": d["n_files_reported"], "h": d["hours_reported"], "ns": d["n_speakers_reported"],
            "rf": d["n_files_release"], "rs": d["n_speakers_release"], "rh": d["hours_release"],
            "cats": cats, "labs": sorted({norm.get(c, c) for c in cats if c != "none"}), "attrs": d["emotion_attributes"],
            "mlt": d["main_label_set_type"], "ml": d["main_labels"], "ls": d["label_source"], "lv": d["label_verification"],
            "sp": d["speech_production"], "lb": d["label_basis"], "std": d["spoken_text_design"], "split": d["official_split"],
            "lt": d["listening_test"], "srn": d["source_rights_note"], "notes": d["notes"], "upd": d["last_updated_on"],
            "doc": v["documents_checked"] == "true", "impl": v["implementation_checked"] == "true",
            "links": [[l["role"], sidx[l["source_id"]]] for l in links[i] if l["source_id"] in sidx],
            "ev": [[e["field"], e["value"], sidx.get(e["source_id"], -1), e["locator"], e["checked_on"], e["checked_by"], e["status"], e["note"]]
                   for e in ev[i] if e["status"] in ("current", "conflicting", "provisional")],
            "ann": [[a["item"], a["name"], a["labels"], a["scale"], a["annotator"], a["label_basis"], a["label_verification"], a["unit"],
                     a["description"], sidx.get(a["source_id"], -1), a["locator"]] for a in anns[i]],
            "lc": [[c["item"], c["label"], c["n"], c["hours"], sidx.get(c["source_id"], -1)] for c in counts[i]],
            "iss": [[x["type"], x["description"], x["n"], sidx.get(x["source_id"], -1), x["locator"]] for x in issues[i]],
            "rel": [[r["relation"], r["other_dataset_id"], r["note"]] for r in rels[i]],
            "alias": [[a["alias"], a["alias_type"]] for a in aliases[i]],
        })
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True).stdout.strip()
    data = {"meta": {"commit": commit, "built": datetime.date.today().isoformat()}, "S": S, "D": D}
    page = (ROOT / "tools" / "site" / "template.html").read_text(encoding="utf-8")
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("�", "\\ufffd")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page.replace("__DATA__", blob), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB, {len(D)} datasets)")


if __name__ == "__main__":
    main()
