"""Native vertical tool slots, not the rejected broad lateral corridors.

The 0300330 drawing depicts opposed clips but does not dimension actuation.
Reserve a nominal0.8x3mm flat tip; coupon must confirm it actually releases.
No new housing, wire datum or component substitution.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, math, shutil, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
CAD=ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1'
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-clip-access-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    begin=datetime.now(timezone.utc);CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    source=ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r3/ServoFuseBank.FCStd'
    report=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json'
    drawing=ROOT/'hardware/reference/servo-holder-p0-2026-09-24/0300330.pdf'
    placements=json.loads(report.read_text(encoding='utf-8'))['placements']
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in (source,report,drawing)}
    d=A.openDocument(str(source));docname=d.Name;sketches=[];slots=[];parts={};tools={}
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def span(x0,x1,y0,y1,z0,z1):return [x0,min(y0,y1),z0,x1,max(y0,y1),z1]
    try:
        par=d.addObject('App::VarSet','ClipAccessParameters')
        par.addProperty('App::PropertyLength','SlotWidth');par.SlotWidth=4
        finals=[]
        for side in (-1,1):
            tag='Left' if side==1 else 'Right';parent=d.getObject(tag+'InputSeatFinished');cutters=[]
            for wire,row in placements.items():
                x,cy,z=row['holder']
                if side*cy<0:continue
                for face in (-1,1):
                    y0=cy+face*14.35;y1=cy+face*15.65
                    b=span(x-2,x+2,y0,y1,138.9,146.7)
                    sk=d.addObject('Sketcher::SketchObject',wire+'ClipSlot'+str(face).replace('-','N'))
                    sk.Placement.Base.z=b[2];rect(sk,b[0],b[1],4,b[4]-b[1],'ClipAccessParameters.SlotWidth');sketches.append(sk)
                    extrusion=d.addObject('Part::Extrusion',sk.Name+'Tool');extrusion.Base=sk;extrusion.Dir=A.Vector(0,0,b[5]-b[2]);extrusion.Solid=True;cutters.append(extrusion)
                    slots.append(dict(wire=wire,face=face,box_mm=b))
                    # Shaft enters outside the28.5mm conservative flange, then
                    # tip reaches the depicted latch from below the panel.
                    shaft=box(span(x-1.5,x+1.5,cy+face*14.6,cy+face*15.4,139.5,190))
                    tip=box(span(x-1.5,x+1.5,cy+face*10.5,cy+face*15.4,139.5,140.3))
                    tools[wire+':'+str(face)]=Part.makeCompound([shaft,tip])
            allcuts=d.addObject('Part::MultiFuse',tag+'ClipSlotTools');allcuts.Shapes=cutters
            final=d.addObject('Part::Cut',tag+'ClipAccessFinished');final.Base=parent;final.Tool=allcuts;final.Refine=False;finals.append(final)
            parent.Visibility=False;allcuts.Visibility=False
            for obj in cutters+sketches:obj.Visibility=False
        print('CLIP_SLOTS_RECOMPUTE',flush=True);d.recompute()
        assert len(slots)==24 and all(sk.solve()==0 and sk.FullyConstrained for sk in sketches)
        for f in finals:assert f.Shape.isValid() and len(f.Shape.Solids)==1 and not f.Shape.check(True),f.Name
        before=[f.Shape.Volume for f in finals];par.SlotWidth=4.2;d.recompute();probe=[f.Shape.Volume for f in finals]
        assert all(a>b for a,b in zip(before,probe));par.SlotWidth=4;d.recompute()
        assert all(abs(f.Shape.Volume-v)<1e-5 for f,v in zip(finals,before))
        dest=CAD/'ServoFuseBank.FCStd';d.saveAs(str(dest));parts={f.Name:f.Shape.copy() for f in finals}
    finally:A.closeDocument(docname)
    print('CLIP_SLOTS_SAVED',flush=True)
    with tempfile.TemporaryDirectory(prefix='robot-cat-clip-access-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert all(re.getObject(n).Shape.isValid() and abs(re.getObject(n).Shape.Volume-s.Volume)<1e-5 for n,s in parts.items())
        finally:A.closeDocument(re.Name)
    dims={};removed={}
    for n,s in parts.items():
        s.exportBrep(str(CAD/(n+'_WORLD.brep')))
        parent=ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r3'/((n[:4] if n.startswith('Left') else 'Right')+'InputSeatFinished_WORLD.brep')
        old=Part.read(str(parent));assert s.cut(old).Volume<1e-5
        removed[n]=old.cut(s).Volume;hashes[parent.relative_to(ROOT).as_posix()]=sha(parent)
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0);b=mesh.BoundBox
        dims[n]=[b.XLength,b.YLength,b.ZLength];assert b.XLength+10<256 and b.YLength+10<256 and b.ZLength<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(n+'_x1.stl')))
    for n,s in tools.items():s.exportBrep(str(OUT/(n.replace(':','_')+'_TOOL_RESERVE.brep')))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_CLIP_TOOL_SLOTS_SHARED_FIT_OPEN',selected=False,W5_complete=False,physical_pass=False,
        native=dest.relative_to(ROOT).as_posix(),slots=slots,parts=list(parts),single_solids=True,strict_BOP_errors=0,
        parameter_volumes=[before,probe,before],relocated_reopen=True,closed_STL=True,dimensions_mm=dims,removed_mm3=removed,
        nominal_tool=dict(flat_tip_width_mm=3,flat_tip_thickness_mm=.8,shaft_z_mm=[139.5,190],clip_contact_z_mm=[139.5,140.3],supplier_actuation_dimension_verified=False),
        open='Shared cover/head-interface fit next. Verify actual clip actuation on the fit coupon; reservations are project assumptions, not a manufacturer tool instruction.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print('CLIP_SLOTS_EXPORT_COMPLETE',flush=True)
if __name__=='__main__':main()
