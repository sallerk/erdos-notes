"""Supervisor for the Erdos #217 n=9 sweep.

Runs a ladder of increasing lattice regions; each region is split into NSH shards
run as independent OS processes (subprocess.Popen -- no multiprocessing pools).
Every shard writes a heartbeat JSON naming the index of the second point it is
currently on, so progress is measured as a DELTA between reads, never as state.

Obeys the standing rules: at most 5 worker CPUs, and a health checkpoint
(STATUS_217.json) refreshed every 60 s carrying HEALTHY = (progress since last read).

Usage: python super217.py <n> <nshards<=5> <R2> [R2 ...]
"""
import subprocess, sys, os, json, time, glob


def read_hb(f):
    try:
        return json.load(open(f))
    except Exception:
        return None


def main():
    n = int(sys.argv[1]); nsh = int(sys.argv[2])
    R2list = [int(x) for x in sys.argv[3:]]
    assert nsh <= 7, 'user rule: at most 7 CPUs per task'
    overall = {'n': n, 'nshards': nsh, 'regions': {}, 'status': 'RUNNING'}
    t_start = time.time()

    for R2 in R2list:
        for f in glob.glob('hb_%d_%d_*.json' % (n, R2)):
            os.remove(f)
        procs = []
        for s in range(nsh):
            hb = 'hb_%d_%d_%d.json' % (n, R2, s)
            out = 'sol_%d_R%d_s%d.txt' % (n, R2, s)
            p = subprocess.Popen(['./crescent2.exe', str(n), str(R2), out,
                                  str(s), str(nsh), hb],
                                 stdout=open('log_%d_R%d_s%d.txt' % (n, R2, s), 'w'),
                                 stderr=subprocess.STDOUT)
            procs.append(p)
        print('R2=%d: launched %d shards' % (R2, nsh), flush=True)
        t0 = time.time()
        last_nodes = 0
        while True:
            time.sleep(60)
            alive = sum(1 for p in procs if p.poll() is None)
            nodes = sols = 0
            done = 0
            ages = []
            for s in range(nsh):
                d = read_hb('hb_%d_%d_%d.json' % (n, R2, s))
                if d:
                    nodes += d.get('nodes', 0)
                    sols += d.get('solutions', 0)
                    if d.get('status') == 'COMPLETED':
                        done += 1
                    ages.append(round(time.time()
                                      - os.path.getmtime('hb_%d_%d_%d.json' % (n, R2, s)), 1))
            delta = nodes - last_nodes
            last_nodes = nodes
            el = time.time() - t0
            st = {'n': n, 'R2': R2, 'nshards': nsh, 'alive': alive,
                  'shards_completed': done, 'nodes': nodes,
                  'nodes_delta_last_60s': delta, 'HEALTHY': delta > 0 or alive == 0,
                  'solutions': sols, 'elapsed_s': round(el, 1),
                  'heartbeat_age_s': ages,
                  'wall_total_s': round(time.time() - t_start, 1),
                  'regions_done': list(overall['regions'].keys())}
            json.dump(st, open('STATUS_217.json', 'w'), indent=1)
            print('  R2=%d %.0fs alive=%d done=%d/%d nodes=%.4g (+%.3g) sols=%d healthy=%s'
                  % (R2, el, alive, done, nsh, nodes, delta, sols, st['HEALTHY']), flush=True)
            if sols:
                print('*** SOLUTIONS FOUND at R2=%d -- stopping ladder' % R2, flush=True)
            if alive == 0:
                break
        nodes = sols = 0
        for s in range(nsh):
            d = read_hb('hb_%d_%d_%d.json' % (n, R2, s))
            if d:
                nodes += d.get('nodes', 0); sols += d.get('solutions', 0)
        overall['regions'][str(R2)] = {'nodes': nodes, 'solutions': sols,
                                       'seconds': round(time.time() - t0, 1),
                                       'shards': nsh, 'status': 'COMPLETED'}
        json.dump(overall, open('LADDER_217.json', 'w'), indent=1)
        print('R2=%d COMPLETE: nodes=%d solutions=%d in %.0fs'
              % (R2, nodes, sols, time.time() - t0), flush=True)
        if sols:
            break
    overall['status'] = 'COMPLETED'
    overall['wall_total_s'] = round(time.time() - t_start, 1)
    json.dump(overall, open('LADDER_217.json', 'w'), indent=1)
    print('LADDER DONE in %.0fs' % (time.time() - t_start), flush=True)


if __name__ == '__main__':
    main()
