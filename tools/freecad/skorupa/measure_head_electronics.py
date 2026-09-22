"""Measure Seeed's reference STEP and screen two envelopes; never edit the cat.

The manufacturer's wiki dimensions disagree with this STEP. Results are
reference-only and do not approve the part revision, mounts or acoustics.
Run with the bundled FreeCAD Python, after cache32.py.
"""
from pathlib import Path
import hashlib,json,math
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/reference/head-electronics-2026-09-22'
SOURCE=OUT/'ReSpeakerLitev1.1.step'
CAD=ROOT/'hardware/skorupa/v32'
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert source_sha=='4a9585d0177dbcfc0efa7d740c8731d0848484c89ee47e4a0cc919afd65d1528'
plan=json.loads((CAD/'assembly-plan.json').read_text())
cad_sha=hashlib.sha256((CAD/plan['cad_filename']).read_bytes()).hexdigest()
assert cad_sha==plan['source_sha256']==json.loads((CAD/'shape-cache/index.json').read_text())['source_sha256']
shape=Part.Shape();shape.read(str(SOURCE));assert shape.isValid() and len(shape.Solids)==484
pcb=max(shape.Solids,key=lambda s:s.Volume)
assert abs(pcb.BoundBox.ZLength-1.51)<1e-6

def bbox(s):
    b=s.optimalBoundingBox()
    return dict(min_mm=[b.XMin,b.YMin,b.ZMin],max_mm=[b.XMax,b.YMax,b.ZMax],
                size_mm=[b.XLength,b.YLength,b.ZLength])

# A full cylindrical wall of diameter2.2, through the laminate; corner
# fillets and connector solder holes are not mistaken for mounting holes.
holes=[]
for i,f in enumerate(pcb.Faces):
    if not isinstance(f.Surface,Part.Cylinder):continue
    r=f.Surface.Radius
    if abs(r-1.1)>1e-6:continue
    assert abs(f.Area-2*math.pi*r*1.51)<1e-5
    assert abs(abs(f.Surface.Axis.z)-1)<1e-9
    holes.append(dict(face_index=i,diameter_mm=2*r,
                      centre_on_bottom_mm=[f.Surface.Center.x,f.Surface.Center.y,0]))
assert len(holes)==2
old=Part.Shape();old.read(str(CAD/'shape-cache/Microphones.brep'))
oldbox=old.optimalBoundingBox();target=A.Vector((oldbox.XMin+oldbox.XMax)/2,
                                              (oldbox.YMin+oldbox.YMax)/2,139.6)
pcbbox=pcb.optimalBoundingBox();datum=A.Vector((pcbbox.XMin+pcbbox.XMax)/2,
                                            (pcbbox.YMin+pcbbox.YMax)/2,0)
targets={}
for row in plan['components']:
    if row['name']=='Microphones':continue
    s=Part.Shape();s.read(str(CAD/'shape-cache'/(row['name']+'.brep')))
    targets[row['name']]=s

cases=[]
for angle in (90,-90):
    rotation=A.Rotation(A.Vector(0,0,1),angle)
    pose=A.Placement(target-rotation.multVec(datum),rotation)
    moved=shape.copy();moved.Placement=pose*moved.Placement
    bounds=moved.optimalBoundingBox()
    envelope=Part.makeBox(bounds.XLength,bounds.YLength,bounds.ZLength,
                         A.Vector(bounds.XMin,bounds.YMin,bounds.ZMin))
    hits=[];tested=0
    for name,other in targets.items():
        if not envelope.BoundBox.intersect(other.optimalBoundingBox()):continue
        volume=0.;solid_pairs=0
        for right in other.Solids:
            if not envelope.BoundBox.intersect(right.optimalBoundingBox()):continue
            common=envelope.common(right);assert common.isNull() or common.isValid(),name
            volume+=abs(common.Volume);solid_pairs+=1
        tested+=solid_pairs
        if volume>.01:hits.append(dict(part=name,envelope_intersection_mm3=volume,
                                      actual_electronic_material_collision_confirmed=False))
        print('Envelope',angle,name,volume,flush=True)
    row=dict(rotation_z_deg=angle,base_mm=list(pose.Base),pcb_datum_world_mm=list(target),
             envelope=bbox(moved),mounting_centres_world_mm=[list(pose.multVec(A.Vector(*h['centre_on_bottom_mm']))) for h in holes],
             envelope_solid_pairs=tested,potential_interferences=hits,
             method='Exact CAD vs conservative whole-STEP AABB, NOT vs 484 electronic solids. Positive hit means unresolved, not a proven material collision.')
    cases.append(row);print('POSE',angle,json.dumps(row),flush=True)

report=dict(reference_only=True,integrated_into_cat=False,mounts_approved=False,
            step_sha256=source_sha,cat_sha256=cad_sha,solid_count=484,valid=True,
            pcb=bbox(pcb),complete_step=bbox(shape),wiki_dimensions_mm=[86,35],
            dimensional_discrepancy_unresolved=True,mounting_holes=holes,
            old_microphones_envelope=bbox(old),cases=cases,
            caveats=['Do not scale the STEP to match wiki dimensions.',
                     '484-solid exact fit probe was stopped for cost; this is conservative envelope screening, not completed detailed fit.',
                     'Only two candidate mounting holes; verify actual supplied hardware revision.',
                     'No plugged USB/audio cable, XIAO board or acoustic channels included in fit test.',
                     'Not a mass or thermal model; electronic CAD solids are not all homogeneous PETG.',
                     'No robot document or assembly joint was changed.'])
(OUT/'measurements.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2),flush=True)
