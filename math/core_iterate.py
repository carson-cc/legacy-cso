#!/usr/bin/env python3
"""Iterated unsat-core shrinking of a non-4-colorable point set: fresh CaDiCaL solve with DRAT on the
current vertex set, drat-trim -c for the core, restrict to core vertices, repeat until no shrink.
Then (optional) greedy single-vertex deletion with fresh solves if the set is small (< 1500).
Usage: core_iterate.py <edgefile> <r_in> <r_out> <drat-trim> <out.xy>"""
import sys, math, time, subprocess, os
from pysat.solvers import Cadical153
from star_on_graph import load_edges
edgefile,r_in,r_out,DT,out=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),sys.argv[4],sys.argv[5]
xy=[tuple(map(float,l.split())) for l in open(edgefile+".xy")]; n,E=load_edges(edgefile)
cur=[i for i,(x,y) in enumerate(xy) if r_in<math.hypot(x,y)<r_out]
k=4; t0=time.time()
def solve(vs, proof=True, budget=None):
    idx={v:i for i,v in enumerate(vs)}; Es=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
    var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(len(vs))]
    for a,b in Es:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    adj={}
    for a,b in Es: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
    for a,b in Es:
        com=adj[a]&adj[b]
        if com:
            for c,u in enumerate((a,b,min(com))): cl.append([var(u,c)])
            break
    s=Cadical153(bootstrap_with=cl,with_proof=proof)
    if budget: s.conf_budget(budget); r=s.solve_limited()
    else: r=s.solve()
    pr=s.get_proof() if (proof and r is False) else None; s.delete()
    return r,cl,pr,len(Es)
rnd=0
while True:
    rnd+=1
    r,cl,pr,ne=solve(cur); print("round %d: %d vertices %d edges -> %s (%.0fs)"%(rnd,len(cur),ne,{True:'SAT',False:'UNSAT',None:'UNKNOWN'}[r],time.time()-t0),flush=True)
    if r is not False: break
    open("notes/ci.cnf","w").write("p cnf %d %d\n"%(len(cur)*k,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
    open("notes/ci.drat","w").write("\n".join(pr)+"\n")
    o=subprocess.run([DT,"notes/ci.cnf","notes/ci.drat","-c","notes/ci_core.cnf"],capture_output=True,text=True).stdout
    ok="s VERIFIED" in o; print("   drat-trim: %s"%("VERIFIED" if ok else "NOT VERIFIED"),flush=True)
    if not ok: break
    cv=set()
    for line in open("notes/ci_core.cnf"):
        if line[0] in "cp": continue
        for lit in line.split():
            if lit!="0": cv.add((abs(int(lit))-1)//k)
    new=[cur[i] for i in sorted(cv) if i<len(cur)]
    if len(new)>=len(cur): break
    cur=new
# greedy deletion with fresh solves if small enough
if len(cur)<=1500:
    order=sorted(cur,key=lambda v:-math.hypot(*xy[v]))
    for v in order:
        trial=[u for u in cur if u!=v]
        r,_,_,_=solve(trial,proof=False,budget=300000)
        if r is False: cur=trial
    r,_,_,_=solve(cur,proof=False); assert r is False
print("final: %d vertices, radius %.4f, diameter %.4f (%.0fs)"%(len(cur),max(math.hypot(*xy[v]) for v in cur),max(math.dist(xy[a],xy[b]) for a in cur for b in cur),time.time()-t0),flush=True)
with open(out,"w") as f:
    for v in cur: f.write("%.15f %.15f\n"%xy[v])
print("wrote",out,flush=True)
