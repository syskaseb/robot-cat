"""Retain selected R49 Deck history; add twelve editable sweeps and four bores.

Route spines are pinned exact circular construction paths. Clearance radius
and bolt radius are editable in the native document; no whole E6 reload.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-deck-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-deck-native-r1'
def main():
    import FreeCAD as A
    import Part,MeshPart
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    src=ROOT/'hardware/cad/studies/source-switch-deck-native-r3/DeckSourceSwitch.FCStd';pin(src)
    route_dir=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11'
    p=route_dir/'checks.json';pin(p);meta=json.loads(p.read_text(encoding='utf-8'))
    assert not meta['hits'] and not meta['errors'] and meta['unchanged_deck_portals_proven']
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-native-r5/checks.json';pin(p)
    bank=json.loads(p.read_text(encoding='utf-8'));axes=bank['deck_bolt_xy'];assert len(axes)==4
    ref_path=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-native-r5/Deck_candidate_UNSELECTED.brep';pin(ref_path)
    ref=Part.read(str(ref_path));d=A.openDocument(str(src));name=d.Name
    try:
        par=d.addObject('App::VarSet','FuseDeckParameters')
        par.addProperty('App::PropertyLength','PortalRadius');par.PortalRadius=1.95
        par.addProperty('App::PropertyLength','BoltRadius');par.BoltRadius=1.2
        cutters=[]
        for n,spec in meta['placements'].items():
            path=route_dir/(n+'_CENTERLINE.brep');pin(path)
            spine=d.addObject('PartDesign::Feature',n+'RouteSpine');spine.Shape=Part.Wire(Part.read(str(path)).Edges)
            spine.addProperty('App::PropertyString','PinnedSource');spine.PinnedSource=path.relative_to(ROOT).as_posix()
            spine.addProperty('App::PropertyString','PinnedSHA256');spine.PinnedSHA256=sha(path)
            profile=d.addObject('Part::Circle',n+'PortalProfile');profile.Radius=1.95
            profile.setExpression('Radius','FuseDeckParameters.PortalRadius')
            start=spec['start'];side=1 if start[1]>0 else -1
            profile.Placement=A.Placement(A.Vector(*start),A.Rotation(A.Vector(0,0,1),A.Vector(0,side,0)))
            sweep=d.addObject('Part::Sweep',n+'PortalSweep');sweep.Sections=[profile];sweep.Spine=(spine,[])
            sweep.Solid=True;sweep.Frenet=False;cutters.append(sweep)
        for i,(x,y) in enumerate(axes):
            bore=d.addObject('Part::Cylinder','FuseBankBolt'+str(i));bore.Radius=1.2;bore.Height=4.2
            bore.Placement.Base=A.Vector(x,y,104.9);bore.setExpression('Radius','FuseDeckParameters.BoltRadius');cutters.append(bore)
        tools=d.addObject('Part::MultiFuse','FuseBankDeckTools');tools.Shapes=cutters;tools.Refine=False
        final=d.addObject('Part::Cut','FuseBankDeck');final.Base=d.SourceSwitchFinalDeck;final.Tool=tools;final.Refine=True
        d.recompute();s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        delta=s.cut(ref).Volume+ref.cut(s).Volume;assert delta<1e-4,delta
        before=s.Volume;par.PortalRadius=2.05;d.recompute();probe=final.Shape.Volume;assert probe<before
        par.PortalRadius=1.95;d.recompute();assert abs(final.Shape.Volume-before)<1e-5
        dest=CAD/'DeckFuseBank.FCStd';d.saveAs(str(dest));s.exportBrep(str(CAD/'Deck_WORLD.brep'))
        portal_shapes=[o.Shape.copy() for o in cutters[:12]]
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fuse-deck-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.FuseBankDeck.Shape.isValid() and abs(re.FuseBankDeck.Shape.Volume-before)<1e-5
        finally:A.closeDocument(re.Name)
    for i,p in enumerate(portal_shapes):assert p.common(s).Volume<1e-5,i
    bearings=[]
    for x,y in axes:
        ring=Part.makeCylinder(2.5,3.8,A.Vector(x,y,105.1)).cut(Part.makeCylinder(1.2,4.1,A.Vector(x,y,105)))
        missing=ring.cut(s).Volume;assert missing<1e-5;bearings.append(dict(xy=[x,y],missing_mm3=missing))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1;b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_x1.stl'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_DECK_FULL_PORTALS_BEARING_CLEAR_NOT_SELECTED',selected=False,W5_complete=False,physical_pass=False,
        native=dest.relative_to(ROOT).as_posix(),parent_native_retained=True,editable_portal_sweeps=12,bolt_axes=axes,
        strict_BOP_errors=0,single_solid=True,closed_STL=True,relocated_reopen=True,symmetric_difference_mm3=delta,
        full_through_portals=12,bearing_checks=bearings,parameter_volumes=[before,probe,before],dimensions_mm=dims,
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(status='NATIVE_DECK_SAVED',delta_mm3=delta,dimensions_mm=dims)),flush=True)
if __name__=='__main__':main()
