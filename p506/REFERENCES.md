# References for the #506 note

* **mzn**, comment of 18 Aug 2026 on https://www.erdosproblems.com/forum/thread/506.
  Source of the Q(sqrt 15) eight-point witness and of the quoted descent argument.
  *[VERIFIED AT SOURCE: thread fetched and the passage read verbatim 2026-08-31]*

* **Liyan Wang**, "Circles determined by planar point sets", arXiv:2608.19844,
  section 7.3. Source of the rational eight-point witness. The eight coordinates and
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

An earlier draft asserted mzn's non-rationalizability remark was false. **That was
withdrawn.** The similarity test showed the design has moduli, and mzn's descent is
explicitly about similarities, so their argument can be correct for their own family
while a rational realisation exists elsewhere in the moduli space.
