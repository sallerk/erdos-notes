"""ROUND-2 PROBE: structural bookkeeping claims in NOTE.md section 5."""
# 2026-09-16: absolute paths replaced by paths relative to this file; nothing else changed.
import sys, os, json
from fractions import Fraction as F
from itertools import combinations, permutations

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the p831 directory
tri = list(combinations(range(5), 3)); ti = {t: i for i, t in enumerate(tri)}


def pdeg(lab):
    d = {}
    for t, c in zip(tri, lab):
        for p in combinations(t, 2):
            d[(p, c)] = d.get((p, c), 0) + 1
            if d[(p, c)] > 2: return False
    return True


def l4only(lab):           # Lemma 4: no class holds exactly 3 of a 4-set
    for q in combinations(range(5), 4):
        sub = [ti[t] for t in combinations(q, 3)]
        cnt = {}
        for i in sub: cnt[lab[i]] = cnt.get(lab[i], 0) + 1
        if 3 in cnt.values(): return False
    return True


def l3only(lab):           # Lemma 3: a saturated 4-set admits no further triple
    for q in combinations(range(5), 4):
        sub = [ti[t] for t in combinations(q, 3)]
        cnt = {}
        for i in sub: cnt[lab[i]] = cnt.get(lab[i], 0) + 1
        for c, m in cnt.items():
            if m == 4:
                for i, t in enumerate(tri):
                    if lab[i] == c and i not in sub and len(set(t) & set(q)) >= 2: return False
    return True


def canon(lab):
    best = None
    for perm in permutations(range(5)):
        out = [lab[ti[tuple(sorted(perm[v] for v in t))]] for t in tri]
        m = {}; rg = []
        for c in out:
            if c not in m: m[c] = len(m)
            rg.append(m[c])
        rg = tuple(rg)
        if best is None or rg < best: best = rg
    return best


def enum(k, filts):
    seen = set()
    def rec(i, lab, used):
        if i == 10:
            if used != k: return
            for f in filts:
                if not f(lab): return
            seen.add(canon(lab)); return
        for c in range(min(used + 1, k)):
            rec(i + 1, lab + [c], used + (1 if c == used else 0))
    rec(0, [], 0)
    return seen


print('1. WHICH lemma cuts 35 -> 15?  NOTE.md credits Lemma 4 alone.')
print('   Lemma 1 only                  : %d' % len(enum(3, [pdeg])))
print('   Lemma 1 + Lemma 4 (3-of-4)    : %d' % len(enum(3, [pdeg, l4only])))
print('   Lemma 1 + Lemma 3 (saturated) : %d' % len(enum(3, [pdeg, l3only])))
print('   Lemma 1 + Lemma 3 + Lemma 4   : %d   <- what penum.py actually imposes'
      % len(enum(3, [pdeg, l3only, l4only])))

print()
print('2. SHAPES of a size-4 class after Lemmas 1+4, and how many of the 12 f(5)-legal')
print('   patterns each shape accounts for.')
shapes = {}
for cls in combinations(tri, 4):
    d = {}; ok = True
    for t in cls:
        for p in combinations(t, 2):
            d[p] = d.get(p, 0) + 1
            if d[p] > 2: ok = False
    if not ok: continue
    if any(sum(1 for t in cls if set(t) <= set(q)) == 3 for q in combinations(range(5), 4)):
        continue
    best = None
    for perm in permutations(range(5)):
        img = tuple(sorted(tuple(sorted(perm[v] for v in t)) for t in cls))
        if best is None or img < best: best = img
    common = set(range(5))
    for t in best: common &= set(t)
    shapes[best] = (len(common), len(set(v for t in best for v in t)))
print('   %d shapes:' % len(shapes))
names = {}
for s, (c, sup) in sorted(shapes.items(), key=lambda kv: -kv[1][0]):
    nm = ('COMMON POINT (4-cycle)' if c else ('ALL ON A 4-SET' if sup == 4 else 'NO COMMON POINT'))
    names[s] = nm
    print('      %-46s support=%d common=%s  %s' % (str(list(s)), sup, bool(c), nm))

pats = enum(3, [pdeg, l3only, l4only])
cnt = {}
for lab in pats:
    sz = sorted((sum(1 for x in lab if x == c) for c in set(lab)), reverse=True)
    if sz[0] > 4: continue
    # the size-4 class
    big = [c for c in set(lab) if sum(1 for x in lab if x == c) == 4]
    tag = set()
    for c in big:
        cls = tuple(sorted(tri[i] for i in range(10) if lab[i] == c))
        best = None
        for perm in permutations(range(5)):
            img = tuple(sorted(tuple(sorted(perm[v] for v in t)) for t in cls))
            if best is None or img < best: best = img
        tag.add(names.get(best, '???'))
    key = tuple(sorted(tag))
    cnt[key] = cnt.get(key, 0) + 1
print()
print('   of the 12 patterns with all classes <= f(5)=4, by the shape(s) of the size-4 class:')
for k, v in sorted(cnt.items()):
    print('      %-70s %d' % (str(k), v))
struct = sum(v for k, v in cnt.items() if all(x != 'NO COMMON POINT' for x in k))
print('   patterns whose EVERY size-4 class has a structural treatment : %d' % struct)
print('   patterns with at least one NO-COMMON-POINT size-4 class      : %d' % (12 - struct))
print('   NOTE.md says "five have a structural treatment ... seven rest on the screen alone"')

print()
print('3. support of the n=5 witness size-4 class')
W5 = [(0, 0), (0, 7), (2, 6), (4, 3), (6, 9)]
def d2(P, Q): return (P[0]-Q[0])**2 + (P[1]-Q[1])**2
def r2(P, Q, R):
    a2, b2, c2 = d2(Q, R), d2(R, P), d2(P, Q)
    S = 2*(a2*b2+b2*c2+c2*a2)-(a2*a2+b2*b2+c2*c2)
    return F(a2*b2*c2, S)
cl = {}
for t in tri: cl.setdefault(r2(W5[t[0]], W5[t[1]], W5[t[2]]), []).append(t)
for v, ts in sorted(cl.items(), key=lambda kv: -len(kv[1])):
    sup = sorted(set(i for t in ts for i in t))
    print('   size %d  triples %s  support %s' % (len(ts), ts, sup))
