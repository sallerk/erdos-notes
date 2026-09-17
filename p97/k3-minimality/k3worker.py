"""One worker of the k=3 decision pass.  Resumable, append-only, heartbeated.

Contract with the supervisor (k3super.py):
  * BEFORE starting each class the worker writes a heartbeat naming the class it is
    about to attempt.  If the worker wedges inside sympy (which cannot be
    interrupted from within), the supervisor sees a stale heartbeat, kills the
    process, appends that class to the skip file, and restarts the worker.
  * Every finished class is appended as one JSON line and flushed, so a kill loses
    at most the single class in flight.
  * On start the worker reads its own results file and its skip file, so a restart
    resumes rather than repeating.

Per class: grevlex Groebner over Q of the 2n equidistance equations in
perpendicular-bisector form (identical to |v_i v_j|^2 = |v_i v_k|^2, the squared
terms cancel), gauge v_0=(0,0), v_1=(1,0).
  GB == {1}  =>  unit ideal  =>  no complex zeros, hence no real ones  =>  REFUTED.
  otherwise  =>  z3 nlsat on the GB plus strict convex position (ALL C(n,3)
                 orientations) and the two implied lemmas.
"""
import sys, os, json, time
from itertools import combinations
import numpy as np, sympy as sp, z3
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
    z3ms = int(sys.argv[4]); tag = sys.argv[5] if len(sys.argv) > 5 else ''
    idxfile = sys.argv[6] if len(sys.argv) > 6 else None    # optional .npy list of class indices
    base = 'n%d%s_%02d' % (n, tag, shard)
    resf = 'res_%s.jsonl' % base
    hbf = 'hb_%s.json' % base
    skipf = 'skip_%s.txt' % base

    pid, NP, NT, TJ, TK, TL = tables(n)
    cls = np.load('cls_n%d.npy' % n)
    pool = np.load(idxfile) if idxfile else np.arange(len(cls))
    idx = pool[shard::nsh].copy()
    np.random.default_rng(12345 + shard).shuffle(idx)

    seen = set()
    if os.path.exists(resf):
        for line in open(resf):
            line = line.strip()
            if not line:
                continue
            try:
                seen.add(json.loads(line)['idx'])
            except Exception:
                pass
    if os.path.exists(skipf):
        for line in open(skipf):
            line = line.strip()
            if line:
                seen.add(int(line.split()[0]))
    todo = [int(i) for i in idx if int(i) not in seen]

    X = sp.symbols('x2:%d' % n); Y = sp.symbols('y2:%d' % n)
    P = [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0))] + \
        [(X[i], Y[i]) for i in range(n - 2)]
    Nn = lambda a: P[a][0] ** 2 + P[a][1] ** 2

    out = open(resf, 'a')
    ndone = len(seen)
    total = len(idx)
    for ci in todo:
        json.dump({'idx': int(ci), 't': time.time(), 'done': ndone, 'total': total,
                   'pid': os.getpid()}, open(hbf, 'w'))
        ch = cls[ci]
        ta = time.time()
        eqs = []
        for i in range(n):
            t = ch[i]; j, k, l = int(TJ[i, t]), int(TK[i, t]), int(TL[i, t])
            eqs.append(sp.expand(2 * (P[k][0] - P[j][0]) * P[i][0]
                                 + 2 * (P[k][1] - P[j][1]) * P[i][1] - (Nn(k) - Nn(j))))
            eqs.append(sp.expand(2 * (P[l][0] - P[k][0]) * P[i][0]
                                 + 2 * (P[l][1] - P[k][1]) * P[i][1] - (Nn(l) - Nn(k))))
        rec = {'idx': int(ci)}
        try:
            g = sp.groebner(eqs, *(list(X) + list(Y)), order='grevlex')
        except Exception as e:
            rec.update(v='gb_error', msg=str(e)[:70], s=round(time.time() - ta, 2))
            out.write(json.dumps(rec) + '\n'); out.flush(); ndone += 1
            continue
        if list(g.exprs) == [sp.Integer(1)]:
            rec.update(v='unit_ideal', s=round(time.time() - ta, 2))
        else:
            m = {}
            for i, s in enumerate(X):
                m[s] = z3.Real('x%d' % (i + 2))
            for i, s in enumerate(Y):
                m[s] = z3.Real('y%d' % (i + 2))
            zx = [z3.RealVal(0), z3.RealVal(1)] + [m[X[i]] for i in range(n - 2)]
            zy = [z3.RealVal(0), z3.RealVal(0)] + [m[Y[i]] for i in range(n - 2)]
            sol = z3.Solver(); sol.set('timeout', z3ms)
            try:
                for e in g.exprs:
                    sol.add(conv(e, m) == 0)
            except Exception as e:
                rec.update(v='conv_error', msg=str(e)[:70], s=round(time.time() - ta, 2))
                out.write(json.dumps(rec) + '\n'); out.flush(); ndone += 1
                continue
            for a, b, cc in combinations(range(n), 3):
                sol.add((zx[b] - zx[a]) * (zy[cc] - zy[a]) - (zy[b] - zy[a]) * (zx[cc] - zx[a]) > 0)
            D = lambda a, b: (zx[a] - zx[b]) ** 2 + (zy[a] - zy[b]) ** 2
            for i in range(n):
                t = ch[i]; j, k, l = int(TJ[i, t]), int(TK[i, t]), int(TL[i, t])
                sol.add(D(j, l) > D(j, k) + D(k, l))
                A, B, C, Rr = D(j, k), D(k, l), D(j, l), D(i, j)
                sol.add(Rr * (2 * A * B + 2 * B * C + 2 * C * A - A * A - B * B - C * C) == A * B * C)
            r = sol.check()
            if r == z3.sat:
                mm = sol.model()
                rec.update(v='SAT', s=round(time.time() - ta, 2),
                           pattern=[[int(TJ[i, ch[i]]), int(TK[i, ch[i]]), int(TL[i, ch[i]])] for i in range(n)],
                           points=[[str(mm.eval(zx[i], model_completion=True)),
                                    str(mm.eval(zy[i], model_completion=True))] for i in range(n)])
            elif r == z3.unsat:
                rec.update(v='unsat', s=round(time.time() - ta, 2))
            else:
                rec.update(v='z3_unknown', s=round(time.time() - ta, 2))
        out.write(json.dumps(rec) + '\n'); out.flush()
        ndone += 1
    json.dump({'idx': -1, 't': time.time(), 'done': ndone, 'total': total,
               'pid': os.getpid(), 'finished': True}, open(hbf, 'w'))
    out.close()
    print('shard %02d EXHAUSTED: %d/%d handled' % (shard, ndone, total), flush=True)


if __name__ == '__main__':
    main()
