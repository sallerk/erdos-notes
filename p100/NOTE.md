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
4-distance set. The same cap applies at every n, and it is what turns the small cases
into finite exact computations.

## 2. Status: the table of delta(n)

| n | lower | delta(n) | status | witness |
|---|---|---|---|---|
| 3 | 1 | **1** | PROVED | equilateral triangle |
| 4 | 2 | **2.0731321850** = (sqrt6+sqrt2)/(sqrt6+sqrt2-2) | PROVED | the 2-distance kite with ratio 2cos15 |
| 5 | 2 | **2.6180339887** = (3+sqrt5)/2 | PROVED | the regular pentagon |
| 6 | 3 | **3.4142135624** = 2+sqrt2 | PROVED | the 3-distance set with ratios 1 : (sqrt6+sqrt2)/2 : 1+sqrt3 |
| 7 | 4 | <= 4.6639024601 | bracketed | any 7 of Piepmeyer's points |
| 8 | 4 | <= 4.6639024601 | bracketed | any 8 of Piepmeyer's points |
| 9 | 4 | <= 4.6639024601 | bracketed | Piepmeyer |
| 10 | 5 | <= 8.2908593694 | bracketed | regular nonagon plus centre |
| 11 | 5 | <= 11.1961524227 = 6+3sqrt3 | bracketed | an 11-point 5-distance subset of the triangular lattice |
| 12 | 5 | <= 11.1961524227 = 6+3sqrt3 | bracketed | the unique 12-point 5-distance set (a lattice set) |
| 13 | 6 | <= 12.9282032303 = 6+4sqrt3 | bracketed | the 13-point 6-distance lattice set |

"PROVED" means an exact computation covering every configuration that could beat the
value. "bracketed" means an upper bound from an explicit set plus the floor `k_min`.

**How the proved entries are proved.** At n = 4 and n = 5 every 2-distance pattern
(colouring of the pairs by distance class, up to relabelling) was decided by a Groebner
basis over Q: at n = 4 all five patterns are realisable and their real solutions are
exactly the six classical 4-point 2-distance sets, at n = 5 sixteen of seventeen
patterns are unrealisable and the seventeenth is the regular pentagon. A 3-distance set
has `delta >= 3`, above both values, so nothing else can compete. At n = 6 the value
`2+sqrt2 < 4` means only sets with at most 3 distances can compete; all 5-point sets
with at most 3 distances were decided exactly (124 patterns, 104 unrealisable, every
solution list certified complete), every one was extended by one point in every way
that keeps at most 3 distances (a complete enumeration, section 4), and the nine
6-point 3-distance sets that result were each certified exactly. The smallest delta
among them is `2+sqrt2`. There is no 6-point set with 2 distances, so `g(2) = 5` comes
out of the same computation (and the one 1-distance pattern on 4 points is unrealisable,
so no 5-point set has fewer than 2 distances).

**The lower bound at n = 7** is 4, not 3: the same chain gives exactly two 7-point
3-distance sets, the regular heptagon (delta 5.0489) and the hexagon plus centre
(delta 7.4641), both above 4.664, so a set beating Piepmeyer's 7-subset has exactly
4 distances. The chain also finds no 8-point set with 3 distances, i.e. `g(3) = 7`.

**Monotonicity.** Any m-subset of an admissible set is admissible with no larger
diameter, so delta is non-decreasing in n, and every subset of a good configuration
bounds a smaller n for free. Piepmeyer's subsets give exactly the entries at n = 7, 8, 9.
This caught an error: a first search at n = 7 reported 5.049, which cannot exceed
`delta(8) <= 4.664`, and the cause was that it had searched only 3-distance sets.

The values at n = 7, 8, 9 coincide because deleting a point from Piepmeyer's set leaves
all four distance values present. Whether 9 points can do better than Piepmeyer is the
case Erdos called difficult. It is a finite check once the 9-point 4-distance sets are
listed, and Erdos-Fishburn (1996) list them; that paper was not obtained here (section 6).

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
attain the floor of 4.

**Piepmeyer does not extend.** Every way of adding a tenth point was enumerated
(section 4): the best gives delta 9.903 with 7 distances, worse than the nonagon plus
centre. The same enumeration applied to the regular nonagon recovers the nonagon plus
centre (the control), and applied to the nonagon plus centre finds no eleventh point
with delta <= 12.

## 4. Methods

**Patterns, not penalties.** Minimising delta over coordinates with a penalty on the
number of distance classes does not work: that number is an integer read off by
clustering, so the penalty is a step function with no descent direction, and the run
reported "no 4-point set with 2 distances" where the square refutes it. `patterns.py`
puts the combinatorics in the enumeration instead: colour the pairs by class,
canonicalise under relabelling, solve the equalities numerically. It is a witness
finder, and two of its habits had to be corrected: a configuration with two points
merged is an exact solution of the equations, so the solver converges to it with a
residual that vanishes quadratically (59 such limits were discarded at n = 4; an earlier
version of this note counted them as "64 shapes"; the true count is six), and sorted
class values do not identify a shape (the two kites share 1 : 1.932 with the
multiplicities swapped); the key is now the full distance multiset.

