"""Native five parent replacements for the qualified thirteen source lands.

Retain all prior native history. Only NEW pilots respond to the new Z allowance;
do not cycle339 old receiver features for a small source-support addition.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_current_harness_interfaces import ROOT,OUT,SHA,BASE
from check_main_p0_placement import SavedShapes
from current_native_receiver_primitives import Construction
from build_current_receiver_supports import editable_feed
from build_remaining_loom_supports import print_orientation
from plan_axial_source_supports import arm_box
from remaining_source_retention_material import saddle
from current_work_guard import check


def valid(s,n):assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
def equal(s,t,n):assert max(s.copy().cut(t.copy()).Volume,t.copy().cut(s.copy()).Volume)<1e-4,n


def run():
    check();tick=time.monotonic();pf=OUT/'local-source-retention-roots.json';plan=json.loads(pf.read_text())
    assert plan['status']=='THIRTEEN_LOCAL_SOURCE_ROOTS_EXACT_SEGMENTS_CLEAR_NATIVE_OPEN'
    assert len(plan['groups'])==13 and not plan['errors']
    for n,h in plan['source_sha256'].items():assert SHA(ROOT/n)==h,n
    receiver_file=OUT/'receiver-supports/manifest.json';receiver=json.loads(receiver_file.read_text())
    owners={r['part']:r['object'] for r in receiver['parts'] if r['kind']=='replacement_Frame'}
    families=[('Frames',OUT/'receiver-supports/ReceiverSupportsCurrent.FCStd',
                {n:obj for n,obj in owners.items() if n in {r['owner'] for r in plan['groups']}}),
              ('Upper',OUT/'upper-fixed-feed-supports/UpperFixedFeedSupportsCurrent.FCStd',
                {'UpperCarrier001':'UpperCarrierFixedFeedsCurrent'}),
              ('Neck',BASE/'head-mount-checkpoint/HeadNeckCurrent.FCStd',{'LeftRiser':'LeftRiser'})]
    assert sum(len(f[2]) for f in families)==5
    output=OUT/'local-source-retention-native';output.mkdir(exist_ok=True)
    assert not (output/'manifest.json').exists(),'Receive existing result, never regenerate unchanged'
    files={pf,receiver_file,Path(__file__),Path(__file__).with_name('remaining_source_retention_material.py'),
           Path(__file__).with_name('current_native_receiver_primitives.py'),
           Path(__file__).with_name('build_current_receiver_supports.py'),
           Path(__file__).with_name('plan_axial_source_supports.py'),Path(__file__).with_name('current_work_guard.py')}
    files.update(f[1] for f in families);records=[];models=[];exports=[];sketches=0
    def save(status):
        result=dict(status=status,parts=records,models=models,exports=exports,
            source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},
            worker_seconds=round(time.monotonic()-tick,3),fully_constrained_new_sketches=sketches,
            source_lacing_blanks=13,source_lacing_project_mm=1950,new_separate_prints=0,new_metal_fasteners=0,
            replaced_prints=sorted({r['owner'] for r in plan['groups']}),
            scope='Source insulation retention only; no extra Frame prints. Thirteen received lands/pilots. Original source case mounts/other25interfaces/assembly/stock remain OPEN.',
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False,stock_selected=False)
        f=output/'manifest.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f)
    save('LOCAL_SOURCE_NATIVE_STARTED')
    reader=SavedShapes()
    for family,src,parent_names in families:
        check();final=output/(family+'SourceRetentionCurrent.FCStd');partial=output/(family+'SourceRetention.partial.FCStd')
        assert not final.exists() and not partial.exists(),'Receive existing native family before starting'
        with tempfile.TemporaryDirectory(prefix='robot-cat-source-native-') as td:
            work=Path(td)/(family+'Source.FCStd');shutil.copy2(src,work);doc=A.openDocument(str(work))
            ops=Construction(doc);par=doc.addObject('App::VarSet','SourceRetentionParameters')
            par.addProperty('App::PropertyLength','BeamZAllowance');par.BeamZAllowance=0
            local=[];baseline={};original={}
            try:
                for owner,parent_name in parent_names.items():
                    check();parent=doc.getObject(parent_name);assert parent
                    saved=reader.shape(src,parent_name);equal(parent.Shape,saved,owner+'sourceworlddatum')
                    original[owner]=parent.Shape.copy();children=[parent];groups=[];bands=[]
                    for row in (r for r in plan['groups'] if r['owner']==owner):
                        check();gid=row['id'];profile=saddle(row['recipe'])
                        assert profile['recipe']==row['recipe']['saddle']
                        seat=editable_feed(ops,profile['recipe'],'SourceSeat'+gid)
                        equal(seat.Shape,profile['body'],gid+'seat');children.append(seat)
                        ref=doc.addObject('Part::Feature','SourceLacing'+gid);ref.Shape=profile['band'];ref.Visibility=False
                        bands.append(ref.Name);groups.append(gid)
                        for i,(a,b) in enumerate(zip(row['path'],row['path'][1:])):
                            s=arm_box(a,b,plan['arm_half_widths_world_mm']);b=s.BoundBox
                            arm=ops.box([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'SourcePilot'+gid+'N'+str(i))
                            arm.Tip.setExpression('Length',str(b.ZLength)+' mm + SourceRetentionParameters.BeamZAllowance')
                            doc.recompute();equal(arm.Shape,s,gid+'pilot');children.append(arm)
                    current=ops.fuse(children,owner+'SourceRetentionCurrent');valid(current.Shape,owner)
                    assert original[owner].copy().cut(current.Shape.copy()).Volume<1e-5,owner+'lost retained material'
                    baseline[owner]=current.Shape.copy()
                    item=dict(part=owner,object=current.Name,native=final.relative_to(ROOT).as_posix(),quantity=1,
                              prior_parent_object=parent_name,retained_native_history=True,source_groups=groups,
                              lacing_reference_objects=bands,volume_mm3=current.Shape.Volume)
                    records.append(item);local.append(item)
                    doc.saveAs(str(partial));sketches+=ops.sketches;ops.sketches=0
                    save('LOCAL_SOURCE_NATIVE_PARTIAL_PARENTS');print('source native parent saved',owner,flush=True)
                par.BeamZAllowance=.2;doc.recompute()
                for r in local:
                    check();s=doc.getObject(r['object']).Shape;valid(s,r['part'])
                    assert s.Volume>r['volume_mm3'],r['part']+'new pilot parameter did not change material'
                par.BeamZAllowance=0;doc.recompute()
                for r in local:equal(doc.getObject(r['object']).Shape,baseline[r['part']],r['part']+'restored')
                for o in doc.Objects:
                    if hasattr(o,'Visibility'):o.Visibility=False
                for r in local:doc.getObject(r['object']).Visibility=True
                doc.saveAs(str(final));models.append(dict(path=final.relative_to(ROOT).as_posix(),sha256=SHA(final),family=family,
                    partial_path=partial.relative_to(ROOT).as_posix(),partial_sha256=SHA(partial)))
                save('LOCAL_SOURCE_NATIVE_PARAMETERS_CLEAR_REOPEN_OPEN')
            finally:
                if par.BeamZAllowance.Value!=0:par.BeamZAllowance=0;doc.recompute()
                A.closeDocument(doc.Name)
            moved=Path(td)/'RelocatedSource.FCStd';shutil.copy2(final,moved);doc=A.openDocument(str(moved));doc.recompute()
            try:
                for r in local:
                    check();s=doc.getObject(r['object']).Shape;valid(s,r['part']);equal(s,baseline[r['part']],r['part']+'reopen')
                    orientation=print_orientation(s);assert orientation['fits_with_5mm_brim'],r['part']
                    shape=s.copy();shape.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*shape.Placement
                    bb=shape.BoundBox;shape.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                    assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1,r['part']
                    f=output/(r['part']+'_source_retained_x1.stl');mesh.write(str(f))
                    r.update(beam_Z_allowance_restore_mm=[0,.2,0],relocated_reopen=True,original_material_preserved=True)
                    exports.append(dict(part=r['part'],path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),quantity=1,printing=orientation))
                    save('LOCAL_SOURCE_NATIVE_PARTIAL_EXPORTS');print('source native export',r['part'],flush=True)
            finally:A.closeDocument(doc.Name)
    assert len(records)==len(exports)==5 and len(models)==3
    save('THIRTEEN_SOURCE_LANDS_FIVE_NATIVE_PARENT_REPLACEMENTS_COMPLETE')


if __name__=='__main__':run()
