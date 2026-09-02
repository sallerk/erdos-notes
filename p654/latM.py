"""Lattice hunt for configurations with a small PINNED maximum, for Erdos #654.

    M(X) = max_i d_X(x_i),   d_X(x) = number of DISTINCT distances from x to the rest.
    f(n) = min over admissible X of M(X).

This is latmin2.py's search with the objective swapped.  Two changes matter.

THE PRUNE IS STILL VALID, AND STRONGER.  Adding a point to a partial configuration can
only ADD distances at each existing point, never remove one, so every pinned count is
monotone non-decreasing along the DFS and hence M(partial) <= M(full).  Abandoning a
branch once M(partial) >= target therefore loses nothing.  (For the total-distance
objective latmin2.py used exactly the same reasoning about |dists|.)

TWO HYPOTHESES, AND A TRAP BETWEEN THEM.
    mode 'g'  : general position, no 3 collinear AND no 4 concyclic  (Sheffer's D-hat_gen)
    mode 'n4' : no 4 concyclic only, collinear points ALLOWED       (the #654 page's f(n))
The 4x4 determinant |x^2+y^2, x, y, 1| vanishes when four points are concyclic OR when
they are collinear.  Under 'g' that conflation is harmless because collinear triples are
banned anyway; under 'n4' it is NOT, and rejecting collinear quadruples would silently
exclude exactly the configurations Aletheia's construction is made of (all points on two
lines).  So in mode 'n4' a vanishing determinant is a violation only if the four points
are not collinear.

The N4 hypothesis already caps each point's own circles: four points equidistant from x
lie on a circle centred at x, and four points on a genuine circle are never collinear, so
the concyclicity test catches that case in both modes.

CAVEAT, carried from #98 assumption A12.  Every squared distance in Z^2 and A_2 is an
integer, so these searches cannot see configurations with irrational distance ratios.  A
negative here is "no witness in this lattice inside this radius", never nonexistence.

Usage:  python latM.py <n> <R2> <z2|a2> <g|n4> <target> [shard] [nshards]
        python latM.py controls
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from common import Lat, collinear, cocircular           # noqa: E402


def concyclic(L, pts):
    """four points on a genuine circle: determinant vanishes AND not all collinear"""
    if not cocircular(L, pts):
        return False
    return not (collinear(L, pts[0], pts[1], pts[2])
                and collinear(L, pts[0], pts[1], pts[3]))


def search(n, R2, kind, mode, target, shard=0, nsh=1, quiet=False, ckpt=None):
    """ckpt: path to dump progress after every completed first-point branch.

    Lesson L72: a job that writes only at the end loses everything when it is killed.  The
    DFS has no useful mid-branch state, but the first-point loop is a natural checkpoint:
    after each first is exhausted, the shard's verdict for that first is final."""
    L = Lat(kind)
    pool = [(a, b) for a in range(-R2, R2 + 1) for b in range(-R2, R2 + 1)
            if L.norm(a, b) <= R2]
    pool.sort(key=lambda p: (L.norm(*p), p))
    rank = {p: i for i, p in enumerate(pool)}
    rest = [p for p in pool if p != (0, 0)]

    orbmin = [p for p in rest
              if all(rank.get(L.act(M, p), 10 ** 9) >= rank[p] for M in L.G)]
    firsts = [p for i, p in enumerate(orbmin) if i % nsh == shard]
    if not quiet:
        print('  pool %d, orbit-minimal firsts %d of %d, this shard %d'
              % (len(pool), len(orbmin), len(rest), len(firsts)))

    best = [target, None]
    nodes = [0]

    def rec(chosen, pin, start):
        """chosen: list of lattice points; pin[i]: set of squared distances seen by
        chosen[i].  Invariant: max(len(s) for s in pin) < best[0]."""
        nodes[0] += 1
        if len(chosen) == n:
            M = max(len(s) for s in pin)
            if M < best[0]:
                best[0] = M
                best[1] = list(chosen)
                if not quiet:
                    print('   HIT: M=%d  %s' % (M, chosen))
            return
        need = n - len(chosen)
        for idx in range(start, len(rest) - need + 1):
            p = rest[idx]
            if mode == 'g':
                bad = False
                for i, j in itertools.combinations(range(len(chosen)), 2):
                    if collinear(L, chosen[i], chosen[j], p):
                        bad = True
                        break
                if bad:
                    continue
            bad = False
            for tri in itertools.combinations(range(len(chosen)), 3):
                if concyclic(L, [chosen[t] for t in tri] + [p]):
                    bad = True
                    break
            if bad:
                continue
            # incremental pinned counts
            npin = [set(s) for s in pin] + [set()]
            for i, c in enumerate(chosen):
                d = L.norm(p[0] - c[0], p[1] - c[1])
                npin[i].add(d)
                npin[-1].add(d)
            if max(len(s) for s in npin) >= best[0]:
                continue
            chosen.append(p)
            rec(chosen, npin, idx + 1)
            chosen.pop()

    t0 = time.time()
    for fi, p in enumerate(firsts):
        d = L.norm(p[0], p[1])
        if 1 >= best[0]:
            break
        rec([(0, 0), p], [{d}, {d}], rank[p])
        if ckpt:
            json.dump({'n': n, 'R2': R2, 'lattice': kind, 'mode': mode,
                       'target': target, 'shard': shard, 'nshards': nsh,
                       'firsts_total': len(firsts), 'firsts_done': fi + 1,
                       'best_M': (best[0] if best[1] else None), 'points': best[1],
                       'nodes': nodes[0], 'seconds': round(time.time() - t0, 1),
                       'completed': fi + 1 == len(firsts)},
                      open(ckpt, 'w'), indent=1)
    return best[0], best[1], nodes[0], time.time() - t0


