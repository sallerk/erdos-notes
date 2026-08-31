# Erdős Problem #1082, first question — results

**Verdict: no counterexample found.**

Two things came out of it that are worth keeping:

1. **The first question is now settled for every `n ≤ 15`.** It comes down to one
   configuration — the unique 12-point 5-distance set — and that set turns out to have
   **18 collinear triples**, so it does not qualify. (This rests on published theorems plus
   one collinearity computation; as far as we could find it is not recorded anywhere, but
   it is the kind of remark a specialist could reconstruct in an afternoon. We are not
   claiming a hard new theorem.)
2. **The smallest conceivable counterexample has `n = 16` and 7 distances**, and it is
   killed by our exhaustive lattice search *if* Erdős and Fishburn's own conjecture about
   `k = 7` is true.

---

## 1. The question we attacked

Problem #1082 asks two things. We attacked **only the first**.

* **First question (OPEN — our target).** If `A` is a set of `n` points in the plane with
  no three on a line, must the *whole set* determine at least `⌊n/2⌋` distinct distances?
* **Second question (already refuted, NOT our target).** Must *some single point* see at
  least `⌊n/2⌋` distinct distances? Harborth's 8-point set kills this; it is in print in
  Erdős–Fishburn [ErFi97b] and studied by Fishburn [Fi02]. We only used it as a test case.

A counterexample to the first question is: `n` points, no three collinear, with fewer than
`⌊n/2⌋` distinct distances in total.

## 2. A cleaner way to say it

Let

* `g(k)` = the largest planar set with only `k` distinct distances (no other condition);
* `h(k)` = the same, but **also** requiring no three points on a line.

If a counterexample has `k` distances then `k < ⌊n/2⌋`, i.e. `⌊n/2⌋ ≥ k+1`, i.e.
`n ≥ 2k+2`. So

> **the conjecture is exactly the statement `h(k) ≤ 2k+1` for every `k`.**

And `h(k) ≥ 2k+1` always, because a regular `(2k+1)`-gon has `2k+1` points, exactly `k`
distances, and no three of its vertices are collinear. So the conjecture says the regular
odd polygon is the best you can do — the bound `⌊n/2⌋` is attained for *every* `n`.
There is no slack anywhere. That is what makes it hard.

Known values (published): `g(1..6) = 3, 5, 7, 9, 12, 13`. Since `h(k) ≤ g(k)`, we get
`h(k) = 2k+1` for free whenever `g(k) = 2k+1`. Checking `k = 1..6` against `2k+1 = 3, 5,
7, 9, 11, 13`: everything matches **except `k = 5`**, where `g(5) = 12 = 2k+2`. That single
case is Phase 1.

## 3. Verifying the verifier (done before any searching)

All arithmetic is exact integers. Distances are squared distances; collinearity is the
vanishing of an integer 3×3 determinant. No floating point touches any conclusion.
`verify_machinery.py` — 15/15 checks pass:

* Harborth's 8-point set, in exact `Q(√3)` arithmetic: no three collinear, every point sees
  exactly 3 distances (so it does refute the second question), but **4 distinct distances in
  total = ⌊8/2⌋**, so it is *not* a counterexample to the first question. The trap is real
  and our code does not fall into it.
* Regular `m`-gons, in exact cyclotomic-integer arithmetic `Z[x]/Φ_m(x)`, have exactly
  `⌊m/2⌋` distinct distances for `3 ≤ m ≤ 25`.
* The lattice branch-and-bound reproduces `g(k) = 3, 7, 9, 12, 13` for `k = 1, 3, 4, 5, 6`
  inside the triangular lattice, and never exceeds any published `g(k)`. It returns 4 for
  `k = 2`, where the true extremal set is the regular pentagon — not a lattice set, so 4 is
  the correct answer for a lattice pool, and the gap is expected rather than a bug.

## 4. PHASE 1 — the decisive check at `n = 12`

`g(5) = 12` (Erdős–Fishburn), and Shinohara proved the 12-point 5-distance set is
**unique up to similarity**. We enumerated *every* 12-point 5-distance subset of a
triangular-lattice pool (109 points, all sets of squared diameter ≤ 30, origin forced in):
48 of them, falling into **2 classes** under the lattice symmetry group — and those two
classes are the same set up to similarity: multiplying by `1+ζ` (`ζ = e^{iπ/3}`), i.e. the
integer map `(i,j) ↦ (i−j, i+2j)`, scales by `√3`, rotates by 30°, and carries one exactly
onto the other (`check_two_classes.py`). So the enumeration sees one set, as Shinohara's
uniqueness theorem requires.

