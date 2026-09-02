"""Re-derive D_gen(6) with NOTHING trusted to gram.py.

gram.py was found to emit false UNSAT verdicts: it calls sympy.solve and treats "no
solution returned" as unsatisfiable, but sympy.solve can silently omit branches.  17
conflicts with the robust decider were found at n=5,k=4, each one a genuine realisable
configuration that gram had called impossible.

So the seed set here comes ONLY from hard.py (Groebner + guaranteed-real roots), plus
pentagon.py's exact elimination for the one pattern hard.py cannot settle.  Candidates
are decided by hard.py as well.

Usage: python six2.py [workers] [seconds]
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

d = json.load(open('sweep_n5_k3_robust.json'))
seeds = set(tuple(p) for p in d['sat']) | set(tuple(p) for p in d['inconclusive'])
PENTAGON = (0, 0, 1, 1, 1, 0, 1, 1, 0, 0)
if PENTAGON in seeds:
    seeds.discard(PENTAGON)
    print('  pentagon dropped: proved unsat by exact elimination (pentagon.py),')
    print('  which is an independent proof, not a gram verdict')
print('  seeds (robust): %d' % len(seeds))

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
        if any(canon5(restrict(t, dd)) not in seeds for dd in range(6)):
            continue
        cands.add(canon(t, 6))
print('  %d canonical 6-point candidates  (%.1fs)' % (len(cands), time.time() - t0))
if not cands:
    print('  => no candidate, so D_gen(6) > 3 and D_gen(6) = 4')
    json.dump({'candidates': 0}, open('six2_result.json', 'w'), indent=1)
    sys.exit(0)


def job(pat):
    cmd = [sys.executable, os.path.join(HERE, 'hard.py'), '6', '3',
           ','.join(map(str, pat))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TMO, cwd=HERE)
    except subprocess.TimeoutExpired:
        return pat, 'timeout', None
    out = (p.stdout or '').strip().splitlines()
    if not out:
        return pat, 'error', (p.stderr or '')[-160:]
    try:
        j = json.loads(out[-1])
        return pat, j['r'], j.get('pts') or j.get('info')
    except Exception:
        return pat, 'error', out[-1][:160]


t0 = time.time()
buck = {}
with ThreadPoolExecutor(max_workers=W) as ex:
    for pat, r, info in ex.map(job, sorted(cands)):
        buck.setdefault(r, []).append((list(pat), info))
for r in sorted(buck):
    print('   %-13s %d' % (r, len(buck[r])))
print('   %.1fs' % (time.time() - t0))
json.dump({r: [x[0] for x in v] for r, v in buck.items()},
          open('six2_result.json', 'w'), indent=1)
print()
if buck.get('sat'):
    pat, info = buck['sat'][0]
    print('  SAT => D_gen(6) = 3, contradicting the earlier result. pattern %s' % (pat,))
    print('  %s' % (info,))
elif all(r in ('sat', 'unsat') for r in buck):
    print('  every candidate UNSAT => D_gen(6) > 3, so D_gen(6) = 4  [RE-ESTABLISHED]')
else:
    und = sum(len(buck.get(r, [])) for r in buck if r not in ('sat', 'unsat'))
    print('  NOT DECIDED: %d candidates undecided' % und)
    for pat, info in [x for r in buck if r not in ('sat', 'unsat') for x in buck[r]][:6]:
        print('     %s  (%s)' % (pat, str(info)[:90]))
