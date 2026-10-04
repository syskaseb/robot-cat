"""Editable R53 replacement Deck with two XA05 insulation supports.

Run ONLY after the complete changed wire/seats/straps fit is clear. Saved
base geometry is linked, not reread E6 or frozen as the new construction.
Local feature BOP, parameter roundtrip, STL and relocated reopen are distinct
from full final strict BOP and physical or cyclic qualification.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-xa05-native-r1'
FIT=ROOT/'hardware/electronics/full-cat/w5-xa05-joint-repair-r3/checks.json'
SOURCE=ROOT/'hardware/cad/studies/w5-bus-native-grips-r4/BusStrapSlots.FCStd'


def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc)
    received=json.loads(FIT.read_text(encoding='utf-8'))
    assert not received['hits'] and not received['errors'],'No export of rejected fits'
    assert all(sha(ROOT/k)==v for k,v in {**received['source_sha256'],**received['files']}.items())
    assert received['new_ties']==2 and received['new_fasteners']==0
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    parent=A.openDocument(str(SOURCE));d=A.newDocument('XA05JointSupports')
    target=CAD/'XA05JointSupports.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','XA05Parameters')
    p.addProperty('App::PropertyLength','GrooveRadius');p.GrooveRadius=1.5
    link=d.addObject('App::Link','R53Deck');link.setLink(parent.BusStrapSlotsFinished)
    link.LinkPlacement=parent.BusStrapSlotsFinished.Placement
    seats=[];tools=[]
    def native_box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2]
        q.Placement.Base=A.Vector(*b[:3]);return q
    for spec in received['support_specs']:
        name,y=spec['name'],spec['y_mm'];cx,_,cz=spec['groove_centre']
        seats.append(native_box(name+'Seat',spec['seat_bounds_mm']))
        groove=d.addObject('Part::Cylinder',name+'InsulationGroove')
        groove.setExpression('Radius','XA05Parameters.GrooveRadius');groove.Height=6.8
        groove.Placement=A.Placement(A.Vector(cx,y-3.4,cz),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
        tools.append(groove)
        for side,x in [('West',cx-4.1),('East',cx+4.1)]:
            tools.append(native_box(name+side+'TieSlot',[x-.8,y-1.6,108.8,x+.8,y+1.6,cz+2.6]))
        tools.append(native_box(name+'UnderTieTunnel',[cx-5.1,y-1.6,109.4,cx+5.1,y+1.6,110.8]))
    raw=d.addObject('Part::MultiFuse','DeckAndXA05Seats');raw.Shapes=[link,*seats];raw.Refine=False
    cutter=d.addObject('Part::Compound','XA05Tools');cutter.Links=tools
    final=d.addObject('Part::Cut','XA05DeckFinished');final.Base=raw;final.Tool=cutter;final.Refine=False
    d.save();print('XA05_NATIVE_SOURCE_SAVED',flush=True);d.recompute()
    d.save();shape=final.Shape.copy();shape.exportBrep(str(CAD/'Deck_WORLD.brep'))
    assert shape.isValid() and len(shape.Solids)==1
    assert all(q.Shape.isValid() and not q.Shape.check(True) for q in seats+tools)
    nominal=shape.Volume;p.GrooveRadius=1.6;d.recompute();probe=final.Shape.Volume
    assert probe<nominal;p.GrooveRadius=1.5;d.recompute()
    assert final.Shape.isValid() and len(final.Shape.Solids)==1
    assert abs(final.Shape.Volume-nominal)<max(1e-5,nominal*1e-8)
    d.save();shape=final.Shape.copy();shape.exportBrep(str(CAD/'Deck_WORLD.brep'))
    # Only the changed interfaces against the final native shape. All other
    # identical owners were checked in FIT; no blanket installed-waiver.
    from w5_r53_owners import installed
    owners,owner_pins,_=installed(A,Part)
    owners.pop('CandidateDeck')
    owners.pop('hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep')
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    ties=[]
    for spec in received['support_specs']:
        y=spec['y_mm'];cx,_,cz=spec['groove_centre'];left,right=cx-4.1,cx+4.1;bottom,top=109.5,cz+1.25
        ties.append(Part.makeCompound([
            box([x-.6,y-1.25,bottom,x+.6,y+1.25,top+1.2]) for x in (left,right)
        ]+[box([left-.6,y-1.25,top,right+.6,y+1.25,top+1.2]),
           box([left-.6,y-1.25,bottom,right+.6,y+1.25,bottom+1.2]),
           box([right+.1,y-2.5,bottom-.1,right+5.1,y+2.5,bottom+3.9])]))
    tiefile=OUT/'TIGHT_TIES_WORLD.brep';Part.makeCompound(ties).exportBrep(str(tiefile))
    contacts=[];errors=[];changed_pairs=0
    for i,s in enumerate(ties):
        for name,other in {**owners,'NativeDeck':shape,'XA05':Part.read(str(FIT.parent/'XA05_WORLD.brep'))}.items():
            if not s.BoundBox.intersect(other.BoundBox):continue
            changed_pairs+=1
            try:
                v=s.common(other).Volume
                if v>1e-5:contacts.append(dict(part='TightTie'+str(i),owner=name,mm3=v))
            except Exception as exc:errors.append(dict(part='TightTie'+str(i),owner=name,error=str(exc)))
    for name,path in [('XA05',FIT.parent/'XA05_WORLD.brep')]:
        s=Part.read(str(path));v=shape.common(s).Volume
        if v>1e-5:contacts.append(dict(part=name,owner='NativeDeck',mm3=v))
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    pins=[Path(__file__),FIT,SOURCE,*dependencies,*owner_pins,ROOT/'hardware/manufacturing/one-batch-prototype-r53/nonfastener-catalog.json']
    base=dict(status='XA05_NATIVE_CONTACTS_REJECTED' if contacts or errors else 'XA05_NATIVE_EXPORT_PENDING',hits=contacts,errors=errors,changed_pairs=changed_pairs,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        native_supports_constructed=True,single_solid=True,new_feature_strict_BOP_errors=0,
        full_final_strict_BOP_verified=False,parameter_radius_mm=[1.5,1.6,1.5],parameter_volumes=[nominal,probe,shape.Volume],
        new_ties=2,tie_SKU='111-02370 T18I-PA66-BK',new_fasteners=0,new_separate_prints=0,
        strap_metadata='Selected111-02370 retained, no new SKU. Upper bands touch nominal insulation top114.75. Checked against owners/wire/nativeDeck; no clamp-force or delivered-head qualification.',
        route_and_other_owner_fit=FIT.relative_to(ROOT).as_posix(),
        assembly=['Disconnected battery andUSB; thread two new bands through Deck slots before Pi mounting.',
            'Identify XA05 power ground P0G2.5 toG_AUX.1; never substitute signal ground.',
            'Seat continuous HELU23501 in two grooves; measure dry fit before cutting/stripping ends.',
            'Release these two straps and both terminal levers before removing the wire; no new splice.'],
        remaining=['Preserved endpoint tie engagement and both WAGO lever/tool actions with changed route.',
            'Full wire/strip/stock and selected-package reconciliation before restoring W1.',
            'Check native added supports with all pending W5 routes when those are chosen.'],
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in [tiefile,*CAD.glob('*.FCStd'),*CAD.glob('*.brep')]},
        started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds())
    save(OUT/'checks.json',base)
    if contacts or errors:return
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+6<=256 and dims[1]+6<=256 and dims[2]<=256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_UNSELECTED_x1.stl'))
    for n in list(A.listDocuments()):A.closeDocument(n)
    with tempfile.TemporaryDirectory(prefix='robot-cat-xa05-native-') as td:
        tmp=Path(td)
        for q in [target,*dependencies]:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        restored=A.openDocument(str(tmp/target.relative_to(ROOT)));restored.recompute()
        assert restored.XA05DeckFinished.Shape.isValid() and len(restored.XA05DeckFinished.Shape.Solids)==1
        assert abs(restored.XA05DeckFinished.Shape.Volume-nominal)<max(1e-5,nominal*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    base.update(status='XA05_NATIVE_STATIC_COMPLETE_UNSELECTED',closed_STL=True,relocated_reopen=True,dimensions_mm=dims,
        files={q.relative_to(ROOT).as_posix():sha(q) for q in [tiefile,*CAD.glob('*.FCStd'),*CAD.glob('*.brep'),*CAD.glob('*.stl')]},
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds())
    save(OUT/'checks.json',base);print('XA05_NATIVE_EXPORTED',dims,flush=True)


if __name__=='__main__':main()
