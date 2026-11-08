"""Group each dataset's license_spdx into a license class for your own experiments.

Writes local/license_class.csv (dataset_id, license_spdx, license_class). The grouping is a
project decision, not a fact, so it lives here and not in the public DB. Edit MAP to suit.
Run from the repository root: python3 local/license_class.py
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = {
    "CC-BY-3.0": "open",
    "CC-BY-4.0": "open",
    "CC-BY-NC-4.0": "noncommercial",
    "CC-BY-NC-SA-4.0": "noncommercial",
    "CC-BY-NC-SA-3.0-DE": "noncommercial",
    "CC-BY-NC-ND-4.0": "noncommercial",
    "CC-BY-SA-4.0": "open",
    "CC0-1.0": "open",
    "ODbL-1.0": "open",
    "MIT": "open",
    "Apache-2.0": "open",
    "GPL-3.0-only": "open",
    "LicenseRef-custom-research-only": "research_only",
    "LicenseRef-proprietary-restricted": "restricted",
    "LicenseRef-other": "other",
    "none_stated": "none_stated",
    "conflicting": "conflicting",
    "unknown": "unknown",
    "CC-BY-NC-SA-2.0": "noncommercial",
    "CC-BY-3.0-US": "open",
    "CC-BY-NC-3.0": "noncommercial",
    "ODC-By-1.0": "open",
    "GPL-3.0-or-later": "open",
    "LicenseRef-citation-request": "open",
    "LicenseRef-golos-public": "open",
}


def main():
    with open(ROOT / "data" / "datasets.csv", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = ROOT / "local" / "license_class.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dataset_id", "license_spdx", "license_class"])
        for r in rows:
            spdx = r["license_spdx"]
            w.writerow([r["dataset_id"], spdx, MAP.get(spdx, "" if spdx == "" else "unmapped")])
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
