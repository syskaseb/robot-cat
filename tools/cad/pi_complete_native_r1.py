"""Four editable Pi harness prints, preserving R31 and already built PWM features.

Inherited bodies explicitly pinned snapshots. All NEW booleans/cylinders,
boxes, circle profiles, sweeps and four fully constrained hex profiles editable.
Save before recompute/BOP/mesh. No hardware, slicer or physical PASS.
"""
import json,math,shutil,tempfile
from pathlib import Path
import FreeCAD as A,Part,MeshPart
import pi_wiring_complete_r1 as M
from upper_cover_mount_r1 import polygon
ROOT=M.ROOT
OUT=ROOT/'hardware/cad/studies/pi-complete-native-r1'
E=ROOT/'hardware/electronics/full-cat';C=ROOT/'hardware/cad/studies'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    OUT.mkdir(exist_ok=True);dest=OUT/'PiWiringInterface.FCStd';assert not (OUT/'checks.json').exists()
    if dest.exists():shutil.copy2(dest,OUT/'PiWiringInterface.pre-recompute.FCStd')
    gpio=read(E/'pi-gpio-integrated-r10/plan.json');caddy=read(E/'pi-cable-caddy-r3/plan.json');bus=read(E/'pi-bus-mount-r3/plan.json')
    assert not read(E/'pi-gpio-integrated-r10/checks.json')['hits']
    assert not read(E/'pi-power-usb-r4/checks.json')['hits']
    assert not read(E/'pi-cable-caddy-r3/checks.json')['hits']
    r=M.SavedShapes();entry=ROOT/read(ROOT/'hardware/cad/current-assembly.json')['entry'];o=r.doc(entry);members={x.get('value') for x in M.prop(o['RobotCatAssembly24'],'Group').findall('.//Link')}
    parents={'PiTray':M.world_shape(r,entry,o,'PiTray18',members),
        'Deck':M.load(C/'pwm-branch-restraints-r4/DeckPWMGroundTerminal.brep'),
        'Carrier':M.load(C/'pwm-board-end-restraint-r1/CarrierPWMService_WORLD.brep')}
    plan=dict(parent_R31='hardware/manufacturing/one-batch-prototype-r31/selection.json',
        explicit_parent_snapshots=True,retained_PWM_native_parents=['pwm-branch-restraints-r4','pwm-board-end-restraint-r1'],
        new_stls=4,quantities={'PiTray':1,'Deck':1,'Carrier':1,'BUSBracket':1},
        replacements=['PiTray','Deck','Carrier'],new_part='BUSBracket',
        original_Pi_bores_and_nut_pockets_preserved=True,Pi_raise_mm=7,
        only_native_geometry_probe_not_shared_full_assembly_parameter=True,
        selected=False,physical_pass=False,CP_PI_complete=False)
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    d=A.newDocument('PiWiringInterface');p=d.addObject('App::VarSet','Parameters')
    for n,v in [('PassageRadius',1.2),('PiRaise',7)]:p.addProperty('App::PropertyLength',n);setattr(p,n,v)
    refs={};finals={};sketches=[]
    def bx(name,b):
        q=d.addObject('Part::Box',name);q.Length=b[3]-b[0];q.Width=b[4]-b[1];q.Height=b[5]-b[2];q.Placement.Base=A.Vector(*b[:3]);return q
    def cy(name,x,y,z,rad,h):
        q=d.addObject('Part::Cylinder',name);q.Radius=rad;q.Height=h;q.Placement.Base=A.Vector(x,y,z);return q
    def compound(name,parts):
        q=d.addObject('Part::Compound',name);q.Links=parts;return q
    def cut(name,base,tools):
        # Hex pocket and through bore overlap. Unite native tools first;
        # cutting an overlapping compound produced an invalid BUS result.
        if name=='FinishedBUSBracket':
            for i,tool in enumerate(tools):
                q=d.addObject('Part::Cut',name if i==len(tools)-1 else name+'Step'+str(i))
                q.Base=base;q.Tool=tool;q.Refine=False;base=q
            return base
        q=d.addObject('Part::Cut',name);q.Base=base;q.Tool=compound(name+'Tools',tools);return q
    def fuse(name,parts):
        if name.startswith('BUS'):
            base=parts[0]
            for i,tool in enumerate(parts[1:]):
                q=d.addObject('Part::Fuse',name if i==len(parts)-2 else name+'Step'+str(i))
                q.Base=base;q.Tool=tool;q.Refine=False;base=q
            return base
        q=d.addObject('Part::MultiFuse',name);q.Shapes=parts;return q
    for name in ('PiTray','Deck','Carrier','BUSBracket'):
        additions=[];cutters=[]
        if name in parents:
            base=d.addObject('PartDesign::Feature',name+'PinnedParent');base.Shape=parents[name];base.Label=name+' [inherited source snapshot, source SHA in checks]'
        else:
            boxes=[[-68,0,49,-23,34,52],[-68,33,47,66,39,49],[-26,0,47,-23,36,52]]
            base=fuse('BUSBase',[bx('BUSBaseBox'+str(i),b) for i,b in enumerate(boxes)])
            for i,(x,y) in enumerate(bus['board_mount_axes_mm']):
                additions.append(cy('BUSStand'+str(i),x,y,52,2.45,6.4))
                cutters.append(cy('BUSBoardBore'+str(i),x,y,46,1.2,16))
                s=d.addObject('Sketcher::SketchObject','BUSNutHex'+str(i));s.Placement.Base.z=49
                rr=4.3/math.sqrt(3);polygon(s,[(x+rr*math.cos(j*math.pi/3),y+rr*math.sin(j*math.pi/3)) for j in range(6)]);sketches.append(s)
                q=d.addObject('Part::Extrusion','BUSNutPocket'+str(i));q.Base=s;q.Dir=A.Vector(0,0,2.4);q.Solid=True;cutters.append(q)
            for i,(x,y) in enumerate(bus['body_mount_axes_mm']):cutters.append(cy('BUSRearEarBore'+str(i),x,y,46,1.7,5))
        if name=='PiTray':
            for i,(x,y) in enumerate(( (x,y) for x in (-15.5,42.5) for y in (-24.5,24.5))):
                q=cy('PiRaisedPost'+str(i),x,y,45,3,7);q.setExpression('Height','Parameters.PiRaise');additions.append(q)
                cutters.append(cy('PiOriginalThrough'+str(i),x,y,35,1.45,25))
            plate=bx('CablePlatform',caddy['plateau_world'])
            relief=[bx('ClampReserve'+str(i),b) for i,b in enumerate(caddy['plate_clamp_clearance_boxes_world'])]
            additions.append(cut('CablePlatformClampClearances',plate,relief))
            ring=cy('USBParkOuter',23,-69,64,26,2);inner=cy('USBParkInner',23,-69,63,22,4)
            additions.append(cut('USBLooseParkSeat',ring,[inner]))
        for owner_key in (name,):
            for label,table in [('GPIO',gpio),('Cable',caddy)]:
                key='adds_world' if label=='GPIO' else 'adds_world'
                for i,b in enumerate(table.get(key,{}).get(owner_key,[])):additions.append(bx(name+label+'Seat'+str(i),b))
                for i,b in enumerate(table.get('cuts_world',{}).get(owner_key,[])):cutters.append(bx(name+label+'Slot'+str(i),b))
        if name=='Deck':cutters.append(bx('PiFanWindow',[3,20,93,28,29,115]))
        if name=='Carrier':
            for i,(x,y,direction,z) in enumerate([(10,45,1,151.5),(22,53,1,151.5),(26,57,1,153.25),(14,51,-1,149),(18,53,-1,151.5)]):
                edge=M.B.arc([x+direction*10,y,z-10],[x,y,z-10],[x+direction*10,y,z])
                path=d.addObject('PartDesign::Feature','GPIOArc'+str(i));path.Shape=Part.Wire([edge]);path.Label='R10 fixed route datum; regenerate if route coordinates change'
                profile=d.addObject('Part::Circle','GPIOCircle'+str(i));profile.setExpression('Radius','Parameters.PassageRadius')
                profile.Placement=A.Placement(edge.valueAt(edge.FirstParameter),A.Rotation(A.Vector(0,0,1),edge.tangentAt(edge.FirstParameter)))
                q=d.addObject('Part::Sweep','GPIOPassage'+str(i));q.Sections=[profile];q.Spine=path;q.Solid=True;q.Frenet=False;cutters.append(q)
        f=fuse(name+'JoinedSeats',[base]+additions) if additions else base
        f=cut('Finished'+name,f,cutters) if cutters else f
        finals[name]=f;refs[name]=base
    # All recoverable native tools exist BEFORE this first explicit recompute.
    d.saveAs(str(dest));d.recompute();d.recompute(None,True,True)
    # Newly created linked Compound/Cut tools can retain transient null caches
    # in headless FreeCAD. Restore the saved dependency graph before checking;
    # never export/cache a null shape or waive a failed BOP.
    d.save();A.closeDocument(d.Name);d=A.openDocument(str(dest));d.recompute()
    p=d.getObject('Parameters')
    finals={name:d.getObject('Finished'+name) for name in finals}
    sketches=[d.getObject('BUSNutHex'+str(i)) for i in range(4)]
    def validate():
        for s in sketches:assert s.FullyConstrained and s.solve()==0
        for n,f in finals.items():
            assert not f.Shape.isNull(),n+' null'
            assert f.Shape.isValid(),n+' invalid'
            assert len(f.Shape.Solids)==1 and not f.Shape.check(True),n
        return {n:f.Shape.Volume for n,f in finals.items()}
    volumes=validate();p.PassageRadius=1.3;p.PiRaise=7.2;d.recompute();changed=validate()
    assert changed['Carrier']<volumes['Carrier'] and changed['PiTray']>volumes['PiTray']
    p.PassageRadius=1.2;p.PiRaise=7;d.recompute();restored=validate()
    assert all(abs(restored[n]-volumes[n])<1e-5 for n in finals)
    for o in d.Objects:
        if hasattr(o,'Visibility'):o.Visibility=o in finals.values()
    d.save();rows={};meshes=[]
    for n,f in finals.items():
        s=f.Shape.copy();s.exportBrep(str(OUT/(n+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
        assert mesh.isSolid() and mesh.countComponents()==1 and max(dims)+10<256,n
        stl=OUT/(n+'_x1.stl');mesh.write(str(stl))
        rows[n]=dict(native_object=f.Name,valid=True,single_solid=True,strict_BOP_errors=0,volumes=[volumes[n],changed[n],restored[n]],
            STL=stl.relative_to(ROOT).as_posix(),sha256=M.sha(stl),closed=True,components=1,dimensions_mm=dims,quantity=1,
            orientation='Base down/world+Z up. Brim5 geometrically fits256; slicer/support/warp/nut trials phase2.')
        vs,fs=s.tessellate(.4);meshes.append(dict(name=n,vertices=[list(v) for v in vs],triangles=fs))
    A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-pi-complete-') as td:
        copy=Path(td)/dest.name;shutil.copy2(dest,copy);d=A.openDocument(str(copy));d.recompute()
        for n,row in rows.items():
            s=d.getObject(row['native_object']).Shape;assert s.isValid() and not s.check(True) and abs(s.Volume-volumes[n])<1e-5
        A.closeDocument(d.Name)
    result=dict(status='NATIVE_PRINT_GEOMETRY_AVAILABLE',new_stls=4,parts=rows,fully_constrained_hex_sketches=4,reopen_recompute=True,
        inherited_source_SHA256={**r.hashes,**{str((C/p).relative_to(ROOT)).replace('\\','/'):M.sha(C/p) for p in ['pwm-branch-restraints-r4/DeckPWMGroundTerminal.brep','pwm-board-end-restraint-r1/CarrierPWMService_WORLD.brep']}},
        physical_pass=False,selected=False,remaining=['Finished-sleeve/fastener/affected wiring evidence','One selected print/quantity set','Pi checkpoint marker'])
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (OUT/'preview-geometry.json').write_text(json.dumps(meshes)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