**Exact decision.** `pexact.py` writes each pattern as the polynomial system
`|P_a - P_b|^2 = v_{colour(ab)}` with `P_0 = (0,0)`, `P_1 = (1,0)`, and one saturation
equation `t * prod v_c = 1` that forbids any class value from being zero (every pair's
squared distance is some `v_c`, so this is exactly "all points distinct"). A reduced
Groebner basis equal to [1] is a proof that no configuration exists over C, hence over
R. For a feasible pattern the system is zero-dimensional; its solutions are computed,
and their number is compared with the dimension of the quotient ring (the count of
standard monomials), which certifies the solution list complete. Every feasible pattern
at n = 4, 5 (k = 2) and n = 5 (k = 3) passed that certificate.

**Extension chain.** `ext3.py` builds `E_{n+1}(<= K)` from `E_n(<= K)`: a new point is
pinned by two conditions of the form "old distance to a base point" (a circle) or "same
new distance to two base points" (a bisector), unless it has at most one such condition,
in which case it brings at least n - 1 new distances, too many. So intersecting every
pair of circles and bisectors is a complete enumeration. Candidates are handled at 60
digits and every survivor is certified by deciding its own pattern exactly. Results:
`E_6(<= 3)` has nine sets, all with 3 distances; `E_7(<= 3)` is exactly {regular
heptagon, hexagon plus centre}, which is Erdos-Fishburn's result as quoted by Wei
(2012), reproduced from scratch; `E_8(<= 3)` is empty. The same machinery (`ext2.py`,
any number of new values) gives the one-point extensions of section 3.

**Lattice enumeration.** `lat.py` lists, in integer arithmetic, every n-point k-distance
subset of the triangular lattice up to lattice similarity, with a true diameter bound.
Controls: the 12-point 5-distance set is unique (Shinohara 2008: one class found), the
13-point 6-distance lattice set of Wei's Figure 1 is unique (one class found). At
n = 10, k = 5 it finds fifteen sets up to similarity with diameter at most 10, and an
independent float implementation with a different canonical key also finds fifteen;
Wei's Theorem 11 shows sixteen lattice figures (2a-2p). The discrepancy is unresolved
here (the figures could not be compared point by point); it does not affect any entry
of the table, since every one of the fifteen has delta = 3/(2-sqrt3) = 11.196.

**Controls for the search that reaches beyond the exact range.** `seeded.py` starts from
regular polygons, concentric polygons at many ratios, lattice patches and Piepmeyer's
shape, each with noise. Random starts landed a valid k-distance set well under 1% of the
time; structured starts raised that to 16-34%, and the seeded search recovers Piepmeyer
at n = 9. It found the nonagon plus centre at n = 10 and the regular 11-gon at n = 11;
the lattice witnesses at n = 11, 12, 13 came from `lat.py` and are better.

## 5. Two page corrections

* The page cites [Er90], [Er92e], [Er95], [Er97f] but not the problem's origin: **Erdos,
  Problem 856A, Elem. Math. 36 (1981) 22**, solved by **Kanold, Elem. Math. 37 (1982) 56**.
* "Kanold proved the diameter is `>= n^{3/4}`" omits two things his 1981 paper states:
  the constant, `delta > 0.366 eps n^{3/4}`, and, more importantly, **Satz 2 already gives
  the LINEAR bound `delta/eps > n/2` whenever the minimum distance is at most eps**. So
  the whole difficulty of #100 lives in the regime where the minimum distance exceeds
  eps, which is exactly Piepmeyer's regime.

## 6. What the literature settles, and what is still open here

Wei (EJC 2012, Theorem 11) classifies the 10-point 5-distance sets: nonagon plus centre,
regular decagon, 11-gon minus a vertex, "double R5 with the same centre" (his Figure
2q, which matches the regular pentagon together with its five diagonal intersections;
that set has exactly 5 distances and delta 9.216), and the lattice configurations. Their
deltas are 8.291, 20.432, 12.344, 9.216 and 11.196, so among 10-point sets with FIVE
distances the nonagon plus centre is optimal. That does not settle `delta(10)`: a set
with 6, 7 or 8 distances could still lie below 8.291, and none was found.

Still open in this directory: `delta(7)`, `delta(8)`, `delta(9)`, each a finite check
against a published list that was not obtained (Lan-Wei 2013 for the 7-point 4-distance
sets; Erdos-Fishburn 1996 for the 9-point ones; the 8-point ones apparently in Wei's
2011 paper on 11-point 5-distance sets), and `delta(n)` for n >= 10 beyond the brackets.
Extending the exact chain to 4 distances from scratch would need the 5-point 4-distance
sets, which include positive-dimensional families (a rectangle with its centre is a
4-distance set for every aspect ratio), so the extension step would have to handle
parameters; that is the next computation if the papers stay out of reach.
