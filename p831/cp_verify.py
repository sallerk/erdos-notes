"""Independent check of the impossibility proof for the surviving common-point pattern of
n = 5 (Erdos #831), {012,013,024,034} | {123,234,014} | {124,134,023}, and of the corrections
section 5c makes to section 5 of NOTE.md.

Nothing here is taken from the derivation being checked except the statements themselves.
Every identity is verified EXACTLY, not numerically: write each centre as o_j = z_j^2 with
|z_j| = 1, so complex conjugation is the substitution z -> 1/z and every squared distance,
cross product and squared circumradius becomes a Laurent polynomial in z1..z4.  An identity
of Laurent polynomials holds for all unit-modulus z, hence for all real angles.

Every [PASS] line below is the outcome of a computation.  Statements that are readings of
earlier checks rather than computations are printed as NOTE lines and do not count towards
ALL CHECKS PASSED.  Sections are numbered in the order NOTE.md section 5c presents them.

Usage: python cp_verify.py
"""
import json
import math
import sys
from fractions import Fraction
from itertools import combinations, permutations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
FAIL = []
PASSED = {}


def ck(key, label, ok, detail=''):
    """record one computed check; ok must be computed by the caller, never a constant"""
    ok = bool(ok)
    PASSED[key] = ok
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


def note(text):
    print('  NOTE   ' + text)


z1, z2, z3, z4 = sp.symbols('z1 z2 z3 z4', nonzero=True)
Z = (z1, z2, z3, z4)


def conj(e):
    return e.subs({z: 1 / z for z in Z}, simultaneous=True)


def zero(e):
    """is this rational function in z1..z4 identically zero?"""
    return sp.expand(sp.numer(sp.cancel(sp.together(sp.expand(e))))) == 0


o1, o2, o3, o4 = z1 ** 2, z2 ** 2, z3 ** 2, z4 ** 2          # the four unit centres
P = [sp.Integer(0), o1 + o2, o1 + o3, o2 + o4, o3 + o4]      # P0 .. P4 (Lemma 5)


def d2(p, q):
    return sp.expand((p - q) * conj(p - q))


def KK(p, q, r):
    """2i times the cross product (q-p) x (r-p)"""
    return sp.expand((q - p) * conj(r - p) - conj(q - p) * (r - p))


def cross2(i, j, k):
    """the squared cross product of the triple (i,j,k): KK = 2i*cross, so cross^2 = -KK^2/4"""
    return -KK(P[i], P[j], P[k]) ** 2 / 4


def R2(i, j, k):
    """squared circumradius of the triple (i,j,k): a2*b2*c2/(4 K^2), with K^2 = -KK^2/4"""
    p, q, r = P[i], P[j], P[k]
    return -d2(p, q) * d2(q, r) * d2(r, p) / KK(p, q, r) ** 2


# rotation-invariant coordinates: alpha = (th3+th4-th1-th2)/2 etc., so e^{i alpha} = z3 z4/(z1 z2)
ea, eb, eg = z3 * z4 / (z1 * z2), z2 * z4 / (z1 * z3), z1 * z4 / (z2 * z3)
A, B, C = [sp.expand((e + 1 / e) / 2) for e in (ea, eb, eg)]
S2A, S2B, S2C = 1 - A ** 2, 1 - B ** 2, 1 - C ** 2              # sin^2 alpha, beta, gamma
D1, D2 = d2(P[1], P[4]), d2(P[2], P[3])


def sin_half(zi, zj):
    """sin((th_j - th_i)/2), since z = exp(i th / 2)"""
    return (zj / zi - zi / zj) / (2 * sp.I)


print('1. The gauge: the four triples through P0 all have squared circumradius 1')
for t in [(0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4)]:
    ck('gauge%s' % (t,), 'R^2%s = 1 identically' % (t,), zero(R2(*t) - 1))

print()
print('2. Lemma 6: the two identities among the remaining six triples')
ck('L6a', 'R^2(123) = R^2(234) identically', zero(R2(1, 2, 3) - R2(2, 3, 4)))
ck('L6b', 'R^2(124) = R^2(134) identically', zero(R2(1, 2, 4) - R2(1, 3, 4)))
ck('L6c', 'R^2(123) and R^2(124) are NOT identically equal (the two classes are genuinely two)',
   not zero(R2(1, 2, 3) - R2(1, 2, 4)))

