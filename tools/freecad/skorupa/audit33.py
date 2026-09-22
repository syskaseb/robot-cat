"""Signed v33 head/PCB manufacturing checks, not whole-robot print release.

The front shell and muzzle are now one part. Inherited intersections with
inserts/neck remain OPEN. New geometry must not add a collision. Purchased
board is checked first with a conservative envelope, then exact subsolids only
where needed; never execute thousands of classifications in the GUI thread.
"""
from pathlib import Path
import hashlib,itertools,json
import FreeCAD as A
import Part
from inheritance30 import compare_text

ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'hardware/skorupa/v33'
OLD=ROOT/'hardware/skorupa/v32'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))
plan=read(OUT/'assembly-plan.json');digest=sha(OUT/plan['cad_filename'])
assert digest==plan['source_sha256']==read(OUT/'shape-cache/index.json')['source_sha256']
assert sha(OUT/plan['master_filename'])==plan['master_sha256']
oldplan=read(OLD/'assembly-plan.json')
assert sha(OLD/oldplan['cad_filename'])==oldplan['source_sha256']
assert read(OLD/'shape-cache/index.json')['source_sha256']==oldplan['source_sha256']
master=A.openDocument(str(OUT/plan['master_filename']))
def brep(folder,name):
    s=Part.Shape();s.read(str(folder/'shape-cache'/(name+'.brep')))
    assert s.isValid() and s.Solids,name
    return s
shapes={r['name']:brep(OUT,r['name']) for r in plan['components']}
def world(o):
    s=o.Shape.copy();s.Placement=o.getGlobalPlacement()*o.Placement.inverse()*s.Placement;return s
def exact(a,b):
    total=0.
    for sa in a.Solids:
        for sb in b.Solids:
            if not sa.BoundBox.intersect(sb.BoundBox):continue
            c=sa.common(sb)
            assert c.isNull() or c.isValid(),'Invalid intersection cannot be treated as clearance'
            assert abs(c.Volume)<=min(sa.Volume,sb.Volume)+.01,'Impossible common volume: stop instead of accepting a kernel error'
            total+=abs(c.Volume)
    return total
def envelope(s):
    b=s.BoundBox
    return Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin))
def collision(a,b):
    # A PCB-wide zero intersection is a conservative exclusion. It is NOT a
    # substitute for detailed checking when the envelope is positive.
    if len(a.Solids)>20 and exact(envelope(a),b)<1e-8:return 0.
    if len(b.Solids)>20 and exact(a,envelope(b))<1e-8:return 0.
    return exact(a,b)
sketches=[dict(name=o.Name,fully_constrained=o.FullyConstrained) for o in master.Objects if o.TypeId=='Sketcher::SketchObject']
assert len(sketches)==3 and all(o['fully_constrained'] for o in sketches)
face=master.getObject('HeadFace33');assert face.Shape.isValid() and len(face.Shape.Solids)==1
assert face.Tip.Name=='IntegralMicSupport33_B'
assert all(o.getStatusString()=='Valid' for o in face.Group if o.TypeId.startswith('PartDesign::') and o.TypeId!='PartDesign::Body'), 'Stale feature shape is not a successful recompute'
assert [master.getObject(n).Type for n in ['IntegralPETGFace33','IntegralMicSupport33_A','IntegralMicSupport33_B']]==['Fuse']*3
pocket=master.getObject('NoseNutAndWireAccess33')
assert pocket.TypeId=='PartDesign::Pocket' and pocket.BaseFeature.Name=='HeadShellRecovered33'
assert not pocket.Reversed and abs(pocket.Length.Value-40)<1e-9
assert pocket.Profile[0].Name=='NoseServiceOpening33'
for n,base,tool in [('IntegralPETGFace33','NoseNutAndWireAccess33','MuzzleFusion33'),
                   ('IntegralMicSupport33_A','IntegralPETGFace33','MicSupport33_A'),
                   ('IntegralMicSupport33_B','IntegralMicSupport33_A','MicSupport33_B')]:
    obj=master.getObject(n)
    assert obj.BaseFeature.Name==base and [o.Name for o in obj.Group]==[tool],n

# Strict serialized topology + numeric comparison (also works for the
# preserved defective source; do not Boolean-diff that source against itself).
identity=[]
def seed_local(n):
    s=brep(OLD,n);s.Placement=face.Placement.inverse()*s.Placement;return s
