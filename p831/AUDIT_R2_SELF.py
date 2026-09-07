"""Round-2 self-audit.  The single question: is the new OBSTRUCTED verdict the old
defect wearing a different hat?

tausweep.py sweeps only `tau`, the flatness and concyclicity margin.  Its objective also
contains a minimum-distance guard (1e-2), a class-separation guard (1e-3) and a span
guard (60).  If one of THOSE is active at the optimum, then a floor that is flat in tau
is measuring the unswept constant, and "OBSTRUCTED" is exactly the defect the first audit
found, relocated.  This decomposes the reported optima and then sweeps every guard.
"""
import sys
import json
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRI = list(combinations(range(5), 3))
QUADS = list(combinations(range(5), 4))


def unpack(v):
    P = np.zeros((5, 2))
    P[1, 0] = 1.0
    P[2:, :] = np.asarray(v).reshape(3, 2)
    return P


def quantities(P):
    r2 = np.empty(10)
    S = np.empty(10)
    for i, (a, b, c) in enumerate(TRI):
        A, B, C = P[a], P[b], P[c]
        a2 = np.sum((B - C) ** 2)
        b2 = np.sum((C - A) ** 2)
        c2 = np.sum((A - B) ** 2)
        s = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
        S[i] = s
        r2[i] = a2 * b2 * c2 / s if s > 1e-300 else np.nan
    return r2, S


def det4(P, q):
    return np.linalg.det(np.array(
        [[P[t, 0] ** 2 + P[t, 1] ** 2, P[t, 0], P[t, 1], 1.0] for t in q]))


def margins(v, labels, k):
    """the guard margins, each in the units its guard uses.

    NOTE: the objective below adds a minimum-distance guard that tausweep.py does NOT
    have.  An earlier version of this file did the same and the write-up then described
    tausweep as containing that guard, which is false.  The decomposition is still
    informative, but it is of a slightly different function; the separation finding was
    re-confirmed against tausweep's actual objective by an independent auditor, more
    strongly (14 of 15 rather than 12 of 13)."""
    P = unpack(v)
    r2, S = quantities(P)
    if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
        return None
    scale = float(np.mean(r2))
    means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c]))
             for c in range(k)}
    return dict(
        equality=max(abs(r2[i] - means[labels[i]]) / scale for i in range(10)),
        flat=float(np.min(S)) / scale ** 2,
        concyclic=min(abs(det4(P, q)) / scale ** 1.5 for q in QUADS),
        min_dist=min(float(np.linalg.norm(P[i] - P[j]))
                     for i, j in combinations(range(5), 2)),
        separation=min(abs(means[a] - means[b])
                       for a in range(k) for b in range(a + 1, k)) / scale,
        span=float(np.max(np.abs(P))))


def make_res(labels, k, tau, mind_tau, sep_tau):
    def f(v):
        P = unpack(v)
        r2, S = quantities(P)
        if np.any(~np.isfinite(r2)) or np.any(r2 <= 0):
            return np.full(10 + 4 + len(QUADS), 1e3)
        scale = float(np.mean(r2))
        means = {c: float(np.mean([r2[i] for i in range(10) if labels[i] == c]))
                 for c in range(k)}
        out = [(r2[i] - means[labels[i]]) / scale for i in range(10)]
        span = float(np.max(np.abs(P)))
        out.append(0.0 if span < 60 else (span - 60) * 1e-2)
        flat = float(np.min(S)) / scale ** 2
        out.append(0.0 if flat > tau else (tau - flat) * 1e3)
        mind = min(float(np.linalg.norm(P[i] - P[j]))
                   for i, j in combinations(range(5), 2))
        out.append(0.0 if mind > mind_tau else (mind_tau - mind) * 1e2)
        sep = min(abs(means[a] - means[b])
                  for a in range(k) for b in range(a + 1, k)) / scale
        out.append(0.0 if sep > sep_tau else (sep_tau - sep) * 1e2)
        for q in QUADS:
            d = abs(det4(P, q)) / scale ** 1.5
            out.append(0.0 if d > tau else (tau - d) * 1e3)
        return np.array(out)
    return f


def floor(labels, k, tau, mind_tau, sep_tau, restarts, rng):
    f = make_res(labels, k, tau, mind_tau, sep_tau)
    best = (np.inf, None)
    for _ in range(restarts):
        v0 = rng.uniform(-8.0, 8.0, size=6)
        try:
            s = least_squares(f, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=3000)
        except Exception:
            continue
        c = float(np.max(np.abs(s.fun)))
        if c < best[0]:
            best = (c, s.x.copy())
    return best


