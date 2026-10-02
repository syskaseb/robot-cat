"""Replace only two crowded G1 cradles, retaining W060/W061 selected routes."""
from datetime import datetime,timezone
import json,sys,shutil,tempfile
from pathlib import Path
import body_ground_front_shared_r5 as R
M=R.M;ROOT=R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/g1-exit-restraints-finish-r1'
CAD=ROOT/'hardware/cad/studies/g1-exit-restraints-finish-r1'

def selected_shapes():
    seats,bands=R.design_shapes()
    return ({n:s for n,s in seats.items() if n in ('G1_W061_seat','G1_W060_seat')},
        {n:s for n,s in bands.items() if n.startswith(('G1_W061_tie_','G1_W060_tie_'))})

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    started=datetime.now(timezone.utc);dest=CAD/'DeckG1ExitRestraints.FCStd'
    iface=dict(status='SAVED_BEFORE_NATIVE',parent='one-batch-prototype-r40',native=dest.relative_to(ROOT).as_posix(),
        affected_routes=['W061/G1.5','W060/G1.2'],unchanged_electrical_endpoints=True,
        G1_labels_plus_X=['.1','.5','.3','.4','.2'],G1_cage_X_mm=[51,58.5,66,73.5,81],
        replaced_restraints=['W061/G1_end','W060/G1_input'],retained_restraints=['W061/G2_end','W061/Middle','W060/Deck_input','W060/MAIN_input'],
        pending_G1_routes=['BAT/G1.1','W025/G1.3','W036/G1.4'],new_routes_selected=[],
        ties=dict(SKU='111-02370',replaces=2,selected=2,net_added=0,bag=100,working_total=93,
            band_width_mm=2.5,band_thickness_mm=1.2,head_prototype_reserve_mm=[6,5,4]),
        cradles=[dict(wire='W061',x=58.5,radius_mm=2.3,prototype_OD_mm=4.2),dict(wire='W060',x=81,radius_mm=1.8,prototype_OD_mm=3)],
        strap_side_offsets_mm=[-3,3],strap_head_location='centred under each own Deck loop; not beside neighbouring cage',
        assembly=['Disconnect battery. Before populated electronics, prethread two T18I ties through the four new full Deck passages; heads centred underneath the corresponding wire cradle.',
          'Reinstall the same W061 and W060 wires in their unchanged G1.5/X58.5 and G1.2/X81 cages. Retain wire lengths, stripping and routes from R38/R40. Never tin WAGO conductor ends.',
          'Seat intact insulation in the two independent shallow cradles and tighten each tie by hand without crushing the cable. Confirm grip and actual head clearances after delivery.',
          'Do not thread these ties through the old wider passage pairs. Those unused historical openings are retained; they are not additional restraints.',
          'For removal, disconnect battery first, cut and replace only the affected tie and release its own G1 wire. Other G1 cages and retained supports are unchanged.'],
        conditions=['Cage centres and W060 OD remain provisional datums. Narrow strap reserves free neighbouring mouth exit stubs, not their full future cable routes.',
          'Two separate straps retain different cable diameters; no mixed-diameter common cap/clamp.',
          'R40 sleeve-to-Pi cable soft-contact condition remains OPEN. This stage does not certify whole assembly collision freedom.',
          'W036 R3/R4/R5 rejected corridors are NOT selected. W5 and stock/tool/assembly completion remain OPEN.'],
        source_start_utc=started.isoformat(),W5_complete=False,physical_pass=False,selected=False)
    M.save(OUT/'interface.json',iface)
    d=A.openDocument(str(R.SOURCE));name=d.Name;feet=[];ns={}
    slots=[(55.5,12.5,1.6,3.2),(61.5,12.5,1.6,3.2),(78,12.5,1.6,3.2),(84,12.5,1.6,3.2)]
    try:
        d.saveAs(str(dest))
        assert d.GroundSeat0 in d.GroundSupportedDeck.Shapes
        assert d.G1InputSeat in d.MainInputDeck.Shapes
        d.GroundSupportedDeck.Shapes=[o for o in d.GroundSupportedDeck.Shapes if o.Name!='GroundSeat0']
        d.MainInputDeck.Shapes=[o for o in d.MainInputDeck.Shapes if o.Name!='G1InputSeat']
        p=d.addObject('App::VarSet','G1ExitParameters')
        for n,v in [('SeatHeight',3.2),('LargeGrooveRadius',2.3),('SmallGrooveRadius',1.8)]:
            p.addProperty('App::PropertyLength',n);setattr(p,n,v)
        def foot(n,z,rects):
            q=d.addObject('Sketcher::SketchObject',n);q.AttacherEngine='Engine Plane';q.Placement=A.Placement(A.Vector(0,0,z),A.Rotation())
            for x,y,w,h in rects:rect(q,x,y,w,h)
            assert q.FullyConstrained and q.solve()==0;feet.append(q);return q
        def extrude(n,f,h,expr=None):
            q=d.addObject('Part::Extrusion',n);q.Base=f;q.Dir=A.Vector(0,0,h);q.Solid=True
            if expr:q.setExpression('Dir.z','G1ExitParameters.'+expr)
            return q
        f=foot('G1ExitThroughSlots',104.9,[(x-w/2,y-h/2,w,h) for x,y,w,h in slots])
        tool=extrude('G1ExitThroughTool',f,4.2)
        base=d.addObject('Part::Cut','G1ExitSlottedDeck');base.Base=d.MainInputDeck;base.Tool=tool;base.Refine=False
        for wire,x,r in [('W061',58.5,2.3),('W060',81,1.8)]:
            f=foot('G1Exit'+wire+'Foot',108.8,[(x-2.2,11.5,4.4,2.5)])
            pad=extrude('G1Exit'+wire+'Pad',f,3.2,'SeatHeight')
            gro=d.addObject('Part::Cylinder','G1Exit'+wire+'Groove');gro.Radius=r;gro.Height=2.7
            gro.Placement=A.Placement(A.Vector(x,11.4,113.5),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
            gro.setExpression('Radius','G1ExitParameters.'+('LargeGrooveRadius' if wire=='W061' else 'SmallGrooveRadius'))
            seat=d.addObject('Part::Cut','G1Exit'+wire+'Seat');seat.Base=pad;seat.Tool=gro;seat.Refine=False
            ns['G1_'+wire+'_seat']=seat
        final=d.addObject('Part::MultiFuse','G1ExitDeck');final.Shapes=[base]+list(ns.values());final.Refine=False
        d.recompute(feet);d.save();d.recompute();s=final.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        volume=s.Volume;p.SeatHeight=3.3;d.recompute();probe=final.Shape.Volume;assert abs(probe-volume)>1e-5
        p.SeatHeight=3.2;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        for x,y,w,h in slots:
            assert Part.makeBox(w-.02,h-.02,4.2,A.Vector(x-w/2+.01,y-h/2+.01,104.9)).common(s).Volume<1e-5
        for n,obj in ns.items():obj.Shape.exportBrep(str(CAD/(n+'_WORLD.brep')))
        d.save();s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-G1-cradles-') as td:
        tmp=Path(td)/dest.name;shutil.copy2(dest,tmp);d=A.openDocument(str(tmp));name=d.Name
        try:
            d.recompute();s=d.G1ExitDeck.Shape.copy()
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-volume)<1e-5
        finally:A.closeDocument(name)
    print('Native G1 Deck saved/probed/reopened.',flush=True)
    owners,hashes=R.P.current_owners();owners.pop('Deck_R40');seats,bands=selected_shapes();rows=[]
    def check(n,a,m,b):
        for i,q in enumerate(a.Solids):
            for j,v in enumerate(b.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,q in {**seats,**bands}.items():
        for m,v in owners.items():check(n,q,m,v)
    for n,q in bands.items():check(n,q,'NativeDeck',s)
    # Check current wires also against changed Deck, not just new cradles.
    for n,q in owners.items():
        if n.startswith(('W061','W060/','Input/W060')) or 'body-ground-bridge-r5/W061_' in n:check(n,q,'NativeDeck',s)
    items=list(bands.items())
    for i,(n,q) in enumerate(items):
        for m,v in items[i+1:]:
            if n.rsplit('_',1)[0]!=m.rsplit('_',1)[0]:check(n,q,m,v)
    reserves={label:Part.makeCylinder(r,2,A.Vector(x,11,113.5),A.Vector(0,1,0)) for label,x,r in [('BAT_exit_reserved',51,1.55),('W025_exit_reserved',66,2.1),('W036_exit_reserved',73.5,2.1)]}
    for n,q in {**seats,**bands}.items():
        for m,v in reserves.items():check(n,q,m,v)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    c=dict(status='REJECTED' if hits else 'G1_INDEPENDENT_RESTRAINTS_COMPLETE',hits=hits,rows=rows,
        native=dest.relative_to(ROOT).as_posix(),strict_BOP_errors=0,fully_constrained_added_sketches=3,
        parameter_probe_volumes_mm3=[volume,probe,volume],relocated_reopen=True,native_saved_before_recompute=True,
        full_through_slots=slots,finite_open_troughs=True,minimum_floor_mm={'W061':2.4,'W060':2.9},
        replacements_only=['W061/G1_end','W060/G1_input'],net_extra_ties=0,new_routes_selected=[],
        neighbouring_stubs_only=True,whole_assembly_collision_free=False,
        source_sha256={**hashes,R.SOURCE.relative_to(ROOT).as_posix():M.sha(R.SOURCE)},
        script_sha256=M.sha(Path(__file__)),mesh_export_complete=False,new_print_jobs=0,physical_pass=False,W5_complete=False)
    M.save(OUT/'checks.json',c)
    if not hits:
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
        assert dims[0]+10<=256 and dims[1]+10<=256 and dims[2]<=256
        mesh.write(str(CAD/'Deck_x1.stl'));c.update(mesh_export_complete=True,closed=True,components=1,dimensions_mm=dims)
    end=datetime.now(timezone.utc);c.update(worker_started_utc=started.isoformat(),worker_finished_utc=end.isoformat(),worker_wall_seconds=(end-started).total_seconds())
    M.save(OUT/'checks.json',c);iface.update(status=c['status'],native_export=c['mesh_export_complete'],restraints_complete=not hits)
    M.save(OUT/'interface.json',iface)
    geo=[]
    for n,q in {'Deck':s,**seats,**bands}.items():
        vs,ts=q.tessellate(.5);geo.append(dict(name=n,vertices=[list(v) for v in vs],triangles=ts))
    M.save(OUT/'preview-geometry.json',geo)
    print(json.dumps(dict(status=c['status'],hits=hits,pairs=len(rows),export=c['mesh_export_complete'])),flush=True)

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'));main()
