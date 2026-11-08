"""Open pull requests with rows the maintainer can only check in a browser (the source could not be opened by Claude). Usage: p11_make_prs.py [dry]"""
import csv, glob, re, subprocess, sys, os
sys.path.insert(0, "tools")
import csvio
ROOT = csvio.ROOT
DATE = "2026-11-03"
TAG = "2026-11-03b"
DRY = len(sys.argv) > 1 and sys.argv[1] == "dry"
def sh(*a, check=True): return subprocess.run(a, cwd=ROOT, capture_output=True, text=True, check=check)
exec(open(ROOT / "local/verification_tools/p9_unknown.py").read().split("res = collections.defaultdict")[0])  # S, L, D, text
sd = S
kur = {}
for f in glob.glob(str(ROOT / "local/scan_cache/*_raw.txt")):
    sid = os.path.basename(f)[:-8]; t = open(f).read()
    m = re.search(r"Paper:\*\*\s*\[[^\]]*\]\(([^)]+)\)", t)
    kur[sid] = m.group(1) if m else None
byurl = {s["url"]: s["source_id"] for s in sd.values() if s["url"]}
def unreadable(sid):
    t = text(sid)
    return len(t) < 1500 or bool(re.search(r"async-google-font|Client Challenge|not a bot|Checking your browser|githubassets\.com/assets/react", t))
rows = []
h, ev = csvio.read_rows(ROOT / "data/evidence.csv")
for e in ev:
    if e["field"] == "name": continue  # a catalogue's name field is the source of the name itself
    if e["status"] != "current" or not e["source_id"] or sd[e["source_id"]]["source_type"] != "secondary" or e["checked_by"] == "user": continue
    d = e["dataset_id"]; url = None; sid = None
    k = kur.get(e["source_id"])
    if k: url = k
    else:
        for l in L:
            if l["dataset_id"] == d and sd[l["source_id"]]["source_type"] == "primary" and sd[l["source_id"]]["url"] and unreadable(l["source_id"]):
                sid = l["source_id"]; url = sd[sid]["url"]; break
    if not url: continue
    if url in byurl: sid = byurl[url]
    rows.append((e, url, sid))
print(len(rows), "rows;", len({e["dataset_id"] for e, _, _ in rows}), "datasets")
if DRY: sys.exit()
# keep clear of the lines the license pull requests change
lic = set()
for b in sh("git", "branch", "-r", "--list", "origin/verify/*").stdout.split():
    d_ = sh("git", "diff", "origin/main..." + b.strip(), "--", "data/evidence.csv").stdout
    lic |= {l[1:].split(",", 1)[0] for l in d_.splitlines() if l.startswith("+") and not l.startswith("+++")}
rows.sort(key=lambda r: r[0]["evidence_id"])
_all = sorted(ev, key=lambda x: x["evidence_id"]); _p = {e["evidence_id"]: i for i, e in enumerate(_all)}
_lp = [_p[i] for i in lic if i in _p]
_n = len(rows); rows = [r for r in rows if all(abs(_p[r[0]["evidence_id"]] - q) >= 4 for q in _lp)]
print("dropped", _n - len(rows), "rows next to license pull request lines")
pos = {e["evidence_id"]: i for i, e in enumerate(sorted(ev, key=lambda x: x["evidence_id"]))}
dpos = {d: i for i, d in enumerate(sorted(D))}
chunks = []; cur = []
for r in rows:
    if cur and len(cur) >= 20:
        last = cur[-1][0]
        if pos[r[0]["evidence_id"]] - pos[last["evidence_id"]] >= 4 and abs(dpos[r[0]["dataset_id"]] - dpos[last["dataset_id"]]) >= 4:
            chunks.append(cur); cur = []
    cur.append(r)
