# References for the #98 / D_gen note

Every quotation below was read at its source. Page numbers are the printed folios, not
PDF page indices. Items corrected during the full audit are marked **[CORRECTED]** with
what was previously wrong; the errors are catalogued in `CORRECTIONS.md`.

`D_gen(n)` = the minimum number of distinct distances among `n` points in the plane with
no three collinear and no four cocircular. The problem page writes `h(n)`; Sheffer's
survey writes `D_gen(n)`; **Erdős–Hickerson–Pach write `G(n)` for the same function**.

---

## The problem, in Erdős's own words

* **[Er83c]** P. Erdős, *Combinatorial problems in geometry*, Math. Chronicle **12**
  (1983) 35–54. Added note dated 19 August 1982, **p. 54**, verbatim:

  > "[Added 19 August, 1982. Let h(n) be the **largest** integer so that if n points are
  > given in the plane no three on a line and no four on a circle then they determine at
  > least h(n) distinct distances. Determine or estimate h(n) as well as you can.]"

  https://www.renyi.hu/~p_erdos/1983-03.pdf *[VERIFIED AT SOURCE]*

  The word **largest** is what makes `h(n)` the minimum over configurations, which is the
  object computed here. This is the check that the right problem is being solved.

* **[Er75f]** P. Erdős, Ann. Mat. Pura Appl. **103** (1975), **p. 101**, verbatim:

  > "Assume that no three x_i are on a line and no four on a circle. What can be said
  > about D_2(x_1, …, x_n). Is it true that (9) lim_{n=∞} D_2(x_1, …, x_n)/n = ∞ ?"

  https://www.renyi.hu/~p_erdos/1975-25.pdf *[VERIFIED AT SOURCE]*

  **[CORRECTED]** An earlier draft attributed a nearby remark to "HARBORTH and RUZSA" and
  quoted it as `D > 6`. The text reads **HAMBURGER** and RUZSA, and the bound is
  `D_2(x_1,…,x_6) ⩾ 6`. More importantly it sits inside the **isosceles-free** variant on
  that page, not the no-three-collinear/no-four-cocircular function, so it is **not** a
  published small value of `h(n)` and does not bear on the novelty question.

* **[Er87b]** P. Erdős, *Some combinatorial and metric problems in geometry*, Colloq.
  Math. Soc. J. Bolyai **48** (1987) 167–177.

  **p. 167:** "I have no example to show that (1) f(n)/n² → 0 and, on the other hand, I
  cannot prove (2) f(n)/n → ∞."

  **p. 168** **[CORRECTED — previously cited as p. 167]:** "f(n) ≥ n for n > n₀ would of
  course show that my conjecture is true." The conjecture is the crescent-configuration
  problem stated on p. 167, i.e. Erdős #217.

  https://www.renyi.hu/~p_erdos/1987-27.pdf *[VERIFIED AT SOURCE]*

## The bounds

* **Lower bound, Szemerédi.** Observed by Szemerédi, unpublished. Stated in
  **Erdős–Hickerson–Pach 1989, p. 571**: "Szemerédi [Sz] observed that G(n) ⩾ (n−1)/3."
  Their reference list gives "[Sz] E. Szemerédi (unpublished)". It requires only
  *no three collinear*. *[VERIFIED AT SOURCE]*

  **A form discrepancy, recorded rather than smoothed over.** Sheffer (arXiv:1406.1949,
  §3) and the Handbook (3rd ed., ch. 1, Table 1.2.4) both state `⌈(n−1)/3⌉`. The primary
  [Er75f] p. 101 prints `max_i d_2(x_i) ⩾ [n/3]`, i.e. `⌊n/3⌋`. These differ at
  `n ≡ 2 mod 3` (at n = 5: 2 versus 1). Everything here compares against the **stronger**
  `⌈(n−1)/3⌉`, so the "best known lower bound" window is conservative either way.

* **Szemerédi's conjecture, `G(n) ≥ (n−1)/2`.** **[NEW — missed until the audit]**
  Erdős–Hickerson–Pach 1989, **p. 571**, same parenthesis:

  > "Szemerédi [Sz] observed that G(n) ⩾ (n−1)/3. (In fact, he conjectures
  > G(n) ⩾ (n−1)/2, which would generalize a theorem of Altman [A].)"

  *[VERIFIED AT SOURCE]* This is a more relevant benchmark than `(n−1)/3`. Every computed
  value satisfies it: equality at n = 3, and roughly double it from n = 4 on.

* **Upper bound `n·2^{O(√log n)}`.** P. Erdős, Z. Füredi, J. Pach, I. Ruzsa, *The grid
  revisited*, Discrete Math. **111** (1993) 189–196, DOI 10.1016/0012-365X(93)90155-M.
  **Theorem 3.1, p. 192**: "There exists a constant c such that, for any natural number n,
  one can find an n-element point set P in the plane in general position such that …
  g(P) ⩽ n·2^{c√log n}." Construction (pp. 192–193): a lattice in `d ≈ √log₂ n`
  dimensions, points on a sphere about the origin, orthogonal projection to a generic
  2-plane chosen injective and giving general position.
  https://www.renyi.hu/~furedi/PUBS3/furedi_124_erdos_pach_ruzsa_grid.pdf
  *[VERIFIED AT SOURCE]*

