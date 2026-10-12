"""Load the single latest U1 candidate without selecting or rebuilding it.

Retain actual MAIN/BUS and all existing conductors. Only obsolete U1 features
and changed E2 tails are replaced. PCB holes are source-backed, not exceptions
that allow a whole wire through an undrilled board.
"""
import json,sys
from pathlib import Path
import FreeCAD as A
import Part
from current_prototype_harness_scene import context as previous,wire
from plan_current_main_sources import ROOT,OUT,SHA
import build_u1_socket_retainer as R
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'electronics'))
import plan_u1_socket_carrier as U
from plan_u1_external_interfaces import pca_pads


def context():
    reader,pins,targets,wires=previous();docs=[];pins.add(Path(__file__))
    receipts={}
    for tag in ('carrier','population','retainer'):
        f=OUT/('u1-socket-'+tag+'-native.json');r=json.loads(f.read_text());receipts[tag]=r
        model=ROOT/r['native'];assert SHA(model)==r['native_sha256'],model
        doc=A.openDocument(str(model));docs.append(doc);pins.update((f,model))
    carrier,pop,ret=docs
    for n in list(targets):
        if n.startswith(('U1BoardAllowance','U1Spacer','U1Insulator','U1Mount','U1_unknown_height')) or n in receipts['retainer']['replaces']:
            targets.pop(n)
    targets['UpperCarrier001']=carrier.UpperCarrier001.Shape.copy()
    targets['U1_Adapter1208PCB']=pop.Adapter1208PCB.Shape.copy()
    for group in (pop.FixedPurchasedReferences,pop.TopFaceReferences):
        assert group.getGlobalPlacement().Base.Length<1e-7,'Unexpected moved population'
        for o in group.Group:targets['U1_'+o.Name]=o.Shape.copy()
    for n in ('AnchorLeft','AnchorRight','RetainerBar'):targets['U1_'+n]=ret.getObject(n).Shape.copy()
    refs,f=R.references();pins.add(f);targets.update({'U1_'+n:s for n,s in refs.items()})
    gf=OUT/'u1-socket-passives-resolved.json';g=json.loads(gf.read_text());pins.add(gf)
    assert not g['errors'] and not g['passive_material_resolutions']
    for n,q in g['changed_E2_routes'].items():
        wires['pwm-branch-checkpoint/'+n]=(wire(q['parts']),q['radius'])
        targets.pop(n,None);targets.pop(n+'_BoardInsulation',None)
    pf=OUT/'u1-socket-carrier-plan.json';p=json.loads(pf.read_text());pins.add(pf)
    drills=[Part.makeCylinder(float(v['drill'])/2,3,A.Vector(91.59+float(v['x']),float(v['y']),82.5))
            for group in p['board']['groups'] for v in group['pads']]
    targets['PWM1608NominalPCB']=targets['PWM1608NominalPCB'].cut(Part.makeCompound(drills))
    bf=ROOT/'hardware/reference/adafruit815-2026-09-26/Adafruit PCA9685 rev C.brd';pads=pca_pads(bf);pins.add(bf)
    # All JP2/3/4 holes already exist in the referenced purchased board.
    pcb=targets['PWM9685NominalPCB']
    targets['PWM9685NominalPCB']=pcb.cut(Part.makeCompound([
        Part.makeCylinder(.508,3,A.Vector(x,y,82.5)) for x,y,z in pads.values()]))
    for n in ('PWM1608NominalPCB','PWM9685NominalPCB'):assert targets[n].isValid()
    for d in docs:A.closeDocument(d.Name)
    return reader,pins,targets,wires
