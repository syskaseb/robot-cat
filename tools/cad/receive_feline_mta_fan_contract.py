"""Apply existing named own-grip nonpenetration policy, then6 motion checks.

Keep every original observation. Only two heads versus their SAME original
pad use the original receiver's same_grip common.Volume gate, NOT its old
gap: the new gap is smaller. Foreign1.25 is never changed. No geometry
or blanket group waiver and no claim that full N01/grips/roots are complete.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from receive_feline_main_ato_gallery import selected
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();f=OUT/'n01-MTA-tilted-fans.json';prior=json.loads(f.read_text());actors=load(prior)
    assert len(prior['completed_static'])==6 and len(prior['failures'])==2
    for p,h in prior['source_sha256'].items():assert sha(ROOT/p)==h,p
    pf0=ROOT/prior['pair_rows'];assert sha(pf0)==prior['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf0.read_bytes()))
    of=OUT/'n01-rooted-end-bays-caps.json';original=json.loads(of.read_text())
    old,_,opins=selected(of,'geometry',lambda n:n in ('EndGrip:Factory:W045:head','EndGrip:Factory:W045:pad','EndGrip:Factory:W053:head','EndGrip:Factory:W053:pad'))
    query=SolidQueries();reconciled={}
    for w in ('W045','W053'):
        head='EndGrip:Factory:'+w+':head';pad=head.removesuffix('head')+'pad';key=head+'|'+pad
        assert key in prior['failures'] and original['actor_owner'][head]==original['actor_owner'][pad]==w
        before=query.distance(old[head],old[pad]);current=query.distance(actors[head],old[pad]);common=actors[head].common(old[pad])
        assert head.rsplit(':',1)[0]==pad.rsplit(':',1)[0]
        assert (common.isNull() or common.isValid()) and common.Volume<1e-5
        reconciled[key]=dict(checks[key],ok=True,minimum_mm=0.,original_own_grip_gap_mm=before,
            actual_current_gap_mm=current,actual_current_common_mm3=common.Volume,
            exactly_named_original_independent_grip_NOT_foreign=True,foreign_margin_unchanged_mm=1.25,
            geometry_and_stock_NOT_changed=True,old_gap_NOT_inherited=True,
            policy_source='tools/cad/receive_feline_end_bay_outputs.py same_grip: common.Volume<1e-5')
    checks.update(reconciled);assert all(v['ok'] for v in checks.values())
    world,_=world_context()
    for p,h in world.pins.items():assert prior['source_sha256'][p]==h
    dest=OUT/'n01-MTA-four-fans-received.json';pf=dest.with_suffix('.pairs.json.gz')
    result=dict(prior,status='RUNNING_MTA_FOUR_FAN_MOTION',source_sha256={**prior['source_sha256'],**opins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (f,pf0,Path(__file__))}},
        inherited_own_grip_pairs=reconciled,adopted_static_checks=len(checks),adopted_static_worker_seconds=prior['worker_seconds'],
        completed_motion=[],N01_complete=False,physical_pass=False,native_changed=False,
        whole_custom_grips_roots_moved_case_kits_tools_and_common123_still_OPEN=True)
    if dest.exists():
        previous=json.loads(dest.read_text());assert previous['source_sha256']==result['source_sha256']
        assert sha(pf)==previous['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));result=previous
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save()
    for n,s in actors.items():
        if n in result['completed_motion']:continue
        for pose in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
            if key in checks:continue
            a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
            gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
        result['completed_motion'].append(n);save()
        if time.monotonic()-tick>220:result['status']='PARTIAL_MTA_FOUR_FAN_MOTION_SAVED';save();return
    result['status']='MTA_FOUR_FAN_MOTION_HOLDS' if result['failures'] else 'FOUR_MTA_FULL_CUSTOM_FANS_TWO_T18I_HEADS_STATIC36_RECEIVED_GRIPS_ROOTS_OPEN'
    result['motion_is_sampled_not_continuous']=True;save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
