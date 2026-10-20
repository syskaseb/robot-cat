"""Receive one real saved motion witness per failed wire, not another sweep."""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_two_lane_receive import world_context
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();source=OUT/'n01-MTA-four-fans-received.json';r=json.loads(source.read_text())
    assert r['status']!='RUNNING_MTA_FOUR_FAN_MOTION','Receive active worker first'
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    assert sha(ROOT/r['pair_rows'])==r['pair_rows_sha256']
    rows=json.loads(gzip.decompress((ROOT/r['pair_rows']).read_bytes()));actors=load(r);world,_=world_context()
    witnesses=[]
    for n in r['completed_motion']:
        failures=[k for k in r['failures'] if k.startswith(n+'|motion:')]
        if not failures:continue
        key=min(failures,key=lambda k:rows[k]['gap_mm']);_,suffix=key.split('|motion:');name,pose=suffix.rsplit(':',1)
        rec=next(p for p in world.motion if p['name']==name and p['pose']==int(pose))
        tf=placement(rec['r'],rec['t']);a=actors[n].copy();a.Placement=tf.inverse()*a.Placement;b=world.rest[name]
        gap,pts,_=a.distToShape(b)
        c=a.common(b);assert c.isNull() or c.isValid()
        bb=b.BoundBox
        witnesses.append(dict(pair=key,code=rec['code'],stage=rec['stage'],pose=rec['pose'],
            actual_gap_mm=gap,actual_overlap_mm3=c.Volume,
            world_contact_points_mm=[[list(tf.multVec(x)),list(tf.multVec(y))] for x,y in pts[:2]],
            actual_rest_part_bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],
            motion_candidate_bounds_NOT_contact_proof=[list(v) for v in rec['bounds']]))
    result=dict(status='SAVED_REAL_MTA_MOTION_WITNESSES',source=source.relative_to(ROOT).as_posix(),
        source_sha256=sha(source),pair_rows_sha256=r['pair_rows_sha256'],witnesses=witnesses,
        worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,native_changed=False)
    save_json(OUT/'n01-MTA-real-motion-contacts.json',result)
    print(json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
