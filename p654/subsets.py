"""Free upper bounds for #654 by deleting points from the verified #98 witnesses.

MONOTONICITY.  Deleting a point from X can only remove distances from a surviving point,
so d_{X'}(x) <= d_X(x) for every x in X', hence M(X') <= M(X).  Therefore f is
NON-DECREASING, and every m-subset of a verified witness is itself a legal configuration
(general position is inherited) giving an upper bound at size m.

So: take every subset of every witness and record the best M at each size.
"""
import sys, itertools, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp
from pinned import WIT, a2, sq, uniq, analyse

print('=' * 78)
print('UPPER BOUNDS BY DELETION from the verified #98 witnesses')
print('=' * 78)

best = {}          # n -> (M, source, index tuple)
for key in [4, '4c', 5, 6, 7, 8]:
    P = WIT[key][0]
    N = len(P)
    # exact pairwise squared distances once, then reuse
    dsq = {}
    for i, j in itertools.combinations(range(N), 2):
        v = sp.expand(sq(P[i], P[j]))
        dsq[(i, j)] = dsq[(j, i)] = v
    for m in range(3, N + 1):
        for S in itertools.combinations(range(N), m):
            pin = [len(uniq([dsq[(i, j)] for j in S if j != i])) for i in S]
            M = max(pin)
            if m not in best or M < best[m][0]:
                best[m] = (M, str(key), S)

print()
print('  n   ceil((n-1)/3)   best M found   witness   subset')
print('  ' + '-' * 68)
for m in sorted(best):
    lo = -(-(m - 1) // 3)
    M, src, S = best[m]
    print('  %-3d %-15d %-14d %-9s %s%s'
          % (m, lo, M, src, S, '   <-- MATCHES THE BOUND' if M == lo else ''))

# verify the champion subsets really are in general position, from scratch
print()
print('  re-verifying each champion subset in exact coordinates:')
out = {}
for m in sorted(best):
    M, src, S = best[m]
    P = [WIT[src if src in WIT else int(src)][0][i] for i in S]
    D, pin, col, cyc, worst = analyse(P)
    ok = (not col) and (not cyc) and max(pin) == M
    print('    n=%d  M=%d  D=%d  pinned=%s  collinear=%d cocircular=%d  [%s]'
          % (m, M, D, pin, len(col), len(cyc), 'OK' if ok else 'MISMATCH'))
    out[m] = {'M': M, 'D': D, 'pinned': pin, 'source': src, 'subset': list(S),
              'points': [[sp.srepr(c) for c in p] for p in P],
              'general_position': ok}
json.dump(out, open('upper_by_deletion.json', 'w'), indent=1)
print()
print('  written: upper_by_deletion.json')
