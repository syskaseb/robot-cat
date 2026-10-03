"""One coupled removable-cover interface, retaining the fixed FR source grip.

The entire Deck extension seat/riser sweep opens through the cover skirt.
Move only the front-left cover screw four mm left, with one replacement
bracket using its unchanged Deck screw. No new installed parts or fasteners.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys,json,math,tempfile,shutil,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-cover-offset-mount-native-r1'
CAD=ROOT/'hardware/cad/studies/servo-fuse-cover-offset-mount-native-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    t=datetime.now(timezone.utc);pins={};OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    def read(rel):pins[rel]=sha(ROOT/rel);return json.loads((ROOT/rel).read_text(encoding='utf-8'))
    parentrec=read('hardware/electronics/full-cat/servo-fuse-cover-source-joint-service-r5/checks.json')
    failed=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r20/checks.json')
    assert not failed['errors'] and failed['completed_clear_lifts_mm']==[2,5,10]
    assert len(failed['hits'])==1 and (failed['hits'][0]['phase'],failed['hits'][0]['owner'])==('sampled_lift_30','CandidateDeck')
    fit=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-r3/checks.json')
    seat=next(r for r in fit['retained_native_seat_datums'] if r['role']=='Extension')
    stocks=[r['box_mm'] for r in fit['native_stocks'] if r['name'].startswith('Extension')]
    b=seat['seat_bounds_mm'];stocks.append(b)
    # Complete stationary feature, not the single 30mm witness.
    sweep=[min(b[i] for b in stocks) for i in range(3)]+[max(b[i] for b in stocks) for i in range(3,6)]
    assert sweep==[-83.5,-102,105,-79.5,-89,160.64101615137753],sweep
    row=parentrec['exports'][0];d=A.openDocument(str(ROOT/row['file']))
    external=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName))
    for fp in external:pins[fp.relative_to(ROOT).as_posix()]=sha(fp)
    parent=d.getObject(row['final']);params=d.addObject('App::VarSet','OffsetMountParameters')
    params.addProperty('App::PropertyLength','Allowance');params.Allowance=.35
    def box(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2];q.Placement.Base=A.Vector(*b[:3]);return q
    def compound(name,items):q=d.addObject('Part::Compound',name);q.Links=items;return q
    def cut(name,base,tool):q=d.addObject('Part::Cut',name);q.Base=base;q.Tool=tool;q.Refine=False;return q
    slot=box('WholeStationaryFRSeatWithdrawalPassage',[-83.85,-102.35,103.9,-79.15,-88.65,160.99101615137753])
    for prop,val in [('Length',4),('Width',13),('Height',160.64101615137753-103.9)]:slot.setExpression(prop,f'{val} mm + '+('2*' if prop!='Height' else '')+'OffsetMountParameters.Allowance')
    slot.setExpression('Placement.Base.x','-83.5 mm - OffsetMountParameters.Allowance')
    slot.setExpression('Placement.Base.y','-102 mm - OffsetMountParameters.Allowance')
    side=d.addObject('Part::Cylinder','OffsetCoverM2Axis');side.Height=10
    side.Placement=A.Placement(A.Vector(-88,-102,116),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
    side.setExpression('Radius','.85 mm + OffsetMountParameters.Allowance')
    cover=cut('OffsetCoverFinished',parent,compound('OffsetCoverTools',[slot,side]))
    base=box('OffsetBracketRetainedDeckBase',[-90,-97,109,-78,-88,112])
    wing=box('OffsetBracketBaseWing',[-92,-97,109,-89,-88,112])
    upright=box('OffsetBracketUpright',[-92,-97,112,-84,-94,120])
    joined=d.addObject('Part::MultiFuse','OffsetBracketJoinedStock');joined.Shapes=[base,wing,upright];joined.Refine=False
    bolt=d.addObject('Part::Cylinder','RetainedDeckM2Axis');bolt.Height=5;bolt.Placement.Base=A.Vector(-84,-91,108.5)
    bolt.setExpression('Radius','.85 mm + OffsetMountParameters.Allowance')
    sk=d.addObject('Sketcher::SketchObject','OffsetM2NutAF4p2')
    sk.Placement=A.Placement(A.Vector(-88,-94,116),A.Rotation(A.Vector(1,0,0),90))
    radius=4.2/math.sqrt(3);points=[A.Vector(radius*math.cos(math.radians(30+60*i)),radius*math.sin(math.radians(30+60*i)),0) for i in range(6)]
    import Sketcher
    for i,a in enumerate(points):j=sk.addGeometry(Part.LineSegment(a,points[(i+1)%6]),False);sk.addConstraint(Sketcher.Constraint('Block',j))
    pocket=d.addObject('Part::Extrusion','OffsetM2NutPocket');pocket.Base=sk;pocket.Dir=A.Vector(0,-1.8,0);pocket.Solid=True
    bracket=cut('OffsetBracketFinished',joined,compound('OffsetBracketTools',[bolt,side,pocket]))
    dest=CAD/'OffsetCoverMount.FCStd';exports=[]
    try:
        print('OFFSET_MOUNT_NATIVE_RECOMPUTE',os.getpid(),flush=True);d.recompute();d.saveAs(str(dest))
        states={q.Name:dict(valid=q.Shape.isValid(),solids=len(q.Shape.Solids),BOP=[str(e) for e in q.Shape.check(True) or []]) for q in (cover,bracket)}
        save(OUT/'progress.json',states);assert all(r['valid'] and r['solids']==1 and not r['BOP'] for r in states.values()),states
        assert sk.solve()==0 and sk.FullyConstrained
        ring=Part.makeCylinder(2.5,2.5,A.Vector(-88,-97.5,116),A.Vector(0,-1,0)).cut(Part.makeCylinder(1.21,2.5,A.Vector(-88,-97.5,116),A.Vector(0,-1,0)))
        missing=ring.cut(cover.Shape).Volume;assert missing<1e-5,('NewCoverBearing',missing)
        unchanged=[]
        for x,sideflag in [(-84,1),(106,-1),(106,1)]:
            ringold=Part.makeCylinder(2.5,3.5,A.Vector(x,sideflag*96.5,116),A.Vector(0,sideflag,0)).cut(Part.makeCylinder(1.2,3.5,A.Vector(x,sideflag*96.5,116),A.Vector(0,sideflag,0)))
            loss=parent.Shape.common(ringold).cut(cover.Shape).Volume;assert loss<1e-5;unchanged.append(dict(axis=[x,sideflag*91,116],bearing_loss_mm3=loss))
        overlap=cover.Shape.common(bracket.Shape).Volume;assert overlap<1e-5,overlap
        assert cover.Shape.distToShape(bracket.Shape)[0]<1e-5
        bore_cover=side.Shape.common(cover.Shape).Volume;bore_bracket=side.Shape.common(bracket.Shape).Volume
        assert max(bore_cover,bore_bracket)<1e-5
        nominal=[q.Shape.Volume for q in (cover,bracket)]
        params.Allowance=.45;d.recompute();probe=[q.Shape.Volume for q in (cover,bracket)];assert all(v<n for v,n in zip(probe,nominal))
        params.Allowance=.35;d.recompute();assert all(abs(q.Shape.Volume-v)<1e-5 for q,v in zip((cover,bracket),nominal))
        for tag,q in [('Cover',cover),('Bracket',bracket)]:
            s=q.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            s.exportBrep(str(CAD/(tag+'_WORLD.brep')))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False);assert mesh.isSolid() and mesh.countComponents()==1
            if tag=='Cover':mesh.rotate(math.pi,0,0)
            bb=mesh.BoundBox;dims=[bb.XLength,bb.YLength,bb.ZLength];assert max(dims)<256 and dims[0]+10<256 and dims[1]+10<256
            mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin);mesh.write(str(CAD/(tag+'_UNSELECTED.stl')))
            exports.append(dict(tag=tag,file=dest.relative_to(ROOT).as_posix(),final=q.Name,single_solid=True,strict_BOP_errors=0,closed_STL=True,dimensions_mm=dims,volume_mm3=s.Volume,parameter_mm=[.35,.45,.35]))
        d.save()
    finally:
        for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-offset-cover-') as td:
        tmp=Path(td)
        for fp in [dest]+external:
            target=tmp/fp.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(fp,target)
        re=A.openDocument(str(tmp/dest.relative_to(ROOT)))
        try:
            re.recompute()
            for row in exports:
                s=re.getObject(row['final']).Shape;assert s.isValid() and len(s.Solids)==1 and abs(s.Volume-row['volume_mm3'])<1e-5;row['relocated_reopen']=True
            assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        finally:
            for name in list(A.listDocuments()):A.closeDocument(name)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='COUPLED_OFFSET_COVER_BRACKET_NATIVE_COMPLETE_FULL_SERVICE_OPEN',selected=False,physical_pass=False,W5_complete=False,exports=exports,
        cover_subtractive_by_native_construction=True,cover_parent='hardware/cad/studies/servo-fuse-cover-source-joint-service-r5/Cover_WORLD.brep',cover_parent_sha256=sha(ROOT/'hardware/cad/studies/servo-fuse-cover-source-joint-service-r5/Cover_WORLD.brep'),
        stationary_FR_feature_bounds_mm=sweep,passage_to_cover_bottom=True,front_left_old_axis_mm=[-84,-91,116],front_left_new_axis_mm=[-88,-91,116],unchanged_Deck_screw_axis_mm=[-84,-91,109],
        nominal_Cover_wall_and_Bracket_upright_mm=[3,3],nut_pocket_AF_depth_mm=[4.2,1.8],new_Cover_bearing_missing_mm3=missing,unchanged_Cover_bearings=unchanged,installed_pair_overlap_mm3=overlap,
        fastener_bores_clear_mm3=[bore_cover,bore_bracket],added_installed_parts=0,added_fasteners=0,added_wires=0,one_of_four_brackets_replaced=True,source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=t.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-t).total_seconds()))
    print('OFFSET_MOUNT_NATIVE_COMPLETE',flush=True)

if __name__=='__main__':main()
