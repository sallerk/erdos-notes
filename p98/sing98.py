"""Re-decide the n = 5, k = 4 patterns whose rejection rests on assumption A8 (ASSUMPTIONS.md),
and the n = 6 and n = 7 candidates of exposure98.py, with Singular and msolve, independently of
hard.py (2026-09-16/17).

THE 96.  Of the 153 patterns hard.py called unsat, 57 are settled independently (11 trivial
Groebner ideals in gap_trivial.json, 46 unordered z3 unsats in ordercheck_out.json).  The other
96 are the 24 ordercheck timeouts plus the 72 unknowns of z3_residual.json; `weak96` rebuilds
that list and asserts the partition.

ENCODING (a pattern lists a class for each pair of points in combinations(range(5), 2) order).
Gauge P0 = (0,0), P1 = (1,0): legitimate because the points are distinct, and it forces the
class of pair (0,1) to have squared length 1.  Unknowns x2..x4, y2..y4 and d_c for each class.
Equations: |P_i - P_j|^2 - d_class(ij) = 0 for all 10 pairs, d_class(01) - 1 = 0, and the
Rabinowitsch equation t * prod_{a<b} (d_a - d_b) * prod_c d_c - 1 = 0, since in an admissible
set the classes are distinct and every distance is non-zero.
  Singular UNIT (1 in the ideal over Q): no complex solution, so no admissible set: REFUTED.
  NON-UNIT: 'genfull' adds no three collinear and no four concyclic (Rabinowitsch variables
  u, w; n = 5 only, the products are too large beyond); 'post' computes dimension, a lex basis
  and msolve's real solutions; realsol98.py then classifies every real solution exactly.
  The z3 subcommand was tried first and abandoned: on a realisable pattern (positive control)
  it did not finish in 600 s, and no verdict anywhere relies on it.

  weak96 <out.json>                        write the 96 patterns
  gen <patterns.json> <dir>                write <dir>/<i>.sing, one per pattern (index in the file)
  genfull <patterns.json> <dir> <singular.json>   the same with u, w, for that run's non-unit ones
  run <dir> <jobs> <timeout_s>             run them in the Docker container cas98; <dir>/singular.json
  post <dir> <timeout_s> [i ...]           dimension, lex basis, msolve; <dir>/post.json
  z3 <patterns.json> <dir> <timeout_s>     z3 on every NON-unit pattern; <dir>/z3.json (not used)
The number of points is SING98_N (default 5).  Pattern files may use the key 'patterns' or
'candidates' (the exposure98.py outputs).
Container: docker run -d --name cas98 --cpus 10 -v "<p98>:/work" erdos831-cas sleep infinity
"""
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations

N = int(os.environ.get('SING98_N', '5'))     # number of points; SING98_N=7 for the n = 7 candidates
CONTAINER = 'cas98'
PAIRS = list(combinations(range(N), 2))


def weak96(out):
    gap = json.load(open('z3_gap_n5k4.json'))
    triv = {tuple(p) for p in json.load(open('gap_trivial.json'))['trivial_ideal']}
    oc = json.load(open('ordercheck_out.json'))['results']
    res = json.load(open('z3_residual.json'))
    all153 = set(map(tuple, gap['unsat'])) | set(map(tuple, gap['unknown']))
    settled = triv | {tuple(r['pattern']) for r in oc if r['verdict'] == 'unsat'}
    weak = {tuple(r['pattern']) for r in oc if r['verdict'] != 'unsat'} | set(map(tuple, res['unknown']))
    assert len(all153) == 153 and len(settled) == 57 and len(weak) == 96
    assert not (weak & settled) and (weak | settled) == all153
    json.dump({'patterns': [list(p) for p in sorted(weak)]}, open(out, 'w'), indent=1)
    print('wrote 96 patterns to', out)


