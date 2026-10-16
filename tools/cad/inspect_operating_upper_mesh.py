"""Inspect the rejected STL on unchanged valid native Upper, no hole filling."""
import json,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_current_harness_interfaces import ROOT,OUT,SHA
from check_main_p0_placement import SavedShapes
from build_remaining_loom_supports import print_orientation
from current_work_guard import check


def run():
    check();tick=time.monotonic();folder=OUT/'operating-supports-native';file=folder/'manifest.json'
    p=json.loads(file.read_text());r=next(r for r in p['parts'] if r['part']=='UpperCarrier001');native=ROOT/r['native']
    model=next(m for m in p['models'] if m['path']==r['native']);assert SHA(native)==model['sha256']
    s=SavedShapes().shape(native,r['object']);assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    orientation=print_orientation(s);assert orientation['fits_with_5mm_brim']
    shape=s.copy();shape.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*shape.Placement
    b=shape.BoundBox;shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
    print('unchanged Upper BRep valid; finer tessellation only',flush=True)
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
    result=dict(native=r['native'],native_sha256=SHA(native),native_object=r['object'],native_one_solid_BOP0=True,
        linear_deflection_mm=.02,angular_deflection_rad=.1,points=mesh.CountPoints,facets=mesh.CountFacets,
        closed=mesh.isSolid(),nonmanifolds=mesh.hasNonManifolds(),components=mesh.countComponents(),
        available_mesh_seam_methods=[n for n in dir(mesh) if any(q in n.lower() for q in ('duplicat','merge','normal','topolog','solid','check'))],
        source_sha256={Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False)
    if result['closed'] and not result['nonmanifolds'] and result['components']==1:
        f=folder/'UpperCarrier001_fine_operating_x1.stl';mesh.write(str(f))
        result.update(export=f.relative_to(ROOT).as_posix(),export_sha256=SHA(f),printing=orientation)
    (folder/'upper-mesh-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
