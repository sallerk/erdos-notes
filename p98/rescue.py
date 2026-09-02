"""Re-decide the patterns gram.py left undecided, using the robust decider (hard.py).

Reads sweep_n<n>_k<k>.json, takes every pattern in a non-decisive bucket
(inconclusive / timeout / error), and re-runs it through hard.py in its own process with
a hard cap.  Writes rescue_n<n>_k<k>.json.  Anything still undecided stays undecided;
nothing is downgraded to unsat without a proof.

Usage: python rescue.py <n> <k> [seconds] [workers]
"""
import sys, json, subprocess, os, time
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
n, k = int(sys.argv[1]), int(sys.argv[2])
TMO = int(sys.argv[3]) if len(sys.argv) > 3 else 300
W = int(sys.argv[4]) if len(sys.argv) > 4 else 6
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open('sweep_n%d_k%d.json' % (n, k)))
todo = []
for key in ('inconclusive', 'timeout', 'error'):
    todo += [tuple(p) for p in d.get(key, [])]
print('re-deciding %d undecided patterns with the robust decider (%ds cap, %d workers)'
      % (len(todo), TMO, W))


def run(pat):
    cmd = [sys.executable, os.path.join(HERE, 'hard.py'), str(n), str(k),
           ','.join(map(str, pat))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TMO, cwd=HERE)
    except subprocess.TimeoutExpired:
        return pat, {'r': 'timeout'}
    out = (p.stdout or '').strip().splitlines()
    if not out:
        return pat, {'r': 'error', 'info': (p.stderr or '')[-160:]}
    try:
        return pat, json.loads(out[-1])
    except Exception:
        return pat, {'r': 'error', 'info': out[-1][:160]}


t0 = time.time()
buck = {}
with ThreadPoolExecutor(max_workers=W) as ex:
    for pat, res in ex.map(run, todo):
        buck.setdefault(res['r'], []).append(list(pat))
for r in sorted(buck):
    print('   %-13s %d' % (r, len(buck[r])))
print('   %.1fs' % (time.time() - t0))
json.dump(buck, open('rescue_n%d_k%d.json' % (n, k), 'w'), indent=1)
still = sum(len(buck.get(r, [])) for r in ('inconclusive', 'timeout', 'error'))
print()
print('   resolved to unsat : %d' % len(buck.get('unsat', [])))
print('   resolved to sat   : %d' % len(buck.get('sat', [])))
print('   still undecided   : %d' % still)
old_sat = len(d.get('sat', []))
print()
print('   seed set for augmentation: was %d, now %d'
      % (old_sat + len(todo), old_sat + len(buck.get('sat', [])) + still))
