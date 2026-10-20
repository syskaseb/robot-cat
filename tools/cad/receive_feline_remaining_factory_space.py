"""Four changed input curves only; shared grips/roots are a separate gate.

Never inherit the old R12.4 curve or pretend a positive mutual plan proves
foreign clearance. Keep bought cases, current joints and all other actors.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_underplate_return_gallery import minimum_for
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    source=OUT/'n01-remaining-factory-input-plan.json';plan=json.loads(source.read_text())
    assert all(p['ok'] for p in plan['pairs'])
    for p,h in plan['source_sha256'].items():assert sha(ROOT/p)==h,p
    names={'Factory:'+w for w in plan['routes']};old={n:parts[n] for n in names}
    actors={n:pipe(plan['routes'][n.split(':')[1]]['parts'],2.1) for n in names}
    dest=OUT/'n01-remaining-factory-space.json';pf=dest.with_suffix('.pairs.json.gz')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (source,Path(__file__))})
    checks={};result=dict(status='RUNNING_FOUR_FACTORY_INPUT_SPACE',source_sha256=pins,
        changed=list(sorted(names)),completed_static=[],completed_motion=[],
        N01_complete=False,native_changed=False,physical_pass=False,
        full_grips_roots_access_length_still_OPEN=True)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        assert sha(pf)==result['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()))
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,result)
    save();query=SolidQueries()
    for n in sorted(names):
        if n in result['completed_static']:continue
        s=actors[n];w=n.split(':')[1];checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in parts.items():
            if m in names:continue
            key=n+'|'+m
            if key in checks:continue
            minimum=minimum_for(n,dict(kind='actual_wire'),m,meta[m])
            ownseat=m.startswith('Seat:'+w+':factory:')
            if ownseat:minimum=.15
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a=s
            if m==world.bus['name']:
                a=s.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
            row=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,meta[m].get('nominal_profile_radius_mm') or meta[m].get('radius_mm'),minimum)
            # Only the unchanged material ingress in the SAME named bought
            # source/target is admissible. All other contacts remain holds.
            if m=='Ref_Material_'+w+'_Joint_0_0' or m.startswith('Ref_Material_MTA_') and m.endswith('_0_0'):
                c=a.common(t);prior=old[n].common(t)
                assert (c.isNull() or c.isValid()) and (prior.isNull() or prior.isValid())
                delta=c.cut(prior).Volume+prior.cut(c).Volume
                if prior.Volume>1e-7:row.update(ok=delta<1e-5,unchanged_named_ingress_mm3=prior.Volume,ingress_symmetric_difference_mm3=delta)
            if not row['ok'] and t.Solids:
                _,pts,_=a.distToShape(t)
                row['witness_mm']=[[list(x),list(y)] for x,y in pts[:2]]
            checks[key]=row
        result['completed_static'].append(n);save()
        print(n,'static holds',len(result['failures']),flush=True)
        if time.monotonic()-tick>210:return
    if not result['failures']:
        for n in sorted(names):
            if n in result['completed_motion']:continue
            s=actors[n]
            for pose in world.motion:
                key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
                if key in checks or bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[key]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            result['completed_motion'].append(n);save()
            if time.monotonic()-tick>210:return
    result['status']='FOUR_FACTORY_INPUT_SPACE_HOLDS' if result['failures'] else 'FOUR_FACTORY_INPUT_STATIC36_RECEIVED_GRIPS_ROOTS_OPEN'
    result['motion_is_sampled_not_continuous']=True;save()
    print(result['status'],result['checks'],len(result['failures']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
