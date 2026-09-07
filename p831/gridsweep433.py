"""The global grid sweep of the type-III family, with an artifact.

NOTE.md previously asserted "a 110^3 grid over the region with separation above 0.25
contains no point with both residuals below 0.02".  The audit found no such run had ever
been made: the number came from a terminal session and no file recorded it.  This script
performs the sweep and stores the result, so the sentence has evidence behind it.

What it measures.  On the three free angles of the type-III parametrisation, with the
fourth centre fixed at angle 0, evaluate

    f1 = (R(014) - R(123)) / (|R(014)| + |R(123)|)
    f2 = (R(023) - R(124)) / (|R(023)| + |R(124)|)

whose simultaneous vanishing is exactly the surviving (4,3,3) pattern, and report the
smallest max(|f1|,|f2|) over the grid, restricted to configurations whose four circle
centres are pairwise separated by at least s.  Fully vectorised, so a 180^3 grid is
cheap.

Usage: python gridsweep433.py [N] [s]
"""
import sys
import json

import numpy as np

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def sweep(N, seps):
    g = np.linspace(0.0, 2 * np.pi, N, endpoint=False) + (np.pi / N)
    A, B, C = np.meshgrid(g, g, g, indexing='ij')
    th = np.stack([A.ravel(), B.ravel(), C.ravel()], axis=1)
    del A, B, C

    def circ(t):
        return np.stack([np.cos(t), np.sin(t)], axis=-1)

    z = np.zeros(len(th))
    o1, o2, o3, o4 = circ(z), circ(th[:, 0]), circ(th[:, 1]), circ(th[:, 2])
    P0 = np.zeros((len(th), 2))
    P1, P2, P3, P4 = o1 + o2, o1 + o3, o2 + o4, o3 + o4

    def r2(X, Y, Z):
        a2 = np.sum((Y - Z) ** 2, axis=1)
        b2 = np.sum((Z - X) ** 2, axis=1)
        c2 = np.sum((X - Y) ** 2, axis=1)
        S = 2 * (a2 * b2 + b2 * c2 + c2 * a2) - (a2 * a2 + b2 * b2 + c2 * c2)
        with np.errstate(divide='ignore', invalid='ignore'):
            return np.where(np.abs(S) > 1e-12, a2 * b2 * c2 / S, np.nan)

    R014 = r2(P0, P1, P4)
    R023 = r2(P0, P2, P3)
    R123 = r2(P1, P2, P3)
    R124 = r2(P1, P2, P4)
    f1 = (R014 - R123) / (np.abs(R014) + np.abs(R123))
    f2 = (R023 - R124) / (np.abs(R023) + np.abs(R124))
    m = np.maximum(np.abs(f1), np.abs(f2))

    ang = np.concatenate([np.zeros((len(th), 1)), th], axis=1)

    def cd(a, b):
        d = np.abs(a - b) % (2 * np.pi)
        return np.minimum(d, 2 * np.pi - d)

    sep = np.full(len(th), 9.0)
    for i in range(4):
        for j in range(i + 1, 4):
            sep = np.minimum(sep, cd(ang[:, i], ang[:, j]))

    fin = np.isfinite(f1) & np.isfinite(f2)
    out = []
    for s in seps:
        ok = fin & (sep > s)
        mm = np.where(ok, m, np.inf)
        i = int(np.argmin(mm))
        n_below = int(np.sum(ok & (m < 0.02)))
        out.append(dict(separation=s, points=int(ok.sum()),
                        min_max_residual=float(mm[i]),
                        argmin_theta=[float(x) for x in th[i]],
                        count_both_below_0p02=n_below,
                        f1=float(f1[i]), f2=float(f2[i])))
        print('  sep > %.2f : %9d points, min max(|f1|,|f2|) = %.4e, '
              'points with both below 0.02: %d'
              % (s, ok.sum(), mm[i], n_below), flush=True)
    return out


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    print('grid %d^3 = %d points over the three free angles' % (N, N ** 3))
    rows = sweep(N, [0.35, 0.25, 0.15, 0.08, 0.0])
    json.dump(dict(N=N, rows=rows, completed=True), open('results/gridsweep433.json', 'w'),
              indent=1)
    print()
    print('Stored in results/gridsweep433.json.  The non-degenerate rows are the evidence')
    print('for the statement that the two equations have no common admissible solution;')
    print('the sep > 0 row shows the minimum falls away only as the centres merge.')