**The set**, in Eisenstein coordinates `(i, j)` meaning the plane point `(i + j/2, j√3/2)`,
where squared distance is `di² + di·dj + dj²`:

```
(0,0) (0,1) (0,2) (1,-1) (1,0) (1,1) (1,2) (2,-1) (2,0) (2,1) (3,-1) (3,0)
```

Drawn in the triangular lattice it is four rows of 3, 4, 3, 2 points.

* squared distances: `{1, 3, 4, 7, 9}` — exactly **5** distinct distances
* `⌊12/2⌋ = 6 > 5`
* **collinear triples: 18**

### Phase 1 verdict

**The unique maximum planar 5-distance set has 18 collinear triples, so it is not a
counterexample.** Hence `h(5) = 11 = 2·5+1` and `k = 5` closes.

With `k = 5` closed, `h(k) = 2k+1` for every `k = 1..6`, and that settles every `n ≤ 15`:
if an `n`-point set with no three collinear had `k < ⌊n/2⌋` distances, then `k ≤ 6`, so
`n ≤ h(k) = 2k+1 ≤ 2⌊n/2⌋ − 1 ≤ n − 1`, a contradiction.

This is the expected outcome, and it is worth stating plainly what it means: *without* the
no-three-collinear condition the claimed inequality is already **false** at `n = 12`
(5 distances < 6). The 18 collinear triples are the only thing saving the conjecture there.
The whole content of problem #1082's first question is the collinearity hypothesis.

Verified three independent ways (`verify_set1.py`), all agreeing on 5 distances and 18
collinear triples: (1) integer Eisenstein arithmetic, (2) sympy symbolic Cartesian
arithmetic with `√3`, (3) an independent integer model on doubled coordinates.

## 5. Where the first possible counterexample can be

A counterexample on `n` points needs `n ≤ g(⌊n/2⌋−1)`. Running that against the published
`g` values (`frontier.py`):

| `n` | needs `k =` | `g(k)` | possible? |
|---|---|---|---|
| 4–11 | 1–4 | 3, 5, 7, 9 | no — too many points |
| **12** | 5 | 12 | survives counting — **killed by Phase 1** |
| 13 | 5 | 12 | no |
| 14, 15 | 6 | 13 | no |
| **16** | 7 | unknown | **first open case** |

> **The smallest conceivable counterexample has `n = 16`, and it must be a *maximum*
> 7-distance set** (so `g(7) ≥ 16` is a prerequisite). Everything below 16 is now closed.

## 6. PHASE 2 — searching the frontier

For each `k` we asked each pool the decisive question directly: *is there a subset of
`2k+2` points with at most `k` distinct distances and no three collinear?* Answer
everywhere: **no**. We also report `g_pool` (largest `k`-distance subset, no collinearity
condition) and `h_pool` (largest with the condition).

### 6a. Triangular lattice `A2` — exhaustive, squared diameter ≤ 147 (535-point pool)

This is the pool Erdős and Fishburn's own conjecture points at: they conjectured that for
`k ≥ 7`, *every* maximum planar `k`-distance set is similar to a triangular-lattice subset.

| `k` | need `n ≥` | `g_A2(k)` | `h_A2(k)` | `2k+1` | counterexample? |
|---|---|---|---|---|---|
| 5 | 12 | 12 | 9 | 11 | no |
| 6 | 14 | 13 | 9 | 13 | no |
| 7 | **16** | **16** | **10** | 15 | no |
| 8 | 18 | 19 | 12 | 17 | no |
| 9 | 20 | 21 | 12 | 19 | no |
| 10 | 22 | 24 | 12 | 21 | no |
| 11 | 24 | 27 | 13 | 23 | no |

(`k = 5..10` exhaustive to squared diameter 147; `k = 11` to 108.)

Read the `k = 7` row carefully. `g_A2(7) = 16 ≥ 16`: the triangular lattice **does** contain
a 16-point 7-distance set — so the unrestricted inequality genuinely fails at `n = 16`, and
the frontier is live. But that set has **42 collinear triples**, and more strongly
`h_A2(7) = 10`: the biggest no-three-collinear 7-distance set anywhere in the lattice has
only 10 points, nowhere near 16.

