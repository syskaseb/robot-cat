"""Finish the two owned remote seats without repeating unchanged harness pairs.

R2 received all external material pairs. Its four failures are the planned
strap lanes against the uncut NEW seats, not four unknown collisions. Apply
those same slots to BOTH seat and parent, then inspect the changed interfaces.
BUS/MAIN retain their received existing straps. No new route or connector.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, shutil, tempfile
import w5_remote_end_layout as R
from servo_fuse_inputs_r1 import sha, save

ROOT=R.ROOT; OUT=R.BASE/'w5-remote-end-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-remote-end-native-r1'
PARENTS={
    'BAT':('battery-feed-mount-finish-r2/BatteryFeedBridge.FCStd','FinishedBatteryFeedBridge','SourceBridge'),
    'AUX':('w5-loom-fixed-native-r1/WholeHarnessFixedLoomFrames.FCStd','FixedLoomDeckFinished','CompleteDeck')}


def main():
    import FreeCAD as A, Part, MeshPart
    start=datetime.now(timezone.utc); assert not (OUT/'checks.json').exists()
    receipt=R.BASE/'w5-remote-end-layout-r2/checks.json'
    proof=json.loads(receipt.read_text(encoding='utf-8'))
    assert not proof['errors'] and len(proof['hits'])==4
    assert {(r['part'],r['owner']) for r in proof['hits']}=={
        (g+'Tie'+str(i),g+'Seat') for g in ('BAT','AUX') for i in range(2)}
    for rel,h in {**proof['source_sha256'],**proof['files']}.items():assert sha(ROOT/rel)==h,rel
    bp=R.blueprint(); proposed,slots=R.proposed(A,Part,bp)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    state=dict(status='REMOTE_NATIVE_PENDING',started_utc=start.isoformat(),selected=False,
               W1_complete=False,W5_complete=False,physical_pass=False)
    def progress(stage,**kw):
        state.update(stage=stage,updated_utc=datetime.now(timezone.utc).isoformat(),**kw)
        save(OUT/'progress.json',state);print('REMOTE_NATIVE',stage,flush=True)
    d=A.newDocument('RemoteEndRetention'); target=CAD/'RemoteEndRetention.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','RemoteParameters');p.addProperty('App::PropertyLength','TieClearance');p.TieClearance=.2
    p.addProperty('App::PropertyString','Readiness');p.Readiness='Nominal prototype, physical fit/creep/shared assembly pending'
    def box(name,b,placement=None):
        o=d.addObject('Part::Box',name);o.Length,o.Width,o.Height=[b[i+3]-b[i] for i in range(3)]
        o.Placement.Base=A.Vector(*b[:3])
        if placement:o.Placement=placement.multiply(o.Placement)
        return o
    finals={};parent_paths=[];ownchecks=[];nominal={};probe={};dimensions={}
    for group,(rel,objname,name) in PARENTS.items():
        src=ROOT/'hardware/cad/studies'/rel; parent_paths.append(src)
        parent=A.openDocument(str(src));obj=parent.getObject(objname);assert obj is not None,objname
        assert obj.Shape.isValid() and len(obj.Shape.Solids)==1,group
        progress('loaded_'+group)
        link=d.addObject('App::Link',group+'ReceivedOwner');link.setLink(obj);link.LinkPlacement=obj.Placement
        r=bp[group];seat=box(group+'SeatBlank',r['root_box_mm'])
        groove=d.addObject('Part::Cylinder',group+'CableGroove');groove.Radius=r['groove_radius_mm'];groove.Height=r['groove_height_mm']
        groove.Placement=A.Placement(A.Vector(*r['groove_start_mm']),A.Rotation(A.Vector(0,0,1),A.Vector(*r['axis'])))
        t=r['tie_local_mm'];a=t['across'];lo=t['bottom'];hi=t['top'];x,y,_=r['station_mm']
        tr=A.Placement(A.Vector(x,y,0),A.Rotation(A.Vector(0,0,1),0 if group=='BAT' else -90))
        cutters=[]
        for i,u in enumerate((-a-1.2,a)):
            q=box(group+'TiePassage'+str(i),[u-.2,-1.55,lo-.2,u+1.4,1.55,hi+1.4],tr)
            q.setExpression('Length','1.2 mm + 2 * RemoteParameters.TieClearance')
            q.setExpression('Width','2.7 mm + 2 * RemoteParameters.TieClearance')
            # Placement retains the nominal center; parameter changes opening,
            # never the mating wire/station or the source part placement.
            cutters.append(q)
        tools=d.addObject('Part::Compound',group+'LocalTools');tools.Links=[groove,*cutters]
        blank=d.addObject('Part::MultiFuse',group+'OwnerAndIntegralSeat');blank.Shapes=[link,seat];blank.Refine=False
        final=d.addObject('Part::Cut',name+'Finished');final.Base=blank;final.Tool=tools;final.Refine=False
        finals[name]=final
    d.save();progress('editable_tree_saved',objects=len(d.Objects));d.recompute()
    for group,(_,_,name) in PARENTS.items():
        s=finals[name].Shape;assert s.isValid() and len(s.Solids)==1,(name,len(s.Solids))
        assert not (s.check(True) or []),name
        nominal[name]=s.Volume
        # Do not load/recheck 906 unchanged materials. The positive additions
        # inherit R2 external checks; subtraction cannot add a new collision.
        for label,t in proposed.items():
            if label.startswith(group) and not label.endswith('Seat'):
                c=s.common(t);v=c.Volume;ownchecks.append(dict(part=label,owner=name,mm3=v));assert v<1e-6,ownchecks[-1]
        wire=ROOT/json.loads(R.N.CENTRAL.read_text(encoding='utf-8'))['routes'][bp[group]['wire']]['geometry']
        v=s.common(Part.read(str(wire))).Volume
        ownchecks.append(dict(part=bp[group]['wire'],owner=name,mm3=v));assert v<1e-6,ownchecks[-1]
        progress('received_'+name,nominal_mm3=nominal)
    p.TieClearance=.3;d.recompute()
    for name,o in finals.items():
        assert o.Shape.isValid() and len(o.Shape.Solids)==1,name
        probe[name]=o.Shape.Volume;assert probe[name]<nominal[name],name
    p.TieClearance=.2;d.recompute()
    for name,o in finals.items():
        assert abs(o.Shape.Volume-nominal[name])<max(1e-5,nominal[name]*1e-8),name
        assert not (o.Shape.check(True) or []),name
    for o in d.Objects:
        if o.ViewObject:o.ViewObject.Visibility=o in finals.values()
    d.save()
    for name,o in finals.items():
        o.Shape.exportBrep(str(CAD/(name+'_CANDIDATE_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1,name
        bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert max(dims)+6<=256,(name,dims)
        dimensions[name]=dims;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(name+'_UNSELECTED_x1.stl')))
        progress('exported_'+name)
    deps=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    assert all(q.is_relative_to(ROOT) for q in deps)
    names={n:o.Name for n,o in finals.items()}
    for n in list(A.listDocuments()):A.closeDocument(n)
    with tempfile.TemporaryDirectory(prefix='robot-cat-remote-ends-') as td:
        tmp=Path(td)
        for q in [target,*deps]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        reopened=A.openDocument(str(tmp/target.relative_to(ROOT)));reopened.recompute()
        for n,objname in names.items():
            s=reopened.getObject(objname).Shape;assert s.isValid() and len(s.Solids)==1,n
            assert abs(s.Volume-nominal[n])<max(1e-5,nominal[n]*1e-8),n
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for n in list(A.listDocuments()):A.closeDocument(n)
    finish=datetime.now(timezone.utc)
    state.update(status='FIVE_REMOTE_ENDS_NATIVE_STATIC_EXPORT_COMPLETE',finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds(),endpoint_count=5,editable_final_objects=names,
        BOP_errors=0,closed_STLs=2,relocated_reopen=True,nominal_mm3=nominal,probe_mm3=probe,
        parameter_probe_mm=[.2,.3,.2],own_material_checks=ownchecks,dimensions_mm=dimensions,
        inherited_external_receipt=receipt.relative_to(ROOT).as_posix(),net_new_T18I=1,
        new_connector_SKUs=0,new_splices=0,BUS_MAIN_retained=True,
        assembly=['Thread BAT return strap through bridge before battery connection.','Thread AUX strap in Deck before G_AUX wiring.','Retain existing BUS plug strap and MAIN insulated-tail strap; no strap on bare solder.'],
        manufacturing={'material':'PETG','orientation':'Use translated STL nominal orientation; bridge feet and Deck underside toward bed.','support':'Review underside strap slots in phase2 slicer; clear slots before wiring.','fit_strength_creep':'Physical tests phase2, not verified.'},
        shared_mount_removal_open=True,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__),Path(R.__file__),receipt,*deps]},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in CAD.iterdir() if q.suffix.lower() in ('.fcstd','.brep','.stl')})
    save(OUT/'checks.json',state);progress('complete')


if __name__=='__main__':main()
