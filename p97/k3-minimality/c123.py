"""Three necessary conditions from convex geometry, applied to the k=3 pattern classes.

Source: veljjanoski's constraints C1-C3 for k=4 (erdosproblems.com forum thread 97, post of
14 Sep 2026, and github.com/veljjanoski/erdos97, n7/README.md).  The proofs do not use k, so
they hold for the witness triples T_i of a k=3 pattern (see core.py):

  C1.  |T_i & T_j| <= 2 for i != j.  The circles about v_i and v_j through T_i and T_j have
       different centres, so they are different circles and meet in at most 2 points.
  C2.  No pair {a,b} lies in three of the T_i.  All three centres would lie on the
       perpendicular bisector of ab: three collinear vertices of a strictly convex polygon.
  C3.  If {a,b} is in T_i & T_j, the line v_i v_j is the perpendicular bisector of ab, so a and
       b are mirror images in it and lie strictly on opposite sides of the chord v_i v_j (they
       are not on it: that would make three vertices collinear).  In a strictly convex polygon
       the vertices on one side of a chord are exactly those strictly between its ends in the
       cyclic order, so a and b are separated by i and j in the cyclic order.

Each condition is necessary for any choice of one witness triple per vertex, so a pattern that
fails one has no strictly convex realisation, and dropping it loses nothing.

Two independent implementations are run over every class and must agree class by class:
A uses Python sets; B uses bit masks and a different separation test.  Controls: Danzer's
9-gon pattern (a real k=3 polygon) must pass; hand-made patterns violating exactly one
condition must fail that condition.

Usage: python c123.py 7     writes c123_n7_survivors.npy and c123_n7.json
"""
import json
import sys
import time
from itertools import combinations

import numpy as np

from enum_nb import tables


def triples_of(ch, n, TJ, TK, TL):
    return [(int(TJ[i, ch[i]]), int(TK[i, ch[i]]), int(TL[i, ch[i]])) for i in range(n)]


def check_A(T, n):
    """returns (c1, c2, c3): True where the condition HOLDS"""
    S = [set(t) for t in T]
    c1 = all(len(S[i] & S[j]) <= 2 for i, j in combinations(range(n), 2))
    count = {}
    for t in S:
        for p in combinations(sorted(t), 2):
            count[p] = count.get(p, 0) + 1
    c2 = all(v <= 2 for v in count.values())

    def strictly_between(i, j, x):          # x on the ccw arc from i to j, ends excluded
        return 0 < (x - i) % n < (j - i) % n

    c3 = True
    for i, j in combinations(range(n), 2):
        common = sorted(S[i] & S[j])
        for a, b in combinations(common, 2):
            if strictly_between(i, j, a) == strictly_between(i, j, b):
                c3 = False
    return c1, c2, c3


def check_B(T, n):
    """same conditions, bit masks, separation by counting sides of both arcs"""
    M = [(1 << t[0]) | (1 << t[1]) | (1 << t[2]) for t in T]
    c1 = True
    c2 = True
    c3 = True
    for i in range(n):
        for j in range(i + 1, n):
            both = M[i] & M[j]
            if bin(both).count('1') >= 3:
                c1 = False
            if bin(both).count('1') >= 2:
                arc = 0                          # vertices i+1, ..., j-1 (indices between i and j)
                for x in range(i + 1, j):
                    arc |= 1 << x
                bits = [x for x in range(n) if both >> x & 1]
                for p in range(len(bits)):
                    for q in range(p + 1, len(bits)):
                        pair = (1 << bits[p]) | (1 << bits[q])
                        if bin(pair & arc).count('1') != 1:
                            c3 = False
    for a in range(n):
        for b in range(a + 1, n):
            pair = (1 << a) | (1 << b)
            if sum(1 for m in M if m & pair == pair) >= 3:
                c2 = False
    return c1, c2, c3


def controls():
    """Danzer must pass.  Random patterns at n = 7 and 8: A and B must agree on every one, and
    every condition must be seen failing, so every test can fire.

    C3 as implemented (every pair inside T_i & T_j must be separated) implies C1 and C2:
    three common points cannot be pairwise separated by one chord (two of them share a side),
    and if a pair {a,b} lies in T_i, T_j and T_l, the three chords among v_i, v_j, v_l cannot
    all separate a from b (the chords cut the cycle into three arcs; if a and b lie in
    different arcs, the chord joining the far ends of those two arcs has both on one side, and
    if they lie in the same arc every chord has both on one side).  So C1 or C2 never fails
    alone; the controls check that implication instead of expecting single failures."""
    import os
    out = {}
    d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'danzer_ccw.json')))
    T = [tuple(d['ccw_triples'][str(i)]) for i in range(9)]
    out['danzer'] = [check_A(T, 9), check_B(T, 9)]
    rng = np.random.default_rng(97)
    failing = {'C1': 0, 'C2': 0, 'C3': 0}
    implication_broken = 0
    agree = 0
    for n in (7, 8):
        for _ in range(100000):
            T = [tuple(sorted(rng.choice([x for x in range(n) if x != i], 3, replace=False).tolist()))
                 for i in range(n)]
            a, b = check_A(T, n), check_B(T, n)
            assert a == b, ('control disagreement', n, T, a, b)
            agree += 1
            for name, ok in zip(('C1', 'C2', 'C3'), a):
                failing[name] += not ok
            if (not a[0] or not a[1]) and a[2]:
                implication_broken += 1
    out['random_patterns_agreeing'] = agree
    out['random_patterns_failing'] = failing
    out['C1_or_C2_fails_but_C3_holds'] = implication_broken
    return out


def main():
    n = int(sys.argv[1])
    ctl = controls()
    print('control: Danzer (A, B) =', ctl['danzer'])
    print('control: %d random patterns, A and B agree on all' % ctl['random_patterns_agreeing'])
    print('control: random patterns failing each condition:', ctl['random_patterns_failing'])
    print('control: C1 or C2 failing while C3 holds: %d' % ctl['C1_or_C2_fails_but_C3_holds'])
    assert ctl['danzer'] == [(True, True, True), (True, True, True)], 'Danzer must pass'
    assert all(ctl['random_patterns_failing'].values()), 'every condition must be seen failing'
    assert ctl['C1_or_C2_fails_but_C3_holds'] == 0, 'C3 must imply C1 and C2'

    pid, NP, NT, TJ, TK, TL = tables(n)
    cls = np.load('cls_n%d.npy' % n)
    t0 = time.time()
    keep = []
    fail = {'C1': 0, 'C2': 0, 'C3': 0}
    disagree = 0
    for ci in range(len(cls)):
        T = triples_of(cls[ci], n, TJ, TK, TL)
        a = check_A(T, n)
        b = check_B(T, n)
        if a != b:
            disagree += 1
        for name, ok in zip(('C1', 'C2', 'C3'), a):
            if not ok:
                fail[name] += 1
        if all(a):
            keep.append(ci)
    keep = np.array(keep, dtype=np.int64)
    np.save('c123_n%d_survivors.npy' % n, keep)
    rec = dict(n=n, classes=int(len(cls)), survivors=int(len(keep)),
               failing_each_condition=fail, implementations_disagree=disagree,
               controls=ctl, seconds=round(time.time() - t0, 1),
               note='a class may fail several conditions, so the failure counts overlap')
    json.dump(rec, open('c123_n%d.json' % n, 'w'), indent=1)
    print(json.dumps(rec, indent=1))
    assert disagree == 0, 'the two implementations disagree'


if __name__ == '__main__':
    main()
