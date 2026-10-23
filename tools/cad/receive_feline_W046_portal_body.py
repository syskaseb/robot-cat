"""Short W046 with unchanged ends and a subset-only shared printed portal.

Receives a planning portion, not structural strength, manufacture or N01.
The original W045 channel and all selected purchased parts stay unchanged.
"""
import hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_channelled_foundation import bearing_area
from receive_feline_W024_shared_body import solid
from refresh_feline_power_space import same_geometry
from plan_feline_usb_service_bight import outer_margin
from solve_feline_W047_simple_graph import self_conflict
import feline_tangent_routes as ft

PORTAL=('CurrentFoundation:ClampSeat:4','CurrentFoundation:BankPier:4')
START='Station:RL_P:wire:RL_P.2'
END='Station:Bank:W046/single/end:wire:W046/single/end'
MATES={'Ref_Material_F_L4_CP2_IN_0_0':0.,'Station:RL_P:case':0.,
       'Station:RL_P:split_common_comb':.15,
       'Station:Bank:W046/single/end:split_cap_exterior':.15}

def equivalent_solid(a,b):
    # Cylinder vs swept-circle constructors need not serialize identical BReps.
    assert a.isValid() and b.isValid() and len(a.Solids)==len(b.Solids)==1
    return abs(a.Volume-b.Volume)<1e-5 and a.cut(b).Volume+b.cut(a).Volume<1e-5

