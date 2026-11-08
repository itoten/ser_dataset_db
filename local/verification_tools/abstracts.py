"""Fetch abstracts of paper sources with a DOI from OpenAlex into local/verification_tools/abstracts.json."""
import csv, json, os, urllib.request, concurrent.futures as cf
P = 'local/verification_tools/abstracts.json'
cache = json.load(open(P)) if os.path.exists(P) else {}
S = [s for s in csv.DictReader(open('data/sources.csv')) if s['doi'] and s['source_id'] not in cache]
def get(s):
    try:
        j = json.load(urllib.request.urlopen(urllib.request.Request('https://api.openalex.org/works/https://doi.org/' + s['doi'], headers={'User-Agent': 'ser-db-check (mailto:none@example.org)'}), timeout=30))
        inv = j.get('abstract_inverted_index') or {}
        words = sorted(((p, w) for w, ps in inv.items() for p in ps))
        return s['source_id'], ' '.join(w for _, w in words)
    except Exception as e:
        return s['source_id'], 'ERR ' + str(e)[:40]
with cf.ThreadPoolExecutor(4) as ex:
    for sid, a in ex.map(get, S): cache[sid] = a
json.dump(cache, open(P, 'w'))
print(len(cache), sum(1 for v in cache.values() if v and not v.startswith('ERR')))
