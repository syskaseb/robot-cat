"""Reconcile all246 identities with received current source poses.

Data preparation only. Explicit pending poses are not silently inherited.
Jacket boundaries remain distinct from solder pads and accounting ends.
No route/stock/N01 or manufacturer guarantee created by a coordinate update.
"""
import copy
import json
import math
import time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed


def pipe_mouth(shape,anchor):
    candidates=[]
    for f in shape.Faces:
        if type(f.Surface).__name__!='Plane':continue
        if len(f.Edges)!=1 or type(f.Edges[0].Curve).__name__!='Circle':continue
        q=f.Edges[0].Curve.Center;d=-f.normalAt(0,0);d.normalize()
        if not shape.isInside(q+d*.1,1e-6,True):continue
        candidates.append(dict(point_mm=list(q),departure_axis=list(d),gap_to_owned_connector_mm=q.distanceToPoint(anchor.BoundBox.Center),face_radius_mm=f.Edges[0].Curve.Radius))
    assert len(candidates)==2,('Expected two saved pipe caps',len(candidates))
    candidates.sort(key=lambda r:r['gap_to_owned_connector_mm'])
    assert candidates[1]['gap_to_owned_connector_mm']-candidates[0]['gap_to_owned_connector_mm']>3,'Ambiguous owned pipe mouth'
    return candidates[0]


