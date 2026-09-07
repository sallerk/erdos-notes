# Erdos #831 - fewest distinct circumradii. Plan.

Started 2026-09-07. Rules in force: tasks/lessons.md (L1-L80), tasks/RULES_COMPUTE.md.

## 0. The problem, verbatim from the site

> "Let h(n) be maximal such that in any n points in R^2 (with no three on a line and
> no four on a circle) there are at least h(n) many circles of different radii passing
> through three points. Estimate h(n)."

So h(n) = min over admissible n-point sets X of the number of DISTINCT circumradii
among the C(n,3) triples of X. Admissible = no three collinear, no four concyclic.

Erdos's own words, [Er75h] = Austral. Math. Soc. Gaz. 2 (1975) 2-3, Renyi archive
item 1975-41, read at source by the literature agent:

> "Let there be given n points in the plane in general position. Denote by h(n) the
> largest integer so that there are at least h(n) circles of different radii passing
> through three of our points. Estimate or if possible determine h(n). How does h(n)
> get modified if we only assume that not all our points are on a circle?"

TWO page discrepancies to check and report separately from any result:
 (a) the site drops Erdos's second question (the "not all on a circle" variant);
 (b) Erdos writes "general position" and the site renders it as no-3-collinear plus
     no-4-concyclic. Martinez-Roldan-Pensado (Acta Math. Hungar. 145 (2015)) working
     on the same family define general position as "no four on a line or circle".
     Which reading is intended changes h(n). Do not calculate before recording this.

## 1. Prior art (scan of 2026-09-07, scratchpad/scan/lit_geom.md)

* Erdos poses h(n) with NO bound and NO value. Never returns to it; his 1978 follow-up
  solves the different Ramsey-type quantity n_k.
* No published value of h(n) for any n. No OEIS sequence (site field: "Possible").
* No arXiv paper on it, ever, except the Ramsey-type relative below.
* One forum comment only (SamKorsky, 16 Jun 2026, partly GPT-assisted, unrefereed):
  (n-2)/2 <= h(n) <= n^2 e^{O(sqrt log n)}.
* Martinez and Roldan-Pensado, "Points defining triangles with distinct circumradii",
  Acta Math. Hungar. 145 (2015), arXiv:1402.6276: solves Erdos's n_k, NOT h(n).
  n_k = O(k^9), n_4 <= 9, n_5 <= 37. Also records that Erdos's 1978 proof has a gap.
* Two users self-flag "currently working on" on the site.

## 2. The analytic line to try first

### 2a. h(4) = 1, and it is Erdos's own remark

[Er75h] opens by quoting E. Szekeres: for any triangle x1x2x3 the orthocentre x4 makes
the four circumradii of the four triples equal, and the four points are not concyclic.
So h(4) <= 1, and h(4) >= 1 trivially. Erdos never writes "h(4)=1"; it follows from
his own sentence. VERIFY in exact arithmetic, including the two side conditions.

### 2b. The reduction to problem #104. This is the main idea.

Fix an admissible X and a radius r. The triples of X with circumradius r are exactly
the circles of radius r through 3 points of X. Scaling by 1/r turns these into UNIT
circles. So, writing f(n) for the maximum number of unit circles through at least
three of n points (this is exactly erdosproblems #104, OEIS A003829):

        (number of triples of X at any single radius)  <=  f(n)

for EVERY admissible X and every r, because f is a maximum over all n-point sets and
our sets are a subfamily. Summing over the h(X) distinct radii,

        C(n,3)  <=  h(X) * f(n)      hence      h(n) >= ceil( C(n,3) / f(n) ).

A003829 is known for n = 3..8: f = 1, 4, 4, 8, 12, 16 (offset 3; a(8)=16 is Harborth
1985, a(4..7) Harborth-Mengersen 1986). That gives, for n = 4..8:

    n            4    5    6    7    8
    C(n,3)       4   10   20   35   56
    f(n)         4    4    8   12   16
    NEW bound    1    3    3    3    4
    (n-2)/2      1    2    2    3    3

so the forum bound is beaten at n = 5, 6 and 8. Nothing here needs a search; it is
two published sequences multiplied together. VERIFY the arithmetic and re-derive the
per-pair count independently before claiming it.

Asymptotic consequence, also free: #104 conjectures f(n) = o(n^2), and that
conjecture is exactly equivalent to h(n) = omega(n) by the same inequality; the
sharper (prized) form f(n) = O(n^{3/2}) would give h(n) = Omega(n^{3/2}). State this
as a conditional implication, not as progress on either problem.

### 2c. Sharpening f(n) to general position. A small computation with real value.

f(n) is a maximum over ALL n-point sets. Our sets are restricted. If the extremal
configuration for f(n) has four concyclic points or three collinear points, then the
restricted maximum f_gen(n) is strictly smaller and the bound of 2b improves. So:
compute f_gen(n) = max number of circles of one radius through exactly three points,
over admissible n-point sets. This is a small exhaustive problem for n <= 7 and is
worth doing regardless of the rest.

### 2d. What the dimension count does NOT give

Naively, forcing C(n,3) - h equalities on 2n - 4 essential parameters suggests
h >= C(n,3) - 2n + 4, which would be cubic in n and would contradict the known
quadratic upper bound. The count is invalid: in a lattice a single translation makes
many triples congruent at once, so the equations are massively dependent. Recorded
here so it is not mistaken for a bound later.

## 3. If the analytic line stalls: the numerical plan

Only if 2b/2c do not settle the small values.

B1. Enumerate radius patterns: partitions of the C(n,3) triples into classes, subject
    to necessary conditions proved first, not assumed:
      - every pair of points lies in at most 2 triples of any one class (two circles
        of a given radius pass through two given points);
      - class size <= f_gen(n);
      - canonical under the S_n action on points.
B2. Decide each pattern exactly. Circumradius equality clears denominators:
    R^2 = a^2 b^2 c^2 / (16 K^2), so R(T1) = R(T2) becomes a polynomial identity
    a1^2 b1^2 c1^2 K2^2 = a2^2 b2^2 c2^2 K1^2. Decide with Groebner and with z3 nlsat,
    two independent deciders (L65). Side conditions as strict inequalities: K != 0,
    the 4x4 concyclicity determinant != 0, points distinct, class radii pairwise
    distinct (L73: least squares never sees these).
B3. Upper bounds by construction: lattice sweep and off-lattice numerical search
    minimising the number of distinct circumradii, every hit re-certified exactly.

## 4. Controls, fixed in advance

* POSITIVE CONTROL (L74): the n=4 orthocentric system must be found by the same
  search machinery that reports any negative. A search that cannot find h(4)=1 may
  not report an absence at n=5.
* TWO DECIDERS (L65): every unrealisable verdict cross-checked by a second method.
* DIRECTION (L3): using the unrestricted f(n) in 2b can only weaken the bound, so an
  error there cannot manufacture a false lower bound.
* No claim of novelty for a TECHNIQUE without its own search (L12, L14).

## 5. Deliverable

Exact h(n) for as many n as fall, the improved lower-bound table, the #104 reduction,
and the two page discrepancies. Every number reproducible from this directory.
