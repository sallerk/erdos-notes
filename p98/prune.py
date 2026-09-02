"""Purely combinatorial filters on distance patterns, from elementary geometry.

Both are sound for ANY planar point set with the general-position hypotheses, need no
solver, and are cheap.  They come out of the arguments that killed two of the three
n=6 candidates by hand.

FILTER 1 (degree).  No four points are cocircular, so at most three points lie at any
given distance from a given point: four would sit on a circle centred there.  Hence in
each distance class every vertex has degree at most 3.

FILTER 2 (K_{2,3}).  For distinct points p, q, the circles of radius d about them are
distinct and of equal radius, so they meet in AT MOST TWO points.  Therefore no three
points can all be at distance d from both p and q: **each distance-class graph is
K_{2,3}-free.**  This needs no general-position hypothesis at all; it is just "two
distinct circles meet twice".

Filter 2 subsumes the K_{3,3} argument used on the n=6 candidate.

Usage:  python prune.py            (measures how much each filter removes)
"""
import sys, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def class_graphs(pat, n):
    P = list(itertools.combinations(range(n), 2))
    g = {}
    for i, pr in enumerate(P):
        g.setdefault(pat[i], []).append(pr)
    return g


def deg_ok(pat, n):
    """no vertex has 4 points at one distance (no four cocircular)"""
    for c, edges in class_graphs(pat, n).items():
        d = {}
        for a, b in edges:
            d[a] = d.get(a, 0) + 1
            d[b] = d.get(b, 0) + 1
            if d[a] > 3 or d[b] > 3:
                return False
    return True


def k23_ok(pat, n):
    """no distance class contains K_{2,3}: two circles of equal radius meet at most twice"""
    for c, edges in class_graphs(pat, n).items():
        adj = {v: set() for v in range(n)}
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)
        for p, q in itertools.combinations(range(n), 2):
            if len(adj[p] & adj[q]) >= 3:
                return False
    return True


def ok(pat, n):
    return deg_ok(pat, n) and k23_ok(pat, n)


if __name__ == '__main__':
    from hdecide import enumerate_patterns
    print('=' * 74)
    print('COMBINATORIAL FILTERS: how much do they remove?')
    print('=' * 74)
    print()
    print('  FILTER 1  degree <= 3 in every class   (no four cocircular)')
    print('  FILTER 2  no K_{2,3} in any class      (two equal circles meet twice)')
    print()
    print('   n  k   all patterns   after F1   after F1+F2   extra cut by F2')
    for (n, k) in ((4, 2), (5, 2), (5, 3), (5, 4), (6, 3)):
        allp = list(enumerate_patterns(n, k))
        f1 = [p for p in allp if deg_ok(p, n)]
        f12 = [p for p in f1 if k23_ok(p, n)]
        extra = len(f1) - len(f12)
        print('  %2d %2d   %8d     %8d    %8d      %6d (%.0f%%)'
              % (n, k, len(allp), len(f1), len(f12), extra,
                 100.0 * extra / max(len(f1), 1)))

    # sanity: the known realisable patterns must SURVIVE both filters
    print()
    print('  sanity check -- known realisable patterns must survive:')
    KNOWN = [((0, 0, 0, 0, 1, 1), 4, 'the n=4 diamond'),
             ((0, 0, 0, 1, 0, 1, 1, 1, 2, 1), 5, 'the n=5 witness')]
    bad = 0
    for pat, n, why in KNOWN:
        good = ok(pat, n)
        bad += (not good)
        print('     [%s] %s' % ('PASS' if good else 'FAIL', why))
    # and a pattern we PROVED impossible by the K_{3,3} argument must be cut
    B = (0, 0, 0, 1, 1, 1, 2, 0, 0, 2, 0, 0, 0, 0, 1)
    cut = not k23_ok(B, 6)
    bad += (not cut)
    print('     [%s] the K_{3,3} n=6 candidate is removed by filter 2'
          % ('PASS' if cut else 'FAIL'))
    print()
    print('FILTER CHECKS FAILED' if bad else 'FILTER CHECKS PASSED')
    sys.exit(1 if bad else 0)
