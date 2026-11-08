import json, re, sys, csv, os
sys.path.insert(0, 'local')
exec(open('local/verification_tools/p9_unknown.py').read().split('res = collections.defaultdict')[0])
r = json.load(open('local/verification_tools/p9_unknown.json'))
start, n = int(sys.argv[1]), int(sys.argv[2])
done = set(open('local/verification_tools/p9_hits_done.txt').read().split()) if os.path.exists('local/verification_tools/p9_hits_done.txt') else set()
items = [(d, f) for d, fs in r.items() for f, (k, m) in fs.items() if k == 'hit' and f"{d}:{f}" not in done]
for d, f in items[start:start + n]:
    srcs = [l['source_id'] for l in L if l['dataset_id'] == d and S[l['source_id']]['source_type'] == 'primary']
    out = []
    for s in dict.fromkeys(srcs):
        t = text(s)
        if len(t) < 1500: continue
        for m in re.finditer(PAT[f], t, re.I if f != 'languages' else 0):
            a = max(0, m.start() - 90); b = min(len(t), m.end() + 90)
            snip = t[a:b]
            if re.search(r'function\(|createElement|googletag|String [yn]|Object |dataLayer|\.insertBefore', snip) or (f in ('n_files_reported','hours_reported','n_speakers_reported') and not re.search(r'\d', m.group(0))): continue
            if all(snip[:60] not in o for _, o in out): out.append((s, snip))
            if len(out) >= 3: break
        if len(out) >= 3: break
    open("local/verification_tools/p9_hits_done.txt","a").write(f" {d}:{f}")
    print(f"## {d}:{f}")
    for s, sn in out: print(f"   [{s}] {sn}")
