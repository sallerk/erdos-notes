"""Enumerate RADIUS PATTERNS for Erdos #831: partitions of the C(n,3) triples into
classes of equal circumradius, canonical under the S_n action on points.

Two necessary conditions are imposed.  Neither is new; both are quoted with their
source.  Lemma numbering follows NOTE.md throughout this file.

LEMMA 1 (NOTE.md numbering).  NOT new: this is the standard unit-circle double count
  already stated on the #104 page ("every pair of points determines at most 2 unit
  circles"), with the n(n-1)/3 refinement credited there to Harborth and Mengersen.
  It is written out because the enumerator needs the per-class form.
  In an admissible set, no pair of points lies in three triples of the same radius
  class.  Proof: let {a,b} lie in triples abc1, abc2, abc3 all of circumradius r.
  Exactly two circles of radius r pass through a and b, so two of c1,c2,c3 lie on the
  same one; those two together with a and b are four concyclic points.  []
  Hence every pair has degree <= 2 in every class, so a class of size m satisfies
  3m <= 2*C(n,2), i.e. m <= n(n-1)/3.

CONDITION 2 (quoted, not proved here).  A class of size m is m circles of one radius
each through exactly three points, so after rescaling m <= f(n), the maximum number of
unit circles through three of n points: OEIS A003829, f(3..8) = 1, 4, 4, 8, 12, 16
(Harborth-Mengersen 1986; f(8) Harborth 1985).  Patterns are tagged with whether they
also satisfy this, so a result can be reported with or without it.

Usage: python penum.py <n> <number of classes>
"""
import sys, json, os
from itertools import combinations, permutations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

F104 = {3: 1, 4: 4, 5: 4, 6: 8, 7: 12, 8: 16}      # OEIS A003829, offset 3


def canonical(labels, triples, tri_index, n):
    """canonical form of a colouring under S_n on points and renaming of colours"""
    best = None
    for perm in permutations(range(n)):
        relabel = {}
        out = []
        for t in triples:
            img = tuple(sorted(perm[v] for v in t))
            out.append(labels[tri_index[img]])
        # restricted growth: rename colours by first appearance
        m = {}
        rg = []
        for c in out:
            if c not in m:
                m[c] = len(m)
            rg.append(m[c])
        rg = tuple(rg)
        if best is None or rg < best:
            best = rg
    return best


def pair_ok(labels, triples, n, k):
    """LEMMA 1: no pair in three triples of one class"""
    deg = {}
    for t, c in zip(triples, labels):
        for p in combinations(t, 2):
            key = (p, c)
            deg[key] = deg.get(key, 0) + 1
            if deg[key] > 2:
                return False
    return True


def quad_ok(labels, triples, tri_index, n, k):
    """LEMMA 4 (NOTE.md numbering; proved there): if three of the four triples on a 4-set have the
    same circumradius then the 4-set is orthocentric and the fourth triple has that
    radius too.  So no class contains EXACTLY three of the four triples of a 4-set.

    LEMMA 3 (NOTE.md numbering): if a class contains all four triples of a 4-set Q then every pair of Q
    already uses both circles of that radius through it, so no further triple sharing
    two points with Q can lie in that class."""
    for q in combinations(range(n), 4):
        sub = [tri_index[t] for t in combinations(q, 3)]
        cnt = {}
        for i in sub:
            cnt[labels[i]] = cnt.get(labels[i], 0) + 1
        for c, m in cnt.items():
            if m == 3:
                return False
            if m == 4:
                for i, t in enumerate(triples):
                    if labels[i] == c and i not in sub:
                        if len(set(t) & set(q)) >= 2:
                            return False
    return True


def enumerate_patterns(n, k):
    triples = list(combinations(range(n), 3))
    tri_index = {t: i for i, t in enumerate(triples)}
    T = len(triples)
    cap = n * (n - 1) // 3                  # Lemma 1 size cap
    seen = set()
    out = []
    labels = [0] * T
    counts = [0] * k

    def rec(i, used):
        if i == T:
            if used != k:
                return
            if not pair_ok(labels, triples, n, k):
                return
            if not quad_ok(labels, triples, tri_index, n, k):
                return
            cf = canonical(list(labels), triples, tri_index, n)
            if cf in seen:
                return
            seen.add(cf)
            sizes = sorted(counts[:used], reverse=True)
            out.append(dict(labels=list(labels), sizes=sizes,
                            f104_ok=all(s <= F104.get(n, 10**9) for s in sizes)))
            return
        # restricted growth: colour i may be any used colour or the next new one
        for c in range(min(used + 1, k)):
            if counts[c] + 1 > cap:
                continue
            # cheap partial pair check
            ok = True
            for p in combinations(triples[i], 2):
                d = 0
                for j in range(i):
                    if labels[j] == c and p[0] in triples[j] and p[1] in triples[j]:
                        d += 1
                if d >= 2:
                    ok = False
                    break
            if not ok:
                continue
            labels[i] = c
            counts[c] += 1
            rec(i + 1, used + (1 if c == used else 0))
            counts[c] -= 1
        labels[i] = 0
    rec(0, 0)
    return out


if __name__ == '__main__':
    n = int(sys.argv[1]); k = int(sys.argv[2])
    pats = enumerate_patterns(n, k)
    os.makedirs('results', exist_ok=True)
    fn = 'results/penum_n%d_k%d.json' % (n, k)
    json.dump(dict(n=n, k=k, count=len(pats), patterns=pats), open(fn, 'w'))
    from collections import Counter
    print('n=%d k=%d : %d canonical patterns' % (n, k, len(pats)))
    print('  by size profile:', Counter(tuple(p['sizes']) for p in pats).most_common())
    print('  satisfying also f(n)=%s: %d' % (F104.get(n), sum(1 for p in pats if p['f104_ok'])))
    print('  (filters: Lemma 1 pair-degree<=2, Lemma 5 no exactly-3-of-a-4-set,')
    print('            Lemma 3 a saturated 4-set admits no further triple in its class)')
    print('  ->', fn)
