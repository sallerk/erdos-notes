"""Decide each enumerated k=3 pattern class over the reals, best encoding.

Encoding (all three ingredients measured to matter, see tactic3_n7.json):
  * FULL convex position: all C(n,3) orientations positive.  Consecutive-triple
    orientations alone are NOT convex position -- they also admit winding-2 star
    polygons, and at n=6 that difference turned 19 spurious SATs into 0.
  * obtuse-middle inequality D_jl > D_jk + D_kl  (implied; supplied as a lemma)
  * circumradius identity, verified symbolically in cmlemma.py (implied; lemma):
        D_ij (2 D_jk D_kl + 2 D_kl D_jl + 2 D_jl D_jk - D_jk^2 - D_kl^2 - D_jl^2)
          = D_jk D_kl D_jl
Both lemmas are logical consequences of the coordinate equations, so they change
no verdict; they only shorten nlsat's refutations.

UNSAT for every class  =>  no strictly convex n-gon has every vertex with 3
other vertices equidistant from it.  UNKNOWN is reported, never folded in.
"""
import sys, json, time, numpy as np, multiprocessing as mp
from itertools import combinations
from enum_nb import tables
_G={}
def _init(n,TJ,TK,TL,tmo): _G.update(n=n,TJ=TJ,TK=TK,TL=TL,tmo=tmo)
def _solve(job):
    import z3
    idx,ch=job
    n,TJ,TK,TL,tmo=_G['n'],_G['TJ'],_G['TK'],_G['TL'],_G['tmo']
    s=z3.Solver(); s.set('timeout',tmo)
    X=[z3.Real(f'x{i}') for i in range(n)]; Y=[z3.Real(f'y{i}') for i in range(n)]
    s.add(X[0]==0,Y[0]==0,X[1]==1,Y[1]==0)
    for a,b,c in combinations(range(n),3):
        s.add((X[b]-X[a])*(Y[c]-Y[a])-(Y[b]-Y[a])*(X[c]-X[a])>0)
    D=lambda a,b:(X[a]-X[b])**2+(Y[a]-Y[b])**2
    for i in range(n):
        t=ch[i]; j,k,l=int(TJ[i,t]),int(TK[i,t]),int(TL[i,t])
        s.add(D(i,j)==D(i,k), D(i,k)==D(i,l))
        s.add(D(j,l)>D(j,k)+D(k,l))
        A,B,C,R=D(j,k),D(k,l),D(j,l),D(i,j)
        s.add(R*(2*A*B+2*B*C+2*C*A-A*A-B*B-C*C)==A*B*C)
    t0=time.time(); r=s.check(); dt=time.time()-t0
    if r==z3.sat:
        m=s.model()
        return (idx,'sat',[[str(m.eval(X[i],model_completion=True)),
                            str(m.eval(Y[i],model_completion=True))] for i in range(n)],dt)
    return (idx,'unsat' if r==z3.unsat else 'unknown',None,dt)

def run(n,tmo,workers,idxfile=None,tag=''):
    pid,NP,NT,TJ,TK,TL=tables(n)
    cls=np.load(f'cls_n{n}.npy')
    sel=np.load(idxfile) if idxfile else np.arange(len(cls))
    jobs=[(int(i),cls[i]) for i in sel]
    print(f"n={n}: {len(jobs):,} classes, {workers} workers, timeout {tmo}ms",flush=True)
    res={'n':n,'total':len(jobs),'sat':[],'unsat':0,'unknown':[],'timeout_ms':tmo,
         'workers':workers,'encoding':'fullconvex+obtuse+circumradius','status':'RUNNING'}
    t0=time.time(); tmax=0.
    with mp.Pool(workers,initializer=_init,initargs=(n,TJ,TK,TL,tmo)) as pool:
        for c,(idx,v,pts,dt) in enumerate(pool.imap_unordered(_solve,jobs,chunksize=1),1):
            tmax=max(tmax,dt)
            if v=='sat':
                ch=cls[idx]
                res['sat'].append({'idx':idx,'pattern':[[int(TJ[i,ch[i]]),int(TK[i,ch[i]]),int(TL[i,ch[i]])] for i in range(n)],'points':pts})
                print(f"*** SAT n={n} idx={idx}",flush=True)
            elif v=='unsat': res['unsat']+=1
            else: res['unknown'].append(idx)
            if c%500==0:
                el=time.time()-t0
                print(f"  {c:,}/{len(jobs):,} {el:.0f}s ({c/el:.1f}/s) unsat={res['unsat']:,} "
                      f"sat={len(res['sat'])} unk={len(res['unknown']):,} eta={(len(jobs)-c)/(c/el)/60:.0f}min",flush=True)
                res['elapsed_s']=round(el,1)
                json.dump(res,open(f'solve2_n{n}{tag}.json','w'),indent=1)
    res['elapsed_s']=round(time.time()-t0,1); res['slowest_s']=round(tmax,2); res['status']='COMPLETED'
    json.dump(res,open(f'solve2_n{n}{tag}.json','w'),indent=1)
    np.save(f'unknown_n{n}{tag}.npy', np.array(res['unknown'],np.int64))
    print(f"n={n} DONE {res['elapsed_s']}s: unsat={res['unsat']:,} sat={len(res['sat'])} "
          f"unknown={len(res['unknown']):,} / {len(jobs):,}",flush=True)
if __name__=='__main__':
    mp.freeze_support()
    n=int(sys.argv[1]); tmo=int(sys.argv[2]); w=int(sys.argv[3])
    idxf=sys.argv[4] if len(sys.argv)>4 and sys.argv[4]!='-' else None
    tag=sys.argv[5] if len(sys.argv)>5 else ''
    run(n,tmo,w,idxf,tag)