print()
print('3. Lemma 7: the diagonals, and the closed forms for the four non-identity radii')
ck('D1', 'D1 = 4(1 - A*B + C*(B-A))', zero(D1 - 4 * (1 - A * B + C * (B - A))))
ck('D2', 'D2 = 4(1 - A*B - C*(B-A))', zero(D2 - 4 * (1 - A * B - C * (B - A))))
ck('R014', 'R^2(014) = D1 / (4 sin^2 alpha)', zero(R2(0, 1, 4) * 4 * S2A - D1))
ck('R023', 'R^2(023) = D2 / (4 sin^2 beta)', zero(R2(0, 2, 3) * 4 * S2B - D2))
ck('R123', 'R^2(123) = D2 / (4 sin^2 gamma)', zero(R2(1, 2, 3) * 4 * S2C - D2))
ck('R124', 'R^2(124) = D1 / (4 sin^2 gamma)', zero(R2(1, 2, 4) * 4 * S2C - D1))

print()
print('4. Lemma 8: the degeneracy dictionary, in the form NOTE.md displays it')
ck('X014', 'cross(P0,P1,P4)^2 = |P0P1|^2 |P0P4|^2 sin^2 alpha',
   zero(cross2(0, 1, 4) - d2(P[0], P[1]) * d2(P[0], P[4]) * S2A))
ck('X023', 'cross(P0,P2,P3)^2 = |P0P2|^2 |P0P3|^2 sin^2 beta',
   zero(cross2(0, 2, 3) - d2(P[0], P[2]) * d2(P[0], P[3]) * S2B))
for t in [(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)]:
    ck('X%d%d%d' % t, 'cross(P%d,P%d,P%d)^2 = |P1P2|^2 |P1P3|^2 sin^2 gamma' % t,
       zero(cross2(*t) - d2(P[1], P[2]) * d2(P[1], P[3]) * S2C))
ck('AmB_z', 'A - B = (z1^2 - z4^2)(z2^2 - z3^2) / (2 z1 z2 z3 z4), with this sign',
   zero(A - B - (z1 ** 2 - z4 ** 2) * (z2 ** 2 - z3 ** 2) / (2 * z1 * z2 * z3 * z4)))
ck('AmB_trig', 'A - B = -2 sin((th4-th1)/2) sin((th3-th2)/2), with this sign',
   zero(A - B + 2 * sin_half(z1, z4) * sin_half(z2, z3)))
ck('P12', '|P1-P2|^2 = |o3-o2|^2', zero(d2(P[1], P[2]) - d2(o3, o2)))
ck('P13', '|P1-P3|^2 = |o4-o1|^2', zero(d2(P[1], P[3]) - d2(o4, o1)))
ck('o23', 'o2 = o3 forces P1 = P2', zero((P[1] - P[2]).subs(z3, z2)))
ck('o14', 'o1 = o4 forces P1 = P3', zero((P[1] - P[3]).subs(z4, z1)))
note('so 014 non-collinear means |A| < 1, 023 non-collinear means |B| < 1, and P1 distinct')
note('from P2 and from P3 means A != B (checks X014, X023, AmB_z, o23, o14).')

print()
print('5. The two genuine equations as polynomials in A, B, C')
a, b, c = sp.symbols('a b c')
d1, d2_ = 4 * (1 - a * b + c * (b - a)), 4 * (1 - a * b - c * (b - a))
E1 = sp.expand(d1 * (1 - c ** 2) - d2_ * (1 - a ** 2))
E2 = sp.expand(d2_ * (1 - c ** 2) - d1 * (1 - b ** 2))
B_E1 = sp.expand(4 * (-a ** 3 * b + a ** 3 * c - a ** 2 * b * c + a ** 2 + a * b * c ** 2
                      + a * c ** 3 - 2 * a * c - b * c ** 3 + 2 * b * c - c ** 2))
B_E2 = sp.expand(4 * (-a * b ** 3 - a * b ** 2 * c + a * b * c ** 2 - a * c ** 3 + 2 * a * c
                      + b ** 3 * c + b ** 2 + b * c ** 3 - 2 * b * c - c ** 2))
