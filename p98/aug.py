"""Augment an n-point seed set to n+1 points, applying every sound filter.

Filters, all sound (none can remove a realisable pattern):
  * the full lemma set in lemmas.py (L1 degree, L2 K(2,3), L3 bisector,
    L4 circumcentre, L5 equilateral-centre) -- all sound, all solver-free
  * every (n)-subset must be a seed, i.e. not PROVEN unsat  (monotonicity)

Usage: python aug.py <n_from> <k> <seedfile> <outfile>
"""
import sys, itertools, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from hdecide import pairs
from lemmas import survives as filt
from extend import canon

nf = int(sys.argv[1]); k = int(sys.argv[2])
seedfile = sys.argv[3]; outfile = sys.argv[4]
nt = nf + 1
d = json.load(open(seedfile))
seeds = set(tuple(p) for p in d.get('sat', [])) | set(tuple(p) for p in d.get('undecided', []))
print('augmenting %d seeds from n=%d to n=%d, k=%d' % (len(seeds), nf, nt, k))

Pf = pairs(nf); Pt = pairs(nt)
idxt = {p: i for i, p in enumerate(Pt)}
_c = {}


def canonf(pat):
    v = _c.get(pat)
    if v is None:
        v = canon(pat, nf); _c[pat] = v
    return v


def restrict(pat, drop):
    keep = [v for v in range(nt) if v != drop]
    out = []
    for (i, j) in itertools.combinations(range(nf), 2):
        a, b = keep[i], keep[j]
        out.append(pat[idxt[(a, b) if a < b else (b, a)]])
    seen, ren = {}, []
    for c in out:
        if c not in seen:
            seen[c] = len(seen)
        ren.append(seen[c])
    return tuple(ren)


t0 = time.time()
raw = passfilt = passsub = 0
cands = set()
for si, seed in enumerate(seeds):
    base = dict(zip(Pf, seed))
    for newc in itertools.product(range(k), repeat=nf):
        raw += 1
        full = [0] * len(Pt)
        for (i, j), c in base.items():
            full[idxt[(i, j)]] = c
        for v in range(nf):
            full[idxt[(v, nf)]] = newc[v]
        t = tuple(full)
        if not filt(t, nt):
            continue
        passfilt += 1
        if any(canonf(restrict(t, dd)) not in seeds for dd in range(nt)):
            continue
        passsub += 1
        cands.add(canon(t, nt))
    if (si + 1) % 25 == 0:
        print('   %d/%d seeds, %d candidates so far, %.0fs'
              % (si + 1, len(seeds), len(cands), time.time() - t0))
print()
print('  raw extensions            : %d' % raw)
print('  survive degree + K23      : %d' % passfilt)
print('  survive the subset test   : %d' % passsub)
print('  distinct up to isomorphism: %d   (%.0fs)' % (len(cands), time.time() - t0))
json.dump({'candidates': [list(c) for c in sorted(cands)]}, open(outfile, 'w'), indent=1)
print('  written: %s' % outfile)
