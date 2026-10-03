"""Native editable fixed-Deck side channel with the existing two M3 bolts.

Exact R3 full-owner preflight, native Box/Cylinder/Cut/Link/MultiFuse.
Preserve unchanged bank, all wires, channel and output restraint geometry.
Deck has3mm/side brim allowance within the user's256mm printer envelope.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,shutil,tempfile,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-guard-fixed-deck-native-r1'
def main():
    import FreeCAD as A
    import Part,MeshPart
    t=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();pins={}
    fp=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-r3/checks.json';pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    fit=json.loads(fp.read_text(encoding='utf-8'));assert fit['status']=='GUARD_FIXED_DECK_PREFLIGHT_CLEAR' and not fit['hits'] and not fit['errors']
    for rel,h in fit['source_sha256'].items():assert sha(ROOT/rel)==h; pins[rel]=h
    for name in ('servo_fuse_guard_fixed_deck_r1.py','servo_fuse_guard_fixed_deck_r2.py','servo_fuse_guard_fixed_deck_r3.py'):
        rel='tools/electronics/'+name;pins[rel]=sha(ROOT/rel)
    a='hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r2/BankRight_WORLD.brep'
    b='hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-r3/BankRight_CANDIDATE.brep'
    pins[a]=sha(ROOT/a);pins[b]=sha(ROOT/b)
    ba=Part.read(str(ROOT/a));bb=Part.read(str(ROOT/b));assert ba.cut(bb).Volume+bb.cut(ba).Volume<1e-5
    sources={'Deck':('hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r2/FRSourceFixedDeck.FCStd','DeckFixedSourceFinished'),
             'Guard':('hardware/cad/studies/servo-fuse-fr-output-station-native-r5/FRGuardOutputStation.FCStd','FRGuardOutputFinished')}
    docs={k:A.openDocument(str(ROOT/rel)) for k,(rel,name) in sources.items()}
    external=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for f in external:pins[f.relative_to(ROOT).as_posix()]=sha(f)
    d=A.newDocument('GuardFixedDeck');dest=CAD/'GuardFixedDeck.FCStd';d.saveAs(str(dest))
    p=d.addObject('App::VarSet','GuardFixedParameters');p.addProperty('App::PropertyLength','HoleDiameter');p.HoleDiameter=3.4
    def link(n,o):q=d.addObject('App::Link',n);q.setLink(o);q.LinkPlacement=o.Placement;return q
    def box(n,b):q=d.addObject('Part::Box',n);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2];q.Placement.Base=A.Vector(*b[:3]);return q
    def union(n,items):q=d.addObject('Part::MultiFuse',n);q.Shapes=items;q.Refine=False;return q
    def cut(n,base,tool):q=d.addObject('Part::Cut',n);q.Base=base;q.Tool=tool;q.Refine=False;return q
    parent={k:link(k+'Current',docs[k].getObject(name)) for k,(rel,name) in sources.items()}
    stocks=[box(r['name'],r['box_mm']) for r in fit['native_stocks']]
    holes=[]
    for i,(x,z) in enumerate(fit['axes_xz_mm']):
        q=d.addObject('Part::Cylinder','FixedGuardM3Tool'+str(i));q.Height=10
        q.Placement=A.Placement(A.Vector(x,82,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
        q.setExpression('Radius','GuardFixedParameters.HoleDiameter / 2');holes.append(q)
    drill=union('GuardFixedHoleTools',holes)
    fixture=cut('GuardFixedFixtureFinished',union('GuardFixedFixtureStock',stocks),drill)
    guard=cut('GuardFixedFinished',cut('GuardNoOldMovingTab',parent['Guard'],box('ObsoleteBankTabRemoval',fit['old_tab_tool_mm'])),drill)
    exports=[]
    try:
        print('GUARD_FIXED_NATIVE_SMALL',os.getpid(),flush=True);d.recompute()
        nominal=[]
        for tag,q in [('FixedFixture',fixture),('Guard',guard)]:
            b=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-r3'/(tag+'_CANDIDATE.brep');pins[b.relative_to(ROOT).as_posix()]=sha(b);s=Part.read(str(b))
            assert q.Shape.isValid() and len(q.Shape.Solids)==1
            assert q.Shape.cut(s).Volume+s.cut(q.Shape).Volume<1e-5,tag
            nominal.append(q.Shape.Volume)
        p.HoleDiameter=3.6;d.recompute();probe=[fixture.Shape.Volume,guard.Shape.Volume]
        assert all(b<a for a,b in zip(nominal,probe));p.HoleDiameter=3.4;d.recompute()
        restored=[fixture.Shape.Volume,guard.Shape.Volume];assert all(abs(a-b)<1e-5 for a,b in zip(nominal,restored))
        param=dict(hole_diameter_mm=[3.4,3.6,3.4],fixture_guard_volumes_mm3=[nominal,probe,restored])
        save(OUT/'small-preflight.json',dict(parameter=param,native_match_mm3=0,selected=False,physical_pass=False))
        print('GUARD_FIXED_NATIVE_DECK_UNION',flush=True)
        deck=union('DeckFixedGuardFinished',[parent['Deck'],fixture]);d.recompute()
        for tag,q in [('Deck',deck),('Guard',guard)]:
            print('GUARD_FIXED_NATIVE_EXPORT',tag,flush=True);s=q.Shape.copy();strict=s.check(True) or []
            assert s.isValid() and len(s.Solids)==1 and not strict,(tag,len(s.Solids),strict)
            s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            if tag=='Guard':mesh.rotate(0,math.pi/2,0)
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];brim=6 if tag=='Deck' else 10
            assert dims[0]+brim<=256 and dims[1]+brim<=256 and dims[2]<=256,(tag,dims,brim)
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=q.Name,single_solid=True,strict_BOP_errors=0,closed_STL=True,
                volume_mm3=s.Volume,dimensions_mm=dims,total_brim_allowance_mm=brim,shared_parameter=param))
            d.save();save(OUT/'progress.json',dict(exports=exports,selected=False,physical_pass=False))
        for o in d.Objects:
            if hasattr(o,'Visibility'):o.Visibility=False
        deck.Visibility=True;guard.Visibility=True;d.save()
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-guard-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            to=tmp/fp.relative_to(ROOT);to.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,to)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            re.recompute()
            for row in exports:
                s=re.getObject(row['final']).Shape;assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-row['volume_mm3'])<1e-5
                row['relocated_reopen']=True
            for doc in A.listDocuments().values():assert Path(doc.FileName).is_relative_to(tmp),doc.FileName
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_FIXED_DECK_GUARD_COMPLETE_SHARED_SERVICE_OPEN',selected=False,physical_pass=False,W5_complete=False,exports=exports,
        source_sha256=pins,script_sha256=sha(Path(__file__)),external_documents=[f.relative_to(ROOT).as_posix() for f in external],
        changed_pairs=fit['pairs'],contacts=0,bearings=fit['bearings'],actual_deck_foot_embed_mm3=fit['embed_mm3'],
        axes_xz_mm=fit['axes_xz_mm'],Guard_owner='FIXED_DECK',bank_unchanged=True,fasteners_reused=dict(M3x8=2,M3nuts=2),
        added_prints=0,added_ties=0,added_wires=0,added_fasteners=0,
        assembly='Fasten Guard to front face of integral Deck post with existing2M3x8/2nuts before laying source/output wires; cavity side head/nut outside before bank/Cover. Guard and all its cages/wires remain on Deck when bank/Cover are removed.',
        started_utc=t.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-t).total_seconds()))
    print('GUARD_FIXED_NATIVE_COMPLETE',len(exports),flush=True)
if __name__=='__main__':main()
