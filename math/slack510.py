#!/usr/bin/env python3
"""Per-vertex slack radius on a 5-chromatic graph: for each v, the largest r such that all vertices
within distance r of v (except v) can be restricted to colours {3,4,5} inside a proper 5-colouring of
G - v. r >= 1 means (star0) fails at v; the size of r measures how much slack the doubled-origin
constraint leaves. Incremental SAT with assumptions; radii taken from the graph's distance set."""
import sys, math, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
from chord_angle import parse_vtx
n,E=load_edges(sys.argv[1]); P=parse_vtx(sys.argv[2]); k=5; var=lambda u,c: u*k+c+1
adj={u:set() for u in range(n)}
for a,b in E: adj[a].add(b); adj[b].add(a)
t0=time.time(); res={}
for v in range(n):
    cl=[[var(u,c) for c in range(k)] for u in range(n) if u!=v]
    for a,b in E:
        if v in (a,b): continue
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    s=Cadical153(bootstrap_with=cl)
    d=sorted((math.dist(P[v],P[u]),u) for u in range(n) if u!=v)
    radii=sorted(set(round(x,6) for x,_ in d))
    lo,hi=0,len(radii)-1; best=None
    # binary search on the radius index (monotone: larger radius = more constraints)
    while lo<=hi:
        mid=(lo+hi)//2; r=radii[mid]
        assum=[-var(u,c) for x,u in d if x<=r+1e-9 for c in (0,1)]
        s.conf_budget(300000); ok=s.solve_limited(assumptions=assum)
        if ok is True: best=r; lo=mid+1
        else: hi=mid-1
    s.delete(); res[v]=best
    if (v+1)%50==0: print("  progress %d/%d (%.0fs)"%(v+1,n,time.time()-t0),flush=True)
vals=sorted(res.values()); 
print("DONE slack radii: min=%.4f median=%.4f max=%.4f; count r<1: %d; distribution: %s"%(
    vals[0],vals[len(vals)//2],vals[-1],sum(1 for x in vals if x<1-1e-9),
    sorted({round(x,3):vals.count(x) for x in set(vals)}.items())[:12]),flush=True)
