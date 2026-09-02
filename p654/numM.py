"""Off-lattice search for a configuration with a small PINNED maximum, for Erdos #654.

WHY THIS AND NOT MORE LATTICE.  latM.py found no M=3 hit in any completed sweep.  Be
precise about which sweeps those are, because the coverage is uneven: A_2 to squared radius
121 completed at n=8 only (at n=7 both R121 shards were abandoned at 3 firsts of 23 and 22),
and the only Z^2 sweep, to radius 100, was also n=8.  At n=7 the completed lattice coverage
is A_2 to radius 49 and nothing else.  Every sweep ran in mode 'g'.  That is much weaker evidence than it looks: every
squared distance in either lattice is an integer, so no configuration whose distance
ratios are irrational can ever appear there, and the extremal 5-point configuration for
the #98 problem is exactly of that kind (its squared distances are 1, 2+sqrt3, 4+2sqrt3).
A lattice negative is "not in this lattice inside this radius", never "does not exist".
So the remaining chance of an M=3 witness lives off-lattice, and only a continuous search
can see it.

THE OBJECTIVE IS PER-POINT, WHICH IS THE WHOLE DIFFERENCE FROM #98.  p98/numsearch.py
clusters the C(n,2) squared distances GLOBALLY into k groups and drives the within-group
spread to zero, which targets the total count D.  Here the target is
M(X) = max_i d_X(x_i), so the cost is computed SEPARATELY AT EACH POINT: cluster the n-1
squared distances FROM point i into m groups and sum the within-group spreads over i.
Zero cost means every point sees at most m distinct distances, which is exactly M <= m,
and says nothing about D.  (The n=6 witness found this way has M=3 but D=7.)

Penalties keep the configuration admissible: small triangle areas are penalised in mode
'g' only, and small cocircularity determinants in both.  Everything is normalised by the
diameter so the penalties are scale-free.

A FLOAT HIT IS NOT A RESULT.  This script only proposes a candidate DISTANCE PATTERN; the
pattern is then handed to pdecide.py / pz3.py, which decide it exactly.  Nothing here is
ever reported as a witness on its own.

Usage:  python numM.py <n> <m> <g|n4> [restarts] [seed] [budget_seconds]
"""
import sys, itertools, json, random, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy.optimize import minimize, least_squares

n = int(sys.argv[1])
m = int(sys.argv[2])
MODE = sys.argv[3]
RESTARTS = int(sys.argv[4]) if len(sys.argv) > 4 else 100000
SEED = int(sys.argv[5]) if len(sys.argv) > 5 else 1
BUDGET = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0

PAIR = list(itertools.combinations(range(n), 2))
TRI_I = np.array(list(itertools.combinations(range(n), 3)))
QUAD_I = np.array(list(itertools.combinations(range(n), 4)))
PIDX = {p: i for i, p in enumerate(PAIR)}
# for each point, the indices in PAIR of its n-1 incident pairs
INC = [np.array([PIDX[(min(i, j), max(i, j))] for j in range(n) if j != i])
       for i in range(n)]


def unpack(z):
    p = np.zeros((n, 2))
    p[1, 0] = z[0]
    p[2:, :] = z[1:].reshape(n - 2, 2)
    return p


def d2s(p):
    d = p[:, None, :] - p[None, :, :]
    s = (d ** 2).sum(-1)
    return s[np.array([a for a, _ in PAIR]), np.array([b for _, b in PAIR])]


# Optimal 1-D k-means over so few values does not need a DP: with L = n-1 values sorted
# and m contiguous groups there are only C(L-1, m-1) ways to cut, at most 15 in the range
# used here.  Enumerating them and evaluating ALL n points at once with numpy replaces the
# per-point Python DP that made the first version take 8 seconds per restart.
L = n - 1
CUTS = [(0,) + c + (L,) for c in itertools.combinations(range(1, L), m - 1)] if m <= L \
    else [(0, L)]


def pinned_cost(sn):
    """sum over points of the optimal within-group spread of that point's distances"""
    X = np.sort(sn[np.array(INC)], axis=1)             # (n, L), each row sorted
    pre = np.concatenate([np.zeros((n, 1)), np.cumsum(X, axis=1)], axis=1)
    pre2 = np.concatenate([np.zeros((n, 1)), np.cumsum(X ** 2, axis=1)], axis=1)
    best = None
    for cut in CUTS:
        tot = np.zeros(n)
        for a, b in zip(cut, cut[1:]):
            c = b - a
            if c <= 1:
                continue
            s = pre[:, b] - pre[:, a]
            tot += np.maximum(pre2[:, b] - pre2[:, a] - s * s / c, 0.0)
        best = tot if best is None else np.minimum(best, tot)
    return float(best.sum())


