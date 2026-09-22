"""Read-only BRep fit audit of v29 additions; run in bundled FreeCAD Python.

Neither whole-robot release nor a continuous collision test. Only new parts
against the retained robot, plus a sampled rigid-tail yaw sweep. Read native
masters separately to verify actual constrained sketches and print envelopes.
"""
from pathlib import Path
import hashlib, itertools, json, math
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v29'
plan=json.loads((OUT/'assembly-plan.json').read_text())
cache=OUT/'shape-cache'
assert hashlib.sha256((OUT/'Kot_v29_OGON_PROTOTYP.FCStd').read_bytes()).hexdigest()==plan['source_sha256']
assert json.loads((cache/'index.json').read_text())['source_sha256']==plan['source_sha256']
oldplan=json.loads((ROOT/'hardware/skorupa/v27/assembly-plan.json').read_text())
oldnames={r['name'] for r in oldplan['components']}
newnames={r['name'] for r in plan['components']} - oldnames
shapes={}
for row in plan['components']:
    s=Part.Shape();s.read(str(cache/(row['name']+'.brep')))
    assert s.isValid() and s.Solids,row['name']
    shapes[row['name']]=s

def interference(a,b):
    if not a.BoundBox.intersect(b.BoundBox): return 0.
    return abs(a.common(b).Volume)

rest=[];tested=0;slivers=[]
for an,bn in itertools.combinations(sorted(shapes),2):
    if an not in newnames and bn not in newnames:continue
    a,b=shapes[an],shapes[bn]
    if not a.BoundBox.intersect(b.BoundBox):continue
    tested+=1;v=interference(a,b)
    if v>.01:rest.append(dict(parts=[an,bn],volume_mm3=v))
    elif v>1e-6:slivers.append(dict(parts=[an,bn],volume_mm3=v))
print('Rest audit',tested,'BRep pairs;',len(rest),'interferences',flush=True)
moving={r['name'] for r in plan['components'] if r['stage']=='Motion_Tail_Yaw'}
static=set(shapes)-moving
poses=[]
for deg in range(-30,31,5):
    p=A.Placement(A.Vector(),A.Rotation(A.Vector(0,0,1),deg),A.Vector(171,-6,91))
    hits=[];pairs=0
    for an in sorted(moving):
        a=shapes[an].copy();a.Placement=p*a.Placement
        for bn in sorted(static):
            b=shapes[bn]
            if not a.BoundBox.intersect(b.BoundBox):continue
            pairs+=1;v=interference(a,b)
            if v>.01:hits.append(dict(parts=[an,bn],volume_mm3=v))
    poses.append(dict(yaw_deg=deg,broadphase_pairs=pairs,interferences=hits))
    print('Yaw',deg,'pairs',pairs,'hits',len(hits),flush=True)

master=A.openDocument(str(OUT/'TailDesign29.FCStd'))
assert hashlib.sha256((OUT/'TailDesign29.FCStd').read_bytes()).hexdigest()==plan['master_sha256']
sketches=[dict(name=o.Name,fully_constrained=o.FullyConstrained,constraints=len(o.Constraints)) for o in master.Objects if o.TypeId=='Sketcher::SketchObject']
parts=[]
for o in master.Objects:
    if o.TypeId!='PartDesign::Body' or o.Name.startswith(('Bolt','Nut')):continue
    s=o.Shape.copy();s.Placement=o.Placement.inverse()*s.Placement
    b=s.BoundBox
    parts.append(dict(name=o.Name,volume_mm3=s.Volume,solid_PETG_g=s.Volume*.00127,valid=s.isValid(),solids=len(s.Solids),local_envelope_mm=[b.XLength,b.YLength,b.ZLength],fits_256_cube=max(b.XLength,b.YLength,b.ZLength)<=256))
print('Native master inspected',flush=True)

# Insertion axis of each existing frame screw, including its nut envelope.
frame=[]
for x in [112,122]:
    for y in [-22.5,22.5]:
        probe=Part.makeCylinder(1,12,A.Vector(x,y,31))
        frame.append(dict(axis_xy=[x,y],interference_frame_mm3=shapes['FrameRear20'].common(probe).Volume,interference_cover_mm3=shapes['Part__Feature038'].common(probe).Volume))

modules=['TailRoot29']+['TailModule29_%02d'%i for i in range(6)]
keyed=[]
for an,bn in zip(modules,modules[1:]):
    keyed.append(dict(parts=[an,bn],minimum_surface_gap_mm=shapes[an].distToShape(shapes[bn])[0],interference_mm3=interference(shapes[an],shapes[bn])))
result=dict(source_sha256=plan['source_sha256'],master_sha256=plan['master_sha256'],new_components=len(newnames),native_sketches=sketches,printable_master_parts=parts,
    rest_brep_pairs=tested,rest_interferences=rest,numerical_slivers_below_001mm3=slivers,yaw_samples=poses,frame_hole_checks=frame,keyed_interfaces=keyed,
    supplier_servo_mount_overlap_mm3=interference(shapes['MG92BCase29'],shapes['MG92BMount29']),
    print_release=False,independent_output_support=False,horn_interface_verified=False,
    scope='New additions vs retained geometry and 13 rigid-tail yaw samples only; old-old collisions and leg sweep not audited here. Nominal fasteners omit threads; nut cylinders conservatively circumscribe hexagons. Geometry fit is not strength, thermal, friction or physical assembly validation.')
(OUT/'fit-audit.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(dict(rest_interferences=rest,sweep_interferences=sum(len(p['interferences']) for p in poses),sketches=len(sketches),unconstrained=[s['name'] for s in sketches if not s['fully_constrained']],not_256=[p['name'] for p in parts if not p['fits_256_cube']]),indent=2))
assert all(s['fully_constrained'] for s in sketches)
assert not rest and not any(p['interferences'] for p in poses)
assert all(p['valid'] and p['solids']==1 and p['fits_256_cube'] for p in parts)
