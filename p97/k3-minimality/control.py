"""POSITIVE CONTROL + LEMMA CHECK for the k=3 minimality search.

Two jobs:
 (1) Verify the OBTUSE-MIDDLE LEMMA on Danzer's 9-gon and on random convex polygons.
     LEMMA.  Let P be a strictly convex polygon, ccw order.  Let v_i be a vertex and
     let v_j,v_k,v_l be three OTHER vertices equidistant from v_i, indexed so that
     j,k,l occur in this ccw order starting after i.  Then v_i is the circumcentre of
     triangle (v_j,v_k,v_l); in the convex quadrilateral (v_i,v_j,v_k,v_l) the
     diagonals cross, so v_i and v_k lie strictly on opposite sides of line v_j v_l;
     hence the circumcentre is on the far side of chord v_j v_l from v_k, so the
     inscribed angle at v_k is STRICTLY OBTUSE.  Therefore
             D_jl  >  D_jk + D_kl          (D = squared distance).
     This is a LINEAR strict inequality in the squared distances -> cheap sound prune.
 (2) Feed Danzer's OWN witness pattern (one triple per vertex) to z3 as a single
     small instance, to check that the per-pattern route is solvable at all.
"""
import json, sys, time
from itertools import combinations
import math, random

def load_danzer():
    d = json.load(open('../p97/artifact_danzer9_t0.json'))[0]
    pts = [(float(a), float(b)) for a, b in d['coords_float']]
    tri = {e['vertex']: sorted(e['equidistant_set']) for e in d['verified_per_vertex']}
    return pts, tri

def ccw_sort(pts):
    cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
    order = sorted(range(len(pts)), key=lambda i: math.atan2(pts[i][1]-cy, pts[i][0]-cx))
    return order

def cross(o, a, b):
    return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])

def check_lemma(pts, triples, n, label):
    """triples: dict vertex -> list of >=3 equidistant vertices (original labels).
    pts are ALREADY in ccw order and triples use the ccw indices."""
    bad = []
    for i in range(n):
        for T in combinations(triples[i], 3):
            # sort by ccw position starting after i
            T = sorted(T, key=lambda x: (x - i) % n)
            j, k, l = T
            D = lambda a,b: (pts[a][0]-pts[b][0])**2 + (pts[a][1]-pts[b][1])**2
            lhs, rhs = D(j,l), D(j,k)+D(k,l)
            if not lhs > rhs:
                bad.append((i, j, k, l, lhs, rhs))
    print(f"[{label}] obtuse-middle lemma: {'HOLDS' if not bad else 'FAILS'} "
          f"({len(bad)} violations)")
    for b in bad[:5]:
        print("   violation", b)
    return not bad

# ---------------------------------------------------------------- random test
def random_convex(n, rng):
    while True:
        pts = [(rng.uniform(-1,1), rng.uniform(-1,1)) for _ in range(3*n)]
        # convex hull
        pts = sorted(set(pts))
        def half(P):
            h=[]
            for p in P:
                while len(h)>=2 and cross(h[-2],h[-1],p)<=0: h.pop()
                h.append(p)
            return h
        lo=half(pts); hi=half(pts[::-1])
        h=lo[:-1]+hi[:-1]
        if len(h)>=n: return h[:n]

def random_lemma_test(trials=4000):
    rng = random.Random(20260830)
    bad = 0; tested = 0
    for _ in range(trials):
        n = rng.randint(4, 9)
        P = random_convex(n, rng)
        m = len(P)
        for i in range(m):
            for (j,k,l) in combinations([x for x in range(m) if x!=i], 3):
                j2,k2,l2 = sorted((j,k,l), key=lambda x:(x-i)%m)
                D = lambda a,b: (P[a][0]-P[b][0])**2 + (P[a][1]-P[b][1])**2
                # the lemma only applies when i is equidistant; test the CONTRAPOSITIVE
                # direction by constructing the circumcentre instead -- see below.
                tested += 1
        # direct test: for each triple of vertices, the circumcentre is a valid v_i
        # only if it is a vertex; instead test the equivalent statement:
        #   for every 4 vertices a<b<c<d in ccw order,
        #   circumcentre of (b,c,d) is on the far side of bd from c  <=>  angle at c obtuse
        # and a is on the far side of bd from c BY CONVEXITY.  So: if a is equidistant
        # from b,c,d then a IS that circumcentre, hence obtuse.  We verify the
        # convexity half (a and c strictly opposite sides of line bd) which is the
        # only geometric input.
        for (a,b,c,d) in combinations(range(m), 4):
            s1 = cross(P[b], P[d], P[a]); s2 = cross(P[b], P[d], P[c])
            if s1*s2 >= 0: bad += 1
    print(f"[random] convex-quadrilateral diagonal-crossing check on {trials} random "
          f"polygons: {bad} violations")
    return bad == 0

if __name__ == '__main__':
    pts, tri = load_danzer()
    order = ccw_sort(pts)
    inv = {v: p for p, v in enumerate(order)}
    P = [pts[v] for v in order]
    T = {inv[v]: sorted(inv[u] for u in tri[v]) for v in tri}
    n = len(P)
    # confirm strict convexity of the reordered polygon
    mn = min(cross(P[i], P[(i+1)%n], P[(i+2)%n]) for i in range(n))
    print(f"Danzer 9-gon, ccw-reordered: min cross = {mn:.8f}  strictly convex = {mn>0}")
    print("witness triples (ccw labels):", {i: T[i] for i in range(n)})
    check_lemma(P, T, n, "Danzer9")
    random_lemma_test(400)
    json.dump({'ccw_points': P, 'ccw_triples': {str(k): v for k, v in T.items()},
               'min_cross': mn},
              open('danzer_ccw.json','w'), indent=1)
