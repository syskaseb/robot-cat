"""Append six editable YZ-pocket features to a COPY of received carriers.

No rebuilding252old sketches, no historical overwrite. Two changed exports
plus two unchanged rear exports form ONE current candidate set. Whole W5,
motion sweep, bond retention and physical approval remain open.
"""
import json
import shutil
import tempfile
import time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import build_complete_source_carriers as B
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
P=B.P


def placement(values):
    m=A.Matrix()
    for i in range(4):
        for j in range(4):setattr(m,'A'+str(i+1)+str(j+1),values[4*i+j])
    return A.Placement(m)


def run():
    tick=time.monotonic();gf=P.OUT/'front-fixed-port-clearance.json'
    gate=json.loads(gf.read_text());assert gate['status']=='FRONT_FIXED_PORT_CLEARANCE_SUBSET_NATIVE_OPEN' and not gate['errors']
    for n,h in gate['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    nf=P.OUT/'complete-source-carriers-native.json';old=json.loads(nf.read_text())
    source=P.ROOT/old['native'];assert P.SHA(source)==old['native_sha256']
    out=P.OUT/'source-carriers-fixed-interface';out.mkdir(exist_ok=True)
    model=out/'SourceCarriersFixedClearance.FCStd';assert not model.exists(),'Receive current result; never overwrite an existing native'
    target_names=[r['part'] for r in gate['rows']];expected={};volumes={}
    with tempfile.TemporaryDirectory(prefix='robot-cat-front-port-native-') as td:
        copy=Path(td)/model.name;shutil.copy2(source,copy);d=A.openDocument(str(copy))
        par=d.addObject('App::VarSet','FrontPortParameters')
        par.addProperty('App::PropertyLength','PocketExtraDepth');par.PocketExtraDepth=.4
        for row in gate['rows']:
            name=row['part'];b=d.getObject(name);expected[name]=b.Shape.copy()
            for index,cut in enumerate(row['cutters']):
                x,y,z,X,Y,Z=cut['world_fixed_box_mm'];inverse=placement(cut['fixed_to_owner'])
                tool=P.box([x,y,z,X,Y,Z]);tool.Placement=inverse*tool.Placement
                expected[name]=expected[name].cut(tool).removeSplitter()
                # local sketchX=worldY, local sketchY=worldZ, normal=worldX.
                m=A.Matrix();m.A11,m.A12,m.A13,m.A14=0,0,1,X
                m.A21,m.A22,m.A23,m.A24=1,0,0,0
                m.A31,m.A32,m.A33,m.A34=0,1,0,0
                sk=sketch(b,name+'FixedPortReliefPlan'+str(index),0)
                sk.Placement=inverse*A.Placement(m);rect(sk,y,z,Y-y,Z-z)
                previous=b.Tip;cutfeature=b.newObject('PartDesign::Pocket',name+'FixedPortRelief'+str(index))
                cutfeature.Profile=sk;cutfeature.BaseFeature=previous
                # Other faces retain their defined0.4mm allowance. This useful
                # parameter changes only the inward X-depth, not cable lands.
                cutfeature.setExpression('Length',f'{X-x-.4} mm + FrontPortParameters.PocketExtraDepth')
                cutfeature.Refine=True;b.Tip=cutfeature;d.recompute();previous.Visibility=False;sk.Visibility=False
                print('native front relief',name,index,flush=True)
            B.validate(b)
            assert b.Shape.cut(expected[name]).Volume<1e-5 and expected[name].cut(b.Shape).Volume<1e-5,name
            volumes[name]=b.Shape.Volume
        # Rear parts and all purchased reference envelopes remain unchanged.
        for name in ('RearLeftSourceCarrier','RearRightSourceCarrier'):
            b=d.getObject(name);B.validate(b);volumes[name]=b.Shape.Volume
        par.PocketExtraDepth=.5;d.recompute()
        for name in target_names:
            b=d.getObject(name);B.validate(b);assert b.Shape.Volume<volumes[name],name
        par.PocketExtraDepth=.4;d.recompute()
        for name,v in volumes.items():
            b=d.getObject(name);B.validate(b);assert abs(b.Shape.Volume-v)<1e-5,name
        d.saveAs(str(model));A.closeDocument(d.Name)
    exports=[r for r in old['exports'] if r['part'] not in target_names]
    with tempfile.TemporaryDirectory(prefix='robot-cat-front-port-reopen-') as td:
        dest=Path(td)/model.name;shutil.copy2(model,dest);d=A.openDocument(str(dest));d.recompute()
        for name,volume in volumes.items():
            b=d.getObject(name);B.validate(b);assert abs(b.Shape.Volume-volume)<1e-5,name
            if name not in target_names:continue
            s=b.Shape.copy();bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1,name
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            path=out/(name+'_x1.stl');mesh.write(str(path))
            exports.append(dict(part=name,path=path.relative_to(P.ROOT).as_posix(),sha256=P.SHA(path),quantity=1,size_mm=size,brim_each_mm=5))
        A.closeDocument(d.Name)
    assert len(exports)==4 and len({r['part'] for r in exports})==4
    receipt=dict(status='FRONT_FIXED_PORT_CLEARANCE_NATIVE_PREPARED_W5_OPEN',
                 native=model.relative_to(P.ROOT).as_posix(),native_sha256=P.SHA(model),
                 exports=exports,retained_native_sketches=252,added_fully_constrained_sketches=6,
                 parameter_restore_mm=[.4,.5,.4],parameter_meaning='FrontPortParameters.PocketExtraDepth; inwardX depth only, other clearance faces fixed at0.4mm',
                 relocated_reopen=True,root_contact_faces=old['root_contact_faces'],
                 inherited_case_cap_and_three_seats_per_front_unchanged=True,
                 unchanged_rear_exports_reused=True,new_hardware=0,
                 selected=False,W5_complete=False,physical_pass=False,
                 assembly=old['assembly'],phase2_gates=old['gates'],
                 source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (gf,nf,source,Path(__file__),Path(B.__file__))},
                 worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'front-fixed-port-clearance-native.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=receipt['status'],added_sketches=6,exports=4,worker_seconds=receipt['worker_seconds'])),flush=True)


if __name__=='__main__':run()
