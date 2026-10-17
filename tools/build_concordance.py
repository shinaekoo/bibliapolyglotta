"""Build the Latin concordance (dictionary form -> places it occurs) from web/data/al*.json.

Output: web/data/cc0..3.json, each {lemma_id: [total, "packed refs"]}.
Each ref is 8 base-36 chars: book(2) chapter(2) row(2) word index(2).
Row: 0 = psalm title row, n = verse n, 900+n = Vulgate-only Daniel 3 verse n.
Very frequent words keep an evenly spread sample of CAP places.
"""
import json, os, sys
from collections import defaultdict
D = os.path.join(os.path.dirname(__file__), '..', 'web', 'data')
CAP, NSH = 300, 4
B36 = '0123456789abcdefghijklmnopqrstuvwxyz'
def b2(n):
    assert 0 <= n < 1296, n
    return B36[n // 36] + B36[n % 36]
occ = defaultdict(list)
for bi in range(66):
    al = json.load(open(os.path.join(D, f'al{bi:02d}.json')))
    for c, rows in sorted((al.get('lx') or {}).items(), key=lambda x: int(x[0])):
        def rk(a): return 0 if a == 't' else (900 + int(a[1:]) if a[0] == 'L' else int(a[1:]))
        for a, toks in sorted(rows.items(), key=lambda x: (rk(x[0]) if x[0][0] != 'L' else 23.5 + int(x[0][1:]) / 1000)):
            for i, t in enumerate(toks):
                occ[t[0]].append((bi, int(c), rk(a), i))
sh = [dict() for _ in range(NSH)]
tot = 0
for lid, lst in occ.items():
    n = len(lst)
    if n > CAP:
        lst = [lst[round(k * (n - 1) / (CAP - 1))] for k in range(CAP)]
    sh[lid % NSH][str(lid)] = [n, ''.join(b2(b) + b2(c) + b2(r) + b2(i) for b, c, r, i in lst)]
    tot += len(lst)
for s in range(NSH):
    json.dump(sh[s], open(os.path.join(D, f'cc{s}.json'), 'w'), separators=(',', ':'))
print('lemmas', len(occ), 'refs kept', tot, file=sys.stderr)
