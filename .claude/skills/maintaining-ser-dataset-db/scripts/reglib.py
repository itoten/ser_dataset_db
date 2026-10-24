"""Stage and save the DB changes for one dataset: evidence rows, cell values, recipe rows,
recipe labels, annotations, aliases and relations.

Import it from a short per-dataset script and run that script once with the system Python
(the one that runs tools/validate.py). Nothing is written until save(); save() rewrites the
CSVs through tools/db.py, which keeps the repository's sort order and formatting.

    import sys
    sys.path.insert(0, "<skill dir>/scripts")
    from reglib import Reg

    R = Reg("mydataset", today="2026-01-31", report="reports/2026-01-31_mydataset_db_update.md")
    R.ev("espnet_status", "implemented", "measured", "data/recipes.csv", "recipe directory exists")
    R.set(status_note="...", status_checked_on=R.today)
    R.save()

See references/registration-example.md for a complete example.
"""

import json
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
import egs3  # noqa: E402
import sync  # noqa: E402


class Reg:
    """Changes for one dataset_id. `report` is stored in evidence.via and datasets.report_path.

    validate.py resolves report_path relative to the directory that contains the repository,
    so a report saved inside the repository is written as "<repo dir name>/reports/<file>.md".
    Pass report=None to keep report_path unchanged and record `via` as the repository itself.
    """

    def __init__(self, dataset_id, today, report=None):
        self.D = dataset_id
        self.today = today
        self.report = report
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
                 source_ref=ref, locator=loc, via=self.report or "", checked_on=self.today,
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
        """Cells that take no evidence row: status_note, notes, license_note, source_url, ..."""
        unknown = [c for c in cells if c not in self.row]
        if unknown:
            raise SystemExit(f"set: no such datasets column(s): {unknown}")
        self.row.update(cells)

    # recipe tables (implemented datasets only) --------------------------------------------

    def recipe(self, **manual_columns):
        """Add the recipes.csv row. Automatic columns come from the recipe branch and measurements/."""
        rh, rr = self.db["recipes"]
        if any(r["recipe"] == self.D for r in rr):
            raise SystemExit(f"recipe: recipes.csv already has {self.D!r}")
        if not (ROOT / "measurements" / f"{self.D}.json").is_file():
            raise SystemExit(f"recipe: measurements/{self.D}.json is missing; run tools/measure.py {self.D} first")
        r = {c: "" for c in rh}
        derived = egs3.derive(self.D)
        for c in ["recipe"] + egs3.SYNC_COLUMNS:
            r[c] = derived[c]
        r.update(sync.measured(self.D))
        bad = [c for c in manual_columns if c not in rh]
        if bad:
            raise SystemExit(f"recipe: no such recipes column(s): {bad}")
        r.update(dataset_id=self.D, **manual_columns)
        rr.append(r)

    def labels(self, spec, label_type="categorical"):
        """spec maps each recipe label to (source_labels, common7, mapping_type).

        Keys must be the recipe's labels as listed in measurements/<id>.json token_list
        (e.g. "fear"), not the corpus's own spelling (e.g. "fearful").
        """
        m = json.loads((ROOT / "measurements" / f"{self.D}.json").read_text(encoding="utf-8"))
        tokens = m["token_list"]
        missing = [t for t in tokens if t not in spec]
        extra = [t for t in spec if t not in tokens]
        if missing or extra:
            raise SystemExit(f"labels: token_list is {tokens}; missing {missing}, unknown {extra}")
        lh, lr = self.db["recipe_labels"]
        for t in tokens:
            c = [m["splits"][s]["labels"].get(t, 0) for s in ("train", "valid", "test")]
            src, c7, mt = spec[t]
            lr.append({**{k: "" for k in lh}, "recipe": self.D, "label": t, "source_labels": src,
                       "label_type": label_type, "common7": c7, "mapping_type": mt,
                       "n_train": str(c[0]), "n_valid": str(c[1]), "n_test": str(c[2]),
                       "n_test2": "NA", "n_total": str(sum(c))})

    # other tables -------------------------------------------------------------------------

    def ann(self, rows, by="claude"):
        """rows: (item, description, annotator, unit, used_in_recipe, source_type, source_ref, locator, note)."""
        ah, ar = self.db["annotations"]
        for item, desc, annotator, unit, used, st, ref, loc, note in rows:
            ar.append({**{k: "" for k in ah}, "dataset_id": self.D, "item": item, "description": desc,
                       "annotator": annotator, "unit": unit, "used_in_recipe": used, "source_type": st,
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
        updates = {"last_updated_on": self.today}
        if self.report:
            updates["report_path"] = self.report
        self.row.update(updates)
        dbmod.save(self.db)
        print(f"saved {self.D}; now run tools/views.py and tools/validate.py")
