"""Run pdecide.decide over many patterns with a REAL per-pattern wall-clock cap.

pdecide.py itself has no cap, and sympy's Groebner engine can sit on a single pattern
indefinitely: a run over 262 patterns reached 200 in two minutes and then made no further
progress in ten.  That is lesson L70 again -- a cap that lives inside the library is not a
cap.  Here each pattern is decided in its own child process which is terminated by the
clock, so the wall ceiling  len(pats) * cap / workers  actually holds, and results are
dumped after every pattern so a kill loses at most one verdict.

A pattern that hits the cap is recorded as 'timeout', which is NOT a rejection: it is
carried forward as a live candidate exactly like 'inconclusive'.

Usage:  python pdrun.py <n> <mode> <patternfile> <outfile> [cap_seconds] [workers]
"""
import sys, json, time
import multiprocessing as mpr

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def _child(q, pat, n, mode):
    try:
        import pdecide
        r, info, pts = pdecide.decide(tuple(pat), n, mode)
        q.put((r, info, pts))
    except Exception as ex:
        q.put(('error', repr(ex), None))


def run(pats, n, mode, cap, workers, outfile):
    todo = list(enumerate(pats))
    live = []
    res = {}
    t0 = time.time()
    ceiling = len(pats) * cap / max(workers, 1)
    print('  %d patterns, cap %ds, %d workers -> wall ceiling %.0fs (%.2f h)'
          % (len(pats), cap, workers, ceiling, ceiling / 3600.0))

    def harvest(i, pat, verdict, info, pts):
        res[i] = {'pattern': list(pat), 'verdict': verdict, 'info': info, 'points': pts}
        buck = {}
        for v in res.values():
            buck[v['verdict']] = buck.get(v['verdict'], 0) + 1
        json.dump({'n': n, 'mode': mode, 'cap': cap, 'done': len(res),
                   'total': len(pats), 'counts': buck,
                   'seconds': round(time.time() - t0, 1),
                   'results': [res[j] for j in sorted(res)]},
                  open(outfile, 'w'), indent=1)
        if verdict != 'unsat' or len(res) % 25 == 0:
            print('   [%3d/%3d] %-12s %s' % (len(res), len(pats), verdict, list(pat)))

    while todo or live:
        while todo and len(live) < workers:
            i, pat = todo.pop(0)
            q = mpr.Queue()
            p = mpr.Process(target=_child, args=(q, list(pat), n, mode))
            p.start()
            live.append((p, q, i, pat, time.time() + cap))
        time.sleep(0.1)
        still = []
        for (p, q, i, pat, dl) in live:
            if not p.is_alive():
                try:
                    verdict, info, pts = q.get_nowait()
                except Exception:
                    verdict, info, pts = 'error', 'no result (exit %s)' % p.exitcode, None
                p.join()
                harvest(i, pat, verdict, info, pts)
            elif time.time() > dl:
                p.terminate()
                p.join(5)
                if p.is_alive():
                    p.kill()
                    p.join()
                harvest(i, pat, 'timeout', 'killed at %ds wall clock' % cap, None)
            else:
                still.append((p, q, i, pat, dl))
        live = still
    return [res[j] for j in sorted(res)]


if __name__ == '__main__':
    mpr.freeze_support()
    n, mode = int(sys.argv[1]), sys.argv[2]
    pf, of = sys.argv[3], sys.argv[4]
    cap = int(sys.argv[5]) if len(sys.argv) > 5 else 30
    W = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    blob = json.load(open(pf))
    pats = [tuple(p) for p in (blob['patterns'] if 'patterns' in blob
                               else blob['candidates'])]
    print('pdecide on %d patterns, n=%d mode=%s' % (len(pats), n, mode))
    out = run(pats, n, mode, cap, W, of)
    buck = {}
    for r in out:
        buck[r['verdict']] = buck.get(r['verdict'], 0) + 1
    print()
    for kk in sorted(buck):
        print('   %-12s %d' % (kk, buck[kk]))
    live = sum(v for kk, v in buck.items() if kk != 'unsat')
    print('   live candidates (everything not proved unsat): %d' % live)
    print('   written: %s' % of)
