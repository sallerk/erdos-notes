"""ROUND-2 PROBE: validate lath.py's DFS + monotone prune by PRUNE-FREE enumeration.

The directory's claim that the prune was validated rests on an external C run with no
artifact here.  This enumerates every 5-subset of a WxW integer grid with no pruning at
all, in exact integer arithmetic, and reports the minimum number of distinct circumradii
over admissible subsets.  Compare with results/lath_n5_WxW_t*.json.
"""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, os, json, time
from math import gcd
from itertools import combinations
import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory

W = int(sys.argv[1]) if len(sys.argv) > 1 else 7
pts = [(x, y) for x in range(W) for y in range(W)]
N = len(pts)
t0 = time.time()

# ---- exact circumradius^2 id for every triple, 0 = collinear
tri_id = {}
vals = {}
nxt = 1
for a, b, c in combinations(range(N), 3):
    P, Q, R = pts[a], pts[b], pts[c]
    a2 = (Q[0]-R[0])**2 + (Q[1]-R[1])**2
    b2 = (R[0]-P[0])**2 + (R[1]-P[1])**2
    c2 = (P[0]-Q[0])**2 + (P[1]-Q[1])**2
    S = 2*(a2*b2 + b2*c2 + c2*a2) - (a2*a2 + b2*b2 + c2*c2)
    if S == 0:
        tri_id[(a, b, c)] = 0
        continue
    num = a2*b2*c2
    g = gcd(num, S)
    key = (num//g, S//g)
    if key not in vals:
        vals[key] = nxt; nxt += 1
    tri_id[(a, b, c)] = vals[key]
print('%dx%d: %d points, %d triples, %d distinct radii^2, %.1fs'
      % (W, W, N, len(tri_id), len(vals), time.time()-t0), flush=True)

# ---- concyclic quadruples
def det4(P, Q, R, T):
    def row(X): return (X[0]*X[0]+X[1]*X[1], X[0], X[1])
    r = [row(P), row(Q), row(R), row(T)]
    def d3(a, b, c):
        return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0]))
    return (-d3(r[1], r[2], r[3]) + d3(r[0], r[2], r[3])
            - d3(r[0], r[1], r[3]) + d3(r[0], r[1], r[2]))

conc = set()
for q in combinations(range(N), 4):
    if det4(*[pts[i] for i in q]) == 0:
        conc.add(q)
print('%d concyclic quadruples, %.1fs' % (len(conc), time.time()-t0), flush=True)

best = 99; bestset = None; nadm = 0; total = 0
for s in combinations(range(N), 5):
    total += 1
    ok = True
    for q in combinations(s, 4):
        if q in conc:
            ok = False; break
    if not ok:
        continue
    ids = []
    for t in combinations(s, 3):
        v = tri_id[t]
        if v == 0:
            ok = False; break
        ids.append(v)
    if not ok:
        continue
    nadm += 1
    d = len(set(ids))
    if d < best:
        best = d; bestset = [pts[i] for i in s]
        print('   new best %d : %s  (%.1fs)' % (d, bestset, time.time()-t0), flush=True)
print('PRUNE-FREE %dx%d n=5 : %d subsets, %d admissible, MIN distinct circumradii = %d'
      % (W, W, total, nadm, best), flush=True)
print('   witness %s   %.1fs' % (bestset, time.time()-t0), flush=True)
fn = 'results/lath_n5_%dx%d_t6.json' % (W, W)
if os.path.exists(fn):
    d = json.load(open(fn))
    print('   lath.py artifact says best=%s witness=%s  -> %s'
          % (d['best'], d['witness'], 'AGREES' if d['best'] == best else 'DISAGREES'))