ck('E1poly', 'E1 matches the claimed polynomial', sp.expand(E1 - B_E1) == 0)
ck('E2poly', 'E2 matches the claimed polynomial', sp.expand(E2 - B_E2) == 0)
ck('E1geo', 'E1 = 0 is exactly R^2(014) = R^2(123) off the excluded loci',
   zero(sp.expand(E1.subs({a: A, b: B, c: C})) - 4 * S2A * S2C * (R2(0, 1, 4) - R2(1, 2, 3))))
ck('E2geo', 'E2 = 0 is exactly R^2(023) = R^2(124) off the excluded loci',
   zero(sp.expand(E2.subs({a: A, b: B, c: C})) - 4 * S2B * S2C * (R2(0, 2, 3) - R2(1, 2, 4))))

print()
print('6. The first proof: a resultant and a positivity certificate (no representative choice)')
# E1 + E2 = 4*G1 and E1 - E2 = 4*(B-A)*G2.  If E1 = E2 = 0 and A != B then G1 and G2 share the
# root C, so their resultant in C vanishes.  It does not: the resultant factors with a factor W
# that a certificate shows is at least 4(A-B)^2 on the square |A| <= 1, |B| <= 1.
G1 = sp.expand(sp.cancel((E1 + E2) / 4))
G2 = sp.expand(sp.cancel((E1 - E2) / (4 * (b - a))))
ck('G12', 'E1 + E2 = 4*G1 and E1 - E2 = 4*(B-A)*G2, exactly',
   sp.expand(E1 + E2 - 4 * G1) == 0 and sp.expand(E1 - E2 - 4 * (b - a) * G2) == 0)
ck('G1form', 'G1 = (1-A*B)*(A^2+B^2-2*C^2) + C*(B-A)^2*(A+B), as NOTE.md writes it',
   sp.expand(G1 - ((1 - a * b) * (a ** 2 + b ** 2 - 2 * c ** 2) + c * (b - a) ** 2 * (a + b))) == 0)
ck('G2form', 'G2 = C*(4 - 2*C^2 - A^2 - B^2) - (1-A*B)*(A+B), as NOTE.md writes it',
   sp.expand(G2 - (c * (4 - 2 * c ** 2 - a ** 2 - b ** 2) - (1 - a * b) * (a + b))) == 0)
ck('lc', 'the leading coefficient of G2 in C is the constant -2, so a shared root forces the '
   'resultant to vanish', sp.Poly(G2, c).LC() == -2, 'G2 has degree %d in C' % sp.Poly(G2, c).degree())
W = (a ** 6 - 2 * a ** 5 * b + 6 * a ** 4 * b ** 2 + a ** 4 + 2 * a ** 3 * b ** 3 - 14 * a ** 3 * b
     + 6 * a ** 2 * b ** 4 + 2 * a ** 2 * b ** 2 + 7 * a ** 2 - 2 * a * b ** 5 - 14 * a * b ** 3
     - 2 * a * b + b ** 6 + b ** 4 + 7 * b ** 2)
res = sp.resultant(G1, G2, c)
ck('res', 'Res_C(G1, G2) = -8 (A^2-1)(B^2-1)(AB-1) W(A,B)',
   sp.expand(res + 8 * (a ** 2 - 1) * (b ** 2 - 1) * (a * b - 1) * W) == 0)
S, Dd = sp.symbols('S D')
cert = (64 * Dd ** 2 + 3 * S ** 2 * (S ** 2 - 4) ** 2 + 4 * Dd ** 6 + 11 * Dd ** 4 * S ** 2
        + 32 * Dd ** 4 + 2 * Dd ** 2 * S ** 2 * (4 - S ** 2))
ck('cert', '16*W = 64 d^2 + 3 s^2 (s^2-4)^2 + 4 d^6 + 11 d^4 s^2 + 32 d^4 + 2 d^2 s^2 (4-s^2), '
   'with s = A+B and d = A-B', sp.expand(16 * W.subs({a: (S + Dd) / 2, b: (S - Dd) / 2}) - cert) == 0)
