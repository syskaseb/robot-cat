"""One editable copy of the two qualified U1/Pi carrier interfaces.

Preserve source history and M5 bearing zones; only obsolete side mounts,
the shared GPIO passage and the passive USB fit relief are removed.
No historical model or selected export is overwritten.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_current_main_sources import ROOT,OUT,BASE,SHA
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect

MODEL=OUT/'U1InterfaceCarriersCurrent.FCStd'


def box(b):return Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3]))


def run():
    tick=time.monotonic();gf=OUT/'u1-common-wiring-checks.json';g=json.loads(gf.read_text())
    pf=OUT/'u1-common-wiring-plan.json';p=json.loads(pf.read_text())
    assert SHA(pf)==g['plan_sha256']
    assert not any(g[k] for k in ('material_resolutions','wire_contacts','USB_fit_reservations','errors'))
    for n,h in g['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert len(p['complete_routes'])==11 and len(p['changed_MAIN_pair'])==2
    assert not MODEL.exists(),'Receive existing native result; do not duplicate'
    d=A.newDocument('U1InterfaceCarriersCurrent');originals={};sources=[]
    for name,f in [('UpperCarrier001',OUT/'SocketCarrierCurrent.FCStd'),
                   ('LowerCarrier001',BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd')]:
        sources.append(f);src=A.openDocument(str(f));body=d.copyObject(src.getObject(name),True)
        for ob in src.Objects:
            if ob.TypeId=='App::VarSet' and d.getObject(ob.Name) is None:d.copyObject(ob,True)
        A.closeDocument(src.Name);d.recompute();originals[name]=body.Shape.copy()
        assert body.Shape.isValid() and len(body.Shape.Solids)==1,name
    params=d.addObject('App::VarSet','InterfaceParameters')
    params.addProperty('App::PropertyLength','GPIOWidth');params.GPIOWidth=54
    params.addProperty('App::PropertyLength','USBReliefDepth');params.USBReliefDepth=9
    bankfile=OUT/'bank-input-plan.json';bank=json.loads(bankfile.read_text())
    cuts={
        'UpperCarrier001':[('GPIOPortal',p['GPIO_carrier_portal_world_mm'])],
        'LowerCarrier001':[(f'ObsoleteSideAttachment{i}',b) for i,b in enumerate(bank['obsolete_side_attachment_removal']['cut_bounds_mm'])]
            +[('USBRelief',p['USB_lower_carrier_relief_world_mm'])]}
    def validate(body):
        assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True),body.Name
        for ob in body.Group:
            assert not any(t in ('Invalid','Error') for t in ob.State),(ob.Name,list(ob.State))
            if ob.TypeId=='Sketcher::SketchObject' and ob.Name.startswith(('GPIO','USB','ObsoleteSide')):
                assert ob.FullyConstrained and ob.solve()==0,ob.Name
    for name,rows in cuts.items():
        body=d.getObject(name);inv=body.Placement.inverse()
        assert abs(body.Placement.Rotation.Angle)<1e-7,'Axis-aligned inherited carrier required'
        for label,b in rows:
            a=inv.multVec(A.Vector(*b[:3]));z=inv.multVec(A.Vector(*b[3:]));old=body.Tip
            sk=sketch(body,label+'Plan',z.z);rect(sk,a.x,a.y,z.x-a.x,z.y-a.y)
            if label=='GPIOPortal':
                # Width constraint of the shared passage is a useful editable parameter.
                for i in range(sk.ConstraintCount):
                    if sk.Constraints[i].Type=='Distance' and abs(sk.Constraints[i].Value-54)<1e-6:
                        sk.setExpression('Constraints['+str(i)+']','InterfaceParameters.GPIOWidth');break
            ob=body.newObject('PartDesign::Pocket',label);ob.Profile=sk;ob.BaseFeature=old
            if label=='USBRelief':ob.setExpression('Length','InterfaceParameters.USBReliefDepth')
            else:ob.Length=z.z-a.z
            body.Tip=ob;sk.Visibility=False;d.recompute();validate(body)
            print('Native interface',label,round(time.monotonic()-tick,2),flush=True)
        expected=originals[name]
        for _,b in rows:expected=expected.cut(box(b))
        assert body.Shape.cut(expected).Volume<1e-5 and expected.cut(body.Shape).Volume<1e-5,name
    lower=d.getObject('LowerCarrier001');before=originals[lower.Name]
    # Actual four Pi mount axes; preserve a4mm bearing zone around each.
    for x in (-15.5,42.5):
        for y in (-24.5,24.5):
            zone=Part.makeCylinder(4,30,A.Vector(x,y,35))
            assert before.common(zone).cut(lower.Shape).Volume<1e-5,(x,y,'M5 bearing removed')
    vols={n:d.getObject(n).Shape.Volume for n in cuts}
    params.USBReliefDepth=9.2;d.recompute();validate(lower)
    assert lower.Shape.Volume<vols[lower.Name]-1e-5
    params.USBReliefDepth=9;d.recompute();validate(lower)
    assert abs(lower.Shape.Volume-vols[lower.Name])<1e-5
    d.saveAs(str(MODEL));A.closeDocument(d.Name)
    exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-interface-carriers-') as td:
        fresh=Path(td)/MODEL.name;shutil.copy2(MODEL,fresh);d=A.openDocument(str(fresh));d.recompute()
        for name in cuts:
            body=d.getObject(name);validate(body);assert abs(body.Shape.Volume-vols[name])<1e-5
            mesh=MeshPart.meshFromShape(Shape=body.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            b=mesh.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)+10<256,size
            mesh.translate(-b.XMin,-b.YMin,-b.ZMin);f=OUT/(name+'_u1_interface_x1.stl');mesh.write(str(f))
            exports.append(dict(part=name,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),quantity=1,size_mm=size,
                brim_margin_each_mm=5,orientation='Original flat base down; PETG; physical support/fit/creep checks phase2'))
        A.closeDocument(d.Name)
    result=dict(status='U1_SHARED_CARRIERS_NATIVE_PREPARED_GRIPS_SERVICE_SELECTION_OPEN',
        native=MODEL.relative_to(ROOT).as_posix(),native_sha256=SHA(MODEL),exports=exports,
        exact_match_planning_cuts=True,preserved_Pi_four_4mm_bearing_zones=True,
        native_parameter_restore_mm=[9,9.2,9],fresh_relocated_reopen=True,
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in [*sources,gf,pf,bankfile,Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,E1_complete=False,W5_complete=False,physical_pass=False)
    (OUT/'u1-interface-carriers-native.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
