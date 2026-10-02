"""Editable S0 mount and real nominal fastener stacks for the R5 corridor.

Only the linked-family switch casing/flange/stud datums are provisional.
Purchased fastener dimensions are sourced; do not waive unrelated contacts.
No selection, whole-source readiness or physical fit claim.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys,json,math,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
LAYOUT=ROOT/'hardware/electronics/full-cat/source-switch-layout-r6'
OUT=ROOT/'hardware/electronics/full-cat/source-switch-mount-finish-r4'
CAD=ROOT/'hardware/cad/studies/source-switch-mount-finish-r4'


def main():
    import FreeCAD as A
    import Part,MeshPart
    from open_deck_p0_plate import rect
    import main_positive_input_r1 as C
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    layout=json.loads((LAYOUT/'checks.json').read_text(encoding='utf-8'))
    assert not layout['hits'] and not layout['errors']
    assert sha(ROOT/'tools/electronics/source_switch_layout_r6.py')==layout['script_sha256']
    hashes={}
    def load(path):
        path=Path(path);hashes[path.relative_to(ROOT).as_posix()]=sha(path)
        s=Part.Shape();s.read(str(path));return s
    reference=load(LAYOUT/'S0_mount_candidate_DESIGN.brep')
    # Keep originalY92 clear of F_FL2. Offset bolts+8X beyond each4mm
    # half-width post, and extend feet laterally rather than forward.
    for x in (-87.5,-37):
        reference=reference.fuse(Part.makeCylinder(1.2,4,A.Vector(x,92,101)))
        old_post_bore=Part.makeCylinder(1.2,.1,A.Vector(x,92,100.9)).common(
            Part.makeBox(8,2.9,.1,A.Vector(x-4,92,100.9)))
        reference=reference.fuse(old_post_bore)
        reference=reference.fuse(Part.makeBox(18,5.4,4,A.Vector(x-6,89.5,101)))
        reference=reference.cut(Part.makeCylinder(1.2,4.2,A.Vector(x+8,92,100.9)))
    reference=reference.removeSplitter()
    d=A.newDocument('SourceSwitchMount');par=d.addObject('App::VarSet','MountParameters')
    par.addProperty('App::PropertyLength','PanelThickness');par.PanelThickness=3
    sketches=[]
    def block(n,b,along_y=False):
        sk=d.addObject('Sketcher::SketchObject',n+'Profile')
        if along_y:
            sk.Placement=A.Placement(A.Vector(0,b[1],0),A.Rotation(A.Vector(1,0,0),90))
            rect(sk,b[0],b[2],b[3]-b[0],b[5]-b[2]);direction=A.Vector(0,b[4]-b[1],0)
        else:
            sk.Placement.Base.z=b[2];rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1]);direction=A.Vector(0,0,b[5]-b[2])
        sketches.append(sk);f=d.addObject('Part::Extrusion',n);f.Base=sk;f.Dir=direction;f.Solid=True;return f
    def cy(n,p,r,h,axis=(0,0,1)):
        f=d.addObject('Part::Cylinder',n);f.Radius=r;f.Height=h
        f.Placement=A.Placement(A.Vector(*p),A.Rotation(A.Vector(0,0,1),A.Vector(*axis)));return f
    panel=block('Panel',[-91.5,95,6,-33,98,71],True);panel.setExpression('Dir.y','MountParameters.PanelThickness')
    additions=[panel];holes=[cy('NeckBore',[-61.5,94.9,43],12,3.2,(0,1,0))]
    for i,c in enumerate(layout['mount_hole_centres']):holes.append(cy('SwitchBore'+str(i),[c[0],94.9,c[2]],3.25,3.2,(0,1,0)))
    for i,x in enumerate((-87.5,-37)):
        additions += [block('Post'+str(i),[x-4,92,71,x+4,94.9,101]),
            block('Join'+str(i),[x-4,92,69,x+4,98,73]),block('Foot'+str(i),[x-6,89.5,101,x+12,94.9,105])]
        holes.append(cy('DeckBoltBore'+str(i),[x+8,92,100.9],1.2,4.2))
    stock=d.addObject('Part::MultiFuse','MountStock');stock.Shapes=additions;stock.Refine=True
    cutters=d.addObject('Part::MultiFuse','MountBores');cutters.Shapes=holes
    finished=d.addObject('Part::Cut','FinishedMount');finished.Base=stock;finished.Tool=cutters;finished.Refine=True
    d.recompute();shape=finished.Shape.copy()
    assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
    assert abs(shape.Volume-reference.Volume)<1e-5,(shape.Volume,reference.Volume)
    assert shape.cut(reference).Volume+reference.cut(shape).Volume<1e-5
    assert all(s.FullyConstrained and s.solve()==0 for s in sketches)
    volume=shape.Volume;par.PanelThickness=3.1;d.recompute();probe=finished.Shape.Volume
    assert probe>volume;par.PanelThickness=3;d.recompute();assert abs(finished.Shape.Volume-volume)<1e-5
    native=CAD/'SourceSwitchMount.FCStd';d.saveAs(str(native));A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-switch-') as td:
        q=Path(td)/native.name;shutil.copy2(native,q);re=A.openDocument(str(q))
        try:
            re.recompute();assert re.FinishedMount.Shape.isValid()
            assert abs(re.FinishedMount.Shape.Volume-volume)<1e-5
        finally:A.closeDocument(re.Name)
    shape.exportBrep(str(CAD/'Mount_WORLD.brep'))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    # Broad panelY98 face down, keep worldX; maximum thickness/offset is9mm.
    mesh.rotate(math.pi/2,0,0);b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+10<256 and dims[1]+10<256 and dims[2]<256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'Mount_x1.stl'))
    def cyl(p,r,h,axis=(0,1,0)):return Part.makeCylinder(r,h,A.Vector(*p),A.Vector(*axis))
    def ring(p,ro,ri,h):return cyl(p,ro,h).cut(cyl([p[0],p[1]-.1,p[2]],ri,h+.2))
    def hexnut(c,y,af,h,ri):
        rad=af/math.sqrt(3)
        vs=[A.Vector(c[0]+rad*math.cos(k*math.pi/3),y,c[2]+rad*math.sin(k*math.pi/3)) for k in range(6)]
        return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,h,0)).cut(cyl([c[0],y-.1,c[2]],ri,h+.2))
    parts={};tools={}
    for i,c in enumerate(layout['mount_hole_centres']):
        # Switch flangeY98..102 is a replaceable4mm project assumption.
        parts[f'M6x20_{i}']=cyl([c[0],83.6,c[2]],3,20).fuse(cyl([c[0],103.6,c[2]],5,6))
        parts[f'M6washers_{i}']=Part.makeCompound([ring([c[0],y,c[2]],6,3.2,1.6) for y in (93.4,102)])
        parts[f'M6nut_{i}']=hexnut(c,88.4,10,5,3)
        tools[f'M6head_tool_{i}']=cyl([c[0],109.6,c[2]],4,30)
        tools[f'M6nut_tool_{i}']=cyl([c[0],58.4,c[2]],7,30).cut(cyl([c[0],58.3,c[2]],3.3,30.2))
    for i,c in enumerate(layout['stud_centres_provisional']):
        parts[f'M10washer_{i}']=ring([c[0],66.95,c[2]],10,5.25,2)
        parts[f'M10nut_{i}']=hexnut(c,58.95,17,8,5)
        # Model stud only in exposed portion; never make an invented exact case.
        parts[f'M10stud_provisional_{i}']=cyl([c[0],55,c[2]],5,15)
        tools[f'M10nut_tool_{i}']=cyl([c[0],28.95,c[2]],12,30).cut(cyl([c[0],28.85,c[2]],5.3,30.2))
    owners,oldhash=C.current_owners();owners.pop('Deck_R41');owners.pop('MAIN_R40')
    owners['Deck_candidate']=load(LAYOUT/'Deck_candidate_UNSELECTED.brep')
    owners['MAIN_R44']=load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for p in LAYOUT.glob('*_DESIGN.brep'):
        if p.stem.startswith(('W','TE')):owners[p.stem]=load(p)
    owners['SourceBridge']=load(ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2/Bridge_WORLD.brep')
    for n in list(owners):
        if n.startswith(('BatteryCarrier','BatteryLiner','BatteryStrap','BatteryScrew','BatteryNut')):owners.pop(n)
    hits=[];access_contacts=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    v=a.common(b).Volume
                    if v>1e-5:
                        row=dict(part=n,owner=m,hit_mm3=v)
                        if n.startswith('M6nut_tool') and m=='TE130207_IN_DESIGN':
                            row['assembly_condition']='Tighten S0 M6 BEFORE installing ring terminals on the removed Deck.';access_contacts.append(row)
                        elif n.startswith('M10nut_tool') and (m in ('MountFrontL','SideLeft22','FrameScrewFrontL') or m.endswith('BUSBracket_WORLD.brep')):
                            row['assembly_condition']='Attach/crimp rings and tighten M10 on the REMOVED Deck, before P0/BUS enclosure installation.';access_contacts.append(row)
                        else:hits.append(row)
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in {**parts,**tools}.items():
        for m,t in owners.items():check(n,s,m,t)
        check(n,s,'Mount',shape)
        for m,t in parts.items():
            # Only own coaxial stud/nut/washer thread interface is intentional.
            if n[-1:]==m[-1:] and n.startswith('M10') and m.startswith('M10'):continue
            if n==m:continue
            check(n,s,m,t)
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    for m,t in owners.items():check('NativeMount',shape,m,t)
    # Saved selected lower guards are already C owners. Record their bounds
    # to distinguish an external key from an unperformed shell aperture cut.
    shell_bounds={n:[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]
        for n,s in owners.items() if n.startswith(('Side','Belly','View_upper','View_lower'))}
    end=datetime.now(timezone.utc)
    report=dict(status='REJECTED_FASTENER_STACK' if hits or errors else 'NATIVE_MOUNT_NOMINAL_FASTENERS_WITH_BENCH_ASSEMBLY_CONDITION',
        hits=hits,tool_access_contacts=access_contacts,errors=errors,pairs=pairs,selected=False,physical_pass=False,W5_complete=False,
        native=dict(path=native.relative_to(ROOT).as_posix(),fully_constrained_sketches=len(sketches),single_solid=True,
            strict_BOP_errors=0,closed_STL=True,relocated_reopen=True,parameter_volumes=[volume,probe,volume],print_dimensions_mm=dims),
        M6_stack=dict(panel_y=[95,98],flange_y_provisional=[98,102],washers_y=[[93.4,95],[102,103.6]],nut_y=[88.4,93.4],
            screw_tip_y=83.6,underhead_y=103.6,thread_projection_mm=4.8,full_thread_mm=20),
        M10_stack=dict(stud_tip_y_provisional=55,ring_y=[68.95,70],washer_y=[66.95,68.95],nut_y=[58.95,66.95],
            thread_projection_mm=3.95,pitch_mm=1.5,delivered_hardware_credit=False),
        actual_nominal_SKUs=[dict(sku='0912A2-M060X020VISK',quantity=2,d=6,L=20,head_d=10,head_h=6,key=5,url='https://www.normreich.de/1x-Zylinderschraube-M6x20-DIN-912-A2'),
            dict(sku='0934A2-M060',quantity=2,AF=10,h=5,url='https://www.normreich.de/1x-Sechskantmutter-M6-DIN-934-A2'),
            dict(sku='0125A2-A060',quantity=4,OD=12,ID=6.4,t=1.6,url='https://www.normreich.de/1x-Unterlegscheibe-M6-O64-DIN-125-Form-A-A2'),
            dict(sku='0934A2-M100',quantity=2,AF=17,h=8,url='https://www.normreich.de/1x-Sechskantmutter-M10-DIN-934-A2'),
            dict(sku='0125A2-A100',quantity=2,OD=20,ID=10.5,t=2,url='https://www.normreich.de/1x-Unterlegscheibe-M10-O105-DIN-125-Form-A-A2')],
        source_read_date='2026-10-02',lower_guard_bounds=shell_bounds,deck_bolt_xy=[[-79.5,92],[-29,92]],
        prototype_conditions=['Ring seatY70 and flange4mm MUST be compared with delivered exact S0; not manufacturer-defined datums.',
            'Switch family cylinder includes own casing/studs; own casing-to-tools access is not proved by this envelope.',
            'Key family reserve extends toY161.5 outside DeckY95. No shell aperture or unchanged full robot outline claim.',
            'Nut torque, PETG creep and actual tool fit remain phase2. No hardware ordered or supplied nuts credited.'],
        remaining=['W066/P_SYS and W043 end restraints, native Deck and complete selected assembly/quantities before selection.'],
        source_sha256={**oldhash,**hashes,(LAYOUT/'checks.json').relative_to(ROOT).as_posix():sha(LAYOUT/'checks.json')},
        script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',report)
    print(json.dumps({k:report[k] for k in ('status','hits','tool_access_contacts','errors','pairs','native','worker_wall_seconds')}),flush=True)

if __name__=='__main__':main()
