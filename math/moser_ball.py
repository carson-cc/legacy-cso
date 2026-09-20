#!/usr/bin/env python3
"""Correct Moser-lattice ball: seed unit vectors w^k * w1^j (w = 60 deg, w1: cos 5/6), |j| <= J,
depth-m Minkowski sums with a radius cap. Exact arithmetic (udg.F). Then: membership of the
CNP 510 graph, exact unit edges, 4-colorability (DRAT if UNSAT), and star0 at the origin."""
import sys, time, math, pickle
from fractions import Fraction as Fr
from udg import F, P, unit_from_cos, OMEGA
from surgery import exact_unit_edges
from pysat.solvers import Cadical153
J=int(sys.argv[1]); depth=int(sys.argv[2]); R=float(sys.argv[3]); vtx=sys.argv[4] if len(sys.argv)>4 else None
# generator: half of the Moser angle, cos = sqrt(33)/6, sin = sqrt(3)/6  (its square is cos 5/6)
w1=P(F.root(33,Fr(1,6)),F.root(3,Fr(1,6))); w1b=P(w1.x,-w1.y)
assert w1.cmul(w1)==unit_from_cos(5,6)
seed={}
for j in range(-J,J+1):
    r=P(F.const(1),F.const(0))
    for _ in range(abs(j)): r=r.cmul(w1 if j>0 else w1b)
    for k in range(6):
        seed[r.key()]=r; r=r.cmul(OMEGA)
U=list(seed.values()); print("seed unit vectors:",len(U),flush=True)
t0=time.time(); ball={P(F.const(0),F.const(0)).key():P(F.const(0),F.const(0))}; frontier=list(ball.values())
for d in range(depth):
    new={}
    for p in frontier:
        for u in U:
            q=p+u
            if q.norm2().to_float()<=R*R+1e-9 and q.key() not in ball: new[q.key()]=q
    ball.update(new); frontier=list(new.values())
    print("depth %d: |ball|=%d (+%d) %.0fs"%(d+1,len(ball),len(new),time.time()-t0),flush=True)
pts=list(ball.values()); n=len(pts)
if vtx:
    from chord_angle import parse_vtx
    S={(round(x,7),round(y,7)) for x,y in (p.to_float() for p in pts)}
    G=parse_vtx(vtx); inb=sum(1 for x,y in G if (round(x,7),round(y,7)) in S)
    print("CNP graph points inside ball: %d / %d"%(inb,len(G)),flush=True)
E=exact_unit_edges(pts); print("exact unit edges: %d (%.0fs)"%(len(E),time.time()-t0),flush=True)
pickle.dump((pts,E),open("notes/moser_ball_J%d_d%d_R%g.pkl"%(J,depth,R),"wb"))
adj={}
for a,b in E: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
def color(k,forbid,budget,proof=False):
    var=lambda u,c: u*k+c+1
    cl=[[var(u,c) for c in range(k)] for u in range(n)]
    for a,b in E:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    for u,cs in forbid.items():
        for c in cs: cl.append([-var(u,c)])
    for a,b in E:
        com=adj[a]&adj[b]
        if com and not forbid:
            for c,u in enumerate((a,b,min(com))): cl.append([var(u,c)])
            break
    s=Cadical153(bootstrap_with=cl,with_proof=proof); s.conf_budget(budget); r=s.solve_limited()
    pr=s.get_proof() if (proof and r is False) else None; s.delete(); return r,pr,cl
t=time.time(); r,pr,cl=color(4,{},50_000_000,proof=True)
print("4-colorable: %s (%.0fs)"%({True:'SAT',False:'UNSAT',None:'UNKNOWN'}[r],time.time()-t),flush=True)
if r is False:
    tag="moser_ball_J%d_d%d_R%g"%(J,depth,R)
    open("notes/%s_k4.cnf"%tag,"w").write("p cnf %d %d\n"%(n*4,len(cl))+"".join(" ".join(map(str,c))+" 0\n" for c in cl))
    open("notes/%s_k4.drat"%tag,"w").write("\n".join(pr)+"\n"); print("DRAT lines:",len(pr),flush=True)
origin=next(i for i,p in enumerate(pts) if p.norm2().is_zero())
forb={u:[0,1] for u in adj.get(origin,())}
t=time.time(); r0,_,_=color(5,forb,50_000_000)
print("star0 at origin (deg %d): %s (%.0fs)"%(len(adj.get(origin,())),{True:'SAT',False:'UNSAT (HIT)',None:'UNKNOWN'}[r0],time.time()-t),flush=True)
