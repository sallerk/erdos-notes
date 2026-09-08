"""Independent re-derivation of every numerical claim in NOTE.md.

This file imports NOTHING from the directory it audits.  Every construction is rebuilt
from the mathematical description (a paper's words, or the definition of delta), every
enumeration is re-implemented, and the only things read from `results/` are artifacts
whose CONTENT is then re-checked from the stored coordinates.

The lattice enumerator here is deliberately built differently from lat.py: it works in
the Eisenstein integers Z[w], w = exp(i pi / 3), where the similarity maps of the
triangular lattice into itself are exactly z -> a z + b and z -> a conj(z) + b with a a
nonzero Eisenstein integer.  Dividing a set of differences by their gcd (Z[w] is
Euclidean) makes it primitive, after which only the six units and conjugation remain.
That reduction is COMPLETE, unlike lat.py's, which divides only by the fixed scalings of
norm 3, 4, 7, 13 and 25; if lat.py over-counted, this file reports fewer classes.

Usage: python AUDIT_RECHECK.py
"""
import sys
import json
import time
from itertools import combinations, permutations, product

import mpmath as mp
import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
mp.mp.dps = 50
TOL = mp.mpf('1e-35')

FAIL = []
N = [0]


def ck(label, ok, detail=''):
    N[0] += 1
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''), flush=True)
    if not ok:
        FAIL.append(label)


# ----------------------------------------------------------------- delta, from scratch
def dvals(pts, tol=TOL):
    """the distinct distances, largest last"""
    vals = []
    for (ax, ay), (bx, by) in combinations(pts, 2):
        d = mp.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
        if d < tol:
            raise ValueError('two points coincide')
        if not any(abs(d - v) < tol for v in vals):
            vals.append(d)
    return sorted(vals)


def delta(pts):
    v = dvals(pts)
    if len(v) == 1:
        return mp.mpf(1)
    gaps = [b - a for a, b in zip(v, v[1:])]
    return v[-1] / min([v[0]] + gaps)


def near(x, y, eps='1e-9'):
    return abs(mp.mpf(x) - mp.mpf(y)) < mp.mpf(eps)


def R(n, r=1, phase=0):
    return [(r * mp.cos(2 * mp.pi * i / n + phase), r * mp.sin(2 * mp.pi * i / n + phase))
            for i in range(n)]


print('=' * 78)
print('INDEPENDENT RE-DERIVATION FOR p100  (shares no code with the directory)')
print('=' * 78)

# ------------------------------------------------------------------ 1. n = 4 and n = 5
print()
print('1. The six 4-point 2-distance sets, each built from its own geometry')
s2, s3, s5 = mp.sqrt(2), mp.sqrt(3), mp.sqrt(5)
tau = (1 + s5) / 2
sets4 = {}
sets4['square'] = [(0, 0), (1, 0), (1, 1), (0, 1)]
sets4['60-degree rhombus'] = [(0, 0), (1, 0), (mp.mpf('0.5'), s3 / 2), (mp.mpf('0.5'), -s3 / 2)]
sets4['equilateral triangle + centre'] = R(3) + [(mp.mpf(0), mp.mpf(0))]
sets4['regular pentagon minus a vertex'] = R(5)[:4]
# The two 4-point sets whose distance ratio is 2cos(15 degrees).  On four vertices the
# short-edge graph can only be a star-plus-edge or a path, and both occur:
#   (i) A at the origin with AB = AC = AD = 1 and CD = 1, taking B, C, D on the unit
#       circle at 0, 150 and -150 degrees; then BC = BD = 2cos(15 deg).  Four short, two
#       long.
#   (ii) an equilateral triangle ACD of side 1 with B on the axis of AC at equal distances
#       from A and C and at distance 1 from D; solving |BD| = 1 puts B at height
#       sqrt3/2 - 1, and then BA = BC = 2sin(15 deg).  Two short, four long.
ang150 = mp.mpf(150) * mp.pi / 180
sets4['kite, four short pairs'] = [(mp.mpf(0), mp.mpf(0)), (mp.mpf(1), mp.mpf(0)),
                                   (mp.cos(ang150), mp.sin(ang150)),
                                   (mp.cos(-ang150), mp.sin(-ang150))]
