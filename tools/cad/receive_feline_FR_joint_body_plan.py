"""One common two-wire plan, with the original W035 departure retained."""
import hashlib,json,time,zipfile
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import pair_spacing
from receive_feline_W024_shared_body import solid
from refresh_feline_power_space import same_geometry
from plan_feline_usb_service_bight import outer_margin
from solve_feline_W047_simple_graph import self_conflict
import feline_tangent_routes as ft


def receive(scene,metadata,rows,whole_recipes,bank_recipes,caps,outer,bus_gaps):
    tick=time.monotonic();dest=OUT/'n01-FR-W031-W033-common-body-plan.json';assert not dest.exists()
    names=['n01-W033-joint-departures-received.json','n01-W031-changed-pair-seven-jackets-graph.json',
        'n01-W031-seven-jackets-whole-static.json','n01-W031-seven-jackets-whole-sampled36.json',
        'n01-W031-left-channel-checked.json','n01-FR-outboard-row-W031-static.json','n01-FR-outboard-row-sampled36.json']
    reports={};pins={}
    for name in names:
        p=OUT/name;r=json.loads(p.read_text());reports[name]=r
        for path,h in r['source_sha256'].items():
            assert sha(ROOT/path)==h,path
            assert path not in pins or pins[path]==h,path
            pins[path]=h
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    prior=reports[names[0]];raw=reports[names[2]];motion=reports[names[3]];channel=reports[names[4]]['channel']
    assert not raw['errors'] and motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert set(motion['completed'])=={'CurrentWhole:W031','Station:Bank:W031/body/end:split_cap_exterior'}
    assert all(c['ok'] for c in channel['checks'].values()) and channel['probes_inside']
    assert all(c['ok'] for c in prior['checks'].values())
    checks={};payload={};updates={};recipes={};byid={r['id']:r for r in rows}
    for wire in ('W031','W033'):
        parts=whole_recipes[wire];shape=solid(parts,1);start=parts[:2];bank=bank_recipes[wire];middle=parts[2:-2]
        assert shape.isValid() and len(shape.Solids)==1
        assert ft.min_radius(parts)>=12.4-1e-7 and self_conflict(parts,[None]*len(parts))[0]>=.2
        assert np.allclose(parts[0]['start'],byid[wire+'/body/start']['point_mm'],atol=1e-7,rtol=0)
        assert np.allclose(parts[-1]['end'],byid[wire+'/body/end']['point_mm'],atol=1e-7,rtol=0)
        assert outer_margin(shape,outer)['ok'] and bus_gaps[wire]>=1.25
        assert same_geometry(shape,solid(start+middle+[ft.reverse(s) for s in reversed(bank)],1))
        recipes[wire]=dict(parts=middle,radius_mm=1,length_mm=ft.length(middle),complete_body_length_mm=ft.length(parts))
        payload['CurrentMiddle:'+wire]=solid(middle,1)
        payload['VerticalCuff:'+wire+'/body/start']=solid(start,1)
        owner='Station:Bank:'+wire+'/body/end:'
        payload[owner+'wire:'+wire+'/body/end']=solid(bank,1);payload[owner+'split_cap_exterior']=caps[wire]
        for side,prefix,actor in [('start',start,'VerticalCuff:'+wire+'/body/start'),('end',bank,owner+'wire:'+wire+'/body/end')]:
            last=prefix[-1]
            updates[wire+'/body/'+side]=dict(routing_exit_mm=last['end'],routing_exit_axis=last['end_tangent'],
                source_prefix_length_mm=ft.length(prefix),prefix_geometry_owner=actor,
                full_middle_route_accepted=True,whole_portion_received=True,current_complete_middle_owner='CurrentMiddle:'+wire,
                whole_portion_receipt=dest.relative_to(ROOT).as_posix(),whole_body_length_mm=ft.length(parts),
                whole_factory900_and_moving_portion_NOT_received=True,complete_individual_termination_relief_NOT_inferred=True)
            if side=='end':updates[wire+'/body/'+side].update(jacket_grip9_mm=None,grip_axis=None,
                grip_length_mm=9,full_grip_arclength_mm=[0,9],curved_grip_prefix=prefix,initial_jacket_land_mm=3,
                source_first9_unchanged=False,old_straight_grip_geometry_invalidated=True)
    assert whole_recipes['W031']==raw['parts'] and whole_recipes['W033']==prior['whole_recipe']
    for name,c in raw['checks'].items():
        minimum=0 if name=='Ref_Material_F_R1_CP2_OUT_0_0' else .15 if name=='VerticalGuide:FR' else pair_spacing('CurrentWhole:W031',{'kind':'actual_wire'},name,metadata.get(name,{}))
        row=dict(c,minimum_mm=minimum,ok=c['gap_mm']>=minimum-1e-6)
        if minimum==0:
            row['common_mm3']=solid(whole_recipes['W031'],1).common(scene[name]).Volume;row['ok'] &= row['common_mm3']<1e-7
        checks[name]=row
    original35=scene['VerticalCuff:W035/body/start']
    for wire in ('W031','W033'):
        gap=solid(whole_recipes[wire],1).distToShape(original35)[0]
        checks[wire+' / ORIGINAL_W035']=dict(gap_mm=gap,minimum_mm=.2,ok=gap>=.2-1e-6)
    assert all(c['ok'] for c in checks.values()),{k:v for k,v in checks.items() if not v['ok']}
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),kind='actual_wire' if name.startswith(('CurrentMiddle:','VerticalCuff:')) or ':wire:' in name else 'PETG'))
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    result=dict(status='FR_TWO_COMPLETE_BODY_CURVES_CURRENT_BOUNDARIES_RECEIVED_NOT_N01',updates=updates,middle_recipes=recipes,
        checks=checks,W035_original_source_retained=True,current_246_identities_preserved=True,selected_SKUs_changed=False,
        sampled36_NOT_continuous_motion=True,root_assembly_compression_and_full_factory_lengths_OPEN=True,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],{w:r['complete_body_length_mm'] for w,r in recipes.items()},result['worker_seconds'],flush=True)
    return result
