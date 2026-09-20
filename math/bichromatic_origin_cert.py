#!/usr/bin/env python3
"""Certificate: a unit-distance graph G (exact coordinates) with origin v such that G - v has no
4-coloring with N(v) 2-colored, i.e. G with v doubled is 5-chromatic ("5-chromatic graph with a
bichromatic origin", the finite core of Falconer's measurable-chi>=5 argument).
Found by radius restriction + greedy deletion in the depth-2 exact universe; DRAT proof emitted."""
import sys, time
from bichromatic_search import build_universe
from surgery import exact_unit_edges
from pysat.solvers import Cadical153
def sat(n,edges,k,forbid,want_proof=False):
    var=lambda v,c: v*k+c+1
    cl=[[var(v,c) for c in range(k)] for v in range(n)]
    for a,b in edges:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    for v,cs in forbid.items():
        for c in cs: cl.append([-var(v,c)])
    s=Cadical153(bootstrap_with=cl,with_proof=want_proof); r=s.solve()
    pr=s.get_proof() if (want_proof and not r) else None; s.delete(); return r,cl,pr
def inst(U,E,keepset,origin):
    keep=[v for v in sorted(keepset) if v!=origin]; idx={v:i for i,v in enumerate(keep)}
    E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
    N0={b for a,b in E if a==origin}|{a for a,b in E if b==origin}
    return keep,E2,{idx[u]:[0,1] for u in N0 if u in idx}
K=int(sys.argv[1]) if len(sys.argv)>1 else 4; R2=float(sys.argv[2]) if len(sys.argv)>2 else 2.5
U=build_universe(2,9); E=exact_unit_edges(U); n=len(U)
origin=next(i for i,p in enumerate(U) if p.norm2().is_zero())
keep={v for v in range(n) if U[v].norm2().to_float()<=R2+1e-9}
t0=time.time()
for v in sorted(keep-{origin}, key=lambda v:-U[v].norm2().to_float()):
    kp,E2,fb=inst(U,E,keep-{v},origin)
    if not sat(len(kp),E2,K,fb)[0]: keep.discard(v)
sub=sorted(keep); Es=[(a,b) for a,b in E if a in keep and b in keep]
print("minimized in %.0fs: |V|=%d (incl. origin) |E|=%d  deg(origin)=%d"%(time.time()-t0,len(sub),len(Es),sum(1 for a,b in Es if origin in (a,b))))
gcol=sat(len(sub),[(sub.index(a),sub.index(b)) for a,b in Es],K,{})[0]
print("G itself %d-colorable: %s   (so the doubled origin is what forces color %d)"%(K,gcol,K+1))
kp,E2,fb=inst(U,E,keep,origin); r,cl,pr=sat(len(kp),E2,K,fb,want_proof=True)
assert r is False
open("notes/bichromatic_origin_k%d.cnf"%K,"w").write("p cnf %d %d\n"%(len(kp)*K,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
open("notes/bichromatic_origin_k%d.drat"%K,"w").write("\n".join(pr)+"\n")
with open("notes/bichromatic_origin_k%d_vertices.txt"%K,"w") as f:
    f.write("# exact coordinates; first line is the origin v. Edges = all pairs at exact unit distance.\n")
    f.write("%r\n"%U[origin])
    for v in sub:
        if v!=origin: f.write("%r\n"%U[v])
print("wrote notes/bichromatic_origin_k%d_{vertices.txt,cnf,drat}; proof lines: %d"%(K,len(pr)))