assert master.getObject('MuzzleFusion33').getGlobalPlacement().isSame(face.Placement,1e-9)
for tag,a,b in [('muzzle_source',seed_local('Muzzle'),master.getObject('MuzzleSource32').Shape),
                ('installed_head',face.Shape,shapes['HeadFront']),
                ('installed_pcb',master.getObject('ReSpeaker33').Shape,shapes['Microphones'])]:
    # Compare in the same source frame. Composing world placements can change
    # the serialized Locations table/order without changing the surface; no
    # fuzzy Boolean equality or enlarged numeric tolerance is used here.
    print('Identity starting',tag,flush=True)
    # Cached viewport triangulation is not BRep geometry and can differ after
    # a save. Remove only that cache on disposable copies before comparison.
    comparison=compare_text(a.cleaned().exportBrepToString(),b.cleaned().exportBrepToString())
    identity.append(dict(name=tag,serialization_equivalent=True,
                         absolute_tolerance_mm=1e-9,relative_tolerance=1e-12,**comparison))
    print('Identity',tag,flush=True)

recovered=world(master.getObject('HeadShellRecovered33'))
supports=[world(master.getObject(n)) for n in ['MicSupport33_A','MicSupport33_B']]
added_hits=[];support_contacts=[]
for i,s in enumerate(supports):
    support_contacts.append(dict(index=i,embedded_in_recovered_shell_mm3=exact(s,recovered)))
    for n,b in shapes.items():
        if n=='HeadFront' or not s.BoundBox.intersect(b.BoundBox):continue
        v=collision(s,b)
        if v>.01:added_hits.append(dict(support=i,part=n,volume_mm3=v))
    print('Support tested',i,flush=True)
newnames={n for n in shapes if n.startswith(('MicBolt33_','MicNut33_'))}
assert len(newnames)==4
changed=newnames|{'Microphones'}
hits=[];pairs=0;pcb_head_bound=None
for an,bn in itertools.combinations(sorted(shapes),2):
    if not ({an,bn}&changed):continue
    a,b=shapes[an],shapes[bn]
    if not a.BoundBox.intersect(b.BoundBox):continue
    pairs+=1
    if {an,bn}=={'HeadFront','Microphones'}:
        # The new head is a subset of recovered front + original muzzle + the
        # two supports, as proved by the native subtractive/fuse chain above.
        # Its PCB-wide box necessarily intersects the posts in EMPTY space
        # below the PCB. Splitting this positive broadphase into the original
        # skin and the two simple supports avoids 484 near-empty NURBS cuts.
        bounds=[dict(source=n,overlap_upper_bound_mm3=collision(shapes['Microphones'],s))
                for n,s in [('recovered_front',recovered),('v32_muzzle',brep(OLD,'Muzzle')),
                            ('support_A',supports[0]),('support_B',supports[1])]]
        v=sum(r['overlap_upper_bound_mm3'] for r in bounds)
        pcb_head_bound=dict(method='Conservative union bound: recovered shell minus service pocket, then original muzzle and two supports',sources=bounds,total_upper_bound_mm3=v)
    else:v=collision(a,b)
    if v>.01:hits.append(dict(parts=[an,bn],volume_mm3=v))
    print('New pair',an,bn,v,flush=True)

# These are reported, never relabelled as cleared just because the new joint
# test passes. The proof above limits added material to collision-free ribs.
inherited=[]
for n in ['HeadRear','EarL','EarR','EarInsetL','EarInsetR','EyeRingL','EyeRingR','EyeLensL','EyeLensR','Camera','IrIlluminator','NeckColumn']:
    v=exact(shapes['HeadFront'],shapes[n])
    if v>.01:inherited.append(dict(parts=['HeadFront',n],volume_mm3=v,status='OPEN inherited interface; not print-ready'))
    print('Head interface',n,v,flush=True)

def annulus(x,y,z,height=.05):
    return Part.makeCylinder(2.5,height,A.Vector(x,y,z)).cut(Part.makeCylinder(1.2,height,A.Vector(x,y,z)))
