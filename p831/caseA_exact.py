"""Case A of n = 5, decided exactly.  Replaces the numerical evidence of caseA2.py.

CASE A.  Four of the five points carry four equal circumradii, so by Lemma 2 they are an
orthocentric system {A,B,C,H}, and by Lemma 3 their class is exactly those four triples.
The other six triples all contain the fifth point P and, for h(5) = 3, fall into exactly
two radius classes.  Lemma 1 caps each class at degree 2 at every one of A,B,C,H, and
that alone leaves nine splits: three of shape (4,2) and six of shape (3,3).  (The size
filter caseA2.py also applies, via f(5) = 4, removes nothing further; checked below.)

THE ALGEBRA.  For a triangle XYZ with squared sides a2, b2, c2 and cross product
K = (Y-X) x (Z-X), the squared circumradius rho satisfies a2*b2*c2 = 4*rho*K^2.  Each of
the six P-triples gets that equation with rho = ra or rb according to its class, which
makes each split a square polynomial system.  If K = 0 the equation forces a2*b2*c2 = 0,
so a collinear triple of DISTINCT points can never satisfy it.

WHAT IS SATURATED AWAY.  Every real admissible solution has all of these non-zero, so
removing the locus where one of them vanishes loses nothing:
  - the squared distances between the five points (the points are distinct);
  - the cross product of ABC (a genuine triangle, so the orthocentre H exists);
  - ra - rb (the two P-classes are different classes);
  - 4*ra*K_ABC^2 - N_ABC and the same for rb, i.e. ra and rb differ from R^2, the
    common squared circumradius of the orthocentric four.
Nothing admissible is missing from that list.  The orthocentric four are never
concyclic (H is on the circumcircle of ABC only when it is a vertex) and no three of them
are collinear once they are distinct (H on line AB forces H = A or H = B).  So four
concyclic points must be P and three of A,B,C,H; the three P-triples on those three
points then have radius R, and one of ra, rb equals R^2.  Hence every real point of the
saturated system is an admissible 5-point set with exactly three circumradii, and a split
is refuted exactly when the saturated system has no real point.

TWO GAUGES, TWO ENGINES.
  F1: A=(0,0), B=(1,0), C=(u,v), H=(u,w) with v*w = u*(1-u)   (caseA2's gauge)
  F2: P=(0,0), A=(1,0), B=(p,q), C=(r,s), H=(m,n), orthocentre by two dot products
Any labelled configuration can be moved into either gauge by a similarity, so each gauge
covers Case A completely on its own.
  Singular saturates by each irreducible factor in turn and reports dim and vdim.
  msolve gets the system plus one Rabinowitsch variable per factor (t*g - 1 = 0) and
  isolates the real roots with certified boxes.  A real root there IS an admissible
  configuration, because t = 1/g is then real and finite.

CONTROL.  A planted rational configuration: the same pipeline with four radius equations
pinned to the planted values must return the planted point.

HOW IT WENT, AND WHY THERE ARE SO MANY SUBCOMMANDS.  msolve decides every full split
quickly, but its "no solution" rests on a Groebner basis modulo one prime, so it is not a
proof.  Singular over Q on the full systems (13 Rabinowitsch variables) ran for hours
without finishing.  The fix was to saturate by FEWER factors: a unit ideal with only some
of the non-degeneracy conditions imposed still refutes the split, and is much cheaper.
Which factors to keep is chosen modulo a prime (genscreen, greedy); the exact decision is
then made over Q on the smaller system (genreduced, gencand).  That decided the six 3+3
splits; every exact run on a 4+2 split was stopped unfinished, and those rest on Lemmas 5
and 6.  A certificate by explicit cofactors, to be checked with python-flint (genlift,
certcheck), was attempted for split 4 and stopped unfinished at its two-hour budget, so no
certificate exists and the proof rests on Singular's computation (NOTE.md section 5a).
(2026-09-16: this paragraph used to say the decision was "certified by explicit cofactors".)

Usage:
  python caseA_exact.py gen                    all systems, both gauges, plus controls
  python caseA_exact.py genrab | genplant | genscreen | gencand
  python caseA_exact.py genreduced K GAUGE KEEP     split K keeping factor indices KEEP
  python caseA_exact.py greedy K GAUGE ORDER        mod-p screen for a small KEEP
  python caseA_exact.py genlift NAME | certcheck NAME
  python caseA_exact.py xcheck                 encoding against caseA2.py's near-solutions
  python caseA_exact.py run ENGINE GAUGE JOBS [THREADS] [TIMEOUT]
      ENGINE msolve | singular | singrab | singstd | singlift;  GAUGE F1 | F2
      JOBS split numbers (3,4) or job suffixes (control, red4, cand1, pin4, ...)
Runs inside the container cas831 (see docker/Dockerfile and REPRODUCE.md).
"""
import io
import json
import os
import re
import subprocess
import sys
import time
from fractions import Fraction
from itertools import combinations

import sympy as sp

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CONTAINER = 'cas831'
EXD = 'exact'
LOG = os.path.join('logs', 'caseA_exact.log')
PAIRS = list(combinations(range(4), 2))          # pairs of {A,B,C,H}; triple = pair + P


def log(msg):
    line = time.strftime('%Y-%m-%d %H:%M:%S ') + msg
    print(line, flush=True)
    with io.open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