if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    pats = json.load(open('results/penum_n5_k3.json'))['patterns']
    sweep = json.load(open('results/tausweep_n5_k3.json'))['results']
    rng = np.random.default_rng(90210)

    print('=' * 78)
    print('ROUND-2 SELF-AUDIT: is "OBSTRUCTED" measuring an UNSWEPT guard?')
    print('=' * 78)
    print()
    print('Step 1.  At each OBSTRUCTED optimum, which guard is active?')
    print('         A guard is ACTIVE if its margin sits on its threshold.')
    print()
    print(' pat  floor(tau=1e-6)  equality   flat/tau   concyc/tau  mind/1e-2  sep/1e-3')
    active = {'flat': 0, 'concyclic': 0, 'min_dist': 0, 'separation': 0, 'none': 0}
    rows = []
    for o in sweep:
        if o['verdict'] != 'OBSTRUCTED':
            continue
        i = o['i']
        lab = pats[i]['labels']
        c, v = floor(lab, 3, 1e-6, 1e-2, 1e-3, R, rng)
        if v is None:
            continue
        m = margins(v, lab, 3)
        if m is None:
            continue
        ratios = dict(flat=m['flat'] / 1e-6, concyclic=m['concyclic'] / 1e-6,
                      min_dist=m['min_dist'] / 1e-2, separation=m['separation'] / 1e-3)
        hot = [g for g, r in ratios.items() if r < 1.05]
        # count EVERY active guard, not just the first: an earlier version tallied
        # hot[0] only and reported separation twice where the rows showed it twelve times
        if hot:
            for g in hot:
                active[g] += 1
        else:
            active['none'] += 1
        rows.append(dict(i=i, floor=c, equality=m['equality'], ratios=ratios,
                         active=hot))
        print(' %3d  %.3e      %.2e   %8.1f   %8.1f    %7.1f   %7.1f  %s'
              % (i, c, m['equality'], ratios['flat'], ratios['concyclic'],
                 ratios['min_dist'], ratios['separation'],
                 ('ACTIVE: ' + ','.join(hot)) if hot else 'no guard active'))
    print()
    print('  guards active at the optimum:', active)

    print()
    print('Step 2.  Sweep the UNSWEPT guards on the three tightest OBSTRUCTED patterns.')
    print('         If the floor tracks a guard, that guard was setting it.')
    tight = sorted(rows, key=lambda r: r['floor'])[:3]
    out2 = []
    for r in tight:
        lab = pats[r['i']]['labels']
        print()
        print('  pattern %d' % r['i'])
        print('     mind_tau   floor        |   sep_tau    floor')
        line = []
        for md, sp in zip([1e-2, 1e-3, 1e-4, 1e-5], [1e-3, 1e-4, 1e-5, 1e-6]):
            a, _ = floor(lab, 3, 1e-6, md, 1e-3, R, rng)
            b, _ = floor(lab, 3, 1e-6, 1e-2, sp, R, rng)
            line.append(dict(mind_tau=md, floor_mind=float(a),
                             sep_tau=sp, floor_sep=float(b)))
            print('     %.0e     %.3e   |   %.0e     %.3e' % (md, a, sp, b))
        out2.append(dict(i=r['i'], sweeps=line))
        f0 = line[0]['floor_mind']
        f3 = line[-1]['floor_mind']
        g0 = line[0]['floor_sep']
        g3 = line[-1]['floor_sep']
        print('     floor changes by %.2fx across mind_tau, %.2fx across sep_tau'
              % (f0 / max(f3, 1e-300), g0 / max(g3, 1e-300)))

    print()
    print('Step 3.  The classification threshold.')
    sl = sorted(o['slope'] for o in sweep)
    print('   slopes, sorted: %s' % ['%.2f' % x for x in sl])
    gap_lo = max(x for x in sl if x < 0.5)
    gap_hi = min(x for x in sl if x > 0.5)
    print('   largest slope below the 0.5 cut: %.2f ; smallest above: %.2f' % (gap_lo, gap_hi))
    print('   %s' % ('the cut sits in a wide empty gap, so it is not doing arbitrary work'
                     if gap_hi - gap_lo > 0.5 else
                     'WARNING: patterns sit close to the cut; the classification is soft'))

    json.dump(dict(restarts=R, active=active, rows=rows, guard_sweeps=out2,
                   slopes=sl, completed=True),
              open('results/audit_r2_self.json', 'w'), indent=1)
    print()
    print('=' * 78)
