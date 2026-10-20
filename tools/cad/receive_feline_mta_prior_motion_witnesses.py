"""Check only eight saved rear-shoe rejection interfaces on current material.

Old failed material is not a current failure or pass. Stop on its first actual
current witness before launching a whole-kit matrix. Four wire job is separate.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-MTA-body-head-clock.json';current=json.loads(sf.read_text())
    of=OUT/'n01-factory-inputs-current-received.json';old=json.loads(of.read_text())
    for r in (current,old):
        for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(current);world,_=world_context();query=SolidQueries()
    for p,h in world.pins.items():assert current['source_sha256'][p]==old['source_sha256'][p]==h,p
    poses={(p['name'],p['pose']):p for p in world.motion};checks={}
    for key in old['failures']:
        n,pk=key.split('|');assert n in ('CaseBase:W044_Joint','CaseBase:W052_Joint')
        source,index=pk.removeprefix('motion:').rsplit(':',1);p=poses[source,int(index)]
        tf=placement(p['r'],p['t']);shape=actors[n].copy();shape.Placement=tf.inverse()*shape.Placement
        material=world.rest[source];gap=query.distance(shape,material)
        row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
        if not row['ok']:
            _,points,_=shape.distToShape(material);c=shape.common(material);assert c.isNull() or c.isValid()
            row.update(world_witness_mm=[[list(tf.multVec(a)),list(tf.multVec(b))] for a,b in points[:1]],
                actual_common_mm3=c.Volume,leg_code=p['code'],stage=p['stage'],pose_index=p['pose'])
        checks[key]=row
        if not row['ok']:break
    dest=OUT/'n01-MTA-prior-motion-witnesses.json';pf=dest.with_suffix('.pairs.json.gz');assert not dest.exists()
    pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    failures=[k for k,v in checks.items() if not v['ok']]
    result=dict(status='CURRENT_REAR_SHOE_MOTION_HOLD' if failures else 'EIGHT_PRIOR_REJECTIONS_CLEAR_ON_CURRENT_SHOES_NOT_WHOLE_KIT',
        source_sha256={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/current['bundle'],of,Path(__file__))}},
        current_actor_sha256={r['name']:r['sha256'] for r in current['geometry'] if r['name'] in ('CaseBase:W044_Joint','CaseBase:W052_Joint')},
        checks=len(checks),failures=failures,pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),
        N01_complete=False,native_changed=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],checks,result['worker_seconds'],flush=True)


if __name__=='__main__':main()
