"""Check the database for format, type, key, evidence and egs3 consistency.

Usage: python3 tools/validate.py [--offline]

--offline skips every check that reads the espnet fork's git branch.
Exit status is 1 when any error is found; warnings do not fail the run.
"""

import datetime
import re
import sys

import csvio
import db as dbmod

SLUG = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
TOKENS = {"unknown", "NA", "none"}
# Lower number = stronger evidence.
RANK = {"user": 0, "measured": 1, "primary": 2, "project_doc": 3, "secondary": 4, "sheet": 5}

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def norm_name(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


# ---- 1. file format -------------------------------------------------------


def check_format(tables, cols):
    for path in sorted(csvio.SCHEMA_DIR.glob("*.csv")):
        check_file_bytes(path, None)
    for name, info in tables.items():
        path = info["path"]
        if not path.is_file():
            err(f"{name}: missing file {path}")
            continue
        try:
            header, rows = csvio.read_rows(path)
        except ValueError as e:
            err(f"{name}: {e}")
            continue
        want = [c["column"] for c in cols[name]]
        if header != want:
            err(f"{name}: header {header} does not match schema/columns.csv {want}")
        check_file_bytes(path, info["keys"], header, rows)
        for i, row in enumerate(rows, 2):
            for c, v in row.items():
                if v != v.strip() or "\n" in v or "\r" in v:
                    err(f"{name} line {i} column {c}: leading/trailing space or newline")


def check_file_bytes(path, keys, header=None, rows=None):
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        err(f"{path.name}: has a BOM")
    if b"\r" in raw:
        err(f"{path.name}: has CR characters")
    if header is None:
        header, rows = csvio.read_rows(path)
    if csvio.format_rows(header, rows, keys).encode("utf-8") != raw:
        err(f"{path.name}: not in canonical form (run tools/db.py fmt)")


# ---- 2. types -------------------------------------------------------------


def check_value(v, ctype, enums):
    """Return an error string or None for a non-null cell."""
    if ctype in ("text", "path"):
        return None
    if ctype == "slug":
        return None if SLUG.match(v) else "not a slug"
    if ctype == "url":
        return None if re.match(r"^https?://\S+$", v) else "not an http(s) URL"
    if ctype == "date":
        try:
            datetime.date.fromisoformat(v)
            return None if re.match(r"^\d{4}-\d{2}-\d{2}$", v) else "not YYYY-MM-DD"
        except ValueError:
            return "not a date"
    if ctype == "int":
        return None if re.match(r"^\d+$", v) else "not an integer"
    if ctype == "float":
        return None if re.match(r"^\d+(\.\d+)?$", v) else "not a number"
    if ctype == "bool":
        return None if v in ("true", "false") else "not true/false"
    if ctype in ("list", "isolist") or ctype.startswith("enumlist:"):
        items = v.split(";")
        if any(not it or it != it.strip() for it in items):
            return "empty or padded list item"
        if ctype == "isolist" and any(not re.match(r"^[a-z]{3}$", it) for it in items):
            return "not ISO 639-3 codes"
        if ctype.startswith("enumlist:"):
            allowed = enums[ctype.split(":", 1)[1]]
            bad = [it for it in items if it not in allowed]
            if bad:
                return f"not in enum {ctype.split(':', 1)[1]}: {bad}"
        return None
    if ctype.startswith("enum:"):
        name = ctype.split(":", 1)[1]
        return None if v in enums[name] else f"not in enum {name}"
    return f"unknown column type {ctype}"


def cell_error(v, ctype, nulls, enums):
    allowed = set(nulls.split(";")) if nulls != "-" else set()
    if v == "":
        return None if "empty" in allowed else "empty cell not allowed"
    if v in TOKENS and v in allowed:
        return None
    return check_value(v, ctype, enums)


def check_types(tables, cols, db, enums):
    for name in tables:
        for i, row in enumerate(db[name][1], 2):
            for c in cols[name]:
                msg = cell_error(row[c["column"]], c["type"], c["nulls"], enums)
                if msg:
                    err(f"{name} line {i} ({row[tables[name]['keys'][0]]}) {c['column']}={row[c['column']]!r}: {msg}")
    for i, row in enumerate(db["datasets"][1], 2):
        derived = enums["license_spdx"].get(row["license_spdx"], {}).get("derived", "")
        if row["license_class"] != derived:
            err(f"datasets {row['dataset_id']}: license_class {row['license_class']!r} != derived {derived!r}")


# ---- 3. keys, foreign keys, aliases ---------------------------------------


def check_keys(tables, db):
    for name, info in tables.items():
        seen = set()
        for row in db[name][1]:
            k = tuple(row[c] for c in info["keys"])
            if k in seen:
                err(f"{name}: duplicate key {k}")
            seen.add(k)
    ds = {r["dataset_id"] for r in db["datasets"][1]}
    recipes = {r["recipe"] for r in db["recipes"][1]}
    for r in db["evidence"][1]:
        if r["dataset_id"] not in ds:
            err(f"evidence {r['evidence_id']}: unknown dataset_id")
        m = re.match(r"^(.+)/([a-z_0-9]+)/(\d{2})$", r["evidence_id"])
        if not m or m.group(1) != r["dataset_id"] or m.group(2) != r["field"]:
            err(f"evidence {r['evidence_id']}: id does not match dataset_id/field/NN")
    for r in db["aliases"][1]:
        if r["dataset_id"] not in ds:
            err(f"aliases {r['alias']}: unknown dataset_id {r['dataset_id']}")
    for r in db["relations"][1]:
        for c in ("dataset_id", "other_dataset_id"):
            if r[c] not in ds:
                err(f"relations {r['dataset_id']}/{r['relation']}/{r['other_dataset_id']}: unknown {c}")
    for r in db["recipes"][1]:
        if r["dataset_id"] != "NA" and r["dataset_id"] not in ds:
            err(f"recipes {r['recipe']}: unknown dataset_id {r['dataset_id']}")
    for r in db["recipe_labels"][1]:
        if r["recipe"] not in recipes:
            err(f"recipe_labels {r['recipe']}/{r['label']}: unknown recipe")
    for r in db["benchmark_membership"][1]:
        for c in ("benchmark_recipe", "member_recipe"):
            if r[c] not in recipes:
                err(f"benchmark_membership: unknown recipe {r[c]} in {c}")
    owners = {}
    names = []
    for r in db["datasets"][1]:
        names += [(r["dataset_id"], r["dataset_id"]), (r["dataset_id"], r["name"])]
    names += [(r["dataset_id"], r["alias"]) for r in db["aliases"][1]]
    for d, n in names:
        owners.setdefault(norm_name(n), set()).add(d)
    for n, d in owners.items():
        if len(d) > 1:
            err(f"name {n!r} is shared by datasets {sorted(d)}; use relations distinct_from and distinct names")


# ---- 4. evidence ----------------------------------------------------------


def check_evidence(cols, db):
    ev_cols = {c["column"]: c["evidence"] for c in cols["datasets"] if c["evidence"] != "no"}
    ev = {}
    for r in db["evidence"][1]:
        ev.setdefault((r["dataset_id"], r["field"]), []).append(r)
        if r["field"] not in ev_cols:
            err(f"evidence {r['evidence_id']}: field {r['field']} does not take evidence")
        if r["field"].endswith("_measured") and r["source_type"] != "measured":
            err(f"evidence {r['evidence_id']}: *_measured fields need source_type measured")
        if r["field"].endswith("_reported") and r["source_type"] == "measured":
            err(f"evidence {r['evidence_id']}: *_reported fields cannot use measured")
        canon = r["is_canonical"] == "true"
        if canon and r["status"] == "superseded":
            err(f"evidence {r['evidence_id']}: canonical row cannot be superseded")
        if not canon and r["status"] == "current":
            err(f"evidence {r['evidence_id']}: non-canonical row must be superseded or conflicting")
    for row in db["datasets"][1]:
        d = row["dataset_id"]
        for field, kind in ev_cols.items():
            v = row[field]
            if kind == "status" and row["espnet_status"] == "implemented":
                needed = False
            else:
                needed = v not in ("", "NA")
            rows = ev.get((d, field), [])
            canon = [r for r in rows if r["is_canonical"] == "true"]
            if not needed:
                if rows and v == "":
                    err(f"evidence {d}/{field}: rows exist but the datasets cell is empty")
                continue
            if len(canon) != 1:
                err(f"evidence {d}/{field}: needs exactly one canonical row, found {len(canon)}")
                continue
            c = canon[0]
            if c["value"] != v:
                err(f"evidence {d}/{field}: canonical value {c['value']!r} != datasets value {v!r}")
            better = [r for r in rows if r is not c and RANK[r["source_type"]] < RANK[c["source_type"]]]
            if better and not c["note"]:
                err(f"evidence {d}/{field}: canonical row uses a weaker source than another row; note is required")
            if c["status"] == "conflicting" and not any(
                r is not c and r["status"] == "conflicting" for r in rows
            ):
                err(f"evidence {d}/{field}: canonical is conflicting but no other conflicting row exists")


# ---- 5/6. egs3 consistency ------------------------------------------------


def check_egs3(cols, db):
    import egs3

    branch = set(egs3.recipes())
    rec = {r["recipe"]: r for r in db["recipes"][1]}
    # An empty recipes.csv means the table has not been filled in yet.
    if rec and set(rec) != branch:
        err(f"recipes.csv and {egs3.BRANCH} differ: only in csv {sorted(set(rec) - branch)}, only in branch {sorted(branch - set(rec))}")
    ds = {r["dataset_id"]: r for r in db["datasets"][1]}
    implemented = {d for d, r in ds.items() if r["espnet_status"] == "implemented"}
    for d in sorted(implemented):
        if rec and d not in rec:
            err(f"datasets {d}: implemented but recipes.csv has no recipe {d}")
    for name, r in rec.items():
        if r["recipe_kind"] == "multi_corpus":
            if r["dataset_id"] != "NA":
                err(f"recipes {name}: multi_corpus recipe must have dataset_id NA")
        elif r["dataset_id"] not in implemented:
            err(f"recipes {name}: dataset_id {r['dataset_id']} is not an implemented dataset")
    for row in db["datasets"][1]:
        implemented_row = row["espnet_status"] == "implemented"
        if implemented_row != (row["status_reason_codes"] == "NA"):
            err(f"datasets {row['dataset_id']}: status_reason_codes must be NA exactly when implemented")
    for name in sorted(set(rec) & branch):
        want = egs3.derive(name)
        for col in egs3.SYNC_COLUMNS:
            if rec[name][col] != want[col]:
                err(f"recipes {name} {col}: csv {rec[name][col]!r} != egs3 {want[col]!r} (run tools/sync.py)")
    labels = {}
    for r in db["recipe_labels"][1]:
        if r["mapping_type"] != "dropped_by_recipe":
            labels.setdefault(r["recipe"], set()).add(r["label"])
    for name, r in rec.items():
        if name in labels and r["num_classes"] not in ("", "NA") and int(r["num_classes"]) != len(labels[name]):
            err(f"recipes {name}: num_classes {r['num_classes']} != {len(labels[name])} labels in recipe_labels")
        tl = r["token_list"]
        if name in labels and tl not in ("", "NA") and set(tl.split(";")) != labels[name]:
            err(f"recipes {name}: token_list differs from recipe_labels")


# ---- 9. paths --------------------------------------------------------------


def check_paths(cols, tables, db):
    for name in tables:
        for c in cols[name]:
            if c["type"] != "path":
                continue
            for row in db[name][1]:
                v = row[c["column"]]
                if v in ("", "NA", "unknown", "none"):
                    continue
                if c["column"] == "recipe_path":
                    continue
                base = csvio.ROOT.parent if c["column"] == "report_path" else csvio.ROOT
                if not (base / v).exists():
                    err(f"{name} {c['column']}={v}: path not found (relative to {base})")


def main(argv):
    offline = "--offline" in argv
    tables = csvio.tables()
    cols = csvio.columns()
    enums = csvio.enums()
    check_format(tables, cols)
    if errors:
        report()
    db = dbmod.load()
    check_types(tables, cols, db, enums)
    check_keys(tables, db)
    check_evidence(cols, db)
    check_paths(cols, tables, db)
    if not offline:
        check_egs3(cols, db)
    report()


def report():
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
