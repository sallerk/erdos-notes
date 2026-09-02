"""Independent verification of every D_gen upper-bound witness.

The searches (latmin.py, witness.py, direct.py) each certify their own output, but they
do it inside the same integer embedding they search in.  This script re-checks each
witness from scratch, in ACTUAL PLANE COORDINATES with sympy exact arithmetic, using no
code from the searchers.  A triangular-lattice point (a,b) becomes the real point
(a + b/2, b*sqrt(3)/2); a square-lattice point is itself.

Everything is decided symbolically: collinearity from a 3x3 determinant, cocircularity
from a 4x4 determinant, distances as exact algebraic numbers.

Usage:  python verify.py
"""
import sys, itertools, json, glob, os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


def to_plane(pts, lattice):
    r3 = sp.sqrt(3)
    out = []
    for a, b in pts:
        if lattice == 'a2':
            out.append((sp.Rational(a) + sp.Rational(b, 2), sp.Rational(b) * r3 / 2))
        else:
            out.append((sp.Rational(a), sp.Rational(b)))
    return out


def check_set(P, name, expect_k=None):
    n = len(P)
    d2 = {}
    for i, j in itertools.combinations(range(n), 2):
        v = sp.expand((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2)
        d2[(i, j)] = sp.simplify(v)
    vals = []
    for v in d2.values():
        if not any(sp.simplify(v - w) == 0 for w in vals):
            vals.append(v)
    vals.sort(key=lambda e: float(e))

    col = [t for t in itertools.combinations(range(n), 3)
           if sp.simplify((P[t[1]][0] - P[t[0]][0]) * (P[t[2]][1] - P[t[0]][1])
                          - (P[t[2]][0] - P[t[0]][0]) * (P[t[1]][1] - P[t[0]][1])) == 0]
    cyc = []
    for q in itertools.combinations(range(n), 4):
        M = sp.Matrix([[P[t][0] ** 2 + P[t][1] ** 2, P[t][0], P[t][1], 1] for t in q])
        if sp.simplify(M.det()) == 0:
            cyc.append(q)

    print()
    print('%s   n=%d' % (name, n))
    print('   distinct squared distances: %d   %s'
          % (len(vals), [sp.nsimplify(v) for v in vals]))
    ck('   no three collinear (%s)' % name, not col,
       '%d offending triples' % len(col))
    ck('   no four cocircular (%s)' % name, not cyc,
       '%d offending quadruples' % len(cyc))
    if expect_k is not None:
        ck('   distinct-distance count is %d as claimed (%s)' % (expect_k, name),
           len(vals) == expect_k, 'found %d' % len(vals))

    # the structural bound: at most 3 points equidistant from any given point
    worst = 0
    for i in range(n):
        cnt = {}
        for j in range(n):
            if j == i:
                continue
            key = None
            v = d2[(min(i, j), max(i, j))]
            for w in cnt:
                if sp.simplify(v - w) == 0:
                    key = w
                    break
            if key is None:
                cnt[v] = 1
            else:
                cnt[key] += 1
        worst = max(worst, max(cnt.values()))
    ck('   no point has 4+ others equidistant from it (%s)' % name, worst <= 3,
       'max multiplicity at a vertex = %d' % worst)
    return len(vals)


print('=' * 74)
print('INDEPENDENT VERIFICATION OF D_gen WITNESSES')
print('re-checked in real plane coordinates with sympy, not in the search embedding')
print('=' * 74)

# the algebraic 5-point witness found by the solver
r3 = sp.sqrt(3)
W5 = [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)),
      (sp.Rational(1, 2), r3 / 2), (-r3 / 2, sp.Rational(-1, 2)),
      (sp.Rational(1, 2), -(2 + r3) / 2)]
check_set(W5, 'solver witness n=5 (algebraic, Q(sqrt3))', 3)

# every lattice witness on disk
for fn in sorted(glob.glob('latmin_n*.json')):
    d = json.load(open(fn))
    P = to_plane([tuple(p) for p in d['points']], d['lattice'])
    check_set(P, '%s  (lattice %s, R2=%d)' % (fn, d['lattice'], d['R2']), d['distinct'])

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL WITNESSES VERIFIED')
print('=' * 74)
