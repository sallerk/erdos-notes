"""Decide, over the REALS, whether a convex n-gon counterexample to #982 exists.

For each combinatorial pattern (edge colouring of K_n with <= floor(n/2)-1
colours at every vertex, enumerated exhaustively in patterns.py) we ask z3's
nonlinear real arithmetic (nlsat) whether there are real points
v_0..v_{n-1} with

    * every triple i<j<k positively oriented        (strictly convex, ccw order)
    * |v_a v_b|^2 == |v_c v_d|^2  whenever edges ab, cd have the same colour

Normalisation v_0=(0,0), v_1=(1,0) is WLOG (translate / rotate / scale; a
clockwise realisation reflects to a ccw one with the same labels, since
(x,y)->(x,-y) preserves all distances).

SOUNDNESS.  If a pattern is SAT the realisation has, at every vertex v, at most
(#colours at v) <= k distinct distances, i.e. it IS a counterexample.
COMPLETENESS.  A counterexample induces its own true colouring c(uv)=|uv|, which
satisfies |S_v| <= k at every vertex, hence appears in the enumeration (we only
impose the EQUALITIES of a pattern, never disequalities, so a coarser accidental
colouring is still covered because it is itself an enumerated pattern).
Therefore: every pattern UNSAT  =>  no convex n-gon counterexample for that n.
UNKNOWN (z3 timeout) leaves a gap and is reported as such.
"""

import sys, json, time, os, multiprocessing as mp
from itertools import combinations

from patterns import enumerate_patterns, reduce_patterns

_G = {}


def _init(n, edges, timeout_ms):
    _G['n'] = n
    _G['edges'] = edges
    _G['tmo'] = timeout_ms


def _solve(job):
    import z3
    idx, colvec = job
    n, edges, tmo = _G['n'], _G['edges'], _G['tmo']
    s = z3.Solver()
    s.set('timeout', tmo)
    X = [z3.Real(f'x{i}') for i in range(n)]
    Y = [z3.Real(f'y{i}') for i in range(n)]
    s.add(X[0] == 0, Y[0] == 0, X[1] == 1, Y[1] == 0)
    for i, j, k in combinations(range(n), 3):
        s.add((X[j] - X[i]) * (Y[k] - Y[i]) - (Y[j] - Y[i]) * (X[k] - X[i]) > 0)
    byc = {}
    for e, c in zip(edges, colvec):
        byc.setdefault(c, []).append(e)

    def sq(e):
        a, b = e
        return (X[a] - X[b]) ** 2 + (Y[a] - Y[b]) ** 2

    for c, es in byc.items():
        for t in range(1, len(es)):
            s.add(sq(es[0]) == sq(es[t]))
    t0 = time.time()
    r = s.check()
    dt = time.time() - t0
    if r == z3.sat:
        m = s.model()
        pts = [[str(m.eval(X[i], model_completion=True)),
                str(m.eval(Y[i], model_completion=True))] for i in range(n)]
        return (idx, 'sat', list(colvec), pts, dt)
    if r == z3.unsat:
        return (idx, 'unsat', list(colvec), None, dt)
    return (idx, 'unknown', list(colvec), None, dt)


def run(n, timeout_ms=60000, workers=16, use_altman=True):
    t_all = time.time()
    pats = enumerate_patterns(n, use_altman=use_altman)
    pats = reduce_patterns(n, pats)
    edges = pats[0][0]
    jobs = [(i, c) for i, (_, c) in enumerate(pats)]
    print(f"n={n}: deciding {len(jobs)} patterns with z3 nlsat, "
          f"{workers} workers, per-pattern timeout {timeout_ms} ms", flush=True)
    res = {'sat': [], 'unsat': 0, 'unknown': [], 'n': n,
           'total_patterns': len(jobs), 'timeout_ms': timeout_ms,
           'workers': workers, 'status': 'RUNNING'}
    slowest = []
    with mp.Pool(workers, initializer=_init, initargs=(n, edges, timeout_ms)) as pool:
        for cnt, (idx, verdict, colvec, pts, dt) in enumerate(
                pool.imap_unordered(_solve, jobs, chunksize=1), 1):
            slowest.append((dt, idx, verdict))
            if verdict == 'sat':
                res['sat'].append({'idx': idx, 'colouring': colvec, 'points': pts})
                print(f"*** SAT n={n} pattern {idx}  colouring={colvec}", flush=True)
            elif verdict == 'unsat':
                res['unsat'] += 1
            else:
                res['unknown'].append({'idx': idx, 'colouring': colvec})
                print(f"  UNKNOWN (timeout) n={n} pattern {idx}", flush=True)
            if cnt % 100 == 0:
                print(f"  {cnt}/{len(jobs)}  {time.time()-t_all:.0f}s  "
                      f"unsat={res['unsat']} sat={len(res['sat'])} "
                      f"unknown={len(res['unknown'])}", flush=True)
    slowest.sort(reverse=True)
    res['slowest'] = [{'sec': round(d, 2), 'idx': i, 'verdict': v}
                      for d, i, v in slowest[:10]]
    res['use_altman'] = use_altman
    res['elapsed_s'] = round(time.time() - t_all, 1)
    res['status'] = 'COMPLETED'
    suffix = '' if use_altman else '_noaltman'
    with open(f'decide_n{n}{suffix}.json', 'w') as f:
        json.dump(res, f, indent=1)
    print(f"\nn={n} COMPLETED in {res['elapsed_s']}s: "
          f"unsat={res['unsat']} sat={len(res['sat'])} "
          f"unknown={len(res['unknown'])} / {len(jobs)} patterns", flush=True)
    if not res['sat'] and not res['unknown']:
        print(f"==> EXHAUSTIVE over the reals: NO convex {n}-gon counterexample "
              f"to #982 exists.", flush=True)
    return res


if __name__ == '__main__':
    mp.freeze_support()
    n = int(sys.argv[1])
    tmo = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    ua = (len(sys.argv) <= 4) or sys.argv[4] != 'noaltman'
    run(n, timeout_ms=tmo, workers=w, use_altman=ua)
