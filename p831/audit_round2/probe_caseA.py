"""ROUND-2 PROBE 3.  Is caseA2's control ladder sound?

(i)  the reported ladder floors are NOT monotone in the number of equations, which is
     impossible for true minima over a fixed feasible set -> they are not minima.
(ii) re-run the ladder with far more restarts, and with the guards switched off, to see
     whether 2 and 3 equations are solvable and where their roots sit relative to the
     guard margins.
(iii) measure the fraction of restarts thrown away by solve()'s post-hoc `continue`.
"""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, os, json, itertools
import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
PAIRS = list(itertools.combinations(range(4), 2))


def config(v):
    cx, cy, px, py = v
    return np.array([[0.0, 0.0], [1.0, 0.0], [cx, cy],
                     [cx, cx * (1.0 - cx) / cy], [px, py]])


def r2S(X, Y, Z):
    a2 = ((Y - Z) ** 2).sum(); b2 = ((Z - X) ** 2).sum(); c2 = ((X - Y) ** 2).sum()
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    return (a2 * b2 * c2 / S if abs(S) > 1e-300 else np.nan), S


def six(v):
    p = config(v)
    return np.array([r2S(p[4], p[i], p[j])[0] for i, j in PAIRS]), p


def det4(p, q):
    return np.linalg.det(np.array([[p[t, 0] ** 2 + p[t, 1] ** 2, p[t, 0], p[t, 1], 1.0] for t in q]))


def marg(v):
    p = config(v)
    if not np.all(np.isfinite(p)):
        return None
    mind = min(np.linalg.norm(p[i] - p[j]) for i, j in itertools.combinations(range(5), 2))
    minS = min(abs(r2S(p[a], p[b], p[c])[1]) for a, b, c in itertools.combinations(range(5), 3))
    scale = float(np.mean(np.abs(p))) + 1.0
    mdet = min(abs(det4(p, q)) / scale ** 3 for q in itertools.combinations(range(5), 4))
    return dict(min_dist=float(mind), min_16K2=float(minS), min_det4=float(mdet), scale=scale)


