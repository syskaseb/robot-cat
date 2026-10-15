"""Editable four received moving-source supports, retaining native history.

Positive sketch masks intersect original native carriers to remove only the
superseded Hip1 branch. New precut seats never cut retained sibling material.
Not the full36-core harness, selected export or a physical load qualification.
"""
import json,shutil,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import check_near_axis_hip_sources as C
from build_front_fixed_port_clearance import placement
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
from build_remaining_loom_supports import print_orientation
from plan_axial_source_supports import arm_box
P=C.P
DEADLINE=datetime.fromisoformat('2026-10-15T07:00:00+00:00')


def check_time():
    if datetime.now(timezone.utc)>=DEADLINE:raise TimeoutError('Authorized09:00 deadline; preserve partial only')


def positive_mask(leg,root,family,bridge,extra):
    x,y,z,X,Y,Z=root['bond_bounds_world_mm']
    rows=[dict(name='CaseCap',bounds_mm=[x,y,Z,X,Y,Z+4])]
    for path in root['paths']:
        if path['loom'].endswith('1'):continue
        for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
            rows.append(dict(name=path['loom']+'Branch'+str(i),bounds_mm=
                [min(a[j],b[j])-h for j,h in enumerate((2,3,2))]+
                [max(a[j],b[j])+h for j,h in enumerate((2,3,2))]))
    sign=-1 if leg.startswith('Front') else 1
    for row in family['hips']:
        if row['physical_leg']!=leg or row['loom'].endswith('1'):continue
        xx,yy,zz=row['moving_anchor_rest_world_mm'];lo,hi=sorted((xx+sign*4,xx+sign*8))
        rows.append(dict(name=row['loom']+'NineMmLand',bounds_mm=[lo,yy-3,zz-9,hi,yy+3,zz]))
    rows.extend(p for p in bridge['recipes'][leg+'SourceCarrier']['pads']
        if 'BelowBandBridge' in p['name'] and not p['name'].split('BelowBandBridge')[0].endswith('1'))
    rows.extend(extra['recipes'][leg+'HipExtension']['pads'])
    return rows