# ---------------------------------------------------------------- the nine splits
def splits():
    """two-class partitions of the six P-triples with degree <= 2 at each of A,B,C,H"""
    out, seen = [], set()
    for mask in range(1, 1 << 6):
        c0 = [i for i in range(6) if mask >> i & 1]
        c1 = [i for i in range(6) if not mask >> i & 1]
        if not c1:
            continue
        key = tuple(sorted([tuple(c0), tuple(c1)]))
        if key in seen:
            continue
        seen.add(key)
        ok = all(sum(1 for t in cl if X in PAIRS[t]) <= 2 for X in range(4) for cl in (c0, c1))
        if ok:
            out.append((c0, c1))
    return out


def check_splits():
    S = splits()
    sizes = sorted(tuple(sorted((len(a), len(b)), reverse=True)) for a, b in S)
    assert len(S) == 9 and sizes == [(3, 3)] * 6 + [(4, 2)] * 3, sizes
    import caseA2                                  # the numerical run's own list
    theirs = {tuple(sorted([tuple(a), tuple(b)])) for a, b in caseA2.splits()}
    mine = {tuple(sorted([tuple(a), tuple(b)])) for a, b in S}
    assert theirs == mine, 'split lists differ from caseA2.py'
    return S


# ---------------------------------------------------------------- geometry
def d2(P, Q):
    return (P[0] - Q[0]) ** 2 + (P[1] - Q[1]) ** 2


def cr(P, Q, R):
    return (Q[0] - P[0]) * (R[1] - P[1]) - (Q[1] - P[1]) * (R[0] - P[0])


def rad_eq(X, Y, Z, rho):
    return sp.expand(d2(Y, Z) * d2(Z, X) * d2(X, Y) - 4 * rho * cr(X, Y, Z) ** 2)


def dot(P, Q):
    return P[0] * Q[0] + P[1] * Q[1]


def sub(P, Q):
    return (P[0] - Q[0], P[1] - Q[1])


def gauge(g):
    """returns ([A,B,C,H], P, orthocentre equations, coordinate symbols)"""
    if g == 'F1':
        u, v, w, x, y = sp.symbols('u v w x y')
        return [(0, 0), (1, 0), (u, v), (u, w)], (x, y), [v * w - u * (1 - u)], [u, v, w, x, y]
    if g == 'F2':
        p, q, r, s, m, n = sp.symbols('p q r s m n')
        A, B, C, H = (1, 0), (p, q), (r, s), (m, n)
        orth = [sp.expand(dot(sub(H, A), sub(B, C))), sp.expand(dot(sub(H, B), sub(A, C)))]
        return [A, B, C, H], (0, 0), orth, [p, q, r, s, m, n]
    raise ValueError(g)


def factors(polys, vs):
    """distinct non-constant irreducible factors over Q, sign-normalised"""
    out = {}
    for g in polys:
        g = sp.expand(g)
        if not g.free_symbols:
            assert g != 0
            continue
        for f, _ in sp.factor_list(g, *vs)[1]:
            P = sp.Poly(f, *vs)
            if P.LC() < 0:
                P = -P
            out[str(P.as_expr())] = P.as_expr()
    return list(out.values())


def split_system(g, c0, c1):
    Q, P, orth, co = gauge(g)
    ra, rb = sp.symbols('ra rb')
    vs = co + [ra, rb]
    eqs = list(orth) + [rad_eq(P, Q[i], Q[j], ra if t in c0 else rb)
                        for t, (i, j) in enumerate(PAIRS)]
    A, B, C = Q[0], Q[1], Q[2]
    K, N = cr(A, B, C), d2(B, C) * d2(C, A) * d2(A, B)
    sat = [d2(X, Y) for X, Y in combinations(Q + [P], 2)]
    sat += [K, ra - rb, 4 * ra * K ** 2 - N, 4 * rb * K ** 2 - N]
    return eqs, factors(sat, vs), vs


# a planted configuration, in F1 coordinates: C = (1/3, 2/3), so H = (1/3, 1/3)
PLANT_F1 = dict(u=Fraction(1, 3), v=Fraction(2, 3), w=Fraction(1, 3),
                x=Fraction(7, 5), y=Fraction(9, 10))


def plant(g):
    """the planted point in gauge g, as {symbol name: Fraction}"""
    p = PLANT_F1
    if g == 'F1':
        return dict(p)
    # the similarity z -> (z - P)/(A - P) sends P to 0 and A = 0 to 1
    Pz = complex_frac(p['x'], p['y'])
    pts = dict(B=(Fraction(1), Fraction(0)), C=(p['u'], p['v']), H=(p['u'], p['w']))
    img = {k: cdiv(csub(val, Pz), csub((Fraction(0), Fraction(0)), Pz)) for k, val in pts.items()}
    return dict(p=img['B'][0], q=img['B'][1], r=img['C'][0], s=img['C'][1],
                m=img['H'][0], n=img['H'][1])


def complex_frac(a, b):
    return (Fraction(a), Fraction(b))


def csub(z, w):
    return (z[0] - w[0], z[1] - w[1])


def cdiv(z, w):
    den = w[0] ** 2 + w[1] ** 2
    return ((z[0] * w[0] + z[1] * w[1]) / den, (z[1] * w[0] - z[0] * w[1]) / den)


