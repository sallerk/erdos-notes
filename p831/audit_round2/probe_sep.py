"""ROUND-2 PROBE 1b.  Sweep the CLASS-SEPARATION guard, which tausweep holds fixed.

If the floor tracks sep_tau with slope ~1, the OBSTRUCTED verdict is measuring the
constant 1e-3, exactly the defect the previous audit found for tau=1e-6.
"""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, json, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe_guards import floor_at, margins

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
pats = json.load(open('results/penum_n5_k3.json'))['patterns']
tw = {o['i']: o for o in json.load(open('results/tausweep_n5_k3.json'))['results']}
R = int(sys.argv[1]) if len(sys.argv) > 1 else 40
TAU = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-8   # guards near-off
SEPS = [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 1e-5]
rng = np.random.default_rng(90210)
print('PROBE 1b: floor vs the class-separation margin (tau fixed at %.0e), %d restarts' % (TAU, R))
print('  reported number = EQUALITY residual at the best point (penalties excluded)')
print('  i  tausweep-verdict  ' + ''.join('  sep=%-8.0e' % s for s in SEPS) + '   slope   NEW VERDICT')
out = []
for i, p in enumerate(pats):
    eqs = []
    for s in SEPS:
        c, v = floor_at(p['labels'], 3, TAU, s, 60.0, None, R, rng)
        m = margins(v, p['labels'], 3)
        eqs.append(m['eq'] if m else np.inf)
    ls = np.log10(SEPS); le = np.log10(np.maximum(eqs, 1e-300))
    sl = float(np.polyfit(ls, le, 1)[0])
    verdict = 'SEP-LIMITED' if sl > 0.5 else 'flat in sep'
    print('  %2d %-16s' % (i, tw[i]['verdict']) + ''.join('  %.3e' % e for e in eqs)
          + '   %+.2f   %s' % (sl, verdict))
    out.append(dict(i=i, old=tw[i]['verdict'], seps=SEPS, eq=[float(x) for x in eqs], slope=sl))
json.dump(out, open('audit_round2/probe1b_tau%.0e.json' % TAU, 'w'), indent=1)
