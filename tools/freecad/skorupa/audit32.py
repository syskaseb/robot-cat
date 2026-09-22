"""v32 optical envelope and local mounting audit, not complete head clearance.

Inherited muzzle/head overlaps are measured and retained as OPEN issues.
Only new/additional intersections fail this incremental checkpoint.
"""
from pathlib import Path
import hashlib,itertools,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v32';CACHE=OUT/'shape-cache'
plan=json.loads((OUT/'assembly-plan.json').read_text())
assert hashlib.sha256((OUT/plan['cad_filename']).read_bytes()).hexdigest()==plan['source_sha256']
assert json.loads((CACHE/'index.json').read_text())['source_sha256']==plan['source_sha256']
master=A.openDocument(str(OUT/plan['master_filename']))
assert hashlib.sha256((OUT/plan['master_filename']).read_bytes()).hexdigest()==plan['master_sha256']
pose=A.Placement(A.Vector(*plan['tof_mount']['pcb_base_CAD_mm']),A.Rotation(A.Vector(0,1,0),-90))
assert all(master.getObject(n).Placement.Rotation.isSame(pose.Rotation,1e-9) for n in ['Muzzle32','Nose32','Part__Feature','ToFRearSpacer32','ToFRearSpacer003','OpticalReserve32','ToFWireReserve32','HeadFrontCable32'])
shapes={}
for row in plan['components']:
    s=Part.Shape();s.read(str(CACHE/(row['name']+'.brep')))
    assert s.isValid() and s.Solids,row['name'];shapes[row['name']]=s
newnames={n for n in shapes if n.startswith(('ToFSpacer32_','ToFBolt32_','ToFNut32_'))};assert len(newnames)==6
changed=newnames|{'ToF','Nose','Muzzle','HeadFront'}
def exact(a,b):
    result=0.
    for sa in a.Solids:
        for sb in b.Solids:
            if not sa.BoundBox.intersect(sb.BoundBox):continue
            c=sa.common(sb);assert c.isNull() or c.isValid(),'Invalid intersection; do not interpret its volume'
            result+=abs(c.Volume)
    return result
oldshapes={};added={}
for n in ['Muzzle','HeadFront']:
    s=Part.Shape();s.read(str(ROOT/'hardware/skorupa/v31/shape-cache'/(n+'.brep')))
    oldshapes[n]=s
# A direct new-head minus old-head gives an INVALID OCC difference for these
# near-coincident trimmed surfaces (even with fuzz). Do not use that volume.
# Prove the source and baked result match, and inspect the sole native Pocket:
# it can only remove material from the verified original front shell.
head=master.getObject('HeadFrontCable32');tip=head.Tip;base=master.getObject('HeadFrontBase32')
assert {o.Name for o in head.Group}=={'HeadFrontBase32','ToFWireSlot32','ToFCablePassage32'}
assert tip.TypeId=='PartDesign::Pocket' and tip.BaseFeature==base and tip.Profile[0].Name=='ToFWireSlot32'
assert not tip.Reversed and abs(tip.Length.Value-14)<1e-9 and tip.getStatusString()=='Valid'
base_world=base.Shape.copy();base_world.Placement=head.Placement*base_world.Placement
identity_checks=[]
for tag,a,b in [('original_to_import',oldshapes['HeadFront'],base_world),('master_to_baked',head.Shape,shapes['HeadFront'])]:
    for left,right in [(a,b),(b,a)]:
        delta=left.cut(right,1e-5)
        assert delta.isNull() or delta.isValid(),'Invalid equality difference'
        assert not delta.Solids and abs(delta.Volume)<1e-8,'Changed source/result geometry'
        identity_checks.append(dict(check=tag,valid=True,residual_volume_mm3=delta.Volume,solids=len(delta.Solids)))
head_proof=dict(method='Verified original base and baked result by bidirectional valid fuzzy differences, plus exactly one native subtractive Pocket; therefore no added head material.',
    equality_tolerance_mm=1e-5,checks=identity_checks,feature=tip.Name,depth_mm=14,
    original_volume_mm3=oldshapes['HeadFront'].Volume,result_volume_mm3=head.Shape.Volume,
    direct_new_minus_old_reliable=False)
added['Muzzle']=shapes['Muzzle'].cut(oldshapes['Muzzle'])
assert added['Muzzle'].isNull() or added['Muzzle'].isValid()
hits=[];inherited=[];pairs=0
for an,bn in itertools.combinations(sorted(shapes),2):
    if not ({an,bn}&changed):continue
    a,b=shapes[an],shapes[bn]
    if not a.BoundBox.intersect(b.BoundBox):continue
    pairs+=1;v=exact(a,b)
    if v>.01:
        row=dict(parts=[an,bn],volume_mm3=v)
        if {an,bn}&set(oldshapes) and not ({an,bn}&(changed-set(oldshapes))):
            previous=exact(oldshapes.get(an,a),oldshapes.get(bn,b))
            extra=sum(exact(added[n],shapes[other]) for n,other in [(an,bn),(bn,an)] if n in added)
            row.update(previous_overlap_mm3=previous,added_material_interference_mm3=extra)
            if 'HeadFront' in (an,bn):row['head_material_evidence']='headfront_subtractive_proof (native Pocket), not invalid coincident difference volume'
            if row['previous_overlap_mm3']>.01 and row['added_material_interference_mm3']<.01:
                row['status']='OPEN inherited head interference, not cleared by v32';inherited.append(row)
            else:hits.append(row)
        else:hits.append(row)
    if pairs%10==0:print('Pairs',pairs,'new hits',hits,'inherited',len(inherited),flush=True)
