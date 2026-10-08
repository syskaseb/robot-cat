"""One editable, removable two-wire saddle on the retained distribution rail.

Only the checked Pi splice pair. Two separate9mm insulation seats, not a
clamp on the joint. Removal slides+Y through existing casing gaps after ties
are cut: no extra electrical disconnection or assumed extra factory length.
Purchased tie dimensions/force and wire OD remain explicit delivery gates.
"""
import json
import math
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from open_prototype_wiring_endpoints import ROOT, BASE, CURRENT, read, sha, bounds

OUT=BASE/'wiring-checkpoint'
MODEL=OUT/'PiWireSupportAssembly.FCStd'
PROOF=OUT/'pi-wire-support-checks.json'


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    from open_deck_p0_supports import sketch,feature
    from open_deck_p0_plate import rect
    if '--reopen' in sys.argv:
        proof=read(PROOF);assert sha(MODEL)==proof['native_sha256']
        d=A.openDocument(str(MODEL));d.recompute()
        for name,row in proof['native_bodies'].items():
            b=d.getObject(name)
            assert b.Shape.isValid() and len(b.Shape.Solids)==1
            assert abs(b.Shape.Volume-row['volume_mm3'])<1e-5
            assert b.Tip.Name==row['tip']
        assert abs(d.Parameters.SpliceSeatThickness.Value-2)<1e-9
        print('Fresh process reopen: native bodies/volumes/tips/parameter preserved',flush=True)
        A.closeDocument(d.Name);return
    tick=time.monotonic()
    route=read(OUT/'source-output-plan.json')
    assert route['status']=='PI_OUTPUT_PATH_CHECKED_SUPPORTS_OPEN'
    for path,digest in route['source_sha256'].items():assert sha(ROOT/path)==digest,path
    assert not MODEL.exists() and not PROOF.exists(),'Receive existing native result before rebuilding'
    # Allocate the WHOLE mount, fastening and removal path before features.
    grips=route['splice']['required_independent_grips']
    z=grips[0]['centre_mm'][2]-2 # flat tangent at factory insulation bottom
    anchors=[-55.,31.] # casing gaps[-57.5,-52.5] and[26.5,35]
    plan=dict(status='PI_TWO_SEAT_SHARED_PLAN',selected=False,physical_pass=False,
        source_route='source-output-plan.json',rail_top_world_z_mm=93,
        anchors_x_mm=anchors,foot_y_mm=[69,73],foot_width_x_mm=4,
        seats=grips,beam_bounds_mm=[-67,67,z-2,33,73,z],
        rail_attachment='Two replaceable T18I through new inner-lip slots; no tie crosses any WAGO lever',
        wire_attachment='One independent T18I on each9mm intact insulation seat; no load on joint/shrink',
        added_ties=4,added_screws=0,new_electrical_connectors_or_splices=0,
        changed_rail='Same editable rail master, two extra upper inner-lip slots per rail; other rail slots unused',
        removal='Cut2wire ties and2rail ties; slide complete saddle+Y35mm beneath unchanged fixed wires, through casing gaps; then lift off. No74WAGO routine disconnects',
        assumptions=['Nominal T18I width2.5/thickness1.1/head6 not a delivered fit or force rating',
            'Actual wire OD/shrink profile and no-crush/pull/creep checks after delivery',
            'Chosen ports/whole harness/5FHAC holder mounts remain unselected'],
        whole_stage_completed=False)
    (OUT/'pi-wire-support-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    paths=[CURRENT,OUT/'source-output-plan.json',OUT/'pi-wire-support-plan.json',BASE/'OpenPrototypePlan.FCStd',
        ROOT/'tools/cad/open_deck_p0_supports.py',ROOT/'tools/cad/open_deck_p0_plate.py',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    d=A.openDocument(str(CURRENT));ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
    p=d.Parameters;p.addProperty('App::PropertyLength','SpliceSeatThickness');p.SpliceSeatThickness=2
    p.addProperty('App::PropertyLength','SpliceSeatTop');p.SpliceSeatTop=z
    p.addProperty('App::PropertyLength','SpliceTieSlotWidth');p.SpliceTieSlotWidth=3.5
    # Retain native history; no frozen Boolean rail replacement.
    rail=d.SideDistributionRail
    sk=sketch(rail,'SpliceRailTiePlan','Parameters.SideRailRise+Parameters.SideRailThickness')
    for x in anchors:rect(sk,x-1.75,-13.2,3.5,1.7,'Parameters.SpliceTieSlotWidth')
    rail.Tip=feature(rail,'Pocket','SpliceRailTieClearance',sk,'Parameters.SideRailThickness')
    b=d.addObject('PartDesign::Body','PiSpliceInsulationSaddle')
    b.addProperty('App::PropertyString','Qualification');b.Qualification='Provisional PETG wire strain mount; delivered no-crush and pull/creep gates OPEN'
    # Start from the shared top beam; reverse posts meet it before separate
    # feet are padded. Every intermediate Body remains ONE connected solid.
    sk=sketch(b,'SpliceBeamOutline','Parameters.SpliceSeatTop-Parameters.SpliceSeatThickness')
    rect(sk,-67,67,100,6)
    b.Tip=feature(b,'Pad','SpliceBeam',sk,'Parameters.SpliceSeatThickness')
    sk=sketch(b,'SplicePostOutline','Parameters.SpliceSeatTop-Parameters.SpliceSeatThickness')
    for x in anchors:rect(sk,x-2,69,4,4)
    f=feature(b,'Pad','SplicePosts',sk,'Parameters.SpliceSeatTop-Parameters.SpliceSeatThickness-95 mm')
    f.Reversed=True;b.Tip=f;d.recompute()
    sk=sketch(b,'SpliceFootOutline',93)
    for x in anchors:rect(sk,x-2,69,4,4)
    b.Tip=feature(b,'Pad','SpliceFeet',sk,2)
    sk=sketch(b,'SpliceWireSeatOutline','Parameters.SpliceSeatTop-Parameters.SpliceSeatThickness')
    for g in grips:rect(sk,g['centre_mm'][0]-4.5,53.5,9,15.5)
    b.Tip=feature(b,'Pad','SpliceWireSeats',sk,'Parameters.SpliceSeatThickness')
    sk=sketch(b,'SpliceSmallWireSeat','Parameters.SpliceSeatTop')
    rect(sk,grips[1]['centre_mm'][0]-4.5,53.5,9,6.5)
    b.Tip=feature(b,'Pad','SpliceSmallWireSeatHeight',sk,.7)
    sk=sketch(b,'SpliceWireTiePlan','Parameters.SpliceSeatTop+0.7 mm')
    for g in grips:
        for y in (51.8,60.1):rect(sk,g['centre_mm'][0]-1.75,y,3.5,1.7,'Parameters.SpliceTieSlotWidth')
    # Inner wire-side slots are open edge notches; outer ones pass through
    # the cantilever. The seat has9mm length regardless of tie tightening.
    b.Tip=feature(b,'Pocket','SpliceWireTieClearance',sk,'Parameters.SpliceSeatThickness+0.7 mm')
    sk=sketch(b,'SpliceFootTiePlan',95)
    for x in anchors:rect(sk,x-1.75,71.55,3.5,1.7,'Parameters.SpliceTieSlotWidth')
    b.Tip=feature(b,'Pocket','SpliceFootTieClearance',sk,2)
    def validate():
        d.recompute();rows={}
        for body in (rail,b):
            assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True),body.Name
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in body.Group),body.Name
            assert all(s.FullyConstrained and s.solve()==0 for s in body.Group if s.TypeId=='Sketcher::SketchObject'),body.Name
            rows[body.Name]=dict(volume_mm3=body.Shape.Volume,tip=body.Tip.Name,bounds_mm=bounds(body.Shape))
        return rows
    initial=validate()
    p.SpliceSeatThickness=2.5;changed=validate()
    assert abs(b.Shape.BoundBox.ZMax-(z+.7))<1e-7,'Seat top stays tangent while useful beam/arm thickness changes'
    assert changed[b.Name]['volume_mm3']>initial[b.Name]['volume_mm3']
    p.SpliceSeatThickness=2;restored=validate()
    assert abs(restored[b.Name]['volume_mm3']-initial[b.Name]['volume_mm3'])<1e-5
    # Read-only route references, not pretend-native editable wire histories.
    def route_solid(name,diam,axis):
        edges=[]
        for row in route['centreline_edges'][name]:
            a,c=A.Vector(*row['start_mm']),A.Vector(*row['end_mm'])
            if row['centre_mm'] is None:edges.append(Part.makeLine(a,c))
            else:
                centre=A.Vector(*row['centre_mm']);v=a-centre;w=c-centre
                mid=centre+(v+w)*((v.Length)/(v+w).Length)
                edges.append(Part.Arc(a,mid,c).toShape())
        wire=Part.Wire(edges)
        return wire.makePipeShell([Part.Wire(Part.makeCircle(diam/2,edges[0].Vertexes[0].Point,A.Vector(*axis)))],True,False)
    wires={'W077':route_solid('W077',4,[1,0,0]),'W078':route_solid('W078',2.6,[-1,0,0])}
    j=A.Vector(*route['splice']['factory_insulation_boundary_mm'])
    wires['PiJointShrinkAllowance']=Part.makeCylinder(2.1,20,j+A.Vector(6,0,0),A.Vector(-1,0,0))
    for name,s in wires.items():
        ob=d.addObject('Part::Feature',name+'_RouteReference');ob.Shape=s
        ob.addProperty('App::PropertyString','Qualification');ob.Qualification='Read-only planning sweep; recipe JSON is editable source, not stock selection'
    sources=read(OUT/'source-layout-plan.json')
    from open_prototype_wiring_source_fit import input_path
    neighbours=dict(wires)
    for r in sources['source_plan']:
        box=r['proposed_body_bounds_mm']
        neighbours[r['holder']+'_budget']=Part.makeBox(*(box[i+3]-box[i] for i in range(3)),A.Vector(*box[:3]))
        neighbours[r['holder']+'_input']=input_path(A,Part,r,2)[0]
    material={};reservations={}
    for doc in (d,ctx):
        for ob in doc.Objects:
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull() or ob is b:continue
            if doc is d and (ob.TypeId in ('App::Link','PartDesign::Body') or ob.Name.endswith('NominalPCB') or ob.Name.startswith('BUSsupplier')):
                material[doc.Name+'/'+ob.Name]=ob.Shape
            elif doc is ctx and (ob.Name.startswith(('P0_','S1_ring_','S1_screw_')) or ob.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily')):
                material[doc.Name+'/'+ob.Name]=ob.Shape
            elif ob.Name.endswith('_CP2') and ob.Name!='MAIN4853_CP2' and not ob.Name.startswith(('W0','F_PI_','F_AUX_','F_HP_','F_HY_','F_TY_')):
                if doc is ctx and d.getObject(ob.Name) is not None:continue
                s=ob.Shape.copy()
                if doc is ctx and ob.Name in ('Pi4_CP2','BUS_CP2','PWM9685_CP2','AUX4092_CP2','PWM1608_CP2'):
                    s.translate(A.Vector(0,0,5.72 if ob.Name in ('Pi4_CP2','BUS_CP2') else 4.72))
                reservations[doc.Name+'/'+ob.Name]=s
    for group in (d.NominalMountHardware,d.SideMountHardware,d.U1NominalMountHardware):
        for ob in group.Group:material['hardware/'+ob.Name]=ob.Shape
    contacts=[];errors=[];tested=0
    def check(shape,label,objects):
        nonlocal tested
        for name,s in objects.items():
            if not shape.BoundBox.intersect(s.BoundBox):continue
            tested+=1
            try:
                assert shape.isValid() and s.isValid()
                hit=shape.common(s);assert hit.isValid()
                if hit.Volume>1e-5:contacts.append(dict(a=label,b=name,volume_mm3=hit.Volume,bounds_mm=bounds(hit)))
            except Exception as e:errors.append(dict(a=label,b=name,error=str(e)))
    check(b.Shape,'saddle',dict(material,**neighbours,**reservations))
    # Continuous+Y slide, not just an end-pose or sampled clearance claim.
    travel=A.Vector(0,35,0)
    prisms=[f.extrude(travel) for f in b.Shape.Faces if f.normalAt(0,0).y>.99]
    sweep=b.Shape.multiFuse(prisms).removeSplitter()
    assert sweep.isValid() and len(sweep.Solids)==1
    check(sweep,'saddle_service_slide_Y35',dict(material,**neighbours,**reservations))
    # Explicit physical rail bearing area at BOTH feet, outside WAGO casings.
    bearing=[]
    for x in anchors:
        probe=Part.makeBox(4,4,.05,A.Vector(x-2,69,92.95))
        hit=probe.common(d.SideRail1.Shape);assert hit.isValid()
        assert hit.Volume>.3,'Retained rail material carries each foot, not a floating clamp'
        bearing.append(dict(x_mm=x,contact_area_mm2=hit.Volume/.05))
    mesh=MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and not mesh.hasNonManifolds()
    bb=b.Shape.BoundBox
    assert max(bb.XLength,bb.YLength,bb.ZLength)+10<256
    mesh.write(str(OUT/'PiSpliceInsulationSaddle.stl'))
    d.saveAs(str(MODEL))
    result=dict(status='PI_INDEPENDENT_SADDLE_PREPARATION_CHECKED' if not(contacts or errors) else 'PI_SADDLE_REQUIRES_CHANGE',
        selected=False,stage_completed=False,physical_pass=False,source_sha256=pins,native_sha256=sha(MODEL),
        native_bodies=restored,parameter_trial='SpliceSeatThickness2->2.5->2; seat datum preserved, material changes/restores',
        material_neighbour_or_reservation_contacts=contacts,errors=errors,tested_pairs=tested,bearing= bearing,
        continuous_service_slide_mm=[0,35,0],nominal_wire_ties_and_rail_ties_need_delivered_no_crush_test=True,
        rail_slot_alignment_world_y_mm=[71.55,73.25],
        exporter='Closed support STL,10mm total XY print margin, no slicer/print',
        other_holders_full_wiring_stock_and_native_wire_histories_open=True,
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=time.monotonic()-tick)
    PROOF.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','native_bodies','material_neighbour_or_reservation_contacts','errors','bearing','worker_wall_seconds')}),flush=True)
    A.closeDocument(ctx.Name);A.closeDocument(d.Name)


if __name__=='__main__':main()
