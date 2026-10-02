"""Twelve small lower-lip openings for the R4 input/module lift envelope.

The coarse continuous lift enclosure contacted the cover, not the bank.
Add clearance at its actual witnesses instead of narrowing numeric padding
until a marginal case appears green. Parent head/cover history retained.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
CAD=ROOT/'hardware/cad/studies/servo-fuse-cover-native-r4'
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-native-r4'


def main():
    import FreeCAD as A
    import Part,MeshPart
    begin=datetime.now(timezone.utc);CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists();hashes={}
    def pin(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-lower-loop-lift-r1/checks.json';pin(p)
    old=json.loads(p.read_text(encoding='utf-8'));assert len(old['hits'])==24 and not old['errors']
    assert all(r['module']=='Cover' for r in old['hits'])
    routes=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json';pin(routes)
    spec=json.loads(routes.read_text(encoding='utf-8'));assert not spec['hits'] and not spec['errors']
    src=ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/FuseBankCover.FCStd';pin(src)
    cached=ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/Cover_WORLD.brep';pin(cached);ref=Part.read(str(cached))
    cuts=[]
    for row in spec['placements'].values():
        x,y,z=row['holder'];side=1 if y>0 else -1;lo,hi=sorted((side*96.7,side*99.2))
        assert min(abs(x-mx) for mx in (-84,106))>10,('Cover mount vicinity',x)
        cuts.append([x-2.2,lo,103,x+2.2,hi,107.2])
    assert len(cuts)==12
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,cuts_mm=cuts,
        reason='24 conservative rigid lift enclosure contacts at the lower lip Z104..106.53/Y97..98.62. Changed actual cover, not a numerical waiver.',
        preserves='Four cover mount axes and all existing head tongue/slots; cuts X at least10mm away from cover mount axes.',
        limits='Complete parent carriers/source-side leads remain open; this is not a whole-bank selection.'))
    d=A.openDocument(str(src));name=d.Name
    try:
        previous=d.BankCoverConnected;assert previous.Shape.isValid() and abs(previous.Shape.Volume-ref.Volume)<1e-5
        par=d.addObject('App::VarSet','LowerWireReliefParameters');par.addProperty('App::PropertyLength','Width');par.Width=4.4
        for i,b in enumerate(cuts):
            tool=d.addObject('Part::Box','LowerWireRelief'+str(i));tool.Length=4.4;tool.Width=b[4]-b[1];tool.Height=4.2
            tool.Placement.Base=A.Vector(*b[:3]);tool.setExpression('Length','LowerWireReliefParameters.Width')
            f=d.addObject('Part::Cut','LowerWireCoverCut'+str(i));f.Base=previous;f.Tool=tool;f.Refine=False
            previous.Visibility=False;tool.Visibility=False;previous=f
        print('NATIVE_LOWER_LIP_RELIEFS',flush=True)
        d.recompute();s=previous.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        v=s.Volume;assert v<ref.Volume
        par.Width=4.6;d.recompute();probe=previous.Shape.Volume;assert probe<v
        par.Width=4.4;d.recompute();assert abs(previous.Shape.Volume-v)<1e-5
        dest=CAD/'FuseBankCover.FCStd';d.saveAs(str(dest));final=previous.Name;s.exportBrep(str(CAD/'Cover_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-lower-lip-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.getObject(final).Shape.isValid() and abs(re.getObject(final).Shape.Volume-v)<1e-5
        finally:A.closeDocument(re.Name)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1;b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Cover_x1.stl'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_TWELVE_LOWER_LIP_RELIEFS_SAVED_LIFT_PENDING',selected=False,physical_pass=False,
        native=dest.relative_to(ROOT).as_posix(),single_solid=True,strict_BOP_errors=0,closed_STL=True,
        relocated_reopen=True,parameter_volumes=[v,probe,v],cuts_mm=cuts,removed_mm3=ref.Volume-v,dimensions_mm=dims,
        inherited_static_fit='Subtraction only from retained CoverR3; no new installed material.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    # Recheck the affected lift with the changed cover. No body/Deck reload.
    parent=ROOT/'tools/electronics/servo_fuse_bank_lower_loop_lift_r1.py'
    code=parent.read_text(encoding='utf-8')
    code=code.replace("OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-lower-loop-lift-r1'",
                      "OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-lower-loop-lift-r2'")
    code=code.replace('servo-fuse-cover-native-r3/Cover_WORLD.brep','servo-fuse-cover-native-r4/Cover_WORLD.brep')
    code=code.replace("hits=[];errors=[];pairs=0;segments=0;rows=[]", """p=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-native-r4/checks.json'
    hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    p=ROOT/'tools/electronics/servo_fuse_bank_lower_loop_lift_r1.py';hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-lower-loop-lift-r1/checks.json';hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    hits=[];errors=[];pairs=0;segments=0;rows=[]""")
    exec(compile(code,str(Path(__file__).resolve()),'exec'),{'__name__':'__main__','__file__':str(Path(__file__).resolve())})


if __name__=='__main__':main()
