#!/usr/bin/env python3
"""After an UNSAT disc/annulus run with DRAT: extract the unsat core with drat-trim (-c), map core clauses
back to vertices, and greedily minimize the vertex set while the graph stays non-4-colorable.
Usage: core_extract.py <edgefile> <r_in> <r_out> <cnf> <drat> <drat-trim binary>"""
import sys, math, subprocess, time
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile,r_in,r_out,cnf,drat,DT=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4],sys.argv[5],sys.argv[6]
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
keep=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out]; idx={v:i for i,v in enumerate(keep)}
E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]; m=len(keep); k=4
out=subprocess.run([DT,cnf,drat,"-c","notes/core.cnf"],capture_output=True,text=True).stdout
print(out.strip().splitlines()[-1])
core_vars=set()
for line in open("notes/core.cnf"):
    if line[0] in "cp": continue
    for lit in line.split():
        if lit!="0": core_vars.add((abs(int(lit))-1)//k)
V=sorted(v for v in core_vars if v<m); print("core touches %d of %d vertices"%(len(V),m),flush=True)
def unsat(Vset):
    id2={v:i for i,v in enumerate(Vset)}; Es=[(id2[a],id2[b]) for a,b in E2 if a in id2 and b in id2]
    var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(len(Vset))]
    for a,b in Es:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    s=Cadical153(bootstrap_with=cl); s.conf_budget(2000000); r=s.solve_limited(); s.delete(); return r is False
assert unsat(V), "core is not UNSAT?!"
t0=time.time(); cur=list(V)
for v in sorted(V, key=lambda v:-math.hypot(*xy[keep[v]])):
    trial=[u for u in cur if u!=v]
    if unsat(trial): cur=trial
print("minimized: %d vertices, %d edges (%.0fs)"%(len(cur),sum(1 for a,b in E2 if a in set(cur) and b in set(cur)),time.time()-t0))
with open("notes/small5_%g_%g.xy"%(r_in,r_out),"w") as f:
    for v in cur: f.write("%.15f %.15f\n"%xy[keep[v]])
print("wrote notes/small5_%g_%g.xy (float coords; re-derive exact coordinates from the CNP file + translation)"%(r_in,r_out))
