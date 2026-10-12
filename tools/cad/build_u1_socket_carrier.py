"""Remove two obsolete U1 functions in a COPY of the current native carrier.

Existing BUS/W1/W2 features remain editable and unchanged. No selected or
historical CAD is overwritten. This candidate cannot qualify external wires.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,Mesh,MeshPart
from plan_current_main_sources import ROOT,OUT,SHA
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect

SOURCE=OUT/'BUSCarrierCurrent.FCStd'
MODEL=OUT/'SocketCarrierCurrent.FCStd'


def run():
    tick=time.monotonic();gatefile=OUT/'u1-socket-passives-resolved.json'
    gate=json.loads(gatefile.read_text())
    assert gate['status']=='SOCKET_FORMED_LEADS_AND_RETAINER_SPACE_CLEAR_NATIVE_ENDS_OPEN'
    for n,h in gate['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert not MODEL.exists(),'Receive existing candidate instead of duplicating it'
    src=A.openDocument(str(SOURCE));d=A.newDocument('SocketCarrierCurrent')
    body=d.copyObject(src.UpperCarrier001,True)
    # Copy expression owners that are not part of a Body dependency tree.
    if d.getObject('BUSParameters') is None:d.copyObject(src.BUSParameters,True)
    A.closeDocument(src.Name);d.recompute();original=body.Shape.copy()
    params=d.addObject('App::VarSet','SocketParameters')
    params.addProperty('App::PropertyLength','ObsoletePostDepth');params.ObsoletePostDepth=7.3
    inverse=body.Placement.inverse()
    for name,bounds,depth in [
        ('ObsoleteU1PlatformRemoval',[77,11,87.52,97,45,90.02],2.5),
        ('ObsoleteU1PostRemoval',[77,26,80.22,97,29,87.52],'SocketParameters.ObsoletePostDepth')]:
        a=inverse.multVec(A.Vector(*bounds[:3]));b=inverse.multVec(A.Vector(*bounds[3:]))
        old=body.Tip;s=sketch(body,name+'Plan',b.z);rect(s,a.x,a.y,b.x-a.x,b.y-a.y)
        ob=body.newObject('PartDesign::Pocket',name);ob.Profile=s;ob.BaseFeature=old
        if isinstance(depth,str):ob.setExpression('Length',depth)
        else:ob.Length=depth
        body.Tip=ob;s.Visibility=False;d.recompute()
        assert body.Shape.isValid() and len(body.Shape.Solids)==1,(name,list(ob.State))
        print('Native socket carrier',name,round(time.monotonic()-tick,2),flush=True)
    def validate():
        assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True)
        for o in body.Group:
            assert not any(t in ('Invalid','Error') for t in o.State),(o.Name,list(o.State))
            if o.Name.startswith('Obsolete') and o.TypeId=='Sketcher::SketchObject':assert o.FullyConstrained and o.solve()==0
    validate();expected=original
    for b in gate['obsolete_U1_function_cuts_mm']:
        expected=expected.cut(Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3])))
    assert body.Shape.cut(expected).Volume<1e-5 and expected.cut(body.Shape).Volume<1e-5
    volume=body.Shape.Volume;params.ObsoletePostDepth=7.5;d.recompute();validate()
    assert body.Shape.Volume<volume-1e-5
    params.ObsoletePostDepth=7.3;d.recompute();validate();assert abs(body.Shape.Volume-volume)<1e-5
    d.saveAs(str(MODEL));A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-socket-carrier-') as td:
        f=Path(td)/MODEL.name;shutil.copy2(MODEL,f);d=A.openDocument(str(f));d.recompute()
        body=d.getObject('UpperCarrier001');validate();assert abs(body.Shape.Volume-volume)<1e-5
        shape=body.Shape.copy()
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
    assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
    b=mesh.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)+10<256,size
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);stl=OUT/'UpperCarrier_socket_current_x1.stl';mesh.write(str(stl))
    result=dict(status='NATIVE_SOCKET_CARRIER_PREPARED_ENDS_SELECTION_OPEN',selected=False,physical_pass=False,
        native=MODEL.relative_to(ROOT).as_posix(),native_sha256=SHA(MODEL),
        export=dict(path=stl.relative_to(ROOT).as_posix(),sha256=SHA(stl),quantity=1,size_mm=size,brim_margin_mm_each=5),
        replaces='BUSCarrierCurrent.UpperCarrier001 only, NOT an extra plate',
        preserved_native_history=True,parameter_restore_mm=[7.3,7.5,7.3],fresh_relocated_reopen=True,
        exact_match_qualified_subtractions=True,source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (SOURCE,gatefile,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'u1-socket-carrier-native.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    A.closeDocument(d.Name);print(json.dumps(result),flush=True)


if __name__=='__main__':run()
