"""z3 decision procedure for pinned patterns, with a harness that actually enforces caps.

z3's nlsat is a decision procedure for real closed fields, so BOTH its `sat` and its
`unsat` are proofs; only `unknown` carries no information.  That makes it the arbiter for
everything pdecide.py leaves inconclusive.

THREE THINGS THIS FIXES relative to p98/z3run.py.

(1) NO ORDERING CONSTRAINT.  z3run.py adds d_0 < d_1 < ... < d_{k-1}.  Canonical patterns
    number their colours by ORDER OF FIRST APPEARANCE along the edge list, which has
    nothing to do with the magnitudes; the two orders coincide only by accident.  Imposing
    the order therefore asks "is this pattern realisable with its colour values in this
    particular order", not "is it realisable", and can in principle turn a realisable
    pattern into `unsat`.  Here the colours are only required to be pairwise DISTINCT.

(2) THE PER-PATTERN CAP IS REAL.  z3's `timeout` parameter is advisory: nlsat does not
    poll for cancellation inside deep real-algebraic arithmetic.  On the last #98 run it
    overran by 95% (87,797 worker-seconds occupied (6 workers x 14,632.9 s wall; about 85,000 CPU-seconds at the 0.967 utilisation measured mid-run) against a 45,000 ceiling).  Here each pattern
    runs in its own child process which is TERMINATED by wall clock, so the ceiling
    `len(pats) * cap / workers` is a bound that actually holds.

(3) RESULTS ARE DUMPED AFTER EVERY PATTERN.  z3run.py used pool.map and wrote its JSON
    only once every task returned, so one stuck pattern made all 75 verdicts
    unrecoverable.  Here a kill at any moment loses at most one verdict.

MODES.  'g' is general position.  'n4' forbids only genuinely concyclic quadruples: the
4x4 determinant also vanishes for collinear quadruples, which under #654's own hypothesis
are legal, so the constraint is "determinant nonzero OR all four collinear".

Usage:  python pz3_noorder.py <n> <mode> <candfile> <outfile> [cap_seconds] [workers]
"""
import sys, os, json, time, itertools
import multiprocessing as mpr

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def build(pat, n, mode):
    import z3
    from common import pairs, det4
    P = pairs(n)
    k = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(k)]
    s = z3.Solver()
    # gauge fixing: translate 0 to the origin, rotate 1 onto the positive x-axis.
    # No reflection is fixed and no colour order is assumed.
    s.add(X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0)
    for c in range(k):
        s.add(D[c] > 0)
    for a, b in itertools.combinations(range(k), 2):
        s.add(D[a] != D[b])
    for idx, (i, j) in enumerate(P):
        s.add((X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2 == D[pat[idx]])

    def tri(a, b, c):
        return (X[b] - X[a]) * (Y[c] - Y[a]) - (X[c] - X[a]) * (Y[b] - Y[a])

    if mode == 'g':
        for a, b, c in itertools.combinations(range(n), 3):
            s.add(tri(a, b, c) != 0)
        for q in itertools.combinations(range(n), 4):
            s.add(det4([[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in q]) != 0)
    else:
        for q in itertools.combinations(range(n), 4):
            d = det4([[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in q])
            flat = z3.And(tri(q[0], q[1], q[2]) == 0, tri(q[0], q[1], q[3]) == 0)
            s.add(z3.Or(d != 0, flat))
    return s


def _child(q, pat, n, mode):
    try:
        s = build(tuple(pat), n, mode)
        r = s.check()
        q.put((str(r), str(s.model()) if str(r) == 'sat' else None))
    except Exception as ex:
        q.put(('error', repr(ex)))


def decide_capped(pat, n, mode, cap):
    """Run one pattern in a child process killed by WALL CLOCK at `cap` seconds."""
    q = mpr.Queue()
    p = mpr.Process(target=_child, args=(q, list(pat), n, mode))
    p.start()
    p.join(cap)
    if p.is_alive():
        p.terminate()
        p.join(5)
        if p.is_alive():
            p.kill()
            p.join()
        return 'timeout', None
    try:
        return q.get_nowait()
    except Exception:
        return 'error', 'child produced no result (exit %s)' % p.exitcode


def run(pats, n, mode, cap, workers, outfile):
    """Manual scheduler: at most `workers` children, each with its own real deadline."""
    todo = list(enumerate(pats))
    live = []                        # (proc, queue, index, pattern, deadline)
    res = {}
    t0 = time.time()
    ceiling = len(pats) * cap / max(workers, 1)
    print('  %d patterns, cap %ds, %d workers -> wall ceiling %.0fs (%.1f h)'
          % (len(pats), cap, workers, ceiling, ceiling / 3600.0))

    def harvest(entry, verdict, model):
        i, pat = entry[2], entry[3]
        res[i] = {'pattern': list(pat), 'verdict': verdict, 'model': model}
        buck = {}
        for v in res.values():
            buck[v['verdict']] = buck.get(v['verdict'], 0) + 1
        json.dump({'n': n, 'mode': mode, 'cap': cap, 'done': len(res),
                   'total': len(pats), 'counts': buck,
                   'seconds': round(time.time() - t0, 1),
                   'results': [res[j] for j in sorted(res)]},
                  open(outfile, 'w'), indent=1)
        print('   [%3d/%3d] %-8s %s' % (len(res), len(pats), verdict, list(pat)))

    while todo or live:
        while todo and len(live) < workers:
            i, pat = todo.pop(0)
            q = mpr.Queue()
            p = mpr.Process(target=_child, args=(q, list(pat), n, mode))
            p.start()
            live.append((p, q, i, pat, time.time() + cap))
        time.sleep(0.15)
        still = []
        for entry in live:
            p, q, i, pat, dl = entry
            if not p.is_alive():
                try:
                    verdict, model = q.get_nowait()
                except Exception:
                    verdict, model = 'error', 'no result (exit %s)' % p.exitcode
                p.join()
                harvest(entry, verdict, model)
            elif time.time() > dl:
                p.terminate()
                p.join(5)
                if p.is_alive():
                    p.kill()
                    p.join()
                harvest(entry, 'timeout', None)
            else:
                still.append(entry)
        live = still
    return [res[j] for j in sorted(res)]


if __name__ == '__main__':
    mpr.freeze_support()
    n, mode = int(sys.argv[1]), sys.argv[2]
    cf, of = sys.argv[3], sys.argv[4]
    cap = int(sys.argv[5]) if len(sys.argv) > 5 else 120
    W = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    blob = json.load(open(cf))
    pats = [tuple(p) for p in (blob['patterns'] if 'patterns' in blob
                               else blob['candidates'])]
    print('z3 on %d patterns, n=%d mode=%s' % (len(pats), n, mode))
    out = run(pats, n, mode, cap, W, of)
    buck = {}
    for r in out:
        buck[r['verdict']] = buck.get(r['verdict'], 0) + 1
    print()
    for kk in sorted(buck):
        print('   %-9s %d' % (kk, buck[kk]))
    print('   written: %s' % of)
