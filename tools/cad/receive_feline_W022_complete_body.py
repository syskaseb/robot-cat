"""Receive one WHOLE current body portion, never the whole900mm or N01.

Reuse the proved FL source/root and bank end. The other simultaneous
candidate W051 failed its own named factory-wire pair and stays rejected.
"""
import hashlib,json,math,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from plan_feline_joint_usb_route import wire
from feline_tangent_routes import min_radius,length


def receive(rows,scene,middle,outer_check):
    tick=time.monotonic();directory=OUT/'joint-corridor-space-20261021'
    paths_file=directory/'current-curved-path-preflight.json';paths=json.loads(paths_file.read_text())
    sf=OUT/'n01-current-W022-W051-whole-middle-static.json';static=json.loads(sf.read_text())
    mf=OUT/'n01-current-W022-whole-middle-motion.json';motion=json.loads(mf.read_text())
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED' and motion['completed']==['CurrentMiddle:W022']
    assert all(r['ok'] for r in motion['checks'].values()) and outer_check['ok']
    checks={k:v for k,v in static['checks'].items() if k.startswith('CurrentMiddle:W022|')}
    assert len(checks)==104 and all(v['ok'] for v in checks.values())
    # Never turn the simultaneous W051 rejection into a green global result.
    assert static['failures']==['CurrentMiddle:W051|FactoryFour:XP02.source']
    ends=[e for e in rows if e['portion_id']=='W022/body'];assert len(ends)==2
    recipe=paths['paths']['W022/body'];assert recipe['status']=='SELF_SEPARATION_PROPOSAL_POSITIVE'
    assert middle.isValid() and len(middle.Solids)==1
    assert min_radius(recipe['parts'])>=12.4-1e-6
    assert abs(length(recipe['parts'])-recipe['length_mm'])<1e-5
    owners=['FLArcCuff:W022/body/start','Station:Bank:W022/body/end:wire:W022/body/end']
    for e,n in zip(ends,owners):
        shape=scene[n];assert shape.isValid() and shape.Solids
        p=A.Vector(*e['routing_exit_mm'])
        caps=[f for f in shape.Faces if type(f.Surface).__name__=='Plane' and (f.CenterOfMass-p).Length<1e-6]
        assert len(caps)==1 and abs(caps[0].Area-np.pi*recipe['radius_mm']**2)<1e-5
        check=checks['CurrentMiddle:W022|'+n]
        assert check['ok'] and check['common_mm3']<1e-5 and check['gap_mm']<=1e-6
    retained_lengths=[]
    for e,n in zip(ends,owners):
        if 'source_prefix_length_mm' in e:L=e['source_prefix_length_mm']
        else:
            # This bank is full9 BEFORE its received60degree R12.4 turn,
            # not a guessed12.25 straight and not another9 after the arc.
            L=e['current_prefix_entry_mm']+e['received_prefix_R_mm']*math.radians(e['current_prefix_sweep_degrees'])
        assert abs(scene[n].Volume/(math.pi*recipe['radius_mm']**2)-L)<1e-4
        retained_lengths.append(L)
    full_length=recipe['length_mm']+sum(retained_lengths)
    dest=OUT/'n01-current-W022-complete-body-plan.json';archive=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {'CurrentMiddle:W022':middle,**{n:scene[n] for n in owners}}.items():
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins={**static['source_sha256'],**motion['source_sha256'],**{
        p.relative_to(ROOT).as_posix():sha(p) for p in (paths_file,sf,mf,Path(__file__))}}
    result=dict(status='CURRENT_W022_COMPLETE_STATIC_BODY_CURVE_AND_SAMPLE36_RECEIVED_NOT_N01',
        portion='W022/body',middle_recipe=recipe,source_prefix_owners=owners,
        current_boundaries=[dict(id=e['id'],point_mm=e['routing_exit_mm'],axis=e['routing_exit_axis'],
            retained_prefix_length_mm=L) for e,L in zip(ends,retained_lengths)],
        complete_body_length_mm=full_length,middle_length_mm=recipe['length_mm'],
        checks=checks,outer=outer_check,motion=mf.relative_to(ROOT).as_posix(),motion_sha256=sha(mf),
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        source_sha256=pins,preserved_other_candidate_failure=static['failures'],
        whole900_moving_side_head_tail_motion_stock_and_complete123_OPEN=True,
        selected_SKUs_changed=False,native_changed=False,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);return result
