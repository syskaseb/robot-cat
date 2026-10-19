"""One current planning packet from an ACTUALLY received complete selection.

Not N03 native manufacture, final middle routing or a physical qualification.
Never compose an arbitrary last trial or an obsolete selected FCStd as current.
"""
import hashlib
import json
import time
import sys
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_t18i_two_lane import unit
from feline_station_zone_domains import materialise
from feline_ato_service import receive as receive_service
from feline_two_lane_receive import world_context
from feline_flat_station_templates import build
from feline_zone_station_templates import zone_build,vertical_build
from feline_underplate_station_templates import build_underplate
from feline_remaining_kits import materialise as remaining_material
from feline_bank_exit_lanes import materialise as bank_material
from feline_bank_exit_lanes import under_key_materialise
from feline_compact_station_fan import unit as compact_unit
from feline_compact_station_fan import legacy_unit
from feline_compact_station_fan import rise_unit
from feline_compact_after_land import unit as after_land_unit
from feline_above_hardware_grip import unit as above_unit
from feline_bank_receiving_grips import both_after_materialise
from feline_bank_zoned_layout import materialise as zoned_materialise
from feline_bank_selected_t18i import materialise as selected_bank_materialise

COMPLETE='WHOLE20_MONITOR_SIX_FANS_FULL_UNITS_STATIC_MUTUAL_RECEIVED_CORRIDORS_ROOTS_TOOLS_OPEN'
COMPLETE54='WHOLE54_FULL_UNITS_STATIC_MUTUAL_RECEIVED_ROOTS_CORRIDORS_TOOLS_OPEN'


def station_lands(station,model):
    result=[]
    bywire={p['wire']:p for p in station['ports']}
    for w in model['wires']+model.get('reused_jacket_lands',[]):
        port=bywire[w['wire']];q=np.asarray(w['point_mm']);d=np.asarray(w['departure_axis'])
        start=np.asarray(w.get('grip_start_mm',q));grip_axis=np.asarray(w.get('grip_axis',d));tip=start+9*grip_axis
        result.append(dict(endpoint=w.get('endpoint',port['endpoint']),wire=w['wire'],
            point_mm=q.tolist(),departure_axis=d.tolist(),radius_mm=w.get('radius_mm',w.get('radius')),
            minimum_R_mm=port['minimum_project_R_mm'],grip_start_mm=start.tolist(),grip_end_mm=tip.tolist(),
            grip_axis=grip_axis.tolist(),received_prefix_R_mm=w.get('R_mm'),
            grip_length_mm=9,not_new_connector=bool(w.get('not_new_wire_geometry')),
            full_middle_route_accepted=False,supplier_datum_guaranteed=False))
    assert {r['endpoint'] for r in result}=={p['endpoint'] for p in station['ports']}
    return result


def station_model(st,choice):
    slot=choice['slot']
    if choice['kind']=='straight_comb':return unit(st,slot,choice.get('lane',0))
    if choice['kind']=='compact_fan':return compact_unit(st,choice)
    if choice['kind']=='after_land_fan':return after_land_unit(st,choice)
    if choice['kind']=='legacy_compact_fan':return legacy_unit(st,choice)
    if choice['kind']=='power_rise_fan':return rise_unit(st,choice)
    if choice['kind']=='above_hardware_fan':return above_unit(st,choice['recipe'])
    r=choice['recipe']
    if r['family']=='UNDER_PLATFORM_SHARED_REMOVABLE_COMBS':return build_underplate(st,slot,r['bend_side'],r['head_side'])
    if st['fixed_identity_pose']:return build(st,'inner',1,-1)
    if r['family']=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS':return vertical_build(st,slot,r['departure_z'],r['lever_sign'],r['head_side'])
    return zone_build(st,slot,r['departure'],r['bend_mode'])