# The sign inspection, computed rather than asserted.  With p = d^2, q = s^2 and u = 4 - s^2 the
# certificate is a polynomial in p, q, u; if every coefficient is positive and p, q, u >= 0, the
# certificate is at least its 64 p term.
p_, q_, u_ = sp.symbols('p q u')
cert_pqu = 64 * p_ + 3 * q_ * u_ ** 2 + 4 * p_ ** 3 + 11 * p_ ** 2 * q_ + 32 * p_ ** 2 + 2 * p_ * q_ * u_
ck('cert_pqu', 'the certificate is the polynomial 64p + 3qu^2 + 4p^3 + 11p^2q + 32p^2 + 2pqu in '
   'p = d^2, q = s^2, u = 4 - s^2',
   sp.expand(cert - cert_pqu.subs({p_: Dd ** 2, q_: S ** 2, u_: 4 - S ** 2})) == 0)
rest_coeffs = sp.Poly(sp.expand(cert_pqu - 64 * p_), p_, q_, u_).coeffs()
ck('cert_pos', '16W - 64d^2 = 3qu^2 + 4p^3 + 11p^2q + 32p^2 + 2pqu has only positive coefficients, '
   'so it is >= 0 wherever p, q, u >= 0', all(k > 0 for k in rest_coeffs),
   'coefficients %s' % rest_coeffs)
ck('u_nonneg', '4 - s^2 = 2(1-A^2) + 2(1-B^2) + (A-B)^2, so u >= 0 on the square |A| <= 1, |B| <= 1',
   sp.expand(4 - (a + b) ** 2 - (2 * (1 - a ** 2) + 2 * (1 - b ** 2) + (a - b) ** 2)) == 0)
ck('ab_lt1', '1 - AB = [(1-A^2) + (1-B^2) + (A-B)^2] / 2, so AB != 1 when |A| < 1 and |B| < 1',
   sp.expand((1 - a * b) - ((1 - a ** 2) + (1 - b ** 2) + (a - b) ** 2) / 2) == 0)
note('hence W >= 4(A-B)^2 > 0 when A != B, every factor of the resultant is non-zero on |A| < 1,')
note('|B| < 1, A != B, and E1 = E2 = 0 has no real solution there (checks G12, lc, res, cert,')
note('cert_pqu, cert_pos, u_nonneg, ab_lt1).')
N = 40
grid_min, grid_neg = None, 0
Wm4 = sp.lambdify((a, b), W - 4 * (a - b) ** 2, 'sympy')
for i in range(N + 1):
    for j in range(N + 1):
        v = Wm4(Fraction(2 * i - N, N), Fraction(2 * j - N, N))
        grid_neg += v < 0
        grid_min = v if grid_min is None or v < grid_min else grid_min
ck('grid', 'control: W - 4(A-B)^2 >= 0 at all %d exact rational points of a %dx%d grid on the square'
   % ((N + 1) ** 2, N + 1, N + 1), grid_neg == 0, 'minimum %s' % grid_min)
ck('mutant', 'control: flipping the sign of the last certificate term breaks the identity, so the '
   'identity check is able to fail', sp.expand(16 * W.subs({a: (S + Dd) / 2, b: (S - Dd) / 2})
                                               - (cert - 4 * Dd ** 2 * S ** 2 * (4 - S ** 2))) != 0)
ck('diag', 'control: on the diagonal W(A,A) = 12 A^2 (A^2-1)^2, which vanishes at A = 0 and A = +-1, '
   'so A != B is load-bearing', sp.expand(W.subs(b, a) - 12 * a ** 2 * (a ** 2 - 1) ** 2) == 0)
ck('origin', 'control: (A,B,C) = (0,0,0) really is a real solution of E1 = E2 = 0, killed only by A != B',
   sp.expand(E1.subs({a: 0, b: 0, c: 0})) == 0 and sp.expand(E2.subs({a: 0, b: 0, c: 0})) == 0)
ck('curve', 'W is not constant and its restriction to the diagonal is not zero, so W = 0 is a curve '
   'meeting the diagonal finitely often; with checks lc and res, E1 = E2 = 0 has a positive-dimensional complex '
   'solution set', sp.Poly(W, a, b).total_degree() > 0 and sp.expand(W.subs(b, a)) != 0
   and PASSED.get('lc') and PASSED.get('res'), 'W has total degree %d' % sp.Poly(W, a, b).total_degree())

