# Lessons, p831

Directory-local. The global file is ../tasks/lessons.md (L1-L80); read it first.

## P1 - Read the problem's own source for the extremal gadget before searching
Erdos's [Er75h] opens by quoting E. Szekeres that the orthocentre of a triangle makes
all four circumradii equal. That single sentence IS h(4)=1, and it is also the whole
key to the n=5 case analysis (Lemma 3 below). Two hours of search would not have
produced it. The problem page does not carry the remark; only the source does.

## P2 - Absolute residuals are meaningless when the configuration can rescale
caseA.py first minimised differences of R^2 directly. A configuration can shrink any
such difference by spreading out, so residuals of 1e-7 looked like near-solutions and
were nothing of the kind. Every residual in this directory is now divided by the mean
R^2 of the configuration, and degeneracy is penalised explicitly so the optimiser
cannot buy a small residual with a flat triangle or a point at infinity.

## P3 - The positive control must be able to fail
ctrlA.py asks the same optimiser to solve 1, 2, 3, 4 and 5 of the four Case A
equations. It solves four to 6e-14 and fails at five. That is what makes the Case A
negative (best residual 7e-8) mean something. CORRECTION (audit, 2026-09-07): this lesson was
written about a control that did not work, and its diagnosis was also wrong. The k=4
configuration is NOT four concyclic points; min |det4| there is 3.66. The real pathology
is a near-collinear triple sending one circumradius to 7.6e14, which the mean-based
normalisation then divided away. See P10. The lesson that a control must be able to fail
stands; this was not an example of one.

## P4 - A greedy beam walked straight into a proved dead end
beam.py with width 400 started every n=5 configuration from the orthocentric n=4
optimum and reached only 5 distinct radii, worse than an exhaustive grid search. The
reason is Lemma 3: an orthocentric quadruple saturates both circles of its radius
through every one of its pairs, so it can never be extended within its own class. The
best n=4 configuration is the worst possible seed. Width 30000 recovered 4.

## P5 - Do not write scratch files to /tmp on this machine
C:\TEMP contains an unrelated inspect.py which shadows the standard library, so any
script run from there dies inside numpy's import. Scratch goes in the session
scratchpad directory or in the project.

## P6 - The dimension count said a solution family existed; the geometry said no
The one surviving n=5 pattern is two equations in three angles, so a one-parameter
family of solutions was expected. There is none in the admissible region. What the
count misses is that the solution set sits entirely on the degenerate boundary: the
residual floor is proportional to the SQUARE of the angular separation of the four
circle centres, so it reaches zero only when two centres merge, which merges two class
circles and puts four points on a circle. Measuring the floor as a function of the
non-degeneracy margin is a much better diagnostic than any single residual, because it
distinguishes "no solution" from "solution just outside the region searched".

## P7 - The optimiser will find the degenerate branch every single time
Four equal circumradii on four points means orthocentric OR concyclic. Least squares
converged on the concyclic branch at once, with residual 4e-15 and a configuration
whose 4x4 concyclicity determinant was 1.5e-15. The equalities cannot distinguish the
branches; only the side conditions can. Concyclicity penalties belong INSIDE the
objective, not in a post-filter, or every restart lands in the same worthless basin.

## P8 - Check the novelty of the exact statement, not of the idea
The lower bound h(n) >= C(n,3)/f(n) reads like a new reduction. It is not: the one
forum comment on the page already says "the same simple double-counting lower bound
from #104", and C(n,3)/(n(n-1)/3) equals (n-2)/2 identically, so that comment IS this
proposition with a weaker f substituted. What survives is only the use of the exact
A003829 values. Found before any claim was drafted, by asking the literature agent
specifically whether the INEQUALITY had been stated (L14 ordering, applied properly).

## P9 - A control that is easier than the target validates nothing about the target
My own audit caught this before either audit agent reported. The pscreen control was a
4-class pattern: six equations in six unknowns, exactly determined. Every pattern it
was validating had three classes: seven equations in six unknowns, overdetermined. So
the control proved the optimiser solves exactly-determined systems, which was never in
doubt, and said nothing about whether it could find a solution that exists only because
the equations are dependent. The fix was to build a control with a KNOWN rank
deficiency (ctrlB.py: six equations, Jacobian rank five, admissible by construction);
the screen finds it at 8.5e-16 from 100 restarts. Always state the control's difficulty
in the same units as the target's - here, equations minus unknowns, and the rank
deficiency - and check they match before quoting a negative.

