"""Resumable changed gallery receipt; exact geometry, no native selection.

Start with four functional probes. No automatic combinatorial sweep until
their named causes have been read. Stores every pair, including rejections.
"""
import hashlib
import copy
import json
import os
import sys
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_case_zone_allocation import current_world
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_beside_bank_plan import slots,unit


def main():
    tick=time.monotonic();straight='--straight' in sys.argv
    makeunit=unit;slot_list=slots()
    if straight:
        from feline_shared_straight_combs import slots as straight_slots,unit as straight_unit
        makeunit=straight_unit;slot_list=straight_slots()
    dest=OUT/('n01-straight-combs-received.json' if straight else 'n01-beside-bank-received.json')
    files=[Path(__file__),Path(__file__).with_name('feline_beside_bank_plan.py'),
           Path(__file__).with_name('feline_underplate_station_templates.py'),
           OUT/'n01-flat-station-architecture.json',OUT/'n01-six-source-current-core.json',
           OUT/'n01-six-source-shared-lanes.outer.brep']
    if straight:files.append(Path(__file__).with_name('feline_shared_straight_combs.py'))
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    result=dict(status='RUNNING_FOUR_FUNCTIONAL_PROBES',source_sha256=pins,units={},errors=[],N01_complete=False,physical_pass=False)
    if dest.exists():
        result=json.loads(dest.read_text())
        if result['source_sha256']!=pins and '--receive-controller' in sys.argv:
            own=Path(__file__).relative_to(ROOT).as_posix()
            assert result['source_sha256'][own]=='25653716c5bb3c96bf82ce6287d253ed40cca158b64cbf9dc2b6aef48ed0c261'
            assert all(result['source_sha256'][n]==v for n,v in pins.items() if n!=own)
            result.setdefault('controller_repairs',[]).append(dict(old_code_sha256=result['source_sha256'][own],reason='Same receive kernel and constructors; requested-only ordering and equivalent physical-profile pair reuse. Existing8probes retained.'))
            result['source_sha256']=pins
        else:assert result['source_sha256']==pins
        result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();world,fixed=current_world();query=SolidQueries()
    if result.get('world_source_sha256'):assert result['world_source_sha256']==world.pins
    result['world_source_sha256']=world.pins
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    stations=json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']
    def receive(parts,record):
        done=record.setdefault('pairs',{})
        for n,s in parts.items():
            if time.monotonic()-tick>240:raise TimeoutError('Four-minute atomic slice; completed pairs saved')
            key=n+'|true_outer'
            if key not in done:
                cut=s.copy().cut(outer);assert cut.isNull() or cut.isValid()
                gap=s.distToShape(outer.Shells[0])[0]
                done[key]=dict(ok=cut.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=cut.Volume,gap_mm=gap);save()
            if not done[key]['ok']:return key
            for other,t in fixed.items():
                minimum=pair_spacing(n,dict(kind='wire' if n.startswith('wire:') else 'proposal_material'),other,world.meta.get(other,{}))
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
    probes=[('D_FL',-46.875,1,None),('FL_P',15.625,1,None),('P_FRONT',75.,1,None),('G1',-5.,-1,None)]
    if straight:probes=[(a,b,c,'interdeck') for a,b,c,_ in probes]+[('D_FR',-15.625,1,'overbank'),('RR_G',46.875,-1,'overbank'),('G_AUX',78.125,1,'overbank'),('P_REAR',35.,-1,'overbank')]
    if '--all' in sys.argv:
        probes=[(st['ref'],s['centre_mm'][0],1 if s['centre_mm'][1]>0 else -1,s.get('tier'))
                for st in stations if not st['fixed_identity_pose'] for s in slot_list
                if s['profile']==('large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard')]
    if '--requested' in sys.argv:
        request=json.loads((OUT/'n01-simple-comb-joint-targets.json').read_text())['requests']
        probes=[]
        for row in request:
            s=next(s for s in slot_list if s['id']==row['slot_id'])
            probes.append((row['ref'],s['centre_mm'][0],s['side'],s['tier']))
    try:
        for ref,x,side,tier in probes:
            st=next(st for st in stations if st['ref']==ref)
            profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
            slot=next(s for s in slot_list if s['profile']==profile and s['centre_mm'][0]==x and s['centre_mm'][1]*side>0 and s.get('tier')==tier)
            key=ref+':'+str(slot['id']);r=result['units'].setdefault(key,dict(ref=ref,slot=slot))
            model=makeunit(st,slot);r['wire_endpoints']=model['wires']
            ordered=sorted(model['wires'],key=lambda w:tuple(w['point_mm']))
            physical=dict(slot=slot,ports=[dict(point=w['point_mm'],radius=w['radius_mm']) for w in ordered])
            physical_key=hashlib.sha256(json.dumps(physical,sort_keys=True).encode()).hexdigest()
            r['physical_key']=physical_key;rename={'wire:'+w['endpoint']:'wire:'+str(i) for i,w in enumerate(ordered)}
            canonical={rename.get(n,n):s for n,s in model['parts'].items()}
            cache=result.setdefault('physical_cache',{})
            if 'failure' in r and physical_key not in cache:
                rec=copy.deepcopy(r)
                def renamed(s):
                    if s is None:return None
                    for a,b in rename.items():s=s.replace(a+'|',b+'|')
                    return s
                rec['pairs']={renamed(k):v for k,v in rec.get('pairs',{}).items()};rec['failure']=renamed(rec['failure']);cache[physical_key]=rec
            record=cache.setdefault(physical_key,dict(source_example=key))
            if 'failure' not in record:record['failure']=receive(canonical,record)
            r['failure']=record['failure'];r['physical_receipt']=physical_key;save()
            print(key,'clear' if r['failure'] is None else 'blocked '+r['failure'],flush=True)
        result['status']='PROBES_RECEIVED_NOT_N01' if '--all' not in sys.argv else 'WHOLE_GALLERY_CATALOGUE_RECEIVED_NOT_N01'
    except TimeoutError as exc:result['status']='PARTIAL_GALLERY_RECEIPT';result['slice_note']=str(exc)
    except Exception as exc:result['status']='GALLERY_RECEIVER_ERROR';result['errors'].append(repr(exc))
    save();print(json.dumps(dict(status=result['status'],worker_seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True);main()
