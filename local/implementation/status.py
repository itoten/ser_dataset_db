"""Implementation status of every dataset: implemented / on_hold / not_investigated.

implemented: the DB has the dataset's recipe readme as a source (implementation_checked=true).
on_hold: listed in on_hold.csv (the dataset cannot be implemented: no audio, cannot be obtained, ...).
not_investigated: everything else.
Writes status.csv next to this file. Run: python3 local/implementation/status.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import dbread

HERE = Path(__file__).resolve().parent


def status():
    """dataset_id -> (status, reason_codes, note)."""
    hold = {r["dataset_id"]: r for r in dbread.rows(HERE / "on_hold.csv")}
    out = {}
    for d, r in dbread.datasets().items():
        if r["implementation_checked"] == "true":
            out[d] = ("implemented", "", "")
        elif d in hold:
            out[d] = ("on_hold", hold[d]["reason_codes"], hold[d]["note"])
        else:
            out[d] = ("not_investigated", "", "")
    return out


if __name__ == "__main__":
    s = status()
    dbread.write(HERE / "status.csv", ["dataset_id", "status", "reason_codes", "note"],
                 [{"dataset_id": d, "status": v[0], "reason_codes": v[1], "note": v[2]} for d, v in sorted(s.items())])
    from collections import Counter
    print(dict(Counter(v[0] for v in s.values())))
