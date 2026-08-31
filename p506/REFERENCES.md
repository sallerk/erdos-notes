# References for the #506 note

* **mzn**, comment of 18 Aug 2026 on https://www.erdosproblems.com/forum/thread/506.
  Source of the Q(sqrt 15) eight-point witness and of the quoted descent argument.
  *[VERIFIED AT SOURCE: thread fetched and the passage read verbatim 2026-08-31]*

* **Liyan Wang**, "Circles determined by planar point sets", arXiv:2608.19844v1
  [math.CO], **posted 20 Aug 2026** (paper internally dated 2026.08.18).

  **This paper solves the problem, and that is the single most important fact for
  this note.** Theorem 1.2, verbatim from the PDF:

  > "For every n>=4, one has c(n) = F(n), with precisely three exceptions:
  > c(6) = 8 = F(6)-1, c(7) = 11 = F(7)-2, c(8) = 17 = F(8)-2."

  with F(n) = 1 + C(n-1,2) - floor((n-1)/2). The three exceptional orders are exactly
  the m(6) = 8, m(7) = 11, m(8) = 17 reported in the forum thread, whose author wrote
  "I did not find any of these values in the literature ... If any of this is known, I
  would be glad to be told." Wang additionally gives c(9) = F(9) = 25, settling the
  n = 9 case the thread leaves open, and solves the no-three-collinear variant, where
  he reports a single exceptional order. The abstract states the scope: "We determine
  c(n) for every n >= 4: it equals F(n) apart from three exceptional orders."

  Chronology, so that nobody is made to look careless: the forum comment is dated
  01:48 on 18 Aug 2026; the arXiv posting is 20 Aug 2026. The values were not findable
  by search when the comment was written.

  I have NOT checked Wang's proof. What is checked here is only the section 7.3
  witness, re-derived from his coordinates.
  *[Theorem 1.2 and the abstract VERIFIED AT SOURCE: PDF read 2026-08-31. The proof
  itself is taken on trust.]*

  Section 7.3 is also the source of the rational eight-point witness. The eight coordinates and
  the list of 17 circles were read directly from the paper and match the values used
  here exactly:

      p0 = (0,0)                      p4 = (53519/195938, 1842342/1273597)
      p1 = (263/626, 2178/4069)       p5 = (184032/458545, 7245468/5961085)
      p2 = (263/313, 4356/4069)       p6 = (160557/917090, 5527026/5961085)
      p3 = (789/626, 6534/4069)       p7 = (-25/313, 312/313)

      circles: 0145 0167 024 0257 026 0347 0356 1247 1256 1346 135 137 157
               2345 2367 246 4567

  *[VERIFIED AT SOURCE: PDF fetched and section 7.3 read 2026-08-31. An earlier
  version of this file flagged these coordinates as secondhand; that caveat is now
  discharged.]*
  Note the paper's title is "Circles determined by planar point sets"; an earlier
  draft of this file gave it incorrectly.

* **P. D. T. A. Elliott**, "On the number of circles determined by n points", Acta
  Math. Acad. Sci. Hungar. **18** (1967), 181-188. Wang cites p. 182 for Segre's
  remark, which is where the two-concentric-squares configuration originates.
  *[secondary]*
* **G. B. Purdy and J. W. Smith**, "Lines, Circles, Planes and Spheres", Discrete
  Comput. Geom. **44** (2010), 860-882, arXiv:0907.0724. Corrects Elliott's bound to
  1 + C(n-1,2) - floor((n-1)/2) for n > 393.  *[secondary]*

## What this note claims, and what it withdrew

It verifies both witnesses, shows their designs are isomorphic (lines to lines,
circles to circles), and shows the point sets are **not similar**. It checks no lower
bound and does not claim m(8) = 17.

**It is not a refutation of mzn's non-rationalizability remark, and should not be read
as one.** mzn's descent argument is explicitly about *similarities* of their own
configuration. The similarity test here shows the design has moduli, so a rational
realisation existing elsewhere in the moduli space is entirely compatible with that
argument being correct. What the note establishes is narrower: the arithmetic
obstruction attaches to the parametrisation, not to the configuration type.
