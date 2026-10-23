"""Receive changed departure geometry, not whole N01 or factory-wire approval."""
import hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import pair_spacing
from receive_feline_W024_shared_body import solid
from receive_feline_jpwm_whole_pose import solid_profile_target
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin
from solve_feline_W047_simple_graph import self_conflict
import feline_tangent_routes as ft


def receive(scene,metadata,whole,shape,cap,oldcap,row_recipes,bank_recipe,outer,bus_gap):
    tick=time.monotonic();dest=OUT/'n01-W033-joint-departures-received.json'
    assert not dest.exists()
    names=['n01-W033-two-departures-six-jackets-graph.json','n01-W033-six-jackets-whole-static.json',
           'n01-W033-six-jackets-whole-sampled36.json','n01-FR-outboard-row-sampled36.json']
    pins={};reports=[]
    for name in names:
        f=OUT/name;r=json.loads(f.read_text());reports.append(r)
        for p,h in r['source_sha256'].items():
            assert sha(ROOT/p)==h,p
            assert p not in pins or pins[p]==h,p
            pins[p]=h
        pins[f.relative_to(ROOT).as_posix()]=sha(f)
    graph,raw,motion,rowmotion=reports
    assert whole==raw['parts'] and not raw['errors']
    assert graph['all_six_current_middle_jackets_checked']
    for r in (motion,rowmotion):assert r['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert set(motion['completed'])=={'CurrentWhole:W033','Station:Bank:W033/body/end:split_cap_exterior'}
    assert ft.min_radius(whole)>=12.4 and self_conflict(whole,[None]*len(whole))[0]>=.2
    assert shape.isValid() and len(shape.Solids)==1
    checks={};wiremeta={'kind':'actual_wire'};owncap='Station:Bank:W033/body/end:split_cap_exterior'
    terminal='Ref_Material_F_R2_CP2_OUT_0_0';short='VerticalCuff:W035/body/start'
    for name,r in raw['checks'].items():
        minimum=0 if name==terminal else .15 if name==owncap else pair_spacing('CurrentWhole:W033',wiremeta,name,metadata.get(name,{}))
        gap=shape.distToShape(scene[name])[0] if name==short else r['gap_mm']
        row=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
        if name==terminal:
            row['common_mm3']=shape.common(scene[name]).Volume;row['ok'] &= row['common_mm3']<1e-7
        checks['whole / '+name]=row
    assert cap.isValid() and len(cap.Solids)==1 and cap.cut(oldcap).Volume<1e-7
    assert cap.common(shape).Volume<1e-7
    # New groove must be checked in its own orientation, not inherit right-exit receipt.
    for name,target in scene.items():
        if name==owncap:continue
        if name in ('Station:Bank:W033/body/end:band_budget','Station:Bank:W033/body/end:head_budget'):
            oldgap=oldcap.distToShape(target)[0];gap=cap.distToShape(target)[0]
            oldcommon=oldcap.common(target).Volume;common=cap.common(target).Volume
            checks['cap / '+name]=dict(gap_mm=gap,old_gap_mm=oldgap,common_mm3=common,old_common_mm3=oldcommon,
                retained_owned_external_tie_interface=True,ok=gap>=oldgap-1e-6 and common<=oldcommon+1e-7)
            continue
        if bbox_lower_bound(cap.BoundBox,target.BoundBox)>=1.25+(metadata.get(name,{}).get('nominal_profile_radius_mm') or 0)+1e-6:continue
        t=solid_profile_target(target,metadata.get(name,{}));gap=cap.distToShape(t)[0]
        minimum=0 if name==terminal else 1.25
        row=dict(gap_mm=gap,minimum_mm=minimum,ok=gap>=minimum-1e-6)
        if name==terminal:row['common_mm3']=cap.common(t).Volume;row['ok'] &= row['common_mm3']<1e-7
        checks['cap / '+name]=row
    R=12.4;b=np.array([-1.,0.,-1.])/math.sqrt(2);side=np.array([1.,0.,-1.])/math.sqrt(2)
    probes=[]
    for length in np.linspace(.25,8.75,35):
        centre=np.array([-18.,-17.152,69.])+[0,min(length,3),0]
        if length>3:
            angle=(length-3)/R;centre+=np.array([0,R*math.sin(angle),0])+R*(1-math.cos(angle))*b
        for sign in (-1,1):
            for radial in (1.2,1.8,2.4):probes.append(cap.isInside(A.Vector(*(centre+sign*radial*side)),1e-7,True))
    assert all(probes)
    checks['BUS_valid_original']=dict(gap_mm=bus_gap,minimum_mm=1.25,ok=bus_gap>=1.25)
    failures={k:v for k,v in checks.items() if not v['ok']};assert not failures,failures
    out=outer_margin(shape,outer);assert out['ok']
    payload={'CurrentWhole:W033':shape,owncap:cap}
    for wire,parts in row_recipes.items():
        assert parts[0]['length']==9
        payload['VerticalCuff:'+wire+'/body/start']=solid(parts,1)
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest()))
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    result=dict(status='W033_JOINT_DEPARTURE_GEOMETRY_RECEIVED_NOT_SELECTED_FULL_PLAN',whole_recipe=whole,
        whole_length_mm=ft.length(whole),row_recipes=row_recipes,bank_recipe=bank_recipe,checks=checks,outer=out,
        grip_first9_probes=len(probes),grip_first9_probes_inside=all(probes),old_cap_external_envelope_retained=True,
        W035_optional_tail_removed_not_mandatory_grip_or_factory_wire_cut=True,
        changed_source_boundary_binding_W031_W033_W035_OPEN=True,W031_W035_continuations_OPEN=True,
        root_assembly_tool_compression_full_factory_and_N01_OPEN=True,selected=False,N01_complete=False,physical_pass=False,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['whole_length_mm'],result['worker_seconds'],flush=True)
    return result
