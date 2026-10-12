"""One-time, mechanical import of the Google Sheet export into the database.

Reads sheet_import/2026-10-12_ser_database_SER_Datasets.csv and fills an empty
database. Every sheet value becomes a datasets cell plus an evidence row with
source_type `sheet`; nothing is corrected from outside knowledge. A sheet cell
that cannot be turned into a typed value mechanically is left empty and its
text is kept in a note column.
"""

import csv
import re
import sys

import csvio
import db as dbmod

SHEET = "sheet_import/2026-10-12_ser_database_SER_Datasets.csv"
DAY = "2026-10-12"
VIA = "tools/import_sheet.py"

# Sheet name -> egs3 recipe directory (the dataset_id of implemented datasets).
RECIPE = {
    "MSP-Podcast": "msppodcast", "Quechua-SER": "quechua", "MELD": "meld",
    "SUBESCO": "subesco", "Emozionalmente": "emozionalmente", "CREMA-D": "cremad",
    "IEMOCAP": "iemocap", "Thorsten-Emotional": "thorsten", "EMNS": "emns",
    "JL-Corpus": "jlcorpus", "eNTERFACE": "enterface05", "EMODB": "emodb",
    "TESS": "tess", "RAVDESS": "ravdess", "SAVEE": "savee", "Dusha": "dusha",
    "ESD": "esd", "PAVOQUE": "pavoque", "EmoV-DB": "emovdb", "ShEMO": "shemo",
    "nEMO": "nemo", "CaFE": "cafe", "EMOVO": "emovo", "RESD": "resd",
    "ASED": "ased", "TurEV-DB": "turevdb", "AESDD": "aesdd", "Oreau": "oreau",
    "ASVP-ESD": "asvpesd", "MESD": "mesd", "MESS": "mess", "URDU": "urdu",
    "VIVAE": "vivae", "Voice Statistics": "voicestats",
    # EmoBox's Polish source is the same MOST Wiedzy corpus as egs3/polishemo.
    "Polish (EmoBox)": "polishemo",
}
# Sheet names whose generic slug would be wrong or unclear.
ID_OVERRIDE = {
    "€motion": "emotion_origlia2010",
    "CH-SIMS v2.0": "chsims2",
    "Belfast Database": "belfast",
}

LICENSE = {
    "CC BY 4.0": "CC-BY-4.0", "CC BY-NC 4.0": "CC-BY-NC-4.0",
    "CC BY-NC-SA 4.0": "CC-BY-NC-SA-4.0", "CC BY-NC-SA 3.0 DE": "CC-BY-NC-SA-3.0-DE",
    "CC0 1.0": "CC0-1.0", "ODbL-1.0": "ODbL-1.0", "MIT": "MIT", "Apache-2.0": "Apache-2.0",
    "Custom academic/research-only": "LicenseRef-custom-research-only",
    "Proprietary/Restricted": "LicenseRef-proprietary-restricted",
    "Other": "LicenseRef-other", "Unknown": "unknown",
}
LANGUAGE = {
    "English": "eng", "Mandarin Chinese": "cmn", "Multilingual": "mul", "German": "deu",
    "Japanese": "jpn", "French": "fra", "Italian": "ita", "Russian": "rus",
    "Turkish": "tur", "Estonian": "est", "Polish": "pol", "Greek": "ell",
    "Amharic": "amh", "Danish": "dan", "Spanish": "spa", "Mexican Spanish": "spa",
    "Quechua": "que", "Persian": "fas", "Bangla": "ben", "Urdu": "urd", "Other": "unknown",
}
CONTEXT = {
    "Acted": "acted", "Spontaneous conversation": "spontaneous_conversation",
    "Affect elicitation": "affect_elicitation", "Multi-source web": "multi_source_web",
    "TV show": "tv_show", "YouTube": "youtube", "Movie/Film": "movie_film",
    "Podcast": "podcast", "Other": "other", "Read speech": "read_speech",
    "Synthetic": "synthetic", "Human-agent interaction": "human_agent_interaction",
    "Unknown": "unknown", "Child-robot interaction": "child_robot_interaction",
    "Talk show": "talk_show", "Non-speech vocalization": "non_speech_vocalization",
}


DERIVED = {v: r["derived"] for v, r in csvio.enums()["license_spdx"].items()}


