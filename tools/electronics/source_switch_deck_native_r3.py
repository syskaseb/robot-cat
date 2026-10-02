"""Move only two mounting holes on the retained native S0 Deck."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
PARENT=ROOT/'hardware/electronics/full-cat/source-switch-deck-native-r1'
ASSEMBLY=ROOT/'hardware/electronics/full-cat/source-switch-assembly-finish-r3'
OUT=ROOT/'hardware/electronics/full-cat/source-switch-deck-native-r3'
CAD=ROOT/'hardware/cad/studies/source-switch-deck-native-r3'

def main():
    import FreeCAD as A
    import Part,MeshPart
    start=datetime.now(timezone.utc);hashes={}
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    for folder in (PARENT,ASSEMBLY):
        p=folder/'checks.json';pin(p);m=json.loads(p.read_text(encoding='utf-8'))
        assert not m.get('hits') and not m.get('errors')
        for rel,h in m['source_sha256'].items():assert sha(ROOT/rel)==h,rel
        if folder==PARENT:parent=m
    src=ROOT/parent['native'];pin(src)
    p=ASSEMBLY/'Deck_candidate_UNSELECTED.brep';pin(p);ref=Part.Shape();ref.read(str(p))
    d=A.openDocument(str(src));name=d.Name
    try:
        par=d.addObject('App::VarSet','SwitchBoltParameters');par.addProperty('App::PropertyLength','BoreRadius');par.BoreRadius=1.2
        fill=[];holes=[]
        for i,x in enumerate((-87.5,-37)):
            f=d.addObject('Part::Cylinder','RestoreOldBoltHole'+str(i));f.Radius=1.2;f.Height=4;f.Placement.Base=A.Vector(x,92,105);fill.append(f)
            f=d.addObject('Part::Cylinder','NewBoltHole'+str(i));f.Radius=1.2;f.Height=4.2;f.Placement.Base=A.Vector(x+8,92,104.9)
            f.setExpression('Radius','SwitchBoltParameters.BoreRadius');holes.append(f)
        stock=d.addObject('Part::MultiFuse','RestoredBoltDeck');stock.Shapes=[d.SourceSwitchDeck,*fill]
        cuts=d.addObject('Part::MultiFuse','CorrectedBoltTools');cuts.Shapes=holes
        final=d.addObject('Part::Cut','SourceSwitchFinalDeck');final.Base=stock;final.Tool=cuts
        d.recompute();s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        assert abs(s.Volume-ref.Volume)<1e-4,(s.Volume,ref.Volume)
        v=s.Volume;par.BoreRadius=1.3;d.recompute();probe=final.Shape.Volume;assert probe<v
        par.BoreRadius=1.2;d.recompute();assert abs(final.Shape.Volume-v)<1e-5
        dest=CAD/'DeckSourceSwitch.FCStd';d.saveAs(str(dest));s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-deck-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.SourceSwitchFinalDeck.Shape.isValid() and abs(re.SourceSwitchFinalDeck.Shape.Volume-v)<1e-5
        finally:A.closeDocument(re.Name)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_x1.stl'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_SOURCE_SWITCH_DECK_CORRECTED_NOT_SELECTED',native=dest.relative_to(ROOT).as_posix(),
        selected=False,W5_complete=False,physical_pass=False,single_solid=True,strict_BOP_errors=0,closed_STL=True,
        relocated_reopen=True,parent_native_retained=True,parameter_volumes=[v,probe,v],dimensions_mm=dims,
        deck_bolt_xy=[[-79.5,92],[-29,92]],source_sha256=hashes,script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(status='NATIVE_DECK_R3_COMPLETE_NOT_SELECTED',dimensions_mm=dims,worker_wall_seconds=(end-start).total_seconds())),flush=True)

if __name__=='__main__':main()
