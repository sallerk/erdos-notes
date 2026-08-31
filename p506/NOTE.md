# Erdos #506 (minimum number of distinct circles determined by n points)

Problem page: https://www.erdosproblems.com/506

Full note. The forum comment is a summary of this page. Bibliography with provenance
is in `REFERENCES.md`; step-by-step reproduction, with the output each command
actually printed, is in `REPRODUCE.md`.

## What this note is, after the novelty check

An earlier version of this note led with the relationship between two eight-point
witnesses. That was the wrong emphasis, and the novelty check is what found it.

The forum thread (mzn, 01:48 on 18 Aug 2026) reports m(5) = 5, m(6) = 8, m(7) = 11,
m(8) = 17 and ends: "I did not find any of these values in the literature, and the
search was not exhaustive... If any of this is known, I would be glad to be told."

They are known. Liyan Wang, "Circles determined by planar point sets", arXiv:2608.19844
(20 Aug 2026), **Theorem 1.2**, verbatim:

> "For every n>=4, one has c(n) = F(n), with precisely three exceptions:
> c(6) = 8 = F(6)-1, c(7) = 11 = F(7)-2, c(8) = 17 = F(8)-2."

where F(n) = 1 + C(n-1,2) - floor((n-1)/2) is the corrected Purdy-Smith value. Those
three exceptional orders are exactly the thread's m(6), m(7), m(8). Wang further gives
c(9) = F(9) = 25, settling the n = 9 case the thread leaves open, and treats the
no-three-collinear variant separately, finding a single exceptional order there.

The timing is worth stating plainly so nobody looks careless: the forum comment is
dated 18 Aug 2026 and Wang reached arXiv on 20 Aug 2026. The values could not have
been found by searching at the time the comment was written.

So the contribution of this note is the pointer, plus the following observation, and
**no new value of c(n)**.

## The two eight-point witnesses, and why they do not conflict

mzn's comment gives an eight-point set determining $17$ circles over
$\mathbb{Q}(\sqrt{15})$, namely $(\pm u, -1)$, $(\pm u/3, -1)$, $(\pm u/2, 3/2)$,
$(\pm u/4, 1/4)$ with $u = \sqrt{15}$, and observes that within that parametrisation
$u^2 = 15$ is forced, since a similarity would require $4a^2+b^2 = 3q^2$, impossible by
descent mod $3$.

Wang's section 7.3 gives eight points with **rational** coordinates also determining
exactly $17$ circles. At first sight these conflict. They do not: the two realise the
same abstract configuration without being similar, so the arithmetic obstruction is a
property of mzn's parametrisation, not of the configuration type.

Checked in exact arithmetic, over $\mathbb{Q}$ for Wang's set and over
$\mathbb{Q}(\sqrt{15})$ for mzn's, by two independent code paths. `verify_iso.py`
identifies a circle as the null vector of the $3 \times 4$ matrix with rows
$x^2+y^2$, $x$, $y$, $1$, so that $A = 0$ is exactly collinearity. `audit.py` instead
solves for the centre and squared radius by Cramer's rule and keys circles on
$(c_x, c_y, r^2)$. The two agree. No floating point enters either.

Both sets give exactly $17$ circles and $3$ lines, with the block profile mzn reports
(twelve blocks of size $4$ and eight of size $3$, covering all $56$ triples once).
Numbering mzn's points in the order listed above, mzn's lines are $\{0,1,2,3\}$,
$\{0,5,6\}$, $\{1,4,7\}$; numbering Wang's as in his section 7.3, his are
$\{0,1,2,3\}$, $\{0,4,6\}$, $\{3,5,7\}$.

The designs are isomorphic. Brute force over all $8!$ relabellings finds exactly four
carrying Wang's blocks onto mzn's while also sending lines to lines and circles to
circles, so the configuration has an automorphism group of order four. One of them
sends Wang's point $i$ to mzn's point $p_i$ with $(p_0,\dots,p_7) = (0,2,3,1,5,7,6,4)$.

The point sets are not similar. Under each of those four relabellings the ratio of
corresponding squared distances takes ten distinct values, never one. So these are two
non-similar realisations of the same incidence design, and the design is not rigid.

## What is verified and what is not

Verified here in exact arithmetic: both witnesses determine 17 circles and 3 lines;
the block profiles; the four designation-preserving isomorphisms; the ten distinct
ratios establishing non-similarity. Two independent implementations agree.

Not verified here: any lower bound. Nothing in this note bears on whether c(8) = 17 is
minimal; that is Wang's theorem, and I have not checked his proof. Wang's coordinates
and his list of 17 circles were transcribed from arXiv:2608.19844 section 7.3 and
re-derived from the coordinates, but the surrounding argument is taken on trust and
marked as such in `REFERENCES.md`.

An earlier draft of the forum comment asserted that mzn's "this one cannot be
rationalized" was false. That was wrong and was withdrawn before posting: mzn's claim
is about similarity within their family, and the check above confirms the two sets are
not similar, so their descent stands.

Disclosure: the computations and the drafting of this note were done with AI
assistance.

## Files in this directory

Documentation: `REPRODUCE.md`, `REFERENCES.md`, `RESULTS.md`.

Verification, two independent paths: `audit.py` (standalone re-derivation of every
checkable claim, including the novelty check against Wang's Theorem 1.2) and
`verify_iso.py` (the earlier verifier, different circle-identification method).

Search and support: `circles.py`, `designs.py`, `gridsearch.py`, `anneal.py`,
and the artifact `artifact_iso_n8.json`.
