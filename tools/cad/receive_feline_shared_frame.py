"""Receive one common foundation against the accepted complete54 layout.

Planning material only, not native manufacture or N01 completion. Existing
BankBed reservations are declared same-frame joints, never bought-part
exemptions. Clamp hardware uses real no-penetration fit, preserving bearing
receipts. Every other rigid interface keeps the established1.25mm margin.
"""
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_shared_layout import chosen_material
from feline_shared_frame import build,material_connections
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_ato_service import reservation
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();source=OUT/'n01-shared54-whole.json';joint,proposal,rows,models=chosen_material(source)
    world,fixed=world_context();channelled='--channelled' in sys.argv
    if channelled:
        from feline_channelled_foundation import build as channelled_build,same_relation
        parts,meta,mates,construction=channelled_build(joint['chosen'],proposal,fixed)
    else:parts,meta,mates=build(joint['chosen'],proposal,fixed);construction={}
    dest=OUT/('n01-channelled-foundation-static.json' if channelled else 'n01-shared-foundation-static.json')
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (source,Path(__file__),Path(__file__).with_name('feline_shared_frame.py'),
        Path(__file__).with_name('feline_atomic_save.py'),OUT/'n01-six-source-shared-lanes.outer.brep')}
    if channelled:
        p=Path(__file__).with_name('feline_channelled_foundation.py');pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_COMMON_FOUNDATION',source_sha256=pins,world_source_sha256=world.pins,
        parts={},mates=mates,positive_material_connections=material_connections(parts),errors=[],N01_complete=False,physical_pass=False,
        native_changed=False,selected=False,full_case_cap_source_roots_still_open=True)
    result['construction']=construction
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins and result['world_source_sha256']==world.pins
        result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    query=SolidQueries();outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    tools={}
    for n,s in fixed.items():
        if n.startswith('Ref_Material_F_') and '_CP2_ATO_' in n:
            pp,_=reservation(n,s);tools.update({'Service:'+n+':'+k:p for k,p in pp.items()})
    assert len(tools)==24
    obstacles={**fixed,**proposal,**tools}
    def check(name,s,rec):
        done=rec.setdefault('pairs',{})
        def record(key,operation):
            if key not in done:done[key]=operation();save()
            return done[key]['ok']
        def outer_check():
            common=s.copy().cut(outer);assert common.isNull() or common.isValid()
            gap=s.distToShape(outer.Shells[0])[0]
            return dict(ok=common.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=common.Volume,gap_mm=gap,required_mm=3.25)
        if not record('outer',outer_check):return 'outer'
        for other,t in obstacles.items():
            if time.monotonic()-tick>240:raise TimeoutError('4minute common-frame slice, completed pairs retained')
            own_hardware=other.startswith(('Station:Anchor:Fore:','Station:Anchor:Rear:'))
            same_frame=other in ('StructureReserve:BankBed-1','StructureReserve:BankBed1')
            beam_mate=name.startswith(('ClampSeat:','ClampNeck:')) and other in (
                'Ref_Material_P0_SideLeft22_0_0','Ref_Material_P0_SideRight22_0_0')
            minimum=0 if own_hardware or same_frame or beam_mate else 1.25
            relation=same_relation(name,other) if channelled else None
            if relation=='replaced_planning_reservation':continue
            if relation:minimum=0
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>max(minimum,1e-7):continue
            def fixed_check():
                q,target=s,t
                if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;target=world.bus['original']
                if relation=='named_same_printed_carrier_union':
                    common=q.copy().common(target.copy());assert common.isNull() or common.isValid()
                    return dict(ok=True,positive_common_mm3=common.Volume,interface=relation,actual_positive_connections_recorded=construction['positive_material_connections'])
                if own_hardware or same_frame or beam_mate or relation:
                    common=q.copy().common(target.copy());assert common.isNull() or common.isValid()
                    return dict(ok=same_frame or common.Volume<1e-7,positive_common_mm3=common.Volume,
                        required_mm=0,interface=relation or ('declared_same_frame_bank_bed_joint' if same_frame else 'selected_P0_beam_bearing_no_penetration' if beam_mate else 'selected_clamp_hardware_fit'))
                gap=query.distance(q,target)
                return dict(ok=gap>=minimum-1e-6,gap_mm=gap,required_mm=minimum)
            key='fixed:'+other
            if not record(key,fixed_check):return key
        for p in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            def motion_check():
                q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                gap=query.distance(q,world.rest[p['name']]);return dict(ok=gap>=1.25-1e-6,gap_mm=gap,required_mm=1.25)
            key='motion:'+p['name']+':'+str(p['pose'])
            if not record(key,motion_check):return key
        return None
    try:
        for name,s in parts.items():
            rec=result['parts'].setdefault(name,dict(meta=meta[name]))
            if channelled and meta[name].get('unchanged_from')=='ShelfPWM:carrier':
                rec.update(failure=None,unchanged_complete_source_received=True);save();continue
            if 'failure' not in rec:
                rec['failure']=check(name,s,rec);save()
                print('Foundation',name,'clear' if rec['failure'] is None else rec['failure'],flush=True)
        result['status']='COMMON_FOUNDATION_CLEAR_NOT_ALL_ROOTS' if all(r['failure'] is None for r in result['parts'].values()) else 'COMMON_FOUNDATION_BLOCKED_NOT_N01'
        bundle=dest.with_suffix('.breps.zip');manifest=[]
        with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for n,s in parts.items():
                raw=s.exportBrepToString().encode();entry=f'{len(manifest):04d}.brep';z.writestr(entry,raw)
                manifest.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
        result.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),geometry=manifest)
    except TimeoutError as exc:result['status']='PARTIAL_COMMON_FOUNDATION';result['slice_note']=str(exc)
    except Exception as exc:result['status']='COMMON_FOUNDATION_ERROR';result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
