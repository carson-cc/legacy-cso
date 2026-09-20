import math, sys
from fractions import Fraction as Fr
from udg import F, P, OMEGA
from chord_angle import parse_vtx
wh=P(F.root(33,Fr(1,6)),F.root(3,Fr(1,6))); whb=P(wh.x,-wh.y)
G=parse_vtx(sys.argv[1]); Gk={(round(x,7),round(y,7)) for x,y in G}
for J in (2,3,4):
    seed={}
    for j in range(-J,J+1):
        r=P(F.const(1),F.const(0))
        for _ in range(abs(j)): r=r.cmul(wh if j>0 else whb)
        for k in range(6): seed[r.key()]=r; r=r.cmul(OMEGA)
    U=[p.to_float() for p in seed.values()]
    ball={(0.0,0.0)}; frontier=[(0.0,0.0)]
    for d in range(5):
        new=set()
        for (x,y) in frontier:
            for (ux,uy) in U:
                q=(round(x+ux,7),round(y+uy,7))
                if q[0]**2+q[1]**2<=3.2**2 and q not in ball: new.add(q)
        ball|=new; frontier=list(new)
        print("J=%d depth=%d |ball|=%d  graph points inside: %d/%d"%(J,d+1,len(ball),len(Gk&ball),len(G)),flush=True)
        if len(Gk&ball)==len(G) or len(ball)>400000: break
