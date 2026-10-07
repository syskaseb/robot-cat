"""Underbody detachable WAGO mounting candidate, no fabricated snap geometry.

Keep retained mounts and logical buses. Adhesive strength/actual casing base and
PETG adhesion are explicit delivered gates. Native pad is a supplied-part space
allowance, not an STL to print or a manufacturer mesh.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, time, tempfile, shutil
from open_prototype_u1_side_support import ROOT, OUT, sha, deadline


def main():
    import FreeCAD as A, Part
    from open_deck_p0_supports import sketch, feature
    from open_deck_p0_plate import rect
    tick=time.monotonic();started=datetime.now(timezone.utc).isoformat();deadline()
    native=OUT/'RetentionMountsCandidate.FCStd';proof=OUT/'wago-retention-checks.json'
    assert not native.exists() and not proof.exists(),'Receive existing result, no duplicate'
    src=OUT/'U1SideSupportCandidate.FCStd'
    assert sha(src)==json.loads((OUT/'u1-side-support-checks.json').read_text(encoding='utf-8'))['native_sha256']
    plan=json.loads((OUT/'wago-retention-plan.json').read_text(encoding='utf-8'))
    rows=json.loads((OUT/'distribution-mount-plan.json').read_text(encoding='utf-8'))['distribution']
    paths=[src,OUT/'u1-side-support-checks.json',OUT/'wago-retention-plan.json',OUT/'distribution-mount-plan.json',OUT.parent/'OpenPrototypePlan.FCStd',Path(__file__)]
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    d=A.openDocument(str(src));ctx=None
    try:
        p=d.Parameters;p.addProperty('App::PropertyLength','WagoRetentionHeight');p.WagoRetentionHeight=2.49
        pad=d.addObject('PartDesign::Body','SuppliedReclosablePadAllowance')
        pad.addProperty('App::PropertyString','Qualification');pad.Qualification='Supplied SJ4570 engaged allowance, NOT printable; delivered adhesion/thickness OPEN'
        sk=sketch(pad,'ReclosablePadFootprint',0);rect(sk,-10,-5,20,10)
        pad.Tip=feature(pad,'Pad','EngagedPadHeight',sk,'Parameters.WagoRetentionHeight')
        group=d.addObject('App::DocumentObjectGroup','WagoUnderbodyRetentionAllowances')
        bodies={};pads={};supports=[]
        for r in rows:
            x,y=r['centre_xy_mm'];z=r['base_z_mm'];w,h,t=r['size_mm']
            body=d.getObject(r['native']);assert body is not None,r['native']
            assert abs(body.Shape.BoundBox.ZMin-z)<1e-6,r['native']
            body.setExpression('Placement.Base.z','Parameters.WagoRetentionHeight')
            link=d.addObject('App::Link',r['role']+'RetentionPad');link.setLink(pad)
            link.LinkPlacement.Base=A.Vector(x,y,z);group.addObject(link)
            bodies[r['role']]=body;pads[r['role']]=link
        def validate():
            deadline();d.recompute();s=pad.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            assert sk.FullyConstrained and sk.solve()==0
            for r in rows:
                assert abs(bodies[r['role']].Shape.BoundBox.ZMin-r['base_z_mm']-p.WagoRetentionHeight.Value)<1e-6
                assert abs(pads[r['role']].Shape.BoundBox.ZLength-p.WagoRetentionHeight.Value)<1e-6
            return s.Volume
        v=validate();p.WagoRetentionHeight=3.;assert validate()>v
        # At maximum delivered-fit allowance, modelled bodies remain separate
        # from every retained material obstacle. Reservations are labelled.
        ctx=A.openDocument(str(OUT.parent/'OpenPrototypePlan.FCStd'))
        real={o.Name:o.Shape for o in ctx.Objects if 'Shape' in o.PropertiesList and not o.Shape.isNull()
              and (o.Name.startswith('P0_') or o.Name in ('LeftRiserWithMain','RightRiser','MainSupplierFamily'))}
        printed={n:d.getObject(n).Shape for n in ('LowerCarrier','UpperCarrier')}
        printed.update({o.Name:o.Shape for o in d.Objects if o.TypeId=='App::Link' and o not in list(pads.values())})
        hardware={o.Name:o.Shape for g in (d.NominalMountHardware,d.SideMountHardware) for o in g.Group}
        vendor={o.Name:o.Shape for o in d.Objects if o.Name.startswith('BUSsupplier')}
        nominal={o.Name:o.Shape for o in d.Objects if o.Name.endswith('NominalPCB') or o.Name=='U1NominalOutlineOnly'}
        other_res={o.Name:o.Shape for o in ctx.Objects if o.Name.startswith(('S0_','S1_','MTA_','F_PI_')) and 'Shape' in o.PropertiesList}
        contacts=[];errors=[];reservations=[];pairs=0
        def compare(n,s,m,t,dest):
            nonlocal pairs
            if not s.BoundBox.intersect(t.BoundBox):return
            pairs+=1;deadline()
            try:
                assert s.isValid() and t.isValid(),(n,m)
                hit=s.common(t);assert hit.isValid()
                if hit.Volume>1e-5:dest.append(dict(a=n,b=m,volume_mm3=hit.Volume))
            except Exception as e:errors.append(dict(a=n,b=m,error=str(e)))
        obstacles={**real,**printed,**hardware,**vendor}
        for role,b in bodies.items():
            s=b.Shape;link=pads[role]
            for n,t in obstacles.items():
                compare(role+'_casing_budget',s,n,t,reservations)
                compare(role+'_underbody_pad_budget',link.Shape,n,t,reservations)
            for n,t in {**nominal,**other_res}.items():compare(role+'_casing_budget',s,n,t,reservations)
            for m,q in bodies.items():
                if m>role:compare(role+'_casing_budget',s,m+'_casing_budget',q.Shape,reservations)
            r=next(r for r in rows if r['role']==role);x,y=r['centre_xy_mm'];z=r['base_z_mm']
            rail=d.getObject('SideRail1' if r['side']=='L' else 'SideRail2').Shape
            probe=Part.makeBox(20,10,.1,A.Vector(x-10,y-5,z-.1));area=probe.common(rail).Volume/.1
            assert abs(area-200)<1e-5,(role,area)
            supports.append(dict(role=role,rail_material_support_area_mm2=area,
                actual_casing_adhesive_area_measured=False,body_base_z_at_3mm=z+3))
            # Clearance budget for modest peel/lift only, not a dimensioned
            # lever trajectory or a proof of connected wiring removal.
            w,h,t=r['size_mm'];svc=Part.makeBox(w+4,h+2,t+10,A.Vector(x-w/2-2,y-h/2-1,z+3))
            for n,q in obstacles.items():compare(role+'_service_budget',svc,n,q,reservations)
            for m,q in bodies.items():
                if m!=role:compare(role+'_service_budget',svc,m+'_casing_budget',q.Shape,reservations)
        assert not errors,(errors,contacts,reservations)
        p.WagoRetentionHeight=2.49;assert abs(validate()-v)<1e-6
        d.Label='Open prototype retention candidate; U1 fit and WAGO bond OPEN'
        d.saveAs(str(native));A.closeDocument(ctx.Name);ctx=None;A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-retention-reopen-') as td:
            cp=Path(td)/native.name;shutil.copy2(native,cp);d=A.openDocument(str(cp))
            p=d.Parameters;pad=d.SuppliedReclosablePadAllowance;sk=d.ReclosablePadFootprint
            bodies={r['role']:d.getObject(r['native']) for r in rows};pads={r['role']:d.getObject(r['role']+'RetentionPad') for r in rows}
            assert abs(validate()-v)<1e-6
        result=dict(status='WAGO_UNDERBODY_RETENTION_GEOMETRY_CLEAR_BOND_OPEN' if not reservations else 'WAGO_UNDERBODY_RETENTION_SPACE_REQUIRES_CHANGE',
            source_sha256=pins,native_sha256=sha(native),started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3),changed_pairs=pairs,material_contacts=contacts,
            nominal_reservation_contacts=reservations,errors=errors,pad_count=20,pad_cut_piece_count=40,
            rail_support=supports,parameter_cycle_mm=[2.49,3,2.49],relocated_reopen=True,
            retained_prints_unchanged=True,print_exports_added=0,selected=False,stage_completed=False,physical_pass=False,
            known_bounds=['Underbody pad and casing are valid reservations, NOT measured supplied meshes',
                'Rail200mm2 support is NOT proof of casing bond area or strength',
                'Service space allowance does not qualify exact lever sweep, finger ergonomics or wired removal',
                'U1 hardware/whole surrounding frame and literal50mm leads still require shared check',
                'No tape purchase, BOM stock selection or old wiring endpoint credit'])
        assert all(sha(ROOT/k)==h for k,h in pins.items())
        proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','worker_wall_seconds','changed_pairs','nominal_reservation_contacts','errors')}),flush=True)
    finally:
        if ctx:A.closeDocument(ctx.Name)
        if d.Name in A.listDocuments():A.closeDocument(d.Name)


if __name__=='__main__':main()
