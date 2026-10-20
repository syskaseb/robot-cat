"""Receive four whole wire motions BEFORE more local retainer-fit work.

Four static+outer proofs are received from the unchanged wire hashes. The
single changed FL tie-head is bbox-separated from all four wires. No wire
motion query repeats once saved; first actual failure stops this family.
"""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_two_lane_receive import world_context
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-MTA-body-head-clock.json';current=json.loads(sf.read_text())
    assert current['status']=='COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN' and not current['failures']
    for p,h in current['source_sha256'].items():assert sha(ROOT/p)==h,p
    oldfile=OUT/'n01-MTA-body-retention-scene.json';old=json.loads(oldfile.read_text())
    for p,h in old['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(current);names=sorted(current['recipes']);assert len(names)==4
    before={r['name']:r for r in old['geometry']};after={r['name']:r for r in current['geometry']}
    for n in names:assert n in old['completed_static'] and before[n]==after[n]
    changed=[n for n in before if before[n]['sha256']!=after[n]['sha256']];assert changed==['CaseTie:FLHead']
    changed_head=actors[changed[0]]
    head_separation={n:bbox_lower_bound(actors[n].BoundBox,changed_head.BoundBox) for n in names}
    assert all(v>=1.25 for v in head_separation.values())
    world,_=world_context()
    for p,h in world.pins.items():assert current['source_sha256'][p]==h,p
    assert {p['pose'] for p in world.motion}==set(range(36))
    pins=dict(current['source_sha256']);pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/current['bundle'],oldfile,Path(__file__))})
    dest=OUT/'n01-MTA-four-wires-motion.json';pf=dest.with_suffix('.pairs.json.gz')
    result=dict(status='RUNNING_FOUR_WIRE_MOTION',source_sha256=pins,source_layout=sf.relative_to(ROOT).as_posix(),
        source_wire_actor_sha256={n:after[n]['sha256'] for n in names},world_source_sha256=world.pins,
        reused_static_outer_names=names,reused_static_scene_sha256=sha(oldfile),new_head_bbox_positive_separation_mm=head_separation,
        completed_motion=[],pose_indices=list(range(36)),motion_is_sampled_not_continuous=True,
        kit_roots_tools_and_shared123_NOT_received=True,N01_complete=False,native_changed=False,physical_pass=False)
    checks={};query=SolidQueries()
    if dest.exists():
        previous=json.loads(dest.read_text());assert previous['source_sha256']==pins
        assert sha(pf)==previous['pair_rows_sha256'];checks=json.loads(gzip.decompress(pf.read_bytes()));result=previous
        if result['failures'] or len(result['completed_motion'])==4:print('Already received terminal wire result',result['status'],flush=True);return
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    def save(status=None):
        if status:result['status']=status
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        result.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3),
            pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf));save_json(dest,result)
    save('RUNNING_FOUR_WIRE_MOTION')
    for n in names:
        if n in result['completed_motion']:continue
        wire=actors[n]
        for pose in world.motion:
            if bbox_lower_bound(wire.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
            key=n+'|motion:'+pose['name']+':'+str(pose['pose'])
            if key in checks:continue
            tf=placement(pose['r'],pose['t']);local=wire.copy();local.Placement=tf.inverse()*local.Placement
            source=world.rest[pose['name']];gap=query.distance(local,source)
            row=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            if not row['ok']:
                _,points,_=local.distToShape(source);row['world_witness_mm']=[[list(tf.multVec(a)),list(tf.multVec(b))] for a,b in points[:1]]
                c=local.common(source);assert c.isNull() or c.isValid();row['actual_common_mm3']=c.Volume
                row.update(leg_code=pose['code'],stage=pose['stage'],pose_index=pose['pose'])
            checks[key]=row;save()
            if not row['ok']:save('FOUR_WIRE_MOTION_ACTUAL_HOLD');print(result['status'],key,gap,flush=True);return
            if time.monotonic()-tick>220:save('PARTIAL_FOUR_WIRE_MOTION_SAVED');print(result['status'],len(checks),flush=True);return
        result['completed_motion'].append(n);save();print('Wire36 received',n,flush=True)
    save('FOUR_FULL_MTA_WIRES_STATIC_AND36MOTION_RECEIVED_KIT_TOOLS_OPEN')
    print(result['status'],len(checks),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
