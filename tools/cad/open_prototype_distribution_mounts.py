"""One shared side-rail mounting plan, native construction and changed checks.

Open prototype: isolated actual-hole PCB mounts plus two accessible distribution
rails. Wire routes/stock and electrical qualification are NOT this stage. No
retained P0, R47, MAIN or original source is overwritten. Bounds select tests,
never establish positive material collisions. Nominal spaces stay labelled.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,time,math,shutil,tempfile

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/mounting-checkpoint'
DEADLINE=datetime.fromisoformat('2026-10-07T23:10:24+00:00')

def sha(p):
    import hashlib
    return hashlib.sha256(p.read_bytes()).hexdigest()

def deadline():assert datetime.now(timezone.utc)<DEADLINE,'Bounded stage deadline; preserve source and stop'

def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    from open_deck_p0_supports import sketch,feature,circles
    from open_deck_p0_plate import rect,circle
    started=datetime.now(timezone.utc).isoformat();tick=time.monotonic();deadline()
    native=OUT/'DistributionMounts.FCStd';proof=OUT/'distribution-mount-checks.json'
    assert not native.exists() and not proof.exists(),'Receive existing result; no duplicate construction'
    source=OUT/'BoardMountAssembly.FCStd'
    old=json.loads((OUT/'board-hardware-checks.json').read_text(encoding='utf-8'))
    mountplan=json.loads((OUT/'board-mount-plan.json').read_text(encoding='utf-8'))
    assert sha(source)==old['native_sha256']
    paths=[source,OUT/'board-hardware-checks.json',OUT/'board-rear-tool-checks.json',OUT/'board-mount-plan.json',
        OUT.parent/'OpenPrototypePlan.FCStd',ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep',
        ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json',
        ROOT/'hardware/electronics/full-cat/board-interfaces-r1/interfaces.json',
        ROOT/'hardware/electronics/full-cat/pi-power-usb-r1/plan.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    rows={'L':[['FL_P','FL_G','D_FL','RL_P','RL_G'],['P_SYS','P_FRONT','P_REAR','D_RL','G2']],
          'R':[['FR_P','FR_G','D_FR','RR_P','RR_G'],['G1','D_RR','P_AUX','G_AUX','G_TAIL']]}
    places=[]
    for side,levels in rows.items():
        for level,names in enumerate(levels):
            for x,name in zip([-76,-34,8,50,92],names):
                large=name in ['P_SYS','P_FRONT','P_REAR','G1']
                places.append(dict(role=name,native=name+'_CP2',side=side,level=level,
                    centre_xy_mm=[x,84.75 if side=='L' else -84.75],base_z_mm=61 if level==0 else 93,
                    size_mm=[37,22,11] if large else [30,19,9],
                    sku='221-615' if large else '221-415',tie_quantity=2,
                    orientation='Flat lever-up; entries toward centre; nominal supplier casing budget, not delivered model'))
    plan=dict(status='SHARED_DISTRIBUTION_MOUNT_PLAN_NOT_SELECTED',physical_pass=False,source_sha256=pins,
        rail_centres_y_mm=[84.75,-84.75],rail_extent_x_mm=[-96,111],width_mm=29.5,
        lower_board_bottom_z_mm=mountplan['pcb_bottom_planes_mm'],monitor_y_mm=[-25,0],
        reason='Monitor leaves BUS USB-C body/withdrawal budget; side distribution avoids central PCB/ATO access',
        arm_and_side_column_axes_xy_mm=[[x,y] for x in (-13,71) for y in (-84.75,84.75)],
        arm_plate_mm=3,rib_and_foot_height_mm=8,side_column_base_z_mm=47.72,
        side_spacer_height_mm=10.28,rail_base_z_mm=58,upper_rail_z_mm=90,
        distribution=places,quantity20_no_added_logical_buses=True,
        fasteners_added={'M3x30':4,'M3_washer':8,'M3_nut':4},distribution_ties=40,
        preserved=['P0','R47 bank geometry','MAIN worldZ46.52','4MTA and both factory exit directions','P0/E6/15 drives/MG92B'],
        invalidated=['Old WAGO placement/short-lead/lever/strain-relief proofs; endpoints and source lengths rebind in next wiring stage',
                    'Monitor old position/tie geometry'],
        assembly=['Seat captive lower PCB nuts, then clamp carrier before Pi',
            'Fit side spacers/rails before side WAGO; side bolts reachable through upper rail driver apertures',
            'Pi/BUS and negative-Y monitor before upper PCB carrier; rear frame nuts by lateral AF5.5 spanner',
            'Bench dress buses; lower WAGO before upper WAGO; two replaceable ties per body, levers open before ties',
            'R47 bank/4MTA retained; route all leads later, no independent cassette lift or74routine disconnects'],
        tools_and_fit='Nominal budgets, actual tools/PETG/tie/connector/temperature checks are phase2',
        selected=False,stage_completed=False)
    (OUT/'distribution-mount-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    d=A.openDocument(str(source));context=None
    try:
        p=d.Parameters;lower=d.LowerCarrier
        # Mirror only monitor supports and its existing tie windows. Pi/BUS axes
        # and all retained source shapes remain unchanged.
        sk=d.MonitorEdgeSeats
        for i,g in enumerate(sk.Geometry):sk.setDatum(i*3+1,A.Units.Quantity(str(-g.Center.y)+' mm'))
        sk=d.MonitorTieSlots
        for i in range(4):
            y=sk.Constraints[i*12+9].Value
            sk.setDatum(i*12+9,A.Units.Quantity(str(-y-2.8)+' mm'))
        for name,value in [('SideFootHeight',8.),('SideSpacerHeight',10.28),('SideRailRise',32.),('SideRailThickness',3.)]:
            p.addProperty('App::PropertyLength',name);setattr(p,name,value)
        sk=sketch(lower,'SideArmPlan','Parameters.LowerBase')
        for x in (-13,71):
            rect(sk,x-5,25,10,59.75);rect(sk,x-5,-84.75,10,59.75)
        lower.Tip=feature(lower,'Pad','SideArms',sk,'Parameters.PlateThickness')
        sk=sketch(lower,'SideRibPlan','Parameters.LowerBase')
        for x in (-13,71):
            rect(sk,x-2,30,4,54.75);rect(sk,x-2,-84.75,4,54.75)
        lower.Tip=feature(lower,'Pad','SideRibs',sk,'Parameters.SideFootHeight')
        sk=sketch(lower,'SideFootPlan','Parameters.LowerBase')
        circles(sk,plan['arm_and_side_column_axes_xy_mm'],12)
        lower.Tip=feature(lower,'Pad','SideFeet',sk,'Parameters.SideFootHeight')
        sk=sketch(lower,'SideFootBorePlan','Parameters.LowerBase+Parameters.SideFootHeight')
        circles(sk,plan['arm_and_side_column_axes_xy_mm'],3.4)
        lower.Tip=feature(lower,'Pocket','SideFootBores',sk,'Parameters.SideFootHeight')
        # Added arms must not refill any inherited captive nut pocket.
        lower.Tip=feature(lower,'Pocket','RetainedCaptiveSeats',d.CaptiveNutPlan,'Parameters.CaptiveNutDepth')
        lower.Tip=feature(lower,'Pocket','RetainedCaptiveBores',d.CaptiveBoltPlan,'Parameters.PlateThickness')
        rail=d.addObject('PartDesign::Body','SideDistributionRail')
        sk=sketch(rail,'SideRailBasePlan',0);rect(sk,-96,-14.75,207,29.5)
        rail.Tip=feature(rail,'Pad','SideRailBase',sk,'Parameters.SideRailThickness')
        sk=sketch(rail,'SideRailUprightPlan','Parameters.SideRailThickness')
        for x in (-13,71):
            rect(sk,x-4,-14.75,8,4);rect(sk,x-4,10.75,8,4)
        rail.Tip=feature(rail,'Pad','SideRailUprights',sk,'Parameters.SideRailRise-Parameters.SideRailThickness')
        sk=sketch(rail,'SideRailUpperPlan','Parameters.SideRailRise');rect(sk,-96,-14.75,207,29.5)
        rail.Tip=feature(rail,'Pad','SideRailUpper',sk,'Parameters.SideRailThickness')
        sk=sketch(rail,'SideRailBoltPlan','Parameters.SideRailRise+Parameters.SideRailThickness')
        circles(sk,[(-13,0),(71,0)],3.4)
        rail.Tip=feature(rail,'Pocket','SideRailBoltClearance',sk,'Parameters.SideRailRise+Parameters.SideRailThickness')
        sk=sketch(rail,'SideRailDriverPlan','Parameters.SideRailRise+Parameters.SideRailThickness')
        circles(sk,[(-13,0),(71,0)],8)
        rail.Tip=feature(rail,'Pocket','SideRailDriverWindows',sk,'Parameters.SideRailThickness')
        for suffix,z in [('Lower','Parameters.SideRailThickness'),('Upper','Parameters.SideRailRise+Parameters.SideRailThickness')]:
            sk=sketch(rail,'SideRailTies'+suffix,z)
            for x in (-76,-34,8,50,92):
                for dx in (-8,8):
                    for y in (-13.2,11.5):rect(sk,x+dx-1.75,y,3.5,1.7)
            rail.Tip=feature(rail,'Pocket','SideRailTieWindows'+suffix,sk,'Parameters.SideRailThickness')
        spacer=d.addObject('PartDesign::Body','SideRailSpacer')
        sk=sketch(spacer,'SideSpacerPlan',0);circle(sk,0,0,8);circle(sk,0,0,3.4)
        spacer.Tip=feature(spacer,'Pad','SideSpacerHeight',sk,'Parameters.SideSpacerHeight')
        links=[]
        for i,y in enumerate(plan['rail_centres_y_mm']):
            ob=d.addObject('App::Link','SideRail'+str(i+1));ob.setLink(rail);ob.LinkPlacement.Base=A.Vector(0,y,58);links.append(ob)
        for i,(x,y) in enumerate(plan['arm_and_side_column_axes_xy_mm']):
            ob=d.addObject('App::Link','SideColumn'+str(i+1));ob.setLink(spacer);ob.LinkPlacement.Base=A.Vector(x,y,47.72);links.append(ob)
        changed_masters=[lower,rail,spacer]
        def validate():
            deadline();d.recompute()
            for body in changed_masters:
                assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True),body.Name
                assert all('Invalid' not in o.State and 'Touched' not in o.State for o in body.Group),body.Name
                assert all(o.FullyConstrained and o.solve()==0 for o in body.Group if o.TypeId=='Sketcher::SketchObject'),body.Name
            return {b.Name:b.Shape.Volume for b in changed_masters}
        baseline=validate()
        d.saveAs(str(native))
        p.SideRailRise=33.;trial=validate();assert trial['SideDistributionRail']>baseline['SideDistributionRail']
        p.SideRailRise=32.;restored=validate();assert all(abs(restored[n]-v)<1e-6 for n,v in baseline.items())
        context=A.openDocument(str(OUT.parent/'OpenPrototypePlan.FCStd'))
        real={o.Name:o.Shape for o in context.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
              and (o.Name.startswith('P0_') or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'))}
        targets={'LowerCarrier':lower.Shape,**{ob.Name:ob.Shape for ob in links}}
        contacts=[];errors=[];tested=0;reservation_contacts=[]
        def compare(name,s,objects,dest=contacts):
            nonlocal tested
            for n,t in objects.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                tested+=1;deadline()
                try:
                    assert s.isValid() and t.isValid();hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:dest.append(dict(a=name,b=n,volume_mm3=hit.Volume))
                except Exception as e:errors.append(dict(a=name,b=n,error=str(e)))
        for n,s in targets.items():compare(n,s,real)
        all_prints={'LowerCarrier':lower.Shape,'UpperCarrier':d.UpperCarrier.Shape,
                    **{ob.Name:ob.Shape for ob in d.Objects if ob.TypeId=='App::Link'}}
        from itertools import combinations
        for (n,s),(m,t) in combinations(all_prints.items(),2):
            if n not in targets and m not in targets:continue
            compare(n,s,{m:t})
        # Supplier BUS is evaluated solid-by-solid. Invalid solid25 may only be
        # excluded when its conservative bounds do not intersect ANY mount.
        raw=Part.Shape();raw.read(str(paths[5]));transform=A.Placement(A.Vector(103.0120752,-20.98790452,50.32000348467585),A.Rotation(A.Vector(0,0,1),90))
        bus_parts={};invalid=[]
        pcbgroup=d.addObject('App::DocumentObjectGroup','SupplierAndNominalBoardReferences')
        for i,part in enumerate(raw.Solids):
            s=part.copy();s.Placement=transform.multiply(s.Placement)
            if not s.isValid():
                near=[n for n,t in all_prints.items() if s.BoundBox.intersect(t.BoundBox)]
                invalid.append(dict(index=i,near_mounts=near,excluded_only_by_conservative_bounds=not near))
                if near:errors.append(dict(a='BUSsolid'+str(i),error='Invalid vendor solid intersects mounting bounds',targets=near))
                continue
            bus_parts['BUSsolid'+str(i)]=s
            ob=d.addObject('Part::Feature','BUSsupplier'+str(i));ob.Shape=s;pcbgroup.addObject(ob)
        for n,s in all_prints.items():compare(n,s,bus_parts)
        for ob in d.NominalMountHardware.Group:compare(ob.Name,ob.Shape,bus_parts)
        # Plain nominal board plates retain real supplier hole axes. Their
        # missing underside population is an explicit delivered-fit allowance.
        nominal={'Pi4':(-19,-28,85,56,1.6,2.75),'PWM9685':(-39,-12.7,62.23,25.4,1.6,2.5),
                 'AUX4092':(35,-12.7,25.4,25.4,1.6,2.18),'PWM1608':(70,-25.4,43.18,50.8,1.6002,3.2)}
        for name,(x,y,w,h,t,hole) in nominal.items():
            z=mountplan['pcb_bottom_planes_mm'][name];s=Part.makeBox(w,h,t,A.Vector(x,y,z))
            for hx,hy in mountplan['board_hole_axes_world_xy_mm'][name]:s=s.cut(Part.makeCylinder(hole/2,t,A.Vector(hx,hy,z)))
            assert s.isValid();ob=d.addObject('Part::Feature',name+'NominalPCB');ob.Shape=s;pcbgroup.addObject(ob)
            for n,q in all_prints.items():compare(n,q,{ob.Name:s})
        # The explicit monitor and actual BUS mouth are planned with the
        # inherited provisional cable body allowance, never called vendor fit.
        monitor=Part.makeBox(41,25,12,A.Vector(108,-25,47.72))
        plug=Part.makeBox(25,12,8,A.Vector(103.81628928,5.1220508043,47.4895251897))
        withdrawal=Part.makeBox(40,12,8,A.Vector(103.81628928,5.1220508043,47.4895251897))
        reserved={'MonitorNominal':monitor,'BUS_USB_C_body_allowance':plug,'BUS_USB_C_withdrawal_allowance':withdrawal}
        compare('BUS_USB_C_withdrawal_allowance',withdrawal,{'MonitorNominal':monitor},reservation_contacts)
        for n,s in all_prints.items():compare(n,s,reserved,reservation_contacts)
        # Every logical bus has exactly one current slot; no copied spare.
        distribution={}
        for r in places:
            x,y=r['centre_xy_mm'];w,h,t=r['size_mm'];s=Part.makeBox(w,h,t,A.Vector(x-w/2,y-h/2,r['base_z_mm']))
            distribution[r['native']]=s
            ob=d.addObject('Part::Feature',r['native']);ob.Shape=s;pcbgroup.addObject(ob)
        context_reserved={o.Name:o.Shape for o in context.Objects if o.Name.startswith(('S0_','S1_','MTA_','F_PI_')) and 'Shape' in o.PropertiesList}
        for n,s in targets.items():compare(n,s,{**distribution,**context_reserved},reservation_contacts)
        new_hardware=d.addObject('App::DocumentObjectGroup','SideMountHardware')
        side_hw={};tools=[]
        for i,(x,y) in enumerate(plan['arm_and_side_column_axes_xy_mm'],1):
            def cylinder(z,r,h):return Part.makeCylinder(r,h,A.Vector(x,y,z))
            shaft=cylinder(31.5,1.5,30).fuse(cylinder(61.5,2.75,3))
            upperwasher=cylinder(61,3.5,.5).cut(cylinder(61,1.6,.5))
            lowerwasher=cylinder(39.22,3.5,.5).cut(cylinder(39.22,1.6,.5))
            rad=5.5/math.sqrt(3);vs=[A.Vector(x+rad*math.cos(j*math.pi/3),y+rad*math.sin(j*math.pi/3),36.82) for j in range(6)]
            nut=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(A.Vector(0,0,2.4)).cut(cylinder(36.82,1.525,2.4))
            for suffix,s in [('Screw',shaft),('TopWasher',upperwasher),('BottomWasher',lowerwasher),('Nut',nut)]:
                name='SideMount'+str(i)+suffix;ob=d.addObject('Part::Feature',name);ob.Shape=s;new_hardware.addObject(ob);side_hw[name]=s
                compare(name,s,{**all_prints,**real});compare(name,s,distribution,reservation_contacts)
            for suffix,s in [('Driver',cylinder(64.5,1.5,40)),('NutSocket',cylinder(24.82,3.5,12))]:
                name='SideMount'+str(i)+suffix;before=len(contacts)+len(reservation_contacts)
                compare(name,s,{**all_prints,**real});compare(name,s,distribution,reservation_contacts)
                tools.append(dict(id=name,clear=len(contacts)+len(reservation_contacts)==before,nominal_allowance=True))
        d.recompute();deadline()
        for body in changed_masters:
            for ob in body.Group:
                if ob.ViewObject:ob.Visibility=False
            if body.ViewObject:body.Visibility=body==lower
        d.save();exports=[]
        if not(contacts or errors or reservation_contacts):
            for body,qty in [(lower,1),(rail,2),(spacer,4)]:
                s=body.Shape.copy();b=s.BoundBox;s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
                path=OUT/(body.Name+'Integrated.stl')
                MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False).write(str(path))
                mesh=Mesh.Mesh(str(path));assert mesh.isSolid() and mesh.countComponents()==1
                size=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength];assert max(size)<256
                exports.append(dict(part=body.Name,quantity=qty,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bounds_with_5mm_brim_mm=size))
        A.closeDocument(context.Name);context=None;A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-side-mount-reopen-') as td:
            path=Path(td)/native.name;shutil.copy2(native,path);d=A.openDocument(str(path))
            lower=d.LowerCarrier;rail=d.SideDistributionRail;spacer=d.SideRailSpacer;p=d.Parameters;changed_masters=[lower,rail,spacer]
            fresh=validate();assert all(abs(fresh[n]-v)<1e-6 for n,v in baseline.items())
            assert len(d.SideMountHardware.Group)==16
        result=dict(status='SHARED_DISTRIBUTION_MOUNTS_LOCAL_CLEAR' if not(contacts or errors or reservation_contacts) else 'SHARED_DISTRIBUTION_MOUNTS_REQUIRE_CHANGE',
            source_sha256=pins,native_sha256=sha(native),started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3),exact_candidate_pairs=tested,
            material_contacts=contacts,errors=errors,nominal_reservation_contacts=reservation_contacts,
            invalid_BUS_solids=invalid,valid_BUS_solid_count=len(bus_parts),
            restored_parameter_mm=[32,33,32],relocated_reopen=True,baseline_volumes_mm3=baseline,
            distribution_role_count=20,exports=exports,side_tools=tools,
            stage_completed=False,selected=False,physical_pass=False,
            known_bounds=['BUS116valid source solids checked individually; invalid component excluded only when no mount bounds overlap',
                'Other nominal PCBs retain supplier holes; underside population/thermal/actual tool and plug fit remain phase2',
                'WAGO flat casing budgets and relocated slots are nominal, not actual lever/cable qualification',
                'No old wire route/endpoint/stock credit after distribution/monitor changes'],
            next='Receive whole result, resolve only changed failed interface; then insulation/fixture/one selection. No wiring stage or deadline extension')
        assert all(sha(ROOT/k)==v for k,v in pins.items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','worker_wall_seconds','exact_candidate_pairs','material_contacts','errors','nominal_reservation_contacts','invalid_BUS_solids')}),flush=True)
    finally:
        if context:A.closeDocument(context.Name)
        if d.Name in A.listDocuments():A.closeDocument(d.Name)

if __name__=='__main__':main()
