# Erdos #100: the smallest diameter of a distance-separated point set

`A` is a planar n-point set with every pairwise distance at least 1 and any two distinct
distances at least 1 apart. Is the diameter `>> n`? Erdos adds, in the same passage of
[Er95], "It is perhaps not uninteresting to try to determine the smallest diameter for
each n, but this will already be difficult for n = 9." That sub-question is what this
directory attacks. Write `delta(n)` for the answer.

## 1. The scale-free form, and the bound it forces

The hypothesis is scale-dependent and the conclusion is not, so normalise. For a set X
with distinct distances `d_1 < ... < d_k`, the smallest legal rescaling is `1/g` with
`g = min(d_1, min_i (d_{i+1} - d_i))`, so the least diameter its SHAPE permits is

        delta(X) = d_k / g,      delta(n) = min over n-point X.

Since `d_k >= d_1 + (k-1) g >= k g`,

        **delta(X) >= k**, the number of distinct distances,

with equality exactly when `d_i = i g`, i.e. the distance set is an arithmetic
progression whose common difference equals its first term.

**This is not new.** It is Kanold's eq. (8), `delta >= d_1 + (s-1) eps`, in print since
Abh. Braunschw. Wiss. Ges. **32** (1981) 55-65, and Erdos's own 1981 formulation already
combined it with Moser's distinct-distance bound to get `delta > C n^{2/3}`. What is done
here is to run it in the other direction, as a per-n floor, and to pair it with the
maximum sizes of k-distance sets.

With `g(1..6) = 3, 5, 7, 9, 12, 13` for the maximum size of a planar k-distance set
(Erdos-Fishburn k <= 4, Shinohara k = 5, Wei k = 6), `k_min(n) = min{k : g(k) >= n}`:

    n         3  4  5  6  7  8  9  10 11 12 13
    delta >=  1  2  2  3  3  4  4  5  5  5  6

**The cap that makes this finite.** Since `delta >= k`, a configuration can only improve
on an incumbent value D if it has `k < D` distinct distances. With Piepmeyer's 4.664 in
hand at n = 9, only 4-distance sets matter there, and 9 is the maximum size of a
4-distance set. The same cap applies at every n.

## 2. Status: the first table of delta(n)

| n | lower | delta(n) | status | witness |
|---|---|---|---|---|
| 3 | 1 | **1** | PROVED | equilateral triangle |
| 4 | 2 | **2.0731321850** = (sqrt6+sqrt2)/(sqrt6+sqrt2-2) | PROVED | a 4-point 2-distance set with ratio 2cos15 |
| 5 | 2 | **2.6180339887** = (3+sqrt5)/2 | PROVED | the regular pentagon |
| 6 | 3 | <= 3.4142135624 = 2+sqrt2 | bracketed | two concentric equilateral triangles |
| 7 | 3 | <= 4.6639024601 | bracketed | any 7 of Piepmeyer's points |
| 8 | 4 | <= 4.6639024601 | bracketed | any 8 of Piepmeyer's points |
| 9 | 4 | <= 4.6639024601 | bracketed | Piepmeyer |

"PROVED" means: an exhaustive enumeration of every k-distance pattern at that n found
the minimum, and `delta >= k` rules out every larger k. At n = 4 all five 2-distance
patterns are realisable, with 64 distinct shapes between them, and the best is
2.0731; a 3-distance set has delta >= 3. At n = 5 exactly ONE of seventeen patterns is
realisable, the regular pentagon, which is Kelly's classification recovered from
scratch; its distances are 1 and phi, so delta = phi/(phi-1) = phi^2.

"bracketed" means an upper bound from a search plus the k_min floor. Proving any of
those needs an exhaustive enumeration at that n, and n = 6 with k = 3 is already
S(15,3) = 2,375,101 partitions before symmetry, beyond what the enumerator here can do.

**Monotonicity.** Any m-subset of an admissible set is admissible with no larger
diameter, so delta is non-decreasing in n, and every subset of a good configuration
bounds a smaller n for free. Piepmeyer's subsets give exactly the table above for
n = 6..9 and, independently, reproduce the n = 4 optimum. This also caught an error:
a first search at n = 7 reported 5.049, which cannot exceed delta(8) <= 4.664, and
the cause was that it had searched only 3-distance sets when 4-distance ones can win.

