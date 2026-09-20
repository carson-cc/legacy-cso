#!/usr/bin/env python3
"""Binary search the smallest radius R such that the given point set restricted to |x| < R is still
non-4-colorable (fresh budgeted solves; UNKNOWN counts as 'not proven', i.e. keep the larger radius)."""
import sys, math, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile,xyfile,budget=sys.argv[1],sys.argv[2],int(sys.argv[3])
allxy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
key={(round(x,7),round(y,7)):i for i,(x,y) in enumerate(allxy)}
pts=[key[(round(x,7),round(y,7))] for x,y in (tuple(map(float,l.split())) for l in open(xyfile))]
rad={v:math.hypot(*allxy[v]) for v in pts}; k=4
def unsat(vs):
    idx={v:i for i,v in enumerate(vs)}; Es=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
    var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(len(vs))]
    for a,b in Es:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    s=Cadical153(bootstrap_with=cl); s.conf_budget(budget); r=s.solve_limited(); s.delete(); return r
radii=sorted(set(round(r,4) for r in rad.values())); lo,hi=0,len(radii)-1; best=radii[-1]; t0=time.time()
while lo<=hi:
    mid=(lo+hi)//2; R=radii[mid]; vs=[v for v in pts if rad[v]<=R+1e-9]; r=unsat(vs)
    print("R=%.4f |V|=%d -> %s (%.0fs)"%(R,len(vs),{True:'SAT',False:'UNSAT',None:'UNKNOWN'}[r],time.time()-t0),flush=True)
    if r is False: best=R; hi=mid-1
    else: lo=mid+1
print("smallest proven radius: %.4f"%best,flush=True)