def control_system(g):
    Q, P, orth, co = gauge(g)
    pt = {sp.Symbol(k): sp.Rational(v.numerator, v.denominator) for k, v in plant(g).items()}
    for e in orth:
        assert sp.expand(e.subs(pt)) == 0, 'planted point is not orthocentric'
    eqs = list(orth)
    for i, j in PAIRS[:4]:
        X, Y, Z = P, Q[i], Q[j]
        K = sp.expand(sp.sympify(cr(X, Y, Z)).subs(pt))
        assert K != 0
        rho = sp.expand(sp.sympify(d2(Y, Z) * d2(Z, X) * d2(X, Y)).subs(pt)) / (4 * K ** 2)
        eqs.append(rad_eq(X, Y, Z, rho))
    A, B, C = Q[0], Q[1], Q[2]
    sat = [d2(X, Y) for X, Y in combinations(Q + [P], 2)] + [cr(A, B, C)]
    for f in sat:
        assert sp.expand(sp.sympify(f).subs(pt)) != 0, 'planted point is degenerate'
    return eqs, factors(sat, co), co, pt


# ---------------------------------------------------------------- file writers
def pstr(e, vs):
    P = sp.Poly(sp.expand(e), *vs)
    _, P = P.clear_denoms(convert=True)
    out = []
    for mon, c in P.terms():
        c = int(c)
        m = '*'.join(('%s^%d' % (v, k)) if k > 1 else str(v) for v, k in zip(vs, mon) if k)
        body = str(abs(c)) if not m else (('' if abs(c) == 1 else '%d*' % abs(c)) + m)
        out.append(('-' if c < 0 else '+') + body)
    s = ''.join(out)
    return s[1:] if s.startswith('+') else s


def write_msolve(name, eqs, fac, vs):
    """msolve eliminates towards its LAST variable, and quits or loops when that variable
    does not separate the solutions.  The gauges are symmetric under reflection in the
    x-axis, so several of the variables take each value twice.  A last variable equal to
    a fixed random linear form in the coordinates separates them (and is checked: msolve
    reports a non-squarefree eliminant otherwise)."""
    ts = [sp.Symbol('t%d' % (k + 1)) for k in range(len(fac))]
    z = sp.Symbol('zsep')
    allv = vs + ts + [z]
    rnd = __import__('random').Random(831)
    lin = z - sum(rnd.randint(1, 97) * v for v in vs)
    polys = [pstr(e, allv) for e in eqs] + [pstr(t * f - 1, allv) for t, f in zip(ts, fac)]
    polys.append(pstr(lin, allv))
    with io.open(os.path.join(EXD, name + '.ms'), 'w', encoding='ascii', newline='\n') as fh:
        fh.write(','.join(map(str, allv)) + '\n0\n' + ',\n'.join(polys) + '\n')
    return [str(v) for v in allv]


def write_singular(name, eqs, fac, vs):
    polys = ',\n  '.join(pstr(e, vs) for e in eqs)
    gens = ',\n  '.join(pstr(f, vs) for f in fac)
    txt = '''// generated by caseA_exact.py; do not edit
LIB "elim.lib";
option(redSB);
ring R = 0, (%s), dp;
ideal I = %s;
ideal G = %s;
I = std(I);
int k;
for (k = 1; k <= ncols(G); k++)
{
  def S = sat(I, G[k]);
  if (typeof(S) == "list") { I = S[1]; } else { I = S; }
  kill S;
  I = std(I);
  print("STEP " + string(k) + " of " + string(ncols(G)) + " dim " + string(dim(I)));
}
print("RESULT dim " + string(dim(I)));
print("RESULT vdim " + string(vdim(I)));
print("RESULT size " + string(size(I)));
write(":w /work/%s/%s.sat", I);
if (dim(I) == 0)
{
  LIB "primdec.lib";
  ideal Jr = std(radical(I));
  print("RESULT radvdim " + string(vdim(Jr)));
}
quit;
''' % (','.join(map(str, vs)), polys, gens, EXD, name)
    with io.open(os.path.join(EXD, name + '.sing'), 'w', encoding='ascii', newline='\n') as fh:
        fh.write(txt)


def write_singular_rab(name, eqs, fac, vs):
    """The same Rabinowitsch system msolve gets (without its separating variable), for an
    exact Groebner basis over Q.  msolve decides 'no solution' from a Groebner basis modulo
    a prime, which is correct with overwhelming probability but is not a proof: a prime
    dividing the right denominators could turn a consistent system into {1}.  Singular's
    slimgb over Q has no such failure mode, so a unit ideal here is a proof."""
    ts = [sp.Symbol('t%d' % (k + 1)) for k in range(len(fac))]
    allv = vs + ts
    polys = ',\n  '.join([pstr(e, allv) for e in eqs] +
                         [pstr(t * f - 1, allv) for t, f in zip(ts, fac)])
    txt = '''// generated by caseA_exact.py; do not edit
option(prot);
ring R = 0, (%s), dp;
ideal I = %s;
ideal G = slimgb(I);
print("RESULT dim " + string(dim(G)));
if (dim(G) == -1) { print("RESULT unit 1"); } else { print("RESULT unit 0"); }
quit;
''' % (','.join(map(str, allv)), polys)
    with io.open(os.path.join(EXD, name + '.rab.sing'), 'w', encoding='ascii',
                 newline='\n') as fh:
        fh.write(txt)


def genrab():
    S = check_splits()
    for g in ('F1', 'F2'):
        for k, (c0, c1) in enumerate(S):
            eqs, fac, vs = split_system(g, c0, c1)
            write_singular_rab('%s_split%d' % (g, k), eqs, fac, vs)
    log('genrab: wrote %d exact-over-Q Singular inputs' % (2 * len(S)))