def names(k, full=False):
    return (['t'] + (['u', 'w'] if full else []) + ['x%d' % i for i in range(2, N)]
            + ['y%d' % i for i in range(2, N)] + ['d%d' % c for c in range(k)])


def nondegeneracy():
    """products of the 10 triple orientations and of the 5 concyclicity determinants, as
    Singular strings; both are non-zero in general position"""
    import sympy as sp
    X = [0, 1] + [sp.Symbol('x%d' % i) for i in range(2, N)]
    Y = [0, 0] + [sp.Symbol('y%d' % i) for i in range(2, N)]
    tri = [(X[b] - X[a]) * (Y[c] - Y[a]) - (X[c] - X[a]) * (Y[b] - Y[a]) for a, b, c in combinations(range(N), 3)]
    dets = [sp.Matrix([[X[u] ** 2 + Y[u] ** 2, X[u], Y[u], 1] for u in q]).det() for q in combinations(range(N), 4)]
    f = lambda e: '(' + str(sp.expand(e)).replace('**', '^') + ')'
    return '*'.join(f(e) for e in tri), '*'.join(f(e) for e in dets)


def coords(i):
    return ('0', '0') if i == 0 else (('1', '0') if i == 1 else ('x%d' % i, 'y%d' % i))


def polys(pat, full=False):
    k = max(pat) + 1
    out = []
    for (i, j), c in zip(PAIRS, pat):
        (xi, yi), (xj, yj) = coords(i), coords(j)
        out.append('(%s-(%s))^2+(%s-(%s))^2-d%d' % (xi, xj, yi, yj, c))
    out.append('d%d-1' % pat[0])
    prod = '*'.join(['(d%d-d%d)' % (a, b) for a, b in combinations(range(k), 2)] + ['d%d' % c for c in range(k)])
    out.append('t*%s-1' % prod)
    if full:
        tri, det = nondegeneracy()
        out.append('u*%s-1' % tri)
        out.append('w*%s-1' % det)
    return out, k


def gen(patfile, d, full=False, only=None):
    data = json.load(open(patfile))
    pats = data['patterns'] if 'patterns' in data else data['candidates']
    os.makedirs(d, exist_ok=True)
    for i, pat in enumerate(pats):
        if only is not None and i not in only:
            continue
        ps, k = polys(pat, full)
        txt = ('ring R = 0, (%s), dp;\nideal I =\n  %s;\nideal G = slimgb(I);\n'
               'if (reduce(poly(1), G) == 0) { print("RESULT UNIT"); }\n'
               'else { print("RESULT NONUNIT " + string(size(G))); write(":w /work/%s/%d.gb", G); }\n'
               'quit;\n') % (','.join(names(k, full)), ',\n  '.join(ps), d, i)
        open(os.path.join(d, '%d.sing' % i), 'w', newline='\n').write(txt)
    print('wrote %d files to %s' % (len(pats), d))


def run(d, jobs, timeout_s):
    files = sorted((f for f in os.listdir(d) if f.endswith('.sing')), key=lambda f: int(f[:-5]))
    resf = os.path.join(d, 'singular.json')
    res = json.load(open(resf)) if os.path.exists(resf) else {}
    import threading
    lock = threading.Lock()

    def one(f):
        key = f[:-5]
        if key in res and res[key]['status'] in ('UNIT', 'NONUNIT'):
            return
        t = time.time()
        cmd = 'cd /work && timeout %d Singular -q %s/%s' % (timeout_s, d, f)
        p = subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-c', cmd], capture_output=True, text=True)
        out = p.stdout + p.stderr
        st = ('UNIT' if 'RESULT UNIT' in out else 'NONUNIT' if 'RESULT NONUNIT' in out
              else 'TIMEOUT' if p.returncode == 124 else 'ERROR rc=%d %s' % (p.returncode, out.strip()[-120:]))
        with lock:
            res[key] = {'status': st, 'seconds': round(time.time() - t, 1)}
            json.dump(res, open(resf, 'w'), indent=1)
        print(key, st, round(time.time() - t, 1), flush=True)

    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(one, files))
    from collections import Counter
    print('SINGULAR DONE', dict(Counter(r['status'].split()[0] for r in res.values())))


