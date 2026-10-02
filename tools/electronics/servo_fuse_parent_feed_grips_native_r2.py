"""Two measured CAD conflicts only: raise RL tie slot and move FR tie head.

R1's native grooves/history/export remain the parent. The RL band contacts
the Pi cable wall ABOVE the old113.6mm slot, not the Deck underside. Extend
only that slot to118.3mm; do not lower all ties or relocate all four feeds.
R1 remains preserved as a failed tie fit. No parent holder mounts selected.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, shutil, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2'
CAD=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r2'


def main():
    import FreeCAD as A
    import Part,MeshPart
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    olddir=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r1'
    oldcad=ROOT/'hardware/cad/studies/servo-fuse-parent-feed-grips-native-r1'
    p=olddir/'checks.json';pin(p);old=json.loads(p.read_text(encoding='utf-8'))
    assert not old['errors'] and {(r['part'],r['owner']) for r in old['hits']}=={
        ('FR_FEED_TIE_4','source-switch-layout-r6/W066_5_DESIGN'),('RL_FEED_TIE_1','R49Deck')}
    source=oldcad/'DeckParentFeedGrips.FCStd';pin(source)
    p=oldcad/'Deck_WORLD.brep';pin(p);base=Part.read(str(p))
    bounds=[28.2,53.05,113.5,29.8,55.95,118.3]
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    expected=base.cut(box(bounds));removed=base.Volume-expected.Volume
    assert removed>0 and expected.isValid() and len(expected.Solids)==1
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,changed_slot_mm=bounds,
        conflict_bounds_mm=[28.8,53.25,113.6,29.6,55.75,117.2],
        FR_head_translation_mm=[12,0,0],removed_wall_mm3=removed,
        retained='Only upper segment of existing RL positive-X tie slot enlarged. Pi mounts and other grips unchanged.',
        remaining='Four parent holder mounts and WAGO/service remain open.'))
    print('ONE_RL_SLOT_EXTENSION',flush=True)
    d=A.openDocument(str(source));name=d.Name
    try:
        par=d.addObject('App::VarSet','UpperFeedTieParameters');par.addProperty('App::PropertyLength','SlotHeight');par.SlotHeight=4.8
        tool=d.addObject('Part::Box','RLFeedTieUpperTool');tool.Length=1.6;tool.Width=2.9;tool.Height=4.8
        tool.Placement.Base=A.Vector(*bounds[:3]);tool.setExpression('Height','UpperFeedTieParameters.SlotHeight')
        f=d.addObject('Part::Cut','ParentFeedGripFinished');f.Base=d.ParentFeedGripDeck;f.Tool=tool;f.Refine=False
        d.recompute();s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        delta=s.cut(expected).Volume+expected.cut(s).Volume;assert delta<1e-4,delta
        before=s.Volume;par.SlotHeight=5;d.recompute();probe=f.Shape.Volume;assert probe<before
        par.SlotHeight=4.8;d.recompute();assert abs(f.Shape.Volume-before)<1e-5
        dest=CAD/'DeckParentFeedGrips.FCStd';d.saveAs(str(dest));s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-feed-slot-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.ParentFeedGripFinished.Shape.isValid() and abs(re.ParentFeedGripFinished.Shape.Volume-before)<1e-5
        finally:A.closeDocument(re.Name)
    print('CHANGED_TIE_CHECKS',flush=True)
    owners,more,_=layout.current_owners();hashes.update(more);owners['R49Deck']=s
    for n in list(owners):
        if '/servo-fuse-bank-restraints-r2/' in n or '/servo-fuse-bank-restraints-fit-r2/' in n:del owners[n]
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):
        pin(p);owners[p.stem]=Part.read(str(p))
    bands={};hits=[];errors=[];pairs=0
    # Inherit all unchanged checks explicitly; the new Deck only loses material.
    # Recheck all20 ties against changed Deck, and moved FR head against owners.
    for p in olddir.glob('*_DESIGN.brep'):
        pin(p);n=p.stem.removesuffix('_DESIGN');t=Part.read(str(p))
        if n=='FR_FEED_TIE_4':t.translate(A.Vector(12,0,0))
        bands[n]=t;t.exportBrep(str(OUT/p.name))
    assert len(bands)==20
    for n,t in bands.items():
        for m,q in owners.items():
            if n!='FR_FEED_TIE_4' and m!='R49Deck':continue
            if not t.BoundBox.intersect(q.BoundBox):continue
            pairs+=1
            try:
                c=t.common(q)
                if c.Volume>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=c.Volume))
            except Exception as exc:errors.append(dict(part=n,owner=m,error=str(exc)))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1;b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Deck_x1.stl'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FOUR_FEED_GRIPS_CLEAR_BODY_MOUNTS_OPEN' if not hits and not errors else 'NATIVE_GRIP_TIE_CONFLICTS',
        selected=False,physical_pass=False,W5_complete=False,grips=4,through_slots=8,
        parent_native_retained=True,native=dest.relative_to(ROOT).as_posix(),hits=hits,errors=errors,pairs=pairs,
        inherited_unchanged_tie_checks='R1 except its2reported contacts; all20against changedDeck and movedFRhead against allowners rechecked.',
        strict_BOP_errors=0,single_solid=True,closed_STL=True,relocated_reopen=True,
        parameter_volumes=[before,probe,before],symmetric_difference_mm3=delta,dimensions_mm=dims,
        removed_wall_mm3=removed,changed_slot_mm=bounds,
        open='Four holder mounts, full parent feeds and WAGO/service order remain open.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,dimensions_mm=dims)),flush=True)


if __name__=='__main__':main()
