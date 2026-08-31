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
  n <= 6 was additionally run unfiltered and is unconditional.

  Two things to keep straight. Altman's bound counts distances **among all vertices**;
  problem #982 asks for floor(n/2) **from a single vertex**, which is why #982 is still
  open. And Altman's result is in fact an equality, D_conv(n) = floor(n/2); only the
  lower half is used here.

  The attribution is verified at source twice over. Erdos, Ann. Mat. Pura Appl. 103
  (1975), p. 100, writing of the first of three conjectures about convex polygons:
  "This conjecture was proved by ALTMAN", with the full reference in the same paper's
  bibliography as "E. ALTMAN, On a problem of P. Erdos, Amer. Math. Monthly, 70 (1963),
  pp. 148-157". Problem #982 is the SECOND conjecture in that same paragraph, which
  Erdos there calls "not yet settled". Independently, [NPPZ13] states "The weaker
  statement that every set of n points in convex position determines floor(n/2) distinct
  distances was proved by Altman."
  *[attribution VERIFIED AT SOURCE (Erdos 1975 scan, read 2026-08-31, and NPPZ13);
  the Altman paper itself is secondary, not obtained]*

  Note also that the #982 problem page carries no Altman reference of its own; the
  citation here comes from the two sources above, not from the page.

See `LITERATURE.md` for the fuller search record.

## Artifacts here

`RESULTS.md`, `LITERATURE.md`, `REPRODUCE.md`, the enumerator `patterns.py` and driver
`decide.py`, the near-miss table `nearmiss_3_14.json`, and the run records
`decide_n6_noaltman.json` (unfiltered n = 6, 1834 classes) and `decide_n7.json`
(5354 classes including the retry pass that closed the last six).
