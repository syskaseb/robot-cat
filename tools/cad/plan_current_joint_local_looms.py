"""One joint-local pilot after rejecting whole-leg roof-loop architecture.

Route the existing continuous cable along rigid leg members, with separate
flex sections at crossed joints. No new electrical connector, reduced bend
radius, selected mount, native edit or W5 credit. This first pilot checks TWO
parallel FL Knee loops, not a fictitious complete cable to the body.
"""
import json,math,time,zipfile,itertools,copy
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,dot,norm,rotation,metrics,curve_length,poles
from plan_current_mta_interfaces import line

RADIUS=45.0
LENGTH=math.pi*RADIUS+10
OD=6.0


def solve_loop(start,start_axis,end,end_axis,length=LENGTH,first_candidates=None):
    """Bounded handle solve at fixed endpoints, tangents and cable length.

    Adding the REAL two grip lands changes the end tangents' lever arms.
    A fixed arbitrary first handle is not a physical cable constraint.
    """
    for first in ((70,65,75,60,80,55,85,50,90) if first_candidates is None else first_candidates):
        lo,hi=1.,200.
        def at(handle):return poles(start,start_axis,end,mul(end_axis,-1),first,handle)
        if not curve_length(at(lo))<=length<=curve_length(at(hi)):continue
        for _ in range(46):
            mid=(lo+hi)/2
            if curve_length(at(mid))<length:lo=mid
            else:hi=mid
        p=at((lo+hi)/2);actual,radius,bounds=metrics(p,360)
        if abs(actual-length)>1e-6 or radius<31:continue
        return dict(kind='bezier',poles_mm=p,start=p[0],end=p[-1],length_mm=actual,
            first_handle_mm=first,second_handle_mm=(lo+hi)/2,
            sampled_minimum_R_mm=radius,sampled_bounds_mm=bounds)
    return None


def basis(axis,side,stage='Knee',front=True):
    # Actual joint axis, not a mirrored front/rear source or guessed globalY.
    normal=mul(axis,1/norm(axis))
    outward=[0,side,0] if stage=='Knee' else [-1 if front else 1,0,0]
    if dot(normal,outward)<0:normal=mul(normal,-1)
    vertical=sub([0,0,1],mul(normal,normal[2]));vertical=mul(vertical,1/norm(vertical))
    bulge=[1 if front else -1,0,0] if stage=='Knee' else [0,side,0]
    bulge=sub(bulge,mul(normal,dot(bulge,normal)))
    bulge=sub(bulge,mul(vertical,dot(bulge,vertical)));bulge=mul(bulge,1/norm(bulge))
    return normal,vertical,bulge


def expanded_pose(row,angle):
    """One curve recipe, not620 copies of derived endpoints and grip lands."""
    pose=next(q for q in row['poses'] if q['angle']==angle)
    if 'parts' in pose:return pose
    fixed=row['fixed_anchor_world_mm'];pivot=row['pivot_mm'];bulge=row['fixed_tangent_world']
    end=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],angle))
    tangent=rotation(row['moving_tangent_rest_world'],row['joint_axis'],angle)
    start=add(fixed,mul(bulge,9));last=sub(end,mul(tangent,9))
    controls=poles(start,bulge,last,mul(tangent,-1),pose['first_handle_mm'],pose['second_handle_mm'])
    q=dict(kind='bezier',poles_mm=controls,start=start,end=last,length_mm=pose['length_mm'],
        sampled_minimum_R_mm=pose['sampled_minimum_R_mm'])
    return dict(angle=angle,curve=q,parts=[line(fixed,start),q,line(last,end)])


def scene_parts(row,hip,knee,axes):
    parts=copy.deepcopy(expanded_pose(row,hip if row['child_stage']=='Hip' else knee)['parts'])
    if row['parent_stage']=='Hip':
        axis=next(a for a in axes if a['code']==row['cad_code'] and a['stage']=='Hip')
        def moved(p):return add(axis['pivot_mm'],rotation(sub(p,axis['pivot_mm']),axis['axis'],hip))
        for segment in parts:
            for key in ('start','end','mid'):
                if key in segment:segment[key]=moved(segment[key])
            if 'poles_mm' in segment:segment['poles_mm']=[moved(v) for v in segment['poles_mm']]
    return parts


