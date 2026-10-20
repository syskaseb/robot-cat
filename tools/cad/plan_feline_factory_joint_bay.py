"""One shared X bay for complete rear joint kits, before another CAD trial.

Project ACTUAL clipped moving material, not contact from bbox overlap.
The conservative intervals provide sufficient X separation for every kit
member; they are not a global impossibility proof when the interval is empty.
Factory source cases stay fixed; only their last straight can lengthen.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from receive_feline_factory_saddle_revision import owner
from receive_feline_global_case_candidates import placement
from feline_atomic_save import save_json


def subtract(intervals,cut):
    lo,hi=cut;result=[]
    for a,b in intervals:
        if hi<=a or lo>=b:result.append((a,b));continue
        if a<lo:result.append((a,lo))
        if hi<b:result.append((hi,b))
    return result


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    f=OUT/'n01-factory-saddles-received.json';r=json.loads(f.read_text());actors=load(r)
    effective={n:s for n,s in parts.items() if n not in r['retired']};effective.update(actors)
    interval=[(-min(r['recipes'][w]['project_factory100_margin_mm'] for w in ('W044','W052'))+1.,0.)]
    initial=interval[:];rows=[];clipped=0
    # Full joint cases/caps/M2/custom-grips AND new full input grip kits.
    moving={n:s for n,s in effective.items() if owner(n) in ('W044','W052') and not n.startswith('Factory:')}
    assert len(moving)==28,len(moving)
    for n,s in moving.items():
        b=s.BoundBox
        roi=Part.makeBox(b.XLength+initial[0][1]-initial[0][0]+2.5,b.YLength+2.5,b.ZLength+2.5,
            A.Vector(b.XMin+initial[0][0]-1.25,b.YMin-1.25,b.ZMin-1.25))
        for pose in world.motion:
            if not roi.BoundBox.intersect(A.BoundBox(*pose['bounds'][0],*pose['bounds'][1])):continue
            leg=world.rest[pose['name']].copy();leg.Placement=placement(pose['r'],pose['t'])*leg.Placement
            cut=leg.common(roi);assert cut.isNull() or cut.isValid();clipped+=1
            for solid in cut.Solids:
                bb=solid.BoundBox;forbidden=[bb.XMin-b.XMax-1.25,bb.XMax-b.XMin+1.25]
                interval=subtract(interval,forbidden)
                rows.append(dict(actor=n,moving=pose['name'],pose=pose['pose'],forbidden_shift_X_mm=forbidden,
                    actual_clipped_solid_volume_mm3=solid.Volume))
    chosen=None
    if interval:
        a,b=max(interval,key=lambda x:x[1]-x[0]);chosen=(a+b)/2
    result=dict(status='COMMON_REAR_JOINT_BAY_CONSTRUCTIVE_X_DOMAIN' if interval else 'COMMON_REAR_JOINT_BAY_NO_CONSERVATIVE_X_DOMAIN_NOT_GLOBAL_IMPOSSIBLE',
        initial_factory_length_shift_X_mm=initial,shared_intervals_X_mm=interval,chosen_whole_kit_shift_X_mm=chosen,
        full_rear_kit_members=list(sorted(moving)),actual_clip_queries=clipped,projection_rows=rows,
        per_actor_bbox_used_for_sufficient_separation_not_contact=True,factory_guide_plus11strip_plus10rework_margin1=True,
        N01_complete=False,physical_pass=False,native_changed=False,static_foreign_parts_factory_extensions_and_roots_still_OPEN=True,
        source_sha256={**pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-factory-rear-joint-bay-plan.json',result)
    print(result['status'],interval,chosen,'clips',clipped,'seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
