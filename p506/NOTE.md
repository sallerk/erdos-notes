# Erdos #506 (minimum number of distinct circles determined by n points)

Full note. The forum comment is a summary of this page.

A small clarification on the arithmetic of the eight-point, seventeen-circle configuration, with an independent check of both witnesses.

mzn's comment of 18 August gives an eight-point set determining $17$ circles over $\mathbb{Q}(\sqrt{15})$, namely $(\pm u, -1)$, $(\pm u/3, -1)$, $(\pm u/2, 3/2)$, $(\pm u/4, 1/4)$ with $u = \sqrt{15}$, and observes that within that parametrisation $u^2 = 15$ is forced, since a similarity would require $4a^2+b^2 = 3q^2$, impossible by descent mod $3$.

Liyan Wang's paper (arXiv:2608.19844, section 7.3) gives eight points with rational coordinates also determining exactly $17$ circles. The two turn out to realise the same abstract configuration without being similar, which seems worth recording, since it says the arithmetic obstruction is a property of the parametrisation rather than of the configuration type.

I checked all of this in exact arithmetic, over $\mathbb{Q}$ for Wang's set and over $\mathbb{Q}(\sqrt{15})$ for mzn's. A circle or line is the zero set of $A(x^2+y^2) + Bx + Cy + D = 0$, and three points determine $(A,B,C,D)$ up to scale as the null vector of the $3 \times 4$ matrix whose rows are $x^2+y^2$, $x$, $y$, $1$; then $A = 0$ is exactly collinearity, and two triples are cocircular exactly when their normalised vectors agree. No floating point enters.

Both sets give exactly $17$ circles and $3$ lines, with the block profile mzn reports (twelve blocks of size $4$ and eight of size $3$, covering all $56$ triples once). Numbering mzn's points in the order listed above, mzn's lines are $\{0,1,2,3\}$, $\{0,5,6\}$, $\{1,4,7\}$; numbering Wang's as in his section 7.3, his are $\{0,1,2,3\}$, $\{0,4,6\}$, $\{3,5,7\}$.

The designs are isomorphic. Brute force over all $8!$ relabellings finds exactly four carrying Wang's blocks onto mzn's while also sending lines to lines and circles to circles, so the configuration has an automorphism group of order four. One of them sends Wang's point $i$ to mzn's point $p_i$ with $(p_0,\dots,p_7) = (0,2,3,1,5,7,6,4)$.

The point sets are not similar. Under each of those four relabellings the ratio of corresponding squared distances takes ten distinct values, never one. So these are two non-similar realisations of the same incidence design, and the design is not rigid.

Taken together: $u^2 = 15$ is forced within mzn's family, exactly as their descent shows, but the seventeen-circle configuration type itself carries no such obstruction, since Wang realises it over $\mathbb{Q}$. Nothing here bears on whether $m(8) = 17$; I checked the two witnesses and the relation between them, and no lower bound.

Verification script and artifact:
https://github.com/sallerk/erdos-notes/blob/main/p506/NOTE.md

Disclosure: the computations and the drafting of this comment were done with AI assistance. The verification script is short and self-contained and can be re-run by anyone.

## How to re-run

    python verify_iso.py

Prints the circle counts for both witnesses, the four designation-preserving
relabellings, and the similarity test. Needs only sympy. Exact throughout.
