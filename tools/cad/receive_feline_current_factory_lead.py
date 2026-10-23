"""Reconcile the retained W043 centreline with its selected OD4 profile."""
import hashlib,json,math,time,zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_n01_shared import pipe
from plan_feline_usb_service_bight import outer_margin
from receive_feline_W046_portal_body import equivalent_solid
from feline_selected_piece_contract import load as selected_load
from feline_solid_distance import bbox_lower_bound

CAP='Station:P_SYS:common_channelled_cap_exterior'
MATES={'Ref_Material_F_PI_new_0_0':0.,'Station:P_SYS:case':0.,CAP:.15,
       'FPIJoint:F_PI.in:pad':.15,'FPIJoint:F_PI.in:band':.15}

def receive(scene,rows,recipe,wire,cap,raw,own,motion,outer,source_files):
    tick=time.monotonic();dest=OUT/'n01-W043-selected-profile-complete-lead.json'
    assert not dest.exists() and not raw['errors']
    contract,cf=selected_load();selected=contract['portions']['W043/single']
    assert selected['project_radius_mm']==2 and selected['minimum_project_R_mm']==6
    assert min(p['radius_mm'] for p in recipe['parts'] if p['kind']=='arc')>=6
    assert equivalent_solid(wire,pipe(recipe['parts'],2))
    length=sum(p['length_mm'] for p in recipe['parts'])
    assert abs(length-recipe['length_mm'])<1e-6
    assert length+recipe['strip_mm']<=50
    assert abs(wire.Volume-math.pi*4*length)<1e-4
    endpoints=[next(e for e in rows if e['id']=='W043/single/'+side) for side in ('start','end')]
    assert math.dist(recipe['parts'][0]['start'],endpoints[0]['point_mm'])<1e-6
    assert math.dist(recipe['parts'][-1]['end'],endpoints[1]['point_mm'])<1e-6
    assert cap.isValid() and len(cap.Solids)==1 and cap.cut(scene[CAP]).Volume<1e-5
    assert equivalent_solid(cap,scene[CAP].cut(pipe(recipe['parts'],2.15)))
    checks=dict(raw['checks'])
    for name,minimum in MATES.items():
        c=dict(own[name])
        if name==CAP:c.update(gap_mm=wire.distToShape(cap)[0],common_mm3=wire.common(cap).Volume)
        assert c['gap_mm']>=minimum-1e-6 and c['common_mm3']<1e-7
        checks['W043|'+name]=dict(c,minimum_mm=minimum,ok=True,intended_own_terminal_or_relief=True)
    assert all(c['ok'] for c in checks.values())
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' and motion['completed']==['W043']
    assert all(c['ok'] for c in motion['checks'].values())
    out=outer_margin(wire,outer);assert out['ok']
    # Check the subset cut does not touch any existing closure band or root
    # interface which actually contacts the old cap. No new contacts possible.
    removed=scene[CAP].cut(cap);joints={}
    for name,target in scene.items():
        if name==CAP or name=='W043' or not target.Solids:continue
        if bbox_lower_bound(removed.BoundBox,target.BoundBox)>1e-6:continue
        cut_common=removed.common(target).Volume
        assert cut_common<1e-5,(name,cut_common)
        joints[name]=dict(removed_material_common_mm3=cut_common)
    payload={'W043':wire,CAP:cap};archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),
                kind='actual_wire' if name=='W043' else 'PETG',nominal_profile_radius_mm=2 if name=='W043' else None))
    pins={}
    for f in (*source_files,cf,OUT/'n01-central-spine-power-plan-r4.json',Path(__file__),OUT/'n01-W043-current-selected-profile-motion.json'):
        p=Path(f)
        if not p.exists() and p.parent==ROOT:p=OUT/p.name
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    updates={e['id']:dict(full_middle_route_accepted=True,whole_portion_received=True,
        current_complete_middle_owner='W043',whole_body_length_mm=length,
        whole_portion_receipt=dest.relative_to(ROOT).as_posix(),source_nominal_profile_radius_mm=2,
        service_native_stock_and_delivery_fit_OPEN=True) for e in endpoints}
    result=dict(status='W043_SELECTED_PROFILE_COMPLETE_LEAD_STATIC36_NOT_SERVICE_OR_N01',updates=updates,
        selected_piece=selected,whole_recipe=recipe,complete_body_length_mm=length,nominal_cut_including_strip_mm=length+12,
        old_profile_radius_mm=1.7,current_profile_radius_mm=2,centreline_and_parts_unchanged=True,
        checks=checks,outer=out,cap_subset_removed_mm3=removed.Volume,cap_existing_interface_checks=joints,
        motion_receipt=(OUT/'n01-W043-current-selected-profile-motion.json').relative_to(ROOT).as_posix(),
        sampled36_NOT_continuous_motion=True,cap_clearance_inherited_by_subset=True,
        service_and_root_assembly_OPEN=True,N01_complete=False,physical_pass=False,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);return result

def current():
    from receive_feline_W046_portal_body import current as parent
    from compose_feline_integrated_boundaries import apply_updates
    base,rows,files=parent();path=OUT/'n01-W043-selected-profile-complete-lead.json';r=json.loads(path.read_text())
    assert r['status']=='W043_SELECTED_PROFILE_COMPLETE_LEAD_STATIC36_NOT_SERVICE_OR_N01'
    assert all(c['ok'] for c in r['checks'].values()) and sha(ROOT/r['bundle'])==r['bundle_sha256']
    for f,h in r['source_sha256'].items():assert sha(ROOT/f)==h,f
    return base,apply_updates(rows,r['updates']),(*files,path)
