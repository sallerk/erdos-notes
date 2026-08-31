"""Single-shot exact decision of #982 for a fixed n, over the REALS.

Instead of enumerating the millions of possible distance-colourings (decide.py),
state the whole question as one quantifier-free formula of nonlinear real
arithmetic and let z3's nlsat do the case splitting:

  reals  x_0..x_{n-1}, y_0..y_{n-1}          the vertices, in ccw order
  reals  t_{v,1}..t_{v,k}                    the k = floor(n/2)-1 squared
                                             distance LEVELS allowed at vertex v

  normalisation:   x_0=y_0=y_1=0, x_1=1                      (WLOG: similarity)
  strict convexity: for all i<j<k, orient(v_i,v_j,v_k) > 0
  budget:          for every v and every u != v,
                       OR_{s=1..k}  |v u|^2 == t_{v,s}

SAT  => a convex n-gon in which every vertex sees at most k distinct distances
        exists, i.e. #982 is FALSE at that n.
UNSAT => no such convex n-gon exists over the reals, i.e. #982 holds at that n.
UNKNOWN (timeout) => nothing.

This is exhaustive by construction: the formula says exactly the counterexample
condition, with no combinatorial pre-enumeration to get wrong.
"""
import sys, json, time
from itertools import combinations
import z3


def build(n, order=True):
    k = n // 2 - 1
    X = [z3.Real(f'x{i}') for i in range(n)]
    Y = [z3.Real(f'y{i}') for i in range(n)]
    T = [[z3.Real(f't{v}_{s}') for s in range(k)] for v in range(n)]
    C = [X[0] == 0, Y[0] == 0, X[1] == 1, Y[1] == 0]
    for i, j, l in combinations(range(n), 3):
        C.append((X[j]-X[i])*(Y[l]-Y[i]) - (Y[j]-Y[i])*(X[l]-X[i]) > 0)
    for v in range(n):
        for s in range(k - 1):
            C.append(T[v][s] < T[v][s + 1])          # levels sorted: symmetry break
        for u in range(n):
            if u == v:
                continue
            d = (X[u]-X[v])**2 + (Y[u]-Y[v])**2
            C.append(z3.Or([d == T[v][s] for s in range(k)]))
    return C, X, Y, T, k


def run(n, timeout_ms=1800000, tactic='qfnra-nlsat'):
    t0 = time.time()
    C, X, Y, T, k = build(n)
    print(f"n={n}: k=floor(n/2)-1={k}; {2*n + n*k} real variables, "
          f"{len(C)} constraints; tactic={tactic}; timeout {timeout_ms} ms",
          flush=True)
    if tactic:
        s = z3.Tactic(tactic).solver()
    else:
        s = z3.Solver()
    s.set('timeout', timeout_ms)
    for c in C:
        s.add(c)
    r = s.check()
    dt = time.time() - t0
    out = {'n': n, 'k': k, 'nvars': 2*n + n*k, 'nconstraints': len(C),
           'tactic': tactic, 'timeout_ms': timeout_ms,
           'elapsed_s': round(dt, 1), 'z3_version': z3.get_version_string()}
    if r == z3.sat:
        m = s.model()
        pts = [[str(m.eval(X[i], model_completion=True)),
                str(m.eval(Y[i], model_completion=True))] for i in range(n)]
        out['verdict'] = 'sat'
        out['points'] = pts
        out['status'] = 'COMPLETED'
        print(f"*** SAT: COUNTEREXAMPLE at n={n} ***\n{pts}", flush=True)
    elif r == z3.unsat:
        out['verdict'] = 'unsat'
        out['status'] = 'COMPLETED'
        print(f"n={n}: UNSAT in {dt:.0f}s  ==> NO convex {n}-gon counterexample "
              f"to #982 exists over the reals.", flush=True)
    else:
        out['verdict'] = 'unknown'
        out['status'] = 'TIMEOUT'
        print(f"n={n}: UNKNOWN (z3 gave up) after {dt:.0f}s -- contributes "
              f"nothing.", flush=True)
    json.dump(out, open(f'decide2_n{n}.json', 'w'), indent=1)
    return out


if __name__ == '__main__':
    n = int(sys.argv[1])
    tmo = int(sys.argv[2]) if len(sys.argv) > 2 else 1800000
    tac = sys.argv[3] if len(sys.argv) > 3 else 'qfnra-nlsat'
    run(n, tmo, None if tac == 'none' else tac)
