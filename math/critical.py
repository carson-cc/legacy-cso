#!/usr/bin/env python3
"""508 program, step 1: vertex-criticality of a 5-chromatic graph. For each v: is G-v 4-colorable?
UNSAT (with budget) => G-v is still 5-chromatic => smaller 5-chromatic graph."""
import sys, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
n,E=load_edges(sys.argv[1]); budget=int(sys.argv[2]) if len(sys.argv)>2 else 3000000
k=4; var=lambda u,c: u*k+c+1
adj={u:set() for u in range(n)}
for a,b in E: adj[a].add(b); adj[b].add(a)
t0=time.time(); crit=[]; unk=[]
for v in range(n):
    cl=[[var(u,c) for c in range(k)] for u in range(n) if u!=v]
    for a,b in E:
        if v in (a,b): continue
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    # pin a triangle avoiding v
    for a,b in E:
        if v in (a,b): continue
        com=[w for w in adj[a]&adj[b] if w!=v]
        if com: 
            for c,u in enumerate((a,b,com[0])): cl.append([var(u,c)])
            break
    s=Cadical153(bootstrap_with=cl); s.conf_budget(budget); r=s.solve_limited(); s.delete()
    if r is False: crit.append(v); print("  DELETABLE vertex %d: G-v still not 4-colorable"%v,flush=True)
    elif r is None: unk.append(v)
    if (v+1)%50==0: print("  progress %d/%d deletable=%d unknown=%d (%.0fs)"%(v+1,n,len(crit),len(unk),time.time()-t0),flush=True)
print("DONE deletable=%s unknown=%s (%.0fs)"%(crit,unk,time.time()-t0),flush=True)
