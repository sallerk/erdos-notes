"""Emit the surviving n=5 pattern as a real quantifier-elimination problem for Redlog.

WHY THIS IS SMALL ENOUGH TO TRY.  The general question has six coordinate unknowns and
degree-10 equations, which is hopeless for cylindrical algebraic decomposition.  The
structure theory collapses the one pattern that survives the lemmas to THREE unknowns:

  * the class {012, 013, 024, 034} has all four circles through P0, so with P0 at the
    origin and the radius 1 the four centres are unit vectors o1..o4 and
        P1 = o1+o2,  P2 = o1+o3,  P3 = o2+o4,  P4 = o3+o4      (Lemma 5)
  * fixing the rotation by o1 = (1,0) leaves three angles;
  * Lemma 6 makes R(123) = R(234) and R(124) = R(134) identities on this family, so the
    six remaining triples already take at most four values and only TWO equations remain,
        R(014) = R(123)   and   R(023) = R(124),
    which is the pattern {012,013,024,034} | {123,234,014} | {124,134,023}.

Writing each angle through the tangent half-angle substitution
cos = (1-t^2)/(1+t^2), sin = 2t/(1+t^2) makes every coordinate rational in t2, t3, t4,
so after clearing denominators the whole question is a sentence about three real
variables.  That is the regime where CAD is actually usable.

The sentence emitted is: does there EXIST (t2,t3,t4) satisfying both equations, with all
five points distinct, no three collinear, no four concyclic, and the three class radii
pairwise different?  An answer of `false` settles this branch; `true` would hand back a
configuration and prove h(5) = 3.

Usage: python mkqe.py            writes qe_typeIII.red and prints the degrees
"""
import sys

import io

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

t2, t3, t4 = sp.symbols('t2 t3 t4', real=True)


def unit_from_t(t):
    """(cos, sin) of the angle with tan(angle/2) = t, as rational functions"""
    d = 1 + t ** 2
    return (1 - t ** 2) / d, 2 * t / d


o = [(sp.Integer(1), sp.Integer(0))]
for t in (t2, t3, t4):
    o.append(unit_from_t(t))

P = {0: (sp.Integer(0), sp.Integer(0)),
     1: (o[0][0] + o[1][0], o[0][1] + o[1][1]),
     2: (o[0][0] + o[2][0], o[0][1] + o[2][1]),
     3: (o[1][0] + o[3][0], o[1][1] + o[3][1]),
     4: (o[2][0] + o[3][0], o[2][1] + o[3][1])}


def d2(i, j):
    return sp.together((P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2)


def r2num_den(i, j, k):
    """circumradius squared as a single rational function, numerator and denominator"""
    a2, b2, c2 = d2(j, k), d2(k, i), d2(i, j)
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 ** 2 + b2 ** 2 + c2 ** 2)
    expr = sp.cancel(sp.together(a2 * b2 * c2 / S))
    n, d = sp.fraction(sp.cancel(expr))
    return sp.expand(n), sp.expand(d)


def eq_poly(T, U):
    """numerator of R^2(T) - R^2(U), cleared of denominators"""
    n1, d1 = r2num_den(*T)
    n2, d2_ = r2num_den(*U)
    return sp.factor(sp.expand(n1 * d2_ - n2 * d1))


def cross(i, j, k):
    return sp.expand(sp.together((P[j][0] - P[i][0]) * (P[k][1] - P[i][1])
                                 - (P[j][1] - P[i][1]) * (P[k][0] - P[i][0])))


def det4(q):
    M = sp.Matrix([[P[v][0] ** 2 + P[v][1] ** 2, P[v][0], P[v][1], 1] for v in q])
    return sp.expand(sp.together(M.det()))


def poly_str(e):
    """Redlog/Reduce syntax: ** for powers, no spaces needed"""
    return str(sp.expand(sp.numer(sp.together(e)))).replace('**', '^')


if __name__ == '__main__':
    from itertools import combinations

    print('building the two equations ...', flush=True)
    E1 = eq_poly((0, 1, 4), (1, 2, 3))
    E2 = eq_poly((0, 2, 3), (1, 2, 4))
    for nm, e in (('E1', E1), ('E2', E2)):
        p = sp.Poly(sp.numer(sp.together(e)), t2, t3, t4)
        print('  %s: total degree %d, %d terms' % (nm, p.total_degree(), len(p.terms())))

    print('building the side conditions ...', flush=True)
    coll = [cross(*T) for T in combinations(range(5), 3)]
    conc = [det4(q) for q in combinations(range(5), 4)]
    dist = [(P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2
            for i, j in combinations(range(5), 2)]
    # the three class radii must differ: class 1 has radius^2 = 1 by construction
    n014, d014 = r2num_den(0, 1, 4)
    n023, d023 = r2num_den(0, 2, 3)
    sep = [sp.expand(n014 - d014), sp.expand(n023 - d023),
           sp.expand(n014 * d023 - n023 * d014)]

    parts = []
    parts.append('(' + poly_str(E1) + ' = 0)')
    parts.append('(' + poly_str(E2) + ' = 0)')
    for e in coll:
        parts.append('(' + poly_str(e) + ' <> 0)')
    for e in conc:
        parts.append('(' + poly_str(e) + ' <> 0)')
    for e in dist:
        parts.append('(' + poly_str(e) + ' > 0)')
    for e in sep:
        parts.append('(' + poly_str(e) + ' <> 0)')

    body = ' and '.join(parts)
    # newline='' keeps LF endings: Reduce on Windows reads a CR as an unknown
    # token and stalls on 'Declare <CR> operator?'
    with io.open('qe_typeIII.red', 'w', newline='') as f:
        f.write('load_package redlog;\nrlset ofsf;\noff nat;\non rlverbose;\n')
        f.write('phi := ex({t2,t3,t4}, ' + body + ');\n')
        f.write('result := rlqe phi;\n')
        f.write('write "ANSWER: ", result;\n')
        f.write('quit;\n')
    print()
    print('wrote qe_typeIII.red')
    print('  equations        : 2')
    print('  collinearity     : %d' % len(coll))
    print('  concyclicity     : %d' % len(conc))
    print('  distinctness     : %d' % len(dist))
    print('  radius-separation: %d' % len(sep))
    import os
    print('  file size        : %d bytes' % os.path.getsize('qe_typeIII.red'))
