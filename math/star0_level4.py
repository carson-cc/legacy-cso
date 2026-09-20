#!/usr/bin/env python3
"""Reproduce a '5-chromatic graph with a bichromatic origin' (Falconer/Polymath16 route to
measurable chi >= 5): find G in the exact universe, v = origin, such that
   G - v has NO 4-coloring in which N(v) uses only 2 colors   (v doubled => 5-chromatic).
Then greedily minimize the vertex set keeping the property, and emit a DRAT-checked certificate."""
import sys, random
from bichromatic_search import build_universe
from surgery import exact_unit_edges
from pysat.solvers import Cadical153

def sat(n, edges, k, forbid, want_proof=False):
    var=lambda v,c: v*k+c+1
    cl=[[var(v,c) for c in range(k)] for v in range(n)]
    for a,b in edges:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    for v,cs in forbid.items():
        for c in cs: cl.append([-var(v,c)])
    s=Cadical153(bootstrap_with=cl, with_proof=want_proof); r=s.solve()
    pr=s.get_proof() if (want_proof and not r) else None; s.delete(); return r,cl,pr

def test(U, E, keepset, origin, k):
    """k-color (G[keep] - origin) with N(origin) forbidden colors {0,1}: True if colorable."""
    keep=[v for v in keepset if v!=origin]; idx={v:i for i,v in enumerate(keep)}
    E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
    N0={b for a,b in E if a==origin}|{a for a,b in E if b==origin}
    forb={idx[u]:[0,1] for u in N0 if u in idx}
    return sat(len(keep),E2,k,forb)[0]

depth=int(sys.argv[2]) if len(sys.argv)>2 else 1
U=build_universe(depth,9); E=exact_unit_edges(U); n=len(U)
origin=next(i for i,p in enumerate(U) if p.norm2().is_zero())
k=int(sys.argv[1]) if len(sys.argv)>1 else 4
full=set(range(n))
r=test(U,E,full,origin,k)
print("universe |V|=%d: (%d-1)-coloring of G-origin with N(origin) 2-colored -> %s"%(n,k+1,"SAT" if r else "UNSAT (bichromatic-origin graph exists)"))
if r: sys.exit(0)
random.seed(1); keep=set(full)
order=sorted(full-{origin}, key=lambda v: U[v].norm2().to_float(), reverse=True)
for v in order:
    if v not in keep: continue
    trial=keep-{v}
    if not test(U,E,trial,origin,k): keep=trial
print("minimized: |V|=%d (incl. origin), |E|=%d"%(len(keep), sum(1 for a,b in E if a in keep and b in keep)))
sub=sorted(keep); print("vertices:"); 
for v in sub: print("  ", "ORIGIN" if v==origin else "", U[v])
# certificate
keepl=[v for v in sub if v!=origin]; idx={v:i for i,v in enumerate(keepl)}
E2=[(idx[a],idx[b]) for a,b in E if a in idx and b in idx]
N0={b for a,b in E if a==origin}|{a for a,b in E if b==origin}
forb={idx[u]:[0,1] for u in N0 if u in idx}
r,cl,pr=sat(len(keepl),E2,k,forb,want_proof=True)
open("notes/bichromatic_origin_k%d.cnf"%k,"w").write("p cnf %d %d\n"%(len(keepl)*k,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
open("notes/bichromatic_origin_k%d.drat"%k,"w").write("\n".join(pr)+"\n")
print("certificate written (%d proof lines); G itself %d-colorable: %s"%(len(pr),k, sat(len(sub),[(sub.index(a),sub.index(b)) for a,b in E if a in keep and b in keep],k,{})[0]))
