"""Decide D_gen(6) exactly: augment realisable 5-point patterns, decide with the Gram method.

Pipeline:
  1. sweep.py 5 3   decides every 5-point pattern with at most 3 classes, exactly.
  2. here           extend each possibly-realisable 5-pattern by a sixth point, keep
                    those whose six 5-subsets are all possibly-realisable, and decide
                    the survivors with the same exact Gram decider.

Completeness.  Deleting a point from a general-position set leaves a general-position set
with no more distances, so every realisable 6-pattern restricts to a realisable 5-pattern
on all six 5-subsets.  Seeding from every non-UNSAT 5-pattern (sat AND inconclusive) is
therefore complete.  Extending a canonical representative by all 3^5 colourings of the
new point's edges reaches every 6-pattern up to isomorphism, because any 6-pattern can be
relabelled so that its first five points match the canonical representative.

Monotonicity gives D_gen(6) >= D_gen(5) = 3, and a verified lattice witness gives <= 4,
so the only question is whether some 6-point pattern with 3 classes is realisable.

Usage:  python six.py [workers]
"""
import sys, itertools, json, time, os, subprocess
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from hdecide import pairs
from witness import vertex_ok
from extend import canon, canon5, restrict

W = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TMO = int(sys.argv[2]) if len(sys.argv) > 2 else 300
HERE = os.path.dirname(os.path.abspath(__file__))


def job(pat):
    """One pattern, in its own process with a hard cap; sympy.solve can hang outright."""
    cmd = [sys.executable, os.path.join(HERE, 'decide1.py'), '6', '3',
           ','.join(map(str, pat))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TMO, cwd=HERE)
    except subprocess.TimeoutExpired:
        return pat, 'timeout', '%ds' % TMO, None
    out = (p.stdout or '').strip().splitlines()
    if not out:
        return pat, 'error', (p.stderr or '')[-200:], None
    try:
        d = json.loads(out[-1])
        return pat, d['r'], d['vals'], d['pts']
    except Exception:
        return pat, 'error', out[-1][:200], None


if __name__ == '__main__':
    print('=' * 74)
    print('D_gen(6): is any 6-point 3-distance pattern realisable in general position?')
    print('=' * 74)
    s5 = json.load(open('sweep_n5_k3.json'))
    seeds = set()
    # 'timeout' MUST be in this list: a pattern the decider ran out of time on is
    # undecided, not refuted, and dropping it would break completeness.
    for key in ('sat', 'inconclusive', 'error', 'timeout'):
        for p in s5.get(key, []):
            seeds.add(tuple(p))
    # ...except the pentagon pattern, which pentagon.py PROVED unsatisfiable by exact
    # elimination (eliminant t^2-3t+1, every real branch cocircular).  The Gram decider
    # returns 'inconclusive' on it only because sympy leaves branches unevaluated.
    PENTAGON = (0, 0, 1, 1, 1, 0, 1, 1, 0, 0)
    if PENTAGON in seeds:
        seeds.discard(PENTAGON)
        print('  (pentagon pattern dropped: proved unsat by pentagon.py, not by Gram)')
    print('  seeds: %d possibly-realisable 5-patterns  (sat %d, inconclusive %d, error %d)'
          % (len(seeds), len(s5.get('sat', [])), len(s5.get('inconclusive', [])),
             len(s5.get('error', []))))
    print('  (unsat 5-patterns: %d, correctly excluded)' % len(s5.get('unsat', [])))
    if not seeds:
        print('  no realisable 5-pattern with 3 classes -- contradicts D_gen(5)=3, abort')
        sys.exit(1)

    idx6 = {p: i for i, p in enumerate(pairs(6))}
    t0 = time.time()
    cands = set()
    for seed in seeds:
        base = dict(zip(pairs(5), seed))
        for newc in itertools.product(range(3), repeat=5):
            full = [0] * 15
            for (i, j), c in base.items():
                full[idx6[(i, j)]] = c
            for v in range(5):
                full[idx6[(v, 5)]] = newc[v]
            t = tuple(full)
            if not vertex_ok(t, 6):
                continue
            if any(canon5(restrict(t, d)) not in seeds for d in range(6)):
                continue
            cands.add(canon(t, 6))
    print('  %d canonical 6-point candidates after augmentation + subset filter  (%.1fs)'
          % (len(cands), time.time() - t0))

    if not cands:
        print()
        print('  => no candidate survives, so D_gen(6) > 3, hence D_gen(6) = 4')
        json.dump({'candidates': 0, 'conclusion': 'D_gen(6) = 4'},
                  open('six_result.json', 'w'), indent=1)
        sys.exit(0)

    t0 = time.time()
    buck = {}
    with ThreadPoolExecutor(max_workers=W) as ex:
        for pat, r, vv, pts in ex.map(job, sorted(cands)):
            buck.setdefault(r, []).append((list(pat), vv, pts))
    print()
    for r in sorted(buck):
        print('   %-13s %d' % (r, len(buck[r])))
    print('   %.1fs' % (time.time() - t0))
    json.dump({r: [x[0] for x in v] for r, v in buck.items()},
              open('six_result.json', 'w'), indent=1)

    print()
    if buck.get('sat'):
        pat, vv, pts = buck['sat'][0]
        print('  SAT => D_gen(6) = 3')
        print('    pattern %s' % (pat,))
        print('    classes %s' % vv)
        print('    points  %s' % pts)
    elif all(r in ('sat','unsat') for r in buck):
        print('  every candidate UNSAT => D_gen(6) > 3')
        print('  with the verified 4-distance witness, D_gen(6) = 4')
    else:
        print('  NOT DECIDED: %d inconclusive, %d error'
              % (len(buck.get('inconclusive', [])), len(buck.get('error', []))))
