#!/usr/bin/env python3
"""Minimal cube-and-conquer driver: cubes from march_cu (icnf 'a ... 0' lines), each cube solved by kissat
on CNF+units with a time limit, W workers. Any SAT cube => SAT (model saved). All UNSAT => UNSAT.
Timeouts are re-queued for a second pass with a longer limit, then reported as UNKNOWN.
Usage: cc.py <cnf> <cubes.icnf> <workdir> <workers> <time_per_cube_s> <kissat>"""
import sys, os, subprocess, time, concurrent.futures as cf
cnf,cubes,wd,W,T,K=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
os.makedirs(wd,exist_ok=True)
hdr=None; body=[]
for line in open(cnf):
    if line.startswith('p'): hdr=line.split()
    elif line.strip() and not line.startswith('c'): body.append(line)
nv,nc=int(hdr[2]),int(hdr[3])
cl=[l.strip() for l in open(cubes) if l.startswith('a')]
cubes_lits=[[int(x) for x in l.split()[1:-1]] for l in cl]
print("cubes: %d"%len(cubes_lits),flush=True)
def solve(i,tl):
    lits=cubes_lits[i]; f="%s/c%06d.cnf"%(wd,i)
    with open(f,"w") as g:
        g.write("p cnf %d %d\n"%(nv,nc+len(lits))); g.writelines(body)
        for x in lits: g.write("%d 0\n"%x)
    t=time.time(); r=subprocess.run([K,"-q","--time=%d"%tl,f],capture_output=True,text=True)
    out=r.stdout; os.remove(f)
    if "s UNSATISFIABLE" in out: v="UNSAT"
    elif "s SATISFIABLE" in out: v="SAT"; open("%s/model_%06d.txt"%(wd,i),"w").write(out)
    else: v="UNKNOWN"
    return i,v,time.time()-t
t0=time.time(); res={}; pending=list(range(len(cubes_lits))); tl=T
for rnd in (1,2):
    if not pending: break
    with cf.ThreadPoolExecutor(max_workers=W) as ex:
        for i,v,dt in ex.map(lambda i: solve(i,tl), pending):
            res[i]=v; print("cube %d: %s (%.0fs) [%d/%d, %.0fs]"%(i,v,dt,len(res),len(cubes_lits),time.time()-t0),flush=True)
            if v=="SAT": print("SAT CUBE FOUND -> instance SATISFIABLE",flush=True)
    pending=[i for i in pending if res[i]=="UNKNOWN"]; tl=T*4
    print("round %d done: unknown=%d (%.0fs)"%(rnd,len(pending),time.time()-t0),flush=True)
c={v:list(res.values()).count(v) for v in ("UNSAT","SAT","UNKNOWN")}
print("DONE",c,"=> %s"%("SAT" if c["SAT"] else ("UNSAT" if c["UNKNOWN"]==0 else "UNKNOWN")),flush=True)
