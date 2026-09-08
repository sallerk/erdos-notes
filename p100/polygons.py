"""delta for the regular-polygon families R_n, R_n plus centre, R_n minus a vertex, and for
the lattice sets found by lat.py, as explicit upper bounds for n = 10..13.  50 digits."""
import sys
import json
from itertools import combinations
import mpmath as mp
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
mp.mp.dps = 50


def dvals(pts, tol=mp.mpf('1e-40')):
    vals = []
    for P, Q in combinations(pts, 2):
        d = mp.sqrt((P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2)
        if not any(abs(d - v) < tol for v in vals):
            vals.append(d)
    return sorted(vals)


def delta(vals):
    gaps = [b - a for a, b in zip(vals, vals[1:])]
    return vals[-1] / min([vals[0]] + gaps)


def R(n, r=1, phase=0):
    return [(r * mp.cos(2 * mp.pi * i / n + phase), r * mp.sin(2 * mp.pi * i / n + phase)) for i in range(n)]


out = {}
for n in range(3, 15):
    fam = {'R%d' % n: R(n), 'R%d+centre' % n: R(n) + [(mp.mpf(0), mp.mpf(0))],
           'R%d-vertex' % n: R(n)[1:]}
    for name, pts in fam.items():
        v = dvals(pts)
        out[name] = dict(n=len(pts), k=len(v), delta=mp.nstr(delta(v), 20))
best = {}
for name, r in out.items():
    b = best.get(r['n'])
    if b is None or float(r['delta']) < float(b[1]):
        best[r['n']] = (name, r['delta'], r['k'])
for n in sorted(best):
    print('n=%2d : best polygon-family witness %-14s k=%d  delta = %s' % (n, best[n][0], best[n][2], best[n][1][:14]))
# lattice witnesses from lat.py, exact strings
for fn in ('lat_n11_k5', 'lat_n12_k5', 'lat_n13_k6'):
    try:
        d = json.load(open('results/%s.json' % fn))
        print('%s : %d similarity classes, min delta = %s  (%s)' % (fn, d['similarity_classes'],
              min(r['delta_num'] for r in d['sets'])[:14], min((r['delta'] for r in d['sets']), key=len)))
    except FileNotFoundError:
        pass
json.dump(out, open('results/polygons.json', 'w'), indent=1)
