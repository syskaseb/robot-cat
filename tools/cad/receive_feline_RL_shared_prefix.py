"""Receive only the non-overlapping RL companion departure, not whole W047."""
import hashlib
import json
import time
import zipfile
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_RL_shared_bundle import construct
from receive_feline_W024_shared_body import solid
from refresh_feline_power_space import same_geometry
from feline_atomic_save import save_json
from plan_feline_usb_service_bight import outer_margin


def receive(shape,old_prefix,outer):
    tick=time.monotonic()
    sf=OUT/'n01-W047-W069-clocked-bundle-source-static.json'
    mf=OUT/'n01-W047-clocked-source-sampled36.json'
    static=json.loads(sf.read_text());motion=json.loads(mf.read_text());parts,_=construct(3)
    assert same_geometry(shape,solid(parts,1))
    assert not static['errors'] and static['parts']==parts
    assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert motion['completed']==['CurrentRLCompanion:W047']
    assert all(r['ok'] for r in motion['checks'].values())
    own='RLArc:W047/body/start';checks={}
    for name,row in static['checks'].items():
        minimum=0 if name==own else .2 if name in ('RLArc:W069/body/start','CurrentMiddle:W069') else 1.25
        checks[name]=dict(row,minimum_mm=minimum,ok=row['gap_mm']>=minimum-1e-6)
    assert all(r['ok'] for r in checks.values())
    assert shape.common(old_prefix).Volume<1e-5
    joint=shape.fuse(old_prefix);assert joint.isValid() and len(joint.Solids)==1
    out=outer_margin(shape,outer);assert out['ok']
    pins={**static['source_sha256'],**motion['source_sha256']}
    for p,h in pins.items():assert sha(ROOT/p)==h,p
    for p in [sf,mf,Path(__file__),ROOT/'tools/cad/plan_feline_RL_shared_bundle.py',
              OUT/'n01-current-W009-complete-body-plan.json',OUT/'n01-current-W069-complete-body-plan.json',
              OUT/'W009-W069-harness-corridor/authoritative-source-bindings.json']:
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    dest=OUT/'n01-RL-W047-companion-prefix-received.json';archive=dest.with_suffix('.breps.zip')
    assert not dest.exists() and not archive.exists()
    raw=shape.exportBrepToString().encode()
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:z.writestr('prefix.brep',raw)
    result=dict(status='RL_W047_COMPANION_DEPARTURE_STATIC36_RECEIVED_NOT_COMPLETE_BODY',
        portion='W047/body',start_mm=parts[0]['start'],routing_exit_mm=parts[-1]['end'],routing_exit_axis=[1,0,0],
        parts=parts,radius_mm=1,retained_source_cap='RLArc:W047/body/start',
        own_cap_common_mm3=0,own_cap_fused_one_valid_solid=True,
        W069_geometry_unchanged=True,checks=checks,outer=out,motion_receipt=mf.relative_to(ROOT).as_posix(),
        motion_scope='36 sampled leg poses, not continuous or head/tail motion',
        geometry=[dict(name='RLCompanion:W047:departure',entry='prefix.brep',sha256=hashlib.sha256(raw).hexdigest())],
        bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        whole_portion_received=False,remaining_bank_branch_and_common_support_OPEN=True,
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],result['worker_seconds'],flush=True);return result
