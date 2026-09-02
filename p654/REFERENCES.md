# References for the #654 / pinned-distance note

Every item records what was actually read and at what fidelity. Items that could not be
obtained are listed as such rather than paraphrased from memory.

`f(n) = min over admissible X of max_i d_X(x_i)`, the **pinned** count. This is not the
total distinct-distance count; conflating the two is the standing hazard in this area
(see the note at the end).

---

## The problem, in Erdős's own words

* **[Er87b]** P. Erdős, *Some combinatorial and metric problems in geometry*, Colloq. Math.
  Soc. János Bolyai **48** (Siófok 1985), 167–177. **p. 168**, read from the page images of
  <https://www.renyi.hu/~p_erdos/1987-27.pdf>, printed folio confirmed:

  > "Denote by `d(x_i)` the number of distinct distances from `x_i`. Trivially,
  > `d(x_i) >= (n-1)/3` for every `i`. I am sure that there is an absolute constant `c > 0`
  > … so that **(3) `D(n) = max_i d(x_i) > (1+c)n/3`**. Is it true that there is a set
  > `x_1,…,x_n` (in general position) for which **(4) `D(n) < (1-c)n`**? It is rather
  > frustrating that I got nowhere with (3) and (4). Perhaps (3) remains true if we only
  > assume that no four of our points are on a circle or even if no circle whose center is
  > one of the `x_i`'s goes through more than **three** of the other `x_j`'s. It would also
  > be of interest to prove or disprove **(5) `Sum_i d(x_i) > (1+c)n^2/3`**."

  *[VERIFIED AT SOURCE]* Erdős's `D(n) = max_i d(x_i)` is exactly the `M(X)` used here.
  See `PAGE_NOTES.md` for how this compares with the problem page's summary.

* **[ErPa90]** P. Erdős, J. Pach, *Variations on the theme of repeated distances*,
  Combinatorica **10** (1990) 261–269, DOI 10.1007/BF02122780.
  **[NOT OBTAINED]** — paywalled at Springer, absent from the Rényi archive, zbMATH
  returned HTTP 403. The problem page cites p. 267. This gap is material and is flagged
  wherever it bears on a claim.

* **[Er97e]** cited by the problem page as p. 530. **[NOT OBTAINED]**.

* **[Er88]** P. Erdős, *Some old and new problems in combinatorial geometry*, printed folio
  **35**, <https://users.renyi.hu/~p_erdos/1988-32.pdf>. *[VERIFIED AT SOURCE, against the
  page image at 400 dpi as well as the extracted text, because the OCR mangles every
  fraction on this page.]* Question (6):

  > "Let `x_1,...,x_n` be n points in the plane, **no four on a circle** and every circle
  > whose center is one of the `x_i` contains at most two of our points. Clearly for every
  > `x_i` we then have `d(x_i) ≥ (n−1)/2`. Is it true that there is an absolute constant `c`
  > so that **(6) `max_{1≤i≤n} d(x_i) > (1+c)n/2`**? **I offer 25 dollars for a solution.**
  > We need the assumption that no four of our points are on a circle since otherwise the
  > regular polygon gives a counterexample."

  followed by "It should certainly hold if we only assume that no `k` of our points are on a
  circle where `k` is independent of `n` … We also assume that not too many of our points
  are on a line."

  Three things this settles. The **at-most-two** hypothesis is attached to **`(1+c)n/2`**,
  not to `(1-o(1))n` and not to `(1+c)n/3`. Erdős's quantity is the **pinned** maximum. And
  the "no four on a circle" hypothesis, absent from the #655 page, is present here together
  with Erdős's reason for it: the regular polygon. See `PAGE_NOTES.md`.

  The same page also carries "Pach just told me that `h(2^n) ≤ 3^n`. The projection of the
  n-dimensional cube shows this. Perhaps `h(n)/n → ∞`, but as far as I know this is still
  open." — a primary source for #98's upper bound and a statement of #98 itself.

## The quantity, named and declared open

* **Sheffer**, *Distinct Distances: Open Problems and Current Bounds*, arXiv:1406.1949.
  **The version matters.** In **v2 (19 May 2015), p. 6**:

  > "Erdős [20] also suggested to study the maximum number `D̂gen(n)` satisfying that for
  > any set `P` of `n` points in general position, there exists a point `p ∈ P` such that
  > `{p}×P` determines at least `D̂gen(n)` distinct distances. … Thus, a trivial lower bound
  > is `D̂gen(n) ≥ ⌈(n−1)/3⌉`. **No non-trivial bound is known for `D̂gen(n)` (neither a
  > lower nor an upper bound)**, and when discussing the problem, Erdős [20] wrote 'It is
  > rather frustrating that I got nowhere with…'."

  and it is his **Problem 10** there. *[VERIFIED, v1/v2/v3 all downloaded and text-extracted]*

  The same paragraph is **Problem 12 in v1**. **v3 (2 July 2018), the current arXiv
  version, removes the paragraph and the problem from the body text**: v3's §3 runs
  Problem 7 (`D̂conv`), 8 (`Dgen`), 9 (`Dpara`), and its Problem 10 is about `D_d(n)` in
  higher dimensions; "frustrating" occurs zero times in v3. A `D̂gen(n)` row survives in
  v3's Table 1. **Cite v2 explicitly**, or a reader checking the current version will not
  find the problem.

## The disproof of the strongest form

