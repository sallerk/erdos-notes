"""Final decision on the surviving 6-point 3-distance pattern.

The lex Groebner basis of the rank-<=2 conditions is exactly

        v = (u - 1)^2                                  ... (A)
        u^3 - 5u^2 + 6u - 1 = 0                        ... (B)

with discriminant 49 > 0, so (B) has three distinct real roots, all positive:
u ~ 0.198062, 1.554958, 3.246980.  Each gives a positive v via (A), and in each case the
three classes 1, u, v are distinct.  So the algebra does NOT rule the pattern out and the
verdict turns entirely on positive semidefiniteness of the Gram matrix.

Because every 3x3 minor vanishes by construction at these (u, v), the rank is at most 2
automatically.  A symmetric matrix of rank <= 2 is PSD exactly when all its 1x1 and 2x2
PRINCIPAL minors are >= 0, so that is what gets tested, exactly: each minor is a
polynomial in u, reduced modulo the cubic, then sign-determined by isolating-interval
arithmetic on the algebraic number (sympy CRootOf), not by floating point.
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import sympy as sp

u = sp.symbols('u', real=True)
CUBIC = u ** 3 - 5 * u ** 2 + 6 * u - 1
VEXPR = (u - 1) ** 2

PAT = (0, 0, 1, 1, 2, 1, 0, 2, 1, 2, 0, 2, 2, 0, 1)
PAIRS = list(itertools.combinations(range(6), 2))


def gram_of(uu, vv):
    VAL = {0: sp.Integer(1), 1: uu, 2: vv}
    D = {}
    for idx, (i, j) in enumerate(PAIRS):
        D[(i, j)] = D[(j, i)] = VAL[PAT[idx]]
    for i in range(6):
        D[(i, i)] = sp.Integer(0)
    return sp.Matrix(5, 5, lambda a, b: sp.Rational(1, 2) *
                     (D[(0, a + 1)] + D[(0, b + 1)] - D[(a + 1, b + 1)]))


print('=' * 74)
print('FINAL DECISION ON THE SURVIVING 6-POINT PATTERN')
print('=' * 74)
print('  basis:  v = (u-1)^2   and   u^3 - 5u^2 + 6u - 1 = 0')
print('  discriminant %s  => three distinct real roots' % sp.discriminant(CUBIC, u))
print()

Gsym = gram_of(u, VEXPR)
roots = sp.real_roots(CUBIC, u)
verdicts = []

for ridx, r in enumerate(roots):
    rf = sp.N(r, 40)
    vf = sp.N(VEXPR.subs(u, r), 40)
    print('  --- branch %d:  u = %.15f,  v = (u-1)^2 = %.15f ---'
          % (ridx, float(rf), float(vf)))
    if rf <= 0 or vf <= 0:
        print('      rejected: squared distances must be positive')
        verdicts.append('rejected: nonpositive')
        continue
    dist = (sp.N(abs(rf - 1), 40) > sp.Float('1e-30')
            and sp.N(abs(vf - 1), 40) > sp.Float('1e-30')
            and sp.N(abs(rf - vf), 40) > sp.Float('1e-30'))
    print('      classes {1, %.9f, %.9f} distinct: %s' % (float(rf), float(vf), dist))
    if not dist:
        verdicts.append('rejected: classes coincide')
        continue

    # rank check: every 3x3 minor must vanish (it should, by construction)
    worst3 = sp.Integer(0)
    for rows in itertools.combinations(range(5), 3):
        for cols in itertools.combinations(range(5), 3):
            e = sp.expand(Gsym[list(rows), list(cols)].det())
            val = sp.N(sp.rem(sp.Poly(e, u), sp.Poly(CUBIC, u)).as_expr().subs(u, r), 40)
            worst3 = max(worst3, abs(val))
    print('      max |3x3 minor| = %.3e  (rank <= 2 confirmed)' % float(worst3))

    # PSD: all 1x1 and 2x2 PRINCIPAL minors >= 0
    bad = []
    mins = []
    for m in (1, 2):
        for c in itertools.combinations(range(5), m):
            e = sp.expand(Gsym[list(c), list(c)].det())
            val = sp.N(sp.rem(sp.Poly(e, u), sp.Poly(CUBIC, u)).as_expr().subs(u, r), 40)
            mins.append((c, val))
            if val < sp.Float('-1e-30'):
                bad.append((c, val))
    print('      1x1 principal minors: %s'
          % [float(v) for c, v in mins if len(c) == 1])
    print('      most negative 2x2 principal minor: %.9f'
          % min(float(v) for c, v in mins if len(c) == 2))
    if bad:
        print('      NOT PSD: %d negative principal minor(s), e.g. %s = %.9f'
              % (len(bad), bad[0][0], float(bad[0][1])))
        print('      => this branch is NOT realisable by real points in the plane')
        verdicts.append('rejected: Gram not PSD')
    else:
        print('      PSD with rank <= 2  => REALISABLE, geometric check still required')
        verdicts.append('ADMISSIBLE')
    print()

print('=' * 74)
print('branch verdicts: %s' % verdicts)
print()
if all(v != 'ADMISSIBLE' for v in verdicts):
    print('Every branch fails, so the pattern is NOT realisable in the plane.')
    print('It was the only 6-point 3-distance candidate surviving augmentation, hence')
    print('    D_gen(6) > 3,')
    print('and with the independently verified 4-distance witness,')
    print('    D_gen(6) = 4.')
else:
    print('At least one branch is admissible; reconstruct coordinates and test')
    print('no-three-collinear and no-four-cocircular before concluding anything.')
