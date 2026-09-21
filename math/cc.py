#!/usr/bin/env python3
"""Minimal cube-and-conquer driver: cubes from an icnf file ('a lits 0' lines), each cube solved by kissat
on CNF+units with a time limit, W workers. Any SAT cube => SAT (model saved). All UNSAT => UNSAT.
Timeouts are re-queued for a second pass with a longer limit, then reported as UNKNOWN.
If a drat-trim binary is given, every UNSAT cube is solved with a DRAT proof which is checked by
drat-trim against CNF+cube (the proof is deleted after a successful check; the cube counts as UNSAT
only if drat-trim prints VERIFIED). A per-cube verdict log <workdir>/verdicts.txt is appended.
Usage: cc.py <cnf> <cubes.icnf> <workdir> <workers> <time_per_cube_s> <kissat> [drat-trim]"""
import sys, os, subprocess, time, concurrent.futures as cf
cnf,cubes,wd,W,T,K=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
DT=sys.argv[7] if len(sys.argv)>7 else None
os.makedirs(wd,exist_ok=True)
hdr=None; body=[]
for line in open(cnf):
    if line.startswith('p'): hdr=line.split()
    elif line.strip() and not line.startswith('c'): body.append(line)
nv,nc=int(hdr[2]),int(hdr[3])
cl=[l.strip() for l in open(cubes) if l.startswith('a')]
cubes_lits=[[int(x) for x in l.split()[1:-1]] for l in cl]
print("cubes: %d"%len(cubes_lits),flush=True)
done={}
vf="%s/verdicts.txt"%wd
if os.path.exists(vf):
    for l in open(vf):
        t=l.split()
        if len(t)>=2 and t[1] in ("UNSAT","SAT"): done[int(t[0])]=t[1]
    print("resuming: %d cubes already decided"%len(done),flush=True)
def solve(i,tl):
    lits=cubes_lits[i]; f="%s/c%06d.cnf"%(wd,i); pf="%s/c%06d.drat"%(wd,i)
    with open(f,"w") as g:
        g.write("p cnf %d %d\n"%(nv,nc+len(lits))); g.writelines(body)
        for x in lits: g.write("%d 0\n"%x)
    t=time.time()
    cmd=[K,"-q","--time=%d"%tl,f]+([pf] if DT else [])
    r=subprocess.run(cmd,capture_output=True,text=True)
    out=r.stdout
    if "s UNSATISFIABLE" in out:
        v="UNSAT"
        if DT:
            d=subprocess.run([DT,f,pf],capture_output=True,text=True)
            if "VERIFIED" not in d.stdout: v="UNVERIFIED"
            else: os.remove(pf)
    elif "s SATISFIABLE" in out: v="SAT"; open("%s/model_%06d.txt"%(wd,i),"w").write(out)
    else: v="UNKNOWN"
    os.remove(f)
    if os.path.exists(pf) and v!="UNVERIFIED": os.remove(pf)
    with open(vf,"a") as g: g.write("%d %s %.0f\n"%(i,v,time.time()-t))
    return i,v,time.time()-t
t0=time.time(); res=dict(done); pending=[i for i in range(len(cubes_lits)) if i not in done]; tl=T
for rnd in (1,2):
    if not pending: break
    with cf.ThreadPoolExecutor(max_workers=W) as ex:
        for i,v,dt in ex.map(lambda i: solve(i,tl), pending):
            res[i]=v; print("cube %d: %s (%.0fs) [%d/%d, %.0fs]"%(i,v,dt,len(res),len(cubes_lits),time.time()-t0),flush=True)
            if v=="SAT": print("SAT CUBE FOUND -> instance SATISFIABLE",flush=True)
    pending=[i for i in pending if res[i] in ("UNKNOWN","UNVERIFIED")]; tl=T*4
    print("round %d done: unknown=%d (%.0fs)"%(rnd,len(pending),time.time()-t0),flush=True)
c={v:list(res.values()).count(v) for v in ("UNSAT","SAT","UNKNOWN","UNVERIFIED")}
print("DONE",c,"=> %s"%("SAT" if c["SAT"] else ("UNSAT" if c["UNKNOWN"]+c["UNVERIFIED"]==0 else "UNKNOWN")),flush=True)
