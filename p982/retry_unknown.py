"""Re-run only the patterns that z3 left UNKNOWN, with a long timeout.
A timed-out pattern contributes nothing, so the certification for a given n is
incomplete until every one of them is resolved."""
import sys, json, time
import multiprocessing as mp
from itertools import combinations
from patterns import enumerate_patterns, reduce_patterns
import decide


def main(n, timeout_ms, workers):
    prev = json.load(open(f'decide_n{n}.json'))
    unk = prev['unknown']
    if not unk:
        print(f"n={n}: nothing unknown."); return
    pats = reduce_patterns(n, enumerate_patterns(n, verbose=False), verbose=False)
    edges = pats[0][0]
    jobs = [(u['idx'], tuple(u['colouring'])) for u in unk]
    print(f"n={n}: retrying {len(jobs)} UNKNOWN patterns, timeout {timeout_ms} ms, "
          f"{workers} workers", flush=True)
    t0 = time.time()
    out = {'sat': [], 'unsat': 0, 'unknown': []}
    with mp.Pool(workers, initializer=decide._init,
                 initargs=(n, edges, timeout_ms)) as P:
        for idx, verdict, colvec, pts, dt in P.imap_unordered(decide._solve, jobs):
            print(f"  pattern {idx}: {verdict}  [{dt:.0f}s]  colouring={colvec}",
                  flush=True)
            if verdict == 'sat':
                out['sat'].append({'idx': idx, 'colouring': colvec, 'points': pts})
            elif verdict == 'unsat':
                out['unsat'] += 1
            else:
                out['unknown'].append({'idx': idx, 'colouring': colvec})
    prev['retry'] = {'timeout_ms': timeout_ms, 'workers': workers,
                     'elapsed_s': round(time.time()-t0, 1),
                     'unsat': out['unsat'], 'sat': out['sat'],
                     'unknown': out['unknown'], 'status': 'COMPLETED'}
    prev['unsat_total'] = prev['unsat'] + out['unsat']
    prev['unknown_remaining'] = out['unknown']
    prev['sat_total'] = prev['sat'] + out['sat']
    json.dump(prev, open(f'decide_n{n}.json', 'w'), indent=1)
    print(f"\nn={n}: after retry  unsat={prev['unsat_total']}/"
          f"{prev['total_patterns']}  sat={len(prev['sat_total'])}  "
          f"unknown={len(out['unknown'])}", flush=True)
    if not prev['sat_total'] and not out['unknown']:
        print(f"==> EXHAUSTIVE over the reals: NO convex {n}-gon counterexample "
              f"to #982 exists.", flush=True)


if __name__ == '__main__':
    mp.freeze_support()
    n = int(sys.argv[1])
    tmo = int(sys.argv[2]) if len(sys.argv) > 2 else 1800000
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    main(n, tmo, w)
