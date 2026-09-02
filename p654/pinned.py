"""Phase 0 for Erdos #654: what our existing verified #98 witnesses already give.

#654 asks for  f(n) = min over configurations of  M(X),  where  M(X) = max_i d_X(x_i)
and d_X(x) is the number of DISTINCT distances from x to the other points.

Two versions, which must not be blurred:
    f_N4(n)  hypothesis: no four points on a circle          <- the problem page's f(n)
    f_G(n)   hypothesis: general position (also no 3 collinear)  <- Sheffer's D-hat_gen(n)
Since G is a subset of N4-only configurations, f_N4(n) <= f_G(n).

Every witness below is in general position (re-checked here), so each gives an upper bound
on BOTH.  They were optimised to minimise the TOTAL count D, not the pinned max M, so
these are upper bounds only and are expected to be beatable.

Exact arithmetic throughout; no floats.
"""
import sys, itertools, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

r3 = sp.sqrt(3)


def a2(a, b):
    """triangular-lattice point (a,b) as an exact plane point"""
    return (sp.Rational(a) + sp.Rational(b, 2), sp.Rational(b) * sp.sqrt(3) / 2)


# the verified #98 witnesses, copied from p98/audit98.py (value = (points, D))
WIT = {
    3: ([a2(0, 0), a2(1, 0), a2(0, 1)], 1),
    4: ([a2(0, 0), a2(-1, 0), a2(-1, 1), a2(0, -1)], 2),
    5: ([(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0)),
         (sp.Rational(1, 2), r3 / 2), (-r3 / 2, sp.Rational(-1, 2)),
         (sp.Rational(1, 2), -(2 + r3) / 2)], 3),
    6: ([a2(0, 0), a2(-1, 0), a2(-1, 2), a2(-3, 1), a2(-3, 2), a2(-2, 3)], 4),
    7: ([a2(0, 0), a2(-1, 0), a2(-1, 1), a2(1, -3), a2(3, -2), a2(2, -4), a2(4, -2)], 5),
    8: ([a2(0, 0), a2(-1, 0), a2(-1, 1), a2(1, -3), a2(2, -3), a2(3, -1), a2(-2, -2),
         a2(2, -4)], 7),
}

# an extra hand-built candidate: equilateral triangle plus its centre.
# every vertex sees {side, circumradius} = 2 values, the centre sees 1.
WIT['4c'] = ([a2(0, 0), a2(1, 0), a2(0, 1),
              ((sp.Rational(1) + sp.Rational(1, 2)) / 3, (r3 / 2) / 3)], None)


def sq(p, q):
    return sp.expand((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def uniq(vals):
    """exact deduplication of a list of algebraic numbers"""
    out = []
    for x in vals:
        if not any(sp.simplify(x - y) == 0 for y in out):
            out.append(sp.nsimplify(x))
    return out


def analyse(P):
    n = len(P)
    dsq = {(i, j): sq(P[i], P[j]) for i, j in itertools.combinations(range(n), 2)}
    dsq.update({(j, i): v for (i, j), v in list(dsq.items())})
    D = len(uniq(list(dsq[(i, j)] for i, j in itertools.combinations(range(n), 2))))
    pin = [len(uniq([dsq[(i, j)] for j in range(n) if j != i])) for i in range(n)]
    col = [t for t in itertools.combinations(range(n), 3)
           if sp.simplify((P[t[1]][0] - P[t[0]][0]) * (P[t[2]][1] - P[t[0]][1])
                          - (P[t[2]][0] - P[t[0]][0]) * (P[t[1]][1] - P[t[0]][1])) == 0]
    cyc = [q for q in itertools.combinations(range(n), 4)
           if sp.simplify(sp.Matrix([[P[t][0] ** 2 + P[t][1] ** 2, P[t][0], P[t][1], 1]
                                     for t in q]).det()) == 0]
    # largest number of points equidistant from a common point of the set
    worst = 0
    for i in range(n):
        c = {}
        for j in range(n):
            if j == i:
                continue
            hit = None
            for key in c:
                if sp.simplify(dsq[(i, j)] - key) == 0:
                    hit = key
                    break
            c[hit if hit is not None else sp.nsimplify(dsq[(i, j)])] = \
                c.get(hit, 0) + 1 if hit is not None else 1
        worst = max(worst, max(c.values()))
    return D, pin, col, cyc, worst


if __name__ == '__main__':
    print('=' * 78)
    print('PHASE 0 -- pinned distance counts M(X) of the verified #98 witnesses')
    print('=' * 78)
    print()
    print('  n   D   M = max_i d(x_i)   per-point counts        N3  N4  max on a circle')
    print('  ' + '-' * 74)
    rows = {}
    for key in [3, 4, '4c', 5, 6, 7, 8]:
        P, _ = WIT[key]
        n = len(P)
        D, pin, col, cyc, worst = analyse(P)
        rows[str(key)] = {'n': n, 'D': D, 'M': max(pin), 'pinned': pin,
                          'collinear_triples': len(col), 'cocircular_quads': len(cyc),
                          'max_equidistant_from_a_point': worst}
        print('  %-3s %2d   %2d                 %-22s %-3s %-3s %d'
              % (key, D, max(pin), pin,
                 'ok' if not col else 'BAD', 'ok' if not cyc else 'BAD', worst))
    print()
    print('  (row "4c" is the equilateral triangle plus its centre, added by hand)')
    print()
    print('  Trivial lower bound under N4: every circle centred at x holds at most 3 other')
    print('  points, so d(x) >= (n-1)/3 and therefore f(n) >= ceil((n-1)/3).')
    print()
    print('  n   ceil((n-1)/3)   best upper bound from a witness above')
    print('  ' + '-' * 74)
    best = {}
    for key, r in rows.items():
        n = r['n']
        if n not in best or r['M'] < best[n][0]:
            best[n] = (r['M'], key)
    for n in sorted(best):
        lo = -(-(n - 1) // 3)
        print('  %-3d %-15d %d   (witness %s)%s'
              % (n, lo, best[n][0], best[n][1],
                 '   <-- SETTLED' if lo == best[n][0] else ''))
    json.dump(rows, open('phase0_pinned.json', 'w'), indent=1)
    print()
    print('  written: phase0_pinned.json')
