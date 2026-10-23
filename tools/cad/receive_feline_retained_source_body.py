"""Reusable receiver for a retained source and changed left/down bank exit."""
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
from check_feline_retained_bank_channel import check as check_channel
from solve_feline_W047_simple_graph import self_conflict
import feline_tangent_routes as ft


def receive(wire,parts,source_count,bank,cap,scene,metadata,rows,outer,bus_gap,graph_name,static_name,motion_name,terminal,owned_guide):
    tick=time.monotonic();dest=OUT/f'n01-current-{wire}-retained-source-body-plan.json';assert not dest.exists()
    pins={};reports=[]
    for name in (graph_name,static_name,motion_name):
        p=OUT/name;r=json.loads(p.read_text());reports.append(r)
        for path,h in r['source_sha256'].items():assert sha(ROOT/path)==h,path;pins[path]=h
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    graph,raw,motion=reports;owner='Station:Bank:'+wire+'/body/end:';source_owner='VerticalCuff:'+wire+'/body/start'
    assert parts==raw['parts'] and not raw['errors']
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' and all(c['ok'] for c in motion['checks'].values())
    assert set(motion['completed'])=={'CurrentWhole:'+wire,owner+'split_cap_exterior'}
    middle=parts[source_count:-len(bank)];source=parts[:source_count]
    assert middle==graph['accepted']['parts']
    assert ft.min_radius(parts)>=12.4-1e-7 and self_conflict(parts,[None]*len(parts))[0]>=.2
    shape=solid(parts,1);assert shape.isValid() and len(shape.Solids)==1
    assert same_geometry(solid(source,1),scene[source_owner])
    assert same_geometry(cap,scene[owner+'split_cap_exterior'].cut(solid(bank,1.15)))
    out=outer_margin(shape,outer);assert out['ok'] and bus_gap>=1.25
    byid={e['id']:e for e in rows};start=byid[wire+'/body/start'];end=byid[wire+'/body/end']
    assert np.allclose(source[-1]['end'],start['routing_exit_mm'],atol=1e-6,rtol=0)
    assert np.allclose(bank[0]['start'],end['point_mm'],atol=1e-6,rtol=0)
    channel=check_channel(wire,cap,scene[owner+'split_cap_exterior'],shape,scene,metadata,end['point_mm'],terminal)
    checks={}
    for name,c in raw['checks'].items():
        minimum=0 if name==terminal else .15 if name in (owner+'split_cap_exterior',owned_guide) else pair_spacing('CurrentWhole:'+wire,{'kind':'actual_wire'},name,metadata.get(name,{}))
        row=dict(c,minimum_mm=minimum,ok=c['gap_mm']>=minimum-1e-6)
        if name==terminal:row['common_mm3']=shape.common(scene[name]).Volume;row['ok'] &= row['common_mm3']<1e-7
        checks[name]=row
    assert all(c['ok'] for c in checks.values()),{k:v for k,v in checks.items() if not v['ok']}
    updates={wire+'/body/'+side:dict(full_middle_route_accepted=True,whole_portion_received=True,
        current_complete_middle_owner='CurrentMiddle:'+wire,whole_portion_receipt=dest.relative_to(ROOT).as_posix(),
        whole_body_length_mm=ft.length(parts),whole_factory900_and_moving_portion_NOT_received=True) for side in ('start','end')}
    updates[wire+'/body/end'].update(routing_exit_mm=bank[-1]['end'],routing_exit_axis=bank[-1]['end_tangent'],
        source_prefix_length_mm=ft.length(bank),jacket_grip9_mm=None,grip_axis=None,grip_length_mm=9,
        full_grip_arclength_mm=[0,9],curved_grip_prefix=bank,initial_jacket_land_mm=3,source_first9_unchanged=False,
        old_straight_grip_geometry_invalidated=True,prefix_geometry_owner=owner+'wire:'+wire+'/body/end')
    payload={'CurrentMiddle:'+wire:solid(middle,1),owner+'wire:'+wire+'/body/end':solid(bank,1),owner+'split_cap_exterior':cap}
    archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            data=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,data)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(data).hexdigest(),kind='PETG' if name.endswith('split_cap_exterior') else 'actual_wire'))
    for f in (Path(__file__),Path(__file__).with_name('check_feline_retained_bank_channel.py')):pins[f.relative_to(ROOT).as_posix()]=sha(f)
    result=dict(status='RETAINED_SOURCE_CHANGED_BANK_COMPLETE_BODY_RECEIVED_NOT_N01',wire=wire,updates=updates,
        middle_recipe=dict(parts=middle,radius_mm=1,length_mm=ft.length(middle)),complete_body_length_mm=ft.length(parts),
        source_geometry_unchanged=True,checks=checks,outer=out,valid_original_BUS_gap_mm=bus_gap,channel=channel,
        sampled36_NOT_continuous_motion=True,root_assembly_compression_and_full_factory_lengths_OPEN=True,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],wire,result['complete_body_length_mm'],result['worker_seconds'],flush=True);return result
