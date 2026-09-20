#!/usr/bin/env python3
"""508 program, step 2: all pair deletions of a 5-chromatic graph, incrementally.
Encoding: 4-coloring clauses for G, each vertex's at-least-one-color clause gets a selector s_v;
assuming s_v = true 'deletes' v (it may stay uncolored). Deleting {u,v}: assumptions s_u, s_v true,
all other selectors false. UNSAT => G - {u,v} is not 4-colorable => a (n-2)-vertex 5-chromatic graph.
UNKNOWN (budget) pairs are logged for later."""
import sys, time, itertools
from pysat.solvers import Cadical153
from star_on_graph import load_edges
n,E=load_edges(sys.argv[1]); budget=int(sys.argv[2]) if len(sys.argv)>2 else 200000
k=4; var=lambda u,c: u*k+c+1; sel=lambda u: n*k+u+1
cl=[[var(u,c) for c in range(k)]+[sel(u)] for u in range(n)]
for a,b in E:
    for c in range(k): cl.append([-var(a,c),-var(b,c)])
s=Cadical153(bootstrap_with=cl)
base=[-sel(u) for u in range(n)]
t0=time.time(); hits=[]; unk=[]; done=0
for u,v in itertools.combinations(range(n),2):
    assum=[x for x in base if x not in (-sel(u),-sel(v))]+[sel(u),sel(v)]
    s.conf_budget(budget); r=s.solve_limited(assumptions=assum); done+=1
    if r is False: hits.append((u,v)); print("  RECORD CANDIDATE: G-{%d,%d} not 4-colorable"%(u,v),flush=True)
    elif r is None: unk.append((u,v))
    if done%5000==0: print("  progress %d pairs, hits=%d unknown=%d (%.0fs)"%(done,len(hits),len(unk),time.time()-t0),flush=True)
print("DONE pairs=%d hits=%s unknown=%d (%.0fs)"%(done,hits,len(unk),time.time()-t0),flush=True)
open("notes/pairs_unknown.txt","w").write("\n".join("%d %d"%p for p in unk))
