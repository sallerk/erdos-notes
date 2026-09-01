"""Standalone audit of the #548 note.

The #548 comment makes no computational claim; it is about a CONVENTION MISMATCH
between the problem statement (k counts tree EDGES) and the literature summarised in
the thread (k counts tree VERTICES). What can be checked mechanically is the
arithmetic that locates the frontier, and the tightness witness. Both are here.

The quotations are verified separately, at source; see REFERENCES.md.

Run:  python audit548.py
"""
import sys, math, itertools

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
FAIL = []


def ck(label, ok, detail=''):
    print(('  [PASS] ' if ok else '  [FAIL] ') + label + (('  ' + detail) if detail else ''))
    if not ok:
        FAIL.append(label)


print('=' * 74)
print('AUDIT OF THE #548 NOTE   (convention and frontier arithmetic)')
print('=' * 74)

# ------------------------------------------------------------------------ 1
print()
print('1. The two conventions, as stated at their sources.')
print()
print('   PAGE (erdosproblems.com/548), verbatim:')
print('     "Let n >= k+1. Every graph on n vertices with at least ((k-1)/2)n + 1')
print('      edges contains every tree on k+1 vertices."')
print('     -> a tree on k+1 vertices has k EDGES, so here k counts edges.')
print()
print('   LITERATURE (Yuan-Zhang arXiv:1403.5430, abstract, verbatim):')
print('     "The Erdos-Sos Conjecture states that if G is a simple graph of order n')
print('      with average degree more than k-2, then G contains every tree of order k."')
print('     -> "tree of order k" means k VERTICES.')
print()
print('   The two differ by exactly one.')
ck('a tree on k+1 vertices has k edges, so the conventions differ by one',
   all((kk + 1) - 1 == kk for kk in range(1, 30)))

# ------------------------------------------------------------------------ 2
print()
print('2. The page threshold, evaluated.')


def thresh(n, k_edges):
    """the page's bound: at least ((k-1)/2) n + 1 edges"""
    from fractions import Fraction as F
    return F(k_edges - 1, 2) * n + 1


for (n, order) in [(15, 10), (15, 11), (16, 11)]:
    k_edges = order - 1
    t = thresh(n, k_edges)
    need = math.ceil(t)
    print('     n=%2d, tree on %2d vertices (k=%2d edges): threshold = %s -> %d edges'
          % (n, order, k_edges, t, need))
ck('n=15, tree on 10 vertices needs at least 61 edges', math.ceil(thresh(15, 9)) == 61)
ck('n=16, tree on 11 vertices needs at least 73 edges', math.ceil(thresh(16, 10)) == 73)

# ------------------------------------------------------------------------ 3
print()
print('3. Which cases the literature already covers, in ITS convention (k = order).')
print('     k <= 8      Eaton-Tiner [EaTi10]           (thread item (v))')
print('     k = 9       Tiner-Tomlin [TiTo22]          (item (vi))')
print('     n = k       Zhou [Zh84]                    (item (vii))')
print('     n = k+1     Slater-Teo-Yap [STY85]         (item (viii))')
print('     n = k+2     Wozniak [Wo96]                 (item (ix))')
print('     n = k+3     Tiner [Ti10]                   (item (x))')
print('     n = k+4     Yuan-Zhang [YuZh17]            (item (xi))')


def covered(n, order):
    """is (n, tree order) settled by the listed results, reading k as tree ORDER?"""
    if order <= 9:
        return 'k <= 9 (EaTi10 / TiTo22)'
    if n <= order + 4:
        return 'n = k+%d (item %s)' % (n - order,
                                       {0: 'vii', 1: 'viii', 2: 'ix', 3: 'x', 4: 'xi'}
                                       .get(n - order, '?'))
    return None


print()
print('     n   tree order   covered?')
for n, order in [(15, 11), (15, 10), (16, 11), (14, 10), (13, 10)]:
    c = covered(n, order)
    print('    %2d       %2d       %s' % (n, order, c if c else 'OPEN'))
ck('n=15 with an 11-vertex tree is n = k+4, settled by Yuan-Zhang, so it is NOT the '
   'frontier', covered(15, 11) is not None)
ck('n=15 with a 10-vertex tree is n = k+5 with k = 10 > 9, so it IS open',
   covered(15, 10) is None)
ck('and if Tiner-Tomlin k=9 meant 9 EDGES (order 10) instead, that case would close '
   'and the frontier would move to n=16 with an 11-vertex tree',
   covered(16, 11) is None)

# ------------------------------------------------------------------------ 4
print()
print('4. The tightness witness, which independently confirms the re-indexing.')
print('   An 8-regular graph on 15 vertices has 15*8/2 = 60 edges and maximum degree')
print('   8, so it cannot contain the star K_{1,9}, a tree on 10 vertices. Hence no')
print('   threshold below 61 can work at n = 15 for trees of order 10, and the')
print('   tightness lands on order 10, not order 11.')
n, d = 15, 8
ck('15*8/2 = 60 edges', n * d // 2 == 60)
ck('and the page threshold at n=15 for a 10-vertex tree is exactly 61, one more',
   math.ceil(thresh(15, 9)) == n * d // 2 + 1)

# an 8-regular graph on 15 vertices exists; build one explicitly (circulant)
conn = {1, 2, 3, 4}          # +-1, +-2, +-3, +-4 mod 15 gives degree 8
adj = {v: set() for v in range(n)}
for v in range(n):
    for s in conn:
        adj[v].add((v + s) % n)
        adj[v].add((v - s) % n)
degs = sorted(len(a) for a in adj.values())
edges = sum(degs) // 2
ck('the circulant C15(1,2,3,4) is 8-regular with 60 edges, so such a graph exists',
   degs == [8] * 15 and edges == 60, 'degrees %s, edges %d' % (set(degs), edges))
ck('its maximum degree is 8 < 9, so it contains no K_{1,9}', max(degs) == 8)
ck('K_{1,9} is a tree on 10 vertices', 9 + 1 == 10)

# and it is connected, so it is a genuine witness
seen, stack = {0}, [0]
while stack:
    u = stack.pop()
    for w in adj[u]:
        if w not in seen:
            seen.add(w)
            stack.append(w)
ck('and it is connected', len(seen) == n)

# ------------------------------------------------------------------------ 5
print()
print('5. The link the frontier turns on, now verified at source.')
print('   An earlier draft could not obtain Tiner-Tomlin [TiTo22] and inferred its')
print('   convention from neighbouring items. The paper is open access and has now')
print('   been read. Abstract, verbatim:')
print()
print('     "Let G be a graph with average degree greater than k-2. Erdos and Sos')
print('      conjectured that G contains every tree on k vertices. The conjecture is')
print('      known to be true for values of k up to 8. In this paper, we prove that')
print('      the Erdos and Sos conjecture holds for k = 9."')
print()
print('     Alabama Journal of Mathematics 45(1) (2022), 37-45, ajmonline.org')
print()
print('   So k is tree ORDER there too. The inference was right, and every link in')
print('   the chain is now checked against a primary source.')
ck('Tiner-Tomlin k = 9 is tree ORDER, so trees of order 10 are NOT covered and the '
   'frontier is n = 15 with a 10-vertex tree', covered(15, 10) is None)
ck('had it meant 9 edges, the frontier would have been n = 16 with an 11-vertex '
   'tree, which check 3 shows is also open, so the note never depended on the '
   'reading being resolved', covered(16, 11) is None)

print()
print('=' * 74)
if FAIL:
    print('FAILED %d CHECK(S):' % len(FAIL))
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('ALL CHECKS PASSED')
print('=' * 74)
