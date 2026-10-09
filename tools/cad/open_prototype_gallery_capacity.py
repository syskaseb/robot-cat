"""Determine available whole-gallery height, not another scalar CAD trial.

Frozen footprint and22mm upright615 reservation inside actual saved torso.
Bisection solves one capacity boundary; no variant models or wire acceptance.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, time
import FreeCAD as A
import Part
from open_prototype_entry_chambers import CONTEXT
from open_prototype_wiring_endpoints import BASE, ROOT, sha, read

OUT=BASE/'wiring-checkpoint';DEST=OUT/'rear-gallery-height-capacity.json'

def main():
    tick=time.monotonic();assert not DEST.exists(),'Receive capacity result, no unchanged query'
    p=read(OUT/'source-group-approach-plan.json');row=next(r for r in p['stations'] if r['role']=='P_REAR')
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in (CONTEXT,OUT/'source-group-approach-plan.json',Path(__file__))}
    doc=A.openDocument(str(CONTEXT));result=dict(status='CAPACITY_ONLY_NOT_ROUTE_ACCEPTANCE',source_sha256=pins,
        errors=[],selected=False,stage_completed=False,physical_pass=False)
    try:
        torso=doc.TorsoEnvelope.Shape;assert torso.isValid() and len(torso.Solids)==1
        x,y,_=row['centre_mm'];size=row['size_mm'];dx,dy,dz=size
        def outside(z):
            s=Part.makeBox(dx,dy,dz,A.Vector(x-dx/2,y-dy/2,z-dz/2))
            cut=s.cut(torso);assert cut.isValid()
            return cut.Volume
        low,high=143,146
        assert outside(low)<=1e-6 and outside(high)>1e-6,'Capacity boundary must be bracketed by actual geometry'
        iterations=0
        while high-low>0.001:
            mid=(low+high)/2;iterations+=1
            if outside(mid)>1e-6:high=mid
            else:low=mid
        # A whole-case0.5mm vertical allocation margin, not a claim about
        # delivered casing tolerance or a globally selected mounting level.
        proposed=low-.5
        result.update(case_footprint_xy_mm=[x,y],size_mm=size,maximum_centre_z_mm_lower_bound=low,
            rejected_centre_z_mm_upper_bound=high,capacity_interval_mm=high-low,
            design_vertical_margin_mm=.5,proposed_centre_z_mm=proposed,
            proposed_entry_z_mm=proposed-11,proposed_outside_volume_mm3=outside(proposed),
            query_iterations=iterations,all_four_input_routes_and_grips_require_joint_rebind=True)
    except Exception as exc:result['errors'].append(str(exc));raise
    finally:
        A.closeDocument(doc.Name)
        assert all(sha(ROOT/n)==h for n,h in pins.items())
        result.update(worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result),flush=True)

if __name__=='__main__':main()
