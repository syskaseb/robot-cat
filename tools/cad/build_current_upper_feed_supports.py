"""One editable replacement UpperCarrier: G1 open web plus G2 feed lands.

Copies qualified source history; never edits a historical master. Component
native/export only, not full W5, stock selection, outer shell or physical PASS.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,Sketcher,MeshPart
from plan_body36_receiver_space import P
from current_native_receiver_primitives import Construction
from current_body_restraint_material import prepare as material
from current_work_guard import check
from plan_axial_source_supports import arm_box
from open_deck_p0_supports import sketch


OUT=P.OUT/'upper-fixed-feed-supports'
MODEL=OUT/'UpperFixedFeedSupportsCurrent.FCStd'
PARTIAL=OUT/'UpperFixedFeedSupports.partial.FCStd'


def valid(s,name):
    assert s.isValid() and len(s.Solids)==1 and not s.check(True),name


def equal(a,b,name):
    assert max(a.cut(b).Volume,b.cut(a).Volume)<1e-4,name


def land(ops,row,name):
    frame=row['local_to_world']
    base=ops.fuse([ops.box(row[k],name+k,frame) for k in ('seat','foot')],name+'Positive')
    r=row['ring_cut']
    ring=ops.cut(ops.box(r['outer'],name+'Outer',frame),ops.box(r['inner'],name+'Inner',frame),name+'Ring')
    return ops.cut(base,ring,name+'Current')


def web(doc,ops,recipe):
    check();body=doc.addObject('PartDesign::Body','G1TriangleWeb')
    sk=sketch(body,'G1TriangleWebPlan',0)
    sk.Placement=A.Placement(A.Vector(0,recipe['spine_y_mm'][1],0),A.Rotation(A.Vector(1,0,0),90))
    points=recipe['spine_triangle_xz_mm']
    for i,(x,z) in enumerate(points):
        X,Z=points[(i+1)%3]
        sk.addGeometry(Part.LineSegment(A.Vector(x,z,0),A.Vector(X,Z,0)),False)
    for i,(x,z) in enumerate(points):
        sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%3,1))
        sk.addConstraint(Sketcher.Constraint('DistanceX',i,1,x))
        sk.addConstraint(Sketcher.Constraint('DistanceY',i,1,z))
    pad=body.newObject('PartDesign::Pad','G1TriangleWebPad');pad.Profile=sk
    pad.Length=recipe['spine_y_mm'][1]-recipe['spine_y_mm'][0]
    pad.Refine=True;body.Tip=pad;doc.recompute()
    assert sk.FullyConstrained and sk.solve()==0
    ops.sketches+=1;sk.Visibility=False;body.Visibility=False
    valid(body.Shape,'TriangleWeb');return body


def run():
    check();tick=time.monotonic();OUT.mkdir(exist_ok=True)
    shapes,pins=material()
    g1file=P.OUT/'g1-rooted-carrier-plan.json';g1=json.loads(g1file.read_text())
    feedsfile=P.OUT/'remaining-fixed-feed-checks.json';feeds=json.loads(feedsfile.read_text())
    source=P.OUT/'U1InterfaceCarriersCurrent.FCStd'
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in
        (source,Path(__file__),Path(__file__).with_name('current_native_receiver_primitives.py'),
         Path(__file__).with_name('native_support_primitives.py'),Path(__file__).with_name('open_deck_p0_supports.py'))})
    records=[];doc=None;ops=None
    def save(status,**extra):
        result=dict(status=status,native=MODEL.relative_to(P.ROOT).as_posix(),
            partial_native=PARTIAL.relative_to(P.ROOT).as_posix(),source_sha256=pins,
            records=records,fully_constrained_new_sketches=ops.sketches if ops else None,
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            physical_print_quantity=1,replaces='UpperCarrier001_u1_interface_x1.stl',new_separate_prints=0,
            native_scope='OneUpperCarrier replacement incl G1/5lands/G2/4ends. Lower source body retained only as hidden history, NOT another export.',
            physical_gates=['Delivered lacing fit/retention/tightening/creep','Installed lever/service access','Whole harness/stock/A2'],**extra)
        f=OUT/'manifest.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f)
    if MODEL.exists():
        previous=json.loads((OUT/'manifest.json').read_text())
        if previous['status']=='CURRENT_UPPER_FEED_NATIVE_COMPONENT_COMPLETE':
            print('Receive existing complete Upper native; do not duplicate',flush=True);return
        for f in (source,g1file,feedsfile):assert previous['source_sha256'][f.relative_to(P.ROOT).as_posix()]==P.SHA(f),f
        doc=A.openDocument(str(MODEL));ops=Construction(doc)
    else:
        assert not PARTIAL.exists(),'Resume saved partial features; do not rebuild completed native stages'
        with tempfile.TemporaryDirectory(prefix='robot-cat-upper-feeds-source-') as td:
            copy=Path(td)/source.name;shutil.copy2(source,copy)
            doc=A.openDocument(str(copy));ops=Construction(doc)
            try:
                parent=doc.getObject('UpperCarrier001');valid(parent.Shape,'RetainedUpper')
                params=doc.addObject('App::VarSet','UpperFeedParameters')
                params.addProperty('App::PropertyLength','PortalPostTop');params.PortalPostTop=142
                children=[parent];r=g1['recipe']
                for row in r['pads']:children.append(ops.box(row['bounds_mm'],'G1'+row['name']))
                children.append(web(doc,ops,r))
                post=ops.box(r['root_post_bounds_mm'],'G1PortalPost')
                post.Tip.setExpression('Length','UpperFeedParameters.PortalPostTop - 76.72 mm')
                children.append(post)
                for i,(a,b) in enumerate(zip(r['root_path_mm'][1:],r['root_path_mm'][2:])):
                    bb=arm_box(a,b,[2,2,2]).BoundBox
                    children.append(ops.box([bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax],'G1PortalBeam'+str(i)))
                for row in r['lands']:
                    children.append(land(ops,row,'G1'+row['wire']))
                    children.append(ops.box(row['bridge_mm'],'G1'+row['wire']+'Bridge'))
                    check();print('Upper native G1 land',row['wire'],flush=True)
                for name in ('Heavy3','BUS_G'):
                    children.append(land(ops,feeds['recipes'][name],'G2'+name))
                final=ops.fuse(children,'UpperCarrierFixedFeedsCurrent');valid(final.Shape,'UpperCurrent')
                for name,s in shapes.items():
                    if name.startswith('FixedFeed/FL_G/'):continue
                    if name.endswith('/band') or name.startswith('G1/W'):
                        ref=doc.addObject('Part::Feature','LacingReference'+name.replace('/','_'));ref.Shape=s;ref.Visibility=False
                for ob in doc.Objects:
                    if hasattr(ob,'Visibility'):ob.Visibility=False
                final.Visibility=True;doc.recompute();doc.saveAs(str(MODEL))
                save('CURRENT_UPPER_NATIVE_SAVED_PARAMETER_EXPORT_OPEN')
            except BaseException:
                if doc:doc.saveAs(str(PARTIAL));save('PARTIAL_CURRENT_UPPER_FEED_NATIVE')
                raise
    try:
        check();final=doc.getObject('UpperCarrierFixedFeedsCurrent');assert final
        parent=doc.getObject('UpperCarrier001').Shape.copy()
        expected=parent.multiFuse([shapes[k] for k in
            ('G1/carrier','FixedFeed/Heavy3/body','FixedFeed/BUS_G/body')]).removeSplitter()
        valid(expected,'ExpectedUpper');valid(final.Shape,'NativeUpper');equal(final.Shape,expected,'Upper exact material')
        nominal=final.Shape.Volume;params=doc.getObject('UpperFeedParameters')
        params.PortalPostTop=142.2;doc.recompute();check();valid(final.Shape,'ChangedPost')
        assert final.Shape.Volume>nominal+1e-5,'Parameter does not change useful material'
        params.PortalPostTop=142;doc.recompute();valid(final.Shape,'RestoredPost')
        equal(final.Shape,expected,'RestoredUpper');doc.saveAs(str(MODEL));A.closeDocument(doc.Name);doc=None
        with tempfile.TemporaryDirectory(prefix='robot-cat-upper-feeds-reopen-') as td:
            moved=Path(td)/MODEL.name;shutil.copy2(MODEL,moved)
            fresh=A.openDocument(str(moved));fresh.recompute();check()
            q=fresh.getObject('UpperCarrierFixedFeedsCurrent');valid(q.Shape,'RelocatedUpper');equal(q.Shape,expected,'RelocatedMaterial')
            mesh=MeshPart.meshFromShape(Shape=q.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            b=mesh.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)+10<256,size
            mesh.translate(-b.XMin,-b.YMin,-b.ZMin);f=OUT/'UpperCarrier_fixed_feeds_x1.stl';mesh.write(str(f))
            A.closeDocument(fresh.Name)
        records.append(dict(part='UpperCarrier001',quantity=1,export=f.relative_to(P.ROOT).as_posix(),
            export_sha256=P.SHA(f),size_mm=size,brim_margin_each_mm=5,closed_manifold=True,
            orientation='Original flat base down; PETG support/fit/creep phase2, no slicer run'))
        save('CURRENT_UPPER_FEED_NATIVE_COMPONENT_COMPLETE',native_sha256=P.SHA(MODEL),
             parameter_restore_mm=[142,142.2,142],relocated_reopen=True,original_material_preserved=True,
             lacing_references=7,lacing_candidate_mm=1050,stock_selected=False)
        print('Upper current native complete',round(time.monotonic()-tick,3),flush=True)
    finally:
        if doc:
            doc.saveAs(str(MODEL));A.closeDocument(doc.Name)


if __name__=='__main__':run()
