"""One five-owner plan: inward front heads, upward RR splice seats/arms.

Actual witnesses identify RR3Splice1 seat and Splice0 arms25..27, not an
unavoidable factory-wire crossing. Preserve all cable endpoints/lengths and
seven unaffected support groups. Reject with decomposed actual new material
before spending time on complete unions/native histories.
"""
import copy
import itertools
import json
import time
from pathlib import Path
import FreeCAD as A
import build_remaining_loom_supports as G
from prepare_rail_hip_retention import overlay
from support_entry_port import build as entry_build
from diagnose_remaining_support_endpoints import moved,transform
P=G.P


def orthogonal(start,end,order):
    points=[list(start)];p=list(start)
    for axis in order:
        if abs(p[axis]-end[axis])<1e-8:continue
        p=p.copy();p[axis]=end[axis];points.append(p)
    assert max(abs(a-b) for a,b in zip(p,end))<1e-7
    return points


def allocate_knee_ports(plan,paths,ports,roots,axes):
    """Finite joint radial-face/orthogonal-arm allocation, not offset retries."""
    owner='RearRightKneeCarrier';rr=next(r for r in plan['hips'] if r['loom']=='RR1')
    local=[]
    for h,k in itertools.product((-15,0,15),repeat=2):
        q=P.wire(next(p['parts'] for p in rr['poses'] if p['angle']==h))
        q.Placement=transform(axes,rr['cad_code'],h,k,'Knee').inverse()*q.Placement
        local.append(q)
    domains={};diagnosis=[]
    for lid in ('RR3/Splice/0','RR3/Splice/1'):
        land=next(r for g in roots['groups'] if g['id']==owner for r in g['lands'] if r['id']==lid)
        oldport=next(r for g in ports['groups'] if g['id']==owner for r in g['ports'] if r['land_id']==lid)
        path=next(r for g in paths['groups'] if g['id']==owner for r in g['paths'] if r['land_id']==lid)
        v=A.Vector(*land['axis']);up=A.Vector(0,0,1);up-=v*up.dot(v);up.normalize()
        domains[lid]=[]
        for normal in ([1,0,0],[-1,0,0],list(up),list(-up)):
            port=copy.deepcopy(oldport);port['arrival_normal']=normal;profile=entry_build(land,port)
            pgap=min(q.distToShape(s)[0] for q in local for s in (profile['body'],profile['band']))
            if pgap<3.25-1e-6:
                diagnosis.append(dict(land_id=lid,normal=normal,profile_gap_mm=pgap));continue
            for order in itertools.permutations((0,1,2)):
                points=orthogonal(path['points_mm'][0],profile['arrival_world_mm'],order);arms=[]
                for a,b in zip(points,points[1:]):
                    bb=[min(x,y)-v for x,y,v in zip(a,b,(2,3,2))]+[max(x,y)+v for x,y,v in zip(a,b,(2,3,2))]
                    arms.append(P.box(bb))
                gap=min(q.distToShape(s)[0] for q in local for s in arms)
                if gap<3.25-1e-6 or any(s.common(profile['band']).Volume>1e-6 for s in arms):continue
                length=sum(A.Vector(*a).distanceToPoint(A.Vector(*b)) for a,b in zip(points,points[1:]))
                domains[lid].append(dict(normal=normal,points=points,profile=profile,arms=arms,length=length,gap=gap))
    selected=[]
    for options in itertools.product(*domains.values()):
        if any(s.common(b['profile']['band']).Volume>1e-6 for a,b in itertools.permutations(options,2)
               for s in [a['profile']['body'],*a['arms']]):continue
        selected.append(options)
    assert selected,('No coupled radial-face/arm allocation; change whole sleeve/support plane',
                     {k:len(v) for k,v in domains.items()},diagnosis)
    chosen=min(selected,key=lambda pair:sum(p['length'] for p in pair))
    return {lid:row for lid,row in zip(domains,chosen)},dict(profile_rejections=diagnosis,
        feasible_arm_domains={k:len(v) for k,v in domains.items()},joint_choices=len(selected),
        selected=[dict(land_id=lid,normal=row['normal'],points=row['points'],minimum_RR_gap_mm=row['gap']) for lid,row in zip(domains,chosen)])


