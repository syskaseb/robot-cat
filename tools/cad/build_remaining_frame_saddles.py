"""Thirty unchanged allocated wire saddles on four current native Frames.

Independent of unresolved Upper bank/G1 service. Preserve original editable
history, source13 and receiver36 geometry. Four replacements, not extra Frames.
Never rebuild unchanged upstream modules or overwrite their historical files.
"""
import argparse,json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_current_harness_interfaces import ROOT,OUT,SHA
from plan_remaining25_restraint_space import profile
from current_native_receiver_primitives import Construction
from build_current_receiver_supports import editable_feed
from build_remaining_loom_supports import print_orientation
from plan_axial_source_supports import arm_box
from check_main_p0_placement import SavedShapes
from current_work_guard import check


def valid(s,n):assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
def equal(a,b,n):assert max(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume)<1e-4,n


def native_recipe(recipe):
    # The frozen allocation uses raw pad bounds; editable_feed consumes named
    # bounds records. Only adapt representation, never move or resize a pad.
    return dict(recipe,pads=[dict(bounds_mm=list(v)) for v in recipe['pads']])


def run(resume=False):
    check();tick=time.monotonic()
    files=[OUT/(n+'.json') for n in ('remaining25-restraint-space','remaining25-saddle-roots','current-body-source-native-set')]
    saddles,roots,current=[json.loads(f.read_text()) for f in files]
    assert roots['accepted_groups']==54 and not roots['errors']
    for p in (saddles,roots,current):
        for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    groups={g['id']:g for g in saddles['spatial_groups']}
    chosen=[r for r in roots['groups'] if r['owner'].endswith('FixedCarrier')]
    assert len(chosen)==30 and len({r['owner'] for r in chosen})==4
    owners={p['part']:p for p in current['prints'] if p['part'].endswith('FixedCarrier')}
    source=OUT/'local-source-retention-native/FramesSourceRetentionCurrent.FCStd'
    files.extend([source,Path(__file__),Path(__file__).with_name('plan_remaining25_restraint_space.py'),
        Path(__file__).with_name('current_native_receiver_primitives.py'),Path(__file__).with_name('build_current_receiver_supports.py'),
        Path(__file__).with_name('plan_axial_source_supports.py'),Path(__file__).with_name('build_remaining_loom_supports.py')])
    output=OUT/'remaining-frame-saddles-native';output.mkdir(exist_ok=True)
    partial=output/'RemainingFrameSaddles.partial.FCStd';final=output/'RemainingFrameSaddlesCurrent.FCStd';manifest=output/'manifest.json'
    pins={f.relative_to(ROOT).as_posix():SHA(f) for f in files};records=[];exports=[];sketches=0;reader=SavedShapes()
    if resume:
        old=json.loads(manifest.read_text());assert old['source_sha256']==pins and not old.get('errors')
        assert SHA(partial)==old['partial_sha256']
        records=old['parts'];exports=old['exports'];sketches=old['fully_constrained_new_sketches']
        assert not exports,'Receive completed native exports; no duplicate rebuild'
    else:assert not partial.exists() and not final.exists() and not manifest.exists(),'Receive existing result or explicitly resume'
    def save(status):
        data=dict(status=status,parts=records,exports=exports,source_sha256=pins,
            fully_constrained_new_sketches=sketches,worker_seconds=round(time.monotonic()-tick,3),
            partial_path=partial.relative_to(ROOT).as_posix(),partial_sha256=SHA(partial) if partial.exists() else None,
            native=final.relative_to(ROOT).as_posix(),native_sha256=SHA(final) if final.exists() else None,
            changed_groups=30,new_lacing_blanks=30,new_lacing_candidate_mm=4500,new_separate_prints=0,
            replacement_Frame_quantity=4,retained_receiver_CAP_quantity=7,
            scope='Only30 qualified unchanged saddle/root groups assigned to4Frames. Original receiver/source features remain; Upper24groups/bank/G1/current whole service and stock are OPEN.',
            selected=False,stock_selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        tmp=manifest.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(manifest)
    save('FOUR_FRAME_THIRTY_SADDLES_NATIVE_PREPARING')
    with tempfile.TemporaryDirectory(prefix='robot-cat-remaining-frames-') as td:
        work=Path(td)/'Frames.FCStd';shutil.copy2(partial if resume else source,work)
        doc=A.openDocument(str(work));ops=Construction(doc);baseline={}
        par=doc.getObject('RemainingFrameParameters') if resume else doc.addObject('App::VarSet','RemainingFrameParameters')
        if not resume:par.addProperty('App::PropertyLength','PilotZAllowance');par.PilotZAllowance=0
        assert par.PilotZAllowance.Value==0
        try:
            complete={r['part'] for r in records}
            for r in records:baseline[r['part']]=doc.getObject(r['object']).Shape.copy()
            for owner,ref in owners.items():
                if owner in complete:continue
                check();parent=doc.getObject(ref['native_object']);assert parent,ref['native_object']
                original_file=ROOT/ref['native'] if ref['native'].startswith('hardware/') else OUT/ref['native']
                frozen=reader.shape(original_file,ref['native_object']);equal(parent.Shape,frozen,owner+'source binding')
                original=parent.Shape.copy();children=[parent];ids=[];band_refs=[]
                for r in (r for r in chosen if r['owner']==owner):
                    check();gid=r['id'];rec=r['recipe'];q=profile(groups[gid],rec['normal'],rec['knot_sign'])
                    assert q['recipe']==rec
                    seat=editable_feed(ops,native_recipe(rec),'RemainingSeat'+gid);equal(seat.Shape,q['body'],gid+'native seat');children.append(seat)
                    band=doc.addObject('Part::Feature','RemainingLacing'+gid);band.Shape=q['band'];band.Visibility=False;band_refs.append(band.Name)
                    for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):
                        s=arm_box(a,b,roots['arm_half_widths_mm']);b=s.BoundBox
                        arm=ops.box([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'RemainingPilot'+gid+'N'+str(i))
                        arm.Tip.setExpression('Length',str(b.ZLength)+' mm + RemainingFrameParameters.PilotZAllowance')
                        doc.recompute();equal(arm.Shape,s,gid+'native pilot');children.append(arm)
                    ids.append(gid)
                current_tip=ops.fuse(children,owner+'RemainingSaddlesCurrent');valid(current_tip.Shape,owner)
                assert original.cut(current_tip.Shape.copy()).Volume<1e-5,owner+'lost prior geometry'
                baseline[owner]=current_tip.Shape.copy()
                records.append(dict(part=owner,object=current_tip.Name,prior_parent_object=parent.Name,
                    groups=ids,lacing_reference_objects=band_refs,volume_mm3=current_tip.Shape.Volume,quantity=1,
                    original_material_preserved=True,retained_native_history=True))
                sketches+=ops.sketches;ops.sketches=0;doc.saveAs(str(partial));save('FOUR_FRAME_NATIVE_PARENTS_PARTIAL')
                print('remaining Frame native saved',owner,len(ids),flush=True)
            par.PilotZAllowance=.2;doc.recompute()
            for r in records:
                check();s=doc.getObject(r['object']).Shape;valid(s,r['part']);assert s.Volume>r['volume_mm3']
            par.PilotZAllowance=0;doc.recompute()
            for r in records:equal(doc.getObject(r['object']).Shape,baseline[r['part']],r['part']+'parameter restored')
            for o in doc.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            for r in records:doc.getObject(r['object']).Visibility=True;r['pilot_Z_allowance_restore_mm']=[0,.2,0]
            doc.saveAs(str(final));save('FOUR_FRAME_PARAMETERS_CLEAR_REOPEN_OPEN')
        finally:
            if par.PilotZAllowance.Value!=0:par.PilotZAllowance=0;doc.recompute()
            A.closeDocument(doc.Name)
        moved=Path(td)/'RelocatedFrames.FCStd';shutil.copy2(final,moved);doc=A.openDocument(str(moved));doc.recompute()
        try:
            for r in records:
                check();s=doc.getObject(r['object']).Shape;valid(s,r['part']);equal(s,baseline[r['part']],r['part']+'relocated reopen')
                orientation=print_orientation(s);assert orientation['fits_with_5mm_brim']
                shape=s.copy();shape.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*shape.Placement
                b=shape.BoundBox;shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
                mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
                f=output/(r['part']+'_remaining_saddles_x1.stl');mesh.write(str(f));r['relocated_reopen']=True
                exports.append(dict(part=r['part'],path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),quantity=1,printing=orientation))
                save('FOUR_FRAME_NATIVE_EXPORTS_PARTIAL');print('remaining Frame native export',r['part'],flush=True)
        finally:A.closeDocument(doc.Name)
    assert len(records)==len(exports)==4;save('FOUR_CURRENT_FRAMES_THIRTY_SADDLES_NATIVE_COMPLETE')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');run(parser.parse_args().resume)