The values at n = 7, 8, 9 coincide because deleting a point from Piepmeyer's set
leaves all four distance values present. Whether 9 points can do better than
Piepmeyer is the case Erdos called difficult, and it remains open here.

## 3. Piepmeyer's configuration, verified

Erdos gives it verbally in [Er95]: `x = (1+sqrt2) sqrt(2-sqrt3)`, two parallel equilateral
triangles a distance x apart, plus the three circumcentres of the trapezoids formed by
each pair of parallel sides. `piepmeyer.py` rebuilds that sentence, independently builds
the closed-form coordinates that appear in a Lean branch of formal-conjectures, and
checks the two agree as exact 36-element distance multisets. They do, to zero error.

    d_1 = sqrt(6 - 3sqrt3 + 4sqrt2 - 2sqrt6) = 1.24968889777
    d_2 = 1 + sqrt2                          = 2.41421356237
    d_3 = 2 + sqrt2                          = 3.41421356237
    d_4 = sqrt(6 + 3sqrt3 + 4sqrt2 + 2sqrt6) = 4.66390246015

The gaps are 1.1645, **exactly 1**, and 1.2497, so the binding constraint is the middle
gap and `delta = d_4 = 4.6639`. The set is not an arithmetic progression, so it does not
attain the floor of 4, and whether 9 points can do better is open.

## 4. Method, and one instrument that failed first

Minimising delta over raw coordinates with a penalty on the number of distance classes
does not work, and the reason is worth recording: that number is an integer read off by
clustering, so the penalty is a step function with no descent direction toward making two
distances coincide. A generic 4-point set has six distinct distances and the optimiser
never reaches the measure-zero set where it has two; the run reported "no configuration
with k <= 2" at n = 4, where the square alone refutes it.

`patterns.py` puts the combinatorics in the enumeration instead: colour the pairs by
class, canonicalise under S_n, solve the resulting equalities, and read delta off the
exact class values with no tolerance anywhere. It collects EVERY distinct realisation
shape per pattern rather than the first one found, since a pattern's equations can have
several solution shapes with different ratios and delta depends on the ratios.

**Controls.** At n = 5, k = 2 the enumeration realises exactly 1 of 17 patterns, and it is
the regular pentagon: Kelly's classification, reproduced from scratch. For the search that
reaches beyond the enumerator's range, random starts turned out to land a valid
k-distance set well under 1% of the time (about 150 restarts to find the pentagon once),
which is far too low to support any negative. The solver itself was not the problem: seeded
at Piepmeyer's coordinates it holds delta to 3e-16 and recovers it from 30 of 30 starts
perturbed by 0.05. Seeding from structure instead (regular polygons, concentric polygons at
many ratios and offsets, lattice patches, Piepmeyer's own shape, each with noise) raised
the hit rate to 16% at n = 5 and 34% at n = 6, and the seeded search recovers Piepmeyer at
n = 9. That is the control the upper bounds rest on.

## 5. Two page corrections

* The page cites [Er90], [Er92e], [Er95], [Er97f] but not the problem's origin: **Erdos,
  Problem 856A, Elem. Math. 36 (1981) 22**, solved by **Kanold, Elem. Math. 37 (1982) 56**.
* "Kanold proved the diameter is `>= n^{3/4}`" omits two things his 1981 paper states:
  the constant, `delta > 0.366 eps n^{3/4}`, and, more importantly, **Satz 2 already gives
  the LINEAR bound `delta/eps > n/2` whenever the minimum distance is at most eps**. So
  the whole difficulty of #100 lives in the regime where the minimum distance exceeds
  eps, which is exactly Piepmeyer's regime.

## 6. Open here

`delta(n)` for `n >= 6`, and whether Piepmeyer is optimal at n = 9. The latter is a
finite check if the 9-point 4-distance sets are classified in the literature; that is
being looked up.