def xcheck():
    """The encoding against caseA2.py's own near-solutions: at each of its best points
    the split's equations must be small (they are its equations, up to normalisation) and
    every saturated factor must be clearly non-zero (its guards held there)."""
    r = json.load(open(os.path.join('results', 'caseA2.json')))
    import caseA2
    import numpy as np
    for row in r['results']:
        c0, c1 = row['split']
        cx, cy, px, py = row['v']
        rad = caseA2.six_radii(np.array(row['v']))[0]
        eqs, fac, vs = split_system('F1', c0, c1)
        val = {sp.Symbol('u'): cx, sp.Symbol('v'): cy, sp.Symbol('w'): cx * (1 - cx) / cy,
               sp.Symbol('x'): px, sp.Symbol('y'): py,
               sp.Symbol('ra'): float(np.mean(rad[c0])), sp.Symbol('rb'): float(np.mean(rad[c1]))}
        Q, P, _, _ = gauge('F1')
        rel = [abs(float(eqs[0].subs(val)))]
        for t, (i, j) in enumerate(PAIRS):
            N = float(sp.sympify(d2(Q[i], Q[j]) * d2(Q[j], P) * d2(P, Q[i])).subs(val))
            rel.append(abs(float(eqs[1 + t].subs(val))) / N)
        fmin = min(abs(float(f.subs(val))) for f in fac)
        log('xcheck split %s|%s: caseA2 residual %.2e, max relative equation %.2e, '
            'min |factor| %.2e' % (c0, c1, row['best'], max(rel), fmin))


def gen():
    os.makedirs(EXD, exist_ok=True)
    S = check_splits()
    man = dict(splits=[[a, b] for a, b in S], jobs={})
    for g in ('F1', 'F2'):
        eqs, fac, vs, pt = control_system(g)
        name = '%s_control' % g
        allv = write_msolve(name, eqs, fac, vs)
        write_singular(name, eqs, fac, vs)
        man['jobs'][name] = dict(gauge=g, vars=allv, nvars=len(vs), nfactors=len(fac),
                                 planted={str(k): str(v) for k, v in pt.items()})
        for k, (c0, c1) in enumerate(S):
            eqs, fac, vs = split_system(g, c0, c1)
            name = '%s_split%d' % (g, k)
            allv = write_msolve(name, eqs, fac, vs)
            write_singular(name, eqs, fac, vs)
            man['jobs'][name] = dict(gauge=g, split=[c0, c1], vars=allv, nvars=len(vs),
                                     nfactors=len(fac),
                                     maxdeg=max(sp.Poly(e, *vs).total_degree() for e in eqs))
    json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    log('gen: wrote %d jobs to %s/' % (len(man['jobs']), EXD))


# ---------------------------------------------------------------- running and parsing
def parse_msolve(text):
    t = text.strip().rstrip(':').strip()
    if t.startswith('[-1]'):
        return 'no complex solution', []
    if t.startswith('[1,'):
        return 'positive dimensional', None
    assert t.startswith('[0,'), t[:80]
    lit = re.sub(r'(-?\d+)\s*/\s*2\^(\d+)', r'Fraction(\1, 2**\2)', t)
    obj = eval(lit, {'__builtins__': {}}, {'Fraction': Fraction})
    boxes = obj[1][1]
    return ('real solutions' if boxes else 'no real solution'), boxes


def run(engine, g, jobs, threads=7, tmo=3600):
    man = json.load(open(os.path.join(EXD, 'manifest.json')))
    resf = os.path.join('results', 'caseA_exact_%s.json' % engine)
    res = json.load(open(resf)) if os.path.exists(resf) else {}
    for j in jobs:
        name = '%s_%s' % (g, 'split%d' % int(j) if j.isdigit() else j)
        job = man['jobs'][name]
        if engine == 'msolve':
            cmd = ['timeout', '-s', 'KILL', str(tmo), 'msolve', '-t', str(threads), '-v', '2',
                   '-f', '/work/%s/%s.ms' % (EXD, name), '-o', '/work/%s/%s.ms.out' % (EXD, name)]
        else:
            # singrab: slimgb on the Rabinowitsch system; singstd: the same system with
            # Singular's plain std, a second algorithm racing the first
            ext = {'singrab': '.rab.sing', 'singstd': '.std.sing',
                   'singlift': '.lift.sing'}.get(engine, '.sing')
            cmd = ['timeout', '-s', 'KILL', str(tmo), 'Singular', '-q',
                   '/work/%s/%s%s' % (EXD, name, ext)]
        # progress is streamed to exact/<job>.<engine>.live while the job runs; Singular
        # buffers a pipe, so it gets a pseudo-terminal from `script` instead
        live = '%s/%s.%s.live' % (EXD, name, engine)
        log('%s %s: start (timeout %d s, threads %s); progress in %s'
            % (engine, name, tmo, threads if engine == 'msolve' else 1, live))
        t0 = time.time()
        inner = ' '.join(cmd)
        if engine != 'msolve':
            inner = "script -qfec '%s' /dev/null" % inner
        p = subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-c',
                            'stdbuf -oL -eL %s > /work/%s 2>&1' % (inner, live)],
                           capture_output=True, text=True)
        dt = time.time() - t0
        rec = dict(engine=engine, job=name, seconds=round(dt, 1), returncode=p.returncode,
                   cmd=' '.join(cmd))
        p.stdout = io.open(live, encoding='utf-8', errors='replace').read()
        if engine == 'msolve' and p.returncode == 0:
            rec['squarefree_eliminant'] = 'not squarefree' not in p.stdout
        if p.returncode != 0:
            rec['status'] = 'KILLED at timeout' if p.returncode in (124, 137) else 'ERROR'
        elif engine == 'msolve' and 'char' in job:
            t = io.open(os.path.join(EXD, name + '.ms.out')).read().strip()
            rec['status'] = ('no solution mod p' if t.startswith('[-1]') else
                             'positive dimensional mod p' if t.startswith('[1,') else
                             'finitely many solutions mod p')
        elif engine == 'msolve':
            status, boxes = parse_msolve(io.open(os.path.join(EXD, name + '.ms.out')).read())
            rec['status'] = status
            rec['n_real'] = None if boxes is None else len(boxes)
            if boxes:
                nv = job['nvars']
                rec['real_boxes_midpoints'] = [
                    [float((lo + hi) / 2) for lo, hi in b[:nv]] for b in boxes]
                if 'planted' in job:
                    pl = [Fraction(job['planted'][v]) for v in job['vars'][:nv]]
                    rec['planted_found'] = any(
                        all(lo <= c <= hi for (lo, hi), c in zip(b[:nv], pl)) for b in boxes)
        else:
            out = dict(re.findall(r'RESULT (\w+) (-?\d+)', p.stdout))
            rec.update({k: int(v) for k, v in out.items()})
            d = rec.get('dim')
            rec['status'] = ('no complex solution' if d == -1 else
                             'zero dimensional' if d == 0 else 'positive dimensional')
            if engine == 'singlift':
                rec['status'] = ('unit ideal, cofactors written' if rec.get('gsize') == 1
                                 and rec.get('g1', 0) != 0 else 'not the unit ideal')
            if 'planted' in job and d == 0:
                rec['planted_in_ideal'] = planted_in(name, job)
        # several runners can share one results file, so re-read it just before writing
        res = json.load(open(resf)) if os.path.exists(resf) else {}
        res[name] = rec
        json.dump(res, open(resf, 'w'), indent=1)     # after EVERY verdict
        log('%s %s: %s  (%.1f s)%s' % (engine, name, rec['status'], dt,
                                        '' if 'n_real' not in rec else '  real roots: %s'
                                        % rec['n_real']))