* **[Fe26]** Feng, Trinh, Bingham et al., *Semi-Autonomous Mathematics Discovery with
  Gemini: A Case Study on the Erdős Problems*, arXiv:2601.22401, **§3.1, pp. 15–17**.
  Construction: `n = 4m`, `K = {10,…,m+9}`, `P = {(0, ±3^k)}` on the y-axis and
  `Q = {(±2^j, 0)}` on the x-axis; Theorem 3 gives `|D(u)| < (3/4)n` for every `u`.
  **Defined only for `n >= 40`**, so it says nothing about small `n`. All points lie on two
  lines, so it does not touch the general-position version; the authors classify it as a
  *partial* solution, and note that Aletheia's attempt at the extra hypothesis "was
  incorrect, so we omit that part". "Aletheia" is a Google DeepMind system (Gemini Deep
  Think). *[VERIFIED AT SOURCE]*

## Novelty: no published small values found

* **OEIS**: zero results for `"distinct distances" "general position"`, `… concyclic`,
  `… cocircular`, `"no four concyclic"`, `"no four points on a circle"`,
  `"distinct distances" pinned`, `crescent configuration`. `"no four on a circle"` gives one
  hit, **A096873** (minimum diameter of an *integral* point set), unrelated. All **31**
  full-text `"distinct distances"` sequences were enumerated; none is a pinned per-point
  function. **A186704** (`0,1,1,2,2,3,3,4,4,5,5,5,6`) and **A131628** are the *unrestricted
  total-count* versions. The #654 page's own OEIS field reads "Possible".
* **Brass–Moser–Pach**, *Research Problems in Discrete Geometry*, Springer 2005,
  **§5.5, pp. 214–216** (section range confirmed against the publisher's table of
  contents). Asymptotic only; probes for `"Table"`, `"for n ="`, `"n = 4"`, `"n = 5"`,
  `"exact value"`, `"small values"`, `"is known only"` returned nothing on pp. 213–217,
  while hitting freely elsewhere in the book. *[SNIPPET VIEW ONLY — Springer and
  ScienceDirect block automated access, so absence of a table is strong evidence, not
  proof.]*
* **Erdős–Fishburn**, *Distinct distances in finite planar sets*, Discrete Math. **175**
  (1997) 97–132: a **different function**. Per zbMATH review **Zbl 0894.52007** (reviewer
  Erhard Quaisser): it studies `Σ_n = min{Σ f_i}` where `f_i` is the number of distinct
  distances from point `i`, over **unrestricted** planar sets, giving
  `(Σ_3..Σ_8) = (3,6,10,15,19,24)`. Different in *both* the aggregation (sum, not max) and
  the admissible class (unrestricted, not no-four-concyclic). **[FULL TEXT NOT OBTAINED —
  ScienceDirect 403; only the review was read.]**
* **38 papers citing Sheffer's survey** were checked; none computes exact small values.
  Crescent-configuration papers (arXiv:1509.07220, 1610.07836, 1909.08769) use the same
  general-position setting but measure something else and contain no pinned counts.
  Dumitrescu 2008/2020 and Tao 2026 concern total counts.

**Confidence that `f(3..6) = 1,2,3,3` is unpublished: ~90%**, resting on searches failing
to find them, with the two access gaps above as the main residual risk.

## The hazard: pinned versus total

Brass–Moser–Pach state Erdős's `(1/3+c)n` question in terms of `v_γ(n)`, the minimum
**total** number of distinct distances (p. 214: "We do not know any argument showing that
there exists `ε > 0` such that `v_no-4-circ(n) ≥ (1/3 + ε)n`"). The problem page and
[Er87b] state it for the **pinned** maximum `max_i d(x_i)`. The two coincide at the trivial
bound, because `⌈(n−1)/3⌉` for the total count is derived from the pinned argument, which is
presumably how they came to be run together. Any "no non-trivial bound is known" claim
needs to say which function it means.

## Not the same problem: the convex case, and `../p982` in this repository

`../p982` in this repository studies **the pinned count under CONVEX position**, Erdős
#982, and was **shelved for lack of novelty**: its `n <= 7` certification already follows
from Moser 1952, Erdős-Fishburn 1994 and Dumitrescu 2006. Since that is the obvious place
to suspect an overlap, the distinction is worth stating.

The hypothesis classes are **incomparable**, so no bound transfers in either direction:

* A convex polygon need not satisfy no-four-concyclic; the regular `n`-gon is convex and
  has *every* four of its vertices on a circle. This is exactly why the regular `n`-gon
  disproves #655 as stated but is inadmissible here.
* A set with no four concyclic need not be convex; nothing in the hypothesis constrains the
  convex hull.

So Moser's `⌊(n+2)/3⌋`, Erdős-Fishburn's run-length bound and Dumitrescu's
`⌈(13n-6)/36⌉` are all statements about `M_C(n)` and say nothing about `f_N4(n)` or
`f_G(n)`. The convex row and the general-position row of the landscape table are separate
open problems; the convex one has non-trivial published bounds and the general-position one,
per Sheffer, has none.

Numerically the two do not even agree on the values: Moser gives `M_C(7) >= 3` while the
trivial bound here is only `⌈6/3⌉ = 2`, and the conjectured convex answer `⌊n/2⌋` is 3 at
`n = 6, 7` where we prove `f(6) = 3` and `f(7) >= 3` by a completely different route.