def main():
    tick=time.monotonic()
    files={k:OUT/n for k,n in dict(body='n01-current-endpoint-packet-r3.json',extra='n01-all-extra-interface-contract.json',
        core='n01-six-source-current-core.json',fans='n01-six-source-shared-lanes.json',
        supported='n01-supported-fore-layout.json',pwm='n01-pwm-board-shelf.json',
        source='n01-full-material-scene.json',modules='n01-module-plan-r5.json').items()}
    files['old_source_stock']=OUT.parent/'wiring-checkpoint/source-current-receipt.json'
    docs={k:json.loads(p.read_text()) for k,p in files.items()};rows=[]
    for e in docs['body']['endpoints']:
        r=copy.deepcopy(e);r.update(portion_id=e['id'].rsplit('/',1)[0],endpoint=e['role'],domain='body89')
        rows.append(r)
    for sec in docs['extra']['sections']:
        assert len(sec['ends'])==2
        for i,e in enumerate(sec['ends']):
            r=copy.deepcopy(e);r.update(id=sec['wire']+'/extra/'+('start' if i==0 else 'end'),portion_id=sec['wire']+'/extra',wire=sec['wire'],domain='extra34')
            rows.append(r)
    assert len(rows)==246 and len({r['id'] for r in rows})==246
    portions={}
    for r in rows:
        portions.setdefault(r['portion_id'],[]).append(r['id'])
        r['source_point_before_reconciliation_mm']=r.get('point_mm')
        r['pose_status']='RETAINED_OR_UNRESOLVED_NOT_CURRENT_POSE_APPROVAL'
        r.update(full_middle_route_accepted=False,stock_selected=False,supplier_datum_guaranteed=False)
        if r['group'].startswith('WAGO:'):r['pose_status']='PENDING_WHOLE_STATION_SELECTION'
    assert len(portions)==123 and all(len(v)==2 for v in portions.values())
    byid={r['id']:r for r in rows};changes=[]
    def update(r,point,direction,basis,**extra):
        assert len(point)==len(direction)==3 and abs(math.sqrt(sum(v*v for v in direction))-1)<1e-5
        r.update(point_mm=list(point),departure_axis=list(direction),pose_status='CURRENT_RECEIVED_PROJECT_DATUM',current_pose_basis=basis,**extra)
        changes.append(r['id'])
    for ref,options in docs['fans']['domains'].items():
        r=options[0];update(byid[ref],r['point_mm'],r['departure_axis'],'Current six-source saved barrel/mouth, same anchor in every retained fan; supplier fit remains delivery HOLD',
            minimum_R_mm=r['R_mm'],source_grip_options_count=len(options))
    for e in docs['core']['FR_accounting_boundary_changes']:
        update(byid[e['id']],e['point_mm'],e['departure_axis'],'Already current FR boundary; delta is audit metadata, NOT applied twice',
            matching_moving_boundary_requires_same_point=True,added_connector=False,grip_length_mm=9)
    delta=docs['supported']['MAIN_whole_changed_unit']['relative_translation_mm']
    for r in rows:
        if r['group']=='MAIN':update(r,[a+b for a,b in zip(r['point_mm'],delta)],r['departure_axis'],'Current whole MAIN relative translation with complete reversed stacks; old middle not inherited',grip_length_mm=12)
    for row in docs['core']['shared_fore_units']['F_HY_full_factory_ports']:
        for r in rows:
            if r['endpoint']=='F_HY.'+row['side']:
                update(r,row['mouth_mm'],row['axis'],'Current F_HY factory case mouth, not custom solder-joint end',
                    factory_external_nominal_mm=row['external_factory_mm'],factory_blank_provisional_mm=100,
                    factory_end_mm=row['factory_end_mm'],custom_grip9_mm=row['custom_grip9_mm'])
    # JPWM old contract and old case share the same already-world R5 frame.
    # Register their offset once to the current received case, not rawGUIDE.
    source=next(r for r in docs['modules']['groups'] if r['role']=='JPWM')
    oldcentre=[sum(v)/2 for v in zip(*source['candidate_bounds_mm'])]
    _,core,_=packed(files['core'])
    newcentre=list(core['Ref_Material_JPWM_0_0'].BoundBox.Center)
    for r in rows:
        if r['group']=='JPWM':update(r,[a+b-c for a,b,c in zip(r['point_mm'],newcentre,oldcentre)],r['departure_axis'],
            'Contract explicitly used module-plan-r5 candidate frame, NOT full-material-scene JPWM pose; transform once to current case',jacket_relief_and_middle_pending=True)
    jpwm=[r for r in rows if r['group']=='JPWM'];assert len(jpwm)==4
    assert all(abs(r['point_mm'][1]-newcentre[1])<1e-6 for r in jpwm)
    assert all(abs(abs(r['point_mm'][0]-newcentre[0])-15.3)<1e-5 for r in jpwm)
    pipe_receipts={};pipe_errors=[]
    roles={r['endpoint']:r for r in rows if r['group']=='Pi4' and r['domain']=='extra34'}
    for role in ('PI.H1','PI.H3','PI.H5','PI.H11','PI.H6'):
        name='PiGPIO:'+role
        try:
            cap=pipe_mouth(core[name],core['PiBudget:GPIO1992OccupiedHousing']);pipe_receipts[name]=cap
            r=roles[role];r.update(point_mm=None,jacket_routing_point_mm=cap['point_mm'],jacket_departure_axis=cap['departure_axis'],
                jacket_pose_basis='Actual current saved pipe cap adjacent to occupiedGPIO housing; NOT solder-pad or manufacturer datum',
                pose_status='CURRENT_JACKET_BOUNDARY_SOLDER_PAD_REMAINS_SEPARATE',minimum_R_mm=10)
        except Exception as exc:pipe_errors.append(dict(part=name,hold=repr(exc)))
    for wire in ('W079','W080'):
        name='PiPower:'+wire
        try:
            cap=pipe_mouth(core[name],core['PiBudget:RetainedK1474Boot']);pipe_receipts[name]=cap
            for r in rows:
                if r['wire']==wire and r['group']=='Pi4':update(r,cap['point_mm'],cap['departure_axis'],'Actual saved jacket cap at retained K1474 boot; not manufacturer pinout')
        except Exception as exc:pipe_errors.append(dict(part=name,hold=repr(exc)))
    for e in docs['pwm']['source_endpoints']:
        matches=[r for r in rows if r['wire']==e['wire'] and r['group']=='PWM9685'];assert len(matches)==1,e['wire']
        matches[0].update(point_mm=None,jacket_routing_point_mm=e['jacket_mouth_world_mm'],jacket_departure_axis=e['departure_axis'],
            jacket_grip9_mm=[e['grip_start_mm'],e['grip_end_mm']],minimum_R_mm=e['R_mm'],
            pose_status='CURRENT_JACKET_BOUNDARY_SOLDER_PAD_REMAINS_SEPARATE',bare_segments_preserved=True)
    result=dict(status='ALL246_IDENTITIES_CURRENT_POSE_RECONCILIATION_PARTIAL_NOT_N01',N01_complete=False,physical_pass=False,
        body_portions=89,extra_portions=34,physical_portions=123,ends=246,internal_U1_sections_not_duplicated=11,
        endpoints=rows,portions=portions,changed_current_datums=changes,actual_saved_Pi_pipe_cap_receipts=pipe_receipts,explicit_pipe_holds=pipe_errors,
        USB_actual_current_mouth=docs['core']['shared_fore_units']['PiUSB_changed_profile'],
        factory_4MTA_lengths=docs['body']['factory_lengths'],
        source_920_accounting=dict(historical_total_mm=920,not_an_extra_conductor_or_stock_purchase=True,
            replaced_by_wire_refs=[r['id'] for r in docs['old_source_stock']['source_recipes']],
            historical_replacement_total_mm=docs['old_source_stock']['source_nominal_total_mm'],
            historical1176_NOT_current_cut_list=True,current_cut_lengths_mm=None,
            reason='All four S1 sources moved in current layout; old920 and later1176 are historical totals, never add either to current stock.'),
        accounting_boundaries_are_not_new_connectors=True,
        open=['Whole20station selection and both directions/factory corridors','Other moved modules not silently inherited','Full shared roots/tools/access','No invented U1/GTech external pinout; delivered fit gate'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'n01-current-246-end-register.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(ends=246,portions=123,updated=len(changes),Pi_caps=len(pipe_receipts),pipe_holds=pipe_errors,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