def planted_in(name, job):
    """does every generator of the saturated ideal vanish at the planted point?"""
    txt = io.open(os.path.join(EXD, name + '.sat')).read()
    vs = sp.symbols(job['vars'][:job['nvars']])
    pt = {sp.Symbol(k): sp.Rational(v) for k, v in job['planted'].items()}
    for gtxt in txt.replace('\n', '').split(','):
        if gtxt.strip() and sp.expand(sp.sympify(gtxt.replace('^', '**')).subs(pt)) != 0:
            return False
    return True


def genrelax(k=4):
    """Non-triviality control for the split systems themselves: split k with one of its
    six radius equations dropped has one unknown more than equations, so it should have
    solutions (a curve).  If msolve called one of these inconsistent too, the unit ideals
    above could be an artefact of the encoding (a saturated factor vanishing on the whole
    solution set, say) rather than a fact about the geometry."""
    S = check_splits()
    c0, c1 = S[k]
    man = json.load(open(os.path.join(EXD, 'manifest.json')))
    for g in ('F2',):
        eqs, fac, vs = split_system(g, c0, c1)
        nor = len(gauge(g)[2])
        for t in range(6):
            name = '%s_relax%d_d%d' % (g, k, t)
            keep = eqs[:nor] + [e for i, e in enumerate(eqs[nor:]) if i != t]
            allv = write_msolve(name, keep, fac, vs)
            man['jobs'][name] = dict(gauge=g, split=[c0, c1], dropped=t, vars=allv,
                                     nvars=len(vs), nfactors=len(fac))
    json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    log('genrelax: wrote 6 relaxed copies of split %d' % k)


def genhyp(k=4, g='F2', drops=(0, 5)):
    """Non-triviality control, zero-dimensional version.  Split k with one radius
    equation dropped is a curve; cutting it with a random hyperplane leaves finitely many
    points, which msolve handles as easily as the splits themselves (the curve itself
    drove F4 past 5 GB).  If the saturated factors killed everything, this would come
    back inconsistent like the splits; it must come back with solutions."""
    S = check_splits()
    c0, c1 = S[k]
    eqs, fac, vs = split_system(g, c0, c1)
    nor = len(gauge(g)[2])
    co = gauge(g)[3]
    rnd = __import__('random').Random(8310)
    man = json.load(open(os.path.join(EXD, 'manifest.json')))
    for t in drops:
        name = '%s_hyp%d_d%d' % (g, k, t)
        hyp = sum(rnd.randint(1, 97) * v for v in co) - rnd.randint(1, 97)
        keep = eqs[:nor] + [e for i, e in enumerate(eqs[nor:]) if i != t] + [hyp]
        allv = write_msolve(name, keep, fac, vs)
        path = os.path.join(EXD, name + '.ms')
        lines = io.open(path, encoding='ascii').read().split('\n')
        lines[1] = str(PRIME)
        io.open(path, 'w', encoding='ascii', newline='\n').write('\n'.join(lines))
        man['jobs'][name] = dict(gauge=g, split=[c0, c1], dropped=t, hyperplane=str(hyp),
                                 char=PRIME, vars=allv, nvars=len(vs), nfactors=len(fac))
    json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    log('genhyp: wrote %d hyperplane-section controls of %s split %d' % (len(drops), g, k))


