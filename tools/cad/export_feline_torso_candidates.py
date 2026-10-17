"""Only qualified candidate geometry exports, not print/assembly approval."""
import json,time
from pathlib import Path
import FreeCAD as A
import MeshPart
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();r=SavedShapes();receipt=json.loads((OUT/'shared-skin-exact.json').read_text())
    access=json.loads((OUT/'skin-access-native.json').read_text());native=ROOT/access['native']
    assert receipt['status']=='SAMPLED_SHARED_SKIN_CLEAR_COWLS_MOUNTS_WIRING_OPEN'
    assert receipt['native_sha256']==access['native_sha256']==sha(native)
    result=dict(status='CANDIDATE_SKIN_EXPORTS_NOT_PRINT_APPROVAL',selected=False,physical_pass=False,
        slicer_run=False,mounts_cowls_service_complete=False,actual_minimum3d_thickness_verified=False,
        print_limit_with_margin_mm=252,parts=[],source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,OUT/'shared-skin-exact.json',Path(__file__))})
    for row in access['parts']:
        s=r.shape(native,row['object']);assert s.isValid() and len(s.Solids)==1
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.12,AngularDeflection=.25,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1,row['object']
        b=mesh.BoundBox;extents=[b.XLength,b.YLength,b.ZLength]
        assert max(extents)<=252,row['object'];mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        target=OUT/(row['object']+'_candidate_x1.stl');mesh.write(str(target))
        result['parts'].append(dict(object=row['object'],closed_stl=True,components=1,measured_mesh_extents_mm=extents,
            stl=target.relative_to(ROOT).as_posix(),sha256=sha(target),print_orientation_and_supports='Phase2 slicer/physical fit gate; normalized assembly axes are not a final print setup'))
    result.update(worker_seconds=round(time.monotonic()-tick,3));(OUT/'torso-candidate-exports.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
