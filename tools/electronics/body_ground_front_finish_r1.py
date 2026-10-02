"""Editable R40 Deck replacement for the complete W036 interface only."""
from datetime import datetime,timezone
import json,sys,shutil,tempfile
from pathlib import Path
import body_ground_front_shared_r5 as R
M=R.M;ROOT=R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/body-ground-front-finish-r1'
CAD=ROOT/'hardware/cad/studies/body-ground-front-finish-r1'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True)
    assert not (OUT/'checks.json').exists()
    started=datetime.now(timezone.utc)
    trial=json.loads((R.OUT/'checks.json').read_text(encoding='utf-8'))
    assert trial['status']=='CLEAR_FOR_NATIVE_FINISH' and not trial['hits']
    intent=json.loads((R.OUT/'intent.json').read_text(encoding='utf-8'))
    dest=CAD/'DeckFrontGround.FCStd'
    intent.update(status='SAVED_BEFORE_NATIVE',native=dest.relative_to(ROOT).as_posix(),
        route_source=R.OUT.relative_to(ROOT).as_posix(),net_extra_ties=3,
        assembly=['Battery disconnected. Before populated electronics, thread five T18I restraints: three independent G1 cradles (W061/W036/W060), FR end and elevated middle. Replace the two original G1 ties; retain W061 G2/middle and W060 portal/MAIN ties.',
          'Keep G1 mouths and graph unchanged: +X [.1,.5,.3,.4,.2]. BAT at51 and W025 at66 remain reserved. Use one untinned conductor per cage.',
          'Cut one provisional W036 blank from the shared TKD2500125 stock. Strip G1.4 according to delivered221-61512-14mm marking, FR_G.1 according to delivered221-41511mm. Extra blank is trim allowance, not strip length.',
          'Form all bends with at least R21. Seat only intact insulation. Keep the crossing below XA02 and the horizontal run in front of capped fuses at Y62.5/Z124.5. Tighten each G1 wire independently by hand; do not crush silicone.',
          'Disconnect battery before servicing any covered fuse. Release upper Carrier as prescribed, cut/replace interfering wire ties, release the affected WAGO ends and lift the wire before pulling a fuse. Never pull a fuse through the installed harness.'],
        physical_conditions=['Prototype head reserve6x5x4mm is not manufacturer measured. Confirm actual T18I wrap/head and individual grip after delivery; centred underside heads must not enter a neighbour loop.',
          'Wire OD4.2 and static R21 are sourced TKD values. Nominal small clearance to XA03/fuse cap edges must be maintained by the selected supports. No qualification of moving leg harness.',
          'G1 W060 retained electrical route and provisional OD3mm allowance; actual cable OD and sleeve contact condition from R40 remain phase2.'],
        physical_pass=False,W5_complete=False,selected=False,started_utc=started.isoformat())
    M.save(OUT/'interface.json',intent)
    d=A.openDocument(str(R.SOURCE));name=d.Name
    feet=[];native_seats={};slot_boxes=[]
    try:
        d.saveAs(str(dest))
        # Keep historical features, but exclude only the two superseded seats.
        d.GroundSupportedDeck.Shapes=[o for o in d.GroundSupportedDeck.Shapes if o.Name!='GroundSeat0']
        d.MainInputDeck.Shapes=[o for o in d.MainInputDeck.Shapes if o.Name!='G1InputSeat']
        p=d.addObject('App::VarSet','FrontGroundParameters')
        for n,v in [('G1SeatHeight',3.2),('G1GrooveRadius',2.3),('G1SmallGrooveRadius',1.8),('FRSeatHeight',5.4),('MiddlePostHeight',17.2),('MiddleBeamHeight',5.9)]:
            p.addProperty('App::PropertyLength',n);setattr(p,n,v)
        def sketch(n,z,rects):
            q=d.addObject('Sketcher::SketchObject',n);q.AttacherEngine='Engine Plane'
            q.Placement=A.Placement(A.Vector(0,0,z),A.Rotation())
            for x,y,w,h in rects:rect(q,x,y,w,h)
            assert q.FullyConstrained and q.solve()==0
            feet.append(q);return q
        def pad(n,foot,h,expression=None):
            q=d.addObject('Part::Extrusion',n);q.Base=foot;q.Dir=A.Vector(0,0,h);q.Solid=True
            if expression:q.setExpression('Dir.z','FrontGroundParameters.'+expression)
            return q
        def groove(n,x,y,z,r,h,direction,expression):
            q=d.addObject('Part::Cylinder',n);q.Radius=r;q.Height=h
            q.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),A.Vector(*direction)))
            q.setExpression('Radius','FrontGroundParameters.'+expression);return q
        def cut(n,base,tool):
            q=d.addObject('Part::Cut',n);q.Base=base;q.Tool=tool;q.Refine=False;return q
        # The adjacent76.5/78 slots intentionally form one wide opening; no0.1mm ligament.
        slots=[(55.5,12.5,1.6,3.2),(61.5,12.5,1.6,3.2),(70.5,12.5,1.6,3.2),(77.25,12.5,3.1,3.2),(84,12.5,1.6,3.2),(-52,-28.75,2,3.2),(-41,-28.75,2,3.2)]
        slotfoot=sketch('FrontGroundDeckSlots',104.9,[(x-w/2,y-h/2,w,h) for x,y,w,h in slots])
        tool=pad('FrontGroundDeckThroughTool',slotfoot,4.2)
        base=cut('FrontGroundSlottedDeck',d.MainInputDeck,tool)
        for wire,x,r,odr in R.G1:
            foot=sketch('Front_'+wire+'_Foot',108.8,[(x-2.2,11.5,4.4,2.5)])
            raw=pad('Front_'+wire+'_Pad',foot,3.2,'G1SeatHeight')
            gro=groove('Front_'+wire+'_Groove',x,11.4,113.5,r,2.7,(0,1,0),'G1SmallGrooveRadius' if wire=='W060' else 'G1GrooveRadius')
            native_seats['G1_'+wire+'_seat']=cut('Front_'+wire+'_Seat',raw,gro)
        foot=sketch('FrontFRFoot',108.8,[(-50.5,-30,8,2.5)])
        raw=pad('FrontFRPad',foot,5.4,'FRSeatHeight')
        gro=groove('FrontFRGroove',-46.5,-30.1,113.5,2.3,2.7,(0,1,0),'G1GrooveRadius')
        native_seats['FR_seat']=cut('FrontFRSeat',raw,gro)
        foot=sketch('FrontMiddlePostFoot',108.8,[(-9,50.5,4,4)])
        post=pad('FrontMiddlePost',foot,17.2,'MiddlePostHeight')
        foot=sketch('FrontMiddleBeamFoot',120.1,[(-11,50.5,8,23)])
        beam=pad('FrontMiddleBeam',foot,5.9,'MiddleBeamHeight')
        mslots=sketch('FrontMiddleSlots',120,[(-8.6,56,3.2,2),(-8.6,67,3.2,2)])
        mtool=pad('FrontMiddleThroughTool',mslots,6.1)
        beam=cut('FrontMiddleSlottedBeam',beam,mtool)
        raw=d.addObject('Part::MultiFuse','FrontMiddleRaw');raw.Shapes=[post,beam];raw.Refine=False
        gro=groove('FrontMiddleGroove',-11.1,62.5,124.5,2.3,8.2,(1,0,0),'G1GrooveRadius')
        native_seats['Middle_seat']=cut('FrontMiddleSeat',raw,gro)
        final=d.addObject('Part::MultiFuse','FrontGroundDeck');final.Shapes=[base]+list(native_seats.values());final.Refine=False
        d.recompute(feet);d.save();d.recompute();s=final.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        nominal=s.Volume;p.G1SeatHeight=3.3;d.recompute();probe=final.Shape.Volume
        assert abs(probe-nominal)>1e-5
        p.G1SeatHeight=3.2;d.recompute();assert abs(final.Shape.Volume-nominal)<1e-5
        for x,y,w,h in slots:
            q=Part.makeBox(w-.02,h-.02,4.2,A.Vector(x-w/2+.01,y-h/2+.01,104.9))
            assert q.common(s).Volume<1e-5,(x,y)
        for y in (57,68):
            assert Part.makeBox(3.18,1.98,6.1,A.Vector(-8.59,y-.99,120)).common(s).Volume<1e-5
        for n,obj in native_seats.items():
            obj.Shape.exportBrep(str(CAD/(n+'_WORLD.brep')))
        d.save();s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-front-ground-') as td:
        tmp=Path(td)/dest.name;shutil.copy2(dest,tmp);d=A.openDocument(str(tmp));name=d.Name
        try:
            d.recompute();s=d.FrontGroundDeck.Shape.copy()
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-nominal)<1e-5
        finally:A.closeDocument(name)
    print('Native saved, parameter changed/restored, relocated reopen complete.',flush=True)
    owners,hashes=R.P.current_owners();owners.pop('Deck_R40')
    seats,bands=R.design_shapes();pieces={}
    for f in R.OUT.glob('W036_*_DESIGN.brep'):
        q=Part.Shape();q.read(str(f));pieces[f.stem]=q;hashes[f.relative_to(ROOT).as_posix()]=M.sha(f)
    rows=[]
    def check(n,a,m,b):
        for i,q in enumerate(a.Solids):
            for j,v in enumerate(b.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,q in {**pieces,**seats,**bands}.items():
        for m,v in owners.items():check(n,q,m,v)
    for n,q in {**pieces,**bands}.items():check(n,q,'NativeDeck',s)
    for n,q in bands.items():
        for m,v in pieces.items():check(n,q,m,v)
    # Distinct loops must not occupy one another, but pieces within one loop meet.
    items=list(bands.items())
    for i,(n,q) in enumerate(items):
        for m,v in items[i+1:]:
            if n.rsplit('_',1)[0]!=m.rsplit('_',1)[0]:check(n,q,m,v)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    result=dict(status='REJECTED' if hits else 'W036_NATIVE_COMPLETE',hits=hits,rows=rows,
        parameter_probe_volumes_mm3=[nominal,probe,nominal],fully_constrained_added_sketches=len(feet),
        native_saved_before_recompute=True,relocated_reopen=True,strict_BOP_errors=0,
        native=dest.relative_to(ROOT).as_posix(),deck_slots=slots,middle_slots=[57,68],
        trough_floor_mm={'G1_large':2.4,'G1_small':2.9,'FR':2.4,'middle':2.1},
        route_length_mm=trial['route_length_mm'],nominal_blank_mm=trial['nominal_blank_mm'],
        source_sha256={**hashes,R.SOURCE.relative_to(ROOT).as_posix():M.sha(R.SOURCE),(R.OUT/'checks.json').relative_to(ROOT).as_posix():M.sha(R.OUT/'checks.json')},
        script_sha256=M.sha(Path(__file__)),new_print_jobs=0,net_extra_ties=3,W5_complete=False,physical_pass=False,mesh_export_complete=False)
    M.save(OUT/'checks.json',result)
    if not hits:
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
        assert dims[0]+10<=256 and dims[1]+10<=256 and dims[2]<=256
        mesh.write(str(CAD/'Deck_x1.stl'));result.update(mesh_export_complete=True,closed=True,components=1,dimensions_mm=dims)
    end=datetime.now(timezone.utc);result.update(worker_started_utc=started.isoformat(),worker_finished_utc=end.isoformat(),worker_wall_seconds=(end-started).total_seconds())
    M.save(OUT/'checks.json',result)
    intent.update(status=result['status'],restraints_complete=not hits,native_export=result['mesh_export_complete'],route_length_mm=trial['route_length_mm'],nominal_blank_mm=trial['nominal_blank_mm'])
    M.save(OUT/'interface.json',intent)
    geo=[]
    for n,q in {'Deck':s,**seats,**bands}.items():
        vs,ts=q.tessellate(.5);geo.append(dict(name=n,vertices=[list(v) for v in vs],triangles=ts))
    M.save(OUT/'preview-geometry.json',dict(shapes=geo,route=json.loads((R.OUT/'preview-lines.json').read_text(encoding='utf-8'))))
    print(json.dumps(dict(status=result['status'],hits=hits,pairs=len(rows),export=result['mesh_export_complete'])),flush=True)

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'));main()
