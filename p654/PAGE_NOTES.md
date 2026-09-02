# Notes on the #654 and #655 problem pages — DRAFT, NOT SENT

Intended for the erdosproblems.com maintainers. Every quotation below was read at source;
the one item that could not be obtained is flagged as such rather than guessed at.

The key source is **P. Erdős, *Some old and new problems in combinatorial geometry*,
printed folio 35**, read from <https://users.renyi.hu/~p_erdos/1988-32.pdf>. Quotations
were checked against the page image at 400 dpi, not only against extracted text, because
the OCR mangles every fraction on that page (it renders `(1+c)n/2` as `(1+c)2`).

---

## 1. #655: the missing hypothesis is not a guess, it is in the source

The [#655](https://www.erdosproblems.com/655) page currently states:

> Let `x_1,…,x_n ∈ R^2` be such that no circle whose centre is one of the `x_i` contains
> three other points. Are there at least `(1+c)n/2` distinct distances determined between
> the `x_i`, for some constant `c>0` and all `n` sufficiently large?

and remarks that Zach Hunter disproved it with equally spaced points on a circle, adding:

> "In the spirit of related conjectures of Erdős and others, **presumably** some kind of
> assumption that the points are in general position (e.g. no three on a line and no four
> on a circle) was intended."

**That presumption is correct, and can be sourced.** Erdős 1988, p. 35, question (6),
verbatim:

> "Here is one final problem of this type: Let `x_1,...,x_n` be n points in the plane,
> **no four on a circle** and every circle whose center is one of the `x_i` contains at
> most two of our points. Clearly for every `x_i` we then have `d(x_i) ≥ (n−1)/2`.
> Is it true that there is an absolute constant `c` so that
>
> **(6)  `max_{1≤i≤n} d(x_i) > (1+c) n/2` ?**
>
> **I offer 25 dollars for a solution.**
>
> We need the assumption that no four of our points are on a circle since otherwise
> **the regular polygon gives a counterexample.**"

Three things follow.

1. **The no-four-on-a-circle hypothesis is part of Erdős's statement**, and is missing from
   the page.
2. **Erdős anticipated the exact counterexample.** The sentence "otherwise the regular
   polygon gives a counterexample" names precisely the configuration Hunter observed. The
   disproof is a disproof of the statement with the hypothesis dropped, not of Erdős's
   question.
3. **The page states the total-distance version; Erdős's (6) is the pinned one.** The page
   asks for `(1+c)n/2` distinct distances "determined between the `x_i`", i.e. in the whole
   set; Erdős asks for `max_i d(x_i) > (1+c)n/2`, the maximum over points of the count from
   a single point. Since `max_i d(x_i) ≤ D(X)`, Erdős's is the stronger claim. The page's
   own next sentence ("this assumption implies that there are at least `(n−1)/2` distinct
   distances determined by **every point**") is the pinned trivial bound, so the page
   already carries Erdős's pinned reading in its commentary while its headline statement is
   the total one.

The page cites only `[Er97e]`. If the 1988 text above is the origin, it is worth citing,
not least because of the prize.

This bears on the open ambiguity flag: the database records #655 as AMBIGUOUS and the
maintainer declined to pick an interpretation. The 1988 source supplies one, in Erdős's own
words, together with his reason for it.

## 2. #654: the weakened hypothesis and its bound

The [#654](https://www.erdosproblems.com/654) page states:

> "**They suggest the lower bound `(1-o(1))n` is true under the assumption that any circle
> around a point `x_i` contains at most 2 other `x_j`.**"

with citations `[Er87b,p.168] [ErPa90,p.267] [Er97e,p.530]`. Against the two sources that
could be read:

* **[Er87b] p. 168** (<https://www.renyi.hu/~p_erdos/1987-27.pdf>, folio confirmed) offers a
  weakened hypothesis, but it says **three**, not two, and attaches it to **(3)**, the
  `n/3`-scale claim:

  > "I am sure that there is an absolute constant `c > 0` … so that **(3) `D(n) = max_i
  > d(x_i) > (1 + c)n/3`**. Is it true that there is a set `x_1,…,x_n` (in general
  > position) for which **(4) `D(n) < (1 − c)n`**? … Perhaps (3) remains true if we only
  > assume that no four of our points are on a circle or even if no circle whose center is
  > one of the `x_i`'s goes through more than **three** of the other `x_j`'s."

* **Erdős 1988 p. 35** has the **at-most-two** hypothesis, but attaches it to
  **`(1+c)n/2`**, as quoted in section 1.

So the at-most-two condition is real and the `(1-o(1))n` target is real, but **no source
read here joins them**: 1987 pairs "three" with `(1+c)n/3`, and 1988 pairs "two" with
`(1+c)n/2`. The page's sentence appears to merge two distinct questions.

A second point on the same sentence: **[Er87b]'s (4) asks whether a set with
`D(n) < (1−c)n` EXISTS.** Erdős is probing for a counterexample there, not conjecturing
`(1−o(1))n` as a lower bound. (The page's headline `(1-o(1))n` question is separately
sourced to `[Er97e]` and described there as "perhaps too optimistic", which is consistent.)

**The gap I could not close.** `[ErPa90, p.267]` is P. Erdős and J. Pach, *Variations on
the theme of repeated distances*, Combinatorica **10** (1990) 261–269,
DOI 10.1007/BF02122780: paywalled at Springer, absent from the Rényi archive, and zbMATH
returned HTTP 403. `[Er97e, p.530]` was likewise not obtained. **If either states the
condition with "two" alongside `(1-o(1))n`, the page is properly sourced and only the
attribution to [Er87b] is loose.** I cannot distinguish those cases; someone with access
can settle it by reading p. 267.

Finally, note that Erdős's 1988 discussion of (6) adds a caveat the page does not carry:
after suggesting (6) should hold under the weaker "no `k` on a circle, `k` independent of
`n`", he writes "**We also assume that not too many of our points are on a line.**"

## 3. #98: a primary source for the `n^{log_2 3}` bound

The [#98](https://www.erdosproblems.com/98) page attributes an `n^{log_2 3}` upper bound to
Pach without a reference. Erdős 1988, p. 35, immediately after question (6), reads (checked
against the page image, where the exponents are clear and the relation is `≤`):

> "Let `S` be a set of `n` points in the plane no three on a line, no four on a circle.
> Denote by `h(n)` the largest integer for which such a set determines at least `h(n)`
> distinct distances. **Pach just told me that `h(2^n) ≤ 3^n`. The projection of the
> n-dimensional cube shows this.** Perhaps `h(n)/n → ∞`, but as far as I know this is
> still open."

`h(2^n) ≤ 3^n` is exactly `h(N) ≤ N^{log_2 3}`, and the named construction is the one
written up as Theorem 1 of Erdős, Hickerson and Pach, *A problem of Leo Moser about repeated
distances on the sphere*, Amer. Math. Monthly **96** (1989) 569–575, **p. 571**, whose proof
begins from the vertices of a unit cube in `R^k`. So the trail runs from an attributed 1988
remark to the 1989 write-up.

The same sentence is also **Erdős stating #98 itself** ("Perhaps `h(n)/n → ∞`, but as far
as I know this is still open"), which may be worth adding to that page's source list.

---

*Prepared with AI assistance. The [Er87b] and 1988 quotations were read from page images of
the Rényi archive scans; `[ErPa90]` and `[Er97e]` were not obtainable and are flagged as
such above rather than guessed at.*
