"""Whole changed AFTER-turn common grip and5wires, identical case reused."""
import json
import time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_compact_after_land import unit
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement


def receive_requests(requests):
    tick=time.monotonic();dest=OUT/'n01-after-land-static.json'
    files=[Path(__file__),Path(__file__).with_name('feline_compact_after_land.py'),
           Path(__file__).with_name('feline_remaining_kits.py'),Path(__file__).with_name('feline_station_zone_domains.py'),
           OUT/'n01-flat-station-architecture.json',OUT/'n01-station-zone-domains.json',
           OUT/'n01-flat20-actual-clamp-kits.json',OUT/'n01-six-source-shared-lanes.outer.brep']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    result=dict(status='RUNNING_CHANGED_AFTER_GRIP_UNIT',source_sha256=pins,units={},errors=[],N01_complete=False,physical_pass=False)
    if dest.exists():result=json.loads(dest.read_text());assert result['source_sha256']==pins
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        temp=dest.with_suffix('.writing.json');temp.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');temp.replace(dest)
    save();world,fixed=world_context();query=SolidQueries()
    old=json.loads((OUT/'n01-station-zone-domains.json').read_text())
    assert old['world_source_sha256']==world.pins,'Reused bought case needs identical fixed world'
    result['world_source_sha256']=world.pins
    stations={s['ref']:s for s in json.loads((OUT/'n01-flat-station-architecture.json').read_text())['stations']}
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    def receive(ref,choice,record):
        model=unit(stations[ref],choice);done=record.setdefault('pairs',{})
        previous=old['geometry_cache'][choice['base_recipe']['geometry_signature']]
        assert previous.get('failure','MISSING') is None
        record.update(old_bought_case_receipt_reused=choice['base_recipe']['geometry_signature'],
            full_stock_guard_mm=model['full_stock_guard_mm'],new_prefix_mm=model['new_prefix_mm'],
            old_shortest_prefix_mm=model['old_shortest_prefix_mm'],clearance_basis=model['clearance_basis'])
        # New wire/grip self-fit must be real no-positive-common, not merely
        # a foreign-air margin at the intentional jacket grooves/mouths.
        for n,s in model['parts'].items():
            if not n.startswith('wire:'):continue
            for other,t in model['parts'].items():
                if other<=n or not other.startswith('wire:') or bbox_lower_bound(s.BoundBox,t.BoundBox)>=.2:continue
                k=n+'|own:'+other
                if k not in done:
                    gap=query.distance(s,t);done[k]=dict(ok=gap>=.2-1e-6,gap_mm=gap,minimum_mm=.2);save()
                if not done[k]['ok']:return k
            for other,t in model['parts'].items():
                if n==other or other.startswith('wire:'):continue
                k=n+'|own:'+other
                if k not in done:
                    common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                    done[k]=dict(ok=common.Volume<1e-7,positive_common_mm3=common.Volume);save()
                if not done[k]['ok']:return k
        for n,s in model['parts'].items():
            if n=='case':continue
            if time.monotonic()-tick>240:raise TimeoutError('4minute whole changed after-grip slice; actual pairs retained')
            k=n+'|outer'
            if k not in done:
                outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
                gap=s.distToShape(outer.Shells[0])[0];done[k]=dict(ok=outside.Volume<1e-5 and gap>=3.25-1e-6,outside_mm3=outside.Volume,gap_mm=gap);save()
            if not done[k]['ok']:return k
            for other,t in fixed.items():
                minimum=pair_spacing(n,dict(kind=model['kinds'][n]),other,world.meta.get(other,{}))
                if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
                k=n+'|fixed:'+other
                if k not in done:
                    q=s
                    if other==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    gap=query.distance(q,t);done[k]=dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum);save()
                if not done[k]['ok']:return k
            for p in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                k=n+'|motion:'+p['name']+':'+str(p['pose'])
                if k not in done:
                    q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                    gap=query.distance(q,world.rest[p['name']]);done[k]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25);save()
                if not done[k]['ok']:return k
        return None
    try:
        for ref,choice in requests:
            rec=result['units'].setdefault(choice['key'],dict(ref=ref,choice=choice))
            if 'failure' not in rec:
                rec['failure']=receive(ref,choice,rec);save()
                print('Whole after-land unit',ref,'clear' if rec['failure'] is None else rec['failure'],flush=True)
        result['status']='REQUESTED_AFTER_LAND_FULL_UNIT_RECEIVED_NOT_N01'
    except TimeoutError as exc:result['status']='PARTIAL_AFTER_LAND_UNIT';result['slice_note']=str(exc)
    except Exception as exc:result['status']='AFTER_LAND_ERROR';result['errors'].append(repr(exc))
    save();assert not result['errors'],result['errors'];return result
