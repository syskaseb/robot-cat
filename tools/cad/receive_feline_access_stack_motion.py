"""Receive changed installed source actors, never the service-only tool budget.

Reuse two unchanged source motion actors by actual symmetric-set proof and
pinned world inputs, not by repeated BRep reserialization or a part count.
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


def shapes(r):
    assert sha(ROOT/r['bundle'])==r['bundle_sha256'];out={}
    with zipfile.ZipFile(ROOT/r['bundle']) as z:
        for n,p in r['geometry'].items():
            raw=z.read(p['entry']);assert hashlib.sha256(raw).hexdigest()==p['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids;out[n]=s
    return out


def main():
    tick=time.monotonic();sf=OUT/'n01-F0-access-stack.json';src=json.loads(sf.read_text())
    assert src['status']=='SHARED_SOURCE_CHANGED_OUTER_STATIC_ONLY_ROOTS_MOTION_ASSEMBLY_OPEN' and not src['failures']
    assert len(src['own_whole_kit_checks'])==28 and all(v['ok'] for v in src['own_whole_kit_checks'].values())
    for p,h in src['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=shapes(src)
    for n in src['service_only_actor_names']:actors.pop(n)
    assert len(actors)==src['installed_source_actor_count']==7
    world,_=world_context()
    for p,h in world.pins.items():assert src['source_sha256'][p]==h,p
    oldf=OUT/'n01-BAT-F0-fork-motion.json';old=json.loads(oldf.read_text());oldsf=ROOT/old['source_layout'];oldsrc=json.loads(oldsf.read_text())
    assert old['status']=='SOURCE_SEVEN_ACTORS36MOTION_RECEIVED_ROOTS_ASSEMBLY_COMMON123_OPEN' and not old['failures']
    assert old['world_source_sha256']==world.pins and old['source_sha256'][oldsf.relative_to(ROOT).as_posix()]==sha(oldsf)
    prior=shapes(oldsrc);identity={}
    for n in src['unchanged_existing_body_names']:
        a,b=actors[n],prior[n];one=a.copy().cut(b.copy());two=b.copy().cut(a.copy())
        assert (one.isNull() or one.isValid()) and (two.isNull() or two.isValid())
        delta=one.Volume+two.Volume;assert delta<1e-5
        assert n in old['completed_motion'];identity[n]=dict(symmetric_difference_mm3=delta,old_actor_sha256=oldsrc['geometry'][n]['sha256'],new_actor_sha256=src['geometry'][n]['sha256'])
    pins=dict(src['source_sha256']);pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/src['bundle'],oldf,oldsf,ROOT/oldsrc['bundle'],Path(__file__))})
    dest=OUT/'n01-F0-access-stack-motion.json';pf=dest.with_suffix('.pairs.json.gz')
    result=dict(status='RUNNING_ACCESS_STACK_MOTION',source_sha256=pins,source_layout=sf.relative_to(ROOT).as_posix(),world_source_sha256=world.pins,
        source_actor_count=7,service_only_budget_NOT_an_installed_component=True,reused_actual_unchanged_identity=identity,
        completed_motion=sorted(identity),pose_indices=list(range(36)),motion_is_sampled_not_continuous=True,
        full_grips_roots_actual_cover_fit_and_shared123_OPEN=True,N01_complete=False,native_changed=False,physical_pass=False)
    checks={};query=SolidQueries()
    if dest.exists():
        old=json.loads(dest.read_text());assert old['source_sha256']==pins
        assert sha(pf)==old['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));result=old
        if result['failures'] or len(result['completed_motion'])==7:print('TERMINAL',result['status']);return
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save(status=None):
        if status:result['status']=status
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf));save_json(dest,result)
    save()
    for n,s in actors.items():
        if n in result['completed_motion']:continue
        bb=s.BoundBox
        for p in world.motion:
            if bbox_lower_bound(bb,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+p['name']+':'+str(p['pose'])
            if key in checks:continue
            tf=placement(p['r'],p['t']);local=s.copy();local.Placement=tf.inverse()*local.Placement;other=world.rest[p['name']];gap=query.distance(local,other)
            row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if not row['ok']:
                _,pts,_=local.distToShape(other);row['world_witness_mm']=[[list(tf.multVec(a)),list(tf.multVec(b))] for a,b in pts[:1]]
                c=local.common(other);assert c.isNull() or c.isValid();row['actual_common_mm3']=c.Volume
                row.update(pose_index=p['pose'],leg_code=p['code'],stage=p['stage'])
            checks[key]=row;save()
            if not row['ok']:save('ACCESS_STACK_MOTION_ACTUAL_HOLD');print(result['status'],key,row,flush=True);return
            if time.monotonic()-tick>220:save('PARTIAL_ACCESS_STACK_MOTION_SAVED');print(result['status'],len(checks),flush=True);return
        result['completed_motion'].append(n);save();print('RECEIVED36',n,flush=True)
    save('ACCESS_STACK_SEVEN_ACTORS36MOTION_RECEIVED_FULL_RESTRAINTS_AND_SHARED123_OPEN')
    print(result['status'],len(checks),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
