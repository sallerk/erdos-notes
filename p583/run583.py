"""Erdos #583 at n: sharded sweep, then exhaustive decision of the residue.

Stage 1  geng -qc n s/NSH  |  sweep12   -> hard_n<n>_<s>.g6
Stage 2  decide5 < hard_n<n>_<s>.g6     -> any counterexample, else all decomposable

Obeys the standing rules: at most 7 worker CPUs, and a health checkpoint
STATUS_583.json refreshed every 60 s whose HEALTHY field is a DELTA between reads,
not a state.

WHY THIS WAS REWRITTEN (2026-08-31).  The previous version launched its shards with
subprocess.Popen(['bash', '-lc', cmd]).  On this machine 'bash' resolves through the
Windows PATH to WSL's bash, which has no distro installed, so every shard died
instantly with "execvpe(/bin/bash) failed".  Three separate defects then combined to
turn that into a false success:

  * the health field was  delta > 0 or alive == 0,  so "every shard is dead" counted
    as healthy;
  * stage 1 broke out of its loop on alive == 0 without checking that any shard had
    reached COMPLETED;
  * the final report printed "VERIFIED" whenever counterexamples == 0, without
    requiring that a single graph had actually been swept.

The run reported "Erdos-Gallai path decomposition VERIFIED for all connected graphs on
12 vertices" after examining zero graphs.  The fixes below are, in order: launch the
executables directly with no shell; make the health check fail on no progress; require
every shard to reach COMPLETED; and check the total against the known number of
connected graphs (OEIS A001349) before any verification claim is printed.

Usage: python run583.py <n> <nshards<=7> [--wait-for FILE KEY VALUE] [--smoke]
"""
import subprocess, sys, os, json, time, glob

NSH = 7
N = 12
HERE = os.path.dirname(os.path.abspath(__file__))
GENG = None  # resolved lazily by _find_geng()
SWEEP = os.path.join(HERE, 'sweep12.exe')
DECIDE = os.path.join(HERE, 'decide5.exe')

# OEIS A001349, connected graphs on n nodes.  The sweep is exhaustive if and only if
# the shard counts sum to this, so it is checked, not assumed.
A001349 = {1: 1, 2: 1, 3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117, 9: 261080,
           10: 11716571, 11: 1006700565, 12: 164059830476}


def _find_geng():
    """nauty is a third-party dependency and is deliberately NOT vendored here.
    Look for geng in this order: the $GENG environment variable, then PATH, then a
    sibling tools/ directory (the author's layout).  Fail with instructions rather
    than a traceback."""
    import shutil
    cands = []
    if os.environ.get('GENG'):
        cands.append(os.environ['GENG'])
    for nm in ('geng.exe', 'geng'):
        w = shutil.which(nm)
        if w:
            cands.append(w)
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (('..', 'tools', 'nauty2_9_3', 'geng.exe'),
                ('..', 'tools', 'nauty2_9_3', 'geng')):
        cands.append(os.path.join(here, *rel))
    for c in cands:
        if c and os.path.exists(c):
            return c
    msg = ["geng (from nauty) was not found.",
           "  nauty is not bundled with this repository. Install it from",
           "  https://pallini.di.uniroma1.it/ and then either put geng on your PATH,",
           "  or set GENG=/path/to/geng before running this script."]
    sys.exit(chr(10).join(msg))


def read(f):
    try:
        return json.load(open(f))
    except Exception:
        return None


def preflight():
    """A missing or broken tool must be reported as a broken tool, never as a result."""
    global GENG
    GENG = _find_geng()
    for p in (GENG, SWEEP, DECIDE):
        if not os.path.exists(p):
            sys.exit('PREFLIGHT FAILED: missing executable %s' % os.path.normpath(p))
    # geng must actually emit graphs.  Count connected graphs on 7 nodes: 853.
    r = subprocess.run([GENG, '-qc', '7'], capture_output=True, timeout=120)
    got = len([l for l in r.stdout.split(b'\n') if l.strip()])
    if r.returncode != 0 or got != A001349[7]:
        sys.exit('PREFLIGHT FAILED: geng -qc 7 gave %d graphs (rc=%d), expected %d.\n%s'
                 % (got, r.returncode, A001349[7], r.stderr.decode()[:300]))
    print('preflight: geng -qc 7 -> %d connected graphs, as expected' % got, flush=True)


