"""Extend the qualified head master, not another independently rebuilt head.

Only the fixed carrier changes. Moving fork, retained fifty identities and
MAIN dependency are inherited from the pinned relocated-reopen master proof.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import plan_fixed_head_jr_terminations as J
from build_fixed_head_interface import add_box,strap_boxes
from build_u1_grouped_grips import validate
from open_prototype_head_assembly import reference_signature
H,S,I=J.H,J.S,J.I
MODEL=H.OUT/'HeadNeckFixedJoined.FCStd'

def run():
    tick=time.monotonic();gf=H.OUT/'fixed-head-jr-terminations-material.json';gate=H.read(gf)
    mf=H.OUT/'fixed-head-native-master.json';master=H.read(mf)
    assert gate['status']=='FIXED_JR_JOINS_SHARED_MATERIAL_CLEAR_NATIVE_OPEN'
    assert gate['head_poses']==9 and gate['leg_poses']==108
    assert not gate['contacts'] and not gate['errors']
    for receipt in (gate,master):
        for n,h in receipt['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    source=H.ROOT/master['model'];assert S.SHA(source)==master['model_sha256']
    assert not MODEL.exists(),'Receive existing result, do not overwrite'
    p,feeds,roots,meta,fork,reader,alloc,archive=I.prepare()
    pads,bands,sleeves,rows=J.allocation(feeds)
    d=A.openDocument(str(source));d.saveAs(str(MODEL))
    body=d.getObject(master['replaced_targets']['YawCarrier']);host=body.Shape.copy()
    expected=S.fuse([host]+[H.T.box(r) for r in pads.values()])
    for band in bands.values():expected=expected.cut(band)
    expected=expected.removeSplitter()
    par=d.addObject('App::VarSet','FixedSpliceParameters')
    par.addProperty('App::PropertyLength','RootThickness');par.RootThickness=3
    for n,row in pads.items():
        add_box(d,body,n,row,expression=par.Name+'.RootThickness' if n.endswith('SpliceRoot') else None)
    for row in rows:
        n=row['wire'];x=pads[n+'SpliceBed'][0]+4;z=pads[n+'SpliceBed'][5]+2.4
        for side,y,direction in [('JR',19.5,-1),('HELU',50.5,1)]:
            for k,box in enumerate(strap_boxes(x,y,41.2,z+1.25,1.25,head_side=direction)):
                if body.Shape.common(H.T.box(box)).Volume>1e-6:
                    add_box(d,body,n+side+'SplicePassage'+str(k),box,pocket=True)
    validate(body)
    assert body.Shape.cut(expected).Volume<1e-5 and expected.cut(body.Shape).Volume<1e-5
    assert host.cut(body.Shape).Volume<1e-5
    nominal=body.Shape.Volume;par.RootThickness=3.2;d.recompute();validate(body)
    assert body.Shape.Volume>nominal,'New splice parameter inert'
    par.RootThickness=3;d.recompute();validate(body);assert abs(body.Shape.Volume-nominal)<1e-5
    native_expected=body.Shape.copy()
    for n,s in {**bands,**{n+'Sleeve':s for n,s in sleeves.items()}}.items():
        ob=d.addObject('Part::Feature','Interface_'+n);s=s.copy();s.translate(-H.SHIFT);ob.Shape=s
        ob.addProperty('App::PropertyString','Scope');ob.Scope='Nominal fixed splice/independent intact-insulation restraint; delivery fit and electrical tests remain gates.'
        d.CP2Head.addObject(ob)
    link=d.getObject('Head_YawCarrier')
    actual=link.Shape.copy();actual.Placement=d.CP2Head.Placement*actual.Placement
    reference_signature(actual,native_expected,'ChangedFixedCarrierWorldPlacement')
    print('Fixed splice native history/parameter/world placement',round(time.monotonic()-tick,3),flush=True)
    d.save();A.closeDocument(d.Name)
    file=H.OUT/'FixedYawCarrier_FixedJoined_x1.stl'
    with tempfile.TemporaryDirectory(prefix='robot-cat-jr-native-') as td:
        cp=Path(td)/MODEL.name;shutil.copy2(MODEL,cp);d=A.openDocument(str(cp));d.recompute()
        body=d.getObject(master['replaced_targets']['YawCarrier']);validate(body)
        reference_signature(body.Shape,native_expected,'RelocatedFixedCarrier')
        assert all(o.getLinkedObject(True).Document==d for o in d.Objects if o.TypeId=='App::Link')
        s=body.Shape.copy();bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
        bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
        mesh.write(str(file));sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in body.Group)
        A.closeDocument(d.Name)
    native=H.read(H.OUT/'fixed-head-interface-native.json')
    moving=next(row for row in native['exports'] if row['part']=='MovingFork')
    assert S.SHA(H.ROOT/moving['path'])==moving['sha256']
    report=dict(status='FIXED_HEAD_JOINED_NATIVE_PREPARED_SELECTION_STOCK_OPEN',selected=False,physical_pass=False,
        model=MODEL.relative_to(H.ROOT).as_posix(),model_sha256=S.SHA(MODEL),
        changed_part='FixedYawCarrier',unchanged_moving_export_reused=True,
        exports=[dict(part='FixedYawCarrier',path=file.relative_to(H.ROOT).as_posix(),sha256=S.SHA(file),size_mm=size,quantity=1,brim_each_mm=5),moving],
        new_bands=6,new_JR=0,splice_joins=3,raw_sleeves_mm=[20]*3,
        parameter_restore_mm=[3,3.2,3],fully_constrained_fixed_sketches=sketches,relocated_reopen=True,external_links=0,
        retained_master_scope='52rest identities, two replaced targets nine poses and MAIN4-5-4 inherited unchanged; changed fixed additions separately checked against nine head and108leg samples.',
        source_sha256={**gate['source_sha256'],gf.relative_to(H.ROOT).as_posix():S.SHA(gf),mf.relative_to(H.ROOT).as_posix():S.SHA(mf),source.relative_to(H.ROOT).as_posix():S.SHA(source),Path(__file__).relative_to(H.ROOT).as_posix():S.SHA(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    H.save('fixed-head-jr-terminations-native.json',report)
    print(json.dumps({k:report[k] for k in ('status','fully_constrained_fixed_sketches','worker_seconds')}),flush=True)

if __name__=='__main__':run()
