import sys,json
sys.argv=['x']; sys.stdout.reconfigure(encoding='utf-8',errors='replace')
exec(open('target433.py').read().split('if __name__')[0])
import numpy as np
from scipy.optimize import minimize
def circd(a,b):
    d=abs(a-b)%(2*np.pi); return min(d,2*np.pi-d)
def sep(th):
    ang=[0.0]+list(th); return min(circd(ang[i],ang[j]) for i in range(4) for j in range(i+1,4))
def f12(th):
    P=points(th)
    a=r2_of(P,(0,1,4))[0]; b=r2_of(P,(1,2,3))[0]; c=r2_of(P,(0,2,3))[0]; d=r2_of(P,(1,2,4))[0]
    if not all(np.isfinite([a,b,c,d])): return None
    return ((a-b)/(abs(a)+abs(b)),(c-d)/(abs(c)+abs(d)))
def obj(th,smin):
    v=f12(th)
    if v is None: return 1e3
    return max(abs(v[0]),abs(v[1]))+max(0.0,smin-sep(th))*50
rng=np.random.default_rng(2718); out=[]
for smin in (0.35,0.25,0.15,0.08,0.03):
    best=(9e9,None)
    for k in range(1200):
        th0=rng.uniform(0,2*np.pi,3)
        if sep(th0)<smin: continue
        r=minimize(obj,th0,args=(smin,),method='Nelder-Mead',
                   options=dict(xatol=1e-12,fatol=1e-14,maxiter=2000,maxfev=2000))
        if r.fun<best[0]: best=(r.fun,r.x.copy())
    v=f12(best[1])
    rec=dict(min_separation=smin,best=float(best[0]),sep=float(sep(best[1])),
             f1=float(v[0]),f2=float(v[1]),theta=list(map(float,best[1])))
    out.append(rec)
    print('separation >= %.2f : best max(|f1|,|f2|) = %.4e  (sep=%.3f f1=%+.2e f2=%+.2e)'
          %(smin,best[0],rec['sep'],v[0],v[1]),flush=True)
json.dump(dict(sweep=out,completed=True),open('results/obstruction433.json','w'),indent=1)