sets4['kite, two short pairs'] = [(-mp.mpf(1) / 2, mp.mpf(0)), (mp.mpf(1) / 2, mp.mpf(0)),
                                  (mp.mpf(0), s3 / 2), (mp.mpf(0), s3 / 2 - 1)]
for name, sgn in ():
    # three points of an isosceles triangle with legs 1 and apex angle 150 degrees,
    # plus the reflection of the apex in the base's perpendicular bisector (sgn = 1) or
    # the fourth point of the rhombus it spans (sgn = -1)
    ang = mp.mpf(150) * mp.pi / 180
    A = (mp.mpf(0), mp.mpf(0))
    B = (mp.mpf(1), mp.mpf(0))
    C = (mp.cos(ang), mp.sin(ang))
    D = (B[0] + C[0] - A[0], B[1] + C[1] - A[1]) if sgn > 0 else \
        (mp.cos(-ang), mp.sin(-ang))
    sets4[name] = [A, B, C, D]
rows4 = {}
for name, pts in sets4.items():
    v = dvals(pts)
    rows4[name] = (len(v), delta(pts), v[-1] / v[0])
    print('   %-32s k=%d  ratio %-12s delta %s'
          % (name, len(v), mp.nstr(v[-1] / v[0], 10), mp.nstr(delta(pts), 12)))
ck('all six are 2-distance sets', all(r[0] == 2 for r in rows4.values()))
best4 = min(r[1] for r in rows4.values())
ck('delta(4) = 2.0731321850 = (sqrt6+sqrt2)/(sqrt6+sqrt2-2)',
   near(best4, 2.0731321849709861) and
   near((mp.sqrt(6) + s2) / (mp.sqrt(6) + s2 - 2), 2.0731321849709861),
   'min over the six = %s' % mp.nstr(best4, 12))
ck('the minimum is attained by a set whose distance ratio is 2cos(15 degrees)',
   near(min(rows4.items(), key=lambda t: t[1][1])[1][2], 2 * mp.cos(mp.pi / 12)))
ck('delta(5) = phi^2 = (3+sqrt5)/2 for the regular pentagon',
   near(delta(R(5)), (3 + s5) / 2) and near((3 + s5) / 2, tau ** 2),
   mp.nstr(delta(R(5)), 12))

# ------------------------------------------------------- 2. the pattern counts, re-done
print()
print('2. The number of canonical colourings of the pairs (own brute force)')


def canon_count(n, k):
    pairs = list(combinations(range(n), 2))
    idx = {p: i for i, p in enumerate(pairs)}
    seen = set()
    for lab in product(range(k), repeat=len(pairs)):
        if len(set(lab)) != k:
            continue
        best = None
        for perm in permutations(range(n)):
            m, rg = {}, []
            for a, b in pairs:
                c = lab[idx[tuple(sorted((perm[a], perm[b])))]]
                if c not in m:
                    m[c] = len(m)
                rg.append(m[c])
            t = tuple(rg)
            if best is None or t < best:
                best = t
        seen.add(best)
    return len(seen)


for n, k, want in ((4, 2, 5), (5, 2, 17), (5, 3, 124)):
    got = canon_count(n, k)
    ck('K%d with %d colours: %d canonical patterns' % (n, k, want), got == want, 'found %d' % got)

# -------------------------------------------------- 3. Piepmeyer from Erdos's sentence
print()
print("3. Piepmeyer's set, rebuilt from the words in [Er95]")
x = (1 + sp.sqrt(2)) * sp.sqrt(2 - sp.sqrt(3))
r_in = x / sp.sqrt(3)                       # circumradius of an equilateral triangle of side x
r_out = r_in + x                            # "distances x between corresponding vertices"
ang = [sp.pi / 2 + 2 * sp.pi * i / 3 for i in range(3)]
inner = [(sp.simplify(r_in * sp.cos(a)), sp.simplify(r_in * sp.sin(a))) for a in ang]
outer = [(sp.simplify(r_out * sp.cos(a)), sp.simplify(r_out * sp.sin(a))) for a in ang]


