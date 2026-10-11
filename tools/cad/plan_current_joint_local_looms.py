"""One joint-local pilot after rejecting whole-leg roof-loop architecture.

Route the existing continuous cable along rigid leg members, with separate
flex sections at crossed joints. No new electrical connector, reduced bend
radius, selected mount, native edit or W5 credit. This first pilot checks TWO
parallel FL Knee loops, not a fictitious complete cable to the body.
"""
import json,math,time,zipfile,itertools
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,dot,norm,rotation,metrics,curve_length,poles
from plan_current_mta_interfaces import line

RADIUS=45.0
LENGTH=math.pi*RADIUS+10
OD=6.0


def solve_loop(start,start_axis,end,end_axis,length=LENGTH):
    """Bounded handle solve at fixed endpoints, tangents and cable length.

    Adding the REAL two grip lands changes the end tangents' lever arms.
    A fixed arbitrary first handle is not a physical cable constraint.
    """
    for first in (70,65,75,60,80,55,85,50,90):
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
            sampled_minimum_R_mm=radius,sampled_bounds_mm=bounds)
    return None


def basis(axis,side):
    # Actual joint axis, not a mirrored front/rear source or guessed globalY.
    normal=mul(axis,1/norm(axis))
    if side*normal[1]<0:normal=mul(normal,-1)
    vertical=sub([0,0,1],mul(normal,normal[2]));vertical=mul(vertical,1/norm(vertical))
    bulge=[1,0,0]
    bulge=sub(bulge,mul(normal,dot(bulge,normal)))
    bulge=sub(bulge,mul(vertical,dot(bulge,vertical)));bulge=mul(bulge,1/norm(bulge))
    return normal,vertical,bulge


def build():
    tick=time.monotonic();af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    hf=OUT/'harness-interfaces-plan.json';axes=json.loads(af.read_text())['axes']
    source=json.loads(hf.read_text());families=[q for q in source['looms'] if q['loom'] in ('FL2','FL3')]
    axis=next(a for a in axes if a['code']==families[0]['cad_code'] and a['stage']=='Knee')
    pivot=axis['pivot_mm'];normal,vertical,bulge=basis(axis['axis'],1)
    archive=ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    # Include integral LegLink005/006 and counter-shells, not merely the
    #bought servo casing. The first pilot exposed precisely this omission.
    members=[q for q in components if q['stage']=='Motion_'+families[0]['cad_code']+'_Knee']
    corners=[]
    for row in members:
        b=row['bbox_mm'];corners.extend(itertools.product(*((b[j],b[j+3]) for j in range(3))))
    # These are candidate tie planes; attachable parent/child feet remain
    #open. Conservative corner projection is an allocation, not a contact.
    plane=max(dot(sub(p,pivot),normal) for p in corners)+OD/2+1.5
    loops=[];failures=[]
    for lane,row in enumerate(families):
        centre=add(pivot,mul(normal,plane+lane*8))
        fixed=add(centre,mul(vertical,RADIUS));moving=add(centre,mul(vertical,-RADIUS))
        poses=[]
        for angle in range(-15,16):
            end=add(pivot,rotation(sub(moving,pivot),axis['axis'],angle))
            end_axis=rotation(mul(bulge,-1),axis['axis'],angle)
            curve_start=add(fixed,mul(bulge,9));curve_end=sub(end,mul(end_axis,9))
            q=solve_loop(curve_start,bulge,curve_end,end_axis)
            if q is None:failures.append(dict(loom=row['loom'],angle=angle,cause='NO_FIXED_LENGTH_R31_LOOP'));continue
            parts=[line(fixed,curve_start),q,line(curve_end,end)]
            poses.append(dict(angle=angle,curve=q,parts=parts))
        loops.append(dict(loom=row['loom'],joint=axis['name'],cad_code=row['cad_code'],
            parent_stage='Hip',child_stage='Knee',project_OD_mm=OD,guide_mm=LENGTH+18,flex_guide_mm=LENGTH,
            independent_insulation_land_mm_each=9,
            fixed_anchor_world_mm=fixed,moving_anchor_rest_world_mm=moving,
            fixed_tangent_world=bulge,moving_tangent_rest_world=mul(bulge,-1),
            plane_axis_offset_mm=plane+lane*8,poses=poses,cores=row['electrical'],
            parent_and_child_anchor_supports='OPEN: actual mounting feet; both9mm insulation lands in this route'))
    files=(af,hf,archive,Path(__file__),Path(__file__).with_name('plan_current_moving_looms.py'))
    result=dict(status='REJECTED_JOINT_LOCAL_PILOT_MATH' if failures else 'JOINT_LOCAL_PILOT_MATH_ONLY',
        scope='Two FL Knee sections only; continuous factory cables, no extra electrical connection',
        reason='Whole-body roof arches crossed retained source/head wires; single risingS had no common length interval',
        pivot_mm=pivot,axis=axis['axis'],loops=loops,failures=failures,
        complete_child_material_members=[q['name'] for q in members],
        old_roof_and_single_S_architectures_rejected=True,
        stage_ownership='Only local Knee motion here; both loops move rigidly with parent Hip. Ankle drive cable casing belongs to Knee, not Ankle.',
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


if __name__=='__main__':build()
