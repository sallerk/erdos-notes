"""ITS UNSAT VERDICTS ARE NOT PROOFS -- use pz3_noorder.py instead.

This script adds  d_0 < d_1 < ... < d_{k-1}  to the encoding.  The patterns it is fed are
CANONICAL forms, whose classes are numbered by ORDER OF FIRST APPEARANCE along the edge
list; that has nothing to do with the magnitudes of the distances.  Canonicalisation
already quotients by colour renaming, so each orbit appears once, and constraining that one
representative to have its values in index order asks "is this pattern realisable with its
classes in this particular order", not "is it realisable".  A pattern realisable only with
some other ordering is reported unsat.

Its `sat` verdicts are fine (they come with a model).  Re-deciding all 70 of its unsats
without the ordering gave 46 unsat, 24 timeout, 0 sat, so no false unsat has actually been
exhibited -- but 24 verdicts turned out not to be proofs.  See ASSUMPTIONS.md A8.

The file is kept because the record of what was run should stay legible.
"""

"""Decide candidates with z3's coordinate encoding.  z3's nlsat is a decision procedure
for real closed fields, so BOTH its sat and unsat verdicts are sound; only 'unknown' is
uninformative.  Slower and more often unknown than the Gram method, but trustworthy.

Usage: python z3run.py <n> <k> <candfile> <outfile> [seconds] [workers]
"""
import sys, json, itertools, time
from multiprocessing import Pool
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3
from hdecide import pairs, det4

n, k = int(sys.argv[1]), int(sys.argv[2])
cf, of = sys.argv[3], sys.argv[4]
TMO = int(sys.argv[5]) if len(sys.argv) > 5 else 600
W = int(sys.argv[6]) if len(sys.argv) > 6 else 3


def solve(pat):
    P = pairs(n)
    m = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(m)]
    s = z3.Solver()
    s.set('timeout', TMO * 1000)
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0, Y[2] >= 0, D[0] > 0)
    for c in range(m - 1):
        s.add(D[c] < D[c + 1])
    for idx, (i, j) in enumerate(P):
        s.add((X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2 == D[pat[idx]])
    for (i, j, l) in itertools.combinations(range(n), 3):
        s.add((X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0)
    for q in itertools.combinations(range(n), 4):
        s.add(det4([[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in q]) != 0)
    r = s.check()
    if r == z3.sat:
        return pat, 'sat', str(s.model())
    return pat, ('unsat' if r == z3.unsat else 'unknown'), None


if __name__ == '__main__':
    cands = [tuple(p) for p in json.load(open(cf))['candidates']]
    print('z3 on %d candidates, n=%d k=%d, %ds cap, %d workers'
          % (len(cands), n, k, TMO, W))
    t0 = time.time()
    with Pool(W) as pool:
        res = pool.map(solve, cands)
    buck = {}
    for pat, r, mdl in res:
        buck.setdefault(r, []).append((list(pat), mdl))
    for r in sorted(buck):
        print('   %-9s %d' % (r, len(buck[r])))
    print('   %.1fs' % (time.time() - t0))
    json.dump({r: [x[0] for x in v] for r, v in buck.items()}, open(of, 'w'), indent=1)
    print('   written: %s' % of)
    if buck.get('sat'):
        print()
        print('   SAT: %s' % (buck['sat'][0][0],))
        print('   %s' % buck['sat'][0][1])
