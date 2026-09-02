"""Parallel sweep with a HARD per-pattern timeout.

A timeout is reported as 'timeout', which is a flavour of inconclusive.  It is never
counted as unsat: a lower-bound claim requires sat=0 AND every other bucket empty.

Usage: python sweep2.py <n> <k> [per_pattern_seconds] [workers]
"""
import sys, json, time, subprocess, os
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from hdecide import enumerate_patterns
from witness import vertex_ok

n, k = int(sys.argv[1]), int(sys.argv[2])
TMO = int(sys.argv[3]) if len(sys.argv) > 3 else 120
W = int(sys.argv[4]) if len(sys.argv) > 4 else 6
HERE = os.path.dirname(os.path.abspath(__file__))


def run(pat):
    cmd = [sys.executable, os.path.join(HERE, 'decide1.py'), str(n), str(k),
           ','.join(map(str, pat))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TMO, cwd=HERE)
    except subprocess.TimeoutExpired:
        return pat, {'r': 'timeout', 'vals': '%ds' % TMO, 'pts': None}
    line = (p.stdout or '').strip().splitlines()
    if not line:
        return pat, {'r': 'error', 'vals': (p.stderr or '')[-200:], 'pts': None}
    try:
        return pat, json.loads(line[-1])
    except Exception:
        return pat, {'r': 'error', 'vals': line[-1][:200], 'pts': None}


pats = [p for p in enumerate_patterns(n, k) if vertex_ok(p, n)]
print('n=%d k=%d: %d patterns, %ds per-pattern cap, %d workers' % (n, k, len(pats), TMO, W))
t0 = time.time()
buck = {}
with ThreadPoolExecutor(max_workers=W) as ex:
    for pat, res in ex.map(run, pats):
        buck.setdefault(res['r'], []).append((list(pat), res['vals'], res['pts']))
for r in sorted(buck):
    print('   %-13s %d' % (r, len(buck[r])))
print('   %.1fs' % (time.time() - t0))
json.dump({r: [x[0] for x in v] for r, v in buck.items()},
          open('sweep_n%d_k%d.json' % (n, k), 'w'), indent=1)
for pat, vals, pts in buck.get('sat', [])[:3]:
    print('   SAT %s\n       classes %s\n       points  %s' % (pat, vals, pts))
for pat, vals, pts in (buck.get('timeout', []) + buck.get('inconclusive', [])
                       + buck.get('error', []))[:8]:
    print('   UNDECIDED %s  (%s)' % (pat, vals))
clean = all(r in ('sat', 'unsat') for r in buck)
print()
if buck.get('sat'):
    print('   => D_gen(%d) <= %d' % (n, k))
elif clean:
    print('   => D_gen(%d) > %d  (all decided, none realisable)' % (n, k))
else:
    print('   => NOT DECIDED')
