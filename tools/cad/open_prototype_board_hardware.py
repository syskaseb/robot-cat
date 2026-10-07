"""Complete board-carrier assembly hardware, preserving the clear foundation.

Captive lower nuts solve the real assembly dependency: rail clamps must be
tightened before the Pi blocks their drivers. No changed supplier PCB holes.
Nominal fastener/thread/tool models are design allowances, not physical PASS.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, time, tempfile, shutil

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'

def sha(p):
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    import FreeCAD as A, Part, Mesh, MeshPart, Sketcher
    from open_deck_p0_supports import sketch,feature,circles
    tick=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    source=OUT/'BoardMounts.FCStd';native=OUT/'BoardMountAssembly.FCStd'
    assert not native.exists(), 'Receive existing worker/result, do not repeat'
    check=json.loads((OUT/'board-mount-checks.json').read_text(encoding='utf-8'))
    plan=json.loads((OUT/'board-mount-plan.json').read_text(encoding='utf-8'))
    assert check['status']=='COMMON_BOARD_MOUNT_LOCAL_CHECKS_CLEAR' and sha(source)==check['native_sha256']
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in
        [source,OUT/'board-mount-checks.json',OUT/'board-mount-plan.json',Path(__file__),
         OUT.parent/'OpenPrototypePlan.FCStd']}
    d=A.openDocument(str(source));context=None
    try:
        lower=d.LowerCarrier;p=d.Parameters
        lower_axes=plan['board_hole_axes_world_xy_mm']['Pi4']+plan['board_hole_axes_world_xy_mm']['BUS']
        p.addProperty('App::PropertyLength','CaptiveNutDepth');p.CaptiveNutDepth=1.8
        sk=sketch(lower,'CaptiveNutBossPlan','Parameters.LowerBase')
        circles(sk,lower_axes,8.)
        lower.Tip=feature(lower,'Pad','CaptiveNutBosses',sk,'Parameters.PlateThickness')
        sk=sketch(lower,'CaptiveNutPlan','Parameters.LowerBase+Parameters.CaptiveNutDepth')
        # Block-constrained regular hexagons; the source axis and AF allowance
        # are stated explicitly, not an uneditable final boolean snapshot.
        radius=4.3/math.sqrt(3)
        for x,y in lower_axes:
            pts=[A.Vector(x+radius*math.cos(i*math.pi/3),y+radius*math.sin(i*math.pi/3),0) for i in range(6)]
            for i in range(6):
                j=sk.addGeometry(Part.LineSegment(pts[i],pts[(i+1)%6]),False)
                sk.addConstraint(Sketcher.Constraint('Block',j))
        lower.Tip=feature(lower,'Pocket','CaptiveNutSeats',sk,'Parameters.CaptiveNutDepth')
        sk=sketch(lower,'CaptiveBoltPlan','Parameters.LowerBase+Parameters.PlateThickness')
        circles(sk,lower_axes,2.4)
        lower.Tip=feature(lower,'Pocket','CaptiveBoltClearance',sk,'Parameters.PlateThickness')
        def validate_lower():
            d.recompute();s=lower.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            assert all(o.FullyConstrained and o.solve()==0 for o in lower.Group if o.TypeId=='Sketcher::SketchObject')
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in lower.Group)
            return s.Volume
        volume=validate_lower();p.CaptiveNutDepth=2.;changed=validate_lower();assert changed<volume
        p.CaptiveNutDepth=1.8;assert abs(validate_lower()-volume)<1e-6
        context=A.openDocument(str(OUT.parent/'OpenPrototypePlan.FCStd'))
        frame={o.Name:o.Shape for o in context.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
               and (o.Name.startswith('P0_') or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'))}
        prints={'LowerCarrier':lower.Shape,'UpperCarrier':d.UpperCarrier.Shape,
            **{o.Name:o.Shape for o in d.Objects if o.TypeId=='App::Link'}}
        contacts=[];errors=[];tested=0
        def compare(name,s,targets,ignore=()):
            nonlocal tested
            assert s.isValid(),name
            for n,t in targets.items():
                if n in ignore or not s.BoundBox.intersect(t.BoundBox):continue
                tested+=1
                try:
                    assert t.isValid();v=s.common(t);assert v.isValid()
                    if v.Volume>1e-5:contacts.append(dict(a=name,b=n,volume_mm3=v.Volume))
                except Exception as e:errors.append(dict(a=name,b=n,error=str(e)))
        # Only the lower carrier changed; inherited unchanged comparisons stay
        # pinned to board-mount-checks rather than rerunning their BOP.
        compare('LowerCarrier',lower.Shape,frame)
        compare('LowerCarrier',lower.Shape,prints,('LowerCarrier',))
        def cylinder(x,y,z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))
        def washer(x,y,z,od,id_,h):return cylinder(x,y,z,od/2,h).cut(cylinder(x,y,z,id_/2,h))
        def nut(x,y,z,af,h,bore):
            r=af/math.sqrt(3);v=[A.Vector(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z) for i in range(6)]
            return Part.Face(Part.makePolygon(v+[v[0]])).extrude(A.Vector(0,0,h)).cut(cylinder(x,y,z,bore/2,h))
        hardware=d.addObject('App::DocumentObjectGroup','NominalMountHardware')
        fasteners=[];hw={};tool_results=[]
        def put(name,s):
            ob=d.addObject('Part::Feature',name);ob.Shape=s;hardware.addObject(ob);hw[name]=s
        def stack(role,x,y,diam,length,underhead,topwasher,bottomwasher,nutz,af,nuth,captive=False):
            root=role+str(len(fasteners)+1);tip=underhead-length
            shaft=cylinder(x,y,tip,diam/2,length)
            head=cylinder(x,y,underhead,2.75 if diam==3 else 1.9,3 if diam==3 else 2)
            put(root+'Screw',shaft.fuse(head))
            for suffix,z in [('TopWasher',topwasher),('BottomWasher',bottomwasher)]:
                if z is not None:put(root+suffix,washer(x,y,z,7 if diam==3 else 4.3,diam+.2,.5 if diam==3 else .3))
            put(root+'Nut',nut(x,y,nutz,af,nuth,diam+.05))
            engagement=min(underhead,nutz+nuth)-max(tip,nutz)
            assert engagement>=nuth-1e-6,(root,engagement,nuth)
            assert tip<=nutz+1e-6,(root,'no full nut engagement')
            fasteners.append(dict(id=root,role=role,axis_xy_mm=[x,y],diameter_mm=diam,length_mm=length,
                nut_z_mm=[nutz,nutz+nuth],underhead_z_mm=underhead,tip_z_mm=tip,
                nominal_nut_engagement_mm=engagement,protrusion_mm=nutz-tip,captive=captive))
            # Tool access belongs to a stated assembly stage, not the final
            # crowded robot; later harness and connector motion remain stage3.
            driver=cylinder(x,y,underhead+(3 if diam==3 else 2),1.5,18)
            obstacles=dict(frame)
            if role=='RailClamp':obstacles.update({n:s for n,s in prints.items() if not n.startswith('Spacer') and n!='UpperCarrier'})
            else:obstacles.update(prints)
            before=len(contacts);compare(root+'DriverStage',driver,obstacles)
            tool_results.append(dict(id=root+'DriverStage',assembly_stage='Before PCB/upper carrier' if role=='RailClamp' else 'Before connectors/harness',
                allowance='D3 vertical driver, nominal design allowance',clear=len(contacts)==before))
            if not captive:
                socket=cylinder(x,y,nutz-12,3.5 if diam==3 else 3.,12)
                before=len(contacts);compare(root+'NutToolStage',socket,obstacles)
                tool_results.append(dict(id=root+'NutToolStage',allowance='D7 M3 / D6 M2 socket; final user tool not measured',clear=len(contacts)==before))
        for x,y in plan['lower_chassis_axes_xy_mm']:
            stack('RailClamp',x,y,3,14,43.22,42.72,33.52,31.12,5.5,2.4)
        for x,y in plan['upper_column_axes_xy_mm']:
            stack('UpperFrame',x,y,3,45,78.22,77.72,39.22,36.82,5.5,2.4)
        for board in ('Pi4','BUS','PWM9685','AUX4092','PWM1608'):
            bottom=plan['pcb_bottom_planes_mm'][board];thickness=1.6002 if board=='PWM1608' else 1.6
            captive=board in ('Pi4','BUS')
            nz=41.52-1.6 if captive else 74.72-.3-1.6
            for x,y in plan['board_hole_axes_world_xy_mm'][board]:
                stack(board,x,y,2,12 if captive else 14,bottom+thickness+.3,bottom+thickness,
                    None if captive else 74.72-.3,nz,4.,1.6,captive)
        for n,s in hw.items():compare(n,s,{**frame,**prints})
        # Verify each clamp's real bearing on the actual retained rail, not bbox.
        bearings=[]
        for i,(x,y) in enumerate(plan['lower_chassis_axes_xy_mm'],1):
            pad=prints['TopClampPad'+str(i)]
            probe=pad.copy();probe.translate(A.Vector(0,0,-.001))
            area=sum(probe.common(s).Volume/.001 for n,s in frame.items() if 'Side' in n)
            assert area>60,(i,area)
            bearings.append(dict(station=i,bearing_area_mm2=area,axis_inboard_no_drill=True))
        # PCB hole entry/underside population are not substituted by rectangles.
        # Here only the fastener's actual supplier axis/known PCB thickness is
        # checked; populated vendor fit remains a separate whole-stage gate.
        export=OUT/'LowerCarrierAssembly.stl';s=lower.Shape.copy();b=s.BoundBox
        s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
        exports=[]
        if not contacts and not errors:
            MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False).write(str(export))
            m=Mesh.Mesh(str(export));assert m.isSolid() and m.countComponents()==1
            assert max(m.BoundBox.XLength+10,m.BoundBox.YLength+10,m.BoundBox.ZLength)<256
            exports=[dict(part='LowerCarrier',replaces='LowerCarrier.stl',path=export.relative_to(ROOT).as_posix(),sha256=sha(export),quantity=1)]
        for o in lower.Group:
            if o.ViewObject:o.Visibility=False
        if lower.ViewObject:lower.Visibility=True
        d.saveAs(str(native));A.closeDocument(context.Name);context=None;A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-board-hardware-reopen-') as td:
            relocated=Path(td)/native.name;shutil.copy2(native,relocated)
            d=A.openDocument(str(relocated));d.recompute();lower=d.LowerCarrier;p=d.Parameters
            assert abs(validate_lower()-volume)<1e-6
            assert len(d.NominalMountHardware.Group)==len(hw)
        result=dict(status='BOARD_HARDWARE_CHECKS_CLEAR' if not(contacts or errors) else 'BOARD_HARDWARE_REQUIRES_ASSEMBLY_CHANGE',
            stage_completed=False,selected=False,physical_pass=False,started_utc=started,
            finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3),
            source_sha256=pins,native_sha256=sha(native),changed_lower_volume_mm3=volume,
            parameter_roundtrip_nut_depth_mm=[1.8,2.,1.8],relocated_reopen=True,
            exact_changed_pairs=tested,contacts=contacts,errors=errors,clamp_bearings=bearings,
            fasteners=fasteners,tools=tool_results,exports=exports,
            quantities={'M3x14':4,'M3x45':4,'M3_washer':16,'M3_nut':8,
                'M2x12':8,'M2x14':9,'M2_washer':26,'M2_nut':17,'monitor_T18I':2},
            installation=['Seat8 M2 nuts in AF4.3 underside pockets; temporary removable tape retains nuts only, not structural',
                'Install lower carrier/pads/jaws; tighten rail clamps before Pi; no frame drilling',
                'Install Pi/BUS M2x12 into captive nuts; monitor2ties; upper spacers/carrierM3x45',
                'Upper9PCB boltsM2x14/nuts before harness; remove upper carrier to service lower board screws'],
            limits=['Nominal fastener/nut/tool dimensions; delivered lengths and fit need phase2 coupon',
                'PCB underside/populated vendor checks and distribution mounting still stage2 OPEN',
                'Full cable routes/strain relief/stock remain stage3; no complete M5/W1/W5 credit'])
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        (OUT/'board-hardware-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','worker_wall_seconds','exact_changed_pairs','contacts','errors')}),flush=True)
    finally:
        if context:A.closeDocument(context.Name)
        if d.Name in A.listDocuments():A.closeDocument(d.Name)

if __name__=='__main__':main()
