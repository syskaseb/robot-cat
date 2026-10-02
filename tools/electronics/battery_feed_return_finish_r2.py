"""Finish the changed G1.1 return only; retain the existing F0/XT60 bridge.

Y31 clears the known Pi cooling reserve. No relocation of the cooling, P0,
selected wires or the rejected S0. All checks remain prototype geometry.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, math, json, tempfile, shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import rounded,save,sha
OLD=ROOT/'hardware/electronics/full-cat/battery-feed-bridge-r1'
OUT=ROOT/'hardware/electronics/full-cat/battery-feed-return-finish-r2'
CAD=ROOT/'hardware/cad/studies/battery-feed-return-finish-r2'


def main():
    import FreeCAD as A
    import Part,MeshPart
    from check_main_p0_placement import SavedShapes
    from open_deck_p0_plate import rect
    import main_positive_input_r1 as C
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    old=json.loads((OLD/'checks.json').read_text(encoding='utf-8'))
    assert sha(ROOT/'tools/electronics/battery_feed_bridge_r1.py')==old['script_sha256']
    assert not old['errors'] and all(h['part'].startswith('W001_') and h['owner']=='PiHatCooling_rise7' for h in old['hits'])
    owners,hashes=C.current_owners()
    def load(pp):
        pp=Path(pp);hashes[pp.relative_to(ROOT).as_posix()]=sha(pp)
        s=Part.Shape();s.read(str(pp));return s
    owners.pop('Deck_R41');owners.pop('MAIN_R40')
    original=load(ROOT/'hardware/cad/studies/main-positive-native-r2/Deck_WORLD.brep')
    owners['MAIN_R44']=load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for folder,pattern in [('hardware/electronics/full-cat/main-positive-complete-r8','*_DESIGN.brep'),
                           ('hardware/cad/studies/main-positive-native-r2','*_WORLD.brep')]:
        for pp in (ROOT/folder).glob(pattern):
            if pp.stem not in ('Deck_WORLD','MAIN_WORLD'):owners['R44/'+pp.stem]=load(pp)
    for n in list(owners):
        if n.startswith(('BatteryCarrier','BatteryLiner','BatteryStrap','BatteryScrew','BatteryNut')):del owners[n]
    reader=SavedShapes();carrier=ROOT/'hardware/cad/studies/battery-p0/r4/electronics/BatteryCarrierP0.FCStd'
    for n in ('Carrier','SelectedPack','SoftLinerEnvelope'):owners['R4/'+n]=reader.shape(carrier,n)
    hashes.update(reader.hashes)
    retained={}
    for pp in OLD.glob('*_DESIGN.brep'):
        if not pp.stem.startswith('W001_'):retained[pp.stem[:-7]]=load(pp)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def cylinder(xyz,r,h,axis=(0,0,1)):return Part.makeCylinder(r,h,A.Vector(*xyz),A.Vector(*axis))
    w=rounded([A.Vector(51,80,69),A.Vector(51,31,69),A.Vector(51,31,113.5),A.Vector(51,11,113.5)],12.4)
    for a,b in zip(w.Edges,w.Edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-6
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-6
    assert min(e.Curve.Radius for e in w.Edges if hasattr(e.Curve,'Radius'))>=12.4-1e-6
    blank=math.ceil((w.Length+19+10)/10)*10;assert blank<=150
    wires={};portals=[]
    for i,e in enumerate(w.Edges):
        def pipe(r):return Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(r,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
        wires['W001_'+str(i)]=pipe(1.55)
        e.exportBrep(str(OUT/('W001_'+str(i)+'_CENTERLINE.brep')))
        if wires['W001_'+str(i)].BoundBox.intersect(original.BoundBox):portals.append(pipe(1.95))
    seat=box([48.8,11.5,108.8,53.2,14,112]).cut(cylinder([51,11.4,113.5],1.8,2.7,(0,1,0)))
    slots=[box([x-.8,10.9,104.9,x+.8,14.1,109.1]) for x in (48,54)]
    bores=[cylinder([x,53,104.9],1.2,4.2) for x in (-10,61)]
    deck=original.cut(Part.makeCompound(portals+slots+bores)).fuse(seat)
    assert deck.isValid() and len(deck.Solids)==1
    bands={
        'G1BAT_left':box([47.4,11.25,103.8,48.6,13.75,115.1]),
        'G1BAT_right':box([53.4,11.25,103.8,54.6,13.75,115.1]),
        'G1BAT_top':box([47.4,11.25,115.1,54.6,13.75,116.3]),
        'G1BAT_bottom':box([47.4,11.25,103.8,54.6,13.75,105]),
        'G1BAT_head':box([48,10,100.1,54,15,104.1])}
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    v=a.common(b).Volume
                    if v>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=v))
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in {**wires,**bands,'G1BAT_seat':seat}.items():
        for m,t in owners.items():check(n,s,m,t)
        # The cradle is fused INTO the Deck, not a separate collision owner.
        # Retain all cable/tie checks against that same complete Deck.
        if n!='G1BAT_seat':check(n,s,'Deck_candidate',deck)
        for m,t in retained.items():
            if m=='XT60_robot_body' and n=='W001_0':continue # own exit endpoint only
            check(n,s,m,t)
    # Retained source parts meet the newly cut Deck without changing geometry.
    for n,s in retained.items():check(n,s,'Deck_candidate',deck)
    for n,s in bands.items():
        for m,t in wires.items():check(n,s,m,t)
        check(n,s,'G1BAT_seat',seat)
    for n,s in {**wires,**bands,'G1BAT_seat':seat}.items():s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    deck.exportBrep(str(OUT/'Deck_UNSELECTED.brep'))
    preliminary=dict(hits=hits,errors=errors,pairs=pairs,selected=False,W5_complete=False,physical_pass=False,
        blank_mm=blank,path_mm=w.Length,portal_segments=len(portals),source_sha256=hashes,
        script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),
        retained_bridge_native='hardware/cad/studies/battery-feed-bridge-r1/BatteryFeedBridge.FCStd',
        retained_bridge_sha256=sha(ROOT/'hardware/cad/studies/battery-feed-bridge-r1/BatteryFeedBridge.FCStd'))
    save(OUT/'geometry.json',preliminary)
    print(json.dumps(dict(local_hits=hits,errors=errors,blank_mm=blank,pairs=pairs)),flush=True)
    if hits or errors:
        end=datetime.now(timezone.utc)
        save(OUT/'checks.json',dict(**preliminary,status='REJECTED_LOCAL_RETURN',finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
        return
    # Preserve all editable parent features. Add only current bores, portal and
    # one independent restraint. Parent file is never saved or recomputed in UI.
    src=ROOT/'hardware/cad/studies/main-positive-native-r2/DeckMainPositive.FCStd'
    hashes[src.relative_to(ROOT).as_posix()]=sha(src)
    d=A.openDocument(str(src));name=d.Name;dest=CAD/'DeckBatteryFeed.FCStd'
    try:
        d.saveAs(str(dest));p=d.addObject('App::VarSet','BatteryFeedParameters')
        p.addProperty('App::PropertyLength','SeatHeight');p.SeatHeight=3.2
        p.addProperty('App::PropertyLength','GrooveRadius');p.GrooveRadius=1.8
        sketches=[]
        def block(n,b):
            sk=d.addObject('Sketcher::SketchObject',n+'Profile');sk.Placement.Base.z=b[2]
            rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1]);sketches.append(sk)
            f=d.addObject('Part::Extrusion',n);f.Base=sk;f.Dir=A.Vector(0,0,b[5]-b[2]);f.Solid=True;return f
        native_tools=[]
        for i,x in enumerate((48,54)):
            native_tools.append(block('BATThroughSlot'+str(i),[x-.8,10.9,104.9,x+.8,14.1,109.1]))
        for i,x in enumerate((-10,61)):
            f=d.addObject('Part::Cylinder','SourceMountBore'+str(i));f.Radius=1.2;f.Height=4.2;f.Placement.Base=A.Vector(x,53,104.9);native_tools.append(f)
        for i,s in enumerate(portals):
            f=d.addObject('PartDesign::Feature','BATReturnPortal'+str(i));f.Shape=s
            f.addProperty('App::PropertyString','SourceScript');f.SourceScript=Path(__file__).relative_to(ROOT).as_posix()
            f.addProperty('App::PropertyString','SourceSHA256');f.SourceSHA256=sha(Path(__file__));native_tools.append(f)
        union=d.addObject('Part::MultiFuse','BATPortalAndBores');union.Shapes=native_tools;union.Refine=False
        base=d.addObject('Part::Cut','BATSlottedDeck');base.Base=d.MainPositiveDeck;base.Tool=union;base.Refine=False
        pad=block('BATG1Pad',[48.8,11.5,108.8,53.2,14,112]);pad.setExpression('Dir.z','BatteryFeedParameters.SeatHeight')
        groove=d.addObject('Part::Cylinder','BATG1Groove');groove.Radius=1.8;groove.Height=2.7
        groove.Placement=A.Placement(A.Vector(51,11.4,113.5),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
        groove.setExpression('Radius','BatteryFeedParameters.GrooveRadius')
        cradle=d.addObject('Part::Cut','BATG1Seat');cradle.Base=pad;cradle.Tool=groove;cradle.Refine=False
        final=d.addObject('Part::MultiFuse','BatteryFeedDeck');final.Shapes=[base,cradle];final.Refine=False
        d.recompute(sketches);d.save();d.recompute();s=final.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        assert all(sk.FullyConstrained and sk.solve()==0 for sk in sketches)
        assert abs(s.Volume-deck.Volume)<1e-4,(s.Volume,deck.Volume)
        volume=s.Volume;p.SeatHeight=3.3;d.recompute();probe=final.Shape.Volume;assert abs(probe-volume)>1e-5
        p.SeatHeight=3.2;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        for slot in slots:assert slot.common(final.Shape).Volume<1e-5
        d.save();s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bat-deck-') as td:
        relocated=Path(td)/dest.name;shutil.copy2(dest,relocated);d=A.openDocument(str(relocated))
        try:
            d.recompute();assert d.BatteryFeedDeck.Shape.isValid()
            assert abs(d.BatteryFeedDeck.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(d.Name)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_x1.stl'))
    end=datetime.now(timezone.utc)
    report=dict(**preliminary,status='LOCAL_FEED_RETURN_COMPLETE_WHOLE_SOURCE_OPEN',
        native=dict(path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),fully_constrained_sketches=len(sketches),
            parameter_volumes=[volume,probe,volume],relocated_reopen=True,single_solid=True,strict_BOP_errors=0,
            closed_STL=True,dimensions_mm=dims,comparison_scope='Unchanged native parent plus changed local features; aggregate volume tolerance1e-4mm3'),
        assembly=['Battery disconnected; prethread seven T18I source/G1 ties while Deck is accessible.',
            'Fasten independent bridge under Deck using2M2x12,4DIN125M2 and2DIN934M2; hold lower nuts before electronics blocks access.',
            'Retain F0/robotXT60 bodies, then intact insulation separately; do not pull factory leads or heat an attached battery.',
            'W001 blank140mm includes14mm G1 strip,5mm robotXT60 allowance and10mm fitting margin. Check actual reach BEFORE cutting; do not tin WAGO end.',
            'Seat W001 in reservedG1.1 atX51; preserveW061/W060 cages and ties. Hand-tighten new tie without crushing insulation.',
            'S0/W076/battery mating reach remain OPEN; this is not a completed source or electrical safety approval.'],
        remaining=['Accepted S0 location and complete W076/W066 with restraints.',
            'Full battery mate/hand reach and thermal/current qualification; existing prototype assumptions retained.',
            'Select/package only after local source-end hardware/tool access and whole-source integration.'],
        finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',report)
    print(json.dumps(dict(status=report['status'],seconds=report['worker_wall_seconds'],blank_mm=blank,native=report['native'])),flush=True)


if __name__=='__main__':main()
