"""One coupled mount: retain neck axes, support MAIN from the left riser.

The board sits 4 mm above a 3 mm cantilever, not on a floating reservation.
Supplier family geometry/hole axes are reused, exact delivered PCB still open.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'hardware/cad/studies/whole-cat-packaging/cp2'
NECK = BASE/'neck-support/coupled'
SEQUENCE = '--assembly-sequence' in sys.argv
OUT = BASE/('neck-support/main-mount-sequence' if SEQUENCE else 'neck-support/main-mount')
SOURCE = BASE/'BoardDatumCandidate.FCStd'
FAMILY = ROOT/'hardware/cad/studies/main-p0-mount/r5/MainP0Mount.FCStd'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import FreeCAD as A
    import Part
    import Mesh
    import MeshPart
    from open_deck_p0_supports import sketch, feature, circles
    from open_deck_p0_plate import rect
    assert not OUT.exists(), 'Preserve saved result, no unchanged retries'
    tick=time.monotonic(); started=datetime.now(timezone.utc).isoformat()
    sources=[SOURCE, NECK/'NeckRisers.FCStd', NECK/'checks.json', FAMILY,
             BASE/'board-datums-checks.json', BASE/'whole-harness-board-plan.json',
             ROOT/'hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    prior=json.loads(sources[2].read_text(encoding='utf-8'))
    assert sha(sources[1])==prior['native_sha256']
    src=A.openDocument(str(SOURCE)); doc=A.openDocument(str(sources[1])); family_doc=A.openDocument(str(FAMILY))
    try:
        main_ref=src.getObject('MAIN4853_CP2')
        main_ref.Placement.Base += A.Vector(34,0,4.52)
        p=doc.Parameters
        for name,value in [('MainGap',4),('MainBoardThickness',1.5748)]:
            p.addProperty('App::PropertyLength',name);setattr(p,name,value)
        left=doc.getObject('LeftRiser'); right=doc.getObject('RightRiser')
        sk=sketch(left,'MainCantileverPlan',1)
        rect(sk,-65,20.021,35,6.6)
        left.Tip=feature(left,'Pad','MainCantilever',sk,3);doc.recompute()
        axes=[(-52.701,23.321),(-34.159,23.321)]
        sk=sketch(left,'MainPostsPlan',4);circles(sk,axes,5.8)
        left.Tip=feature(left,'Pad','MainPosts',sk,'Parameters.MainGap');doc.recompute()
        sk=sketch(left,'MainBoltBores','4 mm+Parameters.MainGap');circles(sk,axes,2.6)
        left.Tip=feature(left,'Pocket','MainBoltClearance',sk,'3 mm+Parameters.MainGap');doc.recompute()
        # Under the cantilever: 0.3 washer + M2 nut. Keep the bearing surface
        # flat and leave the nut exposed for a side key; no captive-nut fantasy.
        ref=family_doc.getObject('SupplierFamilyReference').Shape.copy()
        low=json.loads(sources[4].read_text(encoding='utf-8'))['MAIN_frame']['mounted_family_bbox_min_mm']
        assert math.dist(low,[-17.24,-9.43,9])<1e-6
        ref.translate(A.Vector(*[-v for v in low]))
        ref.transformShape(main_ref.Placement.toMatrix())
        assert ref.isValid()
        old_ref=doc.getObject('MAIN4853_CP2');old_ref.Shape=main_ref.Shape.copy()
        supplier=doc.addObject('Part::Feature','MainSupplierFamily');supplier.Shape=ref
        supplier.setExpression('Placement.Base.z','Parameters.MainGap-4 mm')
        old_ref.setExpression('Placement.Base.z','Parameters.MainGap-4 mm')
        doc.RetainedReferences.addObject(supplier)
        def validate():
            doc.recompute();s=left.Shape
            assert left.Tip.Shape.isValid() and len(left.Tip.Shape.Solids)==1
            assert all('Invalid' not in o.State and 'Touched' not in o.State for o in left.Group)
            assert abs(doc.MainBoltBores.Placement.Base.z-(4+p.MainGap.Value))<1e-6
            assert abs(doc.MainBoltClearance.Length.Value-(3+p.MainGap.Value))<1e-6
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            sketches=[o for o in left.Group if o.TypeId=='Sketcher::SketchObject']
            assert all(o.FullyConstrained and o.solve()==0 for o in sketches)
            return dict(volume_mm3=s.Volume,fully_constrained_sketches=len(sketches))
        baseline=validate();assert baseline['volume_mm3']>prior['parts'][0]['volume_mm3']+500
        baseline_board_z=supplier.Shape.BoundBox.ZMin
        p.MainGap=5;changed=validate()
        if '--diagnose-parameters' in sys.argv:
            print('PARAMETER_DIAG',baseline,changed,'gap',p.MainGap,
                  'posts',doc.MainPosts.Length,'pocket',doc.MainBoltClearance.Length,
                  'tip',left.Tip.Name,'posts_base',doc.MainPosts.BaseFeature,
                  'pocket_base',doc.MainBoltClearance.BaseFeature,
                  'post_sketch_z',doc.MainPostsPlan.Placement.Base.z,
                  'pocket_sketch_z',doc.MainBoltBores.Placement.Base.z,
                  'post_state',doc.MainPosts.State,
                  'pocket_state',doc.MainBoltClearance.State,
                  'pocket_status',doc.MainBoltClearance.getStatusString(),
                  'board_z',supplier.Shape.BoundBox.ZMin,flush=True)
            return
        assert changed['volume_mm3']>baseline['volume_mm3']
        assert abs(supplier.Shape.BoundBox.ZMin-baseline_board_z-1)<1e-6
        assert left.Shape.common(supplier.Shape).Volume<1e-5
        p.MainGap=4;restored=validate()
        assert abs(restored['volume_mm3']-baseline['volume_mm3'])<1e-6
        hardware={};hardware_meta=[];bearing=[]
        zboard=46.52;underhead=zboard+1.5748+.3
        for i,(x,y) in enumerate(axes):
            shaft=Part.makeCylinder(1,12,A.Vector(x,y,underhead),A.Vector(0,0,-1))
            head=Part.makeCylinder(1.9,2,A.Vector(x,y,underhead))
            washers=[Part.makeCylinder(2.5,.3,A.Vector(x,y,z)).cut(
                      Part.makeCylinder(1.1,.3,A.Vector(x,y,z))) for z in (zboard+1.5748,39.22)]
            nut=Part.makeCylinder(4/math.sqrt(3),1.6,A.Vector(x,y,37.62)).cut(
                Part.makeCylinder(1,1.6,A.Vector(x,y,37.62)))
            for label,shape in [('shaft',shaft),('head',head),('upper_washer',washers[0]),('lower_washer',washers[1]),('nut',nut)]:
                hardware[f'MAIN_{i}_{label}']=shape
            protrusion=37.62-(underhead-12);assert protrusion>=.4
            hardware_meta.append(dict(axis_mm=[x,y],screw='0912A2-M020X012VISK',L_mm=12,
                                      underhead_z_mm=underhead,tip_z_mm=underhead-12,
                                      nut_thread_length_mm=1.6,protrusion_mm=protrusion))
            annulus=Part.makeCylinder(2.5,.05,A.Vector(x,y,39.52)).cut(
                Part.makeCylinder(1.31,.05,A.Vector(x,y,39.52)))
            fraction=left.Shape.common(annulus).Volume/annulus.Volume
            assert abs(fraction-1)<1e-6;bearing.append(fraction)
        targets={'LeftRiserWithMain':left.Shape,'MainSupplierFamily':ref,**hardware}
        material={o.Name:o.Shape for o in src.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
                  and (o.Name.startswith(('P0_','Head_','Tail','MTA_','F_','W0','XA','Factory_','Joint_'))
                       or o.Name.endswith('_CP2')) and o.Name!='MAIN4853_CP2'}
        material['RightRiser']=right.Shape
        # Exclude the 12mm tall reservation from material contact checks;
        # the supplier family, not its conservative box, is now tested.
        contacts=[];errors=[];tested=0
        pairs=[(name,shape,oname,other) for name,shape in targets.items() for oname,other in material.items()]
        names=list(targets)
        pairs += [(n,targets[n],m,targets[m]) for i,n in enumerate(names) for m in names[i+1:]]
        for name,s,oname,t in pairs:
            if not s.BoundBox.intersect(t.BoundBox):continue
            tested+=1
            try:
                assert s.isValid() and t.isValid()
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:contacts.append(dict(a=name,b=oname,volume_mm3=hit.Volume))
            except Exception as exc:errors.append(dict(a=name,b=oname,error=str(exc)))
        tools=[]
        for i,(x,y) in enumerate(axes):
            # Applied before wires; head driver vertical and nut key from +Y.
            probes=[('top_driver',Part.makeCylinder(1.5,35,A.Vector(x,y,underhead+2))),
                    ('nut_socket_below',Part.makeCylinder(3,17.62,A.Vector(x,y,20)))
                    if SEQUENCE else ('nut_key_side',Part.makeBox(6,32,1.8,A.Vector(x-3,y,37.52)))]
            for label,probe in probes:
                hits=[]
                for n,t in {**material,'LeftRiserWithMain':left.Shape,'MainSupplierFamily':ref}.items():
                    if SEQUENCE and label=='top_driver' and n=='S0_body_CP2':continue
                    if not probe.BoundBox.intersect(t.BoundBox):continue
                    hit=probe.common(t);assert hit.isValid()
                    if hit.Volume>1e-5:hits.append(dict(part=n,volume_mm3=hit.Volume))
                tools.append(dict(id=f'{i}_{label}',contacts=hits))
        graph=json.loads(sources[5].read_text(encoding='utf-8'));ends=[]
        for row in graph['body_conductors']:
            for e in row['ends']:
                if e.get('native')=='MAIN4853_CP2':
                    q=e['point_mm'];ends.append(dict(id=row['id'],role=e['role'],old_point_mm=q,
                        point_mm=[q[0]+34,q[1],q[2]+4.52],departure=e['departure'],route_restraint_status='OPEN'))
        assert {e['id'] for e in ends}=={'W060','W078','W079','W080'}
        report=dict(status='COUPLED_MAIN_MOUNT_CLEAR' if not(contacts or errors or any(t['contacts'] for t in tools)) else 'COUPLED_MAIN_MOUNT_REJECTED',
            selected=False,M2_complete=False,W5_complete=False,physical_pass=False,source_sha256=pins,
            main_translation_from_board_datum_mm=[34,0,4.52],geometry=baseline,exact_pairs_tested=tested,
            contacts=contacts,errors=errors,hardware=hardware_meta,lower_washer_bearing_fractions=bearing,
            tool_checks=tools,tool_budget_basis='D3x35 driver and D6 socket below before wiring/S0; design allowance, not physical tool qualification' if SEQUENCE else 'D3x35 driver and6x1.8 side-key design allowance, not physical tool qualification',
            assembly=['Risers on bare P0 frame; MAIN pre-soldered on bench',
                      'Place MAIN on integral posts; M2x12/washer from above, washer/nut/socket from below',
                      'Install S0 only after MAIN bolts; retain MAIN leads clear of driver until tightening',
                      'Whole robot sequence and S0 access remain OPEN'],
            S0_intentionally_absent_during_top_driver=SEQUENCE,
            affected_main_ends=ends,parameter_roundtrip_mm=[4,5,4],
            board_follows_gap_parameter=True,
            stock_delta_candidates={'M2x12':2,'M2_nuts':2,'OD5_washers':4,'additional_prints':0,'replaced_left_riser':1},
            remaining=['Full 4 MAIN routes and native strain relief','Full head motion/wiring and current selection',
                       'Actual PCB component population and measured PETG fit/load/thermal tests phase2'],
            started_utc=started)
        OUT.mkdir(parents=True)
        if report['status']=='COUPLED_MAIN_MOUNT_CLEAR':
            for ob in left.Group:
                if ob.ViewObject:ob.Visibility=False
            if left.ViewObject:left.Visibility=True
            doc.saveAs(str(OUT/'NeckMainMount.FCStd'))
            report['native_sha256']=sha(OUT/'NeckMainMount.FCStd')
            shape=left.Shape.copy();b=shape.BoundBox;shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
            stl=OUT/'LeftRiserWithMain_candidate.stl'
            MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False).write(str(stl))
            mesh=Mesh.Mesh(str(stl));assert mesh.isSolid() and mesh.countComponents()==1
            bounds=[mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength];assert max(bounds)<256
            report['stl']=dict(path=stl.relative_to(ROOT).as_posix(),sha256=sha(stl),print_size_with_5mm_brim_mm=bounds)
            A.closeDocument(doc.Name);doc=A.openDocument(str(OUT/'NeckMainMount.FCStd'));left=doc.LeftRiser;p=doc.Parameters
            fresh=validate();assert abs(fresh['volume_mm3']-baseline['volume_mm3'])<1e-6
            report['saved_reopen_verified']=True
        assert all(sha(ROOT/path)==h for path,h in pins.items())
        report.update(finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=round(time.monotonic()-tick,3))
        (OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(report['status'],tested,'pairs',contacts,errors,tools,flush=True)
    finally:
        A.closeDocument(doc.Name);A.closeDocument(src.Name);A.closeDocument(family_doc.Name)


if __name__=='__main__':main()
