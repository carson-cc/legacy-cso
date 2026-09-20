#!/usr/bin/env python3
"""
Chromatic number experiments for epsilon-unit-distance graphs on lattice patches.

Vertices: points of a triangular lattice with spacing s inside a disc of radius R.
Edges:    pairs at Euclidean distance in (1-eps, 1+eps).
Question: is the patch k-colorable?  (UNSAT for k=5 => a 6-chromatic eps-UDG.)
Solver:   CaDiCaL via PySAT, with a conflict budget so runs terminate.
Verdicts: SAT (model verified against the edge list), UNSAT, or UNKNOWN (budget hit).
UNKNOWN is never reported as UNSAT.
"""
import sys, time, math, itertools
import numpy as np
from pysat.solvers import Cadical153

def tri_lattice(s, R):
    pts=[]
    n=int(R/s)+2
    for i in range(-n,n+1):
        for j in range(-n,n+1):
            x=s*(i+0.5*j); y=s*(math.sqrt(3)/2)*j
            if x*x+y*y<=R*R: pts.append((x,y))
    return np.array(pts)

def eps_edges(P, eps):
    d=np.sqrt(((P[:,None,:]-P[None,:,:])**2).sum(-1))
    iu=np.triu_indices(len(P),1)
    m=(np.abs(d[iu]-1.0)<eps)
    return list(zip(iu[0][m].tolist(), iu[1][m].tolist()))

def colorable(n, edges, k, conf_budget=2_000_000):
    var=lambda v,c: v*k+c+1
    cl=[[var(v,c) for c in range(k)] for v in range(n)]
    for a,b in edges:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    # symmetry breaking: fix a triangle if one exists, else an edge
    adj={}
    for a,b in edges: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
    fixed=[]
    for a,b in edges:
        common=adj[a]&adj[b]
        if common: fixed=[a,b,min(common)]; break
    if not fixed and edges: fixed=list(edges[0])
    for c,v in enumerate(fixed[:k]): cl.append([var(v,c)])
    s=Cadical153(bootstrap_with=cl)
    s.conf_budget(conf_budget)
    r=s.solve_limited()
    model=None
    if r is True:
        m=s.get_model(); model=[next(c for c in range(k) if m[var(v,c)-1]>0) for v in range(n)]
        assert all(model[a]!=model[b] for a,b in edges), "model verification failed"
    s.delete()
    return {True:"SAT",False:"UNSAT",None:"UNKNOWN"}[r], model

if __name__=="__main__":
    s=float(sys.argv[1]); R=float(sys.argv[2]); eps=float(sys.argv[3]); k=int(sys.argv[4])
    budget=int(sys.argv[5]) if len(sys.argv)>5 else 2_000_000
    P=tri_lattice(s,R); E=eps_edges(P,eps)
    t0=time.time(); verdict,_=colorable(len(P),E,k,budget)
    print("s=%.3f R=%.2f eps=%.3f k=%d  |V|=%d |E|=%d  -> %s  (%.1fs)"%(s,R,eps,k,len(P),len(E),verdict,time.time()-t0))
