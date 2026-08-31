# References for the #982 note

All of the following are quoted verbatim from https://www.erdosproblems.com/982,
read 2026-08-31.  *[VERIFIED AT SOURCE]*

* **[Mo52] Moser**: f(n) >= ceil(n/3).
* **[ErFi94] Erdős and Fishburn**: f(n) >= floor(n/3 + 1).
* **[Du06b] Dumitrescu**: f(n) >= ceil((13n-6)/36).
* **[NPPZ13] Nivasch, Pach, Pinchasi and Zerbib**: f(n) >= (13/36 + 1/22701)n - O(1).
  This is the published record, and the minus sign on the O(1) is as printed.

* **Scott Duke Kominers**, partial proof claim on the #982 proof-claims tab, "using
  GPT 5.6 Sol, Claude Fable 5", recording a slight strengthening of the additive term.
  *[VERIFIED AT SOURCE: claim exists and is a partial claim, read 2026-08-31. I have
  not examined the claim itself.]*

* **E. Altman**, "On a problem of P. Erdős", Amer. Math. Monthly **70** (1963),
  148-157. Any convex n-gon determines at least floor(n/2) distinct distances in total.
  The pattern enumeration uses this as a prune, so the n = 7 case is conditional on it;
  n <= 6 was additionally run unfiltered and is unconditional. Erdős's own 1975 survey
  (p. 100) attributes this result to Altman.
  *[secondary for the paper itself; the attribution is VERIFIED AT SOURCE via Erdős 1975]*

See `LITERATURE.md` for the fuller search record.

## Artifacts here

`RESULTS.md`, `LITERATURE.md`, `REPRODUCE.md`, the enumerator `patterns.py` and driver
`decide.py`, the near-miss table `nearmiss_3_14.json`, and the run records
`decide_n6_noaltman.json` (unfiltered n = 6, 1834 classes) and `decide_n7.json`
(5354 classes including the retry pass that closed the last six).
