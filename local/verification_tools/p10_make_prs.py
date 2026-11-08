"""P10: open pull requests (20 license_spdx rows each) for the maintainer to verify; first round: the datasets that have a recipe. Usage: p10_make_prs.py [max_prs]"""
import csv, subprocess, sys
sys.path.insert(0, "tools")
import csvio
ROOT = csvio.ROOT
DATE = "2026-11-03b"
def sh(*a, check=True): return subprocess.run(a, cwd=ROOT, capture_output=True, text=True, check=check)
maxn = int(sys.argv[1]) if len(sys.argv) > 1 else 99
assert sh("git", "branch", "--show-current").stdout.strip() == "main"
assert not sh("git", "status", "--porcelain", "--untracked-files=no").stdout.strip(), "working tree not clean"
h, ev = csvio.read_rows(ROOT / "data/evidence.csv"); _, src = csvio.read_rows(ROOT / "data/sources.csv")
sd = {s["source_id"]: s for s in src}
wide = {r["dataset_id"]: r for r in csv.DictReader(open(ROOT / "views/datasets_wide.csv"))}
OVERRIDE = {"emovo/license_spdx/02": "emovo_paper"}  # the row cites a copy bundled in the archive; the maintainer opens the paper online
def url_of(e): return sd.get(OVERRIDE.get(e["evidence_id"], e["source_id"]), {}).get("url", "")
rows = sorted((e for e in ev if wide[e["dataset_id"]]["implementation_checked"] == "true" and e["field"] == "license_spdx" and e["status"] in ("current", "conflicting") and e["checked_by"] != "user"
               and e["source_id"] and url_of(e)), key=lambda e: e["evidence_id"])
chunks = [rows[i:i + 20] for i in range(0, len(rows), 20)]
print(len(rows), "rows", len(chunks), "pull requests")
for n, chunk in enumerate(chunks[:maxn], 1):
    br = f"verify/{DATE}-{n:02d}"
    if sh("git", "ls-remote", "--heads", "origin", br).stdout.strip():
        print("exists", br); continue
    ids = {e["evidence_id"] for e in chunk}
    sh("git", "switch", "-c", br, "main")
    h, ev = csvio.read_rows(ROOT / "data/evidence.csv")
    for e in ev:
        if e["evidence_id"] in ids:
            if e["evidence_id"] in OVERRIDE: e["source_id"] = OVERRIDE[e["evidence_id"]]
            e["checked_by"] = "user"
            e["note"] = (e["note"] + "; " if e["note"] else "") + f"Verified by the maintainer in the pull request of branch {br}"
    csvio.write_rows(ROOT / "data/evidence.csv", h, ev, ["evidence_id"])
    sh("python3", "tools/views.py")
    sh("git", "add", "data/evidence.csv", "views/datasets_wide.csv")
    msg = (f"Mark {len(chunk)} license values as verified by the maintainer ({br})\n\nThe maintainer opens the link of each row, finds the quoted words and merges this "
           "pull request if every value matches the source. Merging records the check: the rows get checked_by=user.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    r = sh("git", "commit", "-q", "-m", msg, check=False)
    if r.returncode: print("commit failed", r.stdout[-300:], r.stderr[-300:]); sh("git", "switch", "main"); sh("git", "branch", "-D", br); break
    sh("git", "push", "-q", "-u", "origin", br)
    table = "| dataset | license | words in the source | source | state |\n|---|---|---|---|---|\n" + "\n".join(
        f"| `{e['dataset_id']}` | `{e['value']}` | {e['locator'].replace('|', '/')[:120]} | {url_of(e)} | {e['status']} |" for e in chunk)
    body = (f"Verification batch {n} of {len(chunks)}: {len(chunk)} values of `license_spdx`.\n\n"
            "**What to do**: open each link, find the quoted words and check that they give the license in the table. "
            "If all match, merge. If one does not, comment on that row; the rest can still be merged after it is fixed.\n\n"
            "Merging sets `checked_by=user` on these rows (the check of a person, not only of AI).\n\n" + table +
            "\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n")
    pr = sh("gh", "pr", "create", "--base", "main", "--head", br, "--title", f"Verify {len(chunk)} license values ({n}/{len(chunks)})", "--body", body)
    url = pr.stdout.strip().splitlines()[-1]; num = url.rsplit("/", 1)[1]
    h, ev = csvio.read_rows(ROOT / "data/evidence.csv")
    for e in ev:
        if e["evidence_id"] in ids: e["note"] = e["note"].replace(f"pull request of branch {br}", f"pull request #{num} (branch {br})")
    csvio.write_rows(ROOT / "data/evidence.csv", h, ev, ["evidence_id"])
    sh("python3", "tools/views.py")
    sh("git", "add", "data/evidence.csv", "views/datasets_wide.csv")
    sh("git", "commit", "-q", "-m", f"Add the pull request number #{num} to the verification notes\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    sh("git", "push", "-q")
    sh("git", "switch", "main")
    print("opened", url)
