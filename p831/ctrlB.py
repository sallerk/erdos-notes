"""A HARDER positive control for pscreen.py, built because the original is too easy.

The original control is a 4-class pattern: six equations in six unknowns, exactly
determined.  The patterns it is used to validate have three classes: seven equations in
six unknowns, overdetermined by one.  So the original control never tests the case that
matters, namely whether the optimiser can find a solution whose existence depends on the
equations being DEPENDENT rather than on a dimension count.

This builds such a control.  Inside the type-III family (four circumradii equal, all
four circles through one point) Lemma 6 makes R(123) = R(234) and R(124) = R(134) hold
identically.  Imposing one more coincidence, R(014) = R(023), gives a configuration
whose radius pattern has FOUR classes with sizes 4,2,2,2 - hence six equations in six
unknowns - but whose six equations have only four independent ones, so its solution set
sits in positive codimension inside the naive count.  If pscreen's optimiser recovers
THAT pattern from random six-dimensional starts, it is capable of finding solutions that
live on a degenerate subvariety, which is precisely the ability the n=5 negative needs.

It remains one equation short of the real thing.  That gap cannot be closed at n = 5,
because a realisable 3-class pattern is exactly what is in question.
"""
import sys
import json
from itertools import combinations

import numpy as np
from scipy.optimize import least_squares

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRI = list(combinations(range(5), 3))


def points(th):
    t = np.concatenate([[0.0], th])
    o = np.stack([np.cos(t), np.sin(t)], axis=1)
    return np.array([[0.0, 0.0], o[0] + o[1], o[0] + o[2], o[1] + o[3], o[2] + o[3]])


def r2_of(P, t):
    A, B, C = P[t[0]], P[t[1]], P[t[2]]
    a2 = np.sum((B - C) ** 2)
    b2 = np.sum((C - A) ** 2)
    c2 = np.sum((A - B) ** 2)
    S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
    return (a2 * b2 * c2 / S if abs(S) > 1e-14 else np.nan), S


def det4(P, q):
    return np.linalg.det(np.array(
        [[P[v, 0] ** 2 + P[v, 1] ** 2, P[v, 0], P[v, 1], 1.0] for v in q]))


def one_eq(th):
    P = points(th)
    a = r2_of(P, (0, 1, 4))[0]
    b = r2_of(P, (0, 2, 3))[0]
    if not (np.isfinite(a) and np.isfinite(b)):
        return np.array([1e3])
    return np.array([(a - b) / (abs(a) + abs(b))])


def build_control(seed=1234, tries=8000):
    """find an admissible member of the family with R(014) = R(023)"""
    rng = np.random.default_rng(seed)
    for _ in range(tries):
        v0 = rng.uniform(0.05, 6.2, 3)
        try:
            s = least_squares(one_eq, v0, xtol=1e-15, ftol=1e-15, gtol=1e-15,
                              max_nfev=800)
        except Exception:
            continue
        if float(np.max(np.abs(s.fun))) > 1e-14:
            continue
        P = points(s.x)
        r2 = np.array([r2_of(P, t)[0] for t in TRI])
        if not np.all(np.isfinite(r2)) or np.any(r2 <= 0):
            continue
        dets = [abs(det4(P, q)) for q in combinations(range(5), 4)]
        mind = min(np.linalg.norm(P[i] - P[j]) for i, j in combinations(range(5), 2))
        minS = min(abs(r2_of(P, t)[1]) for t in TRI)
        if min(dets) < 1e-5 or mind < 1e-2 or minS < 1e-6:
            continue
        vals = sorted(set(np.round(r2, 9)))
        lab = [int(np.argmin([abs(x - v) for v in vals])) for x in r2]
        sizes = sorted((lab.count(c) for c in set(lab)), reverse=True)
        if len(vals) != 4 or sizes != [4, 2, 2, 2]:
            continue
        return dict(theta=list(map(float, s.x)), points=P.tolist(),
                    labels=lab, k=len(vals), sizes=sizes,
                    values=[float(x) for x in vals],
                    min_det4=float(min(dets)), min_dist=float(mind))
    return None


if __name__ == '__main__':
    sys.path.insert(0, '.')
    from pscreen import screen

    ctl = build_control()
    if ctl is None:
        print('could not build the control configuration')
        sys.exit(1)
    print('control configuration built inside the type-III family:')
    print('   theta      = %s' % np.round(ctl['theta'], 10))
    print('   classes    = %d, sizes %s' % (ctl['k'], ctl['sizes']))
    print('   R^2 values = %s' % np.round(ctl['values'], 10))
    print('   min |det4| = %.3e   min pairwise distance = %.3e'
          % (ctl['min_det4'], ctl['min_dist']))
    print('   -> admissible, so this pattern IS realisable by construction.')

    # how many of its six equations are actually independent?
    P = np.array(ctl['points'])
    eps = 1e-6
    rows = []
    base = np.array([r2_of(P, t)[0] for t in TRI])
    for i in range(2, 5):
        for j in range(2):
            Q = P.copy()
            Q[i, j] += eps
            d = (np.array([r2_of(Q, t)[0] for t in TRI]) - base) / eps
            rows.append(d)
    J = np.array(rows).T
    cons = []
    for c in range(ctl['k']):
        idx = [i for i in range(10) if ctl['labels'][i] == c]
        for t in idx[1:]:
            cons.append(J[t] - J[idx[0]])
    Jc = np.array(cons)
    rank = np.linalg.matrix_rank(Jc, tol=1e-6)
    print()
    print('   equations = %d, unknowns = 6, RANK of the constraint Jacobian = %d'
          % (len(cons), rank))
    print('   so %d of the %d equations are dependent: the solution set has positive'
          % (len(cons) - rank, len(cons)))
    print('   codimension relative to the naive count, which is the hard case.')

    rng = np.random.default_rng(4242)
    for restarts in (100, 500):
        c, v = screen(5, ctl['k'], ctl['labels'], restarts, rng)
        print()
        print('   pscreen with %d restarts on this control: residual %.3e -> %s'
              % (restarts, c, 'FOUND' if c < 1e-12 else 'MISSED'))
    json.dump(dict(control=ctl, equations=len(cons), rank=int(rank), completed=True),
              open('results/ctrlB.json', 'w'), indent=1)