**Consequence: assuming the Erdős–Fishburn conjecture at `k = 7`, there is no
counterexample at `n = 16`.** The chain: their conjecture makes every maximum 7-distance
set a triangular-lattice subset, so `g(7)` equals the lattice maximum, which our exhaustive
search puts at 16; then any 16-point 7-distance set is maximum, hence a lattice subset,
hence (since `h_A2(7) = 10`) has three points on a line. The `k ≥ 8` rows say the same
about `n = 18, 20, 22, 24`.

The pattern is stark and stable across every pool size we tried (squared diameter 30, 49,
75, 108, 147 — identical numbers throughout): the lattice is what makes the *unrestricted*
statement false, and general position destroys it completely. `h_A2` sits at 9–13 while
`2k+1` climbs to 23. Note `h_A2(5) = 9 < 11`: the lattice cannot even match the regular
11-gon, which is a warning that lattices are the wrong pool for the collinearity-constrained
problem — a lattice is *made* of collinear triples.

Square lattice `Z2` (exhaustive to squared diameter 100, 317 points) is weaker still:
`g_Z2(5..10) = 9, 9, 12, 14, 16, 17` and `h_Z2(5..10) = 6, 8, 8, 8, 9, 12`. No
counterexample.

### 6b. A richer non-lattice pool: `Z[√3] × Z[√3]`

Points `(a + b√3, c + d√3)` with integer `a,b,c,d`. All arithmetic exact in `Z[√3]`.
This ring simultaneously contains the square lattice, a scaled triangular lattice, all
regular triangles/squares/hexagons/12-gons on them, **and Harborth's 8-point set** — the
one known non-lattice extremal configuration for this problem. Cross-checked: the
`Z[√3]` module and the independent `Q(√3)` module agree exactly on H8.

Pools of 429, 625, 965 and 1177 points (`|coeff| ≤ 2, 3, 4`, bounded squared norm);
`h_pool` is exhaustive within each pool, and the table shows the best over all of them:

| `k` | need `n ≥` | `h_pool(k)` | `2k+1` | counterexample? |
|---|---|---|---|---|
| 3 | 8 | 6 | 7 | no |
| 4 | 10 | **8** | 9 | no |
| 5 | 12 | 9 | 11 | no |
| 6 | 14 | 12 | 13 | no |
| 7 | 16 | 12 | 15 | no |

Much better than the lattices on the collinearity-constrained side (as expected — it
contains them), and the `k = 4` entry of 8 *is* Harborth's set itself, recovered by the
search. Still never within 4 of the target. On the unrestricted side this pool also finds
the 12-point 5-distance set (`g_pool(5) = 12`), confirming both worlds are covered.

*Honesty note:* unlike the lattice runs, this is **not** an exhaustive sweep of a similarity
class. The pool is cut off by a bound on the integer coefficients as well as by radius, and
translating a configuration can push coefficients outside the box. Treat it as a broad
heuristic sweep, not a proof.

*Status note:* the 1177-point pool finished `k = 6` (`h_pool = 12`, no counterexample). A
still larger pool (1429 points, `|coeff| ≤ 3`, `|z|² ≤ 32`) was still running `k = 6` when
this was written (`z3d2.log`). It had not reported a counterexample, but a search that is
still running is not a result, so the table uses only runs that finished.

### 6c. Concentric regular polygons (floating-point screen)

Both known non-lattice extremal configurations for #1082 live here: Harborth's 8 points are
two concentric squares, and eigensolver's 42-point counterexample to the *second* question
is two concentric 21-gons. We scanned two rings of `N` points each (`N = 3..15`, radius
ratio on an 8001-point grid, offsets `0` and `π/N`) and three rings (`N = 3..7`, 2-D radius
grid).

Result: for two rings the minimum number of distinct distances is **exactly `⌊n/2⌋`, never
less**, attained only when the two rings merge into a single regular `2N`-gon. Three rings
are strictly worse. This screen is floating point and certifies nothing; its job was to say
whether anything in the family gets close, and nothing does.

### 6d. Is the known tight configuration extendable? (pool-free, complete)

Delete any point from a hypothetical counterexample on `n = 2k+2` points with `k` distances
and you get `2k+1` points, `k` distances, no three collinear — a configuration meeting the
bound *exactly*. The regular `(2k+1)`-gon is the one such family known for every `k`
(individual `k` may admit others; we have not classified them). So:

> can a regular `(2k+1)`-gon be extended by one point without adding a new distance?

