"""Cheap whole-group proximity screen BEFORE expensive pipe Boolean gates.

Samples exact circular arcs at <=1mm spacing. Close sampled centrelines
reject a planning allocation, not prove a physical supplier collision. A
separated sampled pair has a conservative2mm endpoint-sampling allowance;
retained material, native grips and service still require actual BRep checks.
"""
from datetime import datetime, timezone
import json, math, sys, time
import open_prototype_source_group as G

def samples(parts,step=1):
    for segment,p in enumerate(parts):
        length,t0,_,r=G.segment_geometry(p)
        count=max(1,math.ceil(length/step))
        if r is None:
            d=G.sub(p['end'],p['start'])
            for i in range(count+1):yield segment,G.add(p['start'],G.mul(d,i/count))
        else:
            a,m,b=p['start'],p['mid'],p['end'];u=G.sub(m,a);v=G.sub(b,a);n=G.cross(u,v)
            c=G.add(a,G.mul(G.add(G.mul(G.cross(v,n),G.dot(u,u)),G.mul(G.cross(n,u),G.dot(v,v))),1/(2*G.dot(n,n))))
            radial=G.sub(a,c);angle=length/r
            for i in range(count+1):
                t=angle*i/count
                yield segment,G.add(c,G.add(G.mul(radial,math.cos(t)),G.mul(t0,r*math.sin(t))))

def screen(plan):
    tick=time.monotonic();rows=[]
    for r in plan['tails']+plan['s1_routes']:rows.append((r['wire'],r['OD_mm'],r['segments']))
    for h in plan['holders']:
        for side in ('input','output'):rows.append((h['role']+'/'+side,4,h[side+'_segments']))
    grid={};close={};points=0;cell=7
    for name,od,parts in rows:
        local=[]
        for segment,p in samples(parts):
            key=tuple(math.floor(v/cell) for v in p);points+=1
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    for dz in (-1,0,1):
                        for other,q,other_od,other_segment in grid.get((key[0]+dx,key[1]+dy,key[2]+dz),[]):
                            distance=math.dist(p,q);required=(od+other_od)/2
                            if distance>required+2:continue
                            pair=(other,name);old=close.get(pair)
                            if old is None or distance<old['sampled_distance_mm']:
                                close[pair]=dict(a=other,b=name,sampled_distance_mm=distance,
                                    centreline_minimum_mm=required,sampling_allowance_mm=2,
                                    sample_a_mm=q,sample_b_mm=p,segment_a=other_segment,segment_b=segment,
                                    status='REJECT_PLANNING_PROXIMITY' if distance<required else 'REQUIRES_EXACT_DISTANCE_CHECK')
            local.append((key,(name,p,od,segment)))
        # No insertion until the whole path has been screened: ordinary
        # consecutive points on its own insulation are not other wires.
        for key,record in local:grid.setdefault(key,[]).append(record)
    return dict(status='MUTUAL_ROUTE_ALLOCATION_REQUIRES_CHANGE' if any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in close.values())
            else 'PROXIMITY_SCREEN_ONLY_RETAINED_MATERIAL_OPEN',
        paths=len(rows),samples=points,step_max_mm=1,near_pairs=list(close.values()),
        no_BRep_or_native_acceptance=True,selected=False,stage_completed=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())

if __name__=='__main__':
    plan=G.read(G.PLAN);result=screen(plan)
    dest=G.OUT/'source-group-proximity.json';assert not dest.exists(),'No unchanged repeat'
    result['source_sha256']={G.PLAN.relative_to(G.ROOT).as_posix():G.sha(G.PLAN)}
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],paths=result['paths'],samples=result['samples'],
        near_pairs=[{k:r[k] for k in ('a','b','sampled_distance_mm','status')} for r in result['near_pairs']],seconds=result['worker_seconds'])),flush=True)
