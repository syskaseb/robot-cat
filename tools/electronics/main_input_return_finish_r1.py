"""Complete nominal W060: editable Deck and MAIN seats, insulation, stock.

No changes to P0 supports, the circuit or the retained output harness.
Build only in standalone FreeCAD Python; preserve the interactive session.
"""
from datetime import datetime,timezone
import json,math,shutil,sys,tempfile
from pathlib import Path
import main_input_return_r4 as R4
R=R4.M
import body_ground_routes_r1 as M
ROOT=M.ROOT
OUT=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r1'
CAD=ROOT/'hardware/cad/studies/main-input-return-finish-r1'

def main():
    import FreeCAD as A
    import Part,Sketcher,MeshPart
    from open_deck_p0_plate import rect
    from check_main_p0_placement import SavedShapes
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    begin=datetime.now(timezone.utc)
    route_checks=json.loads((R.OUT/'checks.json').read_text(encoding='utf-8'))
    assert route_checks['status']=='NEEDS_DECK_PASSAGE'
    assert {h['owner'] for h in route_checks['hits']}=={'Deck_R38'}
    interface=dict(parent='one-batch-prototype-r39',wire='W060',source='G1.2',destination='MAIN.input_GND',
        route_source=R.OUT.relative_to(ROOT).as_posix(),nominal_blank_mm=220,
        material='Black18AWG0.823mm2 from shared Joy-IT K-1474 offcut, not another cable',
        strip_mm={'G1.2':[12,14],'MAIN':5},bare_neck_above_MAIN_mm=2,
        geometric_radius_mm=6,radius_and_OD_are_project_allowances=True,
        restraints={'SKU':'111-02370','new_installed':3,'prior_working':90,'new_working':93,'shared_bag':100},
        stock={'one_K1474_factory_mm':1000,'selected_Pi_bound_mm':290.24916022252154,
               'black_W060_blank_mm':220,'red_W078_still_unrouted_allowance_mm':150,
               'black_after_Pi_and_return_mm':489.75083977747846,
               'red_after_Pi_and_input_allowance_mm':559.75083977747846,
               'no_double_count':'Cable contains two parallel conductors; do not add red+black against one1m length'},
        new_separate_parts=0,changed_print_jobs=['DeckP10','MAINMount'],
        physical_pass=False,selected=False,W5_complete=False,started_utc=begin.isoformat())
    M.save(OUT/'interface.json',interface)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def sketch(d,n,z):
        s=d.addObject('Sketcher::SketchObject',n);s.AttacherEngine='Engine Plane'
        s.Placement=A.Placement(A.Vector(0,0,z),A.Rotation());return s
    def pad(d,n,s,h):
        p=d.addObject('Part::Extrusion',n);p.Base=s;p.Dir=A.Vector(0,0,h);p.Solid=True;return p
    def cut(d,n,a,b):
        p=d.addObject('Part::Cut',n);p.Base=a;p.Tool=b;p.Refine=False;return p
    def fuse(d,n,objects):
        p=d.addObject('Part::MultiFuse',n);p.Shapes=objects;p.Refine=False;return p
    def cylinder(d,n,x,y,z,r,h,direction=None):
        p=d.addObject('Part::Cylinder',n);p.Radius=r;p.Height=h
        p.Placement=A.Placement(A.Vector(x,y,z),A.Rotation(A.Vector(0,0,1),direction or A.Vector(0,0,1)));return p
    sketches=[];sources={};seats={};exports={};native_checks={}
    def save_reopen(d,dest,final,params,property_name,nominal):
        for s in sketches:
            if s.Document==d:assert s.FullyConstrained and s.solve()==0
        d.recompute([s for s in sketches if s.Document==d]);d.save();d.recompute()
        s=final.Shape.copy();assert s.isValid() and len(s.Solids)==1 and not s.check(True)
        volume=s.Volume;setattr(params,property_name,nominal+.1);d.recompute();probe=final.Shape.Volume
        assert abs(probe-volume)>1e-6
        setattr(params,property_name,nominal);d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        final_name=final.Name;d.save();name=d.Name;A.closeDocument(name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-main-in-') as td:
            q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
            try:
                re.recompute();ss=re.getObject(final_name).Shape
                assert ss.isValid() and len(ss.Solids)==1 and not ss.check(True)
                assert abs(ss.Volume-volume)<1e-5
            finally:A.closeDocument(re.Name)
        return s,dict(volume_mm3=volume,parameter_probe_mm3=[volume,probe,volume],relocated_reopen=True)

    # Deck: a5mm cable passage and two strap passages; supported vertical U
    # pocket admits the cable from +X without pulling solder through a clamp.
    source=ROOT/'hardware/cad/studies/body-ground-bridge-finish-r5/DeckGroundBridgeSupported.FCStd'
    sources[source.relative_to(ROOT).as_posix()]=M.sha(source)
    d=A.openDocument(str(source));docname=d.Name;dest=CAD/'DeckMainInput.FCStd'
    try:
        d.saveAs(str(dest));old=d.GroundSupportedDeck
        p=d.addObject('App::VarSet','MainInputParameters')
        for n,v in [('ExitHeight',6.4),('PortalHeight',8),('GrooveRadius',1.7)]:
            p.addProperty('App::PropertyLength',n);setattr(p,n,v)
        holes=sketch(d,'MainInputPassages',105);sketches.append(holes)
        for x in (75.5,86.5):rect(holes,x-1,13-1.6,2,3.2)
        i=holes.addGeometry(Part.Circle(A.Vector(132.5,0,0),A.Vector(0,0,1),2.5),False)
        for c in [Sketcher.Constraint('Diameter',i,5.),Sketcher.Constraint('DistanceX',i,3,132.5),Sketcher.Constraint('DistanceY',i,3,0.)]:holes.addConstraint(c)
        tool=pad(d,'MainInputPassageTool',holes,4);base=cut(d,'MainInputSlottedDeck',old,tool)
        foot=sketch(d,'G1InputFoot',108.8);sketches.append(foot);rect(foot,77,11.5,8,3)
        raw=pad(d,'G1InputPad',foot,6.4);raw.setExpression('Dir.z','MainInputParameters.ExitHeight')
        groove=cylinder(d,'G1InputGroove',81,11.4,113.5,1.7,3.2,A.Vector(0,1,0));groove.setExpression('Radius','MainInputParameters.GrooveRadius')
        seat=cut(d,'G1InputSeat',raw,groove)
        foot2=sketch(d,'InputPortalFoot',108.8);sketches.append(foot2);rect(foot2,127.5,-3,5.8,6)
        raw2=pad(d,'InputPortalPad',foot2,8);raw2.setExpression('Dir.z','MainInputParameters.PortalHeight')
        groove2=cylinder(d,'InputPortalGroove',132.5,0,108.7,1.7,8.2);groove2.setExpression('Radius','MainInputParameters.GrooveRadius')
        seat2=cut(d,'InputPortalSeat',raw2,groove2)
        final=fuse(d,'MainInputDeck',[base,seat,seat2])
        d.recompute([holes,foot,foot2]);d.save();d.recompute()
        seats['G1_input_seat']=seat.Shape.copy();seats['Deck_input_portal_seat']=seat2.Shape.copy()
        # Portal is open through the entire original plate, not a shallow mark.
        removed=old.Shape.cut(base.Shape).Volume
        assert abs(removed-(2*2*3.2+math.pi*2.5**2)*4)<1e-4,removed
        assert Part.makeCylinder(1.51,20,A.Vector(132.5,0,104.9)).common(final.Shape).Volume<1e-5
        deck,native_checks['Deck']=save_reopen(d,dest,final,p,'PortalHeight',8)
        exports['Deck']=deck
    finally:
        if docname in A.listDocuments():A.closeDocument(docname)

    # MAIN: preserve all mounting holes, PCB axes and old output tongue.
    # A small integral post/beam carries the input above the gap between P0
    # supports; groove tool follows the actual saved input curve, not a guess.
    source=ROOT/'hardware/cad/studies/main-p0-mount/r5/MainP0Mount.FCStd'
    sources[source.relative_to(ROOT).as_posix()]=M.sha(source)
    d=A.openDocument(str(source));docname=d.Name;dest=CAD/'MainInputMount.FCStd'
    try:
        d.saveAs(str(dest));old=d.Adapter
        p=d.addObject('App::VarSet','InputSeatParameters');p.addProperty('App::PropertyLength','PostHeight');p.PostHeight=20
        f=sketch(d,'InputSeatRoot',17);sketches.append(f);rect(f,24.68,-4.16,3.5,3.5)
        post=pad(d,'InputSeatPost',f,20);post.setExpression('Dir.z','InputSeatParameters.PostHeight')
        bf=sketch(d,'InputSeatBeamFoot',31);sketches.append(bf);rect(bf,20.68,-8.16,7.5,6)
        beam=pad(d,'InputSeatBeam',bf,6)
        curve=R.geometry()[-2];tube=Part.Wire([curve]).makePipeShell([Part.Wire([Part.makeCircle(1.7,curve.valueAt(curve.FirstParameter),curve.tangentAt(curve.FirstParameter))])],True,False)
        tube.translate(A.Vector(-105.82,-8.16,-52))
        gt=d.addObject('PartDesign::Feature','InputCurveGrooveTool');gt.Label='Pinned R4 input curve R>=6; groove radius1.7 prototype';gt.Shape=tube
        raw=fuse(d,'InputRawSeat',[post,beam]);seat=cut(d,'InputMainSeat',raw,gt)
        final=fuse(d,'MainInputAdapter',[old,seat])
        d.recompute([f,bf]);d.save();d.recompute();s=seat.Shape.copy();s.translate(A.Vector(105.82,8.16,52));seats['MAIN_input_seat']=s
        mount,native_checks['MAIN']=save_reopen(d,dest,final,p,'PostHeight',20)
        exports['MAIN']=mount
    finally:
        if docname in A.listDocuments():A.closeDocument(docname)
    mount_world=mount.copy();mount_world.translate(A.Vector(105.82,8.16,52))
    # Three conventional T18I envelopes: G1 strap through Deck; portal strap
    # around its vertical post; MAIN strap around the raised input beam.
    bands={}
    bb=[box([x-.6,11.75,103.8,x+.6,14.25,116.4]) for x in (75.5,86.5)]
    bb += [box([74.9,11.75,115.2,87.1,14.25,116.4]),box([74.9,11.75,103.8,87.1,14.25,105]),box([85.5,10.5,100.1,91.5,15.5,104.1])]
    for i,s in enumerate(bb):bands[f'G1_input_tie_{i}']=s
    portal=[box([126.3,-4.2,111.8,127.5,4.2,114.3]),box([134,-4.2,111.8,135.2,4.2,114.3]),
            box([127.5,-4.2,111.8,134,-3,114.3]),box([127.5,3,111.8,134,4.2,114.3]),box([126.8,4.2,110.3,132.8,9.2,114.3])]
    for i,s in enumerate(portal):bands[f'Deck_input_tie_{i}']=s
    main=[box([129.25,-2.1,81.8,131.75,-.9,91.1]),box([129.25,6,81.8,131.75,7.2,91.1]),
          box([129.25,-.9,81.8,131.75,6,83]),box([129.25,-.9,89.9,131.75,6,91.1]),box([127.5,7.2,88.9,133.5,12.2,92.9])]
    for i,s in enumerate(main):bands[f'MAIN_input_tie_{i}']=s
    wires={}
    for f in sorted(R.OUT.glob('W060_*_DESIGN.brep')):
        s=Part.Shape();s.read(str(f));wires[f.stem]=s
    # Two-millimetre bare neck is individually sleeved; full3mm allowance on
    # the already insulated remainder is preserved. 15mm RNF1003/16 boot
    # overlaps at least6mm intact insulation, formed OFF the PETG mount.
    edges=R.geometry();neck=edges[-1]
    inner=Part.Wire([neck]).makePipeShell([Part.Wire([Part.makeCircle(1.1,neck.valueAt(neck.FirstParameter),neck.tangentAt(neck.FirstParameter))])],True,False)
    # The outer boot follows only the last8mm of the insulated fan plus the
    #2mm neck. Nominal4.2mm OD reserve; source exact sleeve SKU follows below.
    curve=edges[-2];parameter=curve.getParameterByLength(curve.Length-6.01)
    tail=curve.Curve.toShape(parameter,curve.LastParameter)
    boot_path=Part.Wire([tail,neck]);boot=boot_path.makePipeShell([Part.Wire([Part.makeCircle(2.1,tail.valueAt(tail.FirstParameter),tail.tangentAt(tail.FirstParameter))])],True,False)
    # Measure actual path overlap, not assuming the parameter fraction is
    # arc length. The boot is a placement envelope, not shrink-material solid.
    assert tail.Length>=6,tail.Length
    sleeves={'W060_neck_inner':inner,'W060_input_outer_boot':boot}
    owners,hashes=R.current_owners();owners.pop('Deck_R38');owners.pop('MAIN/Adapter')
    rows=[]
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,v in enumerate(t.Solids):
                if q.BoundBox.intersect(v.BoundBox):rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(v).Volume))
    for n,s in {**seats,**bands,**wires,**sleeves}.items():
        for m,t in owners.items():
            if n.startswith('W060_') and m=='MAIN/SupplierFamilyReference' and ('boot' in n or 'inner' in n or n==f'W060_{len(edges)-1}_DESIGN'):continue
            check(n,s,m,t)
    for n,s in {**wires,**sleeves,**bands}.items():
        check(n,s,'NewDeck',deck);check(n,s,'NewMAINMount',mount_world)
    for n,s in {**seats,**bands}.items():
        for m,t in wires.items():check(n,s,m,t)
        for m,t in sleeves.items():check(n,s,m,t)
    hits=[r for r in rows if r['hit_mm3']>1e-5]
    for n,s in {**seats,**bands,**sleeves,'Deck':deck,'MAINMount':mount_world}.items():s.exportBrep(str(CAD/(n+'_WORLD.brep')))
    end=datetime.now(timezone.utc)
    result=dict(status='REJECTED' if hits else 'W060_COMPLETE_NOMINAL',hits=hits,rows=rows,native_checks=native_checks,
        new_print_jobs=0,replaced_print_jobs=2,route_length_mm=route_checks['length_mm'],nominal_blank_mm=220,
        outer_boot_intact_overlap_mm=tail.Length,source_sha256={**hashes,**sources},source_script_sha256=M.sha(Path(__file__)),
        physical_pass=False,W5_complete=False,started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds())
    if not hits:
        dims={}
        for n,s in exports.items():
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
            dims[n]=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength];assert max(dims[n])+10<=256
            mesh.write(str(CAD/(n+'_x1.stl')))
        result['dimensions_mm']=dims
    M.save(OUT/'checks.json',result)
    interface.update(status=result['status'],restraints_complete=not hits,new_STL=2 if not hits else 0)
    M.save(OUT/'interface.json',interface)
    preview=[]
    for n,s in {**seats,**bands,**wires,**sleeves,'Deck':deck,'MAINMount':mount_world}.items():
        vs,ts=s.tessellate(.4);preview.append(dict(name=n,vertices=[list(v) for v in vs],triangles=ts))
    M.save(OUT/'preview-geometry.json',preview)
    print(json.dumps(dict(status=result['status'],hits=hits,pairs=len(rows))),flush=True)

if __name__=='__main__':
    sys.path.insert(0,str(ROOT/'tools/cad'));main()