def circumcentre(A, B, C):
    ax, ay = A; bx, by = B; cx, cy = C
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    a2, b2, c2 = ax ** 2 + ay ** 2, bx ** 2 + by ** 2, cx ** 2 + cy ** 2
    return (sp.simplify((a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d),
            sp.simplify((a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d))


extra, concyclic = [], True
for i, j in ((0, 1), (1, 2), (2, 0)):
    quad = [inner[i], inner[j], outer[i], outer[j]]
    c = circumcentre(quad[0], quad[1], quad[2])
    r2 = sp.simplify((c[0] - quad[0][0]) ** 2 + (c[1] - quad[0][1]) ** 2)
    for q in quad[1:]:
        if sp.simplify((c[0] - q[0]) ** 2 + (c[1] - q[1]) ** 2 - r2) != 0:
            concyclic = False
    extra.append(c)
PIEP = [(mp.mpf(str(sp.N(a, 60))), mp.mpf(str(sp.N(b, 60)))) for a, b in inner + outer + extra]
vp = dvals(PIEP)
ck('the four endpoints of each pair of parallel sides really are concyclic', concyclic)
ck('the 9 points have exactly 4 distinct distances', len(vp) == 4, 'found %d' % len(vp))
ck('the middle gap is exactly 1', near(vp[2] - vp[1], 1, '1e-40'), mp.nstr(vp[2] - vp[1], 25))
ck('delta = 4.6639024601, the binding constraint being that middle gap',
   near(delta(PIEP), '4.66390246014701') and
   min([vp[0]] + [b - a for a, b in zip(vp, vp[1:])]) == vp[2] - vp[1])
ck('delta(9) closed forms agree: (2+sqrt3)/(1+sqrt3-sqrt(2+sqrt3)) = sqrt(6+3sqrt3+4sqrt2+2sqrt6)',
   near((2 + s3) / (1 + s3 - mp.sqrt(2 + s3)), delta(PIEP), '1e-40') and
   near(mp.sqrt(6 + 3 * s3 + 4 * s2 + 2 * mp.sqrt(6)), delta(PIEP), '1e-40'))

# ------------------------------- 4. the Erdos-Fishburn three-triangle set, radii derived
print()
print('4. The Erdos-Fishburn "three equilateral triangles with the same center"')
print('   Radii DERIVED here from their distance rules, not copied from e9.py:')
print('   big side = big vertex to farthest intermediate vertex  =>  r_mid = (sqrt3-1) r_big;')
print('   inner side = inner vertex to nearest intermediate vertex  =>  r_in = (2-sqrt3) r_big.')
rb = mp.mpf(1)
rm = s3 - 1
ri = 2 - s3
ck('r_mid solves sqrt3 r_big = r_big + r_mid', near(s3 * rb, rb + rm, '1e-40'))
ck('r_in solves sqrt3 r_in = r_mid - r_in', near(s3 * ri, rm - ri, '1e-40'))
big = R(3, rb, mp.pi / 2)
mid = R(3, rm, -mp.pi / 2)
inn = R(3, ri, -mp.pi / 2)
EF = big + mid + inn
ve = dvals(EF)
ck('the 9 points have exactly 4 distinct distances', len(ve) == 4, 'found %d' % len(ve))
ratios = [v / ve[0] for v in ve]
ck('ratios are 1 : sqrt(2+sqrt3) : 1+sqrt3 : 2+sqrt3',
   near(ratios[1], mp.sqrt(2 + s3)) and near(ratios[2], 1 + s3) and near(ratios[3], 2 + s3),
   ' '.join(mp.nstr(r, 10) for r in ratios))
ck('the second distance is the side of a square whose diagonal is the third',
   near(ve[1] * s2, ve[2], '1e-30'))
ck('delta equals Piepmeyer\'s delta', near(delta(EF), delta(PIEP), '1e-30'))
mp_ef = sorted(mp.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) for a, b in combinations(EF, 2))
mp_pp = sorted(mp.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) for a, b in combinations(PIEP, 2))
sc = mp_pp[0] / mp_ef[0]
ck('the two 36-element distance multisets agree exactly up to the scale %s' % mp.nstr(sc, 12),
   all(abs(a * sc - b) < mp.mpf('1e-30') for a, b in zip(mp_ef, mp_pp)))

