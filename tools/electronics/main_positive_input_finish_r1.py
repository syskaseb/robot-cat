"""Finish W043/F_PI mount first; retained R2 full output stays unselected.

No pretend full W5: W077/W078 need two-end splice retention, Deck descent
and MAIN insulation separation. This source-side subassembly is independently
useful and corrects the impossible old <=50mm prefuse requirement.
"""
from datetime import datetime, timezone
from pathlib import Path
import json,sys,shutil,tempfile
import main_positive_input_route_r2 as R2
R=R2.R;M=R.M;ROOT=R.ROOT
OUT=ROOT/'hardware/electronics/full-cat/main-positive-source-finish-r1'
CAD=ROOT/'hardware/cad/studies/main-positive-source-finish-r1'
SOURCE=ROOT/'hardware/cad/studies/g1-exit-restraints-finish-r1/DeckG1ExitRestraints.FCStd'

def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    owners,hashes=R.C.current_owners();deck=owners.pop('Deck_R41')
    holder=box(R.HOLDER)
    bands={f'F_PI_source_tie_{i}':s for i,s in enumerate([
        box([-76.2,-26.25,103.8,-75,-22.75,133.4]),
        box([-20,-26.25,103.8,-18.8,-22.75,133.4]),
        box([-75,-26.25,132.2,-20,-22.75,133.4]),
        box([-75,-26.25,103.8,-20,-22.75,105]),
        box([-51.5,-28.5,98.8,-42.5,-20.5,103.8])])}
    slots=[[-76.2,-26.6,104.9,2,4.2,4.2],[-20,-26.6,104.9,2,4.2,4.2]]
    projected=deck.copy()
    for x,y,z,w,l,h in slots:projected=projected.cut(Part.makeBox(w,l,h,A.Vector(x,y,z)))
    wires={}
    for p in (R.OUT).glob('W043_*_DESIGN.brep'):
        s=Part.Shape();s.read(str(p));wires[p.stem]=s
    assert len(wires)==3
    rows=[]
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,v in enumerate(t.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,s in {**bands,**wires,'F_PI_holder':holder}.items():
        for m,t in owners.items():check(n,s,m,t)
        if n!='F_PI_holder':check(n,s,'ChangedDeck',projected)
    for n,s in wires.items():
        for m,t in bands.items():check(n,s,m,t)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    M.save(OUT/'checks.json',dict(status='REJECTED' if hits else 'SOURCE_READY_FOR_NATIVE',hits=hits,rows=rows,
        source_sha256=hashes,physical_pass=False,W5_complete=False,output_selected=False,
        started_utc=begin.isoformat(),native_export_complete=False))
    assert not hits,hits
    iface=dict(parent='one-batch-prototype-r41',selected=False,physical_pass=False,W5_complete=False,
        status='SOURCE_READY_FOR_NATIVE',circuits=['W043/P_SYS.2->F_PI.in'],
        holder_SKU='FHAC0001ZXJ',fuse_SKU='0287003.PXCN',holder_bbox_mm=R.HOLDER,
        P_SYS_labels_plus_X=['.2','.1','.3','.4','.5'],P_SYS_cage_X_mm=[-84,-76.5,-69,-61.5,-54],
        graph_unchanged=True,W043_route_mm=17.676386669828,W043_factory_blank_mm=40,
        factory_minimum_mm=84.5,strip_P_SYS_mm=[12,14],do_not_tin_WAGO=True,
        source_OD_mm=3.4,OD_and_R6_are_prototype_allowances=True,closed_height_22mm_is_project_allowance=True,
        restraints=dict(holder_large_ties=1,holder_large_SKU='111-03410',old_small_holder_ties_removed=2,
            small_working_before=93,small_working_after=91,small_bag=100,large_package=100,
            large_loop_bound_mm=177.4,large_usable_minimum_mm=190,
            closed_cover_tie_rule='One longitudinal band offsetY-24.5, ends below Deck, head under own holder. Cut/replace before opening cap; never energize for fuse service.'),
        source_retention='Fixed WAGO cage and factory moulded boot bound the short17.68mm insulated bridge; no free solder joint or moving mechanism on this segment. Leave the curved bridge unstressed, not pulled straight.',
        output_status='W077/W078 R2 is NOT selected. Needs splice restraint, new Deck passage and MAIN sleeve separation; its inherited metadata mistakenly lists unused old Bezier bounds. Use exact R10/R6 arcs and saved R2 centreline for subsequent work.',
        assembly=['Battery disconnected. Before populated Deck, prethread one111-03410 through the two new full passages, head underneath, offsetY-24.5.',
            'Fit closed F_PI in the new x-73..-22/Y-21 site. Old x43/Y-58.5 tie holes remain unused. Verify delivered closed height and lid travel after cutting tie.',
            'Prepare40mm source factory lead only after dry fit: remove factory bare tip, strip12..14mm per delivered221-615 marking; one untinned16AWG conductor in physical firstX cage labelledP_SYS.2.',
            'Keep the17.68mm curved insulated route and moulded boot free of tension. WAGO label.1 moves to secondX cage; other electrical roles do not change. Do not connect battery.',
            'Output factory wire and red MAIN lead remain unselected until their complete insulation and strain-relief interface is finished. No whole Pi branch or W5 completion here.'],
        phase2=['Delivered lead OD/radius, cage faces/strip marking, closed-cap fit and strap tightening; replace local cradle/lead if needed.',
                'E3 source/branch protection and electrical checks remain required before powering.'])
    M.save(OUT/'interface.json',iface)
    dest=CAD/'DeckMainPositiveSource.FCStd';d=A.openDocument(str(SOURCE));name=d.Name
    try:
        d.saveAs(str(dest));p=d.addObject('App::VarSet','PositiveSourceParameters')
        p.addProperty('App::PropertyLength','SlotWidth');p.SlotWidth=2
        sk=d.addObject('Sketcher::SketchObject','PositiveSourceSlots');sk.AttacherEngine='Engine Plane';sk.Placement=A.Placement(A.Vector(0,0,104.9),A.Rotation())
        # Native rectangle dimensions remain editable. SlotWidth drives extrusion
        # height via separate named ThroughDepth, tested on material removal.
        for x,y,z,w,l,h in slots:rect(sk,x,y,w,l)
        assert sk.FullyConstrained and sk.solve()==0
        p.addProperty('App::PropertyLength','ThroughDepth');p.ThroughDepth=4.2
        tool=d.addObject('Part::Extrusion','PositiveSourceSlotTool');tool.Base=sk;tool.Dir=A.Vector(0,0,4.2);tool.Solid=True;tool.setExpression('Dir.z','PositiveSourceParameters.ThroughDepth')
        final=d.addObject('Part::Cut','PositiveSourceDeck');final.Base=d.G1ExitDeck;final.Tool=tool;final.Refine=False
        d.recompute([sk]);d.save();d.recompute();s=final.Shape.copy()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        volume=s.Volume
        # ThroughDepth above plate is saturated, so use reduced3.5mm to prove
        # actual bottom material responds, then restore full4.2mm passage.
        p.ThroughDepth=3.5;d.recompute();probe=final.Shape.Volume;assert probe>volume
        p.ThroughDepth=4.2;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        for x,y,z,w,l,h in slots:assert Part.makeBox(w-.02,l-.02,h,A.Vector(x+.01,y+.01,z)).common(final.Shape).Volume<1e-5
        d.save();s.exportBrep(str(CAD/'Deck_WORLD.brep'))
    finally:A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-fpi-source-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);d=A.openDocument(str(q));name=d.Name
        try:
            d.recompute();actual=d.PositiveSourceDeck.Shape
            assert actual.isValid() and len(actual.Solids)==1 and not actual.check(True) and abs(actual.Volume-volume)<1e-5
        finally:A.closeDocument(name)
    mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin);dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
    assert dims[0]+10<=256 and dims[1]+10<=256 and dims[2]<=256
    mesh.write(str(CAD/'Deck_x1.stl'))
    for n,s in bands.items():s.exportBrep(str(CAD/(n+'_WORLD.brep')))
    end=datetime.now(timezone.utc)
    c=json.loads((OUT/'checks.json').read_text(encoding='utf-8'));c.update(status='F_PI_SOURCE_FINISHED_NOT_WHOLE_BRANCH',
        native_export_complete=True,native=dest.relative_to(ROOT).as_posix(),strict_BOP_errors=0,
        parameter_probe_volumes_mm3=[volume,probe,volume],relocated_reopen=True,closed=True,components=1,dimensions_mm=dims,
        script_sha256=M.sha(Path(__file__)),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds(),
        source_sha256={**hashes,SOURCE.relative_to(ROOT).as_posix():M.sha(SOURCE)},source_side_complete=True)
    M.save(OUT/'checks.json',c);iface.update(status=c['status'],native_export_complete=True);M.save(OUT/'interface.json',iface)
    geo=[]
    shapes={'Deck':s,'F_PI_closed_reserve':holder,**wires,**bands}
    for n,s in shapes.items():
        vs,ts=s.tessellate(.5);geo.append(dict(name=n,vertices=[list(v) for v in vs],triangles=ts))
    M.save(OUT/'preview-geometry.json',geo)
    print(json.dumps(dict(status=c['status'],pairs=len(rows),dimensions_mm=dims,wall_seconds=c['worker_wall_seconds'])),flush=True)

if __name__=='__main__':main()
