"""Is z3run.py's class-ordering constraint sound?

z3run.py adds  d_0 < d_1 < ... < d_{k-1}  to the coordinate encoding.  But the patterns it
is fed are CANONICAL forms, whose classes are numbered by ORDER OF FIRST APPEARANCE along
the edge list, which has nothing to do with the magnitudes of the distances.  If some
canonical pattern is realisable only with its class values in a different order, then the
ordering constraint turns a realisable pattern into `unsat`, and every unsat z3run.py has
ever emitted is suspect.

This settles it empirically at n=5, k=3, where the whole space is small: run z3 twice on
every canonical pattern, once WITH the ordering constraint and once with only pairwise
distinctness, and look for a pattern that is unsat with it and sat without.
"""
import sys, itertools, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3
from hdecide import pairs, enumerate_patterns, det4

N, K, TMO = 5, 3, 20


def build(pat, ordered):
    n, P = N, pairs(N)
    m = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(m)]
    s = z3.Solver()
    s.set('timeout', TMO * 1000)
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0, Y[2] >= 0)
    for c in range(m):
        s.add(D[c] > 0)
    if ordered:
        for c in range(m - 1):
            s.add(D[c] < D[c + 1])            # z3run.py's constraint
    else:
        for a, b in itertools.combinations(range(m), 2):
            s.add(D[a] != D[b])               # only distinctness, no order
    for idx, (i, j) in enumerate(P):
        s.add((X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2 == D[pat[idx]])
    for (i, j, l) in itertools.combinations(range(n), 3):
        s.add((X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0)
    for q in itertools.combinations(range(n), 4):
        s.add(det4([[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in q]) != 0)
    return s


pats = [p for p in enumerate_patterns(N, K) if max(p) == K - 1]
print('n=%d k=%d: %d canonical patterns using all %d classes' % (N, K, len(pats), K))
t0 = time.time()
bad = []
tally = {}
for p in pats:
    ra = str(build(p, True).check())
    rb = str(build(p, False).check())
    tally[(ra, rb)] = tally.get((ra, rb), 0) + 1
    if ra == 'unsat' and rb == 'sat':
        bad.append(list(p))
print('  %.1fs' % (time.time() - t0))
print()
print('  (ordered, unordered) verdict pairs:')
for kk, v in sorted(tally.items()):
    print('     %-22s %d' % (str(kk), v))
print()
if bad:
    print('  *** THE ORDERING CONSTRAINT IS UNSOUND ***')
    print('  %d canonical pattern(s) are unsat WITH it and sat WITHOUT it:' % len(bad))
    for b in bad[:5]:
        print('     %s' % b)
else:
    print('  No false unsat found at n=5, k=3.')
json.dump({'n': N, 'k': K, 'patterns': len(pats),
           'tally': {str(kk): v for kk, v in tally.items()},
           'false_unsats': bad}, open('ordertest_n5k3.json', 'w'), indent=1)
print('  written: ordertest_n5k3.json')
