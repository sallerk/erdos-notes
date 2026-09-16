"""Light version: do 2- and 3-equation roots of the Case A system exist just OUTSIDE
caseA2's guards?  Guards off, roots collected, margins measured."""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, os, json, itertools
import numpy as np
from scipy.optimize import least_squares
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_caseA import splits, eqs_of, eqs_val, marg, resid

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
R = int(sys.argv[1]) if len(sys.argv) > 1 else 150
S = splits()
print('GUARDS OFF.  %d restarts. Roots = max|e| < 1e-11.' % R, flush=True)
print(' split                k  roots  best min_dist  best min_det4  best min_16K2  scale<40  ALL guards ok', flush=True)
for c0, c1 in S[:4]:
    eqs = eqs_of(c0, c1)
    for k in (2, 3, 4):
        rng = np.random.default_rng(555 + k)
        roots = []
        for _ in range(R):
            v0 = np.array([rng.uniform(-1.5, 2.5), rng.uniform(0.15, 2.5),
                           rng.uniform(-3, 4), rng.uniform(-3, 4)])
            try:
                s = least_squares(resid, v0, args=(eqs[:k], False, 1e-2, 1e-4),
                                  xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=2000)
            except Exception:
                continue
            e = eqs_val(s.x, eqs[:k])
            if e is None:
                continue
            if float(np.max(np.abs(e))) < 1e-11:
                m = marg(s.x)
                if m:
                    roots.append(m)
        if not roots:
            print(' %-20s %d  %5d   -- none --' % (str(c0) + '|' + str(c1), k, 0), flush=True)
            continue
        md = np.array([r['min_dist'] for r in roots])
        dd = np.array([r['min_det4'] for r in roots])
        kk = np.array([r['min_16K2'] for r in roots])
        sc = np.array([r['scale'] for r in roots])
        ok = (md > 1e-2) & (dd > 1e-4) & (kk > 1e-8) & (sc < 40)
        print(' %-20s %d  %5d   %.3e      %.3e      %.3e      %4d      %d'
              % (str(c0) + '|' + str(c1), k, len(roots), md.max(), dd.max(), kk.max(),
                 int((sc < 40).sum()), int(ok.sum())), flush=True)