if __name__ == '__main__':
    if sys.argv[1] == 'controls':
        print('=' * 74)
        print('CONTROLS -- must reproduce pinned maxima we have already verified exactly')
        print('=' * 74)
        bad = 0
        # (n, R2, mode, target, expected best M)  from p654/phase0_pinned.json
        for n, R2, mode, tgt, want in ((4, 13, 'g', 3, 2), (6, 49, 'g', 5, 3),
                                       (7, 49, 'g', 5, 3), (4, 13, 'n4', 3, 2)):
            b, s, nd, dt = search(n, R2, kind='a2', mode=mode, target=tgt, quiet=True)
            ok = (s is not None and b <= want)
            bad += (not ok)
            print('  [%s] n=%d %-3s target M<%d: best %s (expected <= %d)  %.1fs'
                  % ('PASS' if ok else 'FAIL', n, mode, tgt,
                     b if s else 'none', want, dt))
        print()
        print('CONTROLS FAILED' if bad else 'CONTROLS PASSED')
        sys.exit(1 if bad else 0)

    n, R2 = int(sys.argv[1]), int(sys.argv[2])
    kind, mode = sys.argv[3], sys.argv[4]
    target = int(sys.argv[5])
    shard = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    nsh = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    assert mode in ('g', 'n4'), 'mode must be g or n4'
    print('n=%d R2=%d %s mode=%s target M<%d shard %d/%d'
          % (n, R2, kind, mode, target, shard, nsh))
    fn = 'latM_n%d_%s_%s_R%d_t%d_s%d.json' % (n, kind, mode, R2, target, shard)
    b, s, nd, dt = search(n, R2, kind, mode, target, shard, nsh, ckpt=fn)
    out = {'n': n, 'R2': R2, 'lattice': kind, 'mode': mode, 'target': target,
           'shard': shard, 'nshards': nsh, 'best_M': (b if s else None), 'points': s,
           'nodes': nd, 'seconds': round(dt, 1), 'completed': True}
    json.dump(out, open(fn, 'w'), indent=1)
    print('  shard COMPLETE: best M %s, nodes %d, %.1fs'
          % ((b if s else 'none found'), nd, dt))
    print('  written: %s' % fn)
