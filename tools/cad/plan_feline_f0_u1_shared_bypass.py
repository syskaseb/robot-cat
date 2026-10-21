"""One F0 load-path bypass around the whole current U1 obstruction.

Retain the selected case/bond, old POST joint, material section and support
height. Replace the blocking vertical downleg, not the PCB, factory leads,
or a small notch in the controller. Native production detail remains N03.
"""
import FreeCAD as A
from feline_source_restraint_plan import box,joined


def construct(old,post,case,obstacles,metadata):
    px=post.BoundBox.XMin;bottom=case.Solids[0].CenterOfMass.z
    y0,y1=69.,71.;upper=30.75;thick=2.;intervals=[]
    for n,s in obstacles.items():
        if n in ('SourceBody:F0:spine','SourceBody:POST:spine'):continue
        md=metadata.get(n,{})
        if md.get('kind')=='PETG' and md.get('print_group')=='upper':continue
        b=s.BoundBox;radius=0
        if not s.Solids:
            radius=md.get('nominal_profile_radius_mm')
            assert isinstance(radius,(int,float)) and radius>0,(n,'unreceived profile')
        gap=1.25+radius
        if b.YMin>y1+gap or b.YMax<y0-gap or b.ZMin>upper+gap or b.ZMax<bottom+2-gap:continue
        intervals.append((b.XMin-thick-gap,b.XMax+gap,n))
    # Union the complete projected obstruction intervals before any CAD trial.
    x=px;witnesses=[]
    for lo,hi,n in sorted(intervals):
        if lo<x+1e-7 and hi>x:
            witnesses.append(n);x=hi
    assert x>px and x+thick<183.5-3.25
    tool=box([px-.001,y0-.001,bottom+2],[px+2+.001,y1+.001,upper])
    new=joined([old.cut(tool),box([x,y0,bottom],[x+thick,y1,upper+thick]),
                box([px,y0,bottom],[x+thick,y1,bottom+thick]),
                box([px,y0,upper],[x+thick,y1,upper+thick])]).removeSplitter()
    assert new.isValid() and len(new.Solids)==1
    old_joint=old.common(post).Volume;new_joint=new.common(post).Volume
    assert old_joint>1e-5 and abs(old_joint-new_joint)<1e-5
    assert new.fuse(post).isValid() and len(new.fuse(post).Solids)==1
    return new,dict(status='F0_SHARED_U1_OBSTRUCTION_BYPASS_NOT_WORLD_ACCEPTANCE',
        original_column_X_mm=[px,px+2],bypass_column_X_mm=[x,x+2],
        column_Y_mm=[y0,y1],unchanged_cross_section_mm=[2,2],
        whole_region_projected_witnesses=witnesses,
        unchanged_POST_material_joint_mm3=new_joint,
        unchanged_case_and_bond=True,selected_parts_changed=False,
        roots_load_test_and_native_detail_phase2_N03_OPEN=True,N01_complete=False,physical_pass=False)


def receive(new,old,fixed,metadata,print_members,pins):
    import time
    from feline_fore_power_pair import SolidQueries
    from feline_solid_distance import bbox_lower_bound
    from plan_feline_pi_root_access import profile_gap
    from receive_feline_jpwm_whole_pose import solid_profile_target
    tick=time.monotonic();q=SolidQueries();checks={};joints={}
    for n in print_members:
        if n=='SourceBody:F0:spine':continue
        s=fixed[n]
        if bbox_lower_bound(old.BoundBox,s.BoundBox)>1e-6:continue
        before=old.common(s).Volume
        if before>1e-5:
            after=new.common(s).Volume
            assert abs(before-after)<1e-5,(n,'original print joint changed')
            joints[n]=after
    for n,s in fixed.items():
        if n=='SourceBody:F0:spine' or n in print_members:continue
        minimum=.2 if n=='Ref_Material_F0_CP2_0_0' else 0. if n=='SourceBody:F0:patch' else 1.25
        radius=metadata.get(n,{}).get('nominal_profile_radius_mm',0) if not s.Solids else 0
        if bbox_lower_bound(new.BoundBox,s.BoundBox)>minimum+(radius or 0)+1e-6:continue
        if not s.Solids:
            assert radius and radius>0,(n,'unknown curve radius')
            lower=profile_gap(new,s,radius,minimum)
            if lower['ok']:checks[n]=lower;continue
            s=solid_profile_target(s,metadata[n])
        gap=q.distance(new,s);row=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
        if minimum==0:
            row['common_mm3']=new.common(s).Volume;row['ok'] &= row['common_mm3']<1e-5
        checks[n]=row
    failures=[n for n,r in checks.items() if not r['ok']]
    return dict(status='F0_SHARED_BYPASS_STATIC_HOLD' if failures else 'F0_SHARED_BYPASS_STATIC_RECEIVED',
        checks=checks,failures=failures,preserved_original_material_joints_mm3=joints,
        unchanged_other_print_members=list(print_members),source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
