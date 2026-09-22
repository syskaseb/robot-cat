"""Incremental AUX fit, contacts, fastener stack and service probes.

Read-only CAD input. No claim of thermal safety, PCB strength, wiring release,
old-old collision repair, continuous swept-volume clearance or production fit.
"""
import hashlib
import itertools
import json
import FreeCAD as A
import Part
from aux35 import OUT, SOURCE, SOURCE_SHA, MASTER, HOLES, REPLACEMENTS, ADDITIONS, instance


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def exact(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.
    value = sum(abs(sa.common(sb).Volume) for sa in a.Solids for sb in b.Solids
                if sa.BoundBox.intersect(sb.BoundBox))
    assert value < min(abs(a.Volume), abs(b.Volume)) + .001, 'Impossible intersection'
    return value


def envelope(s):
    b = s.BoundBox
    return Part.makeBox(b.XLength, b.YLength, b.ZLength, A.Vector(b.XMin,b.YMin,b.ZMin))


def main():
    plan = json.loads((SOURCE / 'assembly-plan.json').read_text())
    assert sha(SOURCE / plan['cad_filename']) == SOURCE_SHA
    assert json.loads((SOURCE / 'shape-cache/index.json').read_text())['source_sha256'] == SOURCE_SHA
    master_digest=sha(MASTER)
    master = A.openDocument(str(MASTER))
    old, shapes = {}, {}
    for r in plan['components']:
        s = Part.Shape(); s.read(str(SOURCE / 'shape-cache' / (r['name']+'.brep')))
        old[r['name']] = s; shapes[r['name']] = s
    for n, (src, xyz) in REPLACEMENTS.items():
        shapes[n] = instance(master, src, xyz)
    for n, (src, parent, material, xyz) in ADDITIONS.items():
        shapes[n] = instance(master, src, xyz)
    sketches = [dict(name=o.Name, fully_constrained=o.FullyConstrained) for o in master.Objects
                if o.TypeId == 'Sketcher::SketchObject']
    parts = []
    for o in master.Objects:
        if o.TypeId != 'PartDesign::Body': continue
        print('BOP',o.Name,flush=True)
        s = o.Shape; b = s.BoundBox; errors=[]
        try: s.check(True)
        except Exception as exc: errors.append(str(exc))
        parts.append(dict(name=o.Name,label=o.Label,design_role=getattr(o,'DesignRole','Installed'),valid=s.isValid(),solids=len(s.Solids),
            status=o.getStatusString(),bop_errors=errors,volume_mm3=s.Volume,
            envelope_mm=[b.XLength,b.YLength,b.ZLength],fits_256=max(b.XLength,b.YLength,b.ZLength)<=256))
    print('NATIVE',parts,flush=True)
    # Holes remove material only. Do not pretend that inherited old-old
    # clashes became new defects, or that subtracting holes certified them.
    cuts=[]
    for n in sorted(set(REPLACEMENTS)-{'AuxBuck'}):
        print('SUBTRACTIVE',n,flush=True)
        added=abs(shapes[n].cut(old[n]).Volume)
        cuts.append(dict(name=n,added_material_mm3=added,boolean_result_within_physical_bound=added<=shapes[n].Volume+.001,
                         removed_volume_mm3=old[n].Volume-shapes[n].Volume))
    focus=set(ADDITIONS)|{'AuxBuck'}
    hits=[]; pairs=0; proofs=0
    pcb=shapes['AuxBuck']; pcb_box=envelope(pcb)
    for an,bn in itertools.combinations(sorted(shapes),2):
        if not ({an,bn}&focus):continue
        a,b=shapes[an],shapes[bn]
        if not a.BoundBox.intersect(b.BoundBox):continue
        pairs+=1
        if 'AuxBuck' in (an,bn):
            other=b if an=='AuxBuck' else a
            if exact(pcb_box,other)<1e-8:
                proofs+=1; continue
        print('PAIR',pairs,an,bn,flush=True)
        v=exact(a,b)
        if v>.01:hits.append(dict(parts=[an,bn],volume_mm3=v))
    contacts=[]
    for i,(x,y) in enumerate(HOLES):
        post=shapes['AuxPost35_'+str(i)]
        z=38.52 if i<2 else 44
        support=shapes['Part__Feature038' if i<2 else 'TailBridge29']
        ring=Part.makeCylinder(3,.05,A.Vector(x,y,z-.05)).cut(Part.makeCylinder(1.2,.05,A.Vector(x,y,z-.05)))
        top=ring.copy();top.translate(A.Vector(0,0,52-z+.05))
        shaft=Part.makeCylinder(1.03,21 if i<2 else 19,A.Vector(x,y,34 if i<2 else 41))
        members=['AuxBuck','AuxPost35_'+str(i),'Part__Feature038','ShellMounted20']
        if i>=2: members+=['TailBridge29']
        # The notched front post needs its actual footprint, not a full ring.
        shifted=post.copy();shifted.translate(A.Vector(0,0,-.05))
        row=dict(index=i,axis_xy_mm=[x,y],post_to_support_mm2=exact(shifted,support)/.05,
                 post_to_pcb_mm2=exact(top,pcb)/.05,
                 shaft_interference_mm3=sum(exact(shaft,shapes[n]) for n in members),
                 screw_length_mm=19,clamp_stack_mm=16.5548 if i<2 else 12.5748,
                 nut_height_mm=1.6,protrusion_mm=.8452 if i<2 else 4.8252,
                 direction='down' if i<2 else 'up')
        contacts.append(row)
        print('CONTACT',row,flush=True)
    # Local straight reserves from v31's documented terminal drawing; not a
    # routed harness, connector pull space or minimum bend-radius proof.
    reserves=[]
    for x in [75.54,131.5]:
        box=Part.makeBox(12,10,6,A.Vector(x,-18.8,55))
        bad=[]
        for n,s in shapes.items():
            if not box.BoundBox.intersect(s.BoundBox): continue
            v=exact(box,s)
            if v>.01:bad.append(dict(part=n,volume_mm3=v))
        reserves.append(dict(base_mm=[x,-18.8,55],size_mm=[12,10,6],hits=bad))
    tools=[]
    for i,(x,y) in enumerate(HOLES):
        # In-situ only: report blockages. Bench assembly uses a removed deck.
        probes=[('nut_below',Part.makeCylinder(3,25,A.Vector(x,y,9.42)),{'AuxNut35_'+str(i),'AuxBolt35_'+str(i)}),
                ('head_above',Part.makeCylinder(2,30,A.Vector(x,y,55.5748)),{'AuxBolt35_'+str(i)})]
        if i>=2:
            probes=[('rear_head_below_bridge',Part.makeCylinder(2,25,A.Vector(x,y,14)),{'AuxBolt35_'+str(i)}),
                    ('rear_nut_above',Part.makeCylinder(3,10,A.Vector(x,y,55.1748)),{'AuxBolt35_'+str(i),'AuxNut35_'+str(i)})]
        for tag,probe,exclude in probes:
            bad=[]
            for n,s in shapes.items():
                if n in exclude or not probe.BoundBox.intersect(s.BoundBox): continue
                v=exact(probe,s)
                if v>.01:bad.append(dict(part=n,volume_mm3=v))
            tools.append(dict(index=i,route=tag,hits=bad))
    terminals=[]
    for x in [91.74,127.3]:
        for y in [-16.299995,-11.299995]:
            pin=Part.makeCylinder(.5,4,A.Vector(x,y,49.5748))
            shaft=Part.makeCylinder(2,30,A.Vector(x,y,63.5748))
            bad=[]
            for n,s in shapes.items():
                if n.startswith('AuxTerminal35_') or not shaft.BoundBox.intersect(s.BoundBox):continue
                v=exact(shaft,s)
                if v>.01:bad.append(dict(part=n,volume_mm3=v))
            terminals.append(dict(axis_xy_mm=[x,y],pin_to_pcb_mm3=exact(pin,pcb),driver_blockers=bad))
    # Board+terminals pre-soldered, placed on detached deck before overhead
    # modules. Include all supports, frame deck and tail bridge/its screws.
    module=Part.makeCompound([pcb]+[shapes['AuxTerminal35_'+str(i)] for i in range(2)])
    bench=[n for n in shapes if n.startswith(('AuxPost35_','TailFrameBolt29_'))]+['Part__Feature038','TailBridge29','AuxBolt35_2','AuxBolt35_3']
    insertion=[]
    for dz in range(20,-1,-2):
        moved=module.copy();moved.translate(A.Vector(0,0,dz));bad=[]
        for n in bench:
            v=exact(envelope(moved),shapes[n])
            if v>.01:
                v=exact(moved,shapes[n])
                if v>.01:bad.append(dict(part=n,volume_mm3=v))
        insertion.append(dict(lift_mm=dz,hits=bad))
    passed=(not hits and all(s['fully_constrained'] for s in sketches)
        and len(sketches)==11 and len(parts)==9
        and all(p['valid'] and p['solids']==1 and not p['bop_errors'] and p['status']=='Valid' and p['fits_256'] for p in parts)
        and all(r['added_material_mm3']<.001 and r['removed_volume_mm3']>0 for r in cuts)
        and all(min(r['post_to_support_mm2'],r['post_to_pcb_mm2'],r.get('gap_to_deck_mm2',30),r.get('gap_to_bridge_mm2',30))>15 and r['shaft_interference_mm3']<1e-6 for r in contacts)
        and all(not r['hits'] for r in reserves+insertion)
        and all(r['pin_to_pcb_mm3']<1e-6 for r in terminals))
    assert sha(MASTER)==master_digest,'Master changed during read-only audit; rerun'
    report=dict(master_sha256=master_digest,source_checkpoint_sha256=SOURCE_SHA,geometric_checks_passed=passed,
        rest_pairs=pairs,rest_interferences=hits,pcb_envelope_proofs=proofs,native_parts=parts,sketches=sketches,
        subtractive_changes=cuts,contacts=contacts,cable_reserves=reserves,tool_corridors=tools,
        terminal_checks=terminals,bench_insertion_samples=insertion,print_release=False,
        thermal_validation=False,full_harness_validation=False,assembly_requires_removed_deck=True,
        scope=__doc__,limitations=['PCB and fasteners nominal; no torque, PCB stress or thermal PETG approval.',
        'In-situ blocked approaches are retained; assemble deck on bench before overhead modules/legs.',
        'Screw-head/terminal internals and solder fillets not modeled. No outputs paralleled.',
        'Two gap Bodies in master are rejected hidden studies, NOT installed or printed. Rear M2x19 inserted UP before bridge is bolted to deck; top nuts require suitable wrench, circular socket envelope may collide with terminal.',
        'Front Post35_1 notch faces existing washer X98.7,Y0 R7.5; 0.2mm radial/axial nominal clearance, physical fit pending.',
        'Old head/shell and unresolved joints inherited, not certified by this incremental test.'])
    (OUT/'fit-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('native_parts','sketches','scope')},indent=2),flush=True)
    assert passed, 'See retained fit-audit.json'


if __name__=='__main__':main()