def chosen_material(path=None):
    path=path or OUT/'n01-two-lane-comb-joint.json'
    joint=json.loads(path.read_text())
    assert ((joint['status']==COMPLETE and len(joint['chosen'])==27) or
            (joint['status']==COMPLETE54 and len(joint['chosen'])==54))
    for n,h in joint['source_sha256'].items():assert sha(ROOT/n)==h,n
    stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
    fanpath=OUT/'n01-six-source-shared-lanes.json';_,fans,fanrows=packed(fanpath)
    parts={};rows={};models={}
    for group,r in joint['chosen'].items():
        if r['kind']=='straight_comb':
            model=station_model(stations[group],r);models[group]=dict(wires=station_lands(stations[group],model))
            pp=model['parts'];kk={n:'proposal_wire' if n.startswith('wire:') else 'project_stock_reservation' if 'budget' in n else 'proposal_material' for n in pp}
        elif r['kind']=='received_legacy_unit':
            pp,kk=materialise(stations[group],r['slot'],r['recipe'])
            st=stations[group];m=station_model(st,r)
            models[group]=dict(wires=station_lands(st,m))
        elif r['kind']=='remaining_kit':
            pp,kk=remaining_material(group,r['recipe'])
        elif r['kind']=='bank_exit_lane':
            pp,kk=bank_material(group,r['recipe'])
        elif r['kind']=='bank_under_key_lane':
            pp,kk=under_key_materialise(group,r['recipe'])
        elif r['kind']=='bank_both_after':
            pp,kk=both_after_materialise(group,r['recipe'])
        elif r['kind']=='bank_zoned_after':
            pp,kk=zoned_materialise(group,r['recipe'])
        elif r['kind']=='bank_selected_t18i':
            pp,kk=selected_bank_materialise(group,r['recipe'])
        elif r['kind'] in ('compact_fan','after_land_fan','legacy_compact_fan','power_rise_fan','above_hardware_fan'):
            model=station_model(stations[group],r);pp,kk=model['parts'],model['kinds']
            models[group]=dict(wires=station_lands(stations[group],model))
        elif r['kind']=='source_fan':
            pp={p['name']:fans[p['name']] for p in r['option']['parts']}
            kk={n:fanrows[n]['kind'] for n in pp}
        else:
            assert r['kind']=='monitor'
            slot=r['slot'];c=np.asarray(slot['centre_mm']);d=np.asarray(slot['dimensions_mm'])
            lo,hi=np.asarray(slot.get('bounds_mm',[c-d/2,c+d/2]))
            pp={'case':Part.makeBox(*(hi-lo),A.Vector(*lo))};kk={'case':'purchased_case_planning_envelope'}
        for n,s in pp.items():
            name=n if r['kind']=='source_fan' else 'Station:'+group+':'+n
            assert name not in parts and s.isValid() and s.Solids,name
            parts[name]=s;rows[name]=dict(name=name,group=group,kind=kk[n],source_choice_key=r['key'])
    return joint,parts,rows,models


def main():
    tick=time.monotonic();whole54='--whole54' in sys.argv;source=OUT/('n01-shared54-whole.json' if whole54 else 'n01-two-lane-comb-joint.json')
    joint,proposal,rows,models=chosen_material(source)
    world,fixed=world_context()
    assert not set(proposal)&set(fixed),'No proposal may overwrite a preserved owner'
    service,tools=receive_service(world,fixed,proposal)
    dest=OUT/('n01-shared54-current.json' if whole54 else 'n01-shared-plan-current.json');archive=dest.with_suffix('.breps.zip')
    records=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for n,s in {**proposal,**tools}.items():
            raw=s.exportBrepToString().encode();entry=f'{len(records):04d}.brep';z.writestr(entry,raw)
            records.append(dict(rows.get(n,dict(name=n,group='ATO_service',kind='project_access_reservation')),
                                entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    result=dict(status='CURRENT_SHARED54_FULL_UNITS_AND_ATO_RECEIVED_ROOTS_CORRIDORS_OPEN' if whole54 else 'CURRENT_SHARED27_FULL_UNITS_AND_ATO_RECEIVED_REMAINDER_OPEN',
        selected=False,N01_complete=False,physical_pass=False,
        source_sha256={**joint['source_sha256'],source.relative_to(ROOT).as_posix():sha(source),
                       Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
                       'tools/cad/feline_ato_service.py':sha(ROOT/'tools/cad/feline_ato_service.py')},
        world_source_sha256=world.pins,chosen=joint['chosen'],parts=records,
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        ATO_service=service,all12_ATO_reservations_clear=all(r['all_reservations_clear'] for r in service),
        current_station_wire_ends={n:m['wires'] for n,m in models.items()},
        current_occupied_station_end_count=sum(len(m['wires']) for m in models.values()),
        open=([] if whole54 else ['24bank source kits+2full anchor kits+selected F_PWM'])+[
              'All roots/case retention and installation tool interfaces',
              'All123portions246ends/Rcorridors/factorylength capacity; conditional monitor balance separately'],
        worker_seconds=round(time.monotonic()-tick,3))
    temp=dest.with_suffix('.writing.json');temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(dest)
    print(json.dumps(dict(status=result['status'],ATO_clear=sum(r['all_reservations_clear'] for r in service),
                         blockers={r['name']:r['reservation_blockers'] for r in service if r['reservation_blockers']},
                         seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
