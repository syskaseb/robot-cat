"""Receive W047 fixed body only from canonical scene and sampled motion."""
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from receive_feline_W024_shared_body import solid
from refresh_feline_power_space import same_geometry
from plan_feline_usb_service_bight import outer_margin
from feline_tangent_routes import length,min_radius


def receive(shape,scene,rows,outer,bus_gap):
    tick=time.monotonic();pins={};receipts={}
    for suffix in ('graph','static','sampled36'):
        f=OUT/('n01-W047-fixed-departure-all-tangents-'+suffix+'.json')
        r=json.loads(f.read_text());receipts[suffix]=r
        for p,h in r['source_sha256'].items():
            assert sha(ROOT/p)==h,p
            assert p not in pins or pins[p]==h,p
            pins[p]=h
        pins[f.relative_to(ROOT).as_posix()]=sha(f)
    graph,static,motion=(receipts[k] for k in ('graph','static','sampled36'))
    recipe=graph['accepted'];parts=recipe['parts']
    assert graph['all_existing_entry_tangents'] and graph['companion_departure']
    assert recipe['self_gap_lower_mm']>=.2 and min_radius(parts)>=12.4
    assert parts==static['parts'] and same_geometry(shape,solid(parts,1))
    assert not static['errors'] and len(scene)==1541
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert motion['completed']==['CurrentMiddle:W047']
    assert all(v['ok'] for v in motion['checks'].values())
    owners=['RLArc:W047/body/start','Station:Bank:W047/body/end:wire:W047/body/end']
    checks={}
    for name,r in static['checks'].items():
        minimum=0 if name in owners else .2 if name in ('RLArc:W069/body/start','CurrentMiddle:W069','CurrentMiddle:W009') else 1.25
        checks[name]=dict(r,minimum_mm=minimum,ok=r['gap_mm']>=minimum-1e-6)
    assert all(r['ok'] for r in checks.values())
    assert bus_gap>=1.25 and math.isfinite(bus_gap)
    checks['BUS25:valid_original']=dict(gap_mm=bus_gap,minimum_mm=1.25,ok=True)
    out=outer_margin(shape,outer);assert out['ok']
    boundaries=[];payload={'CurrentMiddle:W047':shape}
    for side,owner,endpoint in zip(('start','end'),owners,(parts[0]['start'],parts[-1]['end'])):
        cap=scene[owner];assert cap.isValid() and len(cap.Solids)==1
        e=next(r for r in rows if r['id']=='W047/body/'+side)
        assert np.allclose(endpoint,e['routing_exit_mm'],atol=1e-6,rtol=0)
        common=shape.common(cap).Volume;joint=shape.fuse(cap)
        assert common<1e-5 and joint.isValid() and len(joint.Solids)==1
        checks[owner].update(common_mm3=common)
        boundaries.append(dict(id=e['id'],point_mm=endpoint,axis=e['routing_exit_axis'],retained_prefix_length_mm=cap.Volume/math.pi))
        payload[owner]=cap
    dest=OUT/'n01-current-W047-complete-body-plan.json';archive=dest.with_suffix('.breps.zip')
    assert not dest.exists() and not archive.exists()
    geometry=[]
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,s in payload.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    for p in (Path(__file__),OUT/'W009-W069-harness-corridor/authoritative-source-bindings.json',
              OUT/'n01-current-W009-complete-body-plan.json',OUT/'n01-current-W069-complete-body-plan.json'):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='CURRENT_W047_BODY_CANONICAL_STATIC_AND_SAMPLE36_RECEIVED_NOT_N01',portion='W047/body',
        middle_recipe=recipe,middle_length_mm=length(parts),
        complete_body_length_mm=length(parts)+sum(r['retained_prefix_length_mm'] for r in boundaries),
        current_boundaries=boundaries,source_prefix_owners=owners,checks=checks,outer=out,
        scene_actors=1541,canonical_BUS_original_used=True,sampled_poses=36,motion_actors_covered=3888,
        motion_receipt=(OUT/'n01-W047-fixed-departure-all-tangents-sampled36.json').relative_to(ROOT).as_posix(),
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        whole900_moving_side_stock_supports_and_complete123_OPEN=True,N01_complete=False,physical_pass=False,
        native_changed=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['complete_body_length_mm'],result['worker_seconds'],flush=True)
    return result
