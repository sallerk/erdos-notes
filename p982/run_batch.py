"""Batch driver: runs the searches in sequence and records COMPLETED/KILLED."""
import sys, time, json, traceback
import multiprocessing as mp

LOG = []


def note(kind, desc, status, secs, extra=None):
    LOG.append({'kind': kind, 'desc': desc, 'status': status,
                'seconds': round(secs, 1), **(extra or {})})
    json.dump(LOG, open('run_batch_log.json', 'w'), indent=1)
    print(f"[batch] {kind} {desc}: {status} ({secs:.0f}s)", flush=True)


def main(which):
    import lattice, nsearch
    if 'lat' in which:
        for lat, R in (('Z2', 8), ('A2', 8)):
            for n in (8, 9, 10, 11, 12):
                t = time.time()
                try:
                    r = lattice.run(n, R, lat, int(__import__("os").environ.get("W","16")), None,
                                    tag='_b%d' % (n // 2 - 1))
                    note('lattice', f'{lat} n={n} R={R} budget={n//2-1}',
                         'COMPLETED', time.time() - t,
                         {'counterexamples': len(r['counterexamples']),
                          'nodes': r['nodes'], 'pool': r['pool_size']})
                except Exception:
                    traceback.print_exc()
                    note('lattice', f'{lat} n={n} R={R}', 'FAILED', time.time() - t)
    if 'near' in which:
        # near-miss runs: budget = floor(n/2), i.e. the regular n-gon's value
        for lat, R in (('A2', 7), ('Z2', 7)):
            for n in (6, 7, 8, 9, 10):
                t = time.time()
                try:
                    r = lattice.run(n, R, lat, int(__import__("os").environ.get("W","16")), n // 2, tag="_near")
                    best = (r['best_near_misses'][0]['max_per_vertex']
                            if r['best_near_misses'] else None)
                    note('lattice-near', f'{lat} n={n} R={R} budget={n//2}',
                         'COMPLETED', time.time() - t,
                         {'best_max_per_vertex': best,
                          'n_found': len(r['best_near_misses'])})
                except Exception:
                    traceback.print_exc()
                    note('lattice-near', f'{lat} n={n} R={R}', 'FAILED',
                         time.time() - t)
    if 'ns' in which:
        for n in (8, 9, 10, 11, 12, 13, 14, 16, 20):
            t = time.time()
            try:
                r = nsearch.run(n, 3000, int(__import__("os").environ.get("W","16")))
                note('nsearch', f'n={n} trials=3000', 'COMPLETED', time.time() - t,
                     {'best_rho': r['best_rho'], 'seed0': r['seed0']})
            except Exception:
                traceback.print_exc()
                note('nsearch', f'n={n}', 'FAILED', time.time() - t)


if __name__ == '__main__':
    mp.freeze_support()
    main(sys.argv[1:] or ['lat', 'near', 'ns'])
