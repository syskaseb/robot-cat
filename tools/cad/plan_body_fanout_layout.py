"""Choose36 static core fans in one shared current planning scene.

All receiver lands and source packing are allocated before candidate selection.
The cheap surface/wire screen rejects candidates; it cannot accept actual CAD.
"""
import hashlib
import heapq
import itertools
import json
import math
import time
from pathlib import Path
import numpy as np
from fast_carrier_reservations import TriangleBucket
from plan_current_moving_looms import add,mul,metrics,exact_quarter
from plan_current_mta_interfaces import line
from open_prototype_path_preflight import samples

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def bezier_points(poles,count):
    t=np.linspace(0,1,count+1)[:,None];s=1-t
    a,b,c,d=np.asarray(poles)
    return s**3*a+3*s*s*t*b+3*s*t*t*c+t**3*d


class Scene:
    def __init__(self,data):
        # NpzFile reads/decompresses on EACH item access. Load once, then index
        # all9million triangles with vectorized sorting, not Python triangle
        # objects or repeated archive decompression in every point query.
        self.data={k:data[k] for k in data.files} if hasattr(data,'files') else data
        data=self.data;self.cell=10;self.wires={}
        triangles=data['triangles']
        self.trilow=triangles.min(axis=1);self.trihigh=triangles.max(axis=1)
        extent=np.max(self.trihigh-self.trilow,axis=1)
        self.levels=[];lower=-1
        # Separate long flat triangles instead of scanning every long triangle
        # at every route point. Each level has extent+1.25 < its cell size;
        # all27 neighbouring centroid cells therefore contain every possible hit.
        for cell,upper in ((10,8),(30,28),(100,98)):
            ids=np.flatnonzero((extent>lower)&(extent<=upper));lower=upper
            if not len(ids):continue
            centers=np.floor(triangles[ids].mean(axis=1)/cell).astype(np.int32)
            origin=centers.min(axis=0);dim=centers.max(axis=0)-origin+1;v=centers-origin
            keys=(v[:,0].astype(np.int64)*dim[1]+v[:,1])*dim[2]+v[:,2]
            order=np.argsort(keys);keys=keys[order];ids=ids[order]
            unique,starts=np.unique(keys,return_index=True);stops=np.r_[starts[1:],len(keys)]
            buckets={int(k):(int(a),int(b)) for k,a,b in zip(unique,starts,stops)}
            self.levels.append((cell,origin,dim,ids,buckets))
        self.wide=np.flatnonzero(extent>98)
        for i,p in enumerate(data['wire_points']):self.wires.setdefault(tuple(np.floor(p/self.cell).astype(int)),[]).append(i)
        self.wires={k:np.asarray(v) for k,v in self.wires.items()}
        self.blockers={};self.last_blocker=None;self.material_cache={}

    def add_points(self,name,points,radius=1):
        data=self.data;offset=len(data['wire_points']);identity=len(data['wire_names'])
        data['wire_points']=np.concatenate((data['wire_points'],np.asarray(points)))
        data['wire_radii']=np.r_[data['wire_radii'],np.full(len(points),radius)]
        data['wire_ids']=np.r_[data['wire_ids'],np.full(len(points),identity,dtype=int)]
        data['wire_names']=np.concatenate((data['wire_names'],np.asarray([name])))
        for index,p in enumerate(points,offset):
            key=tuple(np.floor(p/self.cell).astype(int))
            self.wires[key]=np.r_[self.wires.get(key,np.array([],dtype=int)),index]

    def material_hit(self,p):
        memo=tuple(np.round(p,7))
        if memo in self.material_cache:return self.material_cache[memo]
        parts=[self.wide]
        for size,origin,dim,ids,buckets in self.levels:
            center=np.floor(p/size).astype(int)
            for delta in itertools.product((-1,0,1),repeat=3):
                v=center+delta-origin
                if np.any(v<0) or np.any(v>=dim):continue
                key=int((v[0]*dim[1]+v[1])*dim[2]+v[2])
                if key in buckets:
                    a,b=buckets[key];parts.append(ids[a:b])
        ix=np.concatenate(parts)
        if len(ix):
            close=np.all(self.trilow[ix]<=p+1.25+1e-10,axis=1)&np.all(self.trihigh[ix]>=p-1.25-1e-10,axis=1)
            ix=ix[close]
        hit=None
        if len(ix):
            bucket=TriangleBucket([(self.data['triangles'][i],int(self.data['triangle_ids'][i])) for i in ix])
            hit=bucket.hit(p,(1.25,1.25,1.25))
        self.material_cache[memo]=hit
        return hit

    def clear(self,points,row):
        root=np.asarray(row['bundle_root_world_mm']);end=np.asarray(row['receiver_point_mm'])
        for p in points:
            if np.any(p<self.data['low']) or np.any(p>self.data['high']):return False
            key=tuple(np.floor(p/self.cell).astype(int))
            # Contact at the project terminal mouth belongs to the insertion
            # interface. The rest of the route receives the ordinary screen.
            at_mouth=np.linalg.norm(p-end)<1.1
            if not at_mouth:
                hit=self.material_hit(p)
                if hit is not None:
                    name=str(self.data['material_names'][hit]);self.blockers[name]=self.blockers.get(name,0)+1
                    self.last_blocker=dict(kind='surface_reservation',name=name,point_mm=p.tolist())
                    return False
            indexes=[self.wires[k] for shift in itertools.product((-1,0,1),repeat=3)
                     if (k:=tuple(a+b for a,b in zip(key,shift))) in self.wires]
            if not indexes:continue
            ix=np.concatenate(indexes);q=self.data['wire_points'][ix]
            close=np.linalg.norm(q-p,axis=1)<self.data['wire_radii'][ix]+1.55
            if not close.any():continue
            for i in ix[close]:
                name=str(self.data['wire_names'][self.data['wire_ids'][i]])
                if name in ('new/'+row['wire']+'/source','new/'+row['wire']+'/receiver'):continue
                if name.startswith('leg/'+row['loom']+'/') and np.linalg.norm(p-root)<6:continue
                self.blockers['wire/'+name]=self.blockers.get('wire/'+name,0)+1
                self.last_blocker=dict(kind='sampled_wire_reservation',name=name,point_mm=p.tolist())
                return False
        return True


