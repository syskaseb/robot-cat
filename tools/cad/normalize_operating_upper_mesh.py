"""Diagnose exact duplicate topology on the same finer mesh; never fill holes.

Only duplicate point/facet removal and normal harmonization are permitted.
The exact coordinate surface set must remain identical to the raw mesh.
"""
import json,time,collections
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_current_harness_interfaces import ROOT,OUT,SHA
from check_main_p0_placement import SavedShapes
from build_remaining_loom_supports import print_orientation
from current_work_guard import check


def stats(mesh):
    vertices,faces=mesh.Topology;edges=collections.Counter();surface=collections.Counter()
    for f in faces:
        surface[tuple(sorted(tuple(vertices[i]) for i in f))]+=1
        for a,b in zip(f,(f[1],f[2],f[0])):edges[tuple(sorted((a,b)))]+=1
    bad=[(e,n) for e,n in edges.items() if n!=2]
    return dict(points=mesh.CountPoints,facets=mesh.CountFacets,closed=mesh.isSolid(),nonmanifolds=mesh.hasNonManifolds(),
        components=mesh.countComponents(),boundary_edges=sum(n==1 for e,n in bad),many_face_edges=sum(n>2 for e,n in bad),
        duplicate_facets=sum(n-1 for n in surface.values()),
        bad_edge_samples=[dict(points=[list(vertices[i]) for i in e],facets=n) for e,n in bad[:20]]),set(surface)


def run():
    check();tick=time.monotonic();folder=OUT/'operating-supports-native';prior_file=folder/'upper-mesh-inspection.json'
    prior=json.loads(prior_file.read_text());native=ROOT/prior['native'];assert SHA(native)==prior['native_sha256']
    assert prior['native_one_solid_BOP0'] and not prior['closed']
    s=SavedShapes().shape(native,prior['native_object']);orientation=print_orientation(s)
    shape=s.copy();shape.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*shape.Placement
    b=shape.BoundBox;shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.02,AngularDeflection=.1,Relative=False)
    before,surface_before=stats(mesh);print('raw mesh topology',json.dumps(before),flush=True)
    mesh.write(str(folder/'UpperMeshRejected.bms'))
    mesh.removeDuplicatedPoints();mesh.removeDuplicatedFacets();mesh.harmonizeNormals()
    after,surface_after=stats(mesh);assert surface_after==surface_before,'Normalization changed actual coordinate surfaces'
    result=dict(native=prior['native'],native_sha256=prior['native_sha256'],before=before,after=after,
        exact_surface_coordinate_set_preserved=True,no_holes_filled=True,no_component_geometry_changed=True,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),prior_file)},
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False)
    if after['closed'] and not after['nonmanifolds'] and after['components']==1:
        f=folder/'UpperCarrier001_normalized_operating_x1.stl';mesh.write(str(f))
        result.update(export=f.relative_to(ROOT).as_posix(),export_sha256=SHA(f),printing=orientation)
    (folder/'upper-mesh-normalization.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
