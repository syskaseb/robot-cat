"""Choose36 static core fans in one shared current planning scene.

All receiver lands and source packing are allocated before candidate selection.
The cheap surface/wire screen rejects candidates; it cannot accept actual CAD.
"""
import hashlib
import heapq
import itertools
import json
import math
import subprocess
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
        self.blockers={};self.last_blocker=None;self.material_cache={};self.exact_curve_points=set()

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
                if (name,tuple(np.round(p,7))) in self.exact_curve_points:continue
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
        if distances.min()<2.55:return False
    return True


AXES=((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))


def part_points(part):
    if part['kind']=='bezier':return bezier_points(part['poles_mm'],max(40,math.ceil(part['length_mm']/.65)))
    return np.asarray([p for _,p in samples([part],step=.75)])


def reverse_part(part):
    result=dict(part,start=part['end'],end=part['start'])
    if part['kind']=='bezier':result['poles_mm']=list(reversed(part['poles_mm']))
    return result


def corridor(scene,row,backward=False):
    """One bounded tangent/curvature grid, then a checked final spatial span."""
    assert tuple(row['bodyward_bundle_tangent'])==AXES[4],'Changed root direction needs a new shared contract'
    receiving=row.get('receiving_parts',[row['receiving_land']])
    if backward:
        start=np.asarray(row['free_end']);end=np.asarray(row['free_start'])
        initial=[reverse_part(p) for p in reversed(receiving)]
        final_parts=[reverse_part(row['source_land'])]
        first_axis=AXES.index(tuple(row['receiver_outward_axis']))
        end_axis=row['bodyward_bundle_tangent']
    else:
        start=np.asarray(row['free_start']);end=np.asarray(row['free_end'])
        initial=[row['source_land']];final_parts=receiving
        first_axis=4;end_axis=row['receiver_outward_axis']
    fixed=row['source_land']['length_mm']+sum(p['length_mm'] for p in receiving)
    capacity=row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']-fixed
    first=(0,0,0,first_axis);queue=[(float(np.linalg.norm(end-start)),0,0,first)]
    best={first:0};parents={};serial=itertools.count(1);tick=time.monotonic();states=0
    while queue and states<1000 and time.monotonic()-tick<120:
        _,cost,_,state=heapq.heappop(queue)
        if cost!=best.get(state):continue
        states+=1;p=(start+10*np.asarray(state[:3])).tolist();u=AXES[state[3]]
        distance=math.dist(p,end)
        if cost>0 and distance+cost<capacity:
            handles=[max(12,min(65,distance/3)),18,38]
            for h,b in ((handles[0],handles[0]),(18,38),(38,18),(38,38)):
                poles=[p,add(p,mul(u,h)),add(end.tolist(),mul(end_axis,b)),end.tolist()]
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
                whole=[*initial,*middle,*final_parts]
                if backward:whole=[reverse_part(p) for p in reversed(whole)]
                points=np.concatenate([part_points(part) for part in whole])
                assert all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(whole,whole[1:]))
                along=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
                remote=np.abs(along[:,None]-along[None,:])>4
                distance=np.sum((points[:,None,:]-points[None,:,:])**2,axis=2)
                if np.any(distance[remote]<2.1**2):continue
                if not scene.clear(points,row):continue
                guide=sum(q['length_mm'] for q in whole)
                return dict(parts=whole,guide_mm=guide,spare_before_trim_mm=capacity+fixed-guide,
                            minimum_sampled_R_mm=min(10,radius),search_direction='receiver_to_source' if backward else 'source_to_receiver',
                            search_states=states,search_seconds=round(time.monotonic()-tick,3)),points
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


def receiving_profiles(row,direction):
    axis=row['receiver_outward_axis'];end=row['receiver_point_mm']
    entry=line(end,row['free_end']);q=exact_quarter(entry['end'],axis,direction,10)
    yield [entry,q],0,'land_before_turn'
    # The9mm grip requirement does not force the bend to start9mm from the
    # contact. Keep a project3mm external entry, turnR10, then a full9mm land.
    entry=line(end,add(end,mul(axis,3)));q=exact_quarter(entry['end'],axis,direction,10)
    land=line(q['end'],add(q['end'],mul(direction,9)))
    yield [entry,q,land],2,'land_after_turn'


