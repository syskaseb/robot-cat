"""Read the latest qualified U1 snapshots without recomputing their histories.

Same sources/placements as u1_socket_current_context and power-grip overlay.
Use saved native BRep, not obsolete routing boxes or an invented clearance.
"""
import json
from pathlib import Path
import FreeCAD as A
import Part
from current_prototype_harness_scene import context as previous
from check_main_p0_placement import prop
import plan_u1_power_grips as P
import build_u1_socket_retainer as R
from plan_u1_external_interfaces import pca_pads
ROOT,BASE,OUT,SHA=P.ROOT,P.BASE,P.OUT,P.SHA


def context():
    reader,pins,targets,curves=previous();pins.add(Path(__file__))
    receipts={}
    for tag in ('socket-carrier','socket-population','socket-retainer',
                'interface-carriers','grouped-grips','board-grips','power-grips'):
        f=OUT/('u1-'+tag+'-native.json');r=json.loads(f.read_text());m=ROOT/r['native']
        assert SHA(m)==r['native_sha256'],m
        receipts[tag]=(r,m);pins.update((f,m))
    for n in list(targets):
        if n.startswith(('U1BoardAllowance','U1Spacer','U1Insulator','U1Mount','U1_unknown_height')) or n in receipts['socket-retainer'][0]['replaces']:
            targets.pop(n)
    pop=receipts['socket-population'][1];ret=receipts['socket-retainer'][1]
    targets['U1_Adapter1208PCB']=reader.shape(pop,'Adapter1208PCB')
    for group in ('FixedPurchasedReferences','TopFaceReferences'):
        obj=reader.doc(pop)[group]
        assert reader.placement(obj).isIdentity(),'Unexpected moved population'
        for link in prop(obj,'Group').findall('.//Link'):
            name=link.get('value');targets['U1_'+name]=reader.shape(pop,name)
    for name in ('AnchorLeft','AnchorRight','RetainerBar'):
        targets['U1_'+name]=reader.shape(ret,name)
    refs,f=R.references();pins.add(f);targets.update({'U1_'+n:s for n,s in refs.items()})
    f=OUT/'u1-socket-passives-resolved.json';g=json.loads(f.read_text());pins.add(f)
    assert not g['errors'] and not g['passive_material_resolutions']
    for n,q in g['changed_E2_routes'].items():
        curves['pwm-branch-checkpoint/'+n]=(P.wire(q['parts']),q['radius'])
        targets.pop(n,None);targets.pop(n+'_BoardInsulation',None)
    f=OUT/'u1-socket-carrier-plan.json';p=json.loads(f.read_text());pins.add(f)
    drills=[Part.makeCylinder(float(v['drill'])/2,3,A.Vector(91.59+float(v['x']),float(v['y']),82.5))
            for group in p['board']['groups'] for v in group['pads']]
    targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(Part.makeCompound(drills))
    f=ROOT/'hardware/reference/adafruit815-2026-09-26/Adafruit PCA9685 rev C.brd';pads=pca_pads(f);pins.add(f)
    targets['PWM9685NominalPCB']=targets['PWM9685NominalPCB'].cut(Part.makeCompound([
        Part.makeCylinder(.508,3,A.Vector(x,y,82.5)) for x,y,z in pads.values()]))
    for name,tag in [('UpperCarrier001','interface-carriers'),('LowerCarrier001','power-grips'),
                     ('E2Fixture','power-grips'),('GPIOGrip','grouped-grips'),
                     ('PCAGrip','grouped-grips'),('MAINGrip','power-grips')]:
        targets[name]=reader.shape(receipts[tag][1],name)
    for name in ('AnchorLeft','AnchorRight'):targets['U1_'+name]=reader.shape(receipts['board-grips'][1],name)
    g=receipts['grouped-grips'][0]
    for name in g['replaced_upper_washers']:targets.pop(name)
    for row in g['changed_existing_hardware']:
        s=targets[row['name']].copy();s.translate(A.Vector(*row['translation_mm']));targets[row['name']]=s
    for tag,allocation in [('Grouped',P.G.allocation()),('Board',P.B.allocation()),('Power',P.allocation())]:
        targets.update({tag+'/'+n:s for n,s in allocation['bands'].items()})
    targets.update(P.main_hardware())
    f=OUT/'u1-common-wiring-plan.json';p=json.loads(f.read_text());pins.add(f)
    for n,q in {**p['complete_routes'],**p['changed_MAIN_pair']}.items():
        curves[n]=(P.wire(q['parts']),q.get('radius',q.get('radius_mm')))
    curves.update({n+'/bare':(P.wire(q['parts']),q['radius']) for n,q in p['bare'].items()})
    f=OUT/'u1-service-departures-plan.json';p=json.loads(f.read_text());pins.add(f)
    for n,q in p['replacements'].items():curves[n]=(P.wire(q['parts']),q['radius'])
    f=OUT/'e2-tail-insulation-current.json';p=json.loads(f.read_text());pins.add(f)
    assert p['status']=='CHANGED_E2_TAIL_INSULATION_NOMINAL_CLEAR_NATIVE_OPEN'
    for n,q in p['routes'].items():curves['pwm-branch-checkpoint/'+n]=(P.wire(q['parts']),q['radius'])
    f=OUT/'e2-tail-insulation-native.json';p=json.loads(f.read_text());m=ROOT/p['native'];pins.update((f,m))
    assert SHA(m)==p['native_sha256']
    for n in p['envelopes']:targets[n+'_BoardInsulation']=reader.shape(m,n+'_BoardInsulation')
    return reader,pins,targets,curves


if __name__=='__main__':
    import time
    t=time.monotonic();reader,pins,targets,curves=context()
    print(json.dumps(dict(targets=len(targets),curves=len(curves),seconds=time.monotonic()-t,
        BUS_targets={n:[getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
                     for n,s in targets.items() if n in ('D_FL','G2','BUSBand','BUSHead') or 'BUSsupplier' in n})))
