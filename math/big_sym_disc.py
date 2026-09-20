#!/usr/bin/env python3
"""Richest point set inside a disc: translate union of the 510 graph, closed under the 36 symmetries about
the origin (6 rotations x reflection x omega_1^{-1,0,1}), restricted to |x| < R. Float merge; edges by
float unit test. Writes a 'p edge' file + .xy."""
import sys, math
xyfile,R,out=sys.argv[1],float(sys.argv[2]),sys.argv[3]
base=[tuple(map(float,l.split())) for l in open(xyfile)]
base=[(x,y) for x,y in base if math.hypot(x,y)<R]
syms=[]
for k in range(6):
    ck,sk=math.cos(k*math.pi/3),math.sin(k*math.pi/3)
    for refl in (1,-1):
        for j in (-1,0,1):
            cj,sj=math.cos(j*math.acos(5/6)),math.sin(j*math.acos(5/6)); syms.append((ck,sk,refl,cj,sj))
pts={}
for x,y in base:
    for ck,sk,refl,cj,sj in syms:
        X,Y=x,y*refl; X,Y=X*ck-Y*sk,X*sk+Y*ck; X,Y=X*cj-Y*sj,X*sj+Y*cj
        pts.setdefault((round(X,8),round(Y,8)),(X,Y))
P=list(pts.values()); n=len(P)
g={}
for i,(x,y) in enumerate(P): g.setdefault((int(math.floor(x*2)),int(math.floor(y*2))),[]).append(i)
E=[]
for (cx,cy),idx in g.items():
    for dx in (-2,-1,0,1,2):
        for dy in (-2,-1,0,1,2):
            for b in g.get((cx+dx,cy+dy),()):
                for a in idx:
                    if a<b and abs(math.hypot(P[a][0]-P[b][0],P[a][1]-P[b][1])-1)<1e-8: E.append((a,b))
with open(out,"w") as f:
    f.write("p edge %d %d\n"%(n,len(E)))
    for a,b in E: f.write("e %d %d\n"%(a+1,b+1))
with open(out+".xy","w") as f:
    for x,y in P: f.write("%.15f %.15f\n"%(x,y))
print("symmetric disc set R=%.2f: |V|=%d |E|=%d"%(R,n,len(E)),flush=True)
