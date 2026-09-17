"""Supervisor for the k=3 decision pass.  Enforces a HARD budget per class.

Rules this obeys (set by the user 2026-08-30, see tasks/lessons.md L32):
  * at most 5 worker CPUs
  * writes a health checkpoint (STATUS_*.json) that reports DELTA, not state, so a
    wedged run is visible immediately rather than after ten hours

Mechanism: each worker names the class it is about to attempt in a heartbeat file
before starting it.  sympy's Groebner cannot be interrupted from inside the
process, so the supervisor enforces the budget from outside: if a heartbeat goes
stale the worker is killed, the offending class is appended to that shard's skip
file (to be retried later by a different method), and the worker is restarted --
it resumes from its own append-only results file.

Usage: python k3super.py <n> <nworkers<=5> <gb_budget_s> <z3_ms> [tag] [index_file.npy]
(the index file restricts the pass to those class indices, e.g. c123_n7_survivors.npy)
"""
import subprocess, sys, os, json, time, glob


def read_hb(f):
    try:
        return json.load(open(f))
    except Exception:
        return None


def tally(n, nsh, tag):
    t = {'unit_ideal': 0, 'unsat': 0, 'SAT': [], 'z3_unknown': [], 'errors': [],
         'done': 0, 'skipped': 0}
    for sh in range(nsh):
        base = 'n%d%s_%02d' % (n, tag, sh)
        rf = 'res_%s.jsonl' % base
        if os.path.exists(rf):
            for line in open(rf):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                t['done'] += 1
                v = r.get('v')
                if v == 'unit_ideal':
                    t['unit_ideal'] += 1
                elif v == 'unsat':
                    t['unsat'] += 1
                elif v == 'SAT':
                    t['SAT'].append(r)
                elif v == 'z3_unknown':
                    t['z3_unknown'].append(r['idx'])
                else:
                    t['errors'].append([r['idx'], v])
        sf = 'skip_%s.txt' % base
        if os.path.exists(sf):
            t['skipped'] += sum(1 for line in open(sf) if line.strip())
    return t


def main():
    n = int(sys.argv[1]); nsh = int(sys.argv[2])
    budget = float(sys.argv[3]); z3ms = int(sys.argv[4])
    tag = sys.argv[5] if len(sys.argv) > 5 else ''
    idxfile = sys.argv[6] if len(sys.argv) > 6 else None
    import numpy as np
    total = len(np.load(idxfile)) if idxfile else len(np.load('cls_n%d.npy' % n))
    assert nsh <= 5, 'user rule: at most 5 CPUs per task'
    statusf = 'STATUS_n%d%s.json' % (n, tag)

    def spawn(sh):
        return subprocess.Popen([sys.executable, 'k3worker.py', str(n), str(sh),
                                 str(nsh), str(z3ms), tag] + ([idxfile] if idxfile else []),
                                stdout=open('w_%02d.log' % sh, 'a'),
                                stderr=subprocess.STDOUT)

    procs = {sh: spawn(sh) for sh in range(nsh)}
    print('supervisor: %d workers, gb budget %.0fs, z3 %dms' % (nsh, budget, z3ms), flush=True)
    t0 = time.time()
    kills = 0
    last_tally = tally(n, nsh, tag)
    last_t = time.time()
    finished = set()
    while True:
        time.sleep(5)
        now = time.time()
        for sh in range(nsh):
            if sh in finished:
                continue
            hb = read_hb('hb_n%d%s_%02d.json' % (n, tag, sh))
            p = procs[sh]
            alive = p.poll() is None
            if hb and hb.get('finished'):
                finished.add(sh)
                continue
            if alive and hb and (now - hb['t']) > budget:
                bad = hb['idx']
                try:
                    p.kill()
                except Exception:
                    pass
                with open('skip_n%d%s_%02d.txt' % (n, tag, sh), 'a') as f:
                    f.write('%d gb_over_budget %.0f\n' % (bad, budget))
                kills += 1
                print('  KILL shard %02d stuck %.0fs on class %d -> skipped, restarting'
                      % (sh, now - hb['t'], bad), flush=True)
                procs[sh] = spawn(sh)
            elif not alive:
                if hb and hb.get('finished'):
                    finished.add(sh)
                else:
                    print('  shard %02d died unexpectedly, restarting' % sh, flush=True)
                    procs[sh] = spawn(sh)
        if now - last_t >= 60:
            cur = tally(n, nsh, tag)
            delta = cur['done'] - last_tally['done']
            rate = delta / (now - last_t)
            ages = {}
            for sh in range(nsh):
                hb = read_hb('hb_n%d%s_%02d.json' % (n, tag, sh))
                ages[sh] = round(now - hb['t'], 1) if hb else None
            st = {'n': n, 'workers': nsh, 'gb_budget_s': budget, 'z3_ms': z3ms,
                  'wall_s': round(now - t0, 1),
                  'done': cur['done'], 'skipped_over_budget': cur['skipped'],
                  'unit_ideal': cur['unit_ideal'], 'unsat': cur['unsat'],
                  'SAT': len(cur['SAT']), 'z3_unknown': len(cur['z3_unknown']),
                  'errors': len(cur['errors']),
                  'delta_last_interval': delta, 'rate_per_s': round(rate, 3),
                  'HEALTHY': delta > 0,
                  'heartbeat_age_s': ages, 'kills': kills,
                  'finished_workers': sorted(finished),
                  'eta_hours': (round((total - cur['done'] - cur['skipped']) / rate / 3600, 2)
                                if rate > 0 else None),
                  'status': 'RUNNING'}
            json.dump(st, open(statusf, 'w'), indent=1)
            print('  %.0fs done=%d(+%d, %.2f/s) unit=%d unsat=%d SAT=%d unk=%d skip=%d '
                  'kills=%d healthy=%s eta=%sh'
                  % (now - t0, cur['done'], delta, rate, cur['unit_ideal'], cur['unsat'],
                     len(cur['SAT']), len(cur['z3_unknown']), cur['skipped'], kills,
                     st['HEALTHY'], st['eta_hours']), flush=True)
            last_tally, last_t = cur, now
        if len(finished) == nsh:
            break
    cur = tally(n, nsh, tag)
    st = {'n': n, 'workers': nsh, 'wall_s': round(time.time() - t0, 1),
          'done': cur['done'], 'skipped_over_budget': cur['skipped'],
          'unit_ideal': cur['unit_ideal'], 'unsat': cur['unsat'],
          'SAT': cur['SAT'], 'z3_unknown': cur['z3_unknown'], 'errors': cur['errors'],
          'kills': kills, 'status': 'COMPLETED'}
    json.dump(st, open(statusf, 'w'), indent=1)
    print('\nALL WORKERS EXHAUSTED %.0fs: done=%d refuted=%d (unit %d + unsat %d) '
          'SAT=%d z3_unknown=%d skipped=%d'
          % (st['wall_s'], cur['done'], cur['unit_ideal'] + cur['unsat'],
             cur['unit_ideal'], cur['unsat'], len(cur['SAT']),
             len(cur['z3_unknown']), cur['skipped']), flush=True)


if __name__ == '__main__':
    main()
