"""One combined editable Deck/BUS restraint construction after the whole R4 pair.

Full path snapshots are identified as such; native support boxes, parametric
sweeps and cuts remain editable. Never exclude an interfering bought part.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-bus-native-grips-r1'
CAD=ROOT/'hardware/cad/studies/w5-bus-native-grips-r1'
ROUTES=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4'


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    from w5_selected_owners_r52 import cached
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    received=json.loads((ROUTES/'checks.json').read_text(encoding='utf-8'))
    assert not received['errors'] and not received['mutual_contacts']
    assert received['within_one_factory300mm_cable']
    assert all(h['owner'] in ('CandidateDeck','W061_tie/G2_end/1') for h in received['hits']), received['hits']
    intent=json.loads((ROUTES/'intent.json').read_text(encoding='utf-8'))
    sources=intent['source_lead_datums'];sx=(sources['W002'][0]+sources['W003'][0])/2
    # Four new ties; same selected T18I SKU. The existing W061 tie is reused
    # in its actual holes, with a sloping tightened right band, not a rigid box.
    supports=[('Plug',[sx-5.5,26.5,84,sx+5.5,30.3,110]),
              ('Dend',[-12.5,27.5,108.8,-8.5,30,114]),
              ('Gend',[115,13.75,108.8,119,16.25,113.2]),
              ('Gmiddle',[81,59,105,87,63,113])]
    save(OUT/'intent.json',dict(status='SAVED_BEFORE_COMBINED_NATIVE_BUS',
        selected=False,W5_complete=False,physical_pass=False,new_ties=4,
        tie_SKU='Hellermann111-02370 T18I',new_fasteners=0,new_separate_prints=0,
        one_replacement_Deck=True,groove_radius_mm=1.2,
        source_support_bounds=[b for _,b in supports],
        assumptions=intent['prototype_assumptions'],
        tightened_W061_band='Sloped from existing right slot atX116.5/Z108.8 toX114.6/Z115.7; same original tie/holes. Nominal shape, phase2 fitting required.',
        assembly=['Mount BUS/USB and thread hanging source band before fitting populated Deck.',
                  'Remove V unpowered, identify D/G without colour or guessed cavities; retain ONE factory plug/cable.',
                  'Place D/G in their continuous channels; seat four insulation grips before trimming only the remote ends.',
                  'Insert one untinned D intoD_FL.1 and G intoG2.4; tighten W061 band around insulation through its retained holes.',
                  'Battery/USB disconnected: release the four BUS bands, D_FL.1/G2.4 levers and H3 plug before lifting BUS/Deck. Other selected bank service sequence remains separate.']))
    source=ROOT/'hardware/cad/studies/w5-g1-passage-native-r2/DeckG1Passage.FCStd'
    parent=A.openDocument(str(source));d=A.newDocument('BusCompleteDeck')
    target=CAD/'BusCompleteDeck.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','BusGripParameters');p.addProperty('App::PropertyLength','GrooveRadius');p.GrooveRadius=1.2
    link=d.addObject('App::Link','CurrentG1Deck');link.setLink(parent.G1PassageFinished)
    link.LinkPlacement=parent.G1PassageFinished.Placement
    boxes=[]
    for name,b in supports:
        obj=d.addObject('Part::Box',name+'InsulationSeat')
        obj.Length=b[3]-b[0];obj.Width=b[4]-b[1];obj.Height=b[5]-b[2]
        obj.Placement.Base=A.Vector(*b[:3]);boxes.append(obj)
    raw=d.addObject('Part::MultiFuse','DeckAndBusSeats');raw.Shapes=[link]+boxes;raw.Refine=False
    paths=[];tools=[];routefiles=[]
    for wire in ('W002','W003'):
        f=ROUTES/(wire+'_CENTERLINE.brep');routefiles.append(f)
        path=d.addObject('Part::Feature',wire+'PinnedPath');path.Shape=Part.read(str(f));paths.append(path)
        path.addProperty('App::PropertyString','SnapshotSource');path.SnapshotSource=f.relative_to(ROOT).as_posix()
        e=path.Shape.Edges[0];origin=e.valueAt(e.FirstParameter)
        circle=d.addObject('Part::Circle',wire+'ClearanceProfile');circle.setExpression('Radius','BusGripParameters.GrooveRadius')
        circle.Placement=A.Placement(origin,A.Rotation(A.Vector(0,0,1),e.tangentAt(e.FirstParameter)))
        sweep=d.addObject('Part::Sweep',wire+'ContinuousClearance');sweep.Sections=[circle];sweep.Spine=(path,[]);sweep.Solid=True;sweep.Frenet=False;tools.append(sweep)
    # Open the middle groove under its band, retaining the two longitudinal
    # shoulders attached to the Deck. A strap around a closed tunnel is NOT
    # an insulation restraint.
    opening=d.addObject('Part::Box','MiddleOpenGrip');opening.Length=2.5;opening.Width=4.4;opening.Height=6.5
    opening.Placement.Base=A.Vector(82.75,58.8,107.5);tools.append(opening)
    # Endpoint bands use real through-slots, outside each4mm-wide seat.
    for name,x,y in [('D',-10.5,28.75),('G',117,15),('Gmid',84,61)]:
        for side in (-1,1):
            slot=d.addObject('Part::Box',name+'TieSlot'+('L' if side<0 else 'R'))
            if name=='Gmid':slot.Length=3.2;slot.Width=2;slot.Placement.Base=A.Vector(x-1.6,y+side*3-1,100)
            else:slot.Length=2;slot.Width=3.2;slot.Placement.Base=A.Vector(x+side*3-1,y-1.6,100)
            slot.Height=16;tools.append(slot)
    cutters=d.addObject('Part::MultiFuse','BusClearanceTools');cutters.Shapes=tools;cutters.Refine=False
    final=d.addObject('Part::Cut','BusDeckFinished');final.Base=raw;final.Tool=cutters;final.Refine=False
    d.save();print('BUS_NATIVE_SOURCE_SAVED',flush=True);d.recompute()
    final.Shape.exportBrep(str(CAD/'Deck_CANDIDATE_WORLD.brep'))
    assert final.Shape.isValid() and len(final.Shape.Solids)==1 and not final.Shape.check(True)
    nominal=final.Shape.Volume;p.GrooveRadius=1.3;d.recompute();probe=final.Shape.Volume
    assert probe<nominal;p.GrooveRadius=1.2;d.recompute()
    assert abs(final.Shape.Volume-nominal)<max(1e-5,nominal*1e-8)
    d.save();shape=final.Shape.copy()
    owners,cache=cached();old=owners.pop('CandidateDeck');oldband=owners.pop('W061_tie/G2_end/1')
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def bands(x,y,top,half=3,bottom=103.8):
        return [box([x+v-.6,y-1.25,bottom,x+v+.6,y+1.25,top+1.2]) for v in (-half,half)]+[
            box([x-half-.6,y-1.25,top,x+half+.6,y+1.25,top+1.2]),
            box([x-half-.6,y-1.25,bottom,x+half+.6,y+1.25,bottom+1.2]),
            box([x+half-1,y-2.5,100.1,x+half+5,y+2.5,104.1])]
    newties={}
    for name,x,y,top in [('D',-10.5,28.75,114.5),('G',117,15,114.25)]:
        for i,s in enumerate(bands(x,y,top)):newties[name+'/'+str(i)]=s
    for i,s in enumerate(bands(61,-84,108.1,3)):
        s.rotate(A.Vector(),A.Vector(0,0,1),90);newties['Gmid/'+str(i)]=s
    # Source wrap around the vertical two-core seat, width2.5 along Z.
    for i,b in enumerate([[sx-6.1,25.3,84.5,sx-4.9,32,87],
                           [sx+4.9,25.3,84.5,sx+6.1,32,87],
                           [sx-6.1,25.3,84.5,sx+6.1,26.5,87],
                           [sx-6.1,31.5,84.5,sx+6.1,32.7,87],
                           [sx+5.5,26,83,sx+11.5,31,87]]):newties['Plug/'+str(i)]=box(b)
    vertices=[A.Vector(x,9.75,z) for x,z in [(115.9,103.8),(117.1,103.8),(117.1,108.8),(115.2,115.7),(114,115.7),(115.9,108.8)]]
    newties['W061SlopedBand']=Part.Face(Part.makePolygon(vertices+[vertices[0]])).extrude(A.Vector(0,2.5,0))
    addition=shape.cut(link.Shape);tested=0;hits=[];errors=[]
    def check(name,s,reference):
        nonlocal tested
        for key,owner in reference.items():
            if not s.BoundBox.intersect(owner.BoundBox):continue
            for j,o in enumerate(owner.Solids):
                if not s.BoundBox.intersect(o.BoundBox):continue
                tested+=1
                try:
                    v=s.common(o).Volume
                    if v>1e-5:hits.append(dict(part=name,owner=key,solid=j,mm3=v))
                except Exception as exc:errors.append(dict(part=name,owner=key,error=str(exc)))
    for wire in ('W002','W003'):
        check(wire,Part.read(str(ROUTES/(wire+'_DESIGN.brep'))),{'newDeck':shape,**newties})
    check('AddedSeats',addition,owners)
    for name,s in newties.items():
        check(name,s,owners)
        s.exportBrep(str(OUT/(name.replace('/','_')+'.brep')))
    end=datetime.now(timezone.utc)
    paths_to_pin=[source,ROUTES/'checks.json',ROUTES/'intent.json',Path(__file__),*routefiles]
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    paths_to_pin+=dependencies
    result=dict(status='BUS_NATIVE_STATIC_CLEAR_EXPORT_PENDING' if not hits and not errors else 'BUS_NATIVE_REJECTED_CONTACTS',
        hits=hits,errors=errors,changed_pairs=tested,single_solid=True,strict_BOP_errors=0,
        parameter_radius_mm=[1.2,1.3,1.2],parameter_volumes=[nominal,probe,shape.Volume],
        full_routes_receipt=(ROUTES/'checks.json').relative_to(ROOT).as_posix(),
        inherited_R4_contacts_replaced=['CandidateDeck','W061_tie/G2_end/1'],
        new_ties=4,reused_W061_ties=1,new_fasteners=0,new_separate_prints=0,
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in paths_to_pin},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in list(CAD.glob('*'))+list(OUT.glob('*.brep')) if q.is_file()},
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',result);print('BUS_NATIVE_RESULT',json.dumps(dict(hits=hits,errors=errors)),flush=True)
    if hits or errors:return
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+6<=256 and dims[1]+6<=256 and dims[2]<=256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'BusCompleteDeck_UNSELECTED_x1.stl'))
    for n in list(A.listDocuments()):A.closeDocument(n)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bus-deck-') as td:
        tmp=Path(td)
        for f in [target]+dependencies:
            dest=tmp/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
        r=A.openDocument(str(tmp/target.relative_to(ROOT)));r.recompute()
        assert r.BusDeckFinished.Shape.isValid() and abs(r.BusDeckFinished.Shape.Volume-nominal)<max(1e-5,nominal*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    result.update(status='BUS_NATIVE_STATIC_COMPLETE_UNSELECTED',closed_STL=True,relocated_reopen=True,dimensions_mm=dims,
        files={q.relative_to(ROOT).as_posix():sha(q) for q in list(CAD.glob('*'))+list(OUT.glob('*.brep')) if q.is_file()})
    result['finished_utc']=datetime.now(timezone.utc).isoformat()
    result['worker_wall_seconds']=(datetime.now(timezone.utc)-start).total_seconds()
    save(OUT/'checks.json',result)


if __name__=='__main__':main()
