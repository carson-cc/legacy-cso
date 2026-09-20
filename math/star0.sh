#!/bin/bash
# (star0) on a depth-2 exact universe: does some vertex v have N(v) color-saturated in every 5-coloring?
cd /home/user/legacy-cso/math
python3 - >> notes/star0_search.log 2>&1 <<'PY'
import time
from bichromatic_search import build_universe, solve
from surgery import exact_unit_edges
U=build_universe(2,9); E=exact_unit_edges(U); n=len(U)
adj={}
for a,b in E: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
print("depth-2 universe: |V|=%d |E|=%d  4-colorable=%s"%(n,len(E),solve(n,E,4,{})),flush=True)
t0=time.time(); hits=[]
# by symmetry test the origin and the 5 highest-degree vertices
cands=[next(i for i,p in enumerate(U) if p.norm2().is_zero())]+sorted(range(n),key=lambda v:-len(adj.get(v,())))[:5]
for v in cands:
    forb={u:[1] for u in adj.get(v,())}; forb[v]=[1,2,3,4]   # c(v)=0, color 1 absent from N(v)
    r=solve(n,E,5,forb)
    print("v=%d deg=%d  5-coloring with N(v) missing a color: %s"%(v,len(adj.get(v,())),"SAT" if r else "UNSAT (star0 HOLDS)"),flush=True)
print("done %.0fs"%(time.time()-t0))
PY
echo STAR0_DONE >> notes/star0_search.log