def launch_sweep(n, s, nsh):
    """geng | sweep12, wired directly with no shell of any kind."""
    g6 = open(os.path.join(HERE, 'hard_n%d_%d.g6' % (n, s)), 'wb')
    err = open(os.path.join(HERE, 'swlog_%d.txt' % s), 'wb')
    gen = subprocess.Popen([GENG, '-qc', str(n), '%d/%d' % (s, nsh)],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    swp = subprocess.Popen([SWEEP, 'hb583_%d.json' % s, '40'],
                           stdin=gen.stdout, stdout=g6, stderr=err, cwd=HERE)
    gen.stdout.close()          # so sweep sees EOF when geng exits
    return gen, swp


def smoke(nsh):
    """Run the whole stage-1 pipeline at n=10, where the answer is known."""
    print('SMOKE TEST at n=10 (expect %d connected graphs)' % A001349[10], flush=True)
    for f in glob.glob(os.path.join(HERE, 'hb583_*.json')):
        os.remove(f)
    pairs = [launch_sweep(10, s, nsh) for s in range(nsh)]
    for gen, swp in pairs:
        swp.wait(); gen.wait()
    tot = done = 0
    for s in range(nsh):
        d = read(os.path.join(HERE, 'hb583_%d.json' % s)) or {}
        tot += d.get('graphs', 0)
        done += (d.get('status') == 'COMPLETED')
    ok = (tot == A001349[10] and done == nsh)
    print('SMOKE: swept %d graphs across %d/%d completed shards -> %s'
          % (tot, done, nsh, 'PASS' if ok else 'FAIL'), flush=True)
    return ok


def main():
    global N, NSH
    args = sys.argv[1:]
    wait = None
    dosmoke = '--smoke' in args
    if dosmoke:
        args.remove('--smoke')
    if '--wait-for' in args:
        i = args.index('--wait-for')
        wait = (args[i + 1], args[i + 2], args[i + 3])
        args = args[:i] + args[i + 4:]
    if len(args) >= 1:
        N = int(args[0])
    if len(args) >= 2:
        NSH = int(args[1])
    assert NSH <= 7, 'user rule: at most 7 CPUs per task'

    preflight()
    if dosmoke and not smoke(NSH):
        sys.exit('SMOKE TEST FAILED -- not starting the real run')

    if wait:
        f, k, v = wait
        print('waiting for %s[%s] == %s ...' % (f, k, v), flush=True)
        while True:
            d = read(f)
            if d and str(d.get(k)) == v:
                break
            json.dump({'status': 'WAITING', 'waiting_on': f,
                       'checked': time.strftime('%H:%M:%S')},
                      open(os.path.join(HERE, 'STATUS_583.json'), 'w'), indent=1)
            time.sleep(60)
        print('dependency satisfied, starting', flush=True)

    for f in glob.glob(os.path.join(HERE, 'hb583_*.json')):
        os.remove(f)

    # ---------------------------------------------------------------- stage 1
    pairs = [launch_sweep(N, s, NSH) for s in range(NSH)]
    print('stage 1: launched %d sweep shards for n=%d' % (NSH, N), flush=True)
    t0 = time.time()
    last = 0
    stall = 0
    while True:
        time.sleep(60)
        alive = sum(1 for _, swp in pairs if swp.poll() is None)
        tot = hard = filt = done = 0
        ages = []
        for s in range(NSH):
            hb = os.path.join(HERE, 'hb583_%d.json' % s)
            d = read(hb)
            if d:
                tot += d.get('graphs', 0); hard += d.get('hard', 0)
                filt += d.get('filtered', 0)
                if d.get('status') == 'COMPLETED':
                    done += 1
                ages.append(round(time.time() - os.path.getmtime(hb), 1))
        delta = tot - last
        last = tot
        el = time.time() - t0
        # A dead shard that never completed is a FAILURE, not a finish.  Progress
        # means graphs actually swept; "nothing is running" is never healthy unless
        # everything completed.
        healthy = (delta > 0) or (done == NSH)
        if not healthy:
            stall += 1
        else:
            stall = 0
        st = {'problem': 583, 'n': N, 'stage': 1, 'nshards': NSH, 'alive': alive,
              'shards_completed': done, 'graphs_swept': tot,
              'graphs_delta_last_60s': delta, 'HEALTHY': healthy,
              'stalled_intervals': stall,
              'filtered_by_cited_theorem': filt, 'hard_so_far': hard,
              'elapsed_s': round(el, 1),
              'rate_per_s': round(tot / el, 0) if el else 0,
              'heartbeat_age_s': ages, 'status': 'RUNNING'}
        json.dump(st, open(os.path.join(HERE, 'STATUS_583.json'), 'w'), indent=1)
        print('  stage1 %.0fs alive=%d done=%d/%d swept=%.6g (+%.4g) hard=%d healthy=%s'
              % (el, alive, done, NSH, tot, delta, hard, healthy), flush=True)
        if alive == 0:
            break
        if stall >= 5:
            for _, swp in pairs:
                swp.kill()
            sys.exit('ABORTED: no graphs swept in 5 consecutive minutes with shards '
                     'still alive; investigate rather than trusting this run.')
    sweep_secs = time.time() - t0

    tot = hard = filt = done = 0
    for s in range(NSH):
        d = read(os.path.join(HERE, 'hb583_%d.json' % s))
        if d:
            tot += d.get('graphs', 0); hard += d.get('hard', 0)
            filt += d.get('filtered', 0)
            if d.get('status') == 'COMPLETED':
                done += 1
    print('stage 1 done: %d graphs, %d filtered, %d hard, %.0fs, %d/%d shards COMPLETED'
          % (tot, filt, hard, sweep_secs, done, NSH), flush=True)

    # --- the two gates that the previous version lacked ---
    if done != NSH:
        sys.exit('FAILED: only %d of %d shards reached COMPLETED. The sweep is NOT '
                 'exhaustive and nothing may be concluded from it.' % (done, NSH))
    expect = A001349.get(N)
    if expect is not None and tot != expect:
        sys.exit('FAILED: swept %d connected graphs but OEIS A001349(%d) = %d. The '
                 'shards do not partition the space; nothing may be concluded.'
                 % (tot, N, expect))
    if expect is not None:
        print('CHECK: swept count equals OEIS A001349(%d) = %d, so the shard split '
              'was an exhaustive partition.' % (N, expect), flush=True)

    # ---------------------------------------------------------------- stage 2
    procs = []
    for s in range(NSH):
        inp = open(os.path.join(HERE, 'hard_n%d_%d.g6' % (N, s)), 'rb')
        out = open(os.path.join(HERE, 'counter_n%d_%d.txt' % (N, s)), 'wb')
        err = open(os.path.join(HERE, 'dlog_%d.txt' % s), 'wb')
        procs.append(subprocess.Popen([DECIDE, '500000000'], stdin=inp, stdout=out,
                                      stderr=err, cwd=HERE))
    print('stage 2: deciding the residue on %d shards' % NSH, flush=True)
    t1 = time.time()
    while True:
        time.sleep(60)
        alive = sum(1 for p in procs if p.poll() is None)
        ctr = sum(sum(1 for _ in open(os.path.join(HERE, 'counter_n%d_%d.txt' % (N, s))))
                  for s in range(NSH)
                  if os.path.exists(os.path.join(HERE, 'counter_n%d_%d.txt' % (N, s))))
        json.dump({'problem': 583, 'n': N, 'stage': 2, 'alive': alive,
                   'counterexamples_so_far': ctr,
                   'elapsed_s': round(time.time() - t1, 1),
                   'sweep_seconds': round(sweep_secs, 1),
                   'graphs_swept': tot, 'hard': hard, 'status': 'RUNNING'},
                  open(os.path.join(HERE, 'STATUS_583.json'), 'w'), indent=1)
        print('  stage2 %.0fs alive=%d counterexamples=%d'
              % (time.time() - t1, alive, ctr), flush=True)
        if alive == 0:
            break

    rcs = [p.returncode for p in procs]
    ctr = sum(sum(1 for _ in open(os.path.join(HERE, 'counter_n%d_%d.txt' % (N, s))))
              for s in range(NSH)
              if os.path.exists(os.path.join(HERE, 'counter_n%d_%d.txt' % (N, s))))
    undec = 0
    decided = 0
    for s in range(NSH):
        try:
            for ln in open(os.path.join(HERE, 'dlog_%d.txt' % s)):
                if 'undecided(cap)=' in ln:
                    undec += int(ln.split('undecided(cap)=')[1].split()[0])
                if 'decided=' in ln:
                    decided += int(ln.split('decided=')[1].split()[0])
        except Exception:
            pass

    final = {'problem': 583, 'n': N, 'nshards': NSH,
             'graphs_swept': tot, 'expected_connected_graphs': expect,
             'sweep_exhaustive': (expect is None or tot == expect),
             'shards_completed': done,
             'filtered_by_cited_theorem': filt,
             'hard': hard, 'residue_decided': decided,
             'counterexamples': ctr, 'undecided': undec,
             'decider_returncodes': rcs,
             'sweep_seconds': round(sweep_secs, 1),
             'decide_seconds': round(time.time() - t1, 1),
             'status': 'COMPLETED'}
    json.dump(final, open(os.path.join(HERE, 'STATUS_583.json'), 'w'), indent=1)
    json.dump(final, open(os.path.join(HERE, 'RESULT_583_n%d.json' % N), 'w'), indent=1)
    print('\nn=%d COMPLETE: swept=%d filtered=%d hard=%d COUNTEREXAMPLES=%d undecided=%d'
          % (N, tot, filt, hard, ctr, undec), flush=True)

    problems = []
    if tot == 0:
        problems.append('zero graphs swept')
    if done != NSH:
        problems.append('%d/%d shards completed' % (done, NSH))
    if expect is not None and tot != expect:
        problems.append('swept != A001349(%d)' % N)
    if any(rc != 0 for rc in rcs):
        problems.append('decider exit codes %s' % rcs)
    if undec:
        problems.append('%d graphs undecided' % undec)
    if problems:
        sys.exit('NOT VERIFIED -- ' + '; '.join(problems))
    if ctr == 0:
        print('==> Erdos-Gallai path decomposition VERIFIED for all %d connected '
              'graphs on %d vertices.' % (tot, N), flush=True)
    else:
        print('==> %d COUNTEREXAMPLE(S) FOUND; see counter_n%d_*.txt' % (ctr, N),
              flush=True)


if __name__ == '__main__':
    main()