def run():
    tick=time.monotonic();out=P.OUT/'axial-moving-supports';out.mkdir(exist_ok=True)
    planfile=P.OUT/'body-axial-layout-chosen.json';rootfile=P.OUT/'body-axial-rooted-arms-plan.json'
    plan,arms=[json.loads(f.read_text()) for f in (planfile,rootfile)]
    assert arms['status']=='EIGHT_ROOTED_SOURCE_ARMS_EXACT_SEGMENTS_CLEAR_UNION_NATIVE_OPEN'
    for n,h in arms['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    files=[P.OUT/n for n in ('complete-source-carriers-plan.json','leg-source-near-member-plan.json',
        'source-carrier-port-bridges-material.json','remaining-support-shared-material.json','remaining-supports/manifest.json')]
    roots,family,bridge,extra,native=[json.loads(f.read_text()) for f in files]
    source=P.ROOT/next(r['path'] for r in native['native_documents'] if r['path'].endswith('SourceCarriersCurrent.FCStd'))
    assert P.SHA(source)==next(r['sha256'] for r in native['native_documents'] if P.ROOT/r['path']==source)
    manifest_path=P.ROOT/next(n for n in arms['source_sha256'] if 'near-axis-retained-cache/' in n and n.endswith('/manifest.json'))
    retained=json.loads(manifest_path.read_text());files.extend([source,manifest_path,planfile,rootfile,Path(__file__)])
    records=[];exports=[];expected={};sketches=0
    def save(status):
        receipt=dict(status=status,parts=records,exports=exports,fully_constrained_new_sketches=sketches,
            source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='FourmovingHip1sourcearms/ports added to exact native retained subsets.4fixedsourceparents/36receiverarms/native/stock stillOPEN.4mm wire pilot, notlegstructure; physical fit/creep gateOPEN.')
        f=out/'manifest.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(receipt,indent=2)+'\n');tmp.replace(f)
    with tempfile.TemporaryDirectory(prefix='robot-cat-axial-native-') as td:
        copyfile=Path(td)/'AxialMovingSupports.FCStd';shutil.copy2(source,copyfile);d=A.openDocument(str(copyfile))
        par=d.addObject('App::VarSet','AxialParameters');par.addProperty('App::PropertyLength','ArmThickness');par.ArmThickness=4
        def box_feature(row,name,parameter=False):
            nonlocal sketches
            check_time();x,y,z,X,Y,Z=row['bounds_mm'];b=d.addObject('PartDesign::Body',name)
            sk=sketch(b,name+'Plan',z);rect(sk,x,y,X-x,Y-y)
            if row.get('placement'):sk.Placement=placement(row['placement'])*sk.Placement
            pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=sk
            if parameter:pad.setExpression('Length',f'{Z-z-4} mm + AxialParameters.ArmThickness')
            else:pad.Length=Z-z
            pad.Refine=True;b.Tip=pad;d.recompute();assert sk.FullyConstrained and not pad.Shape.isNull(),name
            sketches+=1;sk.Visibility=False;b.Visibility=False;return b
        def union(objects,name):
            q=d.addObject('Part::MultiFuse',name);q.Shapes=objects;q.Refine=True;d.recompute();q.Visibility=False;return q
        dest=out/'AxialMovingSupports.FCStd';partial=out/'AxialMovingSupports.partial.FCStd'
        assert not dest.exists(),'Do not overwrite received native output'
        try:
            for source_row in plan['hips']:
                check_time();leg=source_row['physical_leg'];name=leg+'HipExtension';old=d.getObject(leg+'SourceCarrier');assert old
                maskrows=positive_mask(leg,next(r for r in roots['roots'] if r['leg']==leg),family,bridge,extra)
                masks=[box_feature(row,name+'Mask'+str(i)) for i,row in enumerate(maskrows)]
                mask=union(masks,name+'PositiveMask')
                keep=d.addObject('Part::MultiCommon',name+'RetainedNative');keep.Shapes=[old,mask];keep.Refine=True;d.recompute()
                assert keep.Shape.isValid() and len(keep.Shape.Solids)==1 and not keep.Shape.check(True),name
                cached=retained['parts'][name];file=manifest_path.parent/cached['file'];assert P.SHA(file)==cached['sha256']
                target=Part.Shape();target.read(str(file));files.append(file)
                differences=[keep.Shape.cut(target).Volume,target.cut(keep.Shape).Volume]
                assert max(differences)<1e-4,(name,'Retained native mismatch',differences)
                _,port=C.make_port(source_row,True);recipe=port['recipe'];frame=recipe['local_to_world']
                pads=[box_feature(dict(row,placement=frame),name+'Seat'+str(i)) for i,row in enumerate(recipe['pads'])]
                seat=union(pads,name+'SeatPositive')
                outer=box_feature(dict(bounds_mm=recipe['ring_cut']['outer'],placement=frame),name+'RingOuter')
                inner=box_feature(dict(bounds_mm=recipe['ring_cut']['inner'],placement=frame),name+'RingInner')
                ring=d.addObject('Part::Cut',name+'Ring');ring.Base=outer;ring.Tool=inner;ring.Refine=True;d.recompute()
                cuts=[box_feature(dict(bounds_mm=v,placement=frame),name+'Slot'+str(i)) for i,v in enumerate(recipe['cuts'])]
                cutters=union([ring,*cuts],name+'SeatCutters')
                cutseat=d.addObject('Part::Cut',name+'PrecutSeat');cutseat.Base=seat;cutseat.Tool=cutters;cutseat.Refine=True;d.recompute()
                assert max(cutseat.Shape.cut(port['body']).Volume,port['body'].cut(cutseat.Shape).Volume)<1e-4,name
                arm=next(r for r in arms['groups'] if r['name']==name);points=arm['paths'][0]['points_mm'];arm_shapes=[];arm_bodies=[]
                for i,(a,b) in enumerate(zip(points,points[1:])):
                    s=arm_box(a,b,arm['arm_half_widths_world_mm']);bb=s.BoundBox;arm_shapes.append(s)
                    arm_bodies.append(box_feature(dict(bounds_mm=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax]),name+'Arm'+str(i),True))
                final=union([keep,cutseat,*arm_bodies],name+'Current')
                q=target.copy()
                for s in [port['body'],*arm_shapes]:q=q.fuse(s).removeSplitter()
                assert q.isValid() and len(q.Solids)==1 and not q.check(True),name
                assert final.Shape.isValid() and len(final.Shape.Solids)==1 and not final.Shape.check(True),name
                assert max(final.Shape.cut(q).Volume,q.cut(final.Shape).Volume)<1e-4,name
                assert target.cut(final.Shape).Volume<1e-4,name
                expected[name]=q
                records.append(dict(name=name,object=final.Name,retained_subset_difference_mm3=differences,
                    volume_mm3=final.Shape.Volume,solids=1,BOP_errors=0,fully_editable_sketch_mask_and_precut_seat=True))
                d.saveAs(str(partial));save('PARTIAL_NATIVE_AXIAL_MOVING_SUPPORTS')
                print('native moving support',name,'sketches',sketches,flush=True)
            par.ArmThickness=4.2;d.recompute()
            for row in records:
                s=d.getObject(row['object']).Shape;assert s.isValid() and len(s.Solids)==1 and s.Volume>row['volume_mm3'],row['name']
            par.ArmThickness=4;d.recompute()
            for row in records:assert abs(d.getObject(row['object']).Shape.Volume-row['volume_mm3'])<1e-4,row['name']
            for o in d.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            for row in records:d.getObject(row['object']).Visibility=True
            d.saveAs(str(dest));files.append(dest)
        finally:
            if par.ArmThickness.Value!=4:par.ArmThickness=4;d.recompute()
            if not dest.exists():d.saveAs(str(partial));save('INCOMPLETE_NATIVE_AXIAL_MOVING_SUPPORTS')
            A.closeDocument(d.Name)
        relocated=Path(td)/'Relocated.FCStd';shutil.copy2(dest,relocated);d=A.openDocument(str(relocated));d.recompute()
        try:
            for row in records:
                check_time();s=d.getObject(row['object']).Shape;q=expected[row['name']]
                assert s.isValid() and len(s.Solids)==1 and not s.check(True)
                assert max(s.cut(q).Volume,q.cut(s).Volume)<1e-4,row['name']
                orientation=print_orientation(s);assert orientation['fits_with_5mm_brim'],row['name']
                s=s.copy();s.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*s.Placement
                bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
                file=out/(row['name']+'_x1.stl');mesh.write(str(file));files.append(file)
                exports.append(dict(part=row['name'],path=file.relative_to(P.ROOT).as_posix(),sha256=P.SHA(file),printing=orientation))
                row.update(parameter_restore_mm=[4,4.2,4],relocated_reopen=True);save('PARTIAL_NATIVE_AXIAL_MOVING_EXPORTS')
        finally:A.closeDocument(d.Name)
    save('FOUR_AXIAL_MOVING_SUPPORTS_NATIVE_PREPARED_FULL_W5_OPEN')


if __name__=='__main__':run()
