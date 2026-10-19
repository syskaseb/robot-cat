"""Receive only changed long-lane material, preserving unchanged clear parts.

The first12.25mm wire and case do not move. Full9mm comb/band/head move12mm
axially; exactly12mm of straight wire is added without changing its radius.
No returned clear means full roots, downstream curves or N01 complete.
"""
import json
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_shared_straight_combs import slots
from feline_t18i_two_lane import unit
import feline_persistent_receiver as shared


def world_context():
    if shared._receiver is None:
        import feline_beside_bank_receive as module
        module.current_world=shared.PinnedWorld(module.current_world)
        shared._receiver=module
    return shared._receiver.current_world()


def receive_requests(requests):
    tick=time.monotonic();dest=OUT/'n01-two-lane-static.json'
    files=[Path(__file__),Path(__file__).with_name('feline_t18i_two_lane.py'),Path(__file__).with_name('feline_t18i_selected_head.py'),
        ROOT/'hardware/reference/cable-ties/t18i-111-02370/head-envelope.json',OUT/'n01-six-source-current-core.json',OUT/'n01-six-source-shared-lanes.outer.brep']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    result=dict(status='RUNNING_CHANGED_LONG_LANE_RECEIPT',source_sha256=pins,units={},errors=[],N01_complete=False,physical_pass=False)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        temp=dest.with_suffix('.writing.json');temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(dest)
    save();world,fixed=world_context();query=SolidQueries()
    if result.get('world_source_sha256'):assert result['world_source_sha256']==world.pins
    result['world_source_sha256']=world.pins
    stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']};slotmap={s['id']:s for s in slots()}
    old=json.loads((OUT/'n01-straight-combs-received.json').read_text())
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    def receive(parts,rec):
        done=rec.setdefault('pairs',{})
        for n,s in parts.items():
            if time.monotonic()-tick>240:raise TimeoutError('Atomic4minute changed-interface slice')
            key=n+'|outer'
            if key not in done:
                outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
                gap=s.distToShape(outer.Shells[0])[0]
                done[key]=dict(ok=outside.Volume<1e-5 and gap>=3.25-1e-6,gap_mm=gap,outside_mm3=outside.Volume);save()
            if not done[key]['ok']:return key
            kind='wire' if n.startswith('wire:') else 'project_stock_reservation' if 'budget' in n else 'proposal_material'
            for other,t in fixed.items():
                minimum=pair_spacing('Lane:'+n,dict(kind=kind),other,world.meta.get(other,{}))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                key=n+'|fixed:'+other
                if key not in done:
                    q=s
                    if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    if not t.Solids:return key+'|curve_hold'
                    gap=query.distance(q,t);done[key]=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum);save()
                if not done[key]['ok']:return key
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                key=n+'|motion:'+p['name']+':'+str(p['pose'])
                if key not in done:
                    q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                    gap=query.distance(q,world.rest[p['name']]);done[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25);save()
                if not done[key]['ok']:return key
        return None
    try:
        for request in requests:
            ref=request['ref'];slot=slotmap[request['slot_id']];key=ref+':'+str(slot['id'])+':1'
            rec=result['units'].setdefault(key,dict(ref=ref,slot=slot,lane=1))
            if 'failure' in rec:continue
            previous=old['units'][ref+':'+str(slot['id'])]
            assert 'failure' in previous,'Receive original unit to establish unchanged case/first-wire proof first'
            failure=previous['failure']
            if failure and (failure.startswith('case|') or failure.startswith('wire:')):
                rec.update(failure='UNCHANGED_CASE_OR_WIRE_SUBSET:'+failure,prior_static_failure_reused=True);save();continue
            model=unit(stations[ref],slot,1);d=np.array([0.,-slot['side'],0.]);changed={n:s for n,s in model['parts'].items() if not n.startswith('wire:') and n!='case'}
            for w in model['wires']:
                q=np.asarray(w['point_mm'])+d*12.25
                changed['wire:'+w['endpoint']]=Part.makeCylinder(w['radius_mm'],12,A.Vector(*q),A.Vector(*d))
            rec.update(unchanged_case_and_initial_wire_proof=ref+':'+str(slot['id']),
                changed_full_bodies=['split_common_comb','band_budget','head_budget'],new_wire_straight_mm=12,
                full_wire_and_all_mouths=model['wires'],source_blanks_and_roots_NOT_accepted=True)
            rec['failure']=receive(changed,rec);save()
            print('Long lane',key,'clear' if rec['failure'] is None else rec['failure'],flush=True)
        result['status']='REQUESTED_LONG_LANES_RECEIVED_NOT_WHOLE_PLAN'
    except TimeoutError as exc:result['status']='PARTIAL_LONG_LANE_RECEIPT';result['slice_note']=str(exc)
    except Exception as exc:result['status']='LONG_LANE_RECEIVER_ERROR';result['errors'].append(repr(exc))
    save();assert not result['errors'],result['errors'];return result
