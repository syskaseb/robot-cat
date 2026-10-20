"""Seven source actors through the existing36 poses; reuse exact static proof.

No unchanged MTA/source fixed-pair replay. Save each actual motion pair, resume
missing only, and stop a rejected family before mounting detail.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-BAT-F0-fork-exit.json';src=json.loads(sf.read_text())
    assert src['status']=='SHARED_SOURCE_CHANGED_OUTER_STATIC_ONLY_ROOTS_MOTION_ASSEMBLY_OPEN' and not src['failures']
    assert len(src['own_whole_kit_checks'])==21 and all(v['ok'] for v in src['own_whole_kit_checks'].values())
    for p,h in src['source_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in src['builder_dependency_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/src['bundle'])==src['bundle_sha256'];actors={}
    with zipfile.ZipFile(ROOT/src['bundle']) as z:
        for n,r in src['geometry'].items():
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids;actors[n]=s
    world,_=world_context()
    for p,h in world.pins.items():assert src['source_sha256'][p]==h,p
    assert {p['pose'] for p in world.motion}==set(range(36))
    pins=dict(src['source_sha256']);pins.update(src['builder_dependency_sha256'])
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/src['bundle'],Path(__file__))})
    dest=OUT/'n01-BAT-F0-fork-motion.json';pf=dest.with_suffix('.pairs.json.gz')
    result=dict(status='RUNNING_SOURCE_MOTION',source_sha256=pins,world_source_sha256=world.pins,
        source_layout=sf.relative_to(ROOT).as_posix(),completed_motion=[],source_actor_count=7,
        pose_indices=list(range(36)),motion_is_sampled_not_continuous=True,
        full_grips_roots_tools_battery_leads_and_shared123_still_OPEN=True,
        N01_complete=False,native_changed=False,physical_pass=False)
    checks={};query=SolidQueries()
    if dest.exists():
        old=json.loads(dest.read_text());assert old['source_sha256']==pins
        assert sha(pf)==old['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));result=old
        if result['failures'] or len(result['completed_motion'])==7:print('TERMINAL',result['status']);return
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save(status=None):
        if status:result['status']=status
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf));save_json(dest,result)
    save()
    for n,s in actors.items():
        if n in result['completed_motion']:continue
        bb=s.BoundBox
        for p in world.motion:
            if bbox_lower_bound(bb,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+p['name']+':'+str(p['pose'])
            if key in checks:continue
            tf=placement(p['r'],p['t']);local=s.copy();local.Placement=tf.inverse()*local.Placement
            other=world.rest[p['name']];gap=query.distance(local,other)
            row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if not row['ok']:
                _,pts,_=local.distToShape(other);row['world_witness_mm']=[[list(tf.multVec(a)),list(tf.multVec(b))] for a,b in pts[:1]]
                common=local.common(other);assert common.isNull() or common.isValid();row['actual_common_mm3']=common.Volume
                row.update(pose_index=p['pose'],leg_code=p['code'],stage=p['stage'])
            checks[key]=row;save()
            if not row['ok']:save('SOURCE_MOTION_ACTUAL_HOLD');print(result['status'],key,row,flush=True);return
            if time.monotonic()-tick>220:save('PARTIAL_SOURCE_MOTION_SAVED');print(result['status'],len(checks),flush=True);return
        result['completed_motion'].append(n);save();print('RECEIVED36',n,flush=True)
    save('SOURCE_SEVEN_ACTORS36MOTION_RECEIVED_ROOTS_ASSEMBLY_COMMON123_OPEN')
    print(result['status'],len(checks),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
