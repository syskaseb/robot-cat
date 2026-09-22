"""Incremental v31 BRep fit, clamp stack, terminal pins and service probes.

Does not certify old-old collisions, full gait, thermal behavior or print fit.
Tool access probes are provisional and reported even when obstructed.
"""
from pathlib import Path
import hashlib,itertools,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v31';CACHE=OUT/'shape-cache'
plan=json.loads((OUT/'assembly-plan.json').read_text())
assert hashlib.sha256((OUT/plan['cad_filename']).read_bytes()).hexdigest()==plan['source_sha256']
assert json.loads((CACHE/'index.json').read_text())['source_sha256']==plan['source_sha256']
oldplan=json.loads((ROOT/'hardware/skorupa/v30/assembly-plan.json').read_text())
newnames={r['name'] for r in plan['components']}-{r['name'] for r in oldplan['components']}
assert len(newnames)==16
shapes={}
for row in plan['components']:
    s=Part.Shape();s.read(str(CACHE/(row['name']+'.brep')));assert s.isValid() and s.Solids,row['name'];shapes[row['name']]=s

def exact(a,b):
    return sum(abs(sa.common(sb).Volume) for sa in a.Solids for sb in b.Solids if sa.BoundBox.intersect(sb.BoundBox))

pcb=shapes['Pololu'];b=pcb.BoundBox
envelope=Part.makeBox(b.XLength,b.YLength,b.ZLength,A.Vector(b.XMin,b.YMin,b.ZMin))
hits=[];pairs=0;proofs=0
for an,bn in itertools.combinations(sorted(shapes),2):
    if not ({an,bn}&(newnames|{'Pololu'})):continue
    a,b=shapes[an],shapes[bn]
    if not a.BoundBox.intersect(b.BoundBox):continue
    pairs+=1
    if 'Pololu' in (an,bn) and not ({an,bn}&newnames):
        other=b if an=='Pololu' else a
        if exact(envelope,other)<1e-8:proofs+=1;continue
    volume=exact(a,b)
    if volume>.01:hits.append(dict(parts=[an,bn],volume_mm3=volume))
    if pairs%10==0:print('Pairs',pairs,'hits',hits,flush=True)
print('Fit pairs complete',pairs,flush=True)
master=A.openDocument(str(OUT/'PowerDesign31.FCStd'))
assert hashlib.sha256((OUT/'PowerDesign31.FCStd').read_bytes()).hexdigest()==plan['master_sha256']
sketches=[dict(name=o.Name,fully_constrained=o.FullyConstrained) for o in master.Objects if o.TypeId=='Sketcher::SketchObject']
printed=[];keepouts=[]
for o in master.Objects:
    if o.TypeId!='PartDesign::Body':continue
    if o.DesignRole=='PETG':
        s=o.Shape.copy();s.Placement=o.Placement.inverse()*s.Placement;b=s.BoundBox
        printed.append(dict(name=o.Name,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,local_envelope_mm=[b.XLength,b.YLength,b.ZLength],fits_256_cube=max(b.XLength,b.YLength,b.ZLength)<=256))
    if o.DesignRole=='ClearanceNotPrinted':
        bad=[];s=o.Shape
        for n,b in shapes.items():
            if s.BoundBox.intersect(b.BoundBox):
                v=exact(s,b)
                if v>.01:bad.append(dict(part=n,volume_mm3=v))
        keepouts.append(dict(name=o.Name,hits=bad))
contacts=[]
for i,(x,y) in enumerate(plan['power_mount']['holes_CAD_xy_mm']):
    z=38.52 if i<2 else 44;support='Part__Feature038' if i<2 else 'TailBridge29'
    def ring(z0,inner=1.2):return Part.makeCylinder(3,.05,A.Vector(x,y,z0)).cut(Part.makeCylinder(inner,.05,A.Vector(x,y,z0)))
    probe=Part.makeCylinder(1.03,21,A.Vector(x,y,34))
    members=['Pololu','PowerPost31_%d'%i,'Part__Feature038']
    if i>=2:members+=['TailBridge29','PowerGapSpacer31_%d'%i]
    row=dict(index=i,post_to_support_mm2=exact(ring(z-.05),shapes[support])/.05,
        post_to_PCB_mm2=exact(ring(52),pcb)/.05,
        shaft_clearance_interference_mm3=sum(exact(probe,shapes[n]) for n in members),
        screw_length_mm=19,clamped_stack_mm=16.5548,nut_height_mm=1.6,protrusion_mm=.8452)
    if i>=2:
        row['gap_spacer_to_deck_mm2']=exact(ring(38.47),shapes['Part__Feature038'])/.05
        row['gap_spacer_to_bridge_mm2']=exact(ring(41),shapes['TailBridge29'])/.05
    contacts.append(row);print('Contact',i,'done',flush=True)
pins=[];tools=[]
for x in [88.04,123.6]:
    for y in [5.700005,10.700005]:
        pin=Part.makeCylinder(.5,4,A.Vector(x,y,49.5748));pins.append(dict(axis_CAD_xy_mm=[x,y],PCB_interference_mm3=exact(pin,pcb)))
        # Straight vertical driver shaft only, excluding its own terminal.
        shaft=Part.makeCylinder(2,30,A.Vector(x,y,63.5748));blockers=[]
        for n,b in shapes.items():
            if n.startswith('PowerTerminal31_') or not shaft.BoundBox.intersect(b.BoundBox):continue
            v=exact(shaft,b)
            if v>.01:blockers.append(dict(part=n,volume_mm3=v))
        tools.append(dict(axis_CAD_xy_mm=[x,y],driver_radius_mm=2,driver_length_mm=30,blockers=blockers))
report=dict(source_sha256=plan['source_sha256'],master_sha256=plan['master_sha256'],new_components=16,
    changed_existing=['Pololu','Part__Feature038','ShellMounted20','TailBridge29'],rest_pairs=pairs,rest_interferences=hits,
    PCB_envelope_clearance_proofs=proofs,native_sketches=sketches,printable_master_parts=printed,cable_keepouts=keepouts,
    contacts=contacts,terminal_pins=pins,terminal_tool_access=tools,print_release=False,scope=__doc__,
    limitations=['Two terminal outer/pin envelopes from vendor drawing, not detailed clamps or solder fillets.',
    'Local wire reserve, not complete harness or strain relief.',
    'Vertical screwdriver route blocked by overhead distribution envelope where reported; assemble/remove overhead module first. Actual distribution choice remains unresolved.',
    'PCB/terminal temperatures, PETG creep, torque and board strain unverified. Main regulator only; AUX unchanged.'])
(OUT/'fit-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(pairs=pairs,hits=hits,keepouts=keepouts,contacts=contacts,pins=pins,tool_access=tools,sketches=len(sketches)),indent=2))
assert not hits and all(not r['hits'] for r in keepouts)
assert len(sketches)==9 and all(r['fully_constrained'] for r in sketches)
assert all(r['valid'] and r['solids']==1 and r['fits_256_cube'] for r in printed)
assert all(min(r['post_to_support_mm2'],r['post_to_PCB_mm2'])>15 and r['shaft_clearance_interference_mm3']<1e-6 for r in contacts)
assert all(min(r.get('gap_spacer_to_deck_mm2',20),r.get('gap_spacer_to_bridge_mm2',20))>15 for r in contacts)
assert all(r['PCB_interference_mm3']<1e-6 for r in pins)
