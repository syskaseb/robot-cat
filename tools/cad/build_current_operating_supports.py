"""Build ONE current operating support set after all38 shared root gates.

Copies preserve editable native history. Four owner replacements and one
detachable rail, not dozens of duplicate Frames. Save each owner before
parameter checks; no cosmetic shell, power or physical acceptance.
"""
import argparse,json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from plan_current_harness_interfaces import ROOT,OUT,SHA
from current_native_receiver_primitives import Construction
from current_bank_operating_native import rail_parts,bank_seat,case_backer,equal
from build_current_receiver_supports import editable_feed
from build_remaining_frame_saddles import native_recipe
from build_remaining_loom_supports import print_orientation
from plan_axial_source_supports import arm_box
from plan_remaining25_restraint_space import profile
from loom_land_port import box
from current_work_guard import check


def valid(s,name):assert s.isValid() and len(s.Solids)==1 and not s.check(True),name


def run(resume=False):
    check();tick=time.monotonic()
    files=[OUT/(n+'.json') for n in ('current-upper-operating-roots','individual-bank-roots',
        'bank-prototype-service-plan','current-body-native-composition','local-source-retention-native/manifest',
        'source-case-retention-space')]
    roots,bank,plan,composition,source,preflight=[json.loads(f.read_text()) for f in files]
    saddles_file=OUT/'remaining25-restraint-space.json';files.append(saddles_file)
    saddle_groups={g['id']:g for g in json.loads(saddles_file.read_text())['spatial_groups']}
    assert roots['accepted']==38 and not roots['errors']
    assert len(preflight['parts'])==24 and not any(r['contacts'] for r in preflight['parts'])
    for receipt in (roots,bank,plan,composition,source,preflight):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert bank['accepted']==12 and roots['normal_wires_unchanged'] and not roots['in_robot_parking']
    paths={p['part']:p for p in composition['prints']}
    upper=next(p for p in source['parts'] if p['part']=='UpperCarrier001')
    # Only Upper's explicitly retired21 children are omitted from new tips.
    # Historical features remain in this copied document, hidden, not deleted.
    jobs=[('Upper',ROOT/upper['native'],['UpperCarrier001']),
          ('Frames',ROOT/paths['FrontRightFixedCarrier']['native'],
           ['FrontRightFixedCarrier','RearLeftFixedCarrier','RearRightFixedCarrier'])]
    files.extend([f for _,f,_ in jobs]+[Path(__file__),Path(__file__).with_name('current_bank_operating_native.py'),
        Path(__file__).with_name('current_native_receiver_primitives.py'),Path(__file__).with_name('build_remaining_loom_supports.py')])
    pins={f.relative_to(ROOT).as_posix():SHA(f) for f in files}
    output=OUT/'operating-supports-native';output.mkdir(exist_ok=True)
    manifest=output/'manifest.json';assert resume or not manifest.exists(),'Receive existing native work or explicitly resume'
    records=[];exports=[];models=[];partials=[];sketches=0;reference_records=[];baselines={};progress=None
    if resume:
        old=json.loads(manifest.read_text());assert old['source_sha256']==pins
        records=old['parts'];exports=old['exports'];models=old['models'];partials=old['partial_models']
        sketches=old['fully_constrained_new_sketches'];reference_records=old['reference_objects']
        progress=old.get('in_progress_owner')
        for r in partials+models:assert SHA(ROOT/r['path'])==r['sha256']
        assert len(exports)<5,'Receive completed result; do not rebuild'
    def save(status):
        p=dict(status=status,parts=records,exports=exports,models=models,partial_models=partials,in_progress_owner=progress,reference_objects=reference_records,
            source_sha256=pins,fully_constrained_new_sketches=sketches,worker_seconds=round(time.monotonic()-tick,3),
            replacement_parent_quantity=4,detachable_rail_quantity=1,retained_unchanged_FrontLeft_Frame_quantity=1,
            new_rail_hardware_candidate={'M3x8':2,'M3_nut':2,'M3_washer':2},new_case_laces=0,
            lacing_blanks_Upper_wire=24,lacing_blanks_rail=4,
            case_only_adhesive_patches=12,case_adhesive_NOT_wire_restraint=True,
            selected=False,stock_selected=False,W5_complete=False,A2_complete=False,physical_pass=False,
            scope='Operating support native contribution only. Full assembly/unpowered handling and stock selection remain separate gates.')
        tmp=manifest.with_suffix('.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(manifest)
    save('OPERATING_SUPPORTS_NATIVE_PREPARING')
    for label,src,owners in jobs:
        check();final=output/(label+'OperatingCurrent.FCStd');partial=output/(label+'Operating.partial.FCStd')
        job_parts=set(owners)|({'SourceGripRail'} if label=='Upper' else set())
        if job_parts<={r['part'] for r in exports}:continue
        with tempfile.TemporaryDirectory(prefix='robot-cat-operating-native-') as td:
            work=Path(td)/src.name;shutil.copy2(partial if resume and partial.exists() else src,work);d=A.openDocument(str(work));ops=Construction(d)
            par=d.getObject('OperatingParameters')
            if par is None:
                par=d.addObject('App::VarSet','OperatingParameters');par.addProperty('App::PropertyLength','PilotZAllowance');par.PilotZAllowance=0
            assert par.PilotZAllowance.Value==0
            for r in records:
                if r['native']==final.relative_to(ROOT).as_posix():baselines[r['part']]=d.getObject(r['object']).Shape.copy()
            rail=None
            try:
                rail_bosses={}
                if progress and progress['owner']=='UpperCarrier001':
                    rail_bosses={n:d.getObject(o) for n,o in progress['rail_boss_objects'].items()}
                if label=='Upper' and not any(r['part']=='SourceGripRail' for r in records):
                    rail,rail_bosses,q=rail_parts(ops,plan);valid(rail.Shape,'Source rail')
                    records.append(dict(part='SourceGripRail',object=rail.Name,native=final.relative_to(ROOT).as_posix(),quantity=1,volume_mm3=rail.Shape.Volume,retained_native_history=True))
                    baselines['SourceGripRail']=rail.Shape.copy()
                    for name,s in {**q['hardware'],**{'SourceLacing/'+n:s for n,s in q['bands'].items()}}.items():
                        ref=d.addObject('Part::Feature','Ref_'+name);ref.Shape=s;ref.Visibility=False
                        reference_records.append(dict(part=name,object=ref.Name,native=final.relative_to(ROOT).as_posix(),not_printable=True))
                for owner in owners:
                    if any(r['part']==owner for r in records):continue
                    check();base=d.getObject('UpperCarrierFixedFeedsCurrent' if owner=='UpperCarrier001' else paths[owner]['native_object']);assert base
                    original=base.Shape.copy()
                    if progress and progress['owner']==owner:
                        children=[d.getObject(n) for n in progress['children']];assert all(children)
                        seen_arms={tuple(v) for v in progress['seen_arm_bounds']}
                    else:
                        children=[base];seen_arms=set()
                        progress=dict(owner=owner,children=[base.Name],seen_arm_bounds=[],bank_group_ids=[],operating_group_ids=[],
                            rail_boss_objects={n:o.Name for n,o in rail_bosses.items()})
                    def checkpoint_progress():
                        nonlocal sketches
                        progress.update(children=[o.Name for o in children],seen_arm_bounds=[list(v) for v in sorted(seen_arms)])
                        sketches+=ops.sketches;ops.sketches=0;d.saveAs(str(partial))
                        partials[:]=[r for r in partials if r['path']!=partial.relative_to(ROOT).as_posix()]
                        partials.append(dict(path=partial.relative_to(ROOT).as_posix(),sha256=SHA(partial)))
                        save('OPERATING_NATIVE_EDITABLE_GROUPS_SAVED');print('operating native groups saved',owner,len(progress['bank_group_ids']),len(progress['operating_group_ids']),flush=True)
                    def add_arm(a,b,half,name):
                        s=arm_box(a,b,half);bb=s.BoundBox;values=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax]
                        key=tuple(round(v,8) for v in values)
                        if key in seen_arms:return
                        seen_arms.add(key);obj=ops.box(values,name)
                        obj.Tip.setExpression('Length',str(bb.ZLength)+' mm + OperatingParameters.PilotZAllowance')
                        d.recompute();equal(obj.Shape,s,name);children.append(obj)
                    if owner=='UpperCarrier001':
                        for r in bank['groups']:
                            if r['id'] in progress['bank_group_ids']:continue
                            rec=r['seat_recipe'];seat=bank_seat(ops,rec,'OperatingBank'+r['id']);children.append(seat)
                            add_arm(*r['leaf_points'],bank['leaf_half_mm'],'OperatingBankLeaf'+r['id'])
                            for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):add_arm(a,b,bank['trunk_half_mm'],'OperatingBankTrunk'+r['id']+str(i))
                            progress['bank_group_ids'].append(r['id'])
                            if len(progress['bank_group_ids'])%4==0:checkpoint_progress()
                    for r in (r for r in roots['groups'] if r['owner']==owner):
                        check();gid=r['id'];rec=r['recipe']
                        if gid in progress['operating_group_ids']:continue
                        if r['kind']=='wire_saddle':
                            seat=editable_feed(ops,native_recipe(rec),'OperatingSeat'+gid)
                            q=profile(saddle_groups[gid],rec['normal'],rec['knot_sign']);assert q['recipe']==rec
                            equal(seat.Shape,q['body'],gid+'native saddle')
                            ref=d.addObject('Part::Feature','Ref_OperatingLacing'+gid);ref.Shape=q['band'];ref.Visibility=False
                            reference_records.append(dict(part='WireLacing/'+gid,object=ref.Name,native=final.relative_to(ROOT).as_posix(),not_printable=True))
                        elif r['kind']=='structural_station':seat=rail_bosses[gid]
                        else:
                            seat=case_backer(ops,rec,'OperatingCase'+gid)
                            ref=d.addObject('Part::Feature','Ref_OperatingCaseAdhesive'+gid);ref.Shape=box(rec['adhesive_bounds_mm']);ref.Visibility=False
                            reference_records.append(dict(part='CaseAdhesive/'+gid,object=ref.Name,native=final.relative_to(ROOT).as_posix(),not_printable=True))
                        children.append(seat)
                        for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):add_arm(a,b,r['half_mm'],'OperatingPilot'+gid+'N'+str(i))
                        progress['operating_group_ids'].append(gid)
                        if len(progress['operating_group_ids'])%4==0:checkpoint_progress()
                    checkpoint_progress()
                    current=ops.fuse(children,owner+'OperatingCurrent');valid(current.Shape,owner)
                    assert original.cut(current.Shape.copy()).Volume<1e-5,owner+' lost retained material'
                    baselines[owner]=current.Shape.copy();records.append(dict(part=owner,object=current.Name,native=final.relative_to(ROOT).as_posix(),quantity=1,
                        volume_mm3=current.Shape.Volume,retained_native_history=True,original_material_preserved=True))
                    sketches+=ops.sketches;ops.sketches=0;d.saveAs(str(partial))
                    partials[:]=[r for r in partials if r['path']!=partial.relative_to(ROOT).as_posix()]
                    partials.append(dict(path=partial.relative_to(ROOT).as_posix(),sha256=SHA(partial)))
                    progress=None
                    save('OPERATING_NATIVE_OWNER_SAVED');print('operating native saved',owner,flush=True)
                local=[r for r in records if r['native']==final.relative_to(ROOT).as_posix()]
                par.PilotZAllowance=.2;d.recompute();changed=False
                for r in local:
                    check();s=d.getObject(r['object']).Shape;valid(s,r['part'])
                    changed|=abs(s.Volume-r['volume_mm3'])>1e-4
                assert changed,'Meaningful pilot allowance parameter must affect material'
                par.PilotZAllowance=0;d.recompute()
                for r in local:equal(d.getObject(r['object']).Shape,baselines[r['part']],r['part']+'parameter restore');r['parameter_restore_mm']=[0,.2,0]
                for o in d.Objects:
                    if hasattr(o,'Visibility'):o.Visibility=False
                for r in local:d.getObject(r['object']).Visibility=True
                d.saveAs(str(final));models[:]=[r for r in models if r['path']!=final.relative_to(ROOT).as_posix()]
                models.append(dict(path=final.relative_to(ROOT).as_posix(),sha256=SHA(final)))
                save('OPERATING_NATIVE_PARAMETERS_CLEAR_REOPEN_OPEN')
            finally:
                if par.PilotZAllowance.Value!=0:par.PilotZAllowance=0;d.recompute()
                A.closeDocument(d.Name)
            relocated=Path(td)/('Relocated'+label+'.FCStd');shutil.copy2(final,relocated);d=A.openDocument(str(relocated));d.recompute()
            try:
                for r in local:
                    if any(e['part']==r['part'] for e in exports):continue
                    check();s=d.getObject(r['object']).Shape;valid(s,r['part']);equal(s,baselines[r['part']],r['part']+' relocated reopen')
                    orientation=print_orientation(s);assert orientation['fits_with_5mm_brim']
                    shape=s.copy();shape.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*shape.Placement
                    bb=shape.BoundBox;shape.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
                    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
                    assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
                    f=output/(r['part']+'_operating_x1.stl');mesh.write(str(f));r['relocated_reopen']=True
                    exports.append(dict(part=r['part'],path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),quantity=1,printing=orientation))
                    save('OPERATING_NATIVE_EXPORTS_PARTIAL');print('operating native export',r['part'],flush=True)
            finally:A.closeDocument(d.Name)
    assert len(records)==len(exports)==5;save('FIVE_OPERATING_NATIVE_PRINT_REPLACEMENTS_COMPLETE')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');run(parser.parse_args().resume)
