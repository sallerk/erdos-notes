"""Isolate and re-attack the patterns that hdecide.py left UNKNOWN.

An UNKNOWN is not a result.  Until every pattern is decided, nothing can be claimed
about h(n).  This script finds the undecided ones and throws harder tactics at them:
the dedicated nonlinear-arithmetic solver (qfnra-nlsat), a longer budget, and if that
still fails, a sympy Groebner-basis attempt on the equality part alone.

Usage:  python chase.py <n> <k> [timeout_ms]
"""
import sys, itertools, json, time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import z3
from hdecide import pairs, enumerate_patterns, det4

n = int(sys.argv[1])
k = int(sys.argv[2])
TMO = int(sys.argv[3]) if len(sys.argv) > 3 else 600000


def build(pat, use_strict=True):
    P = pairs(n)
    m = max(pat) + 1
    X = [z3.Real('x%d' % i) for i in range(n)]
    Y = [z3.Real('y%d' % i) for i in range(n)]
    D = [z3.Real('d%d' % c) for c in range(m)]
    C = []
    C += [X[0] == 0, Y[0] == 0, Y[1] == 0, X[1] > 0]
    if n > 2:
        C += [Y[2] >= 0]
    C += [D[0] > 0]
    C += [D[c] < D[c + 1] for c in range(m - 1)]
    for idx, (i, j) in enumerate(P):
        C += [(X[i] - X[j]) ** 2 + (Y[i] - Y[j]) ** 2 == D[pat[idx]]]
    if use_strict:
        for (i, j, l) in itertools.combinations(range(n), 3):
            C += [(X[j] - X[i]) * (Y[l] - Y[i]) - (X[l] - X[i]) * (Y[j] - Y[i]) != 0]
        for quad in itertools.combinations(range(n), 4):
            rows = [[X[t] ** 2 + Y[t] ** 2, X[t], Y[t], 1] for t in quad]
            C += [det4(rows) != 0]
    return C, X, Y, D


def try_solver(pat, tactic, tmo, strict=True):
    C, X, Y, D = build(pat, strict)
    if tactic == 'nlsat':
        s = z3.Tactic('qfnra-nlsat').solver()
    else:
        s = z3.Solver()
    s.set('timeout', tmo)
    s.add(C)
    t0 = time.time()
    r = s.check()
    dt = time.time() - t0
    if r == z3.sat:
        return 'sat', dt, s.model()
    if r == z3.unsat:
        return 'unsat', dt, None
    return 'unknown', dt, None


print('=' * 74)
print('CHASING UNDECIDED PATTERNS  n=%d  k=%d' % (n, k))
print('=' * 74)
pats = list(enumerate_patterns(n, k))
print('%d patterns mod symmetry' % len(pats))
print()

undecided = []
for pat in pats:
    r, dt, mdl = try_solver(pat, 'default', 20000)
    if r == 'unknown':
        undecided.append(pat)
        print('  UNDECIDED at 20s: %s' % (pat,))
print()
print('%d undecided by the default solver at 20s' % len(undecided))
print()

results = {}
for pat in undecided:
    print('  pattern %s' % (pat,))
    # what the pattern means, in words
    P = pairs(n)
    cls = {}
    for idx, p in enumerate(P):
        cls.setdefault(pat[idx], []).append(p)
    for c in sorted(cls):
        print('     class %d (%d pairs): %s' % (c, len(cls[c]), cls[c]))
    for tac, tmo in (('nlsat', TMO), ('default', TMO)):
        r, dt, mdl = try_solver(pat, tac, tmo)
        print('     %-8s %-8s %.1fs' % (tac, r, dt))
        results[str(pat)] = results.get(str(pat), {})
        results[str(pat)][tac] = {'result': r, 'seconds': round(dt, 1)}
        if r == 'sat':
            print('     MODEL:', mdl)
            break
        if r == 'unsat':
            break

json.dump(results, open('chase_n%d_k%d.json' % (n, k), 'w'), indent=1)
print()
print('written: chase_n%d_k%d.json' % (n, k))
