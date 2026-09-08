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
classifications of few-distance sets.

**The cap that makes this finite.** Since `delta >= k`, a configuration can only improve
on an incumbent value D if it has `k < D` distinct distances. With Piepmeyer's 4.664 in
hand at n = 9, only 4-distance sets matter there, and the 9-point 4-distance sets are
classified. The same cap applies at every n, and it is what turns each small case into
a finite exact computation over a published list.

## 2. Status: the table of delta(n)

| n | lower | delta(n) | status | witness |
|---|---|---|---|---|
| 3 | 1 | **1** | PROVED | equilateral triangle |
| 4 | 2 | **2.0731321850** = (sqrt6+sqrt2)/(sqrt6+sqrt2-2) | PROVED | the 2-distance kite with ratio 2cos15 |
| 5 | 2 | **2.6180339887** = (3+sqrt5)/2 | PROVED | the regular pentagon |
| 6 | 3 | **3.4142135624** = 2+sqrt2 | PROVED | the 3-distance set with ratios 1 : (sqrt6+sqrt2)/2 : 1+sqrt3 |
| 7 | 4 | **4.6639024601** | PROVED | any 7 of Piepmeyer's points |
| 8 | 4 | **4.6639024601** | PROVED | any 8 of Piepmeyer's points |
| 9 | 4 | **4.6639024601** = (2+sqrt3)/(1+sqrt3-sqrt(2+sqrt3)) | PROVED | Piepmeyer |
| 10 | 6 | <= 8.2908593694 | bracketed | regular nonagon plus centre |
| 11 | 6 | <= 11.1961524227 = 6+3sqrt3 | bracketed | an 11-point 5-distance subset of the triangular lattice |
| 12 | 6 | <= 11.1961524227 = 6+3sqrt3 | bracketed | the unique 12-point 5-distance set (a lattice set) |
| 13 | 6 | <= 12.9282032303 = 6+4sqrt3 | bracketed | the 13-point 6-distance lattice set |

"PROVED" means an exact computation covering every configuration that could beat the
value. "bracketed" means an upper bound from an explicit set plus a proved floor.

**So Piepmeyer's configuration is optimal for n = 7, 8 and 9**, which answers the
sentence on the problem page for n = 9, and its 7- and 8-point subsets are optimal too.

**How the proved entries are proved.**

* n = 4, 5. Every 2-distance pattern (colouring of the pairs by distance class, up to
  relabelling) was decided by a Groebner basis over Q: at n = 4 all five patterns are
  realisable and their real solutions are exactly the six classical 4-point 2-distance
  sets; at n = 5 sixteen of seventeen patterns are unrealisable and the seventeenth is
  the regular pentagon. A 3-distance set has `delta >= 3`, above both values.
