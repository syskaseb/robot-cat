"""One axial four-arc flex topology, not another transverse-plane offset.

Anchors run along the Hip axis above the motor, rather than a90mm vertical
loop outside the whole foot envelope. Feet remain proposals, not selected
parts. Both9mm grip lands, fixed cable length and R31 are retained.
"""
import json,math,time
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,dot,norm,rotation
from plan_current_mta_interfaces import line,curve
from plan_current_joint_local_looms import scene_parts


def s_offset(start,end,axis):
    delta=sub(end,start);x=dot(delta,axis);offset=sub(delta,mul(axis,x));d=norm(offset)
    assert x>0
    if d<1e-8:return [line(start,end)]
    v=mul(offset,1/d);r=(x*x+d*d)/(4*d);theta=2*math.atan2(d,x)
    def first(t):return add(start,add(mul(axis,r*math.sin(t)),mul(v,r*(1-math.cos(t)))))
    mid=first(theta)
    def second(t):return sub(end,add(mul(axis,r*math.sin(theta-t)),mul(v,r*(1-math.cos(theta-t)))))
    return [curve(start,mid,first(theta/2),r,theta),curve(mid,end,second(theta/2),r,theta)]


def flex(start,end,axis,side,total=108):
    """Two exact S offsets; midpoint is free cable, never a fictitious clamp."""
    direction=[0,side,0];centre=mul(add(start,end),.5)
    def at(h):
        mid=add(centre,mul(direction,h))
        return s_offset(start,mid,axis)+s_offset(mid,end,axis)
    lo,hi=0.,50.
    if not sum(p['length_mm'] for p in at(lo))<=total<=sum(p['length_mm'] for p in at(hi)):return None
    for _ in range(40):
        mid=(lo+hi)/2
        if sum(p['length_mm'] for p in at(mid))<total:lo=mid
        else:hi=mid
    parts=at((lo+hi)/2)
    if min(p.get('radius_mm',float('inf')) for p in parts)<31:return None
    return parts


def build():
    tick=time.monotonic();hf=OUT/'harness-interfaces-plan.json'
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    knee=OUT/'joint-local-knee-plan.json';proof=OUT/'joint-local-knee-material.json'
    sources=json.loads(hf.read_text());axes=json.loads(af.read_text())['axes'];kp=json.loads(knee.read_text())
    receipt=json.loads(proof.read_text());assert receipt['status']=='EIGHT_KNEE_SECTIONS_SAMPLED_MATERIAL_ONLY_FULL_CABLE_OPEN'
    for q in (kp,receipt):
        for n,h in q['source_sha256'].items():assert SHA(ROOT/n)==h,n
    rows=[];bad=[]
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        family=[r for r in sources['looms'] if r['physical_leg']==leg]
        axis=next(a for a in axes if a['code']==family[0]['cad_code'] and a['stage']=='Hip')
        front=leg.startswith('Front');side=1 if leg.endswith('Left') else -1
        outward=[-1 if front else 1,0,0];pivot=axis['pivot_mm']
        for lane,source in enumerate(family):
            # Allocate the whole Hip family ABOVE retained source/return lanes
            # at Z43..50, not move individual wires around each witness.
            fixed=[pivot[0]-outward[0]*55,side*(45+8*lane),65]
            moving=[pivot[0]+outward[0]*65,side*(45+8*lane),65]
            poses=[]
            for angle in range(-15,16):
                end=add(pivot,rotation(sub(moving,pivot),axis['axis'],angle))
                tangent=rotation(outward,axis['axis'],angle)
                start=add(fixed,mul(outward,9));last=sub(end,mul(tangent,9))
                # Hip axis is truly parallel to axial departure, within source tolerance.
                assert norm(sub(tangent,outward))<1e-8
                q=flex(start,last,outward,side)
                if q is None:bad.append(dict(section=source['loom']+'/Hip',angle=angle));continue
                poses.append(dict(angle=angle,parts=[line(fixed,start)]+q+[line(last,end)],
                    flex_length_mm=sum(p['length_mm'] for p in q),minimum_R_mm=min(p.get('radius_mm',float('inf')) for p in q)))
            rows.append(dict(section=source['loom']+'/Hip',loom=source['loom'],cad_code=source['cad_code'],physical_leg=leg,
                parent_stage='Frame',child_stage='Hip',project_OD_mm=6,guide_mm=126,
                fixed_anchor_world_mm=fixed,moving_anchor_rest_world_mm=moving,poses=poses,
                support_status='OPEN: proposed near-frame and near-case roots; actual feet, tool access and load path not qualified'))
    result=dict(status='REJECTED_AXIAL_HIP_MATH' if bad else 'AXIAL_HIP_MATH_ONLY',
        loops=rows+kp['loops'],failures=bad,knee_reuse_commit='cca0194',selected=False,native_changed=False,
        W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
        manufacturer_dynamic_radius_verified=False,
        root_plan='Axial120mm span, all12 Hip sections at Z65 above retained source/return lanes Z43..50; four circular arcs distribute slack. Both roots require native qualification.',
        rejected_lower_gallery=dict(level_mm=45,flex_mm=110,wire_contacts=6,
            wires=['W075','W050','W045_CUSTOM','W058','W053_CUSTOM'],
            reason='Shared source and rear return lanes occupy lower axial gallery; no material gate or native edits performed'),
        worker_seconds=time.monotonic()-tick,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (hf,af,knee,proof,Path(__file__))})
    if not bad:
        from screen_current_remaining_routes import route_rows
        from route_current_leg_fanouts import sampling_parts
        from screen_current_moving_looms import only_new_pairs
        import itertools
        retained,pins=route_rows(tuple(OUT/(s+'-plan.json') for s in ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
        head=OUT/'head-wire-screen-reference.json';hp=json.loads(head.read_text())
        for n,h in hp['source_sha256'].items():assert SHA(ROOT/n)==h,n
        fixed=[dict(r,segments=sampling_parts(r['segments'])) for r in list(retained.values())+hp['rows']]
        def row(r,h=0,k=0):return dict(wire=r['section'],OD_mm=6,segments=sampling_parts(scene_parts(r,h,k,axes)))
        nominal=[row(r) for r in result['loops']];near=only_new_pairs(fixed,nominal)
        rejected=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY'];cases=[]
        if not rejected:
            for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
                moving=[r for r in result['loops'] if r['physical_leg']==leg];names={r['section'] for r in moving}
                stationary=fixed+[r for r in nominal if r['wire'] not in names]
                for h,k in itertools.product((-15,0,15),repeat=2):
                    if h==k==0:continue
                    hits=[q for q in only_new_pairs(stationary,[row(r,h,k) for r in moving]) if q['status']=='REJECT_PLANNING_PROXIMITY']
                    cases.append(dict(leg=leg,hip=h,knee=k,rejected=hits));rejected.extend(hits)
        result.update(status='REJECTED_AXIAL_HIP_SHARED_WIRES' if rejected else 'AXIAL_HIP_SHARED_SAMPLED_ONLY_MATERIAL_AND_FEET_OPEN',
            rejected=rejected,near_pairs=near,motion_cases=cases)
        result['source_sha256'].update({f.relative_to(ROOT).as_posix():SHA(f) for f in pins|{head}})
    result['worker_seconds']=time.monotonic()-tick
    (OUT/'hip-axial-loom-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],math_failures=bad,wire_rejections=result.get('rejected'),worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':build()
