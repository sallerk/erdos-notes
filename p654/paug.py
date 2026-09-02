"""Augmentation: build n-point pinned patterns from realisable (n-1)-point ones.

WHY.  Raw enumeration at m=3 explodes: penum.enumerate_pinned(6,3,3) does not finish in
270s, because the colour budget k <= n*m/2 is 9 and the per-vertex constraint is no longer
tight enough to prune early.  Augmentation replaces "all patterns" by "extensions of the
ones that survived at the previous size", which is the same device #98 used.

COMPLETENESS.  Deleting a point from a configuration leaves a configuration, in the same
hypothesis class, whose pinned counts are all <= the originals.  So every realisable
n-point pattern with M <= m restricts, on the first n-1 points, to a realisable
(n-1)-point pattern with M <= m.  Enumerating extensions of every such seed therefore
reaches every realisable n-point pattern up to relabelling, provided the seed set is
CLOSED under relabelling -- which it is, since seeds are canonical representatives and we
extend a canonical representative by every admissible colouring of the new edges.

THE NEW EDGES.  pairs(n) lists (i,j) with i<j in lexicographic order, so the edges at the
new point n-1 are exactly those with j = n-1, and they are NOT contiguous in that list.
The mapping below places each seed colour at the position of its own pair in pairs(n).

Usage:  python paug.py <n> <m> <g|n4> <seedfile>
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from common import pairs, canonical                      # noqa: E402
from penum import pinned_counts, max_class_at_vertex     # noqa: E402
from plemmas import survives                             # noqa: E402


def extensions(seed, n, m, cap=3):
    """All colourings of the n-1 new edges at point n-1, given a seed on n-1 points."""
    Pn = pairs(n)
    Pp = pairs(n - 1)
    ppidx = {p: i for i, p in enumerate(Pp)}
    base = [None] * len(Pn)
    newpos = []
    for e, (i, j) in enumerate(Pn):
        if j == n - 1:
            newpos.append((e, i))
        else:
            base[e] = seed[ppidx[(i, j)]]
    kseed = max(seed) + 1
    kmax = (n * m) // 2

    # current colour usage at each of the old vertices
    cnt = [dict() for _ in range(n)]
    for e, (i, j) in enumerate(Pn):
        if base[e] is None:
            continue
        cnt[i][base[e]] = cnt[i].get(base[e], 0) + 1
        cnt[j][base[e]] = cnt[j].get(base[e], 0) + 1

    out = []
    pat = list(base)

    def rec(t, ncol):
        if t == len(newpos):
            out.append(tuple(pat))
            return
        e, i = newpos[t]
        j = n - 1
        for c in range(min(ncol, kmax - 1) + 1):
            ni, nj = cnt[i].get(c, 0), cnt[j].get(c, 0)
            if ni >= cap or nj >= cap:
                continue
            if ni == 0 and len(cnt[i]) >= m:
                continue
            if nj == 0 and len(cnt[j]) >= m:
                continue
            cnt[i][c] = ni + 1
            cnt[j][c] = nj + 1
            pat[e] = c
            rec(t + 1, max(ncol, c + 1))
            pat[e] = None
            if ni:
                cnt[i][c] = ni
            else:
                del cnt[i][c]
            if nj:
                cnt[j][c] = nj
            else:
                del cnt[j][c]

    rec(0, kseed)
    return out


if __name__ == '__main__':
    n, m, mode = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    sf = sys.argv[4]
    seeds = [tuple(p) for p in json.load(open(sf))['patterns']]
    print('augmenting %d seeds on %d points -> %d points, m=%d, mode=%s'
          % (len(seeds), n - 1, n, m, mode))
    P = pairs(n)
    index = {p: i for i, p in enumerate(P)}
    t0 = time.time()
    raw = 0
    keep = {}
    killed = {'pinned': 0, 'cap': 0}
    lemma = {}
    for si, s in enumerate(seeds):
        for e in extensions(s, n, m):
            raw += 1
            if max(pinned_counts(e, n)) > m:
                killed['pinned'] += 1
                continue
            if max_class_at_vertex(e, n) > 3:
                killed['cap'] += 1
                continue
            ok, why = survives(e, n, mode)
            if not ok:
                lemma[why] = lemma.get(why, 0) + 1
                continue
            c = canonical(e, n, P, index)
            keep.setdefault(c, e)
        if (si + 1) % 25 == 0 or si + 1 == len(seeds):
            print('   seed %d/%d: raw %d, surviving canonical %d   %.1fs'
                  % (si + 1, len(seeds), raw, len(keep), time.time() - t0))
    print()
    print('  raw extensions       %d' % raw)
    print('  killed by pinned cap %d' % killed['pinned'])
    print('  killed by 3-per-vtx  %d' % killed['cap'])
    for k2, v in sorted(lemma.items()):
        print('  killed by %-12s %d' % (k2, v))
    print('  surviving canonical  %d' % len(keep))
    fn = 'paug_n%d_m%d_%s.json' % (n, m, mode)
    json.dump({'n': n, 'm': m, 'mode': mode, 'seedfile': sf, 'raw': raw,
               'killed': killed, 'lemma': lemma, 'canonical': len(keep),
               'patterns': [list(c) for c in sorted(keep)]}, open(fn, 'w'), indent=1)
    print('  written: %s' % fn)