print()
print('7. The second proof, elementary. Step 2: the ideal identity forcing sin^4 gamma = sin^2 alpha sin^2 beta')
F1 = (1 - c ** 2) ** 2 - (1 - a ** 2) * (1 - b ** 2)
ck('ideal', 'D1*D2*F1 = D1*(1-C^2)*E2 + D2*(1-C^2)*E1 - E1*E2',
   sp.expand(d1 * d2_ * F1 - (d1 * (1 - c ** 2) * E2 + d2_ * (1 - c ** 2) * E1 - E1 * E2)) == 0)

print()
print('8. The second proof, steps 4 and 5: reduction to F2, and its factorisation')
m, n, g = sp.symbols('m n g')
Asub, Bsub, Csub = sp.cos(m + n), sp.cos(m - n), sp.cos(g)
D1t = 4 * (1 - Asub * Bsub + Csub * (Bsub - Asub))
D2t = 4 * (1 - Asub * Bsub - Csub * (Bsub - Asub))
X, Y = sp.sin(m) ** 2, sp.sin(n) ** 2
F2 = D1t * sp.sin(m - n) - D2t * sp.sin(m + n)
claim = -8 * sp.sin(n) * ((X + Y) * sp.cos(m) - 2 * Csub * X * sp.cos(n))
ck('F2', 'F2 = -8 sin(n) [ (X+Y) cos m - 2 C X cos n ]', sp.simplify(sp.expand_trig(F2 - claim)) == 0)
ck('XmY', 'sin(alpha) sin(beta) = X - Y',
   sp.simplify(sp.expand_trig(sp.sin(m + n) * sp.sin(m - n) - (X - Y))) == 0)

print()
print('9. The second proof, step 6: the exact factorisation on the (X, Y) square')
XX, YY = sp.symbols('X Y', nonnegative=True)
lhs = sp.expand((XX + YY) ** 2 * (1 - XX) - 4 * XX ** 2 * (1 - YY) * (1 - XX + YY))
rhs = sp.expand((YY - XX) * ((4 * XX ** 2 - XX + 1) * YY + 3 * XX * (1 - XX)))
ck('XYfac', '(X+Y)^2(1-X) - 4X^2(1-Y)(1-X+Y) = (Y-X)[(4X^2-X+1)Y + 3X(1-X)]', sp.expand(lhs - rhs) == 0)
ck('min1516', '4X^2 - X + 1 has minimum 15/16 > 0 over the reals',
   sp.minimum(4 * XX ** 2 - XX + 1, XX, sp.S.Reals) == sp.Rational(15, 16))

print()
print('10. The second proof, step 7: on [0,1]^2 the second factor vanishes only at Y = 0 with X in {0,1}')
second = (4 * XX ** 2 - XX + 1) * YY + 3 * XX * (1 - XX)
ck('terms_nonneg', 'both terms are non-negative on the square, so the sum is zero only if both are',
   sp.minimum(3 * XX * (1 - XX), XX, sp.Interval(0, 1)) == 0
   and sp.minimum(4 * XX ** 2 - XX + 1, XX, sp.Interval(0, 1)) == sp.Rational(15, 16))
sols = sp.solve([sp.Eq(second, 0), sp.Eq(YY, 0)], [XX, YY], dict=True)
ck('X01', 'with Y = 0 the factor reduces to 3X(1-X) = 0, so X = 0 or X = 1',
   sorted([s[XX] for s in sols]) == [0, 1], str(sols))

print()
print('11. The second proof: what each escape route means geometrically')
ck('AmB_mn', 'A - B = cos(m+n) - cos(m-n) = -2 sin(m) sin(n), so sin(n) = 0 (equivalently Y = 0, '
   'with n in [-pi/2, pi/2]) is exactly A = B',
   sp.simplify(sp.expand_trig(Asub - Bsub + 2 * sp.sin(m) * sp.sin(n))) == 0)
note('Y = X gives sin(alpha) sin(beta) = X - Y = 0 (check XmY), i.e. a collinear triple 014 or')
note('023 (checks X014, X023). A = B means P1 = P2 or P1 = P3 (checks AmB_z, o23, o14).')

print()
print('12. The other two common-point patterns die by Lemma 6 alone')
# In the canonical Lemma 5 form the size-4 class is {012,013,024,034} and section 2 proves
# R(123) = R(234) and R(124) = R(134) IDENTICALLY.  A pattern that puts either pair in two
# different classes therefore needs two distinct classes to share a radius, which is impossible.
TRI = list(combinations(range(5), 3))
PZ = json.load(open('results/penum_n5_k3.json'))['patterns']
CANON = {(0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4)}
IDENT_PAIRS = [((1, 2, 3), (2, 3, 4)), ((1, 2, 4), (1, 3, 4))]


