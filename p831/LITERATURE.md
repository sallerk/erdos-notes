# Erdős #831 — literature report

Compiled 2026-09-07. Two questions: (1) novelty of the reduction `h(n) ≥ ⌈C(n,3)/f(n)⌉`;
(2) the extremal configurations for `f(n)` = A003829, `n = 4..8`, and whether they are
degenerate for #831 (three collinear / four concyclic).

Every claim below is tagged:

* **[VERIFIED AT SOURCE]** — I read the primary text (or ran the computation) myself.
* **[SECONDHAND]** — reported by a reliable intermediary (OEIS, a citing paper, a review).
* **[NOT OBTAINED]** — I could not reach the source; nothing is claimed about its contents.

Files saved into this directory are named at each point.

---

## 0. Sources obtained, and sources that resisted

| Source | Status | Local file |
|---|---|---|
| Erdős, *Some problems on elementary geometry*, Austral. Math. Soc. Gaz. 2 (1975) 2–3 = **[Er75h]** | **[VERIFIED AT SOURCE]** | `erdos_1975-41.pdf`, `er1975_p1.png`, `er1975_p2.png` |
| Harborth, *Einheitskreise in ebenen Punktmengen*, 3. Kolloquium über Diskrete Geometrie, Salzburg, May 1985, 163–168 | **[VERIFIED AT SOURCE]** (all 6 pages read) | `A003829_harborth1985.pdf`, `page163.jpg` … `page168.jpg` (+ `_full.jpg`) |
| OEIS A003829 entry + illustration | **[VERIFIED AT SOURCE]** | `A003829.txt`, `oeis_internal.txt`, `A003829.svg` |
| Martínez & Roldán-Pensado, arXiv:1402.6276 | **[VERIFIED AT SOURCE]** | `MartinezRoldanPensado_1402.6276.pdf` |
| erdosproblems.com pages + forum threads 104, 831, 506, 1068 | **[VERIFIED AT SOURCE]** | `ep*.html`, `thread*.html`, `hist104.html` |
| Erdős, *Some of my favourite problems…* (Resenhas version) | **[VERIFIED AT SOURCE]** | `Erdos_favourite_problems.pdf` |
| Erdős, Renyi archive 1983-03 | **[VERIFIED AT SOURCE]** (searched; no unit-circle content) | `erdos_1983-03.pdf` |
| **Harborth & Mengersen, *Point sets with many unit circles*, Discrete Math. 60 (1986) 193–197** | **[NOT OBTAINED]** | — |
| **Erdős & Purdy, Handbook of Combinatorics ch. 17, pp. 847–848** | **[NOT OBTAINED]** | — |
| **Brass–Moser–Pach, *Research Problems in Discrete Geometry*** | **[NOT OBTAINED]** | — |

Access notes, so the failures are reproducible: ScienceDirect returns HTTP 403 to every
fetcher I have, including a real Chrome instance (Cloudflare `CPE00001`); Unpaywall reports
`is_oa: false` for DOI `10.1016/0012-365X(86)90011-7`; zbMATH's REST API has the record
(Zbl 0638.52005) but carries **no review text**, and its web front end is Cloudflare-gated;
the Internet Archive holds *Handbook of Combinatorics* (1995) as
`handbookofcombin0001unse` but the item is lending-restricted (`401` on the OCR text,
search-inside endpoints dead). **Three of the sources named in the task are therefore
unread, and nothing below is asserted about them.**

---

# QUESTION 1 — Is the reduction novel?

## 1.1 Short answer

**No — the inequality is already stated on the #831 page itself**, in the special case
obtained from the general bound `f(n) ≤ n(n−1)/3`. What I found **no** trace of anywhere is
the use of the **exact A003829 values** to bound `h(n)` for small `n`.

## 1.2 The decisive find: the #831 forum comment

`thread831.html`, the **only** comment on the problem — SamKorsky, 04:34 on 16 Jun 2026 —
opens **[VERIFIED AT SOURCE]**:

> "Note that the same simple double-counting lower bound from #104 gives $h(n) \ge (n - 2)/2$.
> For an upper bound, I'll sketch below how to get $h(n) \le n^2\exp\left(O(\sqrt{\log{n}})\right)$."

That `(n−2)/2` **is** the reduction. Exactly:

```
C(n,3) / (n(n-1)/3)  =  [n(n-1)(n-2)/6] · 3/(n(n-1))  =  (n-2)/2
```

so the comment is `h(n) ≥ C(n,3)/f(n)` evaluated with the Harborth–Mengersen upper bound
`f(n) ≤ n(n−1)/3` quoted on the #104 page. The idea "bound the triples at any one radius by
the #104 quantity, then divide" is therefore **published prior art as of 16 June 2026**, on
the #831 page, and must not be claimed as new.

The comment does not name `f(n)`, does not cite A003829, and does not evaluate anything at
small `n`. Its remaining content is an unrelated upper-bound argument (paraboloid lift +
generic projection), with an AI-assistance acknowledgement for the constant optimisation.

## 1.3 Erdős's own paper: the two problems are adjacent, but never linked

**[VERIFIED AT SOURCE]** — `erdos_1975-41.pdf` is [Er75h], the common source of #104 and
#831. It is two pages and defines **three** quantities in immediate succession:

* `f(n)` (p. 2) — "the largest integer so that there are `f(n)` distinct **circles of radius
  one** determined by the `C(n,3)` triples", with
  `(1)  3n/2 < f(n) ≤ n(n−1)`.
  (Note the site and the OEIS both give the lower bound as `≫ n`; Erdős writes `3n/2`.)
* `g(n)` (p. 3) — "the maximum number of **triples** … so that the circumscribed circle has
  unit radius", assuming not all points are on a unit circle.
* `h(n)` (p. 3) — the #831 quantity.

**No inequality relating any two of them appears.** Erdős simply lists them. He does not
observe that `g` is the per-radius count that controls `h`.

Two further things in [Er75h] that bear directly on this attack:

1. **Erdős himself poses the general-position version of `f(n)`** — the exact quantity
   Question 2 is about:

   > "Let me state a few modifications of the above problem. First of all assume that our
   > points are in general position, i.e. no four are on a circle and no three on a line.
   > Determine or estimate `f(n)` under these conditions."

   Call it `f_gp(n)`. It does not appear to have its own entry on erdosproblems.com.
   **This, not `f(n)`, is the quantity the reduction actually needs.**

2. Erdős's "general position" is defined in this paper as **no four on a circle and no three
   on a line** — matching the #831 page's rendering exactly. Discrepancy (b) in `PLAN.md` is
   resolved in the site's favour. Discrepancy (a) stands: the site drops Erdős's follow-up
   sentence, "How does `h(n)` get modified if we only assume that not all our points are on a
   circle?"

## 1.4 Everything else I checked, and found nothing in

