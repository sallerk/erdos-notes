"""One SHARD of the decision pass: a plain single-threaded process handling the
pattern classes whose index is congruent to SHARD mod NSHARDS.

No multiprocessing anywhere -- shards are independent OS processes launched by
launch.py, each writing its own JSON.  This avoids pool/handle machinery
entirely and makes progress individually inspectable.

Per class:
  1. Build the 2n equidistance equations in perpendicular-bisector form
       2(x_k-x_j) x_i + 2(y_k-y_j) y_i = (x_k^2+y_k^2) - (x_j^2+y_j^2),
     identically equal to |v_i v_j|^2 - |v_i v_k|^2 (the squared terms cancel),
     with the WLOG gauge v_0=(0,0), v_1=(1,0).
  2. Groebner basis over Q, grevlex.
       GB == {1}  =>  unit ideal  =>  no complex zeros (Nullstellensatz)
                  =>  no real zeros  =>  REFUTED exactly, no solver involved.
  3. Otherwise hand z3 the GB generators (same ideal, simpler polynomials) plus
       * strict convex position: ALL C(n,3) orientations positive
       * obtuse-middle inequality  D_jl > D_jk + D_kl
       * the circumradius identity (both implied; proved in cmlemma.py)

Verdicts are recorded separately and never merged: unit_ideal, unsat, SAT,
z3_unknown, error.
"""
import numpy as np, sys, json, time, os
from itertools import combinations
import sympy as sp, z3
from enum_nb import tables


def conv(e, m):
    if e.is_Add:
        return sum(conv(a, m) for a in e.args)
    if e.is_Mul:
        r = 1
        for a in e.args:
            r = r * conv(a, m)
        return r
    if e.is_Pow:
        return conv(e.base, m) ** int(e.exp)
    if e.is_Rational:
        return z3.RealVal(sp.Rational(e))
    if e.is_Symbol:
        return m[e]
    raise ValueError(str(e))


