"""Where the first possible counterexample can live.

A counterexample with n points needs at most floor(n/2)-1 distinct distances,
so it needs  n <= g(floor(n/2)-1)  where g is the max size of a planar
k-distance set.  Published: g(1..6) = 3, 5, 7, 9, 12, 13.
"""
from search import build_pool, prepare, run
from geo import distance_set, collinear_triples, D2

G = {1: 3, 2: 5, 3: 7, 4: 9, 5: 12, 6: 13}     # published, exact
print("n    k=floor(n/2)-1   g(k)        possible?")
for n in range(4, 20):
    k = n // 2 - 1
    if k in G:
        ok = n <= G[k]
        note = f"{G[k]:<11}" + ("possible -> must be a MAXIMUM k-distance set"
                                if ok else "IMPOSSIBLE (too many points)")
    else:
        note = f"{'unknown':<11}unknown"
    print(f"{n:<5}{k:<16}{note}")

print("""
So every n <= 15 is settled by the published values of g:
  n = 12 is the only n <= 15 that survives the counting test, and it needs
  EXACTLY a 12-point 5-distance set.  Erdos-Fishburn proved g(5)=12 and
  Shinohara proved that the 12-point 5-distance set is unique up to
  similarity -- Phase 1 shows that set has 18 collinear triples.
  Hence the smallest conceivable counterexample has n = 16, and it must be a
  MAXIMUM 7-distance set (so g(7) >= 16 is a prerequisite).
""")

# ------------------------------------------------------------------
print("The 16-point 7-distance triangular-lattice set (a candidate g(7)=16 "
      "extremal set):")
pts = build_pool(108, 'A2')
tab = prepare(pts, 108, 'A2')
b, bs, _, _ = run(tab, 7)
S = [pts[i] for i in bs]
print(f"  {b} points, Eisenstein coords: {sorted(S)}")
print(f"  squared distances: {sorted(distance_set(S,'A2'))}")
tri = collinear_triples(S)
print(f"  collinear triples: {len(tri)}   -> {'NO 3 COLLINEAR!!' if not tri else 'not in general position'}")

# ------------------------------------------------------------------
print("""
A structural remark that kills a whole natural family
-----------------------------------------------------
If all n points lie on ONE circle, the conjecture is true, and even the
stronger (already-refuted) per-point version is true.  Proof: fix a point p of
the set.  For q on the circle, |pq| determines q up to reflection in the
diameter through p, so the map q -> |pq| is at most 2-to-1 on the other n-1
points.  Hence p alone sees at least ceil((n-1)/2) = floor(n/2) distinct
distances.  So no subset of a regular polygon, and no concyclic set at all,
can ever be a counterexample -- which is why Harborth's 8-point set and
eigensolver's 42-point set both use TWO concentric circles.
""")
for n in (7, 8, 11, 12, 16, 17):
    print(f"   n={n}: a concyclic set forces >= ceil(({n}-1)/2) = "
          f"{-(-(n-1)//2)} distances from a single point; floor(n/2) = {n//2}")