## P10 - Normalise a residual by the quantities it constrains, never by a global mean
The single worst defect in this directory. ctrlA.py divided each residual by the mean
of ALL SIX radii while constraining only k of them, so the optimiser drove an
UNCONSTRAINED radius to 1e15 by flattening one triangle and divided the residual away.
Rungs reported SOLVED at 1e-14 were violating their equations by up to 61%, and the one
rung that actually held was printed NOT SOLVED. The ladder was inverted, and every
negative that cited it was uncontrolled. This is the exact inverse of P2: P2 says
absolute residuals are meaningless because the configuration can rescale, and the fix
adopted there - divide by the mean - introduced this. The right measure is per-equation:
(r_a - r_b) / (|r_a| + |r_b|), which no other quantity can inflate.

## P11 - A residual that sits on your own penalty margin is measuring the margin
Two of the fifteen screened patterns had their optimum exactly on pscreen's hard-coded
concyclicity threshold tau = 1e-6, and sweeping tau across four decades moved the
"negative" with it, roughly linearly. The headline "min residual 1.5e-7, a gap of eight
orders of magnitude" was a measurement of the constant 1e-6. Whenever a guard is active
at the optimum, the number reported is a property of the guard. The test that means
something is the SCALING: fit the floor against the margin, and read the slope. Slope
near 1 means realisable only in the degenerate limit; slope near 0 means genuinely
obstructed. obstruction433.py did this correctly and survived the audit untouched;
pscreen.py did not and its headline had to be withdrawn.

## P12 - A larger rank deficiency makes a control EASIER, not harder
I built ctrlB.py to be a harder control on the grounds that its solution set had
positive codimension. The inference runs backwards: a bigger rank deficiency means a
BIGGER solution set, which random restarts find more easily. Measured hit rates settled
it, 47/500 against 51/500 for the control it replaced - no harder at all. And the rank
itself was wrong, 4 not 5, because one-sided differences at eps = 1e-6 were compared
against an ABSOLUTE tolerance while the two smallest singular values fall as eps^2.
Measure a control's difficulty by its hit rate, which is the thing you actually care
about, not by a dimension argument.

## P13 - A search for something you have already proved impossible confirms nothing
orthobranch.py searched 80,000 restarts for a configuration that is both a parallelogram
(forced by its own parametrisation) and orthocentric (excluded by Lemma 6). It could
only ever fail, so its empty result is not evidence about anything, and a version with a
bug would have produced the identical artifact. I reported it as "independent
confirmation". Before running a search, check whether the directory already contains a
proof that its target does not exist.

## P14 - Write the audit check against the CONTENT of the artifact, not its flags
verify.py's check of the two headline exhaustive runs tested only the "completed" flag
and the "target" field. A doctored artifact claiming a five-point set with ONE
circumradius would have passed. An audit that reads only metadata audits nothing; it
must re-derive the recorded witness from the definitions.

## P15 - Sweeping one guard does not fix "the residual sits on a guard"
The first audit found pscreen's floor sitting on its concyclicity margin, so I made that
margin a parameter and swept it. The replacement test then classified 13 of 15 patterns
as genuinely obstructed. Round two showed the class-separation guard, which the new test
still held fixed at 1e-3, was active at 12 of those 13, and that sweeping IT moved the
floor by 396x across three decades while the minimum-distance guard moved it by 0.78x.
The fix reproduced the defect one guard over.
RULE: before reporting any floor, report WHICH constraint is active at the optimum. If
one is, the number measures that constant. Sweep every active guard, or state the
verdict as "realisable only as constraint X degenerates" rather than as an obstruction.

## P16 - A retraction that lives only in the prose is not a retraction
I corrected NOTE.md and AUDIT_SUMMARY.md to withdraw the OBSTRUCTED verdict, and left the
script that computes it, the artifact that stores it, and the REPRODUCE line that tells
the reader to run it, all unchanged. An auditor reading the code would have got the old
answer. When a conclusion is withdrawn, the label in the code, the field in the JSON and
the instruction in the reproduction notes all have to move with it.

## P17 - A ladder of nested systems must be monotone BY CONSTRUCTION
My Case A control solved each rung with its own independent random restarts, so rung 4
came back better than rung 3 - impossible, since a 3-equation system is a relaxation of
the 4-equation one. The reported reach was restart noise, and it was the number the
write-up offered as its honest self-assessment. Evaluate every point found at any rung
against every shorter prefix, and assert monotonicity so the run fails loudly instead of
reporting nonsense.

## P18 - Run the audit script after editing it, before quoting its verdict
I edited verify.py to add two checks, then told the user the suite was clean. The edit had
left an orphan `else` and the file did not parse; it had not run since. Then a second
edit asserted a sentence in NOTE.md that the note words slightly differently, so the
check failed on the wording rather than on the fact. Both are the same mistake: an audit
script is code, and changing it invalidates the last result until it is re-run. Never
report a suite as passing on the strength of a run that predates the current edit.
