"""Check the database for format, type, key and evidence consistency.

Usage: python3 tools/validate.py

Exit status is 1 when any error is found; warnings do not fail the run.
"""

import datetime
import re
import subprocess
import sys
import unicodedata

import csvio
import db as dbmod
import derive
import views

SLUG = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")
TOKENS = {"unknown", "NA", "none", "conflicting"}

errors = []
warnings = []
warn_untyped = set()


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def norm_name(s):
    # Accents are dropped (Oréau == Oreau), but letters of any script are kept.
    s = unicodedata.normalize("NFKD", s.casefold())
    return re.sub(r"[\W_]", "", "".join(c for c in s if not unicodedata.combining(c)))


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
    for r in db["evidence"][1]:
        if r["dataset_id"] not in ds:
            err(f"evidence {r['evidence_id']}: unknown dataset_id")
        m = re.match(r"^(.+)/([a-z_0-9.]+)/(\d{2})$", r["evidence_id"])
        if not m or m.group(1) != r["dataset_id"] or m.group(2) != r["field"]:
            err(f"evidence {r['evidence_id']}: id does not match dataset_id/field/NN")
    for r in db["aliases"][1]:
        if r["dataset_id"] not in ds:
            err(f"aliases {r['alias']}: unknown dataset_id {r['dataset_id']}")
    for r in db["annotations"][1]:
        if r["dataset_id"] not in ds:
            err(f"annotations {r['dataset_id']}/{r['item']}: unknown dataset_id")
    for r in db["datasets"][1]:
        if r["label_verification"] and not r["label_source"]:
            err(f"datasets {r['dataset_id']}: label_verification is set but label_source is empty")
    for r in db["relations"][1]:
        for c in ("dataset_id", "other_dataset_id"):
            if r[c] not in ds:
                err(f"relations {r['dataset_id']}/{r['relation']}/{r['other_dataset_id']}: unknown {c}")
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


LIVE = ("current", "conflicting", "provisional")


def set_targets(db):
    """(dataset_id, evidence field, cell value) for the attributes of label sets in annotations."""
    out = []
    for ds_id, sets in derive.label_sets(db).items():
        for item, row in sets.items():
            if item not in ("emotion_categories", "emotion_attributes"):
                continue
            for attr in derive.SET_ATTRS:
                out.append((ds_id, f"{item}.{attr}", row[attr]))
    for ds_id, sets in derive.extra_sets(db).items():
        for name, row in sets.items():
            if row["item"] not in ("emotion_categories", "emotion_attributes"):
                continue
            for attr in derive.SET_ATTRS:
                out.append((ds_id, f"{name}.{attr}", row[attr]))
    return out


def check_traceability(db):
    """Every dataset has a source with a URL, and every source an evidence row cites is linked to its dataset."""
    srcs = {r["source_id"]: r for r in db["sources"][1]}
    linked = {}
    for r in db["dataset_sources"][1]:
        linked.setdefault(r["dataset_id"], set()).add(r["source_id"])
    for d in db["datasets"][1]:
        if not any(srcs.get(s, {}).get("url") for s in linked.get(d["dataset_id"], ())):
            err(f"datasets {d['dataset_id']}: no linked source with a URL; a dataset nobody can trace to a document does not belong in the DB")
    for e in db["evidence"][1]:
        if e["source_id"] and e["status"] in ("current", "conflicting") and e["source_id"] not in linked.get(e["dataset_id"], ()):
            err(f"evidence {e['evidence_id']}: source {e['source_id']} is not linked to the dataset in dataset_sources.csv")


def check_human_checks(db):
    """A person's check is recorded only through a merged verification pull request."""
    for r in db["evidence"][1]:
        if r["checked_by"] == "user" and not re.search(r"pull request (#\d+|of branch)", r["note"]):
            err(f"evidence {r['evidence_id']}: checked_by=user needs a note 'Verified by the maintainer ... in pull request #<number>'")