keepouts=[]
for name in ['OpticalReserve32','ToFWireReserve32']:
    a=master.getObject(name).Shape;bad=[]
    for n,b in shapes.items():
        if n=='ToF' and name=='OpticalReserve32':continue
        if not a.BoundBox.intersect(b.BoundBox):continue
        v=exact(a,b)
        if v>.01:bad.append(dict(part=n,volume_mm3=v))
    keepouts.append(dict(name=name,hits=bad))
    print('Keepout',name,bad,flush=True)
def world(s):s.Placement=pose*s.Placement;return s
contacts=[];tools=[]
for i,(x,y) in enumerate(plan['tof_mount']['holes_local_xy_mm']):
    def ring(z):return world(Part.makeCylinder(2.5,.05,A.Vector(x,y,z)).cut(Part.makeCylinder(1.2,.05,A.Vector(x,y,z))))
    shaft=world(Part.makeCylinder(1.03,13,A.Vector(x,y,-7)))
    contacts.append(dict(index=i,
        muzzle_to_PCB_support_mm2=exact(ring(1.016),shapes['Muzzle'])/.05,
        PCB_front_annulus_mm2=exact(ring(.966),shapes['ToF'])/.05,
        PCB_rear_annulus_mm2=exact(ring(0),shapes['ToF'])/.05,
        rear_spacer_PCB_contact_mm2=exact(ring(-.05),shapes['ToFSpacer32_%d'%i])/.05,
        nose_to_muzzle_contact_mm2=exact(ring(2.95),shapes['Muzzle'])/.05,
        nose_support_annulus_mm2=exact(ring(3),shapes['Nose'])/.05,
        shaft_interference_mm3=sum(exact(shaft,shapes[n]) for n in ['Nose','Muzzle','ToF','ToFSpacer32_%d'%i]),
        clamped_stack_mm=9.5,screw_length_mm=12,nut_height_mm=1.6,protrusion_mm=.9))
    probe=world(Part.makeCylinder(2,30,A.Vector(x,y,7.5)));bad=[]
    for n,b in shapes.items():
        if n=='ToFBolt32_%d'%i or not probe.BoundBox.intersect(b.BoundBox):continue
        v=exact(probe,b)
        if v>.01:bad.append(dict(part=n,volume_mm3=v))
    tools.append(dict(index=i,front_driver_radius_mm=2,length_mm=30,blockers=bad))
printed=[]
for o in master.Objects:
    if o.TypeId=='PartDesign::Body' and o.DesignRole=='PETG':
        s=o.Shape.copy();s.Placement=o.Placement.inverse()*s.Placement;b=s.optimalBoundingBox()
        printed.append(dict(name=o.Name,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,
            local_envelope_mm=[b.XLength,b.YLength,b.ZLength],fits_256_cube=max(b.XLength,b.YLength,b.ZLength)<=256))
sketches=[dict(name=o.Name,fully_constrained=o.FullyConstrained) for o in master.Objects if o.TypeId=='Sketcher::SketchObject']
report=dict(source_sha256=plan['source_sha256'],master_sha256=plan['master_sha256'],new_components=6,changed_existing=['Muzzle','Nose','ToF','HeadFront'],
    rest_pairs=pairs,new_rest_interferences=hits,inherited_head_interferences=inherited,keepouts=keepouts,contacts=contacts,
    headfront_subtractive_proof=head_proof,
    tool_access=tools,native_sketches=sketches,printable_master_parts=printed,print_release=False,full_head_collision_clearance=False,
    scope=__doc__,limitations=['45 degree typical FOV and nominal package bounds, not calibrated receiver/emitter ray tracing; crosstalk, reflectance, alignment and range require a real test.',
    'No protective cover. Do not assume PETG transmits IR; remove manufacturer protective liner before use. No laser optics altered.',
    'Direct soldered wires; local reserve is not full wiring or strain relief. Nut access requires removed muzzle.',
    'M2 head/nut dimensions nominal; clamp torque, board bending, tolerances and PETG printing orientation unvalidated.',
    'Muzzle-to-head attachment remains TEMPORARY; measured inherited head interferences remain OPEN.'])
(OUT/'fit-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ('scope','limitations')},indent=2))
assert not hits and all(not r['hits'] for r in keepouts)
assert len(sketches)==7 and all(r['fully_constrained'] for r in sketches)
assert all(r['valid'] and r['solids']==1 and r['fits_256_cube'] for r in printed)
assert all(min(r[k] for k in ['muzzle_to_PCB_support_mm2','PCB_front_annulus_mm2','PCB_rear_annulus_mm2','rear_spacer_PCB_contact_mm2','nose_to_muzzle_contact_mm2','nose_support_annulus_mm2'])>10 and r['shaft_interference_mm3']<1e-6 for r in contacts)
assert all(not r['blockers'] for r in tools)
