"""Map the three four-face mesh edges back to actual native feature material."""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_harness_interfaces import ROOT,OUT,SHA
from check_main_p0_placement import SavedShapes
from build_remaining_loom_supports import print_orientation
from current_work_guard import check


def run():
    check();tick=time.monotonic();folder=OUT/'operating-supports-native'
    file=folder/'upper-mesh-normalization.json';p=json.loads(file.read_text());native=ROOT/p['native']
    assert SHA(native)==p['native_sha256'] and p['after']['many_face_edges']==3 and p['after']['boundary_edges']==0
    reader=SavedShapes();whole=reader.shape(native,'UpperCarrier001OperatingCurrent')
    o=print_orientation(whole);rotation=A.Placement(A.Vector(),A.Rotation(*o['rotation_quaternion']))
    placed=whole.copy();placed.Placement=rotation*placed.Placement;b=placed.BoundBox
    transform=A.Placement(A.Vector(-b.XMin,-b.YMin,-b.ZMin),A.Rotation())*rotation
    points=[[list(transform.inverse().multVec(A.Vector(*v))) for v in r['points']] for r in p['after']['bad_edge_samples']]
    print('actual native nonmanifold lines',points,flush=True)
    near=[]
    for name,xml in reader.doc(native).items():
        if not name.startswith(('OperatingPilot','OperatingBank','OperatingCase','SourceRailBoss')):continue
        if xml.find("./Properties/Property[@name='Shape']") is None:continue
        s=reader.shape(native,name);bb=s.BoundBox;touch=[]
        for i,(a,b) in enumerate(points):
            mid=A.Vector(*[(x+y)/2 for x,y in zip(a,b)])
            if not (bb.XMin-.001<=mid.x<=bb.XMax+.001 and bb.YMin-.001<=mid.y<=bb.YMax+.001 and bb.ZMin-.001<=mid.z<=bb.ZMax+.001):continue
            check();gap=s.distToShape(Part.Vertex(mid))[0]
            if gap<1e-4:touch.append(dict(line=i,exact_gap_mm=gap))
        if touch:near.append(dict(object=name,contacts=touch,bounds_mm=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax]))
    assert near
    flat=[p for line in points for p in line]
    low=[round(min(p[i] for p in flat),4) for i in range(3)];high=[round(max(p[i] for p in flat),4) for i in range(3)]
    result=dict(native=p['native'],native_sha256=p['native_sha256'],world_lines_mm=points,native_feature_contacts=near,
        candidate_integral_web_bounds_mm=[x-.8 for x in low]+[x+.8 for x in high],
        basis='One continuous1.6mm manufacturing junction web around the actual collinear four-face seam. Candidate only; full current wire/band/case/tool clearance and native union/mesh required. No holder or cable relocation.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),file,native)},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False)
    (folder/'upper-native-junction-location.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