def run():
    tick=time.monotonic();pf=P.OUT/'body-low-hip-rail-exit-plan.json';plan=json.loads(pf.read_text())
    inputs=[P.OUT/n for n in ('remaining-support-shared-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json')]
    original=[json.loads(f.read_text()) for f in inputs]
    paths,ports,roots,changed=overlay(plan,*original)
    owner='RearRightKneeCarrier'
    for current,source in zip((paths,ports,roots),original):current['groups'].append(copy.deepcopy(next(g for g in source['groups'] if g['id']==owner)))
    axesfile=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    selected,allocation=allocate_knee_ports(plan,paths,ports,roots,axes)
    modifications=[('FrontLeftFixedCarrier','FL1/Hip/Fixed',[0,-1,0]),
                   ('FrontRightFixedCarrier','FR1/Hip/Fixed',[0,1,0])]
    knee_lands=next(g for g in roots['groups'] if g['id']==owner)['lands']
    for lid,row in selected.items():modifications.append((owner,lid,row['normal']))
    changed_ports=[]
    for owner,lid,normal in modifications:
        land=next(r for g in roots['groups'] if g['id']==owner for r in g['lands'] if r['id']==lid)
        port=next(r for g in ports['groups'] if g['id']==owner for r in g['ports'] if r['land_id']==lid)
        port['arrival_normal']=normal;profile=entry_build(land,port);port['arrival_world_mm']=profile['arrival_world_mm']
        path=next(r for g in paths['groups'] if g['id']==owner for r in g['paths'] if r['land_id']==lid)
        if owner.endswith('FixedCarrier'):
            original_path=next(r for g in original[0]['groups'] if g['id']==owner for r in g['paths'] if r['land_id']==lid)
            prefix=original_path['points_mm'][:-1]
            path['points_mm']=prefix+orthogonal(prefix[-1],port['arrival_world_mm'],(2,1,0))[1:]
        else:path['points_mm']=selected[lid]['points']
        path['post_arrival_normal']=normal
        changed_ports.append(dict(owner=owner,land_id=lid,normal=normal,profile=profile,path=path))
    # Nominal RR flex against EVERY new RR support primitive in nine coupled
    # Hip/Knee samples. A pass is only an allocation preflight, not full gate.
    rr=next(r for r in plan['hips'] if r['loom']=='RR1');contacts=[];checks=0
    rr_prim=[]
    for row in changed_ports:
        if row['owner']!='RearRightKneeCarrier':continue
        rr_prim += [(row['land_id']+'/Body',row['profile']['body']), (row['land_id']+'/Band',row['profile']['band'])]
        for i,(a,b) in enumerate(zip(row['path']['points_mm'],row['path']['points_mm'][1:])):
            bounds=[min(x,y)-v for x,y,v in zip(a,b,(2,3,2))]+[max(x,y)+v for x,y,v in zip(a,b,(2,3,2))]
            rr_prim.append((row['land_id']+'/Arm'+str(i),P.box(bounds)))
    for h in (-15,0,15):
        wire=P.wire(next(p['parts'] for p in rr['poses'] if p['angle']==h))
        for k in (-15,0,15):
            t=transform(axes,rr['cad_code'],h,k,'Knee')
            for name,s in rr_prim:
                gap=wire.distToShape(moved(s,t))[0];checks+=1
                if gap<3.25-1e-6:contacts.append(dict(target=name,hip=h,knee=k,gap_mm=gap))
    dests={}
    for name,data in (('paths',paths),('ports',ports),('roots',roots)):
        f=P.OUT/('body-rail-support-r2-'+name+'.json');f.write_text(json.dumps(data,indent=2)+'\n');dests[name]=f.relative_to(P.ROOT).as_posix()
    result=dict(status='RAIL_FIVE_OWNER_CORRECTION_PREFLIGHT_CLEAR_FULL_SPACE_OPEN' if not contacts else 'REJECTED_RAIL_FIVE_OWNER_CORRECTION_PREFLIGHT',
        changed_support_owners=[g['id'] for g in roots['groups']],full_plan_files=dests,
        changed_ports=[dict(owner=r['owner'],land_id=r['land_id'],normal=r['normal'],arrival=r['profile']['arrival_world_mm'],points=r['path']['points_mm']) for r in changed_ports],
        joint_knee_allocation=allocation,
        contacts=contacts,checks=checks,worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in inputs+[pf,axesfile,Path(__file__),Path(__file__).with_name('prepare_rail_hip_retention.py')]},
        selected=False,W5_complete=False,physical_pass=False,
        scope='Exact RR flex vs changed RR3splice seat/band/arm primitives in9coupled poses. Other material/oldwires/front motion/newcompleteunions still OPEN. No inherited qualification of changed fifth carrier.')
    (P.OUT/'body-rail-support-correction-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],contacts=contacts,checks=checks,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
