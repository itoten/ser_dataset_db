"""License class of every dataset, from license_spdx in the DB.

The class of a license comes from class_map.csv (a project decision, edit it to suit).
When the DB says 'conflicting', the classes of the disagreeing statements are compared and the
strictest one (highest rank in classes.csv) is taken; none_stated/unknown statements are ignored
when another statement exists. An empty license_spdx gives an empty class (not checked yet).
Writes result.csv next to this file. Run: python3 local/license/classify.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import dbread

HERE = Path(__file__).resolve().parent


def classify():
    """dataset_id -> (class, how it was decided)."""
    rank = {r["class"]: int(r["rank"]) for r in dbread.rows(HERE / "classes.csv")}
    cmap = {r["license_spdx"]: r["class"] for r in dbread.rows(HERE / "class_map.csv")}
    conflicts = {}
    for e in dbread.evidence():
        if e["field"] == "license_spdx" and e["status"] == "conflicting":
            conflicts.setdefault(e["dataset_id"], []).append(e["value"])
    out = {}
    for d, r in dbread.datasets().items():
        v = r["license_spdx"]
        if not v:
            out[d] = ("", "license not checked in the DB")
        elif v == "conflicting":
            stated = [x for x in conflicts.get(d, []) if x not in ("none_stated", "unknown")] or conflicts.get(d, [])
            missing = [x for x in stated if x not in cmap]
            if missing:
                raise SystemExit(f"{d}: add {missing} to class_map.csv")
            cls = max((cmap[x] for x in stated), key=rank.get)
            out[d] = (cls, "conflicting: " + " vs ".join(sorted(set(stated))) + " -> strictest")
        elif v in cmap:
            out[d] = (cmap[v], "class_map")
        else:
            raise SystemExit(f"{d}: add {v} to class_map.csv")
    return out


if __name__ == "__main__":
    c = classify()
    w = dbread.datasets()
    dbread.write(HERE / "result.csv", ["dataset_id", "license_spdx", "class", "decided_by"],
                 [{"dataset_id": d, "license_spdx": w[d]["license_spdx"], "class": v[0], "decided_by": v[1]} for d, v in sorted(c.items())])
    print(dict(Counter(v[0] or "(not checked)" for v in c.values())))
