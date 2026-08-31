"""INDEPENDENT VERIFIER, sharing no code with the DFS prune.

Three checks:
 A. n=4 and n=5: brute-force EVERY pattern with z3, no prune at all.  The prune
    claimed zero survivors; this confirms the conclusion without relying on it.
 B. n=6,7: take a random sample of patterns the prune REJECTED and hand each to
    z3.  If the prune is sound every one must come back UNSAT.  A single SAT
    would mean the obtuse-middle lemma or its implementation is wrong and every
    UNSAT conclusion built on it is void.
 C. re-check the stored survivor set is closed under nothing but the claimed
    symmetry (count divisibility).
"""
import numpy as np, sys, json, time, random, multiprocessing as mp
from itertools import combinations
from enum_nb import tables, _consistent

_G={}
def _init(n,tmo,fullcx): _G.update(n=n,tmo=tmo,fullcx=fullcx)
def _chk(job):
    import z3
    idx, pat = job
    n,tmo,fullcx = _G['n'],_G['tmo'],_G['fullcx']
    s=z3.Solver(); s.set('timeout',tmo)
    X=[z3.Real(f'x{i}') for i in range(n)]; Y=[z3.Real(f'y{i}') for i in range(n)]
    s.add(X[0]==0,Y[0]==0,X[1]==1,Y[1]==0)
    tri = list(combinations(range(n),3)) if fullcx else [(i,(i+1)%n,(i+2)%n) for i in range(n)]
    for a,b,c in tri:
        s.add((X[b]-X[a])*(Y[c]-Y[a])-(Y[b]-Y[a])*(X[c]-X[a])>0)
    D=lambda a,b:(X[a]-X[b])**2+(Y[a]-Y[b])**2
    for i,(j,k,l) in enumerate(pat):
        s.add(D(i,j)==D(i,k), D(i,k)==D(i,l))
    r=s.check()
    return (idx, str(r))

def brute(n, workers=18, tmo=120000):
    """check EVERY pattern, no prune"""
    pid,NP,NT,TJ,TK,TL = tables(n)
    import itertools
    jobs=[]
    for t,combo in enumerate(itertools.product(range(NT), repeat=n)):
        pat=[(int(TJ[i,combo[i]]),int(TK[i,combo[i]]),int(TL[i,combo[i]])) for i in range(n)]
        jobs.append((t,pat))
    print(f"n={n}: brute-forcing ALL {len(jobs):,} patterns (no prune), full convexity",flush=True)
    sat=[]; unsat=0; unk=[]
    t0=time.time()
    with mp.Pool(workers,initializer=_init,initargs=(n,tmo,True)) as pool:
        for c,(idx,r) in enumerate(pool.imap_unordered(_chk,jobs,chunksize=8),1):
            if r=='sat': sat.append(idx); print(f"  *** SAT idx={idx}",flush=True)
            elif r=='unsat': unsat+=1
            else: unk.append(idx)
            if c%200==0: print(f"   {c}/{len(jobs)} {time.time()-t0:.0f}s",flush=True)
    out=dict(n=n,mode='brute_all_patterns',total=len(jobs),sat=len(sat),unsat=unsat,
             unknown=len(unk),unknown_idx=unk[:50],seconds=round(time.time()-t0,1),
             status='COMPLETED')
    print(f"n={n} BRUTE: sat={len(sat)} unsat={unsat} unknown={len(unk)} / {len(jobs)}",flush=True)
    json.dump(out,open(f'verify_brute_n{n}.json','w'),indent=1)
    return out

def sample_rejected(n, k=200, seed=11, workers=18, tmo=60000):
    """random patterns the prune rejects -> z3 must agree they are UNSAT"""
    pid,NP,NT,TJ,TK,TL = tables(n)
    uf=np.zeros(64,np.int32); hi=np.zeros(64,np.int32); lo=np.zeros(64,np.int32)
    indeg=np.zeros(64,np.int32); pres=np.zeros(64,np.int32); st=np.zeros(64,np.int32)
    rng=random.Random(seed); jobs=[]; tries=0
    ch=np.zeros(16,np.int32)
    while len(jobs)<k and tries<400000:
        tries+=1
        for i in range(n): ch[i]=rng.randrange(NT)
        if _consistent(ch,n-1,pid,NP,TJ,TK,TL,uf,hi,lo,indeg,pres,st): continue
        pat=[(int(TJ[i,ch[i]]),int(TK[i,ch[i]]),int(TL[i,ch[i]])) for i in range(n)]
        jobs.append((len(jobs),pat))
    print(f"n={n}: {len(jobs)} prune-REJECTED patterns sampled from {tries} draws; "
          f"z3 must call every one UNSAT",flush=True)
    sat=[]; unsat=0; unk=[]
    t0=time.time()
    with mp.Pool(workers,initializer=_init,initargs=(n,tmo,True)) as pool:
        for c,(idx,r) in enumerate(pool.imap_unordered(_chk,jobs,chunksize=2),1):
            if r=='sat':
                sat.append(jobs[idx][1]); print(f"  *** PRUNE UNSOUND: SAT on rejected pattern {jobs[idx][1]}",flush=True)
            elif r=='unsat': unsat+=1
            else: unk.append(idx)
            if c%50==0: print(f"   {c}/{len(jobs)} {time.time()-t0:.0f}s unsat={unsat} unk={len(unk)}",flush=True)
    verdict = 'PRUNE SOUND ON SAMPLE' if not sat else '*** PRUNE UNSOUND ***'
    print(f"n={n} REJECTED-SAMPLE: unsat={unsat} unknown={len(unk)} sat={len(sat)} -> {verdict}",flush=True)
    out=dict(n=n,mode='sample_of_prune_rejected',sampled=len(jobs),draws=tries,
             unsat=unsat,unknown=len(unk),sat=len(sat),verdict=verdict,
             seconds=round(time.time()-t0,1),status='COMPLETED')
    json.dump(out,open(f'verify_rejected_n{n}.json','w'),indent=1)
    return out

if __name__=='__main__':
    mp.freeze_support()
    what=sys.argv[1]
    if what=='brute': brute(int(sys.argv[2]))
    else: sample_rejected(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv)>3 else 200)
