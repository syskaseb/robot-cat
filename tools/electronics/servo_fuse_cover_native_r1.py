"""Editable local bank clearance in the selected cover, not full E6 reload.

Preserve prior cover/head tie history and four selected cover mounting sites.
Open clearances to the skirt's lower edge to permit vertical removal.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
CAD=ROOT/'hardware/cad/studies/servo-fuse-cover-native-r1'
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    start=datetime.now(timezone.utc)
    CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    src=ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.FCStd'
    cached=ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep'
    ref=Part.read(str(cached));hashes={p.relative_to(ROOT).as_posix():sha(p) for p in (src,cached)}
    cuts=[]
    for side in (-1,1):
        for x in (-57,122):
            lo,hi=sorted((side*90.2,side*97.8))
            cuts.append([x-2.8,lo,103,x+2.8,hi,148])
            lo,hi=sorted((side*88.2,side*97.8))
            cuts.append([x-9.8,lo,103,x+9.8,hi,114.5])
    # 0.25mm witnessed FL3 housing/tongue overlap plus0.5mm clearance.
    # Both existing head tie slots startY133, so leave2.25mm to them.
    cuts.append([-19.25,129.5,134.5,-2.75,130.75,139])
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,source_sha256=hashes,
        cuts_mm=cuts,preserve='All prior head slots, cover mounting holes and native parent features.',
        mount_sites_xy=[[-84,-91],[-84,91],[106,-91],[106,91]],
        removal='Disconnect existing head JR and cut head support ties before lifting. New bank clearance opens below skirt; bank remains on Deck.',
        head_tie_remaining_front_ligament_mm=2.25))
    d=A.openDocument(str(src));name=d.Name
    try:
        previous=[o for o in d.Objects if o.Name.startswith('Interface')][-1]
        assert previous.Shape.cut(ref).Volume+ref.cut(previous.Shape).Volume<1e-5
        parameters=d.addObject('App::VarSet','FuseCoverParameters')
        parameters.addProperty('App::PropertyLength','TongueReliefWidth');parameters.TongueReliefWidth=16.5
        sketches=[]
        for i,b in enumerate(cuts):
            sk=d.addObject('Sketcher::SketchObject','BankClearanceProfile'+str(i));sk.Placement.Base.z=b[2]
            rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1],
                 'FuseCoverParameters.TongueReliefWidth' if i==8 else None);sketches.append(sk)
            t=d.addObject('Part::Extrusion','BankClearance'+str(i));t.Base=sk;t.Dir=A.Vector(0,0,b[5]-b[2]);t.Solid=True
            f=d.addObject('Part::Cut','BankCoverCut'+str(i));f.Base=previous;f.Tool=t;f.Refine=False
            previous.Visibility=False;t.Visibility=False;sk.Visibility=False;previous=f
        d.recompute();s=previous.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        assert all(sk.solve()==0 and sk.FullyConstrained for sk in sketches)
        v=s.Volume;parameters.TongueReliefWidth=16.7;d.recompute();probe=previous.Shape.Volume
        assert probe<v-1e-6
        parameters.TongueReliefWidth=16.5;d.recompute()
        assert abs(previous.Shape.Volume-v)<1e-5
        dest=CAD/'FuseBankCover.FCStd';d.saveAs(str(dest));final=previous.Name
        s.exportBrep(str(CAD/'Cover_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bank-cover-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.getObject(final).Shape.isValid()
            assert abs(re.getObject(final).Shape.Volume-v)<1e-5
        finally:A.closeDocument(re.Name)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Cover_x1.stl'))
    ended=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_COVER_CANDIDATE_ASSEMBLY_OPEN',selected=False,physical_pass=False,
        native=dest.relative_to(ROOT).as_posix(),single_solid=True,strict_BOP_errors=0,
        sketches=len(sketches),closed_STL=True,relocated_reopen=True,parameter_volumes=[v,probe,v],
        removed_mm3=ref.cut(s).Volume,dimensions_mm=dims,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-start).total_seconds()))
    print(json.dumps(dict(status='COVER_SAVED_ASSEMBLY_OPEN',removed_mm3=ref.cut(s).Volume,dimensions_mm=dims)),flush=True)
if __name__=='__main__':main()