def genplant(k=4):
    """Non-triviality control built from the split system itself.  Split k asks the three
    triples of each class to share one squared radius.  Here each triple T of class c gets
    N_T = 4 * lam_T * rho_c * K_T^2 instead, with rational lam_T chosen so that the planted
    configuration solves it exactly (lam = 1 on the first triple of each class).  The
    variables, degrees and the whole saturated-factor list are those of split k, so if the
    saturation or the encoding killed genuine solutions this system would come back
    inconsistent too.  It must come back with real solutions, the planted one among them."""
    S = check_splits()
    c0, c1 = S[k]
    man = json.load(open(os.path.join(EXD, 'manifest.json')))
    for g in ('F2', 'F1'):
        Q, P, orth, co = gauge(g)
        ra, rb = sp.symbols('ra rb')
        vs = co + [ra, rb]
        pt = {sp.Symbol(a): sp.Rational(b.numerator, b.denominator) for a, b in plant(g).items()}
        rho = []
        for i, j in PAIRS:
            K = sp.expand(sp.sympify(cr(P, Q[i], Q[j])).subs(pt))
            N = sp.expand(sp.sympify(d2(Q[i], Q[j]) * d2(Q[j], P) * d2(P, Q[i])).subs(pt))
            assert K != 0
            rho.append(N / (4 * K ** 2))
        base = {0: rho[c0[0]], 1: rho[c1[0]]}
        eqs = list(orth)
        for t, (i, j) in enumerate(PAIRS):
            c = 0 if t in c0 else 1
            lam = rho[t] / base[c]
            X, Y, Z = P, Q[i], Q[j]
            eqs.append(sp.expand(d2(Y, Z) * d2(Z, X) * d2(X, Y)
                                 - 4 * lam * (ra if c == 0 else rb) * cr(X, Y, Z) ** 2))
        _, fac, _ = split_system(g, c0, c1)
        full = dict(pt)
        full[ra], full[rb] = base[0], base[1]
        for e in eqs:
            assert sp.expand(e.subs(full)) == 0, 'planted point does not solve the system'
        for f in fac:
            assert sp.expand(f.subs(full)) != 0, 'planted point is degenerate: %s' % f
        name = '%s_plant%d' % (g, k)
        allv = write_msolve(name, eqs, fac, vs)
        # the pinned copy: the same system with the two free coordinates of the triangle
        # fixed at their planted values.  It keeps every equation and every saturated
        # factor of split k, but has only a handful of solutions, where the full planted
        # system has so many that F4 needed over 9 GB.
        pin = [v - full[v] for v in co[:2]] if g == 'F1' else [v - full[v] for v in co[:4]]
        write_msolve('%s_pin%d' % (g, k), eqs + pin, fac, vs)
        man['jobs']['%s_pin%d' % (g, k)] = dict(gauge=g, split=[c0, c1], vars=allv,
                                                nvars=len(vs), nfactors=len(fac),
                                                pinned=[str(v) for v in pin],
                                                planted={str(a): str(b) for a, b in full.items()})
        man['jobs'][name] = dict(gauge=g, split=[c0, c1], vars=allv, nvars=len(vs),
                                 nfactors=len(fac),
                                 planted={str(a): str(b) for a, b in full.items()})
    json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    log('genplant: wrote planted copies of split %d in F1 and F2' % k)


def cand_indices(k, g):
    """positions of gencand's factors inside split_system's full factor list"""
    S = check_splits()
    c0, c1 = S[k]
    _, fac, vs = split_system(g, c0, c1)
    names = [str(f) for f in fac]
    return [names.index(str(f)) for f in cand_factors(g, vs)]


def greedy(k=4, g='F2', order=None, threads=6, tmo=1800, start=None):
    """Drop saturated factors one at a time, keeping a drop only while the system stays
    inconsistent modulo PRIME.  Every factor passed the single-drop screen, but that says
    nothing about dropping several at once, hence the cumulative pass.  The outcome is only
    a choice of which smaller system to hand to the exact computation over Q; that
    computation, not this screen, is what proves anything."""
    S = check_splits()
    c0, c1 = S[k]
    eqs, fac, vs = split_system(g, c0, c1)
    keep = list(start) if start is not None else list(range(len(fac)))
    order = order if order is not None else list(keep)
    resf = os.path.join('results', 'caseA_exact_greedy_%s_%d.json' % (g, k))
    hist = []
    for j in order:
        trial = [i for i in keep if i != j]
        name = '%s_gr%d_%s' % (g, k, '_'.join(map(str, trial)) or 'none')
        write_msolve(name, eqs, [fac[i] for i in trial], vs)
        path = os.path.join(EXD, name + '.ms')
        lines = io.open(path, encoding='ascii').read().split('\n')
        lines[1] = str(PRIME)
        io.open(path, 'w', encoding='ascii', newline='\n').write('\n'.join(lines))
        cmd = 'timeout -s KILL %d msolve -t %d -f /work/%s/%s.ms -o /work/%s/%s.ms.out' % (
            tmo, threads, EXD, name, EXD, name)
        t0 = time.time()
        p = subprocess.run(['docker', 'exec', CONTAINER, 'bash', '-c', cmd],
                           capture_output=True, text=True)
        dt = time.time() - t0
        out = (io.open(path + '.out').read().strip()
               if p.returncode == 0 and os.path.exists(path + '.out') else '')
        unit = out.startswith('[-1]')
        if unit:
            keep = trial
        hist.append(dict(try_drop=j, factor=str(fac[j]), unit_mod_p=unit, seconds=round(dt, 1),
                         returncode=p.returncode, keep=list(keep)))
        json.dump(dict(gauge=g, split=k, prime=PRIME, factors=[str(f) for f in fac],
                       history=hist, keep=keep), open(resf, 'w'), indent=1)
        log('greedy %s split %d: drop factor %d -> %s (%.1f s); keeping %s'
            % (g, k, j, 'still no solution mod p, DROPPED' if unit else
               ('KILLED' if p.returncode else 'solutions appear, KEPT'), dt, keep))
    return keep