def check_evidence(cols, db):
    ev_cols = {c["column"] for c in cols["datasets"] if c["evidence"] != "no"}
    targets = [(d["dataset_id"], f, d[f]) for d in db["datasets"][1] for f in sorted(ev_cols)] + set_targets(db)
    set_fields = {(d, f) for d, f, _ in set_targets(db)}
    sources = {r["source_id"]: r for r in db["sources"][1]}
    ev = {}
    for r in db["evidence"][1]:
        ev.setdefault((r["dataset_id"], r["field"]), []).append(r)
        eid, st = r["evidence_id"], r["status"]
        if r["field"] not in ev_cols and (r["dataset_id"], r["field"]) not in set_fields:
            err(f"evidence {eid}: field {r['field']} does not take evidence")
        if r["source_id"] and r["source_id"] not in sources:
            err(f"evidence {eid}: unknown source_id {r['source_id']}")
        ty = sources.get(r["source_id"], {}).get("source_type", "")
        if st in ("current", "conflicting"):
            if not r["source_id"]:
                err(f"evidence {eid}: a {st} row needs a source")
            elif not ty:
                warn_untyped.add(r["source_id"])
            if r["field"].endswith("_release") and ty not in ("implementation", ""):
                err(f"evidence {eid}: *_release fields need a source of type implementation")
            if r["field"].endswith("_reported") and ty == "implementation":
                err(f"evidence {eid}: *_reported fields cannot use an implementation source")
        if st == "provisional":
            if r["source_id"] or r["locator"]:
                err(f"evidence {eid}: a provisional row has no source (source_id and locator must be empty)")
            if not r["note"].startswith("Provisional:"):
                err(f"evidence {eid}: the note of a provisional row starts with 'Provisional:'")
    if True:
        for d, field, v in targets:
            rows = [r for r in ev.get((d, field), []) if r["status"] in LIVE]
            needed = v not in ("", "NA")
            if not needed:
                if rows and v == "":
                    err(f"evidence {d}/{field}: live rows exist but the datasets cell is empty")
                continue
            cur = [r for r in rows if r["status"] == "current"]
            con = [r for r in rows if r["status"] == "conflicting"]
            pro = [r for r in rows if r["status"] == "provisional"]
            if not rows:
                err(f"evidence {d}/{field}: no current, conflicting or provisional row for {v!r}")
            elif con:
                if cur:
                    err(f"evidence {d}/{field}: current and conflicting rows together")
                if len({r["value"] for r in con}) < 2:
                    err(f"evidence {d}/{field}: conflicting rows need at least two different values")
                if v != "conflicting":
                    err(f"evidence {d}/{field}: conflicting rows but the datasets cell is {v!r}")
            elif cur:
                vals = {r["value"] for r in cur}
                if len(vals) > 1:
                    err(f"evidence {d}/{field}: current rows disagree {sorted(vals)}; make them conflicting or supersede one")
                if pro:
                    err(f"evidence {d}/{field}: a provisional row next to current rows; supersede it")
                if v not in vals:
                    err(f"evidence {d}/{field}: current value {sorted(vals)} != datasets value {v!r}")
            else:
                if len(pro) != 1:
                    err(f"evidence {d}/{field}: needs exactly one provisional row, found {len(pro)}")
                elif pro[0]["value"] != v:
                    err(f"evidence {d}/{field}: provisional value {pro[0]['value']!r} != datasets value {v!r}")


def check_derived(db):
    exp = derive.expected(db)
    for d in db["datasets"][1]:
        for c, want in exp[d["dataset_id"]].items():
            if d[c] != want:
                err(f"datasets {d['dataset_id']} {c}: {d[c]!r} != {want!r} derived from annotations (run tools/derive.py)")


NOTE_COLS = ("notes", "license_note", "language_note", "source_rights_note")


def check_note_tags(db):
    ids = {r["source_id"] for r in db["sources"][1]}
    for d in db["datasets"][1]:
        for c in NOTE_COLS:
            for sent in re.split(r"(?<=[.;])\s+(?=[A-Z0-9])", d[c]):
                if not sent:
                    continue
                tags = re.findall(r"\[([a-z0-9_]+)\]", sent)
                if not tags:
                    err(f"datasets {d['dataset_id']} {c}: sentence without a [source_id] tag: {sent[:50]!r}")
                for t in tags:
                    if t not in ids:
                        err(f"datasets {d['dataset_id']} {c}: tag [{t}] is not a source")


