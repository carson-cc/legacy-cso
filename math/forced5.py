#!/usr/bin/env python3
"""Step-2 gadget test, literal form: is there a non-adjacent pair (u,v) that receives the SAME colour in
EVERY 5-colouring of G?  (UNSAT of '5-colour G with c(u) != c(v)'.)  Such a pair spindles to a
6-chromatic unit-distance graph. One incremental solver per u with a selector per v."""
import sys, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
n,E=load_edges(sys.argv[1]); budget=int(sys.argv[2]) if len(sys.argv)>2 else 100000
k=5; var=lambda u,c: u*k+c+1
adj={u:set() for u in range(n)}
for a,b in E: adj[a].add(b); adj[b].add(a)
base=[[var(u,c) for c in range(k)] for u in range(n)]
for a,b in E:
    for c in range(k): base.append([-var(a,c),-var(b,c)])
t0=time.time(); hits=[]; unk=0; calls=0
for u in range(n):
    vs=[v for v in range(u+1,n) if v not in adj[u]]
    sel=lambda i: n*k+i+1
    cl=list(base)
    for i,v in enumerate(vs):
        for c in range(k): cl.append([-sel(i),-var(u,c),-var(v,c)])   # sel(i) => c(u) != c(v)
    s=Cadical153(bootstrap_with=cl)
    for i,v in enumerate(vs):
        assum=[sel(i)]+[-sel(j) for j in range(len(vs)) if j!=i]
        s.conf_budget(budget); r=s.solve_limited(assumptions=assum); calls+=1
        if r is False: hits.append((u,v)); print("  FORCED-EQUAL PAIR (u=%d,v=%d): 6-chromatic by spindling!"%(u,v),flush=True)
        elif r is None: unk+=1
    s.delete()
    if (u+1)%50==0: print("  progress u=%d calls=%d hits=%d unknown=%d (%.0fs)"%(u+1,calls,len(hits),unk,time.time()-t0),flush=True)
print("DONE pairs=%d hits=%s unknown=%d (%.0fs)"%(calls,hits,unk,time.time()-t0),flush=True)