* n = 6. The value `2+sqrt2 < 4` means only sets with at most 3 distances compete. All
  5-point sets with at most 3 distances were decided exactly (124 patterns, 104
  unrealisable, every solution list certified complete; the 34 five-point 3-distance
  sets that result are Shinohara's thirty-four), each was extended by one point in every
  way that keeps at most 3 distances (a complete enumeration, section 4), and the nine
  6-point 3-distance sets found were certified exactly (Shinohara: six maximal ones plus
  the three 6-point subsets of the two 7-point sets). The minimum over them is
  `2+sqrt2`. No 6-point set has 2 distances, so `g(2) = 5` comes out of the same
  computation (and the one 1-distance pattern on 4 points is unrealisable).
* n = 7, 8, 9. The value 4.664 < 5 means only sets with at most 4 distances compete;
  the same chain gives exactly two 7-point 3-distance sets, the regular heptagon
  (delta 5.049) and the hexagon plus centre (7.464), and no 8-point one, so the
  competitors have exactly 4 distances. Those are classified: Erdos-Fishburn (1996,
  Theorem 1) for 9 points (the regular nonagon, two lattice sets, and "three
  equilateral triangles with the same center"), Shinohara (2008, Theorem 1.2(a)) for 8
  points (R_8, R_7 plus centre, a square with four apexes, or an 8-subset of a 9-point
  set), Lan-Wei (2013, Theorem 8) for 7 points (42 sets, listed by family in `e78.py`).
  `e9.py` builds the four 9-point sets exactly and finds delta = 8.291, 9.874, 9.874,
  4.664; the three-triangle set IS Piepmeyer's set (equal distance multisets, exactly).
  `e78.py` builds all 15 eight-point sets and 40 of the 42 seven-point sets explicitly
  (the last two only by the distance ratios Lan-Wei state, which is all delta needs),
  reproducing every family's count, and finds the minimum 4.664 in both cases, attained
  only by subsets of Piepmeyer's set.

**The floors at n = 10, 11, 12.** Wei (2012, Theorem 11) classifies the 10-point
5-distance sets: nonagon plus centre (8.291), regular decagon (20.432), 11-gon minus a
vertex (12.344), the "double R_5" (the pentagon with its five diagonal intersections,
9.216) and the lattice ones (all 11.196). So any 10-point set with delta below 8.291
has at least 6 distances, hence delta >= 6. Likewise Wei (2011) gives the four 11-point
5-distance sets (R_11 and three lattice sets, delta 12.344 and 11.196) and Shinohara
(2008) the unique 12-point one (11.196), so `delta(11), delta(12) >= 6` with the same
argument, and `delta(13) >= 6` from `g(5) = 12`.

**Monotonicity.** Any m-subset of an admissible set is admissible with no larger
diameter, so delta is non-decreasing in n. This caught an error early: a first search at
n = 7 reported 5.049, which cannot exceed `delta(8) <= 4.664`.

## 3. Piepmeyer's configuration, verified, and identified

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
gap and `delta = d_4 = 4.6639`. The ratios are `1 : sqrt(2+sqrt3) : 1+sqrt3 : 2+sqrt3`.

**It is the Erdos-Fishburn set.** Erdos and Fishburn (1996) describe a 9-point
4-distance set "composed of three equilateral triangles with the same center" and call
it "a curiosity in that it is the only verified or conjectured realizer of a g(k) that
is not an R_n or R_n^+ or subset of L_triangle". Built from their description, it has the
same distance multiset as Piepmeyer's set, exactly (`e9.py`). Neither paper cites the
other, and neither names the other's construction.

**Piepmeyer does not extend.** Every way of adding a tenth point was enumerated: the
best gives delta 9.903 with 7 distances, worse than the nonagon plus centre. The same
enumeration applied to the regular nonagon recovers the nonagon plus centre (the
control), and applied to the nonagon plus centre finds no eleventh point with
delta <= 12.

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
heptagon, hexagon plus centre}; `E_8(<= 3)` is empty. All three agree with Shinohara
(2004) and Erdos-Fishburn (1996). The same machinery (`ext2.py`, any number of new
values) gives the one-point extensions of section 3.

**Lattice enumeration.** `lat.py` lists, in integer arithmetic, every n-point k-distance
subset of the triangular lattice up to lattice similarity, with a true diameter bound.
Controls: the 12-point 5-distance set is unique (one class found), the 13-point
6-distance lattice set of Wei's Figure 1 is unique (one class found), the two lattice
9-point 4-distance sets of Erdos-Fishburn's Figure 1, the twenty lattice 7-point
4-distance sets and eight lattice 8-point ones of Lan-Wei and Shinohara, and the three
lattice 11-point 5-distance sets of Wei (2011) are all found with exactly those counts.
At n = 10, k = 5 it finds fifteen sets up to similarity (an independent float
implementation with a different canonical key also finds fifteen); Wei's Theorem 11
shows sixteen lattice figures (2a-2p). Extracting the dot coordinates from the figure
shows panels 2c and 2h are mirror images of one another, so the sixteen contain one
duplicate and Theorem 11 lists 19 sets, not 20. That is a finding about the figure,
not a statement of the paper; it does not affect any entry of the table.

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

## 6. Open here

`delta(n)` for n >= 10. At n = 10 the bracket is [6, 8.291]: a better set would have 6, 7
or 8 distances, and the 10-point sets with 6 or more distances are not classified.
Nothing found by the seeded search beats the nonagon plus centre. At n = 11, 12 the
bracket is [6, 11.196] and at n = 13 it is [6, 12.928]; the lattice sets are the best
known, and every subset of the 13-point lattice set with 6 distances has delta 12.928,
so a 13-point set beating it would need 7 or more distances arranged much more evenly.