def hip_common_plane(axis,family,components,axes,faces,wire_boxes,vertical,bulge,normal):
    """Allocate the whole Hip bundle outside shared material BEFORE routing.

    Project actual saved FACE boxes and the complete leg's27 sampled poses
    into this loop's transverse region. This is conservative reservation, not
    a claim that a face box is solid material or a continuous-motion proof.
    """
    pivot=axis['pivot_mm'];footprint=[]
    # Put Hip flex ABOVE the shaft: the moving grip sits on its axis, while
    # the fixed grip sits90mm above. A centred loop occupied the raised foot
    # envelope below the shaft and forced impractical >100mm axial supports.
    centre=add(pivot,mul(vertical,RADIUS))
    for angle in range(-15,16):
        first=add(centre,mul(vertical,RADIUS));rest=sub(centre,mul(vertical,RADIUS))
        end=add(pivot,rotation(sub(rest,pivot),axis['axis'],angle))
        tangent=rotation(mul(bulge,-1),axis['axis'],angle)
        q=solve_loop(add(first,mul(bulge,9)),bulge,sub(end,mul(tangent,9)),tangent)
        assert q is not None
        footprint.extend([first,end]+q['poles_mm'])
    vr=[min(dot(sub(p,pivot),vertical) for p in footprint)-4.5,max(dot(sub(p,pivot),vertical) for p in footprint)+4.5]
    br=[min(dot(sub(p,pivot),bulge) for p in footprint)-4.5,max(dot(sub(p,pivot),bulge) for p in footprint)+4.5]
    candidates=[]
    by_owner={}
    for face in faces:by_owner.setdefault(face['owner'],[]).append(face['bounds_mm'])
    def reserve(owner,points):
        v=[dot(sub(p,pivot),vertical) for p in points];b=[dot(sub(p,pivot),bulge) for p in points]
        if max(v)<vr[0] or min(v)>vr[1] or max(b)<br[0] or min(b)>br[1]:return
        candidates.append((max(dot(sub(p,pivot),normal) for p in points),owner))
    def corners(b):return list(itertools.product(*((b[j],b[j+3]) for j in range(3))))
    for face in faces:reserve(face['owner'],corners(face['bounds_mm']))
    for wire in wire_boxes:reserve('RetainedWire/'+wire['owner'],corners(wire['bounds_mm']))
    aa={a['stage']:a for a in axes if a['code']==family['cad_code']}
    for part in components:
        if not part['stage'].startswith('Motion_'+family['cad_code']+'_'):continue
        stage=part['stage'].split('_')[-1];chain=('Hip','Knee','Ankle')[:('Hip','Knee','Ankle').index(stage)+1]
        # A whole Ankle bbox includes empty diagonal space and produced a
        # >500mm long layout. Use the already saved individual surface boxes.
        boxes=by_owner.get('P0_'+part['name'])
        assert boxes,('MISSING_ACTUAL_SURFACES',part['name'])
        for angles in itertools.product((-15,0,15),repeat=len(chain)):
            for bounds in boxes:
                points=corners(bounds)
                for name,angle in reversed(list(zip(chain,angles))):
                    a=aa[name];points=[add(a['pivot_mm'],rotation(sub(p,a['pivot_mm']),a['axis'],angle)) for p in points]
                reserve('SampledFace/'+part['name'],points)
    furthest,owner=max(candidates)
    return furthest+4.5,dict(method='whole transverse material reservation, not scalar collision adjustment',
        limiting_owner=owner,material_axial_extent_mm=furthest,margin_mm=4.5,
        transverse_vertical_bounds_mm=vr,transverse_bulge_bounds_mm=br,
        complete_leg_sample_angles=[-15,0,15],continuous_sweep_verified=False,
        conservative_face_bounds_not_actual_contacts=True)


