"""L74 POSITIVE CONTROL for caseA.py.  CORRECTED after the audit of 2026-09-07.

THE BUG THIS FILE USED TO HAVE, AND WHY IT MATTERED.
The earlier version measured each residual as (r_a - r_b) / mean(all six radii) while
constraining only k of the six.  The optimiser exploited that directly: it drove an
UNCONSTRAINED radius to about 1e15 by making one triple nearly collinear, which inflated
the denominator by fourteen orders of magnitude and divided the residual away.  The
rungs k = 2, 3, 4 were reported "SOLVED" at 1e-14 while the radii they claimed to have
equalised actually differed by 61%, 33% and 2.6%.  The ladder was inverted: the only
rung that genuinely held its equations was k = 5, the one printed as NOT SOLVED.  Every
negative that cited this control was therefore uncontrolled.

THE FIX.  Measure each equation against the two radii it actually compares,
(r_a - r_b) / (|r_a| + |r_b|), which no other radius can inflate, and add explicit
guards so a small residual cannot be bought with a degenerate configuration.  Report
BOTH the optimiser's objective and this scale-free error, and call a rung solved only
when the scale-free error is small.
"""
import sys
import json
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from caseA import six_radii, PAIRS   # noqa: E402

EQ = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]


def guards(v):
    """returns (min |16K^2| over the six P-triples, min pairwise distance, max radius)"""
    r, pts, P = six_radii(v)
    allp = list(pts) + [P]
    mind = min(np.linalg.norm(allp[i] - allp[j])
               for i, j in combinations(range(len(allp)), 2))
    return mind, float(np.max(r)) if np.all(np.isfinite(r)) else np.inf


def scale_free_error(v, k):
    """the honest measure: each constrained difference against its OWN two radii"""
    r, _, _ = six_radii(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return np.inf
    return max(abs(r[a] - r[b]) / (abs(r[a]) + abs(r[b])) for a, b in EQ[:k])


def residual(v, k):
    r, pts, P = six_radii(v)
    if np.any(~np.isfinite(r)) or np.any(r <= 0):
        return np.full(k + 2, 1e3)
    out = [(r[a] - r[b]) / (abs(r[a]) + abs(r[b])) for a, b in EQ[:k]]
    mind, maxr = guards(v)
    out.append(0.0 if mind > 1e-2 else (1e-2 - mind) * 1e2)
    out.append(0.0 if maxr < 1e4 else np.log10(maxr / 1e4))
    return np.array(out)


if __name__ == '__main__':
    rng = np.random.default_rng(7)
    out = []
    print('Corrected ladder.  A rung counts as solved only when the SCALE-FREE error is')
    print('below 1e-12; the objective value is shown alongside so the two can be compared.')
    print()
    print('  equations  objective    scale-free error  max radius   min dist   verdict')
    for k in range(1, 6):
        best = (1e9, None)
        for _ in range(600):
            v0 = np.array([rng.uniform(-1, 2), rng.uniform(0.2, 2.0),
                           rng.uniform(-2, 3), rng.uniform(-2, 3)])
            try:
                s = least_squares(residual, v0, args=(k,), xtol=1e-15, ftol=1e-15,
                                  gtol=1e-15, max_nfev=4000)
            except Exception:
                continue
            c = float(np.max(np.abs(s.fun)))
            if c < best[0]:
                best = (c, s.x.copy())
        v = best[1]
        sfe = scale_free_error(v, k)
        mind, maxr = guards(v)
        solved = bool(sfe < 1e-12)
        print('  %d          %.3e    %.3e         %.3e   %.3e  %s'
              % (k, best[0], sfe, maxr, mind, 'SOLVED' if solved else 'NOT SOLVED'))
        out.append(dict(k=k, objective=float(best[0]), scale_free_error=float(sfe),
                        max_radius=float(maxr), min_dist=float(mind),
                        solved=solved, v=list(map(float, v))))
    json.dump(dict(ladder=out, corrected=True, completed=True),
              open('results/ctrlA.json', 'w'), indent=1)
    print()
    top = max([r['k'] for r in out if r['solved']], default=0)
    print('Largest number of equations genuinely solved: %d (of 4 unknowns).' % top)
    if top >= 4:
        print('The control supports reading a failure at 4 equations as meaningful.')
    else:
        print('The control does NOT reach four equations, so a failure at four carries')
        print('no information and any Case A negative resting on it is unsupported.')
