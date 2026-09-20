#!/usr/bin/env python3
"""Quantify the slack of the doubled-origin constraint on a big graph: largest radius r such that
'5-color H with every vertex within distance r of the origin restricted to {3,4,5}' is still SAT.
r = 1 is exactly (star0) at the origin (only N(origin) is within distance 1 besides the origin)."""
import sys, math, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile=sys.argv[1]; xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]
n,E=load_edges(edgefile); k=5; var=lambda u,c: u*k+c+1
dist=[math.hypot(x,y) for x,y in xy]
base=[[var(u,c) for c in range(k)] for u in range(n) if u!=0]
for a,b in E:
    if 0 in (a,b): continue
    for c in range(k): base.append([-var(a,c),-var(b,c)])
s=Cadical153(bootstrap_with=base)
radii=sorted(set(round(d,6) for d in dist if d>0))
lo=None
for r in radii:
    if r>4.0: break
    assum=[-var(u,c) for u in range(n) if u!=0 and dist[u]<=r+1e-9 for c in (0,1)]
    s.conf_budget(int(sys.argv[2]) if len(sys.argv)>2 else 2000000); t=time.time(); res=s.solve_limited(assumptions=assum)
    m=sum(1 for u in range(n) if u!=0 and dist[u]<=r+1e-9)
    print("radius %.6f (%d vertices forced into 3 colours): %s (%.0fs)"%(r,m,{True:'SAT',False:'UNSAT',None:'UNKNOWN'}[res],time.time()-t),flush=True)
    if res is not True: break
    lo=r
print("largest SAT radius:",lo)