def group(axis,families,components,axes,faces,wire_boxes):
    pivot=axis['pivot_mm'];side=1 if families[0]['physical_leg'].endswith('Left') else -1
    front=families[0]['physical_leg'].startswith('Front');stage=axis['stage']
    normal,vertical,bulge=basis(axis['axis'],side,stage,front)
    members=[q for q in components if q['stage']=='Motion_'+families[0]['cad_code']+'_'+stage]
    corners=[]
    for row in members:
        b=row['bbox_mm'];corners.extend(itertools.product(*((b[j],b[j+3]) for j in range(3))))
    plane=max(dot(sub(p,pivot),normal) for p in corners)+OD/2+1.5
    allocation=None
    if stage=='Hip':plane,allocation=hip_common_plane(axis,families[0],components,axes,faces,wire_boxes,vertical,bulge,normal)
    loops=[];failures=[]
    for lane,row in enumerate(families):
        centre=add(pivot,mul(normal,plane+lane*8))
        if stage=='Hip':centre=add(centre,mul(vertical,RADIUS))
        fixed=add(centre,mul(vertical,RADIUS));moving=add(centre,mul(vertical,-RADIUS));poses=[]
        for angle in range(-15,16):
            end=add(pivot,rotation(sub(moving,pivot),axis['axis'],angle))
            end_axis=rotation(mul(bulge,-1),axis['axis'],angle)
            curve_start=add(fixed,mul(bulge,9));curve_end=sub(end,mul(end_axis,9))
            q=solve_loop(curve_start,bulge,curve_end,end_axis)
            if q is None:failures.append(dict(loom=row['loom'],stage=stage,angle=angle,cause='NO_FIXED_LENGTH_R31_LOOP'));continue
            poses.append(dict(angle=angle,first_handle_mm=q['first_handle_mm'],second_handle_mm=q['second_handle_mm'],
                length_mm=q['length_mm'],sampled_minimum_R_mm=q['sampled_minimum_R_mm']))
        loops.append(dict(loom=row['loom'],section=row['loom']+'/'+stage,joint=axis['name'],cad_code=row['cad_code'],
            physical_leg=row['physical_leg'],parent_stage='Hip' if stage=='Knee' else 'Frame',child_stage=stage,
            pivot_mm=pivot,joint_axis=axis['axis'],
            project_OD_mm=OD,guide_mm=LENGTH+18,flex_guide_mm=LENGTH,independent_insulation_land_mm_each=9,
            fixed_anchor_world_mm=fixed,moving_anchor_rest_world_mm=moving,fixed_tangent_world=bulge,
            moving_tangent_rest_world=mul(bulge,-1),plane_axis_offset_mm=plane+lane*8,poses=poses,cores=row['electrical'],
            common_material_allocation=allocation,
            complete_child_material_members=[q['name'] for q in members],
            parent_and_child_anchor_supports='OPEN: actual mounting feet; both9mm insulation lands in this route'))
    return loops,failures


