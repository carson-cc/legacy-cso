#!/usr/bin/env python3
"""Union of all CNP-SAT graphs and their images under lattice symmetries about the origin
(rotations by 60 deg, reflection, and rotations by omega_1^{+-1}, cos = 5/6). All CNP graphs contain
the origin as vertex 0, so the union is a much richer unit-distance graph around the origin, and the
doubled-vertex criterion is monotone in the graph. Float merge + float unit edges (search mode)."""
import sys, math, glob, itertools
from chord_angle import parse_vtx
D=sys.argv[1]; out=sys.argv[2]; use_w1=int(sys.argv[3]) if len(sys.argv)>3 else 1
c1,s1=5/6,math.sqrt(11)/6
def rotn(x,y,c,s): return (x*c-y*s, x*s+y*c)
syms=[]
for k in range(6):
    ck,sk=math.cos(k*math.pi/3),math.sin(k*math.pi/3)
    for refl in (1,-1):
        for j in range(-use_w1,use_w1+1):
            cj,sj=math.cos(j*math.acos(5/6)),math.sin(j*math.acos(5/6))
            syms.append((ck,sk,refl,cj,sj))
pts={}
for f in sorted(glob.glob(D+"/*.vtx")):
    for x,y in parse_vtx(f):
        for ck,sk,refl,cj,sj in syms:
            X,Y=x,y*refl; X,Y=rotn(X,Y,ck,sk); X,Y=rotn(X,Y,cj,sj)
            key=(round(X,8),round(Y,8))
            if key not in pts: pts[key]=(X,Y)
P=list(pts.values()); n=len(P)
origin=next(i for i,(x,y) in enumerate(P) if abs(x)<1e-9 and abs(y)<1e-9)
P[0],P[origin]=P[origin],P[0]
g={}
for i,(x,y) in enumerate(P): g.setdefault((int(math.floor(x)),int(math.floor(y))),[]).append(i)
E=[]
for (cx,cy),idx in g.items():
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for b in g.get((cx+dx,cy+dy),()):
                for a in idx:
                    if a<b and abs(math.hypot(P[a][0]-P[b][0],P[a][1]-P[b][1])-1)<1e-8: E.append((a,b))
with open(out,"w") as f:
    f.write("p edge %d %d\n"%(n,len(E)))
    for a,b in E: f.write("e %d %d\n"%(a+1,b+1))
with open(out+".xy","w") as f:
    for x,y in P: f.write("%.15f %.15f\n"%(x,y))
deg0=sum(1 for a,b in E if 0 in (a,b))
print("orbit union: |V|=%d |E|=%d  deg(origin)=%d  (%d symmetries)"%(n,len(E),deg0,len(syms)))
