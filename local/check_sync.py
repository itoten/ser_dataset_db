"""Check that the dataset_id lists in local/ match data/datasets.csv. Run: python3 local/check_sync.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbread

db = set(dbread.datasets())
bad = 0
for f in ["implementation/on_hold.csv"]:  # dataset_filtering checks its own configs when it runs
    ids = [r["dataset_id"] for r in dbread.rows(dbread.LOCAL / f)]
    extra = sorted(set(ids) - db)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    print(f, len(ids), "not in DB:", extra, "duplicated:", dup)
    bad += bool(extra or dup)
spdx = {r["license_spdx"] for r in dbread.datasets().values()} - {"", "conflicting"}
mapped = {r["license_spdx"] for r in dbread.rows(dbread.LOCAL / "license/class_map.csv")}
print("license values without a class:", sorted(spdx - mapped))
bad += bool(spdx - mapped)
sys.exit(bad)
