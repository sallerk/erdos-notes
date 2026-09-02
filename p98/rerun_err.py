"""Re-decide the patterns a stage recorded as 'error'.

Those were not decider failures: a sampled one reproduces cleanly as unsat when run
alone, so they came from subprocess contention under many workers.  Re-running them with
fewer workers and a longer cap shrinks the seed set for the next stage.

Usage: python rerun_err.py <n> <k> <stagefile> <outfile> [seconds] [workers]
"""
import sys, json, subprocess, os, time
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
n, k = int(sys.argv[1]), int(sys.argv[2])
sf, of = sys.argv[3], sys.argv[4]
TMO = int(sys.argv[5]) if len(sys.argv) > 5 else 240
W = int(sys.argv[6]) if len(sys.argv) > 6 else 3
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sf))
todo = [tuple(p) for p in d.get('error', [])]
print('re-deciding %d error patterns, n=%d k=%d, %ds cap, %d workers'
      % (len(todo), n, k, TMO, W))


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
buck = {}
with ThreadPoolExecutor(max_workers=W) as ex:
    for pat, r in ex.map(run, todo):
        buck.setdefault(r, []).append(list(pat))
for r in sorted(buck):
    print('   %-13s %d' % (r, len(buck[r])))
print('   %.1fs' % (time.time() - t0))
merged = {
    'sat': d.get('sat', []) + buck.get('sat', []),
    'unsat': d.get('unsat', []) + buck.get('unsat', []),
    'undecided': (d.get('inconclusive', []) + d.get('timeout', [])
                  + buck.get('inconclusive', []) + buck.get('timeout', [])
                  + buck.get('error', [])),
}
json.dump(merged, open(of, 'w'), indent=1)
print()
print('   merged: sat %d, unsat %d, undecided %d'
      % (len(merged['sat']), len(merged['unsat']), len(merged['undecided'])))
print('   seeds for the next stage: %d  (was %d)'
      % (len(merged['sat']) + len(merged['undecided']),
         len(d.get('sat', [])) + len(d.get('inconclusive', []))
         + len(d.get('timeout', [])) + len(todo)))
print('   written: %s' % of)
