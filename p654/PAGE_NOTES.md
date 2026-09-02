# Notes on the #654 problem page — DRAFT, NOT SENT

Intended for the erdosproblems.com maintainers. Everything below is a *please check*, not
an assertion that the page is wrong: one of the three cited sources could not be obtained,
and it is exactly the one that might support the current wording.

---

## The sentence in question

The page for [#654](https://www.erdosproblems.com/654) currently reads:

> In [Er87b] and [ErPa90] Erdős and Pach ask this under the additional assumption that
> there are no three points on a line (so that the points are in general position),
> although they only ask the weaker question whether there is a lower bound of the shape
> `(1/3+c)n` for some constant `c>0`. **They suggest the lower bound `(1-o(1))n` is true
> under the assumption that any circle around a point `x_i` contains at most 2 other
> `x_j`.**

The citations attached to the problem are `[Er87b,p.168] [ErPa90,p.267] [Er97e,p.530]`.

## What [Er87b] p.168 actually says

P. Erdős, *Some combinatorial and metric problems in geometry*, Colloq. Math. Soc. János
Bolyai **48** (1987) 167–177, read from page images at
<https://www.renyi.hu/~p_erdos/1987-27.pdf>, printed folio 168 confirmed:

> "A related problem states as follows. Let `x_1,...,x_n` be in general position. Denote by
> `d(x_i)` the number of distinct distances from `x_i`. Trivially, `d(x_i) >= (n-1)/3` for
> every `i`. I am sure that there is an absolute constant `c > 0` ... so that
>
> **(3) `D(n) = max_i d(x_i) > (1 + c)n/3`.**
>
> Is it true that there is a set `x_1,...,x_n` (in general position) for which
>
> **(4) `D(n) < (1 - c)n` ?**
>
> It is rather frustrating that I got nowhere with (3) and (4). Perhaps (3) remains true if
> we only assume that no four of our points are on a circle or even if no circle whose
> center is one of the `x_i`'s goes through more than **three** of the other `x_j`'s. It
> would also be of interest to prove or disprove
>
> **(5) `Sum_i d(x_i) > (1 + c)n^2/3`.**"

Three points of difference, against this source only:

1. **Erdős writes "three", not "two"**: *"no circle whose center is one of the `x_i`'s goes
   through more than three of the other `x_j`'s."*
2. **The weakened hypothesis is attached to (3), not to `(1-o(1))n`.** In Erdős's text the
   sentence beginning "Perhaps (3) remains true..." offers the weaker hypotheses as
   possible settings for statement **(3)**, which is the `(1+c)n/3`-scale claim. The page
   attaches it to the much stronger `(1-o(1))n`.
3. **Direction.** Erdős's **(4)** asks whether a set with `D(n) < (1-c)n` *exists*. He is
   probing for a counterexample, not conjecturing `(1-o(1))n` as a lower bound. The page's
   own headline question, "is it true that `f(n) > (1-o(1))n`?", is sourced to [Er97e] and
   is separately described there as "perhaps too optimistic", which is consistent.

## The gap I could not close, and why it matters

**`[ErPa90, p.267]` could not be obtained.** It is P. Erdős and J. Pach, *Variations on the
theme of repeated distances*, Combinatorica **10** (1990) 261–269
(DOI 10.1007/BF02122780). It is paywalled at Springer, absent from the Rényi archive, and
zbMATH refused the request. `[Er97e, p.530]` was likewise not obtained.

This matters directly: **if [ErPa90] p.267 states the condition with "two", then the page's
sentence is properly sourced there and only the attribution to [Er87b] is loose.** I cannot
distinguish those cases. Someone with Springer access can settle it by reading p.267.

## A source that does say "two"

There is at least one Erdős source with the at-most-two form: P. Erdős, in the 1988 SIAM
Clemson problem collection, **p. 35, question (6)**. That version carries a **$25 prize**
and an additional caveat (a restriction on how many points may lie on a line) which the
current page does not mention. So a plausible reading is that the page has merged two
distinct sources into one sentence, in which case the fix is to split the citation rather
than to change the number.

## Separately: a citation trail for #98

Not about this page, but found alongside and possibly useful. The
[#98](https://www.erdosproblems.com/98) page attributes an `n^{log_2 3}` upper bound to
Pach without a reference. The 1988 SIAM Clemson collection, **p. 35**, records:

> "Pach just told me that `h(2^n) <= 3^n`. The projection of the n-dimensional cube shows
> this."

`h(2^n) <= 3^n` is exactly `h(N) <= N^{log_2 3}`, and the named construction is the one
written up as Theorem 1 of Erdős, Hickerson and Pach, *A problem of Leo Moser about repeated
distances on the sphere*, Amer. Math. Monthly **96** (1989) 569–575, **p. 571**, whose proof
begins by taking the vertices of a unit cube in `R^k`. That completes the trail from an
attributed 1988 remark to the 1989 write-up.

---

*Prepared with AI assistance. The [Er87b] quotation was read from the page images of the
Rényi archive scan; the other two cited sources were not obtainable and are flagged as such
above rather than guessed at.*