def main():
    n = int(sys.argv[1]); shard = int(sys.argv[2]); nsh = int(sys.argv[3])
    tmo = int(sys.argv[4]) if len(sys.argv) > 4 else 20000
    tag = sys.argv[5] if len(sys.argv) > 5 else ''
    pid, NP, NT, TJ, TK, TL = tables(n)
    cls = np.load('cls_n%d.npy' % n)
    idx = np.arange(shard, len(cls), nsh)
    np.random.default_rng(12345 + shard).shuffle(idx)   # spread hard regions evenly
    X = sp.symbols('x2:%d' % n); Y = sp.symbols('y2:%d' % n)
    P = [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0))] + \
        [(X[i], Y[i]) for i in range(n - 2)]
    Nn = lambda a: P[a][0] ** 2 + P[a][1] ** 2
    out = {'n': n, 'shard': shard, 'nshards': nsh, 'assigned': int(len(idx)),
           'done': 0, 'unit_ideal': 0, 'unsat': 0, 'sat': [], 'z3_unknown': [],
           'errors': [], 'z3_timeout_ms': tmo, 'slowest_s': 0.0,
           'method': ('grevlex Groebner over QQ; unit ideal refutes exactly; else nlsat on the '
                      'GB + all C(n,3) orientations + obtuse + circumradius lemmas'),
           'status': 'RUNNING', 'pid': os.getpid()}
    fn = 'shard_n%d%s_%02d.json' % (n, tag, shard)
    t0 = time.time()
    for c, ci in enumerate(idx, 1):
        ch = cls[ci]
        eqs = []
        for i in range(n):
            t = ch[i]; j, k, l = int(TJ[i, t]), int(TK[i, t]), int(TL[i, t])
            eqs.append(sp.expand(2 * (P[k][0] - P[j][0]) * P[i][0]
                                 + 2 * (P[k][1] - P[j][1]) * P[i][1] - (Nn(k) - Nn(j))))
            eqs.append(sp.expand(2 * (P[l][0] - P[k][0]) * P[i][0]
                                 + 2 * (P[l][1] - P[k][1]) * P[i][1] - (Nn(l) - Nn(k))))
        ta = time.time()
        try:
            g = sp.groebner(eqs, *(list(X) + list(Y)), order='grevlex')
        except Exception as e:
            out['errors'].append([int(ci), 'gb_error', str(e)[:70]])
            out['done'] = c
            continue
        if list(g.exprs) == [sp.Integer(1)]:
            out['unit_ideal'] += 1
        else:
            m = {}
            for i, s in enumerate(X):
                m[s] = z3.Real('x%d' % (i + 2))
            for i, s in enumerate(Y):
                m[s] = z3.Real('y%d' % (i + 2))
            zx = [z3.RealVal(0), z3.RealVal(1)] + [m[X[i]] for i in range(n - 2)]
            zy = [z3.RealVal(0), z3.RealVal(0)] + [m[Y[i]] for i in range(n - 2)]
            s = z3.Solver(); s.set('timeout', tmo)
            try:
                for e in g.exprs:
                    s.add(conv(e, m) == 0)
            except Exception as e:
                out['errors'].append([int(ci), 'conv_error', str(e)[:70]])
                out['done'] = c
                continue
            for a, b, cc in combinations(range(n), 3):
                s.add((zx[b] - zx[a]) * (zy[cc] - zy[a]) - (zy[b] - zy[a]) * (zx[cc] - zx[a]) > 0)
            D = lambda a, b: (zx[a] - zx[b]) ** 2 + (zy[a] - zy[b]) ** 2
            for i in range(n):
                t = ch[i]; j, k, l = int(TJ[i, t]), int(TK[i, t]), int(TL[i, t])
                s.add(D(j, l) > D(j, k) + D(k, l))
                A, B, C, R = D(j, k), D(k, l), D(j, l), D(i, j)
                s.add(R * (2 * A * B + 2 * B * C + 2 * C * A - A * A - B * B - C * C) == A * B * C)
            r = s.check()
            if r == z3.sat:
                mm = s.model()
                out['sat'].append({'idx': int(ci),
                    'pattern': [[int(TJ[i, ch[i]]), int(TK[i, ch[i]]), int(TL[i, ch[i]])] for i in range(n)],
                    'points': [[str(mm.eval(zx[i], model_completion=True)),
                                str(mm.eval(zy[i], model_completion=True))] for i in range(n)]})
                print('*** SAT idx=%d' % ci, flush=True)
            elif r == z3.unsat:
                out['unsat'] += 1
            else:
                out['z3_unknown'].append(int(ci))
        dt = time.time() - ta
        if dt > out['slowest_s']:
            out['slowest_s'] = round(dt, 2)
            out['slowest_idx'] = int(ci)
        out.setdefault('top', []).append([round(dt, 2), int(ci)])
        out['top'] = sorted(out['top'], reverse=True)[:10]
        out['done'] = c
        if c % 20 == 0:
            el = time.time() - t0
            out['elapsed_s'] = round(el, 1)
            out['rate_per_s'] = round(c / el, 2)
            out['eta_min'] = round((len(idx) - c) / max(1e-9, c / el) / 60, 1)
            json.dump(out, open(fn, 'w'), indent=1)
            print('shard %02d: %d/%d %.0fs unit=%d unsat=%d sat=%d unk=%d eta=%.0fmin'
                  % (shard, c, len(idx), el, out['unit_ideal'], out['unsat'],
                     len(out['sat']), len(out['z3_unknown']), out['eta_min']), flush=True)
    out['elapsed_s'] = round(time.time() - t0, 1)
    out['status'] = 'COMPLETED'
    json.dump(out, open(fn, 'w'), indent=1)
    print('shard %02d COMPLETED %d classes in %.0fs: unit=%d unsat=%d sat=%d unknown=%d err=%d'
          % (shard, len(idx), out['elapsed_s'], out['unit_ideal'], out['unsat'],
             len(out['sat']), len(out['z3_unknown']), len(out['errors'])), flush=True)


if __name__ == '__main__':
    main()