def corridor_exits(scene,row,start,axis):
    """A clear endpoint alone is insufficient: qualify its next R10 move."""
    clear=[];blocked=[]
    for direction in AXES:
        if direction==tuple(axis):recipe=line(start,add(start,mul(axis,10)))
        elif sum(a*b for a,b in zip(axis,direction))==0:recipe=exact_quarter(start,axis,direction,10)
        else:continue
        if scene.clear(part_points(recipe),row):clear.append((recipe,direction))
        else:blocked.append(dict(direction=list(direction),blocker=scene.last_blocker))
    return clear,blocked


def receiving_turns(scene,rows,routes,pins):
    options={};rejected=[];blocked=[];selected={};nodes=0;until=time.monotonic()+30
    evidence=OUT/'body-fanout-receiver-witnesses.json'
    proof=json.loads(evidence.read_text());generator='tools/cad/diagnose_body_fanout_receivers.py'
    historical=subprocess.check_output(['git','show','5b08e89:'+generator],cwd=ROOT)
    assert hashlib.sha256(historical).hexdigest()==proof['source_sha256'][generator]
    for n,h in proof['source_sha256'].items():
        if n!=generator:assert SHA(ROOT/n)==h,n
    pins[evidence.relative_to(ROOT).as_posix()]=SHA(evidence)
    # Replace ONLY conservative sample hits on the already qualified quarter,
    # not clearance elsewhere on this conductor or against any other object.
    for witness in proof['rows']:
        if witness['kind']!='wire' or witness['violates_project_clearance']:continue
        row=next(r for r in rows if r['wire']==witness['wire'])
        quarter=exact_quarter(row['free_end'],row['receiver_outward_axis'],witness['direction'],10)
        scene.exact_curve_points.update((witness['target'],tuple(np.round(p,7))) for p in part_points(quarter))
    for row in rows:
        if row['wire'] in routes:continue
        own=[];side=1 if row['receiver_point_mm'][1]>0 else -1
        directions=sorted(AXES,key=lambda v:(-side*v[1],abs(v[2])))
        for v in directions:
            axis=row['receiver_outward_axis']
            if sum(a*b for a,b in zip(axis,v))!=0:continue
            for parts,grip,kind in receiving_profiles(row,v):
                points=np.concatenate([part_points(p) for p in parts])
                if not scene.clear(points,row):
                    blocked.append(dict(wire=row['wire'],direction=list(v),profile=kind,blocker=scene.last_blocker))
                    continue
                exits,exit_blockers=corridor_exits(scene,row,parts[-1]['end'],v)
                if not exits:
                    blocked.append(dict(wire=row['wire'],direction=list(v),profile=kind,
                        error='CLEAR_APPROACH_WITH_NO_CURVATURE_CORRIDOR_EXIT',exit_blockers=exit_blockers))
                    continue
                reverse=[dict(p,start=p['end'],end=p['start']) for p in reversed(parts)]
                own.append(dict(free_end=parts[-1]['end'],receiver_outward_axis=list(v),
                    receiving_parts=reverse,receiving_grip_part_index=len(parts)-grip-1,
                    receiver_profile=kind,entry_straight_project_mm=parts[0]['length_mm'],
                    clear_next_moves=len(exits),
                    source_connection_lower_bound_mm=min(math.dist(p['end'],row['free_start'])+p['length_mm'] for p,d in exits),samples=points))
        own.sort(key=lambda c:(c['source_connection_lower_bound_mm'],-c['clear_next_moves']))
        options[row['wire']]=own
        if not own:rejected.append(dict(wire=row['wire'],error='NO_R10_RECEIVER_TURN_IN_RESERVATIONS_REQUIRES_EXACT_DIAGNOSIS'))
    def choose(pending):
        nonlocal nodes
        nodes+=1
        if nodes>30000 or time.monotonic()>until:return False
        if not pending:return True
        name=min(pending,key=lambda n:len(options[n]))
        for candidate in options[name]:
            if not all(compatible(candidate,old) for old in selected.values()):continue
            selected[name]=candidate
            if choose([n for n in pending if n!=name]):return True
            selected.pop(name)
        return False
    until=time.monotonic()+30
    if not rejected and not choose(list(options)):rejected.append(dict(error='BOUNDED_SHARED_RECEIVER_TURN_ALLOCATION_UNRESOLVED',nodes=nodes))
    result=dict(status='RECEIVER_TURNS_NEED_ACTUAL_DIAGNOSIS' if rejected else 'SHARED_RECEIVER_R10_TURNS_PLANNED_NO_MATERIAL_ACCEPTANCE',
        options={n:[{k:v for k,v in c.items() if k!='samples'} for c in values] for n,values in options.items()},
        chosen={n:{k:v for k,v in c.items() if k!='samples'} for n,c in selected.items()},
        rejected=rejected,blocked=blocked,reused_existing_final_approaches=list(routes),
        source_sha256=pins,selected=False,W5_complete=False,physical_pass=False)
    f=OUT/'body-fanout-receiving-turns.json';f.write_text(json.dumps(result,indent=2)+'\n')
    if rejected:return None,result
    changed=[]
    for row in rows:
        if row['wire'] in selected:
            c=selected[row['wire']];scene.add_points('new/'+row['wire']+'/receiver',c['samples'])
            row=dict(row,**{k:v for k,v in c.items() if k!='samples'})
        changed.append(row)
    return changed,result


