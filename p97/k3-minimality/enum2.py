"""As enum_nb.py, plus DIHEDRAL SYMMETRY REDUCTION.

Because the triples TJ/TK/TL at vertex i are generated in ccw order starting
after i, the triple INDEX t encodes exactly the relative offsets
(p1,p2,p3) = ((j-i) mod n, (k-i) mod n, (l-i) mod n), the same encoding at every
vertex.  So a rotation of the polygon rotates the sequence (t_0,...,t_{n-1})
without changing any entry, and the reflection i -> -i maps entry t with offsets
(p1,p2,p3) to sigma(t) with offsets (n-p3,n-p2,n-p1) and reverses the order.

Hence: WLOG t_0 = min_i t_i   (a DFS prune), and at each leaf we keep only the
lexicographically smallest of the 2n dihedral images.  Both are sound: every
realisable pattern has a dihedral image that is kept.
"""
import numpy as np, sys, json, time
from numba import njit
from itertools import combinations
from enum_nb import tables, _find, _consistent

def sigma_table(n):
    combs = list(combinations(range(n-1), 3))
    key = {c: t for t, c in enumerate(combs)}
    sig = np.zeros(len(combs), np.int32)
    for t, (a, b, c) in enumerate(combs):
        p1, p2, p3 = a+1, b+1, c+1
        q = tuple(sorted((n-p3, n-p2, n-p1)))
        sig[t] = key[(q[0]-1, q[1]-1, q[2]-1)]
    return sig

@njit(cache=True)
def _lexmin(choice, n, sig, buf):
    """1 if choice is the lex-smallest of its 2n dihedral images, else 0"""
    for r in range(n):
        if r > 0:
            worse = 0
            for q in range(n):
                a = choice[q]; b = choice[(q+r) % n]
                if b < a: return 0
                if b > a: worse = 1; break
        # reflection: image[q] = sig[choice[(r - q) mod n]]
        for q in range(n):
            buf[q] = sig[choice[(r - q) % n]]
        for q in range(n):
            if buf[q] < choice[q]: return 0
            if buf[q] > choice[q]: break
    return 1

@njit(cache=True)
def dfs2(n, NP, NT, pid, TJ, TK, TL, sig, out, out_cap):
    choice = np.zeros(16, np.int32); idx = np.full(16, -1, np.int32)
    uf=np.zeros(64,np.int32); hi=np.zeros(64,np.int32); lo=np.zeros(64,np.int32)
    indeg=np.zeros(64,np.int32); pres=np.zeros(64,np.int32); st=np.zeros(64,np.int32)
    buf=np.zeros(16,np.int32)
    nodes=0; surv=0; nout=0
    d=0; idx[0]=-1
    while d >= 0:
        idx[d] += 1
        if idx[d] >= NT:
            idx[d] = -1; d -= 1; continue
        if d > 0 and idx[d] < choice[0]:      # rotation prune: t_0 = min_i t_i
            continue
        choice[d] = idx[d]
        nodes += 1
        if _consistent(choice, d, pid, NP, TJ, TK, TL, uf, hi, lo, indeg, pres, st):
            if d == n-1:
                if _lexmin(choice, n, sig, buf):
                    surv += 1
                    if nout < out_cap:
                        for q in range(n): out[nout,q]=choice[q]
                        nout += 1
            else:
                d += 1; idx[d] = -1
    return nodes, surv, nout

def run(n, cap=5_000_000):
    pid, NP, NT, TJ, TK, TL = tables(n)
    sig = sigma_table(n)
    out = np.zeros((max(cap,1), n), np.int32)
    t0=time.time()
    nodes, surv, nout = dfs2(n, NP, NT, pid, TJ, TK, TL, sig, out, cap)
    dt=time.time()-t0
    print(f"n={n} NT={NT} raw={NT**n:,} nodes={nodes:,} classes={surv:,} "
          f"stored={nout:,} {dt:.1f}s", flush=True)
    if cap: np.save(f'cls_n{n}.npy', out[:nout])
    json.dump(dict(n=n,NT=NT,raw=NT**n,nodes=int(nodes),classes=int(surv),
                   stored=int(nout),seconds=round(dt,2),
                   status='COMPLETED' if surv==nout else f'TRUNCATED cap={cap}'),
              open(f'enum2_n{n}.json','w'), indent=1)
    return surv

if __name__ == '__main__':
    n = int(sys.argv[1]); cap = int(sys.argv[2]) if len(sys.argv)>2 else 5_000_000
    run(n, cap)