def canonical_forms(labels):
    """one entry per relabelling carrying the size-4 class to CANON: (splits a Lemma 6 pair?, split)"""
    out = []
    for pm in permutations(range(5)):
        cls = {}
        for k, t in enumerate(TRI):
            cls.setdefault(labels[k], set()).add(tuple(sorted(pm[v] for v in t)))
        if any(cc == CANON for cc in cls.values()):
            cl_of = {t: k for k, cc in cls.items() for t in cc}
            split = tuple(sorted(tuple(sorted(cc)) for cc in cls.values() if cc != CANON))
            out.append((any(cl_of[x] != cl_of[y] for x, y in IDENT_PAIRS), split))
    return out


for idx, expect_dead in ((2, True), (12, True), (14, False)):
    forms = canonical_forms(PZ[idx]['labels'])
    kills = [f[0] for f in forms]
    ok = bool(forms) and (all(kills) if expect_dead else not any(kills))
    ck('pat%d' % idx, 'pattern %d: %d canonical forms, %s' % (
        idx, len(forms), 'all split an identically-equal pair, so Lemma 6 alone kills it' if expect_dead
        else 'none splits such a pair, so Lemma 6 leaves it open'), ok,
       '%d of %d split' % (sum(kills), len(forms)))
splits14 = {f[1] for f in canonical_forms(PZ[14]['labels'])}
ck('pat14_one', 'pattern 14 splits the other six triples in exactly ONE way over all its canonical '
   'forms, the crossed pairing {014,123,234} | {023,124,134}, so section 6 treats the whole pattern',
   splits14 == {(((0, 1, 4), (1, 2, 3), (2, 3, 4)), ((0, 2, 3), (1, 2, 4), (1, 3, 4)))},
   '%d distinct split(s)' % len(splits14))

print()
print('13. The corrections section 5c makes to the s^2/2 paragraph of section 5')
# The minimising family th = (0, -pi-s, -s, -2s).  With w = exp(-i s/2) the centres are
# o = (1, -w^2, w^2, w^4), Laurent polynomials in w with real coefficients, so conjugation is
# the substitution w -> 1/w.
w = sp.symbols('w', nonzero=True)


def cjw(e):
    return e.subs(w, 1 / w)


def zerow(e):
    return sp.expand(sp.numer(sp.cancel(sp.together(sp.expand(e))))) == 0


Ow = [sp.Integer(1), -w ** 2, w ** 2, w ** 4]
Pw = [sp.Integer(0), Ow[0] + Ow[1], Ow[0] + Ow[2], Ow[1] + Ow[3], Ow[2] + Ow[3]]


def d2w(p, q):
    return sp.expand((p - q) * cjw(p - q))


def R2w(i, j, k):
    p, q, r = Pw[i], Pw[j], Pw[k]
    kk = sp.expand((q - p) * cjw(r - p) - cjw(q - p) * (r - p))
    return -d2w(p, q) * d2w(q, r) * d2w(r, p) / kk ** 2


Mw = sp.Matrix([[Pw[k], cjw(Pw[k]), sp.expand(Pw[k] * cjw(Pw[k])), 1] for k in (1, 2, 3, 4)])
ck('fam_concyclic', 'on the family, P1, P2, P3, P4 are concyclic identically in s (the 4x4 circle '
   'determinant vanishes), so the configuration attaining the floor is inadmissible at every s',
   zerow(Mw.det()))
ra, rb, rc, rd = R2w(0, 1, 4), R2w(1, 2, 3), R2w(0, 2, 3), R2w(1, 2, 4)
f1, f2 = (ra - rb) / (ra + rb), (rc - rd) / (rc + rd)      # squared radii are positive, so |x| = x
closed = (-(w ** -2 - w ** 2) ** 2 / 4) / (1 + ((w ** -2 + w ** 2) / 2) ** 2)   # sin^2 s / (1 + cos^2 s)
ck('fam_closed', 'on the family, f1^2 = f2^2 = (sin^2 s / (1 + cos^2 s))^2, so the residual '
   'max(|f1|,|f2|) there is exactly sin^2 s / (1 + cos^2 s)',
   zerow(f1 ** 2 - closed ** 2) and zerow(f2 ** 2 - closed ** 2))
