"""Allocate complete Hip1 planes against the OTHER eight full swept leads.

This is a conservative 1mm point-cloud planning allocation, not material QA.
It allocates a shared receiving corridor before generating another geometry.
"""
import itertools,json,math,time
from plan_current_main_sources import ROOT,OUT,SHA
from plan_continuous_joint_family import parts_for_loom
from plan_current_rigid_factory_joins import moved_parts
from route_current_leg_fanouts import sampling_parts
from open_prototype_path_preflight import samples


def merge(intervals):
    result=[]
    for lo,hi in sorted(intervals):
        if result and lo<=result[-1][1]:result[-1][1]=max(result[-1][1],hi)
        else:result.append([lo,hi])
    return result


def run():
    tick=time.monotonic();fp=OUT/'leg-source-underbody-plan.json'
    family=json.loads(fp.read_text());af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes'];routes={r['loom']:r for r in family['routes']}
    grid={};cell=8.;margin=8.;cloud=[]
    for row in family['hips']:
        if row['loom'].endswith('1'):continue
        route=routes[row['loom']]
        for hip,knee in itertools.product((-15,0,15),repeat=2):
            parts=parts_for_loom(family,row['loom'],hip,knee,axes)+moved_parts(route['source_parts'],route['source'],hip,knee,axes)
            cloud.extend((row['loom'],p) for _,p in samples(sampling_parts(parts),step=1))
    for name,p in cloud:grid.setdefault((math.floor(p[1]/cell),math.floor(p[2]/cell)),[]).append((name,p))
    results=[]
    for row in family['hips']:
        if not row['loom'].endswith('1'):continue
        forbidden=[];owners=set()
        for pose in row['poses']:
            for _,p in samples(sampling_parts(pose['parts']),step=1):
                key=(math.floor(p[1]/cell),math.floor(p[2]/cell))
                for dy,dz in itertools.product((-1,0,1),repeat=2):
                    for name,q in grid.get((key[0]+dy,key[1]+dz),[]):
                        yz=(p[1]-q[1])**2+(p[2]-q[2])**2
                        if yz>=margin**2:continue
                        dx=math.sqrt(margin**2-yz);forbidden.append((q[0]-dx,q[0]+dx));owners.add(name)
        intervals=merge(forbidden);free=[];cursor=-64.
        for lo,hi in intervals:
            if hi<cursor:continue
            if lo>106:break
            if lo>cursor:free.append([cursor,min(lo,106.)])
            cursor=max(cursor,hi)
        if cursor<106:free.append([cursor,106.])
        results.append(dict(loom=row['loom'],physical_leg=row['physical_leg'],free_x_intervals_mm=free,
            forbidden_x_intervals_mm=intervals,obstructing_looms=sorted(owners),old_plane_x_mm=row['fixed_anchor_world_mm'][0]))
    report=dict(status='CONSERVATIVE_SHARED_RECEIVING_PLANE_ALLOCATION_ONLY',sampled_other_points=len(cloud),
        results=results,cable_centreline_margin_mm=margin,step_mm=1,plane_domain_mm=[-64,106],
        material_verified=False,source_cross_return_verified=False,native_changed=False,selected=False,W5_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in (fp,af,__import__('pathlib').Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'underbody-channel-allocation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(worker_seconds=report['worker_seconds'],results=results)),flush=True)


if __name__=='__main__':run()
