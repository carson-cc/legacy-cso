#!/usr/bin/env python3
"""
Search for the finite combinatorial core of a Falconer-type argument for measurable chi >= 6.

Falconer's proof of measurable chi(R^2) >= 5 is, combinatorially: the unit rhombus (O,p,q,z)
with the origin O DOUBLED into two vertices of different colors (a "bichromatic" boundary point)
and z joined to both copies is K_5, hence not 4-colorable; measurability realizes the doubled
vertex (essential-boundary point) and the virtual O--z edges (irrational rotation on the |Oz| circle).

Generalization (star): a unit-distance graph G with vertices v, z such that
   G with v doubled (v1,v2 same neighbors, c(v1)!=c(v2)) and z joined to v1,v2 is NOT 5-colorable.
Equivalently: 5-color G-{v} with N(v) forbidden colors {1,2} and z forbidden {1,2}  -> UNSAT.
Necessary condition when G is 4-colorable: (v,z) forced-equal in every 4-coloring of G.

This script tests, for G = exact unit-distance graph on a universe of points and v = origin:
  (a) forced-equal pairs (v,z) under 4-colorings;
  (b) the (star) condition under 5-colorings.
"""
import sys, itertools
from fractions import Fraction as Fr
from pysat.solvers import Cadical153
from udg import F, P, unit_from_cos, rotate_set, conj, OMEGA, HEX7, minkowski
from surgery import exact_unit_edges

def build_universe(depth, normbound):
    G0=list(HEX7)
    for r in (unit_from_cos(5,6),unit_from_cos(7,8)): G0+=rotate_set(HEX7,r)+rotate_set(HEX7,conj(r))
    uni={}; cur=G0
    for j in range(6):
        for p in cur: uni[p.key()]=p
        cur=rotate_set(cur,OMEGA)
    U=list(uni.values())
    for _ in range(depth):
        U=[p for p in minkowski(U,list(uni.values())) if p.norm2().to_float()<=normbound]
    return list({p.key():p for p in U}.values())

def solve(n, edges, k, forbid):
    var=lambda v,c: v*k+c+1
    cl=[[var(v,c) for c in range(k)] for v in range(n)]
    for a,b in edges:
        for c in range(k): cl.append([-var(a,c),-var(b,c)])
    for v,cs in forbid.items():
        for c in cs: cl.append([-var(v,c)])
    s=Cadical153(bootstrap_with=cl); r=s.solve(); s.delete(); return r

if __name__=="__main__":
    depth=int(sys.argv[1]); nb=float(sys.argv[2])
    U=build_universe(depth,nb); E=exact_unit_edges(U); n=len(U)
    origin=next(i for i,p in enumerate(U) if p.norm2().is_zero())
    adj={}
    for a,b in E: adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
    N0=adj.get(origin,set())
    print("universe depth=%d norm<=%g: |V|=%d |E|=%d  deg(origin)=%d  4-colorable=%s"%(depth,nb,n,len(E),len(N0),solve(n,E,4,{})))
    # (a) forced-equal pairs under 4-colorings: UNSAT of "c(origin)=0 and c(z)!=0"
    fe=[]
    for z in range(n):
        if z==origin or z in N0: continue
        if not solve(n,E,4,{origin:[1,2,3], z:[0]}): fe.append(z)
    print("(a) forced-equal partners of origin under 4-colorings:",len(fe), [ (U[z].norm2().to_float()) for z in fe][:10])
    # (b) star condition: 5 colors, origin removed, N(origin) forbidden {0,1}, z forbidden {0,1}
    keep=[i for i in range(n) if i!=origin]; idx={v:i for i,v in enumerate(keep)}
    E2=[(idx[a],idx[b]) for a,b in E if a!=origin and b!=origin]
    forb={idx[u]:[0,1] for u in N0}
    star=[]
    for z in range(n):
        if z==origin or z in N0: continue
        f=dict(forb); f[idx[z]]=[0,1]
        if not solve(len(keep),E2,5,f): star.append(z)
    print("(b) star-condition partners (5 colors, doubled origin):",len(star), [U[z].norm2().to_float() for z in star][:10])
