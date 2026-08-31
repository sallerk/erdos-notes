"""SECOND, STRUCTURALLY DIFFERENT ENCODING of the same decision problem, used
to re-check decide.py's UNSAT answers.

Differences from decide.py:
  * equalities are stated through an explicit LEVEL VARIABLE per colour
    (|e|^2 == L_c for every edge e of colour c) instead of chaining each class
    to its first member;
  * every pattern is fed in its REVERSED vertex labelling
    (v_i -> v_{n-1-i}), which is a different formula with a provably identical
    answer (relabelling composed with the reflection (x,y)->(x,-y)).

It still uses z3, so this is not solver-independent -- it is ENCODING-
independent.  Stated that way in RESULTS.md.
"""
import sys, json, time
import multiprocessing as mp
from itertools import combinations
from patterns import enumerate_patterns, reduce_patterns

_G = {}


def _init(n, edges, tmo):
    _G.update(n=n, edges=edges, tmo=tmo)


def _solve(job):
    import z3
    idx, colvec = job
    n, edges, tmo = _G['n'], _G['edges'], _G['tmo']
    rev = lambda v: n - 1 - v          # reversed labelling
    s = z3.Solver()
    s.set('timeout', tmo)
    X = [z3.Real(f'X{i}') for i in range(n)]
    Y = [z3.Real(f'Y{i}') for i in range(n)]
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] == 1)
    for i, j, k in combinations(range(n), 3):
        s.add((X[j]-X[i])*(Y[k]-Y[i]) - (Y[j]-Y[i])*(X[k]-X[i]) > 0)
    byc = {}
    for e, c in zip(edges, colvec):
        u, v = rev(e[0]), rev(e[1])
        # reversing the labels also reverses the orientation; compose with the
        # reflection (x,y)->(x,-y), which preserves every distance, so the
        # counterexample question is unchanged.
        byc.setdefault(c, []).append((min(u, v), max(u, v)))
    L = {c: z3.Real(f'L{c}') for c in byc}
    for c, es in byc.items():
        s.add(L[c] > 0)
        for (u, v) in es:
            s.add((X[u]-X[v])**2 + (Y[u]-Y[v])**2 == L[c])
    t0 = time.time()
    r = s.check()
    dt = time.time()-t0
    if r == z3.sat:
        m = s.model()
        return (idx, 'sat', list(colvec),
                [[str(m.eval(X[i], model_completion=True)),
                  str(m.eval(Y[i], model_completion=True))] for i in range(n)], dt)
    return (idx, 'unsat' if r == z3.unsat else 'unknown', list(colvec), None, dt)


def run(n, timeout_ms=60000, workers=16):
    t0 = time.time()
    pats = reduce_patterns(n, enumerate_patterns(n, verbose=False), verbose=False)
    edges = pats[0][0]
    jobs = [(i, c) for i, (_, c) in enumerate(pats)]
    print(f"ALT ENCODING n={n}: {len(jobs)} patterns, {workers} workers, "
          f"timeout {timeout_ms} ms", flush=True)
    res = {'n': n, 'total_patterns': len(jobs), 'sat': [], 'unsat': 0,
           'unknown': [], 'timeout_ms': timeout_ms, 'workers': workers,
           'encoding': 'alt (level variables + reversed vertex labelling; scale fixed as in decide.py)'}
    with mp.Pool(workers, initializer=_init, initargs=(n, edges, timeout_ms)) as P:
        for cnt, (idx, v, col, pts, dt) in enumerate(
                P.imap_unordered(_solve, jobs, chunksize=1), 1):
            if v == 'sat':
                res['sat'].append({'idx': idx, 'colouring': col, 'points': pts})
                print(f"*** ALT SAT n={n} pattern {idx}", flush=True)
            elif v == 'unsat':
                res['unsat'] += 1
            else:
                res['unknown'].append({'idx': idx, 'colouring': col})
            if cnt % 500 == 0:
                print(f"  {cnt}/{len(jobs)}  {time.time()-t0:.0f}s  "
                      f"unsat={res['unsat']} unknown={len(res['unknown'])}",
                      flush=True)
    res['elapsed_s'] = round(time.time()-t0, 1)
    res['status'] = 'COMPLETED'
    json.dump(res, open(f'decide_alt_n{n}.json', 'w'), indent=1)
    print(f"ALT n={n} COMPLETED {res['elapsed_s']}s: unsat={res['unsat']} "
          f"sat={len(res['sat'])} unknown={len(res['unknown'])}", flush=True)
    return res


if __name__ == '__main__':
    mp.freeze_support()
    n = int(sys.argv[1])
    tmo = int(sys.argv[2]) if len(sys.argv) > 2 else 60000
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 16
    run(n, tmo, w)