# ----------------------------------------------------------- 5. the polygon families
print()
print('5. Regular-polygon families')
POLY = {'R7': (R(7), '5.04891733952230'), 'R6+centre': (R(6) + [(mp.mpf(0), mp.mpf(0))], '7.46410161513775'),
        'R8': (R(8), mp.nstr(mp.mpf(2) / (2 - mp.sqrt(2 + s2)), 15)),
        'R9': (R(9), '8.29085936938105'),
        'R9+centre': (R(9) + [(mp.mpf(0), mp.mpf(0))], '8.29085936938105'),
        'R10': (R(10), '20.4317290945415'), 'R11': (R(11), '12.3435375196652'),
        'R11 minus a vertex': (R(11)[:10], '12.3435375196652'),
        'R7+centre minus a vertex': (R(7)[:6] + [(mp.mpf(0), mp.mpf(0))], '14.7456601321617'),
        'R8 minus a vertex': (R(8)[:7], mp.nstr(mp.mpf(2) / (2 - mp.sqrt(2 + s2)), 15))}
for name, (pts, want) in POLY.items():
    d = delta(pts)
    ck('%-26s delta = %s' % (name, want[:14]), near(d, want, '1e-10'), mp.nstr(d, 15))
ck('R7 and R6+centre, the only 7-point 3-distance sets, are both above 4.6639',
   delta(R(7)) > mp.mpf('4.664') and delta(R(6) + [(mp.mpf(0), mp.mpf(0))]) > mp.mpf('4.664'))

# ------------------------------------------------- 6. other explicit sets used in e78
print()
print('6. The other explicit few-distance sets')
h = s3 / 2
SQA = [(mp.mpf(0), mp.mpf(0)), (mp.mpf(1), mp.mpf(0)), (mp.mpf(1), mp.mpf(1)), (mp.mpf(0), mp.mpf(1)),
       (mp.mpf('0.5'), -h), (1 + h, mp.mpf('0.5')), (mp.mpf('0.5'), 1 + h), (-h, mp.mpf('0.5'))]
PENTAGRAM = R(5) + R(5, 1 / tau ** 2, mp.pi / 5)
GRID = [(mp.mpf(a), mp.mpf(b)) for a, b in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2))]
ck('square with four equilateral apexes: 4 distances, delta 6.5957541131',
   len(dvals(SQA)) == 4 and near(delta(SQA), '6.59575411272515', '1e-10'), mp.nstr(delta(SQA), 15))
ck('pentagon with its five diagonal intersections: 5 distances, delta 9.2158645473',
   len(dvals(PENTAGRAM)) == 5 and near(delta(PENTAGRAM), '9.21586454726535', '1e-10'),
   mp.nstr(delta(PENTAGRAM), 15))
ck('2x3 grid plus one point: 4 distances in ratio 1 : sqrt2 : 2 : sqrt5, delta 9.4721359550',
   len(dvals(GRID)) == 4 and near(delta(GRID), '9.47213595499958', '1e-10'), mp.nstr(delta(GRID), 15))

# ------------------------------------- 7. lattice enumeration in the Eisenstein integers
print()
print('7. Lattice few-distance sets, re-enumerated over Z[w] (complete similarity reduction)')


def emul(u, v):
    a, b = u; c, d = v
    return (a * c - b * d, a * d + b * c + b * d)


def econj(u):
    a, b = u
    return (a + b, -b)


def enorm(u):
    a, b = u
    return a * a + a * b + b * b


def esub(u, v):
    return (u[0] - v[0], u[1] - v[1])


