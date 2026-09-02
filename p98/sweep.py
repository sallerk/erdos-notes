"""Decide every distance pattern for given n, k with the exact Gram decider, in parallel.

Reports sat / unsat / inconclusive separately.  An 'inconclusive' is a branch the solver
could not evaluate; it is NOT an unsat, and any lower-bound claim requires the
inconclusive count to be zero.

Usage:  python sweep.py <n> <k> [workers]
"""
import sys, time, json
from multiprocessing import Pool
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from gram import decide
from hdecide import enumerate_patterns
from witness import vertex_ok


def job(a):
    pat, n, k = a
    try:
        r, vv, pts = decide(pat, n, k)
    except Exception as ex:
        return pat, 'error', repr(ex)[:200], None
    return pat, r, (str(vv) if vv is not None else None), (str(pts) if pts else None)


if __name__ == '__main__':
    n, k = int(sys.argv[1]), int(sys.argv[2])
    W = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    pats = [p for p in enumerate_patterns(n, k) if vertex_ok(p, n)]
    print('n=%d k=%d: %d canonical patterns after the vertex prune, %d workers'
          % (n, k, len(pats), W))
    t0 = time.time()
    with Pool(W) as pool:
        res = pool.map(job, [(p, n, k) for p in pats], chunksize=1)
    buck = {}
    for pat, r, vv, pts in res:
        buck.setdefault(r, []).append((list(pat), vv, pts))
    for r in sorted(buck):
        print('   %-13s %d' % (r, len(buck[r])))
    print('   %.1fs' % (time.time() - t0))
    json.dump({r: [x[0] for x in v] for r, v in buck.items()},
              open('sweep_n%d_k%d.json' % (n, k), 'w'), indent=1)
    for pat, vv, pts in buck.get('sat', [])[:3]:
        print('   SAT %s' % (pat,))
        print('       classes %s' % vv)
        print('       points  %s' % pts)
    for pat, vv, pts in buck.get('inconclusive', [])[:5]:
        print('   INCONCLUSIVE %s  (%s)' % (pat, vv))
    for pat, vv, pts in buck.get('error', [])[:5]:
        print('   ERROR %s  %s' % (pat, vv))
    ok = not buck.get('inconclusive') and not buck.get('error')
    print()
    if buck.get('sat'):
        print('   => D_gen(%d) <= %d' % (n, k))
    elif ok:
        print('   => D_gen(%d) > %d   (every pattern decided, none realisable)' % (n, k))
    else:
        print('   => NOT DECIDED: %d inconclusive, %d error'
              % (len(buck.get('inconclusive', [])), len(buck.get('error', []))))
