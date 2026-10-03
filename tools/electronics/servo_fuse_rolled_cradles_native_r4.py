"""One shared mount repair, not a new holder-position search.

Split front cantilever roofs around bank walls, move their second feet to the
same solid strip, alternate two interfering tie heads, and provide a local
open-bottom cover clearance for the RR stop. Bodies and R4 feeds stay fixed.
Static fit is saved before expensive native recompute; rejected fit does not
produce a nominally selected export. No strength or physical fit claim.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rolled_cradles_native_r3.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r3'", "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-cradles-native-r4'")
replace("CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r3'", "CAD=ROOT/'hardware/cad/studies/servo-fuse-rolled-cradles-native-r4'")
replace("    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r2.py')", "    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r3.py')\n    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r1.py')\n    pin(ROOT/'tools/electronics/servo_fuse_rolled_cradles_native_r2.py')")
replace("    feed=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4'", """    cover_source=ROOT/'hardware/cad/studies/servo-fuse-feed-reliefs-native-r6/CoverFeedReliefs.FCStd';pin(cover_source)
    old_cover=owners['RetainedCover']
    cover_slot=[30,-99,old_cover.BoundBox.ZMin-1,62,-97,116]
    new_cover=old_cover.cut(box(cover_slot))
    assert new_cover.isValid() and len(new_cover.Solids)==1 and new_cover.Volume<old_cover.Volume
    owners['RetainedCover']=new_cover
    feed=ROOT/'hardware/electronics/full-cat/servo-fuse-rolled-source-loop-r4'""")
replace("fy0,fy1=(-94,-92) if leg=='RR'", "fy0,fy1=(-91,-89) if leg=='RR'")
replace("        integral.append((leg+'Roof',roof,True,thick));parts[leg+'_Roof']=box(roof)", """        if leg in ('FL','FR'):
            inner=roof.copy();inner[1]=b[1];inner[4]=b[4]
            outer=roof.copy();outer[3]=-60
            if leg=='FL':outer[1]=b[4]-.2
            else:outer[4]=b[1]+.2
            for suffix,q in (('Inner',inner),('Outer',outer)):
                integral.append((leg+'Roof'+suffix,q,True,thick));parts[leg+'_Roof_'+suffix]=box(q)
        else:
            integral.append((leg+'Roof',roof,True,thick));parts[leg+'_Roof']=box(roof)""")
replace("        for j,x in enumerate((b[0]+4,b[3]-8)):", "        for j,x in enumerate((b[0]+4,-65 if leg in ('FL','FR') else b[3]-8)):")
replace("        z0=b[2]-thick-1.2;z1=b[5]+1.2", "        z0=b[2]-thick-1.2;z1=b[5]+1.2\n        strap_left=39.5 if leg=='RR' else b[0]")
replace("bands=[(b[0]-1.2,y-1.25,z0,b[0],y+1.25,z1)", "bands=[(strap_left-1.2,y-1.25,z0,strap_left,y+1.25,z1)")
replace("(b[0],y-1.25,z0,b[3],y+1.25,b[2]-thick)", "(strap_left,y-1.25,z0,b[3],y+1.25,b[2]-thick)")
replace("(b[0],y-1.25,b[5],b[3],y+1.25,z1)", "(strap_left,y-1.25,b[5],b[3],y+1.25,z1)")
replace("length=2*((b[3]-b[0])+1.2+(z1-z0)-1.2)", "length=2*((b[3]-strap_left)+1.2+(z1-z0)-1.2)")
replace("            head=[b[3]-4.8,y-2.25,z1,b[3],y+2.25,z1+3.5]", """            head_x=b[0] if (leg=='FL' and j==1) or (leg=='RR' and j==0) else b[3]-4.8
            head=[head_x,y-2.25,z1,head_x+4.8,y+2.25,z1+3.5]
            if leg=='RR' and j==0:
                # Rotate the nominal tie head on the outside +X vertical leg,
                # below XS23_9, not into the holder or its underside shelf.
                head=[b[3]+1.2,y-2.25,b[5]-4.8,b[3]+4.7,y+2.25,b[5]]""")
replace("    for i,(n,s) in enumerate(list(parts.items())):", """    # A tie intersects the native union iff it intersects at least one operand.
    # Added-part pairs are checked below; check the retained base once here.
    # Do not reload the same exported fused Deck for every strap segment.
    for n,s in parts.items():
        if '_Tie_' in n:check(n,s,'RetainedDeckBase',base)
    for i,(n,s) in enumerate(list(parts.items())):""")
replace("    for n,s in parts.items():\n        if '_Tie_' in n:check(n,s,'NewNativeDeck',load(CAD/'Deck_WORLD.brep'))", """    # The native union contains exactly the already checked base/Box operands;
    # retain their exact intersection evidence rather than repeat fused checks.
    print('NATIVE_DECK_TIE_COMPONENT_PROOF_REUSED',flush=True)""")
replace("    # Persist actual editable native construction even if shared fit is rejected.", """    if hits or errors or not all(r['full_bearing'] for r in mount):
        save(OUT/'fault.json',dict(status='SHARED_MOUNT_FIT_REJECTED',selected=False,physical_pass=False,
            hits=hits,errors=errors,mounts=mount,source_sha256=pins,script_sha256=sha(Path(__file__)),
            reason='Do not spend native recompute on a rejected mount. Static construction retained.'))
        print('SHARED_MOUNT_REJECTED',len(hits),sum(not r['full_bearing'] for r in mount),flush=True)
        return
    # The RR stop notch is a native editable Part::Cut on the retained cover.
    coverdoc=A.openDocument(str(cover_source))
    try:
        par=coverdoc.addObject('App::VarSet','CantileverCoverParameters');par.addProperty('App::PropertyLength','OpeningHeight');par.OpeningHeight=cover_slot[5]-cover_slot[2]
        tool=coverdoc.addObject('Part::Box','RRCantileverClearanceTool')
        tool.Length=32;tool.Width=2;tool.Placement.Base=A.Vector(*cover_slot[:3]);tool.setExpression('Height','CantileverCoverParameters.OpeningHeight')
        finish=coverdoc.addObject('Part::Cut','CantileverCoverFinished');finish.Base=coverdoc.FeedReliefsFinished;finish.Tool=tool;finish.Refine=False
        coverdoc.recompute();cs=finish.Shape.copy()
        assert cs.isValid() and len(cs.Solids)==1
        assert cs.cut(new_cover).Volume+new_cover.cut(cs).Volume<1e-4
        assert not cs.check(True)
        cv=cs.Volume;par.OpeningHeight=cover_slot[5]-cover_slot[2]+.2;coverdoc.recompute();cp=finish.Shape.Volume;assert cp<cv
        par.OpeningHeight=cover_slot[5]-cover_slot[2];coverdoc.recompute();assert abs(finish.Shape.Volume-cv)<1e-5
        cover_dest=CAD/'CoverCantileverClearance.FCStd';coverdoc.saveAs(str(cover_dest));cs.exportBrep(str(CAD/'Cover_WORLD.brep'))
        cm=MeshPart.meshFromShape(Shape=cs,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert cm.isSolid() and cm.countComponents()==1
        cb=cm.BoundBox;assert max(cb.XLength+10,cb.YLength+10)<256 and cb.ZLength<256
        cm.translate(-cb.XMin,-cb.YMin,-cb.ZMin);cm.write(str(CAD/'Cover_UNSELECTED.stl'))
    finally:A.closeDocument(coverdoc.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-cover-cantilever-') as td:
        moved=Path(td)/cover_dest.name;shutil.copy2(cover_dest,moved);cd=A.openDocument(str(moved))
        try:cd.recompute();assert abs(cd.CantileverCoverFinished.Shape.Volume-cv)<1e-5
        finally:A.closeDocument(cd.Name)
    save(OUT/'cover-checks.json',dict(single_solid=True,strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,
        opening_mm=cover_slot,parameter_volumes_mm3=[cv,cp,cv],selected=False,physical_pass=False))
    # Persist actual editable native Deck only after shared static fit.
""")
replace("        d.recompute();s=f.Shape.copy();strict=s.check(True)", "        d.recompute();s=f.Shape.copy();assert s.isValid() and len(s.Solids)==1\n        strict=s.check(True)")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
