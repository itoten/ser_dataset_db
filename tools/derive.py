"""Fill the datasets columns that are derived from annotations (the main label set).

Usage: python3 tools/derive.py      (rewrite data/datasets.csv)
validate.py computes the same values and fails if the file differs.
"""

import csvio
import db as dbmod

LABEL_SETS = ("emotion_categories", "emotion_attributes", "speaking_style", "sentiment", "intent")
SET_ATTRS = ("annotator", "label_basis", "label_verification")
DERIVED = ["emotion_categories", "emotion_attributes", "main_label_set_type", "main_labels",
           "label_source", "label_basis", "label_verification"]


def label_sets(db):
    """{dataset_id: {item: annotations row}} for the rows that are label sets (name equals item)."""
    out = {}
    for a in db["annotations"][1]:
        if a["item"] in LABEL_SETS and a["name"] == a["item"]:
            out.setdefault(a["dataset_id"], {})[a["item"]] = a
    return out


def extra_sets(db):
    """{dataset_id: {name: annotations row}} for further label sets of an item: the name is '<basis>_<item>'
    (for example perceived_emotion_categories), used when a release has separate labels by another basis."""
    out = {}
    for a in db["annotations"][1]:
        if a["item"] in LABEL_SETS and a["name"] == f"{a['label_basis'].split(';')[0]}_{a['item']}" and a["label_basis"]:
            out.setdefault(a["dataset_id"], {})[a["name"]] = a
    return out


def main_set(sets):
    for item in LABEL_SETS:
        if item in sets:
            return sets[item]
    return None


def expected(db):
    """{dataset_id: {derived column: value}}."""
    sets = label_sets(db)
    out = {}
    for d in db["datasets"][1]:
        s = sets.get(d["dataset_id"], {})
        m = main_set(s)
        out[d["dataset_id"]] = {
            "emotion_categories": s["emotion_categories"]["labels"] if "emotion_categories" in s else "",
            "emotion_attributes": s["emotion_attributes"]["labels"] if "emotion_attributes" in s else "",
            "main_label_set_type": m["item"] if m else "",
            "main_labels": m["labels"] if m else "",
            "label_source": m["annotator"] if m else "",
            "label_basis": m["label_basis"] if m else "",
            "label_verification": m["label_verification"] if m else "",
        }
    return out


def apply(db):
    exp = expected(db)
    for d in db["datasets"][1]:
        d.update(exp[d["dataset_id"]])


def main():
    db = dbmod.load()
    apply(db)
    dbmod.save(db)
    print("derived columns written")


if __name__ == "__main__":
    main()