| Checked | Result |
|---|---|
| **Harborth 1985** (primary, read in full) | Poses only the *inverse* question of Erdős [2,4] — "the smallest number `n` of boundary points of `f(n)` congruent circles such that each circle is fixed in position by three of the `n` boundary points". **No mention of distinct radii, of `h(n)`, or of general position.** **[VERIFIED AT SOURCE]** |
| **Martínez & Roldán-Pensado, arXiv:1402.6276** | Zero occurrences of `unit`, `Harborth`, `Mengersen`, `congruent`, `Elekes`, `equal radi`, `f(n)`, `h(n)`, `A0038`. Its 6 references contain no unit-circle paper. It solves Erdős's `n_k` (Ramsey-type) only. **No link to #104 whatsoever.** **[VERIFIED AT SOURCE]** |
| **#104 page + thread** (4 comments) | Comments are about the prize amount ($100 vs £100) and a source citation. Body says only "See also [506] and [831]". **[VERIFIED AT SOURCE]** |
| **#506 page + thread** | Zero occurrences of `unit circle`, `radius`, `radii`, `A003829`, `Harborth`, `congruent`, `circumrad`. It is the *minimum number of circles of any radii* — a different quantity. **[VERIFIED AT SOURCE]** |
| **#1068** | *"Does every graph with chromatic number ℵ₁ contain a countable subgraph which is infinitely vertex-connected?"* — set theory / graph theory, **entirely unrelated** to #831. I believe this number was included in the task in error. **[VERIFIED AT SOURCE]** |
| **Citations of Harborth–Mengersen 1986** | Semantic Scholar records **2** citing papers: "Plane point sets with many squares or isosceles right triangles" (2021) and "Improvement of Inequalities for the (r;Q)-structures…" (1995). Neither concerns circumradii. (S2's coverage of 1986 Elsevier papers is incomplete, so this is a weak negative.) **[VERIFIED AT SOURCE]** |
| **Erdős, Renyi 1983-03** | No occurrences of `unit circle`, `radius one`, `different radii`, `distinct radii`, `g(n)`. **[VERIFIED AT SOURCE]** |
| **Erdős, *My favourite problems*** (`Erdos_favourite_problems.pdf`) | §6 restates `f(n)` and Elekes's `n^{3/2}` construction. The `h(n)` problem is **absent** from this version. **[VERIFIED AT SOURCE]** |
| Web searches: `"distinct circumradii"`, `"circles of equal radius through three points"`, `"triple points of a family of congruent circles"`, `"isoradial triangles point set"`, and combinations | Nothing linking the two problems. **[VERIFIED AT SOURCE]** (negative result of a search, not of a text) |
| **Erdős–Purdy Handbook pp. 847–848**; **Brass–Moser–Pach** | **[NOT OBTAINED]** — see §0. OEIS records **[SECONDHAND]** that Erdős–Purdy p. 848 carries the `f`-values and that p. 847 "incorrectly says that each circle must contain a pair of the points". Whether either book relates `f` to `h` is **unknown**. |

## 1.5 Two technical points worth recording

**(a) The reduction needs the no-four-concyclic hypothesis, and it is the reason `f` (circles)
may be substituted for `g` (triples).** In general the triples at a fixed radius `r` number
`Σ_i C(k_i, 3)` over the circles of radius `r`, where `k_i` is the number of points on the
`i`-th circle — which is Erdős's `g(n)`, not `f(n)`. Under #831's hypothesis every circle
carries **at most 3** points, so `k_i = 3` and the two counts coincide. The one-line argument
is valid, but the hypothesis is load-bearing, not decorative.

**(b) `PLAN.md` overstates the asymptotic consequence.** It says #104's conjecture
`f(n) = o(n²)` "is exactly equivalent to `h(n) = ω(n)`". The inequality runs one way only:
`f_gp(n) = o(n²) ⟹ h(n) = ω(n)`. Nothing here yields the converse. Recommend weakening
"exactly equivalent" to "implies".

## 1.6 What is left that might be new

Not the inequality. What I found no source for is:

* substituting the **exact** values `f(5..8) = 4, 8, 12, 16` rather than `n(n−1)/3`;
* the observation that the correct input is `f_gp` (Erdős's own general-position variant),
  which is `≤ f` and possibly strictly smaller;
* the numerical consequences below.

`h(n) ≥ ⌈C(n,3)/f(n)⌉` against the forum's `⌈(n−2)/2⌉`:

| n | C(n,3) | f(n) | ⌈C(n,3)/f(n)⌉ | ⌈(n−2)/2⌉ |
|---|---|---|---|---|
| 4 | 4 | 4 | **1** | 1 |
| 5 | 10 | 4 | **3** | 2 |
| 6 | 20 | 8 | **3** | 2 |
| 7 | 35 | 12 | **3** | 3 |
| 8 | 56 | 16 | **4** | 3 |

So the exact values beat the published forum bound at `n = 5, 6, 8`. This is arithmetic on two
published sequences; it needs no search. It should be presented as *"the forum's reduction,
instantiated with A003829"*, crediting SamKorsky (16 Jun 2026) for the reduction.

---

# QUESTION 2 — The extremal configurations for f(n), n = 4..8

## 2.1 "At least three" vs "exactly three" — settled

The counting convention is **AT LEAST three**, unambiguously, in all three primary sources:

* **Harborth 1985, Satz (p. 163)** **[VERIFIED AT SOURCE]** — emphasis his:
  > "Für die größte Anzahl f(8) von verschiedenen Einheitskreisen in der Ebene, auf deren Rand
  > jeweils **mindestens drei** von acht gegebenen Punkten liegen, gilt f(8) = 16."

  (*mindestens drei* = at least three.)
* **Erdős**, `Erdos_favourite_problems.pdf` §6 **[VERIFIED AT SOURCE]**: "the maximum number
  of distinct unit circles which contain **at least three** of our points".
* **erdosproblems #104** **[VERIFIED AT SOURCE]**: "the number of distinct unit circles
  containing **at least three** points".

The **OEIS name** — "Maximal number of unit circles through n points in plane, each circle
containing 3 of the points" — is the loose one, and reads as *exactly* three. It is the
outlier and should be treated as informal phrasing, not as a different quantity.

The distinction happens not to bite at `n = 8`: Harborth's own **Figur 2 caption (p. 168)**
reads "Auf 16 verschiedenen Einheitskreisen liegen jeweils **3** von 8 Punkten" — in the
extremal set each of the 16 circles carries exactly 3 points.

## 2.2 Harborth 1985 — contents (primary, read in full)

* p. 163: statement; `c·n^{3/2} ≤ f(n) ≤ n(n−1)/3`; the lower bound credited to Elekes [1],
  the upper bound from "through each pair of points at most two congruent circles are
  determined". States that **[SECONDHAND, via Harborth]** "Als erste exakte Werte wurden in
  [3] kürzlich f(3) = 1, f(4) = 4, f(5) = 4, f(6) = 8 und f(7) = 12 bestimmt" — i.e. the
  `n ≤ 7` values are Harborth–Mengersen's, cited as "[3] … (Erscheint)" = to appear.
* p. 163: the `f(8) ≤ 16` sketch — if 4 of the 8 points already determine 4 unit circles then
  each pair of those 4 lies on 2 of them, so `f(8) ≤ 4 + 2·C(4,2) = 16`.
* p. 164: `f(8) ≤ (2·7 + 6·6)/3 = 16` **if at most 2 points lie on 7 unit circles**, using
  "[3], Lemma 2": each point lies on at most 7 unit circles. Then the case analysis assumes
  `P₈`, `P₁` and a third point each lie on 7 circles.
* pp. 164–166: 24 cases `q₁…q₂₄` eliminated; the surviving structure is listed.
* p. 166: the construction, and `f(8) ≥ 16`.
* p. 167: Figur 1 (a construction diagram), and the completion of `f(8) ≤ 16`.
* p. 168: **Figur 2** — the extremal 8-point set with the 16 circle centres — and the
  4-item bibliography ([1] Elekes 1984; [2] Erdős, Congressus Numerantium 39 (1983) 3–20;
  [3] Harborth–Mengersen; [4] **Moser & Pach, *Research Problems in Discrete Geometry* 1984,
  Problem 25** — the predecessor of Brass–Moser–Pach).

**The paper gives no coordinates and no configuration description for `n ≤ 7`**; those live
in Harborth–Mengersen 1986, which I could not obtain.

## 2.3 The OEIS illustration `a003829.svg`

**[VERIFIED AT SOURCE]** (source read, coordinates extracted, counts re-derived). By Martin
Fuller — an OEIS contributor's drawing, **not** taken from either paper, so as evidence about
*the papers'* extremal sets it is **[SECONDHAND]** at best. It is 770×980, covering a(3)–a(7):

* **a(3) = 1** — an equilateral triangle inscribed in one unit circle.
* **a(4) = a(5) = 4** — one panel only, drawn with **4 points**: `(0,0)`, `(0,−1)`,
  `(±√3/2, 1/2)`, with all four unit circles drawn. Nothing is drawn for `n = 5`.
* **a(6) = 8** — captioned *"8 circles are defined by any symmetric subset of 6 of the points
  shown below"* and *"These graphs of points, centers and radii are unit-distance embeddings
  of the rhombic dodecahedral graph."* A pool of **8** points is drawn —
  `(±1.56, 0)`, `(±0.36, 0)`, `(0, ±0.52)`, `(0, ±1.08)` — followed by **four** 6-subset
  panels with the point–centre incidence graphs drawn explicitly.
* **a(7) = 12** — exact coordinates given in the caption:
  `(−⅔, 0)`, `(0, 0)`, `(⅓(−1+√7), ±⅓√2)`, `(⅔, 0)`, `(⅓(1+√7), ±⅓√2)`,
  with the 12 circle centres drawn and the coordinate axes shown in grey.

## 2.4 Verification and degeneracy, per n

All of the following is **[VERIFIED AT SOURCE]** in the sense of *I ran it*:
`verify_f_configs.py`, `probe_general_position.py`, `probe2.py`, `probe3b.py`.
Collinearity test = triangle area; concyclicity test = spread of the four circumcentres of a
4-subset.

### n = 4 — **NOT degenerate**

Extremal set = **a triangle together with its orthocentre**, scaled to circumradius 1. This is
Erdős's opening paragraph in [Er75h], credited to **Mrs. E. Szekeres** **[VERIFIED AT SOURCE]**:

> "Mrs. E. Szekeres observed that there always is a unique point `x₄` so that `x₁, x₂, x₃, x₄`
> are **not on a circle** and so that the radii of the four circles determined by the four
> triples … are the same. It suffices to choose `x₄` as the orthocentre of the triangle
> `x₁, x₂, x₃`."

The OEIS panel draws the equilateral case (where the orthocentre is the centre):
`(0,0), (0,−1), (±√3/2, 1/2)` → 4 unit circles, **0 collinear triples, 0 concyclic 4-sets**.
It is a **2-parameter family**: 1906 of 2000 random triangles + orthocentre gave an admissible
4-point set with all four circumradii equal to 1 (the failures are near-degenerate triangles).
So `f_gp(4) = f(4) = 4`.

### n = 5 — **NOT degenerate**

`f(5) = f(4) = 4`; the OEIS draws no separate picture. Adding **any** generic 5th point to the
`n = 4` set keeps the count at 4: **300/300** random extra points gave an admissible 5-point
set with 4 unit circles. So `f_gp(5) = f(5) = 4`.

### n = 6 — illustrated sets ARE degenerate, but the structure is NOT

Each of the four 6-subsets drawn in the SVG gives exactly **8** unit circles (confirmed), and
each has **4 collinear points** (4 collinear triples), 0 concyclic 4-sets:

| SVG panel | points | degeneracy |
|---|---|---|
| (5.8, 6.8) | `(±1.56,0)`, `(0,±0.52)`, `(0,±1.08)` | `(0,±0.52),(0,±1.08)` collinear on the y-axis |
| (9.2, 6.8) | `(±1.56,0)`, `(±0.36,0)`, `(0,±1.08)` | `(±1.56,0),(±0.36,0)` collinear on the x-axis |
| (5.8, 9.2) | `(±1.56,0)`, `(±0.36,0)`, `(0,±0.52)` | same, x-axis |
| (9.2, 9.2) | `(±0.36,0)`, `(0,±0.52)`, `(0,±1.08)` | y-axis |

(The full 8-point pool is worse still: 8 collinear triples **and** 8 concyclic 4-sets, and it
carries only 8 unit circles, each through 4 points — so it is *not* an `f(8)` configuration.)

**But this degeneracy is an artefact of the symmetric choice.** The incidence structure is the
complete tripartite triple system `K(2,2,2)`: split the 6 points into three pairs
`{A₁,A₂}, {B₁,B₂}, {C₁,C₂}`, and all **8** transversal triples have circumradius 1. That is 8
equations in 9 essential degrees of freedom (12 coordinates − 3 for rigid motion), so the
realisation space is positive-dimensional, and **admissible members exist**. Explicit witness
(`probe2.py`; residual `max|R−1| = 4.4·10⁻¹⁶`):

```
P1  0.000000000000   0.000000000000
P2  2.168445723554   0.000000000000
P3  0.692117263890  -0.029359239861
P4  1.476328459664   0.029359239861
P5  1.110570588219   1.611583161835
P6  1.057875135335  -1.611583161835
```

8 unit circles (`{1,3,5} {1,3,6} {1,4,5} {1,4,6} {2,3,5} {2,3,6} {2,4,5} {2,4,6}`);
**0 collinear triples, 0 concyclic 4-sets**; min triangle area over all 20 triples `0.0318`;
min circumcentre spread over all 15 quadruples `0.883` — robustly non-degenerate, not a
near-miss.

**Conclusion: `f_gp(6) = 8 = f(6)`. No improvement to `h(6)` from this route.**

### n = 7 — **DEGENERATE, and the degeneracy is forced (for this triple system)**

The SVG's exact coordinates give exactly **12** unit circles (confirmed), and the set is
**doubly** degenerate:

* **collinear triple**: `(−⅔,0), (0,0), (⅔,0)` — three points on the x-axis;
* **concyclic 4-set**: `(⅓(−1+√7), ±⅓√2)` together with `(⅓(1+√7), ±⅓√2)` — these four form
  an axis-aligned **rectangle** (two x-values, `±` the same y), hence are automatically
  concyclic.

So this set violates **both** of #831's conditions.

Rigidity test (`probe2.py`): the Jacobian of the 12 realisation equations at this solution has
**rank 11** in 14 unknowns, so the local solution manifold is 3-dimensional — exactly the
translations and the rotation. **The configuration is rigid up to congruence** (scale is
pinned by radius 1); it has zero essential moduli, unlike the `n = 6` case. Consistent with
this, **1458 of 1458** perturbed re-solves returned the identical signature
`(1 collinear triple, 1 concyclic 4-set, 12 circles)`, and **0** were admissible.

**Caveat — this is the one place where I must not overclaim.** What is established is that
*this* 12-circle triple system forces degeneracy. I have **not** ruled out a *different*
triple system realising 12 unit circles on 7 points, so **`f_gp(7) < 12` is not proved.** A
restricted search (`probe3b.py`, seeded from the `n = 6` witness and adding a 7th point on
further unit circles) produced admissible 7-point sets with up to **10** unit circles, so what
is actually known is

```
10  ≤  f_gp(7)  ≤  12.
```

**This is the only value of n where the degeneracy could still improve the bound**: `f_gp(7) ≤ 11`
would give `h(7) ≥ ⌈35/11⌉ = 4`, up from 3.

### n = 8 — **DEGENERATE (three collinear triples)**

Harborth gives no coordinates, but the construction on p. 166 is fully algebraic and I
reconstructed it. Set `P₈ = 0`; let `z₁,…,z₇` be the unit vectors from `P₈` to the centres of
the seven unit circles `C₁,…,C₇` through `P₈`, which the paper fixes as the triples

```
C1={1,2,8} C2={1,3,8} C3={2,4,8} C4={3,5,8} C5={4,6,8} C6={5,7,8} C7={6,7,8}
```

Two unit circles through `P₈ = 0` with centres `z_a, z_b` meet again at `z_a + z_b`, so

```
P1=z1+z2  P2=z1+z3  P3=z2+z4  P4=z3+z5  P5=z4+z6  P6=z5+z7  P7=z6+z7
```

(the paper states `P₂ = z₁ + z₃` explicitly, confirming the indexing). The relations Harborth
derives and then uses in the construction are, verbatim from p. 166:

> "Aus den Rhomben `P₁M₁₅₇P₇M₁₂₇` und `P₂M₁₂₇P₇M₂₆₇` folgen `z₄ = −z₃` und `z₅ = −z₂`."

and

> "Werden nun `P₈`, `z₃ = M₈₂₄` und `z₂ = M₈₁₃` gewählt, und danach `z₁ = M₈₂₁` so bestimmt,
> daß `z₆ + z₇ = 2z₁ + z₂ + z₃` gilt und `2z₃ − z₂ + z₁ − z₆ = M₂₄₅ − P₅` ein Einheitsvektor
> ist (siehe Figur 1), dann sind alle 16 Kreise festgelegt und wie in Figur 2 auch möglich.
> Damit ist schon `f(8) ≥ 16` bewiesen."

Solving that system numerically (`verify_f_configs.py`) gives, for 6 independent solutions:

* exactly **16** unit circles, each through exactly 3 points — matching Figur 2's caption;
* the 16 triples
  `{1,2,8} {1,3,8} {2,4,8} {3,5,8} {4,6,8} {5,7,8} {6,7,8} {1,2,7} {1,3,6} {1,5,7} {1,4,6} {1,4,5} {2,4,5} {2,6,7} {2,3,5} {2,3,6}`;
* **an independent check that the reconstruction really is Harborth's set**: p. 167 asserts
  that `P₃, P₄, P₇` lie on a circle of **radius 2** (centre `z₂ + z₃`), and every solution
  reproduces circumradius `2.000000000` for `P₃P₄P₇` to 10 decimal places.

**Degeneracy — exactly 3 collinear triples, 0 concyclic 4-sets, in all 6 solutions.** The
collinearities are exact identities, verified symbolically with sympy:

```
P3 + P4 = 0        →  P8 is the midpoint of P3P4
P3 + P7 = 2·P1     →  P1 is the midpoint of P3P7
P4 + P7 = 2·P2     →  P2 is the midpoint of P4P7
```

That is: **`{P₈, P₁, P₂}` is the medial triangle of `{P₃, P₄, P₇}`.** This dovetails exactly
with the paper's own radius-2 remark — the medial triangle of a circumradius-2 triangle has
circumradius 1, and indeed `P₁P₂P₈` is the circle `C₁`. So the 16-circle set is the
nine-point-circle configuration of a triangle of circumradius 2, and it contains three
collinear triples. **It is not admissible for #831.**

**Caveat.** Harborth's goal is `f(8) ≤ 16`, not a classification of the 16-circle sets. His
case analysis (pp. 164–166) assumes at least three points each lie on 7 unit circles, whereas
the counting bound `(2·7 + 6·6)/3 = 16.67` permits 16 circles with **no** point on 7 circles.
So the paper does **not** establish that every `f(8) = 16` set is of this form, and
**`f_gp(8) < 16` is not proved.**

In any case `n = 8` would need a large drop to pay: `⌈56/16⌉ = ⌈56/15⌉ = ⌈56/14⌉ = 4`; you
need `f_gp(8) ≤ 13` before `h(8) ≥ 5`.

## 2.5 Summary table

| n | f(n) | extremal set (source) | 3 collinear? | 4 concyclic? | admissible set attaining f(n)? |
|---|---|---|---|---|---|
| 4 | 4 | triangle + orthocentre ([Er75h], via E. Szekeres) | no | no | **yes** — 2-param family |
| 5 | 4 | the `n=4` set + any generic point | no | no | **yes** |
| 6 | 8 | `K(2,2,2)` triple system (OEIS SVG panels are symmetric members) | illustrated ones: **yes** (4 collinear pts) | no | **yes** — explicit witness in §2.4 |
| 7 | 12 | OEIS SVG exact coords; system is rigid up to congruence | **yes** (1 triple) | **yes** (1 quadruple) | **no admissible realisation of this system**; other systems not excluded |
| 8 | 16 | Harborth 1985, reconstructed | **yes** (3 triples, medial-triangle structure) | no | not settled (paper does not classify) |

## 2.6 What this does to the bound

`h(n) ≥ ⌈C(n,3)/f_gp(n)⌉`, and `f_gp(n)` is what we now partly know:

| n | C(n,3) | f(n) | f_gp(n) | bound from f_gp | drop needed to gain +1 |
|---|---|---|---|---|---|
| 4 | 4 | 4 | **4** (exact) | 1 | — |
| 5 | 10 | 4 | **4** (exact) | 3 | need ≤ 3 — ruled out |
| 6 | 20 | 8 | **8** (exact) | 3 | need ≤ 6 — ruled out |
| 7 | 35 | 12 | **10 ≤ · ≤ 12** | 3 | **need ≤ 11 — open, and the 12-configuration is degenerate** |
| 8 | 56 | 16 | ≤ 16 | 4 | need ≤ 13 — not established |

**The degeneracy observation pays off at `n = 7` and nowhere else.** Establishing
`f_gp(7) ≤ 11` — i.e. that no 7 points in general position carry 12 unit circles — would give
`h(7) ≥ 4`. That is a finite, checkable question, and it is Erdős's own general-position
modification of `f(n)` from [Er75h].

---

## 3. Open items (honest gaps)

1. **Harborth–Mengersen 1986 unread.** It is the only source that would give the extremal
   configurations for `n = 4..7` *as the authors describe them*, and whether they prove
   uniqueness. Everything in §2.4 for `n ≤ 7` rests on the OEIS illustration plus my own
   verification, not on the paper.
2. **Erdős–Purdy Handbook pp. 847–848 and Brass–Moser–Pach unread.** Whether either states an
   inequality between `f` and `h` is unknown. This is the main residual risk to the §1
   novelty conclusion.
3. **No classification of `f(n) = 12` (n=7) or `f(n) = 16` (n=8) point sets** exists in
   anything I read. Both "`f_gp(7) < 12`" and "`f_gp(8) < 16`" remain conjectural.
4. The `n = 6` and `n = 7` realisation-space results are **numerical** (least-squares to
   `10⁻¹⁰`–`10⁻¹⁶` residuals, Jacobian rank at `10⁻⁷` relative tolerance), not certified. The
   `n = 8` collinearities *are* exact (symbolic).