def check_sources(db):
    sources = {}
    seen = {}
    for r in db["sources"][1]:
        sid = r["source_id"]
        sources[sid] = r
        t, p, k = r["source_type"], r["publisher"], r["kind"]
        if r["url"]:
            key = (r["url"], t)
            if key in seen:
                err(f"sources {sid}: same url and source_type as {seen[key]}")
            seen[key] = sid
        if r["doi"]:
            key = ("doi", r["doi"], t)
            if key in seen:
                err(f"sources {sid}: same DOI and source_type as {seen[key]}")
            seen[key] = sid
        want = {"primary": "authors", "secondary": "third_party", "implementation": "recipe_author"}.get(t)
        if t and p != want:
            err(f"sources {sid}: source_type {t} needs publisher {want}, not {p!r}")
        if t == "implementation" and k != "readme":
            err(f"sources {sid}: an implementation source is a readme")
        if k == "mirror" and t != "secondary":
            err(f"sources {sid}: a mirror is a secondary source")
        if (t == "") != (p == ""):
            err(f"sources {sid}: source_type and publisher are both set or both empty")
    unknown = sum(1 for r in sources.values() if not r["source_type"])
    if unknown:
        warn(f"{unknown} sources have no publisher and source_type yet (origin not checked)")
    ds = {r["dataset_id"] for r in db["datasets"][1]}
    for r in db["dataset_sources"][1]:
        if r["dataset_id"] not in ds:
            err(f"dataset_sources {r['dataset_id']}/{r['source_id']}: unknown dataset_id")
        if r["source_id"] not in sources:
            err(f"dataset_sources {r['dataset_id']}/{r['source_id']}: unknown source_id")
    for name, key in (("annotations", "item"), ("aliases", "alias"), ("relations", "relation")):
        for r in db[name][1]:
            if r["source_id"] and r["source_id"] not in sources:
                err(f"{name} {r['dataset_id']}/{r[key]}: unknown source_id {r['source_id']}")
    for r in db["annotations"][1]:
        if not r["source_id"] and not r["note"].startswith("Provisional:"):
            err(f"annotations {r['dataset_id']}/{r['item']}: no source_id; a row without a source has a note starting with 'Provisional:'")
    sets = derive.label_sets(db)
    for r in db["issues"][1]:
        if r["source_id"] not in sources:
            err(f"issues {r['dataset_id']}/{r['issue_no']}: unknown source_id {r['source_id']}")
    for r in db["label_counts"][1]:
        if r["source_id"] not in sources:
            err(f"label_counts {r['dataset_id']}/{r['label']}: unknown source_id {r['source_id']}")
        if r["item"] not in sets.get(r["dataset_id"], {}):
            err(f"label_counts {r['dataset_id']}/{r['item']}/{r['label']}: the dataset has no label set {r['item']} in annotations")
    if warn_untyped:
        warn(f"{len(warn_untyped)} sources used by current evidence have no publisher and source_type")


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
                if not (csvio.ROOT / v).exists():
                    err(f"{name} {c['column']}={v}: path not found (relative to {csvio.ROOT})")


LOCAL_PATH = re.compile(r"(?<![\w.])(/home/\w+/|/Users/\w+/|/mnt/\w+|[~]/|[A-Za-z]:\\Users\\)")


def check_no_local_paths():
    """The repository is public: tracked files must not hold machine-specific paths."""
    files = subprocess.run(["git", "-C", str(csvio.ROOT), "ls-files"], capture_output=True,
                           text=True, check=True).stdout.split()
    for name in files:
        try:
            text = (csvio.ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            m = LOCAL_PATH.search(line)
            if m:
                err(f"{name}:{i}: machine-specific path {m.group(0)!r} (use an environment variable name or a relative path)")


def check_views(db):
    for path, text in views.build(db).items():
        f = csvio.ROOT / path
        if not f.exists() or f.read_bytes().decode("utf-8") != text:
            err(f"{path} is out of date: run python3 tools/views.py")


def main(argv):
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
    check_sources(db)
    check_derived(db)
    check_human_checks(db)
    check_traceability(db)
    check_note_tags(db)
    check_paths(cols, tables, db)
    check_views(db)
    check_no_local_paths()
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