def build_knees():
    """Independent eight-section result; never resurrect the parked Hip layout."""
    tick=time.monotonic();af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    hf=OUT/'harness-interfaces-plan.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text())['axes'];source=json.loads(hf.read_text())
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    loops=[];failures=[]
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        family=[q for q in source['looms'] if q['physical_leg']==leg]
        crossed=[q for q in family if any(n.endswith('_Knee') for n in q['crossed_axes'])]
        axis=next(a for a in axes if a['code']==family[0]['cad_code'] and a['stage']=='Knee')
        sections,bad=group(axis,crossed,components,axes,[],[]);loops.extend(sections);failures.extend(bad)
    assert len(loops)==8
    files={af,hf,archive,Path(__file__),Path(__file__).with_name('plan_current_moving_looms.py')}
    result=dict(status='REJECTED_JOINT_LOCAL_KNEE_MATH' if failures else 'JOINT_LOCAL_KNEE_MATH_ONLY',
        scope='Eight Knee flex sections only; Hip, rigid joins, complete cables and native supports OPEN',
        loops=loops,failures=failures,pilot_reuse_commit='86f0754',selected=False,native_changed=False,
        W5_complete=False,physical_pass=False,continuous_sweep_verified=False,manufacturer_dynamic_radius_verified=False,
        worker_seconds=time.monotonic()-tick,source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files})
    (OUT/'joint-local-knee-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],sections=len(loops),failures=failures,worker_seconds=result['worker_seconds'])),flush=True)
    return result


def build():
    tick=time.monotonic();af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    hf=OUT/'harness-interfaces-plan.json';axes=json.loads(af.read_text())['axes']
    source=json.loads(hf.read_text())
    archive=ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    spatialfile=OUT/'BUS-material-routing-space.json';spatial=json.loads(spatialfile.read_text())
    for n,h in spatial['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from screen_current_remaining_routes import route_rows
    from route_current_leg_fanouts import sampling_parts
    from open_prototype_path_preflight import samples
    retained,wirepins=route_rows(tuple(OUT/(s+'-plan.json') for s in
        ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    headsfile=OUT/'head-wire-screen-reference.json';heads=json.loads(headsfile.read_text())
    for n,h in heads['source_sha256'].items():assert SHA(ROOT/n)==h,n
    wire_boxes=[]
    for row in list(retained.values())+heads['rows']:
        # 1mm centreline sampling plus0.5mm extension; bounding reservations
        # include the actual project insulation radius, not a zero-width path.
        radius=row['OD_mm']/2+.5
        for _,point in samples(sampling_parts(row['segments']),step=1):
            wire_boxes.append(dict(owner=row['wire'],bounds_mm=[v-radius for v in point]+[v+radius for v in point]))
    loops=[];failures=[]
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        family=[q for q in source['looms'] if q['physical_leg']==leg]
        for stage in ('Hip','Knee'):
            crossed=[q for q in family if any(n.endswith('_'+stage) for n in q['crossed_axes'])]
            axis=next(a for a in axes if a['code']==family[0]['cad_code'] and a['stage']==stage)
            sections,bad=group(axis,crossed,components,axes,spatial['boxes'],wire_boxes);loops.extend(sections);failures.extend(bad)
    files={af,hf,archive,spatialfile,headsfile,Path(__file__),Path(__file__).with_name('plan_current_moving_looms.py'),
        Path(__file__).with_name('route_current_leg_fanouts.py'),Path(__file__).with_name('open_prototype_path_preflight.py')}|wirepins
    result=dict(status='REJECTED_JOINT_LOCAL_SECTIONS_MATH' if failures else 'JOINT_LOCAL_SECTIONS_MATH_ONLY',
        scope='20 local flex sections for12 continuous factory leads; rigid joining sections and native feet OPEN',
        reason='Whole-body roof arches crossed retained source/head wires; single risingS had no common length interval',
        loops=loops,failures=failures,pilot_reuse_commit='86f0754',
        old_roof_and_single_S_architectures_rejected=True,
        stage_ownership='Hip section parent Frame/child Hip; Knee section parent Hip/child Knee. Ankle drive cable casing belongs to Knee, not Ankle.',
        untouched=['P0','E6','bankR47','15drives','replaceableMG92B','torso325x200x160'],
        open=['actual nominal material','sampled Hip/Knee/Ankle material','two local supports per section',
              'rigid interstage guides','Hip flex sections','source/plug and all36 body ends','whole stock and selection'],
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        manufacturer_dynamic_radius_verified=False,continuous_sweep_verified=False,
        worker_seconds=time.monotonic()-tick,source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in files})
    (OUT/'joint-local-loom-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],loops=len(loops),pose_count=sum(len(q['poses']) for q in loops),
        failures=failures,worker_seconds=result['worker_seconds'])),flush=True)
    return result


def screen(knees_only=False):
    from current_material_reservations import FaceKeepouts
    from screen_current_remaining_routes import route_rows
    from screen_current_moving_looms import only_new_pairs
    from route_current_leg_fanouts import sampling_parts
    tick=time.monotonic();stem='joint-local-knee' if knees_only else 'joint-local-loom'
    source=OUT/(stem+'-plan.json');p=json.loads(source.read_text())
    assert p['status']==('JOINT_LOCAL_KNEE_MATH_ONLY' if knees_only else 'JOINT_LOCAL_SECTIONS_MATH_ONLY')
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    axesfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(axesfile.read_text())['axes']
    headsfile=OUT/'head-wire-screen-reference.json';heads=json.loads(headsfile.read_text())
    retained,pins=route_rows(tuple(OUT/(s+'-plan.json') for s in
        ('ground-tree','data-bridges','positive-source','s0-in-extension','BUS-routes')))
    # Retained body routes also contain Beziers. The proximity checker accepts
    # line/arc samples, regardless of whether a route is old or newly planned.
    fixed=[dict(r,segments=sampling_parts(r['segments'])) for r in list(retained.values())+heads['rows']];rows=[]
    for row in p['loops']:rows.append(dict(wire=row['section'],OD_mm=OD,segments=sampling_parts(scene_parts(row,0,0,axes))))
    near=only_new_pairs(fixed,rows);bad=[q for q in near if q['status']=='REJECT_PLANNING_PROXIMITY']
    spatialfile=OUT/'BUS-material-routing-space.json';spatial=json.loads(spatialfile.read_text())
    for n,h in spatial['source_sha256'].items():assert SHA(ROOT/n)==h,n
    materials=FaceKeepouts(spatial['boxes'])
    reservations=[dict(section=r['wire'],**hit) for r in rows if (hit:=materials.hit(r['segments'],3.5))]
    cases=[]
    if not bad:
        for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
            sections=[r for r in p['loops'] if r['physical_leg']==leg]
            names={r['section'] for r in sections};stationary=fixed+[r for r in rows if r['wire'] not in names]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                if hip==knee==0:continue
                changed=[dict(wire=r['section'],OD_mm=OD,segments=sampling_parts(scene_parts(r,hip,knee,axes))) for r in sections]
                failures=[q for q in only_new_pairs(stationary,changed) if q['status']=='REJECT_PLANNING_PROXIMITY']
                cases.append(dict(physical_leg=leg,hip=hip,knee=knee,rejected=failures))
                bad.extend(dict(physical_leg=leg,hip=hip,knee=knee,**q) for q in failures)
            print('Joint-local cheap whole-leg motion',leg,'rejected',len(bad),flush=True)
    pins.update((source,axesfile,headsfile,spatialfile,Path(__file__),Path(__file__).with_name('current_material_reservations.py')))
    result=dict(status='REJECTED_JOINT_LOCAL_SHARED_SCREEN' if bad else 'JOINT_LOCAL_SHARED_SAMPLED_ONLY_MATERIAL_OPEN',
        sections=len(p['loops']),continuous_cables=len({r['loom'] for r in p['loops']}),near_pairs=near,rejected=bad,motion_cases=cases,
        nominal_face_reservations_not_actual_contacts=reservations,
        selected=False,W5_complete=False,native_changed=False,physical_pass=False,
        full_rigid_and_body_routes_open=True,continuous_or_simultaneous_all_legs_verified=False,
        worker_seconds=time.monotonic()-tick,source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in pins})
    (OUT/(stem+'-screen.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],rejected=bad,reservations=reservations,
        worker_seconds=result['worker_seconds'])),flush=True)
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--screen',action='store_true')
    parser.add_argument('--knees-only',action='store_true');args=parser.parse_args()
    screen(args.knees_only) if args.screen else build_knees() if args.knees_only else build()
