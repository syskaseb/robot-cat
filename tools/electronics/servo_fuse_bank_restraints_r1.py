"""Integral bank output insulation seats; retain R5 native panel/mount history.

Twelve ties from the existing T18I bag, no new electronics or connectors.
Inputs/complete moving leg spans remain open, not silently counted complete.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,math,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
CAD=ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r1'
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-restraints-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    begin=datetime.now(timezone.utc);CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    src=ROOT/'hardware/cad/studies/servo-fuse-bank-native-r5/ServoFuseBank.FCStd'
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-outputs-r1/checks.json'
    output=json.loads(p.read_text(encoding='utf-8'));assert not output['hits'] and not output['errors']
    hashes={q.relative_to(ROOT).as_posix():sha(q) for q in (src,p)}
    specs=output['lengths'];d=A.openDocument(str(src));name=d.Name;sketches=[];parts={};ties={};slots=[]
    def block(n,b):
        sk=d.addObject('Sketcher::SketchObject',n+'Profile');sk.Placement.Base.z=b[2]
        rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1]);sketches.append(sk)
        t=d.addObject('Part::Extrusion',n);t.Base=sk;t.Dir=A.Vector(0,0,b[5]-b[2]);t.Solid=True
        return t
    def bbox(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    try:
        par=d.addObject('App::VarSet','OutputSeatParameters');par.addProperty('App::PropertyLength','GrooveRadius');par.GrooveRadius=1.8
        finals=[]
        for side in (-1,1):
            tag='Right' if side<0 else 'Left';stock=[d.getObject(tag+'Finished')];cutters=[]
            for row in specs:
                x,y,z=row['bank_exit_mm']
                if side*y<0:continue
                n=row['id'];lo,hi=sorted((side*132,side*142))
                stock.append(block(n+'Seat',[x-6,lo,z-3.4,x+6,hi,z-1.2]))
                lo,hi=sorted((side*134,side*136))
                stock.append(block(n+'Rib',[x-4,lo,z-3.4,x+4,hi,144.7]))
                groove=d.addObject('Part::Cylinder',n+'WirePass');groove.Radius=1.8;groove.Height=4
                groove.setExpression('Radius','OutputSeatParameters.GrooveRadius')
                groove.Placement=A.Placement(A.Vector(x,133 if side>0 else -137,z),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
                cutters.append(groove)
                for i,dx in enumerate((-3.5,3.5)):
                    lo,hi=sorted((side*137,side*140));b=[x+dx-1,lo,z-3.6,x+dx+1,hi,z-.9]
                    cutters.append(block(n+'TieSlot'+str(i),b));slots.append(dict(id=n,box_mm=b))
                lo,hi=sorted((side*137.25,side*139.75))
                bands=[bbox([x+dx-.6,lo,z-4.6,x+dx+.6,hi,z+2.4]) for dx in (-3.5,3.5)]
                bands += [bbox([x-4.1,lo,z-4.6,x+4.1,hi,z-3.4]),bbox([x-4.1,lo,z+1.2,x+4.1,hi,z+2.4])]
                ties[n]=Part.makeCompound(bands)
            raw=d.addObject('Part::MultiFuse',tag+'OutputSeatStock');raw.Shapes=stock;raw.Refine=False
            holes=d.addObject('Part::MultiFuse',tag+'OutputSeatTools');holes.Shapes=cutters
            f=d.addObject('Part::Cut',tag+'OutputSeatFinished');f.Base=raw;f.Tool=holes;f.Refine=True;finals.append(f)
        d.recompute()
        for f in finals:assert f.Shape.isValid() and len(f.Shape.Solids)==1 and not f.Shape.check(True),f.Name
        assert all(s.solve()==0 and s.FullyConstrained for s in sketches)
        before=[f.Shape.Volume for f in finals];par.GrooveRadius=1.9;d.recompute();probe=[f.Shape.Volume for f in finals]
        assert all(a>b for a,b in zip(before,probe));par.GrooveRadius=1.8;d.recompute()
        assert all(abs(f.Shape.Volume-v)<1e-5 for f,v in zip(finals,before))
        dest=CAD/'ServoFuseBank.FCStd';d.saveAs(str(dest));parts={f.Name:f.Shape.copy() for f in finals}
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bank-seats-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute()
            assert all(re.getObject(n).Shape.isValid() and abs(re.getObject(n).Shape.Volume-s.Volume)<1e-5 for n,s in parts.items())
        finally:A.closeDocument(re.Name)
    dims={}
    for n,s in parts.items():
        s.exportBrep(str(CAD/(n+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0);b=mesh.BoundBox
        dims[n]=[b.XLength,b.YLength,b.ZLength];assert b.XLength+10<256 and b.YLength+10<256 and b.ZLength<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(n+'_x1.stl')))
    for n,s in ties.items():s.exportBrep(str(OUT/(n+'_TIE_DESIGN.brep')))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_OUTPUT_SEATS_ASSEMBLY_OPEN',selected=False,physical_pass=False,W5_complete=False,
        native=dest.relative_to(ROOT).as_posix(),strict_BOP_errors=0,closed_STLs=True,relocated_reopen=True,
        new_constrained_sketches=len(sketches),parameter_volumes=[before,probe,before],dimensions_mm=dims,
        ties=12,tie_type='Existing HellermannTyton T18I, planning envelope2.5wide/1.2thick, cinch on insulation only',
        slots=slots,print_policy='Roof face down; local seat overhangs up to6mm need supports considered in phase2, not slicer-qualified.',
        remaining='Assembly collisions/access and input strain relief; full moving leg spans open.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(status='NATIVE_OUTPUT_SEATS_SAVED',dimensions_mm=dims)),flush=True)
if __name__=='__main__':main()
