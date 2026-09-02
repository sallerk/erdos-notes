"""Decide a candidate file with the robust decider, in parallel with hard caps.

Usage: python dec.py <n> <k> <candfile> <outfile> [seconds] [workers]
"""
import sys, json, subprocess, os, time
from concurrent.futures import ThreadPoolExecutor
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
n, k = int(sys.argv[1]), int(sys.argv[2])
cf, of = sys.argv[3], sys.argv[4]
TMO = int(sys.argv[5]) if len(sys.argv) > 5 else 120
W = int(sys.argv[6]) if len(sys.argv) > 6 else 6
HERE = os.path.dirname(os.path.abspath(__file__))
cands = [tuple(p) for p in json.load(open(cf))['candidates']]
print('deciding %d candidates, n=%d k=%d, %ds cap, %d workers' % (len(cands), n, k, TMO, W))


def run(pat):
    cmd = [sys.executable, os.path.join(HERE, 'hard.py'), str(n), str(k),
           ','.join(map(str, pat))]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TMO, cwd=HERE)
    except subprocess.TimeoutExpired:
        return pat, 'timeout', None
    out = (p.stdout or '').strip().splitlines()
    if not out:
        return pat, 'error', (p.stderr or '')[-140:]
    try:
        j = json.loads(out[-1])
        return pat, j['r'], (j.get('pts') if j['r'] == 'sat' else j.get('info'))
    except Exception:
        return pat, 'error', out[-1][:140]


t0 = time.time()
buck = {}
done = 0
with ThreadPoolExecutor(max_workers=W) as ex:
    for pat, r, info in ex.map(run, cands):
        buck.setdefault(r, []).append((list(pat), info))
        done += 1
        if done % 250 == 0:
            print('   %d/%d  %.0fs  %s' % (done, len(cands), time.time() - t0,
                                           {a: len(b) for a, b in buck.items()}))
print()
for r in sorted(buck):
    print('   %-13s %d' % (r, len(buck[r])))
print('   %.1fs' % (time.time() - t0))
json.dump({r: [x[0] for x in v] for r, v in buck.items()}, open(of, 'w'), indent=1)
print('   written: %s' % of)
if buck.get('sat'):
    pat, info = buck['sat'][0]
    print()
    print('   SAT example: %s' % (pat,))
    print('   %s' % (info,))
