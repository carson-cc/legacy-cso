#!/usr/bin/env python3
"""Independent check that a cube set is a complete case split for a pinned k-colouring CNF:
(1) the cubes are positive literals on distinct vertices and pairwise distinct; (2) every assignment
of colours to the union of the split vertices that is consistent with the CNF's binary (edge) clauses
among split/pinned vertices, and with the CNF's unit clauses, satisfies some cube (leaf cubes may live
on different vertex sets, as produced by cc.py's refinement).
Assignments that violate such a clause are refuted by the CNF itself, so (1)-(3) imply that
"every leaf cube UNSAT" => "CNF UNSAT". Usage: cube_cover_check.py <cnf> <leaves.icnf> [k=4]"""
import sys, itertools
cnf,cubes=sys.argv[1],sys.argv[2]; k=int(sys.argv[3]) if len(sys.argv)>3 else 4
units={}; bins=set()
for line in open(cnf):
    t=line.split()
    if not t or t[0] in ('p','c'): continue
    lits=[int(x) for x in t[:-1]]
    if len(lits)==1: units[lits[0]]=True
    elif len(lits)==2: bins.add(tuple(sorted(lits)))
vertex=lambda lit:(abs(lit)-1)//k; colour=lambda lit:(abs(lit)-1)%k
pin={vertex(l):colour(l) for l in units if l>0}
C=[[int(x) for x in l.split()[1:-1]] for l in open(cubes) if l.startswith('a')]
S=sorted({vertex(l) for c in C for l in c})
assert all(all(l>0 for l in c) and len({vertex(l) for l in c})==len(c) for c in C), "bad cube"
assert len({tuple(sorted(c)) for c in C})==len(C), "duplicate cubes"
assert not set(S)&set(pin), "cube touches a pinned vertex"
# leaf cubes may live on different vertex sets (refined cubes); index them by vertex set
shapes={}
for c in C: shapes.setdefault(tuple(sorted(vertex(l) for l in c)),set()).add(tuple(sorted(c)))
n_ok=0
rel=set(S)|set(pin)
bins=[(a,b) for a,b in bins if vertex(a) in rel and vertex(b) in rel]
# backtracking enumeration over the split vertices in order S, checking binary clauses as we go
by_v={}
for a,b in bins: by_v.setdefault(vertex(a),[]).append((a,b)); by_v.setdefault(vertex(b),[]).append((a,b))
def sat(lit,asg): return (asg[vertex(lit)]==colour(lit))==(lit>0)
def rec(i,asg):
    global n_ok
    if i==len(S):
        n_ok+=1
        assert any(tuple(v*k+asg[v]+1 for v in sh) in cs for sh,cs in shapes.items()), "uncovered assignment %r"%(asg,)
        return
    v=S[i]
    for c in range(k):
        asg[v]=c
        if all(sat(a,asg) or sat(b,asg) for a,b in by_v.get(v,[]) if vertex(a) in asg and vertex(b) in asg):
            rec(i+1,asg)
        del asg[v]
rec(0,dict(pin))
print("cover OK: %d split vertices, %d admissible assignments, %d leaf cubes on %d vertex sets"%(len(S),n_ok,len(C),len(shapes)))