if cur: chunks.append(cur)
print([len(c) for c in chunks])
assert sh("git", "branch", "--show-current").stdout.strip() == "main"
assert not sh("git", "status", "--porcelain", "--untracked-files=no").stdout.strip()
for n, chunk in enumerate(chunks, 1):
    br = f"verify-browser/{TAG}-{n:02d}"
    if sh("git", "ls-remote", "--heads", "origin", br).stdout.strip(): print("exists", br); continue
    sh("git", "switch", "-c", br, "main")
    h, ev = csvio.read_rows(ROOT / "data/evidence.csv"); sh_h, srcs = csvio.read_rows(ROOT / "data/sources.csv")
    sdd = {s["source_id"]: s for s in srcs}; nxt = {}
    ids = {e["evidence_id"]: (url, sid) for e, url, sid in chunk}
    new = []
    for e in ev:
        if e["evidence_id"] in ids:
            url, sid = ids[e["evidence_id"]]
            if not sid:
                sid = f"{e['dataset_id']}_paper_kural"
                if sid not in sdd:
                    srcs.append({**{k: "" for k in sh_h}, "source_id": sid, "url": url, "kind": "paper", "publisher": "authors", "source_type": "primary", "checked_on": DATE,
                                 "identity_basis": "Linked from the KuralHub entry of the dataset as its paper; the maintainer opened it and checked that it is about the dataset"}); sdd[sid] = srcs[-1]
                    lk = csvio.read_rows(ROOT / "data/dataset_sources.csv")
                    lk[1].append({"dataset_id": e["dataset_id"], "source_id": sid, "role": "paper"}); csvio.write_rows(ROOT / "data/dataset_sources.csv", lk[0], lk[1], ["dataset_id", "source_id", "role"])
            elif not sdd[sid]["publisher"]:
                sdd[sid]["publisher"] = "authors"; sdd[sid]["source_type"] = "primary"
                sdd[sid]["identity_basis"] = sdd[sid]["identity_basis"] or "The maintainer opened the page and checked that it is about the dataset"
            e["status"] = "superseded"; e["note"] = (e["note"] + " " if e["note"] else "") + f"Superseded by a row checked by the maintainer in the browser (branch {br})."
            used = [int(x["evidence_id"].rsplit("/", 1)[1]) for x in ev + new if x["dataset_id"] == e["dataset_id"] and x["field"] == e["field"]]
            num = max(used) + 1
            new.append({**{k: "" for k in h}, "evidence_id": f"{e['dataset_id']}/{e['field']}/{num:02d}", "dataset_id": e["dataset_id"], "field": e["field"], "value": e["value"], "source_id": sid,
                        "locator": f"the value of the KuralHub entry ({e['source_id']}); checked by the maintainer at this page", "checked_on": DATE, "checked_by": "user", "status": "current",
                        "note": f"Verified by the maintainer in the browser in the pull request of branch {br}"})
    ev += new
    csvio.write_rows(ROOT / "data/evidence.csv", h, ev, ["evidence_id"]); csvio.write_rows(ROOT / "data/sources.csv", sh_h, srcs, ["source_id"])
    sh("python3", "tools/views.py")
    r = sh("python3", "tools/validate.py", check=False)
    if "0 error" not in r.stdout: print("validate failed", r.stdout[-400:]); sh("git", "checkout", "."); sh("git", "switch", "main"); sh("git", "branch", "-D", br); break
    sh("python3", "tools/views.py"); sh("git", "add", "data/evidence.csv", "data/sources.csv", "data/dataset_sources.csv", "views/datasets_wide.csv")
    sh("git", "commit", "-q", "-m", f"Mark {len(chunk)} values as checked by the maintainer in the browser ({br})\n\nThe sources of these values could not be opened by Claude. The maintainer opens each link, finds the value and merges if it is stated there. Merging records the check: the rows cite that page with checked_by=user.\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    sh("git", "push", "-q", "-u", "origin", br)
    table = "| dataset | field | value | open this page | KuralHub / survey said |\n|---|---|---|---|---|\n" + "\n".join(
        f"| `{e['dataset_id']}` | `{e['field']}` | `{e['value']}` | {url} | {e['locator'].replace('|','/')[:80]} |" for e, url, _ in chunk)
    body = (f"Browser check {n} of {len(chunks)}: {len(chunk)} values whose source Claude could not open.\n\n"
            "**What to do**: open each page, check that it is the dataset's own paper or page and that it states the value. If all match, merge. "
            "If one does not, comment on that row; Claude fixes it in this pull request.\n\n"
            "Merging records a check by a person: the rows cite the opened page and get `checked_by=user`; the older row from the survey is marked superseded.\n\n" + table +
            "\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n")
    pr = sh("gh", "pr", "create", "--base", "main", "--head", br, "--title", f"Browser check: {len(chunk)} values ({n}/{len(chunks)})", "--body", body)
    url = pr.stdout.strip().splitlines()[-1]; num = url.rsplit("/", 1)[1]
    h, ev = csvio.read_rows(ROOT / "data/evidence.csv")
    for e in ev:
        if e["note"].endswith(f"pull request of branch {br}"): e["note"] = e["note"].replace(f"pull request of branch {br}", f"pull request #{num} (branch {br})")
    csvio.write_rows(ROOT / "data/evidence.csv", h, ev, ["evidence_id"]); sh("python3", "tools/views.py")
    sh("git", "add", "data/evidence.csv", "views/datasets_wide.csv"); sh("git", "commit", "-q", "-m", f"Add the pull request number #{num} to the browser-check notes\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n")
    sh("git", "push", "-q"); sh("git", "switch", "main"); print("opened", url)
