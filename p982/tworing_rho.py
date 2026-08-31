"""How close does the two-ring staggered family get, measured continuously?

For each m, scan the radius ratio r over the whole convex window
(cos(pi/m), 1/cos(pi/m)) and report the configuration minimising

    rho = (largest within-cluster spread of any vertex's distance set,
           when that set is optimally split into floor(n/2)-1 clusters)
        / (shortest side of the polygon)          [n = 2m]

rho = 0 would be a counterexample.  The regular 2m-gon (r = 1) is in the family
and is the baseline to beat.  Everything here is float64; it is a near-miss
measurement, not a certification.
"""
import sys, json, math
import numpy as np
from nsearch import rho_of, degeneracy, sides_of


def build(m, r):
    a = 2 * np.pi * np.arange(m) / m
    b = a + np.pi / m
    A = np.stack([np.cos(a), np.sin(a)], 1)
    B = r * np.stack([np.cos(b), np.sin(b)], 1)
    P = np.empty((2 * m, 2))
    P[0::2] = A
    P[1::2] = B
    return P


def scan(m, steps=20001):
    n = 2 * m
    k = n // 2 - 1
    c = math.cos(math.pi / m)
    lo, hi = c, 1.0 / c
    rs = np.linspace(lo + (hi - lo) * 1e-6, hi - (hi - lo) * 1e-6, steps)
    best = None
    for r in rs:
        P = build(m, r)
        v = rho_of(P, k)
        if best is None or v < best[0]:
            best = (v, r)
    Pb = build(m, best[1])
    Preg = build(m, 1.0)
    D = np.sqrt(((Pb[:, None, :] - Pb[None, :, :]) ** 2).sum(-1))
    pv = []
    for i in range(n):
        vals = np.sort(np.delete(D[i], i))
        # count distinct at 1e-9 relative tolerance
        cnt = 1
        for t in range(1, len(vals)):
            if vals[t] - vals[t - 1] > 1e-9 * max(1.0, vals[t]):
                cnt += 1
        pv.append(cnt)
    return {'m': m, 'n': n, 'k': k, 'best_rho': float(best[0]),
            'best_r': float(best[1]), 'convex_lo': lo, 'convex_hi': hi,
            'regular_2mgon_rho': float(rho_of(Preg, k)),
            'min_side_over_diam': degeneracy(Pb),
            'max_per_vertex_at_1e-9': int(max(pv)),
            'target_floor_n_2': n // 2,
            'points': Pb.tolist(), 'steps': steps}


if __name__ == '__main__':
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    out = []
    for m in range(lo, hi + 1):
        r = scan(m)
        out.append(r)
        print(f"m={m:3d} n={r['n']:3d}: best rho={r['best_rho']:.8f} at "
              f"r={r['best_r']:.8f}  (regular {r['n']}-gon rho="
              f"{r['regular_2mgon_rho']:.8f})  max per-vertex="
              f"{r['max_per_vertex_at_1e-9']} target={r['target_floor_n_2']}  "
              f"minside/diam={r['min_side_over_diam']:.4f}", flush=True)
    json.dump({'status': 'COMPLETED', 'per_m': out},
              open(f'tworing_rho_{lo}_{hi}.json', 'w'), indent=1)
    print(f"-> tworing_rho_{lo}_{hi}.json")
