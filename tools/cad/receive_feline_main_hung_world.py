"""Only25 changed MAIN actors against the current whole planning scene.

Reuse local receipts. Existing printed-root aliases must be proven subsets
of the unchanged Pi carrier; unrelated parts retain ordinary clearances.
"""
import gzip,json,os,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose,received
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose();sf,local=received()
    changed=docs['MAIN_changed'];assert len(changed)==25
    fixed={n:s for n,s in parts.items() if n not in changed};actors={n:parts[n] for n in changed}
    oldfile=ROOT/local['pair_rows'];assert sha(oldfile)==local['pair_rows_sha256'];old=json.loads(gzip.decompress(oldfile.read_bytes()))
    assert all(v['ok'] for v in old.values())
    checks={};dest=OUT/'n01-MAIN-hung-world.json';pf=dest.with_suffix('.pairs.json.gz')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,oldfile,Path(__file__))})
    result=dict(status='RUNNING_MAIN_WHOLE_WORLD',source_sha256=pins,completed_static=[],completed_motion=[],
        adopted_local_checks=len(old),local_pair_rows=oldfile.relative_to(ROOT).as_posix(),local_pair_rows_sha256=sha(oldfile),
        reused_local_pairs=0,root_aliases={},N01_complete=False,physical_pass=False,native_changed=False)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()))
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,result)
    save();query=SolidQueries();parent=parts['SharedPi:Carrier']
    for n in sorted(changed):
        if n in result['completed_static']:continue
        s=actors[n];checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in fixed.items():
            key=n+'|'+m
            if key in checks:continue
            if key in old:
                checks[key]=dict(old[key],unchanged_local_pair_reused=True);result['reused_local_pairs']+=1;continue
            if n=='MainSupported:root' and m in ('SharedPi:Carrier','CurrentFoundation:RetainedPWMCarrier','ShelfPWM:carrier'):
                assert t.isValid() and t.Solids
                missing=t.copy().cut(parent.copy());assert missing.isNull() or missing.isValid();assert missing.Volume<1e-5
                checks[key]=dict(ok=True,named_alias_of_same_received_print_unit=True,material_outside_Pi_parent_mm3=missing.Volume,
                    valid_full_root_Pi_union_source=sf.relative_to(ROOT).as_posix())
                result['root_aliases'][m]=checks[key];continue
            minimum=minimum_for(n,meta[n],m,meta[m])
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a=s
            if m==world.bus['name']:
                a=s.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
            checks[key]=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,meta[m].get('nominal_profile_radius_mm') or meta[m].get('radius_mm'),minimum)
        result['completed_static'].append(n);save();print('MAIN world',n,'holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>220:result['status']='PARTIAL_MAIN_WORLD_SAVED_RECEIVE_BEFORE_RESUME';save();return
    if not result['failures']:
        for n in sorted(changed):
            if n in result['completed_motion']:continue
            s=actors[n]
            for pose in world.motion:
                key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                if key in checks or bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
            if time.monotonic()-tick>220:result['status']='PARTIAL_MAIN_WORLD_SAVED_RECEIVE_BEFORE_RESUME';save();return
    result['status']='MAIN_WHOLE_WORLD_HOLDS' if result['failures'] else 'MAIN_WHOLE_STATIC36_RECEIVED_TOOLS_ASSEMBLY_OPEN'
    result['motion_is_sampled_not_continuous']=True
    save();print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
