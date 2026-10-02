"""Retain editable R48 Deck and add the accepted R6 switch interface only."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
LAYOUT=ROOT/'hardware/electronics/full-cat/source-switch-layout-r6'
REST=ROOT/'hardware/electronics/full-cat/source-switch-restraints-r2'
OUT=ROOT/'hardware/electronics/full-cat/source-switch-deck-native-r1'
CAD=ROOT/'hardware/cad/studies/source-switch-deck-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    layout=json.loads((LAYOUT/'checks.json').read_text(encoding='utf-8'))
    restraint=json.loads((REST/'checks.json').read_text(encoding='utf-8'))
    assert not layout['hits'] and not layout['errors'] and not restraint['hits'] and not restraint['errors']
    hashes={}
    def pin(p):p=Path(p);hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    for p in (LAYOUT/'checks.json',REST/'checks.json'):pin(p)
    for meta in (layout,restraint):
        for path,h in meta['source_sha256'].items():assert sha(ROOT/path)==h,path
    assert sha(ROOT/'tools/electronics/source_switch_layout_r6.py')==layout['script_sha256']
    assert sha(ROOT/'tools/electronics/source_switch_restraints_r2.py')==restraint['script_sha256']
    expected=Part.Shape();expected.read(str(REST/'Deck_candidate_UNSELECTED.brep'));pin(REST/'Deck_candidate_UNSELECTED.brep')
    src=ROOT/'hardware/cad/studies/battery-feed-pair-r2/DeckBatteryFeed.FCStd';pin(src)
    dest=CAD/'DeckSourceSwitch.FCStd';d=A.openDocument(str(src));name=d.Name
    try:
        d.saveAs(str(dest));par=d.addObject('App::VarSet','SwitchWireParameters')
        par.addProperty('App::PropertyLength','GrooveRadius');par.GrooveRadius=2.35
        sketches=[]
        def block(n,b):
            sk=d.addObject('Sketcher::SketchObject',n+'Profile');sk.Placement.Base.z=b[2]
            rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1]);sketches.append(sk)
            f=d.addObject('Part::Extrusion',n);f.Base=sk;f.Dir=A.Vector(0,0,b[5]-b[2]);f.Solid=True;return f
        def cut(n,a,b):
            f=d.addObject('Part::Cut',n);f.Base=a;f.Tool=b;f.Refine=False;return f
        slots=[];seats=[]
        for i,x in enumerate((-87.5,-37)):
            f=d.addObject('Part::Cylinder','SwitchDeckBore'+str(i));f.Radius=1.2;f.Height=4.2;f.Placement.Base=A.Vector(x,92,104.9);slots.append(f)
        for i,p in enumerate(sorted(LAYOUT.glob('Portal_*_UNSELECTED.brep'))):
            pin(p);s=Part.Shape();s.read(str(p));f=d.addObject('PartDesign::Feature','SourceWirePortal'+str(i));f.Shape=s
            f.addProperty('App::PropertyString','PinnedSource');f.PinnedSource=p.relative_to(ROOT).as_posix()
            f.addProperty('App::PropertyString','PinnedSHA256');f.PinnedSHA256=sha(p);slots.append(f)
        for spec in restraint['specs']:
            n=spec['name'];b=spec['seat_box_mm'];pad=block(n+'RawCradle',b)
            f=d.addObject('Part::Cylinder',n+'WireGroove');f.Radius=2.35;f.Height=b[4]-b[1]+.2
            f.setExpression('Radius','SwitchWireParameters.GrooveRadius')
            p=spec['groove_centre'];f.Placement=A.Placement(A.Vector(p[0],b[1]-.1,p[2]),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
            seat=cut(n+'GroovedCradle',pad,f)
            if spec['tie_tunnel']:
                tunnel=block(n+'TieTunnel',spec['tie_tunnel']);seat=cut(n+'TunnelCradle',seat,tunnel)
            for i,b in enumerate(spec['tie_lanes']):
                tool=block(n+'TieLane'+str(i),b);slots.append(tool);seat=cut(n+'SlottedCradle'+str(i),seat,tool)
            seats.append(seat)
        allslots=d.addObject('Part::MultiFuse','SourceSwitchTools');allslots.Shapes=slots;allslots.Refine=False
        base=cut('SourceSwitchSlottedDeck',d.BatteryFeedDeck,allslots)
        final=d.addObject('Part::MultiFuse','SourceSwitchDeck');final.Shapes=[base,*seats];final.Refine=False
        print('Switch Deck: new features saved; recomputing',flush=True)
        d.recompute(sketches);d.save();d.recompute()
        s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        assert all(o.FullyConstrained and o.solve()==0 for o in sketches)
        delta=abs(s.Volume-expected.Volume);assert delta<1e-4,delta
        volume=s.Volume;par.GrooveRadius=2.45;d.recompute();probe=final.Shape.Volume;assert abs(probe-volume)>1e-5
        par.GrooveRadius=2.35;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        d.save();s.exportBrep(str(CAD/'Deck_WORLD.brep'))
        print('Switch Deck: restored parameter and saved native proof',flush=True)
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-switch-deck-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.SourceSwitchDeck.Shape.isValid()
            assert len(re.SourceSwitchDeck.Shape.Solids)==1 and abs(re.SourceSwitchDeck.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(re.Name)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_x1.stl'))
    end=datetime.now(timezone.utc)
    report=dict(status='NATIVE_SOURCE_SWITCH_DECK_COMPLETE_NOT_SELECTED',native=dest.relative_to(ROOT).as_posix(),
        selected=False,W5_complete=False,physical_pass=False,single_solid=True,strict_BOP_errors=0,closed_STL=True,
        fully_constrained_new_sketches=len(sketches),parameter_volumes=[volume,probe,volume],relocated_reopen=True,
        parent_native_retained=True,comparison_scope='Unchanged native parent plus pinned local additions; volume tolerance1e-4mm3, not whole robot audit.',
        candidate_volume_difference_mm3=delta,dimensions_mm=dims,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',report);print(json.dumps(report),flush=True)

if __name__=='__main__':main()