def slug(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def label_list(text, min_items, token):
    """';'-joined list if the sheet text is a plain comma list, else None."""
    items = [t.strip() for t in text.split(",")]
    if len(items) >= min_items and all(re.fullmatch(token, t) for t in items):
        return ";".join(items)
    return None


def main():
    db = dbmod.load()
    if any(db[t][1] for t in ("datasets", "evidence", "aliases")):
        sys.exit("database is not empty; this import runs once")
    with open(csvio.ROOT / SHEET, newline="", encoding="utf-8") as f:
        sheet = [{k: v.strip() for k, v in r.items()} for r in csv.DictReader(f)]
    assert len(sheet) == 84, len(sheet)

    datasets, evidence, aliases = {}, [], []
    ids = set()

    def ev(d, field, value, line, column, note=""):
        n = sum(1 for e in evidence if e["dataset_id"] == d and e["field"] == field) + 1
        evidence.append({
            "evidence_id": f"{d}/{field}/{n:02d}", "dataset_id": d, "field": field,
            "value": value, "source_type": "sheet", "source_ref": SHEET,
            "locator": f"line {line}, column {column}", "via": VIA, "checked_on": DAY,
            "checked_by": "script", "is_canonical": "true", "status": "current", "note": note,
        })

    for i, r in enumerate(sheet):
        line = i + 2
        name = r["Dataset"]
        d = RECIPE.get(name) or ID_OVERRIDE.get(name) or slug(name)
        assert d not in ids, d
        ids.add(d)
        row = {c: "" for c in db["datasets"][0]}
        row.update(
            dataset_id=d, name=name, espnet_status="deferred",
            status_reason_codes="not_individually_checked",
            status_note="シート取り込み直後の仮の状態。egs3 との照合は未実施",
            status_checked_on=DAY, in_sheet="true", sheet_verified=r["Verified"],
            last_updated_on=DAY,
        )
        provisional = "シート取り込み直後の仮の状態"
        for field, value in (("espnet_status", "deferred"), ("status_reason_codes", "not_individually_checked")):
            evidence.append({
                "evidence_id": f"{d}/{field}/01", "dataset_id": d, "field": field, "value": value,
                "source_type": "project_doc", "source_ref": VIA, "locator": "", "via": VIA,
                "checked_on": DAY, "checked_by": "script", "is_canonical": "true",
                "status": "current", "note": provisional,
            })

        lang = r["Language"]
        if lang:
            row["languages"] = LANGUAGE[lang]
            ev(d, "languages", row["languages"], line, "Language", f"シート原文: {lang}")
            if lang == "Mexican Spanish":
                row["language_note"] = "シートの表記は Mexican Spanish"
        ctx = r["Source"]
        if ctx:
            row["recording_context"] = CONTEXT[ctx]
            ev(d, "recording_context", row["recording_context"], line, "Source", f"シート原文: {ctx}")
        lic = r["License"]
        if lic:
            row["license_spdx"] = LICENSE[lic]
            row["license_class"] = DERIVED[row["license_spdx"]]
            ev(d, "license_spdx", row["license_spdx"], line, "License", f"シート原文: {lic}")
        for sheet_col, field in (("Total Hours", "hours_reported"), ("Utterances", "n_utt_reported"), ("Speakers", "n_speakers_reported")):
            if r[sheet_col]:
                row[field] = r[sheet_col]
                ev(d, field, r[sheet_col], line, sheet_col)

        disc = r["Discrete Emotions"]
        if disc == "None":
            row["labels_discrete_reported"] = "none"
            ev(d, "labels_discrete_reported", "none", line, "Discrete Emotions", "シート原文: None")
        elif disc:
            lst = label_list(disc, 2, r"[a-z]+( [a-z]+)?")
            if lst:
                row["labels_discrete_reported"] = lst
                ev(d, "labels_discrete_reported", lst, line, "Discrete Emotions", f"シート原文: {disc}")
            else:
                row["labels_discrete_note"] = disc
        dim = r["Dimensional Emotions"]
        if dim == "None":
            row["dimensional_attributes"] = "none"
            ev(d, "dimensional_attributes", "none", line, "Dimensional Emotions", "シート原文: None")
        elif dim:
            lst = label_list(dim, 1, r"[a-z]+(/[a-z]+)?")
            if lst:
                row["dimensional_attributes"] = lst
                ev(d, "dimensional_attributes", lst, line, "Dimensional Emotions", f"シート原文: {dim}")
            else:
                row["dimensional_note"] = dim

        other = r["Other Annotations"]
        row["annotations_other"] = "none" if other == "None" else other
        row["sheet_notes"] = r["Notes"]
        row["source_url"] = r["Source URL"]
        row["paper_url"] = r["Paper URL"]
        datasets[d] = row
        aliases.append({
            "dataset_id": d, "alias": name, "alias_type": "sheet_name",
            "source_ref": SHEET, "note": f"line {line}",
        })

    db["datasets"] = (db["datasets"][0], list(datasets.values()))
    db["evidence"] = (db["evidence"][0], evidence)
    db["aliases"] = (db["aliases"][0], aliases)
    dbmod.save(db)
    print(len(datasets), "datasets,", len(evidence), "evidence rows")


if __name__ == "__main__":
    main()
