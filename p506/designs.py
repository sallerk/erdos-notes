"""Combinatorial lower bound for Erdos #506 by exact cover.

Any admissible point set induces a block structure: for each line or circle
carrying >= 3 of the points, the set of points on it is a BLOCK.  Every triple of
points lies on exactly one block (three points are either collinear -- a line --
or determine a unique circle).  So the blocks EXACTLY COVER the C(n,3) triples.

Two useful facts drop out:
  * "two blocks meet in at most 2 points" needs no separate constraint: if two
    blocks shared three points that triple would be covered twice, so exact cover
    already forbids it.
  * lines are free (a collinear triple determines no circle), so the count to
    minimise is  #blocks - #blocks designated as lines.
    Lines carry one extra restriction that circles do not: two distinct lines
    meet in at most ONE point.  Circles may meet in two.

Therefore:  m(n) >= min over exact covers of [ #blocks - (max sub-family of
blocks that pairwise meet in <= 1 point) ],  and the minimum is attained only if
the winning design is realisable by actual points and circles in the plane.
This module computes the combinatorial bound; realisability is a separate
question and is NOT decided here.

Excluded: the all-points block (the problem forbids all collinear and all
concyclic).
"""
import sys, json, time
from itertools import combinations


def solve(n, verbose=True, cap=None):
    pts = list(range(n))
    triples = list(combinations(pts, 3))
    tidx = {t: i for i, t in enumerate(triples)}
    T = len(triples)

    # candidate blocks: every subset of size >= 3 except the whole set
    blocks = []
    for size in range(3, n):
        for S in combinations(pts, size):
            mask = 0
            for t in combinations(S, 3):
                mask |= 1 << tidx[t]
            blocks.append((S, mask))
    if verbose:
        print('n=%d: %d triples, %d candidate blocks' % (n, T, len(blocks)), flush=True)

    # blocks containing each triple, largest first (big blocks cover more, so they
    # tend to lead to few blocks and are tried early)
    by_triple = [[] for _ in range(T)]
    for bi, (S, mask) in enumerate(blocks):
        for t in combinations(S, 3):
            by_triple[tidx[t]].append(bi)
    for lst in by_triple:
        lst.sort(key=lambda bi: -len(blocks[bi][0]))

    FULL = (1 << T) - 1
    best = {'circles': cap if cap else 10 ** 9, 'design': None}
    nodes = [0]

    def max_lines(chosen):
        """largest sub-family that pairwise meets in <= 1 point (a valid set of lines)"""
        m = len(chosen)
        sets = [set(blocks[bi][0]) for bi in chosen]
        compat = [[len(sets[i] & sets[j]) <= 1 for j in range(m)] for i in range(m)]
        bestl = [0]

        def rec(i, cur):
            if len(cur) + (m - i) <= bestl[0]:
                return
            if i == m:
                bestl[0] = max(bestl[0], len(cur))
                return
            if all(compat[i][j] for j in cur):
                rec(i + 1, cur + [i])
            rec(i + 1, cur)
        rec(0, [])
        return bestl[0]

    def rec(covered, chosen):
        nodes[0] += 1
        if covered == FULL:
            c = len(chosen) - max_lines(chosen)
            if c < best['circles']:
                best['circles'] = c
                best['design'] = [blocks[bi][0] for bi in chosen]
                if verbose:
                    print('   new best: %d circles, %d blocks %s'
                          % (c, len(chosen), best['design']), flush=True)
            return
        # every block is at best a line, so #circles >= 0; prune on block count only
        # when even making every chosen block a line cannot beat the incumbent
        if len(chosen) - max_lines(chosen) >= best['circles']:
            return
        # first uncovered triple
        i = 0
        while covered >> i & 1:
            i += 1
        for bi in by_triple[i]:
            S, mask = blocks[bi]
            if covered & mask:
                continue
            rec(covered | mask, chosen + [bi])

    t0 = time.time()
    rec(0, [])
    dt = time.time() - t0
    if verbose:
        print('n=%d: combinatorial minimum = %s circles  (%d nodes, %.1fs)'
              % (n, best['circles'], nodes[0], dt), flush=True)
        print('   design:', best['design'], flush=True)
    return best, nodes[0], dt


if __name__ == '__main__':
    n = int(sys.argv[1])
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else None
    best, nodes, dt = solve(n, cap=cap)
    json.dump({'n': n, 'combinatorial_min_circles': best['circles'],
               'design': [list(b) for b in best['design']] if best['design'] else None,
               'nodes': nodes, 'seconds': round(dt, 1), 'cap': cap,
               'note': 'LOWER BOUND ONLY: realisability in the plane is not decided here',
               'status': 'COMPLETED'},
              open('design_n%d.json' % n, 'w'), indent=1)
