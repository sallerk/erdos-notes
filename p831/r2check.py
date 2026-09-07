import sys,json
sys.argv=['x']; sys.stdout.reconfigure(encoding='utf-8',errors='replace')
exec(open('AUDIT_R2_SELF.py').read().split('if __name__')[0])
import numpy as np
from scipy.optimize import least_squares
pats=json.load(open('results/penum_n5_k3.json'))['patterns']
rng=np.random.default_rng(4242)
def eqonly(lab):
    def f(v):
        P=unpack(v); r2,S=quantities(P)
        if np.any(~np.isfinite(r2)) or np.any(r2<=0): return np.full(10,1e3)
        sc=float(np.mean(r2))
        means={c:float(np.mean([r2[i] for i in range(10) if lab[i]==c])) for c in range(3)}
        return np.array([(r2[i]-means[lab[i]])/sc for i in range(10)])
    return f
out=[]; tot=0; worst=0.0
for i in range(15):
    f=eqonly(pats[i]['labels']); roots=0; mx=0.0
    for _ in range(120):
        v0=rng.uniform(-8,8,6)
        try: s=least_squares(f,v0,xtol=1e-15,ftol=1e-15,gtol=1e-15,max_nfev=2000)
        except Exception: continue
        if float(np.max(np.abs(s.fun)))>1e-10: continue
        roots+=1
        m=margins(s.x,pats[i]['labels'],3)
        if m is not None: mx=max(mx,m['concyclic'])
    tot+=roots; worst=max(worst,mx)
    out.append(dict(i=i,roots=roots,max_concyclic_margin=float(mx)))
    print('  pattern %2d: %3d exact roots, largest min|det4|/scale^1.5 = %.2e'%(i,roots,mx),flush=True)
print()
print('total %d roots; largest concyclicity margin anywhere = %.2e'%(tot,worst))
print('VERDICT: every exact root is four-concyclic' if worst<1e-9 else 'VERDICT: not all concyclic')
json.dump(dict(rows=out,total_roots=tot,worst_margin=float(worst),
               all_concyclic=bool(worst<1e-9),completed=True),
          open('results/r2_unguarded_roots.json','w'),indent=1)