def prepared_rows(contract):
    rows=[]
    # Packing is provisional continuity labeling, not supplier cavity order.
    for r in contract['rows']:
        side=1 if r['bundle_root_world_mm'][1]>0 else -1
        angle=math.radians({'D':0,'V':120,'G':240}[r['core']]+side*30)
        start=add(r['bundle_root_world_mm'],[1.5*math.cos(angle),1.5*math.sin(angle),0])
        a=add(start,mul(r['bodyward_bundle_tangent'],5))
        end=r['receiver_point_mm'];b=add(end,mul(r['receiver_outward_axis'],9))
        rows.append(dict(r,start=start,free_start=a,free_end=b,
                         source_land=line(start,a),receiving_land=line(b,end)))
    return rows


def compatible(a,b):
    # Nominal proximity rejection only. Passing sampled curves still requires
    # exact distances; this is not a continuous clearance certificate.
    aa=a['samples'];bb=b['samples'];low=aa.min(axis=0)-3.5;high=aa.max(axis=0)+3.5
    if np.any(bb.max(axis=0)<low) or np.any(bb.min(axis=0)>high):return True
    for p in aa:
        distances=np.linalg.norm(bb-p,axis=1)
        if distances.min()<2.1:return False
    return True


AXES=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))


def part_points(part):
    if part['kind']=='bezier':return bezier_points(part['poles_mm'],max(40,math.ceil(part['length_mm']/.65)))
    return np.asarray([p for _,p in samples([part],step=.75)])


def corridor(scene,row):
    """One bounded tangent/curvature grid, then a checked final spatial span."""
    assert tuple(row['bodyward_bundle_tangent'])==AXES[4],'Changed root direction needs a new shared contract'
    start=np.asarray(row['free_start']);end=np.asarray(row['free_end'])
    capacity=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-14
    first=(0,0,0,4);queue=[(float(np.linalg.norm(end-start)),0,0,first)]
    best={first:0};parents={};serial=itertools.count(1);tick=time.monotonic();states=0
    while queue and states<1000 and time.monotonic()-tick<120:
        _,cost,_,state=heapq.heappop(queue)
        if cost!=best.get(state):continue
        states+=1;p=(start+10*np.asarray(state[:3])).tolist();u=AXES[state[3]]
        distance=math.dist(p,end)
        if cost>0 and distance+cost<capacity:
            handles=[max(12,min(65,distance/3)),18,38]
            for h,b in ((handles[0],handles[0]),(18,38),(38,18),(38,38)):
                poles=[p,add(p,mul(u,h)),add(end.tolist(),mul(row['receiver_outward_axis'],b)),end.tolist()]
                length,radius,_=metrics(poles,24)
                if radius<10.5 or length+cost>capacity:continue
                final=dict(kind='bezier',start=p,end=end.tolist(),poles_mm=poles,length_mm=length)
                pts=part_points(final)
                if not scene.clear(pts,row):continue
                length,radius,_=metrics(poles,400)
                if radius<10 or length+cost>capacity:continue
                final['length_mm']=length
                middle=[final];key=state
                while key!=first:
                    key,part=parents[key];middle.append(part)
                middle=list(reversed(middle[1:]))+[final]
                whole=[row['source_land'],*middle,row['receiving_land']]
                points=np.concatenate([part_points(part) for part in whole])
                assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(whole,whole[1:]))
                along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
                remote=np.abs(along[:,None]-along[None,:])>4
                distance=np.sum((points[:,None,:]-points[None,:,:])**2,axis=2)
                if np.any(distance[remote]<2.1**2):continue
                if not scene.clear(points,row):continue
                guide=sum(q['length_mm'] for q in whole)
                return dict(parts=whole,guide_mm=guide,spare_before_trim_mm=capacity+14-guide,
                            minimum_sampled_R_mm=min(10,radius),search_states=states,search_seconds=round(time.monotonic()-tick,3)),points
        for index,v in enumerate(AXES):
            if index==state[3]:part=line(p,add(p,mul(u,10)))
            elif sum(a*b for a,b in zip(u,v))==0:part=exact_quarter(p,u,v,10)
            else:continue
            nxt=tuple(round((part['end'][j]-start[j])/10) for j in range(3))+(index,)
            new_cost=cost+part['length_mm'];distance=math.dist(part['end'],end)
            if new_cost+distance>capacity or new_cost>=best.get(nxt,float('inf')):continue
            if not scene.clear(part_points(part),row):continue
            best[nxt]=new_cost;parents[nxt]=(state,part)
            heapq.heappush(queue,(new_cost+distance,new_cost,next(serial),nxt))
    return dict(error='BOUNDED_CURVATURE_CORRIDOR_EXHAUSTED_NOT_GEOMETRIC_IMPOSSIBILITY',
                search_states=states,search_seconds=round(time.monotonic()-tick,3)),None


