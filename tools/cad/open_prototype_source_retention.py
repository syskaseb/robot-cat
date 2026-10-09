"""Source-family retention: inspect structural owners before native changes."""
import json
import time
import math
import hashlib
from pathlib import Path
import FreeCAD as A
import Part
from open_prototype_wiring_endpoints import ROOT, BASE
from open_prototype_source_receipt import verified_family
from open_prototype_tail_clearance import profiles, wire
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle

OUT = BASE / 'wiring-checkpoint'
MODEL=OUT/'SourceRetentionCurrent.FCStd'


def bracket_capacity():
    """Reject the complete replacement support in the shared scene before CAD."""
    from open_prototype_tail_clearance import box,near
    tick=time.monotonic();p=verified_family();rows=profiles(p)
    rows.update({r['wire']:(r['segments'],r['OD_mm']/2,None,None) for r in p['s1_routes']})
    # North-only cantilever replaces the rejected two-sided bridge. Keep the
    # entire south distribution/heat-shrink corridor free, not a local notch.
    # Architecture change after two rejected sheet bridges: an annular collar
    # and narrow north spine leave the entire fixed TY sleeve gallery open.
    panel=Part.makeCylinder(12,3,A.Vector(126.2,0,112.25)).fuse(Part.makeBox(12,46,3,A.Vector(120.2,0,112.25)))
    panel=panel.cut(Part.makeCylinder(6.25,3,A.Vector(126.2,0,112.25))).cut(Part.makeCylinder(1.5,3,A.Vector(126.2,-9,112.25)))
    solid=panel
    for y in (28,40):
        solid=solid.fuse(Part.makeBox(6,6,34.53,A.Vector(123.2,y-3,77.72)))
        solid=solid.fuse(Part.makeBox(12,12,5,A.Vector(120.2,y-6,77.72)))
    contacts=[];pairs=0
    for row in p['stations']+p['mta']+p['holders']:
        other=box(row['centre_mm'],row['size_mm'])
        if near(solid,other,0):
            v=solid.common(other).Volume;pairs+=1
            if v>1e-6:contacts.append(dict(a='north_cantilever',b=row['role'],volume_mm3=v))
    for n,(parts,r,_,_) in rows.items():
        curve=wire(parts)
        if near(curve,solid,r):
            d=curve.distToShape(solid)[0];pairs+=1
            if d<r-1e-6:contacts.append(dict(a=n,b='north_cantilever',distance_mm=d,required_mm=r))
    result=dict(status='REJECTED' if contacts else 'NORTH_CANTILEVER_CAPACITY_ONLY',contacts=contacts,pairs=pairs,
                anchors_xy_mm=[[126.2,28],[126.2,40]],worker_seconds=time.monotonic()-tick,
                whole_source_retention_complete=False,selected=False)
    (OUT/'source-retention-capacity.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_sources():
    """Matched S1 bracket/receiving plate, historical files remain read-only."""
    from open_prototype_common_source_platform import polygon
    from open_prototype_shared_distribution_carriers import validate
    from open_prototype_source_ato_radius import point_at
    from open_prototype_tail_clearance import box, near
    tick=time.monotonic();family=verified_family()
    inputs=[OUT/'CommonMtaMounts.FCStd',BASE/'OpenPrototypePlan.FCStd',
            OUT/'source-current-receipt.json',
            ROOT/'hardware/reference/manual-stop-p0-2026-09-24/S821-A120.png',
            ROOT/'hardware/reference/manual-stop-p0-2026-09-24/NKK-hardware-C91.png',
            OUT/'SharedDistributionCarriers.FCStd',Path(__file__)]
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in inputs}
    old=A.openDocument(str(inputs[0]));ctx=A.openDocument(str(inputs[1]))
    rails=A.openDocument(str(OUT/'SharedDistributionCarriers.FCStd'))
    doc=A.newDocument('SourceRetentionCurrent')
    report=dict(status='PENDING',selected=False,physical_pass=False,
        source_retention_checkpoint_complete=False,source_sha256=pins,
        scope='Changed S1 panel/UpperCarrier only. Four moved MTA supports, P_REAR,14wire restraints and whole wiring remain OPEN.',
        contacts=[],errors=[],pairs=0,unresolved_prior_carrier_interfaces=[])
    try:
        carrier=doc.copyObject(old.UpperCarrier,True);doc.recompute()
        params=doc.addObject('App::VarSet','RetentionParameters')
        params.addProperty('App::PropertyLength','PanelThickness');params.PanelThickness=3
        params.addProperty('App::PropertyString','SupplierDatum')
        params.SupplierDatum='NKK Series S A120: M12P1;12.5bore;3key at9pitch;panelmax4.5. Mount pose/case budget require delivery fit.'
        # Both anchor feet bear fully on new ears, not partly outside the plate.
        sk=sketch(carrier,'S1AnchorEarsPlan',74.72)
        rect(sk,120.2,22,12,24)
        carrier.Tip=feature(carrier,'Pad','S1AnchorEars',sk,3)
        # Known source path crosses above the AUX board's north edge, not its PCB.
        sk=sketch(carrier,'SourcePassagesPlan',90.02)
        rect(sk,30,16,13,10)
        rect(sk,113.7,-21.5,25,43)
        # Preserve the PCB post field; release only the relocated F_PI case lip.
        rect(sk,-13.625,-28,21.25,2.5)
        carrier.Tip=feature(carrier,'Pocket','SourcePassages',sk,18.3)
        sk=sketch(carrier,'S1AnchorBoresPlan',77.72)
        for y in (28,40):circle(sk,126.2,y,3.4)
        carrier.Tip=feature(carrier,'Pocket','S1AnchorBores',sk,3)
        body=doc.addObject('PartDesign::Body','S1Bracket')
        sk=sketch(body,'S1PanelPlan',112.25);circle(sk,126.2,0,24)
        body.Tip=feature(body,'Pad','S1Panel',sk,'RetentionParameters.PanelThickness')
        sk=sketch(body,'S1SpinePlan',112.25);rect(sk,120.2,0,12,46)
        body.Tip=feature(body,'Pad','S1Spine',sk,'RetentionParameters.PanelThickness')
        sk=sketch(body,'S1LegsPlan',77.72)
        for y in (25,37):rect(sk,123.2,y,6,6)
        body.Tip=feature(body,'Pad','S1Legs',sk,34.53)
        sk=sketch(body,'S1FeetPlan',77.72)
        rect(sk,120.2,22,12,24)
        body.Tip=feature(body,'Pad','S1Feet',sk,5)
        # Backup nut2mm +locking ring1mm below panel; supplied hardware reused.
        sk=sketch(body,'S1SupplierPanelCutoutPlan','112.25 mm + RetentionParameters.PanelThickness')
        circle(sk,126.2,0,12.5);circle(sk,126.2,-9,3)
        body.Tip=feature(body,'Pocket','S1SupplierPanelCutout',sk,'RetentionParameters.PanelThickness')
        sk=sketch(body,'S1FootScrewsPlan',82.72)
        for y in (28,40):circle(sk,126.2,y,3.4)
        body.Tip=feature(body,'Pocket','S1FootScrews',sk,5)
        sk=sketch(body,'S1CaptiveNutsPlan',77.72)
        for y in (28,40):polygon(sk,126.2,y,5.8)
        cut=feature(body,'Pocket','S1CaptiveNuts',sk,2.6);cut.Reversed=True;body.Tip=cut
        matched_rails=[]
        for side,y,h in [('Left',10.5,35.5),('Right',-29.5,19)]:
            rail=doc.copyObject(rails.getObject(side+'DistributionCarrier'),True)
            doc.recompute()
            # Remove the obsolete G2/D_RR station pads and their unnecessary
            # inward branch, not a load-bearing lower beam or frame bolt boss.
            # All4oldMTA added roots are absent because their cases have moved.
            sk=sketch(rail,side+'RetiredStationPlan',113.01);rect(sk,98,y,30,h)
            rail.Tip=feature(rail,'Pocket',side+'RetiredStationRelease',sk,4)
            matched_rails.append(rail)
        native=[carrier,body]+matched_rails
        base=validate(doc,native)
        params.PanelThickness=3.5;changed=validate(doc,native)
        assert changed['S1Bracket']>base['S1Bracket']
        assert abs(changed['UpperCarrier']-base['UpperCarrier'])<1e-7
        params.PanelThickness=3;restored=validate(doc,native)
        assert all(abs(base[n]-restored[n])<1e-7 for n in base)
        # Build only changed sources. Case models and existing proofs stay pinned.
        source=family['s1_module'];case=ctx.S1_body_CP2.Shape.copy()
        case.rotate(A.Vector(*source['pivot_mm']),A.Vector(1,0,0),source['whole_rotation_deg'])
        case.translate(A.Vector(*source['translation_mm']))
        def material(a,s,b,t):
            if not near(s,t,0):return
            assert s.isValid() and t.isValid(),(a,b)
            v=s.common(t).Volume;report['pairs']+=1
            if v>1e-6:report['contacts'].append(dict(a=a,b=b,volume_mm3=v))
        material('UpperCarrier',carrier.Shape,'S1Bracket',body.Shape)
        for rail in matched_rails:material('S1Bracket',body.Shape,rail.Name,rail.Shape)
        for ob in (carrier,body):
            material(ob.Name,ob.Shape,'S1_case',case)
            for row in family['stations']+family['mta']+family['holders']:
                before=len(report['contacts'])
                material(ob.Name,ob.Shape,row['role'],box(row['centre_mm'],row['size_mm']))
                if ob==carrier and row['role']=='D_RL' and len(report['contacts'])>before:
                    # Explicit unresolved dependency, not a clearance waiver.
                    report['unresolved_prior_carrier_interfaces'].append(report['contacts'].pop())
        # Static boundary check for the changed bracket; plate boundary previously qualified.
        outside=body.Shape.cut(ctx.TorsoEnvelope.Shape).Volume
        if outside>1e-6:report['contacts'].append(dict(a='S1Bracket',b='outside_torso',volume_mm3=outside))
        rows=profiles(family)
        rows.update({r['wire']:(r['segments'],r['OD_mm']/2,None,None) for r in family['s1_routes']})
        for name,(parts,r,_,_) in rows.items():
            curve=wire(parts)
            for ob in (carrier,body):
                if not near(curve,ob.Shape,r):continue
                distance=curve.distToShape(ob.Shape)[0];report['pairs']+=1
                if distance<r-1e-6:report['contacts'].append(dict(a=name,b=ob.Name,distance_mm=distance,required_mm=r))
        # Inspect current component allowances, actual mounting fastener access,
        # and all original holes rather than assuming the cut preserves mounting.
        scene=json.loads((OUT/'obstacle-map-current.json').read_text())['objects']
        for row in scene:
            if row['kind']!='delivery_reservation':continue
            v=row['bounds_mm'];shape=box([(v[i]+v[i+3])/2 for i in range(3)],[v[i+3]-v[i] for i in range(3)])
            material('S1Bracket',body.Shape,row['name'],shape)
            # The old plate already has PCB mounting/board interfaces; only the
            # new S1 anchor ears are tested against board allowances here.
            material('new_ear',Part.makeBox(12,24,3,A.Vector(120.2,22,74.72)),row['name'],shape)
        hardware=[]
        for i,y in enumerate((28,40)):
            shaft=Part.makeCylinder(1.5,8,A.Vector(126.2,y,74.22))
            head=Part.makeCylinder(2.85,3,A.Vector(126.2,y,71.22))
            screw=shaft.fuse(head)
            washer=Part.makeCylinder(3.5,.5,A.Vector(126.2,y,74.22)).cut(Part.makeCylinder(1.6,.5,A.Vector(126.2,y,74.22)))
            for name,shape in [('Screw',screw),('Washer',washer)]:
                ref=doc.addObject('Part::Feature',f'S1Mount{i}{name}');ref.Shape=shape;hardware.append(ref)
                for ob in (carrier,body):material(ref.Name,shape,ob.Name,ob.Shape)
            tool=Part.makeCylinder(3,50,A.Vector(126.2,y,21.22))
            material('S1_driver',tool,'S1_case',case)
            for name,(parts,r,_,_) in rows.items():
                curve=wire(parts)
                if near(curve,tool,r):
                    d=curve.distToShape(tool)[0];report['pairs']+=1
                    if d<r-1e-6:report['contacts'].append(dict(a=name,b='S1_driver',distance_mm=d,required_mm=r))
        report.update(native_volumes_mm3=base,parameter_mm=[3,3.5,3],parameter_restored=True,
            replaced_native_supports=['LeftDistributionCarrier','RightDistributionCarrier'],
            retired_support_interfaces=['oldG2pad','oldD_RRpad','old4MTAaddedroots'],
            current_four_MTA_mounts_still_open=True,
            candidate_hardware={'M3x8':2,'M3_washer':2,'M3_nut':2},
            supplier_hardware_reused=['AT503M','AT506M','AT508','AT527M'],
            delivery_gates=['S821case/bushingdatum','locking_ring_orientation','PETGcreep/clamp','nut/tool/lead actual fit'],
            panel_bounds_mm=[24,58,37.53],worker_seconds=time.monotonic()-tick)
        doc.recompute()
        report['status']='REJECTED_CHANGED_INTERFACE' if report['contacts'] else 'S1_CHANGED_NATIVE_INTERFACES_PREPARED_NOT_WHOLE_SOURCE_RETENTION'
        # Even a rejected native candidate is preserved with explicit status,
        # never installed as a selected model or an accepted STL.
        doc.saveAs(str(MODEL))
        report['model_sha256']=sha(MODEL)
    except Exception as exc:
        report['errors'].append(str(exc));report['status']='ERROR_NOT_ACCEPTED';raise
    finally:
        for d in (doc,old,rails,ctx):A.closeDocument(d.Name)
        assert all(sha(ROOT/n)==h for n,h in pins.items())
        report['worker_seconds']=time.monotonic()-tick
        (OUT/'source-retention-checks.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report),flush=True)


def support_plan():
    """One structural proposal, checked before creating a feature tree."""
    from open_prototype_source_ato_radius import point_at
    p=verified_family(); rows=profiles(p)
    rows.update({r['wire']:(r['segments'],r['OD_mm']/2,None,None) for r in p['s1_routes']})
    doc=A.openDocument(str(OUT/'CommonMtaMounts.FCStd'))
    ctx=A.openDocument(str(BASE/'OpenPrototypePlan.FCStd'))
    try:
        plate=doc.UpperCarrier.Shape
        source=p['s1_module'];case=ctx.S1_body_CP2.Shape.copy()
        case.rotate(A.Vector(*source['pivot_mm']),A.Vector(1,0,0),source['whole_rotation_deg'])
        case.translate(A.Vector(*source['translation_mm']))
        crossings=[]
        parts=rows['W064'][0]
        for seg in parts:
            length=wire([seg]).Length
            for i in range(int(length/.5)+1):
                pt=point_at(seg,min(i*.5,length))
                if plate.isInside(A.Vector(*pt),1e-7,True):crossings.append(pt)
        features=[dict(name=o.Name,type=o.TypeId,
                      bounds=[getattr(o.Shape.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
                  for o in doc.UpperCarrier.Group if hasattr(o,'Shape') and o.TypeId.startswith('PartDesign::')]
        result=dict(s1_previous_plate_overlap_mm3=case.common(plate).Volume,
            W064_plate_centreline_points=crossings,upper_native_features=features,
            proposed_s1_anchor_xy_mm=[[126.2,-30],[126.2,30]],
            proposed_panel_z_mm=[109.25,112.25],
            source_retention_checkpoint_complete=False,selected=False)
        (OUT/'source-retention-structural-plan.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:
        A.closeDocument(doc.Name);A.closeDocument(ctx.Name)


def native_preflight():
    """Compare new source family with the actual previous native carriers."""
    tick=time.monotonic(); p=verified_family(); rows=profiles(p)
    rows.update({r['wire']:(r['segments'],r['OD_mm']/2,None,None) for r in p['s1_routes']})
    doc=A.openDocument(str(OUT/'CommonMtaMounts.FCStd'))
    result=dict(scope='CURRENT_SOURCE_VERSUS_PREVIOUS_NATIVE_SUPPORTS_ONLY',
                contacts=[], pairs=0, errors=[], selected=False, physical_pass=False)
    try:
        bodies=[o for o in doc.Objects if o.TypeId=='PartDesign::Body']
        for name in ('W064','W065','W067','W068','W044','W052','F_AUX/input'):
            parts,radius,_,_=rows[name]; curve=wire(parts)
            for body in bodies:
                b=curve.BoundBox; b.enlarge(radius)
                if not b.intersect(body.Shape.BoundBox): continue
                assert body.Shape.isValid(),body.Name
                result['pairs']+=1
                distance=curve.distToShape(body.Shape)[0]
                if distance<radius-1e-6:
                    result['contacts'].append(dict(wire=name,body=body.Name,
                         distance_mm=distance,required_mm=radius))
        result['status']='PREVIOUS_NATIVE_SUPPORTS_REQUIRE_SHARED_REPLACEMENT' if result['contacts'] else 'SCOPED_NATIVE_SOURCE_GATE_CLEAR'
    finally:
        A.closeDocument(doc.Name)
    result['worker_seconds']=time.monotonic()-tick
    (OUT/'source-retention-native-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


def inspect():
    tick = time.monotonic()
    docs = []
    try:
        for path in (OUT / 'CommonMtaMounts.FCStd',
                     BASE / 'mounting-checkpoint/RetentionMountsAssembly.FCStd',
                     BASE / 'OpenPrototypePlan.FCStd'):
            doc = A.openDocument(str(path)); docs.append(doc)
            rows = []
            for obj in doc.Objects:
                if obj.TypeId not in ('PartDesign::Body', 'App::Link') and not obj.Name.startswith(('S1_', 'P0_Frame', 'UpperCarrier')):
                    continue
                if not hasattr(obj, 'Shape') or obj.Shape.isNull():
                    continue
                b = obj.Shape.BoundBox
                rows.append(dict(name=obj.Name, type=obj.TypeId,
                                 bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                                 valid=obj.Shape.isValid()))
            print(json.dumps(dict(file=path.relative_to(ROOT).as_posix(), objects=rows)),flush=True)
    finally:
        for doc in docs:
            A.closeDocument(doc.Name)
    print(json.dumps(dict(inspect_seconds=time.monotonic()-tick)),flush=True)


if __name__ == '__main__':
    import sys
    if '--preflight' in sys.argv:native_preflight()
    elif '--plan' in sys.argv:support_plan()
    elif '--build' in sys.argv:native_sources()
    elif '--capacity' in sys.argv:bracket_capacity()
    else:inspect()
