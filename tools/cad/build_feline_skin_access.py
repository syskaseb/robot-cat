"""One shared native7portal change; retain4panels and prove material subset.

All7whole portals are driven by one36pose plan, not micro-notches. Cowls,
fasteners, full wire looms and whole exact motion acceptance remain OPEN.
"""
import json,time,sys
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();planfile=OUT/'skin-access-plan.json';plan=json.loads(planfile.read_text())
    assert plan['mesh_poses']==36 and not plan['exact_collision_approval']
    assert all(sha(ROOT/n)==h for n,h in plan['source_sha256'].items())
    mp=OUT/'torso-panels-native.json';m=json.loads(mp.read_text());native=ROOT/m['native'];before=sha(native)
    assert before==m['native_sha256'];reader=SavedShapes()
    original={r['object']:reader.shape(native,r['object']) for r in m['parts']}
    doc=A.openDocument(str(native));doc_name=doc.Name
    report=dict(status='BUILDING_SHARED_NATIVE_SKIN_PORTALS',selected=False,physical_pass=False,
        source_native_sha256=before,portals=[],parts=[],new_material_mm3={},
        full_wiring_complete=False,cowls_complete=False,frame_mounts_complete=False,
        source_sha256={planfile.relative_to(ROOT).as_posix():sha(planfile),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    destination=OUT/'skin-access-native.json'
    previous_access=json.loads(destination.read_text()) if destination.exists() else None
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);destination.write_text(json.dumps(report,indent=2)+'\n')
    try:
        resume=doc.getObject('SharedAccessPortals') is not None
        if resume:
            assert '--extend-from-complete-surface-plan' in sys.argv,'Receive prior result before duplicate changes'
            assert plan.get('sampler')=='FULL_TRIANGLE_SURFACES_MAX_EDGE_2MM'
            assert previous_access and previous_access['native_sha256']==before
            assert previous_access['source_sha256'][planfile.relative_to(ROOT).as_posix()]!=sha(planfile)
            report['previous_access_receipt']=previous_access
        p=doc.Parameters;p.set('A5','BayCornerRadius');p.set('B5','6 mm');p.setAlias('B5','BayCornerRadius')
        recipes=[('Leg_'+r['code'],r['design_box_mm']) for r in plan['leg_bays']]
        recipes += [('Control_'+r['control'],r['design_box_mm']) for r in plan['control_portals']]
        recipes += [('TailRoot',plan['tail_portal']['design_box_mm'])]
        portals=[]
        for name,(low,high) in recipes:
            x0,y0,z0=low;x1,y1,z1=high;w=x1-x0;h=z1-z0;depth=y1-y0
            r=min(6,w/4,h/4);factor=r/6;parts=[]
            # Two cross rectangles and four round corners exactly implement
            # the rounded XZ rectangle, extruded only through this side.
            for i in (0,1):
                b=doc.getObject(name+'Rect'+str(i)) or doc.addObject('Part::Box',name+'Rect'+str(i));b.Width=depth;b.Placement.Base.y=y0
                if i==0:
                    b.setExpression('Length',f'{w:.15g} mm - Parameters.BayCornerRadius * {2*factor:.15g}')
                    b.Height=h;b.setExpression('Placement.Base.x',f'{x0:.15g} mm + Parameters.BayCornerRadius * {factor:.15g}');b.Placement.Base.z=z0
                else:
                    b.Length=w;b.setExpression('Height',f'{h:.15g} mm - Parameters.BayCornerRadius * {2*factor:.15g}')
                    b.Placement.Base.x=x0;b.setExpression('Placement.Base.z',f'{z0:.15g} mm + Parameters.BayCornerRadius * {factor:.15g}')
                parts.append(b)
            for ix in (0,1):
                for iz in (0,1):
                    c=doc.getObject(name+f'Corner{ix}{iz}') or doc.addObject('Part::Cylinder',name+f'Corner{ix}{iz}');c.Height=depth
                    c.Placement=A.Placement(A.Vector(0,y0,0),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)))
                    c.setExpression('Radius',f'Parameters.BayCornerRadius * {factor:.15g}')
                    for dim,side,lo,hi in [('x',ix,x0,x1),('z',iz,z0,z1)]:
                        c.setExpression('Placement.Base.'+dim,f'{(lo if side==0 else hi):.15g} mm '+('+' if side==0 else '-')+f' Parameters.BayCornerRadius * {factor:.15g}')
                    parts.append(c)
            tool=doc.getObject(name+'Portal') or doc.addObject('Part::MultiFuse',name+'Portal');tool.Shapes=parts;portals.append(tool)
            report['portals'].append(dict(name=name,bounds_mm=[low,high],corner_radius_mm=r,
                straight_interior_boxes=[dict(object=b.Name) for b in parts[:2]],
                design_reservation_not_new_contact_proof=True))
        union=doc.getObject('SharedAccessPortals') or doc.addObject('Part::MultiFuse','SharedAccessPortals');union.Shapes=portals
        cut=doc.getObject('ShellWithSharedPortals') or doc.addObject('Part::Cut','ShellWithSharedPortals');cut.Base=doc.ShellWithFootPassages;cut.Tool=union
        for r in m['parts']:doc.getObject(r['object']).Base=cut
        doc.recompute()
        volumes={}
        for n,old in original.items():
            s=doc.getObject(n).Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True),n
            added=s.cut(old);assert added.isNull() or added.isValid()
            report['new_material_mm3'][n]=added.Volume;assert added.Volume<1e-5,n
            assert s.Volume<old.Volume;n_bb=s.BoundBox
            assert max(n_bb.XLength,n_bb.YLength,n_bb.ZLength)<=252,n
            volumes[n]=s.Volume;report['parts'].append(dict(object=n,volume_mm3=s.Volume,
                removed_mm3=old.Volume-s.Volume,conservative_print_bounds_mm=[n_bb.XLength,n_bb.YLength,n_bb.ZLength]))
            save()
        p.set('B5','6.5 mm');doc.recompute()
        assert all(doc.getObject(n).Shape.isValid() and len(doc.getObject(n).Shape.Solids)==1 for n in volumes)
        assert any(abs(doc.getObject(n).Shape.Volume-v)>1e-3 for n,v in volumes.items())
        p.set('B5','6 mm');doc.recompute()
        assert all(abs(doc.getObject(n).Shape.Volume-v)<1e-3 for n,v in volumes.items())
        doc.save();A.closeDocument(doc_name);doc=None
        d=A.openDocument(str(native))
        try:
            for n,v in volumes.items():
                s=d.getObject(n).Shape;assert s.isValid() and abs(s.Volume-v)<1e-3
        finally:A.closeDocument(d.Name)
        report.update(status='FOUR_NATIVE_PANELS_WITH_SEVEN_SHARED_PORTALS_EXACT_MOTION_OPEN',
            native=native.relative_to(ROOT).as_posix(),native_sha256=sha(native),fresh_reopen=True,
            corner_parameter_test_mm=[6,6.5,6],body_width_not_increased=True,
            previous_clear_wire_distances_reused_by_strict_material_subset=True,
            previous_clear_fixed_pairs_reused_by_strict_material_subset=True,
            exact_leg_motion_complete=False,
            source_receipt='45f390a:torso-panel-interfaces.json;69knownwires clear,9fixed positive witnesses and2legposes not accepted')
        m.update(native_sha256=sha(native),fresh_reopen=True,shared_access_portals=7,
            corner_parameter_test_mm=[6,6.5,6],shared_portal_modifier=Path(__file__).relative_to(ROOT).as_posix(),
            current_status='FOUR_NATIVE_PANELS_WITH_SEVEN_SHARED_PORTALS_EXACT_MOTION_OPEN')
        for r in m['parts']:r['volume_mm3']=volumes[r['object']]
        mp.write_text(json.dumps(m,indent=2)+'\n');save()
        print(json.dumps({k:report[k] for k in ('status','parts','new_material_mm3','worker_seconds')}),flush=True)
    except Exception as exc:
        report.update(status='SHARED_NATIVE_SKIN_PORTALS_INCOMPLETE',error=str(exc));save()
        if doc:doc.saveAs(str(OUT/'FelineTorsoPanels.access-partial.FCStd'))
        raise
    finally:
        if doc and doc.Name in A.listDocuments():A.closeDocument(doc.Name)


if __name__=='__main__':main()