This is finite and needs no pool. If `p` works then `|p−v_0|` and `|p−v_1|` both lie in the
`k`-element distance set, so `p` is one of at most `2k²` intersection points of two circles;
enumerate those and test against the remaining vertices (`extend.py`, 60-digit arithmetic).

**Result: zero extensions, for every `m = 2k+1` from 5 to 41.** The regular odd polygon is
rigid — you cannot add a `(2k+2)`-nd point at all, never mind one in general position.

Positive controls (`extend_control.py`), so that "zero" is not just a broken search: the
finder *does* locate the centre of the regular hexagon (at distance = side length from all
6 vertices) and the centre of the regular 12-gon, and correctly rejects both for putting
three points on a line; and it correctly reports no extension for the pentagon.

### 6e. A structural remark that kills a whole natural family

**If all `n` points lie on one circle, the conjecture is true** — and so is the stronger
per-point version. Proof: fix a point `p` of the set. For `q` on the circle, `|pq|`
determines `q` up to reflection in the diameter through `p`, so `q ↦ |pq|` is at most
2-to-1 on the other `n−1` points, and `p` alone sees at least `⌈(n−1)/2⌉ = ⌊n/2⌋` distances.

So no concyclic set is ever a counterexample — no subset of a regular polygon, nothing on
a single circle. That is exactly why both known counterexamples to the *second* question
need two concentric circles, and it explains the 6c result.

## 7. Prior art

We read all 21 comments on the problem page (fetched with a browser user-agent; `WebFetch`
gets 403). Every one of them is about the **second** question — the Harborth/DeepMind
8-point construction, the attribution discussion, and eigensolver's 42-point two-21-gon
construction. Boris Alexeev states explicitly in the thread that the main conjecture is
still open. **We found no computational attack on the first question, in the comments or in
the literature.** The nearest published work is few-distance-set enumeration (Erdős–Fishburn,
Shinohara, Wei) — the same search *without* the collinearity constraint — which is what
supplied our `g(k)` values. Secondary sources also credit Dumitrescu with improving
Szemerédi's `n/3` to `⌈(13n−6)/36⌉` for the per-point version — we did not read that paper,
so treat the exact form as unverified here; either way `13/36 < 1/2`, so it does not by
itself rule out any `n`.

## 8. What remains

* `n = 16` with 7 distances is the first open case, and it is open only because `g(7)` is
  unknown. If someone proves the Erdős–Fishburn "triangular lattice" conjecture at `k = 7`,
  our lattice search closes `n = 16` outright.
* Our exhaustive statements cover triangular-lattice sets of squared diameter up to 147
  (`k ≤ 10`) and square-lattice sets up to 100. The `Z[√3]` and concentric-polygon results
  are heuristic sweeps, not proofs. The polygon-rigidity result of §6d is complete but only
  covers extensions *of the regular polygon*.
* The obvious next step is the one we could not do: classify the `(2k+1)`-point,
  `k`-distance, no-three-collinear configurations for `k = 7` (are they only the regular
  15-gon?). Combined with §6d's circle-intersection extension test — which is complete and
  pool-free once you have the `(2k+1)`-point sets — that would settle `n = 16` outright.
* Not attempted: cyclotomic pools of odd order (`Z[ζ_5]`, `Z[ζ_7]`, …); and any search over
  general real configurations, which would need an abstract-distance-matrix enumeration
  plus a realizability test.

## Files

| file | what |
|---|---|
| `geo.py` | exact integer geometry; exact `Q(√3)` arithmetic |
| `search.py` | numba branch-and-bound over a lattice pool |
| `cyclo.py` | exact `Z[√3] × Z[√3]` pool |
| `verify_machinery.py` | 15 ground-truth checks, run before any search |
| `phase1.py` | enumerate all 12-point 5-distance sets, test collinearity |
| `verify_set1.py` | the Phase 1 set, checked three independent ways |
| `check_two_classes.py` | the two enumerated classes are one set up to similarity |
| `frontier.py` | which `n` are ruled out; the `n = 16` frontier |
| `phase2_lattice.py`, `phase2_z3.py`, `concentric.py` | the Phase 2 searches |
| `extend.py`, `extend_control.py` | rigidity of the regular odd polygon, plus controls |
| `page1082.txt`, `comments1082.txt` | the problem statement and all 21 comments |

*Note for reuse: numba's `cache=True` silently corrupts recursive `@njit` functions and
crashes with an access violation. `search.py` must keep `cache=False`.*
