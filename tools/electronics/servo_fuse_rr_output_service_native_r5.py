"""Matched bank/frame and Cover opening, retaining all current wire paths.

R4 joins both real parents and clears installed wires/ties; only Cover
contacts29.79395mm3. Provide its open-sided matching frame clearance,
then export BOTH editable parts with parameter/reopen/closedSTL checks.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_output_service_native_r4.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-rr-output-service-native-r4','servo-fuse-rr-output-service-native-r5')
code=code.replace("    previous=ROOT/", "    pin(ROOT/'tools/electronics/servo_fuse_rr_output_service_native_r4.py')\n    pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-service-native-r4/bridge-preflight.json')\n    previous=ROOT/",1)
code=code.replace("        bridge_hits=[];bridge_errors=[];bridge_pairs=0", '''        # Clearance opens toward the already-open negativeY side. It
        # subtracts Cover material only, not wires or purchased parts.
        cover_bounds=[-70.4,-111,109.15,-54.8,-95.15,130.2]
        relief=Part.makeBox(cover_bounds[3]-cover_bounds[0],cover_bounds[4]-cover_bounds[1],cover_bounds[5]-cover_bounds[2],A.Vector(*cover_bounds[:3]))
        owners['ModifiableCover']=owners['ModifiableCover'].cut(relief)
        bridge_hits=[];bridge_errors=[];bridge_pairs=0''')
at=code.index("    save(OUT/'checks.json'")
code=code[:at]+'''    # Same CURRENT Cover as checked with the support frame above.
    coverrow=next(r for r in prior['exports'] if r['tag']=='Cover')
    coversource=ROOT/coverrow['file'];pin(coversource)
    cd=A.openDocument(str(coversource));coverdest=CAD/'CoverRROutputService.FCStd'
    try:
        cp=cd.addObject('App::VarSet','RRFrameCoverParameters');cp.addProperty('App::PropertyLength','Clearance');cp.Clearance=.2
        ct=cd.addObject('Part::Box','RRSupportFrameOpenSide')
        ct.Placement.Base=A.Vector(-70.4,-111,109.15)
        for prop,value in [('Length',15.2),('Width',15.45),('Height',20.65)]:
            ct.setExpression(prop,f'{value} mm + 2 * RRFrameCoverParameters.Clearance')
        cf=cd.addObject('Part::Cut','RROutputServiceCoverFinished');cf.Base=cd.RearOutputStationsFinished;cf.Tool=ct;cf.Refine=False
        cd.recompute();cs=cf.Shape.copy()
        assert cs.isValid() and len(cs.Solids)==1 and not cs.check(True)
        # Bridge witness is small; never subtract/compare whole huge Deck.
        assert cs.common(bridge.Shape).Volume<1e-5
        cv=cs.Volume;cp.Clearance=.3;cd.recompute();cvp=cf.Shape.Volume
        assert cf.Shape.isValid() and len(cf.Shape.Solids)==1 and abs(cvp-cv)>1e-5
        cp.Clearance=.2;cd.recompute();assert abs(cf.Shape.Volume-cv)<1e-5
        cs=cf.Shape.copy();cd.saveAs(str(coverdest));cs.exportBrep(str(CAD/'Cover_WORLD.brep'))
        cm=MeshPart.meshFromShape(Shape=cs,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert cm.isSolid() and cm.countComponents()==1
        cb=cm.BoundBox;cdims=[cb.XLength,cb.YLength,cb.ZLength]
        assert cdims[0]+10<256 and cdims[1]+10<256 and cdims[2]<256
        cm.translate(-cb.XMin,-cb.YMin,-cb.ZMin);cm.write(str(CAD/'Cover_UNSELECTED.stl'))
    finally:A.closeDocument(cd.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-rr-service-cover-') as td:
        q=Path(td)/coverdest.name;shutil.copy2(coverdest,q);cr=A.openDocument(str(q))
        try:cr.recompute();assert abs(cr.RROutputServiceCoverFinished.Shape.Volume-cv)<1e-5
        finally:A.closeDocument(cr.Name)
    cover_native=dict(file=coverdest.relative_to(ROOT).as_posix(),final='RROutputServiceCoverFinished',single_solid=True,
        strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,parameter_mm=[.2,.3,.2],volumes_mm3=[cv,cvp,cv],dimensions_mm=cdims)
''' +code[at:]
code=code.replace("native=result,assumptions=proof['assumptions']", "native=result,cover_native=cover_native,assumptions=proof['assumptions']")
code=code.replace("replacement='BankRight'", "replacements=['BankRight','Cover']")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
