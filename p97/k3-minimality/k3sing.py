"""Decide n = 7 pattern classes with Singular instead of sympy, then z3 as k3worker.py does.

For the classes whose sympy Groebner basis did not finish in 300 s (c123_n7_undecided_pass2.npy).
The equations are EXACTLY those of k3worker.py: gauge v_0 = (0,0), v_1 = (1,0), for each vertex i
with witness triple (j,k,l) the two perpendicular-bisector equations for the pairs (j,k), (k,l).

  gen <index.npy> <dir>        write <dir>/<idx>.sing (slimgb over Q, grevlex)
  run <dir> <jobs> <timeout_s> run every .sing in the Docker container cas97k3, <jobs> at a time;
                               results in <dir>/singular.json
  z3  <dir> <timeout_s>        for every class Singular left NON-unit: z3 nlsat on the basis plus
                               strict convex position (all C(7,3) orientations), the obtuse lemma
                               and the circumradius identity, each class in its own process with
                               a hard wall-clock kill; results in <dir>/z3.json

Singular UNIT means 1 is in the ideal over Q: no complex solution, so the class is refuted.
Container: docker run -d --name cas97k3 --cpus 10 -v "<k3min>:/work" erdos831-cas sleep infinity
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

import numpy as np
import sympy as sp

from enum_nb import tables

N = 7
CONTAINER = 'cas97k3'
X = sp.symbols('x2:%d' % N)
Y = sp.symbols('y2:%d' % N)
P = [(sp.Integer(0), sp.Integer(0)), (sp.Integer(1), sp.Integer(0))] + [(X[i], Y[i]) for i in range(N - 2)]


def equations(ch, TJ, TK, TL):
    Nn = lambda a: P[a][0] ** 2 + P[a][1] ** 2
    eqs = []
    for i in range(N):
        t = ch[i]
        j, k, l = int(TJ[i, t]), int(TK[i, t]), int(TL[i, t])
        eqs.append(sp.expand(2 * (P[k][0] - P[j][0]) * P[i][0] + 2 * (P[k][1] - P[j][1]) * P[i][1] - (Nn(k) - Nn(j))))
        eqs.append(sp.expand(2 * (P[l][0] - P[k][0]) * P[i][0] + 2 * (P[l][1] - P[k][1]) * P[i][1] - (Nn(l) - Nn(k))))
    return eqs


def gen(index_file, d):
    pid, NP, NT, TJ, TK, TL = tables(N)
    cls = np.load('cls_n%d.npy' % N)
    os.makedirs(d, exist_ok=True)
    names = ','.join(str(s) for s in list(X) + list(Y))
    for ci in np.load(index_file):
        ci = int(ci)
        polys = ',\n  '.join(str(e).replace('**', '^') for e in equations(cls[ci], TJ, TK, TL))
        txt = ('option(redSB);\nring R = 0, (%s), dp;\nideal I =\n  %s;\nint t0 = rtimer;\n'
               'ideal G = slimgb(I);\n'
               'if (reduce(poly(1), G) == 0) { print("RESULT UNIT"); }\n'
               'else { print("RESULT NONUNIT " + string(size(G))); write(":w /work/%s/%d.gb", G); }\n'
               'quit;\n') % (names, polys, d, ci)
        open(os.path.join(d, '%d.sing' % ci), 'w', newline='\n').write(txt)
    print('wrote %d files to %s' % (len(np.load(index_file)), d))


def run(d, jobs, timeout_s):
    files = sorted(f for f in os.listdir(d) if f.endswith('.sing'))
    resf = os.path.join(d, 'singular.json')
    res = json.load(open(resf)) if os.path.exists(resf) else {}

    def one(f):
        ci = f[:-5]
        if ci in res and res[ci]['status'] in ('UNIT', 'NONUNIT'):
            return
        t = time.time()
        cmd = 'cd /work && timeout %d Singular -q %s/%s' % (timeout_s, d, f)
        p = subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-c', cmd], capture_output=True, text=True)
        out = p.stdout + p.stderr
        if 'RESULT UNIT' in out:
            st = 'UNIT'
        elif 'RESULT NONUNIT' in out:
            st = 'NONUNIT'
        elif p.returncode == 124:
            st = 'TIMEOUT'
        else:
            st = 'ERROR rc=%d %s' % (p.returncode, out.strip()[-120:])
        res[ci] = {'status': st, 'seconds': round(time.time() - t, 1)}
        json.dump(res, open(resf, 'w'), indent=1)
        print('%s %s %.1fs' % (ci, st, time.time() - t), flush=True)

    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(one, files))
    from collections import Counter
    print('SINGULAR DONE', Counter(r['status'].split()[0] for r in res.values()))


def z3_one(ci, d, timeout_s):
    import z3
    from k3worker import conv
    pid, NP, NT, TJ, TK, TL = tables(N)
    ch = np.load('cls_n%d.npy' % N)[ci]
    txt = open(os.path.join(d, '%d.gb' % ci)).read().replace('^', '**')
    loc = {str(s): s for s in list(X) + list(Y)}
    gb = [sp.sympify(p, locals=loc) for p in txt.split(',') if p.strip()]
    m = {s: z3.Real(str(s)) for s in list(X) + list(Y)}
    zx = [z3.RealVal(0), z3.RealVal(1)] + [m[X[i]] for i in range(N - 2)]
    zy = [z3.RealVal(0), z3.RealVal(0)] + [m[Y[i]] for i in range(N - 2)]
    sol = z3.Solver()
    for e in gb:
        sol.add(conv(sp.expand(e), m) == 0)
    for a, b, c in combinations(range(N), 3):
        sol.add((zx[b] - zx[a]) * (zy[c] - zy[a]) - (zy[b] - zy[a]) * (zx[c] - zx[a]) > 0)
    D = lambda a, b: (zx[a] - zx[b]) ** 2 + (zy[a] - zy[b]) ** 2
    for i in range(N):
        t = ch[i]
        j, k, l = int(TJ[i, t]), int(TK[i, t]), int(TL[i, t])
        sol.add(D(j, l) > D(j, k) + D(k, l))
        A, B, C, R = D(j, k), D(k, l), D(j, l), D(i, j)
        sol.add(R * (2 * A * B + 2 * B * C + 2 * C * A - A * A - B * B - C * C) == A * B * C)
    r = sol.check()
    out = {'verdict': str(r)}
    if r == z3.sat:
        mm = sol.model()
        out['points'] = [[str(mm.eval(zx[i], model_completion=True)), str(mm.eval(zy[i], model_completion=True))]
                         for i in range(N)]
    print(json.dumps(out), flush=True)


def z3_all(d, timeout_s):
    sing = json.load(open(os.path.join(d, 'singular.json')))
    resf = os.path.join(d, 'z3.json')
    res = json.load(open(resf)) if os.path.exists(resf) else {}
    for ci, r in sorted(sing.items()):
        if r['status'] != 'NONUNIT' or ci in res:
            continue
        t = time.time()
        try:
            p = subprocess.run([sys.executable, __file__, 'z3one', ci, d], capture_output=True, text=True,
                               timeout=timeout_s)
            line = [x for x in p.stdout.splitlines() if x.startswith('{')]
            v = json.loads(line[-1]) if line else {'verdict': 'ERROR', 'msg': (p.stderr or '')[-200:]}
        except subprocess.TimeoutExpired:
            v = {'verdict': 'TIMEOUT'}
        v['seconds'] = round(time.time() - t, 1)
        res[ci] = v
        json.dump(res, open(resf, 'w'), indent=1)
        print(ci, v['verdict'], v['seconds'], flush=True)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'gen':
        gen(sys.argv[2], sys.argv[3])
    elif cmd == 'run':
        run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'z3':
        z3_all(sys.argv[2], int(sys.argv[3]))
    elif cmd == 'z3one':
        z3_one(int(sys.argv[2]), sys.argv[3], None)