def corridor_layout(scene,rows,files,tick):
    routes={};rejected=[];dest=OUT/'body-fanout-layout.json'
    pins={p.relative_to(ROOT).as_posix():SHA(p) for p in files}
    inherited=[];origin=None
    if dest.exists():
        prior=json.loads(dest.read_text())
        if prior.get('route_family')=='tangent_grid_R10_plus_spatial_completion':
            for p in files[:-1]:assert prior['source_sha256'][p.relative_to(ROOT).as_posix()]==SHA(p),'Changed route geometry input'
            routes=prior['routes'];origin=SHA(dest);inherited=list(routes)
            for name,r in routes.items():
                row=next(row for row in rows if row['wire']==name)
                assert math.dist(r['parts'][0]['start'],row['start'])<1e-8
                assert math.dist(r['parts'][-1]['end'],row['receiver_point_mm'])<1e-8
                assert abs(sum(p['length_mm'] for p in r['parts'])-r['guide_mm'])<1e-6
    for row in rows:
        scene.add_points('new/'+row['wire']+'/source',np.linspace(row['start'],row['free_start'],9))
        # Only the mandatory entry is reserved before choosing the land's
        # side of the bend. Do not protect an unselected old9mm tail.
        entry=add(row['receiver_point_mm'],mul(row['receiver_outward_axis'],3))
        scene.add_points('new/'+row['wire']+'/receiver',np.linspace(entry,row['receiver_point_mm'],6))
    for name,r in routes.items():scene.add_points('new/'+name,np.concatenate([part_points(p) for p in r['parts']]))
    updated,goals=receiving_turns(scene,rows,routes,pins)
    if updated is None:
        print(json.dumps(dict(status=goals['status'],rejected=goals['rejected'],existing_routes=len(routes))),flush=True)
        return
    rows=updated
    pins[(OUT/'body-fanout-receiving-turns.json').relative_to(ROOT).as_posix()]=SHA(OUT/'body-fanout-receiving-turns.json')
    order=sorted(rows,key=lambda r:(r['capacity_before_terminal_mm']-r['terminal_allowance_project_mm']-math.dist(r['free_start'],r['free_end']),r['wire']))
    def save(status):
        result=dict(status=status,route_family='tangent_grid_R10_plus_spatial_completion',routes=routes,rows=rows,
            inherited_routes=inherited,inherited_candidate_sha256=origin,
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
        if row['wire'] in routes:continue
        result,points=corridor(scene,row,backward=True)
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