def receive(scene,rows,middle,portal,raw,own_mates,motion,outer,source_files,tested_whole):
    tick=time.monotonic();dest=OUT/'n01-W046-original-prefix-portal-body.json'
    assert not dest.exists() and not raw['errors']
    byid={e['id']:e for e in rows};a=byid['W046/single/start'];b=byid['W046/single/end']
    source=[ft.line(a['point_mm'],a['routing_exit_mm'])]
    land=ft.add(b['point_mm'],ft.mul(b['departure_axis'],9))
    bank=[ft.line(b['point_mm'],land),ft.arc(land,b['departure_axis'],b['routing_exit_mm'])]
    assert equivalent_solid(solid(source,1.55),scene[START])
    assert equivalent_solid(solid(bank,1.55),scene[END])
    parts=source+middle+[ft.reverse(s) for s in reversed(bank)]
    assert ft.min_radius(parts)>=12.4-1e-7
    self_gap,_=self_conflict(parts,[None]*len(parts),1.55);assert self_gap>=.2
    whole=solid(parts,1.55);assert whole.isValid() and len(whole.Solids)==1
    assert equivalent_solid(whole,tested_whole)
    out=outer_margin(whole,outer);assert out['ok']
    checks=dict(raw['checks'])
    for name,margin in MATES.items():
        row=own_mates[name];assert row['common_mm3']<1e-7
        assert row['direct_middle_gap_mm']>=1.25 and row['gap_mm']>=margin-1e-6
        checks['CurrentWhole:W046|'+name]=dict(row,minimum_mm=margin,ok=True,
            basis='UNCHANGED_ORIGINAL_END_AND_NO_NEW_MIDDLE_CONTACT')
    assert all(c['ok'] for c in checks.values())
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert motion['completed']==['CurrentWhole:W046'] and all(c['ok'] for c in motion['checks'].values())
    structure={};clearance=solid(middle,2.8)
    for name in PORTAL:
        old=scene[name];new=portal[name]
        assert new.isValid() and len(new.Solids)==1 and new.cut(old).Volume<1e-5
        assert same_geometry(new,old.cut(clearance))
        structure[name]=dict(subset_only=True,removed_mm3=old.Volume-new.Volume,
            parent_brep_sha256=hashlib.sha256(old.exportBrepToString().encode()).hexdigest())
    joint=portal[PORTAL[0]].common(portal[PORTAL[1]]).Volume
    assert joint>300 and len(portal[PORTAL[0]].fuse(portal[PORTAL[1]]).Solids)==1
    bearings={}
    for role,name,top,minimum in (('pad','Station:Anchor:Rear:TopClampPad4',True,60),
                                 ('washer','Station:Anchor:Rear:RailClamp4TopWasher',False,10)):
        mate=scene[name];z=mate.BoundBox.ZMax if top else mate.BoundBox.ZMin
        old=bearing_area(scene[PORTAL[0]],mate,z);new=bearing_area(portal[PORTAL[0]],mate,z)
        assert abs(old-new)<1e-5 and new>=minimum
        bearings[role]=dict(before_mm2=old,after_mm2=new)
    # Subset proof preserves prior external and sampled-motion clearances for
    # the printed parts. Actual bearing and connectivity checks are above.
    payload={**portal,'CurrentMiddle:W046':solid(middle,1.55)}
    archive=dest.with_suffix('.breps.zip');geometry=[]
    recovering_archive=archive.exists()
    with zipfile.ZipFile(archive,'r' if recovering_archive else 'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep'
            if recovering_archive:assert z.read(entry)==data,'Existing partial archive differs'
            else:z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),
                kind='actual_wire' if name.startswith('CurrentMiddle:') else 'PETG',
                nominal_profile_radius_mm=1.55 if name.startswith('CurrentMiddle:') else None))
    pins={}
    for f in source_files:
        p=Path(f)
        if not p.exists() and p.parent==ROOT:p=OUT/p.name
        assert p.exists(),p
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    for f in (Path(__file__),OUT/'n01-W046-original-prefix-portal-motion.json',
              OUT/'n01-E2-four-factory-critical-space.json',ROOT/json.loads((OUT/'n01-E2-four-factory-critical-space.json').read_text())['bundle']):
        pins[f.relative_to(ROOT).as_posix()]=sha(f)
    updates={e['id']:dict(full_middle_route_accepted=True,whole_portion_received=True,
        whole_portion_receipt=dest.relative_to(ROOT).as_posix(),current_complete_middle_owner='CurrentMiddle:W046',
        whole_body_length_mm=ft.length(parts),stock_cutting_and_native_mounts_OPEN=True) for e in (a,b)}
    result=dict(status='W046_UNCHANGED_ENDS_SHARED_PORTAL_COMPLETE_PORTION_NOT_N01',portion='W046/single',
        updates=updates,middle_recipe=dict(parts=middle,radius_mm=1.55,length_mm=ft.length(middle)),
        whole_recipe=parts,complete_body_length_mm=ft.length(parts),minimum_R_mm=ft.min_radius(parts),
        self_gap_lower_mm=self_gap,checks=checks,outer=out,scene_actors=len(scene),
        original_ends_and_W045_unchanged=True,portal_subset_proof=structure,portal_joint_mm3=joint,bearings=bearings,
        factory_XP03_metadata_basis='Archive SHA plus same_geometry; actual insulated wire, not rigid component',
        motion_receipt=(OUT/'n01-W046-original-prefix-portal-motion.json').relative_to(ROOT).as_posix(),
        sampled36_NOT_continuous_motion=True,portal_motion_inherited_by_subset=True,
        roots_assembly_strength_native_and_full_N01_OPEN=True,N01_complete=False,physical_pass=False,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);return result

def current():
    from compose_feline_FR_joint_boundaries import current as parent
    from compose_feline_integrated_boundaries import apply_updates
    base,rows,files=parent();path=OUT/'n01-W046-original-prefix-portal-body.json';r=json.loads(path.read_text())
    assert r['status']=='W046_UNCHANGED_ENDS_SHARED_PORTAL_COMPLETE_PORTION_NOT_N01'
    assert all(c['ok'] for c in r['checks'].values()) and r['outer']['ok']
    assert sha(ROOT/r['bundle'])==r['bundle_sha256']
    for f,h in r['source_sha256'].items():assert sha(ROOT/f)==h,f
    return base,apply_updates(rows,r['updates']),(*files,path)
