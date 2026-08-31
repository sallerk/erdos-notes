"""Supervisor: spawn NSHARDS independent shard.py processes with subprocess.Popen
(plain OS processes -- no multiprocessing pools, no handle duplication), wait for
them all, then merge the per-shard JSONs into one result.

Usage:  python launch.py <n> <nshards> <z3_timeout_ms> [tag]
"""
import subprocess, sys, json, time, glob, os


def merge(n, nsh, tag):
    tot = {'n': n, 'nshards': nsh, 'unit_ideal': 0, 'unsat': 0, 'sat': [],
           'z3_unknown': [], 'errors': [], 'assigned': 0, 'done': 0,
           'shards_completed': 0, 'slowest_s': 0.0}
    for sh in range(nsh):
        fn = 'shard_n%d%s_%02d.json' % (n, tag, sh)
        if not os.path.exists(fn):
            continue
        d = json.load(open(fn))
        tot['unit_ideal'] += d['unit_ideal']
        tot['unsat'] += d['unsat']
        tot['sat'].extend(d['sat'])
        tot['z3_unknown'].extend(d['z3_unknown'])
        tot['errors'].extend(d['errors'])
        tot['assigned'] += d['assigned']
        tot['done'] += d['done']
        tot['slowest_s'] = max(tot['slowest_s'], d.get('slowest_s', 0))
        if d.get('status') == 'COMPLETED':
            tot['shards_completed'] += 1
    tot['status'] = 'COMPLETED' if tot['shards_completed'] == nsh else 'PARTIAL'
    tot['refuted'] = tot['unit_ideal'] + tot['unsat']
    tot['residual'] = sorted(set(tot['z3_unknown']) | set(e[0] for e in tot['errors']))
    return tot


def main():
    n = int(sys.argv[1]); nsh = int(sys.argv[2])
    tmo = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
    tag = sys.argv[4] if len(sys.argv) > 4 else ''
    procs = []
    t0 = time.time()
    for sh in range(nsh):
        p = subprocess.Popen([sys.executable, 'shard.py', str(n), str(sh), str(nsh),
                              str(tmo), tag],
                             stdout=open('shard_%02d.log' % sh, 'w'),
                             stderr=subprocess.STDOUT)
        procs.append(p)
    print('launched %d shards for n=%d, z3 timeout %dms' % (nsh, n, tmo), flush=True)
    while True:
        alive = sum(1 for p in procs if p.poll() is None)
        m = merge(n, nsh, tag)
        el = time.time() - t0
        print('  %.0fs alive=%d done=%d/%d unit=%d unsat=%d sat=%d unk=%d err=%d'
              % (el, alive, m['done'], m['assigned'] if m['assigned'] else 0,
                 m['unit_ideal'], m['unsat'], len(m['sat']), len(m['z3_unknown']),
                 len(m['errors'])), flush=True)
        json.dump(m, open('merged_n%d%s.json' % (n, tag), 'w'), indent=1)
        if alive == 0:
            break
        time.sleep(30)
    m = merge(n, nsh, tag)
    m['elapsed_s'] = round(time.time() - t0, 1)
    json.dump(m, open('merged_n%d%s.json' % (n, tag), 'w'), indent=1)
    print('\nn=%d MERGED %.0fs: refuted=%d (unit ideal %d + nlsat unsat %d)  '
          'SAT=%d  residual=%d  shards completed %d/%d'
          % (n, m['elapsed_s'], m['refuted'], m['unit_ideal'], m['unsat'],
             len(m['sat']), len(m['residual']), m['shards_completed'], nsh), flush=True)
    if not m['sat'] and not m['residual'] and m['shards_completed'] == nsh:
        print('==> EXHAUSTIVE OVER THE REALS: no strictly convex %d-gon has every '
              'vertex with 3 other vertices equidistant from it.' % n, flush=True)


if __name__ == '__main__':
    main()
