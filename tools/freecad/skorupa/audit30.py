"""Isolated incremental fit audit: new IMU hardware and shell/deck passages.

The PCB's exact bounding solid proves clearance to unrelated parts without
expensive 55-solid PCB booleans. Own fasteners are checked against individual
actual PCB/component solids. Old-old robot collisions are NOT certified here.
"""
from pathlib import Path
import hashlib,itertools,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v30'
plan=json.loads((OUT/'assembly-plan.json').read_text());cache=OUT/'shape-cache'
assert hashlib.sha256((OUT/plan['cad_filename']).read_bytes()).hexdigest()==plan['source_sha256']
assert json.loads((cache/'index.json').read_text())['source_sha256']==plan['source_sha256']
oldplan=json.loads((ROOT/'hardware/skorupa/v29/assembly-plan.json').read_text())
newnames={r['name'] for r in plan['components']}-{r['name'] for r in oldplan['components']}
assert len(newnames)==12
shapes={}
for row in plan['components']:
    s=Part.Shape();s.read(str(cache/(row['name']+'.brep')))
    assert s.isValid() and s.Solids,row['name'];shapes[row['name']]=s
pcb=shapes['IMU'];b=pcb.BoundBox
envelope=Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin))

def exact(a,b):
    # Per-solid AABB filtering avoids huge compound booleans for catalogue PCBs.
    total=0.
    for sa in a.Solids:
        for sb in b.Solids:
            if sa.BoundBox.intersect(sb.BoundBox):total+=abs(sa.common(sb).Volume)
    return total

hits=[];pairs=0;envelope_proofs=0;slivers=[]
for an,bn in itertools.combinations(sorted(shapes),2):
    if not ({an,bn} & (newnames|{'IMU'})):continue
    a,b=shapes[an],shapes[bn]
    if not a.BoundBox.intersect(b.BoundBox):continue
    pairs+=1
    if 'IMU' in (an,bn) and not ({an,bn} & newnames):
        other=b if an=='IMU' else a
        if exact(envelope,other)<1e-8:envelope_proofs+=1;continue
    v=exact(a,b)
    if v>.01:hits.append(dict(parts=[an,bn],volume_mm3=v))
    elif v>1e-6:slivers.append(dict(parts=[an,bn],volume_mm3=v))
print('Incremental rest pairs',pairs,'hits',hits,flush=True)
master=A.openDocument(str(OUT/'ElectronicsDesign30.FCStd'))
assert hashlib.sha256((OUT/'ElectronicsDesign30.FCStd').read_bytes()).hexdigest()==plan['master_sha256']
sketches=[dict(name=o.Name,fully_constrained=o.FullyConstrained) for o in master.Objects if o.TypeId=='Sketcher::SketchObject']
printed=[];keepouts=[]
for o in master.Objects:
    if o.TypeId!='PartDesign::Body':continue
    if o.DesignRole=='PETG':
        s=o.Shape.copy();s.Placement=o.Placement.inverse()*s.Placement;b=s.BoundBox
        printed.append(dict(name=o.Name,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,local_envelope_mm=[b.XLength,b.YLength,b.ZLength],fits_256_cube=max(b.XLength,b.YLength,b.ZLength)<=256))
    if o.DesignRole=='ClearanceNotPrinted':
        s=o.Shape.copy();bad=[];checked=0
        for n,a in shapes.items():
            if not s.BoundBox.intersect(a.BoundBox):continue
            checked+=1;v=exact(s,a)
            if v>.01:bad.append(dict(part=n,volume_mm3=v))
        keepouts.append(dict(name=o.Name,pairs=checked,hits=bad))
print('Master and cable envelopes checked',flush=True)
contacts=[]
for i,(x,y) in enumerate(plan['imu_mount']['holes_CAD_xy_mm']):
    bottom=Part.makeCylinder(3,.05,A.Vector(x,y,38.47)).cut(Part.makeCylinder(1.2,.05,A.Vector(x,y,38.47)))
    top=Part.makeCylinder(3,.05,A.Vector(x,y,45)).cut(Part.makeCylinder(1.25,.05,A.Vector(x,y,45)))
    axis_probe=Part.makeCylinder(1.15,12,A.Vector(x,y,35))
    board=pcb.Solids[0]
    contacts.append(dict(index=i,hole_CAD_xy_mm=[x,y],post_to_deck_contact_mm2=exact(bottom,shapes['Part__Feature038'])/.05,
        post_to_PCB_contact_mm2=exact(top,board)/.05,
        screw_clearance_interference_mm3=exact(axis_probe,board)+exact(axis_probe,shapes['IMUPost30_%d'%i])+exact(axis_probe,shapes['Part__Feature038']),
        threaded_length_mm=12,nominal_clamped_stack_mm=9.55,nut_height_mm=1.6,nominal_protrusion_mm=.85))
source_parts={}
for n in ['IMU','ShellMounted20','Part__Feature038']:
    old=Part.Shape();old.read(str(ROOT/'hardware/skorupa/v29/shape-cache'/(n+'.brep')))
    source_parts[n]=dict(old_volume_mm3=old.Volume,new_volume_mm3=shapes[n].Volume)
unchanged_names={r['name'] for r in oldplan['components']}-set(source_parts)
byte_identical=[];different_serialization=[]
for n in sorted(unchanged_names):
    a=(ROOT/'hardware/skorupa/v29/shape-cache'/(n+'.brep')).read_bytes();b=(cache/(n+'.brep')).read_bytes()
    (byte_identical if a==b else different_serialization).append(n)
report=dict(source_sha256=plan['source_sha256'],master_sha256=plan['master_sha256'],new_components=12,
    changed_existing=list(source_parts),rest_pairs=pairs,rest_interferences=hits,numerical_slivers_below_001mm3=slivers,
    PCB_envelope_clearance_proofs=envelope_proofs,native_sketches=sketches,printable_master_parts=printed,cable_keepouts=keepouts,
    contacts=contacts,changed_part_volumes=source_parts,unchanged_BRep_byte_identical_count=len(byte_identical),different_BRep_serialization=different_serialization,
    print_release=False,scope=__doc__,limitations=['Cable volume is an assumed local plug/bend reserve, not a routed measured harness.',
    'Assembly with nuts requires removing the deck; whole-robot service sequence remains open.',
    'PCB/magnetic axes and magnetic interference have not been calibrated.',
    'PETG compression, creep, vibration, thermal and strength tests remain open.'])
(OUT/'fit-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(hits=hits,keepouts=keepouts,contacts=contacts,sketches=len(sketches),unconstrained=[o['name'] for o in sketches if not o['fully_constrained']],unchanged_byte_identical=len(byte_identical),different_serialization=different_serialization),indent=2))
assert not hits and all(not r['hits'] for r in keepouts)
assert len(sketches)==6 and all(r['fully_constrained'] for r in sketches)
assert all(r['valid'] and r['solids']==1 and r['fits_256_cube'] for r in printed)
assert all(min(r['post_to_deck_contact_mm2'],r['post_to_PCB_contact_mm2'])>15 and r['screw_clearance_interference_mm3']<1e-6 for r in contacts)