* **The `n^{log₂3}` upper bound.** **[CORRECTED — previously recorded as an uncited
  claim that could not be located]** It is P. Erdős, D. Hickerson, J. Pach, *A problem of
  Leo Moser about repeated distances on the sphere*, Amer. Math. Monthly **96** (1989)
  569–575, **p. 571**:

  > "THEOREM 1. For every natural number n, G(n) < (3/2)n^{log3/log2}"

  with, on the same page, "let G(n) = min g(P), where the minimum is taken over all
  n-element point sets P in the plane in general position", general position defined
  p. 570 as "no 3 of them on a straight line and no 4 on a circle". The abstract adds:
  "We also construct a set of n points in the plane in general position (no 3 on a line,
  no 4 on a circle) such that they determine fewer than const · n^{log3/log2} distinct
  distances, which settles a problem of Erdős."
  https://www.renyi.hu/~p_erdos/1989-02.pdf *[VERIFIED AT SOURCE]*

  So the problem page's attribution to "Pach" alone is **incomplete, not absent**. An
  earlier draft of the comment reported this as a citation gap; that was wrong and has
  been removed.

* **Brass, Moser, Pach**, *Research Problems in Discrete Geometry*, Springer 2005,
  **§5.5 "Repeated Distances in Point Sets in General Position", pp. 214–216** (not
  p. 200, which carries the *unrestricted* Erdős–Fishburn table). p. 214 contains
  "u_no-4-circ(n) ⩽ 3n" and the remark "However, the latter inequality is **almost
  certainly not sharp**". p. 215, verbatim:

  > "**Problem 2 (Erdős)** Find the best constant c such that n points in the plane, no
  > four on a circle, determine at least (c + o(1))n distinct distances."

  *[VERIFIED AT SOURCE, snippet level]* via Google Books search-within-volume (volume
  WehCspo0Qa0C). The companion bound `v_no-4-circ(n) ⩾ n/3` on p. 214 is consistent but
  Google's OCR mangles the fraction, so it is verified only at OCR quality. Note the
  printed problem imposes only *no four on a circle*.

* **Nivasch, Pach, Pinchasi, Zerbib**, arXiv:1207.1266. p. 2: "he established the
  inequality f_conv(n) ⩾ f_gen(n) ⩾ (n−1)/3"; their "general position" means no three
  collinear. p. 2: "Dumitrescu [Du06] showed that, if P is in convex position, then
  Z(P) ⩽ n²(1−1/12)". Theorem 9, p. 6, improves this to `n²(1 − 1/11.981)`.
  **[CORRECTED]** The isosceles-triangle maximisation is their **Problem 1** (p. 3), not
  Problem 2, and it asks for "convex (or in general) position". *[VERIFIED AT SOURCE]*

## Novelty: no published small values found

* **Brass–Moser–Pach §5.5**: asymptotic only, no table.
* **Erdős–Fishburn**, *Distinct distances in finite planar sets*, Discrete Math. **175**
  (1997) 97–132: a **different function**. Per zbMATH review Zbl 0894.52007, it studies
  `Σ_n = min Σ f_i` where `f_i` counts distances *from point i*, over **unrestricted**
  planar sets, giving `(Σ₃..Σ₈) = (3,6,10,15,19,24)`. Not the total distinct-distance
  count, no general-position hypothesis. The PDF itself could not be obtained
  (ScienceDirect 403, OpenAlex `oa_status: closed`).
* **Sheffer** arXiv:1406.1949 Table 1; **Handbook** 3rd ed. ch. 1 Table 1.2.4
  ("in general position": `Ω(n)` / `O(n^{1+c/log log n})`): asymptotic only.
* **Dumitrescu**, Period. Math. Hungar. **57** (2008) 165–176: asymptotic constructions.
* **Crescent-configuration papers** (arXiv:1509.07220, 1610.07836, 1909.08769): same
  general-position setting but they *fix* the count at `n−1` and never ask for the
  minimum. A. Liu, New Zealand J. Math. **15** (1986) 29–33, likewise.
* **OEIS**: full-text `cocircular` → 0; `"no four on a circle"` → 1 hit (A096873, a
  different problem); A186704 and A131628 are the unrestricted versions. The problem page
  lists OEIS status "Possible", i.e. none attached.
* **The single forum comment** (mysticflounder, 07 Aug 2026) and its linked gist, read in
  full (21,659 bytes): the gist contains **no** small values — no `h(3)`–`h(8)`, no
  `n−2`, no table. Its `n = 7,9,11,13,15` references are determinant ranks in an unrelated
  argument. Its only unconditional lower-bound claim is `(n−1)/3`.

**Confidence the small values are unpublished: ~90%**, resting on searches failing to find
them. **Still unchecked:** the four 1990s Erdős surveys the Rényi archive does not carry
([Er90], [Er92b], [Er94b], [Er97e]).
