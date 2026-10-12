"""Load, edit and re-save the database tables.

Usage:
  python3 tools/db.py fmt                       rewrite every table in canonical form
  python3 tools/db.py get TABLE KEY...          print one row (KEY parts follow the table's key columns)
  python3 tools/db.py set TABLE KEY... COL=VAL...   change cells of one existing row
  python3 tools/db.py add TABLE COL=VAL...      add a row

After any change, run tools/validate.py. Changing a value in `datasets` also
needs an evidence row (see README.md).
"""

import sys

import csvio


def load():
    """Return {table: (header, rows)} for every table in schema/tables.csv."""
    out = {}
    for name, info in csvio.tables().items():
        header, rows = csvio.read_rows(info["path"])
        out[name] = (header, rows)
    return out


def save(db):
    for name, info in csvio.tables().items():
        header, rows = db[name]
        csvio.write_rows(info["path"], header, rows, info["keys"])


def find(db, table, key):
    keys = csvio.tables()[table]["keys"]
    if len(key) != len(keys):
        sys.exit(f"{table} key needs {len(keys)} part(s): {keys}")
    for row in db[table][1]:
        if all(row[k] == v for k, v in zip(keys, key)):
            return row
    return None


def parse_assignments(items):
    out = {}
    for it in items:
        col, sep, val = it.partition("=")
        if not sep:
            sys.exit(f"expected COL=VAL, got {it!r}")
        out[col] = val
    return out


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    db = load()
    if cmd == "fmt":
        save(db)
    elif cmd in ("get", "set"):
        table = args[0]
        nkeys = len(csvio.tables()[table]["keys"])
        row = find(db, table, args[1 : 1 + nkeys])
        if row is None:
            sys.exit("no such row")
        if cmd == "get":
            for k, v in row.items():
                print(f"{k}: {v}")
        else:
            changes = parse_assignments(args[1 + nkeys :])
            bad = set(changes) - set(row)
            if bad:
                sys.exit(f"unknown column(s): {sorted(bad)}")
            row.update(changes)
            save(db)
    elif cmd == "add":
        table = args[0]
        header, rows = db[table]
        new = {c: "" for c in header}
        changes = parse_assignments(args[1:])
        bad = set(changes) - set(header)
        if bad:
            sys.exit(f"unknown column(s): {sorted(bad)}")
        new.update(changes)
        rows.append(new)
        save(db)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