def eqs_val(v, eqs):
    r, _ = six(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return None
    return np.array([(r[a] - r[b]) / (abs(r[a]) + abs(r[b])) for a, b in eqs])


def resid(v, eqs, guard, mind, conc):
    e = eqs_val(v, eqs)
    if e is None:
        return np.full(len(eqs) + 4, 1e3)
    if not guard:
        return np.concatenate([e, np.zeros(4)])
    m = marg(v)
    if m is None:
        return np.full(len(eqs) + 4, 1e3)
    g = [0.0 if m['min_dist'] > mind else (mind - m['min_dist']) * 1e2,
         0.0 if m['min_16K2'] > 1e-8 else (1e-8 - m['min_16K2']) * 1e4,
         0.0 if m['min_det4'] > conc else (conc - m['min_det4']) * 1e3,
         0.0 if m['scale'] < 40 else (m['scale'] - 40) * 1e-2]
    return np.concatenate([e, g])


def solve(eqs, restarts, rng, guard=True, mind=1e-2, conc=1e-4, reject=True):
    best = (np.inf, None); acc = 0; tried = 0
    for _ in range(restarts):
        v0 = np.array([rng.uniform(-1.5, 2.5), rng.uniform(0.15, 2.5),
                       rng.uniform(-3, 4), rng.uniform(-3, 4)])
        try:
            s = least_squares(resid, v0, args=(eqs, guard, mind, conc),
                              xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=4000)
        except Exception:
            continue
        tried += 1
        e = eqs_val(s.x, eqs)
        if e is None:
            continue
        c = float(np.max(np.abs(e)))
        m = marg(s.x)
        if reject and (m is None or m['min_dist'] < mind * 0.99 or m['min_det4'] < conc * 0.99):
            continue
        acc += 1
        if c < best[0]:
            best = (c, s.x.copy())
    return best[0], best[1], acc, tried


def splits():
    out = []; seen = set()
    for mask in range(1, 1 << 6):
        c0 = [i for i in range(6) if mask >> i & 1]
        c1 = [i for i in range(6) if not mask >> i & 1]
        if not c1: continue
        if tuple(sorted([len(c0), len(c1)], reverse=True)) not in ((4, 2), (3, 3)): continue
        key = tuple(sorted([tuple(c0), tuple(c1)]))
        if key in seen: continue
        seen.add(key)
        bad = False
        for X in range(4):
            idx = [t for t, (i, j) in enumerate(PAIRS) if i == X or j == X]
            for cl in (c0, c1):
                if len([t for t in idx if t in cl]) > 2: bad = True
        if not bad: out.append((c0, c1))
    return out


def eqs_of(c0, c1):
    return [(cl[0], t) for cl in (c0, c1) for t in cl[1:]]


if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    S = splits()
    print('admissible splits: %d' % len(S))
    art = json.load(open('results/caseA2.json'))
    print()
    print('(i) MONOTONICITY OF THE RECORDED LADDER  (min over a FIXED feasible set of')
    print('    max|e_1..e_k| must be non-decreasing in k)')
    for row in art['ladder']:
        f = row['floors']
        bad = [k for k in range(3) if f[k + 1] < f[k] * 0.99]
        print('    %-22s %s   violations at k->k+1: %s'
              % (str(row['split']), ['%.2e' % x for x in f], [ (k+1,k+2) for k in bad ] or 'none'))
    print()
    print('(ii) RE-RUN the ladder, %d restarts, guards ON (same margins as caseA2)' % R)
    rng = np.random.default_rng(11223344)
    print('     split                 1eq        2eq        3eq        4eq      acc%(4eq)')
    for c0, c1 in S[:4]:
        eqs = eqs_of(c0, c1); row = []; accs = None
        for k in range(1, 5):
            c, v, a, t = solve(eqs[:k], R, rng)
            row.append(c)
            if k == 4: accs = (a, t)
        print('     %-20s' % (str(c0) + '|' + str(c1)) + ''.join('  %.2e' % x for x in row)
              + '   %d/%d' % accs)
    print()
    print('(iii) SAME LADDER WITH THE GUARDS OFF (pure equations, no rejection)')
    rng = np.random.default_rng(11223344)
    print('     split                 1eq        2eq        3eq        4eq   | margins of the 3eq root')
    for c0, c1 in S[:4]:
        eqs = eqs_of(c0, c1); row = []; m3 = None
        for k in range(1, 5):
            c, v, a, t = solve(eqs[:k], R, rng, guard=False, reject=False)
            row.append(c)
            if k == 3 and v is not None: m3 = marg(v)
        print('     %-20s' % (str(c0) + '|' + str(c1)) + ''.join('  %.2e' % x for x in row)
              + '  | mind=%.2e det=%.2e 16K2=%.2e' % (m3['min_dist'], m3['min_det4'], m3['min_16K2']))
    print()
    print('(iv) DO 3-EQUATION ROOTS EXIST OUTSIDE THE GUARDS?  collect every root with')
    print('     max|e|<1e-10 from %d restarts, guards off, and histogram their margins' % (R * 3))
    rng = np.random.default_rng(777)
    for c0, c1 in S[:2]:
        eqs = eqs_of(c0, c1)[:3]
        roots = []
        for _ in range(R * 3):
            v0 = np.array([rng.uniform(-1.5, 2.5), rng.uniform(0.15, 2.5),
                           rng.uniform(-3, 4), rng.uniform(-3, 4)])
            try:
                s = least_squares(resid, v0, args=(eqs, False, 1e-2, 1e-4),
                                  xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=4000)
            except Exception:
                continue
            e = eqs_val(s.x, eqs)
            if e is None: continue
            if np.max(np.abs(e)) < 1e-10:
                m = marg(s.x)
                if m: roots.append(m)
        if not roots:
            print('     %-20s NO roots at all' % (str(c0) + '|' + str(c1)))
            continue
        md = np.array([r['min_dist'] for r in roots]); dd = np.array([r['min_det4'] for r in roots])
        sc = np.array([r['scale'] for r in roots])
        print('     %-20s %d roots.  min_dist: max %.3e  (guard 1e-2, %d pass)'
              % (str(c0) + '|' + str(c1), len(roots), md.max(), int((md > 1e-2).sum())))
        print('       %20s min_det4: max %.3e  (guard 1e-4, %d pass)   scale<40: %d'
              % ('', dd.max(), int((dd > 1e-4).sum()), int((sc < 40).sum())))
        both = int(((md > 1e-2) & (dd > 1e-4) & (sc < 40)).sum())
        print('       %20s roots passing ALL guards: %d' % ('', both))
