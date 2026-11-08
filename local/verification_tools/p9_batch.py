"""Usage: from p9_batch import R; R(dataset, field, value, source_id, locator) ... ; then flush()."""
import sys; sys.path.insert(0, '.claude/skills/maintaining-ser-dataset-db/scripts')
from reglib import Reg
import collections, csv
_D = {d['dataset_id']: d for d in csv.DictReader(open('data/datasets.csv'))}
_q = collections.defaultdict(list)
def R(d, f, v, s, loc): _q[d].append((f, v, s, loc))
def flush(today='2026-11-02'):
    for d, items in _q.items():
        r = Reg(d, today)
        for f, v, s, loc in items:
            if _D[d].get(f, 'x') not in ('', 'unknown', 'none_stated'): print('skip (cell filled):', d, f); continue
            r.ev(f, v, s, loc)
        r.save()
    _q.clear()
