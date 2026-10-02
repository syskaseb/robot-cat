"""Four checked feed grooves, correct under-Deck ties, editable native Deck.

Parent-feedR1 holder shelves conflict with cover/brackets and are NOT used.
Only its clear local grip interfaces survive. No body mounts or full parent
feed route is selected or declared complete by this limited native result.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, shutil, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r1'


def main():
    import FreeCAD as A
    import Part,MeshPart
    import servo_fuse_parent_feeds_r1 as P
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    source=ROOT/'hardware/cad/studies/servo-fuse-deck-native-r1/DeckFuseBank.FCStd';pin(source)
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feeds-r1/checks.json';pin(parent)
    report=json.loads(parent.read_text(encoding='utf-8'))
    assert not report['errors'] and report['hits']
    assert not any(r['part'].endswith(('_GRIP','_WIRE')) for r in report['hits'])
    pin(ROOT/'tools/electronics/servo_fuse_parent_feeds_r1.py')
    shapes,additions,holes,rows=P.geometry(A,Part)
    grips={n:s for n,s in additions.items() if n.endswith('_GRIP')}
    holes=[h for h in holes if h['kind']=='feed_tie'];assert len(grips)==4 and len(holes)==8
    basepath=ROOT/'hardware/cad/studies/servo-fuse-deck-native-r1/Deck_WORLD.brep';pin(basepath)
    expected=Part.read(str(basepath))
    for s in grips.values():expected=expected.fuse(s)
    for h in holes:
        b=h['bounds_mm'];expected=expected.cut(Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-104.9,A.Vector(b[0],b[1],104.9)))
    print('NATIVE_FOUR_FEED_GRIPS',flush=True)
    d=A.openDocument(str(source));name=d.Name
    try:
        par=d.addObject('App::VarSet','ParentFeedGripParameters');par.addProperty('App::PropertyLength','GrooveRadius');par.GrooveRadius=2.75
        finished=[];through=[]
        def box_obj(n,b):
            o=d.addObject('Part::Box',n);o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=A.Vector(*b[:3]);return o
        for row in rows:
            leg=row['leg'];x,y,_=row['WAGO_mm'];side=1 if y>0 else -1;lo,hi=sorted((side*50.5,side*57.5))
            raw=box_obj(leg+'ParentGripBlank',[x-4.5,lo,109,x+4.5,hi,113.5])
            groove=d.addObject('Part::Cylinder',leg+'ParentGroove');groove.Radius=2.75;groove.Height=hi-lo+.2
            groove.Placement=A.Placement(A.Vector(x,lo-.1,113.5),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
            groove.setExpression('Radius','ParentFeedGripParameters.GrooveRadius')
            cut=d.addObject('Part::Cut',leg+'ParentGrip');cut.Base=raw;cut.Tool=groove;finished.append(cut)
        union=d.addObject('Part::MultiFuse','ParentFeedGripDeckUnion');union.Shapes=[d.FuseBankDeck]+finished
        for i,h in enumerate(holes):
            b=h['bounds_mm'];through.append(box_obj('ParentFeedTieThrough'+str(i),[b[0],b[1],104.9,b[3],b[4],b[5]]))
        tools=d.addObject('Part::MultiFuse','ParentFeedTieTools');tools.Shapes=through
        final=d.addObject('Part::Cut','ParentFeedGripDeck');final.Base=union;final.Tool=tools;final.Refine=True
        d.recompute();s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        delta=s.cut(expected).Volume+expected.cut(s).Volume;assert delta<1e-4,delta
        before=s.Volume;par.GrooveRadius=2.85;d.recompute();probe=final.Shape.Volume;assert probe<before
        par.GrooveRadius=2.75;d.recompute();assert abs(final.Shape.Volume-before)<1e-5
        dest=CAD/'DeckParentFeedGrips.FCStd';d.saveAs(str(dest));s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-parent-grips-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.ParentFeedGripDeck.Shape.isValid() and abs(re.ParentFeedGripDeck.Shape.Volume-before)<1e-5
        finally:A.closeDocument(re.Name)
    print('CHANGED_FOUR_TIES',flush=True)
    owners,more,_=layout.current_owners();hashes.update(more);owners['R49Deck']=s
    for n in list(owners):
        if '/servo-fuse-bank-restraints-r2/' in n or '/servo-fuse-bank-restraints-fit-r2/' in n:del owners[n]
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):
        pin(p);owners[p.stem]=Part.read(str(p))
    hits=[];errors=[];pairs=0;bands={}
    for n,t in shapes.items():
        if '_FEED_TIE_' not in n:continue
        # Old bottom band at108..109 crossed the Deck. Put it under the
        # actual105mm underside; extend only the two vertical side bands.
        b=t.BoundBox;coords=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
        index=int(n.rsplit('_',1)[1])
        if index in (0,1):coords[2]=103.8
        if index==3:coords[2:3]=[103.8];coords[5]=105
        q=Part.makeBox(coords[3]-coords[0],coords[4]-coords[1],coords[5]-coords[2],A.Vector(*coords[:3]));bands[n]=q
        q.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    for n,q in bands.items():
        for m,t in owners.items():
            if not q.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                c=q.common(t)
                if c.Volume>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=c.Volume))
            except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1;b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_x1.stl'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FOUR_FEED_GRIPS_CLEAR_BODY_MOUNTS_OPEN' if not hits and not errors else 'NATIVE_GRIP_TIE_CONFLICTS',
         selected=False,physical_pass=False,W5_complete=False,grips=4,through_slots=8,
         parent_native_retained=True,native=dest.relative_to(ROOT).as_posix(),
         hits=hits,errors=errors,pairs=pairs,strict_BOP_errors=0,single_solid=True,
         closed_STL=True,relocated_reopen=True,parameter_volumes=[before,probe,before],
         symmetric_difference_mm3=delta,dimensions_mm=dims,
         replaced_ties='Only4feed bottom/side bands, actual105mm Deck underside; no shelf/holder model inherited.',
         open='Four holder carriers, full parent feeds and lever/service order remain open. Do not select this partial interface alone.',
         source_sha256=hashes,script_sha256=sha(Path(__file__)),
         started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,dimensions_mm=dims)),flush=True)


if __name__=='__main__':main()