def obj(z):
    p = unpack(z)
    s = d2s(p)
    diam = s.max()
    if diam <= 1e-12:
        return 1e6
    sn = s / diam
    f = pinned_cost(sn)              # THE PINNED COST, per point, not global
    f += 1e-3 * np.sum(np.maximum(0.0, 0.02 - sn) ** 2)
    A = p[TRI_I]
    ar = np.abs((A[:, 1, 0] - A[:, 0, 0]) * (A[:, 2, 1] - A[:, 0, 1])
                - (A[:, 2, 0] - A[:, 0, 0]) * (A[:, 1, 1] - A[:, 0, 1])) / diam
    if MODE == 'g':
        f += 1e-4 * np.sum(np.maximum(0.0, 0.03 - ar) ** 2)
    Q = p[QUAD_I]
    MM = np.empty((Q.shape[0], 4, 4))
    MM[:, :, 0] = (Q ** 2).sum(axis=2)
    MM[:, :, 1] = Q[:, :, 0]
    MM[:, :, 2] = Q[:, :, 1]
    MM[:, :, 3] = 1.0
    dt = np.abs(np.linalg.det(MM)) / (diam ** 2)
    f += 1e-4 * np.sum(np.maximum(0.0, 0.02 - dt) ** 2)
    return f


def extract_pattern(sv, tol):
    """single-linkage clustering of the normalised squared distances -> a colouring"""
    order = list(np.argsort(sv))
    lab = {}
    c = 0
    lab[int(order[0])] = 0
    for a, b in zip(order, order[1:]):
        if sv[b] - sv[a] > tol:
            c += 1
        lab[int(b)] = c
    return tuple(lab[i] for i in range(len(sv))), c + 1


def pinned_of(pat):
    out = []
    for i in range(n):
        out.append(len(set(pat[e] for e in INC[i])))
    return out


