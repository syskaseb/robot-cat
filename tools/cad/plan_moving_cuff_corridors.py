"""Shared moving-root plan against the WHOLE retained wire sweep.

The two fixed wires bound a wall in the rotating cuff frame; a guessed
constant crown level is not a solution. Search complete3x4x4mm routes around
that wall before native detail. Point clouds/solid-interior samples are a
conservative planning screen, not clearance, strength or continuous proof.
"""
import heapq,itertools,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import check_low_hip_loom_layout as P
from cad_reservation_math import triangle_box


def run():
    tick=time.monotonic();targets,wires,archive=P.scene()
    fp=P.OUT/'low-joint-family-plan.json';family=json.loads(fp.read_text())
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes'];zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={q['name']:q['stage'].split('_')[1:] for q in members if q['stage'].startswith('Motion_')}
    # Discretize once; includeALL retained wires, not just last contact owners.
    old=[(n,[p for e in s.Edges for p in e.discretize(Distance=1)],r) for n,(s,r) in wires.items()]
    roots=[];half=(1.5,2.,2.);cell=8.;margin=.5;meshes={}
    mesh_deflection=.3;surface_half=tuple(h+mesh_deflection+.5 for h in half)
    crown_top=18.51+math.cos(math.radians(15))*(55.8-18.51)-math.sin(math.radians(15))*(98-16)-1.05-.5
    for leg in dict.fromkeys(r['physical_leg'] for r in family['hips']):
        rows=[r for r in family['hips'] if r['physical_leg']==leg];r=rows[0]
        side=r['side'];front=leg.startswith('Front');code=r['cad_code'];mx=r['moving_anchor_rest_world_mm'][0]
        axis=next(q for q in axes if q['code']==code and q['stage']=='Hip');pv=A.Vector(*axis['pivot_mm'])
        def transform(angle):
            rot=A.Rotation(A.Vector(*axis['axis']),angle)
            return A.Placement(pv-rot.multVec(pv),rot)
        grid={};material=[]
        def addpoint(p,rad,name):
            if not mx-40<p.x<mx+40 or not 65<side*p.y<140 or not -8<p.z<65:return
            v=(p.x,side*p.y,p.z);key=tuple(math.floor(x/cell) for x in v)
            grid.setdefault(key,[]).append((v,rad,name))
        local_old=[(n,[p for p in pts if abs(p.x-mx)<45],rad) for n,pts,rad in old]
        for angle in range(-15,16):
            inv=transform(angle).inverse()
            for n,pts,rad in local_old:
                for p in pts:addpoint(inv.multVec(p),rad,n)
            for row in rows:
                s=P.wire(P.parts_at(row,angle))
                for e in s.Edges:
                    for p in e.discretize(Distance=1):addpoint(inv.multVec(p),3,row['section'])
        for row in family['knees']:
            if row['cad_code']!=code:continue
            for angle in range(-15,16):
                s=P.wire(P.scene_parts(row,0,angle,axes))
                for e in s.Edges:
                    for p in e.discretize(Distance=1):addpoint(p,3,row['section'])
        print('moving plan',leg,'wire sweep buckets',len(grid),flush=True)
        # Material at all coupled Hip/Knee/Ankle extrema in the cuff frame.
        material_seen=set();surface_grid={}
        for hip,knee,ankle in itertools.product((-15,0,15),repeat=3):
            T=A.Placement();trans={}
            for stage,angle in zip(('Hip','Knee','Ankle'),(hip,knee,ankle)):
                ax=next(q for q in axes if q['code']==code and q['stage']==stage)
                v=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(v-rot.multVec(v),rot);trans[stage]=T
            inv=trans['Hip'].inverse()
            for n,s in targets.items():
                mem=membership.get(n.removeprefix('P0_')) if n.startswith('P0_') else None
                # Hip is X-axis rotation. Fixed and same-Hip shapes cannot
                # enter this local X slab; child joints are NOT discarded.
                if not (mem and mem[0]==code and mem[1]!='Hip'):
                    raw=s.BoundBox
                    if raw.XMax<mx-42 or raw.XMin>mx+42:continue
                key=(n,() if mem[1]=='Hip' else (knee,) if mem[1]=='Knee' else (knee,ankle)) if mem and mem[0]==code else (n,hip)
                if key in material_seen:continue
                material_seen.add(key)
                tr=inv*(trans[mem[1]] if mem and mem[0]==code else A.Placement())
                q=s.copy();q.Placement=tr*q.Placement;b=q.BoundBox
                ys=sorted((side*b.YMin,side*b.YMax))
                if b.XMax<mx-40 or b.XMin>mx+40 or ys[1]<75 or ys[0]>136 or b.ZMax<12 or b.ZMin>55:continue
                material.append((n,q,b))
                if n not in meshes:meshes[n]=s.tessellate(mesh_deflection)
                vertices,triangles=meshes[n]
                vv=[tr.multVec(p) for p in vertices]
                for indexes in triangles:
                    tri=tuple((vv[i].x,side*vv[i].y,vv[i].z) for i in indexes)
                    low=[min(p[i] for p in tri)-surface_half[i] for i in range(3)]
                    high=[max(p[i] for p in tri)+surface_half[i] for i in range(3)]
                    lo=[max(a,b) for a,b in zip(low,(mx-40,75,12))]
                    hi=[min(a,b) for a,b in zip(high,(mx+40,136,55))]
                    if any(a>b for a,b in zip(lo,hi)):continue
                    for bucket in itertools.product(*(range(math.floor(a/cell),math.floor(b/cell)+1) for a,b in zip(lo,hi))):
                        surface_grid.setdefault(bucket,[]).append((tri,n))
        print('moving plan',leg,'material surfaces',len(surface_grid),'buckets',len(material),'sampled placements',flush=True)
        blocked={};cache={}
        def clear(p):
            key=tuple(p)
            if key in cache:return cache[key]
            bucket=tuple(math.floor(x/cell) for x in p)
            for d in itertools.product((-1,0,1),repeat=3):
                for v,rad,n in grid.get(tuple(a+b for a,b in zip(bucket,d)),()):
                    gap=sum(max(0,abs(a-b)-h)**2 for a,b,h in zip(p,v,half))
                    if gap<(rad+margin+.5)**2:
                        cache[key]=False;blocked[key]=n;return False
            for tri,n in surface_grid.get(bucket,()):
                if triangle_box(tri,p,surface_half):
                    cache[key]=False;blocked[key]='mesh surface reservation/'+n;return False
            cache[key]=True;return True
        sign=-1 if front else 1
        start=[mx+sign*20.5,82,38.];goal=[mx+sign*7,108,crown_top-2]
        aa=[sorted(set([mx+v for v in range(-36,37,3)]+[start[0],goal[0]])),
            sorted(set(list(range(78,133,3))+[82,108])),
            sorted(set(list(range(16,48,3))+[start[2],goal[2]]))]
        first=tuple(a.index(v) for a,v in zip(aa,start));last=tuple(a.index(v) for a,v in zip(aa,goal))
        def pt(k):return [a[i] for a,i in zip(aa,k)]
        def heur(k):return sum(abs(a-b) for a,b in zip(pt(k),goal))
        queue=[(heur(first),0,first)];best={first:0};parent={};found=None;count=0
        sc,gc=clear(start),clear(goal)
        # A free surface box can be wholly inside a large solid. Reject that
        # at the two endpoints; never call expensive interiors per A* node.
        for endpoint in (start,goal):
            world=A.Vector(endpoint[0],side*endpoint[1],endpoint[2])
            for n,s,b in material:
                if b.isInside(world) and s.isInside(world,1e-6,False):
                    blocked[tuple(endpoint)]='material interior/'+n
                    if endpoint==start:sc=False
                    else:gc=False
                    break
        search_start=time.monotonic()
        while queue and sc and gc and count<10000:
            if time.monotonic()-search_start>90:break
            _,cost,k=heapq.heappop(queue)
            if cost!=best[k]:continue
            count+=1
            if k==last:found=k;break
            for i in range(3):
                for step in (-1,1):
                    kk=list(k);kk[i]+=step
                    if not 0<=kk[i]<len(aa[i]):continue
                    kk=tuple(kk);a,b=pt(k),pt(kk)
                    if not clear(b) or not clear([(x+y)/2 for x,y in zip(a,b)]):continue
                    nc=cost+math.dist(a,b)
                    if nc>=best.get(kk,1e20):continue
                    best[kk]=nc;parent[kk]=k;heapq.heappush(queue,(nc+heur(kk),nc,kk))
            if count%100==0:print('moving search',leg,count,'states',round(time.monotonic()-search_start,2),'s',flush=True)
        path=[]
        if found:
            k=found;path=[pt(k)]
            while k!=first:k=parent[k];path.append(pt(k))
            path.reverse();simple=[path[0]]
            for a,b,c in zip(path,path[1:],path[2:]):
                if next(i for i in range(3) if a[i]!=b[i])!=next(i for i in range(3) if b[i]!=c[i]):simple.append(b)
            simple.append(path[-1]);path=[[p[0],side*p[1],p[2]] for p in simple]
        roots.append(dict(leg=leg,points_mm=path,start_clear=sc,goal_clear=gc,start_blocker=blocked.get(tuple(start)),goal_blocker=blocked.get(tuple(goal)),expansions=count))
        print('moving support corridor',leg,len(path),'knots',count,'states',flush=True)
        (P.OUT/'moving-cuff-corridors-progress.json').write_text(json.dumps(dict(status='PARTIAL_PLANNING_ONLY',roots=roots,worker_seconds=round(time.monotonic()-tick,3)),indent=2)+'\n',encoding='utf-8')
    report=dict(status='MOVING_CORRIDORS_SCREEN_CLEAR_MATERIAL_GATE_OPEN' if all(r['points_mm'] for r in roots) else 'REJECTED_MOVING_CORRIDOR_PLAN',
        roots=roots,beam_dimensions_mm=[3,4,4],wire_margin_mm=margin,crown_top_mm=crown_top,
        fixed_wire_Hip_samples=31,coupled_material_samples=27,selected=False,physical_pass=False,
        limitations=['Point cloud and mesh surface reservations with0.3mm mesh deflection plus0.5mm margin; actual BRep gate required','All52head solids and new supports still require exact affected gate','No continuous sweep, strength or W5 qualification'],
        worker_seconds=round(time.monotonic()-tick,3),source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (archive,fp,af,zf,Path(__file__),Path(__file__).with_name('cad_reservation_math.py'))})
    (P.OUT/'moving-cuff-corridors-plan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)


if __name__=='__main__':run()