def z3_one(patfile, d, i):
    import sympy as sp
    import z3
    pat = json.load(open(patfile))['patterns'][i]
    k = max(pat) + 1
    V = {v: z3.Real(v) for v in names(k)}
    loc = {v: sp.Symbol(v) for v in names(k)}

    def conv(e):
        e = sp.expand(e)
        if e.is_Add:
            return sum(conv(a) for a in e.args)
        if e.is_Mul:
            r = 1
            for a in e.args:
                r = r * conv(a)
            return r
        if e.is_Pow:
            return conv(e.base) ** int(e.exp)
        if e.is_Rational:
            return z3.RealVal(sp.Rational(e))
        if e.is_Symbol:
            return V[str(e)]
        raise ValueError(str(e))

    ps, _ = polys(pat)
    gb = [p for p in open(os.path.join(d, '%d.gb' % i)).read().split(',') if p.strip()]
    s = z3.Solver()
    for p in ps + gb:
        s.add(conv(sp.sympify(p.replace('^', '**'), locals=loc)) == 0)
    for c in range(k):
        s.add(V['d%d' % c] > 0)
    X = [z3.RealVal(0), z3.RealVal(1)] + [V['x%d' % i] for i in range(2, N)]
    Y = [z3.RealVal(0), z3.RealVal(0)] + [V['y%d' % i] for i in range(2, N)]
    tri = lambda a, b, c: (X[b] - X[a]) * (Y[c] - Y[a]) - (X[c] - X[a]) * (Y[b] - Y[a])
    for a, b, c in combinations(range(N), 3):
        s.add(tri(a, b, c) != 0)

    def det4(m):
        def det3(a):
            return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1]) - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
                    + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))
        tot = 0
        for c in range(4):
            minor = [[m[r][cc] for cc in range(4) if cc != c] for r in range(1, 4)]
            tot = tot + m[0][c] * det3(minor) if c % 2 == 0 else tot - m[0][c] * det3(minor)
        return tot

    for q in combinations(range(N), 4):
        s.add(det4([[X[u] ** 2 + Y[u] ** 2, X[u], Y[u], 1] for u in q]) != 0)
    r = s.check()
    out = {'verdict': str(r)}
    if r == z3.sat:
        m = s.model()
        out['points'] = [[str(m.eval(X[u], model_completion=True)), str(m.eval(Y[u], model_completion=True))] for u in range(N)]
    print(json.dumps(out), flush=True)


def z3_all(patfile, d, timeout_s):
    sing = json.load(open(os.path.join(d, 'singular.json')))
    resf = os.path.join(d, 'z3.json')
    res = json.load(open(resf)) if os.path.exists(resf) else {}
    for key in sorted(sing, key=int):
        if sing[key]['status'] != 'NONUNIT' or key in res:
            continue
        t = time.time()
        try:
            p = subprocess.run([sys.executable, os.path.abspath(__file__), 'z3one', patfile, d, key],
                               capture_output=True, text=True, timeout=timeout_s)
            line = [x for x in p.stdout.splitlines() if x.startswith('{')]
            v = json.loads(line[-1]) if line else {'verdict': 'ERROR', 'msg': (p.stderr or '')[-200:]}
        except subprocess.TimeoutExpired:
            v = {'verdict': 'TIMEOUT'}
        v['seconds'] = round(time.time() - t, 1)
        res[key] = v
        json.dump(res, open(resf, 'w'), indent=1)
        print(key, v['verdict'], v['seconds'], flush=True)


