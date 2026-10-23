"""Receive W049 between retained XA02 and W057; no module relocation."""
import hashlib,json,math,time,zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from receive_feline_W024_shared_body import solid
from receive_feline_W046_portal_body import equivalent_solid
from plan_feline_usb_service_bight import outer_margin
from solve_feline_W047_simple_graph import self_conflict
import feline_tangent_routes as ft

END='Station:Bank:W049/body/end:wire:W049/body/end'
MIDDLE='CurrentMiddle:W049'
DEST=OUT/'n01-W049-joint-corridor-received.json'
MATES={'Ref_Material_F_L5_CP2_OUT_0_0':0.,
       'Station:Bank:W049/body/end:split_cap_exterior':.15,'RLArcGuide':.15}

def receive(scene,rows,parts,raw,own,motion,outer,source_files,tested_whole,type_proofs):
    tick=time.monotonic()
    assert not DEST.exists() and not raw['errors']
    assert all(type_proofs.values()) and len(type_proofs)>=10
    source,middle=parts[:2],parts[2:4]
    bank=[ft.reverse(s) for s in reversed(parts[4:])]
    assert len(parts)==6 and bank[0]['kind']=='line'
    assert abs(bank[0]['length']-9)<1e-7
    a,b=[next(e for e in rows if e['id']=='W049/body/'+side) for side in ('start','end')]
    assert math.dist(parts[0]['start'],a['point_mm'])<1e-6
    assert math.dist(parts[-1]['end'],b['point_mm'])<1e-6
    assert math.dist(bank[0]['end'],ft.add(b['point_mm'],ft.mul(b['departure_axis'],9)))<1e-6
    assert equivalent_solid(solid(source,1),scene['RLArc:W049/body/start'])
    assert ft.min_radius(parts)>=12.4-1e-7
    self_gap,_=self_conflict(parts,[None]*len(parts),1);assert self_gap>=.2
    whole=solid(parts,1);assert equivalent_solid(whole,tested_whole)
    out=outer_margin(whole,outer);assert out['ok']
    checks=dict(raw['checks'])
    for name,minimum in MATES.items():
        c=own[name]
        assert c['common_mm3']<1e-7 and c['gap_mm']>=minimum-1e-6
        assert c['new_middle_gap_mm']>=1.25
        checks['W049whole|'+name]=dict(c,minimum_mm=minimum,ok=True,
            basis='UNCHANGED_OWN_MATE_AND_CLEAR_NEW_MIDDLE')
    assert all(c['ok'] for c in checks.values())
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert motion['completed']==['W049whole'] and all(c['ok'] for c in motion['checks'].values())
    archive=DEST.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,shape in ((MIDDLE,solid(middle,1)),(END,solid(bank,1))):
            assert shape.isValid() and len(shape.Solids)==1
            data=shape.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),
                kind='actual_wire',nominal_profile_radius_mm=1))
    pins={}
    for f in (*source_files,Path(__file__),OUT/'n01-W049-coupled-clearance-sampled36.json',
              OUT/'n01-RL9-common-arc-rooted-space.json',OUT/'n01-inboard-comb-XA02-joint-plan.json'):
        p=Path(f)
        if not p.exists() and p.parent==ROOT:p=OUT/p.name
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    updates={e['id']:dict(full_middle_route_accepted=True,whole_portion_received=True,
        current_complete_middle_owner=MIDDLE,whole_body_length_mm=ft.length(parts),
        whole_portion_receipt=DEST.relative_to(ROOT).as_posix(),
        factory_moving_native_stock_OPEN=True) for e in (a,b)}
    updates[b['id']].update(routing_exit_mm=bank[-1]['end'],routing_exit_axis=bank[-1]['end_tangent'])
    result=dict(status='W049_JOINT_FIXED_NEIGHBOURS_COMPLETE_BODY_NOT_N01',updates=updates,
        whole_recipe=parts,middle_recipe=middle,bank_recipe=bank,profile_radius_mm=1,
        complete_body_length_mm=ft.length(parts),minimum_R_mm=ft.min_radius(parts),self_gap_lower_mm=self_gap,
        checks=checks,outer=out,wire_type_geometry_proofs=type_proofs,
        XA02_W057_modules_source_grip_and_bank_first9_unchanged=True,
        sampled36_NOT_continuous_motion=True,motion_receipt='n01-W049-coupled-clearance-sampled36.json',
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        factory_moving_native_stock_OPEN=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(DEST,result);return result

def current():
    from receive_feline_current_factory_lead import current as parent
    from compose_feline_integrated_boundaries import apply_updates
    base,rows,files=parent();r=json.loads(DEST.read_text())
    assert r['status']=='W049_JOINT_FIXED_NEIGHBOURS_COMPLETE_BODY_NOT_N01'
    assert all(c['ok'] for c in r['checks'].values()) and r['outer']['ok']
    assert sha(ROOT/r['bundle'])==r['bundle_sha256']
    for f,h in r['source_sha256'].items():assert sha(ROOT/f)==h,f
    return base,apply_updates(rows,r['updates']),(*files,DEST)
