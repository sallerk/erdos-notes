"""Parallel driver for the two-ring staggered scan, with artifact output."""
import sys, json, time, math
import multiprocessing as mp
import numpy as np
from tworing import candidate_radii, per_vertex_counts_ring, convex_range


def do_m(m):
    n = 2 * m
    target = n // 2 - 1
    best = None
    hits = []
    for r, tag in candidate_radii(m):
        nA, nB = per_vertex_counts_ring(m, r)
        mx = max(nA, nB)
        if best is None or mx < best[0]:
            best = (mx, r, tag, nA, nB)
        if mx <= target:
            hits.append(dict(m=m, n=n, r=r, tag=list(tag), nA=nA, nB=nB, target=target))
    lo, hi = convex_range(m)
    return dict(m=m, n=n, target=target,
                best_max=(best[0] if best else None),
                best_r=(best[1] if best else None),
                best_tag=(list(best[2]) if best else None),
                nA=(best[3] if best else None), nB=(best[4] if best else None),
                convex_lo=lo, convex_hi=hi,
                n_candidates=len(candidate_radii(m)), hits=hits)


def main(mlo, mhi, workers=16):
    t0 = time.time()
    ms = list(range(mlo, mhi + 1))
    out = []
    allhits = []
    with mp.Pool(workers) as P:
        for cnt, rec in enumerate(P.imap_unordered(do_m, ms, chunksize=1), 1):
            out.append(rec)
            allhits += rec['hits']
            if rec['hits']:
                print(f"*** HIT m={rec['m']} n={rec['n']}: {rec['hits']}", flush=True)
            if cnt % 25 == 0:
                print(f"  {cnt}/{len(ms)} done  {time.time()-t0:.0f}s", flush=True)
    out.sort(key=lambda r: r['m'])
    exc = {}
    for r in out:
        e = r['best_max'] - r['target']
        exc[e] = exc.get(e, 0) + 1
    res = {'m_lo': mlo, 'm_hi': mhi, 'workers': workers,
           'elapsed_s': round(time.time() - t0, 1), 'status': 'COMPLETED',
           'excess_histogram': {str(k): v for k, v in sorted(exc.items())},
           'hits': allhits, 'per_m': out}
    fn = f'tworing_m{mlo}_{mhi}.json'
    json.dump(res, open(fn, 'w'), indent=1)
    print(f"\nCOMPLETED m={mlo}..{mhi} in {res['elapsed_s']}s")
    print(f"excess over floor(n/2)-1 histogram: {res['excess_histogram']}")
    print(f"hits (counterexamples in this family): {len(allhits)}  -> {fn}")
    return res


if __name__ == '__main__':
    mp.freeze_support()
    a = int(sys.argv[1]); b = int(sys.argv[2])
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    main(a, b, w)