def post(d, timeout_s, keys=None):
    """For every NON-unit system in <dir>/singular.json (or the given keys): Singular std with
    dim and vdim (<i>.dim.sing -> <i>.std), the lex basis by fglm (<i>.lex.sing -> <i>.lex), and,
    when zero-dimensional, msolve on the std basis (<i>.ms -> <i>.ms.out).  Results in
    <dir>/post.json.  Positive-dimensional systems are reported and left for other methods."""
    import re
    sing = json.load(open(os.path.join(d, 'singular.json')))
    keys = keys or sorted((k for k, v in sing.items() if v['status'] == 'NONUNIT'), key=int)
    resf = os.path.join(d, 'post.json')
    res = json.load(open(resf)) if os.path.exists(resf) else {}

    def sing_run(f):
        cmd = 'cd /work && timeout %d Singular -q %s/%s' % (timeout_s, d, f)
        p = subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-c', cmd], capture_output=True, text=True)
        return (p.stdout + p.stderr).strip()

    for key in keys:
        src = open(os.path.join(d, '%s.sing' % key)).read()
        ring = re.search(r'ring R = 0, \((.*?)\), dp;', src).group(1)
        ideal = src.split('ideal I =', 1)[1].split(';', 1)[0]
        head = 'option(redSB);\nring R = 0, (%s), dp;\nideal I =%s;\nideal G = std(I);\n' % (ring, ideal)
        open(os.path.join(d, '%s.dim.sing' % key), 'w', newline='\n').write(
            head + 'print("DIM " + string(dim(G)) + " VDIM " + string(vdim(G)));\n'
                   'write(":w /work/%s/%s.std", G);\nquit;\n' % (d, key))
        out = sing_run('%s.dim.sing' % key)
        m = re.search(r'DIM (-?\d+) VDIM (-?\d+)', out)
        r = {'dim': int(m.group(1)), 'vdim': int(m.group(2))} if m else {'error': out[-200:]}
        if m and r['dim'] == 0:
            open(os.path.join(d, '%s.lex.sing' % key), 'w', newline='\n').write(
                head + 'ring S = 0, (%s), lp;\nideal J = fglm(R, G);\nwrite(":w /work/%s/%s.lex", J);\n'
                       'print("LEX " + string(size(J)));\nquit;\n' % (ring, d, key))
            r['lex'] = sing_run('%s.lex.sing' % key)[-40:]
            polys = [p.strip() for p in open(os.path.join(d, '%s.std' % key)).read().split(',') if p.strip()]
            open(os.path.join(d, '%s.ms' % key), 'w', newline='\n').write(ring + '\n0\n' + ',\n'.join(polys) + '\n')
            cmd = 'cd /work && timeout %d msolve -f %s/%s.ms -o %s/%s.ms.out' % (timeout_s, d, key, d, key)
            subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-c', cmd], capture_output=True, text=True)
            ms = open(os.path.join(d, '%s.ms.out' % key)).read()
            r['msolve_real_solutions'] = 'none' if re.match(r'\[0,\s*\[1,\s*\[\s*\]\s*\]\]', ms.strip()) else 'some'
        res[key] = r
        json.dump(res, open(resf, 'w'), indent=1)
        print(key, r, flush=True)


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'post':
        post(sys.argv[2], int(sys.argv[3]), sys.argv[4:] or None)
        sys.exit()
    if c == 'weak96':
        weak96(sys.argv[2])
    elif c == 'gen':
        gen(sys.argv[2], sys.argv[3])
    elif c == 'genfull':
        # genfull <patterns.json> <dir> <singular.json of the plain run>: only that run's NON-unit
        # patterns, with no three collinear and no four concyclic also imposed (variables u, w)
        plain = json.load(open(sys.argv[4]))
        gen(sys.argv[2], sys.argv[3], True, {int(k) for k, v in plain.items() if v['status'] == 'NONUNIT'})
    elif c == 'run':
        run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif c == 'z3':
        z3_all(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    elif c == 'z3one':
        z3_one(sys.argv[2], sys.argv[3], int(sys.argv[4]))
