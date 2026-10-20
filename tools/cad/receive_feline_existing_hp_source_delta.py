"""Reuse the accepted HP source/grip/root kit; check only current changes.

The saved six-part kit already owns its three full9mm jacket lands and its
common head-root plate. Do not reconstruct these from old display wires.
This remains an N01 allocation receipt, not head motion/skin or production.
"""
import gzip,json,time
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from feline_atomic_save import save_json


RETIRED={'Ref_Material_headref_0_Interface_FixedJRBand_0_0',
         'Ref_Material_headref_0_Interface_SourceLandBand_0_0','StructureReserve:HeadRootPlate'}


def run(world,old_parts,current_parts,current_meta,current_pins):
    tick=time.monotonic();src=OUT/'n01-common-head-root-JR-neck-received.json';r=json.loads(src.read_text())
    dest=OUT/'n01-existing-HP-current-delta.json';assert not dest.exists(),'Receive existing result first'
    assert r['status']=='INTEGRATED_NECK_SOURCE_CURVES_RECEIVED_OTHER_GATES_OPEN' and not r['failures'] and not r['errors']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(r);assert len(actors)==6 and RETIRED<=set(current_parts)
    unchanged={n for n,s in current_parts.items() if n in old_parts and s.exportBrepToString()==old_parts[n].exportBrepToString()}
    changed={n:s for n,s in current_parts.items() if n not in unchanged and n not in RETIRED}
    records={g['name']:g for g in r['geometry']};query=SolidQueries();checks={};updates={}
    result=dict(status='RUNNING_CURRENT_HP_DELTA',source_sha256={**current_pins,
        src.relative_to(ROOT).as_posix():sha(src),ROOT.joinpath(r['bundle']).relative_to(ROOT).as_posix():sha(ROOT/r['bundle'])},
        reused_prior_complete_six_actor_gate=True,reused_prior_static36_pairs=len(r['checks']),
        unchanged_current_actor_count=len(unchanged),changed_current_actor_count=len(changed),
        retired=sorted(RETIRED),completed=[],failures=[],updates=updates,
        head_motion_skin_and_assembly_OPEN=True,N01_complete=False,physical_pass=False,native_changed=False)
    for n,s in actors.items():
        pieces=[A.BoundBox(*lo,*hi) for lo,hi in records[n].get('swept_piece_bounds_mm',[])]
        for b,t in changed.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
            if pieces and all(bbox_lower_bound(bb,t.BoundBox)>=1.25 for bb in pieces):continue
            other=t;q=s
            if b==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;other=world.bus['original']
            if not other.Solids:
                radius=current_meta.get(b,{}).get('nominal_profile_radius_mm')
                row=profile_gap(q,other,radius,1.25) if radius else dict(ok=False,unknown_existing_curve_profile=True)
            else:
                gap=query.distance(q,other);row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            checks[n+'|'+b]=row
            if not row['ok']:print('HP_CURRENT_WITNESS',n,b,row,flush=True)
        result['completed'].append(n)
    for g in r['geometry']:
        if not g.get('wire'):continue
        w=g['wire'];eid=w+'/extra/'+('end' if w=='XB22' else 'start' if w=='XB23' else 'end')
        updates[eid]=dict(jacket_grip9_mm=g['source_full9_mm'],grip_length_mm=9,
            routing_exit_mm=g['end_mm'],routing_exit_axis=[1,0,0],source_prefix_length_mm=g['path_length_mm'],
            prefix_geometry_owner=g['name'],support_owner='HPJR:carrier',
            routing_boundary_status='EXISTING_WHOLE_HP_SOURCE_GRIP_ROOT_AND_BODY_OUTLET_DELTA_RECEIVED',
            accounting_boundary_not_connector_pin=True,full_middle_route_accepted=False)
    pf=dest.with_suffix('.pairs.json.gz');pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    result.update(failures=[k for k,v in checks.items() if not v['ok']],checks=len(checks),
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3))
    result['status']='EXISTING_HP_SIX_KIT_CURRENT_DELTA_RECEIVED_HEAD_MOTION_SKIN_OPEN' if not result['failures'] else 'EXISTING_HP_WHOLE_CURRENT_DELTA_HOLD'
    save_json(dest,result);print(result['status'],len(checks),result['worker_seconds'],flush=True);return result
