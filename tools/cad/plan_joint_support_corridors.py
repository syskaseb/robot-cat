"""One bounded common corridor plan for all four fixed support roots.

No detailed CAD variants: sampled existing wire jackets and actual solid
interiors constrain a6mm square beam before the shared BRep/motion gate.
This screen cannot certify clearance or mechanical strength.
"""
import heapq,itertools,json,math,time
from pathlib import Path
import FreeCAD as A
from plan_low_power_station_mounts import scene,allocate as station_mounts
from plan_current_main_sources import ROOT,OUT,SHA


def run():
    tick=time.monotonic();targets,wires,archive=scene()
    family_file=OUT/'low-joint-family-plan.json';family=json.loads(family_file.read_text())
    grid={};cell=8;half=3;extra=.8
    for name,(s,r) in wires.items():
        for edge in s.Edges:
            for p in edge.discretize(Distance=1):
                v=list(p);key=tuple(math.floor(x/cell) for x in v)
                grid.setdefault(key,[]).append((v,r,name))
    _,hardware,_=station_mounts(targets)
    material=[(n,s,s.BoundBox) for n,s in {**targets,**hardware}.items() if s.Solids]
    clear_cache={};blockers={}
    def clear(p):
        key=tuple(p)
        if key not in clear_cache:clear_cache[key]=uncached_clear(p)
        return clear_cache[key]
    def uncached_clear(p):
        key=tuple(math.floor(x/cell) for x in p)
        for d in itertools.product((-1,0,1),repeat=3):
            for v,r,n in grid.get(tuple(x+y for x,y in zip(key,d)),()):
                # Full box distance rather than an unnecessarily broad sphere.
                gap2=sum(max(0,abs(a-b)-half)**2 for a,b in zip(p,v))
                if gap2<(r+extra+.5)**2:blockers[tuple(p)]=['wire',n];return False
        for n,s,b in material:
            # Tangent bearing faces are not positive-volume interference.
            if not (b.XMin-half+1e-5<p[0]<b.XMax+half-1e-5 and b.YMin-half+1e-5<p[1]<b.YMax+half-1e-5 and b.ZMin-half+1e-5<p[2]<b.ZMax+half-1e-5):continue
            for d in [(0,0,0)]+list(itertools.product((-half,half),repeat=3)):
                if s.isInside(A.Vector(*(a+v for a,v in zip(p,d))),1e-6,False):blockers[tuple(p)]=['material',n];return False
        return True
    rows=[]
    for leg in dict.fromkeys(r['physical_leg'] for r in family['hips']):
        r=next(v for v in family['hips'] if v['physical_leg']==leg)
        side=r['side'];x=r['fixed_anchor_world_mm'][0];cx=40 if leg.startswith('Front') else 115
        # Root top is the actual washer bearing plane43.52, not rounded44.
        # Backbones/posts sit on +X of every jacket, away from W037 source.
        # Outboard takeoff: washer Ymax58.5 + beam half3 +0.5 margin.
        # A short integral tongue joins the original clamp; routing need
        # not waive its own bolt shank or drill a new chassis hole.
        start=[cx,side*62,43.52-half];goal=[x+4.5,side*96,38]
        if not clear(start) or not clear(goal):
            rows.append(dict(leg=leg,points_mm=[],expansions=0,start_clear=clear(start),goal_clear=clear(goal),start_blocker=blockers.get(tuple(start)),goal_blocker=blockers.get(tuple(goal))))
            print('root endpoint blocked',leg,flush=True);continue
        axes=[sorted(set([float(v) for v in range(math.floor(min(a,b)-12),math.ceil(max(a,b)+12)+1,4)]+[a,b])) for a,b in zip(start,goal)]
        # Shared allocated height budget, not an unbounded escape above robot.
        axes[2]=sorted(set(list(range(38,63,4))+[38,start[2]]))
        first=tuple(v.index(a) for v,a in zip(axes,start));last=tuple(v.index(a) for v,a in zip(axes,goal))
        def point(k):return [axes[i][j] for i,j in enumerate(k)]
        def heur(k):return sum(abs(a-b) for a,b in zip(point(k),goal))
        queue=[(heur(first),0,first)];best={first:0};parent={};checked={};expansions=0;found=None
        while queue and expansions<5000:
            _,cost,k=heapq.heappop(queue)
            if cost!=best[k]:continue
            expansions+=1
            if k==last:found=k;break
            for i in range(3):
                for step in (-1,1):
                    kk=list(k);kk[i]+=step
                    if not 0<=kk[i]<len(axes[i]):continue
                    kk=tuple(kk);p=point(kk);q=point(k)
                    if kk not in checked:checked[kk]=clear(p)
                    if not checked[kk] or not clear([(a+b)/2 for a,b in zip(p,q)]):continue
                    nc=cost+math.dist(p,q)
                    if nc>=best.get(kk,1e20):continue
                    best[kk]=nc;parent[kk]=k;heapq.heappush(queue,(nc+heur(kk),nc,kk))
        path=[]
        if found:
            k=found;path=[point(k)]
            while k!=first:k=parent[k];path.append(point(k))
            path.reverse()
            # Keep only direction changes. Each segment will become one pad.
            simple=[path[0]]
            for a,b,c in zip(path,path[1:],path[2:]):
                if next(i for i in range(3) if a[i]!=b[i])!=next(i for i in range(3) if b[i]!=c[i]):simple.append(b)
            simple.append(path[-1]);path=simple
        rows.append(dict(leg=leg,points_mm=path,expansions=expansions,start_clear=clear(start),goal_clear=clear(goal)))
        print('root corridor',leg,len(path),'knots',expansions,'states',flush=True)
    report=dict(status='FOUR_ROOT_CORRIDORS_SCREEN_CLEAR_BREP_MOTION_OPEN' if all(r['points_mm'] and r['start_clear'] and r['goal_clear'] for r in rows) else 'REJECTED_ROOT_CORRIDOR_PLAN',
        beam_square_mm=6,wire_margin_mm=extra,roots=rows,selected=False,physical_pass=False,
        scope='Sampled jacket/actual solid interiors only; full valid BRep, all support interferences, sampled motion, tool access and PETG load gates remain mandatory.',
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (archive,family_file,Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'joint-support-corridors-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':run()