sv = sp.symbols('s', positive=True)
fam = [sp.Integer(0), -sp.pi - sv, -sv, -2 * sv]
# for 0 < s < pi/3 the angular distance between centres i and j is min(|th_i - th_j|, 2 pi - |th_i - th_j|)
diffs = [sp.expand(fam[j] - fam[i]) for i in range(4) for j in range(i + 1, 4)]
at = sp.Rational(1, 10)
fam_seps = sorted((sp.Abs(x).subs(sv, at) if sp.Abs(x).subs(sv, at) <= sp.pi else 2 * sp.pi - sp.Abs(x).subs(sv, at))
                  for x in diffs)
want_seps = sorted([at, at, 2 * at, sp.pi - at, sp.pi - at, sp.pi])
ck('fam_three', 'on the family the six centre separations are s, s, 2s, pi-s, pi-s, pi (checked exactly '
   'at s = 1/10): three centres lie within 2s of each other and the fourth is antipodal to one, so three '
   'merge as s -> 0', [sp.simplify(x - y) for x, y in zip(fam_seps, want_seps)] == [0] * 6)
rec = json.load(open('results/obstruction433.json'))['sweep']
worst_val, worst_sep = 0.0, 0.0
for r in rec:
    s_ = r['min_separation']
    fl = math.sin(s_) ** 2 / (1 + math.cos(s_) ** 2)
    worst_val = max(worst_val, abs(r['best'] - fl) / fl)
    th = [0.0] + r['theta']
    got = sorted(min(abs(th[i] - th[j]) % (2 * math.pi), 2 * math.pi - abs(th[i] - th[j]) % (2 * math.pi))
                 for i in range(4) for j in range(i + 1, 4))
    want = sorted([s_, s_, 2 * s_, math.pi - s_, math.pi - s_, math.pi])
    worst_sep = max(worst_sep, max(abs(x - y) for x, y in zip(got, want)))
ck('fam_record', 'numerical, against results/obstruction433.json: at all %d recorded margins the floor '
   'equals the closed form and the minimiser has the family\'s separations, so it lies on the family up '
   'to rotation, reflection and relabelling' % len(rec), worst_val < 1e-8 and worst_sep < 1e-6,
   'worst relative gap %.1e, worst separation gap %.1e' % (worst_val, worst_sep))
# An ADMISSIBLE configuration inside the region, in exact rationals: the region is not all
# degenerate, which is why the floor is a valid bound even though the family attaining it is not.
U = [(Fraction(1), Fraction(0)), (Fraction(3, 5), Fraction(4, 5)),
     (Fraction(-5, 13), Fraction(12, 13)), (Fraction(-7, 25), Fraction(-24, 25))]
Q5 = [(Fraction(0), Fraction(0))] + [(U[i][0] + U[j][0], U[i][1] + U[j][1])
                                      for i, j in ((0, 1), (0, 2), (1, 3), (2, 3))]
angs = [math.atan2(float(y), float(x)) % (2 * math.pi) for x, y in U]
min_sep = min(min(abs(angs[i] - angs[j]), 2 * math.pi - abs(angs[i] - angs[j]))
              for i in range(4) for j in range(i + 1, 4))


def cr(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def conc4(ps):
    return sp.Matrix([[x, y, x * x + y * y, 1] for x, y in ps]).det() == 0


ck('region_admissible', 'the region is not all degenerate: an exact rational configuration with centre '
   'separation above 0.35 is admissible (distinct points, no collinear triple, no four concyclic)',
   min_sep > 0.35 and len(set(Q5)) == 5
   and not any(cr(*[Q5[i] for i in t]) == 0 for t in combinations(range(5), 3))
   and not any(conc4([Q5[i] for i in qd]) for qd in combinations(range(5), 4)),
   'minimum centre separation %.3f' % min_sep)
note('these checks cover the family and its closed form; they do not show that the family is the')
note('GLOBAL minimiser of max(|f1|,|f2|), and NOTE.md says that is shown nowhere.')

print()
print('=' * 78)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL %d CHECKS PASSED' % len(PASSED))
print('=' * 78)