def genreduced(k, g, keep):
    """Split k with only the saturated factors in KEEP.  A unit ideal for this smaller
    system is still a complete refutation of the split: every admissible configuration
    has all thirteen factors non-zero, in particular the kept ones, so it would be a
    solution here.  Written for msolve (over Q) and for Singular's slimgb and std."""
    S = check_splits()
    c0, c1 = S[k]
    eqs, fac, vs = split_system(g, c0, c1)
    sub = [fac[i] for i in keep]
    name = '%s_red%d' % (g, k)
    allv = write_msolve(name, eqs, sub, vs)
    write_singular_rab(name, eqs, sub, vs)
    txt = io.open(os.path.join(EXD, name + '.rab.sing'), encoding='ascii').read()
    io.open(os.path.join(EXD, name + '.std.sing'), 'w', encoding='ascii', newline='\n').write(
        txt.replace('ideal G = slimgb(I);', 'ideal G = std(I);'))
    update_manifest(name, dict(gauge=g, split=[c0, c1], vars=allv, nvars=len(vs),
                               nfactors=len(sub), kept=list(keep),
                               factors=[str(f) for f in sub]))
    log('genreduced: %s keeps factors %s of %d' % (name, list(keep), len(fac)))


def update_manifest(name, entry):
    """read-modify-write of manifest.json under a lock file, since two pipelines run"""
    lock = os.path.join(EXD, 'manifest.lock')
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            time.sleep(0.2)
    try:
        man = json.load(open(os.path.join(EXD, 'manifest.json')))
        man['jobs'][name] = entry
        json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    finally:
        os.close(fd)
        os.remove(lock)


def prove(g, ks, threads=2):
    """The split-4 route for each split in KS: shrink the candidate factor list modulo a
    prime (a guide only), then decide the smaller system exactly over Q with Singular,
    and cross-check it with msolve."""
    for k in ks:
        keep = greedy(k, g, None, threads, start=cand_indices(k, g))
        genreduced(k, g, keep)
        run('singrab', g, ['red%d' % k], 1, 21600)
        run('msolve', g, ['red%d' % k], 1, 3600)


def gencand(k, g):
    """Split k keeping only the saturations 'P differs from each of A,B,C,H' and 'neither
    new radius equals R', the kinds the greedy screen of split 4 kept.  As with
    genreduced, a unit ideal here refutes the split completely, since every admissible
    configuration satisfies these conditions too.  Each split and gauge gets its own
    exact decision, so the result does not lean on the relabelling symmetry."""
    S = check_splits()
    c0, c1 = S[k]
    eqs, _, vs = split_system(g, c0, c1)
    Q, P, _, _ = gauge(g)
    ra, rb = sp.symbols('ra rb')
    A, B, C = Q[0], Q[1], Q[2]
    K, N = cr(A, B, C), d2(B, C) * d2(C, A) * d2(A, B)
    sub = factors([d2(P, X) for X in Q] + [4 * ra * K ** 2 - N, 4 * rb * K ** 2 - N], vs)
    name = '%s_cand%d' % (g, k)
    allv = write_msolve(name, eqs, sub, vs)
    write_singular_rab(name, eqs, sub, vs)
    man = json.load(open(os.path.join(EXD, 'manifest.json')))
    man['jobs'][name] = dict(gauge=g, split=[c0, c1], vars=allv, nvars=len(vs),
                             nfactors=len(sub), factors=[str(f) for f in sub])
    json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    return name


def cand_factors(g, vs):
    Q, P, _, _ = gauge(g)
    ra, rb = sp.symbols('ra rb')
    A, B, C = Q[0], Q[1], Q[2]
    K, N = cr(A, B, C), d2(B, C) * d2(C, A) * d2(A, B)
    return factors([d2(P, X) for X in Q] + [4 * ra * K ** 2 - N, 4 * rb * K ** 2 - N], vs)


def job_system(name):
    """rebuild a reduced system from the geometry, not from any file"""
    job = json.load(open(os.path.join(EXD, 'manifest.json')))['jobs'][name]
    c0, c1 = job['split']
    eqs, fac, vs = split_system(job['gauge'], c0, c1)
    sub = [fac[i] for i in job['kept']] if 'kept' in job else cand_factors(job['gauge'], vs)
    assert [str(f) for f in sub] == job['factors'], 'manifest disagrees with the geometry'
    ts = [sp.Symbol('t%d' % (i + 1)) for i in range(len(sub))]
    return eqs + [t * f - 1 for t, f in zip(ts, sub)], vs + ts


def genlift(name):
    """Singular: a standard basis WITH its transformation matrix (liftstd, slimgb), so a
    unit ideal comes with explicit cofactors h_i, sum h_i f_i = G[1] = 1."""
    src = io.open(os.path.join(EXD, name + '.rab.sing'), encoding='ascii').read()
    head = src.split('ideal G = slimgb(I);')[0]
    tail = '''matrix T;
ideal G = liftstd(I, T, "slimgb");
print("RESULT gsize " + string(size(G)));
print("RESULT g1 " + string(G[1]));
link l = ":w /work/%s/%s.cert";
int i;
for (i = 1; i <= nrows(T); i++) { write(l, string(T[i,1])); write(l, "@@"); }
close(l);
quit;
''' % (EXD, name)
    io.open(os.path.join(EXD, name + '.lift.sing'), 'w', encoding='ascii',
            newline='\n').write(head + tail)