def polish(z0, pat, k):
    def resid(w):
        p = unpack(w[:len(z0)])
        D = w[len(z0):]
        sv = d2s(p)
        return np.array([sv[i] - D[pat[i]] for i in range(len(PAIR))])
    p0 = unpack(z0)
    s0 = d2s(p0)
    D0 = np.array([np.mean([s0[i] for i in range(len(PAIR)) if pat[i] == c])
                   for c in range(k)])
    w0 = np.concatenate([z0, D0])
    r = least_squares(resid, w0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
    return r, float(np.max(np.abs(r.fun)))


if __name__ == '__main__':
    rng = random.Random(SEED)
    np.random.seed(SEED)
    print('off-lattice search n=%d, target M<=%d, mode %s, seed %d, budget %ss'
          % (n, m, MODE, SEED, BUDGET or 'none'))
    T0 = time.time()
    best = 1e18
    leads = {}
    done = 0
    outfile = 'numM_n%d_m%d_%s_s%d.json' % (n, m, MODE, SEED)
    for r in range(RESTARTS):
        if BUDGET and time.time() - T0 > BUDGET:
            break
        done += 1
        z0 = np.concatenate([[1.0], np.random.randn(2 * (n - 2)) * 0.8])
        # Powell was costing ~3s per restart for a marginal gain and starving the search of
        # restarts, which is what it actually needs: measured at the known n=6 witness the
        # objective is 1.5e-8 and the polish residual 1.8e-15, so the machinery was never
        # the problem, the number of basins visited was.
        res = minimize(obj, z0, method='Nelder-Mead',
                       options={'maxiter': 3000, 'fatol': 1e-13, 'xatol': 1e-11})
        v = float(res.fun)
        if v < best:
            best = v
        # The soft objective only PROPOSES.  A loose threshold is right: the decisive test is
        # the Gauss-Newton polish onto the exact equalities of the extracted pattern, which
        # reaches ~1e-15 for a genuine configuration and stalls for a near-miss.
        if v > 1e-2:
            continue
        p = unpack(res.x)
        s = d2s(p)
        sn = s / s.max()
        for tol in (1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 3e-3):
            pat, k = extract_pattern(sn, tol)
            pin = pinned_of(pat)
            if max(pin) > m or k < 2:
                continue
            rr, worst = polish(res.x, pat, k)
            if worst > 1e-12:
                continue
            # The polished configuration must still be ADMISSIBLE and NON-DEGENERATE.
            #
            # An earlier version checked only for coincident points and (in mode g)
            # collinear triples, and it produced a false lead at n=7: a configuration whose
            # polish residual was 4.4e-16 but in which classes 1 and 2 had collapsed to the
            # same value, classes 3 and 4 likewise (so the "6 classes" were really 4), and
            # five quadruples were concyclic (three with a float-exact zero determinant and
            # two of order 1e-16, all far below the threshold used below).  The exact decider rejected it.  A
            # tiny residual only says the points fit the EQUALITIES; it says nothing about
            # the INEQUALITIES that make the pattern and the hypothesis meaningful.  Both
            # are now tested here.
            pp = unpack(rr.x[:len(res.x)])
            ss = d2s(pp)
            if ss.min() <= 1e-14 * ss.max():
                continue                                    # coincident points
            Dv = rr.x[len(res.x):]
            if len(Dv) != k or np.any(Dv <= 0):
                continue
            scale = float(np.max(np.abs(Dv)))
            if any(abs(Dv[a] - Dv[b]) <= 1e-9 * scale
                   for a in range(k) for b in range(a + 1, k)):
                continue                                    # classes collapsed: not k-class
            A = pp[TRI_I]
            ar = np.abs((A[:, 1, 0] - A[:, 0, 0]) * (A[:, 2, 1] - A[:, 0, 1])
                        - (A[:, 2, 0] - A[:, 0, 0]) * (A[:, 1, 1] - A[:, 0, 1]))
            if MODE == 'g' and ar.min() <= 1e-9 * ss.max():
                continue                                    # collinear triple
            Q = pp[QUAD_I]
            MM = np.empty((Q.shape[0], 4, 4))
            MM[:, :, 0] = (Q ** 2).sum(axis=2)
            MM[:, :, 1] = Q[:, :, 0]
            MM[:, :, 2] = Q[:, :, 1]
            MM[:, :, 3] = 1.0
            dets = np.abs(np.linalg.det(MM))
            thr = 1e-9 * (ss.max() ** 2)
            bad = False
            for qi, q in enumerate(QUAD_I):
                if dets[qi] > thr:
                    continue
                # determinant vanishes: concyclic, or (legal under n4) collinear
                flat = (abs((pp[q[1], 0] - pp[q[0], 0]) * (pp[q[2], 1] - pp[q[0], 1])
                            - (pp[q[2], 0] - pp[q[0], 0]) * (pp[q[1], 1] - pp[q[0], 1]))
                        <= 1e-9 * ss.max()
                        and abs((pp[q[1], 0] - pp[q[0], 0]) * (pp[q[3], 1] - pp[q[0], 1])
                                - (pp[q[3], 0] - pp[q[0], 0]) * (pp[q[1], 1] - pp[q[0], 1]))
                        <= 1e-9 * ss.max())
                if not (MODE == 'n4' and flat):
                    bad = True
                    break
            if bad:
                continue                                    # four points on a circle
            if max(pinned_of(pat)) > m:
                continue
            key = str(list(pat))
            if key in leads:
                continue
            leads[key] = {'pattern': list(pat), 'classes': k, 'pinned': pin,
                          'residual': worst, 'restart': r,
                          'points': unpack(rr.x[:len(res.x)]).tolist()}
            print('  LEAD restart %d: M=%d k=%d residual %.2e  pattern %s'
                  % (r, max(pin), k, worst, list(pat)))
            json.dump({'n': n, 'm': m, 'mode': MODE, 'seed': SEED, 'restarts_done': done,
                       'best_obj': best, 'leads': list(leads.values())},
                      open(outfile, 'w'), indent=1)
            break
        if done % 200 == 0:
            print('  %d restarts, best objective %.3e, %d leads, %.0fs'
                  % (done, best, len(leads), time.time() - T0))
            json.dump({'n': n, 'm': m, 'mode': MODE, 'seed': SEED, 'restarts_done': done,
                       'best_obj': best, 'leads': list(leads.values())},
                      open(outfile, 'w'), indent=1)
    json.dump({'n': n, 'm': m, 'mode': MODE, 'seed': SEED, 'restarts_done': done,
               'best_obj': best, 'leads': list(leads.values()), 'finished': True},
              open(outfile, 'w'), indent=1)
    print('  done: %d restarts, best objective %.3e, %d distinct leads, %.0fs'
          % (done, best, len(leads), time.time() - T0))
    print('  written: %s   (leads are CANDIDATE PATTERNS, to be decided exactly)' % outfile)
