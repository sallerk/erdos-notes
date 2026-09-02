"""Run the robust decider over every pattern and cross-check against the gram.py sweep.

Two independent deciders disagreeing on a DECISIVE verdict (sat vs unsat) would mean one
of them is wrong, which would invalidate results built on it.  This looks for exactly
that.  One saying 'inconclusive' where the other decides is fine and expected.

Usage: python xcheck.py <n> <k> [seconds] [workers]
"""
import sys, json, subprocess, os, time
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
n, k = int(sys.argv[1]), int(sys.argv[2])
TMO = int(sys.argv[3]) if len(sys.argv) > 3 else 120
W = int(sys.argv[4]) if len(sys.argv) > 4 else 6
HERE = os.path.dirname(os.path.abspath(__file__))
old = json.load(open('sweep_n%d_k%d.json' % (n, k)))
verdict = {}
for r, ps in old.items():
    for p in ps:
        verdict[tuple(p)] = r
pats = list(verdict)
print('cross-checking %d patterns, n=%d k=%d' % (len(pats), n, k))


def run(pat):
    cmd = [sys.executable, os.path.join(HERE, 'hard.py'), str(n), str(k),
           ','.join(map(str, pat))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TMO, cwd=HERE)
    except subprocess.TimeoutExpired:
        return pat, 'timeout'
    out = (p.stdout or '').strip().splitlines()
    if not out:
        return pat, 'error'
    try:
        return pat, json.loads(out[-1])['r']
    except Exception:
        return pat, 'error'


t0 = time.time()
new = {}
with ThreadPoolExecutor(max_workers=W) as ex:
    for pat, r in ex.map(run, pats):
        new[pat] = r
DEC = ('sat', 'unsat')
conflict = [(p, verdict[p], new[p]) for p in pats
            if verdict[p] in DEC and new[p] in DEC and verdict[p] != new[p]]
buck = {}
for p in pats:
    buck.setdefault(new[p], []).append(list(p))
print('robust decider verdicts:')
for r in sorted(buck):
    print('   %-13s %d' % (r, len(buck[r])))
print('   %.1fs' % (time.time() - t0))
print()
print('CONFLICTS (both decisive, disagreeing): %d' % len(conflict))
for p, a, b in conflict[:10]:
    print('   %s  gram=%s  hard=%s' % (list(p), a, b))
json.dump({'robust': buck, 'conflicts': [[list(p), a, b] for p, a, b in conflict]},
          open('xcheck_n%d_k%d.json' % (n, k), 'w'), indent=1)
print()
print('written: xcheck_n%d_k%d.json' % (n, k))
if not conflict:
    print('NO CONFLICTS: the two deciders agree wherever both decide.')
