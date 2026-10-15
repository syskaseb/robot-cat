"""One editable fixed Frame set; add each frozen received receiver owner once.

Source-rooted bases are independent of remaining core middles. Receiver
additions wait for exact owner proofs, never guess a missing root. No original
native file is overwritten. Deadline preserves a partial, unselected document.
"""
import json,shutil,tempfile,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import core_receiver_port as T
import check_near_axis_hip_sources as C
from native_support_primitives import Construction
from build_axial_moving_supports_native import check_time
from build_remaining_loom_supports import print_orientation
from plan_axial_source_supports import arm_box
P=C.P


def valid(s,name):assert s.isValid() and len(s.Solids)==1 and not s.check(True),name


def run():
    tick=time.monotonic();out=P.OUT/'current-fixed-receiver-supports';out.mkdir(exist_ok=True)
    files=[P.OUT/n for n in ('fixed-native-retained-masks.json','body-axial-rooted-arms-plan.json','body-axial-layout-chosen.json','body-low-hip-retention-plan.json')]
    masks,sourcearms,sources,retained=[json.loads(f.read_text()) for f in files]
    assert masks['status']=='FOUR_FIXED_NATIVE_POSITIVE_MASKS_EXACT_RETAINED_SUBSETS'
    for receipt in (masks,sourcearms):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    src=P.ROOT/masks['source_native'];files.extend([src,Path(__file__),Path(__file__).with_name('native_support_primitives.py')])
    archive=P.ROOT/retained['archive'];files.append(archive);expected={}
    with zipfile.ZipFile(archive) as z:
        index=json.loads(z.read('index.json'))
        for row in masks['parts']:
            item=next(r for r in index if r['name']=='Retained_'+row['name']);s=Part.Shape();s.importBrepFromString(z.read(item['file']).decode());expected[row['name']]=s
    bases={};records=[];exports=[];source_records=[];ops=None
    def save(status):
        receipt=dict(status=status,source_bases=source_records,parts=records,exports=exports,
            fully_constrained_new_sketches=ops.sketches if ops else 0,
            source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
            worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
            scope='4fixedFrames with received source/receiver roots, precut independent grips. Missing owner proofs are not accepted. Full W5/19otherguide restraints/stock/release remainOPEN.')
        file=out/'manifest.json';tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(receipt,indent=2)+'\n');tmp.replace(file)
    partial=out/'FixedReceiverSupports.partial.FCStd';dest=out/'FixedReceiverSupports.FCStd';assert not dest.exists()
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-receivers-') as td:
        copyfile=Path(td)/'FixedReceiverSupports.FCStd';shutil.copy2(src,copyfile);d=A.openDocument(str(copyfile));ops=Construction(d)
        par=d.addObject('App::VarSet','ReceiverParameters');par.addProperty('App::PropertyLength','ArmThickness');par.ArmThickness=4
        try:
            for row in masks['parts']:
                check_time();name=row['name'];original=d.getObject(row['original_native_body']);bare=d.getObject(row['bare_native_tip']);assert original and bare
                pads=[ops.box(p['bounds_mm'],name+'Mask'+str(i),p.get('placement')) for i,p in enumerate(row['positive_pads'])]
                mask=ops.fuse([bare,*pads],name+'PositiveMask')
                keep=d.addObject('Part::MultiCommon',name+'Retained');keep.Shapes=[original,mask];keep.Refine=True;d.recompute();valid(keep.Shape,name)
                q=expected[name];assert max(keep.Shape.cut(q).Volume,q.cut(keep.Shape).Volume)<1e-4,name
                source=next(r for r in sources['hips'] if r['physical_leg']+'FixedCarrier'==name);_,port=C.make_port(source,False)
                seat=ops.seat(port['recipe'],name+'SourceSeat');assert max(seat.Shape.cut(port['body']).Volume,port['body'].cut(seat.Shape).Volume)<1e-4,name
                points=next(r for r in sourcearms['groups'] if r['name']==name)['paths'][0]['points_mm'];objects=[]
                q=q.fuse(port['body']).removeSplitter()
                for i,(a,b) in enumerate(zip(points,points[1:])):
                    s=arm_box(a,b,(2,2,2));q=q.fuse(s).removeSplitter();objects.append(ops.arm(s,name+'SourceArm'+str(i)))
                base=ops.fuse([keep,seat,*objects],name+'SourceRooted');valid(base.Shape,name);valid(q,name)
                assert max(base.Shape.cut(q).Volume,q.cut(base.Shape).Volume)<1e-4,name
                bases[name]=base;expected[name]=q;source_records.append(dict(name=name,volume_mm3=q.Volume,BOP_errors=0,solids=1))
                d.saveAs(str(partial));save('PARTIAL_SOURCE_ROOTED_FIXED_NATIVE_RECEIVERS_OPEN');print('fixed native source base',name,flush=True)
            for name,base in bases.items():
                ownerfile=P.OUT/('body36-receiver-roots-'+name+'.json')
                print('waiting frozen receiver owner',name,flush=True)
                while not ownerfile.exists():check_time();time.sleep(5)
                proof=json.loads(ownerfile.read_text());assert proof['status']=='OWNER_RECEIVER_ROOTS_EXACT_CLEAR_NATIVE_OPEN' and proof['owner']==name
                for n,h in proof['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
                files.append(ownerfile);gf=P.OUT/'body36-receiver-selected.json';grips=json.loads(gf.read_text());files.append(gf)
                objects=[];q=expected[name]
                for group in proof['groups']:
                    check_time();wire=group['wire'];g=grips['grips'][wire];profile=T.build(g['land'],g['normal'],g['offset'])
                    seat=ops.seat(profile['recipe'],name+wire+'Seat');objects.append(seat);q=q.fuse(profile['body']).removeSplitter()
                    assert max(seat.Shape.cut(profile['body']).Volume,profile['body'].cut(seat.Shape).Volume)<1e-4,wire
                    points=group['paths'][0]['points_mm']
                    for i,(a,b) in enumerate(zip(points,points[1:])):
                        s=arm_box(a,b,(2,2,2));q=q.fuse(s).removeSplitter();objects.append(ops.arm(s,name+wire+'Arm'+str(i)))
                final=ops.fuse([base,*objects],name+'Current');valid(q,name);valid(final.Shape,name)
                assert max(final.Shape.cut(q).Volume,q.cut(final.Shape).Volume)<1e-4,name
                expected[name]=q;records.append(dict(name=name,object=final.Name,receiver_grips=len(proof['groups']),volume_mm3=q.Volume,BOP_errors=0,solids=1))
                d.saveAs(str(partial));save('PARTIAL_CURRENT_FIXED_RECEIVER_NATIVE');print('fixed receiver native',name,len(proof['groups']),flush=True)
            par.ArmThickness=4.2;d.recompute()
            for row in records:valid(d.getObject(row['object']).Shape,row['name']);assert d.getObject(row['object']).Shape.Volume>row['volume_mm3']
            par.ArmThickness=4;d.recompute()
            for row in records:assert abs(d.getObject(row['object']).Shape.Volume-row['volume_mm3'])<1e-4
            for o in d.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            for row in records:d.getObject(row['object']).Visibility=True
            d.saveAs(str(dest));files.append(dest)
        finally:
            if par.ArmThickness.Value!=4:par.ArmThickness=4;d.recompute()
            if not dest.exists():d.saveAs(str(partial));save('INCOMPLETE_CURRENT_FIXED_RECEIVER_NATIVE')
            A.closeDocument(d.Name)
        reopened=Path(td)/'Relocated.FCStd';shutil.copy2(dest,reopened);d=A.openDocument(str(reopened));d.recompute()
        try:
            for row in records:
                check_time();s=d.getObject(row['object']).Shape;valid(s,row['name']);q=expected[row['name']]
                assert max(s.cut(q).Volume,q.cut(s).Volume)<1e-4
                printing=print_orientation(s);assert printing['fits_with_5mm_brim'],row['name']
                s=s.copy();s.Placement=A.Placement(A.Vector(),A.Rotation(*printing['rotation_quaternion']))*s.Placement
                bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
                file=out/(row['name']+'_x1.stl');mesh.write(str(file));files.append(file)
                exports.append(dict(part=row['name'],path=file.relative_to(P.ROOT).as_posix(),sha256=P.SHA(file),printing=printing))
                row.update(parameter_restore_mm=[4,4.2,4],relocated_reopen=True);save('PARTIAL_CURRENT_FIXED_RECEIVER_EXPORTS')
        finally:A.closeDocument(d.Name)
    save('FOUR_FIXED_RECEIVER_CARRIERS_NATIVE_PREPARED_FULL_W5_OPEN')


if __name__=='__main__':run()