contacts=[];tool_checks=[]
for i,(x,y) in enumerate(plan['microphone_mount']['holes_xy_mm']):
    shaft=Part.makeCylinder(1.02,12,A.Vector(x,y,132))
    contacts.append(dict(index=i,
        support_top_area_mm2=exact(annulus(x,y,139.55),shapes['HeadFront'])/.05,
        pcb_bottom_area_mm2=exact(annulus(x,y,139.6),shapes['Microphones'])/.05,
        shaft_interference_mm3=sum(collision(shaft,shapes[n]) for n in ['HeadFront','Microphones']),
        clamped_stack_mm=9.11,nut_height_mm=1.6,protrusion_mm=1.29))
    probes={
        'bottom_driver':Part.makeCylinder(3.25,6,A.Vector(x,y,124)).fuse(
            Part.makeBox(-120-x,6.5,6.5,A.Vector(x,y-3.25,123.5))),
        'top_wrench':Part.makeBox(-120-x,6,2,A.Vector(x,y-3,141.11))}
    for key,probe in probes.items():
        bad=[]
        # Service on the detached front head, rear shell removed. This is not
        # a claim of assembled-cat access through the unfinished neck.
        for n in ['HeadFront','Microphones','ToF','Nose','Camera','IrIlluminator','EyeRingL','EyeRingR','EarL','EarR']:
            b=shapes[n]
            if not probe.BoundBox.intersect(b.BoundBox):continue
            v=collision(probe,b)
            if v>.01:bad.append(dict(part=n,volume_mm3=v))
        tool_checks.append(dict(index=i,tool=key,blockers=bad,
            before_ear_installation_blockers=[r for r in bad if r['part'] not in ['EarL','EarR']],
            required_absent_parts=[r['part'] for r in bad if r['part'] in ['EarL','EarR']],
            scope='Assembly BEFORE ears are installed, detached front head. Ear attachments unfinished: no assembled-cat service approval. Nominal tool reserve only.'))

pose=A.Placement(A.Vector(*plan['tof_mount']['pcb_base_CAD_mm']),A.Rotation(A.Vector(0,1,0),-90))
nose_access=[]
for i,(x,y) in enumerate(plan['tof_mount']['holes_local_xy_mm']):
    probe=Part.makeCylinder(3.25,40,A.Vector(x,y,-45.6));probe.Placement=pose*probe.Placement
    nose_access.append(dict(index=i,tool_diameter_mm=6.5,depth_mm=40,head_obstruction_mm3=exact(probe,shapes['HeadFront']),
                            scope='Front-head subassembly off robot; neck mechanism not certified'))
optics=A.openDocument(str(OLD/'OpticsDesign32.FCStd'))
optical=[]
for n in ['OpticalReserve32','ToFWireReserve32']:
    probe=optics.getObject(n).Shape
    optical.append(dict(name=n,head_obstruction_mm3=exact(probe,shapes['HeadFront'])))
b=face.Shape.BoundBox
try:face.Shape.check(True);bop_errors=[]
except ValueError as exc:bop_errors=str(exc).splitlines()
mesh=read(OUT/'mesh-proof.json');assert mesh['master_sha256']==plan['master_sha256']
assert mesh['head_manifold'] and mesh['required_clearance_passed']
report=dict(source_sha256=digest,master_sha256=plan['master_sha256'],scope=__doc__,print_release=False,
    obsolete_head_source_note='HeadFrontSource32 is a historical feature, NOT an exact preserved BRep: failed OCCT operations altered tolerance metadata. The original v32 CAD/cache is checksummed and untouched; construction uses the separately recovered shell.',
    assembly_service_validated=False,bop_check_messages=bop_errors,mesh_proof_sha256=sha(OUT/'mesh-proof.json'),
    new_components=4,removed_components=['Muzzle'],changed_existing=['HeadFront','Microphones'],
    new_pair_count=pairs,new_interferences=hits,added_support_interferences=added_hits,pcb_head_clearance_bound=pcb_head_bound,
    inherited_head_interferences=inherited,native_sketches=sketches,identity_checks=identity,
    support_contacts=support_contacts,pcb_contacts=contacts,nose_access=nose_access,tool_access=tool_checks,optical_reserves=optical,
    printable_face=dict(valid=True,solids=1,volume_mm3=face.Shape.Volume,
        conservative_bounds_mm=[b.XLength,b.YLength,b.ZLength],fits_256_cube=max(b.XLength,b.YLength,b.ZLength)<=256),
    limitations=['Reference PCB revision must be checked against the physical board; wiki dimensions differ.',
        'USB/audio plugs, full wiring, microphone acoustic ducts and XIAO are not validated.',
        'Fastener envelopes nominal, torque/creep/printing orientation require PETG coupons.',
        'Native test leaves head locked; missing head axes and tail support are not cleared.'])
(OUT/'fit-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
print(json.dumps(report,indent=2),flush=True)
assert not hits and not added_hits
assert all(r['embedded_in_recovered_shell_mm3']>20 for r in support_contacts)
assert all(min(r['support_top_area_mm2'],r['pcb_bottom_area_mm2'])>8 and r['shaft_interference_mm3']<.01 for r in contacts)
assert all(r['head_obstruction_mm3']<.01 for r in nose_access+optical)
assert report['printable_face']['fits_256_cube']
# Assembly sequence is explicit; do not erase blocked fully-assembled access.
assert all(not r['before_ear_installation_blockers'] for r in tool_checks)
assert {n for r in tool_checks for n in r['required_absent_parts']}=={'EarL'}
