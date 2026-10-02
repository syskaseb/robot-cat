"""Move two source-bridge bolts out of its posts; retain its completed body.

Correct local source tie head reserves to enclose the already recorded exact
T18I4.8x4.5x3.5. No additional electronics or new fastener type is introduced.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,shutil,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/battery-feed-mount-finish-r2'
CAD=ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2'


def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    source=ROOT/'hardware/cad/studies/battery-feed-bridge-r1/BatteryFeedBridge.FCStd'
    dest=CAD/source.name;d=A.openDocument(str(source));name=d.Name
    try:
        d.saveAs(str(dest))
        for i in range(2):
            # Dimensioned rectangle: final constraint is its Y width, not a
            # change of sketch placement or any guessed inherited constraint.
            sk=d.getObject('DeckFoot'+str(i)+'Profile')
            assert sk.ConstraintCount==12 and sk.GeometryCount==4
            for k in reversed(range(sk.ConstraintCount)):sk.delConstraint(k)
            for k in reversed(range(sk.GeometryCount)):sk.delGeometry(k)
            rect(sk,(-10,61)[i]-6,42,12,17)
            post=d.getObject('Stem'+str(i)+'Profile')
            for k in reversed(range(post.ConstraintCount)):post.delConstraint(k)
            for k in reversed(range(post.GeometryCount)):post.delGeometry(k)
            rect(post,(-10,61)[i]-4,42,8,6)
            f=d.getObject('MountBore'+str(i));v=f.Placement.Base;v.y=53;f.Placement.Base=v
        sk=d.FloorProfile
        for k in reversed(range(sk.ConstraintCount)):sk.delConstraint(k)
        for k in reversed(range(sk.GeometryCount)):sk.delGeometry(k)
        rect(sk,-32,42,97,57)
        for n,top in [('Plus',71),('Return',70.3),('FreeSwitchLead',71)]:
            d.getObject(n+'Seat').Dir=A.Vector(0,0,top-59)
        # Tie lanes must avoid the left suspension post, not pass through it.
        for i,x in enumerate((-2,24)):
            for j,y in enumerate((54.85,73.65)):
                sk=d.getObject('HolderTieSlot%d_%dProfile'%(i,j))
                # A large signed-distance edit let Sketcher mirror the slot.
                # Rebuild this owned rectangle explicitly; keep its feature ID.
                for k in reversed(range(sk.ConstraintCount)):sk.delConstraint(k)
                for k in reversed(range(sk.GeometryCount)):sk.delGeometry(k)
                rect(sk,x-1.6,y,3.2,1.4)
        d.recompute();s=d.FinishedBatteryFeedBridge.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        sketches=[o for o in d.Objects if o.TypeId=='Sketcher::SketchObject']
        assert all(o.FullyConstrained and o.solve()==0 for o in sketches)
        volume=s.Volume;d.BridgeParameters.FloorThickness=2.2;d.recompute();probe=d.FinishedBatteryFeedBridge.Shape.Volume
        assert abs(probe-volume)>1e-5
        d.BridgeParameters.FloorThickness=2;d.recompute();assert abs(d.FinishedBatteryFeedBridge.Shape.Volume-volume)<1e-5
        d.save();s.exportBrep(str(CAD/'Bridge_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-feet-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);d=A.openDocument(str(q))
        try:
            d.recompute();assert abs(d.FinishedBatteryFeedBridge.Shape.Volume-volume)<1e-5
            assert d.FinishedBatteryFeedBridge.Shape.isValid()
        finally:A.closeDocument(d.Name)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def cy(x,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,53,z))
    parts={};checks=[]
    for i,x in enumerate((-10,61)):
        parts['M2x12_'+str(i)]=cy(x,97.3,1,12).fuse(cy(x,109.3,1.9,2))
        parts['M2Washers_'+str(i)]=Part.makeCompound([cy(x,z,2.5,.3).cut(cy(x,z-.1,1.1,.5)) for z in (100.7,109)])
        parts['M2Nut_'+str(i)]=cy(x,99.1,2.31,1.6).cut(cy(x,99,1,1.8))
        parts['NutToolReserve_'+str(i)]=cy(x,90,3.5,11)
        parts['HeadToolReserve_'+str(i)]=cy(x,111.3,2.5,24)
        for n in ('M2x12_','M2Washers_','M2Nut_','NutToolReserve_','HeadToolReserve_'):
            key=n+str(i);hit=parts[key].common(s).Volume
            assert hit<1e-5,(key,hit);checks.append(dict(part=key,owner='Bridge',hit_mm3=hit))
    old=ROOT/'hardware/electronics/full-cat/battery-feed-bridge-r1'
    for n,x,y in [('PlusWireTie',44,77.5),('ReturnWireTie',51,77.5),('FreeSwitchLeadWireTie',-26,65),
                  ('F0BodyTie0',-2,54),('F0BodyTie1',24,54),('XT60BodyTie',39.5,88)]:
        pp=old/(n+'_DESIGN.brep');t=Part.Shape();t.read(str(pp))
        assert len(t.Solids)==5,n
        # The original head is the fifth explicitly modeled solid. Enlarge it,
        # never silently reuse the undersized4x4 project head as conservative.
        if n in ('PlusWireTie','ReturnWireTie'):
            top=70.55 if n=='ReturnWireTie' else 71.25
            band=[box([sx,y-1.25,55.8,sx+1.2,y+1.25,top+1.2]) for sx in (x-3.4,x+2.2)]
            band.extend([box([x-3.4,y-1.25,top,x+3.4,y+1.25,top+1.2]),
                         box([x-3.4,y-1.25,55.8,x+3.4,y+1.25,57])])
        elif n=='FreeSwitchLeadWireTie':
            band=[box([x-1.25,sy,55.8,x+1.25,sy+1.2,72.45]) for sy in (y-3.9,y+2.7)]
            band.extend([box([x-1.25,y-3.9,71.25,x+1.25,y+3.9,72.45]),
                         box([x-1.25,y-3.9,55.8,x+1.25,y+3.9,57])])
        elif n.startswith('F0BodyTie'):
            band=list(t.Solids[:4]);oldx=-12 if n.endswith('0') else 29
            for piece in band:piece.translate(A.Vector(x-oldx,0,0))
        else:band=list(t.Solids[:4])
        parts[n]=Part.makeCompound(band+[box([x-2.5,y-2.5,52,x+2.5,y+2.5,56])])
        hit=parts[n].common(s).Volume;assert hit<1e-5,(n,hit)
        checks.append(dict(part=n,owner='Bridge',hit_mm3=hit))
    for n,t in parts.items():t.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength];assert max(dims)+10<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Bridge_x1.stl'))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NATIVE_BRIDGE_FASTENER_CLEAR_PENDING_DECK_PAIR',checks=checks,
        native=dest.relative_to(ROOT).as_posix(),fully_constrained_sketches=len(sketches),single_solid=True,
        strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,relocated_reopen=True,parameter_volumes=[volume,probe,volume],
        new_bolt_xy=[[-10,53],[61,53]],old_wrong_bolt_xy=[[-10,61],[61,61]],
        post_y_mm=[42,48],floor_y_mm=[42,99],foot_y_mm=[42,59],
        tie_head_exact_mm=[4.8,4.5,3.5],tie_head_reserve_mm=[5,5,4],
        corrected_F0_body_tie_x_mm=[-2,24],corrected_wire_cradle_tops_mm=[71,70.3,71],
        source_sha256={source.relative_to(ROOT).as_posix():sha(source)},script_sha256=sha(Path(__file__)),
        source_native_preserved=True,tool_reserves_are_prototype_not_tool_manufacturer=True,
        selected=False,W5_complete=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(status='BRIDGE_FIXED',seconds=(end-start).total_seconds(),parts=len(parts))),flush=True)


if __name__=='__main__':main()
