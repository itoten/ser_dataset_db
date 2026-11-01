"""Stage and save the DB changes for one dataset: evidence rows, cell values,
annotations, aliases and relations.

Import it from a short per-dataset script and run that script once with the system Python
(the one that runs tools/validate.py). Nothing is written until save(); save() rewrites the
CSVs through tools/db.py, which keeps the repository's sort order and formatting.

    import sys
    sys.path.insert(0, "<skill dir>/scripts")
    from reglib import Reg

    R = Reg("mydataset", today="2026-01-31")
    page = R.source("mydataset_page", "https://example.org/page", "distribution_page", "authors")
    R.link(page, "distribution")
    R.ev("license_spdx", "CC-BY-4.0", page, "license field")
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
import derive  # noqa: E402


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

    def _set_cell(self, field, value):
        """The datasets cell, or for a field like emotion_categories.label_basis the attribute of that label set."""
        if "." in field:
            item, attr = field.split(".", 1)
            self._set_row(item)[attr] = value
        else:
            self.row[field] = value

    def _set_row(self, item):
        for a in self.db["annotations"][1]:
            if a["dataset_id"] == self.D and a["item"] == item and a["name"] == item:
                return a
        raise SystemExit(f"no label set {item!r} for {self.D}: call label_set() first")

    def _rows(self, field):
        return [e for e in self.evr if e["dataset_id"] == self.D and e["field"] == field]

    def _next_id(self, field):
        n = max([int(e["evidence_id"].rsplit("/", 1)[1]) for e in self._rows(field)] or [0]) + 1
        return f"{self.D}/{field}/{n:02d}"

    def _append(self, eid, field, value, source_id, loc, by, note, status):
        e = {c: "" for c in self.evh}
        e.update(evidence_id=eid, dataset_id=self.D, field=field, value=value,
                 source_id=source_id, locator=loc, checked_on=self.today,
                 checked_by=by, status=status, note=note.strip())
        self.evr.append(e)

    def _supersede(self, field, nid, only_other_values=None):
        for o in self._rows(field):
            if o["status"] in ("current", "provisional") and (only_other_values is None or o["value"] != only_other_values):
                o.update(status="superseded", note=((o["note"] + "; ") if o["note"] else "") + f"superseded by {nid}")

    def source(self, source_id, url, kind, publisher, title="", doi="", describes_version="", note="",
               identity_basis="", archive_url=""):
        """Add a source to sources.csv (or return the existing one with the same url and publisher).

        publisher: authors (primary) / third_party (secondary) / recipe_author (implementation).
        Use kind mirror or survey for secondary sources, readme for the recipe readme.
        """
        stype = {"authors": "primary", "third_party": "secondary", "recipe_author": "implementation"}[publisher]
        sh, sr = self.db["sources"]
        for r in sr:
            if r["source_id"] == source_id:
                if url and r["url"] != url:
                    raise SystemExit(f"source: {source_id} exists with another url {r['url']!r}")
                return source_id
            if url and r["url"] == url and r["source_type"] == stype:
                return r["source_id"]
        sr.append({**{k: "" for k in sh}, "source_id": source_id, "url": url, "doi": doi, "title": title,
                   "kind": kind, "publisher": publisher, "source_type": stype,
                   "describes_version": describes_version, "identity_basis": identity_basis,
                   "checked_on": self.today, "archive_url": archive_url, "note": note})
        return source_id

    def link(self, source_id, role):
        """Say that this source introduces the dataset (role: paper / distribution / card / mirror / readme / other)."""
        lh, lr = self.db["dataset_sources"]
        if not any(r["dataset_id"] == self.D and r["source_id"] == source_id and r["role"] == role for r in lr):
            lr.append({"dataset_id": self.D, "source_id": source_id, "role": role})

    def _check_source(self, source_id):
        if not any(r["source_id"] == source_id for r in self.db["sources"][1]):
            raise SystemExit(f"no source {source_id!r}: add it with source() first")

    def ev(self, field, value, source_id, loc="", by="claude", note=""):
        """Add a current evidence row for `field` and set the cell to `value`.

        Current rows with another value and provisional rows are marked superseded (history is
        never deleted). Rows with the same value stay current. If the field is conflicting, use
        conflicting() or resolve() first.
        """
        self._check_source(source_id)
        if any(o["status"] == "conflicting" for o in self._rows(field)):
            raise SystemExit(f"ev: {field} is conflicting; call resolve({field!r}, why) first or add with conflicting()")
        nid = self._next_id(field)
        self._supersede(field, nid, only_other_values=value)
        for o in self._rows(field):
            if o["status"] == "provisional":
                o.update(status="superseded", note=((o["note"] + "; ") if o["note"] else "") + f"superseded by {nid}")
        self._append(nid, field, value, source_id, loc, by, note, "current")
        self._set_cell(field, value)

    def conflicting(self, field, value, source_id, loc="", by="claude", note=""):
        """Add a source that disagrees with the others. The cell becomes `conflicting`.

        Current rows with another value become conflicting too; provisional rows are superseded.
        """
        self._check_source(source_id)
        nid = self._next_id(field)
        for o in self._rows(field):
            if o["status"] == "provisional":
                o.update(status="superseded", note=((o["note"] + "; ") if o["note"] else "") + f"superseded by {nid}")
            elif o["status"] == "current" and o["value"] != value:
                o["status"] = "conflicting"
        self._append(nid, field, value, source_id, loc, by, note, "conflicting")
        self._set_cell(field, "conflicting")

    def resolve(self, field, why):
        """Mark every conflicting row of `field` superseded (the dispute was settled by a source)."""
        for o in self._rows(field):
            if o["status"] == "conflicting":
                o.update(status="superseded", note=((o["note"] + "; ") if o["note"] else "") + why)
        self._set_cell(field, "")

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

    def label_set(self, item, labels, source_id, loc="", scale="", perceived_from="", unit="utterance", note="", by="claude"):
        """A label set of the dataset: item is emotion_categories, emotion_attributes, speaking_style, sentiment or intent;
        labels in the source's own words (;-separated). Who made the labels and how are added with ev(item + '.annotator', ...),
        ev(item + '.label_basis', ...), ev(item + '.label_verification', ...)."""
        self._check_source(source_id)
        ah, ar = self.db["annotations"]
        ar.append({**{k: "" for k in ah}, "dataset_id": self.D, "item": item, "name": item, "labels": labels, "scale": scale,
                   "perceived_from": perceived_from, "unit": unit, "source_id": source_id, "locator": loc,
                   "checked_on": self.today, "checked_by": by, "note": note})

    def ann(self, rows, by="claude"):
        """Other annotations. rows: (item, name, description, annotator, unit, source_id, locator, note);
        item is from the fixed vocabulary (schema/enums.csv annotation_item), name is what the release calls it."""
        ah, ar = self.db["annotations"]
        for item, name, desc, annotator, unit, sid, loc, note in rows:
            self._check_source(sid)
            ar.append({**{k: "" for k in ah}, "dataset_id": self.D, "item": item, "name": name, "description": desc,
                       "annotator": annotator, "unit": unit, "source_id": sid, "locator": loc,
                       "checked_on": self.today, "checked_by": by, "note": note})

    def alias(self, alias, alias_type, source_id="", note=""):
        ah, ar = self.db["aliases"]
        ar.append({**{k: "" for k in ah}, "dataset_id": self.D, "alias": alias,
                   "alias_type": alias_type, "source_id": source_id, "note": note})

    def relation(self, relation, other_dataset_id, source_id="", note=""):
        rh, rr = self.db["relations"]
        rr.append({**{k: "" for k in rh}, "dataset_id": self.D, "relation": relation,
                   "other_dataset_id": other_dataset_id, "source_id": source_id, "note": note})

    def save(self):
        self.row.update({"last_updated_on": self.today})
        derive.apply(self.db)
        dbmod.save(self.db)
        print(f"saved {self.D}; now run tools/views.py and tools/validate.py")