def corridor_layout(scene,rows,files,tick):
    routes={};rejected=[];dest=OUT/'body-fanout-layout.json'
    pins={p.relative_to(ROOT).as_posix():SHA(p) for p in files}
    for row in rows:
        scene.add_points('new/'+row['wire']+'/source',np.linspace(row['start'],row['free_start'],9))
        scene.add_points('new/'+row['wire']+'/receiver',np.linspace(row['free_end'],row['receiver_point_mm'],15))
    order=sorted(rows,key=lambda r:(r['capacity_before_terminal_mm']-r['terminal_allowance_project_mm']-math.dist(r['free_start'],r['free_end']),r['wire']))
    def save(status):
        result=dict(status=status,route_family='tangent_grid_R10_plus_spatial_completion',routes=routes,rows=rows,
            rejected=rejected,blocker_counts=scene.blockers,all_new_supports_in_scene=12,
            individual_project_OD_mm=2,project_static_R_mm=10,radial_packing_mm=1.5,
            source_free_straight_mm=5,receiving_land_mm=9,
            individual_core_order_requires_continuity_mapping=True,
            remaining=['Actual BRep qualification; independent receiver/midspan grips and mounts',
                       'All19other guides, assembly, actual cut/stock and one whole selection'],
            selected=False,W5_complete=False,physical_pass=False,source_sha256=pins,
            worker_seconds=round(time.monotonic()-tick,3))
        temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(result,indent=2)+'\n');temp.replace(dest)
        return result
    for row in order:
        result,points=corridor(scene,row)
        if points is None:
            rejected.append(dict(wire=row['wire'],**result));save('PARTIAL_SHARED36CORE_CORRIDORS_CURRENT_END_DIAGNOSIS_OPEN')
            print(json.dumps(dict(stopped_at=row['wire'],found=len(routes),**result)),flush=True)
            return
        routes[row['wire']]=result;scene.add_points('new/'+row['wire'],points)
        save('PARTIAL_SHARED36CORE_CORRIDORS_NO_MATERIAL_ACCEPTANCE')
        print('shared corridor',row['wire'],round(result['guide_mm'],2),result['search_states'],flush=True)
    result=save('SHARED36CORE_PLANNING_SCREEN_ONLY_ACTUAL_MATERIAL_OPEN')
    print(json.dumps(dict(status=result['status'],routes=len(routes),worker_seconds=result['worker_seconds'])),flush=True)


def run():
    tick=time.monotonic();cf=OUT/'body-fanout-work-contract.json';sf=OUT/'body-fanout-scene.json'
    contract=json.loads(cf.read_text());receipt=json.loads(sf.read_text())
    for source in (contract,receipt):
        for n,h in source['source_sha256'].items():assert SHA(ROOT/n)==h,n
    scene_file=ROOT/receipt['scene'];assert SHA(scene_file)==receipt['sha256']
    scene=Scene(np.load(scene_file,allow_pickle=False))
    rows=prepared_rows(contract);rejected=[]
    for row in rows:
        for side,points in (
            ('source',np.linspace(row['start'],row['free_start'],9)),
            ('receiver',np.linspace(row['free_end'],row['receiver_point_mm'],15))):
            if not scene.clear(points,row):
                rejected.append(dict(wire=row['wire'],side=side,blocker=scene.last_blocker))
    if rejected:
        result=dict(status='CURRENT_FANOUT_ENDPOINTS_REQUIRE_ACTUAL_DIAGNOSIS_BEFORE_ROUTING',
            rows=rows,rejected=rejected,routes={},selected=False,W5_complete=False,physical_pass=False,
            decision='Surface/sampling reservations are not actual collisions. Diagnose these exact endpoint/material pairs before choosing directions; changing middle-curve handles cannot free a blocked straight land.',
            source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (cf,sf,scene_file,Path(__file__))},
            worker_seconds=round(time.monotonic()-tick,3))
        (OUT/'body-fanout-layout.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(status=result['status'],blocked_ends=len(rejected),worker_seconds=result['worker_seconds'])),flush=True)
        return
    return corridor_layout(scene,rows,(cf,sf,scene_file,Path(__file__)),tick)

if __name__=='__main__':run()
