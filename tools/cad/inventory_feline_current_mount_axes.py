"""Actual saved current-axis inventory for the NEXT joint load-space plan.

Concave cylindrical surfaces are extracted, not guessed from case bounding
boxes. A saved nominal PCB is labelled nominal, never measured supplier data.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE


def main():
    tick=time.monotonic();reader=SavedShapes();rf=OUT/'motion-receivers-checks.json';receipt=json.loads(rf.read_text())
    native=ROOT/receipt['native'];assert receipt['native_built'] and sha(native)==receipt['native_sha256']
    pf=ROOT/receipt['module_plan'];plan=json.loads(pf.read_text());result=[]
    for g in plan['groups']:
        if g['role'] not in ('Pi4','BUS','MAIN','PWM9685','PWM1608_U1','AUX4092'):continue
        candidates=[]
        for n in g['objects']:
            # Printed U1 anchors are NOT supplier PCB bores. Select the
            # nominal board separately, never classify its anchor recesses.
            if not (g['role']=='BUS' or 'NominalPCB' in n or 'CurrentMainSupplierReference' in n):continue
            s=reader.shape(native,n);b=s.optimalBoundingBox()
            if g['role']=='BUS' and not (b.XLength>25 and b.YLength>30 and .3<b.ZLength<3):continue
            if any(word in n for word in ('Nut','Screw','Band','Washer','Grip','Head')):continue
            cylinders=[]
            for i,f in enumerate(s.Faces):
                surf=f.Surface
                if not isinstance(surf,Part.Cylinder) or not (.9<=surf.Radius<=2.2) or abs(surf.Axis.z)<.999:continue
                box=f.optimalBoundingBox()
                if not (.3<box.ZLength<4):continue
                u0,u1,v0,v1=f.ParameterRange;u=(u0+u1)/2;v=(v0+v1)/2
                point=f.valueAt(u,v);axis=surf.Axis;radial=point-surf.Center;radial=radial-axis*radial.dot(axis)
                if radial.Length<.001 or f.normalAt(u,v).dot(radial/radial.Length)>-.5:continue
                # Full/coplanar split bores may yield two faces; retain all
                # evidence, then group only matching axes/radii.
                cylinders.append(dict(face=i,axis_world_xy_mm=[surf.Center.x,surf.Center.y],diameter_mm=2*surf.Radius,
                    through_z_mm=[box.ZMin,box.ZMax],surface_verified_concave=True))
            if cylinders or 'NominalPCB' in n or 'CurrentMainSupplierReference' in n:
                candidates.append(dict(object=n,reference_kind='PROJECT_NOMINAL_PCB' if 'NominalPCB' in n else 'SAVED_SUPPLIER_REFERENCE_NOT_DELIVERED_MEASUREMENT',
                    actual_saved_cylindrical_faces=cylinders,bounds_are_not_hole_evidence=True))
        unique={}
        for c in candidates:
            for hole in c['actual_saved_cylindrical_faces']:
                key=tuple(round(x,4) for x in (*hole['axis_world_xy_mm'],hole['diameter_mm']))
                unique.setdefault(key,dict(axis_world_xy_mm=hole['axis_world_xy_mm'],diameter_mm=hole['diameter_mm'],source_object=c['object']))
        result.append(dict(role=g['role'],references=candidates,unique_axes=list(unique.values()),count=len(unique),
            mounts_currently_qualified=False,assumption_gate='U1 delivered hole/pad/bearing map remains OPEN' if g['role']=='PWM1608_U1' else 'Saved source/reference only; no new mounting or load qualification'))
    history=BASE/'mounting-checkpoint/manifest.json';historical=json.loads(history.read_text())
    report=dict(status='CURRENT_SAVED_MOUNT_AXIS_INVENTORY_NOT_MOUNT_SELECTION',selected=False,physical_pass=False,
        native_changed=False,groups=result,actual_saved_axis_count=sum(g['count'] for g in result),
        historical_root_rejection=historical['rejected_foundation_reason'],
        prior_free_rail_strategy=historical['changed_foundation'],
        next='Read old root rejection BEFORE another mount plan. Reuse grounded rail-clamp strategy only after reconciling current50groups/all178end records. Bank retention, S0 and routes share the same reserved support volume; no more independently placed columns.',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,rf,pf,history,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'current-mount-axis-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],axes=report['actual_saved_axis_count'],groups=[dict(role=r['role'],count=r['count']) for r in result],seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
