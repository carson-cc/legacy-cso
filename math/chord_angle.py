#!/usr/bin/env python3
"""For a (v,z) hit: read Mathematica-style .vtx coordinates, report d=|vz|, the unit-chord rotation
angle beta = 2*arcsin(1/(2d)) on the circle of radius d, and whether beta/pi is numerically close to a
rational with small denominator (a rigorous irrationality proof is a separate algebraic step)."""
import sys, re, math
from fractions import Fraction
def parse_vtx(path):
    pts=[]
    for line in open(path):
        line=line.strip()
        if not line: continue
        expr=line.strip("{}").replace("Sqrt[","math.sqrt(").replace("]",")")
        x,y=[eval(e,{"math":math}) for e in expr.split(",")]
        pts.append((x,y))
    return pts
if __name__=="__main__":
    pts=parse_vtx(sys.argv[1]); v=int(sys.argv[2]); z=int(sys.argv[3])   # 0-based
    d=math.dist(pts[v],pts[z]); beta=2*math.asin(1/(2*d)) if d>=0.5 else float('nan')
    fr=Fraction(beta/math.pi).limit_denominator(10000)
    print("v=%d z=%d  d=%.12f  beta/pi=%.12f  nearest p/q (q<=1e4)=%s err=%.2e"%(v,z,d,beta/math.pi,fr,abs(beta/math.pi-fr)))
