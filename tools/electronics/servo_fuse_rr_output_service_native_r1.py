"""Open the outward RR cage corridor in the actual current right bank.

One subtractive native box; retain the housing floor, north anchor, both
insulation seats and existing wire routes. Inherit R2's clear other pairs,
check ONLY its three actual right-bank contacts against the changed part.
No rerun of unchanged Deck/Cover/other wire pairs.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,tempfile,shutil

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-rr-output-service-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve existing proof'
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def read(p):pin(p);return json.loads(p.read_text(encoding='utf-8'))
    previous=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-disconnect-r2'
    proof=read(previous/'checks.json')
    assert not proof['errors'] and proof['assumptions']['opening_degrees']==90
    assert len(proof['hits'])==3 and all(r['owner']=='Bank/RightClipAccessFinished_WORLD' for r in proof['hits'])
    prior=read(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json')
    row=next(r for r in prior['exports'] if r['tag']=='BankRight')
    source=ROOT/row['file'];pin(source)
    d=A.openDocument(str(source));dest=CAD/'BankRightRROutputService.FCStd'
    result={}
    try:
        p=d.addObject('App::VarSet','RRServiceParameters');p.addProperty('App::PropertyLength','Clearance');p.Clearance=.2
        tool=d.addObject('Part::Box','RRLeverServiceOpening')
        # Expand the nominal corridor by0.2mm on each face. Neither north
        # anchorY=-93..-90 nor floorZ=109.35..111.75 intersects this opening.
        tool.Placement.Base=A.Vector(-63.5,-120.2,112.3)
        tool.setExpression('Length','14.5 mm + 2 * RRServiceParameters.Clearance')
        tool.setExpression('Width','24.8 mm + 2 * RRServiceParameters.Clearance')
        tool.setExpression('Height','11.5 mm + 2 * RRServiceParameters.Clearance')
        f=d.addObject('Part::Cut','RROutputServiceFinished');f.Base=d.RearOutputStationsFinished;f.Tool=tool;f.Refine=False
        print('RR_SERVICE_NATIVE_RECOMPUTE',flush=True);d.recompute()
        shape=f.Shape.copy()
        state=dict(valid=shape.isValid(),solids=len(shape.Solids),null=shape.isNull(),BOP=[str(e) for e in (shape.check(True) or [])],
            solid_volumes_mm3=[s.Volume for s in shape.Solids],object_status=f.getStatusString())
        print('RR_SERVICE_SHAPE',json.dumps(state),flush=True)
        if not state['valid'] or state['solids']!=1 or state['BOP']:
            save(OUT/'failure.json',dict(state,physical_pass=False,selected=False,script_sha256=sha(Path(__file__)),source_sha256=pins))
            shape.exportBrep(str(OUT/'FAILED_BANK.brep'))
            return
        contacts=[];errors=[]
        for hit in proof['hits']:
            path=previous/(hit['probe']+'.brep');pin(path);s=Part.read(str(path));c=s.common(shape)
            if c.Volume>1e-5:contacts.append(dict(probe=hit['probe'],mm3=c.Volume))
        # Preserve actual footprint and floor using native material, not bbox.
        protected=[[-53,-93,109.35,-49,-90,109.55],[-65,-93,109.35,-50,-90,111.75]]
        retained=[]
        for b in protected:
            q=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
            before=q.common(f.Base.Shape).Volume;after=q.common(shape).Volume
            assert abs(before-after)<1e-5 and before>0
            retained.append(dict(bounds_mm=b,before_mm3=before,after_mm3=after))
        assert not contacts
        volume=shape.Volume;p.Clearance=.3;d.recompute();probe=f.Shape.Volume
        assert f.Shape.isValid() and len(f.Shape.Solids)==1 and abs(probe-volume)>1e-5
        p.Clearance=.2;d.recompute();assert abs(f.Shape.Volume-volume)<1e-5
        shape=f.Shape.copy();d.saveAs(str(dest));shape.exportBrep(str(CAD/'BankRight_WORLD.brep'))
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength]
        assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
        mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/'BankRight_UNSELECTED.stl'))
        result=dict(file=dest.relative_to(ROOT).as_posix(),final=f.Name,single_solid=True,strict_BOP_errors=0,
            closed_STL=True,dimensions_mm=dims,parameter_mm=[.2,.3,.2],volumes_mm3=[volume,probe,volume],contacts=contacts,errors=errors,retained_material=retained)
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-rr-service-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);rd=A.openDocument(str(q))
        try:rd.recompute();assert abs(rd.RROutputServiceFinished.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(rd.Name)
    result['relocated_reopen']=True
    save(OUT/'checks.json',dict(status='RR_PROTOTYPE_SERVICE_CORRIDOR_NATIVE_COMPLETE',selected=False,physical_pass=False,W5_complete=False,
        native=result,assumptions=proof['assumptions'],inherited_clear_other_pairs=proof['pairs']-len(proof['hits']),
        rechecked_changed_pairs=3,actual_manufacturer_lever_motion_qualified=False,
        sequence='Remove ATOs/mini holders keeping24TE ends on their axes; cut three RR output straps; upright outward levers have PROJECT corridor. Wire withdrawal/parking and common bank lift remain OPEN.',
        stock_delta=dict(additional_prints=0,fasteners=0,straps=0,replacement='BankRight'),
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('RR_SERVICE_NATIVE_SAVED',json.dumps(result),flush=True)

if __name__=='__main__':main()
