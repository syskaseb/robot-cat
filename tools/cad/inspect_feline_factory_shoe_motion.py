"""Read only the eight rejected shoe/motion witnesses, no new layout trial."""
import gzip,json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_two_lane_receive import world_context
from receive_feline_rrp_shared_height import load
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();f=OUT/'n01-factory-inputs-current-received.json';r=json.loads(f.read_text());actors=load(r)
    pf=ROOT/r['pair_rows'];assert sha(pf)==r['pair_rows_sha256'];previous=json.loads(gzip.decompress(pf.read_bytes()))
    world,_=world_context();rows=[]
    for key in r['failures']:
        owner,other=key.split('|motion:');name,pose=other.rsplit(':',1)
        p=next(p for p in world.motion if p['name']==name and str(p['pose'])==pose)
        moving=world.rest[name].copy();moving.Placement=placement(p['r'],p['t'])*moving.Placement
        gap,points,_=actors[owner].distToShape(moving)
        assert abs(gap-previous[key]['gap_mm'])<1e-5,'Wrong coordinate frame is not a witness'
        rows.append(dict(pair=key,gap_mm=gap,witness_mm=[[list(a),list(b)] for a,b in points[:2]],
            shoe_bounds_mm=[[actors[owner].BoundBox.XMin,actors[owner].BoundBox.YMin,actors[owner].BoundBox.ZMin],
                            [actors[owner].BoundBox.XMax,actors[owner].BoundBox.YMax,actors[owner].BoundBox.ZMax]]))
    assert len(rows)==8
    result=dict(status='EIGHT_ACTUAL_MOVING_SHOE_WITNESSES_NO_NEW_GEOMETRY',rows=rows,N01_complete=False,
        source_sha256={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (f,pf,ROOT/r['bundle'],Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-factory-shoe-motion-witnesses.json',result);print(json.dumps(result['rows'],indent=2));print(result['worker_seconds'])


if __name__=='__main__':main()
