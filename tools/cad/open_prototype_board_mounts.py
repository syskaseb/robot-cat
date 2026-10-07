"""One shared two-level mounting module; no chassis ownership or wiring claim.

Supplier hole patterns, current P0 datums, both connector directions and tool
sequence are planned together. Retained modules stay untouched. New lower
board frames deliberately invalidate their prior endpoint positions for stage3.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import math
import time
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT = BASE / 'mounting-checkpoint'


def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_plan(A,Part):
    interfaces = ROOT/'hardware/electronics/full-cat/board-interfaces-r1/interfaces.json'
    population = ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json'
    bus = ROOT/'hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep'
    docs = json.loads(interfaces.read_text(encoding='utf-8'))
    pop = json.loads(population.read_text(encoding='utf-8'))
    board = Part.Shape(); board.read(str(bus))
    mount_faces = [f for f in board.Faces if isinstance(f.Surface,Part.Cylinder)
                   and abs(f.Surface.Radius-1.25)<1e-5]
    assert len(mount_faces)==4
    # Reuse the exact world placement from whole_cat_interior, then one explicit
    # +4.52 Z datum change. The cached compound is invalid: datums only, no BOP.
    transform = A.Placement(A.Vector(103.0120752,-20.98790452,49.12000348467585),
                            A.Rotation(A.Vector(0,0,1),90))
    bus_axes = [list(transform.multVec(f.Surface.Center))[:2] for f in mount_faces]
    patterns = {'Pi4':[(x,y) for x in (-15.5,42.5) for y in (-24.5,24.5)],
        'BUS':bus_axes,
        'PWM9685':[(-39+h['xy_mm'][0],-12.7+h['xy_mm'][1]) for h in docs['adafruit815']['holes']],
        'AUX4092':[(35+h['xy_mm'][0],-12.7+h['xy_mm'][1]) for h in docs['pololu4092']['holes']],
        'PWM1608':[(91.59+h['x'],h['y']) for h in pop['board']['holes']]}
    assert len(patterns['AUX4092'])==3 and len(patterns['PWM1608'])==2
    assert abs(patterns['PWM1608'][1][0]-patterns['PWM1608'][0][0]-35.56)<1e-8
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in
            (interfaces,population,bus,BASE/'OpenPrototypePlan.FCStd',
             ROOT/'hardware/reference/pi-interface-2026-10-01/pi4-mechanical.pdf',
             ROOT/'hardware/reference/permaproto1608-2026-09-26/quarterbreadboard.brd',
             ROOT/'tools/cad/whole_cat_interior.py',Path(__file__))}
    return dict(status='SHARED_TWO_LEVEL_MOUNT_PLAN_NOT_SELECTED',selected=False,physical_pass=False,
        source_sha256=pins,source_native= str((BASE/'OpenPrototypePlan.FCStd').relative_to(ROOT)),
        board_hole_axes_world_xy_mm=patterns,
        pcb_bottom_planes_mm={'Pi4':46.52,'BUS':47.52000414467585,'PWM9685':78.,'AUX4092':78.,'PWM1608':78.},
        lower_plate_bottom_z_mm=38.52,plate_thickness_mm=3.,upper_plate_bottom_z_mm=70.,
        pcb_standoff_height_mm={'Pi4':5.,'BUS':6.00000414467585,'upper':5.},
        lower_chassis_axes_xy_mm=[[-70,-31.5],[-70,31.5],[112,-31.5],[112,31.5]],
        upper_column_axes_xy_mm=[[-24,-22],[-24,22],[132,-30],[132,30]],
        upper_spacer_height_mm=28.48,upper_spacer_od_mm=8.,upper_spacer_bore_mm=3.4,
        explicit_frame_changes={'Pi4_CP2':[0,0,4.52],'BUS_CP2':[0,0,4.52],'Monitor_CP2':[0,0,4.52]},
        affected_wire_endpoints_must_rebind_in_stage3=True,old_wire_routes_not_requalified=True,
        retained=['MAIN/neck repaired master','bank R47','all four MTA with both exits','P0/E6 and 15 drives'],
        supplier_vs_assumption={
            'Pi4':'Supplier 58x49 holes at3.5mm PCB edge, design orientation USB/Ethernet+X',
            'BUS':'Four actual R1.25 cylinder axes from vendor source; whole vendor compound invalid',
            'PWM9685':'Adafruit815 revC holes; delivered revision not confirmed',
            'AUX4092':'Supplier reg24d three holes; electrical orientation/population remains OPEN',
            'PWM1608':'Supplier Eagle two holes and1.6002mm PCB; circuit population retained',
            'Monitor':'No invented holes. Four insulating edge supports and two removable ties; delivered underside/lead exits OPEN',
            'gaps_tools':'5/6mm insulation gaps, D3 driver/D6 nut socket are design allowances, not delivered/tool measurements'},
        nominal_fasteners={
            'chassis':'4 M2x8,8 OD4.3/ID2.2/t0.3 washers,4 AF4/h1.6 nuts',
            'pcb':'17 M2x14,34 OD4.3/ID2.2/t0.3 washers,17 AF4/h1.6 nuts; PCB thickness1.6 nominal except1608=1.6002',
            'upper_frame':'4 M3x40,8 OD7/ID3.2/t0.5 washers,4 AF5.5/h2.4 nuts',
            'monitor':'2 T18I ties, removable; quantity/stock candidate until final integration'},
        assembly=['Battery/P0 and MAIN on empty frame; MAIN tightened before S0',
            'Lower carrier on four P0 axes; hold nuts below upper flanges before remaining harness',
            'Lower PCB screws/nuts, Pi/BUS and monitor ties before upper carrier',
            'Upper carrier with four spacers/M3x40; upper PCB mounting before cable insertion',
            'Fit distribution rails/bank next; route both ends of MTA and harness in stage3',
            'Service with source disconnected: remove upper carrier if lower PCB tools need its space; no routine74WAGO disconnections'],
        upper_posts_avoid_narrow_MAIN_PI_and_USB_corridors=True,
        open=['Full harness and moving access','Delivered PCB/PETG fit, load/creep and temperature in phase2',
              'Monitor underside and lead exits','Distribution rail integration, stock and common assembly'] )


def main():
    import FreeCAD as A, Part, Mesh, MeshPart
    from open_deck_p0_supports import sketch,feature,circles
    from open_deck_p0_plate import rect,circle
    tick=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
    native=OUT/'BoardMounts.FCStd'; proof=OUT/'board-mount-checks.json'
    assert not native.exists() and not proof.exists(), 'Recover existing model; do not repeat unchanged construction'
    plan=read_plan(A,Part)
    (OUT/'board-mount-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    d=A.newDocument('OpenPrototypeBoardMounts')
    context=None
    try:
        p=d.addObject('App::VarSet','Parameters')
        for n,v in [('PlateThickness',3),('LowerBase',38.52),('UpperBase',70),('PcbGap',5),
                    ('BusGap',6.00000414467585),('SpacerHeight',28.48),('PcbBore',2.4)]:
            p.addProperty('App::PropertyLength',n); setattr(p,n,v)
        lower=d.addObject('PartDesign::Body','LowerCarrier')
        sk=sketch(lower,'LowerMainPlan','Parameters.LowerBase');rect(sk,-29,-35.5,184,71)
        lower.Tip=feature(lower,'Pad','LowerMain',sk,'Parameters.PlateThickness')
        sk=sketch(lower,'FrontArmsPlan','Parameters.LowerBase')
        rect(sk,-76,28,47.5,7.5);rect(sk,-76,-35.5,47.5,7.5)
        lower.Tip=feature(lower,'Pad','FrontArms',sk,'Parameters.PlateThickness')
        sk=sketch(lower,'LowerVentPlan','Parameters.LowerBase+Parameters.PlateThickness')
        rect(sk,-9,-17,68,34);rect(sk,78,-12,17,24)
        lower.Tip=feature(lower,'Pocket','LowerVentWindows',sk,'Parameters.PlateThickness')
        sk=sketch(lower,'LowerFrameBores','Parameters.LowerBase+Parameters.PlateThickness')
        circles(sk,plan['lower_chassis_axes_xy_mm'],2.4)
        circles(sk,plan['upper_column_axes_xy_mm'],3.4)
        lower.Tip=feature(lower,'Pocket','LowerFrameClearance',sk,'Parameters.PlateThickness')
        sk=sketch(lower,'PiPostPlan','Parameters.LowerBase+Parameters.PlateThickness')
        circles(sk,plan['board_hole_axes_world_xy_mm']['Pi4'],4.5)
        lower.Tip=feature(lower,'Pad','PiPosts',sk,'Parameters.PcbGap')
        sk=sketch(lower,'BusPostPlan','Parameters.LowerBase+Parameters.PlateThickness')
        circles(sk,plan['board_hole_axes_world_xy_mm']['BUS'],4.5)
        lower.Tip=feature(lower,'Pad','BusPosts',sk,'Parameters.BusGap')
        sk=sketch(lower,'LowerPcbBores','Parameters.LowerBase+Parameters.PlateThickness+Parameters.BusGap')
        circles(sk,plan['board_hole_axes_world_xy_mm']['Pi4']+plan['board_hole_axes_world_xy_mm']['BUS'],2.4)
        lower.Tip=feature(lower,'Pocket','LowerPcbClearance',sk,'Parameters.PlateThickness+Parameters.BusGap')
        sk=sketch(lower,'MonitorEdgeSeats','Parameters.LowerBase+Parameters.PlateThickness')
        circles(sk,[(112,2.5),(145,2.5),(112,22.5),(145,22.5)],4.5)
        lower.Tip=feature(lower,'Pad','MonitorInsulatingSeats',sk,'Parameters.PcbGap')
        sk=sketch(lower,'MonitorTieSlots','Parameters.LowerBase+Parameters.PlateThickness')
        for x in (118,139):
            for y in (-4,25.5):rect(sk,x-1.4,y,2.8,3.5)
        lower.Tip=feature(lower,'Pocket','MonitorTieWindows',sk,'Parameters.PlateThickness')
        upper=d.addObject('PartDesign::Body','UpperCarrier')
        sk=sketch(upper,'UpperMainPlan','Parameters.UpperBase');rect(sk,-45,-36,183,72)
        upper.Tip=feature(upper,'Pad','UpperMain',sk,'Parameters.PlateThickness')
        sk=sketch(upper,'UpperVentPlan','Parameters.UpperBase+Parameters.PlateThickness')
        for x,y,w,h in [(-33,-6,51,12),(41,-6,14,12),(78,-12,27,24)]:rect(sk,x,y,w,h)
        upper.Tip=feature(upper,'Pocket','UpperVentWindows',sk,'Parameters.PlateThickness')
        sk=sketch(upper,'UpperFrameBores','Parameters.UpperBase+Parameters.PlateThickness')
        circles(sk,plan['upper_column_axes_xy_mm'],3.4)
        upper.Tip=feature(upper,'Pocket','UpperFrameClearance',sk,'Parameters.PlateThickness')
        upper_axes=sum([plan['board_hole_axes_world_xy_mm'][n] for n in ('PWM9685','AUX4092','PWM1608')],[])
        sk=sketch(upper,'UpperPostsPlan','Parameters.UpperBase+Parameters.PlateThickness')
        circles(sk,upper_axes,4.5)
        upper.Tip=feature(upper,'Pad','UpperPcbPosts',sk,'Parameters.PcbGap')
        sk=sketch(upper,'UpperPcbBores','Parameters.UpperBase+Parameters.PlateThickness+Parameters.PcbGap')
        circles(sk,upper_axes,2.4)
        upper.Tip=feature(upper,'Pocket','UpperPcbClearance',sk,'Parameters.PlateThickness+Parameters.PcbGap')
        spacer=d.addObject('PartDesign::Body','UpperSpacer')
        sk=sketch(spacer,'SpacerProfile',0);circle(sk,0,0,8);circle(sk,0,0,3.4)
        spacer.Tip=feature(spacer,'Pad','SpacerHeight',sk,'Parameters.SpacerHeight')
        instances=[]
        for i,(x,y) in enumerate(plan['upper_column_axes_xy_mm']):
            ob=d.addObject('App::Link',f'Spacer{i+1}');ob.setLink(spacer)
            ob.LinkPlacement.Base=A.Vector(x,y,41.52)
            instances.append(ob)
        def validate():
            d.recompute()
            sketches=[o for o in d.Objects if o.TypeId=='Sketcher::SketchObject']
            assert all(s.FullyConstrained and s.solve()==0 for s in sketches)
            for b in (lower,upper,spacer):
                assert b.Tip.Shape.isValid() and len(b.Tip.Shape.Solids)==1,b.Name
                assert not b.Tip.Shape.check(True),b.Name
                assert all('Invalid' not in o.State and 'Touched' not in o.State for o in b.Group),b.Name
            return {b.Name:b.Tip.Shape.Volume for b in (lower,upper,spacer)}
        baseline=validate()
        d.saveAs(str(native)) # recoverable module before expensive contact/export checks
        p.PcbGap=5.5; changed=validate();assert changed['LowerCarrier']>baseline['LowerCarrier'] and changed['UpperCarrier']>baseline['UpperCarrier']
        p.PcbGap=5;restored=validate();assert all(abs(restored[n]-v)<1e-6 for n,v in baseline.items())
        context=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
        material={o.Name:o.Shape for o in context.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
                  and (o.Name.startswith('P0_') or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'))}
        targets={'LowerCarrier':lower.Shape,'UpperCarrier':upper.Shape,
                 **{o.Name:o.Shape for o in instances}}
        contacts=[];errors=[];tested=0
        for name,s in targets.items():
            for other,t in material.items():
                if not s.BoundBox.intersect(t.BoundBox):continue
                tested+=1
                try:
                    assert s.isValid() and t.isValid()
                    hit=s.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:contacts.append(dict(a=name,b=other,volume_mm3=hit.Volume))
                except Exception as exc:errors.append(dict(a=name,b=other,error=str(exc)))
        exports=[]
        if not contacts and not errors:
            for ob,qty in ((lower,1),(upper,1),(spacer,4)):
                s=ob.Shape.copy();b=s.BoundBox;s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
                path=OUT/(ob.Name+'.stl')
                MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.2,Relative=False).write(str(path))
                mesh=Mesh.Mesh(str(path));assert mesh.isSolid() and mesh.countComponents()==1
                size=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength]
                assert max(size)<256
                exports.append(dict(part=ob.Name,quantity=qty,path=path.relative_to(ROOT).as_posix(),
                    sha256=sha(path),bounds_with_5mm_brim_mm=size,orientation='Flat base +Z; PETG; physical coupon/profile/support assessment OPEN'))
        for body in (lower,upper,spacer):
            for o in body.Group:
                if o.ViewObject:o.Visibility=False
            if body.ViewObject:body.Visibility=True
        d.save()
        A.closeDocument(context.Name);context=None
        A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-mount-reopen-') as temp:
            relocated=Path(temp)/native.name;shutil.copy2(native,relocated)
            d=A.openDocument(str(relocated));lower=d.LowerCarrier;upper=d.UpperCarrier;spacer=d.UpperSpacer;p=d.Parameters
            fresh=validate();assert all(abs(fresh[n]-v)<1e-6 for n,v in baseline.items())
            assert len([o for o in d.Objects if o.TypeId=='App::Link'])==4
        result=dict(status='COMMON_BOARD_MOUNT_LOCAL_CHECKS_CLEAR' if not(contacts or errors) else 'COMMON_BOARD_MOUNT_REQUIRES_LAYOUT_CHANGE',
            selected=False,stage_completed=False,W1_complete=False,W5_complete=False,physical_pass=False,
            started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3),
            source_sha256=plan['source_sha256'],native_sha256=sha(native),baseline_volumes_mm3=baseline,
            parameter_roundtrip_mm=[5,5.5,5],relocated_reopen=True,three_editable_masters_four_spacer_links=True,
            exact_changed_context_pairs=tested,contacts=contacts,errors=errors,exports=exports,
            no_cached_vendor_BUS_BOP=True,full_populated_board_and_harness_contacts_OPEN=True,
            pending=['Fastener bearing/shaft/nut/tool checks','Distribution rail/support/insulation integration',
                     'Current endpoint datum rebinding in stage3; old routes not qualified'])
        assert all(sha(ROOT/path)==digest for path,digest in plan['source_sha256'].items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','worker_wall_seconds','exact_changed_context_pairs','contacts','errors')}),flush=True)
    finally:
        if context:A.closeDocument(context.Name)
        if d.Name in A.listDocuments():A.closeDocument(d.Name)


if __name__=='__main__':main()
