"""Two native neck risers on existing P0 axes; one bounded candidate.

Replace the removed cassette's front feet, not the robot frame. Existing
foundation moves as a whole with the accepted head. No electrical placement
or selected manufacturing package is changed by this local study.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'hardware/cad/studies/whole-cat-packaging/cp2'
OUT = BASE/'neck-support'
SOURCE = BASE/'BoardDatumCandidate.FCStd'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import FreeCAD as A
    import Part
    import Mesh
    import MeshPart
    from open_deck_p0_supports import sketch, feature, circles
    from open_deck_p0_plate import rect

    started = datetime.now(timezone.utc); tick = time.monotonic()
    assert not OUT.exists(), 'Preserve result; do not repeat an unchanged candidate'
    source_files = [SOURCE, Path(__file__), BASE.parent/'layout.json',
        ROOT/'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json',
        ROOT/'hardware/cad/studies/head-p7/base-r1/checks.json']
    pins = {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files}
    layout = json.loads(source_files[2].read_text(encoding='utf-8'))
    assert layout['params_mm']['HeadForward'] == 42 and layout['params_mm']['HeadRaise'] == 25
    prior = json.loads(source_files[4].read_text(encoding='utf-8'))
    assert prior['fit']['stack']['underhead_z_mm'] == 35.22
    src = A.openDocument(str(SOURCE))
    doc = A.newDocument('WholeCatNeckRisers')
    try:
        params = doc.addObject('App::VarSet','Parameters')
        for name, value in [('HeadForward',42),('HeadRaise',25),('FootThickness',4)]:
            params.addProperty('App::PropertyLength',name); setattr(params,name,value)
        bodies = []
        for side, y in [('Left',22.5),('Right',-22.5)]:
            body = doc.addObject('PartDesign::Body',side+'Riser')
            body.Placement.Base.z = 38.52
            sk = sketch(body,side+'FootPlan',0); rect(sk,-90,y-5,30,10)
            feature(body,'Pad',side+'Foot',sk,'Parameters.FootThickness')
            low = sketch(body,side+'WebBottom','Parameters.FootThickness')
            rect(low,-90,y-5,30,10)
            high = sketch(body,side+'WebTop','Parameters.HeadRaise')
            rect(high,-86,y-5,22,10)
            high.setExpression('Placement.Base.x','-Parameters.HeadForward')
            loft = body.newObject('PartDesign::AdditiveLoft',side+'InclinedWeb')
            loft.Profile = low; loft.Sections = [high]; loft.Ruled = True; doc.recompute()
            sk = sketch(body,side+'UpperFootPlan','Parameters.HeadRaise')
            rect(sk,-86,y-5,22,10)
            sk.setExpression('Placement.Base.x','-Parameters.HeadForward')
            feature(body,'Pad',side+'UpperFoot',sk,'Parameters.FootThickness')
            # Both bolt axes follow the same displacement as the retained foundation.
            sk = sketch(body,side+'UpperBores', 'Parameters.HeadRaise+Parameters.FootThickness')
            sk.setExpression('Placement.Base.x','-Parameters.HeadForward')
            circles(sk,[(-80,y),(-70,y)],2.6)
            feature(body,'Pocket',side+'UpperBoltClearance',sk,12)
            sk = sketch(body,side+'UpperNutAccess','Parameters.HeadRaise')
            sk.setExpression('Placement.Base.x','-Parameters.HeadForward')
            for x in (-80,-70): rect(sk,x-2.8,y-5,5.6,10)
            feature(body,'Pocket',side+'UpperNutPockets',sk,2.4)
            # Existing M2x10 lower stack, accessed on the bare frame before electronics.
            sk = sketch(body,side+'LowerNutAccess',6.8)
            for x in (-80,-70): rect(sk,x-2.8,y-5,5.6,10)
            feature(body,'Pocket',side+'LowerNutPockets',sk,2.8)
            sk = sketch(body,side+'LowerBores',10)
            circles(sk,[(-80,y),(-70,y)],2.6)
            feature(body,'Pocket',side+'LowerBoltClearance',sk,10)
            bodies.append(body)
            for ob in body.Group:
                if ob.ViewObject: ob.Visibility = False
            if body.ViewObject:
                body.Visibility = True; body.ViewObject.ShapeColor = (.90,.45,.12)

        def validate():
            doc.recompute(); rows = []
            for body in bodies:
                assert body.Shape.isValid() and len(body.Shape.Solids)==1,body.Name
                assert not body.Shape.check(True),body.Name
                sketches=[o for o in body.Group if o.TypeId=='Sketcher::SketchObject']
                assert all(s.FullyConstrained and s.solve()==0 for s in sketches)
                b=body.Shape.BoundBox
                assert abs(b.ZMax-(42.52+params.HeadRaise.Value))<1e-7
                rows.append(dict(name=body.Name,volume_mm3=body.Shape.Volume,
                    bounds_mm=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],
                    fully_constrained_sketches=len(sketches)))
            return rows
        baseline=validate()
        params.HeadForward=43;changed=validate()
        assert all(abs(b['volume_mm3']-a['volume_mm3'])>1e-5 for a,b in zip(baseline,changed))
        params.HeadForward=42; restored=validate()
        assert all(abs(a['volume_mm3']-b['volume_mm3'])<1e-6 for a,b in zip(baseline,restored))

        contacts=[]; errors=[]; tested=0
        # Torso/neck planning volumes and service reservations are not material.
        material=[o for o in src.Objects if 'Shape' in o.PropertiesList
            and not o.Shape.isNull() and o.Name not in ('TorsoEnvelope','BatteryNominal','NeckMountReservation')
            and not o.Name.startswith('Access_')
            and (o.Name.startswith(('P0_','Head_','Tail','MTA_','F_','W0','XA','Factory_','Joint_'))
                 or o.Name.endswith('_CP2'))]
        for body in bodies:
            for ob in material:
                if not body.Shape.BoundBox.intersect(ob.Shape.BoundBox): continue
                tested+=1
                try:
                    assert ob.Shape.isValid(), 'Invalid neighbor BRep'
                    common=body.Shape.common(ob.Shape); assert common.isValid()
                    if common.Volume>1e-5:
                        contacts.append(dict(part=body.Name,neighbor=ob.Name,volume_mm3=common.Volume))
                except Exception as err: errors.append(dict(part=body.Name,neighbor=ob.Name,error=str(err)))
        # Verify nominal washer support and all eight shank/nut spaces on the new material.
        washer_bearing=[]; hardware=[]
        for body,y in zip(bodies,[22.5,-22.5]):
            for x in (-80,-70):
                for role,px,underhead,washer_z,nut_z,tip in [
                    ('lower',x,35.22,42.52,42.82,45.22),
                    ('upper',x-42,71.82,63.22,61.62,59.82)]:
                    ring=Part.makeCylinder(2.5,.05,A.Vector(px,y,
                         42.47 if role=='lower' else 63.52)).cut(
                         Part.makeCylinder(1.31,.05,A.Vector(px,y,
                         42.47 if role=='lower' else 63.52)))
                    fraction=body.Shape.common(ring).Volume/ring.Volume
                    assert abs(fraction-1)<1e-6,(body.Name,role,px,fraction)
                    shaft=Part.makeCylinder(1,abs(underhead-tip),A.Vector(px,y,min(underhead,tip)))
                    washer=Part.makeCylinder(2.5,.3,A.Vector(px,y,washer_z)).cut(
                        Part.makeCylinder(1.1,.3,A.Vector(px,y,washer_z)))
                    # Circumscribed nut budget conservatively includes AF4 corners.
                    nut=Part.makeCylinder(4/(3**.5),1.6,A.Vector(px,y,nut_z)).cut(
                        Part.makeCylinder(1,1.6,A.Vector(px,y,nut_z)))
                    hits=[body.Shape.common(s).Volume for s in (shaft,washer,nut)]
                    assert max(hits)<1e-5,(body.Name,role,px,hits)
                    hardware.append(dict(role=role,axis_mm=[px,y],tip_z_mm=tip,
                        screw='M2x10 retained' if role=='lower' else 'M2x12 candidate'))
                    washer_bearing.append(dict(role=role,axis_mm=[px,y],fraction=fraction))
        OUT.mkdir()
        report=dict(status='LOCAL_NECK_RISERS_CLEAR' if not(contacts or errors)
                           else 'LOCAL_NECK_RISERS_REJECTED',
            selected=False,physical_pass=False,M2_complete=False,source_sha256=pins,
            parts=baseline,contacts=contacts,errors=errors,exact_pairs_tested=tested,
            parameter_roundtrip_mm=[42,43,42],hardware=hardware,washer_bearing=washer_bearing,
            lower_anchor_plane_mm=38.52,upper_foundation_plane_mm=67.52,
            installed_candidate_changes={'PETG_risers':2,'additional_M2x12':4,'additional_M2_nuts':4,
                'additional_OD5_washers':8,'lower_M2x10':4,'removed_old_front_cassette_feet':2},
            stock_not_selected=True,
            assembly=['Bare P0 frame: lower bolts from below, washers/nuts through side pockets',
                'Upper nuts/washers through side pockets, then shifted foundation and M2x12 from above',
                'Retained yaw unit onto foundation before shell/electronics; complete robot sequence OPEN'],
            remaining=['Upper hardware vs actual head parts and tool approach',
                'Moving head/body and new complete central harness',
                'PETG load/creep and calibrated fits phase2; complete M2 selection still OPEN'],
            started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3))
        if not(contacts or errors):
            group=doc.addObject('App::DocumentObjectGroup','RetainedReferences')
            for name in ('P0_FrameFront20','Head_Foundation'):
                ref=doc.addObject('Part::Feature',name);ref.Shape=src.getObject(name).Shape.copy();group.addObject(ref)
                if ref.ViewObject: ref.ViewObject.ShapeColor=(.35,.55,.70)
            doc.saveAs(str(OUT/'NeckRisers.FCStd'))
            report['native_sha256']=digest(OUT/'NeckRisers.FCStd')
            meshes=[]
            for body in bodies:
                shape=body.Shape.copy();b=shape.BoundBox
                shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
                file=OUT/(body.Name+'_candidate.stl')
                MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.2,
                    Relative=False).write(str(file))
                mesh=Mesh.Mesh(str(file));assert mesh.isSolid() and mesh.countComponents()==1
                size=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength]
                assert max(size)<256
                meshes.append(dict(path=file.relative_to(ROOT).as_posix(),sha256=digest(file),
                    print_size_with_5mm_brim_mm=size,orientation='Lower foot on bed; support review phase2'))
            report['meshes']=meshes
            A.closeDocument(doc.Name);doc=A.openDocument(str(OUT/'NeckRisers.FCStd'))
            bodies=[doc.getObject(n) for n in ('LeftRiser','RightRiser')];params=doc.Parameters
            assert validate()==baseline
            report['saved_reopen_verified']=True
        assert all(digest(ROOT/p)==h for p,h in pins.items())
        (OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',
                                       encoding='utf-8')
        print(report['status'],tested,'pairs',contacts,errors,report['worker_wall_seconds'],'seconds',flush=True)
    finally:
        A.closeDocument(doc.Name);A.closeDocument(src.Name)


if __name__=='__main__':main()
