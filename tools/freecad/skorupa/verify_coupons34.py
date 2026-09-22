"""Check signed native PETG fit coupons and their independent STL topology."""
import hashlib
import json
import FreeCAD as A
import Mesh
from support34 import OUT

folder = OUT / 'coupons'
doc = A.openDocument(str(folder / 'PETGFit34.FCStd'))
names = ['Seat220', 'Seat221', 'Seat222', 'Journal78', 'Journal79', 'Journal80']
rows = []
for name in names:
    b = doc.getObject(name)
    assert b.Shape.isValid() and len(b.Shape.Solids) == 1 and b.getStatusString() == 'Valid'
    b.Shape.check(True)
    path = folder / (name + '.stl')
    mesh = Mesh.Mesh(str(path))
    assert mesh.isSolid() and mesh.hasNonManifolds() is False and mesh.countComponents() == 1
    assert abs(mesh.Volume - b.Shape.Volume) / b.Shape.Volume < .005
    rows.append(dict(name=name, native_volume_mm3=b.Shape.Volume, mesh_volume_mm3=mesh.Volume,
        closed=True, components=1, nonmanifold=False, facets=mesh.CountFacets,
        stl_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
assert all(o.FullyConstrained for o in doc.Objects if o.TypeId == 'Sketcher::SketchObject')
report = dict(master_sha256=hashlib.sha256((folder / 'PETGFit34.FCStd').read_bytes()).hexdigest(),
    coupons=rows, estimated_solid_PETG_g=sum(r['native_volume_mm3'] for r in rows)*.00127,
    export_linear_deflection_mm=.005, export_angular_deflection_rad=.05,
    physical_fit_verified=False, structural_validation=False, robot_print_release=False)
(folder / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf8', newline='\n')
print(json.dumps(report, indent=2))
