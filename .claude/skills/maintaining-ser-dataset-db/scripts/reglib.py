"""Stage and save the DB changes for one dataset: evidence rows, cell values,
annotations, aliases and relations.

Import it from a short per-dataset script and run that script once with the system Python
(the one that runs tools/validate.py). Nothing is written until save(); save() rewrites the
CSVs through tools/db.py, which keeps the repository's sort order and formatting.

    import sys
    sys.path.insert(0, "<skill dir>/scripts")
    from reglib import Reg

    R = Reg("mydataset", today="2026-01-31")
    R.ev("license_spdx", "CC-BY-4.0", "primary", "https://example.org/page", "license field")
    R.set(notes="...")
    R.save()

See references/registration-example.md for a complete example.
"""

import sys
from pathlib import Path


def _find_root():
    """The DB repository root: the nearest parent that holds tools/validate.py."""
    for p in Path(__file__).resolve().parents:
        if (p / "tools" / "validate.py").is_file() and (p / "data" / "datasets.csv").is_file():
            return p
    raise SystemExit("reglib: could not find the DB root (a parent with tools/validate.py and data/datasets.csv)")


ROOT = _find_root()
sys.path.insert(0, str(ROOT / "tools"))
import db as dbmod  # noqa: E402


class Reg:
    """Changes for one dataset_id."""

    def __init__(self, dataset_id, today):
        self.D = dataset_id
        self.today = today
        self.db = dbmod.load()
        self.evh, self.evr = self.db["evidence"]
        self.row = dbmod.find(self.db, "datasets", (dataset_id,))
        if self.row is None:
            raise SystemExit(f"{dataset_id!r} is not in data/datasets.csv. Add the row first: "
                             f"python3 tools/db.py add datasets dataset_id={dataset_id} ...")

    # evidence -----------------------------------------------------------------------------

    def _rows(self, field):
        return [e for e in self.evr if e["dataset_id"] == self.D and e["field"] == field]

    def _next_id(self, field):
        n = max([int(e["evidence_id"].rsplit("/", 1)[1]) for e in self._rows(field)] or [0]) + 1
        return f"{self.D}/{field}/{n:02d}"

    def _append(self, eid, field, value, stype, ref, loc, by, note, canonical, status):
        e = {c: "" for c in self.evh}
        e.update(evidence_id=eid, dataset_id=self.D, field=field, value=value, source_type=stype,
                 source_ref=ref, locator=loc, checked_on=self.today,
                 checked_by=by, is_canonical=canonical, status=status, note=note.strip())
        self.evr.append(e)

    def ev(self, field, value, stype, ref, loc="", by="claude", note=""):
        """Add the new canonical evidence row for `field` and set the cell to `value`.

        The previous canonical row is kept and marked superseded (history is never deleted).
        """
        nid = self._next_id(field)
        for o in self._rows(field):
            if o["is_canonical"] == "true":
                o.update(is_canonical="false", status="superseded",
                         note=((o["note"] + "; ") if o["note"] else "") + f"superseded by {nid}")
        self._append(nid, field, value, stype, ref, loc, by, note, "true", "current")
        self.row[field] = value

    def conflicting(self, field, value, stype, ref, loc="", by="claude", note=""):
        """Keep a source that disagrees with the canonical value, as a non-canonical row."""
        self._append(self._next_id(field), field, value, stype, ref, loc, by, note, "false", "conflicting")

    def note_on(self, evidence_id, text):
        """Append to the note of an existing evidence row, e.g. 'independently re-measured, matches'."""
        for e in self.evr:
            if e["evidence_id"] == evidence_id:
                e["note"] = (((e["note"] + "; ") if e["note"] else "") + text).strip()
                return
        raise SystemExit(f"note_on: no evidence row {evidence_id!r}")

    # cells without evidence ---------------------------------------------------------------

    def set(self, **cells):
        """Cells that take no evidence row: notes, license_note, language_note, ..."""
        unknown = [c for c in cells if c not in self.row]
        if unknown:
            raise SystemExit(f"set: no such datasets column(s): {unknown}")
        self.row.update(cells)

    # other tables -------------------------------------------------------------------------

    def ann(self, rows, by="claude"):
        """rows: (item, description, annotator, unit, source_type, source_ref, locator, note)."""
        ah, ar = self.db["annotations"]
        for item, desc, annotator, unit, st, ref, loc, note in rows:
            ar.append({**{k: "" for k in ah}, "dataset_id": self.D, "item": item, "description": desc,
                       "annotator": annotator, "unit": unit, "source_type": st,
                       "source_ref": ref, "locator": loc, "checked_on": self.today, "checked_by": by,
                       "note": note})

    def alias(self, alias, alias_type, source_ref, note=""):
        ah, ar = self.db["aliases"]
        ar.append({**{k: "" for k in ah}, "dataset_id": self.D, "alias": alias,
                   "alias_type": alias_type, "source_ref": source_ref, "note": note})

    def relation(self, relation, other_dataset_id, source_ref, note=""):
        rh, rr = self.db["relations"]
        rr.append({**{k: "" for k in rh}, "dataset_id": self.D, "relation": relation,
                   "other_dataset_id": other_dataset_id, "source_ref": source_ref, "note": note})

    def save(self):
        self.row.update({"last_updated_on": self.today})
        dbmod.save(self.db)
        print(f"saved {self.D}; now run tools/views.py and tools/validate.py")