def parse_sing(s, names):
    idx = {v: i for i, v in enumerate(names)}
    s = s.replace('\n', '').replace(' ', '')
    out = {}
    if s in ('', '0'):
        return out
    for term in re.findall(r'[+-]?[^+-]+', s):
        sign = -1 if term[0] == '-' else 1
        coef, ex = Fraction(sign), [0] * len(names)
        for f in term.lstrip('+-').split('*'):
            if re.fullmatch(r'\d+(/\d+)?', f):
                coef *= Fraction(f)
            else:
                v, _, e = f.partition('^')
                ex[idx[v]] += int(e) if e else 1
        out[tuple(ex)] = out.get(tuple(ex), 0) + coef
    return out


def certcheck(name):
    """The unit-ideal proof checked WITHOUT Singular's Groebner code: the generators are
    rebuilt from the geometry, the cofactors are read from Singular's file, and
    sum h_i f_i is expanded with python-flint's exact rational arithmetic."""
    import flint
    polys, allv = job_system(name)
    names = tuple(str(v) for v in allv)
    ctx = flint.fmpq_mpoly_ctx.get(names, 'degrevlex')

    def fl(d):
        return ctx.from_dict({k: flint.fmpq(v.numerator, v.denominator)
                              for k, v in d.items() if v != 0})
    gens = [fl({m: Fraction(int(c.p), int(c.q)) for m, c in sp.Poly(e, *allv).terms()})
            for e in polys]
    chunks = io.open(os.path.join(EXD, name + '.cert'), encoding='ascii').read().split('@@')
    hs = [fl(parse_sing(c, names)) for c in chunks[:len(gens)]]
    assert len(hs) == len(gens), 'cofactor count %d, generators %d' % (len(hs), len(gens))
    total = ctx.from_dict({})
    for h, f in zip(hs, gens):
        total = total + h * f
    ok = total == ctx.from_dict({tuple([0] * len(names)): 1})
    nterms = sum(len(h.to_dict()) if hasattr(h, 'to_dict') else 0 for h in hs)
    log('certcheck %s: sum h_i f_i == 1 exactly: %s  (%d generators, %d cofactor terms)'
        % (name, ok, len(gens), nterms))
    return ok


PRIME = 1073741827


def genscreen(k=4, g='F2'):
    """Which saturations are needed?  Dropping a factor from the Rabinowitsch list keeps a
    unit-ideal conclusion VALID (it only removes fewer degenerate cases, so it proves
    more), and every variable removed makes the exact computation over Q smaller.  This
    screens, modulo one prime and so only as a guide, the system with each factor
    dropped in turn.  Nothing is concluded from these runs; they only choose which exact
    computation to attempt."""
    S = check_splits()
    c0, c1 = S[k]
    eqs, fac, vs = split_system(g, c0, c1)
    man = json.load(open(os.path.join(EXD, 'manifest.json')))
    for j in [None] + list(range(len(fac))):
        keep = [f for i, f in enumerate(fac) if i != j]
        name = '%s_scr%d_%s' % (g, k, 'all' if j is None else 'x%d' % j)
        allv = write_msolve(name, eqs, keep, vs)
        path = os.path.join(EXD, name + '.ms')
        lines = io.open(path, encoding='ascii').read().split('\n')
        lines[1] = str(PRIME)
        io.open(path, 'w', encoding='ascii', newline='\n').write('\n'.join(lines))
        man['jobs'][name] = dict(gauge=g, split=[c0, c1], char=PRIME, vars=allv,
                                 nvars=len(vs), nfactors=len(keep),
                                 dropped=None if j is None else str(fac[j]))
    json.dump(man, open(os.path.join(EXD, 'manifest.json'), 'w'), indent=1)
    log('genscreen: wrote %d mod-p screening copies of %s split %d' % (len(fac) + 1, g, k))


if __name__ == '__main__':
    if sys.argv[1] == 'gen':
        gen()
    elif sys.argv[1] == 'genscreen':
        genscreen()
    elif sys.argv[1] == 'genhyp':
        genhyp()
    elif sys.argv[1] == 'genplant':
        genplant()
    elif sys.argv[1] == 'genlift':
        genlift(sys.argv[2])
    elif sys.argv[1] == 'certcheck':
        sys.exit(0 if certcheck(sys.argv[2]) else 1)
    elif sys.argv[1] == 'gencand':
        for g in ('F1', 'F2'):
            for k in range(9):
                gencand(k, g)
        log('gencand: wrote the candidate reduced system of all 9 splits in F1 and F2')
    elif sys.argv[1] == 'genreduced':
        # python caseA_exact.py genreduced K GAUGE KEEP   (KEEP comma-separated indices)
        genreduced(int(sys.argv[2]), sys.argv[3], [int(x) for x in sys.argv[4].split(',')])
    elif sys.argv[1] == 'greedy':
        # python caseA_exact.py greedy K GAUGE ORDER   (ORDER comma-separated factor indices)
        greedy(int(sys.argv[2]), sys.argv[3], [int(x) for x in sys.argv[4].split(',')])
    elif sys.argv[1] == 'genrelax':
        genrelax()
    elif sys.argv[1] == 'genrab':
        genrab()
    elif sys.argv[1] == 'xcheck':
        xcheck()
    elif sys.argv[1] == 'run':
        engine, g, jobs = sys.argv[2], sys.argv[3], sys.argv[4].split(',')
        threads = int(sys.argv[5]) if len(sys.argv) > 5 else 7
        tmo = int(sys.argv[6]) if len(sys.argv) > 6 else 3600
        run(engine, g, jobs, threads, tmo)
