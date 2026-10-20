"""Necessary transverse-wrap collar domain before another retainer edit.

Project actual connected F0 material cut by the COMPLETE top-strap rail.
Every point of a connected solid's X projection is occupied at some Y/Z;
the rail spans all those Y/Z. Thus these are material collisions, not bbox
overlaps. Empty domain rejects this wrap topology only, not all retention.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_plan import box
from plan_feline_mta_body_head_clock import subtract
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-body-head-clock.json';r=json.loads(sf.read_text());actors=load(r)
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    f0=parts['Ref_Material_F0_CP2_0_0'];assert f0.isValid() and f0.Solids
    rows={}
    for code in ('RL','RR'):
        tie=r['body_ties'][code];case=parts[tie['case']];b=case.optimalBoundingBox(False,False)
        start=[(b.XMin+1.25,b.XMax-1.25)]
        rail=box([b.XMin,b.YMin-1.4,b.ZMax+.2],[b.XMax,b.YMax+1.4,b.ZMax+1.4])
        cut=f0.common(rail);assert cut.isNull() or cut.isValid()
        intervals=start[:];projections=[]
        for solid in cut.Solids:
            assert solid.isValid() and solid.Volume>1e-8
            c=solid.optimalBoundingBox(False,False)
            # Clamp to true Boolean clipping planes; optimal bounding box
            # may still contain redundant surface poles outside the cut.
            low=max(b.XMin,c.XMin);high=min(b.XMax,c.XMax)
            blocked=[low-1.25,high+1.25];intervals=subtract(intervals,blocked)
            projections.append(dict(connected_solid_volume_mm3=solid.Volume,occupied_X_mm=[low,high],
                forbidden_collar_centre_X_mm=blocked,actual_Boolean_material_not_bbox_contact=True))
        rows[code]=dict(complete_top_rail_YZ_mm=[[b.YMin-1.4,b.YMax+1.4],[b.ZMax+.2,b.ZMax+1.4]],
            original_collar_domain_X_mm=start,material_collision_free_X_mm=intervals,actual_projections=projections,
            actual_cut_volume_mm3=cut.Volume,head_and_foreign_margin_NOT_yet_applied=True)
    dest=OUT/'n01-MTA-rear-wrap-domain.json';assert not dest.exists()
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],Path(__file__))})
    result=dict(status='TRANSVERSE_REAR_WRAPS_BLOCKED_BY_ACTUAL_F0_NO_COLLAR_RETRY' if all(not v['material_collision_free_X_mm'] for v in rows.values()) else 'NECESSARY_REAR_WRAP_DOMAINS_NOT_COMPLETE_RETENTION',
        source_sha256=pins,rows=rows,selected_parts_changed=False,global_infeasibility_NOT_claimed=True,
        N01_complete=False,native_changed=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result);print(result['status'],rows,result['worker_seconds'],flush=True)


if __name__=='__main__':main()
