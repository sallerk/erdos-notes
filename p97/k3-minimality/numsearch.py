"""INDEPENDENT numerical search, sharing no code with the z3 path.

For each enumerated pattern class at a given n, run scipy least-squares from many
random strictly-convex starts on the 2n equidistance residuals, then check the
result for STRICT CONVEX POSITION using all C(n,3) orientations (not just
consecutive triples -- consecutive-only would also accept a winding-2 star).
Reports the best convexity margin among exact-residual solutions.
"""
import numpy as np, sys, json, time
from itertools import combinations
from scipy.optimize import least_squares
from enum_nb import tables

def resid_fn(n, pat):
    def f(z):
        P = np.zeros((n,2)); P[1,0] = 1.0
        P[2:,0] = z[0::2]; P[2:,1] = z[1::2]
        r = []
        for i,(j,k,l) in enumerate(pat):
            d = lambda a,b: (P[a,0]-P[b,0])**2 + (P[a,1]-P[b,1])**2
            r.append(d(i,j)-d(i,k)); r.append(d(i,k)-d(i,l))
        return np.array(r)
    return f

def pts_from(n, z):
    P = np.zeros((n,2)); P[1,0]=1.0; P[2:,0]=z[0::2]; P[2:,1]=z[1::2]; return P

def margin(P, n):
    """min normalised orientation over ALL triples; >0 iff strictly convex ccw"""
    m = 1e9
    scale = max(1e-12, np.max(np.abs(P)))
    for a,b,c in combinations(range(n),3):
        cr = (P[b,0]-P[a,0])*(P[c,1]-P[a,1]) - (P[b,1]-P[a,1])*(P[c,0]-P[a,0])
        m = min(m, cr/scale**2)
    return m

def rand_convex_start(n, rng):
    th = np.sort(rng.uniform(0, 2*np.pi, n))
    rr = rng.uniform(0.7, 1.4, n)
    P = np.c_[rr*np.cos(th), rr*np.sin(th)]
    # normalise so P0=(0,0), P1=(1,0)
    P = P - P[0]
    a = np.arctan2(P[1,1], P[1,0]); s = np.hypot(*P[1])
    R = np.array([[np.cos(-a),-np.sin(-a)],[np.sin(-a),np.cos(-a)]])
    P = (P @ R.T)/s
    return P[2:].ravel()

def run(n, restarts=60, seed=1, limit=None, tol=1e-18):
    pid,NP,NT,TJ,TK,TL = tables(n)
    cls = np.load(f'cls_n{n}.npy')
    if limit: cls = cls[:limit]
    rng = np.random.default_rng(seed)
    hits = []
    t0=time.time()
    for ci, ch in enumerate(cls):
        pat = [(int(TJ[i,ch[i]]),int(TK[i,ch[i]]),int(TL[i,ch[i]])) for i in range(n)]
        f = resid_fn(n, pat)
        best = None
        for _ in range(restarts):
            z0 = rand_convex_start(n, rng)
            try:
                sol = least_squares(f, z0, xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=4000)
            except Exception:
                continue
            if sol.cost > tol:  continue
            P = pts_from(n, sol.x)
            mg = margin(P, n)
            if mg > 1e-7 and (best is None or mg > best[0]):
                best = (mg, P.copy(), float(sol.cost))
        if best:
            hits.append({'class':int(ci),'pattern':pat,'margin':float(best[0]),
                         'cost':best[2],'points':best[1].tolist()})
            print(f"  *** class {ci} pattern={pat} margin={best[0]:.6g} cost={best[2]:.3g}",flush=True)
    dt=time.time()-t0
    print(f"n={n}: {len(hits)}/{len(cls)} classes numerically realisable as a STRICTLY CONVEX "
          f"{n}-gon ({dt:.0f}s, {restarts} restarts each)",flush=True)
    json.dump({'n':n,'restarts':restarts,'seed':seed,'classes':len(cls),
               'realisable':len(hits),'hits':hits,'seconds':round(dt,1),
               'status':'COMPLETED'}, open(f'numsearch_n{n}.json','w'), indent=1)
    return hits

if __name__=='__main__':
    n=int(sys.argv[1]); r=int(sys.argv[2]) if len(sys.argv)>2 else 60
    lim=int(sys.argv[3]) if len(sys.argv)>3 else None
    run(n, r, limit=lim)