def ediv(u, v):
    """nearest-integer quotient and remainder in Z[w]; N(remainder) < N(v)"""
    p, q = emul(u, econj(v))
    n = enorm(v)
    quo = ((2 * p + n) // (2 * n), (2 * q + n) // (2 * n))
    return quo, esub(u, emul(quo, v))


def egcd(items):
    g = (0, 0)
    for it in items:
        a, b = g, it
        while b != (0, 0):
            a, b = b, ediv(a, b)[1]
        g = a
    return g


# the six units of Z[w] are the powers of w; since w^2 = w - 1 they are
# 1, w, w-1, -1, -w, 1-w
UNITS = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
assert all(enorm(u) == 1 for u in UNITS)
assert sorted(enorm(emul(u, (3, 5))) for u in UNITS) == [enorm((3, 5))] * 6


def ecanon(pts):
    """canonical form under translation, the six units, and conjugation"""
    best = None
    for conj in (False, True):
        P = [econj(p) for p in pts] if conj else list(pts)
        for u in UNITS:
            im = [emul(u, p) for p in P]
            m = min(im, key=lambda p: (p[1], p[0]))
            t = tuple(sorted(esub(p, m) for p in im))
            if best is None or t < best:
                best = t
    return best


def eprimitive(pts):
    base = pts[0]
    diffs = [esub(p, base) for p in pts]
    g = egcd([d for d in diffs if d != (0, 0)])
    if g == (0, 0):
        return ecanon(pts)
    red = []
    for d in diffs:
        q, r = ediv(d, g)
        assert r == (0, 0), 'gcd did not divide a difference'
        red.append(q)
    return ecanon(red)


def lat_enum(n, k, D2):
    patch = [(a, b) for a in range(-D2, D2 + 1) for b in range(-D2, D2 + 1)
             if 0 < enorm((a, b)) <= D2 and (b > 0 or (b == 0 and a > 0))]
    patch.sort(key=lambda p: (p[1], p[0]))
    found = {}
    def rec(chosen, ds, start):
        if len(chosen) == n:
            if len(ds) == k:
                found.setdefault(eprimitive(chosen), list(chosen))
            return
        for i in range(start, len(patch)):
            p = patch[i]
            nd, ok = set(ds), True
            for r in chosen:
                q = enorm(esub(p, r))
                if q > D2:
                    ok = False; break
                nd.add(q)
                if len(nd) > k:
                    ok = False; break
            if ok:
                rec(chosen + [p], nd, i + 1)
    rec([(0, 0)], set(), 0)
    return found


# A lattice set with k distances has them among 1, sqrt3, 2, sqrt7, 3, 2sqrt3, ...; the
# binding constraint in every case below is the gap 2 - sqrt3, so the expected delta is
# d_k (2 + sqrt3).  These closed forms are derived here, not copied.
EXPECT = {(7, 4): (20, mp.sqrt(7) * (2 + s3)), (8, 4): (8, mp.sqrt(7) * (2 + s3)),
          (9, 4): (2, mp.sqrt(7) * (2 + s3)), (10, 5): (15, 3 * (2 + s3)),
          (11, 5): (3, 3 * (2 + s3)), (12, 5): (1, 3 * (2 + s3)),
          (13, 6): (1, 2 * s3 * (2 + s3))}
for (n, k), (want, wd) in EXPECT.items():
    t0 = time.time()
    got = lat_enum(n, k, 100)
    ds = []
    for pts in got.values():
        P = [(mp.mpf(a) + mp.mpf(b) / 2, mp.mpf(b) * s3 / 2) for a, b in pts]
        ds.append(delta(P))
    ck('lattice n=%d k=%d : %d similarity classes, every one with delta = %s'
       % (n, k, want, mp.nstr(wd, 15)),
       len(got) == want and all(near(d, wd, '1e-25') for d in ds),
       'found %d classes, deltas %s (%.0fs)'
       % (len(got), sorted({mp.nstr(d, 15) for d in ds}), time.time() - t0))

# ------------------------------------------------------- 8. the stored classification
print()
print('8. Re-checking the stored artifacts from their own coordinates')
PIEP_RATIOS = [mp.mpf(1), mp.sqrt(2 + s3), 1 + s3, 2 + s3]


def load(fn):
    try:
        return json.load(open(fn))
    except FileNotFoundError:
        ck('artifact %s exists' % fn, False)
        return None


e78 = load('results/e78_k4.json')
if e78:
    for tag in ('E7', 'E8'):
        bad = 0
        best = None
        att = []
        for r in e78[tag]:
            P = [(mp.mpf(a), mp.mpf(b)) for a, b in r['points']]
            v = dvals(P)
            d = delta(P)
            if len(v) != 4 or not near(d, r['delta'], '1e-15'):
                bad += 1
            if best is None or d < best:
                best = d
            att.append((d, [vv / v[0] for vv in v]))
        ck('%s: every stored set rebuilt from its coordinates has 4 distances and the stored delta'
           % tag, bad == 0, '%d mismatches out of %d' % (bad, len(e78[tag])))
        ck('%s: the minimum is 4.6639024601' % tag, near(best, '4.66390246014701', '1e-12'),
           mp.nstr(best, 15))
        only = all(all(near(a, b, '1e-20') for a, b in zip(rat, PIEP_RATIOS))
                   for d, rat in att if near(d, best, '1e-20'))
        ck('%s: the minimum is attained only by sets with Piepmeyer\'s distance ratios' % tag, only)
    ck('E_7(4): 42 sets, matching Lan-Wei Theorem 8', e78['E7_classes'] == 42,
       'stored %d' % e78['E7_classes'])
    ck('E_8(4): 15 sets, the count implied by Shinohara Theorem 1.2(a)', e78['E8_classes'] == 15)

e9 = load('results/e9_k4.json')
if e9:
    got = sorted(round(float(v['delta_num']), 6) for v in e9['sets'].values())
    ck('E_9(4): the four sets have delta 4.663902, 8.290859, 9.874078, 9.874078',
       got == [4.663902, 8.290859, 9.874078, 9.874078], str(got))

for fn, want_n, want_k, want_min in (('results/e6_k3.json', 9, 3, '3.41421356237310'),
                                     ('results/e7_k3.json', 2, 3, '5.04891733952230')):
    d = load(fn)
    if d:
        bad = 0
        for r in d['sets']:
            P = [(mp.mpf(a), mp.mpf(b)) for a, b in r['points']]
            if len(dvals(P)) != 3 or not near(delta(P), r['delta'], '1e-15'):
                bad += 1
        ck('%s: %d sets, each with 3 distances and the stored delta' % (fn, want_n),
           len(d['sets']) == want_n and bad == 0, '%d sets, %d mismatches' % (len(d['sets']), bad))
        mn = min(mp.mpf(r['delta']) for r in d['sets'])
        ck('%s: minimum delta = %s' % (fn, want_min[:14]), near(mn, want_min, '1e-12'),
           mp.nstr(mn, 15))
ck('delta(6) = 2+sqrt2 exactly', near(mp.mpf('3.41421356237310'), 2 + s2, '1e-12'))

# ------------------------------------------------- 9. two patterns re-decided from scratch
print()
print('9. Two 5-point 2-distance patterns re-decided with an independent Groebner setup')


def decide(labels):
    """own polynomial system: p0 = (0,0), p1 = (1,0), one squared value per class, and a
    saturation variable forcing every class value to be nonzero"""
    pairs = list(combinations(range(5), 2))
    P = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
    var = []
    for i in range(2, 5):
        u, w = sp.symbols('u%d w%d' % (i, i))
        P[i] = (u, w)
        var += [u, w]
    c01 = labels[pairs.index((0, 1))]
    val = {}
    for c in set(labels):
        val[c] = sp.Integer(1) if c == c01 else sp.Symbol('m%d' % c)
        if c != c01:
            var.append(val[c])
    z = sp.Symbol('z')
    var.append(z)
    eqs, prod = [], sp.Integer(1)
    for (a, b), c in zip(pairs, labels):
        if (a, b) == (0, 1):
            continue
        eqs.append(sp.expand((P[a][0] - P[b][0]) ** 2 + (P[a][1] - P[b][1]) ** 2 - val[c]))
    for c in set(labels):
        if c != c01:
            prod *= val[c]
    eqs.append(sp.expand(z * prod - 1))
    G = sp.groebner(eqs, *var, order='grevlex')
    return list(G.exprs) == [sp.Integer(1)]


pent = []
pairs5 = list(combinations(range(5), 2))
for a, b in pairs5:
    pent.append(0 if (b - a) % 5 in (1, 4) else 1)
ck('the regular-pentagon pattern is REALISABLE', not decide(pent))
# a 5-point pattern with a vertex meeting four pairs of the same class: that vertex would
# have four points on a circle about it at one radius and none at the other, and the four
# would then need to realise a 2-distance set with one distance missing
star = []
for a, b in pairs5:
    star.append(0 if a == 0 else 1)
ck('the "one vertex sees a single distance, the other four another" pattern is UNREALISABLE',
   decide(star))

print()
print('=' * 78)
print('%d checks, %d failed' % (N[0], len(FAIL)))
for f in FAIL:
    print('  FAILED:', f)
print('=' * 78)
sys.exit(1 if FAIL else 0)
